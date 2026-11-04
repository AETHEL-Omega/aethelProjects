import 'dart:convert';
import 'package:file_selector/file_selector.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

void main() => runApp(const AethelPlm());

class AethelPlm extends StatelessWidget {
  const AethelPlm({super.key, this.initialJson});
  final String? initialJson;
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'AETHEL Arbeitsraum',
    theme: ThemeData(
      colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xff27566a)),
      useMaterial3: true,
    ),
    home: Workspace(initialJson: initialJson),
  );
}

/// Displays an assessment, never calculates or grants a verdict.
class Workspace extends StatefulWidget {
  const Workspace({super.key, this.initialJson});
  final String? initialJson;
  @override
  State<Workspace> createState() => _WorkspaceState();
}

class _WorkspaceState extends State<Workspace> {
  Map<String, dynamic>? document;
  final List<SourceItem> sources = [];
  String origin = 'Kein Dokument geöffnet';
  String? error;
  int section = 0;

  @override
  void initState() {
    super.initState();
    if (widget.initialJson != null) {
      _setDocument(widget.initialJson!, 'Übergebene Auswertung');
    } else {
      _example('assets/y1-assessment.json', 'Historischer Pilot Y-1');
    }
  }

  Future<void> _example(String asset, String title) async {
    try {
      _setDocument(await rootBundle.loadString(asset), title);
    } catch (_) {
      if (mounted) {
        setState(() => error = 'Beispieldaten konnten nicht geladen werden.');
      }
    }
  }

  Future<void> _open() async {
    try {
      final file = await openFile(
        acceptedTypeGroups: [
          const XTypeGroup(label: 'JSON', extensions: ['json']),
        ],
      );
      if (file == null) return;
      if (await file.length() > 8 * 1024 * 1024) {
        throw const FormatException('Datei überschreitet 8 MiB.');
      }
      final content = await file.readAsString();
      if (utf8.encode(content).length > 8 * 1024 * 1024) {
        throw const FormatException('Datei überschreitet 8 MiB.');
      }
      _setDocument(content, 'Datei: ${file.name}');
    } catch (_) {
      if (mounted) {
        setState(
          () => error = 'Datei konnte nicht geöffnet werden oder ist zu groß.',
        );
      }
    }
  }

