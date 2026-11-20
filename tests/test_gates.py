"""The gates, G0 to G5, on fixture artefacts in throwaway git repositories.

`walk` takes the public form service sample brief through every gate the way the thin path
will: work on a branch, a decision card for each of Tom's gates, Tom's merge, and at G3 a loop's
commit that the verifier passes.
"""

from __future__ import annotations

import copy
import os
from datetime import date
from pathlib import Path
from typing import Any

import pytest
import yaml
from langgraph.checkpoint.memory import InMemorySaver
from langsmith import utils as langsmith_utils
from pydantic import ValidationError
from typer.testing import CliRunner

from kiln import gates
from kiln.artefacts import BuildRecord
from kiln.cards import DecisionCard, card_text
from kiln.cli import app
from kiln.gates import GateMachine, GateOutcome, GateStatus, Workspace, run_gates, validate
from kiln.ids import content_hash
from kiln.verifier import verify, write_record
from kiln.vocabulary import Gate
from tests.gitrepo import Repo
from tests.solution import (
    FITNESS,
    GREETING,
    RIGHT,
    ticket,
    ticket_list,
    write_build_contract,
    write_tickets,
)

SAMPLE = Path(__file__).resolve().parent.parent / "evals/sample-briefs/public-form-service.yaml"
EVIDENCE = content_hash(b"placeholder evidence")


def profile(**changes: Any) -> dict[str, Any]:
    data: dict[str, Any] = yaml.safe_load(SAMPLE.read_text())
    data.update(changes)
    return data


def with_all_measures() -> dict[str, Any]:
    data = profile()
    for hypothesis in data["hypotheses"]:
        if hypothesis["measure"] == "unknown":
            hypothesis["measure"] = "Placeholder measure."
    data["budget"]["run_usd_per_month"] = 20
    return data


APPLICABILITY: dict[str, Any] = {
    "version": 1,
    "triggered_experts": ["solution_architect", "governance_guru", "ux_designer"],
    "obligations": [
        {
            "id": "OBL-0001",
            "title": "Placeholder obligation",
            "source": "policy:placeholder",
            "owner": "governance_guru",
        },
    ],
}
PLAN: dict[str, Any] = {
    "version": 1,
    "consulted_experts": ["solution_architect", "governance_guru", "ux_designer"],
    "contracts": [{"id": "ux", "owner": "ux_designer", "path": "council/contracts/ux.yaml"}],
    "review": {
        "reviewer": "placeholder-model",
        "findings": [
            {
                "id": "FND-0001",
                "severity": "medium",
                "summary": "Placeholder.",
                "owner": "ux_designer",
                "response": "accepted",
                "reason": "Placeholder.",
            }
        ],
    },
    "estimate": {"build_usd": 20, "run_usd_per_month": 10},
    "packet": "council/g2-packet.md",
}
PRE_RELEASE: dict[str, Any] = {
    "version": 1,
    "findings": [{"id": "FND-0002", "severity": "high", "status": "fixed"}],
    "obligations": [{"id": "OBL-0001", "status": "met", "evidence": [EVIDENCE]}],
    "assurance_case": "council/assurance-case.md",
    "test_plan": "council/test-plan.md",
}
REAL_WORLD_TEST: dict[str, Any] = {
    "version": 1,
    "results": [
        {"hypothesis": h, "finding": "supported", "evidence": [EVIDENCE], "summary": "Placeholder."}
        for h in ("H1", "H2", "H3")
    ],
}


