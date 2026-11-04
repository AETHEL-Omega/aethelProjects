"""TC-067 — Inkubator-Reifeleiter — Stufen R0–R11, RF, RI mit Belegen (REQ-026).

Die Tests laufen vollständig in ``tmp_path``: kein Netz, kein echter Workspace.
"""

from __future__ import annotations

import json
import os
import re
from datetime import date
from pathlib import Path

import pytest
from conftest import git, make_repo

from aethel_projects import incubator
from aethel_projects.incubator import (
    STAGES,
    Readiness,
    assess,
    build,
    klasse_aus,
    leiter,
    render_json,
    render_markdown,
)
from aethel_projects.models import ManifestEntry, RepoReport

HEUTE = date(2026, 11, 3)


def _report(
    repo: Path,
    *,
    category: str | None = None,
    commits: int = 1,
    worktree: bool = False,
    name: str | None = None,
) -> RepoReport:
    entry = (
        ManifestEntry(name=repo.name, category=category, status="active", last_commit=None, remote=None)
        if category
        else None
    )
    return RepoReport(
        name=name or repo.name,
        path=str(repo),
        git_common_dir=str(repo / ".git"),
        is_worktree=worktree,
        worktree_paths=(),
        default_branch="main",
        current_branch="main",
        commits_total=commits,
        commits_on_main=commits,
        commits_not_on_main=0,
        branches_total=1,
        branches_unmerged=0,
        unmerged_branches=(),
        ahead_of_origin=None,
        behind_origin=None,
        dirty_files=0,
        last_commit_date=None,
        last_commit_subject=None,
        remote_url=None,
        manifest_entry=entry,
    )


def _schreibe(repo: Path, rel: str, text: str = "x\n") -> None:
    ziel = repo / rel
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(text, encoding="utf-8")


def _bewerte(repo: Path, **kwargs: object) -> Readiness:
    klasse = kwargs.pop("klasse", None)
    return assess(_report(repo, **kwargs), repo, klasse=klasse, heute=HEUTE)  # type: ignore[arg-type]


# -- Bausteine: jede Funktion erfüllt genau eine weitere Stufe ------------------


def _r1(repo: Path) -> None:
    _schreibe(repo, "README.md", "".join(f"Zeile {i}\n" for i in range(25)))


def _r2(repo: Path) -> None:
    _schreibe(repo, "src/app.py", "".join(f"wert_{i} = {i}\n" for i in range(210)))


def _r3(repo: Path) -> None:
    _schreibe(repo, "docs/SPEC.md", "# SPEC\n\n- REQ-001 a\n- REQ-002 b\n- REQ-003 c\n")
    _schreibe(repo, "docs/TEST-CASES.md", "# TC\n\n| TC-001 | REQ-001 |\n")


def _r4(repo: Path) -> None:
    for i in range(5):
        _schreibe(repo, f"tests/test_{i}.py", "def test_x():\n    assert True\n")


def _r5(repo: Path) -> None:
    _schreibe(repo, ".github/workflows/ci.yml", "jobs:\n  t:\n    steps:\n      - run: pytest -q\n")


def _r6(repo: Path) -> None:
    _schreibe(repo, "docs/ARCHITECTURE.md", "# Architektur\n")
    _schreibe(repo, "CHANGELOG.md", "# Changelog\n\n## [1.0.0] - 2026-10-20\n- erste Version\n")
    _schreibe(repo, "LICENSE", "MIT\n")


def _r7(repo: Path) -> None:
    _schreibe(repo, ".gitignore", ".env\n*.pem\n")
    _schreibe(repo, ".env", "GEHEIM=1\n")


def _r8(repo: Path) -> None:
    _schreibe(repo, "VERSION", "1.0.0\n")


def _bis(repo: Path, stufe: int) -> None:
    """Erfüllt R1 … R<stufe> (R6–R8 über die Bausteine; R9+ separat)."""
    for nummer, baustein in enumerate((_r1, _r2, _r3, _r4, _r5, _r6, _r7, _r8), start=1):
        if nummer <= stufe:
            baustein(repo)


