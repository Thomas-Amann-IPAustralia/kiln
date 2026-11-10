# Build method

> **Changed from the seed.** `CONTEXT.md` reads `GLOSSARY.md` throughout: the skills renamed
> the file and now read only the new name. Every skill this page names exists in
> `mattpocock/skills` at commit `4ae2317` (v1.3.2, 31 October 2026). `ralph-once` is not a
> skill there; it is the single-iteration script from Pocock's Ralph articles (D-004).

Build each agent the way Matt Pocock ships a feature, and build the Council so it runs that same process for every solution. The Council automates his planning and QA phases, and the coding swarm is his execution phase.

## Seven phases, two uses

The phases come from Pocock's [seven phases of AI development](https://www.aihero.dev/my-7-phases-of-ai-development). Skill names are from the current [mattpocock/skills](https://github.com/mattpocock/skills) repo, which has renamed the article's `/write-a-prd` and `/prd-to-issues` to `/to-spec` and `/to-tickets`.

| Phase | Building a Council agent (Tom, in Claude Code) | Running a solution (the Council) |
| --- | --- | --- |
| 1. Idea | `/grill-with-docs` on the agent's charter until every branch is resolved. It writes GLOSSARY.md terms and ADRs as it goes. | G0 intake: the chair (later the Interpreter) questions Tom until the question, DVF hypotheses and budget are clear. |
| 2. Research | `/research` caches cited findings for the build sprint, such as how ISM control IDs are structured. Delete them when the sprint ends. | G1: the Researcher answers open questions with packets scoped to the solution, never stored as lasting facts. |
| 3. Prototype | `/prototype` the risky piece first, such as three throwaway versions of the applicability rules tested on real briefs. | Spikes before committing: architecture spikes in Modal, UX variations, Data Engineer benchmarks. |
| 4. Spec | `/to-spec` turns the grilled charter into the agent's spec: typed inputs, outputs and end state, not steps. | G2: architecture, domain contracts and a draft real-world test plan, approved by Tom. |
| 5. Tickets | `/to-tickets` cuts tracer-bullet slices with blocking edges. Use `/wayfinder` for the Council as a whole, which is bigger than any one session. | G2: the chair compiles tickets with acceptance criteria and dependencies. |
| 6. Execution | HITL Ralph for risky slices, AFK Ralph for the rest, with `/implement`, `/tdd` and `/code-review` inside the loop. | G3: coding loops build against the contract, with Council checks as backpressure. |
| 7. QA | A QA plan for Tom's own review plus the agent's golden eval set in Langfuse. Failures become new tickets. | G4 and G5: a test-ready build with an assurance case and test plan, then DVF evidence from Tom's team. |

## Practices to adopt from day one

- **One shared language.** Run `/grill-with-docs` over this charter first. Its GLOSSARY.md becomes the Council glossary, and every prompt, schema and table name uses those terms. Pocock's case is that a shared vocabulary cuts tokens and makes a codebase easier for agents to navigate.
- **Appendix A becomes ADRs.** Each decision in Appendix A seeds an ADR in the Council repo, so later sessions see why, not just what. (Done: [`docs/adr/`](../adr/README.md), ADR-0001 to ADR-0026.)
- **Vertical slices, not layers.** An agent's first ticket runs end to end: schema, one rule, one tool, one LangGraph node, one eval case. Do not ingest every corpus before anything runs.
- **Feedback loops set the speed limit.** Python has no compiler pushing back, so wire in a type checker (pyright, mypy or pyrefly), pytest, ruff and pre-commit hooks that block commits on failure. [Huntley](https://ghuntley.com/ralph/) calls this backpressure and counts security scanners and static analysers as part of it.
- **Risky work first, and by hand.** Schemas, gates, the decision store and anything security-sensitive go through HITL Ralph (`ralph-once`). Corpus adapters, provider profiles, rule backlogs and test coverage suit AFK Ralph, capped at 5 to 10 iterations for small work and 30 to 50 for large ([tips](https://www.aihero.dev/tips-for-ai-coding-with-ralph-wiggum)).
- **One item per loop.** Each iteration reads the same plan and specs, picks one ticket, searches before assuming anything is missing, runs the checks, commits and appends to a progress file ([getting started](https://www.aihero.dev/getting-started-with-ralph)). Delete the progress file when the sprint ends.
- **State the quality bar.** The Council's AGENTS.md, and every solution repo's, says production quality in proportion to the system: deterministic-first, no placeholder implementations, and every test notes why it exists. Agents copy what they find in the repo, so the first agent's code sets the pattern for the other six.
- **Sandbox every AFK loop.** Docker sandbox or Modal, never the Oracle VM.
- **Deep modules.** Each agent is a small interface (typed request in, typed packet out) over deep internals. Run `/improve-codebase-architecture` every few days to catch drift.
- **Ask the right human.** When a build decision needs an expert Tom is not, `/to-questionnaire` turns it into a short questionnaire for that person.

## How Council skills are packaged

A Council skill is a folder: a SKILL.md stating when to use it, the procedure and the escalation conditions, a typed Python function with Pydantic input and output, and its tests and eval cases. Agents see only skill descriptions until they pick one, which keeps prompts small. Tom can write and test each skill in Claude Code before wiring it into LangGraph, using `/writing-for-agents` for the SKILL.md.

This follows Pocock's split between skills that orchestrate and skills that hold reusable discipline. In the Council, orchestration lives in LangGraph graphs and discipline lives in skills. Graphs call skills; skills never call graphs.

## Where Ralph and the Council part ways

Huntley argues that agents talking to agents is not needed and keeps Ralph as one process working in one repository. The Council keeps that discipline where it counts. Execution starts as one loop per repository and only fans out for tickets with no blocking edges, and loops reach Council members only through typed questions, never open chat.

The multi-agent part is confined to planning and assurance, where separate knowledge and separate authority are the point, and it runs on typed artefacts rather than conversation.

Huntley also says he would not use Ralph on an existing codebase, and that senior judgement is still needed. Council solutions start greenfield, which suits Ralph. Changes to an existing Council-built repo get smaller tickets and HITL loops, and expert assessment before production supplies the senior judgement.
