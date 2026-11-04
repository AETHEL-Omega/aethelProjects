# Leitstand

Eine Seite für alles: Ablage, Vorschläge, Kreisläufe, Register, Schichten, Inkubator, Apple-first.

| Kennzahl | Wert | Quelle | Hinweis |
|---|---:|---|---|
| Analysen | 11 | `analysen/INDEX.json` | - |
| Vorschläge | 30 | `analysen/vorschlaege.json` | existiert 1, in-arbeit 1, vorgeschlagen 28 |
| Kreisläufe | 22 | `analysen/kreislaeufe.json` | offen 17, teilweise 5 |
| Register-Drift | 375 | `2026-11-03/register-abgleich-2026-11-03.json` | Summe der Abweichungen |
| Leere Schichten | 5 | `2026-11-03/schichtenkarte-2026-11-03.json` | - |
| Inkubator | 322 Repos | `2026-11-03/inkubator-2026-11-03.json` | -: 2, R0: 94, R1: 9, R2: 171, R3: 32, R4: 6, R5: 4, R6: 1, R7: 2, R9: 1 |
| Apple-first | 322 Repos | `2026-11-03/applefirst-2026-11-03.json` | Apple-first: 10, fremdgeführt: 50, ohne Code: 22, teilweise: 70, vernachlässigt: 170 |

## Was fehlt (aus den Daten abgeleitet)

- Kein Kreislauf ist geschlossen: Loop-Registry im Kern (aixd) fehlt
- Manifest ist 66 Tage alt: Registry mit Produkt-ID fehlt
- 5 Stack-Schichten ohne eigenes Repo

## Dominosteine (Vorschläge mit größtem Hebel)

- B5 aixd: hebt 8
- B1 aethelRegistry: hebt 7
- B2 aethelContracts: hebt 6
- B8 aethelContainer.sandbox: hebt 4
- B9 aethelAppleRuntime: hebt 4

## Offene Kreisläufe (17)

- K-E0-werkzeug (E0): fehlt PreToolUse-Tor; Policy-as-Code; Containerization statt sandbox-exec
- K-E2-review (E2): fehlt Review als Software statt Anweisung; Rubrik aus Consultant
- K-E2-landung (E2): fehlt Landung als Verb; Receipt-Verifier; Limbus-Route in Landung
- K-E3-reife (E3): fehlt Konsument (aethelCompany/aethelFactory); Reife nach Funktion
- K-E3-intent (E3): fehlt Intent aus Code; Vergleicher Absicht/Code
- K-E3-register (E3): fehlt Produkt-ID; Konfigurations-Compiler
- K-E3-inkubator (E3): fehlt Inkubator; Tor-Kriterien; Company-Entscheidung
- K-E4-paritaet (E4): fehlt Release-Pipeline; Stellglied Neustart aus Release
- K-E4-kosten (E4): fehlt Kostenklasse im Ledger; Router nach Gesamtkosten; Budget je Produkt (Company)
- K-E5-portfolio (E5): fehlt aethelCompany; Portfolio-Zustand; Kennzahlen
- K-E5-kanon (E5): fehlt Policy-Compiler; Abgleichsensor
- K-E5-rat (E5): fehlt aethelConsultant; Rückkopplungsfeld je Rat
- K-E6-markt (E6): fehlt Nutzungssensor; Geschäftsfall je Produkt
- K-E6-plattform (E6): fehlt Radar-Dienst
- K-META-harness (META): fehlt Eval je Version; Versionierung der Harness; äußerer Prüfer
- K-S3-audit (META): fehlt aethelAudit
- K-TWIN (META): fehlt aethelTwin; Ledger-Export als Zeitreihe

## Register-Drift

| Kategorie | Anzahl |
|---|---:|
| missing_in_manifest | 76 |
| dead_manifest_entries | 0 |
| unregistered_worktrees | 174 |
| profiles_without_manifest | 97 |
| profiles_without_repo | 28 |
| auftraege_unknown_repos | 0 |
| manifest_age_days | 66 |

## Leere Stack-Schichten

- S1 Firmware
- S6 Sprache/Compiler/Toolchain
- S13 Sicherheit/Identität
- S16 Distribution
- S17 Entscheidung/Doku/Wissen-Text

## Inkubator-Verteilung

| Stufe | Repos |
|---|---:|
| - | 2 |
| R0 | 94 |
| R1 | 9 |
| R2 | 171 |
| R3 | 32 |
| R4 | 6 |
| R5 | 4 |
| R6 | 1 |
| R7 | 2 |
| R9 | 1 |

## Apple-first

| Grade | Repos |
|---|---:|
| Apple-first | 10 |
| fremdgeführt | 50 |
| ohne Code | 22 |
| teilweise | 70 |
| vernachlässigt | 170 |

Schlechteste zehn:

- aider: 5 (fremdgeführt, Python 91 %)
- cognee: 5 (fremdgeführt, Python 97 %)
- rllm: 5 (fremdgeführt, Python 91 %)
- pydantic-ai: 10 (fremdgeführt, Python 100 %)
- amrlib: 15 (fremdgeführt, Python 99 %)
- deepseek-coder: 15 (fremdgeführt, Python 100 %)
- dspy: 15 (fremdgeführt, Python 99 %)
- guidance: 15 (fremdgeführt, Python 96 %)
- instructor: 15 (fremdgeführt, Python 100 %)
- spacy: 15 (fremdgeführt, Python 95 %)

## Analysen in der Ablage

- 2026-11-03 applefirst-audit-2026-11-03: Apple-first-Audit
- 2026-11-03 chat-protokoll-arbeitsweise-2026-11-03: Protokoll dieses Chats: Arbeitsweise, Recherche, Verluste
- 2026-11-03 inkubator-reifeleiter-2026-11-03: Inkubator-Reifeleiter
- 2026-11-03 neue-projekte-kreislaeufe-rat: Neue Projekte, Kreisläufe und der Ort des Rats
- 2026-11-03 register-abgleich-2026-11-03: Register-Abgleich
- 2026-11-03 schichtenkarte-2026-11-03: Schichtenkarte
- 2026-11-03 werkzeuge-die-werkzeuge-bauen: Werkzeuge, die Werkzeuge bauen: rekursives Bootstrapping für AETHEL
- 2026-11-03 workspace-analyse-2026-11-03: Gesamtanalyse des Workspace ~/workspace – Projekte, Erfassung, Fabrik, Lücken, Stand der Technik
- 2026-11-03 workspace-analyse-2026-11-03-ergaenzung-technologie-architektur: Ergänzungsbericht: Technologie, Architektur, Kybernetik auf macOS 27
- 2026-11-03 workspace-analyse-2026-11-03-gesamtstack-bauteile: Gesamtstack-Bericht: was fehlt, wo nicht Best Practice, welche Bauteile zuerst
- 2026-11-03 zielbetriebsmodell-und-dominosteine: Zielbetriebsmodell: professionell und kybernetisch, mit knapper Kapazität

