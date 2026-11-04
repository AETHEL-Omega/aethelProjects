# AETHEL Arbeitsraum – lesender Pilot

Eigenständiger Flutter-Prototyp für macOS. Er zeigt eine historische
Momentaufnahme des aethelBrowser-Piloten Y-1 sowie ein synthetisches
Qualitätsbeispiel. Die Ansichten verbinden Aussagen, referenzierte Belege,
Issues und Maßnahmen, ohne aus einer Verknüpfung eine geprüfte Erfüllung
abzuleiten. `Quelle` zeigt gesondert geöffnete Projects- und Copilot-Berichte;
eine automatische Zuordnung zu einer Änderung findet nicht statt.

## Start

Mit installiertem Flutter-SDK und lokal verfügbaren Abhängigkeiten:

```sh
cd components/plm-evidence/ui
flutter pub get --offline
flutter run -d macos
```

Über **Auswertung öffnen** lässt sich eine JSON-Ausgabe des Rust-Fachkerns
auswählen. Ein Beispiel kann vom Repository-Wurzelverzeichnis aus erzeugt
werden:

```sh
cargo run --offline --manifest-path components/plm-evidence/Cargo.toml -- \
  assess --input components/plm-evidence/fixtures/y1-historical.json --format json \
  > /tmp/aethel-y1-assessment.json
```

Die Quelldateien der beiden eingebauten Beispiele sind Rust-Ausgaben; die
Oberfläche berechnet keine fachlichen Zustände selbst. Sie kann außerdem die
versionierten Ausgaben von `project-observation` und `copilot-observation`
einzeln öffnen. Die Kommandos und deren Grenzen stehen in
[`docs/PLM-EVIDENCE-P0.md`](../../../docs/PLM-EVIDENCE-P0.md).

## Grenzen

- Ein Dateidialog öffnet explizit ausgewählte Dateien. Quelle, Autorität und
  Aktualität der Inhalte werden nicht verifiziert. Die Prüfung des nativen
  Dateidialogs war zuletzt nicht vollständig abgeschlossen.
- Es gibt noch keine native Rust-Anbindung, keine automatische Aktualisierung,
  keine Live-Anbindung an AIX, Projects, Landing, Git oder aethelBrowser und
  keine Schreib-, Auftrags-, Ausführungs- oder Mergefunktion.
- Die historische Momentaufnahme ist kein aktueller Produkt- oder
  Freigabestand. Die Beispiele belegen weder eine gültige Produktidentität
  noch die Wirksamkeit einer Maßnahme.
- Der macOS-Debug-Build ist ein Prototyp, keine unabhängig geprüfte,
  signierte und notarisierte Veröffentlichung.