def _apple(repo: Path) -> None:
    _schreibe(repo, "ios/Runner/Info.plist", "<plist/>\n")
    _schreibe(repo, "ios/Runner/Assets.xcassets/AppIcon.appiconset/Contents.json", "{}\n")
    _schreibe(repo, "ios/Runner/de.lproj/Localizable.strings", '"a" = "b";\n')
    _schreibe(repo, "lib/main.dart", "Semantics(label: 'x');\n")


def _vertrieb(repo: Path) -> None:
    _schreibe(repo, "ExportOptions.plist", "<plist/>\n")
    _schreibe(repo, "PRIVACY.md", "# Datenschutz\n")


# -- Leiter R0 … R8 --------------------------------------------------------------


def test_leeres_repo_ist_r0(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "leer")
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R0"
    assert ergebnis.stufe_name == "Idee"
    assert ergebnis.klasse == "produkt"
    assert ergebnis.naechste_stufe == "R1"
    assert ergebnis.naechste_luecken  # nennt, was für R1 fehlt
    assert all(isinstance(text, str) and text for text in ergebnis.naechste_luecken)


def test_ohne_commit_gibt_es_keine_stufe(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "r")
    ergebnis = assess(_report(repo, commits=0), repo, heute=HEUTE)
    assert ergebnis.stufe == "-"
    assert ergebnis.stufe_name == "Keine Stufe"
    assert ergebnis.naechste_stufe == "R0"
    assert any("Commit" in beleg for beleg in ergebnis.naechste_luecken)


def test_fehlendes_verzeichnis_ist_kein_fehler(tmp_path: Path) -> None:
    ergebnis = assess(_report(tmp_path / "gibt-es-nicht"), tmp_path / "gibt-es-nicht", heute=HEUTE)
    assert ergebnis.stufe == "-"
    assert ergebnis.naechste_stufe == "R0"


@pytest.mark.parametrize("variante", ["readme", "spec"])
def test_readme_oder_spec_ist_r1(tmp_path: Path, variante: str) -> None:
    repo = make_repo(tmp_path / "skizze")
    if variante == "readme":
        _r1(repo)
    else:
        _schreibe(repo, "docs/SPEC.md", "# SPEC\n")
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R1"
    assert ergebnis.stufe_name == "Skizze"
    signal = ergebnis.stage("R1").signale[0]  # type: ignore[union-attr]
    assert signal.erfuellt
    assert "README.md" in signal.beleg or "SPEC.md" in signal.beleg


def test_kurze_readme_ohne_spec_bleibt_r0(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "kurz")
    _schreibe(repo, "README.md", "# Titel\n\nEin Satz.\n")
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R0"
    assert any("Inhaltszeilen" in beleg for beleg in ergebnis.naechste_luecken)


def test_zweihundert_loc_sind_r2(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "proto")
    _bis(repo, 2)
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R2"
    assert ergebnis.stufe_name == "Prototyp"
    loc = ergebnis.stage("R2").signale[0].beleg  # type: ignore[union-attr]
    assert loc.startswith("210 LOC")


def test_weniger_als_zweihundert_loc_bleiben_r1(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "klein")
    _r1(repo)
    _schreibe(repo, "src/app.py", "".join(f"a{i} = 1\n" for i in range(199)))
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R1"
    assert ergebnis.naechste_stufe == "R2"
    assert any("199 LOC" in beleg for beleg in ergebnis.naechste_luecken)


def test_stub_mehrheit_verhindert_r2(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "stubs")
    _r1(repo)
    for i in range(3):
        _schreibe(
            repo,
            f"src/modul{i}.rs",
            "".join(f"fn f{i}_{j}() {{}}\n" for j in range(90)) + "fn rest() { unimplemented!() }\n",
        )
    ergebnis = _bewerte(repo)
    r2 = ergebnis.stage("R2")
    assert r2 is not None
    assert r2.signale[0].erfuellt  # genug LOC …
    assert not r2.signale[1].erfuellt  # … aber alles Stub
    assert ergebnis.stufe == "R1"
    assert any("Stub-Marker" in beleg for beleg in ergebnis.naechste_luecken)


