# Gesamtanalyse des Workspace ~/workspace – Projekte, Erfassung, Fabrik, Lücken, Stand der Technik

Stand: 03.11.2026. Rein lesend erhoben (git log/status lokal, Dateisystem, launchctl list, pytest in aethelProjects). Kein fetch, push, gh, Modellaufruf. Zahlen aus dem Live-Dateisystem heute, ergänzt um den aethelProjects-Scan vom 23.10.2026 (`aethelProjects/reports/2026-10-23/`), wo eine Zahl älter ist, steht das Datum dabei.

Ziel laut Manuel: alle Projekte automatisiert steuern; digitale Fabrik zum Coden; digitale Firma; künftig kybernetische Steuerung mit mehreren Regelkreisen (Firma → Projekte → Fabrik → AIX/Copilot → zurück). Dieser Bericht ist Analyse, kein Plan und keine neue Autorität.

---

## 0. Kurzfazit (zehn Sätze)

1. Der Workspace hat heute 330 Einträge direkt unter `~/workspace`: 211 echte Git-Repos, 88 Worktrees, 31 Verzeichnisse ohne Git. Dedupliziert sind es 321 lesbare Git-Historien (Scan 23.10.), rund 200 davon sind eigene Produkte oder Komponenten.
2. Es gibt **fünf Register**, die alle etwas anderes wissen und nicht gegeneinander abgeglichen werden: `workspace-manifest/projects.yaml` (198 Einträge, Stand 29.08.), der aethelProjects-Scan (321 Historien, 23.10.), 330 `.aix/project-profile.json`, `~/.aix/auftraege/auftraege.jsonl` (494 Zeilen) und die GitHub-Org AETHEL-Omega. Keines ist Software-Autorität, alle sind Dateien.
3. Das Manifest ist zwei Monate alt: 15 echte Repos fehlen, darunter die aktuellen Fabrik-Organe aethelBot, aethelLanding, aethelProjects, aethelHelix, aethelAnalytics; 73 Worktrees fehlen; 2 Einträge zeigen ins Leere; 125 von 198 Einträgen tragen noch das Massen-Import-Datum 09.06.
4. aethelProjects ist das reifste Portfolio-Werkzeug (118 Tests grün, Score 100), aber ein **Python-Sammler ohne Consumer**: kein PM-Repo, kein MCP-Tool, kein `~/bin`-Eintrag, kein Aufruf aus aethelScripts. Es ruft aethelCodeAnalyzer als Subprozess auf, der Vertrag ist einseitig und nur gegen eine Attrappe getestet.
5. aethelCodeAnalyzer ist das Vertragsvorbild (capability.json + aix_contract.rs, 200 Tests), kann aber nur Rust und Dart in der Tiefe; Python, TS, JS bekommen Zeilenlänge und TODO, Swift fehlt ganz. Das Binary im Worktree ist älter als `main`, die Versionsangaben widersprechen sich (0.12.0 vs 0.1.0).
6. Die Fabrik existiert **zweimal und unverbunden**: die ältere Schicht workspace-manifest/factory mit RFC 0001/0002 (Juni) und die neuere Schicht aethelScripts mit `_aix_factory_*`, Rollen-Jobs, Worklane-Stub, auftraege.jsonl. Nur die zweite läuft (31 launchd-Prozesse), aber als Skript-Flotte, nicht als Komponentenlaufzeit.
7. Die Firmen-Schicht (Portfolio-Entscheidung, Intake/Backlog, Angebot, Abrechnung, Support, Nutzung, Gesamtkosten) ist **nur Dokument** (RFC 0002: „~40 % einer Firma“, Portfolio ❌, Intake ❌). Es gibt kein Repo, das die Firma als Software führt.
8. Reifegrad des Portfolios (Scan 23.10., Skala 0–100): 64 Historien bei 0–19 (Skizze), 75 bei 20–39, 169 bei 40–59, 11 bei 60–79, 2 bei 100. Nur 47 haben eine SPEC, 29 eine ARCHITECTURE, 3 ein DESIGN, 2 eine DNA. 254 Historien gelten als stale (> 90 Tage), 106 Repos haben als letzten Commit den Importtag 09.06.
9. Technologisch ist der Kanon vom 07.09./14.10./30.10. (Rust-Kern mit Zustand in SQLite, Swift-Laufzeit über XPC, Foundation Models, Containerization, aethelema als Cockpit, Verträge mit beidseitigem Test) **beschlossen, aber nicht gelandet**: 0 von 7 Vertragsgrenzen beidseitig getestet, kein `aixd`, kein Swift-Dienst, Foundation Models in keinem AIX-Pfad, `sandbox-exec` weiterhin in Gebrauch, 1.006 Dateien in `aethelScripts/bin`, 478 Koordinationsdokumente als Gedächtnis.
10. Für eine kybernetische Steuerung fehlen die drei Dinge, die jeder Regelkreis braucht: ein **Messwert in Software** (statt Markdown-Berichten), ein **Sollwert je Projekt** (Zweck, Besitzer, Zielzustand, Budget) und ein **Stellglied mit Rückmeldung** (Auftrag → Ausführung → Receipt → Zustandsänderung in einer Datenbank). Heute sind alle drei Teile vorhanden, aber jeweils in einem anderen Werkzeug und ohne Rückkopplung.

---

## 1. Inventar in Zahlen

| Größe | Wert | Quelle |
|---|---:|---|
| Einträge direkt unter ~/workspace | 330 | ls, heute |
| davon echte Git-Repos (`.git` Verzeichnis) | 211 | heute |
| davon Worktrees (`.git` Datei) | 88 | heute |
| davon ohne Git | 31 | heute |
| Unterschiedliche lesbare Git-Historien (dedupliziert, rekursiv) | 321 | Scan 23.10. |
| Worktree-Checkouts dazu | 218 | Scan 23.10. |
| Commits gesamt / auf main / nicht auf main | 44.582 / 31.821 / 12.761 | Scan 23.10. |
| Branches | 3.384 | Scan 23.10. |
| Dirty Checkouts | 229 (Scan) · heute fast jedes Repo ≥ 1 Datei dirty, lector_os 33.256 | Scan / heute |
| Stale (> 90 Tage) | 254 | Scan 23.10. |
| Repos mit letztem Commit 09.06.2026 (Importtag) | 106 von 211 | heute |
| Ohne main / ohne Remote | 9 / 4 | Scan 23.10. |
| Größte Brocken | _archive 20 GB, ComfyUI 20 GB, _universitas_sicherung 2,3 GB, GrokAethelBench 1,4 GB, SafeNest 1,1 GB | du |
| Technologie-Marker (Repos) | 94 Cargo.toml · 123 pubspec.yaml · 37 pyproject · 5 package.json · 2 Package.swift · 265 mit GitHub-Workflows · 16 rust-toolchain-Pins · 1 flake.nix | heute |
| Steuerungs-Doku-Marker | 226 CLAUDE.md · 117 AGENTS.md · 77 docs/SPEC.md · 2 .aethel/engineering.yaml · 2 dna/genome.yaml · 330 .aix/project-profile.json · 0 capability.json in Repo-Wurzeln (1 in aethelCodeAnalyzer/capabilities/) | heute |
| Apple-Plattform-Nutzung | SwiftUI in 14 Repos · XCTest 45 · Swift Testing 20 · FoundationModels nur aethelBrowser-Brücke + fimas · AppIntents nur in aethelBrowser/aethelema-Shells · OSLog aus Rust: 0 | grep heute |
| aethelScripts | Branch `docs/aix-umbau-rust-swift-flutter`, 99 dirty, 2.369 Commits, 1.006 Dateien in bin/ (457 `_aix_*.py`), 13 Crates, 478 Koordinationsdokumente, 1.067 Testeinträge | heute |
| launchd (aethel/aix/ollama/mlx/litellm) | 38 Einträge, 31 mit PID, 14 Rollen-Jobs, 3 mit letztem Exit −15 | launchctl heute |

