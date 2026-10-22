"""TC-001, TC-002 — Discovery und Worktree-Deduplizierung (REQ-001)."""

from __future__ import annotations

import subprocess
from pathlib import Path

from conftest import git, make_repo

from aethel_projects.discovery import discover


def test_tc001_single_repo_is_found(tmp_path: Path) -> None:
    """TC-001: Ein Verzeichnis mit .git ergibt genau eine RepoIdentity."""
    make_repo(tmp_path / "solo", commits=2)

    identities = discover(tmp_path)

    assert len(identities) == 1
    assert identities[0].name == "solo"
    assert identities[0].is_worktree is False
    assert identities[0].worktree_paths == ()


def test_tc002_worktrees_count_as_one_repo(tmp_path: Path) -> None:
    """TC-002: Hauptverzeichnis + 2 Worktrees = eine Identität mit 2 Worktree-Pfaden."""
    main = make_repo(tmp_path / "projekt", commits=2)
    for name in ("wt_a", "wt_b"):
        subprocess.run(
            ["git", "-C", str(main), "worktree", "add", "-q", "-b", f"br_{name}", str(tmp_path / name)],
            check=True,
            capture_output=True,
        )

    identities = discover(tmp_path)

    assert len(identities) == 1, "Worktrees müssen zum Haupt-Repo dedupliziert werden"
    identity = identities[0]
    assert identity.name == "projekt"
    assert identity.is_worktree is False
    assert set(identity.worktree_paths) == {str(tmp_path / "wt_a"), str(tmp_path / "wt_b")}


def test_tc002_worktree_directory_is_marked(tmp_path: Path) -> None:
    """TC-002 (Variante): Das Worktree-Verzeichnis selbst wird als Worktree erkannt."""
    main = make_repo(tmp_path / "projekt", commits=1)
    subprocess.run(
        ["git", "-C", str(main), "worktree", "add", "-q", "-b", "feature", str(tmp_path / "wt")],
        check=True,
        capture_output=True,
    )

    identities = discover(tmp_path)

    assert len(identities) == 1
    # Der Hauptpfad ist der Besitzer, der Worktree-Pfad ist in worktree_paths
    assert identities[0].path == str(tmp_path / "projekt")


def test_discovery_skips_non_git_directories(tmp_path: Path) -> None:
    """Nicht-Git-Verzeichnisse werden ignoriert, nicht als Fehler gewertet."""
    make_repo(tmp_path / "echt", commits=1)
    (tmp_path / "kein_git").mkdir()
    (tmp_path / "kein_git" / "datei.txt").write_text("x", encoding="utf-8")

    identities = discover(tmp_path)

    assert [i.name for i in identities] == ["echt"]
