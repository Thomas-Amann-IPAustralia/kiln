"""`kiln scan`: each pinned scanner is checked, run with a bare environment, and read strictly.

No scanner runs here (tests never touch the network, and CI's test job has none installed).
`FakeTools` plays them: it answers the version checks and writes a fixture report shaped from
a real run (tests/fixtures/scanners/). The real runs are CI's job `scanners`.
"""

from __future__ import annotations

import functools
import shutil
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath

import pytest
from typer.testing import CliRunner

from kiln import scanners
from kiln.cli import app
from kiln.config import KilnConfig, load_config
from kiln.errors import KilnError
from kiln.findings import Scanner
from tests.gitrepo import Repo

FIXTURES = Path(__file__).parent / "fixtures" / "scanners"
SEEDED = Path(__file__).parent / "seeded-findings"
BINARIES = {name: f"/opt/tools/{name}" for name in ("semgrep", "osv-scanner", "trivy", "go")}


def build_info(config: KilnConfig, name: str, *, version: str | None = None) -> str:
    assert config.scanners is not None
    pinned = config.scanners.osv_scanner if name == "osv-scanner" else config.scanners.trivy
    return (
        f"{BINARIES[name]}: go1.27.4\n"
        f"\tpath\t{pinned.package}\n"
        f"\tmod\t{pinned.module}\t{version or pinned.version}\th1:placeholder=\n"
        "\tdep\texample.invalid/dep\tv1.0.0\th1:placeholder=\n"
    )


class FakeTools:
    """Plays the scanners and `go version -m`, and records every command and environment."""

    def __init__(
        self,
        config: KilnConfig,
        report: bytes | None,
        *,
        exit_code: int = 0,
        semgrep_version: str = "1.183.0",
        built_from: str | None = None,
    ) -> None:
        self.report, self.exit_code = report, exit_code
        self.semgrep_version = semgrep_version
        self.info = {
            name: build_info(config, name, version=built_from) for name in ("osv-scanner", "trivy")
        }
        self.calls: list[tuple[list[str], dict[str, str]]] = []

    def __call__(
        self, argv: Sequence[str], cwd: Path, env: Mapping[str, str], timeout: float
    ) -> subprocess.CompletedProcess[str]:
        argv = list(argv)
        self.calls.append((argv, dict(env)))
        if argv[0] == BINARIES["go"]:
            return subprocess.CompletedProcess(argv, 0, self.info[Path(argv[3]).name], "")
        if argv[1:] == ["--version"]:
            return subprocess.CompletedProcess(argv, 0, self.semgrep_version + "\n", "")
        flag = "--output-file" if "--output-file" in argv else "--output"
        if self.report is not None:
            Path(argv[argv.index(flag) + 1]).write_bytes(self.report)
        return subprocess.CompletedProcess(argv, self.exit_code, "", "scanner said no")

    @property
    def scans(self) -> list[list[str]]:
        return [argv for argv, _ in self.calls if argv[0] != BINARIES["go"] and len(argv) > 2]


def which(name: str) -> str | None:
    return BINARIES.get(name)


@pytest.fixture
def config(repo_root: Path) -> KilnConfig:
    return load_config(repo_root / "config" / "kiln.yaml")


@pytest.fixture
def root(tmp_path: Path) -> Path:
    """A solution-shaped repo holding the seeded findings exactly as Kiln's repo does."""
    (tmp_path / "repo").mkdir()
    repo = Repo(tmp_path / "repo")
    shutil.copytree(SEEDED, repo.root / "tests" / "seeded-findings")
    repo.commit("seeded findings")
    return repo.root


@pytest.fixture
def rules(tmp_path: Path) -> Repo:
    """A stand-in for the semgrep-rules checkout: the pinned packs, at one commit."""
    (tmp_path / "semgrep-rules").mkdir()
    repo = Repo(tmp_path / "semgrep-rules")
    repo.write("python/placeholder.yaml", "rules: []\n")
    repo.write("yaml/github-actions/placeholder.yaml", "rules: []\n")
    repo.commit("rules")
    return repo


