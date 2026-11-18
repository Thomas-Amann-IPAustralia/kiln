"""The id formats every record and agent shares (sketch, "Contracts others will depend on").

- A **record id** names its kind: `DEC-0001`, `CARD-0001`, `OBL-0001`, `FND-0001`, `TKT-0001`.
- **Evidence is addressed by content:** `sha256:<64 hex digits>` of the exact bytes.
- A **source id** names its source: `<source>:<local-id>`. Stores keep local ids; the boundary
  qualifies them, so an agent never sees a bare local id (SOP D-057).

These are contracts. Changing one changes every agent that reads it, so they are settled here,
before their first consumer, and changed only with a decision entry.
"""

from __future__ import annotations

import hashlib
import re
from enum import StrEnum
from typing import Annotated

from pydantic import AfterValidator, Field


class RecordKind(StrEnum):
    """The kinds of numbered record. The value is the id's prefix."""

    DECISION = "DEC"
    """A decision record: a decision the Council makes while building a solution."""
    CARD = "CARD"
    """A decision card: a decision put to Tom."""
    OBLIGATION = "OBL"
    FINDING = "FND"
    TICKET = "TKT"


_RECORD_ID = re.compile(r"^(DEC|CARD|OBL|FND|TKT)-(\d{4,})$")
_CONTENT_HASH = re.compile(r"^sha256:[0-9a-f]{64}$")
_SOURCE_ID = re.compile(r"^([a-z][a-z0-9_-]*):(\S+)$")


def record_id(kind: RecordKind, number: int) -> str:
    """The id of record `number` of `kind`, such as `DEC-0007`."""
    if number < 1:
        raise ValueError(f"record numbers start at 1, not {number}")
    return f"{kind.value}-{number:04d}"


def parse_record_id(value: str) -> tuple[RecordKind, int]:
    """Split a record id into its kind and number, or raise `ValueError`."""
    match = _RECORD_ID.match(value)
    if match is None or int(match.group(2)) < 1:
        raise ValueError(f"not a record id (KIND-NNNN, numbered from 0001): {value!r}")
    return RecordKind(match.group(1)), int(match.group(2))


def _id_of(kind: RecordKind) -> AfterValidator:
    def check(value: str) -> str:
        if parse_record_id(value)[0] is not kind:
            raise ValueError(f"expected a {kind.value}- id, got {value!r}")
        return value

    return AfterValidator(check)


DecisionId = Annotated[str, _id_of(RecordKind.DECISION)]
CardId = Annotated[str, _id_of(RecordKind.CARD)]
ObligationId = Annotated[str, _id_of(RecordKind.OBLIGATION)]
FindingId = Annotated[str, _id_of(RecordKind.FINDING)]
TicketId = Annotated[str, _id_of(RecordKind.TICKET)]

ContentHash = Annotated[str, Field(pattern=_CONTENT_HASH.pattern)]
"""`sha256:<hex>` of a file's exact bytes."""


def content_hash(data: bytes) -> str:
    """The content address of `data`: `sha256:<hex>`."""
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _check_evidence_ref(value: str) -> str:
    if _CONTENT_HASH.match(value):
        return value
    source = _SOURCE_ID.match(value)
    if source is None or source.group(1) == "sha256":
        raise ValueError(
            f"evidence must be `sha256:<64 hex>` or `<source>:<local-id>`, not {value!r}"
        )
    return value


EvidenceRef = Annotated[str, AfterValidator(_check_evidence_ref)]
"""An exact item a claim rests on: a content hash, or a qualified source id."""
