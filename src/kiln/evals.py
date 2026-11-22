"""Evaluation sets and the rules that grade them, fixed before any run (sketch, slice 9).

Two kinds of record, each one file in `kiln.recordfile`'s form, so the file Tom reads is
exactly the record a run is graded against, and its hash names one version:

- A **golden set** (`evals/golden-questions/<set>.md`): questions with a key fixed in advance,
  and the rule that decides whether an agent passes them. The first is the Researcher's 20
  (charter, Researcher, "First slice"), seeded with the charter's own dated claims (D-005 R6).
- A **baseline protocol** (`evals/baseline/<protocol>.md`): ADR-0029's comparison of the
  Council's path with one plain Claude Code session: what runs, what is held equal, what is
  measured, and the rule that decides, committed before either path runs (SOP §12).

**A key is only as good as its check.** Each question records whether its key was verified at
its source, when, and the exact evidence read. One that could not be is marked unverified,
with the reason, and keeps its unknowns stated; a set holding one is not ready to run.

**The decision rule is code.** `decide` applies the protocol's thresholds to the paths'
results, so what "wins" means is settled now, in a form that cannot be reread after the
numbers exist. Nothing here runs an evaluation or spends money: the runners arrive in phase 1.
"""

from __future__ import annotations

import re
from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, model_validator

from kiln import recordfile
from kiln.errors import KilnError
from kiln.ids import ContentHash
from kiln.model import Expert, Record, RepoPath, Slug, Text, Unknown
from kiln.profile import load_profile
from kiln.vocabulary import Actor, Basis

GOLDEN_DIR = Path("evals/golden-questions")
BASELINE_DIR = Path("evals/baseline")

HttpsUrl = Annotated[str, Field(pattern=r"^https://[^\s/]+(?:/\S*)?$")]
GoldenId = Annotated[str, Field(pattern=r"^golden:[a-z0-9]+(?:-[a-z0-9]+)*$")]
"""A golden question's id, qualified by its source (`kiln.ids`): `golden:<slug>`."""


class Mode(StrEnum):
    """The Researcher's modes its first slice covers (charter, Researcher)."""

    LOOKUP = "lookup"
    """Find what the authoritative source says."""
    VERIFY = "verify"
    """Test a stated claim against the authoritative source."""


class Family(StrEnum):
    """What a question tests (charter, Researcher, "First slice"; Researcher proposal,
    "Suggested benchmark questions")."""

    CURRENCY = "currency"
    """Whether a fact is current, in force or still true."""
    SUPERSESSION = "supersession"
    """Whether a source has been replaced, and by what."""
    JURISDICTION = "jurisdiction"
    """Whose rule it is, and whom it binds."""
    CITATION = "citation"
    """The exact words, from the exact source."""
    FALSE_PREMISE = "false_premise"
    """A question that rests on something untrue, which the answer must challenge."""
    INJECTION = "injection"
    """A page laced with instructions, which must stay data."""
    ESCALATION = "escalation"
    """A question outside the agent's remit, which it must route rather than answer."""
    TECHNICAL = "technical"
    """A version-specific library or tool fact, from its docs, code or advisories."""


class Verdict(StrEnum):
    """What the source says of a claim, in verify mode."""

    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    PARTLY_SUPPORTED = "partly_supported"


class Delivery(StrEnum):
    """How a question's context reaches the agent under test."""

    FETCHED = "fetched"
    """Served at a URL the agent's fetch tool reaches, as a page found while researching."""
    FORWARDED = "forwarded"
    """Passed in the request's context field, as material a caller forwards."""


class Status(StrEnum):
    VERIFIED = "verified"
    """The key was checked at its source, and the evidence read is recorded."""
    UNVERIFIED = "unverified"
    """The key could not be checked yet. The question cannot be graded until it is."""


class Context(Record):
    """Material handed to the agent with the question. It is data, never instructions."""

    path: RepoPath
    delivered_as: Delivery
    note: Text
    """What the material holds, and what it is for."""


class SeededFrom(Record):
    """The sentence in a repo file that a question tests, quoted exactly."""

    path: RepoPath
    quote: Text


class Source(Record):
    """Where a good answer should come from: the authority for the point."""

    publisher: Text
    title: Text
    url: HttpsUrl


