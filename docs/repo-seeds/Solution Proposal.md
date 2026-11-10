# Proposal for the Solution Architect Agent’s Knowledge Base and Toolkit
 
## Executive recommendation
 
Your initial role description — **“Defines what technology components are required to achieve the desired outcome”** — is directionally right, but I would broaden it substantially.
 
For this system, the Solution Architect should be **the Council’s integrator of constraints, quality attributes, trade-offs, reusable capabilities, and technical decisions**. It should not try to become a substitute Security Architect, Data Engineer, Governance Guru or UX Designer. Its distinctive competence should be taking the outputs and constraints of those specialists and turning them into **one coherent, buildable and testable architecture**.
 
This distinction matters particularly in the environment you describe. Generative AI has made *implementation effort* a poor proxy for *solution maturity*: a coding swarm may produce a substantial working application before anyone has established whether its identity model, records behaviour, accessibility, recovery objectives, operational cost or deployment topology are appropriate. I therefore recommend that the Solution Architect classify maturity by **evidence and controls**, rather than by how much code exists.
 
The most important design decision I would make is to turn the Solution Architect into **less of an architecture chatbot and more of an architecture decision engine**. Most of its routine work can be structured or deterministic; inference should be concentrated in the genuinely valuable task of comparing imperfect alternatives.
 
| Capability | Recommended implementation | Why it matters |
|---|---|---|
| **Applicability engine** | Deterministic rules over a structured project profile | Decides which Australian Government policies, standards and Council experts are relevant before design begins. |
| **Reuse-before-build search** | Structured search of the Australian Government Architecture (AGA), internal pattern catalogue and previously approved solutions | The AGA explicitly promotes reusable government capabilities/designs, while the Digital Access Standard directs agencies toward reuse rather than unnecessary duplication. citeturn0view1turn12search6 |
| **Quality-attribute engine** | Standard scenarios and weighted option matrix | Forces the agent to reason about reliability, cost, portability, performance, accessibility, security, operability and maintainability rather than merely choosing technologies it recognizes. |
| **Architecture Decision Records** | Deterministic template plus LLM-assisted analysis | Creates a durable explanation of *why* an architecture was selected rather than just what was selected. ADR methods explicitly capture significant architectural decisions and their rationale/consequences. citeturn15search3turn15search27 |
| **Architecture-as-code** | C4 model + Structurizr DSL; Mermaid for lightweight diagrams | Structurizr provides a text-based C4 architecture model, supports documentation and ADRs, and can validate/inspect/export architecture definitions. citeturn21view0 |
| **Contract-first integration** | OpenAPI, AsyncAPI and CloudEvents where applicable | These give machine-readable interface and event contracts that coding agents can implement and test rather than infer. citeturn20view0turn20view1turn20view2 |
| **Architecture fitness functions** | Tests derived from approved decisions | Converts Council decisions into executable constraints so the coding swarm can detect architectural drift automatically. |
| **Cost modelling** | Deterministic calculators + Infracost for supported IaC + live vendor pricing | AGA guidance now explicitly covers FinOps and AI-related costs; Infracost can evaluate IaC and expose cost changes in engineering workflows. citeturn4search26turn22view1 |
| **Technology/supply-chain vetting** | Approved-tool registry + OpenSSF Scorecard + OSV + SBOM/provenance checks | OpenSSF Scorecard evaluates project security practices, while modern SBOM and provenance specifications allow dependencies and build provenance to be recorded systematically. citeturn22view2turn22view3turn23view0turn23view2 |
| **Source freshness and authority control** | Metadata-filtered retrieval before semantic retrieval | Australian Government policies have applicability dates, versions and statuses; stale guidance should not silently outrank current mandatory material. citeturn4search3turn3search0turn3search16 |
 
I would **not** add a separate vector database, knowledge graph platform or enterprise architecture product initially. Given your existing Neon/Postgres/pgvector design, add PostgreSQL full-text search for lexical retrieval and metadata filtering alongside vectors. PostgreSQL already provides parsing, indexing, query processing and result ranking for full-text search. citeturn23view3 The architecture corpus is small enough that good metadata and routing will matter considerably more than exotic retrieval infrastructure.
 
A second important recommendation is to alter the Council's concept of **consensus**. Mandatory constraints should not be decided by majority vote. A Security Architect should not be “outvoted” when it identifies an applicable mandatory security requirement, nor should an accessibility or records requirement disappear because four other agents prefer a simpler architecture. I would instead use:
 
**binding constraint → decision owner → consultation → dissent → human risk acceptance**
 
The Solution Architect chairs trade-offs among *legitimate options*. It does not have unilateral authority to waive a binding constraint.
 
## Role, authority and decision model
 
### A stronger role definition
 
I would give `Squire_Solution-Architect` a role definition approximately equivalent to:
 
> **Owns the coherent technical design of the solution. Determines system boundaries, component responsibilities, integration patterns, deployment topology, quality-attribute trade-offs and technology selections; identifies and incorporates applicable external constraints; prefers reuse and simplicity; records significant decisions and alternatives; translates approved architecture into machine-testable constraints for implementation; and chairs cross-domain technical disagreements without overriding binding specialist constraints.**
 
This gives the agent a clear identity distinct from “senior programmer.”
 
### Council boundaries
 
The Solution Architect should know enough of adjacent disciplines to recognize when they matter, but *recognition and integration* should be its responsibility rather than detailed interpretation.
 
| Decision area | Solution Architect responsibility | Primary expert | Recommended authority |
|---|---|---|---|
| System boundaries, component decomposition, deployment topology | **Own** | Solution Architect | SA decides |
| Build/reuse/buy and technology alternatives | **Own** | SA, Researcher | SA decides after evidence |
| Cross-domain quality-attribute trade-offs | **Chair** | Relevant Council members | SA decides unless binding constraint exists |
| Threat model, control interpretation, security architecture | Integrate and challenge assumptions | Security Architect | Security expert owns security conclusions |
| Data modelling, movement, persistence, lineage implementation | Integrate | Data Engineer | Data Engineer owns domain design |
| Statistical/analytical validity | Understand architectural requirements | Data Analyst | Data Analyst owns methodology |
| Privacy, records, AI governance and policy interpretation | Incorporate constraints | Governance Guru | Governance owns compliance interpretation |
| User journeys, accessibility and interaction design | Ensure architecture can support them | UX Designer | UX owns user-design conclusions |
| Evidence gathering and uncertain factual questions | Define evidence required | Researcher | Researcher owns research method |
| Mandatory requirement conflict | Record conflict and alternatives | Relevant experts | Human escalation if no compliant resolution |
| Optional preference conflict | Resolve trade-off | Council | SA as chair |
 
This division also suggests an important knowledge-management principle: **do not duplicate every specialist's KB into the Solution Architect's KB**. Maintain a small shared “constitutional corpus” of cross-cutting mandatory material, while the SA holds indexes, architectural implications and escalation triggers pointing into specialist corpora.
 
