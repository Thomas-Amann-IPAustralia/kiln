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

## D-006 — The documentation reviewed against Anthropic's and GitHub's guidance: the rulebook is too long, and D-001's branch-protection advice would have blocked every merge (2026-11-17)

**Context.** Tom asked whether the documentation from D-001 to D-005 would be considered good
practice by AI experts, and what I think of deferring the Interpreter. Claude wrote the
documents under review, so this is a self-review. The charter's own rule is that a reviewer
needs a fresh context and another provider to be independent (ADR-0026).

**Decision (a recommendation; Tom decides adoption).** Read against Claude Code's memory and
best-practices pages, agents.md, and GitHub's pages on required reviews and code owners, all
read on 2026-11-17.

**What holds up.**

- `CLAUDE.md` imports `AGENTS.md` (`@AGENTS.md`). That is the documented pattern, and
  `AGENTS.md` has the sections agents.md suggests.
- Rules are backed by checks. `kiln records check` and the hygiene tests turn written rules
  into failing builds. The seal on the seeds caught a real error before commit (D-002's
  correction).
- Decisions carry their reasons. The best-practices page names undocumented decisions as
  exactly what belongs in the record.
- Reconstructions are labelled, and dated facts are marked `assumed`.

**What does not.**

| | Found | Evidence | Recommended |
| --- | --- | --- | --- |
| 1 | The always-loaded rulebook is over the guidance | `CLAUDE.md` is 189 lines and imports `AGENTS.md`'s 77: 266 lines and about 2,500 words in every session. The memory page targets "under 200 lines per CLAUDE.md file" and says longer files "reduce adherence". Imports load at launch, so they do not reduce the cost. | Cut the always-loaded part to about 120 lines: scope, commands, Tom's five decisions, the tripwires and where things live. Move procedures that apply only sometimes (experiments, paid runs, flags, the reply format) into skills, which load only when used. |
| 2 | Rules that cannot bend are written, not enforced | 23 uses of never, always, must or non-negotiable in the always-loaded files. The best-practices page says emphasis tends to cause over-application, and that rules that cannot bend belong in hooks or deny rules. | Enforce, then delete the sentence. Next: a deny rule or hook that stops edits under `docs/repo-seeds/`. The manifest check stays, because the ruff incident came through a shell command, which a deny rule on edits would not catch. |
| 3 | The documents run far ahead of the code | 49 live Markdown files and about 25,000 words, against 572 lines of code. Normal at kickoff, but a description of a system that does not exist yet is the kind that drifts. | No new design document until slice 1's code exists. From then on, the code and its tests are the spec, and the documents follow them in the same commit. |
| 4 | The charter's front page said what runtime prompts contain | "Runtime agents carry this page, the operating model and their own charter" was Claude's addition, not the charter's, and it decided something undecided. | Corrected now. A runtime prompt is a versioned, measured artefact (SOP §20.2). |
| 5 | The glossary is large for a seed | 56 terms. The skills' format asks for project-specific terms only, added as they are resolved. Some are general (sandbox, backpressure, ADR). | Let the grilling session prune it. |

**A correction (D-001).** D-001 said CODEOWNERS "routes changes to the control plane" to Tom,
and recommended requiring a code-owner review on `main`. Both are wrong for this repo.

- Pull request #1 came from a Claude session and is authored by Tom's account. CI run 1's
  actor is Tom's account too.
- GitHub: "Pull request authors cannot approve their own pull requests." With Tom as the only
  code owner, a required code-owner review could never be met, and every merge would need an
  admin bypass.
- Without that requirement, CODEOWNERS only requests a review. It enforces nothing.

So with one person and one GitHub identity, Tom's merge is the review. The handover's item 12
now recommends requiring a pull request and the `ci` checks, and not a code-owner review. The
CODEOWNERS comment says what the file does. D-001 stands as the record of what was believed.

**On deferring the Interpreter (a recommendation).**

- **Deferring the agent is right.** It translates the Council's output, and there is none yet.
  Its design should come from observed friction, by the charter's own rule that evidence about
  users comes from real users first. Tom is its only user. In build sessions, Claude Code is
  already doing its job.
- **Deferring its job is not.** Kickoff ended with 13 items for Tom, several of them
  technical. G2 assumes Tom understands the plan he approves. The cost of a decision he did
  not follow lands later and larger.
