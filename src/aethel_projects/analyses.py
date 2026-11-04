"""Versionierte Ablage für Projektanalysen — der Ordner ``analysen/`` im Repo.

aethelProjects hält die Ergebnisse seiner Analysen **im Repo** und nicht im Chat:
Markdown-Dateien unter ``analysen/<YYYY-MM-DD>/*.md`` plus drei maschinenlesbare
Register, die dieses Modul liest und (eines davon) pflegt:

* ``INDEX.json`` (``aethel.projects.analysen/v1``) — Verzeichnis aller
  registrierten Analysen mit Titel, Datum, Scope und **SHA-256** der Datei.
* ``vorschlaege.json`` (``aethel.projects.vorschlaege/v1``) — Projektvorschläge,
  die aus den Analysen folgen (Komponente@Vertrag, Ebene, Stufe, was sie hebt).
* ``kreislaeufe.json`` (``aethel.projects.kreislaeufe/v1``) — Regelkreise der
  Fabrik (Sollwert, Sensor, Vergleicher, Stellglied) und was ihnen zum
  Schließen fehlt.

Garantien:

* **Nur ``analysen/``.** Alle Funktionen nehmen ``base`` (den Pfad des
  ``analysen/``-Ordners); nichts außerhalb davon wird gelesen oder geschrieben.
  Pfadflucht (``..``, Symlinks) wird über ``resolve`` erkannt und abgelehnt.
* **Genau eine schreibende Funktion:** :func:`register`. Sie schreibt
  ausschließlich ``INDEX.json`` — deterministisch und atomar (Temp-Datei im
  selben Ordner, dann ``os.replace``). Die Analysen selbst werden nie verändert.
* **Fail-closed.** Falsches Schema, unbekannte Felder, doppelte IDs, ungültige
  Datums-/Hash-/Statuswerte führen zu ``ValueError`` mit klarer Meldung — es wird
  nichts geraten und nichts stillschweigend verworfen. Schema v1 ist geschlossen;
  neue Felder erfordern v2.
* **Belegbar.** :func:`show` prüft die SHA-256 und warnt, wenn die Datei seit der
  Registrierung verändert wurde.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import tempfile
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

#: Schema-Kennungen der drei Register.
SCHEMA_INDEX = "aethel.projects.analysen/v1"
SCHEMA_PROPOSALS = "aethel.projects.vorschlaege/v1"
SCHEMA_LOOPS = "aethel.projects.kreislaeufe/v1"

#: Dateinamen der Register innerhalb von ``analysen/``.
INDEX_FILE = "INDEX.json"
PROPOSALS_FILE = "vorschlaege.json"
LOOPS_FILE = "kreislaeufe.json"

#: Erlaubte Werte.
SCOPES = ("workspace", "aethelProjects", "fabrik", "firma", "stack")
PROPOSAL_STATUS = ("vorgeschlagen", "in-arbeit", "existiert")
LOOP_EBENEN = ("E0", "E1", "E2", "E3", "E4", "E5", "E6", "META")
LOOP_STATUS = ("offen", "teilweise", "geschlossen")

#: Warnzeile, die :func:`show` voranstellt, wenn die Prüfsumme nicht mehr stimmt.
CHANGED_WARNING = "> Warnung: Datei verändert seit Registrierung"

_KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_UMLAUTE = str.maketrans(
    {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "ae", "Ö": "oe", "Ü": "ue"}
)


# ---------------------------------------------------------------------------
# Datenmodelle
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AnalysisEntry:
    """Ein registrierter Analysebericht (Zeile in ``INDEX.json``)."""

    id: str
    date: str
    title: str
    path: str  # relativ zu analysen/, POSIX-Notation
    sha256: str
    scope: str
    summary: str
    tags: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "date": self.date,
            "title": self.title,
            "path": self.path,
            "sha256": self.sha256,
            "scope": self.scope,
            "summary": self.summary,
            "tags": list(self.tags),
        }


@dataclass(frozen=True)
class AnalysesIndex:
    """Der gesamte Inhalt von ``INDEX.json``."""

    entries: tuple[AnalysisEntry, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA_INDEX,
            "entries": [entry.as_dict() for entry in self.entries],
        }


@dataclass(frozen=True)
class Proposal:
    """Ein Projektvorschlag aus ``vorschlaege.json``."""

    id: str
    name: str
    zweck: str
    komponente: str
    vertrag: str
    ebene: str
    stufe: int
    status: str  # "vorgeschlagen" | "in-arbeit" | "existiert"
    hebt: tuple[str, ...] = ()
    bestand: str = ""
    quelle: str = ""  # Analyse-ID, aus der der Vorschlag folgt

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "zweck": self.zweck,
            "komponente": self.komponente,
            "vertrag": self.vertrag,
            "ebene": self.ebene,
            "stufe": self.stufe,
            "hebt": list(self.hebt),
            "bestand": self.bestand,
            "status": self.status,
            "quelle": self.quelle,
        }


@dataclass(frozen=True)
class Loop:
    """Ein Regelkreis aus ``kreislaeufe.json``."""

    id: str
    name: str
    ebene: str  # "E0".."E6" | "META"
    status: str  # "offen" | "teilweise" | "geschlossen"
    takt: str = ""
    sollwert: str = ""
    sensor: str = ""
    vergleicher: str = ""
    stellglied: str = ""
    stoergroessen: tuple[str, ...] = ()
    besitzer: str = ""  # Komponente, der der Kreis gehört
    fehlt: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "ebene": self.ebene,
            "takt": self.takt,
            "sollwert": self.sollwert,
            "sensor": self.sensor,
            "vergleicher": self.vergleicher,
            "stellglied": self.stellglied,
            "stoergroessen": list(self.stoergroessen),
            "besitzer": self.besitzer,
            "status": self.status,
            "fehlt": list(self.fehlt),
        }


# ---------------------------------------------------------------------------
# Pfade
# ---------------------------------------------------------------------------


def default_base() -> Path:
    """``analysen/`` an der Repo-Wurzel, relativ zu dieser Moduldatei ermittelt."""
    return Path(__file__).resolve().parents[2] / "analysen"


def _root(base: Path | str | None) -> Path:
    """Der aufgelöste ``analysen/``-Ordner (``None`` → :func:`default_base`)."""
    return (default_base() if base is None else Path(base)).resolve()


def _today() -> str:
    """Heutiges Datum als ``YYYY-MM-DD`` (eigene Funktion, damit testbar)."""
    return _dt.date.today().isoformat()


# ---------------------------------------------------------------------------
# Validierung (gemeinsam für alle drei Register)
# ---------------------------------------------------------------------------


def _read_document(file: Path, schema: str, list_key: str) -> list[Any] | None:
    """Liest ein Register und gibt dessen Liste zurück; ``None`` wenn die Datei fehlt."""
    if not file.exists():
        return None
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError(f"{file.name}: kein gültiges JSON ({error})") from error
    if not isinstance(data, dict):
        raise ValueError(f"{file.name}: JSON-Objekt erwartet")
    found = data.get("schema")
    if found != schema:
        raise ValueError(f"{file.name}: falsches Schema {found!r}, erwartet {schema!r}")
    unknown = sorted(set(data) - {"schema", list_key})
    if unknown:
        raise ValueError(f"{file.name}: unbekannte Felder {unknown}")
    items = data.get(list_key)
    if not isinstance(items, list):
        raise ValueError(f"{file.name}: Feld {list_key!r} muss eine Liste sein")
    return items


def _check_keys(
    obj: Any, ctx: str, required: frozenset[str], optional: frozenset[str]
) -> dict[str, Any]:
    if not isinstance(obj, dict):
        raise ValueError(f"{ctx}: Objekt erwartet")
    missing = sorted(required - set(obj))
    if missing:
        raise ValueError(f"{ctx}: Pflichtfelder fehlen {missing}")
    unknown = sorted(set(obj) - required - optional)
    if unknown:
        raise ValueError(f"{ctx}: unbekannte Felder {unknown}")
    return obj


def _text(obj: dict[str, Any], key: str, ctx: str, *, required: bool = True) -> str:
    value = obj.get(key, "")
    if not isinstance(value, str):
        raise ValueError(f"{ctx}: Feld {key!r} muss ein Text sein")
    if required and not value.strip():
        raise ValueError(f"{ctx}: Feld {key!r} darf nicht leer sein")
    return value


def _choice(obj: dict[str, Any], key: str, ctx: str, allowed: tuple[str, ...]) -> str:
    value = _text(obj, key, ctx)
    if value not in allowed:
        raise ValueError(f"{ctx}: Feld {key!r} = {value!r} ungültig, erlaubt {list(allowed)}")
    return value


def _texts(obj: dict[str, Any], key: str, ctx: str) -> tuple[str, ...]:
    value = obj.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{ctx}: Feld {key!r} muss eine Liste von Texten sein")
    return tuple(value)


def _check_unique(file: str, kind: str, ids: list[str]) -> None:
    seen: set[str] = set()
    for item_id in ids:
        if item_id in seen:
            raise ValueError(f"{file}: doppelte {kind}-ID {item_id!r}")
        seen.add(item_id)


def _is_date(value: str) -> bool:
    """Ist ``value`` ein existierendes Datum im Format ``YYYY-MM-DD``?"""
    if not _DATE.match(value):
        return False
    try:
        _dt.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _check_date(value: str, ctx: str) -> str:
    if not _DATE.match(value):
        raise ValueError(f"{ctx}: Datum {value!r} ist nicht im Format YYYY-MM-DD")
    if not _is_date(value):
        raise ValueError(f"{ctx}: Datum {value!r} existiert nicht")
    return value


def _check_relative(value: str, ctx: str) -> str:
    """Ein Pfad im Register muss relativ und frei von ``..`` sein."""
    posix = PurePosixPath(value)
    if posix.is_absolute() or ".." in posix.parts or not posix.parts or "\\" in value:
        raise ValueError(f"{ctx}: Pfad {value!r} muss relativ zu analysen/ sein (ohne '..')")
    return value


# ---------------------------------------------------------------------------
# Lesen
# ---------------------------------------------------------------------------

_ENTRY_REQUIRED = frozenset({"id", "date", "title", "path", "sha256", "scope", "summary"})
_ENTRY_OPTIONAL = frozenset({"tags"})


def _parse_entry(raw: Any, position: int) -> AnalysisEntry:
    label = f"{INDEX_FILE}: entries[{position}]"
    obj = _check_keys(raw, label, _ENTRY_REQUIRED, _ENTRY_OPTIONAL)
    entry_id = _text(obj, "id", label)
    ctx = f"{INDEX_FILE}: Eintrag {entry_id!r}"
    if not _KEBAB.match(entry_id):
        raise ValueError(f"{ctx}: ID muss kebab-case sein")
    sha = _text(obj, "sha256", ctx)
    if not _SHA256.match(sha):
        raise ValueError(f"{ctx}: sha256 {sha!r} ist kein 64-stelliger Hex-Wert")
    return AnalysisEntry(
        id=entry_id,
        date=_check_date(_text(obj, "date", ctx), ctx),
        title=_text(obj, "title", ctx),
        path=_check_relative(_text(obj, "path", ctx), ctx),
        sha256=sha,
        scope=_choice(obj, "scope", ctx, SCOPES),
        summary=_text(obj, "summary", ctx),
        tags=_texts(obj, "tags", ctx),
    )


def load_index(base: Path | None = None) -> AnalysesIndex:
    """Liest ``INDEX.json``. Fehlende Datei → leerer Index; falsches Schema → ``ValueError``."""
    items = _read_document(_root(base) / INDEX_FILE, SCHEMA_INDEX, "entries")
    if items is None:
        return AnalysesIndex()
    entries = tuple(_parse_entry(raw, position) for position, raw in enumerate(items))
    _check_unique(INDEX_FILE, "Analyse", [entry.id for entry in entries])
    return AnalysesIndex(entries=entries)


def _sort_entries(entries: Any) -> tuple[AnalysisEntry, ...]:
    """Datum absteigend, bei gleichem Datum nach ID aufsteigend."""
    by_id = sorted(entries, key=lambda entry: entry.id)
    return tuple(sorted(by_id, key=lambda entry: entry.date, reverse=True))


def list_entries(base: Path | None = None) -> tuple[AnalysisEntry, ...]:
    """Alle Einträge, neueste zuerst (Datum absteigend, dann ID)."""
    return _sort_entries(load_index(base).entries)


_PROPOSAL_REQUIRED = frozenset(
    {"id", "name", "zweck", "komponente", "vertrag", "ebene", "stufe", "status"}
)
_PROPOSAL_OPTIONAL = frozenset({"hebt", "bestand", "quelle"})


def _parse_proposal(raw: Any, position: int) -> Proposal:
    label = f"{PROPOSALS_FILE}: projects[{position}]"
    obj = _check_keys(raw, label, _PROPOSAL_REQUIRED, _PROPOSAL_OPTIONAL)
    proposal_id = _text(obj, "id", label)
    ctx = f"{PROPOSALS_FILE}: Vorschlag {proposal_id!r}"
    stufe = obj["stufe"]
    if isinstance(stufe, bool) or not isinstance(stufe, int) or stufe < 0:
        raise ValueError(f"{ctx}: Feld 'stufe' muss eine ganze Zahl >= 0 sein")
    return Proposal(
        id=proposal_id,
        name=_text(obj, "name", ctx),
        zweck=_text(obj, "zweck", ctx),
        komponente=_text(obj, "komponente", ctx),
        vertrag=_text(obj, "vertrag", ctx),
        ebene=_text(obj, "ebene", ctx),
        stufe=stufe,
        status=_choice(obj, "status", ctx, PROPOSAL_STATUS),
        hebt=_texts(obj, "hebt", ctx),
        bestand=_text(obj, "bestand", ctx, required=False),
        quelle=_text(obj, "quelle", ctx, required=False),
    )


def load_proposals(base: Path | None = None) -> tuple[Proposal, ...]:
    """Liest ``vorschlaege.json``. Fehlende Datei → leer; falsches Schema → ``ValueError``."""
    items = _read_document(_root(base) / PROPOSALS_FILE, SCHEMA_PROPOSALS, "projects")
    if items is None:
        return ()
    proposals = tuple(_parse_proposal(raw, position) for position, raw in enumerate(items))
    _check_unique(PROPOSALS_FILE, "Vorschlags", [proposal.id for proposal in proposals])
    _check_references(proposals, base)
    return proposals


def _check_references(proposals: tuple[Proposal, ...], base: Path | None) -> None:
    """``hebt`` darf nur auf vorhandene Vorschlags- oder Kreislauf-IDs zeigen."""
    known = {proposal.id for proposal in proposals}
    loops_file = _root(base) / LOOPS_FILE
    if loops_file.is_file():
        try:
            known |= {loop.id for loop in load_loops(base)}
        except ValueError:
            pass  # Kreisläufe werden an ihrer eigenen Stelle gemeldet
    for proposal in proposals:
        unknown = sorted(set(proposal.hebt) - known)
        if unknown:
            raise ValueError(
                f"{PROPOSALS_FILE}: Vorschlag {proposal.id!r} hebt unbekannte IDs: {', '.join(unknown)}"
            )


_LOOP_REQUIRED = frozenset({"id", "name", "ebene", "status"})
_LOOP_OPTIONAL = frozenset(
    {"takt", "sollwert", "sensor", "vergleicher", "stellglied", "stoergroessen", "besitzer", "fehlt"}
)


def _parse_loop(raw: Any, position: int) -> Loop:
    label = f"{LOOPS_FILE}: loops[{position}]"
    obj = _check_keys(raw, label, _LOOP_REQUIRED, _LOOP_OPTIONAL)
    loop_id = _text(obj, "id", label)
    ctx = f"{LOOPS_FILE}: Kreislauf {loop_id!r}"
    return Loop(
        id=loop_id,
        name=_text(obj, "name", ctx),
        ebene=_choice(obj, "ebene", ctx, LOOP_EBENEN),
        status=_choice(obj, "status", ctx, LOOP_STATUS),
        takt=_text(obj, "takt", ctx, required=False),
        sollwert=_text(obj, "sollwert", ctx, required=False),
        sensor=_text(obj, "sensor", ctx, required=False),
        vergleicher=_text(obj, "vergleicher", ctx, required=False),
        stellglied=_text(obj, "stellglied", ctx, required=False),
        stoergroessen=_texts(obj, "stoergroessen", ctx),
        besitzer=_text(obj, "besitzer", ctx, required=False),
        fehlt=_texts(obj, "fehlt", ctx),
    )


def load_loops(base: Path | None = None) -> tuple[Loop, ...]:
    """Liest ``kreislaeufe.json``. Fehlende Datei → leer; falsches Schema → ``ValueError``."""
    items = _read_document(_root(base) / LOOPS_FILE, SCHEMA_LOOPS, "loops")
    if items is None:
        return ()
    loops = tuple(_parse_loop(raw, position) for position, raw in enumerate(items))
    _check_unique(LOOPS_FILE, "Kreislauf", [loop.id for loop in loops])
    return loops


# ---------------------------------------------------------------------------
# Anzeigen mit Prüfsumme
# ---------------------------------------------------------------------------


def show(base: Path | None, entry_id: str) -> str:
    """Der Markdown-Inhalt einer Analyse.

    Stimmt die SHA-256 nicht mehr mit dem Index überein, steht
    :data:`CHANGED_WARNING` (und eine Leerzeile) vor dem Inhalt. Eine unbekannte
    ID führt zu ``KeyError``; ein Indexpfad außerhalb von ``base`` zu ``ValueError``.
    """
    root = _root(base)
    entry = next((e for e in load_index(root).entries if e.id == entry_id), None)
    if entry is None:
        raise KeyError(f"Unbekannte Analyse-ID: {entry_id}")
    file = (root / entry.path).resolve()
    if not file.is_relative_to(root):
        raise ValueError(f"Pfad {entry.path!r} von {entry.id!r} liegt außerhalb von {root}")
    if not file.is_file():
        raise FileNotFoundError(f"Analyse {entry.id!r}: Datei {entry.path!r} fehlt")
    data = file.read_bytes()
    text = data.decode("utf-8", errors="replace")
    if hashlib.sha256(data).hexdigest() != entry.sha256:
        return f"{CHANGED_WARNING}\n\n{text}"
    return text


# ---------------------------------------------------------------------------
# Registrieren — die einzige schreibende Funktion
# ---------------------------------------------------------------------------


def kebab_case(text: str) -> str:
    """``Projekt_Übersicht v2`` → ``projekt-uebersicht-v2`` (Umlaute werden umgeschrieben)."""
    text = unicodedata.normalize("NFKD", text.translate(_UMLAUTE))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _title_of(text: str, fallback: str) -> str:
    """Die erste ``# ``-Überschrift (außerhalb von Codeblöcken), sonst ``fallback``."""
    in_fence = False
    for line in text.lstrip("﻿").splitlines():
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if not in_fence and line.startswith("# ") and line[2:].strip():
            return line[2:].strip()
    return fallback


