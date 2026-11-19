from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from kiln import records, review, spend
from kiln.config import SpendConfig
from kiln.vocabulary import Actor, Basis
from tests.test_cards import PLAN, make_card, write_card


def make_repo(root: Path) -> Path:
    """The smallest repo whose records agree. Each test below breaks one thing in it."""
    (root / "docs/adr").mkdir(parents=True)
    (root / "docs/repo-seeds").mkdir()
    (root / "docs/decisions.md").write_text(
        "# Decision log\n\n"
        "## D-001 — The stack (2026-11-10)\n\nText.\n\n"
        "## D-002 — The records (2026-11-11)\n\nText.\n",
        encoding="utf-8",
    )
    (root / "docs/handover.md").write_text(
        "# Handover\n\nSee [the log](decisions.md).\n\nNext free decision number: D-003\n",
        encoding="utf-8",
    )
    (root / "docs/adr/0001-first.md").write_text(
        "---\nstatus: superseded by ADR-0002\n---\n\n# First\n\nWhy.\n", encoding="utf-8"
    )
    (root / "docs/adr/0002-second.md").write_text(
        "---\nstatus: accepted\n---\n\n# Second\n\nWhy.\n", encoding="utf-8"
    )
    (root / "docs/adr/README.md").write_text(
        "# ADRs\n\n- [First](0001-first.md)\n- [Second](0002-second.md)\n", encoding="utf-8"
    )
    seed = root / "docs/repo-seeds/A Seed.md"
    seed.write_text("A [dead link](gone.md) in a seed is not ours to fix.\n", encoding="utf-8")
    (root / "docs/repo-seeds/MANIFEST.sha256").write_text(
        f"{records.sha256_of(seed)}  A Seed.md\n", encoding="utf-8"
    )
    return root


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    return make_repo(tmp_path)


def messages(root: Path) -> list[str]:
    return [problem.one_line() for problem in records.check_all(root)]


def test_this_repos_records_agree(repo_root: Path) -> None:
    """Why: the next session trusts these records, so CI proves them on every change."""
    assert messages(repo_root) == []


def test_the_fixture_repo_is_clean(repo: Path) -> None:
    """Why: every test below must fail for its own reason and no other."""
    assert messages(repo) == []


def test_a_skipped_decision_number_is_found(repo: Path) -> None:
    """Why: a gap in the log reads as a lost decision."""
    path = repo / "docs/decisions.md"
    path.write_text(path.read_text().replace("D-002", "D-004"))
    assert any("expected D-002" in m for m in messages(repo))


def test_a_malformed_decision_heading_is_found(repo: Path) -> None:
    """Why: entries are found by their heading, so a loose one would vanish from every count."""
    path = repo / "docs/decisions.md"
    path.write_text(path.read_text() + "\n## D-003: no dash or date\n")
    assert any("heading is not" in m for m in messages(repo))


def test_a_backdated_decision_is_found(repo: Path) -> None:
    """Why: the log is append-only, so dates never run backwards."""
    path = repo / "docs/decisions.md"
    path.write_text(path.read_text().replace("2026-11-11", "2026-11-09"))
    assert any("append-only" in m for m in messages(repo))


def test_a_stale_handover_number_is_found(repo: Path) -> None:
    """Why: two sessions that trust a stale number write two entries with one id."""
    path = repo / "docs/handover.md"
    path.write_text(path.read_text().replace("D-003", "D-002"))
    assert any("the log makes it D-003" in m for m in messages(repo))


def test_an_adr_missing_from_the_index_is_found(repo: Path) -> None:
    """Why: the index is how a reader finds the ruling that binds them."""
    (repo / "docs/adr/README.md").write_text("# ADRs\n\n- [First](0001-first.md)\n")
    assert any("does not link 0002-second.md" in m for m in messages(repo))


def test_an_adr_without_a_status_is_found(repo: Path) -> None:
    """Why: a proposed ruling must never be mistaken for an accepted one."""
    (repo / "docs/adr/0002-second.md").write_text("# Second\n\nWhy.\n")
    assert any("no `status:` line" in m for m in messages(repo))


def test_an_adr_superseded_by_nothing_is_found(repo: Path) -> None:
    """Why: a superseded ruling must lead to the one that replaced it."""
    path = repo / "docs/adr/0001-first.md"
    path.write_text(path.read_text().replace("ADR-0002", "ADR-0009"))
    assert any("ADR-0009, which does not exist" in m for m in messages(repo))


def test_a_skipped_adr_number_is_found(repo: Path) -> None:
    """Why: ADR numbers are cited from decisions and code, so they stay dense and stable."""
    (repo / "docs/adr/0002-second.md").rename(repo / "docs/adr/0005-second.md")
    assert any("expected ADR-0002" in m for m in messages(repo))


