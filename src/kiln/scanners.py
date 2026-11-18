"""`kiln scan`: run one pinned scanner, and read its report into Kiln's finding format (D-013).

CI installs each scanner at the version config names; this module checks the installed one
before it runs and refuses any other. Then it:

- refuses to run where a scanner's own suppression file exists (`.trivyignore`, `trivy.yaml`,
  `osv-scanner.toml`) and turns off Semgrep's inline `# nosemgrep`, so every dismissal is in
  Kiln's one list, where Tom sees it;
- gives the scanner only the environment variables config allows: a scanner is outside code,
  and one of them shipped a release that stole CI credentials (CVE-2026-33634);
- treats any exit code the scanner does not document for a finished scan as a failure, and a
  report it cannot read as a failure, never as "no findings".

A **seeded** run scans a fixture with one planted finding, and succeeds only if that finding is
reported at a blocking severity. It is how CI shows that a scanner still detects: an empty
report from a broken scanner looks exactly like a clean one.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from kiln.config import GoScannerConfig, KilnConfig, ScannersConfig
from kiln.errors import KilnError
from kiln.findings import (
    Finding,
    Scanner,
    ScanReport,
    read_osv,
    read_semgrep,
    read_trivy,
    semgrep_rule_prefix,
)
from kiln.ids import content_hash

FOREIGN_SUPPRESSIONS = frozenset(
    {".trivyignore", ".trivyignore.yaml", "trivy.yaml", "osv-scanner.toml"}
)
"""Files through which a scanner would set findings aside outside Kiln's dismissal list."""

FINISHED: Mapping[Scanner, frozenset[int]] = {
    Scanner.SEMGREP: frozenset({0}),
    Scanner.OSV_SCANNER: frozenset({0, 1}),  # 1: vulnerabilities were found
    Scanner.TRIVY: frozenset({0}),
}
"""The exit codes each scanner documents for a scan that finished."""

Runner = Callable[
    [Sequence[str], Path, Mapping[str, str], float], "subprocess.CompletedProcess[str]"
]
"""Runs a command with an exact environment, in a working directory, under a timeout."""


