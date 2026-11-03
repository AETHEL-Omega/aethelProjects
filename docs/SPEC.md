# SPEC — aethelProjects

> WAS soll die Software können? Eine Requirement = eine prüfbare Aussage.
> Jede REQ wird in [TEST-CASES.md](TEST-CASES.md) durch ≥1 TC abgedeckt.
> Anforderungs-Format laut `.aethel/engineering.yaml` → `method.spec_format`.

## Zweck (ein Satz)

`aethelProjects` ist das Portfolio-Werkzeug des AETHEL-Workspace: Es vermisst alle
Git-Repositories, berechnet den wahren Git-Zustand (Commits, Branches, was **nicht auf
main** ist), gleicht ihn gegen das Manifest ab, leitet Reife, Intent, Positionierung und
Alleinstellungsmerkmale ab und liefert daraus einen entscheidbaren Projektmanagement-,
Markt- und Marketing-Blick — **ausschließlich lesend**.

## Problem (Ausgangslage)

Der Workspace unter `~/workspace` enthält 329 Verzeichnisse mit Git, aber nur **208 echte
Repositories** — 122 Verzeichnisse sind Worktrees, die dieselbe Historie teilen. Wer die
Zahlen naiv zählt (ein `git`-Aufruf pro Verzeichnis), bekommt Ergebnisse, die um den
Faktor ~30 zu hoch sind: 617.524 statt 25.376 Commits, 70.047 statt 3.169 Branches.

Die vorhandene Werkzeuglandschaft deckt die Einzelaspekte ab, aber nicht die Gesamtsicht:

| Fähigkeit | Existiert | Wo | Lücke |
|---|---|---|---|
| Commit-Zahl je Repo | ja | `~/bin/_aix_workspace_review.py:444-460` (dedupliziert über `--git-common-dir`) | — |
| Commits **nicht auf main** | ja, **pro Repo** | `~/bin/_aix_rueckstand.py:63-64` | **kein Workspace-Driver** |
| Branch-Liste | ja, pro Repo | `~/bin/_aix_werkzeuge.py:2244-2281` | kein Workspace-Sweep |
| Dirty-State | ja | `~/bin/_aix_workspace_review.py:550-561` | — |
| Zweck/Description | ja | `~/bin/_aix_workspace_review.py:64-76` (README-Auszug) | nur Auszug, kein Intent |
| Kategorisierung | schwach | `projects.yaml` (Stand 2026-08-07, teils veraltet) | keine Domänen-Kategorien aus dem Code |
| Portfolio-Dashboard | nein | `~/bin/_aix_workspace_view.py` = **pro Repo** HTML | **fehlt komplett** |

`aethelProjects` schließt genau diese Lücke: **ein** read-only Kommando, das den
Gesamtzustand des Workspace als eine konsistente, deduplizierte Wahrheit liefert.

## Scope

- **In-Scope:**
  - Workspace-Discovery aller Git-Repositories, Worktree-Deduplizierung über `git rev-parse --git-common-dir`
  - Git-Metriken: Commits (total / auf main / **nicht auf main**), Branches (gesamt / unmerged),
    ahead/behind origin, Dirty-State, letzter Commit, Remote
  - Intent-Erkennung: Kernzweck je Repository, mit Konfidenz und Evidenz
  - Reifegrad: Scorecard-Anbindung (inhaltlich, 0–100, AETHEL Engineering Standard v2)
  - Manifest-Abgleich: fehlende/verwaiste Einträge, Datums-Drift, Kategorie-Drift
  - Aufräum-Vorschläge: inaktiv, Duplikat, Shared-Historie, Stub, Worktree-Räumung — **nur Vorschlag**
  - Portfolio-Report: JSON, Markdown, HTML
  - Projektmanagement-View: Status, Risiko, nächste Schritte je Repository
  - Marktview: interne Positionierung im AETHEL-Portfolio, Kategorie-Abdeckung, USP-Kandidaten
- **Non-Goals:**
  - **Kein Löschen, Verschieben, Committen, Pushen oder sonstiges Schreiben im Workspace.**
    Rückbau-Vorschläge sind ausschließlich Empfehlungen im Report.
  - Keine externen Marktdaten (Wettbewerber, Trends) — der Marktview ist **intern**
    (Portfolio- statt Weltmarkt) und als solcher gekennzeichnet.
  - Keine Code-Inhaltsanalyse (kein LLM, kein Embedding) — Intent wird regelbasiert abgeleitet.
  - Kein Ersatz für `workspace-manifest` (dieses bleibt die kanonische Registrierung).

## Anforderungen

