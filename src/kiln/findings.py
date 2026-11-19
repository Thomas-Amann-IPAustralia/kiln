"""The one finding format, and the readers that bring each scanner's report into it (D-013).

Semgrep CE, OSV-Scanner and Trivy each write their own JSON. A finding leaves here in one
shape: which scanner found it, the rule, a severity on Kiln's one scale, where it is, and a
key. The key is a hash of *what* was found (the matched code, or the package and version),
not of where the line numbers fell, so it stays the same while the finding does. A dismissal
names a key: it covers that finding and no other, and stops applying when the code or the
package under it changes.

Reading is strict. A missing field, or a value outside what a scanner is known to write, is a
`KilnError`: a finding is never dropped because its report looked unfamiliar.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Annotated, Any, Literal, cast

import yaml
from pydantic import Field, TypeAdapter, ValidationError, model_validator

from kiln.errors import KilnError
from kiln.ids import ContentHash, content_hash
from kiln.model import Record, RepoPath, Text
from kiln.vocabulary import Actor, Severity

SEVERITY_ORDER: tuple[Severity, ...] = (
    Severity.CRITICAL,
    Severity.HIGH,
    Severity.UNKNOWN,
    Severity.MEDIUM,
    Severity.LOW,
)
"""Most urgent first. `unknown` sits above `medium`: nothing shows it is any smaller."""


class Scanner(StrEnum):
    """The scanners whose reports Kiln reads. The value is the scanner's command name."""

    SEMGREP = "semgrep"
    OSV_SCANNER = "osv-scanner"
    TRIVY = "trivy"


class FileLocation(Record):
    """A place in a file. The lines are absent when a check is about the whole file."""

    kind: Literal["file"] = "file"
    path: RepoPath
    start_line: Annotated[int, Field(ge=1)] | None = None
    end_line: Annotated[int, Field(ge=1)] | None = None

    def where(self) -> str:
        if self.start_line is None:
            return self.path
        if self.end_line in (None, self.start_line):
            return f"{self.path}:{self.start_line}"
        return f"{self.path}:{self.start_line}-{self.end_line}"


class PackageLocation(Record):
    """A package at a version, as a lockfile or manifest names it."""

    kind: Literal["package"] = "package"
    path: RepoPath
    ecosystem: Text
    package: Text
    version: Text

    def where(self) -> str:
        return f"{self.path}: {self.package} {self.version} ({self.ecosystem})"


Location = Annotated[FileLocation | PackageLocation, Field(discriminator="kind")]


class Finding(Record):
    """What a scanner observed, in the one format every consumer reads."""

    key: ContentHash
    """The finding's identity: a hash of the scanner, the rule and what was matched."""
    scanner: Scanner
    rule: Text
    """The scanner's id for the check or the advisory, such as `DS-0002` or `CVE-2020-14343`."""
    aliases: tuple[str, ...] = ()
    """Other ids for the same advisory."""
    severity: Severity
    title: Text
    cwe: tuple[str, ...] = ()
    location: Location
    reference: str | None = None
    """A page that explains the rule or the advisory."""


class ScanReport(Record):
    """One run of one scanner: what ran, on what, and everything it found."""

    scanner: Scanner
    version: Text
    """The installed version, as checked before the run."""
    rules: Text
    """Which rules or advisory data the run used."""
    target: RepoPath
    seeded: bool
    """True for a run on a seeded finding, which proves the scanner still detects."""
    raw: ContentHash
    """The hash of the scanner's own report, byte for byte: the evidence for these findings."""
    findings: tuple[Finding, ...]

    @model_validator(mode="after")
    def _sorted_and_distinct(self) -> ScanReport:
        keys = [finding.key for finding in self.findings]
        if keys != sorted(set(keys)):
            raise ValueError("findings must be sorted by key, each key once")
        return self


class Dismissal(Record):
    """A finding set aside with a recorded reason (Security Architect charter: "fix or
    explain"). It covers exactly one key, and must agree with the finding it names."""

    key: ContentHash
    scanner: Scanner
    rule: Text
    path: RepoPath
    reason: Text
    by: Actor
    dismissed_on: date
    """Not `on`: YAML 1.1 reads a bare `on` key as `true` (D-011)."""


