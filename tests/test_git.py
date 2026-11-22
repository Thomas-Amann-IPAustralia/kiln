"""The one reader of git history: what it reports, and that nothing ambient can redirect it."""

from __future__ import annotations

from pathlib import Path

import pytest

from kiln.errors import KilnError
from kiln.git import Git
from tests.gitrepo import Repo


def new_repo(root: Path) -> Repo:
    root.mkdir()
    return Repo(root)


@pytest.fixture
def repo(tmp_path: Path) -> Repo:
    return new_repo(tmp_path / "repo")


def test_reads_files_changes_and_ancestry(repo: Repo) -> None:
    """Why: the verifier and G3 decide on these answers; each must be exact."""
    repo.write("a.txt", "one\n")
    first = repo.commit("add a")
    repo.write("a.txt", "two\n")
    repo.write("b/c.txt", "three\n")
    second = repo.commit("change a, add c")
    git = Git(repo.root)
    assert git.commit("HEAD") == second
    assert git.show(first, "a.txt") == b"one\n"
    assert git.show(first, "b/c.txt") is None
    assert git.show(second, "b") is None, "a folder is not a file"
    assert git.changed(first, second) == ["a.txt", "b/c.txt"]
    assert git.is_ancestor(first, second)
    assert not git.is_ancestor(second, first)
    assert git.first_parent("main")[-2:] == [first, second]
    repo.write("a.txt", "edited\n")
    repo.write("new.txt", "untracked\n")
    assert git.changed(second) == ["a.txt"]
    assert git.untracked() == ["new.txt"]


def test_a_rename_counts_as_both_of_its_paths(repo: Repo) -> None:
    """Why: moving a protected file away is changing it; a rename must not hide the old path."""
    repo.write("council/fitness/check.py", "placeholder = 1\n")
    before = repo.commit("add")
    repo.git("mv", "council/fitness/check.py", "elsewhere.py")
    after = repo.commit("move")
    assert Git(repo.root).changed(before, after) == ["council/fitness/check.py", "elsewhere.py"]


def test_a_variable_that_relocates_git_is_ignored(
    repo: Repo, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Why: a pre-commit hook exports GIT_INDEX_FILE; read through it, a solution's working
    tree would be compared with another repository's index, and GIT_DIR would read another
    repository's history altogether."""
    other = new_repo(tmp_path / "other")
    other.write("only-here.txt", "placeholder\n")
    other.commit("other")
    monkeypatch.setenv("GIT_DIR", str(other.root / ".git"))
    monkeypatch.setenv("GIT_INDEX_FILE", str(other.root / ".git" / "index"))
    git = Git(repo.root)
    assert git.show("HEAD", "only-here.txt") is None
    assert git.changed("HEAD") == []


def test_a_name_that_is_not_a_commit_fails_with_its_cause(repo: Repo) -> None:
    """Why: a mistyped commit or an unfetched ref must stop the command, not read as empty."""
    with pytest.raises(KilnError, match="the loop's commit is not here"):
        Git(repo.root).commit("no-such-branch", cause="the loop's commit is not here")
