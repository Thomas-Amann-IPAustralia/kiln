"""The verifier: the only writer of a ticket's pass (ADR-0027).

Slice 4's own checks are the first two groups here: a commit that passes its steps gets the
pass, and one that edits a fitness function, a contract or its own verification steps is
refused, whatever its tests say. Each test builds a real git repository: `main` holds the build
contract as Tom merged it, and a loop works on a branch.
"""

from __future__ import annotations

import copy
import os
import time
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError
from typer.testing import CliRunner

from kiln.artefacts import BuildRecord, parse_yaml
from kiln.cli import app
from kiln.config import load_config
from kiln.errors import KilnError
from kiln.ids import content_hash
from kiln.verifier import (
    RECORD_HEADER,
    environment_for,
    recheck,
    verify,
    write_record,
)
from kiln.vocabulary import Tripwire
from tests.gitrepo import Repo
from tests.solution import (
    COMPILES,
    FITNESS,
    GREETING,
    PYTHON,
    RIGHT,
    STEP,
    WRONG,
    marks,
    ticket,
    ticket_list,
    write_build_contract,
    write_plan,
    write_tickets,
)

TODAY = date(2026, 11, 20)
ENVIRONMENT = {"PATH": os.environ.get("PATH", "")}
REPO_CONFIG = Path(__file__).resolve().parent.parent / "config/kiln.yaml"

PLAN: dict[str, Any] = {
    "version": 1,
    "consulted_experts": ["solution_architect", "ux_designer"],
    "contracts": [
        {"id": "ux", "owner": "ux_designer", "path": "council/contracts/ux.yaml"},
        {"id": "api", "owner": "solution_architect", "path": "docs/api.yaml"},
    ],
    "review": {"reviewer": "placeholder-model", "findings": []},
    "estimate": {"build_usd": 1, "run_usd_per_month": 1},
    "packet": "council/g2-packet.md",
}


class Solution(Repo):
    """`main` with the build contract merged; `loop` is the loop's branch."""

    def __init__(self, root: Path, tickets: dict[str, Any]) -> None:
        root.mkdir()
        super().__init__(root)
        write_plan(self, PLAN)
        self.write("council/contracts/ux.yaml", "placeholder: true\n")
        self.write("docs/api.yaml", "placeholder: true\n")
        write_build_contract(self, tickets)
        self.base = self.commit("the build contract, as Tom merged it")
        self.branch("loop")

    def verify(self, commit: str = "HEAD", **options: Any) -> BuildRecord:
        options.setdefault("environment", ENVIRONMENT)
        return verify(self.root, commit, ref="main", today=TODAY, **options)


@pytest.fixture
def marker(tmp_path: Path) -> Path:
    return tmp_path / "ran"


@pytest.fixture
def repo(tmp_path: Path, marker: Path) -> Solution:
    return Solution(tmp_path / "solution", ticket_list([COMPILES, marks(marker)]))


# A commit that passes its steps gets the pass -----------------------------------------------


def test_a_commit_that_passes_its_steps_gets_the_pass(repo: Solution, marker: Path) -> None:
    """Why: slice 4's first check. The pass comes from the verifier's own run on the commit,
    and the record names exactly what the commit was judged against."""
    repo.write(GREETING, RIGHT)
    commit = repo.commit("the loop greets by name")
    record = repo.verify()
    assert [(t.id, t.passes) for t in record.tickets] == [("TKT-0001", True)]
    assert [c.passed for c in record.checks] == [True, True]
    assert (record.commit, record.base, record.ref) == (commit, repo.base, "main")
    tickets_file = (repo.root / "council/tickets.json").read_bytes()
    assert record.tickets_sha256 == content_hash(tickets_file)
    assert record.refused == []
    assert marker.exists()


def test_a_commit_that_fails_a_step_does_not_pass_and_says_why(repo: Solution) -> None:
    """Why: a failure is useful only if the loop can read what failed; the record keeps the
    end of the step's output."""
    repo.write("src/other.py", "placeholder = 1\n")
    repo.commit("the loop changes something else")
    record = repo.verify()
    step = record.tickets[0].steps[0]
    assert not record.tickets[0].passes
    assert step.exit_code == 1
    assert step.output is not None and "AssertionError: Hello." in step.output
    assert str(repo.root) not in step.output


# One that edits what judges it is refused, whatever its tests say ---------------------------


