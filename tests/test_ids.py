from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from kiln.ids import (
    CardId,
    DecisionId,
    EvidenceRef,
    RecordKind,
    content_hash,
    parse_record_id,
    record_id,
)


class _Ids(BaseModel):
    decision: DecisionId | None = None
    card: CardId | None = None
    evidence: EvidenceRef | None = None


def test_record_ids_name_their_kind_and_round_trip() -> None:
    """Why: every agent parses these ids; a format drift would break all of them at once."""
    assert record_id(RecordKind.DECISION, 7) == "DEC-0007"
    assert parse_record_id("CARD-0012") == (RecordKind.CARD, 12)
    assert parse_record_id("TKT-12345") == (RecordKind.TICKET, 12345)


@pytest.mark.parametrize("bad", ["DEC-7", "dec-0001", "DEC-0000", "ADR-0001", "DEC-0001x"])
def test_malformed_record_ids_are_refused(bad: str) -> None:
    """Why: a loose id would collide with an ADR or D-NNN number, or sort out of order."""
    with pytest.raises(ValueError, match="not a record id"):
        parse_record_id(bad)


def test_a_decision_id_field_refuses_a_card_id() -> None:
    """Why: an id names its kind, so a card cannot stand where a decision is expected."""
    assert _Ids(decision="DEC-0001").decision == "DEC-0001"
    with pytest.raises(ValidationError, match="expected a DEC- id"):
        _Ids(decision="CARD-0001")


def test_evidence_is_a_content_hash_or_a_qualified_source_id() -> None:
    """Why: evidence must name an exact item; a bare local id loses its source (SOP D-057)."""
    empty = "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert content_hash(b"") == empty  # the published SHA-256 of no bytes
    digest = content_hash(b"placeholder")
    assert _Ids(evidence=digest).evidence == digest
    assert _Ids(evidence="legislation:privacy-act-s6").evidence == "legislation:privacy-act-s6"
    for bad in ["privacy-act", "sha256:abc", "Source:x", "web: spaced"]:
        with pytest.raises(ValidationError, match="evidence must be"):
            _Ids(evidence=bad)
