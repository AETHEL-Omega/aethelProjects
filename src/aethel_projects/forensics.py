"""Forensik: das Hässliche, das Schöne, das Interessante (Erweiterungsmodul).

Drei Sichtweisen auf denselben Workspace:

* **hässlich**  — Muster, die Aufmerksamkeit, Zeit oder Vertrauen kosten
* **schön**    — Muster, die Qualität, Tragfähigkeit und Sorgfalt belegen
* **interessant** — Muster, die eine Entscheidung anstossen (Lücke, Alleinsteller, Hotspot)

Jedes Ergebnis nennt die **messbare Beobachtung**, aus der es folgt, und — sofern
sinnvoll — einen konkreten nächsten Schritt. Es wird **nie** etwas ausgeführt.
"""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from .models import RepoReport

#: Verzeichnisse, die nie eingecheckt werden dürfen.
BUILD_ARTIFACT_DIRS = (".dart_tool", "target", "node_modules", "__pycache__", ".pytest_cache")

#: Dateien, die auf **echte** Credentials hindeuten.
SECRET_PATTERNS = (
    re.compile(r"^\.env$"),
    re.compile(r"^\.env\.(local|prod|production|secrets?|real)$"),
    re.compile(r"^.*\.pem$"),
    re.compile(r"^.*\.(p12|pfx|key|keystore)$"),
    re.compile(r"^id_(rsa|dsa|ecdsa|ed25519)$"),
    re.compile(r"^credentials(\.json)?$"),
    re.compile(r"^\.netrc$"),
    re.compile(r"^.*_rsa\.key$"),
    re.compile(r"^secrets?\.(ya?ml|json|toml)$"),
)

#: Beispieldateien — **kein** Verstoß, sondern gute Praxis. Sie werden getrennt
#: gemeldet, damit echte Credentials nicht im Rauschen verschwinden.
EXAMPLE_PATTERNS = (
    re.compile(r"^\.env\.(example|sample|template|default|dist|tpl|template\.local)$"),
    re.compile(r"^.*\.(example|sample|template|dist)$"),
    re.compile(r"^docker-compose\..*\.ya?ml$"),
)

#: Bekannte Vendor-/Fork-Verzeichnisse (Fremdcode im eigenen Workspace).
VENDOR_NAMES = {"comfyui", "osxq", "flutter", "litellm", "pytorch"}

#: Scratch-Verzeichnisse aus Laufzeit-Aufträgen.
SCRATCH_PREFIXES = ("run-task-", "run-cli-", "tmp-", "scratch-")

SOURCE_SUFFIXES = (".py", ".rs", ".dart", ".ts", ".tsx", ".js", ".jsx", ".go", ".swift", ".kt")

PATH_DEP = re.compile(r"path:\s*(\.{0,2}/[^\s\"']+)")


@dataclass(frozen=True)
class Observation:
    """Ein forensischer Befund mit Beobachtung, Einordnung und Vorschlag."""

    repo: str
    kind: str  # "hässlich" | "schön" | "interessant"
    code: str
    title: str
    observation: str
    suggestion: str
    weight: int  # 0-100, Gewichtung innerhalb der Einordnung


def _source_files(root: Path) -> list[Path]:
    """Die Quellcodedateien eines Repositories — ohne Build-Verzeichnisse."""
    from .fsutil import walk_files

    return walk_files(root, suffix=SOURCE_SUFFIXES)


def _code_signature(root: Path, name: str) -> tuple[str, int, int]:
    """Signatur eines Repositories: normalisierte Pfade + LOC.

    Der Repo-Name wird in Pfaden durch einen Platzhalter ersetzt, damit die
    Template-Familie (gleiche Struktur, anderer Name) als gleiche Signatur
    erkannt wird.
    """
    files = _source_files(root)
    parts: list[str] = []
    total_lines = 0
    for path in sorted(files):
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = len(content.splitlines())
        total_lines += lines
        relative = path.relative_to(root).as_posix().replace(name, "<name>")
        parts.append(f"{relative}:{lines}")
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:12]
    return digest, len(files), total_lines


def _tracked_files(root: Path) -> set[str]:
    """Die von Git verfolgten Dateien (ohne Netzwerk, nur lokaler Index)."""
    from . import gitio

    output = gitio.run_git_lines(root, "ls-files")
    return set(output)


def _broken_path_dependencies(root: Path) -> list[str]:
    """Path-Dependencies in pubspec.yaml, die auf nicht existierende Pfade zeigen."""
    pubspec = root / "pubspec.yaml"
    if not pubspec.is_file():
        return []
    try:
        content = pubspec.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    broken: list[str] = []
    for match in PATH_DEP.finditer(content):
        target = (root / match.group(1)).resolve()
        if not target.exists():
            broken.append(match.group(1))
    return broken


