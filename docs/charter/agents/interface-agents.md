# Interface agents (deferred)

## Interpreter (deferred)

The Interpreter is Tom's single point of contact with the Council. It explains Council outputs in plain language, and questions Tom until an instruction is clear enough to act on. It never makes domain decisions, and never softens a hard constraint while explaining it.

Its three moves map to Pocock skills: grilling Tom before work starts (`/grill-with-docs`), re-explaining anything that did not land (`/wait-what`), and turning a question only a human expert can answer into a questionnaire (`/to-questionnaire`). Voice comes later.

Until it exists, Tom runs `/grill-with-docs` at intake himself. Every decision put to Tom uses one format: options, consequences, recommendation and dissent.

## Illustrator (deferred)

The Illustrator reports to the Interpreter and draws decision aids, because Tom learns visually. It draws only from structured Council state: C4 models, decision packets, journeys and the matrix. It adds no content of its own, so every picture traces back to a record. Its first tools are Structurizr and Mermaid rendering, and Vega-Lite charts.
