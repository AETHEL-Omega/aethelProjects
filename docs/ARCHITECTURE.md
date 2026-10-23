# ARCHITECTURE — aethelProjects

> STRUKTUR? Kontext, Bausteine, Entscheidungen (arc42-lite/C4 + ADRs).

## 1. Kontext (C4 Level 1)

```
        ┌───────────────────────────────────────────────┐
        │            AETHEL-Workspace (~/workspace)      │
        │  208 Repos · 329 Git-Verzeichnisse · 122 WT    │
        └───────────────────┬───────────────────────────┘
                            │  liest (git, Dateien)
                            ▼
        ┌───────────────────────────────────────────────┐
        │                  aethelProjects                 │
        │  scan → report → audit → market                │
        └────┬─────────────┬──────────────┬─────────────┘
             │             │              │
             ▼             ▼              ▼
        JSON/MD/HTML   findings      Marktview+USP
             │
             ▼
   ┌─────────────────────┐
   │ workspace-manifest   │  projects.yaml (kanonische Registrierung)
   │ (projects.yaml)      │  ← wird gelesen, Drift wird gemeldet, nie geschrieben
   └─────────────────────┘
```

**Trust-Boundary:** `aethelProjects` liest den Workspace. Es schreibt **ausserhalb**
des Workspace (nur in das Output-Verzeichnis, das der Aufrufer angibt). Es ist damit
ein **reines Analyse-Werkzeug**.

## 2. Bausteine (C4 Level 2)

```
aethel_projects/
├── models.py       Datenmodelle (frozen dataclasses)  — keine Logik, nur Form
├── gitio.py        Dünne Hülle um `git` (timeout, Fehler → None, kein Schreiben)
├── discovery.py    Workspace-Scan → Repo-Identitäten (Dedup via common_dir)
├── metrics.py      Git-Metriken je Repo (commits, branches, ahead/behind, dirty)
├── intent.py       Intent-Erkennung (REQ-009)
├── maturity.py     Reifegrad (REQ-010)
├── manifest.py     Manifest-Parser + Abgleich (REQ-011)
├── findings.py     Aufräum-/Risiko-Erkennung (REQ-012)
├── pmview.py       Projektmanagement-View (REQ-013)
├── market.py       Marktview, USP, Marketing-Claims (REQ-014, REQ-015)
├── scanner.py      Orchestrierung: discovery + metrics + Ableitungen → ScanResult
├── report.py       Renderer: JSON / Markdown / HTML
├── cli.py          argparse-CLI (dünne Hülle)
└── __init__.py     öffentliche API
```

### Schichten (hexagonal)

| Schicht | Module | Kennt |
|---------|--------|-------|
| **Domain** | `models.py` | nichts |
| **Ports** | `gitio.py` | `models` |
| **Adapter** | `discovery`, `metrics`, `intent`, `maturity`, `manifest`, `findings`, `pmview`, `market` | `models`, `gitio` |
| **Anwendung** | `scanner` | alle Adapter |
| **Präsentation** | `report`, `cli` | `models`, `scanner` |

Die Kernlogik (Intent, Reife, Findings, Markt) kennt **kein** `git` und **kein**
Dateisystem. Sie arbeitet auf Datenklassen. Deshalb sind sie ohne echten Workspace
testbar — die Tests bauen Mini-Repos in `tmp_path`.

## 3. Datenfluss

```
root
 └─ discovery.discover(root)
      → [(name, path, common_dir, worktree_paths)]
 └─ metrics.collect(repo)                ← parallel (ThreadPoolExecutor)
      → RepoReport(git-Zustand)
 └─ intent.infer(repo)      → Intent
 └─ maturity.score(repo)    → Maturity
 └─ manifest.compare(...)   → ManifestEntry + Drift
 └─ findings.detect(...)    → tuple[Finding]
 └─ pmview.build(...)       → ProjectManagementView
 └─ ScanResult(repos, findings, categories, summary)
```

`market.build(result)` und `pmview` arbeiten **ausschließlich** auf dem `ScanResult` —
der Marktview braucht also keine zweite Git-Runde.

## 4. Bausteine im Detail

### 4.1 `gitio.py` — die einzige Git-Schnittstelle

