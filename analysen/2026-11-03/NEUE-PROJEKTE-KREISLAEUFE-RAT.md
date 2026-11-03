# Neue Projekte, Kreisläufe und der Ort des Rats

Stand 03.11.2026. Vierter Teil der Workspace-Analyse. Teile 1–3 liegen im selben Ordner (`WORKSPACE-ANALYSE-2026-11-03*.md`). Antwort auf Manuels Fragen vom 03.11.: Was macht aethelProjects und wie wird es besser? Wo liegen die Analysen? Wie hängt es mit aethelCompany, aethelFactory, aethelCodeAnalyzer zusammen? Welche Projekte wurden auf GitHub angelegt? Wie werden wir wirklich kybernetisch? Was fehlt betriebswirtschaftlich, marketingtechnisch, volkswirtschaftlich, IT-technisch, strategisch auf jeder Ebene, und wohin gehört dieser Rat?

## 0. Die kurzen Antworten

1. **Was aethelProjects macht:** Es ist das Messorgan der Projekt-Ebene (E3). Es liest den Workspace nur, vermisst Git-Zustand, Reifegrad, Absicht, Stubs, Duplikate, Marktsicht, Forensik, Code-Befunde (über aethelCodeAnalyzer) und erzeugt Dossiers als PM-Eingabe. Es entscheidet nichts und verändert nichts. Mit dieser Ausbaustufe bekommt es vier neue Sichten: Analysen-Ablage (`analyses`), Register-Abgleich (`registers`), Schichtenkarte (`stack`) und die Vorschlags- und Kreislauf-Listen.
2. **Wie es besser wird:** Es bekommt einen Konsumenten (aethelCompany für die Firmensicht, aethelFactory für Aufträge), misst Funktion statt Dateiexistenz, bezieht Stub- und Intent-Urteile aus Code und SPEC statt README-Zeilen, gleicht die fünf Register ab, und seine Analysen werden versioniert im Repo abgelegt statt in gitignorierten Ordnern.
3. **Wo die Analysen liegen:** `aethelProjects/analysen/<Datum>/*.md`, Index in `analysen/INDEX.json`, Vorschläge in `analysen/vorschlaege.json`, Kreisläufe in `analysen/kreislaeufe.json`. Aufruf: `aethel-projects analyses --list`, `--show <id>`, `--proposals`, `--loops`. Kopien bleiben zusätzlich unter `~/workspace/_docs/`.
4. **Zusammenhang:** aethelCodeAnalyzer ist der Code-Sensor (E1/E3), aethelProjects das Projekt-Messorgan (E3) und ein Teil des Radars (S4), aethelFactory die Ausführung (E2/E4, VSM S1–S3), aethelCompany die Firmensteuerung (E5, VSM S5 mit S4) in nicht-technischer Information: Portfolio, Geschäftsfall, Kunde, Markt, Preis, Kosten, Rollen, Recht. aethelConsultant ist das Rat-Organ, das Company, Factory und Projects mit Grundsätzen, Mustern und Entscheidungsvorlagen versorgt. Heute existieren nur Analyzer und Projects als Code; Factory ist Spezifikation ohne Code; Company und Consultant existieren nicht.
5. **Auf GitHub neu angelegt:** nichts. Alle neuen Projekte sind Vorschläge in `vorschlaege.json`. Anlegen erst nach Manuels Freigabe und nur über die Registry, damit kein sechstes Register entsteht.
6. **Wie wir kybernetisch werden:** Abschnitt 5. Kurz: jeden Kreis registrieren, Sollwert und Sensor in Software, Vergleicher und Stellglied als Übergang der Zustandsmaschine, Takt innen schneller als außen, Alarmkanal, Audit, Radar, Politik als Daten. Erst Dämpfer, dann Verstärker.

## 1. Die Organe und ihr Ort im Regelkreis

