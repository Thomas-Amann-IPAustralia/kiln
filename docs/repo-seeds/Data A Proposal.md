# Proposal for the Data-Analyst Agent in “The Council”
 
## Executive recommendation
 
The Data-Analyst should be designed less as an autonomous “data scientist who knows lots of statistics” and more as an **analytical control system**: it translates a decision or research question into an explicit analytical specification, inspects the available data, deterministically narrows the permissible methods, executes calculations through trusted libraries, tests the result from several directions, and only then uses model inference to interpret and communicate what the computations mean.
 
That architecture is unusually well suited to the system you describe. Existing statistical software already covers almost all of the mechanical work. SciPy provides distributions, descriptive statistics, resampling and hypothesis tests; statsmodels covers regression, generalized models, mixed models, time-series, survival analysis, imputation and other classical inference; scikit-learn covers supervised and unsupervised machine learning, preprocessing, model selection and validation; and specialist open-source packages can be called only when the problem requires survey inference, causal inference, spatial statistics, record linkage or Bayesian modelling. citeturn10view3turn13view0turn19view2
 
My central recommendation is therefore:
 
> **Do not build the Data-Analyst around a large statistical prompt. Build it around a machine-readable analytical ontology, a method registry, deterministic diagnostic and validation functions, specialist execution adapters, and an evidence/provenance ledger.**
 
The LLM should decide things such as *what question the human is really asking*, *which estimand matters*, *whether a result answers that question*, *which limitations are material*, and *how the findings should be explained*. It should not calculate correlations, decide whether a column contains duplicates by eyeballing samples, manufacture SQL, manually calculate confidence intervals, or remember from its weights which statistical test applies. Those activities can be delegated to code.
 
This is also why your ChooseMyStat and Smart Data Analysis V2 ideas are valuable, but I would use them principally as **source material and design precedents for your own decision engine**, rather than making either one the engine itself. SDA-V2 explicitly performs exploratory analysis, checks assumptions and automatically selects methods, but covers only nine packages of relatively conventional analyses and its authors explicitly caution that it does not replace statistical understanding. citeturn20view1turn20view2 ChooseMyStat similarly demonstrates the value of branching method selection and analysis-plan generation, but is oriented toward clinical research and, as of 2026, is a recent preprint rather than a universal statistical standard. citeturn4search0
 
The resulting agent would look approximately like this:
 
| Layer | Data-Analyst responsibility | Predominantly deterministic? |
|---|---|---:|
| Question formulation | Convert natural-language request into population, unit of analysis, outcome, comparison, time period, objective and estimand | No |
| Governance preflight | Detect personal/sensitive/linkable data and conditions requiring Council escalation | Mostly |
| Data discovery | Find appropriate datasets, variables, classifications and metadata | Mostly |
| Data inspection | Schema, types, distributions, missingness, uniqueness, impossible values, duplicates, temporal/spatial coverage | **Yes** |
| Quality assessment | Produce structured fit-for-purpose assessment | **Yes**, with judgment at end |
| Method eligibility | Remove methods incompatible with design/data/estimand | **Yes** |
| Method choice | Select among remaining defensible approaches and document trade-offs | Mixed |
| Transformation | Joins, recoding, reshaping, weighting, feature engineering, imputation | **Yes** |
| Analysis | Statistics, model fitting, resampling, prediction, linkage, spatial operations | **Yes** |
| Validation | Assumption diagnostics, sensitivity analyses, leakage checks, out-of-sample validation, alternative specifications | **Yes** |
| Interpretation | Explain effect size, uncertainty, practical significance, limitations and applicability | No |
| Reporting | Generate answer with traceable claims, tables, charts and provenance | Mixed |
| Reproducibility | Persist data fingerprints, code, queries, parameters, seeds, dependency versions and results | **Yes** |
 
This complements rather than duplicates the other Council members. The Data-Engineer should own durable ingestion, production pipelines and data platform engineering; the Researcher should own broad external evidence gathering; Governance should own authoritative interpretation of policy, legislation, privacy and data-sharing requirements; Security should decide technical security controls. The Data-Analyst owns the narrower question: **“Given this evidence and these data, what can defensibly be concluded?”**
 
## Knowledge base design
 
I would not create one monolithic vector database of books, package documentation and statistical papers. The most important part of the Data-Analyst's knowledge should instead be **structured knowledge that is executable or queryable before semantic retrieval occurs**.
 
A useful division is four knowledge collections.
 
### Core analytical knowledge
 
This should contain the relatively stable body of knowledge the agent needs to reason about analytical design.
 
