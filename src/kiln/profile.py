"""The project profile: the one structured record of a solution's question, users, hypotheses,
proportionality profile and budget (charter, "The shared core"; ADR-0023).

`unknown` is a valid value, and distinct from missing: every field must be present, and a fact
nobody knows yet is stated as `unknown`. The three proportionality facts carry the basis of
their value, because they size every expert's work and an inferred one should be confirmable.

This module checks a profile's shape. Whether a profile is ready to pass G0 (for example, that
its hypotheses cover desirability, viability and feasibility) is the gate's check, not the
schema's. Each expert's own section of the profile arrives with that expert, from phase 1.
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Annotated, Generic, Literal, TypeVar

import yaml
from pydantic import Field, ValidationError, field_validator, model_validator

from kiln.errors import KilnError
from kiln.model import UNKNOWN, Record, Slug, Text, Unknown
from kiln.vocabulary import Basis


class Audience(StrEnum):
    """Who will use the solution (charter seed: "Tom's team, the agency or the public")."""

    TOMS_TEAM = "toms_team"
    AGENCY = "agency"
    PUBLIC = "public"


class DataKind(StrEnum):
    """What data the solution touches. The list is the Governance proposal's intake "Data"
    row, with two added so that every solution has a true answer: `public` for published
    information and `internal` for unpublished information that is none of the other kinds.
    It states what the solution touches; classification itself is set by the information
    owner (ADR-0005). The Governance Guru refines this list in phase 2."""

    PUBLIC = "public"
    INTERNAL = "internal"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    CLASSIFIED = "classified"
    COMMERCIAL = "commercial"
    HEALTH = "health"
    INDIGENOUS = "indigenous"
    LINKED = "linked"


class Effect(StrEnum):
    """Whether the solution informs, acts or decides about people: the strongest that applies."""

    INFORMS = "informs"
    ACTS = "acts"
    DECIDES = "decides"


class Dimension(StrEnum):
    """Which part of DVF a hypothesis tests."""

    DESIRABILITY = "desirability"
    VIABILITY = "viability"
    FEASIBILITY = "feasibility"


V = TypeVar("V")


class Fact(Record, Generic[V]):
    """One intake fact, with how it is known. `unknown` goes with basis `unknown`, and only
    with it, so a guess cannot pass as a known value or the reverse."""

    value: V | Unknown
    basis: Basis
    note: Text | None = None

    @model_validator(mode="after")
    def _unknown_iff_basis_unknown(self) -> Fact[V]:
        if (self.value == UNKNOWN) != (self.basis is Basis.UNKNOWN):
            raise ValueError("a value of `unknown` needs basis `unknown`, and only it does")
        return self


Audiences = Annotated[list[Audience], Field(min_length=1)]
DataKinds = Annotated[list[DataKind], Field(min_length=1)]


class ProportionalityProfile(Record):
    """The three intake facts that size every expert's work (ADR-0023)."""

    who_uses: Fact[Audiences]
    data_touched: Fact[DataKinds]
    effect_on_people: Fact[Effect]

    @model_validator(mode="after")
    def _no_repeats(self) -> ProportionalityProfile:
        for name, values in (
            ("who_uses", self.who_uses.value),
            ("data_touched", self.data_touched.value),
        ):
            if isinstance(values, list) and len(set(values)) != len(values):
                raise ValueError(f"{name}: a value is listed twice")
        return self


class UserGroup(Record):
    name: Text
    description: Text


class Hypothesis(Record):
    """A claim a real-world test can support or refute. Its measure may be `unknown` at intake;
    G2 needs one for every hypothesis."""

    id: Annotated[str, Field(pattern=r"^H[1-9][0-9]*$")]
    dimension: Dimension
    statement: Text
    measure: Text | Unknown


class SolutionBudget(Record):
    """Tom's budget for the solution, in US dollars."""

    build_usd: Annotated[float, Field(gt=0)] | Unknown
    """What Kiln may spend building it: model calls, sandboxes and services."""
    run_usd_per_month: Annotated[float, Field(ge=0)] | Unknown
    """What it may cost to run during the real-world test."""


class ProjectProfile(Record):
    """One solution's `profile.yaml`."""

    version: Literal[1]
    solution: Slug
    title: Text
    question: Text
    """The question Tom sets at G0, in one sentence. Never `unknown`."""
    brief: Text
    """What Tom brought to intake, verbatim."""
    users: Annotated[list[UserGroup], Field(min_length=1)] | Unknown
    hypotheses: Annotated[list[Hypothesis], Field(min_length=1)] | Unknown
    proportionality: ProportionalityProfile
    budget: SolutionBudget

    @field_validator("hypotheses")
    @classmethod
    def _hypothesis_ids_distinct(
        cls, hypotheses: list[Hypothesis] | Unknown
    ) -> list[Hypothesis] | Unknown:
        if isinstance(hypotheses, list):
            ids = [hypothesis.id for hypothesis in hypotheses]
            if len(set(ids)) != len(ids):
                raise ValueError("hypothesis ids must not repeat")
        return hypotheses


def load_profile(path: Path) -> ProjectProfile:
    """Read and validate a profile, or raise a `KilnError` naming the first problem."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise KilnError("profile not found", item=str(path)) from exc
    except yaml.YAMLError as exc:
        raise KilnError(f"profile is not valid YAML: {exc}", item=str(path)) from exc
    try:
        return ProjectProfile.model_validate(raw)
    except ValidationError as exc:
        first = exc.errors()[0]
        where = ".".join(str(part) for part in first["loc"]) or "(profile)"
        raise KilnError(
            f"profile is invalid ({exc.error_count()} problem(s)); first: {where}: {first['msg']}",
            item=str(path),
            see="src/kiln/profile.py",
        ) from exc