### Replace “prototype versus production” with evidence-based maturity
 
Because working software can now arrive extremely early, I recommend an explicit `solution_maturity` field.
 
| State | What it proves | What it does **not** imply |
|---|---|---|
| **Experiment** | Tests a hypothesis or technique | Architectural suitability |
| **Proof of concept** | Demonstrates that a difficult capability can work | User value, robustness or operational readiness |
| **MVP** | Delivers the minimum coherent user/business outcome | Suitability for unrestricted production |
| **Pilot** | Exercises the solution with controlled real users/data/processes | General production readiness |
| **Production candidate** | Has architecture evidence, required controls, operational arrangements and traceable decisions | Final organisational approval |
| **Production** | Has passed the relevant human/organisational assurance and release processes | Permanent architectural correctness |
 
The important consequence is that **a fully functioning application generated in an afternoon can still be an Experiment**. The classifier is not based on lines of code.
 
### Give every architectural decision an executable form
 
A conventional ADR is a good base, but I would extend it for an agentic development environment.
 
Every significant decision should record:
 
| Field | Purpose |
|---|---|
| `decision_id` | Stable reference for agents and commits |
| `decision` | What was selected |
| `status` | proposed / approved / superseded / rejected |
| `decision_owner` | SA or named Council expert |
| `drivers` | Requirements and quality attributes causing the decision |
| `binding_constraints` | Policy, security, privacy, user or operational constraints |
| `options_considered` | Genuine alternatives |
| `evidence` | Source citations, experiments, measurements |
| `tradeoffs` | Benefits surrendered as well as gained |
| `assumptions` | Facts which may later prove false |
| `confidence` | Confidence in evidence, not merely LLM confidence |
| `reversibility` | Easy / moderate / costly / practically irreversible |
| `consequences` | Expected implications |
| `dissent` | Council disagreement preserved rather than averaged away |
| `review_triggers` | Events requiring reconsideration |
| `fitness_functions` | Automated checks that enforce the decision |
| `supersedes` | Previous ADR where relevant |
 
MADR is particularly suitable as a seed because it provides a streamlined structured format for significant architecture decisions; Structurizr can also associate ADRs with architecture documentation. citeturn15search27turn21view0
 
## Australian Government knowledge base
 
This should be the most authoritative portion of the Solution Architect's KB when a Commonwealth Government context applies.
 
The AGA itself should be more than another RAG collection. It has domains covering service delivery, individual experience, technology, cyber security, data and analytics, AI, interoperability and governance, with artefacts including capabilities, policies, standards and designs. citeturn0view1turn14search6 I would ingest its structure and relationships so the SA can reason:
 
**capability required → existing government capability/design → associated standard/policy → architectural constraint**
 
rather than merely search passages that happen to contain similar words.
 
### Core government corpus
 
| Knowledge source | Priority | Treatment | Why the Solution Architect needs it |
|---|---:|---|---|
| **Australian Government Architecture** | **P0** | Structured ingestion + scheduled refresh | Make this the first reuse/design lookup. Preserve Domains, Capabilities, Policies, Standards, Designs, status and relationships rather than flattening everything into chunks. The AGA is intended to align digital investment/design with government direction. citeturn0view1turn14search6 |
| **Digital Experience Policy and Digital Service Standard** | **P0** | Structured criteria/checklist | The Digital Service Standard is now fully in effect and includes criteria around intent, users, inclusion, connected services, trust, reuse, avoiding harm and purposeful innovation. DTA also publishes checklists that lend themselves to deterministic assessment. citeturn12search5turn12search11turn12search19 |
| **Digital Inclusion Standard** | **P0** | Applicability trigger + checklist | It addresses diversity, motivation to use digital channels, user protection, accessibility and flexibility/choice, and its scope includes a broad set of public- and staff-facing digital services. The SA should detect applicability, while the UX Designer owns detailed design interpretation. citeturn12search2turn12search14 |
| **Digital Access Standard** | **P0** | Reuse/consolidation gate | Especially important to your system: it emphasizes reducing duplicated entry points and prioritizing reuse, integration and consolidation. One criterion specifically directs users toward the AGA to identify reusable capabilities/platforms. citeturn12search0turn12search6 |
| **Digital Performance Standard** | **P0** | NFR/SLO input | Its criteria include monitoring, service availability, success and understanding whether customer needs are being met. This is a natural bridge from policy to the SA's operational requirements. citeturn12search11 |
| **Whole-of-Government Cloud Computing Policy and guidance** | **P0** | Versioned policy + deterministic applicability | The policy took effect on **1 July 2026** and applies to relevant digital/ICT investments by non-corporate Commonwealth entities across cloud models and lifecycle stages. Associated guidance addresses cloud strategy, legacy retirement, procurement, portability/exit, security/privacy/operational risk, improvement and cost. citeturn4search3turn4search6turn4search10turn4search11 |
| **Government cloud/AI cost guidance** | **P0** | FinOps checklist + calculators | Current AGA guidance calls for cost visibility, accountability, forecasting, allocation and optimization, and explicitly addresses AI expenditure such as model/token/agent/downstream-call costs and accountable ownership. citeturn4search26 |
| **Policy for the Responsible Use of AI in Government** | **P0 when AI involved** | Applicability engine + Governance hand-off | Version 2.0 took effect on **15 December 2025** and requires arrangements including AI strategy/oversight and use-case impact assessment for entities within scope. DTA also released the AI Impact Assessment Tool and government AI procurement guidance. citeturn3search0turn3search10 |
| **Technical Standard for Government's Use of AI** | **P0 when AI involved** | Machine-addressable requirements where feasible | The AGA identifies a technical standard spanning procurement, design, development, deployment and use of AI systems. This should be a direct architecture input rather than relying only on generic responsible-AI principles. citeturn3search17turn12search23 |
| **CSIRO Responsible AI Pattern Catalogue** | **P1** | Pattern catalogue; retain your proposed source | This is exactly the kind of applied pattern layer worth putting between policy and implementation. My browser fetch was blocked by the site during this research session, so I would test your ingestion method rather than assume unattended HTML crawling will work reliably. citeturn0view0 |
| **Protective Security Policy Framework — current release** | **P0** | Shared constitutional corpus; details owned by Security Architect | PSPF Release 2026 is the current framework and organizes government protective-security requirements across security domains. The SA primarily needs scope/applicability and resulting architecture constraints; the Security Architect should own interpretation. citeturn3search16turn3search9 |
| **ASD Information Security Manual** | **P0** | Shared index; deep corpus owned by Security Architect | The ISM provides the Australian Government cyber-security framework for protecting IT and operational-technology systems using risk management. Keep the SA aware of relevant controls without turning it into a second Security Architect. citeturn3search2turn3search8 |
| **Australian Privacy Principles** | **P0 trigger** | Privacy classifier + Governance hand-off | The 13 APPs cover areas including handling, use/disclosure, integrity, correction and access to personal information. Architecture needs to identify where personal information exists and expose the relevant data flows to the Governance/Security experts. citeturn4search7 |
| **OAIC generative-AI privacy guidance** | **P1, conditional** | Retrieve when building/adapting AI | OAIC guidance explicitly addresses organisations that design, build, train, adapt or combine generative-AI models and systems, including adaptation such as fine-tuning. citeturn18search12 |
| **National Archives Information Management Standard** | **P0 trigger** | Records architecture checklist | NAA's standard applies to structured and unstructured Australian Government business information and is grounded in records-management standards. Information creation may be integrated/automated within business processes, making record capture an architecture concern rather than an administrative afterthought. citeturn11search0turn11search12 |
| **Australian Government Recordkeeping Metadata Standard** | **P1** | Schema/reference | NAA provides a metadata standard for consistent description of government information assets. This is useful whenever the solution itself creates or manages official business information. citeturn11search8turn11search28 |
| **Retention/disposal guidance and Records Authorities** | **P0 trigger** | Design question + Governance hand-off | Government information can have retention/disposal requirements, so storage architecture should identify authoritative records, retention hooks, exports and defensible deletion rather than adding them later. citeturn11search20 |
| **AI-generated government records guidance** | **P1 conditional** | AI/records cross-domain trigger | NAA explicitly states that information-management requirements can apply to AI-generated and related records. citeturn11search36 |
| **Digital Sourcing Framework** | **P1** | Build/buy/procure decision input | It is the Australian Government framework underlying digital sourcing and BuyICT. Retrieve it when an architecture assumes procurement, SaaS or external suppliers. citeturn12search25 |
| **Digital Investment Plan policy** | **P1 conditional** | Investment-context trigger | The policy has requirements for relevant Commonwealth entities around current systems, future vision, roadmap, enablers, risks and alignment with government digital direction. It becomes relevant when a “solution” is actually part of a broader agency investment. citeturn5search2 |
| **Digital/ICT Investment Assurance Framework** | **P1 conditional** | Readiness/assurance mapping | The current framework supports government oversight and assurance of digital/ICT investments and includes benefits-management material. The SA should know when its design must supply evidence into that process. citeturn2search9 |
| **AGA reusable designs and standards** | **P1, dynamically selected** | Search rather than wholesale prompt injection | Existing AGA artefacts include reusable patterns/designs relating to authentication, permissions, payments, revenue receipting, data and other common capabilities. The SA should search these by capability before designing a new subsystem. citeturn6search21turn12search20turn12search17turn5search5 |
 
