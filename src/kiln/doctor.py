"""`kiln doctor`: is this machine ready for the current build phase?

One free, read-only call per HTTP service, and a presence check for services whose client has
not been built yet. Nothing here spends money, and no secret value is ever printed or returned.

Tools prove presence, not absence (charter rule 6): `keys_present` means the variables are set,
not that the service accepts them.
"""

from __future__ import annotations

import base64
from collections.abc import Mapping
from enum import StrEnum

import httpx
from pydantic import BaseModel, ConfigDict

from kiln.config import BasicAuth, BearerAuth, HttpProbe, KilnConfig, Service

# Sent when a key's variable is unset. A cloud session's proxy replaces it with the real key;
# anywhere else the service answers 401 and the check reports `unauthorised`.
PLACEHOLDER_KEY = "placeholder-replaced-by-session-proxy"


class Status(StrEnum):
    OK = "ok"
    KEYS_PRESENT = "keys_present"
    NOT_CONFIGURED = "not_configured"
    UNAUTHORISED = "unauthorised"
    UNREACHABLE = "unreachable"
    ERROR = "error"


READY = frozenset({Status.OK, Status.KEYS_PRESENT})


class Check(BaseModel):
    """The outcome of checking one service."""

    model_config = ConfigDict(frozen=True)

    service: str
    status: Status
    needed_from_phase: int
    detail: str

    @property
    def ready(self) -> bool:
        return self.status in READY


def _auth_headers(probe: HttpProbe, env: Mapping[str, str]) -> tuple[dict[str, str], bool]:
    """Build the auth headers, and say whether every key came from the environment."""
    auth = probe.auth
    if isinstance(auth, BasicAuth):
        user, password = env.get(auth.env_user), env.get(auth.env_password)
        pair = f"{user or PLACEHOLDER_KEY}:{password or PLACEHOLDER_KEY}".encode()
        return {"Authorization": "Basic " + base64.b64encode(pair).decode()}, bool(
            user and password
        )
    key = env.get(auth.env)
    if isinstance(auth, BearerAuth):
        return {"Authorization": f"Bearer {key or PLACEHOLDER_KEY}"}, bool(key)
    return {auth.header: key or PLACEHOLDER_KEY}, bool(key)


def _check_http(
    name: str, service: Service, probe: HttpProbe, client: httpx.Client, env: Mapping[str, str]
) -> Check:
    headers, from_env = _auth_headers(probe, env)
    key_source = "key from the environment" if from_env else "placeholder key"

    def result(status: Status, detail: str) -> Check:
        return Check(
            service=name, status=status, needed_from_phase=service.needed_from_phase, detail=detail
        )

    try:
        response = client.get(
            probe.base_url + probe.path, headers={**probe.extra_headers, **headers}
        )
    except httpx.HTTPError as exc:
        return result(Status.UNREACHABLE, f"{type(exc).__name__} reaching {probe.base_url}")
    if response.is_success:
        return result(Status.OK, f"HTTP {response.status_code}, {key_source}")
    if response.status_code in (401, 403):
        names = ", ".join(service.env_names())
        return result(
            Status.UNAUTHORISED, f"HTTP {response.status_code}, {key_source}; set {names}"
        )
    return result(Status.ERROR, f"HTTP {response.status_code} from {probe.base_url}{probe.path}")


def _check_env(name: str, service: Service, env: Mapping[str, str]) -> Check:
    missing = [var for var in service.env if not env.get(var)]
    if missing:
        status, detail = Status.NOT_CONFIGURED, "unset: " + ", ".join(missing)
    else:
        status, detail = Status.KEYS_PRESENT, "variables set; no live check until its client exists"
    return Check(
        service=name, status=status, needed_from_phase=service.needed_from_phase, detail=detail
    )


def run_checks(config: KilnConfig, env: Mapping[str, str], client: httpx.Client) -> list[Check]:
    """Check every configured service, in name order."""
    checks: list[Check] = []
    for name in sorted(config.services):
        service = config.services[name]
        if service.probe is None:
            checks.append(_check_env(name, service, env))
        else:
            checks.append(_check_http(name, service, service.probe, client, env))
    return checks


def blocking(checks: list[Check], phase: int) -> list[Check]:
    """The checks that stop work in `phase`: services it needs that are not ready."""
    return [check for check in checks if check.needed_from_phase <= phase and not check.ready]


def make_client(timeout_seconds: float) -> httpx.Client:
    """A client for probes: it honours the session's proxy and CA bundle, and never follows a
    redirect, so a probe's credentials go only to the host named in config."""
    return httpx.Client(timeout=timeout_seconds, follow_redirects=False, trust_env=True)


def render(checks: list[Check], phase: int) -> str:
    """A plain table, readable on a phone."""
    width = max(len(check.service) for check in checks)
    status_width = max(len(check.status) for check in checks)
    lines = [f"Environment check for phase {phase}:"]
    for check in checks:
        marker = " " if check.ready else ("!" if check.needed_from_phase <= phase else "-")
        lines.append(
            f"{marker} {check.service:<{width}}  {check.status:<{status_width}}  "
            f"phase {check.needed_from_phase}+  {check.detail}"
        )
    stopped = blocking(checks, phase)
    if stopped:
        lines.append(f"Not ready for phase {phase}: " + ", ".join(c.service for c in stopped))
    else:
        lines.append(f"Ready for phase {phase}.")
    return "\n".join(lines)
