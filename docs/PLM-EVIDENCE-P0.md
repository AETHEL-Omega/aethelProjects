# PLM Evidence P0 — vorgeschlagener, lesender Vertrag

Eigenständiger Rust-Fachkern und CLI; kein bestehender AETHEL-Standard und keine
Produkt-, Rollen-, Prüf- oder Freigabeautorität. Er liest ausschließlich das
angegebene JSON. `source`, `source_id`, Herkunft und alle anderen Eingabetexte
sind passive Angaben: keine Auflösung von Pfaden oder URLs, keine Befehle, keine
Adapter, kein Netzwerk. Keine Datenbank, kein Server, keine Registry.

## Austausch

Eingabe `aethel.plm.case/v1`, Ausgabe `aethel.plm.assessment/v1`. Ein vollständiges
Beispiel steht in `components/plm-evidence/fixtures/y1-historical.json`. `change`
enthält Fall-ID, optional eine bestehende Produktreferenz (sonst `null`), Problem,
Ziel, optional den Kandidatenstand und Kontext. Claims benennen die nötige Art
und referenzieren Evidence-IDs. Evidence enthält Quelle, Quellen-ID, optionale
Revision/Digest, Art, optionalen Kandidaten, Herkunft und berichtetes Ergebnis
(`pass`, `fail`, `unknown`, `not_applicable`). `not_applicable` verlangt eine
nichtleere Erklärung für die jeweilige Referenz, keine Befreiung der Aussage.
Eine solche Referenz zählt nicht als anwendbarer Nachweis. `verified` ist optional und wird nur als behauptetes
Eingabefeld durchgereicht; es verleiht keine Beweiskraft.

Alle IDs müssen innerhalb ihres Objekttyps eindeutig sein, Referenzen je Claim
eindeutig und auf vorhandene Evidence zeigen. Unbekannte Felder und Versionen,
leere Pflichtangaben und leere optionale Zeichenketten sind Strukturfehler.
Claims, Referenzen und Lücken sind stabil sortiert. Belegart (`kind_match`) und Kandidatenbindung (`candidate_binding`) werden
unabhängig bewertet, auch wenn beide unpassend sind. Fehlende Referenzen
(`missing_evidence`), nicht anwendbare Referenzen und ausschließlich
unpassende Referenzen (`missing_applicable_evidence`) bleiben unterscheidbar.
Ein berichteter Fehlschlag bzw. unbekanntes Ergebnis eines passenden Belegs
erzeugt `reported_failure` bzw. `reported_unknown`. Gegenläufige
Ergebnisse gleichartiger, auf den Kandidaten gebundener Belege werden angezeigt.
Ein passender Beleg bleibt eine Quellenbehauptung; ein Digest bindet keine
Wahrheit, `not_applicable` ist keine Freigabe. P0 prüft keine Quellen und kann
keine externe Verifikation bestätigen. Deshalb bleibt für jede Aussage die
Lücke `independent_verification_missing` bestehen. Die Ausgabe enthält keine
Gesamtfreigabe, keinen Fertigwert und kein Produktgate.

## Verwendung

```sh
cargo run --manifest-path components/plm-evidence/Cargo.toml -- assess \
  --input components/plm-evidence/fixtures/y1-historical.json --format text
cargo run --manifest-path components/plm-evidence/Cargo.toml -- assess \
  --input components/plm-evidence/fixtures/y1-historical.json --format json
```

Ergebnisse gehen auf stdout, Diagnosen auf stderr. Exitcode 0 bedeutet gültige
Auswertung, auch mit Lücken; 2 bedeutet ungültige Eingabe oder Bedienfehler;
3 bedeutet Ein-/Ausgabe-I/O-Fehler. Ein gültiges Ergebnis ist kein grünes Gate.

## Historischer Pilot und Übergabe

Y-1 ist eine Momentaufnahme vom 04.11.2026, kein aktueller Live-Stand. Der
Kettentest betrifft berechnete User-Agent-Werte; ein tatsächlicher Login ist
nicht belegt. Die 269 Tests sind im Changelog berichtet, kein unabhängiger
Gatebeleg. Review, Gate, Installation und Login bleiben offen. Produkt-ID ist
unbekannt. Ein späterer Adapter muss Quellen und Autorität eigenständig prüfen;
der Vorschlag hier ersetzt keinen bestehenden Prüfvertrag.

Auftrag: isolierter P0-Schnitt; Basis des Arbeitsbranches ist lokal gespeichertes
`origin/main` `8e714c0`. Ausführung: Codex/Terra laut Nutzerangabe; tatsächlicher
Host/Inference-Ort und Verbrauch durch diesen Baustein nicht belegt. Besitzakte
für den Schnitt wurde bei der Vorprüfung nicht gefunden; keine fremden
Worktrees geändert. Autorenprüfungen sind keine unabhängige Reviewfreigabe.
Nächster Schritt: getrenntes Review, danach zuständiges Gate auf dem finalen
Kopf und gegebenenfalls Landung ausschließlich über `aix-merge-gated`.

Reviewfragen für Opus: Sind die Dimensionen und die Behandlung von einzelnen
Fehlschlägen, widersprüchlichen Ergebnissen und Nichtanwendbarkeit fachlich
korrekt? Ist der Vertrag für spätere Adapter hinreichend eindeutig, ohne eine
Prüfautorität vorzutäuschen?

## Präzisierung des noch unveröffentlichten v1-Vorschlags

- `snapshot` ist optional. Ohne Angabe gilt `{"kind":"unspecified"}`:
  keine bekannte Quellenzeit, keine Aktualitätsaussage. Für die Pilotfixture
  gilt `{"kind":"historical","captured_on":"2026-11-04"}`. Das Datum wird
  kalendarisch geprüft, bleibt aber eine Quellenbehauptung. Es gibt bewusst
  keinen `live`-Status; der Evaluator liest keine aktuellen Quellen und keine Uhr.
- Jeder Fall muss mindestens eine Aussage enthalten. Leere Fälle sind
  Strukturfehler und werden nicht als erfolgreiche Auswertung ausgegeben.
- Lücken besitzen `evidence_ids`: konkrete Ursachen referenzieren die betroffenen
  Belege; Widersprüche nennen alle vergleichbaren Pass-/Fail-Referenzen.
  Allgemeine Lücken haben eine leere Liste. Kein UI muss IDs aus Text parsen.
- `unreferenced_evidence` bewahrt alle keiner Aussage zugeordneten Belege,
  sortiert nach ID. Sie begründen keine Aussage und werden im Text ausgewiesen.
- Vergleichbar bedeutet hier ausschließlich gleiche **deklarierte** Belegart
  und gleicher **deklarierter** Kandidatenstand. Identische Strings verifizieren
  weder Semantik noch Quelle. Herkunft, Digest und `verified` sind keine Autorität.
  Freie Belegartnamen sind ein offener Vorschlagsvertrag, keine zentrale Registry.
- Die CLI akzeptiert reguläre JSON-Dateien bis 8 MiB; Übergröße ist Exitcode 2.
  Ein-/Ausgabefehler einschließlich Broken Pipe sind Exitcode 3. Referenzfelder
  werden weiterhin nicht aufgelöst. Die Bibliothek selbst macht kein I/O;
  direkte Bibliotheksnutzer verantworten die Eingabegrößenbegrenzung.
- Die Textprojektion maskiert Steuerzeichen und gerichtete Unicode-Steuerzeichen
  aus Quelldaten. JSON erhält die ursprünglichen Daten; ein späteres UI muss
  diese seinerseits als untrusted Text rendern.

Die Erweiterung erfolgte im bestehenden Chat mit gpt-6-astra (Modellangabe der
Sitzung), ohne zusätzliche Modellaufträge. Das ist keine unabhängige Prüfung.
Autorenprüfungen: 16 Integrationstests, darunter eine 24-Fälle-Matrix,
Formatprüfung und Clippy mit `-D warnings`. Kein Gate oder Merge durchgeführt.
Review bleibt bei Opus: vorgeschlagene Wire-Semantik, Quellen-/Kandidatenbindung,
Nichtanwendbarkeit, vollständige Referenzprojektion und CLI-Fehlervertrag prüfen.
Der neue Kopf ersetzt den früheren Reviewkandidaten; Urteil und Gate müssen an
den finalen Stand gebunden werden.

## Issue–Action–Wirksamkeitsvertrag (Erweiterung vom 04.11.2026)

