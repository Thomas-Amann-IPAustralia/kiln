# Proposal for the Governance Guru: Knowledge Base, Toolkit, and Operating Model
 
## Executive recommendation
 
The Governance Guru should not primarily be built as an encyclopedic “policy expert.” It should be built as **The Council’s obligation router, assurance coordinator, and evidence custodian**.
 
That distinction matters. In an Australian Government setting, a solution can simultaneously touch AI policy, administrative law, privacy, records management, procurement, accessibility, risk management, security, data governance, human rights, copyright, and agency-specific legislation. No single risk score or giant RAG corpus will reliably tell you whether all of those obligations have been considered. The stronger pattern is to have the Governance Guru determine *which regimes apply*, turn those regimes into explicit requirements, allocate them to the appropriate Council members, and continuously collect evidence that they were satisfied.
 
This is especially appropriate now because the Australian Government's current AI governance regime is explicitly lifecycle-oriented. The DTA's current Policy for the responsible use of AI in government is mandatory for non-corporate government departments and agencies from 15 December 2025 and establishes requirements around strategy, accountability, use-case registers and impact assessment. citeturn18view1 For every new AI use case, agencies must assess and document whether it meets the policy's in-scope criteria during design; in-scope uses then require an AI impact assessment, monitoring, and reassessment after material changes. citeturn21view0turn22search2
 
For your architecture, I would therefore define the agent approximately as follows:
 
> **Governance Guru:** Maintains the authoritative view of the obligations, principles, risks, approvals and evidence applicable to a proposed solution. It determines what governance work must occur, delegates specialist assessments to other Council members, challenges inadequate evidence, maintains traceability from obligation → decision → control → test → evidence, and assembles an auditable assurance case for human review. It provides legal and policy triage, but does not impersonate qualified legal counsel or provide the final human authority required for production deployment.
 
A key consequence is that I would **not** give it a single generic “risk assessment matrix” and let it infer everything from there. Different frameworks ask materially different questions: the DTA AI impact assessment governs AI-specific impact and inherent/residual risk; the OAIC privacy process assesses privacy impacts; the Commonwealth Risk Management Policy covers enterprise risk; administrative-law questions concern legal authority, discretion and procedural fairness; security risk belongs principally to the Security Architect. citeturn21view0turn18view8 Mandatory obligations should never disappear merely because an LLM calculated a low aggregate score.
 
The overall design I recommend is:
 
| Capability | Recommended implementation | LLM dependence |
|---|---|---:|
| Identify jurisdiction/entity/use-case characteristics | Typed intake questionnaire | Very low |
| Determine potentially applicable regimes | Deterministic rules + source metadata | Very low |
| Identify precise obligations | Rules first, retrieval second | Low–medium |
| Interpret ambiguous applicability | Retrieval + reasoned analysis | Medium |
| Conduct prescribed assessments | Reuse official tools/templates | Low |
| Obtain technical evidence | Structured requests to other Council agents | Low |
| Detect unresolved obligations | Database/query logic | Very low |
| Assess novel ethical trade-offs | Structured deliberation | Medium–high |
| Research unusual sector-specific requirements | Researcher/web retrieval | Medium |
| Draft governance documents | Author subagent grounded in evidence ledger | Medium |
| Approve production deployment | **Human decision, not agent** | N/A |
 
This approach closely matches the DTA's direction for agentic AI: responsibilities should be assigned between agents and humans, actions should be traceable in multi-agent systems, human oversight and intervention paths should be defined, and irreversible or high-risk actions should receive particular oversight. citeturn21view3
 
## What the Governance Guru should own
 
### A deliberately broad but shallow domain
 
The Governance Guru should have **breadth across regulatory and assurance domains, while other Council experts retain technical depth**.
 
For example, it needs to know enough about the PSPF to recognize that a solution involving classified information requires a security workstream, but it should not compete with the Security Architect on control design. Similarly, it should recognize that biased training data creates fairness, administrative-law and ethical concerns, while asking the Data Analyst to produce the actual cohort analysis.
 
I would divide responsibilities as follows.
 
| Governance area | Governance Guru's role | Primary collaborating expert |
|---|---|---|
| Applicable laws, policies, standards | **Own** applicability register and traceability | Researcher |
| AI governance / impact assessment | **Own** governance process | Solution Architect + all relevant experts |
| Ethics and public-interest impacts | **Own** cross-domain assessment | Whole Council |
| Administrative-law triage | **Own** identification/escalation | Researcher / eventual human lawyer |
| Privacy | **Own applicability/evidence status**; coordinate PIA | Security Architect + Data Engineer |
| Human rights / discrimination | **Own** impact checklist and escalation | UX + Data Analyst |
| Indigenous data / collective rights | **Own applicability and engagement trigger** | Researcher + human stakeholders |
| Cybersecurity | Verify that assessment/evidence exists; **do not own technical assessment** | Security Architect |
| Data governance / quality | Verify required controls/evidence | Data Engineer + Data Analyst |
| Accessibility / inclusion | Verify requirements and evidence | UX Designer |
| Records / FOI / transparency | **Own governance requirements** | Researcher + solution owner |
| Procurement / vendor governance | **Own compliance checklist** | Solution Architect |
| Intellectual property / OSS licensing | **Own legal/compliance flagging** | Coding swarm + Researcher |
| Operational monitoring | Define governance indicators and reviews | Solution Architect + domain experts |
| Evidence and auditability | **Own** | Entire Council |
| Exceptions / waivers / unresolved risks | **Own register and escalation** | Solution Architect as Chair |
| Final assurance documentation | **Own** | Author subagents |
 
The current DTA accountability standard strongly supports this kind of model. Accountable use-case owners are expected to ensure assessments occur, monitor the use case, revalidate it after change, and maintain records demonstrating transparency, traceability, auditability and explainability. citeturn21view2turn22search4
 
### The Governance Guru should not be “the lawyer”
 
I would give it strong **legal issue-spotting** capability, but explicitly prohibit conclusions such as:
 
> “This is definitely lawful.”
 
Instead, allow findings such as:
 
> “The proposed feature appears to materially influence an administrative decision involving discretion. The Commonwealth Ombudsman's Better Practice Guide identifies automation of discretionary decisions as an area requiring particular caution. Legal authority and the extent of permissible automation have not been established. **Human legal review is required before production deployment.**”
 
That is a particularly important boundary in government. The Commonwealth Ombudsman's updated automated decision-making guidance emphasizes legality, fairness, rationality, transparency, privacy and human rights, and says automated decision systems should not be used where they would contravene administrative law or other legal obligations. Its guidance is particularly cautious about automation of discretionary decision-making. citeturn2search1turn3view0
 
This is compatible with your stated risk model: the system can autonomously build a sophisticated prototype while producing a precise list of legal questions that a human expert must resolve before actual deployment.
 
## Recommended knowledge base
 
### Use an authority hierarchy rather than one undifferentiated vector store
 
I would build the Governance Guru's knowledge base as **two coupled systems**:
 
1. **A structured obligations/control registry** for deterministic reasoning.
2. **A searchable evidence corpus** containing authoritative source materials, guidance and examples.
The vector store should help answer *“what does the source say?”* It should not be the thing deciding *“which obligations apply?”*
 
A useful source hierarchy would be:
 
