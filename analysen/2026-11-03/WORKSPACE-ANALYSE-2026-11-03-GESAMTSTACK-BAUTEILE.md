# Gesamtstack-Bericht: was fehlt, wo nicht Best Practice, welche Bauteile zuerst

Stand 03.11.2026. Dritter Teil nach Hauptbericht (`WORKSPACE-ANALYSE-2026-11-03.md`) und Ergänzungsbericht (`…-ERGAENZUNG-TECHNOLOGIE-ARCHITEKTUR.md`). Nur Analyse; nichts verändert, nichts installiert. Auftrag von Manuel: Der gesamte Softwarestack vom Prozessor bis zu allen Anwendungen soll gebaut werden. Was fehlt noch, wo ist die Praxis nicht Best Practice, und strategisch: welche Bauteile bauen wir, damit wir anderes bauen können.

## 0. Kurzfazit

1. Die Fabrik arbeitet an Stufe 2 (Kernel-Namen, Simulator-Scaffolds, Theorie-Repos), ohne Stufe 1 zu haben (die Fabrik kann kein eigenes Bauteil ohne Hand herstellen und ausliefern). Deshalb bleibt jede Schicht ein unverbundenes Repo. Das ist die strategische Diagnose.
2. Von 20 Meta-Bauteilen (Abschnitt 4) mit Hebelwirkung existieren null als Komponente mit Vertrag; für 14 gibt es Bestand, der hineinwächst. Die fünf mit höchstem Fan-out: Kern aixd (8), Registry (7), Vertragsgenerator (6), Isolationshülle (4), Harness (4). Release-Pipeline hält alle anderen haltbar.
3. Für Hardware, Firmware, Kernel und Schnittstellen-IDL existiert im eigenen Code nichts: 0 Verilog, 0 Devicetree, 0 WIT/FIDL, 0 eigene `no_std`-Kerne, 0 eigene Beweise. aethel_os, omega-system und dinOmegaFoundations haben zusammen 1.292 Zeilen, so viel wie ein aix-Crate.
4. Die Theorie-Repos sind das Gegenteil: aethel-v6 141k, aethelDeepLearning 166k, Athelix 44k, aethelHelix 34k Zeilen ohne Vertrag und ohne Konsument. Ein Forschungs-Tor fehlt.
5. Die Werkzeuge für „Simulator zuerst“ sind installiert (QEMU für drei Architekturen, Verilator, Yosys, cosign, syft, cargo-fuzz, Coq), die Ziele fehlen (keine Rust-Bare-Metal-, WASI- oder Static-Linux-Ziele, keine Swift-SDKs). Nichts davon ist in einem Vertrag verlangt.
6. Referenzstacks 2026 (Oxide, seL4, Asterinas 0.18, Redox, Fuchsia im Wartungsmodus, RISC-V RVA23 fast ohne Silizium, WASI 0.3, Embedded Swift experimentell) sagen übereinstimmend: Rust-Kern, Simulator zuerst, fremde ABI anbieten, Capabilities, RFD-Entscheidungen, Provenance je Artefakt, Konformitätstests in eigener CI. Der Kanon stimmt mit 2 davon vollständig überein (Rust-Kern, SQLite-Wahrheit) und mit keinem der übrigen in der Praxis.
7. Nicht Best Practice in 17 Schichten (Abschnitt 3): vier Sandboxen, zwei Kerne, drei Gedächtnisse, 826 Regelorte, Release aus Worktree, Entscheidungen in Chat statt RFD, Logdateien statt Signposts, Geheimnisse teils in Dateien, kein Threat Model, kein CRA-Prozess trotz Meldepflicht seit 11.09.2026.
8. Eigen bleiben: Rechenmodell als Simulator, Systemdienste, Komponentenlaufzeit, Wissen, SDK, Apps, Distribution. Fremd bleiben: Silizium, ISA (RISC-V/ARM64), Kernel (XNU, Linux-Gast), Hypervisor, Sprachen, Compiler. Ein eigener Framekernel ist nach Stufe 1 als RFD zu entscheiden, nicht vorher.
9. Das messbare Kriterium für Stufe 1: Ein Auftrag „neuer Analyzer-Regelsatz“ läuft von Spec-Compiler über Harness, Isolation, Verdict, Release, Registry, Konfigurations-Compiler, Gedächtnis bis Eval ohne Chat und ohne Markdown mit einem Receipt durch.
10. Die Reihenfolge (Abschnitt 4.2 und 6) ist Hebel-sortiert: Registry, Release, Kern, Vertragsgenerator, Konfigurations-Compiler, Verdict, Isolation, Harness, Spec-Compiler, Eval, Modellgrenze, Policy, Gedächtnis, Radar, Generator; dann IDL, SDK, Systemschicht, Distribution, Simulator; zuletzt die Kernel-Entscheidung.
## 1. Was auf diesem Mac für den Bau unterer Schichten schon installiert ist (gemessen 03.11.2026)

| Bereich | Installiert | Fehlt | Bedeutung |
|---|---|---|---|
| Emulation | qemu-system-riscv64, -aarch64, -x86_64 | Renode | Kern- und Firmware-Entwicklung „Simulator zuerst“ ist sofort möglich |
| Hardwarebeschreibung | Verilator, Yosys, Icarus Verilog, LLVM 21 | nextpnr, FPGA-Board-Toolchain, RISC-V-GNU-Toolchain | Ein Rechenmodell kann in Verilog simuliert und mit Yosys synthetisiert werden; auf ein Board bringen geht nicht |
| Rust-Ziele | stable + nightly; Ziele: darwin, iOS, Android, wasm32-unknown-unknown, x86_64-linux-gnu, windows-msvc; alte Toolchains 1.78/1.83/1.86 | `riscv64gc-unknown-none-elf`, `aarch64-unknown-none`, `thumbv*`, `wasm32-wasip2/wasip3`, `x86_64-unknown-linux-musl`, `aarch64-unknown-linux-gnu` | Keine Bare-Metal-Ziele: kein `no_std`-Kern baubar; kein WASI-Komponentenziel; kein statisches Linux-Ziel für Container-Gäste |
| Swift | 6.4.2 | keine Swift-SDKs (`swift sdk list` leer): kein Static Linux SDK, kein Embedded-Ziel | Containerization baut mit Static Linux SDK; Embedded Swift nicht nutzbar |
| C/Zig | clang (Xcode), zig 0.x, cmake, make | ninja, meson | Zig als Cross-Linker vorhanden |
| WebAssembly | wasmtime, wasmer, wasm-pack | wasm-tools, cargo-component, WIT-Werkzeuge | Laufzeit da, Komponentenmodell-Werkzeuge fehlen |
| Supply Chain | cosign, syft, grype, trivy, cargo-audit, cargo-deny, cargo-fuzz | cargo-vet, osv-scanner, cargo-sbom, in-toto, slsa-verifier | Signatur und SBOM möglich; kein Pfad nutzt sie |
| Verifikation | Coq (coqc, opam), cargo-fuzz | Kani, Verus, Prusti, TLA+, Lean | Formale Mittel vorhanden, keine Nutzung im Workspace gefunden |
| Debug/Flash | lldb, openocd | probe-rs, gdb-multiarch | Hardware-Debug möglich |
| Container/VM | Virtualization.framework, Docker, OrbStack, podman, lima, Parallels | Apple `container`, `tart` | fünf Container-Wege, keiner der zwei, auf die eigener Code zeigt |
| Build-Systeme | cargo, swiftpm, make, cmake, flutter | nix, bazel, buck2 | keine hermetischen, reproduzierbaren Builds über Sprachgrenzen |