| Knowledge source | What I would ingest | Why it belongs | Priority |
|---|---|---|---:|
| **An Introduction to Statistical Learning, Python edition** | Conceptual sections and method summaries; retain chapter/page/source metadata | Excellent relatively accessible catalogue spanning regression, classification, resampling, regularisation, nonlinear methods, trees, SVMs, deep learning, survival analysis, unsupervised learning and multiple testing. It also has executable Python labs. citeturn20view3 | Essential |
| **scikit-learn User Guide** | Versioned documentation, especially preprocessing, model selection, metrics, inspection, pipelines, estimator choice and pitfalls | Particularly valuable because methodological guidance and executable implementation are adjacent. The documentation explicitly includes estimator selection and pitfalls such as preprocessing inconsistencies, leakage and randomness. citeturn20view4turn20view5 | Essential |
| **SciPy statistics documentation** | Functions plus assumptions/parameters/return semantics for tests, distributions and resampling | Forms the deterministic low-level engine for much classical analysis instead of asking an LLM to calculate statistics. citeturn10view3 | Essential |
| **statsmodels documentation** | Model families, diagnostics and result semantics | Provides the richer inferential toolkit: regression, generalized and mixed models, robust methods, discrete outcomes, time series/state-space methods, survival/duration, nonparametric and multivariate methods, imputation and treatment-effect functionality. citeturn13view0 | Essential |
| **SDA-V2 paper and source implementation** | Extract its decision branches and assumption checks into candidate rules; do not treat them as immutable truth | It is an existing example of translating statistical decision logic into software, including automatic EDA, assumption assessment and method selection. citeturn20view1turn20view2 | High |
| **ChooseMyStat paper/application** | Extract question taxonomy, branching concepts, generated-plan structure and references | It is directly aligned with your intended concept of deterministic method routing, although its clinical focus means rules should be reviewed before generalisation. citeturn4search0 | High |
| **DoWhy documentation** | Causal assumptions, identification, estimation and refutation workflow | DoWhy explicitly treats assumptions as first-class objects, separates identification from estimation and supports automated sensitivity/robustness checks. That philosophy is extremely compatible with Council-style analysis. citeturn16view0 | High |
| **Complex-survey methodology and R `survey` documentation** | Sampling weights, strata, clusters, replicate weights, calibration and variance estimation | Government data frequently arises from surveys where naïve independent-observation analyses are inappropriate. The `survey` package handles multistage, stratified, clustered and unequal-probability samples, replicate weights, calibration and related estimation. citeturn22search3turn22search7 | High |
| **PyMC guides/examples** | Bayesian workflow, prior/predictive checking, posterior diagnostics and model comparison | Useful for genuinely Bayesian questions, hierarchical modelling and uncertainty propagation, but sufficiently specialised that it should sit behind an explicit routing gate. citeturn13view1 | Medium |
 
I would **not** simply chunk those sources and hope RAG finds the correct paragraph. Extract their reusable knowledge into what I would call **Method Cards**.
 
A Method Card might look conceptually like:
 
```yaml
method_id: regression.logistic.binary
family: generalized_linear_model
 
supports:
  objectives:
    - association
    - adjusted_association
    - prediction
  outcome:
    type: binary
 
requires:
  - independent_unit_defined
  - outcome_has_two_valid_levels
 
conditional_requirements:
  - if: clustered_observations
    then:
      - cluster_robust_or_multilevel_strategy
  - if: complex_survey
    then:
      - survey_aware_estimator
 
prohibits:
  - perfect_target_leakage
 
diagnostics:
  - separation
  - influential_observations
  - calibration_if_predictive
  - residual_or_fit_diagnostics
  - multicollinearity_where_relevant
 
validation:
  inference:
    - confidence_interval
    - sensitivity_specification
  prediction:
    - held_out_evaluation
    - calibration
    - discrimination
 
implementations:
  - statsmodels
  - sklearn
  - r_survey
 
escalate_when:
  - causal_claim_requested
  - consequential_individual_decision
  - unsupported_sampling_design
 
references:
  - ...
```
 
The key distinction is that **retrieval provides explanation; the Method Card controls execution**.
 
### Australian Government analytical knowledge
 
This should be a first-class partition of the KB, not merely a few documents embedded alongside generic statistical material.
 
The ABS Data Quality Framework is particularly valuable despite the source page now being archived. It defines seven dimensions—**institutional environment, relevance, timeliness, accuracy, coherence, interpretability and accessibility**—and was explicitly intended to help determine whether statistical data is fit for purpose. citeturn19view4turn19view5 I would turn those dimensions into a mandatory `DataQualityAssessment` schema rather than merely letting the agent retrieve the document.
 
| Australian source | How the Data-Analyst should use it | Implementation |
|---|---|---|
| **ABS Data Quality Framework** | Fit-for-purpose assessment and mandatory quality statement | Encode the seven dimensions as structured checks/questions; retain the source document for explanatory retrieval. citeturn19view4turn19view5 |
| **ABS classifications** | Standardise occupations, geography, industries, countries, languages, offences and other common government variables | Maintain a machine-readable classification registry and version/correspondence tables. ABS currently publishes a suite of classifications, and OSCA has replaced ANZSCO for Australian occupational classification. citeturn18search4turn15search30 |
| **Australian Statistical Geography Standard** | Geographical aggregation, comparisons and spatial analysis | Persist version/edition information and require explicit geography-level checks before joins or area comparisons. citeturn5search24 |
| **ABS Data API** | Machine-readable acquisition of economic, social and Census statistics | Create dedicated discovery and query tools around its SDMX model rather than letting the LLM construct requests ad hoc. The API supports metadata-driven discovery and CSV/JSON/XML responses. citeturn19view8turn19view9 |
| **AIHW METEOR** | Interpret definitions and metadata for health, housing, homelessness, aged care, First Nations health, disability, children/families and youth-justice data | Build a `meteor_lookup()` connector; METEOR exposes read access to metadata through its API. citeturn19view10 |
| **Commonwealth Evaluation Policy and Toolkit** | Program/policy evaluation questions, particularly the transition from “analysis” to formal evaluation | Use as an evaluation-methodology KB and escalation trigger. The Commonwealth policy is intended to embed evaluation and evidence-based policy/delivery, and its toolkit assists Commonwealth entities in applying it. citeturn22search0turn22search12 |
| **Indigenous evaluation guidance** | Evaluation involving Aboriginal and Torres Strait Islander people | Explicitly route to appropriate cultural/evaluation guidance and Governance/human review; Commonwealth guidance requires evaluations to be robust, ethical and culturally appropriate. citeturn22search32 |
| **DATA Scheme / ONDC material** | Recognise data-sharing context and determine when governance expertise is required | Treat it as a trigger/metadata source rather than allowing the Analyst to make final legal determinations. The scheme operates alongside existing Australian law and contains safeguards for sharing Australian Government data. citeturn19view6 |
| **OAIC Australian Privacy Principles** | Personal-information detection and escalation | Encode broad triggers only. The APPs govern collection, use/disclosure, governance/accountability, data integrity/correction and access rights. citeturn19view7 |
| **HILDA manuals, when relevant** | Correct analysis of a prominent Australian longitudinal dataset | The release documentation covers joining waves, missing-value conventions, derived variables, weights, imputation and data quality, making it far safer than inferring dataset semantics from column names. citeturn9search10 |
 