  void _setDocument(String content, String title) {
    try {
      final value = jsonDecode(content);
      if (value is! Map<String, dynamic> ||
          !supported.contains(value['schema'])) {
        throw const FormatException();
      }
      validateShape(value);
      if (mounted) {
        setState(() {
          if (value['schema'] == 'aethel.plm.project-observation/v1' ||
              value['schema'] == 'aethel.plm.copilot-observation/v1') {
            sources.add(SourceItem(title, value));
            section = 3;
          } else {
            document = value;
            origin = title;
            section = 0;
          }
          error = null;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(
          () =>
              error = 'Ungültiges oder nicht unterstütztes Auswertungsformat.',
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final data = document;
    return Scaffold(
      appBar: AppBar(
        title: const Text('AETHEL  /  Arbeitsraum'),
        actions: [
          PopupMenuButton<String>(
            tooltip: 'Beispiel auswählen',
            onSelected: (v) => _example(
              v,
              v.contains('y1-')
                  ? 'Historischer Pilot Y-1'
                  : 'Synthetischer Qualitätsfall',
            ),
            itemBuilder: (_) => const [
              PopupMenuItem(
                value: 'assets/y1-assessment.json',
                child: Text('Y-1 · historisch'),
              ),
              PopupMenuItem(
                value: 'assets/linked-assessment.json',
                child: Text('Qualitätsfall · synthetisch'),
              ),
            ],
          ),
          TextButton.icon(
            onPressed: _open,
            icon: const Icon(Icons.folder_open),
            label: const Text('Auswertung öffnen'),
          ),
          const SizedBox(width: 12),
        ],
      ),
      body: Column(
        children: [
          Container(
            width: double.infinity,
            color: Theme.of(context).colorScheme.secondaryContainer,
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 9),
            child: Text(
              '$origin · Lesende Ansicht · Quelle und Autorität nicht geprüft',
            ),
          ),
          if (error != null)
            Padding(
              padding: const EdgeInsets.all(12),
              child: Semantics(
                liveRegion: true,
                child: Text(
                  error!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ),
            ),
          if (data == null)
            Expanded(
              child: Center(
                child: error == null
                    ? const CircularProgressIndicator()
                    : const Text("Bitte eine Auswertung öffnen."),
              ),
            )
          else
            Expanded(
              child: LayoutBuilder(
                builder: (context, constraints) {
                  final compact = constraints.maxWidth < 680;
                  return Row(
                    children: [
                      if (!compact)
                        NavigationRail(
                          selectedIndex: section,
                          labelType: NavigationRailLabelType.all,
                          onDestinationSelected: (v) =>
                              setState(() => section = v),
                          destinations: destinations,
                        ),
                      Expanded(
                        child: Column(
                          children: [
                            if (compact)
                              SegmentedButton<int>(
                                segments: const [
                                  ButtonSegment(
                                    value: 0,
                                    label: Text('Änderung'),
                                  ),
                                  ButtonSegment(
                                    value: 1,
                                    label: Text('Qualität'),
                                  ),
                                  ButtonSegment(
                                    value: 2,
                                    label: Text('Zusammenhang'),
                                  ),
                                  ButtonSegment(
                                    value: 3,
                                    label: Text('Quelle'),
                                  ),
                                ],
                                selected: {section},
                                onSelectionChanged: (v) =>
                                    setState(() => section = v.first),
                              ),
                            Expanded(
                              child: SingleChildScrollView(
                                padding: const EdgeInsets.all(24),
                                child: Center(
                                  child: ConstrainedBox(
                                    constraints: const BoxConstraints(
                                      maxWidth: 1100,
                                    ),
                                    child: switch (section) {
                                      0 => ChangePanel(data: data),
                                      1 => QualityPanel(data: data),
                                      2 => TracePanel(data: data),
                                      _ => SourcePanel(
                                        data: data,
                                        sources: sources,
                                      ),
                                    },
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  );
                },
              ),
            ),
        ],
      ),
    );
  }
}

const destinations = [
  NavigationRailDestination(
    icon: Icon(Icons.account_tree_outlined),
    label: Text('Änderung'),
  ),
  NavigationRailDestination(
    icon: Icon(Icons.fact_check_outlined),
    label: Text('Qualität'),
  ),
  NavigationRailDestination(
    icon: Icon(Icons.hub_outlined),
    label: Text('Zusammenhang'),
  ),
  NavigationRailDestination(
    icon: Icon(Icons.source_outlined),
    label: Text('Quelle'),
  ),
];
const supported = {
  'aethel.plm.assessment/v1',
  'aethel.plm.linked-assessment/v1',
  'aethel.plm.quality-assessment/v1',
  'aethel.plm.project-observation/v1',
  'aethel.plm.copilot-observation/v1',
};
Map<String, dynamic>? object(dynamic value) =>
    value is Map<String, dynamic> ? value : null;
List<dynamic> list(dynamic value) => value is List ? value : const [];
String show(dynamic value) => value == null ? 'Unbekannt' : value.toString();
void validateShape(Map<String, dynamic> data) {
  final schema = data['schema'];
  if (schema == 'aethel.plm.assessment/v1' &&
      (object(data['change']) == null || data['claims'] is! List)) {
    throw const FormatException();
  }
  if (schema == 'aethel.plm.linked-assessment/v1' &&
      (object(data['change']) == null ||
          object(data['quality']) == null ||
          data['links'] is! List)) {
    throw const FormatException();
  }
  if (schema == 'aethel.plm.quality-assessment/v1' &&
      object(data['source']) == null) {
    throw const FormatException();
  }
  if ((schema == 'aethel.plm.project-observation/v1' ||
          schema == 'aethel.plm.copilot-observation/v1') &&
      object(data['evidence']) == null) {
    throw const FormatException();
  }
}

Map<String, dynamic>? changeAssessment(Map<String, dynamic> data) =>
    data['schema'] == 'aethel.plm.assessment/v1'
    ? data
    : data['schema'] == 'aethel.plm.linked-assessment/v1'
    ? object(data['change'])
    : null;
Map<String, dynamic>? qualityAssessment(Map<String, dynamic> data) =>
    data['schema'] == 'aethel.plm.quality-assessment/v1'
    ? data
    : data['schema'] == 'aethel.plm.linked-assessment/v1'
    ? object(data['quality'])
    : null;

class ChangePanel extends StatelessWidget {
  const ChangePanel({super.key, required this.data});
  final Map<String, dynamic> data;
  @override
  Widget build(BuildContext context) {
    final assessment = changeAssessment(data);
    if (assessment == null) {
      return const EmptyPanel('Diese Datei enthält keine Änderungsauswertung.');
    }
    final change = object(assessment['change']) ?? {};
    final snapshot = object(assessment['snapshot']) ?? {};
    final claims = list(assessment['claims']);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Änderung ${show(change['id'])}',
          style: Theme.of(context).textTheme.headlineMedium,
        ),
        const SizedBox(height: 6),
        Text(
          show(change['goal']),
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 16),
        Wrap(
          spacing: 20,
          runSpacing: 8,
          children: [
            Fact('Produktreferenz', show(change['product_reference'])),
            Fact('Betrachteter Kandidat', show(change['candidate'])),
            Fact(
              'Quellenzeit',
              snapshot['kind'] == 'historical'
                  ? 'Historisch: ${show(snapshot['captured_on'])}'
                  : 'Unbekannt',
            ),
          ],
        ),
        const SizedBox(height: 18),
        Text(show(change['context'])),
        const SizedBox(height: 20),
        Text(
          'Aussagen und Nachweise',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 8),
        if (claims.isEmpty) const Text('Keine Aussagen in der Auswertung.'),
        for (final item in claims)
          if (object(item) case final claim?) ClaimCard(claim: claim),
        if (list(assessment['unreferenced_evidence']).isNotEmpty) ...[
          const SizedBox(height: 16),
          const Text('Nicht zugeordnete Belege'),
          for (final item in list(assessment['unreferenced_evidence']))
            if (object(item) case final e?)
              ListTile(
                title: Text(show(e['id'])),
                subtitle: Text('Quelle: ${show(e['source'])}'),
              ),
        ],
      ],
    );
  }
}

class ClaimCard extends StatelessWidget {
  const ClaimCard({super.key, required this.claim});
  final Map<String, dynamic> claim;
  @override
  Widget build(BuildContext context) => Card(
    child: ExpansionTile(
      title: Text(show(claim['statement'])),
      subtitle: Text(
        '${show(claim['id'])} · Benötigt: ${show(claim['required_kind'])} · ${list(claim['gaps']).length} Lücken',
      ),
      childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
      expandedCrossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (final item in list(claim['gaps']))
          if (object(item) case final gap?)
            ListTile(
              dense: true,
              leading: const Icon(Icons.info_outline),
              title: Text(show(gap['code'])),
              subtitle: Text(show(gap['explanation'])),
            ),
        if (list(claim['references']).isEmpty)
          const Text('Keine Belegreferenz vorhanden.'),
        for (final item in list(claim['references']))
          if (object(item) case final ref?) EvidenceTile(ref: ref),
      ],
    ),
  );
}

class EvidenceTile extends StatelessWidget {
  const EvidenceTile({super.key, required this.ref});
  final Map<String, dynamic> ref;
  @override
  Widget build(BuildContext context) {
    final e = object(ref['evidence']) ?? {};
    return ListTile(
      dense: true,
      leading: const Icon(Icons.description_outlined),
      title: Text(
        '${show(e['id'])} · ${show(e['reported_result'])} (berichtet)',
      ),
      subtitle: Text(
        'Quelle: ${show(e['source'])}\nArt: ${show(e['kind'])} · Stand: ${show(e['candidate'])}\nArtvergleich: ${show(ref['kind_match'])} · Standbindung: ${show(ref['candidate_binding'])}\nHerkunft: ${show(e['provenance'])}',
      ),
    );
  }
}

class QualityPanel extends StatelessWidget {
  const QualityPanel({super.key, required this.data});
  final Map<String, dynamic> data;
  @override
  Widget build(BuildContext context) {
    final assessment = qualityAssessment(data);
    if (assessment == null) {
      return const EmptyPanel(
        'Keine verknüpfte Qualitätsakte in dieser Auswertung.',
      );
    }
    final source = object(assessment['source']) ?? {};
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Qualitätsakte ${show(source['id'])}',
          style: Theme.of(context).textTheme.headlineMedium,
        ),
        const SizedBox(height: 8),
        const Text(
          'Übergänge sind nicht ausgeführt. Externe Autorität ist nicht verifiziert.',
        ),
        const SizedBox(height: 20),
        Text('Issues', style: Theme.of(context).textTheme.titleLarge),
        for (final item in list(source['issues']))
          if (object(item) case final issue?)
            ListTile(
              leading: const Icon(Icons.report_problem_outlined),
              title: Text(show(issue['problem'])),
              subtitle: Text(
                '${show(issue['id'])} · Status (berichtet): ${show(issue['state'])} · Konfiguration: ${show(issue['affected_configuration'])}',
              ),
            ),
        const SizedBox(height: 12),
        Text('Maßnahmen', style: Theme.of(context).textTheme.titleLarge),
        for (final item in list(source['actions']))
          if (object(item) case final action?)
            Card(
              child: ExpansionTile(
                title: Text(show(action['objective'])),
                subtitle: Text(
                  '${show(action['id'])} · ${show(action['kind'])} · ${show(action['state'])}',
                ),
                children: [
                  ListTile(
                    title: Text(
                      'Verantwortung: ${show(action['owner_reference'])}',
                    ),
                    subtitle: Text(
                      'Termin: ${show(action['due_on'])} · Ursachenreferenz: ${show(action['cause_reference'])}',
                    ),
                  ),
                  for (final item in list(action['scopes']))
                    if (object(item) case final scope?)
                      ListTile(
                        dense: true,
                        title: Text(
                          'Issue ${show(scope['issue_id'])} · Kandidat ${show(scope['candidate'])}',
                        ),
                        subtitle: Text(
                          'Umgebung: ${show(scope['environment'])}\nKriterium: ${show(scope['criterion'])}\nBeobachtung: ${show(scope['observation_window'])}',
                        ),
                      ),
                ],
              ),
            ),
        const SizedBox(height: 12),
        Text(
          'Wirksamkeitsprüfungen (berichtet)',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        if (list(source['checks']).isEmpty)
          const Text('Keine Wirksamkeitsprüfung im Qualitätsfall.'),
        for (final item in list(source['checks']))
          if (object(item) case final check?)
            ListTile(
              title: Text(
                '${show(check['id'])} · Maßnahme ${show(check['action_id'])}',
              ),
              subtitle: Text(
                'Prüfer: ${show(check['reviewer_reference'])} · Planrevision: ${show(check['plan_revision'])}\nKandidat: ${show(check['candidate'])} · Umgebung: ${show(check['environment'])}\nKriterium: ${show(check['criterion'])} · Belege: ${list(check['evidence_ids']).join(', ')}',
              ),
            ),
        const SizedBox(height: 12),
        Text('Offene Befunde', style: Theme.of(context).textTheme.titleLarge),
        for (final item in list(assessment['snapshot_findings']))
          if (object(item) case final f?) FindingTile(f: f),
        for (final item in list(assessment['transitions']))
          if (object(item) case final transition?) ...[
            for (final item in list(transition['findings']))
              if (object(item) case final f?) FindingTile(f: f),
          ],
      ],
    );
  }
}

/// Only renders explicit relationships; absent links never imply coverage.
class TracePanel extends StatelessWidget {
  const TracePanel({super.key, required this.data});
  final Map<String, dynamic> data;
  @override
  Widget build(BuildContext context) {
    final assessment = changeAssessment(data);
    if (assessment == null) {
      return const EmptyPanel('Keine Aussage-/Änderungsauswertung vorhanden.');
    }
    final links = list(
      data['links'],
    ).map(object).whereType<Map<String, dynamic>>().toList();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Aussagen und Zusammenhänge',
          style: Theme.of(context).textTheme.headlineMedium,
        ),
        const SizedBox(height: 10),
        const Text(
          'Referenzen und Zuordnungen sind berichtet. Sie belegen weder Prüfung noch Erfüllung.',
        ),
        const SizedBox(height: 18),
        for (final item in list(assessment['claims']))
          if (object(item) case final claim?)
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      show(claim['statement']),
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Aussage: ${show(claim['id'])} · benötigte Belegart: ${show(claim['required_kind'])}',
                    ),
                    const SizedBox(height: 8),
                    if (list(claim['references']).isEmpty)
                      const Text('Belegreferenz: keine'),
                    for (final item in list(claim['references']))
                      if (object(item) case final ref?)
                        Text(
                          'Beleg: ${show(object(ref['evidence'])?['id'])} · Ergebnis berichtet: ${show(object(ref['evidence'])?['reported_result'])} · Standbindung: ${show(ref['candidate_binding'])}',
                        ),
                    if (!links.any((l) => l['claim_id'] == claim['id']))
                      const Text(
                        'Issue- und Maßnahmenzuordnung: nicht angegeben',
                      ),
                    for (final link in links.where(
                      (l) => l['claim_id'] == claim['id'],
                    ))
                      Text(
                        'Berichtete Zuordnung: Issue ${show(link['issue_id'])} → Maßnahme ${show(link['action_id'])}',
                      ),
                    const SizedBox(height: 8),
                    Text('Offene Befunde: ${list(claim['gaps']).length}'),
                  ],
                ),
              ),
            ),
        if (data['schema'] != 'aethel.plm.linked-assessment/v1')
          const Padding(
            padding: EdgeInsets.only(top: 14),
            child: Text('Diese Datei enthält keine verknüpfte Qualitätsakte.'),
          ),
      ],
    );
  }
}

