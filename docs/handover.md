# Handover: Kiln

For the next Claude Code session. Read [`CLAUDE.md`](../CLAUDE.md) first. Build only what Tom
asks for next; nothing that spends money is approved beyond the $2 second-opinion budget.

**Status (2026-11-22):** phase 0. Tom approved the phase 0 sketch (D-010). Slices 1 to 4 of 9
are built and merged to `main` (D-011 to D-014), in pull requests #3, #4 and #5. `main` is
protected by a ruleset Tom added (ADR-0028); this session cannot read its settings, so which
checks it requires is unverified.

**For a reader who wants the whole picture on one page:**
[`docs/kiln-explained.html`](kiln-explained.html), a self-contained explainer of what is built,
what is planned and why, written at `9f9a138` on 2026-11-22. It is a dated snapshot, not a record:
this note and `CLAUDE.md` stay authoritative, and it is not updated with each slice.

**Next free decision number: D-015**

## Where things stand

- **The rulebook:** `CLAUDE.md` (how to work with Tom, condensed from the SOP) and `AGENTS.md`
  (the engineering bar, for any coding agent).
- **The design:** [`docs/charter/`](charter/README.md) is the live charter, split from the
  seed by script. [`docs/adr/`](adr/README.md) holds ADR-0001 to ADR-0026, the seed's
  Appendix A, and ADR-0027 to ADR-0030, adopted in D-008. `GLOSSARY.md` holds 65 terms: 56
  seeded, three added in D-011, four in D-013 and two in D-014 (*verification step*, *verifier*).
- **The seeds** are sealed in `docs/repo-seeds/` with a hash manifest.
- **Code:** `src/kiln/` has the config loader, `kiln doctor`, `kiln records check` and
  `render`, `kiln review`, `kiln approvals`, `kiln gates`, `kiln scan`, `kiln spend` and
  `kiln verify`, with their tests (344). CI runs lint, format, pyright, tests, the records check,
  gitleaks and the three scanners, on `main`, `claude/**` and `ccr-**` branches and on pull
  requests.
- **Slice 1 (D-011):** the enums (`kiln.vocabulary`), the id formats (`kiln.ids`), the
  project profile (`kiln.profile`), decision records and their store
  (`kiln.decision_records`), decision cards (`kiln.cards`) and approvals read from history
  (`kiln.approvals`). Three synthetic sample briefs in `evals/sample-briefs/`, drafts until
  Tom approves the set.
- **Slice 2 (D-012):** the gates, G0 to G5 (`kiln.gates`, `kiln gates`), on LangGraph 1.2.19,
  with the artefacts each gate reads (`kiln.artefacts`). Passes are recomputed, never stored.
  Tom's gates pass on a decision card with a `gate` field, approved at the files' current
  hashes. LangSmith tracing is switched off in code.
- **Slice 3 (D-013):** the scanner baseline, Semgrep CE 1.183.0, OSV-Scanner v2.7.0 and Trivy
  v0.76.1, in CI job `scanners`, each with a seeded finding it must detect; one finding format
  (`kiln.findings`) and one dismissal list, [`config/dismissals.yaml`](../config/dismissals.yaml).
  And the spend ledger, [`docs/spend/ledger.jsonl`](spend/ledger.jsonl) (`kiln.spend`,
  `kiln spend`): every paid call reserves its bound and settles at its cost. It holds the three
  reviews of D-007: $0.3792 of the $2 budget.
- **Slice 4 (D-014):** tickets and the verifier.
  - *Tickets:* `council/tickets.json` in a solution (`kiln.tickets`): each ticket's description,
    contract, blockers and verification steps, which are commands; the checks every commit must
    pass, some of them tripwire checks; and extra read-only paths. It holds no pass. Tom's G2
    card rests on it.
  - *The verifier* (`kiln.verifier`, `kiln verify COMMIT --runner local`): reads the build
    contract at the branch's base on `main`'s first-parent history; refuses a commit that changes
    anything in `council/`, a contract the plan names or a read-only path, before any of its code
    runs; runs every check and each ticket's steps, each in its own clean clone, under an
    environment allowlist and a timeout; and writes `council/build.yaml`, which only it writes.
    G3 reads that record and rechecks it against history.
  - *Checked:* 29 deliberate breaks each failed a test; all six scans pass here. *On GitHub*
    (observed): run 19, on commit `0569fd7`, passed all three jobs. The `scanners` job took 5
    minutes 14 seconds, 4 minutes 14 of them building the Go tools; every repo scan passed, with
    the new dismissals, and every seeded finding was detected.
  - *Dismissals:* now four. The two new ones are the verifier's step runner, which Semgrep flags
    for running commands that are not literals (that is its job), and CVE-2026-115563, a new high
    advisory against Semgrep's own `mcp` pin in code `semgrep scan` never loads (D-014).
- **Second opinion:** two OpenAI reviews of the docs, in `docs/reviews/2026-11-17-docs/`, for
  $0.38 of a $2 budget (D-007).