class Evidence(Record):
    """One exact thing read to check a key."""

    url: HttpsUrl
    retrieved_on: date
    sha256: ContentHash
    """The bytes that were read. A web page's bytes change between fetches; the quote is
    what a re-check looks for."""
    locator: Text
    """Where in the source: a section, an item, a heading."""
    quote: Text
    """The words that settle the point, verbatim. Line breaks are joined, `...` marks words
    left out, and ` | ` joins the cells of a table row."""


class Verification(Record):
    """How the key was checked, by whom, and on what."""

    status: Status
    basis: Basis
    checked_on: date
    """The date the key is true as of."""
    by: Actor
    evidence: list[Evidence] = Field(default_factory=list[Evidence])
    reason: Text | None = None
    """Why a key is unverified: what was tried, and what failed."""

    @model_validator(mode="after")
    def _consistent(self) -> Verification:
        if self.status is Status.VERIFIED:
            if self.basis is not Basis.OBSERVED:
                raise ValueError("a verified key was observed at its source: basis `observed`")
            if not self.evidence:
                raise ValueError("a verified key records the evidence it was checked against")
            if self.reason is not None:
                raise ValueError("a verified key needs no reason")
        else:
            if self.basis not in (Basis.ASSUMED, Basis.UNKNOWN):
                raise ValueError("an unverified key is `assumed` or `unknown`, never more")
            if self.reason is None:
                raise ValueError("an unverified key says why it could not be checked")
        for item in self.evidence:
            if item.retrieved_on > self.checked_on:
                raise ValueError(f"evidence from {item.url} is dated after the check")
        return self


class Key(Record):
    """What a good answer says, fixed before any run."""

    verdict: Verdict | Unknown | None = None
    """Verify mode only: what the source says of the claim."""
    answer: Text | Unknown
    """The reference answer, in a few sentences."""
    points: Annotated[list[Text], Field(min_length=1)]
    """What a complete answer covers. A judge grades each: covered, partly or not."""
    sources: Annotated[list[Source], Field(min_length=1)]
    flag_if_says: list[Text] = Field(default_factory=list[Text])
    """Strings that send an answer to be read by hand: an obeyed injection, a stale fact, a
    conclusion outside the agent's remit."""
    escalate_to: Expert | None = None
    """The expert a good answer routes the question to."""


class GoldenQuestion(Record):
    id: GoldenId
    family: Family
    mode: Mode
    asked_by: Expert
    """The Council member who would ask it. Questions are phrased as that caller would."""
    question: Text
    claim: Text | None = None
    """Verify mode only: the claim under test, as the caller states it."""
    context: Context | None = None
    seeded_from: SeededFrom | None = None
    key: Key
    verification: Verification

    @model_validator(mode="after")
    def _consistent(self) -> GoldenQuestion:
        verify = self.mode is Mode.VERIFY
        if verify != (self.claim is not None):
            raise ValueError("a verify question states its claim, and only it does")
        if verify != (self.key.verdict is not None):
            raise ValueError("a verify question's key has a verdict, and only it does")
        if self.verification.status is Status.VERIFIED and "unknown" in (
            self.key.answer,
            self.key.verdict,
        ):
            raise ValueError("a verified key states its answer and verdict, not `unknown`")
        if self.family is Family.INJECTION and self.context is None:
            raise ValueError("an injection question hands the agent the page")
        if self.family is Family.ESCALATION and self.key.escalate_to is None:
            raise ValueError("an escalation question names the expert it routes to")
        if self.key.escalate_to is not None and self.key.escalate_to is self.asked_by:
            raise ValueError("a question does not escalate to the expert who asked it")
        return self

    @property
    def verified(self) -> bool:
        return self.verification.status is Status.VERIFIED


class PassRule(Record):
    """When the agent under test passes the set. Drafted with the set; Tom approves both."""

    reverify_within_days: Annotated[int, Field(ge=1)]
    """A key older than this on the day of a run is checked again first: currency moves."""
    question_passes_when: Annotated[list[Text], Field(min_length=1)]
    hard_rules: Annotated[list[Text], Field(min_length=1)]
    """Breached on any one question, the set fails, whatever the count."""
    min_passed: Annotated[int, Field(ge=1)]


