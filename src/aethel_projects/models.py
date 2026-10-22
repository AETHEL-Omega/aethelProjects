"""Datenmodelle — die Form des Analyseergebnisses.

Alle Modelle sind `frozen`: ein Scan ist ein Snapshot, Ableitungen erhalten den
unveränderten Wert und liefern einen neuen zurück.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class UnmergedBranch:
    """Ein Branch, der nicht auf dem Default-Branch gelandet ist."""

    name: str
    commits_ahead: int
    kind: str  # "local" | "remote-only"


@dataclass(frozen=True)
class Intent:
    """Der erkannte Zweck eines Repositories (REQ-009)."""

    text: str | None
    confidence: str  # "high" | "medium" | "low"
    source: str  # "docs/SPEC.md" | "README.md" | "manifest" | "none"
    evidence: str = ""


@dataclass(frozen=True)
class Maturity:
    """Reifegrad nach AETHEL Engineering Standard v2 (REQ-010)."""

    score: int
    grade: str  # "Professional" | "Solide" | "Prototyp" | "Skizze"
    parts: dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {"score": self.score, "grade": self.grade, "parts": dict(self.parts)}


@dataclass(frozen=True)
class ManifestEntry:
    """Ein Eintrag aus workspace-manifest/projects.yaml (REQ-011)."""

    name: str
    category: str
    status: str
    last_commit: str | None
    remote: str | None


@dataclass(frozen=True)
class Finding:
    """Ein Hinweis mit konkreter, aber **nicht ausgeführter** Empfehlung (REQ-012)."""

    code: str
    severity: str  # "info" | "warn" | "critical"
    message: str
    action: str
    repo: str = ""


@dataclass(frozen=True)
class ProjectManagementView:
    """Status, Risiko und nächste Schritte je Repository (REQ-013)."""

    activity: str  # "active" | "inactive"
    risk: str  # "low" | "medium" | "high"
    next_actions: tuple[str, ...] = ()


@dataclass(frozen=True)
class RepoReport:
    """Der vollständige Befund zu einem Repository."""

    name: str
    path: str
    git_common_dir: str
    is_worktree: bool
    worktree_paths: tuple[str, ...]

    default_branch: str | None
    current_branch: str
    commits_total: int
    commits_on_main: int
    commits_not_on_main: int
    branches_total: int
    branches_unmerged: int
    unmerged_branches: tuple[UnmergedBranch, ...]
    ahead_of_origin: int | None
    behind_origin: int | None
    dirty_files: int
    last_commit_date: str | None
    last_commit_subject: str | None
    remote_url: str | None

    intent: Intent | None = None
    maturity: Maturity | None = None
    manifest_entry: ManifestEntry | None = None
    findings: tuple[Finding, ...] = ()
    pm_view: ProjectManagementView | None = None

    @property
    def category(self) -> str:
        return self.manifest_entry.category if self.manifest_entry else "-"

    @property
    def source_files(self) -> int:
        return 0

    def as_dict(self) -> dict[str, Any]:
        """Serialisierbare Darstellung (REQ-005)."""
        return {
            "name": self.name,
            "path": self.path,
            "git_common_dir": self.git_common_dir,
            "is_worktree": self.is_worktree,
            "worktree_paths": list(self.worktree_paths),
            "default_branch": self.default_branch,
            "current_branch": self.current_branch,
            "commits_total": self.commits_total,
            "commits_on_main": self.commits_on_main,
            "commits_not_on_main": self.commits_not_on_main,
            "branches_total": self.branches_total,
            "branches_unmerged": self.branches_unmerged,
            "unmerged_branches": [
                {"name": u.name, "commits_ahead": u.commits_ahead, "kind": u.kind}
                for u in self.unmerged_branches
            ],
            "ahead_of_origin": self.ahead_of_origin,
            "behind_origin": self.behind_origin,
            "dirty_files": self.dirty_files,
            "last_commit_date": self.last_commit_date,
            "last_commit_subject": self.last_commit_subject,
            "remote_url": self.remote_url,
            "intent": (
                {
                    "text": self.intent.text,
                    "confidence": self.intent.confidence,
                    "source": self.intent.source,
                    "evidence": self.intent.evidence,
                }
                if self.intent
                else None
            ),
            "maturity": self.maturity.as_dict() if self.maturity else None,
            "manifest": (
                {
                    "name": self.manifest_entry.name,
                    "category": self.manifest_entry.category,
                    "status": self.manifest_entry.status,
                    "last_commit": self.manifest_entry.last_commit,
                    "remote": self.manifest_entry.remote,
                }
                if self.manifest_entry
                else None
            ),
            "findings": [
                {
                    "code": f.code,
                    "severity": f.severity,
                    "message": f.message,
                    "action": f.action,
                }
                for f in self.findings
            ],
            "pm_view": (
                {
                    "activity": self.pm_view.activity,
                    "risk": self.pm_view.risk,
                    "next_actions": list(self.pm_view.next_actions),
                }
                if self.pm_view
                else None
            ),
        }


@dataclass(frozen=True)
class CategorySummary:
    """Kennzahlen je Kategorie (Portfolio-Sicht)."""

    name: str
    repos: int
    commits_total: int
    commits_not_on_main: int
    branches: int
    median_maturity: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "repos": self.repos,
            "commits_total": self.commits_total,
            "commits_not_on_main": self.commits_not_on_main,
            "branches": self.branches,
            "median_maturity": self.median_maturity,
        }


@dataclass(frozen=True)
class ScanSummary:
    """Die Kopfdaten des Scans."""

    repos: int
    worktree_dirs: int
    commits_total: int
    commits_on_main: int
    commits_not_on_main: int
    branches: int
    dirty_repos: int
    stale_repos: int
    repos_without_main: int
    repos_without_remote: int
    total_size_kb: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "repos": self.repos,
            "worktree_dirs": self.worktree_dirs,
            "commits_total": self.commits_total,
            "commits_on_main": self.commits_on_main,
            "commits_not_on_main": self.commits_not_on_main,
            "branches": self.branches,
            "dirty_repos": self.dirty_repos,
            "stale_repos": self.stale_repos,
            "repos_without_main": self.repos_without_main,
            "repos_without_remote": self.repos_without_remote,
            "total_size_kb": self.total_size_kb,
        }


@dataclass(frozen=True)
class ScanResult:
    """Das vollständige Analyseergebnis."""

    generated_at: str
    workspace_root: str
    repos: tuple[RepoReport, ...]
    findings: tuple[Finding, ...]
    categories: tuple[CategorySummary, ...]
    summary: ScanSummary

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": "aethel.projects/v1",
            "generated_at": self.generated_at,
            "workspace_root": self.workspace_root,
            "summary": self.summary.as_dict(),
            "repos": [r.as_dict() for r in self.repos],
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
            "categories": [c.as_dict() for c in self.categories],
        }
