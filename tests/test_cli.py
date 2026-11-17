from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from kiln.cli import app
from tests.test_records import make_repo

runner = CliRunner()


def test_records_check_passes_on_agreeing_records(tmp_path: Path) -> None:
    """Why: exit 0 is what CI and the pre-commit hook key on."""
    result = runner.invoke(app, ["records", "check", "--root", str(make_repo(tmp_path))])
    assert result.exit_code == 0
    assert "Records agree." in result.output


def test_records_check_exits_2_and_names_each_problem(tmp_path: Path) -> None:
    """Why: failure is loud: exit code 2, the file, and where to read more."""
    root = make_repo(tmp_path)
    (root / "docs/handover.md").write_text("# Handover\n")
    result = runner.invoke(app, ["records", "check", "--root", str(root)])
    assert result.exit_code == 2
    assert "docs/handover.md" in result.output
    assert "see: CLAUDE.md" in result.output


def test_doctor_exits_2_on_a_bad_config_before_any_call(tmp_path: Path) -> None:
    """Why: a config error must stop the command before it reaches for the network."""
    bad = tmp_path / "kiln.yaml"
    bad.write_text("current_phase: 0\nservices: {}\nsurprise: true\n")
    result = runner.invoke(app, ["doctor", "--config", str(bad)])
    assert result.exit_code == 2
    assert "surprise" in result.output