A useful lesson from the 2025–2026 changes is that these cannot be treated as a one-time static corpus. The cloud policy only took effect on **1 July 2026**, the government AI policy is now version 2.0, and PSPF has a current 2026 release. citeturn4search3turn3search0turn3search16 A source that was correctly embedded two years earlier can now be precisely wrong.
 
### Store architectural implications separately from source text
 
I would create an `applicability_rules` table rather than asking the LLM to rediscover scope in policy prose on every run.
 
For example:
 
| Project fact | Deterministic action |
|---|---|
| Commonwealth / non-corporate Commonwealth entity | Evaluate Commonwealth mandatory-policy applicability |
| Uses cloud services | Retrieve current cloud policy + security/privacy/exit/cost requirements |
| Uses AI | Trigger AI policy, impact-assessment workflow, technical standard, privacy/records questions |
| Public-facing service | Trigger Digital Experience suite and UX consultation |
| Staff-facing service | Test Digital Experience applicability rather than assume exemption |
| Handles personal information | Governance + Security consultation; privacy data-flow artefact mandatory |
| Creates government business records | Trigger NAA requirements |
| New authentication capability | Search AGA authentication/reuse designs before creating bespoke identity |
| Payment capability | Search AGA payment designs/standards |
| External SaaS/vendor | Procurement, exit, supply chain, data location and identity questions |
| Material digital investment | Test Digital Investment Plan/assurance applicability |
 
The policy source remains authoritative. The rules merely determine **what must be retrieved and considered**. That separation is important: do not let an LLM-generated summary become the canonical policy.
 
## Architecture and engineering knowledge base
 
The second half of the corpus should be **government-neutral architecture knowledge**. This should mostly teach the agent *how to make and represent decisions*, rather than give it thousands of pages of product documentation.
 
### Architecture methods and frameworks
 
| Source | Priority | Recommended use | Why include it |
|---|---:|---|---|
| **C4 Model** | **P0** | Architecture vocabulary/model | Gives the agent a consistent hierarchy for context, containers, components and supporting views rather than allowing every project to invent diagram semantics. citeturn13search0 |
| **Structurizr DSL** | **P0** | Primary architecture-as-code representation | It directly models C4 in a textual DSL and supports documentation, ADRs, dynamic/deployment views, validation/inspection and export to formats including Mermaid/PlantUML. This is unusually well aligned with agent-generated artefacts. citeturn21view0 |
| **arc42** | **P0** | Architecture document structure | arc42 is a free/open architecture-documentation template and is technology/process agnostic. I would use a reduced arc42 structure as the human-readable “architecture pack.” citeturn13search1 |
| **MADR / ADR practice** | **P0** | Decision log | Use for significant decisions, with your extra evidence/confidence/fitness fields. citeturn15search3turn15search27 |
| **ISO/IEC/IEEE 42010:2022** | **P1 reference** | Conceptual vocabulary and architecture-description discipline | The standard addresses architecture descriptions, viewpoints and related concepts. Because ISO material may be licensed rather than freely redistributable, I would store permitted metadata/notes and use the licensed standard only if you obtain appropriate rights, rather than automatically scraping it. citeturn14search1 |
| **IBM Well-Architected** | **P1** | Cross-check quality attributes | Your proposed source is useful because IBM frames architecture around portability/hybrid operation, resilience, efficient operations, security/compliance, performance and financial/sustainability considerations. citeturn0view2 |
| **AWS Well-Architected Framework** | **P1** | Cloud design/review source | It provides a repeatable framework for assessing security, reliability, efficiency, cost and sustainability and explicitly focuses on understanding the pros/cons of architecture decisions. citeturn17view2 |
| **AWS Decision Guides** | **P1** | Technology decision research | Keep your proposed source. The guides compare AWS service alternatives using decision criteria across areas such as compute, databases, storage and integration, making them useful exemplars for your own provider-neutral decision guides. citeturn0view3 |
| **Azure Well-Architected Framework** | **P1** | Independent cloud cross-check | Azure structures its guidance around reliability, security, cost optimization, operational excellence and performance efficiency, and provides review tooling. citeturn17view0 |
| **Google Cloud Well-Architected Framework** | **P1** | Independent cloud cross-check | Google's framework includes operations, security/privacy/compliance, reliability, cost, performance and sustainability, plus technology-specific perspectives such as AI/ML. Its core principles also emphasize documentation and keeping designs simple. citeturn17view1 |
| **Google SRE material** | **P1** | Reliability/operability patterns | SRE is explicitly focused on engineering practices for operating reliable production systems. It is particularly useful when the SA turns availability/recovery requirements into operational architecture. citeturn16search25 |
| **FinOps Framework** | **P1** | Cost-quality trade-offs | Gives the agent a structured vocabulary around FinOps scopes, principles, phases, maturity, domains and capabilities. Use this behind a simpler internal cost decision process rather than making every Council discussion FinOps-heavy. citeturn17view3 |
 
