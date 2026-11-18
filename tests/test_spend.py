"""The spend ledger: the meter behind tripwire 4, shared by every paid command (D-013)."""

from __future__ import annotations

import threading
import time
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from kiln import spend
from kiln.cli import app
from kiln.config import KilnConfig
from kiln.errors import KilnError
from kiln.vocabulary import Actor, Basis

CONFIG = KilnConfig.model_validate(
    {
        "current_phase": 0,
        "services": {"none": {"purpose": "x", "needed_from_phase": 5, "env": ["NONE_KEY"]}},
        "budgets": {
            "small": {"usd": 1.00, "approved": "fixture"},
            "other": {"usd": 5.00, "approved": "fixture"},
        },
        "spend": {"ledger": "ledger.jsonl", "warn_at": 0.8},
    }
)
START = datetime(2026, 11, 18, 9, 0, tzinfo=UTC)


class Clock:
    """A clock that moves a minute each time it is read."""

    def __init__(self) -> None:
        self.at = START

    def __call__(self) -> datetime:
        self.at += timedelta(minutes=1)
        return self.at


def hold(root: Path, usd: float, budget: str = "small", **kwargs: Any) -> spend.Reserved:
    return spend.reserve(
        root,
        kwargs.pop("config", CONFIG),
        budget=budget,
        usd=usd,
        command="kiln review",
        ref="sha256:" + "0" * 64,
        by=Actor.BUILD_SESSION,
        now=kwargs.pop("now", Clock()),
    )


def pay(root: Path, reservation: int, usd: float) -> spend.Settlement:
    return spend.settle(
        root,
        CONFIG,
        reservation,
        usd=usd,
        outcome="completed",
        basis=Basis.OBSERVED,
        by=Actor.BUILD_SESSION,
        now=Clock(),
    )


def ledger(root: Path) -> spend.Ledger:
    return spend.read_ledger(root / "ledger.jsonl")


def position(root: Path, budget: str = "small") -> spend.Position:
    return ledger(root).position(budget, CONFIG.budgets[budget].usd)


# --- The guard -------------------------------------------------------------------------------


def test_a_call_that_could_pass_the_cap_is_refused_and_nothing_is_written(tmp_path: Path) -> None:
    """Why: the slice's check, and tripwire 4: refuse before the call, not after the bill."""
    hold(tmp_path, 0.60)
    before = (tmp_path / "ledger.jsonl").read_bytes()
    with pytest.raises(KilnError, match=r"over budget: .* \$0\.4000 of the \$1\.00 'small'"):
        hold(tmp_path, 0.41)
    assert (tmp_path / "ledger.jsonl").read_bytes() == before


def test_a_call_that_exactly_fills_the_budget_is_allowed(tmp_path: Path) -> None:
    """Why: the cap is what Tom approved; reaching it is within it."""
    hold(tmp_path, 0.25)
    hold(tmp_path, 0.75)
    assert position(tmp_path).left == 0


def test_cents_that_float_arithmetic_blurs_do_not_refuse_a_call(tmp_path: Path) -> None:
    """Why: 0.1 + 0.2 is not 0.3 in floating point; a cap must not fail on that."""
    config = CONFIG.model_copy(
        update={"budgets": {"small": CONFIG.budgets["small"].model_copy(update={"usd": 0.3})}}
    )
    hold(tmp_path, 0.1, config=config)
    hold(tmp_path, 0.2, config=config)


def test_the_warning_comes_before_the_call_that_reaches_80_percent(tmp_path: Path) -> None:
    """Why: the slice's check; a warning after the money is gone is too late to act on."""
    assert hold(tmp_path, 0.70).warning is None
    warned = hold(tmp_path, 0.10).warning
    assert warned is not None
    assert "may reach 80% of its $1.00" in warned


def test_an_open_reservation_counts_at_its_bound(tmp_path: Path) -> None:
    """Why: a call in flight, or one whose cost is unknown, has not been shown to be cheap."""
    hold(tmp_path, 0.90)
    with pytest.raises(KilnError, match="over budget"):
        hold(tmp_path, 0.20)