---

## 2. Welche Projekte wir haben (Gruppierung aller 211 Repos)

Gruppen aus Manifest-Kategorie, README-Intent und Aktivität. „aktiv“ = Commit nach 01.10.2026. Alles andere ruht seit Juni/Juli.

### 2.1 Kern, Steuerung, Fabrik (28)
| Repo | Rolle | Stand |
|---|---|---|
| aethelScripts | AIX Engineering Runtime: Gate, Solve, Aufträge, Rollen, Copilot, Leitstand | aktiv, Hauptbaustelle, Branch ≠ main |
| aethelAgentRuntime | Agent-Laufzeit (VM-Isolation, Receipts) | aktiv (22.10.), 1.796 Commits |
| aethelContainer | Prozess-Hypervisor (Rust+Dart, SQLite-Registry, REST/MCP) | ruht seit 22.07., Daemon Exit 78 |
| aethelLanding | Kandidat, Siegel, Verdict, Ledger, Landeweg | aktiv (21.10.), Branch `land/kandidaten-1021`, nicht installiert |
| aethelBot | Messenger-Steuerung des M4/M5 (Rust) | aktiv (15.10.), läuft als launchd |
| aethelLocalCoder | lokales Coding-Cockpit, Jobs, Modellwahl | aktiv (02.11.), Release 2026.11.02.2 installiert |
| aethelCodeAnalyzer (Worktree von aethelCodeAnalyzer_git) | statische Analyse Rust/Dart, AIX-Vertrag | aktiv (22.10.), 200 Tests |
| aethelProjects | Portfolio-Forensik, Dossiers, PM-Input | aktiv (23.10.), Branch `codex/...`, 118 Tests |
| workspace-manifest | Registry projects.yaml, factory-CLI, scorecard, RFC 0001/0002 | ruht seit 21.08. |
| aethelFactory | Worklane-Spezifikation (1.459 Zeilen), kein src | ruht seit 21.08. |
| aethel-omega | Wissens-Rückgrat (TS-Monorepo, 18 Pakete, MCP) | ruht seit 07.10. |
| aethelAnalytics | Analytik (Schnitt 1) | aktiv (28.10.), Feature-Branch |
| aethelOmegaM0 / aethelOmegaLM | Mikro-Kern-Experimente / LM | 13.10. / 25.09. |
| aethelAgent / aethelAgentFactory | Rust-Planer, CoWork-Adapter / Agentenfabrik | ruhen seit 09.06. |
| aethel-supervisor | Out-of-band-Beobachter für aiderDesktop | ruht |
| aethel-build-orchestrator / aethel-test-orchestrator | zentrale Build-/Test-Orchestrierung (je 1 Commit) | Stubs |
| aethel-launcher | generischer Launcher + JSON-Registry | 15.06., als Stub erkannt |
| digitalSoftwareFactory | MES-Idee aus RFC 0001 | 09.06., ersetzt laut Manifest |
| aethel-forge / aethel-workspace / aethel_os / aethel_pythonclone | nur `chore/fastlane-governance`, je 3 Commits | leere Hüllen |
| ai-fastlane-governance | CI-Governance (Risk-Klassen) | 09.06., in 265 Workflows referenziert |
| aethelMacUIAgent / aethel-macos-work-surface | Mac-UI-Effektor / Plan≠Aktion-Grenze | 14.10. / 09.06. |
| aethel-codegraph | SCIP-Graph + Embeddings | 29.06. |
| claude-code-proxy | Proxy | 15.08. |
| hydra_forge | LangGraph-Coder (Mock) | 17.06. |
| aethelCoWork / aethel_cowork_flutter / aethelTerminal / aethelEditor | Arbeitsflächen | Juni–Okt |
| Ohne Git: aethel_core_orchestrator, aethelControlhubMacBookPro, aetherDesktop, agentRuntime, aethel-dependency-scanner, aethel-executor-probe, AIX-dist | Altlasten/Entwürfe | – |

### 2.2 Coding-Agenten, Modelle, Benchmarks (20)
aiderDesktop (1.758 Commits, 03.10.), aiderDesktopGrok (502, Agentenbranch), aiderDesktopCursor (kein HEAD), aiderDesktopLogos, aiderDesktop_memristor_v1, pragmaticAethelDesktop (997, 26 dirty), aethelGemini, aethelGemini-project (490), aethelMistral (14.10.), aethelZLAMA, aethellm, aethelDeepLearning (23.09.) plus 4 `run-task-*`-Klone davon, GrokAethelBench, aethelPromtEngineerung, aethel_rag_workbench, ragFileSystemChatGpt5, memoristorCursor, aethelreasoningcomputer, logos (124 Commits).

### 2.3 Produkte und Apps (ca. 55)
- **Kommunikation/Browser:** aethelBrowser (5.413 Commits, 31.10.) + aethelBrowser-build, aethelema (1.088, 31.10.) + aethelMessanger (gleicher Remote), mymessanger, aethel_secure_messenger.
- **Medien:** vintage_radio (1.272, 22.10.), vintage_tv, vintage_Radio_newUI, vintage_language_lab, vintage_media_center, vintage_radio_aethel, vintage_radio_harness, space_radio, photon_radio, aethel_music_studio, youtubereader_flutter (189, 23.10.), youtube_reader, youtubereader-python, newsfeed_engine, aethel_newsroom (15.10.).
- **Bibel/Heritage:** heritage_bible_aethelNuru (1.440, 13.10.), heritage_bible, heritage_bible_aethel, heritage_bible_engine, heritage_bible_flutter, heritage_bible_flutter_perichoresis_refactor, BIblePublishProject, aethel_sermon_archive, faith_metrics, universitas (03.10.).
- **Bitplay/Spiele:** bitplay, bitplay_core, bitplay_lab_flutter (184, 23.10.), bitplay_lab_flutter-orginal, bitplay_lab_original, bitplay_agents, bitplay_cli, bitplay_labs, bitplay_sip, bitplay_visualizers, bitplay_widgets, blocks_3d (03.10.), fjord_race, aethelCLIGames, bit_encodings.
- **Sonstige Apps:** aethelFamilyAppStore (22.10., eigener GitHub-Runner läuft), aethelHelix (31.10., Forschung/Geometrie), aethelHealthLab, aethelVoiceControl, aethelSGML, kgu-sgml-pipeline, SafeNest (Swift, 1,1 GB), metropolitan_developer (+_impeller, metropolitan_impeller), cash_pilot, kinder_guard, impact_lens, macos_study_plattform, aethelDesktopResearch, aethelSystemObservation, aethel-forensics, aethel_muehle, aethelHall (Stub), website_aethel_systems, aethel-systems (Next.js).

### 2.4 aethel_core-Produktlinie (38)
aethel_core (7 Dart-Dateien, 1.540 LOC), aethel_design (3.226 LOC), aethel_product_shells (8.080 LOC, 16 Tests), aethel-foundation (869 LOC) und **34 Varianten** (aethel_architect, _ausbildung, _bitplay, _buerger, _campus, _cockpit, _daktari, _didact, _grundgesetz, _handwerk, _harmonia, _heimat, _justitia, _konformitaet, _lexikon, _lichthaus, _logopaedie, _memoria, _mwalimu, _neno, _observatory, _openclaw, _orion, _pharma, _polis, _quantor, _reader, _sandbox, _shamba, _shield, _stammbaum, _studio, _uhuru, _unified, _voice, _wachturm, _webbrowser_complex, _worship, _xray, _zertifikat). Typisch: **2 Dart-Dateien, 78 LOC, 9 Commits, 6 dirty, letzter Commit 28.06.** 35 Varianten hängen per pubspec an aethel_core, 13 aethel_*-Repos nicht.

