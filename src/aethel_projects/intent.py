"""Intent-Erkennung (REQ-009).

Regelbasiert und ehrlich: ohne Fund wird ``Intent(text=None)`` geliefert.
Der Report erfindet **niemals** einen Zweck (ADR-004).
"""

from __future__ import annotations

import re
from pathlib import Path

from .models import Intent, RepoReport

MAX_TEXT = 240

SPEC_SECTION = re.compile(
    r"^#{1,3}\s*zweck\b.*?^\s*(.+?)\s*$",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)
PLACEHOLDER = re.compile(r"[<…]|^\s*(TODO|TBD)\b", re.IGNORECASE)
NOISE_LINE = re.compile(
    r"^(badges?|license|installation|usage|quick ?start|table of contents|"
    r"introduction|contributing|status|build|ci|dna|architecture|design)\b",
    re.IGNORECASE,
)


def _clean(text: str) -> str:
    """Entfernt Markdown-Auszeichnungen und kürzt."""
    stripped = re.sub(r"[`*_>#]", "", text)
    stripped = re.sub(r"\s+", " ", stripped).strip()
    return stripped[:MAX_TEXT]


def _from_spec(path: Path) -> Intent | None:
    """Abschnitt „Zweck (ein Satz)" aus docs/SPEC.md."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    match = SPEC_SECTION.search(content)
    if not match:
        return None
    text = _clean(match.group(1))
    if not text or PLACEHOLDER.search(text):
        return None
    return Intent(text=text, confidence="high", source="docs/SPEC.md", evidence=text)


def _from_readme(path: Path) -> Intent | None:
    """Erster Prosaabsatz nach der Überschrift."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    paragraph: list[str] = []
    in_code = False
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if not line:
            if paragraph:
                break
            continue
        if line.startswith("#"):
            if paragraph:
                break
            continue
        if NOISE_LINE.match(line) or line.startswith("|") or line.startswith("!["):
            continue
        if PLACEHOLDER.search(line):
            continue
        paragraph.append(line)
    if not paragraph:
        return None
    text = _clean(" ".join(paragraph))
    if len(text) < 15:
        return None
    return Intent(text=text, confidence="medium", source="README.md", evidence=text)


def _from_manifest_field(repo: Path) -> Intent | None:
    """`description:` aus pubspec.yaml / package.json / pyproject.toml."""
    candidates = {
        "pubspec.yaml": re.compile(r"^description:\s*(.+)$", re.MULTILINE),
        "package.json": re.compile(r'"description"\s*:\s*"([^"]+)"'),
        "pyproject.toml": re.compile(r'^description\s*=\s*"([^"]+)"', re.MULTILINE),
        "Cargo.toml": re.compile(r'^description\s*=\s*"([^"]+)"', re.MULTILINE),
    }
    for filename, pattern in candidates.items():
        candidate = repo / filename
        if not candidate.is_file():
            continue
        try:
            content = candidate.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        match = pattern.search(content)
        if not match:
            continue
        text = _clean(match.group(1).strip("\"'"))
        if not text or PLACEHOLDER.search(text) or len(text) < 8:
            continue
        return Intent(text=text, confidence="medium", source=filename, evidence=text)
    return None


def _from_manifest_entry(report: RepoReport) -> Intent | None:
    """Name + Kategorie aus projects.yaml — niedrige Konfidenz."""
    entry = report.manifest_entry
    if entry is None:
        return None
    text = f"{entry.name} — Kategorie {entry.category} (Status {entry.status})"
    return Intent(text=text, confidence="low", source="manifest", evidence=text)


def infer(report: RepoReport) -> Intent | None:
    """Bestimmt den Intent eines Repositories, priorisiert nach Verlässlichkeit."""
    repo = Path(report.path)

    for candidate in (repo / "docs" / "SPEC.md", repo / "SPEC.md"):
        if candidate.is_file():
            intent = _from_spec(candidate)
            if intent:
                return intent

    for candidate in (repo / "README.md", repo / "README.rst", repo / "README.txt"):
        if candidate.is_file():
            intent = _from_readme(candidate)
            if intent:
                return intent

    intent = _from_manifest_field(repo)
    if intent:
        return intent

    return _from_manifest_entry(report)
