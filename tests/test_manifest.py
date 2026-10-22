"""TC-022, TC-023 — Manifest-Abgleich (REQ-011)."""

from __future__ import annotations

from pathlib import Path

from conftest import make_repo

from aethel_projects.discovery import discover
from aethel_projects.manifest import compare, load_manifest
from aethel_projects.metrics import collect

MANIFEST = """# AETHEL Workspace Manifest
projects:
  - name: vorhanden
    category: core
    status: active
    last_commit: "2026-01-01"
    remote: "https://github.com/AETHEL-Omega/vorhanden.git"
  - name: geist
    category: scratch
    status: scratch
    last_commit: "2026-05-05"
    remote: ""
"""


def _write_manifest(tmp_path: Path) -> Path:
    path = tmp_path / "projects.yaml"
    path.write_text(MANIFEST, encoding="utf-8")
    return path


def test_manifest_is_parsed(tmp_path: Path) -> None:
    """Der Parser liest Name, Kategorie, Status und Datum."""
    entries = load_manifest(_write_manifest(tmp_path))

    assert set(entries) == {"vorhanden", "geist"}
    assert entries["vorhanden"].category == "core"
    assert entries["vorhanden"].status == "active"
    assert entries["vorhanden"].last_commit == "2026-01-01"


def test_tc022_manifest_entry_without_local_repo_is_orphan(tmp_path: Path) -> None:
    """TC-022: Manifest-Eintrag ohne lokales Repo ⇒ 'verwaist'."""
    make_repo(tmp_path / "vorhanden", commits=1)
    manifest = load_manifest(_write_manifest(tmp_path))
    reports = tuple(collect(i) for i in discover(tmp_path))

    findings = compare(reports, manifest)

    orphans = [f for f in findings if f.code == "manifest-wittern"]
    assert len(orphans) == 1
    assert orphans[0].repo == "geist"


def test_tc023_stale_manifest_date_is_reported(tmp_path: Path) -> None:
    """TC-023: Manifest-Datum älter als der lokale letzte Commit ⇒ Drift."""
    repo = make_repo(tmp_path / "vorhanden", commits=1)
    manifest = load_manifest(_write_manifest(tmp_path))
    reports = tuple(collect(i) for i in discover(tmp_path))

    findings = compare(reports, manifest)

    stale = [f for f in findings if f.code == "manifest-veraltet"]
    assert len(stale) == 1
    assert stale[0].repo == "vorhanden"
    assert "2026-01-01" in stale[0].message


def test_repo_missing_in_manifest_is_reported(tmp_path: Path) -> None:
    """Ein lokales Repo ohne Manifest-Eintrag wird gemeldet."""
    make_repo(tmp_path / "vorhanden", commits=1)
    make_repo(tmp_path / "ausserhalb", commits=1)
    manifest = load_manifest(_write_manifest(tmp_path))
    reports = tuple(collect(i) for i in discover(tmp_path))

    findings = compare(reports, manifest)

    missing = [f for f in findings if f.code == "manifest-fehlt"]
    assert [f.repo for f in missing] == ["ausserhalb"]


def test_missing_manifest_file_is_not_fatal(tmp_path: Path) -> None:
    """Fehlende Manifest-Datei ⇒ leere Map, kein Absturz."""
    entries = load_manifest(tmp_path / "gibt_es_nicht.yaml")
    assert entries == {}