class Solution(Repo):
    """A solution repository with a `council/` folder."""

    def put(self, name: str, data: dict[str, Any]) -> None:
        self.write(f"council/{name}", yaml.safe_dump(data, sort_keys=False))

    def gate_card(
        self, number: int, gate: Gate, rests_on: list[str], choice: str | None = "Approve"
    ) -> DecisionCard:
        """A card putting `gate` to Tom, resting on files as they are now, maybe answered."""
        card = DecisionCard.model_validate(
            {
                "id": f"CARD-{number:04d}",
                "title": f"Pass {gate.value}",
                "put_by": "solution_architect",
                "put_on": date(2026, 11, 18),
                "question": f"Pass {gate.value}?",
                "options": [
                    {"label": "Approve", "consequences": "Placeholder: the solution moves on."},
                    {"label": "Decline", "consequences": "Placeholder: it does not."},
                ],
                "recommendation": {"option": "Approve", "reason": "Placeholder."},
                "undo": {"possible": True, "how": "Placeholder."},
                "if_no_answer": "Placeholder: nothing moves.",
                "rests_on": [
                    {"path": p, "sha256": content_hash((self.root / p).read_bytes())}
                    for p in rests_on
                ],
                "gate": {"gate": gate.value, "pass_option": "Approve"},
                "answer": None
                if choice is None
                else {"choice": choice, "words": "Placeholder.", "answered_on": date(2026, 11, 18)},
            }
        )
        self.write(f"council/cards/{card.file_name}", card_text(card))
        return card

    def merged(self, branch: str) -> None:
        """Commit the working tree on `branch` and merge it the way Tom does."""
        self.git("checkout", "--quiet", "-b", branch)
        self.commit(branch)
        self.git("checkout", "--quiet", "main")
        self.git("merge", "--quiet", "--no-ff", "-m", f"Merge {branch}", branch)

    def run(self) -> list[GateOutcome]:
        return run_gates(self.root, ref="main")

    def loop_and_verify(self) -> BuildRecord:
        """A loop's commit on its own branch, and the verifier's record of it, uncommitted."""
        self.git("checkout", "--quiet", "-b", "loop")
        self.write(GREETING, RIGHT)
        self.commit("the loop greets by name")
        record = verify(self.root, "HEAD", environment=ENVIRONMENT, ref="main", today=TODAY)
        write_record(self.root, record)
        return record

    def statuses(self) -> list[tuple[str, str]]:
        return [(o.gate.value, o.status.value) for o in self.run()]


G2_FILES = [
    "council/profile.yaml",
    "council/plan.yaml",
    "council/tickets.json",
    "council/g2-packet.md",
    "council/contracts/ux.yaml",
]
ENVIRONMENT = {"PATH": os.environ.get("PATH", "")}
TODAY = date(2026, 11, 20)
G4_FILES = ["council/pre-release.yaml", "council/assurance-case.md", "council/test-plan.md"]


def through_g0(repo: Solution) -> None:
    repo.put("profile.yaml", profile())
    repo.gate_card(1, Gate.G0, ["council/profile.yaml"])
    repo.merged("g0")


def through_g2(repo: Solution) -> None:
    through_g0(repo)
    g2_part(repo)


def g2_part(repo: Solution) -> None:
    repo.put("profile.yaml", with_all_measures())
    repo.put("applicability.yaml", APPLICABILITY)
    repo.put("plan.yaml", PLAN)
    write_build_contract(repo, ticket_list())
    repo.write("council/g2-packet.md", "# Placeholder G2 packet\n")
    repo.write("council/contracts/ux.yaml", "placeholder: true\n")
    repo.gate_card(2, Gate.G2, G2_FILES)
    repo.merged("g2")


def through_g5(repo: Solution) -> None:
    through_g2(repo)
    through_g5_rest(repo)


@pytest.fixture
def repo(tmp_path: Path) -> Solution:
    return Solution(tmp_path)


def test_a_sample_brief_walks_g0_to_g5(repo: Solution) -> None:
    """Why: slice 2's own check; the thin path runs on exactly this walk."""
    through_g0(repo)
    assert repo.statuses() == [("G0", "passed"), ("G1", "incomplete")]
    g2_part(repo)
    run = repo.run()
    assert [o.status for o in run][:3] == [GateStatus.PASSED] * 3
    assert run[0].approved_by == "CARD-0002", "Tom's G2 approval covers the edited profile"
    assert run[3].status is GateStatus.INCOMPLETE
    through_g5_rest(repo)
    final = repo.run()
    assert [o.status for o in final] == [GateStatus.PASSED] * 6
    assert [o.approved_by for o in final] == [
        "CARD-0002",
        None,
        "CARD-0002",
        None,
        "CARD-0003",
        "CARD-0004",
    ]