- **Three cheap pieces now,** so the agent is a renderer when it arrives, not a redesign:
  1. **A decision card in slice 1:** the question, the options and their consequences, a
     recommendation, any dissent, whether the decision can be reversed, and what happens if
     Tom does not answer. An approval binds to the card's id and hash, never to a summary of
     it. When the Interpreter arrives it renders cards, and it cannot paraphrase a decision
     into existence.
  2. **Diagrams as Mermaid text.** The charter's two diagrams were lost because they were
     pictures. Mermaid renders on GitHub, survives export and stays readable to agents. That
     is the Illustrator's job done cheaply, for an owner who learns visually.
  3. **A friction log:** one line each time Tom needs a second explanation or reverses a
     decision he misread. By phase 5 it is the Interpreter's requirements and its first eval
     set.
- **One constraint to keep:** a single point of contact means every decision passes through
  one model's wording. Build the Interpreter as a renderer over records, with a check that
  every option and number it shows traces to the card. That is the same pattern as the
  Researcher's citation check.

**Checked.** The guidance pages were read for this entry. The counts above were counted
(`wc`, `grep`). Pull request #1's author and CI run 1's actor were read from GitHub.

**Spend:** $0. An independent review by another provider's model would cost cents, and needs
a budget (handover, "For Tom" 11).

**Consequences.** Corrected in this commit: the CODEOWNERS comment, the charter front page's
line on runtime prompts, a session-specific line in `CLAUDE.md`, and the handover's item 12.
**For Tom:** handover item 14. The rulebook's restructure waits for his answer, because it
changes what every later session reads.

## D-007 — A second opinion from OpenAI's model, for $0.38 of $2: five problems Claude's review missed, and three of its recommendations corrected (2026-11-17)

**Context.** Before agreeing or disagreeing with D-006, Tom allowed "up to $2 on OpenAI tokens
to get a second opinion." D-006 was a self-review, and the charter says independence needs a
fresh context and another provider (ADR-0026).

**Decision (Claude: the method. The recommendations are for Tom.)**

- **A new paid command, `kiln review`,** with the SOP's money rules in code: a dry run, a
  required `--confirm`, a budget guard that counts every recorded dollar, and every response
  cached under its request's hash and committed (`docs/reviews/cache/`).
- **Three requests to `gpt-6.1-sol` at high effort,** each spec committed before it was sent
  (`docs/reviews/2026-11-17-docs/`):
  1. a smoke test on one small file;
  2. **blind:** the 17 live documents and the SOP as they stood at `b57c335`, before D-006,
     with Tom's two questions;
  3. **compare:** the same, plus D-006 and the blind answer.

  Documents were read from git and defanged, and Tom's GitHub handle was redacted.
- **Rejected:** sending D-006 in the first request, which would have anchored the reviewer
  on Claude's findings.

**Runs, in order.**

| Request | Input tokens | Output (reasoning) | Cost | Upper bound |
| --- | --- | --- | --- | --- |
| 00-smoke | 618 | 38 (0) | $0.0016 | $0.3215 |
| 01-blind | 54,072 | 6,139 (4,142) | $0.1966 | $0.5035 |
| 02-compare | 57,994 | 3,600 (2,127) | $0.1810 | $0.5178 |

- **The smoke test found a bucket the code did not price.** OpenAI caches by default and bills
  a cache write at $2.50 per million tokens, 1.25 times the input rate, instead of the input
  rate. Fixed before the blind request (`e9b1521`). Unfixed, the blind run would have been
  recorded at $0.1695, 14% low.
- **The comparison got no cache hit,** though its first 17 documents matched the blind
  request's byte for byte. Both paid the write premium for nothing, about $0.056 in all.
- Real input ran at about 4.1 characters a token (4.05 and 4.07), against the estimate's bound of 3. Each run cost
  35 to 39% of its bound.

**What the second opinion found that D-006 did not.** Each was checked against the source text.

| | Found | Checked |
| --- | --- | --- |
| 1 | A loop can still set its own ticket's `passes` flag, and an `actor: tom` field in a record does not show that Tom approved anything | `coding-swarm.md`, step 5; the sketch's slice 1 |
| 2 | Phase 0 promises harness controls before agents have tools, but the sketch omits the scanner baseline and defers the credential broker | The sketch names no scanner; the build plan's first move 7 names three |
| 3 | The charter's rule 11, "Only a tripwire waits for Tom", contradicts the Tom band and the four gates Tom decides | `operating-model.md`, rule 11 |
| 4 | Rules on spending and authority are in `CLAUDE.md` only, so an agent that reads only `AGENTS.md` (Codex, Cursor) would not get them | `AGENTS.md` had no spending rule |
| 5 | The SOP chooses models on the test split (§20.5), and also says "choose on dev, report on test" (§12) | Both lines, in the sealed SOP |
| 6 | `store: false` does not by itself mean zero retention at the provider | The SOP's §23 says it does. So did Claude's own docstring in `kiln review`, corrected in `f24e1c5`. |
| 7 | Phase 0 builds hosted storage, ingestion and a sandbox before the first useful result, and nothing compares the multi-agent design with a simpler baseline | The sketch's build order |