| Organ | Ebene | VSM | Informationsart | Heute | Konsumiert | Liefert an |
|---|---|---|---|---|---|---|
| aethelCodeAnalyzer | E1, E3 | S1-Sensor | Code-Befunde (Rust, Dart tief; Rest fehlt) | läuft, 200 Tests | Quellcode | aethelProjects, Gate |
| aethelProjects | E3, Teil S4 | S3*-Sensor, S4 | Projektmessung: Reife, Absicht, Stubs, Drift, Markt, Forensik, Schichten | läuft, 134+ Tests, kein Konsument | Workspace, Analyzer, Manifest | Company, Factory, Consultant |
| aethelFactory (Worklane) | E2, E4 | S1, S2, S3 | Aufträge, Schnitte, Gates, Landungen, Kapazität | 1.459 Zeilen SPEC, kein Code; Betrieb als Skriptflotte in aethelScripts | Projects-Dossiers, Company-Prioritäten, aixd | Receipts an Projects und Company |
| aethelCompany | E5 | S5, S4 | nicht-technisch: Portfolio-Entscheidung, Geschäftsfall, Kunde, Markt, Preis, Kosten, Kapital, Rollen, Recht, Marke | fehlt (nur RFC 0002 im workspace-manifest) | Projects, Consultant, Radar, Ledger-Kosten | Prioritäten und Budgets an Factory; Kanonänderungen |
| aethelConsultant | alle, vor allem E5 | S4/S5-Berater, S3*-Rubrik | Grundsätze, Muster, Playbooks, Checklisten, Entscheidungsvorlagen je Disziplin (BWL, Marketing, VWL, IT, Strategie, Recht, Organisation, Kybernetik) | fehlt; Rat liegt in 289 CLAUDE.md, 478 Akten, drei Berichten | Forschung, Radar, Erfahrungen (Receipts) | Company (Entscheidungen), Factory (Review-Rubriken, Harness-Kontext), Projects (Prüfregeln), Incubator (Stage-Kriterien) |
| aethelIncubator | E3→E4 | S4→S1 Übergang | Idee → Konzept → Prototyp → Produkt → Betrieb → Archiv mit Toren | fehlt; heute entstehen Repos ohne Tor | Ideen, Company-Kriterien, Consultant-Checklisten | Registry-Einträge, erste Aufträge |

## 2. Neue Projekte (konsolidiert aus Teil 1–3, ergänzt)

Vollständig und maschinenlesbar in `vorschlaege.json`. Hier die Übersicht nach Zweck. Stufe: 1 = die Fabrik baut sich selbst, 2 = die Fabrik baut den Stack.

**Steuerung und Rat (E5)**
- **aethelCompany**: Firmensteuerung als Daten, nicht als Technik. Objekte: Produkt (Produkt-ID aus der Registry), Geschäftsfall (Nutzerproblem, Zielgruppe, Preis, Kosten, Deckungsbeitrag, Risiko), Portfolio-Entscheidung (Start, Weiter, Pause, Archiv) mit Beleg, Budget je Produkt und Kostenklasse, Rollen und Verantwortliche, Marke und Botschaft, Rechtsrahmen (Lizenz, CRA, DSGVO). Sicht in aethelema, Daten in aixd. Vertrag `aethel.company/v1`.
- **aethelConsultant**: der Ort allen grundsätzlichen Rats. Struktur: Disziplinen × Ebenen (Abschnitt 4), je Zelle Grundsätze, Muster, Anti-Muster, Checklisten, Kennzahlen, Entscheidungsvorlagen (RFD), Quellen. Jeder Ratschlag hat Version, Gültigkeit, Belegstelle und Rückkopplung („wurde befolgt, Ergebnis“). Wird von Company (Entscheidung), Factory (Review-Rubrik, Harness-Kontext, Hooks), Projects (Prüfregeln) und Incubator (Tor-Kriterien) maschinell gelesen. Vertrag `aethel.consultant/v1`. Manuel 03.11.: „das brauchen wir ja selbst, wo aller grundsätzlicher Rat liegt“, und: „den brauchen wir auf jeden Fall auch in der aethelCompany“.
- **aethelIncubator**: Tore für heterogene Projekte von aethelHelix (Forschung) über aethelOmegaMikro bis heritageBibel und Nuru (Inhalt, Produkt). Stufen: Idee (eine Seite: Problem, Wer, Warum jetzt) → Konzept (SPEC, Markt, Kosten) → Prototyp (ein Nutzer, ein Beleg) → Produkt (Registry-Eintrag, Vertrag, Distribution) → Betrieb (Kennzahlen) → Archiv. Jedes Tor hat Kriterien aus Consultant und eine Company-Entscheidung. Vertrag `aethel.incubator/v1`.
- **aethelRadar** (S4): Dienst, der Plattform-Releases, Changelogs, arXiv, Markt und Register-Drift liest und Ereignisse an Company und Consultant liefert. Dieser Bericht ist ein Radar-Lauf von Hand.
- **aethelTwin** (Überraschung): digitaler Zwilling der Fabrik. Simulation der Kreise (WIP, Gate-Kapazität, Modellkosten, Durchsatz, Totzeiten) als System-Dynamics-Modell aus dem Ledger, bevor ein Stellglied geändert wird. Antwort auf „Gate-Stau 14.10.“ vor dem nächsten Stau.