def through_g3(repo: Solution) -> None:
    """The loop's branch, with the verifier's record committed on it, merged by Tom."""
    repo.loop_and_verify()
    repo.commit("the verifier's record")
    repo.merge("loop")


def through_g5_rest(repo: Solution) -> None:
    through_g3(repo)
    repo.put("pre-release.yaml", PRE_RELEASE)
    repo.write("council/assurance-case.md", "# Placeholder assurance case\n")
    repo.write("council/test-plan.md", "# Placeholder test plan\n")
    repo.gate_card(3, Gate.G4, G4_FILES)
    repo.merged("g4")
    repo.put("real-world-test.yaml", REAL_WORLD_TEST)
    repo.gate_card(4, Gate.G5, ["council/real-world-test.yaml"])
    repo.merged("g5")


def test_a_missing_artefact_fails_its_gate_and_stops_the_run(repo: Solution) -> None:
    """Why: a gate passes on what exists, never on what is promised."""
    through_g5(repo)
    (repo.root / "council/applicability.yaml").unlink()
    run = repo.run()
    assert [(o.gate.value, o.status) for o in run][1:] == [("G1", GateStatus.INCOMPLETE)]
    assert run[1].problems == ["council/applicability.yaml does not exist yet"]


def test_a_plan_edited_after_approval_fails_g2(repo: Solution) -> None:
    """Why: slice 2's check; a change to what Tom approved goes back to him (Tom band)."""
    through_g2(repo)
    plan = copy.deepcopy(PLAN)
    plan["estimate"]["build_usd"] = 21
    repo.put("plan.yaml", plan)
    run = repo.run()
    assert run[2].status is GateStatus.FAILED
    assert "changed since Tom approved it: council/plan.yaml" in run[2].problems[0]
    repo.merged("edit-plan")
    run = repo.run()
    assert [o.status for o in run[:2]] == [GateStatus.PASSED] * 2, (
        "the lapsed G2 card still approves the profile, which did not change"
    )
    merged = run[2]
    assert merged.status is GateStatus.FAILED
    assert "council/plan.yaml, which it rests on, changed after its approval" in merged.problems[0]


def test_a_superseding_card_puts_an_edited_plan_back_through(repo: Solution) -> None:
    """Why: the right way to change an approved plan must work, not only the wrong way fail."""
    through_g2(repo)
    plan = copy.deepcopy(PLAN)
    plan["estimate"]["build_usd"] = 21
    repo.put("plan.yaml", plan)
    card = repo.gate_card(3, Gate.G2, G2_FILES)
    path = repo.root / "council/cards" / card.file_name
    superseding = card.model_copy(update={"supersedes": "CARD-0002"})
    path.write_text(card_text(superseding))
    assert repo.run()[2].status is GateStatus.AWAITING_TOM
    repo.merged("revise-plan")
    assert repo.run()[2].approved_by == "CARD-0003"


def test_a_pass_written_from_outside_the_validation_node_is_refused(repo: Solution) -> None:
    """Why: slice 2's check. Only a gate's validation can pass it; a pass injected into the
    run's state, here through LangGraph's own `update_state`, must not move the solution on."""
    through_g0(repo)
    machine = GateMachine(lambda: Workspace(repo.root, ref="main"), InMemorySaver())
    run = machine.run("t1")
    assert [o.status for o in run] == [GateStatus.PASSED, GateStatus.INCOMPLETE]
    forged = GateOutcome(gate=Gate.G1, status=GateStatus.PASSED).model_dump(mode="json")
    config: Any = {"configurable": {"thread_id": "t1"}}
    machine.graph.update_state(config, {"outcomes": [forged]}, as_node="G1")
    resumed = machine.resume("t1")
    refusal = resumed[-1]
    assert refusal.gate is Gate.G1
    assert refusal.status is GateStatus.FAILED
    assert refusal.problems[0].startswith("refused a pass recorded for G1")
    assert not any(o.gate is Gate.G2 for o in resumed)


