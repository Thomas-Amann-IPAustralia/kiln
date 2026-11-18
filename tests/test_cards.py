from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from kiln.cards import (
    CARDS_DIR,
    DecisionCard,
    card_text,
    check_cards,
    load_card,
    render_cards,
)
from kiln.errors import KilnError
from kiln.ids import content_hash

PLAN = "docs/plan.md"


def make_card(root: Path, number: int = 1, **changes: Any) -> DecisionCard:
    """A valid card resting on `docs/plan.md` as it is now in `root`. Placeholder text."""
    plan = root / PLAN
    fields: dict[str, Any] = {
        "id": f"CARD-{number:04d}",
        "title": f"Approve the placeholder plan {number}",
        "put_by": "build_session",
        "put_on": date(2026, 11, 18),
        "question": "Approve the placeholder plan?",
        "options": [
            {"label": "Approve", "consequences": "Placeholder work starts."},
            {"label": "Decline", "consequences": "Nothing starts."},
        ],
        "recommendation": {"option": "Approve", "reason": "Placeholder reason."},
        "undo": {"possible": True, "how": "Nothing is built yet."},
        "if_no_answer": "Nothing starts.",
        "rests_on": [{"path": PLAN, "sha256": content_hash(plan.read_bytes())}],
    }
    fields.update(changes)
    return DecisionCard.model_validate(fields)


def answer(**changes: Any) -> dict[str, Any]:
    return {
        "choice": "Approve",
        "words": "Placeholder yes.",
        "answered_on": date(2026, 11, 18),
    } | changes


def write_card(root: Path, card: DecisionCard) -> Path:
    path = root / CARDS_DIR / card.file_name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(card_text(card), encoding="utf-8")
    return path


@pytest.fixture
def root(tmp_path: Path) -> Path:
    (tmp_path / "docs").mkdir()
    (tmp_path / PLAN).write_text("# Placeholder plan\n")
    return tmp_path


def test_a_card_round_trips_through_its_file(root: Path) -> None:
    """Why: the file is the record; reading it back must give the same card exactly."""
    card = make_card(root, answer=answer())
    path = write_card(root, card)
    assert load_card(path.read_text(), item=str(path)) == card
    assert check_cards(root) == []


def test_the_rendering_shows_tom_everything_he_is_approving(root: Path) -> None:
    """Why: ADR-0030 lists what a card must show; Tom reads the body, not the YAML."""
    text = card_text(make_card(root))
    for expected in [
        "**The question.** Approve the placeholder plan?",
        "| Approve | Placeholder work starts. |",
        "**Recommended: Approve.**",
        "**Dissent.** None recorded.",
        "**Can it be undone?** Yes.",
        "**If Tom does not answer.** Nothing starts.",
        f"| `{PLAN}` |",
        "**Answer.** Not yet answered.",
    ]:
        assert expected in text


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"recommendation": {"option": "Maybe", "reason": "R."}}, "recommendation 'Maybe'"),
        ({"answer": answer(choice="Maybe")}, "answer 'Maybe'"),
        ({"answer": answer(answered_on=date(2026, 11, 1))}, "answered before"),
        ({"options": [{"label": "Approve", "consequences": "C."}]}, "at least 2 items"),
        ({"put_by": "tom"}, "put to Tom, not by him"),
        ({"rests_on": []}, "at least 1 item"),
        ({"rests_on": [{"path": "../outside.md", "sha256": content_hash(b"")}]}, "plain"),
        ({"rests_on": [{"path": PLAN, "sha256": "abc"}]}, "sha256"),
        ({"supersedes": "CARD-0001"}, "supersede itself"),
        ({"approved": True}, "Extra inputs"),
    ],
)
def test_a_malformed_card_is_refused(root: Path, changes: dict[str, Any], message: str) -> None:
    """Why: each rule closes a way a card could mislead Tom or claim an approval it lacks;
    an `approved` field in particular must not exist, since anyone could write it."""
    with pytest.raises(ValidationError, match=message):
        make_card(root, **changes)


def test_a_changed_file_under_a_card_fails_the_check(root: Path) -> None:
    """Why: a change to what Tom approved needs a new card, caught before the commit."""
    write_card(root, make_card(root, answer=answer()))
    (root / PLAN).write_text("# Placeholder plan, edited\n")
    problems = check_cards(root)
    assert len(problems) == 1
    assert "needs a new card that supersedes it" in problems[0].cause


def test_a_superseded_card_no_longer_pins_its_files(root: Path) -> None:
    """Why: once a newer card covers the change, the old hashes are history, not a problem."""
    write_card(root, make_card(root, answer=answer()))
    (root / PLAN).write_text("# Placeholder plan, revised\n")
    write_card(root, make_card(root, 2, supersedes="CARD-0001"))
    assert check_cards(root) == []


def test_numbering_names_and_rendering_are_checked(root: Path) -> None:
    """Why: the same structural rules as the decision log, for the same reasons."""
    write_card(root, make_card(root, 2))
    path = write_card(root, make_card(root, 1))
    path.write_text(path.read_text().replace("Not yet answered.", "Approved, honest."))
    causes = " ".join(problem.cause for problem in check_cards(root))
    assert "not its record's rendering" in causes
    (root / CARDS_DIR / "notes.md").write_text("stray\n")
    assert "CARD-NNNN-slug.md" in " ".join(problem.cause for problem in check_cards(root))


def test_render_rewrites_a_hand_edited_card_into_canonical_form(root: Path) -> None:
    """Why: authors edit the front matter by hand; render makes the file the record again."""
    path = write_card(root, make_card(root))
    text = path.read_text().replace(
        "answer: null",
        "answer:\n  choice: Approve\n  words: Placeholder yes.\n  answered_on: 2026-11-18",
    )
    path.write_text(text)
    assert render_cards(root) == [CARDS_DIR / path.name]
    assert "**Answer: Approve.**" in path.read_text()
    assert check_cards(root) == []
    assert render_cards(root) == []


def test_render_refuses_an_invalid_card(root: Path) -> None:
    """Why: render must never turn a bad record into a canonical-looking file."""
    path = write_card(root, make_card(root))
    path.write_text(path.read_text().replace("put_by: build_session", "put_by: tom"))
    with pytest.raises(KilnError, match="put to Tom"):
        render_cards(root)
