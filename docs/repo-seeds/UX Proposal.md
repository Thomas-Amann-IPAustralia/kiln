# Proposal for the User Experience Designer Agent in “The Council”
 
## Executive recommendation
 
The proposed UX expert should be broader than a conventional interface designer. In an Australian Government context, many of the hardest experience problems occur **before and after the screen**: channel choice, identity and authentication, transitions between agencies, accessibility, digital exclusion, trauma, service terminology, trust, error recovery, assisted-digital pathways, and the way policy or security constraints are exposed to a person. The Australian Public Service's current Experience Design Principles explicitly apply across online, phone and in-person interactions, as well as policy, programs and behind-the-scenes processes. They emphasize seven principles: **Simple, Inclusive, Safe, Tailored, Connected, Transparent and Trustworthy**. citeturn21search1turn18search0
 
For that reason, I would retain the agent name **UX Designer** if it is convenient, but give it the charter of an **Experience Designer**. Its concern should be the entire human experience of a solution, not merely visual UI.
 
I would also slightly change one phrase in the proposed role. Rather than instructing the agent to prioritize “the user experience over all else,” make it **the Council's advocate for user outcomes**. Security, legislation, privacy, accessibility and safety occasionally need to constrain convenience. The useful organizational behavior is constructive tension: the UX Designer argues forcefully from the user's perspective, the Security Architect argues from the threat model, the Governance Guru from policy and legal obligations, and the Solution Architect resolves the engineering trade-off when necessary. This is consistent with the Australian Government Digital Service Standard, which simultaneously requires teams to know users, leave no one behind, build trust, avoid harm and meet applicable standards. citeturn21search6turn21search25turn21search30
 
The current Australian Government Digital Experience Policy is an especially important foundation for this agent. Existing public-facing services are now expected to comply with the Digital Service Standard and Digital Inclusion Standard, and the policy ecosystem additionally includes Digital Access and Digital Performance standards. citeturn21search0 The Inclusion Standard explicitly requires consideration of diverse users, co-design, cohort-specific requirements, safety, accessibility, flexibility and seamless channel transitions. citeturn21search4turn21search13
 
My recommended shape is therefore:
 
| Area | Recommendation | Importance |
|---|---|---:|
| **Agent identity** | UX Designer, chartered as an end-to-end **Experience Designer** | Critical |
| **Primary authority** | Australian Government Digital Experience Policy, standards, toolkit and APS Experience Design Principles | Critical |
| **Accessibility** | WCAG 2.2 + WAI guidance + automated and manual evaluation methodology | Critical |
| **Inclusive design** | Digital Inclusion Standard, Style Manual, COGA guidance, Australian inclusion research, trauma-informed and culturally sensitive guidance | Critical |
| **Interaction patterns** | Current Australian design systems first; GOV.UK/W3C/USWDS as secondary pattern libraries | High |
| **Content design** | Australian Government Style Manual encoded partly as deterministic Vale rules | High |
| **Browser inspection** | Chrome DevTools for agents | High |
| **Automated UX/accessibility QA** | Playwright + axe-core + HTML validation + framework-specific static linting | Critical |
| **Component development** | Storybook when the solution benefits from a component system | High |
| **Visual craft** | Anthropic `frontend-design` skill as an optional aesthetic specialist, not an authority | Medium |
| **AI UX** | Microsoft HAX human-AI interaction guidelines and patterns | High for AI-enabled solutions |
| **Design artifacts** | Text/code-first, version-controlled journey maps, interaction specifications, UX decision records and acceptance criteria | Critical |
| **GUI design tool** | Penpot optional, not foundational | Low–Medium |
| **Knowledge architecture** | Source-authority hierarchy + metadata filtering + semantic retrieval + freshness checks | Critical |
| **Escalation behavior** | Explicit triggers for vulnerable cohorts, conflicting standards, irreversible actions, authentication/security friction, uncertain evidence and consequential AI | Critical |
 
The most important implementation principle is **not to turn the UX agent into one enormous prompt containing accumulated UX wisdom**. Give it a small constitutional layer, structured decision procedures and checklists, then retrieve detailed guidance as needed. This suits your deterministic-first philosophy and should substantially reduce both context cost and the tendency of a model to “remember” an attractive generic design rule when a more specific Australian rule applies.
 
## Role charter and place on The Council
 
I suggest the following as the basis of its system-level role description.
 
> **The UX Designer is The Council's advocate for the people who will interact with the solution. It is accountable for understanding and representing user needs, end-to-end journeys, information architecture, interaction design, content interaction, accessibility, inclusive design, service usability and the human consequences of design choices. It converts evidence about users into requirements, design decisions and testable acceptance criteria. It prefers existing, researched and accessible interaction patterns over novel ones unless evidence supports deviation. It must distinguish known user evidence from assumptions. It must never treat automated accessibility testing as proof of accessibility. It collaborates with other Council members where user experience intersects with architecture, security, governance and data, and escalates unresolved conflicts to the Council Chair.**
 
That language deliberately makes **evidence** a first-class concept. DTA's service-design guidance says teams should understand users before building, include diverse abilities, ages, languages and backgrounds in research, understand the surrounding processes and constraints, and use artifacts such as journey maps to capture the *real* user experience rather than the team's idealized process. citeturn12view1 DTA's current “Know your user” criterion similarly asks who will use the service, their needs, frustrations, existing experience and devices or technologies. citeturn21search30
 
### Recommended division of Council responsibilities
 
