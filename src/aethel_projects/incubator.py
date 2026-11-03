"""Inkubator-Reifeleiter — vom Prototyp bis „reif für den App Store“, mit Belegen.

Der grobe Reifegrad (``maturity.py``, Score 0–100 nach Dateiexistenz) sagt, *wie
viel* ein Repository hat. Die Reifeleiter sagt, *wo es steht*: eine geordnete
Folge fein abgestufter Stufen (R0 Idee … R11 Betrieb), jede mit prüfbaren
**Signalen** und je Signal einem **Beleg** (Fundstelle oder Fehlbefund). Sie
ergänzt den Reifegrad und ersetzt ihn nicht.

Regeln:

* Eine Stufe gilt als **erreicht**, wenn *alle* ihre Signale erfüllt sind *und*
  alle vorigen Stufen der Leiter erreicht sind. Die höchste erreichte Stufe ist
  das Ergebnis; eine fehlende Stufe sperrt alle höheren. Die Signale gesperrter
  Stufen werden trotzdem ausgewertet (Sicht auf den Rückstand), zählen aber nicht.
* Vier **Portfolio-Klassen** bestimmen die Leiter (``leiter``): ``produkt``
  (Vorgabe) und ``inhalt`` durchlaufen R0–R11; ``forschung`` R0–R6, **RF**
  (Reproduzierbar) und R11; ``infrastruktur`` R0–R8, **RI** (Vertrag) und R11.
  Die Klasse folgt aus der Manifest-Kategorie (``klasse_aus``).
* R9 (Plattformreif) und R10 (Vertriebsreif) setzen ein **Apple-Ziel** voraus
  (Swift-Quellen, ``ios/``/``macos/``, Xcode-Projekt …). Ohne Apple-Ziel
  entfallen beide Stufen in der Leiter eines ``produkt``/``inhalt``-Repos.
* Dokumente werden — wie in ``maturity.py`` — in ``docs/`` oder im Wurzelordner
  gesucht, ohne Rücksicht auf Groß-/Kleinschreibung.

Strikt lesend: gelesen wird nur unter dem Repo-Pfad (keine Symlinks), pro Datei
höchstens 256 KiB; ``fsutil.is_skipped``-Ordner und versteckte Ordner (außer
``.github``) werden nicht betreten. Einziger Git-Zugriff: ein lesendes
``for-each-ref`` über ``gitio`` (Tags). Fehlende Dateien sind ein Fehlbefund,
kein Fehler.

Stub-Marker: ``stubs.scan`` läuft über einen eigenen, unbegrenzten Walk und zählt
auch Prosa-Hinweise („Platzhalter“); die Leiter braucht dagegen eine Zählung je
Quelldatei innerhalb derselben Lesegrenzen. Wiederverwendet werden deshalb die
Sprachmuster ``stubs.PATTERNS`` (Rust, Swift, Dart, TypeScript/JavaScript), ergänzt
um Python, Go und Kotlin.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from functools import cached_property
from pathlib import Path
from typing import Any

from . import stubs
from .findings import SOURCE_SUFFIXES
from .fsutil import is_skipped
from .gitio import run_git
from .models import RepoReport

#: Schema der JSON-Ausgabe.
SCHEMA = "aethel.projects.incubator/v1"

#: Portfolio-Klassen; die erste ist die Vorgabe.
KLASSEN: tuple[str, ...] = ("produkt", "forschung", "infrastruktur", "inhalt")
DEFAULT_KLASSE = "produkt"

#: Kategorie-Schlüsselwörter je Klasse (Prüfreihenfolge = Rangfolge bei Mehrfachtreffern).
KLASSEN_SCHLUESSEL: tuple[tuple[str, frozenset[str]], ...] = (
    ("forschung", frozenset({"research", "forschung"})),
    (
        "infrastruktur",
        frozenset(
            {"tool", "tools", "infra", "infrastruktur", "infrastructure", "library", "lib", "core"}
        ),
    ),
    ("inhalt", frozenset({"content", "inhalt", "heritage"})),
)

#: Alle Stufen in Reihenfolge: R0–R11, danach die Sonderstufen RF (forschung) und RI (infrastruktur).
STAGES: tuple[tuple[str, str], ...] = (
    ("R0", "Idee"),
    ("R1", "Skizze"),
    ("R2", "Prototyp"),
    ("R3", "Spezifiziert"),
    ("R4", "Getestet"),
    ("R5", "Integriert"),
    ("R6", "Dokumentiert"),
    ("R7", "Gesichert"),
    ("R8", "Versioniert"),
    ("R9", "Plattformreif"),
    ("R10", "Vertriebsreif"),
    ("R11", "Betrieb"),
    ("RF", "Reproduzierbar"),
    ("RI", "Vertrag"),
)

_NAMEN = dict(STAGES)

#: Lesegrenze je Datei in Byte.
MAX_BYTES = 256 * 1024
#: Obergrenze der betrachteten Dateien je Repo.
MAX_DATEIEN = 20_000

MIN_README_ZEILEN = 20
MIN_LOC = 200
STUB_MAX_PROZENT = 10
MIN_REQ_ZEILEN = 3
MIN_TESTDATEIEN = 5
MIN_TEST_PROZENT = 10
RELEASE_MAX_TAGE = 180

#: Zusätzlich zu ``fsutil`` nie betretene Ordner (Fremdcode, Erzeugtes).
EXTRA_SKIP = frozenset({"Pods", "Carthage", "DerivedData", "ephemeral", "vendor"})

#: Anzahl Lücken je Repo im Markdown.
MAX_LUECKEN = 3

_GENERIERT = (".g.dart", ".freezed.dart", ".generated.dart")
_TEST_ORDNER = frozenset({"tests", "test", "__tests__", "integration_test"})
_TEST_HILFSDATEIEN = frozenset({"conftest.py", "__init__.py"})
_TEST_NAME = re.compile(r"^test_|_tests?\.|\.(?:test|spec)\.|Tests?\.(?:swift|kt)$")

#: Ergänzung zu ``stubs.PATTERNS`` für Sprachen, die dort fehlen.
_STUB_ZUSATZ: dict[str, re.Pattern[str]] = {
    ".py": re.compile(r"\braise\s+NotImplementedError\b"),
    ".go": re.compile(r"\bpanic\(\s*\"(?:not implemented|unimplemented|todo)", re.I),
    ".kt": re.compile(r"\bTODO\s*\(|\bNotImplementedError\b"),
}

_QUELL_HINWEISE: dict[str, re.Pattern[str]] = {
    "barrierefreiheit": re.compile(
        r"accessibilityLabel|accessibilityHint|accessibilityValue|Semantics\(|semanticsLabel"
    ),
    "telemetrie": re.compile(r"MetricKit|MXMetricManager|OSLog|os_log|Sentry|Crashlytics|telemetry", re.I),
}
_TELEMETRIE = _QUELL_HINWEISE["telemetrie"]
_BARRIEREFREI_DOKU = re.compile(r"barrierefrei|accessibilit|voiceover", re.I)

_TESTKOMMANDO = re.compile(
    r"\bpytest\b|-m\s+unittest\b|\bcargo\s+(?:nextest\s+run|test)\b|\bswift\s+test\b"
    r"|\bflutter\s+test\b|\bnpm\s+(?:run\s+)?test\b|\bnpm\s+t\b|\bdart\s+test\b"
    r"|\b(?:yarn|pnpm)\s+(?:run\s+)?test\b|\bgo\s+test\b|\bxcodebuild\b[^\n]*\btest\b",
    re.I,
)
_MAKE_TESTZIEL = re.compile(r"^tests?\s*:", re.M)

_LIZENZ_NAME = re.compile(r"^(?:license|licence|copying|unlicense)(?:[-._].*)?$", re.I)
_SIGNATUR = re.compile(r"\bcodesign\b|-exportArchive\b|\bnotarytool\b")
_EIN_SPRACHE = re.compile(
    r"nur\s+deutsch|nur\s+englisch|german\s+only|english\s+only|einsprachig"
    r"|ausschlie(?:ß|ss)lich\s+(?:deutsch|englisch)|single[- ]language|monolingual",
    re.I,
)
_SUPPORT = re.compile(r"\bsupport\b|fehler\s+melden|bug\s+melden|report\s+(?:a\s+)?bug|bug\s*report", re.I)
_PRIVACY_NAMEN = frozenset(
    {
        "privacy.md",
        "privacy-policy.md",
        "datenschutz.md",
        "datenschutzerklaerung.md",
        "datenschutzerklärung.md",
    }
)
_PRIVACY_PFADE = _PRIVACY_NAMEN | {f"docs/{name}" for name in _PRIVACY_NAMEN}
_PRIVACY_KOPF = re.compile(r"^\s{0,3}#{1,6}\s.*(?:privacy|datenschutz)", re.I | re.M)

_VERSION_KOPF = re.compile(
    r"^\s{0,3}(?:#{1,6}\s*(?:version\s+|release\s+)?|(?:version|release)\s+)"
    r"\[?v?(\d+\.\d+(?:\.\d+)?[\w.+-]*)\]?",
    re.I,
)
_DATUM_ISO = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
_DATUM_DE = re.compile(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b")

_APPLE_DATEIEN = frozenset({"info.plist", "privacyinfo.xcprivacy", "exportoptions.plist"})
_PRIVACY_PLIST = re.compile(r"(?:^|/)(?:ios|macos)/Runner/Info\.plist$", re.I)

#: Lock-Dateien je Manifest.
_LOCKS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Cargo.toml", ("Cargo.lock",)),
    ("pubspec.yaml", ("pubspec.lock",)),
    ("package.json", ("package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml")),
    ("pyproject.toml", ("poetry.lock", "uv.lock", "pdm.lock")),
    ("Package.swift", ("Package.resolved",)),
)

_MANIFESTE = frozenset(
    {"cargo.toml", "pubspec.yaml", "package.json", "pyproject.toml", "package.swift", "podfile"}
)
_SKRIPT_SUFFIXE = (".sh", ".zsh", ".bash", ".command", ".rb", ".yml", ".yaml")
_SKRIPT_NAMEN = frozenset({"makefile", "justfile", "fastfile"})
_UMGEBUNG_NAMEN = frozenset(
    {
        "pyproject.toml",
        "environment.yml",
        "environment.yaml",
        "cargo.lock",
        "uv.lock",
        "poetry.lock",
        "pipfile.lock",
    }
)
_REPRO_SKRIPT = re.compile(r"^(?:run|experiment|reproduce)(?:[-_.].*)?$", re.I)
_REPRO_SUFFIXE = frozenset({".sh", ".zsh", ".bash", ".py", ".jl", ".r", ".command"})
_MAKE_REPRO_ZIEL = re.compile(r"^(?:run|experiment|reproduce)[\w-]*\s*:", re.M | re.I)


# ---------------------------------------------------------------------------
# Datenmodell
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Signal:
    """Ein prüfbares Merkmal einer Stufe mit Beleg (Fundstelle oder Fehlbefund)."""

    code: str
    erfuellt: bool
    beleg: str

    def as_dict(self) -> dict[str, Any]:
        return {"code": self.code, "erfuellt": self.erfuellt, "beleg": self.beleg}


@dataclass(frozen=True)
class Stage:
    """Eine Stufe der Leiter. ``erreicht`` = alle Signale erfüllt *und* alle vorigen Stufen erreicht."""

    code: str
    name: str
    erreicht: bool
    signale: tuple[Signal, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "name": self.name,
            "erreicht": self.erreicht,
            "signale": [s.as_dict() for s in self.signale],
        }


@dataclass(frozen=True)
class Readiness:
    """Der Stand eines Repositories auf der Reifeleiter.

    ``stufe`` ist die höchste erreichte Stufe (``"-"``, wenn nicht einmal R0 gilt),
    ``naechste_stufe`` die erste nicht erreichte (``None`` am Ende der Leiter) und
    ``naechste_luecken`` die Belege ihrer nicht erfüllten Signale. ``stages``
    enthält nur die für die Klasse geltenden Stufen, in Leiterfolge.
    """

    repo: str
    klasse: str
    stufe: str
    stufe_name: str
    naechste_stufe: str | None
    naechste_luecken: tuple[str, ...]
    stages: tuple[Stage, ...]
    apple_ziel: bool = False

    @property
    def rang(self) -> int:
        """Anzahl erreichter Stufen — die Sortiergröße (klassenübergreifend vergleichbar genug)."""
        return sum(1 for stage in self.stages if stage.erreicht)

    def stage(self, code: str) -> Stage | None:
        """Die Stufe mit diesem Code, falls sie in der Leiter der Klasse steht."""
        return next((s for s in self.stages if s.code == code), None)

    def as_dict(self) -> dict[str, Any]:
        return {
            "repo": self.repo,
            "klasse": self.klasse,
            "stufe": self.stufe,
            "stufe_name": self.stufe_name,
            "naechste_stufe": self.naechste_stufe,
            "naechste_luecken": list(self.naechste_luecken),
            "rang": self.rang,
            "apple_ziel": self.apple_ziel,
            "stages": [s.as_dict() for s in self.stages],
        }


# ---------------------------------------------------------------------------
# Klasse und Leiter
# ---------------------------------------------------------------------------


def klasse_aus(report: RepoReport) -> str:
    """Portfolio-Klasse aus der Manifest-Kategorie; ohne Treffer ``produkt``."""
    eintrag = report.manifest_entry
    kategorie = (eintrag.category if eintrag else "").strip().lower()
    woerter = {w for w in re.split(r"[^0-9a-zäöüß]+", kategorie) if w}
    for klasse, schluessel in KLASSEN_SCHLUESSEL:
        if woerter & schluessel:
            return klasse
    return DEFAULT_KLASSE


def leiter(klasse: str, apple_ziel: bool = True) -> tuple[str, ...]:
    """Die Stufencodes, die für die Klasse gelten (in Reihenfolge)."""
    basis = ("R0", "R1", "R2", "R3", "R4", "R5", "R6")
    if klasse == "forschung":
        return (*basis, "RF", "R11")
    if klasse == "infrastruktur":
        return (*basis, "R7", "R8", "RI", "R11")
    plattform = ("R9", "R10") if apple_ziel else ()
    return (*basis, "R7", "R8", *plattform, "R11")


# ---------------------------------------------------------------------------
# Dateibaum (nur unter dem Repo-Pfad)
# ---------------------------------------------------------------------------


def _betreten(name: str) -> bool:
    if is_skipped(name) or name in EXTRA_SKIP:
        return False
    return not name.startswith(".") or name == ".github"


def _lies_datei(pfad: Path) -> str:
    """Höchstens ``MAX_BYTES`` Byte als Text; bei Fehlern leer."""
    try:
        with pfad.open("rb") as handle:
            roh = handle.read(MAX_BYTES)
    except OSError:
        return ""
    return roh.decode("utf-8", errors="replace")


class _Baum:
    """Der Dateibaum eines Repos: relative POSIX-Pfade, ohne Symlinks und Fremdordner."""

    def __init__(self, wurzel: Path) -> None:
        self.wurzel = wurzel
        self.dateien: dict[str, Path] = {}
        self.ordner: set[str] = set()
        self._durchlaufen()
        self._klein: dict[str, str] = {}
        for rel in self.dateien:
            self._klein.setdefault(rel.lower(), rel)
        self._texte: dict[str, str] = {}

    def _durchlaufen(self) -> None:
        if not self.wurzel.is_dir():
            return
        for pfad, ordner, namen in os.walk(self.wurzel, topdown=True, followlinks=False):
            basis = Path(pfad)
            ordner[:] = sorted(d for d in ordner if _betreten(d) and not (basis / d).is_symlink())
            rel_basis = basis.relative_to(self.wurzel).as_posix()
            prefix = "" if rel_basis == "." else rel_basis + "/"
            self.ordner.update(prefix + d for d in ordner)
            for name in sorted(namen):
                datei = basis / name
                if datei.is_symlink():
                    continue
                self.dateien[prefix + name] = datei
                if len(self.dateien) >= MAX_DATEIEN:
                    return

    def erste(self, *kandidaten: str) -> str | None:
        """Der erste vorhandene relative Pfad (Groß-/Kleinschreibung egal)."""
        for kandidat in kandidaten:
            rel = self._klein.get(kandidat.lower())
            if rel is not None:
                return rel
        return None

    def lies(self, rel: str) -> str:
        if rel not in self._texte:
            pfad = self.dateien.get(rel)
            self._texte[rel] = _lies_datei(pfad) if pfad is not None else ""
        return self._texte[rel]


def _name(rel: str) -> str:
    return rel.rsplit("/", 1)[-1]


def _suffix(rel: str) -> str:
    return os.path.splitext(rel)[1].lower()


def _ist_testdatei(rel: str) -> bool:
    if _suffix(rel) not in SOURCE_SUFFIXES:
        return False
    name = _name(rel)
    if name in _TEST_HILFSDATEIEN:
        return False
    if any(teil.lower() in _TEST_ORDNER for teil in rel.split("/")[:-1]):
        return True
    return bool(_TEST_NAME.search(name))


def _ist_quelldatei(rel: str) -> bool:
    if _suffix(rel) not in SOURCE_SUFFIXES or rel.endswith(_GENERIERT):
        return False
    return not _ist_testdatei(rel)


def _hat_stub(suffix: str, text: str) -> bool:
    for muster in (stubs.PATTERNS.get(suffix), _STUB_ZUSATZ.get(suffix)):
        if muster is not None and muster.search(text):
            return True
    return False


@dataclass(frozen=True)
class _Quelle:
    rel: str
    loc: int
    stub: bool
    hinweise: frozenset[str]


def _inhaltszeilen(text: str) -> int:
    return sum(1 for zeile in text.splitlines() if zeile.strip())


# ---------------------------------------------------------------------------
# Kontext: alles, was mehrere Stufen brauchen, einmal berechnet
# ---------------------------------------------------------------------------


class _Kontext:
    def __init__(self, report: RepoReport, pfad: Path, heute: date) -> None:
        self.report = report
        self.pfad = pfad
        self.heute = heute
        self.baum = _Baum(pfad)

    # -- Quellen und Tests -------------------------------------------------

    @cached_property
    def quellen(self) -> tuple[_Quelle, ...]:
        ergebnis = []
        for rel, datei in self.baum.dateien.items():
            if not _ist_quelldatei(rel):
                continue
            text = _lies_datei(datei)
            hinweise = frozenset(n for n, muster in _QUELL_HINWEISE.items() if muster.search(text))
            ergebnis.append(_Quelle(rel, _inhaltszeilen(text), _hat_stub(_suffix(rel), text), hinweise))
        return tuple(ergebnis)

    @cached_property
    def testdateien(self) -> tuple[str, ...]:
        return tuple(rel for rel in self.baum.dateien if _ist_testdatei(rel))

    # -- Dokumente ---------------------------------------------------------

    def doc(self, *namen: str) -> str | None:
        """``docs/<name>`` oder ``<name>`` im Wurzelordner."""
        kandidaten: list[str] = []
        for name in namen:
            kandidaten += [f"docs/{name}", name]
        return self.baum.erste(*kandidaten)

    @cached_property
    def readme(self) -> str | None:
        return self.baum.erste("README.md", "README.rst", "README.txt", "README")

    @cached_property
    def changelog(self) -> str | None:
        return self.doc("CHANGELOG.md", "CHANGES.md", "CHANGELOG", "CHANGELOG.rst", "CHANGELOG.txt", "CHANGES")

    @cached_property
    def lizenz(self) -> str | None:
        for rel in self.baum.dateien:
            if "/" not in rel and _LIZENZ_NAME.match(rel):
                return rel
        return None

    @cached_property
    def markdown(self) -> tuple[str, ...]:
        return tuple(r for r in self.baum.dateien if r.lower().endswith((".md", ".markdown", ".rst")))

    @cached_property
    def manifeste(self) -> tuple[str, ...]:
        return tuple(
            r
            for r in self.baum.dateien
            if _name(r).lower() in _MANIFESTE or _name(r).lower().startswith("requirements")
        )

    @cached_property
    def skripte(self) -> tuple[str, ...]:
        return tuple(
            r
            for r in self.baum.dateien
            if _suffix(r) in _SKRIPT_SUFFIXE or _name(r).lower() in _SKRIPT_NAMEN
        )

    def finde(self, muster: re.Pattern[str], rels: Iterable[str]) -> tuple[str, str] | None:
        """Erste Fundstelle ``(Datei, Treffer)`` des Musters in den Dateien."""
        for rel in rels:
            treffer = muster.search(self.baum.lies(rel))
            if treffer is not None:
                return rel, treffer.group(0)
        return None

    # -- CI ----------------------------------------------------------------

    @cached_property
    def ci_dateien(self) -> tuple[str, ...]:
        gefunden = []
        for rel in self.baum.dateien:
            klein = rel.lower()
            if klein.startswith(".github/workflows/") and klein.endswith((".yml", ".yaml")):
                gefunden.append(rel)
            elif klein == ".gitlab-ci.yml" or _name(klein) == "local-ci.sh":
                gefunden.append(rel)
            elif klein in {"makefile", "gnumakefile"} and _MAKE_TESTZIEL.search(self.baum.lies(rel)):
                gefunden.append(rel)
        return tuple(gefunden)


# ---------------------------------------------------------------------------
# Hilfen der Prüfungen
# ---------------------------------------------------------------------------


def _signal(code: str, erfuellt: bool, ok: str, fehlt: str) -> Signal:
    return Signal(code, bool(erfuellt), ok if erfuellt else fehlt)


def _datei_signal(code: str, rel: str | None, fehlt: str) -> Signal:
    return _signal(code, rel is not None, f"{rel} vorhanden", fehlt)


def _gitignore_trifft(text: str, rest: str) -> bool:
    """Wird ``rest`` (Pfad relativ zur .gitignore) ausgeschlossen? Letzter Treffer gewinnt."""
    teile = rest.split("/")
    ignoriert = False
    for zeile in text.splitlines():
        muster = zeile.strip()
        if not muster or muster.startswith("#"):
            continue
        negiert = muster.startswith("!")
        if negiert:
            muster = muster[1:]
        nur_ordner = muster.endswith("/")
        muster = muster.rstrip("/")
        verankert = "/" in muster
        muster = muster.lstrip("/")
        if not muster:
            continue
        bis = len(teile) - 1 if nur_ordner else len(teile)
        for tiefe in range(1, bis + 1):
            kandidat = "/".join(teile[:tiefe]) if verankert else teile[tiefe - 1]
            if fnmatch.fnmatchcase(kandidat, muster):
                ignoriert = not negiert
                break
    return ignoriert


def _ignoriert(baum: _Baum, rel: str) -> bool:
    """Schließt eine .gitignore im Wurzel- oder einem Elternordner die Datei aus?"""
    teile = rel.split("/")
    for tiefe in range(len(teile)):
        ordner = "/".join(teile[:tiefe])
        gitignore = f"{ordner}/.gitignore" if ordner else ".gitignore"
        if gitignore in baum.dateien and _gitignore_trifft(baum.lies(gitignore), "/".join(teile[tiefe:])):
            return True
    return False


def _ist_geheimnis(name: str) -> bool:
    return name == ".env" or name == "id_rsa" or name.lower().endswith((".pem", ".p12"))


def _hat_abhaengigkeiten(manifest: str, text: str) -> bool:
    """Deklariert das Manifest Abhängigkeiten? Nur dort geprüft, wo es günstig geht."""
    if manifest == "package.json":
        try:
            daten = json.loads(text)
        except ValueError:
            return True
        if not isinstance(daten, dict):
            return False
        schluessel = ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies")
        return any(daten.get(k) for k in schluessel)
    if manifest == "pyproject.toml":
        return bool(
            re.search(r"^dependencies\s*=\s*\[\s*[\"']", text, re.M)
            or re.search(r"^\[(?:tool\.poetry\.(?:dev-)?dependencies|dependency-groups)\]", text, re.M)
            or re.search(r"^\[project\.optional-dependencies", text, re.M)
        )
    if manifest == "Package.swift":
        return bool(re.search(r"\.package\s*\(", text))
    return True


def _toml_version(text: str) -> str | None:
    abschnitt = ""
    for zeile in text.splitlines():
        s = zeile.strip()
        if s.startswith("["):
            abschnitt = s.strip("[] ").lower()
        elif abschnitt in {"package", "project", "tool.poetry", "workspace.package"}:
            treffer = re.match(r"version\s*=\s*[\"']([^\"']+)[\"']", s)
            if treffer:
                return treffer.group(1)
    return None


def _manifest_version(rel: str, text: str) -> str | None:
    name = _name(rel).lower()
    if name == "pubspec.yaml":
        treffer = re.search(r"^version:\s*(\S+)", text, re.M)
        return treffer.group(1) if treffer else None
    if name in {"cargo.toml", "pyproject.toml"}:
        return _toml_version(text)
    if name == "package.json":
        try:
            daten = json.loads(text)
        except ValueError:
            return None
        version = daten.get("version") if isinstance(daten, dict) else None
        return version if isinstance(version, str) and version else None
    return None


def _git_tag(pfad: Path) -> bool:
    """Gibt es mindestens einen Git-Tag? (Lesendes ``for-each-ref``; ohne ``.git`` kein Aufruf.)"""
    if not (pfad / ".git").exists():
        return False
    ausgabe = run_git(pfad, "for-each-ref", "--count=1", "--format=%(refname)", "refs/tags")
    return bool(ausgabe)


def _datum(zeile: str) -> date | None:
    try:
        iso = _DATUM_ISO.search(zeile)
        if iso:
            return date(int(iso.group(1)), int(iso.group(2)), int(iso.group(3)))
        de = _DATUM_DE.search(zeile)
        if de:
            return date(int(de.group(3)), int(de.group(2)), int(de.group(1)))
    except ValueError:
        return None
    return None


def _versionsabschnitte(text: str) -> list[tuple[str, date | None]]:
    """(Version, Datum) je Versionsabschnitt eines Änderungsprotokolls."""
    abschnitte = []
    for zeile in text.splitlines():
        treffer = _VERSION_KOPF.match(zeile)
        if treffer:
            abschnitte.append((treffer.group(1), _datum(zeile)))
    return abschnitte


# ---------------------------------------------------------------------------
# Prüfungen je Stufe
# ---------------------------------------------------------------------------


def _pruefe_r0(k: _Kontext) -> tuple[Signal, ...]:
    commits = k.report.commits_total
    return (
        _signal(
            "r0.repo",
            k.pfad.is_dir(),
            f"Verzeichnis vorhanden: {k.pfad}",
            f"Verzeichnis fehlt: {k.pfad}",
        ),
        _signal("r0.commit", commits >= 1, f"{commits} Commit(s)", "kein Commit im Repository"),
    )


def _pruefe_r1(k: _Kontext) -> tuple[Signal, ...]:
    zeilen = _inhaltszeilen(k.baum.lies(k.readme)) if k.readme else 0
    spec = k.doc("SPEC.md")
    if k.readme and zeilen >= MIN_README_ZEILEN:
        return (Signal("r1.readme_oder_spec", True, f"{k.readme}: {zeilen} Inhaltszeilen (≥ {MIN_README_ZEILEN})"),)
    if spec:
        return (Signal("r1.readme_oder_spec", True, f"{spec} vorhanden"),)
    if k.readme:
        fehlt = f"{k.readme} hat nur {zeilen} Inhaltszeilen (< {MIN_README_ZEILEN}) und docs/SPEC.md fehlt"
    else:
        fehlt = f"weder README (≥ {MIN_README_ZEILEN} Inhaltszeilen) noch docs/SPEC.md vorhanden"
    return (Signal("r1.readme_oder_spec", False, fehlt),)


def _pruefe_r2(k: _Kontext) -> tuple[Signal, ...]:
    quellen = k.quellen
    loc = sum(q.loc for q in quellen)
    stubdateien = sum(1 for q in quellen if q.stub)
    anzahl = len(quellen)
    ok_stub = stubdateien * 100 <= STUB_MAX_PROZENT * anzahl
    return (
        _signal(
            "r2.loc",
            loc >= MIN_LOC,
            f"{loc} LOC in {anzahl} Quelldateien (≥ {MIN_LOC})",
            f"{loc} LOC in {anzahl} Quelldateien (< {MIN_LOC})",
        ),
        _signal(
            "r2.stubs",
            ok_stub,
            f"{stubdateien} von {anzahl} Quelldateien mit Stub-Marker (≤ {STUB_MAX_PROZENT} %)",
            f"{stubdateien} von {anzahl} Quelldateien mit Stub-Marker (> {STUB_MAX_PROZENT} %)",
        ),
    )


def _pruefe_r3(k: _Kontext) -> tuple[Signal, ...]:
    spec = k.doc("SPEC.md")
    testfaelle = k.doc("TEST-CASES.md")
    req = 0
    if spec:
        text = k.baum.lies(spec)
        req = sum(1 for zeile in text.splitlines() if "REQ-" in zeile or re.search(r"\bSHALL\b", zeile))
    return (
        _datei_signal("r3.spec", spec, "docs/SPEC.md fehlt"),
        _datei_signal("r3.testfaelle", testfaelle, "docs/TEST-CASES.md fehlt"),
        _signal(
            "r3.req",
            req >= MIN_REQ_ZEILEN,
            f"{spec} enthält {req} REQ-/SHALL-Zeilen (≥ {MIN_REQ_ZEILEN})",
            f"{spec} enthält nur {req} REQ-/SHALL-Zeilen (< {MIN_REQ_ZEILEN})"
            if spec
            else "SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar",
        ),
    )


def _pruefe_r4(k: _Kontext) -> tuple[Signal, ...]:
    tests = len(k.testdateien)
    quellen = len(k.quellen)
    if tests == 0:
        return (
            Signal(
                "r4.tests",
                False,
                "keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart)",
            ),
        )
    anteil = 100 * tests / quellen if quellen else 100.0
    umfang = f"{tests} Testdateien, Anteil {anteil:.0f} % an {quellen} Quelldateien"
    genug = tests >= MIN_TESTDATEIEN or tests * 100 >= MIN_TEST_PROZENT * quellen
    return (
        _signal(
            "r4.tests",
            genug,
            f"{umfang} (≥ {MIN_TESTDATEIEN} Dateien oder ≥ {MIN_TEST_PROZENT} %)",
            f"{umfang} (< {MIN_TESTDATEIEN} Dateien und < {MIN_TEST_PROZENT} %)",
        ),
    )


def _pruefe_r5(k: _Kontext) -> tuple[Signal, ...]:
    ci = k.ci_dateien
    treffer = k.finde(_TESTKOMMANDO, ci)
    if treffer:
        kommando = f"Testkommando „{treffer[1]}“ in {treffer[0]}"
    elif ci:
        kommando = (
            "kein Testkommando (pytest, cargo test, swift test, flutter test, npm test, dart test) "
            "in den CI-Dateien"
        )
    else:
        kommando = "keine CI-Datei, daher kein Testkommando"
    return (
        _signal(
            "r5.ci",
            bool(ci),
            f"CI-Konfiguration: {', '.join(ci[:3])}",
            "keine CI-Konfiguration (.github/workflows/*.yml, .gitlab-ci.yml, Makefile mit test-Ziel, local-ci.sh)",
        ),
        Signal("r5.testkommando", treffer is not None, kommando),
    )


def _pruefe_r6(k: _Kontext) -> tuple[Signal, ...]:
    return (
        _datei_signal(
            "r6.architektur",
            k.doc("ARCHITECTURE.md", "DESIGN.md"),
            "docs/ARCHITECTURE.md oder docs/DESIGN.md fehlt",
        ),
        _datei_signal("r6.changelog", k.changelog, "CHANGELOG.md (oder CHANGES.md) fehlt"),
        _datei_signal("r6.lizenz", k.lizenz, "Lizenzdatei (LICENSE) fehlt"),
    )


def _pruefe_r7(k: _Kontext) -> tuple[Signal, ...]:
    baum = k.baum
    geheimnisse = [rel for rel in baum.dateien if _ist_geheimnis(_name(rel))]
    offen = [rel for rel in geheimnisse if not _ignoriert(baum, rel)]
    if offen:
        geheimnis = f"Geheimnisdatei ohne .gitignore-Eintrag: {', '.join(offen[:3])}"
    elif geheimnisse:
        geheimnis = f"{len(geheimnisse)} Geheimnisdatei(en), alle per .gitignore ausgeschlossen"
    else:
        geheimnis = "keine .env/*.pem/*.p12/id_rsa im Baum"

    fehlend: list[str] = []
    vorhanden: list[str] = []
    namen = {_name(r) for r in baum.dateien}
    for manifest, locks in _LOCKS:
        rels = [r for r in baum.dateien if _name(r) == manifest]
        if not any(_hat_abhaengigkeiten(manifest, baum.lies(r)) for r in rels):
            continue
        gefunden = next((lock for lock in locks if lock in namen), None)
        if gefunden:
            vorhanden.append(f"{gefunden} (zu {manifest})")
        else:
            fehlend.append(f"{locks[0]} (zu {manifest})")
    if fehlend:
        lock = f"Abhängigkeits-Lock fehlt: {', '.join(fehlend)}"
    elif vorhanden:
        lock = f"Abhängigkeits-Lock vorhanden: {', '.join(vorhanden)}"
    else:
        lock = "kein Manifest mit Abhängigkeiten, Lock nicht erforderlich"
    return (
        _datei_signal("r7.lizenz", k.lizenz, "Lizenzdatei (LICENSE) fehlt"),
        Signal("r7.geheimnisse", not offen, geheimnis),
        Signal("r7.lock", not fehlend, lock),
    )


def _versionsbeleg(k: _Kontext) -> Signal:
    code = "r8.version"
    gesetzt = getattr(k.report, "has_tags", None)
    if isinstance(gesetzt, bool):
        return _signal(code, gesetzt, "Git-Tag vorhanden (report.has_tags)", "kein Git-Tag (report.has_tags)")
    if _git_tag(k.pfad):
        return Signal(code, True, "Git-Tag vorhanden")
    version = k.baum.erste("VERSION")
    if version and k.baum.lies(version).strip():
        return Signal(code, True, f"Datei {version}: {k.baum.lies(version).strip().splitlines()[0]}")
    for rel in k.manifeste:
        gefunden = _manifest_version(rel, k.baum.lies(rel))
        if gefunden:
            return Signal(code, True, f"version-Feld in {rel}: {gefunden}")
    return Signal(
        code,
        False,
        "weder Git-Tag noch Datei VERSION noch version-Feld in pubspec.yaml/Cargo.toml/package.json/pyproject.toml",
    )


def _pruefe_r8(k: _Kontext) -> tuple[Signal, ...]:
    abschnitte = _versionsabschnitte(k.baum.lies(k.changelog)) if k.changelog else []
    if abschnitte:
        changelog = Signal("r8.changelog_version", True, f"{k.changelog}: Versionsabschnitt {abschnitte[0][0]}")
    elif k.changelog:
        changelog = Signal(
            "r8.changelog_version",
            False,
            f"{k.changelog} ohne Versionsabschnitt (erwartet z. B. „## [1.0.0] - 2026-10-20“)",
        )
    else:
        changelog = Signal("r8.changelog_version", False, "kein CHANGELOG, daher kein Versionsabschnitt")
    return (_versionsbeleg(k), changelog)


def _apple_beleg(baum: _Baum) -> str | None:
    """Fundstelle eines Apple-Ziels (Swift, ios/macos, Xcode-Projekt …) oder ``None``."""
    for rel in baum.dateien:
        teile = rel.lower().split("/")
        if _suffix(rel) == ".swift" or teile[-1] in _APPLE_DATEIEN:
            return rel
        for teil in teile[:-1]:
            if teil in {"ios", "macos"} or teil.endswith((".xcodeproj", ".xcworkspace", ".xcassets")):
                return rel
    return None


def _pruefe_r9(k: _Kontext) -> tuple[Signal, ...]:
    baum = k.baum
    privacy = next(
        (r for r in baum.dateien if _name(r).lower() == "privacyinfo.xcprivacy" or _PRIVACY_PLIST.search(r)),
        None,
    )
    icon = next(
        (o for o in sorted(baum.ordner) if _name(o) in {"AppIcon.appiconset", "AppIcon.icon"}),
        None,
    )
    if icon is None:
        pubspec = k.baum.erste("pubspec.yaml")
        if (pubspec and "flutter_launcher_icons" in baum.lies(pubspec)) or any(
            _name(r).lower().startswith("flutter_launcher_icons") for r in baum.dateien
        ):
            icon = "flutter_launcher_icons"
    lokal = next(
        (
            o
            for o in sorted(baum.ordner)
            if _name(o).lower().endswith(".lproj") or _name(o).lower() == "l10n"
        ),
        None,
    ) or next(
        (r for r in baum.dateien if _suffix(r) in {".arb", ".xcstrings"} or _name(r) == "Localizable.strings"),
        None,
    )
    erklaerung = k.finde(_EIN_SPRACHE, [k.readme] if k.readme else [])
    if lokal is not None:
        lokalisierung = f"Lokalisierung: {lokal}"
    elif erklaerung is not None:
        lokalisierung = f"Ein-Sprach-Erklärung in {erklaerung[0]}: „{erklaerung[1]}“"
    else:
        lokalisierung = ""
    barriere = next((q.rel for q in k.quellen if "barrierefreiheit" in q.hinweise), None)
    if barriere is None:
        gefunden = k.finde(_BARRIEREFREI_DOKU, k.markdown)
        barriere = gefunden[0] if gefunden else None
    return (
        _signal(
            "r9.privacy",
            privacy is not None,
            f"Datenschutz-/Plattform-Manifest: {privacy}",
            "weder PrivacyInfo.xcprivacy noch ios/Runner bzw. macos/Runner mit Info.plist",
        ),
        _signal(
            "r9.icon",
            icon is not None,
            f"App-Icon: {icon}",
            "kein App-Icon (Assets.xcassets/AppIcon.appiconset oder flutter_launcher_icons)",
        ),
        _signal(
            "r9.lokalisierung",
            bool(lokalisierung),
            lokalisierung,
            "keine Lokalisierung (*.lproj, l10n/, *.arb, *.xcstrings) und keine "
            "Ein-Sprach-Erklärung im README („nur Deutsch“/„English only“)",
        ),
        _signal(
            "r9.barrierefreiheit",
            barriere is not None,
            f"Barrierefreiheits-Hinweis in {barriere}",
            "kein Barrierefreiheits-Hinweis (accessibilityLabel, Semantics(, semanticsLabel "
            "oder Abschnitt in docs/README)",
        ),
    )


def _pruefe_r10(k: _Kontext) -> tuple[Signal, ...]:
    baum = k.baum
    signatur = next((r for r in baum.dateien if _name(r) == "ExportOptions.plist"), None)
    if signatur is None:
        signatur = next((o for o in sorted(baum.ordner) if _name(o).lower() == "fastlane"), None)
    if signatur is None:
        gefunden = k.finde(_SIGNATUR, k.skripte)
        signatur = f"{gefunden[0]} („{gefunden[1]}“)" if gefunden else None

    release = None
    grund = "kein CHANGELOG und kein docs/RELEASE*.md"
    if k.changelog:
        datierte = [(d, v) for v, d in _versionsabschnitte(baum.lies(k.changelog)) if d is not None]
        if datierte:
            letzte, version = max(datierte)
            alter = (k.heute - letzte).days
            if alter <= RELEASE_MAX_TAGE:
                release = (
                    f"{k.changelog}: Version {version} vom {letzte.isoformat()} "
                    f"({alter} Tage, ≤ {RELEASE_MAX_TAGE})"
                )
            else:
                grund = (
                    f"{k.changelog}: letzte Version {version} vom {letzte.isoformat()} ist {alter} Tage alt "
                    f"(> {RELEASE_MAX_TAGE}) und kein docs/RELEASE*.md"
                )
        else:
            grund = f"{k.changelog} ohne datierten Versionsabschnitt und kein docs/RELEASE*.md"
    if release is None:
        notiz = next(
            (r for r in baum.dateien if re.fullmatch(r"(?:docs/)?release[^/]*\.md", r.lower())), None
        )
        if notiz:
            release = f"Release-Notizen: {notiz}"

    datenschutz = next((r for r in baum.dateien if r.lower() in _PRIVACY_PFADE), None)
    if datenschutz is None and k.readme and _PRIVACY_KOPF.search(baum.lies(k.readme)):
        datenschutz = f"{k.readme} (Überschrift)"
    return (
        _signal(
            "r10.signatur",
            signatur is not None,
            f"Signatur-/Notarisierungs-Konfiguration: {signatur}",
            "keine Signatur-/Notarisierungs-Konfiguration (ExportOptions.plist, fastlane/, "
            "codesign in Skripten, xcodebuild -exportArchive)",
        ),
        _signal("r10.release_notizen", release is not None, release or "", grund),
        _signal(
            "r10.datenschutz",
            datenschutz is not None,
            f"Datenschutzerklärung: {datenschutz}",
            "keine Datenschutzerklärung (PRIVACY.md, docs/DATENSCHUTZ.md, "
            "„Privacy“/„Datenschutz“ als README-Überschrift)",
        ),
    )


def _pruefe_r11(k: _Kontext) -> tuple[Signal, ...]:
    metrik: str | None = next((q.rel for q in k.quellen if "telemetrie" in q.hinweise), None)
    if metrik is None:
        gefunden = k.finde(_TELEMETRIE, (*k.manifeste, *k.markdown))
        metrik = gefunden[0] if gefunden else None
    support = k.baum.erste(
        "SUPPORT.md",
        "docs/SUPPORT.md",
        ".github/SUPPORT.md",
        "CONTRIBUTING.md",
        "docs/CONTRIBUTING.md",
        ".github/CONTRIBUTING.md",
    )
    if support is None and k.readme:
        gefunden = k.finde(_SUPPORT, [k.readme])
        support = f"{k.readme} („{gefunden[1]}“)" if gefunden else None
    return (
        _signal(
            "r11.metriken",
            metrik is not None,
            f"Metriken/Crash-Reporting-Hinweis in {metrik}",
            "kein Metriken-/Crash-Reporting-Hinweis (MetricKit, OSLog, Sentry, Crashlytics, telemetry)",
        ),
        _signal(
            "r11.support",
            support is not None,
            f"Support-/Issue-Hinweis: {support}",
            "kein Support-/Issue-Hinweis (SUPPORT.md, CONTRIBUTING.md oder „Support“/„Fehler melden“ im README)",
        ),
    )


def _pruefe_rf(k: _Kontext) -> tuple[Signal, ...]:
    baum = k.baum
    umgebung = next(
        (
            r
            for r in baum.dateien
            if _name(r).lower() in _UMGEBUNG_NAMEN
            or re.fullmatch(r"requirements[^/]*\.txt", _name(r).lower())
        ),
        None,
    )
    skript = next(
        (
            r
            for r in baum.dateien
            if _suffix(r) in _REPRO_SUFFIXE and _REPRO_SKRIPT.match(os.path.splitext(_name(r))[0])
        ),
        None,
    )
    if skript is None:
        for rel in baum.dateien:
            if _name(rel).lower() not in {"makefile", "gnumakefile", "justfile"}:
                continue
            if _MAKE_REPRO_ZIEL.search(baum.lies(rel)):
                skript = f"{rel} (Ziel)"
                break
    ergebnisse = next(
        (
            r
            for r in baum.dateien
            if r.lower().startswith(("results/", "ergebnisse/", "docs/results", "docs/ergebnisse"))
        ),
        None,
    )
    return (
        _signal(
            "rf.umgebung",
            umgebung is not None,
            f"Umgebungsdatei: {umgebung}",
            "keine Umgebungsdatei (requirements*.txt, pyproject.toml, environment.yml, Cargo.lock)",
        ),
        _signal(
            "rf.skript",
            skript is not None,
            f"Reproduktions-Einstieg: {skript}",
            "kein Skript oder Makefile-Ziel namens run/experiment/reproduce",
        ),
        _signal(
            "rf.ergebnisse",
            ergebnisse is not None,
            f"Ergebnisse: {ergebnisse}",
            "kein Ergebnisordner (results/ oder docs/results*)",
        ),
    )


def _pruefe_ri(k: _Kontext) -> tuple[Signal, ...]:
    baum = k.baum
    vertrag = next((r for r in baum.dateien if _name(r).lower() == "capability.json"), None)
    if vertrag is None:
        vertrag = next(
            (r for r in baum.dateien if re.fullmatch(r"(?:docs/)?contract[^/]*\.md", r.lower())), None
        )
    if vertrag is None:
        vertrag = next(
            (
                r
                for r in baum.dateien
                if _suffix(r) == ".json" and r.lower().startswith(("schema/", "schemas/"))
            ),
            None,
        )
    return (
        _signal(
            "ri.vertrag",
            vertrag is not None,
            f"Vertrag: {vertrag}",
            "kein Vertrag (capability.json, docs/CONTRACT*.md oder schema/ mit *.json)",
        ),
    )


_PRUEFER = {
    "R0": _pruefe_r0,
    "R1": _pruefe_r1,
    "R2": _pruefe_r2,
    "R3": _pruefe_r3,
    "R4": _pruefe_r4,
    "R5": _pruefe_r5,
    "R6": _pruefe_r6,
    "R7": _pruefe_r7,
    "R8": _pruefe_r8,
    "R9": _pruefe_r9,
    "R10": _pruefe_r10,
    "R11": _pruefe_r11,
    "RF": _pruefe_rf,
    "RI": _pruefe_ri,
}


# ---------------------------------------------------------------------------
# Bewertung
# ---------------------------------------------------------------------------


def assess(
    report: RepoReport,
    repo_path: Path,
    *,
    klasse: str | None = None,
    heute: date | None = None,
) -> Readiness:
    """Stellt den Stand eines Repos auf der Reifeleiter fest.

    :param klasse: erzwingt eine Klasse (sonst :func:`klasse_aus`); Unbekanntes wird ignoriert
    :param heute: Stichtag für „letzte Version ≤ 180 Tage“ (Vorgabe: heute)
    """
    gewaehlt = klasse if klasse in KLASSEN else klasse_aus(report)
    kontext = _Kontext(report, Path(repo_path), heute or date.today())
    apple = _apple_beleg(kontext.baum) is not None

    stages: list[Stage] = []
    bisher = True
    for code in leiter(gewaehlt, apple):
        signale = _PRUEFER[code](kontext)
        erreicht = bisher and all(s.erfuellt for s in signale)
        stages.append(Stage(code, _NAMEN[code], erreicht, signale))
        bisher = erreicht

    erreichte = [s for s in stages if s.erreicht]
    offen = next((s for s in stages if not s.erreicht), None)
    return Readiness(
        repo=report.name,
        klasse=gewaehlt,
        stufe=erreichte[-1].code if erreichte else "-",
        stufe_name=erreichte[-1].name if erreichte else "Keine Stufe",
        naechste_stufe=offen.code if offen else None,
        naechste_luecken=tuple(s.beleg for s in offen.signale if not s.erfuellt) if offen else (),
        stages=tuple(stages),
        apple_ziel=apple,
    )


def build(
    repos: tuple[RepoReport, ...],
    root: Path,
    *,
    heute: date | None = None,
) -> tuple[Readiness, ...]:
    """Bewertet alle Repos (Worktrees werden übersprungen) in der Reihenfolge der Eingabe."""
    wurzel = Path(root)
    ergebnis = []
    for report in repos:
        if report.is_worktree:
            continue
        kandidat = wurzel / report.path
        pfad = kandidat if kandidat.exists() else Path(report.path)
        ergebnis.append(assess(report, pfad, heute=heute))
    return tuple(ergebnis)


# ---------------------------------------------------------------------------
# Ausgabe
# ---------------------------------------------------------------------------


def _sortiert(items: Iterable[Readiness]) -> list[Readiness]:
    """Nach Stufe absteigend (Anzahl erreichter Stufen), dann nach Name."""
    return sorted(items, key=lambda r: (-r.rang, r.repo))


def verteilung(items: Iterable[Readiness]) -> tuple[tuple[str, str, int], ...]:
    """(Stufe, Name, Anzahl) je Stufe aus ``STAGES``; ``("-", "Keine Stufe", n)`` nur bei n > 0."""
    zaehler: dict[str, int] = {}
    for item in items:
        zaehler[item.stufe] = zaehler.get(item.stufe, 0) + 1
    zeilen = [(code, name, zaehler.get(code, 0)) for code, name in STAGES]
    if zaehler.get("-"):
        zeilen.append(("-", "Keine Stufe", zaehler["-"]))
    return tuple(zeilen)


def _zelle(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _luecken(item: Readiness) -> str:
    if item.naechste_stufe is None:
        return "-"
    gezeigt = [_zelle(text) for text in item.naechste_luecken[:MAX_LUECKEN]]
    rest = len(item.naechste_luecken) - len(gezeigt)
    if rest > 0:
        gezeigt.append(f"(+{rest} weitere)")
    return "; ".join(gezeigt) or "-"


def render_markdown(items: Iterable[Readiness]) -> str:
    """Verteilungstabelle und je Repo eine Zeile mit Stufe, nächster Stufe und nächsten Lücken."""
    liste = _sortiert(items)
    zeilen = [
        "# Inkubator-Reifeleiter",
        "",
        "Nur lesend. Eine Stufe gilt, wenn alle ihre Signale erfüllt und alle vorigen Stufen erreicht sind.",
        "",
        "## Verteilung",
        "",
        "| Stufe | Name | Anzahl |",
        "|---|---|---:|",
    ]
    zeilen += [f"| {code} | {name} | {anzahl} |" for code, name, anzahl in verteilung(liste)]
    zeilen += [
        "",
        f"## Repos ({len(liste)})",
        "",
        "| Repo | Klasse | Stufe | nächste Stufe | nächste Lücken |",
        "|---|---|---|---|---|",
    ]
    for item in liste:
        stufe = f"{item.stufe} {item.stufe_name}"
        naechste = f"{item.naechste_stufe} {_NAMEN[item.naechste_stufe]}" if item.naechste_stufe else "-"
        zeilen.append(
            f"| {_zelle(item.repo)} | {item.klasse} | {stufe} | {naechste} | {_luecken(item)} |"
        )
    return "\n".join(zeilen)


def render_json(items: Iterable[Readiness]) -> str:
    """Die Reifeleiter als JSON (Schema ``aethel.projects.incubator/v1``)."""
    liste = _sortiert(items)
    daten = {
        "schema": SCHEMA,
        "anzahl": len(liste),
        "verteilung": [
            {"stufe": code, "name": name, "anzahl": anzahl} for code, name, anzahl in verteilung(liste)
        ],
        "repos": [item.as_dict() for item in liste],
    }
    return json.dumps(daten, indent=2, ensure_ascii=False, sort_keys=True)