def pinned_to(config: KilnConfig, commit: str) -> KilnConfig:
    """The repo's config, with the rules commit set to the stand-in checkout's."""
    assert config.scanners is not None
    semgrep = config.scanners.semgrep
    rules = semgrep.rules.model_copy(update={"commit": commit})
    settings = config.scanners.model_copy(
        update={"semgrep": semgrep.model_copy(update={"rules": rules})}
    )
    return config.model_copy(update={"scanners": settings})


def semgrep_report(rules: Repo, root: Path) -> bytes:
    prefix = scanners.semgrep_rule_prefix(rules.root, root)
    text = (FIXTURES / "semgrep-seeded.json").read_text(encoding="utf-8")
    return text.replace("{prefix}", prefix).encode()


def fixture(name: str, root: Path) -> bytes:
    return (FIXTURES / name).read_text(encoding="utf-8").replace("{root}", str(root)).encode()


# --- What runs, and with what ------------------------------------------------------------------


def test_semgrep_runs_the_pinned_packs_with_its_escape_hatches_shut(
    config: KilnConfig, root: Path, rules: Repo
) -> None:
    """Why: metrics off, no inline `# nosemgrep`, and the seeded fixture out of the repo scan."""
    config = pinned_to(config, rules.git("rev-parse", "HEAD"))
    tools = FakeTools(config, semgrep_report(rules, root))
    report = scanners.scan(
        config, Scanner.SEMGREP, root, rules_dir=rules.root, runner=tools, which=which
    )
    (argv,) = tools.scans
    for flag in ("--metrics=off", "--disable-version-check", "--disable-nosem", "--json"):
        assert flag in argv
    configs = [argv[i + 1] for i, arg in enumerate(argv) if arg == "--config"]
    assert configs == [str(rules.root / "python"), str(rules.root / "yaml/github-actions")]
    assert config.scanners is not None
    excludes = [argv[i + 1] for i, arg in enumerate(argv) if arg == "--exclude"]
    assert excludes == list(config.scanners.semgrep.exclude)
    seeded = PurePosixPath(config.scanners.semgrep.seeded.target)
    assert any(seeded.is_relative_to(path) for path in excludes)
    assert argv[-1] == "."
    assert report.version == "1.183.0"
    assert report.rules.startswith("semgrep-rules ")
    assert len(report.findings) == 3


def test_a_seeded_semgrep_run_targets_the_fixture_and_excludes_nothing(
    config: KilnConfig, root: Path, rules: Repo
) -> None:
    """Why: the repo scan's exclusion would otherwise hide the very finding CI looks for."""
    config = pinned_to(config, rules.git("rev-parse", "HEAD"))
    tools = FakeTools(config, semgrep_report(rules, root))
    report = scanners.scan(
        config, Scanner.SEMGREP, root, seeded=True, rules_dir=rules.root, runner=tools, which=which
    )
    (argv,) = tools.scans
    assert "--exclude" not in argv
    assert argv[-1] == "tests/seeded-findings/semgrep"
    assert config.scanners is not None
    found = scanners.seeded_finding(report, config.scanners)
    assert found is not None
    assert found.rule == "python.lang.security.audit.subprocess-shell-true"


def test_osv_scanner_reads_the_seeded_file_as_the_configured_lockfile_format(
    config: KilnConfig, root: Path
) -> None:
    """Why: the fixture's name is one no tool or bot reads by itself, so the format is named."""
    tools = FakeTools(config, fixture("osv-seeded.json", root), exit_code=1)
    report = scanners.scan(
        config, Scanner.OSV_SCANNER, root, seeded=True, runner=tools, which=which
    )
    (argv,) = tools.scans
    assert argv[-2:] == [
        "-L",
        "requirements.txt:tests/seeded-findings/osv-scanner/seeded-requirements",
    ]
    assert report.version.startswith("v2.7.0 (h1:")
    assert [f.rule for f in report.findings] == ["CVE-2020-14343"]


