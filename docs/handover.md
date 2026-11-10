# Handover: Kiln

For the next Claude Code session. Read [`CLAUDE.md`](../CLAUDE.md) first. Build only what Tom
asks for next; nothing that spends money is approved, because no budget is set.

**Status (2026-11-10):** phase 0, kickoff done. Recorded in D-001 to D-005, on branch
`claude/loving-johnson-8yysoc`. No pull request is open; Tom has not asked for one.

**Next free decision number: D-006**

## Where things stand

- **The rulebook:** `CLAUDE.md` (how to work with Tom, condensed from the SOP) and `AGENTS.md`
  (the engineering bar, for any coding agent).
- **The design:** [`docs/charter/`](charter/README.md) is the live charter, split from the
  seed by script. [`docs/adr/`](adr/README.md) holds ADR-0001 to ADR-0026, the seed's
  Appendix A. `GLOSSARY.md` holds 56 seeded terms.
- **The seeds** are sealed in `docs/repo-seeds/` with a hash manifest.
- **Code:** `src/kiln/` has the config loader, `kiln doctor` and `kiln records check`, with 42
  tests. CI runs lint, format, pyright, tests, the records check and gitleaks.
- **Not built:** every component of the shared core. The proposed order is
  [`docs/sketches/phase-0-shared-core.md`](sketches/phase-0-shared-core.md).
- **Reusable pieces:**
  - `kiln.errors.KilnError`: the one-line, exit-code-2 failure every command uses.
  - `kiln.config`: strict Pydantic config; copy its pattern for new config sections.
  - `kiln.doctor.run_checks`: add a service in `config/kiln.yaml`, not in code.
  - `kiln.records.check_all`: add a check here when a new kind of record appears.
  - `tests/conftest.py`: the fixture that refuses sockets.

## Open items

1. **The gitleaks job has not been seen to pass.** This session could not download and run
   the binary; CI's first run on the pushed branch is its test. Read that run before relying
   on it (D-001).
2. **`kiln doctor` checks Neon, R2, Modal and Brave by key name only.** Each gains a live
   check with its client, in slice 4 or 6 of the sketch.
3. **The glossary is a seed, not a grilled glossary.** Expect the grilling session to rename
   terms; rename them everywhere in the same commit.
4. **"Maturity target" in the chair's first slice** conflicts with ADR-0018 and ADR-0023
   (D-005, F3). Settle the wording when the chair's charter is grilled.
5. **How the reference build's data expert agent joins Kiln** is not in the seeds. The Data
   Engineer's charter ranks its source as background only. A question for phase 3.
6. **The skills setup has not run here.** When Tom runs `/setup-matt-pocock-skills`, it will
   add an "Agent skills" block to `CLAUDE.md` and write `docs/agents/`; keep both.
7. **The SOP's Part C was written for one knowledge-base agent.** Each expert's knowledge base
   should follow it, but the charter's stores differ from the reference build's (D-005, F2).

## For Tom

Each has a recommendation; most can be answered in a word. Detail is in D-005 unless another
entry is named.

1. **The phase 0 sketch.** Approve its build order? *Recommended: yes.* And grill the
   charter's front page and operating model before slice 1, or after? *Recommended: before.*
2. **The gate table** in `docs/charter/operating-model.md` is rebuilt from the charter's text,
   because the diagram was lost. Correct? Four places are marked *inferred* (D-003).
3. **The six exit tests** in `docs/charter/build-plan.md` are drafts, because the roadmap
   diagram was lost. Confirm, or send the originals (D-003).
4. **Secrets, before the session that needs them** (D-004): `NEON_DATABASE_URL`, `R2_BUCKET`,
   `MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET` for phase 0; an Anthropic key for Kiln and
   `BRAVE_API_KEY` for phase 1. The environment's network policy must allow each host.
5. **A Langfuse project for Kiln** (F1). The session's keys point at `data-expert-agent`.
   *Recommended: a new project, one for the whole Council.*
6. **Real-world test results** (R2): how do they come back to the Council? *Recommended:
   de-identified aggregates, produced by analysis code the Council writes and your team runs.*
7. **A separate verifier sets a ticket's `passes` flag,** and loops cannot edit what judges
   them (R3). *Recommended: adopt.*
8. **Provenance, not screening, is the control for tripwire 1,** and the brief is screened at
   intake (R4). *Recommended: adopt.*
9. **Files are the record; Postgres is an index** (F2). *Recommended: adopt.*
10. **The reading of the charter's two rules on silence** (R5): for what the charter names,
    the proposal gives detail; what it does not name is outside the first build. Correct?
11. **A budget, in dollars:** for phase 0's cents of sandbox and embedding calls, for the
    first eval sets, and an allowance for exploration without asking.
12. **Protect `main`:** require the `ci` checks and a CODEOWNERS review. It is a repository
    setting only you can make (D-001).
13. **The model heuristics** in `CLAUDE.md` are the SOP's table. Still yours?

## Conventions to keep

- Commit code, run it, then commit its outputs, so a run's record names a clean commit.
- `make check` before every commit. Never weaken a check to get one through.
- Dates in records are the session's date (UTC).
- Never edit a seed. Ruff is excluded from `docs/repo-seeds/` because it once reformatted a
  code block inside one (D-002).
- A recommendation is not an adoption. The charter, the ADRs and the defaults move only on
  Tom's word, in a commit of their own.
