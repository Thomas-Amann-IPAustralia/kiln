# Proposal for the Security Architect in “The Council”
 
## Executive recommendation
 
The Security Architect should not primarily be built as a conversational expert with a very large pile of cybersecurity documents. I would build it as a **security policy, architecture and assurance agent backed by a versioned control catalogue and a deterministic security toolchain**.
 
That distinction matters. In an Australian Government context, “what is good security practice?” and “what is required for this particular system?” are different questions. The Australian Government Protective Security Policy Framework was substantially reorganised in its 2026 release and now operates across six security domains; the 2026 release also introduced changes relating to matters such as AI, post-quantum cryptography and BYOD. The Information Security Manual remains ASD's risk-based cybersecurity framework, while the Essential Eight is a deliberately narrower baseline of mitigation strategies. ASD explicitly cautions that the Essential Eight was designed principally for internet-connected enterprise IT rather than every conceivable environment. citeturn1search2turn1search6turn8search4
 
This argues strongly against embedding a static set of “security rules” into the Security Architect's prompt. Instead, I recommend the following architecture:
 
| Layer | What the Security Architect should do | Why |
|---|---|---|
| **Authoritative requirements** | Determine applicable PSPF, ISM, Essential Eight and other Australian Government requirements from a structured project profile. | These should outrank generic industry advice. PSPF Release 2026 is the current Australian Government protective-security policy framework, while the ISM supplies risk-based cybersecurity controls. citeturn1search30turn8search4 |
| **Verification standards** | Turn requirements into testable engineering requirements using standards such as OWASP ASVS/MASVS and NIST controls. | A “Top 10” list identifies common problems; a verification standard is much better suited to determining what must actually be tested. OWASP maintains both risk-awareness projects and verification/testing standards. citeturn11search0turn19search6 |
| **Threat knowledge** | Use structured threat/weakness catalogues such as CWE, CAPEC, MITRE ATT&CK/ATLAS and OWASP agentic-AI risks to enrich threat modelling. | CWE is machine-accessible and describes underlying software/hardware weaknesses, while CAPEC supplies structured adversary attack patterns useful throughout design, implementation and verification. citeturn21view1turn20search16 |
| **Deterministic assurance** | Run SAST, secrets, dependency, SBOM, IaC/container, policy and supply-chain checks automatically. | These questions generally do not require an LLM. Existing open-source tools can produce repeatable machine-readable results. citeturn12search0turn12search2turn13search11turn14search0 |
| **Reasoning** | Interpret architecture, construct abuse cases, resolve ambiguous findings, propose mitigations and explain trade-offs. | This is where inference adds genuine value. |
| **Evidence** | Associate each security decision with source requirements, tests, evidence and exceptions. | The PSPF's contemporary reporting model places considerable emphasis on evidence-based compliance and assurance rather than unsupported assertions of compliance. citeturn1search34 |
| **Escalation** | Escalate exceptions and material risk decisions rather than silently relaxing controls. | This preserves the useful autonomy of the coding swarm without allowing an agent to redefine acceptable risk for the organisation. |
 
The core design principle I would adopt is:
 
> **Inference proposes; deterministic controls test; authoritative sources decide applicability; humans accept material residual risk.**
 
This also fits your cost objective unusually well. Most of the recommended assurance components below are open-source and can execute transiently in CI or Modal rather than requiring another permanent platform. The expensive LLM should be invoked mainly where human-like architectural interpretation is useful.
 
One particularly important finding from the research is that **the Security Architect for your Council needs substantially more AI/agent security expertise than a conventional application-security architect**. ASD's September 2026 guidance on agentic-AI harnesses identifies the harness—the layer connecting the model to tools, data, memory, execution privileges and its control loop—as a major security control point. ASD specifically warns that tools, connectors, external information and memory increase attack surface, and that substantial risks arise from the privileges an agent is able to exercise. citeturn4search7
 
That description is almost exactly your proposed system.
 
## The knowledge base
 
### A hierarchy rather than a document collection
 
I would organise the Security Architect's knowledge into tiers. This lets the agent distinguish between a mandatory Australian Government requirement, a useful verification standard, a threat catalogue and implementation advice.
 
The agent should **never resolve a conflict by whichever chunk happens to have the highest vector similarity**.
 
