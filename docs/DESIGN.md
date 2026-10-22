# DESIGN — aethelProjects

> WIE im Detail? Datenmodelle, Schnittstellen, Schlüssel-Algorithmen.
> Jede REQ-NNN aus [SPEC.md](SPEC.md) hat hier eine Entsprechung.

## 1. Datenmodell

### 1.1 `RepoReport` — das Herzstück

```python
@dataclass(frozen=True)
class RepoReport:
    # Identität
    name: str                    # Verzeichnisname, z.B. "aethelScripts"
    path: str                    # absoluter Pfad des Hauptverzeichnisses
    git_common_dir: str          # Dedup-Schlüssel (REQ-001)
    is_worktree: bool            # war der Pfad selbst ein Worktree?
    worktree_paths: tuple[str, ...]   # alle Verzeichnisse, die diese Historie teilen

    # Git-Zustand (REQ-002..004)
    default_branch: str | None   # None = kein main/master vorhanden
    current_branch: str
    commits_total: int
    commits_on_main: int
    commits_not_on_main: int     # UNIQUE, über alle Branches (REQ-002)
    branches_total: int
    branches_unmerged: int
    unmerged_branches: tuple[UnmergedBranch, ...]   # (name, commits_ahead, kind)
    ahead_of_origin: int | None  # None = unbekannt (REQ-004)
    behind_origin: int | None
    dirty_files: int
    last_commit_date: str | None
    last_commit_subject: str | None
    remote_url: str | None

    # Ableitungen
    intent: Intent | None        # REQ-009
    maturity: Maturity | None    # REQ-010
    manifest_entry: ManifestEntry | None   # REQ-011
    findings: tuple[Finding, ...]   # REQ-012 (Aufräum-/Risikohinweise)

    # Bewertung
    pm_view: ProjectManagementView   # REQ-013
```

**Warum `frozen=True`:** Der Scan ist ein Snapshot. Jede Ableitung (Intent, Reife, PM-View)
erhält den unveränderten `RepoReport` und liefert einen neuen Wert zurück. So ist
nachvollziehbar, welcher Wert aus welchem Input entstanden ist.

### 1.2 Hilfstypen

```python
@dataclass(frozen=True)
class UnmergedBranch:
    name: str
    commits_ahead: int
    kind: str          # "local" | "remote-only"

@dataclass(frozen=True)
class Intent:
    text: str | None
    confidence: str    # "high" | "medium" | "low"
    source: str        # "docs/SPEC.md" | "README.md" | "manifest" | "none"
    evidence: str      # gekürzter Originalfund

@dataclass(frozen=True)
class Maturity:
    score: int                       # 0..100
    grade: str                       # "Professional" | "Solide" | "Prototyp" | "Skizze"
    parts: dict[str, int]            # Teilpunkte je Artefakt

@dataclass(frozen=True)
class Finding:
    code: str          # "stale" | "duplicate" | "shared-history" | "stub" | "orphan-worktree" | ...
    severity: str      # "info" | "warn" | "critical"
    message: str
    action: str        # konkrete, ausführbare Empfehlung (nie ausgeführt)

@dataclass(frozen=True)
class ProjectManagementView:
    activity: str      # "active" | "inactive"
    risk: str          # "low" | "medium" | "high"
    next_actions: tuple[str, ...]
```

### 1.3 JSON-Schema (REQ-005)

```jsonc
{
  "schema": "aethel.projects/v1",
  "generated_at": "2026-10-22T14:03:11+02:00",
  "workspace_root": "/Users/manuel/workspace",
  "summary": {
    "repos": 208, "worktree_dirs": 122, "commits_total": 37357,
    "commits_on_main": 25362, "commits_not_on_main": 11995,
    "branches": 3169, "dirty_repos": 192, "stale_repos": 168
  },
  "repos": [ /* RepoReport, camelCase-snake_case wie oben */ ],
  "findings": [ /* projektübergreifende Findings */ ],
  "categories": { /* name -> {repos, commits, not_on_main, branches} */ }
}
```