I would **not** concatenate all four cloud-provider well-architected frameworks and ask the LLM to synthesize them every time. Instead, extract their recurring architecture questions once into your own provider-neutral model, then retrieve the provider-specific source only when a provider decision is under consideration.
 
### Create your own canonical quality-attribute model
 
I suggest giving the SA these top-level dimensions:
 
| Dimension | Example questions |
|---|---|
| **Functional fit** | Can this actually meet the required outcome and workflow? |
| **Simplicity / evolvability** | How many independently moving components are being introduced? How easy is replacement? |
| **Reliability / recoverability** | What fails? What is the blast radius? What are RTO/RPO and availability targets? |
| **Security / privacy** | What trust boundaries, data classes, identities and external dependencies exist? |
| **Performance / scalability** | What throughput, latency, concurrency, storage growth and burst profile are expected? |
| **Operability / observability** | Can operators identify, diagnose and recover from failures? |
| **Cost efficiency** | Fixed cost, usage cost, idle cost, egress, support, AI tokens, human operational cost? |
| **Portability / exit** | Can data and workloads be exported? What happens if a supplier disappears or pricing changes? |
| **Maintainability** | Can coding agents and later humans understand, test and modify the system safely? |
| **Interoperability** | Are interfaces and events explicit and portable? |
| **Accessibility / inclusion** | Can the architecture support applicable channels, assistive technologies and alternative pathways? |
| **Data / records integrity** | Where is authoritative state? What provenance, retention and deletion behaviour exists? |
| **Sustainability** | Are there avoidable computational/storage costs or overprovisioning? |
 
The cloud frameworks substantially overlap on reliability, security, performance, operations and cost, despite different terminology. citeturn0view2turn17view0turn17view1turn17view2 This makes a normalized internal model preferable to letting the agent inherit one vendor's ontology.
 
### Build a small, high-value internal decision-guide library
 
This is one area where custom structuring is worth the work. AWS's decision guides demonstrate the value of explicit criteria, but your SA needs **vendor-neutral** choices. citeturn0view3
 
I would initially author guides for:
 
| Decision guide | Candidate classes to compare |
|---|---|
| **Build / reuse / buy** | Existing government capability; existing OSS; SaaS; bespoke |
| **Application execution** | Managed PaaS; serverless function; container service; VM; Kubernetes |
| **Relational persistence** | Managed Postgres; serverless Postgres; self-hosted; embedded DB |
| **Non-relational storage** | Key-value; document; search; vector; graph; object store |
| **Integration** | Synchronous API; queue; pub/sub; event stream; batch/file transfer |
| **Workflow/orchestration** | Application code; job queue; durable workflow engine; agent graph |
| **Identity** | Existing government identity; workforce IdP; OIDC/OAuth; service identity; bespoke auth as last resort |
| **AI versus deterministic implementation** | Rules/code/search; classical ML; LLM call; RAG; agent; fine-tuning |
| **Model deployment** | Managed API; managed private model; local/self-hosted |
| **RAG** | No RAG; lexical; vector; hybrid; reranked hybrid; graph augmentation |
| **Deployment geography** | Single zone; multi-zone; multi-region; hybrid |
| **State** | Stateless; local ephemeral; shared persistent; event-sourced |
| **Tenancy** | Shared; logically isolated; database/schema isolated; infrastructure isolated |
| **API style** | REST/HTTP; GraphQL; RPC; asynchronous events |
| **Data movement** | Query in place; replication; ETL/ELT; streaming |
| **Observability** | Provider-native only; OpenTelemetry + chosen backend |
| **Secrets/configuration** | Deployment platform secret store; external secret manager; local/developer-only |
| **Search** | PostgreSQL FTS; external search engine; vector retrieval; hybrid |
| **Background compute** | In-process; queue workers; scheduled jobs; ephemeral sandbox/batch |
| **Architecture complexity** | Monolith/modular monolith; services; microservices |
 
Each guide should have machine-readable **decision factors, disqualifiers and evidence requests**. An LLM can explain the recommendation, but deterministic conditions can eliminate obviously unsuitable choices first.
 
### Interface and interoperability standards
 
I would include the specifications themselves where licensing permits, not summaries alone.
 
OpenAPI now defines a language-agnostic, machine-readable interface description for HTTP APIs; AsyncAPI does the equivalent for message-driven APIs across protocols; CloudEvents gives event data a common envelope. citeturn20view0turn20view1turn20view2
 
That allows the architecture agent to say not merely:
 
> “Use an API.”
 
but:
 
> “This boundary is synchronous HTTP and must have an OpenAPI contract committed before implementation.”
 
Likewise:
 
> “These components are asynchronously coupled; define the producer/consumer contract with AsyncAPI and use a normalized event envelope.”
 
This is precisely the kind of deterministic structure that coding agents exploit well.
 
## Toolkit and skills
 
I would think in terms of **skills** rather than merely “tools.” A tool is something the agent can invoke; a skill combines a workflow, allowed tools, deterministic checks, required outputs and escalation conditions.
 
### Core toolkit
 
