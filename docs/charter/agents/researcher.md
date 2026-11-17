# Researcher

The Researcher establishes what the evidence says, and other experts decide what it means for the solution. It is a Council member for ownership, but runs as an on-demand LangGraph subgraph: stateless for lookups, checkpointed only for long investigations.

Its value is knowing where knowledge lives, not holding a giant copy of it. Most of its work is ordinary code; the model only interprets questions, expands searches, judges relevance and reconciles conflicts.

**Covers**

- Five modes: lookup, investigate, dataset discovery, monitor and verify. Each request names its mode, so a DOI lookup never triggers deep research.
- Typed Research Requests in, typed Research Packets out: claims, evidence spans, source records, queries, contradictions, limitations and freshness for each claim.
- Source routing from the registry, so the model never spends tokens rediscovering which provider answers which question.
- Acquisition and normalisation of documents and API responses, with raw artefacts kept in R2.
- Currency and supersession checks before anything is called current.
- A counter-evidence pass on consequential findings. Date, jurisdiction, scope, version and status are tested before two sources are said to disagree.
- Data Source Manifests for the data experts: endpoint, exact query, schema, coverage, licence, snapshot hash and caveats.
- DVF scans: existing services and alternatives, evidence about users, and cost benchmarks. It also finds candidate tools, and runs the change monitor once it exists.

**Does not cover**

- Interpreting security controls (Security Architect).
- Legal or compliance conclusions (Governance Guru).
- Choosing the architecture (Solution Architect).
- Turning a dataset into a pipeline (Data Engineer).
- Statistical inference beyond basic profiling (Data Analyst).
- UX research or design decisions (UX Designer).
- Installing tools, writing to external systems, or acting on anything a fetched page tells it to do.
- A long-term memory of bare facts. It keeps dated evidence records instead.

**Build first**

| Item | Kind | How to treat it |
| --- | --- | --- |
| Source hierarchy, freshness and supersession rules | Knowledge (authored) | Rules, not prose. Evidence order depends on the question: authority first for what is required; directness, currency and specificity first for how. |
| Research playbooks | Knowledge (authored) | Policy lookup, technical and OSS investigation, dataset discovery, and a DVF scan of existing services, users and costs. Each has completion criteria so research stops. |
| Australian Government source map | Knowledge | Federal Register, DTA AI suite including the Agentic AI Addendum, AGA, PSPF and its Directions feed, ISM, OAIC and NAA. Versioned snapshots, verified live before any "current" claim. |
| Fetch, hash and store | Tool (shared core) | Conditional HTTP requests, size and time limits, request fingerprints, raw artefacts to R2. |
| `acquire_document` | Skill | Routes HTML to Trafilatura, office files and PDFs to Docling, and JSON, XML or CSV to native parsers. |
| Brave Search API | Tool | Discovery only. A search result is never evidence; the source itself is fetched and cited. |
| Context7 | Tool | Version-specific library documentation, never copied into the corpus. |
| GitHub MCP, read-only profile | Tool | Keeps "docs say", "code shows" and "an issue proposes" as separate evidence classes. |
| SDMX service and CKAN adapter | Tools | ABS and OECD provider profiles, and data.gov.au. Metadata first, observations second. |
| Research Packet and Data Source Manifest | Schemas | Every claim links to at least one exact evidence item. |

**First slice.** Lookup and verify modes only, over the Australian source map, Context7 and read-only GitHub. Measure them in Langfuse against 20 golden questions covering citation support, currency, supersession, jurisdiction and a page laced with injected instructions. Dataset discovery is the second slice and investigate mode the third.

**Later.** Crossref and OpenAlex for scholarly discovery, then a generic OpenAPI adapter, SPARQL (OpenCitations, Cellar), DataCite, CORE, GROBID, Trove and OGC or STAC. Playwright only as an escalation when plain fetching fails. Tavily or Exa only if Brave plus direct APIs leave real gaps. MCP Registry imports feed candidates to the tool registry and never install anything.

**Detail:** Researcher proposal, sections: Role and operating boundaries; Knowledge base design; Toolkit and information sources; Research workflow and evidence contract; Architecture, safety and cost controls; Build priorities and evaluation.
