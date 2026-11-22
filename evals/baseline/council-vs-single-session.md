---
version: 1
protocol: council-vs-single-session
title: The baseline comparison, the Council against one session (draft for Tom's approval)
adr: ADR-0029
drafted_by: build_session
drafted_on: '2026-11-22'
question: Does the Council's path (the chair, the Researcher and one coding loop) take the three sample
  briefs to a better plan and build than one plain Claude Code session given the same briefs and the same
  rulebook, by enough to be worth its extra cost and time?
paths:
- id: council
  name: The Council's path
  runs: The chair (Solution Architect) takes the brief to a profile, a plan and a ticket list, consulting
    the Researcher; the plan goes through G2; one coding loop builds the tickets in the sandbox; the verifier
    sets each ticket's pass.
- id: single-session
  name: One plain session
  runs: One Claude Code session, given the brief and the rulebook, writes the same artefacts (a profile,
    a plan and a ticket list), takes the plan through the same G2, and builds the tickets in the same
    sandbox; the same verifier sets each pass. It has no Council agent's prompt, knowledge base or source
    registry.
held_equal:
- The three sample briefs, as Tom approved them, byte for byte.
- The rulebook (AGENTS.md, CLAUDE.md and the charter) at one commit, named in each run's record.
- The model and effort of every Claude call in both paths, and the judge's model.
- 'The harness, the same for both: the sandbox, its egress allowlist and credential, the scanners, the
  verifier and the gates.'
- 'The outside tools: web fetch, Context7 and read-only GitHub. The Researcher''s source map is the Council''s
  own knowledge, so the session does not get it.'
- A spend cap per brief per path, and a wall-clock cap per brief per path, set in config before the first
  run.
- 'The starting state: a fresh solution repo from one template for every run.'
- 'Tom''s part: he approves each plan at G2 in both paths, in the same way.'
- Neither path sees the other's outputs, the points below, or anything under `evals/`.
runs_per_brief: 1
order: The order of the briefs, and which path runs a brief first, are fixed by the sha256 of each brief's
  file name, recorded before the first run. Both paths run each brief within the same 48 hours, so a change
  at the provider falls on both.
briefs:
- brief: evals/sample-briefs/public-form-service.yaml
  points:
  - The plan says the form collects personal and commercial information, and routes the privacy obligations
    (the collection notice and the privacy policy) to the Governance Guru before any real data is used.
  - The form targets WCAG 2.2 AA and works on a phone; the build runs automated accessibility checks and
    lists the manual checks automation cannot settle.
  - The form checks a request is complete before it is sent and returns a reference number.
  - The applicant can track a request by its reference without seeing anyone else's.
  - Staff, not the form, decide whether to reissue; the plan keeps that decision with staff and says what
    would change if any of it were automated.
  - The hand-off to the case system (H3) is built against a sandboxed copy, with every field mapped and
    tested; no live system is touched.
  - H2 has no measure; the plan proposes one for cost per request, or names the data it needs.
  - The build estimate is within the $25 budget, worked out by calculation, not judgement.
- brief: evals/sample-briefs/internal-rag-assistant.yaml
  points:
  - Answers come from the manual only, each citing the section it relied on, and the assistant declines
    when the manual is silent.
  - 'H2 is measured as the brief says: 50 held-out questions with known answers, 90% citing the right
    section, every uncovered question declined.'
  - A deterministic check confirms each answer's citation resolves to a real section that supports it,
    so no procedure is invented.
  - Retrieval over the manual is chosen by measurement, exact search first, not by assumption.
  - The manual is unpublished; the plan says what of it reaches a model provider, and Tom approves that
    before it does.
  - Text inside the manual is treated as data, never as instructions to the assistant.
  - Running cost is estimated by calculation from prices looked up at the time, within $30 a month, and
    the build within $40.
  - H3 has no measure; the plan proposes one, and the AI policy's applicability is routed to the Governance
    Guru.
- brief: evals/sample-briefs/data-dashboard.yaml
  points:
  - The data touched is unknown; the plan asks the data owner whether the extract holds applicant names
    before G1, and designs to work without them.
  - The build uses a synthetic stand-in for the extract; no real data enters it (ADR-0024).
  - Time to decision is computed deterministically by application type, with its start and end events
    defined.
  - 'H2 is tested as the brief says: a past month''s figures reconciled against that month''s hand-built
    spreadsheet.'
  - Application types near the service standard are flagged, with the threshold in configuration and documented.
  - The weekly refresh needs no manual cleaning, and a change in the extract's shape fails loudly.
  - The budget is unknown; the plan estimates build and running cost and asks Tom for a budget before
    G2.
  - H1 and H3 have no measure; the plan proposes one for each.
measures:
- id: g2-validation
  kind: floor
  what: The plan passes G2's validation node.
  how: '`kiln gates` on the run''s solution repo, before Tom''s approval; deterministic.'
- id: tickets-pass
  kind: floor
  what: Every ticket in the plan passes.
  how: The verifier's run on a clean checkout of the final commit (slice 4); deterministic.
- id: no-blocking-findings
  kind: floor
  what: No open critical, high or unknown scanner finding.
  how: '`kiln scan` with each of the three scanners on the final commit; deterministic.'
- id: within-caps
  kind: floor
  what: The run finished within its spend and wall-clock caps.
  how: The spend ledger and the run's record; a run stopped at a cap fails this floor.
- id: points-covered
  kind: quality
  what: How many of the brief's points the plan, tickets and build cover.
  how: The judge grades each point covered, partly or not, against the run's artefacts, blind to the path.
- id: pairwise
  kind: quality
  what: Which path's plan and build for the brief is better as a whole.
  how: The judge compares the two paths' artefacts for a brief in both orders; a preference counts only
    when both orders agree.
- id: cost-usd
  kind: cost
  what: Dollars spent by the path on the brief, failed calls included.
  how: The spend ledger, every entry the run reserved and settled.
- id: elapsed-minutes
  kind: time
  what: Wall-clock minutes from the brief handed over to the last ticket's pass, or the stop, less any
    time spent waiting for Tom.
  how: The run's record, from its first and last events; waits for Tom are taken out and reported under
    `tom-questions`.
- id: tom-questions
  kind: reported
  what: The decisions and questions each path put to Tom, and the minutes he spent on them.
  how: Counted from the decision cards and the session transcripts; Tom's minutes as he reports them.
    Tom's attention is the scarce resource, so it is shown beside the result.
- id: behaviour
  kind: reported
  what: Tool calls by tool, tokens in and out, retries and typed questions, per path per brief.
  how: The traces.
judge:
  who: 'A model from a family neither path uses: both run Claude, so OpenAI''s or Google''s, named and
    pinned before the first run, through `kiln review`''s client and the spend ledger.'
  blinding: 'Each path''s artefacts are normalised before the judge sees them: agent names, trace ids,
    timestamps and path-specific file names are removed, and the two are labelled by a hash. The judge
    never learns which path wrote which.'
  checked_by: Before its grades count, the judge grades damaged copies of one brief's artefacts, each
    with one known fault (SOP template T9), and must notice each; what "noticed" means for each fault
    is fixed before that check runs.
thresholds:
  quality_margin: 0.1
  pairwise_min_wins: 2
  pairwise_max_losses: 0
  cost_ratio_max: 3.0
  time_ratio_max: 2.0
if_not_won: The Council's path has not shown it is better. The numbers go to Tom with a recommendation,
  and phase 2 does not start unless he decides to go on anyway (ADR-0029).
precision: 'Three briefs, one run each: three paired comparisons. No statistical test separates two paths
  at that size; even three wins in three has a one-sided sign-test p of 0.125. The rule is a screen that
  asks for a consistent, visible advantage on every axis, not a proof. Run-to-run variation is unknown
  with one run per brief, so a single bad run can decide a brief; the result reports which criteria were
  met narrowly. Slice 6''s thin path is a pilot. It runs one ticket, before the Council exists, to measure
  a brief''s cost for the estimate, and it is not one of the comparisons.'
budget: Nothing here spends. Before the first run, Tom sets a budget for the comparison in `config/kiln.yaml`,
  from an estimate built on slice 6's measured cost per brief (the sketch guesses about a dollar for one
  ticket). Each run reserves its cap through the spend ledger before it starts, and the judge's calls
  are metered the same way.
