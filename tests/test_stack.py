"""TC-064 — Schichtenkarte des Gesamtstacks (stack.py) — Namensregeln, Herkunft, Marker, Karte (REQ-023)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aethel_projects import stack
from aethel_projects.models import ManifestEntry, Maturity, RepoReport

OWN_REMOTE = "git@github.com:AETHEL-Omega/projekt.git"
FOREIGN_REMOTE = "https://github.com/someone/projekt.git"


def _report(
    name: str,
    *,
    remote: str | None = None,
    category: str | None = None,
    grade: str | None = None,
    worktree: bool = False,
    path: str | None = None,
) -> RepoReport:
    """Ein RepoReport ohne Git — nur die Felder, die die Schichtenkarte liest."""
    return RepoReport(
        name=name,
        path=path if path is not None else f"/nicht/vorhanden/{name}",
        git_common_dir=f"/nicht/vorhanden/{name}/.git",
        is_worktree=worktree,
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
        remote_url=remote,
        intent=None,
        maturity=Maturity(score=70, grade=grade, parts={}) if grade else None,
        manifest_entry=(
            ManifestEntry(name=name, category=category, status="active", last_commit=None, remote=None)
            if category
            else None
        ),
        findings=(),
        pm_view=None,
    )


def _repo_dir(tmp_path: Path, name: str, files: dict[str, str]) -> Path:
    root = tmp_path / name
    root.mkdir(parents=True, exist_ok=True)
    for relative, content in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return root


# --- Katalog -----------------------------------------------------------------


def test_layer_catalog_has_s0_to_s17_and_sx() -> None:
    codes = [code for code, _name in stack.LAYERS]
    assert codes == [f"S{i}" for i in range(18)] + ["SX"]
    assert stack.LAYER_NAMES["S0"] == "Rechenmodell/Silizium-Simulation"
    assert stack.LAYER_NAMES["S5"] == "Komponentenlaufzeit/Agenten"
    assert stack.LAYER_NAMES["S17"] == "Entscheidung/Doku/Wissen-Text"
    assert stack.LAYER_NAMES["SX"] == "unbestimmt"
    assert all(layer in stack.LAYER_NAMES for layer, _kw in stack.NAME_RULES)


# --- Namensregeln ------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "layer"),
    [
        ("aethel-memristor-sim", "S0"),
        ("aethelFirmware", "S1"),
        ("aethel_os", "S2"),
        ("aethelContainer", "S3"),
        ("aethelLanding", "S4"),
        ("aethelScripts", "S5"),
        ("aethel-toolchain", "S6"),
        ("aethel-build", "S7"),
        ("aethel-omega", "S8"),
        ("aethelema", "S9"),
        ("aethel_core", "S10"),
        ("aethelBrowser", "S11"),
        ("aethel-cockpit", "S12"),
        ("aethel-secrets", "S13"),
        ("aethel-telemetry", "S14"),
        ("aethelCodeAnalyzer", "S15"),
        ("aethel-dist", "S16"),
        ("aethel-rfc", "S17"),
    ],
)
def test_name_rules_hit_every_layer(name: str, layer: str) -> None:
    assignment = stack.classify(_report(name))
    assert assignment.layer == layer
    assert assignment.layer_name == stack.LAYER_NAMES[layer]
    assert assignment.confidence == "medium"
    assert "Name" in assignment.evidence


@pytest.mark.parametrize(
    ("name", "layer"),
    [
        ("boot-firmware", "S1"),  # firmware → S1, nicht boot → S2
        ("ledger-data", "S4"),  # ledger → S4 hat Vorrang vor data → S8
        ("dist-release", "S7"),  # release → S7 hat Vorrang vor dist → S16
        ("dist-store", "S11"),  # store → S11 hat Vorrang vor dist → S16
        ("aethel-wissen", "S8"),
        ("aethel-wissen-text", "S17"),  # Mehrwort-Regel schlägt „wissen“
        ("aethelAgentRuntime", "S5"),  # Komponentenlaufzeit statt Systemdienst
        ("aethel-runtime", "S4"),
    ],
)
def test_name_rule_precedence(name: str, layer: str) -> None:
    assert stack.classify(_report(name)).layer == layer


@pytest.mark.parametrize(
    "name",
    ["schema-tools", "kubernetes-x", "guide-x", "social-x", "latest-x", "scorecard", "mlx-clean"],
)
def test_short_keywords_match_whole_words_only(name: str) -> None:
    """„ema“, „net“, „ui“, „ci“, „test“, „core“ dürfen nicht mitten im Wort treffen."""
    assignment = stack.classify(_report(name))
    assert assignment.layer == "SX"
    assert assignment.confidence == "low"


@pytest.mark.parametrize(
    ("name", "layer"),
    [
        ("aethelbot-v0-m5", "S5"),  # Markenpräfix verschmolzen: aethel+bot
        ("aethelema-pakete", "S9"),
        ("osxQ", "S0"),  # CamelCase, verschmolzen osxq
        ("aethel-apps", "S11"),  # Beugung
        ("aethel-tests", "S15"),
        ("aix-merge-gated", "S4"),  # gate + d
    ],
)
def test_name_tokens_handle_fusion_and_inflection(name: str, layer: str) -> None:
    assert stack.classify(_report(name)).layer == layer


# --- Review-Befunde: Marken, Wortgrenzen, Vorrang von Oberfläche/Anwendung -------


@pytest.mark.parametrize(
    ("name", "layer"),
    [
        # aix/omega sind führende Marken, keine Schlüsselwörter
        ("_aix_wissen", "S8"),
        ("aix-wissen", "S8"),
        ("AIX-dist", "S16"),
        ("omega_ui", "S12"),
        ("omega_bridge", "S9"),
        ("omega_domain", "S8"),  # Heimatschicht der Marke omega (Wissens-Rückgrat)
        ("aethel-omega", "S8"),
        ("aethelOmegaLM", "S8"),
        ("aethel-omega-ui", "S12"),  # ganze führende Markenkette wird abgetrennt
        ("foo-omega", "S8"),  # nicht führend: Schlüsselwort „omega“
        # lange Schlüsselwörter nur als ganzes Wort
        ("transcripts", "SX"),
        ("gewissen", "SX"),
        ("aethelLandingPage", "S11"),  # Webseite, nicht der Landeweg
        ("aethelLanding", "S4"),
        # manifest ist Projektregister/Zustand, nicht Build
        ("workspace-manifest", "S4"),
        # Anwendung vor Rechenmodell, Oberfläche vor Anwendung
        ("photon_radio", "S11"),
        ("aethelTerminal_cockpit", "S12"),
        ("aethelappstore", "S11"),
        # Inhalt/App
        ("heritageBibel", "S11"),
        ("heritage_bible", "S11"),
        ("aethelNuru", "S11"),
        ("aethel-reader", "S11"),
        ("aethelPlayer", "S11"),
    ],
)
def test_review_regression_names(name: str, layer: str) -> None:
    assignment = stack.classify(_report(name))
    assert assignment.layer == layer, assignment.evidence
    assert (assignment.confidence == "low") == (layer == "SX")


def test_aix_is_a_brand_not_a_keyword() -> None:
    keywords = {kw for _layer, kws in stack.NAME_RULES for kw in kws}
    assert "aix" not in keywords
    assert stack.classify(_report("aix-etwas")).layer == "SX"  # keine Schicht allein aus der Marke
    assert stack.classify(_report("aixd")).layer == "S4"  # aixd bleibt eigenes Schlüsselwort


def test_brand_home_layer_only_applies_without_other_keyword() -> None:
    home = stack.classify(_report("aethel-omega"))
    assert home.layer == "S8"
    assert "Marke „omega“" in home.evidence
    assert stack.classify(_report("omega_ui")).layer == "S12"
    assert "Name „ui“" in stack.classify(_report("omega_ui")).evidence


def test_long_keywords_need_word_boundaries() -> None:
    for name in ("transcripts", "gewissen", "aethelrunningtimes", "xcontainerx", "memorylane2"):
        assert stack.classify(_report(name)).layer == "SX", name
    # als eigenes Wort (CamelCase, Trennzeichen, Beugung) treffen sie weiterhin
    for name, layer in (("aethelScripts", "S5"), ("my_scripts", "S5"), ("aethel-containers", "S3"),
                        ("Wissen-Atlas", "S8")):
        assert stack.classify(_report(name)).layer == layer, name


# --- Herkunft ----------------------------------------------------------------


def test_origin_foreign_by_category() -> None:
    for category in ("fork", "forks", "fremd", "vendor", "Vendor"):
        assignment = stack.classify(_report("aethel-x", remote=OWN_REMOTE, category=category))
        assert assignment.origin == "fremd", category
        assert "Kategorie" in assignment.evidence


def test_origin_foreign_by_remote_without_own_prefix() -> None:
    assert stack.classify(_report("litellm-router", remote=FOREIGN_REMOTE)).origin == "fremd"


def test_origin_own_by_remote_owner() -> None:
    assert stack.classify(_report("litellm-router", remote=OWN_REMOTE)).origin == "eigen"
    manuel = "https://github.com/ManuelWilde/litellm-router.git"
    assert stack.classify(_report("litellm-router", remote=manuel)).origin == "eigen"


def test_origin_own_by_name_prefix_despite_foreign_remote() -> None:
    for name in ("aethelFoo", "AIX-bar", "Omega-baz", "DIN-spec"):
        assert stack.classify(_report(name, remote=FOREIGN_REMOTE)).origin == "eigen", name


def test_origin_remote_owner_must_be_a_path_segment() -> None:
    """`xManuelWilde/…` ist ein anderes Konto, nicht ManuelWilde."""
    remote = "https://github.com/xManuelWilde/repo.git"
    assert stack.classify(_report("litellm-router", remote=remote)).origin == "fremd"


def test_origin_unclear_without_remote_and_name_hint() -> None:
    assert stack.classify(_report("litellm-router")).origin == "unklar"
    assert stack.classify(_report("aethelFoo")).origin == "eigen"  # Namensindiz genügt


# --- Marker ------------------------------------------------------------------


def test_marker_no_std_means_s2(tmp_path: Path) -> None:
    root = _repo_dir(tmp_path, "baremetal", {"src/lib.rs": "#![no_std]\npub fn f() {}\n"})
    assignment = stack.classify(_report("baremetal"), root)
    assert assignment.layer == "S2"
    assert assignment.confidence == "medium"
    assert "no_std" in assignment.evidence


def test_marker_verilog_means_s0(tmp_path: Path) -> None:
    for filename in ("rtl/alu.v", "rtl/alu.sv"):
        root = _repo_dir(tmp_path / filename.replace("/", "_"), "chipx", {filename: "module alu; endmodule\n"})
        assignment = stack.classify(_report("chipx"), root)
        assert assignment.layer == "S0", filename
        assert "Verilog" in assignment.evidence


@pytest.mark.parametrize("marker", ["capability.json", "SKILL.md"])
def test_marker_capability_or_skill_means_s5(tmp_path: Path, marker: str) -> None:
    root = _repo_dir(tmp_path, "baustein", {marker: "{}\n"})
    assert stack.classify(_report("baustein"), root).layer == "S5"


def test_marker_swift_package_with_xpc_means_s4(tmp_path: Path) -> None:
    root = _repo_dir(tmp_path, "dienst", {"Package.swift": "// import XPC\nlet x = 1\n"})
    assert stack.classify(_report("dienst"), root).layer == "S4"
    other = _repo_dir(tmp_path, "plain", {"Package.swift": "let x = 1\n"})
    assert stack.classify(_report("plain"), other).layer == "SX"


def test_marker_pubspec_without_rust_crate_means_s11(tmp_path: Path) -> None:
    flutter = _repo_dir(tmp_path, "flutterx", {"pubspec.yaml": "name: x\n"})
    assert stack.classify(_report("flutterx"), flutter).layer == "S11"
    mixed = _repo_dir(tmp_path, "gemischt", {"pubspec.yaml": "name: x\n", "rust/Cargo.toml": "[package]\n"})
    assert stack.classify(_report("gemischt"), mixed).layer == "SX"


def test_marker_workspace_cargo_dockerfile_flake(tmp_path: Path) -> None:
    ws = _repo_dir(tmp_path, "mono", {"Cargo.toml": "[workspace]\nmembers = []\n"})
    assert stack.classify(_report("mono"), ws).layer == "S10"
    single = _repo_dir(tmp_path, "single", {"Cargo.toml": "[package]\nname = \"x\"\n"})
    assert stack.classify(_report("single"), single).layer == "SX"
    docker = _repo_dir(tmp_path, "imagex", {"Dockerfile": "FROM scratch\n"})
    assert stack.classify(_report("imagex"), docker).layer == "S7"
    nix = _repo_dir(tmp_path, "nixx", {"flake.nix": "{}\n"})
    assert stack.classify(_report("nixx"), nix).layer == "S7"


def test_marker_scan_ignores_hidden_build_dirs_and_depth(tmp_path: Path) -> None:
    root = _repo_dir(
        tmp_path,
        "versteckt",
        {
            ".hidden/a.v": "x",
            "node_modules/b.v": "x",
            "target/c.v": "x",
            "build/d.v": "x",
            "a/b/c/e.v": "x",  # drei Ebenen tief
        },
    )
    assert stack.classify(_report("versteckt"), root).layer == "SX"
    near = _repo_dir(tmp_path, "nah", {"a/b/f.v": "x"})  # zwei Ebenen: gilt
    assert stack.classify(_report("nah"), near).layer == "S0"


def test_marker_ignored_without_repo_path_or_missing_dir(tmp_path: Path) -> None:
    assert stack.classify(_report("baremetal")).layer == "SX"
    assert stack.classify(_report("baremetal"), tmp_path / "gibt-es-nicht").layer == "SX"


# --- Konfidenz ---------------------------------------------------------------


def test_confidence_high_medium_low(tmp_path: Path) -> None:
    # Name und Marker zeigen auf dieselbe Schicht → high.
    agreeing = _repo_dir(tmp_path, "aethelRuntime", {"Package.swift": "import ServiceManagement\n"})
    high = stack.classify(_report("aethelRuntime"), agreeing)
    assert high.layer == "S4"
    assert high.confidence == "high"
    assert "bestätigt" in high.evidence

    # Nur der Name → medium.
    assert stack.classify(_report("aethelRuntime")).confidence == "medium"

    # Marker widerspricht dem Namen: der Name gewinnt, die Abweichung steht im Beleg → medium.
    divergent = _repo_dir(tmp_path, "aethelContainer", {"Package.swift": "import ServiceManagement\n"})
    medium = stack.classify(_report("aethelContainer"), divergent)
    assert medium.layer == "S3"
    assert medium.confidence == "medium"
    assert "abweichender Marker S4" in medium.evidence

    # Nur ein Marker → medium; nichts → SX, low.
    marker_only = _repo_dir(tmp_path, "baustein", {"capability.json": "{}\n"})
    assert stack.classify(_report("baustein"), marker_only).confidence == "medium"
    nothing = stack.classify(_report("unbekannt"))
    assert (nothing.layer, nothing.confidence) == ("SX", "low")


# --- Reife -------------------------------------------------------------------


def test_maturity_grade_from_report_or_unbekannt() -> None:
    assert stack.classify(_report("aethelBot", grade="Solide")).maturity_grade == "Solide"
    assert stack.classify(_report("aethelBot")).maturity_grade == "unbekannt"


# --- Karte -------------------------------------------------------------------


def test_build_skips_worktrees() -> None:
    result = stack.build((_report("aethelBot"), _report("aethelBot-wt", worktree=True)))
    assert [a.repo for a in result.assignments] == ["aethelBot"]
    assert sum(result.per_layer.values()) == 1


def test_build_per_layer_and_empty_layers() -> None:
    repos = (
        _report("aethelBot", remote=OWN_REMOTE),  # S5 eigen
        _report("aethelScripts", remote=OWN_REMOTE),  # S5 eigen
        _report("litellm-router", remote=FOREIGN_REMOTE),  # SX fremd
        _report("vendor-browser", remote=FOREIGN_REMOTE),  # S11 nur fremd
    )
    result = stack.build(repos)
    assert result.per_layer["S5"] == 2
    assert result.per_layer["S11"] == 1
    assert result.per_layer["SX"] == 1
    assert result.per_layer["S0"] == 0
    assert set(result.per_layer) == {code for code, _name in stack.LAYERS}
    # S5 hat eigene Repos; S11 nur ein fremdes → leer; SX ist keine Stack-Schicht.
    assert "S5" not in result.empty_layers
    assert "S11" in result.empty_layers
    assert "SX" not in result.empty_layers
    assert result.empty_layers == tuple(f"S{i}" for i in range(18) if i != 5)


def test_build_sorts_assignments_by_layer_then_name() -> None:
    result = stack.build((_report("zeta-bot"), _report("aethelLanding"), _report("alpha-bot"), _report("nix")))
    assert [(a.layer, a.repo) for a in result.assignments] == [
        ("S4", "aethelLanding"),
        ("S5", "alpha-bot"),
        ("S5", "zeta-bot"),
        ("SX", "nix"),
    ]


def test_build_with_root_reads_markers_from_relative_path(tmp_path: Path) -> None:
    _repo_dir(tmp_path, "chip", {"alu.v": "module alu; endmodule\n"})
    result = stack.build((_report("chip", path="chip"), _report("fehlt", path="fehlt")), root=tmp_path)
    layers = {a.repo: a.layer for a in result.assignments}
    assert layers == {"chip": "S0", "fehlt": "SX"}
    # Ohne root werden Marker nicht gelesen.
    assert stack.build((_report("chip", path=str(tmp_path / "chip")),)).assignments[0].layer == "SX"


def test_as_dict_is_serialisable() -> None:
    assignment = stack.classify(_report("aethelBot", remote=OWN_REMOTE, grade="Solide"))
    assert assignment.as_dict() == {
        "repo": "aethelBot",
        "layer": "S5",
        "layer_name": "Komponentenlaufzeit/Agenten",
        "origin": "eigen",
        "maturity_grade": "Solide",
        "evidence": assignment.evidence,
        "confidence": "medium",
    }
    json.dumps(stack.build((_report("aethelBot"),)).as_dict())


# --- Ausgabe -----------------------------------------------------------------


def _sample_map() -> stack.StackMap:
    return stack.build(
        (
            _report("aethelBot", remote=OWN_REMOTE, grade="Solide"),
            _report("aethelContainer", remote=OWN_REMOTE, grade="Professional"),
            _report("vendor-browser", remote=FOREIGN_REMOTE),
            _report("mlx|clean"),
        )
    )


def test_render_markdown_has_layers_empty_list_and_detail() -> None:
    text = stack.render_markdown(_sample_map())
    assert text.startswith("# Schichtenkarte")
    for name in ("Isolation/Hypervisor", "Komponentenlaufzeit/Agenten", "Firmware", "unbestimmt"):
        assert name in text
    assert "Leer: diese Schichten haben kein eigenes Repo" in text
    assert "- S1 Firmware" in text
    assert "- S3 Isolation/Hypervisor" not in text  # S3 hat ein eigenes Repo
    assert "- S11 Anwendung" in text  # nur fremdes Repo → leer
    assert "| Repo | Schicht | Herkunft | Reife | Konfidenz | Beleg |" in text
    assert "mlx\\|clean" in text  # Pipe im Namen ist maskiert


def test_render_markdown_detail_sorted_by_layer_then_name() -> None:
    text = stack.render_markdown(_sample_map())
    detail = text.split("## Detail", 1)[1]
    order = [detail.index(f"| {name} |") for name in ("aethelContainer", "aethelBot", "vendor-browser", "mlx\\|clean")]
    assert order == sorted(order)


def test_render_markdown_examples_limited_to_five() -> None:
    repos = tuple(_report(f"bot-{i}", remote=OWN_REMOTE) for i in range(7))
    text = stack.render_markdown(stack.build(repos))
    row = next(line for line in text.splitlines() if line.startswith("| S5 |"))
    assert "bot-0, bot-1, bot-2, bot-3, bot-4, …" in row
    assert "bot-5" not in row


def test_render_markdown_without_empty_layers_omits_leer_sentence() -> None:
    full = stack.StackMap(assignments=(), per_layer={code: 0 for code, _n in stack.LAYERS}, empty_layers=())
    text = stack.render_markdown(full)
    assert "Leer:" not in text
    assert "Keine Schicht ist leer" in text


def test_render_json_is_valid_and_complete() -> None:
    data = json.loads(stack.render_json(_sample_map()))
    assert data["schema"] == "aethel.projects.stack/v1"
    assert data["layer_names"]["S3"] == "Isolation/Hypervisor"
    assert data["per_layer"]["S5"] == 1
    assert "S1" in data["empty_layers"]
    assert "S3" not in data["empty_layers"]
    assert {a["repo"] for a in data["assignments"]} == {"aethelBot", "aethelContainer", "vendor-browser", "mlx|clean"}
    assert all(set(a) >= {"repo", "layer", "layer_name", "origin", "maturity_grade", "evidence", "confidence"}
               for a in data["assignments"])
