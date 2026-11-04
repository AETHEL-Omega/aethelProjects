# Zielbetriebsmodell: professionell und kybernetisch, mit knapper Kapazität

Stand 03.11.2026. Fünfter Teil der Workspace-Analyse. Antworten auf Manuels Fragen vom 03.11.: Nach welchen Maßstäben werden die Projekte bewertet, wo geht das über aethelProjects hinaus, welche Kriterien braucht aethelCompany, was fehlt für echte Arbeitsfähigkeit, wie läuft aethelCompany mit lokaler KI, warum führt die heutige Git-Arbeit in eine Sackgasse und was gehört „on top“ (Cursor, aethelLanding), welche Projekte sind strategisch und welche technologisch bedeutend, welche Dominosteine machen alles schneller, und wie arbeiten wir mit wenig Kapazität super effizient. Vorbilder: Cursor, aethelLanding, Siemens Teamcenter, Mendix, Xcelerator.

## 0. Kurzantworten

1. **Maßstäbe.** aethelProjects misst heute acht Dinge (Abschnitt 1.1). Ich bewerte darüber hinaus zehn weitere (Abschnitt 1.2), die noch kein Werkzeug misst; sie gehören in aethelCompany und aethelConsultant.
2. **aethelCompany-Kriterien** sind nicht-technisch: Geschäftsfall, Zielgruppe, Kanal, Preis, Kosten je Produkt einschließlich Modellkosten, Deckungsbeitrag, Zeit bis Nutzen, Risiko, Abhängigkeit, Portfolio-Balance, Kapazität (Manuels Stunden), Marke, Recht (Abschnitt 1.3).
3. **Arbeitsfähig** werden wir mit acht Dingen, von denen keines neu erfunden werden muss (Abschnitt 2).
4. **Lokale KI für aethelCompany:** Stufe 0 (Apple Foundation Models über `fm`) für Klassifikation, Extraktion, Zusammenfassung, Triage; Stufe 1 (MLX 32B lokal, läuft bereits auf :8181) für Entwürfe und Rat-Abruf; Urteil und Architektur bleiben bei Opus/Fable mit Beleg. Alles auf dem M5 Max in Unified Memory nebeneinander, mit 48 GiB Reserve (Abschnitt 3).
5. **Git-Sackgasse:** Branches und Worktrees als Zustandsträger skalieren nicht (88 Worktrees, 12.761 Commits außerhalb von main, drei Branches allein in aethelProjects mit überlappender Arbeit). On top gehört ein Kandidaten-Objekt mit Siegel, Verdikt, Receipt und Landung: aethelLanding, nach dem Vorbild von Cursors Cloud-Agenten (eigene VM je Lauf, PR als Ergebnis, Review-Bot, Rollout-Überwachung) und Teamcenters Änderungsobjekt mit Freigabestatus. Git wird Speicher, nicht Wahrheit (Abschnitt 4).
6. **Strategisch bedeutend:** aethelLanding, aixd (aethelAgentRuntime), aethelRegistry, aethelCompany, aethelConsultant, aethelProjects, aethelema, aethelBrowser, aethelCodeAnalyzer, aethelContainer. **Technologisch bedeutend:** aethelAgentRuntime, aethelContainer, aethelCodeAnalyzer, aethelBrowser (Foundation-Models-Brücke), aethelema (frb, P2P), aethel-omega, aix Code-Intelligenz, aethelHelix, osxQ, bit_encodings (Abschnitt 5).
7. **Erste Dominosteine** (in dieser Reihenfolge, jeder macht die nächsten billiger): Parität und Release, Registry mit Produkt-ID, Landung als Verb auf aethelAgentRuntime, Company und Consultant als Daten in aethelProjects mit Stufe-0-KI, Apple-first-Audit als Gate-Kriterium (Abschnitt 6).
8. **Wenig Kapazität:** eine Entscheidung pro Woche gebündelt, WIP eins für Manuel, nur Komponenten mit Konsument, keine Stufe-2-Arbeit vor Stufe 1, Mechanik an günstige Modelle, Urteil an eine getrennte Instanz nur bei Landung, nichts löschen sondern archivieren (Abschnitt 7).

## 1. Maßstäbe

### 1.1 Was aethelProjects misst (Werkzeug, reproduzierbar)