```python
def run_git(repo: Path, *args: str, timeout: int = 30) -> str | None:
    """Führt `git -C repo <args>` aus. Gibt stdout zurück, None bei Fehler/Timeout."""
```

**Harte Regel:** In `gitio.py` ist keine andere Git-Funktion erlaubt, und `run_git`
enthält **kein** `checkout`, `commit`, `push`, `branch -d`, `worktree remove`, `reset`,
`clean`, `rm`, `mv`. Das ist durch TC-007 maschinell belegt: der Test liest alle
Quelltextdateien und schlägt fehl, wenn ein verbotener Begriff in einem
Git-Aufruf-String auftaucht.

### 4.2 `discovery.py`

```python
def discover(root: Path) -> list[RepoIdentity]
```

Findet `.git` (Datei **oder** Ordner) rekursiv innerhalb offengelegter Suchregeln sowie Git-Verzeichnisse ohne Checkout, normalisiert den Common-Dir-Pfad
und gruppiert danach. Rückgabe: ein `RepoIdentity` pro Historie, mit Liste aller
Verzeichnisse.

### 4.3 `metrics.py`

```python
def collect(identity: RepoIdentity) -> RepoReport
```

Führt die in DESIGN §3.2 gelisteten `rev-list`-Aufrufe aus. Jeder Aufruf ist einzeln
fehlertolerant: `None` bei Fehler, `0` nur wenn das Kommando erfolgreich „0" sagt.

### 4.4 `scanner.py`

```python
def scan_workspace(root: Path, jobs: int = 8, timeout: int = 30) -> ScanResult
```

Paralleles Sammeln der Metriken über einen `ThreadPoolExecutor` (git-Aufrufe sind
I/O-gebunden; Threads genügen, kein Overhead durch Prozesse).

**Determinismus:** Ergebnisse werden nach `name` sortiert, Findings nach
`(severity, repo)`.

## 5. Schnittstellen

| Typ | Name | Richtung | Beschreibung |
|-----|------|----------|--------------|
| CLI | `aethel-projects` | Ein | Einstiegspunkt, delegiert an `cli.main` |
| CLI | `scan` | Ein | JSON-Ausgabe auf stdout oder Datei |
| CLI | `report` | Ein | Markdown/HTML in ein Ausgabeverzeichnis |
| CLI | `audit` | Ein | Findings-Liste, filterbar nach Schweregrad |
| CLI | `market` | Ein | Marktview + USP + Claims |
| Datei | `projects.yaml` | Ein | Manifest von `workspace-manifest` (nur gelesen) |
| Datei | `*.md`, `pubspec.yaml`, `Cargo.toml`, `package.json` | Ein | Intent-/Reife-Quellen |

Keine HTTP-Schnittstelle, keine Datenbank, kein Cache auf der Platte.

## 6. Entscheidungen (ADR-lite)

### ADR-001 — Deduplizierung über `git-common-dir` statt `git-dir`
**Kontext:** 122 der 329 Verzeichnisse sind Worktrees.
**Entscheidung:** `rev-parse --path-format=absolute --git-common-dir` als Dedup-Schlüssel.
**Folge:** Ein Repo = eine Historie = eine Zeile im Report. `worktree_paths` listet die
Verzeichnisse. Alternative (`--git-dir`) hätte jeden Worktree als eigenes Repo gezählt
und die Metriken um Faktor ~30 verfälscht.
**Status:** entschieden.

### ADR-002 — `ahead`/`behind` = `None` statt `0` bei fehlendem Remote
**Kontext:** 2 Repos haben kein `origin`; bei vielen ist `origin/main` lokal nicht bekannt.
**Entscheidung:** Unwissenheit als `None` modellieren.
**Folge:** Der Report kann „unbekannt" von „0" unterscheiden — sonst wäre ein Report
unnötig schmeichelhaft.
**Status:** entschieden.

### ADR-003 — Kein `fetch`/`ls-remote`
**Kontext:** Aktuelle `origin/*`-Stände könnten veraltet sein.
**Entscheidung:** Nur lokale Refs lesen; im Report wird `origin`-Stand als
„lokal bekannter Stand" ausgewiesen.
**Folge:** Kein Netzwerkzugriff, reproduzierbar, aber `ahead` bezieht sich auf den letzten
bekannten Push. Ein `fetch` ist bewusst **nicht** implementiert (Schreib-/Netzwerkaktion,
widerspräche REQ-007).
**Status:** entschieden.

