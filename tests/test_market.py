"""TC-027 bis TC-029 — Marktview, USP, Marketing (REQ-014, REQ-015)."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from conftest import make_repo

from aethel_projects.discovery import discover
from aethel_projects.market import build, claims
from aethel_projects.metrics import collect
from aethel_projects.models import Intent, ManifestEntry


def _report(root: Path, name: str):
    for identity in discover(root):
        if identity.name == name:
            return collect(identity)
    raise AssertionError(f"{name} nicht gefunden")


def _with_manifest(report, category: str):
    return replace(
        report,
        manifest_entry=ManifestEntry(
            name=report.name, category=category, status="active", last_commit=None, remote=None
        ),
    )


def test_tc027_market_view_is_internal_scoped(tmp_path: Path) -> None:
    """TC-027: der Marktview ist als 'internal' gekennzeichnet und zählt Kategorien."""
    make_repo(tmp_path / "a", commits=1)
    make_repo(tmp_path / "b", commits=1)
    reports = (
        _with_manifest(_report(tmp_path, "a"), "kernel"),
        _with_manifest(_report(tmp_path, "b"), "omega"),
    )

    view = build(reports)

    assert view.scope == "internal"
    assert {c.name for c in view.categories} == {"kernel", "omega"}
    assert all(c.repos == 1 for c in view.categories)


def test_tc028_sole_category_repo_with_many_commits_is_usp(tmp_path: Path) -> None:
    """TC-028: einziges Repo einer Kategorie mit 600 Commits ⇒ USP 'Alleinsteller'."""
    make_repo(tmp_path / "solo", commits=1)
    report = replace(
        _with_manifest(_report(tmp_path, "solo"), "kernel"),
        commits_on_main=600,
        commits_not_on_main=0,
    )

    view = build((report,))

    alone = [u for u in view.usps if u.kind == "Alleinsteller"]
    assert alone
    assert alone[0].repo == "solo"
    assert "600" in alone[0].claim
    assert alone[0].evidence


def test_tc029_claims_require_evidence(tmp_path: Path) -> None:
    """TC-029: Claims nennen messbare Zahlen; ohne Evidenz kein Claim."""
    make_repo(tmp_path / "a", commits=1)
    report = replace(_report(tmp_path, "a"), commits_on_main=800)

    found = claims(report)

    assert any("800" in claim for claim in found)


def test_no_claims_without_evidence(tmp_path: Path) -> None:
    """Ein leeres Repo ohne Reifegrad, ohne Commits, dirty ⇒ kein Claim."""
    make_repo(tmp_path / "leer", commits=1)
    report = replace(
        _report(tmp_path, "leer"),
        commits_on_main=0,
        commits_total=0,
        branches_total=0,
        dirty_files=3,
        remote_url=None,
    )

    assert claims(report) == ()


def test_positioning_is_assigned_per_category(tmp_path: Path) -> None:
    """Jedes Repo erhält eine Position innerhalb seiner Kategorie."""
    make_repo(tmp_path / "a", commits=1)
    make_repo(tmp_path / "b", commits=1)
    reports = (
        _with_manifest(_report(tmp_path, "a"), "kernel"),
        _with_manifest(_report(tmp_path, "b"), "kernel"),
    )

    view = build(reports)

    assert set(view.positioning) == {"a", "b"}
    assert all("/2 in 'kernel'" in value for value in view.positioning.values())
