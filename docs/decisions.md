# Decision log

Events in building Kiln, in order: choices, measurements, spends, adoptions and deferrals.
Append-only. To change a decision, write a new entry that names the one it supersedes. Each
entry says whose decision it was and what it spent. Standing design rulings live in
[`docs/adr/`](adr/README.md); the entry that adopts one names it.

Template: SOP §27, T3.

## D-001 — The stack and tooling: Python 3.11, uv, ruff, pyright, pytest, with CI that needs no network (2026-11-10)

**Context.** The repo held a licence, a one-line README and the seeds. The SOP (§15.3, §24) and
the charter ("Practices to adopt from day one") both ask for backpressure before any feature
code: a type checker, tests, lint and hooks that block a commit.

**Decision (Claude; engineering inside the kickoff's scope).**

- **Python 3.11 as the floor, uv with a committed lockfile, ruff, pytest** (the SOP's
  defaults), plus **pyright in strict mode**, the first checker the charter names. 3.11 keeps
  code shareable with the reference build; nothing here needs a newer version.
- **One package, `src/kiln/`, with a typer CLI named `kiln`.** "Kiln" is the factory and this
  repo; "the Council" is the seven experts inside it (`GLOSSARY.md`).
- **Config in `config/kiln.yaml`,** validated by Pydantic with unknown keys as errors.
- **Two free commands, as the first code and the pattern for the rest:**
  - `kiln doctor` makes one read-only call to each outside service and exits 2 if a service
    the current phase needs does not answer. Base URLs come only from config, redirects are
    not followed, and no secret value is printed.
  - `kiln records check` verifies the decision log's numbering and dates, the ADRs and their
    index, the handover's next free number, the sealed seeds and every relative link in the
    live documents.
- **CI** (`.github/workflows/ci.yml`): lint, format check, pyright, pytest and the records
  check in one job; gitleaks over the whole history in another, installed from the release
  and verified against its published SHA-256. Actions are pinned to full commit SHAs, the
  token is read-only, and there is no privileged trigger.
- **`AGENTS.md` holds the engineering bar** for any coding agent, and `CLAUDE.md` imports it
  and adds how to work with Tom. The swarm will read `AGENTS.md`; the skills' setup step edits
  `CLAUDE.md` when it exists.
- **`.github/CODEOWNERS`** routes changes to the control plane (workflows, config, the
  charter, ADRs, seeds, the rulebook, the lockfile) to Tom.
- **Rejected:** a third-party action to install uv (one less thing to pin: `pip install uv`
  at a pinned version does it); mypy (one checker is enough); a regex-only secret check
  (kept as a second net in the tests, with gitleaks as the control).

**Checked.**

- 42 tests pass with sockets refused (`tests/conftest.py`), covering the config loader, the
  doctor against a mock transport, each records check against a fixture repo, the CLI's exit
  codes and the repo's hygiene. Ruff and pyright (strict) are clean.
- `kiln doctor` was run live (D-004). `kiln records check` passes on this repo.
- **Not checked here:** gitleaks itself. This session's permissions refused downloading and
  running an outside binary, so the gitleaks job is verified only by CI's first run on the
  pushed branch. The handover says how that run went.

**Spend:** $0.

**Consequences.** Every later slice inherits these checks. For Tom: protecting `main` so that
CI and a CODEOWNERS review are required is a repository setting only he can make (handover,
"For Tom").

## D-002 — Records and vocabulary: three numbered series, a root GLOSSARY.md, and sealed seeds (2026-11-10)

**Context.** The seeds name three kinds of decision record without relating them: the SOP's
decision log (`D-NNN`), the charter's ADRs from Appendix A, and the Council's decision store
(`DEC-NNNN`). The charter also asks for a `CONTEXT.md` glossary. A contract others will
consume is settled before its first consumer (SOP §3).

**Decision (Claude).**

- **Three series, each with one home and one meaning:**

  | Series | Home | Meaning |
  | --- | --- | --- |
  | `D-NNN` | `docs/decisions.md` | An event in building Kiln. Append-only. |
  | `ADR-NNNN` | `docs/adr/` | A standing ruling about what Kiln and the Council are. Superseded, never rewritten. |
  | `DEC-NNNN` | each solution's decision store | A decision the Council makes while building a solution. Not in this repo. |

  An adoption that changes the design is a `D` entry and a new ADR in one commit.
- **The glossary is `GLOSSARY.md` at the repo root,** in the format `mattpocock/skills` reads
  and maintains, because the skills renamed `CONTEXT.md` and now look only for the new name
  (D-004). It is seeded with 56 terms from the charter and the SOP, so that the first schemas
  have names to use. Tom's `/grill-with-docs` session sharpens it.
- **ADRs use the skills' format** (`docs/adr/NNNN-slug.md`, a title, a short ruling, a
  `status`), so the same session extends the folder instead of starting a second one.