def edit_fitness(repo: Repo) -> None:
    repo.write(FITNESS, "placeholder = 'a fitness function that checks nothing'\n")


EDITS: dict[str, tuple[Callable[[Repo], object], list[str]]] = {
    "a fitness function, weakened": (edit_fitness, [FITNESS]),
    "a fitness function, removed": (lambda r: (r.root / FITNESS).unlink(), [FITNESS]),
    "a fitness function, moved": (
        lambda r: r.git("mv", FITNESS, "src/check.py"),
        [FITNESS],
    ),
    "a contract": (
        lambda r: r.write("council/contracts/ux.yaml", "placeholder: false\n"),
        ["council/contracts/ux.yaml"],
    ),
    "a contract outside the council folder": (
        lambda r: r.write("docs/api.yaml", "placeholder: false\n"),
        ["docs/api.yaml"],
    ),
    "its own verification steps": (
        lambda r: write_tickets(
            r, ticket_list([COMPILES], [ticket(1, [STEP | {"run": ["true"]}])])
        ),
        ["council/tickets.json"],
    ),
    "its own pass": (
        lambda r: r.write("council/build.yaml", "version: 2\n"),
        ["council/build.yaml"],
    ),
    "a path the ticket list makes read-only": (
        lambda r: r.write("conftest.py", "placeholder = 1\n"),
        ["conftest.py"],
    ),
    "the council folder under another case": (
        lambda r: r.write("COUNCIL/fitness/check_greeting.py", "placeholder = 1\n"),
        ["COUNCIL/fitness/check_greeting.py"],
    ),
}


@pytest.mark.parametrize("edit", EDITS.values(), ids=EDITS.keys())
def test_a_commit_that_edits_what_judges_it_is_refused_whatever_its_tests_say(
    repo: Solution, marker: Path, edit: tuple[Callable[[Repo], object], list[str]]
) -> None:
    """Why: slice 4's second check, and ADR-0027's reason: a loop that grades itself passes by
    changing the test instead of the code. The weakened fitness function would pass if run, so
    the refusal must come first, and none of the commit's code may run."""
    change, refused = edit
    repo.write(GREETING, RIGHT)
    change(repo)
    repo.commit("the loop changes what judges it")
    record = repo.verify()
    assert record.refused == refused
    assert [(t.passes, t.steps) for t in record.tickets] == [(False, [])]
    assert record.checks == []
    assert not marker.exists(), "nothing of a refused commit runs"


def test_an_edit_undone_on_the_branch_is_not_a_change(repo: Solution) -> None:
    """Why: the verifier judges the commit's files, not its history; a loop that reverts its
    mistake must be able to go on."""
    repo.write(GREETING, RIGHT)
    edit_fitness(repo)
    repo.commit("the loop weakens the check")
    repo.git("checkout", "main", "--", FITNESS)
    repo.commit("the loop puts it back")
    record = repo.verify()
    assert record.refused == []
    assert record.tickets[0].passes


# What it runs, and how ------------------------------------------------------------------------


def test_it_runs_the_commit_not_the_working_tree(repo: Solution) -> None:
    """Why: "a clean checkout of the loop's commit". An uncommitted fix in the working tree is
    not what a merge would carry."""
    repo.write(GREETING, WRONG + "# the loop's commit\n")
    repo.commit("the loop commits the wrong greeting")
    repo.write(GREETING, RIGHT)
    assert not repo.verify().tickets[0].passes


def test_no_command_sees_what_another_did(tmp_path: Path) -> None:
    """Why: a check runs the loop's code, and that code could rewrite a fitness function in
    its checkout before the step runs it. Each command gets its own clean checkout."""
    rewrite = {"name": "runs-the-code", "run": [PYTHON, GREETING]}
    repo = Solution(tmp_path / "solution", ticket_list([rewrite]))
    repo.write(
        GREETING,
        WRONG + f"open({FITNESS!r}, 'w').write('placeholder = 1')\n",
    )
    repo.commit("the loop's code rewrites the fitness function when run")
    record = repo.verify()
    assert record.checks[0].passed
    assert not record.tickets[0].passes, "the step ran the fitness function as Tom merged it"


