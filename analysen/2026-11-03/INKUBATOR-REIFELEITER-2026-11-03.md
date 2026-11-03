# Inkubator-Reifeleiter

Nur lesend. Eine Stufe gilt, wenn alle ihre Signale erfüllt und alle vorigen Stufen erreicht sind.

## Verteilung

| Stufe | Name | Anzahl |
|---|---|---:|
| R0 | Idee | 94 |
| R1 | Skizze | 9 |
| R2 | Prototyp | 171 |
| R3 | Spezifiziert | 32 |
| R4 | Getestet | 6 |
| R5 | Integriert | 4 |
| R6 | Dokumentiert | 1 |
| R7 | Gesichert | 2 |
| R8 | Versioniert | 0 |
| R9 | Plattformreif | 1 |
| R10 | Vertriebsreif | 0 |
| R11 | Betrieb | 0 |
| RF | Reproduzierbar | 0 |
| RI | Vertrag | 0 |
| - | Keine Stufe | 2 |

## Repos (322)

| Repo | Klasse | Stufe | nächste Stufe | nächste Lücken |
|---|---|---|---|---|
| aethelBrowser | produkt | R9 Plattformreif | R10 Vertriebsreif | CHANGELOG.md ohne datierten Versionsabschnitt und kein docs/RELEASE*.md |
| aethelAgentRuntime | infrastruktur | R7 Gesichert | R8 Versioniert | CHANGELOG.md ohne Versionsabschnitt (erwartet z. B. „## [1.0.0] - 2026-10-20“) |
| heritage_bible_aethelNuru | inhalt | R7 Gesichert | R8 Versioniert | CHANGELOG.md ohne Versionsabschnitt (erwartet z. B. „## [1.0.0] - 2026-10-20“) |
| aethelBrowser-build | produkt | R6 Dokumentiert | R7 Gesichert | Abhängigkeits-Lock fehlt: package-lock.json (zu package.json) |
| aethel-omega | produkt | R5 Integriert | R6 Dokumentiert | docs/ARCHITECTURE.md oder docs/DESIGN.md fehlt |
| aethelProjects | produkt | R5 Integriert | R6 Dokumentiert | CHANGELOG.md (oder CHANGES.md) fehlt; Lizenzdatei (LICENSE) fehlt |
| aethelScripts | produkt | R5 Integriert | R6 Dokumentiert | docs/ARCHITECTURE.md oder docs/DESIGN.md fehlt |
| aiderDesktopGrok | produkt | R5 Integriert | R6 Dokumentiert | docs/ARCHITECTURE.md oder docs/DESIGN.md fehlt |
| aethelSGML | produkt | R4 Getestet | R5 Integriert | keine CI-Konfiguration (.github/workflows/*.yml, .gitlab-ci.yml, Makefile mit test-Ziel, local-ci.sh); keine CI-Datei, daher kein Testkommando |
| aethelTerminal | produkt | R4 Getestet | R5 Integriert | kein Testkommando (pytest, cargo test, swift test, flutter test, npm test, dart test) in den CI-Dateien |
| aethel_daktari | produkt | R4 Getestet | R5 Integriert | kein Testkommando (pytest, cargo test, swift test, flutter test, npm test, dart test) in den CI-Dateien |
| aethel_didact | produkt | R4 Getestet | R5 Integriert | kein Testkommando (pytest, cargo test, swift test, flutter test, npm test, dart test) in den CI-Dateien |
| aethel_logopaedie | produkt | R4 Getestet | R5 Integriert | kein Testkommando (pytest, cargo test, swift test, flutter test, npm test, dart test) in den CI-Dateien |
| aethel_product_shells | produkt | R4 Getestet | R5 Integriert | keine CI-Konfiguration (.github/workflows/*.yml, .gitlab-ci.yml, Makefile mit test-Ziel, local-ci.sh); keine CI-Datei, daher kein Testkommando |
| aethelCodeAlphaClean | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_architect | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_ausbildung | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_bitplay | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_buerger | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_campus | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_design | produkt | R3 Spezifiziert | R4 Getestet | 1 Testdateien, Anteil 4 % an 25 Quelldateien (< 5 Dateien und < 10 %) |
| aethel_grundgesetz | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_handwerk | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_harmonia | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_heimat | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_justitia | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_konformitaet | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_lexikon | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_lichthaus | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_memoria | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_mwalimu | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_neno | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_observatory | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_orion | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_pharma | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_quantor | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_reader | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_sandbox | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_shamba | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_shield | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_stammbaum | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_uhuru | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_wachturm | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_worship | inhalt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| aethel_zertifikat | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| workspace-manifest | produkt | R3 Spezifiziert | R4 Getestet | keine Testdateien (tests/, test/, *_test.*, test_*.*, *Tests.swift, *_test.dart) |
| AETHEL | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| Athelix | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| BIblePublishProject | inhalt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| ComfyUI | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| GrokAethelBench | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| SafeNest | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel-apple | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel-build-orchestrator | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel-codegraph | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel-evolution | infrastruktur | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel-evolutionCascade | infrastruktur | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel-forensics | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel-foundation | infrastruktur | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel-macos-work-surface | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel-supervisor | infrastruktur | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel-systems | infrastruktur | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel-test-orchestrator | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel-v6 | forschung | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel-v6-omega | forschung | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel1 | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel1 | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel1 | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel1 | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel1 | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel1 | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel1 | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel1 | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel1 | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel1 | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel2 | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel2 | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel2 | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel2 | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel2 | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelAgent | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelAgent | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelAgentFactory | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelAgentFactory | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelAnalytics | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelBot | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelCoWork | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelCoWork | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelCodeAnalyzer | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelContainer | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelDeepLearning | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelDesktopLean1 | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelDesktopResearch | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelFactory | produkt | R2 Prototyp | R3 Spezifiziert | docs/TEST-CASES.md fehlt |
| aethelFamilyAppStore | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelHealthLab | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelHelix | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelIntegrationProvisorisch | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelLanding | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelLocalCoder | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelMacUIAgent | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelMessanger | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelMistral | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelOmegaLM | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelOmegaM0 | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelPromtEngineerung | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelPromtEngineerung | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelScripts-clean | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelSystemObservation | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelVoiceControl | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelZLAMA | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel_cowork_flutter | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel_cowork_flutter | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel_newsroom | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel_python | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel_rag_workbench | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel_vintage_radio | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel_voice | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelappstore | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelema | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethelema | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethellm | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| ai-fastlane-governance | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aider | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aiderDesktop | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aiderDesktopLogos | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aider_desktop_grok | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| amrlib | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| autogen | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| bitplay | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| bitplay_lab_flutter | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| bitplay_lab_flutter-orginal | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| bitplay_lab_original | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| bitplay_visualizers | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| bsc | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| byztxt | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| claude-code-proxy | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| click_test_project | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| cline | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| cn | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| cognee | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| crewai | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| crush | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| deepseek-coder | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| digitalSoftwareFactory | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| dotfiles | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| ds4 | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| dspy | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| fimas | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| fjord_race | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| goose | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| gptme | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| guidance | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| hydra_forge | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| instructor | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| intelizign_consulting | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| interpreter | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| langgraph | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| letta-code | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| logos | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| memoristorCursor | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| metropolitan_developer_impeller | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| metropolitan_impeller | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| mini-swe-agent | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| mods | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| neon-pulse-survivors | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| omega_bridge | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| omega_domain | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| omega_ui | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| opencode | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| openhands | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| osxQ | forschung | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| photon-plm | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| photon_radio | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| pragmaticAethelDesktop | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| promptfoo | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| pydantic-ai | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| python_backend | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| r2e-gym | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| ragFileSystemChatGpt5 | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| rasa | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| rllm | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| run-cli-task-aethel_aider-aider-mlx | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| run-cli-task-aethel_coder-aider-mlx | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| run-cli-task-aider_omega-aider-mlx | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| run-cli-task-claude_code_omega-aider-mlx | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| run-task-challenge-quick-001-aethel_aider-aider-mlx | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| run-task-challenge-quick-001-aethel_aider-aider-mlx | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| run-task-challenge-quick-001-aethel_coder-aider-mlx | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| run-task-challenge-quick-001-aethel_coder-aider-mlx | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| run-task-challenge-quick-001-aider_omega-aider-mlx | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| run-task-challenge-quick-001-aider_omega-aider-mlx | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| run-task-challenge-quick-001-claude_code_omega-aider-mlx | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| run-task-challenge-quick-001-claude_code_omega-aider-mlx | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| run-task-rust-substrate-001-aethel_aider-aider-mlx | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| run-task-rust-substrate-001-aethel_coder-aider-mlx | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| run-task-rust-substrate-001-aider_omega-aider-mlx | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| run-task-rust-substrate-001-claude_code_omega-aider-mlx | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| scrollmapper | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| semgrep | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| sgpt | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| snips-nlu | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| space_radio | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| spacy | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| stanza | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| swarm | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| swe-agent | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| swe-bench | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| syrnt | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| tau | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| universitas | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| vintage_radio | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| vintage_radio_harness | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| website_aethel_systems | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| youtube_reader | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| youtubereader-python | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| youtubereader_flutter | produkt | R2 Prototyp | R3 Spezifiziert | docs/SPEC.md fehlt; docs/TEST-CASES.md fehlt; SPEC fehlt, daher keine REQ-/SHALL-Zeilen prüfbar |
| aethel-launcher | produkt | R1 Skizze | R2 Prototyp | 0 LOC in 0 Quelldateien (< 200) |
| aethelEditor | produkt | R1 Skizze | R2 Prototyp | 0 LOC in 0 Quelldateien (< 200) |
| aethelHall | produkt | R1 Skizze | R2 Prototyp | 0 LOC in 0 Quelldateien (< 200) |
| aethel_polis | produkt | R1 Skizze | R2 Prototyp | 86 LOC in 2 Quelldateien (< 200) |
| letta | produkt | R1 Skizze | R2 Prototyp | 0 LOC in 0 Quelldateien (< 200) |
| llm | produkt | R1 Skizze | R2 Prototyp | 3 von 22 Quelldateien mit Stub-Marker (> 10 %) |
| osxq-pennylane | forschung | R1 Skizze | R2 Prototyp | 1 von 6 Quelldateien mit Stub-Marker (> 10 %) |
| outlines | produkt | R1 Skizze | R2 Prototyp | 21 von 65 Quelldateien mit Stub-Marker (> 10 %) |
| smolagents | produkt | R1 Skizze | R2 Prototyp | 7 von 50 Quelldateien mit Stub-Marker (> 10 %) |
| ManuelCrypto | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| ManuelCrypto | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| StartUp | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| SuperDuperMarkt | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| SuperDuperMarktBrockhaus | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| TestSWT | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| TestSWT | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| TestXCode | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| TestXCode | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| adg_testbench | produkt | R0 Idee | R1 Skizze | README.md hat nur 7 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| aethel-forge | infrastruktur | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| aethel-workspace | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| aethelGemini | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| aethelGemini-project | produkt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| aethel_architect | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| aethel_ausbildung | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| aethel_buerger | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| aethel_campus | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| aethel_cockpit | produkt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| aethel_core | infrastruktur | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| aethel_daktari | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| aethel_didact | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| aethel_grundgesetz | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| aethel_handwerk | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| aethel_harmonia | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| aethel_heimat | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| aethel_justitia | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| aethel_konformitaet | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| aethel_lexikon | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| aethel_lichthaus | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| aethel_logopaedie | produkt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| aethel_muehle | produkt | R0 Idee | R1 Skizze | README.md hat nur 16 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| aethel_music_studio | produkt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| aethel_music_studio | produkt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| aethel_mwalimu | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| aethel_openclaw | produkt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| aethel_os | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| aethel_pythonclone | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| aethel_secure_messenger | produkt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| aethel_sermon_archive | inhalt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| aethel_studio | produkt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| aethel_unified | produkt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| aethel_webbrowser_complex | produkt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| aethel_xray | produkt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| aethelreasoningcomputer | forschung | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| aiderDesktop_memristor_v1 | produkt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| bit_encodings | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| bitplay_agents | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| bitplay_cli | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| bitplay_core | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| bitplay_labs | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| bitplay_sip | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| bitplay_widgets | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| blocks_3d | produkt | R0 Idee | R1 Skizze | README.md hat nur 10 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| cash_pilot | produkt | R0 Idee | R1 Skizze | README.md hat nur 10 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| faith_metrics | produkt | R0 Idee | R1 Skizze | README.md hat nur 10 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| flutter | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| flutter_ui_showcase | produkt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| helloscout | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| helloscout | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| heritage_bible | inhalt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| heritage_bible_aethel | inhalt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| heritage_bible_engine | inhalt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| heritage_bible_flutter | inhalt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| heritage_bible_flutter_perichoresis_refactor | inhalt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| impact_lens | produkt | R0 Idee | R1 Skizze | README.md hat nur 10 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| kgu-sgml-pipeline | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| kgu-sgml-pipeline | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| kinder_guard | produkt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| kss-tools | produkt | R0 Idee | R1 Skizze | README.md hat nur 6 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| kss-tools | produkt | R0 Idee | R1 Skizze | README.md hat nur 6 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| lector_os | produkt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| macos_study_plattform | produkt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| manuel-jsx-snippets | produkt | R0 Idee | R1 Skizze | README.md hat nur 7 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| manuel-jsx-snippets | produkt | R0 Idee | R1 Skizze | README.md hat nur 7 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| manuelcrypto-maven | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| manuelcrypto-maven | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| metropolitan_developer | produkt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| mymessanger | produkt | R0 Idee | R1 Skizze | README.md hat nur 10 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| newsfeed_engine | produkt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| nius-linux | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| omega-system | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| photon-defense | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| swt-test | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| testProject1 | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| testprojekt1 | produkt | R0 Idee | R1 Skizze | weder README (≥ 20 Inhaltszeilen) noch docs/SPEC.md vorhanden |
| tree-sitter | produkt | R0 Idee | R1 Skizze | README.md hat nur 16 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| vintage_Radio_newUI | produkt | R0 Idee | R1 Skizze | README.md hat nur 15 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| vintage_language_lab | produkt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| vintage_media_center | produkt | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| vintage_radio_aethel | produkt | R0 Idee | R1 Skizze | README.md hat nur 15 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| vintage_tv | produkt | R0 Idee | R1 Skizze | README.md hat nur 17 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| weltformel | forschung | R0 Idee | R1 Skizze | README.md hat nur 11 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| werkstatt | produkt | R0 Idee | R1 Skizze | README.md hat nur 9 Inhaltszeilen (< 20) und docs/SPEC.md fehlt |
| aethelCLIGames | produkt | - Keine Stufe | R0 Idee | kein Commit im Repository |
| aiderDesktopCursor | produkt | - Keine Stufe | R0 Idee | kein Commit im Repository |