| Question | UX Designer's role | Primary collaborator / escalation | Why this boundary matters |
|---|---|---|---|
| What should the person be able to achieve? | **Own** task and journey definition from user evidence | Researcher, Solution Architect | Separates human outcome from technical implementation. |
| What do users actually need or do today? | Form hypotheses; synthesize available UX evidence; identify gaps | **Researcher** for deeper external research or methodological questions | Prevents an LLM-generated persona from masquerading as research. DTA emphasizes actual user research and existing evidence. citeturn12view1turn21search30 |
| What should the interface do? | **Own** IA, interactions, states, progressive disclosure, error recovery and UX acceptance criteria | Solution Architect | Core UX responsibility. |
| What should it look like? | Own high-level visual hierarchy and design direction | Coding swarm / frontend specialist | The UX agent should specify human outcomes and constraints without micromanaging every CSS property. |
| Is it accessible? | **Own experience-level accessibility requirements and evidence** | Developers implement; Governance Guru advises on mandatory obligations | DTA requires latest WCAG and Style Manual, but technical checks alone do not demonstrate accessibility. citeturn21search4turn6search3 |
| Can a security measure be made less burdensome? | Advocate for reduced friction and accessible recovery | **Security Architect** owns residual security risk | Prevents UX from silently weakening a security control. |
| Is collection of a field lawful or necessary? | Challenge apparent over-collection and explain UX harm | **Governance Guru** decides policy/legal interpretation | UX should spot harmful collection without pretending to be counsel. |
| How should analytics measure whether the design works? | Define behavioral questions, critical tasks and experience success criteria | **Data Analyst** designs measurement/analysis | Keeps telemetry tied to user outcomes. |
| What event/data structures support analytics? | State UX intent | **Data Engineer** | Avoids UX prescribing data plumbing. |
| Is the proposed pattern technically feasible? | Explain user impact of alternatives | **Solution Architect** | Enables explicit trade-offs rather than silent degradation. |
| Are two Council priorities irreconcilable? | Document affected users and consequences | **Solution Architect as Chair** | Creates traceable Council decisions. |
 
A valuable rule is: **the UX Designer may make a decision where it has strong applicable evidence; it should escalate when it only has a principle and competing Council concerns materially affect the outcome.**
 
For example, it can autonomously reject a placeholder-only form field with no persistent label. It should not autonomously decide to remove re-authentication from a high-risk transaction because usability testing suggests users dislike it.
 
## Proposed knowledge base
 
I would divide the knowledge base into authority tiers rather than one flat vector collection. The metadata is almost as important as the content itself.
 
### Core knowledge corpus
 
| Knowledge package | What to ingest | How the agent should use it | Priority |
|---|---|---|---:|
| **Australian Government Digital Experience Policy** | Policy, applicability, implementation guidance, checklists, Digital Service, Inclusion, Access and Performance standards | This is the first retrieval target for Commonwealth-facing service design. Current policy covers service design, inclusion, access and measurement, with existing public services now subject to Service and Inclusion requirements. citeturn21search0turn21search4 | **Essential** |
| **APS Experience Design Principles** | Simple, Inclusive, Safe, Tailored, Connected, Transparent, Trustworthy; guidance and examples | Treat these as the UX agent's Australian-government “constitutional” principles. They are deliberately broader than screen design and were last updated in June 2026. citeturn21search1 | **Essential** |
| **Digital Experience Toolkit** | Discovery/Alpha/Beta/Live guidance; research methods; diversity guidance; service design methods; templates and checklists | Gives the agent a government-specific working method rather than merely generic UX knowledge. The current toolkit includes user research, service-design stages and practical evidence artifacts. citeturn21search5turn21search16 | **Essential** |
| **Australian Government Style Manual** | Entire public Style Manual, especially accessibility, inclusion, clear language, inclusive terminology, forms and content conventions | Authoritative content-design layer. The Style Manual describes itself as the standard for Australian Government writing and editing and recommends accessible, inclusive, user-centered content. citeturn21search10 | **Essential** |
| **Style Manual accessibility corpus** | Accessible/inclusive content; disability and neurodiversity; literacy; Easy Read; how people read; inclusive language | Important for public-facing services and vulnerable cohorts. The Style Manual recommends writing around Australian Year 7 level for broad accessibility and using short sentences/simple structures. citeturn21search3turn21search29 | **Essential** |
| **WCAG 2.2** | Normative WCAG 2.2, Understanding documents and relevant techniques | Authoritative web accessibility baseline. W3C recommends WCAG 2.2 as the current version; Australian Government guidance calls for the latest WCAG version. citeturn6search2turn21search4 | **Essential** |
| **WAI evaluation guidance / ACT context** | Evaluation methodology, limits of automation, ACT rules | Critical guardrail so the agent never equates “axe passed” with “accessible.” W3C explicitly states that no evaluation tool alone can determine conformance. citeturn6search3turn6search9 | **Essential** |
| **WAI ARIA Authoring Practices Guide** | Current widget patterns, keyboard behavior, names/descriptions, landmarks | Use when custom interactions are genuinely needed. APG supplies patterns and functional examples for ARIA semantics and keyboard behavior, while warning that it is guidance rather than a UI design system. citeturn16search0turn16search12 | **Essential** |
| **W3C Cognitive Accessibility guidance** | COGA objectives, patterns, user needs and personas | Fills important usability gaps not captured by WCAG conformance alone, particularly for neurodivergence, cognitive and learning disabilities. W3C explicitly describes this guidance as supplemental to WCAG. citeturn17search0turn17search22 | **High** |
| **DTA Digital Inclusion cohort guidance** | Disability, low vision, Deaf/hard-of-hearing, First Nations, domestic/family violence, neurodiversity, culturally and linguistically diverse users, low digital ability | This should drive “who might we be excluding?” checks before interface design starts. DTA's inclusion guidance requires consideration of diverse cohorts rather than treating accessibility as an end-stage test. citeturn3view0turn21search6 | **Essential** |
| **Australian Digital Inclusion Index** | Latest national findings and methodology | Gives the agent empirical context for access, affordability and digital ability rather than assuming “everyone has a phone and broadband.” The index measures those three dimensions and supports comparisons across groups and places. citeturn11search3turn11search18 | **High** |
| **eSafety Safety by Design** | Safety-by-design principles and relevant industry guidance | Particularly useful for services involving messaging, communities, children, vulnerable people or user-generated content. eSafety centers proactive user safety, empowerment and accountability. citeturn11search2turn11search6 | **High** |
| **Trauma-informed Australian guidance** | DTA vulnerability guidance plus AIFS trauma-informed practice resources | Use when interactions concern family violence, disaster, health, welfare, justice, bereavement or other distressing situations. DTA explicitly places trauma-informed and dignity-promoting practices within APS experience design; AIFS emphasizes safety, trust, transparency, choice and avoiding re-traumatization. citeturn18search0turn18search2turn18search6 | **High** |
| **First Nations engagement/cultural safety** | DTA Indigenous inclusion material; selected current AIATSIS ethics, cultural capability and research guidance | This must be treated as an area where generic inference is especially dangerous. The agent should identify the need for genuine co-design/cultural expertise rather than “designing for” First Nations people from an LLM persona. DTA calls for culturally sensitive, strengths-based engagement; AIATSIS emphasizes Indigenous involvement and agency in relevant research. citeturn18search4turn18search10 | **High** |
| **Australian Government Architecture reuse guidance** | Reuse policies/patterns and reusable capabilities relevant to user journeys | Before inventing another service entrance or interaction, check what government already provides. The current Digital Access Standard explicitly tells teams to investigate how users already access services and available reusable platforms/capabilities. citeturn21search11 | **High** |
 