| Tier | Material | How it should be treated |
|---|---|---|
| **Authoritative law** | Acts, regulations, legislative/notifiable instruments | Highest authority; check status and commencement every time |
| **Mandatory government policy / standard** | DTA policies, PSPF requirements, CPRs, mandatory standards | Treat explicit requirements as rules |
| **Regulator / oversight guidance** | OAIC, Ombudsman, NAA, Finance, ANAO, AHRC | Strong interpretive/assurance material |
| **Agency / cross-government guidance** | DTA technical guidance, procurement tools, implementation guidance | Operational implementation knowledge |
| **Australian best practice** | AI Ethics Principles, assurance frameworks, Indigenous governance frameworks | Apply according to status/context |
| **International standards** | ISO, NIST, OECD, Canada, UK | Gap detection and assurance enhancement, not substitutes for Australian obligations |
| **Secondary legal sources** | AustLII discovery, commentary, scholarship | Discovery/context only; verify important claims against primary material |
 
The Federal Register of Legislation should be the canonical source for Commonwealth legislation because it is the authorized whole-of-government repository and tracks the lifecycle and relationships of Commonwealth laws. It also supports notifications of changes through registered user preferences. citeturn17search0turn17search1 AustLII is extremely useful as a free search/discovery layer across legislation and cases, but I would have the agent validate material legal propositions against an authorized or official source where available. citeturn17search2turn17search6
 
### Core Australian Government corpus
 
This would be my initial ingestion backlog, approximately in priority order.
 
| Knowledge family | Material to ingest/index | Why the Governance Guru needs it | Priority |
|---|---|---|---|
| **Australian Government AI policy** | Policy for responsible use of AI in government v2, appendices, Accountability Standard, Transparency Standard | Determines AI governance applicability, accountabilities, registers and assessment requirements | **Essential** |
| **Government AI Impact Assessment** | Tool, guidance and question structure | Do not invent an inferior home-grown assessment where a government one already exists | **Essential** |
| **AI Technical Standard** | Full public DTA material and individual lifecycle statements | Gives the Guru a concrete assurance checklist across design, data, training, evaluation, integration, deployment, monitoring and retirement | **Essential** |
| **Agentic AI Addendum** | All DTA agentic statements | Directly relevant to your multi-agent/swarm architecture | **Essential** |
| **AI PoC-to-scale guidance** | Guidance plus readiness, evaluation, procurement and Technical Standard mapping appendices | Your central problem is precisely the collapsing distinction between PoC and deployable system | **Essential** |
| **AI Ethics Principles** | Eight Australian AI Ethics Principles and implementation material | Baseline ethical vocabulary and impact categories | **Essential** |
| **Administrative decision-making** | Commonwealth Ombudsman ADM Better Practice Guide; future AGD reforms/guidance | Critical whenever software materially influences government decisions | **Essential** |
| **Privacy** | Privacy Act metadata/current compilation, APP Guidelines, Agencies Privacy Code, OAIC AI/privacy guidance | Personal information will be common in government solutions | **Essential** |
| **Privacy assessment** | OAIC threshold assessment and PIA tool/guidance | Gives you a ready-made deterministic branch: changed handling → screen → PIA where required | **Essential** |
| **Records management** | Archives Act references, NAA Information Management Standard and AI-specific records guidance | Agent actions, decisions and outputs can create Commonwealth records | **Essential** |
| **FOI / transparency** | FOI Act applicability references, IPS guidance, OAIC ADM reporting work | A system must be designed with discoverability and disclosure implications in mind | **High** |
| **Commonwealth risk** | Commonwealth Risk Management Policy and RMG-211 | Gives non-AI-specific risk governance context under PGPA arrangements | **High** |
| **PGPA** | PGPA Act / Rule references and Finance guidance | Resource management, accountability and internal-control context | **High** |
| **Procurement** | Current CPRs, Commonwealth Contracting Suite, ClauseBank, Supplier Code, DTA AI procurement guidance/model clauses | Vendor AI, SaaS, foundation models and external hosting create contractual governance dependencies | **High** |
| **Fraud/corruption/integrity** | Commonwealth Fraud and Corruption Control Framework, NACC-related procurement guidance | Government systems can introduce fraud, integrity and conflict risks beyond conventional cyber risk | **High** |
| **Protective security** | PSPF applicability and mandatory requirements, but not necessarily every technical implementation guide | Needed to route security obligations to Security Architect | **High** |
| **Digital Experience** | Digital Experience Policy, Digital Service Standard, Digital Inclusion Standard, relevant WCAG requirements | Public-facing systems must consider inclusion/accessibility | **High** |
| **Human rights** | AHRC Human Rights and Technology material plus AGD public-sector human-rights guidance | Provides rights-centred impact prompts and escalation criteria | **High** |
| **Anti-discrimination** | Relevant federal Acts, official guidance and sector overlays | AI error/bias can become unequal or discriminatory treatment | **High** |
| **Indigenous governance** | NIAA Framework for Governance of Indigenous Data; AIATSIS ethics resources; Maiam nayri Wingara principles | Government solutions involving First Nations peoples/data require collective and governance considerations not captured by ordinary individual privacy | **High** |
| **Data sharing** | Data Availability and Transparency Act/Scheme guidance and Dataplace processes | Relevant when Commonwealth datasets are combined or shared | Medium–high |
| **Copyright/IP** | Copyright Act source metadata, AGD copyright guidance, current Copyright and AI work | Relevant to training/grounding data, generated media, third-party code/content and licensing | Medium–high |
| **Cloud/digital investment** | Current Commonwealth cloud policy and relevant DTA architecture/investment policy | Allows applicability routing when solutions leave prototype infrastructure | Medium |
| **Agency/sector legislation** | Dynamically acquired rather than preloading everything | Health, welfare, taxation, immigration, employment, education etc. can radically alter obligations | **On demand** |
| **State/territory overlays** | Dynamically load appropriate jurisdiction packs | Avoid contaminating Commonwealth assessments with irrelevant state requirements | **On demand** |
 
The DTA's own current policy makes this breadth necessary. Its minimum in-scope criteria include potential for more than insignificant harm; material influence over administrative decisions; public interaction or significant impact without human review; use of personal, sensitive or security-classified information; or another elevated-risk designation. It specifically tells agencies to carefully consider areas such as employment, discretionary automated decision-making, justice and democratic processes, law enforcement/profiling/border control, health, education and critical infrastructure. citeturn22search0turn22search1
 
### Privacy, records and FOI deserve unusually strong representation
 
These should not be small subfolders in the knowledge base.
 
The OAIC requires Australian Government agencies to undertake a threshold assessment where a project involves new or changed handling of personal information; high-privacy-risk projects require a PIA under the Australian Government Agencies Privacy Code. The OAIC already provides a flexible PIA tool, so there is little reason to create your own from first principles. citeturn18view8turn18view9
 
Your Governance Guru should also be **effective-date aware**. For example, as at 2 October 2026, new APP 1 automated-decision transparency provisions are enacted but do not commence until **10 December 2026**. From that date, an APP entity meeting the statutory conditions must include prescribed information in its privacy policy when personal information is used by a computer program in connection with decisions that could reasonably be expected to significantly affect an individual's rights or interests. citeturn20search0turn20search3 A naïve RAG system could easily see that text and incorrectly describe it as already operative; your structured registry should distinguish `enacted`, `commencement_date`, `currently_in_force`, and `future_obligation`.
 
Records management is similarly important for your multi-agent architecture. National Archives states that AI-generated information created or received by Australian Government agencies is subject to the same Commonwealth-record obligations as other information. It does **not** require every prompt, chat or output to be retained; instead, agencies should take a risk-based approach based on business, legal, evidentiary and accountability value. NAA also specifically emphasizes records supporting decisions, relevant metadata, and documentation of technologies/processes where AI informs agency decision-making. citeturn18view10turn18view11
 
