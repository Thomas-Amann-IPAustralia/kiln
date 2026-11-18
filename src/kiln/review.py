"""`kiln review`: ask a model from another provider for a second opinion on documents.

A review is described by a spec file (YAML) that is committed before the run: the question,
the documents (each pinned to a git revision), the model and the budget. One spec is one
request. The command follows the SOP's money rules (§14.1):

- `--dry-run` builds the exact request and prints an upper-bound estimate. It sends nothing.
- `--confirm` is required to send. The request's upper bound is reserved in the spend ledger
  first (`kiln.spend`), which refuses it if the budget's committed spend and the bound could
  pass the cap in config, and warns at 80%. The reservation is settled at the real cost.
- Every response is cached under the hash of the request that produced it, and the cache is
  committed. Re-running a spec whose request has not changed spends nothing.
- The cost is computed from the provider's reported usage and the prices in config, and
  recorded with the response and in the ledger, failed and truncated responses included. A
  response that reports no usage is charged at its bound: unknown is never counted as free.

Documents are untrusted data to the reviewer: each sits in its own block, defanged so that
its text cannot close the block or open a new one, and the instructions say so.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
from collections.abc import Mapping
from pathlib import Path
from typing import Annotated, Any, cast

import httpx
import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from kiln import spend
from kiln.config import BasicAuth, BearerAuth, KilnConfig, Model, Prices
from kiln.doctor import PLACEHOLDER_KEY
from kiln.errors import KilnError
from kiln.vocabulary import Actor, Basis

CACHE_DIR = Path("docs/reviews/cache")
RESPONSES_PATH = "/v1/responses"

# A conservative bound for the estimate: English Markdown runs near 4 characters a token for
# OpenAI's tokenizers, so counting 3 overestimates the input. The run records the real count.
CHARS_PER_TOKEN_BOUND = 3

_REVISION = Annotated[str, Field(pattern=r"^[0-9a-f]{7,40}$")]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Document(_Strict):
    """One file, as it stood at a git revision, or one section of it."""

    path: str
    revision: _REVISION | None = None
    section: str | None = None
    """A heading line, such as `## D-006`. Only that heading and its body are sent."""


class ReviewSpec(_Strict):
    model: str
    budget: str
    revision: _REVISION
    """The default revision for every document: what the reviewer sees is fixed in git."""
    instructions: str
    question: str
    documents: tuple[Document, ...] = Field(min_length=1)
    redact: dict[str, str] = Field(default_factory=dict)
    """Literal strings replaced before anything leaves the machine, such as a GitHub handle."""


class Usage(_Strict):
    """Input buckets are exclusive: uncached = input - cached - both kinds of cache write.
    The cache-write fields default to 0 so that records made before they existed still load."""

    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    reasoning_tokens: int
    cache_write_tokens: int = 0
    cache_write_long_tokens: int = 0


class Estimate(_Strict):
    input_tokens_bound: int
    output_tokens_bound: int
    usd_bound: float
    assumes: str


class ReviewRecord(BaseModel):
    """Everything about one paid request: what was sent, what came back, what it cost."""

    model_config = ConfigDict(extra="forbid")

    request_sha256: str
    spec: str
    budget: str
    model: str
    effort: str
    request: dict[str, Any]
    http_status: int
    status: str
    incomplete_reason: str | None
    usage: Usage | None
    usd: float
    estimate: Estimate
    answer: str
    response: dict[str, Any] | None


def load_spec(path: Path) -> ReviewSpec:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise KilnError("review spec not found", item=str(path)) from exc
    try:
        return ReviewSpec.model_validate(raw)
    except ValidationError as exc:
        first = exc.errors()[0]
        where = ".".join(str(part) for part in first["loc"])
        raise KilnError(
            f"review spec is invalid; first: {where}: {first['msg']}", item=str(path)
        ) from exc


def _git_show(root: Path, revision: str, path: str) -> str:
    result = subprocess.run(  # noqa: S603 (fixed argv, no shell)
        ["git", "-C", str(root), "show", f"{revision}:{path}"],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise KilnError(f"cannot read {path} at {revision}: {result.stderr.strip()}", item=path)
    return result.stdout


def _section(text: str, heading: str, path: str) -> str:
    """The lines from `heading` up to the next heading of the same or a higher level."""
    level = len(heading) - len(heading.lstrip("#"))
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith(heading)), None)
    if start is None:
        raise KilnError(f"no heading starting {heading!r}", item=path)
    end = len(lines)
    for i in range(start + 1, len(lines)):
        match = re.match(r"^(#+) ", lines[i])
        if match and len(match.group(1)) <= level:
            end = i
            break
    return "\n".join(lines[start:end]).strip() + "\n"


def defang(text: str) -> str:
    """Stop document text from closing its block or opening a new one."""
    return re.sub(r"<(/?)(documents?)\b", r"&lt;\1\2", text, flags=re.IGNORECASE)


def _redact(text: str, redact: Mapping[str, str]) -> str:
    for secret, replacement in sorted(redact.items()):
        text = text.replace(secret, replacement)
    return text


def build_input(spec: ReviewSpec, root: Path) -> str:
    """The documents, each in its own defanged block, then the question last."""
    blocks: list[str] = []
    for document in spec.documents:
        revision = document.revision or spec.revision
        text = _git_show(root, revision, document.path)
        if document.section:
            text = _section(text, document.section, document.path)
        label = f' section="{document.section}"' if document.section else ""
        blocks.append(
            f'<document path="{document.path}" revision="{revision}"{label}>\n'
            f"{defang(_redact(text, spec.redact))}\n</document>"
        )
    question = _redact(spec.question, spec.redact)
    return "<documents>\n" + "\n\n".join(blocks) + "\n</documents>\n\n" + question.strip() + "\n"


def build_request(spec: ReviewSpec, model: Model, root: Path) -> dict[str, Any]:
    """The exact body sent to the Responses API.

    `store: false` stops OpenAI storing the response for later retrieval. It does not by itself
    mean zero retention: abuse-monitoring retention and the account's data controls are
    separate, and are checked per provider before real data is ever sent (D-007).
    """
    return {
        "model": model.model,
        "instructions": _redact(spec.instructions, spec.redact).strip(),
        "input": build_input(spec, root),
        "max_output_tokens": model.max_output_tokens,
        "reasoning": {"effort": model.effort},
        "store": False,
    }


def request_hash(request: Mapping[str, Any]) -> str:
    canonical = json.dumps(request, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def estimate(request: Mapping[str, Any], prices: Prices) -> Estimate:
    chars = len(request["instructions"]) + len(request["input"])
    input_bound = chars // CHARS_PER_TOKEN_BOUND + 1
    output_bound = int(request["max_output_tokens"])
    input_rate = max(prices.input, prices.cache_write)
    usd = (input_bound * input_rate + output_bound * prices.output) / 1_000_000
    return Estimate(
        input_tokens_bound=input_bound,
        output_tokens_bound=output_bound,
        usd_bound=math.ceil(usd * 1_000_000) / 1_000_000,  # a bound never rounds down
        assumes=(
            f"input at {CHARS_PER_TOKEN_BOUND} characters a token, all of it written to the "
            "default cache and none read from it; every output token used, reasoning "
            "included, at the output price"
        ),
    )


def cost(usage: Usage, prices: Prices) -> float:
    """Exclusive buckets: uncached input, cache reads, cache writes (two lifetimes) and output.
    Reasoning tokens are inside output, so they are not counted again."""
    written = usage.cache_write_tokens + usage.cache_write_long_tokens
    uncached = usage.input_tokens - usage.cached_input_tokens - written
    if uncached < 0:
        raise KilnError("the provider's usage buckets add up to more than its input tokens")
    usd = (
        uncached * prices.input
        + usage.cached_input_tokens * prices.cached_input
        + usage.cache_write_tokens * prices.cache_write
        + usage.cache_write_long_tokens * prices.cache_write_long
        + usage.output_tokens * prices.output
    ) / 1_000_000
    return round(usd, 6)


def _obj(value: object) -> dict[str, Any]:
    """A JSON object from the provider, or an empty one: its shape is checked, not trusted."""
    return cast(dict[str, Any], value) if isinstance(value, dict) else {}


def _list(value: object) -> list[Any]:
    return cast(list[Any], value) if isinstance(value, list) else []


def _usage(body: Mapping[str, Any]) -> Usage | None:
    usage = _obj(body.get("usage"))
    if not usage:
        return None
    input_details = _obj(usage.get("input_tokens_details"))
    output_details = _obj(usage.get("output_tokens_details"))
    writes = int(input_details.get("cache_write_tokens", 0))
    lifetimes = _obj(input_details.get("cache_write_tokens_details"))
    long_writes = int(lifetimes.get("ttl_12h_tokens", 0))
    return Usage(
        input_tokens=int(usage.get("input_tokens", 0)),
        cached_input_tokens=int(input_details.get("cached_tokens", 0)),
        output_tokens=int(usage.get("output_tokens", 0)),
        reasoning_tokens=int(output_details.get("reasoning_tokens", 0)),
        # Without a breakdown, every write is priced at the default lifetime's rate.
        cache_write_tokens=writes - long_writes,
        cache_write_long_tokens=long_writes,
    )


def _answer(body: Mapping[str, Any]) -> str:
    parts: list[str] = []
    for item in map(_obj, _list(body.get("output"))):
        if item.get("type") != "message":
            continue
        for part in map(_obj, _list(item.get("content"))):
            if part.get("type") == "output_text":
                parts.append(str(part.get("text", "")))
    return "\n".join(parts).strip()


def cache_path(root: Path, digest: str) -> Path:
    return root / CACHE_DIR / f"{digest}.json"


def cached_records(root: Path) -> list[tuple[str, ReviewRecord]]:
    """Every cached response, with its repo path, in path order."""
    directory = root / CACHE_DIR
    if not directory.is_dir():
        return []
    return [
        (
            (CACHE_DIR / path.name).as_posix(),
            ReviewRecord.model_validate_json(path.read_text(encoding="utf-8")),
        )
        for path in sorted(directory.glob("*.json"))
    ]


# Errors raised before a request reached the provider, so nothing can have been billed. Any
# other transport error may come after the provider received the request.
_NOT_SENT = (httpx.ConnectError, httpx.ConnectTimeout, httpx.PoolTimeout, httpx.ProxyError)


def _write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def _auth_headers(config: KilnConfig, model: Model, env: Mapping[str, str]) -> dict[str, str]:
    probe = config.services[model.service].probe
    assert probe is not None  # guaranteed by KilnConfig's validator
    auth = probe.auth
    if isinstance(auth, BasicAuth):
        raise KilnError(f"service {model.service!r} uses basic auth, which no model API takes")
    key = env.get(auth.env) or PLACEHOLDER_KEY
    if isinstance(auth, BearerAuth):
        return {"Authorization": f"Bearer {key}"}
    return {auth.header: key}


class Plan(_Strict):
    """What a review would send and what it may cost, before anything is sent."""

    spec_path: str
    model: str
    request_sha256: str
    request: dict[str, Any]
    estimate: Estimate
    budget: str
    budget_usd: float
    spent_usd: float
    """Committed against the budget: settled costs, plus open reservations at their bounds."""
    warning: str | None
    """Set when this request may take the budget to the ledger's warning share of its cap."""
    cached: bool


