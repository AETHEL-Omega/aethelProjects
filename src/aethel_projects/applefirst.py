"""Apple-first-Audit: wie weit trägt jedes Repo die Apple-Plattform und das Silizium?

Vorgabe (Manuel, 03.11.2026): Das AETHEL-Ökosystem ist Apple-first — Unified
Memory und alles, was der M5 Max mit 128 GB bietet (NPU, CPU, GPU,
Beschleuniger). Kanon: **Rust ist Kern, Swift ist die Apple-native Laufzeit,
Flutter ist Client, Python ist Übergangsrand, Bash ist Aufruf.** Kein Eigenbau,
wo ein Systemframework existiert.

Dieses Modul beantwortet je Repo vier Fragen — ohne etwas zu verändern:

1. **Sprachanteile** — Dateien und grobe LOC je Sprache, daraus ``python_anteil``.
2. **Plattform** — welche Apple-Frameworks das Repo tatsächlich nutzt (Metal,
   MLX, Core ML, Foundation Models, Accelerate, XPC, App Intents, …).
3. **Unified-Memory-Bewusstsein** — Treffer für Unified Memory, Shared-Storage,
   ``mx.array``, „M5“, „128 GB“ und Verwandtes in Code oder Doku.
4. **Anti-Muster** — Docker für die lokale Laufzeit, ``sandbox-exec``, CPU-ML
   (torch/tensorflow ohne ``mps``/Core ML/MLX), Subprozess-Orchestrierung, …

Daraus entstehen ein Score 0–100, ein Grade und Befunde (:class:`Finding`).

**Scan-Regeln (Dateimarker, kein Parser):**

* Tiefe: Dateien bis zu drei Verzeichnisebenen unter dem Repo-Wurzelordner.
* Übersprungen: versteckte Ordner, ``fsutil.is_skipped`` (``node_modules``,
  ``target``, ``build`` …), symbolische Links.
* Pro Datei werden höchstens 256 KiB gelesen; höchstens 3000 Dateien je Repo.
* Gelesen werden nur die Suffixe aus :data:`SCAN_SUFFIXES`; Sprachanteile
  zählen ``.swift .rs .dart .py .m .mm .metal .sh`` sowie — damit TypeScript-
  und C-Repos den Python-Anteil nicht verfälschen — ``.ts .tsx .js .jsx .mjs
  .cjs .c .h .cpp .hpp``.
* Apple-Frameworks werden nur in **Code** (und für Abhängigkeiten in
  ``.toml``) gezählt, nie in Markdown: eine Doku, die „Metal“ erwähnt, nutzt
  Metal nicht. Unified-Memory-Bewusstsein zählt dagegen auch in Doku.

Strikt lesend: es werden nur Dateien gelesen, nie geschrieben, und kein
Unterprozess gestartet. Befunde sind Daten, keine Aktionen (ADR-006).
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .fsutil import is_skipped
from .models import Finding, RepoReport

#: Schema der JSON-Ausgabe.
SCHEMA = "aethel.projects.applefirst/v1"

# ---------------------------------------------------------------------------
# Grenzen und Schwellen
# ---------------------------------------------------------------------------

#: Höchste Verzeichnistiefe unter der Repo-Wurzel, aus der Dateien gelesen werden.
MAX_DEPTH = 3
#: Höchstzahl gelesener Dateien je Repo.
MAX_FILES = 3000
#: Lesegrenze je Datei (Bytes).
MAX_READ_BYTES = 256 * 1024
#: Höchstzahl der Belege je Repo.
MAX_BELEGE = 10
#: Höchstlänge eines Treffertextes im Beleg.
_SNIPPET_LENGTH = 60
#: Obergrenze der gesammelten Treffer, bevor die Belege ausgewählt werden.
_EVIDENCE_POOL = 400

#: Python-Anteil (Bruch 0..1), ab dem Python „schwer“ ist / sehr schwer.
PYTHON_SCHWER = 0.6
PYTHON_SEHR_SCHWER = 0.8
#: Swift- oder Rust-Anteil (Bruch 0..1) für den Kern-Bonus.
KERN_ANTEIL = 0.3
#: Ab so vielen ``.py``-Dateien mit ``subprocess.`` gilt das Repo als Subprozess-lastig.
SUBPROCESS_DATEIEN = 20
#: Bash-Skripte mit mehr Zeilen als diesem Wert sind Anti-Muster.
BASH_ZEILEN = 200
#: Quellcode über dieser Größe ohne Apple-Framework ist auffällig.
SILIZIUM_LOC = 2000

#: Grade-Grenzen (Score ab, Name) in absteigender Reihenfolge.
GRADE_STUFEN: tuple[tuple[int, str], ...] = (
    (80, "Apple-first"),
    (60, "teilweise"),
    (40, "vernachlässigt"),
    (0, "fremdgeführt"),
)
#: Grade für Repos ohne Quellcode.
GRADE_OHNE_CODE = "ohne Code"
#: Alle Grades in Anzeigereihenfolge.
GRADES: tuple[str, ...] = tuple(name for _score, name in GRADE_STUFEN) + (GRADE_OHNE_CODE,)

# ---------------------------------------------------------------------------
# Sprachen und Suffixe
# ---------------------------------------------------------------------------

#: Sprachschlüssel in Anzeigereihenfolge. ``typescript`` umfasst auch JavaScript,
#: ``c_objc`` C/C++/Objective-C, ``metal`` die Metal Shading Language.
LANGUAGES: tuple[str, ...] = (
    "swift",
    "rust",
    "dart",
    "python",
    "typescript",
    "shell",
    "c_objc",
    "metal",
)

LANGUAGE_BY_SUFFIX: dict[str, str] = {
    ".swift": "swift",
    ".rs": "rust",
    ".dart": "dart",
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "typescript",
    ".jsx": "typescript",
    ".mjs": "typescript",
    ".cjs": "typescript",
    ".sh": "shell",
    ".m": "c_objc",
    ".mm": "c_objc",
    ".c": "c_objc",
    ".h": "c_objc",
    ".cpp": "c_objc",
    ".hpp": "c_objc",
    ".metal": "metal",
}

#: Suffixe, die als Code gelten (Sprachanteile, Framework- und Anti-Muster-Suche).
CODE_SUFFIXES = frozenset(LANGUAGE_BY_SUFFIX)
#: Doku-Suffixe (nur Unified-Memory-Bewusstsein).
DOC_SUFFIXES = frozenset({".md"})
#: Konfigurations-Suffixe.
CONFIG_SUFFIXES = frozenset({".toml", ".yaml", ".yml", ".json", ".plist"})
#: Alle gelesenen Suffixe.
SCAN_SUFFIXES = CODE_SUFFIXES | DOC_SUFFIXES | CONFIG_SUFFIXES

#: In diesen Suffixen zählt Unified-Memory-Bewusstsein (JSON und Plist sind Daten).
_UNIFIED_SUFFIXES = CODE_SUFFIXES | DOC_SUFFIXES | {".toml", ".yaml", ".yml"}

_ALL_CODE: tuple[str, ...] = tuple(sorted(CODE_SUFFIXES))
_CODE_AND_TOML: tuple[str, ...] = _ALL_CODE + (".toml",)

# ---------------------------------------------------------------------------
# Apple-Frameworks
# ---------------------------------------------------------------------------

#: Frameworks, die echte Silizium-Nutzung belegen (Bonus „MLX/Metal/Core ML/FM“).
SILIZIUM_FRAMEWORKS: tuple[str, ...] = ("MLX", "Metal", "CoreML", "FoundationModels")
#: Frameworks, die Modellarbeit tragen (für „ML ohne Unified-Memory-Bewusstsein“).
_ML_FRAMEWORKS = frozenset(
    {"MLX", "Metal", "CoreML", "FoundationModels", "Accelerate", "CoreAI", "Vision"}
)
#: Frameworks, die ein Repo als echten Dienst/Aktion auf der Plattform ausweisen.
_DIENST_FRAMEWORKS = ("XPC", "AppIntents")
#: Frameworks, die einen nativen Modellzugang belegen (Gegenpol zu „nur HTTP“).
_MODELLZUGANG_FRAMEWORKS = ("MLX", "CoreML", "FoundationModels")


@dataclass(frozen=True)
class _Signal:
    """Ein Suchmuster für ein Framework, beschränkt auf bestimmte Suffixe.

    ``anchors`` sind Teilstrings, von denen mindestens einer in der Datei
    stehen muss, damit das Muster überhaupt läuft — ein billiger Vorfilter, der
    den Scan über Tausende Dateien um eine Größenordnung beschleunigt. Bei
    ``ci``-Mustern sind die Anker kleingeschrieben und gelten gegen den
    kleingeschriebenen Text.
    """

    name: str
    pattern: re.Pattern[str]
    suffixes: frozenset[str]
    anchors: tuple[str, ...]
    ci: bool = False

    def hits(self, text: str, lowered: str) -> tuple[int, str | None]:
        """(Anzahl Treffer, erster Treffertext) — ``(0, None)`` ohne Treffer."""
        haystack = lowered if self.ci else text
        if not any(anchor in haystack for anchor in self.anchors):
            return 0, None
        count = 0
        first: str | None = None
        for match in self.pattern.finditer(text):
            count += 1
            if first is None:
                first = match.group(0)
        return count, first


def _sig(
    name: str,
    pattern: str,
    anchors: tuple[str, ...],
    suffixes: tuple[str, ...] = _ALL_CODE,
    flags: int = 0,
) -> _Signal:
    return _Signal(
        name,
        re.compile(pattern, flags),
        frozenset(suffixes),
        anchors,
        ci=bool(flags & re.IGNORECASE),
    )


_SWIFT = (".swift",)
_APPLE_AND_RUST = (".swift", ".m", ".mm", ".h", ".rs")
_RUST = (".rs", ".toml")
_OBJC_IMPORT = (".m", ".mm", ".h", ".c")

#: Die Signalliste. Mehrere Muster desselben Namens werden zusammengezählt.
SIGNALS: tuple[_Signal, ...] = (
    # Metal
    _sig("Metal", r"\bimport[ \t]+(?:Metal|MetalKit|MetalFX|MetalPerformanceShaders\w*)\b", ("Metal",), _SWIFT),
    _sig("Metal", r"#[ \t]*import[ \t]*<(?:Metal|MetalKit|MetalPerformanceShaders)/", ("Metal",), _OBJC_IMPORT),
    _sig("Metal", r"\bMTL[A-Z][A-Za-z]+\b", ("MTL",), _APPLE_AND_RUST),
    _sig("Metal", r"\b(?:objc2_metal|metal)::", ("metal::",), (".rs",)),
    _sig("Metal", r"(?m)^[ \t]*(?:objc2-metal|metal-rs|metal)[ \t]*=", ("metal",), (".toml",)),
    # MLX
    _sig("MLX", r"(?m)^[ \t]*(?:import|from)[ \t]+mlx(?:\.\w+)*\b", ("mlx",), (".py",)),
    _sig("MLX", r"\bimport[ \t]+MLX\w*\b", ("MLX",), _SWIFT),
    _sig("MLX", r"\bmlx[-_](?:rs|swift|lm|vlm)\b", ("mlx-", "mlx_"), _CODE_AND_TOML),
    _sig("MLX", r"""(?m)(?:^[ \t]*|["'])mlx(?=[ \t]*=|[<>=~!\["', ])""", ("mlx",), (".toml",)),
    # Core ML
    _sig("CoreML", r"\bimport[ \t]+CoreML\b", ("CoreML",), _SWIFT),
    _sig("CoreML", r"#[ \t]*import[ \t]*<CoreML/", ("CoreML",), _OBJC_IMPORT),
    _sig("CoreML", r"\bcoremltools\b", ("coremltools",), (".py", ".sh", ".toml")),
    _sig("CoreML", r"\bMLModel(?:Configuration)?\b", ("MLModel",), (".swift", ".m", ".mm")),
    _sig("CoreML", r"\.mlpackage\b|\.mlmodelc?\b", (".mlpackage", ".mlmodel")),
    _sig("CoreML", r"\bobjc2[-_]core[-_]ml\b", ("objc2",), _RUST),
    # Foundation Models (Framework und /usr/bin/fm)
    _sig("FoundationModels", r"\bimport[ \t]+FoundationModels\b", ("FoundationModels",), _SWIFT),
    _sig(
        "FoundationModels",
        r"\b(?:LanguageModelSession|SystemLanguageModel)\b",
        ("LanguageModelSession", "SystemLanguageModel"),
    ),
    _sig("FoundationModels", r"/usr/bin/fm\b", ("/usr/bin/fm",)),
    _sig("FoundationModels", r"\bfm[ \t]+respond\b", ("respond",)),
    # Accelerate
    _sig("Accelerate", r"\bimport[ \t]+Accelerate\b", ("Accelerate",), _SWIFT),
    _sig("Accelerate", r"#[ \t]*import[ \t]*<Accelerate/", ("Accelerate",), _OBJC_IMPORT),
    _sig("Accelerate", r"\bvDSP[_.]\w+", ("vDSP",)),
    _sig("Accelerate", r"\bBNNS[A-Za-z]\w*", ("BNNS",)),
    _sig("Accelerate", r"\baccelerate[-_]src\b", ("accelerate",), _RUST),
    # Core AI
    _sig("CoreAI", r"\bCoreAI\b", ("CoreAI",)),
    # Vision
    _sig("Vision", r"\bimport[ \t]+Vision\b", ("Vision",), _SWIFT),
    _sig("Vision", r"#[ \t]*import[ \t]*<Vision/", ("Vision",), _OBJC_IMPORT),
    _sig("Vision", r"\bVN(?:ImageRequestHandler|[A-Z]\w*Request)\b", ("VN",), (".swift", ".m", ".mm")),
    # XPC / SMAppService
    _sig(
        "XPC",
        r"\b(?:NSXPC(?:Connection|Listener|Interface)|XPCSession|XPCListener|SMAppService)\b",
        ("NSXPC", "XPCSession", "XPCListener", "SMAppService"),
    ),
    _sig("XPC", r"\bimport[ \t]+XPC\b", ("XPC",), _SWIFT),
    _sig("XPC", r"\bxpc_[a-z_]+\b", ("xpc_",)),
    _sig("XPC", r"\bxpc[-_]sys\b", ("xpc",), _RUST),
    # App Intents
    _sig(
        "AppIntents",
        r"\bimport[ \t]+AppIntents\b|\b(?:AppIntent|AppEntity|AppShortcutsProvider)\b",
        ("AppIntent", "AppEntity", "AppShortcutsProvider"),
        _SWIFT,
    ),
    # OSLog / Signposts / MetricKit
    _sig(
        "OSLog",
        r"\bimport[ \t]+(?:OSLog|MetricKit)\b|\bOSSignposter\b|\bMXMetricManager\b",
        ("OSLog", "MetricKit", "OSSignposter", "MXMetricManager"),
        _SWIFT,
    ),
    _sig("OSLog", r"\bos_(?:signpost|log)\w*", ("os_signpost", "os_log")),
    _sig("OSLog", r"\bLogger\([ \t]*subsystem:", ("subsystem",), _SWIFT),
    _sig("OSLog", r"\boslog\b", ("oslog",), _RUST),
    # Virtualization / Containerization
    _sig(
        "Virtualization",
        r"\bimport[ \t]+(?:Virtualization|Containerization\w*)\b",
        ("Virtualization", "Containerization"),
        _SWIFT,
    ),
    _sig("Virtualization", r"#[ \t]*import[ \t]*<Virtualization/", ("Virtualization",), _OBJC_IMPORT),
    _sig("Virtualization", r"\bVZ[A-Z][A-Za-z]+\b", ("VZ",), _APPLE_AND_RUST),
    _sig("Virtualization", r"\bapple/containerization\b", ("apple/containerization",), _SWIFT),
    _sig("Virtualization", r"\bobjc2[-_]virtualization\b", ("objc2",), _RUST),
    # Keychain / Secure Enclave / LocalAuthentication
    _sig(
        "Keychain",
        r"\bSecItem(?:Add|CopyMatching|Update|Delete)\b|\bkSec[A-Z]\w+|\bSecureEnclave\b",
        ("SecItem", "kSec", "SecureEnclave"),
    ),
    _sig("Keychain", r"\bimport[ \t]+LocalAuthentication\b|\bLAContext\b", ("LocalAuthentication", "LAContext")),
    _sig("Keychain", r"keychain", ("keychain",), _ALL_CODE, re.IGNORECASE),
    _sig("Keychain", r"\bsecurity[-_]framework\b", ("security",), _RUST),
    # Network.framework
    _sig("Network", r"\bimport[ \t]+Network\b", ("Network",), _SWIFT),
    _sig("Network", r"#[ \t]*import[ \t]*<Network/", ("Network",), _OBJC_IMPORT),
    _sig("Network", r"\bNW(?:Listener|Browser|Connection|PathMonitor)\b", ("NW",)),
    # Swift Concurrency / SwiftData / Swift Testing (nur Swift)
    _sig(
        "SwiftConcurrency",
        r"\basync[ \t]+let\b|\bactor[ \t]+[A-Z]\w*|TaskGroup\b",
        ("async", "actor", "TaskGroup"),
        _SWIFT,
    ),
    _sig("SwiftData", r"\bimport[ \t]+SwiftData\b", ("SwiftData",), _SWIFT),
    _sig("SwiftTesting", r"\bimport[ \t]+Testing\b|(?m:^)[ \t]*@Test\b", ("Testing", "@Test"), _SWIFT),
)

_SIGNALS_BY_SUFFIX: dict[str, tuple[_Signal, ...]] = {
    suffix: tuple(signal for signal in SIGNALS if suffix in signal.suffixes)
    for suffix in sorted(CODE_SUFFIXES | {".toml"})
}

#: SMAppService wird zusätzlich einzeln gezählt (Gegenstück zu launchd-Plists).
_SMAPPSERVICE = "SMAppService"

# ---------------------------------------------------------------------------
# Unified Memory
# ---------------------------------------------------------------------------

#: Unified-Memory-Marker, ohne Beachtung der Groß-/Kleinschreibung: (Anker, Muster),
#: beide kleingeschrieben und gegen den kleingeschriebenen Text geprüft.
_UNIFIED_CI: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("unified", re.compile(r"unified[ _-]?memory")),
    ("mtlstoragemode", re.compile(r"mtlstoragemode\.shared")),
    ("storagemodeshared", re.compile(r"storagemodeshared")),
    ("mlx.core", re.compile(r"\bmlx\.core\b")),
    ("mx.array", re.compile(r"\bmx\.array\b")),
    ("wired", re.compile(r"wired[ _-]?memory")),
    ("os_proc_available_memory", re.compile(r"os_proc_available_memory")),
    ("budget", re.compile(r"memory[ _-]budget")),
    ("128", re.compile(r"\b128[ \t]?(?:gb|gib)\b")),
    ("silicon", re.compile(r"apple[ _-]silicon")),
)
#: Chip-Namen, groß geschrieben („M5“, „M4“).
_UNIFIED_CS = re.compile(r"\bM[45]\b")
_UNIFIED_CS_ANCHORS = ("M4", "M5")

