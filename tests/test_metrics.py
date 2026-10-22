"""TC-003 bis TC-008 — Git-Metriken (REQ-002, REQ-003, REQ-004)."""

from __future__ import annotations

import subprocess
from pathlib import Path

from conftest import add_commit, git, make_repo

from aethel_projects.discovery import discover
from aethel_projects.metrics import collect


def _collect(path: Path):
    identities = discover(path)
    return collect(identities[0])


def test_tc003_commits_on_main_and_not_on_main(tmp_path: Path) -> None:
    """TC-003: main mit 3 Commits, Feature-Branch mit 1 zusätzlichen."""
    repo = make_repo(tmp_path / "r", commits=3)
    git(repo, "checkout", "-q", "-b", "feature")
    add_commit(repo, "Nur im Feature")

    report = _collect(tmp_path)

    assert report.commits_on_main == 3
    assert report.commits_not_on_main == 1


def test_tc004_shared_commit_counts_once(tmp_path: Path) -> None:
    """TC-004: derselbe Commit auf 3 Branches zählt genau einmal."""
    repo = make_repo(tmp_path / "r", commits=2)
    git(repo, "checkout", "-q", "-b", "b1")
    add_commit(repo, "Geteilt", "shared.txt")
    # b2 und b3 werden von b1 abgezweigt — der Commit liegt auf allen dreien,
    # aber nicht auf main.
    git(repo, "checkout", "-q", "-b", "b2", "b1")
    git(repo, "checkout", "-q", "-b", "b3", "b1")

    report = _collect(tmp_path)

    # Der gemeinsame Commit darf nicht dreifach gezählt werden.
    assert report.commits_not_on_main == 1, report.unmerged_branches
    assert report.commits_on_main == 2
    assert report.branches_unmerged == 3


def test_tc005_branch_classification(tmp_path: Path) -> None:
    """TC-005: ein gemergter, ein ungemergter Branch."""
    repo = make_repo(tmp_path / "r", commits=2)
    git(repo, "checkout", "-q", "-b", "merged")
    add_commit(repo, "Wird gemergt")
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "-q", "--no-ff", "merged", "-m", "merge")
    git(repo, "checkout", "-q", "-b", "offen")
    add_commit(repo, "Bleibt offen", "offen.txt")

    report = _collect(tmp_path)

    assert report.branches_total == 3  # main, merged, offen
    assert report.branches_unmerged == 1
    assert [b.name for b in report.unmerged_branches] == ["offen"]


def test_tc006_unmerged_branch_has_commit_count(tmp_path: Path) -> None:
    """TC-006: der ungemergte Branch nennt seine Vorsprung-Commits."""
    repo = make_repo(tmp_path / "r", commits=1)
    git(repo, "checkout", "-q", "-b", "feature")
    for index in range(5):
        add_commit(repo, f"Commit {index}", f"c{index}.txt")

    report = _collect(tmp_path)

    assert report.branches_unmerged == 1
    assert report.unmerged_branches[0].name == "feature"
    assert report.unmerged_branches[0].commits_ahead == 5


def test_tc007_missing_origin_is_none_not_zero(tmp_path: Path) -> None:
    """TC-007: ohne origin ist ahead/behind unbekannt (None), nicht 0."""
    repo = make_repo(tmp_path / "r", commits=2)

    report = _collect(tmp_path)

    assert report.remote_url is None
    assert report.ahead_of_origin is None
    assert report.behind_origin is None


def test_tc008_dirty_files_are_counted(tmp_path: Path) -> None:
    """TC-008: geänderte Dateien im Working Tree werden gezählt."""
    repo = make_repo(tmp_path / "r", commits=1)
    (repo / "file0.txt").write_text("geändert\n", encoding="utf-8")
    (repo / "neu.txt").write_text("neu\n", encoding="utf-8")

    report = _collect(tmp_path)

    assert report.dirty_files >= 2


def test_repo_without_main_reports_all_commits_as_unmerged(tmp_path: Path) -> None:
    """Ein Repo ohne main/master: alle Commits zählen als 'nicht auf main'."""
    repo = make_repo(tmp_path / "r", commits=2, branch="trunk")

    report = _collect(tmp_path)

    assert report.default_branch is None
    assert report.commits_on_main == 0
    assert report.commits_not_on_main == report.commits_total
