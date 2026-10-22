"""TC-026 — Projektmanagement-View (REQ-013)."""

from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path

from conftest import make_repo

from aethel_projects.discovery import discover
from aethel_projects.metrics import collect
from aethel_projects.pmview import build


def _report(root: Path):
    return collect(discover(root)[0])


def test_tc026_inactive_repo_has_risk_and_actions(tmp_path: Path) -> None:
    """TC-026: 200 Tage ohne Commit ⇒ inaktiv, Risiko nicht niedrig, Schritte vorhanden."""
    make_repo(tmp_path / "alt", commits=1)
    old = (date.today() - timedelta(days=200)).isoformat()
    report = replace(_report(tmp_path), last_commit_date=old)

    view = build(report)

    assert view.activity == "inactive"
    assert view.risk != "low"
    assert view.next_actions
    assert any("Archiv" in action or "Weiterbau" in action for action in view.next_actions)


def test_active_repo_is_low_risk(tmp_path: Path) -> None:
    """Ein aktuelles, aufgeräumtes Repo ist 'active' mit niedrigem Risiko."""
    make_repo(tmp_path / "frisch", commits=1)
    report = replace(
        _report(tmp_path),
        last_commit_date=date.today().isoformat(),
        commits_not_on_main=0,
        default_branch="main",
    )

    view = build(report)

    assert view.activity == "active"
    assert view.risk == "low"


def test_unmerged_work_raises_risk(tmp_path: Path) -> None:
    """Offene Commits erhöhen das Risiko auf mindestens 'medium'."""
    make_repo(tmp_path / "r", commits=1)
    report = replace(
        _report(tmp_path),
        last_commit_date=date.today().isoformat(),
        commits_not_on_main=12,
        default_branch="main",
    )

    view = build(report)

    assert view.risk in {"medium", "high"}
    assert any("nicht auf main" in action for action in view.next_actions)