# ---------------------------------------------------------------------------
# Anti-Muster
# ---------------------------------------------------------------------------

#: Alle Anti-Muster-Schlüssel in Anzeigereihenfolge. Jeder Zähler zählt **Dateien**.
ANTI_MUSTER: tuple[str, ...] = (
    "docker_lokal",
    "sandbox_exec",
    "ml_cpu",
    "subprocess_lastig",
    "bash_gross",
    "launchd_ohne_smappservice",
    "numpy_ohne_mlx",
    "electron",
    "modellzugang_http",
)
#: Anti-Muster mit dem hohen Abzug von 10 Punkten; alle übrigen kosten 5.
_ANTI_SCHWER = ("docker_lokal", "sandbox_exec", "ml_cpu")

_DOCKERFILE = re.compile(r"(?:Dockerfile(?:\.[\w.-]+)?|[\w.-]+\.Dockerfile)", re.IGNORECASE)
_COMPOSE_FILE = re.compile(r"(?:docker-)?compose(?:[.-][\w.-]*)?\.ya?ml", re.IGNORECASE)
_DOCKER_CMD = re.compile(r"\bdocker[ \t]+(?:run|compose)\b|\bdocker-compose\b")
_SANDBOX_EXEC = re.compile(r"\bsandbox-exec\b")
_ML_CPU_IMPORT = re.compile(r"(?m)^[ \t]*(?:import|from)[ \t]+(?:torch|tensorflow|onnxruntime)\b")
_ML_APPLE_PATH = re.compile(r"\bmps\b|core[ _-]?ml|coremltools|\bmlx\b", re.IGNORECASE)
_NUMPY_IMPORT = re.compile(r"(?m)^[ \t]*(?:import|from)[ \t]+numpy\b")
_SUBPROCESS = re.compile(r"\bsubprocess\.")
_LAUNCHD = re.compile(r"<key>(?:ProgramArguments|Program)</key>")
_ELECTRON = re.compile(r"\"electron(?:-builder|-forge)?\"[ \t]*:")
_PORT_4000 = re.compile(r":4000\b")


