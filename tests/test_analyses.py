"""Versionierte Analysenablage (analysen/): Register lesen, registrieren, anzeigen, rendern.

Alle Tests arbeiten in ``tmp_path``; die echte Ablage im Repo wird nicht angefasst.
"""

from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path

import pytest

from aethel_projects import analyses
from aethel_projects.analyses import (
    CHANGED_WARNING,
    AnalysesIndex,
    AnalysisEntry,
    Loop,
    Proposal,
)


@pytest.fixture
def base(tmp_path: Path) -> Path:
    """Ein leerer analysen/-Ordner."""
    folder = tmp_path / "analysen"
    folder.mkdir()
    return folder


def write_json(folder: Path, name: str, data: object) -> None:
    (folder / name).write_text(json.dumps(data), encoding="utf-8")


def make_note(base: Path, day: str, name: str, content: str) -> Path:
    folder = base / day
    folder.mkdir(parents=True, exist_ok=True)
    file = folder / name
    file.write_text(content, encoding="utf-8")
    return file


def sample_proposal(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "id": "B1",
        "name": "aethelRegistry",
        "zweck": "Register aller Komponenten",
        "komponente": "aethelRegistry",
        "vertrag": "aethel.registry/v1",
        "ebene": "E4",
        "stufe": 1,
        "hebt": [],
        "bestand": "teilweise in aethelLanding",
        "status": "vorgeschlagen",
        "quelle": "landeweg-analyse",
    }
    data.update(overrides)
    return data


def sample_loop(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "id": "K-E2-landung",
        "name": "Landekreis",
        "ebene": "E2",
        "takt": "pro PR",
        "sollwert": "main grün",
        "sensor": "Gate-Receipt",
        "vergleicher": "aix-merge-gated",
        "stellglied": "Merge",
        "stoergroessen": ["Gate-Stau"],
        "besitzer": "aethelLanding",
        "status": "teilweise",
        "fehlt": ["Rückmeldung bei Rot"],
    }
    data.update(overrides)
    return data


# --- Index ---------------------------------------------------------------


def test_default_base_liegt_an_der_repo_wurzel() -> None:
    expected = Path(analyses.__file__).resolve().parents[2] / "analysen"
    assert analyses.default_base() == expected
    assert analyses.default_base().name == "analysen"


def test_index_ohne_datei_ist_leer(base: Path) -> None:
    index = analyses.load_index(base)
    assert index == AnalysesIndex()
    assert index.entries == ()
    assert analyses.list_entries(base) == ()


@pytest.mark.parametrize(
    "document, fragment",
    [
        ({"schema": "falsch/v9", "entries": []}, "falsches Schema"),
        ({"entries": []}, "falsches Schema"),
        ({"schema": analyses.SCHEMA_INDEX}, "Liste"),
        ({"schema": analyses.SCHEMA_INDEX, "entries": [], "extra": 1}, "unbekannte Felder"),
        ([], "JSON-Objekt"),
    ],
)
def test_index_mit_ungueltigem_schema_wirft_value_error(
    base: Path, document: object, fragment: str
) -> None:
    write_json(base, "INDEX.json", document)
    with pytest.raises(ValueError, match=fragment):
        analyses.load_index(base)


def test_index_mit_kaputtem_json_wirft_value_error(base: Path) -> None:
    (base / "INDEX.json").write_text("{nicht json", encoding="utf-8")
    with pytest.raises(ValueError, match="kein gültiges JSON"):
        analyses.load_index(base)


def entry_dict(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "id": "foo",
        "date": "2026-11-03",
        "title": "Foo",
        "path": "2026-11-03/FOO.md",
        "sha256": "a" * 64,
        "scope": "workspace",
        "summary": "Ein Satz.",
        "tags": [],
    }
    data.update(overrides)
    return data


