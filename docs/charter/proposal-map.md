# The proposals: how to read them, and where the detail lives

The seven proposals and the original brief are sealed in
[`docs/repo-seeds/`](../repo-seeds/README.md). They were written before the charter, each
without sight of the others, and the charter overruled parts of every one. Read them for
detail, never for authority.

## How to read a proposal

1. **The charter wins.** Then the ADRs, then the proposal for the agent concerned, then the
   other proposals ([precedence](README.md)).
2. **For something the charter names, the proposal supplies the detail.** Something the
   charter does not name is outside the first build.
3. **Check the table below before acting on a proposal.** It lists what the charter overruled
   in that file.
4. **Dated policy facts are `assumed`.** The proposals' citations are export tokens that
   resolve to nothing. A fact with a date (a commencement, a version, a mandate) is verified at
   its source before anything is built on it.
5. **A proposal's "must", "hard gate" and "cannot" are its author's words,** not the Council's
   rules. The Council's stops are the four tripwires.

## What the charter overruled in each proposal

> **Added to the seed's Appendix B** (review item 5). Derived from the ADRs' "conflict it
> settled" text; each row cites the ADR that rules.

| Proposal | It says | The charter rules |
| --- | --- | --- |
| The brief (Agentic Software Factory Proposal) | Experts reach consensus | No vote: the owning expert decides, the chair settles clashes (ADR-0001) |
| | Experts advise and confer | Typed artefacts, not conversation (ADR-0002) |
| | Solutions could go straight to production | A real-world test, then human experts, come first (ADR-0018) |
| | A swarm of coding agents | One sequential loop first (ADR-0014) |
| Solution | A 17-stage workflow | Six gates, G0 to G5 (ADR-0011) |
| | Hard, soft and advisory constraints, and its own autonomy envelope | Tripwires, obligations and preferences; one envelope (ADR-0019, ADR-0012) |
| | Portability and exit as design drivers | A soft preference, below speed and simplicity (ADR-0022) |
| | OPA and Conftest at P1 | Typed Python first (ADR-0006) |
| | PSPF detail sits with Security | Governance decides whether a regime applies (ADR-0004) |
| | Its own source schema, registry and profile; one authority ranking | One shared core; evidence matched to the question (ADR-0003, ADR-0016) |
| | Freshness monitoring at P1 | The change monitor arrives in phase 2 (ADR-0015) |
| | "Human" approves the architecture | Tom approves the plan at G2 (ADR-0013, ADR-0025) |
| Security | OPA and Conftest at the core now | Typed Python first; Conftest with the first infrastructure code (ADR-0006) |
| | Its checks are hard release gates | Obligations designed in; deferral recorded and settled by Tom at G4 (ADR-0020) |
| | Agents cannot suppress a finding | Fix, or dismiss with a recorded reason; critical and high settled before G4 (ADR-0021) |
| | Many hard constraints and escalation triggers | Four tripwires (ADR-0019) |
| | Classification set by Governance or a human; its own autonomy table | A human information owner; one envelope (ADR-0005, ADR-0012) |
| Governance | Nine gates | Six gates (ADR-0011) |
| | Its checks are hard release gates; many hard triggers | ADR-0020, ADR-0019 |
| | Its own source registry and data model | One shared core (ADR-0003) |
| | Change detection is core and early | Phase 2, with a live check until then (ADR-0015) |
| Researcher | Its own source and tool registry | One shared core (ADR-0003) |
| | A dataset discovery mode and a generic SDMX service | Kept, as the only one: it returns a Data Source Manifest, and one SDMX service serves everyone (ADR-0008) |
| Data-E | Data discovery is its duty | The Researcher discovers; the Data Engineer profiles (ADR-0008) |
| | Polars at P0, then Great Expectations | DuckDB first, Polars for transforms, Pandera for contracts; Great Expectations deferred (ADR-0010) |
| | Project decisions rank above law as a source | Evidence matched to the question (ADR-0016) |
| | PSPF interpretation sits with Security; classification with Security or the owner | ADR-0004, ADR-0005 |
| | Its own autonomy table | One envelope (ADR-0012) |
| Data-A | Its own ABS connectors and discovery layer | One SDMX service; the Researcher discovers (ADR-0008) |
| | Its own profiler and Splink wrapper (Data-E has one too) | One of each, owned by the Data Engineer (ADR-0009) |
| | pandas and Pandera at P0 | pandas only where a library needs it (ADR-0010) |
| | Analysis may run on the Oracle host | Generated code runs only in Modal sandboxes (ADR-0007) |
| UX | Its own pipeline | Six gates (ADR-0011) |
| | Its checks are hard release gates; its own autonomy table | ADR-0020, ADR-0012 |
| Every proposal | "Skill" means a workflow, a function or a review | One packaging: a SKILL.md, a typed function and its tests (ADR-0017) |

## Where the detail lives

> From the seed's Appendix B, unchanged. Section names are as they appear in each file.

Agent-specific detail is listed at the end of each [agent charter](agents/). This map covers topics that span several proposals; section names are as they appear in each file.

| Topic | Where to read more |
| --- | --- |
| Source metadata and authority ranking | Solution: Recommended source schema; Authority should outrank semantic similarity. Governance: Give the Guru a source registry before giving it broad web search. Researcher: Source records should preserve temporal provenance. |
| Retrieval order | Solution: Use four retrieval layers. Security: Retrieval strategy. Governance: A sensible retrieval order. Data-E: Do not use one undifferentiated RAG index. |
| Change monitoring | Governance: Change detection should be a first-class tool. Researcher: Currentness should be tested, not assumed. UX: Dynamic web lookup. |
| Tool registry and discovery | Solution: Tool discovery should be controlled, not open-ended. Researcher: Tool discovery itself. Data-A: Tool and capability discovery. Data-E: Tool discovery should itself be an agent capability. |
| Decision records | Solution: Give every architectural decision an executable form. Security: Security artefacts should live with the software. Data-E: Keep provenance on the agent's own decisions. |
| Disagreement packets and routing | Governance: A formal disagreement packet for the Council Chair. Solution: Route experts using triggers. |
| Autonomy envelope | Solution: Give coding agents an autonomy envelope. Security: Coding-swarm autonomy. Data-E: Autonomy and mandatory escalation. UX: Risk-sensitive UX autonomy. |
| Harness security and infrastructure fit | Security: Agentic-system security should be its own specialty; Fit to your proposed infrastructure. |
| Contracts for the swarm | Solution: Architecture fitness functions are especially valuable here; Suggested architecture repository contract. Governance: Give coding agents machine-readable governance constraints. UX: A structured UX contract for the coding swarm. |
| Evidence and provenance | Researcher: The Research Packet. Governance: Provenance on every meaningful governance claim; Separate evidence from observability logs. Data-A: Standard analytical artefacts. |
| Gates and escalation triggers | Governance: Use explicit governance gates; Deterministic escalation triggers. Solution: Proposed architecture workflow. |
| Original brief and infrastructure | Agentic Software Factory proposal. |
