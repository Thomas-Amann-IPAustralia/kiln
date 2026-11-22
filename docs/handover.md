# Handover: Kiln

For the next Claude Code session. Read [`CLAUDE.md`](../CLAUDE.md) first. Build only what Tom
asks for next; nothing that spends money is approved beyond the $2 second-opinion budget.

**Status (2026-11-22):** phase 0. Tom approved the phase 0 sketch (D-010). Slices 1, 2, 3 and 9
of 9 are built. Slices 1 and 2 (D-011, D-012) were merged in pull request #3, which put
`CARD-0001` into effect (`kiln approvals` shows it approved at `5dd97e5`), and slice 3 (D-013)
in pull request #4 (observed). Slice 9 (D-014) is on branch `ccr-48174fb5-kwxmpb`, not yet
merged; no pull request is open. Tom chose slice 9 next because he has no time yet to set up
Modal, which slice 5 needs. `main` is protected by a ruleset Tom added (ADR-0028); this session
cannot read its settings, so which checks it requires is unverified.

**Next free decision number: D-015**

## Where things stand

- **The rulebook:** `CLAUDE.md` (how to work with Tom, condensed from the SOP) and `AGENTS.md`
  (the engineering bar, for any coding agent).
- **The design:** [`docs/charter/`](charter/README.md) is the live charter, split from the
  seed by script. [`docs/adr/`](adr/README.md) holds ADR-0001 to ADR-0026, the seed's
  Appendix A, and ADR-0027 to ADR-0030, adopted in D-008. `GLOSSARY.md` holds 65 terms: 56
  seeded, three added in D-011, four in D-013 (*spend ledger*, *severity*, *seeded finding*,
  *dismissal*) and two in D-014 (*golden question*, *single-session baseline*).
- **The seeds** are sealed in `docs/repo-seeds/` with a hash manifest.
- **Code:** `src/kiln/` has the config loader, `kiln doctor`, `kiln records check` and
  `render`, `kiln review`, `kiln approvals`, `kiln gates`, `kiln scan` and `kiln spend`, and the
  eval records (`kiln.evals`), with their tests (307). CI runs lint, format, pyright, tests, the records check, gitleaks and the
  three scanners, on `main`, `claude/**` and `ccr-**` branches and on pull requests.
- **Slice 1 (D-011):** the enums (`kiln.vocabulary`), the id formats (`kiln.ids`), the
  project profile (`kiln.profile`), decision records and their store
  (`kiln.decision_records`), decision cards (`kiln.cards`) and approvals read from history
  (`kiln.approvals`). Three synthetic sample briefs in `evals/sample-briefs/`, drafts until
  Tom approves the set.
- **Slice 2 (D-012):** the gates, G0 to G5 (`kiln.gates`, `kiln gates`), on LangGraph 1.2.19,
  with the artefacts each gate reads (`kiln.artefacts`). Passes are recomputed, never stored.
  Tom's gates pass on a decision card with a `gate` field, approved at the files' current
  hashes. LangSmith tracing is switched off in code.
- **Slice 3 (D-013):** the scanner baseline and the spend ledger.
  - *Scanners:* Semgrep CE 1.183.0 (rules from one `semgrep-rules` commit), OSV-Scanner v2.7.0
    and Trivy v0.76.1 (both built from their Go modules), in CI job `scanners`. Each runs on the
    repo and on its seeded finding in `tests/seeded-findings/`, which it must detect. One
    finding format (`kiln.findings`), one severity scale, and one dismissal list,
    [`config/dismissals.yaml`](../config/dismissals.yaml), which holds two entries: a Semgrep
    finding in `kiln.scanners`, and a high advisory against Semgrep's own `mcp` dependency that
    no Semgrep release can take the fix for yet. Critical, high and unknown findings block.
  - *Ledger:* [`docs/spend/ledger.jsonl`](spend/ledger.jsonl) (`kiln.spend`, `kiln spend`).
    Every paid call reserves its bound and settles at its cost; a call that could pass a cap is
    refused, and one that may reach 80% warns. `kiln review` uses it. It holds the three
    reviews of D-007: $0.3792 of the $2 budget.
  - *On GitHub* (observed): run 14, on commit `0588dc6`, passed all three jobs. The
    `scanners` job took 5 minutes 40 seconds, 4 minutes 41 of them building the Go tools; every
    repo scan passed and every seeded finding was detected. Run 13 had failed on the `mcp`
    advisory, which D-013's correction explains.
