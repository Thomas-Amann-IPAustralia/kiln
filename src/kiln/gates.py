"""The six gates, G0 to G5, as a LangGraph state machine whose nodes only validate artefacts.

**What a gate checks.** Each gate reads its artefacts from the solution's `council/` folder
(`kiln.artefacts`) and runs the charter's checks for it. A missing artefact leaves the gate
`incomplete`; a check that fails leaves it `failed`.

**Tom's gates.** G0, G2, G4 and G5 also need Tom's approval: a decision card for the gate,
answered with its pass option and merged into `main` (`kiln.cards`, `kiln.approvals`), that
rests on the gate's artefacts **at their current hashes**. A file edited after Tom approved it
fails the gate, because the edit is a change to what he approved. Tom's latest approval of a
file counts for every earlier gate that needs it: the G2 card rests on the profile as it stands
at G2, so G0 does not need a fresh card each time the profile gains a measure.

**Passes are never trusted, only recomputed.** Every gate is evaluated from the files and the
history as they are now. Before a node validates its own gate, it re-validates every pass
already in the run's state and refuses any that does not hold. So a pass written from outside
the validation node, for example through LangGraph's `update_state`, is refused at the next
gate, and nothing about a pass needs to be stored to be believed.

**No tracing leaves through LangGraph.** LangGraph's tracing client sends a run's state to
LangSmith when an environment variable asks it to (observed, D-012). Kiln's tracer is Langfuse
(slice 7), so every run here is wrapped in `tracing_context(enabled=False)`.
"""

from __future__ import annotations

import itertools
import operator
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any, TypedDict, TypeVar

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph  # pyright: ignore[reportMissingTypeStubs]
from langsmith.run_helpers import tracing_context  # pyright: ignore[reportUnknownVariableType]
from pydantic import BaseModel, Field, ValidationError

from kiln import artefacts, verifier
from kiln.approvals import DEFAULT_REF, CardApproval, Status, read_approvals
from kiln.artefacts import (
    COUNCIL_DIR,
    ApplicabilityRegister,
    BuildRecord,
    Plan,
    PreRelease,
    RealWorldTest,
    Severity,
    parse_yaml,
)
from kiln.cards import DecisionCard
from kiln.errors import KilnError
from kiln.ids import CardId, ContentHash, content_hash, parse_record_id
from kiln.model import Record
from kiln.profile import Dimension, ProjectProfile
from kiln.tickets import TicketList, parse_tickets
from kiln.vocabulary import Gate

GATES: tuple[Gate, ...] = tuple(Gate)
M = TypeVar("M", bound=BaseModel)


class GateStatus(StrEnum):
    PASSED = "passed"
    AWAITING_TOM = "awaiting Tom"
    """The checks pass; Tom's approval is not yet in effect."""
    INCOMPLETE = "incomplete"
    """An artefact the gate needs does not exist yet."""
    FAILED = "failed"
    """An artefact is invalid, a check failed, Tom declined, or a recorded pass did not hold."""


class GateOutcome(Record):
    """One gate's result, and exactly what it was computed from."""

    gate: Gate
    status: GateStatus
    problems: list[str] = Field(default_factory=list[str])
    artefacts: dict[str, ContentHash] = Field(default_factory=dict[str, ContentHash])
    """Every file the gate read, by content hash."""
    approved_by: CardId | None = None
    card_sha256: ContentHash | None = None


class Workspace:
    """One solution's files and card history, as they are now."""

    def __init__(self, root: Path, council: Path = COUNCIL_DIR, ref: str = DEFAULT_REF) -> None:
        self.root, self.council, self.ref = root, council, ref
        self.cards_dir = council / "cards"
        self._approvals: list[CardApproval] | None = None

    def artefact(self, name: str) -> str:
        return (self.council / name).as_posix()

    def read(self, path: str) -> bytes | None:
        file = self.root / path
        return file.read_bytes() if file.is_file() else None

    def approvals(self) -> list[CardApproval]:
        if self._approvals is None:
            self._approvals = read_approvals(self.root, self.ref, self.cards_dir)
        return self._approvals


class _MissingError(Exception):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.path = path


