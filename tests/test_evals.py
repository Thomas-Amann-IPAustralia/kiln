from __future__ import annotations

import copy
import shutil
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from kiln import evals, recordfile, records
from kiln.errors import KilnError
from kiln.evals import (
    BaselineProtocol,
    Comparison,
    Family,
    GoldenQuestion,
    GoldenSet,
    PathResult,
    Verification,
    decide,
)

REPO = Path(__file__).resolve().parent.parent
GOLDEN = REPO / evals.GOLDEN_DIR / "researcher-first-slice.md"
PROTOCOL = REPO / evals.BASELINE_DIR / "council-vs-single-session.md"
BRIEF = "evals/sample-briefs/public-form-service.yaml"
HASH = "sha256:" + "0" * 64


def verified() -> dict[str, Any]:
    return {
        "status": "verified",
        "basis": "observed",
        "checked_on": "2026-01-02",
        "by": "build_session",
        "evidence": [
            {
                "url": "https://example.org/placeholder",
                "retrieved_on": "2026-01-02",
                "sha256": HASH,
                "locator": "Placeholder section",
                "quote": "Placeholder words.",
            }
        ],
    }


def question(**changes: Any) -> dict[str, Any]:
    """A valid lookup question with a verified key. Each test below breaks one thing."""
    data: dict[str, Any] = {
        "id": "golden:placeholder-one",
        "family": "currency",
        "mode": "lookup",
        "asked_by": "solution_architect",
        "question": "Placeholder question?",
        "key": {
            "answer": "Placeholder answer.",
            "points": ["Placeholder point."],
            "sources": [
                {
                    "publisher": "Placeholder publisher",
                    "title": "Placeholder title",
                    "url": "https://example.org/placeholder",
                }
            ],
        },
        "verification": verified(),
    }
    data.update(changes)
    return data


def golden(**changes: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "version": 1,
        "set": "placeholder-set",
        "title": "Placeholder set",
        "for_agent": "researcher",
        "purpose": "Placeholder purpose.",
        "drafted_by": "build_session",
        "drafted_on": "2026-01-02",
        "covers": ["currency"],
        "pass_rule": {
            "reverify_within_days": 30,
            "question_passes_when": ["Placeholder criterion."],
            "hard_rules": ["Placeholder rule."],
            "min_passed": 1,
        },
        "questions": [question()],
    }
    data.update(changes)
    return data


def protocol(**changes: Any) -> dict[str, Any]:
    """A valid protocol over one brief, with two runs, so two comparisons."""
    data: dict[str, Any] = {
        "version": 1,
        "protocol": "placeholder-protocol",
        "title": "Placeholder protocol",
        "adr": "ADR-0029",
        "drafted_by": "build_session",
        "drafted_on": "2026-01-02",
        "question": "Placeholder question?",
        "paths": [
            {"id": "council", "name": "Council", "runs": "Placeholder."},
            {"id": "single-session", "name": "Session", "runs": "Placeholder."},
        ],
        "held_equal": ["Placeholder."],
        "runs_per_brief": 2,
        "order": "Placeholder.",
        "briefs": [{"brief": BRIEF, "points": ["One.", "Two.", "Three.", "Four."]}],
        "measures": [
            {"id": "floor-a", "kind": "floor", "what": "W.", "how": "H."},
            {"id": "floor-b", "kind": "floor", "what": "W.", "how": "H."},
            {"id": "points", "kind": "quality", "what": "W.", "how": "H."},
            {"id": "usd", "kind": "cost", "what": "W.", "how": "H."},
            {"id": "minutes", "kind": "time", "what": "W.", "how": "H."},
        ],
        "judge": {"who": "W.", "blinding": "B.", "checked_by": "C."},
        "thresholds": {
            "quality_margin": 0.25,
            "pairwise_min_wins": 1,
            "pairwise_max_losses": 0,
            "cost_ratio_max": 2.0,
            "time_ratio_max": 2.0,
        },
        "if_not_won": "Placeholder.",
        "precision": "Placeholder.",
        "budget": "Placeholder.",
        "deviations": "Placeholder.",
    }
    data.update(changes)
    return data


def rejected(model: type[Any], data: dict[str, Any]) -> str:
    with pytest.raises(ValidationError) as caught:
        model.model_validate(data)
    return str(caught.value)


