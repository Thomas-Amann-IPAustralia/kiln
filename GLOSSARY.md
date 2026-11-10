# Kiln

Kiln is a software factory: a Council of expert agents that plans and assures a solution, a
coding swarm that builds it, and the shared core they all run on. This glossary is the one
vocabulary for its prompts, schemas, table names and documents.

Seeded from the charter's "Terms used throughout" (D-002). `/grill-with-docs` sharpens it.
A definition says what a thing is, never how it is built.

## Language

### People

**Tom**:
The owner. The person accountable for Kiln, who can override any rule or decision in it.
_Avoid_: the user, the human

**Tom's team**:
The people who run a real-world test on a test-ready build. Real users and real data stay with them.

**Human expert**:
A person outside Kiln who assesses a solution before production, through the agency's own approval path.
_Avoid_: reviewer

**Information owner**:
The human who sets the classification of information. Agents may only propose one.

### The factory

**Kiln**:
The whole factory: the Council, the coding swarm and the shared core, and this repository.
_Avoid_: the Council repo, the system

**The Council**:
The seven domain experts: Solution Architect, Researcher, Security Architect, Governance Guru, Data Engineer, UX Designer and Data Analyst.
_Avoid_: the agents, the experts' committee

**Expert**:
A member of the Council. Each owns one domain and writes its own position.
_Avoid_: Council agent (when a member is meant)

**Chair**:
The Solution Architect, when it routes work to experts and settles a clash between them.

**Coding swarm**:
The agents that implement the Council's plans. They are not Council members.
_Avoid_: the coders, the dev agents

**Interface agents**:
The Interpreter, Tom's single point of contact with the Council, and the Illustrator, which draws decision aids for it. Both are deferred.

**Shared core**:
The machinery every agent uses, built once: profiles, registries, the decision store, gates and sandboxes.
_Avoid_: the platform, the framework

**Solution**:
What the Council builds in answer to one question from Tom.
_Avoid_: project (for the thing built), product, app

**Brief**:
What Tom brings to intake: the problem, in his words, before it becomes a project profile.

### Sizing and stopping

**DVF**:
Desirability (do people want it?), viability (is it worth doing, and allowed?) and feasibility (can it be built and run?).

**Hypothesis**:
A claim about a solution's desirability, viability or feasibility that a real-world test can support or refute.

**Proportionality profile**:
Three intake facts that size every expert's work: who will use the solution, what data it touches, and whether it informs, acts or decides about people.
_Avoid_: risk level, maturity level

**Project profile**:
The one structured record of a solution's question, users, hypotheses, proportionality profile and budget, with a section per expert.
_Avoid_: project brief, intake form

**Tripwire**:
One of four conditions that stop the affected work until Tom decides: real sensitive data in a build, an exposed secret, a real-world action before approval, or spend over budget.
_Avoid_: hard constraint, blocker, hard gate

**Obligation**:
Something a law, policy or standard requires of this kind of solution. It is designed in by default.
_Avoid_: requirement (when a legal or policy duty is meant), control

**Deferral**:
A recorded decision not to meet an obligation yet, because meeting it would be out of proportion. Never because it is hard.

**Preference**:
A trade-off between goods, such as speed against transferability, which the owning expert decides.

**Autonomy envelope**:
The four bands that say what an agent or loop may do with a decision: Green (decide and record), Amber (proceed and notify), Red (pause for the owning expert) and Tom (stop and ask Tom).

**Override**:
Tom's decision to set aside a rule, a band, a tripwire or another decision. It is always a record.

### The path of a solution

**Gate**:
One of six checkpoints, G0 to G5, that a solution passes in order: intake, applicability, design, build, pre-release and real-world test.
_Avoid_: stage, phase (a phase is a step in building Kiln)

**G2 packet**:
The short plain-language summary Tom reads to approve a plan before any code is written.

**Build contract**:
What the coding swarm builds against: the domain contracts, the fitness functions derived from decisions, and the tickets.
_Avoid_: spec (for a solution), architecture contract

**Domain contract**:
One expert's machine-readable terms for a solution, such as the UX contract or the data contracts.

**Fitness function**:
A rule or test that enforces a decision on every commit.

**Ticket**:
One unit of work for a coding loop, with verification steps and a flag that says whether it passes.
_Avoid_: issue, task (for swarm work)

**Typed question**:
The only way a coding loop reaches an expert: a structured question whose answer updates the contract.

**Test-ready build**:
A build that has passed the Council's pre-release checks, handed over at G4 with its assurance case and test plan.
_Avoid_: release, MVP, prototype

**Real-world test**:
The trial Tom's team runs on a test-ready build. It produces DVF evidence, and its form depends on the solution.
_Avoid_: pilot, UAT

**Assurance case**:
The argument, assembled at G4 from records already kept, that a build is fit to test: claims, controls, evidence, deferrals and dissent.
_Avoid_: compliance certificate, sign-off

**Obligation-Control-Evidence matrix**:
One row per applicable obligation: its owner, its control, its evidence and its status. The authoritative state of assurance.

### Evidence and records

**Source**:
A document, dataset or service that evidence is drawn from, registered once with its authority, dates and hash.

**Evidence**:
An exact item from a source, or a measured result, that a claim rests on.
_Avoid_: context, reference

**Finding**:
What a check or a review observed about a solution. It is not a source, and not a decision.

**Basis**:
The label every claim carries for how it is known: observed, authoritative, rule, supported, inferred, assumed or unknown.

**Research packet**:
The Researcher's typed answer to a research request: claims, each tied to exact evidence, with contradictions, limits and freshness.

**Data Source Manifest**:
The Researcher's handover of an external dataset: endpoint, exact query, schema, coverage, licence, snapshot hash and caveats.

**Decision record**:
A decision the Council makes while building a solution, numbered DEC-NNNN, with its actor, time, basis and any dissent.
_Avoid_: ADR (that is a ruling about Kiln itself)

**Dissent**:
An expert's recorded disagreement with a decision, written by that expert and shown to Tom unedited.

**ADR**:
A standing ruling about what Kiln and the Council are, numbered ADR-NNNN.

**Decision entry**:
An event in building Kiln, numbered D-NNN in the decision log: a choice, a measurement, a spend, an adoption or a deferral.

**Seed**:
A planning document Tom placed in the repo before the first session. Sealed, and never authority over the live charter.

### Building

**Phase**:
One of six steps, 0 to 5, in building Kiln itself, each closed by an exit test.
_Avoid_: gate, stage, sprint

**First build**:
The smallest version of an agent that does useful work end to end.
_Avoid_: MVP, v1

**First slice**:
The first end-to-end task an agent is built to do, which also becomes its first evaluation set.

**Deterministic first**:
If a rule, lookup or test can answer a question, the model does not.

**Council skill**:
A reusable discipline packaged as a folder: when to use it, a typed function, and its tests and evaluation cases.
_Avoid_: tool (a tool is an outside program or service a skill may call)

**Renderer**:
A stateless component that only turns structured state into a document or a picture. It adds no content.

**Ralph loop**:
One coding agent working through tickets in one repository, one ticket per iteration. HITL when a person watches each iteration, AFK when it runs unattended under an iteration cap and a spend cap.

**Backpressure**:
The checks that block a commit until they pass.

**Sandbox**:
A disposable machine where generated or untrusted code runs, with limits on files, network, secrets and spend.

**Capability broker**:
The component that gives a tool call a scoped, short-lived credential, so that no agent holds one.

**Adoption**:
Tom's decision that a measured result or a recommendation enters the design, the defaults or a contract.