That lends itself neatly to an explicit records policy for The Council rather than simply enabling “log everything.”
 
### Indigenous data and collective rights need their own trigger
 
I would make this a first-class governance category, not bury it under ordinary privacy.
 
The Commonwealth's Framework for Governance of Indigenous Data is intended to give Aboriginal and Torres Strait Islander peoples greater agency over government-held data about them and supports the Closing the Gap priority reforms. citeturn15search8turn15search14 The Australian Indigenous Data Sovereignty principles developed by Maiam nayri Wingara emphasize Indigenous control over the data ecosystem, including creation, stewardship, analysis and dissemination. citeturn15search2turn15search6 AIATSIS's ethics framework similarly addresses meaningful engagement and Indigenous data sovereignty in relevant research contexts. citeturn15search4turn15search7
 
This is also no longer peripheral to mainstream government AI assessment: the DTA's current in-scope test expressly includes possible harm to the collective rights of cultural groups, including First Nations peoples. citeturn22search1
 
I would therefore give the intake process a deterministic trigger such as:
 
```text
Does the system collect, infer, link, classify, generate conclusions about,
or make decisions affecting Aboriginal or Torres Strait Islander peoples,
communities, Country, culture, knowledge or Indigenous data?
 
YES / POSSIBLY
→ Activate Indigenous Data Governance review
→ Notify Governance Guru + Researcher
→ Identify appropriate human/community engagement requirement
→ Do not treat individual consent/privacy compliance as sufficient by itself
```
 
### Human rights, equality and accessibility
 
The Australian AI Ethics Principles provide eight useful broad categories: human/social/environmental wellbeing, human-centred values, fairness, privacy/security, reliability/safety, transparency/explainability, contestability and accountability. citeturn7search3 I would map these principles to concrete evidence requirements rather than leave them as values in a prompt.
 
For public-facing digital services, the DTA's Digital Inclusion guidance directs agencies to design consistently with the Disability Discrimination Act, current government WCAG requirements and the Australian Government Style Manual. citeturn19search3 Current Australian Government web guidance references WCAG 2.2, and the Digital Experience Policy provides the broader mandatory framework for relevant government digital services. citeturn19search7turn19search15
 
The Australian Human Rights Commission's technology work is also valuable interpretive material because it explicitly addresses AI decision-making and accessible technology. citeturn19search2turn19search26
 
The Guru should therefore ask UX and Data experts questions that translate abstract fairness into evidence:
 
> “Which cohorts could receive materially different outcomes?”
 
> “Which accessibility requirements were tested and what was the result?”
 
> “What happens to a user who cannot use the digital channel?”
 
> “Can an affected person understand that AI influenced the outcome?”
 
> “Can they challenge an error?”
 
> “Did the Data Analyst test performance and error rates across relevant cohorts?”
 
That makes “ethics” operational.
 
### Procurement, IP and supplier governance
 
Procurement deserves more weight than it commonly receives in AI governance frameworks because your swarm will often prefer third-party models, APIs, packages and services rather than building everything itself.
 
The current Commonwealth Procurement Rules govern how relevant Commonwealth entities buy goods and services, while Finance provides supporting templates, guidance and a Commonwealth Contracting Suite. citeturn19search1turn19search13 The Commonwealth Supplier Code of Conduct is incorporated through Commonwealth contracting requirements and sets expectations relating to ethics, governance and business practices. citeturn19search17 Finance's ClauseBank is particularly valuable because it gives you **already-written government contracting language** rather than requiring an LLM to invent clauses. citeturn19search9
 
The DTA's AI-specific procurement guidance should be indexed alongside these resources. It covers issues including risk and assurance, privacy/security, transparency/explainability, staged contracting, interoperability and vendor dependency. citeturn1search1turn10search3
 
Copyright should be a flagged uncertainty area rather than an assumed solved problem. The Attorney-General's Department continues to run a dedicated Copyright and AI Reference Group examining AI inputs, outputs, licensing and transparency; the Government has stated that it is not pursuing a general text-and-data-mining exception. citeturn19search0turn19search4 That means the Governance Guru should flag training, fine-tuning, RAG ingestion, generated media and scraped content where rights status is unclear rather than confidently applying norms learned from US-centric material.
 
### International material as a gap detector
 
I would ingest a curated international layer, but keep it clearly labeled **non-normative for Australian compliance unless separately applicable**.
 
| External framework/tool | Value to the Guru | How I would use it |
|---|---|---|
| **NIST AI RMF** | Mature risk vocabulary across Govern/Map/Measure/Manage | Cross-check whether Australian assessment has missed a risk family |
| **NIST AI RMF Playbook** | Concrete suggested actions | Source of controls/questions, not Australian law |
| **Canada Algorithmic Impact Assessment** | Detailed questionnaire and impact-level approach | Secondary assessment for government decision systems |
| **UK Algorithmic Transparency Recording Standard** | Excellent disclosure structure plus real government examples | Basis for generating human-readable algorithmic transparency records |
| **OECD AI Principles** | International governance baseline | Ethics crosswalk |
| **OECD Catalogue of Tools & Metrics** | Discovery of assessment/evaluation tools | Tool-finding capability |
| **OECD AI Incidents and Hazards Monitor** | Real-world failure modes | Scenario generation and hazard research |
| **ISO/IEC 42001** | AI management-system structure | Optional organizational assurance crosswalk |
| **ISO/IEC 42005** | AI impact assessment standard | Optional gap analysis against impact methodology |
| **ISO/IEC 23894** | AI risk-management guidance | Cross-check risk-management practices |
| **UNESCO Recommendation on AI Ethics** | Broad societal/ethical impact framework | Novel ethical issues and international projects |
| **EU AI Act** | Material where an EU nexus exists; otherwise useful comparison | Trigger only when jurisdictionally relevant |
 
NIST's AI RMF ecosystem includes both the framework and a Playbook of suggested actions, and its resource center provides crosswalks and other implementation material. citeturn8search0turn8search12turn8search16 Canada's Algorithmic Impact Assessment is particularly reusable because it is a structured questionnaire used under the Canadian government's Directive on Automated Decision-Making. citeturn8search5turn8search9 The UK's ATRS provides both a standardized transparency record and a corpus of published examples, making it useful training material for your Author agents. citeturn8search6turn8search10turn8search22
 
The OECD's tools catalogue and incident/hazard monitor would be excellent **live search targets** rather than material you periodically stuff wholesale into pgvector. citeturn8search19turn8search7
 
ISO/IEC 42001, 23894 and the newer 42005 cover AI management systems, risk management and AI impact assessment respectively. citeturn9search0turn9search1turn9search19 Because most ISO standards are copyrighted/licensed materials, I would store bibliographic metadata and your own mappings unless you obtain a license allowing fuller internal ingestion.
 
## Recommended toolkit
 
### Reuse official assessment tools before creating new ones
 
Your instinct toward deterministic processes is very good. In fact, a large proportion of the Governance Guru can be deterministic because government already provides checklists, templates, standards and prescribed fields.
 
The following would be my initial toolkit.
 