def test_osv_scanner_scans_the_repo_recursively(config: KilnConfig, root: Path) -> None:
    """Why: every lockfile in the repo counts, not only the one at the top."""
    tools = FakeTools(config, b'{"results": []}')
    report = scanners.scan(config, Scanner.OSV_SCANNER, root, runner=tools, which=which)
    (argv,) = tools.scans
    assert argv[-2:] == ["-r", "."]
    assert report.findings == ()


def test_trivy_uses_its_built_in_checks_and_skips_only_the_seeded_folder(
    config: KilnConfig, root: Path
) -> None:
    """Why: checks fetched at run time would change under a pinned version; built-in ones
    cannot. With vulnerability scanning off it needs no database either."""
    tools = FakeTools(config, (FIXTURES / "trivy-seeded.json").read_bytes())
    scanners.scan(config, Scanner.TRIVY, root, runner=tools, which=which)
    (argv,) = tools.scans
    assert argv[argv.index("--scanners") + 1] == "misconfig"
    assert "--skip-check-update" in argv
    assert "--skip-db-update" in argv
    assert argv[argv.index("--skip-dirs") + 1] == "tests/seeded-findings"


def test_a_scanner_sees_only_the_allowed_environment(config: KilnConfig, root: Path) -> None:
    """Why: a scanner is outside code; Trivy's compromised release stole CI credentials from
    exactly this environment (CVE-2026-33634)."""
    environ = {
        "PATH": "/usr/bin",
        "HTTPS_PROXY": "http://proxy.invalid:3128",
        "GITHUB_TOKEN": "placeholder",
        "OPENAI_API_KEY": "placeholder",
        "AWS_SECRET_ACCESS_KEY": "placeholder",
    }
    tools = FakeTools(config, (FIXTURES / "trivy-seeded.json").read_bytes())
    scanners.scan(config, Scanner.TRIVY, root, runner=tools, which=which, environ=environ)
    for _, env in tools.calls:
        assert env == {"PATH": "/usr/bin", "HTTPS_PROXY": "http://proxy.invalid:3128"}


# --- What is refused before anything runs -----------------------------------------------------


def test_another_semgrep_version_is_refused_before_it_scans(
    config: KilnConfig, root: Path, rules: Repo
) -> None:
    """Why: findings from an unpinned scanner cannot be compared with the last run's."""
    config = pinned_to(config, rules.git("rev-parse", "HEAD"))
    tools = FakeTools(config, b"{}", semgrep_version="1.199.0")
    with pytest.raises(KilnError, match=r"semgrep 1\.199\.0 is installed; config pins 1\.183\.0"):
        scanners.scan(
            config, Scanner.SEMGREP, root, rules_dir=rules.root, runner=tools, which=which
        )
    assert tools.scans == []


@pytest.mark.parametrize("scanner", [Scanner.OSV_SCANNER, Scanner.TRIVY])
def test_a_go_scanner_built_from_another_version_is_refused(
    config: KilnConfig, root: Path, scanner: Scanner
) -> None:
    """Why: the build information names the module version the binary was built from,
    whatever its `--version` says (a source build of Trivy says `dev`)."""
    tools = FakeTools(config, b"{}", built_from="v0.69.4")
    with pytest.raises(KilnError, match=r"was built from .* v0\.69\.4"):
        scanners.scan(config, scanner, root, runner=tools, which=which)
    assert tools.scans == []


def test_a_binary_with_no_build_information_is_refused(config: KilnConfig, root: Path) -> None:
    """Why: without it nothing shows which source the binary came from."""
    tools = FakeTools(config, b"{}")
    tools.info["trivy"] = "/opt/tools/trivy: could not read Go build info\n"
    with pytest.raises(KilnError, match="no Go build information"):
        scanners.scan(config, Scanner.TRIVY, root, runner=tools, which=which)