**Stabilitätszusage:** Die Feldnamen in `summary` und `repos[]` ändern sich nur mit
Bump des `schema`-Strings. Neue Felder dürfen ergänzt werden.

## 2. Schnittstellen

### 2.1 CLI (`bin/aethel-projects`)

```
aethel-projects scan    [--root DIR] [--json OUT|-] [--quiet]
aethel-projects report  [--root DIR] [--format md|html] [--out DIR] [--include-detail]
aethel-projects audit   [--root DIR] [--format md|json] [--severity warn|critical]
aethel-projects market  [--root DIR] [--format md|html]
aethel-projects --help
```

Gemeinsame Optionen: `--root` (Default `~/workspace`), `--timeout` (Default 30 s pro
Git-Aufruf), `--jobs` (Parallelfaktor für den Scan, Default = CPU/2).

**Exit-Codes:** `0` Erfolg · `1` Fehler (Root nicht lesbar, git fehlt) · `2` Aufruf-Fehler.
Ein Report mit Findings ist **kein** Fehler — der Report ist auch bei roten Findings gültig.

### 2.2 Python-API

```python
from aethel_projects import scan_workspace, render_markdown, render_html

result = scan_workspace("/Users/manuel/workspace")
print(result.summary.repos)                 # 208
print(render_markdown(result))
```

Die API ist die Quelle; die CLI ist eine dünne Hülle (`cli.py` ruft nur die API auf).

## 3. Schlüssel-Algorithmen

### 3.1 Discovery + Deduplizierung (REQ-001)

```
1. Alle Unterverzeichnisse mit .git (Datei oder Ordner) unterhalb root, max_depth 2.
2. Pro Verzeichnis: git rev-parse --path-format=absolute --git-common-dir
3. Dedup-Schlüssel = common_dir (ohne Suffix /.git)
4. Hauptverzeichnis des Repos = der Pfad, dessen common_dir == common_dir/.git
   (bei Worktree: der Elternpfad des common_dir)
5. Alle weiteren Verzeichnisse desselben Schlüssels = worktree_paths
```

**Warum `common_dir` und nicht `git rev-parse --git-dir`:** Bei einem Worktree zeigt
`--git-dir` auf `…/.git/worktrees/<name>`, was jeden Worktree als eigenes Repo
aussehen ließe. `common_dir` zeigt auf das **gemeinsame** `.git` und identifiziert
die Historie korrekt.

**Alternative geprüft und verworfen:** `git worktree list --porcelain` im Hauptverzeichnis
liefert dieselbe Information, ist aber nur aufrufbar, wenn das Hauptverzeichnis bereits
bekannt ist — chicken-and-egg bei der Discovery. `common_dir` löst das in einem Schritt.

### 3.2 Commit-Messung (REQ-002)

| Metrik | Kommando | Bedeutung |
|---|---|---|
| `commits_total` | `rev-list --count --all` | alle jemals referenzierten Commits |
| `commits_on_main` | `rev-list --count <default>` | Commits, die auf main sind |
| `commits_not_on_main` | `rev-list --count --all --not <default>` | **unique**, über alle Branches |
| `ahead_of_origin` | `rev-list --count origin/<default>..<default>` | lokal, nicht gepusht |
| `behind_origin` | `rev-list --count <default>..origin/<default>` | origin hat mehr |

**Die Falle, die der Code vermeidet:** `rev-list --count default..branch` pro Branch
summiert **dieselbe** Commits mehrfach (ein Commit auf 5 unmerged Branches zählt 5×).
Auf dem echten Workspace ergibt das 1.454.853 statt der korrekten 11.995 — Faktor 121.
`--all --not <default>` zählt jeden Commit genau einmal.

