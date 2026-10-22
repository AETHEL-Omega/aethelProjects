"""TC-009 bis TC-012 — Report-Renderer (REQ-005, REQ-006)."""

from __future__ import annotations

import json
from pathlib import Path

from conftest import make_repo

from aethel_projects.discovery import discover
from aethel_projects.metrics import collect
from aethel_projects.report import render_html, render_markdown, to_json
from aethel_projects.scanner import scan_workspace


def _scan(tmp_path: Path):
    make_repo(tmp_path / "erstes", commits=2)
    make_repo(tmp_path / "zweites", commits=1)
    return scan_workspace(tmp_path)


def test_tc009_json_has_stable_schema(tmp_path: Path) -> None:
    """TC-009: JSON trägt schema, generated_at, summary und repos."""
    result = _scan(tmp_path)

    payload = json.loads(to_json(result))

    assert payload["schema"] == "aethel.projects/v1"
    assert "generated_at" in payload
    assert payload["summary"]["repos"] == 2
    assert len(payload["repos"]) == 2


def test_tc010_every_repo_carries_all_fields(tmp_path: Path) -> None:
    """TC-010: auch 'unbekannte' Werte erscheinen als Feld (nicht als fehlender Schlüssel)."""
    result = _scan(tmp_path)

    payload = json.loads(to_json(result))

    required = {
        "name", "path", "default_branch", "commits_total", "commits_on_main",
        "commits_not_on_main", "branches_total", "ahead_of_origin", "dirty_files",
        "last_commit_date", "intent", "maturity", "findings",
    }
    for repo in payload["repos"]:
        assert required <= set(repo)


def test_tc011_markdown_contains_summary_and_tables(tmp_path: Path) -> None:
    """TC-011: Markdown enthält Summary, Kategorien und Repo-Tabelle."""
    result = _scan(tmp_path)

    text = render_markdown(result)

    assert "# AETHEL Portfolio-Übersicht" in text
    assert "Commits NICHT auf main" in text
    assert "## Kategorien" in text
    assert "erstes" in text and "zweites" in text


def test_tc012_html_is_wellformed(tmp_path: Path) -> None:
    """TC-012: HTML enthält Tabellen und alle Repo-Namen."""
    result = _scan(tmp_path)

    html = render_html(result)

    assert html.startswith("<!doctype html>")
    assert "<table>" in html
    assert "</html>" in html
    assert "erstes" in html and "zweites" in html


def test_worktrees_are_deduplicated_in_the_report(tmp_path: Path) -> None:
    """Ein Worktree taucht nicht als eigenes Repository im Report auf."""
    import subprocess

    main = make_repo(tmp_path / "projekt", commits=2)
    subprocess.run(
        ["git", "-C", str(main), "worktree", "add", "-q", "-b", "wt", str(tmp_path / "wt")],
        check=True,
        capture_output=True,
    )

    result = scan_workspace(tmp_path)

    assert [r.name for r in result.repos] == ["projekt"]
    assert result.summary.worktree_dirs == 1


def test_summary_totals_are_consistent(tmp_path: Path) -> None:
    """Die Summary-Summen ergeben sich aus den Repos."""
    result = _scan(tmp_path)

    assert result.summary.commits_total == sum(r.commits_total for r in result.repos)
    assert result.summary.commits_not_on_main == sum(
        r.commits_not_on_main for r in result.repos
    )
    assert result.summary.branches == sum(r.branches_total for r in result.repos)