def test_settling_releases_what_the_bound_overstated(tmp_path: Path) -> None:
    """Why: a bound is pessimistic; the budget is charged what the call really cost."""
    first = hold(tmp_path, 0.90).reservation
    pay(tmp_path, first.entry, 0.05)
    hold(tmp_path, 0.90)
    assert position(tmp_path).settled == 0.05


def test_budgets_are_metered_separately(tmp_path: Path) -> None:
    """Why: each budget is Tom's approval for one purpose; one cannot spend another's."""
    hold(tmp_path, 1.00)
    hold(tmp_path, 4.00, budget="other")
    assert (position(tmp_path).committed, position(tmp_path, "other").committed) == (1.0, 4.0)


def test_a_budget_tom_did_not_set_is_refused(tmp_path: Path) -> None:
    """Why: only Tom sets a budget; a command cannot name one into existence."""
    with pytest.raises(KilnError, match="only Tom sets one"):
        hold(tmp_path, 0.01, budget="invented")


def test_once_spend_passes_a_cap_every_call_is_refused(tmp_path: Path) -> None:
    """Why: tripwire 4 stops the affected work until Tom decides, even a free-looking call."""
    first = hold(tmp_path, 0.50).reservation
    pay(tmp_path, first.entry, 1.20)
    with pytest.raises(KilnError, match="tripwire 4"):
        hold(tmp_path, 0.0)


def test_two_commands_cannot_both_take_the_last_of_a_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Why: the check and the append are one step under the lock. The slowed read widens the
    window in which, without the lock, every racer would see the budget empty."""
    real_read = spend.read_ledger

    def slow_read(path: Path) -> spend.Ledger:
        result = real_read(path)
        time.sleep(0.05)
        return result

    monkeypatch.setattr(spend, "read_ledger", slow_read)
    outcomes: list[str] = []
    gate = threading.Barrier(8)

    def racer() -> None:
        gate.wait()
        try:
            hold(tmp_path, 0.60)
            outcomes.append("reserved")
        except KilnError:
            outcomes.append("refused")

    threads = [threading.Thread(target=racer) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert sorted(outcomes) == ["refused"] * 7 + ["reserved"]
    assert len(real_read(tmp_path / "ledger.jsonl").entries) == 1


# --- The record --------------------------------------------------------------------------------


def test_settling_needs_an_open_reservation(tmp_path: Path) -> None:
    """Why: a cost with nothing reserved for it, or recorded twice, breaks the arithmetic."""
    first = hold(tmp_path, 0.10).reservation
    with pytest.raises(KilnError, match="no reservation 9"):
        pay(tmp_path, 9, 0.01)
    pay(tmp_path, first.entry, 0.01)
    with pytest.raises(KilnError, match="already settled"):
        pay(tmp_path, first.entry, 0.01)


def write(tmp_path: Path, *lines: str) -> Path:
    path = tmp_path / "ledger.jsonl"
    path.write_text("".join(line + "\n" for line in lines), encoding="utf-8")
    return path


def entry(number: int, **fields: Any) -> str:
    values: dict[str, Any] = {
        "entry": number,
        "kind": "reserve",
        "at": f"2026-11-18T09:{number:02d}:00Z",
        "budget": "small",
        "usd": 0.1,
        "command": "kiln review",
        "ref": "sha256:x",
        "by": "build_session",
    }
    values.update(fields)
    if values["kind"] == "settle":
        for name in ("budget", "command", "ref"):
            values.pop(name)
        values = {
            "entry": values["entry"],
            "kind": "settle",
            "at": values["at"],
            "reservation": values["reservation"],
            "usd": values["usd"],
            "outcome": "completed",
            "basis": "observed",
            "by": "build_session",
        }
    return spend.canonical_line(spend._ENTRY.validate_python(values))  # pyright: ignore[reportPrivateUsage]


@pytest.mark.parametrize(
    ("lines", "message"),
    [
        ([entry(1), entry(3)], "entry 2 is numbered 3"),
        ([entry(2, entry=1), entry(1, entry=2)], "dated before"),
        ([entry(1), entry(2, kind="settle", reservation=5)], "no earlier reservation"),
        (
            [
                entry(1),
                entry(2, kind="settle", reservation=1),
                entry(3, kind="settle", reservation=1),
            ],
            "a second time",
        ),
    ],
)
def test_a_ledger_that_is_not_append_only_is_refused(
    tmp_path: Path, lines: list[str], message: str
) -> None:
    """Why: a renumbered, reordered or doubled entry is a rewrite of the record."""
    with pytest.raises(KilnError, match=message):
        spend.read_ledger(write(tmp_path, *lines))


def test_an_entry_edited_by_hand_is_refused(tmp_path: Path) -> None:
    """Why: the canonical form is what makes a hand edit visible."""
    edited = entry(1).replace('"usd": 0.1', '"usd":0.1')
    with pytest.raises(KilnError, match="canonical form"):
        spend.read_ledger(write(tmp_path, edited))


def test_a_time_outside_utc_is_refused(tmp_path: Path) -> None:
    """Why: order is checked by time, and records use the session's date in UTC."""
    with pytest.raises(ValueError, match="UTC"):
        spend.Reservation(
            entry=1,
            at=datetime(2026, 11, 18, 9, 0, tzinfo=timezone(timedelta(hours=10))),
            budget="small",
            usd=0.1,
            command="kiln review",
            ref="sha256:x",
            by=Actor.BUILD_SESSION,
        )