**Kern und Fabrik (E2–E4, Stufe 1)**
- **aixd** (aus aethelAgentRuntime): Zustandsmaschine, Ledger, Lease, Freigabe, Policy, Loop-Registry, Modellkatalog, Agentenidentität.
- **aethelRegistry**: Produkt-ID; erzeugt projects.yaml, CLAUDE.md, AGENTS.md, Cursor-Regeln, MCP-Registries, Plists.
- **aethelContracts**: Vertragsgenerator (`capability.json` → Schema, Konsumententests, Stubs) und IDL-Compiler (WIT → Rust, Swift, Dart).
- **aethelRelease**: signierte Releases mit SBOM, SLSA-Provenance, Paritätskreis.
- **aethelLanding** (Ausbau): Verdict mit drei Sensoren, Landung als Verb, Receipt-Verifier (S3*).
- **aethelContainer** (Ausbau): Hülle über Apple Containerization, Gate-Image mit Digest, WASI-Komponenten.
- **aethelAppleRuntime**: der Swift-Harness mit sieben Teilsystemen, ACP- und MCP-Server, Skills, Hooks, Subagenten.
- **aethelEval**: Zyklusmessung je Harness-Version, Stufe-0-Kette, Modell; Reward-Hacking-Fälle; Apple Evaluations.
- **aethelPolicy**: Kanon als Daten mit Version → Hooks, Rechte, Kostenklassen, Alarmschwellen.
- **aethelOmega** (Ausbau als aethelMemory): Gedächtnis mit Provenienz aus Commits, Receipts, Freigaben.
- **aethelSupplier**: Lieferantenkonten für Fremdagenten (Codex, Copilot, Cursor, Cloud) mit Identität, Rolle, Kostenklasse, Budget, Bewertung.
- **aethelAudit** (S3*): unangekündigte Stichproben: Receipts nachrechnen, Digests prüfen, Testdateien vergleichen, Parität messen.

**Projekte und Produkte (E3, Stufe 1–2)**
- **aethelProjects** (Ausbau): dieser Schnitt plus Spec-Graph-Compiler (SPEC → Aufgabengraph → Wellen), Intent aus Code, Reife nach Funktion.
- **aethelProjectManagement**: Software-PLM: Revision, Komponentenstückliste, Änderungsobjekt mit Betroffenheit, Digital Thread SPEC → Code → Test → Receipt → Betrieb.
- **aethelVariants**: Variantenmodell und Generator für die aethel_core-Linie (34 Kopien werden Konfiguration).
- **aethelSDK**: eine Bibliothek je Sprache für Identität, Auftrag, Wissen, Receipt, Modellzugang.
- **aethelDistribution**: Signatur, Notarisierung, Update-Kanal, Rücknahme, CRA-Meldeprozess, SBOM je Release.

**Stack (Stufe 2)**
- **aethelStackMap** (in aethelProjects begonnen: `stack`), **aethelSystem** (Systemschicht auf macOS 27, Linux-Gast), **aethelCompute** (Simulator-Vertrag für Memristor, vChip, Helix, Quanten), **aethelResearchGate** (Forschung wird nur über Spec, Test, Konsument Komponente), **aethelToolchain** (Ziele als Vertrag).

## 3. Kreisläufe, definiert

Vollständig in `kreislaeufe.json` (22 Kreise). Jeder Kreis hat Sollwert, Sensor, Vergleicher, Stellglied, Störgrößen, Takt, Besitzer, Status und die Liste der fehlenden Glieder. Auszug:

| ID | Ebene | Takt | Sollwert | Sensor | Stellglied | Status |
|---|---|---|---|---|---|---|
| K-E0-werkzeug | E0 | ms | Policy je Werkzeug | PreToolUse-Hook | erlauben, verweigern, Sandbox | offen |
| K-E1-lauf | E1 | min | Akzeptanzkriterien, Budget | Tests, Analyzer, Token-Zähler | nächster Schritt, Subagent, Abbruch, Fortsetzungsauftrag | teilweise |
| K-E2-review | E2 | h | Vertrag, Rückbauklasse | getrennte Review-Instanz, Rubrik aus Consultant | Nacharbeit, Freigabe zum Gate | offen (Anweisung) |
| K-E2-gate | E2 | h | Gate grün hermetisch | Gate-Container, zurückgehaltene Tests, Testdatei-Wächter | Landen, Zurückweisen | teilweise |
| K-E2-landung | E2 | h | Receipt vollständig | Receipt-Verifier | Landung als Verb, Rückbau-Route | offen |
| K-E3-reife | E3 | Tage | Reifegrad-Ziel je Produkt | aethelProjects-Scan | Aufträge erzeugen, Stub archivieren | offen (kein Konsument) |
| K-E3-intent | E3 | Tage | Absicht = Code | Intent aus SPEC, Code-Abgleich | SPEC nachziehen oder Code zurückbauen | offen |
| K-E3-register | E3 | Tage | ein Register | `registers`-Abgleich | Registry-Eintrag, Archiv | offen (Sensor ab heute) |
| K-E3-inkubator | E3 | Wochen | Tor-Kriterien je Stufe | Incubator-Prüfung mit Consultant-Checkliste | Tor öffnen, zurückstellen, archivieren | offen |
| K-E4-wip | E4 | h | drei Spuren | Lease-Zähler in aixd | Zuteilen, Warten | teilweise (Umgebungsvariable) |
| K-E4-kapazitaet | E4 | min | 4 Gate-Worker, ≥ 48 GiB frei | Speicher, Warteschlange | Worker starten, drosseln | teilweise |
| K-E4-paritaet | E4 | h | Betrieb = Release | `aix_doctor`, Digest-Vergleich | Neustart aus Release | offen (Sensor rot, kein Stellglied) |
| K-E4-kosten | E4 | je Lauf | Gesamtkosten bis geprüftes Ergebnis | Ledger: Fehlversuche, Nacharbeit, Wartezeit, Kostenklasse | Router: Modell und Ort wechseln | offen |
| K-E5-portfolio | E5 | Monate | Portfolio-Entscheidung | Company-Kennzahlen aus Projects und Ledger | Start, Weiter, Pause, Archiv | offen (RFC) |
| K-E5-kanon | E5 | Monate | Kanon = Code | Policy-Abgleich Kanon ↔ Hooks ↔ Betrieb | Kanon ändern oder Betrieb ändern | offen |
| K-E5-rat | E5 | Quartal | Rat wirkt | Consultant-Rückkopplung: befolgt, Ergebnis | Rat ändern, Rat streichen | offen |
| K-E6-markt | E6 | Quartal | Nutzerproblem gelöst | Nutzung, Fehlerberichte, Markt (Radar) | Produktdefinition, Geschäftsfall | offen |
| K-E6-plattform | E6 | Release | Plattform genutzt statt nachgebaut | Radar: Apple-Guides, Changelogs | Komponente ablösen | offen (dieser Bericht) |
| K-META-harness | META | Wochen | Zykluskennzahlen besser | aethelEval | Harness-Version wechseln | offen |
| K-S3-audit | quer | Stichprobe | Receipts stimmen | aethelAudit | Alarm, Sperre | offen |
| K-ALGEDON | quer | sofort | Kosten, Cloud unter LOCAL_AI_ONLY, Sicherheit, Speicher | Schwellen aus Policy | Stopp, Nachricht an Manuel, Beleg | teilweise (nur LOCAL_AI_ONLY) |
| K-TWIN | META | vor Änderung | Vorhersage = Beobachtung | aethelTwin | Stellglied-Änderung freigeben oder verwerfen | offen |

