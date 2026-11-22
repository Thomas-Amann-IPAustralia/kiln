"""The `kiln` command line. Every command exits 0 on success and 2 on a failure to act on."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Annotated

import httpx
import typer

from kiln import approvals as approvals_module
from kiln import cards as cards_module
from kiln import doctor as doctor_module
from kiln import findings as findings_module
from kiln import gates as gates_module
from kiln import records as records_module
from kiln import review as review_module
from kiln import scanners as scanners_module
from kiln import spend as spend_module
from kiln import verifier as verifier_module
from kiln.artefacts import COUNCIL_DIR, Runner
from kiln.config import DEFAULT_CONFIG_PATH, load_config
from kiln.errors import EXIT_FAILURE, KilnError
from kiln.vocabulary import Actor, Basis

app = typer.Typer(no_args_is_help=True, add_completion=False, help="Kiln: the software factory.")
records_app = typer.Typer(no_args_is_help=True, help="The repo's records.")
app.add_typer(records_app, name="records")
spend_app = typer.Typer(help="The spend ledger: every paid call against a budget Tom set.")
app.add_typer(spend_app, name="spend")


def _fail(message: str) -> typer.Exit:
    typer.echo(f"error: {message}", err=True)
    return typer.Exit(EXIT_FAILURE)


@app.command()
def doctor(
    config_path: Annotated[
        Path, typer.Option("--config", help="Config file.")
    ] = DEFAULT_CONFIG_PATH,
    phase: Annotated[
        int | None, typer.Option(help="Check readiness for this phase, not the current one.")
    ] = None,
) -> None:
    """Check that every service the current build phase needs answers. Free; spends nothing."""
    try:
        config = load_config(config_path)
    except KilnError as exc:
        raise _fail(exc.one_line()) from exc
    target = config.current_phase if phase is None else phase
    with doctor_module.make_client(config.probe_timeout_seconds) as client:
        checks = doctor_module.run_checks(config, os.environ, client)
    typer.echo(doctor_module.render(checks, target))
    if doctor_module.blocking(checks, target):
        raise typer.Exit(EXIT_FAILURE)


@app.command()
def review(
    spec: Annotated[Path, typer.Argument(help="The review spec (YAML), committed first.")],
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Build the request and estimate it. Sends nothing.")
    ] = False,
    confirm: Annotated[
        bool, typer.Option("--confirm", help="Send the request. Spends money.")
    ] = False,
    print_request: Annotated[
        bool, typer.Option("--print-request", help="With --dry-run: print the exact body.")
    ] = False,
    config_path: Annotated[
        Path, typer.Option("--config", help="Config file.")
    ] = DEFAULT_CONFIG_PATH,
) -> None:
    """Ask another provider's model for a second opinion on documents. Paid."""
    if dry_run == confirm:
        raise _fail("pass exactly one of --dry-run (free) or --confirm (spends money)")
    root = Path()
    try:
        config = load_config(config_path)
        the_plan = review_module.plan(spec, config, root)
    except KilnError as exc:
        raise _fail(exc.one_line()) from exc
    left = the_plan.budget_usd - the_plan.spent_usd
    typer.echo(
        f"{spec}: request sha256:{the_plan.request_sha256[:12]}, "
        f"{len(the_plan.request['input']):,} characters of input\n"
        f"Estimate: up to ${the_plan.estimate.usd_bound:.4f} "
        f"({the_plan.estimate.input_tokens_bound:,} input and "
        f"{the_plan.estimate.output_tokens_bound:,} output tokens at most; assumes "
        f"{the_plan.estimate.assumes})\n"
        f"Budget {the_plan.budget!r}: ${the_plan.spent_usd:.4f} committed of "
        f"${the_plan.budget_usd:.2f}, ${left:.4f} left (kiln spend shows the ledger)"
        + ("\nCached: re-running costs nothing." if the_plan.cached else "")
    )
    if the_plan.warning:
        typer.echo(the_plan.warning, err=True)
    if dry_run:
        if print_request:
            typer.echo(json.dumps(the_plan.request, indent=2, ensure_ascii=False))
        return
    with httpx.Client(follow_redirects=False, trust_env=True) as client:
        try:
            record = review_module.run(the_plan, config, root, client)
        except KilnError as exc:
            raise _fail(exc.one_line()) from exc
    page = spec.with_suffix(".md")
    page.write_text(review_module.render(record), encoding="utf-8")
    typer.echo(f"Status {record.status}; cost ${record.usd:.4f}. Wrote {page}.")
    if record.status != "completed":
        raise _fail(
            f"the review did not complete ({record.incomplete_reason or record.status}); "
            "its cost is recorded | see: " + str(page)
        )