# ---------------------------------------------------------------------------
# Ergebnis
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AppleFirst:
    """Der Apple-first-Befund zu einem Repository.

    * ``score`` — 0..100 oder ``None`` bei Repos ohne Quellcode.
    * ``python_anteil`` — Python-LOC / Gesamt-LOC aller Quellsprachen als Bruch
      0..1 (4 Nachkommastellen); 0.0 ohne Code.
    * ``sprachen`` — je Sprache aus :data:`LANGUAGES` ``{"files", "loc"}``.
    * ``frameworks`` — Apple-Framework → Anzahl Treffer (nur genutzte).
    * ``anti_muster`` — Schlüssel aus :data:`ANTI_MUSTER` → Anzahl **Dateien**
      (immer vollständig, 0 = nicht vorhanden).
    * ``belege`` — bis zu zehn Einträge ``Datei: Treffer``.
    """

    repo: str
    score: int | None
    grade: str
    python_anteil: float
    sprachen: dict[str, dict[str, int]]
    frameworks: dict[str, int]
    unified_memory_hits: int
    anti_muster: dict[str, int]
    findings: tuple[Finding, ...]
    belege: tuple[str, ...]

    @property
    def loc(self) -> int:
        """Gesamt-LOC aller Quellsprachen."""
        return sum(entry["loc"] for entry in self.sprachen.values())

    @property
    def silizium_genutzt(self) -> bool:
        """Nutzt das Repo MLX, Metal, Core ML oder Foundation Models?"""
        return any(self.frameworks.get(name, 0) > 0 for name in SILIZIUM_FRAMEWORKS)

    def anteil(self, sprache: str) -> float:
        """Anteil einer Sprache an der Gesamt-LOC als Bruch 0..1."""
        return _share(self.sprachen.get(sprache, {}).get("loc", 0), self.loc)

    def as_dict(self) -> dict[str, Any]:
        return {
            "repo": self.repo,
            "score": self.score,
            "grade": self.grade,
            "python_anteil": self.python_anteil,
            "sprachen": {name: dict(entry) for name, entry in self.sprachen.items()},
            "frameworks": dict(self.frameworks),
            "unified_memory_hits": self.unified_memory_hits,
            "anti_muster": dict(self.anti_muster),
            "findings": [
                {
                    "code": f.code,
                    "severity": f.severity,
                    "message": f.message,
                    "action": f.action,
                    "repo": f.repo,
                }
                for f in self.findings
            ],
            "belege": list(self.belege),
        }


