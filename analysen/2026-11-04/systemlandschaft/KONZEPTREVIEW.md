# Konzeptabgleich und Gegenprüfung

Der vom Nutzer gelieferte Konzeptabgleich enthält acht Befunde. Seine Implementierungsanweisungen sind Prüfmaterial; sie erteilen diesem Dokument keine neuen Rechte zum Ändern fremder Aufträge oder laufender Writer.

| ID | Inhalt | Eigene Einordnung am 4. November |
|---|---|---|
| K-01 | Begriffe und widersprüchliche Konzeptfassungen | In Landschaft aufgenommen; ursprüngliche Gesamtkonzepte nicht vollständig selbst gelesen |
| K-02 | BOM-Bezeichnungen und hBOM | Terminologie korrigiert; deklarierter Vertrag und operative Durchsetzung getrennt |
| K-03 | Vorhandene Firmen-/Projects-Funktionen | Vorhandene Implementierungen und unterschiedliche Branches anerkannt; keine Betriebsfreigabe |
| K-04 | Übergaben der benannten Produkte | In Architektur konkretisiert; reale Consumer-Nachweise offen |
| K-05 | Zu starke Struktur-/Namensheuristiken | Statische Prüfung am vorhandenen Projects-Blob bestätigt relevante Muster |
| K-06 | Modussemantik | Unterschied benannt; aktueller Policy-Aufrufweg noch zu prüfen |
| K-07 | Verlust von Evidenzfeldern im früheren Review-Anhang | Neuer Paketkatalog mechanisch mit Original verglichen: alle Original-Wurzelfelder einschließlich Inhalte gleich |
| K-08 | Kandidat, Task, Attempt, Effect | Typisierte Referenzen vorgesehen; kein globaler Idempotenznachweis behauptet |

## Eigene Codeprüfung und Abweichung zum Review

Projects-Basis: d1b42a8cfc5b6717835281985a44e8ce4d6f6991. Der geprüfte Firmenleitstand-Commit 4147ef19e6ebd6080c2b27620ef55c556c45aca5 enthält für factory.py denselben Git-Blob 13e2277c9b201b98542a88f24aed03bd6d17652c.

Im Code sichtbar:
- Rollen aus ROLE_PATTERNS/Namensmustern.
- Breites landing-Muster unter „Landing oder Marktmaterial“.
- Aggregation über repo.name.
- end_to_end bei mindestens sechs von acht Stufen.
- Allgemeine Container-/Service-Strukturmerkmale.
- Vorhandene Unterscheidung vorhanden/belegt und Stub-Prüfung; diese Verbesserungen erhalten.

Das ist statische Bestätigung der Logik, keine erneute Ausführung der externen synthetischen Tests und kein vollständiger Workspace-Scorelauf.

**Offene Quellenabweichung:** Der lokal direkt aus dem genannten Git-Commit berechnete SHA-256 der vollständigen factory.py lautet ab27f29879c4ece8e80f1ba093316de3c1eeadfee1d38a1fe1fa8b1d12c62bff. Pruefergebnisse.json des Fremdberichts nennt 5ef58b9823ef5220d1097542a2df70347d6ee51175c806db8ab81126b2105421. Der Git-Blob stimmt überein; die Ursache der unterschiedlichen SHA-256 ist ungeklärt. Mögliche Extraktion/Normalisierung nicht ohne Beleg als Erklärung übernehmen.

Der ergänzte Inventarkatalog bewahrt alle Originalfelder und fügt _concept_review separat hinzu. Diese Prüfung bestätigt Feld-/Inhaltsgleichheit des Snapshots, keine Aktualität oder Vollständigkeit des laufenden Systems.

## Reviewzusammenführung

Fables Zusammenfassung liegt inzwischen vor; der ergänzende [Fable-Abgleich](FABLE-ABGLEICH.md) hält PR-Metadaten, Diffprüfung, zugeschriebene Testergebnisse und weiterhin offene Betriebsnachweise getrennt fest. Neue Befunde erhalten Quellenstand und eigene ID. Übereinstimmung zweier Modelle aus derselben Quelle ist keine unabhängige Bestätigung. Priorität, Erreichbarkeit und Belegsicherheit getrennt behandeln. Historische AIX-Admission-/Owner-Befunde verlangen eine aktuelle Callerprüfung vor einer produktiven Sicherheitsbehauptung.