def _secret_candidates(root: Path, tracked: set[str]) -> list[str]:
    """Verfolgte Dateien, die nach **echten** Credentials aussehen.

    Beispieldateien (``.env.example``) zaehlen nicht als Verstoß — sie sind die
    richtige Praxis. Sie werden getrennt gemeldet.
    """
    found: list[str] = []
    for relative in tracked:
        name = relative.rsplit("/", 1)[-1]
        if any(pattern.match(name) for pattern in SECRET_PATTERNS):
            found.append(relative)
    return sorted(found)[:10]


def _example_candidates(root: Path, tracked: set[str]) -> list[str]:
    """Verfolgte Beispieldateien — ein gutes Zeichen, kein Mangel."""
    found: list[str] = []
    for relative in tracked:
        name = relative.rsplit("/", 1)[-1]
        if any(pattern.match(name) for pattern in EXAMPLE_PATTERNS):
            found.append(relative)
    return sorted(found)[:5]


def _has_substance(repo: RepoReport) -> bool:
    """Hat das Repository Inhalt — oder ist es nur eine Hülle?

    Ein Repo mit neun Commits, ohne README und ohne Tests ist kein Projekt.
    Solche Repos duerfen nicht als „schoen“ gelobt werden.
    """
    if repo.maturity and repo.maturity.score >= 40:
        return True
    if repo.commits_total >= 20 and repo.commits_on_main >= 20:
        return True
    return False


def _tracked_build_artifacts(root: Path, tracked: set[str]) -> list[str]:
    """Eingecheckte Build-Artefakte — ein Hygiene-Verstoß."""
    offenders = [
        relative
        for relative in tracked
        if any(f"{artifact}/" in relative for artifact in BUILD_ARTIFACT_DIRS)
    ]
    return sorted(offenders)[:10]


def _is_ignored_globally(name: str) -> bool:
    """Steht das Verzeichnis in der globalen Gitignore?"""
    ignore_file = Path.home() / ".gitignore_global"
    if not ignore_file.is_file():
        return False
    try:
        for line in ignore_file.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.rstrip("/") in {".aix", ".aethel", name}:
                return True
    except OSError:
        return False
    return False


