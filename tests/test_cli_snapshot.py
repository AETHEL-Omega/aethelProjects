"""TC-068 — Snapshot als Eingabe (REQ-027)."""

import json
from pathlib import Path

import pytest
from conftest import make_repo

from aethel_projects.cli import main
from aethel_projects.scanner import load_snapshot, scan_workspace


def test_snapshot_rundlauf(tmp_path: Path) -> None:
    """Ein echter Scan bleibt beim JSON-Rundlauf erhalten."""
    root = tmp_path / "ws"
    make_repo(root / "alpha", commits=1)
    make_repo(root / "beta", commits=1)
    original = scan_workspace(root).as_dict()
    snapshot = tmp_path / "scan.json"
    snapshot.write_text(json.dumps(original), encoding="utf-8")
    assert load_snapshot(snapshot).as_dict() == original


@pytest.mark.parametrize("command", ["stack", "incubator", "applefirst", "audit"])
def test_sichten_mit_snapshot(tmp_path: Path, capsys, monkeypatch, command: str) -> None:
    """Sichten liefern dieselbe Ausgabe und scannen beim Laden nicht erneut."""
    root = tmp_path / "ws"
    make_repo(root / "alpha", commits=1)
    snapshot = tmp_path / "scan.json"
    snapshot.write_text(json.dumps(scan_workspace(root).as_dict()), encoding="utf-8")
    args = ["--root", str(root), command, "--format", "json"]
    assert main(args) == 0
    expected = json.loads(capsys.readouterr().out)

    def kein_scan(*args, **kwargs):
        raise AssertionError("Snapshot darf keinen Scan auslösen")

    monkeypatch.setattr("aethel_projects.cli.scan_workspace", kein_scan)
    assert main([*args, "--snapshot", str(snapshot)]) == 0
    assert json.loads(capsys.readouterr().out) == expected


def test_snapshot_falsches_schema(tmp_path: Path, capsys) -> None:
    """Ein fremdes Schema wird mit Exit 1 abgelehnt."""
    snapshot = tmp_path / "falsch.json"
    snapshot.write_text('{"schema": "falsch"}', encoding="utf-8")
    with pytest.raises(ValueError, match="aethel.projects/v1"):
        load_snapshot(snapshot)
    assert main(["--root", str(tmp_path), "audit", "--snapshot", str(snapshot)]) == 1
    assert "aethel.projects/v1" in capsys.readouterr().err


def test_snapshot_fehlt(tmp_path: Path, capsys) -> None:
    """Ein fehlender Snapshot nennt die Erzeugung und liefert Exit 2."""
    snapshot = tmp_path / "fehlt.json"
    with pytest.raises(FileNotFoundError, match="scan --json"):
        load_snapshot(snapshot)
    assert main(["--root", str(tmp_path), "audit", "--snapshot", str(snapshot)]) == 2
    assert "scan --json" in capsys.readouterr().err
