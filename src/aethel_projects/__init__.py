"""aethelProjects — Portfolio-Analyse des AETHEL-Workspace.

Ausschließlich lesend. Siehe docs/SPEC.md.
"""

from __future__ import annotations

from .codeanalysis import CodeAnalysis, analyse_repo, find_analyzer
from .continuity import Continuity, WorkspaceContinuity
from .continuity import build as build_continuity
from .discovery import RepoIdentity, discover
from .factory import FactoryView, Stage
from .factory import build as build_factory
from .forensics import Observation
from .forensics import inspect as inspect_forensics
from .forensics import inspect_workspace
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

__version__ = "0.2.0"

__all__ = [
    "CategorySummary",
    "CodeAnalysis",
    "Continuity",
    "FactoryView",
    "Finding",
    "Intent",
    "ManifestEntry",
    "Maturity",
    "Observation",
    "ProjectManagementView",
    "RepoIdentity",
    "RepoReport",
    "ScanResult",
    "ScanSummary",
    "Stage",
    "UnmergedBranch",
    "WorkspaceContinuity",
    "analyse_repo",
    "build_continuity",
    "build_factory",
    "collect",
    "discover",
    "find_analyzer",
    "inspect_forensics",
    "inspect_workspace",
    "render_html",
    "render_markdown",
    "scan_workspace",
    "to_json",
]
