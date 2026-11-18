# Handover: Kiln

For the next Claude Code session. Read [`CLAUDE.md`](../CLAUDE.md) first. Build only what Tom
asks for next; nothing that spends money is approved beyond the $2 second-opinion budget.

**Status (2026-11-18):** phase 0. Tom approved the phase 0 sketch (D-010). Slice 1 of 9 is
built (D-011) on branch `ccr-d620ebdd-x20kar`, not yet merged; no pull request is open. D-001
to D-009 are merged to `main` (pull request #2). `main` is protected by a ruleset
Tom added (ADR-0028); GitHub reports the branch as protected, but this session cannot read the
ruleset's settings, so which checks it requires is unverified.

**Next free decision number: D-012**

## Where things stand

- **The rulebook:** `CLAUDE.md` (how to work with Tom, condensed from the SOP) and `AGENTS.md`
  (the engineering bar, for any coding agent).
- **The design:** [`docs/charter/`](charter/README.md) is the live charter, split from the
  seed by script. [`docs/adr/`](adr/README.md) holds ADR-0001 to ADR-0026, the seed's
  Appendix A, and ADR-0027 to ADR-0030, adopted in D-008. `GLOSSARY.md` holds 59 terms: 56
  seeded, and *decision card*, *approval* and *build session* added in D-011.
- **The seeds** are sealed in `docs/repo-seeds/` with a hash manifest.
- **Code:** `src/kiln/` has the config loader, `kiln doctor`, `kiln records check` and
  `render`, `kiln review` and `kiln approvals`, with their tests. CI runs lint, format,
  pyright, tests, the records check and gitleaks.
- **Slice 1 (D-011):** the enums (`kiln.vocabulary`), the id formats (`kiln.ids`), the
  project profile (`kiln.profile`), decision records and their store
  (`kiln.decision_records`), decision cards (`kiln.cards`) and approvals read from history
  (`kiln.approvals`). Three synthetic sample briefs in `evals/sample-briefs/`, drafts until
  Tom approves the set. The first card, [`docs/cards/`](cards/), records Tom's approval of
  the sketch; it takes effect when he merges it.
- **Second opinion:** two OpenAI reviews of the docs, in `docs/reviews/2026-11-17-docs/`, for
  $0.38 of a $2 budget (D-007).
  CI's first run passed both jobs on commit `8f4b596`, which is the first time the gitleaks
  job ran anywhere (D-001 could not run it in the session).
- **Not built:** slices 2 to 9 of the approved order,
  [`docs/sketches/phase-0-shared-core.md`](sketches/phase-0-shared-core.md). Next is slice 2
  (gates) or slice 3 (scanners and the spend ledger); 3, 4 and 9 need no money or secrets.
- **Reusable pieces:**
  - `kiln.errors.KilnError`: the one-line, exit-code-2 failure every command uses.
  - `kiln.config`: strict Pydantic config; copy its pattern for new config sections.
  - `kiln.doctor.run_checks`: add a service in `config/kiln.yaml`, not in code.
  - `kiln.records.check_all`: add a check here when a new kind of record appears.
  - `kiln.recordfile`: one file per record, front matter then rendering. Use it for tickets,
    findings and obligations rather than a new format.
  - `kiln.approvals.read_approvals`: G2's question "is this plan approved, at this hash?"
  - `kiln.model.Record`, `Text`, `Unknown`: the base and field types every record uses.
  - `tests/conftest.py`: the fixture that refuses sockets.
  - `kiln review`: a spec in, a cached and costed answer out. Use it for the cross-provider
    reviewer before G2 (ADR-0026) rather than writing a second client.

## Open items

1. **`kiln doctor` checks Neon, R2, Modal and Brave by key name only.** Each gains a live
   check with its client, in slice 4 or 6 of the sketch.
2. **The glossary is a seed, not a grilled glossary.** Expect the grilling session to rename
   terms; rename them everywhere in the same commit.
3. **"Maturity target" in the chair's first slice** conflicts with ADR-0018 and ADR-0023
   (D-005, F3). Settle the wording when the chair's charter is grilled.
4. **How the reference build's data expert agent joins Kiln** is not in the seeds. The Data
   Engineer's charter ranks its source as background only. A question for phase 3.
5. **The skills setup has not run here.** When Tom runs `/setup-matt-pocock-skills`, it will
   add an "Agent skills" block to `CLAUDE.md` and write `docs/agents/`; keep both.
6. **The SOP's Part C was written for one knowledge-base agent.** Each expert's knowledge base
   should follow it, but the charter's stores differ from the reference build's (D-005, F2).
7. **`kiln review`'s second request got no cache hit,** though its first 17 documents matched
   the first request's exactly. Under OpenAI's default caching both paid the write premium for
   nothing (about $0.056). Before the next multi-request review, smoke-test documents and
   question as separate input items (D-007).
8. **G0's readiness checks belong to slice 2:** that a profile's hypotheses cover
   desirability, viability and feasibility, and which `unknown`s may pass G0 (D-011).
9. **`kiln approvals` is not in CI.** CI's checkout is shallow and has no `origin/main`. Adding
   it means `fetch-depth: 0` in `.github/workflows/ci.yml`, a control-plane change for a pull
   request Tom reviews. Worth doing with slice 2, when G2 starts to depend on approvals.
10. **CI does not run on pushes to this session's branch.** The workflow runs on pushes to
    `main` and `claude/**`, and on pull requests; this branch is `ccr-*`. CI runs once a pull
    request is open. Every check it runs passed here.
11. **The data kinds in the profile** are the Governance proposal's list plus `public` and
    `internal`. The Governance Guru refines them in phase 2; the grilling may rename them.

## For Tom

You approved the phase 0 sketch (D-010), and slice 1 is built (D-011). Nothing blocks the
next slice. When you are ready, ask for a pull request: merging it is what puts `CARD-0001`,
your approval of the sketch, into effect.

**These can wait.** Nothing is built on them until you answer.

1. **The gate table** in `docs/charter/operating-model.md` was rebuilt from text; four places
   are marked *inferred*. Correct? (D-003)
2. **The six draft exit tests** in `docs/charter/build-plan.md`: confirm, or send the
   originals. (D-003)
3. **Secrets, before the session that needs them:** `NEON_DATABASE_URL`, `R2_BUCKET`,
   `MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET`; later an Anthropic key and `BRAVE_API_KEY`. (D-004)
4. **A Langfuse project for Kiln.** The session's keys point at `data-expert-agent`.
   *Recommended: a new one.* (D-005 F1)
5. **Four design rulings from D-005:** real-world results come back as de-identified
    aggregates (R2); provenance, not screening, guards tripwire 1 (R4); files are the record
    and Postgres an index (F2); and the reading of the charter's rules on silence (R5).
    *Recommended: yes to each.*
6. **A budget** for phase 0's cents of sandbox and embedding calls, and an allowance for
    exploration. $1.62 of the second-opinion budget is unspent; it is kept for that purpose.
7. **Evaluation policy:** the SOP chooses models on the test split (§20.5) but says "choose on
    dev, report on test" (§12). *Recommended: choose on dev, always.* (D-007)
8. **The model heuristics** in `CLAUDE.md` are the SOP's table. Still yours?
9. **How approvals are made unforgeable,** before any loop runs unattended (ADR-0028): a
    separate GitHub identity for agents, or approvals signed with a key that never enters a
    cloud session. *Recommended: decide when the sketch's verifier slice is built.*
10. **How you merge.** Use "Create a merge commit", as you did for pull request #2, or
    "Squash and merge". "Rebase and merge" can make `kiln approvals` report an approval as
    lapsed when it is not: safe, but noise. The ruleset can allow only the first two. (D-011)
11. **The three sample briefs** in `evals/sample-briefs/`: approve them as the chair's first
    evaluation set, or ask for changes. Needed before phase 1's first run, not before.

## Conventions to keep

- Commit code, run it, then commit its outputs, so a run's record names a clean commit.
- `make check` before every commit. Never weaken a check to get one through.
- Dates in records are the session's date (UTC).
- Never edit a seed. Ruff is excluded from `docs/repo-seeds/` because it once reformatted a
  code block inside one (D-002).
- A recommendation is not an adoption. The charter, the ADRs and the defaults move only on
  Tom's word, in a commit of their own.