| Maßstab | Modul | Skala | Grenze |
|---|---|---|---|
| Git-Zustand: Commits außerhalb main, unmerged Branches, dirty, ahead/behind | metrics | Zahlen | sagt nichts über Wert |
| Reifegrad | maturity | 0–100 (README 10, SPEC 15, DESIGN 10, ARCHITECTURE 10, TEST-CASES 10, tests 20, CI 10, DNA 10, engineering.yaml 5) | misst Dateiexistenz |
| Stubs | stubs, findings | Marker, Datei-/LOC-Grenzen | Plattform-Boilerplate zählt mit |
| Absicht | intent | SPEC > README > Manifest, Konfidenz | README-Erstzeilen dominieren |
| Duplikate, Drift, verwaist | findings | Befunde | – |
| Register-Drift | registers (neu) | sechs Kategorien, Zähler | kein Netz |
| Schicht | stack (neu) | S0–S17, eigen/fremd, Konfidenz | Namensregeln |
| Inkubator-Reife | incubator (neu) | R0 Idee … R11 Betrieb, je Stufe Signale mit Beleg | Signale, nicht Nutzerurteil |
| Apple-first | applefirst (neu) | 0–100, Sprachanteile, Frameworks, Unified-Memory-Bewusstsein, Anti-Muster | Treffer, nicht Laufzeitmessung |
| Markt, Forensik, Fabrik, Kontinuität | market, forensics, factory, continuity | Sichten | heuristisch |

### 1.2 Was ich darüber hinaus bewerte (heute von Hand, künftig Company und Consultant)

| Maßstab | Frage | Heute messbar? | Gehört zu |
|---|---|---|---|
| Konsument | Wer ruft die Komponente auf? | teilweise (Registry fehlt) | Registry, Company |
| Vertrag | Ist die Grenze beidseitig getestet? | nein (0 von 7) | Contracts |
| Betrieb | Läuft es (launchd, Port, PID) oder liegt es? | ja, von Hand | Release, Registry |
| Hebel | Wie viele andere Bauteile hängen davon ab? | ja (vorschlaege.json, `hebt`) | Company |
| Zyklusgesamtkosten | Kosten bis geprüftes Ergebnis inkl. Fehlversuche, Nacharbeit, Wartezeit, Manuels Zeit | nein | Ledger, Eval |
| Kanon-Treue | Rust-Kern, Swift-Laufzeit, Python dünn, Apple-first, Zustand in Software | ab heute teilweise (applefirst) | Policy |
| Nutzerproblem | Wessen Problem löst es, zahlt jemand? | nein | Company |
| Risiko und Abhängigkeit | Single Point of Failure (Apple, Anthropic, OpenAI), Austrittsoption | nein | Company, Consultant |
| Position | eigen oder fremd je Schicht, Beschluss vorhanden? | nein | Company (RFD) |
| Regulatorik | CRA, DSGVO, Lizenzen | nein | Distribution, Company |

### 1.3 aethelCompany-Kriterien (nicht-technisch)

Je Produkt ein Geschäftsfall mit: Nutzerproblem (ein Satz), Zielgruppe, Kanal, Preis oder Nutzenform, Kosten je Monat (Modelle, Abos, Infrastruktur, Manuels Stunden), Deckungsbeitrag, Zeit bis erster Nutzen, Risiko (technisch, Markt, Recht), Abhängigkeiten, Portfolio-Klasse (Forschung, Infrastruktur, Produkt, Inhalt), Inkubator-Stufe, Marke und Botschaft, Rechtsrahmen, Entscheidung (Start, Weiter, Pause, Archiv) mit Datum und Beleg. Das ist Teamcenters Item mit Revision und Freigabestatus, übertragen auf Produkte.

## 2. Was fehlt, damit wir realistisch arbeitsfähig werden

1. Ein Kern, der läuft, aus Release: aethelAgentRuntime als aixd, Parität grün.
2. Eine Registry mit Produkt-ID, die alle Regel- und Clientdateien erzeugt.
3. Landung als Verb mit Receipt statt Merge von Hand.
4. Company- und Consultant-Daten (Geschäftsfall, Rat) an einem Ort, zunächst in `analysen/` von aethelProjects.
5. Ein Cockpit, das Kreise, Kandidaten und Entscheidungen zeigt: aethelema liest aixd.
6. Stufe-0-KI (fm) im Betrieb für Triage, Klassifikation, Zusammenfassung, mit Eval.
7. Ein Wochentakt: eine Company-Sitzung von 30 Minuten mit gebündelten Entscheidungen aus dem Cockpit.
8. Apple-first als Gate-Kriterium, beginnend mit dem Python-Anteil von aethelScripts.

## 3. aethelCompany mit lokaler KI betreiben

