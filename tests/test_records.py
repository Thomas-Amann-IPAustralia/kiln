from __future__ import annotations

from pathlib import Path

import pytest

from kiln import records


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