def test_wenige_stubs_sind_erlaubt(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "fast-fertig")
    _r1(repo)
    for i in range(10):
        _schreibe(repo, f"src/m{i}.py", "".join(f"v{j} = {j}\n" for j in range(30)))
    _schreibe(repo, "src/stub.py", "def f():\n    raise NotImplementedError\n")
    assert _bewerte(repo).stufe == "R2"  # 1 von 11 Dateien ≈ 9 % ≤ 10 %


def test_spec_mit_req_und_testfaellen_ist_r3(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "spec")
    _bis(repo, 3)
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R3"
    assert ergebnis.stufe_name == "Spezifiziert"
    assert ergebnis.stage("R3").signale[2].beleg.startswith("docs/SPEC.md enthält 3 REQ")  # type: ignore[union-attr]


def test_spec_mit_zu_wenig_req_zeilen_bleibt_r2(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "duenn")
    _bis(repo, 2)
    _schreibe(repo, "docs/SPEC.md", "# SPEC\n\nREQ-001 a\nREQ-002 b\n")
    _schreibe(repo, "docs/TEST-CASES.md", "# TC\n")
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R2"
    assert any("2 REQ-/SHALL-Zeilen" in beleg for beleg in ergebnis.naechste_luecken)


def test_shall_zeilen_zaehlen_wie_req(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "shall")
    _bis(repo, 2)
    _schreibe(repo, "docs/SPEC.md", "Das System SHALL a.\nDas System SHALL b.\nDas System SHALL c.\n")
    _schreibe(repo, "docs/TEST-CASES.md", "# TC\n")
    assert _bewerte(repo).stufe == "R3"


def test_testdateien_sind_r4(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "getestet")
    _bis(repo, 4)
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R4"
    assert ergebnis.stufe_name == "Getestet"


def test_zehn_prozent_testdateien_genuegen_unter_fuenf(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "anteil")
    _bis(repo, 3)  # 1 Quelldatei
    _schreibe(repo, "tests/test_a.py", "def test_a():\n    assert True\n")
    assert _bewerte(repo).stufe == "R4"  # 1 Test ≥ 10 % von 1 Quelldatei

    viele = make_repo(tmp_path / "viele-quellen")
    _bis(viele, 3)
    for i in range(19):
        _schreibe(viele, f"src/m{i}.py", f"a{i} = 1\n")
    _schreibe(viele, "tests/test_a.py", "def test_a():\n    assert True\n")
    ergebnis = _bewerte(viele)  # 1 Test bei 20 Quelldateien = 5 %
    assert ergebnis.stufe == "R3"
    assert any("Testdateien" in beleg for beleg in ergebnis.naechste_luecken)


def test_ci_mit_pytest_ist_r5(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "ci")
    _bis(repo, 5)
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R5"
    assert ergebnis.stufe_name == "Integriert"
    assert "pytest" in ergebnis.stage("R5").signale[1].beleg  # type: ignore[union-attr]


def test_ci_ohne_testkommando_bleibt_r4(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "ci-leer")
    _bis(repo, 4)
    _schreibe(repo, ".github/workflows/ci.yml", "name: ci\njobs:\n  b:\n    steps:\n      - run: echo hallo\n")
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R4"
    assert ergebnis.naechste_stufe == "R5"
    assert any("Testkommando" in beleg for beleg in ergebnis.naechste_luecken)


@pytest.mark.parametrize(
    ("rel", "inhalt"),
    [
        ("Makefile", "test:\n\tcargo test\n"),
        (".gitlab-ci.yml", "test:\n  script:\n    - flutter test\n"),
        ("scripts/local-ci.sh", "#!/bin/sh\nswift test\n"),
    ],
)
def test_weitere_ci_formen(tmp_path: Path, rel: str, inhalt: str) -> None:
    repo = make_repo(tmp_path / "ci-form")
    _bis(repo, 4)
    _schreibe(repo, rel, inhalt)
    assert _bewerte(repo).stufe == "R5"


def test_makefile_ohne_testziel_ist_keine_ci(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "make")
    _bis(repo, 4)
    _schreibe(repo, "Makefile", "build:\n\techo pytest\n")
    assert _bewerte(repo).stufe == "R4"


