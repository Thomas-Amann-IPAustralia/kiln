"""The spend ledger: every paid call, in dollars, against a budget Tom set (sketch, "Spend";
D-013).

Tripwire 4 is spend over budget. The ledger is how no paid command reaches it:

- **Before a call,** the command reserves the call's upper-bound cost against its budget. The
  reservation is refused if the budget's committed spend (every settled cost, plus every
  reservation still open) and this bound together could pass the cap. A reservation that
  takes the budget to `warn_at` of its cap (80%) warns, and proceeds.
- **After the call,** the command settles the reservation at the real cost, naming the record
  that shows it. A call that may have been billed but returned no cost, such as one that timed
  out after it was sent, stays open, so its bound keeps counting until someone settles it from
  the provider's own account. The ledger can overstate spend; it never understates it.
- **Entries are appended, never rewritten:** one canonical JSON object a line, numbered from 1.
  A lock makes the check and the append one step, so two commands on one machine cannot both
  take the last of a budget.

Its limit, stated plainly: the ledger is a file in git, so it is per branch. Two sessions on
two branches each see only their own spend. Until the ledger has a shared home (slice 7), one
session spends against a budget at a time.
"""

from __future__ import annotations

import fcntl
import json
from collections.abc import Callable, Generator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    AwareDatetime,
    Field,
    TypeAdapter,
    ValidationError,
    model_validator,
)

from kiln.config import KilnConfig
from kiln.errors import KilnError
from kiln.model import Record, RepoPath, Text
from kiln.recordfile import write_atomic
from kiln.vocabulary import Actor, Basis, Tripwire

Usd = Annotated[float, Field(ge=0)]
BudgetName = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]*$")]


def _cents(usd: float) -> float:
    """Dollars to the micro-dollar, which every price and cost in Kiln is given to."""
    return round(usd, 6)


def _utc(at: datetime) -> datetime:
    if at.utcoffset() != timedelta(0):
        raise ValueError("times in the ledger are UTC")
    return at


UtcTime = Annotated[AwareDatetime, AfterValidator(_utc)]


class Reservation(Record):
    """A paid call's upper-bound cost, held against its budget before the call is sent."""

    entry: Annotated[int, Field(ge=1)]
    kind: Literal["reserve"] = "reserve"
    at: UtcTime
    budget: BudgetName
    usd: Usd
    """The upper bound: the most the call can cost."""
    command: Text
    ref: Text
    """What the call was, such as `sha256:<request hash>`."""
    by: Actor
    note: Text | None = None


class Settlement(Record):
    """What a reserved call really cost, and how that is known."""

    entry: Annotated[int, Field(ge=1)]
    kind: Literal["settle"] = "settle"
    at: UtcTime
    reservation: Annotated[int, Field(ge=1)]
    usd: Usd
    outcome: Text
    basis: Basis
    """`observed` when the provider reported the cost; `assumed` when it is inferred, such as
    an error response taken as unbilled."""
    record: RepoPath | None = None
    """The committed record of the call, such as a cached response."""
    by: Actor
    note: Text | None = None


Entry = Annotated[Reservation | Settlement, Field(discriminator="kind")]
_ENTRY: TypeAdapter[Reservation | Settlement] = TypeAdapter(Entry)