| Tool / skill | Build or reuse? | What it does in The Council | Recommendation |
|---|---|---|---|
| **DTA AI in-scope classifier** | Build rules from official criteria | Determines whether an AI use case triggers government AI-policy assessment | **Core** |
| **DTA AI Impact Assessment Tool** | **Reuse/integrate** | AI impact/risk assessment | **Core** |
| **AI use-case register** | Implement DTA fields in Postgres | Persistent inventory of AI solutions and accountability | **Core** |
| **DTA Technical Standard conformance checker** | Build structured checklist | Maps architecture/build evidence to lifecycle statements | **Core** |
| **DTA Agentic AI Addendum checker** | Build structured checklist | Additional assurance for multi-agent systems | **Core for your platform** |
| **OAIC privacy threshold assessment** | Reuse official logic/template | Determines whether deeper PIA required | **Core** |
| **OAIC PIA workflow** | Reuse/adapt official tool | Structured privacy assessment | **Core** |
| **Ombudsman ADM checker** | Convert guide into structured checklist | Identifies administrative-law/decision-system hazards | **Core** |
| **Obligation applicability engine** | Build | Determines policies/laws/frameworks activated by context | **Core** |
| **Obligation–Control–Evidence Matrix** | Build | Central assurance data structure | **Core** |
| **Commonwealth risk workflow** | Adapt Finance framework | Non-AI enterprise/project risks | High |
| **Records-retention classifier** | Build from NAA guidance + agency authorities | Determines what Council/build artifacts need capture | High |
| **FOI/transparency readiness check** | Build | Flags discoverability/publication/transparency requirements | High |
| **Human-rights/equality checklist** | Build from official sources | Rights and discriminatory-impact triage | High |
| **Indigenous data trigger/checklist** | Build from NIAA/AIATSIS/MnW material | Identifies collective governance/engagement issues | High |
| **Digital Experience/accessibility gate** | Adapt DTA criteria | Ensures UX has supplied accessibility/inclusion evidence | High |
| **Procurement applicability checker** | Build | Determines procurement policy/contract requirements | High |
| **Finance ClauseBank retriever** | Retrieval skill | Surfaces existing government clauses rather than drafting blindly | High |
| **AI vendor due-diligence questionnaire** | Adapt DTA PoC/procurement resources | Collects information needed for privacy, security, data, IP, monitoring, lock-in | High |
| **Open-source/IP inventory** | Tool-assisted | Identifies software/license obligations | Medium–high |
| **NIST RMF crosswalk** | Build once | Finds governance gaps after Australian requirements | Medium |
| **Canada AIA cross-check** | Reuse questions | Additional scrutiny for consequential ADM | Medium |
| **UK ATRS generator** | Adapt template | Creates public-facing transparency record | Medium |
| **OECD tool finder** | Search integration | Finds specialized metrics/tools for unusual risks | Medium |
| **OECD incident search** | Live retrieval | Generates known-failure scenarios relevant to proposed system | Medium |
| **Policy-as-code engine** | Optional | Executes expanding deterministic applicability/control rules | Later |
| **Assurance-case generator** | Build | Turns evidence ledger into final human-review document | **Core** |
| **Governance diff / change monitor** | Build | Detects changes in authoritative sources | **Core** |
| **Exception/waiver workflow** | Build | Prevents unresolved requirements disappearing from context | **Core** |
 
The DTA expressly permits agencies to use its AI impact tool or an internal process that integrates **all** its provisions and produces the same or higher risk outcomes; integrated processes also need to track updates to the official tool. citeturn21view0 That is almost an instruction to build exactly the sort of machine-readable implementation you are contemplating.
 
### The AI Impact Assessment should become a root workflow
 
I would not make “risk matrix” the Guru's top-level assessment.
 
Instead:
 
```text
Context intake
    ↓
Applicability rules
    ├── DTA AI policy → AI Impact Assessment
    ├── Personal information → OAIC threshold → possible PIA
    ├── Administrative decision → Ombudsman ADM assessment
    ├── Security-sensitive → Security Architect assessment
    ├── Public digital service → Digital Experience / accessibility
    ├── Indigenous data/impact → Indigenous governance workstream
    ├── Procurement/vendor → procurement/vendor assurance
    ├── Commonwealth records → records plan
    └── Sector/jurisdiction triggers → Researcher performs targeted discovery
```
 
This is much safer than:
 
```text
LLM considers everything
    ↓
Risk = 7.4/10
```
 
The current DTA impact-assessment model itself distinguishes inherent risk, mitigations and residual risk and requires high-risk uses to receive stronger governance and at least annual review after deployment. citeturn21view0
 
### Build an Obligation–Control–Evidence Matrix
 
I think this should be the **central artifact of the Governance Guru**.
 
Every applicable requirement becomes a row, not merely text in an assessment report.
 
For example:
 
| Field | Example |
|---|---|
| `obligation_id` | `DTA-AI-ACCOUNTABILITY-REGISTER-01` |
| Source | DTA Standard for Accountability |
| Authority | Mandatory policy |
| Jurisdiction | Commonwealth |
| Applies because | NCE + in-scope AI use case |
| Requirement | Use case recorded in internal register |
| Owner | Governance Guru |
| Contributor | Solution Architect |
| Control | Register-writing workflow |
| Evidence required | Persisted register row |
| Evidence location | `governance://use_cases/UC-0081` |
| Status | Satisfied |
| Verified by | deterministic schema check |
| Source version | hash/version/date |
| Decision date | timestamp |
| Revalidation trigger | material use-case change |
| Confidence | 1.0 |
| Human review | Not required for this row |
| Notes | — |
 
The DTA already specifies minimum use-case-register information including description, technology type, lifecycle stage, domain, usage pattern, accountable owner, in-scope criteria, inherent/residual risk and assessment dates, with additional review data for high-risk systems. citeturn21view2turn22search4 Your internal schema can simply be a superset.
 
The same structure can represent softer requirements:
 
| Obligation | Status |
|---|---|
| “Assess disproportionate effects on vulnerable users” | `evidence_required` |
| Data Analyst cohort-testing report | `received` |
| UX consultation evidence | `received` |
| Residual concern | `medium` |
| Governance conclusion | `satisfied_with_condition` |
| Condition | monitoring at 30/90 days |
| Human acceptance needed | `yes` |
 
This gives you something much more valuable than a PDF: **machine-verifiable governance state** from which PDFs can be generated.
 
### Add a policy-as-code layer, but not immediately
 
For the first version, ordinary typed Python rules or JSON-based decision tables stored in GitHub are sufficient. That gives you:
 
- straightforward unit tests;
- easy code review;
- version history;
- deterministic execution;
- no extra infrastructure;
- direct integration into LangGraph.
As the rule base grows, **Open Policy Agent/Rego** becomes worth considering. OPA is an open-source general-purpose policy engine using declarative Rego policies and is designed to separate policy decisions from application logic. citeturn16search0turn16search6 It can also evaluate infrastructure and CI/CD policies, which might ultimately let The Council enforce governance decisions automatically at build or deployment time. citeturn16search24
 
I would not introduce OPA on day one. Your first several dozen applicability rules will probably be easier to understand, test and maintain in a typed internal rules package. Introduce a policy engine when **policy maintenance**, rather than LLM inference, becomes the bottleneck.
 
### Software licensing/IP scan
 
A Governance Guru need not run every development check, but it should be able to require an artifact from the coding swarm.
 
One useful zero/low-cost option is ScanCode Toolkit. Its tooling detects licenses, copyright and package information in source trees and package manifests. citeturn16search2turn16search11
 
The interaction could simply be:
 
```text
Governance Guru:
"Release gate requires software-composition/IP evidence."
 
Coding swarm:
→ runs license/package scan
→ writes structured JSON artifact
 
Governance Guru:
→ checks forbidden/unknown-license conditions
→ unresolved licenses → Researcher/legal review
→ records evidence hash in assurance ledger
```
 