| ID | Prio | Anforderung (MUST/SHOULD/MAY) | Akzeptanzkriterium |
|----|------|-------------------------------|--------------------|
| REQ-001 | MUST | Das System MUSS alle Git-Repositories unterhalb des Workspace-Root finden und jedes Repository **genau einmal** erfassen, auch wenn es als Worktree vorliegt. | Dedup-Schlüssel ist `git rev-parse --path-format=absolute --git-common-dir`; N Verzeichnisse mit `.git` ergeben ≤N Repos, und alle Worktree-Verzeichnisse eines Repos teilen denselben Schlüssel. |
| REQ-002 | MUST | Das System MUSS pro Repository die Commits **nicht auf dem Default-Branch** eindeutig zählen (ein Commit zählt einmal, auch wenn er auf 5 Branches liegt). | Zählung über `git rev-list --count --all --not <default>`; die Summe über alle Repos ist ≤ der Summe aller Einzel-Branch-Zählungen. |
| REQ-003 | MUST | Das System MUSS Branches unterscheiden in *gesamt*, *unmerged* und *nicht auf main*. | `unmerged` = Branches mit `default..branch` > 0 Commits; je Branch wird die Commit-Zahl ausgewiesen. |
| REQ-004 | MUST | Das System MUSS ahead/behind gegenüber `origin/<default>` sowie den Dirty-State (Anzahl geänderter Dateien) erfassen. | Fehlender Remote wird als `unknown` ausgewiesen, **nicht** als 0 — Unwissenheit ist kein Befund. |
| REQ-005 | MUST | Das System MUSS einen stabilen JSON-Schema-Output liefern. | `scan --json` erzeugt ein Objekt mit `schema`, `generated_at`, `summary` und `repos[]`; gleiche Eingabe → gleiche Feldstruktur. |
| REQ-006 | MUST | Das System MUSS einen lesbaren Markdown-Report und einen HTML-Report erzeugen. | `report --format md|html` erzeugt Dateien mit Summary, Ranglisten, Kategorietabelle und Detailtabelle. |
| REQ-007 | MUST | Das System MUSS **ausschließlich lesend** arbeiten. | Kein Modul führt `git checkout`, `git commit`, `git branch -d`, `git worktree remove`, `rm` oder `mv` aus; ein Test belegt die Abwesenheit solcher Aufrufe. |
| REQ-008 | MUST | Das System MUSS eine CLI mit den Subcommands `scan`, `report`, `audit` und `market` anbieten. | `aethel-projects --help` listet alle vier; jeder Subcommand endet mit Exit-Code 0 bei Erfolg. |
| REQ-009 | SHOULD | Das System SOLL den **Intent** je Repository bestimmen: Kernzweck, Konfidenz (hoch/mittel/niedrig) und Evidenz (Quelle + Fundstelle). | Intent stammt priorisiert aus `docs/SPEC.md` → `README.md` → Manifest-Description; ohne Fund wird `null` geliefert, **nichts wird erfunden**. |
| REQ-010 | SHOULD | Das System SOLL den **Reifegrad** je Repository bestimmen (0–100, AETHEL Standard v2) und die Teilbewertung offenlegen. | Teilpunkte README/SPEC/DESIGN/ARCHITECTURE/TEST-CASES/tests/CI/DNA/engineering.yaml sind einzeln ausgewiesen; Summe = Score. |
| REQ-011 | SHOULD | Das System SOLL das Manifest (`projects.yaml`) gegen den Ist-Zustand abgleichen. | Erkannt werden: im Manifest fehlend, verwaist (lokal weg), veraltetes `last_commit`, Kategorie-Drift zwischen Manifest und Ableitung. |
| REQ-012 | SHOULD | Das System SOLL **Aufräum-Vorschläge** liefern: inaktiv, Duplikat, Shared-Historie-Klon, Stub/Leer, verwaister Worktree. | Jeder Vorschlag nennt Repo, Grund, Schweregrad und die konkrete Ziel-Aktion; **kein Vorschlag löst eine Aktion aus**. |
| REQ-013 | SHOULD | Das System SOLL eine **Projektmanagement-View** liefern: Aktivitätsstatus, Risikoklasse, Reifegrad und priorisierte nächste Schritte. | Jedes Repository erhält Status (aktiv/inaktiv), Risiko (niedrig/mittel/hoch) und ≥1 Handlungsvorschlag, wenn Handlungsbedarf besteht. |
| REQ-014 | MAY | Das System DARF eine **Marktview** liefern: Positionierung im AETHEL-Portfolio, Kategorie-Abdeckung und USP-Kandidaten. | Positionierung ist **intern** und als `scope: internal` gekennzeichnet; USP-Kandidaten nennen die messbare Beobachtung, aus der sie folgen. |
| REQ-015 | SHOULD | Das System SOLL einen **Marketing-Output** erzeugen: je Repository einen Einzeiler und Claim-Formulierungen, gestützt auf messbare Fakten. | Claims enthalten keine Zahlen, die nicht aus dem Scan stammen; fehlende Evidenz erzeugt keinen Claim. |
| REQ-016 | MUST | Das System MUSS mit Python ≥ 3.11 laufen und MUSS eine Testsuite mit echten Assertions besitzen, die ohne Netzwerk und ohne existierenden Workspace läuft. | `pytest` grün mit Fixtures auf temporären Git-Repos; die Tests bauen ihre eigenen Mini-Repos. |