- **Slice 9 (D-014):** the first evaluation sets, drafts for Tom's approval.
  - *The Researcher's golden questions,*
    [`evals/golden-questions/researcher-first-slice.md`](../evals/golden-questions/researcher-first-slice.md):
    20 questions over the charter's five families and three more, the charter's eight dated
    claims first, each with a key, the points a complete answer covers and the sources it should
    cite, and a pass rule (17 of 20, and four hard rules). **14 keys are verified at source; 6
    are not,** because the DTA, PSPF and ASD sites refuse this cloud environment (open item 14).
    The three charter claims that could be checked are supported. The injected page is in
    `evals/golden-questions/pages/`.
  - *The baseline protocol,*
    [`evals/baseline/council-vs-single-session.md`](../evals/baseline/council-vs-single-session.md):
    ADR-0029's two paths, what is held equal, ten measures, a blinded judge from another model
    family, eight points per sample brief, and the rule, which is code (`kiln.evals.decide`).
  - `kiln records check` refuses a question whose charter sentence has changed under it.
- **Second opinion:** two OpenAI reviews of the docs, in `docs/reviews/2026-11-17-docs/`, for
  $0.38 of a $2 budget (D-007).
- **Not built:** slices 4 to 8 of the approved order,
  [`docs/sketches/phase-0-shared-core.md`](sketches/phase-0-shared-core.md). Slice 4 (tickets and
  the verifier) needs no money or secrets and can be next; slice 5 needs Modal.
- **Reusable pieces:**
  - `kiln.errors.KilnError`: the one-line, exit-code-2 failure every command uses.
  - `kiln.config`: strict Pydantic config; copy its pattern for new config sections.
  - `kiln.doctor.run_checks`: add a service in `config/kiln.yaml`, not in code.
  - `kiln.records.check_all`: add a check here when a new kind of record appears.
  - `kiln.recordfile`: one file per record, front matter then rendering. Use it for tickets,
    findings and obligations rather than a new format.
  - `kiln.approvals.read_approvals`: every card's approval, read from history.
  - `kiln.gates.validate(gate, workspace)`: one gate, from the files as they are now. The
    thin path in slice 6 calls this, not a stored pass.
  - `kiln.model.Record`, `Text`, `Unknown`: the base and field types every record uses.
  - `kiln.spend.reserve` and `settle`: the only way a paid call spends. Slice 5's sandbox
    reserves each run's cap here.
  - `kiln.findings`: the finding format and its readers. A new scanner adds a reader here.
  - `tests/conftest.py`: the fixture that refuses sockets.
  - `kiln.evals`: golden sets and the baseline protocol. A new agent's first eval set is a new
    `GoldenSet` file, not a new format. `decide` is the baseline's rule; phase 1's comparison
    calls it, never a re-reading of the protocol.
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
8. **G3 trusts `build.yaml` until slice 4.** Its ticket results are written by hand until the
   verifier becomes their only writer (ADR-0027). No real solution uses the gates before then.
9. **`kiln approvals` is not in CI.** CI's checkout is shallow and has no `origin/main`. Adding
   it means `fetch-depth: 0` in `.github/workflows/ci.yml`, a control-plane change for a pull
   request Tom reviews. `kiln gates` reads history the same way. Worth doing before slice 6,
   when a real solution starts to depend on them.
10. **The data kinds in the profile** are the Governance proposal's list plus `public` and
    `internal`. The Governance Guru refines them in phase 2; the grilling may rename them.
11. **LangGraph's packages are held to uploads before 2026-11-04** in `pyproject.toml`. To
    upgrade one, move its date deliberately and review the lockfile diff (D-012). OSV-Scanner's
    first scan of `uv.lock` found no known vulnerability (D-013).
12. **What the scanners leave for later** (D-013):
    - Trivy's vulnerability scanning is off, since it would repeat OSV-Scanner's on `uv.lock`;
      turn it on when there is a container image to scan. Trivy does not write the CycloneDX
      SBOM yet, which the Security Architect's charter gives it; it belongs with G4's
      pre-release record.
    - The scanners' own reports are not kept as CI artifacts; the log holds Kiln's summary and
      each report's hash.
    - Semgrep's 13 medium findings in `src/` are printed on every run. D-013 read each and found
      none real; they are not dismissed, because medium does not block. The same goes for five
      medium advisories against Semgrep's own `mcp` and `opentelemetry-api`, which wait for a
      Semgrep release that moves those pins; the `mcp` dismissal goes stale when it does.
    - `unknown` blocks, an inferred reading of the charter. The Security Architect revisits the
      blocking set, and the severity mapping, in its first slice.
    - The `scanners` job builds two Go tools on every run (about six minutes). Cache them with
      `actions/cache` if the wait gets in the way.
