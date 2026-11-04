import 'package:flutter/material.dart';

/// Read-only presentation; no product identity, order or release is created here.
class ProductHome extends StatelessWidget {
  const ProductHome({
    super.key,
    required this.cockpit,
    this.projectsStatus,
    this.onProjectsStop,
    this.aixDashboard,
    this.aixStatus,
    this.aixConnected = false,
    this.onAixConnect,
    this.onAixDisconnect,
    this.factoryInput,
    required this.onOpenY1,
    required this.onLandscape,
  });
  final Map<String, dynamic>? cockpit;
  final String? projectsStatus;
  final VoidCallback? onProjectsStop;
  final Map<String, dynamic>? aixDashboard;
  final String? aixStatus;
  final bool aixConnected;
  final VoidCallback? onAixConnect;
  final VoidCallback? onAixDisconnect;
  final Map<String, dynamic>? factoryInput;
  final VoidCallback onOpenY1;
  final VoidCallback onLandscape;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final tiles =
        (cockpit?['tiles'] is List ? cockpit!['tiles'] as List : const [])
            .whereType<Map<String, dynamic>>()
            .toList();
    final missing = (cockpit?['missing'] is List
        ? cockpit!['missing'] as List
        : const []);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Produkte und Entscheidungen',
          style: theme.textTheme.headlineMedium,
        ),
        const SizedBox(height: 8),
        const Text(
          'Ein Einstieg in Produkt, Firma und Fabrik. Quellen sind datierte Beobachtungen; Entscheidungen und Ausführung bleiben in den zuständigen Systemen.',
        ),
        const SizedBox(height: 16),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'aethelBrowser · Pilot Y-1',
                  style: theme.textTheme.titleLarge,
                ),
                const Text(
                  'Ziel: Google-/YouTube-Anmeldung bis zum sichtbar angemeldeten Zustand.',
                ),
                const SizedBox(height: 8),
                const Text(
                  'Belegter Stand: historische Fallauswertung vom 04.11.2026; Quellen und Autorität nicht verifiziert.',
                ),
                const Text(
                  'Installierter Stand: nicht zugeordnet. Wirkung: nicht nachgewiesen.',
                ),
                const Text(
                  'Nächste Entscheidung: Owner und Produktentscheidung klären; Review, Gate und Feldnachweis am jeweiligen Kandidaten zuordnen.',
                ),
                const Text(
                  'Produktidentität und aktueller Betriebsstand sind nicht aus dieser Fallakte bestätigt.',
                ),
                Wrap(
                  spacing: 8,
                  children: [
                    FilledButton.tonal(
                      onPressed: onOpenY1,
                      child: const Text('Fall Y-1 öffnen'),
                    ),
                    TextButton(
                      onPressed: onLandscape,
                      child: const Text('Projektlandschaft durchsuchen'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        LayoutBuilder(
          builder: (context, constraints) {
            final columns = constraints.maxWidth >= 1000
                ? 3
                : constraints.maxWidth >= 480
                ? 2
                : 1;
            final width = (constraints.maxWidth - (columns - 1) * 12) / columns;
            return Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                SizedBox(
                  width: width,
                  child: _area(
                    context,
                    'Firma',
                    'Produktziel, Markt, Budget und Freigabe',
                    'Für Y-1 sind Entscheidung und zuständiger Owner in dieser Sicht nicht zugeordnet.',
                    'Bestehende Firmen- und Auftragsakte klären.',
                  ),
                ),
                SizedBox(
                  width: width,
                  child: _area(
                    context,
                    'Fabrik',
                    'Auftrag, Arbeitsplan und Prüfplan',
                    'Ein qualifizierter AIX-Auftrag und ein tatsächlicher Lauf sind für Y-1 hier nicht zugeordnet.',
                    'Vorhandenen Auftrag, Rechte und Laufbeleg prüfen.',
                  ),
                ),
                SizedBox(
                  width: width,
                  child: _area(
                    context,
                    'mBOM',
                    'Produktbindung und Fertigungsweg',
                    'Der AIX-Vertrag nennt Spezifikation, Modellreferenzen, Produktionsmodus, Host und Outputvertrag. Eine Y-1-mBOM liegt dieser Sicht nicht vor.',
                    'Konkreten, versionierten Fertigungsauftrag mit Produkt- und Hostbindung auswählen.',
                  ),
                ),
              ],
            );
          },
        ),
        const SizedBox(height: 18),
        Text('AIX-Dashboard', style: theme.textTheme.titleLarge),
        Text(aixStatus ?? 'Nicht verbunden'),
        if (onAixConnect != null)
          TextButton.icon(
            onPressed: aixConnected ? onAixDisconnect : onAixConnect,
            icon: Icon(aixConnected ? Icons.link_off : Icons.link),
            label: Text(
              aixConnected
                  ? 'Automatische Abfrage beenden'
                  : 'AIX lokal verbinden',
            ),
          ),
        const Text(
          'Lokales Dashboard; keine Prüfung der Identität oder Produktzuordnung.',
        ),
        if (aixDashboard != null) ...[
          Text(
            'AIX-Fabrikstand · ausgewählte Quelle',
            style: theme.textTheme.titleLarge,
          ),
          Text(
            'Quelle: ${aixDashboard!['source']} · Zeitpunkt laut AIX: ${aixDashboard!['timestamp']}',
          ),
          Text(
            'Letztes Goal: ${aixDashboard!['goal_id'] ?? 'nicht angegeben'} · Zustand: ${aixDashboard!['state'] ?? 'unbekannt'} · Belegstatus: ${aixDashboard!['proof'] ?? 'unbekannt'}',
          ),
          const Text(
            'Nicht automatisch dem Pilot Y-1 zugeordnet; Quelle und Aktualität nicht unabhängig geprüft.',
          ),
          const SizedBox(height: 16),
        ],
        if (factoryInput != null) ...[
          Text(
            'Ausgewählter Fertigungsvertrag',
            style: theme.textTheme.titleLarge,
          ),
          Text(
            'Quelle: ${factoryInput!['source']} · Eingabe: ${factoryInput!['id']} · Revision: ${factoryInput!['revision'] ?? 'unbekannt'}',
          ),
          Text(
            'POM: ${factoryInput!['pom']} · Auftrag: ${factoryInput!['work_order_id'] ?? 'nicht angegeben'} · Aktivierung laut Quelle: ${factoryInput!['enabled'] ?? 'unbekannt'}',
          ),
          Text(
            'Linie: ${factoryInput!['line'] ?? 'nicht angegeben'} · Station: ${factoryInput!['station'] ?? 'nicht angegeben'}',
          ),
          Text(
            'Produktbindung: ${factoryInput!['product_binding'] ?? 'nicht angegeben'}',
          ),
          Text(
            'Hostbindung: ${factoryInput!['substrate_binding'] ?? 'nicht angegeben'}',
          ),
          Text(
            'Outputvertrag: ${factoryInput!['output_contract'] ?? 'nicht angegeben'}',
          ),
          const Text(
            'Quellangaben; keine Validierung, Freigabe oder Zuordnung zu Y-1. Ein POM v1 ist keine produktgebundene mBOM v2.',
          ),
          const SizedBox(height: 16),
        ],
        Text('Projects-Leitstand', style: theme.textTheme.titleLarge),
        if (projectsStatus != null) Text(projectsStatus!),
        if (onProjectsStop != null)
          TextButton(
            onPressed: onProjectsStop,
            child: const Text('Datei-Neulesen beenden'),
          ),

        Text(
          cockpit == null
              ? 'Keine Leitstandprojektion geladen.'
              : 'Quelle: ${cockpit!['source_id']} · Zeitpunkt und Aktualität nicht unabhängig geprüft.',
        ),
        const Text(
          'Die Kennzahlen sind berichtete Bestandsdaten, keine Produkt- oder Betriebsfreigabe.',
        ),
        for (final t in tiles)
          ListTile(
            dense: true,
            title: Text('${t['titel']} · ${t['wert']}'),
            subtitle: Text(
              'Quelle: ${t['quelle']}${t['hinweis'] == null || t['hinweis'] == '' ? '' : '\n${t['hinweis']}'}',
            ),
          ),
        if (missing.isNotEmpty)
          ExpansionTile(
            title: const Text('Offene Punkte laut Leitstand'),
            children: [
              for (final item in missing)
                ListTile(dense: true, title: Text(item.toString())),
            ],
          ),
      ],
    );
  }

  Widget _area(
    BuildContext context,
    String title,
    String role,
    String state,
    String next,
  ) => Card.outlined(
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: Theme.of(context).textTheme.titleMedium),
          Text(role, style: Theme.of(context).textTheme.labelMedium),
          const SizedBox(height: 8),
          Text(state),
          const SizedBox(height: 8),
          Text('Nächster Schritt: $next'),
        ],
      ),
    ),
  );
}
