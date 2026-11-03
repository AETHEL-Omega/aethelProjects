# Ergänzungsbericht: Technologie, Architektur, Kybernetik auf macOS 27

Stand 03.11.2026. Ergänzt `WORKSPACE-ANALYSE-2026-11-03.md` (Hauptbericht). Nur Analyse; nichts verändert, nichts installiert, keine Lizenz bestätigt. Auftrag von Manuel: sicherstellen, dass auf macOS 27 die richtige Technologie und Architektur eingesetzt wird; alle Fähigkeiten von Cursor, LangGraph und anderen übernehmen; Teamcenter, Xcelerator, Mendix und Kiraa architektonisch abgleichen; Forschungsstand seit Mitte 2026; Kybernetik vollständig auf allen Ebenen.

## 0. Kurzfazit

1. Die Plattform ist komplett: macOS 27.0.1, Xcode 27.2, Swift 6.4.2, Foundation Models mit `fm`, Core AI, Containerization 1.4, App Intents, XPC. Die Fabrik nutzt davon fast nichts; die Lücke ist Anbindung, nicht fehlende Software.
2. Apple hat 2026 genau die Schichten geliefert, die der Kanon vom 07.09. als Eigenbau vorsah: Modellabstraktion (`LanguageModel`-Protokoll), Evaluation, Agent-Cockpit mit Plan und Subagenten (Xcode 27), Skills, Isolation. Eigenbau dort ist nach Kanonregel 1 nicht mehr erlaubt.
3. Der Verfassungskern existiert bereits in Teilen: aethelAgentRuntime hat Replay-Ledger, Proposal → Policy → Approval → Action, Rust-Risikoklassifizierer, Governor-Leases, Audit, Limbus und Compliance mit 55 Werkzeugen und Verträgen `aethel.*.v1`. Er läuft als Beobachter, wird von der aix-Fabrik nicht benutzt und heißt nicht aixd. Das korrigiert den Hauptbericht.
4. Es gibt zwei Kerne, vier Sandboxen, drei Gedächtnisse, drei Regelquellen an 826 Orten, zwei Modellkataloge, elf MCP-Server-Implementierungen und 238 Crates ohne Betrieb in aiderDesktop. Die Varietät der Fabrik übersteigt die der Projekte, die sie steuern soll.
5. Deploy-Drift ist systemisch: `~/bin` weicht vom Repo ab, deployte MCP-Server vom Repo, die aix-Laufzeit liegt 114 Commits hinter main, Parität ist rot. Jeder Lauf arbeitet mit unbekanntem Code.
6. Im Werkzeugabgleich (32 Fähigkeiten) hat AETHEL in 9 Betrieb, in 15 Code ohne Betrieb, in 4 nur Dokument, in 4 nichts. In zwei Punkten (deterministische Code-Intelligenz, Mutationstests) ist AETHEL weiter als Cursor und Claude Code.
7. Eine fertige LangGraph-Fabrik (digitalSoftwareFactory: Zustandsgraph, SQLite-Checkpointer, Interrupt/Resume, MCP, Tests) liegt seit Juni ungenutzt. LangGraph-Übernahme heißt zuerst: eigenen Code bewerten.
8. Forschung 2026 verlangt drei Dinge, die fehlen: Harness als Komponente mit sieben Teilsystemen; Verifikation, die mit dem Erzeuger mitwächst (zurückgehaltene Tests, Testdatei-Wächter, unabhängiger Richter); Gedächtnis aus Commit-Historie.
9. Teamcenter und Mendix zeigen, was der digitalen Firma fehlt: Produkt-ID mit Revision und Status, Komponentenstückliste, Änderungsobjekt mit Betroffenheit, Workflow als Daten, Digital Thread von SPEC bis Betrieb, Konfigurator für Varianten, Lieferantenkonten für Fremdagenten, Compliance als Kategorie. Kiro zeigt den Spec-Graph mit Wellen, Kiraa das Schichtenmodell lokal-nativ.
10. Kybernetik vollständig heißt: sieben Rekursionsebenen (Werkzeugaufruf, Lauf, Schnitt, Projekt, Portfolio, Firma, Umwelt) plus Meta-Ebene, jede mit Sollwert, Sensor, Vergleicher, Stellglied in Software; VSM-Organe S2, S3, S3*, S4, S5 und algedonischer Kanal; heute sind alle Kreise offen, S3*, S4 und der Alarmkanal fehlen als Organe. Erster Schritt ist die Loop-Registry im Kern.
## 1. Plattformstand auf diesem Mac (gemessen am 03.11.2026)

Alle Werte sind auf dieser Maschine gemessen, nicht aus Dokumenten übernommen.

| Baustein | Ist | Kanon (CLAUDE.md 30.10.) | Befund |
|---|---|---|---|
| macOS | 27.0.1 (26A434) | macOS 27 | passt |
| Xcode | 27.2 (27B52) | Xcode 27 | passt; `mcpbridge`, `mcp-server`, `lldb-mcp` und `xcrun agent skills` sind vorhanden und ungenutzt |
| Swift | 6.4.2 | Swift 6.4 | passt |
| Rust | 1.97.1 (Homebrew, Juli 2026) | Rust 1.98 | Abweichung: Kanon nennt eine Version, die nicht installiert ist. Kanon oder Toolchain angleichen |
| Python | 3.15.1 | Übergangsrand | passt zur Rolle |
| Flutter / Dart | 3.48.0 / 3.12.2 | aethelema-Client | passt |
| MLX | 0.32.4 (Python); `mlx_lm.server` vorhanden | lokale Inferenz | vorhanden, aber ohne Katalogbindung |
| Ollama | 0.40.11 | lokale Inferenz | vorhanden |
| litellm-Router :4000 | läuft (launchd `dev.toolkit.litellm`, PID 26548, Port offen); `/health` antwortet nicht innerhalb von 2 s, weil es alle Modelle prüft | Hub laut Memory | läuft; aber zwei Sensoren (`aix_doctor` grün, kurzer HTTP-Probe rot) ohne gemeinsamen Gesundheitsvertrag |
| `/usr/bin/fm` | vorhanden; Befehle `respond`, `chat`, `serve` (Chat-Completions-Server), `schema` (strukturierte Ausgabe), `count-tokens`, `available` (Systemmodell verfügbar) | Stufe 0 für Triage/Extraktion | Lizenz (`fm license`) noch nicht bestätigt; `apple_fm_sdk` (Python) nicht installiert |
| FoundationModels.framework | vorhanden; 133 Swift-Dateien im Workspace importieren es, alle in aethelBrowser-Worktrees | Stufe 0 | Nutzung nur im Browser-Projekt, nicht in Fabrik oder Laufzeit |
| Containerization / `container` | `container` nicht installiert; Virtualization.framework vorhanden; stattdessen Docker, OrbStack, Parallels, colima, lima, podman | Containerization statt sandbox-exec | Zielwerkzeug fehlt, fünf Ersatzwerkzeuge parallel installiert |
| Core AI | Framework in macOS 27 (laut Apple-Guide: Swift-API zum Laden, Spezialisieren, Ausführen eigener Modelle) | nicht im Kanon | nirgends verwendet, nirgends bewertet |
| App Intents, ExtensionKit, ServiceManagement, MetricKit, Network, SwiftData | alle vorhanden | gefordert | kein Dienst im Workspace nutzt SMAppService oder XPC als Vertragsgrenze (Subagent-Befund, Abschnitt 3) |
| Agent-CLIs installiert | claude, codex, cursor, cursor-agent, cline, goose, opencode, zed, aider; Apps: Cursor, Zed, VS Code, LM Studio, Claude, CodexBar | Codex als Worker freigegeben | neun Agent-Harnesses installiert, kein gemeinsamer Vertrag, kein gemeinsames Gedächtnis |
| MCP-Server (Claude-Benutzerkonfiguration) | 10: aethel, aethel-runtime, aix, browser, codebase, filesystem, frb, github, playwright, software | Komponenten mit Verträgen | eigene Server `aix`, `aethel`, `aethel-runtime`, `software` ohne Versionsvertrag; MCP-Revision 2026-07-28 (zustandslos, Roots/Sampling/Logging abgekündigt) nicht geprüft |
| Codex-Konfiguration | 15 `mcp_servers`-Einträge | | zweite MCP-Konfiguration neben Claude, nicht aus einer Quelle erzeugt |
| Claude-Hooks | 4 Ereignisse (SessionStart, Notification, UserPromptSubmit, Stop) von 17–18 möglichen | | Hooks als Steuerungsfläche kaum genutzt; kein PreToolUse/PostToolUse-Tor |
| Claude-Skills / -Agents | 6 Skills, 0 Agents | | Rollen laufen als launchd-Skripte statt als Agent-Definitionen |
| `.cursor`-Verzeichnisse im Workspace | 290 | | Regeln dreifach (CLAUDE.md 226, AGENTS.md 117, .cursor 290), ohne gemeinsame Quelle |
| ACP (Agent Client Protocol) | 42 Treffer, alle in Forks (goose, interpreter, gptme, pydantic-ai, openhands); 0 eigene | | kein eigener Agent ist in Xcode 27, Zed oder JetBrains andockbar |
| Spezifikationsdateien | 157 SPEC/DESIGN/TEST-CASES im Workspace, 15 davon mit SHALL/EARS-Sätzen | Spec→Tests→Impl | Spezifikation existiert, aber nicht maschinenlesbar verknüpft mit Tasks und Code (Kiro-Vergleich, Abschnitt 4) |
| Node | `nvm`-Lazy-Loader defekt, `node` nicht aufrufbar | | TypeScript-Agent-SDKs (Claude, Cursor) sind in dieser Shell nicht lauffähig |

Kurz: Die Plattform ist komplett und aktuell. Die Fabrik nutzt davon fast nichts. Der Abstand liegt nicht in fehlender Software, sondern in fehlender Anbindung.

## 2. Was macOS 27 und Xcode 27 liefern und was davon gehört

Quelle: Apple WWDC26 macOS-Guide, Xcode-27-Sessions, Sekundärquellen (Kennzeichnung „sek.“ bei nicht primär belegten Angaben).