@pytest.mark.parametrize("missing", ["trivy", "go"])
def test_a_missing_tool_is_loud(config: KilnConfig, root: Path, missing: str) -> None:
    """Why: a scanner that is not there must fail the job, not skip it."""
    tools = FakeTools(config, b"{}")
    with pytest.raises(KilnError, match=r"not installed|needs `go`"):
        scanners.scan(
            config,
            Scanner.TRIVY,
            root,
            runner=tools,
            which=lambda name: None if name == missing else BINARIES.get(name),
        )


def test_semgrep_rules_at_another_commit_are_refused(
    config: KilnConfig, root: Path, rules: Repo
) -> None:
    """Why: a ruleset that moved finds different things under the same version."""
    tools = FakeTools(config, b"{}")
    with pytest.raises(KilnError, match="config pins 16b9e6d45f10"):
        scanners.scan(
            config, Scanner.SEMGREP, root, rules_dir=rules.root, runner=tools, which=which
        )
    assert tools.scans == []


def test_edited_semgrep_rules_are_refused(config: KilnConfig, root: Path, rules: Repo) -> None:
    """Why: a deleted rule in a clean-looking checkout would quietly stop a check."""
    config = pinned_to(config, rules.git("rev-parse", "HEAD"))
    (rules.root / "python/placeholder.yaml").unlink()
    with pytest.raises(KilnError, match="local changes"):
        scanners.scan(
            config,
            Scanner.SEMGREP,
            root,
            rules_dir=rules.root,
            runner=FakeTools(config, b"{}"),
            which=which,
        )


def test_semgrep_without_its_rules_is_refused(config: KilnConfig, root: Path) -> None:
    """Why: Semgrep with no rules finds nothing, which reads as a clean scan."""
    with pytest.raises(KilnError, match="needs --rules"):
        scanners.scan(config, Scanner.SEMGREP, root, runner=FakeTools(config, b"{}"), which=which)


@pytest.mark.parametrize("name", sorted(scanners.FOREIGN_SUPPRESSIONS))
@pytest.mark.parametrize("tracked", [True, False])
def test_a_scanners_own_suppression_file_is_refused(
    config: KilnConfig, root: Path, name: str, tracked: bool
) -> None:
    """Why: a finding set aside there would bypass the one dismissal list Tom reviews."""
    (root / "sub").mkdir()
    (root / "sub" / name).write_text("# placeholder\n", encoding="utf-8")
    if tracked:
        subprocess.run(["git", "-C", str(root), "add", "--all"], check=True)
    tools = FakeTools(config, b"{}")
    with pytest.raises(KilnError, match="outside Kiln's dismissal list"):
        scanners.scan(config, Scanner.TRIVY, root, runner=tools, which=which)
    assert tools.calls == []


# --- What counts as a finished scan -----------------------------------------------------------


def test_an_exit_code_the_scanner_does_not_document_for_a_finished_scan_fails(
    config: KilnConfig, root: Path
) -> None:
    """Why: OSV-Scanner exits 128 when it found no lockfile; that is not "no vulnerabilities"."""
    tools = FakeTools(config, b'{"results": []}', exit_code=128)
    with pytest.raises(KilnError, match="exited 128, which is not a finished scan"):
        scanners.scan(config, Scanner.OSV_SCANNER, root, runner=tools, which=which)


def test_a_scan_that_wrote_no_report_fails(config: KilnConfig, root: Path) -> None:
    """Why: no report is not an empty report."""
    tools = FakeTools(config, None)
    with pytest.raises(KilnError, match="wrote no report"):
        scanners.scan(config, Scanner.TRIVY, root, runner=tools, which=which)


def test_a_seeded_finding_below_the_blocking_line_does_not_count(
    config: KilnConfig, root: Path
) -> None:
    """Why: the check is that a finding like it would fail CI, which only a blocking one does."""
    assert config.scanners is not None
    text = (FIXTURES / "trivy-seeded.json").read_text(encoding="utf-8")
    tools = FakeTools(config, text.replace('"HIGH"', '"LOW"').encode())
    report = scanners.scan(config, Scanner.TRIVY, root, seeded=True, runner=tools, which=which)
    assert scanners.seeded_finding(report, config.scanners) is None


