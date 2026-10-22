# Software-DNA — aethelProjects

> Was ein Agent braucht, um dieses Projekt **neu zu erzeugen**.
> Maschinenlesbare Fassung: [`genome.yaml`](genome.yaml).

## Identität

- **Name:** aethelProjects
- **Zweck:** Portfolio-Analyse des AETHEL-Workspace — Git-Zustand, Intent, Reife,
  Marktview und Aufräum-Vorschläge in einem read-only Werkzeug.
- **Einzeiler:** Der ganze Workspace auf einen Blick — ohne Doppelzählung, ohne Erfindungen.

## Abstammung

- **Plattform:** `aethel-omega` (AETHEL-Ökosystem)
- **Teilt Codebasis mit:** `workspace-manifest` (Manifest-Format), `aethelScripts`
  (AIX-Laufzeitumgebung, Werkzeugstil)

## Stack

| Aspekt | Wert |
|--------|------|
| Sprache | Python ≥ 3.11 |
| Runtime-Dependencies | **keine** (nur stdlib) |
| Test | pytest |
| Build | keiner (reines Python) |
| Externes Werkzeug | `git` (nur lesende Subkommandos) |

## Bootstrap / Build / Test / Run

```bash
git clone https://github.com/AETHEL-Omega/aethelProjects.git
cd aethelProjects
PYTHONPATH=src python3 -m pytest tests/ -v          # Test
PYTHONPATH=src bin/aethel-projects scan --root ~/workspace   # Run
```

## Invarianten, die ein Klon erfüllen muss

1. **Worktree-Dedup:** N Verzeichnisse mit `.git` ⇒ ≤ N Repos im Report.
2. **Commit-Eindeutigkeit:** `commits_not_on_main` ≤ Summe aller Einzel-Branch-Zählungen.
3. **Read-only:** Kein `checkout`, `commit`, `push`, `reset`, `clean`, `rebase`, `merge`,
   `cherry-pick`, `rm`, `mv` in einem Git-Aufruf. Nur `gitio.py` ruft `subprocess`.
4. **Unwissenheit ≠ Befund:** Fehlender Remote ⇒ `ahead_of_origin is None`.
5. **Keine Erfindungen:** Ohne Quelle bleibt `intent.text is None`.
6. **Offline:** Die Testsuite läuft ohne Netzwerk und ohne `~/workspace`.
7. **Vollständigkeit:** Jede REQ-NNN in `docs/SPEC.md` hat ≥1 TC-NNN.

## Regenerations-Vertrag

Ein frisch erzeugtes Projekt gilt als korrekt, wenn **alle Tests grün** sind und alle
Invarianten halten — nicht, wenn die Bytes gleich sind. Das ist der FVR-Grundsatz des
AETHEL-Standards: die Testsuite ist das Akzeptanz-Orakel.

## Nicht-deterministische Quellen

| Quelle | Umgang |
|--------|--------|
| `generated_at` (Zeitstempel) | einziger variabler Wert im Report |
| Reihenfolge der Findings bei gleichem Gewicht | deterministisch sortiert nach Repo-Name, dann Code |
| `ahead`/`behind` | beziehen sich auf den **lokal bekannten** `origin/*`-Stand, kein `fetch` |
| Dateisystem-Zeitstempel | werden nicht ausgegeben |

## Akzeptanz

> Alle `tests/` grün **und** alle REQ-NNN abgedeckt.