### Pattern libraries rather than authorities
 
The agent will also need concrete interaction patterns. I would deliberately label these **precedent and pattern sources**, not compliance authorities.
 
| Pattern source | Recommendation | Why |
|---|---|---|
| **NSW Design System** | Make this the first generic component/pattern library searched when there is no applicable Commonwealth component | It is actively maintained, provides components/templates/Figma resources, and currently targets WCAG 2.2 AA. This makes it an unusually relevant Australian public-sector precedent. citeturn13search2turn13search6 |
| **GOV.UK Design System** | Ingest components, patterns, research notes and use/avoid guidance | Particularly strong for transactional government interactions such as forms, question flows, check-answer pages and end-to-end tasks. GOV.UK publishes research-backed styles, components and patterns and explicitly encourages reuse of existing researched solutions. citeturn13search0turn13search4turn13search30 |
| **US Web Design System** | Secondary reference for government components and inclusive patterns | Supplies components together with UX/accessibility guidance and government design principles. citeturn13search5turn13search11 |
| **WAI APG** | Use when accessibility behavior matters more than visual styling | It is particularly valuable for the functional contract of menus, dialogs, tabs, trees, grids and keyboard navigation. citeturn16search0turn16search2 |
| **Project or agency design system** | Always search before generic external systems | Existing organizational components usually carry branding, implementation constraints and institutional research the agent should not throw away. |
| **Historical Australian Government Design System** | Keep only in a **deprecated/historical** collection | The former whole-of-government AGDS repository was archived and explicitly says the system was decommissioned. Do not allow RAG to accidentally treat its components as current Commonwealth standards. citeturn8view0 |
 
That last point is important. A naïve RAG search for “Australian Government button component” can retrieve authoritative-looking but obsolete material. **Status metadata is therefore a UX safety mechanism**, not mere data hygiene.
 
### Specialist knowledge worth including
 
| Domain | Corpus / framework | Use |
|---|---|---|
| **Human-AI interaction** | Microsoft Human-AI Experience (HAX) Toolkit | Very relevant because the Council itself will build AI-enabled applications. HAX's 18 evidence-based guidelines cover initial expectations, normal interaction, AI failures and adaptation over time. citeturn16search1turn16search3 |
| **AI failure UX** | HAX design patterns/playbook | Useful for uncertainty, correction, feedback, user control, graceful fallback and communicating system capability. The underlying guidelines were validated with practitioners against real AI-enabled products. citeturn16search9 |
| **Responsive/adaptive design** | DTA flexibility guidance + current design-system precedents | DTA asks government services to support adaptable interfaces, device contexts and different ways of engaging. citeturn21search13 |
| **Service/channel design** | DTA Access Standard and service-design process | Prevents “web app tunnel vision”; government users may transition between digital and assisted channels. citeturn21search6turn21search11 |
| **Easy Read / low literacy** | Australian Government Style Manual | Use when audience analysis indicates need; do not have the model invent an “Easy Read” version and assume it is valid simply because sentences are short. citeturn21search3turn21search21 |
| **Design systems/tokens** | Design Tokens Community Group specification | A machine-readable token layer is extremely useful when the Council hands designs to coding agents. The DTCG published its first stable format specification, v2025.10, for exchanging design tokens. citeturn20search2turn20search10 |
 
### Project-specific evidence should be first-class knowledge
 
