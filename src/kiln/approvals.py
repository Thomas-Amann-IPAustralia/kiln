"""Which decision cards Tom has approved, read from `main`'s history (ADR-0028).

**The rule.** A card is approved at the first commit on `main`'s first-parent history where it
holds Tom's answer and every file it rests on has the hash the card states. With `main`
protected so that only a pull request reaches it, every such commit got there by Tom's merge.
The approval names the card's content hash at that commit.

**Lapse.** After approval, the card file and each file it rests on must stay exactly as they
were. If either changes on `main`, the approval has lapsed, even though Tom merged the change:
an edit after approval needs a new card (ADR-0028), and lapsing loudly is how a quiet edit
inside a large merge is caught. A card stops being checked once a card that supersedes it is
approved.

**Limits, stated plainly.** This reads history; it cannot tell Tom's merge from anyone else's
push. It relies on the ruleset that protects `main`, and on Tom's merges being merge commits
or squashes: a rebase merge replays each branch commit onto `main`, so a card corrected on the
branch would show as approved, then edited. That error is loud and safe, never a false
approval.

The working tree is checked too, so a branch that would lapse an approval is caught before Tom
merges it.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import StrEnum
from pathlib import Path

from kiln.cards import CARDS_DIR, DecisionCard, parse_card
from kiln.errors import KilnError
from kiln.ids import content_hash

DEFAULT_REF = "origin/main"


class Status(StrEnum):
    OPEN = "open"
    """Not answered: on `main` or only here, it awaits Tom's answer."""
    AWAITING_MERGE = "awaiting merge"
    """Answered in the working tree, not yet merged into the ref. Not in effect."""
    APPROVED = "approved"
    LAPSED = "lapsed"
    """Approved, then the card or a file it rests on changed on the ref."""
    SUPERSEDED = "superseded"
    INVALID = "invalid"
    """On the ref, but not a valid card, or answered with hashes that did not match."""


@dataclass(frozen=True)
class Commit:
    sha: str
    on: date


@dataclass
class CardApproval:
    """What the history says about one card file."""

    path: str
    card_id: str | None = None
    title: str | None = None
    status: Status = Status.OPEN
    approved_at: Commit | None = None
    card_sha256: str | None = None
    """The card's content hash when approved, or its current one if not approved."""
    choice: str | None = None
    notes: list[str] = field(default_factory=list[str])
    warnings: list[str] = field(default_factory=list[str])
    """Changes in the working tree that would lapse an approval if merged."""

    @property
    def needs_action(self) -> bool:
        return self.status in (Status.LAPSED, Status.INVALID) or bool(self.warnings)


