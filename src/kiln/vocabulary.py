"""The fixed vocabularies every record uses: basis, actors, bands, tripwires and gates.

Each is one enum, so a value outside the charter's list is a validation error, not a new term.
Values are the `GLOSSARY.md` terms in lower case. Changing a value changes every record that
holds it, so a rename happens everywhere in one commit (handover, open item 2).
"""

from __future__ import annotations

from enum import StrEnum


class Basis(StrEnum):
    """How a claim is known (charter rule 7). Every claim carries one."""

    OBSERVED = "observed"
    """Seen directly: a measurement, a run, a file read."""
    AUTHORITATIVE = "authoritative"
    """Stated by a source with authority over the point: a law, a policy, or Tom on his own
    intent."""
    RULE = "rule"
    """Follows from a rule the Council applies, such as a routing trigger."""
    SUPPORTED = "supported"
    """Backed by evidence that is good but not authoritative."""
    INFERRED = "inferred"
    """Read from evidence that does not state it."""
    ASSUMED = "assumed"
    """Taken as true without evidence, until checked."""
    UNKNOWN = "unknown"
    """Not known. Missing evidence stays missing."""


class Actor(StrEnum):
    """Who made a record (charter rule 5). Prose naming an actor confers nothing."""

    TOM = "tom"
    SOLUTION_ARCHITECT = "solution_architect"
    RESEARCHER = "researcher"
    SECURITY_ARCHITECT = "security_architect"
    GOVERNANCE_GURU = "governance_guru"
    DATA_ENGINEER = "data_engineer"
    UX_DESIGNER = "ux_designer"
    DATA_ANALYST = "data_analyst"
    CODING_SWARM = "coding_swarm"
    BUILD_SESSION = "build_session"
    """An agent session building Kiln itself, outside the Council."""


EXPERTS: frozenset[Actor] = frozenset(
    {
        Actor.SOLUTION_ARCHITECT,
        Actor.RESEARCHER,
        Actor.SECURITY_ARCHITECT,
        Actor.GOVERNANCE_GURU,
        Actor.DATA_ENGINEER,
        Actor.UX_DESIGNER,
        Actor.DATA_ANALYST,
    }
)
"""The seven members of the Council. Only an expert writes dissent."""


class Band(StrEnum):
    """The autonomy envelope: what an agent or loop may do with a decision."""

    GREEN = "green"
    """Decide, record, continue."""
    AMBER = "amber"
    """Proceed provisionally, record, and notify the owning expert."""
    RED = "red"
    """Pause that path; the owning expert decides."""
    TOM = "tom"
    """Stop that path and ask Tom."""


class Tripwire(StrEnum):
    """The four conditions that stop the affected work until Tom decides (charter, Purpose)."""

    REAL_DATA_IN_BUILD = "real_data_in_build"
    EXPOSED_SECRET = "exposed_secret"  # noqa: S105 -- a tripwire's name, not a secret
    REAL_WORLD_ACTION_BEFORE_APPROVAL = "real_world_action_before_approval"
    SPEND_OVER_BUDGET = "spend_over_budget"

    @property
    def number(self) -> int:
        """The tripwire's number in the charter, 1 to 4."""
        return list(Tripwire).index(self) + 1


class Gate(StrEnum):
    """The six checkpoints a solution passes in order."""

    G0 = "G0"
    G1 = "G1"
    G2 = "G2"
    G3 = "G3"
    G4 = "G4"
    G5 = "G5"

    @property
    def label(self) -> str:
        """What the gate settles, as the glossary names it: intake, applicability and so on."""
        return _GATE_LABELS[self]

    @property
    def tom_decides(self) -> bool:
        """Tom decides at G0, G2, G4 and G5; a validation node passes G1 and G3."""
        return self in _TOM_GATES


_GATE_LABELS = {
    Gate.G0: "intake",
    Gate.G1: "applicability",
    Gate.G2: "design",
    Gate.G3: "build",
    Gate.G4: "pre-release",
    Gate.G5: "real-world test",
}
_TOM_GATES = frozenset({Gate.G0, Gate.G2, Gate.G4, Gate.G5})
