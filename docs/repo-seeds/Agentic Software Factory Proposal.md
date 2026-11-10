## Agentic Software Factory Proposal

In the age of generative AI, the distinction between a mockup, low-fi experiment, proof-of-concept, minimum viable product and pilot have become much blurrier. The time it used to take to sketch a solution on some butcher's paper is now similar to the length of time for ‘vibe coding’ a working prototype.

I am creating a multi-agent system whose solutions could feasibly be deployed directly into production.The types of solutions the system will be asked to construct are likely to be very broad, though, often focussing within an Australian Government context.

To achieve this fidelity, several ‘experts’ must be developed and deployed within the agentic system so that they may advise and confer on matters relating to the solution’s design. After a consensus is reached among the experts, and the proposed solution has been agreed to by the human user, they will continue to advise on matters relating to their domains, helping to resolve issues which may arise during the development phase of work. The collective term for the domain expert agents will be ‘The Council’. Where expert interests overlap or there is disagreement between the correct course of action, The Council will escalate the matter to the council chair. In most circumstances, the role of Council chair will be performed by the ‘Solution Architect’ agent.

Development will likely be undertaken by a swarm of coding agents, who operate according to the plans previously set out by The Council. If a coding agent within the swarm encounters an error or issue that was not anticipated by the plan, the coding agent will be permitted to operate within a fixed level of autonomy, escalating to the relevant Council member when appropriate.

To control costs and feasibility of the solution, I am hoping to develop a limited number of expert Agents, specialising in the domains which are expected to come under greatest scrutiny or whose expertise is likely going to be frequently called upon. I am the end-user of this agentic development pipeline and, while I have been growing in my technical competence, I am still a mere human and am unable to attain and implement knowledge at a rate that could compete with this process. This means that the experts will often be making genuinely meaningful decisions without expert oversight. This is acceptable from a risk perspective, as the produced solutions will not be genuinely deployed into a ‘production’ context until they have been assessed by human experts. It is essential that the agent's produce work which would likely stand up to the scrutiny of a human expert, instead of deferring difficult tasks because an expert will eventually be consulted. The human expert review should be treated as a safety net, not an excuse for poor performance.

At the moment, the experts I have identified as being worth building are:
- Security Architect
- Data-Analyst
- Data-Engineer
- Researcher
- Solution Architect
- Governance Guru
- UX Designer

These experts will be equipped with their own, domain specific knowledge bases against which they may search for information. They will also be provisioned with a variety of tools, plugins and skills which will empower them to be as useful within their domains as feasible.

Where feasible, experts will leverage deterministic processes, calling on their inference ability only when it offers value/benefit. This is to reduce costs of running the system, reducing the likelihood for hallucinations and to provide greater transparency and explainability for particular outcomes.

The actual process loop has not yet been fully designed. However, given that I (the creator and user of this system) am not a subject matter expert, particular attention will *eventually* be paid to the points of interaction between myself and the council. For example a clean and simple graphical user interface, progressive information disclosure, etc.
To this end, I hope to eventually deploy 1 agent and 1 sub-agent, purpose built to address this point of potential friction.
- Agent - Interpreter
    - Basic role description: Communicates the needs of the council to the human and intercedes on behalf of the human with the council. The interpreter’s primary function is to ensure that complex information being used by the council is easy to understand and communicated clearly to the human and, when the human isn’t clear enough in their response/instruction, that the interpreter will ask probing questions until it has enough information to provide clear information to the council.
    - Initial thoughts on tools/skills: 1. Real time voice to text and text to voice streaming (in case verbal communication is opted for). 2. Grill with docs skill (from Matt Pocock). 3. Can invoke the 'Illustrator' sub-agent.
- Sub-Agent - Illustrator
- Basic role description: Reports directly to the interpreter, creates visual aids to help the interpreter communicate to the human. The human is not omniscient but will be required to make decisions about matters which may fall outside their existing knowledge. The human is a visual learner. When called upon, the illustrator must elucidate/clarify the technical information, allowing the human to make a more informed decision.

NOTE ABOUT THE HUMAN-MACHINE INTERFACE: This is a solution is not an immediate priority. I have mentioned it in case it influences any decisions regarding the construction of The Council.

The infrastructure cost for the agentic development system (The Council and their Coding swarm) should be free/very low (with the exception of LLM token usage).Infrastructure of the solutions they build may require different/more expensive infrastructure to run. This is acceptable (so long as the costs remain reasonably low). 

My working draft of the infrastructure that will run The Council is:
Requirement 1: Agent orchestration,
    Solution 1: LangGraph OSS,

Requirement 2: Monitoring,
    Solution 2:Langfuse,

Requirement 3: Knowledge ingestion,
    Solution 3: Direct ingestion using custom scripts,
        NOTE: LlamaIndex if ingestion becomes infeasible,

Requirement 4: Agent persistence,
    Solution 4: Neon Postgres,

Requirement 5: Database,
    Solution 5: Neon,
        NOTE: Postgres works for LangGraph checkpoints, metadata and vectors (with pgvector) in one system,

Requirement 6: Object storage,
    Solution 6: Cloudflare R2,

Requirement 7: Vector storage,
    Solution 7: pgvector with Neon,
        NOTE: Will consider Pincone Starter if Postgres and pgvector get bottlenecked,

Requirement 8: Ephemeral VMs,
    Solution 8: Modal Sandboxes,

Requirement 9: Application hosting,
    Solution 9: Railway & Oracle VM,
        NOTE: Using an Oracle for operations requiring more significant compute/memory (like local reranking models, etc.). Oracle VM and Railway app on the same Tailscale network, so the app calls the embedding endpoint over a private encrypted link, dramatically reducing the attack surface and maintenance burden,

Requirement 10: Git/Code repository,
    Solution 10: Github