| Skill/tool | Priority | Execution style | What the Solution Architect should do with it |
|---|---:|---|---|
| **Project Profile Compiler** | **P0** | Deterministic schema + selective inference | Turn the user's natural-language brief into structured facts: entity/jurisdiction, users, data, AI, criticality, integrations, load, budget, deployment, accessibility, records, procurement and unknowns. |
| **Government Applicability Router** | **P0** | Deterministic | Map the project profile to potentially applicable DTA/AGA/PSPF/ISM/privacy/records/AI material and relevant Council agents. |
| **AGA Reuse Finder** | **P0** | Metadata + lexical/vector retrieval | Search government capabilities/designs **before** architecture generation. Return “reuse/adapt/build” candidates with evidence. The AGA and Digital Access Standard make this particularly valuable. citeturn0view1turn12search6 |
| **Architecture Pattern Retriever** | **P0** | Hybrid retrieval | Retrieve a small set of relevant patterns and anti-patterns rather than dumping a pattern library into context. |
| **Quality Attribute Workshop** | **P0** | Structured + inference | Convert vague requirements such as “reliable” into measurable scenarios and identify conflicts. |
| **Option Generator** | **P0** | Inference | Generate genuinely different architectures, ideally two or three, rather than prematurely anchoring on the first plausible stack. |
| **Option Scorer** | **P0** | Mostly deterministic | Weighted decision matrix against mandatory constraints and agreed quality attributes. LLM supplies evidence/explanation; arithmetic is deterministic. |
| **ADR Writer/Validator** | **P0** | Template-driven | Generate ADRs, ensure alternatives/evidence/consequences are present, link to requirements and fitness functions. MADR is a suitable foundation. citeturn15search27 |
| **C4/Structurizr Generator** | **P0** | Deterministic syntax generation + validation | Maintain context/container/deployment architecture in the repository. Structurizr supports C4 DSL, validation, inspection, documentation and ADR integration. citeturn21view0 |
| **Mermaid Renderer** | **P1** | Deterministic | Useful for sequence, state, ER, flow and lightweight diagrams embedded directly in Markdown. Mermaid supports these text-defined diagram types and can be incorporated into production/documentation scripts. citeturn21view1 |
| **OpenAPI validator** | **P0** | Deterministic | Require syntactically valid interface contracts for HTTP boundaries; use contract tests downstream. OpenAPI is machine-readable specifically to describe HTTP service capabilities. citeturn20view0 |
| **AsyncAPI validator** | **P1** | Deterministic | Same concept for event/message interfaces. citeturn20view1 |
| **CloudEvents schema support** | **P1** | Deterministic | Normalize event metadata where event-driven architecture is chosen. citeturn20view2 |
| **Repository Topology Inspector** | **P0** | Deterministic | Inspect directory structure, manifests, dependencies, entrypoints, database migrations, APIs and infrastructure files before advising on an existing system. |
| **Architecture Drift Detector** | **P1** | Deterministic | Compare repository/deployment state with the approved architecture model and ADR constraints. |
| **Infrastructure-as-Code Inspector** | **P0** | Deterministic | Parse plans/manifests and expose resources, networking, storage, regions, public endpoints and dependencies to Council agents. |
| **OPA / policy-as-code adapter** | **P1** | Deterministic | Encode technical rules that are legitimately machine-testable. OPA is designed to apply policy across areas including APIs, Kubernetes, CI/CD and Terraform. citeturn21view2 |
| **Conftest** | **P1** | Deterministic | A practical mechanism for testing configuration/IaC against policy before deployment, complementary to OPA. citeturn21view3 |
| **Infracost** | **P1** | Deterministic + live pricing data | Evaluate supported IaC for cost implications before deployment. Current Infracost supports engineering/CI workflows for Terraform, CloudFormation and AWS CDK across major clouds and now exposes agent-oriented integration. citeturn22view1 |
| **Architecture Cost Calculator** | **P0** | Custom deterministic skill | Your own calculator for storage, requests, network, model tokens, embedding/reranking, background jobs, concurrency and expected monthly ranges. This covers platforms that Infracost cannot. |
| **Capacity/latency calculator** | **P0** | Deterministic | Work through expected requests/sec, concurrency, queue depth, storage growth, bandwidth and latency budgets instead of asking the LLM to perform arithmetic. |
| **Availability/recovery calculator** | **P1** | Deterministic | Check whether proposed redundancy, backups and dependencies are compatible with stated RTO/RPO/availability objectives. |
| **OpenTelemetry architecture checker** | **P1** | Deterministic requirements | Require an observability plan and standardized telemetry boundaries. OpenTelemetry provides APIs/SDKs, collectors and semantic conventions for traces, metrics and logs across many platforms. citeturn19view0 |
| **OpenSSF Scorecard** | **P1** | Deterministic external assessment | Use when the SA proposes a new OSS dependency/tool. Scorecard performs automated checks across source, dependencies, build and project-maintenance practices and can assess third-party repositories. citeturn22view2 |
| **OSV lookup** | **P1** | Deterministic external lookup | Check proposed open-source packages against known vulnerability information; Scorecard itself incorporates OSV for its vulnerability check. citeturn22view2turn22view3 |
| **SBOM generator/validator** | **P1** | Deterministic | Produce a software bill of materials using CycloneDX or SPDX. CycloneDX can represent components, services, dependencies, vulnerabilities and provenance-related information; SPDX is an international open standard and is currently at document version 3.0. citeturn23view0turn23view1 |
| **SLSA provenance checks** | **P2** | Deterministic | Useful as the coding pipeline matures. SLSA defines incremental levels/tracks for supply-chain security and attestation/provenance formats. citeturn23view2 |
| **Live documentation retriever** | **P0** | Live web/API | Fetch current service limits, current pricing, current library/framework support and current government policy at decision time. Do not trust embeddings for volatile facts. |
| **Source Freshness Monitor** | **P1** | Deterministic scheduler | Hash canonical pages, compare changed metadata/content, flag superseded/changed material and re-index. |
| **Ephemeral architecture experiment** | **P1** | Modal sandbox | Permit the SA to ask a coding agent to empirically test uncertain architecture properties rather than speculate: package compatibility, startup time, throughput, memory use, API behaviour, etc. |
| **Architecture Fitness Runner** | **P0/P1** | Deterministic CI | Execute all machine-testable architecture constraints on every relevant pull request. |
| **Council Consultation Router** | **P0** | Deterministic trigger + agent call | Decide which expert needs to review a proposed decision and provide a focused dossier rather than sending every decision to every Council member. |
 
### Architecture fitness functions are especially valuable here
 
This is one of the strongest opportunities created by your agentic development model.
 
The SA should translate suitable ADRs into rules such as:
 
```text
ADR-014: Production data must remain in the approved persistence tier.
Fitness function:
  FAIL if any deployment manifest introduces an unapproved persistent datastore.
 
ADR-019: No component other than the public gateway has public ingress.
Fitness function:
  FAIL if IaC exposes another listener/public IP.
 
ADR-023: All inter-service HTTP interfaces use committed OpenAPI contracts.
Fitness function:
  FAIL if a new service endpoint has no corresponding contract.
 
ADR-031: Estimated baseline infrastructure spend <= approved monthly budget.
Fitness function:
  WARN at 80%; FAIL above approved threshold.
 
ADR-037: All deployable artifacts produce an SBOM.
Fitness function:
  FAIL release pipeline if no valid SBOM artifact exists.
```
 
This changes architecture from **advice that coding agents can forget** into **constraints the swarm physically cannot ignore without an explicit exception**.
 
The Security Architect can contribute security fitness functions; Governance can contribute records/privacy checks; Data Engineering can contribute schema/data-contract checks. The SA owns the combined architecture contract.
 
### Tool discovery should be controlled, not open-ended
 
I would give the SA a searchable **Tool Registry**, rather than unrestricted authority to discover a GitHub project and immediately execute it.
 
Recommended metadata:
 