Implementiert in `components/plm-evidence/src/quality.rs`, ausschließlich lesend.
Neuer Vorschlag: `aethel.plm.quality-case/v1` →
`aethel.plm.quality-assessment/v1`. Kein Teamcenter-kompatibles Austauschformat,
keine S1000D-Konformität, kein Workflow-Executor und kein neues Rollenregister.

```sh
cargo run --offline --manifest-path components/plm-evidence/Cargo.toml -- \
  assess-quality --input components/plm-evidence/fixtures/quality-synthetic.json \
  --format json
```

`--format text` ist ebenfalls verfügbar. Dieselben Exitcodes und I/O-Grenzen
wie bei `assess`: 0 = strukturell gültig, auch mit Übergangssperren;
2 = Struktur-/Bedienfehler; 3 = I/O-Fehler. Das synthetische Beispiel liefert
`effectiveness_missing`: Umsetzung allein trägt keinen Maßnahmenabschluss.

### Objekte und Bindungen

- `issues`: ID, Zustandsrevision, Problem, beobachtete Konfiguration, Schweregrad,
  Triagebegründung und optional eine externe Abschlussentscheidungsreferenz.
- `actions`: ID, Zustandsrevision, **Planrevision**, Art (`containment`,
  `corrective`, `preventive`), Ziel, Verantwortungsreferenz, Termin, optionale
  Ursachenreferenz, Geltungsbereiche, Umsetzungsbelege und Dispositionsangaben.
- Jeder Geltungsbereich bindet Issue, Zielkandidat, Umgebung, Prüfkriterium und
  vereinbartes Beobachtungsfenster/Prüfprotokoll. Die beobachtete Fehlerkonfiguration
  darf vom Zielkandidaten abweichen. Mehrere Issues/Konfigurationen sind möglich.
- `checks` sind eigene Wirksamkeitsberichte: Maßnahme, Planrevision, konkreter
  Geltungsbereich, Prüferreferenz und Belegreferenzen. Alle passenden aktuellen
  Berichte werden ausgewertet; ein neuer Pass verdeckt keinen aktuellen Fail.
- `evidence` nutzt den bestehenden Referenzvertrag. Die benötigten Belegarten
  sind hier `implementation` und `effectiveness`. Ergebnisse bleiben berichtet;
  `verified`, Digest, Quellenname oder verschiedene Prüfer-Strings erzeugen
  keine nachgewiesene Prüferautorität.
- `transitions` enthalten Antrags-ID, Objektart/ID, erwartete Zustandsrevision,
  Zielzustand, Begründung und ggf. externe Entscheidungsreferenz. Jeder Antrag
  wird unabhängig gegen denselben Snapshot geprüft: keine simulierte Ausführung,
  kein automatischer Maßnahmen- oder Issue-Abschluss durch einen anderen Antrag.

Zustandsrevision und Planrevision sind bewusst getrennt. Eine zuständige
schreibende Instanz muss bei einer fachlichen Planänderung (insbesondere Scope,
Kriterium, Verantwortlicher oder Ziel) die Planrevision erhöhen; bei einem
Zustandswechsel die Zustandsrevision. Der reine Snapshot-Prüfer kann nicht
beweisen, dass diese Disziplin in der Quelle eingehalten wurde. Ein späterer
Adapter muss Historie und Berechtigungen validieren und konkurrierende Writes
an der erwarteten Revision abweisen. P0 schreibt keinen solchen Zustand.

### Übergangsregeln

Maßnahmen-Hauptweg:
`proposed → assigned → in_progress → implemented → awaiting_effectiveness → closed`.

Weitere explizite Kanten:

| Ausgang | Zusätzliche Ziele |
|---|---|
| proposed | cancelled, not_required |
| assigned | cancelled, superseded, not_required |
| in_progress | cancelled, superseded |
| implemented | in_progress, superseded |
| awaiting_effectiveness | in_progress, superseded |
| closed | in_progress (Wiedereröffnung) |

`cancelled`, `superseded`, `not_required` haben keine ausgehenden Kanten.
Selbstübergänge und das Überspringen von Stufen sind ungültig. Ab Beauftragung
sind Verantwortlicher und Termin erforderlich; Korrekturmaßnahmen brauchen eine
Ursachenreferenz. Ab `implemented` müssen für jeden Zielkandidaten passende
berichtete Umsetzungsbelege vorliegen. Terminüberschreitung wird hier nicht
berechnet: kein versteckter Uhrzugriff und kein Scheduler.

`closed` braucht zusätzlich für jeden Geltungsbereich einen aktuellen,
passenden Wirksamkeitsbericht mit berichteten Pass-Belegen, getrenntem
Prüfer-Identifier und einer Entscheidungsreferenz im Übergangsantrag.
Eigenprüfung, wiederverwendete Umsetzungsreferenzen, falsche Art/Stand,
Fail/Unknown/NotApplicable und widersprüchliche Berichte blockieren die
Voraussetzungen. Ein anderer Prüfer-Identifier ist nur eine notwendige
Konsistenzbedingung; Identität, Unabhängigkeit und Befugnis bleiben ungeprüft.

Dispositionszustände verlangen Begründung und externe Entscheidungsreferenz.
`superseded` verlangt einen vorhandenen, zyklusfrei erreichbaren Nachfolger.
Er muss die bisherigen Issue-/Umgebungs-/Kriteriums-/Beobachtungsbereiche decken;
der Zielkandidat darf sich ändern. Ein Nachfolger braucht eigene passende
Wirksamkeitsberichte. `cancelled` und `not_required` gelten nicht als erfolgreiche
Problemlösung. Administrative Abschlüsse/Risikoakzeptanz sind in diesem ersten
Vertrag nicht implementiert; solche Maßnahmen halten den Issue-Abschluss offen.

Issue-Hauptweg:
`registered → triaged → investigating → monitoring → closed`.
`monitoring` und `closed` können nach `investigating` zurückkehren. Ab Triage
sind Konfiguration, Schweregrad und Begründung nötig. Monitoring verlangt
umgesetzte Maßnahmen; Abschluss verlangt abgeschlossene Maßnahmen einschließlich
ihrer erneut geprüften Belegvoraussetzungen und externe Entscheidungsreferenzen.
Ersetzte Maßnahmen werden über die explizite Nachfolgerkette geprüft.
Wiedereröffnung benötigt eine Entscheidungsreferenz; ein widersprüchlicher alter
Abschluss bleibt im Snapshot sichtbar, verhindert aber nicht den Rückweg.
Rückgabe von `awaiting_effectiveness` nach `in_progress` benötigt ebenfalls eine
Entscheidungsreferenz. Die bisherige Historie muss die zuständige Akte bewahren.

### Ausgabe, Grenzen und Reviewübergabe

Die Ausgabe bewahrt den vollständig sortierten Quellsnapshot, separate
`snapshot_findings` und Befunde pro Antrag mit `code`, `object_id` und
`reference_ids`. Veraltete oder außerhalb des Plans liegende Checks bleiben
sichtbar. Strukturfehler (u. a. unbekannte Version/Felder, IDs, Referenzen,
zyklische Nachfolger und kaputte Daten) werden abgelehnt. Eine leere Befundliste
bedeutet ausschließlich vollständige **deklarierte** Voraussetzungen.
`authority` bleibt immer `external_authority_not_verified; requirements_only;
no_transition_applied`. Keine Boolesche Freigabe und kein Green-Gate-Ersatz.

Ausführung im bestehenden Chat mit gpt-6-astra, ohne Unteragenten; Kosten/Token
nicht gemessen. Orakel: Zustandsmatrizen, Scope-/Revisionsbindung, unvollständige
und widersprüchliche Belege, Eigenprüfung, Wiedereröffnung, Nachfolger und
CLI-Exitcodes. Abbruchgrenze bleibt dieser isolierte Vertrag ohne fremde
Architekturänderungen oder schreibende Integration. Keine neue Autorität.

Für Opus: besonders die Trennung von Snapshot-Konsistenz und externer Autorität,
Planrevision versus Zustandsrevision, Mehrfach-Scope, Nachfolgerketten und den
konservativen Umgang mit administrativen Abschlüssen prüfen. Root-Cause-Urteil,
Rollenprüfung, Signatur-/Receiptprüfung, echte Workflow-Historie, Fristeskalation
und CSDB-Anbindung bleiben bei späteren bestehenden Integrationswegen.

