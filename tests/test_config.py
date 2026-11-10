from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from kiln.config import load_config
from kiln.errors import KilnError

VALID = {
    "current_phase": 0,
    "services": {
        "example": {
            "purpose": "An HTTP service.",
            "needed_from_phase": 0,
            "probe": {
                "base_url": "https://api.example.com",
                "path": "/v1/ping",
                "auth": {"scheme": "bearer", "env": "EXAMPLE_API_KEY"},
            },
        },
        "store": {
            "purpose": "A service with no client yet.",
            "needed_from_phase": 1,
            "env": ["STORE_URL"],
        },
    },
}


def write(tmp_path: Path, data: object) -> Path:
    path = tmp_path / "kiln.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def test_the_committed_config_loads(repo_root: Path) -> None:
    """Why: a config that fails validation should fail in CI, not in the next session."""
    config = load_config(repo_root / "config/kiln.yaml")
    assert config.services


def test_a_valid_config_round_trips(tmp_path: Path) -> None:
    """Why: the fixture below is the baseline every rejection test mutates."""
    config = load_config(write(tmp_path, VALID))
    assert config.services["example"].env_names() == ("EXAMPLE_API_KEY",)
    assert config.services["store"].env_names() == ("STORE_URL",)


def test_an_unknown_key_is_an_error(tmp_path: Path) -> None:
    """Why: a typo must never become a silently ignored setting."""
    data = {**VALID, "curent_phase": 1}
    with pytest.raises(KilnError, match="curent_phase"):
        load_config(write(tmp_path, data))


def test_a_plain_http_base_url_is_refused(tmp_path: Path) -> None:
    """Why: probes carry credentials, so they only ever go over TLS."""
    data = yaml.safe_load(yaml.safe_dump(VALID))
    data["services"]["example"]["probe"]["base_url"] = "http://api.example.com"
    with pytest.raises(KilnError, match="base_url"):
        load_config(write(tmp_path, data))


def test_a_service_needs_exactly_one_kind_of_check(tmp_path: Path) -> None:
    """Why: a service with neither a probe nor key names would always look ready."""
    data = yaml.safe_load(yaml.safe_dump(VALID))
    del data["services"]["store"]["env"]
    with pytest.raises(KilnError, match="exactly one"):
        load_config(write(tmp_path, data))


def test_a_missing_file_names_the_path(tmp_path: Path) -> None:
    """Why: failure is loud and says which item to look at."""
    with pytest.raises(KilnError) as raised:
        load_config(tmp_path / "absent.yaml")
    assert "absent.yaml" in raised.value.one_line()
