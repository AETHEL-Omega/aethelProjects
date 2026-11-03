"""Register-Abgleich — fünf Register, von denen keines Wahrheit ist.

Im Workspace führen fünf Stellen je ihre eigene Liste der Projekte:

1. das workspace-manifest (``projects.yaml``),
2. der aethelProjects-Scan (``scan --json``),
3. die Projektprofile ``.aix/project-profile.json`` in einzelnen Repo-Ordnern,
4. die AIX-Aufträge (``~/.aix/auftraege/auftraege.jsonl``),
5. die GitHub-Organisation.

Dieses Modul gleicht 1–4 gegeneinander ab und meldet Drift. Es ist strikt lesend:
kein Netz (die GitHub-Organisation wird nicht abgefragt), kein Git-Aufruf, keine
Schreibzugriffe. Verglichen wird ausschließlich über den **Repo-Namen**
(case-sensitiv) — Namen sind keine Projektidentität. Dass der Abgleich nur über
Namen läuft, ist selbst der Befund: eine Produkt-ID fehlt.
"""

from __future__ import annotations

import json
import os
import time
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .fsutil import is_skipped
from .models import ManifestEntry

#: Standardort der AIX-Aufträge.
DEFAULT_AUFTRAEGE = Path.home() / ".aix" / "auftraege" / "auftraege.jsonl"

#: Schlüssel eines Auftrags, in denen der Repo-Bezug stehen kann (in dieser Rangfolge).
REPO_REF_KEYS = ("repo", "projekt", "project", "pfad", "path", "ziel")

#: Schlüssel eines Projektprofils, die zusätzlich zum Ordnernamen einen Repo-Namen tragen können.
PROFILE_NAME_KEYS = ("name", "id", "projekt", "repo")

#: Relativer Pfad des Projektprofils in einem Repo-Ordner.
PROFILE_RELPATH = Path(".aix") / "project-profile.json"

#: Höchstzahl der Einträge je Kategorie im Markdown.
MAX_LIST = 50

#: Schlusssatz — nur bei vorhandener Drift.
CLOSING = "Kein Register ist Wahrheit; Produkt-ID fehlt."

#: Kategorien der Drift: (Feldname, Überschrift im Markdown).
CATEGORIES: tuple[tuple[str, str], ...] = (
    ("missing_in_manifest", "Im Scan, aber nicht im Manifest"),
    ("dead_manifest_entries", "Im Manifest, aber nicht im Scan"),
    ("unregistered_worktrees", "Worktrees ohne Manifest-Eintrag"),
    ("profiles_without_manifest", "Projektprofile ohne Manifest-Eintrag"),
    ("profiles_without_repo", "Projektprofile ohne Repo im Scan"),
    ("auftraege_unknown_repos", "Aufträge mit unbekanntem Repo"),
)

#: Zähler: (Schlüssel in ``counts``, Beschriftung in der Tabelle).
COUNT_LABELS: tuple[tuple[str, str], ...] = (
    ("scan_repos", "Scan: Repos"),
    ("scan_worktrees", "Scan: Worktrees"),
    ("manifest_entries", "Manifest: Einträge"),
    ("profiles", "Projektprofile"),
    ("auftraege_lines", "Aufträge: Zeilen"),
    ("auftraege_parsed", "Aufträge: gelesen"),
)

_SECONDS_PER_DAY = 86_400