- **The seeds are sealed.** `docs/repo-seeds/` stays byte for byte as Tom committed it, with a
  SHA-256 manifest and a README. `kiln records check` fails if a seed changes, appears or
  disappears. The live documents are derived from the seeds; a changed seed means the
  derivation is stale (SOP §16.5, applied to our own inputs).
- **One handover note,** `docs/handover.md`, kept current as a whole.
- **Rejected:** moving or renaming the seeds (Tom will look for them where he put them, and
  the charter may be exported again); status headers inside each proposal (they would break
  the seal; the proposal map carries them instead); a copy of the SOP at `docs/sop.md` (a
  second copy to drift; `CLAUDE.md` links the seed).

**A correction, in this session.** `ruff format .` rewrote a Python code block inside one
seed, `Governance Proposal.md`, and the manifest was first sealed after that, so it sealed the
changed file. Found by `git status` before anything was committed. The seed was restored from
git, ruff now excludes `docs/repo-seeds/`, and the manifest was resealed and compared with the
committed blobs: all 11 match.

**Checked.** `kiln records check` passes; its tests break each rule in turn.

**Spend:** $0.

**Consequences.** Seal a manifest only against what git holds. Dates in records are the session's date, which is UTC. Tom's local date can
be a day ahead (the review seed is named for 11 November).

## D-003 — The charter planted as live documents: 26 ADRs, and the two lost diagrams rebuilt as tables for Tom to confirm (2026-11-10)

**Context.** The charter is the controlling design, and its first moves are to grill it and to
turn Appendix A into ADRs. The seed is one 80 kB export in which the gate flow and the build
roadmap are placeholders (`[embedded content: …]`): what each gate checks and the six phases'
exit tests are not in any text (review, item 1).