That is a good example of the Guru **governing a test rather than performing all expert work itself**.
 
## Operating model inside The Council
 
### Start every project with a governance intake
 
The intake should be mostly deterministic. It should establish facts that later rules can consume.
 
I would capture at least:
 
| Category | Example questions |
|---|---|
| Jurisdiction | Commonwealth, state/territory, multi-jurisdictional, other? |
| Entity | NCE, CCE, contractor, hypothetical agency, public/private? |
| Purpose | What government/business function is affected? |
| Users | Staff, public, businesses, vulnerable groups, children? |
| Decisions | Does the solution make/recommend/materially influence decisions? |
| Discretion | Does any decision involve judgment or statutory discretion? |
| Consequence | Could an error affect rights, benefits, employment, liberty, safety, finances or access to a service? |
| Human review | Is output reviewed before affecting anyone? By whom? |
| AI | Which AI/ML/LLM/agent components are involved? |
| Autonomy | Can agents call tools, write data, transact, publish, notify or alter systems? |
| Reversibility | Which actions cannot readily be undone? |
| Data | Personal, sensitive, classified, commercial, health, Indigenous, linked data? |
| Data location | Local, SaaS, offshore processing/storage? |
| Public interaction | Does the public converse with or receive generated output directly? |
| Procurement | Existing contract, new vendor, API, SaaS, OSS? |
| IP | Third-party source material, model training/fine-tuning, generated content? |
| Records | Will it contribute to decisions or official government business? |
| Accessibility | Is there a citizen-facing or employee-facing interface? |
| Sector | Health, welfare, tax, employment, education, border, law enforcement, etc.? |
| Deployment | experiment, PoC, pilot, production-like prototype, production? |
 
The DTA's current policy intentionally captures many apparently innocuous systems once harm, administrative decisions, public impact, protected data or other elevated risks are present. citeturn22search1 The Technical Standard is also explicitly intended to help early experiments, PoCs and pilots establish a pathway toward responsible production use rather than treating governance as something that begins after the prototype. citeturn22search9
 
That aligns extraordinarily well with your premise that “prototype” and “deployable software” have converged.
 
### Use explicit governance gates
 
I would define these gates in LangGraph.
 
| Gate | Governance Guru must establish | Permitted outcome |
|---|---|---|
| **Problem framing** | Jurisdiction, users, consequences, preliminary obligations | Continue / research / stop |
| **Concept** | Applicable governance regimes, prohibited/critical issues, initial risks | Council design may proceed |
| **Design** | Required assessments initiated; owners and evidence requirements allocated | Human approves proposed design |
| **Build** | Coding swarm receives governance constraints as machine-readable requirements | Development proceeds |
| **Integration** | Required tests/evidence collected; deviations reconciled | Candidate release |
| **Pre-deployment assurance** | All mandatory rows satisfied or explicitly escalated; residual risks identified | Human review package |
| **Operation** | Monitoring, incident, revalidation, records and change rules defined | Controlled operation |
| **Material change** | Applicability/impact assessment rerun | Continue / reapprove |
| **Retirement** | Data, records, access, vendor, model and transparency obligations closed | Decommission |
 
The DTA explicitly requires in-scope AI assessments to start during design and be finalized before deployment, with reassessment after material changes including potentially vendor or regulatory changes. citeturn21view0 That makes `material_change` a natural LangGraph transition rather than merely a paragraph in policy documentation.
 
### Deterministic escalation triggers
 
Do not ask the LLM to decide from scratch whether something is “serious enough” to escalate.
 
Define hard triggers. For example:
 
| Trigger | Mandatory action |
|---|---|
| Potential DTA high-risk use case | Solution Architect + human accountable reviewer |
| Administrative decision involving discretion | Legal-review flag |
| Legal authority for automated action unclear | Legal-review flag |
| Irreversible external action | Human approval checkpoint |
| Personal information + changed handling | OAIC threshold assessment |
| High privacy risk | Full PIA |
| Classified information | Security Architect; block unsupported infrastructure |
| Significant public impact without human review | Enhanced AI assessment |
| Health/safety/law enforcement/border/justice | Enhanced domain research |
| Bias/fairness concern affecting protected/vulnerable cohort | Data Analyst + UX + Governance |
| First Nations data or collective impact | Indigenous governance workstream |
| Material vendor/model update | Revalidate relevant assessments |
| Unknown software/content licence | IP/legal flag |
| Required evidence missing at deployment gate | Deployment gate fails |
| Experts disagree on mandatory obligation | Council Chair |
| Expert disagreement could materially affect rights/safety/lawfulness | Chair + human-review flag |
 
The DTA Agentic AI Addendum is particularly supportive of deterministic autonomy boundaries: it calls for human oversight models, real-time monitoring, human review at key stages, intervention for irreversible/high-risk actions and documented escalation pathways. citeturn21view3
 
### A formal disagreement packet for the Council Chair
 
When experts disagree, do not simply put them back into a conversational loop until one “wins.”
 
Have the Governance Guru construct:
 
```yaml
decision:
  id: DEC-0042
  question: "May the agent autonomously reject this class of application?"
  decision_needed_by: "Design Gate"
 
options:
  - id: A
    description: "AI recommends; human decides"
  - id: B
    description: "AI makes determination automatically"
 
positions:
  governance_guru:
    preferred: A
    evidence: [...]
  solution_architect:
    preferred: B
    evidence: [...]
  security_architect:
    preferred: A
    evidence: [...]
 
constraints:
  mandatory: [...]
  unresolved_legal_questions: [...]
  reversibility: low
  affected_parties: [...]
 
risk_delta:
  A: [...]
  B: [...]
 
governance_recommendation: A
dissent_preserved: true
human_review_required: true
```
 
The Solution Architect then receives a **decision problem**, rather than pages of agent chat.
 
Do not retain private model chain-of-thought as your assurance record. Retain source citations, relevant inputs, tool actions, concise reasons, alternative options, decisions, dissent and approvals. That gives you auditability without turning hidden reasoning into an uncontrolled information asset. The DTA requires traceability and auditable records for agentic systems, while NAA specifically recommends preservation of appropriate decision records and contextual metadata where AI contributes to government decision-making. citeturn21view3turn18view10
 
### Give coding agents machine-readable governance constraints
 
The Governance Guru should output more than prose to the coding swarm.
 
For example:
 
```json
{
  "constraint_id": "GOV-PRIV-014",
  "title": "No production personal data in prototype telemetry",
  "severity": "blocking",
  "owner": "governance_guru",
  "applies_to": ["api", "observability", "llm_prompts"],
  "verification": {
    "type": "evidence_required",
    "requested_from": "security_architect",
    "artifact": "telemetry-data-flow-review"
  },
  "reopen_on": [
    "telemetry_provider_changed",
    "new_personal_data_field",
    "logging_configuration_changed"
  ]
}
```
 
A swarm agent encountering a conflict can then determine deterministically:
 
```text
Can I solve this without violating any blocking governance constraint?
    YES → proceed within autonomy budget
    NO / UNKNOWN → identify constraint owner → escalate
```
 
That is considerably more robust than putting the final Council report into every coder's context window.
 
## Search, retrieval, and evidence architecture
 
### Give the Guru a source registry before giving it broad web search
 
I would maintain a structured `governance_sources` table containing:
 
```text
source_id
title
issuing_authority
jurisdiction
source_type
authority_level
canonical_location
status
published_date
effective_from
effective_to
next_known_commencement
supersedes
superseded_by
last_checked
content_hash
ingestion_version
licence/reuse_status
retrieval_policy
```
 