Fazit: Die Werkzeuge für „Simulator zuerst“ (QEMU, Verilator, Yosys) sind da, die Ziele (Rust Bare-Metal, WASI, Static Linux) fehlen. Das ist eine Stunde Installation, aber ohne Vertrag, der sie verlangt, bleibt es ungenutzt.
## 2. Wie vollständige Stacks heute gebaut werden: Referenzen und Stand Oktober 2026

Belegstellen sind Projektseiten, Phoronix, offizielle Blogs; „sek.“ markiert Sekundärquellen.

| Referenz | Was sie zeigt | Stand 2026 | Lehre für AETHEL |
|---|---|---|---|
| **Oxide Computer (Hubris, Humility, RFDs)** | Vollständiger Stack von Service-Prozessor-Firmware bis Steuerungsebene, komplett in Rust, Hardware-Root-of-Trust; Hubris ~2.000 Zeilen Mikrokern, kein dynamischer Speicher, kein C; jede Entscheidung als nummeriertes RFD (Request for Discussion) mit Status | produktiv; RFD 26 begründet OS- und Hypervisor-Wahl | Entscheidungen als RFD mit Status in der Registry, nicht als Chat. Debugger (Humility) ist Teil des OS-Vertrags, nicht Nachtrag. Firmware ist Stufe 1 des Stacks, nicht Stufe 0 (Silizium) |
| **seL4** | Formal verifizierter Mikrokern (Isabelle/HOL), Capability-Modell | weiter Referenz; Heiser 2026 beschreibt Nutzungshürden | Capabilities von unten bis oben; Verifikation ist Prozess, nicht Zusatz |
| **Asterinas** | Rust-„Framekernel“: unsicherer Rust nur im Rahmen (~14 % TCB), Linux-ABI-kompatibel, 210+ Syscalls (2025), 0.18 (Juni 2026) mit Namespaces, NVMe, kselftest/xfstests integriert, Ziel Kata/Confidential Containers | experimentell, x86-64 VM zuerst, riscv64/loongarch64 in CI | Ein neuer Kern ist nur realistisch, wenn er eine bestehende ABI anbietet (Linux) und in einer VM zuerst läuft. Konformitätstests der Zielplattform gehören in die eigene CI |
| **Redox OS** | Rust-Mikrokern mit eigener libc (relibc), eigener Desktop | monatliche Berichte, echte Hardware erst 2026 besser, kein Installer, kein Alltagseinsatz | Ein eigenes OS braucht zehn Jahre bis zum Alltag; Priorität VM-Boot vor Hardware |
| **Fuchsia (Zircon, FIDL, Komponentenrahmen)** | Capability-Kern, typisierte IPC-Verträge (FIDL), Komponenten mit Manifesten | Wartungsmodus (F30 April 2026, sek.), Google setzt auf Android-Basis | Die Architekturideen (IDL für jede Grenze, Komponentenmanifeste, Capabilities) überleben das Produkt. Für AETHEL: IDL für XPC/MCP/A2A-Grenzen |
| **Oxide + Asterinas + Redox gemeinsam** | Alle drei: Rust, Mikrokern oder Framekernel, Simulator/VM zuerst, offene Entwicklung, Testsuiten der Zielplattform | | Rust-Kern ist bestätigte Praxis, deckt sich mit Kanon 2 |
| **RISC-V RVA23** | Offenes ISA-Profil, von Distributionen als Basis gesetzt (Ubuntu 25.10/26.04) | Hardware hinkt: erster RVA23-SoC SpacemiT K3 (Linux 7.0, Boards ab Mai 2026, sek.); Images oft nur für QEMU | Ein eigener Prozessor ist nicht die Lücke; selbst der offene Standard hat kaum Silizium. Eigenes Rechenmodell als Simulator-Vertrag auf QEMU/Verilator, ISA = RISC-V als Fremdschicht |
| **CHERI / CHERIoT** | Hardware-Capabilities gegen Speicherfehler | Sonata-Board (CHERIoT Ibex auf FPGA) käuflich; erster kommerzieller CHERIoT-Tapeout lowRISC/SCI angekündigt (Aug. 2026, sek.) | Capability-Modell ist Hardware-Trend; Software-Capabilities heute, Hardware später |
| **Linux Rust (Nova, Tyr)** | Rust-Treiber im Mainline, NVIDIA Nova als Ziel für offiziellen Treiber (LPC 2026) | Rust im Kern ist etabliert, nicht Pflicht | Linux bleibt die Fremdschicht für Gäste in Containern; eigene Treiber nur in Rust |
| **WASI 0.3 / Component Model** | Komponentenmodell mit typisierten Schnittstellen (WIT), nativer Async seit 11.06.2026, Wasmtime 46+ standardmäßig | Rust-Bindings (wasip3), andere Sprachen hinken; kein 1.0-Datum | Portabilitätsschicht für Komponenten über Mac, Linux, Gast: aethelContainer hat schon WASI-Tasks (Wasmtime). WIT als IDL für Komponentenverträge prüfen |
| **Embedded Swift** | Swift ohne Laufzeit für Mikrocontroller (STM32, RP2040, nRF52, ESP32-C6 RISC-V); 6.3 Diagnosen, 6.4 Metatypen | experimentell | Swift reicht bis zur Firmware, aber Kanon setzt Rust als Kern; Swift bleibt Laufzeit und Oberfläche |
| **Apple-Stack selbst (Darwin, XNU, Swift, Clang, Containerization, Core AI)** | Geschlossener Stack vom Silizium bis zur App, mit offenen Teilen (Swift, Containerization, FM-Framework) | macOS 27 | Das ist der Stack, auf dem AETHEL heute läuft. „Gesamtstack bauen“ heißt zuerst: entscheiden, welche Apple-Schichten fremd bleiben |
| **SLSA 1.1, in-toto, Sigstore, SBOM** | Herkunftsnachweis je Artefakt, Attestierungen, Signatur ohne Schlüsselverwaltung | SLSA 1.1 aktuell; reproduzierbare Builds sind Option, nicht Pflicht | Jeder Release-Vertrag trägt Provenance; Receipts mit Digests (Kanon 6) sind genau das, nur eigenformatig |
| **EU Cyber Resilience Act** | Meldepflichten für aktiv ausgenutzte Schwachstellen seit 11.09.2026 (24 h / 72 h / 14 Tage); Hauptpflichten (Secure by Design, SBOM, CE) ab 11.12.2027; Open-Source-Stewards ab 12.2027 (sek., widersprüchlich) | in Kraft | Wer Software in der EU in Verkehr bringt, braucht SBOM, Schwachstellenprozess, Update-Kanal. aethelDistribution (S7) ist Pflicht, nicht Komfort |
| **Formale Verifikation in Rust** | Atmosphere (verifizierter Kern mit Verus, SOSP ’25), KVerus (Proof-Generierung, arXiv 2605.03822), Kani | Forschung bis früh produktiv | Für aixd-Zustandsmaschine: Kani/Verus für erlaubte Übergänge; typisierte Zustände als Kompilierfehler (Kanon 6) sind die Vorstufe |

