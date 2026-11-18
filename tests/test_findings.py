"""The one finding format, and the readers that bring each scanner's report into it.

The fixtures in tests/fixtures/scanners/ are shaped from real runs of the pinned scanners on
the seeded findings (D-013), with each scanner's prose replaced by placeholder text.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from kiln import findings
from kiln.errors import KilnError
from kiln.findings import (
    Dismissal,
    DismissalList,
    FileLocation,
    Finding,
    PackageLocation,
    Scanner,
    ScanReport,
)
from kiln.ids import content_hash
from kiln.vocabulary import Actor, Severity

FIXTURES = Path(__file__).parent / "fixtures" / "scanners"
SEEDED_PY = Path(__file__).parent / "seeded-findings" / "semgrep" / "seeded.py"
PREFIX = "rules.semgrep-rules"
BLOCKING = (Severity.CRITICAL, Severity.HIGH, Severity.UNKNOWN)


def fixture(name: str, **tokens: str) -> bytes:
    text = (FIXTURES / name).read_text(encoding="utf-8")
    for token, value in tokens.items():
        text = text.replace("{" + token + "}", value)
    return text.encode("utf-8")


def as_json(name: str, **tokens: str) -> dict[str, Any]:
    return json.loads(fixture(name, **tokens))


@pytest.fixture
def root(tmp_path: Path) -> Path:
    """A repo holding the seeded Semgrep file, byte for byte, where the report says it is."""
    target = tmp_path / "tests" / "seeded-findings" / "semgrep" / "seeded.py"
    target.parent.mkdir(parents=True)
    target.write_bytes(SEEDED_PY.read_bytes())
    return tmp_path


def semgrep(root: Path, body: dict[str, Any] | None = None) -> tuple[Finding, ...]:
    raw = json.dumps(body).encode() if body else fixture("semgrep-seeded.json", prefix=PREFIX)
    return findings.read_semgrep(raw, root=root, rule_prefix=PREFIX)


# --- Semgrep -------------------------------------------------------------------------------


def test_semgrep_rules_lose_the_folder_prefix_and_map_to_one_scale(root: Path) -> None:
    """Why: a rule's id must not depend on where CI put the rules, and ERROR must block."""
    by_rule = {f.rule: f for f in semgrep(root)}
    assert set(by_rule) == {
        "python.lang.security.audit.dangerous-subprocess-use-audit",
        "python.lang.security.audit.subprocess-shell-true",
        "python.lang.correctness.unchecked-subprocess-call",
    }
    shell = by_rule["python.lang.security.audit.subprocess-shell-true"]
    assert shell.severity is Severity.HIGH
    assert shell.cwe == ("CWE-78",)
    assert shell.location == FileLocation(
        path="tests/seeded-findings/semgrep/seeded.py", start_line=11, end_line=11
    )
    assert by_rule["python.lang.correctness.unchecked-subprocess-call"].severity is Severity.MEDIUM


def test_a_semgrep_key_survives_lines_moving_above_the_match(root: Path) -> None:
    """Why: a dismissal must not go stale because someone added an import above it."""
    before = {f.rule: f.key for f in semgrep(root)}
    path = root / "tests/seeded-findings/semgrep/seeded.py"
    added = b"# one more line\n# and another\n"
    path.write_bytes(added + path.read_bytes())
    body = as_json("semgrep-seeded.json", prefix=PREFIX)
    for result in body["results"]:
        for end in ("start", "end"):
            result[end]["offset"] += len(added)
            result[end]["line"] += 2
    after = {f.rule: f.key for f in semgrep(root, body)}
    assert after == before


def test_a_semgrep_key_changes_when_the_matched_code_does(root: Path) -> None:
    """Why: a dismissal covers the code that was judged, not whatever later sits there."""
    before = {f.rule: f.key for f in semgrep(root)}
    path = root / "tests/seeded-findings/semgrep/seeded.py"
    # The same length, so every offset in the report still holds. Only the audit rule's match
    # spans the whole call; the other two match `call` and `True`, which are unchanged.
    path.write_bytes(path.read_bytes().replace(b"command, shell=True", b"commands,shell=True"))
    after = {f.rule: f.key for f in semgrep(root)}
    changed = {rule for rule in before if after[rule] != before[rule]}
    assert changed == {"python.lang.security.audit.dangerous-subprocess-use-audit"}


