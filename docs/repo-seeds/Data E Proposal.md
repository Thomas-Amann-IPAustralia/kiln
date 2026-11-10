# Proposal for the Data Engineer Agent in “The Council”
 
## Executive proposal
 
The Data Engineer should not primarily be designed as an agent that “knows lots of data-engineering facts.” It should be designed as a **data-systems planning, inspection, transformation, validation, and assurance agent** with a relatively small authoritative knowledge base, access to current technical documentation, and a substantial deterministic toolbelt.
 
A more useful role definition than the draft would be:
 
> **Data Engineer:** Converts data requirements and the actual characteristics of source data into implementable, testable, observable, and reversible data architectures and pipelines. It is responsible for discovering and profiling data; designing schemas, storage layouts, transformations, ingestion and migration processes; specifying data-quality controls, contracts, lineage and provenance; and validating that resulting datasets retain the intended meaning and integrity. It prefers deterministic inspection and execution over inference and escalates questions of data meaning, privacy, security classification, retention, analytical methodology, or system-wide architecture to the appropriate Council member.
 
That scope corresponds well to contemporary data engineering: data engineers deal not merely with ETL, but with storage, integration, processing, quality, pipelines, architectures and reliable access to data. IBM's current data-management material usefully covers these areas as a broad orientation, although I would treat it as background rather than as an authoritative specification. citeturn2view0
 
The most important design recommendation is to distinguish **four different kinds of “knowledge”**, rather than putting everything into one vector database:
 
| Layer | What belongs there | How the agent should access it | Examples |
|---|---|---|---|
| **Normative knowledge** | Obligations, standards, policies, principles | Versioned local corpus with strict metadata and source precedence | NAA Information Management Standard, OAIC APP guidance, DATA Scheme, PSPF |
| **Engineering knowledge** | Stable concepts and your preferred engineering patterns | Curated local KB and executable playbooks | Idempotency, schema evolution, data-quality dimensions, dimensional/normalized modeling, migration patterns |
| **Fast-changing product knowledge** | APIs, configuration, syntax, version behavior | Retrieve live/version-specific official documentation at runtime | DuckDB, Polars, dbt, dlt, Neon, R2, orchestration tools |
| **Project knowledge** | Schemas, samples, contracts, ADRs, profiling results, decisions | Project workspace, Git repository, Neon metadata tables and artifacts | `schema.sql`, data dictionary, profiling report, migration plan, validation output |
 
This separation matters. Context7, for example, is much more valuable as a **live technical-documentation retrieval capability** than as something whose contents are copied into your vector store. Its MCP implementation is explicitly intended to provide current/version-specific library documentation and code examples, using library resolution followed by scoped documentation queries. Its own recommended usage is for framework, SDK, API, CLI and cloud-service questions rather than general business logic. citeturn12search12turn12search19
 
My recommended initial Data Engineer stack is consequently quite small:
 
| Function | Default |
|---|---|
| Dataset inspection/querying | **DuckDB** |
| DataFrame transformations | **Polars** |
| Columnar interchange | **Apache Arrow / PyArrow** |
| Analytical file format | **Parquet** |
| Programmatic ingestion | **dlt** |
| SQL parsing/analysis | **SQLGlot** |
| SQL linting | **SQLFluff** |
| Deterministic data assertions | **Native SQL/Polars assertions first; Great Expectations when a persistent quality framework is warranted** |
| Document → structured data | **Docling**, with Apache Tika as a complementary file/content extractor |
| Personal-information screening | **Presidio**, strictly as a detector rather than proof that data is safe |
| Record/entity linkage | **Splink** |
| Current documentation | **Context7 + primary official documentation fallback** |
| Lineage standard | **OpenLineage** when persistent pipelines warrant it |
| SQL transformation projects | **dbt OSS** when the problem is genuinely dbt-shaped |
| Large object-store tables | **Apache Iceberg**, only after Parquet alone becomes insufficient |
| Change-data capture | **Debezium**, only when CDC is actually required |
| Workflow orchestration | **Prefect or Dagster** for solutions that need it; do not introduce an orchestrator merely because the Council itself uses LangGraph |
 
This is deliberately biased toward tools that can run locally or in a Modal sandbox and that compose well with your existing Postgres/R2 architecture.
 
## Role, authority and Council boundaries
 
### What the Data Engineer should actually own
 
The agent should own the path between **“here is some data”** and **“here is a trustworthy, maintainable data subsystem ready for implementation.”**
 
Its primary responsibilities should be:
 
| Area | Data Engineer responsibility | Typical artifact |
|---|---|---|
| Data discovery | Determine what actually exists rather than trusting descriptions | Inventory, file manifest, source-system map |
| Profiling | Establish schema, types, volume, nullness, cardinality, distributions and anomalies | Machine-readable profile + human summary |
| Data modeling | Design physical/logical structures appropriate to workload | ERD/schema, keys, constraints, partition strategy |
| Ingestion | Design repeatable extraction/loading from files, APIs, databases and object stores | Ingestion specification |
| Transformation | Convert source structures into required structures without losing semantics | Transformation DAG/specification |
| Data quality | Turn assumptions into executable checks | Assertions/expectation suite |
| Data contracts | Define what downstream consumers may rely upon | Versioned schema/interface contract |
| Schema evolution | Determine compatibility and migration implications | Schema diff + migration plan |
| Migrations | Plan reversible movement or restructuring of data | Dry-run results, migration and rollback scripts |
| Storage | Recommend database/file/table representation based on observed workload | Storage decision record |
| Performance | Measure rather than guess where feasible | Benchmark report and query plan |
| Provenance | Record origin and transformation history | Lineage/provenance metadata |
| Unstructured → structured conversion | Extract text/tables/entities and construct proposed structure | Extraction result plus confidence/exception report |
| Entity resolution | Identify likely duplicate/matching entities where no reliable key exists | Linkage model, thresholds and review set |
| Retention implementation | Implement an approved retention rule | Lifecycle/retention configuration |
| Pipeline operability | Make pipelines idempotent, observable, recoverable and testable | Runbook and operational checks |
 