A subtle but important point is **versioning classifications and definitions**, not simply storing their current names. An occupational category, geographical boundary or administrative definition can change while the historical data being analysed remains encoded under an earlier version. The Analyst needs to be able to say, in effect, “these two datasets cannot be directly joined using current codes without a correspondence transformation.”
 
### Knowledge that should remain outside the Analyst
 
An expert agent can become worse, not better, if its KB causes it to confidently invade another expert's responsibility. I would define explicit ownership boundaries.
 
| Topic | Data-Analyst may do | Final authority |
|---|---|---|
| Privacy | Detect personal information, linkage/re-identification issues and potentially unsafe analytical outputs | Governance Guru / Security Architect |
| DATA Scheme/legal authority | Identify potentially applicable provisions and record provenance | Governance Guru |
| Security classification/storage | Characterise data fields and analytical requirements | Security Architect |
| Data pipeline architecture | Specify analytical input/output requirements | Data-Engineer |
| External literature review | Request evidence and evaluate quantitative results | Researcher |
| UI/dashboard usability | Produce semantically correct visual specification | UX Designer |
| Overall solution trade-off | State analytical consequences | Solution Architect / Chair |
 
That should be reflected directly in the agent's tool permissions. The Analyst should be capable of saying **“analysis blocked pending governance determination”** rather than being rewarded for producing an answer at all costs.
 
## Deterministic analytical decision engine
 
This is, in my view, the highest-value custom component to build.
 
The important innovation over a simple “which statistical test?” decision tree is to route based on **the question, study design and data-generating structure before inspecting which test happens to produce an attractive result**.
 
### The analytical specification
 
Every substantial job should begin by producing an `AnalysisSpec`. The LLM can draft it from the user's language, but deterministic validation should ensure all necessary fields are populated before execution.
 
| Field | Examples | Why it matters |
|---|---|---|
| `objective` | describe, estimate, compare, test, predict, forecast, explain, causal-effect, cluster, anomaly-detect, link-records | Immediately removes irrelevant method families |
| `decision_question` | “Should this program be expanded?” | Separates analytical output from the decision ultimately supported |
| `population` | Australian residents aged 18–24 | Defines external validity |
| `unit_of_analysis` | person, household, business, postcode, transaction | Prevents pseudoreplication and bad joins |
| `outcome` | employment status | Drives distribution/model family |
| `outcome_scale` | continuous, binary, count, ordinal, nominal, duration | Deterministically constrains candidate methods |
| `exposure_or_treatment` | program participation | Required for many causal/evaluation analyses |
| `estimand` | mean difference, risk ratio, ATE, forecast, probability | Forces precision about what is being estimated |
| `comparison` | participants vs eligible non-participants | Prevents implicit comparison groups |
| `design` | census, convenience sample, RCT, longitudinal panel, complex survey, observational administrative data | Determines inferential assumptions |
| `dependence` | independent, repeated measures, household clusters, sites | Controls permissible variance/model treatment |
| `time_structure` | cross-sectional, panel, regular time series, event history | Controls validation and modelling |
| `spatial_structure` | none, points, polygons, administrative geography | Activates CRS/spatial rules |
| `survey_design` | weights, strata, PSU, replicate weights | Routes to survey-aware estimation |
| `missingness` | pattern and amount | Selects complete-case/imputation/sensitivity paths |
| `decision_costs` | false negative substantially worse | Determines predictive metrics/thresholding |
| `required_uncertainty` | CI, prediction interval, posterior | Determines output |
| `claim_strength` | descriptive, associational, predictive, causal | Particularly important for preventing causal overclaim |
| `sensitivity` | public, internal, personal, highly sensitive | Controls allowed execution environments/tools |
 
A well-formed specification is far more useful than merely asking the model, “What test should I use?”
 
### Method routing
 
I would implement routing as a **constraint solver over Method Cards**, not one enormous tree.
 
Conceptually:
 
```text
All registered methods
      ↓
filter(objective)
      ↓
filter(outcome/data types)
      ↓
filter(study design)
      ↓
filter(dependence structure)
      ↓
filter(sample/survey design)
      ↓
filter(time/spatial structure)
      ↓
apply hard prohibitions
      ↓
attach required transformations
      ↓
attach diagnostics
      ↓
attach validation protocol
      ↓
rank remaining candidates
      ↓
LLM judgment only if >1 defensible candidate remains
```
 
That distinction matters. **Rules eliminate invalid methods; inference chooses among valid methods.**
 
The framework should also be multi-stage rather than allowing an assumption test alone to dictate the analysis. SDA-V2 is useful as precedent because it programmatically explores data, checks assumptions and selects tests, but its relatively narrow method catalogue and explicit warning that software does not replace statistical understanding are good reasons to use it as a seed rather than your final ontology. citeturn20view1turn20view2
 
Some high-value deterministic rules would be:
 
| Condition detected | Deterministic consequence |
|---|---|
| Complex-survey weights/strata/clusters exist | Naïve iid standard errors are prohibited; route to survey-aware methods such as R `survey`. citeturn22search7 |
| Prediction objective | Require out-of-sample validation and metric appropriate to output/decision; activate leakage checks. scikit-learn explicitly documents leakage and preprocessing pitfalls. citeturn20view5 |
| Time-ordered prediction | Random train/test shuffling prohibited unless explicitly justified; use temporally appropriate validation |
| Causal claim requested | Prediction/association models alone cannot satisfy request; require explicit treatment, outcome, target estimand and identification assumptions |
| Causal analysis approved | Route through assumption → identification → estimation → refutation workflow; DoWhy deliberately separates identification and estimation. citeturn16view0 |
| Repeated observations/person | Independence-only procedure prohibited unless dependence is otherwise accounted for |
| Record linkage without universal identifier | Route to deterministic or probabilistic linkage workflow; do not silently fuzzy-join |
| Geographic distance/area calculation | CRS must be known and appropriate before execution |
| Multiple simultaneous hypotheses | Require explicit multiplicity policy |
| Missing target values in supervised learning | Prohibit treating missing target as an ordinary class unless analytically intended |
| Data transformed using full dataset before validation split | Fail leakage test |
| Survey or administrative category versions differ | Require correspondence/reconciliation or block direct comparison |
| Requested claim exceeds design | Downgrade claim or escalate; observational association must not automatically become causal language |
| Sample cannot support requested subgroup | Suppress/qualify output rather than produce unstable point estimates |
| High-consequence individual prediction | Require Council/human escalation before treating model performance as sufficient evidence |
 