## 4. Was fehlt aus betriebswirtschaftlicher, marketingtechnischer, volkswirtschaftlicher, IT-technischer und strategischer Sicht, je Ebene

Jede Zelle nennt die Lücke. Der Rat dazu gehört nach aethelConsultant (Inhalt) und wird von aethelCompany (Entscheidung), aethelFactory (Umsetzung) oder aethelProjects (Messung) konsumiert.

| Sicht | E3 Projekt | E4 Portfolio / Fabrik | E5 Firma | E6 Umwelt |
|---|---|---|---|---|
| **Betriebswirtschaft** | kein Geschäftsfall je Projekt: Nutzerproblem, Zielgruppe, Preis, Kosten, Deckungsbeitrag fehlen in allen 55 Produkten | Kosten je Schnitt nur als Token, nicht als Gesamtkosten (Fehlversuche, Nacharbeit, Wartezeit, Manuels Zeit); kein Budget je Produkt; WIP ohne Kostenwirkung | keine Gewinn- und Verlustsicht, keine Liquiditätsplanung, keine Make-or-Buy-Regel außer Kanon-Sätzen; Abo-Kosten (Codex, Claude, Cursor) nicht je Produkt zugeordnet | kein Marktpreis-Abgleich, keine Zahlungsbereitschaft gemessen |
| **Marketing** | Intent aus README-Erstzeilen; keine Positionierung, kein Nutzenversprechen, kein Name-Test (Athelix, Nuru, heritageBibel nebeneinander) | `market`-Modul erzeugt Claims, die niemand prüft oder nutzt | keine Marke, keine Botschaft, kein Kanal, keine Zielgruppe für AETHEL als Ganzes; Kiraa zeigt, dass „lokal-nativ auf Apple Silicon“ ein verkaufbares Versprechen ist | keine Wettbewerberliste mit Datum (Cursor, Kiro, Antigravity, Devin, Kiraa, Mendix) als Datensatz, nur in Berichten |
| **Volkswirtschaft** | Lizenz- und Kostenklasse je Komponente nicht als Daten (nur CLAUDE.md) | keine Abhängigkeitsökonomie: welche Fremdleistung (Apple, Anthropic, OpenAI) ist Single Point of Failure, zu welchem Preis, mit welcher Austrittsoption | keine Regulatorik als Vertrag (CRA seit 11.09.2026, AI Act, DSGVO); keine Open-Source-Strategie (was offen, was eigen, welche Lizenz); keine Förder- oder Partnerlogik | Plattformzyklen (WWDC jährlich) und Modellpreise nicht als Zeitreihe verfolgt |
| **IT-Technik** | Reife misst Dateien, nicht Funktion; Analyzer nur Rust/Dart; Stubs nur als Marker | zwei Kerne, vier Sandboxen, drei Gedächtnisse, Deploy-Drift, keine Verträge (Teil 2) | keine Architekturentscheidungen als RFD mit Status; Kanon als Prosa an 289 Orten | Plattform (FM, Core AI, Containerization, Xcode-Agenten, ACP) ungenutzt |
| **Strategie** | kein Tor zwischen Idee und Repo: Projekte entstehen ohne Entscheidung (Inkubator fehlt) | keine Hebel-Reihenfolge im Betrieb (Teil 3, Abschnitt 4 liefert sie); Stufe 2 wird vor Stufe 1 gebaut | kein Zielbild mit Zeitachse, kein Portfolio-Zustand (Start/Weiter/Pause/Archiv), keine Entscheidung eigen/fremd je Schicht als Beschluss | kein Radar als Dienst; Forschung (Helix, Omega, v6) ohne Verwertungspfad |
| **Organisation / Kybernetik** | Lehren bleiben in Akten statt Tests | Kreise nicht registriert, S3* und S4 fehlen | S5 nicht maschinenlesbar; ein Mensch als einziger Vergleicher | Rückkopplung Betrieb → Anforderung fehlt |

**Wohin der Rat gehört:** Inhalt und Begründung in aethelConsultant (versioniert, mit Beleg und Rückkopplung). Entscheidung in aethelCompany (Zustandsobjekt mit Beleg). Durchsetzung in aixd-Policy und Factory (Hooks, Rubriken, Tor-Kriterien). Messung in aethelProjects. So liegt der Rat an einem Ort, wirkt an drei und wird an einem gemessen.

