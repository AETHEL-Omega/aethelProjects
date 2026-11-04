"""TC-046 bis TC-050 — Anbindung an aethelCodeAnalyzer (REQ-020).

Die Tests laufen **ohne** das echte Analyzer-Binary: sie benutzen ein
Attrappen-Skript, das denselben AIX-Vertrag ausgibt.
"""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import pytest

from aethel_projects import codeanalysis
from aethel_projects.models import Maturity, RepoReport


def _report(tmp_path: Path, name: str, *, cargo: bool = False, pubspec: bool = False) -> RepoReport:
    root = tmp_path / name
    root.mkdir(parents=True, exist_ok=True)
    if cargo:
        (root / "Cargo.toml").write_text("[package]\nname = \"x\"\n", encoding="utf-8")
    if pubspec:
        (root / "pubspec.yaml").write_text("name: x\n", encoding="utf-8")
    return RepoReport(
        name=name,
        path=str(root),
        git_common_dir=str(root / ".git"),
        is_worktree=False,
        worktree_paths=(),
        default_branch="main",
        current_branch="main",
        commits_total=1,
        commits_on_main=1,
        commits_not_on_main=0,
        branches_total=1,
        branches_unmerged=0,
        unmerged_branches=(),
        ahead_of_origin=None,
        behind_origin=None,
        dirty_files=0,
        last_commit_date="2026-10-01",
        last_commit_subject="Init",
        remote_url=None,
        intent=None,
        maturity=Maturity(score=50, grade="Solide", parts={}),
        manifest_entry=None,
        findings=(),
        pm_view=None,
    )