For each solution, create a temporary project UX corpus containing the brief, relevant policy, existing service screenshots/content, user research, previous evaluations, analytics, contact-center themes, feedback, identified cohorts, known devices and assistive technologies, organizational design system, terminology and prior decisions.
 
This material should normally outrank generic UX literature because it describes the actual environment. DTA specifically recommends using existing research and data, understanding real journeys and documenting evidence about diverse and vulnerable cohorts. citeturn12view1turn3view0
 
The agent should distinguish:
 
| Evidence label | Meaning |
|---|---|
| `OBSERVED` | Direct project research, analytics or documented behavior |
| `AUTHORITATIVE` | Applicable standard, policy or organizational requirement |
| `SUPPORTED` | Relevant external research or established pattern |
| `INFERRED` | Reasonable deduction from available evidence |
| `ASSUMED` | Unvalidated proposition required to continue |
| `UNKNOWN` | Material evidence gap |
 
That one mechanism would make the agent substantially safer. A generated persona saying “older users will probably prefer…” should never quietly acquire the epistemic status of a user interview.
 
## Toolkit and skills
 
The most valuable toolkit is not a giant assortment of design applications. It is a small chain that lets the agent **observe a real interface, test objective properties deterministically, retrieve standards, reason about what remains, and return precise defects or requirements to the coding swarm**.
 
### Recommended core tools
 
| Tool / capability | What it should do | Suggested status | Why it belongs |
|---|---|---|---|
| **Chrome DevTools for agents / MCP** | Give the UX agent direct access to a rendered browser: navigate, inspect elements, interact with the application, investigate performance and run browser-level checks | **Core** | This is unusually well matched to your architecture. Chrome now provides agent-focused DevTools that allow coding agents to control and inspect live Chrome; the MCP server and CLI reached stable status in the current Chrome 149 generation. citeturn19search0turn19search20turn19search36 |
| **Playwright** | Deterministic critical-journey execution across browser engines; keyboard/task tests; state traversal; regression tests | **Core** | It turns Council decisions such as “the transaction must remain completable by keyboard” into repeatable tests rather than future model inference. Playwright has dedicated accessibility-testing guidance and supports ARIA-tree snapshots. citeturn19search1turn19search5 |
| **axe-core integrated with Playwright** | Automated WCAG-oriented checking against rendered states | **Core** | Excellent automated first pass. Deque says axe-core can detect an average of about 57% of WCAG issues automatically and marks uncertain cases for manual review. That limitation is precisely why it should be a gate, not a declaration of compliance. citeturn19search3turn6search9 |
| **Playwright ARIA snapshots** | Snapshot the accessibility tree for critical states and detect semantic regressions | **Core** | A subtle frontend change can leave the screenshot looking identical while changing names, roles or hierarchy. Playwright represents and compares the accessibility tree in YAML/structured form. citeturn19search5turn19search17 |
| **Nu HTML Checker (`v.Nu`)** | Validate generated HTML/SVG/CSS structures | **Core for web** | Cheap deterministic hygiene. The checker can batch-test documents and run locally or as a service. citeturn15search5 |
| **`eslint-plugin-jsx-a11y`** | Catch statically identifiable accessibility mistakes when React/JSX is used | **Conditional core** | Useful “shift-left” check, although its own documentation stresses that static analysis is insufficient and should be combined with rendered-DOM and assistive-technology testing. citeturn15search2 |
| **Lighthouse** | Performance and broad web-quality audits | **Useful** | Performance is part of experience, particularly under weak devices/networks. It is an automated audit tool rather than a substitute for real-user performance evidence. citeturn9search1 |
| **Storybook + official accessibility addon** | Isolated component states, documentation and component-level axe testing | **Use where a component system exists** | Very valuable when the coding swarm builds a reusable UI library. Storybook's official accessibility addon runs axe-core against component stories. citeturn19search2 |
| **Vale** | Deterministic prose linting against encoded Australian Government writing rules | **Core** | This is the best match I found for your proposed “deterministic APS Style Manual checker.” Vale is specifically designed to turn writing guidelines into checks that run locally, in editors and CI, including completely offline. citeturn15search0turn15search3 |
| **Custom Style Manual rule pack for Vale** | Encode reliably machine-checkable terminology, capitalization, common constructions, forbidden/flagged terms and house conventions | **Build once** | Not every Style Manual rule is deterministic, but many are. The Style Manual itself is the Australian Government standard and includes clear accessibility/inclusion guidance. citeturn21search10turn21search24 |
| **Custom UX policy evaluator** | Structured rules evaluating project metadata against Council requirements | **Build once** | Example: “public-facing Commonwealth service + form” automatically loads DX standards, WCAG/Style Manual, relevant inclusion checks and a form-pattern corpus before design begins. This is where determinism can eliminate unnecessary model calls. |
| **Design-system/pattern search tool** | Search components and patterns by intent rather than name alone | **Core skill** | Before generating a bespoke interaction, the agent should check Australian/project systems, then researched external public-service patterns. DTA itself emphasizes reuse; GOV.UK similarly says to start with what exists. citeturn21search11turn13search3 |
| **Rendered visual inspection skill** | Inspect hierarchy, density, state visibility, clipping, overflow, responsive behavior and obvious usability problems | **Core inferential skill** | Deterministic tools cannot judge whether an interface is overwhelmingly dense, the hierarchy misleading or a progressive-disclosure decision appropriate. |
| **UX heuristic review skill** | Structured rubric rather than free-form “review this UI” prompting | **Core inferential skill** | Makes subjective reasoning repeatable and reportable. Inputs should include user/task/context and deterministic test outputs. |
| **Journey simulator** | Execute representative user journeys with explicit goals and constraints | **High value** | The agent should reason through full tasks rather than evaluate screenshots independently. This is particularly aligned with DTA's emphasis on end-to-end journeys. citeturn12view1turn21search11 |
| **UX decision record writer** | Emit structured rationale, evidence, alternatives, affected groups and unresolved risk | **Core** | Gives Langfuse/Git/GitHub an auditable explanation of why Council decisions were made. |
| **Design-token reader/writer** | Read or produce a common machine-readable design-token format | **High** | The stable DTCG format gives you a tool-independent representation for colors, spacing, typography and related design-system values. citeturn20search2turn20search10 |
 
