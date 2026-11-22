"""A synthetic build contract and a loop's work on it, shared by the verifier and gate tests.

The solution greets a person by name. Its fitness function, under `council/fitness/`, checks the
greeting; a loop's job is `src/greeting.py`. Placeholder text throughout: no real source text and
no real data.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

from tests.gitrepo import Repo

PYTHON = sys.executable
"""The interpreter running the tests, by absolute path, so a step needs nothing from PATH."""

FITNESS = "council/fitness/check_greeting.py"
FITNESS_TEXT = '''"""Placeholder fitness function: the greeting names the person."""
import sys

sys.path.insert(0, "src")
from greeting import greet

assert greet("Placeholder") == "Hello, Placeholder.", greet("Placeholder")
'''
GREETING = "src/greeting.py"
RIGHT = 'def greet(name):\n    return f"Hello, {name}."\n'
WRONG = 'def greet(name):\n    return "Hello."\n'

STEP: dict[str, Any] = {"description": "The greeting names the person.", "run": [PYTHON, FITNESS]}
COMPILES: dict[str, Any] = {"name": "compiles", "run": [PYTHON, "-m", "compileall", "-q", "src"]}


def ticket(number: int, steps: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "id": f"TKT-{number:04d}",
        "title": f"Placeholder ticket {number}",
        "description": "Placeholder: greet a person by name.",
        "contract": "ux",
        "steps": steps or [STEP],
    }


def ticket_list(
    checks: list[dict[str, Any]] | None = None,
    tickets: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "version": 1,
        "checks": checks or [COMPILES],
        "read_only": ["conftest.py"],
        "tickets": tickets or [ticket(1)],
    }


def marks(marker: Path) -> dict[str, Any]:
    """A check that leaves a file outside the checkout, to show whether anything ran."""
    return {"name": "marks", "run": [PYTHON, "-c", f"open({str(marker)!r}, 'a').close()"]}


def write_tickets(repo: Repo, data: dict[str, Any]) -> None:
    repo.write("council/tickets.json", json.dumps(data, indent=2) + "\n")


def write_build_contract(repo: Repo, tickets: dict[str, Any]) -> None:
    """The tickets, the fitness function they run, and the code a loop starts from."""
    write_tickets(repo, tickets)
    repo.write(FITNESS, FITNESS_TEXT)
    repo.write(GREETING, WRONG)


def write_plan(repo: Repo, plan: dict[str, Any]) -> None:
    repo.write("council/plan.yaml", yaml.safe_dump(plan, sort_keys=False))
