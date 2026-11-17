---
status: accepted
source: D-008
---

# Only Tom approves or merges, and an approval names the exact version approved

No agent merges a pull request, and no agent records an approval in Tom's name. An approval
names what it approves by id and content hash, including the version of every plan or
contract it rests on, so a later edit cannot inherit it.

**Conflict it settled.** Records carry an `actor` field, but a field anyone can write proves
nothing (second opinion, D-007). Claude's sessions act on GitHub under Tom's own account, so
GitHub cannot tell an agent's merge from Tom's, and a required code-owner review can never be
met (D-006).

**Why.** With one person and one identity, Tom's merge is the only human review there is. It
is worth nothing if an agent can perform it.

**The limit, stated plainly.** Today this rests on the rule, not on a mechanism: an agent with
Tom's credentials could break it. Before any coding loop runs unattended, or any gate could be
passed without Tom, approvals need a path no agent can use: a separate identity for agents,
or approvals signed with a key that never enters a cloud session. That choice is Tom's.

**Decided.** Tom, 17 November 2026 (D-008).
