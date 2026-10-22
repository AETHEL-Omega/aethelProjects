"""TC-033 bis TC-038 — Fabrik- und Firmensicht (REQ-017, REQ-018)."""

from __future__ import annotations

from pathlib import Path

from conftest import make_repo

from aethel_projects import factory
from aethel_projects.models import Maturity, RepoReport


def _report(
    tmp_path: Path,
    name: str,
    *,
    files: dict[str, str] | None = None,
    maturity: int = 0,
) -> RepoReport:
    """Ein RepoReport mit frei definierbarem Inhalt — ohne Git nötig."""
    root = tmp_path / name
    root.mkdir(parents=True, exist_ok=True)
    for relative, content in (files or {}).items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return RepoReport(
        name=name,
        path=str(root),
        git_common_dir=str(root / ".git"),
        is_worktree=False,
        worktree_paths=(),
        default_branch="main",
        current_branch="main",
        commits_total=10,
        commits_on_main=10,
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
        maturity=Maturity(score=maturity, grade="Solide", parts={}),
        manifest_entry=None,
        findings=(),
        pm_view=None,
    )


def test_tc033_stage_without_evidence_is_leer(tmp_path: Path) -> None:
    """TC-033: eine Stufe ohne Beleg ist leer, nicht teilweise."""
    repo = _report(tmp_path, "leerprojekt", files={"main.py": "print('x')\n"})

    view = factory.build((repo,))
    stufen = {s.key: s for s in view.stages}

    assert stufen["freigabe"].level == "leer"
    assert stufen["freigabe"].covered_by == ()
    assert stufen["freigabe"].carriers == ()


def test_tc034_carrier_must_fulfil_all_requirements(tmp_path: Path) -> None:
    """TC-034: nur ein Repo mit *allen* Anforderungen ist Träger."""
    teil = _report(tmp_path, "teil", files={"docs/SPEC.md": "# SPEC\n"})
    voll = _report(
        tmp_path,
        "voll",
        files={
            "docs/SPEC.md": "# SPEC\n",
            "docs/DESIGN.md": "# DESIGN\n",
            "docs/ARCHITECTURE.md": "# Architektur\n",
        },
    )

    view = factory.build((teil, voll))
    stufen = {s.key: s for s in view.stages}

    assert stufen["entwurf"].carriers == ("voll",)
    assert "teil" in stufen["entwurf"].covered_by
    assert "teil" not in stufen["entwurf"].carriers
    assert stufen["entwurf"].level == "voll"


def test_tc035_readiness_reflects_carriers(tmp_path: Path) -> None:
    """TC-035: eine leere Fabrik hat Reifegrad 0, eine volle mehr."""
    leer = _report(tmp_path, "a", files={"main.py": "x\n"})
    view_leer = factory.build((leer,))
    assert view_leer.readiness < 30

    voll = _report(
        tmp_path,
        "b",
        files={
            "README.md": "# Projekt\n\nZweck\n",
            "docs/SPEC.md": "# SPEC\n",
            "docs/DESIGN.md": "# DESIGN\n",
            "docs/ARCHITECTURE.md": "# A\n",
            ".github/workflows/ci.yml": "on: push\n",
            ".github/workflows/release.yml": "on: push\n",
            "tests/t.py": "def test(): pass\n",
            ".aix/validation-contract.json": "{}\n",
            "src/main.py": "x\n",
            "pyproject.toml": "[project]\n",
            "CHANGELOG.md": "# Changelog\n",
            "Dockerfile": "FROM alpine\n",
            "scripts/install.sh": "echo hi\n",
            "run.sh": "echo run\n",
            "docs/auswertung.md": "# Auswertung\n",
            "feedback.md": "# Feedback\n",
        },
        maturity=80,
    )
    view_voll = factory.build((voll,))
    assert view_voll.readiness > view_leer.readiness
    assert view_voll.readiness > 50


def test_tc036_gaps_name_stages_without_carrier(tmp_path: Path) -> None:
    """TC-036: Lücken benennen die Stufen ohne Träger."""
    repo = _report(tmp_path, "x", files={"main.py": "x\n"})

    view = factory.build((repo,))

    assert view.gaps
    assert any("Freigabe" in gap for gap in view.gaps)