| Field | Example purpose |
|---|---|
| `tool_id`, `name`, `version` | Identity |
| `capabilities` | What problems it can solve |
| `interfaces` | CLI/API/library/MCP/etc. |
| `deterministic` | Whether outputs can be reproduced |
| `permissions_required` | File, repository, network, cloud, secrets |
| `data_classification_ceiling` | What information may safely be passed to it |
| `external_network_calls` | Supply-chain/data leakage consideration |
| `license` | Adoption constraint |
| `source_repository` | Provenance |
| `approved_version/hash` | Prevent silent tool substitution |
| `maintenance_state` | Adoption evidence |
| `security_assessment` | Scorecard/security findings |
| `vulnerability_state` | OSV or relevant scanner result |
| `estimated_execution_cost` | Cost router input |
| `owner` | Who approved it |
| `last_verified` | Staleness |
| `alternatives` | Avoid dependency lock-in |
| `allowed_agents` | Least-privilege access |
 
OpenSSF Scorecard is well suited as **one input** to that adoption decision because it assesses open-source projects using automated checks covering issues such as maintenance, branch protection, code review, dependency handling and CI/build practices. citeturn22view2 It should not become an automatic “score > X means safe” rule; Security should retain ownership of adoption risk.
 
The governing principle should be:
 
> **Discovery can be autonomous; installation/execution should require the tool to pass the approved-tool workflow.**
 
## Retrieval, source governance and memory design
 
I would invest more effort here than in model prompt engineering. An architect that retrieves the wrong version of the right standard is dangerous precisely because its answer sounds authoritative.
 
### Use four retrieval layers
 
For the Solution Architect, I recommend:
 
**Metadata filter → lexical search → semantic search → optional reranking**
 
rather than vector search alone.
 
PostgreSQL already provides full-text parsing, matching, indexes and relevance ranking. citeturn23view3 Combined with your existing pgvector plan, Neon can therefore handle the SA's early retrieval requirements without adding another datastore.
 
A request such as:
 
> “Design a public-facing AI-assisted grants application service for a Commonwealth department”
 
would first be narrowed deterministically to something like:
 
```yaml
jurisdiction: AU_Commonwealth
entity_type: non_corporate_commonwealth
audience:
  - public
service_type: transactional
uses_ai: true
personal_information: likely
creates_business_records: true
cloud: likely
```
 
The retrieval query then becomes:
 
```text
authority = Australian Government
status = current
applies_to ~= non-corporate Commonwealth entity
topics IN (
  digital-service,
  digital-inclusion,
  cloud,
  AI,
  privacy,
  records,
  cyber
)
```
 
**before embeddings are consulted**.
 
That is far more robust than asking:
 
> “What government architecture guidance seems relevant?”
 
### Recommended source schema
 
Every source/document should carry metadata similar to:
 
| Metadata | Reason |
|---|---|
| `source_id` | Stable identity |
| `canonical_uri` | Deduplication |
| `publisher` | DTA, ASD, OAIC, NAA, W3C, AWS, etc. |
| `authority_class` | Government mandate / standard / official guidance / vendor / community |
| `jurisdiction` | Commonwealth / state / international / vendor |
| `artifact_type` | policy / standard / guidance / pattern / design / specification |
| `binding_level` | mandatory / conditional / recommended / informative / unknown |
| `applies_to` | Entity/service scopes |
| `status` | current / draft / superseded / archived / unknown |
| `effective_from` | Temporal applicability |
| `effective_until` | If known |
| `version` | Human-readable version |
| `supersedes` | Previous document |
| `superseded_by` | Replacement |
| `topics` | AI, cloud, identity, records, etc. |
| `capabilities` | Architecture capabilities affected |
| `owner_agent` | SA/Security/Governance/etc. |
| `retrieved_at` | Freshness |
| `content_hash` | Change detection |
| `raw_object_uri` | Canonical snapshot in R2 |
| `citation_locator` | Page/section/heading |
| `license/reuse_status` | Avoid inappropriate corpus copying |
| `review_required` | Whether automated extraction needs validation |
 
This is especially useful with AGA because its content has explicit categories and current government policy pages expose status/applicability information that can be represented structurally. citeturn0view1turn4search6
 
### Authority should outrank semantic similarity
 
A sensible default ordering would be:
 
| Rank | Source |
|---|---|
| **A** | Applicable legislation / mandatory government policy / controlling government standard |
| **B** | Authoritative Australian Government guidance and government architecture designs |
| **C** | International/open technical standards and specifications |
| **D** | Official vendor documentation/frameworks |
| **E** | Established architecture pattern catalogues/books/projects |
| **F** | Community material |
| **G** | Unverified web content |
 
Recency then operates **within authority**, not blindly across it.
 
A newly published vendor blog post should not outrank the current Australian Government Cloud Computing Policy merely because it is newer or semantically closer.
 
### Split the corpus by volatility
 
| Content | Retrieval strategy |
|---|---|
| C4, arc42 concepts, foundational architecture methods | Local KB |
| Current AGA policies and standards | Local indexed copy **plus live freshness verification** |
| PSPF/ISM | Versioned local corpus plus current-status check |
| Cloud architecture frameworks | Local selective corpus |
| Cloud prices | **Live lookup only** |
| Service quotas/region availability | **Live lookup only** |
| Software/package versions | **Live lookup only** |
| Security vulnerability status | **Live lookup only** |
| OSS project health | **Live assessment** |
| Internal ADRs/project architecture | Repository + structured project memory |
| Measurements from experiments | Project evidence store |
| Council decisions | Authoritative project decision store |
 
### Use your existing infrastructure
 
I would map this onto your stack as follows:
 
| Existing component | Solution Architect use |
|---|---|
| **Neon/Postgres** | Source registry, applicability rules, ADR index, tool registry, project profiles, quality attributes, lexical FTS |
| **pgvector** | Semantic chunk retrieval |
| **Cloudflare R2** | Raw immutable-ish source snapshots, large artefacts, generated architecture packs, evaluation datasets |
| **LangGraph** | Architecture workflow/state machine and Council consultation |
| **Langfuse** | Trace why sources/tools were selected, Council calls, model use and decisions |
| **Modal Sandbox** | Short architecture experiments and repository analyses |
| **GitHub** | Source of truth for architecture-as-code, ADRs, interfaces, fitness functions and generated documentation |
| **Railway/Oracle VM** | Your existing application/reranking arrangement; no additional architecture-specific service initially |
| **Tailscale** | Existing private path for internal supporting services |
 
I see **no compelling reason to introduce Pinecone for this agent at the outset**. Architecture retrieval should be dominated by good metadata and authority filtering; Postgres FTS provides lexical search/ranking and your planned pgvector layer provides semantic retrieval. citeturn23view3 Measure actual retrieval latency/quality before paying the architectural complexity cost of another store.
 
### Keep raw evidence separate from distilled knowledge
 
I would maintain three related objects:
 
**Source**
> Exact authoritative material.
 
**Finding**
> “Requirement X appears applicable because project fact Y.”
 
**Decision**
> “Given requirement X plus requirements A/B, we chose architecture Z.”
 
That chain lets you later reconstruct:
 
**Why is the service deployed this way? → ADR → finding → exact policy source/version.**
 