This goes beyond “large datasets.” A 50 MB CSV with malformed dates, duplicate people, unstable identifiers and personal information may need considerably more Data Engineer attention than a clean 500 GB Parquet dataset.
 
### Where it should stop
 
A major risk in a Council architecture is that every capable agent slowly becomes a generalist. Explicit ownership boundaries will improve both reasoning quality and escalation behavior.
 
| Question | Primary Council owner | Data Engineer's role |
|---|---|---|
| “What does this field **mean** to the business?” | Human / domain expert; sometimes Data Analyst | Detect ambiguity; do not invent semantics |
| “Is this statistically valid?” | Data Analyst | Produce and transform required data |
| “Which KPI or analytical methodology is correct?” | Data Analyst | Implement the agreed definition |
| “May we legally collect/share/retain this?” | Governance Guru | Surface the data flows and relevant triggers |
| “Is this personal information / what privacy obligations apply?” | Governance Guru | Detect potential personal information and map where it flows |
| “What security classification applies?” | Security Architect / information owner | Preserve and propagate classification metadata |
| “What security controls are sufficient?” | Security Architect | Implement agreed controls in data systems |
| “Should the overall solution use Postgres, event streaming, an object lake, etc.?” | Solution Architect, advised by Data Engineer | Present evidence and data-specific trade-offs |
| “How should the interface collect or present this information?” | UX Designer | Advise on data constraints and validation |
| “Can we rely on this external dataset/source?” | Researcher + Governance where necessary | Inspect technical characteristics and provenance |
 
This separation is particularly important in an Australian Government setting. For example, the National Archives' Information Management Standard applies to Australian Government business information in **both structured and unstructured form**, including information managed through outsourced arrangements. It requires information to remain findable, interpretable, trustworthy, appropriately retained, securely stored and accountably destroyed or transferred. citeturn22view1 The Data Engineer therefore needs enough records-management knowledge to detect these issues, but deciding the agency's legal retention authority remains a governance responsibility.
 
Similarly, the OAIC's current APP guidance includes separate requirements/guidance around collection, use and disclosure, cross-border disclosure, quality, security, access and correction of personal information. citeturn22view2 The Data Engineer should be able to say *“this architecture transfers personal information through service X in jurisdiction Y and maintains copies A, B and C”*. It should not autonomously decide *“therefore APP 8 does not apply.”*
 
### Autonomy and mandatory escalation
 
A useful rule is:
 
> **The Data Engineer may autonomously make reversible engineering choices inside previously agreed constraints; it must escalate choices that change the meaning, legal status, exposure, durability, external interface, or irreversible state of data.**
 
I would encode this as a deterministic policy rather than merely putting it in the prompt.
 
| Situation | Agent authority |
|---|---|
| Profile a read-only dataset | Autonomous |
| Infer candidate types/schema | Autonomous; label them inferred |
| Create a sandbox copy in an approved environment | Autonomous |
| Convert CSV → Parquet in scratch storage | Autonomous |
| Choose between equivalent Polars/DuckDB implementation approaches | Autonomous |
| Add deterministic tests | Autonomous |
| Benchmark two alternative transformations | Autonomous |
| Repair a pipeline implementation without changing its contract | Autonomous within coding-agent budget |
| Change field semantics | **Escalate** |
| Drop columns/records from an authoritative dataset | **Escalate unless explicitly planned and reversible** |
| Change public or cross-system schema contract | **Escalate** |
| Decide retention/deletion period | **Governance escalation** |
| Discover personal/sensitive information unexpectedly | **Governance + Security escalation** |
| De-identify data for subsequent sharing | **Governance + Security; Data Engineer executes method** |
| Move data across a new jurisdiction/trust boundary | **Security + Governance + Solution Architect** |
| Encounter a new security classification | **Security Architect** |
| Resolve uncertain entity matches that affect rights/entitlements | **Human/domain owner; often Governance** |
| Introduce Kafka/Spark/lakehouse infrastructure not in the approved design | **Solution Architect** |
| Execute destructive production migration | **Human gate regardless of Council consensus** |
 
That last control is worth maintaining even in your present “not genuinely production until reviewed” model. It lets the same Council architecture mature without having to redesign the safety model later.
 
## Recommended knowledge base
 
### Australian Government corpus
 
For your likely workloads, I would make Australian Government information-management material considerably more prominent than the IBM GDPR material in the initial proposal.
 
The National Archives standard is unusually important because its scope explicitly encompasses structured and unstructured information, and its principles cover metadata, preservation, retention, accountable disposal, managed systems, and future access/reuse. citeturn22view1 PSPF Release 2026 is likewise the current Australian Government protective-security framework and sets requirements for protecting government people, information and resources. citeturn22view3 These are exactly the sorts of constraints a data-engineering plan must detect even where another Council member ultimately interprets them.
 
