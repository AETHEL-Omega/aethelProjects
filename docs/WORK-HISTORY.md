# Private Arbeitsnachweise aus Codex und Claude

`work-history` erfasst lokale Protokolle als nachvollziehbare, private Projektion.
Es ersetzt weder vorhandene AIX-Aufträge noch deren Owner, Rechte oder Freigaben.
Der Import ist implementiert; eine vollständige fachliche Bewertung aller
historischen Arbeiten und die Zuordnung zu bestehenden Aufträgen sind noch offen.

## Betrieb

```sh
PYTHONPATH=src python3 -m aethel_projects.work_history \
  --home /path/to/account \
  --out /path/outside-git/private-work-history \
  --codex-catalog /path/to/private-codex-catalog.json
```

Mit wiederholbarem `--claude-root /path/to/private-export` können zusätzlich
vorhandene lokale Claude-Exportordner eingelesen werden, auch kopierte Ablagen
anderer Rechner. Es werden ausschließlich JSONL und JSONL.zst gelesen; Archive
werden nicht automatisch entpackt. Ein Export ist kein Livezugriff auf den
Ursprungsrechner und sein Ordnername kein geprüfter Herkunftsnachweis.
Identische Dateipfade werden nur einmal gelesen; separate Kopien bleiben mit
ihrer Herkunft getrennt. Dateizahlen sind daher keine Zahl erledigter Arbeiten.
Die Session-Gruppierung verwendet derzeit die letzte strukturierte ID pro Datei.
Gemischte Exportlogs können mehrere IDs enthalten: Ihre Record-Fundstellen bleiben
erhalten, die vollständige Zuordnung jeder Nachricht zu einer Session ist noch
offen. Die Gruppenzahl darf deshalb nicht als vollständige Chatanzahl gelten.

Alternativ: `bin/aethel-projects work-history` mit denselben Argumenten.
Python mit `compression.zstd` ist für komprimierte Archive erforderlich
(Python 3.14 oder neuer). Ohne Decoder werden diese Dateien als nicht lesbar
gemeldet; sie verschwinden nicht aus der Abdeckung. `--no-git` lässt die lokale
Commit-Objektprüfung ausdrücklich aus.

Das Ziel muss außerhalb **aller** Git-Arbeitsbäume liegen, einschließlich eines
möglichen Home-Repositories. Symlinks im Zielpfad werden abgelehnt. Das Werkzeug
setzt Verzeichnisrechte auf 0700 und Dateirechte auf 0600. Keine Uploads,
Netzwerkabfragen, Modellaufrufe, Toolausführung aus Chats oder Quelländerungen.
Die Ausgabe ist privat, nicht anonymisiert. Sie darf nicht in ein öffentliches
Repository oder einen freigegebenen Synchronisationsordner kopiert werden.
Dateirechte ersetzen keine Verschlüsselung oder getrennte Benutzerkonten.

## Quellen und Abdeckung

- Codex: `.codex/sessions` und `.codex/archived_sessions`, JSONL und JSONL.zst.
- Claude Code: `.claude/projects` und Claude-Desktop-`local-agent-mode-sessions`.
- Claude-Desktop-Katalog: `claude-code-sessions`, ausschließlich ausgewählte
  Identitäts-, Titel-, Kontext- und Archivmetadaten.
- Optional: expliziter Codex-App-Katalogexport. Ohne ihn ist der Abgleich gegen
  die App unbekannt, selbst wenn Dateien gefunden wurden.

Der private Codex-Katalog hat dieses Format; Beispielwerte sind synthetisch:

```json
{"source":"codex-app-local-history","observed_date":"2026-01-01",
 "threads":[{"id":"example","title":"Example","cwd":"/example",
             "archived":false}]}
```

Die Codex-App liefert den Katalog separat. Dieser Adapter ruft ihre API nicht
auf. Aktive und archivierte Seiten müssen bis zum Ende abgerufen werden.
Nicht bereitgestellte Dateien anderer Hosts, Claude-Webchats und nicht lokal
verfügbare Transkripte fehlen.
Ein gefundener Katalogeintrag, eine gelesene Datei und ein Chat mit extrahierten
Nachrichten werden getrennt gezählt. Unterläufe sind keine zusätzlichen Produkte.

