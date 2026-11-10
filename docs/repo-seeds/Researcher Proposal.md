# Proposal for the Researcher Agent in “The Council”
 
## Executive recommendation
 
The Researcher should be built less like a traditional autonomous “expert persona” and more like a **shared evidence-acquisition and evidence-synthesis service** available to every Council member. Logically it can remain a member of The Council; operationally, I would implement it as an **on-demand LangGraph subgraph** that can run cheaply and statelessly for ordinary lookups, acquire its own checkpoint only for longer investigations, and return a strongly typed **Research Packet** rather than merely prose. LangGraph explicitly supports stateless subgraphs as lightweight subagents as well as checkpointed subgraphs for work that needs durable execution or human interruption. citeturn18search1turn18search0
 
This distinction matters. Most of what a good Researcher needs to do is not reasoning:
 
**discover → retrieve → parse → normalize → identify → deduplicate → filter → rank → verify currency → attach provenance → hand off**
 
Only a relatively small portion should require model inference:
 
**interpret an ambiguous question → formulate additional searches → judge contextual relevance → reconcile apparently conflicting evidence → synthesize an answer**
 
That makes the Researcher unusually well suited to your deterministic-first philosophy. LangGraph itself is designed to mix deterministic and LLM-driven steps within the same graph, so this need not be simulated with an agent loop. citeturn18search5
 
My highest-level recommendations are:
 
| Recommendation | Proposed approach | Why |
|---|---|---|
| **Implement Researcher as a Council service/subgraph** | Spawn it on demand from Solution Architect, Governance Guru, Security Architect, Data Analyst, Data Engineer, UX Designer, or coding agents | Research is cross-cutting, but it usually does not require a continuously active persona or its own persistent conversational state. LangGraph supports exactly this subgraph pattern. citeturn18search1 |
| **Make the fundamental output an evidence object, not an answer** | Return claims, evidence excerpts, source metadata, source authority, retrieval time, identifiers, contradiction flags, and optionally a narrative synthesis | Other experts can inspect the actual evidence rather than inheriting an opaque Researcher conclusion. This is especially important for an Australian Government-oriented agentic system where accountability and traceability matter. The Australian Government Agentic AI Addendum calls for traceable agent actions, documented records and explicit accountability for external data and tools. citeturn17view2 |
| **Use protocol adapters rather than dozens of bespoke tools** | Build generic SDMX, SPARQL, OpenAPI/REST, CKAN, OAI-PMH, RSS/Atom, GitHub, and OGC/STAC capabilities, then configure providers | ABS, OECD and other statistical providers expose standardized interfaces; CKAN similarly exposes a common Action API, while OGC and STAC standardize major classes of geospatial discovery. citeturn19view8turn19view9turn14search0turn15search0turn15search5 |
| **Treat the knowledge base primarily as an authority map plus curated high-value corpus** | Keep Australian Government rules, standards, research methodology and tool documentation locally; retrieve volatile facts and datasets live | For example, the September 2026 ISM material and a PSPF Direction issued on 29 September 2026 demonstrate that government security guidance can change close to the point of use. citeturn17view6turn17view3 |
| **Build a private tool/source registry** | Mirror approved entries from the official MCP Registry, add native APIs and internal tools, security-review them, and expose only allow-listed capabilities to Researcher | The official MCP Registry is useful for discovery but remains in preview and explicitly does **not** security-scan server code itself; that is delegated to package registries and downstream aggregators. citeturn20search1 |
| **Prefer structured retrieval before web search** | Identifier lookup/API → structured catalogue → lexical search → semantic search → broad web search → browser automation | This generally produces more reproducible queries, cleaner provenance and lower token consumption. ABS and OECD, for example, expose both data and structural metadata programmatically. citeturn19view8turn19view9 |
| **Make provenance first-class** | Raw artifact in R2; normalized representation, metadata, provenance and vectors in Neon/Postgres; trace operations in Langfuse | W3C PROV provides a domain-independent model for provenance, while Langfuse traces can capture model calls, retrievals and API/tool operations. citeturn11search0turn18search11 |
| **Do not turn the Researcher KB into a giant copy of the internet** | Persist authoritative reference material, source manifests, previous evidence packets and useful cached artifacts; leave academic literature, statistics, technical docs and the general web primarily on demand | This reduces staleness, ingestion cost and the tendency to treat retrieved historical text as current truth. |
| **Separate research from domain decisions** | Researcher says *what the evidence says*; Security Architect decides security architecture; Governance Guru interprets governance implications; Data Analyst performs substantive analysis | This preserves clear ownership and lets Council members challenge an evidence packet without challenging a second expert's hidden reasoning. |
 
One small terminology point: I have treated your proposed **“Content7” as Context7**. Context7 is the Upstash project intended to provide current, version-specific software documentation and examples to coding agents, with MCP and agent-skill interfaces. It is a strong fit for this system. citeturn1search0turn1search4
 
The Researcher I would build therefore looks approximately like:
 
> **Council member asks question → Research Router → deterministic source selection → source-specific retrieval workers → normalization/provenance → evidence ranking → contradiction/currentness checks → optional model synthesis → typed Research Packet → requesting Council member**
 
Notably, most of those “workers” should be ordinary code, not more LLM agents.
 
## Role and operating boundaries
 
### The Researcher should be a capability, not a general-purpose oracle
 
The Australian Government's current Agentic AI Addendum describes an agentic system as having an orchestration layer that coordinates agents, governs tool use, provides human oversight and applies security and governance across the workflow. It specifically calls for responsibilities to be assigned to agents while accountability remains attributable to humans, including where third-party tools and external data are involved. citeturn17view1turn17view2
 
That maps surprisingly well to your Council model. I would give the Researcher explicit responsibility for **evidence**, not authority over every subject it can research.
 
| Researcher should own | Researcher should not own |
|---|---|
| Finding candidate authoritative sources | Final interpretation of security controls |
| Determining which retrieved material actually answers the research question | Final legal/compliance determination |
| Verifying publication, update, version and supersession information | Selecting the application's architecture |
| Acquiring documents and structured data | Transforming exploratory data access into a production data pipeline |
| Normalizing metadata and identifiers | Statistical inference beyond basic validation/profiling |
| Detecting disagreements between sources | Deciding which Council expert “wins” a policy disagreement |
| Comparing evidence and describing uncertainty | UX research/design decisions |
| Maintaining citations and retrieval provenance | Writing production application code |
| Reproducing API/search queries | Giving a coding agent unrestricted authority because “research says so” |
| Passing structured datasets to the Data Analyst/Data Engineer | Becoming a generic browser with unrestricted credentials |
| Finding technical documentation, implementations and OSS precedents | Automatically installing an MCP server merely because it appears in a registry |
 
A useful operating maxim would be:
 
> **Researcher establishes the evidentiary state of the world; domain experts decide what that evidence means for the solution.**
 
### Research modes
 
I would expose four task classes rather than one unconstrained `research()` tool.
 
| Mode | Typical request | Model use | Output |
|---|---|---:|---|
| **Lookup** | “What is the current requirement for X?” / “What does ABS call this measure?” | None or minimal | One or more authoritative evidence items |
| **Investigate** | “Compare approaches to X and identify current best-supported options.” | Moderate | Multi-source Research Packet with synthesis |
| **Dataset discovery** | “Find authoritative Australian unemployment data at SA4 level.” | Minimal | Dataset/dataflow candidates, metadata, reproducible query and samples |
| **Monitor** | “Tell Governance Guru if this standard changes.” | Normally none | Change event with old/new hashes and affected source record |
 
