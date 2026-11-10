# Sketch: phase 0, the shared core

**Status: proposed (D-005). Nothing here is built. For Tom to approve, change or replace.**

This is the SOP's design sketch (T5) for the charter's phase 0. It does not pre-empt the
grilling session: if Tom would rather grill the charter first, slice 1 waits for it, and the
grilling's answers replace anything here they contradict.

## Purpose, and who calls it

The shared core is the machinery every agent uses, built once (ADR-0003). In phase 0 it has
one job: carry **one thin path from brief to code**, with the harness controls in place
before any agent has a tool. Its callers are the seven experts, the coding swarm, the gates
and Tom.

## Shape

```text
  Tom's brief
      │  intake
      ▼
 ┌──────────────┐   typed artefacts only    ┌───────────────────────────┐
 │ Project      │◄─────────────────────────►│ Experts (phase 1 onwards) │
 │ profile      │                           └───────────────────────────┘
 └──────┬───────┘
        ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ Gates G0 → G5: nodes that only validate artefacts.           │
 │ Only a validation node writes a pass. A tripwire pauses any. │
 └──────┬───────────────────────────────────────────────────────┘
        │ reads and writes
        ▼
 ┌───────────┬────────────┬───────────┬────────────┬────────────┐
 │ Decision  │ Source and │ Evidence  │ Spend      │ Sandbox    │
 │ store     │ tool       │ store     │ ledger     │ runner     │
 │           │ registries │ (by hash) │            │            │
 └───────────┴────────────┴───────────┴────────────┴────────────┘
   files are the record; Postgres indexes them; R2 holds the bytes
```

One package, `src/kiln/`, one module per component, each a small typed interface over its
internals.

## Contracts others will depend on

These are settled in slice 1, before their first consumer, because changing one later means
changing every agent.

| Contract | Proposal |
| --- | --- |
| **Record ids** | Every id names its kind: `DEC-0001` (decision record), `OBL-…` (obligation), `FND-…` (finding), `TKT-…` (ticket). Evidence is addressed by content: `sha256:<hex>`. |
| **Source ids** | Every id an agent sees names its source: `<source>:<local-id>`. Stores keep local ids; the boundary qualifies them (the SOP's lesson from D-057, applied from the first build). |
| **Actor** | Every decision, approval and override names who made it (`tom`, an expert, `validator`), when, and its id. Prose cannot confer one (charter rule 5). |
| **Basis** | One enum of seven values on every claim: observed, authoritative, rule, supported, inferred, assumed, unknown. |
| **Bands, tripwires, gates** | One enum each: Green, Amber, Red, Tom; the four tripwires; G0 to G5. |
| **`unknown`** | A valid value in a profile, distinct from missing. |
| **Trace names** | `<agent>.<node>`, with the build's identity on every trace (SOP §20.0). |
| **Storage rule** | Files are the record and Postgres is an index (D-005, F2; needs Tom's adoption). |

## What it must survive later

- **Seven agents with their own sections** of one profile, and their own extensions of one
  decision format.
- **Many solutions,** each with its own repo and its own `council/` folder.
- **A second model provider** reviewing a plan it did not write (ADR-0026).
- **The real-data boundary:** nothing in the core may assume it can see real data
  (ADR-0024). That is why provenance, not screening, should be the control (D-005, R4).
- **A coding loop that would mark its own work as passing** (D-005, R3): the pass is written
  by a verifier.

## Build order

Each slice is one session, runs end to end, and is checked by something that can be run. The
charter asks for schemas, gates and the decision store to be built by hand with Tom watching
(HITL), so slices 1 to 3 are sessions Tom steers.

| Slice | Builds | Needs | Spends | Checked by |
| --- | --- | --- | --- | --- |
| **1. Vocabulary and records** | The enums above. `ProjectProfile` (question, users, DVF hypotheses, proportionality profile, budget, a section per expert). `Decision` and a file-backed decision store that renders `DEC-NNNN-<slug>.md`. An approval command that writes Tom's decision as a record (D-005, A4). | Nothing | $0 | Three sample briefs (public form service, internal RAG assistant, data dashboard) validate as profiles. Fixture tests for every rejection. |
| **2. Gates** | G0 to G5 as a LangGraph state machine whose nodes only validate artefacts. Only the validation node writes a pass. | Slice 1 | $0 | A sample brief walks G0 to G5 on fixture artefacts. A missing artefact fails its gate. A test tries to write a pass from outside the validation node and is refused. |
| **3. Tripwires and the spend ledger** | A check per tripwire: gitleaks (done), a dataset origin manifest, an egress allowlist, a spend ledger in dollars with a warning before the stop (D-005, A1). | Slice 2; Tom's ruling on R4 | $0 | One fixture fires each tripwire and pauses the gate. |
| **4. Services** | Pinned clients for Neon (schemas and roles per the charter), R2 (evidence by hash) and Langfuse (a tracer that refuses to be switched off silently). `kiln doctor` gains live checks for each. | Neon and R2 secrets; a Langfuse project for Kiln (D-005, F1) | $0 on free tiers | `kiln doctor` reports phase 0 ready. A round trip stores and reads back an artefact by hash. A trace is read back through the API. |
| **5. Ingestion, once** | Fetch, hash, store in R2, normalise, index in Postgres full-text and pgvector, register the source: one path, on one small source. Each stage is deterministic and writes a manifest. | Slice 4; Tom's ruling on F2; an embedding model | Cents, if the embedder is a paid API | A re-run is byte-identical. The source's inventory is counted before the profile is trusted (SOP §15.1). |
| **6. Sandbox runner** | A Modal runner with a spend cap per run, a scoped short-lived token, and the egress allowlist (D-005, A2). | Modal secrets; a budget | Cents | A trivial generated program runs under the cap and its trace is read back. An attempt to reach a host off the allowlist fails. |
| **7. First eval sets** | Three sample briefs with DVF hypotheses and proportionality profiles, and 20 golden research questions that start with the charter's own dated policy claims (D-005, R6). | Slice 1 | $0 to draft | Claude drafts; Tom approves each set and its pass rule before any run. |

Slices 1, 2 and 7 need no secret and no money, and can start as soon as this is approved.

The other shared-core components in the charter's table (the change monitor, the retrieval
service, the Obligation-Control-Evidence matrix, the renderers, the capability broker, the
assurance case) arrive with the agent that first needs them, from phase 1 on.

## For Tom

1. **Approve this build order,** or say what to change. Recommended: yes, starting with
   slice 1.
2. **Grill first, or build slice 1 first?** Recommended: grill the charter's front page and
   operating model first, since slice 1 freezes their vocabulary into schemas.
3. The rulings slices 3 and 5 wait on are in the handover: D-005 R4 and F2.