def run_process(
    argv: Sequence[str], cwd: Path, env: Mapping[str, str], timeout: float
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(  # noqa: S603 (argv is built here, never a shell)
            list(argv),
            cwd=cwd,
            env=dict(env),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise KilnError(f"{Path(argv[0]).name} ran past {timeout:.0f} seconds") from exc
    except OSError as exc:
        raise KilnError(f"cannot run {argv[0]}: {exc}") from exc


def scanner_environment(config: ScannersConfig, environ: Mapping[str, str]) -> dict[str, str]:
    """The allowed variables that are set, and nothing else."""
    return {name: environ[name] for name in sorted(config.environment) if name in environ}


def scan(
    config: KilnConfig,
    scanner: Scanner,
    root: Path,
    *,
    seeded: bool = False,
    rules_dir: Path | None = None,
    runner: Runner = run_process,
    environ: Mapping[str, str] | None = None,
    which: Callable[[str], str | None] = shutil.which,
) -> ScanReport:
    """Run `scanner` on the repo at `root`, or on its seeded finding, and read the report."""
    if config.scanners is None:
        raise KilnError("config has no `scanners` section", see="config/kiln.yaml")
    settings = config.scanners
    env = scanner_environment(settings, os.environ if environ is None else environ)
    _refuse_foreign_suppressions(root)
    binary = which(scanner.value)
    if binary is None:
        raise KilnError(
            f"{scanner.value} is not installed; CI installs the pinned version",
            see=".github/workflows/ci.yml, job `scanners`",
        )
    run = _Run(runner=runner, root=root, env=env, timeout=settings.timeout_seconds)
    with tempfile.TemporaryDirectory(prefix="kiln-scan-") as scratch:
        out = Path(scratch) / "report.json"
        if scanner is Scanner.SEMGREP:
            if rules_dir is None:
                raise KilnError("semgrep needs --rules: a checkout of the pinned rules commit")
            result = _semgrep(run, binary, settings, rules_dir, out, seeded=seeded)
        elif scanner is Scanner.OSV_SCANNER:
            result = _osv(run, which, binary, settings, out, seeded=seeded)
        else:
            result = _trivy(run, which, binary, settings, out, seeded=seeded)
    return ScanReport(
        scanner=scanner,
        version=result.version,
        rules=result.rules,
        target=result.target,
        seeded=seeded,
        raw=content_hash(result.raw),
        findings=result.findings,
    )


@dataclass(frozen=True)
class _Result:
    version: str
    rules: str
    target: str
    raw: bytes
    findings: tuple[Finding, ...]


def _semgrep(
    run: _Run, binary: str, settings: ScannersConfig, rules_dir: Path, out: Path, *, seeded: bool
) -> _Result:
    pinned = settings.semgrep
    version = _semgrep_version(run, binary, pinned.version)
    rules = _semgrep_rules(rules_dir, settings)
    target = pinned.seeded.target if seeded else "."
    configs = [str(rules_dir.resolve() / pack) for pack in pinned.rules.packs]
    excludes = [] if seeded else list(pinned.exclude)
    argv = [
        binary,
        "scan",
        *_each("--config", configs),
        "--metrics=off",
        "--disable-version-check",
        "--disable-nosem",
        "--json",
        "--output",
        str(out),
        "--quiet",
        *_each("--exclude", excludes),
        target,
    ]
    raw = run.finish(Scanner.SEMGREP, argv, out)
    prefix = semgrep_rule_prefix(rules_dir, run.root)
    return _Result(
        version, rules, target, raw, read_semgrep(raw, root=run.root, rule_prefix=prefix)
    )


def _osv(
    run: _Run,
    which: Callable[[str], str | None],
    binary: str,
    settings: ScannersConfig,
    out: Path,
    *,
    seeded: bool,
) -> _Result:
    pinned = settings.osv_scanner
    version = _go_version(run, which, binary, pinned)
    if seeded and pinned.seeded.parse_as is None:
        raise KilnError("OSV-Scanner's seeded finding needs `parse_as`", see="config/kiln.yaml")
    target = pinned.seeded.target if seeded else "."
    where = ["-L", f"{pinned.seeded.parse_as}:{target}"] if seeded else ["-r", target]
    argv = [binary, "scan", "source", "--format", "json", "--output-file", str(out)]
    argv += ["--verbosity", "error", *where]
    raw = run.finish(Scanner.OSV_SCANNER, argv, out)
    return _Result(
        version, "OSV.dev advisories, read live", target, raw, read_osv(raw, root=run.root)
    )


def _trivy(
    run: _Run,
    which: Callable[[str], str | None],
    binary: str,
    settings: ScannersConfig,
    out: Path,
    *,
    seeded: bool,
) -> _Result:
    pinned = settings.trivy
    version = _go_version(run, which, binary, pinned)
    reads_advisories = "vuln" in pinned.scanners
    rules = f"the checks built into trivy {pinned.version}" + (
        ", and its vulnerability database, read live" if reads_advisories else ""
    )
    target = pinned.seeded.target if seeded else "."
    argv = [binary, "fs", "--scanners", ",".join(pinned.scanners), "--skip-check-update"]
    argv += [] if reads_advisories else ["--skip-db-update"]
    argv += ["--format", "json", "--output", str(out), "--quiet"]
    argv += [*_each("--skip-dirs", [] if seeded else list(pinned.exclude)), target]
    raw = run.finish(Scanner.TRIVY, argv, out)
    return _Result(version, rules, target, raw, read_trivy(raw, target=target))


def _each(flag: str, values: Sequence[str]) -> list[str]:
    """`--flag a --flag b`."""
    return [part for value in values for part in (flag, value)]


def seeded_finding(report: ScanReport, config: ScannersConfig) -> Finding | None:
    """The planted finding, if the seeded run reported it at a blocking severity."""
    rule = {
        Scanner.SEMGREP: config.semgrep.seeded.rule,
        Scanner.OSV_SCANNER: config.osv_scanner.seeded.rule,
        Scanner.TRIVY: config.trivy.seeded.rule,
    }[report.scanner]
    return next(
        (f for f in report.findings if f.rule == rule and f.severity in config.blocking), None
    )


class _Run:
    def __init__(
        self, *, runner: Runner, root: Path, env: Mapping[str, str], timeout: float
    ) -> None:
        self.runner, self.root, self.env, self.timeout = runner, root, env, timeout

    def output(self, argv: Sequence[str]) -> str:
        """The stdout of a command that must succeed."""
        result = self.runner(argv, self.root, self.env, self.timeout)
        if result.returncode != 0:
            raise KilnError(
                f"{' '.join(argv[:3])} exited {result.returncode}: {_last_line(result.stderr)}"
            )
        return result.stdout

    def finish(self, scanner: Scanner, argv: Sequence[str], out: Path) -> bytes:
        """Run a scan and return its report, or fail if it did not finish."""
        result = self.runner(argv, self.root, self.env, self.timeout)
        if result.returncode not in FINISHED[scanner]:
            raise KilnError(
                f"{scanner.value} exited {result.returncode}, which is not a finished scan: "
                f"{_last_line(result.stderr)}"
            )
        try:
            return out.read_bytes()
        except FileNotFoundError as exc:
            raise KilnError(f"{scanner.value} finished but wrote no report") from exc


def _last_line(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1][:300] if lines else "no message"


def _semgrep_version(run: _Run, binary: str, pinned: str) -> str:
    lines = run.output([binary, "--version"]).strip().splitlines()
    installed = lines[0].strip() if lines else ""
    if installed != pinned:
        raise KilnError(
            f"semgrep {installed or '(no version)'} is installed; config pins {pinned}",
            see="config/kiln.yaml, scanners.semgrep",
        )
    return installed


_MOD_LINE = re.compile(r"^\s*mod\s+(\S+)\s+(\S+)(?:\s+(\S+))?\s*$", re.MULTILINE)
_PATH_LINE = re.compile(r"^\s*path\s+(\S+)\s*$", re.MULTILINE)


def _go_version(
    run: _Run, which: Callable[[str], str | None], binary: str, pinned: GoScannerConfig
) -> str:
    """The module and version the binary was built from, read from its embedded build
    information with `go version -m`: a binary built from source by `go install` names its
    module's exact version and hash there, whatever its own `--version` prints."""
    go = which("go")
    if go is None:
        raise KilnError("checking a Go scanner's version needs `go` on PATH")
    info = run.output([go, "version", "-m", binary])
    package = _PATH_LINE.search(info)
    module = _MOD_LINE.search(info)
    if package is None or module is None:
        raise KilnError(f"{binary} carries no Go build information", item=binary)
    built = (package.group(1), module.group(1), module.group(2))
    if built != (pinned.package, pinned.module, pinned.version):
        raise KilnError(
            f"{binary} was built from {built[1]} {built[2]} ({built[0]}); config pins "
            f"{pinned.module} {pinned.version} ({pinned.package})",
            see="config/kiln.yaml, scanners",
        )
    checksum = module.group(3)
    return f"{pinned.version} ({checksum})" if checksum else pinned.version


def _semgrep_rules(rules_dir: Path, settings: ScannersConfig) -> str:
    """Check that the rules are a clean checkout of the pinned commit, and describe them."""
    pinned = settings.semgrep.rules
    head = _git(rules_dir, "rev-parse", "HEAD").strip()
    if head != pinned.commit:
        raise KilnError(
            f"the rules are at {head[:12] or '(no commit)'}; config pins {pinned.commit[:12]}",
            item=str(rules_dir),
        )
    if _git(rules_dir, "status", "--porcelain").strip():
        raise KilnError("the rules checkout has local changes", item=str(rules_dir))
    for pack in pinned.packs:
        if not (rules_dir / pack).is_dir():
            raise KilnError(f"the rules have no pack {pack!r}", item=str(rules_dir))
    return f"semgrep-rules {pinned.commit[:12]}: {', '.join(pinned.packs)}"


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(  # noqa: S603 (fixed argv, no shell)
        ["git", "-C", str(root), *args],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise KilnError(f"git {args[0]} failed: {_last_line(result.stderr)}", item=str(root))
    return result.stdout


def _refuse_foreign_suppressions(root: Path) -> None:
    """Every file git would show a scanner, tracked or not, minus what .gitignore hides."""
    listed = _git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    found = sorted(
        name for name in listed.split("\0") if name and Path(name).name in FOREIGN_SUPPRESSIONS
    )
    if found:
        raise KilnError(
            f"{found[0]} would let a scanner set findings aside outside Kiln's dismissal list; "
            "record a dismissal in config/dismissals.yaml instead",
            item=found[0],
        )