## Ergänzung 23.10.2026: Erfassung und PM-Input

| ID | Prio | Anforderung (MUST/SHOULD/MAY) | Akzeptanzkriterium |
|----|------|-------------------------------|--------------------|
| REQ-017 | MUST | Die Inventur MUSS tiefe/versteckte Worktrees, Git-Verzeichnisse ohne Checkout und Nicht-Git-Projektkandidaten unterscheiden und Erfassungsgrenzen offenlegen. | `inventory` nennt jeden Kandidaten, Deduplizierung, Fehler, Ausschlüsse und externe Worktree-Registrierungen; defekte Git-Verweise werden nicht zu Nicht-Git-Projekten. |
| REQ-018 | MUST | Projektdossiers MÜSSEN Intent, Architekturquellen, Git-Forensik und belegte Klärungsfragen als PM-Input exportieren. | `dossier --snapshot` liefert `aethel.projects.pm-input/v1`, lokale Repository-ID, datierte Herkunft, Quellen-Hashes und explizit nicht verifizierte Implementierung; kein Auftrag wird ausgeführt. |

| REQ-019 | MUST | Der AIX-Anschluss MUSS Projektbelege ausschließlich an den Kontext eines bestehenden unfreigegebenen Engineering-Eingangs binden. | Scope/Modus/Orakel/Rechte bleiben identisch; Projektidentität, HEAD, Quellenhash und Aktualität geprüft; kompilierte/freigegebene Inputs, Mehrdeutigkeit, Drift und Pfadausbruch blockieren. |

## Ergänzung 03.11.2026: Analysen-Ablage, Register-Abgleich, Schichtenkarte

Komponente: `aethelProjects@aethel.projects.analysen/v1` (Ablage), `aethelProjects@aethel.projects.register-drift/v1` (Abgleich), `aethelProjects@aethel.projects.stack/v1` (Schichtenkarte). Herkunft: Workspace-Analyse 03.11.2026 (vier Berichte unter `analysen/2026-11-03/`).