A fifth internal mode, **verify**, is useful whenever another Council member presents an assertion: it searches specifically for supporting, contradicting and superseding evidence rather than conducting a broad investigation.
 
This prevents Researcher from automatically using the most expensive workflow. “What is the DOI for this paper?” should not launch an LLM-driven deep-research process when Crossref can answer it deterministically. Crossref exposes publicly available scholarly metadata through its REST API and supports direct DOI retrieval, filters, facets and searches without requiring registration. citeturn19view0
 
### How other Council members should invoke it
 
The caller should supply a typed **Research Request** rather than an unconstrained natural-language message.
 
| Field | Example | Purpose |
|---|---|---|
| `question` | “What Australian Government requirements affect storage of AI-generated decision records?” | Actual research target |
| `requester` | `GovernanceGuru` | Provenance and routing |
| `jurisdiction` | `AU/Commonwealth` | Determines authority hierarchy |
| `as_of` | `2026-10-02` | Prevents accidental use of superseded material |
| `decision_context` | “Prototype intended for later agency deployment” | Helps assess relevance |
| `source_policy` | `primary_preferred` | Controls evidence threshold |
| `freshness` | `current` | Forces live authoritative verification |
| `depth` | `lookup / investigate / exhaustive` | Cost control |
| `output` | `claims_and_sources / dataset_manifest / full_packet` | Avoids unnecessary synthesis |
| `constraints` | “public sources only; no browser login” | Safety |
| `max_cost` | Internal cost tier | Lets the graph decide whether Tavily/Exa/stronger model/reranker is justified |
 
The requester does **not** need to know whether ABS happens to be SDMX or OpenCitations happens to offer SPARQL. That mapping belongs to a deterministic **source router**.
 
### Handoff to Data Analyst and Data Engineer
 
I would tighten one aspect of your preliminary concept: Researcher should generally **not directly create a long-running “data stream”** for downstream agents.
 
It should instead return a **Data Source Manifest**. For example:
 
| Manifest element | Why it matters |
|---|---|
| Provider and dataset/dataflow identifier | Stable identity |
| Canonical endpoint and protocol | Reproducibility |
| Exact query/parameters | Data Analyst can reproduce exploration |
| Schema/data-structure definition | Data Engineer can build ingestion safely |
| Dimension/codelist metadata | Prevents semantic mistakes |
| Geographic/time coverage | Suitability |
| Update schedule or observed update behavior | Pipeline design |
| Authentication | Operational implications |
| Rate/response limits | Engineering implications |
| Licence/attribution | Governance |
| Retrieval time | Auditability |
| Snapshot hash | Reproduction |
| Sample payload | Validation |
| Known provider caveats | Risk |
| Researcher's relevance assessment | Why it was selected |
 
That is particularly suitable for SDMX. ABS's Data API supports data plus structural metadata and currently provides XML, JSON and CSV representations through an SDMX 2.1-compliant interface; OECD similarly exposes data and structural metadata through an SDMX-based API. citeturn19view8turn19view9
 
Researcher performs **discovery**. Data Engineer decides how it should become an enduring pipeline. Data Analyst decides how to analyze it.
 
## Knowledge base design
 
I would split the Researcher's knowledge into **five materially different collections**. Treating them all as interchangeable vector-store chunks would discard valuable semantics.
 
### Core epistemic and procedural knowledge
 
This is the highest-value bespoke material for you to create because it encodes *how your system researches*, rather than facts it can retrieve elsewhere.
 
| Knowledge asset | What to encode | Why it belongs locally |
|---|---|---|
| **Source hierarchy** | Jurisdiction-specific rules for primary, official, scholarly, secondary and community sources | Deterministic authority selection |
| **Research playbooks** | Policy lookup, literature search, technical investigation, statistics discovery, vendor/product research, OSS investigation | Reduces repeated reasoning |
| **Freshness policy** | Which question classes require live verification | Prevents stale KB material from masquerading as current truth |
| **Supersession rules** | Current/in-force/superseded/draft/archive/withdrawn/deprecated statuses | Crucial for legislation, policy and technical APIs |
| **Evidence rules** | Direct evidence vs inferential support vs contextual evidence | Better synthesis |
| **Contradiction protocol** | Search for scope/date/version/jurisdiction differences before declaring a true conflict | Reduces false disagreements |
| **Identifier rules** | DOI, ORCID, ROR, ISSN, CELEX, government publication IDs, Git commit/release identifiers, SDMX dataflows, etc. | Deterministic entity resolution |
| **Citation contract** | Every decision-relevant claim links to evidence and original artifact | Explainability |
| **Research completion criteria** | What “enough evidence” means for lookup vs investigation | Prevents endless browsing |
| **Council escalation matrix** | Security evidence → Security Architect; privacy/records → Governance; data quality → Analyst/Engineer; architecture → Solution Architect | Keeps expert boundaries clear |
 
I would **not** implement a single numerical “trust score” generated by an LLM. Instead use a mostly deterministic evidence ordering such as:
 
**authority → directness → status/currentness → temporal applicability → specificity → corroboration → contextual relevance**
 
A Commonwealth Act does not become less authoritative than a blog because a language model assigns the blog a 0.93 “quality score.”
 
### Australian Government core corpus
 
This is where local ingestion is most worthwhile. These materials are repeatedly relevant to what your Council is likely to construct, and several are precisely the sources that other agents need Researcher to locate and quote accurately.
 
| Corpus/source family | Recommendation | Researcher use |
|---|---|---|
| **Federal Register of Legislation** | **Must index/source-map; verify live before consequential use.** | The Register is the authorized whole-of-government source for Commonwealth legislation and includes full text, lifecycle information and relationships between laws. citeturn19view7 |
| **Australian Government Architecture** | **Ingest.** | Gives Researcher a map of whole-of-government digital architecture guidance that can be surfaced to Solution Architect. DTA describes AGA as shared architecture guidance/artifacts supporting government digital alignment. citeturn3search0turn3search36 |
| **Digital Service Standard** | **Ingest and version.** | Repeatedly relevant to service design, accessibility, measurement, inclusion and public/staff-facing government services. The current Standard sets requirements for high-quality government digital services. citeturn3search1turn3search13 |
| **Data and Digital Government Strategy** | **Ingest.** | Useful context for determining government strategic alignment. citeturn2search14 |
| **Policy for the responsible use of AI in government** | **Must ingest and monitor.** | Direct relevance to anything AI-enabled; the updated policy took effect on 15 December 2025. citeturn9search0turn9search1 |
| **AI Technical Standard** | **Must ingest and monitor.** | Provides lifecycle practices for Australian Government AI systems and complements the responsible-AI policy and impact-assessment requirements. citeturn10search3turn10search31 |
| **Agentic AI Addendum** | **Must ingest and monitor.** | Especially important for *The Council itself*. The DTA's addendum, last updated 4 June 2026, explicitly addresses secure and governed implementation of agentic systems. citeturn17view0 |
| **AI Impact Assessment materials** | **Ingest.** | Useful for Governance Guru and Solution Architect when proposed systems involve government AI use. Current guidance requires assessment of in-scope use cases and ongoing governance for higher-risk uses. citeturn10search1turn10search28 |
| **Protective Security Policy Framework** | **Must ingest/version/monitor.** | PSPF Release 2026 prescribes Australian Government requirements across six security domains. citeturn17view7 |
| **PSPF Directions and Advisories** | **Monitor as a high-priority feed.** | New directions can materially affect technology choices. Direction 002-2026 was published on **29 September 2026**, only days before this report, illustrating why “we indexed PSPF once” is inadequate. citeturn17view3 |
| **ASD Information Security Manual** | **Must ingest/version/monitor.** | ASD's September 2026 material describes the ISM as a risk-based cyber-security framework for IT and OT; its guidelines span the system lifecycle. citeturn17view6 |
| **OAIC Australian Privacy Principles and AI privacy guidance** | **Must ingest/version.** | The 13 APPs cover personal-information lifecycle obligations; OAIC also provides specific AI/privacy guidance. citeturn2search6turn9search2 |
| **National Archives of Australia information/AI guidance** | **Must ingest.** | Particularly significant for a research agent: NAA states that AI-generated content created or received by Australian Government agencies constitutes Commonwealth records and must be managed accordingly. citeturn17view4 |
| **API.gov.au guidance/catalogue** | **Ingest guidance; query catalogue live.** | The whole-of-government API guidance treats API descriptions as technical contracts and specifies OpenAPI documentation expectations; the site also provides API discovery and the Definitions Catalogue. citeturn17view5turn4search1turn4search15 |
| **data.gov.au** | **Do not bulk-ingest datasets; index via CKAN API.** | data.gov.au exposes CKAN package search, allowing the Researcher to find datasets through structured catalogue queries rather than web scraping. citeturn16search1turn14search0 |
| **ABS API documentation and metadata** | **Ingest connector docs; query observations live.** | ABS's API is freely accessible without an API key, is SDMX 2.1-compliant and exposes detailed statistics plus metadata, but ABS itself warns its beta API may not always contain the most current information. That caveat belongs in your provider profile. citeturn19view8 |
| **Trove API** | **Source registry + live retrieval.** | Useful when research moves into historical Australian newspapers, gazettes and cultural collections; API v3 supports machine-readable search across multiple Trove categories. citeturn4search2turn4search16 |
 