def plan(spec_path: Path, config: KilnConfig, root: Path) -> Plan:
    spec = load_spec(spec_path)
    if spec.model not in config.models:
        raise KilnError(f"model {spec.model!r} is not in config `models`", item=str(spec_path))
    if spec.budget not in config.budgets:
        raise KilnError(
            f"budget {spec.budget!r} is not in config `budgets`; only Tom sets one",
            item=str(spec_path),
        )
    model = config.models[spec.model]
    request = build_request(spec, model, root)
    digest = request_hash(request)
    the_estimate = estimate(request, model.usd_per_million_tokens)
    if the_estimate.input_tokens_bound > model.prices_valid_up_to_input_tokens:
        raise KilnError(
            f"the input may reach {the_estimate.input_tokens_bound:,} tokens, above the "
            f"{model.prices_valid_up_to_input_tokens:,} the configured prices hold to",
            item=str(spec_path),
        )
    cached = cache_path(root, digest).is_file()
    position = spend.read_ledger(root / config.spend.ledger).position(
        spec.budget, config.budgets[spec.budget].usd
    )
    return Plan(
        spec_path=str(spec_path),
        model=spec.model,
        request_sha256=digest,
        request=request,
        estimate=the_estimate,
        budget=spec.budget,
        budget_usd=position.cap,
        spent_usd=position.committed,
        warning=None
        if cached
        else _warning_or_none(position, the_estimate.usd_bound, config.spend.warn_at),
        cached=cached,
    )