### Validation should be a separate agentic phase
 
The same reasoning process that selects a model should not simply pronounce its own work correct.
 
I would have the Analyst produce a candidate result and then run a **deterministic validation suite plus an adversarial analytical review node**. That review can still be the same expert identity in Council terms, but it should receive the original question, specification and output independently.
 
For example:
 
```text
Question
   ↓
AnalysisSpec
   ↓
Primary analysis
   ↓
┌─────────────────────────────────────┐
│ Deterministic validation            │
│ schema / assumptions / leakage      │
│ numerical checks / holdout metrics  │
│ residuals / sensitivity / stability │
└─────────────────────────────────────┘
   ↓
Independent critic
   ↓
Does evidence support exact claim?
   ↓
Final answer
```
 
For causal work, DoWhy is particularly aligned with this philosophy because it treats assumptions explicitly and includes robustness/refutation functions rather than considering estimation the end of the analysis. citeturn16view0
 
### Standard analytical artefacts
 
Every non-trivial analysis should leave substantially more behind than a natural-language response.
 
| Artefact | Contents | Storage |
|---|---|---|
| `analysis_spec.json` | Question, population, estimand, objective, design, claim level | Postgres / Git |
| `source_manifest.json` | Dataset origin, retrieval date, source version, hashes, licence/metadata | Postgres |
| `schema.json` | Variables, types, units, categories, keys | Git/object storage |
| `quality_report.json` | Automated profile + ABS-quality assessment | R2/Postgres |
| `method_decision.json` | Candidate methods, rejected methods, constraints, chosen method and reason | Postgres |
| `transform_plan.sql/json` | Exact deterministic transformations | Git |
| `validation_report.json` | Diagnostics, sensitivity tests, leakage checks, model metrics | R2/Postgres |
| `run_manifest.json` | Code commit, package lock, container identifier, seeds, parameters | Postgres |
| `results.parquet` | Machine-readable analytical output | R2 |
| `visualisations/*.json` | Declarative chart specifications where feasible | Git/R2 |
| `evidence_ledger.jsonl` | Final claims mapped to calculations/data/source evidence | Postgres/R2 |
| `answer.md` | Human-facing response | Application |
 
The **evidence ledger** is especially important for your intended role description. Instead of allowing the LLM to turn a dataframe into prose without accountability, a conclusion might internally be represented as:
 
```json
{
  "claim_id": "C17",
  "claim": "Group A had a higher adjusted rate than Group B.",
  "result_ids": ["R11"],
  "method_id": "glm.poisson.robust",
  "effect": 1.18,
  "interval": [1.09, 1.27],
  "data_sources": ["ABS_X", "ADMIN_Y"],
  "analysis_run": "run_8f314...",
  "limitations": ["observational_data"],
  "claim_strength": "association"
}
```
 
The prose generator is then constrained to statements already supported by an evidence object.
 
That is much closer to a defensible autonomous analyst than merely giving an LLM access to Python.
 
## Recommended analytical toolkit
 
Your infrastructure choices make an **embedded/local-first Python analytical stack** particularly attractive. Most jobs can execute inside a Modal sandbox or your Oracle host without introducing another persistent service.
 
### Core data plane
 
| Tool | Recommended role | Why I would include it | Priority |
|---|---|---|---:|
| **DuckDB** | Default analytical SQL engine | DuckDB directly handles CSV, JSON and Parquet, integrates with Python/dataframe tools, supports PostgreSQL connectivity and includes documented S3/R2 access. This aligns unusually well with your R2 + Postgres/Neon architecture while requiring no separate analytical database service. citeturn11view0 | **P0** |
| **Apache Arrow / Parquet** | Internal interchange and analytical file format | Arrow defines a language-independent columnar memory format intended for efficient analytical processing and interoperability. citeturn9search19 | **P0** |
| **pandas** | Compatibility/default dataframe API | Its documentation covers broad IO, joins, reshaping, missing data, grouping, windowing and time-series operations; huge amounts of analytical Python code expect its interface. citeturn10view2 | **P0** |
| **Polars** | Optional larger/faster dataframe execution | Polars is an open-source analytical DataFrame/query engine written in Rust and built around Arrow. I would expose it through the same analytical abstractions rather than make agents choose pandas versus Polars themselves. citeturn17search3turn17search7 | P1 |
| **Pandera** | Data contracts and dataframe validation | Supports declarative dataframe schemas, custom checks, lazy validation/error reporting, schema persistence and multiple dataframe backends. It is an excellent basis for deterministic input/output contracts. citeturn13view2 | **P0** |
 
I would make DuckDB the first choice for **set-oriented work** and pandas/Polars an implementation detail for algorithms that genuinely require dataframe objects.
 
That gives you an appealing execution pattern:
 
```text
R2 Parquet/CSV
      ↓
    DuckDB ←→ Neon/Postgres
      ↓
validated Arrow/DataFrame
      ↓
 statistical/model library
      ↓
 Parquet + JSON artefacts
```
 
Because DuckDB documents direct object-storage and PostgreSQL workflows, it is a natural bridge across the infrastructure you already plan to operate. citeturn11view0
 
### Statistics and machine learning
 
