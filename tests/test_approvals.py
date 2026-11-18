"""`kiln approvals` against real, throwaway git repositories with real merge commits.

Each test builds a small history: work on a branch, then a `--no-ff` merge into `main`, the
way Tom merges a pull request on GitHub.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from kiln.approvals import CardApproval, Status, read_approvals
from kiln.cards import DecisionCard
from kiln.cli import app
from kiln.errors import KilnError
from kiln.ids import content_hash
from tests.test_cards import PLAN, answer, make_card, write_card

_ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "Placeholder",
    "GIT_AUTHOR_EMAIL": "placeholder@example.invalid",
    "GIT_COMMITTER_NAME": "Placeholder",
    "GIT_COMMITTER_EMAIL": "placeholder@example.invalid",
}


class Repo:
    """A repository with a `main` branch and one plan file."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.git("init", "--quiet", "--initial-branch=main")
        (root / "docs").mkdir()
        (root / PLAN).write_text("# Placeholder plan\n")
        self.commit("start")

    def git(self, *args: str) -> str:
        done = subprocess.run(
            ["git", "-c", "commit.gpgsign=false", *args],
            cwd=self.root,
            env=_ENV,
            capture_output=True,
            text=True,
            check=True,
        )
        return done.stdout.strip()

    def commit(self, message: str) -> str:
        self.git("add", "--all")
        self.git("commit", "--quiet", "--allow-empty", "-m", message)
        return self.git("rev-parse", "HEAD")

    def branch(self, name: str) -> None:
        self.git("checkout", "--quiet", "-b", name, "main")

    def merge(self, name: str) -> str:
        """Tom's merge: a merge commit on `main`, then back to `main`'s working tree."""
        self.git("checkout", "--quiet", "main")
        self.git("merge", "--quiet", "--no-ff", "-m", f"Merge {name}", name)
        return self.git("rev-parse", "HEAD")

    def card(self, card: DecisionCard) -> Path:
        return write_card(self.root, card)


@pytest.fixture
def repo(tmp_path: Path) -> Repo:
    return Repo(tmp_path)


def approval(repo: Repo, path_part: str = "CARD-0001") -> CardApproval:
    results = read_approvals(repo.root, "main")
    return next(r for r in results if path_part in r.path)


def approve_first_card(repo: Repo) -> str:
    repo.branch("card-1")
    repo.card(make_card(repo.root, answer=answer()))
    repo.commit("card 1, answered")
    return repo.merge("card-1")


def test_an_answered_card_is_approved_by_the_merge_that_brings_it(repo: Repo) -> None:
    """Why: ADR-0028: Tom's merge is the approval, and it names the card's exact hash."""
    merge = approve_first_card(repo)
    result = approval(repo)
    assert result.status is Status.APPROVED
    assert result.approved_at is not None and result.approved_at.sha == merge
    card_file = next((repo.root / "docs/cards").glob("CARD-0001-*.md"))
    assert result.card_sha256 == content_hash(card_file.read_bytes())
    assert result.choice == "Approve"
    assert not result.needs_action


def test_a_merged_card_without_an_answer_approves_nothing(repo: Repo) -> None:
    """Why: a merged question is not an answer (D-010): the sketch was merged before Tom
    answered it."""
    repo.branch("card-1")
    repo.card(make_card(repo.root))
    repo.commit("card 1, open")
    repo.merge("card-1")
    assert approval(repo).status is Status.OPEN


def test_an_answer_on_a_branch_is_not_in_effect_until_merged(repo: Repo) -> None:
    """Why: an agent can write Tom's answer down, but only his merge puts it into effect."""
    repo.branch("card-1")
    repo.card(make_card(repo.root, answer=answer()))
    repo.commit("card 1, answered")
    assert approval(repo).status is Status.AWAITING_MERGE


def test_editing_an_approved_card_lapses_it_even_through_a_merge(repo: Repo) -> None:
    """Why: an edit after approval needs a new card; a quiet change inside a large merge must
    show up, not inherit the approval."""
    approve_first_card(repo)
    repo.branch("edit")
    card = make_card(repo.root, answer=answer(words="Placeholder yes, edited later."))
    repo.card(card)
    repo.commit("edit card 1")
    repo.merge("edit")
    result = approval(repo)
    assert result.status is Status.LAPSED
    assert "the card was edited after its approval" in result.notes[0]
    assert result.needs_action


