# Apple-first-Audit

Kanon: Rust ist Kern, Swift ist Apple-native Laufzeit, Flutter ist Client, Python ist Übergangsrand, Bash ist Aufruf. Ziel: Unified Memory und das Silizium des M5 Max (CPU, GPU, NPU, Beschleuniger) tatsächlich nutzen.

322 Repositories; Durchschnittsscore 49.0; 99 mit Python-Anteil ab 60 %; 86 nutzen MLX, Metal, Core ML oder Foundation Models.

## Verteilung der Grades

| Grade | Repos |
|---|---|
| Apple-first | 10 |
| teilweise | 70 |
| vernachlässigt | 170 |
| fremdgeführt | 50 |
| ohne Code | 22 |

## Top 10 schlechteste Scores

| Rang | Repo | Score | Grade | Python % | Anti-Muster |
|---|---|---|---|---|---|
| 1 | cognee | 5 | fremdgeführt | 97 | docker_lokal=13, ml_cpu=1, subprocess_lastig=21, numpy_ohne_mlx=6, modellzugang_http=1 |
| 2 | rllm | 5 | fremdgeführt | 91 | docker_lokal=1, ml_cpu=8, numpy_ohne_mlx=18 |
| 3 | aider | 5 | fremdgeführt | 91 | docker_lokal=7, bash_gross=1, numpy_ohne_mlx=4, modellzugang_http=1 |
| 4 | pydantic-ai | 10 | fremdgeführt | 100 | docker_lokal=3, ml_cpu=1, bash_gross=2, numpy_ohne_mlx=1 |
| 5 | instructor | 15 | fremdgeführt | 100 | docker_lokal=1, numpy_ohne_mlx=1 |
| 6 | deepseek-coder | 15 | fremdgeführt | 100 | ml_cpu=9, numpy_ohne_mlx=10 |
| 7 | swe-bench | 15 | fremdgeführt | 99 | ml_cpu=3, numpy_ohne_mlx=2 |
| 8 | dspy | 15 | fremdgeführt | 99 | ml_cpu=1, numpy_ohne_mlx=6 |
| 9 | amrlib | 15 | fremdgeführt | 99 | ml_cpu=19, numpy_ohne_mlx=9 |
| 10 | stanza | 15 | fremdgeführt | 98 | ml_cpu=128, numpy_ohne_mlx=43 |

## Alle Repos

