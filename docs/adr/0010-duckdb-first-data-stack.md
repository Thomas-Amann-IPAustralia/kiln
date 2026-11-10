---
status: accepted
source: charter Appendix A, row 10
---

# DuckDB first, Polars for transforms, Pandera for contracts

DuckDB first; Polars for Data Engineer transforms; pandas only where a library needs it; Pandera as the shared contract layer; Great Expectations deferred.

**Conflict it settled.** Data-A puts pandas and Pandera at P0; Data-E puts Polars at P0 and moves from plain assertions to Great Expectations.

**Why.** One contract library for both agents, and Pandera works with both kinds of dataframe.

**Decided.** Settled in the consolidated charter of 10 November 2026.