**Where it corrected D-006.** Each correction is accepted.

- **The rulebook's length was overstated.** Anthropic's target is under 200 lines *per file*.
  `CLAUDE.md` is 189 and `AGENTS.md` is 77. Duplication is worth cutting, but contradictory and
  missing rules matter more.
- **"Enforce, then delete the sentence" goes too far.** Enforcement blocks a forbidden action;
  a short statement of the boundary helps an agent choose a permitted one. Keep both.
- **"No new design document until code exists" is too categorical.** Code can implement the
  wrong policy faithfully. Revising the sketch comes first.
- **The Interpreter cannot be only a renderer.** It also questions Tom. Rendering approvals
  should be constrained; its conversation is tested separately.

It also confirmed D-006's correction on CODEOWNERS, with one condition: Tom's merge is the only
human review **only if Claude never merges**. GitHub cannot tell Claude from Tom on one account.

**A claim neither review had caught, corrected now.** `CLAUDE.md` said `kiln records check`
"proves these agree". It checks structure: numbering, dates, the index, the seed hashes and
links. It cannot check meaning, which finding 3 shows.

**Recommendations (Tom decides).** These are the handover's "For Tom" items 1 to 5 and 12.

1. Revise the phase 0 sketch before approving it, with findings 1, 2 and 7.
2. Fix rule 11 and move the authority and spending rules into `AGENTS.md`, then cut the
   duplication from `CLAUDE.md`.
3. Protect `main` with a required pull request and both CI jobs; no required code-owner review;
   Claude never merges.
4. Compare a single-session baseline on the three sample briefs before going beyond the chair
   and the Researcher.
5. Defer the Interpreter and the Illustrator. Build the decision card, Mermaid diagrams and a
   one-line friction log now.
6. Choose on dev, always.

**Checked.** 62 tests pass, 20 of them on `kiln review`, with sockets refused. Each finding
above was checked against the file it cites. Every request and response is committed.

**Spend:** $0.3792 of Tom's $2 `docs-second-opinion` budget. No failed requests. $1.62 is unspent
and kept for that purpose.

**Consequences.** Corrected in this entry's commit: `CLAUDE.md` (what is built, the budget, what
the records check proves), `AGENTS.md` (the paid command and its rule), the README, and the
handover, whose owner list now leads with the five items that start the next step. **For
Tom:** handover items 1 to 5. D-006's recommendations stand as amended here.

## D-008 — Tom adopts the five recommendations of D-006 and D-007 (2026-11-17)

**Context.** D-007 put five recommendations to Tom, drawn from Claude's review (D-006) and
OpenAI's second opinion. Tom answered: "Yes to all."

**Decision (owner).** Each change below lands in this entry's commit.

| | Adopted | What changed |
| --- | --- | --- |
| 1 | Revise the phase 0 sketch before approving it, for D-007's findings 1, 2 and 7 | The charter's phase 0 exit test now ends in one sample brief taken the whole thin path before the hosted services, with the verifier setting the pass, the harness refusals tested and the scanner baseline in CI. First moves 5 and 6 come after that path. The sketch itself is revised in D-009 and goes back to Tom for approval. |
| 2 | Fix the authority rules, then shorten | Charter rule 11 now names Tom's gates and changes to what he approved, as well as tripwires. `coding-swarm.md`'s opening names the Tom band. `AGENTS.md` now holds the rules every agent must follow: Tom's five decisions, when to stop and ask, and what no agent ever does. `CLAUDE.md` keeps only what is specific to Claude Code sessions. |
| 3 | Protect `main` with a pull request and both CI jobs; no code-owner review; Claude never merges | ADR-0028. The GitHub setting is Tom's to make (handover, "For Tom" 2). |
| 4 | Compare a single-session baseline before building beyond the chair and the Researcher | ADR-0029, and the phase 1 exit test. |
| 5 | Defer the interface agents; build the interface now | ADR-0030: decision cards (in `CLAUDE.md` now, a typed record in slice 1), diagrams as Mermaid text, and [`docs/friction-log.md`](friction-log.md). |

Adopting item 1 adopts D-005 R3 too: an independent verifier sets a ticket's pass, and loops
cannot edit what judges them (ADR-0027, `coding-swarm.md`).

