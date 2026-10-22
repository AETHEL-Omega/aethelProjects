"""TC-031 — Abdeckung: jede REQ hat ≥1 TC, jeder TC verweist auf existierende REQ."""

from __future__ import annotations

import re
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1] / "docs"

REQ_PATTERN = re.compile(r"^\|\s*(REQ-\d{3})\s*\|", re.MULTILINE)
TC_PATTERN = re.compile(r"^\|\s*(TC-\d{3})\s*\|", re.MULTILINE)
#: Jede Zeile, die mit einer ID beginnt (Definition, nicht Erwähnung).
TC_DEFINITION = re.compile(r"^\|\s*(TC-\d{3})\s*\|", re.MULTILINE)
REQ_DEFINITION = re.compile(r"^\|\s*(REQ-\d{3})\s*\|", re.MULTILINE)
TC_ROW_REFS = re.compile(r"TC-\d{3}")
REQ_ROW_REFS = re.compile(r"REQ-\d{3}")


def _spec_requirements() -> set[str]:
    return set(REQ_PATTERN.findall((DOCS / "SPEC.md").read_text(encoding="utf-8")))


def _test_case_ids() -> set[str]:
    return set(TC_PATTERN.findall((DOCS / "TEST-CASES.md").read_text(encoding="utf-8")))


def test_every_requirement_has_a_test_case() -> None:
    """Jede REQ-NNN aus der SPEC hat mindestens eine TC-NNN."""
    spec = (DOCS / "SPEC.md").read_text(encoding="utf-8")
    cases = (DOCS / "TEST-CASES.md").read_text(encoding="utf-8")

    requirements = _spec_requirements()
    assert requirements, "SPEC enthält keine REQ"

    covered = {
        req
        for req in requirements
        if re.search(rf"\|[^|]*\b{re.escape(req)}\b[^|]*\|", cases)
    }
    missing = requirements - covered
    assert not missing, f"REQ ohne Testfall: {sorted(missing)}"


def test_every_test_case_points_to_an_existing_requirement() -> None:
    """Jede TC-NNN verweist auf eine REQ, die in der SPEC existiert."""
    spec = (DOCS / "SPEC.md").read_text(encoding="utf-8")
    cases = (DOCS / "TEST-CASES.md").read_text(encoding="utf-8")

    requirements = set(REQ_PATTERN.findall(spec))
    referenced = set(REQ_ROW_REFS.findall(cases))
    unknown = referenced - requirements
    assert not unknown, f"TC verweist auf unbekannte REQ: {sorted(unknown)}"


def test_test_case_ids_are_unique() -> None:
    """Keine doppelt vergebenen TC-NNN (Definitionszeilen, nicht Erwähnungen)."""
    text = (DOCS / "TEST-CASES.md").read_text(encoding="utf-8")
    ids = re.findall(r"^\|\s*(TC-\d{3})\s*\|\s*REQ-", text, re.MULTILINE)
    assert ids, "keine TC-Definitionen gefunden"
    assert len(ids) == len(set(ids)), "doppelte TC-NNN"


def test_requirement_ids_are_unique() -> None:
    """Keine doppelt vergebenen REQ-NNN (Definitionszeilen der Anforderungstabelle)."""
    text = (DOCS / "SPEC.md").read_text(encoding="utf-8")
    ids = re.findall(r"^\|\s*(REQ-\d{3})\s*\|\s*(?:MUST|SHOULD|MAY)\s*\|", text, re.MULTILINE)
    assert ids, "keine REQ-Definitionen gefunden"
    assert len(ids) == len(set(ids)), "doppelte REQ-NNN"


def test_documented_artifacts_exist() -> None:
    """Die im Engineering Standard geforderten Artefakte liegen im Repo."""
    root = Path(__file__).resolve().parents[1]
    for relative in (
        "README.md",
        "docs/SPEC.md",
        "docs/DESIGN.md",
        "docs/ARCHITECTURE.md",
        "docs/TEST-CASES.md",
        ".aethel/engineering.yaml",
        "dna/genome.yaml",
        "dna/GENOME.md",
        ".github/workflows/ci.yml",
        "tests",
        "src/aethel_projects",
    ):
        assert (root / relative).exists(), f"fehlt: {relative}"
