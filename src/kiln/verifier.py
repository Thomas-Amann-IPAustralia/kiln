"""The verifier: the only writer of a ticket's pass (ADR-0027).

A coding loop hands the verifier a commit. The verifier, not the loop, decides whether each
ticket passes there:

1. **Where the branch began.** The commit's merge base with `origin/main` must be a single
   commit on main's first-parent history: a state Tom merged. The build contract is read
   there, never from the commit: `council/tickets.json` and `council/plan.yaml`.
2. **What judges it is untouched.** Compared with that base, the commit may not change anything
   read-only to loops: the whole `council/` folder (the tickets and their verification steps,
   the contracts, the fitness functions, the plan, the cards and the verifier's own record),
   every contract the plan names wherever it lives, and every path the ticket list marks
   `read_only`. Paths are compared without regard to case, so `COUNCIL/` cannot stand in for
   `council/` where a file system folds case. A commit that changes one is **refused, whatever
   its tests say**, and none of its code runs.
3. **Clean checkouts.** Each check and each step runs in its own fresh clone of the commit, so
   nothing in the working tree the commit came from (an uncommitted fix, an untracked file) can
   make it pass, and nothing one command does can change what the next one sees.
4. **Every check, then each ticket's steps.** Each is an argument list run with no shell, only
   the environment variables config allows, and its timeout, after which it and everything it
   started are stopped. A ticket passes when every check and every one of its steps exits 0.
5. **The record,** `council/build.yaml`: the commit, its base, the hashes of the ticket list
   and plan it was judged against, and each result. G3 reads it, and `recheck` recomputes from
   history everything in it except the commands' results.

**Limits, stated plainly.**

- *It runs the commit's code.* ADR-0007 puts agent-written code only in a sandbox, and slice 5
  builds one. The `local` runner is this machine, with only the environment allowlist between
  the code and it: use it on code no agent wrote, or from inside a sandbox.
- *A step is only as strong as what it runs.* A step that runs a test the loop may edit can be
  passed by editing the test, so steps should run files under `council/fitness/` or paths in
  `read_only`. Code written to detect that it is under test is not caught here; Tom's team and
  the human experts are the check on that.
- *A record can be forged by anyone who can write the repository.* `recheck` catches a record
  that disagrees with history, not one invented with care. Before a loop runs unattended, a pass
  needs, like an approval, a writer no agent can impersonate (ADR-0028; handover, For Tom).
"""

from __future__ import annotations

import contextlib
import fnmatch
import os
import signal
import subprocess
import tempfile
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

from kiln.approvals import DEFAULT_REF
from kiln.artefacts import (
    BUILD,
    COUNCIL_DIR,
    PLAN,
    TICKETS,
    BuildRecord,
    CheckResult,
    Plan,
    Ran,
    Runner,
    TicketResult,
    parse_yaml,
)
from kiln.errors import KilnError
from kiln.git import Git
from kiln.ids import content_hash
from kiln.recordfile import front_matter, write_atomic
from kiln.tickets import Command, Ticket, TicketList, parse_tickets
from kiln.vocabulary import Actor

RECORD_HEADER = (
    "# Written by the verifier (`kiln verify`), never by hand: ADR-0027. G3 reads it, and\n"
    "# rechecks everything in it against git history except the commands' results.\n"
)
OUTPUT_LINES = 20
"""How much of a failed command's output the record keeps: its last lines, enough to act on."""
OUTPUT_LINE_CHARS = 300


@dataclass(frozen=True)
class Finished:
    """What a runner reports for one command."""

    exit_code: int | None
    output: str
    problem: str | None = None


CommandRunner = Callable[[Sequence[str], Path, Mapping[str, str], float], Finished]
"""Runs one argument list in a directory, with exactly the given environment, under a timeout."""