Autorenprüfung dieses Vertragsschnitts: 31 Integrationstests bestanden
(16 vorhandene + 15 Qualitätsvertragstests, einschließlich 81 Maßnahmen- und
25 Issue-Zustandspaaren), `cargo fmt --check`, `cargo clippy --offline
--all-targets -- -D warnings` und `git diff --check` bestanden. Die synthetische
CLI-Auswertung in Text und JSON meldet fehlende Wirksamkeit bei Exitcode 0.
Keine unabhängige Prüfung, kein Gate und kein Merge durchgeführt.

## Verbindung Änderung ↔ Issue ↔ Maßnahme ↔ Aussage

Die versionierten Vorschläge `aethel.plm.linked-case/v1` und
`aethel.plm.linked-assessment/v1` verbinden je einen vollständigen
`aethel.plm.case/v1` und `aethel.plm.quality-case/v1` über explizite Links.
Jeder Link nennt Issue-ID, Action-ID, Claim-ID und Quellenangabe. Der
Qualitätsfall und der Änderungsfall behalten ihre getrennten Identitätsräume;
ein Link darf nur eine Maßnahme verwenden, deren Scope das Issue nennt.
Doppelte Links, kaputte Referenzen, falsche Versionen und leere Angaben sind
Strukturfehler. Unterschiedliche oder unbekannte Kandidatenbindung und fehlende
Zuordnungen werden als eigene Lücken ausgewiesen. Die Eingaben und Ergebnisse
beider Prüfungen bleiben erhalten. Ein Link ist eine Quellenbehauptung, kein
Beweis, dass die Maßnahme die Aussage erfüllt, und keine Freigabe.

```sh
cargo run --offline --manifest-path components/plm-evidence/Cargo.toml -- \
  assess-linked --input components/plm-evidence/fixtures/linked-synthetic.json \
  --format json
```

Das Beispiel ist synthetisch und enthält bewusst keine Wirksamkeitsprüfung.
`assess-linked` prüft beide bestehenden Verträge mit denselben Funktionen wie
die Einzelkommandos, sortiert unabhängig von der Eingabereihenfolge und öffnet
keine Quellenreferenzen. `text` zeigt auch die jeweiligen ursprünglichen Lücken.
Der äußere Vertrag ergänzt weder Produktidentitäten noch Auftragsrechte.

Übergabe dieses Schnitts: Codex `gpt-6.1-terra` (Sitzungsmodell),
kein weiterer Modellauftrag; Token/Kosten nicht gemessen. Opus-Review für den
neuen Gesamtkopf steht aus. Für Flutter ist die bestehende `flutter_rust_bridge`
2.13.0 in aethelema vorhanden, aber ein P1-Schnitt betrifft ein anderes Repo
mit eigenem Owner, vorhandenen Änderungen und mehreren Worktrees. P2 benötigt
separat validierte Source-/Rechte-/Aktualitätsverträge. Beide sind nicht als
implementiert oder freigegeben aus dem vorliegenden P0-Kern abzuleiten.

## Anschlussabgleich: Projects, AIX Copilot und AgentRuntime

Lesebefund vom 04.11.2026, kein Live-Integrationsnachweis:

- **aethelProjects:** `docs/PM-INPUT.md` und `src/aethel_projects/aix_input.py`
  beschreiben den bestehenden `aethel.projects.pm-input/v1`-Export und einen
  separaten Consumer für rohe `aix.engineering_input.v1`. Der vorhandene
  AIX-Input-Adapter bindet u. a. Dossier, Quelle und Digest vor der Compilation;
  dies ist kein PLM-Import und prüft nicht die Produktwirkung. Ein künftiger
  PLM-Leseadapter muss Quellenzeit, betrachteten HEAD, unterschiedliche
  Export-/Scanzeit und lokale Repository-Identität erhalten. Nie aus `path`
  oder `repository_id` eine globale Produkt-ID ableiten. Private Dossiers nicht
  in Fixtures/Logs übernehmen.
- **AIX Copilot:** `docs/AIX-COPILOT-GOAL.md` beschreibt einen getrennten
  Rohprompt-, Proposal-/Digest-, Freigabe- und Auftragsweg sowie Goal-Artefakte
  und Receipts. Ein zukünftiger Adapter muss diese Zustände und ihren jeweiligen
  konkreten Digest/Kandidaten unterscheiden. Eine bloße Proposal-, Rollen- oder
  `reviewer.json`-Referenz ist keine nachgewiesene Befugnis, Prüfung oder
  Landung. AIX bleibt für Auftrag, Modus, Besitz und Rechte zuständig.
- **aethelAgentRuntime:** `docs/agent-proposal-surface.md` beschreibt
  Proposal-ID, Zielfingerprint, Zustandsversion, Kontext-Epoch, Risiko, Belege,
  Prüfplan und Reconciliation; `docs/executor-e1-content.md` unterscheidet
  Payload-Digest von tatsächlich gemessenem Effekt. Künftige Projektionen
  müssen diese Bindungen erhalten und fehlende oder veraltete Epoch-/Receipt-
  Belege offenlassen. Text oder UI-Freigabe ist kein ausgeführter, geprüfter
  Effekt. Die Dokumente enthalten zeitgebundene Kandidatenstände; keine
  vollständige heutige AIX→Runtime-Ausführung behaupten.
- **Grenze der vorliegenden Verknüpfung:** Ihre Links sind manuelle,
  quellengebundene Behauptungen. Sie prüfen keine Proposal-Digests, Leases,
  Kontext-Epochen, Signaturen, Projektidentitäten oder Live-Quellen. Sie starten
  weder Copilot noch Runtime und legen keine zweite Auftragsakte an.

Prüforakel für spätere Adapter: unveränderte Quelle/Kandidat/Scope positiv;
fehlende oder fremde Quelle, abweichender Digest/Kandidat, abgelaufene oder
unbelegte Autorität, alte Zustandsversion/Kontext-Epoch und nicht erfolgte
Reconciliation negativ. Bestehende Adapter und Rechtewege verwenden; keine
zweite Registry, keinen Scheduler und keinen Executor ergänzen. Owner,
P1-Dateiumfang und veröffentlichte Abhängigkeits-/Paketbindung für aethelema
sind vor dem Cross-Repo-Schnitt noch zu bestimmen.

## Erste explizite Quellenprojektionen

`project-observation` liest ein ausdrücklich bereitgestelltes
`aethel.projects.pm-input/v1`-Exportpaket und verlangt die exakte lokale
`--repository-id`, `--source-id` und `--evidence-id`. Keine automatische
Workspace-Suche, kein Öffnen referenzierter Dokumente. Mehrdeutige oder fehlende
Auswahl und unbekannte Versionen sind Strukturfehler. Die Ausgabe
`aethel.plm.project-observation/v1` bewahrt die berichteten Scan-/Exportzeiten
getrennt; Produktreferenz ist `null`, Aktualität `not_checked`. Der gemeldete
HEAD bleibt eine Quellenbehauptung. Das enthaltene `evidence`-Objekt kann
explizit in einem bestehenden `case/v1` referenziert werden. Weder Export noch
Repository oder Quelle werden durch diesen Parser verifiziert.

`copilot-observation` liest ein ausdrücklich übergebenes `aix.copilot_goal.v1`
und verlangt `--goal-id`, `--source-id` und `--evidence-id`. Es projiziert nur
Goal-ID, berichteten Zustand/Akteur/Agenten-ID/Modus/Zeit und die gemeldete
**Basisrevision**. Kein Prompt, Artefaktpfad, Eventlog oder Kontoinhalt wird
übernommen. Ergebnis `aethel.plm.copilot-observation/v1` meldet Aktualität und
tatsächlichen Inferenzort ungeprüft/`null`; die Basis ist kein Ergebnis- oder
Reviewkandidat. Beide Kommandos akzeptieren nur `--format json`. Ihre Ausgabe
ist ein Quellenbericht, niemals eine Freigabe, ein neuer Auftrag oder ein Lauf.

```sh
plm-evidence project-observation --input export.json --format json \
  --repository-id '<lokale-repository-identitaet>' --source-id '<quelle>' --evidence-id '<id>'
plm-evidence copilot-observation --input goal.json --format json \
  --goal-id '<goal-id>' --source-id '<quelle>' --evidence-id '<id>'
```