| Tool | Capability | Routing recommendation | Priority |
|---|---|---|---:|
| **SciPy `stats`** | Distributions, descriptive statistics, correlation, hypothesis tests, resampling/Monte Carlo and other statistical primitives | Default deterministic primitive layer | **P0** citeturn10view3 |
| **statsmodels** | Classical statistical modelling and inference, GLMs, mixed/discrete models, robust methods, time series, survival, multivariate methods and imputation | Default when inference/coefficients/uncertainty are primary | **P0** citeturn13view0 |
| **scikit-learn** | Preprocessing, supervised/unsupervised ML, ensembles, model selection, evaluation, dimensionality reduction, anomaly detection and pipelines | Default predictive/modelling engine | **P0** citeturn19view2turn20view4 |
| **R `survey`** | Proper analysis of complex samples with weights, clustering, strata, calibration and replicate-weight variance estimation | Automatically activate when survey-design metadata demands it | **P1 but important for government** citeturn22search3turn22search7 |
| **PyMC** | Bayesian and hierarchical modelling with posterior/predictive workflows | Expert-only route; do not invoke merely because it is powerful | P2 citeturn13view1 |
| **DoWhy** | Causal model/assumption definition, identification, estimation and refutation | Governing causal-analysis workflow | **P1** citeturn16view0 |
| **EconML** | Machine-learning-assisted heterogeneous causal-effect estimation | Advanced causal route after identification is established | P2. EconML is specifically designed for estimating individualized causal responses from observational or experimental data. citeturn14search7turn14search11 |
 
I would resist installing dozens of competing model libraries initially. scikit-learn's breadth is already substantial, including estimator-selection guidance, and model proliferation would increase the validation burden on your Method Registry. citeturn20view4
 
### Specialist capabilities worth provisioning
 
This is where a small number of good tools dramatically expands the Analyst's usefulness.
 
| Domain | Tool | Why it is valuable in your context | Priority |
|---|---|---|---:|
| **Spatial/GIS** | **GeoPandas** | Government questions frequently involve administrative areas, service coverage or regional variation. GeoPandas handles projections, geometric operations, overlay, aggregation, spatial merging and geocoding in the normal Python analytical environment. citeturn14search0turn14search20 | P1 |
| **Record linkage/entity resolution** | **Splink** | One of the strongest fits in the entire toolkit. It performs probabilistic linkage/deduplication where unique identifiers do not exist, includes evaluation/diagnostic tooling and DuckDB execution, and the ABS itself is listed as using Splink for national linkage-spine work. citeturn16view1 | **P1** |
| **Networks/relationships** | **NetworkX** | Provides graph structures and algorithms for analysing network structure and relationships. Useful for service networks, organisations, transactions, dependency analysis and linked-data investigations. citeturn17search2turn17search14 | P2 |
| **Visualisation specification** | **Vega-Altair** | Declarative chart specifications are preferable to agent-written plotting imperative code when possible: the chart itself becomes serialisable, testable and reproducible. Altair is a declarative Python interface for Vega-Lite. citeturn16view3 | **P0/P1** |
| **Text analytics** | **scikit-learn + deterministic parsing initially** | Feature extraction, classification/clustering and conventional ML are already within the scikit ecosystem; reserve LLM semantic interpretation for tasks where it genuinely adds value. citeturn19view2 | P1 |
| **Time-series/forecasting** | **statsmodels initially** | Avoid another dependency until requirements justify it; statsmodels already contains substantial time-series and state-space functionality. citeturn13view0 | **P0** |
| **Survival/event history** | **statsmodels initially** | Existing support avoids prematurely adding another modelling stack. citeturn13view0 | P1 |
| **Large-data linkage** | **Splink + DuckDB; Spark only if truly needed** | Splink supports DuckDB for ordinary execution and larger backends where required, so you do not need standing Spark infrastructure. citeturn16view1 | P1 |
 
Splink deserves particular emphasis. It is not just theoretically appropriate: its documentation lists substantial public-sector use, including the Australian Bureau of Statistics' 2024 National Linkage Spine and planned subsequent linkage work. citeturn16view1 That makes it a compelling example of **not rebuilding work that government statistical organisations already use**.
 
### Useful skills to wrap around those libraries
 
Coding agents should not receive unrestricted instructions like “use Python to analyse this”. Give the Data-Analyst and coding swarm semantically meaningful analytical tools.
 
| Proposed skill | Deterministic core | Output |
|---|---|---|
| `inspect_dataset()` | DuckDB/Pandera | `DatasetProfile` |
| `validate_schema()` | Pandera | Pass/fail + violations |
| `assess_data_quality()` | Custom rules + ABS DQF | `DataQualityReport` |
| `discover_relationships()` | SQL/SciPy | Candidate relationships, explicitly marked exploratory |
| `select_analysis_method()` | Method Registry constraint engine | Ranked `MethodPlan` |
| `run_descriptive_analysis()` | DuckDB/SciPy | Tables, distributions, uncertainty |
| `run_statistical_test()` | SciPy/statsmodels | Statistic, effect, uncertainty, assumptions |
| `fit_inferential_model()` | statsmodels | Model result + diagnostics |
| `fit_predictive_model()` | scikit-learn | Fitted pipeline + validation report |
| `compare_models()` | deterministic metric framework | Ranked models + uncertainty |
| `run_survey_analysis()` | R `survey` adapter | Survey-correct estimates |
| `run_causal_analysis()` | DoWhy/EconML adapters | Identified estimand, estimate, refutation report |
| `run_bayesian_analysis()` | PyMC | Posterior diagnostics and summaries |
| `run_spatial_analysis()` | GeoPandas | Validated geospatial outputs |
| `link_records()` | Splink | Links, probabilities, diagnostics |
| `analyse_network()` | NetworkX | Graph statistics |
| `make_visualisation()` | Altair | Vega-Lite/Altair specification |
| `validate_analysis()` | Method-specific test suite | `ValidationReport` |
| `build_evidence_bundle()` | Provenance code | Claims → results → data → code mapping |
 
