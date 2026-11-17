"""Load and validate config/kiln.yaml.

Behaviour is tuned in config, not in code, and an unknown key is an error: a typo must never
become a silently ignored setting.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from kiln.errors import KilnError

DEFAULT_CONFIG_PATH = Path("config/kiln.yaml")

EnvName = Annotated[str, Field(pattern=r"^[A-Z][A-Z0-9_]*$")]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class BearerAuth(_Strict):
    """`Authorization: Bearer <key>`."""

    scheme: Literal["bearer"]
    env: EnvName


class HeaderAuth(_Strict):
    """The key travels in a named header, such as `x-goog-api-key`."""

    scheme: Literal["header"]
    header: Annotated[str, Field(pattern=r"^[A-Za-z][A-Za-z0-9-]*$")]
    env: EnvName


class BasicAuth(_Strict):
    """HTTP basic auth from two environment variables."""

    scheme: Literal["basic"]
    env_user: EnvName
    env_password: EnvName


Auth = Annotated[BearerAuth | HeaderAuth | BasicAuth, Field(discriminator="scheme")]


class HttpProbe(_Strict):
    """One free, read-only GET that shows a service answers with our credentials.

    The base URL comes from here and nowhere else, so an ambient variable such as
    `OPENAI_BASE_URL` cannot redirect a call (CLAUDE.md, security rules).
    """

    base_url: Annotated[str, Field(pattern=r"^https://[a-z0-9.-]+$")]
    path: Annotated[str, Field(pattern=r"^/")]
    auth: Auth
    extra_headers: dict[str, str] = Field(default_factory=dict)


class Service(_Strict):
    """An outside service Kiln depends on, and the first build phase that needs it."""

    purpose: str
    needed_from_phase: Annotated[int, Field(ge=0, le=5)]
    probe: HttpProbe | None = None
    env: tuple[EnvName, ...] = ()

    @model_validator(mode="after")
    def _probe_or_env(self) -> Service:
        if (self.probe is None) == (not self.env):
            raise ValueError("give exactly one of `probe` (an HTTP check) or `env` (key names)")
        return self

    def env_names(self) -> tuple[str, ...]:
        """Every environment variable this service reads."""
        if self.probe is None:
            return self.env
        auth = self.probe.auth
        if isinstance(auth, BasicAuth):
            return (auth.env_user, auth.env_password)
        return (auth.env,)


Name = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]*$")]
Usd = Annotated[float, Field(ge=0)]


class Prices(_Strict):
    """US dollars per million tokens, as the provider's own pricing page shows them."""

    input: Usd
    cached_input: Usd
    output: Usd


class Model(_Strict):
    """A model Kiln may call, through a configured service.

    Prices are copied from the provider's page by hand, with the date and page they came from,
    because no provider serves them through its API. A paid command refuses a model whose
    prices are not configured, so a spend can always be computed (SOP §14.1).
    """

    service: Name
    model: Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9.-]*$")]
    effort: Literal["none", "minimal", "low", "medium", "high", "xhigh", "max"]
    max_output_tokens: Annotated[int, Field(gt=0, le=200_000)]
    request_timeout_seconds: Annotated[float, Field(gt=0, le=1800)] = 600.0
    usd_per_million_tokens: Prices
    prices_valid_up_to_input_tokens: Annotated[int, Field(gt=0)]
    """Providers charge more above a context size. A request above it is refused, not
    mispriced."""
    prices_checked: str


class Budget(_Strict):
    """A cap in dollars that Tom set, with his words and the date. Code enforces it."""

    usd: Annotated[float, Field(gt=0)]
    approved: str


class KilnConfig(_Strict):
    current_phase: Annotated[int, Field(ge=0, le=5)]
    probe_timeout_seconds: Annotated[float, Field(gt=0, le=60)] = 20.0
    services: dict[Name, Service]
    models: dict[Name, Model] = Field(default_factory=dict)
    budgets: dict[Name, Budget] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _models_name_http_services(self) -> KilnConfig:
        for name, model in self.models.items():
            service = self.services.get(model.service)
            if service is None or service.probe is None:
                raise ValueError(
                    f"model {name!r} names service {model.service!r}, "
                    "which is not an HTTP service in `services`"
                )
        return self


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> KilnConfig:
    """Read the config file, or raise a `KilnError` that names what is wrong with it."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise KilnError("config file not found", item=str(path), see="README.md") from exc
    except yaml.YAMLError as exc:
        raise KilnError(f"config is not valid YAML: {exc}", item=str(path)) from exc
    try:
        return KilnConfig.model_validate(raw)
    except ValidationError as exc:
        first = exc.errors()[0]
        where = ".".join(str(part) for part in first["loc"])
        raise KilnError(
            f"config is invalid ({exc.error_count()} problem(s)); first: {where}: {first['msg']}",
            item=str(path),
            see="src/kiln/config.py",
        ) from exc