The important architectural distinction is that “in the knowledge base” need not mean “every page embedded forever.” For legislation, PSPF Directions and similar sources, the local KB should hold **authority metadata and cached/versioned artifacts**, while Researcher verifies the current authoritative source at execution time.
 
### Research-method and scholarly-source knowledge
 
You do not need to ingest the scholarly literature. You need an excellent map of how to search it.
 
I would locally retain:
 
| Material | Content |
|---|---|
| Query-design playbooks | Boolean/field searching, synonym expansion, identifier search, backward/forward citation chaining |
| Evidence-type taxonomy | Systematic review, RCT, observational study, benchmark, position paper, technical report, preprint, standard, etc. |
| Retraction/correction workflow | Check publication identifiers and post-publication metadata before relying on important papers |
| Literature-search templates | Technology comparison, policy question, empirical-effectiveness question, state-of-the-art survey |
| Extraction templates | Research question, population/context, method, sample, result, limitation, citation |
| Citation-chain procedures | Seed paper → cited works → citing works → related topics/authors/institutions |
| Research-object identifiers | DOI/ORCID/ROR/ISSN/DataCite identifiers and normalization logic |
| “No paper says this” discipline | Distinguish explicit findings from Researcher's inference |
 
Crossref is valuable here because it exposes publisher-deposited bibliographic metadata, including licences, funding, ORCID/ROR identifiers and post-publication updates. citeturn19view0 OpenAlex adds a connected graph spanning works, authors, institutions, sources and topics and supports direct DOI/ORCID/ROR/ISSN lookups as well as filtering and search. citeturn19view1
 
### Tool and source registry
 
This may ultimately be more valuable than the document vector store.
 
Create a first-class `source_registry`/`tool_registry` in Postgres, with records such as:
 
| Metadata | Example |
|---|---|
| `source_id` | `abs_sdmx` |
| `source_class` | `official_statistics` |
| `authority` | Australian Bureau of Statistics |
| `jurisdiction` | AU |
| `protocol` | SDMX 2.1 |
| `discovery_capability` | dataflows / structures |
| `retrieval_capability` | observations / metadata |
| `auth_type` | none |
| `structured` | true |
| `freshness_strategy` | live |
| `preferred_for` | Australian official statistics |
| `fallbacks` | ABS website |
| `rate_limit` | Provider metadata |
| `data_limit` | Provider metadata |
| `licence` | Provider metadata |
| `sensitive_capability` | false |
| `tool_id` | `sdmx.query` |
| `allowed_callers` | Researcher, Data Analyst |
| `security_review` | approved |
| `version_checked_at` | timestamp |
| `health_checked_at` | timestamp |
| `docs_artifact` | R2/document ID |
 
This registry is where Researcher's deterministic router gets its intelligence. It should answer:
 
> “For an official Australian population series, which provider and which tool should I try first?”
 
without calling an LLM.
 
### Do not create an unqualified long-term “fact memory”
 
I would resist the temptation to let Researcher accumulate extracted facts in pgvector and later retrieve them as though they remained true.
 
Instead, persist **Evidence Records**:
 
`claim → source → evidence span → published/updated date → retrieved date → valid time → source authority → version/status → transformation provenance`
 
The W3C PROV family was designed precisely to support interoperable descriptions of provenance and relationships among entities, activities and agents. You do not need full RDF/PROV-O internally, but using a PROV-inspired model will make your evidence history substantially more robust. citeturn11search0turn11search15
 
Your existing infrastructure maps neatly onto this:
 
| Existing component | Researcher use |
|---|---|
| **R2** | Immutable/raw HTML, JSON, XML, CSV, PDF and API-response artifacts |
| **Neon Postgres** | Source registry, document/version metadata, query manifests, evidence records, claims, identifiers |
| **pgvector** | Semantic retrieval over normalized chunks |
| **Postgres lexical search** | Exact terms, identifiers, phrases and deterministic lexical retrieval |
| **LangGraph checkpoints** | Task execution state, not canonical research knowledge |
| **LangGraph shared store / Postgres** | Cross-task source/tool memory where appropriate; LangGraph distinguishes thread checkpoints from cross-thread stores. citeturn18search17 |
| **Langfuse** | Research trace: routing, tool invocations, searches, retrieved artifacts, model calls, cost and evaluation metadata. Langfuse's tracing model supports LLM and non-LLM operations including retrieval and API calls. citeturn18search2turn18search11 |
| **Modal Sandbox** | Untrusted document transformation, browser automation and disposable research utilities |
| **Oracle VM** | Optional local reranking/embedding or batch parsing when it is cheaper than ephemeral execution |
| **GitHub** | Source-controlled provider profiles, research policies, deterministic extractors, evaluation datasets |
 
## Toolkit and information sources
 
The most useful design move is to create **a fairly small number of powerful protocol tools**, then a much larger catalogue of source configurations.
 
Your SDMX and SPARQL ideas are exactly the direction I would take.
 
### Protocol and connector layer
 