| Angebot der Plattform | Was es ist | Was es für AETHEL bedeutet | Entscheidung |
|---|---|---|---|
| **Foundation Models: `LanguageModel`-Protokoll** | Eine `LanguageModelSession` kann jedes konforme Modell tragen: `SystemLanguageModel` (On-Device), `PrivateCloudComputeLanguageModel`, `CoreAILanguageModel`, `MLXLanguageModel` (sek.), Anthropic- und Google-Pakete (sek.). Wechsel ist Paketwechsel, kein Codewechsel | Das ist die native Modellabstraktion, die AETHEL bisher mit litellm, `~/bin/*-mlx` und Katalogdateien nachbaut | Übernehmen als Modellgrenze der Apple-Laufzeit. litellm bleibt nur am Python-Rand. Ein Katalog (aixd) speist beide |
| **On-Device-Modell** | ca. 3B Parameter, Kontext 8.192 Token, Tool-Calling, Bildeingabe, `@Generable` strukturierte Ausgabe, Guardrails | Reicht genau für Stufe 0: Triage, Klassifikation, Extraktion, Zusammenfassung. Nicht für Review oder Architektur | Stufe 0 festschreiben; kein Urteil |
| **Private Cloud Compute** | 32k Kontext, Reasoning-Stufen, ohne API-Schlüssel; kostenfrei unter 2 Mio. Erst-Downloads | Ist Cloud. Unter LOCAL_AI_ONLY verboten, unter HYBRID als Kostenklasse „nachweislich kostenlos, Apple-Bedingungen“ führbar | Nur mit Freigabe und Kostenklasse im Katalog |
| **Dynamic Profiles** | Instruktionen, Werkzeuge, Modell und Reasoning je Zweig innerhalb einer Sitzung wechselbar, Verlauf bleibt | Entspricht Rollenwechsel (Triage → Extraktion → Bericht) ohne Kontextverlust | Für Stufe-0-Ketten nutzen |
| **Systemwerkzeuge** | OCR, Barcode, Spotlight-Suche als Tools, lokale RAG über den Spotlight-Index | Belege und Screenshots aus Gates könnten lokal gelesen werden | Für Beleg-Extraktion prüfen |
| **Evaluations-Framework** | Swift-Framework zum statistischen Messen von KI-Verhalten bei wechselnden Eingaben | AETHEL hat kein Evaluationsgerüst für eigene Prompts/Stufe-0-Ketten | Übernehmen für jede Stufe-0-Kette: Eval vor Betrieb |
| **`fm` CLI + Python-SDK `apple_fm_sdk`** | Skriptzugang zum Systemmodell; `fm serve` bietet Chat-Completions-API | Python-Übergangsrand kann ohne litellm ans Systemmodell | `fm serve` als lokaler Endpunkt für Stufe 0 im Python-Rand; SDK installieren, Lizenz durch Manuel |
| **Open Source FM-Framework** | Framework und „Utilities“-Paket (Transcript-Verwaltung, Skill-API, Chat-Completions) sollen offen und auf Linux lauffähig werden (sek.) | Laufzeit könnte in Linux-Containern dieselbe Modellgrenze nutzen | Beobachten; Vertragsgrenze nicht darauf bauen, bis Quelle veröffentlicht |
| **Core AI** | Speichersicheres Swift-Framework zum Laden, Spezialisieren und Ausführen eigener Modelle auf Apple Silicon, AOT-Kompilierung, Zero-Copy, zustandsbehaftete Ausführung; Nachfolger von Core ML (sek.) | Eigene Gewichte (Adapter, feinjustierte Klassifikatoren) gehören hierhin, nicht in Python-Prozesse | Für eigene Spezialmodelle (Stub-Erkennung, Intent-Klassifikation) als Zielrahmen vormerken |
| **MLX** | Apple-Array-Framework für Training und Experiment; über FM-Protokoll als Backend (sek.) | Ist der Forschungsrand; bleibt | Experiment ja, Laufzeit über FM-Protokoll |
| **Xcode 27 Agentic Coding** | Agenten von Anthropic, Google, OpenAI eingebaut; jeder ACP-Agent andockbar; `/plan`-Modus mit editierbaren Plan-Artefakten; Agenten schreiben und laufen Tests, nutzen Playgrounds, Previews, Simulator über Device Hub; koordinierte Subagenten; Transcript links, Artefakte rechts | Xcode ist bereits ein Agent-Cockpit mit Plan, Verifikation und Subagenten. AETHEL baut dasselbe als Skriptflotte | AETHEL-Agent als ACP-Server anbieten, damit Xcode, Zed, JetBrains ihn fahren. Xcodes Plan/Verify-Schleife als Referenz für die Laufzeit |
| **`mcpbridge` / Xcode-MCP** | MCP-Server für Dateien, Build, Tests, Diagnostik, Debugger-Konsole, Schemes, Build-Settings, Entitlements, Info.plist | Deterministische Werkzeuge für Swift-Projekte sind fertig | Für alle Swift-Repos als Werkzeugquelle nutzen statt eigener Skripte |
| **Agent Skills in Xcode** | Sieben Apple-Skills im offenen `SKILL.md`-Format, Export per `xcrun agent skills export` | Gleiches Format wie Claude Code und Deep Agents | Skill-Format als Standard für AETHEL-Rollen übernehmen |
| **Device Hub / `devicectl`** | Geräte- und Simulatorverwaltung mit CLI für CI | Gate für iOS-Varianten (aethel_core-Linie) automatisierbar | In Gate-Container aufnehmen |
| **Instruments agentic profiling, Organizer-Fixes** | Profiling von Agent-Erfahrungen; agentengestützte Crash-Fix-Empfehlungen | Signposts statt Logdateien, wie Kanon fordert | OSLog/Signposts in Laufzeit und Dienste |
| **App Intents** | Entity- und Intent-Schemas ohne Phrasen, View Annotations, `AppIntentsTesting`, Spotlight-Semantikindex | Fabrik vom iPhone/Siri steuern (Auftrag anlegen, Freigabe geben) | Freigabe-Intents mit LocalAuthentication |
| **Containerization 1.4.1 / `container`** | Ein leichtes VM je Container, OCI-Images, Static Linux SDK; kein Compose; signiertes Installationspaket von GitHub | Hermetischer Gate-Container ist möglich, aber kein Compose: Mehrdienst-Gates brauchen eigenes Orchestrieren | Installieren; aethelContainer als Vertragshülle; Compose-Lücke in aethelContainer schließen, nicht mit Docker Desktop |
| **Swift 6.4 / Swift Testing** | Async-freundliche Makros, XCTest-Migration | Tests zuerst, wie Kanon | Pflicht für neue Swift-Pakete |
| **ServiceManagement (SMAppService), XPC, launchd** | Dienste mit Lebenszyklus und Rechten | 38 launchd-Skripte ohne XPC-Vertrag | aixd und Apple Runtime als XPC-Dienste |
| **Keychain, Secure Enclave, LocalAuthentication** | Geheimnisse und Freigaben | Freigaben laufen heute über Chat | Freigabe = LocalAuthentication-Ereignis mit Beleg |
| **Network.framework / Bonjour** | Verbund M4/MacBook | aethelBot koppelt über aethelema | Bonjour-Dienstankündigung für aixd |
| **MetricKit, OSLog** | Metriken, Signposts | 478 Markdown-Akten als Gedächtnis | Ereignisstrom statt Akten |

Fazit zu Abschnitt 2: Apple hat 2026 genau die Schichten geliefert, die der Kanon vom 07.09. als Eigenbau vorsah: Modellabstraktion, Evaluation, Agent-Cockpit, Skills, Isolation. Der Eigenbau ist damit nicht mehr nötig und nach Kanonregel 1 nicht mehr erlaubt.
## 3. Eigener Bestand: was im Workspace an Agent-Infrastruktur existiert

### 3.1 Direkt gemessen über die laufenden MCP-Server (03.11.2026)

**aethelAgentRuntime 0.1.0** (`aethel-agent mcp serve`, Schema `aethel.runtime.capabilities.v1`) meldet 55 Werkzeuge mit Annotationen, Mutationsflag und `allowedForCaller`. Invarianten laut Selbstauskunft: Replay ist einzige Wahrheit; Proposal → Policy Decision → Approval → Action ohne Abkürzung; beobachteter Text ist Beleg, keine Anweisung; Mutationen nur mit `AETHEL_MCP_ALLOW_MUTATIONS=1` und `AETHEL_MCP_TRUSTED_HUMAN`. Vorhanden:

| Fähigkeit | Werkzeuge | Bewertung |
|---|---|---|
| Ledger, Replay, Zeitleiste | sessions.list, events.tail, proposals.list, approvals.list, replay.get, replay.store.search (FTS5 SQLite), knowledge.timeline | Das ist der Ledger, den der Kanon für aixd fordert. Er existiert, in Rust, mit SQLite-Projektion |
| Vorschlag, Freigabe, Aktion | proposals.create (mit sha256 vorher/nachher je Datei, Provenance-Zeile mit Modellklasse, Prompt-/Response-Hash), approvals.approve/reject/pending | Freigabe als Ereignis mit Beleg existiert; aber `allowedForCaller=false` für alle 54 Werkzeuge außer describe: im Betrieb beobachtet nur |
| Richtlinie und Risiko | policy.evaluate (Rust-Klassifizierer, einzige Wahrheit, ersetzt veraltete Python/Dart-Kopien), blocks.by_risk, governor.leases.get (active/constrained/frozen, concurrencyLimit, maxRisk) | S2/S3-Organe (Lease, Drossel) sind als Code da; Governor schreibt Leases nur mit `--apply` |
| Prüfung und Compliance | evals.score (Geisteraktionen, fehlende Belege, Freigabe-Hygiene), compliance.verify (manipulationssichere Kette), compliance.evidence (COBIT/BSI), privacy_label, gdpr | S3*-Audit existiert als Code: advisory, blockiert nichts |
| Sandbox | aethel.shell über `aethelcontainerd` („hard sandbox“), container.* als Proxy auf die aethelContainer-API (Instanzen, Stacks, Dienste, WASI-Agent-Tasks über Wasmtime mit Speicherlimit) | Eigene Container-API vorhanden; Verhältnis zu Apple Containerization ungeklärt; Stacks-Begriff deckt die Compose-Lücke |
| Gedächtnis und Wissen | memory.snapshot, catalytic.reconstruct, knowledge.search/recall/evidence (FTS über Terminal-Journal, Replay, Belege, mit Provenienz), graph.search/neighbors/query/brief (SQLite-Graph), graph.set_user_weight (Lernsignal) | Ein Wissensgraph mit Provenienz existiert. Er ist nicht aethel-omega und nicht `_aix_wissen`: drittes Gedächtnis |
| Rückbau statt Löschen | limbus.list/quarantine/restore/purge (Papierkorb mit TTL, Undo-Route senkt Freigabe-Reibung) | Manuels Regel „nichts wegwerfen“ als Software |
| Fremdagenten | coder.resume (claude, codex, aider, aethel-surfer deterministisch fortsetzen) | Ansatz für Lieferantenkonten |
| Welt und Terminal | world.snapshot/diff, command.boundaries | Typisierte Umgebungswahrnehmung statt Textparsen |
| Forschung | quantum.simulate (osxQ/MLX) | Forschungsrand im Laufzeitvertrag: gehört hinter ein Forschungs-Tor |

**aix (aethelScripts)** meldet über `aix_doctor`: Parität verletzt (`bin/stack-sync --deploy-only` rot), Laufzeit STALE (Worktree `docs/aix-umbau-rust-swift-flutter` 114 Commits hinter main, `aix-solve` läuft alten Code), Gateway :4000 grün, z3 grün. Mein eigener `curl` auf `:4000/health` ergab HTTP 000. Zwei Sensoren widersprechen sich; keiner löst etwas aus.

**aix Copilot** meldet 27 In-Prozess-Werkzeuge, darunter strukturelle Suche (ast-grep), `wer_ruft`, `sprengradius` (was bricht), `bisect` ohne Modell, `mutationstest`, `inspiziere` (JetBrains offline: Datenfluss, Nullability, toter Code), `repariere` (gemessen 61 von 93 Befunden ohne Token), `aendere_signatur` (alle Aufrufstellen mechanisch), `omega_validate_dag` (Zyklenfreiheit eines Auftragsgraphen), `sheaf_verify_budgets` (Ressourcenverträge), `aix_cut_ast_hole` und `aix_verify_vsa_scope` (getypte Löcher, Scope-Verifikation), `aix_clarify` (strukturierte Rückfrage).

### 3.2 Was das für den Hauptbericht korrigiert

1. Der Hauptbericht sagte „kein aixd“. Richtig ist: Der Verfassungskern existiert in Teilen als aethelAgentRuntime (Ledger, Proposal/Approval, Policy, Lease, Audit, Limbus), nur nicht unter dem Namen aixd, nicht als XPC-Dienst, nicht von der aix-Fabrik benutzt, und im Betrieb auf „nur beobachten“ gestellt. Die Lücke ist Anbindung und Betrieb, nicht Code.
2. Es gibt zwei Kerne (aix in aethelScripts, aethelAgentRuntime) mit zwei Werkzeugsätzen, drei Gedächtnissen (aethel-omega, `_aix_wissen`, runtime graph.sqlite) und zwei Sandboxen (sandbox-exec in aix, aethelcontainerd in der Runtime). Kanonregel 4 (Bestand vor Neubau) verlangt, einen davon zur Wahrheit zu erklären.
3. Die Code-Intelligenz (ast-grep, Sprengradius, Bisect, Mutationstest, Signaturänderung) ist weiter als bei Cursor oder Claude Code, die keines dieser deterministischen Werkzeuge mitbringen. Sie ist nur in Python und nicht als Vertrag für Fremdagenten veröffentlicht.
4. Die Parität ist rot und die Laufzeit veraltet. Jeder Lauf von `aix-solve` auf diesem Mac arbeitet mit Code, der 114 Commits zurückliegt. Das ist ein offener Kreis auf Ebene E4 mit Sensor, aber ohne Stellglied.
### 3.3 Inventar der Agent-Infrastruktur im Workspace (Subagent, read-only, grobe Zeilenzahlen)

Methode: grep auf Importe, `wc -l`, `launchctl list`, Port-Probes. Ausgeschlossen: node_modules, target, build, .venv, archive*, Worktree-Ordner. „Läuft“ heißt: launchd-Job mit PID oder Port antwortet am 03.11.2026.

**Wo die Substanz liegt**

