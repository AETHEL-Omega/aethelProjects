"""Register-Abgleich — Scan, Manifest, Projektprofile und Aufträge gegeneinander.

Die Tests laufen vollständig in ``tmp_path``: kein Netz, kein echter Workspace.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import replace
from pathlib import Path

import pytest
from conftest import make_repo

from aethel_projects import registers
from aethel_projects.manifest import load_manifest
from aethel_projects.models import ManifestEntry, RepoReport
from aethel_projects.registers import (
    MAX_LIST,
    RegisterDrift,
    find_profiles,
    load_auftraege,
    load_scan,
    reconcile,
    render_json,
    render_markdown,
    repo_ref,
)
from aethel_projects.report import to_json
from aethel_projects.scanner import scan_workspace

MANIFEST = """# AETHEL Workspace Manifest
projects:
  - name: alpha
    category: core
    status: active
    last_commit: "2026-01-01"
    remote: "https://github.com/AETHEL-Omega/alpha.git"
  - name: geist
    category: scratch
    status: scratch
    last_commit: "2026-05-05"
    remote: ""
"""


def _entry(name: str) -> ManifestEntry:
    return ManifestEntry(name=name, category="core", status="active", last_commit=None, remote=None)


def _manifest(*names: str) -> dict[str, ManifestEntry]:
    return {name: _entry(name) for name in names}


def _repo(name: str, *, worktree: bool = False) -> dict:
    return {"name": name, "path": f"/x/{name}", "is_worktree": worktree, "worktree_paths": []}


def _write_profile(root: Path, relative: str, content: str | dict) -> Path:
    folder = root / relative
    (folder / ".aix").mkdir(parents=True)
    text = content if isinstance(content, str) else json.dumps(content)
    (folder / ".aix" / "project-profile.json").write_text(text, encoding="utf-8")
    return folder


def _write_scan(path: Path, empty_report: RepoReport) -> Path:
    """Scan-JSON in der Form von ``scan --json``: drei Repos, davon ein Worktree."""
    repos = [
        replace(empty_report, name="alpha", remote_url="https://github.com/AETHEL-Omega/alpha.git"),
        replace(empty_report, name="beta"),
        replace(empty_report, name="gamma", is_worktree=True),
    ]
    document = {"schema": "aethel.projects/v1", "summary": {}, "repos": [r.as_dict() for r in repos]}
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def _snapshot(root: Path) -> dict[str, tuple[int, int]]:
    """Dateibaum mit Größe und mtime — Beleg für 'nur lesend'."""
    return {
        str(p.relative_to(root)): (p.stat().st_size, p.stat().st_mtime_ns)
        for p in sorted(root.rglob("*"))
    }


# ----------------------------------------------------------------------- Gesamtfall


def test_reconcile_full_scenario_checks_every_field(tmp_path: Path, empty_report: RepoReport) -> None:
    """Drei Scan-Repos (ein Worktree), zwei Manifest-Namen (einer tot), zwei Profile, drei Auftragszeilen."""
    scan = load_scan(_write_scan(tmp_path / "scan.json", empty_report))
    manifest_path = tmp_path / "projects.yaml"
    manifest_path.write_text(MANIFEST, encoding="utf-8")
    manifest = load_manifest(manifest_path)

    root = tmp_path / "ws"
    _write_profile(root, "alpha", {"name": "alpha"})
    _write_profile(root, "waise", {"name": "waise"})
    profiles = find_profiles(root)

    auftraege_path = tmp_path / "auftraege.jsonl"
    auftraege_path.write_text(
        "\n".join(
            [
                '{"id": "a-1", "repo": "unbekannt"}',
                "{das ist kein json",
                '{"id": "a-2", "pfad": "/irgendwo/alpha/"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    auftraege, lines = load_auftraege(auftraege_path)

    drift = reconcile(
        scan, manifest, profiles, auftraege, manifest_path=manifest_path, auftraege_lines=lines
    )

    assert drift.missing_in_manifest == ("beta",)
    assert drift.dead_manifest_entries == ("geist",)
    assert drift.unregistered_worktrees == ("gamma",)
    assert drift.profiles_without_manifest == ("waise",)
    assert drift.profiles_without_repo == ("waise",)
    assert drift.auftraege_unknown_repos == ("unbekannt",)
    assert drift.manifest_age_days is not None and drift.manifest_age_days >= 0
    assert drift.counts == {
        "scan_repos": 2,
        "scan_worktrees": 1,
        "manifest_entries": 2,
        "profiles": 2,
        "auftraege_lines": 3,
        "auftraege_parsed": 2,
    }
    assert drift.has_drift is True


def test_reconcile_works_on_a_real_scan_snapshot(tmp_path: Path) -> None:
    """Vertragstest: der Abgleich versteht das, was ``scan --json`` wirklich schreibt."""
    workspace = tmp_path / "ws"
    make_repo(workspace / "alpha", commits=1)
    make_repo(workspace / "beta", commits=1)
    manifest_path = tmp_path / "projects.yaml"
    manifest_path.write_text(MANIFEST, encoding="utf-8")
    snapshot = tmp_path / "scan.json"
    snapshot.write_text(to_json(scan_workspace(workspace, manifest_path=manifest_path)), encoding="utf-8")

    drift = reconcile(load_scan(snapshot), load_manifest(manifest_path), {}, [], manifest_path=manifest_path)

    assert drift.missing_in_manifest == ("beta",)
    assert drift.dead_manifest_entries == ("geist",)
    assert drift.unregistered_worktrees == ()
    assert drift.counts["scan_repos"] == 2


def test_profiles_are_split_into_the_two_categories(tmp_path: Path) -> None:
    """Im Scan aber nicht im Manifest ≠ im Manifest aber nicht im Scan."""
    drift = reconcile(
        [_repo("beta")],
        _manifest("geist"),
        {"beta": {}, "geist": {}},
        [],
    )

    assert drift.profiles_without_manifest == ("beta",)
    assert drift.profiles_without_repo == ("geist",)


def test_profile_declared_name_counts_as_a_match() -> None:
    """Ein Profil in einem fremd benannten Ordner gilt über 'repo'/'name' als bekannt."""
    drift = reconcile(
        [_repo("alpha")],
        _manifest("alpha"),
        {"kopie": {"repo": "AETHEL-Omega/alpha"}, "fremd": {"name": "AETHEL Fremd Projekt"}},
        [],
    )

    assert drift.profiles_without_manifest == ("fremd",)
    assert drift.profiles_without_repo == ("fremd",)


def test_worktree_name_in_manifest_is_neither_dead_nor_unregistered() -> None:
    drift = reconcile([_repo("gamma", worktree=True)], _manifest("gamma"), {}, [])

    assert drift.dead_manifest_entries == ()
    assert drift.unregistered_worktrees == ()
    assert drift.missing_in_manifest == ()


def test_names_are_compared_case_sensitively() -> None:
    drift = reconcile([_repo("Alpha")], _manifest("alpha"), {}, [])

    assert drift.missing_in_manifest == ("Alpha",)
    assert drift.dead_manifest_entries == ("alpha",)


def test_auftraege_unknown_repos_are_deduplicated_and_sorted() -> None:
    auftraege = [
        {"repo": "zeta"},
        {"projekt": "mu"},
        {"path": "/irgendwo/zeta"},
        {"repo": "alpha"},  # im Scan bekannt
        {"repo": "nur-im-manifest"},  # im Manifest bekannt
        {"keine": "referenz"},
    ]

    drift = reconcile([_repo("alpha")], _manifest("nur-im-manifest"), {}, auftraege)

    assert drift.auftraege_unknown_repos == ("mu", "zeta")


def test_scan_entries_without_a_name_are_ignored() -> None:
    drift = reconcile([{"path": "/x"}, {"name": ""}, {"name": 7}, "kaputt", _repo("alpha")], {}, {}, [])  # type: ignore[list-item]

    assert drift.missing_in_manifest == ("alpha",)
    assert drift.counts["scan_repos"] == 1


def test_auftraege_lines_never_below_parsed() -> None:
    drift = reconcile([], {}, {}, [{"repo": "x"}, {"repo": "y"}], auftraege_lines=0)

    assert drift.counts["auftraege_lines"] == 2
    assert drift.counts["auftraege_parsed"] == 2


# ----------------------------------------------------------------------- Manifest-Alter


def test_manifest_age_days_from_mtime(tmp_path: Path) -> None:
    manifest_path = tmp_path / "projects.yaml"
    manifest_path.write_text(MANIFEST, encoding="utf-8")
    ten_days_ago = time.time() - 10 * 86_400 - 120
    os.utime(manifest_path, (ten_days_ago, ten_days_ago))

    drift = reconcile([], load_manifest(manifest_path), {}, [], manifest_path=manifest_path)

    assert drift.manifest_age_days == 10


def test_manifest_age_is_none_without_a_usable_path(tmp_path: Path) -> None:
    assert reconcile([], {}, {}, []).manifest_age_days is None
    assert reconcile([], {}, {}, [], manifest_path=tmp_path / "gibt-es-nicht.yaml").manifest_age_days is None


def test_manifest_age_is_never_negative(tmp_path: Path) -> None:
    manifest_path = tmp_path / "projects.yaml"
    manifest_path.write_text(MANIFEST, encoding="utf-8")
    future = time.time() + 3 * 86_400
    os.utime(manifest_path, (future, future))

    assert reconcile([], {}, {}, [], manifest_path=manifest_path).manifest_age_days == 0


# ----------------------------------------------------------------------- Leere Eingaben


def test_empty_inputs_yield_empty_tuples_and_no_closing_sentence() -> None:
    drift = reconcile([], {}, {}, [])

    for name, _title in registers.CATEGORIES:
        assert getattr(drift, name) == ()
    assert drift.manifest_age_days is None
    assert drift.has_drift is False
    assert all(value == 0 for value in drift.counts.values())
    assert registers.CLOSING not in render_markdown(drift)
    assert "Produkt-ID" not in render_markdown(RegisterDrift())


# ----------------------------------------------------------------------- load_scan


def test_load_scan_missing_file_hints_at_scan_json(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match=r"scan --json"):
        load_scan(tmp_path / "scan.json")


def test_load_scan_returns_the_repo_list(tmp_path: Path, empty_report: RepoReport) -> None:
    repos = load_scan(_write_scan(tmp_path / "scan.json", empty_report))

    assert [r["name"] for r in repos] == ["alpha", "beta", "gamma"]
    assert [r["is_worktree"] for r in repos] == [False, False, True]
    assert repos[0]["remote_url"] == "https://github.com/AETHEL-Omega/alpha.git"


@pytest.mark.parametrize("content", ["{nicht json", "[]", '{"summary": {}}', '{"repos": "x"}'])
def test_load_scan_rejects_what_is_not_a_snapshot(tmp_path: Path, content: str) -> None:
    path = tmp_path / "scan.json"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError):
        load_scan(path)


# ----------------------------------------------------------------------- find_profiles


def test_find_profiles_reads_by_folder_name_up_to_max_depth(tmp_path: Path) -> None:
    _write_profile(tmp_path, "flach", {"name": "flach"})
    _write_profile(tmp_path, "gruppe/tief", {"name": "tief"})
    _write_profile(tmp_path, "gruppe/tief/zu-tief", {"name": "zu-tief"})

    assert set(find_profiles(tmp_path)) == {"flach", "tief"}
    assert set(find_profiles(tmp_path, max_depth=1)) == {"flach"}
    assert set(find_profiles(tmp_path, max_depth=3)) == {"flach", "tief", "zu-tief"}
    assert find_profiles(tmp_path, max_depth=0) == {}
    assert find_profiles(tmp_path)["flach"] == {"name": "flach"}


def test_find_profiles_skips_hidden_and_build_directories(tmp_path: Path) -> None:
    _write_profile(tmp_path, "echt", {"name": "echt"})
    for skipped in (".versteckt", "node_modules", "target", "build"):
        _write_profile(tmp_path, f"{skipped}/repo", {"name": skipped})
        _write_profile(tmp_path, skipped, {"name": skipped})

    assert set(find_profiles(tmp_path)) == {"echt"}


def test_find_profiles_skips_invalid_json_and_non_objects(tmp_path: Path) -> None:
    _write_profile(tmp_path, "gut", {"name": "gut"})
    _write_profile(tmp_path, "kaputt", "{nicht json")
    _write_profile(tmp_path, "liste", "[1, 2]")
    _write_profile(tmp_path, "leer", "")
    (tmp_path / "ohne-profil" / ".aix").mkdir(parents=True)

    assert set(find_profiles(tmp_path)) == {"gut"}


def test_find_profiles_prefers_the_shallower_folder_on_name_clash(tmp_path: Path) -> None:
    _write_profile(tmp_path, "a/dup", {"wo": "tief"})
    _write_profile(tmp_path, "dup", {"wo": "flach"})

    assert find_profiles(tmp_path)["dup"] == {"wo": "flach"}


def test_find_profiles_missing_root_is_empty(tmp_path: Path) -> None:
    assert find_profiles(tmp_path / "gibt-es-nicht") == {}


# ----------------------------------------------------------------------- load_auftraege


def test_load_auftraege_none_or_missing_is_empty(tmp_path: Path) -> None:
    assert load_auftraege(None) == ([], 0)
    assert load_auftraege(tmp_path / "gibt-es-nicht.jsonl") == ([], 0)


def test_load_auftraege_counts_broken_lines_but_does_not_parse_them(tmp_path: Path) -> None:
    path = tmp_path / "auftraege.jsonl"
    path.write_text(
        '{"repo": "a"}\n\n   \n{kaputt\n[1, 2]\n"text"\n{"repo": "b"}\n',
        encoding="utf-8",
    )

    parsed, lines = load_auftraege(path)

    assert parsed == [{"repo": "a"}, {"repo": "b"}]
    assert lines == 5  # leere Zeilen zählen nicht


def test_load_auftraege_survives_invalid_utf8(tmp_path: Path) -> None:
    path = tmp_path / "auftraege.jsonl"
    path.write_bytes(b'{"repo": "a"}\n\xff\xfe{"repo": "b"}\n{"ziel": "caf\xe9"}\n')

    parsed, lines = load_auftraege(path)

    assert lines == 3
    assert parsed[0] == {"repo": "a"}


# ----------------------------------------------------------------------- repo_ref


@pytest.mark.parametrize("key", ["repo", "projekt", "project", "pfad", "path", "ziel"])
def test_repo_ref_reads_every_documented_key(key: str) -> None:
    assert repo_ref({key: "aethelFoo"}) == "aethelFoo"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("/Users/x/workspace/aethelFoo", "aethelFoo"),
        ("/Users/x/workspace/aethelFoo/", "aethelFoo"),
        ("~/workspace/aethelFoo", "aethelFoo"),
        ("AETHEL-Omega/aethelFoo", "aethelFoo"),
        ("https://github.com/AETHEL-Omega/aethelFoo", "aethelFoo"),
        ("C:\\work\\aethelFoo", "aethelFoo"),
        ("/Users/x/Mein Ordner/aethelFoo", "aethelFoo"),
        ("  aethelFoo  ", "aethelFoo"),
    ],
)
def test_repo_ref_takes_the_last_path_component(value: str, expected: str) -> None:
    assert repo_ref({"pfad": value}) == expected


@pytest.mark.parametrize(
    "auftrag",
    [
        {},
        {"id": "a-1"},
        {"repo": None},
        {"repo": 42},
        {"repo": ["a"]},
        {"repo": {"name": "a"}},
        {"repo": ""},
        {"repo": "   "},
        {"repo": "/"},
        {"repo": ".."},
        {"ziel": "Dokumentation verbessern"},  # Freitext ist kein Repo
    ],
)
def test_repo_ref_is_none_without_a_usable_value(auftrag: dict) -> None:
    assert repo_ref(auftrag) is None


def test_repo_ref_uses_key_priority_and_falls_through_unusable_values() -> None:
    assert repo_ref({"ziel": "z", "path": "/p/y", "repo": "x"}) == "x"
    assert repo_ref({"repo": "", "projekt": None, "path": "/p/y"}) == "y"
    assert repo_ref({"repo": "Freitext mit Leerzeichen", "pfad": "/p/y"}) == "y"
    assert repo_ref("kein dict") is None  # type: ignore[arg-type]


# ----------------------------------------------------------------------- Ausgabe


def _drift_with_everything() -> RegisterDrift:
    return RegisterDrift(
        missing_in_manifest=("beta",),
        dead_manifest_entries=("geist",),
        unregistered_worktrees=("gamma",),
        profiles_without_manifest=("waise",),
        profiles_without_repo=("waise",),
        auftraege_unknown_repos=("unbekannt",),
        manifest_age_days=12,
        counts={
            "scan_repos": 2,
            "scan_worktrees": 1,
            "manifest_entries": 2,
            "profiles": 2,
            "auftraege_lines": 3,
            "auftraege_parsed": 2,
        },
    )


def test_render_markdown_has_header_counts_names_and_closing_sentence() -> None:
    text = render_markdown(_drift_with_everything())

    assert text.startswith("# Register-Abgleich")
    assert "| Scan: Repos | 2 |" in text
    assert "| Scan: Worktrees | 1 |" in text
    assert "| Aufträge: Zeilen | 3 |" in text
    assert "| Manifest: Alter in Tagen | 12 |" in text
    for name in ("beta", "geist", "gamma", "waise", "unbekannt"):
        assert f"- `{name}`" in text
    assert "Kein Register ist Wahrheit; Produkt-ID fehlt" in text
    assert text.rstrip().endswith(registers.CLOSING)


def test_render_markdown_lists_every_category_and_marks_empty_ones() -> None:
    text = render_markdown(RegisterDrift(missing_in_manifest=("beta",)))

    for _name, title in registers.CATEGORIES:
        assert f"## {title} (" in text
    assert text.count("Keine.") == len(registers.CATEGORIES) - 1
    assert "Kein Register ist Wahrheit" in text  # eine Kategorie nicht leer


def test_render_markdown_truncates_long_lists() -> None:
    names = tuple(f"repo-{index:03d}" for index in range(MAX_LIST + 13))

    text = render_markdown(RegisterDrift(missing_in_manifest=names))

    assert f"- `repo-{MAX_LIST - 1:03d}`" in text
    assert f"repo-{MAX_LIST:03d}" not in text
    assert "… und 13 weitere" in text
    assert f"({MAX_LIST + 13})" in text  # die Überschrift nennt die volle Zahl


def test_render_markdown_does_not_truncate_at_the_limit() -> None:
    names = tuple(f"repo-{index:03d}" for index in range(MAX_LIST))

    text = render_markdown(RegisterDrift(missing_in_manifest=names))

    assert "weitere" not in text
    assert f"- `repo-{MAX_LIST - 1:03d}`" in text


def test_render_markdown_age_unknown_is_a_dash() -> None:
    assert "| Manifest: Alter in Tagen | - |" in render_markdown(RegisterDrift())


def test_render_json_is_valid_sorted_and_keeps_umlauts() -> None:
    drift = replace(_drift_with_everything(), missing_in_manifest=("bär",))

    text = render_json(drift)
    data = json.loads(text)

    assert data == drift.as_dict()
    assert data["missing_in_manifest"] == ["bär"]
    assert "bär" in text  # ensure_ascii=False
    assert list(data) == sorted(data)
    assert text.startswith("{\n  ")  # indent=2
    assert data["manifest_age_days"] == 12
    assert data["counts"]["auftraege_parsed"] == 2


def test_as_dict_turns_tuples_into_lists_and_copies_counts() -> None:
    drift = _drift_with_everything()

    data = drift.as_dict()
    data["counts"]["scan_repos"] = 99

    assert isinstance(data["missing_in_manifest"], list)
    assert drift.counts["scan_repos"] == 2


# ----------------------------------------------------------------------- Nur lesend


def test_reconcile_pipeline_does_not_modify_its_inputs(tmp_path: Path, empty_report: RepoReport) -> None:
    _write_scan(tmp_path / "scan.json", empty_report)
    (tmp_path / "projects.yaml").write_text(MANIFEST, encoding="utf-8")
    (tmp_path / "auftraege.jsonl").write_text('{"repo": "x"}\n{kaputt\n', encoding="utf-8")
    _write_profile(tmp_path / "ws", "alpha", {"name": "alpha"})
    before = _snapshot(tmp_path)

    scan = load_scan(tmp_path / "scan.json")
    manifest = load_manifest(tmp_path / "projects.yaml")
    profiles = find_profiles(tmp_path / "ws")
    auftraege, lines = load_auftraege(tmp_path / "auftraege.jsonl")
    drift = reconcile(
        scan, manifest, profiles, auftraege,
        manifest_path=tmp_path / "projects.yaml", auftraege_lines=lines,
    )
    render_markdown(drift)
    render_json(drift)

    assert _snapshot(tmp_path) == before