| Capability | Priority | Build or reuse | Why it belongs in Researcher |
|---|---:|---|---|
| **HTTP/REST fetcher** | Essential | Custom thin deterministic skill | The universal lowest-cost primitive. Support GET/HEAD, headers, redirects, timeouts, content-type detection, compression, checksums, size limits, caching and conditional requests. |
| **OpenAPI REST caller** | Essential | Generic adapter/MCP | Lets Researcher discover and invoke many documented APIs without bespoke source code. Australian Government API guidance itself is organized around machine-readable OpenAPI descriptions. citeturn17view5 |
| **SDMX client/MCP** | Essential | **Build one generic service**, configure providers | Strong choice from your draft. ABS is SDMX 2.1; OECD also exposes an SDMX API, while IMF and ECB publish SDMX interfaces. citeturn19view8turn19view9turn0search2turn0search3 |
| **SPARQL client/MCP** | Essential | Generic | Excellent for knowledge graphs. OpenCitations exposes separate bibliographic-metadata and citation-index SPARQL endpoints; the EU Publications Office's Cellar can expose publication metadata through SPARQL. citeturn19view5turn13search2turn13search3 |
| **CKAN adapter** | High | Small custom wrapper over CKAN API | Opens data.gov.au and many other CKAN catalogues. CKAN's Action API exposes core catalogue functionality and its DataStore can query tabular resources. citeturn14search0turn14search20turn16search1 |
| **OAI-PMH harvester** | Medium-high | Existing library wrapped as tool | Useful for repository metadata and bulk harvesting. DataCite explicitly supports OAI-PMH alongside its APIs. citeturn19view4 |
| **GraphQL client** | Medium | Thin generic tool | Useful where providers expose GraphQL; retain ordinary REST as preferred where possible because schemas and deprecations vary. DataCite, for example, currently offers REST, GraphQL and OAI-PMH interfaces. citeturn19view4 |
| **RSS/Atom watcher** | High | Lightweight custom | Cheap deterministic monitoring for policy/news/release changes where feeds exist; avoids repeatedly asking a model to search sites. |
| **Sitemap/site-map reader** | High | Custom | Useful site discovery before broad crawling; cheap and deterministic. |
| **OGC API / STAC adapter** | Medium-high | Existing client libraries behind a single Researcher tool | Worth adding because government questions frequently become geographic. OGC API Features standardizes web querying of spatial feature data; STAC provides a common searchable description for spatiotemporal assets. citeturn15search0turn15search1turn15search5 |
| **GitHub API / GitHub MCP** | High | **Reuse official GitHub MCP**, read-only Researcher profile | Very useful for researching OSS implementation, releases, source, issues and examples. GitHub's official MCP server exposes repository/code capabilities; its REST API is separately versioned and documented. citeturn14search3turn14search1 |
| **Browser automation** | High but escalated | Microsoft Playwright MCP | Use only where ordinary HTTP/API retrieval fails because of JavaScript or interaction. Microsoft's Playwright MCP provides browser automation and can operate against browser state. citeturn14search2 |
 
I would expose these to the LLM as relatively **high-level semantic tools**, not every underlying operation.
 
For example, instead of giving Researcher 42 raw SDMX functions:
 
`search_statistical_catalog(provider, query)`  
`describe_dataset(provider, id)`  
`query_statistics(provider, dataset, dimensions, period)`  
`validate_statistical_query(...)`
 
Internally those functions can remain deterministic.
 
### Statistical sources
 
Your local SDMX MCP can become one of the most valuable Researcher services.
 
| Provider | Suggested use | Notes |
|---|---|---|
| **ABS** | Australian demographic, economic, labour, census and social statistics | The current Data API is SDMX 2.1 compliant, freely accessible without an API key and returns XML/JSON/CSV. ABS warns the beta service can change and may not always be the most current source, so Researcher should retain that caveat and be capable of falling back to the ABS site. citeturn19view8 |
| **OECD** | International comparison, policy, economic and social data | OECD provides free programmatic data access using SDMX and exposes structural metadata alongside data. citeturn19view9 |
| **IMF** | Macroeconomic, financial and international data | IMF currently documents SDMX interfaces and also offers DataMapper for common country/indicator retrieval. citeturn0search2turn0search6 |
| **ECB** | Monetary/economic/financial data | ECB data services support SDMX REST access. citeturn0search3turn0search31 |
| **Other SDMX providers** | Add through configuration rather than new code | The provider profile should map base endpoint, SDMX version, quirks, licensing, limits and preferred output format. |
 
I would make the service **metadata-first**. Before asking for observations, Researcher should inspect the Data Structure Definition/codelists and validate dimension values. This is less glamorous than asking an LLM to construct a query, but considerably more reliable.
 
### Scholarly and research infrastructure
 
I would not select one “research API.” Their strengths are complementary.
 
| Service | Priority | Primary job |
|---|---:|---|
| **Crossref** | Essential | DOI resolution and publisher-deposited bibliographic metadata. Its REST API includes work, journal, member, funder and licence metadata and post-publication updates. citeturn19view0 |
| **OpenAlex** | Essential | Broad scholarly discovery and graph traversal. It represents works, authors, institutions, sources and topics and accepts established identifiers directly. citeturn19view1 |
| **OpenCitations** | Essential | Open citation graph and bibliographic relations; perfect fit for your proposed SPARQL MCP, and it also exposes REST interfaces. citeturn19view5turn13search1 |
| **DataCite** | High | Datasets, software and other DOI-identified research outputs in addition to conventional publications; REST API supports querying/browsing DOI metadata and OAI-PMH supports harvesting. citeturn19view4 |
| **CORE** | High | Open-access research-paper/full-text discovery; especially useful after metadata services identify a work. CORE describes its corpus as aggregating research outputs from repositories and journals. citeturn6search3turn6search11 |
| **Semantic Scholar** | Medium | Additional academic-graph search, citations and recommendations. Useful as a second discovery system rather than a mandatory dependency. Its official APIs expose Academic Graph, recommendation and dataset services. citeturn6search2turn6search6 |
 
A sensible literature workflow would therefore be:
 
**OpenAlex discovery → Crossref/DataCite identifier and metadata normalization → OpenCitations citation expansion → publisher/repository/full-text retrieval → Researcher extraction**
 
rather than repeatedly performing Google-like web searches.
 
### Australian information-discovery tools
 
| Tool/source | Include? | Rationale |
|---|---:|---|
| **Federal Register of Legislation** | Essential | Authoritative Commonwealth legislation source. Researcher should search and retrieve directly from it whenever a question turns on current Australian legislation. citeturn19view7 |
| **data.gov.au CKAN API** | Essential | Structured discovery of government datasets. The site's current CKAN `package_search` endpoint supports text/filter queries, facets, pagination and result metadata. citeturn16search1 |
| **API.gov.au catalogue** | High | Discovery path for Australian Government APIs plus government API design/definitions material. citeturn4search1turn4search3 |
| **Australian Government Definitions Catalogue** | High | Useful for resolving semantic meaning before passing data to Data Analyst/Data Engineer. It exposes a public read-only API for government data definitions. citeturn4search15 |
| **Trove API** | High | Adds historical newspapers, gazettes, magazines, works and cultural collections to Researcher's search surface. citeturn4search2turn4search16 |
| **ABS Data API** | Essential | Primary structured statistical source for Australian questions. citeturn19view8 |
| **DTA/digital.gov.au live source search** | Essential | AI, digital standards and architecture are sufficiently changeable that authoritative live pages should always be available in addition to local ingestion. The Agentic AI Addendum itself was introduced as an addition to the broader AI Technical Standard. citeturn17view0 |
| **cyber.gov.au** | Essential | Current ASD security guidance and ISM material. The current ISM guidance page was published/updated in September 2026. citeturn17view6 |
| **protectivesecurity.gov.au** | Essential | PSPF and directions. Recent 2026 directions demonstrate why monitoring is valuable. citeturn17view3turn17view7 |
| **OAIC** | Essential | Authoritative privacy guidance and APP interpretation. citeturn2search6turn9search2 |
| **National Archives of Australia** | Essential | Records/information-management implications of Council and application outputs. citeturn17view4 |
 
For Commonwealth legislation I would **not invent or depend on an unofficial API simply for architectural neatness**. Treat the Federal Register as a specialized authoritative web source unless/until you identify and validate an official structured interface that meets the need.
 
### Technical research and OSS
 
This deserves a specialized path because your Researcher will frequently be asked things like “Can library X actually do this?” or “Has someone implemented Y already?”
 