@dataclass
class _Reading:
    """What one gate read, so its outcome can name each file by hash."""

    workspace: Workspace
    seen: dict[str, str] = field(default_factory=dict[str, str])

    def file(self, path: str) -> bytes:
        data = self.workspace.read(path)
        if data is None:
            raise _MissingError(path)
        self.seen[path] = content_hash(data)
        return data

    def model(self, name: str, model: type[M]) -> M:
        path = self.workspace.artefact(name)
        return parse_yaml(self.file(path), model, item=path)

    def tickets(self) -> TicketList:
        path = self.workspace.artefact(artefacts.TICKETS)
        return parse_tickets(self.file(path), item=path)

    def text(self, path: str, what: str) -> list[str]:
        """Require a document to exist (else incomplete) and to say something."""
        if not self.file(path).strip():
            return [f"{what} ({path}) is empty"]
        return []


@dataclass(frozen=True)
class _Checked:
    problems: list[str]
    for_tom: list[str]
    """The files Tom's approval must cover, for a gate he decides."""


# The checks for each gate. Each reads only what it needs, and raises `_MissingError` for an
# artefact that is not there yet.


def _g0(read: _Reading) -> _Checked:
    profile = read.model(artefacts.PROFILE, ProjectProfile)
    problems: list[str] = []
    if profile.hypotheses == "unknown":
        problems.append("the hypotheses are unknown; G0 settles them")
    else:
        tested = {h.dimension for h in profile.hypotheses}
        problems += [f"no hypothesis tests {d.value}" for d in Dimension if d not in tested]
    return _Checked(problems, [read.workspace.artefact(artefacts.PROFILE)])


def _g1(read: _Reading) -> _Checked:
    read.model(artefacts.APPLICABILITY, ApplicabilityRegister)
    return _Checked([], [])


def _g2(read: _Reading) -> _Checked:
    profile = read.model(artefacts.PROFILE, ProjectProfile)
    register = read.model(artefacts.APPLICABILITY, ApplicabilityRegister)
    plan = read.model(artefacts.PLAN, Plan)
    problems = [
        f"{expert.value} was triggered at G1 but not consulted"
        for expert in register.triggered_experts
        if expert not in plan.consulted_experts
    ]
    if profile.hypotheses == "unknown":
        problems.append("the hypotheses are unknown, so none has a measure")
    else:
        problems += [f"{h.id} has no measure" for h in profile.hypotheses if h.measure == "unknown"]
    for name, cap, estimate in (
        ("build", profile.budget.build_usd, plan.estimate.build_usd),
        ("monthly running", profile.budget.run_usd_per_month, plan.estimate.run_usd_per_month),
    ):
        if isinstance(cap, str):
            problems.append(f"the {name} budget is unknown, so the cost cannot be checked")
        elif estimate > cap:
            problems.append(f"the {name} cost, ${estimate:.2f}, is over its budget, ${cap:.2f}")
    tickets = read.tickets()
    contract_ids = {contract.id for contract in plan.contracts}
    problems += [
        f"{t.id} traces to {t.contract!r}, which is not a contract in the plan"
        for t in tickets.tickets
        if t.contract not in contract_ids
    ]
    problems += read.text(plan.packet, "the G2 packet")
    contracts = [contract.path for contract in plan.contracts]
    for path in contracts:
        read.file(path)
    ws = read.workspace
    tom = [
        ws.artefact(artefacts.PROFILE),
        ws.artefact(artefacts.PLAN),
        ws.artefact(artefacts.TICKETS),
        plan.packet,
        *contracts,
    ]
    return _Checked(problems, tom)