That solves several problems RAG cannot solve elegantly:
 
- whether a rule is actually in force;
- whether a document was superseded;
- whether something is mandatory or guidance;
- whether the source is Commonwealth or state;
- whether a later version should override an older embedding;
- whether a future commencement needs an alert.
The Privacy Act example demonstrates why this matters: the Federal Register can contain an in-force compilation while also noting amendments that have been enacted but have not commenced, and OAIC guidance already describes the 10 December 2026 ADM changes. citeturn20search2turn20search0
 
### A sensible retrieval order
 
For a governance question, I suggest:
 
```text
1. Resolve context
   entity + jurisdiction + domain + lifecycle stage + date
 
2. Query structured applicability registry
   ↓
   candidate obligations
 
3. Retrieve authoritative supporting passages
   metadata filters first:
       jurisdiction
       issuing body
       authority class
       effective date
       current/superseded
 
4. Hybrid retrieval
   lexical + pgvector
 
5. Rerank only the small candidate set
 
6. If evidence insufficient:
   authoritative-domain search
 
7. If novel legal issue:
   Researcher conducts legal-source discovery
 
8. Important proposition:
   verify against primary source
 
9. Persist citation + source version with conclusion
```
 
This is a very good fit for Neon/Postgres because applicability metadata, relational mappings and pgvector can remain in the same datastore.
 
### Search allowlist
 
The Governance Guru should prefer these public domains before generalized search:
 
| Domain family | Purpose |
|---|---|
| `legislation.gov.au` | Authoritative Commonwealth legislation |
| `digital.gov.au`, Australian Government Architecture | AI/digital policy and standards |
| `oaic.gov.au` | Privacy and FOI |
| `ombudsman.gov.au` | Administrative law / decision systems |
| `finance.gov.au` | PGPA, risk, procurement, fraud, contract material |
| `protectivesecurity.gov.au` | PSPF |
| `cyber.gov.au` | Cyber guidance, principally delegated to Security Architect |
| `naa.gov.au` | Archives/records |
| `ag.gov.au` | Administrative law reform, human rights guidance, copyright |
| `humanrights.gov.au` | Human rights/equality guidance |
| `anao.gov.au` | Real audit findings and governance lessons |
| `niaa.gov.au` | Indigenous data governance / relevant Commonwealth policy |
| `aiatsis.gov.au` | Indigenous ethics/research guidance |
| `austlii.edu.au` | Legal discovery/case research, followed by verification |
| Official state/territory legislation sites | Activated by jurisdiction |
| `nist.gov` | International AI risk cross-check |
| OECD official AI resources | Tools, incidents, principles |
| Official UK/Canada government sites | Comparative public-sector governance |
| `iso.org` | Standards metadata, licensed material where available |
 
The ANAO corpus is especially valuable because it tells the Guru what auditors actually criticize rather than merely what frameworks say in theory. Recent Commonwealth audits have examined AI governance issues such as inventory, roles, lifecycle processes, assurance, monitoring and benefits realization. citeturn2search2turn2search6 That makes ANAO findings excellent retrieval material for an “auditor challenge” subroutine.
 
### Change detection should be a first-class tool
 
This is one capability I would build early.
 
A cheap scheduled process can:
 
1. fetch the canonical sources;
2. honor ordinary HTTP cache metadata where available;
3. calculate a normalized content hash;
4. detect changed pages/documents;
5. identify the changed section;
6. open a governance source-update task;
7. ask the Researcher/Governance Guru to determine whether rules are affected;
8. run unit tests against changed rules;
9. re-embed only changed content;
10. mark affected projects for revalidation.
The need is explicit in the current DTA regime: accountable officials are expected to stay current as AI policy evolves, and deployed use cases should be reassessed after relevant regulatory or vendor changes. citeturn21view0turn22search4
 
For critical legislation, you could additionally subscribe a maintained account to Federal Register notifications. The Register supports email notifications for changes to Commonwealth law according to user preferences. citeturn17search1
 
### Search sector-specific obligations dynamically
 
Do **not** attempt to ingest every Australian law into the Governance Guru.
 
Instead, have rules activate research questions such as:
 
```text
Sector = aged care
Jurisdiction = Commonwealth
Decision consequence = eligibility/access to service
AI = recommendation influences human decision
 
→ Search:
   administering legislation
   delegated legislation
   regulator standards
   agency-specific policy
   review/appeal rights
   mandatory notices
   privacy overlays
   records requirements
   relevant Ombudsman/tribunal/court decisions
```
 
This is where your **Researcher** becomes an important companion agent. Governance should formulate a precise research commission; Researcher finds and verifies sources; Governance turns the findings into obligations.
 
That limits your core knowledge base while still allowing extremely broad project coverage.
 
## Governance artifacts and Author subagents
 
Your proposed `Author` child agents are an excellent fit, but I would keep them **stateless and evidence-bound**. They should not decide whether compliance exists. They should write from the Governance Guru's structured assurance state.
 
### Artifacts across the lifecycle
 
| Lifecycle | Governance artifact | Main producer |
|---|---|---|
| Intake | Context and jurisdiction record | Governance Guru |
| Intake | Applicable-regimes matrix | Governance Guru |
| Concept | Governance applicability memo | Author |
| Concept | Initial risk/issues register | Governance Guru |
| Design | AI in-scope assessment | Governance Guru |
| Design | AI Impact Assessment | Governance Guru + Council evidence |
| Design | Privacy threshold / PIA | Governance + specialists |
| Design | ADM/legal issue assessment | Governance Guru |
| Design | Ethical/human-rights impact assessment | Governance Guru |
| Design | Indigenous governance assessment, where triggered | Governance + Researcher |
| Design | Assurance plan | Governance Guru |
| Build | Obligation–Control–Evidence Matrix | Governance Guru |
| Build | Decision/dissent register | Governance Guru |
| Build | Governance constraints manifest | Governance Guru |
| Build | Exceptions and deviations log | Governance Guru |
| Build | Supplier assurance record | Governance + Solution Architect |
| Build | Records-management plan | Governance Guru |
| Pre-release | Technical Standard conformance report | Author from Council evidence |
| Pre-release | Agentic AI conformance report | Author |
| Pre-release | Accessibility/inclusion assurance | UX → Author |
| Pre-release | Security assurance summary | Security → Author |
| Pre-release | Data-quality/fairness assurance | Data experts → Author |
| Pre-release | Residual-risk register | Governance Guru |
| Pre-release | Unresolved human-review items | Governance Guru |
| Pre-release | Deployment readiness recommendation | Governance Guru |
| Release | AI use-case register entry | Governance Guru |
| Release | Transparency material | Author |
| Operation | Monitoring/review schedule | Governance Guru |
| Change | Revalidation record | Governance Guru |
| Retirement | Decommission/records closure report | Author |
| Final | **Consolidated Assurance Case** | Author |
 
DTA's PoC-to-scale guidance already supplies reusable readiness, evaluation, procurement and technical-standard mapping material, so several of these artifacts can be seeded from existing government work instead of designed from zero. citeturn21view4
 
### The final product should be an assurance case, not a “compliance certificate”
 
I would avoid having the system announce:
 
> **COMPLIANT**
 
Instead produce:
 
> **Assurance conclusion: Suitable for expert pre-production review, subject to the following unresolved items and assumptions.**
 
Then structure the document around **claim → supporting control → evidence → exceptions → human decision**.
 
For example:
 