# ---------------------------------------------------------------------------
# Scan
# ---------------------------------------------------------------------------


@dataclass
class _Tally:
    """Zwischenstand des Scans (veränderlich, nie nach außen gegeben)."""

    sprachen: dict[str, dict[str, int]] = field(
        default_factory=lambda: {name: {"files": 0, "loc": 0} for name in LANGUAGES}
    )
    frameworks: dict[str, int] = field(default_factory=dict)
    unified: int = 0
    smappservice: int = 0
    ml_imports: int = 0
    anti: dict[str, int] = field(default_factory=lambda: {name: 0 for name in ANTI_MUSTER})
    evidence: list[tuple[str, str, str]] = field(default_factory=list)
    seen: set[tuple[str, str]] = field(default_factory=set)

    def note(self, key: str, rel: str, snippet: str) -> None:
        """Einen Beleg je (Signal, Datei) merken — begrenzt."""
        if (key, rel) in self.seen or len(self.evidence) >= _EVIDENCE_POOL:
            return
        self.seen.add((key, rel))
        text = " ".join(snippet.split())
        if len(text) > _SNIPPET_LENGTH:
            text = text[: _SNIPPET_LENGTH - 1] + "…"
        self.evidence.append((key, rel, text))


def _is_container_file(name: str) -> bool:
    return bool(_DOCKERFILE.fullmatch(name) or _COMPOSE_FILE.fullmatch(name))


