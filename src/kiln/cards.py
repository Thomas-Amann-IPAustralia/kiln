"""Decision cards: every decision put to Tom, as a typed record (ADR-0030).

A card holds the question, the options and what each costs or changes, a recommendation, any
dissent, whether it can be undone, what happens without an answer, and exactly what Tom is
approving: each file it rests on, by content hash. When Tom answers, his answer is written into
the card in his own words.

**An approval is Tom's merge, into `main`, of a card that holds his answer** (ADR-0028). A
merged card without an answer approves nothing: a merged question is not an answer (D-010).
The card never says whether it is approved; that is read from `main`'s history by
`kiln.approvals`, because a field anyone can write proves nothing.

Cards live one per file, `CARD-NNNN-<slug>.md`, numbered without gaps (`kiln.recordfile`).
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator, model_validator

from kiln import recordfile
from kiln.errors import KilnError
from kiln.ids import CardId, ContentHash, RecordKind, content_hash, parse_record_id, record_id
from kiln.model import Record, RepoPath, Text
from kiln.vocabulary import Actor, Gate

CARDS_DIR = Path("docs/cards")
_FILE = re.compile(r"^(CARD-\d{4,})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")

OptionLabel = Annotated[str, Field(min_length=1, max_length=40, pattern=r"^\S(?:.*\S)?$")]


class Option(Record):
    label: OptionLabel
    """What Tom would answer: a word or two."""
    consequences: Text
    """What choosing it would cost or change."""


class Recommendation(Record):
    option: OptionLabel
    reason: Text


class CardDissent(Record):
    """A recorded disagreement with the recommendation, unedited."""

    by: Actor
    text: Text


class Undo(Record):
    possible: bool
    how: Text
    """How it would be undone, or why it cannot be."""


class RestsOn(Record):
    """One file the decision rests on, at one exact version."""

    path: RepoPath
    sha256: ContentHash


class GateDecision(Record):
    """Marks a card as Tom's decision at one of his gates, and which answer passes it."""

    gate: Gate
    pass_option: OptionLabel
    """The option that lets the solution through the gate, such as `Approve`."""

    @field_validator("gate")
    @classmethod
    def _toms_gate(cls, gate: Gate) -> Gate:
        if not gate.tom_decides:
            raise ValueError(f"{gate.value} is passed by a validation node, not by Tom")
        return gate


class Answer(Record):
    """Tom's answer, in his words. Only Tom answers a card."""

    choice: OptionLabel
    words: Text
    """What Tom said, verbatim."""
    answered_on: date
    """Not `on`: YAML 1.1 reads a bare `on` key as the boolean true."""


class DecisionCard(Record):
    id: CardId
    title: Text
    put_by: Actor
    put_on: date
    question: Text
    """Answerable in a word or two."""
    options: Annotated[list[Option], Field(min_length=2)]
    recommendation: Recommendation
    dissent: list[CardDissent] = Field(default_factory=list[CardDissent])
    undo: Undo
    if_no_answer: Text
    rests_on: Annotated[list[RestsOn], Field(min_length=1)]
    """Exactly what Tom is approving."""
    gate: GateDecision | None = None
    """Set when the card is Tom's decision at a gate (`kiln.gates`)."""
    supersedes: CardId | None = None
    answer: Answer | None = None

    @model_validator(mode="after")
    def _consistent(self) -> DecisionCard:
        labels = [option.label for option in self.options]
        if len(set(labels)) != len(labels):
            raise ValueError("two options share a label")
        if self.recommendation.option not in labels:
            raise ValueError(f"the recommendation {self.recommendation.option!r} is not an option")
        if self.answer is not None:
            if self.answer.choice not in labels:
                raise ValueError(f"the answer {self.answer.choice!r} is not an option")
            if self.answer.answered_on < self.put_on:
                raise ValueError("the card is answered before it was put")
        paths = [item.path for item in self.rests_on]
        if len(set(paths)) != len(paths):
            raise ValueError("a file is listed twice in rests_on")
        if self.put_by is Actor.TOM:
            raise ValueError("a card is put to Tom, not by him")
        if self.gate is not None and self.gate.pass_option not in labels:
            raise ValueError(f"the gate's pass option {self.gate.pass_option!r} is not an option")
        if self.supersedes == self.id:
            raise ValueError("a card cannot supersede itself")
        return self

    @property
    def number(self) -> int:
        return parse_record_id(self.id)[1]

    @property
    def file_name(self) -> str:
        return f"{self.id}-{recordfile.slugify(self.title)}.md"