def test_two_identical_matches_in_one_file_are_two_findings(root: Path) -> None:
    """Why: dismissing one copy of a pattern must not dismiss the other."""
    body = as_json("semgrep-seeded.json", prefix=PREFIX)
    body["results"].append(body["results"][0])
    keys = [f.key for f in semgrep(root, body)]
    assert len(keys) == 4 == len(set(keys))


def test_a_semgrep_rule_from_outside_the_pinned_rules_is_refused(root: Path) -> None:
    """Why: a finding from rules nobody pinned has no stable id to dismiss or count."""
    raw = fixture("semgrep-seeded.json", prefix="elsewhere")
    with pytest.raises(KilnError, match="not from the pinned rules"):
        findings.read_semgrep(raw, root=root, rule_prefix=PREFIX)


def test_a_semgrep_report_with_errors_is_refused(root: Path) -> None:
    """Why: a file Semgrep could not parse was not scanned; that is not a clean result."""
    body = as_json("semgrep-seeded.json", prefix=PREFIX)
    body["errors"] = [{"type": "Syntax error", "message": "at line 3"}]
    with pytest.raises(KilnError, match="1 error"):
        semgrep(root, body)


def test_a_semgrep_scan_of_no_files_is_refused(root: Path) -> None:
    """Why: a scan of nothing finds nothing, which reads exactly like a clean scan."""
    body = as_json("semgrep-seeded.json", prefix=PREFIX)
    body["results"], body["paths"] = [], {"scanned": []}
    with pytest.raises(KilnError, match="scanned no files"):
        semgrep(root, body)


def test_offsets_outside_the_file_are_refused(root: Path) -> None:
    """Why: a key read from the wrong bytes would identify the wrong code."""
    body = as_json("semgrep-seeded.json", prefix=PREFIX)
    body["results"][0]["end"]["offset"] = 10**6
    with pytest.raises(KilnError, match="outside the file"):
        semgrep(root, body)


@pytest.mark.parametrize(
    ("prefix", "rules", "cwd"),
    [
        ("rules", "/work/repo/rules", "/work/repo"),
        ("work.temp.semgrep-rules", "/work/temp/semgrep-rules", "/work/repo"),
    ],
)
def test_the_rule_prefix_follows_where_semgrep_found_the_rules(
    prefix: str, rules: str, cwd: str
) -> None:
    """Why: Semgrep dots the rules' path relative to the working directory when it can, and
    absolute otherwise (observed); a wrong prefix fails every scan."""
    assert findings.semgrep_rule_prefix(Path(rules), Path(cwd)) == prefix


# --- OSV-Scanner ---------------------------------------------------------------------------


def osv(root: Path, body: dict[str, Any] | None = None) -> tuple[Finding, ...]:
    raw = json.dumps(body).encode() if body else fixture("osv-seeded.json", root=str(root))
    return findings.read_osv(raw, root=root)


def test_osv_gives_one_finding_per_vulnerability_with_the_cve_as_its_rule(root: Path) -> None:
    """Why: two databases' records of one CVE are one thing to fix, and dismiss, once."""
    (finding,) = osv(root)
    assert finding.rule == "CVE-2020-14343"
    assert finding.aliases == ("GHSA-8q59-q68h-6hv4", "PYSEC-2021-142")
    assert finding.severity is Severity.CRITICAL
    assert finding.cwe == ("CWE-20",)
    assert finding.location == PackageLocation(
        path="tests/seeded-findings/osv-scanner/seeded-requirements",
        ecosystem="PyPI",
        package="pyyaml",
        version="5.3.1",
    )
    assert finding.reference == "https://osv.dev/vulnerability/GHSA-8q59-q68h-6hv4"


@pytest.mark.parametrize(
    ("score", "rating"),
    [
        (10.0, Severity.CRITICAL),
        (9.0, Severity.CRITICAL),
        (8.9, Severity.HIGH),
        (7.0, Severity.HIGH),
        (6.9, Severity.MEDIUM),
        (4.0, Severity.MEDIUM),
        (3.9, Severity.LOW),
        (0.0, Severity.LOW),
    ],
)
def test_cvss_scores_take_the_specifications_ratings(score: float, rating: Severity) -> None:
    """Why: the boundaries decide what blocks; they come from the CVSS specification."""
    assert findings.cvss_rating(score) is rating