- **Not built:** slices 5 to 9 of the approved order,
  [`docs/sketches/phase-0-shared-core.md`](sketches/phase-0-shared-core.md). Slice 5 (the
  sandbox) needs Modal's secrets and a budget of cents; slice 9 (eval sets) needs neither.
- **Reusable pieces:**
  - `kiln.errors.KilnError`: the one-line, exit-code-2 failure every command uses.
  - `kiln.config`: strict Pydantic config; copy its pattern for new config sections.
  - `kiln.doctor.run_checks`: add a service in `config/kiln.yaml`, not in code.
  - `kiln.records.check_all`: add a check here when a new kind of record appears.
  - `kiln.recordfile`: one file per record, front matter then rendering, and `write_atomic`.
  - `kiln.git.Git`: the one reader of git history. Use it rather than calling git directly.
  - `kiln.approvals.read_approvals`: every card's approval, read from history.
  - `kiln.gates.validate(gate, workspace)`: one gate, from the files as they are now. The
    thin path in slice 6 calls this, not a stored pass.
  - `kiln.artefacts.parse_yaml`: an artefact's bytes to its model, failing in one line.
  - `kiln.tickets.parse_tickets`: a ticket list's bytes, strict JSON, to its model.
  - `kiln.verifier.verify` and `recheck`: a commit judged, and a record rechecked. A runner is
    a `CommandRunner`; slice 5's sandbox is a second one beside `run_command`.
  - `kiln.model.Record`, `Text`, `Unknown`: the base and field types every record uses.
  - `kiln.spend.reserve` and `settle`: the only way a paid call spends. Slice 5's sandbox
    reserves each run's cap here.
  - `kiln.findings`: the finding format and its readers. A new scanner adds a reader here.
  - `tests/conftest.py`: the fixture that refuses sockets. `tests/solution.py`: a synthetic
    build contract and a loop's work on it.
  - `kiln review`: a spec in, a cached and costed answer out. Use it for the cross-provider
    reviewer before G2 (ADR-0026) rather than writing a second client.

## Open items

1. **`kiln doctor` checks Neon, R2, Modal and Brave by key name only.** Each gains a live
   check with its client, in slice 5 or 7 of the sketch.
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
8. **What the verifier leaves for slices 5 and 6** (D-014):
   - *It runs a commit's code on the machine it runs on.* `--runner local` is for code no agent
     wrote until slice 5's sandbox is a second runner. Only the environment allowlist stands
     between the code and the machine.
   - *The record must stay off the loop's branch while the loop works.* Committed there, it would
     make the loop's next commit differ from the base in `council/` and be refused. Slice 6 runs
     the verifier in a clone of its own and commits the record when the loop is done.
   - *Each command builds its own environment* in its own clone, so a `uv run` step is slower than
     in a shared checkout. Submodules are not checked out.
   - *The order of the tickets is their priority,* but nothing picks the next one yet; the loop
     does that in slice 6, and a rule should if one can (deterministic first).
9. **`kiln approvals` is not in CI.** CI's checkout is shallow and has no `origin/main`. Adding
   it means `fetch-depth: 0` in `.github/workflows/ci.yml`, a control-plane change for a pull
   request Tom reviews. `kiln gates` and `kiln verify` read history the same way. Worth doing
   before slice 6, when a real solution starts to depend on them.
10. **The data kinds in the profile** are the Governance proposal's list plus `public` and
    `internal`. The Governance Guru refines them in phase 2; the grilling may rename them.
11. **LangGraph's packages are held to uploads before 2026-11-04** in `pyproject.toml`. To
    upgrade one, move its date deliberately and review the lockfile diff (D-012). OSV-Scanner's
    scans of `uv.lock` have found no known vulnerability (D-013, D-014).
12. **What the scanners leave for later** (D-013, D-014):
    - Trivy's vulnerability scanning is off, since it would repeat OSV-Scanner's on `uv.lock`;
      turn it on when there is a container image to scan. Trivy does not write the CycloneDX
      SBOM yet, which the Security Architect's charter gives it; it belongs with G4's
      pre-release record.
    - The scanners' own reports are not kept as CI artifacts; the log holds Kiln's summary and
      each report's hash.
    - Semgrep's 13 medium findings in `src/` are printed on every run. D-013 read each and found
      none real; they are not dismissed, because medium does not block. The same goes for five
      medium advisories against Semgrep's own `mcp` and `opentelemetry-api`. Two `high` ones
      against `mcp` are dismissed; both go stale when a Semgrep release moves off `mcp==1.29.0`.
      Semgrep 1.186.0 (2026-11-18) has not.
    - `unknown` blocks, an inferred reading of the charter. The Security Architect revisits the
      blocking set, and the severity mapping, in its first slice.
    - The `scanners` job builds two Go tools on every run (about six minutes). Cache them with
      `actions/cache` if the wait gets in the way.
13. **The ledger's lock needs POSIX** (Linux, macOS). Every machine Kiln runs on is one today.

## For Tom