def write_golden(root: Path, data: dict[str, Any]) -> Path:
    path = root / evals.GOLDEN_DIR / f"{data['set']}.md"
    recordfile.write_atomic(path, evals.golden_text(GoldenSet.model_validate(data)))
    return path


def write_protocol(root: Path, data: dict[str, Any]) -> Path:
    path = root / evals.BASELINE_DIR / f"{data['protocol']}.md"
    recordfile.write_atomic(path, evals.protocol_text(BaselineProtocol.model_validate(data)))
    return path


def problems(root: Path) -> list[str]:
    return [error.one_line() for error in evals.check_evals(root)]


# The drafted sets.


def test_the_researcher_set_has_20_questions_covering_the_charters_families() -> None:
    """Why: slice 9's draft is what Tom approves; the charter asks for 20 questions covering
    citation support, currency, supersession, jurisdiction and an injected page."""
    golden_set = evals.load_golden(GOLDEN, item=str(GOLDEN))
    assert len(golden_set.questions) == 20
    assert golden_set.for_agent.value == "researcher"
    families = {q.family for q in golden_set.questions}
    assert {
        Family.CITATION,
        Family.CURRENCY,
        Family.SUPERSESSION,
        Family.JURISDICTION,
        Family.INJECTION,
    } <= families
    assert set(golden_set.covers) == {
        Family.CITATION,
        Family.CURRENCY,
        Family.SUPERSESSION,
        Family.JURISDICTION,
        Family.INJECTION,
    }


def test_the_set_starts_with_the_charters_own_dated_claims() -> None:
    """Why: D-005 R6 makes the charter's dated claims the first golden questions, so the
    Researcher's first test is to verify them."""
    golden_set = evals.load_golden(GOLDEN, item=str(GOLDEN))
    seeded = [q for q in golden_set.questions if q.seeded_from is not None]
    assert golden_set.questions[: len(seeded)] == seeded
    assert len(seeded) >= 8
    assert all(q.seeded_from.path.startswith("docs/charter/") for q in seeded if q.seeded_from)


def test_every_unverified_key_states_its_unknowns_and_why() -> None:
    """Why: a key nobody checked must never pass as golden; the six that could not be reached
    keep `unknown` and the reason, so the set reads as not ready to run."""
    golden_set = evals.load_golden(GOLDEN, item=str(GOLDEN))
    assert [q.id for q in golden_set.unverified] == [
        "golden:dta-ai-policy-mandatory",
        "golden:cloud-policy-effective",
        "golden:essential-eight-ml2",
        "golden:agentic-ai-addendum",
        "golden:digital-experience-standards",
        "golden:ai-policy-v1-superseded",
    ]
    for q in golden_set.unverified:
        assert q.key.answer == "unknown"
        assert q.verification.reason
    assert "**Not ready to run.** 6 keys not yet verified" in GOLDEN.read_text(encoding="utf-8")


def test_the_injected_page_is_synthetic_and_names_only_an_unresolvable_host() -> None:
    """Why: the injection question's page must test injection without pointing an agent at a
    host anyone could own; `.invalid` never resolves (RFC 2606)."""
    golden_set = evals.load_golden(GOLDEN, item=str(GOLDEN))
    (injected,) = [q for q in golden_set.questions if q.family is Family.INJECTION]
    assert injected.context is not None
    page = (REPO / injected.context.path).read_text(encoding="utf-8")
    assert "SYNTHETIC" in page
    assert "collector.example.invalid" in page
    assert "collector.example.invalid" in injected.key.flag_if_says


def test_the_protocol_compares_the_three_sample_briefs() -> None:
    """Why: ADR-0029 names the three sample briefs; a protocol over others would test
    something Tom did not decide."""
    protocol_record = evals.load_protocol(PROTOCOL, item=str(PROTOCOL))
    briefs = sorted(entry.brief for entry in protocol_record.briefs)
    assert briefs == sorted(
        str(path.relative_to(REPO)) for path in (REPO / "evals/sample-briefs").glob("*.yaml")
    )
    assert protocol_record.adr == "ADR-0029"


def test_the_repos_eval_records_have_no_problems() -> None:
    """Why: CI must prove the drafted sets valid, rendered and pointing at what they test."""
    assert problems(REPO) == []


# Keys and their checks.


def test_the_placeholder_set_is_valid() -> None:
    """Why: every rejection below must fail for its own reason and no other."""
    GoldenSet.model_validate(golden())
    BaselineProtocol.model_validate(protocol())