class DismissalList(Record):
    dismissals: tuple[Dismissal, ...] = ()

    @model_validator(mode="after")
    def _one_per_key(self) -> DismissalList:
        counts = Counter(dismissal.key for dismissal in self.dismissals)
        repeated = sorted(key for key, count in counts.items() if count > 1)
        if repeated:
            raise ValueError(f"a key may be dismissed once; repeated: {repeated[0]}")
        return self


class Dismissed(Record):
    finding: Finding
    dismissal: Dismissal


class Assessment(Record):
    """A scan's findings sorted into open and dismissed, against the blocking severities."""

    report: ScanReport
    blocking: tuple[Severity, ...]
    open: tuple[Finding, ...]
    dismissed: tuple[Dismissed, ...]
    stale: tuple[Dismissal, ...]
    """Dismissals for this scanner that matched nothing: the finding is gone, or changed."""

    @property
    def open_blocking(self) -> tuple[Finding, ...]:
        return tuple(finding for finding in self.open if finding.severity in self.blocking)


def load_dismissals(path: Path) -> DismissalList:
    """Read the dismissal list, or raise a `KilnError` naming what is wrong with it."""
    try:
        raw: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise KilnError("the dismissal list is missing", item=str(path)) from exc
    except yaml.YAMLError as exc:
        raise KilnError(f"the dismissal list is not valid YAML: {exc}", item=str(path)) from exc
    try:
        return DismissalList.model_validate(raw)
    except ValidationError as exc:
        first = exc.errors()[0]
        where = ".".join(str(part) for part in first["loc"])
        raise KilnError(
            f"the dismissal list is invalid; first: {where}: {first['msg']}", item=str(path)
        ) from exc


def assess(
    report: ScanReport, dismissals: DismissalList, blocking: Iterable[Severity]
) -> Assessment:
    """Apply the dismissals for this report's scanner. A seeded run takes no dismissals: a
    seeded finding exists to be found."""
    by_key = {finding.key: finding for finding in report.findings}
    dismissed: list[Dismissed] = []
    stale: list[Dismissal] = []
    covered: set[str] = set()
    candidates: tuple[Dismissal, ...] = () if report.seeded else dismissals.dismissals
    for dismissal in candidates:
        if dismissal.scanner is not report.scanner:
            continue
        finding = by_key.get(dismissal.key)
        if finding is None:
            stale.append(dismissal)
            continue
        if (finding.rule, _path_of(finding)) != (dismissal.rule, dismissal.path):
            raise KilnError(
                f"a dismissal names key {dismissal.key[:19]}… as {dismissal.rule} in "
                f"{dismissal.path}, but that key is {finding.rule} in {_path_of(finding)}",
                see="config/dismissals.yaml",
            )
        dismissed.append(Dismissed(finding=finding, dismissal=dismissal))
        covered.add(finding.key)
    return Assessment(
        report=report,
        blocking=tuple(sorted(set(blocking), key=SEVERITY_ORDER.index)),
        open=tuple(f for f in report.findings if f.key not in covered),
        dismissed=tuple(dismissed),
        stale=tuple(stale),
    )


def render(assessment: Assessment) -> str:
    """A plain summary for a terminal or a CI log, most urgent first."""
    report = assessment.report
    counts = Counter(finding.severity for finding in report.findings)
    tally = ", ".join(f"{counts[s]} {s.value}" for s in SEVERITY_ORDER)
    lines = [
        f"{report.scanner.value} {report.version} on {report.target} ({report.rules}); "
        f"report {report.raw[:19]}…",
        f"{len(report.findings)} finding(s): {tally}. {len(assessment.dismissed)} dismissed. "
        f"{len(assessment.open_blocking)} blocking "
        f"(blocking: {', '.join(s.value for s in assessment.blocking)}).",
    ]
    for finding in _urgent_first(assessment.open):
        marker = "BLOCKING " if finding.severity in assessment.blocking else ""
        lines += [
            f"  {marker}{finding.severity.value}  {finding.rule}  {finding.location.where()}",
            f"    {finding.title.splitlines()[0][:160]}",
            f"    key {finding.key}",
        ]
    for item in assessment.dismissed:
        lines.append(
            f"  dismissed  {item.finding.rule}  {item.finding.location.where()}: "
            f"{item.dismissal.reason.splitlines()[0][:120]}"
        )
    for dismissal in assessment.stale:
        lines.append(
            f"  stale dismissal  {dismissal.rule}  {dismissal.path}: it matches no finding "
            "now; remove it from config/dismissals.yaml"
        )
    return "\n".join(lines)


