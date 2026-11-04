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
