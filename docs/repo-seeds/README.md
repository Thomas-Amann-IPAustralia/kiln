# Seeds (sealed)

The planning documents Tom put in the repo before the first session. They are the inputs the
live design was derived from, kept exactly as they arrived. **Do not edit them.**

| Seed | What it is | Where it lives on |
| --- | --- | --- |
| `sop-agent-construction-v3.md` | The SOP: how Tom and Claude work together, how a thing is known to be true, and how one agent is built. Still current; read it here. | Condensed into [`CLAUDE.md`](../../CLAUDE.md), which is the rulebook from session two on |
| `Council Construction — Consolidated Charter.md` | The controlling design for the Council, 10 November 2026 | [`docs/charter/`](../charter/README.md) (live; it wins where they differ), [`docs/adr/`](../adr/README.md), [`GLOSSARY.md`](../../GLOSSARY.md) |
| `Agentic Software Factory Proposal.md` | Tom's original brief, and the infrastructure draft | Overruled in places: see the [proposal map](../charter/proposal-map.md) |
| `Solution`, `Researcher`, `Security`, `Governance`, `Data E`, `Data A`, `UX Proposal.md` | One proposal per Council agent, each written without sight of the others | Detail only, never authority: see the [proposal map](../charter/proposal-map.md) |
| `26-11-11_docs-review.md` | A review of the nine documents above for consistency and gaps | Worked through in D-005 of [`docs/decisions.md`](../decisions.md) |

## Why they are sealed

The live documents were derived from these files as they stood. `MANIFEST.sha256` records each
file's hash, and `kiln records check` fails when a seed changes, disappears or appears. That
failure means the derivation is stale, in the same way a source can change under a knowledge
base's snapshot (SOP §16.5).

**To add or replace a seed:** put the file here, reconcile the live documents with it, record
that in a decision entry, then reseal:

```bash
cd docs/repo-seeds && sha256sum -- *.md | grep -v '  README.md$' > MANIFEST.sha256
```

## Known problems in the seeds

Carried here so that nobody rediscovers them. None is fixed in the seeds themselves.

- **The proposals' citations are dead.** They are export tokens that resolve to nothing, so
  no dated policy fact in a proposal can be traced. Treat each as `assumed` until verified at
  its source.
- **The charter's two diagrams are missing.** The gate flow and the build roadmap were
  pictures. The live charter holds reconstructions, marked as such.
- **The proposals contradict the charter** on consensus, hard release gates, the number of
  gates and dismissing findings. The proposal map lists each case and the ADR that rules.
- **`CONTEXT.md` is now `GLOSSARY.md`,** and the skills install command differs from the
  charter's (D-004).
