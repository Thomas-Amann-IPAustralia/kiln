"""The base every record model shares, and the small field types they all use."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

Unknown = Literal["unknown"]
"""A stated `unknown`: a valid answer, and distinct from a missing one."""

UNKNOWN: Unknown = "unknown"


class Record(BaseModel):
    """A record is immutable once built, and an unknown key is an error: a typo must never
    become a silently ignored field."""

    model_config = ConfigDict(extra="forbid", frozen=True)


def _not_blank(value: str) -> str:
    if not value.strip():
        raise ValueError("must not be blank")
    return value


Text = Annotated[str, AfterValidator(_not_blank)]
"""Text that says something: not empty, not only whitespace."""

Slug = Annotated[str, Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")]
"""Lower-case words and digits joined by single hyphens, such as `public-form-service`."""
