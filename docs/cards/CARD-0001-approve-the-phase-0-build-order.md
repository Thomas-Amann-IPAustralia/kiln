---
id: CARD-0001
title: Approve the phase 0 build order
put_by: build_session
put_on: '2026-11-17'
question: Approve the build order in the phase 0 sketch?
options:
- label: Approve
  consequences: 'Slice 1 starts: the record formats, the decision card and `kiln approvals`. It needs
    no money and no secrets. The sketch is frozen, so a change to it comes back to Tom.'
- label: Decline
  consequences: Nothing is built. The sketch is revised again or replaced.
recommendation:
  option: Approve
  reason: 'The sketch carries the changes Tom adopted after two reviews (D-008), and slice 1 can be undone:
    no code depends on it yet.'
dissent: []
undo:
  possible: true
  how: A later card that supersedes this one changes the order, while no code depends on it.
if_no_answer: Nothing is built.
rests_on:
- path: docs/sketches/phase-0-shared-core.md
  sha256: sha256:4108af325f38e33c5021aac1d92c44c8ccfee48c5c5596a6d060cfab0438ac12
gate: null
supersedes: null
answer:
  choice: Approve
  words: I approve the phase 0 build order. Please commence thoughtfully
  answered_on: '2026-11-18'
---

# CARD-0001: Approve the phase 0 build order

**The question.** Approve the build order in the phase 0 sketch?

| Option | What it costs or changes |
| --- | --- |
| Approve | Slice 1 starts: the record formats, the decision card and `kiln approvals`. It needs no money and no secrets. The sketch is frozen, so a change to it comes back to Tom. |
| Decline | Nothing is built. The sketch is revised again or replaced. |

**Recommended: Approve.** The sketch carries the changes Tom adopted after two reviews (D-008), and slice 1 can be undone: no code depends on it yet.

**Dissent.** None recorded.

**Can it be undone?** Yes. A later card that supersedes this one changes the order, while no code depends on it.

**If Tom does not answer.** Nothing is built.

**What Tom is approving.** These files, at exactly these versions:

| File | sha256 |
| --- | --- |
| `docs/sketches/phase-0-shared-core.md` | `4108af325f38e33c5021aac1d92c44c8ccfee48c5c5596a6d060cfab0438ac12` |

Put by build_session on 2026-11-17.

**Answer: Approve.** Tom, 2026-11-18: “I approve the phase 0 build order. Please commence thoughtfully”

The answer takes effect when Tom merges this card into `main`. `kiln approvals` shows whether it has.

<!-- Rendered from the front matter by Kiln. Edit the front matter, then run `kiln records render`. -->