def _without_score(root: Path, words: list[str | None]) -> dict[str, Any]:
    body = as_json("osv-seeded.json", root=str(root))
    package = body["results"][0]["packages"][0]
    package["groups"][0]["max_severity"] = ""
    for record, word in zip(package["vulnerabilities"], words, strict=True):
        record["database_specific"] = {} if word is None else {"severity": word}
    return body


@pytest.mark.parametrize(
    ("words", "rating"),
    [
        (["MODERATE", None], Severity.MEDIUM),
        (["LOW", "HIGH"], Severity.HIGH),
        (["MODERATE", "something-new"], Severity.UNKNOWN),
        ([None, None], Severity.UNKNOWN),
    ],
)
def test_without_a_score_the_databases_words_decide_and_never_a_guess(
    root: Path, words: list[str | None], rating: Severity
) -> None:
    """Why: a vulnerability nobody has scored is `unknown`, which blocks; not `low`."""
    (finding,) = osv(root, _without_score(root, words))
    assert finding.severity is rating


def test_an_osv_record_outside_every_group_is_refused(root: Path) -> None:
    """Why: grouping must not be how a vulnerability falls out of the report."""
    body = as_json("osv-seeded.json", root=str(root))
    package = body["results"][0]["packages"][0]
    package["groups"][0]["ids"] = ["PYSEC-2021-142"]
    with pytest.raises(KilnError, match="outside every group"):
        osv(root, body)


def test_an_osv_group_naming_a_missing_record_is_refused(root: Path) -> None:
    """Why: a group the report cannot back has no severity or title to trust."""
    body = as_json("osv-seeded.json", root=str(root))
    body["results"][0]["packages"][0]["groups"][0]["ids"].append("GHSA-none")
    with pytest.raises(KilnError, match="lacks"):
        osv(root, body)


def test_an_osv_lockfile_outside_the_repo_is_refused(root: Path) -> None:
    """Why: every location must be a path in the repo, so a finding can be found again."""
    raw = fixture("osv-seeded.json", root="/somewhere/else")
    with pytest.raises(KilnError, match="outside the repo"):
        findings.read_osv(raw, root=root)


# --- Trivy -----------------------------------------------------------------------------------


def trivy(body: dict[str, Any], target: str = "tests/seeded-findings/trivy") -> tuple[Finding, ...]:
    return findings.read_trivy(json.dumps(body).encode(), target=target)


def test_trivy_misconfigurations_keep_their_lines_and_severity() -> None:
    """Why: DS-0002 is the seeded finding, and a whole-file check has no line to show."""
    by_rule = {f.rule: f for f in trivy(as_json("trivy-seeded.json"))}
    assert by_rule["DS-0002"].severity is Severity.HIGH
    assert by_rule["DS-0002"].location.where() == "tests/seeded-findings/trivy/Dockerfile:3"
    assert by_rule["DS-0026"].severity is Severity.LOW
    assert by_rule["DS-0026"].location.where() == "tests/seeded-findings/trivy/Dockerfile"


def test_trivy_vulnerabilities_are_packages() -> None:
    """Why: when image scanning arrives, its vulnerabilities must not be dropped as unknown."""
    (finding,) = trivy(as_json("trivy-vulnerability.json"), target=".")
    assert finding.rule == "CVE-2020-14343"
    assert finding.severity is Severity.CRITICAL
    assert finding.cwe == ("CWE-20",)
    assert finding.location == PackageLocation(
        path="requirements.txt", ecosystem="pip", package="pyyaml", version="5.3.1"
    )


def test_a_trivy_report_with_no_results_has_no_findings() -> None:
    """Why: Trivy leaves `Results` out when nothing matched; that is a clean scan."""
    body = as_json("trivy-seeded.json")
    del body["Results"]
    assert trivy(body) == ()


@pytest.mark.parametrize("section", ["Secrets", "Licenses"])
def test_trivy_sections_kiln_does_not_read_are_refused(section: str) -> None:
    """Why: findings in a section nobody reads would pass silently."""
    body = as_json("trivy-seeded.json")
    body["Results"][0][section] = [{"RuleID": "x"}]
    with pytest.raises(KilnError, match=section.lower()):
        trivy(body)