Kompatibilitätsprobe: Die **echte** Projects-Funktion `dossier.build` erzeugte
mit synthetischem Projekteintrag einen Export, der vom Adapter gelesen wurde;
dies ist kein Live-Repo-/Quellen-/Rechte- oder Frische-Nachweis. Copilot-Tests
nutzen synthetische Daten nach dem gelesenen vorhandenen Schema. Keine echten
privaten Akten, Prompts oder Zugangsdaten wurden übernommen. Ein prüfender
Adapter für Scope, Lease, Signatur, Provenienz und Aktualität sowie Bezüge zu
Bot-/Runtime-Läufen stehen aus. Versionierte Eingaben erlauben spätere Provider,
Träger und Quellen ohne zweite Rollen- oder Auftragsautorität.

Owner-/Paketprüfung 04.11.: Rollenlease nennt `codex-terra-aethelema-1028`, Gen 1,
`haelt`, Puls jedoch > 7 Tage alt; `bauer-aethelema/stand.json` enthält nur
TODO-Vorlage. Zuständiger aktiver Owner und Besitzfreigabe für P1 sind deshalb
nicht belegt. `flutter_rust_bridge` 2.13.0 und Codegen sind vorhanden. Ein
Git-Dependency-Pin auf den exakten PLM-Commit ist technisch reproduzierbar als
Quellreferenz, aber der PLM-PR ist noch ungeprüft/unveröffentlicht; eine
freigegebene Distribution und Cross-Repo-Verifikation sind nicht nachgewiesen.
Kein bewegliches lokales Workspace-Verzeichnis als Abhängigkeit eintragen.
Flutter-Anbindung bleibt offen. Keine fremde Rolle oder Worktree übernommen.

Paketprobe 04.11.: Ein isolierter temporärer Cargo-Verbraucher band den lokal
geklonten Git-Stand `434f2a42f9449a16076f72fe2f8968fcf5295392` über eine
explizite `rev` und baute beide Projektionsfunktionen erfolgreich. Das belegt
das Cargo-Paketlayout und den Commit-Pin, nicht den GitHub-Download, eine
veröffentlichte Version oder Flutter-/Plattformkompatibilität. Der Test nutzte
nur als Probe eine lokale file-URL; die Produktabhängigkeit darf keinen
veränderlichen Workspace-Pfad nutzen. Ein gemeinsamer, reviewter und
veröffentlichter bzw. fest commitgebundener Stand samt Lockfile ist als
P1-Vertrag festzulegen. Der aktuelle Owner ist wegen alter Lease/TODO-Stand und
nicht zugeordneten laufenden Prozessen weiter nicht sicher bestimmbar.

## Arbeitsraum und digitale Fabrik: Grenzen und nächste Verbindungen

Der eigenständige macOS-Pilot unter `components/plm-evidence/ui` zeigt
Rust-Ausgaben für Änderung, Qualität, Zusammenhang und explizit geöffnete
Quellen. Y-1 ist eine historische Momentaufnahme, kein Live-Status. Eine
Flutter-Rust-Bindung, die automatische Übernahme und Quellenverifikation sind
nicht implementiert. Einzelheiten und Start stehen in der dortigen README.

Für den weiteren Ausbau ist die gemeinsame Sicht auf die vorhandenen
Zuständigkeiten entscheidend, nicht eine neue zentrale Auftragsdatenbank:

| Schritt | Vorhandener Anknüpfungspunkt | Noch zu klärender oder zu belegender Übergang |
| --- | --- | --- |
| Bedarf und Produkt | Projects-Export und benannte Repositories | stabile Produkt-/Kundenreferenz und berechtigte Zuordnung zu Anforderungen und Entscheidungen |
| Auftrag und Verantwortung | AIX-TaskContract, Copilot-Goal und bestehende Rollen-/Lease-Akten | wirksamer Scope, aktuelle Besitzgeneration, Rechte und geladener Kontext |
| Ausführung | AIX/Copilot und bestehende austauschbare Ausführungswege | belegter Lauf mit tatsächlichem Modell, Host, Modus und Ergebnis; kein zweiter Executor |
| Änderung | Git-Commit/Tree und isolierte Arbeitsbereiche | Ergebnisrevision statt bloßer Basisrevision, unveränderte Kandidatenbindung |
| Prüfung und Landung | vorhandene Review- und aethelLanding-Verträge, `aix-merge-gated` | unabhängiges Review vor Gate, Gate am finalen Kopf, vertrauenswürdiger Review-/Prüfbeleg |
| Bereitstellung | versionsgebundene Artefakte und Betriebsdaten als notwendige Quellen | Verbindung von freigegebener Revision, gebauten Artefakten und tatsächlich installierter Version |
| Kundenwirkung | Issues, Maßnahmen und Wirksamkeitsprüfungen im Fachvertrag | reale Kunden-/Betriebsbelege, messbare Erfolgskriterien und gültige Wirksamkeitsentscheidung |

Die Aufzählung beschreibt Integrationsbedarf, keinen Nachweis, dass diese
Übergänge bereits Ende-zu-Ende laufen. Das vorhandene Landing-Architekturpapier
ist ein Vorschlag; einzelne Implementierungen und Produktionsnutzung sind
getrennt zu prüfen. Ein Git-Worktree oder eine selbst gemeldete erfolgreiche
Prüfung ersetzt keinen Review-, Gate-, Installations- oder Wirkungsbeleg.

Für eine digitale Firma fehlen zusätzlich explizite Verantwortlichkeiten und
Verbindungen für Angebot/Vertrag, Kunden und Support, Kosten und Kapazität,
Lieferanten und Lizenzen, Sicherheitsvorfälle, Betrieb und Produktstrategie.
Vor neuen Modulen sind jeweils bestehender Owner, Quelle, Zugriffsrecht und
konkrete Entscheidung zu bestimmen. Die Oberfläche soll lesend verbinden;
Änderungen und Aufträge verbleiben bei den zuständigen Systemen.