def _relevant(name: str) -> bool:
    suffix = os.path.splitext(name)[1].lower()
    return suffix in SCAN_SUFFIXES or bool(_DOCKERFILE.fullmatch(name))


def _iter_files(root: Path) -> list[tuple[str, Path]]:
    """Relevante Dateien bis :data:`MAX_DEPTH` Ebenen unter ``root``."""
    found: list[tuple[str, Path]] = []
    if not root.is_dir():
        return found
    for dirpath, dirnames, filenames in os.walk(root, topdown=True, onerror=lambda _e: None):
        base = Path(dirpath)
        depth = len(base.relative_to(root).parts)
        if depth >= MAX_DEPTH:
            dirnames[:] = []
        else:
            dirnames[:] = sorted(d for d in dirnames if not d.startswith(".") and not is_skipped(d))
        for filename in sorted(filenames):
            if not _relevant(filename):
                continue
            path = base / filename
            if path.is_symlink():
                continue
            found.append((path.relative_to(root).as_posix(), path))
            if len(found) >= MAX_FILES:
                return found
    return found


def _read_text(path: Path) -> str:
    try:
        with path.open("rb") as handle:
            return handle.read(MAX_READ_BYTES).decode("utf-8", errors="replace")
    except OSError:
        return ""


def _scan_signals(tally: _Tally, rel: str, suffix: str, text: str, lowered: str) -> None:
    for signal in _SIGNALS_BY_SUFFIX.get(suffix, ()):
        count, first = signal.hits(text, lowered)
        if count:
            tally.frameworks[signal.name] = tally.frameworks.get(signal.name, 0) + count
            tally.note(signal.name, rel, first or signal.name)


def _scan_unified(tally: _Tally, rel: str, text: str, lowered: str) -> None:
    first: str | None = None
    count = 0
    for anchor, pattern in _UNIFIED_CI:
        if anchor not in lowered:
            continue
        for match in pattern.finditer(lowered):
            count += 1
            if first is None:
                first = text[match.start() : match.end()]
    if any(anchor in text for anchor in _UNIFIED_CS_ANCHORS):
        for match in _UNIFIED_CS.finditer(text):
            count += 1
            if first is None:
                first = match.group(0)
    if count:
        tally.unified += count
        tally.note("unified_memory", rel, first or "unified memory")


