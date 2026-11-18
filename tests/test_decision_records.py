from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from kiln.decision_records import DecisionDraft, DecisionStatus, DecisionStore, render
from kiln.errors import KilnError
from kiln.ids import content_hash
from kiln.recordfile import slugify


def draft(**changes: Any) -> DecisionDraft:
    """A valid draft with placeholder text. Each test changes what it is about."""
    fields: dict[str, Any] = {
        "title": "Use the placeholder store",
        "actor": "solution_architect",
        "decided_on": date(2026, 11, 18),
        "context": "Placeholder context.",
        "decision": "Placeholder store.",
        "options": ["Placeholder store", "Another store"],
        "basis": "observed",
        "evidence": [content_hash(b"placeholder measurement")],
        "reversibility": "easy",
        "consequences": "Placeholder consequences.",
    }
    fields.update(changes)
    return DecisionDraft.model_validate(fields)


@pytest.fixture
def store(tmp_path: Path) -> DecisionStore:
    return DecisionStore(tmp_path / "council/decisions")


def test_records_are_numbered_from_dec_0001_and_named_by_slug(store: DecisionStore) -> None:
    """Why: DEC-NNNN is the contract every expert cites; it must never skip or repeat."""
    first = store.add(draft())
    second = store.add(draft(title="Second: a title, with punctuation!"))
    assert (first.id, second.id) == ("DEC-0001", "DEC-0002")
    names = sorted(p.name for p in store.directory.iterdir())
    assert names == [
        "DEC-0001-use-the-placeholder-store.md",
        "DEC-0002-second-a-title-with-punctuation.md",
    ]
    assert store.get("DEC-0002") == second


def test_writing_is_deterministic(tmp_path: Path) -> None:
    """Why: the same record must give byte-identical files, or hashes and diffs mean nothing."""
    texts: list[bytes] = []
    for name in ("a", "b"):
        record = DecisionStore(tmp_path / name).add(draft())
        texts.append((tmp_path / name / record.file_name).read_bytes())
    assert texts[0] == texts[1]


def test_the_body_is_rendered_from_the_record_alone(store: DecisionStore) -> None:
    """Why: Tom reads the body; it must say what the record says and nothing more."""
    record = store.add(draft(dissent=[{"by": "security_architect", "text": "Placeholder."}]))
    body = render(record)
    assert "# DEC-0001: Use the placeholder store" in body
    assert "**security_architect:**" in body
    assert record.evidence[0] in body


def test_a_hand_edited_body_is_refused(store: DecisionStore) -> None:
    """Why: a body that disagrees with its record would show Tom something machines ignore."""
    record = store.add(draft())
    path = store.directory / record.file_name
    path.write_text(path.read_text().replace("Placeholder consequences.\n\n##", "Edited.\n\n##"))
    with pytest.raises(KilnError, match="not its record's rendering"):
        store.records()


def test_a_gap_in_the_numbers_is_found(store: DecisionStore) -> None:
    """Why: a gap reads as a lost decision."""
    store.add(draft())
    second = store.add(draft(title="Second"))
    path = store.directory / second.file_name
    text = path.read_text().replace("DEC-0002", "DEC-0003")
    path.unlink()
    (store.directory / "DEC-0003-second.md").write_text(text)
    assert any("expected DEC-0002 next" in e.cause for e in store.problems())


def test_a_file_name_that_does_not_match_its_record_is_found(store: DecisionStore) -> None:
    """Why: people and links find a record by its file name."""
    record = store.add(draft())
    (store.directory / record.file_name).rename(store.directory / "DEC-0001-renamed.md")
    assert any("file name should be" in e.cause for e in store.problems())


def test_superseding_links_both_records(store: DecisionStore) -> None:
    """Why: records are superseded, never rewritten, and each must point at the other."""
    old = store.add(draft())
    new = store.add(draft(title="Replace the placeholder store", supersedes=old.id))
    old_now = store.get(old.id)
    assert old_now.status is DecisionStatus.SUPERSEDED
    assert old_now.superseded_by == new.id
    assert "superseded by DEC-0002" in render(old_now)
    with pytest.raises(KilnError, match="already superseded"):
        store.add(draft(title="Third", supersedes=old.id))


def test_a_one_sided_supersession_is_found(store: DecisionStore) -> None:
    """Why: an interrupted supersede leaves one side unmarked; the check must say so."""
    old = store.add(draft())
    store.add(draft(title="Replace it", supersedes=old.id))
    path = store.directory / old.file_name
    (store.directory / old.file_name).write_text(
        path.read_text()
        .replace("status: superseded", "status: accepted")
        .replace("superseded_by: DEC-0002", "superseded_by: null")
        .replace("| Status | superseded by DEC-0002 |", "| Status | accepted |")
    )
    assert any("does not say it is superseded" in e.cause for e in store.problems())


def test_an_existing_record_is_never_overwritten(store: DecisionStore) -> None:
    """Why: two writers picking the same number must not silently replace each other's record."""
    record = store.add(draft())
    store.directory.joinpath("DEC-0002-placeholder.md").write_text("")
    with pytest.raises(KilnError):
        store.add(draft(title="Placeholder"))
    assert store.directory.joinpath(record.file_name).exists()


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"options": ["Only one"]}, "at least 2 items"),
        ({"evidence": []}, "needs evidence"),
        ({"dissent": [{"by": "tom", "text": "No."}]}, "written by a Council expert"),
        ({"dissent": [{"by": "solution_architect", "text": "No."}]}, "own decision"),
        ({"options": ["Same", "Same"]}, "listed twice"),
    ],
)
def test_a_malformed_decision_is_refused(changes: dict[str, Any], message: str) -> None:
    """Why: the format's rules (alternatives, evidence for a basis, dissent by another expert)
    are what make a record worth trusting later."""
    with pytest.raises(ValidationError, match=message):
        draft(**changes)


def test_assumed_and_unknown_stand_without_evidence() -> None:
    """Why: missing evidence stays missing (rule 7); the basis says so instead."""
    assert draft(basis="assumed", evidence=[]).evidence == []


def test_slugs_are_ascii_and_bounded() -> None:
    """Why: file names must be portable and short enough to read on a phone."""
    assert slugify("Ça va: Café — OK?") == "ca-va-cafe-ok"
    assert len(slugify("word " * 40)) <= 60
    with pytest.raises(ValueError, match="at least one letter"):
        slugify("—")
