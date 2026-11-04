import 'dart:io';
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
  const InventoryPanel({
    super.key,
    required this.data,
    required this.status,
    this.onChooseSource,
    this.orders,
    this.orderStatus = 'AIX-Auftragsquelle nicht verbunden',
    this.onConnectOrders,
    this.analyses = const {},
    this.analysisStatus = '',
    this.analysisRunning = false,
    this.onAnalyze,
  });
  final Map<String, dynamic>? data;
  final String status;
  final VoidCallback? onChooseSource;
  final Map<String, dynamic>? orders;
  final String orderStatus;
  final VoidCallback? onConnectOrders;
  final Map<String, Map<String, dynamic>> analyses;
  final String analysisStatus;
  final bool analysisRunning;
  final void Function(String, String)? onAnalyze;
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
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Projekte anzeigen'),
            Text(widget.status),
            const Text(
              'Inventurordner einmalig auswählen; vorhandene Quelle wird beim nächsten Start wieder geöffnet.',
            ),
            if (widget.onChooseSource != null)
              FilledButton.tonal(
                onPressed: widget.onChooseSource,
                child: const Text('Inventurordner auswählen'),
              ),
          ],
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
          ({
            String name,
            String description,
            String identity,
            bool candidate,
            Map<String, dynamic>? observation,
            Map<String, dynamic>? analyzer,
            Map<String, dynamic>? readme,
            String recent,
            List<String> paths,
          })
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
        paths: paths,
        observation: repo['direct_observation'] is Map<String, dynamic>
            ? repo['direct_observation'] as Map<String, dynamic>
            : null,
        recent:
            matching
                .map((c) => c['last_commit'])
                .whereType<String>()
                .firstOrNull ??
            '',
        readme: repo['readme_purpose'] is Map<String, dynamic>
            ? repo['readme_purpose'] as Map<String, dynamic>
            : null,
        analyzer:
            widget.analyses[identity] ??
            (repo['analyzer_observation'] is Map<String, dynamic>
                ? repo['analyzer_observation'] as Map<String, dynamic>
                : null),
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
        observation: null,
        analyzer: null,
        readme: null,
        recent: '',
        paths: [path],
      ));
    }
    final filtered = rows
        .where(
          (r) => '${r.name} ${r.identity} ${r.description}'
              .toLowerCase()
              .contains(query.toLowerCase()),
        )
        .toList();
    filtered.sort((a, b) {
      final needle = query.toLowerCase();
      int rank(String name) {
        final value = name.toLowerCase();
        if (needle.isEmpty) return 0;
        if (value == needle) return 0;
        if (value.startsWith(needle)) return 1;
        if (value.contains(needle)) return 2;
        return 3;
      }
      final byRank = rank(a.name).compareTo(rank(b.name));
      return byRank != 0 ? byRank : a.name.toLowerCase().compareTo(b.name.toLowerCase());
    });
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
              Text('${filtered.length} Einträge · $freshness'),
              if (widget.onChooseSource != null)
                TextButton(
                  onPressed: widget.onChooseSource,
                  child: const Text('Inventurordner ändern'),
                ),
              ExpansionTile(
                title: const Text('Quelle und Erfassungsdetails'),
                children: [
                  Text(widget.status),
                  if (data['message'] != null)
                    Text('Hinweis: ${data['message']}'),
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
                ],
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
              String? realPath(String path) {
                try {
                  return Directory(path).resolveSymbolicLinksSync();
                } on FileSystemException {
                  return null;
                }
              }

              final paths = row.paths.map(realPath).whereType<String>().toSet();
              final orders =
                  (widget.orders?['auftraege'] is List
                          ? widget.orders!['auftraege'] as List
                          : const [])
                      .whereType<Map>()
                      .where((order) {
                        final project = order['projekt'];
                        if (row.candidate ||
                            project is! String ||
                            order['lesestatus'] != 'gebunden') {
                          return false;
                        }
                        final resolved = realPath(project);
                        if (resolved == null || !paths.contains(resolved)) {
                          return false;
                        }
                        return rows
                                .where(
                                  (candidate) => candidate.paths
                                      .map(realPath)
                                      .contains(resolved),
                                )
                                .length ==
                            1;
                      })
                      .toList();
              return ExpansionTile(
                title: Text(row.name),
                subtitle: Text(
                  row.observation?['state'] == 'source_bytes_match' &&
                          row.observation?['purpose'] is String
                      ? '${row.observation!['purpose']}'
                      : row.readme?['text'] is String
                      ? 'Laut README: ${row.readme!['text']}'
                      : row.candidate
                      ? 'Nicht-Git-Kandidat · Zuordnung offen'
                      : 'Repositorygruppe · Zweck noch nicht geprüft',
                ),
                children: [
                  if (row.observation?['state'] == 'source_bytes_match') ...[
                    ListTile(
                      title: const Text('Was ist bekannt?'),
                      subtitle: Text(
                        '${row.observation!['finding'] ?? 'Nicht angegeben'}',
                      ),
                    ),
                    ListTile(
                      title: const Text('Nächster Schritt'),
                      subtitle: Text(
                        '${row.observation!['next_step'] ?? 'Nicht angegeben'}',
                      ),
                    ),
                    const Text(
                      'Quellenbericht, keine Freigabe oder Betriebsbestätigung.',
                    ),
                  ] else if (row.observation != null)
                    const Text(
                      'Frühere Quellenbeobachtung ist veraltet oder nicht verifiziert.',
                    ),
                  if (row.recent.isNotEmpty)
                    ListTile(
                      title: const Text('Letzter Commit der Arbeitskopie'),
                      subtitle: Text(row.recent),
                    ),
                  if (!row.candidate &&
                      row.paths.isNotEmpty &&
                      widget.onAnalyze != null)
                    if (row.paths.length == 1)
                      ListTile(
                        title: const Text('CodeAnalyzer'),
                        subtitle: Text(
                          widget.analysisStatus.isEmpty
                              ? 'Diese Arbeitskopie begrenzt analysieren.'
                              : widget.analysisStatus,
                        ),
                        trailing: FilledButton.tonal(
                          onPressed: widget.analysisRunning
                              ? null
                              : () => widget.onAnalyze!(
                                  row.identity,
                                  row.paths.first,
                                ),
                          child: const Text('Projekt analysieren'),
                        ),
                      )
                    else
                      ExpansionTile(
                        title: const Text('Arbeitskopie für Analyse auswählen'),
                        subtitle: Text(
                          widget.analysisStatus.isEmpty
                              ? 'Mehrere Arbeitskopien; bitte eine auswählen.'
                              : widget.analysisStatus,
                        ),
                        children: [
                          for (final path in row.paths)
                            ListTile(
                              title: Text(path),
                              trailing: TextButton(
                                onPressed: widget.analysisRunning
                                    ? null
                                    : () =>
                                          widget.onAnalyze!(row.identity, path),
                                child: const Text('Analysieren'),
                              ),
                            ),
                        ],
                      ),
                  if (row.analyzer != null)
                    AnalyzerSummary(data: row.analyzer!)
                  else
                    const ListTile(
                      title: Text('Codeanalyse: noch kein Ergebnis zugeordnet'),
                      subtitle: Text(
                        'Vorhandenen CodeAnalyzer für dieses Projekt ausführen und Ergebnis zuordnen.',
                      ),
                    ),
                  ListTile(
                    title: const Text('AIX-Aufträge'),
                    subtitle: Text(
                      widget.orders == null
                          ? widget.orderStatus
                          : orders.isEmpty
                          ? 'Kein eindeutig gebundener Auftrag in dieser Quelle gefunden.'
                          : '${orders.length} eindeutig zugeordnete Aufträge',
                    ),
                    trailing:
                        widget.orders == null && widget.onConnectOrders != null
                        ? TextButton(
                            onPressed: widget.onConnectOrders,
                            child: const Text('AIX verbinden'),
                          )
                        : null,
                  ),
                  ...orders.map(
                    (order) => ListTile(
                      title: Text(
                        'Auftrag ${order['auftrag_ref']} · ${order['zustand']}',
                      ),
                      subtitle: Text(
                        'Revision ${order['revision']} · Kandidat ${order['kandidat']} · Quelle: AIX',
                      ),
                    ),
                  ),
                  const ListTile(
                    title: Text('Getestet · gelandet · installiert'),
                    subtitle: Text('In dieser Quelle nicht belegt.'),
                  ),
                  ExpansionTile(
                    title: const Text('Technische Quelle und Arbeitskopien'),
                    children: [
                      SelectableText(row.identity),
                      SelectableText(row.description),
                      if (row.readme != null)
                        SelectableText(
                          'README: ${row.readme!['source']} · SHA-256 ${row.readme!['sha256']} · Arbeitskopie, kein Funktionsnachweis',
                        ),
                      if (row.observation?['sources'] != null)
                        SelectableText('${row.observation!['sources']}'),
                    ],
                  ),
                ],
              );
            },
          ),
        ),
      ],
    );
  }
}