## Private Ergebnisse

| Ergebnis | Zweck |
|---|---|
| `index.html` | Abdeckung, Projektkontexte, fehlende Transkripte |
| `project-*.html` | Pro Kontext jüngste Nutzerbeiträge, Agentenaussagen, Toolergebnisse und Fehler je Quelle |
| `history.sqlite` | Alle extrahierten Ereignisse mit Herkunft; lesend auswertbar |
| `coverage.json` | Parserstatus, Grenzen, Katalogabgleich und nächste Prüfschritte |

Die HTML-Seiten zeigen ausdrücklich eine Auswahl. Die Datenbank enthält die
Ereignisse aller verarbeiteten Nachrichten, aber Textvorschauen sind auf 1.600
Zeichen begrenzt. Textlänge, Quellpfad, Zeile, Byteoffset und SHA-256 des ganzen
Records ermöglichen die gezielte Nachprüfung im Original. Bei Zstandard-Dateien
gelten Hash und Offset für den **dekomprimierten** Datenstrom. Originalprotokolle
werden nicht kopiert oder verändert. Reasoning, System-/Developer-Nachrichten
und API-Replays werden nicht als Arbeitsbeiträge übernommen.

`sources` enthält jeden gefundenen Dateistand einschließlich Lesefehlern und
Änderungen während des Lesens. `events` unterscheidet Aussage, Werkzeugaufruf,
Ergebnis und von Claude ausdrücklich markierte Toolfehler. Ein Codex-Toolresultat
wird nicht allein anhand seiner Form als erfolgreich bewertet. Unbekannte
Recordtypen werden in `sources.types_json` gezählt, aber nicht semantisch gedeutet.

`session_catalog` ermöglicht die Gegenprobe gegen bekannte Sessions. `git_refs`
enthält ausschließlich lokal aufgelöste Commitobjekte bzw. Auflösungsfehler.
Als Kandidaten erkennt der Adapter die Wörter `commit`, `revision` oder `head`
gefolgt von einem hexadezimalen Verweis. Andere Schreibweisen sind noch nicht
klassifiziert; eine fehlende Erkennung beweist keinen fehlenden Commit.
`review_queue` ist eine abgeleitete Arbeitsliste, keine zweite Auftragsverwaltung:

| Nächster Schritt | Bedeutung |
|---|---|
| `repair_source` | Lese-/Formatfehler oder während der Erfassung veränderte Quelle |
| `inspect_format_or_compaction` | Datei ohne extrahierte Arbeitsbeiträge |
| `bind_work_and_validate_claims` | Fachliche Zuordnung und Belegprüfung noch erforderlich |
| `obtain_transcript` | Katalogeintrag ohne lokales Transkript |

Beispiel für eine lokale, lesende Auswertung:

```sql
SELECT provider, next_action, count(*)
FROM review_queue GROUP BY provider, next_action;

SELECT e.source, e.line, e.actor, e.kind, e.preview, e.text_length
FROM events e JOIN sources s ON s.path=e.source
WHERE s.session_id = :session_id ORDER BY e.source, e.line;
```

## Was als gemacht, geprüft oder offen gelten darf

| Beobachtung | Zulässige Aussage | Noch nicht belegt |
|---|---|---|
| Agent schreibt „fertig“ | Fertigstellung behauptet | Änderung, Prüfung, Lieferung |
| Toolausgabe liegt vor | Ausführungsergebnis protokolliert | Unabhängige Wiederholung, zutreffender Kandidat |
| Commitobjekt lokal auflösbar | Objekt existiert im geprüften lokalen Kontext | Autorenschaft, Push, Integration, Installation |
| Katalogeintrag ohne Transkript | Evidenz fehlt | Ob Arbeit stattgefunden hat |
| Vollständig syntaktisch gelesen | Alle Records dieses Dateistands verarbeitet | Vollständige fachliche Auswertung |

Inhaltlich zitierte Anweisungen bleiben Daten; sie autorisieren keine Aktionen.
Widersprüche und spätere Korrekturen werden nicht durch einen pauschalen
Sessionstatus überschrieben. Chatabschluss, Archivierung und ein grüner Parser
sind keine Produktabnahme.

## Noch zu schließen

