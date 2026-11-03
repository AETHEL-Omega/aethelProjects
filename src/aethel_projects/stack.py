"""Schichtenkarte des Gesamtstacks: welches Repo trägt welche Stack-Schicht.

aethelProjects beantwortet hier die Frage, die weder die Fabrik- noch die
Portfolio-Sicht beantwortet: **Welche Schichten des Stacks haben ein eigenes
Repo — und welche sind leer?** Der Stack reicht von S0 (Rechenmodell) bis S17
(Entscheidung/Doku); jedes Repo wird genau einer Schicht zugeordnet, mit
Herkunft (eigen/fremd/unklar) und Reife.

Es wird nichts erfunden: jede Zuordnung nennt die Regel, die getroffen hat, und
bleibt ohne Beleg ``SX`` (unbestimmt, Konfidenz ``low``). Die Regeln in dieser
Reihenfolge — die erste, die trifft, gewinnt:

1. **Herkunft** — fremd bei Fork-Kategorie oder fremdem Remote ohne
   AETHEL-Namenspräfix; eigen sonst; ohne Remote und Namensindiz unklar.
2. **Namensregeln** (:data:`NAME_RULES`) — Schlüsselwörter im Repo-Namen.
3. **Dateimarker** im Repo (nur mit ``repo_path``; flach, höchstens zwei
   Verzeichnisebenen, ohne versteckte und Build-Verzeichnisse).
4. Sonst ``SX``.

Strikt lesend: es werden nur Dateien gelesen, nie geschrieben, und kein
Unterprozess gestartet.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .fsutil import is_skipped
from .models import RepoReport

#: Die Schichten des Gesamtstacks (Code, Name) in Stapelreihenfolge. ``SX`` ist
#: kein Stack-Schicht, sondern der Sammelplatz für alles ohne Beleg.
LAYERS: tuple[tuple[str, str], ...] = (
    ("S0", "Rechenmodell/Silizium-Simulation"),
    ("S1", "Firmware"),
    ("S2", "Kernel/OS"),
    ("S3", "Isolation/Hypervisor"),
    ("S4", "Systemdienste/Zustand/Rechte"),
    ("S5", "Komponentenlaufzeit/Agenten"),
    ("S6", "Sprache/Compiler/Toolchain"),
    ("S7", "Build/Release"),
    ("S8", "Daten/Wissen"),
    ("S9", "Kommunikation/Verbund"),
    ("S10", "Plattform-SDK/Bibliothek"),
    ("S11", "Anwendung"),
    ("S12", "Oberfläche/Cockpit"),
    ("S13", "Sicherheit/Identität"),
    ("S14", "Beobachtbarkeit"),
    ("S15", "Qualität/Test/Eval"),
    ("S16", "Distribution"),
    ("S17", "Entscheidung/Doku/Wissen-Text"),
    ("SX", "unbestimmt"),
)

#: Code → Name.
LAYER_NAMES: dict[str, str] = dict(LAYERS)

#: Sammelschicht für alles ohne Beleg.
UNDETERMINED = "SX"

_LAYER_INDEX = {code: index for index, (code, _name) in enumerate(LAYERS)}

#: Kategorien des Manifests, die ein Repo als fremd ausweisen.
FOREIGN_CATEGORIES = frozenset({"fork", "forks", "fremd", "vendor"})

#: Namenspräfixe (case-insensitiv), die ein Repo als eigen ausweisen.
OWN_NAME_PREFIXES = ("aethel", "aix", "omega", "din")

#: Remote-URLs, die auf ein eigenes Konto zeigen (``AETHEL-Omega/``, ``ManuelWilde/``).
_OWN_REMOTE = re.compile(r"(?:^|[/:@])(?:aethel-omega|manuelwilde)/", re.IGNORECASE)

#: Markenpräfixe, die in verschmolzenen Namen („aethelema“, „aethelbot“) vom
#: eigentlichen Schlüsselwort getrennt werden.
_BRAND_PREFIXES = ("aethel", "aix", "aider")

#: Namensregeln: ``(Schicht, Schlüsselwörter)``. **Erster Treffer gewinnt** —
#: Reihenfolge der Tupel und der Schlüsselwörter ist Teil des Vertrags.
#:
#: * Die zwei Mehrwort-Regeln stehen vorn, weil sonst das Teilwort gewinnt
#:   (``wissen`` → S8 statt ``wissen-text`` → S17; ``runtime`` → S4 statt
#:   ``agent-runtime`` → S5, die Komponentenlaufzeit).
#: * Vorrang laut Vorgabe: ``firmware`` → S1 (nicht S2), ``ledger`` → S4 (nicht
#:   S8), ``store`` → S11 und ``release`` → S7 (nicht S16).
#: * Mehrwort-Schlüssel (``-``/``_``) müssen als aufeinanderfolgende Wörter im
#:   Namen stehen. Schlüsselwörter ab sechs Zeichen gelten als Teilstring des
#:   Namens, kürzere nur als ganzes Wort (``ui`` trifft ``aethel-ui``, nicht
#:   ``build``; ``ema`` trifft ``aethelema``, nicht ``schema``).
NAME_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("S17", ("wissen-text",)),
    ("S5", ("agent-runtime",)),
    ("S0", ("memristor", "vchip", "quantum", "osxq", "pennylane", "helix",
            "bit_encodings", "photon", "silicon")),
    ("S1", ("firmware",)),
    ("S2", ("os", "kernel", "boot")),
    ("S3", ("container", "sandbox", "hypervisor", "vm")),
    ("S4", ("runtime", "aixd", "ledger", "state", "rechte", "registry", "landing", "gate")),
    ("S5", ("agent", "aix", "scripts", "factory", "worklane", "bot", "coder", "harness",
            "forge", "hydra")),
    ("S6", ("lang", "compiler", "toolchain", "lexer", "parser")),
    ("S7", ("release", "build", "ci", "manifest")),
    ("S8", ("omega", "wissen", "knowledge", "memory", "memoria", "atlas", "data")),
    ("S9", ("ema", "p2p", "mesh", "bridge", "bruecke", "net")),
    ("S10", ("sdk", "core", "design", "shells", "lib", "foundations")),
    ("S11", ("app", "player", "reader", "radio", "store", "lab", "browser", "terminal")),
    ("S12", ("ui", "cockpit", "leitstand", "dashboard", "view")),
    ("S13", ("auth", "identity", "secrets", "keychain", "defense", "security")),
    ("S14", ("metrics", "telemetry", "observ", "trace", "analytics")),
    ("S15", ("test", "bench", "eval", "analyzer", "projects", "audit")),
    ("S16", ("dist",)),
    ("S17", ("docs", "rfc", "plan", "consultant", "canon")),
)

#: Ab dieser Länge gilt ein Schlüsselwort als Teilstring des Namens.
_SUBSTRING_MIN_LENGTH = 6

#: Beugungen, die ein kurzes Schlüsselwort als ganzes Wort mitnimmt
#: (``apps``, ``gated``, ``viewer``, ``testing``). Schlüssel bis zwei Zeichen
#: (``os``, ``ci``, ``ui``, ``vm``) gelten nur exakt.
_INFLECTIONS = ("s", "d", "ed", "er", "ers", "ing")

#: Belegsuche im Repo: Tiefe, Dateien, Lesegrenze (read-only und billig).
_MARKER_MAX_DEPTH = 2
_MARKER_MAX_FILES = 4000
_MARKER_MAX_RUST_FILES = 400
_MARKER_MAX_READ_BYTES = 256 * 1024

_NO_STD = re.compile(r"^\s*#!\[no_std\]", re.MULTILINE)
_CARGO_WORKSPACE = re.compile(r"^\s*\[workspace\]", re.MULTILINE)

_CAMEL_LOWER_UPPER = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
_CAMEL_ACRONYM = re.compile(r"(?<=[A-Z])(?=[A-Z][a-z])")
_NON_ALNUM = re.compile(r"[^A-Za-z0-9]+")
_KEY_SEPARATOR = re.compile(r"[-_]")


@dataclass(frozen=True)
class LayerAssignment:
    """Die Zuordnung eines Repos zu einer Stack-Schicht — samt Beleg."""

    repo: str
    layer: str  # Code, "S0" … "S17" | "SX"
    layer_name: str
    origin: str  # "eigen" | "fremd" | "unklar"
    maturity_grade: str  # Reifegrad aus dem Scan oder "unbekannt"
    evidence: str  # welche Regel traf
    confidence: str  # "high" | "medium" | "low"

    def as_dict(self) -> dict[str, Any]:
        return {
            "repo": self.repo,
            "layer": self.layer,
            "layer_name": self.layer_name,
            "origin": self.origin,
            "maturity_grade": self.maturity_grade,
            "evidence": self.evidence,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class StackMap:
    """Die Schichtenkarte: Zuordnungen, Zähler je Schicht, leere Schichten.

    * ``per_layer`` zählt **alle** Repos je Schicht (jede Schicht ist Schlüssel,
      auch mit 0; ``SX`` eingeschlossen).
    * ``empty_layers`` nennt die Stack-Schichten ``S0`` bis ``S17``, die **kein
      eigenes** Repo tragen — auch wenn dort nur fremde Repos liegen.
    """

    assignments: tuple[LayerAssignment, ...]
    per_layer: dict[str, int]
    empty_layers: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": "aethel.projects.stack/v1",
            "layer_names": dict(LAYER_NAMES),
            "per_layer": dict(self.per_layer),
            "empty_layers": list(self.empty_layers),
            "assignments": [a.as_dict() for a in self.assignments],
        }


@dataclass(frozen=True)
class _Marker:
    """Ein Dateibeleg im Repo und die Schicht, auf die er zeigt."""

    layer: str
    label: str


# ---------------------------------------------------------------------------
# Herkunft
# ---------------------------------------------------------------------------


def _origin(report: RepoReport) -> tuple[str, str]:
    """Herkunft (eigen/fremd/unklar) und der Grund dafür."""
    entry = report.manifest_entry
    category = (entry.category if entry else "").strip().lower()
    if category in FOREIGN_CATEGORIES:
        return "fremd", f"Kategorie „{category}“"

    lowered = report.name.lower()
    prefix = next((p for p in OWN_NAME_PREFIXES if lowered.startswith(p)), None)
    remote = (report.remote_url or "").strip()
    if remote:
        if _OWN_REMOTE.search(remote):
            return "eigen", "Remote bei AETHEL-Omega/ManuelWilde"
        if prefix:
            return "eigen", f"Namenspräfix „{prefix}“ trotz fremdem Remote"
        return "fremd", "Remote nicht bei AETHEL-Omega/ManuelWilde"
    if prefix:
        return "eigen", f"Namenspräfix „{prefix}“"
    return "unklar", "kein Remote, kein Namenspräfix"


# ---------------------------------------------------------------------------
# Namensregeln
# ---------------------------------------------------------------------------


def _name_tokens(name: str) -> tuple[list[str], set[str]]:
    """Wörter des Namens: (geordnet, Menge inklusive verschmolzener Formen).

    Getrennt wird an Nicht-Alphanumerischem und an CamelCase-Grenzen. Dazu
    kommen die verschmolzene Form je Segment (``osxQ`` → ``osxq``) und der Rest
    nach einem Markenpräfix (``aethelema`` → ``ema``).
    """
    ordered: list[str] = []
    fused: set[str] = set()
    for segment in _NON_ALNUM.split(name):
        if not segment:
            continue
        lowered = segment.lower()
        fused.add(lowered)
        spaced = _CAMEL_ACRONYM.sub(" ", _CAMEL_LOWER_UPPER.sub(" ", segment))
        ordered.extend(part.lower() for part in spaced.split())
        for brand in _BRAND_PREFIXES:
            if lowered.startswith(brand) and len(lowered) - len(brand) >= 2:
                fused.add(lowered[len(brand):])
    return ordered, set(ordered) | fused


def _word_matches(token: str, keyword: str) -> bool:
    """Ist ``token`` das Schlüsselwort — oder seine einfache Beugung?"""
    if token == keyword:
        return True
    if len(keyword) <= 2:
        return False
    return any(token == keyword + suffix for suffix in _INFLECTIONS)


def _keyword_matches(keyword: str, lowered: str, ordered: list[str], tokens: set[str]) -> bool:
    parts = _KEY_SEPARATOR.split(keyword)
    if len(parts) > 1:
        width = len(parts)
        return any(
            all(_word_matches(ordered[start + i], part) for i, part in enumerate(parts))
            for start in range(len(ordered) - width + 1)
        )
    if len(keyword) >= _SUBSTRING_MIN_LENGTH:
        return keyword in lowered
    return any(_word_matches(token, keyword) for token in tokens)


def _match_name(name: str) -> tuple[str, str] | None:
    """Erste Namensregel, die trifft: ``(Schicht, Schlüsselwort)``."""
    lowered = name.lower()
    ordered, tokens = _name_tokens(name)
    for layer, keywords in NAME_RULES:
        for keyword in keywords:
            if _keyword_matches(keyword, lowered, ordered, tokens):
                return layer, keyword
    return None


# ---------------------------------------------------------------------------
# Dateimarker
# ---------------------------------------------------------------------------


def _scan_files(repo_path: Path) -> list[tuple[str, Path]]:
    """Dateien bis zwei Ebenen unter ``repo_path`` — ohne versteckte und Build-Ordner."""
    root = Path(repo_path)
    found: list[tuple[str, Path]] = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=True, onerror=lambda _e: None):
        base = Path(dirpath)
        depth = len(base.relative_to(root).parts)
        if depth >= _MARKER_MAX_DEPTH:
            dirnames[:] = []
        else:
            dirnames[:] = sorted(
                d for d in dirnames if not d.startswith(".") and not is_skipped(d)
            )
        for filename in sorted(filenames):
            path = base / filename
            if path.is_symlink():
                continue
            found.append((path.relative_to(root).as_posix(), path))
            if len(found) >= _MARKER_MAX_FILES:
                return found
    return found


def _read_text(path: Path) -> str:
    try:
        with path.open("rb") as handle:
            return handle.read(_MARKER_MAX_READ_BYTES).decode("utf-8", errors="replace")
    except OSError:
        return ""


def _first(
    files: list[tuple[str, Path]], predicate: Callable[[Path], bool]
) -> tuple[str, Path] | None:
    return next((item for item in files if predicate(item[1])), None)


def _is_no_std(path: Path) -> bool:
    return bool(_NO_STD.search(_read_text(path)))


def _is_swift_service(path: Path) -> bool:
    if path.name != "Package.swift":
        return False
    text = _read_text(path)
    return "XPC" in text or "ServiceManagement" in text


def _is_cargo_workspace(path: Path) -> bool:
    return path.name == "Cargo.toml" and bool(_CARGO_WORKSPACE.search(_read_text(path)))


def _detect_markers(repo_path: Path) -> list[_Marker]:
    """Dateimarker in der Reihenfolge ihrer Priorität (erster entscheidet)."""
    files = _scan_files(repo_path)
    markers: list[_Marker] = []

    rust = [item for item in files if item[0].endswith(".rs")][:_MARKER_MAX_RUST_FILES]
    hit = _first(rust, _is_no_std)
    if hit:
        markers.append(_Marker("S2", f"{hit[0]} (#![no_std])"))

    hit = _first(files, _is_swift_service)
    if hit:
        markers.append(_Marker("S4", f"{hit[0]} (XPC/ServiceManagement)"))

    has_cargo = _first(files, lambda path: path.name == "Cargo.toml") is not None
    pubspec = _first(files, lambda path: path.name == "pubspec.yaml")
    if pubspec and not has_cargo:
        markers.append(_Marker("S11", f"{pubspec[0]} ohne Rust-Crate"))

    hit = _first(files, _is_cargo_workspace)
    if hit:
        markers.append(_Marker("S10", f"{hit[0]} ([workspace])"))

    hit = _first(files, lambda path: path.name in ("flake.nix", "Dockerfile"))
    if hit:
        markers.append(_Marker("S7", hit[0]))

    hit = _first(files, lambda path: path.suffix in (".v", ".sv"))
    if hit:
        markers.append(_Marker("S0", f"{hit[0]} (Verilog)"))

    hit = _first(files, lambda path: path.name in ("SKILL.md", "capability.json"))
    if hit:
        markers.append(_Marker("S5", hit[0]))

    return markers


# ---------------------------------------------------------------------------
# Zuordnung
# ---------------------------------------------------------------------------


def classify(report: RepoReport, repo_path: Path | None = None) -> LayerAssignment:
    """Ordnet ein Repo einer Schicht zu.

    Reihenfolge: Namensregel, dann Dateimarker (nur mit ``repo_path``), sonst
    ``SX``. Konfidenz: ``high`` bei Namensregel plus bestätigendem Marker,
    ``medium`` bei genau einem Beleg, ``low`` bei ``SX``.
    """
    origin, origin_reason = _origin(report)
    markers: list[_Marker] = []
    if repo_path is not None and Path(repo_path).is_dir():
        markers = _detect_markers(Path(repo_path))

    named = _match_name(report.name)
    if named is not None:
        layer, keyword = named
        confirming = [m for m in markers if m.layer == layer]
        divergent = [m for m in markers if m.layer != layer]
        evidence = f"Name „{keyword}“ → {layer}"
        if confirming:
            evidence += f"; bestätigt durch {confirming[0].label}"
            confidence = "high"
        else:
            confidence = "medium"
            if divergent:
                evidence += f"; abweichender Marker {divergent[0].layer}: {divergent[0].label}"
    elif markers:
        layer = markers[0].layer
        evidence = f"Marker {markers[0].label} → {layer}"
        confidence = "medium"
    else:
        layer = UNDETERMINED
        evidence = "weder Namens- noch Dateiregel getroffen"
        confidence = "low"

    grade = report.maturity.grade if report.maturity else "unbekannt"
    return LayerAssignment(
        repo=report.name,
        layer=layer,
        layer_name=LAYER_NAMES[layer],
        origin=origin,
        maturity_grade=grade,
        evidence=f"{evidence}; Herkunft {origin}: {origin_reason}",
        confidence=confidence,
    )


def _repo_path(report: RepoReport, root: Path | None) -> Path | None:
    if root is None:
        return None
    candidate = Path(root) / report.path
    return candidate if candidate.is_dir() else None


def _sort_key(assignment: LayerAssignment) -> tuple[int, str, str]:
    return (_LAYER_INDEX.get(assignment.layer, len(LAYERS)), assignment.repo.casefold(), assignment.repo)


def build(repos: tuple[RepoReport, ...], root: Path | None = None) -> StackMap:
    """Baut die Schichtenkarte aus dem Scan-Ergebnis.

    Mit ``root`` wird je Repo ``root / report.path`` nach Dateimarkern
    durchsucht (sofern das Verzeichnis existiert). Worktrees werden übersprungen.
    """
    assignments = sorted(
        (
            classify(report, _repo_path(report, root))
            for report in repos
            if not report.is_worktree
        ),
        key=_sort_key,
    )
    per_layer = {code: 0 for code, _name in LAYERS}
    own_layers: set[str] = set()
    for assignment in assignments:
        per_layer[assignment.layer] = per_layer.get(assignment.layer, 0) + 1
        if assignment.origin == "eigen":
            own_layers.add(assignment.layer)
    empty = tuple(
        code for code, _name in LAYERS if code != UNDETERMINED and code not in own_layers
    )
    return StackMap(assignments=tuple(assignments), per_layer=per_layer, empty_layers=empty)


# ---------------------------------------------------------------------------
# Ausgabe
# ---------------------------------------------------------------------------


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(_cell(cell) for cell in row) + " |")
    return lines


_EXAMPLE_LIMIT = 5
_ORIGIN_ORDER = {"eigen": 0, "fremd": 1, "unklar": 2}


def render_markdown(stack_map: StackMap) -> str:
    """Die Schichtenkarte als Markdown: Schichttabelle, leere Schichten, Detail."""
    by_layer: dict[str, list[LayerAssignment]] = {}
    for assignment in stack_map.assignments:
        by_layer.setdefault(assignment.layer, []).append(assignment)

    stack_layers = len(LAYERS) - 1
    filled = sum(1 for code, _name in LAYERS if code != UNDETERMINED and by_layer.get(code))
    lines: list[str] = ["# Schichtenkarte", ""]
    lines.append(
        f"{len(stack_map.assignments)} Repositories (Worktrees ausgenommen); "
        f"{filled} von {stack_layers} Schichten belegt, "
        f"{len(stack_map.empty_layers)} ohne eigenes Repo."
    )
    lines.append("")

    lines.append("## Schichten")
    lines.append("")
    rows: list[list[str]] = []
    for code, name in LAYERS:
        members = by_layer.get(code, [])
        if code == UNDETERMINED and not members:
            continue
        ordered = sorted(members, key=lambda a: (_ORIGIN_ORDER.get(a.origin, 3), a.repo.casefold()))
        examples = ", ".join(a.repo for a in ordered[:_EXAMPLE_LIMIT])
        if len(ordered) > _EXAMPLE_LIMIT:
            examples += ", …"
        rows.append(
            [
                code,
                name,
                str(sum(1 for a in members if a.origin == "eigen")),
                str(sum(1 for a in members if a.origin == "fremd")),
                str(sum(1 for a in members if a.origin == "unklar")),
                examples or "-",
            ]
        )
    lines.extend(_table(["Code", "Schicht", "Eigene Repos", "Fremde Repos", "Unklar", "Beispiele"], rows))
    lines.append("")

    lines.append("## Leere Schichten")
    lines.append("")
    if stack_map.empty_layers:
        lines.append("Leer: diese Schichten haben kein eigenes Repo.")
        lines.append("")
        for code in stack_map.empty_layers:
            lines.append(f"- {code} {LAYER_NAMES.get(code, code)}")
    else:
        lines.append("Keine Schicht ist leer: jede hat mindestens ein eigenes Repo.")
    lines.append("")

    lines.append("## Detail")
    lines.append("")
    detail = sorted(stack_map.assignments, key=_sort_key)
    lines.extend(
        _table(
            ["Repo", "Schicht", "Herkunft", "Reife", "Konfidenz", "Beleg"],
            [
                [a.repo, f"{a.layer} {a.layer_name}", a.origin, a.maturity_grade, a.confidence, a.evidence]
                for a in detail
            ],
        )
    )
    lines.append("")
    return "\n".join(lines)


def render_json(stack_map: StackMap) -> str:
    """Die Schichtenkarte als JSON (``aethel.projects.stack/v1``)."""
    return json.dumps(stack_map.as_dict(), ensure_ascii=False, indent=2, sort_keys=False)