| Priority | Knowledge set | Role in the agent | Recommended treatment |
|---|---|---|---|
| **P0 — Australian authoritative** | PSPF Release 2026 | Determine Australian Government protective-security obligations and expected outcomes. PSPF Release 2026 is the current whole-of-government framework and now comprises six security domains. citeturn1search2turn1search30 | Structured control catalogue + exact-source retrieval. Monitor for annual releases and advisories. |
| **P0 — Australian authoritative** | ASD Information Security Manual | Primary technical cybersecurity-control source for Australian Government-oriented solutions. ASD describes the ISM as a cyber security framework organisations apply using their risk-management framework. citeturn8search4 | Parse control identifiers, applicability and guidance separately rather than treating it as undifferentiated prose. |
| **P0 — Australian authoritative** | Essential Eight Maturity Model + assessment guidance | Baseline hardening and maturity assessment. Essential Eight controls map into the ISM, but ASD cautions they are primarily intended for internet-connected enterprise IT. citeturn0search0turn8search4 | Encode maturity checks where they are mechanically testable. Do not treat E8 as the complete security architecture. |
| **P0 — Australian authoritative** | PSPF–Essential Eight relationship | Important applicability knowledge. Under current PSPF arrangements, non-corporate Commonwealth entities need Essential Eight Maturity Level Two mitigations to achieve the relevant PSPF “Managing” outcome. citeturn1search14 | Applicability rule rather than RAG text. |
| **P0 — Australian authoritative** | ASD Secure by Design | Design principles covering security throughout design, development and deployment; ASD explicitly identifies built-in controls such as MFA and logging as secure-by-default characteristics. citeturn8search2turn8search20 | Use as architecture-review rubric. |
| **P0 — AI-specific Australian guidance** | ASD *Guidelines for secure AI system development* | Covers secure design, development, deployment, operation, supply chains, infrastructure/model protection, incident management and logging. citeturn1search3 | Mandatory retrieval whenever the proposed solution contains AI. |
| **P0 — AI-specific Australian guidance** | ASD *Agentic AI harnesses* and *Careful adoption of agentic AI services* | Directly relevant to the Council itself and to solutions containing agents. ASD focuses on privileges, tool/data/memory integration, harness controls and defence in depth; its broader agentic guidance references OWASP Agentic Top 10, OWASP GenAI risks, NIST AI RMF, NIST Zero Trust and MITRE ATLAS. citeturn4search7turn4search35 | Make this a first-class security domain, not an appendix. |
| **P0/P1 — Australian hosting** | Whole-of-Government Hosting Certification Framework | Relevant where Australian Government information, sensitive workloads or government cloud-hosting requirements enter scope. The framework exists to provide enhanced privacy, sovereignty and security assurances and support PSPF/ISM requirements. citeturn6search27turn6search31 | Applicability rule triggered by government hosting/data classification. |
| **P1 — assurance** | IRAP information and assessment guidance | Gives the agent context for what a later independent Australian Government security assessment will examine. ASD describes IRAP assessors as independent assessors who identify control strengths, weaknesses and mitigations. citeturn8search0 | Use to make prototypes “assessment-ready”; do not let the agent represent its own review as IRAP certification. |
| **P1 — application requirements** | OWASP Application Security Verification Standard | Convert vague “secure application” requirements into verifiable application-security requirements. OWASP positions ASVS among its principal application-security resources. citeturn11search0 | Structured requirements/checklist, preferably preserving stable requirement IDs. |
| **P1 — application testing** | OWASP Web Security Testing Guide | Testing procedures for web applications and services. The official WSTG repository is a comprehensive open-source web-security testing guide. citeturn11search34 | Retrieve only the relevant test category for the architecture/component being assessed. |
| **P1 — implementation guidance** | OWASP Cheat Sheet Series | Keep your proposed inclusion. It is extremely useful as implementation guidance after a requirement has been identified. | Git-sync Markdown; classify as **guidance**, not the policy authority. |
| **P1 — risk awareness** | OWASP Top 10 | Useful taxonomy and awareness layer. OWASP's current general web Top 10 is the 2025 edition. citeturn11search0 | Map to ASVS/CWE/control IDs; don't make “passes Top 10” synonymous with secure. |
| **P1 — maturity** | OWASP SAMM | Gives the agent a measurable model for assessing and improving software security practices rather than individual vulnerabilities. citeturn4search1turn4search9 | Useful when Council advice concerns SDLC/process maturity. |
| **P1 — mobile** | OWASP MASVS/MASWE/MASTG | MASVS defines baseline mobile security/privacy requirements and links those requirements to weakness and testing material. citeturn19search6 | Load when the solution has mobile clients. |
| **P1 — agentic AI** | OWASP Top 10 for Agentic Applications 2026 | Highly relevant to both the Council and agentic solutions it produces. The 2026 project was developed as an agentic-application risk taxonomy with broad expert review. citeturn5search1 | Map risks directly to your harness guardrails and threat-model schema. |
| **P1 — GenAI** | OWASP GenAI/LLM Top 10 | Current GenAI risk material for LLM-enabled applications; the 2026 edition followed the earlier LLM Top 10 work. citeturn5search11turn5search15turn19search13 | Trigger for any RAG, LLM, multimodal or model-integrated system. |
| **P1 — AI verification, emerging** | OWASP AISVS | A structured AI-security verification initiative. It is promising for converting AI guidance into testable requirements but should be treated as an emerging source rather than an Australian Government authority. citeturn11search25 | Watch/version separately; don't make it a hard compliance gate until mature enough for your use. |
| **P1 — AI scoring, emerging** | OWASP AIVSS | Developing a quantifiable methodology for AI-specific vulnerability assessment, initially focused on agentic risks. citeturn19search25 | Candidate scoring enrichment, not sole risk-acceptance algorithm. |
| **P1 — security controls** | NIST SP 800-53 | Large, structured security/privacy control catalogue useful for filling gaps and mapping controls. NIST publishes machine-readable OSCAL material and mappings alongside SP 800-53. citeturn3search3turn3search27 | Particularly valuable as a machine-readable reference and crosswalk source. |
| **P1 — lifecycle risk** | NIST Risk Management Framework | Gives the agent a disciplined system-development lifecycle for selecting, implementing, assessing and monitoring controls, including privacy and supply-chain considerations. citeturn3search14 | Use as process model rather than another flat checklist. |
| **P1 — organisational framework** | NIST CSF 2.0 | Useful common taxonomy for describing security outcomes and communicating risk beyond the security specialist. NIST also provides informative-reference material for mapping other controls into the CSF. citeturn9search2 | Cross-reference rather than duplicate controls. |
| **P1 — AI governance/risk** | NIST AI RMF + Generative AI Profile | International complement to ASD AI guidance. NIST publishes the AI RMF and its Generative AI Profile for GenAI-specific risk management. citeturn3search22 | Jointly accessible by Security Architect and Governance Guru. |
| **P1 — zero trust** | NIST SP 800-207 | Useful architectural reference for identity- and resource-centred access decisions rather than relying on network location as trust. citeturn9search33 | Especially relevant to Council tool access and service-to-service design. |
| **P1 — weakness taxonomy** | MITRE CWE | Machine-readable catalogue of software and hardware weaknesses. The current CWE site exposes downloads and a REST API, making it much more useful than prose-only RAG content. citeturn21view1 | **Do not vectorise as the primary representation.** Ingest IDs, relationships, categories and mappings structurally. |
| **P1 — attack patterns** | MITRE CAPEC | Catalogues common adversarial attack patterns and explicitly supports architecture analysis, requirements, verification and penetration-testing use cases; downloadable structured forms include CSV/XML. citeturn20search9turn20search16turn20search22 | Excellent candidate for a threat-model expansion tool. |
| **P1 — AI adversary behaviour** | MITRE ATLAS | ASD itself identifies MITRE ATLAS among relevant references when considering agentic AI security. citeturn4search35turn21view0 | Load for AI threat modelling, not every conventional CRUD app. |
| **P1 — software supply chain** | SLSA | Provides an approved specification with progressively stronger supply-chain guarantees, source/build tracks and provenance/attestation formats. citeturn18view2turn18view3 | Use as release/build-pipeline architecture guidance. |
| **P1 — BOM standard** | CycloneDX | Current specification can represent software, services, dependencies, cryptographic assets and other supply-chain information; project guidance also covers SBOM, cryptographic BOM and AI/ML BOM use cases. citeturn16search14turn16search10 | I would standardise Council-generated SBOM interchange on CycloneDX unless a consuming system requires SPDX. |
| **P1 — BOM standard** | SPDX | Open international standard for BOM information and increasingly broader AI/data/system metadata. citeturn16search3turn16search27 | Support as an interchange format; avoid unnecessarily maintaining two internal canonical models. |
| **P2 — source/dependency assurance** | OpenSSF Scorecard knowledge | Provides automated heuristics for source-project security practices such as pinned dependencies, code review, token permissions, SAST and vulnerabilities. Its own documentation explicitly cautions that the aggregate score is not a definitive judgement. citeturn17view0 | Use individual findings as signals, **not an “8/10 = safe” purchasing rule**. |
| **P2 — crosswalk/index** | OpenCRE | Open Cybersecurity Requirement Expression is intended to link security requirements across standards and frameworks. citeturn11search2 | Very valuable as a crosswalk/navigation layer, but keep the originating standard as the authoritative source. |
 
