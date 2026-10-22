"""Manifest-Abgleich gegen workspace-manifest/projects.yaml (REQ-011).

Das Manifest ist die kanonische Registrierung. `aethelProjects` liest es und meldet
Drift — es schreibt es nie.
"""

from __future__ import annotations

import re
from pathlib import Path

from .models import Finding, ManifestEntry, RepoReport

DEFAULT_MANIFEST = Path.home() / "workspace" / "workspace-manifest" / "projects.yaml"

_NAME = re.compile(r"^\s*-\s*name:\s*(.+?)\s*$")
_FIELD = re.compile(r"^\s{4}(category|status|last_commit|remote):\s*(.*?)\s*$")


def _strip_quotes(value: str) -> str:
    return value.strip().strip('"').strip("'")


def load_manifest(path: Path | str | None = None) -> dict[str, ManifestEntry]:
    """Liest projects.yaml. Gibt bei fehlender/kaputter Datei eine leere Map zurück."""
    manifest_path = Path(path) if path else DEFAULT_MANIFEST
    if not manifest_path.is_file():
        return {}

    entries: dict[str, ManifestEntry] = {}
    current: str | None = None
    data: dict[str, str] = {}

    def flush() -> None:
        if current is None:
            return
        entries[current] = ManifestEntry(
            name=current,
            category=data.get("category", "-"),
            status=data.get("status", "-"),
            last_commit=data.get("last_commit"),
            remote=data.get("remote"),
        )

    try:
        lines = manifest_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return {}

    for line in lines:
        name_match = _NAME.match(line)
        if name_match:
            flush()
            current = _strip_quotes(name_match.group(1))
            data = {}
            continue
        field_match = _FIELD.match(line)
        if field_match and current:
            data[field_match.group(1)] = _strip_quotes(field_match.group(2))
    flush()
    return entries


def compare(
    repos: tuple[RepoReport, ...],
    manifest: dict[str, ManifestEntry],
) -> tuple[Finding, ...]:
    """Vergleicht den Ist-Zustand mit dem Manifest."""
    findings: list[Finding] = []
    local_names = {r.name for r in repos}

    for name, entry in sorted(manifest.items()):
        if name not in local_names:
            findings.append(
                Finding(
                    code="manifest-wittern",
                    severity="warn",
                    message=f"Im Manifest als '{entry.status}' geführt, lokal nicht vorhanden.",
                    action=f"Manifest prüfen: Eintrag '{name}' entfernen oder Repository wiederherstellen.",
                    repo=name,
                )
            )

    for repo in repos:
        entry = manifest.get(repo.name)
        if entry is None:
            findings.append(
                Finding(
                    code="manifest-fehlt",
                    severity="info",
                    message="Im Manifest nicht geführt.",
                    action=f"Manifest ergänzen: 'projects.yaml' um '{repo.name}' erweitern.",
                    repo=repo.name,
                )
            )
            continue
        if entry.last_commit and repo.last_commit_date and entry.last_commit < repo.last_commit_date:
            findings.append(
                Finding(
                    code="manifest-veraltet",
                    severity="info",
                    message=(
                        f"Manifest nennt last_commit {entry.last_commit}, "
                        f"lokal ist {repo.last_commit_date}."
                    ),
                    action="Manifest-Datum aktualisieren.",
                    repo=repo.name,
                )
            )

    return tuple(findings)