class AnalyzerSummary extends StatelessWidget {
  const AnalyzerSummary({super.key, required this.data});
  final Map<String, dynamic> data;
  @override
  Widget build(BuildContext context) {
    final findings = data['findings'] is List
        ? data['findings'] as List
        : const [];
    final incomplete = data['incomplete_reasons'] is List
        ? data['incomplete_reasons'] as List
        : const [];
    final stubCoverage = data['stub_coverage'];
    final limited = incomplete.isNotEmpty || data['truncated'] == true;
    return ExpansionTile(
      title: Text(
        'Codeanalyse · ${data['reported_finding_count'] ?? '?'} Hinweise',
      ),
      subtitle: Text(
        'Stand: ${data['observed_at'] ?? 'unbekannt'} · Quellen: ${data['source_state'] ?? 'unbekannt'} · Abdeckung ${limited ? 'unvollständig' : 'nicht unabhängig bestätigt'}',
      ),
      children: [
        if (data['release_reported'] is String)
          SelectableText('Analyzer-Version: ${data['release_reported']}'),
        if (data['checkout'] is String)
          SelectableText('Analysierte Arbeitskopie: ${data['checkout']}'),
        if (incomplete.isNotEmpty)
          SelectableText('Grenzen: ${incomplete.join(', ')}'),
        if (data['truncated'] == true)
          const Text('Ergebnis ist abgeschnitten.'),
        if (stubCoverage is Map)
          SelectableText('Stub-Abdeckung laut Analyzer: $stubCoverage')
        else
          const Text('Stub-Abdeckung vom Analyzer nicht angegeben.'),
        ...findings.whereType<Map>().map(
          (item) => ListTile(
            title: Text(
              '${item['rule'] ?? 'Regel unbekannt'} · ${item['severity'] ?? 'unbekannt'} · ${item['evidence_tier'] ?? 'unbekannt'}',
            ),
            subtitle: SelectableText(
              '${item['file'] ?? '?'}:${item['line'] ?? '?'} · ${item['message'] ?? ''}',
            ),
          ),
        ),
        const Text(
          'Befunde sind keine automatische Fehlerfreiheit oder Produktfreigabe. Wiederholkommandos werden nicht ausgeführt.',
        ),
      ],
    );
  }
}