### 2.5 Forschung/Theorie (14)
AETHEL (Rust, 62 MB), aethel-v6 (156 Commits, 48 dirty, Codex-Branch), aethel-evolution + aethel-evolutionCascade (gleicher Remote), Athelix (218 MB, Apple-27-Branch), aethel-apple, omega-system, omega_bridge, omega_domain, omega_ui, weltformel, osxq-pennylane, photon-defense, photon-plm, aethelHelix (auch Produkt).

### 2.6 Fremdcode/Forks (5)
ComfyUI (20 GB), bsc, ds4, flutter (nur Governance-Branch), osxQ.

### 2.7 Scratch, Lernen, Tests (ca. 25)
testProject1, TestSWT, TestXCode, StartUp, helloscout, adg_testbench, SuperDuperMarkt(+Brockhaus), ManuelCrypto, manuelcrypto-maven, manuel-jsx-snippets, flutter_ui_showcase, aethel_python, intelizign_consulting, nius-linux, kss-tools, dotfiles, aethelIntegrationProvisorisch, aethelCodeAlphaClean, fimas, lector_os (33.256 dirty Dateien = generierter Baum), 4× run-task-challenge-*.

### 2.8 Worktree-Zoo (88) und Nicht-Git (31)
aethelema-* (26), aethelBrowser-* (14), aethelLanding-* (9), aiderDesktop-* (11), aethelScripts-* (9), aethelAgentRuntime-* (8), alc-*, cockpit-*, glm-*, bp-lf-views, vr-perf u. a. Das sind Arbeitsstränge laufender oder vergangener Agentenläufe; ob sie noch gebraucht werden, prüft niemand maschinell.

---

## 3. Wo die Projekte erfasst sind – und wo sie auseinanderlaufen

| Register | Ort | Umfang | Aktualität | Autorität | Lücke |
|---|---|---|---|---|---|
| projects.yaml | workspace-manifest | 198 Einträge, 14 Kategorien | 29.08. | keine (Datei, manuell kuratiert) | 15 Repos fehlen (aethel-test-orchestrator, aethelAnalytics, aethelBot, aethelEditor, aethelHall, aethelHealthLab, aethelHelix, aethelLanding, aethelOmegaLM, aethelOmegaM0, aethelProjects, aethel_muehle, aethel_newsroom, bsc, ds4); 73 Worktrees fehlen; aethel-v6-omega und aethelCodeAnalyzer zeigen ins Leere; 125 Einträge mit Importdatum; README nennt noch 199 Repos/11 Kategorien |
| Portfolio-Scan / Dossiers | aethelProjects/reports (gitignored) | 321 Historien, 321 PM-Dossiers | 23.10. | keine (Beobachtung) | keine Produkt-ID über Klone, kein Consumer, Berichte nur lokal |
| .aix/project-profile.json | in 330 Repos | Profil je Repo | gemischt | keine | 0 von 210 gelesenen Profilen mit Rollenbindung (Scan) |
| auftraege.jsonl | ~/.aix/auftraege | 494 Zeilen | 29.10. | faktische Auftragswahrheit | JSONL statt Transaktion; keine Zustandsmaschine; Lease-Semantik fehlt |
| GitHub-Org AETHEL-Omega | Remote | 172+ Repos (Stand Juni) | – | – | Topics/Projects-Board aus README nicht nachgewiesen; Drift lokal↔remote ungemessen (kein fetch) |
| CLAUDE.md / AGENTS.md | 226 / 117 Repos | Arbeitsregeln | gemischt | – | zwei Formate parallel; keine Prüfung, ob Regeln aktuell sind |
| 478 Koordinationsdokumente | aethelScripts/docs/coordination | Pläne, Akten | täglich | de facto Gedächtnis | nicht abfragbar, widersprechen sich zeitlich (Bauabgleich 23.10. belegt F0/Z1-Widerspruch) |

**Kernbefund:** Es gibt keinen Schlüssel „Produkt“, der Pfad, Git-Historie, Klone, Worktrees, Manifest-Eintrag, Auftrag und Rolle zusammenhält. 38 Repo-Namen kommen mehrfach vor (Scan). Jeder Konsument rät sich die Zuordnung selbst.

---

## 4. Wie aethelProjects mit aethelCodeAnalyzer zusammenarbeitet

### 4.1 Mechanik (belegt)
- `aethelProjects/src/aethel_projects/codeanalysis.py` sucht das Binary über `AETHEL_CODE_ANALYZER_BIN`, dann `~/workspace/aethelCodeAnalyzer/target/release/aethel_code_analyzer`, dann `~/bin/aethel-code-analyzer`.
- Aufruf je Repo: `<bin> --path <repo> --format aix`, `subprocess.run`, Timeout 120 s, nur für Repos mit Cargo.toml oder pubspec.yaml (`is_analysable`). Andere Repos werden als „nicht vollständig analysiert“ markiert, nicht verschwiegen.
- Schema wird geprüft (`aethel.code_analyzer.aix_findings.v1`), Felder `rule, severity, file, line, message, evidence_tier, repro, truncated` gelesen; Severity high→critical, med→warn, low→info. Finding-Code wird `code:<rule>`, Action = repro.
- CLI-Verb `code`; Tests TC-046–TC-050 laufen **gegen ein Shell-Skript als Attrappe**, nie gegen das echte Binary.
- Feldnamen stimmen mit `AixFinding`/`AixFindingsDocument` in `analyzer_core/src/lib.rs` überein (Quellvergleich, kein Test).

### 4.2 Brüche
1. **Einseitiger Vertrag.** Der Analyzer testet Producer-seitig (`tests/aix_contract.rs`, 339 Zeilen, eigene Rust-Structs). aethelProjects testet gegen eine selbstgeschriebene Attrappe. Eine gemeinsame Golden-Fixture oder ein Konsumententest im Analyzer-Repo existiert nicht; das Analyzer-Repo erwähnt aethelProjects nirgends. Damit ist genau das Vorbild-Muster (capability.json + beidseitiger Konsumententest) **zwischen diesen beiden nicht** umgesetzt.
2. **Stale-Binary-Falle.** Der Worktree-Build (22.10. 15:28) hat Vorrang vor dem installierten Release (`~/.local/share/aethel-code-analyzer/current`, Release 7e3e38c mit sha256). HEAD b2b0a6c ist jünger. `_analyzer_version` wird gelesen, aber nicht ausgewertet; kein SHA-/Versions-Gate.
3. **Versionschaos.** capability.json sagt 0.12.0, Cargo und `--version` sagen 0.1.0.
4. **Worktree als Abhängigkeit.** `~/workspace/aethelCodeAnalyzer` ist ein Linked Worktree (`.git`-Datei → aethelCodeAnalyzer_git). Ein `ls` schlug heute einmal fehl; das Manifest kennt nur den Namen ohne lokalen Treffer.
5. **Dead Code.** `READ_ONLY_FLAGS` wird nicht erzwungen; `--only-file`, `--mode`, `--profile` nie genutzt; `kind`, `scan`, `profile`, `files_skipped_unreadable` gehen verloren; `truncated`/`scan-truncated` werden als normale Findings durchgereicht, `analyzed` bleibt true.
6. **Drei Python-Konsumenten desselben Schemas:** `codeanalysis.py`, `aethelCodeAnalyzer/integrations/aix/aethel_analyzer.py` (strenger, prüft `tool == "aethel"`), Kopie `~/bin/_aix_aethel_analyzer.py`.
7. **Sprachlücke.** Volle Tiefe nur Rust/Dart. Python (aethelProjects selbst, 457 `_aix_*.py`, 14.974 Zeilen aethelLocalCoder), TypeScript (aethel-omega 341k Zeilen), Swift (SafeNest, Brücken, 14 SwiftUI-Repos) bleiben ohne Code-Sicht.
8. **Kein Standardformat.** `--format sarif` wird bewusst abgelehnt; kein tree-sitter, kein LSP, lexer-basiert („parser-free“). Dadurch keine Integration in Xcode, VS Code, GitHub Code Scanning.
9. **CI.** Beide Repos haben nur Fastlane-Governance-Workflows; kein sichtbarer `cargo test`/`clippy`/`pytest` in CI. Beide sind lokal-first.
10. **Doku hinkt.** `docs/ARCHITECTURE.md` in aethelProjects kennt `codeanalysis` nicht; `docs/INTEGRATION.md`, auf die README verweist, existiert nicht; `~/bin/aix-projects` aus der README existiert nicht.