deviations: This file is approved at one hash and not edited after. A change before the first run is a
  new version with a new card; a change after it is disclosed in the result, in order, with what it changed
  (SOP §12). A failed or stopped run is recorded, not re-run quietly.
---

# The baseline comparison, the Council against one session (draft for Tom's approval)

**For ADR-0029.** Drafted by build_session on 2026-11-22. Committed before either path runs.

**The question.** Does the Council's path (the chair, the Researcher and one coding loop) take the three sample briefs to a better plan and build than one plain Claude Code session given the same briefs and the same rulebook, by enough to be worth its extra cost and time?

## The two paths

| Path | What runs |
| --- | --- |
| **The Council's path** (`council`) | The chair (Solution Architect) takes the brief to a profile, a plan and a ticket list, consulting the Researcher; the plan goes through G2; one coding loop builds the tickets in the sandbox; the verifier sets each ticket's pass. |
| **One plain session** (`single-session`) | One Claude Code session, given the brief and the rulebook, writes the same artefacts (a profile, a plan and a ticket list), takes the plan through the same G2, and builds the tickets in the same sandbox; the same verifier sets each pass. It has no Council agent's prompt, knowledge base or source registry. |

**Held equal:**

- The three sample briefs, as Tom approved them, byte for byte.
- The rulebook (AGENTS.md, CLAUDE.md and the charter) at one commit, named in each run's record.
- The model and effort of every Claude call in both paths, and the judge's model.
- The harness, the same for both: the sandbox, its egress allowlist and credential, the scanners, the verifier and the gates.
- The outside tools: web fetch, Context7 and read-only GitHub. The Researcher's source map is the Council's own knowledge, so the session does not get it.
- A spend cap per brief per path, and a wall-clock cap per brief per path, set in config before the first run.
- The starting state: a fresh solution repo from one template for every run.
- Tom's part: he approves each plan at G2 in both paths, in the same way.
- Neither path sees the other's outputs, the points below, or anything under `evals/`.