class GoldenSet(Record):
    version: Literal[1]
    set: Slug
    title: Text
    for_agent: Expert
    purpose: Text
    drafted_by: Actor
    drafted_on: date
    covers: Annotated[list[Family], Field(min_length=1)]
    """The families the set must cover, each by at least one question."""
    pass_rule: PassRule
    questions: Annotated[list[GoldenQuestion], Field(min_length=1)]
    notes: list[Text] = Field(default_factory=list[Text])
    """What a reader should know: the set's limits, and how it must be run."""

    @model_validator(mode="after")
    def _consistent(self) -> GoldenSet:
        ids = [question.id for question in self.questions]
        if len(set(ids)) != len(ids):
            raise ValueError("two questions share an id")
        present = {question.family for question in self.questions}
        missing = [family.value for family in self.covers if family not in present]
        if missing:
            raise ValueError(f"no question covers {', '.join(missing)}")
        if self.pass_rule.min_passed > len(self.questions):
            raise ValueError("the pass rule asks for more passes than there are questions")
        if any(question.asked_by is self.for_agent for question in self.questions):
            raise ValueError("the agent under test does not ask its own questions")
        if self.drafted_by is Actor.TOM:
            raise ValueError("a set is drafted for Tom's approval, not by him")
        return self

    @property
    def unverified(self) -> list[GoldenQuestion]:
        """The questions that cannot be graded until their keys are checked at source."""
        return [question for question in self.questions if not question.verified]

    @property
    def file_name(self) -> str:
        return f"{self.set}.md"


PathId = Literal["council", "single-session"]


class EvalPath(Record):
    """One of the two ways the briefs are taken from intake to a verified build."""

    id: PathId
    name: Text
    runs: Text
    """What runs, and what it writes."""


class MeasureKind(StrEnum):
    FLOOR = "floor"
    """Pass or fail on each brief; a path that fails one where the other passes loses."""
    QUALITY = "quality"
    COST = "cost"
    TIME = "time"
    REPORTED = "reported"
    """Shown beside the result; not part of the rule."""


class Measure(Record):
    id: Slug
    kind: MeasureKind
    what: Text
    how: Text
    """The instrument, and where its number comes from."""


class BriefPoints(Record):
    """One sample brief and what a complete plan and build for it covers."""

    brief: RepoPath
    points: Annotated[list[Text], Field(min_length=3)]


class Judge(Record):
    who: Text
    blinding: Text
    checked_by: Text
    """How the judge is checked before its grades count (SOP §12, T9)."""


class Thresholds(Record):
    """The numbers the rule applies. `decide` is the rule; these are its settings."""

    quality_margin: Annotated[float, Field(gt=0, le=1)]
    """How far the Council's share of points covered must exceed the single session's."""
    pairwise_min_wins: Annotated[int, Field(ge=1)]
    pairwise_max_losses: Annotated[int, Field(ge=0)]
    cost_ratio_max: Annotated[float, Field(gt=0)]
    """The Council's total cost may be at most this many times the single session's."""
    time_ratio_max: Annotated[float, Field(gt=0)]


class BaselineProtocol(Record):
    version: Literal[1]
    protocol: Slug
    title: Text
    adr: Annotated[str, Field(pattern=r"^ADR-\d{4}$")]
    drafted_by: Actor
    drafted_on: date
    question: Text
    paths: Annotated[list[EvalPath], Field(min_length=2, max_length=2)]
    held_equal: Annotated[list[Text], Field(min_length=1)]
    runs_per_brief: Annotated[int, Field(ge=1)]
    order: Text
    briefs: Annotated[list[BriefPoints], Field(min_length=1)]
    measures: Annotated[list[Measure], Field(min_length=1)]
    judge: Judge
    thresholds: Thresholds
    if_not_won: Text
    precision: Text
    """What the design can and cannot detect, stated before the numbers."""
    budget: Text
    deviations: Text

    @model_validator(mode="after")
    def _consistent(self) -> BaselineProtocol:
        if {path.id for path in self.paths} != {"council", "single-session"}:
            raise ValueError("the two paths are `council` and `single-session` (ADR-0029)")
        briefs = [entry.brief for entry in self.briefs]
        if len(set(briefs)) != len(briefs):
            raise ValueError("a brief is listed twice")
        ids = [measure.id for measure in self.measures]
        if len(set(ids)) != len(ids):
            raise ValueError("two measures share an id")
        kinds = {measure.kind for measure in self.measures}
        missing = [
            kind.value
            for kind in (MeasureKind.FLOOR, MeasureKind.QUALITY, MeasureKind.COST, MeasureKind.TIME)
            if kind not in kinds
        ]
        if missing:
            raise ValueError(f"ADR-0029 compares quality, cost and time; no {missing} measure")
        comparisons = len(self.briefs) * self.runs_per_brief
        rule = self.thresholds
        if rule.pairwise_min_wins + rule.pairwise_max_losses > comparisons:
            raise ValueError(f"the pairwise thresholds need more than {comparisons} comparisons")
        if self.drafted_by is Actor.TOM:
            raise ValueError("a protocol is drafted for Tom's approval, not by him")
        return self

    @property
    def floors(self) -> list[str]:
        return [m.id for m in self.measures if m.kind is MeasureKind.FLOOR]

    @property
    def file_name(self) -> str:
        return f"{self.protocol}.md"


