# AETHEL Arbeitsraum – lesender Pilot

Eigenständiger Flutter-Prototyp für macOS. Der Produkteinstieg zeigt den
historischen Y-1-Fall sowie getrennte Fragen für Firma, Fabrik und mBOM. Der
eingebundene Projects-Leitstand stammt aus dem abgelegten Export vom
03.11.2026 aus PR #2; Aktualität und Autorität werden nicht live geprüft. Die
mBOM-Karte beschreibt AIX-Vertragsfelder, keinen nachgewiesenen Y-1-Auftrag.

Die Projektlandschaft ist eine datierte,
pseudonymisierte Rechercheprojektion der Projektlandschaft: 624 Einträge und
921 Beziehungen aus dem ursprünglichen Bericht sowie zwei ausdrücklich
gekennzeichnete Komponenten und drei Beziehungen als Zusatz. Es handelt sich
nicht um 626 eigenständige Produkte. Die Quelle enthält Erfassungsprobleme,
ausgelassene Pfade und ungeprüfte Beziehungen; diese Grenzen sind einsehbar.
Trefferliste und Details zeigen gleichnamige Repositorygruppen und
Registereinträge getrennt. Zweck, deklarierter Stand, Beleglage, installierter
Stand und offene Fragen sind eigene Felder. Ausgewählte, datierte Quellen
ergänzen das aethelema-README und einen tatsächlichen lokalen CodeAnalyzer-Lauf
für aethelOmegaM0; verworfene Fundstellen und unbekannte Konfiguration werden
ausgewiesen. Die Einzelfunde sind kein Qualitätsurteil für das gesamte Projekt.

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

Eine vorhandene Projects-Leitstanddatei im Schema
`aethel.projects.cockpit/v1` kann ebenfalls ausdrücklich projiziert und über
**Auswertung öffnen** geladen werden. Der Quellenbezeichner ist eine Angabe,
keine Prüfung der Herkunft:

```sh
cargo run --offline --manifest-path components/plm-evidence/Cargo.toml -- \
  cockpit-observation --input /pfad/zum/leitstand.json --source-id 'Projects-Export' --format json \
  > /tmp/aethel-cockpit.json
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

## Aktuelle Quellen ausdrücklich öffnen

**Auswertung öffnen** akzeptiert auch unmittelbar die JSON-Ausgaben von
`aethel.projects.cockpit/v1`, `aix.dashboard.v2` und einen
`aix.engineering_input.v1` mit `factory`-Abschnitt. Die Auswahl ersetzt keine
Quellen- oder Rechteprüfung. Der AIX-Dashboard-Adapter übernimmt nur Zeitpunkt,
Goal-Kennung, Zustand und Belegstatus; der Dashboard-Export selbst kann weitere
private Angaben enthalten. Dateien geschützt ablegen und nach Gebrauch löschen.
Die Dateiquellen müssen bewusst exportiert und ausgewählt werden. Zusätzlich
verbindet **AIX lokal verbinden** das bestehende Dashboard unter
`127.0.0.1:7331/api/state` lesend und aktualisiert es alle 30 Sekunden bis zum
Beenden der Verbindung oder der App. Die App startet keinen Dienst. Ist das
Dashboard nicht verfügbar oder die Antwort ungültig, wird ein früherer Stand
als möglicherweise veraltet gekennzeichnet. Loopback und Schema belegen weder
die Identität des Dienstes noch eine Produktzuordnung. Ein über den Dateidialog gewählter Projects-Cockpit-Export wird während der
Sitzung alle 30 Sekunden erneut gelesen; bei Fehlern bleibt der letzte Stand mit
Warnung sichtbar. Der Arbeitsraum erzeugt keinen neuen Export, prüft dessen
Alter nicht und speichert die Dateiberechtigung nicht für den nächsten Start.
Die mBOM wird noch nicht automatisch aktualisiert.

Beispiel mit vorhandenen Werkzeugen und einem Projects-Checkout, der `cockpit`
bereitstellt (derzeit PR #2):

```sh
umask 077
PYTHONPATH=/pfad/zu/aethelProjects/src python3 -m aethel_projects.cli \
  cockpit --base /pfad/zu/aethelProjects/analysen --format json > /tmp/projects-cockpit.json
/pfad/zu/aethelScripts/bin/aix-dashboard state --json > /tmp/aix-dashboard.json
```

Ein Engineering-Input wird direkt aus der bestehenden AIX-Akte ausgewählt;
POM v1 und v2 werden als Quellenangaben unterschieden. Diese Ansicht prüft weder
POM-Konformität noch Freigabe oder Produktidentität. Ein konkreter Y-1-Auftrag
oder eine wirksame Produktbindung ist nicht belegt; v2 ist hier nur ein
lesender Vertragspfad, kein nachgewiesener v2-Compiler.

## Grenzen

- Ein Dateidialog öffnet explizit ausgewählte Dateien. Quelle, Autorität und
  Aktualität der Inhalte werden nicht verifiziert. Die Prüfung des nativen
  Dateidialogs war zuletzt nicht vollständig abgeschlossen.
- Es gibt noch keine native Rust-Anbindung, keine automatische Erzeugung eines Projects-Exports oder mBOM, keine Live-Anbindung an Landing, Git oder aethelBrowser und
  keine Schreib-, Auftrags-, Ausführungs- oder Mergefunktion.
- Die historische Momentaufnahme ist kein aktueller Produkt- oder
  Freigabestand. Die Beispiele belegen weder eine gültige Produktidentität
  noch die Wirksamkeit einer Maßnahme.
- Der macOS-Debug-Build ist ein Prototyp, keine unabhängig geprüfte,
  signierte und notarisierte Veröffentlichung.