def _g3(read: _Reading) -> _Checked:
    """Every ticket passes by the verifier's record of the build as it is now (ADR-0027)."""
    ws = read.workspace
    tickets = read.tickets()
    read.model(artefacts.PLAN, Plan)
    build = read.model(artefacts.BUILD, BuildRecord)
    problems: list[str] = []
    for name, recorded in (
        (artefacts.TICKETS, build.tickets_sha256),
        (artefacts.PLAN, build.plan_sha256),
    ):
        if read.seen[ws.artefact(name)] != recorded:
            problems.append(
                f"the verifier judged a {ws.artefact(name)} other than the one here; run it again"
            )
    if build.refused:
        problems.append(
            f"the verifier refused {build.commit[:12]}: it changes "
            f"{', '.join(build.refused)}, which a loop may not"
        )
    results = {t.id: t for t in build.tickets}
    problems += [f"{t.id} has no result" for t in tickets.tickets if t.id not in results]
    if not build.refused:
        problems += [
            f"{t.id} does not pass"
            for t in tickets.tickets
            if t.id in results and not results[t.id].passes
        ]
    listed = {t.id for t in tickets.tickets}
    problems += [f"{t} is not a ticket in tickets.json" for t in sorted(results) if t not in listed]
    problems += [f"the check {c.name!r} did not pass" for c in build.checks if not c.passed]
    problems += [f"tripwire {t.number} ({t.value}) is open" for t in build.open_tripwires]
    problems += [
        f"{ws.artefact(artefacts.BUILD)} does not hold: {problem}"
        for problem in verifier.recheck(ws.root, build, ws.ref, ws.council)
    ]
    return _Checked(problems, [])


def _g4(read: _Reading) -> _Checked:
    register = read.model(artefacts.APPLICABILITY, ApplicabilityRegister)
    release = read.model(artefacts.PRE_RELEASE, PreRelease)
    serious = {Severity.CRITICAL, Severity.HIGH}
    problems = [
        f"{f.id} ({f.severity.value}) is still open"
        for f in release.findings
        if f.severity in serious and f.status == "open"
    ]
    statuses = {o.id for o in release.obligations}
    problems += [
        f"{o.id} is neither met nor deferred" for o in register.obligations if o.id not in statuses
    ]
    known = {o.id for o in register.obligations}
    problems += [f"{o} is not an obligation from G1" for o in sorted(statuses) if o not in known]
    problems += read.text(release.assurance_case, "the assurance case")
    problems += read.text(release.test_plan, "the real-world test plan")
    tom = [
        read.workspace.artefact(artefacts.PRE_RELEASE),
        release.assurance_case,
        release.test_plan,
    ]
    return _Checked(problems, tom)


def _g5(read: _Reading) -> _Checked:
    profile = read.model(artefacts.PROFILE, ProjectProfile)
    test = read.model(artefacts.REAL_WORLD_TEST, RealWorldTest)
    found = {r.hypothesis for r in test.results}
    hypotheses = [] if profile.hypotheses == "unknown" else [h.id for h in profile.hypotheses]
    problems = [
        f"{h} has no finding from the real-world test" for h in hypotheses if h not in found
    ]
    problems += [
        f"{h} is not a hypothesis in the profile" for h in sorted(found) if h not in hypotheses
    ]
    return _Checked(problems, [read.workspace.artefact(artefacts.REAL_WORLD_TEST)])


_CHECKS: dict[Gate, Callable[[_Reading], _Checked]] = {
    Gate.G0: _g0,
    Gate.G1: _g1,
    Gate.G2: _g2,
    Gate.G3: _g3,
    Gate.G4: _g4,
    Gate.G5: _g5,
}


def validate(gate: Gate, workspace: Workspace) -> GateOutcome:
    """The validation node's work for one gate: the only place a pass is produced."""
    read = _Reading(workspace)
    try:
        checked = _CHECKS[gate](read)
    except _MissingError as missing:
        return GateOutcome(
            gate=gate,
            status=GateStatus.INCOMPLETE,
            problems=[f"{missing.path} does not exist yet"],
            artefacts=dict(sorted(read.seen.items())),
        )
    except KilnError as exc:
        return GateOutcome(
            gate=gate,
            status=GateStatus.FAILED,
            problems=[exc.one_line()],
            artefacts=dict(sorted(read.seen.items())),
        )
    seen = dict(sorted(read.seen.items()))
    if checked.problems:
        return GateOutcome(
            gate=gate, status=GateStatus.FAILED, problems=checked.problems, artefacts=seen
        )
    if not gate.tom_decides:
        return GateOutcome(gate=gate, status=GateStatus.PASSED, artefacts=seen)
    required = {path: seen[path] for path in checked.for_tom}
    return _toms_decision(gate, required, workspace.approvals(), seen)


