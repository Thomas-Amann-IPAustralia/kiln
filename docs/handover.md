# Handover: Kiln

For the next Claude Code session. Read [`CLAUDE.md`](../CLAUDE.md) first. Build only what Tom
asks for next; nothing that spends money is approved, because no budget is set.

**Status (2026-11-17):** phase 0. Kickoff done, reviewed twice, and five recommendations adopted. Recorded in D-001 to D-009,
merged to `main` by Tom in pull request #2. `main` is protected by a ruleset Tom added
(ADR-0028); GitHub reports the branch as protected, but this session cannot read the
ruleset's settings, so which checks it requires is unverified.

**Next free decision number: D-010**

## Where things stand

- **The rulebook:** `CLAUDE.md` (how to work with Tom, condensed from the SOP) and `AGENTS.md`
  (the engineering bar, for any coding agent).
- **The design:** [`docs/charter/`](charter/README.md) is the live charter, split from the
  seed by script. [`docs/adr/`](adr/README.md) holds ADR-0001 to ADR-0026, the seed's
  Appendix A. `GLOSSARY.md` holds 56 seeded terms.
- **The seeds** are sealed in `docs/repo-seeds/` with a hash manifest.
- **Code:** `src/kiln/` has the config loader, `kiln doctor`, `kiln records check` and
  `kiln review`, with their tests. CI runs lint, format, pyright, tests, the records check and
  gitleaks.
- **Second opinion:** two OpenAI reviews of the docs, in `docs/reviews/2026-11-17-docs/`, for
  $0.38 of a $2 budget (D-007).
  CI's first run passed both jobs on commit `8f4b596`, which is the first time the gitleaks
  job ran anywhere (D-001 could not run it in the session).
- **Not built:** every component of the shared core. The proposed order is
  [`docs/sketches/phase-0-shared-core.md`](sketches/phase-0-shared-core.md).
- **Reusable pieces:**
  - `kiln.errors.KilnError`: the one-line, exit-code-2 failure every command uses.
  - `kiln.config`: strict Pydantic config; copy its pattern for new config sections.
  - `kiln.doctor.run_checks`: add a service in `config/kiln.yaml`, not in code.
  - `kiln.records.check_all`: add a check here when a new kind of record appears.
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

## For Tom

You adopted D-007's five recommendations (D-008) and protected `main`. **One thing starts the next step:**

1. **Approve the revised phase 0 sketch,**
   [`docs/sketches/phase-0-shared-core.md`](sketches/phase-0-shared-core.md), as revised in D-009.
   *Recommended: yes.* Approving it starts slice 1 and nothing else. It can be undone: no code
   exists yet. If you do not answer, nothing is built.
**These can wait.** Nothing is built on them until you answer.

2. **The gate table** in `docs/charter/operating-model.md` was rebuilt from text; four places
   are marked *inferred*. Correct? (D-003)
3. **The six draft exit tests** in `docs/charter/build-plan.md`: confirm, or send the
   originals. (D-003)
4. **Secrets, before the session that needs them:** `NEON_DATABASE_URL`, `R2_BUCKET`,
   `MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET`; later an Anthropic key and `BRAVE_API_KEY`. (D-004)
5. **A Langfuse project for Kiln.** The session's keys point at `data-expert-agent`.
   *Recommended: a new one.* (D-005 F1)
6. **Four design rulings from D-005:** real-world results come back as de-identified
    aggregates (R2); provenance, not screening, guards tripwire 1 (R4); files are the record
    and Postgres an index (F2); and the reading of the charter's rules on silence (R5).
    *Recommended: yes to each.*
7. **A budget** for phase 0's cents of sandbox and embedding calls, and an allowance for
    exploration. $1.62 of the second-opinion budget is unspent; it is kept for that purpose.
8. **Evaluation policy:** the SOP chooses models on the test split (§20.5) but says "choose on
    dev, report on test" (§12). *Recommended: choose on dev, always.* (D-007)
9. **The model heuristics** in `CLAUDE.md` are the SOP's table. Still yours?
10. **How approvals are made unforgeable,** before any loop runs unattended (ADR-0028): a
    separate GitHub identity for agents, or approvals signed with a key that never enters a
    cloud session. *Recommended: decide when the sketch's verifier slice is built.*

## Conventions to keep

- Commit code, run it, then commit its outputs, so a run's record names a clean commit.
- `make check` before every commit. Never weaken a check to get one through.
- Dates in records are the session's date (UTC).
- Never edit a seed. Ruff is excluded from `docs/repo-seeds/` because it once reformatted a
  code block inside one (D-002).
- A recommendation is not an adoption. The charter, the ADRs and the defaults move only on
  Tom's word, in a commit of their own.
