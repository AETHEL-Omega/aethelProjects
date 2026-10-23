# aethelProjects

**Portfolio-Analyse des AETHEL-Workspace.** Ein read-only Werkzeug, das den gesamten
Workspace vermisst und daraus einen entscheidbaren Blick macht: Git-Zustand, was **nicht
auf main** ist, Zweck, Reifegrad, Positionierung, Aufräum-Vorschläge — und eine
forensische Sicht auf das Hässliche, das Schöne und das Interessante.

> Ausschließlich lesend. Es wird nichts gelöscht, verschoben, committet oder gepusht.

## Das Problem, das es löst

Die folgenden Zahlen sind historische Beispiele vom Erststand, keine aktuelle Inventur.

Unter `~/workspace` liegen 329 Verzeichnisse mit Git — aber nur **208 echte Repositories**.
122 Verzeichnisse sind Worktrees, die dieselbe Historie teilen. Wer naiv zählt, kommt auf
**617.524 Commits und 70.047 Branches** — die wahren Zahlen sind **25.376 Commits und
3.169 Branches**. Faktor ~30.

Zusätzlich sind 11.995 Commits auf keinem main-Branch gelandet — 32 % aller Arbeit des
Workspace. Diese Zahl sah vorher niemand, weil sie nirgends workspace-weit erhoben wurde.

## Installation

Keine Installation nötig — nur Python ≥ 3.11 und `git`:

```bash
cd ~/workspace/aethelProjects
PYTHONPATH=src bin/aethel-projects scan --root ~/workspace --json /tmp/portfolio.json
```

Optional in die AIX-Laufzeitumgebung deployen (siehe [docs/INTEGRATION.md](docs/INTEGRATION.md)):

```bash
cp bin/aix-projects ~/bin/aix-projects && chmod +x ~/bin/aix-projects
```

## Nutzung

```bash
aethel-projects inventory --root ~/workspace --format json --out /tmp/inventory.json
aethel-projects scan      --root ~/workspace --json scan.json   # JSON-Snapshot
aethel-projects report    --root ~/workspace --format md|html   # Portfolio-Report
aethel-projects audit     --root ~/workspace --format md|json   # Aufräum-Vorschläge
aethel-projects market    --root ~/workspace --format md|json   # Marktview + USP + Claims
aethel-projects forensics --root ~/workspace --format md|json   # hässlich / schön / interessant
```

Gemeinsame Optionen: `--root` (Default `~/workspace`), `--jobs` (Parallelität),
`--timeout` (je Git-Aufruf), `--manifest` (Pfad zu `projects.yaml`).

## Python-API

```python
from aethel_projects import scan_workspace, render_markdown

result = scan_workspace("~/workspace")
print(result.summary.repos)              # 208
print(result.summary.commits_not_on_main) # 11.995
print(render_markdown(result))
```

## Was es liefert

| Bereich | Inhalt |
|---------|--------|
| **Git-Zustand** | Commits (gesamt / auf main / **nicht auf main**), Branches, ungemergte Branches mit Vorsprung, ahead/behind origin, Dirty-State, letzter Commit |
| **Intent** | Kernzweck je Repo, mit Quelle und Konfidenz — **ohne Fund wird nichts erfunden** |
| **Reifegrad** | 0–100 nach AETHEL Engineering Standard v2, mit Teilpunkten |
| **Manifest-Abgleich** | Repos fehlen im Manifest / verwaist / Datum veraltet |
| **Aufräum-Vorschläge** | inaktiv, Duplikat, Stub, kein main, Worktree-Räumung — als Empfehlung |
| **Projektmanagement** | Aktivitätsstatus, Risikoklasse, priorisierte nächste Schritte |
| **Marktview** | Interne Positionierung im AETHEL-Portfolio, Kategorie-Abdeckung, USP-Kandidaten |
| **Marketing** | Einzeiler und Claims je Repo — jeder Claim nennt messbare Fakten |
| **Forensik** | Das Hässliche, das Schöne, das Interessante — mit Beobachtung und Vorschlag |

## Zwei Grundsätze

1. **Keine Doppelzählung.** Worktrees werden über `git rev-parse --git-common-dir`
   dedupliziert; Commits „nicht auf main" werden über `rev-list --all --not <default>`
   **einmal** gezählt, nicht pro Branch summiert.