### 4.3 Bewertung
Die Kopplung ist funktional (Subprozess, JSON, Schema-String), aber nicht das, was der Kanon vom 14.10. „Vertrag“ nennt. Sie ist ein Skript, das ein Binary findet. Für eine Fabrik müsste der Analyzer ein Dienst mit Fähigkeitsbeschreibung, Cache nach Baum-Hash und beidseitigem Vertragstest sein, und aethelProjects ein Konsument dieses Dienstes, nicht eines Pfads.

---

## 5. Fabrik- und Firmen-Organe: Dokument, Code, Betrieb

| Organ | Repo | Nur Dokument | Code ohne Betrieb | Läuft |
|---|---|:-:|:-:|:-:|
| Registry/Portfolio | workspace-manifest | | ✔ (Skripte, von Hand) | |
| Portfolio-Forensik | aethelProjects | | ✔ (kein Consumer) | |
| Code-Analyse | aethelCodeAnalyzer | | | ✔ (Binary installiert, Aufruf manuell) |
| Intake/Worklane | aethelFactory | ✔ (1.459 Z. Spec, kein src) | Stub `~/bin/worklane` 299 Z. | |
| Arbeitsvorbereitung | aethelScripts `_aix_factory_*` (5 Module, 02.11.) | | ✔ neu, Betrieb unbelegt | |
| Auftrags-/Rechteautorität | aethelScripts AIX, auftraege.jsonl | | | ✔ (als Skripte) |
| Rollen/Agentenflotte | aethelScripts + launchd (14 Rollen-Jobs, Agentenbrücken, Knoten) | | | ✔ |
| Ausführung | aethelLocalCoder, aethelAgentRuntime, aethelContainer | | aethelContainer tot (Exit 78) | ✔ LocalCoder, AgentRuntime |
| Isolation | aethelContainer (sandbox_exec), Containerization | ✔ Containerization | | ✔ sandbox-exec (veraltet) |
| Gate | aethelScripts Gate (Worktrees, 25 min) | | | ✔ |
| Kandidat/Siegel/Landung | aethelLanding | Landung (CAS) nur Spec | ✔ 2,5k Code, 3,7k Tests, nicht installiert | |
| Receipts/Evidenz | aethelBrowser-Brücken (HardwareRuntimeEvidence), aethelLanding (runner_pin, receipts geplant) | ✔ | ✔ Brücke in Flutter | |
| Wissen | aethel-omega, `_aix_wissen.py` | | ✔ omega ruht; Python-Prinzipien | MCP registriert |
| Leitstand/Cockpit | aix/leitstand (React), `_aix_uebersicht.py` (2.278 Z. HTML), aethelema-Reiter | ✔ aethelema-Reiter | ✔ React | ✔ HTML-Projektion |
| Fernsteuerung M4 | aethelBot | | | ✔ (Textbefehle, `Daten:` leer) |
| Inferenz | litellm :4000, ollama, mlx-proxy, Foundation Models | ✔ FM/aix-intel | | ✔ litellm/ollama/mlx |
| Firma: Portfolio-Entscheidung, Intake, Angebot, Abrechnung, Support, Nutzung | RFC 0002 | ✔ | | |
| Kosten-/Budgetwahrheit | `_aix_kostenleiter.py`, `_aix_factory_economy.py`, `unit-economics.py` | | ✔ drei Stellen | |
| Kontrollebene/Spine | RFC 0001 (`omega-ingestd`, claims→apply) | ✔ | | |

Doppelungen: 2 Fabriksysteme (manifest/factory vs. aethelScripts), 5 Registries (projects.yaml, aix-registry, coder-registry, _aix_modell_registry, _aix_mcp_registry), 4 Orchestratoren (digitalSoftwareFactory, aethel_core_orchestrator, orchestrate, factory-manager), 6 Cockpits/Launcher (aethel-launcher, aethelLocalCoder, aiderDesktop, factory-cockpit.sh, aix-dashboard, dashboard.py), 3 Kostenrechner, 3 Status-Wahrheiten (landing-Ledger, Gate-Logs, Rollen-Prüfer).

---

## 6. Lücken nach Achsen

### 6.1 Technologie-Abgleich (Kanon 07.09./14.10./30.10. vs. Ist)
| Kanon | Ist | Lücke |
|---|---|---|
| Rust besitzt Wahrheit/Zustand/Lease/Ledger/Gate (`aixd`) | 13 Crates existieren, `aix-ledger` hat SQLite+Migrationen, aber Wahrheit liegt in auftraege.jsonl, hosts.json, nacht-queue.tsv, Markdown | Kern ohne Autorität; `aixd` Schnitt 1 (Zustandstabelle/Übergangsvertrag) nicht gelandet |
| Swift „AETHEL Apple Runtime“ über XPC mit Receipts | Foundation-Models-Brücke und Evidenz-Brücke nur als Flutter-MethodChannel in aethelBrowser (156 + 395 Z.) | kein Swift-Paket, kein XPC, keine Signatur; von AIX ungenutzt |
| Foundation Models als Stufe 0 (Triage, Extraktion, kostenlos) | `/usr/bin/fm` vorhanden, `fm license` unbestätigt, 0 Aufrufe im AIX-Pfad | Stufe 0 fehlt; Triage läuft weiter über 30B-Modelle oder Cloud |
| Containerization statt sandbox-exec | `sandbox-exec` in aethelScripts (bin, crates, tests), aethelContainer, aiderDesktop; `container`-CLI nicht installiert | Gates unhermetisch, Cache nach Baum-Hash unmöglich |
| Verträge mit beidseitigem Konsumententest, Ablage `workspace-manifest/contracts/` | 1 capability.json im ganzen Workspace, `contracts/` nicht vorhanden | 0 von 7 Vertragsgrenzen gelandet |
| OSLog/Signposts/MetricKit statt Logdateien | 0 Rust-Crates mit oslog; `logs-1007/*.log` | nicht abfragbar, keine Prozess↔Ereignis-Korrelation |
| Keychain/Secure Enclave/Touch ID für Freigaben | Geheimnisse teils in Dateien (Akte 30.10.) | Freigaben als Chat-Text |
| App Intents für iPhone/Siri | nur in aethelBrowser/aethelema-Shells importiert, keine AIX-Intents | keine Aktionen vom Handy |
| aethelema als Cockpit (Flutter+frb) | React-Leitstand + HTML-Renderer | zweiter UI-Stack, kein Leitstand-Reiter |
| SwiftPM/Swift Testing/swift-subprocess | 2 Package.swift; Swift Testing in 20 Repos, XCTest 45; swift-subprocess 0 | Apple-Stack ist Minderheit |
| Hermetische Toolchain | `python3` zeigt auf 3.15 ohne PyYAML, Vertrag 3.14; 16 rust-toolchain-Pins von 94 Cargo-Repos; 1 flake.nix | PATH-Zufall (L16 der Akte 30.10.) |
| SQLite als Autorität je Host | aix-ledger (SQLite) existiert; aethelContainer hat SQLite-Registry; keine `.db` unter ~/.aix Wurzel | Transaktion vorhanden, aber nicht im Steuerpfad |

