"""TC-015, TC-016 — CLI (REQ-008)."""

from __future__ import annotations

import json
from pathlib import Path

from conftest import make_repo

from aethel_projects.cli import main


def test_tc015_help_lists_all_subcommands(capsys) -> None:
    """TC-015: --help listet scan, report, audit und market."""
    with pytest_raises_system_exit():
        main(["--help"])
    out = capsys.readouterr().out
    for command in ("scan", "report", "audit", "market"):
        assert command in out


def pytest_raises_system_exit():
    import pytest

    return pytest.raises(SystemExit)


def test_tc016_scan_writes_parseable_json(tmp_path: Path) -> None:
    """TC-016: 'scan --json <datei>' erzeugt gültiges JSON und Exit-Code 0."""
    make_repo(tmp_path / "projekt", commits=2)
    target = tmp_path / "out" / "scan.json"

    code = main(["--root", str(tmp_path), "scan", "--json", str(target)])

    assert code == 0
    assert target.is_file()
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["schema"] == "aethel.projects/v1"
    assert payload["summary"]["repos"] == 1


def test_report_writes_markdown(tmp_path: Path) -> None:
    """'report --format md' schreibt eine Markdown-Datei."""
    make_repo(tmp_path / "projekt", commits=1)
    out_dir = tmp_path / "reports"

    code = main(["--root", str(tmp_path), "report", "--format", "md", "--out", str(out_dir)])

    assert code == 0
    target = out_dir / "aethel-projects.md"
    assert target.is_file()
    assert "AETHEL Portfolio-Übersicht" in target.read_text(encoding="utf-8")


def test_audit_outputs_findings(tmp_path: Path) -> None:
    """'audit --format json' liefert eine Finding-Liste."""
    make_repo(tmp_path / "projekt", commits=1)

    code = main(["--root", str(tmp_path), "audit", "--format", "json"])

    assert code == 0


def test_market_outputs_view(tmp_path: Path) -> None:
    """'market --format json' liefert den Marktview mit scope 'internal'."""
    make_repo(tmp_path / "projekt", commits=1)

    code = main(["--root", str(tmp_path), "market", "--format", "json"])

    assert code == 0


def test_unreadable_root_returns_error_code(tmp_path: Path) -> None:
    """Ein nicht existierender Root ⇒ Exit-Code 1."""
    code = main(["--root", str(tmp_path / "gibt_es_nicht"), "scan", "--json", "-"])
    assert code == 1