def test_r6_bis_r8(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "reif")
    _bis(repo, 6)
    ergebnis = _bewerte(repo)
    # Ohne Geheimnisse und ohne Manifest ist R7 mit der Lizenz aus R6 bereits erfüllt.
    assert ergebnis.stufe == "R7"
    assert ergebnis.stage("R6").erreicht  # type: ignore[union-attr]
    assert ergebnis.naechste_stufe == "R8"
    assert any("Git-Tag" in beleg for beleg in ergebnis.naechste_luecken)
    _bis(repo, 7)  # .env liegt vor, ist aber ausgeschlossen
    assert _bewerte(repo).stufe == "R7"
    _r8(repo)
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R8"
    assert ergebnis.stufe_name == "Versioniert"
    assert "VERSION" in ergebnis.stage("R8").signale[0].beleg  # type: ignore[union-attr]


def test_fehlende_stufe_blockiert_hoehere(tmp_path: Path) -> None:
    """R6 ist erfüllt, R5 (CI) fehlt: Ergebnis R4, nächste Stufe R5 mit Lücken."""
    repo = make_repo(tmp_path / "luecke")
    _bis(repo, 4)
    _r6(repo)
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R4"
    assert ergebnis.naechste_stufe == "R5"
    assert len(ergebnis.naechste_luecken) == 2  # CI-Datei und Testkommando fehlen
    r6 = ergebnis.stage("R6")
    assert r6 is not None
    assert all(signal.erfuellt for signal in r6.signale)  # Signale sind erfüllt …
    assert not r6.erreicht  # … die Stufe zählt trotzdem nicht
    assert ergebnis.rang == 5  # R0 … R4


def test_geheimnisdatei_ohne_gitignore_verhindert_r7(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "geheim")
    _bis(repo, 6)
    _schreibe(repo, "keys/server.pem", "-----BEGIN-----\n")
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R6"
    assert any("server.pem" in beleg for beleg in ergebnis.naechste_luecken)
    _schreibe(repo, ".gitignore", "*.pem\n")  # jetzt per .gitignore ausgeschlossen
    assert _bewerte(repo).stufe == "R7"


def test_gitignore_negation_und_ordner(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "gi")
    _bis(repo, 6)
    _schreibe(repo, "secrets/id_rsa", "x\n")
    _schreibe(repo, ".gitignore", "secrets/\n")
    assert _bewerte(repo).stufe == "R7"
    _schreibe(repo, ".gitignore", "id_rsa\n!secrets/id_rsa\n")
    assert _bewerte(repo).stufe == "R6"


def test_manifest_ohne_lock_verhindert_r7(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "lock")
    _bis(repo, 6)
    _schreibe(repo, "Cargo.toml", '[package]\nname = "x"\n')
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R6"
    assert any("Cargo.lock" in beleg for beleg in ergebnis.naechste_luecken)
    _schreibe(repo, "Cargo.lock", "# lock\n")
    assert _bewerte(repo).stufe == "R7"


def test_pyproject_ohne_abhaengigkeiten_braucht_kein_lock(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "py")
    _bis(repo, 6)
    _schreibe(repo, "pyproject.toml", "[tool.pytest.ini_options]\npythonpath = ['src']\n")
    assert _bewerte(repo).stufe == "R7"
    _schreibe(repo, "pyproject.toml", '[project]\nname = "x"\ndependencies = ["requests"]\n')
    assert _bewerte(repo).stufe == "R6"
    _schreibe(repo, "uv.lock", "# lock\n")
    assert _bewerte(repo).stufe == "R7"


def test_git_tag_belegt_r8(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "tag")
    _bis(repo, 7)
    assert _bewerte(repo).stufe == "R7"
    git(repo, "tag", "v1.0.0")
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R8"
    assert ergebnis.stage("R8").signale[0].beleg == "Git-Tag vorhanden"  # type: ignore[union-attr]


def test_version_in_manifest_belegt_r8(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "pubspec")
    _bis(repo, 7)
    _schreibe(repo, "pubspec.yaml", "name: x\nversion: 1.2.3+4\n")
    _schreibe(repo, "pubspec.lock", "# lock\n")
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R8"
    assert "pubspec.yaml: 1.2.3+4" in ergebnis.stage("R8").signale[0].beleg  # type: ignore[union-attr]


