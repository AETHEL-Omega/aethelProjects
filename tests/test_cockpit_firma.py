"""TC-069 — Firma, Rat, Inkubator-Tore (REQ-028)."""

import json
from pathlib import Path

import pytest

from aethel_projects import analyses, cockpit


def write(path, schema, key, rows):
    path.write_text(json.dumps({"schema": schema, key: rows}), encoding="utf-8")


def test_register_laden_und_validieren(tmp_path):
    rat = {"id": "r1", "sicht": "bwl", "ebene": "E3", "luecke": "L", "rat": "R", "konsument": "company", "quelle": "a", "status": "offen"}
    path = tmp_path / "rat.json"
    write(path, analyses.SCHEMA_RAT, "raete", [rat])
    assert analyses.load_rat(tmp_path)[0].id == "r1"
    write(path, analyses.SCHEMA_RAT, "raete", [rat, rat])
    with pytest.raises(ValueError):
        analyses.load_rat(tmp_path)
    write(path, analyses.SCHEMA_RAT, "raete", [dict(rat, sicht="falsch")])
    with pytest.raises(ValueError):
        analyses.load_rat(tmp_path)
    fall = {"produkt": "p", "klasse": "produkt", "nutzerproblem": None, "zielgruppe": None, "kanal": None, "preis_oder_nutzen": None, "kosten_monat": None, "risiko": "unbekannt", "abhaengigkeiten": [], "entscheidung": "offen", "entschieden_am": None, "beleg": None}
    path = tmp_path / "geschaeftsfaelle.json"
    write(path, analyses.SCHEMA_GESCHAEFTSFAELLE, "geschaeftsfaelle", [fall])
    assert analyses.load_geschaeftsfaelle(tmp_path)[0].produkt == "p"
    for rows in ([fall, fall], [dict(fall, fremd=1)], [dict(fall, risiko="falsch")], [dict(fall, entschieden_am="2026-02-30")]):
        write(path, analyses.SCHEMA_GESCHAEFTSFAELLE, "geschaeftsfaelle", rows)
        with pytest.raises(ValueError):
            analyses.load_geschaeftsfaelle(tmp_path)


def test_leitstand_mit_und_ohne_inkubator(tmp_path):
    rat = {"id": "r1", "sicht": "bwl", "ebene": "E3", "luecke": "L", "rat": "R", "konsument": "company", "quelle": "a", "status": "offen"}
    write(tmp_path / "rat.json", analyses.SCHEMA_RAT, "raete", [rat])
    view = cockpit.build(tmp_path)
    assert view.rat["matrix"]["bwl"]["E3"] == 1
    assert not view.inkubator_tore["naechste_tore"]
    assert "Rat ohne Rückkopplung" in view.fehlt
    directory = tmp_path / "2026-11-04"
    directory.mkdir()
    item = {"repo": "unbekannt", "klasse": "produkt", "stufe": "R3", "rang": 4, "naechste_stufe": "R4", "naechste_luecken": ["Test fehlt"], "stages": [{"code": "R3", "erreicht": True}]}
    write(directory / "inc.json", cockpit.RUN_SCHEMAS["incubator"], "repos", [item])
    view = cockpit.build(tmp_path)
    assert view.firma["ohne_geschaeftsfall"] == ["unbekannt"]
    assert view.inkubator_tore["naechste_tore"][0]["luecke"] == "Test fehlt"
    assert view.inkubator_tore["verteilung"]["produkt"] == {"R3": 1}
    html = cockpit.render_html(view)
    assert all(title in html for title in ("Firma (aethelCompany)", "Rat (aethelConsultant)", "Inkubator-Tore"))
    assert view.as_dict()["schema"] == "aethel.projects.cockpit/v2"


def test_echte_register():
    base = Path(__file__).resolve().parents[1] / "analysen"
    assert len(analyses.load_rat(base)) == 24
    assert len(analyses.load_geschaeftsfaelle(base)) == 12
