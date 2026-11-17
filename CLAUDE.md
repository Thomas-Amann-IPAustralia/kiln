# CLAUDE.md — Kiln

@AGENTS.md

Kiln is Tom's software factory. A **Council** of seven expert agents plans and assures a
solution, a **coding swarm** builds it, and a **shared core** carries the records, gates and
sandboxes they all use. Solutions are often for Australian Government use. The Council hands
Tom's team a test-ready build; nothing reaches production before a real-world test and human
experts. Tom is the owner and is not a subject-matter expert: the work must stand up to an
expert's scrutiny without one in the room.

**Current scope: phase 0 of 6 (the shared core). Nothing in the shared core is built yet.**
The repo holds the rulebook, the records, the live charter, CI, two free commands (`kiln
doctor`, `kiln records check`) and one paid one (`kiln review`, a second opinion from another
provider's model). The phase 0 sketch,
[`docs/sketches/phase-0-shared-core.md`](docs/sketches/phase-0-shared-core.md), was revised
for D-008 (D-009) and waits for Tom's approval; build slice 1 once he gives it. The only budget is
Tom's $2 for a second opinion on the docs ($0.38 spent, D-007); **no other paid call is
approved**.

This file is the single source of truth for what is built and what is adopted. Update it in
the step that changes it. `AGENTS.md`, imported above, holds the rules every agent follows:
what Tom decides, when to stop and ask him, and the engineering bar.

## Start of every session

1. Read this file, [`docs/handover.md`](docs/handover.md) and the last few entries of
   [`docs/decisions.md`](docs/decisions.md). Note the next free decision number.
2. Run `git log --oneline -15` and `make check`.
3. Run `make doctor` if the step touches an outside service.
4. After a gap of weeks, also do SOP §9.1: check that the records still reproduce, and what
   moved outside the repo (providers' model pages, the skills repo, the sources).
5. Work on the branch the session names. Open a pull request only when asked.

## How we work

The full method is the SOP, [`docs/repo-seeds/sop-agent-construction-v3.md`](docs/repo-seeds/sop-agent-construction-v3.md),
Part A. Read it once. What follows is the part to keep in mind every turn.

**Tom's attention is the scarce resource.** He often reads on a phone: the reply, the decision
entry, the report, rarely the code. Spend it on his five decisions (`AGENTS.md`) and nothing
else.

**One request, one complete turn** (SOP §2): find what is already known; answer from free
evidence first; fix the yardstick before the numbers; build with tests; verify without
spending; stop at a gate that needs money or adoption, with an estimate and a recommendation;
read the output yourself; record; reply.

**Act, record, measure, flag or ask** (SOP §3):

- An engineering choice inside the step: **do it,** and write a decision entry if it is not
  obvious.
- A trade-off data can settle: **measure it,** against a rule fixed before the numbers.
- A contract others will consume (an id, a schema, a trace name): **settle it before its
  first consumer.**
- A new major component: **sketch it** (`docs/sketches/`) with a build order; Tom approves.
- Paid work Tom has agreed in aim but not funded: **build it up to the gate,** nothing sent.
- A risk, gap, contradiction or cost Tom would want to weigh: **flag it once,** with a
  recommendation, and carry on with whatever it does not affect.
- Your own earlier number or reading was wrong: **correct it at once,** in the reply and in
  the record.
- Tom's request looks wrong for his goal: **push back once, with evidence.**

**A flag has six parts** (SOP §4, template T4): what was found; the evidence; why it matters;
the options and their costs; a recommendation; what is needed from Tom. Flag once, then carry
it under "For Tom" in the handover until it is settled.

**Recommendation, then adoption** (SOP §5). A measurement or a review ends in a
recommendation. Adoption is Tom's, and it is its own decision entry and its own commit, which
updates this file, the config, the charter or ADR, and the handover together. Defaults and
the charter do not move until then. A deferral is a decision too: record what would reopen it.

**Replies** (SOP §8): the outcome in one line; the result in numbers; the spend against the
budget; a recommendation; what is open for Tom; where the detail is. Plain English. Never
claim more than was verified.

**Putting a decision to Tom** (ADR-0030). Ask for at most five things at once, the ones that
block the next step first, and mark the rest as able to wait. For each, give a decision card:

- the question, answerable in a word or two;
- the options, and what each would cost or change;
- your recommendation, and any dissent;
- whether it can be undone, and what happens if Tom does not answer;
- exactly what he is approving: the file and its commit, or the record and its hash.

**The friction log.** When Tom needs something explained twice, asks what a term means,
reverses a decision he misread, or answers a different question from the one asked, add one
line to [`docs/friction-log.md`](docs/friction-log.md) in that turn.

## How we know

- **Climb the evidence ladder only as far as the decision needs** (SOP §11): read the docs and
  the code; fixture tests; real data with no API; replays of recorded runs; probes for cents;
  a smoke test on the real transport; the budgeted run; reading outputs by hand; checking the
  instrument.
- **Check a fact at its source before building on it.** A seed can be out of date: two of
  the charter's details were (D-004), and so was a provider's price list until a smoke test
  showed an unpriced bucket (D-007).
- **Every claim carries a basis:** observed, authoritative, rule, supported, inferred, assumed
  or unknown. A dated policy fact from a seed is `assumed` until verified at its source.
- **Experiments** follow SOP §12: the grid, the choice rule and the headline are committed
  before any real number; choose on dev, report on test; a judge never shares the model family
  it grades and is checked on answers with known faults before its grades are trusted.
- **Money** follows SOP §14 and `AGENTS.md`: every paid response is cached and committed, and
  every decision entry records its spend, failed runs included.
- **A review by the model that wrote the work is a self-review.** For an independent one, use
  `kiln review` with another provider, within a budget Tom set.

## Documents and precedence

This file and `AGENTS.md`, then [`docs/charter/`](docs/charter/README.md), then the ADRs in
[`docs/adr/`](docs/adr/README.md), then the proposals in `docs/repo-seeds/`, which are detail
only: read [`docs/charter/proposal-map.md`](docs/charter/proposal-map.md) first. The SOP
governs how we work and how we know; the charter governs what the Council is. Where they
differ on technology, the charter wins on where things live and the SOP on how things are
measured and adopted (D-005, F2).

## Records

| Record | Where | Rule |
| --- | --- | --- |
| Decision log | [`docs/decisions.md`](docs/decisions.md), `D-NNN` | Append-only. A correction is a new entry or a commit that names what it corrects. Each entry says whose decision it was and what it spent. |
| ADRs | [`docs/adr/`](docs/adr/README.md), `ADR-NNNN` | Standing design rulings. Superseded, never rewritten. A new one lands with the decision entry that adopts it. |
| Handover | [`docs/handover.md`](docs/handover.md) | One note, kept current as a whole. Close the items an update settles in the same commit. |
| Glossary | [`GLOSSARY.md`](GLOSSARY.md) | The one vocabulary. No implementation detail. |
| Friction log | [`docs/friction-log.md`](docs/friction-log.md) | One line each time Tom and Kiln miss each other. |
| Sketches | `docs/sketches/` | A design proposed for Tom's approval before a major component is built. |
| Reviews | `docs/reviews/` | Second opinions: the spec, the answer and the cached response with its cost. |
| Seeds | `docs/repo-seeds/` | Sealed inputs, with a hash manifest. |

`kiln records check` checks that these agree in structure, in CI and before each commit:
numbering, dates, the index, the seed hashes and links. It cannot check that they agree in
meaning; a second opinion found two rules that contradicted each other (D-007).

Dates in records are the session's date (UTC). Commit code first, then run it, then commit its
outputs, so a run's record names a clean commit.

## Claude Code sessions in the cloud

- **Where the session's proxy injects a key,** leave the variable unset or set it to a
  placeholder. Never ask Tom to paste a secret into chat.
- **The session acts on GitHub under Tom's own account.** That is why no agent merges
  (ADR-0028): GitHub cannot tell the difference.
- **The container is ephemeral.** Commit and push everything worth keeping, and checkpoint
  long runs as they go.

## Model choice (Tom's heuristics, from SOP §14.3, until he changes them)

| Work | Model |
| --- | --- |
| High-volume extraction and classification | A small, cheap model, behind validation checks |
| The same, when errors are costly | A strong model at low effort |
| General production work | A strong model at medium or high effort |
| Sophisticated agentic execution | A Claude model at medium or high effort |

Keep a second model family wherever it checks the first. Check model ids, prices and limits on
the provider's own page before configuring them.

## Future state (context only — do not build yet)

The rest of the Council, in the order of [`docs/charter/build-plan.md`](docs/charter/build-plan.md),
with the single-session baseline after phase 1 (ADR-0029). Each expert's knowledge base follows
the SOP's Part C, and tracing its eight conventions (§20.0). Shape today's outputs for them;
build only the current step.

## End of every session

- This file's current scope is accurate.
- The handover is current as a whole: status, open items, Tom's items, the next free decision
  number.
- `make check` passes, and everything is pushed.