def test_changelog_ohne_versionsabschnitt_verhindert_r8(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "cl")
    _bis(repo, 8)
    _schreibe(repo, "CHANGELOG.md", "# Changelog\n\n- irgendetwas\n")
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R7"
    assert any("Versionsabschnitt" in beleg for beleg in ergebnis.naechste_luecken)


def test_has_tags_feld_hat_vorrang(tmp_path: Path) -> None:
    """Existiert ``has_tags`` am Report, entscheidet allein dieses Feld."""
    repo = make_repo(tmp_path / "feld")
    _bis(repo, 7)
    _r8(repo)

    bericht = _report(repo)
    object.__setattr__(bericht, "has_tags", False)
    ohne = assess(bericht, repo, heute=HEUTE)
    assert ohne.stufe == "R7"
    object.__setattr__(bericht, "has_tags", True)
    assert assess(bericht, repo, heute=HEUTE).stufe == "R8"


# -- R9 / R10 / R11 -------------------------------------------------------------


def test_produkt_mit_apple_ziel_durchlaeuft_r9_und_r10(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "app")
    _bis(repo, 8)
    _schreibe(repo, "ios/Runner/Info.plist", "<plist/>\n")
    ergebnis = _bewerte(repo)
    assert ergebnis.apple_ziel
    assert ergebnis.stufe == "R8"
    assert ergebnis.naechste_stufe == "R9"
    assert len(ergebnis.naechste_luecken) == 3  # Icon, Lokalisierung, Barrierefreiheit

    _apple(repo)
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R9"
    assert ergebnis.stufe_name == "Plattformreif"
    assert ergebnis.naechste_stufe == "R10"

    _vertrieb(repo)
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R10"
    assert ergebnis.stufe_name == "Vertriebsreif"

    _schreibe(repo, "SUPPORT.md", "Hilfe\n")
    _schreibe(repo, "Sources/Log.swift", "import OSLog\n")
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R11"
    assert ergebnis.stufe_name == "Betrieb"
    assert ergebnis.naechste_stufe is None
    assert ergebnis.naechste_luecken == ()
    assert [s.code for s in ergebnis.stages][-3:] == ["R9", "R10", "R11"]


def test_release_notizen_muessen_frisch_sein(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "alt")
    _bis(repo, 8)
    _apple(repo)
    _schreibe(repo, "ios/Runner/Info.plist", "<plist/>\n")
    _vertrieb(repo)
    assert _bewerte(repo).stufe == "R10"  # 2026-10-20 ist 14 Tage alt
    spaet = assess(_report(repo), repo, heute=date(2027, 6, 1))
    assert spaet.stufe == "R9"
    assert any("Tage alt" in beleg for beleg in spaet.naechste_luecken)
    _schreibe(repo, "docs/RELEASE-NOTES.md", "# Notizen\n")
    assert assess(_report(repo), repo, heute=date(2027, 6, 1)).stufe == "R10"


def test_einsprachig_erklaerung_ersetzt_lokalisierung(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "de")
    _bis(repo, 8)
    _apple(repo)
    for pfad in (repo / "ios/Runner/de.lproj/Localizable.strings",):
        pfad.unlink()
        pfad.parent.rmdir()
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R8"
    assert any("Lokalisierung" in beleg for beleg in ergebnis.naechste_luecken)
    _schreibe(repo, "README.md", "".join(f"Zeile {i}\n" for i in range(25)) + "Die App ist nur Deutsch.\n")
    assert _bewerte(repo).stufe == "R9"


def test_produkt_ohne_apple_ziel_ueberspringt_r9_und_r10(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "web")
    _bis(repo, 8)
    _schreibe(repo, "SUPPORT.md", "Hilfe\n")
    _schreibe(repo, "src/telemetry.py", "# sendet telemetry\n")
    ergebnis = _bewerte(repo)
    assert not ergebnis.apple_ziel
    codes = [s.code for s in ergebnis.stages]
    assert "R9" not in codes and "R10" not in codes
    assert codes[-2:] == ["R8", "R11"]
    assert ergebnis.stufe == "R11"