| Claim | Evidence | Confidence/status |
|---|---|---|
| Applicable AI governance regimes were identified | Intake v4 + applicability rule execution log | Satisfied |
| DTA AI impact process completed | Impact assessment artifact | Satisfied |
| Privacy impacts assessed | OAIC threshold + PIA | Satisfied |
| Administrative-law authority confirmed | No legal opinion supplied | **Unresolved — human legal review** |
| Security controls appropriate | Security Architect assessment `SEC-19` | Satisfied for prototype |
| Accessibility requirements met | UX test report | Satisfied with exception |
| Remaining accessibility exception | Keyboard workflow defect | **Must remediate before deployment** |
| Agent actions are auditable | trace/evidence tests | Satisfied |
| Human intervention works | kill/approval-path test | Satisfied |
| Model vendor update process exists | vendor-monitoring control | Satisfied |
| Production data retention is lawful | agency records authority not supplied | **Human validation required** |
 
That is much more defensible to a future privacy officer, lawyer, executive, auditor or security assessor because it makes clear **what the agents established and what they did not**.
 
### Suggested Author specializations
 
Rather than one generic Author, I would allow the Guru to instantiate very cheap temporary roles:
 
| Author subagent | Output |
|---|---|
| **Assurance Case Author** | Overall release dossier |
| **Impact Assessment Author** | Human-readable AI/ethics assessment from structured answers |
| **Privacy Author** | PIA draft from evidence |
| **Transparency Author** | AI/public transparency language |
| **Decision Record Author** | Concise Council decision record |
| **Audit Pack Author** | Evidence index for external reviewer |
| **Executive Brief Author** | Two-page risks/decisions briefing |
| **Operations Governance Author** | Monitoring, review and incident plan |
 
These agents should be prohibited from creating unsupported claims. Every substantive statement should resolve to an evidence ID or authoritative citation.
 
The UK Algorithmic Transparency Recording Standard is particularly useful inspiration for the Transparency Author because it is specifically designed to standardize public-sector disclosures about why and how algorithmic tools are used, and the UK publishes completed records that can act as examples. citeturn8search6turn8search22
 
## Implementation in your proposed stack
 
The good news is that I do **not** think the Governance Guru requires another major infrastructure product. Your proposed stack is already well suited to it.
 
### Suggested component mapping
 
| Existing component | Governance use |
|---|---|
| **LangGraph OSS** | Governance state machine, gates, escalation and Council requests |
| **Neon Postgres** | Source registry, obligations, controls, evidence metadata, decisions, assessments, exceptions |
| **pgvector** | Semantic retrieval over authoritative governance corpus |
| **Cloudflare R2** | Immutable-ish source snapshots, reports, evidence files, assessment artifacts |
| **GitHub** | Version-controlled rules, schemas, source manifests, assessment templates and governance-as-code |
| **Langfuse** | Agent/tool observability and evaluation telemetry |
| **Modal Sandboxes** | Isolated document transformation, tests, scanners where appropriate |
| **Oracle VM** | Local reranker/embedding or document-processing workload if required |
| **Railway** | Main orchestration/API service |
| **Tailscale** | Private connectivity to your heavier local services |
| **Coding swarm** | Generates machine-readable evidence under Guru requests |
 
### Proposed data model
 
I would create something conceptually like:
 
```text
governance_project
governance_context
source
source_version
obligation
applicability_rule
project_obligation
control
evidence_requirement
evidence_artifact
assessment
assessment_answer
risk
treatment
decision
decision_position
exception
human_review_requirement
use_case_register
monitoring_requirement
change_event
release_gate
```
 
The central relationship is:
 
```text
SOURCE
  ↓ supports
OBLIGATION
  ↓ applies-to
PROJECT
  ↓ implemented-by
CONTROL
  ↓ verified-by
EVIDENCE
  ↓ assessed-at
GATE
```
 
That is the ontology I would optimize the entire agent around.
 
### Example applicability rule
 
Initially, I would keep these rules straightforward:
 
```python
if (
    project.entity.is_non_corporate_commonwealth_entity
    and project.uses_ai
):
    require("DTA_AI_POLICY_SCOPE_ASSESSMENT")
 
if project.ai_can_cause_more_than_insignificant_harm:
    require("DTA_AI_IMPACT_ASSESSMENT")
 
if project.ai_materially_influences_administrative_decision:
    require("DTA_AI_IMPACT_ASSESSMENT")
    require("ADM_BETTER_PRACTICE_ASSESSMENT")
 
if project.handles_personal_information_in_new_or_changed_way:
    require("OAIC_PRIVACY_THRESHOLD_ASSESSMENT")
 
if project.privacy_threshold_potential_high_risk:
    require("OAIC_PIA")
 
if project.affects_first_nations_collective_rights_or_data:
    require("INDIGENOUS_DATA_GOVERNANCE_ASSESSMENT")
 
if project.public_digital_service:
    require("DIGITAL_EXPERIENCE_ASSESSMENT")
    request_evidence("ux_designer", "ACCESSIBILITY")
 
if project.uses_security_classified_information:
    escalate("security_architect")
```
 
Those first AI conditions directly mirror the current DTA scope criteria rather than asking the LLM to reinvent policy interpretation. citeturn22search1 The privacy branch similarly mirrors the OAIC's existing threshold → possible PIA structure. citeturn18view8
 
Then let an LLM handle the genuinely ambiguous part:
 
> “The user says this agent ‘prioritizes’ applications but a human technically clicks approve. Does that materially influence the administrative decision?”
 
That is where inference adds value.
 
### Separate evidence from observability logs
 
I would **not** use Langfuse traces themselves as your governance record.
 
Instead:
 
- Langfuse = technical observability;
- Postgres = authoritative governance state;
- R2 = evidence/source artifacts;
- Git = policy/rule history.
A governance evidence row may reference a Langfuse trace, but the trace should not silently become the permanent record simply because it exists.
 
That approach is consistent with NAA's risk-based position: not every AI prompt/output/log must be preserved, but information needed for business, legal, evidentiary and accountability purposes should be identified and appropriately managed. citeturn18view10
 
### Provenance on every meaningful governance claim
 
For each generated conclusion, store something like:
 
```json
{
  "claim": "A privacy impact assessment is required.",
  "classification": "mandatory",
  "basis": [
    {
      "source_id": "OAIC_AGENCY_PRIVACY_CODE_PIA",
      "source_version": "2026-09-...",
      "passage_id": "p-0188"
    }
  ],
  "facts": [
    "system handles personal information",
    "handling method is new",
    "threshold assessment indicates potential high privacy risk"
  ],
  "rule_id": "PRIVACY-PIA-002",
  "method": "deterministic",
  "review_status": "not_required",
  "created_at": "..."
}
```
 
Compare that with:
 
```json
{
  "claim": "Human review is likely insufficiently independent for this decision.",
  "classification": "advisory",
  "method": "llm_reasoning",
  "confidence": 0.72,
  "sources": ["..."],
  "human_review_status": "required"
}
```
 
That distinction between **fact, rule execution, interpretation and recommendation** will make the system dramatically easier to trust.
 
### Suggested deterministic/LLM boundary
 
| Governance task | Default method |
|---|---|
| “Is this a Commonwealth NCE?” | Deterministic/look-up |
| “Does DTA AI policy apply to that entity class?” | Deterministic |
| “Does use case meet an explicitly stated trigger?” | Deterministic where facts are clear |
| “Could this failure cause more than insignificant harm?” | Structured assessment + LLM/human judgment |
| “Which APP provision says X?” | Retrieval |
| “Was the PIA completed?” | Deterministic |
| “Does this evidence satisfy the control?” | Deterministic where schema/test exists; inference otherwise |
| “Are two policies in tension?” | LLM analysis |
| “What emerging ethical concern is missing?” | LLM |
| “Has every mandatory requirement got evidence?” | SQL |
| “Draft the final report” | LLM |
| “Is the report's claim actually evidenced?” | Deterministic citation/evidence validator |
| “May this deploy?” | Rules establish blockers; human gives real production approval |
 
