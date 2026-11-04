# AETHEL Arbeitsraum – lesender Pilot

Eigenständiger Flutter-Prototyp für macOS. Einstieg ist eine datierte,
pseudonymisierte Rechercheprojektion der Projektlandschaft: 624 Einträge und
921 Beziehungen aus dem ursprünglichen Bericht sowie zwei ausdrücklich
gekennzeichnete Komponenten und drei Beziehungen als Zusatz. Es handelt sich
nicht um 626 eigenständige Produkte. Die Quelle enthält Erfassungsprobleme,
ausgelassene Pfade und ungeprüfte Beziehungen; diese Grenzen sind einsehbar.

Die Oberfläche zeigt eine historische Momentaufnahme des aethelBrowser-Piloten
Y-1 sowie ein synthetisches Qualitätsbeispiel. Die Ansichten verbinden Aussagen, referenzierte Belege,
Issues und Maßnahmen, ohne aus einer Verknüpfung eine geprüfte Erfüllung
abzuleiten. Die Landing-Leseprobe zu PR 1518 wurde am 04.11. aus den damals
abgefragten PR-Kommentaren ohne Gate-Log erzeugt. Ihre Zuordnung zum exakt
passenden lokalen Repository muss in der Oberfläche ausdrücklich erfolgen;
unterschiedliche Kandidaten werden angezeigt. Sie belegt keine Landung.

## Start

Mit installiertem Flutter-SDK und lokal verfügbaren Abhängigkeiten:

```sh
cd components/plm-evidence/ui
flutter pub get --offline
flutter run -d macos
```

Über **Auswertung öffnen** lässt sich eine JSON-Ausgabe des Rust-Fachkerns
auswählen. Eine neue Landschaftsprojektion wird explizit aus einer vorhandenen
Recherchedatei erzeugt und anschließend geöffnet:

```sh
cargo run --offline --manifest-path components/plm-evidence/Cargo.toml -- \
  landscape-project --input projektgraph.json --format json --source-id 'Recherche 04.11.2026' \
  > /tmp/aethel-landschaft.json
```

Für eine Fallzuordnung sind außerdem ein ausdrücklich gebundenes `--binding`
und die zugehörige `--case`-Datei nötig; Beispiele stehen in `fixtures/`.
Bereiche werden aus mitgelieferten Angaben oder Manifestkategorien gebildet;
ohne solche Angabe bleibt ein Eintrag unter „Unzugeordnet“ auffindbar. Das
integrierte Beispiel verwendet pseudonymisierte Pfade; ein Export mit echten
lokalen Identitäten darf nicht anhand des gleichen Namens damit verschmolzen
werden.

Eine Fallauswertung kann vom Repository-Wurzelverzeichnis aus erzeugt
werden:

```sh
cargo run --offline --manifest-path components/plm-evidence/Cargo.toml -- \
  assess --input components/plm-evidence/fixtures/y1-historical.json --format json \
  > /tmp/aethel-y1-assessment.json
```

Die Quelldateien der beiden eingebauten Beispiele sind Rust-Ausgaben; die
Oberfläche berechnet keine fachlichen Zustände selbst. Sie kann außerdem die
versionierten Ausgaben von `project-observation`, `copilot-observation` und
`landing-observation`
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