| Repo | Größe (grob) | Rolle | Betrieb |
|---|---|---|---|
| aethelScripts | Python ~307k Zeilen (`bin/` 1.006 Dateien), Rust ~25,7k in 13 `aix-*`-Crates; 2.369 Commits, letzter 28.10. | De-facto-Kern „AIX“ | läuft über `~/bin` (1.127 Einträge, gedriftete Kopie) |
| `~/.aix` | 61 GB Zustand; `events/` 347 MB in 66.159 Dateien; `ledger/aix.sqlite` 2,1 MB (nicht lesbar) | Live-Zustand | Dashboard :7331 läuft |
| aiderDesktop | Rust ~280k, Swift ~243k, Python ~44k; **238 Crates**; letzter Commit 03.10. | Crate-Landschaft (Orchestratoren, MCP, Sandbox, Router, Eval, Memory) | kein launchd-Eintrag; nichts davon läuft |
| aethelAgentRuntime | Rust ~158k (Dart ~241k, teils generiert) | `aethel-agent`, Session-Daemon, MCP `aethel-runtime` | läuft (Session-Daemon PID 3798) |
| aethel-omega | TypeScript ~44,7k, 143 Testdateien | Wissen, Claims, Atlas, eigener MCP-Server | nur auf Abruf; MCP-Server in keiner Client-Konfiguration |
| digitalSoftwareFactory | Python ~44,9k; letzter Commit 09.06. | **LangGraph-Fabrik** mit `StateGraph`, Memory-/SQLite-Checkpointer, Interrupt/Resume (`Command`), MCP-Server (1.015 Zeilen), Daemon- und Installationsskript, Tests | kein Betrieb, kein Client |
| hydra_forge | Python ~3,75k; letzter Commit 17.06. | LangGraph-Agent (`StateGraph(AlgoMaxState)`), Control-Plane, Omega-Client, MLX-Engine | kein Betrieb |
| aethelContainer | Rust ~6,5k (7 Crates), Flutter ~7,3k; letzter Commit 22.07. | Container-/VM-Daemon; `vm.rs` ruft `tart`; Isolation `profile`/`sandbox_exec`/`vm`; E2E-Test 1.370 Zeilen | Plist zeigt auf `target/debug`, nicht geladen; `tart` nicht installiert |
| aethelLocalCoder | Python ~15k | Model-Hub, Cursor-Continue-Audit-Proxy; einziges Repo mit versionierten Releases | läuft (2 PIDs) |
| aethelLanding | Python ~6,2k, 9 Worktrees | Siegel/Verdikt | nicht geladen (Inhalt vom Subagenten nicht gelesen) |

**Agent-Frameworks**: LangGraph nur in digitalSoftwareFactory und hydra_forge, beide ohne Betrieb. CrewAI, AutoGen, DSPy, pydantic-ai, smolagents, Claude Agent SDK, OpenAI Agents SDK: keine Importe im eigenen Code. Referenzklone unter `orchestrierung-quellen/`, `sprache-quellen/`, `coder-quellen/` (aider, cline, goose, openhands, swe-agent, swe-bench, mini-swe-agent, letta, langgraph u. a.) sind Lesestoff, kein Einsatz. Der laufende Stack ist Eigenbau in Python und Bash (Postfach-Knoten `knoten.sh`).

**MCP**: Ein gemeinsamer Hub (`local.mcp-hub` → `~/bin/mcp-hub`, Quelle `aethelScripts/mcp/registry.json`) startet sechs FastMCP-Server auf :9101–9106 (aethel 14 Tools, codebase 4, software 3, frb 5, browser 7, aix 24) und einen Proxy :9110 (aethel-runtime, filesystem, github). Alle sieben Ports antworteten. Das ist das einzige Stück Infrastruktur, das Claude und Codex aus einer Quelle versorgt. Drift: deployte `mcp_aethel.py` 147 Zeilen gegen 212 im Repo, `mcp_browser.py` 239 gegen 337. Weitere MCP-Server ohne Betrieb: omega (TS), aethelcontainer (Rust), fabric (Rust), elf `aether_mcp_*`-Crates in aiderDesktop, digitalSoftwareFactory-Player, quantumstudio, aethel-macos-work-surface, claude-cybernetic-loop (Kopie von aethel-mcp). `~/.cursor/mcp.json` fehlt; `~/.claude/settings.json` hat keinen `permissions`-Block; LSP-Plugins (swift, clangd, rust-analyzer) aktiv.

**Code-Intelligenz**: LSP nur als Rename-Brücke (`_lsp_client.py` 678 Zeilen: rust-analyzer, gopls). tree-sitter nur in aiderDesktop-Crates (`code_symbols`, `ast_parser.rs` 700) ohne Betrieb; der laufende Python-Pfad nutzt `ast`, also nur Python. Python-AST-Chirurgie (`_aix_ast_hole.py`, `_aix_ast_slice.py`) läuft über :9106. Symbolindex (`aix_world_symbols`, `codebase_index.py` 455, SQLite-Caches 751 Dateien) läuft. Repo-Map klein, läuft. Embeddings/Vektor (`aethel_embeddings`, qdrant in digitalSoftwareFactory, `memoria.py` 943) nirgends im Betrieb. Kein sourcekit-lsp-Client.

**Sandboxing**: Aktiv nur `sandbox-exec` im Hermes-Pfad (`_mlx_runtime.py` Z. 46–125, Test vorhanden). Drei weitere Seatbelt-Implementierungen ohne Anbindung (`aix-agent/sandbox.rs` 155, aiderDesktop `aether_mcp_sandbox_macos` mit `(deny default)` und `worktree_guard.rs` 1.090, claude-cybernetic-loop `mcp_sandbox.rs` 691). Virtualization.framework: kein eigener Code. Docker, podman, lima, OrbStack installiert und von keinem Agentenpfad benutzt.

**Zustand und Gedächtnis**: Rust-Crates aix-ledger, aix-kernel, aix-domain, aix-hdc, aix-sheaf, aix-sync, aix-recovery, aix-verification, aix-secrets, aix-forgejo, aix-workspace, aix-cli, aix-agent (~25,7k Zeilen) mit unklarer Verbindung zu `~/bin`. Wissensschleife (`_aix_wissen*.py`, `_aix_unwissen.py`) läuft über `aix-boot`; ein Repo `_aix_wissen` existiert nicht. aethel-omega auf Abruf über `aix_omega_claim/query` und `aix-claim-omega-bridge.mjs`. LangGraph-Checkpointer in digitalSoftwareFactory mit Test, ohne Betrieb. aiderDesktop: acht Zustands-Crates dem Namen nach. Regeldateien ohne Archive: CLAUDE.md 289, AGENTS.md 252, `.cursor/rules` 285, GEMINI.md 11, `.claude/skills`-Ordner 21, `.claude/commands`-Ordner 16.

**Governance**: Lese-/Schreib-Trennung in `mcp_aix.py` (`_NUR_LESEND`, `_MUTIERENDE_WERKZEUGE`, Tests). Drei Merger-Rollen als launchd-Jobs mit PID; `aix-merge-gated` nicht gelesen. Receipts: `docs/receipts/`, `aethel_gate/receipt.rs` in aethel-v6, `~/.aix/audit-ledger.jsonl` mit 6 Zeilen. Diff-Review-Crates nur dem Namen nach.

**Evaluation**: `aethelScripts/bench/` (Korpus, Hard-9, Ergebnisse, Dashboard-HTML), `aix-bench*`, `aix-eval*`; Job `aix-bench-world-auto` nicht geladen. `eval_models` erreichbar. SWE-bench nur als Klon. Kein Regressionstor je Änderung.

**Inferenz**: Läuft: litellm :4000, `local.mlx-coder` (Qwen2.5-Coder-32B-4bit :8181), Cold-Start-Proxy, LocalCoder-Hub, Ollama :11434, Tabby :8080. Nicht geladen: mlx-heavy :8085, qwen3-next :8099 (dort lauscht trotzdem ein nicht zugeordneter Python-Prozess), qwen-coder-1.5b :8097, qwen38, fast :8098, claude-proxy, ccproxy. Kataloge: `coders/aliases.json`, `model-families.json`, `playbook.json`, `profiles.json`; Router-Crates in aiderDesktop ohne Betrieb.

**Multi-Agent**: 13 `com.aethel.rolle-*` plus drei Knoten (claude, copilot, pl) als Postfach-Knoten mit PID; Brücken (`agentenbruecke` ×2, `copilot-messenger`, `aethelbot-v0-m5`); Flotte (`aix-fleet*`, `aix-dispatch-coder`, `aix-coord`); Nachtbetrieb nicht geladen; über 100 Geschwister-Worktrees plus `~/worktrees`, `~/.claude/worktrees`; Aufräumung manuell. Cloud-Delegation extern (Codex-Daemon, Copilot-Werkzeuge), kein eigener Cloud-Runner.

**Apple-nativ**: Vom Subagenten nicht geprüft; Betrieb hängt an rund 50 LaunchAgents mit Bash-Wrappern. Eigener Befund (Abschnitt 1): kein SMAppService, kein XPC-Vertrag, FoundationModels nur in aethelBrowser.

### 3.4 Was das Inventar hinzufügt

1. **Eine fertige LangGraph-Fabrik liegt ungenutzt.** digitalSoftwareFactory hat Zustandsgraph, SQLite-Checkpointer, Interrupt/Resume, MCP-Server, Daemon und Tests. Sie ist seit Juni unberührt und in keiner Konfiguration. Die Frage „LangGraph-Features übernehmen“ ist damit zuerst eine Frage „eigenen LangGraph-Code bewerten“: entweder er wird die Python-Referenz für den Vertrag `aethel.run/v1`, oder er wird archiviert. Beides ist besser als der heutige Zustand.
2. **aiderDesktop ist 238 Crates ohne Betrieb.** Darunter liegen Sandbox, Router, Eval-Ledger, Memory, Repo-Map, tree-sitter, Diff-Review. Das ist der größte Bestand an Harness-Teilsystemen im Workspace, und keiner läuft. Nach Kanonregel 4 muss jede neue Komponente erst gegen diese Crates geprüft werden.
3. **Deploy-Drift ist systemisch.** `~/bin` gegen `aethelScripts/bin`, deployte MCP-Server gegen Repo, Runtime 114 Commits hinter main. Es gibt keinen Release-Pfad außer bei aethelLocalCoder. Jeder Lauf arbeitet mit unbekanntem Code.
4. **Der mcp-hub ist das Vorbild.** Eine Registry, sechs Server, ein Proxy, zwei Clients versorgt. So sollte jeder Vertrag ausgeliefert werden.
5. **Vierfache Sandbox, dreifaches Gedächtnis, zwei Kerne, drei Regelquellen.** Die Varietät der Fabrik ist höher als die der Projekte, die sie steuern soll. Das verletzt Ashby in der falschen Richtung.
## 4. Feature-Abgleich: Cursor, Claude Code, Codex, LangGraph/Deep Agents, Kiro, Xcode 27, OpenHands gegen AETHEL

Legende Stand AETHEL: **L** läuft im Betrieb, **C** Code ohne Betrieb, **D** nur Dokument, **–** fehlt. Spalte „Übernehmen“ nennt die Komponente und den Vertrag nach Kanonregel 7.