class PathResult(Record):
    """One path's result on one brief."""

    floors_failed: list[Slug] = Field(default_factory=list[Slug])
    points_covered: Annotated[float, Field(ge=0)]
    """The judge's grades summed: covered 1, partly 0.5, not 0."""
    usd: Annotated[float, Field(ge=0)]
    """Every paid call of the run, failed ones included, from the spend ledger."""
    minutes: Annotated[float, Field(ge=0)]


class Comparison(Record):
    """The two paths on one run of one brief, and the judge's pairwise preference: a path
    is preferred only when both orders agree, and otherwise `neither`."""

    brief: RepoPath
    council: PathResult
    single_session: PathResult
    preferred: Literal["council", "single-session", "neither"]


class Criterion(Record):
    name: Text
    met: bool
    detail: Text


class Decision(Record):
    council_wins: bool
    criteria: list[Criterion]


def decide(protocol: BaselineProtocol, comparisons: list[Comparison]) -> Decision:
    """Apply the protocol's rule to the results. The Council's path wins only if it meets
    every criterion; otherwise phase 2 waits for Tom (ADR-0029)."""
    points = {entry.brief: len(entry.points) for entry in protocol.briefs}
    expected = sorted(points) * protocol.runs_per_brief
    if sorted(c.brief for c in comparisons) != sorted(expected):
        raise KilnError(
            f"the rule needs {protocol.runs_per_brief} comparison(s) for each of the "
            f"protocol's {len(points)} briefs, and only those",
            item=protocol.protocol,
        )
    floors = set(protocol.floors)
    for comparison in comparisons:
        for result in (comparison.council, comparison.single_session):
            unknown = set(result.floors_failed) - floors
            if unknown:
                raise KilnError(f"not floor measures: {sorted(unknown)}", item=comparison.brief)
            if result.points_covered > points[comparison.brief]:
                raise KilnError("more points covered than the brief has", item=comparison.brief)
    rule = protocol.thresholds

    floor_losses = [
        f"{c.brief}: {sorted(set(c.council.floors_failed) - set(c.single_session.floors_failed))}"
        for c in comparisons
        if set(c.council.floors_failed) - set(c.single_session.floors_failed)
    ]
    total = sum(points[c.brief] for c in comparisons)
    council_share = sum(c.council.points_covered for c in comparisons) / total
    single_share = sum(c.single_session.points_covered for c in comparisons) / total
    wins = sum(c.preferred == "council" for c in comparisons)
    losses = sum(c.preferred == "single-session" for c in comparisons)
    council_usd = sum(c.council.usd for c in comparisons)
    single_usd = sum(c.single_session.usd for c in comparisons)
    council_minutes = sum(c.council.minutes for c in comparisons)
    single_minutes = sum(c.single_session.minutes for c in comparisons)

    criteria = [
        Criterion(
            name="Floors",
            met=not floor_losses,
            detail="; ".join(floor_losses)
            or "the Council's path passed every floor the single session passed",
        ),
        Criterion(
            name="Points covered",
            met=council_share - single_share >= rule.quality_margin - 1e-9,
            detail=f"Council {council_share:.1%}, single session {single_share:.1%}; "
            f"needs a lead of {rule.quality_margin:.0%}",
        ),
        Criterion(
            name="Pairwise preference",
            met=wins >= rule.pairwise_min_wins and losses <= rule.pairwise_max_losses,
            detail=f"Council preferred {wins} time(s), single session {losses}; needs at "
            f"least {rule.pairwise_min_wins} and at most {rule.pairwise_max_losses}",
        ),
        Criterion(
            name="Cost",
            met=_within(council_usd, single_usd, rule.cost_ratio_max),
            detail=f"Council ${council_usd:.2f}, single session ${single_usd:.2f}; "
            f"allows {rule.cost_ratio_max:g} times",
        ),
        Criterion(
            name="Time",
            met=_within(council_minutes, single_minutes, rule.time_ratio_max),
            detail=f"Council {council_minutes:g} min, single session {single_minutes:g} min; "
            f"allows {rule.time_ratio_max:g} times",
        ),
    ]
    return Decision(council_wins=all(c.met for c in criteria), criteria=criteria)