def _scan_anti(tally: _Tally, rel: str, name: str, suffix: str, text: str, lines: int) -> None:
    """Anti-Muster einer Datei. Billige ``in``-Prüfungen stehen vor jedem Muster."""
    anti = tally.anti

    if _is_container_file(name):
        anti["docker_lokal"] += 1
        tally.note("docker_lokal", rel, name)
    elif suffix in (".sh", ".py") and "docker" in text:
        match = _DOCKER_CMD.search(text)
        if match:
            anti["docker_lokal"] += 1
            tally.note("docker_lokal", rel, match.group(0))

    if suffix in CODE_SUFFIXES:
        if "sandbox-exec" in text:
            match = _SANDBOX_EXEC.search(text)
            if match:
                anti["sandbox_exec"] += 1
                tally.note("sandbox_exec", rel, match.group(0))
        if ":4000" in text:
            match = _PORT_4000.search(text)
            if match:
                anti["modellzugang_http"] += 1
                tally.note("modellzugang_http", rel, _context(text, match))
        tally.smappservice += text.count(_SMAPPSERVICE)

    if suffix == ".py":
        if any(module in text for module in ("torch", "tensorflow", "onnxruntime")):
            ml = _ML_CPU_IMPORT.search(text)
            if ml:
                tally.ml_imports += 1
                if not _ML_APPLE_PATH.search(text):
                    anti["ml_cpu"] += 1
                    tally.note("ml_cpu", rel, ml.group(0))
        if "numpy" in text and _NUMPY_IMPORT.search(text):
            anti["numpy_ohne_mlx"] += 1
            tally.note("numpy_ohne_mlx", rel, "import numpy")
        if "subprocess." in text and _SUBPROCESS.search(text):
            anti["subprocess_lastig"] += 1
    elif suffix == ".sh":
        if lines > BASH_ZEILEN:
            anti["bash_gross"] += 1
            tally.note("bash_gross", rel, f"{lines} Zeilen")
    elif suffix == ".plist":
        if "<key>Program" in text:
            match = _LAUNCHD.search(text)
            if match:
                anti["launchd_ohne_smappservice"] += 1
                tally.note("launchd_ohne_smappservice", rel, match.group(0))
    elif name == "package.json" and "electron" in text:
        match = _ELECTRON.search(text)
        if match:
            anti["electron"] += 1
            tally.note("electron", rel, match.group(0))


def _context(text: str, match: re.Match[str]) -> str:
    """Die Zeile um einen Treffer — als lesbarer Beleg."""
    start = text.rfind("\n", 0, match.start()) + 1
    end = text.find("\n", match.end())
    return text[start : end if end != -1 else len(text)].strip()


def _scan(root: Path) -> _Tally:
    """Liest das Repo einmal und sammelt alle Signale."""
    tally = _Tally()
    for rel, path in _iter_files(root):
        name = path.name
        suffix = os.path.splitext(name)[1].lower()
        if suffix not in SCAN_SUFFIXES:
            # Dockerfile ohne Suffix: nur der Name zählt.
            _scan_anti(tally, rel, name, suffix, "", 0)
            continue

        text = _read_text(path)
        lines = len(text.splitlines())

        language = LANGUAGE_BY_SUFFIX.get(suffix)
        if language:
            entry = tally.sprachen[language]
            entry["files"] += 1
            entry["loc"] += lines

        if suffix == ".metal":
            tally.frameworks["Metal"] = tally.frameworks.get("Metal", 0) + 1
            tally.note("Metal", rel, "Metal-Shader")

        lowered = text.lower() if suffix in _UNIFIED_SUFFIXES else ""
        _scan_signals(tally, rel, suffix, text, lowered)
        if suffix in _UNIFIED_SUFFIXES:
            _scan_unified(tally, rel, text, lowered)
        _scan_anti(tally, rel, name, suffix, text, lines)
    return tally


# ---------------------------------------------------------------------------
# Bewertung
# ---------------------------------------------------------------------------


def _share(part: int, total: int) -> float:
    """Anteil als Bruch, auf vier Nachkommastellen gerundet."""
    return round(part / total, 4) if total > 0 else 0.0


def _final_anti(tally: _Tally) -> dict[str, int]:
    """Die Rohzähler mit den Bedingungen aus der Vorgabe."""
    anti = dict(tally.anti)
    if anti["subprocess_lastig"] < SUBPROCESS_DATEIEN:
        anti["subprocess_lastig"] = 0
    if tally.smappservice > 0:
        anti["launchd_ohne_smappservice"] = 0
    if tally.frameworks.get("MLX", 0) > 0:
        anti["numpy_ohne_mlx"] = 0
    if any(tally.frameworks.get(name, 0) > 0 for name in _MODELLZUGANG_FRAMEWORKS):
        anti["modellzugang_http"] = 0
    return anti


def grade_for(score: int | None) -> str:
    """Der Grade zu einem Score (``None`` → „ohne Code“)."""
    if score is None:
        return GRADE_OHNE_CODE
    for threshold, name in GRADE_STUFEN:
        if score >= threshold:
            return name
    return GRADE_STUFEN[-1][1]


def _score(
    *,
    sprachen: dict[str, dict[str, int]],
    python_anteil: float,
    frameworks: dict[str, int],
    unified: int,
    anti: dict[str, int],
) -> int:
    total = sum(entry["loc"] for entry in sprachen.values())
    score = 50
    if (
        _share(sprachen["swift"]["loc"], total) >= KERN_ANTEIL
        or _share(sprachen["rust"]["loc"], total) >= KERN_ANTEIL
    ):
        score += 10
    if len(frameworks) >= 3:
        score += 10
    if any(name in frameworks for name in SILIZIUM_FRAMEWORKS):
        score += 10
    if unified >= 1:
        score += 10
    if any(name in frameworks for name in _DIENST_FRAMEWORKS):
        score += 10

    if python_anteil >= PYTHON_SEHR_SCHWER:
        score -= 20
    elif python_anteil >= PYTHON_SCHWER:
        score -= 10

    for key in _ANTI_SCHWER:
        if anti.get(key, 0) > 0:
            score -= 10
    score -= 5 * sum(1 for key, count in anti.items() if key not in _ANTI_SCHWER and count > 0)
    return max(0, min(100, score))


def _pct(value: float) -> str:
    return f"{value * 100:.0f}"