@dataclass(frozen=True)
class RegisterDrift:
    """Der Befund des Abgleichs. Alle Listen sind sortiert und ohne Duplikate.

    ``counts["scan_repos"]`` zählt Scan-Einträge **ohne** Worktrees,
    ``counts["scan_worktrees"]`` die Scan-Einträge mit ``is_worktree=True``.
    """

    #: Repos im Scan ohne Manifest-Eintrag (keine Worktrees).
    missing_in_manifest: tuple[str, ...] = ()
    #: Manifest-Namen ohne Repo (oder Worktree) im Scan.
    dead_manifest_entries: tuple[str, ...] = ()
    #: Scan-Einträge mit ``is_worktree=True``, deren Name nicht im Manifest steht.
    unregistered_worktrees: tuple[str, ...] = ()
    #: Profil-Ordner, deren Namen das Manifest nicht kennt.
    profiles_without_manifest: tuple[str, ...] = ()
    #: Profil-Ordner, deren Namen der Scan nicht kennt.
    profiles_without_repo: tuple[str, ...] = ()
    #: Repo-Bezüge aus den Aufträgen, die weder Scan noch Manifest kennen.
    auftraege_unknown_repos: tuple[str, ...] = ()
    #: Alter der Manifest-Datei in vollen Tagen (aus der mtime), sonst ``None``.
    manifest_age_days: int | None = None
    counts: dict[str, int] = field(default_factory=dict)

    @property
    def has_drift(self) -> bool:
        """Ist mindestens eine Kategorie nicht leer?"""
        return any(getattr(self, name) for name, _title in CATEGORIES)

    def as_dict(self) -> dict[str, Any]:
        """Serialisierbare Darstellung (Tupel werden zu Listen)."""
        return {
            "missing_in_manifest": list(self.missing_in_manifest),
            "dead_manifest_entries": list(self.dead_manifest_entries),
            "unregistered_worktrees": list(self.unregistered_worktrees),
            "profiles_without_manifest": list(self.profiles_without_manifest),
            "profiles_without_repo": list(self.profiles_without_repo),
            "auftraege_unknown_repos": list(self.auftraege_unknown_repos),
            "manifest_age_days": self.manifest_age_days,
            "counts": dict(self.counts),
        }


# --------------------------------------------------------------------------- Laden


def load_scan(path: Path) -> list[dict]:
    """Liest den Scan-Snapshot (``scan --json``) und gibt die ``repos``-Liste zurück.

    :raises FileNotFoundError: Datei fehlt — mit Hinweis, wie sie erzeugt wird
    :raises ValueError: kein JSON oder kein Scan-Snapshot (``repos`` fehlt)
    """
    snapshot_path = Path(path)
    if not snapshot_path.is_file():
        raise FileNotFoundError(
            f"Scan-Snapshot nicht gefunden: {snapshot_path} "
            f"(erzeugen mit: aethel-projects scan --json {snapshot_path})"
        )
    try:
        document = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise ValueError(f"Scan-Snapshot ist kein gültiges JSON: {snapshot_path} ({exc})") from exc
    if not isinstance(document, dict) or not isinstance(document.get("repos"), list):
        raise ValueError(f"Kein Scan-Snapshot (Schlüssel 'repos' fehlt): {snapshot_path}")
    return [repo for repo in document["repos"] if isinstance(repo, dict)]