@pytest.mark.parametrize(
    "overrides, fragment",
    [
        ({"date": "03.11.2026"}, "YYYY-MM-DD"),
        ({"date": "2026-13-45"}, "existiert nicht"),
        ({"sha256": "xyz"}, "sha256"),
        ({"scope": "irgendwas"}, "scope"),
        ({"id": "Nicht Kebab"}, "kebab-case"),
        ({"path": "../draussen.md"}, "relativ"),
        ({"path": "/etc/passwd"}, "relativ"),
        ({"title": ""}, "title"),
    ],
)
def test_index_eintrag_wird_streng_validiert(
    base: Path, overrides: dict[str, object], fragment: str
) -> None:
    write_json(base, "INDEX.json", {"schema": analyses.SCHEMA_INDEX, "entries": [entry_dict(**overrides)]})
    with pytest.raises(ValueError, match=fragment):
        analyses.load_index(base)


def test_index_unbekanntes_feld_und_doppelte_id_werden_abgelehnt(base: Path) -> None:
    write_json(
        base,
        "INDEX.json",
        {"schema": analyses.SCHEMA_INDEX, "entries": [entry_dict(notiz="x")]},
    )
    with pytest.raises(ValueError, match="unbekannte Felder"):
        analyses.load_index(base)
    write_json(
        base,
        "INDEX.json",
        {"schema": analyses.SCHEMA_INDEX, "entries": [entry_dict(), entry_dict()]},
    )
    with pytest.raises(ValueError, match="doppelte"):
        analyses.load_index(base)


# --- register --------------------------------------------------------------


def test_register_erzeugt_eintrag_mit_titel_sha_und_datum_aus_ordnername(base: Path) -> None:
    content = "Vorspann\n\n# Landeweg-Analyse\n\nText mit Umlauten: äöü.\n"
    file = make_note(base, "2026-11-03", "LANDE_WEG.md", content)

    entry = analyses.register(
        base, file, scope="stack", summary="Wo der Landeweg bricht.", tags=("landung", "gate")
    )

    assert entry == AnalysisEntry(
        id="lande-weg",
        date="2026-11-03",
        title="Landeweg-Analyse",
        path="2026-11-03/LANDE_WEG.md",
        sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
        scope="stack",
        summary="Wo der Landeweg bricht.",
        tags=("landung", "gate"),
    )
    assert analyses.load_index(base).entries == (entry,)


