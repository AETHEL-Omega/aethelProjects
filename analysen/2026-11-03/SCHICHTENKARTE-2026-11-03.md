# Schichtenkarte

322 Repositories (Worktrees ausgenommen); 13 von 18 Schichten belegt, 5 ohne eigenes Repo.

## Schichten

| Code | Schicht | Eigene Repos | Fremde Repos | Unklar | Beispiele |
|---|---|---|---|---|---|
| S0 | Rechenmodell/Silizium-Simulation | 6 | 1 | 0 | aethelHelix, aiderDesktop_memristor_v1, bit_encodings, osxq-pennylane, photon-defense, … |
| S1 | Firmware | 0 | 0 | 0 | - |
| S2 | Kernel/OS | 2 | 0 | 0 | aethel_os, lector_os |
| S3 | Isolation/Hypervisor | 2 | 0 | 0 | aethel_sandbox, aethelContainer |
| S4 | Systemdienste/Zustand/Rechte | 2 | 0 | 0 | aethelLanding, workspace-manifest |
| S5 | Komponentenlaufzeit/Agenten | 18 | 3 | 0 | aethel-forge, aethelAgent, aethelAgent, aethelAgentFactory, aethelAgentFactory, … |
| S6 | Sprache/Compiler/Toolchain | 0 | 0 | 0 | - |
| S7 | Build/Release | 4 | 16 | 0 | aethel-build-orchestrator, claude-code-proxy, nius-linux, youtubereader_flutter, aider, … |
| S8 | Daten/Wissen | 15 | 0 | 0 | aethel-omega, aethel-v6-omega, aethel_memoria, aethelOmegaLM, aethelOmegaM0, … |
| S9 | Kommunikation/Verbund | 3 | 0 | 0 | aethelema, aethelema, omega_bridge |
| S10 | Plattform-SDK/Bibliothek | 49 | 3 | 0 | AETHEL, aethel-evolution, aethel-evolutionCascade, aethel-forensics, aethel-foundation, … |
| S11 | Anwendung | 101 | 0 | 0 | aethel_architect, aethel_architect, aethel_ausbildung, aethel_ausbildung, aethel_bitplay, … |
| S12 | Oberfläche/Cockpit | 5 | 1 | 0 | aethel_cockpit, aethelMacUIAgent, flutter_ui_showcase, omega_ui, vintage_Radio_newUI, … |
| S13 | Sicherheit/Identität | 0 | 0 | 0 | - |
| S14 | Beobachtbarkeit | 2 | 0 | 0 | aethelAnalytics, faith_metrics |
| S15 | Qualität/Test/Eval | 10 | 2 | 0 | aethel-test-orchestrator, aethelCodeAnalyzer, aethelProjects, GrokAethelBench, swt-test, … |
| S16 | Distribution | 0 | 0 | 0 | - |
| S17 | Entscheidung/Doku/Wissen-Text | 0 | 0 | 0 | - |
| SX | unbestimmt | 51 | 23 | 3 | adg_testbench, aethel-apple, aethel-codegraph, aethel-launcher, aethel-macos-work-surface, … |

## Leere Schichten

Leer: diese Schichten haben kein eigenes Repo.

- S1 Firmware
- S6 Sprache/Compiler/Toolchain
- S13 Sicherheit/Identität
- S16 Distribution
- S17 Entscheidung/Doku/Wissen-Text

## Detail