def _toms_decision(
    gate: Gate, required: dict[str, str], approvals: list[CardApproval], seen: dict[str, str]
) -> GateOutcome:
    """Has Tom approved these files, at these hashes, at this gate or a later one?

    In order: an approval that covers them passes; Tom's latest answer at this gate, if it
    was not the pass option, fails; a card awaiting his answer or merge waits; an approval at
    this gate for other versions fails, since the files changed after he approved them; and
    with no card at all, the gate waits for one.
    """
    cards = sorted(
        (_GateCard(a) for a in approvals if a.card is not None and a.card.gate is not None),
        key=lambda c: c.number,
    )
    later = [c for c in cards if GATES.index(c.gate) >= GATES.index(gate)]

    def result(status: GateStatus, problem: str | None = None, by: _GateCard | None = None):
        return GateOutcome(
            gate=gate,
            status=status,
            problems=[problem] if problem else [],
            artefacts=seen,
            approved_by=by.approval.card_id if by else None,
            card_sha256=by.approval.card_sha256 if by else None,
        )

    passing = [c for c in later if c.approves and not c.changed(required)]
    if passing:
        return result(GateStatus.PASSED, by=passing[-1])
    own = [c for c in cards if c.gate is gate and c.approval.status is not Status.SUPERSEDED]
    latest = own[-1] if own else None
    declined = (
        latest
        and latest.approval.approved_at
        and latest.approval.choice != (latest.card.gate.pass_option if latest.card.gate else None)
    )
    if latest and declined and not latest.approval.card_edited:
        return result(
            GateStatus.FAILED,
            f"Tom answered {latest.approval.choice!r} in {latest.approval.card_id}",
        )
    pending = [c for c in later if c.pending and not c.changed(required)]
    if pending:
        waiting = pending[-1].approval
        what = "his answer" if waiting.status is Status.OPEN else "his merge"
        return result(GateStatus.AWAITING_TOM, f"{waiting.card_id} awaits {what}")
    if latest and not latest.pending:
        why = "; ".join(latest.approval.notes) or (
            "changed since Tom approved it: " + ", ".join(latest.changed(required))
        )
        return result(
            GateStatus.FAILED,
            f"{latest.approval.card_id} no longer holds ({why}); put the change to Tom in a "
            "new card that supersedes it",
        )
    return result(
        GateStatus.AWAITING_TOM,
        f"no card puts {gate.value} to Tom; write one resting on " + ", ".join(sorted(required)),
    )


@dataclass(frozen=True)
class _GateCard:
    """A card that decides a gate, with what its approval history says."""

    approval: CardApproval

    @property
    def card(self) -> DecisionCard:
        if self.approval.card is None:
            raise ValueError("a gate card always has its card")
        return self.approval.card

    @property
    def gate(self) -> Gate:
        if self.card.gate is None:
            raise ValueError("a gate card always names its gate")
        return self.card.gate.gate

    @property
    def number(self) -> int:
        return parse_record_id(self.card.id)[1]

    @property
    def approves(self) -> bool:
        """Approved by Tom's merge, with the answer that passes the gate.

        A card that lapsed because a file it rests on changed still approves the files that
        did not; `changed` decides whether those are the ones a gate needs. A card that was
        itself edited approves nothing."""
        decision = self.card.gate
        stands = self.approval.status is Status.APPROVED or (
            self.approval.status is Status.LAPSED and not self.approval.card_edited
        )
        return (
            stands
            and self.approval.approved_at is not None
            and decision is not None
            and self.approval.choice == decision.pass_option
        )

    @property
    def pending(self) -> bool:
        return self.approval.status in (Status.OPEN, Status.AWAITING_MERGE)

    def changed(self, required: dict[str, str]) -> list[str]:
        """The required files this card does not name at their current hash."""
        named = {entry.path: entry.sha256 for entry in self.card.rests_on}
        return sorted(path for path, digest in required.items() if named.get(path) != digest)


# The machine ----------------------------------------------------------------------------------


class GateState(TypedDict):
    """The run's state. Outcomes are plain data: whatever is written here is re-validated
    before anything relies on it."""

    outcomes: Annotated[list[dict[str, Any]], operator.add]


