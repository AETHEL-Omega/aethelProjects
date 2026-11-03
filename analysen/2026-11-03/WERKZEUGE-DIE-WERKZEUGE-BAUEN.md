# Werkzeuge, die Werkzeuge bauen: rekursives Bootstrapping für AETHEL

Stand 03.11.2026. Sechster Teil der Workspace-Analyse. Manuel 03.11.: „Wie können wir Werkzeuge bauen, mit denen wir Werkzeuge bauen, und dann Werkzeuge bauen und so weiter? Dieser Aspekt wurde sträflich vernachlässigt, ist aber strategisch von größter Bedeutung. Wir können es uns nicht leisten, Software nach Prinzipien von gestern zu entwickeln; das gilt für jeden technischen Aspekt wie auch für Domänen.“ Dieser Teil bringt Theorie (Bootstrapping, generative Programmierung, Sprachwerkbänke) und Forschung bis Oktober 2026 (selbstverbessernde Agenten, Skill- und Harness-Synthese, Code-Modus) zusammen und leitet daraus die Werkzeugkette für AETHEL ab.

## 0. Kurzfazit

1. Rekursives Werkzeugbauen hat drei bewährte Vorbilder: der Compiler-Bootstrap (Stufe 0 fremd, Stufe 1 baut sich selbst, Stufe 2 baut alles andere), die Sprachwerkbank (Sprache definieren → Editor, Prüfer, Generator fallen heraus) und die Software-Produktlinie (Variabilitätsmodell → Varianten werden erzeugt, nicht kopiert). AETHEL hat zu jedem Vorbild Bestand und zu keinem die Maschine.
2. Die Forschung 2026 hat das Thema von der Theorie in den Agentenalltag geholt: Agenten erzeugen Werkzeuge (EvoSkills, SkillSmith, CodeSkill, Tool-Making-Pipelines), Skills aus Spuren (SkillCraft, SkillGenBench, UPskill), und ganze Harnesses (Meta-Harness, AutoHarness, Agentic Harness Engineering, JIT-Agent, Self-Harness, Harness-Zero, OO-Harness). Die Darwin-Gödel-Maschine (ICLR 2026) zeigt offenes Selbstverbessern mit Archiv: SWE-bench von 20 % auf 50 %.
3. Die Gefahr ist bekannt und benannt: Werkzeuge, die Werkzeuge bauen, erben Fehler rekursiv (Thompsons „Trusting Trust“; Reward-Hacking bei EvilGenie; 34 % Einbruch synthetisierter Skills bei geänderten Werkzeugen, sek.). Gegenmittel sind Provenance je Artefakt, unabhängige Verifikation, die mit dem Erzeuger mitwächst, und ein Archiv statt Überschreiben.
4. Für AETHEL heißt das: Nicht noch ein Werkzeug, sondern fünf Werkzeugmacher (Abschnitt 4), jeder mit Vertrag, Eval und Archiv, in der Reihenfolge Vertragsgenerator → Komponentengenerator → Skill-Synthese → Harness-Evolution → Selbsthosting. Der Vertragsgenerator ist der erste, weil er jedes weitere Werkzeug sofort für Agenten nutzbar macht (MCP-Beschreibung, Konsumententest, Stubs aus einer Quelle).
5. „Prinzipien von heute“ je Aspekt stehen in Abschnitt 5 als Tabelle gestern/heute, damit kein Schnitt auf veralteter Praxis beginnt.

## 1. Drei Vorbilder aus der Theorie