# --- The command line ---------------------------------------------------------------------------


@pytest.fixture
def cli_root(root: Path, repo_root: Path) -> Path:
    """The solution repo, with Kiln's config and dismissal list copied in."""
    (root / "config").mkdir()
    for name in ("kiln.yaml", "dismissals.yaml"):
        shutil.copy(repo_root / "config" / name, root / "config" / name)
    return root


def fake_scanning(monkeypatch: pytest.MonkeyPatch, config: KilnConfig, report: bytes) -> None:
    """Route the CLI's scan through `FakeTools`, everything else unchanged."""
    original = scanners.scan
    monkeypatch.setattr(
        scanners,
        "scan",
        functools.partial(original, runner=FakeTools(config, report), which=which),
    )


def invoke(root: Path, *args: str) -> tuple[int, str]:
    result = CliRunner().invoke(
        app, ["scan", *args, "--root", str(root), "--config", str(root / "config" / "kiln.yaml")]
    )
    return result.exit_code, result.output


def test_the_cli_fails_a_scan_with_an_open_blocking_finding(
    monkeypatch: pytest.MonkeyPatch, config: KilnConfig, cli_root: Path
) -> None:
    """Why: the slice's check: a scanner fails CI on a finding like its seeded one."""
    fake_scanning(monkeypatch, config, (FIXTURES / "trivy-seeded.json").read_bytes())
    code, output = invoke(cli_root, "trivy")
    assert code == 2
    assert "BLOCKING high  DS-0002  Dockerfile:3" in output
    assert "1 open finding(s) at a blocking severity from trivy" in output


def test_the_cli_passes_a_scan_once_the_finding_is_dismissed(
    monkeypatch: pytest.MonkeyPatch, config: KilnConfig, cli_root: Path
) -> None:
    """Why: "fix or explain": an explained finding no longer blocks, and still shows."""
    fake_scanning(monkeypatch, config, (FIXTURES / "trivy-seeded.json").read_bytes())
    _, output = invoke(cli_root, "trivy")
    key = next(line.split()[1] for line in output.splitlines() if line.strip().startswith("key"))
    high = output.split("BLOCKING high  DS-0002", 1)[1].split("key ", 1)[1].split()[0]
    assert high.startswith("sha256:") and key.startswith("sha256:")
    (cli_root / "config" / "dismissals.yaml").write_text(
        "dismissals:\n"
        f"  - key: {high}\n"
        "    scanner: trivy\n"
        "    rule: DS-0002\n"
        "    path: Dockerfile\n"
        "    reason: Placeholder reason.\n"
        "    by: build_session\n"
        "    dismissed_on: 2026-11-18\n",
        encoding="utf-8",
    )
    code, output = invoke(cli_root, "trivy")
    assert code == 0, output
    assert "1 dismissed. 0 blocking" in output
    assert "dismissed  DS-0002  Dockerfile:3: Placeholder reason." in output


def test_the_cli_seeded_run_succeeds_only_when_the_finding_is_found(
    monkeypatch: pytest.MonkeyPatch, config: KilnConfig, cli_root: Path
) -> None:
    """Why: CI's proof that each scanner detects; an empty report must fail it."""
    fake_scanning(monkeypatch, config, (FIXTURES / "trivy-seeded.json").read_bytes())
    code, output = invoke(cli_root, "trivy", "--seeded")
    assert code == 0, output
    assert "Seeded finding detected: DS-0002 (high)" in output
    monkeypatch.undo()
    fake_scanning(monkeypatch, config, b'{"SchemaVersion": 2}')
    code, output = invoke(cli_root, "trivy", "--seeded")
    assert code == 2
    assert "did not report its seeded finding" in output
