---
status: accepted
source: D-008
---

# An independent verifier sets a ticket's pass; loops cannot edit what judges them

A coding loop never sets its own ticket's `passes` flag. A verifier that is not the loop sets
it, by running the ticket's verification steps and every check on a clean checkout of the
loop's commit. `contracts/`, `fitness/` and each ticket's verification steps are read-only to
loops; a loop that needs one changed raises a typed question.

**Conflict it settled.** The charter let a loop flip its own flag after the checks pass, and
nothing stopped a loop from editing the tests, fitness functions and contracts it is judged
by (review, item 3; D-005 R3).

**Why.** A loop that grades itself can pass by changing the test instead of the code. This is
the charter's own rule that only a validation node writes a pass, applied to tickets.

**Decided.** Tom, 17 November 2026 (D-008).