### 2.1 Best Practices, die aus den Referenzen folgen

1. **Schichtenkarte mit Verträgen vor Code.** Jede Grenze hat eine IDL (FIDL, WIT, Protobuf, XPC-Protokoll, MCP-Schema) und eine Konformitätssuite.
2. **Simulator zuerst, Hardware zuletzt.** QEMU, Verilator, Renode; kein Kern ohne VM-Boot in CI; kein Rechenmodell ohne Simulator-Vertrag.
3. **Fremde ABI anbieten, bevor eigene erfunden wird.** Asterinas läuft Linux-Programme; Redox baut relibc. Ein eigenes OS ohne POSIX-/Linux-Kompatibilität hat keine Anwendungen.
4. **Capabilities statt ACLs, von Hardware bis App.** seL4, Fuchsia, CHERI, WASI.
5. **Entscheidungen als RFD mit Status**, Code mit Verweis auf das RFD.
6. **Provenance je Artefakt** (SLSA, in-toto, Signatur, SBOM), reproduzierbar wo möglich, Release aus Pipeline, nie aus Worktree.
7. **Konformitätstests der Zielplattform in eigener CI** (kselftest, xfstests, WASI-Spec-Tests, Swift Testing).
8. **Debugger und Beobachtbarkeit als Teil der Schicht** (Humility, Instruments, Signposts), nicht als Werkzeug daneben.
9. **Ein Kern pro Zweck, eine Wahrheit pro Zustand**: kein zweiter Kernel, kein zweiter Ledger, kein zweiter Katalog.
10. **Regulatorik als Vertrag**: CRA-Meldeprozess, SBOM, Update-Kanal als Komponenten mit Tests.
## 3. Schicht für Schicht: was fehlt und wo die heutige Praxis von Best Practice abweicht

Bestand aus Hauptbericht Abschnitt 12 und Ergänzungsbericht; Zahlen des Stack-Inventars in 3.1. Spalte „nicht Best Practice“ nennt die Abweichung gegen Abschnitt 2.1.