| Repo | Schicht | Herkunft | Reife | Konfidenz | Beleg |
|---|---|---|---|---|---|
| aethelHelix | S0 Rechenmodell/Silizium-Simulation | eigen | Prototyp | medium | Name „helix“ → S0; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aiderDesktop_memristor_v1 | S0 Rechenmodell/Silizium-Simulation | eigen | Prototyp | medium | Name „memristor“ → S0; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| bit_encodings | S0 Rechenmodell/Silizium-Simulation | eigen | Prototyp | medium | Name „bit_encodings“ → S0; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| osxQ | S0 Rechenmodell/Silizium-Simulation | fremd | Prototyp | medium | Name „osxq“ → S0; abweichender Marker S11: quantumstudio/flutter_app/pubspec.yaml ohne Rust-Crate; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| osxq-pennylane | S0 Rechenmodell/Silizium-Simulation | eigen | Prototyp | medium | Name „osxq“ → S0; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| photon-defense | S0 Rechenmodell/Silizium-Simulation | eigen | Prototyp | medium | Name „photon“ → S0; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| photon-plm | S0 Rechenmodell/Silizium-Simulation | eigen | Prototyp | medium | Name „photon“ → S0; abweichender Marker S11: pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_os | S2 Kernel/OS | eigen | Skizze | medium | Name „os“ → S2; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| lector_os | S2 Kernel/OS | eigen | Prototyp | medium | Name „os“ → S2; abweichender Marker S10: native/rust/Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_sandbox | S3 Isolation/Hypervisor | eigen | Prototyp | medium | Name „sandbox“ → S3; abweichender Marker S11: pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelContainer | S3 Isolation/Hypervisor | eigen | Solide | medium | Name „container“ → S3; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelLanding | S4 Systemdienste/Zustand/Rechte | eigen | Prototyp | medium | Name „landing“ → S4; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| workspace-manifest | S4 Systemdienste/Zustand/Rechte | eigen | Professional | medium | Name „manifest“ → S4; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel-forge | S5 Komponentenlaufzeit/Agenten | eigen | Skizze | medium | Name „forge“ → S5; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelAgent | S5 Komponentenlaufzeit/Agenten | eigen | Skizze | medium | Name „agent“ → S5; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelAgent | S5 Komponentenlaufzeit/Agenten | eigen | Prototyp | medium | Name „agent“ → S5; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelAgentFactory | S5 Komponentenlaufzeit/Agenten | eigen | Prototyp | medium | Name „agent“ → S5; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelAgentFactory | S5 Komponentenlaufzeit/Agenten | eigen | Solide | medium | Name „agent“ → S5; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelAgentRuntime | S5 Komponentenlaufzeit/Agenten | eigen | Solide | high | Name „agent-runtime“ → S5; bestätigt durch skills/aethel-terminal-cockpit-user-agent/SKILL.md; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelBot | S5 Komponentenlaufzeit/Agenten | eigen | Prototyp | medium | Name „bot“ → S5; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelFactory | S5 Komponentenlaufzeit/Agenten | eigen | Skizze | medium | Name „factory“ → S5; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelLocalCoder | S5 Komponentenlaufzeit/Agenten | eigen | Prototyp | medium | Name „coder“ → S5; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelScripts | S5 Komponentenlaufzeit/Agenten | eigen | Solide | medium | Name „scripts“ → S5; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelScripts-clean | S5 Komponentenlaufzeit/Agenten | eigen | Prototyp | medium | Name „scripts“ → S5; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| bitplay_agents | S5 Komponentenlaufzeit/Agenten | eigen | Skizze | medium | Name „agent“ → S5; abweichender Marker S11: pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| deepseek-coder | S5 Komponentenlaufzeit/Agenten | fremd | Prototyp | medium | Name „coder“ → S5; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| digitalSoftwareFactory | S5 Komponentenlaufzeit/Agenten | eigen | Solide | medium | Name „factory“ → S5; abweichender Marker S11: apps/digital_factory_app/pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| hydra_forge | S5 Komponentenlaufzeit/Agenten | eigen | Prototyp | medium | Name „forge“ → S5; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| mini-swe-agent | S5 Komponentenlaufzeit/Agenten | fremd | Prototyp | medium | Name „agent“ → S5; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| run-cli-task-aethel_coder-aider-mlx | S5 Komponentenlaufzeit/Agenten | eigen | Prototyp | medium | Name „coder“ → S5; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| run-task-challenge-quick-001-aethel_coder-aider-mlx | S5 Komponentenlaufzeit/Agenten | eigen | Prototyp | medium | Name „coder“ → S5; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| run-task-challenge-quick-001-aethel_coder-aider-mlx | S5 Komponentenlaufzeit/Agenten | eigen | Prototyp | medium | Name „coder“ → S5; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| run-task-rust-substrate-001-aethel_coder-aider-mlx | S5 Komponentenlaufzeit/Agenten | eigen | Prototyp | medium | Name „coder“ → S5; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| swe-agent | S5 Komponentenlaufzeit/Agenten | fremd | Prototyp | medium | Name „agent“ → S5; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| aethel-build-orchestrator | S7 Build/Release | eigen | Skizze | medium | Name „build“ → S7; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aider | S7 Build/Release | fremd | Prototyp | medium | Marker benchmark/Dockerfile → S7; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| bsc | S7 Build/Release | fremd | Prototyp | medium | Marker Dockerfile → S7; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| claude-code-proxy | S7 Build/Release | eigen | Prototyp | medium | Marker Dockerfile → S7; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| cn | S7 Build/Release | fremd | Prototyp | medium | Marker manual-testing-sandbox/Dockerfile → S7; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| cognee | S7 Build/Release | fremd | Prototyp | medium | Marker Dockerfile → S7; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| crush | S7 Build/Release | fremd | Prototyp | medium | Marker flake.nix → S7; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| gptme | S7 Build/Release | fremd | Prototyp | medium | Marker scripts/Dockerfile → S7; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| instructor | S7 Build/Release | fremd | Solide | medium | Marker examples/citation_with_extraction/Dockerfile → S7; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| letta-code | S7 Build/Release | fremd | Prototyp | medium | Marker flake.nix → S7; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| nius-linux | S7 Build/Release | eigen | Skizze | medium | Marker flake.nix → S7; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| opencode | S7 Build/Release | fremd | Prototyp | medium | Marker flake.nix → S7; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| openhands | S7 Build/Release | fremd | Solide | medium | Marker docker/Dockerfile → S7; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| outlines | S7 Build/Release | fremd | Prototyp | medium | Marker flake.nix → S7; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| promptfoo | S7 Build/Release | fremd | Prototyp | medium | Marker Dockerfile → S7; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| rasa | S7 Build/Release | fremd | Prototyp | medium | Marker Dockerfile → S7; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| semgrep | S7 Build/Release | fremd | Prototyp | medium | Marker Dockerfile → S7; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| sgpt | S7 Build/Release | fremd | Prototyp | medium | Marker Dockerfile → S7; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| spacy | S7 Build/Release | fremd | Prototyp | medium | Marker website/Dockerfile → S7; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| youtubereader_flutter | S7 Build/Release | eigen | Prototyp | medium | Marker Dockerfile → S7; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel-omega | S8 Daten/Wissen | eigen | Solide | medium | Marke „omega“ → S8; abweichender Marker S7: Dockerfile; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel-v6-omega | S8 Daten/Wissen | eigen | Prototyp | medium | Name „omega“ → S8; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_memoria | S8 Daten/Wissen | eigen | Prototyp | medium | Name „memoria“ → S8; abweichender Marker S11: pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelOmegaLM | S8 Daten/Wissen | eigen | Prototyp | medium | Marke „omega“ → S8; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelOmegaM0 | S8 Daten/Wissen | eigen | Prototyp | medium | Marke „omega“ → S8; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| omega-system | S8 Daten/Wissen | eigen | Skizze | medium | Marke „omega“ → S8; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| omega_domain | S8 Daten/Wissen | eigen | Prototyp | medium | Marke „omega“ → S8; abweichender Marker S11: pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| run-cli-task-aider_omega-aider-mlx | S8 Daten/Wissen | eigen | Prototyp | medium | Name „omega“ → S8; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| run-cli-task-claude_code_omega-aider-mlx | S8 Daten/Wissen | eigen | Prototyp | medium | Name „omega“ → S8; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| run-task-challenge-quick-001-aider_omega-aider-mlx | S8 Daten/Wissen | eigen | Prototyp | medium | Name „omega“ → S8; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| run-task-challenge-quick-001-aider_omega-aider-mlx | S8 Daten/Wissen | eigen | Prototyp | medium | Name „omega“ → S8; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| run-task-challenge-quick-001-claude_code_omega-aider-mlx | S8 Daten/Wissen | eigen | Prototyp | medium | Name „omega“ → S8; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| run-task-challenge-quick-001-claude_code_omega-aider-mlx | S8 Daten/Wissen | eigen | Prototyp | medium | Name „omega“ → S8; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| run-task-rust-substrate-001-aider_omega-aider-mlx | S8 Daten/Wissen | eigen | Prototyp | medium | Name „omega“ → S8; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| run-task-rust-substrate-001-claude_code_omega-aider-mlx | S8 Daten/Wissen | eigen | Prototyp | medium | Name „omega“ → S8; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelema | S9 Kommunikation/Verbund | eigen | Prototyp | medium | Name „ema“ → S9; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelema | S9 Kommunikation/Verbund | eigen | Prototyp | medium | Name „ema“ → S9; abweichender Marker S10: rust-core/fuzz/Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| omega_bridge | S9 Kommunikation/Verbund | eigen | Prototyp | medium | Name „bridge“ → S9; abweichender Marker S11: pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| AETHEL | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel-evolution | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel-evolutionCascade | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel-forensics | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel-foundation | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel-supervisor | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel-v6 | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel1 | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel1 | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel1 | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel1 | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel1 | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel1 | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel1 | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel1 | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel1 | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel1 | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel2 | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel2 | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel2 | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel2 | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel2 | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_core | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Name „core“ → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_design | S10 Plattform-SDK/Bibliothek | eigen | Solide | medium | Name „design“ → S10; abweichender Marker S11: pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_product_shells | S10 Plattform-SDK/Bibliothek | eigen | Solide | medium | Name „shells“ → S10; abweichender Marker S11: pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelDeepLearning | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelDesktopLean1 | S10 Plattform-SDK/Bibliothek | eigen | Skizze | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelDesktopResearch | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelGemini-project | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker native/rust/Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelIntegrationProvisorisch | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethellm | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker rust/Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelMistral | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelPromtEngineerung | S10 Plattform-SDK/Bibliothek | eigen | Solide | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelPromtEngineerung | S10 Plattform-SDK/Bibliothek | eigen | Solide | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelSGML | S10 Plattform-SDK/Bibliothek | eigen | Solide | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aiderDesktop | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aiderDesktopLogos | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| Athelix | S10 Plattform-SDK/Bibliothek | eigen | Solide | medium | Marker athelix_engine/Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| BIblePublishProject | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker crates/Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| bitplay_core | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Name „core“ → S10; abweichender Marker S11: pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| fimas | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| goose | S10 Plattform-SDK/Bibliothek | fremd | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| interpreter | S10 Plattform-SDK/Bibliothek | fremd | Prototyp | medium | Marker codex-rs/Cargo.toml ([workspace]) → S10; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| logos | S10 Plattform-SDK/Bibliothek | eigen | Solide | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| memoristorCursor | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| pragmaticAethelDesktop | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| ragFileSystemChatGpt5 | S10 Plattform-SDK/Bibliothek | eigen | Solide | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| run-cli-task-aethel_aider-aider-mlx | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| run-task-challenge-quick-001-aethel_aider-aider-mlx | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| run-task-challenge-quick-001-aethel_aider-aider-mlx | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| run-task-rust-substrate-001-aethel_aider-aider-mlx | S10 Plattform-SDK/Bibliothek | eigen | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| tree-sitter | S10 Plattform-SDK/Bibliothek | fremd | Prototyp | medium | Marker Cargo.toml ([workspace]) → S10; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| aethel_architect | S11 Anwendung | eigen | Skizze | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_architect | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_ausbildung | S11 Anwendung | eigen | Skizze | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_ausbildung | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_bitplay | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_buerger | S11 Anwendung | eigen | Skizze | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_buerger | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_campus | S11 Anwendung | eigen | Skizze | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_campus | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_daktari | S11 Anwendung | eigen | Skizze | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_daktari | S11 Anwendung | eigen | Solide | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_didact | S11 Anwendung | eigen | Skizze | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_didact | S11 Anwendung | eigen | Solide | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_grundgesetz | S11 Anwendung | eigen | Skizze | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_grundgesetz | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_handwerk | S11 Anwendung | eigen | Skizze | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_handwerk | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_harmonia | S11 Anwendung | eigen | Skizze | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_harmonia | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_heimat | S11 Anwendung | eigen | Skizze | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_heimat | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_justitia | S11 Anwendung | eigen | Skizze | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_justitia | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_konformitaet | S11 Anwendung | eigen | Skizze | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_konformitaet | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_lexikon | S11 Anwendung | eigen | Skizze | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_lexikon | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_lichthaus | S11 Anwendung | eigen | Skizze | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_lichthaus | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_logopaedie | S11 Anwendung | eigen | Skizze | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_logopaedie | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_music_studio | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_music_studio | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_mwalimu | S11 Anwendung | eigen | Skizze | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_mwalimu | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_neno | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_newsroom | S11 Anwendung | eigen | Prototyp | medium | Marker app/pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_observatory | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_openclaw | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_orion | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_pharma | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_polis | S11 Anwendung | eigen | Solide | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_quantor | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_rag_workbench | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_reader | S11 Anwendung | eigen | Prototyp | high | Name „reader“ → S11; bestätigt durch pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_secure_messenger | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_sermon_archive | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_shamba | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_shield | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_stammbaum | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_studio | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_uhuru | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_unified | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_vintage_radio | S11 Anwendung | eigen | Prototyp | high | Name „radio“ → S11; bestätigt durch pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_voice | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_wachturm | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_webbrowser_complex | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_worship | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_xray | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_zertifikat | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelappstore | S11 Anwendung | eigen | Prototyp | high | Name „appstore“ → S11; bestätigt durch pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelBrowser | S11 Anwendung | eigen | Solide | medium | Name „browser“ → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelBrowser-build | S11 Anwendung | eigen | Solide | medium | Name „browser“ → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelCoWork | S11 Anwendung | eigen | Solide | medium | Marker aethel_cowork_flutter/pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelCoWork | S11 Anwendung | eigen | Solide | medium | Marker aethel_cowork_flutter/pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelFamilyAppStore | S11 Anwendung | eigen | Prototyp | medium | Name „app“ → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelGemini | S11 Anwendung | eigen | Prototyp | medium | Marker worktrees/perichoresis-gutenberg-extract/pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelHealthLab | S11 Anwendung | eigen | Prototyp | medium | Name „lab“ → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelreasoningcomputer | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelTerminal | S11 Anwendung | eigen | Solide | high | Name „terminal“ → S11; bestätigt durch pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| bitplay_cli | S11 Anwendung | eigen | Skizze | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| bitplay_lab_flutter | S11 Anwendung | eigen | Prototyp | medium | Name „lab“ → S11; abweichender Marker S10: rust/bitplay_fast/Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| bitplay_lab_flutter-orginal | S11 Anwendung | eigen | Prototyp | high | Name „lab“ → S11; bestätigt durch pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| bitplay_lab_original | S11 Anwendung | eigen | Prototyp | high | Name „lab“ → S11; bestätigt durch pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| bitplay_labs | S11 Anwendung | eigen | Skizze | high | Name „lab“ → S11; bestätigt durch pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| bitplay_sip | S11 Anwendung | eigen | Skizze | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| bitplay_visualizers | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| bitplay_widgets | S11 Anwendung | eigen | Skizze | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| blocks_3d | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| cash_pilot | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| heritage_bible | S11 Anwendung | eigen | Skizze | medium | Name „heritage“ → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| heritage_bible_aethel | S11 Anwendung | eigen | Prototyp | medium | Name „heritage“ → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| heritage_bible_aethelNuru | S11 Anwendung | eigen | Solide | medium | Name „heritage“ → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| heritage_bible_engine | S11 Anwendung | eigen | Prototyp | medium | Name „heritage“ → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| heritage_bible_flutter | S11 Anwendung | eigen | Prototyp | high | Name „heritage“ → S11; bestätigt durch pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| heritage_bible_flutter_perichoresis_refactor | S11 Anwendung | eigen | Skizze | medium | Name „heritage“ → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| impact_lens | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| kinder_guard | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| metropolitan_developer_impeller | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| metropolitan_impeller | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| mymessanger | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| photon_radio | S11 Anwendung | eigen | Prototyp | high | Name „radio“ → S11; bestätigt durch pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| space_radio | S11 Anwendung | eigen | Prototyp | high | Name „radio“ → S11; bestätigt durch pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| universitas | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| vintage_language_lab | S11 Anwendung | eigen | Prototyp | high | Name „lab“ → S11; bestätigt durch pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| vintage_media_center | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| vintage_radio | S11 Anwendung | eigen | Solide | medium | Name „radio“ → S11; abweichender Marker S10: aethellm/rust/Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| vintage_radio_aethel | S11 Anwendung | eigen | Prototyp | high | Name „radio“ → S11; bestätigt durch pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| vintage_radio_harness | S11 Anwendung | eigen | Prototyp | medium | Name „radio“ → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| weltformel | S11 Anwendung | eigen | Prototyp | medium | Marker pubspec.yaml ohne Rust-Crate → S11; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| youtube_reader | S11 Anwendung | eigen | Prototyp | medium | Name „reader“ → S11; abweichender Marker S7: Dockerfile; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_cockpit | S12 Oberfläche/Cockpit | eigen | Prototyp | medium | Name „cockpit“ → S12; abweichender Marker S11: pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelMacUIAgent | S12 Oberfläche/Cockpit | eigen | Solide | medium | Name „ui“ → S12; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| ComfyUI | S12 Oberfläche/Cockpit | fremd | Prototyp | medium | Name „ui“ → S12; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| flutter_ui_showcase | S12 Oberfläche/Cockpit | eigen | Prototyp | medium | Name „ui“ → S12; abweichender Marker S11: pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| omega_ui | S12 Oberfläche/Cockpit | eigen | Prototyp | medium | Name „ui“ → S12; abweichender Marker S11: pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| vintage_Radio_newUI | S12 Oberfläche/Cockpit | eigen | Prototyp | medium | Name „ui“ → S12; abweichender Marker S11: pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelAnalytics | S14 Beobachtbarkeit | eigen | Prototyp | medium | Name „analytics“ → S14; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| faith_metrics | S14 Beobachtbarkeit | eigen | Prototyp | medium | Name „metrics“ → S14; abweichender Marker S11: pubspec.yaml ohne Rust-Crate; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel-test-orchestrator | S15 Qualität/Test/Eval | eigen | Prototyp | medium | Name „test“ → S15; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelCodeAnalyzer | S15 Qualität/Test/Eval | eigen | Prototyp | medium | Name „analyzer“ → S15; abweichender Marker S10: Cargo.toml ([workspace]); Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelProjects | S15 Qualität/Test/Eval | eigen | Professional | medium | Name „projects“ → S15; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| click_test_project | S15 Qualität/Test/Eval | fremd | Prototyp | medium | Name „test“ → S15; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| GrokAethelBench | S15 Qualität/Test/Eval | eigen | Prototyp | medium | Name „bench“ → S15; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| swe-bench | S15 Qualität/Test/Eval | fremd | Prototyp | medium | Name „bench“ → S15; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| swt-test | S15 Qualität/Test/Eval | eigen | Skizze | medium | Name „test“ → S15; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| testProject1 | S15 Qualität/Test/Eval | eigen | Skizze | medium | Name „test“ → S15; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| TestSWT | S15 Qualität/Test/Eval | eigen | Skizze | medium | Name „test“ → S15; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| TestSWT | S15 Qualität/Test/Eval | eigen | Skizze | medium | Name „test“ → S15; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| TestXCode | S15 Qualität/Test/Eval | eigen | Skizze | medium | Name „test“ → S15; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| TestXCode | S15 Qualität/Test/Eval | eigen | Skizze | medium | Name „test“ → S15; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| adg_testbench | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel-apple | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel-codegraph | SX unbestimmt | eigen | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel-launcher | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel-macos-work-surface | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel-systems | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel-workspace | SX unbestimmt | eigen | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_cowork_flutter | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_cowork_flutter | SX unbestimmt | eigen | Solide | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_muehle | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_python | SX unbestimmt | eigen | Solide | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethel_pythonclone | SX unbestimmt | eigen | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelCLIGames | SX unbestimmt | eigen | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Namenspräfix „aethel“ |
| aethelCodeAlphaClean | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelEditor | SX unbestimmt | eigen | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Namenspräfix „aethel“ |
| aethelHall | SX unbestimmt | eigen | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelMessanger | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelSystemObservation | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelVoiceControl | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aethelZLAMA | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| ai-fastlane-governance | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aider_desktop_grok | SX unbestimmt | eigen | Solide | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| aiderDesktopCursor | SX unbestimmt | unklar | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft unklar: kein Remote, kein Namenspräfix |
| aiderDesktopGrok | SX unbestimmt | eigen | Solide | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| amrlib | SX unbestimmt | fremd | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| autogen | SX unbestimmt | fremd | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| bitplay | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| byztxt | SX unbestimmt | fremd | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| cline | SX unbestimmt | fremd | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| crewai | SX unbestimmt | fremd | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| dotfiles | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| ds4 | SX unbestimmt | fremd | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| dspy | SX unbestimmt | fremd | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| fjord_race | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| flutter | SX unbestimmt | eigen | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| guidance | SX unbestimmt | fremd | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| helloscout | SX unbestimmt | eigen | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| helloscout | SX unbestimmt | eigen | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| intelizign_consulting | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| kgu-sgml-pipeline | SX unbestimmt | eigen | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| kgu-sgml-pipeline | SX unbestimmt | eigen | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| kss-tools | SX unbestimmt | eigen | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| kss-tools | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| langgraph | SX unbestimmt | fremd | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| letta | SX unbestimmt | fremd | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| llm | SX unbestimmt | fremd | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| macos_study_plattform | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| manuel-jsx-snippets | SX unbestimmt | eigen | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| manuel-jsx-snippets | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| ManuelCrypto | SX unbestimmt | eigen | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| ManuelCrypto | SX unbestimmt | eigen | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| manuelcrypto-maven | SX unbestimmt | eigen | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| manuelcrypto-maven | SX unbestimmt | eigen | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| metropolitan_developer | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| mods | SX unbestimmt | fremd | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| neon-pulse-survivors | SX unbestimmt | fremd | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| newsfeed_engine | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| pydantic-ai | SX unbestimmt | fremd | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| python_backend | SX unbestimmt | eigen | Solide | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| r2e-gym | SX unbestimmt | fremd | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| rllm | SX unbestimmt | fremd | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| SafeNest | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| scrollmapper | SX unbestimmt | fremd | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| smolagents | SX unbestimmt | fremd | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| snips-nlu | SX unbestimmt | fremd | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| stanza | SX unbestimmt | fremd | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| StartUp | SX unbestimmt | eigen | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| SuperDuperMarkt | SX unbestimmt | eigen | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| SuperDuperMarktBrockhaus | SX unbestimmt | eigen | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| swarm | SX unbestimmt | fremd | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| syrnt | SX unbestimmt | fremd | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| tau | SX unbestimmt | fremd | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft fremd: Remote nicht bei AETHEL-Omega/ManuelWilde |
| testprojekt1 | SX unbestimmt | unklar | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft unklar: kein Remote, kein Namenspräfix |
| vintage_tv | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| website_aethel_systems | SX unbestimmt | eigen | Prototyp | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |
| werkstatt | SX unbestimmt | unklar | Skizze | low | weder Namens- noch Dateiregel getroffen; Herkunft unklar: kein Remote, kein Namenspräfix |
| youtubereader-python | SX unbestimmt | eigen | Solide | low | weder Namens- noch Dateiregel getroffen; Herkunft eigen: Remote bei AETHEL-Omega/ManuelWilde |

