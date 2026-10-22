"""TC-051 bis TC-057 — Forensik: die geschärften Regeln (REQ-013, REQ-021).

Diese Tests decken die Korrekturen ab, die der erste Lauf gegen den echten
Workspace erzwungen hat:

* ``.env.example`` ist **kein** Credential-Verstoß.
* Ein Repo ohne Substanz ist **nicht** „schön“, nur weil es auf main liegt.
* Namen und Seed-Klon-Familien werden erkannt.
"""

from __future__ import annotations

from pathlib import Path

from conftest import add_commit, git, make_repo

from aethel_projects import forensics
from aethel_projects.discovery import discover
from aethel_projects.metrics import collect
from aethel_projects.models import Maturity, RepoReport


def _codes(observations) -> set[str]:
    return {o.code for o in observations}


def _report(tmp_path: Path, name: str, *, maturity: int = 0) -> RepoReport:
    root = tmp_path / name
    root.mkdir(parents=True, exist_ok=True)
    return RepoReport(
        name=name,
        path=str(root),
        git_common_dir=str(root / ".git"),
        is_worktree=False,
        worktree_paths=(),
        default_branch="main",
        current_branch="main",
        commits_total=4,
        commits_on_main=4,
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
        maturity=Maturity(score=maturity, grade="Skizze", parts={}),
        manifest_entry=None,
        findings=(),
        pm_view=None,
    )


def test_tc051_env_example_is_no_credential(tmp_path: Path) -> None:
    """TC-051: eine Beispieldatei ist kein Verstoß."""
    repo = make_repo(tmp_path / "r", commits=1)
    (repo / ".env.example").write_text("API_KEY=\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "Beispiel")

    report = collect(discover(tmp_path)[0])
    observations = forensics.inspect(report)

    assert "moegliche-credentials" not in _codes(observations)
    assert "beispiel-konfiguration" in _codes(observations)


def test_tc052_real_env_is_a_credential(tmp_path: Path) -> None:
    """TC-052: eine echte `.env` ist ein Verstoß."""
    repo = make_repo(tmp_path / "r", commits=1)
    (repo / ".env").write_text("API_KEY=abc\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "Secret")

    report = collect(discover(tmp_path)[0])
    observations = forensics.inspect(report)

    assert "moegliche-credentials" in _codes(observations)


def test_all_env_variants_are_reported_but_examples_are_not(tmp_path: Path) -> None:
    """Alle `.env*`-Varianten werden gemeldet; nur Beispielendungen nicht."""
    repo = make_repo(tmp_path / "r", commits=1)
    for name in (".env.dev", ".env.staging", ".env.test", ".env.development"):
        (repo / name).write_text("K=v\n", encoding="utf-8")
    for name in (".env.example", ".env.sample", ".env.template", ".env.dist"):
        (repo / name).write_text("K=\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "Envs")

    root = Path(repo)
    tracked = {p.name for p in root.iterdir() if p.name.startswith(".env")}
    found = forensics._secret_candidates(root, tracked)

    assert found == [".env.dev", ".env.development", ".env.staging", ".env.test"]


def test_docker_compose_variant_is_no_example(tmp_path: Path) -> None:
    """`docker-compose.<x>.yml` ist keine Beispieldatei und wird nicht gelobt."""
    root = tmp_path / "r"
    root.mkdir()
    assert forensics._example_candidates(root, {"docker-compose.prod.yml"}) == []


def test_tc053_stub_is_not_beautiful(tmp_path: Path) -> None:
    """TC-053: ein Repo ohne Substanz wird nicht als „vollständig auf main“ gelobt."""
    repo = make_repo(tmp_path / "r", commits=2)

    report = collect(discover(tmp_path)[0])
    observations = forensics.inspect(report)

    assert "vollstaendig-auf-main" not in _codes(observations)
    assert "leere-huelle" in _codes(observations)


def test_tc054_substantial_repo_on_main_is_beautiful(tmp_path: Path) -> None:
    """TC-054: mit Substanz darf „vollständig auf main“ gelobt werden."""
    repo = make_repo(tmp_path / "r", commits=25)
    (repo / "README.md").write_text("# Projekt\n\nInhalt\n", encoding="utf-8")

    report = collect(discover(tmp_path)[0])
    observations = forensics.inspect(report)

    assert "vollstaendig-auf-main" in _codes(observations)


def test_tc055_name_collision_is_detected(tmp_path: Path) -> None:
    """TC-055: zwei verschiedene Repos mit gleichem Namen werden erkannt."""
    a = make_repo(tmp_path / "a" / "gleich", commits=1)
    b = make_repo(tmp_path / "b" / "gleich", commits=1)

    reports = tuple(collect(identity) for identity in discover(tmp_path))
    observations = forensics.inspect_workspace(reports)

    assert "namenskollision" in _codes(observations)


def test_tc056_seed_family_is_detected(tmp_path: Path) -> None:
    """TC-056: Repos mit identischer Mini-Struktur werden als Seed-Familie erkannt."""
    reports = []
    for index in range(3):
        root = tmp_path / f"seed{index}"
        root.mkdir(parents=True)
        reports.append(
            RepoReport(
                name=f"seed{index}",
                path=str(root),
                git_common_dir=str(root / ".git"),
                is_worktree=False,
                worktree_paths=(),
                default_branch=None,
                current_branch="chore/x",
                commits_total=4,
                commits_on_main=0,
                commits_not_on_main=4,
                branches_total=2,
                branches_unmerged=2,
                unmerged_branches=(),
                ahead_of_origin=None,
                behind_origin=None,
                dirty_files=0,
                last_commit_date="2026-10-01",
                last_commit_subject="Seed",
                remote_url=None,
                intent=None,
                maturity=Maturity(score=0, grade="Skizze", parts={}),
                manifest_entry=None,
                findings=(),
                pm_view=None,
            )
        )

    observations = forensics.inspect_workspace(tuple(reports))

    assert "seed-familie" in _codes(observations)


def test_tc057_template_family_still_detected(tmp_path: Path) -> None:
    """TC-057: die Template-Familie-Erkennung bleibt erhalten."""
    reports = []
    for index in range(2):
        root = tmp_path / f"tpl{index}"
        (root / "lib").mkdir(parents=True)
        (root / "lib" / "main.dart").write_text("void main() {}\n", encoding="utf-8")
        reports.append(
            RepoReport(
                name=f"tpl{index}",
                path=str(root),
                git_common_dir=str(root / ".git"),
                is_worktree=False,
                worktree_paths=(),
                default_branch="main",
                current_branch="main",
                commits_total=5,
                commits_on_main=5,
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
                maturity=Maturity(score=20, grade="Skizze", parts={}),
                manifest_entry=None,
                findings=(),
                pm_view=None,
            )
        )

    observations = forensics.inspect_workspace(tuple(reports))

    assert "template-familie" in _codes(observations)


def test_stub_detection_uses_maturity(tmp_path: Path) -> None:
    """Ein Repo mit Reifegrad 40 gilt als substanziell."""
    report = _report(tmp_path, "ok", maturity=40)

    assert forensics._has_substance(report)
    assert not forensics._has_substance(_report(tmp_path, "schwach", maturity=10))


def test_credentials_only_check_tracked_files(tmp_path: Path) -> None:
    """Nicht verfolgte Dateien werden nicht als Fund gemeldet."""
    repo = make_repo(tmp_path / "r", commits=1)
    (repo / ".env").write_text("API_KEY=abc\n", encoding="utf-8")

    report = collect(discover(tmp_path)[0])
    observations = forensics.inspect(report)

    assert "moegliche-credentials" not in _codes(observations)