| Vorbild | Prinzip | Was AETHEL davon hat | Was fehlt |
|---|---|---|---|
| **Compiler-Bootstrap** (Stufe 0: fremder Compiler baut den eigenen; Stufe 1: der eigene baut sich selbst; Stufe 2: er baut alles andere; Full-Source-Bootstrap von Guix und live-bootstrap aus einem 357-Byte-Seed als Gegenmittel gegen „Trusting Trust“) | Vertrauen entsteht, wenn der Erzeuger sich selbst reproduzieren kann und jede Stufe nachvollziehbar ist | Stufe 0 läuft (Claude, Codex, Cursor bauen Teile); Receipts mit Digests im Kanon | Stufe 1 (Fabrik baut ein eigenes Bauteil ohne Hand) fehlt; keine Provenance je Artefakt; Deploy aus Worktrees |
| **Sprachwerkbank** (JetBrains MPS, Spoofax, Racket `#lang`, Xtext: aus einer Sprach- oder Schemadefinition entstehen Editor, Prüfer, Generator, Doku) | Eine Definition, viele Werkzeuge | `capability.json` als Vertragsdefinition (ein Fall), `omega_validate_dag`, aix AST-Werkzeuge | Kein Generator, der aus dem Vertrag Tests, Stubs, MCP-Beschreibung, Doku erzeugt; 0 WIT/IDL-Dateien |
| **Software-Produktlinie** (Czarnecki/Eisenecker generative Programmierung; Greenfield/Short „Software Factories“; Feature-Modelle; Mendix: Modell ist Wahrheit) | Varianten werden konfiguriert, nicht kopiert; Domänenwissen steckt im Generator | aethel_core/design, Athelix (Low-Code), 34 Varianten als Rohstoff | Variabilitätsmodell und Generator fehlen; Forschung 2026 zeigt: LLM-gestützte Produktlinien und DSL-Engineering sind noch Lücke (Mapping-Studie über 86 Arbeiten: Modellgenerierung dominiert, Metamodellierung und DSL kaum) |

Ergänzende Linien: Forth und Lisp („grow a language“: kleine Kernsprache, der Rest wird in ihr geschrieben); von Neumanns universeller Konstruktor (Maschine, die Maschinen baut, braucht Bauplan und Kopierer getrennt); Toyotas Jidoka (Maschine stoppt sich selbst bei Fehler, das ist der algedonische Kanal); Nix (Build-Beschreibung erzeugt reproduzierbare Umgebungen, also Werkzeuge für Werkzeuge).

## 2. Forschungsstand 2026: Agenten, die Werkzeuge bauen