### Why OpenCRE and OSCAL are particularly interesting for you
 
One of the strongest “the work has already been done” opportunities is **not another vector database**. It is using existing control identifiers and mappings.
 
OpenCRE exists specifically to link requirements across security standards. NIST publishes SP 800-53 material through OSCAL and provides framework mappings. CWE exposes an API and structured downloads, while CAPEC exposes machine-readable catalogues. citeturn11search2turn3search27turn21view1turn20search22
 
I would therefore make the Security Architect's underlying knowledge model resemble a small security knowledge graph:
 
```text
Australian requirement
       │
       ├── maps_to ──> implementation requirement
       │                    │
       │                    ├── mitigates ──> CWE / CAPEC / AI risk
       │                    ├── verified_by ─> automated check
       │                    └── evidenced_by -> artifact/test/report
       │
       ├── maps_to ──> NIST / OWASP requirement
       │
       └── exception ─> decision + approver + expiry
```
 
A normalised `security_requirement` object could contain:
 
```yaml
id: "internal:SEC-AUTH-001"
source:
  authority: "ASD"
  document: "ISM"
  source_id: "<original control identifier>"
  version: "<source version>"
  retrieved_at: "<timestamp>"
authority_level: "australian-government-authoritative"
 
applicability:
  internet_facing: true
  authentication: true
  information_classification: ["OFFICIAL", "OFFICIAL:SENSITIVE"]
  ai_system: false
 
requirement_summary: "..."
normative_text_reference: "..."
 
mappings:
  owasp_asvs: ["..."]
  nist_800_53: ["..."]
  cwe: ["..."]
 
verification:
  automated:
    - check_id: "..."
      tool: "..."
  manual:
    - evidence_required: "..."
 
status: applicable
exception:
  allowed: false
```
 
The important thing is that the LLM sees **structured applicability and provenance**, not just semantically similar paragraphs.
 
### Retrieval strategy
 
I would use the following retrieval sequence rather than ordinary “RAG over everything”:
 
| Order | Retrieval mechanism | Example | Inference required? |
|---|---|---|---|
| First | **Applicability rules** | “This is a non-corporate Commonwealth entity; this system is internet-facing; it processes OFFICIAL:SENSITIVE; it contains GenAI.” | Mostly no |
| Second | **Exact identifier lookup** | ISM control, ASVS requirement, CWE-79, CAPEC ID. | No |
| Third | **Structured crosswalk traversal** | ISM requirement → related OWASP test → CWE weakness → automated scanner. | No |
| Fourth | **Keyword/BM25 retrieval** | Exact authentication/session-management terminology. | No |
| Fifth | **Vector retrieval** | “Find design guidance conceptually similar to this unusual architecture.” | Some |
| Sixth | **LLM synthesis** | Explain conflicts, propose architecture, create abuse cases. | Yes |
| Seventh | **Live authoritative lookup** | Determine whether ASD, PSPF, OWASP, NIST or a provider has published a newer version. | Yes, but source-constrained |
 
This is particularly important because the Australian source set is changing. PSPF Release 2026 was issued on 1 July 2026, and ASD has also been consulting on an evolution of the Essential Eight into broader enterprise-IT essentials. A frozen embedding corpus could therefore quietly become wrong. citeturn1search30turn0search24
 
I recommend giving every ingested source:
 
`source_authority`, `document_id`, `version`, `effective_date`, `retrieved_at`, `content_hash`, `supersedes`, `jurisdiction`, `scope`, `normative/advisory`, and `canonical_source`.
 
Your custom ingestion approach is perfectly suitable for this. **I would not add LlamaIndex merely to make ingestion more sophisticated unless maintaining the ingestion pipeline actually becomes painful.** Your bigger challenge is metadata and control semantics, not document parsing.
 
## The toolkit
 
### Recommended low-cost baseline
 
The Security Architect should rarely execute arbitrary shell commands directly. Give it **narrow, typed tool wrappers** which invoke trusted deterministic tools in a sandbox and return normalised results.
 
A pragmatic baseline looks like this:
 
