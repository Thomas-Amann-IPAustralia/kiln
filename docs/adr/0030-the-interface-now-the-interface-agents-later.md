---
status: accepted
source: D-008
---

# The interface to Tom is built now; the Interpreter and Illustrator agents later

The agents stay in phase 5. Their job starts now, in three cheap pieces:

1. **A decision card** for every decision put to Tom: the question, the options and their
   consequences, a recommendation, any dissent, whether it can be undone, what happens if Tom
   does not answer, and exactly what he is approving. Slice 1 makes it a typed record, and an
   approval binds to its id and hash (ADR-0028).
2. **Diagrams as Mermaid text** where a picture helps a real decision. They render on GitHub,
   survive export and stay readable to agents.
3. **A friction log** (`docs/friction-log.md`): one line each time Tom needs something
   explained twice or reverses a decision he misread.

When the Interpreter is built, it renders decision cards and cannot paraphrase a decision
into existence. Its conversation with Tom (questioning, explaining) is tested separately.

**Conflict it settled.** The brief deferred the human interface; kickoff then ended with 13
questions for Tom, several of them technical (D-006, D-007).

**Why.** Deferring the agent is right: it would translate Council output that does not exist
yet, and its design should come from observed friction. Deferring its job is not: G2 assumes
Tom understands the plan he approves.

**Decided.** Tom, 17 November 2026 (D-008).
