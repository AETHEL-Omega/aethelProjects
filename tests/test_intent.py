"""TC-017 bis TC-019 — Intent-Erkennung (REQ-009)."""

from __future__ import annotations

from pathlib import Path

from conftest import make_repo

from aethel_projects.intent import infer
from aethel_projects.metrics import collect
from aethel_projects.discovery import discover


def _report(root: Path):
    return collect(discover(root)[0])


def test_tc017_spec_wins_with_high_confidence(tmp_path: Path) -> None:
    """TC-017: docs/SPEC.md liefert den Zweck mit hoher Konfidenz."""
    repo = make_repo(tmp_path / "r", commits=1)
    (repo / "docs").mkdir()
    (repo / "docs" / "SPEC.md").write_text(
        "# SPEC — Projekt\n\n## Zweck (ein Satz)\n\n"
        "Dieses Werkzeug analysiert den gesamten AETHEL-Workspace und liefert einen "
        "entscheidbaren Portfolio-Überblick.\n\n## Scope\n- x\n",
        encoding="utf-8",
    )
    (repo / "README.md").write_text("# Projekt\n\nEin anderes Repository hier.\n", encoding="utf-8")

    intent = infer(_report(tmp_path))

    assert intent is not None
    assert intent.confidence == "high"
    assert intent.source == "docs/SPEC.md"
    assert "analysiert den gesamten AETHEL-Workspace" in intent.text


def test_tc018_readme_is_medium_confidence(tmp_path: Path) -> None:
    """TC-018: README-Absatz ergibt mittlere Konfidenz."""
    repo = make_repo(tmp_path / "r", commits=1)
    (repo / "README.md").write_text(
        "# Projekt\n\nDieses Repository enthält die vollständige Implementierung "
        "der lokalen Coding-Agent-Flotte mit Gate und Solver.\n",
        encoding="utf-8",
    )

    intent = infer(_report(tmp_path))

    assert intent is not None
    assert intent.confidence == "medium"
    assert intent.source == "README.md"
    assert "Coding-Agent-Flotte" in intent.text


def test_tc019_no_source_means_no_invented_intent(tmp_path: Path) -> None:
    """TC-019: ohne Quelle wird kein Zweck erfunden."""
    repo = make_repo(tmp_path / "r", commits=1)

    intent = infer(_report(tmp_path))

    assert intent is None or intent.text is None


def test_pubspec_description_is_used(tmp_path: Path) -> None:
    """pubspec.yaml description dient als Quelle."""
    repo = make_repo(tmp_path / "r", commits=1)
    (repo / "pubspec.yaml").write_text(
        "name: beispiel\ndescription: Eine Flutter-App zur Verwaltung von Rechnungen.\n",
        encoding="utf-8",
    )

    intent = infer(_report(tmp_path))

    assert intent is not None
    assert intent.source == "pubspec.yaml"
    assert "Rechnungen" in intent.text


def test_placeholder_is_not_accepted(tmp_path: Path) -> None:
    """Platzhalter gelten nicht als Quelle."""
    repo = make_repo(tmp_path / "r", commits=1)
    (repo / "docs").mkdir()
    (repo / "docs" / "SPEC.md").write_text(
        "# SPEC\n\n## Zweck (ein Satz)\n\n<…>\n", encoding="utf-8"
    )

    intent = infer(_report(tmp_path))

    assert intent is None or intent.text is None
