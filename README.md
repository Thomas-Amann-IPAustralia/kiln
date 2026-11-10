# Kiln

A software factory. A **Council** of seven expert agents plans and assures a solution, a
**coding swarm** builds it, and a **shared core** carries the records, gates and sandboxes
they all use. The Council hands over a test-ready build; nothing reaches production before a
real-world test and human experts.

**Status: phase 0 of 6.** The foundation is in place: the rulebook, the records, the live
charter and CI. No part of the shared core or any agent is built yet.

## Where to start

| If you are | Read |
| --- | --- |
| Tom | [`docs/handover.md`](docs/handover.md), "For Tom" |
| A Claude Code session | [`CLAUDE.md`](CLAUDE.md), then the handover |
| Any coding agent | [`AGENTS.md`](AGENTS.md) |
| Anyone asking what Kiln is | [`docs/charter/`](docs/charter/README.md) |

## What the repo holds

| Path | What |
| --- | --- |
| `CLAUDE.md`, `AGENTS.md` | How to work here: with Tom, and on the code |
| `GLOSSARY.md` | The one vocabulary |
| `docs/charter/` | The controlling design for the Council |
| `docs/adr/` | The rulings behind the design, ADR-0001 onwards |
| `docs/decisions.md` | The log of what was decided, measured and spent while building Kiln |
| `docs/handover.md` | Where things stand, and what is open |
| `docs/sketches/` | Designs proposed for Tom's approval |
| `docs/repo-seeds/` | The sealed planning documents everything above was derived from |
| `config/kiln.yaml` | The outside services Kiln depends on, by phase |
| `src/kiln/`, `tests/` | The code and its tests |

## Commands

```bash
make setup    # install locked dependencies and the pre-commit hooks (needs uv)
```

```bash
make check    # lint, format check, type check, tests and the records check: what CI runs
```

```bash
make doctor   # is this machine ready for the current phase? Free; spends nothing
```

```bash
uv run kiln records check   # do the decision log, ADRs, handover, seeds and links agree?
```

No command in this repo spends money yet.

## Licence

MIT. See [`LICENSE`](LICENSE).