**`ahead`/`behind` = `None`, nicht 0**, wenn `origin/<default>` fehlt: fehlender Remote
ist Unwissenheit, kein Befund. (REQ-004)

### 3.3 Intent-Erkennung (REQ-009)

Regelbasiert, priorisiert:

| Priorität | Quelle | Konfidenz | Extraktion |
|---|---|---|---|
| 1 | `docs/SPEC.md` | hoch | Abschnitt „Zweck (ein Satz)" |
| 2 | `README.md` | mittel | erster nicht-leerer Prosaabsatz nach dem Titel |
| 3 | `pubspec.yaml`/`Cargo.toml`/`package.json` `description` | mittel | Feldwert |
| 4 | Manifest `projects.yaml` (Name/Kategorie) | niedrig | „<Name> — <Kategorie>" |
| — | keine | — | `Intent(text=None)` |

Satzbereinigung: Markdown-Auszeichnungen (`#`, `*`, `` ` ``, `>`) entfernen, Zeilen mit
„Badges", „License", „Installation" überspringen, auf 240 Zeichen kürzen.

**Vertrauen:** Ohne Treffer wird `text=None` geliefert. Der Report erfindet **keinen**
Zweck — das wäre die häufigste Fehlerquelle solcher Werkzeuge.

### 3.4 Reifegrad (REQ-010)

Scorecard-v2-Gewichte, **inhaltsbasiert** (Existenz allein zählt nicht):

| Artefakt | Punkte | Prüfung |
|---|---|---|
| README | 10 | Datei vorhanden |
| SPEC | 15 | `docs/SPEC.md` mit ≥1 `REQ-NNN (MUST|SHOULD|MAY)` ohne Platzhalter |
| DESIGN | 10 | ≥3 inhaltliche Zeilen ohne Platzhalter |
| ARCHITECTURE | 10 | ≥3 inhaltliche Zeilen ohne Platzhalter |
| TEST-CASES | 10 | ≥1 Zeile `| TC-NNN` ohne Platzhalter |
| tests | 20 | Testdatei mit echter Assertion, sonst 8 bei Vorhandensein |
| CI | 10 | `.github/workflows/` existiert |
| DNA | 10 | `dna/genome.yaml` mit `schema: aethel.dna/v1` + gefüllter `purpose:` |
| engineering.yaml | 5 | `.aethel/engineering.yaml` mit `schema: aethel.engineering/v1` |

Summe = 100 max. Grade: ≥80 Professional · ≥50 Solide · ≥20 Prototyp · sonst Skizze.

### 3.5 Aufräum-Erkennung (REQ-012)

| Code | Auslöser | Schweregrad | Vorschlag |
|---|---|---|---|
| `stale` | letzter Commit > 90 Tage | warn | „Archiv prüfen: `mv <repo> _archive/`" |
| `duplicate` | gleicher Zweckstext wie ein anderes Repo | warn | „Duplikat prüfen: `<other>`" |
| `shared-history` | common_dir == common_dir eines anderen Repos, eigener `.git` | warn | „Klon-Ziel: gemeinsame Historie mit `<owner>`" |
| `stub` | < 30 Quelldateien **und** 0 Tests **und** < 50 LOC | info | „Skelett: generieren oder archivieren" |
| `no-main` | kein main/master | warn | „Default-Branch fehlt" |
| `orphan-worktree` | Worktree-Verzeichnis ohne zugehörigen Branch | info | „Worktree entfernen: `git worktree remove <pfad>`" |
| `not-on-main` | > 50 Commits nicht auf main | critical | „<n> Commits nicht auf main — mergen oder archivieren" |
| `unpushed` | ahead > 0 | warn | „<n> Commits pushen" |

**Grundregel:** Findings sind **Daten**, keine Aktionen. Das Tool führt sie nie aus.
(REQ-007, REQ-012)

### 3.6 Marktview (REQ-014)

Der Marktview ist **intern** (`scope: internal`) — er beschreibt die Positionierung im
AETHEL-Portfolio, nicht den Weltmarkt. Grund: externe Marktdaten wären entweder
nicht verfügbar (offline) oder geraten — beides verstößt gegen REQ-009s Ehrlichkeitsprinzip.

Berechnet werden:
- **Kategorie-Abdeckung:** Repos je Kategorie, mit Commits und „nicht auf main"
- **Überbesetzte Kategorien:** > 5 Repos in einer Kategorie (Hinweis auf Generator-Wildwuchs)
- **Unterbesetzte:** 1–2 Repos (Hinweis auf fehlende Produktlinien)
- **Reife-Werte je Kategorie:** Median-Score → „wo trägt die Produktlinie?"
- **USP-Kandidaten:** Repos, die messbar herausragen:
  - höchste Commit-Zahl in ihrer Kategorie **und** Reife ≥ 50 → „Führungsrepo"
  - einziges Repo einer Kategorie mit ≥ 500 Commits → „Alleinsteller"
  - 0 Repos in der Kategorie mit ≥ 100 Commits → „Lücke"
- **Positionierung:** Rang des Repos innerhalb seiner Kategorie nach (Reife, Commits)

Jeder USP nennt die **messbare Beobachtung**, aus der er folgt — kein Marketing-Sprech
ohne Beleg.

### 3.7 Marketing-Claims (REQ-015)

Je Repository ein Einzeiler plus 1–3 Claims, ausschließlich aus Scan-Fakten:

| Bedingung | Claim |
|---|---|
| `commits_on_main >= 500` | „<n> Commits auf main — substanzieller Stand" |
| `maturity.score >= 80` | „Entspricht dem AETHEL Engineering Standard" |
| `not_on_main == 0 and branches <= 2` | „Vollständig auf main integriert" |
| `tests` vorhanden | „Testabdeckung vorhanden" |
| `dirty_files == 0` | „Sauberer Working Tree" |
| Kategorie-Einzigartigkeit | „Einzige <Kategorie> im Portfolio" |

**Kein Claim ohne Bedingung.** Fehlt die Evidenz, entfällt der Claim.

## 4. Fehlerbehandlung

| Fall | Verhalten |
|---|---|
| `git` nicht im PATH | Abbruch mit Exit 1 + klarer Meldung |
| Verzeichnis kein Git-Repo | wird übersprungen, nicht als Fehler gewertet |
| `git`-Aufruf läuft in Timeout | Feld wird `None`/`unknown`, Scan läuft weiter |
| Repo ohne main/master | `default_branch=None`; `commits_not_on_main` = alle Commits, `commits_on_main` = 0 |
| Manifest fehlt/kaputt | Manifest-Abgleich wird übersprungen, Scan läuft weiter |
| Kein README/SPEC | Intent `None`, Reifegrad niedrig, **kein** Absturz |

Robustheit: Der Scan darf **nie** an einem einzelnen defekten Repo scheitern. Defekte
Repos erscheinen im Report mit gesetzten `None`-Feldern, damit „unbekannt" sichtbar bleibt.

## 5. Nicht-funktionale Anforderungen

- **Laufzeit:** Scan des echten Workspace < 90 s (208 Repos, ~5.000 Git-Aufrufe, parallel).
- **Determinismus:** Gleicher Workspace → gleiches Ergebnis bis auf `generated_at` und
  Reihenfolge-sortierte Felder. `repos[]` ist nach `name` sortiert.
- **Keine Netzwerkzugriffe.** Ausnahme: `git` selbst ruft bei `fetch`/`ls-remote` auf —
  das Werkzeug tut das **nie**, es liest nur lokale Refs. `ahead`/`behind` beziehen sich
  auf den **lokal bekannten** `origin/*`-Stand und werden als solcher ausgewiesen.
- **Python ≥ 3.11**, keine Runtime-Dependencies (nur stdlib + `pytest` für Tests).