| Capability | Recommended tool | Why it belongs | Proposed Council use | Priority |
|---|---|---|---|---|
| Policy-as-code | **Open Policy Agent / Rego** | OPA is an open-source general-purpose policy engine that evaluates structured inputs against declarative policies and is explicitly suitable for CI/CD, APIs, microservices and infrastructure. citeturn18view0 | Encode Council rules such as permitted public exposure, required authentication, approved registries, agent tool privileges and mandatory evidence. | **Core** |
| Config/IaC policy testing | **Conftest** | Evaluates structured configuration such as Terraform, Kubernetes and other configuration against Rego policies. citeturn18view1 | `security.validate_config()` before a coding agent can merge infrastructure changes. | **Core** |
| SAST | **Semgrep CE** | Open-source static analysis engine with broad language support and community rules; it can execute locally, making it suitable for low-cost deterministic scanning. citeturn12search0turn12search16 | Run targeted rules based on language/framework and convert findings to one Council finding schema. | **Core** |
| Secret detection | **Gitleaks** | Open-source scanner for passwords, API keys and tokens in repositories/files/input. citeturn12search2 | Pre-commit/PR scan plus explicit “no secret committed” release gate. | **Core** |
| Dependency vulnerability scanning | **OSV-Scanner** | Official OSV frontend for identifying vulnerabilities in project dependencies; OSV also provides CI-oriented scanning workflows. citeturn13search11turn13search3 | Scan manifests/lockfiles on every material dependency change. | **Core** |
| Broad vulnerability/IaC/container scanning | **Trivy** | Open-source scanner for repositories, binary artifacts, container images and Kubernetes, including CVEs and IaC misconfiguration; it can also consume CycloneDX/SPDX SBOMs. citeturn14search0turn14search32 | Broad baseline scanner, especially for generated Dockerfiles, containers and IaC. | **Core** |
| SBOM generation | **Syft** | Open-source CLI/library designed to generate SBOMs from container images and filesystems. citeturn13search6 | Generate release SBOM as evidence. | **Core if shipping artifacts** |
| BOM schema | **CycloneDX** | Current schema supports components, services and dependency relationships, with security-oriented BOM capabilities. citeturn16search14turn16search18 | Make this the default internal SBOM format. | **Core** |
| Component inventory & continuous supply-chain monitoring | **OWASP Dependency-Track** | Open-source component-analysis platform that consumes CycloneDX and monitors components, vulnerabilities and policy violations. citeturn13search4turn13search26 | Optional central inventory once multiple produced applications make one-off CI reports inconvenient. | **Phase two** |
| OSS dependency/project due diligence | **OpenSSF Scorecard** | Automates security-health heuristics for open-source repositories and exposes CLI/API/GitHub Action modes. Its individual checks cover practices such as code review, SAST, token permissions, pinning and vulnerabilities. citeturn17view0 | Run when the agent proposes a material new OSS dependency, framework or GitHub Action. | **Core** |
| Artifact signing | **Sigstore Cosign** | Sigstore is designed to sign and verify software artifacts; Cosign supports artifact signatures and transparency mechanisms. citeturn14search3turn14search15turn14search19 | Sign release images/SBOMs/attestations after successful gates. | **Phase two** |
| Build provenance | **SLSA** | Defines increasing supply-chain guarantees and standard provenance/verification concepts. citeturn18view2turn18view3 | Define what evidence generated builds must carry. | **Phase two** |
| Threat modelling as code | **Threagile** | Open-source threat-modelling toolkit representing architecture/assets in YAML and evaluating standard/custom risk rules. citeturn19search3 | Candidate deterministic threat-model engine behind a Council wrapper. | **Evaluate first** |
| Web-security verification corpus | **OWASP WSTG** | Comprehensive open-source procedures for testing web applications and services. citeturn11search34 | Let the Security Architect choose relevant tests and ask coding/testing agents to implement or execute them. | **Core knowledge, selective execution** |
| Mobile verification | **OWASP MASVS/MASTG** | Provides a requirements-to-testing system specifically for mobile applications. citeturn19search6 | Activate only for mobile projects. | **Conditional** |
| WAF rules | **OWASP Core Rule Set** | OWASP maintains a generic attack-detection ruleset for ModSecurity/Coraza-class WAFs. citeturn5search26turn19search32 | Recommendation when a solution actually needs a WAF; not a blanket architectural requirement. | **Conditional** |
| Control crosswalking | **OpenCRE + your local mappings** | Connects requirements across frameworks rather than forcing the LLM to rediscover equivalence. citeturn11search2 | `security.map_requirement()` and control deduplication. | **Core knowledge service** |
| Weakness lookup | **CWE REST/structured dataset** | CWE exposes a machine-readable catalogue and REST API. citeturn21view1 | `security.lookup_weakness("CWE-...")`; enrich SAST findings deterministically. | **Core** |
| Attack-pattern lookup | **CAPEC structured dataset** | CAPEC is downloadable and explicitly intended to inform design, requirements, testing and verification. citeturn20search16turn20search22 | Expand threat models without prompting an LLM to invent attacks from scratch. | **Core** |
 
### Deliberate overlap is useful, but duplication is not
 
I would **not** run every scanner simply because it is free.
 
For example, Trivy, Syft, OSV-Scanner and Dependency-Track overlap, but their useful roles differ:
 
```text
source repository
     │
     ├─ Gitleaks ───────────── secrets
     ├─ Semgrep ────────────── source-code weaknesses
     ├─ OSV-Scanner ────────── dependency vulnerabilities
     ├─ Trivy ──────────────── image/IaC/package baseline
     │
     └─ Syft ──> CycloneDX SBOM
                    │
                    └─ Dependency-Track
                         continuous inventory/policy monitoring
```
 
Trivy itself can produce and consume SBOM information, so you may eventually decide Syft adds insufficient marginal value. Trivy supports scanning CycloneDX and SPDX input, while Syft's primary purpose is SBOM generation. citeturn14search32turn13search6
 
That is exactly the sort of decision I would **benchmark once and turn into pipeline configuration**, rather than let the Security Architect repeatedly reason about which tool it feels like using.
 
### A security wrapper API
 
Rather than expose each CLI directly to the LLM, I would give the agent functions resembling:
 
| Council tool | Deterministic implementation | LLM's job |
|---|---|---|
| `build_security_profile(project)` | JSON Schema validation + classification rules | Identify ambiguous project characteristics. |
| `get_applicable_controls(profile)` | SQL/rules/OPA | Explain resulting control set. |
| `lookup_requirement(id)` | Exact database lookup | Interpret in architecture context. |
| `map_requirement(id)` | OpenCRE/local graph mappings | Explain mappings where useful. |
| `validate_architecture(model)` | OPA + deterministic architecture rules | Identify novel risks rules do not cover. |
| `generate_threat_candidates(model)` | CAPEC/CWE/ATLAS/OWASP retrieval first | Rank and contextualise threats. |
| `run_code_security(repo, diff)` | Semgrep + Gitleaks + OSV | Triage/contextualise findings. |
| `run_artifact_security(image)` | Trivy | Explain exploitable versus irrelevant findings, but **not silently suppress them**. |
| `generate_sbom(artifact)` | Syft/CycloneDX | None normally. |
| `assess_dependency(package)` | OSV + OpenSSF Scorecard + licence metadata | Recommend accept/reject/alternative. |
| `validate_config(files)` | Conftest/OPA/Trivy | Propose remediation. |
| `verify_release(release)` | required-check matrix | Explain why release is blocked. |
| `record_security_decision(decision)` | JSON Schema + DB write | Supply rationale. |
| `request_security_exception(control)` | Workflow/rules | Prepare case; cannot self-approve. |
| `diff_attack_surface(old,new)` | architecture-model comparison | Reason about newly introduced pathways. |
| `get_current_authoritative_guidance(topic)` | Domain-restricted retrieval | Synthesise only after retrieving current source. |
 
