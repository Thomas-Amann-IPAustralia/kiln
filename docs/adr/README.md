# Architecture decision records

A standing ruling about what Kiln and the Council are. Each one settles a real trade-off that
is hard to reverse and would surprise a reader who did not know why.

- **ADR-0001 to ADR-0026** are the 26 rows of the seed charter's Appendix A, text unchanged
  (D-003). Each settles a conflict between proposals, or between a proposal and the brief.
- **A new ADR** is written when Tom adopts a design ruling. It lands in the same commit as the
  decision entry that records the adoption.
- **An ADR is never edited to change its ruling.** A new ADR supersedes it, and the old one's
  status becomes `superseded by ADR-NNNN`.
- **Format:** the one `mattpocock/skills` uses, so `/grill-with-docs` reads and extends this
  folder: `NNNN-slug.md`, a title, and a short statement of the ruling and why. `status` is
  `proposed`, `accepted`, `deprecated` or `superseded by ADR-NNNN`.

`kiln records check` verifies the numbering, the statuses and this index.

Three series of numbered records exist, and they are not interchangeable:

| Series | Lives in | Records |
| --- | --- | --- |
| `ADR-NNNN` | this folder | A standing design ruling. Current until superseded. |
| `D-NNN` | [`docs/decisions.md`](../decisions.md) | An event in building Kiln: a choice, a measurement, a spend, an adoption, a deferral. Append-only. |
| `DEC-NNNN` | each solution's decision store | A decision the Council makes while building a solution. Not in this repo. |

## Index

| ADR | Ruling | Status |
| --- | --- | --- |
| [ADR-0001](0001-no-vote-the-owning-expert-decides.md) | There is no vote: the owning expert decides | accepted |
| [ADR-0002](0002-typed-artefacts-not-conversation.md) | Agents exchange typed artefacts, not conversation | accepted |
| [ADR-0003](0003-one-shared-core.md) | One shared profile, source registry, tool registry and decision store | accepted |
| [ADR-0004](0004-governance-decides-applicability.md) | Governance decides whether a regime applies; the domain expert decides how to meet it | accepted |
| [ADR-0005](0005-a-human-sets-classification.md) | A human information owner sets classification | accepted |
| [ADR-0006](0006-rules-start-as-typed-python.md) | Rules start as typed Python; Conftest and OPA wait | accepted |
| [ADR-0007](0007-generated-code-runs-only-in-sandboxes.md) | Generated code runs only in Modal sandboxes | accepted |
| [ADR-0008](0008-researcher-discovers-external-datasets.md) | The Researcher discovers external datasets and hands over a manifest | accepted |
| [ADR-0009](0009-one-profiler-one-record-linkage-skill.md) | One profiler and one record-linkage skill, owned by the Data Engineer | accepted |
| [ADR-0010](0010-duckdb-first-data-stack.md) | DuckDB first, Polars for transforms, Pandera for contracts | accepted |
| [ADR-0011](0011-one-gate-model-g0-to-g5.md) | One gate model, G0 to G5 | accepted |
| [ADR-0012](0012-one-autonomy-envelope.md) | One Green, Amber, Red and Tom envelope for agents and loops | accepted |
| [ADR-0013](0013-tom-decides-at-four-gates-and-can-override.md) | Tom decides at four gates and can override anything | accepted |
| [ADR-0014](0014-the-swarm-is-ralph-loops-in-modal.md) | The swarm is a coding-agent CLI running Ralph loops in Modal | accepted |
| [ADR-0015](0015-change-monitor-in-phase-2.md) | The source change monitor is built in phase 2 | accepted |
| [ADR-0016](0016-evidence-matched-to-the-question.md) | Evidence is matched to the question | accepted |
| [ADR-0017](0017-council-skill-packaging.md) | A Council skill is a SKILL.md, a typed function and its tests | accepted |
| [ADR-0018](0018-production-quality-in-proportion.md) | Production quality in proportion, behind real-world testing and expert assessment | accepted |
| [ADR-0019](0019-four-tripwires.md) | Four tripwires replace the proposals' hard constraints | accepted |
| [ADR-0020](0020-obligations-designed-in-deferrals-recorded.md) | Obligations are designed in; a deferral needs a reason and Tom | accepted |
| [ADR-0021](0021-quality-findings-fixed-or-dismissed-with-a-reason.md) | Quality findings are fixed, or dismissed with a recorded reason | accepted |
| [ADR-0022](0022-transferability-is-a-soft-preference.md) | Transferability is a soft preference | accepted |
| [ADR-0023](0023-proportionality-profile.md) | Every solution carries a proportionality profile | accepted |
| [ADR-0024](0024-handover-at-g4.md) | The Council hands over a test-ready build at G4; Tom's team runs the test | accepted |
| [ADR-0025](0025-tom-approves-the-plan-at-g2.md) | Tom approves the plan at G2, before any code is written | accepted |
| [ADR-0026](0026-one-cross-provider-reviewer-before-g2.md) | One reviewer from another model provider red-teams the plan before G2 | accepted |