| Linie | Arbeiten (arXiv) | Kernaussage | Lehre für AETHEL |
|---|---|---|---|
| Werkzeug-Selbstentwicklung | EvoSkills 2604.01687 (mehrdateiige Skill-Pakete iterativ erzeugt und ko-evolutionär verifiziert), SkillSmith 2606.01314, CodeSkill 2605.25430 (Skills aus Trajektorien extrahiert, Skill-Bank mit GRPO trainiert), Tool-Making-Pipeline 2607.08010 (Werkzeugmacher erzeugt Kandidaten, repariert gegen gelabelte Fälle), RL mit Skill-Bibliothek 2512.17102, Survey Self-Evolving Coding Agents 2608.03392 | Werkzeuge entstehen aus Spuren erfolgreicher Läufe, werden gegen Fälle verifiziert und in einer Bank versioniert | Jeder Lauf hinterlässt Spur (Replay-Ledger existiert); ein Skill-Synthetisierer liest Spuren und schlägt `SKILL.md` plus Testfälle vor; Aufnahme nur über Eval |
| Skills aus Spuren | SkillCraft (Trajektorie → Abstraktion → Generalisierung → SKILL.md; +12 % auf verwandten Aufgaben, −34 % bei geänderten Werkzeugen, sek.), SkillGenBench 2605.18693, SkillsBench 2602.12670 (ohne, kuratiert, selbst erzeugt), „Demystifying Agent Skills“ 2608.14036, SKILL.md-Smells 2607.01456, UPskill (Hugging Face) | Destillierte Skills schlagen rohe Spuren; rohe Spuren schaden sogar; Skills brechen, wenn sich die Werkzeuge ändern | Skills tragen Werkzeugverträge als Abhängigkeit; Vertragsänderung löst Skill-Reeval aus (Kreis) |
| Harness-Evolution | Meta-Harness 2603.28052 (äußere Schleife sucht über Harness-Code, Proposer liest Code, Scores, Spuren aller Kandidaten; Gewinne auf TerminalBench-2), AutoHarness 2603.03329, Agentic Harness Engineering 2604.25850 (Engpass ist Beobachtbarkeit), AutoSaddler 2608.23041 (dauerhafte Updates aus Spuren), JIT-Agent 2608.25593, Self-Harness 2606.09498, Hierarchical Self-Improvement 2608.08466, Harness-Zero 2609.24974 (Agent als Harness), OO-Harness 2610.28380, AutoDesign 2608.13560 | Der Harness ist selbst Gegenstand automatischer Optimierung; Voraussetzung sind Evals und vollständige Spuren | aethelEval und Replay sind die Voraussetzung; Harness-Änderungen laufen als Kandidaten durch dasselbe Gate wie Code (Kreis K-META-harness, äußerer Prüfer) |
| Offenes Selbstverbessern | Darwin-Gödel-Maschine 2505.22954 (v3 März 2026, ICLR 2026): Archiv von Agenten, Eltern aus Archiv, Selbständerung nur mit empirischem Nachweis; SWE-bench 20 % → 50 %, Polyglot 14,2 % → 30,7 %; Ablationen zeigen: ohne Archiv oder ohne Selbständerung schlechter | Archiv statt Überschreiben; Nachweis statt Beweis | Limbus und Ledger sind das Archiv; jede Harness- oder Skill-Version bleibt abrufbar; „nichts wegwerfen“ ist hier Methode, nicht Vorsicht |
| Recursive Self-Improvement (Übersicht) | 2607.07663 (von begrenzter Selbstverfeinerung zu autonomen Forschungsschleifen), Continual Learning in Transition 2608.06216 | Grenzen: Bewertung, Sicherheit, Driftkontrolle | Jede Rekursionsstufe braucht einen Prüfer außerhalb (Kybernetik zweiter Ordnung) |
| Code-Modus und Werkzeugsuche | Anthropic Tool Search (Nov. 2025) und programmatischer Werkzeugaufruf (GA Feb. 2026; 150k → 2k Token in einem Beispiel, sek.), Cloudflare Code Mode (sek. 99,9 % weniger Eingabetoken bei 2.500 Endpunkten), Gateways 50–92 % | Agenten schreiben Code, der Werkzeuge aufruft, statt Werkzeuge einzeln zu rufen; Werkzeugbeschreibungen werden erst bei Bedarf geladen | aix (27) und Runtime (55) Werkzeuge immer geladen: Werkzeugsuche und Code-Modus senken Kosten; Vertragsgenerator liefert die Beschreibungen |
| Bibliotheks-Lernen | ReGAL (Refactoring zu Abstraktionen, geprüft gegen Ausgaben), LILO (LLM + Stitch-Kompression), Prospective Compression 2605.09985 (Abstraktionen für künftige Aufgaben wählen) | Gemeinsame Hilfsfunktionen entstehen durch Refactoring über viele Lösungen, geprüft gegen Tests | Die 1.006 `bin`-Skripte sind der Rohstoff für Bibliotheks-Lernen: wiederkehrende Muster werden Komponenten |
| Verifikation | Verification Horizon 2606.26300 (Verifizierer müssen ko-evolvieren), EvilGenie 2511.21654 (Reward-Hacking bei Codex und Claude Code) | Ein Werkzeug, das Werkzeuge baut, optimiert gegen seinen Prüfer | Prüfer werden mitgebaut: zurückgehaltene Tests, Testdatei-Wächter, Richter, Mutationstest (aix hat ihn) |

## 3. Warum das bei AETHEL vernachlässigt wurde (Befund)