**Runs:** 1 per path per brief: 3 paired comparisons in all. The order of the briefs, and which path runs a brief first, are fixed by the sha256 of each brief's file name, recorded before the first run. Both paths run each brief within the same 48 hours, so a change at the provider falls on both.

## The rule

The Council's path wins only if all five hold:

1. **Floors.** On every brief, it passes each floor measure the single session passes.
2. **Points covered.** Over all briefs, its share of the points covered beats the single session's by at least 10% of the points.
3. **Pairwise.** The judge prefers it in at least 2 of the 3 comparisons, and never prefers the single session. A preference counts only when both orders agree.
4. **Cost.** Its total cost is at most 3 times the single session's.
5. **Time.** Its total elapsed time is at most 2 times the single session's.

**Otherwise:** The Council's path has not shown it is better. The numbers go to Tom with a recommendation, and phase 2 does not start unless he decides to go on anyway (ADR-0029).

The rule is `kiln.evals.decide`, with these numbers as its settings.

## Measures

| Measure | Kind | What | How |
| --- | --- | --- | --- |
| `g2-validation` | floor | The plan passes G2's validation node. | `kiln gates` on the run's solution repo, before Tom's approval; deterministic. |
| `tickets-pass` | floor | Every ticket in the plan passes. | The verifier's run on a clean checkout of the final commit (slice 4); deterministic. |
| `no-blocking-findings` | floor | No open critical, high or unknown scanner finding. | `kiln scan` with each of the three scanners on the final commit; deterministic. |
| `within-caps` | floor | The run finished within its spend and wall-clock caps. | The spend ledger and the run's record; a run stopped at a cap fails this floor. |
| `points-covered` | quality | How many of the brief's points the plan, tickets and build cover. | The judge grades each point covered, partly or not, against the run's artefacts, blind to the path. |
| `pairwise` | quality | Which path's plan and build for the brief is better as a whole. | The judge compares the two paths' artefacts for a brief in both orders; a preference counts only when both orders agree. |
| `cost-usd` | cost | Dollars spent by the path on the brief, failed calls included. | The spend ledger, every entry the run reserved and settled. |
| `elapsed-minutes` | time | Wall-clock minutes from the brief handed over to the last ticket's pass, or the stop, less any time spent waiting for Tom. | The run's record, from its first and last events; waits for Tom are taken out and reported under `tom-questions`. |
| `tom-questions` | reported | The decisions and questions each path put to Tom, and the minutes he spent on them. | Counted from the decision cards and the session transcripts; Tom's minutes as he reports them. Tom's attention is the scarce resource, so it is shown beside the result. |
| `behaviour` | reported | Tool calls by tool, tokens in and out, retries and typed questions, per path per brief. | The traces. |

