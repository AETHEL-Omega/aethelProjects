"""TC-024, TC-025 — Aufräum-Vorschläge (REQ-012)."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from conftest import make_repo

from aethel_projects.discovery import discover
from aethel_projects.findings import detect, detect_duplicates
from aethel_projects.metrics import collect


def _report(root: Path):
    return collect(discover(root)[0])


def test_tc024_many_commits_not_on_main_is_critical(tmp_path: Path) -> None:
    """TC-024: > 50 Commits nicht auf main ⇒ Schweregrad critical."""
    repo = make_repo(tmp_path / "r", commits=1)
    report = replace(
        _report(tmp_path), commits_not_on_main=200, branches_unmerged=3
    )

    findings = detect(report)

    critical = [f for f in findings if f.code == "not-on-main"]
    assert critical
    assert critical[0].severity == "critical"
    assert "200" in critical[0].message


def test_tc025_missing_main_is_reported_without_executing(tmp_path: Path) -> None:
    """TC-025: fehlender Default-Branch ⇒ Finding 'no-main'; keine ausgeführte Aktion."""
    make_repo(tmp_path / "r", commits=1, branch="trunk")
    report = _report(tmp_path)

    findings = detect(report)

    no_main = [f for f in findings if f.code == "no-main"]
    assert len(no_main) == 1
    assert no_main[0].severity == "warn"
    # Die Empfehlung ist Text, keine ausgeführte Operation.
    assert isinstance(no_main[0].action, str)


def test_findings_carry_repo_name(tmp_path: Path) -> None:
    """Jedes Finding nennt sein Repository."""
    make_repo(tmp_path / "meinrepo", commits=1)
    report = _report(tmp_path)

    findings = detect(report)

    assert all(f.repo == "meinrepo" for f in findings)


def test_duplicate_detection_groups_by_intent(tmp_path: Path) -> None:
    """Zwei Repos mit gleichem Zweck werden als Duplikat-Kandidat gemeldet."""
    from aethel_projects.models import Intent

    make_repo(tmp_path / "a", commits=1)
    make_repo(tmp_path / "b", commits=1)
    reports = tuple(collect(i) for i in discover(tmp_path))
    text = "Diese Anwendung verwaltet Rechnungen und Belege für kleine Betriebe."
    reports = tuple(
        replace(r, intent=Intent(text=text, confidence="high", source="README.md", evidence=text))
        for r in reports
    )

    findings = detect_duplicates(reports)

    assert len(findings) == 2
    assert all(f.code == "duplicate" for f in findings)