Each skill should have a Pydantic/JSON Schema input and output contract. An agent therefore cannot call `run_survey_analysis()` without supplying survey design information, or `run_causal_analysis()` without an estimand and causal assumptions.
 
That is the sort of deterministic friction I would actively design into the system.
 
## Data discovery, source search and government context
 
The Data-Analyst needs two different search capabilities that should not be conflated:
 
**knowledge discovery** asks “How should this analysis be done?”
 
**data discovery** asks “What authoritative data exists, and what exactly does it mean?”
 
### Build source-specific connectors before generic web search
 
For frequently used Australian sources, specialised tools will be more reliable and considerably cheaper than repeatedly asking an LLM to browse websites.
 
The ABS is an obvious first target. Its Data API provides detailed economic, social and Census data and explicitly supports two modes: retrieval when the desired series is already known, and metadata-driven discovery when it is not. It uses the SDMX data/metadata model and can return CSV, JSON and XML. citeturn19view8turn19view9
 
I would expose this to the agent as:
 
```text
abs_search_dataflows(query, dimensions?)
abs_describe_dataflow(id)
abs_search_codes(dataflow, dimension, query)
abs_fetch_series(spec)
abs_get_metadata(id)
```
 
The LLM should never need to remember that an ABS series key happens to look like `M1.AUS.Q`, even though the underlying API uses multidimensional keys of this form. Your wrapper should resolve human intent into a validated request and preserve the actual SDMX query in provenance. citeturn19view9
 
There is an important freshness nuance: the ABS itself warns that its Beta API may not necessarily contain the most up-to-date information and advises using the ABS website for the most current information. citeturn19view8 I would therefore encode:
 
```text
if request.freshness == "latest":
    retrieve_api_data()
    verify_latest_release_metadata()
```
 
That is precisely the sort of subtle rule an LLM should not be expected to remember reliably.
 
METEOR deserves a similar wrapper for Australian health and human-services work because it is specifically a registry of metadata standards and exposes API access to that metadata. citeturn19view10
 
### Recommended source hierarchy
 
For analytical facts and definitions I would encode an explicit source preference order:
 
| Rank | Source class | Example | Default treatment |
|---:|---|---|---|
| Highest | Current legislation/regulator/government authority | OAIC, ONDC | Authoritative for applicable governance metadata; legal interpretation still escalates |
| Highest | National statistical agency/source publisher | ABS, AIHW | Preferred data and definitions |
| High | Official package documentation | SciPy, statsmodels, scikit-learn, DoWhy | Preferred executable-method reference |
| High | Peer-reviewed methodological work | Statistical methodology papers | Methodological evidence |
| Medium-high | Major textbooks | ISL | Conceptual guidance |
| Medium | Reviewed open-source government implementations | Splink | Implementation precedent |
| Conditional | Preprints | ChooseMyStat | Candidate method/design knowledge requiring validation |
| Low | Blogs/forums/issues | Community implementation discussion | Troubleshooting only, never sole methodological authority |
 
This also gives you a deterministic mechanism for resolving contradictory retrieval results: **source authority becomes a field rather than something the LLM improvises**.
 
### Tool and capability discovery
 
I would create a Postgres-backed **Capability Registry** separate from the RAG corpus.
 
A tool entry should contain at least:
 
```yaml
tool_id: splink.link_records
tool_family: entity_resolution
package: splink
 
capabilities:
  - deduplication
  - probabilistic_record_linkage
 
input_types:
  - tabular
 
execution:
  environment: sandbox
  network_required: false
 
privacy:
  sends_data_external: false
  maximum_data_classification: governed_by_local_runtime
 
constraints:
  requires_multiple_identifying_fields: true
 
cost:
  infrastructure: low
  model_tokens: none
 
documentation:
  authority: primary
  version: pinned
 
review:
  status: approved
  last_reviewed: ...
```
 
Tool selection then becomes:
 
```text
objective
  ↓
SQL filter Capability Registry
  ↓
eligible tools
  ↓
constraints checked against AnalysisSpec
  ↓
one tool → execute
multiple tools → use method ranking / inference
zero tools → search registry documentation / ask Researcher
```
 
This prevents an extremely dangerous agentic pattern: an LLM discovering some random new PyPI package on the internet and immediately installing it because its README sounds relevant.
 
### Search should progressively become less deterministic
 
I would use a four-stage retrieval cascade.
 
| Stage | Search mode | When used |
|---|---|---|
| **Registry** | SQL/filtering over structured Method Cards, source catalogue and capability manifests | Always first |
| **Local KB** | Hybrid keyword + vector retrieval over approved/versioned material | When interpretation is required |
| **Authoritative live source** | Source-specific API or constrained web search | Current releases, changed documentation, unknown datasets |
| **Researcher escalation** | Ask Council Researcher to conduct broader investigation | Novel methods, disputed evidence, unfamiliar domain |
 
That will dramatically reduce unnecessary embedding searches and inference tokens.
 
It also allows the Data-Analyst to distinguish:
 
> “I know which tool supports this.”
 
from:
 
> “I know what statistical technique is appropriate.”
 
from:
 
> “I found a package online which claims to implement it.”
 
Those are not equivalent propositions.
 
## Governance, reproducibility and Council interaction
 
The Data-Analyst is likely to encounter some of the most sensitive material in your entire Council because analysis often means bringing datasets together. This is particularly important in Australian Government contexts: the DATA Scheme specifically emphasises safe and responsible sharing, particularly where information relates to individuals, while the APPs establish obligations concerning personal-information collection, use/disclosure, governance, integrity and access. citeturn19view6turn19view7
 
The Analyst should therefore **recognise governance conditions without pretending to be the Governance Guru**.
 
### Escalation rules
 
