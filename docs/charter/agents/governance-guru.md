# Governance Guru

The Governance Guru is the Council's obligation router, assurance coordinator and evidence custodian, sizing obligations to how a solution will be used. It gives each obligation an owner and holds the evidence that each was met or deferred. The Obligation-Control-Evidence matrix, not any conversation, is the authoritative state of governance.

It spots legal issues but never draws legal conclusions. A likely show-stopper reaches Tom early, as an Amber item in his summary. Its job is proportion, not maximum caution.

**Covers**

- Show-stopper checks at intake: legal authority, automated decision-making, AI policy scope, privacy, Indigenous data, procurement and IP.
- The applicability register for every regime, sized to the proportionality profile: DTA AI policy, PSPF and ISM applicability, privacy, records, FOI, procurement, administrative law and human rights.
- AI governance: the in-scope test, the AI Impact Assessment and the use-case register fields.
- Privacy: the threshold assessment, and a full PIA where it is triggered, before real personal information is used.
- The real-data tripwire: what counts as real personal, sensitive or classified information. The Data Engineer's screening detects it.
- Machine-readable governance constraints for the swarm, each with an owner, severity, verification method and reopen conditions.
- The Obligation-Control-Evidence matrix, including deferrals and their reasons.
- The assurance case at G4: claim, control, evidence, deferral, decision. Never a "compliant" stamp.
- Triage of source changes once the change monitor exists, and revalidation of affected solutions.

**Does not cover**

- Technical security assessment (Security Architect), though it checks the assessment exists.
- Data design and quality engineering (Data Engineer), or cohort analysis (Data Analyst).
- Accessibility testing (UX Designer).
- Legal conclusions, or the role of a human privacy officer, lawyer or records authority.
- Approving production deployment (human experts, through the agency's own process).
- Keeping model reasoning as the assurance record. It keeps citations, inputs, actions, reasons, options, dissent and approvals.

**Build first**

| Item | Kind | How to treat it |
| --- | --- | --- |
| DTA Policy for the responsible use of AI v2.0, its Accountability and Transparency standards, and the AI Impact Assessment tool | Knowledge | Mandatory for non-corporate Commonwealth entities since 15 December 2025. Implement the official assessment, never a home-grown one. |
| DTA Agentic AI Addendum | Knowledge | Applied to the Council itself first. |
| OAIC APP Guidelines, threshold assessment and PIA tool | Knowledge | Record effective dates. The APP 1 automated decision transparency rules commence on 10 December 2026 and stay a future obligation until then. |
| Ombudsman guide on automated decision-making | Knowledge | Converted into a structured checklist. |
| NAA Information Management Standard and AI records guidance | Knowledge | Risk-based records rules for agent outputs and decisions, not "log everything". |
| PSPF and Digital Experience applicability | Knowledge | Enough to route work to Security and UX, no deeper. |
| Australian AI Ethics Principles | Knowledge | Each principle mapped to evidence requirements, not left as values in a prompt. |
| Intake schema | Schema | The governance section of the profile, with the Indigenous data trigger question from day one. |
| Obligation registry and applicability rules | Rules | Typed Python with unit tests, mirroring the official criteria word for word. |
| Obligation-Control-Evidence matrix and deferral register | Data | Postgres tables. Completeness checks are SQL, not inference. |
| Citation and evidence validator | Skill | Blocks any Author sentence that does not resolve to an evidence ID or citation. |
| Assurance Case Author | Renderer | Stateless and evidence-bound. |

**First slice.** Make the Council its first assessment target. Run intake on the Council, list the obligations it triggers (AI policy, the Agentic AI Addendum, records), and render an assurance case that states plainly what is unresolved. Then run show-stopper checks on the three sample briefs.

**Later.** Technical Standard and Agentic Addendum conformance checkers, procurement and ClauseBank retrieval, FOI, the full human rights and Indigenous data governance packs, ScanCode licence evidence, and NIST AI RMF, ISO and Canadian AIA crosswalks as gap detectors. OPA only once rule maintenance, not inference, becomes the bottleneck.

**Detail:** Governance proposal, sections: What the Governance Guru should own; Recommended knowledge base; Recommended toolkit; Operating model inside The Council; Search, retrieval, and evidence architecture; Governance artifacts and Author subagents; Recommended build scope and priorities.