| Stufe | Modell | Ort | Aufgaben für Company | Grenze |
|---|---|---|---|---|
| 0 | Apple Foundation Models (3B, 8k, `fm`, `apple_fm_sdk`, `fm serve`) | On-Device | Portfolio-Klasse klassifizieren, Geschäftsfall-Felder aus SPEC/README extrahieren (`@Generable`), Tor-Kriterien prüfen (erfüllt/nicht), Wochenbericht zusammenfassen, Aufträge triagieren | kein Urteil; Eval mit Apple Evaluations vor Betrieb; Lizenz durch Manuel bestätigen |
| 1 | MLX lokal (Qwen2.5-Coder-32B-4bit läuft auf :8181, ca. 20 GB; Qwen3 27B konfiguriert) | On-Device, GPU, Unified Memory | Entwürfe von Geschäftsfällen und RFDs, Vergleich mit Consultant-Kriterien, Rat-Abruf (RAG über Spotlight-Index oder FTS5 im Runtime-Graph), mechanische Texte (Worklog, Protokoll) | kein Review, keine Architektur (Manuel 28.10.) |
| 2 | Opus/Fable | Cloud, bezahlt (Abo) | Urteil, Architektur, Integration, Landung | nur mit Kostenklasse im Ledger |

Betrieb auf dem M5 Max 128 GB: ein 32B-4bit-Modell (ca. 20 GB), das Systemmodell (ca. 2 GB), vier Gate-Container und aethelema laufen gleichzeitig; Regel bleibt ≥ 48 GiB frei. `fm serve` liefert einen Chat-Completions-Endpunkt für den Python-Rand, die Swift-Laufzeit nutzt `LanguageModelSession` direkt. Company-Daten liegen in aixd (SQLite), Sicht in aethelema, Entscheidungen als Zustand mit LocalAuthentication-Beleg. Kostenklasse lokal = 0 wird im Ledger geführt, nicht angenommen.

## 4. Die Git-Sackgasse und was „on top“ gehört

Befund: Git trägt heute Zustand, den es nicht tragen kann. 88 Worktrees, 12.761 Commits außerhalb von main, in aethelProjects drei Branches mit überlappender Arbeit (codex, stubs, wip-Rettung), Deploy aus Worktrees, Parität rot. Jeder Branch ist ein Kandidat ohne Objekt, jeder Merge ein Urteil ohne Beleg.

| Vorbild | Prinzip | Übertragung auf AETHEL |
|---|---|---|
| Cursor Cloud Agents, Projects, Bugbot, Rollouts | Lauf in eigener VM, Ergebnis ist ein PR mit Review-Bot, Rollout überwacht Deploy und schlägt Revert vor, nichts merged automatisch | Lauf im Gate-Container, Ergebnis ist ein Kandidat mit Receipt, Verdict mit drei Sensoren, Landung als Verb, Rollout-Kreis K-E4-paritaet |
| aethelLanding (candidate, seal, verdict, ledger, CAS-Worktree) | Kandidat wird versiegelt (Digest), beurteilt, gelandet, im Ledger geführt; inhaltsadressiert statt branch-adressiert | wird installiert und zur einzigen Landungstür; Branches werden Kandidaten mit Ablauf; Landung schreibt main |
| Teamcenter Änderungsobjekt (ECR/ECO) mit Freigabestatus, Betroffenheitsanalyse, Bulk-Revert | Änderung ist ein Objekt mit Zustand, Beteiligten, Betroffenen, Rückweg | Kandidat trägt Auftrag, Vertrag, Betroffene (Konsumenten aus Registry), Rückbauklasse; Revert ist Limbus-Route |
| Mendix (Modell ist Wahrheit, Code wird erzeugt; Agenten arbeiten am Modell) | Wahrheit liegt im Modell, nicht in Textdateien | Wahrheit liegt im Kandidaten-Objekt und Receipt in aixd; Git speichert Dateien |
| Xcelerator (kuratiertes Portfolio, Marktplatz, Partner) | Komponenten mit Katalog und Verträgen statt loser Repos | Registry als Katalog, Verträge als Eintrittsbedingung |

Betriebsregel ab Landung: Niemand committet auf main. Jede Änderung ist ein Kandidat (Worktree mit Ablauf, von der Fabrik erzeugt), bekommt Receipt und Verdict, und aethelLanding landet. Was nicht landet, geht nach Ablauf in den Limbus, nicht ins Nichts.

## 5. Strategische und technologische Bedeutung

| Rang | Strategisch bedeutend | Warum |
|---|---|---|
| 1 | aethelLanding | einzige Tür, die die Git-Sackgasse schließt; Kreis K-E2 |
| 2 | aixd (aethelAgentRuntime) | Wahrheit, Ledger, Freigabe; alle Kreise hängen daran |
| 3 | aethelRegistry | Produkt-ID; beendet fünf Register und 826 Regelorte |
| 4 | aethelCompany | Entscheidung als Zustand; ohne sie entscheidet der Chat |
| 5 | aethelConsultant | Rat an einem Ort, wirkt an drei |
| 6 | aethelProjects | Messorgan; ab heute mit Inkubator und Apple-first |
| 7 | aethelema | Cockpit auf Mac, iPhone, Windows; Verbund |
| 8 | aethelBrowser | größtes substanzielles Produkt; Foundation-Models-Brücke |
| 9 | aethelCodeAnalyzer | Code-Sensor; Vorbild für Verträge |
| 10 | aethelContainer | Isolation; Voraussetzung hermetischer Gates |