**What the rulebook change did to its length.** `CLAUDE.md` fell from 189 lines to 171, and
`AGENTS.md` rose from 77 to 121, so the two together went from 266 to 292. Both are under
Anthropic's 200-line target per file. The rules on authority, money, security and stopping
are now each stated once, and every agent gets them, not only Claude.

**Not adopted, and still open:** the evaluation policy (D-007 recommendation 6) and the
items D-005 left for Tom. They remain in the handover under "These can wait".

**The limit ADR-0028 states.** "Claude never merges" is a rule, not yet a mechanism. Claude's
sessions act under Tom's GitHub account. Before any loop runs unattended, approvals need a
path no agent can use. That choice is Tom's, and it is in the handover.

**Spend:** $0.

**Consequences.** Next is D-009: the sketch revised to match, for Tom's approval. Nothing in
slice 1 is built until then.

## D-009 — The phase 0 sketch revised for D-008, for Tom's approval; and ADR-0028's wording corrected (2026-11-17)

**Context.** D-008 adopted five changes. The first was to revise the phase 0 sketch before Tom
approves it. The revision is a design for approval, so it is groundwork, not an adoption.

**Decision (groundwork; Tom decides whether to approve the sketch).**
[`docs/sketches/phase-0-shared-core.md`](sketches/phase-0-shared-core.md) now has nine slices,
not seven.

- **First useful result before the hosted services.** Slice 6 takes one sample brief through
  the thin path, with the plan approved by Tom's merge and the pass set by the verifier.
  Neon, R2, Langfuse and ingestion follow it, as slices 7 and 8.
- **The harness is tested in phase 0.** Slice 3 puts Semgrep CE, OSV-Scanner and Trivy in CI
  and generalises `kiln review`'s budget guard into a shared spend ledger. Slice 5's sandbox
  must refuse a file, a host and a credential it was not given, and stop before its cap.
- **Slice 4 is new:** tickets and the verifier (ADR-0027). The verifier refuses a commit that
  edits what judges it, whatever its tests say.
- **Approvals bind to a version.** An approval is Tom's merge of the commit that holds a
  decision card. `kiln approvals` will list each approved card with its hash, and flag one
  edited since (ADR-0028).
- **The baseline is planned from slice 6.** Its single-session plan is the baseline's first
  data point, and slice 9 commits the comparison's rule before either path runs (ADR-0029).
- **Two Mermaid diagrams** show the shape and the slice order. A third draws the reconstructed
  gate flow in the operating model, beside the table Tom has yet to confirm.
- **Not designed here:** the real-data tripwire's check, which waits for Tom's ruling on
  D-005 R4. Until then no dataset enters a build.

**A correction (ADR-0028).** As written in D-008's commit, ADR-0028 said "no agent records an
approval in Tom's name". Read literally, that forbids the decision log's own practice: D-008
records Tom's "Yes to all". The ruling was meant, and now reads, that an agent may write down
what Tom decided, but the record takes effect only when Tom merges it. The ruling is
unchanged; its wording was Claude's error, corrected before the ADR was merged. `AGENTS.md`
matches.