It also prevents a common RAG failure mode in which a model-generated summary gets embedded, later retrieved as though it were primary evidence, then summarized again until nobody can determine what the original source actually said.
 
## Council workflow and escalation
 
The Solution Architect is best implemented as a **state machine around a few inference-heavy transitions**.
 
### Proposed architecture workflow
 
| Stage | Default mode | Output | Council involvement |
|---|---|---|---|
| **Normalize problem** | Schema extraction | Project Profile | None unless ambiguity materially affects risk |
| **Classify solution maturity** | Deterministic rules | Experiment/PoC/MVP/Pilot/production-candidate target | User confirms |
| **Determine applicability** | Rules + authoritative retrieval | Constraint map | Governance/Security selectively |
| **Search for reusable capability** | Retrieval | Reuse candidates | Researcher if evidence uncertain |
| **Define quality attributes** | Structured interview/inference | Measurable quality scenarios | Relevant experts |
| **Establish architecture drivers** | Deterministic synthesis | Ranked drivers + hard constraints | Council |
| **Generate alternatives** | **Inference-heavy** | Two–three viable architectures | SA |
| **Eliminate invalid options** | Deterministic | Feasible set | Domain experts can block |
| **Evaluate trade-offs** | Calculation + inference | Decision matrix | Council |
| **Resolve cross-domain conflict** | **Inference-heavy** | Preferred option + dissent | SA chairs |
| **Human architecture approval** | Human decision | Approved architecture baseline | User |
| **Compile Architecture Contract** | Deterministic generation | C4, ADRs, APIs, rules, budget, tests | SA |
| **Generate swarm plan** | Structured | Tasks + dependencies + guardrails | Coding orchestration |
| **Monitor implementation drift** | Deterministic | Pass/warn/fail events | Council only on exceptions |
| **Resolve unforeseen issue** | Bounded autonomy | Patch/revised plan/ADR | Relevant expert if threshold crossed |
| **Reassess architecture** | Event driven | Updated ADR/model | Council + user for material change |
| **Production-candidate assessment** | Checklist/evidence | Readiness dossier | Human experts ultimately assess |
 
This minimizes expensive multi-agent “discussion.” Most Council members should **not** be invoked on most decisions.
 
### Route experts using triggers
 
Examples:
 
| Trigger | Consult |
|---|---|
| New public endpoint, trust boundary, authentication, secret, external integration | Security Architect |
| New persistent data store/schema/data movement | Data Engineer |
| Statistical model/metric/analytical inference | Data Analyst |
| Personal information, records, AI policy, retention, procurement/governance | Governance Guru |
| Public/staff user interaction or channel/accessibility implication | UX Designer |
| Factual uncertainty materially affecting technology choice | Researcher |
| Interaction among two or more of the above | SA chairs |
 
A Council consultation should receive a **small structured dossier**:
 
```yaml
decision:
constraints:
proposed_option:
alternatives:
evidence:
assumptions:
questions_for_expert:
requested_response:
  - binding_constraint?
  - objection?
  - mitigation?
  - confidence?
```
 
That is considerably cheaper than passing the entire conversation history to every expert.
 
### Use hard, soft and advisory constraints
 
This gives disagreements semantics.
 
| Class | Meaning | Example response |
|---|---|---|
| **Hard** | Cannot proceed without satisfying it or explicit authorized risk acceptance | Block architecture |
| **Soft** | Strong preference that can be traded against another objective | Record trade-off in ADR |
| **Advisory** | Best-practice improvement | Implement if cost/complexity justified |
 
The SA can resolve soft-versus-soft disagreements.
 
It should **not** silently resolve hard-versus-preference disagreements.
 
### Give coding agents an autonomy envelope
 
A coding agent encountering an unforeseen problem should not need Council consultation for every library error. I suggest classifying deviations by their architectural significance.
 
| Change | Coding agent autonomy |
|---|---|
| Refactor with identical interfaces/behaviour | Proceed |
| Patch-level dependency substitution inside approved technology family | Proceed if automated checks pass |
| Small implementation technique change | Proceed and record |
| Interface contract modification | SA review |
| New package with meaningful privileges/network behaviour | Tool/dependency vetting; Security as triggered |
| New database/message broker/cloud service | SA + relevant expert |
| New public endpoint/trust boundary | Security + SA |
| Change affecting personal information/retention | Governance + Security/Data as applicable |
| Change to deployment region/vendor | SA + Governance/Security |
| Budget threshold exceeded | SA |
| Violates an approved ADR fitness function | Cannot self-waive |
| Requires waiving a hard constraint | Human escalation |
 
This is where your architecture fitness functions become the practical enforcement boundary for swarm autonomy.
 
### Make observability part of the architecture, not an implementation afterthought
 
OpenTelemetry is worth including at the architecture layer because it standardizes the telemetry concepts and tooling around traces, metrics and logs and provides a collector model with language/platform integrations. citeturn19view0 The SA need not dictate the final monitoring backend, but it should decide:
 
- what service boundaries require tracing;
- what business/technical metrics establish successful operation;
- what identifiers must propagate;
- what data must **not** enter telemetry;
- what SLOs and alerts correspond to the quality-attribute scenarios;
- what logs are necessary for audit/recovery;
- retention and cost assumptions.
The Security Architect can then layer ASD-specific logging/security requirements where applicable; ASD separately publishes practitioner guidance on prioritising log sources for SIEM/SOAR use. citeturn18search10
 
## Prioritized build plan
 
Trying to implement every capability above before the agent becomes useful would defeat your low-cost objective. I would build it in three layers.
 
### Foundation
 
These deliver most of the value and require little new infrastructure.
 
| Capability | Impact | Build effort | Incremental infrastructure | Recommendation |
|---|---:|---:|---:|---|
| Structured Project Profile | Very high | Low | Negligible | **Build first** |
| Applicability rules engine | Very high | Medium | Negligible | **Build first** |
| AGA + core government corpus | Very high | Medium | Very low | **Build first** |
| Source authority/freshness metadata | Very high | Medium | Very low | **Build first** |
| Postgres lexical + pgvector hybrid retrieval | Very high | Medium | Existing stack | **Build first** |
| Quality-attribute template | Very high | Low | None | **Build first** |
| Vendor-neutral architecture decision matrix | Very high | Medium | None | **Build first** |
| ADR/MADR workflow | Very high | Low | GitHub | **Build first** |
| C4 + Structurizr DSL | Very high | Medium | CLI/container only | **Build first** |
| Council routing triggers | Very high | Low–medium | LangGraph | **Build first** |
| Human approval gate | Critical | Low | Existing UI/workflow | **Build first** |
| Architecture Contract schema | Very high | Medium | GitHub | **Build first** |
| Basic architecture fitness runner | Very high | Medium | CI | **Build first** |
| Deterministic cost/capacity calculators | High | Low–medium | None | **Build first** |
| Live current-doc lookup | High | Low | Web access | **Build first** |
 