def run_command(argv: Sequence[str], cwd: Path, env: Mapping[str, str], timeout: float) -> Finished:
    """Run a command in its own process group, with no shell and no input. When it ends or
    runs out of time, everything it started is stopped too, so a lingering child can neither
    hold the verifier up nor outlive the check."""
    try:
        process = subprocess.Popen(  # noqa: S603 -- an argument list from tickets.json, no shell
            list(argv),
            cwd=cwd,
            env=dict(env),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    except OSError as exc:
        return Finished(None, "", f"cannot run {argv[0]}: {exc.strerror or exc}")
    try:
        out, _ = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        _stop_group(process.pid)
        out, _ = process.communicate()
        text = out.decode("utf-8", "replace")
        return Finished(None, text, f"ran past its timeout of {timeout:g} seconds")
    finally:
        _stop_group(process.pid)
    return Finished(process.returncode, out.decode("utf-8", "replace"))


def _stop_group(pid: int) -> None:
    with contextlib.suppress(ProcessLookupError, PermissionError):
        os.killpg(pid, signal.SIGKILL)


@dataclass(frozen=True)
class Contract:
    """The build contract a commit is judged against, read at its base."""

    base: str
    council: str
    tickets: TicketList
    tickets_sha256: str
    plan: Plan
    plan_sha256: str

    def read_only(self, path: str) -> bool:
        """Whether a loop may not change `path`."""
        return _under(path, self.council) or self._named(path)

    def judges(self, path: str) -> bool:
        """Whether a result depends on `path`: every file outside the council folder, and the
        build contract inside it. Cards and later gates' artefacts are added after a build is
        verified, and do not change what it did."""
        if not _under(path, self.council):
            return True
        inside = (TICKETS, PLAN, "contracts", "fitness")
        return any(_under(path, f"{self.council}/{name}") for name in inside) or self._named(path)

    def _named(self, path: str) -> bool:
        return any(_under(path, contract.path) for contract in self.plan.contracts) or any(
            fnmatch.fnmatchcase(path.casefold(), pattern.casefold())
            for pattern in self.tickets.read_only
        )


def _under(path: str, prefix: str) -> bool:
    folded, top = path.casefold(), prefix.casefold().rstrip("/")
    return folded == top or folded.startswith(top + "/")


def find_base(git: Git, commit: str, ref: str) -> str:
    """Where the commit's branch left `ref`: one merge base, on `ref`'s first-parent history."""
    tip = git.commit(
        ref,
        cause="the branch Tom merges into is not here",
        see="`git fetch origin main`, or pass --ref",
    )
    bases = git.merge_bases(commit, tip)
    if not bases:
        raise KilnError(
            f"the commit shares no history with {ref}; a loop's branch starts from it",
            item=commit,
        )
    if len(bases) > 1:
        raise KilnError(
            f"the commit has {len(bases)} merge bases with {ref}; merge {ref} into its branch",
            item=commit,
        )
    if bases[0] not in set(git.first_parent(tip)):
        raise KilnError(
            f"the branch starts from {bases[0][:12]}, which is not on {ref}'s first-parent "
            f"history, so not a state Tom merged; start it from {ref}",
            item=commit,
        )
    return bases[0]


def read_contract(git: Git, base: str, council: Path = COUNCIL_DIR) -> Contract:
    """The ticket list and plan at `base`, or a `KilnError` if either is missing or invalid."""
    folder = council.as_posix()

    def read(name: str) -> tuple[bytes, str]:
        path = f"{folder}/{name}"
        data = git.show(base, path)
        if data is None:
            raise KilnError(
                f"there is no {path} at {base[:12]}; a loop builds only what Tom has merged",
                item=path,
            )
        return data, f"{path} at {base[:12]}"

    tickets_data, tickets_item = read(TICKETS)
    plan_data, plan_item = read(PLAN)
    return Contract(
        base=base,
        council=folder,
        tickets=parse_tickets(tickets_data, item=tickets_item),
        tickets_sha256=content_hash(tickets_data),
        plan=parse_yaml(plan_data, Plan, item=plan_item),
        plan_sha256=content_hash(plan_data),
    )


def refused_paths(git: Git, contract: Contract, commit: str) -> list[str]:
    """The paths read-only to loops that the commit changed, compared with its base."""
    return [path for path in git.changed(contract.base, commit) if contract.read_only(path)]


def verify(
    root: Path,
    commit: str,
    *,
    environment: Mapping[str, str],
    ref: str = DEFAULT_REF,
    council: Path = COUNCIL_DIR,
    ticket_ids: Iterable[str] = (),
    runner: Runner = Runner.LOCAL,
    run: CommandRunner = run_command,
    today: date | None = None,
) -> BuildRecord:
    """Judge `commit` against the build contract at its base, and return the record.

    `environment` is the whole environment each command gets. `ticket_ids` limits which
    tickets' steps run; every check always runs. Nothing is written here (`write_record`)."""
    git = Git(root)
    if not git.is_top_level():
        raise KilnError(
            "run the verifier at the top of the solution's repository, where git's paths begin",
            item=str(root),
        )
    sha = git.commit(commit, cause="the commit to verify is not here")
    contract = read_contract(git, find_base(git, sha, ref), council)
    chosen = _choose(contract.tickets, ticket_ids, contract.base)
    refused = refused_paths(git, contract, sha)
    if refused:
        checks: list[CheckResult] = []
        results = [TicketResult(id=t.id, passes=False, steps=[]) for t in chosen]
    else:
        with tempfile.TemporaryDirectory(prefix="kiln-verify-") as scratch:
            checkouts = _Checkouts(git, sha, Path(scratch), environment, run)
            checks = [
                CheckResult(name=c.name, tripwire=c.tripwire, **checkouts.ran(c).model_dump())
                for c in contract.tickets.checks
            ]
            green = all(check.passed for check in checks)
            results = [_ticket_result(t, green, checkouts) for t in chosen]
    return BuildRecord(
        version=2,
        verified_by=Actor.VERIFIER,
        verified_on=today or datetime.now(UTC).date(),
        runner=runner,
        ref=ref,
        base=contract.base,
        commit=sha,
        tickets_sha256=contract.tickets_sha256,
        plan_sha256=contract.plan_sha256,
        refused=refused,
        checks=checks,
        tickets=results,
    )


def _choose(tickets: TicketList, ids: Iterable[str], base: str) -> list[Ticket]:
    wanted = set(ids)
    missing = sorted(wanted - {t.id for t in tickets.tickets})
    if missing:
        raise KilnError(
            f"{missing[0]} is not in the ticket list at {base[:12]}; a ticket takes effect when "
            "Tom merges it",
            item=missing[0],
        )
    return [t for t in tickets.tickets if not wanted or t.id in wanted]


def _ticket_result(ticket: Ticket, green: bool, checkouts: _Checkouts) -> TicketResult:
    steps = [checkouts.ran(step) for step in ticket.steps]
    return TicketResult(id=ticket.id, passes=green and all(s.passed for s in steps), steps=steps)


class _Checkouts:
    """A fresh clone of the commit for each command, so no command sees another's changes."""

    def __init__(
        self,
        git: Git,
        commit: str,
        scratch: Path,
        environment: Mapping[str, str],
        run: CommandRunner,
    ) -> None:
        self.git, self.commit, self.scratch = git, commit, scratch
        self.environment, self.run = dict(environment), run
        self.count = 0

    def ran(self, command: Command) -> Ran:
        """Run `command` in its own checkout of the commit."""
        self.count += 1
        checkout = self.scratch / str(self.count)
        self.git.run("clone", "--quiet", "--no-checkout", "--shared", ".", str(checkout))
        Git(checkout).run("-c", "core.hooksPath=/dev/null", "checkout", "--quiet", self.commit)
        finished = self.run(command.run, checkout, self.environment, command.timeout_seconds)
        return Ran(
            run=command.run,
            exit_code=finished.exit_code,
            problem=finished.problem,
            output=None if finished.exit_code == 0 else _tail(finished.output, checkout),
        )


def _tail(output: str, checkout: Path) -> str:
    """The last lines of a command's output, with the scratch checkout's path made relative,
    so the record says the same thing wherever it ran."""
    text = output.replace(str(checkout.resolve()), ".").replace(str(checkout), ".")
    lines = text.rstrip("\n").splitlines()[-OUTPUT_LINES:]
    return "\n".join(line[:OUTPUT_LINE_CHARS] for line in lines) or "(no output)"


def environment_for(names: Iterable[str], environ: Mapping[str, str]) -> dict[str, str]:
    """The allowed variables that are set, and nothing else."""
    return {name: environ[name] for name in sorted(set(names)) if name in environ}


def render(record: BuildRecord) -> str:
    """The record, for a person to read: the verdict first, then each result."""
    lines = [
        f"{record.commit[:12]}, from {record.base[:12]} on {record.ref}, run {record.runner.value}:"
    ]
    if record.refused:
        lines.append("  refused: it changes what judges it, so none of its code ran")
        lines += [f"  - {path}" for path in record.refused]
    for check in record.checks:
        lines += _rendered(f"check {check.name}", check)
    for ticket in record.tickets:
        lines.append(f"  {ticket.id}: {'passes' if ticket.passes else 'does not pass'}")
        for number, step in enumerate(ticket.steps, start=1):
            lines += _rendered(f"  step {number}", step)
    return "\n".join(lines)


def _rendered(name: str, ran: Ran) -> list[str]:
    if ran.passed:
        return [f"  {name}: passed"]
    why = ran.problem or f"exited {ran.exit_code}"
    lines = [f"  {name}: failed ({why}): {' '.join(ran.run)}"]
    return lines + [f"      {line}" for line in (ran.output or "").splitlines()]


def write_record(root: Path, record: BuildRecord, council: Path = COUNCIL_DIR) -> Path:
    """Write the record to `council/build.yaml`, all at once."""
    path = root / council / BUILD
    write_atomic(path, RECORD_HEADER + front_matter(record))
    return path


def recheck(root: Path, record: BuildRecord, ref: str, council: Path = COUNCIL_DIR) -> list[str]:
    """Everything wrong with a record that history can show, without running any code.

    Its base must be on `ref`'s first-parent history and below its commit; the ticket list and
    plan it names must be the ones at that base; its refusals must be what that base and commit
    give; and every file the result depends on must be in the working tree as it was in the
    commit. A record that passes all of this can still hold forged results (module docstring)."""
    git = Git(root)
    try:
        for sha in (record.base, record.commit):
            git.commit(sha, cause="the record names a commit that is not here")
        tip = git.commit(ref, cause="the branch Tom merges into is not here")
        if record.base not in set(git.first_parent(tip)):
            return [f"its base, {record.base[:12]}, is not on {ref}'s first-parent history"]
        if not git.is_ancestor(record.base, record.commit):
            return [f"its base, {record.base[:12]}, is not below its commit"]
        contract = read_contract(git, record.base, council)
        problems: list[str] = []
        if contract.tickets_sha256 != record.tickets_sha256:
            problems.append(f"it names a ticket list other than the one at {record.base[:12]}")
        if contract.plan_sha256 != record.plan_sha256:
            problems.append(f"it names a plan other than the one at {record.base[:12]}")
        refused = refused_paths(git, contract, record.commit)
        if refused != record.refused:
            problems.append(
                f"it records the refusal of {record.refused or 'nothing'}, but history gives "
                f"{refused or 'nothing'}"
            )
        moved = sorted(
            path
            for path in {*git.changed(record.commit), *git.untracked()}
            if contract.judges(path)
        )
        if moved:
            problems.append(
                f"{_some(moved)} changed after the verifier ran on {record.commit[:12]}; run it "
                "again on the commit that holds them"
            )
        return problems
    except KilnError as exc:
        return [exc.one_line()]


def _some(paths: list[str], shown: int = 3) -> str:
    more = len(paths) - shown
    return ", ".join(paths[:shown]) + (f" and {more} more" if more > 0 else "")
