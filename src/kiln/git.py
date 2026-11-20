"""Read access to a git repository, for every module that reads history.

Kiln's own reads of history (approvals, the verifier, G3) go through `Git`, so every failure
is one `KilnError`, and no ambient variable can point a read at another repository: the
variables that move where git looks (`GIT_DIR`, `GIT_INDEX_FILE` and the like) are dropped
before each call. A pre-commit hook exports `GIT_INDEX_FILE`, for example, and a comparison
of a solution's working tree would otherwise read Kiln's own index.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from kiln.errors import KilnError

RELOCATING = frozenset(
    {
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_COMMON_DIR",
        "GIT_DIR",
        "GIT_INDEX_FILE",
        "GIT_NAMESPACE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_WORK_TREE",
    }
)
"""Variables that make git read a repository, index or object store other than the one named."""


def git_environment() -> dict[str, str]:
    """The current environment, minus the variables that relocate git."""
    return {name: value for name, value in os.environ.items() if name not in RELOCATING}


class Git:
    """One repository, read through git. Every failure is a `KilnError`."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self._blobs: dict[str, bytes] = {}

    def run(self, *args: str, ok: frozenset[int] = frozenset({0})) -> bytes:
        """git's output for `args`, run in this repository. An exit code outside `ok` fails."""
        return self.result(*args, ok=ok)[1]

    def result(self, *args: str, ok: frozenset[int] = frozenset({0})) -> tuple[int, bytes]:
        """git's exit code and output, for a command whose exit code is its answer."""
        try:
            done = subprocess.run(  # noqa: S603 -- fixed git subcommands, no shell
                ["git", "-C", str(self.root), *args],  # noqa: S607 -- git from PATH, like CI
                capture_output=True,
                check=False,
                env=git_environment(),
            )
        except FileNotFoundError as exc:
            raise KilnError("git is not installed", item="git") from exc
        if done.returncode not in ok:
            message = done.stderr.decode("utf-8", "replace").strip().splitlines()
            raise KilnError(
                f"git {args[0]} failed: {message[-1] if message else done.returncode}",
                item=" ".join(args),
            )
        return done.returncode, done.stdout

    def commit(self, revision: str, *, cause: str | None = None, see: str | None = None) -> str:
        """The full id of the commit `revision` names, or a `KilnError` with `cause`."""
        code, out = self.result(
            "rev-parse", "--verify", "--quiet", f"{revision}^{{commit}}", ok=frozenset({0, 1})
        )
        if code != 0:
            raise KilnError(cause or "no such commit here", item=revision, see=see)
        return out.decode().strip()

    def is_top_level(self) -> bool:
        """Whether the root is the top of its working tree, so paths from git match ours."""
        return self.run("rev-parse", "--show-prefix").decode().strip() == ""

    def first_parent(self, ref: str) -> list[str]:
        """The commits on `ref`'s first-parent history, oldest first."""
        out = self.run("rev-list", "--first-parent", "--reverse", ref, "--")
        return out.decode().split()

    def merge_bases(self, one: str, other: str) -> list[str]:
        code, out = self.result("merge-base", "--all", one, other, ok=frozenset({0, 1}))
        return out.decode().split() if code == 0 else []

    def is_ancestor(self, ancestor: str, commit: str) -> bool:
        code, _ = self.result("merge-base", "--is-ancestor", ancestor, commit, ok=frozenset({0, 1}))
        return code == 0

    def changed(self, base: str, commit: str | None = None) -> list[str]:
        """Every path that differs between two commits, or between a commit and the working
        tree when `commit` is None. A rename counts as both of its paths."""
        args = ["diff", "--name-only", "-z", "--no-renames", "--no-relative", "--no-ext-diff"]
        out = self.run(*args, base, *([commit] if commit else []), "--")
        return sorted(path for path in out.decode("utf-8").split("\0") if path)

    def untracked(self) -> list[str]:
        """Files in the working tree that git does not track and does not ignore."""
        out = self.run("ls-files", "--others", "--exclude-standard", "-z")
        return sorted(path for path in out.decode("utf-8").split("\0") if path)

    def show(self, commit: str, path: str) -> bytes | None:
        """A file's bytes at `commit`, or None if it has no such file."""
        for entry in self.run("ls-tree", "-z", commit, "--", path).split(b"\0"):
            if not entry:
                continue
            meta, name = entry.split(b"\t", 1)
            _mode, kind, blob = meta.decode().split()
            if kind == "blob" and name.decode("utf-8") == path:
                return self.blob(blob)
        return None

    def tree(self, commit: str) -> dict[str, str]:
        """Every file at `commit`, path to blob id."""
        entries: dict[str, str] = {}
        for entry in self.run("ls-tree", "-r", "-z", commit).split(b"\0"):
            if not entry:
                continue
            meta, path = entry.split(b"\t", 1)
            _mode, kind, blob = meta.decode().split()
            if kind == "blob":
                entries[path.decode("utf-8")] = blob
        return entries

    def blob(self, blob: str) -> bytes:
        if blob not in self._blobs:
            self._blobs[blob] = self.run("cat-file", "blob", blob)
        return self._blobs[blob]
