"""The artefacts each gate reads, in a solution's `council/` folder.

Each model here is the **minimum its gate needs** to run the checks the charter names for it
(`docs/charter/operating-model.md`, "How a solution moves through the Council"). The expert who
owns an artefact extends it when that expert is built: the Governance Guru the applicability
register, the chair the plan. A field is here only because a gate check reads it.

| Gate | Artefact | Owner, when built |
| --- | --- | --- |
| G0 | `profile.yaml` (`kiln.profile`) | Solution Architect |
| G1 | `applicability.yaml` | Governance Guru |
| G2 | `plan.yaml`, the G2 packet, the domain contracts | Solution Architect |
| G3 | `build.yaml` | The verifier (slice 4) |
| G4 | `pre-release.yaml`, the assurance case, the real-world test plan | Governance Guru |
| G5 | `real-world-test.yaml` | Data Analyst |

**Until slice 4,** `build.yaml` is written by hand, so a ticket's `passes` in it is a claim, not
a verified result. Slice 4 makes the verifier its only writer (ADR-0027).
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field, model_validator

from kiln.ids import EvidenceRef, FindingId, ObligationId, TicketId
from kiln.model import Expert, Record, RepoPath, Slug, Text
from kiln.vocabulary import Actor, Tripwire

PROFILE = "profile.yaml"
APPLICABILITY = "applicability.yaml"
PLAN = "plan.yaml"
BUILD = "build.yaml"
PRE_RELEASE = "pre-release.yaml"
REAL_WORLD_TEST = "real-world-test.yaml"


def _distinct(values: list[str], what: str) -> None:
    if len(set(values)) != len(values):
        raise ValueError(f"{what} must not repeat")


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# G1 -------------------------------------------------------------------------------------------


class Obligation(Record):
    """An obligation that applies to this solution, and the expert who owns meeting it."""

    id: ObligationId
    title: Text
    source: EvidenceRef
    """The law, policy or standard it comes from."""
    owner: Expert


class ApplicabilityRegister(Record):
    """Which obligations apply, sized to the profile, and which experts the routing calls in."""

    version: Literal[1]
    triggered_experts: Annotated[list[Expert], Field(min_length=1)]
    obligations: list[Obligation]

    @model_validator(mode="after")
    def _consistent(self) -> ApplicabilityRegister:
        _distinct([e.value for e in self.triggered_experts], "triggered experts")
        _distinct([o.id for o in self.obligations], "obligation ids")
        if Actor.SOLUTION_ARCHITECT not in self.triggered_experts:
            raise ValueError("the chair, solution_architect, works on every solution")
        for obligation in self.obligations:
            if obligation.owner not in self.triggered_experts:
                raise ValueError(
                    f"{obligation.id} is owned by {obligation.owner.value}, who is not triggered"
                )
        return self


# G2 -------------------------------------------------------------------------------------------


class DomainContract(Record):
    id: Slug
    owner: Expert
    path: RepoPath


class PlannedTicket(Record):
    id: TicketId
    title: Text
    contract: Slug
    """The domain contract it traces to."""


class ReviewFinding(Record):
    """A finding from the cross-provider review, and its owner's response (ADR-0026)."""

    id: FindingId
    severity: Severity
    summary: Text
    owner: Expert
    response: Literal["accepted", "rejected"]
    reason: Text


class Review(Record):
    reviewer: Text
    """The model that reviewed the plan, from a provider other than the plan's author."""
    findings: list[ReviewFinding]


class CostEstimate(Record):
    build_usd: Annotated[float, Field(ge=0)]
    run_usd_per_month: Annotated[float, Field(ge=0)]


class Plan(Record):
    """What G2 asks Tom to approve, beside the G2 packet he reads."""

    version: Literal[1]
    consulted_experts: Annotated[list[Expert], Field(min_length=1)]
    contracts: Annotated[list[DomainContract], Field(min_length=1)]
    tickets: Annotated[list[PlannedTicket], Field(min_length=1)]
    review: Review
    estimate: CostEstimate
    packet: RepoPath
    """The G2 packet: the short plain-language summary Tom reads."""

    @model_validator(mode="after")
    def _consistent(self) -> Plan:
        _distinct([e.value for e in self.consulted_experts], "consulted experts")
        _distinct([c.id for c in self.contracts], "contract ids")
        _distinct([t.id for t in self.tickets], "ticket ids")
        _distinct([f.id for f in self.review.findings], "finding ids")
        contracts = {c.id for c in self.contracts}
        for ticket in self.tickets:
            if ticket.contract not in contracts:
                raise ValueError(f"{ticket.id} traces to {ticket.contract!r}, not a contract here")
        return self


# G3 -------------------------------------------------------------------------------------------


class TicketResult(Record):
    id: TicketId
    passes: bool


class BuildRecord(Record):
    """The state of the build at one commit."""

    version: Literal[1]
    commit: Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
    engineering_checks: Literal["passed", "failed"]
    tickets: list[TicketResult]
    open_tripwires: list[Tripwire]

    @model_validator(mode="after")
    def _consistent(self) -> BuildRecord:
        _distinct([t.id for t in self.tickets], "ticket ids")
        return self


# G4 -------------------------------------------------------------------------------------------


class ReleaseFinding(Record):
    id: FindingId
    severity: Severity
    status: Literal["fixed", "explained", "open"]
    explanation: Text | None = None

    @model_validator(mode="after")
    def _explained(self) -> ReleaseFinding:
        if (self.status == "explained") != (self.explanation is not None):
            raise ValueError("an `explained` finding needs an explanation, and only it has one")
        return self


class ObligationStatus(Record):
    """Whether an obligation is met, with evidence, or deferred, with a reason."""

    id: ObligationId
    status: Literal["met", "deferred"]
    evidence: list[EvidenceRef] = Field(default_factory=list[EvidenceRef])
    reason: Text | None = None

    @model_validator(mode="after")
    def _supported(self) -> ObligationStatus:
        if self.status == "met" and not self.evidence:
            raise ValueError(f"{self.id} is met, so it needs evidence")
        if self.status == "deferred" and self.reason is None:
            raise ValueError(f"{self.id} is deferred, so it needs a reason")
        return self


class PreRelease(Record):
    version: Literal[1]
    findings: list[ReleaseFinding]
    obligations: list[ObligationStatus]
    assurance_case: RepoPath
    test_plan: RepoPath
    """The real-world test plan."""

    @model_validator(mode="after")
    def _consistent(self) -> PreRelease:
        _distinct([f.id for f in self.findings], "finding ids")
        _distinct([o.id for o in self.obligations], "obligation ids")
        return self


# G5 -------------------------------------------------------------------------------------------


class HypothesisResult(Record):
    hypothesis: Annotated[str, Field(pattern=r"^H[1-9][0-9]*$")]
    finding: Literal["supported", "refuted", "inconclusive"]
    evidence: Annotated[list[EvidenceRef], Field(min_length=1)]
    summary: Text


class RealWorldTest(Record):
    """What the real-world test found against each hypothesis."""

    version: Literal[1]
    results: Annotated[list[HypothesisResult], Field(min_length=1)]

    @model_validator(mode="after")
    def _consistent(self) -> RealWorldTest:
        _distinct([r.hypothesis for r in self.results], "hypotheses")
        return self
