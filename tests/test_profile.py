from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from kiln.errors import KilnError
from kiln.profile import Audience, Effect, ProjectProfile, load_profile

SAMPLES = sorted((Path(__file__).resolve().parent.parent / "evals/sample-briefs").glob("*.yaml"))


def minimal() -> dict[str, Any]:
    """A valid profile with every fact stated. Each test below breaks one thing in it."""
    return {
        "version": 1,
        "solution": "placeholder-solution",
        "title": "Placeholder",
        "question": "Placeholder question?",
        "brief": "Placeholder brief.",
        "users": [{"name": "Placeholder users", "description": "Placeholder."}],
        "hypotheses": [
            {"id": "H1", "dimension": "desirability", "statement": "S.", "measure": "M."}
        ],
        "proportionality": {
            "who_uses": {"value": ["agency"], "basis": "authoritative"},
            "data_touched": {"value": ["internal"], "basis": "authoritative"},
            "effect_on_people": {"value": "informs", "basis": "authoritative"},
        },
        "budget": {"build_usd": 10, "run_usd_per_month": 0},
    }


def errors(data: dict[str, Any]) -> str:
    with pytest.raises(ValidationError) as caught:
        ProjectProfile.model_validate(data)
    return str(caught.value)


def test_the_three_sample_briefs_validate_as_profiles() -> None:
    """Why: slice 1's check; the thin path and the chair's first evals start from these."""
    assert [p.stem for p in SAMPLES] == [
        "data-dashboard",
        "internal-rag-assistant",
        "public-form-service",
    ]
    profiles = [load_profile(path) for path in SAMPLES]
    assert {p.solution for p in profiles} == {p.stem for p in SAMPLES}


def test_the_sample_briefs_differ_where_the_set_needs_them_to() -> None:
    """Why: an evaluation set of three alike briefs would test one case three times."""
    profiles = [load_profile(path) for path in SAMPLES]
    audiences = {
        a for p in profiles if isinstance(v := p.proportionality.who_uses.value, list) for a in v
    }
    assert audiences == set(Audience)
    effects = {p.proportionality.effect_on_people.value for p in profiles}
    assert {Effect.INFORMS, Effect.ACTS} <= effects
    assert any(p.proportionality.data_touched.value == "unknown" for p in profiles)


def test_the_minimal_profile_is_valid() -> None:
    """Why: every rejection below must fail for its own reason and no other."""
    ProjectProfile.model_validate(minimal())


def test_unknown_is_a_valid_answer() -> None:
    """Why: the charter makes `unknown` valid, so intake can proceed honestly."""
    data = minimal()
    data["users"] = "unknown"
    data["hypotheses"] = "unknown"
    data["budget"] = {"build_usd": "unknown", "run_usd_per_month": "unknown"}
    data["proportionality"]["who_uses"] = {"value": "unknown", "basis": "unknown"}
    ProjectProfile.model_validate(data)


@pytest.mark.parametrize("field", ["users", "hypotheses", "proportionality", "budget"])
def test_a_missing_fact_is_refused(field: str) -> None:
    """Why: missing is not unknown; an omitted fact must be stated, even as `unknown`."""
    data = minimal()
    del data[field]
    assert "Field required" in errors(data)


def test_the_question_cannot_be_unknown_or_blank() -> None:
    """Why: Tom sets the question at G0; without one there is nothing to build."""
    data = minimal()
    data["question"] = "   "
    assert "must not be blank" in errors(data)


def test_a_value_and_its_basis_must_agree_about_unknown() -> None:
    """Why: a guess must not pass as known, nor a known value hide behind `unknown`."""
    stated_unknown = minimal()
    stated_unknown["proportionality"]["effect_on_people"] = {"value": "unknown", "basis": "assumed"}
    assert "needs basis `unknown`" in errors(stated_unknown)
    unknown_basis = minimal()
    unknown_basis["proportionality"]["effect_on_people"] = {"value": "acts", "basis": "unknown"}
    assert "needs basis `unknown`" in errors(unknown_basis)


def test_out_of_vocabulary_values_are_refused() -> None:
    """Why: proportion rules key on these values; a new word would match no rule."""
    data = minimal()
    data["proportionality"]["who_uses"]["value"] = ["everyone"]
    assert "who_uses" in errors(data)


def test_repeated_values_and_hypothesis_ids_are_refused() -> None:
    """Why: a repeat is a copying slip that would double-count in later rules."""
    data = minimal()
    data["proportionality"]["data_touched"]["value"] = ["personal", "personal"]
    assert "listed twice" in errors(data)
    data = minimal()
    data["hypotheses"].append(copy.deepcopy(data["hypotheses"][0]))
    assert "ids must not repeat" in errors(data)


def test_an_empty_list_is_refused_where_unknown_is_meant() -> None:
    """Why: `[]` would read as "no users" or "touches no data", a claim nobody made."""
    data = minimal()
    data["users"] = []
    assert "at least 1 item" in errors(data)


def test_an_unknown_key_is_refused() -> None:
    """Why: a typo in a field name must not become a silently ignored fact."""
    data = minimal()
    data["budget"]["build_aud"] = 10
    assert "Extra inputs are not permitted" in errors(data)


def test_load_profile_fails_loudly_with_the_file_and_field(tmp_path: Path) -> None:
    """Why: the person fixing a profile needs the file and the first bad field in one line."""
    data = minimal()
    data["budget"]["build_usd"] = -1
    path = tmp_path / "profile.yaml"
    path.write_text(yaml.safe_dump(data))
    with pytest.raises(KilnError) as caught:
        load_profile(path)
    line = caught.value.one_line()
    assert "budget.build_usd" in line
    assert str(path) in line