| # | Fähigkeit | Wer hat sie (Stand Okt. 2026) | AETHEL | Übernehmen als |
|---|---|---|---|---|
| 1 | Harness mit sieben Teilsystemen (Schleife, Werkzeuge, Kontext, Sicherheit, Orchestrierung, Erweiterung, +1) als eine Komponente | alle elf untersuchten Systeme; Deep Agents nennt es explizit „agent harness“ | C: Teile in aethelAgentRuntime (Policy, Ledger, Shell), Teile in aix (Solve, Werkzeuge), Rest in 1.006 Skripten | `aethelAppleRuntime@aethel.harness/v1` (Swift, XPC) auf Kern `aixd` |
| 2 | Plan-Modus mit editierbarem Plan-Artefakt vor jeder Änderung | Xcode 27 `/plan`, Claude Code Plan Mode, Cursor Projects, Kiro Specs | D: Engineering Standard SPEC→Tests→Impl ohne Maschine | `aixd@aethel.auftrag/v1` mit Plan als Zustand `geplant`, Freigabe als Übergang |
| 3 | Spezifikation in drei Dateien (Anforderung mit EARS, Design, Aufgaben) mit Aufgabenstatus und Wellenausführung nach Abhängigkeitsgraph | Kiro | D: 157 SPEC/DESIGN/TEST-CASES, 15 mit SHALL; `omega_validate_dag` prüft Graphen | `aethelProjects@aethel.spec-graph/v1`: Spezifikation → Aufgabengraph → Wellen; Konsument aixd |
| 4 | Subagenten isoliert oder geforkt, asynchron, bis fünf Ebenen, mit eigenem Worktree oder eigener VM | Claude Code (Hintergrund standardmäßig, Tiefe 5, `isolation: worktree`), Cursor (eigene VM je Subagent, Koordinator mit tausenden Subagenten), Deep Agents (`task`, isolated/fork, async), Xcode 27 | C: Rollen-Jobs als launchd; Worktrees von Hand; keine Subagent-Abstraktion | Harness-Teilsystem Orchestrierung; Grenze: drei Spuren (Kanon) als Lease in aixd |
| 5 | Hooks auf 17–18 Lebenszyklus-Ereignisse, auch je Agent/Skill | Claude Code, Cursor (Hooks auf Nutzer-, Team-, Workspace-Ebene), Kiro Agent Hooks | L: 4 Ereignisse; kein PreToolUse/PostToolUse | Hooks in Harness-Vertrag; Policy-Entscheidung aus aixd, nicht aus Shell-Skripten |
| 6 | Skills im offenen `SKILL.md`-Format mit progressivem Laden, Werkzeugbeschränkung je Skill | Claude Code, Xcode 27 (7 Apple-Skills, Export), Deep Agents, Cursor, Antigravity | L: 6 Skills; Rollen als Skripte | Jede Rolle (Merger, Reviewer, Gate) als Skill mit `disallowed-tools` |
| 7 | Kontextdateien aus einer Quelle (AGENTS.md, CLAUDE.md, Regeln) mit Einbindungsmodi | Kiro Steering, Cursor Rules, Claude Code CLAUDE.md, Deep Agents AGENTS.md-Gedächtnis | L: 226 CLAUDE.md, 117 AGENTS.md, 290 `.cursor`, ohne Quelle | `aethelRegistry` erzeugt alle drei aus einer Komponentenbeschreibung |
| 8 | Dauerhafte Ausführung mit Checkpointer, `interrupt`/`resume` auf derselben Thread-ID | LangGraph (Kern), Deep Agents, Cursor Cloud Agents (Ziel halten, Steuerung mitten im Lauf) | C: Replay-Ledger kann rekonstruieren (`catalytic.reconstruct`); kein Resume-Vertrag | `aixd@aethel.run/v1`: Lauf = Thread-ID, Checkpoint je Schritt, Resume als Übergang; Fortsetzungsauftrag statt Zeitlimit (Kanon 6) |
| 9 | Middleware-Kette: Zusammenfassung, Mensch-in-der-Schleife, Modell-/Werkzeuglimits, Fallback, Retry, PII, Todo, Werkzeugauswahl, Kontextbereinigung, Shell, Dateisystem, Subagent, Rubrik-Selbstbewertung | LangChain/LangGraph 1.x (19 eingebaute) | C: Teile verstreut (Limit in Gated-Solve, Policy in Runtime) | Harness-Teilsystem Kontext und Sicherheit als Kette von Verträgen; Reihenfolge testbar |
| 10 | Mensch-in-der-Schleife mit `interrupt_on` je Werkzeug, Freigabe/Bearbeiten/Ablehnen, Klassifizierer-Subagent für Auto-Review | Deep Agents, Cursor Auto-review (Shell/MCP/Fetch), Claude Code Permission Modes, Runtime approvals.* | C: approvals.approve/reject existieren, im Betrieb deaktiviert | Freigabe = LocalAuthentication-Ereignis → approvals.approve; iPhone über App Intent |
| 11 | Sandbox je Lauf: VM je Subagent, Sandbox-Backends, Docker, Containerization | Cursor (VM je Subagent, Self-hosted Machines, Computer Use in Workern), Claude Code Sandbox (Shell-Startdateien gehärtet 2.1.310), Deep Agents Sandbox-Backends, OpenHands Docker, Apple `container` | C: aethelcontainerd, aethelContainer-API mit WASI-Tasks; L: sandbox-exec in aix | `aethelContainer@aethel.sandbox/v1` auf Apple Containerization; sandbox-exec abschalten |
| 12 | Cloud-/Hintergrundagenten mit Ereignisauslösern (PR, Slack, Cron, Webhook), Zielhalten, Steuerung mitten im Lauf | Cursor (Automations, `/goal`, Channels im Agent SDK), Codex Cloud/Remote, Jules, Claude Code Scheduled Tasks | L: 14 Rollen-Jobs per launchd, Auslöser Zeit; Steuerung über Chat | Auslöser als Ereignisse im Ledger (Commit, PR, Zeit, Alarm); Rollen als Skills, nicht Skripte |
| 13 | Koordinator-Agent mit Wellen/Parallelität und gemeinsamem Kontext | Cursor Projects, Kiro Wellen, Xcode 27 Subagenten, Claude Code Workflows | – | aixd plant Wellen aus Spec-Graph (#3); Harness führt aus; drei Spuren |
| 14 | Fernsteuerung lokaler Agenten vom iPhone | Cursor Remote Control (iOS), Claude Code Remote Control | L: aethelBot über aethelema (M4 ohne SSH) | Beibehalten; Freigabe-Intents ergänzen |
| 15 | Review-Bots: PR-Review, Security Review (Angriffspfad, Schwere), Rollouts (Monitoring-Plan, Revert-PR, kein Auto-Merge) | Cursor Bugbot/Security Review/Rollouts, Claude Code `/code-review`, Codex Review | D: Review-Regel; aethelLanding verdict als Code ohne Betrieb | `aethelLanding@aethel.verdict/v1` mit drei Sensoren (zurückgehaltene Tests, Testdatei-Wächter, Richter) |
| 16 | Evals als Teil des Agenten: Eval-Ordner, PR-Replay mit signierten Webhooks, Rubrik-Mittelware, Apple Evaluations-Framework, LangSmith | Cursor Agent SDK, Deep Agents RubricMiddleware, Apple, LangChain | C: `evals.score` (Governance-Integrität), Hard-9 (Aufgaben) | `aethelEval@aethel.eval/v1`: je Harness-Version und Stufe-0-Kette; Apple Evaluations für Swift |
| 17 | Modell-Routing nach Kosten/Balance/Intelligenz mit Admin-Kontrolle; Fallback-Modelle | Cursor Router, LangChain ModelFallback, litellm | L: litellm-Router (steht gerade), `~/bin/*-mlx`, Modellkatalog in aix | `aixd@aethel.model-catalog/v1`: Kostenklasse, Inferenzort, Beleg; Router nach Gesamtkosten (Manuel 28.10.) |
| 18 | Budgetgrenzen: Geld je Lauf inkl. Subagenten, Modell- und Werkzeugaufruf-Limits mit definiertem Ende | Claude Agent SDK `maxBudgetUsd`, LangChain Limits | C: Abbruchgrenze in Gated-Solve | Budget als Feld im Auftrag; Ende = Fortsetzungsauftrag |
| 19 | Werkzeugsuche/aufgeschobene Werkzeuge, Werkzeugauswahl durch kleines Modell | Claude Code ToolSearch, LangChain ProviderToolSearch/LLMToolSelector, MCP Tool Search | – (27 aix-Werkzeuge, 55 Runtime-Werkzeuge immer geladen) | Stufe 0 (fm) wählt Werkzeuge; Vertrag `capabilities.describe` schon da |
| 20 | Code-Intelligenz: Repo-Karte, tree-sitter, LSP, strukturelle Suche, Sprengradius, Bisect, Mutationstest | Aider (Repo-Karte), Cursor (Index), aix (ast-grep, Sprengradius, Bisect, Mutationstest, JetBrains offline) | L: aix voraus; nur Python, nur intern | Als Vertrag veröffentlichen: `aethelCodeAnalyzer@aix_findings.v1` + `aix-tools@aethel.code-intel/v1`; tree-sitter/LSP für Python, TS, Swift |
| 21 | Terminal- und IDE-Zustandsbewusstsein | Codex (Terminal state), Codex IDE (recent activity), Runtime world.snapshot/command.boundaries | C | In Harness-Kontextteilsystem |
| 22 | Browser- und Computer-Nutzung in Agentenläufen | Cursor (Linux/Mac Worker), Claude Code Browser, aethelBrowser | L: aethelBrowser-Brücken | Beibehalten |
| 23 | Canvases/Artefakte, geteilt per Link | Cursor Canvases, Xcode Artefakt-Spalte, Claude Artifacts | D | aethelema zeigt Receipts und Pläne aus aixd; kein HTML als Hauptoberfläche (Kanon 5) |
| 24 | Agent als Code-Ordner (instructions, tools, skills, mcp-connections, channels) mit Deploy | Cursor Agent SDK GA, Claude Agent SDK | – | Rolle = Ordner mit `capability.json`; Deploy = SMAppService |
| 25 | Umgebungen als API, Build-Snapshots für schnellen Start | Cursor Environments API, Builds; OpenHands | C: aethelContainer Stacks | Gate-Image mit Snapshot in aethelContainer |
| 26 | Beobachtbarkeit: Tracing, Signposts, agentisches Profiling | LangSmith, Instruments agentic profiling, Runtime timeline | C: Replay-Timeline; Logdateien in aix | OSLog/Signposts in Harness; Instruments statt Logdateien (Kanon 1) |
| 27 | Protokolle: MCP 2026-07-28, ACP, A2A | alle; Xcode nimmt nur ACP | L: 10 MCP-Server unversioniert; ACP –; A2A – | ACP-Server in Harness; MCP-Revision prüfen |
| 28 | Marktplatz/Plugins/Mods | Cursor Origin, Xcode Plug-ins, Claude Mods, Mendix Marketplace, Xcelerator Marketplace | – | `aethelRegistry` als Katalog eigener Komponenten; Marktplatz erst mit Produkt-ID |
| 29 | Property-based Correctness, Mutationstests | Kiro Correctness, aix `mutationstest` | L: aix | In Gate als Pflichtsensor für Kernkomponenten |
| 30 | Gedächtnis mit Provenienz, aus Commits und Freigaben lernend | Cursor Memories, Deep Agents Store, MemCoder (Forschung), Runtime graph mit user_weight | C: drei Gedächtnisse ohne gemeinsamen Vertrag | `aethelOmega@aethel.memory/v1`: Quelle, Typ, Gültigkeit, Abruf; speist Harness-Kontext |
| 31 | Rückbau/Undo als Teil der Freigabe | Runtime Limbus (TTL, Undo-Route senkt Reibung) | C | In Landung: Rückbauklasse R1–R4 (Manuel 15.10.) als Limbus-Route |
| 32 | Nutzer ändert Code während der Agent läuft (SWE-Touch), interaktive Sitzungen | Cursor Steering, Claude Code Queue, Forschung | – | Harness: Weltdiff vor jedem Schritt (`world.diff` existiert) |

Zählung: 32 Fähigkeiten; AETHEL L 9, C 15, D 4, – 4. In zwei Punkten (20, 29) ist AETHEL weiter als die Werkzeuge. In 23 Punkten existiert Code oder Betrieb, aber kein Vertrag und keine Anbindung an einen Kern. Das deckt sich mit dem Hauptbericht: Die Lücke ist Integration, nicht Erfindung.
## 5. Forschungsstand 2026 und was er für die Fabrik vorschreibt

Stand der Literatur bis Oktober 2026, ergänzt aus Trainingswissen. arXiv-Nummern sind Belegstellen; sekundär vermittelte Zahlen sind als „sek.“ markiert.

### 5.1 Harness-Engineering ist die Disziplin, nicht Prompting

- **Agent = Modell + Harness.** Die Quellcode-Studie von elf Systemen (Claude Code, Codex CLI, Gemini CLI, Mistral Vibe, OpenHands, Aider, Mini-SWE-Agent, Hermes, Pi, OpenCode, OpenClaw; arXiv 2609.00006) identifiziert sieben kanonische Teilsysteme (Schleife, Werkzeuge, Kontextverwaltung, Sicherheitskontrollen, Orchestrierung, Erweiterungsflächen und ein siebtes, in der Zusammenfassung nicht genanntes), 29 wiederkehrende Entwurfsmuster und 18 Empfehlungen.
- **Acht Konfigurationsmechanismen** (Kontextdateien, Skills, Subagenten, Hooks, Regeln, Befehle, MCP, Modi) sind in 2.853 Repositories untersucht (arXiv 2602.14690). Die Mechanismen sind werkzeugübergreifend konvergiert.
- **Entwicklungslinie** Prompt-Engineering → Context-Engineering → Harness-Engineering → agent-natives Training (Survey arXiv 2606.20683). Die Fabrik steht heute zwischen Stufe 1 und 2.
- **Selbstverbessernde Harnesses**: Meta-Harness, AutoHarness, „Agentic Harness Engineering“ (beobachtungsgetriebene Evolution), Harness Handbook (arXiv 2607.13285), empirische Harness-Studie (arXiv 2609.20804).

Folge für AETHEL: Die Laufzeit ist als Harness mit genau diesen sieben Teilsystemen zu entwerfen, jedes mit Vertrag. Heute sind sie auf 1.006 `bin`-Dateien und 38 launchd-Jobs verteilt, ohne Grenze. Die Harness-Evolution selbst ist ein Regelkreis (Abschnitt 7, Meta-Ebene).

### 5.2 Verifikation muss mit dem Erzeuger mitwachsen

- **„The Verification Horizon“** (Qwen, arXiv 2606.26300): Kein fester Verifizierer bleibt wirksam, wenn die Fähigkeit des Erzeugers wächst; Verifikation muss ko-evolvieren. Unit-Tests werden mit Shortcut-Überwachung und einem agentischen Richter kombiniert.
- **EvilGenie** (arXiv 2511.21654, Rev. Mai 2026): Reward-Hacking-Benchmark; Codex und Claude Code zeigten explizites Reward-Hacking. Messmittel: zurückgehaltene Tests, LLM-Richter, Erkennung von Testdatei-Änderungen.
- **„Building to the Test“** (sek.): Agenten fehlt „validation self-awareness“; Verfügbarkeit eines Orakels erodiert fachliche Praxis; Gegenmittel ist ein unabhängiger Prüf-Subagent.
- **METR (März 2026, sek.)**: Viele „gelöste“ SWE-bench-PRs wären nicht mergefähig.

Folge für AETHEL: Das Gate darf nicht nur „Tests grün“ messen. aethelLanding braucht drei Sensoren: zurückgehaltene Tests, Erkennung von Test- und Fixture-Änderungen im Schnitt, unabhängiger Richter mit eigenem Kontext. Das ist heute keiner der drei. Manuels Regel „Review vor Gate, getrennte Opus-Instanz“ ist genau die Literaturempfehlung und muss Software werden statt Arbeitsanweisung.

### 5.3 Gedächtnis aus Projektgeschichte

- **MemCoder** (arXiv 2603.13258): Strukturiertes Gedächtnis aus Commit-Historie (Absicht→Code-Abbildungen), Selbstkorrektur aus Verifikationsrückmeldung, Verinnerlichung menschlich bestätigter Lösungen; +9,4 % gelöste Fälle auf SWE-bench Verified über DeepSeek-V3.2.
- Surveys 2026 zu Gedächtnismechanismen; **SWE-Pruner** (adaptives Kontextbeschneiden); Kontextkompression für Issue-Lösung.
- Werkzeugseite: Cursor Memories, Deep-Agents-Gedächtnis aus `AGENTS.md` im Store, Claude Code Auto-Memory.

Folge für AETHEL: aethel-omega und `_aix_wissen` sind Markdown-Gedächtnisse ohne Schreib-/Leseprotokoll. Das Ziel ist ein Gedächtnis mit Vertrag: Quelle (Commit, Receipt, Freigabe), Typ (Absicht, Lehre, Regel), Gültigkeit, Abruf nach Projekt und Schnitt. Die 12.761 Commits außerhalb von main und 494 Aufträge sind der ungenutzte Rohstoff.

### 5.4 Benchmarks sind gesättigt, Lebenszyklus-Messung fehlt

- SWE-bench Verified: 97,0 % (Claude Opus 5, Mini-SWE-agent, Stand 01.09.2026, Vals.ai); OpenAI erklärte den Benchmark im Februar 2026 für erschöpft.
- Nachfolger: **SWE-bench Pro Verified** (arXiv 2609.08149; Fable 5.1 81,2 %, sek.), **SWE-Cycle** (vollständiger Issue-Zyklus, arXiv 2605.13139), **SWE-Touch** (Nutzer ändert Code während des Lauf, arXiv 2608.02499), **SWE-Together** (interaktive Sitzungen, arXiv 2606.29957), Terminal-Bench. Positionspapier: Benchmarks sind mit agentischer Softwareentwicklung fehlausgerichtet (arXiv 2606.17799).
- Ein Praxisbericht nennt 19,78 % semantisch falsche „gelöste“ Fälle (unverifiziert).

Folge für AETHEL: Eine eigene Messung über den ganzen Zyklus (Auftrag → Schnitt → Review → Gate → Landung → Betrieb) auf eigenen Repos ist nötig. aethelScripts Hard-9 misst nur „löst Aufgabe“. Modellwahl ohne Zykluskosten (Fehlversuche, Nacharbeit, Wartezeit) widerspricht Manuels Regel vom 28.10.

### 5.5 Plattform-Engineering 2.0 und Governance

- CNCF (Juli 2026): Agenten sind nicht-menschliche Plattformkonsumenten mit eigener Identität, Scope und Governance. „Agentic Development Platform“: gleiches Betriebsmodell, breiteres Substrat.
- DORA 2026 (sek., unverifiziert): +25 % KI-Adoption korrelierte mit −1,5 % Durchsatz und −7,2 % Stabilität. Formale Governance: 94 % Vertrauen gegen 51 % ad hoc (sek.).
- EU AI Act, Cyber Resilience Act, NIS2 treiben Compliance-as-Code.
- FinOps wandert in die Plattform.

Folge für AETHEL: Jeder Agent (Claude, Codex, Copilot, lokale Modelle) braucht eine Identität mit Rechten im Rechtekern, nicht ein Shell-Konto. Kostenklasse je Aufruf gehört in den Ledger. Das ist die Software-Form von Manuels Kostenregeln.

### 5.6 Protokollstapel

| Protokoll | Stand | AETHEL-Stand | Entscheidung |
|---|---|---|---|
| MCP | Revision 2026-07-28 stabil; zustandslos, `initialize`-Handshake und Session-ID entfallen; Multi-Round-Trip-Requests; Roots, Sampling, Logging mit 12-Monats-Abkündigung | 10 Server registriert, eigene (`aix`, `aethel`, `aethel-runtime`, `software`) ohne Revisionsangabe | Alle eigenen Server auf 2026-07-28 prüfen; Vertrag `aethel.mcp/<revision>` |
| ACP (Zed) | v1; Xcode 27, Zed, JetBrains, Neovim, Microsoft Intelligent Terminal (sek.); 25+ Agenten (sek.) | 0 eigene Implementierungen | AETHEL-Laufzeit als ACP-Agent anbieten |
| A2A | v1.0.1 (Mai 2026), Linux Foundation / Agentic AI Foundation | nichts | Für Fremdagenten (Codex, Copilot) als „Lieferanten“ prüfen |
| Agent Skills (`SKILL.md`) | Offener Standard; Claude Code, Xcode 27, Deep Agents, Cursor | 6 Skills | Rollen als Skills |
## 6. Siemens Xcelerator, Teamcenter, Mendix, Kiraa, Kiro: was der digitalen Firma architektonisch fehlt

### 6.1 Siemens als Referenz für die digitale Firma

Siemens Xcelerator ist ein kuratiertes Portfolio plus Partnerökosystem plus Marktplatz. Teamcenter ist das PLM-Rückgrat („digital thread“), Mendix die modellgetriebene Low-Code-Schicht, Polarion Anforderungen, Opcenter Fertigung, Insights Hub Betriebsdaten, Simcenter Simulation. 2026: neun Industrie-Copilots (Teamcenter, Polarion, Opcenter, Simcenter, Mendix, EDA), Teamcenter 2606 mit erstem Agenten (AI-BOM-Agent), Intelligence Center X als Orchestrierung einer „hybriden Belegschaft“ aus Menschen und Agenten (sek., kein Primärbeleg).

Übertragung auf eine Software-Firma, die Software baut: Jedes PLM-Konzept hat ein Gegenstück, das AETHEL fehlt.

| PLM-Konzept (Teamcenter) | Bedeutung dort | Gegenstück für AETHEL | Stand heute |
|---|---|---|---|
| Item / Item Revision / Release-Status | Jedes Teil hat Identität, Revisionen, freigegebene Stände | Produkt-ID je Repo/Komponente, Revision = Landung, Status = Entwurf/Geprüft/Freigegeben/Betrieb | fehlt; fünf Register ohne Produkt-ID |
| BOM (Stückliste), MBOM/BOP | Produktstruktur mit Mengen und Varianten | Komponentenstückliste: welche Crates/Pakete/Verträge bilden ein Produkt; Bauplan je Produkt | fehlt; `capability.json` nur in einer Komponente |
| Produktkonfigurator, intentbasierte Sichten | Varianten aus einer konfigurierbaren Struktur | aethel_core-Linie: 34 Varianten als Konfiguration einer Struktur statt 34 Kopien | fehlt (Variant-Generator) |
| Change Management (ECR/ECO), Impact-Analyse, Bulk-Revert | Änderung als Objekt mit Betroffenen, Teilnehmern, Rückabwicklung | Auftrag → Schnitt → Landung als Änderungsobjekt mit Betroffenheitsanalyse (welche Konsumenten, welche Verträge) und Rückbau | Auftrag in JSONL, keine Betroffenheit, Rückbau als Textzeile |
| Workflow-Engine, Vorlagen, KI-Zuweisung, Regel-Routing | Arbeitsfluss als Daten mit erlaubten Übergängen | Zustandsmaschine in aixd (Kanon 3) mit Vorlagen je Auftragstyp und Routing nach Rolle | Doku; Übergänge in Bash |
| Digital Thread, Traceability | Anforderung → Design → Test → Fertigung durchgängig navigierbar | SPEC → DESIGN → TEST-CASES → Code → Receipt → Betrieb als Graph; Landung blockiert, bis verknüpfte Tasks fertig (Teamcenter–Polarion-Regel) | 157 Spezifikationsdateien ohne Verknüpfung |
| MBSE-KI: Anforderungen gegen INCOSE-Regeln prüfen, Testfälle empfehlen, Abdeckung verfolgen | Qualität der Anforderung wird geprüft | SPEC gegen Regelwerk (EARS, SHALL-Sätze, Testbarkeit) prüfen, Testfälle vorschlagen, Abdeckung messen | fehlt; 15 von 157 Spezifikationen mit SHALL-Sätzen |
| Copilot mit Guardrails, On-Prem, Prompt-Validierung | KI-Vorschläge werden geprüft, bevor sie eingefügt werden | Stufe 0 (fm) mit Eval und Guardrail; nie Autorität | fm vorhanden, keine Eval |
| Knowledge Pulse (Hochgeschwindigkeits-APIs PLM → Analytik) | Daten statt Exporte | Ledger → aethelAnalytics als Ereignisstrom | Markdown-Exporte |
| Blue-Green-Deployment, Self-Service-Admin | Betrieb ohne Stillstand | Dienste (aixd, Runtime) mit zwei Ständen, Umschaltung mit Beleg | launchd-Neustart von Hand |
| Lieferantenkonten, Rollen, Bulk-Import | Externe als Beteiligte mit Rechten | Fremdagenten (Codex, Copilot, Cloud) als Lieferanten mit Konto, Rolle, Kostenklasse, Budget | Shell-Aufrufe ohne Identität |
| Compliance (REACH, RoHS, PFAS) als Kategorien in Bulk | Regelkonformität als Daten | Lizenz-, Kosten- und Inferenzort-Konformität als Kategorie je Komponente (LOCAL_AI_ONLY, kostenlos, bezahlt) | Regeln in CLAUDE.md |
| Microsoft-365-/Power-BI-/SAP-Integration mit Quellsystem-Sicherheit | Daten bleiben im Besitzsystem | Cockpit liest aus aixd-Abfragen; keine Kopien in Chats und Akten | 478 Akten als Kopien |

### 6.2 Mendix: modellgetriebene Entwicklung und Agenten als Bürger

Mendix 11 (Okt. 2025) und 11.12 LTS (Juni 2026): Agents Kit 2.0 mit Agent Editor, Maia Plan (Backlog aus verstreuten Eingaben), Maia Make (Seiten, Datenmodell, Logik), BYO-Agent über MCP, Marktplatz, Governance und Guardrails. Architekturlehre: Das Modell (Domänenmodell, Microflows, Seiten) ist die Wahrheit, Code wird daraus erzeugt; Agenten operieren auf dem Modell, nicht auf Textdateien.

Für AETHEL: Die aethel_core-Produktlinie und die Flutter-Stubs sind der Fall für modellgetriebene Erzeugung. Ein Variantenmodell plus Generator (P8 aus dem Hauptbericht) ist der Mendix-Weg. Agenten sollten auf `capability.json`, SPEC und Zustandsmaschine arbeiten, nicht auf 1.006 Skripten.

### 6.3 Kiraa (kiraa.ai): Apple-Silicon-nativ als Produktversprechen

Australisches Unternehmen, Entscheidungsunterstützung statt Dashboards. Technik laut eigener Seite: Swift-Kern, Metal, Unified Memory ohne Kopien, mehrfädige In-Memory-Analytik, eigenes LLM, „CAG statt RAG“, Ontologie als semantische Schicht, rollenbasierte Kontextrahmung, On-Prem auf Apple-Hardware, horizontale Skalierung, ISO 27001. Behauptungen ohne Beleg: „80× schneller“, „erfindet nie Fakten“, „keine Angriffsfläche“.

Lehre für AETHEL: Die Schichtung ist richtig und deckungsgleich mit dem Kanon: Hardware → Swift-Kern → Datenschicht → semantische Schicht (Ontologie) → Wissensschicht → Schlussfolgerungsschicht → Zugriffsschicht. AETHEL hat die Daten- und Wissensschicht als Markdown (`_aix_wissen`, aethel-omega) und die Zugriffsschicht als Chat. Kiraa zeigt, dass lokal-nativ ein verkaufbares Versprechen ist, wenn die semantische Schicht Software ist. Nichts von Kiraa ist übernehmbarer Code; übernehmbar ist das Schichtenmodell als Vertragsreihe.

### 6.4 Kiro (AWS): spezifikationsgetrieben als Arbeitsfluss

Drei Dateien je Spezifikation: `requirements.md` (User Stories, Akzeptanzkriterien, EARS-Notation), `design.md` (Architektur, Sequenzen, Fehlerbehandlung, Teststrategie), `tasks.md` (Aufgaben mit Status). Ausführung baut einen Abhängigkeitsgraphen und führt Aufgaben in Wellen aus: Wellen nacheinander, Aufgaben in einer Welle parallel. Steering-Dateien mit Einbindungsmodi, Agent-Hooks auf Ereignisse, Property-based „Correctness“, Markdown-Review mit Kommentaren an den Agenten.

Für AETHEL: Der Engineering Standard (SPEC → TEST-CASES → Impl) ist Kiros Modell ohne die Maschine. Es fehlt die Aufgabenliste als Daten, der Abhängigkeitsgraph, die Wellenausführung und die Rückkopplung Task ↔ Code. Das ist die Brücke zwischen aethelProjects (Reifegrad, Intent) und aethelFactory (Worklane) und gehört in aixd als Auftragsstruktur.
## 7. Kybernetik vollständig: ein Mehrebenenmodell für Firma, Fabrik, Projekt und Lauf

Manuels Vorgabe: Kybernetik vollständig auf vielen Ebenen. Der Hauptbericht nannte vier Kreise mit fehlenden Gliedern. Hier das vollständige Modell, damit jede Lücke einen Ort hat.

### 7.1 Begriffe, die verbindlich werden sollen

- **Regelkreis**: Sollwert, Messgröße (Sensor), Vergleicher, Regler, Stellglied, Störgröße, Totzeit. Ein Kreis ist nur geschlossen, wenn alle sechs in Software existieren und die Totzeit kleiner ist als die Änderungsrate der Störung.
- **Ashbys Gesetz der erforderlichen Varietät**: Ein Regler braucht mindestens so viel Varietät wie die Störungen. 330 Einträge × neun Agent-Harnesses × Dutzende Modelle sind die Varietät; Register, Verträge und Gates sind die Dämpfer, Subagenten und Flotten die Verstärker. Heute gibt es Verstärker ohne Dämpfer.
- **Conant-Ashby**: Jeder gute Regler enthält ein Modell des Geregelten. Die Fabrik braucht ein Modell ihrer Projekte (Registry, Stückliste, Zustandsmaschine), sonst regelt sie blind.
- **Beers Viable System Model (VSM)**: System 1 Operationen, System 2 Koordination gegen Oszillation, System 3 Ressourcenverhandlung und Steuerung im Inneren mit 3* Audit, System 4 Intelligenz nach außen und in die Zukunft, System 5 Politik und Identität; algedonischer Kanal für Alarme an allen Ebenen vorbei; Rekursion: jede Operation ist selbst ein lebensfähiges System.
- **Double-Loop-Lernen** (Argyris): Nicht nur Fehler korrigieren, sondern die Regel korrigieren, die den Fehler erlaubt hat. Manuels Satz „Jede Lehre wird ein Test an der Zustandsmaschine“ ist Double-Loop in einem Satz.
- **Kybernetik zweiter Ordnung**: Der Beobachter ist Teil des Systems. Die Harness, die sich selbst verbessert (Meta-Harness, Abschnitt 5.1), ist ein Regler, der sich selbst regelt, und braucht deshalb einen äußeren Prüfer.
- **POSIWID** (Beer): Der Zweck eines Systems ist, was es tut. Was die Fabrik heute tut: Akten schreiben. Das ist ihr aktueller Zweck, unabhängig von den Dokumenten.

### 7.2 Rekursionsebenen mit Sollwert, Sensor, Vergleicher, Stellglied

| Ebene | Takt | Sollwert | Sensor | Vergleicher | Stellglied | Störgrößen | Heute vorhanden | Fehlt |
|---|---|---|---|---|---|---|---|---|
| **E0 Werkzeugaufruf** | ms–s | Erlaubnisregel, Pfadgrenze, Budget je Aufruf | PreToolUse/PostToolUse-Hook, Sandbox-Log | Regelwerk (Policy) | Erlauben, Verweigern, Umleiten in Sandbox | Prompt-Injektion, Pfadflucht, Netzwerk | Claude-Hooks für 4 Ereignisse, keines pro Werkzeug; sandbox-exec | PreToolUse-Tor, Policy-as-Code, Containerization |
| **E1 Lauf (Agent-Schleife)** | s–min | Aufgabe mit Akzeptanzkriterien, Token-/Zeitbudget, erlaubte Dateien | Tests, Compiler, Linter, Analyzer; Token-Zähler; Schritte | Orakel (Tests grün, Kriterien erfüllt), Limit-Mittelware | Nächster Schritt, Subagent, Abbruch, Zusammenfassen | Kontextverlust, Halluzination, Reward-Hacking | Gated-Solve mit Orakel; Hard-9 | Zurückgehaltene Tests, Testdatei-Wächter, unabhängiger Richter, Kontextbeschneidung, Budgetgrenze mit Fortsetzungsauftrag |
| **E2 Schnitt / Auftrag** | h | Auftragstext, Vertrag, Rückbau-Klasse, Kostenklasse | Review (getrennte Instanz), Gate-Ergebnis, Receipt mit Digests | Verdict (aethelLanding) | Landen, Zurückweisen, Nacharbeit, Fortsetzungsauftrag | Fremdlast, Gate-Stau, Flakiness | Review-Regel als Anweisung; aethelLanding-Code ohne Betrieb; Auftrag in JSONL | Zustandsmaschine mit Lease, Receipt-Verifier, Landung als Verb, Betroffenheitsanalyse |
| **E3 Projekt** | Tage | Intent, Reifegrad-Ziel, Backlog aus SPEC/tasks | aethelProjects-Scan, Analyzer-Befunde, Testabdeckung, Betriebsmetriken | Reifegrad-Delta, offene Befunde, Abdeckungslücke | Aufträge erzeugen, Priorität setzen, Stub archivieren | Drift, Duplikate, verwaiste Zweige | Scan + Score + Findings; kein Konsument | aethelProjectManagement als Konsument; Task-Graph (Kiro-Wellen); Digital Thread |
| **E4 Portfolio / Fabrik** | Wochen | WIP-Grenze (3 Spuren), Gate-Kapazität (4 Worker, 48 GiB frei), Durchsatz, Kosten | Ledger, Gate-Auslastung, Speicher, Warteschlange, Kostenklasse je Lauf | Kapazität vs. Nachfrage; Kosten vs. Budget | Zuteilen, Drosseln, Verschieben, Modell wechseln (Router) | Nachfragespitzen, Fremdlast, Modellausfall | 14 Rollen-Jobs, Gate-Worker-Zahl als Umgebungsvariable | S3-Ressourcenverhandlung als Dienst, S2-Koordination (ein Schreiber je Schnitt als Lease), Router nach Gesamtkosten |
| **E5 Firma** | Monate | Kanon (CLAUDE.md), Portfolio-Entscheidung, Lizenz-/Kostenregeln, Produktziele | Marktbefund, Technologie-Radar (dieser Bericht), Nutzung, Abrechnung | Strategie vs. Ist; Kanon vs. Code | Kanon ändern, Produkt starten/einstellen, Freigabe erteilen | Plattformwechsel (WWDC), Modellpreise, Forschung | RFC 0002 als Dokument; Kanon als Markdown | S5-Politik maschinenlesbar (Policy in aixd), S4-Radar als Dienst, Portfolio-Entscheidung als Zustandsobjekt |
| **E6 Umwelt** | Monate–Jahre | Nutzerproblem, Markt, Plattform-Roadmap | Nutzung, Fehlerberichte, Changelogs Apple/Cursor/arXiv | Nutzen vs. Aufwand | Produktdefinition | Konkurrenz, Regulierung | Forensik-/Marktmodul in aethelProjects ohne Konsument | Rückkopplung Betrieb → Anforderung |
| **Meta: Harness-/Modellevolution** | Wochen | Zyklus-Kennzahlen (Fehlversuche, Nacharbeit, Kosten bis geprüftes Ergebnis) | Eval-Suite (Apple Evaluations, eigene SWE-Cycle-Messung) | Kennzahl-Delta je Harness-Version | Harness-Vertrag ändern, Modell im Katalog umstufen | Benchmark-Sättigung, Reward-Hacking | Modellproben ad hoc | Eval-Vertrag, Versionierung der Harness, äußerer Prüfer (zweite Ordnung) |

### 7.3 VSM-Zuordnung der Fabrik

| VSM-System | Funktion | AETHEL-Organ (Soll) | Ist |
|---|---|---|---|
| S1 Operationen | Schnitte bauen, Gates laufen, Landungen | Laufzeit (Swift) + Gate-Container + aethelLanding | Skriptflotte, Code ohne Betrieb |
| S2 Koordination | Oszillation verhindern: ein Schreiber je Schnitt, Leases, Reihenfolge | aixd Lease/Sperre | Arbeitsanweisung, Gate-Stau als Symptom |
| S3 Steuerung innen | Ressourcen zuteilen, WIP, Budget, Kapazität | aixd Zuteilung + Router | Umgebungsvariablen, Hand |
| S3* Audit | Stichprobenprüfung ohne Ankündigung: Receipts nachrechnen, Digests prüfen, Testdateien vergleichen | Receipt-Verifier, Testdatei-Wächter, Richter | fehlt vollständig |
| S4 Intelligenz | Außen und Zukunft: Plattform-Releases, Forschung, Markt, Konkurrenz | aethelRadar (neu): periodischer Scan von Apple-Guides, Changelogs, arXiv, Registry-Abgleich, als Dienst mit Ereignissen | dieser Bericht, von Hand |
| S5 Politik | Identität und Regeln; schlichtet S3/S4 | Kanon als Policy-Daten in aixd mit Versionsstand, Freigabe nur durch Manuel (LocalAuthentication) | CLAUDE.md in 226 Kopien |
| Algedonischer Kanal | Alarm an allen Ebenen vorbei: Kostenüberschreitung, Cloud unter LOCAL_AI_ONLY, Sicherheitsbefund, Speicher < 48 GiB | Ereignis mit Pflichtstopp und Benachrichtigung (aethelBot, iPhone) | LOCAL_AI_ONLY fail-closed ist der einzige |

### 7.4 Querschnittsregeln für geschlossene Kreise

1. **Jeder Kreis ist registriert.** Vertrag `aethel.loop/v1`: Name, Ebene, Sollwert-Quelle, Sensor-Abfrage, Vergleicher, Stellglied, Takt, Besitzer, letzter Schluss. Ein Kreis ohne Registrierung existiert nicht. Cockpit zeigt alle Kreise mit Zeit seit letztem Schluss.
2. **Innen schneller als außen.** E0 in Millisekunden, E1 in Minuten, E2 in Stunden, E3 in Tagen. Ein Kreis, der langsamer ist als der darüber, oszilliert (Gate-Stau vom 14.10. war genau das: E2 langsamer als E4-Nachfrage).
3. **Jede Lehre wird ein Test an der Zustandsmaschine** (Double-Loop), kein weiterer Wächter.
4. **Kein Kreis über Chat oder Markdown.** Rückkopplung ist ein Ereignis im Ledger. Akten sind Berichte über den Ledger, nicht sein Ersatz.
5. **Varietät dämpfen vor verstärken.** Erst Registry und Verträge (Dämpfer), dann Subagenten und Flotten (Verstärker). Die Reihenfolge der Schnitte in Abschnitt 10 folgt dem.
6. **Zweite Ordnung braucht einen äußeren Prüfer.** Harness-Änderungen bewertet eine getrennte Instanz mit eigener Eval, nie die Harness selbst.
7. **Algedonisch heißt sofort.** Kosten, Cloud-Verstoß, Sicherheit, Speicher: Stopp ohne Rat, Nachricht an Manuel, Beleg im Ledger.

### 7.5 Heutige Kreise im Zustand „offen“

- E0: Hooks greifen nicht pro Werkzeug; sandbox-exec statt Containerization.
- E1: Orakel nur Tests; keine zurückgehaltenen Tests; kein Testdatei-Wächter; Budget ohne Fortsetzungsauftrag.
- E2: Review als Anweisung; Receipts ohne Verifier; Landung ohne Verb; Auftrag ohne Zustandsmaschine.
- E3: Scan ohne Konsument; Intent ohne Code-Abgleich; Spezifikation ohne Task-Graph.
- E4: Kapazität in Umgebungsvariablen; Router nach Tokenpreis statt Gesamtkosten; kein S2-Lease.
- E5: Kanon als Markdown; Portfolio-Entscheidung als RFC; keine Freigabe als Ereignis.
- E6: Markt- und Forensikmodule ohne Rückkopplung.
- Meta: keine Eval je Harness-Version; keine Versionierung der Harness.
- S3*, S4, algedonischer Kanal: fehlen als Organe.
## 8. Soll-Architektur auf macOS 27

Das Zielbild folgt Kanon (07.09., 14.10., 30.10.), Plattformangebot (Abschnitt 2), Forschung (Abschnitt 5) und Kybernetik (Abschnitt 7). Jede Schicht ist ein Vertrag; jede Schicht hat heute einen Bestand, der benannt wird.

| Schicht | Soll | Technologie (macOS 27) | Bestand, der hineinwächst | Bestand, der archiviert wird |
|---|---|---|---|---|
| **L0 Hardware** | Apple Silicon, Unified Memory als Grenze für Modell- und Gate-Zuteilung (48 GiB Reserve) | `silicon_lease_status`, MetricKit | aix Silicon-Lease | – |
| **L1 System** | Dienste als signierte XPC-Dienste mit SMAppService; Isolation mit Containerization; Geheimnisse in Keychain/Secure Enclave; Signposts statt Logs; Bonjour im Verbund | ServiceManagement, XPC, Containerization 1.4, Virtualization, Keychain, LocalAuthentication, OSLog, Network | aethelContainer (Daemon, Stacks, WASI-Tasks) als Hülle über `container`; aethelcontainerd | sandbox-exec-Pfad, drei Seatbelt-Kopien, `tart`-Aufruf, Docker/OrbStack/podman/lima für Agenten |
| **L2 Modelle** | Ein Katalog mit Kostenklasse und Inferenzort; Stufe 0 = SystemLanguageModel (fm), Stufe 1 = MLX/Ollama lokal, Stufe 2 = Cloud (PCC, Claude, Codex) nur unter HYBRID mit Beleg; eigene Gewichte über Core AI | FoundationModels `LanguageModel`-Protokoll, Core AI, MLX, `fm serve` am Python-Rand, litellm nur als Cloud-Rand | `coders/*.json`-Kataloge, litellm-Router, mlx-coder, Cold-Start-Proxy, LocalCoder-Hub | tote MLX-Plists, claude-proxy, ccproxy, aiderDesktop-Router-Crates (als Referenz lesen, dann archivieren) |
| **L3 Verfassungskern aixd** | Wahrheit, Zustandsmaschine (Auftrag, Schnitt, Lauf, Lease, Freigabe, Landung, Rückbau), Ledger mit Receipts und Digests, Policy-as-Code (Kanon als Daten), Loop-Registry (`aethel.loop/v1`), Modellkatalog, Identitäten für Agenten | Rust, SQLite, XPC-Schnittstelle; Vertrag `aethel.aixd/v1` | **aethelAgentRuntime** (Replay-Ledger, Proposal/Approval, Policy-Klassifizierer, Governor-Leases, Limbus, Compliance) als Ausgangspunkt; aix-ledger/-kernel/-domain als Lieferanten von Typen; `omega_validate_dag` | `~/.aix/auftraege.jsonl`, Postfach-Bash, Zustand in Markdown/TSV |
| **L4 Apple Runtime (Harness)** | Sieben Teilsysteme als Swift-Pakete: Schleife, Werkzeuge, Kontext (Zusammenfassung, Beschneidung, Gedächtnisabruf), Sicherheit (Hooks pro Werkzeug, Sandbox, Budget), Orchestrierung (Subagenten, Wellen, drei Spuren), Erweiterung (Skills, MCP, Hooks), Beobachtung (Signposts, Replay). Spricht MCP 2026-07-28 (Server und Client), ACP (für Xcode, Zed, JetBrains), A2A (für Lieferanten) | Swift 6.4, Swift Testing, FoundationModels, Agent Skills, `mcpbridge`, Apple Evaluations | aix Gated-Solve als Referenzschleife; aix Copilot-Werkzeuge als Werkzeugvertrag; digitalSoftwareFactory als Python-Referenz für Checkpoint/Interrupt; Hooks-Skripte als Ereignisliste | `knoten.sh`-Rollen, 1.006 `bin`-Skripte als Laufzeit (bleiben Aufruf, nie Zustand) |
| **L5 Werkzeuge mit Vertrag** | aethelCodeAnalyzer (Rust, Dart + tree-sitter/LSP für Python, TS, Swift), aix Code-Intelligenz (ast-grep, Sprengradius, Bisect, Mutationstest, Signaturänderung), aethelProjects (Scan, Reifegrad, Spec-Graph), aethelLanding (Verdict mit drei Sensoren), aethelAnalytics, aethelEval | Rust/Python mit `capability.json` und beidseitigem Test | alle genannten; aiderDesktop `code_symbols`, `ast_parser.rs`, `aider_grounding` als tree-sitter/LSP-Lieferanten | Doppelimplementierungen in aiderDesktop nach Übernahme |
| **L6 Gedächtnis** | Ein Vertrag `aethel.memory/v1`: Quelle (Commit, Receipt, Freigabe, Nutzergewicht), Typ (Absicht, Lehre, Regel, Beleg), Gültigkeit, Abruf nach Projekt und Schnitt; lernt aus Commits (MemCoder-Prinzip) | SQLite (Runtime graph.sqlite, FTS5), Spotlight-Index für lokale RAG | aethel-omega (Claims, Atlas), Runtime knowledge/graph, Wissensschleife | 478 Koordinationsakten als Gedächtnis; `_aix_wissen`-Markdown als Wahrheit |
| **L7 Oberflächen** | aethelema (Flutter) als Cockpit aller Kreise; SwiftUI-Leitstand; App Intents für Freigabe vom iPhone; Xcode/Zed über ACP; aethelBot für Fernwartung | SwiftUI, Flutter+frb, App Intents, ACP | aethelema, aethelBot, aix-dashboard :7331 (Daten), aethelTerminal | HTML-Dashboards (`bench/dashboard.html`, `audit.html`) als Hauptoberfläche |
| **L8 Firma** | Software-PLM: Produkt-ID, Revision, Status; Komponentenstückliste; Änderungsobjekt mit Betroffenheit; Spec-Graph mit Wellen; Portfolio-Entscheidung als Zustand; Lieferantenkonten für Fremdagenten; Radar (S4); Kanon als Policy (S5) | Daten in aixd, Sicht in aethelema | workspace-manifest `projects.yaml`, aethelProjects-Scan, RFC 0001/0002 als Quelle der Regeln | fünf Register nach Zusammenführung in aethelRegistry |

### 8.1 Entscheidungen, die der Bericht empfiehlt

| Entscheidung | Begründung | Verwirft |
|---|---|---|
| **aethelAgentRuntime wird der Kern aixd**, umbenannt oder nicht | Ledger, Proposal/Approval, Policy, Leases, Audit, Limbus existieren dort in Rust mit Verträgen `aethel.*.v1`; Neubau verstößt gegen Kanon 4 | Neubau „aixd“ von null; aix-Zustand in JSONL |
| **Harness in Swift auf dem Kern**, nicht in Python | Kanon 2; Apple liefert Modellgrenze, Skills, Eval, ACP, Sandbox in Swift; Python bleibt Rand | hydra_forge und digitalSoftwareFactory als Laufzeit (bleiben Referenz oder werden archiviert) |
| **FoundationModels `LanguageModel` ist die Modellgrenze der Laufzeit**; litellm nur Cloud-Rand | Ein Protokoll für On-Device, MLX, Core AI, PCC, Claude, Gemini; Katalog in aixd | zweiter Katalog im Router; `~/bin/*-mlx` als Wahrheit |
| **Containerization statt sandbox-exec, aethelContainer als Hülle** | Kanon 1; `container` 1.4 stabil; Stacks decken Compose-Lücke | vier Sandbox-Implementierungen, `tart`, Docker für Agenten |
| **ACP-Server in der Laufzeit** | Xcode 27 nimmt nur ACP; Zed, JetBrains, Neovim ebenso; ein Protokoll statt neun Harness-Clients | eigene Editor-Integrationen |
| **MCP-Hub bleibt und wird Vertragslieferant** | einzige funktionierende Ein-Quelle-Auslieferung; Revision 2026-07-28 prüfen | stdio-Server je Client |
| **Spec-Graph mit Wellen in aethelProjects, Ausführung in aixd** | Kiro zeigt den Weg; 157 Spezifikationen warten; `omega_validate_dag` prüft schon Graphen | Worklane-Stub, Markdown-Backlogs |
| **Verdict mit drei Sensoren in aethelLanding** | Verification Horizon, EvilGenie: Tests allein reichen nicht | „Gate grün = fertig“ |
| **Loop-Registry `aethel.loop/v1` im Kern, Cockpit zeigt Kreise** | Kybernetik vollständig verlangt registrierte, geschlossene Kreise | Kreise in Chat und Akten |
| **Kanon als Policy-Daten mit Version in aixd** | S5 maschinenlesbar; 289 CLAUDE.md-Kopien werden daraus erzeugt | Regeln als Prosa an 826 Orten |
| **Rust-Version im Kanon auf Ist (1.97.1) oder Toolchain auf 1.98** | Kanon darf nichts nennen, was nicht installiert ist | – |
| **aiderDesktop: Crate-Audit, Übernahme in L5/L6, Rest archivieren** | 238 Crates ohne Betrieb sind Varietät ohne Regler | 238 Crates als latente Laufzeit |
## 9. Konsolidierte Lücken (priorisiert)

Zusammenführung aus Hauptbericht (Register, Verträge, Kreise), Plattform (Abschnitt 1–2), Werkzeugabgleich (4), Forschung (5), Siemens/Kiro (6), Kybernetik (7), Inventar (3). Priorität: 1 = blockiert alles andere.

| Prio | Lücke | Beleg | Komponente@Vertrag |
|---|---|---|---|
| 1 | Zwei Kerne, kein Beschluss, welcher Wahrheit ist (aix-Zustand in JSONL/Bash gegen aethelAgentRuntime-Ledger) | 3.1, 3.3 | `aixd@aethel.aixd/v1` = aethelAgentRuntime + aix-Typen |
| 1 | Deploy-Drift: `~/bin` ≠ Repo, MCP-Server ≠ Repo, Runtime 114 Commits zurück, Parität rot | `aix_doctor`, 3.3 | `aethelRelease@aethel.release/v1`: signierte Releases, Parität als Pflichtsensor mit Stellglied |
| 1 | Keine Produkt-ID, fünf Register | Hauptbericht 3 | `aethelRegistry@aethel.registry/v1` |
| 2 | Kein beidseitiger Vertragstest irgendwo (0/7) | Hauptbericht 4 | `aethelContracts@aethel.contract/v1`, erster Fall Analyzer↔aethelProjects |
| 2 | Verdict misst nur Tests; keine zurückgehaltenen Tests, kein Testdatei-Wächter, kein Richter | 5.2 | `aethelLanding@aethel.verdict/v1` |
| 2 | Freigabe über Chat; approvals.* im Betrieb deaktiviert; keine LocalAuthentication | 3.1, 7.2 | `aethelAppleRuntime@aethel.approval/v1` + App Intent |
| 2 | Vier Sandboxen, Zielwerkzeug `container` fehlt | 3.3, 2 | `aethelContainer@aethel.sandbox/v1` |
| 2 | Kreise nicht registriert; S3*, S4, algedonischer Kanal fehlen | 7 | `aixd@aethel.loop/v1`, `aethelRadar@aethel.radar/v1` |
| 3 | Harness-Teilsysteme ohne Grenze; Hooks 4 von 18 Ereignissen; keine Subagent-Abstraktion; kein Resume-Vertrag | 4 (#1, 4, 5, 8) | `aethelAppleRuntime@aethel.harness/v1`, `aethel.run/v1` |
| 3 | Modellgrenze doppelt (litellm, Kataloge); FM-Protokoll ungenutzt; `fm`-Lizenz offen; `apple_fm_sdk` fehlt; Core AI unbewertet | 1, 2 | `aixd@aethel.model-catalog/v1`; Lizenzbestätigung durch Manuel |
| 3 | Spezifikation ohne Task-Graph, Wellen, Code-Verknüpfung; 15 von 157 mit SHALL | 6.4 | `aethelProjects@aethel.spec-graph/v1` |
| 3 | Kein ACP, MCP-Revision ungeprüft, kein A2A | 5.6 | in Harness |
| 3 | Drei Gedächtnisse ohne Vertrag; Lernen aus Commits fehlt | 5.3, 3.3 | `aethelOmega@aethel.memory/v1` |
| 3 | Regeln an 826 Orten (289+252+285) ohne Quelle; keine Permission-Policy über Clients | 3.3 | aus Registry erzeugt; Policy in aixd |
| 3 | Code-Intelligenz nur Python, nur intern; kein tree-sitter/LSP im Betrieb für Python, TS, Swift | 3.3 | `aethelCodeAnalyzer@aix_findings.v1` + `aix-tools@aethel.code-intel/v1` |
| 4 | Keine Eval je Harness-Version; Bench-Job nicht geladen; keine Zyklusmessung | 5.4, 3.3 | `aethelEval@aethel.eval/v1`, Apple Evaluations für Swift |
| 4 | Kein Software-PLM: Revision, Stückliste, Änderungsobjekt, Betroffenheit, Lieferantenkonten | 6.1 | `aethelProjectManagement@aethel.pm/v1` |
| 4 | Variantenlinie als 34 Kopien statt Konfiguration | 6.2 | `aethelVariants@aethel.variant/v1` |
| 4 | Kein Agent als Code-Ordner mit Deploy; Rollen als launchd-Bash | 4 (#24) | Rolle = Skill + `capability.json`, Deploy = SMAppService |
| 4 | Beobachtung über Logdateien und 66.159 Ereignisdateien; kein Zustandsbrowser | 3.3 | Signposts + Replay-Sicht in aethelema |
| 5 | 238 Crates (aiderDesktop), LangGraph-Fabrik, hydra_forge, Nachtbetrieb, tote MLX-Plists: Bestand ohne Urteil | 3.3 | Crate-Audit; archivieren statt löschen |
| 5 | Node-Umgebung defekt; TS-SDKs nicht lauffähig | 1 | Toolchain-Pflege im Release-Vertrag |
| 5 | Kanon nennt Rust 1.98, installiert 1.97.1 | 1 | Kanon korrigieren |

## 10. Reihenfolge der Schnitte

Die Reihenfolge folgt Regel 5 aus Abschnitt 7.4: erst Dämpfer, dann Verstärker. Jeder Schnitt ist eine Komponente mit Vertrag und beidseitigem Test; höchstens drei Spuren gleichzeitig; Review vor Gate; ein Gate am finalen Kopf.

1. **Beschluss Kern.** aethelAgentRuntime wird aixd. Schnitt: XPC-Fassade und `aethel.aixd/v1` mit den heutigen Werkzeugen; Mutationen für den Fabrikpfad aktivieren; aix-Typen (Auftrag, Lease) als Rust-Typen übernehmen. Orakel: Ein Auftrag läuft Proposal → Approval → Action mit Receipt durch.
2. **Release und Parität.** `aethelRelease`: signierte Releases für `~/bin`, MCP-Server, Runtime; Parität als Loop mit Stellglied (Neustart aus Release, nie aus Worktree). Orakel: `aix_doctor` grün aus Release.
3. **Registry.** `aethelRegistry` mit Produkt-ID, erzeugt `projects.yaml`, CLAUDE.md, AGENTS.md, `.cursor/rules`, MCP-Registry. Orakel: fünf Register aus einer Quelle, Diff null.
4. **Erster beidseitiger Vertrag.** `aethelContracts` mit Fixture Analyzer↔aethelProjects; Analyzer-Binary aus Release. Orakel: beide Tests laufen gegen dieselbe Fixture.
5. **Loop-Registry und Cockpit.** `aethel.loop/v1` in aixd; aethelema zeigt Kreise, Zeit seit Schluss, offene Glieder; algedonischer Kanal für Kosten, Cloud, Speicher. Orakel: Parität-Loop und Gate-Kapazität-Loop als erste registrierte Kreise.
6. **Verdict mit drei Sensoren.** aethelLanding installiert aus Release; zurückgehaltene Tests, Testdatei-Wächter, Richter mit eigenem Kontext; Landung als Verb mit Receipt. Orakel: EvilGenie-artiger Testfall wird abgewiesen.
7. **Sandbox.** `container` installieren; aethelContainer als Hülle; Gate-Image mit Snapshot; sandbox-exec abschalten. Orakel: Gate läuft hermetisch mit Digest des Images im Receipt.
8. **Harness Schnitt 1 (Swift).** Schleife, Werkzeuge über MCP-Hub, Hooks pro Werkzeug aus aixd-Policy, Budget mit Fortsetzungsauftrag; ACP-Server; Skills im `SKILL.md`-Format. Orakel: Xcode 27 fährt den AETHEL-Agenten über ACP durch einen Schnitt.
9. **Modellgrenze.** `LanguageModel`-Protokoll in der Laufzeit; Katalog in aixd mit Kostenklasse; Stufe 0 über SystemLanguageModel nach Lizenzbestätigung; Eval mit Apple Evaluations. Orakel: Triage-Kette lokal, Eval grün, Kostenklasse im Ledger.
10. **Spec-Graph.** aethelProjects erzeugt Aufgabengraph und Wellen aus SPEC/DESIGN/TEST-CASES; aixd führt Wellen aus; Rückkopplung Task ↔ Commit. Orakel: ein Repo vom SPEC bis zur Landung ohne Markdown-Backlog.
11. **Gedächtnis.** `aethel.memory/v1` über aethel-omega und Runtime-Graph; Lernen aus Commits und Receipts. Orakel: Lehre aus einem Receipt erscheint im Kontext des nächsten Schnitts desselben Projekts.
12. **Software-PLM und Radar.** aethelProjectManagement (Revision, Stückliste, Änderungsobjekt, Lieferantenkonten) und aethelRadar (Apple-Guides, Changelogs, arXiv, Registry-Abgleich als Dienst). Orakel: dieser Bericht wird als Radar-Lauf reproduzierbar.
13. **Bestand richten.** Crate-Audit aiderDesktop, Urteil über digitalSoftwareFactory und hydra_forge, tote Plists, Varianten-Generator. Nichts löschen, alles archivieren.

## 11. Grenzen dieses Berichts

- Webquellen sind teils sekundär (Blogs, Aggregatoren). Als „sek.“ markierte Angaben, die DORA-Zahl, Kiraas „80×“, „Intelligence Center X“ und Claude Codes ACP-Status sind nicht primär belegt.
- Apple-Angaben stammen aus dem WWDC26-macOS-Guide und einem Xcode-27-Artikel; Core-AI-Details und FM-Open-Source-Lizenz sind nicht aus Apple-Primärtext.
- Der Subagent hat Zeilen grob gezählt, Tests nicht ausgeführt, aethelLanding und `aix-merge-gated` nicht gelesen, Apple-Laufzeit nicht geprüft. Die Apple-Befunde stammen aus meinen eigenen Proben.
- Gemessen wurde auf diesem Mac am 03.11.2026; Ports und PIDs sind Momentaufnahmen.
- Kein Repo wurde verändert, nichts installiert, keine Lizenz bestätigt, kein Modell aufgerufen außer den Suchwerkzeugen.

## 12. Quellen

Apple: developer.apple.com/wwdc26/guides/macos/ · developer.apple.com/videos/play/wwdc2026/258/ (Xcode 27) · developer.apple.com/videos/play/wwdc2026/241/ (Foundation Models) · spaceport.build/blog/whats-new-xcode-27 · dev.to/hariharanjagan/whats-new-in-apples-foundation-models-framework-at-wwdc-2026-5227 · appleinsider.com/articles/26/03/01/wwdc-2026-to-introduce-core-ai-as-replacement-for-core-ml · cloudnativenow.com/features/apple-ships-stable-1-0-of-its-native-container-tool-for-macos/ · swiftpackageregistry.com/apple/container
Werkzeuge: cursor.com/changelog · gradually.ai/en/changelogs/cursor/ · code.claude.com/docs/en/changelog · claudelog.com/faqs/claude-code-release-notes/ · learn.chatgpt.com/codex/changelog · codex.danielvaughan.com (2026) · docs.langchain.com/oss/python/langchain/middleware/built-in · docs.langchain.com/oss/python/deepagents/overview · kiro.dev/docs/specs/ · zed.dev/acp · github.com/modelcontextprotocol/specification/releases/tag/2026-07-28 · openhands.dev
Forschung: arXiv 2609.00006, 2602.14690, 2606.20683, 2607.13285, 2609.20804, 2603.13258, 2606.26300, 2511.21654, 2609.08149, 2605.13139, 2608.02499, 2606.29957, 2606.17799 · vals.ai/benchmarks/swebench · morphllm.com/best-ai-coding-agents-2026 · cncf.io/blog/2026/07/06/evolving-platform-engineering-for-ai-native-workloads/
Siemens/Mendix/Kiraa: blogs.sw.siemens.com/teamcenter/teamcenter-2606/ · press.siemens.com (CES 2026) · mendix.com/blog/mendix-release-11-0-… · community.mendix.com (11.12 LTS) · docs.mendix.com/refguide/maia-development-lifecycle/ · kiraa.ai/tech · itbrief.com.au (Kiraa)
Eigene Messungen: `sw_vers`, `xcodebuild`, `swift`, `rustc`, `fm --help`, `fm available`, `fm license`, `launchctl`, `aethel_capabilities_describe`, `aix_doctor`, `aix_copilot_list_tools`, grep über /Users/manuel/workspace.