- Werkzeuge entstanden als Antwort auf Vorfälle (478 Akten, 1.006 Skripte), nicht als Erzeugnis eines Generators. Jedes neue Problem erzeugte ein neues Skript statt eine Regel im Werkzeugmacher.
- Es gibt keine Spur→Skill-Schleife, obwohl der Replay-Ledger Spuren hat und `SKILL.md` als Standard existiert (6 Skills).
- Es gibt keinen Vertragsgenerator, obwohl `capability.json` als Vorbild existiert; deshalb hat jedes Werkzeug eine handgeschriebene MCP-Beschreibung oder keine.
- Harness-Änderungen (Prompts, Hooks, Rollen) laufen ohne Eval, also ohne Fitnessfunktion; es gibt nichts, was eine Verbesserung von einer Verschlechterung unterscheidet.
- Varianten werden kopiert (34), nicht erzeugt.
- Archiv ist Prinzip („nichts wegwerfen“), aber nicht Methode: alte Versionen von Skripten und Prompts sind nicht adressierbar, also nicht als Eltern nutzbar.

## 4. Die Werkzeugkette für AETHEL: fünf Werkzeugmacher

| # | Werkzeugmacher | Eingabe → Ausgabe | Verifikation | Archiv | Komponente@Vertrag | Hebt |
|---|---|---|---|---|---|---|
| W1 | **Vertragsgenerator** | `capability.json` (oder WIT) → JSON-Schema, Konsumententest-Gerüst, Client-Stubs (Rust, Swift, Dart, Python), MCP-Tool-Beschreibung, Doku-Abschnitt, Registry-Eintrag | beidseitiger Test gegen gemeinsame Fixture; Schemaprüfung | Vertragsversionen im Ledger | `aethelContracts@aethel.contract/v1` | jedes neue Werkzeug ist sofort agentennutzbar; Code-Modus und Werkzeugsuche bekommen ihre Beschreibungen |
| W2 | **Komponenten- und Variantengenerator** | Vorlage + Variabilitätsmodell + Registry-Eintrag → Paket/Crate/App mit Vertrag (W1), Tests, CI, Skill-Hülle, Plist | Erzeugtes baut und testet grün; `incubator` R3 sofort erreicht | Generator-Versionen, erzeugte Komponenten mit Herkunft | `aethelVariants@aethel.variant/v1` | 34 Varianten werden Konfiguration; jede neue Komponente beginnt vertragsfähig |
| W3 | **Skill-Synthetisierer** | Replay-Spuren erfolgreicher Läufe → `SKILL.md`-Kandidat mit Schritten, Werkzeugen, Fehlerbildern, Testfällen (SkillCraft-Prinzip: destillieren, nicht kopieren) | SkillsBench-artig: ohne, kuratiert, erzeugt; Aufnahme nur bei Gewinn; Werkzeugverträge als Abhängigkeit, Reeval bei Änderung | Skill-Versionen, Eltern-Spur | `aethelSkills@aethel.skill/v1` | Rollen (Merger, Reviewer, Gate) werden Skills, die sich aus eigener Arbeit verbessern |
| W4 | **Harness-Evolver** | Harness-Version + Eval-Ergebnisse + Spuren → Vorschlag einer Harness-Änderung als Kandidat (Meta-Harness-Prinzip) | aethelEval mit Zykluskennzahlen; äußerer Prüfer; Gate wie Code | Harness-Versionen als Archiv (DGM-Prinzip: Eltern wählbar) | `aethelEval@aethel.eval/v1` + `aethel.harness/v1` | der Harness verbessert sich messbar statt per Anweisung |
| W5 | **Selbsthosting** | Auftrag „neues Bauteil“ → W1–W4 bauen es über Spec-Compiler, Harness, Isolation, Verdict, Release, Registry ohne Hand | Stufe-1-Kriterium (Teil 3, 4.4) | Receipt je Bauteil | Fabrik gesamt | Stufe 2 wird möglich |

Reihenfolge und Begründung: W1 zuerst, weil er die kleinste Maschine mit größtem Fan-out ist und den heutigen Analyzer-Vertrag als Testfall hat. W2 danach, weil er W1 konsumiert und die Variantenlinie sofort bedient. W3 braucht Replay (existiert) und W1 (Werkzeugverträge). W4 braucht Eval und W3. W5 ist das Ziel, kein Bauteil.

