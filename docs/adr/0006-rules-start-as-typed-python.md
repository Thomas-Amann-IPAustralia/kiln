---
status: accepted
source: charter Appendix A, row 6
---

# Rules start as typed Python; Conftest and OPA wait

Rules start as typed Python with unit tests. Conftest arrives with the first infrastructure code, and OPA only when rule maintenance is the bottleneck.

**Conflict it settled.** Security puts OPA and Conftest at the core now; Governance defers OPA; Solution rates it P1.

**Why.** The stack is Python. The guarantee Security wants, that approvals cannot be faked, comes from gates and database records, not from OPA.

**Decided.** Settled in the consolidated charter of 10 November 2026.