**Decision (Claude: structure and reconstruction. The content marked for confirmation is
Tom's.)**

- **`docs/charter/` is the live charter,** split so that runtime agents do not carry the build
  method: a front page (purpose, precedence, the Council at a glance), the operating model,
  one file per agent, the build method, the build plan and the proposal map.
- **The text was carried over by script,** not retyped: the seed's 731 lines into 14 files and 26 ADRs, with
  only blank lines, heading levels and non-breaking spaces normalised. Every other departure
  is marked "Changed from the seed" in place and listed on the charter's front page.
- **Appendix A is ADR-0001 to ADR-0026,** one file per row, the ruling, the conflict and the
  reason unchanged, each marked `accepted` with the date of Tom's feedback the charter gives.
- **The gate flow is a table,** rebuilt from the charter's own sentences. Three cells and one
  loop are marked *inferred*: what passes G1, G3 and G5, and where a new round re-enters.
- **The build roadmap is a table.** The phases and what each builds are the charter's. **The
  six exit tests are drafts,** written from each agent's "first slice", because the seed's
  are lost.
- **The first moves have a status column,** and the skills install command is corrected
  (D-004).
- **No amendment was applied.** The review's recommended changes of substance are in D-005
  for Tom.

**Checked.** The split script asserted 26 Appendix A rows of three cells each. Every relative
link in the new files resolves (`kiln records check`).

**Spend:** $0.

**Consequences. For Tom:** confirm the gate table, and confirm or replace the six exit tests
(handover, "For Tom" 2 and 3). Until then both are working readings, not charter.

## D-004 — The environment and the tools, checked at source: three services answer, three are not configured, and two charter details were out of date (2026-11-10)

**Context.** SOP §15.4: check the environment in the first hour. The review also asked for the
charter's skills details to be checked against the skills repo.

**Decision (Claude; free evidence only).** One read-only call per service through `kiln
doctor`, plus two manual probes. Nothing was written to any service.

**Results.**

| Service | Needed from | Result |
| --- | --- | --- |
| Langfuse (`cloud.langfuse.com`) | phase 0 | Answers. The injected keys belong to a project named `data-expert-agent`. |
| Cloudflare R2 | phase 0 | The keys are present and the endpoint accepts them, but they are scoped to a bucket and no bucket name is set (`ListBuckets` is refused). Checked by hand with boto3. |
| Neon | phase 0 | Not configured: no `NEON_DATABASE_URL`. |
| Modal | phase 0 | Not configured: no `MODAL_TOKEN_ID` or `MODAL_TOKEN_SECRET`. |
| OpenAI | phase 1 | Answers; lists `gpt-6-luna`, `gpt-6-sol`, `gpt-6.1-sol` among 96 models. |
| Gemini | phase 1 | Answers; 61 models. |
| Anthropic | phase 1 | No key for Kiln's own use (HTTP 401 on a placeholder). |
| Brave Search | phase 1 | Not configured. |

`kiln doctor` therefore exits 2 for phase 0, naming Modal, Neon and R2. The session machine
has 4 vCPUs and 30 GB of free disk. No model was run, so CPU features were not assessed.

**The skills, read from `mattpocock/skills` at commit `4ae2317` (plugin v1.3.2, 31 October
2026):**

- Every skill the charter names exists: `grill-with-docs`, `research`, `prototype`, `to-spec`,
  `to-tickets`, `wayfinder`, `implement`, `tdd`, `code-review`,
  `improve-codebase-architecture`, `to-questionnaire`, `wait-what`, `writing-for-agents` and
  `setup-matt-pocock-skills`. That includes the two the review could not confirm.
- **The install command is `claude plugin install mattpocock-skills@claude-plugins-official`,**
  not the charter's `claude plugins install mattpocock-skills`.
- **The glossary file is `GLOSSARY.md`.** The changelog records the rename from `CONTEXT.md`,
  and the skills now read only the new name.
- `ralph-once` is not a skill in the repo; it is the one-iteration script from Pocock's Ralph
  articles.
- The setup skill writes `docs/agents/` and an "Agent skills" block in `CLAUDE.md`. It edits
  `CLAUDE.md` when that file exists.

**Spend:** $0. Listing models and projects is free.

**Consequences.** The live charter uses the corrected command and file name. **For Tom:** the
missing keys and the Langfuse project (handover, "For Tom" 4 and 5). A running session does
not see secrets added after it started, so they are needed before the session that uses them.

## D-005 — The seeds reviewed: six fixes and five additions worked through, three more flags, and nothing of substance changed without Tom (2026-11-10)

**Context.** `docs/repo-seeds/26-11-11_docs-review.md` reviews the other nine seeds. It lists
six things to fix before seeding and five worth adding, and ends by offering to draft them as
charter edits. Tom committed it with the seeds. Some of its items are structure, which is
Claude's to do; others amend the charter's policy, which is Tom's (`CLAUDE.md`, "Tom decides
five things").

**Decision (a recommendation; Tom decides adoption).** Structure is done. Each change of
substance is a recommendation below. On adoption each becomes an ADR and an edit to the live
charter, in one commit.

**The review's six fixes.**

| | The review found | Done now | Recommended, for Tom |
| --- | --- | --- | --- |
| R1 | The gate flow and roadmap exist only as pictures | Both are tables in the live charter, marked as reconstructions (D-003) | Confirm the gate table; confirm or replace the exit tests |
| R2 | The Data Analyst and UX Designer analyse real test results, but real data stays with Tom's team (ADR-0024) | Nothing | **Results come back as de-identified aggregates.** The Council writes the analysis as code against the synthetic stand-in; Tom's team runs it where the real data lives; only the outputs the test plan names cross back, each with an origin manifest. Keeps ADR-0024 whole and makes every result reproducible. |
| R3 | A loop sets its own `passes` flag and can edit the tests, `fitness/` and contracts it is judged by | Nothing | **A verifier that is not the loop sets the flag,** by running the ticket's verification steps and every check on a clean checkout. `contracts/`, `fitness/` and each ticket's verification steps are read-only to loops; a loop that needs one changed raises a typed question. This is the charter's own rule that only a validation node writes a pass, applied to tickets. |
| R4 | Tripwire 1 rests on screening, which fires on realistic synthetic data and can miss real data. The brief itself goes to model providers unscreened. | Nothing | **Provenance is the control; screening is the second net.** Every dataset enters a build with an origin manifest (who made it and how). A dataset without one does not enter. A registered synthetic set is exempt from a screening stop. Intake screens the brief before any provider sees it. |
| R5 | The proposals still say consensus, hard gates, nine gates and no dismissing findings; and two charter rules on silence pull apart | The proposal map lists what each proposal says against the ADR that rules, with five reading rules. A working reading of the silence rules is on the charter's front page, marked inferred. | Confirm the reading: for what the charter names, the proposal gives detail; what it does not name is outside the first build. |
| R6 | The proposals' citations are dead tokens, so dated policy facts cannot be traced. The APP 1 automated-decision rules commence on 10 December 2026. | Dated policy facts are `assumed` until verified (`CLAUDE.md`, the proposal map, the seeds' README) | **Make the charter's own dated claims the first of the Researcher's 20 golden questions,** so verifying them is its first slice's test. No decision needed until that set is drafted. |