The scanner outputs should be normalised into one finding object rather than dumped into the model:
 
```yaml
finding_id: SEC-2026-00421
source_tool: semgrep
category:
  cwe: CWE-89
severity: high
confidence: high
 
asset:
  repo: example-api
  file: src/query.py
  line: 142
 
evidence:
  raw_artifact: r2://...
  artifact_hash: ...
 
applicable_controls:
  - internal:SEC-INPUT-003
  - owasp:...
 
disposition: open
 
agent_analysis:
  exploitable: likely
  rationale: "User-controlled value reaches query construction."
  confidence: 0.91
 
exception:
  status: none
```
 
Raw evidence can remain outside the prompt; the Security Architect sees the structured finding and retrieves the necessary fragment when required.
 
### Use policy-as-code much more aggressively than ordinary RAG
 
OPA is especially well suited to your preference for deterministic behaviour because it lets arbitrary structured information be evaluated against declarative rules and can return structured decisions, not merely yes/no answers. citeturn18view0
 
Examples worth encoding immediately:
 
```text
DENY deployment IF:
    public_endpoint = true
    AND authentication_required = true
    AND authentication_design_reviewed != true
 
DENY agent_tool_binding IF:
    tool.can_execute_code = true
    AND execution_environment.sandboxed != true
 
DENY agent_tool_binding IF:
    tool.has_production_credentials = true
    AND human_approval != true
 
DENY pull_request IF:
    security.high_findings > 0
    AND approved_exception IS NULL
 
DENY release IF:
    sbom_generated != true
    OR secrets_scan_passed != true
    OR dependency_scan_passed != true
 
REQUIRE council_review IF:
    data_classification_changed = true
    OR internet_exposure_added = true
    OR identity_architecture_changed = true
    OR new_external_processor = true
```
 
This gives you a major benefit: **the agent can explain a decision, but it cannot hallucinate the existence of an approval that the underlying state machine does not contain.**
 
## Agentic-system security should be its own specialty
 
Your Security Architect has two jobs:
 
1. secure the software the Council produces; and
2. secure **the Council's ability to produce and manipulate software**.
The second is arguably the more unusual and important responsibility.
 
ASD's current agentic-AI guidance says that the harness controls how the model interacts with tools, data sources, memory, planning and execution privileges, and stresses phased adoption, data classification, access management, monitoring, incident response and validating controls before expanding deployment. citeturn4search7 ASD's broader 2026 agentic guidance explicitly points practitioners toward OWASP's Agentic Top 10, OWASP's GenAI risks, MITRE ATLAS, NIST AI RMF and zero-trust material. citeturn4search35
 
### Threats I would explicitly model in the Council
 
| Threat | Example in your architecture | Primary mitigation |
|---|---|---|
| **Indirect prompt/goal injection** | Coding agent reads a README, issue, webpage, package metadata or source comment telling it to ignore Council instructions or exfiltrate credentials. | Treat retrieved content as **data, never policy**; label source provenance; prohibit data from modifying system/tool policy. OWASP maintains dedicated GenAI and agentic-risk guidance, while ASD now treats agentic harnesses as a security boundary. citeturn19search13turn5search1turn4search7 |
| **Tool privilege abuse** | A compromised agent uses GitHub, DB or shell privileges for something unrelated to its task. | Per-agent capability lists; action-specific credentials; OPA authorization before side effects; no shared “Council admin token”. ASD highlights access and action privileges as a significant source of agentic risk. citeturn4search7 |
| **Unexpected code execution** | Malicious dependency/test code executes on a machine attached to the Council's persistent private network. | Execute untrusted/generated code only in ephemeral sandbox environments with explicit filesystem, network, secret and runtime limits. |
| **Credential exfiltration** | Generated code prints environment variables or posts them to an external endpoint. | Do not place unrelated secrets in execution environments; default-deny sensitive egress; use short-lived scoped credentials. GitHub's security guidance similarly emphasises least-privilege workflow tokens and warns that secrets can leak through logs or compromised actions. citeturn21view2 |
| **Memory poisoning** | A coding agent writes “security review approved” into persistent agent memory; subsequent agents treat it as authority. | Separate observations from approved security state; only deterministic workflow functions can change approval fields. |
| **Cross-agent confused deputy** | A low-privilege coding agent asks Security Architect or Solution Architect to invoke a privileged operation on its behalf. | Carry original caller identity and requested purpose through tool calls; authorise on the **effective principal**, not merely the privileged intermediary. |
| **Supply-chain compromise** | Coding agent installs an obscure package suggested by generated code. | OSV + OpenSSF Scorecard + SBOM + pinning/lockfiles; material dependencies receive deterministic due diligence. Scorecard is explicitly intended to help consumers assess dependency security signals, while warning that its heuristics are not definitive. citeturn17view0 |
| **Malicious CI action** | Agent adds `uses: random/action@main`. | Policy requiring approved actions and full commit-SHA pinning. GitHub states that a full-length commit SHA is the only way to use an Action as an immutable release reference. citeturn21view2 |
| **Agent-to-agent instruction spoofing** | “Security Architect approved this” appears in an ordinary message. | Decisions are database objects carrying actor identity, timestamp and decision ID; prose cannot confer approval. |
| **Unbounded autonomy/resource consumption** | Swarm repeatedly rebuilds, scans or calls LLMs because remediation causes another error. | Per-task iteration, token, execution-time and monetary budgets plus bounded retry policies. |
| **Cascading change** | Coding agent fixes a finding by altering authentication, network topology or encryption architecture. | “Change classes” automatically re-open Council review when sensitive architectural fields change. |
| **Sensitive telemetry leakage** | Prompts/source code/secrets are captured by agent tracing. | Classification-aware telemetry filter; redact/drop before tracing rather than attempting post-hoc cleanup. |
| **Security-agent capture** | Malicious repository content persuades the Security Architect itself that a vulnerability should be ignored. | Scanner finding remains authoritative evidence; LLM may recommend disposition but suppression requires a structured exception according to policy. |
| **Model/provider dependency risk** | Security process relies on one frontier-model provider or sends sensitive material to it. | Explicit provider/data-flow register and risk assessment. ASD's 2026 frontier-AI advice highlights both AI-enabled threats and risks arising from reliance on AI providers and cyber supply chains. citeturn19search8 |
 
