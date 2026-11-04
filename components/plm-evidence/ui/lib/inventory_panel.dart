import 'package:flutter/material.dart';

void validateInventory(Map<String, dynamic> data) {
  final scan = data['scan'];
  if (data['schema'] != 'aethel.projects.inventory-live/v1' ||
      !['ok', 'partial', 'error'].contains(data['status']) ||
      (scan != null &&
          (scan is! Map<String, dynamic> ||
              scan['repositories'] is! List ||
              scan['checkouts'] is! List ||
              scan['projects_without_git'] is! List))) {
    throw const FormatException('Ungültiger Inventurstand');
  }
}

class InventoryPanel extends StatefulWidget {
  const InventoryPanel({super.key, required this.data, required this.status});
  final Map<String, dynamic>? data;
  final String status;
  @override
  State<InventoryPanel> createState() => _InventoryPanelState();
}

class _InventoryPanelState extends State<InventoryPanel> {
  String query = '';
  @override
  Widget build(BuildContext context) {
    final data = widget.data;
    final scan = data?['scan'];
    if (data == null || scan is! Map<String, dynamic>) {
      return Center(
        child: Text(
          data == null
              ? 'Inventurdatei über „Auswertung öffnen“ auswählen.'
              : 'Kein gültiger Inventurstand verfügbar.',
        ),
      );
    }
    final attempted = DateTime.tryParse('${data['attempted_at'] ?? ''}');
    final age = attempted == null
        ? null
        : DateTime.now().toUtc().difference(attempted.toUtc());
    final freshness = age == null
        ? 'Aktualität unbekannt'
        : (age.isNegative || age > const Duration(minutes: 30))
        ? 'Inventurstand möglicherweise veraltet'
        : 'Letzter Versuch innerhalb von 30 Minuten';
    final repos = (scan['repositories'] as List)
        .whereType<Map<String, dynamic>>();
    final nonGit = (scan['projects_without_git'] as List)
        .whereType<Map<String, dynamic>>();
    final changes = data['changes'] is Map ? data['changes'] as Map : const {};
    final checkout = (scan['checkouts'] as List)
        .whereType<Map<String, dynamic>>()
        .toList();
    final rows =
        <
          ({String name, String description, String identity, bool candidate})
        >[];
    for (final repo in repos) {
      final identity = '${repo['git_common_dir'] ?? ''}';
      final paths = repo['paths'] is List
          ? (repo['paths'] as List).whereType<String>().toList()
          : <String>[];
      final first = paths.isEmpty ? identity : paths.first;
      final name =
          first.split('/').where((x) => x.isNotEmpty).lastOrNull ?? first;
      final matching = checkout.where((c) => c['git_common_dir'] == identity);
      final states = matching
          .map(
            (c) =>
                '${c['path']} · ${c['branch'] ?? 'Branch unbekannt'} · HEAD ${c['head'] ?? 'unbekannt'} · Änderungen ${c['dirty_files'] ?? 'unbekannt'}',
          )
          .join('\n');
      rows.add((
        name: name,
        description: states.isEmpty ? paths.join('\n') : states,
        identity: identity,
        candidate: false,
      ));
    }
    for (final item in nonGit) {
      final path = '${item['path'] ?? ''}';
      final name =
          path.split('/').where((x) => x.isNotEmpty).lastOrNull ?? path;
      rows.add((
        name: name,
        description: 'Manifest-Kandidat ohne Git: $path',
        identity: path,
        candidate: true,
      ));
    }
    final filtered = rows
        .where(
          (r) => '${r.name} ${r.identity} ${r.description}'
              .toLowerCase()
              .contains(query.toLowerCase()),
        )
        .toList();
    filtered.sort(
      (a, b) => a.name.toLowerCase().compareTo(b.name.toLowerCase()),
    );
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Projekte aus Inventur',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              Text(widget.status),
              if (data['message'] != null) Text('Hinweis: ${data['message']}'),
              Text(
                'Leseprobleme: ${(scan['summary'] is Map ? (scan['summary'] as Map)['checkout_errors'] : null) ?? 'unbekannt'} Git-Orte · ${(scan['summary'] is Map ? (scan['summary'] as Map)['filesystem_errors'] : null) ?? 'unbekannt'} Dateisystemfehler',
              ),
              Text(freshness),
              Text(
                'Erfassung: ${data['attempted_at'] ?? 'unbekannt'} · letzter vollständiger Lauf: ${data['last_success_at'] ?? 'unbekannt'} · Zustand: ${data['status']}',
              ),
              const Text(
                'Lokale Beobachtung, kein Produkt- oder Liefernachweis. Nicht gefundene Einträge sind nicht automatisch gelöscht.',
              ),
              Text(
                'Neu beobachtete Repositorygruppen: ${(changes['new_repositories'] is List ? changes['new_repositories'] as List : []).length} · geänderte Arbeitskopien: ${(changes['changed_checkouts'] is List ? changes['changed_checkouts'] as List : []).length} · neu beobachtete Nicht-Git-Kandidaten: ${(changes['new_non_git_candidates'] is List ? changes['new_non_git_candidates'] as List : []).length}',
              ),
              TextField(
                decoration: const InputDecoration(
                  labelText: 'Projekt oder Pfad suchen',
                ),
                onChanged: (v) => setState(() => query = v.trim()),
              ),
              Text(
                '${filtered.length} Einträge · Repositorygruppen und Kandidaten, keine bestätigte Produktzahl',
              ),
            ],
          ),
        ),
        Expanded(
          child: ListView.builder(
            itemCount: filtered.length,
            itemBuilder: (context, index) {
              final row = filtered[index];
              return ExpansionTile(
                title: Text(row.name),
                subtitle: Text(
                  row.candidate
                      ? 'Nicht-Git-Kandidat · Zuordnung offen'
                      : 'Repositorygruppe · Identität lokal',
                ),
                children: [
                  SelectableText(row.identity),
                  SelectableText(row.description),
                ],
              );
            },
          ),
        ),
      ],
    );
  }
}