class Ledger(Record):
    entries: tuple[Entry, ...] = ()

    @model_validator(mode="after")
    def _append_only(self) -> Ledger:
        reserved: set[int] = set()
        settled: set[int] = set()
        last: datetime | None = None
        for number, entry in enumerate(self.entries, start=1):
            if entry.entry != number:
                raise ValueError(f"entry {number} is numbered {entry.entry}")
            if last is not None and entry.at < last:
                raise ValueError(f"entry {number} is dated before the entry above it")
            last = entry.at
            if isinstance(entry, Reservation):
                reserved.add(number)
            elif entry.reservation not in reserved:
                raise ValueError(
                    f"entry {number} settles {entry.reservation}, no earlier reservation"
                )
            elif entry.reservation in settled:
                raise ValueError(f"entry {number} settles {entry.reservation} a second time")
            else:
                settled.add(entry.reservation)
        return self

    def reservations(self) -> dict[int, Reservation]:
        return {e.entry: e for e in self.entries if isinstance(e, Reservation)}

    def settlements(self) -> dict[int, Settlement]:
        """Each settlement, by the reservation it settles."""
        return {e.reservation: e for e in self.entries if isinstance(e, Settlement)}

    def open(self) -> list[Reservation]:
        settled = self.settlements()
        return [r for r in self.reservations().values() if r.entry not in settled]

    def position(self, budget: str, cap: float) -> Position:
        settlements = self.settlements()
        mine = [r for r in self.reservations().values() if r.budget == budget]
        return Position(
            budget=budget,
            cap=cap,
            settled=_cents(sum(settlements[r.entry].usd for r in mine if r.entry in settlements)),
            reserved=_cents(sum(r.usd for r in mine if r.entry not in settlements)),
        )


class Position(Record):
    """Where one budget stands."""

    budget: str
    cap: float
    settled: float
    reserved: float
    """Open reservations, counted at their bounds."""

    @property
    def committed(self) -> float:
        return _cents(self.settled + self.reserved)

    @property
    def left(self) -> float:
        return _cents(self.cap - self.committed)

    @property
    def tripped(self) -> bool:
        """Tripwire 4: settled spend has passed the cap."""
        return self.settled > _cents(self.cap)


def canonical_line(entry: Reservation | Settlement) -> str:
    return json.dumps(entry.model_dump(mode="json", exclude_none=True), ensure_ascii=False)


def read_ledger(path: Path) -> Ledger:
    """The ledger, checked: every line valid, canonical, numbered and in order. A missing file
    is an empty ledger: nothing has been spent."""
    if not path.is_file():
        return Ledger()
    entries: list[Reservation | Settlement] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        where = f"{path}:{number}"
        try:
            entry = _ENTRY.validate_json(line)
        except ValidationError as exc:
            first = exc.errors()[0]
            field = ".".join(str(part) for part in first["loc"]) or "(entry)"
            raise KilnError(
                f"invalid ledger entry; first: {field}: {first['msg']}", item=where
            ) from exc
        if line != canonical_line(entry):
            raise KilnError(
                "the ledger entry is not in canonical form; it was edited by hand",
                item=where,
                see="src/kiln/spend.py",
            )
        entries.append(entry)
    try:
        return Ledger(entries=tuple(entries))
    except ValidationError as exc:
        raise KilnError(
            f"the ledger is not append-only: {exc.errors()[0]['msg']}", item=str(path)
        ) from exc


def positions(config: KilnConfig, ledger: Ledger) -> list[Position]:
    """Every budget in config, in name order."""
    return [ledger.position(name, budget.usd) for name, budget in sorted(config.budgets.items())]


def check(position: Position, usd: float, warn_at: float) -> str | None:
    """Refuse a call that could pass the cap, or return a warning when it may reach `warn_at`
    of the cap. Free: it only reads."""
    if position.tripped:
        raise KilnError(
            f"tripwire {Tripwire.SPEND_OVER_BUDGET.number}: budget {position.budget!r} has "
            f"${position.settled:.4f} settled against a cap of ${position.cap:.2f}; nothing more "
            "is spent from it until Tom decides",
            see="kiln spend",
        )
    after = _cents(position.committed + usd)
    if after > _cents(position.cap):
        raise KilnError(
            f"over budget: the call may cost up to ${usd:.4f}, and ${position.left:.4f} of the "
            f"${position.cap:.2f} {position.budget!r} budget is left",
            see="config/kiln.yaml, budgets",
        )
    if after >= _cents(position.cap * warn_at):
        return (
            f"warning: budget {position.budget!r} may reach {after / position.cap:.0%} of its "
            f"${position.cap:.2f} with this call (${after:.4f}, counting this call at its bound)"
        )
    return None


def now_utc() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


Clock = Callable[[], datetime]


class Reserved(Record):
    reservation: Reservation
    warning: str | None


