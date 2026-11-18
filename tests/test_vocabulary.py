from __future__ import annotations

from kiln.vocabulary import EXPERTS, Actor, Band, Basis, Gate, Tripwire


def test_basis_is_the_charters_seven_values() -> None:
    """Why: rule 7 fixes the seven labels; an eighth would be a term no other agent knows."""
    assert [b.value for b in Basis] == [
        "observed",
        "authoritative",
        "rule",
        "supported",
        "inferred",
        "assumed",
        "unknown",
    ]


def test_the_envelope_has_four_bands_and_the_charter_four_tripwires() -> None:
    """Why: Tom's authority rests on these lists being exactly the charter's."""
    assert [b.value for b in Band] == ["green", "amber", "red", "tom"]
    assert [t.number for t in Tripwire] == [1, 2, 3, 4]
    assert Tripwire.SPEND_OVER_BUDGET.number == 4


def test_tom_decides_at_g0_g2_g4_and_g5_only() -> None:
    """Why: the gates read this to know where to stop for Tom (ADR-0013)."""
    assert [g.value for g in Gate if g.tom_decides] == ["G0", "G2", "G4", "G5"]
    assert Gate.G2.label == "design"


def test_the_council_is_seven_experts_and_excludes_tom_and_the_swarm() -> None:
    """Why: only an expert may write dissent, so this set guards who can."""
    assert len(EXPERTS) == 7
    assert Actor.TOM not in EXPERTS
    assert Actor.CODING_SWARM not in EXPERTS
    assert Actor.BUILD_SESSION not in EXPERTS