def test_a_verified_key_needs_observed_evidence() -> None:
    """Why: "verified" must mean someone read the source; a key without evidence, or on a
    weaker basis, is a guess with a label."""
    data = verified()
    data["evidence"] = []
    assert "records the evidence" in rejected(Verification, data)
    data = verified()
    data["basis"] = "supported"
    assert "basis `observed`" in rejected(Verification, data)


def test_an_unverified_key_says_why_and_claims_no_more_than_assumed() -> None:
    """Why: the reason is what the next session acts on, and an unchecked key must never read
    as observed."""
    data = {"status": "unverified", "basis": "observed", "checked_on": "2026-01-02", "by": "tom"}
    assert "never more" in rejected(Verification, data)
    data["basis"] = "assumed"
    assert "says why" in rejected(Verification, data)
    data["reason"] = "Placeholder reason."
    Verification.model_validate(data)


def test_evidence_cannot_postdate_its_check() -> None:
    """Why: a key is true as of its check; evidence from later was not what it was checked on."""
    data = verified()
    data["evidence"][0]["retrieved_on"] = "2026-01-03"
    assert "dated after the check" in rejected(Verification, data)


def test_verify_mode_needs_a_claim_and_a_verdict_and_lookup_neither() -> None:
    """Why: a verify question is graded on its verdict; without one, or with one on a lookup,
    the runner would grade the wrong thing."""
    assert "states its claim" in rejected(GoldenQuestion, question(mode="verify"))
    data = question(mode="verify", claim="Placeholder claim.")
    assert "has a verdict" in rejected(GoldenQuestion, data)
    data["key"] = {**data["key"], "verdict": "supported"}
    GoldenQuestion.model_validate(data)
    data = question()
    data["key"] = {**data["key"], "verdict": "supported"}
    assert "has a verdict" in rejected(GoldenQuestion, data)


def test_a_verified_key_states_its_answer() -> None:
    """Why: `unknown` is honest on an unverified key and a contradiction on a verified one."""
    data = question()
    data["key"] = {**data["key"], "answer": "unknown"}
    assert "not `unknown`" in rejected(GoldenQuestion, data)


def test_injection_and_escalation_questions_carry_what_they_test() -> None:
    """Why: an injection question without its page, or an escalation question without the
    expert to route to, cannot test what its family promises."""
    assert "hands the agent the page" in rejected(GoldenQuestion, question(family="injection"))
    assert "names the expert" in rejected(GoldenQuestion, question(family="escalation"))
    data = question()
    data["key"] = {**data["key"], "escalate_to": "solution_architect"}
    assert "expert who asked it" in rejected(GoldenQuestion, data)


def test_a_set_covers_what_it_promises() -> None:
    """Why: the charter names the families the first slice must cover; a set that drops one
    must fail before Tom approves it."""
    assert "no question covers injection" in rejected(
        GoldenSet, golden(covers=["currency", "injection"])
    )


def test_a_set_rejects_repeats_impossible_rules_and_self_questions() -> None:
    """Why: a repeated id grades one question twice; a pass mark above the count can never be
    met; an agent asking itself tests nothing."""
    assert "share an id" in rejected(GoldenSet, golden(questions=[question(), question()]))
    rule = {**golden()["pass_rule"], "min_passed": 2}
    assert "more passes" in rejected(GoldenSet, golden(pass_rule=rule))
    assert "own questions" in rejected(
        GoldenSet, golden(questions=[question(asked_by="researcher")])
    )
    assert "not by him" in rejected(GoldenSet, golden(drafted_by="tom"))


# The records check.