| Schicht | Bestand | Fehlt für einen baubaren Stack | Nicht Best Practice heute |
|---|---|---|---|
| **S0 Silizium / Rechenmodell** | aiderDesktop_memristor_v1, memoristorCursor (Rust-Scaffolds), osxQ/osxq-pennylane (Quantensimulator auf MLX, eigenes Device), aethelHelix, bit_encodings, photon-* | ISA- oder Rechenmodell-Spezifikation; Simulator-Vertrag; ein Konsument (Compiler-Backend, Benchmark); Verilog-Modell für Verilator; Entscheidung „RISC-V als ISA“ | Vier Simulator-Ansätze ohne gemeinsame Spezifikation und ohne Konsument (Regel 1, 3); kein Simulator-zuerst-Vertrag (Regel 2); Forschung und Produkt vermischt (Regel 9) |
| **S1 Firmware / Root of Trust** | nichts eigenes; Secure Enclave im Kanon | nichts fehlt, solange Silizium fremd ist; Vertrag, dass Geheimnisse und Freigaben über Secure Enclave/LocalAuthentication laufen | Freigaben über Chat statt Hardware-gestützt (Regel 4) |
| **S2 Kernel** | aethel_os (leere Hülle, 3 Commits), lector_os (Flutter-Template), omega-system (6 Commits, kein README), dinOmegaFoundations (leer) | Entscheidung fremd/eigen; wenn eigen: Framekernel-Ansatz, Linux-ABI, VM-Boot in CI, kselftest; `no_std`-Ziele installiert | Namen ohne Inhalt statt RFD (Regel 5); kein VM-Boot (Regel 2); kein ABI-Ziel (Regel 3) |
| **S3 Hypervisor / Isolation** | Virtualization.framework vorhanden; aethelContainer (7 Crates, `tart`-Aufruf, Isolation profile/sandbox_exec/vm, Stacks, WASI-Tasks) nicht geladen; vier Sandbox-Implementierungen; Docker/OrbStack/podman/lima installiert | Apple `container` installiert und als einzige Isolation; aethelContainer als Hülle mit Vertrag; Gate-Image mit Digest | Vier Sandboxen (Regel 9); Daemon-Plist zeigt auf `target/debug` (Regel 6); Isolation hängt an nicht installiertem `tart` |
| **S4 Systemdienste** | aethelAgentRuntime (Ledger, Proposal/Approval, Policy, Leases, Audit, Limbus, 55 Werkzeuge), aix-Crates (Ledger, Kernel, Domain, Secrets), 38 launchd-Jobs mit Bash-Wrappern | XPC-Dienst mit SMAppService; Capability-Modell über alle Schichten; Loop-Registry; Policy-as-Code; Agentenidentitäten | Zwei Kerne (Regel 9); Dienste als Skripte (Kanon 1); Zustand teils in JSONL/Markdown (Kanon 3); keine Capabilities (Regel 4) |
| **S5 Komponentenlaufzeit** | aix Gated-Solve, Copilot-Werkzeuge, Rollen-Knoten; digitalSoftwareFactory (LangGraph, Checkpointer, Interrupt) ohne Betrieb; WASI-Tasks in aethelContainer | Swift-Harness mit sieben Teilsystemen; WIT/IDL-Verträge; ACP/MCP 2026-07-28; Resume-Vertrag | Harness über 1.006 Skripte verteilt (Regel 1); keine IDL an Grenzen (Regel 1); kein Konformitätstest (Regel 7) |
| **S6 Sprache / Compiler / Toolchain** | Rust 1.97.1, Swift 6.4.2, Dart 3.12, Python 3.15, Zig; `sprache-quellen/` (dspy, guidance, outlines, tree-sitter) als Klone; keine eigene Sprache | Toolchain-Ziele (Bare-Metal, WASI, Static Linux, Embedded Swift); Toolchain als Vertrag im Release; Kanon-Rust-Version passend | Kanon nennt 1.98, installiert 1.97.1; drei alte Rust-Toolchains ohne Zweck; Node defekt; keine Pinning-Datei über Sprachen hinweg (Regel 6) |
| **S7 Build / Release / Provenance** | cargo, swiftpm, flutter, make; cosign, syft, grype, trivy, cargo-audit/-deny/-fuzz installiert; nur aethelLocalCoder mit versionierten Releases | Release-Pipeline mit Signatur, SBOM, SLSA-Provenance; Parität als Kreis mit Stellglied; hermetische Builds (nix/bazel/buck2) für Kernpfade | `~/bin` 1.127 gegen 1.006 im Repo; MCP-Server deployt ≠ Repo; Runtime 114 Commits zurück; Release aus Worktree (Regel 6); Werkzeuge installiert, nirgends im Pfad |
| **S8 Daten / Wissen** | aix-ledger (SQLite), Runtime replay.sqlite + graph.sqlite, aethel-omega (TS, 143 Tests), `_aix_wissen`-Skripte, 478 Akten, `~/.aix` 61 GB mit 66.159 Ereignisdateien | ein Datenmodell, Read-Model, Provenienz-Schicht, Aufbewahrungsregel, Gedächtnisvertrag | Drei Gedächtnisse (Regel 9); Ereignisse als Dateien statt Strom; Akten als Wahrheit (Kanon 3) |
| **S9 Kommunikation / Verbund** | aethelema P2P (Ed25519), aethelBot, mcp-hub :9101–9110, agentenbruecke, copilot-messenger | typisierte Nachrichten mit IDL; Bonjour-Ankündigung; Föderation M5↔M4 als Vertrag; Sicherheitsaudit | Textnachrichten statt Schema (Regel 1); Identität ungeprüft (Regel 4) |
| **S10 Plattform-SDK** | aethel_core/design, Athelix (Low-Code, 103 Commits), direkte Kopplungen (13 Varianten, 3 Analyzer-Konsumenten) | eine Bibliothek je Sprache (Rust, Swift, Dart) für Identität, Aufträge, Wissen, Receipts | Apps koppeln direkt (Regel 1); keine Versionierung der Plattform-API |
| **S11 Anwendungen** | ca. 55 Produkte, 34 Varianten je 78 LOC, 5–6 substanziell | Variantenmodell und Generator; gemeinsame Basis durchgezogen; Reifegrad nach Funktion statt Datei | Kopien statt Konfiguration (Mendix-Lehre); Reifegrad misst Dateien |
| **S12 Oberflächen** | Flutter 123 Repos, SwiftUI 14, React-Leitstand, HTML-Dashboards | SwiftUI-Leitstand, aethelema als Cockpit aller Kreise, App Intents | HTML als Hauptoberfläche (Kanon 5); vier Oberflächen-Technologien |
| **S13 Sicherheit / Identität / Rechte** | aethelema Ed25519, 15 Rollen, aix-secrets, Keychain im Kanon, Rust-Risikoklassifizierer, Limbus | Capability-Modell von S3 bis S11; Agentenkonten; Geheimnisse ausschließlich Keychain/SE; Threat Model je Schicht | Geheimnisse teils in Dateien; Rollen ohne Identität (Regel 4); kein Threat Model |
| **S14 Beobachtbarkeit** | Replay-Timeline, aix-dashboard :7331, Logdateien, 66.159 Ereignisdateien, `bench/dashboard.html` | OSLog/Signposts, MetricKit, Instruments-Profile, Zustandsbrowser im Cockpit | Logdateien statt Signposts (Kanon 1); Debugger nicht Teil der Schicht (Regel 8) |
| **S15 Qualität / Verifikation** | Tests je Repo (uneinheitlich), 200 Analyzer-Tests, Hard-9, Mutationstest in aix, cargo-fuzz installiert, Coq installiert | Konformitätssuiten je Vertrag; Kani/Verus für aixd-Übergänge; Fuzzing für Parser/Protokolle; Eval je Harness-Version | Kein Fuzzing im Betrieb; keine formale Prüfung trotz Werkzeugen (Regel 7); Gate misst nur „Tests grün“ |
| **S16 Distribution / Regulatorik** | FamilyAppStore (privat), Apple-Signatur bei Apps vermutlich, keine SBOM, kein Update-Kanal, kein Schwachstellenprozess | aethelDistribution: Signatur, Notarisierung, SBOM, Update, Rücknahme, CRA-Meldeprozess (24 h/72 h/14 Tage) | CRA-Meldepflicht gilt seit 11.09.2026 für in der EU vertriebene Produkte; kein Prozess vorhanden (Regel 10) |
| **S17 Entscheidungen / Dokumentation** | RFC 0001/0002 (workspace-manifest), 478 Koordinationsakten, Kanon in CLAUDE.md an 289 Orten, SPEC/DESIGN/TEST-CASES 157 Dateien | RFD-Prozess mit Status und Verweis aus Code; Schichtenkarte; Kanon als Daten | Entscheidungen in Chat und Akten statt RFD (Regel 5); Doku widerspricht Code (Hauptbericht 6.6) |