def test_register_schreibt_deterministisches_index_json(base: Path) -> None:
    file = make_note(base, "2026-11-03", "Über Größe.md", "# Über Größe\n")
    analyses.register(base, file, scope="firma", summary="Umlaute ÄÖÜ bleiben lesbar.")
    first = (base / "INDEX.json").read_bytes()

    analyses.register(base, file, scope="firma", summary="Umlaute ÄÖÜ bleiben lesbar.")
    assert (base / "INDEX.json").read_bytes() == first

    text = first.decode("utf-8")
    assert text.endswith("}\n") and not text.endswith("\n\n")
    assert "Über Größe" in text and "\\u" not in text  # ensure_ascii=False
    assert text == json.dumps(json.loads(text), sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def test_register_schreibt_nur_index_json(base: Path) -> None:
    file = make_note(base, "2026-11-03", "FOO.md", "# Foo\n")
    before = sorted(p.relative_to(base).as_posix() for p in base.rglob("*"))

    analyses.register(base, file, scope="workspace", summary="Foo.")

    after = sorted(p.relative_to(base).as_posix() for p in base.rglob("*"))
    assert after == sorted(before + ["INDEX.json"])  # auch keine Temp-Datei bleibt liegen
    assert file.read_text(encoding="utf-8") == "# Foo\n"


def test_register_ausserhalb_von_base_wirft_value_error(base: Path, tmp_path: Path) -> None:
    outside = tmp_path / "fremd.md"
    outside.write_text("# Fremd\n", encoding="utf-8")
    with pytest.raises(ValueError, match="außerhalb"):
        analyses.register(base, outside, scope="workspace", summary="Nein.")
    assert not (base / "INDEX.json").exists()


def test_register_erkennt_pfadflucht_per_punkt_punkt_und_symlink(base: Path, tmp_path: Path) -> None:
    outside = tmp_path / "fremd.md"
    outside.write_text("# Fremd\n", encoding="utf-8")
    sneaky = base / "2026-11-03" / ".." / ".." / "fremd.md"
    (base / "2026-11-03").mkdir()
    with pytest.raises(ValueError, match="außerhalb"):
        analyses.register(base, sneaky, scope="workspace", summary="Nein.")

    link = base / "2026-11-03" / "LINK.md"
    link.symlink_to(outside)
    with pytest.raises(ValueError, match="außerhalb"):
        analyses.register(base, link, scope="workspace", summary="Nein.")


def test_register_ohne_ueberschrift_nutzt_dateinamen_und_ignoriert_codebloecke(base: Path) -> None:
    plain = make_note(base, "2026-11-03", "ohne-titel.md", "Nur Text.\n## Unterabschnitt\n")
    assert analyses.register(base, plain, scope="workspace", summary="A.").title == "ohne-titel.md"

    fenced = make_note(
        base, "2026-11-03", "fenced.md", "```bash\n# Kommentar, kein Titel\n```\n\n# Echter Titel\n"
    )
    assert analyses.register(base, fenced, scope="workspace", summary="B.").title == "Echter Titel"


def test_register_datum_faellt_ohne_datumsordner_auf_heute_zurueck(
    base: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(analyses, "_today", lambda: "2030-01-02")
    loose = base / "lose.md"
    loose.write_text("# Lose\n", encoding="utf-8")
    assert analyses.register(base, loose, scope="workspace", summary="C.").date == "2030-01-02"

    named = make_note(base, "kein-datum", "x.md", "# X\n")
    assert analyses.register(base, named, scope="workspace", summary="D.").date == "2030-01-02"

    today = datetime.date.today().isoformat()
    monkeypatch.undo()
    assert analyses.register(base, loose, scope="workspace", summary="C.").date == today


def test_register_explizite_id_datum_und_relativer_pfad(base: Path) -> None:
    make_note(base, "2026-11-03", "FOO.md", "# Foo\n")
    entry = analyses.register(
        base,
        "2026-11-03/FOO.md",  # relativ zu base
        scope="fabrik",
        summary="  Mehrzeilig\n  zusammengefasst.  ",
        entry_id="mein-id",
        date=datetime.date(2026, 10, 1),
        tags=["a", " a ", "", "b"],
    )
    assert entry.id == "mein-id"
    assert entry.date == "2026-10-01"
    assert entry.summary == "Mehrzeilig zusammengefasst."
    assert entry.tags == ("a", "b")


@pytest.mark.parametrize(
    "kwargs, fragment",
    [
        ({"scope": "mond", "summary": "x"}, "Scope"),
        ({"scope": "stack", "summary": "   "}, "Zusammenfassung"),
        ({"scope": "stack", "summary": "x", "entry_id": "Nicht Kebab"}, "kebab-case"),
        ({"scope": "stack", "summary": "x", "date": "03.11.2026"}, "YYYY-MM-DD"),
    ],
)
def test_register_lehnt_ungueltige_eingaben_ab(base: Path, kwargs: dict[str, object], fragment: str) -> None:
    file = make_note(base, "2026-11-03", "FOO.md", "# Foo\n")
    with pytest.raises(ValueError, match=fragment):
        analyses.register(base, file, **kwargs)  # type: ignore[arg-type]
    assert not (base / "INDEX.json").exists()


def test_register_nimmt_nur_vorhandene_markdown_dateien(base: Path) -> None:
    text = make_note(base, "2026-11-03", "notiz.txt", "# nicht Markdown\n")
    with pytest.raises(ValueError, match="Markdown"):
        analyses.register(base, text, scope="workspace", summary="x")
    with pytest.raises(FileNotFoundError):
        analyses.register(base, base / "2026-11-03" / "fehlt.md", scope="workspace", summary="x")


def test_register_ersetzt_eintrag_mit_gleicher_id(base: Path) -> None:
    file = make_note(base, "2026-11-03", "FOO.md", "# Alt\n")
    analyses.register(base, file, scope="workspace", summary="Alt.")
    file.write_text("# Neu\n", encoding="utf-8")

    analyses.register(base, file, scope="firma", summary="Neu.")

    entries = analyses.load_index(base).entries
    assert len(entries) == 1
    assert (entries[0].title, entries[0].scope, entries[0].summary) == ("Neu", "firma", "Neu.")
    assert entries[0].sha256 == hashlib.sha256(b"# Neu\n").hexdigest()


def test_register_bricht_bei_defektem_index_ab_und_laesst_ihn_unveraendert(base: Path) -> None:
    (base / "INDEX.json").write_text('{"schema": "falsch"}', encoding="utf-8")
    file = make_note(base, "2026-11-03", "FOO.md", "# Foo\n")
    with pytest.raises(ValueError, match="falsches Schema"):
        analyses.register(base, file, scope="workspace", summary="x")
    assert (base / "INDEX.json").read_text(encoding="utf-8") == '{"schema": "falsch"}'


def test_kebab_case_schreibt_umlaute_um() -> None:
    assert analyses.kebab_case("Projekt_Übersicht v2") == "projekt-uebersicht-v2"
    assert analyses.kebab_case("__Straße__") == "strasse"
    assert analyses.kebab_case("café") == "cafe"
    assert analyses.kebab_case("!!!") == ""


# --- list_entries / show -----------------------------------------------------


def test_list_entries_sortiert_nach_datum_absteigend_dann_id(base: Path) -> None:
    write_json(
        base,
        "INDEX.json",
        {
            "schema": analyses.SCHEMA_INDEX,
            "entries": [
                entry_dict(id="b", date="2026-11-01"),
                entry_dict(id="z", date="2026-11-03"),
                entry_dict(id="a", date="2026-11-03"),
                entry_dict(id="c", date="2026-10-01"),
            ],
        },
    )
    assert [e.id for e in analyses.list_entries(base)] == ["a", "z", "b", "c"]


def test_show_mit_passender_pruefsumme_liefert_inhalt_ohne_warnung(base: Path) -> None:
    content = "# Foo\n\nInhalt.\n"
    file = make_note(base, "2026-11-03", "FOO.md", content)
    analyses.register(base, file, scope="workspace", summary="Foo.")
    assert analyses.show(base, "foo") == content


def test_show_mit_veraenderter_datei_stellt_warnzeile_voran(base: Path) -> None:
    file = make_note(base, "2026-11-03", "FOO.md", "# Foo\n")
    analyses.register(base, file, scope="workspace", summary="Foo.")
    file.write_text("# Foo\n\nNachträglich geändert.\n", encoding="utf-8")

    shown = analyses.show(base, "foo")

    assert CHANGED_WARNING == "> Warnung: Datei verändert seit Registrierung"
    assert shown.startswith(CHANGED_WARNING + "\n")
    assert shown.endswith("Nachträglich geändert.\n")


def test_show_unbekannte_id_wirft_key_error(base: Path) -> None:
    with pytest.raises(KeyError):
        analyses.show(base, "gibt-es-nicht")


def test_show_lehnt_indexpfad_ausserhalb_von_base_ab(base: Path, tmp_path: Path) -> None:
    secret = tmp_path / "geheim.md"
    secret.write_text("# Geheim\n", encoding="utf-8")
    (base / "2026-11-03").mkdir()
    (base / "2026-11-03" / "LINK.md").symlink_to(secret)
    write_json(
        base,
        "INDEX.json",
        {"schema": analyses.SCHEMA_INDEX, "entries": [entry_dict(path="2026-11-03/LINK.md")]},
    )
    with pytest.raises(ValueError, match="außerhalb"):
        analyses.show(base, "foo")


def test_show_meldet_fehlende_datei(base: Path) -> None:
    write_json(base, "INDEX.json", {"schema": analyses.SCHEMA_INDEX, "entries": [entry_dict()]})
    with pytest.raises(FileNotFoundError):
        analyses.show(base, "foo")


# --- Vorschläge und Kreisläufe -----------------------------------------------


def test_load_proposals_ohne_datei_ist_leer(base: Path) -> None:
    assert analyses.load_proposals(base) == ()


def test_load_proposals_liest_gueltige_datei(base: Path) -> None:
    write_json(
        base,
        "vorschlaege.json",
        {"schema": analyses.SCHEMA_PROPOSALS,
         "projects": [sample_proposal(hebt=["B2", "B3"]), sample_proposal(id="B2"), sample_proposal(id="B3")]},
    )
    proposal = analyses.load_proposals(base)[0]
    assert proposal == Proposal(
        id="B1",
        name="aethelRegistry",
        zweck="Register aller Komponenten",
        komponente="aethelRegistry",
        vertrag="aethel.registry/v1",
        ebene="E4",
        stufe=1,
        status="vorgeschlagen",
        hebt=("B2", "B3"),
        bestand="teilweise in aethelLanding",
        quelle="landeweg-analyse",
    )
    assert proposal.as_dict()["hebt"] == ["B2", "B3"]


@pytest.mark.parametrize(
    "document, fragment",
    [
        ({"schema": "aethel.projects.vorschlaege/v2", "projects": []}, "falsches Schema"),
        ({"schema": analyses.SCHEMA_PROPOSALS, "loops": []}, "unbekannte Felder"),
        ({"schema": analyses.SCHEMA_PROPOSALS, "projects": [sample_proposal(status="fertig")]}, "status"),
        ({"schema": analyses.SCHEMA_PROPOSALS, "projects": [sample_proposal(stufe="1")]}, "stufe"),
        ({"schema": analyses.SCHEMA_PROPOSALS, "projects": [sample_proposal(stufe=True)]}, "stufe"),
        ({"schema": analyses.SCHEMA_PROPOSALS, "projects": [sample_proposal(hebt="B2")]}, "hebt"),
        ({"schema": analyses.SCHEMA_PROPOSALS, "projects": [sample_proposal(extra=1)]}, "unbekannte Felder"),
        ({"schema": analyses.SCHEMA_PROPOSALS, "projects": [{"id": "B1"}]}, "Pflichtfelder"),
        (
            {"schema": analyses.SCHEMA_PROPOSALS, "projects": [sample_proposal(), sample_proposal()]},
            "doppelte",
        ),
    ],
)
def test_load_proposals_lehnt_ungueltiges_ab(base: Path, document: object, fragment: str) -> None:
    write_json(base, "vorschlaege.json", document)
    with pytest.raises(ValueError, match=fragment):
        analyses.load_proposals(base)


def test_load_loops_ohne_datei_ist_leer(base: Path) -> None:
    assert analyses.load_loops(base) == ()


def test_load_loops_liest_gueltige_datei_und_optionale_felder(base: Path) -> None:
    write_json(
        base,
        "kreislaeufe.json",
        {
            "schema": analyses.SCHEMA_LOOPS,
            "loops": [
                sample_loop(),
                {"id": "K-META", "name": "Meta", "ebene": "META", "status": "offen"},
            ],
        },
    )
    full, minimal = analyses.load_loops(base)
    assert isinstance(full, Loop)
    assert full.stoergroessen == ("Gate-Stau",) and full.fehlt == ("Rückmeldung bei Rot",)
    assert full.as_dict()["stoergroessen"] == ["Gate-Stau"]
    assert minimal.sensor == "" and minimal.fehlt == ()


@pytest.mark.parametrize(
    "document, fragment",
    [
        ({"schema": analyses.SCHEMA_PROPOSALS, "loops": []}, "falsches Schema"),
        ({"schema": analyses.SCHEMA_LOOPS, "loops": [sample_loop(ebene="E9")]}, "ebene"),
        ({"schema": analyses.SCHEMA_LOOPS, "loops": [sample_loop(status="kaputt")]}, "status"),
        ({"schema": analyses.SCHEMA_LOOPS, "loops": [sample_loop(fehlt="x")]}, "fehlt"),
        ({"schema": analyses.SCHEMA_LOOPS, "loops": [sample_loop(), sample_loop()]}, "doppelte"),
        ({"schema": analyses.SCHEMA_LOOPS, "loops": ["K1"]}, "Objekt erwartet"),
    ],
)
def test_load_loops_lehnt_ungueltiges_ab(base: Path, document: object, fragment: str) -> None:
    write_json(base, "kreislaeufe.json", document)
    with pytest.raises(ValueError, match=fragment):
        analyses.load_loops(base)


# --- Darstellung -------------------------------------------------------------


def make_entries() -> tuple[AnalysisEntry, ...]:
    return (
        AnalysisEntry("foo", "2026-11-03", "Foo-Titel", "2026-11-03/FOO.md", "a" * 64, "stack",
                      "Foo | Bar\nzweite Zeile."),
        AnalysisEntry("bar", "2026-10-01", "Bar-Titel", "2026-10-01/BAR.md", "b" * 64, "firma", "Bar."),
    )


def test_render_index_markdown_hat_kopfzeile_und_werte() -> None:
    lines = analyses.render_index_markdown(make_entries()).splitlines()
    assert lines[0] == "| Datum | ID | Titel | Scope | Zusammenfassung |"
    assert lines[1] == "| --- | --- | --- | --- | --- |"
    assert lines[2] == "| 2026-11-03 | foo | Foo-Titel | stack | Foo \\| Bar zweite Zeile. |"
    assert lines[3] == "| 2026-10-01 | bar | Bar-Titel | firma | Bar. |"
    assert len(lines) == 4


def test_render_proposals_markdown_hat_kopfzeile_und_werte() -> None:
    proposal = Proposal(
        id="B1", name="aethelRegistry", zweck="Register", komponente="aethelRegistry",
        vertrag="aethel.registry/v1", ebene="E4", stufe=1, status="in-arbeit", hebt=("B2", "B3"),
    )
    lines = analyses.render_proposals_markdown([proposal]).splitlines()
    assert lines[0] == "| ID | Name | Zweck | Komponente@Vertrag | Ebene | Stufe | hebt | Status |"
    assert lines[2] == (
        "| B1 | aethelRegistry | Register | aethelRegistry@aethel.registry/v1 | E4 | 1 | B2, B3 | in-arbeit |"
    )


def test_render_loops_markdown_hat_kopfzeile_und_werte() -> None:
    loop = Loop(
        id="K-E2-landung", name="Landekreis", ebene="E2", status="teilweise", takt="pro PR",
        sollwert="main grün", sensor="Receipt", vergleicher="Gate", stellglied="Merge",
        fehlt=("Rückmeldung", "Alarm"),
    )
    lines = analyses.render_loops_markdown([loop]).splitlines()
    assert lines[0] == (
        "| ID | Ebene | Takt | Sollwert | Sensor | Vergleicher | Stellglied | Status | fehlt |"
    )
    assert lines[2] == (
        "| K-E2-landung | E2 | pro PR | main grün | Receipt | Gate | Merge | teilweise | Rückmeldung; Alarm |"
    )
    empty = analyses.render_loops_markdown([Loop(id="K", name="K", ebene="E0", status="offen")])
    assert empty.splitlines()[2] == "| K | E0 | - | - | - | - | - | offen | - |"


def test_render_markdown_ohne_daten_liefert_nur_die_kopfzeile() -> None:
    assert len(analyses.render_index_markdown(()).splitlines()) == 2
    assert len(analyses.render_proposals_markdown(()).splitlines()) == 2
    assert len(analyses.render_loops_markdown(()).splitlines()) == 2


def test_render_json_hat_dieselbe_form_wie_die_dateien(base: Path) -> None:
    entries = make_entries()
    rendered = analyses.render_index_json(entries)
    assert rendered["schema"] == analyses.SCHEMA_INDEX
    assert rendered["entries"][0]["tags"] == [] and rendered["entries"][0]["id"] == "foo"
    assert AnalysesIndex(entries=entries).as_dict() == rendered
    json.dumps(rendered)  # serialisierbar

    write_json(base, "vorschlaege.json", {"schema": analyses.SCHEMA_PROPOSALS, "projects": [sample_proposal()]})
    write_json(base, "kreislaeufe.json", {"schema": analyses.SCHEMA_LOOPS, "loops": [sample_loop()]})
    proposals = analyses.render_proposals_json(analyses.load_proposals(base))
    loops = analyses.render_loops_json(analyses.load_loops(base))
    assert proposals == {"schema": analyses.SCHEMA_PROPOSALS, "projects": [sample_proposal()]}
    assert loops == {"schema": analyses.SCHEMA_LOOPS, "loops": [sample_loop()]}


# --- summary -----------------------------------------------------------------


def test_summary_einer_leeren_ablage_ist_null(base: Path) -> None:
    assert analyses.summary(base) == {
        "analyses": 0,
        "proposals": 0,
        "loops_total": 0,
        "loops_offen": 0,
        "loops_teilweise": 0,
        "loops_geschlossen": 0,
    }


def test_summary_zaehlt_alle_register(base: Path) -> None:
    file = make_note(base, "2026-11-03", "FOO.md", "# Foo\n")
    analyses.register(base, file, scope="workspace", summary="Foo.")
    write_json(
        base,
        "vorschlaege.json",
        {
            "schema": analyses.SCHEMA_PROPOSALS,
            "projects": [sample_proposal(), sample_proposal(id="B2", status="existiert")],
        },
    )
    write_json(
        base,
        "kreislaeufe.json",
        {
            "schema": analyses.SCHEMA_LOOPS,
            "loops": [
                sample_loop(id="K1", status="offen"),
                sample_loop(id="K2", status="offen"),
                sample_loop(id="K3", status="teilweise"),
                sample_loop(id="K4", status="geschlossen"),
            ],
        },
    )
    assert analyses.summary(base) == {
        "analyses": 1,
        "proposals": 2,
        "loops_total": 4,
        "loops_offen": 2,
        "loops_teilweise": 1,
        "loops_geschlossen": 1,
    }


def test_load_proposals_lehnt_tote_hebt_verweise_ab(tmp_path: Path) -> None:
    """REQ-021: ``hebt`` muss auf vorhandene Vorschlags- oder Kreislauf-IDs zeigen."""
    base = tmp_path / "analysen"
    base.mkdir()
    write_json(base, "kreislaeufe.json", {"schema": analyses.SCHEMA_LOOPS, "loops": [sample_loop()]})
    write_json(base, "vorschlaege.json", {
        "schema": analyses.SCHEMA_PROPOSALS,
        "projects": [sample_proposal(hebt=["B2", "K-E2-landung"]), sample_proposal(id="B2")],
    })
    assert len(analyses.load_proposals(base)) == 2  # Vorschlag und Kreislauf sind bekannt
    write_json(base, "vorschlaege.json", {
        "schema": analyses.SCHEMA_PROPOSALS,
        "projects": [sample_proposal(hebt=["B13"])],
    })
    with pytest.raises(ValueError, match="B13"):
        analyses.load_proposals(base)