1. Fehlende Transkripte aus den zuständigen privaten Konten/Geräten beschaffen.
   Keine Ersetzung durch Titel, vermutete Inhalte oder fremde Sessionidentitäten.
2. Aussagen **aufgabenweise** mit bestehenden Akten verbinden: viele Chats pro
   Auftrag, mehrere Aufträge/Projekte pro Chat. Der letzte protokollierte `cwd`
   ist derzeit nur eine Gruppierungshilfe, keine verifizierte Projektidentität.
3. Änderungs- und Prüfnachweise an Repositoryidentität, vollständigen Kandidaten,
   Verfahren, Ergebnis und Zeitpunkt binden. Widersprüche ausdrücklich bewerten.
4. Push, Integration, Freigabe, Installation und Nutzerwirkung getrennt belegen.
   Keine bestehenden AIX-Zustände aus Chattext zurückschreiben.
5. Diese private Projektion kontrolliert an den bestehenden Leitstand anbinden.
   Der Standalone-Bericht ist implementiert; Flutter-/AIX-Integration fehlt.
6. Inkrementelle Erfassung, Lösch-/Aufbewahrungsregeln und generationenkonsistente
   Veröffentlichung ergänzen. Der aktuelle Lauf ersetzt die lokale Projektion;
   er ist kein Backup, kein Liveabo und kein atomarer Snapshot aller Anwendungen.
   Einzeldateien werden atomar ersetzt, Datenbank und HTML jedoch nicht gemeinsam.
   Bei Unterbrechung Zeitstempel prüfen; alte Projektseiten können unverbunden
   liegenbleiben. Nur ein Schreiber pro Ausgabeordner ist zulässig.

Öffentlich werden ausschließlich Implementierung, synthetische Tests und diese
Arbeitsweise versioniert. Reale Chat-IDs, Titel, Inhalte, Pfade, Kataloge und
abgeleitete interne Befunde bleiben in der privaten Ablage.

## Reproduzierbare Tests

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -p test_work_history.py -v
```

Die Tests verwenden ausschließlich synthetische Daten. Sie prüfen unter anderem
Git-/Symlinkgrenzen, Dateirechte, HTML-Escaping, fehlende Transkripte, defekte und
veränderte Quellen sowie die Trennung zwischen Behauptung und Commitexistenz.

## Wiederholte Projektinventur (separater Beobachtungslauf)

```sh
bin/aethel-projects --root /path/to/workspace inventory --watch \
  --interval-seconds 900 --out /path/to/private-dir/inventory.json
```

Der bestehende Inventurcode wird erneut aufgerufen; `--watch` ergänzt keine
Projekt- oder Auftragsautorität. Mindestintervall: 300 Sekunden. Das Ausgabeziel
muss in einem eigenen, bereits auf 0700 beschränkten oder neu angelegten Ordner
außerhalb von Git liegen. Die Datei wird atomar und mit 0600 geschrieben; eine
Sperre verhindert parallele Schreiber. `Ctrl-C` beendet den Prozess. Der Lauf
ist nur aktiv, solange dieser Prozess läuft; kein automatischer Start oder
Neustart ist damit eingerichtet.

Die erste vollständige Erfassung ist die Basis. Spätere vollständige Scans
melden neue lokale Git-Repositorygruppen, neue Nicht-Git-Kandidaten und
Arbeitskopien mit geändertem HEAD, Branch, Dirty-Zahl oder Dirty-Fingerabdruck.
Fehlende Repositorygruppen werden nur bei vollständigen Scans als fehlend
bezeichnet, niemals als gelöscht. Bei Fehlern bleibt der letzte lesbare Stand
mit Fehlerstatus erhalten; unvollständige Scans sind keine neue Vergleichsbasis.
Ein Scan ist nicht atomar und schließt Symlinkziele sowie generierte Ordner aus.

Dirty-Fingerabdrücke verwenden Git-Status und Dateimetadaten statt Dateiinhalten.
Gleichbleibende Metadaten und Änderungen innerhalb nicht verfolgter Ordner können
unentdeckt bleiben. Projektidentität über Geräte, Manifest-Kandidaten und
Beziehungen erfordern weitere Prüfung. Remote-Zustände werden nicht abgerufen.