| Knowledge source | Priority | Why the Data Engineer needs it | Retrieval treatment / owner |
|---|---:|---|---|
| **National Archives – Information Management Standard for Australian Government** | **Core** | Defines whole-of-government expectations spanning structured/unstructured information, metadata, storage, preservation, retention, disposal, integrity and reuse. citeturn22view1 | Full local corpus; Governance owns interpretation |
| **Australian Government Recordkeeping Metadata Standard / NAA metadata guidance** | **Core** | Gives the agent a government-specific basis for designing metadata required to identify, understand, manage and preserve records; useful when generating metadata schemas. citeturn1search19turn5search30 | Local/versioned |
| **NAA born-digital file-format standards** | High | Directly relevant when generating or converting government information into durable file formats; the NAA distinguishes born-digital standards from digitisation specifications. citeturn15search8 | Local, tagged by applicability |
| **OAIC Australian Privacy Principles Guidelines** | **Core trigger corpus** | Data pipelines regularly affect collection, disclosure, data quality, security, cross-border handling, access and correction. Current consolidated guidance was updated May 13, 2026. citeturn22view2 | Retrieve only relevant APP chapters; Governance Guru authoritative |
| **OAIC APP 11 guidance** | Core trigger | Particularly relevant to storage, copies, backups, retention and deletion. OAIC guidance requires active measures to secure personal information and addresses destruction/de-identification when it is no longer needed, subject to applicable recordkeeping/legal requirements. citeturn5search0turn5search16 | Governance + Security escalation |
| **OAIC APP 10 guidance** | High | “Data quality” is not solely an engineering concept where personal information is involved; the agent needs to detect when technical quality problems can have privacy consequences. citeturn5search20 | Governance cross-reference |
| **OAIC APP 8 guidance** | High | Makes hosting/data-flow geography a first-class architecture field whenever personal information crosses organisational/geographic boundaries. citeturn5search12 | Do not let DE interpret applicability alone |
| **Data Availability and Transparency Act / DATA Scheme resources** | High | Relevant to Australian Government data sharing and reuse designs; the DATA Scheme was created under the Data Availability and Transparency Act 2022 and operates alongside privacy obligations. citeturn5search1turn5search9 | Governance-led; DE models sharing mechanics |
| **PSPF Release 2026** | **Core trigger corpus** | Data stores, replicas, exports and pipelines need to preserve information-protection constraints. The 2026 PSPF is the current framework. citeturn22view3 | Security Architect owns interpretation |
| **ASD Information Security Manual** | Core trigger / live reference | Technical implementation of government systems may need ISM controls. The ISM is ASD's cybersecurity framework for information and operational-technology systems. citeturn6search32 | Prefer current official retrieval; Security Architect owns |
| **Digital Service Standard / Digital Experience Policy** | Medium | Useful to prevent “back-end only” thinking where a data architecture determines service performance, monitoring, accessibility of data-driven features or user-data handling. The current standard applies across Australian Government digital services. citeturn5search3turn5search35 | Shared Council corpus |
| **Data and Digital Government Strategy** | Medium | Strategic context rather than implementation rules; its 2030 vision emphasizes simple, secure and connected services supported by government data/digital capability. citeturn1search26 | Background |
| **data.gov.au** | Medium | Discovery point for Australian public-sector datasets. citeturn10search8 | Tool/search target rather than fully ingested corpus |
| **ABS metadata guidance and dataset metadata** | Medium | Particularly helpful because the agent should assess fitness-for-purpose and definitions before joining or restructuring official statistics. ABS notes the importance of metadata in determining fitness for purpose. citeturn1search35 | Retrieve with relevant ABS dataset |
| **ARDC metadata/FAIR guidance** | Optional | Useful supplementary material on metadata, provenance and reusable datasets, particularly for research-heavy solutions. citeturn1search11 | Background |
 
I would explicitly **not** make the Data Engineer reproduce all these documents into every answer. Retrieval should be triggered by project facts: Australian Government entity; personal information; records; external sharing; high-value data; public release; cross-border flow; AI-generated government information; and so forth.
 
### Technical corpus
 
The technical KB should concentrate on **principles and decision criteria**, not rapidly aging instructions.
 
| Topic to teach deeply | What it should know |
|---|---|
| Data modeling | Normalization/denormalization, dimensional models, event models, document structures, identifiers, keys, cardinality and constraints |
| Data architecture | Operational vs analytical workloads; database vs warehouse vs object store; batch vs streaming; lake/lakehouse concepts |
| File/data formats | CSV/JSON limitations, Parquet, Arrow, compression, encoding, partitioning, open table formats |
| Pipeline design | Idempotency, retries, checkpointing, incremental loads, watermarks, late data, backfills, replay |
| Schema management | Compatibility, schema inference vs declaration, evolution, migration, contracts, versioning |
| Data quality | Completeness, validity, uniqueness, consistency, timeliness, referential integrity, semantic quality |
| Provenance and lineage | Source identity, transformation version, run identity, data lineage, reproducibility |
| Database engineering | Transactions, indexes, query plans, isolation, constraints, bulk operations, migrations |
| Performance | Predicate pushdown, column pruning, partition pruning, vectorised processing, query profiling, benchmark design |
| Distributed-data fundamentals | Partitioning, skew, shuffle, consistency, delivery semantics — enough to recognize when distributed infrastructure is justified |
| CDC | Log-based changes, ordering, initial snapshots, deletes/tombstones, schema evolution, replay |
| Unstructured processing | Parsing, OCR, document layout, tables, extraction confidence, provenance back to source locations |
| Entity resolution | Deterministic matching, fuzzy/probabilistic linkage, blocking, thresholds, clerical review |
| Privacy-aware engineering | Data minimisation, pseudonymisation, de-identification mechanics, copy proliferation, sensitive-field discovery |
| Records-aware engineering | Retention metadata, immutable provenance, accountable disposal, preservation/export |
| Geospatial fundamentals | Coordinate/reference systems, geometries, spatial indexes, boundary joins and common government geospatial data patterns |
| Data migration | Source/target reconciliation, dual running, cutover, rollback, checksums and exception handling |
| Observability | Freshness, volume, schema, quality, run-state and lineage telemetry |
 
Parquet and Arrow deserve explicit treatment because they form a useful low-cost substrate for agent-produced solutions: Parquet is a column-oriented file format designed for efficient storage/retrieval, while Arrow defines a language-independent columnar memory representation that supports efficient interchange between processing systems. citeturn7search2turn8view2
 
For genuinely large object-store datasets, the agent should also understand when a collection of Parquet files has become a **table-management problem**. Apache Iceberg adds schema evolution, hidden and evolving partitioning, snapshot-based time travel, rollback, atomic changes and concurrent-writing semantics over object-store data. That makes it valuable knowledge, but I would not make it your default storage abstraction: introduce it only where those properties solve a demonstrated problem. citeturn17view0
 
### Assessment of your initial sources
 