**Checked.** `kiln records check` passes. **Not checked:** how the diagrams render. A render
with Mermaid's own tool was refused by this session's permissions (it would have run a
downloaded package with the browser's sandbox switched off). The syntax was kept
conservative instead: every label quoted, each group defined before it is linked, and no
label that opens with a list number. GitHub renders Mermaid in Markdown files, so Tom sees it
there.

**Spend:** $0.

**Consequences. For Tom:** approve the sketch (handover, "For Tom" 1). Slice 1 needs no secret
and no money.

## D-010 — Tom approves the phase 0 build order; slice 1 starts (2026-11-18)

**Context.** D-009 revised the phase 0 sketch and put it to Tom. On 2026-11-17 Tom reported
that he had added the ruleset protecting `main` (ADR-0028). On 2026-11-18 he answered the
sketch's card: "I approve the phase 0 build order. Please commence thoughtfully."

**Decision (Tom).** The sketch is approved as it stood at commit `2fd52ad`, merged to `main` in
pull request #2. This commit changes only its status line, to say so.

- **The sketch is now frozen.** A change to it is a change to what Tom approved, so it falls in
  the Tom band and goes back to him. Progress is tracked in the handover, not in the sketch.
- **Merging the sketch was not the approval.** Pull request #2 put the sketch on `main` the day
  before Tom answered. A merged question is not an answer. Slice 1 builds that distinction
  into the decision card: an approval needs Tom's answer in the card *and* his merge.
- **The ruleset.** GitHub reports `main` as protected (observed, 2026-11-17). This session
  cannot read a ruleset's settings, so which checks it requires is unverified.

**What changed with it.** The sketch's status line; `CLAUDE.md`'s current scope; the status of
first move 4 in `docs/charter/build-plan.md`; the handover.

**Spend:** $0.

**Consequences.** Slice 1 starts: the enums, the id formats, `ProjectProfile`, the decision
record and its store, the decision card and `kiln approvals`, and three synthetic sample
briefs. When the card format exists, this approval is written as the first card, so that the
mechanism is tested on a real decision.

## D-011 — Slice 1 built: the record formats, the decision card and `kiln approvals` (2026-11-18)

**Context.** Tom approved the phase 0 sketch (D-010). Slice 1 settles the contracts every
later slice and agent consumes: the enums, the id formats, the project profile, the decision
record, the decision card, and how an approval is read.

**Decision (Claude; engineering inside the approved slice).** Each choice below that is not
obvious, and why.

1. **One file per record, and the file must be its own rendering.** A card or decision record
   is YAML front matter (the record, which machines read) followed by Markdown rendered from
   it (which Tom reads). A file is valid only if it is byte-for-byte what its record renders
   to, so the two halves cannot disagree, and the file's hash names one exact version.
   `kiln records render` turns a hand-edited front matter back into that form. The
   alternative, a YAML file beside a Markdown file, doubles the files and lets them drift.
2. **An approval needs Tom's answer in the card and his merge.** `kiln approvals` walks
   `origin/main`'s first-parent history. A card is approved at the first commit there that
   holds Tom's answer and in which every file it rests on matches the card's hash. A merged
   card with no answer approves nothing (D-010). After approval, a change to the card or to a
   file it rests on lapses the approval *even though Tom merged it*: an edit needs a new card
   that supersedes the old one (ADR-0028), and lapsing loudly is how a quiet edit inside a
   large merge is caught. `kiln records check` also refuses, before any commit, a card whose
   files have changed, unless a later card supersedes it.
3. **`origin/main`, not `main`.** A local `main` can hold commits nobody merged. The remote is
   where Tom's merges land; the command fails loudly if it has not been fetched.
4. **The profile states `unknown` and the basis of its sizing facts.** Every field is
   required; `unknown` is a value. The three proportionality facts each carry a basis, and
   `unknown` goes with basis `unknown` and only with it, so a guess cannot pass as known. The
   data kinds are the Governance proposal's intake list, plus `public` and `internal`:
   drafting the sample briefs showed that most government information is neither published
   nor any of that list's kinds. Each expert's section and the other core facts arrive with
   the expert that uses them; whether a profile is ready for G0 (for example, that its
   hypotheses cover all of DVF) is the gate's check in slice 2, not the schema's.
5. **The decision record keeps the glossary's fields** (actor, time, basis, dissent) and the
   proposal's options, evidence, reversibility, consequences and supersession. Evidence is
   required unless the basis is `assumed` or `unknown`; dissent is written by an expert other
   than the one deciding. A record is never rewritten except to be marked superseded. Its
   status uses *accepted*, not *approved*, which now means only Tom's approval. The chair's
   architecture fields arrive as an extension in phase 1.
6. **The id formats are types now;** trace names and the spend contract are typed in the
   slices that first use them (7 and 3).
7. **The decision card's answer date is `answered_on`, not `on`.** YAML 1.1 reads a bare `on`
   key as the boolean `true`; a test of a hand-edited card caught it.

**The first card.** Tom's approval of the sketch is written as `CARD-0001`. It rests on the
sketch as it is now, with D-010's new status line; the diff from what Tom read at `2fd52ad` is
that line alone. When Tom merges the pull request that holds it, `kiln approvals` will show it
approved. Until then it reads "awaiting merge", which is correct.

**The sample briefs** are drafted as three synthetic profiles in `evals/sample-briefs/`. They
are fixtures until Tom approves them as an evaluation set (first move 9).

**Checked.** `make check` passes: 135 tests, none touching the network. The approvals tests
build real git repositories with real merge commits. Each of five deliberate breaks to
`kiln approvals` (reading all history instead of first-parent, ignoring supersession,
skipping the lapse check, approving an unanswered card, skipping the hash check at merge) made
at least one test fail. **Not checked:** how GitHub renders a card's front matter; and the
real history, because no card has been merged yet.

**Limits, stated plainly.** `kiln approvals` reads history; it cannot tell Tom's merge from
anyone else's push, so it rests on the ruleset. A rebase merge would replay each branch commit
onto `main` and could show an approved card as edited: a false lapse, loud and safe, never a
false approval. It is not in CI yet: CI's checkout is shallow and has no `origin/main`.

**Spend:** $0.

**Consequences.** Slice 2 (gates) and slice 4 (tickets and the verifier) can build on these
records. For Tom: nothing new blocks. Two small items join the handover's list that can wait:
the merge method, and the sample briefs.

## D-012 — Slice 2 built: the gates, G0 to G5, on LangGraph (2026-11-18)

**Context.** Tom asked for the next slice. Slice 2 of the approved sketch (D-010) builds "G0 to
G5 as a LangGraph state machine whose nodes only validate artefacts", checked by four things:
a sample brief walks G0 to G5 on fixture artefacts; a missing artefact fails its gate; a pass
written from outside the validation node is refused; a plan edited after approval fails G2.

**Decision (Claude; engineering inside the approved slice).**

1. **LangGraph, as the approved sketch and the charter name it, pinned and held back.**
   LangGraph 1.2.19 (30 October). It adds 26 packages to the lockfile, among them
   `langchain-core`, `langsmith`, `requests` and `websockets`; no existing package changed
   version. Each new package is held to releases uploaded before 4 November, two weeks before
   today, in `pyproject.toml`'s `[tool.uv.exclude-newer-package]`, so a release in the window
   in which bad ones are usually caught cannot slip in through a later `uv lock`. A first try
   applied the cutoff to every package; it downgraded three existing ones and wrote a
   repo-wide rule into the lockfile, which would bind every agent, so it was reverted.
   *What LangGraph buys today is small:* six nodes in a line, a checkpointer, and
   `update_state`. The gate logic is plain functions under it (`kiln.gates.validate`), so the
   machine is a thin shell, cheap to replace if phase 1's agent nodes do not need it.
2. **Tracing through LangGraph is switched off in code** (observed). With
   `LANGSMITH_TRACING=true` in the environment, a plain LangGraph run posted its state to
   `api.smith.langchain.com` (this session's proxy refused it with a 403). Gate state names a
   solution's files, so every run is wrapped in `tracing_context(enabled=False)`, and a test
   sets both tracing variables and checks that no gate runs with tracing on. Kiln's tracer is
   Langfuse, in slice 7.
3. **A pass is never trusted, only recomputed.** Every gate is evaluated from the files and
   `origin/main`'s history as they are now; nothing about a pass is stored to be believed.
   Before a node validates its gate, it re-validates every pass already in the run's state and
   refuses one that does not hold. A pass injected through `update_state`, posing as the G1
   node, is refused at G2.
4. **Tom's gates need a gate card.** A decision card gains an optional `gate` field: which of
   Tom's gates it decides, and which option passes it. A Tom gate passes when an approved card
   answered with that option rests on the gate's files *at their current hashes*. Two rules
   follow, each tested:
   - *Tom's latest approval of a file counts for every earlier gate that needs it.* The G2
     card rests on the profile as it stands at G2, so G0 does not need a fresh card each time
     the profile gains a measure.
   - *A lapsed approval still covers the files that did not change,* unless the card itself
     was edited, when it covers nothing. Without this, a plan edit lapsed the G2 card and the
     run blamed G0, the wrong gate.
5. **Four states, one exit rule.** A gate is `passed`, `awaiting Tom`, `incomplete` (an
   artefact does not exist yet) or `failed`. `kiln gates` exits 2 only on `failed`: waiting for
   work or for Tom is normal.
6. **Each gate's artefact holds only what its checks read** (`kiln.artefacts`): an
   applicability register, a plan with its review and estimate, a build record, a pre-release
   record, and the real-world test's findings. Their owners extend them when built.

**Readings of the charter (inferred), for Tom with the gate table (handover, "These can
wait", 1).** G0 requires hypotheses covering desirability, viability and feasibility. G1
requires only a valid register: it does not yet require the profile's `unknown`s to be
resolved, which is the Governance Guru's call in phase 2. G3 trusts `build.yaml`, which is
written by hand until slice 4 makes the verifier its only writer.

**Also changed.** The data dashboard sample brief gained a viability hypothesis, since G0 now
needs one. `CARD-0001` was re-rendered with the new `gate: null` field; it is not merged, so no
approval is affected.

**Checked.** `make check` passes: 157 tests, none touching the network. The walk runs a sample
brief through five real merges and four of Tom's cards. Each of six deliberate breaks (no
re-confirmation, no tracing guard, coverage ignoring hashes, only same-gate cards counting,
an edited card still counting, Tom's gates needing no card) made at least one test fail.
**Not checked:** a real solution, which slice 6 brings; LangGraph on CI's runner.

**Spend:** $0.

**Consequences.** Slice 3 (scanners and the spend ledger) is next. Slice 4 makes the verifier
the only writer of G3's ticket results.

## D-013 — Slice 3 built: the scanner baseline, one finding format, and the spend ledger (2026-11-18)

**Context.** Tom asked for slice 3 of the approved sketch (D-010): "Semgrep CE, OSV-Scanner and
Trivy in CI, pinned, feeding one finding format. The spend ledger, shared by every paid
command." It is checked by two things: each scanner fails CI on a seeded finding, and the
ledger refuses a call that could pass a cap and warns at 80%.

**Found at source first.**

- **Trivy's release pipeline was compromised in March 2026** (supported: CVE-2026-33634,
  advisory GHSA-69fq-xp46-6x23, and Aqua's own post on the attack). Trivy v0.69.4 was a
  malicious release, built to steal what a CI job's environment holds, and the tags of Aqua's
  `trivy-action` and `setup-trivy` were moved to malicious commits. The Go module proxy refuses
  to serve v0.69.4 as "malicious" (observed). Trivy is named by the charter and the approved
  sketch, so it stays, pinned as in 1 and 5 below; for Tom under "These can wait".
- **Semgrep's built-in ignore list skips `tests/`,** even when a folder under it is named as the
  target (observed). Semgrep prefixes each rule id with the rules folder's path, relative to the
  working directory when it can be and absolute otherwise, and reports offsets in bytes
  (observed, Semgrep 1.183.0).
- **The first scan of LangGraph's packages** (handover, open item 12): OSV-Scanner read all 63
  packages in `uv.lock` and found no known vulnerability (observed, 2026-11-18).

**Decision (Claude; engineering inside the approved slice).**

1. **Pinned at every layer, and checked before each run.** Every version is at least two weeks
   old (D-012's rule).
   - *Semgrep CE 1.183.0* from PyPI, with all 66 packages pinned with their hashes
     (`.github/scanners/semgrep-requirements.txt`). Its *rules* come from one commit of
     `semgrep-rules` (`16b9e6d`, 21 October), the `python` and `yaml/github-actions` packs,
     fetched by CI and not copied into the repo: a registry ruleset can change under the same
     name, and the Semgrep Rules License v1.0 allows internal use.
   - *OSV-Scanner v2.7.0 and Trivy v0.76.1* are built by `go install` from the Go module proxy.
     The Go checksum database fixes each version's hash for good, so a tag moved after the fact,
     as Trivy's were, is refused rather than built. GitHub's release pages, which the gitleaks
     job uses, are not reachable from this session, so their checksums could not be checked
     here; the module route was verified end to end. It costs about six minutes of build time
     per CI run (90 seconds and 4.5 minutes on four cores here).
   - *`kiln scan` refuses another version.* For the Go scanners it reads the build information
     in the binary (`go version -m`), because a source build of Trivy reports its version as
     `dev`. A hygiene test keeps CI's pins and config's equal.
2. **One finding format** (`kiln.findings`): the scanner, the rule, one severity scale
   (`critical`, `high`, `medium`, `low`, `unknown`), a file or package location, CWE ids, a
   reference, and a key. The key hashes what was matched (the bytes for Semgrep, the cause lines
   for a Trivy check, the package and version for a vulnerability), so it survives lines moving
   above a finding and changes when the code under it does. Semgrep's `ERROR` maps to `high`,
   `WARNING` to `medium` and `INFO` to `low`. OSV-Scanner's score maps by the CVSS
   specification's ratings, or failing a score by the databases' own words, or else to
   `unknown`. OSV-Scanner's grouped records of one vulnerability are one finding, named by its
   CVE where it has one. A scan's findings are regenerated on every run, so they carry no
   `FND-` number; that id is for a finding kept as a record, which arrives with the Security
   Architect.
3. **What blocks: `critical`, `high` and `unknown`** (inferred). The charter says critical and
   high findings are fixed or explained before G4; `unknown` blocks too, because nothing shows
   it is smaller. Medium and low findings are printed on every run and do not fail it.
4. **One way to set a finding aside:** `config/dismissals.yaml`, which is in CODEOWNERS. Each
   entry names one key, the reason, who and when, and must agree with its finding's rule and
   path. The scanners' own routes are shut: Semgrep runs with `--disable-nosem`, and `kiln scan`
   refuses to run where a `.trivyignore`, `.trivyignore.yaml`, `trivy.yaml` or
   `osv-scanner.toml` exists. A dismissal that matches nothing is reported as stale.
5. **A scanner sees only an allowlisted environment** (config, `scanners.environment`): enough to
   run and reach the network, and no credential. This session's own environment holds GitHub,
   AWS and cloud tokens (observed, by name only), which is exactly what the malicious Trivy
   release stole.
6. **Seeded findings,** one per scanner, in `tests/seeded-findings/`. `kiln scan --seeded`
   succeeds only if the planted finding is reported at a blocking severity, so a scanner that
   silently stops detecting fails CI instead of passing it. OSV-Scanner's fixture has a file
   name that neither it nor a dependency bot reads by itself.
7. **What each scan covers.** Semgrep scans the files git tracks, minus `tests/`: test code runs
   only in CI with a read-only token, Semgrep leaves tests out by default, and its first scan of
   Kiln's tests gave four false positives: three read `subprocess.CompletedProcess(...)`, which
   builds a result, as running a command, and one flagged the race test's deliberate sleep. Trivy checks misconfiguration only, with the checks
   built into its version and no database: its vulnerability scanning would repeat OSV-Scanner's
   on `uv.lock`, so it waits for a container image to scan. OSV-Scanner reads every lockfile.
8. **The spend ledger** (`kiln.spend`, `docs/spend/ledger.jsonl`). A paid call reserves its
   upper bound before it is sent and settles at its real cost after. A reservation is refused if
   settled spend plus open reservations plus its bound could pass the cap, and warns when it may
   take the budget to 80% (config, `spend.warn_at`). Once settled spend passes a cap, tripwire 4
   refuses every call against that budget and `kiln spend` exits 2. A lock makes the check and
   the append one step. Entries are canonical JSON lines, numbered and appended, never
   rewritten.
   - `kiln review` now spends only through it. A request refused before it left settles at $0;
     an error response settles at $0 on an `assumed` basis; a timeout after sending leaves the
     reservation open at its bound until `kiln spend settle` records the provider's figure. A
     response that reports no usage is now charged at its bound. **This corrects `kiln review`,
     which recorded such a response at $0:** no recorded response had that shape, so no figure
     changes.
   - The three recorded reviews are backfilled, each timed at the commit that recorded it. The
     ledger's total is $0.3792, D-007's figure. `kiln records check` now requires each cached
     response to have exactly one settlement, for its cost, against its budget.
9. **CI runs on `ccr-**` branches** too, which is how this session's cloud branches are named
   (closes handover open item 10). A change to `.github/`, for Tom's review when he merges.

**What the first scans found** (observed). OSV-Scanner and Trivy found nothing in the repo.
Semgrep found 14 things in `src/`; I read each by hand. Thirteen are `medium` and wrong in
context: nine implicit string joins in lists, which are deliberate; three reads of httpx's
`is_success`, a property the rule takes for a method; and one regex that reads only Kiln's own
files. One is `high`, in this slice's own code: `run_process` builds a scanner's command from
config and fixed strings, with no shell. It is dismissed with that reason rather than rewritten
to dodge the pattern.

**Checked.** `make check` passes: 273 tests (157 before), none touching the network. With the
pinned binaries in this session, the three repo scans pass (Semgrep with one dismissal) and each
seeded finding is detected: Semgrep's `subprocess-shell-true` (high), OSV-Scanner's
CVE-2020-14343 (critical), Trivy's DS-0002 (high). Semgrep installs cleanly from the committed
requirements. Each of 15 deliberate breaks made at least one test fail: no lock; a seeded check
that ignores severity; the whole environment passed through; suppression files allowed; any exit
code taken as a finished scan; no build-information check; dismissals applied to a seeded run; a
Semgrep key by line number; an unknown severity word graded low; open reservations not counted;
no 80% warning; the tripwire not enforced; a timeout settled at $0; the ledger not checked
against responses; and CI's pins drifting from config. **Not checked here:** the `scanners` job
on GitHub's runner. The handover records its first result.

**Limits, stated plainly.** The ledger is a file in git, so it is per branch: two sessions on
two branches could together pass a budget (for Tom under "These can wait"). Advisory data is
read live, so CI can go red with no change here when a new advisory lands; that is the point.
The scanners' own reports are not kept as CI artifacts; the log holds Kiln's summary and each
report's hash. Trivy does not write the CycloneDX SBOM yet (charter, Security Architect). The
lock needs POSIX (Linux, macOS).

**Spend:** $0. The scans call OSV.dev's free API.

**Consequences.** Slice 5's sandbox reserves each run's cap in this ledger. Slice 4 (tickets and
the verifier) is independent of this slice and can be next.