def inspect(repo: RepoReport) -> list[Observation]:
    """Alle forensischen Beobachtungen für ein einzelnes Repository."""
    root = Path(repo.path)
    findings: list[Observation] = []
    name = repo.name
    tracked = _tracked_files(root)

    # ---------------- hässlich ----------------
    if repo.commits_total == 0:
        findings.append(
            Observation(
                repo=name, kind="hässlich", code="leer",
                title="Repository ohne Commits",
                observation="0 Commits, 0 Branches — es existiert nur ein Verzeichnis.",
                suggestion="Entweder initialisieren und nutzen oder als leer markieren.",
                weight=70,
            )
        )

    if not any(
        (root / candidate).is_file() for candidate in ("README.md", "README.rst", "README.txt")
    ):
        findings.append(
            Observation(
                repo=name, kind="hässlich", code="kein-readme",
                title="Kein README",
                observation="Kein README im Repository — Zweck nur aus dem Code erschließbar.",
                suggestion="README anlegen: Zweck, Quickstart, Status.",
                weight=45,
            )
        )

    broken = _broken_path_dependencies(root)
    if broken:
        findings.append(
            Observation(
                repo=name, kind="hässlich", code="kaputte-pfad-abhaengigkeit",
                title="Kaputte Path-Dependency",
                observation=f"{len(broken)} Path-Dependency(s) zeigen ins Leere: {', '.join(broken[:3])}.",
                suggestion="Pfad korrigieren oder Abhängigkeit entfernen — sonst kein Build.",
                weight=80,
            )
        )

    artifacts = _tracked_build_artifacts(root, tracked)
    if artifacts:
        findings.append(
            Observation(
                repo=name, kind="hässlich", code="build-artifakte-eingecheckt",
                title="Build-Artefakte eingecheckt",
                observation=f"{len(artifacts)} verfolgte Datei(en) aus Build-Verzeichnissen.",
                suggestion="Aus dem Index entfernen und in .gitignore aufnehmen.",
                weight=50,
            )
        )

    secrets = _secret_candidates(root, tracked)
    if secrets:
        findings.append(
            Observation(
                repo=name, kind="hässlich", code="echte-credentials",
                title="Echte Credentials im Repository",
                observation=f"{len(secrets)} verfolgte Datei(en) mit Credential-Muster: {', '.join(secrets[:3])}.",
                suggestion="Prüfen, ob echte Zugangsdaten — dann ersetzen und Historie bereinigen.",
                weight=95,
            )
        )

    examples = _example_candidates(root, tracked)
    if examples:
        findings.append(
            Observation(
                repo=name, kind="schön", code="beispiel-konfiguration",
                title="Beispiel-Konfiguration mitgeliefert",
                observation=(
                    f"{len(examples)} Beispieldatei(en) verfolgt: {', '.join(examples[:3])} — "
                    f"Geheimnisse sind nicht eingecheckt."
                ),
                suggestion="—",
                weight=30,
            )
        )

    if repo.commits_total > 0 and not _has_substance(repo):
        score = repo.maturity.score if repo.maturity else 0
        findings.append(
            Observation(
                repo=name, kind="hässlich", code="leere-huelle",
                title="Leere Hülle ohne Substanz",
                observation=(
                    f"{repo.commits_total} Commits, aber Reifegrad {score}/100 — "
                    f"das Repo traegt keinen eigenen Inhalt."
                ),
                suggestion="Klon-Zustand: entweder ausbauen oder als Scaffold kennzeichnen.",
                weight=55,
            )
        )

    if repo.name.lower() in VENDOR_NAMES:
        findings.append(
            Observation(
                repo=name, kind="hässlich", code="vendor-im-workspace",
                title="Fremdcode im eigenen Workspace",
                observation="Bekanntes Vendor-/Fork-Verzeichnis — zählt in Portfolio-Zahlen mit.",
                suggestion="Aus dem Workspace verschieben oder als Vendor markieren.",
                weight=40,
            )
        )

    if name.lower().startswith(SCRATCH_PREFIXES):
        findings.append(
            Observation(
                repo=name, kind="hässlich", code="scratch-verzeichnis",
                title="Scratch-Verzeichnis aus einem Lauf",
                observation="Namensschema deutet auf ein Wegwerf-Arbeitsverzeichnis.",
                suggestion="Nach Abschluss archivieren — nicht löschen.",
                weight=30,
            )
        )

    if repo.default_branch is None and repo.commits_total > 0:
        findings.append(
            Observation(
                repo=name, kind="hässlich", code="kein-default-branch",
                title="Kein main/master",
                observation=f"{repo.commits_total} Commits, aber kein main/master — alle Arbeit ist 'nicht auf main'.",
                suggestion="Default-Branch festlegen und Hauptlinie bestimmen.",
                weight=60,
            )
        )

    if repo.branches_total > 100 and repo.commits_on_main < repo.commits_total / 2:
        findings.append(
            Observation(
                repo=name, kind="hässlich", code="branch-hotspot",
                title="Branch-Hotspot",
                observation=(
                    f"{repo.branches_total} Branches, davon {repo.commits_not_on_main} Commits "
                    f"nicht auf main."
                ),
                suggestion="Branches aufräumen: gemergte löschen, offene zusammenführen.",
                weight=65,
            )
        )

    # ---------------- schön ----------------
    if repo.maturity and repo.maturity.score >= 80:
        findings.append(
            Observation(
                repo=name, kind="schön", code="professional",
                title="Engineering-Standard erfüllt",
                observation=(
                    f"Reifegrad {repo.maturity.score}/100 (Professional) — "
                    f"{repo.commits_on_main} Commits auf main."
                ),
                suggestion="Als Referenz für die übrigen Repos heranziehen.",
                weight=90,
            )
        )

    if repo.maturity and repo.maturity.parts.get("DNA", 0) > 0:
        findings.append(
            Observation(
                repo=name, kind="schön", code="hat-dna",
                title="Software-DNA vorhanden",
                observation="dna/genome.yaml mit Schema aethel.dna/v1 — das Repo ist regenerierbar.",
                suggestion="DNA verifizieren: 'factory dna verify'.",
                weight=80,
            )
        )

    if repo.dirty_files == 0 and repo.commits_total > 0:
        findings.append(
            Observation(
                repo=name, kind="schön", code="sauberer-baum",
                title="Sauberer Working Tree",
                observation="Keine ungespeicherten Änderungen.",
                suggestion="—",
                weight=40,
            )
        )

    if repo.commits_not_on_main == 0 and repo.commits_on_main > 0 and _has_substance(repo):
        findings.append(
            Observation(
                repo=name, kind="schön", code="vollstaendig-auf-main",
                title="Vollständig auf main",
                observation=(
                    f"Alle {repo.commits_on_main} Commits liegen auf main "
                    f"(Reifegrad {repo.maturity.score if repo.maturity else 0}/100)."
                ),
                suggestion="—",
                weight=70,
            )
        )

    # ---------------- interessant ----------------
    if len(repo.worktree_paths) >= 5:
        findings.append(
            Observation(
                repo=name, kind="interessant", code="worktree-hub",
                title="Worktree-Hub",
                observation=f"{len(repo.worktree_paths)} Worktrees — hohe parallele Aktivität.",
                suggestion="Worktree-Hub ist ein Signal für laufende Parallelarbeit.",
                weight=75,
            )
        )

    if repo.commits_total > 200 and (repo.maturity is None or repo.maturity.score < 20):
        findings.append(
            Observation(
                repo=name, kind="interessant", code="einsamer-wolf",
                title="Einsamer Wolf",
                observation=(
                    f"{repo.commits_total} Commits, aber Reifegrad "
                    f"{repo.maturity.score if repo.maturity else 0}/100 — viel Code, kein Prozess."
                ),
                suggestion="SPEC, Tests, CI und DNA nachziehen — das ist die teuerste Lücke.",
                weight=85,
            )
        )

    return findings