def _findings(
    name: str,
    *,
    loc: int,
    python_anteil: float,
    frameworks: dict[str, int],
    unified: int,
    anti: dict[str, int],
    ml_imports: int,
) -> tuple[Finding, ...]:
    found: list[Finding] = []

    if python_anteil >= PYTHON_SCHWER:
        found.append(
            Finding(
                code="applefirst-python-schwer",
                severity="warn",
                message=f"Python-Anteil {_pct(python_anteil)} %; Kanon: Rust-Kern, Swift-Laufzeit, Python dünn.",
                action=(
                    "Kern nach Rust und die Apple-native Laufzeit nach Swift herauslösen; "
                    "Python auf den Übergangs- und Forschungsrand begrenzen (Komponente mit Vertrag)."
                ),
                repo=name,
            )
        )
    if anti["docker_lokal"]:
        found.append(
            Finding(
                code="applefirst-docker-lokal",
                severity="warn",
                message=f"Docker/Compose für die lokale Laufzeit ({anti['docker_lokal']} Dateien).",
                action=(
                    "Containerization (container) bzw. Virtualization statt Docker; "
                    "Compose durch einen Dienstvertrag ersetzen."
                ),
                repo=name,
            )
        )
    if anti["sandbox_exec"]:
        found.append(
            Finding(
                code="applefirst-sandbox-exec",
                severity="warn",
                message=f"sandbox-exec in {anti['sandbox_exec']} Datei(en); Containerization statt sandbox-exec.",
                action="Isolation über Containerization oder Virtualization statt sandbox-exec.",
                repo=name,
            )
        )
    if anti["ml_cpu"]:
        found.append(
            Finding(
                code="applefirst-ml-cpu",
                severity="warn",
                message=(
                    f"torch/tensorflow ohne mps/coreml; MLX oder Core ML nutzen "
                    f"({anti['ml_cpu']} Dateien)."
                ),
                action=(
                    "Inferenz auf MLX (Unified Memory, GPU) oder Core ML (NPU) umstellen; "
                    "CPU-Pfad nur als Fallback."
                ),
                repo=name,
            )
        )
    if loc > SILIZIUM_LOC and not frameworks:
        found.append(
            Finding(
                code="applefirst-kein-silizium",
                severity="info",
                message=(
                    f"{loc} LOC Quellcode, aber keine Apple-Frameworks "
                    "(Metal, MLX, Core ML, Foundation Models, Accelerate, XPC …)."
                ),
                action=(
                    "Plattform zuerst: prüfen, welche Systemframeworks Eigenbau ersetzen "
                    "und welche Last auf GPU/NPU gehört."
                ),
                repo=name,
            )
        )
    ml_hits = sum(count for key, count in frameworks.items() if key in _ML_FRAMEWORKS) + ml_imports
    if ml_hits > 0 and unified == 0:
        found.append(
            Finding(
                code="applefirst-kein-unified-memory",
                severity="info",
                message=(
                    "ML-Code ohne Unified-Memory-Bewusstsein (kein Treffer für Unified Memory, "
                    "Shared-Storage, mx.array, M5/128 GB)."
                ),
                action=(
                    "Speicherbudget und Shared-Storage (MTLStorageMode.shared, MLX-Arrays) "
                    "dokumentieren und im Code nutzen."
                ),
                repo=name,
            )
        )
    if anti["launchd_ohne_smappservice"]:
        found.append(
            Finding(
                code="applefirst-launchd-ohne-smappservice",
                severity="info",
                message=f"{anti['launchd_ohne_smappservice']} launchd-Plist(s) ohne SMAppService-Treffer im Repo.",
                action="Dienste über SMAppService (Agent/Daemon) registrieren statt Plists von Hand zu installieren.",
                repo=name,
            )
        )
    if anti["modellzugang_http"]:
        found.append(
            Finding(
                code="applefirst-modellzugang-nur-http",
                severity="info",
                message=(
                    f"Modellzugang nur über HTTP (:4000, litellm) in {anti['modellzugang_http']} Datei(en); "
                    "kein MLX, Core ML oder Foundation Models."
                ),
                action=(
                    "Lokale Modelle nativ anbinden (Foundation Models, MLX, Core ML); "
                    "den HTTP-Router höchstens als Fallback führen."
                ),
                repo=name,
            )
        )
    return tuple(found)


def _belege(evidence: list[tuple[str, str, str]]) -> tuple[str, ...]:
    """Bis zu zehn Belege — zuerst je Signal der erste, dann die übrigen."""
    first: list[str] = []
    rest: list[str] = []
    seen_keys: set[str] = set()
    for key, rel, snippet in evidence:
        entry = f"{rel}: {snippet}"
        if key in seen_keys:
            rest.append(entry)
        else:
            seen_keys.add(key)
            first.append(entry)
    return tuple((first + rest)[:MAX_BELEGE])


def audit(report: RepoReport, repo_path: Path) -> AppleFirst:
    """Apple-first-Audit eines Repositories unter ``repo_path`` (nur lesend)."""
    tally = _scan(Path(repo_path))
    total = sum(entry["loc"] for entry in tally.sprachen.values())
    python_anteil = _share(tally.sprachen["python"]["loc"], total)
    anti = _final_anti(tally)
    frameworks = dict(sorted(tally.frameworks.items()))
    sprachen = {name: dict(entry) for name, entry in tally.sprachen.items()}

    if total == 0:
        return AppleFirst(
            repo=report.name,
            score=None,
            grade=GRADE_OHNE_CODE,
            python_anteil=0.0,
            sprachen=sprachen,
            frameworks=frameworks,
            unified_memory_hits=tally.unified,
            anti_muster=anti,
            findings=(),
            belege=_belege(tally.evidence),
        )

    score = _score(
        sprachen=sprachen,
        python_anteil=python_anteil,
        frameworks=frameworks,
        unified=tally.unified,
        anti=anti,
    )
    return AppleFirst(
        repo=report.name,
        score=score,
        grade=grade_for(score),
        python_anteil=python_anteil,
        sprachen=sprachen,
        frameworks=frameworks,
        unified_memory_hits=tally.unified,
        anti_muster=anti,
        findings=_findings(
            report.name,
            loc=total,
            python_anteil=python_anteil,
            frameworks=frameworks,
            unified=tally.unified,
            anti=anti,
            ml_imports=tally.ml_imports,
        ),
        belege=_belege(tally.evidence),
    )


