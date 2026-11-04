# Flutter–Rust Evidence Bridge · P1

Dieser isolierte P1-Schnitt ruft den bestehenden `plm-evidence`-Fachkern über
`flutter_rust_bridge` 2.13.0 auf. Die drei JSON-Funktionen werten Änderungen,
Qualität und verknüpfte Fälle im Speicher aus. Sie lesen keine Quellen, starten
keine Aufträge und erteilen keine Verifikation oder Freigabe. Die Eingabe ist
auf 8 MiB begrenzt; ungültige Eingaben liefern einen Fehler.

`EvidencePanel(caseJson: ...)` stellt eine Änderungsauswertung dar. Der
Aufrufer initialisiert vorher `RustLib` und stellt die native Bibliothek bereit.
Das Paket ist noch nicht in die bestehende Projects-Oberfläche eingebunden und
enthält noch keine macOS-Release-Paketierung der nativen Bibliothek. Echte AIX-
Aufträge und der laufende Dashboard-Dienst gehören zum separaten Quellenweg.

Lokale native Prüfung auf macOS mit vorhandenen Abhängigkeiten:

```sh
CARGO_BUILD_JOBS=1 cargo build --offline --manifest-path rust/Cargo.toml
flutter pub get --offline
flutter test --no-pub test/native_bridge_test.dart
```

Die Tests laden die gerade gebaute Debug-Bibliothek explizit. Sie belegen die
lokale Flutter→Rust-Verbindung einschließlich des Widgets, keine Installation,
keinen Release-Build und keinen echten Y-1-Login. Der P0-Kern bleibt bis Review,
Gate und Landung ein fest referenzierter, noch nicht freigegebener Kandidat.