## 5. So werden wir wirklich kybernetisch

1. **Loop-Registry zuerst.** `aethel.loop/v1` in aixd; die 22 Kreise aus `kreislaeufe.json` werden eingetragen; aethelema zeigt je Kreis: Zeit seit letztem Schluss, fehlende Glieder. Ein Kreis ohne Eintrag existiert nicht.
2. **Jeder Sollwert ist ein Datum, kein Satz.** Reifegrad-Ziel, WIP, Kapazität, Budget, Kanon-Regel: alle als Werte in aixd mit Version.
3. **Jeder Sensor ist eine Abfrage mit Takt.** Scan, Analyzer, Ledger, Doctor, Radar laufen als Dienste und schreiben Messwerte, nicht Markdown.
4. **Jeder Vergleicher ist ein Übergang der Zustandsmaschine.** Illegale Übergänge sind Kompilierfehler (Kanon 6). Kein Vergleich im Chat.
5. **Jedes Stellglied ist eine Aktion mit Beleg.** Freigabe über LocalAuthentication, Landung als Verb, Zuteilung als Lease, Portfolio-Entscheidung als Zustand.
6. **Innen schneller als außen.** E0 ms, E1 min, E2 h, E3 Tage, E4 Wochen, E5 Monate. Der Gate-Stau war E2 langsamer als E4.
7. **Dämpfer vor Verstärker.** Registry, Verträge, Release, Policy vor Subagenten, Flotten, Varianten.
8. **S3* Audit ohne Ankündigung** (aethelAudit) und **algedonischer Kanal** (Stopp, Nachricht, Beleg) als eigene Organe.
9. **S4 Radar als Dienst**, S5 Politik als Daten. Dieser Bericht ist der letzte Radar-Lauf von Hand.
10. **Double-Loop:** jede Lehre wird ein Test an der Zustandsmaschine; aethelConsultant prüft vierteljährlich, ob befolgter Rat wirkte, und streicht, was nicht wirkt.
11. **Zweite Ordnung:** aethelEval und aethelTwin bewerten Änderungen am Regler selbst, bevor sie wirken; ein äußerer Prüfer, nie die Harness selbst.
12. **Ein Kriterium für „kybernetisch“:** Keiner der 22 Kreise hat den Status „offen“, und kein Kreis schließt über Chat oder Markdown.

## 6. Der Inkubator für heterogene Projekte

Manuel 03.11.: „Die Projekte sind sehr unterschiedlich, von aethelHelix, aethelOmegaMikro bis heritageBibel, Aethel Nuru.“ Darum vier Portfolio-Klassen mit eigenen Tor-Kriterien, aber einer Pipeline:

| Klasse | Beispiele | Idee → Konzept | Konzept → Prototyp | Prototyp → Produkt | Produkt → Betrieb |
|---|---|---|---|---|---|
| Forschung | aethelHelix, aethel-v6, aethelDeepLearning, osxQ, Memristor | Hypothese, Messgröße, Fremdstand | Experiment mit Digest im Ledger | Forschungs-Tor: Spec, Test, ein Konsument | Komponente im Stack |
| Infrastruktur / Fabrik | aixd, Registry, Harness, Consultant | Hebel (Fan-out), Vertrag | beidseitiger Vertragstest | Release mit Provenance | Kreis geschlossen |
| Produkt / App | aethelBrowser, aethelema, FamilyAppStore, youtubereader | Nutzerproblem, Zielgruppe, Preis, Kosten | ein Nutzer, ein Beleg | Registry, Vertrag, Distribution, CRA | Kennzahlen Nutzung, Fehler, Kosten |
| Inhalt / Kultur | heritageBibel, Nuru, vintage_radio | Zielgruppe, Rechte, Quelle | Inhalt mit Qualitätsprüfung | Distribution, Lizenz | Nutzung |

Jedes Tor: Kriterien aus aethelConsultant, Entscheidung in aethelCompany, Messung durch aethelProjects, Umsetzung durch aethelFactory. Zustand des Projekts (Idee, Konzept, Prototyp, Produkt, Betrieb, Archiv) steht in der Registry, nicht im Repo-Namen.
