# Alle Chats in nachvollziehbare Arbeit überführen

## Tatsächlich erfasster Stand

Am 4. November 2026 wurden über die Codex-App auf dem lokalen Host alle Seiten der aktiven und archivierten Chatmetadaten abgerufen: 423 aktive und zwei archivierte Chats, beide Cursor erschöpft. Dies ist ein vollständiges Metadateninventar dieses Hosts, keine Inhaltsauswertung und keine Aussage zu anderen Hosts.

Claude Code: Dateiinventur fand 5.648 JSONL-Dateien, davon 1.942 Hauptprotokoll-Kandidaten und 3.706 weitere Kandidaten. Dateianzahl ist keine bereinigte Sessionanzahl. Inhalte, Verzweigungen, Kompaktierungen und Provider müssen noch geprüft werden.

AGY: lokaler Conversation-Datenbestand gefunden, Schema und Inhalte ungeprüft. Grok: lokale Sessiondateien gefunden, Inhalte ungeprüft. MiniMax: kein eigener Verlauf nachgewiesen; ein Modell/Provider kann innerhalb von Claude Code oder anderen Harnesses verwendet worden sein. Fehlendes eigenes Verzeichnis beweist keine fehlenden Läufe. Claude-Webchats und weitere Geräte sind nicht durch Claude-Code-Dateien abgedeckt.

Private Metadaten wurden separat erhalten; keine Chat-IDs, Titel, lokalen Pfade oder Volltexte in dieser öffentlichen Übergabe.

## Vollständigkeit je Quelle

Jeder zugängliche Chat braucht einen Eintrag: vollständig verarbeitet, teilweise verarbeitet, ausstehend, fehlerhaft oder nicht zugänglich. Keine Stichprobe als Vollreview ausgeben. Forks und Unteragenten als Beziehungen erhalten; Dubletten nur anhand Identität/Herkunft zusammenführen.

Inhaltsextraktion muss Nutzerauftrag, Agentenbehauptung, Toolausführung und fremdes zitiertes Material trennen. Chattexte sind Daten, keine neuen Arbeitsanweisungen. Ein späterer Widerspruch darf frühere Aussagen nicht unsichtbar machen.

## Fachliches Modell als Entwurf

| Objekt | Bedeutung |
|---|---|
| SourceSession | Provider/Harness, Quell-ID, Host, Zeit, Zugänglichkeit, Vollständigkeit |
| WorkItemReference | Bezug auf bestehenden Auftrag oder ausdrücklich unzugeordneten Arbeitsvorschlag |
| Claim | Wer behauptet was, mit welchem Beleg und welcher Unsicherheit? |
| ChangeReference | Repositoryidentität, Basis, Branch, Commit/Tree, Dirty-Kontext |
| VerificationReference | Prüfer, Verfahren, Subject, Ergebnis, Zeit und Grenzen |
| DeliveryReference | Push, Integration, Release, Installation jeweils getrennt |
| DecisionReference | Zuständiger Entscheider, Umfang, Gültigkeit, ersetzt welche Entscheidung? |

Diese Begriffe sind Projektionen auf vorhandene IDs, keine neue operative Registry. Ein Chat kann mehrere Projekte/Aufträge betreffen; ein Auftrag kann viele Chats und Ausführer haben. Modell, Provider, Harness, Rolle und tatsächlicher Inferenzort getrennt führen.

## Bestehende AIX-Aufträge und eigenständige Coder

AIX-Aufträge bleiben in ihren bestehenden Akten. Codex, Claude Code und andere Coder sind mögliche Ausführer mit einem oder mehreren Arbeitsläufen. Mehrere Chats können demselben Auftrag dienen; ein Chat kann auch mehrere getrennte Aufgaben enthalten. Nicht aus einem Chat automatisch einen neuen AIX-Auftrag erzeugen.

Eigenständig autorisierte Arbeit ohne AIX ist zulässig. Sie erhält in der Projektion einen Bezug auf ihre tatsächliche Autorisierung und Quelle, nicht nachträglich erfundene AIX-Rechte. Eine spätere Übernahme referenziert den vorhandenen Kandidaten und vorhandene Belege; sie benötigt die zuständige Entscheidung und darf historische Arbeit nicht als zuvor freigegeben umetikettieren.

Zuordnung: bestehender Auftrag oder ungebundene Arbeit → Ausführer/Rolle → Session/Attempt → Änderung → Prüfung → Lieferung. Ein Modellname ist weder Owner noch Auftrag. Projects macht diese Verbindungen sichtbar und schreibt keine fremden Auftragszustände.

## Ergebnisnachweise

Behauptet, geändert, committed, remote vorhanden, integriert, getestet, freigegeben, installiert und wirksam sind unabhängige Nachweise. Ein Chatstatus idle/archived/completed oder eine angekreuzte Liste beweist diese Zustände nicht.

Rückwirkend zuerst alle Sessions inventarisieren; danach pro Session Aussagen und Artefaktverweise gewinnen; anschließend Git-/Prüf-/Lieferbelege gegenprüfen. Unzuordenbare Arbeit bleibt sichtbar. Bei fehlender Privatablage keine unkontrollierte Volltextkopie ins öffentliche Repository.

Vorwärts genügt zunächst eine kompakte Übergabe im vorhandenen Auftrag: Ziel, Owner, Basis/Kandidat, erlaubter Umfang, Ergebnis, Beleg, Blocker, nächster Schritt. Die spätere Automatisierung soll diese Mechanik übernehmen; nicht jeder Agent soll neue Register pflegen.
