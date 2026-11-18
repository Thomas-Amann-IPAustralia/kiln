"""A throwaway git repository with real merge commits, for tests that read history."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

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
    """A repository with a `main` branch and one commit, made with no user or system git
    config, so a developer's signing or hooks cannot leak into a test."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.git("init", "--quiet", "--initial-branch=main")
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

    def write(self, path: str, text: str) -> Path:
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text, encoding="utf-8")
        return file