class FindingTile extends StatelessWidget {
  const FindingTile({super.key, required this.f});
  final Map<String, dynamic> f;
  @override
  Widget build(BuildContext context) => ListTile(
    dense: true,
    leading: const Icon(Icons.info_outline),
    title: Text(show(f['code'])),
    subtitle: Text(
      'Objekt: ${show(f['object_id'])} · Referenzen: ${list(f['reference_ids']).join(', ')}',
    ),
  );
}

class SourceItem {
  const SourceItem(this.name, this.data);
  final String name;
  final Map<String, dynamic> data;
}

class SourcePanel extends StatelessWidget {
  const SourcePanel({super.key, required this.data, this.sources = const []});
  final Map<String, dynamic> data;
  final List<SourceItem> sources;
  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(
        'Quellen und Einordnung',
        style: Theme.of(context).textTheme.headlineMedium,
      ),
      const SizedBox(height: 12),
      const Text(
        'Ausgewählte Dateien sind Quellenbehauptungen. Die App prüft weder Signaturen, Rechte noch Aktualität und vergibt keine Freigaben. Zusätzlich geöffnete Quellen werden nicht automatisch einer Änderung zugeordnet.',
      ),
      const SizedBox(height: 18),
      SourceDetails(name: 'Aktuelle Fallauswertung', data: data),
      for (final source in sources)
        SourceDetails(name: source.name, data: source.data),
    ],
  );
}

