"""TC-039 bis TC-045 — Kontinuität über Git (REQ-019)."""

from __future__ import annotations

from pathlib import Path

from conftest import add_commit, git, make_repo

from aethel_projects import continuity
from aethel_projects.discovery import discover
from aethel_projects.metrics import collect


def _collect(root: Path):
    identities = discover(root)
    return collect(identities[0])


def test_tc039_standort_names_branch_and_commit(tmp_path: Path) -> None:
    """TC-039: der Standort nennt Branch und letzten Commit."""
    repo = make_repo(tmp_path / "r", commits=2)
    add_commit(repo, "Letzte Arbeit", "letzte.txt")

    report = _collect(tmp_path)
    state = continuity.continuity_for(report)

    assert "main" in state.standort
    assert "Letzte Arbeit" in state.standort


def test_tc040_offen_lists_unmerged_branches(tmp_path: Path) -> None:
    """TC-040: ungemergte Branches tauchen unter „offen“ auf."""
    repo = make_repo(tmp_path / "r", commits=2)
    git(repo, "checkout", "-q", "-b", "feature")
    add_commit(repo, "Offene Arbeit", "offen.txt")

    report = _collect(tmp_path)
    state = continuity.continuity_for(report)

    assert any("feature" in eintrag for eintrag in state.offen)
    assert any("ausserhalb" in eintrag for eintrag in state.offen)


def test_tc041_next_step_prefers_unmerged_branch(tmp_path: Path) -> None:
    """TC-041: der ungemergte Branch mit dem größten Vorsprung ist der nächste Schritt."""
    repo = make_repo(tmp_path / "r", commits=2)
    git(repo, "checkout", "-q", "-b", "feature")
    for index in range(3):
        add_commit(repo, f"Arbeit {index}", f"a{index}.txt")

    report = _collect(tmp_path)
    state = continuity.continuity_for(report)

    assert state.naechster_schritt is not None
    assert "feature" in state.naechster_schritt
    assert state.dringlichkeit > 0
    assert "ungemergter" in state.beweis


def test_tc042_next_step_from_documentation(tmp_path: Path) -> None:
    """TC-042: das Projektdokument liefert den nächsten Schritt, wenn Git schweigt."""
    repo = make_repo(tmp_path / "r", commits=2)
    (repo / "README.md").write_text(
        "# Projekt\n\nBeschreibung.\n\n## Nächste Schritte\n\n- [ ] API-Anbindung bauen\n",
        encoding="utf-8",
    )

    report = _collect(tmp_path)
    state = continuity.continuity_for(report)

    assert state.naechster_schritt == "API-Anbindung bauen"
    assert "README.md" in state.beweis


def test_tc043_task_marker_is_recognized(tmp_path: Path) -> None:
    """TC-043: die Aufgabenliste `[ ]` wird als nächster Schritt gelesen."""
    repo = make_repo(tmp_path / "r", commits=2)
    (repo / "docs").mkdir()
    (repo / "docs" / "SPEC.md").write_text(
        "# SPEC\n\n## Nächste Schritte\n\n- [x] Erledigt\n- [ ] Noch offen\n",
        encoding="utf-8",
    )

    report = _collect(tmp_path)
    state = continuity.continuity_for(report)

    assert state.naechster_schritt == "Noch offen"


def test_tc044_no_open_work_means_no_step(tmp_path: Path) -> None:
    """TC-044: ohne offene Arbeit wird kein Schritt behauptet."""
    repo = make_repo(tmp_path / "r", commits=3)

    report = _collect(tmp_path)
    state = continuity.continuity_for(report)

    assert state.naechster_schritt is None
    assert state.dringlichkeit == 0


def test_tc045_workspace_ranks_by_recency(tmp_path: Path) -> None:
    """TC-045: die Workspace-Kontinuität zeigt die zuletzt angefassten Repos zuerst."""
    alt = make_repo(tmp_path / "alt", commits=1)
    neu = make_repo(tmp_path / "neu", commits=1)
    git(alt, "commit", "--amend", "-q", "-m", "Alte Arbeit")
    git(neu, "commit", "--amend", "-q", "-m", "Neue Arbeit")

    identities = discover(tmp_path)
    reports = [collect(identity) for identity in identities]

    view = continuity.build(tuple(reports))

    assert view.zuletzt
    assert view.offene_arbeit == 0
    assert view.naechster_schritt is None


def test_continuity_workspace_counts_open_work(tmp_path: Path) -> None:
    """Die offene Arbeit ist die Summe aller Commits ausserhalb von main."""
    repo = make_repo(tmp_path / "r", commits=2)
    git(repo, "checkout", "-q", "-b", "feature")
    add_commit(repo, "Offen", "offen.txt")

    report = _collect(tmp_path)
    view = continuity.build((report,))

    assert view.offene_arbeit == 1


def test_continuity_reports_uncommitted_hint(tmp_path: Path) -> None:
    """Uncommittete Aenderungen werden als Wiedereinstiegspunkt genannt."""
    repo = make_repo(tmp_path / "r", commits=1)
    (repo / "neu.txt").write_text("offen\n", encoding="utf-8")

    report = _collect(tmp_path)
    view = continuity.build((report,))

    assert view.uncommittet == 1
    assert "uncommittete" in view.hinweis