def _urgent_first(findings: Iterable[Finding]) -> list[Finding]:
    return sorted(
        findings,
        key=lambda f: (SEVERITY_ORDER.index(f.severity), f.rule, f.location.where(), f.key),
    )


def _path_of(finding: Finding) -> str:
    return finding.location.path


# --- Reading the scanners' own reports -------------------------------------------------------
#
# Each reader turns one scanner's JSON into findings. Every value is checked for its type before
# it is used. A finding's key hashes its scanner, its rule, what it matched, and how many
# identical matches came before it, so two identical matches in one file stay two findings.


@dataclass(frozen=True)
class _Draft:
    """A finding before its key is computed."""

    rule: str
    identity: tuple[str, ...]
    severity: Severity
    title: str
    location: FileLocation | PackageLocation
    aliases: tuple[str, ...] = ()
    cwe: tuple[str, ...] = ()
    reference: str | None = None


def _finish(scanner: Scanner, drafts: Iterable[_Draft]) -> tuple[Finding, ...]:
    seen: Counter[tuple[str, ...]] = Counter()
    findings: list[Finding] = []
    for draft in drafts:
        base = (scanner.value, draft.rule, *draft.identity)
        occurrence = seen[base]
        seen[base] += 1
        identity = json.dumps([*base, occurrence], separators=(",", ":"), ensure_ascii=False)
        findings.append(
            Finding(
                key=content_hash(identity.encode("utf-8")),
                scanner=scanner,
                rule=draft.rule,
                aliases=draft.aliases,
                severity=draft.severity,
                title=draft.title.strip() or draft.rule,
                cwe=draft.cwe,
                location=draft.location,
                reference=draft.reference,
            )
        )
    return tuple(sorted(findings, key=lambda finding: finding.key))


def _load(raw: bytes, scanner: Scanner) -> dict[str, Any]:
    try:
        body: object = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise KilnError(f"{scanner.value} wrote a report that is not JSON: {exc}") from exc
    return _obj(body, f"{scanner.value}'s report")