13. **The ledger's lock needs POSIX** (Linux, macOS). Every machine Kiln runs on is one today.
14. **Six golden keys are unverified, and the Researcher's main sources refuse this cloud
    environment** (D-014's flag). `www.digital.gov.au`, `www.protectivesecurity.gov.au`,
    `www.cyber.gov.au`, `www.finance.gov.au`, `www.naa.gov.au` and `www.industry.gov.au` fail
    upstream with network access unrestricted; OAIC and the Ombudsman serve bot challenges. In
    slice 5, probe them from Modal, where the Researcher will run. Until each of the six keys is
    checked at its source, the set is not ready to run.
15. **What slice 9 leaves for phase 1:** the runners for both sets, with the run-day check that
    refuses an unverified key or one older than 30 days; the judge's known-fault copies (SOP T9);
    Langfuse datasets (slice 7). The bytes each key was checked on are hashed, not stored: they
    belong in R2 once slice 7 and Tom's ruling on D-005 F2 allow.
16. **The eval sets are the keys.** The agent under test must not be able to read `evals/`
    during a run, and read-only GitHub access to this repo would let it. The runner must scope
    it out (a hard rule in the golden set). Once Tom approves a set, a card rests on its hash,
    so any edit lapses the approval loudly; adding `/evals/` to CODEOWNERS would also ask for his
    review on every change. A control-plane change, for a pull request when he wants it.

## For Tom

Slice 9 is built (D-014), at no cost. Nothing blocks slice 4, which needs no money or secrets.
When you are ready, ask for a pull request. It touches the control plane, which you review when
you merge: `CLAUDE.md`'s scope and records table, one line of `AGENTS.md`, and first move 9's
status in the build plan. These three are new; none blocks slice 4, and each
is needed before phase 1 runs anything.

1. **Approve the Researcher's golden questions and their pass rule?** File
   `evals/golden-questions/researcher-first-slice.md`. *Recommended: approve.* Six keys stay
   unverified until open item 14 is settled, so the set cannot run before then whatever you
   answer.
2. **Approve the baseline protocol and its thresholds?** File
   `evals/baseline/council-vs-single-session.md`: the Council wins only with no floor lost, a
   10-point lead on points covered, 2 of 3 pairwise wins and no loss, at most 3 times the cost
   and 2 times the time. *Recommended: approve, with one run per brief;* two runs per brief
   would halve the chance one bad run decides a brief, at twice the cost. Answering also
   answers item 14 below (the sample briefs), since the protocol runs on them.
3. **How should the six unverified keys be checked?** *Recommended: probe the sites from Modal
   in slice 5, and if refused there too, from a session on your own computer.* Nothing is
   needed now.

**These can wait.** Nothing is built on them until you answer.

4. **The gate table** in `docs/charter/operating-model.md` was rebuilt from text; four places
   are marked *inferred*. Correct? The gates now run on that reading, plus three more inferred
   readings in D-012: G0 needs hypotheses covering D, V and F; G1 does not yet need the
   profile's `unknown`s resolved; G3 trusts a hand-written build record until slice 4. (D-003)
5. **The six draft exit tests** in `docs/charter/build-plan.md`: confirm, or send the
   originals. (D-003)
6. **Secrets, before the session that needs them:** `NEON_DATABASE_URL`, `R2_BUCKET`,
   `MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET`; later an Anthropic key and `BRAVE_API_KEY`. (D-004)
7. **A Langfuse project for Kiln.** The session's keys point at `data-expert-agent`.
   *Recommended: a new one.* (D-005 F1)
8. **Four design rulings from D-005:** real-world results come back as de-identified
    aggregates (R2); provenance, not screening, guards tripwire 1 (R4); files are the record
    and Postgres an index (F2); and the reading of the charter's rules on silence (R5).
    *Recommended: yes to each.*
9. **A budget** for phase 0's cents of sandbox and embedding calls, and an allowance for
    exploration. $1.62 of the second-opinion budget is unspent; it is kept for that purpose.
10. **Evaluation policy:** the SOP chooses models on the test split (§20.5) but says "choose on
    dev, report on test". *Recommended: choose on dev, always.* (D-007)
11. **The model heuristics** in `CLAUDE.md` are the SOP's table. Still yours?
12. **How approvals are made unforgeable,** before any loop runs unattended (ADR-0028): a
    separate GitHub identity for agents, or approvals signed with a key that never enters a
    cloud session. *Recommended: decide when the sketch's verifier slice is built.*
13. **How you merge.** You used "Create a merge commit" for pull requests #2 to #4; keep to it,
    or "Squash and merge". "Rebase and merge" can make `kiln approvals` report an approval as
    lapsed when it is not: safe, but noise. The ruleset can allow only the first two. (D-011)
14. **The three sample briefs** in `evals/sample-briefs/`: approve them as the chair's first
    evaluation set, or ask for changes. Needed before phase 1's first run, not before.
15. **Two risks found in slice 3, for your awareness.** Nothing is needed unless you disagree.
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