def _fake_analyzer(tmp_path: Path, payload: str, *, returncode: int = 0) -> Path:
    """Ein Attrappen-Binary, das den AIX-Vertrag ausgibt."""
    script = tmp_path / "fake-analyzer"
    script.write_text(
        "#!/bin/sh\n"
        f"cat <<'JSON'\n{payload}\nJSON\n"
        f"exit {returncode}\n",
        encoding="utf-8",
    )
    script.chmod(script.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return script


def test_tc046_directories_can_be_sent_to_existing_analyzer(tmp_path: Path) -> None:
    """Language coverage is reported by the analyzer, not guessed from manifests."""
    assert codeanalysis.is_analysable(_report(tmp_path, "rust", cargo=True))
    assert codeanalysis.is_analysable(_report(tmp_path, "dart", pubspec=True))
    assert codeanalysis.is_analysable(_report(tmp_path, "python"))


def test_tc047_findings_are_translated(tmp_path: Path) -> None:
    """TC-047: AIX-Findings werden ins Portfolio-Modell übersetzt."""
    payload = json.dumps(
        {
            "schema": codeanalysis.AIX_SCHEMA,
            "tool": "aethel",
            "truncated": False,
            "findings": [
                {
                    "tool": "aethel",
                    "kind": "smell",
                    "file": "src/lib.rs",
                    "line": 42,
                    "rule": "high-complexity",
                    "severity": "high",
                    "message": "Funktion ist komplex",
                    "evidence_tier": "proven",
                    "repro": "analyzer --assert-clean high-complexity",
                }
            ],
        }
    )
    binary = _fake_analyzer(tmp_path, payload)
    report = _report(tmp_path, "rust", cargo=True)

    analysis = codeanalysis.analyse_repo(report, binary=binary)

    assert analysis.available
    assert analysis.analyzed
    assert len(analysis.findings) == 1
    finding = analysis.findings[0]
    assert finding.severity == "critical"
    assert finding.code == "code:high-complexity"
    assert "src/lib.rs:42" in finding.message
    assert analysis.rule_counts == {"high-complexity": 1}


def test_tc048_wrong_schema_is_refused(tmp_path: Path) -> None:
    """TC-048: ein fremdes Schema wird nicht als Analyse gewertet."""
    payload = json.dumps({"schema": "etwas.anderes/v9", "findings": []})
    binary = _fake_analyzer(tmp_path, payload)
    report = _report(tmp_path, "rust", cargo=True)

    analysis = codeanalysis.analyse_repo(report, binary=binary)

    assert analysis.available
    assert not analysis.analyzed
    assert analysis.findings == ()
    assert "Unerwartetes Schema" in analysis.note


def test_tc049_missing_analyzer_is_reported_not_guessed(tmp_path: Path) -> None:
    """TC-049: fehlt der Analyzer, wird das gesagt — nicht geraten."""
    report = _report(tmp_path, "rust", cargo=True)

    analysis = codeanalysis.analyse_repo(report, binary=Path(tmp_path / "gibt-es-nicht"))

    assert not analysis.available
    assert not analysis.analyzed
    assert "nicht gefunden" in analysis.note


def test_tc050_failing_analyzer_is_reported(tmp_path: Path) -> None:
    """TC-050: ein Fehlschlag des Analyzers wird als Hinweis geführt."""
    binary = _fake_analyzer(tmp_path, "{}", returncode=3)
    report = _report(tmp_path, "rust", cargo=True)

    analysis = codeanalysis.analyse_repo(report, binary=binary)

    assert analysis.available
    assert not analysis.analyzed
    assert "rc=3" in analysis.note


def test_find_analyzer_prefers_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Die Umgebungsvariable schlägt die bekannten Pfade."""
    binary = _fake_analyzer(tmp_path, "{}")
    monkeypatch.setenv("AETHEL_CODE_ANALYZER_BIN", str(binary))

    assert codeanalysis.find_analyzer() == binary


def test_non_analysable_repo_is_skipped_with_note(tmp_path: Path) -> None:
    """Ein fehlendes Projektverzeichnis wird ausdrücklich gemeldet."""
    binary = _fake_analyzer(tmp_path, "{}")
    report = _report(tmp_path, "python")
    Path(report.path).rmdir()

    analysis = codeanalysis.analyse_repo(report, binary=binary)

    assert analysis.available
    assert not analysis.analyzed
    assert "nicht analysiert" in analysis.note


def test_python_and_coverage_are_kept(tmp_path: Path) -> None:
    report = _report(tmp_path, "python")
    Path(report.path, "main.py").write_text("pass\n")
    coverage = {"incomplete_reasons": ["limit"], "stub_coverage": {"python": "partial"}}
    binary = _fake_analyzer(tmp_path, json.dumps({"schema": codeanalysis.AIX_SCHEMA, "findings": [], "scan": coverage}))
    analysis = codeanalysis.analyse_repo(report, binary=binary)
    assert analysis.analyzed
    assert analysis.coverage == coverage
    assert "unvollstaendig" in analysis.note


def test_cli_exact_path_selects_only_matching_checkout(tmp_path, monkeypatch, capsys):
    from types import SimpleNamespace
    from aethel_projects import cli
    first = _report(tmp_path / 'one', 'same', cargo=True)
    second = _report(tmp_path / 'two', 'same', cargo=True)
    calls = []
    monkeypatch.setattr(cli, 'scan_workspace', lambda *a, **k: SimpleNamespace(repos=[first, second]))
    monkeypatch.setattr(codeanalysis, 'find_analyzer', lambda: tmp_path / 'installed')
    def analyze(repo, **kwargs):
        calls.append(repo.path)
        return codeanalysis.CodeAnalysis(True, True, codeanalysis.AIX_SCHEMA, (), {}, coverage={'incomplete_reasons': ['limit']})
    monkeypatch.setattr(codeanalysis, 'analyse_repo', analyze)
    args = SimpleNamespace(root=str(tmp_path), jobs=1, timeout=1, manifest=None, repo=None,
        repo_path=Path(second.path), limit=0, severity='info', format='json', out=None)
    assert cli._cmd_code(args) == 0
    assert calls == [second.path]
    result = json.loads(capsys.readouterr().out)
    assert result['analysen'][0]['coverage']['incomplete_reasons'] == ['limit']
    args.repo_path = tmp_path / 'missing'
    assert cli._cmd_code(args) == cli.EXIT_ERROR


def test_mismatched_analyzer_scope_is_rejected(tmp_path: Path) -> None:
    repo = _report(tmp_path, "one", cargo=True)
    binary = _fake_analyzer(tmp_path, json.dumps({"schema": codeanalysis.AIX_SCHEMA, "scope": str(tmp_path / 'two'), "findings": []}))
    result = codeanalysis.analyse_repo(repo, binary=binary)
    assert not result.analyzed
    assert 'Scope' in result.note
