# Datenhaltung und bisherige Arbeitsmängel

## Konkret festgestellte Mängel und Korrekturen

| Mangel dieser Arbeit | Korrektur | Grenze |
|---|---|---|
| Ergebnisse nur in Chat, Page und lokalem Artefaktordner | Versionierter Repo-Einstieg und bestehender Analysenindex | Private Originale noch nicht dauerhaft organisiert |
| Abweichende Prompts ohne Gültigkeitsregel | Standalone-Vorgabe explizit; korrigierte Promptdateien | Alte Chats bleiben historische Quellen |
| Vermischung von Plan, Dateifund und Erfolg | Getrennte Status-/Belegdimensionen | Noch nicht überall in Produktcode umgesetzt |
| Privates Prüfpaket für öffentliches Ziel vorbereitet | Vom Nutzer genehmigte bereinigte Veröffentlichung | Rohdaten bewusst ausgeschlossen |
| Review akzeptiert Quellenhash ohne Gegenprüfung | Paket-/Blob-/Dateihash getrennt prüfen | Festgestellte Hashdifferenz bleibt offen |
| Chatabschluss als möglicher Arbeitsabschluss | Sessions, Aufträge und Ergebnisse getrennt modellieren | Inhaltsprüfung aller Chats noch ausstehend |

## Zuständige Quellen statt eines allmächtigen Speichers

- Code und versionierte Produktdokumentation: zuständiges Repository.
- Aufträge, Mandate, Besitz und autorisierte Übergänge: bestehende operative Autoritäten.
- Originalchats: jeweiliger Provider beziehungsweise zugelassener Export; private Inhalte bleiben privat.
- Arbeitsbeobachtungen: quellengebundene, wiederaufbaubare Projects-Projektion, keine zweite Auftragsverwaltung.
- Öffentliche Analysen: diese Ablage und bestehender INDEX.json mit SHA-256.
- Test-, Build-, Installations- und Betriebsbelege: zuständiger Produzent; Projektionen referenzieren Subject, Revision, Zeitpunkt und Zugriffsklasse.
- Geheimnisse: vorhandene Secret-Verwaltung, niemals Chat-/Portfolioindex.

Private Daten brauchen vor dauerhafter Übernahme einen bestätigten Ablageort, Zugriffsmodell, Aufbewahrung, Löschverfahren, Backup und Wiederherstellungstest. Diese Entscheidung ist noch offen. Ein weiterer temporärer Ordner oder ein privater Unterordner im öffentlichen Git-Repository ist keine Lösung.

## Historisierung und Datenqualität

Originalfelder erhalten; Ergänzungen getrennt führen. Projektionen dürfen reduziert sein, müssen Verluste aber benennen. Speicherung beweist weder Wahrheit noch Aktualität. Ereigniszeit und Erfassungszeit getrennt, Parser-/Vertragsversion, Quellenrevision und Fehler festhalten.

Änderungen oder Löschung der Quelle invalidieren betroffene Sichten; Fehler werden nicht als leere Ergebnisse gespeichert. Wiederaufnahme über stabile Quell-IDs und Cursor, idempotente Verarbeitung und nachvollziehbare Korrekturen. Cache ist rekonstruierbar; eine neue Abfrage macht alte Belege nicht frisch.

Ein gewünschtes Datenmodell ist noch keine implementierte Datenplattform. Bestehende Projects-Module für Inventar, Kontinuität, Dossiers und Analysen zuerst erweitern, statt einen neuen Wissenskern anzulegen.