### 6.2 Patterns und Architekturmuster
- **Zustand in Dateien statt Zustandsmaschine:** JSONL, TSV, Markdown, Chat. Jede Lehre wird ein weiterer Wächter (14 Nachtläufer-Skripte, `melde-waechter`, `worker.sh`-Familie).
- **Skripte rufen Skripte:** 1.006 Dateien in bin/, kein Dienstprozess hält Leases/Heartbeats; nichts überlebt einen Kontextschnitt.
- **Projektion und Autorität vermischt:** Leitstand-Projektion (richtig), aber auch `Daten:`-Zeile des Bots als Maschinenkanal, der leer bleibt (L5).
- **Doppelte Konsumenten statt Vertrag:** drei Python-Leser desselben Analyzer-Schemas.
- **Plan ≠ Aktion** ist als Prinzip in aethel-macos-work-surface kodiert, aber im Steuerpfad nicht erzwungen (Agent schreibt direkt).
- **Keine Idempotenz-IDs:** identische Wiederholungsläufe (L4: dreimal derselbe A–I-Lauf) waren möglich, weil keine Aktions-ID im Zustand geführt wird.
- **Variant-Generator fehlt:** 34 Flutter-Varianten sind kopierte Shells; `new-aethel-variant.sh` und `upgrade-variants.sh` existieren im Manifest, aber die Varianten haben 78 LOC und wurden seit 28.06. nicht nachgezogen.
- **Hexagonale Struktur** nur in aethelProjects, aethelContainer (ac-domain/application/infra) und aethelLanding sauber; aethelScripts bleibt Monolith aus Skripten.

### 6.3 Reifegrad
- Verteilung (Scan 23.10., 321 Historien): Skizze 0–19: 64 · 20–39: 75 · 40–59: 169 · 60–79: 11 · 100: 2 (aethelProjects, workspace-manifest).
- Teilpunkte vorhanden: README 267 · CI 257 · tests 211 · SPEC 47 · ARCHITECTURE 29 · TEST-CASES 16 · DESIGN 3 · DNA 2 · engineering.yaml 2.
- **Messfehler des Scores:** Er misst Dateiexistenz und Inhaltszeilen, nicht Funktion. 257 Repos bekommen CI-Punkte für einen Fastlane-Governance-Workflow, der oft keinen Test ausführt. Eine 78-LOC-Variante mit Flutter-Standardtest erreicht 35 Punkte („Prototyp“). `scorecard.sh` (Bash) und `maturity.py` (Python) sind zwei Implementierungen derselben Gewichte; Drift nicht getestet.
- Fehlende Reife-Dimensionen: Release/Installierbarkeit, tatsächliche Nutzung, Betriebszustand (läuft/installiert), Sicherheitsaudit, Abhängigkeits-Aktualität, Gesamtkosten.

### 6.4 Stub-Erkennung
- Regel in `findings.py`: Stub nur wenn `branches ≤ 2`, `commits_not_on_main == 0`, `< 30 Quelldateien` und `< 50 LOC` (SOURCE_SUFFIXES). Ergebnis: **9 Stubs** (aethel-launcher, aethelHall, helloscout, kgu-sgml-pipeline, letta, ManuelCrypto, manuelcrypto-maven, swt-test, TestSWT).
- **Nicht erkannt:** die 34 aethel_core-Varianten (78 LOC Dart, aber Flutter-Plattformordner mit Swift/Kotlin/C++-Dateien zählen als Quelle; 2 Branches nach Import), die vier `chore/fastlane-governance`-Hüllen (aethel-forge, aethel-workspace, aethel_os, aethel_pythonclone, je 3 Commits), aethel-build-orchestrator und aethel-test-orchestrator (je 1 Commit), aethel-apple (6 Commits). Die LOC-Schwelle 50 ist zu niedrig, Plattform-Boilerplate wird nicht abgezogen, generierter Code (frb_generated, lector_os) nicht erkannt.
- `semantic-dedup.py` im Manifest und `detect_duplicates` in aethelProjects sind zwei Duplikat-Erkenner; letzterer liefert 147 Duplikat-Findings, davon die Mehrzahl durch 23 identische Scratch-Klone von aethelDeepLearning.
- Keine Erkennung von: leeren Templates mit Platzhaltern (`…`, `<…>`), Repos deren README einen anderen Zweck nennt als der Code, Klonen mit gleichem `git_common_dir`-Ursprung aber verschiedenem Remote.