### Your proposed WCAG checker
 
I strongly agree with the idea, but I would implement it as a **testing stack**, not a single “WCAG compliance checker.”
 
A sensible sequence is:
 
`static code checks → HTML validation → rendered axe scan → deterministic keyboard/task tests → ARIA snapshots → agent visual/heuristic review → targeted human/assistive-technology evaluation`
 
W3C warns that automated tools cannot test all accessibility requirements and that human judgment is necessary; usability testing with disabled users can also reveal problems that conformance checks miss. citeturn6search3turn6search14
 
The UX agent therefore should be **forbidden from outputting**:
 
> “The application is WCAG compliant because axe reported no violations.”
 
Its permissible statement should look more like:
 
> “No automated WCAG violations were detected by axe-core in the 14 tested states. Keyboard traversal and accessibility-tree regression tests also passed. This does not establish WCAG conformance; the following criteria and assistive-technology behaviors still require human/manual evaluation.”
 
That distinction is particularly important because axe itself states that it detects only a portion of WCAG issues automatically. citeturn19search3
 
Deque now also publishes an **agent-facing Axe Accessibility plugin/MCP capability**, which may be worth evaluating if you prefer an off-the-shelf bridge between your agents and accessibility tooling rather than writing that integration yourself. citeturn19search35 I would still keep raw axe-core/Playwright available because they are easy to make deterministic, CI-friendly and transparent.
 
### Your proposed APS Style Manual checker
 
This is also a strong idea. I would build **`council-style-au` as a Vale style package** rather than a bespoke text-analysis program.
 
The rules should be divided into three classes:
 
| Rule type | Example | Treatment |
|---|---|---|
| **Deterministic** | prohibited terminology, preferred capitalization, common abbreviations, punctuation conventions, numerals, known terminology | Vale error/warning |
| **Heuristic but measurable** | sentence length, heading density, possible passive construction, unexplained acronym, extremely long paragraphs | Warning requiring contextual review |
| **Semantic/judgmental** | whether wording is genuinely plain, respectful, trauma-informed, culturally appropriate or adequately explains a complex concept | Send to UX model with the relevant Style Manual passages |
 
The Style Manual says government content should be clear and consistent, designed around user needs, and accessible and inclusive. It also says familiar language and user research should inform word choice. citeturn21search10turn21search32 That second category illustrates why the checker should not become a simplistic readability-score gate: a mathematically “easy” sentence can still be ambiguous, patronizing or wrong.
 
This provides a very attractive deterministic workflow:
 
`coding/content agent writes copy → Vale emits precise violations → agent automatically fixes safe rules → UX Designer reviews only semantic warnings`
 
That should be cheaper than passing every paragraph through the UX LLM.
 
### Anthropic's Frontend Design skill
 
Your initial instinct is sound, but I would position this as a **craft specialist**, not part of the UX agent's authority stack.
 
Anthropic's current official `frontend-design` skill describes itself as guidance for distinctive, intentional visual design, covering aesthetic direction, typography and avoiding templated/default-looking interfaces. The corresponding plugin describes its aim as creating distinctive, production-grade frontend interfaces. citeturn20search0turn20search8turn20search12
 
That is useful because generative coding agents have a tendency to converge on competent-but-generic dashboards. The skill is largely concerned with the thing your WCAG/DTA/pattern machinery intentionally does **not** answer: *what makes this particular interface visually considered rather than merely valid?*
 
I would therefore use the responsibilities as follows:
 
| Layer | Authority |
|---|---|
| User needs, journey, inclusion, task model | **UX Designer** |
| Applicable standards and government patterns | **UX Designer / Governance Guru** |
| Security/privacy constraints | **Security Architect / Governance Guru** |
| Structure, interaction, information hierarchy | **UX Designer** |
| Visual design intent | **UX Designer** |
| Detailed aesthetic execution | **Frontend Design skill + coding agent** |
| Implementation feasibility | **Solution Architect / coding swarm** |
| Rendered validation | **UX Designer + deterministic test stack** |
 
Also, the `claudecowork.im` page in the prompt is not the source I would ingest as canonical. The current first-party source is Anthropic's own GitHub repository. Anthropic also warns generally that plugins may include external servers/files/software and should be trusted before installation. citeturn20search13
 
If The Council is intended to be model-provider-neutral, I would call the Anthropic skill conditionally rather than building the UX architecture around it. The generic capability you need is “frontend craft review/generation”; the Anthropic implementation is one current provider.
 
### Optional design environment
 
For your particular system I would remain **code-first** by default. With coding agents able to generate a functional HTML/React prototype as quickly as traditional mockups, creating a Figma-like representation and then separately translating it into code can become unnecessary duplication.
 