def test_a_pass_for_files_that_have_changed_is_refused(repo: Solution) -> None:
    """Why: a pass is only for the exact files it names; a stale one is no pass at all."""
    through_g2(repo)
    machine = GateMachine(lambda: Workspace(repo.root, ref="main"), InMemorySaver())
    machine.run("t2")
    real = validate(Gate.G1, Workspace(repo.root, ref="main"))
    stale = real.model_copy(update={"artefacts": {"council/applicability.yaml": EVIDENCE}})
    config: Any = {"configurable": {"thread_id": "t2"}}
    machine.graph.update_state(config, {"outcomes": [stale.model_dump(mode="json")]}, as_node="G1")
    assert machine.resume("t2")[-1].problems[0].startswith("refused a pass recorded for G1")


@pytest.mark.parametrize(
    ("choice", "status", "problem"),
    [
        (None, GateStatus.AWAITING_TOM, "CARD-0001 awaits his answer"),
        ("Decline", GateStatus.FAILED, "Tom answered 'Decline' in CARD-0001"),
    ],
)
def test_tom_gates_wait_for_his_answer_and_respect_a_no(
    repo: Solution, choice: str | None, status: GateStatus, problem: str
) -> None:
    """Why: G0, G2, G4 and G5 are Tom's; a question merged or a "no" answered is not a pass."""
    repo.put("profile.yaml", profile())
    repo.gate_card(1, Gate.G0, ["council/profile.yaml"], choice=choice)
    repo.merged("g0")
    assert repo.run()[0].problems == [problem]
    assert repo.run()[0].status is status


def test_an_answer_not_yet_merged_awaits_toms_merge(repo: Solution) -> None:
    """Why: an agent can write Tom's answer, but only his merge puts it into effect."""
    repo.put("profile.yaml", profile())
    repo.gate_card(1, Gate.G0, ["council/profile.yaml"])
    assert repo.run()[0].problems == ["CARD-0001 awaits his merge"]


def test_a_card_edited_after_approval_approves_nothing(repo: Solution) -> None:
    """Why: an edited card may no longer hold Tom's words; it cannot pass any gate."""
    through_g0(repo)
    card_file = next((repo.root / "council/cards").glob("CARD-0001-*.md"))
    card_file.write_text(card_file.read_text().replace("words: Placeholder.", "words: Edited."))
    repo.merged("edit-card")
    outcome = repo.run()[0]
    assert outcome.status is GateStatus.FAILED
    assert "the card was edited after its approval" in outcome.problems[0]


def test_with_no_card_the_gate_says_what_tom_must_approve(repo: Solution) -> None:
    """Why: the next step for whoever reads the run is to write that card."""
    repo.put("profile.yaml", profile())
    outcome = repo.run()[0]
    assert outcome.status is GateStatus.AWAITING_TOM
    assert outcome.problems == ["no card puts G0 to Tom; write one resting on council/profile.yaml"]


def failing(repo: Solution, gate: Gate) -> list[str]:
    outcome = validate(gate, Workspace(repo.root, ref="main"))
    assert outcome.status is GateStatus.FAILED, outcome
    return outcome.problems


def test_g0_needs_hypotheses_covering_dvf(repo: Solution) -> None:
    """Why: nothing reaches production unproved on all three; each needs a hypothesis."""
    data = profile()
    data["hypotheses"] = [h for h in data["hypotheses"] if h["dimension"] != "viability"]
    repo.put("profile.yaml", data)
    assert failing(repo, Gate.G0) == ["no hypothesis tests viability"]


def test_g2_runs_the_charters_hard_checks(repo: Solution) -> None:
    """Why: these are the checks G2 must pass before Tom reads the packet (charter)."""
    repo.put("profile.yaml", profile())
    repo.put("applicability.yaml", APPLICABILITY)
    plan = copy.deepcopy(PLAN)
    plan["consulted_experts"] = ["solution_architect", "ux_designer"]
    plan["estimate"]["build_usd"] = 26
    repo.put("plan.yaml", plan)
    write_tickets(repo, ticket_list(tickets=[ticket(1) | {"contract": "elsewhere"}]))
    repo.write("council/g2-packet.md", "  \n")
    repo.write("council/contracts/ux.yaml", "placeholder: true\n")
    assert failing(repo, Gate.G2) == [
        "governance_guru was triggered at G1 but not consulted",
        "H2 has no measure",
        "the build cost, $26.00, is over its budget, $25.00",
        "the monthly running budget is unknown, so the cost cannot be checked",
        "TKT-0001 traces to 'elsewhere', which is not a contract in the plan",
        "the G2 packet (council/g2-packet.md) is empty",
    ]