| Trigger | Analyst action | Council escalation |
|---|---|---|
| Dataset contains personal information | Stop external-data egress; describe analytical requirement | Governance + Security |
| Proposed linkage increases identifiability | Produce linkage purpose/variables/necessity | Governance + Security |
| New external SaaS analysis service requested | Do not upload | Security |
| Data sharing authority unclear | Preserve metadata and stop | Governance |
| Source classifications/definitions conflict | Explain analytical consequence | Data Engineer / Governance as appropriate |
| Production pipeline required | Specify expected input contract | Data Engineer |
| Causal conclusion materially affects policy/program | Provide design/identification assessment | Researcher + Governance; human review where consequential |
| Indigenous evaluation context | Activate relevant Commonwealth evaluation guidance and cultural review | Governance / relevant human expertise; current Commonwealth guidance specifically stresses robust, ethical and culturally appropriate evaluation. citeturn22search32 |
| Novel method has no approved Method Card | No autonomous production use | Solution Architect / specialist |
| Coding agent encounters analysis-changing error | Freeze original plan; return diagnostic evidence | Data-Analyst |
| Analytical experts disagree | Preserve competing specifications/results | Solution Architect as Chair |
 
This is an area where your Council architecture has an advantage over a single “super-agent”: **uncertainty can be routed to an appropriate authority instead of being converted into hallucinated confidence.**
 
### Local-first analysis
 
For government-oriented work, I would make **local execution the default and external analytical web applications reference material rather than operational dependencies**.
 
SDA-V2, for example, asks users to upload a CSV into its application. citeturn20view1 That makes the software extremely useful as an implementation to study, but it is not a sensible default execution surface for sensitive Council data. The same principle should apply generally: reproduce validated open-source logic locally whenever feasible rather than shipping source datasets to third-party analytical services.
 
Your Modal sandbox / Oracle compute pattern fits this nicely:
 
```text
Sensitive input
     ↓
approved execution environment
     ↓
deterministic Python/R executable
     ↓
only derived approved artefacts exit
```
 
### Reproducibility should be mandatory, not aspirational
 
The Analyst should never be allowed to say “I ran a model” without enough information to recreate it.
 
At minimum, persist:
 
| Category | Persist |
|---|---|
| Data | source identifier, version/retrieval timestamp, content hash |
| Transformation | SQL/code and configuration |
| Dependencies | lockfile/container digest |
| Randomness | every explicit seed |
| Method | Method Card version |
| Model | hyperparameters and fitted-artifact hash where retained |
| Evaluation | train/test or resampling partitions |
| Output | values and machine-readable result objects |
| Source documentation | document identifier/version and retrieval timestamp |
| Agent judgment | structured rationale for non-deterministic choice |
| Council intervention | escalation, decision and approving actor |
| Code | Git commit SHA |
 
The scikit-learn documentation itself identifies controlling randomness, leakage and reproducible preprocessing as important concerns, reinforcing the case for making these properties part of execution infrastructure rather than prompt instructions. citeturn20view5
 
I would also distinguish **analytical reproducibility** from **answer reproducibility**. The first means running the same analysis again; the second means being able to reconstruct *why each sentence was written*. The evidence ledger gives you the latter.
 
### The Analyst's answer contract
 
Every substantial answer should follow a predictable semantic shape even when the prose varies:
 
| Component | Requirement |
|---|---|
| Answer | Direct answer to question |
| Evidence | Primary estimates/results |
| Uncertainty | Intervals/probabilities/validation uncertainty |
| Method | What was done and why |
| Quality | Whether data are fit for purpose |
| Assumptions | Material assumptions |
| Sensitivity | What happened under reasonable alternative specifications |
| Limitations | What cannot be concluded |
| Provenance | Data and methodological sources |
| Reproducibility | Analysis/run identifier |
| Escalations | Any unresolved governance/domain issues |
 
That would make the Data-Analyst's outputs far more useful to other Council agents than an ordinary chat response.
 
## Recommended build sequence and target architecture
 
I would resist launching the Analyst with every possible technique. The highest-value initial capability is not exotic modelling; it is **making ordinary analysis extremely difficult to do incorrectly and extremely easy to audit**.
 
### Capability priorities
 
| Priority | Component | Recommendation | Reason |
|---|---|---|---|
| **P0** | `AnalysisSpec` | Build | Foundation for every other decision |
| **P0** | Dataset profiler | Build around DuckDB | Cheap, deterministic, broadly reusable |
| **P0** | Data contracts | Pandera | Catches many failures before inference |
| **P0** | ABS DQF assessment | Custom structured implementation | Gives outputs an Australian-government-oriented quality language. citeturn19view4 |
| **P0** | Method Registry | Custom YAML/JSON/Postgres | Central deterministic reasoning layer |
| **P0** | SciPy | Integrate | Core statistics |
| **P0** | statsmodels | Integrate | Core inference |
| **P0** | scikit-learn | Integrate | Core ML/preprocessing/validation |
| **P0** | DuckDB | Integrate deeply | Analytical data plane and R2/Postgres fit. citeturn11view0 |
| **P0** | pandas / Arrow / Parquet | Integrate | Interoperability |
| **P0** | Evidence ledger | Build | Makes “defensible answer” concrete |
| **P0** | Reproducible run manifest | Build | Required for meaningful autonomy |
| **P0** | ABS API adapter | Build | High-probability Australian use case; API supports machine-readable discovery/retrieval. citeturn19view8turn19view9 |
| **P0/P1** | Altair | Integrate | Reproducible declarative graphics |
| **P1** | R `survey` adapter | Integrate | Materially important for official/survey data. citeturn22search7 |
| **P1** | GeoPandas | Integrate | Government geography/spatial work |
| **P1** | Splink | Integrate | High-value administrative-data linkage; already used by ABS according to project documentation. citeturn16view1 |
| **P1** | DoWhy | Integrate | Explicit causal reasoning/validation |
| **P1** | METEOR adapter | Build | Strong health/human-services metadata source. citeturn19view10 |
| **P1** | Commonwealth Evaluation KB | Ingest/structure | Policy/program evaluation alignment. citeturn22search0turn22search12 |
| **P1** | Australian classification registry | Build | Standard definitions and crosswalk handling. citeturn18search4 |
| **P1** | Polars | Install behind abstraction | Useful optimisation path without changing analytical semantics |
| **P2** | PyMC | Specialist integration | Bayesian/hierarchical questions |
| **P2** | EconML | Specialist integration | Heterogeneous causal effects |
| **P2** | NetworkX | Specialist integration | Graph/network cases |
| **P2** | Additional forecasting/NLP libraries | Add only from demonstrated demand | Avoid unnecessary dependency/method surface |
 