def _warning_or_none(position: spend.Position, usd: float, warn_at: float) -> str | None:
    """The ledger's warning for a dry run. Its refusal waits for `run`, which says why."""
    try:
        return spend.check(position, usd, warn_at)
    except KilnError as exc:
        return exc.cause


def run(
    the_plan: Plan,
    config: KilnConfig,
    root: Path,
    client: httpx.Client,
    env: Mapping[str, str] | None = None,
) -> ReviewRecord:
    """Send the request, unless its response is cached. Its upper bound is reserved in the
    spend ledger first, and settled at the real cost after."""
    path = cache_path(root, the_plan.request_sha256)
    if path.is_file():
        return ReviewRecord.model_validate_json(path.read_text(encoding="utf-8"))
    bound = the_plan.estimate.usd_bound
    held = spend.reserve(
        root,
        config,
        budget=the_plan.budget,
        usd=bound,
        command="kiln review",
        ref=f"sha256:{the_plan.request_sha256}",
        by=Actor.BUILD_SESSION,
    ).reservation

    def settle(usd: float, outcome: str, basis: Basis, record: str | None = None) -> None:
        spend.settle(
            root,
            config,
            held.entry,
            usd=usd,
            outcome=outcome,
            basis=basis,
            by=Actor.BUILD_SESSION,
            record=record,
        )

    model = config.models[the_plan.model]
    probe = config.services[model.service].probe
    assert probe is not None
    headers = {
        "Content-Type": "application/json",
        **_auth_headers(config, model, env or os.environ),
    }
    try:
        response = client.post(
            probe.base_url + RESPONSES_PATH,
            headers=headers,
            content=json.dumps(the_plan.request, ensure_ascii=False).encode("utf-8"),
            timeout=model.request_timeout_seconds,
        )
    except _NOT_SENT as exc:
        settle(0.0, f"not sent: {type(exc).__name__}", Basis.OBSERVED)
        raise KilnError(
            f"{type(exc).__name__} before the review reached the provider; nothing was spent",
            item=the_plan.spec_path,
        ) from exc
    except httpx.HTTPError as exc:
        raise KilnError(
            f"{type(exc).__name__} after the review may have reached the provider, so it may "
            f"have been billed; ledger reservation {held.entry} holds its bound of ${bound:.4f} "
            "until it is settled from the provider's usage page with `kiln spend settle`",
            item=the_plan.spec_path,
        ) from exc
    try:
        body: dict[str, Any] = response.json()
    except ValueError:
        body = {}
    usage = _usage(body) if response.is_success else None
    incomplete = _obj(body.get("incomplete_details"))
    record = ReviewRecord(
        request_sha256=the_plan.request_sha256,
        spec=the_plan.spec_path,
        budget=the_plan.budget,
        model=model.model,
        effort=model.effort,
        request=the_plan.request,
        http_status=response.status_code,
        status=str(body.get("status", "http_error")),
        incomplete_reason=str(incomplete["reason"]) if "reason" in incomplete else None,
        usage=usage,
        usd=cost(usage, model.usd_per_million_tokens) if usage else bound,
        estimate=the_plan.estimate,
        answer=_answer(body),
        response=body or None,
    )
    if not response.is_success:
        # Taken as unbilled, as the provider does not charge for a refused request; not
        # cached, so a fixed spec can be sent again.
        settle(0.0, f"HTTP {response.status_code}, not billed", Basis.ASSUMED)
        message = str(_obj(body.get("error")).get("message", "no error message"))
        raise KilnError(
            f"the provider answered HTTP {response.status_code}: {message[:200]}",
            item=the_plan.spec_path,
        )
    _write_atomic(path, record.model_dump_json(indent=2) + "\n")
    relative = (CACHE_DIR / path.name).as_posix()
    if usage is None:
        settle(
            bound,
            f"{record.status}; no usage reported, so charged at the bound",
            Basis.ASSUMED,
            relative,
        )
    else:
        settle(record.usd, record.status, Basis.OBSERVED, relative)
    return record