@records_app.command("render")
def records_render(
    root: Annotated[Path, typer.Option(help="Repo root.")] = Path(),
) -> None:
    """Rewrite each decision card as its canonical rendering, after editing its front matter."""
    try:
        changed = cards_module.render_cards(root)
    except KilnError as exc:
        raise _fail(exc.one_line()) from exc
    for path in changed:
        typer.echo(f"rendered {path}")
    if not changed:
        typer.echo("Every card is already its rendering.")


@app.command()
def approvals(
    ref: Annotated[
        str, typer.Option(help="The branch Tom merges into. Fetch it first.")
    ] = approvals_module.DEFAULT_REF,
    root: Annotated[Path, typer.Option(help="Repo root.")] = Path(),
) -> None:
    """List each decision card: open, awaiting Tom's merge, approved, lapsed or superseded.
    Exits 2 if an approval has lapsed, or a change here would lapse one. Free."""
    try:
        results = approvals_module.read_approvals(root, ref)
    except KilnError as exc:
        raise _fail(exc.one_line()) from exc
    typer.echo(approvals_module.render(results, ref))
    flagged = [result.card_id or result.path for result in results if result.needs_action]
    if flagged:
        raise _fail(
            f"{len(flagged)} card(s) need a new card or a fix: {', '.join(flagged)} | "
            "see: docs/adr/0028-only-tom-approves-or-merges.md"
        )


@app.command()
def gates(
    council: Annotated[Path, typer.Option(help="The solution's council folder.")] = COUNCIL_DIR,
    ref: Annotated[
        str, typer.Option(help="The branch Tom merges into. Fetch it first.")
    ] = approvals_module.DEFAULT_REF,
    root: Annotated[Path, typer.Option(help="The solution's repo root.")] = Path(),
) -> None:
    """Walk a solution's gates, G0 to G5, from its files and history as they are now.
    Exits 2 if a gate failed; waiting for work or for Tom is not a failure. Free."""
    try:
        outcomes = gates_module.run_gates(root, council, ref)
    except KilnError as exc:
        raise _fail(exc.one_line()) from exc
    typer.echo(gates_module.render(outcomes))
    failed = [o.gate.value for o in outcomes if o.status is gates_module.GateStatus.FAILED]
    if failed:
        raise _fail(f"{', '.join(failed)} failed | see: src/kiln/gates.py")


@app.command()
def verify(
    commit: Annotated[str, typer.Argument(help="The loop's commit.")],
    runner: Annotated[
        Runner,
        typer.Option(
            help="Where the commit's code runs. `local` is this machine, not a sandbox: use it "
            "only on code no agent wrote, or from inside a sandbox (ADR-0007).",
        ),
    ],
    ticket: Annotated[
        list[str] | None,
        typer.Option("--ticket", help="Run only this ticket's steps; repeat for more."),
    ] = None,
    ref: Annotated[
        str, typer.Option(help="The branch Tom merges into. Fetch it first.")
    ] = approvals_module.DEFAULT_REF,
    council: Annotated[Path, typer.Option(help="The solution's council folder.")] = COUNCIL_DIR,
    root: Annotated[Path, typer.Option(help="The solution's repo root.")] = Path(),
    config_path: Annotated[
        Path, typer.Option("--config", help="Config file.")
    ] = DEFAULT_CONFIG_PATH,
) -> None:
    """Verify a loop's commit and write each ticket's pass to council/build.yaml (ADR-0027).
    Runs the commit's code. Exits 2 if the commit is refused or a ticket does not pass. Free."""
    try:
        config = load_config(config_path)
        if config.verifier is None:
            raise KilnError("config has no `verifier` section", see="config/kiln.yaml")
        environment = verifier_module.environment_for(config.verifier.environment, os.environ)
        record = verifier_module.verify(
            root,
            commit,
            environment=environment,
            ref=ref,
            council=council,
            ticket_ids=ticket or [],
            runner=runner,
        )
        path = verifier_module.write_record(root, record, council)
    except KilnError as exc:
        raise _fail(exc.one_line()) from exc
    typer.echo(verifier_module.render(record))
    typer.echo(f"Wrote {path}.")
    if record.refused:
        raise _fail(
            f"refused {record.commit[:12]}: it changes what judges it, so none of its code ran | "
            "see: docs/adr/0027-an-independent-verifier-sets-a-pass.md"
        )
    failing = [t.id for t in record.tickets if not t.passes]
    if failing:
        raise _fail(f"{', '.join(failing)} did not pass at {record.commit[:12]} | see: {path}")


