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
