# Build sequence and first moves

Build in six phases, and close each one with a test you can run rather than a feeling that it is done. The order follows Pocock's advice to tackle risky and integration work first: the shared core and one thin path from brief to code come before any expert goes deep.

> **Changed from the seed.** The seed held a picture here ("Build roadmap · six phases, each
> closed by an exit test") that did not survive export. The phases and what each builds are
> from this charter's text. **The exit tests are drafts**, written from each agent's first
> slice, because the seed's are lost. Tom to confirm or replace.

| Phase | Builds | Exit test (draft) |
| --- | --- | --- |
| **0** | The shared core, the harness controls, and one thin path from brief to code | From a fresh clone, with no network, `make check` passes. `kiln doctor` reports every phase 0 service ready. A sample brief validates as a project profile and walks G0 to G5 on fixture artefacts, where a missing artefact fails its gate. Each tripwire has a fixture that fires it. One source goes through ingestion end to end, and a re-run is byte-identical. A trivial generated program runs in a Modal sandbox under a spend cap, and its trace is read back from Langfuse. |
| **1** | Solution Architect (chair), Researcher, and the coding swarm as one loop | The chair's first slice runs on the three sample briefs. The Researcher's lookup and verify modes are measured against the 20 golden questions, the injected-instructions page included. One loop takes a chair-written ticket list to passing tickets in a sandbox. |
| **2** | Security Architect, Governance Guru, and the source change monitor | Both assess the Council itself: a security profile, a threat model, encoded harness rules and the CI baseline; a governance intake, the obligations it triggers, and an assurance case that states what is unresolved. The change monitor opens a revalidation task when a registered source's hash changes. |
| **3** | Data Engineer, UX Designer | The Data Engineer's first slice runs on a messy CSV and an XLSX workbook. The UX Designer's first slice runs on one transactional form service, through to an Experience Assurance Report. |
| **4** | Data Analyst | Its first slice takes a synthetic test-results dataset through to a DVF evidence statement. One sample brief runs G0 to G4 with every expert, and seeded defects trip each tripwire. |
| **5** | Interpreter, Illustrator | Tom runs a G0 intake and a G2 approval through the Interpreter alone, and every picture the Illustrator draws traces to a record. |

Phases run in order and are not to scale, since no dates are set. Each exit test is something you can run and watch pass.

The harness controls that keep Tom's environment safe arrive in phase 0, before any agent has tools. Until the Data Analyst arrives in phase 4, the chair writes simple success measures for real-world tests.

## First moves

> **Changed from the seed.** Each move now has a status, as of D-005 (10 November 2026). The
> install command is corrected from the skills repo's README. The order is the seed's.

| # | Move | Status |
| --- | --- | --- |
| 1 | Create the Council repo, install Pocock's skills (`claude plugin install mattpocock-skills@claude-plugins-official`) and run `/setup-matt-pocock-skills` once. | Repo created. **Tom:** the install and the setup run are yours, in Claude Code. The setup skill will add an "Agent skills" block to `CLAUDE.md` and write `docs/agents/`. |
| 2 | Run `/grill-with-docs` over this charter to produce GLOSSARY.md, then turn Appendix A into ADR-0001 onwards. | ADRs done (D-003). `GLOSSARY.md` is seeded from the charter's terms (D-002). **Tom:** the grilling is yours; it sharpens the seed. |
| 3 | Write AGENTS.md: production quality in proportion to the system, build and test commands, and the ban on placeholder code. | Done (D-001). |
| 4 | Define the core schemas as Pydantic models with tests: ProjectProfile (with DVF hypotheses, proportionality profile and budget), Source, Decision, ToolRegistryEntry, EvidenceArtefact, ResearchRequest and ResearchPacket. | Next. Sketched for approval in [`docs/sketches/phase-0-shared-core.md`](../sketches/phase-0-shared-core.md). |
| 5 | Stand up Neon schemas and roles, R2 buckets, Langfuse, and a Modal sandbox runner with spend caps. | Langfuse answers; R2's keys work but no bucket is named; Neon and Modal have no keys yet (D-004). |
| 6 | Build the ingestion path once: fetch, hash, store in R2, normalise, index in Postgres full-text and pgvector, and register the source. | Not started. |
| 7 | Add the tripwire checks (Gitleaks, real-data screening, egress closed to live systems, spend caps) and the scanner baseline (Semgrep CE, OSV-Scanner, Trivy). | Gitleaks runs in CI and pre-commit (D-001). The rest is not started. |
| 8 | Wire LangGraph gates G0 to G5 as nodes that only validate artefacts. | Not started. |
| 9 | Write three sample briefs with DVF hypotheses and proportionality profiles, and 20 golden research questions, as the first eval sets. | Not started. Claude drafts; Tom approves the sets before any run. |
| 10 | Run the first chair slice as HITL Ralph, and hand the ingestion adapters to AFK Ralph with an iteration cap. | Phase 1. |