@app.command()
def scan(
    scanner: Annotated[findings_module.Scanner, typer.Argument(help="The scanner to run.")],
    seeded: Annotated[
        bool,
        typer.Option(
            "--seeded",
            help="Scan the planted finding instead, and succeed only if it is found.",
        ),
    ] = False,
    rules: Annotated[
        Path | None,
        typer.Option(help="Semgrep only: a checkout of the pinned rules commit."),
    ] = None,
    root: Annotated[Path, typer.Option(help="Repo root.")] = Path(),
    config_path: Annotated[
        Path, typer.Option("--config", help="Config file.")
    ] = DEFAULT_CONFIG_PATH,
) -> None:
    """Run one pinned scanner and report its findings in Kiln's one format. Exits 2 on an open
    finding at a blocking severity, or if the scanner did not run as pinned. Free."""
    try:
        config = load_config(config_path)
        report = scanners_module.scan(config, scanner, root, seeded=seeded, rules_dir=rules)
        assert config.scanners is not None  # scan() refuses a config without them
        dismissals = findings_module.load_dismissals(root / config.scanners.dismissals)
        assessment = findings_module.assess(report, dismissals, config.scanners.blocking)
    except KilnError as exc:
        raise _fail(exc.one_line()) from exc
    typer.echo(findings_module.render(assessment))
    if seeded:
        found = scanners_module.seeded_finding(report, config.scanners)
        if found is None:
            raise _fail(
                f"{scanner.value} did not report its seeded finding at a blocking severity, so "
                f"it is not detecting what it should | item: {report.target} | "
                "see: config/kiln.yaml, scanners"
            )
        typer.echo(
            f"Seeded finding detected: {found.rule} ({found.severity.value}) at "
            f"{found.location.where()}. {scanner.value} detects, and a finding like it fails CI."
        )
        return
    blocking = assessment.open_blocking
    if blocking:
        raise _fail(
            f"{len(blocking)} open finding(s) at a blocking severity from {scanner.value}; "
            "fix each, or dismiss it with a reason | see: config/dismissals.yaml"
        )


@spend_app.callback(invoke_without_command=True)
def spend_report(
    ctx: typer.Context,
    root: Annotated[Path, typer.Option(help="Repo root.")] = Path(),
    config_path: Annotated[
        Path, typer.Option("--config", help="Config file.")
    ] = DEFAULT_CONFIG_PATH,
) -> None:
    """Show where each budget stands, and any reservation still open. Exits 2 if tripwire 4
    (spend over budget) has tripped. Free."""
    if ctx.invoked_subcommand is not None:
        return
    try:
        config = load_config(config_path)
        ledger = spend_module.read_ledger(root / config.spend.ledger)
    except KilnError as exc:
        raise _fail(exc.one_line()) from exc
    typer.echo(spend_module.render(config, ledger))
    tripped = [p.budget for p in spend_module.positions(config, ledger) if p.tripped]
    if tripped:
        raise _fail(
            f"tripwire 4: spend is over budget on {', '.join(tripped)}; stop and ask Tom | "
            "see: AGENTS.md, 'Authority and money'"
        )


@spend_app.command("settle")
def spend_settle(
    reservation: Annotated[int, typer.Argument(help="The open reservation's entry number.")],
    usd: Annotated[float, typer.Option(help="What the call really cost, in US dollars.")],
    outcome: Annotated[str, typer.Option(help="What happened to the call.")],
    note: Annotated[str, typer.Option(help="Where the cost was read, such as a usage page.")],
    basis: Annotated[Basis, typer.Option(help="How the cost is known.")] = Basis.OBSERVED,
    root: Annotated[Path, typer.Option(help="Repo root.")] = Path(),
    config_path: Annotated[
        Path, typer.Option("--config", help="Config file.")
    ] = DEFAULT_CONFIG_PATH,
) -> None:
    """Settle a reservation a paid command left open, such as a call that timed out after it
    was sent, from the provider's own record of the cost. Free."""
    try:
        config = load_config(config_path)
        settled = spend_module.settle(
            root,
            config,
            reservation,
            usd=usd,
            outcome=outcome,
            basis=basis,
            by=Actor.BUILD_SESSION,
            note=note,
        )
    except KilnError as exc:
        raise _fail(exc.one_line()) from exc
    typer.echo(f"Settled reservation {reservation} at ${settled.usd:.4f} (entry {settled.entry}).")


@records_app.command("check")
def records_check(
    root: Annotated[Path, typer.Option(help="Repo root.")] = Path(),
) -> None:
    """Check the decision log, the ADRs, the handover, the sealed seeds and the docs' links."""
    problems = records_module.check_all(root)
    for problem in problems:
        typer.echo(problem.one_line(), err=True)
    if problems:
        raise _fail(f"{len(problems)} problem(s) in the records | see: CLAUDE.md, 'Records'")
    typer.echo("Records agree.")
