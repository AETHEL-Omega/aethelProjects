"""TC-066 — Apple-first-Audit (applefirst.py) — Sprachen, Frameworks, Unified Memory, Anti-Muster, Score (REQ-025)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import make_repo

from aethel_projects import applefirst
from aethel_projects.discovery import discover
from aethel_projects.metrics import collect
from aethel_projects.models import RepoReport


def _report(name: str, path: str, *, worktree: bool = False) -> RepoReport:
    """Ein RepoReport ohne Git — nur die Felder, die der Audit liest."""
    return RepoReport(
        name=name,
        path=path,
        git_common_dir=f"{path}/.git",
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
        remote_url=None,
        intent=None,
        maturity=None,
        manifest_entry=None,
        findings=(),
        pm_view=None,
    )


def _lines(count: int, text: str = "x") -> str:
    return "\n".join(f"{text}{i}" for i in range(count)) + "\n" if count else ""


def _repo(tmp_path: Path, name: str, files: dict[str, str], *, git: bool = True) -> Path:
    """Ein echtes Git-Repo (make_repo) mit zusätzlichen, nicht committeten Dateien."""
    root = make_repo(tmp_path / name) if git else tmp_path / name
    root.mkdir(parents=True, exist_ok=True)
    for relative, content in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return root


def _audit(
    tmp_path: Path, name: str, files: dict[str, str], *, git: bool = True
) -> applefirst.AppleFirst:
    root = _repo(tmp_path, name, files, git=git)
    return applefirst.audit(_report(name, str(root)), root)


def _codes(item: applefirst.AppleFirst) -> set[str]:
    return {f.code for f in item.findings}


SWIFT_APPLE_FIRST = {
    "Package.swift": "// swift-tools-version: 6.0\nimport PackageDescription\n",
    "Sources/Kern/Gpu.swift": (
        "import Metal\n"
        "import MLX\n"
        "final class Gpu {\n"
        "    // Unified Memory: Puffer teilen sich CPU und GPU\n"
        "    let device = MTLCreateSystemDefaultDevice()\n"
        "    func puffer() -> MTLBuffer? { device?.makeBuffer(length: 4096, options: .storageModeShared) }\n"
        "}\n"
    ),
    "Sources/Kern/Dienst.swift": (
        "import Foundation\n"
        "final class Dienst: NSObject, NSXPCListenerDelegate {\n"
        "    let listener = NSXPCListener.anonymous()\n"
        "}\n"
    ),
}

PYTHON_FREMD = {
    "Dockerfile": "FROM python:3.12\nCOPY . /app\n",
    "app/train.py": "import torch\nimport subprocess\n\nmodel = torch.nn.Linear(2, 2)\nsubprocess.run(['ls'])\n",
    **{f"scripts/s{i}.py": "import subprocess\n\nsubprocess.run(['echo', 'x'])\n" for i in range(20)},
}


# --- Gesamtbild --------------------------------------------------------------


def test_swift_repo_with_metal_mlx_xpc_unified_memory_is_apple_first(tmp_path: Path) -> None:
    item = _audit(tmp_path, "aethelKern", SWIFT_APPLE_FIRST)

    assert item.score is not None and item.score >= 80
    assert item.grade == "Apple-first"
    assert {"Metal", "MLX", "XPC"} <= set(item.frameworks)
    assert item.unified_memory_hits >= 1
    assert item.python_anteil == 0.0
    assert item.silizium_genutzt is True
    assert all(count == 0 for count in item.anti_muster.values())
    assert item.findings == ()


def test_python_repo_with_docker_torch_subprocess_is_fremdgefuehrt(tmp_path: Path) -> None:
    item = _audit(tmp_path, "aethelPy", PYTHON_FREMD)

    assert item.score is not None and item.score < 20
    assert item.grade == "fremdgeführt"
    assert item.python_anteil == 1.0
    assert item.anti_muster["docker_lokal"] == 1
    assert item.anti_muster["ml_cpu"] == 1
    assert item.anti_muster["subprocess_lastig"] == 21
    assert {
        "applefirst-python-schwer",
        "applefirst-docker-lokal",
        "applefirst-ml-cpu",
    } <= _codes(item)
    python_finding = next(f for f in item.findings if f.code == "applefirst-python-schwer")
    assert python_finding.severity == "warn"
    assert python_finding.message.startswith("Python-Anteil 100 %")
    assert "Python dünn" in python_finding.message


def test_findings_are_warn_or_info_with_repo_and_action(tmp_path: Path) -> None:
    item = _audit(tmp_path, "aethelPy", PYTHON_FREMD)

    assert item.findings
    for finding in item.findings:
        assert finding.code.startswith("applefirst-")
        assert finding.severity in {"warn", "info"}
        assert finding.repo == "aethelPy"
        assert finding.message and finding.action
    severities = [f.severity for f in item.findings]
    assert severities == sorted(severities, key=lambda s: 0 if s == "warn" else 1)


def test_sandbox_exec_is_a_warn_finding(tmp_path: Path) -> None:
    item = _audit(
        tmp_path,
        "aethelSandbox",
        {"bin/run.sh": "#!/bin/sh\nsandbox-exec -f profil.sb ./agent\n"},
    )

    assert item.anti_muster["sandbox_exec"] == 1
    finding = next(f for f in item.findings if f.code == "applefirst-sandbox-exec")
    assert finding.severity == "warn"
    assert "Containerization statt sandbox-exec" in finding.message
    # Basis 50, sandbox-exec -10
    assert item.score == 40


def test_repo_without_code_has_no_score(tmp_path: Path) -> None:
    item = _audit(tmp_path, "aethelDoku", {"README.md": "# Nur Doku\n\nApple Silicon.\n"})

    assert item.score is None
    assert item.grade == "ohne Code"
    assert item.findings == ()
    assert item.python_anteil == 0.0
    assert item.loc == 0
    # Doku-Hinweise werden trotzdem gezählt.
    assert item.unified_memory_hits == 1


def test_missing_directory_counts_as_repo_without_code(tmp_path: Path) -> None:
    item = applefirst.audit(_report("weg", str(tmp_path / "weg")), tmp_path / "weg")

    assert item.score is None
    assert item.grade == "ohne Code"


# --- Sprachen ----------------------------------------------------------------


def test_language_shares_are_counted(tmp_path: Path) -> None:
    item = _audit(
        tmp_path,
        "aethelMix",
        {
            "Sources/A/A.swift": _lines(30),
            "src/lib.rs": _lines(10),
            "tools/a.py": _lines(40),
            "tools/b.py": _lines(20),
            "run.sh": _lines(5),
            "lib/main.dart": _lines(15),
            "web/app.ts": _lines(8),
            "native/x.m": _lines(2),
            "kernel.metal": _lines(3),
            "README.md": _lines(500),
            "Cargo.toml": _lines(50),
        },
    )

    assert item.sprachen["swift"] == {"files": 1, "loc": 30}
    assert item.sprachen["rust"] == {"files": 1, "loc": 10}
    assert item.sprachen["python"] == {"files": 2, "loc": 60}
    assert item.sprachen["shell"] == {"files": 1, "loc": 5}
    assert item.sprachen["dart"] == {"files": 1, "loc": 15}
    assert item.sprachen["typescript"] == {"files": 1, "loc": 8}
    assert item.sprachen["c_objc"] == {"files": 1, "loc": 2}
    assert item.sprachen["metal"] == {"files": 1, "loc": 3}
    assert set(item.sprachen) == set(applefirst.LANGUAGES)
    # Markdown und TOML sind keine Quellsprachen.
    assert item.loc == 133
    assert item.python_anteil == round(60 / 133, 4)
    assert item.anteil("swift") == round(30 / 133, 4)


@pytest.mark.parametrize(
    ("python_loc", "c_loc", "score", "grade", "python_schwer"),
    [
        (59, 41, 50, "vernachlässigt", False),
        (60, 40, 40, "vernachlässigt", True),
        (79, 21, 40, "vernachlässigt", True),
        (80, 20, 30, "fremdgeführt", True),
    ],
)
def test_python_share_penalty_thresholds(
    tmp_path: Path, python_loc: int, c_loc: int, score: int, grade: str, python_schwer: bool
) -> None:
    item = _audit(
        tmp_path,
        "aethelGrenze",
        {"tools/a.py": _lines(python_loc), "native/a.c": _lines(c_loc)},
    )

    assert item.score == score
    assert item.grade == grade
    assert ("applefirst-python-schwer" in _codes(item)) is python_schwer


def test_core_language_bonus_for_swift_or_rust(tmp_path: Path) -> None:
    swift = _audit(tmp_path, "s", {"Sources/A/A.swift": _lines(10)})
    rust = _audit(tmp_path, "r", {"src/lib.rs": _lines(10)})
    dart = _audit(tmp_path, "d", {"lib/main.dart": _lines(10)})

    assert swift.score == 60  # 50 + Kern-Bonus
    assert rust.score == 60
    assert dart.score == 50  # Flutter ist Client: weder Bonus noch Abzug


# --- Frameworks --------------------------------------------------------------


@pytest.mark.parametrize(
    ("filename", "content", "framework"),
    [
        ("a.swift", "import Metal\n", "Metal"),
        ("a.metal", "kernel void f() {}\n", "Metal"),
        ("a.rs", "use objc2_metal::MTLDevice;\n", "Metal"),
        ("a.swift", "import MLX\n", "MLX"),
        ("a.py", "import mlx.core as mx\n", "MLX"),
        ("a.py", "from mlx_lm import load\n", "MLX"),
        ("Cargo.toml", 'mlx-rs = "0.21"\n', "MLX"),
        ("pyproject.toml", 'dependencies = ["mlx>=0.20"]\n', "MLX"),
        ("a.swift", "import CoreML\n", "CoreML"),
        ("a.py", "import coremltools as ct\n", "CoreML"),
        ("a.swift", "import FoundationModels\n", "FoundationModels"),
        ("a.swift", "let s = LanguageModelSession()\n", "FoundationModels"),
        ("a.py", 'cmd = ["/usr/bin/fm", "respond"]\n', "FoundationModels"),
        ("a.sh", 'fm respond "hallo"\n', "FoundationModels"),
        ("a.swift", "import Accelerate\n", "Accelerate"),
        ("a.swift", "vDSP_vadd(a, 1, b, 1, &c, 1, 4)\n", "Accelerate"),
        ("a.swift", "import CoreAI\n", "CoreAI"),
        ("a.swift", "import Vision\n", "Vision"),
        ("a.swift", 'let c = NSXPCConnection(serviceName: "x")\n', "XPC"),
        ("a.swift", "try SMAppService.mainApp.register()\n", "XPC"),
        ("a.swift", "struct Oeffnen: AppIntent {}\n", "AppIntents"),
        ("a.swift", "import OSLog\n", "OSLog"),
        ("a.swift", "import Virtualization\n", "Virtualization"),
        ("a.swift", "import Containerization\n", "Virtualization"),
        ("a.swift", "SecItemAdd(query, nil)\n", "Keychain"),
        ("a.swift", "import LocalAuthentication\n", "Keychain"),
        ("a.swift", "let l = try NWListener(using: .tcp)\n", "Network"),
        ("a.swift", "async let a = laden()\n", "SwiftConcurrency"),
        ("a.swift", "actor Zaehler {}\n", "SwiftConcurrency"),
        ("a.swift", "try await withTaskGroup(of: Int.self) { _ in }\n", "SwiftConcurrency"),
        ("a.swift", "import SwiftData\n", "SwiftData"),
        ("a.swift", "import Testing\n", "SwiftTesting"),
        ("a.swift", "@Test func prueft() {}\n", "SwiftTesting"),
    ],
)
def test_framework_signals(tmp_path: Path, filename: str, content: str, framework: str) -> None:
    item = _audit(
        tmp_path,
        "aethelFw",
        {f"Sources/{filename}": content, "Sources/Rest.swift": "import Foundation\n"},
        git=False,
    )

    assert item.frameworks.get(framework, 0) >= 1, item.frameworks


def test_frameworks_are_not_counted_in_docs_or_in_foreign_languages(tmp_path: Path) -> None:
    item = _audit(
        tmp_path,
        "aethelDoku",
        {
            "README.md": "import Metal\nimport MLX\nLanguageModelSession\n",
            "tools/a.py": "actor Foo\nasync let x\n@Test\n",
            "tools/b.py": "x = 1\n",
        },
    )

    assert item.frameworks == {}


def test_framework_hits_are_counted_and_sorted(tmp_path: Path) -> None:
    item = _audit(
        tmp_path,
        "aethelZaehler",
        {
            "Sources/A.swift": "import MLX\nimport Metal\nimport Metal\n",
            "Sources/B.swift": "import Accelerate\n",
        },
    )

    assert item.frameworks == {"Accelerate": 1, "MLX": 1, "Metal": 2}
    assert list(item.frameworks) == sorted(item.frameworks)


def test_three_distinct_frameworks_earn_a_bonus_without_silicon(tmp_path: Path) -> None:
    item = _audit(
        tmp_path,
        "aethelPlattform",
        {
            "Sources/A.swift": "import Accelerate\nimport Network\nlet k = SecItemAdd(q, nil)\n",
        },
    )

    assert set(item.frameworks) == {"Accelerate", "Network", "Keychain"}
    assert item.silizium_genutzt is False
    # 50 + Swift 10 + >=3 Frameworks 10 (kein Silizium-, Unified-, Dienst-Bonus)
    assert item.score == 70
    assert item.grade == "teilweise"


#: Je ein Treffertext pro Signalmuster — hält den Anker-Vorfilter ehrlich.
SIGNAL_SAMPLES: tuple[tuple[str, str], ...] = (
    (".swift", "import Metal\n"),
    (".m", "#import <Metal/Metal.h>\n"),
    (".swift", "let d: MTLDevice\n"),
    (".rs", "use objc2_metal::MTLDevice;\n"),
    (".toml", 'objc2-metal = "0.2"\n'),
    (".py", "import mlx.core as mx\n"),
    (".swift", "import MLX\n"),
    (".rs", "use mlx_rs::Array;\n"),
    (".toml", 'dependencies = ["mlx>=0.20"]\n'),
    (".swift", "import CoreML\n"),
    (".m", "#import <CoreML/CoreML.h>\n"),
    (".py", "import coremltools as ct\n"),
    (".swift", "let m: MLModel\n"),
    (".py", 'ziel = "modell.mlpackage"\n'),
    (".toml", 'objc2-core-ml = "0.2"\n'),
    (".swift", "import FoundationModels\n"),
    (".swift", "let s = LanguageModelSession()\n"),
    (".sh", "/usr/bin/fm respond hallo\n"),
    (".sh", "fm respond hallo\n"),
    (".swift", "import Accelerate\n"),
    (".m", "#import <Accelerate/Accelerate.h>\n"),
    (".swift", "vDSP_vadd(a, 1, b, 1, &c, 1, 4)\n"),
    (".swift", "let n = BNNSFilterCreate()\n"),
    (".toml", 'accelerate-src = "0.3"\n'),
    (".swift", "import CoreAI\n"),
    (".swift", "import Vision\n"),
    (".m", "#import <Vision/Vision.h>\n"),
    (".swift", "let h = VNImageRequestHandler()\n"),
    (".swift", "let c = NSXPCConnection(serviceName: \"x\")\n"),
    (".swift", "import XPC\n"),
    (".c", "xpc_connection_create(NULL, NULL);\n"),
    (".toml", 'xpc-sys = "0.1"\n'),
    (".swift", "struct A: AppIntent {}\n"),
    (".swift", "import OSLog\n"),
    (".c", "os_signpost_event_emit(a, b, c);\n"),
    (".swift", 'let l = Logger(subsystem: "de.aethel", category: "x")\n'),
    (".toml", 'oslog = "0.2"\n'),
    (".swift", "import Virtualization\n"),
    (".m", "#import <Virtualization/Virtualization.h>\n"),
    (".swift", "let v = VZVirtualMachineConfiguration()\n"),
    (".swift", '.package(url: "https://github.com/apple/containerization", from: "0.1.0")\n'),
    (".toml", 'objc2-virtualization = "0.2"\n'),
    (".swift", "SecItemAdd(q, nil)\n"),
    (".swift", "import LocalAuthentication\n"),
    (".py", "def lese_Keychain(): pass\n"),
    (".toml", 'security-framework = "2"\n'),
    (".swift", "import Network\n"),
    (".m", "#import <Network/Network.h>\n"),
    (".swift", "let b = NWBrowser(for: d, using: p)\n"),
    (".swift", "async let a = laden()\n"),
    (".swift", "import SwiftData\n"),
    (".swift", "import Testing\n"),
)


def test_every_framework_signal_has_a_working_sample() -> None:
    """Jedes Signalmuster trifft auf mindestens einen Beispieltext (Anker eingeschlossen)."""
    uncovered = [
        f"{signal.name}: {signal.pattern.pattern}"
        for signal in applefirst.SIGNALS
        if not any(
            suffix in signal.suffixes and signal.hits(text, text.lower())[0] >= 1
            for suffix, text in SIGNAL_SAMPLES
        )
    ]
    assert not uncovered, "Signale ohne Beispieltreffer:\n" + "\n".join(uncovered)


# --- Unified Memory ----------------------------------------------------------


def test_unified_memory_hits_are_counted_in_code_and_docs(tmp_path: Path) -> None:
    item = _audit(
        tmp_path,
        "aethelUm",
        {
            "README.md": "Unified Memory auf dem M5 Max mit 128 GB.\n",
            "tools/a.py": "import mlx.core as mx\nx = mx.array([1])\n",
            "daten.json": '{"chip": "M4"}\n',
        },
    )

    # Doku: Unified Memory, M5, 128 GB (3); Code: mlx.core, mx.array (2); JSON zählt nicht.
    assert item.unified_memory_hits == 5


@pytest.mark.parametrize(
    "text",
    [
        "unified memory",
        "unifiedMemory",
        "MTLStorageMode.shared",
        "storageModeShared",
        "wired memory",
        "os_proc_available_memory()",
        "memory budget",
        "128GB",
        "128 GiB",
        "M5",
        "M4",
        "Apple Silicon",
    ],
)
def test_each_unified_memory_marker_counts(tmp_path: Path, text: str) -> None:
    item = _audit(tmp_path, "aethelUm", {"NOTIZ.md": f"Hinweis: {text}.\n", "a.py": "x = 1\n"}, git=False)

    assert item.unified_memory_hits == 1


def test_unified_memory_does_not_match_inside_words(tmp_path: Path) -> None:
    item = _audit(tmp_path, "aethelUm", {"NOTIZ.md": "M50 und AM4 und 1280GB\n", "a.py": "x = 1\n"})

    assert item.unified_memory_hits == 0


# --- Anti-Muster -------------------------------------------------------------


def test_ml_with_mps_or_coreml_is_not_a_cpu_path(tmp_path: Path) -> None:
    item = _audit(
        tmp_path,
        "aethelMps",
        {
            "ml/a.py": 'import torch\ndevice = torch.device("mps")\n',
            "ml/b.py": "import tensorflow as tf\nimport coremltools\n",
            "ml/c.py": "import onnxruntime\nprint('cpu')\n",
        },
    )

    assert item.anti_muster["ml_cpu"] == 1  # nur c.py
    assert "applefirst-ml-cpu" in _codes(item)
    finding = next(f for f in item.findings if f.code == "applefirst-ml-cpu")
    assert "torch/tensorflow ohne mps/coreml" in finding.message

    sauber = _audit(tmp_path, "aethelMps2", {"ml/a.py": 'import torch\ndevice = torch.device("mps")\n'})
    assert sauber.anti_muster["ml_cpu"] == 0
    assert "applefirst-ml-cpu" not in _codes(sauber)


def test_docker_files_and_scripts_are_counted(tmp_path: Path) -> None:
    item = _audit(
        tmp_path,
        "aethelDocker",
        {
            "Dockerfile": "FROM scratch\n",
            "docker-compose.yml": "services: {}\n",
            "compose.yaml": "services: {}\n",
            "deploy/Dockerfile.dev": "FROM scratch\n",
            "bin/start.sh": "#!/bin/sh\ndocker run --rm img\n",
            "bin/ok.sh": "#!/bin/sh\necho hallo\n",
            "tools/a.py": "x = 1\n",
        },
    )

    assert item.anti_muster["docker_lokal"] == 5
    assert "applefirst-docker-lokal" in _codes(item)


def test_subprocess_heavy_needs_twenty_files(tmp_path: Path) -> None:
    def files(count: int) -> dict[str, str]:
        return {f"s{i}.py": "import subprocess\nsubprocess.run(['x'])\n" for i in range(count)}

    knapp = _audit(tmp_path, "aethelSub19", files(19))
    genug = _audit(tmp_path, "aethelSub20", files(20))

    assert knapp.anti_muster["subprocess_lastig"] == 0
    assert genug.anti_muster["subprocess_lastig"] == 20
    assert genug.score == (knapp.score or 0) - 5


def test_large_bash_scripts_are_flagged(tmp_path: Path) -> None:
    item = _audit(
        tmp_path,
        "aethelBash",
        {"bin/gross.sh": _lines(201), "bin/grenze.sh": _lines(200)},
    )

    assert item.anti_muster["bash_gross"] == 1


def test_launchd_plist_without_smappservice(tmp_path: Path) -> None:
    plist = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<plist version="1.0"><dict>\n'
        "<key>Label</key><string>de.aethel.dienst</string>\n"
        "<key>ProgramArguments</key><array><string>/usr/local/bin/dienst</string></array>\n"
        "</dict></plist>\n"
    )
    ohne = _audit(
        tmp_path,
        "aethelLaunchd",
        {"LaunchAgents/de.aethel.dienst.plist": plist, "a.swift": "import Foundation\n"},
    )
    mit = _audit(
        tmp_path,
        "aethelLaunchdSM",
        {
            "LaunchAgents/de.aethel.dienst.plist": plist,
            "a.swift": (
                "import ServiceManagement\n"
                'try SMAppService.agent(plistName: "de.aethel.dienst.plist").register()\n'
            ),
        },
    )
    info_plist = _audit(
        tmp_path,
        "aethelInfo",
        {"Info.plist": "<plist><dict><key>CFBundleName</key><string>x</string></dict></plist>\n", "a.swift": "x\n"},
    )

    assert ohne.anti_muster["launchd_ohne_smappservice"] == 1
    finding = next(f for f in ohne.findings if f.code == "applefirst-launchd-ohne-smappservice")
    assert finding.severity == "info"
    assert mit.anti_muster["launchd_ohne_smappservice"] == 0
    assert "applefirst-launchd-ohne-smappservice" not in _codes(mit)
    assert info_plist.anti_muster["launchd_ohne_smappservice"] == 0


def test_numpy_without_mlx_and_electron(tmp_path: Path) -> None:
    numpy_nur = _audit(tmp_path, "aethelNp", {"a.py": "import numpy as np\n"})
    numpy_mlx = _audit(tmp_path, "aethelNpMlx", {"a.py": "import numpy as np\n", "b.py": "import mlx.core as mx\n"})
    electron = _audit(
        tmp_path,
        "aethelElectron",
        {"package.json": '{"devDependencies": {"electron": "^30.0.0"}}\n', "main.js": "console.log(1)\n"},
    )
    node = _audit(
        tmp_path,
        "aethelNode",
        {"package.json": '{"dependencies": {"express": "^4"}}\n', "main.js": "console.log(1)\n"},
    )

    assert numpy_nur.anti_muster["numpy_ohne_mlx"] == 1
    assert numpy_mlx.anti_muster["numpy_ohne_mlx"] == 0
    assert electron.anti_muster["electron"] == 1
    assert node.anti_muster["electron"] == 0
    # weiteres Anti-Muster: -5 (Python 100 % -20 bei numpy_nur)
    assert numpy_nur.score == 50 - 20 - 5
    assert electron.score == 50 - 5


def test_model_access_only_over_http(tmp_path: Path) -> None:
    http = {"llm.py": 'import requests\nr = requests.post("http://localhost:4000/v1/chat/completions")\n'}
    nur_http = _audit(tmp_path, "aethelHttp", http)
    mit_fm = _audit(
        tmp_path, "aethelFm", {**http, "fm.py": 'cmd = ["/usr/bin/fm", "respond"]\n'}
    )
    doku = _audit(tmp_path, "aethelDoku", {"README.md": "Router auf :4000\n", "a.py": "x = 1\n"})

    assert nur_http.anti_muster["modellzugang_http"] == 1
    finding = next(f for f in nur_http.findings if f.code == "applefirst-modellzugang-nur-http")
    assert finding.severity == "info"
    assert mit_fm.anti_muster["modellzugang_http"] == 0
    assert "applefirst-modellzugang-nur-http" not in _codes(mit_fm)
    assert doku.anti_muster["modellzugang_http"] == 0


def test_anti_muster_dict_is_always_complete(tmp_path: Path) -> None:
    item = _audit(tmp_path, "aethelLeer", {"a.swift": "x\n"})

    assert tuple(item.anti_muster) == applefirst.ANTI_MUSTER
    assert tuple(item.sprachen) == applefirst.LANGUAGES


# --- Findings ----------------------------------------------------------------


def test_kein_silizium_needs_more_than_2000_loc_and_no_frameworks(tmp_path: Path) -> None:
    gross = _audit(tmp_path, "aethelGross", {"src/lib.rs": _lines(2001)})
    grenze = _audit(tmp_path, "aethelGrenze", {"src/lib.rs": _lines(2000)})
    mit_fw = _audit(tmp_path, "aethelFw", {"src/lib.rs": _lines(2001), "Sources/A.swift": "import Metal\n"})

    finding = next(f for f in gross.findings if f.code == "applefirst-kein-silizium")
    assert finding.severity == "info"
    assert "applefirst-kein-silizium" not in _codes(grenze)
    assert "applefirst-kein-silizium" not in _codes(mit_fw)


def test_kein_unified_memory_for_ml_without_awareness(tmp_path: Path) -> None:
    ohne = _audit(tmp_path, "aethelMl", {"a.py": "import coremltools as ct\n"})
    mit = _audit(tmp_path, "aethelMlUm", {"a.py": "import mlx.core as mx\n"})
    kein_ml = _audit(tmp_path, "aethelKeinMl", {"Sources/A.swift": "import Network\n"})
    cpu = _audit(tmp_path, "aethelCpu", {"a.py": "import torch\n"})

    assert "applefirst-kein-unified-memory" in _codes(ohne)
    assert next(f for f in ohne.findings if f.code == "applefirst-kein-unified-memory").severity == "info"
    assert "applefirst-kein-unified-memory" not in _codes(mit)
    assert "applefirst-kein-unified-memory" not in _codes(kein_ml)
    assert "applefirst-kein-unified-memory" in _codes(cpu)


def test_grade_boundaries() -> None:
    assert applefirst.grade_for(100) == "Apple-first"
    assert applefirst.grade_for(80) == "Apple-first"
    assert applefirst.grade_for(79) == "teilweise"
    assert applefirst.grade_for(60) == "teilweise"
    assert applefirst.grade_for(59) == "vernachlässigt"
    assert applefirst.grade_for(40) == "vernachlässigt"
    assert applefirst.grade_for(39) == "fremdgeführt"
    assert applefirst.grade_for(0) == "fremdgeführt"
    assert applefirst.grade_for(None) == "ohne Code"


def test_score_is_clamped_to_zero(tmp_path: Path) -> None:
    files = {
        **PYTHON_FREMD,
        "bin/sb.sh": "#!/bin/sh\nsandbox-exec -f p ./x\ndocker run x\n" + _lines(201),
        "a.py": "import numpy\nimport requests\nrequests.get('http://localhost:4000')\n",
        "package.json": '{"devDependencies": {"electron": "1"}}\n',
        "LaunchAgents/x.plist": "<key>ProgramArguments</key>\n",
    }
    item = _audit(tmp_path, "aethelSchlecht", files)

    assert item.score is not None and 0 <= item.score <= 5


# --- Scan-Regeln -------------------------------------------------------------


def test_build_directories_and_hidden_folders_are_ignored(tmp_path: Path) -> None:
    item = _audit(
        tmp_path,
        "aethelFremd",
        {
            "node_modules/pkg/index.py": "import torch\n" + _lines(100),
            "target/debug/build.rs": _lines(100),
            "build/gen.py": _lines(100),
            ".venv/lib/x.py": _lines(100),
            ".hidden/y.py": "import torch\n" + _lines(100),
            "repo-worktrees/wt/z.py": _lines(100),
            "Sources/Ok/Ok.swift": "import Metal\n",
        },
    )

    assert item.sprachen["python"] == {"files": 0, "loc": 0}
    assert item.sprachen["rust"] == {"files": 0, "loc": 0}
    assert item.sprachen["swift"] == {"files": 1, "loc": 1}
    assert item.anti_muster["ml_cpu"] == 0


def test_depth_limit_is_three_directory_levels(tmp_path: Path) -> None:
    item = _audit(
        tmp_path,
        "aethelTief",
        {
            "top.py": _lines(1),
            "a/eins.py": _lines(2),
            "a/b/zwei.py": _lines(3),
            "a/b/c/drei.py": _lines(4),
            "a/b/c/d/vier.py": _lines(100),
        },
    )

    assert item.sprachen["python"] == {"files": 4, "loc": 10}


def test_files_are_read_only_up_to_256_kib(tmp_path: Path) -> None:
    filler = "# " + "x" * 98 + "\n"  # 101 Bytes je Zeile
    text = filler * 3000 + "import mlx.core as mx\n"  # > 256 KiB davor
    assert len(text.encode()) > applefirst.MAX_READ_BYTES
    item = _audit(tmp_path, "aethelGrossDatei", {"gross.py": text})

    assert "MLX" not in item.frameworks
    assert item.sprachen["python"]["files"] == 1
    assert 2000 < item.sprachen["python"]["loc"] < 3001


def test_symlinks_are_not_followed(tmp_path: Path) -> None:
    fremd = tmp_path / "fremd"
    fremd.mkdir()
    (fremd / "x.py").write_text(_lines(50), encoding="utf-8")
    root = _repo(tmp_path, "aethelLink", {"a.py": _lines(1)})
    (root / "datei.py").symlink_to(fremd / "x.py")
    (root / "ordner").symlink_to(fremd, target_is_directory=True)

    item = applefirst.audit(_report("aethelLink", str(root)), root)

    assert item.sprachen["python"] == {"files": 1, "loc": 1}


def test_belege_are_capped_and_name_file_and_hit(tmp_path: Path) -> None:
    files = {f"app/m{i}.py": "import torch\n" for i in range(15)}
    files["Sources/A.swift"] = "import Metal\n"
    item = _audit(tmp_path, "aethelBelege", files)

    assert len(item.belege) == 10
    # Je Signal zuerst ein Beleg: Metal steht trotz der 15 torch-Dateien drin.
    assert "Sources/A.swift: import Metal" in item.belege
    assert "app/m0.py: import torch" in item.belege


def test_audit_is_strictly_read_only(tmp_path: Path) -> None:
    root = _repo(tmp_path, "aethelLesen", SWIFT_APPLE_FIRST)

    def snapshot() -> dict[str, tuple[int, int]]:
        return {
            p.relative_to(root).as_posix(): (p.stat().st_size, p.stat().st_mtime_ns)
            for p in sorted(root.rglob("*"))
            if p.is_file() and ".git/" not in p.relative_to(root).as_posix() + "/"
        }

    before = snapshot()
    applefirst.audit(_report("aethelLesen", str(root)), root)
    assert snapshot() == before


# --- build -------------------------------------------------------------------


def test_build_skips_worktrees_and_sorts_by_name(tmp_path: Path) -> None:
    _repo(tmp_path, "zeta", {"a.py": _lines(5)})
    _repo(tmp_path, "Alpha", SWIFT_APPLE_FIRST)
    _repo(tmp_path, "zeta-wt", {"a.py": _lines(5)})
    reports = (
        _report("zeta", "zeta"),
        _report("Alpha", "Alpha"),
        _report("zeta-wt", "zeta-wt", worktree=True),
    )

    items = applefirst.build(reports, tmp_path)

    assert [item.repo for item in items] == ["Alpha", "zeta"]
    assert items[0].grade == "Apple-first"


def test_build_reads_real_git_repos_end_to_end(tmp_path: Path) -> None:
    _repo(tmp_path, "aethelKern", SWIFT_APPLE_FIRST)
    _repo(tmp_path, "aethelPy", PYTHON_FREMD)
    reports = [collect(identity) for identity in discover(tmp_path)]

    items = {item.repo: item for item in applefirst.build(reports, tmp_path)}

    assert set(items) == {"aethelKern", "aethelPy"}
    assert items["aethelKern"].grade == "Apple-first"
    assert items["aethelPy"].grade == "fremdgeführt"


def test_as_dict_is_json_serializable_and_complete(tmp_path: Path) -> None:
    item = _audit(tmp_path, "aethelPy", PYTHON_FREMD)

    data = json.loads(json.dumps(item.as_dict()))

    assert set(data) == {
        "repo",
        "score",
        "grade",
        "python_anteil",
        "sprachen",
        "frameworks",
        "unified_memory_hits",
        "anti_muster",
        "findings",
        "belege",
    }
    assert data["repo"] == "aethelPy"
    assert data["findings"][0]["code"] == "applefirst-python-schwer"
    assert set(data["findings"][0]) == {"code", "severity", "message", "action", "repo"}


# --- Ausgabe -----------------------------------------------------------------


@pytest.fixture
def items(tmp_path: Path) -> tuple[applefirst.AppleFirst, ...]:
    _repo(tmp_path, "aethelKern", SWIFT_APPLE_FIRST)
    _repo(tmp_path, "aethelPy", PYTHON_FREMD)
    _repo(tmp_path, "aethelDoku", {"README.md": "# Doku\n"})
    reports = (
        _report("aethelKern", "aethelKern"),
        _report("aethelPy", "aethelPy"),
        _report("aethelDoku", "aethelDoku"),
    )
    return applefirst.build(reports, tmp_path)


def test_render_markdown_has_heading_grades_and_top_ten(items: tuple[applefirst.AppleFirst, ...]) -> None:
    md = applefirst.render_markdown(items)

    assert md.startswith("# Apple-first-Audit")
    assert "## Verteilung der Grades" in md
    for grade in ("Apple-first", "teilweise", "vernachlässigt", "fremdgeführt", "ohne Code"):
        assert f"| {grade} |" in md
    assert "## Top 10 schlechteste Scores" in md
    top = md.split("## Top 10 schlechteste Scores")[1].split("## Alle Repos")[0]
    assert "aethelPy" in top
    assert "docker_lokal=1" in top
    assert "100" in top  # Python %
    assert "aethelDoku" not in top  # ohne Code kein Rang
    table = md.split("## Alle Repos")[1]
    header = next(line for line in table.splitlines() if line.startswith("| Repo"))
    for column in ("Score", "Grade", "Python %", "Frameworks", "Unified Memory", "Anti-Muster", "Erste Lücke"):
        assert column in header
    kern_row = next(line for line in table.splitlines() if line.startswith("| aethelKern"))
    assert "Apple-first" in kern_row and "MLX" in kern_row and "Metal" in kern_row
    py_row = next(line for line in table.splitlines() if line.startswith("| aethelPy"))
    assert "applefirst-python-schwer" in py_row
    doku_row = next(line for line in table.splitlines() if line.startswith("| aethelDoku"))
    assert "ohne Code" in doku_row


def test_render_markdown_top_ten_limits_to_ten_worst(tmp_path: Path) -> None:
    reports = []
    for index in range(12):
        _repo(tmp_path, f"py{index:02d}", {"a.py": _lines(5)})
        reports.append(_report(f"py{index:02d}", f"py{index:02d}"))
    _repo(tmp_path, "gut", SWIFT_APPLE_FIRST)
    reports.append(_report("gut", "gut"))

    md = applefirst.render_markdown(applefirst.build(reports, tmp_path))
    top = md.split("## Top 10 schlechteste Scores")[1].split("## Alle Repos")[0]
    rows = [line for line in top.splitlines() if line.startswith("| ") and not line.startswith(("| Rang", "|---"))]

    assert len(rows) == 10
    assert "| gut " not in top


def test_render_markdown_handles_empty_input() -> None:
    md = applefirst.render_markdown(())

    assert md.startswith("# Apple-first-Audit")
    assert "Kein Repo mit Quellcode." in md


def test_render_json_is_valid_and_versioned(items: tuple[applefirst.AppleFirst, ...]) -> None:
    data = json.loads(applefirst.render_json(items))

    assert data["schema"] == "aethel.projects.applefirst/v1"
    assert [repo["repo"] for repo in data["repos"]] == [item.repo for item in items]
    assert data["summary"]["repos"] == 3
    by_repo = {repo["repo"]: repo for repo in data["repos"]}
    assert by_repo["aethelDoku"]["score"] is None
    assert by_repo["aethelDoku"]["grade"] == "ohne Code"
    assert by_repo["aethelKern"]["grade"] == "Apple-first"
    assert "Python dünn" in json.dumps(data, ensure_ascii=False)


def test_summary_counts(items: tuple[applefirst.AppleFirst, ...]) -> None:
    stats = applefirst.summary(items)

    kern = next(i for i in items if i.repo == "aethelKern")
    py = next(i for i in items if i.repo == "aethelPy")
    assert stats["repos"] == 3
    assert stats["grades"] == {
        "Apple-first": 1,
        "teilweise": 0,
        "vernachlässigt": 0,
        "fremdgeführt": 1,
        "ohne Code": 1,
    }
    assert kern.score is not None and py.score is not None
    assert stats["durchschnitt_score"] == round((kern.score + py.score) / 2, 1)
    assert stats["python_schwer"] == 1
    assert stats["python_schwer_repos"] == ["aethelPy"]
    assert stats["silizium"] == 1
    assert stats["silizium_repos"] == ["aethelKern"]


def test_summary_of_nothing() -> None:
    stats = applefirst.summary(())

    assert stats["repos"] == 0
    assert stats["durchschnitt_score"] is None
    assert sum(stats["grades"].values()) == 0
