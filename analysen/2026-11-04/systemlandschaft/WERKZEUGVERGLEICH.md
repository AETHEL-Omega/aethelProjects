# Fähigkeitsvergleich statt naiver Gleichsetzung

Stand: 4. November 2026. Begrenzter Abgleich offizieller Quellen, kein vollständiges Featureaudit oder Kaufentscheid. AETHEL-Zuordnungen sind Prüfaufgaben, keine bereits implementierten Fähigkeiten.

| Bereich | Zu prüfende Fähigkeit in AETHEL | Abnahmebeispiel |
|---|---|---|
| Agentenarbeit | Kontext, Planung, Werkzeuge, Review, Regeln, Skills, MCP, CLI, kontrollierte Automation | Ein Auftrag bleibt bei Harnesswechsel verständlich und prüfbar |
| Versionsverwaltung | Repository-/Branchrechte, Review, Spiegelzustand, Herkunft | Autoritative Quelle und Spiegel widersprechen sich nicht unbemerkt |
| ALM | Anforderungen, Tests, Änderungen, Baselines, Varianten, Traceability | Änderung markiert betroffene Nachweise als neu zu prüfen |
| Produktkonfiguration | eBOM/mBOM, Varianten und Gültigkeit | Geliefertes Produkt ist einer freigegebenen Konfiguration zugeordnet |
| Qualitätsplanung | Risiken, FMEA, Prüf- und Reaktionsplan | Risiko führt zu konkreter Prüfung und Reaktion |
| Qualitätsproblem | Abweichung, Sofortmaßnahme, Ursache, Korrektur, Wirksamkeit | Geschlossenes Ticket benötigt nachgewiesene Wirksamkeit |
| Lieferanten/Abhängigkeiten | Herkunft, Qualität, Lizenzen und Änderungen | Geänderte Komponente löst betroffene Neubewertung aus |
| Audit | Verantwortliche, Änderungen, Nachweise, offene Feststellungen | Entscheidung und historische Grundlage rekonstruierbar |
| Betrieb | Installationsbezug, Incident, Support, Rücknahme | Fehler eines konkreten Releases in nächste Entscheidung zurückgeführt |
| Forschungsprodukt | Hypothese, Baseline, Gegenbeispiel, Geltungsbereich | Enger Erfolg wird nicht zu allgemeiner Fähigkeit hochgestuft |

Die Cursor-Dokumentation führt unter anderem Planung, Review, Anpassung über Rules/Skills/MCP sowie Cloud- und CLI-Wege auf. Das Vorhandensein einer Rubrik ersetzt keine Prüfung ihrer Grenzen oder Übertragbarkeit. [Cursor-Dokumentation](https://cursor.com/docs)

**Origin ist laut aktuell gelesener Primärquelle eine Git-Forge in früher Beta.** Sie unterstützt Git-Operationen, PRs und GitHub-Spiegelung. Bei gespiegelten Repositories bleibt GitHub autoritativ; bei Origin-gehosteten ist es Origin. Das belegt weder Git-freie Speicherung noch eine AETHEL-Integration. Die frühere Unbestätigt-Aussage des Reviews wird dadurch für diese konkrete Frage präzisiert. [Origin](https://cursor.com/docs/origin)

Polarion beschreibt Anforderungen, Workflows, Rechte, Versionshistorie und Rückverfolgbarkeit; der Validierungsbeitrag ergänzt Baselines/Collections und Verknüpfung zu Testläufen. Für AETHEL müssen diese Übergänge am eigenen Modell geprüft werden, statt Dateivollständigkeit als ALM auszugeben. [Requirements](https://www.siemens.com/en-us/products/polarion/requirements/), [Validierung](https://blogs.sw.siemens.com/polarion/accelerate-and-scale-early-validation-with-polarion/)

Teamcenter Quality verbindet Qualitätsplanung, Beschwerden/Abweichungen und Problemlösung mit Änderungen und Fertigungsrückmeldung. Die dokumentierten Funktionen umfassen insbesondere FMEA, Prüfplanung und Maßnahmen. Der Releasebeitrag 2606 beschreibt auch Abgleiche von FMEA-Strukturen mit BOM/BOP sowie KI-Vorschläge zur Prüfung vor Übernahme. Daraus folgt keine automatische Normkonformität von AETHEL. [Quality](https://www.siemens.com/en-us/products/teamcenter/solutions/quality-compliance-management/), [2606](https://blogs.sw.siemens.com/teamcenter/whats-new-teamcenter-quality-2606/)

## Noch nicht ausreichend abgeglichen

Komplette Editions-/Versionsmatrix, Berechtigungsdetails, Offline-/Exportfähigkeit, Integrationsgrenzen, Kosten, Sicherheitsmodell und jede einzelne Cursor-/PLM-Funktion sind offen. Ebenso fehlt die umfassende Zuordnung zu aktuellen AETHEL-Consumern. Kein allgemeines Feature-Paritätsversprechen.

Die nächste Matrix benötigt pro Fähigkeit: Bedarf/Nutzerfall, Quelle/Version, vorhandene AETHEL-Komponente, Implementierungs-/Betriebsbeleg, Lücke, Anwendbarkeit, Owner und nächster Negativtest. Nur relevante Fähigkeiten übernehmen; keine parallele Nachbildung kompletter Werkzeugplattformen.
