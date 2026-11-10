"""`kiln records check`: do the repo's records still agree with each other?

The records are how one session hands work to the next (CLAUDE.md, "Records"). Each check here
guards a way they have gone stale before: a skipped decision number, an ADR missing from its
index, a handover that names the wrong next number, a seed document changed under its
snapshot, a link to a file that moved.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

DECISIONS = Path("docs/decisions.md")
HANDOVER = Path("docs/handover.md")
ADR_DIR = Path("docs/adr")
SEEDS_DIR = Path("docs/repo-seeds")
SEEDS_MANIFEST = SEEDS_DIR / "MANIFEST.sha256"
SEEDS_UNSEALED = frozenset({"MANIFEST.sha256", "README.md"})

ADR_STATUSES = ("proposed", "accepted", "deprecated", "superseded by ADR-")

_DECISION_HEADING = re.compile(r"^## D-(\d{3}) — .+ \((\d{4}-\d{2}-\d{2})\)$")
_ANY_DECISION_HEADING = re.compile(r"^## D-")
_ADR_FILE = re.compile(r"^(\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
_STATUS_LINE = re.compile(r"^status: (.+)$", re.MULTILINE)
_SUPERSEDED_BY = re.compile(r"^superseded by ADR-(\d{4})$")
_NEXT_FREE = re.compile(r"[Nn]ext free decision number:\** \**D-(\d{3})")
_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
_FENCE = re.compile(r"^(```|~~~).*?^\1\s*$", re.MULTILINE | re.DOTALL)
_INLINE_CODE = re.compile(r"`[^`\n]*`")


@dataclass(frozen=True)
class Problem:
    """One disagreement between records, with the file to open."""

    path: Path
    message: str

    def one_line(self) -> str:
        return f"{self.path}: {self.message}"


def decision_numbers(root: Path) -> list[int]:
    """The decision numbers in the log, in file order (well-formed headings only)."""
    text = (root / DECISIONS).read_text(encoding="utf-8")
    return [int(m.group(1)) for line in text.splitlines() if (m := _DECISION_HEADING.match(line))]


def check_decisions(root: Path) -> list[Problem]:
    path = root / DECISIONS
    if not path.is_file():
        return [Problem(DECISIONS, "the decision log is missing")]
    problems: list[Problem] = []
    expected, last_date = 1, date.min
    for line in path.read_text(encoding="utf-8").splitlines():
        if not _ANY_DECISION_HEADING.match(line):
            continue
        match = _DECISION_HEADING.match(line)
        if match is None:
            problems.append(
                Problem(DECISIONS, f"heading is not `## D-NNN — Title (YYYY-MM-DD)`: {line!r}")
            )
            continue
        number, when = int(match.group(1)), date.fromisoformat(match.group(2))
        if number != expected:
            problems.append(
                Problem(DECISIONS, f"expected D-{expected:03d} next, found D-{number:03d}")
            )
        if when < last_date:
            problems.append(
                Problem(
                    DECISIONS,
                    f"D-{number:03d} is dated before the entry above it; the log is append-only",
                )
            )
        expected, last_date = number + 1, max(last_date, when)
    if expected == 1:
        problems.append(Problem(DECISIONS, "no decision entries found"))
    return problems


def check_handover(root: Path) -> list[Problem]:
    path = root / HANDOVER
    if not path.is_file():
        return [Problem(HANDOVER, "the handover note is missing")]
    match = _NEXT_FREE.search(path.read_text(encoding="utf-8"))
    if match is None:
        return [Problem(HANDOVER, "no `Next free decision number: D-NNN` line")]
    numbers = decision_numbers(root) if (root / DECISIONS).is_file() else []
    want = max(numbers, default=0) + 1
    if int(match.group(1)) != want:
        return [
            Problem(
                HANDOVER,
                f"says the next free decision number is D-{int(match.group(1)):03d}; "
                f"the log makes it D-{want:03d}",
            )
        ]
    return []


def check_adrs(root: Path) -> list[Problem]:
    directory = root / ADR_DIR
    if not directory.is_dir():
        return [Problem(ADR_DIR, "the ADR directory is missing")]
    problems: list[Problem] = []
    index_path = directory / "README.md"
    index = index_path.read_text(encoding="utf-8") if index_path.is_file() else ""
    if not index:
        problems.append(Problem(ADR_DIR / "README.md", "the ADR index is missing"))
    files = sorted(p for p in directory.glob("*.md") if p.name != "README.md")
    numbers: set[int] = set()
    superseders: list[tuple[Path, int]] = []
    for expected, path in enumerate(files, start=1):
        rel = ADR_DIR / path.name
        match = _ADR_FILE.match(path.name)
        if match is None:
            problems.append(Problem(rel, "file name is not `NNNN-lower-case-slug.md`"))
            continue
        number = int(match.group(1))
        numbers.add(number)
        if number != expected:
            problems.append(
                Problem(rel, f"expected ADR-{expected:04d} next; numbers must not skip")
            )
        text = path.read_text(encoding="utf-8")
        status = _STATUS_LINE.search(text.split("\n# ", 1)[0])
        if status is None:
            problems.append(Problem(rel, "no `status:` line in the front matter"))
        elif not status.group(1).startswith(ADR_STATUSES):
            problems.append(Problem(rel, f"unknown status {status.group(1)!r}"))
        elif superseded := _SUPERSEDED_BY.match(status.group(1)):
            superseders.append((rel, int(superseded.group(1))))
        if "\n# " not in "\n" + text:
            problems.append(Problem(rel, "no `# Title` heading"))
        if index and f"({path.name})" not in index:
            problems.append(Problem(ADR_DIR / "README.md", f"the index does not link {path.name}"))
    for rel, target in superseders:
        if target not in numbers:
            problems.append(Problem(rel, f"superseded by ADR-{target:04d}, which does not exist"))
    return problems


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_manifest(path: Path) -> dict[str, str]:
    """Parse `sha256sum` output: `<hex>  <name>` per line."""
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, name = line.split("  ", 1)
            entries[name] = digest
    return entries


def check_seeds(root: Path) -> list[Problem]:
    manifest_path = root / SEEDS_MANIFEST
    if not manifest_path.is_file():
        return [Problem(SEEDS_MANIFEST, "the seed manifest is missing")]
    sealed = read_manifest(manifest_path)
    present = {
        p.name for p in (root / SEEDS_DIR).iterdir() if p.is_file() and p.name not in SEEDS_UNSEALED
    }
    problems = [
        Problem(SEEDS_DIR / name, "sealed in the manifest but missing from disk")
        for name in sorted(sealed.keys() - present)
    ]
    problems += [
        Problem(
            SEEDS_DIR / name,
            "not in the manifest: a new seed needs reconciling with the live docs first",
        )
        for name in sorted(present - sealed.keys())
    ]
    problems += [
        Problem(
            SEEDS_DIR / name, "changed since it was sealed: reconcile the live docs, then reseal"
        )
        for name in sorted(present & sealed.keys())
        if sha256_of(root / SEEDS_DIR / name) != sealed[name]
    ]
    return problems


def live_markdown(root: Path) -> list[Path]:
    """Every Markdown file that is ours to keep current: all but the sealed seeds."""
    skip = {".git", ".venv", "node_modules"}
    return sorted(
        path
        for path in root.rglob("*.md")
        if not skip & set(path.relative_to(root).parts) and (root / SEEDS_DIR) not in path.parents
    )


def check_links(root: Path) -> list[Problem]:
    """Relative links in live Markdown must point at files that exist."""
    problems: list[Problem] = []
    for path in live_markdown(root):
        text = _INLINE_CODE.sub("", _FENCE.sub("", path.read_text(encoding="utf-8")))
        for target in _LINK.findall(text):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
                continue
            file_part = target.split("#", 1)[0].replace("%20", " ")
            if not (path.parent / file_part).exists():
                problems.append(Problem(path.relative_to(root), f"broken link: {target}"))
    return problems


def check_all(root: Path) -> list[Problem]:
    return [
        *check_decisions(root),
        *check_handover(root),
        *check_adrs(root),
        *check_seeds(root),
        *check_links(root),
    ]