| Tool | Recommendation | Why |
|---|---|---|
| **Context7** | **Definitely retain.** | Current/version-specific library documentation is exactly the sort of information that should not be frozen into your KB. Context7 is designed to provide current code documentation/examples through agent interfaces. citeturn1search0turn1search4 |
| **Official GitHub MCP** | **Add, initially read-only for Researcher.** | Gives direct access to repositories/code/issues/PR-related material without making the Researcher invent browser searches. citeturn14search3 |
| **GitHub REST API fallback** | Add behind the same Researcher abstraction | Useful for deterministic repository metadata and files; GitHub documents both repository and repository-content endpoints. citeturn14search5turn14search17 |
| **Release/tag watcher** | Custom deterministic skill | Lets Researcher answer “what changed?” and monitor dependencies without an LLM repeatedly reading changelogs. |
| **Repo snapshot/search tool** | Run in Modal sandbox | For deeper OSS research: shallow clone, exact text search, inspect package manifests, licence, examples and tests. Keep it read-only and disposable. |
 
Researcher should have a separate concept of:
 
**documentation says feature exists**  
versus  
**source code shows implementation**  
versus  
**issue/PR discusses proposed behavior**
 
Those are different evidence classes.
 
### Web search
 
There will always be questions for which no known structured source exists, so a general search capability remains necessary.
 
I would use a **search cascade**, not bind your architecture to one vendor:
 
| Tier | Option | Role |
|---|---|---|
| Primary | **Brave Search API** | Conventional indexed web discovery with a relatively simple search API; Brave currently offers monthly free API credit. citeturn7search0turn7search4 |
| Self-hosted/fallback | **SearXNG** | Useful low-infrastructure-cost metasearch option; the project is open-source and aggregates multiple search services. citeturn7search3 |
| Research escalator | **Tavily** | Optional when you want higher-level agent-oriented search/retrieval rather than implementing all search plumbing yourself; its current service includes a free monthly credit allowance. citeturn7search2turn7search6 |
| Semantic/deep discovery | **Exa** | Optional for semantic/web-content discovery where traditional keyword search performs poorly. citeturn7search1turn7search5 |
 
Given your cost objective, I would start with **Brave + direct source APIs**, possibly add SearXNG, and only route to Tavily/Exa when ordinary discovery does not resolve the question. Agentic search vendors effectively charge you for doing part of the research orchestration you are already building.
 
Search-engine output should **never itself count as evidence**. It is discovery metadata. Researcher should fetch and cite the actual source.
 
### Document acquisition and extraction
 
This is another area where it is worth having multiple implementations hidden behind one Researcher capability.
 
| Input | Preferred extraction path | Tool recommendation |
|---|---|---|
| Ordinary HTML | HTTP fetch → boilerplate removal | **Trafilatura**; its official documentation supports downloading/crawling and extraction of main text and metadata. citeturn8search2 |
| Complex/JS site | Browser/crawler after ordinary HTTP failure | **Crawl4AI** or Playwright; Crawl4AI supports JS-oriented crawling and structured/Markdown extraction, including MCP integration. citeturn8search0turn8search8 |
| PDF/DOCX/PPTX/HTML/image | General document converter | **Docling**; it supports multiple office/document formats and extraction of structure such as tables, reading order and formulas. citeturn8search1turn8search37 |
| Scholarly PDF | Academic-structure extraction | **GROBID**, which is specifically designed to restructure scholarly publications into structured TEI XML. citeturn8search3 |
| JSON/XML/CSV | Native parser | Do not send it through an LLM or document converter |
| API docs/OpenAPI | Schema parser | Parse OpenAPI directly |
| RDF | RDF parser/SPARQL | Preserve graph structure rather than flattening immediately |
| Large tabular files | Data tool / Data Analyst handoff | Researcher profiles enough to identify the dataset; do not stuff every row into model context |
 
I would expose a single tool such as:
 
`acquire_document(uri, purpose, preferred_representation)`
 
and let deterministic routing select Trafilatura, Docling, GROBID, Playwright or a native structured parser.
 
### Tool discovery itself
 
You asked whether the Researcher may search/identify information **or tools available to it**. I strongly recommend making this an explicit subsystem.
 
The official MCP Registry now provides a centralized metadata repository and REST API for publicly accessible MCP servers, including standardized `server.json` installation/configuration metadata and namespace verification. However, as of October 2026 it is still described as **preview**, and its own documentation says the Registry delegates actual package security scanning rather than certifying the safety of listed server code. citeturn20search1turn20search5
 
Therefore:
 
**Do use the MCP Registry for discovery. Do not let Researcher dynamically install arbitrary discovered MCP servers.**
 
Build a small **Council Tool Registry**:
 
| Lifecycle | Action |
|---|---|
| `discovered` | Found in MCP Registry/GitHub/vendor documentation |
| `candidate` | Capability appears useful |
| `reviewed` | Source/authorship/licence/dependencies/security assessed |
| `sandbox_only` | Can be trialed in disposable Modal environment |
| `approved_read` | Available to Researcher for read operations |
| `approved_write` | Explicitly approved state-changing operations |
| `deprecated` | No new tasks |
| `blocked` | Known inappropriate/unsafe |
 
MCP's own distinction between **tools**, **resources** and **prompts** is also useful when designing your internal catalogue: tools are model-invoked operations, resources expose context/data, and prompts provide templates. citeturn1search1turn1search7turn1search5
 
For many knowledge providers you do **not** need a full MCP server. A static API/resource adapter is simpler, cheaper and easier to secure.
 
## Research workflow and evidence contract
 
The Researcher's quality will depend more on this workflow than on its system prompt.
 
### A deterministic-first graph
 
I would implement approximately these stages:
 
| Stage | Default implementation | LLM required? | Key output |
|---|---|---:|---|
| **Classify request** | Rules + schema fields | Sometimes | Research mode/domain |
| **Resolve jurisdiction/time** | Deterministic | No | Scope |
| **Select source classes** | Source registry/routing table | No | Ordered source plan |
| **Resolve known identifiers** | DOI/SDMX/legislation/GitHub etc. | No | Canonical entities |
| **Generate initial queries** | Templates | Usually no | Search queries |
| **Expand ambiguous concepts** | Model | Sometimes | Additional synonyms/queries |
| **Discover candidates** | APIs/catalogues/search | No | Candidate sources |
| **Acquire artifacts** | HTTP/API/browser | No | Raw artifacts |
| **Extract/normalize** | Parsers | No | Normalized records |
| **Deduplicate** | IDs/canonical URI/hash | No | Unique evidence |
| **Check source status** | Metadata/rules | No | Current/superseded/etc. |
| **Retrieve evidence spans** | Lexical/vector retrieval | No | Candidate passages |
| **Assess relevance** | Filters + optional model/reranker | Sometimes | Relevant evidence |
| **Search for contradiction** | Rules + query generation | Sometimes | Counter-evidence |
| **Construct claims** | Model or deterministic mapping | Often | Claim/evidence graph |
| **Check claims against evidence** | Entailment/review pass | Often | Support status |
| **Synthesize** | Model | Only if requested | Narrative |
| **Package and persist** | Code | No | Research Packet |
 
The important economy here is that **a model should not spend tokens rediscovering what your router already knows**.
 
For instance, when it sees:
 
`jurisdiction=AU + intent=official_statistics`
 
the first candidate source class can deterministically be ABS. Only after ABS fails or proves unsuitable should broad search occur.
 
### The Research Packet
 
I would make this the formal contract between Researcher and The Council.
 
A packet should contain at least:
 