def test_r11_braucht_metriken_und_support(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "betrieb")
    _bis(repo, 8)
    _schreibe(repo, "SUPPORT.md", "Hilfe\n")
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R8"
    assert any("Metriken" in beleg for beleg in ergebnis.naechste_luecken)
    _schreibe(repo, "docs/BETRIEB.md", "Wir nutzen Sentry für Crash-Reports.\n")
    assert _bewerte(repo).stufe == "R11"


# -- Klassen ----------------------------------------------------------------------


def test_klasse_forschung_hat_rf_statt_r7_bis_r10(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "studie")
    _bis(repo, 6)
    ergebnis = _bewerte(repo, category="research")
    assert ergebnis.klasse == "forschung"
    assert [s.code for s in ergebnis.stages] == ["R0", "R1", "R2", "R3", "R4", "R5", "R6", "RF", "R11"]
    assert ergebnis.stufe == "R6"
    assert ergebnis.naechste_stufe == "RF"
    assert len(ergebnis.naechste_luecken) == 3

    _schreibe(repo, "requirements.txt", "numpy\n")
    _schreibe(repo, "scripts/reproduce.sh", "#!/bin/sh\n")
    _schreibe(repo, "results/lauf-1.csv", "a,b\n")
    ergebnis = _bewerte(repo, category="research")
    assert ergebnis.stufe == "RF"
    assert ergebnis.stufe_name == "Reproduzierbar"
    assert ergebnis.naechste_stufe == "R11"

    _schreibe(repo, "SUPPORT.md", "Hilfe\n")
    _schreibe(repo, "src/log.py", "import logging  # telemetry\n")
    assert _bewerte(repo, category="research").stufe == "R11"


def test_forschung_makefile_ziel_und_docs_results(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "studie2")
    _bis(repo, 6)
    _schreibe(repo, "environment.yml", "name: x\n")
    _schreibe(repo, "Makefile", "experiment:\n\tpython run.py\n")
    _schreibe(repo, "docs/results-2026.md", "# Ergebnisse\n")
    assert _bewerte(repo, category="forschung").stufe == "RF"


def test_klasse_infrastruktur_hat_ri_nach_r8(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "kern")
    _bis(repo, 8)
    ergebnis = _bewerte(repo, category="core")
    assert ergebnis.klasse == "infrastruktur"
    assert [s.code for s in ergebnis.stages][-3:] == ["R8", "RI", "R11"]
    assert ergebnis.stufe == "R8"
    assert ergebnis.naechste_stufe == "RI"

    _schreibe(repo, "capability.json", "{}\n")
    ergebnis = _bewerte(repo, category="core")
    assert ergebnis.stufe == "RI"
    assert ergebnis.stufe_name == "Vertrag"
    assert ergebnis.naechste_stufe == "R11"
    # Infrastruktur kennt weder R9 noch R10, auch mit Apple-Ziel nicht.
    _apple(repo)
    assert "R9" not in [s.code for s in _bewerte(repo, category="core").stages]


@pytest.mark.parametrize("beleg", ["docs/CONTRACT-v1.md", "schema/antwort.json"])
def test_ri_weitere_vertragsformen(tmp_path: Path, beleg: str) -> None:
    repo = make_repo(tmp_path / "vertrag")
    _bis(repo, 8)
    _schreibe(repo, beleg, "{}\n")
    assert _bewerte(repo, category="library").stufe == "RI"


@pytest.mark.parametrize(
    ("kategorie", "erwartet"),
    [
        (None, "produkt"),
        ("aethel-app", "produkt"),
        ("misc", "produkt"),
        ("research", "forschung"),
        ("Forschung", "forschung"),
        ("tool", "infrastruktur"),
        ("infra", "infrastruktur"),
        ("library", "infrastruktur"),
        ("core", "infrastruktur"),
        ("content", "inhalt"),
        ("heritage", "inhalt"),
        ("inhalt", "inhalt"),
    ],
)
def test_klasse_aus_manifest_kategorie(tmp_path: Path, kategorie: str | None, erwartet: str) -> None:
    assert klasse_aus(_report(tmp_path / "r", category=kategorie)) == erwartet


def test_klasse_kann_erzwungen_werden(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "erzwungen")
    assert _bewerte(repo, klasse="forschung").klasse == "forschung"
    assert _bewerte(repo, klasse="unsinn").klasse == "produkt"