| ID | Prio | Anforderung (MUST/SHOULD/MAY) | Akzeptanzkriterium |
|----|------|-------------------------------|--------------------|
| REQ-020 | MUST | Projektanalysen MÜSSEN versioniert im Repo abgelegt und über die CLI auffindbar sein. | `analysen/INDEX.json` (Schema `aethel.projects.analysen/v1`) führt jede Analyse mit ID, Datum, Titel, Pfad, SHA-256, Scope, Zusammenfassung; `analyses --list`, `--show ID` (Prüfsumme wird geprüft, Abweichung wird als Warnzeile ausgegeben), `--register PATH` (einzige Schreiboperation in `analysen/`, nur `INDEX.json`, atomar über mkstemp, nur Dateien innerhalb `analysen/`, Pfadflucht blockiert; `--out` darf nicht in die Ablage zeigen, auch nicht in anderer Schreibung); `hebt`-Verweise in `vorschlaege.json` müssen auf vorhandene Vorschlags- oder Kreislauf-IDs zeigen. |
| REQ-021 | MUST | Vorgeschlagene Projekte und definierte Kreisläufe MÜSSEN als maschinenlesbare Register vorliegen und ausgebbar sein. | `analysen/vorschlaege.json` (`aethel.projects.vorschlaege/v1`: id, name, zweck, komponente, vertrag, ebene, stufe, hebt, bestand, status, quelle) und `analysen/kreislaeufe.json` (`aethel.projects.kreislaeufe/v1`: id, name, ebene E0–E6/META, takt, sollwert, sensor, vergleicher, stellglied, stoergroessen, besitzer, status offen/teilweise/geschlossen, fehlt); `analyses --proposals|--loops|--stats` in md und json; Schemafehler werden abgelehnt. |
| REQ-022 | MUST | Die vier lokalen Projektregister (Manifest, Scan, Projektprofile, Aufträge) MÜSSEN gegeneinander abgeglichen werden, ohne Netz; die GitHub-Organisation wird nicht abgefragt. | `registers --snapshot` meldet: Repos ohne Manifest-Eintrag, tote Manifest-Einträge, nicht registrierte Worktrees, Profile (`.aix/project-profile.json`) ohne Manifest oder ohne Repo, Auftragsbezüge (`auftraege.jsonl`) auf unbekannte Repos, Manifest-Alter in Tagen, Zähler; `--fail-on-drift` liefert Exit 1 bei Drift; kaputte Zeilen und ungültiges JSON werden gezählt, nicht geparst. |
| REQ-023 | SHOULD | Jedes Repo SOLL einer Stack-Schicht (S0–S17, SX) mit Herkunft eigen/fremd/unklar, Reife, Konfidenz und Beleg zugeordnet werden; leere Schichten werden genannt. | `stack` ordnet nach Namensregeln und Dateimarkern (`no_std`, Verilog, `capability.json`, `Package.swift` mit XPC, `pubspec.yaml`, `Cargo.toml [workspace]`, `flake.nix`/`Dockerfile`) zu; Worktrees werden übersprungen; Ausgabe je Schicht und je Repo in md und json. |
| REQ-024 | MUST | Ein Leitstand MUSS alle Register und die jüngsten Läufe auf einer Seite verdichten, ohne neu zu rechnen. | `cockpit` liest Index, Vorschläge, Kreisläufe und die jüngste JSON-Ausgabe von `registers`, `stack`, `incubator`, `applefirst` aus `analysen/`, zeigt Kennzahlen mit Quelle, abgeleitete Lücken („Was fehlt“), Dominosteine (größter Hebel), offene Kreisläufe, Verteilungen; Ausgabe md, json (`aethel.projects.cockpit/v1`), html; kaputte oder fremde JSON-Dateien stören nicht. |
| REQ-025 | MUST | Jedes Repo MUSS auf Apple-first geprüft werden: Sprachanteile, Apple-Frameworks, Unified-Memory-Bewusstsein, Anti-Muster, Score 0–100 mit Grade und Befunden. | `applefirst` liefert je Repo Score, Grade (Apple-first, teilweise, vernachlässigt, fremdgeführt, ohne Code), Python-Anteil, Frameworks, Unified-Memory-Treffer, Anti-Muster (Docker lokal, sandbox-exec, ML ohne mps/coreml/MLX, subprocess-lastig, große Bash-Skripte, launchd ohne SMAppService, numpy ohne MLX, Electron, Modellzugang nur HTTP) und Findings `applefirst-*`; `--min-score N` als Gate mit Exit 1; Schema `aethel.projects.applefirst/v1`. |
| REQ-026 | MUST | Die Inkubator-Reifeleiter MUSS je Repo die höchste erreichte Stufe von R0 Idee bis R11 Betrieb mit Belegen je Signal und der nächsten Lücke liefern, abhängig von der Portfolio-Klasse (forschung, infrastruktur, produkt, inhalt). | `incubator` prüft je Stufe alle Signale (Dateimarker, LOC, Tests, CI mit Testkommando, Doku, Lizenz, Lock, Version, Plattformreife, Vertriebsreife, Betrieb; RF Reproduzierbar für Forschung, RI Vertrag für Infrastruktur); eine nicht erreichte Stufe blockiert höhere; Ausgabe md und json (`aethel.projects.incubator/v1`). |

## Akzeptanzkriterien (gesamt)

- `pytest` läuft grün ohne Netzwerk und ohne Zugriff auf den echten `~/workspace`.
- `inventory` legt Suchregeln, jeden lokalen Git-Kandidaten, Bare-Repositories, Nicht-Git-Projektkandidaten und Fehler offen; Repo-Zahlen werden aktuell gemessen statt historisch festgeschrieben.
- Die Summe der Commits „nicht auf main" liegt unter der Summe der Einzel-Branch-Zählungen.
- Kein Modul enthält einen schreibenden Git-Aufruf (durch Test belegt).
- `scorecard.sh` aus `workspace-manifest` bewertet das Repo ≥ 80 (Professional).

## Offene Fragen

- Soll `aethelProjects` die kanonische Projekt-Registrierung **übernehmen** (und
  `workspace-manifest` ablösen) oder **daneben** laufen? → aktuell: **daneben**; das Manifest
  bleibt die Single Source of Truth, `aethelProjects` liest und meldet Drift.
- Sollen Extern-Marktdaten (Wettbewerber-Recherche) später über einen Import dazukommen?
  → als REQ-014-Erweiterung vorgesehen, aktuell Non-Goal.