This should keep the expensive models focused where they genuinely outperform ordinary software.
 
## Recommended build scope and priorities
 
### The minimum viable Governance Guru is smaller than it first appears
 
I would resist implementing all of the above simultaneously. A surprisingly capable first release can be built around **six core objects and a handful of official tools**.
 
#### Foundation
 
The first build should contain:
 
| Build item | Why first |
|---|---|
| Context/intake schema | Everything depends on knowing the facts |
| Source/version registry | Prevents stale-policy hallucinations |
| Obligation registry | Gives governance a structured unit of work |
| Applicability rules | Produces deterministic coverage |
| Obligation–Control–Evidence Matrix | Creates your central assurance state |
| Decision/exception register | Prevents unresolved issues disappearing |
| Release gates | Converts governance into enforceable workflow |
| Citation/evidence validator | Stops Authors asserting unsupported compliance |
 
The initial knowledge pack should consist of the DTA AI regime, OAIC privacy material, Ombudsman ADM guidance, NAA AI records guidance, Commonwealth risk/procurement essentials, PSPF applicability, Digital Experience/accessibility and the Australian AI Ethics Principles. These cover a large proportion of likely cross-cutting Australian Government prototype issues. citeturn18view1turn18view8turn18view10turn19search1turn19search3
 
#### Assurance depth
 
Next, add:
 
| Capability | Reason |
|---|---|
| DTA Technical Standard mapping | Production-like engineering assurance |
| Agentic AI Addendum mapping | Highly specific to your architecture |
| Human-rights/anti-discrimination assessment | Consequential government uses |
| Indigenous Data Governance trigger | Important gap in generic governance frameworks |
| Procurement/vendor questionnaire | External AI services will be frequent |
| FOI/transparency assessment | Government accountability |
| IP/open-source scanning evidence | Coding swarm dependency risk |
| Source-change monitor | Keeps all of the above current |
 
The Agentic AI Addendum should be prioritized unusually early for **your own Council itself**, not just systems the Council constructs. Its requirements around agent responsibilities, human accountability, traceable multi-agent actions, oversight and intervention are directly applicable to your platform architecture. citeturn21view3
 
In other words, **The Council should be its Governance Guru's first assessment target.**
 
That would be a very useful dogfooding exercise.
 
#### Advanced capability
 
Only after the core works would I add:
 
| Capability | Value |
|---|---|
| NIST/Canada/UK/ISO crosswalks | Higher maturity and international coverage |
| OECD incident search | Dynamic red-teaming/scenario generation |
| OPA/Rego | Scalable policy-as-code |
| Sector-specific packs | Repeated domains justify permanent packs |
| State/territory packs | Build only as usage demands |
| Automated legislative-policy diff impact analysis | Significant long-term maintenance saving |
| Assurance analytics | Detect recurring weak controls across projects |
 
### A proposed system prompt-level charter
 
I would encode the Guru's mission approximately as:
 
> You are the Governance Guru of The Council. Your purpose is not to maximize caution or to prevent innovation. Your purpose is to establish what obligations, ethical considerations, assurance activities and human decisions are proportionate to the proposed solution and to maintain verifiable evidence that they were addressed.
>
> Prefer authoritative Australian primary sources over secondary commentary. Distinguish legislation, mandatory policy, guidance and best practice. Always consider jurisdiction, entity type, lifecycle stage, applicability and effective date.
>
> Prefer deterministic rules and official assessment processes where the required decision follows from known facts. Use inference for ambiguity, novel ethical questions, cross-domain trade-offs and synthesis.
>
> Never treat a low risk score as permission to disregard a mandatory obligation.
>
> Do not claim legal certainty where interpretation is genuinely contestable. Identify the legal question, relevant authority, assumptions and consequences, then flag expert review where appropriate.
>
> Delegate technical judgments to the appropriate Council expert. Governance owns assurance that the judgment was obtained and evidenced, not every underlying technical decision.
>
> Preserve dissent. Where Council members materially disagree, create a structured decision packet and escalate according to the Council protocol.
>
> Every material assurance conclusion must be traceable to authoritative requirements, evidence supplied by the Council, deterministic tests, or an explicitly identified judgment.
>
> Never fabricate evidence. Missing evidence remains missing.
>
> A prototype may proceed with documented unresolved matters where permitted by the project's autonomy rules; actual production release requires the designated human authority and any expert reviews marked as mandatory.
 
### The most useful final architecture
 
The resulting Governance Guru would operate less like a chatbot and more like this:
 
```text
                         ┌──────────────────────┐
                         │   HUMAN / COUNCIL    │
                         │      CHAIR           │
                         └──────────┬───────────┘
                                    │ escalation
                         ┌──────────▼───────────┐
                         │   GOVERNANCE GURU    │
                         └──────────┬───────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           │                        │                        │
 ┌─────────▼─────────┐   ┌──────────▼──────────┐  ┌────────▼────────┐
 │ Applicability     │   │ Assurance /         │  │ Research &       │
 │ Engine            │   │ Evidence Engine     │  │ Interpretation   │
 │ deterministic     │   │ deterministic       │  │ LLM + retrieval  │
 └─────────┬─────────┘   └──────────┬──────────┘  └────────┬────────┘
           │                        │                        │
           └─────────────┬──────────┴─────────────┬──────────┘
                         │                        │
              ┌──────────▼─────────┐   ┌────────▼──────────┐
              │ Obligation–Control │   │ Author Subagents  │
              │ –Evidence Matrix   │   │ evidence-bound    │
              └──────────┬─────────┘   └───────────────────┘
                         │
       ┌─────────────────┼──────────────────────────────────┐
       │                 │              │                   │
 ┌─────▼─────┐    ┌──────▼─────┐ ┌──────▼─────┐    ┌──────▼─────┐
 │ Security  │    │ Data       │ │ UX         │ ...│ Researcher │
 │ Architect │    │ experts    │ │ Designer   │    │            │
 └───────────┘    └────────────┘ └────────────┘    └────────────┘
                         │
                         ▼
               CODING-SWARM CONSTRAINTS
                         │
                         ▼
               BUILD / TEST EVIDENCE
                         │
                         ▼
               PRE-DEPLOY ASSURANCE CASE
                         │
                         ▼
                    HUMAN REVIEW
```
 
The most important design decision is the box in the center: **the Obligation–Control–Evidence Matrix, not the LLM conversation, is the authoritative state of governance**.
 
That fits both the technology you already intend to operate and the direction of Australian Government AI governance. DTA now expects accountable owners, documented impact assessment, traceable decision records, monitoring, explicit handling of higher-risk use cases and revalidation after change; its agentic guidance adds human accountability, multi-agent traceability, oversight and intervention. citeturn21view0turn21view2turn21view3
 
The Governance Guru therefore does not need to become a simulated lawyer, ethicist, privacy officer, records manager, procurement specialist, auditor and risk executive simultaneously. It needs to become something arguably more useful: **a highly reliable machine for knowing which of those perspectives are required, making sure each is actually exercised, preserving the evidence, and preventing a rapidly generated “working prototype” from silently outrunning its governance.**