def test_changing_a_file_the_card_rests_on_lapses_it(repo: Repo) -> None:
    """Why: G2's rule in slice 2: a plan edited after approval is no longer approved."""
    approve_first_card(repo)
    repo.branch("edit-plan")
    (repo.root / PLAN).write_text("# Placeholder plan, edited\n")
    repo.commit("edit the plan")
    repo.merge("edit-plan")
    result = approval(repo)
    assert result.status is Status.LAPSED
    assert f"{PLAN}, which it rests on, changed" in result.notes[0]


def test_a_card_whose_hashes_were_wrong_when_merged_is_invalid(repo: Repo) -> None:
    """Why: an approval must cover exactly the version the card names, or it covers nothing."""
    repo.branch("card-1")
    card = make_card(repo.root, answer=answer())
    (repo.root / PLAN).write_text("# Placeholder plan, not what the card names\n")
    repo.card(card)
    repo.commit("card 1 with a stale hash")
    repo.merge("card-1")
    result = approval(repo)
    assert result.status is Status.INVALID
    assert PLAN in result.notes[0]


def test_only_mains_first_parent_history_counts(repo: Repo) -> None:
    """Why: commits on a branch were never merged on their own; only the merge was Tom's."""
    repo.branch("card-1")
    bad = make_card(repo.root, answer=answer())
    (repo.root / PLAN).write_text("# Placeholder plan v2\n")
    repo.card(bad)
    repo.commit("answered card with a stale hash")
    repo.card(make_card(repo.root, answer=answer()))
    repo.commit("fix the hash")
    merge = repo.merge("card-1")
    result = approval(repo)
    assert result.status is Status.APPROVED
    assert result.approved_at is not None and result.approved_at.sha == merge


def test_a_superseding_card_ends_the_old_approval_without_a_lapse(repo: Repo) -> None:
    """Why: changing an approved plan the right way, with a new card, must not read as a lapse."""
    approve_first_card(repo)
    repo.branch("card-2")
    (repo.root / PLAN).write_text("# Placeholder plan, revised\n")
    repo.card(make_card(repo.root, 2, supersedes="CARD-0001", answer=answer()))
    repo.commit("card 2 supersedes card 1")
    repo.merge("card-2")
    assert approval(repo, "CARD-0001").status is Status.SUPERSEDED
    assert approval(repo, "CARD-0002").status is Status.APPROVED


def test_a_branch_that_would_lapse_an_approval_is_flagged_before_the_merge(repo: Repo) -> None:
    """Why: the warning is most useful while the pull request is still open."""
    approve_first_card(repo)
    repo.branch("edit-plan")
    (repo.root / PLAN).write_text("# Placeholder plan, edited on a branch\n")
    result = approval(repo)
    assert result.status is Status.APPROVED
    assert result.warnings == [f"{PLAN} differs here from its approved version"]
    assert result.needs_action


def test_a_missing_ref_fails_loudly(repo: Repo) -> None:
    """Why: in a fresh clone `main` may not exist locally; silence would read as "no cards"."""
    with pytest.raises(KilnError, match="does not exist here"):
        read_approvals(repo.root, "origin/main")


def test_the_cli_exits_2_on_a_lapse_and_0_otherwise(repo: Repo) -> None:
    """Why: exit codes are what a hook or CI step would key on."""
    approve_first_card(repo)
    runner = CliRunner()
    ok = runner.invoke(app, ["approvals", "--ref", "main", "--root", str(repo.root)])
    assert ok.exit_code == 0, ok.output
    assert "CARD-0001: Approve the placeholder plan 1" in ok.output
    assert "approved at" in ok.output
    (repo.root / PLAN).write_text("# Placeholder plan, edited\n")
    flagged = runner.invoke(app, ["approvals", "--ref", "main", "--root", str(repo.root)])
    assert flagged.exit_code == 2
    assert "merging this would lapse the approval" in flagged.output