def test_tc037_roles_are_derived_not_invented(tmp_path: Path) -> None:
    """TC-037: die Rolle folgt aus dem Namen und dem Inhalt."""
    kern = _report(tmp_path, "aethel_core", files={"Cargo.toml": "[package]\n"})
    werkzeug = _report(tmp_path, "aethelScripts", files={"bin/x": "x\n"})
    wissen = _report(tmp_path, "aethel_memory", files={"dna/genome.yaml": "schema: x\n"})

    view = factory.build((kern, werkzeug, wissen))

    assert "aethel_core" in view.roles.get("kern", ())
    assert "aethelScripts" in view.roles.get("werkzeug", ())
    assert "aethel_memory" in view.roles.get("wissen", ())


def test_tc038_engine_and_output_are_separated(tmp_path: Path) -> None:
    """TC-038: Fabrik-Motor und Fabrik-Output sind getrennte Mengen."""
    werkzeug = _report(tmp_path, "aethelScripts", files={"bin/x": "x\n"})
    produkt = _report(tmp_path, "aethel_app", files={"pubspec.yaml": "name: x\n"}, maturity=70)

    view = factory.build((werkzeug, produkt))

    assert "aethelScripts" in view.engine
    assert "aethel_app" in view.output
    assert not set(view.engine) & set(view.output)


def test_factory_reports_no_product_as_gap(tmp_path: Path) -> None:
    """Ohne Produkt ist die Lücke explizit benannt."""
    nur_werkzeug = _report(tmp_path, "aethelScripts", files={"bin/x": "x\n"})

    view = factory.build((nur_werkzeug,))

    assert any("Fabrik-Output" in gap for gap in view.gaps)


def test_factory_stage_evidence_names_the_file(tmp_path: Path) -> None:
    """Jede Stufe nennt den Beleg, aus dem sie folgt."""
    repo = _report(tmp_path, "mit_docker", files={"Dockerfile": "FROM alpine\n"})

    view = factory.build((repo,))
    stufen = {s.key: s for s in view.stages}

    assert "mit_docker" in stufen["auslieferung"].covered_by
    assert "Dockerfile" in stufen["auslieferung"].evidence["mit_docker"]


def test_chain_integrity_is_zero_without_carriers(tmp_path: Path) -> None:
    """Ohne Träger gibt es keine Kette — die Kettenintegrität ist 0."""
    repo = _report(tmp_path, "a", files={"main.py": "x\n"})

    view = factory.build((repo,))

    assert view.kettenintegritaet == 0
    assert view.end_to_end == ()
    assert any("fragmentiert" in note for note in view.notes)


def test_end_to_end_repo_is_recognized(tmp_path: Path) -> None:
    """Ein Repo, das die ganze Kette trägt, wird als End-to-End-Kette erkannt."""
    alle = {
        "README.md": "# Projekt\n\nZweck\n",
        "docs/SPEC.md": "# SPEC\n",
        "docs/DESIGN.md": "# DESIGN\n",
        "docs/ARCHITECTURE.md": "# A\n",
        ".github/workflows/ci.yml": "on: push\n",
        ".github/workflows/release.yml": "on: push\n",
        "tests/t.py": "def test(): pass\n",
        ".aix/validation-contract.json": "{}\n",
        "src/main.py": "x\n",
        "pyproject.toml": "[project]\n",
        "CHANGELOG.md": "# Changelog\n",
        "Dockerfile": "FROM alpine\n",
        "scripts/install.sh": "echo hi\n",
        "run.sh": "echo run\n",
        "docs/auswertung.md": "# Auswertung\n",
        "feedback.md": "# Feedback\n",
    }
    repo = _report(tmp_path, "kette", files=alle, maturity=90)

    view = factory.build((repo,))

    assert view.kettenintegritaet > 80
    assert "kette" in view.end_to_end


def test_factory_works_on_real_git_repo(tmp_path: Path) -> None:
    """Die Fabriksicht laeuft auch auf einem echten Mini-Repo."""
    repo_path = make_repo(tmp_path / "echt", commits=2)
    (repo_path / "README.md").write_text("# Echt\n\nZweck: testen\n", encoding="utf-8")
    (repo_path / "src").mkdir()
    (repo_path / "src" / "main.py").write_text("print('x')\n", encoding="utf-8")

    from aethel_projects.discovery import discover
    from aethel_projects.metrics import collect
    from aethel_projects.scanner import _derive

    identity = discover(repo_path.parent)[0]
    report = _derive(collect(identity), {})

    view = factory.build((report,))

    assert view.stages
    assert view.readiness >= 0
