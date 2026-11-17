# Data Analyst

The Data Analyst answers one question: given this evidence and these data, what can defensibly be concluded? It is an analytical control system. Rules remove invalid methods, the model chooses among valid ones, trusted libraries do the arithmetic, and a separate validation pass checks the claim.

The main risk is not bad arithmetic. It is doing the wrong analysis correctly: the wrong unit, a missed survey weight, leakage between training and test data, or association reported as cause.

**Covers**

- Measurement plans for DVF hypotheses: what to measure, how much evidence is enough, and what result would change the decision.
- Analysis of real-world test results, usage data and viability models, with honest uncertainty.
- The AnalysisSpec: objective, population, unit of analysis, outcome, estimand, comparison, design, dependence and claim strength.
- Fitness for purpose of data, using the seven dimensions of the ABS Data Quality Framework.
- Method selection through Method Cards and a constraint solver.
- Analysis in sandboxes, with full run manifests.
- Validation: assumptions, leakage, sensitivity, out-of-sample checks and an independent critic node.
- An evidence ledger linking every claim to results, data and code.
- Declarative chart specifications rather than plotting code.

**Does not cover**

- Pipelines and production data (Data Engineer).
- Finding external literature or datasets (Researcher).
- Privacy, data-sharing authority or legal questions (Governance Guru).
- Classification or storage controls (Security Architect).
- Dashboard usability (UX Designer).
- Overall solution trade-offs (Solution Architect).
- Causal claims the design cannot support. It downgrades them to association, and labels any method without a Method Card as unreviewed.

**Build first**

| Item | Kind | How to treat it |
| --- | --- | --- |
| ABS Data Quality Framework | Knowledge | Encoded as a mandatory `DataQualityAssessment` schema. The source text stays for explanation. |
| Method Cards | Knowledge (authored) | Seeded from SDA-V2 and ChooseMyStat logic and reviewed before use. Retrieval explains; the card controls execution. |
| SciPy, statsmodels and scikit-learn documentation | Knowledge | Pinned to the installed versions, especially scikit-learn's pitfalls and model selection pages. |
| An Introduction to Statistical Learning (Python edition) | Knowledge | Conceptual handbook. |
| ABS classifications and ASGS editions | Knowledge | Versioned with correspondence tables, so mismatched codes block a join. |
| `AnalysisSpec` schema and validator | Schema | Nothing executes until the required fields are filled. |
| Method Registry constraint solver | Skill | Filters by objective, outcome, design, dependence, survey and time structure, then applies hard prohibitions. |
| SciPy, statsmodels, scikit-learn, DuckDB and Pandera | Tools | One Modal image. pandas only where these libraries need it. |
| `assess_data_quality` | Skill | Builds on the Data Engineer's shared profile. |
| `validate_analysis` and the critic node | Skill | Deterministic suite first, then an independent check that the evidence supports the exact claim. |
| Evidence ledger and run manifest | Data | Data hashes, code commit, package lock, seeds and parameters. |
| Altair | Tool | Vega-Lite specifications that can be stored and tested. |
| ABS wrappers | Skill | Thin functions over the shared SDMX service, never a second client. |

**First slice.** For one sample brief, write the measurement plan for its hypotheses. Then take a small synthetic test-results dataset through the full path (AnalysisSpec, quality assessment, method selection, execution and validation) into a DVF evidence statement in the standard answer contract.

**Later.** The R `survey` adapter, which matters for government survey data, then DoWhy for causal work, GeoPandas, METEOR, the Commonwealth Evaluation Policy and Toolkit, and Splink through the Data Engineer's skill. PyMC, EconML and NetworkX only when a question needs them.

**Detail:** Data-A proposal, sections: Knowledge base design; Deterministic analytical decision engine; Recommended analytical toolkit; Data discovery, source search and government context; Governance, reproducibility and Council interaction; Recommended build sequence and target architecture.
