"""Statische Code-Analyse aus aethelCodeAnalyzer — die Code-Sicht auf das Portfolio.

aethelProjects sieht das **Portfolio** (Git-Zustand, Intent, Reifegrad).
aethelCodeAnalyzer sieht den **Code** (Komplexität, Zyklen, Panics, Duplikate,
ungetestete Symbole, Path-Dependencies).

Diese Module verbindet beides: sie ruft den Analyzer auf und führt seine
Findings in das Portfolio-Modell ein. Der Aufruf ist **lesend** — der Analyzer
schreibt nur nach stdout, es werden keine Dateien verändert.

Der Analyzer analysiert Rust und Dart. Für andere Sprachen liefert er nur
Marker-Regeln; aethelProjects markiert solche Repos deshalb als
``nicht vollstaendig analysiert`` — keine stillschweigende Lücke.

Umgesetzt wird der AIX-Vertrag ``aethel.code_analyzer.aix_findings.v1``.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .models import Finding, RepoReport

#: Schema, das der Analyzer im AIX-Modus ausgibt.
AIX_SCHEMA = "aethel.code_analyzer.aix_findings.v1"

#: Standard-Timeout je Analyzer-Aufruf (Sekunden).
DEFAULT_TIMEOUT = 120

#: Wo der Analyzer liegen kann — in dieser Reihenfolge.
CANDIDATE_PATHS = (
    Path("~/workspace/aethelCodeAnalyzer/target/release/aethel_code_analyzer"),
    Path("~/bin/aethel-code-analyzer"),
)

#: Severity-Übersetzung: Analyzer → Portfolio.
SEVERITY_MAP = {
    "high": "critical",
    "med": "warn",
    "medium": "warn",
    "low": "info",
}

#: Analyzer-Set, das ausschließlich liest. Alles andere wäre ein Verstoß.
READ_ONLY_FLAGS = {"--path", "--format", "--only-file", "--mode", "--profile"}


@dataclass(frozen=True)
class CodeAnalysis:
    """Das Ergebnis eines Analyzer-Aufrufs für ein Repository."""

    available: bool
    analyzed: bool
    schema: str
    findings: tuple[Finding, ...]
    rule_counts: dict[str, int]
    note: str = ""


def find_analyzer() -> Path | None:
    """Locate the analyzer binary — env var first, then the known paths."""
    from_env = os.environ.get("AETHEL_CODE_ANALYZER_BIN")
    if from_env:
        candidate = Path(from_env).expanduser()
        if candidate.is_file():
            return candidate
    for candidate in CANDIDATE_PATHS:
        resolved = candidate.expanduser()
        if resolved.is_file():
            return resolved
    return None


def is_analysable(repo: RepoReport) -> bool:
    """Der Analyzer hat volle Tiefe nur für Rust und Dart."""
    root = Path(repo.path)
    return (root / "Cargo.toml").is_file() or (root / "pubspec.yaml").is_file()


def _analyzer_version(binary: Path) -> str:
    try:
        result = subprocess.run(
            [str(binary), "--version"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError):
        return "unbekannt"
    return result.stdout.strip() or "unbekannt"


def analyse_repo(
    repo: RepoReport,
    binary: Path | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> CodeAnalysis:
    """Ruft den Analyzer für ein Repository auf und übersetzt die Findings."""
    if binary is None:
        binary = find_analyzer()
    if binary is None or not Path(binary).is_file():
        return CodeAnalysis(
            available=False,
            analyzed=False,
            schema=AIX_SCHEMA,
            findings=(),
            rule_counts={},
            note="aethelCodeAnalyzer nicht gefunden — Code-Sicht entfaellt.",
        )

    if not is_analysable(repo):
        return CodeAnalysis(
            available=True,
            analyzed=False,
            schema=AIX_SCHEMA,
            findings=(),
            rule_counts={},
            note="Kein Rust- oder Dart-Projekt — der Analyzer liefert hier nichts.",
        )

    command = [str(binary), "--path", repo.path, "--format", "aix"]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError) as error:
        return CodeAnalysis(
            available=True,
            analyzed=False,
            schema=AIX_SCHEMA,
            findings=(),
            rule_counts={},
            note=f"Analyzer nicht erreichbar: {error}",
        )

    if result.returncode != 0 or not result.stdout.strip():
        detail = (result.stderr or "").strip().splitlines()
        return CodeAnalysis(
            available=True,
            analyzed=False,
            schema=AIX_SCHEMA,
            findings=(),
            rule_counts={},
            note=f"Analyzer-Fehler (rc={result.returncode}): {detail[-1] if detail else 'keine Ausgabe'}",
        )

    try:
        document = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        return CodeAnalysis(
            available=True,
            analyzed=False,
            schema=AIX_SCHEMA,
            findings=(),
            rule_counts={},
            note=f"Analyzer-Ausgabe unlesbar: {error}",
        )

    schema = document.get("schema", "")
    if schema != AIX_SCHEMA:
        return CodeAnalysis(
            available=True,
            analyzed=False,
            schema=schema,
            findings=(),
            rule_counts={},
            note=f"Unerwartetes Schema {schema!r} — erwartet {AIX_SCHEMA}.",
        )

    findings: list[Finding] = []
    rule_counts: dict[str, int] = {}
    for raw in document.get("findings", []):
        rule = str(raw.get("rule", "unbekannt"))
        rule_counts[rule] = rule_counts.get(rule, 0) + 1
        severity = SEVERITY_MAP.get(str(raw.get("severity", "low")).lower(), "info")
        location = raw.get("file", "?")
        line = raw.get("line")
        where = f"{location}:{line}" if line else str(location)
        tier = raw.get("evidence_tier", "unbekannt")
        findings.append(
            Finding(
                code=f"code:{rule}",
                severity=severity,  # type: ignore[arg-type]
                message=f"{raw.get('message', rule)} ({where}, tier={tier})",
                action=str(raw.get("repro", "") or "Kein Repro angegeben."),
                repo=repo.name,
            )
        )

    note = ""
    if document.get("truncated"):
        note = "Analyzer meldet: Ergebnis abgeschnitten — nicht vollstaendig."

    return CodeAnalysis(
        available=True,
        analyzed=True,
        schema=schema,
        findings=tuple(findings),
        rule_counts=rule_counts,
        note=note,
    )


def summarise(analyses: dict[str, CodeAnalysis]) -> dict[str, int]:
    """Kennzahlen ueber alle Analyzer-Laeufe."""
    total = sum(len(a.findings) for a in analyses.values())
    analyzed = sum(1 for a in analyses.values() if a.analyzed)
    high = sum(
        1
        for a in analyses.values()
        for f in a.findings
        if f.severity == "critical"
    )
    return {
        "repos_analysiert": analyzed,
        "repos_gefunden": len(analyses),
        "findings": total,
        "high": high,
    }
