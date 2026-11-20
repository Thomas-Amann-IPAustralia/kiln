"""A solution's tickets, and the checks every commit must pass: `council/tickets.json`.

The chair writes this file and Tom approves it with the plan at G2. It is the executable half of
the build contract: what a coding loop builds, and how the verifier tells that it was built.

- **A ticket** is one unit of work: a description, the domain contract it traces to, the tickets
  that block it, and its **verification steps**. The list's order is its priority: a loop takes
  the first open ticket that nothing blocks.
- **A verification step** is a command that succeeds, exiting 0, when the ticket's behaviour is
  there. It is an argument list, never a shell line, so what runs is exactly what is written.
- **A check** is a command every commit must pass whatever the ticket: tests, the type checker,
  the fitness functions. A **tripwire check**, such as a secret scan, names the tripwire it
  watches; if it fails, that tripwire is open.
- **`read_only`** lists further paths a loop may not change, beyond the ones every solution
  protects (`kiln.verifier`). A step is only as strong as what it runs: a test runner's
  configuration or a `Makefile` a step calls belongs here.

The shape follows the one Pocock borrows from Anthropic's work on long-running agents (charter,
`agents/coding-swarm.md`): a description, steps and a `passes` flag. It differs in two ways, both
for ADR-0027. The steps are commands, because a verifier that is not a model must run them. And
`passes` is not in this file: only the verifier writes it, in `council/build.yaml`, so the file
Tom approved never changes when a ticket passes, and a loop has no reason to write here at all.
"""

from __future__ import annotations

import json
from pathlib import PurePosixPath
from typing import Annotated, Any, Literal

from pydantic import AfterValidator, Field, ValidationError, model_validator

from kiln.errors import KilnError
from kiln.ids import TicketId
from kiln.model import Record, Slug, Text
from kiln.vocabulary import Tripwire

DEFAULT_TIMEOUT_SECONDS = 600
MAX_TIMEOUT_SECONDS = 3600


def _a_path_pattern(value: str) -> str:
    pure = PurePosixPath(value)
    if not value.strip() or pure.is_absolute() or ".." in pure.parts or "\\" in value:
        raise ValueError(f"must be a repo-relative path or pattern, not {value!r}")
    return value


PathPattern = Annotated[str, AfterValidator(_a_path_pattern)]
"""A repo-relative path, or a pattern matched against the whole path, in which `*` matches any
characters, `/` included: `conftest.py`, `*/conftest.py`, `pyproject.toml`, `scripts/*`."""


class Command(Record):
    """A command the verifier runs in a clean checkout of a loop's commit."""

    run: Annotated[list[Text], Field(min_length=1)]
    """The argument list. The first is the program, found on the verifier's allowed `PATH`."""
    timeout_seconds: Annotated[int, Field(gt=0, le=MAX_TIMEOUT_SECONDS)] = DEFAULT_TIMEOUT_SECONDS


class Check(Command):
    """A command every commit must pass, whatever the ticket."""

    name: Slug
    tripwire: Tripwire | None = None
    """The tripwire this check watches, for a tripwire check: if it fails, that one is open."""


class Step(Command):
    """A verification step: it succeeds when the ticket's behaviour is there."""

    description: Text
    """What success shows, in words the loop and Tom can read."""


class Ticket(Record):
    id: TicketId
    title: Text
    description: Text
    """The work, for the loop."""
    contract: Slug
    """The domain contract in the plan that it traces to (G2)."""
    blocked_by: list[TicketId] = Field(default_factory=list[TicketId])
    steps: Annotated[list[Step], Field(min_length=1)]


class TicketList(Record):
    """`council/tickets.json`. Read-only to loops (ADR-0027)."""

    version: Literal[1]
    checks: Annotated[list[Check], Field(min_length=1)]
    read_only: list[PathPattern] = Field(default_factory=list[str])
    tickets: Annotated[list[Ticket], Field(min_length=1)]
    """In priority order: a loop takes the first open ticket that nothing blocks."""

    @model_validator(mode="after")
    def _consistent(self) -> TicketList:
        names = [c.name for c in self.checks]
        if len(set(names)) != len(names):
            raise ValueError("check names must not repeat")
        ids = [t.id for t in self.tickets]
        if len(set(ids)) != len(ids):
            raise ValueError("ticket ids must not repeat")
        known = set(ids)
        for ticket in self.tickets:
            for blocker in ticket.blocked_by:
                if blocker == ticket.id:
                    raise ValueError(f"{ticket.id} blocks itself")
                if blocker not in known:
                    raise ValueError(f"{ticket.id} is blocked by {blocker}, not a ticket here")
        cycle = _a_cycle({t.id: t.blocked_by for t in self.tickets})
        if cycle:
            raise ValueError("these tickets block each other in a cycle: " + " -> ".join(cycle))
        return self

    def ticket(self, ticket_id: str) -> Ticket | None:
        return next((t for t in self.tickets if t.id == ticket_id), None)


def _a_cycle(blocked_by: dict[str, list[str]]) -> list[str]:
    """One cycle in the blocking edges, as the ids along it, or an empty list if none."""
    done: set[str] = set()
    path: list[str] = []

    def visit(node: str) -> list[str]:
        if node in path:
            return [*path[path.index(node) :], node]
        if node in done:
            return []
        path.append(node)
        for blocker in sorted(blocked_by[node]):
            if cycle := visit(blocker):
                return cycle
        path.pop()
        done.add(node)
        return []

    for start in sorted(blocked_by):
        if cycle := visit(start):
            return cycle
    return []


def _refuse_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    keys = [key for key, _ in pairs]
    repeated = sorted({key for key in keys if keys.count(key) > 1})
    if repeated:
        raise ValueError(f"the key {repeated[0]!r} appears twice in one object")
    return dict(pairs)


def parse_tickets(data: bytes, *, item: str) -> TicketList:
    """Validate the bytes of a `tickets.json`, or raise a `KilnError` naming the first problem.

    A key that appears twice in one object is refused: JSON readers keep the last, so the first
    would be silently ignored."""
    try:
        raw: object = json.loads(data.decode("utf-8"), object_pairs_hook=_refuse_duplicates)
    except (UnicodeDecodeError, ValueError) as exc:
        raise KilnError(f"not valid JSON: {exc}", item=item) from exc
    try:
        return TicketList.model_validate(raw)
    except ValidationError as exc:
        first = exc.errors()[0]
        where = ".".join(str(part) for part in first["loc"]) or "(file)"
        raise KilnError(
            f"invalid TicketList; first of {exc.error_count()}: {where}: {first['msg']}",
            item=item,
        ) from exc