| Rang | Technologisch bedeutend | Warum |
|---|---|---|
| 1 | aethelAgentRuntime | Rust, Ledger, Policy, Compliance, 55 Werkzeuge, Verträge `aethel.*.v1` |
| 2 | aethelContainer | Daemon, Stacks, WASI-Tasks; Brücke zu Apple Containerization |
| 3 | aethelCodeAnalyzer | Rust-Analyse, 200 Tests, `capability.json` |
| 4 | aethelBrowser | 133 Dateien mit FoundationModels; Metal, Core ML, ANE-Evidenz |
| 5 | aethelema | Flutter+Rust (frb), Ed25519, P2P |
| 6 | aethel-omega | Wissen, Claims, Atlas, 143 Tests |
| 7 | aix Code-Intelligenz | ast-grep, Sprengradius, Bisect, Mutationstest; voraus gegenüber Cursor |
| 8 | aethelHelix | aktive Forschung (31.10.), Träger-Codierung |
| 9 | osxQ / osxq-pennylane | Quantensimulator auf MLX, eigenes Device |
| 10 | bit_encodings, Memristor-Scaffolds | Rechenmodell-Vorarbeit |

Nicht in der Liste, aber groß: aiderDesktop (238 Crates ohne Betrieb), aethel-v6 (141k Zeilen), aethelDeepLearning (166k Zeilen). Sie sind Bestand, kein Hebel, bis ein Konsument existiert.

## 6. Die ersten Dominosteine

| # | Dominostein | Was fällt danach von selbst | Aufwand |
|---|---|---|---|
| 1 | **Parität und Release**: `~/bin`, MCP-Server, Runtime aus signiertem Release; `aix_doctor` grün; Kreis K-E4-paritaet geschlossen | jeder weitere Schnitt läuft mit bekanntem Code; Fehlersuche hört auf, Geister zu jagen | klein |
| 2 | **Registry mit Produkt-ID**, erzeugt projects.yaml, CLAUDE.md, AGENTS.md, Cursor-Regeln, MCP-Registries | 826 Regelorte werden einer; `registers` meldet Drift null; Company und Incubator haben einen Schlüssel | mittel |
| 3 | **Landung als Verb** auf aethelAgentRuntime: Kandidat, Receipt, Verdict, Landung; aethelLanding installiert | Git-Sackgasse endet; Review wird Software; Branches bekommen Ablauf | mittel |
| 4 | **Company und Consultant als Daten** in `aethelProjects/analysen/` (vorschlaege, kreislaeufe, ab jetzt geschaeftsfaelle.json und rat.json) mit Stufe-0-KI (fm) für Klassifikation und Zusammenfassung | Entscheidungen bekommen einen Ort ohne neue Infrastruktur; Wochen-Sitzung hat eine Vorlage | klein |
| 5 | **Apple-first-Audit als Gate-Kriterium**, erster Fall aethelScripts: Python dünn, Rust/Swift-Komponenten, Umbauplan je Modul | Kanon wird Messwert; der größte Python-Block (1.741 Dateien) bekommt einen Pfad | klein (Messung), groß (Umbau, in Schnitten) |

## 7. Super effizient mit wenig Kapazität

1. **Manuel entscheidet einmal pro Woche**, gebündelt, aus dem Cockpit; dazwischen laufen nur freigegebene Schnitte.
2. **WIP eins für Entscheidungen, drei für Schnitte**, nie mehr.
3. **Kein Bauteil ohne Konsument**, keine Stufe-2-Arbeit vor Stufe 1.
4. **Mechanik an günstige Modelle** (Lesen, Zählen, Gerüste, Worklogs), Urteil an eine getrennte Instanz nur bei Landung, Stufe 0 für Triage.
5. **Jeder Lauf hinterlässt ein Receipt**, kein Chat als Gedächtnis.
6. **Nichts löschen, alles archivieren**, aber Archiv ist Archiv: aiderDesktop, Theorie-Repos, tote Plists werden markiert, nicht gepflegt.
7. **Messen vor Bauen**: `registers`, `stack`, `incubator`, `applefirst` laufen vor jedem Portfolio-Beschluss.
8. **Eine Analyse-Ablage**: alles, was dieser Chat erzeugt hat, liegt unter `analysen/` und ist mit einem Befehl abrufbar; der nächste Radar-Lauf ergänzt, statt neu zu beginnen.
