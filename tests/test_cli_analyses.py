"""TC-061, TC-063 — CLI für analyses und registers (REQ-020, REQ-021, REQ-022)."""

from __future__ import annotations

import json
from pathlib import Path

from conftest import make_repo

from aethel_projects.cli import main


def _ablage(tmp_path: Path) -> Path:
    base = tmp_path / "analysen"
    (base / "2026-11-03").mkdir(parents=True)
    (base / "2026-11-03" / "BERICHT.md").write_text("# Ein Bericht\n\nInhalt.\n", encoding="utf-8")
    (base / "vorschlaege.json").write_text(json.dumps({
        "schema": "aethel.projects.vorschlaege/v1",
        "projects": [{"id": "B1", "name": "aethelRegistry", "zweck": "Produkt-ID", "komponente": "aethelRegistry",
                      "vertrag": "aethel.registry/v1", "ebene": "E4", "stufe": 1, "status": "vorgeschlagen"}],
    }), encoding="utf-8")
    (base / "kreislaeufe.json").write_text(json.dumps({
        "schema": "aethel.projects.kreislaeufe/v1",
        "loops": [{"id": "K-E2-gate", "name": "Gate", "ebene": "E2", "status": "teilweise"}],
    }), encoding="utf-8")
    return base


def test_tc061_register_then_list_show_and_stats(tmp_path: Path, capsys) -> None:
    """TC-061: registrieren, auflisten, anzeigen, zählen über die CLI."""
    base = _ablage(tmp_path)
    code = main(["--root", str(tmp_path), "analyses", "--base", str(base), "--register",
                 str(base / "2026-11-03" / "BERICHT.md"), "--scope", "firma", "--summary", "Ein Satz.", "--tags", "a,b"])
    assert code == 0
    assert "registriert: bericht (2026-11-03)" in capsys.readouterr().out

    assert main(["--root", str(tmp_path), "analyses", "--base", str(base), "--list"]) == 0
    out = capsys.readouterr().out
    assert "Ein Bericht" in out and "firma" in out

    assert main(["--root", str(tmp_path), "analyses", "--base", str(base), "--show", "bericht"]) == 0
    assert capsys.readouterr().out.startswith("# Ein Bericht")

    assert main(["--root", str(tmp_path), "analyses", "--base", str(base), "--stats", "--format", "json"]) == 0
    stats = json.loads(capsys.readouterr().out)
    assert stats["analyses"] == 1 and stats["proposals"] == 1 and stats["loops_total"] == 1


def test_tc061_proposals_and_loops_as_json(tmp_path: Path, capsys) -> None:
    """TC-061: Vorschläge und Kreisläufe kommen als JSON mit Schema heraus."""
    base = _ablage(tmp_path)
    assert main(["--root", str(tmp_path), "analyses", "--base", str(base), "--proposals", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema"] == "aethel.projects.vorschlaege/v1"
    assert payload["projects"][0]["name"] == "aethelRegistry"

    assert main(["--root", str(tmp_path), "analyses", "--base", str(base), "--loops"]) == 0
    assert "K-E2-gate" in capsys.readouterr().out


def test_tc061_unknown_id_and_out_on_index_are_usage_errors(tmp_path: Path, capsys) -> None:
    """TC-061: unbekannte ID und --out auf INDEX.json geben Exit 2."""
    base = _ablage(tmp_path)
    assert main(["--root", str(tmp_path), "analyses", "--base", str(base), "--show", "gibt-es-nicht"]) == 2
    assert "Unbekannte Analyse" in capsys.readouterr().err
    assert main(["--root", str(tmp_path), "analyses", "--base", str(base), "--list",
                 "--out", str(base / "INDEX.json")]) == 2


def test_tc061_register_requires_scope_and_summary(tmp_path: Path, capsys) -> None:
    """TC-061: --register ohne --scope/--summary ist ein Bedienfehler."""
    base = _ablage(tmp_path)
    assert main(["--root", str(tmp_path), "analyses", "--base", str(base), "--register",
                 str(base / "2026-11-03" / "BERICHT.md")]) == 2


def test_tc063_registers_on_real_snapshot(tmp_path: Path, capsys) -> None:
    """TC-063: registers läuft auf einem echten scan-Snapshot und meldet Drift."""
    root = tmp_path / "ws"
    make_repo(root / "alpha", commits=1)
    make_repo(root / "beta", commits=1)
    snapshot = tmp_path / "scan.json"
    assert main(["--root", str(root), "scan", "--json", str(snapshot)]) == 0
    capsys.readouterr()

    manifest = tmp_path / "projects.yaml"
    manifest.write_text("projects:\n  - name: alpha\n    category: tool\n    status: active\n", encoding="utf-8")
    auftraege = tmp_path / "auftraege.jsonl"
    auftraege.write_text('{"repo": "unbekannt"}\nkaputt\n', encoding="utf-8")

    code = main(["--root", str(root), "--manifest", str(manifest), "registers", "--snapshot", str(snapshot),
                 "--auftraege", str(auftraege), "--format", "json"])
    assert code == 0
    drift = json.loads(capsys.readouterr().out)
    assert drift["missing_in_manifest"] == ["beta"]
    assert drift["auftraege_unknown_repos"] == ["unbekannt"]
    assert drift["counts"]["auftraege_lines"] == 2

    code = main(["--root", str(root), "--manifest", str(manifest), "registers", "--snapshot", str(snapshot),
                 "--auftraege", str(auftraege), "--fail-on-drift"])
    assert code == 1


def test_tc063_registers_missing_snapshot_is_usage_error(tmp_path: Path, capsys) -> None:
    """TC-063: fehlender Snapshot nennt den Weg zu scan --json und gibt Exit 2."""
    assert main(["--root", str(tmp_path), "registers", "--snapshot", str(tmp_path / "fehlt.json")]) == 2
    assert "scan --json" in capsys.readouterr().err