| Your proposed source | Recommendation |
|---|---|
| **IBM Data Management Guide** | **Keep.** Good broad orientation/index of concepts. It spans architecture, engineering, integration, pipelines, processing, quality, governance, databases, lakes/warehouses and related subjects. citeturn2view0 Do not treat vendor explanatory prose as the final authority for standards or product behavior. |
| **IBM Guide to AI** | **Do not make it core Data Engineer material.** Keep in a shared Council/Researcher corpus or retrieve when a data pipeline feeds AI systems. The guide is intentionally broad across ML, agents, responsible AI, platforms and AI development. citeturn2view1 |
| **IBM GDPR guide** | **Demote to conditional reference.** GDPR certainly can matter to an Australian solution, but it should be triggered by actual European jurisdiction/data-processing circumstances. The Australian OAIC, NAA, DATA Scheme and protective-security corpus should be materially more prominent in this agent. citeturn2view2turn22view2 |
| **Context7** | **Strongly keep, but as a tool rather than KB content.** Use it for version-aware software/API documentation, with official-source fallback. citeturn12search12turn12search19 |
 
## Toolkit and specialist capabilities
 
### Core local tools
 
These are the tools I would actually install in the standard Data Engineer sandbox image.
 
| Tool | Priority | Give the agent direct execution access? | Why it earns the dependency |
|---|---:|---:|---|
| **DuckDB** | **P0** | **Yes** | Exceptionally useful “Swiss Army knife” for an agent: SQL over CSV, JSON and Parquet; access to external databases and object stores; profiling/query-plan facilities; Arrow/Polars interoperability; and extensions including PostgreSQL, spatial data, Iceberg/Delta and S3-compatible object storage. Current docs also document Cloudflare R2 workflows. citeturn9view0 |
| **Polars** | **P0** | **Yes** | Excellent deterministic transformation engine when SQL becomes awkward. Its Rust-backed query engine provides parallel execution, query optimisation, streaming/out-of-core execution and Arrow interoperability. citeturn8view1 |
| **PyArrow / Apache Arrow** | **P0** | **Yes** | Common interchange layer between data tools and useful for Parquet, columnar schemas, record batches and low-copy interchange. citeturn8view2 |
| **dlt** | **P0** | **Yes** | Particularly well matched to your low-infrastructure model: Python-native ingestion from REST APIs, databases, cloud storage and Python objects, with schema inference, nested-data normalisation, incremental loading, schema evolution and contracts. citeturn10search12turn10search10 |
| **SQLGlot** | **P0** | **Yes** | Gives the agent a deterministic SQL parser/AST rather than asking an LLM to reason from SQL strings. It supports parsing, analysis, dialect translation, table/column extraction, optimisation and AST diffs across many SQL dialects. citeturn20view0 |
| **SQLFluff** | P1 | Yes / CI | Useful as a deterministic quality gate around generated SQL and dbt projects, including dialect-specific linting and pre-commit/CI integration. citeturn21view2 |
| **Great Expectations Core** | P1 | Yes | Use when data-quality rules are becoming a durable product rather than a handful of assertions. GX treats Expectations as verifiable assertions and supports explicit schema and value checks that can fail pipeline checkpoints. citeturn13search9turn13search16 |
| **Docling** | **P0 for document-heavy work** | **Yes** | Strong fit for the “introduce structure to unstructured data” portion of the role. It parses PDF, DOCX, PPTX, XLSX, HTML, email, images and other formats; understands document layout/table structure; emits structured representations; can execute locally for sensitive data; and now exposes MCP and agent integrations. citeturn21view1 |
| **Apache Tika** | P1 | Yes | Complement Docling with robust format/content/metadata detection and extraction across many file types; current Apache Tika 4.x documentation includes supported-format, parsing, content/language detection and configuration facilities. citeturn21view0 |
| **Presidio** | **P0 as a screening tool** | Yes, with warnings | Detect potential personal/sensitive entities in text and structured/semi-structured data before samples are sent elsewhere. It supports regex, NER and custom recognizers and anonymisation operators. Crucially, Presidio itself warns that automated detection does **not** guarantee all sensitive information will be found. citeturn19view0turn19view1 |
| **Splink** | P1 | Yes when invoked | Highly useful in government-style administrative data where reliable identifiers are often absent. Splink performs probabilistic record linkage/deduplication, supports DuckDB and large-data backends, and exposes diagnostics for linkage decisions. It is already used across numerous public-sector linkage projects. citeturn22view0 |
| **Git** | P0 | Yes, repository-scoped | Schemas, migrations, contracts, quality rules and pipeline definitions should be versioned artifacts. In your architecture GitHub is already the logical system of record for these changes. |
 
A significant advantage of DuckDB is that a surprisingly large fraction of “we need a data platform” tasks can first be tested with **SQL + files + a sandbox**. That lets the Data Engineer empirically establish whether something more elaborate is required before the Solution Architect commits to infrastructure.
 
Likewise, Polars should generally be preferred over writing bespoke Python loops for transformations. Its optimizer and streaming engine make “generate a plan, execute it deterministically, inspect the result” a much better agent pattern than asking an LLM to reason row-by-row. citeturn8view1
 
### Pipeline and platform tools the agent should know but not automatically deploy
 
