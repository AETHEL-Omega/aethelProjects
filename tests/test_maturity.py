"""TC-020, TC-021 — Reifegrad (REQ-010)."""

from __future__ import annotations

from pathlib import Path

from conftest import make_repo

from aethel_projects.discovery import discover
from aethel_projects.maturity import score
from aethel_projects.metrics import collect


def _report(root: Path):
    return collect(discover(root)[0])


def test_tc020_full_artifact_set_is_professional(tmp_path: Path) -> None:
    """TC-020: alle Pflichtartefakte ⇒ Score ≥ 80, Grad Professional."""
    repo = make_repo(tmp_path / "r", commits=1)
    (repo / "docs").mkdir()
    (repo / ".aethel").mkdir()
    (repo / "dna").mkdir()
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / "tests").mkdir()

    (repo / "README.md").write_text("# Projekt\n\nBeschreibung.\n", encoding="utf-8")
    (repo / "docs" / "SPEC.md").write_text(
        "# SPEC\n\n| ID | Anforderung |\n|---|---|\n| REQ-001 | Das System MUST tun. |\n",
        encoding="utf-8",
    )
    (repo / "docs" / "DESIGN.md").write_text(
        "# Design\n\n## Datenmodell\n\nEin Modell mit Feldern.\n\n## Schnittstellen\n\nEine Schnittstelle.\n",
        encoding="utf-8",
    )
    (repo / "docs" / "ARCHITECTURE.md").write_text(
        "# Architektur\n\n## Kontext\n\nEin Kontext.\n\n## Bausteine\n\nEin Baustein.\n",
        encoding="utf-8",
    )
    (repo / "docs" / "TEST-CASES.md").write_text(
        "# Testfälle\n\n| TC | REQ |\n|---|---|\n| TC-001 | REQ-001 |\n", encoding="utf-8"
    )
    (repo / "tests" / "test_x.py").write_text(
        "def test_was():\n    assert True\n", encoding="utf-8"
    )
    (repo / ".github" / "workflows" / "ci.yml").write_text("name: ci\n", encoding="utf-8")
    (repo / "dna" / "genome.yaml").write_text(
        "schema: aethel.dna/v1\nidentity:\n  purpose: Ein echter Zweck.\n", encoding="utf-8"
    )
    (repo / ".aethel" / "engineering.yaml").write_text(
        "schema: aethel.engineering/v1\nmethod:\n  lifecycle: spec-driven\n", encoding="utf-8"
    )

    maturity = score(_report(tmp_path))

    assert maturity.score >= 80, maturity.parts
    assert maturity.grade == "Professional"
    assert maturity.parts["tests"] == 20


def test_tc021_readme_only_scores_ten(tmp_path: Path) -> None:
    """TC-021: nur README ⇒ Score 10, alle anderen Anteile 0."""
    repo = make_repo(tmp_path / "r", commits=1)
    (repo / "README.md").write_text("# Projekt\n", encoding="utf-8")

    maturity = score(_report(tmp_path))

    assert maturity.score == 10
    assert maturity.parts["README"] == 10
    assert maturity.parts["SPEC"] == 0
    assert maturity.parts["tests"] == 0
    assert maturity.grade == "Skizze"


def test_empty_template_does_not_count_as_spec(tmp_path: Path) -> None:
    """Ein SPEC mit Platzhaltern zählt nicht als SPEC."""
    repo = make_repo(tmp_path / "r", commits=1)
    (repo / "docs").mkdir()
    (repo / "docs" / "SPEC.md").write_text(
        "# SPEC\n\n| ID | Anforderung |\n|---|---|\n| REQ-001 | <…> |\n", encoding="utf-8"
    )

    maturity = score(_report(tmp_path))

    assert maturity.parts["SPEC"] == 0


def test_tests_without_assertion_score_eight(tmp_path: Path) -> None:
    """Testdatei ohne echte Assertion ⇒ 8 statt 20 Punkte."""
    repo = make_repo(tmp_path / "r", commits=1)
    (repo / "tests").mkdir()
    (repo / "tests" / "test_leer.py").write_text("# noch keine Assertion\n", encoding="utf-8")

    maturity = score(_report(tmp_path))

    assert maturity.parts["tests"] == 8
