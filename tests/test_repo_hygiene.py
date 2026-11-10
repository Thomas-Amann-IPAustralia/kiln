"""The repo is part of the Council's control plane, so its hygiene is tested, not assumed."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from kiln.config import load_config

# High-confidence shapes only. Gitleaks is the real control (it runs in CI and pre-commit);
# this is the net that needs no extra binary. A clean run means "nothing detected by these
# patterns", never "no secrets".
SECRET_PATTERNS = {
    "private key block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "AWS access key id": re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    "OpenAI-style key": re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b"),
    "Anthropic key": re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"),
    "Langfuse key": re.compile(r"\b[sp]k-lf-[0-9a-f]{8}-[0-9a-f-]{20,}\b"),
    "GitHub token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,})\b"),
    "Google API key": re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    "Postgres URL with password": re.compile(r"postgres(?:ql)?://[^\s:@/]+:[^\s@/]{6,}@"),
}


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
    ).stdout


@pytest.fixture(scope="module")
def tracked(repo_root: Path) -> list[Path]:
    return [repo_root / name for name in git(repo_root, "ls-files", "-z").split("\0") if name]


def test_no_tracked_file_holds_a_secret(tracked: list[Path], repo_root: Path) -> None:
    """Why: a committed secret is tripwire 2, and cannot be un-published."""
    found: list[str] = []
    for path in tracked:
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        found += [
            f"{path.relative_to(repo_root)}: {name}"
            for name, pattern in SECRET_PATTERNS.items()
            if pattern.search(text)
        ]
    assert found == []


@pytest.mark.parametrize("name", [".env", ".env.local", "sub/.env"])
def test_env_files_are_ignored(repo_root: Path, name: str) -> None:
    """Why: `.env` is where real keys live on a developer machine."""
    ignored = subprocess.run(
        ["git", "-C", str(repo_root), "check-ignore", "-q", name], check=False
    ).returncode
    assert ignored == 0


def test_env_example_is_tracked_and_holds_names_only(repo_root: Path) -> None:
    """Why: the example documents which keys exist without ever holding one."""
    assert git(repo_root, "ls-files", ".env.example").strip() == ".env.example"
    for line in (repo_root / ".env.example").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            assert re.fullmatch(r"[A-Z][A-Z0-9_]*=", line), f"value or bad name in: {line!r}"


def test_env_example_and_config_name_the_same_keys(repo_root: Path) -> None:
    """Why: a key declared in one place and not the other is a session lost to a 401."""
    config = load_config(repo_root / "config/kiln.yaml")
    declared = {name for service in config.services.values() for name in service.env_names()}
    example = {
        line.split("=", 1)[0]
        for line in (repo_root / ".env.example").read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    }
    assert example == declared


def test_workflow_actions_are_pinned_to_a_commit(repo_root: Path) -> None:
    """Why: a tag can be moved to new code; a full commit SHA cannot."""
    uses = re.compile(r"^\s*(?:-\s+)?uses:\s*(\S+)", re.MULTILINE)
    pinned = re.compile(r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")
    workflows = sorted((repo_root / ".github/workflows").glob("*.y*ml"))
    assert workflows, "CI is missing"
    for workflow in workflows:
        for action in uses.findall(workflow.read_text(encoding="utf-8")):
            assert pinned.match(action), f"{workflow.name}: {action} is not pinned to a SHA"


def test_workflows_default_to_read_only_tokens(repo_root: Path) -> None:
    """Why: a workflow token should hold the least privilege that does its job."""
    for workflow in sorted((repo_root / ".github/workflows").glob("*.y*ml")):
        text = workflow.read_text(encoding="utf-8")
        assert re.search(r"^permissions:\s*\n\s+contents: read\s*$", text, re.MULTILINE), (
            f"{workflow.name} does not set top-level `permissions: contents: read`"
        )
        assert "pull_request_target" not in text, (
            f"{workflow.name} runs privileged on untrusted pull requests"
        )