Where genuine collaborative visual design is needed, **Penpot** is a particularly interesting optional tool: it is open source, supports prototyping and can be self-hosted, including inside controlled infrastructure. citeturn20search3turn20search15turn20search27
 
I would not initially deploy it. Add it only when you discover a recurring need for humans to manipulate visual designs independently of the code. The default Council artifacts can remain Git-native.
 
## Deterministic-first operating model
 
The UX agent is particularly well suited to your deterministic-first philosophy because much of good experience governance consists of asking known questions consistently.
 
I recommend giving it a pipeline rather than a single “design this solution” tool call.
 
| Stage | Deterministic work first | Inference work only where valuable | Output |
|---|---|---|---|
| **Classify solution** | Identify jurisdiction, public/staff-facing, channels, user groups, transaction criticality, AI involvement, vulnerable cohorts | Infer ambiguous risk characteristics | `ux_context.json` |
| **Resolve obligations** | Rule engine maps classification to applicable DTA/WCAG/Style Manual/agency guidance | Resolve genuinely ambiguous applicability with Governance Guru | Standards manifest |
| **Retrieve evidence** | Search project evidence and authoritative KB using metadata filters | Synthesize evidence; identify contradictions/gaps | Evidence map |
| **Model user experience** | Apply artifact schemas | Infer journeys/tasks from evidence while explicitly marking assumptions | Journey/task model |
| **Search existing patterns** | Exact/tag retrieval across agency/NSW/DTA/GOV.UK/W3C libraries | Compare pattern suitability to the problem | Pattern decision |
| **Produce interaction specification** | Schema validation for required states/errors/content/accessibility criteria | Design information architecture and progressive disclosure | UX contract |
| **Council review** | Automated check for unaddressed risks or missing evidence | Argue trade-offs with other experts | Approved Council plan |
| **Build** | Coding swarm follows UX contract | Local design decisions within delegated autonomy | Working application |
| **Static QA** | Vale, HTML validator, linters | None unless errors are ambiguous | Machine reports |
| **Rendered QA** | Playwright, axe, ARIA snapshots, critical-path scripts | Visual and heuristic inspection | UX defect report |
| **Repair loop** | Categorize failures and route them automatically | Infer fix for non-obvious UX defects | Patched build |
| **Pre-release assessment** | Evidence matrix verifies required tests exist | Synthesize unresolved risks and manual-test requirements | UX assurance pack |
 
This means a large proportion of interactions need not call the full UX agent at all.
 
For example:
 
```text
axe violation
    ↓
known rule + known affected DOM
    ↓
coding agent receives deterministic remediation task
    ↓
rerun axe
    ↓
pass
```
 
The UX Designer only enters the loop when, for example, fixing the WCAG problem requires changing the interaction model or two solutions create different user consequences.
 
Likewise:
 
```text
Vale terminology error
    ↓
safe deterministic replacement
    ↓
rerun Vale
```
 
versus:
 
```text
“Is this warning message understandable without causing undue distress?”
    ↓
UX Designer retrieves Style Manual + trauma-informed guidance
    ↓
semantic reasoning required
```
 
### A structured UX contract for the coding swarm
 
The UX Designer should not primarily communicate its approved design to coding agents through prose. Have it produce a machine-readable **UX Contract**, perhaps YAML, containing at least:
 
| Contract field | Example contents |
|---|---|
| `user_groups` | Primary, secondary, vulnerable/at-risk, assisted-digital users |
| `critical_tasks` | User goal, start condition, successful end state |
| `journeys` | Ordered stages across digital and non-digital channels |
| `evidence` | Source IDs and evidence classifications |
| `assumptions` | Explicit unvalidated assumptions |
| `information_architecture` | Pages/views and hierarchy |
| `interaction_rules` | Progressive disclosure, default states, save/resume behavior |
| `component_patterns` | Selected researched component/pattern references |
| `content_rules` | Terminology, reading considerations, required explanations |
| `states` | Empty, loading, partial, error, expired, unavailable, success, permission denied |
| `accessibility_acceptance` | Keyboard, semantics, zoom/reflow, contrast, error identification, etc. |
| `responsive_expectations` | Relevant viewport/device behavior |
| `safety_requirements` | Quick exit, sensitive notifications, session privacy, etc., where applicable |
| `ai_interaction` | Capability disclosure, uncertainty, correction, feedback, fallback |
| `telemetry_questions` | What UX questions need later measurement |
| `manual_validation` | Checks automation cannot establish |
| `escalation_conditions` | Decisions the coding swarm cannot make alone |
 
The coding agents can then implement against that contract, while automated tests can be generated from parts of it. That is a much stronger architecture than asking the swarm to repeatedly reinterpret a long UX design document.
 
### Risk-sensitive UX autonomy
 
A useful autonomy framework is:
 
| Band | UX agent behavior | Examples |
|---|---|---|
| **Green** | Decide and implement through the plan without escalation | Button wording, hierarchy, common component selection, spacing intent, documented form-error pattern |
| **Amber** | Decide provisionally, record rationale and notify relevant Council member | New interaction pattern, complicated progressive disclosure, unusual workflow, significant departure from agency design system |
| **Red** | Must escalate | Vulnerable-user safety; family/domestic violence scenarios; potentially coercive consent; inaccessible critical journey; conflict between security and access; irreversible/high-consequence action; culturally sensitive First Nations assumptions; consequential AI automation; conflicting government requirements |
 
This is particularly appropriate given DTA's current emphasis on marginalised and vulnerable users, non-digital pathways, alternate formats and assistive-technology evaluation. citeturn21search6
 