def test_a_trivy_check_that_did_not_fail_is_refused() -> None:
    """Why: Kiln asks Trivy for failures only; anything else means its flags changed."""
    body = as_json("trivy-seeded.json")
    body["Results"][0]["Misconfigurations"][0]["Status"] = "PASS"
    with pytest.raises(KilnError, match="status 'PASS'"):
        trivy(body)


def test_another_trivy_report_schema_is_refused() -> None:
    """Why: a new schema can move a field the reader trusts."""
    body = as_json("trivy-seeded.json")
    body["SchemaVersion"] = 3
    with pytest.raises(KilnError, match="schema 3"):
        trivy(body)


@pytest.mark.parametrize(
    ("name", "path", "value"),
    [
        ("semgrep", ("results", 0, "extra", "severity"), "SEVERE"),
        ("trivy", ("Results", 0, "Misconfigurations", 0, "Severity"), "SEVERE"),
    ],
)
def test_a_severity_no_mapping_covers_is_refused(
    root: Path, name: str, path: tuple[str | int, ...], value: str
) -> None:
    """Why: a scanner's new severity word must not be graded by guesswork."""
    body = as_json(f"{name}-seeded.json", prefix=PREFIX)
    node: Any = body
    for part in path[:-1]:
        node = node[part]
    node[path[-1]] = value
    with pytest.raises(KilnError, match="does not map"):
        semgrep(root, body) if name == "semgrep" else trivy(body)


@pytest.mark.parametrize("scanner", list(Scanner))
def test_a_report_that_is_not_json_is_refused(root: Path, scanner: Scanner) -> None:
    """Why: a truncated report must fail, not read as no findings."""
    with pytest.raises(KilnError, match="not JSON"):
        if scanner is Scanner.SEMGREP:
            findings.read_semgrep(b"{", root=root, rule_prefix=PREFIX)
        elif scanner is Scanner.OSV_SCANNER:
            findings.read_osv(b"{", root=root)
        else:
            findings.read_trivy(b"{", target=".")


# --- Reports, dismissals and the blocking rule ------------------------------------------------


def report(*found: Finding, seeded: bool = False) -> ScanReport:
    return ScanReport(
        scanner=Scanner.TRIVY,
        version="v0.0.1",
        rules="fixture checks",
        target=".",
        seeded=seeded,
        raw=content_hash(b"fixture"),
        findings=tuple(sorted(found, key=lambda f: f.key)),
    )


def dismissal(finding: Finding, **overrides: Any) -> Dismissal:
    fields: dict[str, Any] = {
        "key": finding.key,
        "scanner": finding.scanner,
        "rule": finding.rule,
        "path": finding.location.path,
        "reason": "Placeholder reason.",
        "by": Actor.BUILD_SESSION,
        "dismissed_on": date(2026, 11, 18),
    }
    fields.update(overrides)
    return Dismissal.model_validate(fields)


@pytest.fixture
def seeded_trivy() -> tuple[Finding, ...]:
    return trivy(as_json("trivy-seeded.json"), target=".")


def test_an_open_high_finding_blocks(seeded_trivy: tuple[Finding, ...]) -> None:
    """Why: the charter's rule: critical and high findings are fixed or explained."""
    assessment = findings.assess(report(*seeded_trivy), DismissalList(), BLOCKING)
    assert [f.rule for f in assessment.open_blocking] == ["DS-0002"]


def test_a_dismissal_with_a_reason_lifts_exactly_its_finding(
    seeded_trivy: tuple[Finding, ...],
) -> None:
    """Why: "fix or explain"; the explanation covers one finding, by key, and no other."""
    high = next(f for f in seeded_trivy if f.rule == "DS-0002")
    assessment = findings.assess(
        report(*seeded_trivy), DismissalList(dismissals=(dismissal(high),)), BLOCKING
    )
    assert assessment.open_blocking == ()
    assert [d.finding.rule for d in assessment.dismissed] == ["DS-0002"]
    assert [f.rule for f in assessment.open] == ["DS-0026"]


