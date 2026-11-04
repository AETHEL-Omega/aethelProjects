# AETHEL Systemlandschaft und Arbeitsnachweise

Stand: 4. November 2026. Öffentliche, bereinigte Übergabe; Architektur und Steuerung sind Reviewentwürfe, keine behauptete vollständige Implementierung.

## Verbindliche Nutzervorgaben für diese Übergabe

- aethelema entwickelt sich eigenständig weiter. AIX oder ein gemeinsamer Y-1-Durchstich sind keine Voraussetzung für seine bestehenden Standalone-Funktionen.
- Die gesamte Landschaft berücksichtigen; Produkt, Repository, Capability und logische Verantwortung nicht gleichsetzen.
- Alle zugänglichen Codex- und Claude-Chats sollen einzeln eingearbeitet werden. Inventarisierung ist noch keine Inhaltsauswertung.
- Fable- und ChatGPT-Feedback aufnehmen, Unterschiede erhalten und am Code prüfen.
- Nur bereinigte öffentliche Dokumentation veröffentlichen. Private Quellkopien, Chattexte, lokale Pfade und Betriebsdaten nicht in dieses öffentliche Repository übernehmen.

## Bestätigter Integrationsauftrag vom 4. November 2026

Der Nutzer hat die Umsetzung und die Gesamtkoordination beauftragt. Der erste
Lieferfall lautet: **aethelProjects zeigt tatsächliche Projekte und laufende
AIX-Arbeiten automatisch, aktuell und mit belegtem Lieferstatus; Copilot nutzt
dieselben Quellen.** Y-1 ist ein historischer Browser-Prüffall und keine
Voraussetzung dieses Auftrags. Vollständige Chatrekonstruktion bleibt eine
separate Arbeit und blockiert die Projektübersicht nicht.

Die Zieldefinition und Verantwortungsgrenzen stehen in [Architektur](ARCHITEKTUR.md),
die konkrete Abnahme und Aufteilung in [Offene Lücken](OFFENE-LUECKEN.md).
Dieser Dokumentationszweig ist ein überprüfbarer Arbeitsstand, noch kein auf
main geltender Architekturkanon und kein Implementierungsnachweis.

## Einstieg

| Dokument | Zweck | Stand |
|---|---|---|
| [Projektlandschaft](PROJEKTLANDSCHAFT.md) | Begriffe, Verantwortungen, mehrfacher Bezug | Konzeptabgleich, kein Vollaudit |
| [Architektur](ARCHITEKTUR.md) | Eigenständige Produkte und kontrollierte Integration | Reviewentwurf |
| [Datenhaltung](DATENHALTUNG.md) | Zuständige Quellen, Datenschutz, Historie | Teilweise umgesetzt durch diese Ablage |
| [Chatübergreifende Arbeit](ARBEITSNACHWEISE.md) | Alle Sessions, Aufträge, Ergebnisse, Provider | Inventar begonnen; Inhaltsabgleich offen |
| [Fable-Abgleich](FABLE-ABGLEICH.md) | Drei PRs, Beleggrenzen und Entscheidungsvorschläge | PR-Metadaten/Diffs geprüft; nicht gelandet |
| [Konzeptreview](KONZEPTREVIEW.md) | K-01 bis K-08 und eigene Gegenprüfung | Quellengebunden |
| [Werkzeugvergleich](WERKZEUGVERGLEICH.md) | Cursor/Origin, PLM, Polarion, Quality | Begrenzter Primärquellenabgleich |
| [Prüfauftrag](PRUEFAUFTRAG.md) | Unabhängige Prüfung einschließlich Codex | Kopierbarer Auftrag |
| [AIX-Prompt](PROMPT-AIX.md) | Einordnung und Entwicklungsleitlinien | Kein neuer Implementierungsauftrag |
| [aethelema-Prompt](PROMPT-AETHELEMA.md) | Eigenständige Produktentwicklung | Korrigiert frühere Zwangskopplung |
| [Offene Lücken](OFFENE-LUECKEN.md) | Restarbeit und Abnahme | Offen, kein Gesamtgrün |

Alle Dokumente werden im bestehenden `analysen/INDEX.json` registriert. Dieser Ordner ist kein zweites Auftrags- oder Projektregister. Chats und Pages dienen als Hinweise und Lesekopien; dieser versionierte Stand ist der gemeinsame Einstieg für diese Übergabe.

## Herkunft und Veröffentlichungsgrenze

Grundlage sind vorhandene lokale Analyseartefakte, der vom Nutzer gelieferte Konzeptabgleich und gezielte Quellprüfungen. Der Konzeptabgleich wurde als ZIP gelesen; sein SHA-256 ist `0e5659764db395c7f2f18ccabc53edb06aee5fa13339210986f487909fd5a41b`. Die Ursprungsdokumente des Gesamtkonzepts und der AIX-Zielarchitektur wurden in dieser Vertiefung nicht selbst vollständig gelesen. Deren Aussagen bleiben entsprechend zugeschrieben.

Der vollständige private Katalog und die Chat-Metadaten werden hier bewusst nicht kopiert. Das ist eine reduzierte öffentliche Übergabe, kein verlustfreier Export aller internen Daten. Ein dauerhafter privater, zugriffsgesteuerter Ablageort samt Backup/Restore-Nachweis bleibt offen. Die Originale bleiben erhalten.

Basis dieser Dokumentationsarbeit: Projects `d1b42a8cfc5b6717835281985a44e8ce4d6f6991`. Andere Branches und ihre Integration nicht aus dieser Basis ableiten. Der Liefercommit ist über Git zu bestimmen; kein selbstreferenzieller Commit-Hash im Dokument.


## Prüfung dieser Übergabe

- Interne Dokumentlinks, Markdown-Fences, Prüfsummen und Erhaltung aller bisherigen Indexeinträge geprüft.
- Veröffentlichungsprüfung: keine lokalen Benutzerpfade, privaten Chat-IDs, Rohchats oder privaten Quellkopien in den neuen Dokumenten.
- Git-Diff auf Whitespacefehler geprüft.
- Die gezielten bestehenden pytest-Suites konnten nicht starten: pytest fehlt in beiden geprüften vorhandenen Python-Umgebungen. Keine Abhängigkeit installiert; kein bestandener Test behauptet.
- Keine Produktcodeänderung, kein Merge, keine Installation und keine neue Betriebsfreigabe.
