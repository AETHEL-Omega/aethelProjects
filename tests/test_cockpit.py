"""TC-065 — Leitstand (REQ-024)."""

from __future__ import annotations

import json
from pathlib import Path

from aethel_projects import analyses, cockpit


def _ablage(tmp_path: Path) -> Path:
    base = tmp_path / "analysen"
    (base / "2026-11-03").mkdir(parents=True)
    (base / "2026-11-03" / "A.md").write_text("# Analyse A\n\nText.\n", encoding="utf-8")
    analyses.register(base, base / "2026-11-03" / "A.md", scope="firma", summary="Eine Analyse.")
    (base / "vorschlaege.json").write_text(json.dumps({
        "schema": analyses.SCHEMA_PROPOSALS,
        "projects": [
            {"id": "B1", "name": "aethelRegistry", "zweck": "Produkt-ID", "komponente": "aethelRegistry",
             "vertrag": "aethel.registry/v1", "ebene": "E4", "stufe": 1, "status": "vorgeschlagen", "hebt": ["B2"]},
            {"id": "B2", "name": "aethelRelease", "zweck": "Releases", "komponente": "aethelRelease",
             "vertrag": "aethel.release/v1", "ebene": "E4", "stufe": 1, "status": "existiert"},
        ],
    }), encoding="utf-8")
    (base / "kreislaeufe.json").write_text(json.dumps({
        "schema": analyses.SCHEMA_LOOPS,
        "loops": [
            {"id": "K-E2-gate", "name": "Gate", "ebene": "E2", "status": "teilweise"},
            {"id": "K-E4-paritaet", "name": "Parität", "ebene": "E4", "status": "offen", "fehlt": ["Release-Pipeline"]},
        ],
    }), encoding="utf-8")
    return base


def test_tc065_leitstand_ohne_laeufe_nennt_was_fehlt(tmp_path: Path) -> None:
    """TC-065: Ohne abgelegte Läufe sagt der Leitstand, welche Läufe fehlen."""
    base = _ablage(tmp_path)
    view = cockpit.build(base)
    assert view.kreise == {"teilweise": 1, "offen": 1}
    assert view.kreise_offen == ("K-E4-paritaet (E4): fehlt Release-Pipeline",)
    assert view.vorschlaege == {"vorgeschlagen": 1, "existiert": 1}
    assert view.dominosteine[0].startswith("B1 aethelRegistry: hebt 1")
    assert any("Register-Abgleich" in f for f in view.fehlt)
    assert any("Kein Kreislauf ist geschlossen" in f for f in view.fehlt)
    assert view.register_drift == {} and view.leere_schichten == ()
    md = cockpit.render_markdown(view)
    assert "# Leitstand" in md and "Was fehlt" in md and "Analyse A" in md


def test_tc065_leitstand_liest_juengste_laeufe(tmp_path: Path) -> None:
    """TC-065: Register-, Stack-, Inkubator- und Apple-first-Läufe werden aus der Ablage gelesen."""
    base = _ablage(tmp_path)
    tag = base / "2026-11-03"
    (tag / "register-abgleich.json").write_text(json.dumps({
        "schema": "aethel.projects.register-drift/v1", "missing_in_manifest": ["a", "b"], "dead_manifest_entries": [],
        "unregistered_worktrees": ["w"], "profiles_without_manifest": [], "profiles_without_repo": [],
        "auftraege_unknown_repos": [], "manifest_age_days": 66, "counts": {},
    }), encoding="utf-8")
    (tag / "schichtenkarte.json").write_text(json.dumps({
        "schema": "aethel.projects.stack/v1", "layer_names": {"S1": "Firmware", "S16": "Distribution"},
        "per_layer": {}, "empty_layers": ["S1", "S16"], "assignments": [],
    }), encoding="utf-8")
    (tag / "inkubator.json").write_text(json.dumps({
        "schema": "aethel.projects.incubator/v1",
        "items": [{"repo": "x", "stufe": "R2"}, {"repo": "y", "stufe": "R2"}, {"repo": "z", "stufe": "R5"}],
    }), encoding="utf-8")
    (tag / "applefirst.json").write_text(json.dumps({
        "schema": "aethel.projects.applefirst/v1",
        "items": [{"repo": "x", "score": 20, "grade": "fremdgeführt", "python_anteil": 0.9},
                  {"repo": "y", "score": 85, "grade": "Apple-first", "python_anteil": 0.0},
                  {"repo": "z", "score": None, "grade": "ohne Code", "python_anteil": 0.0}],
    }), encoding="utf-8")

    view = cockpit.build(base)
    assert view.register_drift["missing_in_manifest"] == 2
    assert view.register_drift["manifest_age_days"] == 66
    assert view.leere_schichten == ("S1 Firmware", "S16 Distribution")
    assert view.inkubator == {"R2": 2, "R5": 1}
    assert view.applefirst == {"Apple-first": 1, "fremdgeführt": 1, "ohne Code": 1}
    assert view.applefirst_schlechteste[0].startswith("x: 20 (fremdgeführt, Python 90 %)")
    assert any("Manifest ist 66 Tage alt" in f for f in view.fehlt)
    assert not any("Register-Abgleich" in f for f in view.fehlt)

    payload = json.loads(cockpit.render_json(view))
    assert payload["schema"] == "aethel.projects.cockpit/v2"
    assert payload["quellen"]["registers"] == "2026-11-03/register-abgleich.json"
    page = cockpit.render_html(view)
    assert page.startswith("<!doctype html>") and "AETHEL Leitstand" in page and "S16 Distribution" in page


def test_tc065_leitstand_ignoriert_kaputte_und_fremde_json(tmp_path: Path) -> None:
    """TC-065: Ungültiges JSON und fremde Schemata stören den Leitstand nicht."""
    base = _ablage(tmp_path)
    (base / "2026-11-03" / "kaputt.json").write_text("{", encoding="utf-8")
    (base / "2026-11-03" / "fremd.json").write_text(json.dumps({"schema": "x/v9", "items": []}), encoding="utf-8")
    view = cockpit.build(base)
    assert view.quellen == {}


def test_tc065_juengster_datumsordner_gewinnt_und_archiv_zaehlt_nicht(tmp_path: Path) -> None:
    """TC-065: Nur <Datum>/-Ordner zählen; das jüngste Datum gewinnt."""
    base = _ablage(tmp_path)
    for ordner, leer in (("2026-11-02", ["S1"]), ("2026-11-04", ["S16"])):
        (base / ordner).mkdir(exist_ok=True)
        (base / ordner / "stack.json").write_text(json.dumps({
            "schema": "aethel.projects.stack/v1", "layer_names": {}, "per_layer": {}, "empty_layers": leer, "assignments": []}), encoding="utf-8")
    (base / "archiv" / "2025-01-01").mkdir(parents=True)
    (base / "archiv" / "zzz.json").write_text(json.dumps({
        "schema": "aethel.projects.stack/v1", "layer_names": {}, "per_layer": {}, "empty_layers": ["S0"], "assignments": []}), encoding="utf-8")
    view = cockpit.build(base)
    assert view.leere_schichten == ("S16",)
    assert view.quellen["stack"] == "2026-11-04/stack.json"
