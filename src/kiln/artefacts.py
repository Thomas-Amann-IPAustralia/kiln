"""The artefacts each gate reads, in a solution's `council/` folder.

Each model here is the **minimum its gate needs** to run the checks the charter names for it
(`docs/charter/operating-model.md`, "How a solution moves through the Council"). The expert who
owns an artefact extends it when that expert is built: the Governance Guru the applicability
register, the chair the plan. A field is here only because a gate check reads it.

| Gate | Artefact | Owner, when built |
| --- | --- | --- |
| G0 | `profile.yaml` (`kiln.profile`) | Solution Architect |
| G1 | `applicability.yaml` | Governance Guru |
| G2 | `plan.yaml`, `tickets.json`, the G2 packet, the domain contracts | Solution Architect |
| G3 | `build.yaml` | The verifier (`kiln.verifier`), and nothing else |
| G4 | `pre-release.yaml`, the assurance case, the real-world test plan | Governance Guru |
| G5 | `real-world-test.yaml` | Data Analyst |

`build.yaml` is the verifier's record of one commit: what it judged the commit against, and each
check's and step's result. A ticket's `passes` lives there, never in `tickets.json`, so the file
Tom approved at G2 does not change when a ticket passes (ADR-0027, D-014).
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Literal, TypeVar

import yaml
from pydantic import BaseModel, Field, ValidationError, model_validator

from kiln.errors import KilnError
from kiln.ids import ContentHash, EvidenceRef, FindingId, ObligationId, TicketId
from kiln.model import Expert, Record, RepoPath, Slug, Text
from kiln.vocabulary import Actor, Tripwire

COUNCIL_DIR = Path("council")
PROFILE = "profile.yaml"
APPLICABILITY = "applicability.yaml"
PLAN = "plan.yaml"
TICKETS = "tickets.json"
BUILD = "build.yaml"
PRE_RELEASE = "pre-release.yaml"
REAL_WORLD_TEST = "real-world-test.yaml"


M = TypeVar("M", bound=BaseModel)


def parse_yaml(data: bytes, model: type[M], *, item: str) -> M:
    """Validate a YAML artefact's bytes, or raise a `KilnError` naming its first problem."""
    try:
        raw: object = yaml.safe_load(data.decode("utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        raise KilnError(f"not valid YAML: {exc}", item=item) from exc
    try:
        return model.model_validate(raw)
    except ValidationError as exc:
        first = exc.errors()[0]
        where = ".".join(str(part) for part in first["loc"]) or "(file)"
        raise KilnError(
            f"invalid {model.__name__}; first of {exc.error_count()}: {where}: {first['msg']}",
            item=item,
        ) from exc


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
    """The tickets that trace to them are in `tickets.json` (`kiln.tickets`)."""
    review: Review
    estimate: CostEstimate
    packet: RepoPath
    """The G2 packet: the short plain-language summary Tom reads."""

    @model_validator(mode="after")
    def _consistent(self) -> Plan:
        _distinct([e.value for e in self.consulted_experts], "consulted experts")
        _distinct([c.id for c in self.contracts], "contract ids")
        _distinct([c.path for c in self.contracts], "contract paths")
        _distinct([f.id for f in self.review.findings], "finding ids")
        return self


# G3 -------------------------------------------------------------------------------------------


Commit = Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]


class Runner(StrEnum):
    """Where the verifier ran a commit's code."""

    LOCAL = "local"
    """The machine the verifier ran on, with only an environment allowlist between the code and
    it. Not a sandbox (ADR-0007); slice 5 adds one."""


class Ran(Record):
    """What one command did, run by the verifier in its own clean checkout."""

    run: Annotated[list[Text], Field(min_length=1)]
    exit_code: int | None
    """None when it did not finish: it could not start, or it ran past its timeout."""
    problem: Text | None = None
    """Why it did not finish."""
    output: str | None = None
    """The end of what it printed, kept only when it failed."""

    @property
    def passed(self) -> bool:
        return self.exit_code == 0

    @model_validator(mode="after")
    def _consistent(self) -> Ran:
        if (self.exit_code is None) != (self.problem is not None):
            raise ValueError("a command that did not finish says why, and only it does")
        if self.passed and self.output is not None:
            raise ValueError("output is kept only for a command that failed")
        return self


class CheckResult(Ran):
    name: Slug
    tripwire: Tripwire | None = None


class TicketResult(Record):
    id: TicketId
    passes: bool
    steps: list[Ran]


class BuildRecord(Record):
    """The verifier's record of one commit (ADR-0027). Nothing else writes it.

    It names what the commit was judged against, so G3 can recompute all of it from history
    except the commands' results (`kiln.verifier.recheck`)."""

    version: Literal[2]
    verified_by: Literal[Actor.VERIFIER]
    verified_on: date
    runner: Runner
    ref: Text
    """The branch Tom merges into, which the commit's branch started from."""
    base: Commit
    """Where the commit's branch left `ref`: a commit on its first-parent history."""
    commit: Commit
    tickets_sha256: ContentHash
    """The ticket list at `base`, whose checks and steps were run."""
    plan_sha256: ContentHash
    """The plan at `base`, which names the contracts a loop may not change."""
    refused: list[Text]
    """Paths read-only to loops that the commit changed. If any, nothing was run."""
    checks: list[CheckResult]
    tickets: Annotated[list[TicketResult], Field(min_length=1)]

    @property
    def open_tripwires(self) -> list[Tripwire]:
        """The tripwires whose checks failed at this commit, in the charter's order."""
        tripped = {c.tripwire for c in self.checks if c.tripwire and not c.passed}
        return [t for t in Tripwire if t in tripped]

    @model_validator(mode="after")
    def _consistent(self) -> BuildRecord:
        _distinct([t.id for t in self.tickets], "ticket ids")
        _distinct([c.name for c in self.checks], "check names")
        if self.refused and (self.checks or any(t.steps for t in self.tickets)):
            raise ValueError("a refused commit is never run, so it has no results")
        if not self.refused and not self.checks:
            raise ValueError("an admitted commit runs every check")
        green = not self.refused and all(c.passed for c in self.checks)
        for ticket in self.tickets:
            earned = green and bool(ticket.steps) and all(s.passed for s in ticket.steps)
            if ticket.passes != earned:
                raise ValueError(f"{ticket.id}'s pass does not follow from its results")
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