### Build the harness around capabilities, not “agent trust”
 
A useful conceptual model is:
 
```text
                      ┌──────────────────────┐
                      │    Council policy    │
                      │ OPA / state machine  │
                      └──────────┬───────────┘
                                 │ allow?
                                 ▼
┌─────────┐   request   ┌────────────────────┐    scoped call    ┌──────────────┐
│  Agent  │ ──────────> │ Capability broker  │ ────────────────> │ External tool│
└─────────┘             └────────────────────┘                   └──────────────┘
     │                           │
     │                           ├── caller identity
     │                           ├── task identity
     │                           ├── target resource
     │                           ├── approved scope
     │                           ├── credential scope
     │                           └── audit record
     │
     └──────── no direct privileged credential ────────X
```
 
I would not give the Security Architect unrestricted credentials simply because it is the *Security* Architect. In a compromised-agent scenario, that makes it your most attractive target.
 
The Security Architect should possess **more authority to block than authority to modify**.
 
For example, it can deterministically block a release on a critical finding, but changing the production IAM policy should require a separate controlled operation.
 
### Coding-swarm autonomy
 
I would encode the coding agents' permitted autonomy instead of describing it only in prompts:
 
| Situation | Coding agent | Security Architect | Human |
|---|---|---|---|
| Linter/test failure | Fix autonomously within task scope. | Not involved. | No |
| Low/medium scanner finding with obvious local remediation | Fix and re-run deterministic check. | Observe/review only if repeated. | No |
| High finding | Attempt pre-approved remediation pattern; cannot suppress finding. | Decide remediation adequacy. | Usually no |
| Critical finding | Stop affected path. | Review and escalate. | Depending on impact |
| Add a new third-party dependency | Run dependency assessment automatically. | Review only if risk thresholds trip. | Usually no |
| Add internet ingress | Stop and re-open architectural review. | Mandatory review. | For material/high-risk environments |
| Change identity/authentication architecture | Stop and re-open Council design. | Mandatory review. | Potentially |
| Expand an agent's tools or credential scope | Cannot self-authorise. | Mandatory review. | Human for material privileges |
| Disable security check | Prohibited. | Can propose exception, not silently bypass. | **Required for material checks** |
| Accept known critical/high residual risk | Prohibited. | Recommend only. | **Required** |
| Alter information classification | Prohibited. | Advise. | Governance/human authority |
 
This is an important distinction between *autonomy to repair* and *autonomy to accept risk*.
 
I would make the former generous and the latter narrow.
 
## Fit to your proposed infrastructure
 
Your current infrastructure is fundamentally compatible with this approach. I would make a few security-oriented design adjustments.
 
| Component | Security Architect recommendation | Rationale |
|---|---|---|
| **LangGraph OSS** | Use the graph itself to enforce gates. “Security reviewed” should be an explicit state transition produced by a validation node, not a sentence another agent can claim. | State machines give you a deterministic place to enforce Council workflow and escalation. |
| **LangGraph persistence** | Treat checkpoint contents as potentially sensitive security data. Define schemas for durable versus ephemeral fields and prohibit raw credentials in checkpoints. | Agent state may contain source snippets, architecture details, user data and outputs that were never intended to become permanent. |
| **Langfuse** | Introduce a telemetry classification/redaction gateway *before* traces are written. Store hashes/references for sensitive artifacts rather than their full contents where possible. | Observability is highly valuable for forensic reconstruction, but generative-AI traces can themselves become a sensitive dataset. |
| **Neon/Postgres** | Keep the one-database simplicity, but separate DB roles and schemas at minimum: control catalogue, agent workflow state, security findings, project metadata. Consider stronger physical separation when classifications/tenants justify it. | Combining checkpoints, metadata and vectors is economical but also creates a concentrated blast radius. This is an architectural trade-off rather than a reason to abandon Postgres. |
| **pgvector** | Use embeddings only for semantic retrieval. Security controls, mappings, approvals, exceptions and applicability should remain relational/graph-like deterministic data. | “Nearest security requirement” is not a safe substitute for an exact control lookup. |
| **Cloudflare R2** | Good logical location for immutable-ish evidence artifacts, scanner outputs and SBOMs; DB records should carry artifact hash, type and storage reference. Do not use it as a secret store. | Separating bulky evidence from transactional metadata keeps security provenance manageable. |
| **Modal Sandboxes** | Make these the default execution boundary for generated or untrusted code wherever practical. Give each run the minimum filesystem/network/secrets it needs and destroy it afterwards. | Your persistent Oracle/Railway environment should not become the place where arbitrary generated code gets its first execution. |
| **Railway application** | Keep its Council runtime identity narrowly scoped; avoid credentials that implicitly confer privileges over produced solutions. | Compromise of an orchestrator should not imply compromise of everything it can build. |
| **Oracle VM** | Treat the reranking/compute VM as persistent infrastructure, **not a generic coding-agent runner**. Restrict what can reach it and what it can reach. | Persistent hosts are poor places to execute potentially hostile generated/repository code. |
| **Tailscale** | Retain it as a useful private encrypted connectivity layer, but do not make “on the tailnet” equivalent to authorised. Authenticate and authorise service calls separately. | Zero-trust architecture does not treat network location itself as sufficient trust; NIST SP 800-207 provides the relevant architectural model. citeturn9search33 |
| **GitHub** | Make repository configuration part of the security baseline: protected review paths, CODEOWNERS for sensitive files, minimum Actions permissions, approved Actions, full-SHA pinning and OIDC/short-lived credentials where supported. | GitHub specifically recommends least-privilege `GITHUB_TOKEN`, CODEOWNERS around workflow changes, full-SHA Action pinning and OIDC rather than persistent cloud credentials where available. citeturn21view2 |
| **GitHub Actions / runners** | Do not allow an untrusted PR to execute privileged workflows or run on a persistent machine attached to Council infrastructure. | GitHub warns that privileged triggers combined with untrusted checkout can expose write access/secrets, and that persistent self-hosted runners can be compromised by untrusted code. citeturn21view2 |
| **Council knowledge ingestion** | Run source updates through a distinct ingestion identity and quarantine/parser process. New knowledge must not become an instruction channel into the Council. | This mitigates supply-chain and indirect-prompt-injection risks arising from externally sourced documents. |
| **Security evidence** | Store the scanner version, rule-pack version, timestamp, git SHA, configuration hash and raw-result hash with every gate result. | This allows you to explain later *what was actually tested*, rather than merely recording “scan passed”. |
| **Secrets** | Build a credential-broker abstraction early. Agents request a named capability; the runtime injects an appropriately scoped credential into the specific tool invocation. Do not make secret retrieval a general-purpose agent tool. | Least privilege is particularly important in agentic harnesses because tool/action privileges are a major risk driver. citeturn4search7 |
 
