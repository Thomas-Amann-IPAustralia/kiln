"""Decision records: the decisions the Council makes while building a solution, `DEC-0001` on.

One record format for every expert (charter, "The shared core"). Each record is one file,
`DEC-NNNN-<slug>.md`, in the solution's decision directory: front matter that is the record,
then its rendering (`kiln.recordfile`). Numbers run from 0001 without gaps. A record is never
rewritten except to mark it superseded, and a new record says which one it supersedes.

Each expert's domain fields (an architecture decision's drivers and fitness functions, for
one) arrive as extensions with that expert, from phase 1.
"""

from __future__ import annotations

import re
from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Annotated

from pydantic import Field, model_validator

from kiln import recordfile
from kiln.errors import KilnError
from kiln.ids import DecisionId, EvidenceRef, RecordKind, parse_record_id, record_id
from kiln.model import Record, Text
from kiln.vocabulary import EXPERTS, Actor, Basis

_FILE = re.compile(r"^(DEC-\d{4,})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
_NEEDS_NO_EVIDENCE = frozenset({Basis.ASSUMED, Basis.UNKNOWN})


class DecisionStatus(StrEnum):
    PROPOSED = "proposed"
    """Recorded, and awaiting its owning expert (the Red band)."""
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    """Considered and declined; kept so it is not reopened without new evidence."""
    SUPERSEDED = "superseded"


class Reversibility(StrEnum):
    """How hard the decision is to undo (Solution proposal, decision fields)."""

    EASY = "easy"
    MODERATE = "moderate"
    COSTLY = "costly"
    IRREVERSIBLE = "irreversible"


class Dissent(Record):
    """An expert's disagreement, in that expert's own words, shown to Tom unedited."""

    by: Actor
    text: Text

    @model_validator(mode="after")
    def _by_an_expert(self) -> Dissent:
        if self.by not in EXPERTS:
            raise ValueError(f"dissent is written by a Council expert, not {self.by.value!r}")
        return self


class DecisionDraft(Record):
    """A decision record before the store numbers it."""

    title: Text
    status: DecisionStatus = DecisionStatus.ACCEPTED
    actor: Actor
    """Who decided: the owning expert, or Tom for an override."""
    decided_on: date
    context: Text
    """Why a decision was needed."""
    decision: Text
    """What was chosen."""
    options: Annotated[list[Text], Field(min_length=2)]
    """The alternatives considered, the chosen one included."""
    basis: Basis
    evidence: list[EvidenceRef] = Field(default_factory=list[EvidenceRef])
    reversibility: Reversibility
    consequences: Text
    dissent: list[Dissent] = Field(default_factory=list[Dissent])
    supersedes: DecisionId | None = None

    @model_validator(mode="after")
    def _consistent(self) -> DecisionDraft:
        if self.basis not in _NEEDS_NO_EVIDENCE and not self.evidence:
            raise ValueError(
                f"basis {self.basis.value!r} needs evidence; only `assumed` and `unknown` "
                "stand without it"
            )
        if len(set(self.options)) != len(self.options):
            raise ValueError("an option is listed twice")
        if any(dissent.by is self.actor for dissent in self.dissent):
            raise ValueError("the deciding expert cannot dissent from its own decision")
        return self


class DecisionRecord(DecisionDraft):
    """A numbered decision record."""

    id: DecisionId
    superseded_by: DecisionId | None = None

    @model_validator(mode="after")
    def _superseded_consistently(self) -> DecisionRecord:
        if (self.status is DecisionStatus.SUPERSEDED) != (self.superseded_by is not None):
            raise ValueError("status `superseded` goes with `superseded_by`, and only with it")
        if self.id in (self.supersedes, self.superseded_by):
            raise ValueError("a record cannot supersede itself")
        return self

    @property
    def number(self) -> int:
        return parse_record_id(self.id)[1]

    @property
    def file_name(self) -> str:
        return f"{self.id}-{recordfile.slugify(self.title)}.md"


def render(record: DecisionRecord) -> str:
    """The Markdown body of a decision record. It adds nothing the record does not hold."""
    lines = [
        f"# {record.id}: {record.title}",
        "",
        "| | |",
        "| --- | --- |",
        f"| Status | {_status_cell(record)} |",
        f"| Decided by | {record.actor.value} |",
        f"| Decided on | {record.decided_on.isoformat()} |",
        f"| Basis | {record.basis.value} |",
        f"| Reversibility | {record.reversibility.value} |",
    ]
    if record.supersedes:
        lines.append(f"| Supersedes | {record.supersedes} |")
    lines += ["", "## Context", "", record.context.strip(), ""]
    lines += ["## Decision", "", record.decision.strip(), ""]
    lines += ["## Options considered", ""]
    lines += [f"- {option}" for option in record.options]
    lines += ["", "## Evidence", ""]
    lines += [f"- `{ref}`" for ref in record.evidence] or ["None. The basis is stated above."]
    lines += ["", "## Consequences", "", record.consequences.strip(), ""]
    lines += ["## Dissent", ""]
    for dissent in record.dissent:
        lines += [f"**{dissent.by.value}:**", "", dissent.text.strip(), ""]
    if not record.dissent:
        lines += ["None recorded.", ""]
    lines += [_GENERATED]
    return "\n".join(lines)


_GENERATED = (
    "<!-- Rendered from the front matter by Kiln. Edit the front matter, then run "
    "`kiln records render`. -->"
)


def _status_cell(record: DecisionRecord) -> str:
    if record.superseded_by:
        return f"superseded by {record.superseded_by}"
    return record.status.value


def _text(record: DecisionRecord) -> str:
    return recordfile.compose(record, render(record))


class DecisionStore:
    """The decision records in one directory, read and written whole files at a time.

    Every read validates the whole directory first, so a gap, a duplicate or a hand-edited
    rendering stops the caller instead of being worked around.
    """

    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def problems(self) -> list[KilnError]:
        """Everything wrong with the directory, in file order. Empty when it is sound."""
        return self._scan()[1]

    def records(self) -> list[DecisionRecord]:
        """Every record, in number order. Raises the first problem if the directory is unsound."""
        records, problems = self._scan()
        if problems:
            raise problems[0]
        return records

    def _scan(self) -> tuple[list[DecisionRecord], list[KilnError]]:
        records: list[DecisionRecord] = []
        problems: list[KilnError] = []
        paths = sorted(self.directory.glob("*.md")) if self.directory.is_dir() else []
        for path in paths:
            if _FILE.match(path.name) is None:
                problems.append(KilnError("file name is not `DEC-NNNN-slug.md`", item=str(path)))
                continue
            try:
                record = recordfile.load(
                    path.read_text(encoding="utf-8"), DecisionRecord, render, item=str(path)
                )
            except KilnError as exc:
                problems.append(exc)
                continue
            if path.name != record.file_name:
                problems.append(
                    KilnError(f"file name should be {record.file_name}", item=str(path))
                )
            expected = len(records) + 1
            if record.number != expected:
                problems.append(
                    KilnError(
                        f"expected {record_id(RecordKind.DECISION, expected)} next; "
                        "numbers must not skip or repeat",
                        item=str(path),
                    )
                )
            records.append(record)
        by_id = {record.id: record for record in records}
        for record in records:
            problems += _link_problems(record, by_id, self.directory)
        return records, problems

    def get(self, decision_id: str) -> DecisionRecord:
        for record in self.records():
            if record.id == decision_id:
                return record
        raise KilnError("no such decision record", item=decision_id, see=str(self.directory))

    def add(self, draft: DecisionDraft) -> DecisionRecord:
        """Number and write a new record. If it supersedes one, mark that one superseded."""
        existing = {record.id: record for record in self.records()}
        if draft.status is DecisionStatus.SUPERSEDED:
            raise KilnError("a new record cannot start superseded", item=draft.title)
        old = None
        if draft.supersedes is not None:
            old = existing.get(draft.supersedes)
            if old is None:
                raise KilnError("supersedes a record that does not exist", item=draft.supersedes)
            if old.superseded_by is not None:
                raise KilnError(f"already superseded by {old.superseded_by}", item=draft.supersedes)
        new_id = record_id(RecordKind.DECISION, len(existing) + 1)
        record = DecisionRecord(id=new_id, **draft.model_dump())
        recordfile.write_atomic(self.directory / record.file_name, _text(record), exclusive=True)
        if old is not None:
            marked = old.model_copy(
                update={"status": DecisionStatus.SUPERSEDED, "superseded_by": new_id}
            )
            recordfile.write_atomic(self.directory / old.file_name, _text(marked))
        return record


def _link_problems(
    record: DecisionRecord, records: dict[str, DecisionRecord], directory: Path
) -> list[KilnError]:
    item = str(directory / record.file_name)
    problems: list[KilnError] = []
    if record.supersedes is not None:
        old = records.get(record.supersedes)
        if old is None:
            problems.append(
                KilnError(f"supersedes {record.supersedes}, which is missing", item=item)
            )
        elif old.superseded_by != record.id:
            problems.append(
                KilnError(
                    f"supersedes {record.supersedes}, which does not say it is superseded by "
                    f"{record.id}",
                    item=item,
                )
            )
    if record.superseded_by is not None:
        new = records.get(record.superseded_by)
        if new is None or new.supersedes != record.id:
            problems.append(
                KilnError(
                    f"says it is superseded by {record.superseded_by}, which does not say it "
                    f"supersedes {record.id}",
                    item=item,
                )
            )
    return problems