| Repo | Score | Grade | Python % | Frameworks | Unified Memory | Anti-Muster | Erste Lücke |
|---|---|---|---|---|---|---|---|
| adg_testbench | 30 | fremdgeführt | 100 | - | 0 | - | applefirst-python-schwer |
| AETHEL | 60 | teilweise | 0 | - | 2 | docker_lokal=2 | applefirst-docker-lokal |
| aethel-apple | - | ohne Code | 0 | - | 1 | - | - |
| aethel-build-orchestrator | 60 | teilweise | 0 | - | 0 | - | - |
| aethel-codegraph | 60 | teilweise | 0 | - | 0 | - | - |
| aethel-evolution | 60 | teilweise | 0 | - | 0 | - | applefirst-kein-silizium |
| aethel-evolutionCascade | 60 | teilweise | 0 | - | 0 | - | applefirst-kein-silizium |
| aethel-forensics | 50 | vernachlässigt | 0 | Keychain | 0 | sandbox_exec=1 | applefirst-sandbox-exec |
| aethel-forge | - | ohne Code | 0 | - | 0 | - | - |
| aethel-foundation | 70 | teilweise | 0 | - | 178 | - | applefirst-kein-silizium |
| aethel-launcher | 55 | vernachlässigt | 0 | - | 6 | bash_gross=4 | applefirst-kein-silizium |
| aethel-macos-work-surface | 60 | teilweise | 0 | - | 0 | - | - |
| aethel-omega | 45 | vernachlässigt | 0 | - | 1 | docker_lokal=2, bash_gross=2 | applefirst-docker-lokal |
| aethel-supervisor | 55 | vernachlässigt | 0 | - | 0 | launchd_ohne_smappservice=1 | applefirst-launchd-ohne-smappservice |
| aethel-systems | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel-test-orchestrator | 60 | teilweise | 0 | - | 0 | - | - |
| aethel-v6 | 100 | Apple-first | 1 | AppIntents, CoreML, Keychain, MLX | 170 | - | - |
| aethel-v6-omega | 90 | Apple-first | 1 | CoreML, Keychain, MLX | 168 | - | - |
| aethel-workspace | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel1 | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=30 | applefirst-python-schwer |
| aethel1 | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=30 | applefirst-python-schwer |
| aethel1 | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=30 | applefirst-python-schwer |
| aethel1 | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=30 | applefirst-python-schwer |
| aethel1 | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=30 | applefirst-python-schwer |
| aethel1 | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=30 | applefirst-python-schwer |
| aethel1 | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=30 | applefirst-python-schwer |
| aethel1 | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=30 | applefirst-python-schwer |
| aethel1 | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=30 | applefirst-python-schwer |
| aethel1 | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=30 | applefirst-python-schwer |
| aethel2 | 45 | vernachlässigt | 96 | Keychain, MLX | 536 | subprocess_lastig=60 | applefirst-python-schwer |
| aethel2 | 45 | vernachlässigt | 96 | Keychain, MLX | 536 | subprocess_lastig=60 | applefirst-python-schwer |
| aethel2 | 45 | vernachlässigt | 96 | Keychain, MLX | 536 | subprocess_lastig=60 | applefirst-python-schwer |
| aethel2 | 45 | vernachlässigt | 96 | Keychain, MLX | 536 | subprocess_lastig=60 | applefirst-python-schwer |
| aethel2 | 45 | vernachlässigt | 96 | Keychain, MLX | 536 | subprocess_lastig=60 | applefirst-python-schwer |
| aethel_architect | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_architect | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_ausbildung | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_ausbildung | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_bitplay | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_buerger | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_buerger | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_campus | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_campus | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_cockpit | 60 | teilweise | 0 | MLX | 0 | - | applefirst-kein-unified-memory |
| aethel_core | 50 | vernachlässigt | 0 | - | 0 | - | applefirst-kein-silizium |
| aethel_cowork_flutter | 30 | fremdgeführt | 87 | - | 0 | - | applefirst-python-schwer |
| aethel_cowork_flutter | 30 | fremdgeführt | 87 | - | 0 | - | applefirst-python-schwer |
| aethel_daktari | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_daktari | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_design | 60 | teilweise | 0 | - | 22 | - | applefirst-kein-silizium |
| aethel_didact | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_didact | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_grundgesetz | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_grundgesetz | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_handwerk | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_handwerk | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_harmonia | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_harmonia | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_heimat | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_heimat | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_justitia | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_justitia | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_konformitaet | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_konformitaet | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_lexikon | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_lexikon | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_lichthaus | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_lichthaus | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_logopaedie | 60 | teilweise | 0 | - | 0 | - | - |
| aethel_logopaedie | 60 | teilweise | 0 | - | 0 | - | - |
| aethel_memoria | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_muehle | 40 | vernachlässigt | 100 | - | 5 | - | applefirst-python-schwer |
| aethel_music_studio | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_music_studio | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_mwalimu | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_mwalimu | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_neno | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_newsroom | 45 | vernachlässigt | 64 | - | 12 | bash_gross=1 | applefirst-python-schwer |
| aethel_observatory | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_openclaw | 50 | vernachlässigt | 3 | - | 0 | - | - |
| aethel_orion | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_os | - | ohne Code | 0 | - | 0 | - | - |
| aethel_pharma | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_polis | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_product_shells | 50 | vernachlässigt | 0 | - | 0 | - | applefirst-kein-silizium |
| aethel_python | 30 | fremdgeführt | 100 | - | 0 | - | applefirst-python-schwer |
| aethel_pythonclone | - | ohne Code | 0 | - | 0 | - | - |
| aethel_quantor | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_rag_workbench | 70 | teilweise | 22 | MLX | 7 | - | - |
| aethel_reader | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_sandbox | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_secure_messenger | 50 | vernachlässigt | 10 | - | 0 | - | - |
| aethel_sermon_archive | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_shamba | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_shield | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_stammbaum | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_studio | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_uhuru | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_unified | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_vintage_radio | 50 | vernachlässigt | 0 | - | 0 | - | applefirst-kein-silizium |
| aethel_voice | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_wachturm | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_webbrowser_complex | 50 | vernachlässigt | 2 | - | 0 | - | - |
| aethel_worship | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethel_xray | 60 | teilweise | 9 | - | 2 | - | - |
| aethel_zertifikat | 50 | vernachlässigt | 0 | - | 0 | - | - |
| aethelAgent | 70 | teilweise | 0 | - | 4 | - | applefirst-kein-silizium |
| aethelAgent | 70 | teilweise | 0 | - | 4 | - | applefirst-kein-silizium |
| aethelAgentFactory | 70 | teilweise | 0 | - | 7 | - | applefirst-kein-silizium |
| aethelAgentFactory | 70 | teilweise | 0 | - | 7 | - | applefirst-kein-silizium |
| aethelAgentRuntime | 80 | Apple-first | 4 | CoreML, Keychain, MLX | 477 | bash_gross=17, launchd_ohne_smappservice=3 | applefirst-launchd-ohne-smappservice |
| aethelAnalytics | 30 | fremdgeführt | 100 | - | 0 | - | applefirst-python-schwer |
| aethelappstore | 50 | vernachlässigt | 0 | - | 0 | - | applefirst-kein-silizium |
| aethelBot | 65 | teilweise | 0 | - | 45 | launchd_ohne_smappservice=6 | applefirst-launchd-ohne-smappservice |
| aethelBrowser | 75 | teilweise | 2 | Accelerate, CoreML, FoundationModels, Keychain, MLX, Metal, Network, OSLog, Vision | 1778 | bash_gross=1 | - |
| aethelBrowser-build | 75 | teilweise | 2 | Accelerate, CoreML, FoundationModels, Keychain, MLX, Metal, Network, OSLog, Vision | 1775 | bash_gross=1 | - |
| aethelCLIGames | - | ohne Code | 0 | - | 0 | - | - |
| aethelCodeAlphaClean | 50 | vernachlässigt | 64 | - | 0 | - | applefirst-python-schwer |
| aethelCodeAnalyzer | 70 | teilweise | 0 | - | 7 | - | - |
| aethelContainer | 55 | vernachlässigt | 0 | Keychain | 2 | sandbox_exec=2, launchd_ohne_smappservice=1 | applefirst-sandbox-exec |
| aethelCoWork | 20 | fremdgeführt | 68 | - | 0 | docker_lokal=1, bash_gross=1, modellzugang_http=1 | applefirst-python-schwer |
| aethelCoWork | 20 | fremdgeführt | 68 | - | 0 | docker_lokal=2, bash_gross=1, modellzugang_http=1 | applefirst-python-schwer |
| aethelDeepLearning | 45 | vernachlässigt | 98 | Keychain, MLX | 1057 | subprocess_lastig=120 | applefirst-python-schwer |
| aethelDesktopLean1 | 70 | teilweise | 0 | - | 19 | - | - |
| aethelDesktopResearch | 45 | vernachlässigt | 96 | Keychain, MLX | 305 | subprocess_lastig=30 | applefirst-python-schwer |
| aethelEditor | - | ohne Code | 0 | - | 6 | - | - |
| aethelema | 60 | teilweise | 0 | - | 0 | - | applefirst-kein-silizium |
| aethelema | 50 | vernachlässigt | 1 | Keychain, Network | 283 | sandbox_exec=1, bash_gross=3, modellzugang_http=1 | applefirst-sandbox-exec |
| aethelFactory | 40 | vernachlässigt | 100 | - | 34 | - | applefirst-python-schwer |
| aethelFamilyAppStore | 55 | vernachlässigt | 41 | Keychain | 58 | bash_gross=1 | - |
| aethelGemini | 70 | teilweise | 5 | Accelerate, CoreML, Keychain, MLX | 501 | docker_lokal=2 | applefirst-docker-lokal |
| aethelGemini-project | 75 | teilweise | 3 | Accelerate, CoreML, Keychain, MLX, Metal, Vision | 1617 | docker_lokal=2, bash_gross=7 | applefirst-docker-lokal |
| aethelHall | - | ohne Code | 0 | - | 24 | - | - |
| aethelHealthLab | 60 | teilweise | 0 | SwiftConcurrency | 0 | - | - |
| aethelHelix | 75 | teilweise | 23 | Metal | 76 | subprocess_lastig=23 | - |
| aethelIntegrationProvisorisch | 60 | teilweise | 0 | - | 0 | - | - |
| aethelLanding | 35 | fremdgeführt | 96 | - | 29 | modellzugang_http=1 | applefirst-python-schwer |
| aethellm | 70 | teilweise | 5 | MLX, Metal | 19 | - | - |
| aethelLocalCoder | 45 | vernachlässigt | 93 | CoreML, MLX | 53 | subprocess_lastig=20 | applefirst-python-schwer |
| aethelMacUIAgent | 80 | Apple-first | 4 | MLX, Vision | 14 | - | - |
| aethelMessanger | 60 | teilweise | 0 | - | 0 | - | applefirst-kein-silizium |
| aethelMistral | 90 | Apple-first | 1 | CoreML, MLX, Metal | 371 | - | - |
| aethelOmegaLM | 50 | vernachlässigt | 100 | MLX | 107 | - | applefirst-python-schwer |
| aethelOmegaM0 | 50 | vernachlässigt | 84 | MLX | 1417 | - | applefirst-python-schwer |
| aethelProjects | 50 | vernachlässigt | 100 | Accelerate, CoreAI, CoreML, FoundationModels, Keychain, MLX, Network, OSLog, XPC | 162 | docker_lokal=3, sandbox_exec=2 | applefirst-python-schwer |
| aethelPromtEngineerung | 80 | Apple-first | 0 | MLX | 4 | - | - |
| aethelPromtEngineerung | 80 | Apple-first | 0 | MLX | 4 | - | - |
| aethelreasoningcomputer | 60 | teilweise | 1 | FoundationModels, Keychain | 1 | docker_lokal=2 | applefirst-docker-lokal |
| aethelScripts | 25 | fremdgeführt | 90 | CoreAI, CoreML, FoundationModels, Keychain, MLX, Metal | 3489 | docker_lokal=2, sandbox_exec=4, subprocess_lastig=440, bash_gross=3, launchd_ohne_smappservice=8 | applefirst-python-schwer |
| aethelScripts-clean | 30 | fremdgeführt | 99 | MLX | 76 | sandbox_exec=1, subprocess_lastig=35, launchd_ohne_smappservice=7 | applefirst-python-schwer |
| aethelSGML | 60 | teilweise | 0 | - | 0 | - | applefirst-kein-silizium |
| aethelSystemObservation | 60 | teilweise | 0 | - | 0 | - | applefirst-kein-silizium |
| aethelTerminal | 65 | teilweise | 0 | Network, SwiftConcurrency | 1 | bash_gross=1 | - |
| aethelVoiceControl | 60 | teilweise | 0 | Network, SwiftConcurrency | 0 | - | - |
| aethelZLAMA | 55 | vernachlässigt | 38 | Keychain | 1 | bash_gross=4 | - |
| ai-fastlane-governance | 30 | fremdgeführt | 100 | - | 0 | - | applefirst-python-schwer |
| aider | 5 | fremdgeführt | 91 | - | 0 | docker_lokal=7, bash_gross=1, numpy_ohne_mlx=4, modellzugang_http=1 | applefirst-python-schwer |
| aider_desktop_grok | 50 | vernachlässigt | 59 | CoreML, MLX | 972 | docker_lokal=1, subprocess_lastig=154, bash_gross=6 | applefirst-docker-lokal |
| aiderDesktop | 75 | teilweise | 1 | CoreML, Keychain, MLX, Metal | 1856 | sandbox_exec=11, bash_gross=10 | applefirst-sandbox-exec |
| aiderDesktop_memristor_v1 | 60 | teilweise | 0 | - | 0 | - | - |
| aiderDesktopCursor | 25 | fremdgeführt | 100 | - | 0 | modellzugang_http=2 | applefirst-python-schwer |
| aiderDesktopGrok | 30 | fremdgeführt | 85 | CoreML, MLX | 930 | docker_lokal=1, subprocess_lastig=102, bash_gross=6 | applefirst-python-schwer |
| aiderDesktopLogos | 70 | teilweise | 0 | - | 20 | - | applefirst-kein-silizium |
| amrlib | 15 | fremdgeführt | 99 | - | 0 | ml_cpu=19, numpy_ohne_mlx=9 | applefirst-python-schwer |
| Athelix | 60 | teilweise | 6 | - | 42 | docker_lokal=2 | applefirst-docker-lokal |
| autogen | 25 | fremdgeführt | 74 | - | 0 | docker_lokal=1, bash_gross=1 | applefirst-python-schwer |
| BIblePublishProject | 50 | vernachlässigt | 0 | - | 0 | - | applefirst-kein-silizium |
| bit_encodings | 70 | teilweise | 0 | - | 7 | - | applefirst-kein-silizium |
| bitplay | 70 | teilweise | 0 | FoundationModels | 12 | - | - |
| bitplay_agents | 50 | vernachlässigt | 0 | - | 0 | - | - |
| bitplay_cli | 50 | vernachlässigt | 0 | - | 0 | - | applefirst-kein-silizium |
| bitplay_core | 50 | vernachlässigt | 0 | - | 0 | - | applefirst-kein-silizium |
| bitplay_lab_flutter | 70 | teilweise | 0 | FoundationModels | 53 | - | - |
| bitplay_lab_flutter-orginal | 65 | teilweise | 0 | CoreML, FoundationModels | 31 | numpy_ohne_mlx=1 | - |
| bitplay_lab_original | 40 | vernachlässigt | 2 | - | 28 | docker_lokal=3, bash_gross=1, numpy_ohne_mlx=6 | applefirst-docker-lokal |
| bitplay_labs | 50 | vernachlässigt | 0 | - | 0 | - | - |
| bitplay_sip | 50 | vernachlässigt | 0 | - | 0 | - | - |
| bitplay_visualizers | 50 | vernachlässigt | 0 | - | 0 | - | applefirst-kein-silizium |
| bitplay_widgets | 50 | vernachlässigt | 0 | - | 0 | - | - |
| blocks_3d | 40 | vernachlässigt | 0 | - | 0 | docker_lokal=2 | applefirst-docker-lokal |
| bsc | 45 | vernachlässigt | 4 | - | 1 | docker_lokal=6, bash_gross=2 | applefirst-docker-lokal |
| byztxt | 30 | fremdgeführt | 100 | - | 0 | - | applefirst-python-schwer |
| cash_pilot | 50 | vernachlässigt | 0 | - | 0 | - | - |
| claude-code-proxy | 40 | vernachlässigt | 99 | MLX | 1 | docker_lokal=2 | applefirst-python-schwer |
| click_test_project | 30 | fremdgeführt | 100 | - | 0 | - | applefirst-python-schwer |
| cline | 60 | teilweise | 1 | - | 9 | - | applefirst-kein-silizium |
| cn | 45 | vernachlässigt | 0 | - | 2 | docker_lokal=3, bash_gross=1 | applefirst-docker-lokal |
| cognee | 5 | fremdgeführt | 97 | - | 1 | docker_lokal=13, ml_cpu=1, subprocess_lastig=21, numpy_ohne_mlx=6, modellzugang_http=1 | applefirst-python-schwer |
| ComfyUI | 25 | fremdgeführt | 100 | - | 2 | ml_cpu=289, numpy_ohne_mlx=54 | applefirst-python-schwer |
| crewai | 40 | vernachlässigt | 100 | - | 30 | - | applefirst-python-schwer |
| crush | 50 | vernachlässigt | 0 | - | 0 | - | - |
| deepseek-coder | 15 | fremdgeführt | 100 | - | 0 | ml_cpu=9, numpy_ohne_mlx=10 | applefirst-python-schwer |
| digitalSoftwareFactory | 30 | fremdgeführt | 98 | - | 153 | docker_lokal=3 | applefirst-python-schwer |
| dotfiles | 60 | teilweise | 61 | MLX | 11 | - | applefirst-python-schwer |
| ds4 | 65 | teilweise | 5 | Keychain, Metal | 62 | bash_gross=2 | - |
| dspy | 15 | fremdgeführt | 99 | - | 0 | ml_cpu=1, numpy_ohne_mlx=6 | applefirst-python-schwer |
| faith_metrics | 50 | vernachlässigt | 0 | - | 0 | - | applefirst-kein-silizium |
| fimas | 80 | Apple-first | 0 | FoundationModels, SwiftConcurrency, SwiftTesting, Virtualization | 568 | - | - |
| fjord_race | 50 | vernachlässigt | 1 | - | 0 | - | applefirst-kein-silizium |
| flutter | - | ohne Code | 0 | - | 0 | - | - |
| flutter_ui_showcase | 50 | vernachlässigt | 0 | - | 0 | - | - |
| goose | 60 | teilweise | 7 | Keychain, MLX | 7 | docker_lokal=5, bash_gross=9, electron=1 | applefirst-docker-lokal |
| gptme | 20 | fremdgeführt | 90 | - | 1 | docker_lokal=17, subprocess_lastig=149, numpy_ohne_mlx=4 | applefirst-python-schwer |
| GrokAethelBench | 60 | teilweise | 0 | - | 0 | - | applefirst-kein-silizium |
| guidance | 15 | fremdgeführt | 96 | - | 0 | ml_cpu=3, numpy_ohne_mlx=10 | applefirst-python-schwer |
| helloscout | 50 | vernachlässigt | 0 | - | 0 | - | - |
| helloscout | 50 | vernachlässigt | 0 | - | 0 | - | - |
| heritage_bible | - | ohne Code | 0 | - | 0 | - | - |
| heritage_bible_aethel | 60 | teilweise | 4 | - | 0 | - | - |
| heritage_bible_aethelNuru | 60 | teilweise | 0 | - | 3 | - | - |
| heritage_bible_engine | 60 | teilweise | 0 | - | 0 | - | - |
| heritage_bible_flutter | 50 | vernachlässigt | 0 | - | 0 | - | - |
| heritage_bible_flutter_perichoresis_refactor | - | ohne Code | 0 | - | 0 | - | - |
| hydra_forge | 50 | vernachlässigt | 100 | MLX | 21 | - | applefirst-python-schwer |
| impact_lens | 50 | vernachlässigt | 0 | - | 0 | - | - |
| instructor | 15 | fremdgeführt | 100 | - | 0 | docker_lokal=1, numpy_ohne_mlx=1 | applefirst-python-schwer |
| intelizign_consulting | - | ohne Code | 0 | - | 0 | - | - |
| interpreter | 40 | vernachlässigt | 4 | Keychain, OSLog | 1 | docker_lokal=2, sandbox_exec=5, subprocess_lastig=21, bash_gross=1 | applefirst-docker-lokal |
| kgu-sgml-pipeline | 50 | vernachlässigt | 0 | - | 0 | - | applefirst-kein-silizium |
| kgu-sgml-pipeline | 50 | vernachlässigt | 0 | - | 0 | - | applefirst-kein-silizium |
| kinder_guard | 50 | vernachlässigt | 0 | - | 0 | - | - |
| kss-tools | 20 | fremdgeführt | 100 | - | 0 | ml_cpu=1 | applefirst-python-schwer |
| kss-tools | 20 | fremdgeführt | 100 | - | 0 | ml_cpu=1 | applefirst-python-schwer |
| langgraph | 25 | fremdgeführt | 100 | - | 1 | docker_lokal=9, numpy_ohne_mlx=1 | applefirst-python-schwer |
| lector_os | 50 | vernachlässigt | 0 | - | 0 | - | applefirst-kein-silizium |
| letta | - | ohne Code | 0 | - | 0 | - | - |
| letta-code | 25 | fremdgeführt | 0 | Keychain | 0 | docker_lokal=1, sandbox_exec=6, modellzugang_http=1 | applefirst-docker-lokal |
| llm | 35 | fremdgeführt | 100 | - | 2 | numpy_ohne_mlx=1 | applefirst-python-schwer |
| logos | 75 | teilweise | 0 | MLX | 47 | bash_gross=2 | - |
| macos_study_plattform | 55 | vernachlässigt | 0 | - | 2 | bash_gross=1 | applefirst-kein-silizium |
| manuel-jsx-snippets | 50 | vernachlässigt | 0 | - | 0 | - | applefirst-kein-silizium |
| manuel-jsx-snippets | 50 | vernachlässigt | 0 | - | 0 | - | applefirst-kein-silizium |
| ManuelCrypto | - | ohne Code | 0 | - | 0 | - | - |
| ManuelCrypto | - | ohne Code | 0 | - | 0 | - | - |
| manuelcrypto-maven | - | ohne Code | 0 | - | 0 | - | - |
| manuelcrypto-maven | - | ohne Code | 0 | - | 0 | - | - |
| memoristorCursor | 80 | Apple-first | 0 | Metal | 28 | - | - |
| metropolitan_developer | 60 | teilweise | 0 | MLX | 0 | - | applefirst-kein-unified-memory |
| metropolitan_developer_impeller | 50 | vernachlässigt | 0 | - | 0 | - | applefirst-kein-silizium |
| metropolitan_impeller | 50 | vernachlässigt | 0 | - | 0 | - | - |
| mini-swe-agent | 30 | fremdgeführt | 100 | - | 0 | - | applefirst-python-schwer |
| mods | - | ohne Code | 0 | - | 0 | - | - |
| mymessanger | 50 | vernachlässigt | 0 | - | 0 | - | - |
| neon-pulse-survivors | 50 | vernachlässigt | 0 | - | 0 | - | applefirst-kein-silizium |
| newsfeed_engine | 60 | teilweise | 0 | - | 0 | - | applefirst-kein-silizium |
| nius-linux | 50 | vernachlässigt | 0 | - | 0 | - | - |
| omega-system | 70 | teilweise | 0 | - | 3 | - | - |
| omega_bridge | 50 | vernachlässigt | 0 | - | 0 | - | - |
| omega_domain | 70 | teilweise | 14 | MLX | 15 | - | - |
| omega_ui | 50 | vernachlässigt | 0 | - | 0 | - | - |
| opencode | 45 | vernachlässigt | 0 | - | 22 | docker_lokal=7, electron=1 | applefirst-docker-lokal |
| openhands | 35 | fremdgeführt | 0 | - | 2 | docker_lokal=3, bash_gross=1, electron=1, modellzugang_http=1 | applefirst-docker-lokal |
| osxQ | 45 | vernachlässigt | 83 | MLX | 328 | bash_gross=4 | applefirst-python-schwer |
| osxq-pennylane | 50 | vernachlässigt | 93 | MLX | 11 | - | applefirst-python-schwer |
| outlines | 40 | vernachlässigt | 100 | MLX | 53 | ml_cpu=6 | applefirst-python-schwer |
| photon-defense | 60 | teilweise | 0 | - | 0 | - | applefirst-kein-silizium |
| photon-plm | 40 | vernachlässigt | 0 | - | 0 | docker_lokal=2 | applefirst-docker-lokal |
| photon_radio | 40 | vernachlässigt | 0 | - | 0 | docker_lokal=5 | applefirst-docker-lokal |
| pragmaticAethelDesktop | 75 | teilweise | 1 | CoreML, MLX | 1287 | bash_gross=5 | - |
| promptfoo | 20 | fremdgeführt | 2 | Keychain | 0 | docker_lokal=2, ml_cpu=1, numpy_ohne_mlx=1, modellzugang_http=7 | applefirst-docker-lokal |
| pydantic-ai | 10 | fremdgeführt | 100 | - | 6 | docker_lokal=3, ml_cpu=1, bash_gross=2, numpy_ohne_mlx=1 | applefirst-python-schwer |
| python_backend | 40 | vernachlässigt | 64 | CoreML, MLX | 557 | docker_lokal=1, subprocess_lastig=149, bash_gross=3 | applefirst-python-schwer |
| r2e-gym | 20 | fremdgeführt | 86 | - | 0 | bash_gross=2, numpy_ohne_mlx=1 | applefirst-python-schwer |
| ragFileSystemChatGpt5 | 70 | teilweise | 0 | MLX | 0 | - | applefirst-kein-unified-memory |
| rasa | 25 | fremdgeführt | 99 | Metal | 4 | docker_lokal=13, ml_cpu=23, numpy_ohne_mlx=64 | applefirst-python-schwer |
| rllm | 5 | fremdgeführt | 91 | - | 0 | docker_lokal=1, ml_cpu=8, numpy_ohne_mlx=18 | applefirst-python-schwer |
| run-cli-task-aethel_aider-aider-mlx | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=28 | applefirst-python-schwer |
| run-cli-task-aethel_coder-aider-mlx | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=28 | applefirst-python-schwer |
| run-cli-task-aider_omega-aider-mlx | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=28 | applefirst-python-schwer |
| run-cli-task-claude_code_omega-aider-mlx | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=28 | applefirst-python-schwer |
| run-task-challenge-quick-001-aethel_aider-aider-mlx | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=28 | applefirst-python-schwer |
| run-task-challenge-quick-001-aethel_aider-aider-mlx | 45 | vernachlässigt | 98 | Keychain, MLX | 1055 | subprocess_lastig=120 | applefirst-python-schwer |
| run-task-challenge-quick-001-aethel_coder-aider-mlx | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=28 | applefirst-python-schwer |
| run-task-challenge-quick-001-aethel_coder-aider-mlx | 45 | vernachlässigt | 98 | Keychain, MLX | 1055 | subprocess_lastig=120 | applefirst-python-schwer |
| run-task-challenge-quick-001-aider_omega-aider-mlx | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=28 | applefirst-python-schwer |
| run-task-challenge-quick-001-aider_omega-aider-mlx | 45 | vernachlässigt | 98 | Keychain, MLX | 1055 | subprocess_lastig=120 | applefirst-python-schwer |
| run-task-challenge-quick-001-claude_code_omega-aider-mlx | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=28 | applefirst-python-schwer |
| run-task-challenge-quick-001-claude_code_omega-aider-mlx | 45 | vernachlässigt | 98 | Keychain, MLX | 1055 | subprocess_lastig=120 | applefirst-python-schwer |
| run-task-rust-substrate-001-aethel_aider-aider-mlx | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=29 | applefirst-python-schwer |
| run-task-rust-substrate-001-aethel_coder-aider-mlx | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=29 | applefirst-python-schwer |
| run-task-rust-substrate-001-aider_omega-aider-mlx | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=29 | applefirst-python-schwer |
| run-task-rust-substrate-001-claude_code_omega-aider-mlx | 45 | vernachlässigt | 93 | Keychain, MLX | 279 | subprocess_lastig=29 | applefirst-python-schwer |
| SafeNest | 80 | Apple-first | 0 | CoreML, Keychain, Network, SwiftConcurrency, SwiftTesting, Vision | 0 | - | applefirst-kein-unified-memory |
| scrollmapper | 30 | fremdgeführt | 100 | - | 0 | - | applefirst-python-schwer |
| semgrep | 40 | vernachlässigt | 49 | Accelerate, SwiftConcurrency | 1 | docker_lokal=99, bash_gross=1, numpy_ohne_mlx=1 | applefirst-docker-lokal |
| sgpt | 20 | fremdgeführt | 99 | - | 0 | docker_lokal=2 | applefirst-python-schwer |
| smolagents | 40 | vernachlässigt | 100 | MLX | 1 | ml_cpu=5 | applefirst-python-schwer |
| snips-nlu | 25 | fremdgeführt | 100 | - | 0 | numpy_ohne_mlx=7 | applefirst-python-schwer |
| space_radio | 60 | teilweise | 8 | MLX | 469 | ml_cpu=1 | applefirst-ml-cpu |
| spacy | 15 | fremdgeführt | 95 | - | 1 | docker_lokal=1, ml_cpu=1, numpy_ohne_mlx=45 | applefirst-python-schwer |
| stanza | 15 | fremdgeführt | 98 | - | 0 | ml_cpu=128, numpy_ohne_mlx=43 | applefirst-python-schwer |
| StartUp | 50 | vernachlässigt | 44 | - | 83 | bash_gross=1, launchd_ohne_smappservice=1 | applefirst-kein-silizium |
| SuperDuperMarkt | - | ohne Code | 0 | - | 0 | - | - |
| SuperDuperMarktBrockhaus | - | ohne Code | 0 | - | 0 | - | - |
| swarm | 20 | fremdgeführt | 100 | - | 0 | docker_lokal=2 | applefirst-python-schwer |
| swe-agent | 25 | fremdgeführt | 97 | - | 0 | numpy_ohne_mlx=2 | applefirst-python-schwer |
| swe-bench | 15 | fremdgeführt | 99 | - | 0 | ml_cpu=3, numpy_ohne_mlx=2 | applefirst-python-schwer |
| swt-test | - | ohne Code | 0 | - | 0 | - | - |
| syrnt | 30 | fremdgeführt | 100 | - | 0 | - | applefirst-python-schwer |
| tau | 40 | vernachlässigt | 99 | - | 3 | - | applefirst-python-schwer |
| testProject1 | 40 | vernachlässigt | 100 | - | 9 | - | applefirst-python-schwer |
| testprojekt1 | 30 | fremdgeführt | 100 | - | 0 | - | applefirst-python-schwer |
| TestSWT | - | ohne Code | 0 | - | 0 | - | - |
| TestSWT | - | ohne Code | 0 | - | 0 | - | - |
| TestXCode | 60 | teilweise | 0 | - | 0 | - | - |
| TestXCode | 60 | teilweise | 0 | - | 0 | - | - |
| tree-sitter | 60 | teilweise | 0 | - | 1 | docker_lokal=1 | applefirst-docker-lokal |
| universitas | 50 | vernachlässigt | 0 | Keychain | 0 | - | - |
| vintage_language_lab | 60 | teilweise | 0 | - | 1 | - | - |
| vintage_media_center | 50 | vernachlässigt | 0 | - | 0 | - | - |
| vintage_radio | 60 | teilweise | 2 | Accelerate, CoreML, FoundationModels, Keychain, MLX, Metal, Network, OSLog, SwiftConcurrency | 1285 | docker_lokal=1, subprocess_lastig=20, bash_gross=8 | applefirst-docker-lokal |
| vintage_radio_aethel | 50 | vernachlässigt | 0 | - | 0 | - | applefirst-kein-silizium |
| vintage_radio_harness | 50 | vernachlässigt | 0 | - | 0 | - | - |
| vintage_Radio_newUI | 60 | teilweise | 0 | Accelerate, MLX | 52 | ml_cpu=1 | applefirst-ml-cpu |
| vintage_tv | 75 | teilweise | 0 | Accelerate, CoreML, Metal | 104 | numpy_ohne_mlx=1 | - |
| website_aethel_systems | 50 | vernachlässigt | 0 | - | 0 | - | - |
| weltformel | 50 | vernachlässigt | 0 | - | 0 | - | - |
| werkstatt | 30 | fremdgeführt | 100 | - | 0 | - | applefirst-python-schwer |
| workspace-manifest | 50 | vernachlässigt | 33 | - | 44 | bash_gross=2, modellzugang_http=3 | applefirst-modellzugang-nur-http |
| youtube_reader | 60 | teilweise | 24 | AppIntents, FoundationModels | 27 | docker_lokal=8, bash_gross=2, numpy_ohne_mlx=6 | applefirst-docker-lokal |
| youtubereader-python | 30 | fremdgeführt | 100 | - | 0 | - | applefirst-python-schwer |
| youtubereader_flutter | 65 | teilweise | 29 | AppIntents, FoundationModels, Keychain | 34 | docker_lokal=9, subprocess_lastig=39, bash_gross=4, numpy_ohne_mlx=10 | applefirst-docker-lokal |

