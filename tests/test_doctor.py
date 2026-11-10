from __future__ import annotations

from collections.abc import Callable

import httpx

from kiln.config import KilnConfig
from kiln.doctor import PLACEHOLDER_KEY, Status, blocking, render, run_checks

CONFIG = KilnConfig.model_validate(
    {
        "current_phase": 0,
        "services": {
            "bearer_api": {
                "purpose": "x",
                "needed_from_phase": 0,
                "probe": {
                    "base_url": "https://bearer.example.com",
                    "path": "/models",
                    "auth": {"scheme": "bearer", "env": "BEARER_KEY"},
                },
            },
            "header_api": {
                "purpose": "x",
                "needed_from_phase": 1,
                "probe": {
                    "base_url": "https://header.example.com",
                    "path": "/models",
                    "auth": {"scheme": "header", "header": "x-api-key", "env": "HEADER_KEY"},
                    "extra_headers": {"api-version": "1"},
                },
            },
            "basic_api": {
                "purpose": "x",
                "needed_from_phase": 0,
                "probe": {
                    "base_url": "https://basic.example.com",
                    "path": "/projects",
                    "auth": {
                        "scheme": "basic",
                        "env_user": "BASIC_USER",
                        "env_password": "BASIC_PASSWORD",
                    },
                },
            },
            "store": {"purpose": "x", "needed_from_phase": 0, "env": ["STORE_URL", "STORE_TOKEN"]},
        },
    }
)

Handler = Callable[[httpx.Request], httpx.Response]


def check(handler: Handler, env: dict[str, str]) -> dict[str, Status]:
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        return {c.service: c.status for c in run_checks(CONFIG, env, client)}


def always(status_code: int) -> Handler:
    return lambda _request: httpx.Response(status_code)


def test_a_service_that_answers_is_ok() -> None:
    """Why: the happy path, and the baseline for the failures below."""
    statuses = check(always(200), {"STORE_URL": "u", "STORE_TOKEN": "t"})
    assert statuses == {
        "bearer_api": Status.OK,
        "header_api": Status.OK,
        "basic_api": Status.OK,
        "store": Status.KEYS_PRESENT,
    }


def test_each_auth_scheme_sends_its_key_where_the_service_reads_it() -> None:
    """Why: a key in the wrong header looks like a bad key, which wastes a session."""
    seen: dict[str, httpx.Headers] = {}

    def record(request: httpx.Request) -> httpx.Response:
        seen[request.url.host] = request.headers
        return httpx.Response(200)

    check(
        record,
        {
            "BEARER_KEY": "b-key",
            "HEADER_KEY": "h-key",
            "BASIC_USER": "user",
            "BASIC_PASSWORD": "pass",
        },
    )
    assert seen["bearer.example.com"]["authorization"] == "Bearer b-key"
    assert seen["header.example.com"]["x-api-key"] == "h-key"
    assert seen["header.example.com"]["api-version"] == "1"
    assert seen["basic.example.com"]["authorization"] == "Basic dXNlcjpwYXNz"


def test_an_unset_key_sends_a_placeholder() -> None:
    """Why: in a cloud session the proxy injects the key, so an unset variable is normal
    there and the probe must still be sent."""
    seen: list[str] = []

    def record(request: httpx.Request) -> httpx.Response:
        seen.append(request.headers.get("authorization", request.headers.get("x-api-key", "")))
        return httpx.Response(200)

    check(record, {})
    assert all(PLACEHOLDER_KEY in value or value.startswith("Basic ") for value in seen)


def test_a_refused_key_is_unauthorised_and_names_the_variable() -> None:
    """Why: the fix for a 401 is a named secret, so the message must name it."""
    with httpx.Client(transport=httpx.MockTransport(always(401))) as client:
        checks = {c.service: c for c in run_checks(CONFIG, {}, client)}
    assert checks["bearer_api"].status is Status.UNAUTHORISED
    assert "BEARER_KEY" in checks["bearer_api"].detail


def test_a_server_error_is_an_error_not_a_pass() -> None:
    """Why: only a 2xx shows the service works with our credentials."""
    assert check(always(503), {})["bearer_api"] is Status.ERROR


def test_a_redirect_is_not_followed() -> None:
    """Why: a probe's credentials go only to the host named in config."""
    hosts: list[str] = []

    def redirect(request: httpx.Request) -> httpx.Response:
        hosts.append(request.url.host)
        return httpx.Response(302, headers={"location": "https://elsewhere.example.net/"})

    statuses = check(redirect, {})
    assert "elsewhere.example.net" not in hosts
    assert statuses["bearer_api"] is Status.ERROR


def test_a_host_that_cannot_be_reached_is_unreachable() -> None:
    """Why: a blocked host is the network policy's problem, not the key's."""

    def refuse(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("blocked", request=request)

    assert check(refuse, {})["bearer_api"] is Status.UNREACHABLE


def test_missing_variables_are_not_configured() -> None:
    """Why: a service with no client yet is checked by its key names alone."""
    with httpx.Client(transport=httpx.MockTransport(always(200))) as client:
        checks = {c.service: c for c in run_checks(CONFIG, {"STORE_URL": "u"}, client)}
    assert checks["store"].status is Status.NOT_CONFIGURED
    assert "STORE_TOKEN" in checks["store"].detail
    assert "STORE_URL" not in checks["store"].detail


def test_only_services_the_phase_needs_block_it() -> None:
    """Why: a phase 1 service that is down must not stop phase 0 work."""
    with httpx.Client(transport=httpx.MockTransport(always(401))) as client:
        checks = run_checks(CONFIG, {"STORE_URL": "u", "STORE_TOKEN": "t"}, client)
    assert {c.service for c in blocking(checks, phase=0)} == {"bearer_api", "basic_api"}
    assert {c.service for c in blocking(checks, phase=1)} == {
        "bearer_api",
        "basic_api",
        "header_api",
    }


def test_no_secret_value_reaches_the_report() -> None:
    """Why: secrets are never printed (tripwire 2)."""
    env = {
        "BEARER_KEY": "s3cret-bearer",
        "HEADER_KEY": "s3cret-header",
        "BASIC_USER": "s3cret-user",
        "BASIC_PASSWORD": "s3cret-pass",
        "STORE_URL": "s3cret-url",
        "STORE_TOKEN": "s3cret-token",
    }
    for status_code in (200, 401, 500):
        with httpx.Client(transport=httpx.MockTransport(always(status_code))) as client:
            checks = run_checks(CONFIG, env, client)
        report = render(checks, phase=0) + "".join(c.model_dump_json() for c in checks)
        assert "s3cret" not in report