class _Git:
    """Read-only access to one repository. Every failure is a `KilnError`."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self._blobs: dict[str, bytes] = {}

    def run(self, *args: str) -> bytes:
        try:
            done = subprocess.run(  # noqa: S603 -- fixed git subcommands, no shell
                ["git", "-C", str(self.root), *args],  # noqa: S607 -- git from PATH, like CI
                capture_output=True,
                check=False,
            )
        except FileNotFoundError as exc:
            raise KilnError("git is not installed", item="git") from exc
        if done.returncode != 0:
            message = done.stderr.decode("utf-8", "replace").strip().splitlines()
            raise KilnError(
                f"git {args[0]} failed: {message[-1] if message else done.returncode}",
                item=" ".join(args),
            )
        return done.stdout

    def first_parent_commits(self, ref: str) -> list[Commit]:
        try:
            self.run("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
        except KilnError as exc:
            raise KilnError(
                "the ref to read approvals from does not exist here",
                item=ref,
                see="`git fetch origin main`, or pass --ref",
            ) from exc
        out = self.run("log", "--first-parent", "--reverse", "--format=%H %ct", ref, "--")
        commits: list[Commit] = []
        for line in out.decode().splitlines():
            sha, stamp = line.split()
            commits.append(Commit(sha, datetime.fromtimestamp(int(stamp), UTC).date()))
        return commits

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


@dataclass
class _Tracked:
    result: CardApproval
    blob: str | None = None
    card: DecisionCard | None = None
    rested_blobs: dict[str, str | None] = field(default_factory=dict[str, str | None])


def read_approvals(
    root: Path, ref: str = DEFAULT_REF, cards_dir: Path = CARDS_DIR
) -> list[CardApproval]:
    """Every card on `ref` or in the working tree, with what the history says about it."""
    git = _Git(root)
    prefix = cards_dir.as_posix().rstrip("/") + "/"
    tracked: dict[str, _Tracked] = {}
    for commit in git.first_parent_commits(ref):
        tree = git.tree(commit.sha)
        for path in sorted(p for p in tree if p.startswith(prefix) and p.endswith(".md")):
            tracked.setdefault(path, _Tracked(CardApproval(path)))
        states = [tracked[path] for path in sorted(tracked)]
        # 1. Read each changed card that is not yet approved; it may become approved here.
        newly_approved: list[DecisionCard] = []
        for state in states:
            if state.result.status in _SETTLED or tree.get(state.result.path) == state.blob:
                continue
            _read_version(git, state, tree, commit)
            if state.result.status is Status.APPROVED and state.card is not None:
                newly_approved.append(state.card)
        # 2. A card approved here ends the cards it supersedes, before any lapse is judged.
        for card in newly_approved:
            if card.supersedes is None:
                continue
            for state in states:
                target = state.result
                if card.supersedes == target.card_id and target.status is not Status.SUPERSEDED:
                    target.status = Status.SUPERSEDED
                    target.notes.append(f"superseded by {card.id} on {commit.on}")
        # 3. A card approved earlier lapses if it, or a file it rests on, changed here.
        for state in states:
            if state.result.status is Status.APPROVED and state.result.approved_at != commit:
                _check_unchanged(state, tree, commit)
    results = {path: state.result for path, state in tracked.items()}
    _check_working_tree(root, cards_dir, tracked, results)
    return [results[path] for path in sorted(results)]


_SETTLED = frozenset({Status.APPROVED, Status.LAPSED, Status.SUPERSEDED})
"""States a later version of the card cannot change: only a superseding card ends them."""


def _read_version(git: _Git, state: _Tracked, tree: dict[str, str], commit: Commit) -> None:
    result = state.result
    state.blob = tree.get(result.path)
    if state.blob is None:
        result.status, result.notes, state.card = Status.OPEN, ["removed from the ref"], None
        return
    data = git.blob(state.blob)
    result.card_sha256 = content_hash(data)
    try:
        card = parse_card(data.decode("utf-8"), item=result.path)
    except (KilnError, UnicodeDecodeError) as exc:
        result.status, result.notes, state.card = Status.INVALID, [f"not a valid card: {exc}"], None
        return
    state.card = card
    result.card_id, result.title = card.id, card.title
    if card.answer is None:
        result.status, result.notes = Status.OPEN, []
        return
    mismatched = [
        entry.path
        for entry in card.rests_on
        if (blob := tree.get(entry.path)) is None or content_hash(git.blob(blob)) != entry.sha256
    ]
    if mismatched:
        result.status = Status.INVALID
        result.notes = [
            f"answered at {commit.sha[:7]}, but these files did not match the card's hashes "
            "there, so nothing was approved: " + ", ".join(mismatched)
        ]
        return
    result.status, result.notes = Status.APPROVED, []
    result.approved_at, result.choice = commit, card.answer.choice
    state.rested_blobs = {entry.path: tree.get(entry.path) for entry in card.rests_on}


def _check_unchanged(state: _Tracked, tree: dict[str, str], commit: Commit) -> None:
    result = state.result
    blob = tree.get(result.path)
    if blob != state.blob:
        what = "removed" if blob is None else "edited"
        result.status = Status.LAPSED
        result.notes.append(f"the card was {what} after its approval, at {commit.sha[:7]}")
        return
    for path, rested in state.rested_blobs.items():
        if tree.get(path) != rested:
            result.status = Status.LAPSED
            result.notes.append(
                f"{path}, which it rests on, changed after its approval, at {commit.sha[:7]}"
            )
            return


def _check_working_tree(
    root: Path, cards_dir: Path, tracked: dict[str, _Tracked], results: dict[str, CardApproval]
) -> None:
    """Compare the working tree with the ref: what is answered but unmerged, and what a merge
    of this branch would lapse."""
    folder = root / cards_dir
    here: dict[str, bytes] = {}
    if folder.is_dir():
        here = {(cards_dir / p.name).as_posix(): p.read_bytes() for p in folder.glob("*.md")}
    answered_supersessions: set[str] = set()
    for path, data in sorted(here.items()):
        try:
            card = parse_card(data.decode("utf-8"), item=path)
        except (KilnError, UnicodeDecodeError) as exc:
            if path not in results:
                results[path] = CardApproval(path, status=Status.INVALID, notes=[str(exc)])
            continue
        if card.supersedes and card.answer is not None:
            answered_supersessions.add(card.supersedes)
        result = results.get(path)
        if result is None:
            result = results[path] = CardApproval(path, card.id, card.title)
            result.card_sha256 = content_hash(data)
        if result.status is Status.OPEN and content_hash(data) != result.card_sha256:
            result.card_id, result.title = card.id, card.title
            result.card_sha256 = content_hash(data)
        if result.status is Status.OPEN and card.answer is not None:
            result.status = Status.AWAITING_MERGE
    for path, state in sorted(tracked.items()):
        result = state.result
        if result.status is not Status.APPROVED or result.card_id in answered_supersessions:
            continue
        if path not in here or content_hash(here[path]) != result.card_sha256:
            result.warnings.append("the card differs here from its approved version")
        for entry in state.card.rests_on if state.card is not None else []:
            file = root / entry.path
            if not file.is_file() or content_hash(file.read_bytes()) != entry.sha256:
                result.warnings.append(f"{entry.path} differs here from its approved version")


def render(results: list[CardApproval], ref: str) -> str:
    """One block per card, for a person to read."""
    if not results:
        return f"No decision cards on {ref} or in the working tree."
    lines: list[str] = []
    for result in results:
        name = f"{result.card_id or result.path}: {result.title}" if result.title else result.path
        if result.status is Status.APPROVED and result.approved_at:
            head = (
                f"approved at {result.approved_at.sha[:7]} on {result.approved_at.on}, "
                f"answer {result.choice!r}, card {result.card_sha256}"
            )
        else:
            head = result.status.value
        lines.append(f"{name}\n  {head}")
        lines += [f"  - {note}" for note in result.notes]
        lines += [f"  ! merging this would lapse the approval: {w}" for w in result.warnings]
    return "\n".join(lines)