def test_a_line_that_is_not_an_entry_is_refused(tmp_path: Path) -> None:
    """Why: a line nobody can read is spend nobody can count."""
    with pytest.raises(KilnError, match="invalid ledger entry") as caught:
        spend.read_ledger(write(tmp_path, "{not json"))
    assert caught.value.item == f"{tmp_path / 'ledger.jsonl'}:1"


def test_no_ledger_means_nothing_spent(tmp_path: Path) -> None:
    """Why: a fresh repo has spent nothing, and reading must not create a file."""
    assert spend.read_ledger(tmp_path / "ledger.jsonl").entries == ()
    assert not (tmp_path / "ledger.jsonl").exists()


def test_the_report_shows_open_reservations_and_costs_above_their_bound(tmp_path: Path) -> None:
    """Why: an open reservation needs someone to settle it, and a cost above its bound means
    the estimator that guards the budget is wrong."""
    first = hold(tmp_path, 0.10).reservation
    pay(tmp_path, first.entry, 0.20)
    hold(tmp_path, 0.65)
    text = spend.render(CONFIG, ledger(tmp_path))
    assert "small: $0.2000 spent and $0.6500 reserved of $1.00 (85%)" in text
    assert "WARNING: at 85%, past 80% of its cap" in text
    assert "Open: reservation 3, $0.6500 on 'small'" in text
    assert "Above its bound: reservation 1 cost $0.2000 against an upper bound of $0.1000" in text


# --- The command line ----------------------------------------------------------------------------


def config_file(tmp_path: Path) -> Path:
    path = tmp_path / "kiln.yaml"
    path.write_text(CONFIG.model_dump_json(), encoding="utf-8")
    return path


def test_kiln_spend_exits_2_once_tripwire_4_has_tripped(tmp_path: Path) -> None:
    """Why: a tripwire must stop the work loudly, in CI and in a session alike."""
    args = ["spend", "--root", str(tmp_path), "--config", str(config_file(tmp_path))]
    assert CliRunner().invoke(app, args).exit_code == 0
    first = hold(tmp_path, 0.50).reservation
    pay(tmp_path, first.entry, 1.50)
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 2
    assert "TRIPWIRE 4" in result.output


def test_kiln_spend_settle_closes_an_open_reservation(tmp_path: Path) -> None:
    """Why: a call that timed out after sending is settled from the provider's own record."""
    held = hold(tmp_path, 0.40, now=lambda: START).reservation
    result = CliRunner().invoke(
        app,
        [
            "spend",
            "settle",
            str(held.entry),
            "--usd",
            "0.12",
            "--outcome",
            "timed out after sending; billed",
            "--note",
            "Read from the provider's usage page.",
            "--root",
            str(tmp_path),
            "--config",
            str(config_file(tmp_path)),
        ],
    )
    assert result.exit_code == 0, result.output
    assert ledger(tmp_path).open() == []
    assert position(tmp_path).settled == 0.12
