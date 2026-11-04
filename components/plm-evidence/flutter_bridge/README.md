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

## Übergabe für den Projects-UI-Schnitt

- Der gesamte selbstständige Paketbaum liegt unter
  `components/plm-evidence/flutter_bridge/`; sein Rust-Paket verwendet den
  vorhandenen Fachkern über `path = "../.."` innerhalb desselben Repositories.
  P1-Quellbasis: Branch `codex/plm-p1-bridge`, Commit `b185959`.
- Die App kann das Dart-Paket als `aethel_evidence_bridge` über den relativen
  Paketpfad `../flutter_bridge` einbinden. Sie benötigt `flutter_rust_bridge`
  2.13.0; die Lockfiles liegen diesem Schnitt bei. Im UI auf eine gemeinsame
  Version auflösen, keine zweite Bridge-Version installieren.
- Einstieg für die Änderungsauswertung: `EvidencePanel(caseJson: ...)` aus
  `package:aethel_evidence_bridge/aethel_evidence_bridge.dart`. Vorher muss
  `RustLib.init` erfolgreich abgeschlossen sein. Für Qualität und verknüpfte
  Fälle stehen `assessQualityJson` und `assessLinkedJson` zur Verfügung.
- Der Quellstand allein reicht für die native Laufzeit **nicht**. Der Test
  lädt auf macOS `rust/target/debug/libaethel_evidence_bridge.dylib` explizit.
  Für eine ausgelieferte App muss die passende Architektur-Bibliothek in den
  App-Build eingebettet und mit diesem signiert werden. Der generierte
  Standardlader sucht sonst auch relativ zu `rust/target/release/`; das ist
  kein tragfähiger Installationsvertrag. Keine absolute Worktree-Abhängigkeit
  in die App oder ihren Release aufnehmen.
- Es gibt hier keine Änderungen an `ui/lib/main.dart`, `ui/pubspec.yaml` oder
  dem Xcode-Projekt. Deren Anschluss und das Lebenszyklus-/Fehlerverhalten
  gehören in den parallel geführten UI-Schnitt. Die Live-Auftragsquelle bleibt
  `readLocalAixOrders` / `/api/orders`; sie ist keine Auswertung der Bridge.

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