## The judge

- **Who:** A model from a family neither path uses: both run Claude, so OpenAI's or Google's, named and pinned before the first run, through `kiln review`'s client and the spend ledger.
- **Blinding:** Each path's artefacts are normalised before the judge sees them: agent names, trace ids, timestamps and path-specific file names are removed, and the two are labelled by a hash. The judge never learns which path wrote which.
- **Checked first:** Before its grades count, the judge grades damaged copies of one brief's artefacts, each with one known fault (SOP template T9), and must notice each; what "noticed" means for each fault is fixed before that check runs.

## Points per brief

Each point is graded covered (1), partly (0.5) or not (0), from the plan, the tickets and the build.

**`evals/sample-briefs/public-form-service.yaml`**

1. The plan says the form collects personal and commercial information, and routes the privacy obligations (the collection notice and the privacy policy) to the Governance Guru before any real data is used.
2. The form targets WCAG 2.2 AA and works on a phone; the build runs automated accessibility checks and lists the manual checks automation cannot settle.
3. The form checks a request is complete before it is sent and returns a reference number.
4. The applicant can track a request by its reference without seeing anyone else's.
5. Staff, not the form, decide whether to reissue; the plan keeps that decision with staff and says what would change if any of it were automated.
6. The hand-off to the case system (H3) is built against a sandboxed copy, with every field mapped and tested; no live system is touched.
7. H2 has no measure; the plan proposes one for cost per request, or names the data it needs.
8. The build estimate is within the $25 budget, worked out by calculation, not judgement.

**`evals/sample-briefs/internal-rag-assistant.yaml`**

1. Answers come from the manual only, each citing the section it relied on, and the assistant declines when the manual is silent.
2. H2 is measured as the brief says: 50 held-out questions with known answers, 90% citing the right section, every uncovered question declined.
3. A deterministic check confirms each answer's citation resolves to a real section that supports it, so no procedure is invented.
4. Retrieval over the manual is chosen by measurement, exact search first, not by assumption.
5. The manual is unpublished; the plan says what of it reaches a model provider, and Tom approves that before it does.
6. Text inside the manual is treated as data, never as instructions to the assistant.
7. Running cost is estimated by calculation from prices looked up at the time, within $30 a month, and the build within $40.
8. H3 has no measure; the plan proposes one, and the AI policy's applicability is routed to the Governance Guru.

**`evals/sample-briefs/data-dashboard.yaml`**

1. The data touched is unknown; the plan asks the data owner whether the extract holds applicant names before G1, and designs to work without them.
2. The build uses a synthetic stand-in for the extract; no real data enters it (ADR-0024).
3. Time to decision is computed deterministically by application type, with its start and end events defined.
4. H2 is tested as the brief says: a past month's figures reconciled against that month's hand-built spreadsheet.
5. Application types near the service standard are flagged, with the threshold in configuration and documented.
6. The weekly refresh needs no manual cleaning, and a change in the extract's shape fails loudly.
7. The budget is unknown; the plan estimates build and running cost and asks Tom for a budget before G2.
8. H1 and H3 have no measure; the plan proposes one for each.

## Precision

Three briefs, one run each: three paired comparisons. No statistical test separates two paths at that size; even three wins in three has a one-sided sign-test p of 0.125. The rule is a screen that asks for a consistent, visible advantage on every axis, not a proof. Run-to-run variation is unknown with one run per brief, so a single bad run can decide a brief; the result reports which criteria were met narrowly. Slice 6's thin path is a pilot. It runs one ticket, before the Council exists, to measure a brief's cost for the estimate, and it is not one of the comparisons.

## Budget

Nothing here spends. Before the first run, Tom sets a budget for the comparison in `config/kiln.yaml`, from an estimate built on slice 6's measured cost per brief (the sketch guesses about a dollar for one ticket). Each run reserves its cap through the spend ledger before it starts, and the judge's calls are metered the same way.

## Deviations

This file is approved at one hash and not edited after. A change before the first run is a new version with a new card; a change after it is disclosed in the result, in order, with what it changed (SOP §12). A failed or stopped run is recorded, not re-run quietly.

<!-- Rendered from the front matter by Kiln. Edit the front matter, then run `kiln records render`. -->