def make_root(tmp_path: Path) -> Path:
    """A repo with one charter sentence, the one brief, and a valid set seeded from it."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/claim.md").write_text(
        "Placeholder line one.\nThe placeholder rule\ncommences on a placeholder date.\n",
        encoding="utf-8",
    )
    (tmp_path / "evals/sample-briefs").mkdir(parents=True)
    shutil.copy(REPO / BRIEF, tmp_path / BRIEF)
    return tmp_path


def seeded_set() -> dict[str, Any]:
    seed = {
        "path": "docs/claim.md",
        "quote": "The placeholder rule commences on a placeholder date.",
    }
    return golden(questions=[question(seeded_from=seed)])


def test_a_seed_still_standing_passes_across_line_breaks(tmp_path: Path) -> None:
    """Why: the quote is matched ignoring line breaks, which a re-wrapped file moves."""
    root = make_root(tmp_path)
    write_golden(root, seeded_set())
    assert problems(root) == []


def test_a_seed_changed_under_its_question_is_caught(tmp_path: Path) -> None:
    """Why: if the charter's claim changes, the question testing it tests the old claim; the
    check sends it back for redrafting rather than letting it drift."""
    root = make_root(tmp_path)
    write_golden(root, seeded_set())
    (root / "docs/claim.md").write_text("The placeholder rule moved.\n", encoding="utf-8")
    assert any("no longer stands" in line for line in problems(root))


def test_a_missing_context_page_is_caught(tmp_path: Path) -> None:
    """Why: an injection question whose page is gone would be run without the injection."""
    root = make_root(tmp_path)
    context = {"path": "evals/pages/gone.html", "delivered_as": "fetched", "note": "N."}
    write_golden(root, golden(questions=[question(family="currency", context=context)]))
    assert any("context evals/pages/gone.html is missing" in line for line in problems(root))


def test_a_hand_edited_body_or_a_wrong_name_is_caught(tmp_path: Path) -> None:
    """Why: Tom reads the body and the runner reads the front matter; they must not disagree,
    and the file's name is how a card finds it."""
    root = make_root(tmp_path)
    path = write_golden(root, golden())
    path.write_text(path.read_text(encoding="utf-8") + "An extra line.\n", encoding="utf-8")
    assert any("not its record's rendering" in line for line in problems(root))
    path.unlink()
    recordfile.write_atomic(
        root / evals.GOLDEN_DIR / "other-name.md",
        evals.golden_text(GoldenSet.model_validate(golden())),
    )
    assert any("file name should be placeholder-set.md" in line for line in problems(root))


def test_a_protocol_whose_brief_no_longer_validates_is_caught(tmp_path: Path) -> None:
    """Why: the comparison runs on the briefs as profiles; one that stopped validating would
    fail at the first run instead of now."""
    root = make_root(tmp_path)
    write_protocol(root, protocol())
    assert problems(root) == []
    (root / BRIEF).write_text("version: 1\n", encoding="utf-8")
    assert any(f"brief {BRIEF}" in line for line in problems(root))


def test_render_turns_front_matter_into_the_canonical_file(tmp_path: Path) -> None:
    """Why: drafts are written as front matter and rendered; the render must be the file the
    check accepts, and a second render must change nothing."""
    root = make_root(tmp_path)
    path = root / evals.BASELINE_DIR / "placeholder-protocol.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        recordfile.FENCE
        + recordfile.front_matter(BaselineProtocol.model_validate(protocol()))
        + recordfile.FENCE,
        encoding="utf-8",
    )
    assert evals.render_evals(root) == [evals.BASELINE_DIR / "placeholder-protocol.md"]
    assert problems(root) == []
    assert evals.render_evals(root) == []


def test_the_records_check_reports_eval_problems(tmp_path: Path) -> None:
    """Why: `kiln records check` is what CI and the pre-commit hook run, so an eval problem
    must reach it."""
    root = make_root(tmp_path)
    write_golden(root, seeded_set())
    (root / "docs/claim.md").write_text("Changed.\n", encoding="utf-8")
    assert any("no longer stands" in p.message for p in records.check_evals(root))


# The protocol and its rule.


def test_a_protocol_has_the_two_paths_and_every_kind_of_measure() -> None:
    """Why: ADR-0029 compares these two paths on quality, cost and time; a protocol missing a
    path or an axis decides something else."""
    data = protocol()
    data["paths"] = [data["paths"][0], {**data["paths"][1], "id": "council"}]
    assert "`council` and `single-session`" in rejected(BaselineProtocol, data)
    data = protocol()
    data["measures"] = [m for m in data["measures"] if m["kind"] != "cost"]
    assert "no ['cost'] measure" in rejected(BaselineProtocol, data)


def test_a_protocol_rejects_pairwise_thresholds_it_cannot_meet() -> None:
    """Why: a rule that needs more comparisons than the design makes can never be won, which
    would quietly decide the result in advance."""
    thresholds = {**protocol()["thresholds"], "pairwise_min_wins": 3}
    assert "more than 2 comparisons" in rejected(BaselineProtocol, protocol(thresholds=thresholds))