def test_inhalt_durchlaeuft_wie_produkt(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "heft")
    _bis(repo, 8)
    _schreibe(repo, "ios/Runner/Info.plist", "<plist/>\n")
    ergebnis = _bewerte(repo, category="heritage")
    assert ergebnis.klasse == "inhalt"
    assert ergebnis.naechste_stufe == "R9"


def test_leiter_je_klasse() -> None:
    assert leiter("produkt")[-4:] == ("R8", "R9", "R10", "R11")
    assert leiter("produkt", apple_ziel=False)[-2:] == ("R8", "R11")
    assert leiter("inhalt") == leiter("produkt")
    assert "RF" in leiter("forschung") and "R7" not in leiter("forschung")
    assert "RI" in leiter("infrastruktur") and "R9" not in leiter("infrastruktur")
    codes = [code for code, _name in STAGES]
    assert codes[:12] == [f"R{i}" for i in range(12)]
    assert set(codes[12:]) == {"RF", "RI"}


# -- Lesegrenzen und Robustheit ---------------------------------------------------


def test_fremdordner_und_versteckte_ordner_zaehlen_nicht(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "fremd")
    _r1(repo)
    gross = "".join(f"v{i} = {i}\n" for i in range(300))
    for rel in ("node_modules/x/index.js", ".versteckt/a.py", "target/b.rs", "build/c.py", ".venv/d.py"):
        _schreibe(repo, rel, gross)
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R1"
    assert ergebnis.stage("R2").signale[0].beleg.startswith("0 LOC")  # type: ignore[union-attr]
    # Der einzige versteckte Ordner, der betreten wird, ist .github.
    _schreibe(repo, ".github/workflows/ci.yml", "run: pytest\n")
    _schreibe(repo, ".versteckt/workflows/ci.yml", "run: pytest\n")
    r5 = _bewerte(repo).stage("R5")
    assert r5 is not None and r5.signale[0].erfuellt
    assert r5.signale[0].beleg == "CI-Konfiguration: .github/workflows/ci.yml"


def test_dateien_werden_nur_bis_256_kib_gelesen(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "gross")
    _r1(repo)
    _schreibe(repo, "src/riesig.py", ("a" * 99 + "\n") * 5000)  # 500 000 Byte
    beleg = _bewerte(repo).stage("R2").signale[0].beleg  # type: ignore[union-attr]
    zeilen = int(re.match(r"(\d+) LOC", beleg).group(1))  # type: ignore[union-attr]
    assert incubator.MAX_BYTES == 256 * 1024
    assert 2500 < zeilen < 2700


def test_symlinks_werden_nicht_gelesen(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "link")
    _r1(repo)
    draussen = tmp_path / "draussen.py"
    draussen.write_text("".join(f"v{i} = {i}\n" for i in range(500)), encoding="utf-8")
    (repo / "src").mkdir()
    os.symlink(draussen, repo / "src" / "link.py")
    ergebnis = _bewerte(repo)
    assert ergebnis.stufe == "R1"
    assert ergebnis.stage("R2").signale[0].beleg.startswith("0 LOC")  # type: ignore[union-attr]


def test_assess_veraendert_nichts(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "readonly")
    _bis(repo, 8)

    def schnappschuss() -> dict[str, tuple[float, int]]:
        return {
            str(p.relative_to(repo)): (p.stat().st_mtime, p.stat().st_size)
            for p in repo.rglob("*")
            if ".git" not in p.parts and p.is_file()
        }

    vorher = schnappschuss()
    _bewerte(repo)
    assert schnappschuss() == vorher


# -- build / Ausgabe --------------------------------------------------------------


def test_build_ueberspringt_worktrees(tmp_path: Path) -> None:
    haupt = make_repo(tmp_path / "haupt")
    zweig = make_repo(tmp_path / "haupt-wt")
    ergebnis = build(
        (_report(haupt), _report(zweig, worktree=True)),
        tmp_path,
        heute=HEUTE,
    )
    assert [item.repo for item in ergebnis] == ["haupt"]