def _within(council: float, single: float, ratio: float) -> bool:
    return council <= single * ratio + 1e-9


def render_golden(golden: GoldenSet) -> str:
    """The set as Tom reads it. It adds nothing the record does not hold."""
    done = len(golden.questions) - len(golden.unverified)
    lines = [
        f"# {golden.title}",
        "",
        f"**For:** {golden.for_agent.value}. **Drafted** by {golden.drafted_by.value} on "
        f"{golden.drafted_on.isoformat()}. **{len(golden.questions)} questions**, "
        f"{done} with a key verified at its source.",
        "",
        golden.purpose.strip(),
        "",
    ]
    if golden.unverified:
        names = ", ".join(f"`{q.id}`" for q in golden.unverified)
        lines += [
            f"**Not ready to run.** {_count(len(golden.unverified), 'key')} not yet verified "
            f"at their source: {names}.",
            "",
        ]
    rule = golden.pass_rule
    lines += [
        "## The pass rule",
        "",
        f"The set passes if at least **{rule.min_passed} of {len(golden.questions)}** "
        "questions pass and no hard rule is broken on any of them.",
        "",
        "**A question passes when:**",
        "",
        *[f"- {line.strip()}" for line in rule.question_passes_when],
        "",
        "**Hard rules:**",
        "",
        *[f"- {line.strip()}" for line in rule.hard_rules],
        "",
        f"A key checked more than {rule.reverify_within_days} days before a run is checked "
        "at its source again first.",
        "",
    ]
    if golden.notes:
        lines += ["## Notes", "", *[f"- {note.strip()}" for note in golden.notes], ""]
    lines += [
        "## The questions",
        "",
        "| # | Question | Family | Mode | Asked by | Key |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for number, q in enumerate(golden.questions, start=1):
        lines.append(
            f"| {number} | [`{q.id}`](#{_anchor(number, q.id)}) | {q.family.value} | "
            f"{q.mode.value} | {q.asked_by.value} | {q.verification.status.value} |"
        )
    lines.append("")
    for number, q in enumerate(golden.questions, start=1):
        lines += _render_question(number, q)
    lines += [_RENDERED_NOTE]
    return "\n".join(lines)


def _render_question(number: int, q: GoldenQuestion) -> list[str]:
    lines = [
        f"### {number}. `{q.id}`",
        "",
        f"**{q.family.value}, {q.mode.value}, asked by {q.asked_by.value}.** {_flat(q.question)}",
        "",
    ]
    if q.claim:
        lines += [f"**Claim under test.** {_flat(q.claim)}", ""]
    if q.seeded_from:
        lines += [
            f"**Seeded from** `{q.seeded_from.path}`: “{_flat(q.seeded_from.quote)}”",
            "",
        ]
    if q.context:
        lines += [
            f"**Context,** {q.context.delivered_as.value}: `{q.context.path}`. "
            f"{_flat(q.context.note)}",
            "",
        ]
    key = q.key
    if key.verdict is not None:
        lines += [f"**Verdict:** {key.verdict}.", ""]
    lines += [f"**Reference answer.** {_flat(key.answer)}", "", "**Points to cover:**", ""]
    lines += [f"- {_flat(point)}" for point in key.points]
    lines += ["", "**Sources a good answer cites:**", ""]
    lines += [f"- {s.publisher}, [{_flat(s.title)}]({s.url})" for s in key.sources]
    lines.append("")
    if key.escalate_to:
        lines += [f"**Routes to** {key.escalate_to.value}.", ""]
    if key.flag_if_says:
        flags = "; ".join(f"“{_flat(flag)}”" for flag in key.flag_if_says)
        lines += [f"**Read by hand if the answer says:** {flags}.", ""]
    check = q.verification
    lines += [
        f"**Key {check.status.value}** ({check.basis.value}) on {check.checked_on.isoformat()} "
        f"by {check.by.value}.",
        "",
    ]
    if check.reason:
        lines += [f"*Why not verified:* {_flat(check.reason)}", ""]
    for item in check.evidence:
        lines += [
            f"- Read {item.retrieved_on.isoformat()}: <{item.url}>, {_flat(item.locator)} "
            f"(`{item.sha256.removeprefix('sha256:')[:16]}…`)",
            "",
            f"  > {_flat(item.quote)}",
            "",
        ]
    return lines


def render_protocol(protocol: BaselineProtocol) -> str:
    """The protocol as Tom reads it. The rule's sentences are written from its numbers."""
    rule = protocol.thresholds
    comparisons = len(protocol.briefs) * protocol.runs_per_brief
    lines = [
        f"# {protocol.title}",
        "",
        f"**For {protocol.adr}.** Drafted by {protocol.drafted_by.value} on "
        f"{protocol.drafted_on.isoformat()}. Committed before either path runs.",
        "",
        f"**The question.** {_flat(protocol.question)}",
        "",
        "## The two paths",
        "",
        "| Path | What runs |",
        "| --- | --- |",
        *[f"| **{p.name}** (`{p.id}`) | {_cell(p.runs)} |" for p in protocol.paths],
        "",
        "**Held equal:**",
        "",
        *[f"- {_flat(line)}" for line in protocol.held_equal],
        "",
        f"**Runs:** {protocol.runs_per_brief} per path per brief: "
        f"{_count(comparisons, 'paired comparison')} in all. {_flat(protocol.order)}",
        "",
        "## The rule",
        "",
        "The Council's path wins only if all five hold:",
        "",
        "1. **Floors.** On every brief, it passes each floor measure the single session passes.",
        f"2. **Points covered.** Over all briefs, its share of the points covered beats the single "
        f"session's by at least {rule.quality_margin:.0%} of the points.",
        f"3. **Pairwise.** The judge prefers it in at least {rule.pairwise_min_wins} of the "
        f"{_count(comparisons, 'comparison')}, and "
        + (
            "never prefers the single session."
            if rule.pairwise_max_losses == 0
            else f"prefers the single session in at most {rule.pairwise_max_losses}."
        )
        + " A preference counts only when both orders agree.",
        f"4. **Cost.** Its total cost is at most {rule.cost_ratio_max:g} times the single "
        "session's.",
        f"5. **Time.** Its total elapsed time is at most {rule.time_ratio_max:g} times the single "
        "session's.",
        "",
        f"**Otherwise:** {_flat(protocol.if_not_won)}",
        "",
        "The rule is `kiln.evals.decide`, with these numbers as its settings.",
        "",
        "## Measures",
        "",
        "| Measure | Kind | What | How |",
        "| --- | --- | --- | --- |",
        *[
            f"| `{m.id}` | {m.kind.value} | {_cell(m.what)} | {_cell(m.how)} |"
            for m in protocol.measures
        ],
        "",
        "## The judge",
        "",
        f"- **Who:** {_flat(protocol.judge.who)}",
        f"- **Blinding:** {_flat(protocol.judge.blinding)}",
        f"- **Checked first:** {_flat(protocol.judge.checked_by)}",
        "",
        "## Points per brief",
        "",
        "Each point is graded covered (1), partly (0.5) or not (0), from the plan, the tickets "
        "and the build.",
        "",
    ]
    for entry in protocol.briefs:
        lines += [f"**`{entry.brief}`**", ""]
        lines += [f"{n}. {_flat(point)}" for n, point in enumerate(entry.points, start=1)]
        lines.append("")
    lines += [
        "## Precision",
        "",
        _flat(protocol.precision),
        "",
        "## Budget",
        "",
        _flat(protocol.budget),
        "",
        "## Deviations",
        "",
        _flat(protocol.deviations),
        "",
        _RENDERED_NOTE,
    ]
    return "\n".join(lines)


_RENDERED_NOTE = (
    "<!-- Rendered from the front matter by Kiln. Edit the front matter, then run "
    "`kiln records render`. -->"
)


def _count(number: int, noun: str) -> str:
    return f"{number} {noun}" + ("" if number == 1 else "s")


def _flat(text: str) -> str:
    return " ".join(text.split())


def _cell(text: str) -> str:
    return _flat(text).replace("|", "\\|")


def _anchor(number: int, question_id: str) -> str:
    """GitHub's anchor for the question's heading, `### N. `golden:slug``."""
    return f"{number}-{question_id.replace(':', '')}"


def golden_text(golden: GoldenSet) -> str:
    return recordfile.compose(golden, render_golden(golden))


def protocol_text(protocol: BaselineProtocol) -> str:
    return recordfile.compose(protocol, render_protocol(protocol))


def load_golden(path: Path, *, item: str) -> GoldenSet:
    return recordfile.load(path.read_text(encoding="utf-8"), GoldenSet, render_golden, item=item)


def load_protocol(path: Path, *, item: str) -> BaselineProtocol:
    return recordfile.load(
        path.read_text(encoding="utf-8"), BaselineProtocol, render_protocol, item=item
    )


def check_evals(root: Path) -> list[KilnError]:
    """Each eval record is valid and its own rendering, under its own name, and what it points
    at still holds: a seeded quote still stands in its file, a context page exists, and every
    brief still validates as a profile."""
    problems: list[KilnError] = []
    for path in _records(root, GOLDEN_DIR):
        item = str(GOLDEN_DIR / path.name)
        try:
            golden = load_golden(path, item=item)
        except KilnError as exc:
            problems.append(exc)
            continue
        if path.name != golden.file_name:
            problems.append(KilnError(f"file name should be {golden.file_name}", item=item))
        for question in golden.questions:
            problems += [
                KilnError(f"{question.id}: {message}", item=item)
                for message in _pointer_problems(root, question)
            ]
    for path in _records(root, BASELINE_DIR):
        item = str(BASELINE_DIR / path.name)
        try:
            protocol = load_protocol(path, item=item)
        except KilnError as exc:
            problems.append(exc)
            continue
        if path.name != protocol.file_name:
            problems.append(KilnError(f"file name should be {protocol.file_name}", item=item))
        for entry in protocol.briefs:
            try:
                load_profile(root / entry.brief)
            except KilnError as exc:
                problems.append(KilnError(f"brief {entry.brief}: {exc.cause}", item=item))
    return problems


def _pointer_problems(root: Path, question: GoldenQuestion) -> list[str]:
    problems: list[str] = []
    if question.context and not (root / question.context.path).is_file():
        problems.append(f"its context {question.context.path} is missing")
    seed = question.seeded_from
    if seed:
        source = root / seed.path
        if not source.is_file():
            problems.append(f"it is seeded from {seed.path}, which is missing")
        elif _squash(seed.quote) not in _squash(source.read_text(encoding="utf-8")):
            problems.append(
                f"its seed no longer stands in {seed.path}: the claim it tests has changed, "
                "so the question needs redrafting"
            )
    return problems


def _squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _records(root: Path, directory: Path) -> list[Path]:
    folder = root / directory
    return sorted(folder.glob("*.md")) if folder.is_dir() else []


def render_evals(root: Path) -> list[Path]:
    """Rewrite each eval record as its canonical rendering. Returns the files that changed."""
    changed: list[Path] = []
    for directory, compose in ((GOLDEN_DIR, _compose_golden), (BASELINE_DIR, _compose_protocol)):
        for path in _records(root, directory):
            text = path.read_text(encoding="utf-8")
            canonical = compose(text, str(directory / path.name))
            if canonical != text:
                recordfile.write_atomic(path, canonical)
                changed.append(directory / path.name)
    return changed


def _compose_golden(text: str, item: str) -> str:
    return golden_text(recordfile.parse(text, GoldenSet, item=item))


def _compose_protocol(text: str, item: str) -> str:
    return protocol_text(recordfile.parse(text, BaselineProtocol, item=item))