def inspect_workspace(repos: tuple[RepoReport, ...]) -> list[Observation]:
    """Workspace-weite Beobachtungen: Template-Familien, Vendor, Lücken."""
    findings: list[Observation] = []

    # Namenskollisionen: verschiedene Repos mit gleichem Basisnamen.
    by_name: dict[str, list[RepoReport]] = defaultdict(list)
    for repo in repos:
        by_name[repo.name].append(repo)
    for name, group in sorted(by_name.items()):
        distinct = {r.git_common_dir for r in group}
        if len(distinct) < 2:
            continue
        for repo in group:
            findings.append(
                Observation(
                    repo=name, kind="interessant", code="namenskollision",
                    title="Namenskollision",
                    observation=(
                        f"{len(distinct)} verschiedene Repos tragen den Namen „{name}“ "
                        f"({len(group)} Verzeichnisse) — Zuordnung ueber den Namen ist nicht eindeutig."
                    ),
                    suggestion="Repo-Identitaet ueber den common-dir fuehren, nicht ueber den Namen.",
                    weight=65,
                )
            )

    # Seed-Familien: viele Repos mit exakt gleicher Struktur und miniem Umfang.
    seeds: dict[tuple[int, int, str | None], list[RepoReport]] = defaultdict(list)
    for repo in repos:
        if repo.commits_total > 10 or repo.commits_total == 0:
            continue
        seeds[(repo.commits_total, repo.branches_total, repo.default_branch)].append(repo)
    for (commits, branches, default), group in sorted(
        seeds.items(), key=lambda item: (-len(item[1]), item[0])
    ):
        if len(group) < 3:
            continue
        for repo in group:
            findings.append(
                Observation(
                    repo=repo.name, kind="hässlich", code="seed-familie",
                    title="Seed-Klon ohne eigene Geschichte",
                    observation=(
                        f"{len(group)} Repos haben dieselbe Struktur: {commits} Commits, "
                        f"{branches} Branches, kein default-Branch."
                    ),
                    suggestion="Seed-Klon: entweder echten Inhalt aufbauen oder als Scaffold markieren.",
                    weight=60,
                )
            )

    # Template-Familien: gleiche Code-Signatur in mehreren Repos
    signatures: dict[tuple[str, int, int], list[str]] = defaultdict(list)
    for repo in repos:
        root = Path(repo.path)
        if not root.is_dir():
            continue
        digest, files, lines = _code_signature(root, repo.name)
        if files == 0:
            continue
        signatures[(digest, files, lines)].append(repo.name)

    for (digest, files, lines), names in sorted(signatures.items()):
        if len(names) < 2:
            continue
        for name in names:
            findings.append(
                Observation(
                    repo=name, kind="interessant", code="template-familie",
                    title="Template-Familie",
                    observation=(
                        f"{len(names)} Repos teilen dieselbe Codebasis "
                        f"({files} Dateien, {lines} LOC, Signatur {digest})."
                    ),
                    suggestion="Gemeinsame Basis extrahieren oder die Familie auflösen.",
                    weight=70,
                )
            )

    # Kategorie-Lücken: eine Kategorie, die nur ein Repo ohne Reifegrad hat
    by_category: dict[str, list[RepoReport]] = defaultdict(list)
    for repo in repos:
        by_category[repo.category].append(repo)
    for category, group in sorted(by_category.items()):
        if category in {"-", ""} or len(group) != 1:
            continue
        only = group[0]
        score = only.maturity.score if only.maturity else 0
        if score < 50:
            findings.append(
                Observation(
                    repo=only.name, kind="interessant", code="kategorie-luecke",
                    title="Kategorie ohne Träger",
                    observation=(
                        f"Einziges Repository der Kategorie '{category}' mit "
                        f"{only.commits_on_main + only.commits_not_on_main} Commits, "
                        f"Reifegrad {score}/100."
                    ),
                    suggestion="Kategorie entweder ausbauen oder als bewusste Lücke dokumentieren.",
                    weight=60,
                )
            )

    return findings


def summarise(observations: list[Observation]) -> dict[str, int]:
    """Anzahl der Beobachtungen je Einordnung."""
    counts: dict[str, int] = {"hässlich": 0, "schön": 0, "interessant": 0}
    for observation in observations:
        counts[observation.kind] = counts.get(observation.kind, 0) + 1
    return counts
