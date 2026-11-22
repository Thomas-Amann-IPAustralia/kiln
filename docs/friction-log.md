# Friction log

Where Tom and Kiln miss each other. One line per entry, added in the turn it happens, by
whoever notices it. By phase 5 this log is the Interpreter's requirements and its first
evaluation set (ADR-0030).

**Add an entry when** Tom needs something explained a second time, asks what a term or a
number means, reverses a decision he had misread, or answers a question other than the one
asked. Also when a reply or a list asks more of Tom's attention than the decision needs.

**Do not** add praise, status or engineering trouble. Keep entries short; the decision entry
holds the detail.

| Date | What happened | What helped | Source |
| --- | --- | --- | --- |
| 2026-11-10 | Kickoff ended with 13 questions for Tom, several of them technical (files as the record, the ticket verifier). | Splitting the list into five that start the next step and eight that can wait (D-007) | Both document reviews (D-006, D-007) |
| 2026-11-17 | Tom asked whether the documentation "would be considered good practice by AI experts": he could not judge it himself, and Claude had written it. | A second opinion from another provider's model, then a comparison of the two reviews | Tom (D-006, D-007) |
| 2026-11-18 | Tom asked Claude to open a pull request and merge it once the tests passed; ADR-0028, adopted in D-008, says no agent merges, and the pull request held his own approval (`CARD-0001`), which an agent's merge would have forged. | Claude opened the pull request, took it to green and left the merge to Tom, saying why | Tom |
| 2026-11-21 | Tom asked what "the Modal keys" were: the slice 4 reply asked for them by variable name without saying what Modal is, what the keys unlock or where they come from. | Saying what the service is, why Kiln uses it, what the token is and what it costs, before asking for it | Tom |
| 2026-11-22 | Tom asked for one document explaining everything built and planned, the slices, phases and rules, and why: the picture was spread over about 50 files written for agents. | A single self-contained explainer, `docs/kiln-explained.html`, with diagrams, status labels and a table of which rules code enforces | Tom |
