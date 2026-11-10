I'll read all nine documents, then come back with a review covering consistency across them and gaps that matter for seeding the factory.

The set is strong, and the charter resolves most of the conflicts between proposals. The problems below are the ones I'd fix before using the nine files as seeds, most important first.

**Fix before seeding**

1. **Two key designs exist only as pictures.** The gate flow and build roadmap appear in the charter file as "[embedded content]" placeholders. What each gate checks, and the six phases with their exit tests, aren't in text an agent can read. Write both as tables.

2. **Real test results collide with tripwire 1.** The Data Analyst and UX Designer are chartered to analyse real-world test results, but row 24 keeps real users and data with your team. Decide how results come back: de-identified aggregates, or analysis code your team runs on its side.

3. **Loops can certify their own work.** A loop flips its own `passes` flag and can edit the tests, `fitness/` and contracts it's judged against. Have a separate verifier set the flag, and make those paths read-only to loops.

4. **Tripwire 1 can't rest on screening.** Presidio will fire on realistic synthetic data and can miss real data. Make provenance the main control: every dataset enters with an origin manifest, and registered synthetic sets are exempt. The brief itself also isn't covered, though it goes to model providers.

5. **The proposals still contradict the charter.** They say consensus, hard release gates, nine gates and no dismissing findings. Two charter rules also pull apart: "where silent, the proposal is the reference" and "not mentioned means outside the first build". Add a status header to each proposal listing what was overruled, and keep one rule.

6. **Policy facts can't be traced.** The proposals' citations are dead tokens, so "the proposals cite their own sources" no longer holds. The facts date from early October, and the APP 1 automated-decision rules commence on 10 December. Mark dated claims as assumed until the Researcher's first slice verifies them.

**Worth adding**

- **Spend ledger:** tripwire 4 has no unit or meter. Track model, Modal and search spend in the shared core, with a warning before the stop.
- **Egress allowlist:** "open for packages and documentation" is an exfiltration path when a sandbox holds a repo token and model key.
- **Evals for all seven agents:** only the Researcher and chair have eval sets. Add one end-to-end brief with seeded defects that trips each tripwire.
- **Approval command:** rule 5 makes approvals records, but until the Interpreter exists you approve in chat. A small command should write the decision record.
- **Split the charter:** separate the standing rules, the agent charters and the build plan, so runtime agents don't carry the build method.

**One check on the first move**

The charter's `claude plugins install mattpocock-skills` doesn't match what a third-party guide shows: an `npx skills@latest add mattpocock/skills` copy, or a marketplace add followed by `/plugin install mattpocock-skills@mattpocock`. The renamed skills hold up, with /to-spec and /to-tickets listed as the July 2026 successors to /to-prd and /to-issues. I couldn't open the repo itself or confirm `/wait-what` and `/to-questionnaire`, so check those against the README.

Want me to draft these as charter edits, starting with the gate and phase tables?

Sources: [claudekit: mattpocock-skills](https://claudekit.io/en/tools/mattpocock-skills/), [Skillselion: Matt Pocock's skills, mapped](https://skillselion.com/guide/matt-pocock-skills-map)
