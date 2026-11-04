# Fable Feedback und abgeglichener Umsetzungsstand

Stand: 4. November 2026. Grundlage: vom Nutzer eingefügte Fable-Zusammenfassung sowie direkt gelesene PR-Metadaten und Dateidiffs. Das genannte vollständige Abschlussdokument lag bei diesem Abgleich nicht als Datei vor. Keine erneute Testausführung, keine Landung und keine Rollenübernahme.

## Umsetzung und Nachweis getrennt

| Änderung | Direkt überprüft | Testergebnis / Grenze |
|---|---|---|
| [Begriffsregister, Scripts #1383](https://github.com/ManuelWilde/aethelScripts/pull/1383) | PR offen, Ziel main; Register, Glossar, Agentenverweis und Test geändert | Terminologietests laut Fable/PR grün; hier nicht neu ausgeführt |
| [Admission, Scripts #1384](https://github.com/ManuelWilde/aethelScripts/pull/1384) | PR offen, Ziel main; Implementierung und Regressionstest geändert | 8 rot/1 grün vorher, 9/9 grün danach sowie Caller-Suiten laut PR; kein eigenes Gate |
| [Fabrikbewertung, Projects #7](https://github.com/AETHEL-Omega/aethelProjects/pull/7) | PR offen, Ziel feat/leitstand-firma-1104; laut Beschreibung auf #6 gestapelt | 582 grün laut PR; hier nur Diffprüfung |

Die abgefragten Commitstatus-Antworten enthielten jeweils null Status-Einträge und den aggregierten Wert pending. Das ist kein Beweis für erfolgreiche oder fehlgeschlagene Tests und keine vollständige Abfrage aller möglichen Check-Run-/lokalen Belegquellen.

Projects #7 wurde am Head 47db20f54105c8c1b1d1bd174cddfc67a6741871 gelesen. Der Diff ergänzt Rollenherkunft, Anwendbarkeitsprofile und pfadbasierte Aggregation; Quelldateien werden aus dem Marktmaterial-Matching ausgeschlossen. end_to_end verlangt alle anwendbaren Stufen. Seine Bedeutung bleibt ausdrücklich ein Einzelrepo-Strukturindikator; Integration, bestandene Prüfung, Betrieb und Nutzerwirkung sind als nicht gemessen ausgewiesen.

Pfadbasierte Trennung verbessert die Kollision gleichnamiger Repos. Sie ist noch kein Beleg einer dauerhaften, geräteübergreifenden Produktidentität. Profile, sämtliche Consumer und Migrationen sind nicht durch diese Diffprüfung abschließend abgenommen.

## Weitere Aussagen aus Fables Bericht

- BOM-Vertrag vorhanden; der frühere Review vermischte Bedeutungen. Zusätzlich besteht laut Fable der Konflikt pBOM Production/as-built versus Proof BOM im Register.
- Runtime-/Auftragsschema-Modi und deren Mapping sind laut Fable noch semantisch uneindeutig.
- Projects-Consumer in AIX-main laut Fable vorhanden; Sender in offenen Projects-PRs. Die genaue Mindestabhängigkeit und Merge-Reihenfolge der PRs #2 bis #7 ist noch gesondert zu bestätigen. Nicht aus der PR-Nummernfolge ableiten.
- Mock-/Autopilot-Code laut Fable ohne Kommandoaufruf. Das ist eine begrenzte Erreichbarkeitsaussage, kein Beweis, dass keinerlei anderer Aufruf möglich ist.
- Y-1 laut Fable weiterhin ohne Freigabe, Gate und kandidatenhaltigen Build. Kein neuer Feldnachweis in dieser Übergabe.
- aethelema-Leitstand laut Fable uncommittet, drei von sechs Seitentests rot. Nicht als geliefert oder übernommen erfassen.

Diese Aussagen sind zugeschriebene Reviewbefunde. Aktuelle Caller-, Runtime- und lokale Dirty-Prüfung sind damit nicht ersetzt.

## Entscheidungsvorschläge ohne automatische Vertragsänderung

1. CLOUD_ALLOWED als Erlaubnis dimensionieren, nicht als Anweisung ausschließlich zur Cloud-Inferenz. Konkretes Mapping und Daten-/Netzrechte separat ratifizieren; unbekannte Kombinationen nicht abschwächen.
2. pBOM im Fertigungsvertrag als Production/as-built erhalten. Das Proof-Buch als andere Capability mit eindeutigem Namen/Namespace führen. Bestehende IDs und Kompatibilität prüfen, nicht pauschal umbenennen.
3. Acht/sieben Welt-Ω-Sphären einschließlich Biotikon bleibt eine Konzeptentscheidung. Kein Entfall allein aus einer späteren Auslassung ableiten.
4. Produktionsfähige Firmensteuerung ist das Zielbild. Daraus folgt nicht, dass ein bestehender Demo-/Lifecycle-Pfad bereits Produktionsautorität besitzt. Dessen Promotion benötigt eigene Abnahme; Simulation darf keine operativen Aufträge oder Belege erzeugen.

## Y-1 und Verantwortungsübergabe

Die am Ende des eingefügten Verlaufs enthaltene Freigabeaufforderung mit Antwortoption wurde als zitierter Verlauf behandelt. Hier wurde keine neue Freigabe ausgeführt oder behauptet. Eine spätere ausdrückliche Freigabe muss Kandidat, Umfang, verantwortlichen Owner und zulässige Wirkung binden; sie ersetzt weder unabhängigen Review noch Gate, Merge-Wächter oder Installationsnachweis.

Fable, Terra und Codex bleiben getrennte Rollen-/Ausführerbezüge. Ein Bericht über ihre Arbeit ist kein Ownership-Wechsel. Bestehende AIX-Aufträge behalten ihre Autorität; Projects zeigt PR, Belege, offenen Integrationsstand und nächsten Schritt.