| Field | Meaning |
|---|---|
| `research_question` | Normalized question actually investigated |
| `request_context` | Who asked and why |
| `as_of` | Point in time to which answer applies |
| `scope` | Jurisdiction, domain, exclusions |
| `answer` | Optional concise synthesis |
| `claims[]` | Atomic propositions |
| `evidence[]` | Evidence supporting/contradicting claims |
| `sources[]` | Canonical source records |
| `queries[]` | API/search queries issued |
| `artifacts[]` | Raw cached documents/responses |
| `dataset_manifests[]` | Structured data candidates |
| `contradictions[]` | Unresolved disagreements |
| `limitations[]` | Gaps |
| `freshness` | Fresh/current/stale/unknown per important claim |
| `confidence_basis` | Why Researcher considers evidence sufficient |
| `escalations[]` | Issues needing another Council expert |
| `trace_id` | Langfuse/LangGraph trace reference |
| `cost` | Requests, tokens, paid search usage, execution cost |
 
Each claim should connect to **one or more exact evidence items**.
 
That permits a Solution Architect to consume the summary while Governance Guru can drill through to the authoritative text.
 
### Source records should preserve temporal provenance
 
At minimum:
 
| Metadata | Why |
|---|---|
| Canonical URI | Identity |
| Publisher/authority | Source ranking |
| Title | Human readability |
| Source class | Legislation/policy/data/paper/etc. |
| Jurisdiction | Applicability |
| Publication date | Temporal evidence |
| Updated date | Temporal evidence |
| Retrieved date | Reproduction |
| Valid-from / valid-to | Where knowable |
| Version | Supersession |
| Current status | Current/draft/superseded/deprecated/etc. |
| Content hash | Detect change |
| ETag/Last-Modified | Cheap monitoring |
| Licence | Reuse |
| Identifiers | DOI/SDMX/etc. |
| Extractor/version | Transformation provenance |
| Raw R2 artifact | Original evidence |
| Normalized artifact | Searchable form |
| Evidence offsets | Exact support |
| Parent/source relationship | Provenance |
| Security/data classification | Controls |
 
DCAT is worth looking at when representing source/catalog metadata because W3C defines it specifically for interoperable data catalogues, while PROV provides the provenance model. citeturn11search1turn11search0
 
Again, I would borrow their semantics rather than requiring every internal operation to become RDF.
 
### Currentness should be tested, not assumed
 
This deserves its own deterministic stage.
 
The ABS API documentation, for example, explicitly warns that its beta API can lag the main ABS website and can change. citeturn19view8 The OECD warns that omitting a dataset version may select the latest structure, but newer structure versions can contain non-backward-compatible changes. citeturn19view9 Australian Government security policy can similarly move quickly: PSPF Direction 002-2026 was published on 29 September 2026. citeturn17view3
 
Therefore each provider profile should say how to establish currentness.
 
A source cached six months ago can still be perfectly useful for semantic retrieval; it simply cannot be the **final authority for a “current requirements” claim** until revalidated.
 
### Contradiction should be a deliberate search operation
 
Research systems commonly stop when they find support. Your Researcher should have a specific **counter-evidence pass** for consequential findings.
 
Before declaring that two authorities disagree, test:
 
**different date? → different jurisdiction? → different scope? → normative requirement vs recommendation? → different version? → different population/system? → primary vs secondary interpretation?**
 
Only then classify the disagreement as substantive.
 
Where genuine disagreement remains, return both positions rather than forcing an artificial consensus. The requesting Council member can escalate to the Chair.
 
### Raw evidence should sometimes be preferred to synthesis
 
Your preliminary thinking here is sound.
 
Researcher should be able to return:
 
`RAW_EVIDENCE`  
`STRUCTURED_FINDINGS`  
`SYNTHESIS`
 
and choose the cheapest sufficient representation.
 
Examples:
 
| Request | Best return |
|---|---|
| “What is the exact current control wording?” | Evidence span + source, little synthesis |
| “Give Data Analyst the series.” | Data Source Manifest + data |
| “Compare three implementation approaches.” | Structured findings + synthesis |
| “Does this library support feature X in current version?” | Version-specific docs/source evidence |
| “Find all papers meeting these criteria.” | Bibliographic records first; narrative only if asked |
 
This should materially reduce both hallucination opportunity and token consumption.
 
## Architecture, safety and cost controls
 
### A proposed Researcher graph
 
Within your current stack, I would structure the subgraph conceptually as:
 
```text
Research Request
      │
      ▼
┌────────────────────┐
│ Scope / policy gate│
└─────────┬──────────┘
          ▼
┌────────────────────┐
│ Deterministic      │
│ source router      │
└─────────┬──────────┘
          │
      fan-out
    ┌─────┼─────────┬───────────┐
    ▼     ▼         ▼           ▼
  SDMX  SPARQL    REST/API    Search
    │     │         │           │
    └─────┴──────┬──┴───────────┘
                 ▼
        Acquire / normalize
                 │
                 ▼
        Deduplicate / identify
                 │
                 ▼
        Authority + freshness
                 │
                 ▼
        Evidence retrieval
                 │
          ┌──────┴──────┐
          │ sufficient? │
          └───┬─────┬───┘
             yes    no
              │      └────► query expansion /
              │             browser / broader search
              ▼
       Counter-evidence pass
              │
              ▼
        Claim/evidence map
              │
        optional LLM synthesis
              │
              ▼
          Research Packet
              │
        Council / coder caller
```
 
This is preferable to:
 
> “Here are twenty-five MCP tools; Researcher, reason your way through them.”
 
because the latter burns model tokens just deciding what deterministic code could decide once.
 
### Stateless by default, stateful when justified
 
For short lookups, compile the Researcher subgraph without its own checkpointer. LangGraph explicitly describes this as the lightweight option for a subagent that behaves like a function and does not need pause/resume recovery. For longer investigations, give the subgraph its own checkpoint namespace so that intermediate work and human-interrupt points are durable. citeturn18search1turn18search9
 
Useful persisted state is:
 
**what the current research task has done**
 
rather than:
 
**everything Researcher has ever believed**.
 
Cross-task knowledge belongs in your source/evidence store, not hidden conversational memory.
 
### Determinism and idempotency
 
Network requests, raw snapshots and expensive retrievals should be discrete checkpointable tasks. LangGraph's current guidance recommends isolating side effects and non-deterministic operations into tasks and making operations idempotent so replay does not cause unintended duplicate work. citeturn18search10
 
For Researcher this suggests:
 
`request fingerprint = source + method + normalized parameters + relevant headers + auth scope`
 
Then:
 
1. check permitted cache,
2. execute request,
3. persist raw response,
4. record hash/timestamp/status,
5. return artifact ID.
A resumed graph can reuse the artifact instead of refetching it.
 
### Security model for research tools
 
The Researcher is likely to become one of the Council's **largest attack surfaces** because it reads arbitrary external content and operates many connectors.
 
MCP maintains dedicated security guidance precisely because servers, tools, authorization and externally sourced resources introduce security concerns. citeturn1search15 The DTA's current Agentic AI Addendum similarly emphasizes governed tools, defined permissions, external-system accountability, monitoring and human intervention around higher-risk agent actions. citeturn17view1turn17view2
 
I would implement these controls from the beginning:
 
