"""Gemeinsame Fixtures: Mini-Git-Repos in tmp_path.

Die Testsuite läuft ohne Netzwerk und ohne den echten ~/workspace.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aethel_projects.models import RepoReport  # noqa: E402


def git(repo: Path, *args: str) -> str:
    """Führt einen Git-Befehl aus und gibt stdout zurück."""
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def make_repo(path: Path, *, commits: int = 1, branch: str = "main") -> Path:
    """Erzeugt ein Git-Repo mit `commits` Commits auf `branch`."""
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q")
    git(path, "config", "user.email", "test@example.invalid")
    git(path, "config", "user.name", "Test")
    git(path, "checkout", "-q", "-b", branch)
    for index in range(commits):
        (path / f"file{index}.txt").write_text(f"Inhalt {index}\n", encoding="utf-8")
        git(path, "add", "-A")
        git(path, "commit", "-q", "-m", f"Commit {index}")
    return path


def add_commit(repo: Path, message: str, filename: str = "extra.txt") -> None:
    (repo / filename).write_text(message + "\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)


@pytest.fixture
def mini_repo(tmp_path: Path) -> Path:
    """Ein Repo mit 3 Commits auf main."""
    return make_repo(tmp_path / "mini", commits=3)


@pytest.fixture
def repo_report(mini_repo: Path) -> RepoReport:
    """Ein fertiges RepoReport ohne Git-Zugriff (für reine Ableitungs-Tests)."""
    from aethel_projects.discovery import discover
    from aethel_projects.metrics import collect

    identities = discover(mini_repo.parent)
    return collect(identities[0])


@pytest.fixture
def empty_report(tmp_path: Path) -> RepoReport:
    """Ein RepoReport für ein Verzeichnis ohne Git."""
    return RepoReport(
        name="leer",
        path=str(tmp_path / "leer"),
        git_common_dir=str(tmp_path / "leer" / ".git"),
        is_worktree=False,
        worktree_paths=(),
        default_branch=None,
        current_branch="",
        commits_total=0,
        commits_on_main=0,
        commits_not_on_main=0,
        branches_total=0,
        branches_unmerged=0,
        unmerged_branches=(),
        ahead_of_origin=None,
        behind_origin=None,
        dirty_files=0,
        last_commit_date=None,
        last_commit_subject=None,
        remote_url=None,
        intent=None,
        maturity=None,
        manifest_entry=None,
        findings=(),
        pm_view=None,
    )
