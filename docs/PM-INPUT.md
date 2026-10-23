# Projektdossiers als Input für aethelProjectManagement

Status: implementierter Export, vorgeschlagener Consumer-Vertrag; kein laufender
PM-Import nachgewiesen. Auftrag Manuel, 23.10.2026: aethelProjects soll Forensik,
Intent und Architektur abbilden und wertvollen Input für Projektmanagement liefern.

`inventory` beantwortet, welche Verzeichnisse, Historien, Checkouts und
Projektkandidaten vorliegen. `scan` liefert Git-Metriken und regelbasierte Befunde.
`dossier --snapshot <scan.json>` erzeugt `aethel.projects.pm-input/v1`.

Jedes Dossier enthält:

- `repository_id`: lokales gemeinsames Git-Verzeichnis, niemals nur Projektname.
  Das ist eine lokale Repository-Identität, keine globale Produkt-ID. Mehrere
  Klone desselben Produkts müssen im bestehenden Register zugeordnet werden.
- `intent.declared`: erkannter Zweck mit Quelle und Konfidenz;
  `intent.implemented` bleibt `not_verified`.
- `architecture`: bekannte Architekturdokumente mit SHA-256, Überschriften und
  begrenztem Quellenauszug. `runtime_conformance` bleibt `not_verified`.
- `documents`, `manifests`: lokale Belege; übergroße, unlesbare und außerhalb des
  Projekts liegende verlinkte Dokumente werden explizit ausgewiesen.
- `relationships.declared_local_dependencies`: direkte Pfadabhängigkeiten der
  obersten Cargo.toml, einschließlich Existenzprüfung. Kein vollständiger Graph,
  keine Auflösung von Versionspaketen, kein Beweis tatsächlicher Nutzung.
- `forensics`, `findings`: lokale Git-Beobachtungen aus dem datierten Snapshot.
- `questions_for_project_management`: belegte Klärungsbedarfe, keine ausführbaren
  Aufträge und keine automatisch beschlossenen Prioritäten.

`scan_generated_at` datiert die Git-Metriken; `generated_at` datiert den Export.
Dokumente und `observed_head` werden beim Export gelesen. Das ist kein atomarer
Snapshot und kein Siegel. SHA-256 bindet den gelesenen Text, nicht dessen Wahrheit.
Fehlende, veraltete und nur behauptete Eigenschaften dürfen beim Import nicht
zu „fertig“ werden. README, Tests-Ordner und CI-Datei sind keine Produktabnahme.

Der künftige PM-Consumer ordnet Repository und Produkt anhand der bestehenden
Projektregistrierung zu. Er nutzt die Fragen für manuell/vertraglich priorisierte
Arbeitsvorbereitung. Erst die vorhandene AIX-Auftragsakte gibt Rechte, Rolle,
Dateiumfang, Budget, Orakel und Besitzbindung vor. Keine zweite Rollendatenbank,
kein zweiter Executor, keine Auto-Merges oder GitHub-Workflow-Auslösung.

Nächste Erweiterung innerhalb dieses Vertrags: belegte Komponenten und
Schnittstellen, Abweichungen zwischen Architektur und Code, tatsächliche lokale
Abhängigkeiten von Dart/Node/Python sowie Test-/Release-Receipts. Der vorhandene
CodeAnalyzer ist vor einer neuen Analyse-Engine zu integrieren. Semantische
Bewertungen brauchen einen zugelassenen Harness und ein gebundenes Budget.

## Anschluss an den vorhandenen AIX-Eingang

```bash
bin/aethel-projects aix-input --input auftrag-entwurf.json \
  --dossiers pm-input.json --out auftrag-mit-projektbelegen.json
```

`auftrag-entwurf.json` muss der vorhandene rohe `aix.engineering_input.v1` mit
explizitem `project.path` sein. Das Werkzeug fügt nur
`context.project_evidence` hinzu. Es erzeugt weder Auftrag noch Freigabe;
Scope, Modus, Rollen, Budget, Ziel und Orakel bleiben unverändert. Bereits
freigegebene/gesiegelte oder kompilierte Eingänge werden abgelehnt. Ein
vorhandener gleichnamiger Kontextblock wird nicht still überschrieben.

Vor der Bindung prüft der Adapter genau einen Dossiereintrag für diesen Pfad,
das gemeinsame Git-Verzeichnis, den aktuellen HEAD und die Dokument-Hashes.
Scan und Export dürfen standardmäßig höchstens eine Stunde alt sein;
Zeitangaben ohne Zeitzone, aus der Zukunft oder Quellen außerhalb des Projekts
blockieren. Ein anderer Commit oder geänderter Quellentext verlangt einen
neuen Export. Git-Metriken bleiben datierte Beobachtungen aus dem Scan.

Der Output geht anschließend unverändert in die vorhandene AIX-Compilation:
`aix-copilot package --file auftrag-mit-projektbelegen.json --output arbeitspaket.json`.
Die bestehende Normalisierung und Arbeitspaket-Compilation erhalten `context`;
der ergänzte Inhalt geht in den neuen Proposal-/Source-Digest ein. AIX prüft
weiter die gesamte Eingabe und die aktuelle Rolle/Lease. Dieser Export selbst
führt die Compilation nicht aus. Eine vorherige Freigabe gilt dafür nicht.

Projekttexte bleiben nicht vertrauenswürdige Beobachtungen. Ein Hash belegt
Integrität des gelesenen Inhalts, keine Autorität und keine Produktfunktion.
Der Lauf durch Messenger, Rollenwechsel, Ausführung und Forge ist getrennt
abzunehmen; die lokalen Adaptertests behaupten keinen Live-Durchstich.