def _locate(root: Path, path: Path | str) -> Path:
    """Löst ``path`` auf (relativ: gegen das aktuelle Verzeichnis, sonst gegen ``root``)."""
    candidate = Path(path).expanduser()
    if not candidate.is_absolute() and not candidate.exists() and (root / candidate).exists():
        candidate = root / candidate
    return candidate.resolve()


def _write_index(root: Path, entries: tuple[AnalysisEntry, ...]) -> None:
    """Schreibt ``INDEX.json`` deterministisch und atomar."""
    document = AnalysesIndex(entries=_sort_entries(entries)).as_dict()
    payload = json.dumps(document, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    target = root / INDEX_FILE
    # mkstemp legt die Datei exklusiv an (O_EXCL, folgt keinem Symlink) und mit zufälligem Namen.
    handle, temp_name = tempfile.mkstemp(prefix=f".{INDEX_FILE}.", suffix=".tmp", dir=root)
    temp = Path(temp_name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
        os.replace(temp, target)
    except BaseException:
        temp.unlink(missing_ok=True)
        raise


def register(
    base: Path | None,
    path: Path | str,
    *,
    scope: str,
    summary: str,
    tags: tuple[str, ...] | list[str] = (),
    entry_id: str | None = None,
    date: str | _dt.date | None = None,
) -> AnalysisEntry:
    """Trägt eine Markdown-Analyse in ``INDEX.json`` ein (oder ersetzt den Eintrag).

    * ``path`` muss eine ``.md``-Datei **innerhalb** von ``base`` sein (nach
      ``resolve``, also auch gegen ``..`` und Symlinks); sonst ``ValueError``.
      Relative Pfade gelten gegen das aktuelle Verzeichnis, ersatzweise gegen ``base``.
    * Titel: erste ``# ``-Zeile, Fallback Dateiname. Prüfsumme: SHA-256 der Datei.
    * ``entry_id`` Default: kebab-case des Dateinamens ohne Endung.
    * ``date`` Default: Ordnername, wenn er ``YYYY-MM-DD`` ist, sonst heute.
    * Ein vorhandener Eintrag mit gleicher ID wird ersetzt.

    Geschrieben wird ausschließlich ``INDEX.json``.
    """
    root = _root(base)
    if scope not in SCOPES:
        raise ValueError(f"Scope {scope!r} ungültig, erlaubt {list(SCOPES)}")
    summary_text = " ".join(summary.split())
    if not summary_text:
        raise ValueError("Zusammenfassung darf nicht leer sein")
    tag_list: list[str] = []
    for tag in tags:
        cleaned = tag.strip()
        if cleaned and cleaned not in tag_list:
            tag_list.append(cleaned)

    file = _locate(root, path)
    if not file.is_relative_to(root):
        raise ValueError(f"{file} liegt außerhalb von {root} — nur Dateien unter analysen/ erlaubt")
    if file.suffix.lower() != ".md":
        raise ValueError(f"{file.name}: nur Markdown-Dateien (.md) können registriert werden")
    if not file.is_file():
        raise FileNotFoundError(f"{file} existiert nicht")
    relative = file.relative_to(root)

    identifier = entry_id if entry_id is not None else kebab_case(file.stem)
    if not _KEBAB.match(identifier):
        raise ValueError(f"ID {identifier!r} muss kebab-case sein (a-z, 0-9, Bindestriche)")

    if date is None:
        folder = relative.parent.name
        chosen = folder if _is_date(folder) else _today()
    else:
        chosen = date.isoformat() if isinstance(date, _dt.date) else date
    _check_date(chosen, "register")

    data = file.read_bytes()
    entry = AnalysisEntry(
        id=identifier,
        date=chosen,
        title=_title_of(data.decode("utf-8", errors="replace"), file.name),
        path=relative.as_posix(),
        sha256=hashlib.sha256(data).hexdigest(),
        scope=scope,
        summary=summary_text,
        tags=tuple(tag_list),
    )
    kept = tuple(e for e in load_index(root).entries if e.id != entry.id)
    _write_index(root, kept + (entry,))
    return entry


# ---------------------------------------------------------------------------
# Darstellung
# ---------------------------------------------------------------------------


def _cell(value: object) -> str:
    """Ein Tabellenfeld: ``|`` maskiert, Zeilenumbrüche geglättet, leer → ``-``."""
    text = " ".join(str(value).split()).replace("|", "\\|")
    return text or "-"


def _table(headers: tuple[str, ...], rows: list[tuple[object, ...]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(_cell(value) for value in row) + " |" for row in rows)
    return "\n".join(lines) + "\n"


def render_index_markdown(entries: tuple[AnalysisEntry, ...] | list[AnalysisEntry]) -> str:
    """Tabelle: Datum, ID, Titel, Scope, Zusammenfassung (Reihenfolge wie übergeben)."""
    return _table(
        ("Datum", "ID", "Titel", "Scope", "Zusammenfassung"),
        [(e.date, e.id, e.title, e.scope, e.summary) for e in entries],
    )


def render_proposals_markdown(proposals: tuple[Proposal, ...] | list[Proposal]) -> str:
    """Tabelle: ID, Name, Zweck, Komponente@Vertrag, Ebene, Stufe, hebt, Status."""
    return _table(
        ("ID", "Name", "Zweck", "Komponente@Vertrag", "Ebene", "Stufe", "hebt", "Status"),
        [
            (
                p.id,
                p.name,
                p.zweck,
                f"{p.komponente}@{p.vertrag}",
                p.ebene,
                p.stufe,
                ", ".join(p.hebt),
                p.status,
            )
            for p in proposals
        ],
    )


def render_loops_markdown(loops: tuple[Loop, ...] | list[Loop]) -> str:
    """Tabelle: ID, Ebene, Takt, Sollwert, Sensor, Vergleicher, Stellglied, Status, fehlt."""
    return _table(
        (
            "ID",
            "Ebene",
            "Takt",
            "Sollwert",
            "Sensor",
            "Vergleicher",
            "Stellglied",
            "Status",
            "fehlt",
        ),
        [
            (
                loop.id,
                loop.ebene,
                loop.takt,
                loop.sollwert,
                loop.sensor,
                loop.vergleicher,
                loop.stellglied,
                loop.status,
                "; ".join(loop.fehlt),
            )
            for loop in loops
        ],
    )


def render_index_json(entries: tuple[AnalysisEntry, ...] | list[AnalysisEntry]) -> dict[str, Any]:
    """Dieselbe Form wie ``INDEX.json`` (``schema`` + ``entries``)."""
    return {"schema": SCHEMA_INDEX, "entries": [entry.as_dict() for entry in entries]}


def render_proposals_json(proposals: tuple[Proposal, ...] | list[Proposal]) -> dict[str, Any]:
    """Dieselbe Form wie ``vorschlaege.json`` (``schema`` + ``projects``)."""
    return {"schema": SCHEMA_PROPOSALS, "projects": [p.as_dict() for p in proposals]}


def render_loops_json(loops: tuple[Loop, ...] | list[Loop]) -> dict[str, Any]:
    """Dieselbe Form wie ``kreislaeufe.json`` (``schema`` + ``loops``)."""
    return {"schema": SCHEMA_LOOPS, "loops": [loop.as_dict() for loop in loops]}


# ---------------------------------------------------------------------------
# Kennzahlen
# ---------------------------------------------------------------------------


def summary(base: Path | None = None) -> dict[str, int]:
    """Zähler über alle drei Register."""
    loops = load_loops(base)
    return {
        "analyses": len(load_index(base).entries),
        "proposals": len(load_proposals(base)),
        "loops_total": len(loops),
        "loops_offen": sum(1 for loop in loops if loop.status == "offen"),
        "loops_teilweise": sum(1 for loop in loops if loop.status == "teilweise"),
        "loops_geschlossen": sum(1 for loop in loops if loop.status == "geschlossen"),
    }
