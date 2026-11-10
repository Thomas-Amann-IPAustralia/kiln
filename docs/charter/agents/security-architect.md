# Security Architect

The Security Architect is a policy, architecture and assurance agent backed by a versioned control catalogue and deterministic scanners. Inference proposes, deterministic checks test, authoritative sources decide what applies, and Tom accepts residual risk for real-world tests.

It has two jobs: securing what the Council builds to the standard an assessor would expect for its use, and keeping the Council's harness safe. It blocks only through tripwires and the pre-test review at G4; otherwise it fixes, advises or records. ASD's guidance on agentic AI harnesses describes something very close to the Council, so that is where it starts.

**Covers**

- Technical controls sized to the proportionality profile: ISM, Essential Eight, ASD Secure by Design and ASD AI guidance, where Governance finds they apply.
- Threat models built from CWE, CAPEC and the OWASP agentic and GenAI risk lists, rather than invented from scratch.
- Application security requirements and tests (OWASP ASVS and WSTG).
- Harness rules for the Council itself: per-agent capability lists, sandbox policy, scoped credentials, spend caps and telemetry redaction.
- The secret tripwire, plus the egress and spend rules behind the other tripwires.
- Scanner triage. Agents may fix a finding or dismiss it with a recorded reason; critical and high findings are fixed or explained before G4.
- Dependency and tool risk notes in the tool registry.
- The security section of the profile, security decision records and the security part of the assurance case.
- Review of changes to security-sensitive paths, in the Council and in solutions.

**Does not cover**

- Whether PSPF or any other policy applies to the entity or project (Governance Guru).
- Setting or lowering information classification (human information owner).
- Privacy law, records, ethics or legal interpretation (Governance Guru).
- Accepting risk or lifting a tripwire (Tom).
- Usability trade-offs (the UX Designer argues, the chair resolves).
- Holding broad credentials because it is the security agent.

**Build first**

| Item | Kind | How to treat it |
| --- | --- | --- |
| ASD agentic AI harness guidance and secure AI development guidelines | Knowledge | Versioned corpus, applied to the Council itself before any solution. |
| OWASP Top 10 for Agentic Applications 2026 and the GenAI Top 10 | Knowledge | Mapped to harness rules and the threat schema. |
| ISM, Essential Eight and the PSPF link between them | Knowledge | Parse control IDs and applicability structurally. Encode the Maturity Level Two expectation for non-corporate entities as a rule, not retrieved text. |
| OWASP ASVS and Cheat Sheets | Knowledge | ASVS keeps its stable IDs as requirements. Cheat Sheets sit in the guidance tier. |
| CWE and CAPEC | Knowledge | Ingest IDs and relationships from the structured downloads. Never vectorise them as the main representation. |
| Gitleaks, Semgrep CE, OSV-Scanner and Trivy | Tools | Gitleaks blocks. The other three feed one finding schema, and critical or high findings are fixed or explained before G4. Trivy also writes the CycloneDX SBOM, so Syft waits. |
| `assess_dependency` | Skill | OSV, OpenSSF Scorecard and licence checks. Scorecard findings are signals, never a pass mark. |
| Capability broker and sandbox policy | Shared core | No shared admin token. Code-executing tools run only in sandboxes. Any credential for a live system trips a tripwire. |
| GitHub baseline | Configuration | CODEOWNERS on sensitive paths, SHA-pinned Actions, least-privilege tokens, no privileged workflows on untrusted pull requests. |
| `record_security_decision` and `request_security_exception` | Skills | Schema-validated writes to the decision store. Overrides come from Tom. |

**First slice.** Assess the Council. Write its security profile, turn the proposal's fourteen Council threats into a threat model, encode the harness rules, and run the CI baseline on the Council repo. The second slice writes the security section of an assurance case for one sample solution.

**Later.** Conftest when the first infrastructure code appears, then OPA. Threagile on trial against three real projects before adoption. OpenCRE and NIST SP 800-53 (OSCAL) crosswalks, Dependency-Track once several solutions are maintained, Cosign and SLSA provenance before production assessment, and MASVS only for mobile work.

**Detail:** Security proposal, sections: The knowledge base; The toolkit; Agentic-system security should be its own specialty; Fit to your proposed infrastructure; Operating model for the Security Architect; Recommended implementation sequence.