**The review's five additions.**

| | Addition | Where it now sits |
| --- | --- | --- |
| A1 | A spend ledger: tripwire 4 has no unit or meter | In the phase 0 sketch, slice 3: dollars, metered per call, a warning before the stop |
| A2 | An egress allowlist: "open for packages and documentation" is an exfiltration path | In the phase 0 sketch, slice 6: a named list of registries and documentation hosts, default-deny beyond it |
| A3 | Evals for all seven agents, and one end-to-end brief with seeded defects | Each agent's first slice is its first eval set (already the charter's rule for two of them). The seeded-defect brief is in the draft exit test for phase 4. |
| A4 | An approval command, since Tom approves in chat until the Interpreter exists | In the phase 0 sketch, slice 1: a command that writes the decision record |
| A5 | Split the charter | Done (D-003) |

**Three more flags, found in this session.**

| | Found | Recommended, for Tom |
| --- | --- | --- |
| F1 | The Langfuse keys this session holds belong to the reference build's project, `data-expert-agent` (D-004). Kiln's traces would mix with that agent's recorded evaluations. | A separate Langfuse project for Kiln, with its own keys. One project for the whole Council, since trace names already carry the agent. |
| F2 | The SOP's reference build keeps its knowledge base in SQLite and Parquet files committed to the repo; the charter puts the Council's in Neon and R2. The charter governs, but the SOP's guarantees (a build that reproduces byte for byte, a measurement that can be replayed, a fresh clone that can read the library) do not come free from a hosted database. | **Files are the record; Postgres is an index.** Every ingestion stage writes deterministic, hashed files to R2, and Postgres is loaded from them and can be rebuilt. Retrieval is measured on exact search before any approximate index is adopted. In the phase 0 sketch, slice 5. |
| F3 | The chair's first slice asks for "a maturity target", but ADR-0018 and ADR-0023 replaced maturity levels with production quality sized by the proportionality profile. | Read "maturity target" as the proportionality profile, and settle the wording in the grilling session. Small. |

**Checked.** Each "found" above is from the seed named, read in full or at the section cited.
Nothing was measured.

**Spend:** $0.

**Consequences.** Until Tom rules, R2 to R4 and F2 are open and the affected parts are not
built. None blocks slices 1 and 2 of the sketch. **For Tom:** handover, "For Tom" 1 to 8.