## 5. Prinzipien von heute statt gestern, je Aspekt

| Aspekt | Gestern (so arbeitet die Fabrik heute) | Heute (Stand 2026) | Umsetzung |
|---|---|---|---|
| Werkzeugbau | Skript je Vorfall | Generator je Vertrag; Skills aus Spuren; Harness aus Eval | W1–W4 |
| Agentenarchitektur | Prompt und Shell-Flotte | Harness mit sieben Teilsystemen, Hooks pro Werkzeug, Subagenten in Isolation, Code-Modus, Werkzeugsuche, dauerhafte Ausführung mit Resume | aethelAppleRuntime |
| Verifikation | Tests grün | ko-evolvierende Verifizierer: zurückgehaltene Tests, Testdatei-Wächter, Richter, Mutationstest, Eval je Version | aethelLanding, aethelEval |
| Gedächtnis | Markdown-Akten | Gedächtnis mit Provenienz aus Commits und Receipts; destillierte Skills statt roher Spuren | aethelOmega, W3 |
| Modellnutzung | ein Router nach Tokenpreis | Stufen nach Aufgabe (On-Device 3B, lokal 32B, Cloud mit Beleg), Gesamtkosten bis geprüftes Ergebnis, Code-Modus | Modellkatalog in aixd |
| Plattform | Eigenbau neben dem System | Systemframeworks zuerst (Foundation Models, Core AI, Containerization, App Intents, XPC, Evaluations); Apple-first auf Unified Memory | Kanon 1, applefirst-Audit |
| Isolation | sandbox-exec | ein leichtes VM je Lauf (Containerization), Image-Digest im Receipt | aethelContainer |
| Zusammenarbeit | Branches und Merges von Hand | Kandidat, Receipt, Verdict, Landung; Git als Speicher | aethelLanding |
| Varianten | Kopien | Konfiguration aus Variabilitätsmodell | W2 |
| Entscheidungen | Chat | RFD mit Status, Policy als Daten, Freigabe als Ereignis | aethelCompany, aethelPolicy |
| Lieferkette | Deploy aus Worktree | signierte Releases, SBOM, SLSA-Provenance, Paritätskreis | aethelRelease |
| Protokolle | eigene Aufrufe | MCP 2026-07-28, ACP, A2A, Agent Skills, WASI 0.3 | Harness |
| Regulatorik | nicht betrachtet | CRA-Meldepflicht seit 11.09.2026, SBOM, Update-Kanal | aethelDistribution |
| Domänenwissen (BWL, Marketing, VWL, Recht) | implizit in Gesprächen | Rat als versionierte Daten mit Rückkopplung; Geschäftsfall je Produkt; Agenten als Lieferanten mit Konto | aethelConsultant, aethelCompany |
| Organisation | Mensch als einziger Regler | Kreise registriert, S3* Audit, S4 Radar, S5 Politik, algedonischer Kanal | Loop-Registry |

## 6. Erster Schnitt (klein, mit Hebel)

W1 Vertragsgenerator als Python-Übergangsmodul in aethelProjects oder als Rust-Crate neben aethelCodeAnalyzer: liest `capability.json`, erzeugt (a) JSON-Schema, (b) Konsumententest-Gerüst für den nächsten Konsumenten (aethelProjects), (c) MCP-Tool-Beschreibung, (d) Registry-Eintrag. Testfall: der bestehende Analyzer-Vertrag `aethel.code_analyzer.aix_findings.v1`. Orakel: beidseitiger Test grün gegen eine gemeinsame Fixture; `analyses --proposals` zeigt den Vertrag als `existiert`. Danach W2 mit der ersten aethel_core-Variante.

## 7. Grenzen

Zahlen aus Sekundärquellen sind markiert (sek.); arXiv-Arbeiten wurden über Zusammenfassungen und Suchtreffer erfasst, nicht vollständig gelesen. Die Werkzeugkette ist Entwurf; Aufwände sind nicht geschätzt.