### ADR-004 — Intent wird nicht erfunden
**Kontext:** Die verbreitetste Fehlerquelle von Workspace-Analyse-Werkzeugen ist
halluzinierte Projektbeschreibungen.
**Entscheidung:** Ohne Fund `text=None`; Konfidenz und Quelle werden immer mitgeführt.
**Folge:** Der Report kann Lücken zeigen — genau das macht die Lücke sichtbar
(Grundsatz aus dem Engineering Standard: Transparenz vor Kosmetik).
**Status:** entschieden.

### ADR-005 — Marktview ist intern
**Kontext:** REQ-014 verlangt Marktview; externe Wettbewerberdaten sind offline nicht
belastbar verfügbar.
**Entscheidung:** Der Marktview beschreibt die **interne** Portfolio-Landschaft und ist
mit `scope: internal` gekennzeichnet. USP-Kandidaten nennen stets die messbare
Beobachtung, aus der sie folgen.
**Folge:** Kein Weltmarkt-Claim, aber eine belastbare Sicht auf Stärken und Lücken des
Portfolios. Externe Daten sind als spätere Erweiterung vorgesehen (Import, nicht Scraping).
**Status:** entschieden.

### ADR-006 — Findings sind Daten, keine Aktionen
**Kontext:** Die AETHEL-Regel lautet: nichts wegschmeißen, immer archivieren.
**Entscheidung:** Findings enthalten einen `action`-Text, führen ihn aber nie aus. Es
existiert kein `rm`/`mv`/`git branch -d` im Code.
**Folge:** Das Werkzeug kann gefahrlos auf dem gesamten Workspace laufen.
**Status:** entschieden.

### ADR-007 — Python, keine Runtime-Dependencies
**Kontext:** Das Werkzeug ruft `git` auf und analysiert Text; es braucht keine
schwere Laufzeit.
**Entscheidung:** Python ≥ 3.11, nur stdlib. Tests mit `pytest`.
**Folge:** Überall lauffähig, keine Installationshürde (`PYTHONPATH=src`), keine
Lieferkettenabhängigkeiten — passend zum Sicherheitsprofil der AETHEL-Repos.
**Status:** entschieden.

## 7. Qualitätsattribute

| Attribut | Ziel | Umsetzung |
|----------|------|------------|
| Korrektheit | Metriken stimmen mit `git` überein | TC-001..TC-005 vergleichen gegen echte Mini-Repos |
| Robustheit | Ein defektes Repo stoppt den Scan nicht | `run_git` → `None`; kein `raise` im Scan-Pfad |
| Geschwindigkeit | < 90 s für 208 Repos | ThreadPoolExecutor, 5.000 Git-Aufrufe |
| Reproduzierbarkeit | gleiche Eingabe → gleiches Ergebnis | Sortierung, `generated_at` als einzige Variable |
| Sicherheit | read-only | TC-007 prüft Quelltext auf Schreiboperationen |
| Ehrlichkeit | keine erfundenen Fakten | ADR-004, `None` statt Rate, `scope: internal` |

## Ergänzung 23.10.2026: Inventar, Dossier, AIX-Kontext

`inventory` trennt Checkout-Pfade, gemeinsame Git-Identität, bekannte
Projektmarker und externe Worktree-Registrierungen. `dossier` verbindet den
Scan mit begrenzten, gehashten Dokumentquellen. `aix_input.attach` bindet ein
eindeutiges aktuelles Dossier ausschließlich an den Kontext eines vorhandenen
unfreigegebenen Engineering-Eingangs. Die Kernlogik berührt dabei keine
AIX-Auftragsakte, Rollen-Lease oder Merge-Referenz.

Ein Weg: aethelema/Bot → bestehender AIX-Engineering-Eingang mit Projektbelegen
→ bestehendes Arbeitspaket/Rollenprüfung → vorhandener Harness → Forge/Landing.
Dieses Repo liefert das Material, nicht eine zweite Zustandsmaschine.