### What I would build from your existing ideas
 
Your original four starting references are all worth retaining, but I would change their roles:
 
| Your candidate | My recommendation |
|---|---|
| **ChooseMyStat** | **Mine it for decision-tree structure, question decomposition and analysis-plan patterns.** Do not install it as the universal selector. Its recent/preprint and clinical orientation argue for treating its rules as candidates that enter your own reviewed Method Registry. citeturn4search0 |
| **Smart Data Analysis V2** | **Use aggressively as a reference implementation.** Extract its EDA, assumption-checking and routing concepts, compare its code to your own rules, and create regression tests from representative examples. Do not make its nine-package scope the boundary of your Analyst. citeturn20view1turn20view2 |
| **ISL** | **Keep as the Analyst's high-quality conceptual statistical-learning handbook.** Its breadth and Python labs make it especially useful for explanation and method context. citeturn20view3 |
| **scikit-learn User Guide** | **Make it both KB material and implementation documentation.** In particular, ingest model-selection, evaluation, inspection, preprocessing and pitfalls sections and bind documentation versions to your installed version. citeturn20view4turn20view5 |
 
### Proposed LangGraph shape
 
Within your existing architecture, I would aim for something close to:
 
```text
                         ┌─────────────────────┐
                         │     User question   │
                         └──────────┬──────────┘
                                    ↓
                         ┌─────────────────────┐
                         │ Intent / AnalysisSpec│ ← LLM judgement
                         └──────────┬──────────┘
                                    ↓
                         ┌─────────────────────┐
                         │ Governance preflight│ ← rules
                         └──────────┬──────────┘
                                    ↓
                         ┌─────────────────────┐
                         │ Data discovery      │ ← source registry/APIs
                         └──────────┬──────────┘
                                    ↓
                         ┌─────────────────────┐
                         │ Profile + validate  │ ← DuckDB/Pandera
                         └──────────┬──────────┘
                                    ↓
                         ┌─────────────────────┐
                         │ Fit-for-purpose DQ  │ ← ABS DQF rules
                         └──────────┬──────────┘
                                    ↓
                         ┌─────────────────────┐
                         │ Method constraint   │ ← Method Registry
                         │ solver              │
                         └──────────┬──────────┘
                                    ↓
                    multiple? ─────┴───── one?
                       ↓                     ↓
             ┌──────────────────┐            │
             │ LLM adjudication │            │
             └────────┬─────────┘            │
                      └───────────┬───────────┘
                                  ↓
                         ┌─────────────────────┐
                         │ Analysis plan       │
                         └──────────┬──────────┘
                                    ↓
                         Council/user approval
                                    ↓
                         ┌─────────────────────┐
                         │ Sandbox execution   │ ← Python/R/SQL
                         └──────────┬──────────┘
                                    ↓
             ┌──────────────────────────────────┐
             │ Deterministic validation suite   │
             └────────────────┬─────────────────┘
                              ↓
                    ┌──────────────────┐
                    │ Analytical critic│ ← LLM judgement
                    └─────────┬────────┘
                              ↓
                 failure ─────┴──── success
                    ↓                 ↓
              revise/escalate   Evidence ledger
                                      ↓
                                Final synthesis
                                      ↓
                              Council / user
```
 
Langfuse can then observe not merely prompts and token usage, but **which analytical pathways are being selected**. I would log fields such as `objective`, `method_id`, rejected methods, escalation reason, validation failures, correction loops, data-quality score/flags and whether the final answer survived the first validation pass. That gives you a much more meaningful evaluation surface than generic “agent success”.
 
### The most important design choice
 
The greatest risk in this agent is probably **not an incorrect arithmetic calculation**. Python will usually get arithmetic right. It is that an extremely articulate system performs the wrong analysis correctly: wrong unit, wrong population, wrong comparison, ignored survey weights, leakage between train and test, a causal interpretation of observational association, incompatible geographic classifications, an inappropriate join, or a technically significant result that has no practical decision relevance.
 
Existing tools already solve much of the computation. SciPy, statsmodels and scikit-learn collectively provide an enormous executable analytical surface; specialist packages such as `survey`, DoWhy, GeoPandas and Splink cover important cases that general-purpose modelling does not. citeturn10view3turn13view0turn19view2turn22search7turn16view0turn14search20turn16view1
 
The custom intellectual property worth building for **The Council** is therefore the layer above them:
 
> **Question → explicit estimand → data fitness → permissible methods → deterministic execution → independent validation → evidence-linked claim.**
 
That architecture also satisfies your cost objective. The frequent, mechanical parts of analysis—profiling, joins, quality checks, transformations, statistics, model fitting, diagnostics, charts, source retrieval and reproducibility—can happen through ordinary code. Expensive inference is concentrated at the relatively few points where human-like judgment is genuinely valuable: framing ambiguous questions, adjudicating between multiple defensible analyses, interpreting context, challenging a result and explaining it.
 
The resulting Data-Analyst would consequently be much harder to fool with a plausible-looking dataset and much easier for a later human expert to audit. Instead of asking that reviewer to reverse-engineer an AI's reasoning, you can hand them the `AnalysisSpec`, source manifest, data-quality report, Method Card, exact execution artefacts, validation report and evidence ledger—and let them concentrate on the few decisions where expertise was actually required.
