"""The base every record model shares, and the small field types they all use."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

from kiln.vocabulary import EXPERTS, Actor

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


def _repo_relative(value: str) -> str:
    pure = PurePosixPath(value)
    if not value or pure.is_absolute() or ".." in pure.parts or "\\" in value or str(pure) != value:
        raise ValueError(f"must be a plain repo-relative path, not {value!r}")
    return value


RepoPath = Annotated[str, AfterValidator(_repo_relative)]
"""A file's path relative to the repository root, with forward slashes and no `..`."""


def _an_expert(actor: Actor) -> Actor:
    if actor not in EXPERTS:
        raise ValueError(f"must be a Council expert, not {actor.value!r}")
    return actor


Expert = Annotated[Actor, AfterValidator(_an_expert)]
"""An actor who is one of the seven Council experts."""