This is what I would call the **minimum viable Solution Architect**.
 
### High-value extensions
 
| Capability | Impact | Effort | Why next |
|---|---:|---:|---|
| OpenAPI contract generation/validation | High | Low | Makes service boundaries executable |
| AsyncAPI/CloudEvents support | Medium–high | Medium | Valuable once event-driven solutions appear |
| IaC introspection | Very high | Medium | Connects design to actual deployments |
| OPA/Conftest architecture policies | High | Medium | Turns repeated constraints into deterministic enforcement |
| Infracost adapter | High | Low–medium | Strong match for cost-sensitive architecture; current tooling supports CI and agent workflows. citeturn22view1 |
| OSS Tool/Dependency Registry | High | Medium | Prevents coding agents creating an uncontrolled technology estate |
| OpenSSF + OSV evaluation | High | Low | Good automated evidence for dependency/tool vetting. citeturn22view2turn22view3 |
| CycloneDX/SPDX SBOM | High | Medium | Gives a durable inventory and supply-chain artefact. citeturn23view0turn23view1 |
| OpenTelemetry architecture checks | High | Medium | Improves readiness of “prototype that suddenly became real” |
| Automated source freshness monitor | High | Medium | Particularly useful for Government material |
| Architecture-vs-repository drift detection | Very high | Medium–high | Important once autonomous coding becomes substantial |
| Empirical architecture experiments via Modal | High | Medium | Lets evidence replace architectural speculation |
| Architecture evaluation test suite | Very high | Medium | Needed before trusting genuine autonomous decisions |
 
### Later sophistication
 
| Capability | Value | Why defer |
|---|---|---|
| SLSA provenance enforcement | High at mature production stage | Useful, but your initial Council can gain more from basic SBOM/CI governance first. SLSA provides a sophisticated incremental provenance/security model when needed. citeturn23view2 |
| Architecture knowledge graph | Potentially high | A relational source graph is sufficient initially; demonstrate a graph-specific query need first |
| Automated architecture reconstruction from arbitrary code | High | Technically difficult; repo topology inspection plus declared architecture gives better early ROI |
| Full technology radar automation | Medium | Risks generating noise and novelty bias |
| Automatic benchmark laboratory | Medium–high | Add as repeated architecture decisions reveal the tests that actually matter |
| Separate vector database | Currently low | Your existing Postgres/pgvector + FTS architecture should be tested before another datastore is introduced. PostgreSQL already supplies native text-search capabilities. citeturn23view3 |
| Dedicated enterprise architecture platform | Currently low | Likely adds cost and process before you have demonstrated requirements that Git + structured Postgres + architecture-as-code cannot meet |
 
### Suggested architecture repository contract
 
I would ultimately have the Solution Architect produce something resembling:
 
```text
/architecture
    /profile
        project.yaml
        applicability.yaml
 
    /requirements
        architecture-drivers.yaml
        quality-attributes.yaml
        constraints.yaml
 
    /model
        workspace.dsl
        deployment.dsl
 
    /decisions
        ADR-001-....md
        ADR-002-....md
 
    /interfaces
        openapi/
        asyncapi/
        events/
        schemas/
 
    /governance
        policy-mappings.yaml
        records.yaml
        data-classification.yaml
 
    /cost
        assumptions.yaml
        budget.yaml
        estimates.json
 
    /operations
        slos.yaml
        recovery.yaml
        observability.yaml
 
    /fitness
        architecture-rules.yaml
        policies/
        tests/
 
    /supply-chain
        sbom/
        approved-tools.yaml
 
    /evidence
        experiments/
        benchmarks/
 
    /readiness
        checklist.yaml
        unresolved-risks.yaml
        dissent.yaml
```
 
That structure is deliberately **agent-friendly**: the Council has persistent machine-readable state, coding agents have explicit implementation contracts, humans can inspect the corresponding Markdown/diagrams, and CI can test much of it.
 
The actual architecture narrative can be generated as a compact **arc42-style architecture pack**, while C4/Structurizr maintains the underlying system model. arc42 is explicitly technology/process agnostic, while Structurizr can combine its C4 model with documentation and architecture decisions. citeturn13search1turn21view0
 
### The most valuable custom skills to build
 
Given your preference to avoid reinventing existing work, most of the *knowledge* above can be adopted from authoritative existing sources. The places where bespoke work is genuinely justified are the connective tissue:
 
| Custom skill | Why there is disproportionate value in building it |
|---|---|
| **`compile_project_profile`** | Gives every subsequent expert the same facts and eliminates repeated inference |
| **`resolve_applicable_architecture_sources`** | Converts a huge policy corpus into a small applicable set |
| **`find_government_reuse_candidate`** | Makes AGA reuse a behaviour rather than a document the agent happens to know about |
| **`create_quality_attribute_scenarios`** | Converts “fast/reliable/cheap/secure” into architecture requirements |
| **`compare_architecture_options`** | Provides consistent, explainable trade-off analysis |
| **`create_or_supersede_adr`** | Makes architectural reasoning durable |
| **`compile_architecture_contract`** | Bridges Council reasoning to coding-swarm instructions |
| **`derive_fitness_functions`** | Bridges prose architecture to deterministic CI enforcement |
| **`estimate_solution_cost`** | Keeps costs grounded in arithmetic/current pricing rather than model intuition |
| **`assess_architectural_change`** | Determines whether a coding-agent deviation can proceed or requires Council escalation |
| **`vet_new_technology`** | Combines functionality, license, maintenance, Scorecard, vulnerabilities, permissions, lock-in and alternatives |
| **`check_source_currency`** | Prevents the agent relying confidently on obsolete policy or technical guidance |
| **`prepare_council_dossier`** | Minimizes multi-agent token use by presenting specialists only the information relevant to their decision |
 
These custom skills are where I would spend engineering effort. C4, Structurizr, arc42, ADR/MADR, OpenAPI, AsyncAPI, OpenTelemetry, OPA, supply-chain standards, vendor architecture frameworks and most government policy knowledge have already been developed for you. citeturn13search0turn13search1turn15search27turn20view0turn20view1turn19view0turn21view2turn23view0
 
The unique intellectual property of your system should instead be **the decision machinery that composes those resources into an architecture and then makes the architecture enforceable**.
 
The resulting Solution Architect would therefore be much more than an LLM with an architecture library. It would have a repeatable chain:
 
**understand → classify → determine applicability → search for reuse → establish quality attributes → generate options → eliminate invalid choices → quantify trade-offs → consult specialists → record dissent → obtain human approval → compile architecture as code → enforce it during implementation → reopen decisions when evidence changes.**
 
That architecture matches the central problem your Council is intended to solve: when generating working software becomes extremely cheap, the scarce resource is no longer the ability to construct something. It is the ability to **know what should be constructed, why, under which constraints, and whether the thing that was ultimately constructed still satisfies the decision that was approved**.
