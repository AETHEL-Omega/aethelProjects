"""aethelProjects — Portfolio-Analyse des AETHEL-Workspace.

Ausschließlich lesend. Siehe docs/SPEC.md.
"""

from __future__ import annotations

from .discovery import RepoIdentity, discover
from .metrics import collect
from .models import (
    CategorySummary,
    Finding,
    Intent,
    ManifestEntry,
    Maturity,
    ProjectManagementView,
    RepoReport,
    ScanResult,
    ScanSummary,
    UnmergedBranch,
)
from .report import render_html, render_markdown, to_json
from .scanner import scan_workspace

__version__ = "0.1.0"

__all__ = [
    "CategorySummary",
    "Finding",
    "Intent",
    "ManifestEntry",
    "Maturity",
    "ProjectManagementView",
    "RepoIdentity",
    "RepoReport",
    "ScanResult",
    "ScanSummary",
    "UnmergedBranch",
    "collect",
    "discover",
    "render_html",
    "render_markdown",
    "scan_workspace",
    "to_json",
]
