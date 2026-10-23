# TEST-CASES — aethelProjects

> Testfälle TC-NNN → decken REQ-NNN ab (Given/When/Then).
> Jeder TC hat genau einen automatisierten Test in `tests/`.
> Testlauf: `PYTHONPATH=src python3 -m pytest tests/ -v`

## Zuordnung REQ → TC

| REQ | Abdeckende Testfälle | Testdatei |
|-----|----------------------|-----------|
| REQ-001 Discovery + Worktree-Dedup | TC-001, TC-002 | `test_discovery.py` |
| REQ-002 Commits eindeutig zählen | TC-003, TC-004 | `test_metrics.py` |
| REQ-003 Branch-Klassifikation | TC-005, TC-006 | `test_metrics.py` |
| REQ-004 ahead/behind/dirty, None statt 0 | TC-007, TC-008 | `test_metrics.py` |
| REQ-005 JSON-Schema | TC-009, TC-010 | `test_report.py` |
| REQ-006 Markdown- und HTML-Report | TC-011, TC-012 | `test_report.py` |
| REQ-007 ausschließlich lesend | TC-013, TC-014 | `test_readonly.py` |
| REQ-008 CLI-Subcommands | TC-015, TC-016 | `test_cli.py` |
| REQ-009 Intent-Erkennung | TC-017, TC-018, TC-019 | `test_intent.py` |
| REQ-010 Reifegrad | TC-020, TC-021 | `test_maturity.py` |
| REQ-011 Manifest-Abgleich | TC-022, TC-023 | `test_manifest.py` |
| REQ-012 Aufräum-Vorschläge | TC-024, TC-025 | `test_findings.py` |
| REQ-013 Projektmanagement-View | TC-026 | `test_pmview.py` |
| REQ-014 Marktview/USP | TC-027, TC-028 | `test_market.py` |
| REQ-015 Marketing-Claims | TC-029 | `test_market.py` |
| REQ-016 Offline, ohne echten Workspace | TC-030 | `test_readonly.py` |

**Abdeckungsgrad:** 16 von 16 REQs abgedeckt, 30 Testfälle.
Ein Test prüft die Vollständigkeit der Zuordnung (TC-031 in `test_coverage.py`).

---

## Testfälle

### Discovery

| TC | REQ | Given | When | Then |
|----|-----|-------|------|------|
| TC-001 | REQ-001 | Ein Verzeichnis mit `.git` | `discover(root)` | Es wird genau eine `RepoIdentity` geliefert, `name` = Verzeichnisname |
| TC-002 | REQ-001 | Hauptverzeichnis + 2 Worktrees (gemeinsames `.git`) | `discover(root)` | Genau **eine** Identität; `worktree_paths` enthält beide Worktree-Pfade |

### Metriken

| TC | REQ | Given | When | Then |
|----|-----|-------|------|------|
| TC-003 | REQ-002 | main mit 3 Commits, Branch `feature` mit 1 extra Commit | `collect()` | `commits_on_main == 3`, `commits_not_on_main == 1` |
| TC-004 | REQ-002 | 3 Branches, alle mit demselben 1 Extra-Commit | `collect()` | `commits_not_on_main == 1` (nicht 3) — der Commit zählt **einmal** |
| TC-005 | REQ-003 | 1 gemergter, 1 ungemergter Branch | `collect()` | `branches_total == 2`, `branches_unmerged == 1` |
| TC-006 | REQ-003 | Ungemergter Branch mit 5 Commits | `collect()` | `unmerged_branches` enthält den Branch mit `commits_ahead == 5` |
| TC-007 | REQ-004 | Repo **ohne** `origin` | `collect()` | `ahead_of_origin is None` (nicht `0`) |
| TC-008 | REQ-004 | Geänderte Datei im Working Tree | `collect()` | `dirty_files >= 1` |

### Report

| TC | REQ | Given | When | Then |
|----|-----|-------|------|------|
| TC-009 | REQ-005 | Ein Scan-Ergebnis | `to_json()` | Enthält `schema`, `summary`, `repos`; `schema == "aethel.projects/v1"` |
| TC-010 | REQ-005 | Zwei gleichnamige Felder | `to_json()` | Jedes Repo-Objekt trägt alle Pflichtfelder (auch `None`-Werte) |
| TC-011 | REQ-006 | Ein Scan-Ergebnis | `render_markdown()` | Enthält Summary-Zahlen, Kategorietabelle und Repo-Tabelle |
| TC-012 | REQ-006 | Ein Scan-Ergebnis | `render_html()` | Gültiges HTML mit `<table>` und allen Repo-Namen |

### Read-only

| TC | REQ | Given | When | Then |
|----|-----|-------|------|------|
| TC-013 | REQ-007 | Der gesamte Quelltext von `src/` | Quelltext wird nach Schreiboperationen durchsucht | Kein `git checkout`, `commit`, `push`, `branch -d`, `worktree remove`, `reset`, `clean`, `rm `, `mv ` in Git-Kommando-Strings |
| TC-014 | REQ-007 | Der Quelltext | `subprocess`-Aufrufe werden gesucht | Jeder `git`-Aufruf nutzt ausschließlich lesende Subkommandos (Whitelist) |
| TC-030 | REQ-016 | Kein echter Workspace vorhanden | Gesamte Testsuite | Läuft grün, ohne `~/workspace` zu berühren; nur `tmp_path` wird benutzt |

