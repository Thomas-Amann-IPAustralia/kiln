"""The ticket list, `council/tickets.json`: what it accepts, and every way it refuses."""

from __future__ import annotations

import copy
import json
from typing import Any

import pytest

from kiln.errors import KilnError
from kiln.tickets import TicketList, parse_tickets


def ticket(number: int, *, blocked_by: list[int] | None = None) -> dict[str, Any]:
    return {
        "id": f"TKT-{number:04d}",
        "title": f"Placeholder ticket {number}",
        "description": "Placeholder work.",
        "contract": "ux",
        "blocked_by": [f"TKT-{b:04d}" for b in blocked_by or []],
        "steps": [{"description": "Placeholder behaviour.", "run": ["true"]}],
    }


VALID: dict[str, Any] = {
    "version": 1,
    "checks": [
        {"name": "tests", "run": ["pytest"]},
        {"name": "secrets", "run": ["gitleaks", "dir", "."], "tripwire": "exposed_secret"},
    ],
    "read_only": ["pyproject.toml", "*/conftest.py"],
    "tickets": [ticket(1), ticket(2, blocked_by=[1])],
}


def encoded(data: dict[str, Any]) -> bytes:
    return json.dumps(data).encode()


def test_a_valid_list_parses_with_its_defaults() -> None:
    """Why: the chair writes this file by hand; the defaults it may leave out must be the ones
    the verifier then uses."""
    tickets = parse_tickets(encoded(VALID), item="council/tickets.json")
    assert [t.id for t in tickets.tickets] == ["TKT-0001", "TKT-0002"]
    assert tickets.checks[0].timeout_seconds == 600
    assert tickets.checks[0].tripwire is None
    assert tickets.ticket("TKT-0002") is not None
    assert tickets.ticket("TKT-0009") is None


def changed(path: str, value: Any) -> dict[str, Any]:
    """VALID with one field replaced, the field named by a dotted path."""
    data = copy.deepcopy(VALID)
    *parents, last = path.split(".")
    target: Any = data
    for part in parents:
        target = target[int(part)] if part.isdigit() else target[part]
    if last.isdigit():
        target[int(last)] = value
    else:
        target[last] = value
    return data


@pytest.mark.parametrize(
    ("data", "message"),
    [
        (changed("version", 2), "version"),
        (changed("tickets", []), "tickets"),
        (changed("checks", []), "checks"),
        (changed("tickets.1", ticket(1)), "ticket ids must not repeat"),
        (changed("checks.1.name", "tests"), "check names must not repeat"),
        (changed("tickets.1", ticket(2, blocked_by=[2])), "TKT-0002 blocks itself"),
        (changed("tickets.1", ticket(2, blocked_by=[7])), "blocked by TKT-0007, not a ticket"),
        (changed("tickets.0", ticket(1, blocked_by=[2])), "TKT-0001 -> TKT-0002 -> TKT-0001"),
        (changed("tickets.0.steps", []), "steps"),
        (changed("tickets.0.steps.0.run", []), "run"),
        (changed("tickets.0.steps.0.run", ["  "]), "must not be blank"),
        (changed("tickets.0.steps.0.timeout_seconds", 0), "timeout_seconds"),
        (changed("tickets.0.steps.0.timeout_seconds", 3601), "timeout_seconds"),
        (changed("tickets.0.id", "TASK-1"), "not a record id"),
        (changed("tickets.0.contract", "Not A Slug"), "contract"),
        (changed("checks.0.tripwire", "a_new_tripwire"), "tripwire"),
        (changed("read_only", ["/etc/passwd"]), "repo-relative"),
        (changed("read_only", ["../outside"]), "repo-relative"),
        (changed("tickets.0.passes", True), "passes"),
    ],
)
def test_each_rejection_names_its_field(data: dict[str, Any], message: str) -> None:
    """Why: a ticket list is a contract a loop and the verifier both read; a bad one must fail
    loudly, in one line naming the field, before either relies on it. The last case is the one
    that matters most: a ticket cannot carry a `passes` flag here, where Tom approved it."""
    with pytest.raises(KilnError, match=message):
        parse_tickets(encoded(data), item="council/tickets.json")


def test_a_key_given_twice_is_refused_not_overwritten() -> None:
    """Why: a JSON reader keeps the last of two equal keys, so a typo would silently drop the
    first, perhaps a step."""
    text = encoded(VALID).replace(b'"version": 1', b'"version": 1, "version": 1')
    with pytest.raises(KilnError, match="'version' appears twice"):
        parse_tickets(text, item="council/tickets.json")


@pytest.mark.parametrize("data", [b"{not json", b"\xff\xfe", b"[]"])
def test_bytes_that_are_not_a_ticket_list_fail_in_one_line(data: bytes) -> None:
    """Why: the verifier reads this file from history; whatever is there must fail as itself."""
    with pytest.raises(KilnError) as raised:
        parse_tickets(data, item="council/tickets.json")
    assert "\n" not in raised.value.one_line()
    assert "council/tickets.json" in raised.value.one_line()


def test_a_ticket_list_is_immutable() -> None:
    """Why: the verifier reads one version and runs it; nothing may change it in between."""
    tickets = TicketList.model_validate(VALID)
    with pytest.raises(ValueError, match="frozen"):
        tickets.tickets[0].title = "Changed"  # pyright: ignore[reportAttributeAccessIssue]