class SourceDetails extends StatelessWidget {
  const SourceDetails({super.key, required this.name, required this.data});
  final String name;
  final Map<String, dynamic> data;
  @override
  Widget build(BuildContext context) => Card(
    child: ExpansionTile(
      title: Text(name),
      subtitle: Text(show(data['schema'])),
      childrenPadding: const EdgeInsets.all(16),
      expandedCrossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Fact('Autorität', show(data['authority'] ?? data['assessment'])),
        if (data.containsKey('freshness'))
          Fact('Aktualität', show(data['freshness'])),
        if (data.containsKey('goal_id')) ...[
          Fact('Copilot-Goal', show(data['goal_id'])),
          Fact(
            'Gemeldeter Träger / Agent',
            '${show(data['reported_actor'])} / ${show(data['reported_agent_id'])}',
          ),
          Fact(
            'Gemeldeter Modus / Inferenzort',
            '${show(data['reported_compute_mode'])} / ${show(data['actual_inference_location'])}',
          ),
          Fact('Quellenzeit (berichtet)', show(data['updated_at_reported'])),
        ],
        if (data.containsKey('repository_id')) ...[
          Fact('Lokale Repository-Identität', show(data['repository_id'])),
          Fact('Produktreferenz', show(data['product_reference'])),
          Fact(
            'Scanzeit / Exportzeit (berichtet)',
            '${show(data['scan_generated_at_reported'])} / ${show(data['export_generated_at_reported'])}',
          ),
        ],
        if (data['findings'] is List) ...[
          const SizedBox(height: 12),
          const Text('Zuordnungslücken'),
          for (final item in list(data['findings']))
            if (object(item) case final f?) FindingTile(f: f),
        ],
        if (data['links'] is List) ...[
          const SizedBox(height: 12),
          const Text('Zuordnungen (berichtet)'),
          for (final item in list(data['links']))
            if (object(item) case final link?)
              ListTile(
                title: Text(
                  '${show(link['issue_id'])} → ${show(link['action_id'])} → ${show(link['claim_id'])}',
                ),
                subtitle: Text('Quelle: ${show(link['provenance'])}'),
              ),
        ],
      ],
    ),
  );
}

class Fact extends StatelessWidget {
  const Fact(this.label, this.value, {super.key});
  final String label, value;
  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    mainAxisSize: MainAxisSize.min,
    children: [
      Text(label, style: Theme.of(context).textTheme.labelMedium),
      SelectableText(value),
    ],
  );
}

class EmptyPanel extends StatelessWidget {
  const EmptyPanel(this.message, {super.key});
  final String message;
  @override
  Widget build(BuildContext context) =>
      Padding(padding: const EdgeInsets.all(24), child: Text(message));
}