| Tool | Recommendation | Trigger for use |
|---|---|---|
| **dbt OSS** | **Strong conditional recommendation** | SQL-centric analytical transformation projects requiring models, tests, documentation, lineage/contracts and software-engineering workflow. Current dbt OSS provides an open-source runtime and models SQL transformations as managed project artifacts. citeturn8view3turn7search31 |
| **Airbyte** | Connector fallback | Use when the breadth of pre-built connectors saves enough work to justify a larger runtime footprint. Airbyte's current platform centers on open-source data replication and a large connector ecosystem, and exposes programmatic/agent-oriented interfaces. citeturn11view0 |
| **Prefect** | Preferred orchestration candidate for dynamic Python workflows | When a solution needs durable workflow state, retries/recovery, scheduling/event triggers, human approvals or distributed execution beyond simple cron/jobs. Prefect's current platform is Python-oriented and also exposes an MCP server for diagnostics/documentation. citeturn11view2 |
| **Dagster** | Preferred candidate for asset-centric data platforms | When explicit data assets, partitions, lineage, checks and backfills are central architectural concepts. Dagster is designed around those concepts and has increasingly exposed AI/CLI integration mechanisms. citeturn11view1turn12search2 |
| **Apache Airflow** | Know it well; **do not default to it** | Existing Airflow environments or conventional, clearly bounded batch DAGs where its mature provider ecosystem is valuable. Airflow's own documentation characterizes it as a batch-oriented workflow platform. citeturn11view3 |
| **OpenLineage** | Strong standard; deploy once lineage is worth persisting | Open standard for runtime lineage events based around datasets, jobs and runs, with integrations including Airflow, Spark, dbt and Great Expectations. citeturn16view0 |
| **Apache Iceberg** | Architectural option, not default | Large mutable analytical tables on R2/object storage where schema/partition evolution, snapshots, atomic changes or multiple writers become material requirements. citeturn17view0 |
| **Debezium** | CDC specialist | When a solution genuinely needs database change capture rather than periodic incremental queries. Debezium emits ordered row-level change events; PostgreSQL capture can read logical replication, and it may run through Kafka Connect or an embedded/server architecture. citeturn18view0turn18view1 |
| **OpenLineage + a backend such as Marquez** | Optional | When merely recording provenance in pipeline artifacts no longer provides sufficient ecosystem-wide traceability. Marquez is the reference implementation of the OpenLineage API. citeturn16view0 |
 
A useful Council rule would be **“complexity requires evidence.”** Kafka, Spark, Iceberg, Airflow, a separate catalog and a separate data-quality service should never appear in a design merely because they are “data engineering best practice.” The Data Engineer should first demonstrate a requirement that a simpler architecture cannot meet.
 
### Unstructured and semi-structured information
 
This deserves more emphasis than it usually receives in a Data Engineer persona because your own role description specifically includes introducing structure into unstructured data.
 
Docling is now unusually well aligned with agentic pipelines: alongside PDFs it supports office files, spreadsheets, HTML, email, images, audio and other formats; it models page layout, reading order and tables; can emit lossless structured output; and supports local execution, which is useful when information cannot safely leave the environment. citeturn21view1
 
I would establish the following hierarchy:
 
| Input problem | Preferred approach |
|---|---|
| CSV/TSV/JSON/NDJSON | DuckDB/Polars deterministic parser |
| XLSX | Deterministic spreadsheet parsing first; Docling where document semantics/layout matter |
| XML | Schema-aware parser |
| HTML | Structured DOM extraction before LLM |
| DOCX/PPTX | Docling/native parser |
| Digitally generated PDF | Docling structured extraction |
| Scanned PDF/image | OCR + Docling layout processing |
| Unknown binary/document collection | Tika MIME/content/metadata detection first |
| Named personal information | Presidio screening plus project-specific deterministic recognizers |
| Tables with imperfect identifiers | Normalization then Splink where probabilistic entity resolution is warranted |
| Ambiguous semantic extraction | LLM **after** deterministic parsing, with source spans retained |
 
The LLM should therefore usually receive something like:
 
```text
Document
  └─ pages
      ├─ headings
      ├─ paragraphs
      ├─ tables
      ├─ figures
      └─ source coordinates
```
 
rather than simply being handed raw document bytes and asked, “extract the data.”
 
That preserves auditability: each extracted value can retain `source_document_id`, page, table/cell or source span, extractor version, timestamp and — where applicable — confidence.
 
## Deterministic skills and workflows
 
The biggest return on investment may come not from adding more third-party tools, but from wrapping the good ones in **narrow Council skills with typed inputs and outputs**.
 
### Dataset inspection skill
 
I would build one first-class skill called something like `inspect_data_asset`.
 
**Input contract:**
 
```json
{
  "asset_uri": "...",
  "access_mode": "read_only",
  "sample_policy": "safe_default",
  "expected_schema": null,
  "project_data_classification": null
}
```
 
It would deterministically produce:
 
```json
{
  "format": "...",
  "size_bytes": 0,
  "row_count": 0,
  "schema": [],
  "null_profile": {},
  "cardinality_profile": {},
  "candidate_keys": [],
  "duplicate_summary": {},
  "numeric_ranges": {},
  "date_ranges": {},
  "encoding_issues": [],
  "schema_anomalies": [],
  "potential_sensitive_fields": [],
  "quality_flags": [],
  "recommended_next_actions": []
}
```
 
DuckDB and Polars are particularly well suited to implementing most of this without model inference. citeturn9view0turn8view1
 
Only **after** this deterministic report exists should the LLM interpret what is interesting.
 
### Schema and contract skill
 
Build `compare_data_contract` around deterministic parsers rather than language-model comparison.
 
It should perform:
 
1. canonicalization of types;
2. field additions/removals;
3. nullability changes;
4. type widening/narrowing;
5. key/constraint changes;
6. rename candidates;
7. downstream-reference lookup;
8. compatibility classification;
9. generated migration requirements.
SQLGlot is especially useful for SQL-related versions of this problem because it produces an AST, can enumerate tables/columns, translate dialects and calculate semantic differences rather than relying only on text comparison. citeturn20view0
 
A schema change can then be represented as a machine artifact:
 
```json
{
  "compatibility": "breaking",
  "changes": [
    {
      "field": "customer_id",
      "change": "varchar_to_integer",
      "risk": "narrowing_conversion",
      "affected_consumers": ["model_a", "api_b"]
    }
  ],
  "requires_council_review": true
}
```
 
### Data-quality skill
 
Do not start by giving the LLM a blank page and asking it to invent “good quality checks.”
 
Use three tiers:
 
| Tier | Source of rule | Example |
|---|---|---|
| Structural | Automatically derivable | Schema, type, non-null key, uniqueness, referential integrity |
| Statistical/operational | Baseline-derived and explicitly accepted | Volume change, date freshness, cardinality drift |
| Semantic | Human/Council approved | `status = CLOSED` requires `closed_at`; entitlement amount must follow domain rule |
 
Great Expectations is useful once these rules need to exist as declarative, persistent assertions and checkpoints. Its Expectations are explicit verifiable assertions, and its schema validation supports required fields, types, column sets/counts and other checks. citeturn13search9turn13search16
 
