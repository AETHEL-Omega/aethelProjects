# Protokoll dieses Chats: Arbeitsweise, Recherche, Verluste

Stand 03.11.2026, abends. Manuel: „Ich brauche einen kompletten Bericht zu diesem Chat, deiner Arbeitsweise, was du recherchiert hast, was verloren gegangen ist.“ Dieser Bericht ist Teil der Analysen-Ablage, damit der Chat selbst nicht das Gedächtnis ist.

## 1. Verlauf in Phasen

| Phase | Auftrag (Manuel) | Ergebnis | Ort |
|---|---|---|---|
| 1 | Große Analyse des Workspace: Projekte, Register, Lücken, aethelProjects↔CodeAnalyzer, Stand der Technik, Fabrik, Firma, Kybernetik, fehlende Projekte, Gesamtstack | Hauptbericht, 380 Zeilen | `WORKSPACE-ANALYSE-2026-11-03.md` |
| 2 | Tiefer: richtige Technologie und Architektur auf macOS 27; alle Features von Cursor, LangGraph u. a.; Teamcenter, Mendix, Xcelerator; Kiraa; Forschung nach Trainingsstand; Kybernetik vollständig | Ergänzungsbericht, 444 Zeilen | `…-ERGAENZUNG-TECHNOLOGIE-ARCHITEKTUR.md` |
| 3 | Gesamtstack: was fehlt, wo nicht Best Practice; strategisch denken: Bauteile, die Bauteile bauen | Gesamtstack-Bericht, 222 Zeilen | `…-GESAMTSTACK-BAUTEILE.md` |
| 4 | aethelProjects erweitern, Analysen speichern und aufrufbar machen, günstige Subagenten, commit/push/merge; neue Projekte, Kreisläufe, aethelConsultant, aethelCompany, Inkubator, Apple-first, Rat-Matrix, Dominosteine, Werkzeuge, die Werkzeuge bauen, Chat-Protokoll | Code (sechs Module, CLI, Tests) und fünf weitere Analysen | dieses Repo, Branch `feat/analysen-register-schichten-1103` |

## 2. Arbeitsweise

- **Lesen vor Schreiben.** Jede Analyse begann mit Messungen auf diesem Mac (Versionen, Ports, PIDs, Dateizählungen, `git log`) und mit den vorhandenen Akten (`.aix-worker/*-30-10.md`, Kanon in CLAUDE.md, RFC 0001/0002). Zahlen im Bericht sind gemessen oder als Sekundärquelle markiert.
- **Günstige Subagenten für Breite, eigene Instanz für Urteil.** Vier Sonnet-Erkundungen (Workspace-Inventar, Agent-Infrastruktur, untere Stack-Schichten, Fabrik-Komponenten), fünf Sonnet-Bauschnitte (analyses, registers, stack, incubator, applefirst), eine Opus-Prüfinstanz für den Diff. Urteil, Architektur, Kybernetik, Rat-Matrix und alle Berichtstexte von der Hauptinstanz. Das folgt Manuels Regel vom 28.10. (Mechanik günstig, Urteil getrennt).
- **Außenrecherche mit Suchwerkzeugen**, mit dem Trainingsstand als Basis und gezielter Suche nach allem seit Mitte 2026. Jede Zahl aus Sekundärquellen ist als „sek.“ markiert; unbestätigte Angaben (DORA-Zahl, Kiraas „80×“, Intelligence Center X, CRA-Steward-Datum, SkillCraft-Prozentwerte) sind benannt.
- **Spezifikation vor Code.** REQ-020 bis REQ-023 und TC-059 bis TC-064 vor der Verdrahtung; jedes Modul mit Tests vom Autor; CLI, Doku und Inhalte von der Hauptinstanz; Review vor Merge.
- **Ein Schreiber je Datei.** Subagenten durften nur ihr Modul und ihre Testdatei anfassen; cli.py, README und docs blieben bei der Hauptinstanz. So gab es keine Konflikte.
- **Nichts gelöscht, nichts installiert, keine Lizenz bestätigt, kein GitHub-Repo angelegt.** Der Workspace wurde nur gelesen; geschrieben wurde in `_docs/` (Kopien) und in aethelProjects.

## 3. Was recherchiert wurde