2. **Keine Erfindungen.** Fehlender Remote ergibt `null`, nicht `0`. Ohne README/SPEC
   bleibt der Intent leer. Der Marktview ist als `internal` gekennzeichnet — er
   beschreibt das Portfolio, nicht den Weltmarkt.

## Projektstruktur

```
docs/SPEC.md          Anforderungen REQ-NNN
docs/DESIGN.md        Datenmodelle, Algorithmen
docs/ARCHITECTURE.md  Bausteine, ADRs
docs/TEST-CASES.md    TC-NNN ↔ REQ-NNN
docs/INTEGRATION.md   Anbindung an AIX, MCP und Nachbarprojekte
src/aethel_projects/  Implementierung (stdlib, keine Runtime-Dependencies)
tests/                pytest — läuft offline, ohne den echten Workspace
dna/genome.yaml       Software-DNA (Regenerations-Bauplan)
```

## Tests

```bash
PYTHONPATH=src python3 -m pytest tests/ -v
```

Die Suite baut ihre eigenen Mini-Git-Repos in `tmp_path` und berührt `~/workspace` nicht.

## Status

🟢 Solide — Spec, Design, Architektur, Testfälle, Tests, CI und DNA vorhanden.
Offen: Anbindung an `aethelScripts` (MCP-Tool) und Erweiterung um externe Marktdaten.

## Lizenz

Proprietär — © Manuel Wilde

## Vollständigkeit und GitHub-Kosten

`inventory` läuft rekursiv, auch durch versteckte Worktree- und Archivordner,
und erkennt Bare-Repositories. Es erfasst jeden Checkout mit HEAD, Branch und
Dirty-Zustand; gemeinsame Git-Verzeichnisse identifizieren zusammengehörige
Historien. Package-Manifeste außerhalb von Git erscheinen als Projektkandidaten.
Alle Einträge direkt im Workspace bleiben sichtbar, auch ohne Projektmarker.

JSON enthält ausgeschlossene Pfade, nicht verfolgte Symlinks und Lesefehler.
Generierte Verzeichnisse (`node_modules`, `target`, `build`, virtuelle Umgebungen
usw.) werden bewusst ausgelassen; vollständige Erfassung gilt nur innerhalb
dieser offengelegten Suchregeln. Ein Projekt ohne bekannte Marker ist kein
sicher erkennbares Softwareprojekt. Unterpakete sind keine eigenen Produkte.

Kein GitHub-API-Aufruf, Fetch, Push, Build, Modellaufruf oder Workflow-Dispatch.
Der Git-Zugang verweigert schreibende Subkommandos und blockiert Git-Transporte,
Lazy Fetch und externe fsmonitor-Aufrufe. Remote-Tracking-Refs sind lokale,
möglicherweise veraltete Daten. Die Existenz einer CI-Datei belegt weder einen
bestandenen Test noch kostenlose CI. Bestehende zeitgesteuerte GitHub-Workflows
werden durch diese lokale Analyse nicht deaktiviert; Kontobudget unbekannt.

Die Fabrik-Scores sind Dateistruktur-Heuristiken und kein Nachweis für
Produktabnahme, Integration, Umsatz oder Einsatzbereitschaft.

## Projektdossier und Projektmanagement-Input

```bash
bin/aethel-projects dossier --snapshot /tmp/portfolio.json --out /tmp/pm-input.json
```

Der Export `aethel.projects.pm-input/v1` verbindet Intent, dokumentierte Architektur,
Quellen mit SHA-256 und Auszügen, lokale Cargo-Pfadabhängigkeiten, Git-Forensik und
Klärungsfragen. Er ist ein vorgeschlagener Eingabevertrag für
`aethelProjectManagement`, noch keine verifizierte Integration in einen Consumer.
Details und Grenzen: [docs/PM-INPUT.md](docs/PM-INPUT.md).

`aix-input --input auftrag-entwurf.json --dossiers pm-input.json --out auftrag.json`
bindet den vorhandenen AIX-Engineering-Eingang an einen aktuellen Projektbefund.
Es ergänzt nur Kontext und prüft Identität/HEAD/Quellen/Aktualität. Compilation,
Freigabe, Rollenprüfung, Ausführung und Forge bleiben im bestehenden AIX-Weg.