Slice 4 is merged (pull request #5), with its dismissal of CVE-2026-115563, so `main`'s scanner
job no longer waits on it.

**For the next step.**

1. **Slice 5 or slice 9 next?** Slice 5 is the sandbox the verifier and the loop run in. It runs
   on Modal (modal.com), the cloud service the charter chose for running agent-written code
   (ADR-0007). It needs a Modal account and one API token from it, which comes as two values, a
   token ID and a token secret (`MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET`; authoritative, Modal's
   docs). They are saved in the environment's settings or a secure form, never in chat. It also
   needs a Kiln budget for its test runs. *Recommended: slice 5, with a $1 cap.* Modal's free plan
   includes $30 of use a month, and lists CPU at about $0.00004 per core-second, roughly 14 cents
   an hour (observed, modal.com/pricing, 2026-11-21); the exact sandbox rate is rechecked before
   any run. Slice 9, the eval sets, needs neither, and can come first if you would rather not set
   up Modal yet. (D-004, D-014)

**Due now, blocking nothing in phase 0.**

2. **How approvals and passes are made unforgeable** (ADR-0028), before any loop runs unattended.
   Both are files any agent working as you could write. Options: (a) a separate GitHub identity
   for agents, a GitHub App the sessions push as, so the ruleset lets only your account merge;
   (b) signatures, your approvals with a key on your own device, and the verifier's records with
   a key no agent's credentials reach; (c) wait, and keep every loop watched. *Recommended: (a)
   for approvals and the verifier's key from (b) for passes, decided now and built before the
   first unattended loop.* It can be undone. Without an answer, loops stay watched (HITL) and
   nothing runs unattended. (D-014)

**These can wait.** Nothing is built on them until you answer.

3. **The charter's layout line for tickets.** `agents/coding-swarm.md` says `tickets.json` holds
   "tickets with passes flags". The passes now live in `build.yaml`, which only the verifier
   writes, so the file you approve at G2 never changes when a ticket passes. *Recommended: amend
   the line to say so.* (D-014)
4. **The gate table** in `docs/charter/operating-model.md` was rebuilt from text; four places
   are marked *inferred*. Correct? The gates now run on that reading, plus three more inferred
   readings in D-012: G0 needs hypotheses covering D, V and F; G1 does not yet need the
   profile's `unknown`s resolved; G3 needs every ticket passing by the verifier's record. (D-003)
5. **The six draft exit tests** in `docs/charter/build-plan.md`: confirm, or send the
   originals. (D-003)
6. **Secrets, before the session that needs them:** `NEON_DATABASE_URL` and the R2 keys for
   slice 7; later an Anthropic key and `BRAVE_API_KEY`. (D-004)
7. **A Langfuse project for Kiln.** The session's keys point at `data-expert-agent`.
   *Recommended: a new one.* (D-005 F1)
8. **Four design rulings from D-005:** real-world results come back as de-identified
   aggregates (R2); provenance, not screening, guards tripwire 1 (R4); files are the record
   and Postgres an index (F2); and the reading of the charter's rules on silence (R5).
   *Recommended: yes to each.*
9. **An allowance for exploration,** beyond slice 5's budget. $1.62 of the second-opinion
   budget is unspent; it is kept for that purpose.
10. **Evaluation policy:** the SOP chooses models on the test split (§20.5) but says "choose on
    dev, report on test". *Recommended: choose on dev, always.* (D-007)
11. **The model heuristics** in `CLAUDE.md` are the SOP's table. Still yours?
12. **How you merge.** You used "Create a merge commit" for pull requests #2 to #4; keep to it,
    or "Squash and merge". "Rebase and merge" can make `kiln approvals` report an approval as
    lapsed when it is not: safe, but noise. The ruleset can allow only the first two. (D-011)
13. **The three sample briefs** in `evals/sample-briefs/`: approve them as the chair's first
    evaluation set, or ask for changes. Needed before phase 1's first run, not before.
14. **Two risks found in slice 3, for your awareness.** Nothing is needed unless you disagree.
    (D-013)
    - *Trivy, which the charter names, shipped a malicious release in March 2026*
      (CVE-2026-33634) that stole CI credentials. Kiln builds a later version from source,
      checked by Go's checksum database, gives it no credentials, and uses it only to check
      Dockerfiles and configuration. *Recommended: keep it on those terms.*
    - *The spend ledger is per git branch.* Two sessions spending at once on two branches could
      together pass a budget. *Recommended: fund one paid session at a time until slice 7 gives
      the ledger a shared home.*

## Conventions to keep

- Commit code, run it, then commit its outputs, so a run's record names a clean commit.
- `make check` before every commit. Never weaken a check to get one through.
- Dates in records are the session's date (UTC).
- Never edit a seed. Ruff is excluded from `docs/repo-seeds/` because it once reformatted a
  code block inside one (D-002).
- A recommendation is not an adoption. The charter, the ADRs and the defaults move only on
  Tom's word, in a commit of their own.
- A scanner finding is fixed, or dismissed in `config/dismissals.yaml` with a reason, never with
  the scanner's own ignore files (D-013).