def _obj(value: object, what: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise KilnError(f"{what} is not a JSON object")
    return cast(dict[str, Any], value)


def _list(value: object, what: str) -> list[Any]:
    if not isinstance(value, list):
        raise KilnError(f"{what} is not a JSON list")
    return cast(list[Any], value)


def _str(value: object, what: str) -> str:
    if not isinstance(value, str):
        raise KilnError(f"{what} is not a string")
    return value


def _int(value: object, what: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise KilnError(f"{what} is not an integer")
    return value


def _field(obj: Mapping[str, Any], name: str, what: str) -> Any:
    if name not in obj:
        raise KilnError(f"{what} has no `{name}`")
    return obj[name]


def _objs(value: object, what: str) -> list[dict[str, Any]]:
    """A JSON list of objects; `what` names one of them."""
    return [_obj(item, what) for item in _list(value, f"a list of {what}s")]


def _strs(value: object, what: str) -> list[str]:
    return [_str(item, what) for item in _list(value, what)]


_REPO_PATH: TypeAdapter[str] = TypeAdapter(RepoPath)


def _repo_path(value: str, scanner: Scanner) -> str:
    try:
        return _REPO_PATH.validate_python(PurePosixPath(value).as_posix())
    except ValidationError as exc:
        raise KilnError(f"{scanner.value} reported a path outside the repo: {value!r}") from exc


def _relative_to(root: Path, value: str, scanner: Scanner) -> str:
    path = Path(value)
    absolute = (path if path.is_absolute() else root / path).resolve()
    try:
        return _repo_path(absolute.relative_to(root.resolve()).as_posix(), scanner)
    except ValueError as exc:
        raise KilnError(f"{scanner.value} reported a path outside the repo: {value!r}") from exc


_CWE = re.compile(r"\bCWE-\d+\b")


def _cwe_ids(value: object) -> tuple[str, ...]:
    """`CWE-89` ids from a string or a list of strings, such as `CWE-89: SQL Injection`."""
    if value is None:
        return ()
    texts = [value] if isinstance(value, str) else _strs(value, "a CWE list")
    return tuple(sorted({match for text in texts for match in _CWE.findall(text)}))


def _url(value: object) -> str | None:
    return value if isinstance(value, str) and value.startswith(("https://", "http://")) else None


def _reference(metadata: Mapping[str, Any]) -> str | None:
    """A Semgrep rule's `source` page, else its first reference that is a link."""
    references: object = metadata.get("references")
    candidates = cast(list[object], references) if isinstance(references, list) else [references]
    return next(
        (url for url in map(_url, [metadata.get("source"), *candidates]) if url is not None), None
    )


# Semgrep's rules use ERROR, WARNING and INFO; newer rules may use the five-level scale.
_SEMGREP_SEVERITY = {
    "CRITICAL": Severity.CRITICAL,
    "ERROR": Severity.HIGH,
    "HIGH": Severity.HIGH,
    "WARNING": Severity.MEDIUM,
    "MEDIUM": Severity.MEDIUM,
    "INFO": Severity.LOW,
    "LOW": Severity.LOW,
}


def semgrep_rule_prefix(rules_dir: Path, cwd: Path) -> str:
    """The prefix Semgrep puts on every rule id: the rules folder's path, dotted. It is
    relative to the working directory when the folder is inside it, and absolute otherwise
    (observed, Semgrep 1.183.0)."""
    rules, here = rules_dir.resolve(), cwd.resolve()
    try:
        parts = rules.relative_to(here).parts
    except ValueError:
        parts = rules.parts[1:]
    return ".".join(parts)


def read_semgrep(raw: bytes, *, root: Path, rule_prefix: str) -> tuple[Finding, ...]:
    """Semgrep's `--json` report. The key hashes the bytes each result matched, read from the
    file at the result's byte offsets, so it survives lines moving above it."""
    body = _load(raw, Scanner.SEMGREP)
    errors = _list(body.get("errors", []), "semgrep's `errors`")
    if errors:
        first = _obj(errors[0], "a semgrep error")
        raise KilnError(
            f"semgrep reported {len(errors)} error(s), so its scan is incomplete; first: "
            f"{first.get('type')}: {str(first.get('message', ''))[:200]}"
        )
    paths = _obj(_field(body, "paths", "semgrep's report"), "semgrep's `paths`")
    if not _list(paths.get("scanned", []), "semgrep's scanned paths"):
        raise KilnError("semgrep scanned no files, and a scan of nothing finds nothing")
    prefix = rule_prefix + "."
    contents: dict[str, bytes] = {}
    drafts: list[_Draft] = []
    for item in _list(_field(body, "results", "semgrep's report"), "semgrep's `results`"):
        result = _obj(item, "a semgrep result")
        check_id = _str(_field(result, "check_id", "a semgrep result"), "a semgrep rule id")
        if not check_id.startswith(prefix):
            raise KilnError(f"semgrep rule {check_id!r} is not from the pinned rules")
        path = _repo_path(_str(_field(result, "path", check_id), "a path"), Scanner.SEMGREP)
        start = _obj(_field(result, "start", check_id), "a start")
        end = _obj(_field(result, "end", check_id), "an end")
        first, last = _int(start.get("offset"), "an offset"), _int(end.get("offset"), "an offset")
        if path not in contents:
            try:
                contents[path] = (root / path).read_bytes()
            except OSError as exc:
                raise KilnError("semgrep reported a file that cannot be read", item=path) from exc
        if not 0 <= first <= last <= len(contents[path]):
            raise KilnError(f"semgrep's offsets {first}-{last} are outside the file", item=path)
        extra = _obj(_field(result, "extra", check_id), "a result's `extra`")
        word = _str(_field(extra, "severity", check_id), "a severity")
        if word not in _SEMGREP_SEVERITY:
            raise KilnError(f"semgrep wrote severity {word!r}, which Kiln does not map")
        metadata = _obj(extra.get("metadata", {}), "a rule's metadata")
        drafts.append(
            _Draft(
                rule=check_id[len(prefix) :],
                identity=(path, hashlib.sha256(contents[path][first:last]).hexdigest()),
                severity=_SEMGREP_SEVERITY[word],
                title=_str(_field(extra, "message", check_id), "a message"),
                location=FileLocation(
                    path=path,
                    start_line=_int(start.get("line"), "a line"),
                    end_line=_int(end.get("line"), "a line"),
                ),
                cwe=_cwe_ids(metadata.get("cwe")),
                reference=_reference(metadata),
            )
        )
    return _finish(Scanner.SEMGREP, drafts)


_OSV_WORDS = {
    "CRITICAL": Severity.CRITICAL,
    "HIGH": Severity.HIGH,
    "MODERATE": Severity.MEDIUM,
    "MEDIUM": Severity.MEDIUM,
    "LOW": Severity.LOW,
}


def cvss_rating(score: float) -> Severity:
    """The CVSS qualitative rating of a base score (FIRST, CVSS v3.1 and v4.0 specifications).
    A score of 0.0 ("none") is rated low, since a scanner reported it."""
    if score >= 9.0:
        return Severity.CRITICAL
    if score >= 7.0:
        return Severity.HIGH
    if score >= 4.0:
        return Severity.MEDIUM
    return Severity.LOW


def _osv_severity(max_severity: object, members: Sequence[dict[str, Any]]) -> Severity:
    """OSV-Scanner's `max_severity` is a CVSS score as text, or empty when no record in the
    group has one. Then the databases' own words decide; a word Kiln does not know is
    `unknown`, never a guess."""
    text = "" if max_severity is None else _str(max_severity, "max_severity").strip()
    if text:
        try:
            score = float(text)
        except ValueError as exc:
            raise KilnError(f"OSV-Scanner wrote max_severity {text!r}, not a score") from exc
        if not 0.0 <= score <= 10.0:
            raise KilnError(f"OSV-Scanner wrote a CVSS score of {score}, outside 0 to 10")
        return cvss_rating(score)
    ratings: list[Severity] = []
    for member in members:
        word = _database_specific(member).get("severity")
        if isinstance(word, str) and word.strip():
            ratings.append(_OSV_WORDS.get(word.strip().upper(), Severity.UNKNOWN))
    return min(ratings, key=SEVERITY_ORDER.index) if ratings else Severity.UNKNOWN


def read_osv(raw: bytes, *, root: Path) -> tuple[Finding, ...]:
    """OSV-Scanner's `--format json` report. One finding per group: OSV-Scanner groups the
    records that describe one vulnerability under their aliases, and the rule is the group's
    first id in sorted order, which puts a CVE first when there is one."""
    body = _load(raw, Scanner.OSV_SCANNER)
    drafts: list[_Draft] = []
    for result in _objs(_field(body, "results", "OSV-Scanner's report"), "an OSV result"):
        source = _obj(_field(result, "source", "an OSV result"), "an OSV source")
        lockfile = _str(_field(source, "path", "an OSV source"), "a path")
        path = _relative_to(root, lockfile, Scanner.OSV_SCANNER)
        for entry in _objs(result.get("packages", []), "an OSV package"):
            drafts += _osv_package(entry, path)
    return _finish(Scanner.OSV_SCANNER, drafts)


def _osv_package(entry: Mapping[str, Any], path: str) -> list[_Draft]:
    package = _obj(_field(entry, "package", "an OSV package"), "a package")
    name = _str(_field(package, "name", "a package"), "a package name")
    version = _str(_field(package, "version", name), "a package version")
    ecosystem = _str(_field(package, "ecosystem", name), "an ecosystem")
    records = {
        _str(_field(record, "id", name), "an advisory id"): record
        for record in _objs(entry.get("vulnerabilities", []), "an OSV record")
    }
    drafts: list[_Draft] = []
    grouped: set[str] = set()
    for group in _objs(entry.get("groups", []), "an OSV group"):
        ids = sorted(_strs(_field(group, "ids", name), "group ids"))
        missing = [advisory for advisory in ids if advisory not in records]
        if not ids or missing:
            raise KilnError(f"an OSV group names records the report lacks: {missing}", item=name)
        grouped.update(ids)
        members = [records[advisory] for advisory in ids]
        names = sorted(set(ids) | set(_strs(group.get("aliases", []), "aliases")))
        summaries = [str(member.get("summary") or "").strip() for member in members]
        cwe = {
            cwe for member in members for cwe in _cwe_ids(_database_specific(member).get("cwe_ids"))
        }
        drafts.append(
            _Draft(
                rule=names[0],
                identity=(path, ecosystem, name, version),
                severity=_osv_severity(group.get("max_severity"), members),
                title=next((text for text in summaries if text), f"{names[0]} in {name} {version}"),
                location=PackageLocation(
                    path=path, ecosystem=ecosystem, package=name, version=version
                ),
                aliases=tuple(alias for alias in names if alias != names[0]),
                cwe=tuple(sorted(cwe)),
                reference=f"https://osv.dev/vulnerability/{ids[0]}",
            )
        )
    ungrouped = sorted(set(records) - grouped)
    if ungrouped:
        raise KilnError(f"OSV records outside every group: {ungrouped}", item=name)
    return drafts


def _database_specific(record: Mapping[str, Any]) -> dict[str, Any]:
    return _obj(record.get("database_specific", {}), "an advisory's database_specific")


_TRIVY_SEVERITY = {
    "CRITICAL": Severity.CRITICAL,
    "HIGH": Severity.HIGH,
    "MEDIUM": Severity.MEDIUM,
    "LOW": Severity.LOW,
    "UNKNOWN": Severity.UNKNOWN,
}


def _trivy_severity(value: object) -> Severity:
    word = _str(value, "a Trivy severity")
    if word not in _TRIVY_SEVERITY:
        raise KilnError(f"Trivy wrote severity {word!r}, which Kiln does not map")
    return _TRIVY_SEVERITY[word]


def _line(value: object) -> int | None:
    """Trivy writes 0, or nothing, when a check is about the whole file."""
    if value is None:
        return None
    number = _int(value, "a line number")
    return number if number > 0 else None


def read_trivy(raw: bytes, *, target: str) -> tuple[Finding, ...]:
    """Trivy's `--format json` report (schema 2). Misconfigurations are keyed by the lines that
    cause them; vulnerabilities by the package and version. Secrets and licences are refused:
    gitleaks owns secrets, and licences are not scanned yet."""
    body = _load(raw, Scanner.TRIVY)
    if body.get("SchemaVersion") != 2:
        raise KilnError(f"Trivy wrote report schema {body.get('SchemaVersion')!r}; Kiln reads 2")
    drafts: list[_Draft] = []
    for result in _objs(body.get("Results") or [], "a Trivy result"):
        name = _str(_field(result, "Target", "a Trivy result"), "a Trivy target")
        path = _repo_path((PurePosixPath(target) / name).as_posix(), Scanner.TRIVY)
        for section in ("Secrets", "Licenses"):
            if result.get(section):
                raise KilnError(
                    f"Trivy reported {section.lower()}, which Kiln does not read from it; "
                    "check the scanners it was given",
                    item=path,
                )
        for check in _objs(result.get("Misconfigurations") or [], "a misconfiguration"):
            drafts.append(_trivy_misconfiguration(check, path))
        for vulnerability in _objs(result.get("Vulnerabilities") or [], "a vulnerability"):
            ecosystem = _str(_field(result, "Type", path), "a Trivy result type")
            drafts.append(_trivy_vulnerability(vulnerability, path, ecosystem))
    return _finish(Scanner.TRIVY, drafts)


def _trivy_misconfiguration(check: Mapping[str, Any], path: str) -> _Draft:
    rule = _str(_field(check, "ID", path), "a check id")
    status = _str(_field(check, "Status", rule), "a check status")
    if status != "FAIL":
        raise KilnError(f"Trivy reported check {rule} with status {status!r}", item=path)
    cause = _obj(check.get("CauseMetadata") or {}, "CauseMetadata")
    code = _obj(cause.get("Code") or {}, "the cause's code")
    lines = [
        _str(line.get("Content", ""), "a line")
        for line in _objs(code.get("Lines") or [], "a code line")
        if line.get("IsCause")
    ]
    return _Draft(
        rule=rule,
        identity=(path, "\n".join(lines)),
        severity=_trivy_severity(_field(check, "Severity", rule)),
        title=str(check.get("Title") or check.get("Message") or rule),
        location=FileLocation(
            path=path,
            start_line=_line(cause.get("StartLine")),
            end_line=_line(cause.get("EndLine")),
        ),
        reference=_url(check.get("PrimaryURL")),
    )


def _trivy_vulnerability(vulnerability: Mapping[str, Any], path: str, ecosystem: str) -> _Draft:
    rule = _str(_field(vulnerability, "VulnerabilityID", path), "an advisory id")
    package = _str(_field(vulnerability, "PkgName", rule), "a package name")
    version = _str(_field(vulnerability, "InstalledVersion", rule), "a version")
    return _Draft(
        rule=rule,
        identity=(path, ecosystem, package, version),
        severity=_trivy_severity(_field(vulnerability, "Severity", rule)),
        title=str(vulnerability.get("Title") or f"{rule} in {package} {version}"),
        location=PackageLocation(path=path, ecosystem=ecosystem, package=package, version=version),
        cwe=_cwe_ids(vulnerability.get("CweIDs")),
        reference=_url(vulnerability.get("PrimaryURL")),
    )