def test_build_loest_pfad_gegen_root_auf(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "ws" / "relativ")
    _r1(repo)
    bericht = _report(repo)
    relativ = RepoReport(**{**bericht.__dict__, "path": "relativ"})
    ergebnis = build((relativ,), tmp_path / "ws", heute=HEUTE)
    assert ergebnis[0].stufe == "R1"
    # Gibt es root/path nicht, gilt der Pfad des Reports selbst.
    absolut = build((bericht,), tmp_path / "anderswo", heute=HEUTE)
    assert absolut[0].stufe == "R1"


def _beispiele(tmp_path: Path) -> tuple[Readiness, ...]:
    a = make_repo(tmp_path / "alpha")
    b = make_repo(tmp_path / "beta")
    c = make_repo(tmp_path / "gamma")
    _bis(b, 4)
    _r1(c)
    _schreibe(c, "pipe.txt", "x\n")
    return build((_report(a), _report(b), _report(c, category="research")), tmp_path, heute=HEUTE)


def test_render_markdown_enthaelt_verteilung_und_luecken(tmp_path: Path) -> None:
    markdown = render_markdown(_beispiele(tmp_path))
    assert markdown.startswith("# Inkubator-Reifeleiter")
    assert "| Stufe | Name | Anzahl |" in markdown
    assert "| R0 | Idee | 1 |" in markdown
    assert "| R1 | Skizze | 1 |" in markdown
    assert "| R4 | Getestet | 1 |" in markdown
    assert "| R5 | Integriert | 0 |" in markdown
    assert "nächste Lücken" in markdown
    zeilen = [z for z in markdown.splitlines() if z.startswith(("| alpha", "| beta", "| gamma"))]
    # Stufe absteigend: beta (R4) vor gamma (R1) vor alpha (R0).
    assert [z.split("|")[1].strip() for z in zeilen] == ["beta", "gamma", "alpha"]
    beta = zeilen[0]
    assert "produkt" in beta and "R4 Getestet" in beta and "R5 Integriert" in beta
    gamma = zeilen[1]
    assert "forschung" in gamma


def test_render_markdown_kuerzt_luecken_auf_drei(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "forsch")
    _bis(repo, 6)
    markdown = render_markdown((_bewerte(repo, category="research"),))
    zeile = next(z for z in markdown.splitlines() if z.startswith("| forsch"))
    assert zeile.count(";") == 2  # drei Lücken, zwei Trenner
    assert "weitere" not in zeile


def test_render_markdown_leer_und_vollstaendig(tmp_path: Path) -> None:
    assert "Inkubator-Reifeleiter" in render_markdown(())
    repo = make_repo(tmp_path / "ganz")
    _bis(repo, 8)
    _schreibe(repo, "SUPPORT.md", "Hilfe\n")
    _schreibe(repo, "src/t.py", "# telemetry\n")
    markdown = render_markdown((_bewerte(repo),))
    zeile = next(z for z in markdown.splitlines() if z.startswith("| ganz"))
    assert "R11 Betrieb" in zeile
    assert zeile.rstrip().endswith("| - | - |")


def test_render_json_ist_gueltig_mit_schema(tmp_path: Path) -> None:
    daten = json.loads(render_json(_beispiele(tmp_path)))
    assert daten["schema"] == "aethel.projects.incubator/v1"
    assert daten["anzahl"] == 3
    assert [r["repo"] for r in daten["repos"]] == ["beta", "gamma", "alpha"]
    assert {v["stufe"] for v in daten["verteilung"]} >= {"R0", "R1", "R4", "RF", "RI"}
    erstes = daten["repos"][0]
    assert set(erstes) == {
        "repo",
        "klasse",
        "stufe",
        "stufe_name",
        "naechste_stufe",
        "naechste_luecken",
        "rang",
        "apple_ziel",
        "stages",
    }
    stage = erstes["stages"][0]
    assert set(stage) == {"code", "name", "erreicht", "signale"}
    assert set(stage["signale"][0]) == {"code", "erfuellt", "beleg"}
    assert isinstance(erstes["naechste_luecken"], list)


def test_as_dict_ist_json_serialisierbar(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "dict")
    _bis(repo, 3)
    ergebnis = _bewerte(repo)
    daten = json.loads(json.dumps(ergebnis.as_dict()))
    assert daten["stufe"] == "R3"
    assert daten["stages"][0]["signale"][0]["erfuellt"] is True