### 3.1 Zahlen der unteren Schichten (gemessen 03.11.2026, ohne Archive, Worktrees, Vendoring; LOC über rs/swift/dart/py/ts)

| Repo | Dateien | LOC | letzter Commit | Commits | Befund |
|---|---:|---:|---|---:|---|
| aethel_os | 16 | 303 | 09.06. | 3 | leere Hülle |
| omega-system | 35 | 989 | 09.06. | 6 | Skizze, kein README |
| omega_domain | 235 | 86.354 (198 Dart, nicht generiert) | 09.06. | 6 | großer Dart-Domänencode, 6 Commits, nie weiterentwickelt |
| omega_bridge / omega_ui | 28 / 28 | 583 / 320 | 09.06. | 6 / 5 | Hüllen |
| lector_os | 186 | 12.311 | 09.06. | 6 | Flutter-/Rust-Template |
| dinOmegaFoundations | 5 | 0 | kein Git | – | leer |
| aethel-v6 | 478 | 140.914 | 03.10. | 156 | „Unified Cybernetic Framework“, Rust+Dart, substanziell, ohne Konsument |
| aethellm | 335 | 10.203 | 09.06. | 58 | ruht |
| AETHEL | 263 | 19.571 | 29.06. | 56 | FIMAS-Kontrollebene, ruht |
| aethel-evolution | 176 | 18.609 | 16.06. | 102 | Rust, ruht |
| aethelDeepLearning | 8.746 | 165.923 | 23.09. | 102 | größtenteils Python, Summa Ω |
| aethelHelix | 882 | 34.259 | 31.10. | 31 | Träger-/Dimensionen-Codierung, aktiv |
| bit_encodings | 121 | 16.066 | 03.10. | 13 | Rust+Dart |
| aiderDesktop_memristor_v1 / memoristorCursor | 28 / 50 | 892 / 4.878 | 09.06. / 27.06. | 2 / 12 | Simulator-Scaffolds |
| osxQ / osxq-pennylane | 1.913 / 37 | 28.993 / 819 | 09.06. | 3 / 3 | Quantensimulator (Klon mit Anpassung) + eigenes Device |
| photon-defense / photon-plm | 40 / 39 | 5.511 / 3.780 | 09.06. | 6 / 5 | ohne README |
| aethelContainer | 165 | 14.269 | 22.07. | 114 | einziger Systemdienst-Ansatz |
| Athelix | 300 | 44.442 | 17.09. | 103 | Low-Code, Flutter+Rust |
| nius-linux | – | – | 09.06. | 6 | NixOS-Konfiguration (flake.nix, hardware, modules, darwin): einziges Nix-Artefakt |
| Vergleich: aix-kernel / aix-ledger | | 718 / 1.322 | | | |

Korrektur zum Hauptbericht: „aethel_os, omega-system, lector_os, dinOmegaFoundations zusammen weniger Code als ein aix-Crate“ gilt für aethel_os + omega-system + dinOmegaFoundations (1.292 LOC ≈ aix-ledger). lector_os (12k, Template) und omega_domain (86k Dart) sind größer, aber seit dem Importtag 09.06. unberührt und ohne Konsument. Die Aussage „Namen ohne Inhalt“ bleibt für Kernel/OS richtig; für die Theorie-Repos (aethel-v6 141k, aethelDeepLearning 166k, Athelix 44k, aethelHelix 34k) gilt das Gegenteil: viel Code ohne Vertrag.

**Querschnitt** (eigener Code, ohne Klone): Verilog/VHDL 0, Devicetree 0, Linker-Skripte 0 eigene (3 in torch), WIT 0, FIDL 0, Cap’n Proto 0, Protobuf 32 (nur in Fremd- und Teilprojekten bsc, fimas), TLA+/Alloy/Lean 0, QEMU/Verilator-Konfigurationen 1, Dockerfiles 25, flake.nix 1 (nius-linux), Bazel/Buck 4 (fremd), RFC-Dokumente 4 eigene (workspace-manifest 3, aethelFactory 1), SBOM-Werkzeug 1 eigenes (`aethelScripts/bin/_aix_sbom.py`), Signatur-/Provenance-Dateien 0, Fuzz-Ziele 31 Verzeichnisse (davon bit_encodings und aethelema je 1 eigene, Rest Fremdcode), `no_std`-Dateien 525 (keine in einem eigenen Kern-Repo; Herkunft Vendoring), Kani/Verus-Treffer 25 (Abhängigkeiten, kein eigener Proof), Assembly 246 (alle vendored in aethelVoiceControl).

Lesart: Für Hardware, Firmware, Kernel und IDL existiert im eigenen Code nichts. Für Provenance existiert ein SBOM-Skript, keine Signatur, keine Attestierung. Für Verifikation existieren Werkzeuge, kein eigener Beweis. Für Nix existiert eine Maschinenkonfiguration, kein Build.
## 4. Strategie: Bauteile, die Bauteile bauen

Manuel 03.11.: „Es fehlt noch viel. Strategisch denken: Bauteile, die fehlen, die wir bauen, damit wir anderes bauen.“ Der Maßstab ist deshalb nicht „welche Komponente fehlt“, sondern „welches Bauteil hebt die meisten anderen“. Das ist das Bootstrapping-Problem jedes Compilers und jeder Fabrik, in drei Stufen:

- **Stufe 0: Fremde Werkzeuge bauen die Fabrik.** Claude, Codex, Cursor, cargo, swiftpm, launchd bauen aixd, Registry, Verträge. Hier stehen wir, nur dass die Fabrik noch nicht gebaut wird, sondern ihre Teile nebeneinander liegen.
- **Stufe 1: Die Fabrik baut sich selbst.** Eine Komponente mit Vertrag entsteht aus Spezifikation über Schnitt, Review, Gate, Landung, Release ohne Hand, mit Receipt. Kriterium: Die Fabrik kann ein eigenes Bauteil (z. B. den nächsten Analyzer-Regelsatz) selbst herstellen und ausliefern.
- **Stufe 2: Die Fabrik baut den Stack.** Systemschicht, Komponentenlaufzeit, SDK, Apps, Simulator, später Kernel. Jede Schicht ist eine Komponente, die Stufe 1 produziert.

Alles, was heute an Stufe 2 gearbeitet wird (aethel_os, omega-system, Memristor-Scaffolds, Theorie-Repos), entsteht ohne Stufe 1 und bleibt deshalb unverbunden. Das ist die strategische Diagnose.

### 4.1 Die Hebelkette: welches Bauteil welches ermöglicht

Lesart: A → B heißt „B ist ohne A nicht baubar oder nicht haltbar“. Fan-out ist die Zahl der direkt abhängigen Bauteile; je höher, desto früher.

| # | Bauteil (Meta-Werkzeug) | Was es herstellt | Ermöglicht direkt (Fan-out) | Bestand | Komponente@Vertrag | Stufe |
|---|---|---|---|---|---|---|
| B1 | **Registry mit Produkt-ID** | eine Wahrheit über Produkte, Komponenten, Pfade, Klone, Worktrees, Rollen, Verträge | B2, B3, B4, B6, B8, B13, B17 (7) | fünf Register, projects.yaml 2 Monate alt | `aethelRegistry@aethel.registry/v1` | 1 |
| B2 | **Vertragsgenerator** | aus `capability.json` werden Schema, Konsumententest-Gerüst, Client-Stubs (Rust, Swift, Dart, Python), MCP-Tool-Beschreibung, Doku-Abschnitt | B5, B9, B10, B11, B14, B18 (6) | ein handgeschriebener Vertrag (Analyzer) | `aethelContracts@aethel.contract/v1` | 1 |
| B3 | **Konfigurations-Compiler** | aus Registry werden CLAUDE.md, AGENTS.md, `.cursor/rules`, MCP-Registry (Claude, Codex, Cursor, Xcode), launchd/SMAppService-Plists, Hooks | B9, B12 (2) + beendet 826 Regelorte | mcp-hub-Registry (Vorbild, nur MCP) | `aethelRegistry@aethel.config/v1` | 1 |
| B4 | **Release-Pipeline mit Provenance** | signierte Artefakte mit SBOM, SLSA-Provenance, Digest; Installation aus Release, Paritätsprüfung | B5–B20 alle (Haltbarkeit), B16 | aethelLocalCoder-Releases; cosign/syft installiert | `aethelRelease@aethel.release/v1` | 1 |
| B5 | **Kern aixd** (aus aethelAgentRuntime) | Zustandsmaschine, Ledger, Lease, Freigabe, Policy, Loop-Registry, Modellkatalog, Agentenidentität | B6, B7, B8, B9, B10, B11, B12, B15 (8) | aethelAgentRuntime 0.1.0, aix-Typen | `aixd@aethel.aixd/v1` | 1 |
| B6 | **Spec-Compiler** | aus SPEC/DESIGN/TEST-CASES (EARS) werden Aufgabengraph, Wellen, Testgerüste, Akzeptanzorakel | B7, B9, B18 (3) | 157 Spezifikationen, `omega_validate_dag` | `aethelProjects@aethel.spec-graph/v1` | 1 |
| B7 | **Verdict mit drei Sensoren** | Landungsentscheid aus zurückgehaltenen Tests, Testdatei-Wächter, Richter; Receipt | B9, B10, B16 (3) + jede Landung | aethelLanding-Code | `aethelLanding@aethel.verdict/v1` | 1 |
| B8 | **Isolationshülle** | hermetische Gate- und Lauf-Umgebung mit Image-Digest auf Containerization, WASI-Tasks | B9, B10, B14, B19 (4) | aethelContainer, aethelcontainerd | `aethelContainer@aethel.sandbox/v1` | 1 |
| B9 | **Harness (Swift)** | die Schleife, die aus Auftrag und Werkzeugen einen Schnitt macht: sieben Teilsysteme, Hooks, Subagenten, ACP/MCP | B10, B11, B13, B18 (4) + Stufe-1-Kriterium | aix Gated-Solve, digitalSoftwareFactory als Referenz | `aethelAppleRuntime@aethel.harness/v1` | 1 |
| B10 | **Eval-Gerüst** | Messung je Harness-Version, Stufe-0-Kette, Modell: Zykluskosten, Reward-Hacking-Fälle, Apple Evaluations | B9 (Rückkopplung), B11, B15 (3) | Hard-9, `evals.score`, Bench-Daten | `aethelEval@aethel.eval/v1` | 1 |
| B11 | **Modellgrenze** | ein Katalog (Kostenklasse, Inferenzort, Beleg) hinter `LanguageModel`-Protokoll; Stufe 0 fm | B9, B12, B18 (3) | litellm, `coders/*.json`, fm | `aixd@aethel.model-catalog/v1` | 1 |
| B12 | **Gedächtnis-Compiler** | aus Commits, Receipts, Freigaben, Akten werden typisierte Lehren mit Provenienz und Gültigkeit; Abruf je Projekt | B9 (Kontext), B13, B15 (3) | aethel-omega, Runtime-Graph, Wissensschleife, 478 Akten | `aethelOmega@aethel.memory/v1` | 1 |
| B13 | **Radar (S4)** | Dienst, der Apple-Guides, Changelogs, arXiv, Registry-Drift liest und Ereignisse erzeugt; dieser Bericht als Lauf | B15, B16 (2) | drei Berichte von Hand | `aethelRadar@aethel.radar/v1` | 1 |
| B14 | **IDL-Compiler** | aus WIT/Schema werden Bindings für XPC, MCP, A2A, aethelema-Nachrichten in Rust, Swift, Dart | B17, B19, B20 (3) | nichts (0 WIT, 32 proto in Fremdcode) | `aethelContracts@aethel.idl/v1` | 1–2 |
| B15 | **Policy-Compiler (S5)** | Kanon als Daten mit Version → Hooks, Permission-Regeln, Kostenklassen-Regeln, algedonische Schwellen | B9, B4 (2) | CLAUDE.md an 289 Orten | `aixd@aethel.policy/v1` | 1 |
| B16 | **Distribution/CRA** | Signatur, Notarisierung, Update-Kanal, Rücknahme, Schwachstellen-Meldeprozess, SBOM je Release | alle Produkte (55) | FamilyAppStore privat | `aethelDistribution@aethel.dist/v1` | 2 |
| B17 | **Plattform-SDK** | eine Bibliothek je Sprache für Identität, Auftrag, Wissen, Receipt, Modellzugang | B18, B20, alle Apps | direkte Kopplungen | `aethelSDK@aethel.sdk/v1` | 2 |
| B18 | **Komponenten- und Variantengenerator** | aus Vorlage + Modell entsteht ein neues Paket/Crate/App mit Vertrag, Tests, CI, Registry-Eintrag; 34 Varianten als Konfiguration | alle neuen Komponenten; Stufe-1-Kriterium | aethel_core/design, Athelix (Low-Code), Skill „aethel-module-scaffold“ | `aethelVariants@aethel.variant/v1` | 1–2 |
| B19 | **Systemschicht auf macOS 27** | XPC-Dienste, Capabilities, Keychain, Containerization, Linux-Gast als zweites Ziel | B20, Stufe-2-Kernel-Option | aethelContainer, Virtualization | `aethelSystem@aethel.system/v1` | 2 |
| B20 | **Simulator-Rahmen** | gemeinsamer Vertrag für Rechenmodelle (Memristor, vChip, Helix, Quanten) mit Verilator/QEMU-Anbindung und Eval-Konsument | Forschungs-Tor, spätere ISA-/Compiler-Arbeit | vier Simulator-Ansätze | `aethelCompute@aethel.isa/v1` | 2 |