| Control | Researcher policy |
|---|---|
| **Fetched content is data, never instructions** | Documents cannot modify system/tool policy |
| **Read-only by default** | Researcher GitHub, databases and government APIs get read access unless an explicit use case proves otherwise |
| **Tool allow-list** | Only approved Tool Registry entries exposed |
| **Capability filtering** | A GitHub MCP does not need PR creation simply because the server offers it |
| **Domain/egress policy** | Connectors declare allowed network destinations |
| **No arbitrary local shell** | Use narrowly scoped deterministic utilities; arbitrary code execution occurs only in disposable sandbox |
| **Sandbox browser/crawlers** | Untrusted JS/documents isolated from Council host |
| **Response-size limits** | Prevent accidental multi-GB fetches/context attacks |
| **Timeout/request budgets** | Protect cost and orchestration |
| **Secret isolation** | Tools receive only credentials they require |
| **Prompt-injection boundary** | Extracted page instructions never enter privileged control fields |
| **Raw artifact preservation** | Allows later audit of what Researcher actually saw |
| **External-tool attribution** | Evidence records capture which connector produced data |
| **High-impact intervention gate** | Research itself can be autonomous; actions that modify an external system require separately authorized capability |
 
The Australian Government guidance specifically states that oversight should cover the overall agentic system, including third-party agents/tools, and calls for intervention processes around irreversible or high-risk actions. citeturn17view2
 
### Records and privacy
 
This is particularly relevant to your Australian Government context.
 
If this architecture eventually operates inside an Australian Government agency, research packets, prompts, evidence selections and generated analyses cannot simply be treated as disposable model exhaust. The National Archives states that AI-generated material created or received by Australian Government agencies constitutes Commonwealth records under the Archives Act framework and must be managed accordingly. citeturn17view4
 
Researcher's artifact schema should therefore include fields that make later information-management policies possible rather than impossible:
 
`classification`  
`personal_information`  
`retention_class`  
`project`  
`agency/context`  
`disposal/retention status`  
`access restrictions`
 
The Researcher itself should not decide the records authority—that belongs with Governance—but it should produce recordable objects.
 
Similarly, personal-information-bearing research must be capable of invoking stricter handling because the Australian Privacy Principles govern collection, use/disclosure, quality, access/correction and associated handling of personal information. citeturn2search6
 
### Observability
 
You already selected Langfuse, and Researcher is an excellent use case.
 
Langfuse traces can capture prompts, model responses, tool calls and causal relationships, while its data model supports metadata, environments, releases and tags; its evaluation facilities can attach programmatic or human scores to traces/dataset runs. citeturn18search2turn18search6turn18search8
 
I would tag every research trace with:
 
| Tag/metadata | Example |
|---|---|
| `research_mode` | `lookup` |
| `requester` | `security_architect` |
| `domain` | `australian_government_security` |
| `jurisdiction` | `AU` |
| `source_classes` | `ASD, PSPF` |
| `deep_search_used` | false |
| `browser_used` | false |
| `llm_query_expansion` | true |
| `evidence_count` | 7 |
| `contradiction_count` | 1 |
| `freshness_required` | current |
| `cache_hit_ratio` | metric |
| `research_policy_version` | commit/version |
| `tool_registry_version` | commit/version |
| `packet_id` | evidence-store identifier |
 
This lets you later ask questions such as:
 
> “Why is Researcher suddenly twice as expensive?”
 
or:
 
> “How often does it invoke browser automation for ABS questions?”
 
instead of merely inspecting anecdotes.
 
### Cost ladder
 
I would encode a cost ladder into the graph:
 
| Escalation | Method | Cost |
|---|---|---:|
| A | Existing verified Research Packet/cache | Lowest |
| B | Exact identifier / Postgres lookup | Very low |
| C | Direct structured API call | Very low |
| D | Provider catalogue/full-text lexical search | Low |
| E | Cached semantic/vector retrieval | Low |
| F | Public search API | Low–moderate |
| G | Fetch and deterministic extraction | Low–moderate |
| H | Local reranking | Compute |
| I | Cheap-model relevance/query expansion | Tokens |
| J | Browser automation | Compute/time |
| K | Multiple parallel open-web searches | API + compute |
| L | Strong-model contradiction/synthesis | Highest model cost |
 
The graph should stop as soon as the evidence threshold for the requested research mode is satisfied.
 
That alone is likely to matter more to operating cost than optimizing the Researcher's system prompt.
 
## Build priorities and evaluation
 
### What I would build first
 
The following sequence should produce a highly useful Researcher without turning the initial implementation into another platform project.
 
| Phase | Build | Rationale |
|---|---|---|
| **Foundation** | `ResearchRequest`, `Source`, `Evidence`, `Claim`, `ResearchPacket`, `DatasetManifest` schemas | Everything else becomes testable once the data contract is stable |
| **Foundation** | Source/Tool Registry in Neon | Central deterministic routing and governance mechanism |
| **Foundation** | HTTP acquisition + R2 artifact persistence + hashes | Universal evidence primitive |
| **Foundation** | HTML/document normalization | Turns sources into inspectable evidence |
| **Foundation** | Postgres lexical + pgvector evidence retrieval | Uses infrastructure you already intend to run |
| **Core research** | Search API adapter | Covers unknown/open-web questions |
| **Core research** | OpenAPI/REST adapter | Broadest structured source coverage |
| **Core research** | Generic SDMX service | ABS/OECD/IMF/ECB immediately provide substantial value. ABS and OECD both expose SDMX interfaces. citeturn19view8turn19view9 |
| **Core research** | Generic SPARQL service | OpenCitations and Cellar become available through one abstraction. citeturn19view5turn13search2 |
| **Core research** | CKAN adapter | data.gov.au plus other CKAN catalogues. citeturn16search1turn14search0 |
| **Core research** | Crossref + OpenAlex | High-quality scholarly discovery and metadata normalization with modest implementation effort. citeturn19view0turn19view1 |
| **Technical research** | Context7 | Live/versioned docs rather than stale embeddings. citeturn1search0 |
| **Technical research** | Official GitHub MCP, read-only profile | OSS/code research. citeturn14search3 |
| **Australian corpus** | DTA AI suite, AGA, DSS, PSPF, ISM, OAIC, NAA, legislation source map | Highest-frequency government context |
| **Extraction expansion** | Docling + GROBID + JS/browser fallback | Handle increasingly awkward source material. citeturn8search1turn8search3 |
| **Source expansion** | DataCite, OpenCitations REST/SPARQL, CORE, Trove, OGC/STAC | Broadens Researcher beyond conventional web/document research |
| **Monitoring** | Conditional fetch/hash/feed/change pipeline | Makes volatile authority sources sustainable |
| **Tool discovery** | MCP Registry importer → private candidate registry | Lets you continuously discover new capabilities without granting them automatically. citeturn20search1 |
 
### The initial approved toolkit I would actually deploy
 
If constraining the first implementation, my concrete shortlist would be:
 
| Tool/capability | First release? | Notes |
|---|---:|---|
| HTTP fetch | **Yes** | Fundamental |
| Search API | **Yes** | Brave initially |
| Context7 | **Yes** | Strong technical-research ROI |
| SDMX MCP | **Yes** | ABS + OECD + IMF + ECB provider profiles |
| SPARQL MCP | **Yes** | OpenCitations + Cellar provider profiles |
| OpenAPI/REST tool | **Yes** | Broad gateway |
| CKAN adapter | **Yes** | data.gov.au |
| Crossref adapter | **Yes** | DOI/bibliographic authority |
| OpenAlex adapter | **Yes** | Scholarly discovery |
| Federal Register source skill | **Yes** | Australian Government priority |
| Australian Government authoritative-site router | **Yes** | DTA/ASD/PSPF/OAIC/NAA |
| Docling | **Yes** | General document extraction |
| Trafilatura | **Yes** | Cheap HTML path |
| GitHub MCP, read-only | **Yes** | OSS investigation |
| Playwright MCP | **Yes, escalated only** | Complex web retrieval |
| DataCite | Second wave | Research datasets/software |
| OpenCitations | Second wave, unless SPARQL makes it trivial | Citation graphs |
| CORE | Second wave | OA full-text |
| Semantic Scholar | Optional | Useful redundancy, but OpenAlex already covers much of initial need |
| Trove | Second wave | Very useful Australian historical research |
| OGC/STAC | Second wave | Important once geospatial work emerges |
| Crawl4AI | Optional | Add when ordinary HTML + Playwright patterns prove inadequate |
| GROBID | Second wave | Excellent if scholarly PDF extraction volume becomes material |
| Tavily | Optional escalator | Avoid paying for duplicated orchestration initially |
| Exa | Optional escalator | Add when semantic web discovery justifies it |
| SearXNG | Optional infrastructure optimization | Attractive once search volume makes self-hosting worthwhile |
| MCP Registry discovery | **Yes** | Search tool candidates, but do not auto-install |
 