For a one-off prototype, however, ten straightforward DuckDB assertions may be substantially simpler than introducing a data-quality framework. The agent should understand that distinction.
 
### Migration skill
 
`plan_data_migration` should automatically generate an ordered assurance structure:
 
| Phase | Required deterministic evidence |
|---|---|
| Baseline | Counts, schema, keys, constraints, hashes/checksums where feasible |
| Dry run | Transformation on representative/sandbox copy |
| Exceptions | Rejected/unconvertible records preserved separately |
| Target validation | Counts, constraints, quality rules |
| Reconciliation | Source ↔ target differences explicitly enumerated |
| Performance | Measured migration duration/throughput on sample |
| Cutover | Ordered operations and dependencies |
| Rollback | Restorable source or known-good snapshot |
| Audit | Tool versions, code commit, timestamps and output artifacts |
 
For migrations involving personal information, records retention, a new hosting location or changed access pattern, the workflow itself should automatically invoke the appropriate Council review rather than relying on the Data Engineer to remember to ask. OAIC guidance treats cross-border disclosure, quality and security as distinct APP concerns, while the National Archives standard requires reliable management through retention and accountable disposition. citeturn22view2turn22view1
 
### Personal-information screening skill
 
Presidio is worth wrapping rather than exposing as an undifferentiated tool:
 
```text
scan_sensitive_data
    |
    +--> deterministic Australian patterns
    |       ABN / ACN / TFN-style patterns where permitted
    |       email / phone / IP / identifiers
    |
    +--> Presidio recognizers
    |
    +--> project-specific dictionary/regex
    |
    +--> sample-based semantic classifier, only where necessary
    |
    +--> "potential sensitive information" report
```
 
The output should **never** say “this dataset contains no PII.” It should say:
 
> “No candidate personal-information entities were detected by configured screening mechanisms.”
 
That distinction is substantive because Presidio's documentation explicitly warns that automated mechanisms cannot guarantee detection of every sensitive item. citeturn19view0
 
A positive result can automatically trigger Governance/Security review; a negative result cannot automatically waive it.
 
### Unstructured extraction skill
 
A reusable `structure_documents` skill could give you significant leverage.
 
It should persist all of:
 
```text
original object
content hash
parser/version
normalized document structure
extracted records
source location for every record
validation status
extraction confidence where applicable
exceptions
transformation commit/version
```
 
Docling can provide much of the deterministic document-structure layer and operates locally, including for sensitive environments. citeturn21view1 Tika provides a useful preceding/fallback layer for content-type, metadata and format handling. citeturn21view0
 
This is an ideal example of your principle of **inference only where inference adds value**:
 
```text
file
 ↓
determine type
 ↓
native deterministic parser
 ↓
layout/table extraction
 ↓
schema mapping
 ↓
deterministic validations
 ↓
LLM resolves only ambiguous fields
 ↓
revalidate
 ↓
human review where confidence/risk requires
```
 
### Entity-resolution skill
 
Splink merits inclusion even if it is infrequently used because the problems it solves are disproportionately common in public administration: people, organisations and addresses recorded differently across systems.
 
Splink links/deduplicates records without requiring unique identifiers and uses probabilistic linkage with inspectable outputs. It supports local DuckDB execution as well as larger backends and is used in numerous government linkage use cases. citeturn22view0
 
The Data Engineer must not turn its match probabilities into ground truth. The skill should output:
 
```text
high-confidence automatic matches
ambiguous matches requiring review
non-matches
thresholds used
features contributing to linkage
model/configuration version
```
 
Where matching can affect rights, eligibility, enforcement or entitlements, the decision threshold itself should be escalated.
 
### Profiling before reasoning
 
A general policy worth hard-coding into the Data Engineer is:
 
> **Never reason about a dataset the agent is permitted to inspect when it could cheaply measure the relevant property instead.**
 
Examples:
 
| Question | Bad agent behavior | Required behavior |
|---|---|---|
| “Is this dataset huge?” | Guess from filename/user description | Measure bytes, rows and column widths |
| “Could `customer_id` be a key?” | Infer from name | Check nullness + uniqueness |
| “Will a join explode?” | Intuit cardinality | Profile join-key cardinalities and execute/sample |
| “Would Parquet be smaller?” | General textbook answer | Convert representative sample and measure |
| “Is this query slow?” | Rewrite based on intuition | `EXPLAIN`/profile/benchmark |
| “Are there duplicates?” | Look at sample | Exact/grouped test or appropriate approximation |
| “Did migration preserve records?” | LLM reviews logs | Automated reconciliation |
| “Does the schema match?” | Compare prose | Parse and diff schemas |
| “Is this file really a PDF?” | Trust extension | Inspect MIME/content |
| “Has personal data been removed?” | Read a few rows | Run configured scan and still preserve governance gate |
 
This is where your deterministic-first philosophy can make the Data Engineer materially more reliable than a conventional chat agent.
 
## Retrieval, provenance and tool-selection design
 
### Do not use one undifferentiated RAG index
 
For the Data Engineer, I would place a metadata envelope around **every knowledge object**:
 
| Metadata field | Purpose |
|---|---|
| `source_authority` | OAIC, NAA, ASD, vendor docs, internal pattern, etc. |
| `authority_class` | law / policy / standard / official guidance / technical docs / internal guidance |
| `jurisdiction` | Commonwealth, state, EU, general technical |
| `valid_from` | Avoid retrieving obsolete obligations |
| `valid_to` | Prevent superseded guidance appearing current |
| `retrieved_at` | Refresh auditing |
| `document_version` | Reproducibility |
| `content_hash` | Detect upstream changes |
| `owner_agent` | Governance, Security, Data Engineer, shared |
| `escalation_tags` | `privacy`, `recordkeeping`, `cross_border`, `classified`, etc. |
| `project_applicability` | Rules for whether source should enter retrieval |
| `source_type` | canonical document, technical docs, commentary |
| `precedence` | Deterministic conflict resolution |
| `chunk_path` | Chapter/section/heading hierarchy |
| `canonical_uri` | Traceability back to authority |
 