### GitHub deserves special treatment
 
Because the coding swarm can modify the repository, the repository is effectively part of your Council's **control plane**, not merely storage.
 
GitHub warns that a compromised third-party Action may access repository secrets and use the `GITHUB_TOKEN`, recommends minimum token permissions, and says third-party Actions should be pinned to full commit SHAs for immutable references. It also supports using CODEOWNERS to require review of workflow changes and OIDC to replace long-lived cloud credentials where the target provider supports it. citeturn21view2
 
I would therefore consider these paths “security-sensitive” regardless of the application:
 
```text
.github/workflows/**
CODEOWNERS
security/**
infra/**
terraform/**
Dockerfile*
docker-compose*
dependency lockfiles
agent / MCP / tool configuration
authentication / authorisation modules
database migration files affecting security data
```
 
A coding agent can propose changes to those files, but the graph should route the resulting diff through a Security Architect check before merge.
 
OpenSSF Scorecard is particularly attractive here because its automated checks already address several relevant repository-security behaviours, including pinned dependencies, token permissions, branch protection, review, SAST and vulnerabilities. The project's documentation appropriately warns that its checks are heuristics and that its aggregate score is not a definitive assessment. citeturn17view0
 
### SBOM and provenance should be automatic
 
ASD's joint guidance on software bills of materials emphasises that an SBOM enables organisations to map dependencies to known vulnerabilities and continue monitoring them as new vulnerabilities emerge. citeturn12search1
 
For your system, I would make the following release chain routine rather than something the agent needs to remember:
 
```text
merge
  ↓
build
  ↓
security scanners
  ↓
generate CycloneDX SBOM
  ↓
vulnerability/policy evaluation
  ↓
record build + source provenance
  ↓
sign artifact / attestation
  ↓
Council release gate
```
 
CycloneDX's current model is broad enough to represent software components, services and dependencies and has evolved to cover additional forms of BOM, while SLSA specifies progressively stronger supply-chain provenance and verification properties. citeturn16search14turn18view2
 
For the type of AI-generated software factory you envisage, this has another advantage: **you can know exactly what the agents actually assembled**, even when no human manually selected every transitive dependency.
 
## Operating model for the Security Architect
 
### Start every project with a security profile
 
The most valuable deterministic artefact may be a short `project-security-profile.yaml`.
 
Instead of asking the agent, “What security controls should this project use?”, establish facts:
 
```yaml
project:
  deployment_stage: prototype
  intended_production_fidelity: high
 
jurisdiction:
  australian_government: true
  entity_type: unknown
 
information:
  classification: OFFICIAL
  personal_information: false
  sensitive_information: false
 
exposure:
  internet_facing: true
  public_api: false
  administrative_interface: true
 
identity:
  human_users: true
  machine_identities: true
  privileged_users: true
 
technology:
  web_application: true
  mobile_application: false
  containers: true
  infrastructure_as_code: true
 
ai:
  generative_ai: true
  rag: true
  autonomous_agents: false
  external_model_provider: true
 
data:
  external_processors: true
  australian_residency_required: unknown
 
criticality:
  business_impact: medium
  availability_requirement: medium
```
 
`unknown` should be a legitimate and important value. The agent then knows what must be clarified or treated conservatively rather than hallucinating an answer.
 
The profile drives:
 
```text
security profile
      ↓
applicability rules
      ↓
required control set
      ↓
architecture requirements
      ↓
threat model
      ↓
verification plan
      ↓
CI security gates
      ↓
release evidence
```
 
### Security artefacts should live with the software
 
I would have every substantial Council-built project contain something like:
 
```text
security/
├── profile.yaml
├── architecture.yaml
├── threat-model.yaml
├── controls.yaml
├── verification-plan.yaml
├── exceptions/
├── policies/
│   └── rego/
├── evidence-manifest.json
└── decisions/
    ├── SDR-001.yaml
    └── SDR-002.yaml
```
 
The large scanner artifacts and SBOMs can live in R2; these files contain the human-readable and machine-actionable state.
 
A **Security Decision Record** could parallel an Architecture Decision Record:
 
```yaml
id: SDR-014
title: Permit external identity provider
status: accepted
date: 2026-10-01
 
context:
  ...
 
applicable_requirements:
  - ...
 
threats:
  - ...
 
decision:
  ...
 
controls:
  - ...
 
verification:
  - ...
 
residual_risk:
  rating: low
 
approved_by:
  council:
    security_architect: decision-id-...
    solution_architect: decision-id-...
 
human_approval:
  required: false
 
sources:
  - authority: ASD
    source_id: ...
    version: ...
```
 
That would make your desired transparency/explainability substantially more robust than relying on Langfuse conversation traces alone.
 
### Division of responsibility inside the Council
 
I would make the boundaries between the Security Architect and Governance Guru explicit.
 
| Question | Primary owner | Contributor |
|---|---|---|
| “Does PSPF/another policy apply to this entity/project?” | **Governance Guru** | Security Architect |
| “What technical controls satisfy the identified cyber requirement?” | **Security Architect** | Solution Architect |
| “What information classification applies?” | Governance Guru / human | Security Architect |
| “How should the architecture enforce least privilege?” | **Security Architect** | Solution Architect |
| “Is this residual technical risk acceptable?” | Human risk owner for material risk | Security Architect recommends |
| “Does this design meet usability/accessibility requirements?” | UX Designer | Security Architect identifies security implications |
| “How should sensitive data be structured/transformed?” | Data Engineer | Security Architect specifies protections |
| “Can this vulnerability finding be technically mitigated?” | **Security Architect** | Coding swarm |
| “Can we legally/privacy-wise process this data this way?” | Governance Guru / appropriate human expert | Security Architect contributes security risk |
| “Which architecture wins when controls conflict with cost/performance?” | Solution Architect as Chair | Council collectively |
 
