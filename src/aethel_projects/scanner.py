"""Orchestrierung: Discovery → Metriken → Ableitungen → ScanResult."""

from __future__ import annotations

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
from .models import CategorySummary, Finding, RepoReport, ScanResult, ScanSummary

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
