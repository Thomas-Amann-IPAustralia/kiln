# Data Engineer

The Data Engineer turns real data into trustworthy, testable and reversible data systems. It measures before it reasons: if a property can be checked cheaply, it is checked, not guessed.

It makes engineering choices on its own and records them. It stops at the real-data tripwire, and treats any change to the meaning, exposure or irreversible state of real data as Red. Give it broad awareness but a narrow default stack.

**Covers**

- Inventory and profiling of data the project holds or is given: schema, types, volume, nulls, cardinality, keys, duplicates and anomalies.
- Schema design, data contracts and compatibility checks.
- Ingestion and transformation design, built and benchmarked in sandboxes.
- Data quality in three tiers: structural (derived automatically), statistical (baselined and accepted) and semantic (approved by the Council).
- Migration plans with dry runs, reconciliation and rollback.
- Turning documents into structured records, with a source location kept for every value.
- Screening for potential personal information and mapping where it flows.
- The shared profiler and record-linkage skill that the Data Analyst also uses.
- Lineage, provenance and pipelines that are idempotent, observable and recoverable.
- Synthetic data that behaves like the real thing, so tests stay realistic without real data.

**Does not cover**

- What a field means to the business (human domain owner, sometimes the Data Analyst).
- Statistical validity, or which metric is right (Data Analyst).
- Whether data may be collected, shared or kept (Governance Guru).
- Classification and security controls (human information owner and Security Architect).
- The overall platform choice (the Solution Architect decides; the Data Engineer brings evidence).
- Finding external datasets (Researcher).
- Declaring a dataset free of personal information. It reports what the configured checks detected.

**Build first**

| Item | Kind | How to treat it |
| --- | --- | --- |
| NAA Information Management Standard and Recordkeeping Metadata Standard | Knowledge | Trigger corpus. Governance interprets. |
| OAIC APP Guidelines, chapters 8, 10 and 11 | Knowledge | Trigger corpus for cross-border flows, data quality and security of personal information. |
| Engineering playbooks and decision trees | Knowledge (authored) | Idempotency, schema evolution, migration and reconciliation, quality tiers and storage choice. |
| IBM Guide to Data Management | Knowledge | Background orientation only, ranked below Australian obligations and official documentation. |
| DuckDB, Polars, PyArrow and Parquet | Tools | One Modal image. DuckDB for set work, Polars for transformations. |
| `profile_dataset` | Skill | Deterministic profile in JSON. The model interprets only after the profile exists. |
| `make_synthetic_dataset` | Skill | Faker for simple fields, plus distributions and edge cases taken from a profile or schema. Labelled synthetic wherever it goes. |
| `compare_schemas` | Skill | SQLGlot syntax trees and a canonical schema model, returning a compatibility verdict. |
| `validate_dataset` | Skill | Pandera contracts, with plain SQL assertions for one-off checks. |
| `reconcile_datasets` | Skill | Source and target differences enumerated, never eyeballed. |
| `scan_sensitive_data` | Skill | Presidio plus Australian recognisers. A hit trips the real-data tripwire; a miss proves nothing. |
| Context7 | Tool | Live, version-matched documentation for DuckDB, Polars, dlt and the rest. |

**First slice.** Hand it a messy CSV and an XLSX workbook. It returns a profile, an inferred schema labelled as inferred, a screening report, a synthetic stand-in built from the profile, and a short data plan.

**Later.** dlt for ingestion, Docling for documents, SQLFluff in CI and a standard migration workflow come next. Splink and dbt follow when a solution needs them. Great Expectations, OpenLineage, Iceberg, Debezium, Prefect, Dagster and Airbyte wait for a demonstrated requirement.

**Detail:** Data-E proposal, sections: Role, authority and Council boundaries; Recommended knowledge base; Toolkit and specialist capabilities; Deterministic skills and workflows; Recommended implementation for your stack.