def test_toms_g2_approval_covers_the_verification_steps(repo: Solution) -> None:
    """Why: the steps decide what "done" means for a loop; they are part of the plan Tom
    approves, and an edit to them goes back to him."""
    through_g2(repo)
    write_tickets(repo, ticket_list(tickets=[ticket(1), ticket(2)]))
    run = repo.run()
    assert run[2].status is GateStatus.FAILED
    assert "changed since Tom approved it: council/tickets.json" in run[2].problems[0]


def test_g3_passes_on_the_verifiers_record_and_only_for_the_build_it_verified(
    repo: Solution,
) -> None:
    """Why: G3's check is "every ticket passes", and since slice 4 only the verifier's record
    can say so (ADR-0027). A pass is for one commit: code changed after it was never verified."""
    through_g2(repo)
    assert [o.status for o in repo.run()][3] is GateStatus.INCOMPLETE
    through_g3(repo)
    assert repo.run()[3].status is GateStatus.PASSED
    repo.write(GREETING, RIGHT + "# changed after the verifier ran\n")
    problems = failing(repo, Gate.G3)
    assert len(problems) == 1
    assert problems[0].startswith(
        "council/build.yaml does not hold: src/greeting.py changed after the verifier ran"
    )


def test_g3_reports_every_failure_in_the_record(repo: Solution) -> None:
    """Why: G3's checks, from the verifier's results: a ticket that does not pass, a result for
    a ticket that is not in the list, a failed check, and an open tripwire."""
    through_g2(repo)
    record = repo.loop_and_verify().model_dump(mode="json")
    record["checks"].append(
        {
            "name": "secrets",
            "run": ["placeholder-secret-scan"],
            "exit_code": 1,
            "output": "placeholder",
            "tripwire": "exposed_secret",
        }
    )
    record["tickets"][0]["passes"] = False
    record["tickets"].append({"id": "TKT-0009", "passes": False, "steps": []})
    write_record(repo.root, BuildRecord.model_validate(record))
    assert failing(repo, Gate.G3) == [
        "TKT-0001 does not pass",
        "TKT-0009 is not a ticket in tickets.json",
        "the check 'secrets' did not pass",
        "tripwire 2 (exposed_secret) is open",
    ]


def test_g3_fails_on_a_refused_commit(repo: Solution) -> None:
    """Why: a loop that changed what judges it has not built the ticket, whatever ran."""
    through_g2(repo)
    repo.git("checkout", "--quiet", "-b", "loop")
    repo.write(FITNESS, "placeholder = 'checks nothing'\n")
    repo.commit("the loop weakens the check")
    record = verify(repo.root, "HEAD", environment=ENVIRONMENT, ref="main", today=TODAY)
    write_record(repo.root, record)
    assert failing(repo, Gate.G3) == [
        f"the verifier refused {record.commit[:12]}: it changes {FITNESS}, which a loop may not"
    ]


def test_g3_fails_a_record_judged_against_another_ticket_list(repo: Solution) -> None:
    """Why: the record names the ticket list it ran; a list changed since may hold steps that
    never ran."""
    through_g2(repo)
    repo.loop_and_verify()
    write_tickets(repo, ticket_list(tickets=[ticket(1), ticket(2)]))
    problems = failing(repo, Gate.G3)
    assert problems[0] == (
        "the verifier judged a council/tickets.json other than the one here; run it again"
    )
    assert "TKT-0002 has no result" in problems


