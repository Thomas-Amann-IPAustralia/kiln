# Sample briefs

Three synthetic briefs, each written as a project profile: a public form service, an internal
RAG assistant and a data dashboard. They are the chair's first evaluation set
([`docs/charter/agents/solution-architect.md`](../../docs/charter/agents/solution-architect.md),
"First slice") and the briefs phase 0's thin path runs on.

- **Synthetic.** Claude wrote them. They describe no real service, agency or person, and hold
  no real data.
- **Drafts.** Tom approves an evaluation set before any run uses it (first move 9). Until then
  they are fixtures: `tests/test_profile.py` checks that each validates as a profile.
- **Chosen to differ.** Between them they cover each audience (Tom's team, the agency, the
  public), each effect (informs, acts), facts stated and inferred, and facts still `unknown`.
  None of them decides about people, a case the set will need before the chair is evaluated.
