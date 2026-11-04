# Offene Lücken und nächste Nachweise

| Lücke | Erforderlicher nächster Nachweis | Zustand |
|---|---|---|
| Alle Codex-Chats inhaltlich eingearbeitet | Je Session Inhalte, Aufträge, Artefakte und Grenzen, dann Git-/Prüfbelege | Metadaten vollständig für lokalen Host; Inhalte offen |
| Alle Claude-Chats eingearbeitet | Sessionidentität, Haupt-/Nebenläufe, Kompaktierungen, Claude Code und Web getrennt | Dateikandidaten erfasst; Inhalte offen |
| AGY/Grok/MiniMax-Abdeckung | Zugängliche Quellen, Schema, Harness/Provider-Zuordnung, Parser und Rechte | Quellen teilweise gefunden |
| Dauerhafte private Ablage | Zuständigkeit, Zugriff, Retention, Backup und Restore-Test | Offen |
| Vollständiges aktuelles Codeaudit | Branch-/Commitmatrix und Callerprüfung pro kritischer Grenze | Nur gezielte statische Prüfung |
| Abweichender factory.py-SHA-256 | Originalbytes des externen Prüfers gegen Git-Blob vergleichen | Offen |
| Fable-Feedback | Vollständiges Abschlussdokument und zusätzliche Belege | Zusammenfassung und drei PRs abgeglichen; siehe [Fable-Abgleich](FABLE-ABGLEICH.md) |
| Projects-Strukturheuristiken | Produktprofile, Identität und Consumer nach Integration prüfen | Korrekturen in offenem PR #7; nicht auf main übernommen |
| Y-1 installiert und nutzbar | Kandidat, Prüfung, autorisierte Installation, Login und Nutzeraufgabe | Hier nicht neu nachgewiesen |
| Vollständige PLM/Quality-Fähigkeiten | Source-backed Fähigkeitsmatrix und echte Consumer-Belege | Vergleich begonnen |
| Übernahme laufender Claude-Arbeit | Bestehender Auftrag, Owner, Schreibsperre/Prozessstand, gültiger Handoff | Kein automatischer Rollenwechsel |
| Vollständige Investoren-/Rechtslage | Autorisierte Primärdaten, produkt-/marktbezogene Fachprüfung | Nicht durch Architektur erledigt |

Diese Übergabe schließt die Dokumentationsablage, nicht alle genannten Produkt- und Datenlücken. Weitere Reviews können Entscheidungen ändern. Kein globaler Fortschrittsprozentsatz aus Dokumentanzahl.

Die nächste Arbeit sollte zwei getrennte Bahnen haben: private Quellen vollständig erschließen und vorhandene Produktarbeit innerhalb ihrer autorisierten Grenzen weiterführen. Beide werden über gemeinsame Belegreferenzen sichtbar; keine Zwangsabhängigkeit der Produktentwicklung von einer vollständigen historischen Rekonstruktion.

## Erster gemeinsamer Lieferfall: aktuelle Projekte und laufende Arbeit

Nutzerbestätigung: 4. November 2026. Ziel und Koordinationsauftrag sind bestätigt;
Umsetzung und integrierte Abnahme sind noch offen. Y-1 bleibt historischer
Regressionstest; sein Google-/YouTube-Login ist kein Leitfall dieser Lieferung.

### Abnahme

1. Ein neues Projekt im freigegebenen Scanbereich wird ohne erneuten Chatimport
   erkannt. Repository, Arbeitskopie und Produkt werden nicht blind gleichgesetzt.
2. Eine Änderung einer bekannten Arbeitskopie wird automatisch sichtbar. Die
   vereinbarte Aktualisierungsfrist wird vor Abnahme dokumentiert und gemessen.
3. Ein fehlgeschlagener oder unvollständiger Scan löscht keine bekannten Projekte.
   Letzter erfolgreicher Stand, Quellenzeit, Fehler und veraltete Daten sind sichtbar.
4. Ein tatsächlich vorhandener AIX-Auftrag ist an seine Quelle/Revision gebunden
   und zeigt Projektbezug, Owner, Zustand sowie nächsten Schritt oder Blocker.
   Nicht vorhandene Felder sind unbekannt, nicht aus Chattext erfunden.
5. Änderungen zweier getrennt arbeitender Agenten bleiben ihren Kandidaten zugeordnet.
   Die App-Integration hat einen Schreiber und einen identifizierten Integrationskopf.
6. Getestet, unabhängig geprüft, gelandet, gebaut und installiert bleiben getrennte
   Belegarten. Falsche Kandidatenbindung und fehlende Belege erzeugen kein Grün.
7. Copilot und Projects zeigen für denselben Auftrag dieselbe ID und Revision.
   Ausfall der AIX-Quelle lässt eigenständige Projects-Funktionen weiter nutzbar.
8. Der identifizierte App-Build besteht Signatur-/Startprüfung und eine tatsächliche
   Bedienprobe des Datenwegs. Quellcodetests allein genügen hierfür nicht.

### Aufteilung und Lieferreihenfolge

| Schnitt | Bestehende Verantwortung | Nächster überprüfbarer Abschluss |
|---|---|---|
| Inventur und Projects-App | Projects-Integrator, Branch `codex/private-project-chat-ui`; Inventur im vorhandenen Projects-Schnitt | Realen Scan belegen, App integrieren und startbaren Build prüfen |
| AIX-Auftragsquelle und lesender Adapter | Bestehender PLM/AIX-Schnitt, `codex/plm-evidence-p0` und zugehöriger AIX-Zweig | Einen echten Auftrag quellgebunden projizieren; Adapter/Diff an UI-Integrator |
| Gemeinsame Zieldefinition und Abnahme | Beauftragte Gesamtkoordination in dieser vorhandenen Übergabe | Diese Verträge und offene Schnittstellen zusammenhalten |
| Stabilitätsrelease 0.10.1 | Bestehender Release-Integrator | Bestätigten kleinen Umfang bis Installation prüfen |
| Helix/aethelGit | Bestehender Prototyp-Schnitt | Kandidaten-/Rechte-/Runtime-Vertrag getrennt erproben |

Gemeinsame Flutter-Einstiegsdateien hält der Projects-Integrator. Adapter und
AIX-Änderungen bleiben in abgegrenzten Schnitten. Tatsächliche aktuelle Köpfe,
Dateigrenzen und Prozessstände werden in den jeweiligen Implementierungsakten
geführt; diese Tabelle ist keine zweite Lease-Datenbank. Die Gesamtkoordination
ersetzt keine vorhandene Rollen-Lease oder unabhängige Prüfung.

Zuerst Datenquelle und Adapter liefern, dann auf einem identifizierten App-Kopf
zusammenführen, integriert prüfen und den Build bedienen. Die bestehende
unabhängige Prüfung bleibt erhalten. Ein finales Gate folgt dem Review am finalen
Kopf über die vorhandene Ressourcenautorität; Landung nur im vorgesehenen Weg.
0.10.1 bekommt durch diesen Auftrag keine zusätzliche PLM-/Helix-Voraussetzung.

Neue Wünsche werden dem laufenden Lieferumfang oder einem expliziten Folgeschnitt
zugeordnet. Bei Blockaden werden fehlende Fähigkeit/Quelle, zuständiger Owner,
Beleg und Auflösungsbedingung genannt. Unveränderte Blockaden rechtfertigen keine
wiederholten Modellanläufe. Ergebnisberichte nennen Nutzerwirkung, Quellstand,
Prüfbeleg und verbleibende Grenze statt nur Dokument- oder Testanzahlen.