def result(
    *, failed: tuple[str, ...] = (), points: float, usd: float, minutes: float
) -> PathResult:
    return PathResult(floors_failed=list(failed), points_covered=points, usd=usd, minutes=minutes)


def winning() -> list[Comparison]:
    """Two runs of the one brief where the Council's path wins on every criterion."""
    council = result(points=4, usd=2.0, minutes=60)
    single = result(points=2, usd=1.0, minutes=40)
    return [
        Comparison(brief=BRIEF, council=council, single_session=single, preferred="council"),
        Comparison(brief=BRIEF, council=council, single_session=single, preferred="neither"),
    ]


def the_protocol() -> BaselineProtocol:
    return BaselineProtocol.model_validate(protocol())


def test_the_council_wins_only_when_every_criterion_holds() -> None:
    """Why: the rule is a conjunction; this is the case where it is met, so each test below
    can break one criterion and see the decision flip."""
    decision = decide(the_protocol(), winning())
    assert decision.council_wins
    assert [c.met for c in decision.criteria] == [True] * 5


@pytest.mark.parametrize(
    ("change", "criterion"),
    [
        ({"council": result(failed=("floor-a",), points=4, usd=2.0, minutes=60)}, "Floors"),
        ({"council": result(points=1, usd=2.0, minutes=60)}, "Points covered"),
        ({"preferred": "single-session"}, "Pairwise preference"),
        ({"council": result(points=4, usd=2.1, minutes=60)}, "Cost"),
        ({"council": result(points=4, usd=2.0, minutes=101)}, "Time"),
    ],
)
def test_breaking_one_criterion_loses(change: dict[str, Any], criterion: str) -> None:
    """Why: each criterion must be able to decide the result on its own; a criterion that
    cannot fail is not part of the rule."""
    comparisons = winning()
    comparisons[1] = comparisons[1].model_copy(update=change)
    decision = decide(the_protocol(), comparisons)
    assert not decision.council_wins
    assert [c.name for c in decision.criteria if not c.met] == [criterion]


def test_a_floor_both_paths_fail_is_not_held_against_the_council() -> None:
    """Why: the floor criterion asks whether the Council does worse than the baseline, not
    whether the task was easy; a floor neither passed shows in the quality grades."""
    comparisons = winning()
    both = ("floor-b",)
    comparisons[0] = comparisons[0].model_copy(
        update={
            "council": result(failed=both, points=4, usd=2.0, minutes=60),
            "single_session": result(failed=both, points=2, usd=1.0, minutes=40),
        }
    )
    assert decide(the_protocol(), comparisons).council_wins


def test_a_margin_met_exactly_counts() -> None:
    """Why: "at least" must mean at least; float rounding must not turn an exact tie with the
    margin into a loss."""
    comparisons = winning()
    comparisons[1] = comparisons[1].model_copy(
        update={"council": result(points=2, usd=1.0, minutes=40)}
    )
    decision = decide(the_protocol(), comparisons)
    assert decision.criteria[1].met
    assert decision.criteria[3].met and decision.criteria[4].met


def test_decide_refuses_results_that_do_not_match_the_design() -> None:
    """Why: a missing run, a made-up floor or an impossible score would let the rule decide
    on the wrong evidence; it must fail loudly instead."""
    with pytest.raises(KilnError, match="comparison"):
        decide(the_protocol(), winning()[:1])
    bad = copy.deepcopy(winning())
    bad[0] = bad[0].model_copy(
        update={"council": result(failed=("not-a-floor",), points=4, usd=2.0, minutes=60)}
    )
    with pytest.raises(KilnError, match="not floor measures"):
        decide(the_protocol(), bad)
    bad = winning()
    bad[0] = bad[0].model_copy(update={"council": result(points=5, usd=2.0, minutes=60)})
    with pytest.raises(KilnError, match="more points"):
        decide(the_protocol(), bad)


def test_the_rendered_rule_states_the_thresholds() -> None:
    """Why: Tom approves the rule by reading it; the sentences must come from the numbers the
    code applies, never be written beside them."""
    text = evals.render_protocol(the_protocol())
    assert "by at least 25% of the points" in text
    assert "at least 1 of the 2 comparisons, and never prefers the single session" in text
    assert "at most 2 times the single session's" in text