| Thema | Quellen (Auswahl) | Ergebnis im Bericht |
|---|---|---|
| Plattform macOS 27, Xcode 27, Foundation Models, Core AI, Containerization | Apple WWDC26-Guide, Session-Seiten, Xcode-27-Artikel, FM-Artikel, apple/container 1.4 | Ergänzung Abschnitt 1–2 |
| Werkzeuge: Cursor (Changelog bis 20.10.2026), Claude Code, Codex, LangGraph/Deep Agents (19 Middleware), Kiro (Specs, Wellen), Antigravity/Jules, OpenHands, Devin | Changelogs, Docs, Blogs | Ergänzung Abschnitt 4 (32 Fähigkeiten) |
| Protokolle: MCP 2026-07-28, ACP, A2A 1.0, Agent Skills, WASI 0.3 | Spezifikationsseiten, Zed, wasi.dev | Ergänzung 5.6, Gesamtstack 2 |
| Forschung 2026: Harness-Engineering (11 Systeme), Verification Horizon, EvilGenie, MemCoder, SWE-bench Pro/Cycle/Touch, Meta-Harness-Familie, EvoSkills/SkillSmith/CodeSkill, SkillCraft/SkillsBench, Darwin-Gödel-Maschine (ICLR 2026), Code-Modus | arXiv, Vals.ai, Blogs | Ergänzung 5, Werkzeuge-Bericht 2 |
| Siemens Teamcenter 2606, Xcelerator, Mendix 11.12, Industrial Copilots, Kiraa | Siemens-Blog, Mendix-Seiten, kiraa.ai, Pressemeldungen | Ergänzung 6, Neue Projekte 4 |
| Referenzstacks: Oxide Hubris, seL4, Asterinas 0.18, Redox, Fuchsia, RISC-V RVA23, Embedded Swift, Rust für Linux, CHERIoT | Projektseiten, Phoronix, Swift.org | Gesamtstack 2 |
| Regulatorik und Lieferkette: CRA (Meldepflicht seit 11.09.2026), SLSA 1.1, Bootstrapping (Guix, live-bootstrap) | Kanzleien, slsa.dev, Projektseiten | Gesamtstack 2, Werkzeuge 1 |
| Plattform-Engineering 2.0, DORA 2026 (sek.) | CNCF, Analysten | Ergänzung 5.5 |

## 4. Was verloren gegangen ist oder nicht gesichert war

1. **Kontextverdichtung.** Der Chat wurde einmal zusammengefasst, bevor der erste Abschlusstext geschrieben war. Die Zusammenfassung enthielt die Fakten; der Wortlaut früher Zwischenergebnisse (Rohausgaben von Befehlen, Zwischenlisten) ist nur noch im Transkript (`~/.claude/projects/-Users-manuel-workspace/505ee935-….jsonl`), nicht in den Berichten. Alle Zahlen in den Berichten stammen aus den gespeicherten Dateien, nicht aus der Erinnerung.
2. **Ein Subagent brach ab.** Die Erkundung der unteren Stack-Schichten endete mit einem API-Fehler (Netz). Die Zählung wurde von der Hauptinstanz selbst wiederholt; nichts fehlt, aber der Subagent-Lauf ist verloren.
3. **Antworten, die nur im Chat standen.** Mehrere Fragen (Welche Projekte wurden auf GitHub angelegt? Wie wird die Arbeit dieses Chats zu Software?) wurden zuerst nur im Chat beantwortet. Sie stehen jetzt in `NEUE-PROJEKTE-KREISLAEUFE-RAT.md` Abschnitt 0 und `ZIELBETRIEBSMODELL-UND-DOMINOSTEINE.md` Abschnitt 0. Antwort auf die GitHub-Frage: nichts wurde angelegt.
4. **Nicht erledigt:** keine GitHub-Repos für aethelCompany, aethelConsultant, aethelIncubator (brauchen Freigabe und Registry); `aix-merge-gated` nicht benutzt (Laufzeit laut `aix_doctor` 114 Commits veraltet, Parität rot); `.aix/` in aethelProjects bleibt unversioniert; die ruff-Befunde (21) sind Altbestand und unberührt; die Basis-Branches `codex/…` und `feat/projekte-belege-stubs-1030` landen mit diesem Merge, waren aber von einer anderen Instanz nicht separat geprüft.
5. **Unverifiziert geblieben:** die Apple-Laufzeit-Prüfung durch den Subagenten (XPC, SMAppService) fand nicht statt; die Hauptinstanz hat sie durch Stichproben ersetzt. Zeilenzahlen sind grob. Ports und PIDs sind Momentaufnahmen.
6. **Review-Befunde, die bewusst offen bleiben:** TC-IDs in den Docstrings der drei Modultests, `show()` liefert `verified` nicht als Rückgabewert, kein AST-Wächter für Schreibzugriffe, stack-Regeln für `aix`/`omega` als Markenpräfix (an den Autor gegeben, Stand siehe STATUS).

## 5. Wie dieser Chat künftig überflüssig wird

Alles, was hier von Hand geschah, hat jetzt einen Ort: Messung in aethelProjects (`registers`, `stack`, `incubator`, `applefirst`, `analyses`), Rat und Entscheidungen in `analysen/` bis aethelConsultant und aethelCompany existieren, Kreisläufe in `kreislaeufe.json` bis die Loop-Registry in aixd steht. Der nächste Radar-Lauf beginnt mit `aethel-projects analyses --list` statt mit einem leeren Chat.
