# Coding swarm

The coding swarm is a coding-agent CLI (Claude Code in headless mode today) running Ralph loops inside Modal sandboxes. It implements tickets against the build contract, with broad autonomy, and pauses a path only for a Red item, which goes to the owning expert, or a tripwire, which goes to Tom. It is not a Council member, and reaches one only through typed questions, never open chat.

## How a loop runs

Every iteration loads the same stack: AGENTS.md, GLOSSARY.md, the ticket file and the contracts that apply to its ticket. Then it:

1. Picks the highest-priority open ticket that nothing blocks, favouring risky and integration work.
2. Searches the code before assuming anything is missing, and checks the ticket against the contracts. If the ticket is ambiguous or clashes with a decision, it raises a typed question to the owning expert and works on another ticket meanwhile. The answer updates the contract, so the next loop does not ask again.
3. Implements that one ticket only.
4. Runs every check. A failing check blocks the commit.
5. Commits, sets the ticket's `passes` flag and appends a short progress note.
6. Stops with a completion signal when every ticket passes, or when the iteration cap or token budget runs out.

Tickets use the JSON shape [Pocock borrows](https://www.aihero.dev/tips-for-ai-coding-with-ralph-wiggum) from Anthropic's work on long-running agents: a description, verification steps and a `passes` flag. The chair writes the tickets. A loop may only flip its own ticket's flag, and only after the checks pass.

## Backpressure

Engineering checks and tripwires block a commit. Quality checks run on every commit too. The loop fixes what it can or dismisses a false positive with a recorded reason, and critical or high findings are settled before G4.

| Check | Effect | Examples |
| --- | --- | --- |
| Engineering feedback | Blocks the commit | Type checker, pytest, ruff, pre-commit hooks, data contracts, OpenAPI contract tests, critical Playwright journeys, fitness functions |
| Tripwire checks | Blocks the commit and asks Tom | Gitleaks, real-data screening, egress to live systems, spend over budget |
| Quality checks | Fix or explain; critical and high findings settled before G4 | Semgrep, OSV-Scanner, Trivy, SBOM, axe, ARIA snapshots, Vale, v.Nu, governance constraints |

## What the swarm reads

Every solution repo keeps its Council state in one place. Large artefacts live in R2 and are referenced by hash.

```
council/
  profile.yaml          question, users, DVF hypotheses, proportionality, budget
  decisions/            DEC-0001-<slug>.md, rendered from the decision store
  contracts/
    architecture/       workspace.dsl (C4), deployment.dsl
    interfaces/         OpenAPI and AsyncAPI files
    data/               schemas and data contracts
    ux/                 ux-contract.yaml, design tokens
    security/           controls.yaml, threat-model.yaml
    governance/         constraints.json
  fitness/              rules and tests that enforce decisions
  tickets.json          tickets with passes flags
  evidence/manifest.json
  readiness/            assurance case, real-world test plan, open risks, dissent
  findings/             real-world test results and DVF findings
AGENTS.md               build and test commands, the quality bar
GLOSSARY.md              the shared vocabulary

```

A loop queries the constraints that apply to its ticket rather than loading every contract.

## Limits

- Start with one sequential loop per repository. Fan out to parallel loops only for tickets with no blocking edges, once a single loop is reliable.
- Run HITL only while a loop prompt is new. After that, AFK is the default, always with an iteration cap and a spend cap.
- Each sandbox gets a repo-scoped, short-lived GitHub token and a spend-capped model key. Network access is open for packages and documentation, and closed to live systems.
- A tripwire stops the affected path and asks Tom. The loop carries on with other tickets.