def render(card: DecisionCard) -> str:
    """The card as Tom reads it. It adds nothing the record does not hold."""
    lines = [f"# {card.id}: {card.title}", "", f"**The question.** {card.question.strip()}", ""]
    lines += ["| Option | What it costs or changes |", "| --- | --- |"]
    lines += [f"| {_cell(o.label)} | {_cell(o.consequences)} |" for o in card.options]
    lines += [
        "",
        f"**Recommended: {card.recommendation.option}.** {card.recommendation.reason.strip()}",
        "",
    ]
    if card.dissent:
        lines += ["**Dissent.**", ""]
        lines += [f"- **{d.by.value}:** {d.text.strip()}" for d in card.dissent]
        lines += [""]
    else:
        lines += ["**Dissent.** None recorded.", ""]
    can = "Yes" if card.undo.possible else "No"
    lines += [f"**Can it be undone?** {can}. {card.undo.how.strip()}", ""]
    lines += [f"**If Tom does not answer.** {card.if_no_answer.strip()}", ""]
    lines += ["**What Tom is approving.** These files, at exactly these versions:", ""]
    lines += ["| File | sha256 |", "| --- | --- |"]
    lines += [f"| `{r.path}` | `{r.sha256.removeprefix('sha256:')}` |" for r in card.rests_on]
    lines += [""]
    if card.gate:
        lines += [
            f"**Gate.** This is Tom's decision at {card.gate.gate.value} "
            f"({card.gate.gate.label}). Answering {card.gate.pass_option!r} passes it.",
            "",
        ]
    if card.supersedes:
        lines += [f"**Supersedes** {card.supersedes}.", ""]
    lines += [f"Put by {card.put_by.value} on {card.put_on.isoformat()}.", ""]
    if card.answer is None:
        lines += ["**Answer.** Not yet answered.", ""]
    else:
        lines += [
            f"**Answer: {card.answer.choice}.** Tom, {card.answer.answered_on.isoformat()}: "
            f"“{card.answer.words.strip()}”",
            "",
            "The answer takes effect when Tom merges this card into `main`. "
            "`kiln approvals` shows whether it has.",
            "",
        ]
    lines += [
        "<!-- Rendered from the front matter by Kiln. Edit the front matter, then run "
        "`kiln records render`. -->"
    ]
    return "\n".join(lines)


def _cell(text: str) -> str:
    return " ".join(text.split()).replace("|", "\\|")


def card_text(card: DecisionCard) -> str:
    """The whole card file: front matter, then rendering."""
    return recordfile.compose(card, render(card))


def parse_card(text: str, *, item: str) -> DecisionCard:
    """Validate a card's front matter, whether or not its body is the canonical rendering."""
    return recordfile.parse(text, DecisionCard, item=item)


def load_card(text: str, *, item: str) -> DecisionCard:
    """Validate a card, and require the file to be exactly its rendering."""
    return recordfile.load(text, DecisionCard, render, item=item)


def check_cards(root: Path, directory: Path = CARDS_DIR) -> list[KilnError]:
    """Check the cards in the working tree: names, numbering, renderings, links, and that each
    card still rests on the files it names, unless a later card supersedes it.

    A changed file under an approved card fails here, before the commit, so a change to what
    Tom approved needs a new card, not a quiet edit (ADR-0028).
    """
    folder = root / directory
    if not folder.is_dir():
        return []
    problems: list[KilnError] = []
    cards: list[tuple[Path, DecisionCard]] = []
    for path in sorted(folder.glob("*.md")):
        item = str(directory / path.name)
        if _FILE.match(path.name) is None:
            problems.append(KilnError("file name is not `CARD-NNNN-slug.md`", item=item))
            continue
        try:
            card = load_card(path.read_text(encoding="utf-8"), item=item)
        except KilnError as exc:
            problems.append(exc)
            continue
        if path.name != card.file_name:
            problems.append(KilnError(f"file name should be {card.file_name}", item=item))
        expected = len(cards) + 1
        if card.number != expected:
            problems.append(
                KilnError(
                    f"expected {record_id(RecordKind.CARD, expected)} next; numbers must not "
                    "skip or repeat",
                    item=item,
                )
            )
        cards.append((path, card))
    ids = {card.id for _, card in cards}
    superseded = {card.supersedes for _, card in cards if card.supersedes}
    for path, card in cards:
        item = str(directory / path.name)
        if card.supersedes and card.supersedes not in ids:
            problems.append(KilnError(f"supersedes {card.supersedes}, which is missing", item=item))
        if card.id in superseded:
            continue
        problems += [
            KilnError(message, item=item) for message in rests_on_problems(root, card.rests_on)
        ]
    return problems


def rests_on_problems(root: Path, rests_on: list[RestsOn]) -> list[str]:
    """Where the working tree no longer holds the exact files a card names."""
    problems: list[str] = []
    for entry in rests_on:
        path = root / entry.path
        if not path.is_file():
            problems.append(f"rests on {entry.path}, which is missing")
            continue
        actual = content_hash(path.read_bytes())
        if actual != entry.sha256:
            problems.append(
                f"rests on {entry.path} at {entry.sha256}, but the file is now {actual}: "
                "a change to what a card names needs a new card that supersedes it"
            )
    return problems


def render_cards(root: Path, directory: Path = CARDS_DIR) -> list[Path]:
    """Rewrite each card file as its canonical rendering. Returns the files that changed."""
    folder = root / directory
    changed: list[Path] = []
    for path in sorted(folder.glob("*.md")) if folder.is_dir() else []:
        text = path.read_text(encoding="utf-8")
        canonical = card_text(parse_card(text, item=str(directory / path.name)))
        if canonical != text:
            recordfile.write_atomic(path, canonical)
            changed.append(directory / path.name)
    return changed