## Knowledge retrieval, ingestion and freshness
 
Your existing Neon/Postgres/pgvector architecture is entirely adequate for this agent initially. I would not introduce a separate vector database solely for UX knowledge.
 
The important improvement is to treat retrieval as **structured information retrieval first and semantic similarity second**.
 
### Suggested document metadata
 
Every ingested chunk should carry fields such as:
 
```text
source_id
source_title
publisher
canonical_url
jurisdiction
authority_level
source_type
topic
user_cohort
service_stage
interaction_pattern
normative_or_informative
effective_date
last_updated
last_verified_at
status
supersedes
superseded_by
applicability
wcag_criteria[]
tags[]
```
 
The resulting ranking logic can resemble:
 
```text
1. Applicable project/agency mandate
2. Applicable Australian Government standard/policy
3. W3C normative accessibility standard
4. Australian Government official guidance/toolkit
5. Project-specific observed evidence
6. Australian specialist authority
7. Research-backed public-sector pattern
8. General evidence/framework
9. Generic UX knowledge
10. Historical/deprecated material
```
 
There is one nuance: **observed project user evidence should outrank generic guidance for questions about what users actually do, but it must not override a mandatory standard**. An interview participant preferring low-contrast gray text is not evidence for violating accessibility requirements.
 
### Search before semantic retrieval
 
I would give the agent explicit search operators rather than only `similarity_search(query)`:
 
| Retrieval primitive | Example |
|---|---|
| `find_standard()` | `jurisdiction=Commonwealth`, `topic=accessibility`, `status=current` |
| `find_pattern()` | `intent=collect postal address`, `source_tier<=pattern` |
| `find_cohort_guidance()` | `cohort=family_domestic_violence` |
| `find_wcag()` | `criterion=3.3.2` |
| `find_style_rule()` | `topic=links` |
| `find_project_evidence()` | `task=reset account access` |
| `find_precedent()` | `intent=check answers before submission` |
| `find_decisions()` | Previous UX decision records matching this context |
| `find_counterevidence()` | Deliberately retrieve evidence opposing the proposed design |
 
The last function is worth building. Once the agent has a favorite solution, ask retrieval to find **reasons it may fail**, particularly for an excluded cohort.
 
### Dynamic web lookup
 
Do not rely indefinitely on snapshots of the DTA ecosystem. Current Australian digital-experience material is actively maintained: for example, the APS Experience Design Principles were updated in June 2026, and the policy rollout itself has changed over the 2024–2026 period. citeturn21search0turn21search1
 
Give each authoritative source an update policy:
 
| Source | Suggested refresh |
|---|---|
| DTA Digital Experience Policy/standards/toolkit | Weekly or fortnightly change check |
| Australian Government Style Manual | Monthly change check + changelog |
| WCAG/WAI guidance | Monthly |
| Current design systems | Monthly |
| eSafety / AIFS specialist guidance | Quarterly, or live search when context requires |
| Research frameworks / academic classics | Much slower |
| Project evidence | Event-driven |
| Deprecated material | Never auto-promote; retain immutable status |
 
The refresh job does not need an LLM. Fetch, normalize, hash and compare pages deterministically; invoke a model only to classify material differences or update metadata.
 
### Chunk by decisions, not arbitrary token windows
 
For UX guidance, naive 500-token chunking can break the relationship between:
 
> “Use this pattern when…”
 
and
 
> “Do not use this pattern when…”
 
That can cause exactly the kind of confident RAG error you want to avoid.
 
Chunk source documents by semantic structure:
 
```text
pattern
 ├─ purpose
 ├─ when_to_use
 ├─ when_not_to_use
 ├─ implementation
 ├─ accessibility
 ├─ research_evidence
 └─ examples
```
 
Retrieve the **whole pattern object** once a match is found.
 
This works especially well with sources such as GOV.UK, where patterns explicitly include research and contextual usage guidance rather than merely screenshots. citeturn13search4turn13search30
 
### Store deprecation explicitly
 
The archived Australian Government Design System is the clearest example of why:
 
```json
{
  "status": "deprecated",
  "usable_as": ["historical_context", "pattern_inspiration"],
  "usable_as_authority": false
}
```
 
Its GitHub repository is archived and read-only, so a normal “government + design system + high semantic similarity” query could otherwise incorrectly rank it above a current NSW or DTA resource. citeturn8view0
 
## Recommended UX agent workflow and deliverables
 
I would make the agent produce a consistent evidence package at each major Council checkpoint. This also gives Langfuse meaningful artifacts to inspect rather than only chat traces.
 
### Before The Council approves a solution
 
| Artifact | Contents | Why |
|---|---|---|
| **Experience Brief** | Users, context, goals, channels, critical tasks, constraints, risks | Prevents UI generation before the human problem is understood. |
| **Evidence Map** | What is observed, authoritative, inferred, assumed and unknown | Exposes hallucinated “user needs.” |
| **Inclusion Map** | Potentially excluded cohorts and relevant guidance | DTA requires explicit consideration of marginalised, vulnerable and non-digital users. citeturn21search6 |
| **Current/Target Journey** | End-to-end experience including non-screen steps | DTA emphasizes real end-to-end journeys and existing access behavior. citeturn12view1turn21search11 |
| **Pattern Inventory** | Existing applicable patterns/components plus reasons for use/rejection | Biases the system toward reuse. |
| **Interaction Model** | IA, flow, states, progressive disclosure, recovery | Coding swarm implementation contract. |
| **Accessibility Strategy** | Applicable requirements, automated coverage and manual gaps | Prevents “accessibility at the end.” |
| **Content Strategy** | Terminology, reading level intent, sensitive wording, localization/alternate format needs | Ties writing into UX rather than treating it as decoration. |
| **UX Risk Register** | Severity, affected cohorts, mitigation and owner | Gives Council conflicts somewhere explicit to live. |
| **UX Decision Records** | Decision, alternatives, evidence and rationale | Makes meaningful autonomous decisions auditable. |
 
