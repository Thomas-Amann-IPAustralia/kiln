"""The `kiln` command line. Every command exits 0 on success and 2 on a failure to act on."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import typer

from kiln import doctor as doctor_module
from kiln import records as records_module
from kiln.config import DEFAULT_CONFIG_PATH, load_config
from kiln.errors import EXIT_FAILURE, KilnError

app = typer.Typer(no_args_is_help=True, add_completion=False, help="Kiln: the software factory.")
records_app = typer.Typer(no_args_is_help=True, help="The repo's records.")
app.add_typer(records_app, name="records")


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
