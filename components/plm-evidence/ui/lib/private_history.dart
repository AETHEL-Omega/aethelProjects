import 'package:flutter/material.dart';

bool isPrivateHistory(Map<String, dynamic> data) =>
    data['schema'] == 'aethel.projects.private-work-history/v1' ||
    (data['case'] is String &&
        data['chat_evidence'] is List &&
        data['open'] is List);

void validatePrivateHistory(Map<String, dynamic> data) {
  if (data['case'] is String &&
      data['chat_evidence'] is List &&
      data['open'] is List) {
    return;
  }
  if (data['schema'] != 'aethel.projects.private-work-history/v1' ||
      data['sources'] is! List ||
      data['review_queue'] is! List ||
      data['events'] is! int ||
      data['catalog_without_transcript'] is! int) {
    throw const FormatException('Ungültige private Erfassung');
  }
}

class PrivateHistoryPanel extends StatelessWidget {
  const PrivateHistoryPanel({
    super.key,
    required this.data,
    required this.status,
  });
  final Map<String, dynamic>? data;
  final String status;

  @override
  Widget build(BuildContext context) {
    final value = data;
    if (value == null) {
      return const Center(
        child: Text(
          'Private coverage.json über „Auswertung öffnen“ auswählen.',
        ),
      );
    }
    if (value['case'] is String) {
      final open = value['open'] as List;
      final evidence = value['chat_evidence'] as List;
      return ListView(
        padding: const EdgeInsets.all(24),
        children: [
          Text(
            'Fall: ${value['case']}',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          Text(status),
          const Text('Teilprüfung: Chat-Aussagen sind keine Abnahme.'),
          Text('Offen', style: Theme.of(context).textTheme.titleMedium),
          ...open.map((item) => ListTile(title: Text('$item'))),
          Text(
            'Historische Quellen',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          ...evidence.whereType<Map<String, dynamic>>().map(
            (entry) => ExpansionTile(
              title: Text(
                '${entry['actor'] ?? 'Unbekannt'} · ${entry['kind'] ?? 'Unbekannt'} · Zeile ${entry['line'] ?? '?'}',
              ),
              subtitle: Text('${entry['source'] ?? 'Quelle unbekannt'}'),
              children: [SelectableText('${entry['preview'] ?? ''}')],
            ),
          ),
        ],
      );
    }
    final queue = value['review_queue'] as List;
    return ListView(
      padding: const EdgeInsets.all(24),
      children: [
        Text(
          'Private Arbeitsnachweise',
          style: Theme.of(context).textTheme.headlineSmall,
        ),
        Text(status),
        Text('Erfassung begonnen: ${value['observed_at'] ?? 'unbekannt'}'),
        const Text(
          'Lokaler Snapshot · keine vollständige fachliche Bewertung · keine Freigabe',
        ),
        const SizedBox(height: 16),
        Text('Extrahierte Ereignisse: ${value['events']}'),
        Text(
          'Katalogeinträge ohne Transkript: ${value['catalog_without_transcript']}',
        ),
        const SizedBox(height: 16),
        Text(
          'Offene Prüfschritte',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        ...queue
            .whereType<List>()
            .where((row) => row.length == 2)
            .map(
              (row) => ListTile(
                title: Text(switch (row[0]) {
                  'repair_source' => 'Quelle reparieren oder erneut prüfen',
                  'inspect_format_or_compaction' =>
                    'Format oder Kompaktierung prüfen',
                  'bind_work_and_validate_claims' =>
                    'Arbeit zuordnen und Aussagen prüfen',
                  'obtain_transcript' => 'Fehlendes Transkript beschaffen',
                  _ => 'Unbekannter Prüfschritt: ${row[0]}',
                }),
                trailing: Text('${row[1]}'),
              ),
            ),
        const Text(
          'Dateizahlen sind keine Anzahl erledigter Aufgaben. Chatinhalte und Projektzuordnungen sind hier noch nicht eingebunden.',
        ),
      ],
    );
  }
}