def test_a_changed_seed_is_found(repo: Path) -> None:
    """Why: the live docs were derived from the seeds as sealed; a changed seed means the
    derivation is stale (the SOP's 'a source changed under its snapshot')."""
    (repo / "docs/repo-seeds/A Seed.md").write_text("Rewritten.\n")
    assert any("changed since it was sealed" in m for m in messages(repo))


def test_a_new_seed_is_found(repo: Path) -> None:
    """Why: a document dropped into the seeds has not been reconciled with the charter."""
    (repo / "docs/repo-seeds/New Proposal.md").write_text("New.\n")
    assert any("not in the manifest" in m for m in messages(repo))


def test_a_deleted_seed_is_found(repo: Path) -> None:
    """Why: the record of what the design was derived from must not shrink silently."""
    (repo / "docs/repo-seeds/A Seed.md").unlink()
    assert any("missing from disk" in m for m in messages(repo))


def test_a_broken_link_in_a_live_doc_is_found(repo: Path) -> None:
    """Why: docs are the handover; a link to a moved file strands the next reader."""
    path = repo / "docs/handover.md"
    path.write_text(path.read_text() + "\nSee [the plan](plan.md#phase-0).\n")
    assert any("broken link: plan.md#phase-0" in m for m in messages(repo))


def test_links_in_code_and_to_the_web_are_left_alone(repo: Path) -> None:
    """Why: templates show placeholder links, and the web is not ours to check offline."""
    path = repo / "docs/handover.md"
    path.write_text(
        path.read_text()
        + "\n`[x](nowhere.md)` and [a site](https://example.com) and [here](#top).\n"
        + "\n```md\n[template](reports/<file>.md)\n```\n"
    )
    assert messages(repo) == []


def test_a_card_resting_on_a_changed_file_fails_the_records_check(repo: Path) -> None:
    """Why: the records check runs before every commit, so a quiet edit to what Tom approved
    is stopped there, not discovered after the merge."""
    (repo / PLAN).write_text("# Placeholder plan\n")
    write_card(repo, make_card(repo))
    assert messages(repo) == []
    (repo / PLAN).write_text("# Placeholder plan, edited\n")
    assert any("needs a new card" in m for m in messages(repo))


def add_paid_response(repo: Path, usd: float = 0.25, *, settled: bool = True) -> str:
    """One cached review response, and (unless `settled` is false) its ledger entries."""
    digest = "a" * 64
    path = f"docs/reviews/cache/{digest}.json"
    record = review.ReviewRecord(
        request_sha256=digest,
        spec="docs/reviews/spec.yaml",
        budget="small",
        model="example-model",
        effort="high",
        request={},
        http_status=200,
        status="completed",
        incomplete_reason=None,
        usage=None,
        usd=usd,
        estimate=review.Estimate(
            input_tokens_bound=1, output_tokens_bound=1, usd_bound=0.5, assumes="fixture"
        ),
        answer="Placeholder answer.",
        response=None,
    )
    (repo / "docs/reviews/cache").mkdir(parents=True)
    (repo / path).write_text(record.model_dump_json(indent=2) + "\n", encoding="utf-8")
    if settled:
        at = datetime(2026, 11, 18, 9, 0, tzinfo=UTC)
        entries = [
            spend.Reservation(
                entry=1,
                at=at,
                budget="small",
                usd=0.5,
                command="kiln review",
                ref=f"sha256:{digest}",
                by=Actor.BUILD_SESSION,
            ),
            spend.Settlement(
                entry=2,
                at=at,
                reservation=1,
                usd=0.25,
                outcome="completed",
                basis=Basis.OBSERVED,
                record=path,
                by=Actor.BUILD_SESSION,
            ),
        ]
        ledger = repo / SpendConfig().ledger
        ledger.parent.mkdir(parents=True, exist_ok=True)
        ledger.write_text(
            "".join(spend.canonical_line(entry) + "\n" for entry in entries), encoding="utf-8"
        )
    return path


def test_a_paid_response_in_the_ledger_agrees(repo: Path) -> None:
    """Why: the fixture for the three tests below must start clean."""
    add_paid_response(repo)
    assert records.check_spend(repo) == []


def test_a_paid_response_missing_from_the_ledger_is_found(repo: Path) -> None:
    """Why: spend recorded only beside its response is spend the budget guard cannot see."""
    path = add_paid_response(repo, settled=False)
    problems = records.check_spend(repo)
    assert [(p.path.as_posix(), "has 0" in p.message) for p in problems] == [(path, True)]


def test_a_ledger_that_disagrees_with_its_response_is_found(repo: Path) -> None:
    """Why: two records of one cost that differ mean one of them is wrong."""
    add_paid_response(repo, usd=0.30)
    (problem,) = records.check_spend(repo)
    assert "records $0.3" in problem.message


def test_a_ledger_naming_a_missing_response_is_found(repo: Path) -> None:
    """Why: a cost must rest on a committed record of the call."""
    path = add_paid_response(repo)
    (repo / path).unlink()
    (problem,) = records.check_spend(repo)
    assert "which is missing" in problem.message