Retrieval would then work approximately as:
 
```text
question / project fact
        ↓
intent + trigger classifier
        ↓
metadata filter
        ↓
authority/validity filter
        ↓
exact/keyword search
        ↓
semantic search where needed
        ↓
rerank small candidate set
        ↓
return source passages + metadata
        ↓
agent reasoning
```
 
This prevents a semantically similar IBM paragraph from outranking the current OAIC chapter when the question is actually about Australian privacy obligations.
 
### Source-precedence rules
 
I would make these rules executable:
 
```text
Project-specific approved decision
    >
Current applicable law/policy/standard
    >
Current authoritative government guidance
    >
Current official product documentation
    >
Council-approved internal engineering standard
    >
Primary project/source-code documentation
    >
General technical background
    >
Third-party commentary
```
 
For current software behavior, however, **version-matched official docs beat an old internal recipe**.
 
### Live documentation rather than duplicated documentation
 
Context7 should sit behind a restricted tool such as:
 
```text
get_library_docs(
    library,
    version,
    topic,
    max_results
)
```
 
Its current MCP design revolves around resolving a library identifier and querying scoped documentation, making it a strong fit for exactly this role. citeturn12search12turn12search19
 
The Data Engineer's documentation resolution policy could be:
 
```text
Is the question about project code/schema?
    -> project repository first
 
Is it an Australian Government obligation?
    -> versioned authoritative local corpus / current official source
 
Is it about library/API syntax or configuration?
    -> Context7
       -> official documentation fallback
       -> source repository/changelog if behavior remains unclear
 
Is it a general design question?
    -> curated engineering KB
       -> empirical experiment/benchmark
       -> inference last
```
 
This is considerably cheaper than embedding thousands of pages of framework documentation that will age almost immediately.
 
### Tool discovery should itself be an agent capability
 
I would permit the Data Engineer to identify new tools, but not silently introduce them.
 
A `research_tool_candidate` skill should produce:
 
```json
{
  "problem": "…",
  "existing_tools_considered": [],
  "candidate": "…",
  "official_source": "…",
  "deployment_model": "…",
  "license": "…",
  "runtime_dependencies": [],
  "network_requirements": [],
  "data_exposure": "…",
  "maturity_evidence": "…",
  "advantages": [],
  "disadvantages": [],
  "why_existing_stack_is_insufficient": "…",
  "recommended_disposition": "trial | reject | council_review"
}
```
 
The key field is **`why_existing_stack_is_insufficient`**. It stops the agent accumulating dependencies merely because it discovered a fashionable project.
 
### Keep provenance on the agent's own decisions
 
Every meaningful Data Engineer recommendation should ideally be serializable as:
 
```json
{
  "decision": "Use Parquet partitioned by year/month",
  "observations": [
    "source_rows=184238122",
    "queries_are_predominantly_date_bounded",
    "append_only=true"
  ],
  "evidence_artifacts": [
    "profile.json",
    "benchmark.parquet.json"
  ],
  "knowledge_sources": [],
  "alternatives": [
    "Postgres",
    "unpartitioned Parquet",
    "Iceberg"
  ],
  "reason": "...",
  "confidence": 0.91,
  "assumptions": [],
  "escalations": [],
  "approved_by": null
}
```
 
That object is vastly more useful to the Solution Architect and future coding agents than a prose conversation buried in an agent trace.
 
OpenLineage gives you a compatible conceptual model for runtime pipeline provenance: its standard represents **datasets, jobs and runs** and attaches extensible metadata facets to them. citeturn16view0 You need not deploy a full lineage backend on day one to adopt those concepts in your own artifact model.
 
## Recommended implementation for your stack
 
Given LangGraph + Neon + R2 + Modal + GitHub, I would build the Data Engineer in stages rather than loading it with every conceivable data tool.
 
### Initial production-quality agent image
 
The first image would contain:
 
| Component | Initial disposition |
|---|---|
| Python runtime | Install |
| DuckDB | Install |
| Polars | Install |
| PyArrow | Install |
| dlt | Install |
| SQLGlot | Install |
| SQLFluff | Install |
| Docling | Install or separate heavier Modal image |
| Presidio | Install or invoke dedicated local service |
| Great Expectations | Available, but loaded only when needed |
| Splink | Available on demand |
| PostgreSQL client | Install |
| R2/S3 client capability | Install |
| Git | Install |
| dbt OSS | Separate/on-demand dependency |
| Java/Tika | Separate extraction sandbox if footprint warrants |
| Spark/Kafka/Airflow | **Do not install by default** |
 
DuckDB's ability to work directly with common files, object stores and databases is particularly attractive for the ephemeral Modal model, while Polars provides a complementary Python-native transformation engine with streaming/out-of-core capability. citeturn9view0turn8view1
 
### Knowledge storage
 
I would organise your R2/Neon content approximately as:
 
```text
knowledge/
    government/
        naa/
        oaic/
        asd/
        pspf/
        dat-scheme/
        digital-service-standard/
    engineering/
        patterns/
        antipatterns/
        decision-trees/
        format-guides/
        migration-guides/
        quality-guides/
 
projects/
    <project-id>/
        data-inventory/
        profiles/
        contracts/
        schemas/
        lineage/
        migrations/
        benchmarks/
        decisions/
        exception-reports/
```
 
The **raw authoritative source** can live in R2. Parsed text/chunks, source metadata and embeddings can sit in Neon. A source hash lets the ingestion job detect actual changes before re-parsing/re-embedding.
 
### A small “Data Engineer Standard Library”
 
This is where I believe custom work is worth doing. Rather than hundreds of bespoke skills, make about a dozen highly reusable deterministic functions:
 