### 6.5 Intents
- 318 von 321 haben einen Intent, aber: 260 aus README (medium), 30 aus Manifest-Kategorie (low: „aethel-forge — Kategorie core (Status active)“ ist kein Intent), 20 aus pubspec, nur 2 aus SPEC (high).
- README-Erstzeilen sind oft Badges („[![Build Status]…“ bei aethel-omega), Framework-Boilerplate („This is a Next.js project…“ bei aethel-systems) oder identisch über 23 Klone („Arbeitsrepo fuer das Projekt Summa Ω“).
- Kein Intent-Vergleich mit dem Code (semantischer Abgleich fehlt laut STATUS 23.10.), keine Prüfung Intent↔Manifest-Kategorie↔Besitzer↔Nutzer. Es fehlt ein Feld „Nutzerproblem/Zielgruppe/Besitzer“ (RFC 0002 nennt es als ❌).
- Ohne Foundation Models oder lokales Modell bleibt Intent-Extraktion Textheuristik; der Kanon sieht genau dafür Stufe 0 vor.

### 6.6 Dokumentation
- Zwei Regelwerke parallel (226 CLAUDE.md, 117 AGENTS.md), nicht gegeneinander geprüft; AGENTS.md in aethelScripts behauptet falsch, `python3` zeige auf 3.14 (L16).
- Status-Dokumente widersprechen dem Code: aethelLanding README „design stage, nothing lands code“ vs. CHANGELOG 0.0.12; aethelema PROJECT_STATUS.md Stand 08.05.; workspace-manifest STATUS.md „ALLES KOMPLETT“ (Dokumente, kein Betrieb); workspace-manifest README nennt 199 Repos/11 Kategorien; aethelProjects README verweist auf nicht existierende INTEGRATION.md und `~/bin/aix-projects`.
- 478 Koordinationsdokumente in aethelScripts, 100+ Analyse-/Spec-Dateien in `_docs` (AETHEL_COMPLETE_DESIGN_SPECIFICATION_..._DEEP_PART1–3): Wissen ohne Index, ohne Gültigkeitsdatum, ohne maschinenlesbaren Status.
- Nur 47 SPEC, 29 ARCHITECTURE, 3 DESIGN, 16 TEST-CASES im ganzen Portfolio; DNA/genome nur in 2 Repos.
- Keine ADR-Pflicht außer in workspace-manifest/docs/adr; Architekturentscheidungen stehen in Chat-Akten.

### 6.7 Zustand, Verträge, Tests, Betrieb
- **Zustand:** siehe 6.1; zusätzlich 345 geänderte Checkouts (Scan), 99 dirty in aethelScripts, 48 in aethel-v6: unklarer Besitz.
- **Branches:** Fabrik-Organe arbeiten nicht auf main: aethelScripts (`docs/aix-umbau-...`), aethelLanding (`land/kandidaten-1021`), aethelProjects (`codex/...`), aethelAnalytics (`feat/...`), aethelContainer (`feat/resource-limits-domain`), aethel-v6 (`codex/...`). 12.761 Commits nicht auf main.
- **Tests:** 211 Historien haben einen tests-Ordner, aber nur aethelProjects (118), aethelCodeAnalyzer (200+20), aethelLanding (18 Dateien), aethelLocalCoder (18 Dateien), aethelScripts (1.067 Einträge) sind substanzielle Suiten. Gate-Laufzeit 25 min, Timing-Tests falsch rot unter Last (L7).
- **CI:** 265 Repos mit Workflows, überwiegend derselbe Fastlane-Governance-Workflow; 823 Workflow-Dateien in Historien, 106 mit `schedule` (Kostenrisiko ungemessen).
- **Betrieb:** 38 launchd-Einträge, 3 mit letztem Exit −15, aethelContainer-Daemon Exit 78, `.plist.vor-*`-Backups als Altlast; kein Health-Vertrag, kein MetricKit, keine Service-Inventur in Software.
- **Sicherheit:** aethelema ohne unabhängiges Audit; Geheimnisse teils in Dateien; `sandbox-exec` veraltet; aethelAgentRuntime-Plan „Isolation Pflicht“ nicht für alle Ausführer durchgesetzt.
- **Kosten:** drei Kostenrechner, keine gemessene Gesamtkostenwahrheit je Auftrag (Fehlversuche, Gate-Minuten, Wartezeit); Speicherzulassung erst 30.10. sichtbar gemacht (L19).

---

## 7. Was nicht Stand der Technik ist (konkret, mit Gegenstück)

| Heute | Stand der Technik (bei uns verfügbar) |
|---|---|
| Portfolio-Register als YAML von Hand, 2 Monate alt | Register als Tabelle in SQLite mit Generator-Lauf per launchd, Drift als Ereignis |
| Reifegrad = Dateiexistenz | Reifegrad aus gemessenen Receipts: Build grün, Tests grün, installiert, genutzt, Abhängigkeiten aktuell |
| Intent aus README-Erstzeile | Intent als Pflichtfeld im Projektvertrag + Foundation-Models-Extraktion mit Konfidenz und Quelle |
| Code-Analyse als Subprozess mit Pfadsuche | Analyzer als Dienst (XPC/Unix-Socket) mit `DescribeCapabilities`, Cache nach Baum-Hash, SARIF |
| Analyse nur Rust/Dart, Lexer | tree-sitter/SCIP (aethel-codegraph existiert!) für Rust, Dart, Swift, Python, TS |
| Zustand in JSONL/TSV/Markdown | Rust-Enums + SQLite WAL, illegaler Übergang = Kompilierfehler |
| 1.006 bin-Skripte, Bash-Nachtläufer | `aixd` unter launchd mit KeepAlive, Leases mit Generation, Heartbeats |
| HTML alle 60 s neu gerendert, React-Leitstand | SwiftUI-Menüleiste + aethelema-Reiter über Dienstvertrag, Live-Abfragen |
| Logs in Dateien | OSLog Subsystem/Kategorie, OSLogStore, Signposts, MetricKit |
| sandbox-exec, 88 Worktrees als Ausführungsort | Containerization/Virtualization, gepinntes Image, Limits, Hash-Cache |
| Modelle nur über :4000 (Ollama/MLX) | Foundation Models Stufe 0 (kostenlos, on-device) für Triage/Extraktion/Klassifikation |
| Bot als Textparser, `Daten:` leer | typisierte Vertragsnachrichten über aethelema-Transport, Belege als Dateien mit Hash in Git |
| Freigaben als Chat-Text | App Intents + LocalAuthentication (Touch ID) |
| `python3` = PATH-Zufall | gepinnte Toolchain (uv/Nix), Vertrag erzwungen |
| 3 Duplikat-/Kosten-/Status-Rechner | je Begriff genau eine Komponente mit Vertrag |
| 34 kopierte Flutter-Shells | Variant-Generator aus aethel_core/design mit Vertragsversion |
| Fastlane-Workflow als „CI“ | CI, die `cargo test`, `clippy`, `pytest`, `flutter test` wirklich ausführt, mit Grün-Cache je Baum |
| Wissen in 478 Markdown-Akten | aethel-omega/Read-Model: typisierte, datierte Entscheidungen mit Provenienz (Kiraa-Prinzip) |

---

## 8. Kybernetische Steuerung: Soll-Kreisläufe und was fehlt

Ein Regelkreis braucht Sollwert, Messwert, Regler, Stellglied, Rückmeldung. Vier verschachtelte Kreise sind gemeint:

### K1 Firma (Wochen/Monate): Welche Produkte, mit welchem Ziel, Besitzer, Budget?
- Sollwert fehlt vollständig: kein Repo führt Nutzerproblem, Zielgruppe, Besitzer, Release-/Supportzustand, Budget je Produkt (RFC 0002 ❌).
- Messwert teilweise: aethelProjects liefert Git-/Reife-/Intent-Daten; Nutzung, Kosten, Rückmeldung fehlen.
- Regler/Stellglied fehlen: keine Portfolio-Entscheidung als Software (aktiv/pausiert/archiviert mit Begründung und Datum), kein Intake.
- **Lücke:** Produkt-ID als Schlüssel über Klone; Firmen-Ledger (SQLite) mit Entscheidungen; Nutzungs-/Kostenmessung.

### K2 Projekt (Tage): Ist das Projekt auf Kurs (Spec, Architektur, Reife, Abhängigkeiten, Sicherheit)?
- Sollwert: Engineering-Standard v2 (Dateien), aber kein Zielzustand je Projekt.
- Messwert: aethelProjects Scan + CodeAnalyzer (nur Rust/Dart), scorecard; Drift Manifest↔Realität wird gezählt, aber niemand konsumiert sie.
- Regler: Worklane (Spec, kein Code) sollte Dossier → Arbeitsauftrag machen.
- **Lücke:** Consumer des PM-Inputs; Worklane-Implementierung; Abhängigkeitsgraph Dart/Node/Python/Swift; Sicherheits- und Dependency-Scan (dependency-scanner ist leer); Pattern-Prüfung (Hexagonal, Vertrag, Zustand) als Regel.

### K3 Fabrik (Stunden): Auftrag → Ausführung → Kandidat → Gate → Landung → Receipt
- Vorhanden: auftraege.jsonl, Rollen-Flotte, aethelLocalCoder, Gate, aethelLanding (Kandidat/Siegel/Verdict), Copilot-Knoten.
- Fehlt: Landung als Compare-and-Swap-Verb; runner_pin/receipts; eine Installation = ein Auftrag (L17/L18: vier Pins mussten von Hand gleichgezogen werden); Lease/Generation als Fencing; Idempotenz-ID; Kapazitätsprüfung vor Lauf (L19); Grün-Cache je Baum; Container statt Worktree.
- **Lücke:** `aixd` Schnitt 1–6; Komponenten-Tor in aethelLanding (Policy gegen neue bin-Skripte); Receipt-Vertrag.

### K4 Lauf (Minuten): Einzelner Agentenlauf mit Modell, Werkzeug, Sandbox, Evidenz
- Vorhanden: aethelAgentRuntime (Receipts geplant), aethelLocalCoder (Datei-Beweis, Plan/Edit-Review), litellm-Routing.
- Fehlt: Foundation Models Stufe 0; hermetische Isolation; gemessene Gesamtkosten je Lauf; OSLog-Korrelation; Wiederholsperre bei identischem Befund (L4/L10 erst 30.10. beauftragt).

### Querschnitt: Rückkopplung zwischen den Kreisen
- K4→K3: Receipt → Zustandsübergang: existiert nur als Textbeleg/Chat (L2/L5).
- K3→K2: Landung → Projektreife/Dossier aktualisiert: nicht verbunden (aethelProjects liest nur Git).
- K2→K1: Dossier → Portfolio-Entscheidung: kein Consumer.
- K1→K3: Entscheidung → Auftrag mit Budget/Rolle: kein Intake; Aufträge entstehen im Chat.
- Copilot/AIX als Regler: Copilot-Knoten laufen, aber ihre Entscheidungen werden nicht als Übergänge in einer Zustandsmaschine festgehalten, sondern als Chat und JSONL.

---

## 9. Projekte, die fehlen (Vorschläge, je mit Komponente@Vertrag)

Jedes als Paket/Crate mit versioniertem Vertrag und beidseitigem Konsumententest; keine neuen bin-Skripte.

| # | Vorschlag | Komponente@Vertrag | Schließt |
|---|---|---|---|
| P1 | **aethelProjectManagement** (bisher nur als gewünschter Consumer genannt): Produkt-ID, Portfolio-Entscheidung (aktiv/pausiert/archiviert), Besitzer, Zielzustand, Budget; SQLite-Ledger, Flutter/SwiftUI-Sicht in aethelema | `aethel-pm@portfolio.v1`, konsumiert `aethel.projects.pm-input/v1` | K1, K2→K1 |
| P2 | **aixd** als eigenes Crate-Bündel in aethelScripts/crates oder eigenes Repo: Auftrag, Zustand, Lease/Generation, Receipts, Unix-Socket JSON-RPC | `aix-kernel@auftrag-zustand.v1`, `aix-ledger@receipt.v1` | K3 |
| P3 | **AETHEL Apple Runtime / aix-intel** (Swift-Paket aus den aethelBrowser-Brücken, XPC-Dienst, Foundation Models, Evidenz-Receipts, App Intents) | `aethel-apple-runtime@capabilities.v1` | 6.1, K4 |
| P4 | **aethelRegistry** als Ablösung von projects.yaml + 4 weiteren Registries: Produkt, Repo, Klon, Worktree, Komponente, Vertrag in SQLite; Generator per launchd; Drift als Ereignis | `aethel-registry@repo-produkt.v1` | 3 |
| P5 | **aethelContracts** (`workspace-manifest/contracts/` oder eigenes Repo): Ablage aller capability.json/Schemas, Konsumententest-Harness, Versionsregister | `aethel-contracts@index.v1` | 6.1 |
| P6 | **aethelCodeAnalyzer-Dienst + Sprachausbau**: tree-sitter für Swift/Python/TS, SARIF, Baum-Hash-Cache, XPC/Socket; aethel-codegraph (SCIP) als Datenquelle einbinden statt neu bauen | `aethelCodeAnalyzer@aix_findings.v2` | 4 |
| P7 | **aethelDependencyScanner** (Repo existiert leer): Cargo/pub/npm/SwiftPM/pip-Graph, Advisories, Pins; Konsument: aethelProjects | `aethel-deps@graph.v1` | 6.7 |
| P8 | **aethelReceipts/Evidenz**: Receipt-Schema (Digest, Baum-Hash, Image-Hash, Zeit, Thermik, Speicher), Signatur, Verifier (aus aethelAgentRuntime-Plan „Receipt-Verifier“) | `aethel-receipt@v1` | K3/K4 |
| P9 | **aethelGateContainer**: Gate-Image (Python 3.14, ruff, pinned), Containerization-Läufer, Grün-Cache je Baum+Image | `aethel-gate@container.v1` | 6.1 Isolation |
| P10 | **aethelVariantGenerator** für die aethel_core-Linie: aus core/design/product_shells generieren, 34 Shells nachziehen oder archivieren | `aethel_core@variant.v1` | 6.2 |
| P11 | **aethelObservability**: OSLog-Subsysteme, Signposts, MetricKit-Sammler, Service-Inventur (launchd-Soll/Ist), Health-Vertrag je Dienst | `aethel-obs@health.v1` | 6.7 Betrieb |
| P12 | **aethelKnowledgeReadModel**: Kiraa-Prinzipien aus `_aix_wissen.py` als Rust-Read-Model (Arrow/DataFusion), Import der 478 Akten mit Datum/Status, Anbindung aethel-omega | `aix-wissen@readmodel.v1` | 6.6 |
| P13 | **aethelCompanyLedger** (Firma): Angebot/Vertrag, Abrechnung, Support, Nutzung, Gesamtkosten je Produkt und Auftrag; Konsument der drei Kostenrechner | `aethel-firma@ledger.v1` | K1 |
| P14 | **aethelSecurityAudit**: Secrets-Scan, sandbox-exec-Verbot, Keychain-Migration, Audit-Receipts (aethelema ohne Audit) | `aethel-sec@audit.v1` | 6.7 |
| P15 | **aethelArchiveWave** (Prozess, kein Skript): die 106 Import-Repos, 88 Worktrees, 31 Nicht-Git-Ordner, 23 Scratch-Klone nach Regel „nichts löschen, archivieren“ mit Beleg | nutzt P4 | 2.8 |

Nicht vorgeschlagen: zweiter Orchestrator, zweite Registry neben P4, zweiter UI-Stack, Server-Datenbank, neue Agentenwelle.

---

## 10. Reihenfolge (Empfehlung, keine Beauftragung)
1. P4 Registry + Produkt-ID (ohne sie messen alle anderen Kreise falsch).
2. P5 Verträge-Ablage und als erster beidseitiger Test: aethelCodeAnalyzer ↔ aethelProjects (Golden-Fixture, Versions-Gate).
3. P2 aixd Schnitt 1 (Zustandstabelle, Übergangsvertrag) – ist bereits beauftragt (Astra-Entwurf); Komponenten-Tor in aethelLanding.
4. P3 aix-intel-Pilot (Foundation Models, Stufe 0) – nach `fm license` durch Manuel.
5. P1 ProjectManagement als Consumer des vorhandenen PM-Inputs.
6. Dann P6–P9, P11; P10/P15 als Aufräumwelle parallel (max. 3 Spuren).

---

## 11. Grenzen dieser Analyse
Kein fetch: Remote-Stände unbekannt. Reife- und Intent-Zahlen stammen aus dem Scan vom 23.10.; Repo-Zählung, Marker, launchd, Manifest-Abgleich von heute. Keine Funktionsprüfung einzelner Produkte (nicht gebaut, nicht gestartet). aethel-omega-Füllstand, Worktree-Nutzung, GitHub-Topics/Board und Kontobudget nicht geprüft. Zeilenangaben aus Lesezugriffen der Subagenten; Dateien unverändert, nur pytest-Cache geschrieben.

Quellen: aethelProjects reports/2026-10-23 (portfolio.scan.json, softwarefirma-bauabgleich.md, STATUS.md), aethelScripts/.aix-worker (PROFESSIONALISIERUNG-STAND-30-10, LUECKEN-UND-KORREKTUR-30-10, TECHNOLOGIE-ANSATZ-30-10, BESTAND-KOMPONENTEN-30-10), workspace-manifest (README, projects.yaml, docs/CONTROL-PLANE-RFC, DIGITAL-FIRM-RFC, STATUS), aethelFactory/README+docs/SPEC, aethelLanding README/CHANGELOG, aethelCodeAnalyzer (capabilities/, tests/aix_contract.rs, lib.rs), launchctl list, Dateisystem.

---

## 12. Ausblick Gesamtstack: vom Prozessor über das Betriebssystem bis zu allen Anwendungen

Manuel 03.11.: künftig soll ein eigener, geschlossener Softwarestack entstehen, von der Prozessor-/Rechenebene über ein Betriebssystem bis zu allen Anwendungen. Hier der Bestand je Schicht und die Lücke. Bewertung ist Ist-Befund, kein Plan.

| Schicht | Vorhanden im Workspace | Reife | Lücke |
|---|---|---|---|
| **Hardware/Rechenmodell** | aiderDesktop_memristor_v1 + memoristorCursor (Memristor- und Omega-vChip-Simulation, Rust, „compile-safe scaffold“), osxQ/osxq-pennylane (Quantensimulator auf MLX, eigenes PennyLane-Device), aethelHelix (Träger-/Dimensionen-Codierung, Amplituhedron-Branch), bit_encodings, photon-defense/photon-plm (ohne README) | Skizzen bis frühe Simulatoren; keine Hardwarebeschreibung (kein HDL, kein ISA-Dokument), keine Toolchain-Ziele | ISA/Rechenmodell nicht spezifiziert; kein Compiler-Backend; Simulatoren nicht an den Rest angebunden |
| **Laufzeit/Silizium-Nutzung** | MLX/Ollama hinter litellm :4000, aethelBrowser Evidenz-Brücke (Chip, Metal, Core ML, ANE), Foundation Models verfügbar, Metal 4 im Kanon | Betrieb, aber Skripte | „AETHEL Apple Runtime“ (Swift/XPC) fehlt; kein eigener Scheduler für GPU/ANE/Speicher (L12/L19) |
| **Betriebssystem/Kern** | aethel_os (leere Hülle, 3 Commits), lector_os (Flutter-Template, 33.256 generierte Dateien), omega-system/omega_domain/omega_bridge/omega_ui (6 Commits, kein README), aethelContainer (Prozess-Hypervisor, Zustandsmaschine, SQLite) als einziger echter Systemdienst-Ansatz | aethelContainer: Code ohne Betrieb; Rest Namen ohne Inhalt | Kein Kernel, kein Prozess-/Rechte-/Dateimodell, keine Bootkette. Realistischer Pfad im Kanon ist nicht ein eigenes OS, sondern eine Systemschicht **auf** macOS 27 (launchd, XPC, Containerization, Virtualization) und später ein Linux-Gastsystem in Containern; dafür fehlt die Entscheidung |
| **Komponentenlaufzeit / Steuerung** | aethelScripts AIX (Skripte), 13 aix-Crates, aethelAgentRuntime, aethelLanding, aethelBot | läuft als Skript-Flotte | `aixd`, Verträge, Receipts (siehe Abschnitte 5–8) |
| **Plattform-Kern / Wissen** | AETHEL (FIMAS-Kontrollebene, Rust), aethel-omega (Ω-Epistemik, TS), aethel-v6 (Cybernetic Framework), aethel-evolution, dinOmegaFoundations (leer), aethelDeepLearning (Summa Ω, Text) | Forschung, teils großer Code, ruht seit Juni/Okt | Vier Theorie-Repos ohne gemeinsamen Vertrag; keines liefert heute eine API, die eine Anwendung konsumiert |
| **Entwicklungsplattform** | Athelix (Low-Code, Flutter+Rust, 103 Commits), aethel_core/design/product_shells, aethelCodeAnalyzer, aethelLocalCoder, aiderDesktop-Familie, aethelAgentRuntime | gemischt, Athelix und aiderDesktop substanziell | Kein eigener Compiler/Build-System; Variant-Generator fehlt; Analyzer ohne Swift/Python/TS |
| **Daten / Speicher** | aix-ledger (SQLite), aethelContainer-Registry (SQLite), rust-mls/storage in aethelema, DuckDB im Kanon | punktuell | kein gemeinsames Datenmodell, kein Read-Model, keine Provenienz-Schicht (Kiraa) in Software |
| **Kommunikation / Verbund** | aethelema (P2P, Ed25519, Flutter+Rust, Mac/iOS/Windows), aethelBot, Bonjour im Kanon | läuft, experimentell, kein Audit | typisierte Nachrichten statt Text; Föderation M5↔M4 als Vertrag |
| **Anwendungen** | ca. 55 Produkt-Repos + 34 Varianten (Abschnitt 2.3/2.4) | 5–6 substanzielle (Browser, aethelema, vintage_radio, heritage Nuru, bitplay_lab, youtubereader, FamilyAppStore), Rest Shells | gemeinsame Basis (aethel_core/design) nicht durchgezogen; Distribution nur FamilyAppStore (privat) |
| **Oberflächen** | Flutter (123 Repos), SwiftUI (14), React-Leitstand, HTML-Renderer | Flutter dominiert | Kanon: SwiftUI für Mac-Natives + Flutter in aethelema; React/HTML sind Abweichung |
| **Querschnitt: Sicherheit, Identität, Rechte** | aethelema Identität (Ed25519), Rollenkatalog (15 Rollen), aix-secrets, Keychain im Kanon | Rollen laufen, Identität ungeprüft | kein Rechte-/Capability-Modell über alle Schichten; Geheimnisse teils in Dateien |

### Befund zum Gesamtstack
1. **Die unteren Schichten sind Namen, keine Komponenten.** aethel_os, omega-system, lector_os, dinOmegaFoundations, bit_encodings, photon-* haben zusammen weniger Inhalt als ein einzelner aix-Crate. Nur aethelContainer und die Memristor-Scaffolds enthalten Systemdenken in Code.
2. **Es gibt keine Schichtenkarte mit Verträgen.** Welche Schicht welche API nach oben anbietet, steht nirgends; damit kann keine Anwendung „auf dem Stack“ gebaut werden, sie baut auf Flutter und macOS.
3. **Die Forschung ist vom Produkt getrennt.** AETHEL, aethel-omega, aethel-v6, Summa Ω, Helix, osxQ laufen nebeneinander, ohne dass ein Ergebnis als Komponente in AIX, aethelema oder eine App eingeht.
4. **Der Kanon vom 07.09. ist schon eine Stack-Entscheidung:** Rust-Kern, Swift-Laufzeit auf Apple-Frameworks, Flutter-Clients, SQLite-Wahrheit. Ein eigener Prozessor oder Kernel steht darin nicht. Ein Stack „von unten“ widerspricht nicht dem Kanon, braucht aber eine ausdrückliche Entscheidung, welche Schichten eigen (Rechenmodell, Komponentenlaufzeit, Wissen, Apps) und welche fremd (Silizium, macOS/Linux-Kern, Compiler) bleiben.
5. **Reihenfolge-Risiko:** Ohne funktionierende Mitte (aixd, Verträge, Registry, Receipts) ist jede weitere Schicht unten oder oben ein weiteres unverbundenes Repo. Die Fabrik muss erst sich selbst bauen können, bevor sie einen Stack baut.

### Fehlende Projekte für den Gesamtstack (Ergänzung zu Abschnitt 9)
| # | Vorschlag | Komponente@Vertrag |
|---|---|---|
| S1 | **aethelStackMap**: Schichtenkarte als Datenmodell (Schicht, Komponente, Vertrag nach oben/unten, eigen/fremd, Reife), gepflegt in der Registry P4, Sicht in aethelema | `aethel-registry@stack.v1` |
| S2 | **aethelComputeModel**: ISA-/Rechenmodell-Spezifikation (Memristor/Omega-vChip, Helix-Codierung, Quanten-Device) mit einem Simulator-Vertrag, den Compiler und Laufzeit konsumieren; zusammenführen von memristor_v1, memoristorCursor, osxq-pennylane, bit_encodings | `aethel-compute@isa.v1` |
| S3 | **aethelSystemLayer** (statt „aethel_os“): Systemdienste auf macOS 27 als Komponenten (aethelContainer wiederbelebt, Containerization, launchd/SMAppService, XPC-Verträge, Rechte/Capabilities, Keychain), später Linux-Gast in Containern als zweites Ziel | `aethel-system@services.v1` |
| S4 | **aethelCompilerToolchain**: eigene Zielplattform in vorhandene Toolchains (Rust-Target/LLVM-Backend für S2, Dart/Flutter-Embedder für S3), bevor an eigene Sprachen gedacht wird | `aethel-toolchain@target.v1` |
| S5 | **aethelPlatformSDK**: eine Bibliothek je Sprache (Rust, Swift, Dart), über die Anwendungen den Stack nutzen (Identität, Aufträge, Wissen, Receipts); löst die 13 direkt gekoppelten Varianten und die drei Analyzer-Konsumenten ab | `aethel-sdk@v1` |
| S6 | **aethelResearchGate**: Regel plus Vertrag, wie ein Forschungsergebnis (AETHEL, omega, v6, Summa Ω, Helix) zu einer Komponente wird: Spec, Test, Konsument; sonst bleibt es im Forschungsregister | nutzt P5 |
| S7 | **aethelDistribution**: Signierung, Notarisierung, Update-Kanal, Rücknahme für alle Apps (heute nur FamilyAppStore privat) | `aethel-dist@release.v1` |

---
Ergänzungsbericht (Technologie, Architektur, Kybernetik auf macOS 27, Werkzeug- und Forschungsabgleich, Siemens/Mendix/Kiraa/Kiro): `WORKSPACE-ANALYSE-2026-11-03-ERGAENZUNG-TECHNOLOGIE-ARCHITEKTUR.md` (03.11.2026).
Gesamtstack-Bericht (Schichten, Best Practice, Bauteile mit Hebel, eigen/fremd, Reihenfolge): `WORKSPACE-ANALYSE-2026-11-03-GESAMTSTACK-BAUTEILE.md` (03.11.2026).