Cursor dokumentiert Git weiterhin als dauerhafte Versionsverwaltung;
Agenten-Checkpoints dienen dem lokalen Rücksetzen und Worktrees der Isolation
([Agent](https://cursor.com/docs/agent/overview),
[Worktrees](https://cursor.com/docs/configuration/worktrees)). Daraus folgt
kein nachgewiesener Ersatz für Git. Für Mistral ist AIX-seitig ein manueller,
nicht automatisch installierter Eintrag vorhanden. Ein historischer lokaler
Devstral-Versuch bestand ein enges Coding-Orakel, während ein anderer lokaler
Prior Devstral aus der Leiter ausschließt; die unterschiedlichen Belege
beweisen weder aktuelle Verfügbarkeit noch allgemeine Eignung. Mistral Vibe
beschreibt lokale Modelle über einen vorhandenen kompatiblen Dienst
([Dokumentation](https://docs.mistral.ai/vibe/code/cli/offline-models)).
Keinen neuen Server, keine bezahlte API und keine neue Modellrunde aus diesem
Papier ableiten; Review und Architektur bleiben unabhängig und hochwertig.

## Nächster Schnitt: Projektlandschaft als Einstieg

Manuels Ergänzung vom 04.11. verlangt eine sichtbare Projektlandschaft im
Arbeitsraum. Firma, Produkt, Projekt, Repository, Komponente, Auftrag, Rolle,
Lauf, Modell, Host, Release und Installation bleiben verschiedene Identitäten;
Beziehungen sind typisiert und können mehrfach vorkommen. Der Arbeitsraum ist
lesender Consumer: das Workspace-Manifest bleibt bestehendes Register, AIX
zuständig für Aufträge/Rechte/Ressourcen, Landing für Prüfung/Landung. Keine
Namensgleichheit als Identitätsnachweis und kein zweiter Executor.

Enger Bauschnitt: eine explizit übergebene datierte
`aethel.workspace.relationship-observation/v1`-Rechercheprojektion im Rust-Kern
strukturell prüfen und als versionierte, nicht autoritative Lesesicht darstellen;
Einstieg mit Suche, Bereichen, Beziehungen und Quelle. Die vorhandene Recherche
ist nicht atomar, nicht vollständig und enthält ausdrücklich ungeprüfte Kanten;
„bestehend“ bei einer Manifestkante bedeutet keine nachgewiesene Laufzeit.
Für den Pilot ist die Y-1-Fallakte nur anhand einer expliziten Zuordnung zur
genauen lokalen Repository-Identität anschließbar. Ein abweichender Kandidat
ist sichtbar, unbekannte Produktidentität bleibt unbekannt. Die beigefügte
Ansicht ist eine historische, pseudonymisierte Rechercheprojektion, kein neues
Register; ein ausdrücklich benannter Zusatz markiert weitere geplante Bezüge.

Orakel: Original-IDs, Mehrfachkanten, Status und Herkunft bleiben erhalten;
Namensgleichheit ordnet nicht zu; doppelte IDs blockieren; fehlende Endpunkte
bleiben als Lücke sichtbar; falsche Repository-ID blockiert die Fallzuordnung;
abweichende Kandidaten dürfen keine passenden Belege suggerieren. Die UI muss
von aethelBrowser nach Y-1 und zurück führen, offene Auftrags-, Review-, Gate-,
Lauf-, Liefer- und Wirkungsbelege anzeigen und auch geplante/ungeprüfte
Objekte auswählbar halten. Eine tatsächlich aktuelle AIX-/Git-/Release-Abfrage,
schriftliche Workflows, Quellenautorisierung und Live-Adapter sind nicht Teil
dieses Schnitts. Opus-Review vor finalem Gate bleibt unverändert.

## Cursor Origin, eigenständiges Landing und Helix

Cursor Origin ist eine Git-Forge mit nativen Repositories, PRs und Code Tours;
bei einem GitHub-Spiegel bleibt GitHub die führende Quelle. Seine API erlaubt
`expectedHeadSha` und kann bei gestapelten PRs mehrere Änderungen gemeinsam
landen. Ein passender PR-Kopf allein beweist weder eine unveränderte Basis noch
den tatsächlich geprüften Ergebnisbaum. Quellen: [Origin](https://cursor.com/docs/origin),
[Spiegel](https://cursor.com/docs/origin/mirror-github),
[Code Tours](https://cursor.com/docs/origin/code-tours),
[API](https://cursor.com/docs/api/origin).

Der gelesene aethelLanding-Stand `0a290bf` enthält bereits Kandidat, Siegel,
Urteil, Blocker, Queue, Audit und `landing_beleg`; die ältere README-Markierung
„design stage“ beschreibt nicht jeden heutigen Codebestand. Ein allgemeiner
eigenständiger Publikationsbefehl ist damit nicht nachgewiesen. Landing bleibt
eigene Python-/Git-Stdlib-Autorität; AIX ist Consumer. Für eine bessere
Reviewoberfläche: versionierte Änderungen und konkrete Landungsmenge, Diff und
Prüfbelege nachvollziehbar gruppieren sowie Änderungen seit dem letzten Review
zeigen. Gelesen, reviewt, gegatet, gelandet, installiert und wirksam bleiben
getrennte Zustände. Erklärtexte erteilen kein Urteil; das Öffnen benötigt keinen
Modellaufruf. Runner-/Policy-Pin aus der Basis, unabhängige Prüfung, versiegelter
Ergebnisbaum, Basis-CAS und Nachsiegel sind gegenüber einer reinen Kopfprüfung
zusätzliche Anforderungen. Eine Umsetzung in Landing braucht einen eigenen
besitzgebundenen Schnitt und dessen Review/Gate.

Manuels Ziel vom 04.11. umfasst **beides**: Landing unabhängig von AIX und
Hostingdienst sowie zusätzlich einen Git-freien Betrieb. Für Letzteres ist ein
versionierter Vertrag vorzuschlagen, nicht `landing.v1` still umzudeuten:
typisierter Kandidat aus Git-Baum oder kanonischem Artefakt-/Snapshot-Digest;
getrennte Inhalts- und Publikationsadapter; gleiche Regeln für Policy, Basis,
Prüfumfang, unabhängiges Urteil, atomaren Zielwechsel und Nachprüfung. Git lokal
oder bare sowie optionale Forge-Adapter sind ein möglicher Weg; ein unveränderlicher
Dateibundle-Snapshot wäre ein möglicher Git-freier Anfang. Kein Git-freier
Publikationsadapter ist hier gebaut oder freigegeben.

`aethelHelix` ist in Entwicklung. Der gelesene Stand dokumentiert HoloGit-Code
und Forschungsergebnisse, nennt aber äußere Authentifizierung/Reparatur und
einen dauerhaften Commit-/Historienvertrag als nächste offene Schritte. Helix
ist deshalb ein experimenteller möglicher Inhalts-/Transportadapter, keine
nachgewiesene Landing-Integration. Physischer Trägerhash, logischer
Inhaltsdigest, Decoder-/Formatversion und etwaige Git-OID bleiben verschiedene
Identitäten; Rekodierung ist nicht automatisch eine neue fachliche Freigabe.
Ohne nachgewiesene Crash-/Transaktionsgarantie keine Veröffentlichung über
diesen Pfad. Erst Vertrags- und Fehlertests, dann eigenständiger Durchstich;
Helix-Dateien und fremde Landing-Schnitte bleiben bei ihrem Owner.

Lesender Landing-Anschluss dieses Schnitts: `landing-observation` übernimmt
einen explizit bereitgestellten Bericht aus `landing verdict --check`, nicht
die Review- oder Gateautorität. Repository, Kopf, Quelle und Zeit werden vom
Aufrufer mitgegeben und nicht unabhängig verifiziert. Die datierte Y-1-Probe
nutzt PR 1518, dessen Kopf `532c170…` und die damals abgefragten PR-Kommentare;
ohne Gate-Log meldete Landing `no_structured_verdict_for_head`. Das ist keine
Aussage über nicht abgefragte Reviews, spätere Kommentare oder ein Gate. Der
historische Fall nennt `c1b0c46…`; die Oberfläche weist die unterschiedlichen
Commits aus, statt sie gleichzusetzen.

## Projektabdeckung und nächster Projects-Providerschnitt

Die separat vorgelegte symlinkfreie Recherche unterscheidet 323 auflösbare
Repositorygruppen, Archive und 41 nicht aufgelöste Git-Orte; daraus folgen
keine 323 eigenständigen Produkte und keine Laufzeitabnahme. Dauerhafte
Bestandsaufnahme und Herkunft gehören in bestehende `aethelProjects`-Scanner
und Exportverträge, nicht in einen zweiten Scanner oder eine neue Registry
dieses Arbeitsraums. Der engste Folgeschnitt am Provider ist: Cargo-Binärziele
und Workspace-Pakete, Flutter-Pakete und Python-Entrypoints mit Quellpfad,
Revision und Quelldigest entdecken; fehlende oder nicht gelesene Quellen,
Archive, Alias- und Registerkonflikte als offene Befunde erhalten. Das bestehende
Workspace-Manifest und `aethel-foundation/workspace-registry.yaml` sind
getrennte Quellen und vor einer Zuordnung abzugleichen. Consumer-Vertrag und
Providerrechte sind vor dem Eingriff in Dateien außerhalb dieses P0-Schnitts zu
binden. Kein vorhandener Scanner wird hier überschrieben.

Konkreter Referenzfall: `aethelOmegaLambda0` ist laut Cargo-Manifest des
Repositories `aethelOmegaM0` ein `[[bin]]` mit `src/bin/lambda0.rs`, kein
eigenes nachgewiesenes Repository. Das gelesene Manifest entspricht HEAD
`6e70e86176e7fcf2e9749a7f6bc986ce04171b80`, SHA-256
`3236be8c49d86c4379e2d57e085386112788a502e5da02cd0f8f64493813b579`.
Das Architekturpapier beschreibt 18 registrierte Angebote und begrenzte
Runtime-Tests; Registrierung belegt nicht jede Funktion. Die Python-Route
enthält als Simulation markierte Anteile. Dieser ausdrücklich belegte
Einzelbefund ist ein Zusatz zur Rechercheansicht, kein allgemeiner
Komponentenentdecker. Athelix beschreibt eine Low-Code-/Compilerlinie im
README; eine durchgängige Laufzeit wurde hier nicht geprüft. Fabrik-, Runtime-
und Sensorprojekte dürfen wegen ähnlicher Namen nicht gleichgesetzt werden.

Für die Informationsqualität zeigt der Arbeitsraum Quelle, Stand und
Revisionsbindung getrennt von der berichteten Aussage. Ein gezielter Lauf des
vorhandenen `aethelProjects.codeanalysis.head_findings` nutzte am 04.11. den
lokalen aethelCodeAnalyzer 0.1.0 für aethelOmegaM0 am HEAD `6e70e861…`: 2187
Fundstellen konnten an Quelldatei und Commit gebunden werden, vier wurden
verworfen. Die Konfiguration ist nicht digestgebunden, andere Sprachen als
Rust/Dart sind nicht vollständig abgedeckt; der Lauf ist kein Nachweis für
fehlerfreie Architektur oder Betrieb. Ein konkreter `high-complexity`-Hinweis
auf `src/bin/lambda0.rs:85` wird mit Datei-Digest angezeigt, seine fachliche
Behandlung ist offen. Er erzeugt keinen Auftrag. Das vorhandene README von
aethelema ist separat als datierte Dokumentationsaussage mit Revision und
Digest aufgenommen; sein Inhalt ist keine erneute Prüfung des Produkts.

Für einen späteren echten Durchstich vorhandene Befunde bei gleicher Quelle,
Tool-/Regelkonfiguration und Revision wiederverwenden; bei Änderung oder
fehlender Bindung neu beurteilen. Abgeschnittene Scans, unbekannte Sprachen und
verworfene Fundstellen dürfen nicht als mängelfrei erscheinen. Der existierende
`aix-input`-Adapter von Projects bindet ein ausgewähltes frisches Dossier an
einen rohen AIX-Eingang; AIX/Copilot bleibt für Paket, Rechte und Ausführung
zuständig. Erst eine Owner-Entscheidung über einen konkreten Fund, dann den
bereits vorhandenen Weg zu Auftrag, Ergebnis, Landing-Beleg und Rückmessung
verbinden. Keine automatische Auftragserzeugung oder zweiter Analyzerlauf allein
für die Oberfläche.

Eine nachfolgende, separat erstellte Katalogrecherche berichtet 685 Datensätze
einschließlich 61 zusätzlicher Manifestkomponenten und 986 Beziehungsangaben.
Diese neuere Recherche ist in der hier ausgelieferten älteren
Landschaftsprojektion noch nicht enthalten und nicht automatisch ein
Produktbestand oder Betriebsnachweis. Die dauerhafte Übernahme gehört in den
beschriebenen Projects-Providerschnitt mit Abdeckungs- und Identitätsprüfung.

Für spätere Produktfreigaben sind Bedienungsanleitung, Warnhinweise und
anwendbare rechtliche Anforderungen als versionierte Releasebestandteile mit
menschlicher Zuständigkeit vorzusehen. Diese Oberfläche erzeugt daraus weder
eine Rechtsbewertung noch ein Konformitätslabel. Versionsgebundene
Anforderung–Test–Release-Baselines und eine Verdachtsmarkierung nach Änderung
sind als nächster Fachvertrag zu prüfen; dieser Schnitt implementiert sie nicht.

## Firma, Fabrik und Produkt: Ist und nächste Schnitte

Der AIX-Stand `2ad5fb1c73a2ac921d5a873dd74bc6d750714cbc` enthält bereits
`config/aix-bom-chain.v1.json` mit eBOM, mBOM, pBOM und weiteren Sichten sowie
`config/aix-production-operations-model.v2.json` mit Produkt- und
Substratbindung. `_aix_sbom.py` erzeugt SPDX für begrenzte Eingaben;
`_aix_pbom.py` führt ein Herkunftsbelegbuch. Weder dessen Name noch ein
SPDX-Dokument beweist vollständige Fertigungs- oder Lizenzabdeckung.
`aix-firma-data-model.json`, `_aix_firma_workorder.py` und `_aix_feed.py`
enthalten Firmen-/Auftrags- und Engineering-Eingänge. Diese Verträge sind vor
Erweiterungen zu nutzen; Firma entscheidet Portfolio und Mittel, die Fabrik
führt qualifizierte Arbeit aus, Produkt und Betrieb belegen die Wirkung.

Gezielte Prüfhypothesen für den vorhandenen AIX-Owner: Feed prüft weiterhin
POM v1; ein v2-Compiler ist in den gelesenen Quellen nicht nachgewiesen. Ein
isolierter Ausfallfall meldete `job_ready=true` ohne einzelne Bind-/Digest-
Module; produktive Erreichbarkeit wurde nicht geprüft. Lifecycle-Demoweg enthält
Mock-Digest und Gate-Defaults; Caller und Identität vor einem Sicherheitsurteil
prüfen. HUD-Konstanten sind keine Telemetrie. Quellenkopie und Reproduktion:
`~/.codex/visualizations/2026/11/04/01a1a66e-4642-7242-8540-d5790ee619fd/aix-quellen/`.
Kein Eingriff in fremde AIX-Schnitte aus diesem Arbeitsraum.

Priorität 1: Y-1 über Firma, Fabrik und Produkt lesend verbinden; konkrete
Aufträge, mBOM, Installation und Feldwirkung bleiben ungeprüft, bis die
zuständigen Quellen sie binden. Priorität 2: bestehende Engineering-Eingabe um
quellengebundene Produktentscheidung, Anforderungen, Produktstruktur, mBOM,
Arbeits- und Prüfplan ergänzen; offene Entscheidungen nicht automatisch füllen.
Priorität 3: Firmen-/Investorenansicht mit Berechtigungen, getrenntem Cap Table
und nachvollziehbaren, datierten Bewertungsannahmen; keine Bewertung aus
Commitzahlen. Priorität 4: Release und Markt an Anleitungen, Warnungen und
rechtliche Prüfung durch zuständige Menschen binden. Diese Prioritäten sind
Vorschläge, keine implementierten oder freigegebenen Prozesse.

## Owner-Hinweis und Abgrenzung

Manuel meldet drei wieder arbeitende Claude-Arbeitsbereiche: AIX/Copilot,
Workspace-Übersicht und aethelBot/aethelema. Das ist ein aktueller
Owner-Hinweis, keine unabhängig geprüfte Lease oder Dateisperre. Die
Workspace-Übersicht kann den Projects-/Arbeitsraum-Schnitt überschneiden.
Vor weiteren überlappenden Änderungen Dateibesitz, Branch, HEAD, laufenden
Schreiber und bestehende Übergabe im zuständigen System prüfen; bei unklarer
Bindung nur den betroffenen Schreibschnitt zurückstellen. Keine zweite
Registry, keinen zweiten Scanner und keinen parallelen Schreiber anlegen.

AIX-Kernbefunde gehören zur Prüfung durch den AIX/Copilot-Owner; Bot- und
aethelema-Integration zum dortigen Owner. Dieser Schnitt bleibt bei
versionierter Produkt-/Änderungsakte, belegtem Zustand und lesender Darstellung
vorhandener Projects-Projektionen. Eine Übergabe der AIX-Befunde oder eine
aktive Besitzerbestätigung ist durch diesen Hinweis noch nicht belegt.

Besitzabgleich nach Claudes durch Manuel übermittelter Antwort: Der Schnitt
`components/plm-evidence/**` und dieses Dokument sind parallel frei. Claudes
Projects-PRs #2–#4 betreffen `src/aethel_projects/**`, `tests/**`, `analysen/**`
und andere Projektdokumente, nicht `components/`; der laufende Worker arbeitet
an `aethelScripts`. Keine dieser fremden Dateien wurde geändert. Der Arbeitsraum
zeigt nun einen eigenen Produkteinstieg für den historischen Y-1-Fall und
getrennte Firmen-, Fabrik- und mBOM-Fragen. Ein datierter Projects-Leitstand
aus PR #2 wird über `cockpit-observation` projiziert; er ist kein Live-Stand.
Der AIX-POM-v2-Vertrag beschreibt die mBOM-Felder, aber kein konkreter Y-1-
Fertigungsauftrag oder dessen mBOM wurde hier gefunden oder geprüft.

Zukünftige Gesamt- und Rollenansichten müssen auf denselben berechtigten
Quellen beruhen. Rollenfilter allein sind keine Datenzugriffskontrolle; Finanz-
und Investorendaten brauchen Rechte an der Quelle. Dieser Schnitt implementiert
keine Rollenautorisierung und keine finanzielle Bewertung.

## Lesende AIX-/Projects-Quellenauswahl (04.11.2026)

Die Flutter-Dateiauswahl akzeptiert die Originalformate `aethel.projects.cockpit/v1`,
`aix.dashboard.v2` und `aix.engineering_input.v1` mit Fabrikteil. Projects
`cockpit --format json` und AIX `aix-dashboard state --json` bleiben die
Erzeuger; der Arbeitsraum speichert keine neuen Aufträge und führt keine
Fabrikprozesse aus. Die Adapter wurden mit aktuellen Kommandoausgaben geprüft;
keine automatisierte Live-Synchronisation. Dashboard-Prompt und Telemetrie
werden nicht in den angezeigten AIX-Ausschnitt übernommen.

Der auswählbare AIX-Engineering-Input zeigt POM-Version, Auftrags-, Linien-,
Stations-, Produkt-, Host- und Outputangaben mit Quelle. Das ist eine lesende
Anzeige, kein Validator. Die Quelle `aix.engineering_input.v1` bindet in ihrem
bestehenden Schema POM v1; POM v2 ist dokumentierter Zielvertrag. Es wurde kein
konkreter Y-1-Auftrag mit v2-Produktbindung gefunden. Weder Name noch manuelle
Auswahl belegen eine Y-1-Zuordnung, einen Lauf, eine Freigabe oder Installation.
Nächster Schnitt: autoritative Auftragsreferenz und ausgeführte v2-Quelle mit
dem AIX-Owner klären und die bestehende AIX-Prüfung integrieren.

## Lokale AIX-Dashboard-Verbindung

Die Oberfläche kann das bereits vorhandene AIX-Dashboard nach ausdrücklichem
Start durch den Nutzer über `127.0.0.1:7331/api/state` alle 30 Sekunden
lesen. Keine Umleitung, kein Proxy, höchstens 1 MiB, begrenzte Wartezeit;
Fehler kennzeichnen den letzten Stand als möglicherweise veraltet. Der Adapter
übernimmt weder den Prompt noch Rohtelemetrie in seine Darstellung. Das
Dashboard wird nicht durch den Arbeitsraum gestartet und die Verbindung ist
nicht authentifiziert: Die Quelle ist eine ungeprüfte lokale Behauptung.
Die Sandbox erhält das Netzwerk-Client-Entitlement; der implementierte Client
verwendet ausschließlich den lokalen Dashboard-Pfad. Getrennte POM-/Y-1- und
Projects-Live-Anbindung bleiben offen.

AIX-Owner-Auskunft vom 04.11.2026 im Chat „AIX/Copilot 0.10 Fertigstellung“:
Bei seiner lesenden Prüfung von `origin/main`, Auftragsledger und
Produktionsplan fand Claude keinen konkreten Y-1-Auftrag mit Produkt-/
Kandidatenbindung oder mBOM. Die gefundenen Browser-Aufträge sind andere
Korpusfälle und werden nicht zu Y-1 zusammengeführt. Er nennt das Ledger als
read-only SQLite-Quelle für `aix.auftrag.v2`; `aix-kernel auftrag` sei wegen
Sperre und Migration kein rein lesender Weg. Dies ist eine Owner-Auskunft mit
dem genannten Prüfumfang, kein Beweis weltweiter Nichtexistenz. Die frühere POM-v2-Dokumentation ist im AIX-Commit
`2ad5fb1c73a2ac921d5a873dd74bc6d750714cbc` tatsächlich enthalten; die
abweichende Aussage zur POM-Suche ist nicht auf einen von Claude genannten
Commit zurückgeführt. Die Differenz bleibt ungeklärt. Y-1-Bindung und ihre autoritative Quelle
bleiben offen. Die Dashboard-Verbindung zeigt einen generischen Betriebsstand,
nicht den Y-1-Auftrag.

## Y-1: Auftrags- und Fertigungsentwurf zur Klärung (04.11.2026)

Manuel hat für diesen Entwurf das historische Ziel und den historischen
Code-Kandidaten bestätigt. **Entwurf, nicht im AIX-Ledger angelegt oder
gebunden; keine Ausführungs-, Schreib- oder Freigabeautorität.** Ein gültiger
AIX-Auftrag entsteht erst über den vorhandenen AIX-Auftrags- und Besitzvertrag.

| Feld | Vorschlag / bekannter Stand |
| --- | --- |
| Zweck | Google-/YouTube-Anmeldung im identifizierten aethelBrowser-Build bis zum sichtbar angemeldeten Zustand ermöglichen und belegen. |
| Fallreferenz | `Y-1` aus `components/plm-evidence/fixtures/y1-historical.json`; noch keine AIX-Auftrags-ID. |
| Repository | `https://github.com/AETHEL-Omega/aethelBrowser.git`; genaue lokale Arbeits- und Produktidentität muss AIX binden. |
| Kandidat | Historischer Code-Commit `c1b0c46cbae60a69a00332a050841044e64b32e1`, Git-Tree `b09c77c936c088c4e87bb487d3be6a41f069cb17`. Manuel hat ihn **für den Entwurf** gewählt, nicht als aktuellen Release bestätigt. |
| Abweichender Branchkopf | Lokal bekannte Remote-Referenz `origin/fix/y1-google-ua-chain`: `532c170bd23ca9d5f905262c4fad9bb043b92937`, Tree `e8a6334c694a94c23c688bae6cb40198f7382b74`. Dieser enthält nach dem Code-Commit einen Changelog-Commit; sein Tree ist nicht derselbe Kandidat. Remote-Aktualität nicht geprüft. |
| Ergebnisnachweis | Echter Login im identifizierten Browser-Build, unabhängiges Review und Gate am tatsächlich geprüften Stand sowie belegte Installation und Wirkung; nicht aus Unit-Test oder Changelog allein ableiten. |
| Verantwortung | Zuständiger Produkt- und Auftrags-Owner, Besitzgeneration, Rechte und zugelassener Ausführungsweg offen; AIX ist dafür zuständig. |

### mBOM: konkreter Bindungsbedarf, noch keine Quelle

Als **Vorschlag** dient der POM-v2-Vertrag im untersuchten lokalen AIX-Stand
`2ad5fb1c73a2ac921d5a873dd74bc6d750714cbc`,
`config/aix-production-operations-model.v2.json`. Dieser Vertrag beschreibt
Felder, belegt jedoch weder eine erzeugte mBOM noch einen produktiven Compiler
oder die Gültigkeit auf dem später verwendeten AIX-Stand. Der aktuelle
Engineering-Input-Vertrag nennt POM v1. Die Differenz ist mit dem AIX-Owner zu
klären; keine zweite Registry oder eigener POM-Compiler im Arbeitsraum.

Für eine spätere konkrete, versionierte mBOM müssen mindestens diese Bindungen
aus der zuständigen AIX-Quelle kommen:

- AIX-Auftrags-ID, Revision und zuständiger Owner; Produktidentität und
  Repository-Identität sowie der tatsächlich gebundene Kandidat/Arbeitsstand.
- Spezifikationsdigest und Modellreferenzen als eBOM-Anker sowie
  Produktionsmodus; alle derzeit **offen**.
- Hostprofil und Compute-Modus, Fertigungslinie/Station, Abhängigkeiten und
  Ressourcenbudget; alle derzeit **offen**.
- Outputvertrag und versionierte mBOM-Quellreferenz mit Digest; beide derzeit
  **offen**. Eine pbom.jsonl oder ein POM-Schemadokument ist nicht automatisch
  die mBOM dieses Auftrags.
- Verweise auf die zum selben Kandidaten passenden Review-, Gate-, Build-,
  Installations- und Wirkungsbelege, soweit vorhanden; deren Fehlen bleibt
  sichtbar und erzeugt keinen erfolgreichen Zustand.

### Automatische Anbindung: benötigter nächster Vertrag

Den von AIX bestätigten lesenden Ledger-Zugang (`aix.auftrag.v2` über SQLite
`mode=ro`) erst mit einer **echten** Auftrags-ID, spezifiziertem
Ereignis-/Revisionsvertrag und geklärter Zugriffsbefugnis verwenden. Vor einer
Anzeige müssen Produkt-, Kandidaten- und mBOM-Referenzen exakt zugeordnet und
Quelle, Zeitpunkt, Revisionsstand, fehlende Felder und Lesefehler ausgewiesen
werden. Unbekannt, mehrdeutig, veraltet oder abweichend bleibt unverbunden.
Die allgemeine Dashboard-Projektion ist kein auf Y-1 gebundener Auftrag.
Bis zum Vorliegen der echten Quelle gibt es keine automatische Y-1-mBOM-
Anbindung. Dieser Entwurf erzeugt weder ein Ledger-Ereignis noch einen
Fertigungsauftrag; die verbleibende Entscheidung ist die Einführung und
Belegung des Auftrags über den AIX-Owner.

## Erneutes Lesen ausgewählter Projects-Exporte

Ein über den Dateidialog gewählter Originalexport `aethel.projects.cockpit/v1`
wird während der Sitzung alle 30 Sekunden erneut eingelesen. Fehler, ungültige
oder zu große Dateien lassen den letzten Stand mit Veraltet-Hinweis stehen.
Die Dateiauswahl kann beendet werden; nach App-Neustart muss sie erneut
erfolgen. Die App startet keinen Projects-Scan und erzeugt keinen Export.
Das Zeitpunkt-/Aktualitätsproblem der eigentlichen Daten bleibt unaufgelöst;
das neue Lesen ist keine Quellen- oder Autoritätsprüfung.

## AIX-Erstellungslauf für Y-1 (04.11.2026)

Der vorhandene installierte `aix-copilot auftrag` hat einen Engineering-Input
für einen isolierten Checkout des ausgewählten historischen Commits erzeugt
(`c1b0c46cbae60a69a00332a050841044e64b32e1`, Tree
`b09c77c936c088c4e87bb487d3be6a41f069cb17`). Seine automatische Ableitung
meldete `contract_ready=true`, machte aber `flutter test` zur einzigen
Abnahme und nannte als Erfolg lediglich Exit 0. Das belegt weder den echten
Login noch separates unabhängiges Review oder Installation und Wirkung. Die
vorgeschlagene Freigabe **und Ausführung** wurde deshalb nicht erteilt.

Der aus dem AIX-Entwurf bearbeitete, bewusst nicht freigegebene Eingang liegt
unter `components/plm-evidence/fixtures/y1-aix-engineering-draft.json`.
Sein Projektpfad und die Akzeptanz bleiben offen; `extensions.y1_mbom_proposal`
enthält nur die nicht gebundenen, überwiegend unbekannten POM-v2-Felder. Sie
sind weder eine gültige mBOM noch ein neuer AIX-Zustand. Bei der Prüfung mit
`aix-feed review` und dem isolierten Checkout meldete AIX
`contract_ready=false`, Digest
`aa5e2b2a56f8b23af803dbc1a4c2caaf158649564c6f529d42f20a94ec2c69b1` und
blockierte wegen fehlender Kriterien, Projektpfad, Scope, Ausschlüssen und
Akzeptanz. Dieser Digest gilt nur für den konkreten Prüflauf und ersetzt
keine Freigabe.

Eine getrennte POM-v2-Probe im bestehenden Feed zeigte zusätzlich den
blockierenden Befund `factory.pom`: Der implementierte Feed fordert POM v1;
weitere Fertigungsfelder sind ungebunden. Der installierte Kernel meldete in
seiner Hilfe keinen `auftrag`-Befehl; der in einem anderen Checkout vorliegende
`aix-kernel auftrag` migriert das Produktivledger und beansprucht Besitz.
Ein für diesen Fall bestätigter installierter, berechtigter Auftragsweg und
eine gültige mBOM-Quelle sind somit nicht nachgewiesen. Kein Besitz und keine
Ledger-Bindung wurden vorgetäuscht. Automatische mBOM-Anbindung bleibt offen,
bis der zuständige AIX-Weg und die konkrete Quelle verfügbar sind.

## AIX-POM-Schnitt und Kernel-Abhängigkeit (04.11.2026)

Der separate AIX-Draft-PR `ManuelWilde/aethelScripts#1387`, Kopf
`a75607a4066694ff4756a734e8e3b034c3c700aa`, ergänzt eine strukturelle
POM-v2-Prüfung im vorhandenen Feed und Schema. Der Feed hält v2 mit
`factory.v2_runtime` bewusst blockiert: Eine Fabriklaufzeit, die die Produkt-,
Host- und Outputbindung bis zum Ergebnis nachweist, ist noch nicht belegt.
Die gezielte Feed-Suite meldete 65 bestandene Tests; Opus-Review, Gate und
Landung stehen aus. Der AIX-Kernel-Schutzschnitt `#1379` ist separat offen;
er schützt das echte AIX-Heim vor Entwicklungskernen, installiert aber keinen
neuen Kernel. Er war bei der Abfrage nicht mergefähig (`DIRTY`). Die
Fertigstellung des installierten Auftragswegs, die tatsächliche Y-1-Bindung,
die echte mBOM-Quelle und deren automatische Zuordnung bleiben offen. Es
wurden weder die Produktivinstallation noch das Produktivledger verändert.

## Kernelkorrektur und POM-Arbeitspaket (04.11.2026)

Die frühere Aussage zum installierten Auftragskernel betraf `~/bin/aix-kernel`
und war für die angeheftete Copilot-Laufzeit unvollständig: Der tatsächliche
Release-Zeiger zeigte bei der Probe auf
`~/.aix/copilot/releases/cc4139e4fddc9fb258ea03bb6791af6cfd94960e/bin`.
Dessen Kernel verarbeitet `auftrag arbeitsstand`, obwohl der Befehl in seiner
Hilfe fehlt. Mit eigenem `AIX_HOME` unter `/private/tmp` gab er für den
isolierten historischen Browser-Checkout Commit `c1b0c46…` und einen
Arbeitsstand-Digest aus. Das belegt weder eine Produktiv-Ledger-Bindung noch
Bereitschaft des gesamten Auftragswegs. Der wirksame AIX-Modus war bei der
Prüfung `LOCAL_AI_ONLY`.

Im AIX-Schnitt #1387 werden POM-v2-Daten zusätzlich unverändert in das
Engineering-Arbeitspaket und dessen Digest übernommen. Die Paketprüfung und
ASSM-Admission blockieren v2 weiter, auch bei einer behaupteten Ready-Meldung.
Die Prüfung mit 76 Feed-Tests war grün; die breitere ASSM-Suite meldete drei
Mill-Testfehler, die am unveränderten AIX-Basiskopf identisch auftraten
(jeweils 63 bestanden, 3 fehlgeschlagen). Eine Laufzeitprüfung realer
Produkt- und Hostbindung sowie die Y-1-mBOM bleiben offen. Kein produktiver
Auftrag, kein Produktionsledger und keine Installation wurden verändert.

POM v2 kann `HYBRID` als deklarierte Planung tragen. Der Feed blockiert
abweichende Ausführungs-/Hostmodi und das nicht eindeutig auf die vorhandene
AIX-Autorität abgebildete `CLOUD_ALLOWED`. Der tatsächlich wirksame Modus,
Ressourcen- und Datenfreigaben bleiben beim bestehenden AIX-Pfad; diese
Vorprüfung ändert keine Prefs und genehmigt keine Cloud-Nutzung. AIX-PR #1387
stand nach dieser Ergänzung auf `9e8910392e43a6321770bdb81336ea18e8be9b80`.

Ergänzende isolierte Kernelprobe: Derselbe Release-Kernel hat im eigenen
`AIX_HOME=/private/tmp/aix-y1-kernel-probe` unter der ausdrücklich als Probe
benannten Kennung `probe-y1-only` Besitzgeneration und Auftragskontext für den
historischen Checkout erzeugt (`revision=0`, `modus=LOCAL_AI_ONLY`,
Kontextdigest vorhanden). Das sind ausschließlich Testdaten. Es wurde kein
Modelllauf und keine `binde`-Aktion durchgeführt; die Probe belegt weder
produktive Besitzerrechte noch einen echten Y-1-Auftrag oder eine mBOM.

AIX-PR #1387, Kopf `20e606f612859f4adee528e24067d69d3b7db51a`, ergänzt eine
ASSM-Laufzeitvorprüfung: Das deklarierte Hostprofil wird mit der vorhandenen
Host-Erkennung und der deklarierte Modus mit der wirksamen AIX-Modusautorität
verglichen. Fehlende oder abweichende Angaben blockieren. Auch bei passenden
Beobachtungen bleiben Host-Lease, Produkt- und Outputbindung ungeprüft und
POM v2 wird nicht freigegeben. Ein direkt gestartetes oder fortgesetztes Goal
mit POM v2 hält vor dem Ausführungspfad an. Prüfergebnis: 80 Feed-Tests und
der gezielte Goal-Test grün. Es existieren weiterhin kein produktiv gebundener
Y-1-Auftrag und keine maßgebliche mBOM-Quelle; eine automatische Anbindung darf
dies nicht suggerieren. Das separate Opus-Review ist ausstehend.