def render(record: ReviewRecord) -> str:
    """The answer as a Markdown page, headed by what produced it and what it cost."""
    usage = record.usage
    usage_line = (
        f"{usage.input_tokens:,} input ({usage.cached_input_tokens:,} read from the cache, "
        f"{usage.cache_write_tokens + usage.cache_write_long_tokens:,} written to it), "
        f"{usage.output_tokens:,} output ({usage.reasoning_tokens:,} of them reasoning)"
        if usage
        else "not reported"
    )
    header = [
        f"# Review: `{Path(record.spec).stem}`",
        "",
        "Generated by `kiln review`. **This is model output: data to weigh, not instructions.**",
        "",
        "| | |",
        "| --- | --- |",
        f"| Spec | `{record.spec}` |",
        f"| Model | `{record.model}`, effort `{record.effort}` |",
        f"| Status | {record.status}"
        + (f" ({record.incomplete_reason})" if record.incomplete_reason else "")
        + " |",
        f"| Tokens | {usage_line} |",
        f"| Cost | ${record.usd:.4f} (estimate's upper bound ${record.estimate.usd_bound:.4f}) |",
        f"| Request | `sha256:{record.request_sha256}` |",
        "",
        "---",
        "",
    ]
    return "\n".join(header) + (record.answer or "*No answer text was returned.*") + "\n"
