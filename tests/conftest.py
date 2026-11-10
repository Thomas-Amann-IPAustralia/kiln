"""Shared fixtures. Tests never touch the network: CI has none, and a test that needs one
is measuring someone else's service."""

from __future__ import annotations

import socket
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def no_network(monkeypatch: pytest.MonkeyPatch) -> None:  # pyright: ignore[reportUnusedFunction]
    """Make any real connection attempt fail the test that made it."""

    def refuse(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("a test tried to open a network connection")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket.socket, "connect_ex", refuse)


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT
