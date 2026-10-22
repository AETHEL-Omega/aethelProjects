"""Reifegrad nach AETHEL Engineering Standard v2 (REQ-010).

Inhaltsbasiert: Existenz allein zählt nicht. Ein leeres Template zählt 0.
Gewichte: README 10 · SPEC 15 · DESIGN 10 · ARCHITECTURE 10 · TEST-CASES 10 ·
tests 20 · CI 10 · DNA 10 · engineering.yaml 5.
"""

from __future__ import annotations

import re
from pathlib import Path

from .models import Maturity, RepoReport

PLACEHOLDER = re.compile(r"[<…]")
REQ_LINE = re.compile(r"REQ-\d{3}.*(MUST|SHOULD|MAY)")
TC_LINE = re.compile(r"^\|\s*TC-\d{3}")
TEST_FILE_PATTERNS = ("*_test.*", "test_*.*", "*.test.*", "*_tests.rs", "*_test.dart")
ASSERTION = re.compile(
    r"expect\(|assert|testWidgets|#\[test\]|\bok\(|\bcheck\(|\bit\(|assert_eq!|assert!"
)
SKIP_DIRS = {"node_modules", "target", "build", ".git", "vendor", "_legacy", ".dart_tool"}

WEIGHTS = {
    "README": 10,
    "SPEC": 15,
    "DESIGN": 10,
    "ARCHITECTURE": 10,
    "TEST-CASES": 10,
    "tests": 20,
    "CI": 10,
    "DNA": 10,
    "engineering.yaml": 5,
}


def _content_lines(path: Path, minimum: int = 3) -> bool:
    """Enthält die Datei mindestens `minimum` echte Inhaltszeilen (ohne Platzhalter)?"""
    if not path.is_file():
        return False
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return False
    count = 0
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith(">"):
            continue
        if line.startswith("```") or set(line) <= set("-|: "):
            continue
        if PLACEHOLDER.search(line):
            continue
        count += 1
        if count >= minimum:
            return True
    return False


def _find_doc(repo: Path, name: str) -> Path | None:
    for candidate in (repo / "docs" / name, repo / name):
        if candidate.is_file():
            return candidate
    return None


def _has_spec(repo: Path) -> bool:
    spec = _find_doc(repo, "SPEC.md")
    if spec is None:
        return False
    try:
        content = spec.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return bool(REQ_LINE.search(content))


def _has_test_cases(repo: Path) -> bool:
    doc = _find_doc(repo, "TEST-CASES.md")
    if doc is None:
        return False
    try:
        content = doc.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    for line in content.splitlines():
        if TC_LINE.match(line.strip()) and not PLACEHOLDER.search(line):
            return True
    return False


def _tests_score(repo: Path) -> int:
    """20 bei einer Testdatei mit echter Assertion, sonst 8 bei Vorhandensein."""
    candidates: list[Path] = []
    for pattern in TEST_FILE_PATTERNS:
        candidates.extend(repo.glob(f"**/{pattern}"))
    tests_dir = repo / "tests"
    if tests_dir.is_dir():
        candidates.extend(tests_dir.rglob("*"))
    filtered = [
        p
        for p in candidates
        if p.is_file() and not any(part in SKIP_DIRS for part in p.parts)
    ]
    if not filtered:
        return 0
    for candidate in filtered[:40]:
        try:
            content = candidate.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if ASSERTION.search(content):
            return WEIGHTS["tests"]
    return 8


def _dna_score(repo: Path) -> int:
    genome = repo / "dna" / "genome.yaml"
    if not genome.is_file():
        return 0
    try:
        content = genome.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0
    if "aethel.dna/v1" not in content:
        return 0
    for line in content.splitlines():
        if line.strip().startswith("purpose:") and not PLACEHOLDER.search(line):
            return WEIGHTS["DNA"]
    return 0


def _engineering_score(repo: Path) -> int:
    config = repo / ".aethel" / "engineering.yaml"
    if not config.is_file():
        return 0
    try:
        content = config.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0
    return WEIGHTS["engineering.yaml"] if "aethel.engineering/v1" in content else 0


def score(report: RepoReport) -> Maturity:
    """Bewertet den Reifegrad eines Repositories."""
    repo = Path(report.path)
    parts: dict[str, int] = {}

    readme = next(
        (repo / name for name in ("README.md", "README.rst", "README.txt") if (repo / name).is_file()),
        None,
    )
    parts["README"] = WEIGHTS["README"] if readme else 0
    parts["SPEC"] = WEIGHTS["SPEC"] if _has_spec(repo) else 0
    parts["DESIGN"] = WEIGHTS["DESIGN"] if _content_lines(_find_doc(repo, "DESIGN.md") or repo / "x") else 0
    parts["ARCHITECTURE"] = (
        WEIGHTS["ARCHITECTURE"]
        if _content_lines(_find_doc(repo, "ARCHITECTURE.md") or repo / "x")
        else 0
    )
    parts["TEST-CASES"] = WEIGHTS["TEST-CASES"] if _has_test_cases(repo) else 0
    parts["tests"] = _tests_score(repo)
    parts["CI"] = WEIGHTS["CI"] if (repo / ".github" / "workflows").is_dir() else 0
    parts["DNA"] = _dna_score(repo)
    parts["engineering.yaml"] = _engineering_score(repo)

    total = sum(parts.values())
    if total >= 80:
        grade = "Professional"
    elif total >= 50:
        grade = "Solide"
    elif total >= 20:
        grade = "Prototyp"
    else:
        grade = "Skizze"
    return Maturity(score=total, grade=grade, parts=parts)