### CLI

| TC | REQ | Given | When | Then |
|----|-----|-------|------|------|
| TC-015 | REQ-008 | Aufruf `--help` | `main(["--help"])` | Listet `scan`, `report`, `audit`, `market` |
| TC-016 | REQ-008 | Mini-Workspace | `main(["scan", "--root", tmp, "--json", out])` | Exit-Code 0, JSON-Datei existiert und ist parsebar |

### Intent

| TC | REQ | Given | When | Then |
|----|-----|-------|------|------|
| TC-017 | REQ-009 | Repo mit `docs/SPEC.md` mit Abschnitt „Zweck (ein Satz)" | `infer()` | `confidence == "high"`, `source == "docs/SPEC.md"`, Text = der Satz |
| TC-018 | REQ-009 | Repo nur mit `README.md` | `infer()` | `confidence == "medium"`, `source == "README.md"` |
| TC-019 | REQ-009 | Repo ohne jede Quelle | `infer()` | `text is None` — **kein erfundener Zweck** |

### Reifegrad

| TC | REQ | Given | When | Then |
|----|-----|-------|------|------|
| TC-020 | REQ-010 | Repo mit allen Pflichtartefakten inkl. Tests | `score()` | `score >= 80`, `grade == "Professional"` |
| TC-021 | REQ-010 | Repo nur mit README | `score()` | `score == 10`, `parts` listet „README": 10 und den Rest 0 |

### Manifest

| TC | REQ | Given | When | Then |
|----|-----|-------|------|------|
| TC-022 | REQ-011 | Manifest nennt ein Repo, das lokal fehlt | `compare()` | Finding „verwaist" mit Repo-Name |
| TC-023 | REQ-011 | Manifest-Datum älter als lokaler letzter Commit | `compare()` | Finding „last_commit veraltet" mit beiden Datumsangaben |

### Findings

| TC | REQ | Given | When | Then |
|----|-----|-------|------|------|
| TC-024 | REQ-012 | Repo mit 200 Commits nicht auf main | `detect()` | Finding `not-on-main` mit Schweregrad `critical` |
| TC-025 | REQ-012 | Repo ohne main/master | `detect()` | Finding `no-main`; **kein** Finding mit einer ausgeführten Aktion |

### Projektmanagement-View

| TC | REQ | Given | When | Then |
|----|-----|-------|------|------|
| TC-026 | REQ-013 | Letzter Commit vor 200 Tagen | `build()` | `activity == "inactive"`, `risk != "low"`, `next_actions` nicht leer |

### Marktview

| TC | REQ | Given | When | Then |
|----|-----|-------|------|------|
| TC-027 | REQ-014 | Scan mit 2 Kategorien | `build()` | `scope == "internal"`, Kategorien mit Abdeckungszahlen |
| TC-028 | REQ-014 | Einziges Repo einer Kategorie mit 600 Commits | `build()` | Es erscheint als USP-Kandidat „Alleinsteller" mit messbarer Begründung |

### Marketing

| TC | REQ | Given | When | Then |
|----|-----|-------|------|------|
| TC-029 | REQ-015 | Repo mit 800 Commits auf main | `claims()` | Claim nennt „800"; für ein leeres Repo wird **kein** Claim erzeugt |

### Abdeckung

| TC | REQ | Given | When | Then |
|----|-----|-------|------|------|
| TC-031 | alle | `docs/SPEC.md` + `docs/TEST-CASES.md` | Abgleich REQ-Liste ↔ TC-Liste | Jede REQ-NNN hat ≥1 TC; jeder TC verweist auf eine existierende REQ |

### Erfassung und Projektdossiers (23.10.2026)

| TC | REQ | Given | When | Then |
|----|-----|-------|------|------|
| TC-056 | REQ-017 | Tiefer versteckter Worktree, Bare-Repo, kaputter Git-Verweis und Nicht-Git-Paket | `tests/test_inventory.py` | Identitäten/Checkouts korrekt getrennt; ungültige Verweise, externe Registrierungen und Ausschlüsse explizit |
| TC-057 | REQ-018 | Architekturdokument, Cargo-Pfadabhängigkeit und externe Dokumentverknüpfung | `tests/test_dossier.py` | Quelle gehasht; fehlende Abhängigkeit sichtbar; fremdes Dokument nicht gelesen; Verhalten nicht als geprüft behauptet |

| TC-058 | REQ-019 | Eingangsvertrag und Projektbefund; Varianten mit Drift, fremdem Pfad oder Freigabe | `tests/test_aix_input.py` | Nur context wird ergänzt; keine Freigabe oder Wirkung; alle negativen Bindungsfälle blockieren |