def _repo_path(report: RepoReport, root: Path) -> Path:
    """``root / report.path``; ein absoluter ``report.path`` gilt unverändert."""
    return Path(root) / report.path


def build(repos: Iterable[RepoReport], root: Path) -> tuple[AppleFirst, ...]:
    """Audit über alle Repos — Worktrees werden übersprungen.

    Je Repo wird ``root / report.path`` gelesen; fehlt das Verzeichnis, gilt das
    Repo als ohne Code. Die Ausgabe ist nach Repo-Name sortiert.
    """
    items = [audit(report, _repo_path(report, root)) for report in repos if not report.is_worktree]
    return tuple(sorted(items, key=lambda item: (item.repo.casefold(), item.repo)))


# ---------------------------------------------------------------------------
# Ausgabe
# ---------------------------------------------------------------------------


def summary(items: Iterable[AppleFirst]) -> dict[str, Any]:
    """Kennzahlen: Grades, Durchschnittsscore, Python-lastige und Silizium-Repos."""
    rows = tuple(items)
    scores = [item.score for item in rows if item.score is not None]
    grades = {name: 0 for name in GRADES}
    for item in rows:
        grades[item.grade] = grades.get(item.grade, 0) + 1
    python_repos = sorted(item.repo for item in rows if item.python_anteil >= PYTHON_SCHWER)
    silizium_repos = sorted(item.repo for item in rows if item.silizium_genutzt)
    return {
        "repos": len(rows),
        "grades": grades,
        "durchschnitt_score": round(sum(scores) / len(scores), 1) if scores else None,
        "python_schwer": len(python_repos),
        "python_schwer_repos": python_repos,
        "silizium": len(silizium_repos),
        "silizium_repos": silizium_repos,
    }


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(_cell(cell) for cell in row) + " |")
    return lines


def _anti_text(item: AppleFirst) -> str:
    parts = [f"{key}={count}" for key, count in item.anti_muster.items() if count > 0]
    return ", ".join(parts) if parts else "-"


def _score_text(item: AppleFirst) -> str:
    return "-" if item.score is None else str(item.score)


def _first_gap(item: AppleFirst) -> str:
    return item.findings[0].code if item.findings else "-"


def render_markdown(items: Iterable[AppleFirst]) -> str:
    """Der Audit als Markdown: Verteilung, schlechteste zehn Scores, Tabelle je Repo."""
    rows = tuple(items)
    stats = summary(rows)
    lines: list[str] = ["# Apple-first-Audit", ""]
    lines.append(
        "Kanon: Rust ist Kern, Swift ist Apple-native Laufzeit, Flutter ist Client, "
        "Python ist Übergangsrand, Bash ist Aufruf. Ziel: Unified Memory und das "
        "Silizium des M5 Max (CPU, GPU, NPU, Beschleuniger) tatsächlich nutzen."
    )
    lines.append("")
    average = stats["durchschnitt_score"]
    lines.append(
        f"{stats['repos']} Repositories; Durchschnittsscore "
        f"{'-' if average is None else average}; "
        f"{stats['python_schwer']} mit Python-Anteil ab {_pct(PYTHON_SCHWER)} %; "
        f"{stats['silizium']} nutzen MLX, Metal, Core ML oder Foundation Models."
    )
    lines.append("")

    lines.append("## Verteilung der Grades")
    lines.append("")
    lines.extend(_table(["Grade", "Repos"], [[name, str(stats["grades"][name])] for name in GRADES]))
    lines.append("")

    lines.append("## Top 10 schlechteste Scores")
    lines.append("")
    scored = sorted(
        (item for item in rows if item.score is not None),
        key=lambda item: (item.score, -item.python_anteil, item.repo.casefold()),
    )
    worst = scored[:10]
    if worst:
        lines.extend(
            _table(
                ["Rang", "Repo", "Score", "Grade", "Python %", "Anti-Muster"],
                [
                    [
                        str(rank),
                        item.repo,
                        _score_text(item),
                        item.grade,
                        _pct(item.python_anteil),
                        _anti_text(item),
                    ]
                    for rank, item in enumerate(worst, start=1)
                ],
            )
        )
    else:
        lines.append("Kein Repo mit Quellcode.")
    lines.append("")

    lines.append("## Alle Repos")
    lines.append("")
    ordered = sorted(rows, key=lambda item: (item.repo.casefold(), item.repo))
    lines.extend(
        _table(
            [
                "Repo",
                "Score",
                "Grade",
                "Python %",
                "Frameworks",
                "Unified Memory",
                "Anti-Muster",
                "Erste Lücke",
            ],
            [
                [
                    item.repo,
                    _score_text(item),
                    item.grade,
                    _pct(item.python_anteil),
                    ", ".join(item.frameworks) or "-",
                    str(item.unified_memory_hits),
                    _anti_text(item),
                    _first_gap(item),
                ]
                for item in ordered
            ],
        )
    )
    lines.append("")
    return "\n".join(lines)


def render_json(items: Iterable[AppleFirst]) -> str:
    """Der Audit als JSON (``aethel.projects.applefirst/v1``)."""
    rows = tuple(items)
    payload = {
        "schema": SCHEMA,
        "summary": summary(rows),
        "repos": [item.as_dict() for item in rows],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False)