def test_g4_needs_serious_findings_closed_and_every_obligation_settled(repo: Solution) -> None:
    """Why: G4's checks: no open critical or high finding, every obligation met or deferred."""
    repo.put("applicability.yaml", APPLICABILITY)
    release = copy.deepcopy(PRE_RELEASE)
    release["findings"] = [{"id": "FND-0002", "severity": "critical", "status": "open"}]
    release["obligations"] = []
    repo.put("pre-release.yaml", release)
    repo.write("council/assurance-case.md", "# Placeholder\n")
    repo.write("council/test-plan.md", "# Placeholder\n")
    assert failing(repo, Gate.G4) == [
        "FND-0002 (critical) is still open",
        "OBL-0001 is neither met nor deferred",
    ]


def test_g5_needs_a_finding_for_every_hypothesis(repo: Solution) -> None:
    """Why: G5 records what the evidence supports for each hypothesis, none left out."""
    repo.put("profile.yaml", profile())
    test = copy.deepcopy(REAL_WORLD_TEST)
    test["results"] = test["results"][:2]
    repo.put("real-world-test.yaml", test)
    assert failing(repo, Gate.G5) == ["H3 has no finding from the real-world test"]


def test_an_invalid_artefact_fails_its_gate_in_one_line(repo: Solution) -> None:
    """Why: the person fixing it needs the file and the first bad field."""
    repo.write("council/profile.yaml", "version: 1\nsolution: [not, a, slug]\n")
    problems = failing(repo, Gate.G0)
    assert len(problems) == 1
    assert "council/profile.yaml" in problems[0]


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"gate": {"gate": "G1", "pass_option": "Approve"}}, "passed by a validation node"),
        ({"gate": {"gate": "G2", "pass_option": "Maybe"}}, "pass option 'Maybe'"),
    ],
)
def test_a_card_can_only_decide_one_of_toms_gates(
    repo: Solution, change: dict[str, Any], message: str
) -> None:
    """Why: G1 and G3 belong to validation nodes; a card must not claim to pass them."""
    repo.put("profile.yaml", profile())
    card = repo.gate_card(1, Gate.G0, ["council/profile.yaml"])
    with pytest.raises(ValidationError, match=message):
        DecisionCard.model_validate(card.model_dump() | change)


def tracing_enabled() -> bool:
    return bool(langsmith_utils.tracing_is_enabled())  # pyright: ignore[reportUnknownMemberType]


def forget_langsmith_env() -> None:
    """LangSmith caches what it read from the environment; make it read again."""
    langsmith_utils.get_env_var.cache_clear()  # pyright: ignore[reportFunctionMemberAccess]


def test_no_run_is_traced_through_langgraph(
    repo: Solution, monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest
) -> None:
    """Why: with LANGSMITH_TRACING set, LangGraph sent a run's state to LangSmith (D-012).
    Gate state names a solution's files; it must not leave by a tracer Kiln did not choose."""
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "true")
    forget_langsmith_env()
    request.addfinalizer(forget_langsmith_env)
    assert tracing_enabled(), "the environment asks for tracing"
    seen: list[bool] = []
    real = gates.validate

    def spy(gate: Gate, workspace: Workspace) -> GateOutcome:
        seen.append(tracing_enabled())
        return real(gate, workspace)

    monkeypatch.setattr(gates, "validate", spy)
    through_g0(repo)
    repo.run()
    assert seen and not any(seen)


def test_the_cli_reports_each_gate_and_exits_2_only_on_a_failure(repo: Solution) -> None:
    """Why: waiting for Tom or for work is normal; a failed check is something to act on."""
    runner = CliRunner()
    args = ["gates", "--ref", "main", "--root", str(repo.root)]
    through_g0(repo)
    waiting = runner.invoke(app, args)
    assert waiting.exit_code == 0, waiting.output
    assert "G0 intake: passed (CARD-0001)" in waiting.output
    assert "G1 applicability: incomplete" in waiting.output
    repo.write("council/applicability.yaml", "version: 2\n")
    failed = runner.invoke(app, args)
    assert failed.exit_code == 2
    assert "G1 applicability: failed" in failed.output


def test_the_cli_fails_loudly_without_a_council_folder(tmp_path: Path) -> None:
    """Why: run from the wrong directory, silence would read as "nothing has started"."""
    result = CliRunner().invoke(app, ["gates", "--root", str(tmp_path)])
    assert result.exit_code == 2
    assert "no council folder here" in result.output