| Skill | Backing implementation | Model required? |
|---|---|---:|
| `inventory_data_source` | OS/R2/database metadata + Tika | No |
| `profile_dataset` | DuckDB/Polars | No |
| `infer_schema` | DuckDB/Polars/PyArrow | Mostly no |
| `compare_schemas` | SQLGlot/custom canonical schema model | No |
| `validate_dataset` | SQL/Polars/GX | No |
| `scan_sensitive_data` | deterministic recognizers + Presidio | Mostly no |
| `convert_dataset` | DuckDB/Polars/PyArrow | No |
| `sample_dataset` | deterministic strategies | No |
| `benchmark_transform` | sandbox execution | No |
| `reconcile_datasets` | DuckDB | No |
| `extract_documents` | Docling/Tika | No/occasionally |
| `link_entities` | Splink | Model is statistical, not LLM |
| `inspect_query` | database `EXPLAIN` + SQLGlot | No |
| `retrieve_technical_docs` | Context7/official docs | LLM summarizes result |
| `produce_data_plan` | Aggregates deterministic evidence | **Yes** |
 
That means the expensive inference call happens mainly at the final line: **reasoning across facts the tools have already established**.
 
### Internal decision trees
 
Give the Data Engineer compact decision trees in addition to prose knowledge.
 
For example:
 
```text
Need to store analytical data?
|
+-- Fits operational relational workload?
|     -> Postgres
|
+-- File-oriented, scan/aggregate, mostly immutable?
|     -> Parquet on object storage
|
+-- Need frequent table mutation / concurrent writers /
|   snapshots / schema+partition evolution on object storage?
|     -> Evaluate Iceberg
|
+-- Need low-latency event consumption?
      -> Escalate streaming architecture assessment
```
 
Iceberg should only enter the third branch because its added value is precisely table-level schema/partition evolution, snapshot/time-travel and atomic/concurrent operations over large analytic datasets. citeturn17view0
 
Another:
 
```text
Need data from external system?
|
+-- REST/simple API?
|      -> dlt/custom typed client
|
+-- Database incremental extraction sufficient?
|      -> dlt/query with watermark
|
+-- Need every committed row-level change quickly?
|      -> evaluate Debezium CDC
|
+-- Existing connector would save major implementation effort?
       -> evaluate Airbyte
```
 
Debezium only appears when actual change-data capture is needed; its purpose is to capture row-level database changes into ordered event streams. citeturn18view0
 
### Council workflow
 
The Data Engineer could participate in a solution-design loop like:
 
```text
                   Human request
                         |
                 Solution Architect
                         |
                 Data requirements?
                        / \
                      no   yes
                           |
                    DATA ENGINEER
                           |
                deterministic discovery
                  / profile / inspect
                           |
                  data risk triggers
                    /      |       \
                privacy  security  records
                   |        |        |
              Governance  Security  Governance
                    \       |       /
                     \      |      /
                   Data Engineer
                           |
                  proposed data plan
                           |
                  Data Analyst review
                 (when semantics/analysis)
                           |
                   Solution Architect
                           |
                     Council agreement
                           |
                      Human approval
                           |
                     Coding swarm
                           |
                 unexpected data issue
                           |
              Data Engineer triage first
                    /             \
              within plan       material change
                  |                  |
               resolve          Council escalation
```
 
This gives the Data Engineer substantial autonomy without accidentally turning it into privacy counsel, security authority, statistician and Solution Architect simultaneously.
 
### Priority roadmap
 
I would implement in this order:
 
| Priority | Build | Why |
|---|---|---|
| **First** | Role charter + deterministic escalation matrix | Prevents agent overlap before sophistication grows |
| **First** | `profile_dataset`, `compare_schema`, `validate_dataset`, `reconcile_datasets` | Highest-frequency work; almost entirely deterministic |
| **First** | DuckDB + Polars + Arrow tool wrappers | Foundation for the preceding skills |
| **First** | NAA + OAIC + PSPF/ISM trigger corpus | Australian Government problems need the agent to notice these constraints early. citeturn22view1turn22view2turn22view3 |
| **First** | Context7 documentation capability | Avoids filling your KB with aging package docs. citeturn12search12turn12search19 |
| **First** | Source metadata/versioning model | Makes regulatory and technical retrieval reproducible |
| **Next** | dlt ingestion wrapper | Reusable ingestion without introducing a platform service. citeturn10search12 |
| **Next** | Docling document extraction | Broadens the agent substantially into unstructured government information. citeturn21view1 |
| **Next** | Presidio screening + Australian/project-specific recognizers | Gives pipelines an early-warning privacy trigger while retaining human/governance oversight. citeturn19view0 |
| **Next** | SQLGlot analysis + SQLFluff CI | Makes generated SQL inspectable and mechanically checked. citeturn20view0turn21view2 |
| **Next** | Standard migration/reconciliation workflow | High value once the coding swarm starts changing real schemas |
| **Then** | Splink entity-resolution skill | Powerful specialist capability for administrative data. citeturn22view0 |
| **Then** | dbt project skill | Activate for analytical transformation projects rather than every project. citeturn8view3 |
| **Then** | OpenLineage events | Adopt when cross-pipeline provenance becomes difficult to understand from project artifacts alone. citeturn16view0 |
| **Later/as triggered** | Prefect/Dagster/Airbyte/Iceberg/Debezium | Let actual solution requirements justify additional infrastructure. citeturn11view0turn11view1turn11view2turn17view0turn18view0 |
 
The overarching principle I would use for this Council member is:
 
> **Give the Data Engineer broad awareness but a narrow default stack. Give it many things it can identify and recommend, but only a small set of deterministic tools that it reaches for automatically.**
 
That produces a better match for your overall architecture than making it a miniature enterprise data platform. It can recognize that a problem may require Airbyte, Debezium, Iceberg, Dagster or Spark without paying the operational and cognitive cost of making those technologies defaults.
 
More importantly, it changes the role of the LLM. The Data Engineer would not normally be asked to *guess* what a dataset contains, *guess* whether a migration succeeded, *guess* whether SQL is compatible, *guess* which records were lost, or *guess* whether a PDF table was extracted correctly. It would **measure, parse, validate, reconcile and benchmark first**, and reserve inference for the genuinely valuable task: deciding what those verified facts imply for the solution.
