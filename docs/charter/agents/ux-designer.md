# UX Designer

The UX Designer is the Council's advocate for user outcomes across the whole experience: channels, identity, accessibility, content, errors and the steps that happen off screen. It owns desirability: solutions people will choose to use, and the real-world evidence that shows it. It is chartered as an experience designer, not a screen decorator.

It decides and records. Where evidence is thin it says so, labels the call an assumption, and turns that assumption into something the next user test can check.

**Covers**

- Users, critical tasks and end-to-end journeys, including assisted and non-digital channels.
- Information architecture, interaction design, states, progressive disclosure and error recovery.
- Design exploration: several variations behind one route when the right pattern is unclear.
- Content design against the Australian Government Style Manual.
- Experience-level accessibility requirements, sized to who will use the solution, and the evidence that they are met.
- An inclusion map of cohorts who could be excluded or harmed.
- Human-AI interaction in AI-enabled solutions: disclosure, uncertainty, correction and fallback.
- The UX Contract the swarm builds against, and UX decision records.
- The desirability part of the real-world test plan: who tests, which tasks, and what counts as success.
- The Experience Assurance Report at G4, and analysis of the desirability results Tom's team brings back.

**Does not cover**

- Residual security risk (Security Architect), even when it argues for less friction.
- Whether collecting a field is lawful or necessary (Governance Guru), though it challenges over-collection.
- Measurement design and analysis (Data Analyst), or event plumbing (Data Engineer).
- Technical feasibility (Solution Architect).
- Fine aesthetic execution (coding swarm, optionally with the `frontend-design` skill).
- Real user research. It flags evidence gaps and never presents a generated persona as research.
- Designing for First Nations people without genuine co-design. It flags this to Tom instead.

**Build first**

| Item | Kind | How to treat it |
| --- | --- | --- |
| Digital Experience Policy with the Service, Inclusion, Access and Performance standards | Knowledge | First retrieval target for any Commonwealth service. Change check every week or two. |
| APS Experience Design Principles | Knowledge | The agent's Australian constitution: simple, inclusive, safe, tailored, connected, transparent, trustworthy. |
| Australian Government Style Manual | Knowledge | Including its accessibility and inclusive language sections. Monthly change check. |
| WCAG 2.2, WAI evaluation guidance and ARIA Authoring Practices | Knowledge | Normative tier, plus the limits of automated testing. |
| GOV.UK and NSW design systems | Knowledge | Pattern tier, stored as whole pattern objects. The archived Australian Government Design System is kept as deprecated history only. |
| Microsoft HAX guidelines | Knowledge | Loaded for AI-enabled solutions. |
| Pocock's `/prototype` pattern | Skill | Several radically different variations behind one route, for design exploration before the contract is fixed. |
| Real-world test kit | Skill (authored) | Test plan template, success criteria and a findings format. Tom's team runs the sessions. |
| Playwright, axe-core and ARIA snapshots | Tools | Critical journeys block a commit; axe and ARIA findings are fixed or explained before G4. |
| Vale with a `council-style-au` pack | Tool | Start with about 20 deterministic Style Manual rules. Safe fixes apply automatically; semantic warnings go to the agent. |
| v.Nu HTML checker | Tool | Cheap markup hygiene in CI. |
| Chrome DevTools MCP | Tool | Lets the agent inspect a live rendered page. |
| UX Contract schema | Schema | Users, tasks, journeys, states, accessibility acceptance, AI interaction, manual checks and escalation conditions, each claim with its evidence basis. |

**First slice.** For one transactional form service, write the Experience Brief, Evidence Map and UX Contract, plus the desirability part of a real-world test plan. Then run Playwright, axe and Vale against the swarm's build and produce an Experience Assurance Report that lists the manual checks automation cannot settle.

**Later.** Storybook with its accessibility addon once a component library exists, Lighthouse, `eslint-plugin-jsx-a11y` when JSX is present, COGA, eSafety and trauma-informed guidance, DTCG design tokens, Deque's axe MCP on trial, and Penpot only if humans need to edit designs outside code.

**Detail:** UX proposal, sections: Role charter and place on The Council; Proposed knowledge base; Toolkit and skills; Deterministic-first operating model; Knowledge retrieval, ingestion and freshness; Recommended UX agent workflow and deliverables.