def _confirm(state: GateState, workspace: Workspace, at: Gate) -> GateOutcome | None:
    """A refusal for the first recorded pass that does not hold now, or None if all hold."""
    for raw in state["outcomes"]:
        try:
            recorded = GateOutcome.model_validate(raw)
        except ValidationError as exc:
            return GateOutcome(
                gate=at,
                status=GateStatus.FAILED,
                problems=[f"the run's state holds a malformed outcome: {exc}"],
            )
        if recorded.status is not GateStatus.PASSED:
            continue
        now = validate(recorded.gate, workspace)
        if now != recorded:
            return GateOutcome(
                gate=recorded.gate,
                status=GateStatus.FAILED,
                problems=[
                    f"refused a pass recorded for {recorded.gate.value}: re-validated now, the "
                    f"gate is {now.status.value}. Only its validation node writes a pass, and a "
                    "pass holds only for the files it names",
                    *now.problems,
                ],
                artefacts=now.artefacts,
            )
    return None


class GateMachine:
    """G0 to G5 in order, stopping at the first gate that does not pass."""

    def __init__(
        self,
        workspace: Callable[[], Workspace],
        checkpointer: BaseCheckpointSaver[str] | None = None,
    ) -> None:
        self._workspace = workspace
        builder: StateGraph[GateState] = StateGraph(GateState)
        for gate in GATES:
            builder.add_node(gate.value, self._node(gate))  # pyright: ignore[reportUnknownMemberType]
        builder.add_edge(START, Gate.G0.value)
        for gate, following in itertools.pairwise(GATES):
            builder.add_conditional_edges(gate.value, self._router(gate, following.value))
        builder.add_edge(Gate.G5.value, END)
        self.graph = builder.compile(  # pyright: ignore[reportUnknownMemberType]
            checkpointer=checkpointer
        )

    def _node(self, gate: Gate):  # LangGraph checks the node's parameter name, so no Callable type
        def node(state: GateState) -> dict[str, list[dict[str, Any]]]:
            workspace = self._workspace()
            outcome = _confirm(state, workspace, gate) or validate(gate, workspace)
            return {"outcomes": [outcome.model_dump(mode="json")]}

        return node

    @staticmethod
    def _router(gate: Gate, following: str) -> Callable[[GateState], str]:
        def route(state: GateState) -> str:
            last = GateOutcome.model_validate(state["outcomes"][-1])
            passed = last.gate is gate and last.status is GateStatus.PASSED
            return following if passed else END

        return route

    def run(self, thread_id: str | None = None) -> list[GateOutcome]:
        """Walk the gates from G0. A `thread_id` needs the machine's checkpointer."""
        return self._invoke({"outcomes": []}, thread_id)

    def resume(self, thread_id: str) -> list[GateOutcome]:
        """Continue a checkpointed run from wherever its state now points."""
        return self._invoke(None, thread_id)

    def _invoke(self, start: GateState | None, thread_id: str | None) -> list[GateOutcome]:
        config: dict[str, Any] = {"configurable": {"thread_id": thread_id}} if thread_id else {}
        with tracing_context(enabled=False):
            final = self.graph.invoke(  # pyright: ignore[reportUnknownMemberType]
                start,
                config,  # pyright: ignore[reportArgumentType]
            )
        raw: list[dict[str, Any]] = final["outcomes"]
        return [GateOutcome.model_validate(item) for item in raw]


def run_gates(root: Path, council: Path = COUNCIL_DIR, ref: str = DEFAULT_REF) -> list[GateOutcome]:
    """Walk one solution's gates, reading its files and `ref`'s history as they are now."""
    if not (root / council).is_dir():
        raise KilnError(
            "no council folder here", item=str(root / council), see="src/kiln/artefacts.py"
        )
    return GateMachine(lambda: Workspace(root, council, ref)).run()


def render(outcomes: list[GateOutcome]) -> str:
    lines: list[str] = []
    for outcome in outcomes:
        by = f" ({outcome.approved_by})" if outcome.approved_by else ""
        lines.append(f"{outcome.gate.value} {outcome.gate.label}: {outcome.status.value}{by}")
        lines += [f"  - {problem}" for problem in outcome.problems]
    reached = [o.gate for o in outcomes if o.status is GateStatus.PASSED]
    if len(reached) == len(GATES):
        lines.append("Every gate passes.")
    return "\n".join(lines)