### Evaluation suite
 
Before calling the Researcher “expert,” I would construct a fixed benchmark spanning the types of work you realistically expect it to perform.
 
The most important metrics are not “did the answer sound good?”
 
| Evaluation | What it measures | Example failure |
|---|---|---|
| **Authoritative-source selection** | Correct source hierarchy | Cites consultant blog instead of ASD |
| **Citation entailment** | Evidence actually supports claim | Source is related but does not say what Researcher claims |
| **Citation completeness** | Decision-relevant claims have evidence | Architecture recommendation appears without support |
| **Currentness accuracy** | Uses current/in-force material | Retrieves superseded standard |
| **Supersession detection** | Recognizes replaced material | Treats old API/policy as live |
| **Jurisdiction accuracy** | Correct governmental scope | State guidance presented as Commonwealth requirement |
| **Source-type accuracy** | Correctly identifies law/policy/guidance/opinion | Recommendation described as mandate |
| **Contradiction recall** | Finds material counter-evidence | Stops after first confirming source |
| **Dataset reproducibility** | Data Analyst can repeat retrieval | Dataset found but exact series/query lost |
| **Identifier resolution** | DOI, dataset, legislation etc. correctly canonicalized | Merges similarly titled papers |
| **Extraction fidelity** | Parser retained relevant text/tables | Critical footnote omitted |
| **Research completeness** | Meets declared depth | “Exhaustive” literature request searches one API |
| **Escalation correctness** | Knows its domain boundary | Researcher makes legal conclusion itself |
| **Tool routing efficiency** | Uses cheapest appropriate path | Launches Playwright for a JSON API |
| **LLM avoidance rate** | Deterministic steps stay deterministic | Model used to parse JSON |
| **Unsupported claim rate** | Hallucination control | Claim has no evidence edge |
| **Cost per resolved request** | Operational efficiency | Small lookups trigger strong model repeatedly |
| **Latency per request class** | Usability | Identifier lookup behaves like deep research |
| **Cache effectiveness** | Reuse | Same immutable paper downloaded repeatedly |
| **Human acceptance/correction** | Real utility | Experts frequently reject evidence packet |
 
Langfuse is already capable of grouping traces and attaching evaluation scores, dataset experiments and human feedback, so these can become a regression suite rather than an occasional manual audit. citeturn18search8turn18search16
 
### Suggested benchmark questions
 
Your golden test set should deliberately include adversarially similar tasks:
 
| Test family | Example |
|---|---|
| Current Australian rule | “What current Australian Government guidance applies to agentic AI oversight?” |
| Recent change | “Have PSPF technology requirements changed recently?” |
| Legislation | “What is the authoritative current Commonwealth law concerning X?” |
| Statistical series | “Retrieve Australia's quarterly series for X and document every dimension.” |
| International comparison | “Compare Australian measure X with OECD measure Y; are the definitions actually equivalent?” |
| Scholarly search | “Find the strongest recent evidence for X, including contradictory studies.” |
| Publication verification | “Is this paper corrected/retracted/updated?” |
| Technical capability | “Does current library X support Y?” |
| OSS evidence | “Is feature X released or merely proposed in an issue?” |
| Dataset discovery | “Find official Commonwealth/state data on X.” |
| Historical AU research | “Find primary historical reporting concerning X.” |
| Contradiction | Give it a plausible false premise and see whether it challenges it |
| Superseded source | Seed search with an old standard and test whether it detects replacement |
| Prompt injection | Put malicious instructions in a fetched page and verify they remain inert |
| Tool safety | Expose read and write GitHub tools and verify research routes only to read |
| Cost | Repeat a previously researched immutable question and ensure it uses cache |
 
### The resulting Researcher
 
The core design principle is that **the Researcher should know where knowledge lives more than it “knows” the knowledge itself**.
 
Its proprietary value to your system is not a gigantic embedding collection. It is the combination of:
 
**authority map + source registry + protocol adapters + research procedures + provenance model + deterministic routing + evidence contracts + escalation rules + evaluation set.**
 
That lets the Researcher remain useful even as sources, APIs, standards and models change.
 
It also creates a useful asymmetry within The Council. The Security Architect can have a relatively focused security corpus. Governance Guru can have a relatively focused governance corpus. Researcher does **not** need a comparable encyclopedic corpus because its expertise is chiefly **epistemic and connective**: knowing what source should answer a question, how to interrogate it, how to determine whether the result is current and authoritative, and how to hand the evidence to whichever Council expert is competent to act on it.
 
For your particular infrastructure, the proposed end state is therefore:
 
| Layer | Recommended implementation |
|---|---|
| **Orchestration** | Researcher LangGraph subgraph; stateless for lookup, checkpointed for investigations |
| **Deterministic routing** | Postgres Source/Tool Registry |
| **Stable knowledge** | Curated procedural + Australian Government corpus in Neon/R2 |
| **Lexical retrieval** | Postgres |
| **Semantic retrieval** | pgvector |
| **Raw evidence** | R2 |
| **Statistics** | Generic local SDMX service |
| **Knowledge graphs** | Generic SPARQL service |
| **General APIs** | OpenAPI/REST adapter |
| **Government catalogues** | CKAN adapter + API.gov.au/source profiles |
| **Scholarly discovery** | Crossref + OpenAlex initially; DataCite/OpenCitations/CORE expansion |
| **Technical documentation** | Context7 |
| **OSS research** | Official GitHub MCP with Researcher read-only toolset |
| **Open web discovery** | Brave first; SearXNG/Tavily/Exa as optional layers |
| **HTML extraction** | Trafilatura |
| **Complex web** | Playwright/Crawl4AI, sandboxed |
| **General documents** | Docling |
| **Scholarly PDF structure** | GROBID |
| **Geospatial** | OGC/STAC adapter when required |
| **Tool discovery** | Official MCP Registry → private reviewed Tool Registry |
| **Provenance** | PROV-inspired Evidence/Artifact model |
| **Observability/evaluation** | Langfuse |
| **Untrusted execution** | Modal Sandboxes |
| **Local reranking/heavier processing** | Oracle VM endpoint over your private Tailscale path |
| **Human/Council intervention** | LangGraph interrupts for genuinely consequential ambiguity; LangGraph supports persisted interrupt/resume workflows. citeturn18search0 |
 
Most importantly, this architecture gives you a Researcher that can grow horizontally. Adding a new statistical agency is usually a **provider configuration**, not a new agent. Adding another RDF knowledge graph is a **SPARQL source record**, not a new tool. Adding an OpenAPI-described government service is primarily **registration and policy**, not new reasoning. Adding an MCP server is a **reviewed Tool Registry entry**, not an unpredictable expansion of the model's authority.
 
That is the approach most consistent with your stated aims of **low infrastructure cost, deterministic processing wherever practical, limited hallucination exposure, transparent decision-making, and a Council capable of producing near-production-fidelity solutions before final human expert review**.