### 4.2 Reihenfolge nach Hebel

Höchster Fan-out zuerst, Abhängigkeiten beachtet: **B1 Registry → B4 Release → B5 Kern → B2 Vertragsgenerator → B3 Konfigurations-Compiler → B7 Verdict → B8 Isolation → B9 Harness → B6 Spec-Compiler → B10 Eval → B11 Modellgrenze → B15 Policy → B12 Gedächtnis → B13 Radar → B18 Generator** (Stufe 1 erreicht, wenn B18 ein Bauteil über B9/B7/B4 herstellt) **→ B14 IDL → B17 SDK → B19 System → B16 Distribution → B20 Simulator**.

### 4.3 Was wir bewusst nicht bauen

Silizium, ISA, Kernel (bis RFD nach Stufe 1), Hypervisor, Programmiersprache, Compiler, Modelltraining von Grund auf, zweiter Ledger, zweiter Katalog, zweite Sandbox, HTML-Cockpit. Jedes dieser Bauteile existiert fremd in besserer Qualität, als es die Fabrik vor Stufe 1 herstellen könnte. Die Entscheidung je Schicht steht in Abschnitt 5.

### 4.4 Messbares Kriterium für „die Fabrik baut sich selbst“

Ein Auftrag „neuer Analyzer-Regelsatz für Swift“ durchläuft: Spec-Compiler (B6) erzeugt Aufgaben und Tests → Harness (B9) baut in Isolation (B8) mit Modell aus Katalog (B11) → Verdict (B7) mit drei Sensoren → Release (B4) signiert mit SBOM → Registry (B1) kennt die neue Version → Konfigurations-Compiler (B3) verteilt sie → Gedächtnis (B12) speichert die Lehre → Eval (B10) misst Zykluskosten. Kein Chat, kein Markdown, ein Receipt. Solange dieser Lauf nicht existiert, ist jede Arbeit an Stufe 2 ein weiteres Repo ohne Anschluss.
## 5. Eigen oder fremd: die Entscheidung je Schicht

Der Kanon (07.09.) entscheidet Rust-Kern, Swift-Laufzeit, Flutter-Client, SQLite-Wahrheit. Für einen Gesamtstack fehlt die Entscheidung je Schicht. Vorschlag, mit Begründung aus Abschnitt 2, 3 und 4:

| Schicht | Eigen / fremd / später | Begründung | Vertrag |
|---|---|---|---|
| Silizium | **fremd** (Apple Silicon heute; RISC-V-Boards als zweites Ziel) | selbst der offene Standard hat 2026 kaum Silizium; eigener Tapeout ist Forschung | – |
| Rechenmodell (Memristor, Omega-vChip, Helix, Quanten) | **eigen als Simulator** | Forschung wird nur Komponente, wenn Compiler oder Laufzeit sie konsumieren; Simulator-Vertrag auf QEMU/Verilator | `aethel-compute@isa.v1` |
| ISA | **fremd** (RISC-V RVA23 als offenes Ziel, ARM64 als Ist) | Toolchains, Emulatoren, Linux vorhanden | – |
| Firmware / Root of Trust | **später, eigen in Rust** nach Oxide-Muster | erst wenn eigene Hardware existiert; bis dahin Secure Enclave | `aethel-firmware@v1` |
| Kernel | **fremd** (XNU heute, Linux als Gast in Containern); **eigener Framekernel später** nur Linux-ABI-kompatibel in VM | Asterinas und Redox zeigen Aufwand und Weg; aethel_os ist leer | `aethel-system@services.v1` |
| Hypervisor / Isolation | **fremd** (Virtualization, Containerization), **eigen als Hülle** (aethelContainer) | Kanon 1 | `aethel.sandbox/v1` |
| Systemdienste (Zustand, Rechte, Ledger, Lease, Freigabe) | **eigen** (aixd = aethelAgentRuntime) | Kern der Fabrik; existiert | `aethel.aixd/v1` |
| Komponentenlaufzeit | **eigen** (Swift Harness) + **fremd** (WASI 0.3 für portable Komponenten) | Kanon 2; WASI-Tasks existieren in aethelContainer | `aethel.harness/v1`, WIT |
| Sprache / Compiler | **fremd** (Rust, Swift, Dart) ; **keine eigene Sprache** | eigene Sprache ohne Konsumenten ist die teuerste Lücke; `sprache-quellen/` bleibt Lesestoff | – |
| Toolchain-Ziel | **eigen** als Konfiguration fremder Toolchains (Rust-Target, Static Linux SDK, WASI) | S4 aus Hauptbericht | `aethel-toolchain@target.v1` |
| Build / Release / Provenance | **eigen** auf fremden Werkzeugen (cargo, swiftpm, cosign, syft, SLSA) | Deploy-Drift ist die akute Lücke | `aethel.release/v1` |
| Daten / Wissen | **eigen** (SQLite, Ledger, Gedächtnis mit Provenienz) | Kanon 3 | `aethel.memory/v1` |
| Kommunikation / Verbund | **eigen** (aethelema P2P, Ed25519) auf **fremd** (Network.framework, Bonjour) | läuft | typisierte Nachrichten, IDL |
| Plattform-SDK | **eigen** (Rust, Swift, Dart) | S5 | `aethel-sdk@v1` |
| Anwendungen | **eigen** auf Flutter/SwiftUI | 55 Produkte, 34 Varianten | Variantenmodell |
| Distribution / CRA | **eigen** auf Apple-Signatur/Notarisierung, SBOM, Update-Kanal | Pflicht ab 12.2027, Meldepflicht seit 09.2026 | `aethel-dist@release.v1` |

