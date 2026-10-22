"""Aufräum- und Risikohinweise (REQ-012).

**Grundregel (ADR-006):** Findings sind Daten, keine Aktionen. Jeder Vorschlag nennt
eine konkrete Handlung, führt sie aber **nie** aus. Nichts wird gelöscht, verschoben
oder committet — die AETHEL-Regel lautet: nichts wegschmeißen, immer archivieren.
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from .models import Finding, RepoReport

STALE_DAYS = 90
CRITICAL_NOT_ON_MAIN = 50
STUB_MAX_FILES = 30
STUB_MAX_LOC = 50
SOURCE_SUFFIXES = (".py", ".rs", ".dart", ".ts", ".tsx", ".js", ".jsx", ".go", ".swift", ".kt")


def _today() -> date:
    return date.today()


def _days_since(timestamp: str | None) -> int | None:
    if not timestamp:
        return None
    try:
        parsed = datetime.strptime(timestamp, "%Y-%m-%d").date()
    except ValueError:
        return None
    return (_today() - parsed).days


def _source_stats(repo: RepoReport) -> tuple[int, int]:
    """(Anzahl Quelldateien, Gesamt-LOC) im Repository."""
    root = Path(repo.path)
    files = 0
    lines = 0
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in SOURCE_SUFFIXES:
            continue
        if any(part in {".git", "build", "target", "node_modules", ".dart_tool"} for part in path.parts):
            continue
        files += 1
        try:
            lines += len(path.read_text(encoding="utf-8", errors="replace").splitlines())
        except OSError:
            continue
    return files, lines


def detect(repo: RepoReport) -> tuple[Finding, ...]:
    """Erkennt Hinweise für ein einzelnes Repository."""
    findings: list[Finding] = []
    name = repo.name

    if repo.commits_not_on_main > 0:
        severity = "critical" if repo.commits_not_on_main > CRITICAL_NOT_ON_MAIN else "warn"
        findings.append(
            Finding(
                code="not-on-main",
                severity=severity,
                message=(
                    f"{repo.commits_not_on_main} Commits sind auf keinem main-Branch "
                    f"({repo.branches_unmerged} ungemergte Branches)."
                ),
                action=(
                    f"Ungemergte Branches prüfen: {', '.join(b.name for b in repo.unmerged_branches[:5])}"
                    if repo.unmerged_branches
                    else "Branches mit 'git branch --no-merged' prüfen."
                ),
                repo=name,
            )
        )

    if repo.default_branch is None:
        findings.append(
            Finding(
                code="no-main",
                severity="warn",
                message="Kein main/master-Branch vorhanden.",
                action="Default-Branch anlegen oder Repository-Status klären.",
                repo=name,
            )
        )

    if repo.ahead_of_origin:
        findings.append(
            Finding(
                code="unpushed",
                severity="warn",
                message=f"{repo.ahead_of_origin} Commits sind lokal, aber nicht auf origin.",
                action=f"Push prüfen: 'git push origin {repo.default_branch}'.",
                repo=name,
            )
        )

    age = _days_since(repo.last_commit_date)
    if age is not None and age > STALE_DAYS:
        findings.append(
            Finding(
                code="stale",
                severity="warn",
                message=f"Letzter Commit vor {age} Tagen ({repo.last_commit_date}).",
                action=f"Archiv prüfen: 'mv {repo.path} _archive/' — nur nach Prüfung, es wird nichts gelöscht.",
                repo=name,
            )
        )

    if repo.is_worktree:
        findings.append(
            Finding(
                code="orphan-worktree",
                severity="info",
                message="Verzeichnis ist ein Worktree eines anderen Repositories.",
                action=f"Worktree-Bezug prüfen: gehört zu {Path(repo.git_common_dir).parent.name}.",
                repo=name,
            )
        )

    if repo.commits_total and repo.branches_total <= 2 and repo.commits_not_on_main == 0:
        files, lines = _source_stats(repo)
        if files < STUB_MAX_FILES and lines < STUB_MAX_LOC:
            findings.append(
                Finding(
                    code="stub",
                    severity="info",
                    message=(
                        f"Skizze: {files} Quelldateien, {lines} LOC, keine offene Arbeit."
                    ),
                    action="Ausbauen oder als 'archived' im Manifest führen.",
                    repo=name,
                )
            )

    return tuple(findings)


def detect_duplicates(repos: tuple[RepoReport, ...]) -> tuple[Finding, ...]:
    """Findet Repos, die denselben erkannten Zweck teilen (Duplikat-Kandidat)."""
    by_intent: dict[str, list[str]] = {}
    for repo in repos:
        if not repo.intent or not repo.intent.text:
            continue
        key = repo.intent.text.strip().lower()
        if len(key) < 20:
            continue
        by_intent.setdefault(key, []).append(repo.name)

    findings: list[Finding] = []
    for names in sorted(by_intent.values()):
        if len(names) < 2:
            continue
        for name in names:
            others = [n for n in names if n != name]
            findings.append(
                Finding(
                    code="duplicate",
                    severity="warn",
                    message=f"Gleicher Zweck wie: {', '.join(others)}.",
                    action="Duplikat prüfen: gemeinsame Codebasis prüfen, gemeinsam archivieren.",
                    repo=name,
                )
            )
    return tuple(findings)