def test_a_command_gets_only_the_allowlisted_environment(
    repo: Solution, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Why: the commands run a loop's code, so they get no credential; with the whole
    environment, the same step sees the variable, which shows the test can fail."""
    monkeypatch.setenv("PLACEHOLDER_TOKEN", "placeholder")
    probe = [PYTHON, "-c", "import os, sys; sys.exit('PLACEHOLDER_TOKEN' in os.environ)"]
    write_tickets(repo, ticket_list([COMPILES], [ticket(1, [STEP | {"run": probe}])]))
    repo.git("checkout", "--quiet", "main")
    repo.base = repo.commit("a step that looks for a credential")
    repo.git("checkout", "--quiet", "loop")
    repo.git("merge", "--quiet", "main")
    config = load_config(REPO_CONFIG)
    assert config.verifier is not None
    allowed = environment_for(config.verifier.environment, os.environ)
    assert repo.verify(environment=allowed).tickets[0].passes
    assert not repo.verify(environment=dict(os.environ)).tickets[0].passes


def test_a_command_that_hangs_is_stopped_with_everything_it_started(tmp_path: Path) -> None:
    """Why: a loop's code can hang, or leave a child holding the output open; the verifier
    must stop on time and record why the step failed."""
    sleeper = "import time; time.sleep(60)"
    child = f"import subprocess, sys; subprocess.run([sys.executable, '-c', {sleeper!r}])"
    hang = STEP | {"run": [PYTHON, "-c", child], "timeout_seconds": 1}
    repo = Solution(tmp_path / "solution", ticket_list(tickets=[ticket(1, [hang])]))
    started = time.monotonic()
    step = repo.verify().tickets[0].steps[0]
    assert time.monotonic() - started < 20
    assert step.exit_code is None
    assert step.problem == "ran past its timeout of 1 seconds"


def test_a_command_that_cannot_start_fails_its_step_not_the_verifier(tmp_path: Path) -> None:
    """Why: a missing tool is a failed step to report, not a crash that leaves no record."""
    missing = STEP | {"run": ["kiln-placeholder-no-such-program"]}
    repo = Solution(tmp_path / "solution", ticket_list(tickets=[ticket(1, [missing])]))
    step = repo.verify().tickets[0].steps[0]
    assert step.exit_code is None
    assert (
        step.problem is not None and "cannot run kiln-placeholder-no-such-program" in step.problem
    )


def test_a_failing_check_fails_every_ticket_and_a_tripwire_check_opens_its_tripwire(
    tmp_path: Path,
) -> None:
    """Why: a check guards every commit whatever the ticket; a failed tripwire check is the
    charter's "blocks the commit and asks Tom"."""
    secret_scan = {
        "name": "secrets",
        "run": [PYTHON, "-c", "raise SystemExit(1)"],
        "tripwire": "exposed_secret",
    }
    tickets = ticket_list([COMPILES, secret_scan], [ticket(1), ticket(2)])
    repo = Solution(tmp_path / "solution", tickets)
    repo.write(GREETING, RIGHT)
    repo.commit("the loop greets by name")
    record = repo.verify()
    assert [t.passes for t in record.tickets] == [False, False]
    assert [s.passed for s in record.tickets[0].steps] == [True], "the step itself passed"
    assert record.open_tripwires == [Tripwire.EXPOSED_SECRET]


def test_only_the_tickets_asked_for_are_run(tmp_path: Path) -> None:
    """Why: a loop hands over one ticket at a time; the record then says nothing of the rest,
    and G3 asks for them."""
    repo = Solution(tmp_path / "solution", ticket_list(tickets=[ticket(1), ticket(2)]))
    assert [t.id for t in repo.verify(ticket_ids=["TKT-0002"]).tickets] == ["TKT-0002"]
    with pytest.raises(KilnError, match="TKT-0009 is not in the ticket list"):
        repo.verify(ticket_ids=["TKT-0009"])


# Where the branch began -----------------------------------------------------------------------


def test_a_commit_with_no_history_on_main_is_not_verified(repo: Solution) -> None:
    """Why: with no base, there is no build contract Tom merged to judge it against."""
    repo.git("checkout", "--quiet", "--orphan", "stray")
    repo.commit("a stray commit")
    with pytest.raises(KilnError, match="shares no history with main"):
        repo.verify()


def test_a_branch_must_start_from_a_state_tom_merged(repo: Solution) -> None:
    """Why: a commit inside a merged branch was never on `main` as a whole, so its build
    contract may be one Tom never saw."""
    repo.git("checkout", "--quiet", "-b", "feature", "main")
    repo.write("council/notes.md", "placeholder\n")
    inside = repo.commit("a commit inside a feature branch")
    repo.write("council/notes.md", "placeholder, revised\n")
    repo.commit("its fix")
    repo.merge("feature")
    repo.git("checkout", "--quiet", "-b", "late-loop", inside)
    repo.write(GREETING, RIGHT)
    repo.commit("the loop starts from inside the feature")
    with pytest.raises(KilnError, match="not on main's first-parent history"):
        repo.verify()


def test_a_branch_with_two_merge_bases_is_not_verified(repo: Solution) -> None:
    """Why: with two bases there are two build contracts the commit could be judged against;
    the verifier asks for one."""
    repo.write(GREETING, RIGHT)
    on_loop = repo.commit("loop")
    repo.git("checkout", "--quiet", "main")
    repo.write("council/notes.md", "placeholder\n")
    on_main = repo.commit("main")
    repo.git("merge", "--quiet", "--no-ff", "-m", "main takes loop", on_loop)
    repo.git("checkout", "--quiet", "loop")
    repo.git("merge", "--quiet", "--no-ff", "-m", "loop takes main", on_main)
    with pytest.raises(KilnError, match="2 merge bases"):
        repo.verify()


def test_the_verifier_runs_only_from_the_top_of_the_repository(repo: Solution) -> None:
    """Why: git's paths start at the top; from a subfolder, `council/` would not be the folder
    git reports, and a protected change could pass unseen."""
    with pytest.raises(KilnError, match="top of the solution's repository"):
        verify(repo.root / "src", "HEAD", environment=ENVIRONMENT, ref="main")


def test_an_unfetched_ref_fails_loudly(repo: Solution) -> None:
    """Why: in a fresh clone `origin/main` may not be fetched; that must not read as no base."""
    with pytest.raises(KilnError, match="the branch Tom merges into is not here"):
        verify(repo.root, "HEAD", environment=ENVIRONMENT, ref="origin/main")


# The record, and rechecking it ----------------------------------------------------------------


def passing(repo: Solution) -> BuildRecord:
    repo.write(GREETING, RIGHT)
    repo.commit("the loop greets by name")
    return repo.verify()


def test_the_record_is_written_whole_and_reads_back_the_same(repo: Solution) -> None:
    """Why: G3 reads this file; it must say exactly what the verifier found, and the same run
    must write the same bytes."""
    record = passing(repo)
    path = write_record(repo.root, record)
    first = path.read_text()
    assert first.startswith(RECORD_HEADER)
    assert parse_yaml(path.read_bytes(), BuildRecord, item=str(path)) == record
    write_record(repo.root, repo.verify())
    assert path.read_text() == first


def test_a_record_whose_pass_does_not_follow_from_its_results_will_not_load(
    repo: Solution,
) -> None:
    """Why: the record is the only place a pass lives. A hand edit that keeps a pass after a
    failed check, gives a refused commit results, or hides why a command stopped must fail to
    load, not be believed."""
    record = passing(repo).model_dump(mode="json")
    edits: list[tuple[dict[str, Any], str]] = [
        ({"exit_code": 1, "output": "placeholder"}, "pass does not follow from its results"),
        ({"exit_code": None}, "did not finish says why"),
        ({"output": "placeholder"}, "kept only for a command that failed"),
    ]
    for edit, message in edits:
        broken = copy.deepcopy(record)
        broken["checks"][0].update(edit)
        with pytest.raises(ValidationError, match=message):
            BuildRecord.model_validate(broken)
    refused = copy.deepcopy(record) | {"refused": [FITNESS]}
    with pytest.raises(ValidationError, match="a refused commit is never run"):
        BuildRecord.model_validate(refused)


def test_a_fresh_record_rechecks_clean(repo: Solution) -> None:
    """Why: the rechecks must accept the verifier's own work, or G3 can never pass."""
    record = passing(repo)
    write_record(repo.root, record)
    assert recheck(repo.root, record, "main") == []


def test_a_record_for_code_that_changed_since_does_not_hold(repo: Solution) -> None:
    """Why: a pass is for one commit; code changed after it, committed or not, was never
    verified."""
    record = passing(repo)
    repo.write("src/greeting.py", RIGHT + "# changed after\n")
    assert recheck(repo.root, record, "main") == [
        "src/greeting.py changed after the verifier ran on "
        f"{record.commit[:12]}; run it again on the commit that holds them"
    ]


def test_a_file_added_after_the_record_was_written_means_it_does_not_hold(repo: Solution) -> None:
    """Why: an untracked file is in the build G3 looks at, but was not in the commit the
    verifier ran; a new module beside the code could change what it does."""
    record = passing(repo)
    repo.write("src/sitecustomize.py", "placeholder = 1\n")
    problems = recheck(repo.root, record, "main")
    assert len(problems) == 1 and problems[0].startswith("src/sitecustomize.py changed after")


def test_a_record_that_hides_a_refusal_does_not_hold(repo: Solution) -> None:
    """Why: a record written by hand could claim a pass for a commit that weakened its fitness
    function; history shows the change, whatever the record says."""
    record = passing(repo)
    edit_fitness(repo)
    repo.commit("the loop weakens the check")
    forged = record.model_copy(update={"commit": repo.git("rev-parse", "HEAD")})
    assert recheck(repo.root, forged, "main") == [
        f"it records the refusal of nothing, but history gives ['{FITNESS}']"
    ]


@pytest.mark.parametrize(
    ("field", "value", "problem"),
    [
        ("tickets_sha256", content_hash(b"other"), "a ticket list other than the one at"),
        ("plan_sha256", content_hash(b"other"), "a plan other than the one at"),
        ("base", "f" * 40, "a commit that is not here"),
    ],
)
def test_a_record_that_misnames_what_it_judged_does_not_hold(
    repo: Solution, field: str, value: str, problem: str
) -> None:
    """Why: each of these names what the pass was judged against; a wrong one is no pass."""
    record = passing(repo).model_copy(update={field: value})
    problems = recheck(repo.root, record, "main")
    assert len(problems) == 1 and problem in problems[0]


def test_a_record_is_rechecked_only_from_the_top_of_the_repository(repo: Solution) -> None:
    """Why: from a subfolder, git's paths and the council folder's would not line up, and a
    change could be missed; G3 run from the wrong place must fail, not pass."""
    problems = recheck(repo.root / "src", passing(repo), "main")
    assert problems == [
        "it can be rechecked only from the top of the repository, where git's paths begin"
    ]


def test_a_record_whose_base_tom_never_merged_does_not_hold(repo: Solution) -> None:
    """Why: the base is where the build contract was read; it must be a state on `main`."""
    record = passing(repo)
    off_main = repo.git("rev-parse", "HEAD")
    problems = recheck(repo.root, record.model_copy(update={"base": off_main}), "main")
    assert problems == [f"its base, {off_main[:12]}, is not on main's first-parent history"]


# The command ----------------------------------------------------------------------------------


def run_cli(repo: Solution, *extra: str) -> Any:
    args = ["verify", "HEAD", "--ref", "main", "--root", str(repo.root)]
    return CliRunner().invoke(app, [*args, "--config", str(REPO_CONFIG), *extra])


def test_the_cli_writes_the_record_and_exits_2_unless_every_ticket_passes(
    repo: Solution,
) -> None:
    """Why: the loop and the person running it act on the exit code; the record is written
    whatever it is, so G3 and the loop read the same thing."""
    repo.commit("the loop has done nothing yet")
    failed = run_cli(repo, "--runner", "local")
    assert failed.exit_code == 2
    assert "TKT-0001 did not pass" in failed.output
    record_file = repo.root / "council/build.yaml"
    assert not parse_yaml(record_file.read_bytes(), BuildRecord, item="build").tickets[0].passes
    record_file.unlink()
    repo.write(GREETING, RIGHT)
    repo.commit("the loop greets by name")
    passed = run_cli(repo, "--runner", "local")
    assert passed.exit_code == 0, passed.output
    assert "TKT-0001: passes" in passed.output
    data = yaml.safe_load(record_file.read_text())
    assert data["verified_by"] == "verifier" and data["runner"] == "local"


def test_the_cli_exits_2_on_a_refused_commit(repo: Solution) -> None:
    """Why: a refusal is the loudest result there is; it must not read as a plain failure."""
    edit_fitness(repo)
    repo.commit("the loop weakens the check")
    result = run_cli(repo, "--runner", "local")
    assert result.exit_code == 2
    assert "refused" in result.output and FITNESS in result.output


def test_the_cli_makes_its_caller_say_where_the_code_runs(repo: Solution) -> None:
    """Why: `local` is not a sandbox (ADR-0007); whoever runs the verifier names that choice."""
    result = run_cli(repo)
    assert result.exit_code == 2
    assert not (repo.root / "council/build.yaml").exists()
