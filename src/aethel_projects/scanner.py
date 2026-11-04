"""Orchestrierung: Discovery → Metriken → Ableitungen → ScanResult."""

from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime
from pathlib import Path

from . import findings as findings_mod
from . import intent as intent_mod
from . import manifest as manifest_mod
from . import maturity as maturity_mod
from . import pmview as pmview_mod
from .discovery import discover
from .metrics import collect
from .models import (
    CategorySummary, Finding, Intent, ManifestEntry, Maturity, ProjectManagementView,
    RepoReport, ScanResult, ScanSummary, UnmergedBranch,
)

STALE_DAYS = 90


def _size_kb(path: Path) -> int:
    total = 0
    for root, dirs, files in os.walk(path, onerror=lambda _e: None):
        dirs[:] = [d for d in dirs if d not in {".git", "build", "target", "node_modules"}]
        for name in files:
            try:
                total += os.path.getsize(os.path.join(root, name))
            except OSError:
                continue
    return total // 1024


def _median(values: list[int]) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) // 2


def _derive(
    report: RepoReport,
    manifest: dict[str, manifest_mod.ManifestEntry],
) -> RepoReport:
    """Hängt Manifest-Eintrag, Intent, Reifegrad, Findings und PM-View an."""
    updated = report
    entry = manifest.get(report.name)
    if entry is not None:
        updated = replace(updated, manifest_entry=entry)

    updated = replace(updated, intent=intent_mod.infer(updated))
    updated = replace(updated, maturity=maturity_mod.score(updated))
    updated = replace(updated, findings=findings_mod.detect(updated))
    updated = replace(updated, pm_view=pmview_mod.build(updated))
    return updated


def load_snapshot(path: Path | str) -> ScanResult:
    """Lädt einen Scan-Snapshot und stellt seine Datenmodelle wieder her."""
    snapshot = Path(path).expanduser()
    try:
        document = json.loads(snapshot.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Snapshot nicht gefunden: {snapshot} (erzeugen mit: scan --json <pfad>)"
        ) from exc
    if not isinstance(document, dict) or document.get("schema") != "aethel.projects/v1":
        raise ValueError("Erwartet: Scan-Snapshot mit Schema aethel.projects/v1")

    repos = []
    for item in document["repos"]:
        data = dict(item)
        data["worktree_paths"] = tuple(data["worktree_paths"])
        data["unmerged_branches"] = tuple(UnmergedBranch(**branch) for branch in data["unmerged_branches"])
        data["intent"] = Intent(**data["intent"]) if data["intent"] is not None else None
        data["maturity"] = Maturity(**data["maturity"]) if data["maturity"] is not None else None
        manifest = data.pop("manifest")
        data["manifest_entry"] = ManifestEntry(**manifest) if manifest is not None else None
        data["findings"] = tuple(Finding(**finding) for finding in data["findings"])
        pm = data["pm_view"]
        data["pm_view"] = (ProjectManagementView(**{**pm, "next_actions": tuple(pm["next_actions"])})
                           if pm is not None else None)
        repos.append(RepoReport(**data))
    return ScanResult(
        generated_at=document["generated_at"], workspace_root=document["workspace_root"],
        repos=tuple(repos), findings=tuple(Finding(**finding) for finding in document["findings"]),
        categories=tuple(CategorySummary(**category) for category in document["categories"]),
        summary=ScanSummary(**document["summary"]),
    )


def scan_workspace(
    root: Path | str,
    jobs: int = 8,
    timeout: int = 30,
    manifest_path: Path | str | None = None,
) -> ScanResult:
    """Vermisst den gesamten Workspace und liefert das Analyseergebnis."""
    root_path = Path(root).expanduser().resolve()
    identities = discover(root_path)
    manifest = manifest_mod.load_manifest(manifest_path)

    if identities:
        with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
            reports = list(pool.map(lambda i: collect(i, timeout=timeout), identities))
    else:
        reports = []

    reports = [_derive(report, manifest) for report in reports]
    reports.sort(key=lambda r: r.name.lower())

    all_findings: list[Finding] = []
    for report in reports:
        all_findings.extend(report.findings)
    all_findings.extend(findings_mod.detect_duplicates(tuple(reports)))
    all_findings.extend(manifest_mod.compare(tuple(reports), manifest))
    severity_order = {"critical": 0, "warn": 1, "info": 2}
    all_findings.sort(key=lambda f: (severity_order.get(f.severity, 3), f.repo.lower(), f.code))

    buckets: dict[str, list[RepoReport]] = {}
    for report in reports:
        buckets.setdefault(report.category, []).append(report)
    categories = tuple(
        CategorySummary(
            name=name,
            repos=len(group),
            commits_total=sum(r.commits_on_main + r.commits_not_on_main for r in group),
            commits_not_on_main=sum(r.commits_not_on_main for r in group),
            branches=sum(r.branches_total for r in group),
            median_maturity=_median([r.maturity.score if r.maturity else 0 for r in group]),
        )
        for name, group in sorted(buckets.items())
    )

    worktree_dirs = sum(len(r.worktree_paths) for r in reports)
    stale = sum(
        1
        for r in reports
        if r.last_commit_date
        and (datetime.now().date() - datetime.strptime(r.last_commit_date, "%Y-%m-%d").date()).days
        > STALE_DAYS
    )

    summary = ScanSummary(
        repos=len(reports),
        worktree_dirs=worktree_dirs,
        commits_total=sum(r.commits_total for r in reports),
        commits_on_main=sum(r.commits_on_main for r in reports),
        commits_not_on_main=sum(r.commits_not_on_main for r in reports),
        branches=sum(r.branches_total for r in reports),
        dirty_repos=sum(1 for r in reports if r.dirty_files > 0),
        stale_repos=stale,
        repos_without_main=sum(1 for r in reports if r.default_branch is None),
        repos_without_remote=sum(1 for r in reports if not r.remote_url),
        total_size_kb=sum(_size_kb(Path(r.path)) for r in reports),
    )

    return ScanResult(
        generated_at=datetime.now().astimezone().isoformat(timespec="seconds"),
        workspace_root=str(root_path),
        repos=tuple(reports),
        findings=tuple(all_findings),
        categories=categories,
        summary=summary,
    )