def reserve(
    root: Path,
    config: KilnConfig,
    *,
    budget: str,
    usd: float,
    command: str,
    ref: str,
    by: Actor,
    now: Clock = now_utc,
) -> Reserved:
    """Hold `usd` against `budget` before a paid call, or refuse. The check and the append
    happen under one lock."""
    if budget not in config.budgets:
        raise KilnError(f"budget {budget!r} is not in config `budgets`; only Tom sets one")
    path = root / config.spend.ledger
    with _locked(path):
        ledger = read_ledger(path)
        warning = check(
            ledger.position(budget, config.budgets[budget].usd), usd, config.spend.warn_at
        )
        reservation = Reservation(
            entry=len(ledger.entries) + 1,
            at=now(),
            by=by,
            budget=budget,
            usd=_cents(usd),
            command=command,
            ref=ref,
        )
        _append(path, ledger, reservation)
    return Reserved(reservation=reservation, warning=warning)


def settle(
    root: Path,
    config: KilnConfig,
    reservation: int,
    *,
    usd: float,
    outcome: str,
    basis: Basis,
    by: Actor,
    record: str | None = None,
    note: str | None = None,
    now: Clock = now_utc,
) -> Settlement:
    """Record what a reserved call really cost."""
    path = root / config.spend.ledger
    with _locked(path):
        ledger = read_ledger(path)
        if reservation not in ledger.reservations():
            raise KilnError(f"there is no reservation {reservation} in the ledger", item=str(path))
        if reservation in ledger.settlements():
            raise KilnError(f"reservation {reservation} is already settled", item=str(path))
        settlement = Settlement(
            entry=len(ledger.entries) + 1,
            at=now(),
            by=by,
            note=note,
            reservation=reservation,
            usd=_cents(usd),
            outcome=outcome,
            basis=basis,
            record=record,
        )
        _append(path, ledger, settlement)
    return settlement


def _append(path: Path, ledger: Ledger, entry: Reservation | Settlement) -> None:
    Ledger(entries=(*ledger.entries, entry))  # the same checks as a read
    lines = [canonical_line(e) for e in (*ledger.entries, entry)]
    write_atomic(path, "\n".join(lines) + "\n")


@contextmanager
def _locked(path: Path) -> Generator[None]:
    """An exclusive lock beside the ledger, held while it is read and rewritten. The ledger is
    replaced by rename, so the lock cannot be on the ledger itself."""
    lock = path.with_name(path.name + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open("a", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def render(config: KilnConfig, ledger: Ledger) -> str:
    """Where each budget stands, its open reservations, and any cost that passed its bound."""
    lines: list[str] = []
    for position in positions(config, ledger):
        share = position.committed / position.cap
        flag = ""
        if position.tripped:
            flag = f"  TRIPWIRE {Tripwire.SPEND_OVER_BUDGET.number}: over its cap"
        elif share >= config.spend.warn_at:
            flag = f"  WARNING: at {share:.0%}, past {config.spend.warn_at:.0%} of its cap"
        lines.append(
            f"{position.budget}: ${position.settled:.4f} spent and ${position.reserved:.4f} "
            f"reserved of ${position.cap:.2f} ({share:.0%}); ${position.left:.4f} left.{flag}"
        )
    if not lines:
        lines.append("No budgets are set. Only Tom sets one, in config/kiln.yaml.")
    known = set(config.budgets)
    others = sorted({r.budget for r in ledger.reservations().values()} - known)
    if others:
        lines.append(f"Spent against budgets no longer in config: {', '.join(others)}.")
    for reservation in ledger.open():
        lines.append(
            f"Open: reservation {reservation.entry}, ${reservation.usd:.4f} on "
            f"{reservation.budget!r} by `{reservation.command}` ({reservation.ref}), since "
            f"{reservation.at.isoformat()}. Settle it with `kiln spend settle`."
        )
    reservations = ledger.reservations()
    for number, settlement in sorted(ledger.settlements().items()):
        bound = reservations[number].usd
        if settlement.usd > bound:
            lines.append(
                f"Above its bound: reservation {number} cost ${settlement.usd:.4f} against an "
                f"upper bound of ${bound:.4f}. The estimate behind it is wrong; fix it."
            )
    return "\n".join(lines)