Was „Gesamtstack vom Prozessor bis zur Anwendung“ dann konkret heißt: eigenes Rechenmodell als Simulator, eigene Systemdienste, eigene Komponentenlaufzeit, eigenes Wissen, eigene Apps, eigene Distribution; fremd bleiben Silizium, ISA, Kernel, Hypervisor, Sprachen. Ein eigener Kernel ist als Framekernel in einer VM mit Linux-ABI möglich, aber erst nach der Mitte.

## 6. Reihenfolge für den Gesamtstack

Voraussetzung ist die Mitte aus dem Ergänzungsbericht (Kern-Beschluss, Release, Registry, Verträge, Loop-Registry). Danach:

1. **Schichtenkarte** (`aethel-registry@stack.v1`): jede Schicht, Komponente, Vertrag nach oben und unten, eigen/fremd, Reife; aus diesem Bericht erzeugt. Orakel: jede App im Workspace lässt sich einer Schicht und einem Vertrag zuordnen.
2. **Toolchain-Ziele installieren und im Release-Vertrag festschreiben**: Rust `riscv64gc-unknown-none-elf`, `aarch64-unknown-none`, `wasm32-wasip3`, `x86_64-unknown-linux-musl`; Swift Static Linux SDK; wasm-tools; Kani. Orakel: ein `no_std`-Hello-World bootet in QEMU aus der Pipeline.
3. **Provenance**: SBOM (syft), Signatur (cosign), SLSA-Provenance für jedes Release; Receipts tragen Digest und Attestierung. Orakel: `aix_doctor` prüft Signatur, nicht Pfad.
4. **Systemschicht auf macOS 27**: aethelContainer auf Containerization, XPC-Verträge, Capabilities, Keychain; Linux-Gast als zweites Ziel. Orakel: Gate läuft im Gast, Receipt mit Image-Digest.
5. **Komponentenmodell**: WIT-Verträge für portable Komponenten, WASI-0.3-Laufzeit in aethelContainer; erster Konsument: Analyzer-Regeln als Komponente. Orakel: gleiche Komponente auf Mac und im Linux-Gast.
6. **Rechenmodell als Simulator-Vertrag**: memristor_v1, memoristorCursor, bit_encodings, osxq-pennylane unter `aethel-compute@isa.v1`; Verilog-Modell in Verilator; Konsument: ein Benchmark in aethelEval. Orakel: Simulator-Ergebnis mit Digest im Ledger.
7. **Forschungs-Tor**: AETHEL, aethel-omega, aethel-v6, Summa Ω, Helix werden nur über Spec, Test, Konsument zu Komponenten. Orakel: Forschungsregister mit Status je Projekt.
8. **Plattform-SDK** in Rust, Swift, Dart; Variantenmodell; 34 Kopien werden Konfiguration. Orakel: eine Variante aus Modell erzeugt, gebaut, signiert.
9. **Distribution und CRA**: Signatur, Notarisierung, Update-Kanal, Rücknahme, Schwachstellenprozess mit 24-h-Meldung. Orakel: Probe-Meldung im Prozess, SBOM je Release.
10. **Kernel-Entscheidung**: erst jetzt RFD „eigener Framekernel (Rust, Linux-ABI, VM zuerst)“ ja oder nein, mit Aufwandsschätzung aus Asterinas/Redox-Daten. Vorher ist jede Kernel-Arbeit ein weiteres unverbundenes Repo.

## 7. Grenzen

- Der Subagent hat Zeilen grob gezählt und nicht gebaut; Reife beruht auf Dateien, nicht auf Läufen.
- Webquellen teils sekundär (markiert); Fuchsia-Status, SpacemiT-Preise, CHERIoT-Tapeout, CRA-Steward-Datum sind nicht primär belegt.
- Toolchain-Befunde sind Momentaufnahme dieses Macs.
- Nichts verändert, nichts installiert.

## 8. Quellen

Referenzstacks: github.com/oxidecomputer/hubris · hubris.oxide.computer · trustworthy.systems (seL4, Heiser 2026) · phoronix.com/news/asterinas-0.18 · usenix.org/conference/atc25/presentation/peng-yuke · redox-os.org/news/this-month-260131/ · phoronix.com/news/redox-os-april-2026 · pbxscience.com (Fuchsia, sek.) · phoronix.com/news/ubuntu-risc-v-2026 · canonical.com/blog/risc-v-profiles-why-is-rva23-significant · wasi.dev/releases · swift.org/blog/embedded-swift-improvements-coming-in-swift-6.4/ · phoronix.com/news/Nova-Driver-LPC-2026 · lowrisc.org (Sonata) · thetechoutlook.com (CHERIoT-Tapeout, sek.) · arxiv.org/abs/2605.03822 (KVerus, Atmosphere)
Regulatorik und Supply Chain: slsa.dev/faq · hoganlovells.com (CRA 2026) · jonesday.com (CRA 24h) · ncsc.gov.ie/cra/
Eigene Messungen: `command -v` über Toolchains, `rustup target list --installed`, `swift sdk list`, `find`/`grep`/`git log` über /Users/manuel/workspace (ohne Archive, Worktrees, Klone).
