# Solution Architect (Chair)

The Solution Architect owns the coherent technical design and turns it into a contract the swarm builds against. It is an architecture decision engine, not an architecture chatbot: rules and arithmetic do the routine work, and inference is spent comparing imperfect options.

**Covers**

- Intake: works out with Tom the problem, the users, the DVF hypotheses, the proportionality profile and the budget. The build target is production quality unless Tom asks for less.
- Reuse before build: searches the Australian Government Architecture (AGA), approved patterns and earlier Council solutions before designing anything new.
- Quality attributes: turns "fast, reliable, cheap" into measurable scenarios.
- Options: two or three genuinely different architectures, with invalid ones removed by rule and the rest scored.
- Decisions: an ADR for every significant choice, with alternatives, evidence, trade-offs, reversibility and dissent.
- Architecture as code: C4 in Structurizr DSL, and an OpenAPI contract for every HTTP boundary.
- Cost and capacity: deterministic estimates, never model intuition.
- Routing and chairing: decides which experts see which decision, sends each a small dossier, and resolves soft trade-offs.
- Build contract: indexes the domain contracts, derives fitness functions from ADRs, cuts the tickets and judges unplanned changes against the autonomy envelope. At G4 it hands Tom the test-ready build and a real-world test plan written with the UX Designer and Data Analyst.

**Does not cover**

- Threat models and security control interpretation (Security Architect).
- Whether a law or policy applies, and privacy or records interpretation (Governance Guru).
- Data models, pipelines and migrations (Data Engineer).
- Statistical validity (Data Analyst).
- User journeys and accessibility conclusions (UX Designer).
- Research method and evidence gathering (Researcher).
- Lifting a tripwire (Tom).
- Writing production code (coding swarm).

**Build first**

| Item | Kind | How to treat it |
| --- | --- | --- |
| Australian Government Architecture | Knowledge | Ingest its structure (domains, capabilities, designs, policies, standards and the links between them), not just its text. Scheduled refresh. |
| Digital Access Standard and Whole-of-Government Cloud Computing Policy | Knowledge | Versioned, with applicability rules. The cloud policy took effect on 1 July 2026. |
| C4 model, Structurizr DSL and MADR | Knowledge | Local reference. They set the vocabulary for every model and decision record. |
| Quality-attribute model and five decision guides | Knowledge (authored) | Write once: build, reuse or buy; execution platform; relational persistence; AI versus deterministic; RAG pattern. Each guide lists its disqualifiers. Simplicity and delivery speed weigh heavily; transferability counts, but never at a real cost to either. |
| `compile_project_profile` | Skill | Pydantic schema plus targeted questions. Unknowns stay unknown. |
| Routing triggers | Rules | One table mapping profile facts to experts, such as a new endpoint or secret to Security and a new store to the Data Engineer. |
| `find_government_reuse_candidate` | Skill | AGA search through the shared retrieval service, run before any option is generated. |
| `compare_architecture_options` | Skill | Weighted matrix. The model supplies evidence and explanation; code does the arithmetic. |
| `create_or_supersede_adr` | Skill | MADR template plus the extended fields, with a validator that rejects missing alternatives or evidence. |
| `estimate_solution_cost` | Skill | Calculator for storage, requests, tokens, compute and egress, fed by live prices from the Researcher. Includes cost at scale as viability evidence. |
| `compile_build_contract` | Skill | Indexes domain contracts, derives fitness functions and writes tickets with acceptance criteria and blocking edges. |
| Structurizr CLI, Mermaid and an OpenAPI validator | Tools | Run in a sandbox to validate and render. |

**First slice.** Take three sample briefs: a public form service, an internal RAG assistant and a data dashboard. For each, produce a profile, a maturity target, one reuse search, two options, one ADR, a C4 context and container view, a ticket list a single Ralph loop can start on, and an evidence plan for each hypothesis. These three runs become the chair's first eval set.

**Later.** IaC inspection, Conftest, Infracost, drift detection, OpenTelemetry checks, and AsyncAPI once event-driven work appears. arc42 packs and the AWS, Azure and Google well-architected frameworks are cross-checks, not first-build knowledge.

**Detail:** Solution proposal, sections: Role, authority and decision model; Core government corpus; Toolkit and skills; Council workflow and escalation; Prioritized build plan; The most valuable custom skills to build.
