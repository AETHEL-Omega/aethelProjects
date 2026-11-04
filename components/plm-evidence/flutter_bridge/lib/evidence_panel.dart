import 'dart:convert';

import 'package:flutter/material.dart';

import 'src/rust/api.dart';

/// Displays the Rust evaluator's reference-only result; source authority is not inferred.
class EvidencePanel extends StatefulWidget {
  const EvidencePanel({super.key, required this.caseJson});
  final String caseJson;

  @override
  State<EvidencePanel> createState() => _EvidencePanelState();
}

class _EvidencePanelState extends State<EvidencePanel> {
  late Future<Map<String, dynamic>> assessment;

  Future<Map<String, dynamic>> _evaluate(String input) async {
    if (utf8.encode(input).length > 8 * 1024 * 1024) {
      throw const FormatException('Eingabe zu groß');
    }
    final result = jsonDecode(await assessCaseJson(input: input));
    if (result is! Map<String, dynamic> ||
        result['schema'] != 'aethel.plm.assessment/v1' ||
        result['claims'] is! List) {
      throw const FormatException('Ungültige Auswertung');
    }
    return result;
  }

  @override
  void initState() {
    super.initState();
    assessment = _evaluate(widget.caseJson);
  }

  @override
  void didUpdateWidget(covariant EvidencePanel oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.caseJson != widget.caseJson) {
      assessment = _evaluate(widget.caseJson);
    }
  }

  @override
  Widget build(BuildContext context) => FutureBuilder<Map<String, dynamic>>(
    future: assessment,
    builder: (context, snapshot) {
      if (snapshot.connectionState != ConnectionState.done) {
        return const CircularProgressIndicator();
      }
      if (snapshot.hasError) return const Text('Auswertung nicht verfügbar.');
      if (!snapshot.hasData) return const CircularProgressIndicator();
      final claims = (snapshot.data!['claims'] as List).whereType<Map>();
      final sourceSnapshot = snapshot.data!['snapshot'];
      final change = snapshot.data!['change'];
      final historical =
          sourceSnapshot is Map && sourceSnapshot['kind'] == 'historical';
      return ListView(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        children: [
          Text(
            historical
                ? 'Historische Momentaufnahme: ${sourceSnapshot['captured_on']} · kein Live-Stand'
                : 'Quellenzeit nicht angegeben',
          ),
          if (change is Map)
            Text(
              'Fall: ${change['id'] ?? 'unbekannt'} · Kandidat: ${change['candidate'] ?? 'unbekannt'}',
            ),
          const Text(
            'Quellenangaben; keine unabhängige Verifikation oder Freigabe.',
          ),
          for (final claim in claims)
            ListTile(
              title: Text('${claim['statement'] ?? ''}'),
              subtitle: Text(
                (claim['gaps'] is List ? claim['gaps'] as List : const [])
                    .whereType<Map>()
                    .map((gap) => '${gap['explanation'] ?? ''}')
                    .join('\n'),
              ),
            ),
        ],
      );
    },
  );
}