def test_a_dismissal_that_matches_nothing_is_reported_stale(
    seeded_trivy: tuple[Finding, ...],
) -> None:
    """Why: a list of dismissals for findings long gone hides how much was set aside."""
    high = next(f for f in seeded_trivy if f.rule == "DS-0002")
    gone = dismissal(high, key=content_hash(b"something else"))
    assessment = findings.assess(report(*seeded_trivy), DismissalList(dismissals=(gone,)), BLOCKING)
    assert assessment.stale == (gone,)
    assert "stale dismissal" in findings.render(assessment)


def test_a_dismissal_that_disagrees_with_its_finding_is_refused(
    seeded_trivy: tuple[Finding, ...],
) -> None:
    """Why: a key copied onto the wrong entry would hide a finding nobody judged."""
    high = next(f for f in seeded_trivy if f.rule == "DS-0002")
    wrong = dismissal(high, rule="DS-0026")
    with pytest.raises(KilnError, match="but that key is DS-0002"):
        findings.assess(report(*seeded_trivy), DismissalList(dismissals=(wrong,)), BLOCKING)


def test_a_seeded_run_takes_no_dismissals(seeded_trivy: tuple[Finding, ...]) -> None:
    """Why: a seeded finding exists to be found; dismissing it would hide a broken scanner."""
    high = next(f for f in seeded_trivy if f.rule == "DS-0002")
    assessment = findings.assess(
        report(*seeded_trivy, seeded=True), DismissalList(dismissals=(dismissal(high),)), BLOCKING
    )
    assert [f.rule for f in assessment.open_blocking] == ["DS-0002"]


def test_another_scanners_dismissals_do_not_apply(seeded_trivy: tuple[Finding, ...]) -> None:
    """Why: each scan judges its own findings, and is not stale for another's."""
    high = next(f for f in seeded_trivy if f.rule == "DS-0002")
    other = dismissal(high, scanner=Scanner.SEMGREP)
    assessment = findings.assess(
        report(*seeded_trivy), DismissalList(dismissals=(other,)), BLOCKING
    )
    assert assessment.stale == ()
    assert len(assessment.open_blocking) == 1


def test_a_key_may_be_dismissed_only_once(seeded_trivy: tuple[Finding, ...]) -> None:
    """Why: two reasons for one finding leave nobody sure which was accepted."""
    high = next(f for f in seeded_trivy if f.rule == "DS-0002")
    with pytest.raises(ValueError, match="dismissed once"):
        DismissalList(dismissals=(dismissal(high), dismissal(high, reason="Another reason.")))


def test_the_repos_dismissal_list_loads(repo_root: Path) -> None:
    """Why: a broken dismissal list would fail every scan in CI at once."""
    findings.load_dismissals(repo_root / "config" / "dismissals.yaml")


@pytest.mark.parametrize(
    ("text", "message"),
    [
        (None, "missing"),
        ("dismissals: [", "not valid YAML"),
        ("dismissals:\n  - key: sha256:abc\n", "invalid"),
    ],
)
def test_a_bad_dismissal_list_is_loud(tmp_path: Path, text: str | None, message: str) -> None:
    """Why: a typo in a dismissal must stop the scan, not quietly dismiss nothing."""
    path = tmp_path / "dismissals.yaml"
    if text is not None:
        path.write_text(text, encoding="utf-8")
    with pytest.raises(KilnError, match=message):
        findings.load_dismissals(path)


def test_a_report_keeps_its_findings_sorted_and_distinct(
    seeded_trivy: tuple[Finding, ...],
) -> None:
    """Why: the same scan must give the same bytes, and one key must mean one finding."""
    fields = {**report(*seeded_trivy).model_dump(), "findings": seeded_trivy[::-1]}
    with pytest.raises(ValueError, match="sorted by key"):
        ScanReport.model_validate(fields)


def test_the_summary_puts_blocking_findings_first_and_marks_them(
    seeded_trivy: tuple[Finding, ...],
) -> None:
    """Why: a CI log is read from the top; the finding that failed it must be there."""
    text = findings.render(findings.assess(report(*seeded_trivy), DismissalList(), BLOCKING))
    lines = text.splitlines()
    assert "2 finding(s): 0 critical, 1 high, 0 unknown, 0 medium, 1 low" in lines[1]
    assert lines[2].startswith("  BLOCKING high  DS-0002")
    assert any(line.startswith("  low  DS-0026") for line in lines)
    assert f"key {seeded_trivy[0].key}" in text