### During development
 
The UX agent should not continuously hover over every coding agent. Instead, the swarm receives the UX Contract and automated checks. The UX Designer is invoked when a threshold is crossed.
 
Example routing:
 
```text
Coding agent encounters UX question
          │
          ├── Existing UX contract answers it
          │       └── continue
          │
          ├── Existing authoritative pattern unambiguously answers it
          │       └── apply + record
          │
          ├── Local Green-band choice
          │       └── decide + record
          │
          ├── UX ambiguity
          │       └── UX Designer
          │
          ├── Security / privacy / governance conflict
          │       └── relevant Council experts
          │
          └── unresolved cross-domain conflict
                  └── Solution Architect / Chair
```
 
That should save substantial tokens compared with repeatedly holding a full Council discussion.
 
### Before prototype completion
 
The UX Designer should create an **Experience Assurance Report**, not a binary “UX passed” output.
 
A good report could contain:
 
| Assurance dimension | Evidence |
|---|---|
| Critical journeys | Passed/failed Playwright journeys |
| Accessibility automation | axe results by tested state |
| Semantic regression | ARIA snapshot differences |
| Markup | v.Nu results |
| Content rules | Vale results |
| Responsive behavior | Tested viewport/device matrix |
| Browser compatibility | Relevant Playwright/browser results |
| UI states | Coverage of loading/error/empty/partial/success/timeout states |
| Inclusion | Cohorts considered and outstanding evidence |
| Cognitive accessibility | COGA-informed review findings |
| AI behavior | HAX review where relevant |
| Safety | Sensitive interaction review |
| Manual gaps | Exact checks still requiring expert/users/assistive technology |
| Known UX debt | Open defects and rationale |
| Council exceptions | Explicitly accepted trade-offs |
 
That format is important because an automated agent should make **claims proportional to the evidence it has**.
 
## Recommended target configuration
 
I would build the first version with surprisingly few moving pieces.
 
| Component | Initial implementation |
|---|---|
| **UX agent constitution** | Your custom system prompt + decision hierarchy + Council escalation policy |
| **Australian authority KB** | Current DTA Digital Experience corpus + APS Experience Design Principles + Australian Government Style Manual |
| **Accessibility KB** | WCAG 2.2 + WAI evaluation guidance + ARIA APG + COGA |
| **Inclusion/safety KB** | DTA Inclusion guidance + ADII + eSafety + selected AIFS/AIATSIS material |
| **Pattern KB** | NSW Design System + GOV.UK Design System + WAI APG; project design systems dynamically added |
| **AI UX KB** | Microsoft HAX |
| **Retrieval** | Postgres metadata filters → hybrid keyword/vector retrieval → reranking only when necessary |
| **Web observer** | Chrome DevTools for agents |
| **Journey automation** | Playwright |
| **Accessibility automation** | axe-core through Playwright |
| **Semantic regression** | Playwright ARIA snapshots |
| **Markup validation** | v.Nu |
| **Content linting** | Vale + your Australian Government style pack |
| **Framework linting** | `eslint-plugin-jsx-a11y` when JSX is present |
| **Component environment** | Storybook when justified by the solution |
| **Visual craft skill** | Anthropic `frontend-design`, invoked conditionally |
| **Design representation** | Working code + design tokens + machine-readable UX Contract |
| **Visual design application** | None initially; Penpot only when human visual collaboration justifies it |
| **Observability** | Langfuse traces tagged with UX decision/evidence IDs |
| **Artifacts/versioning** | GitHub alongside code |
| **Runtime** | Existing Modal/Railway/Oracle environment; no specialized UX infrastructure required |
 
This stack is unusually compatible with your cost objective. Vale, v.Nu, Playwright, axe-core and framework linters can run as ordinary local/CI processes; the browser can be provisioned inside the same disposable environments already intended for coding agents. Chrome's agent tooling provides a direct browser-observation interface rather than requiring you to invent one. citeturn15search0turn15search5turn19search0turn19search3
 
I would **not** initially add a dedicated vector store, heavyweight design SaaS, separate usability-testing platform, or collection of overlapping accessibility scanners. pgvector is sufficient for this corpus size; redundancy among automated WCAG scanners will add more output than insight. Where your architecture should spend sophistication is on **authority metadata, evidence provenance, deterministic acceptance tests and escalation rules**.
 
The strongest version of this agent is therefore not “an LLM that knows a lot about UX.” It is a small decision system whose model is surrounded by authoritative Australian guidance, research-backed interaction precedents, project-specific evidence and deterministic test machinery.
 
Its preferred reasoning sequence should effectively be:
 
> **Who is the person, and what are they trying to achieve? → What evidence do we actually have? → Who could be excluded or harmed? → What rules constrain us? → Has this problem already been solved and tested? → What is the simplest suitable interaction? → How will we prove the implementation preserves that experience?**
 
That philosophy is closely aligned with the current Australian Government direction: understand users, design inclusively from the outset, reuse what already works, provide flexible channels, build trust, do no harm and continuously evaluate the resulting service. citeturn21search4turn21search6turn21search11turn21search15