def _read_profile(folder: Path) -> dict | None:
    """Das Projektprofil eines Ordners — ``None`` bei fehlender, kaputter oder falsch geformter Datei."""
    profile_path = folder / PROFILE_RELPATH
    if not profile_path.is_file():
        return None
    try:
        document = json.loads(profile_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return document if isinstance(document, dict) else None


def _skip_dir(name: str) -> bool:
    return name.startswith(".") or is_skipped(name)


def find_profiles(root: Path, max_depth: int = 2) -> dict[str, dict]:
    """Findet ``.aix/project-profile.json`` unterhalb von ``root``.

    Schlüssel ist der **Name des Repo-Ordners**. ``max_depth`` zählt Ordnerebenen
    unter ``root`` (``root/repo`` = 1, ``root/gruppe/repo`` = 2); ``root`` selbst
    wird nicht geprüft. Versteckte Ordner sowie ``node_modules``, ``target``,
    ``build`` und weitere Build-/Worktree-Verzeichnisse (``fsutil.is_skipped``)
    werden nicht betreten. Ungültiges JSON oder ein Profil, das kein Objekt ist,
    wird übersprungen. Bei gleichem Ordnernamen gewinnt der flachere, dann der
    alphabetisch frühere Pfad.
    """
    base = Path(root)
    if max_depth < 1 or not base.is_dir():
        return {}

    candidates: list[tuple[int, str, str, dict]] = []
    for dirpath, dirnames, _filenames in os.walk(base, topdown=True, onerror=lambda _e: None):
        folder = Path(dirpath)
        depth = len(folder.relative_to(base).parts)
        # Pruning: nur betreten, was noch innerhalb der Tiefe liegt und nicht ausgeschlossen ist.
        dirnames[:] = sorted(d for d in dirnames if not _skip_dir(d)) if depth < max_depth else []
        if depth == 0:
            continue
        profile = _read_profile(folder)
        if profile is not None:
            candidates.append((depth, str(folder), folder.name, profile))

    found: dict[str, dict] = {}
    for _depth, _path, name, profile in sorted(candidates, key=lambda c: (c[0], c[1])):
        found.setdefault(name, profile)
    return found


def load_auftraege(path: Path | None) -> tuple[list[dict], int]:
    """Liest ``auftraege.jsonl`` zeilenweise.

    Gibt ``(geparste Auftraege, Zahl der nicht leeren Zeilen)`` zurück. Kaputte
    Zeilen und Zeilen, die kein JSON-Objekt sind, zählen mit, werden aber nicht
    geparst. ``None`` oder eine fehlende/unlesbare Datei ergibt ``([], 0)``.
    """
    if path is None:
        return [], 0
    source = Path(path)
    if not source.is_file():
        return [], 0

    parsed: list[dict] = []
    lines = 0
    try:
        with source.open(encoding="utf-8", errors="replace") as handle:
            for raw in handle:
                text = raw.strip()
                if not text:
                    continue
                lines += 1
                try:
                    document = json.loads(text)
                except ValueError:
                    continue
                if isinstance(document, dict):
                    parsed.append(document)
    except OSError:
        return [], 0
    return parsed, lines


# --------------------------------------------------------------------------- Namen


def _name_from(value: object) -> str | None:
    """Repo-Name aus einem Wert: bei Pfaden/URLs der letzte Bestandteil.

    Freitext (Leerzeichen, aber kein ``/``) ist kein Repo-Name und ergibt ``None``.
    """
    if not isinstance(value, str):
        return None
    text = value.strip().replace("\\", "/").rstrip("/")
    if not text:
        return None
    if "/" not in text and any(char.isspace() for char in text):
        return None
    name = text.rsplit("/", 1)[-1].strip()
    if name in {"", ".", ".."}:
        return None
    return name


def repo_ref(auftrag: dict) -> str | None:
    """Der Repo-Name, auf den sich ein Auftrag bezieht — oder ``None``.

    Geprüft werden :data:`REPO_REF_KEYS` in Rangfolge; der erste brauchbare Wert
    gewinnt. Pfade (``/a/b/repo/``) und URLs liefern den letzten Bestandteil.
    Fehlende Schlüssel, Nicht-Strings und leere Werte werden übersprungen.
    """
    if not isinstance(auftrag, dict):
        return None
    for key in REPO_REF_KEYS:
        name = _name_from(auftrag.get(key))
        if name:
            return name
    return None


def _profile_names(folder: str, profile: dict) -> set[str]:
    """Alle Namen, unter denen ein Profil gelten kann: Ordnername plus ``name``/``id``/``projekt``/``repo``."""
    names = {folder}
    for key in PROFILE_NAME_KEYS:
        declared = _name_from(profile.get(key)) if isinstance(profile, dict) else None
        if declared:
            names.add(declared)
    return names


def _manifest_age_days(path: Path | None) -> int | None:
    if path is None:
        return None
    try:
        mtime = Path(path).stat().st_mtime
    except OSError:
        return None
    return max(0, int((time.time() - mtime) // _SECONDS_PER_DAY))


# --------------------------------------------------------------------------- Abgleich


def reconcile(
    scan_repos: Iterable[dict],
    manifest: dict[str, ManifestEntry],
    profiles: dict[str, dict],
    auftraege: list[dict],
    *,
    manifest_path: Path | None = None,
    auftraege_lines: int = 0,
) -> RegisterDrift:
    """Gleicht Scan, Manifest, Projektprofile und Aufträge über den Repo-Namen ab.

    * Ein Name gilt als im Scan bekannt, wenn *irgendein* Scan-Eintrag (auch ein
      Worktree) ihn trägt.
    * Ein Profil gilt als im Manifest bzw. im Scan bekannt, wenn sein Ordnername
      **oder** ein deklarierter Name (``name``/``id``/``projekt``/``repo``) dort
      steht; gemeldet wird es unter dem Ordnernamen.
    * Aufträge ohne erkennbaren Repo-Bezug werden nicht gemeldet.
    """
    entries = [
        repo for repo in scan_repos
        if isinstance(repo, dict) and isinstance(repo.get("name"), str) and repo["name"]
    ]
    worktrees = [repo for repo in entries if repo.get("is_worktree") is True]
    plain = [repo for repo in entries if repo.get("is_worktree") is not True]

    scan_names = {repo["name"] for repo in entries}
    manifest_names = set(manifest)

    missing = sorted({repo["name"] for repo in plain} - manifest_names)
    dead = sorted(manifest_names - scan_names)
    unregistered = sorted({repo["name"] for repo in worktrees} - manifest_names)

    without_manifest = sorted(
        folder for folder, profile in profiles.items()
        if not _profile_names(folder, profile) & manifest_names
    )
    without_repo = sorted(
        folder for folder, profile in profiles.items()
        if not _profile_names(folder, profile) & scan_names
    )

    refs = {ref for ref in (repo_ref(a) for a in auftraege) if ref}
    unknown = sorted(refs - scan_names - manifest_names)

    return RegisterDrift(
        missing_in_manifest=tuple(missing),
        dead_manifest_entries=tuple(dead),
        unregistered_worktrees=tuple(unregistered),
        profiles_without_manifest=tuple(without_manifest),
        profiles_without_repo=tuple(without_repo),
        auftraege_unknown_repos=tuple(unknown),
        manifest_age_days=_manifest_age_days(manifest_path),
        counts={
            "scan_repos": len(plain),
            "scan_worktrees": len(worktrees),
            "manifest_entries": len(manifest),
            "profiles": len(profiles),
            "auftraege_lines": max(auftraege_lines, len(auftraege)),
            "auftraege_parsed": len(auftraege),
        },
    )


# --------------------------------------------------------------------------- Ausgabe


def render_markdown(drift: RegisterDrift) -> str:
    """Der Abgleich als Markdown: Zählertabelle, je Kategorie eine Liste, Schlusssatz bei Drift."""
    lines = [
        "# Register-Abgleich",
        "",
        "Nur lesend; die GitHub-Organisation wird nicht abgefragt.",
        "",
        "| Register | Anzahl |",
        "|---|---:|",
    ]
    for key, label in COUNT_LABELS:
        lines.append(f"| {label} | {drift.counts.get(key, 0)} |")
    age = "-" if drift.manifest_age_days is None else str(drift.manifest_age_days)
    lines.append(f"| Manifest: Alter in Tagen | {age} |")

    for name, title in CATEGORIES:
        names: tuple[str, ...] = getattr(drift, name)
        lines += ["", f"## {title} ({len(names)})", ""]
        if not names:
            lines.append("Keine.")
            continue
        lines.extend(f"- `{item}`" for item in names[:MAX_LIST])
        if len(names) > MAX_LIST:
            lines.append(f"- … und {len(names) - MAX_LIST} weitere")

    if drift.has_drift:
        lines += ["", CLOSING]
    return "\n".join(lines)


def render_json(drift: RegisterDrift) -> str:
    """Der Abgleich als JSON (Schlüssel sortiert, Umlaute unverändert)."""
    return json.dumps(drift.as_dict(), indent=2, ensure_ascii=False, sort_keys=True)