That boundary matters because “security” should not become a catch-all for privacy law, records management, ethics, data governance or legal interpretation.
 
### Decision authority
 
I suggest three operational decision classes:
 
| Class | Security Architect authority | Examples |
|---|---|---|
| **Routine / reversible** | Autonomous | Select known secure implementation pattern; require TLS; reject hard-coded credential; patch ordinary dependency vulnerability; add security headers; enforce scanner rule. |
| **Architectural / consequential** | Council decision, Solution Architect chairs disagreement | Identity architecture, new public endpoint, new data processor, persistent agent memory, new network trust boundary, substantial cryptographic design, changing cloud-hosting pattern. |
| **Risk acceptance / high impact** | Recommendation only; human approval | Waive material ISM/PSPF control, knowingly ship critical vulnerability, process materially more sensitive government information, expand production agent privileges, disable mandatory security gate, accept major supply-chain risk. |
 
This preserves the benefit of an expert agent that genuinely makes technical decisions while stopping it from becoming its own risk owner.
 
## Recommended implementation sequence
 
I would resist building a “perfect cyber expert” in one pass. A surprisingly capable Security Architect can be produced from a small number of high-leverage components.
 
| Stage | Build | Why |
|---|---|---|
| **Foundation** | Project Security Profile schema; source-authority hierarchy; security requirement schema; Security Decision Record schema; exception schema. | These structures determine how everything else reasons. |
| **Australian core** | PSPF 2026, ISM, Essential Eight, ASD Secure by Design, ASD secure-AI and agentic-AI guidance. | These are the highest-value sources for your anticipated operating context. citeturn1search30turn8search4turn8search2turn1search3turn4search7 |
| **Application core** | OWASP ASVS, Cheat Sheets, WSTG, Top 10; OpenCRE mappings. | Gives requirements, implementation guidance, test procedures and cross-framework navigation rather than one flat document corpus. citeturn11search0turn11search34turn11search2 |
| **Threat core** | CWE + CAPEC structured ingestion; OWASP Agentic/GenAI risks; MITRE ATLAS as AI-specific enrichment. | Much more reliable than asking the model to invent a complete threat catalogue. citeturn21view1turn20search16turn5search1turn4search35 |
| **Deterministic CI baseline** | Gitleaks + Semgrep + OSV-Scanner + Trivy. | Four inexpensive tools cover secrets, source patterns, dependencies and broad artifact/configuration scanning. citeturn12search2turn12search16turn13search11turn14search0 |
| **Policy engine** | OPA + Conftest plus a small initial Rego library. | Turns Council principles into enforceable software rather than prompt instructions. citeturn18view0turn18view1 |
| **Supply-chain evidence** | CycloneDX SBOM; Syft or Trivy generator; OpenSSF Scorecard; GitHub Actions hardening. | AI-generated code makes dependency and build provenance unusually valuable. citeturn16search14turn13search6turn17view0turn21view2 |
| **Agent harness security** | Tool capability broker, scoped identities, sandbox policy, durable approval objects, prompt/data provenance, budgets and escalation rules. | ASD's current guidance makes the harness and the privileges it mediates central to agentic-AI security. citeturn4search7 |
| **Threat modelling as code** | Trial Threagile against several representative Council projects; retain only if it produces sufficiently useful structured output. | Its architecture-as-YAML and rule-oriented design are well aligned with your deterministic philosophy, but it is worth validating its practical fit before making it foundational. citeturn19search3 |
| **Continuous component assurance** | Add Dependency-Track once the number of maintained Council-produced applications makes CI-only SBOMs cumbersome. | Dependency-Track is designed to consume CycloneDX inventories and continuously identify component vulnerabilities/policy issues. citeturn13search4turn13search26 |
| **Higher assurance** | SLSA provenance/signing with Sigstore; expanded NIST/OSCAL mapping; IRAP-oriented evidence packs. | Valuable once the objective progresses from “production-fidelity prototype” toward “ready for formal assessment/deployment”. citeturn18view2turn14search15turn3search27turn8search0 |
 
My **minimum viable Security Architect** would therefore be considerably smaller than the complete catalogue above:
 
| Essential component | My recommendation |
|---|---|
| Australian KB | **PSPF + ISM + Essential Eight + ASD Secure by Design + ASD AI/agentic guidance** |
| Application KB | **OWASP ASVS + Cheat Sheets + WSTG + Top 10** |
| Threat KB | **CWE + CAPEC + OWASP Agentic/GenAI** |
| Crosswalk | **OpenCRE + your own mappings** |
| Policy engine | **OPA + Conftest** |
| SAST | **Semgrep CE** |
| Secrets | **Gitleaks** |
| Dependencies | **OSV-Scanner** |
| Artifact/IaC/container | **Trivy** |
| Supply-chain assessment | **OpenSSF Scorecard** |
| BOM | **CycloneDX**, generated by Syft or Trivy |
| Execution boundary | **Modal Sandboxes** for generated/untrusted execution |
| Audit artefacts | Postgres metadata + R2 evidence |
| Workflow enforcement | **LangGraph state transitions, not prompt-only instructions** |
| Git control plane | Hardened GitHub Actions, CODEOWNERS, least-privilege tokens, SHA-pinned actions and short-lived identity where supported. citeturn21view2 |
 
The single biggest architectural choice I would make is **not** adding another security product. It would be building the **Security Profile → Applicable Controls → Threats → Tests → Evidence → Exception** chain as structured data.
 
That converts the Security Architect from:
 
> “an LLM that has read the ISM and OWASP”
 
into:
 
> **“an explainable security-engineering system that can determine which requirements apply, retrieve their authoritative basis, translate them into engineering constraints, execute deterministic assurance, reason over the unresolved parts, and prove what it checked.”**
 
That design is particularly well suited to the blurred prototype-to-production boundary you described. A vibe-coded application can emerge in hours; the security architecture does not then need to be reconstructed retrospectively from a chat transcript. The control selection, threat model, evidence and exceptions can exist from the first working prototype and simply become progressively more rigorous as the solution moves toward pilot and eventual human production assessment. ASD's Secure by Design guidance similarly frames security as something incorporated from design through development and deployment rather than bolted on afterwards. citeturn8search2turn8search20
