import 'package:flutter/material.dart';

Map<String, dynamic>? _map(dynamic v) => v is Map<String, dynamic> ? v : null;
List<Map<String, dynamic>> _maps(dynamic v) =>
    v is List ? v.map(_map).whereType<Map<String, dynamic>>().toList() : [];
String _show(dynamic v) =>
    v == null || v.toString().isEmpty ? 'Unbekannt' : v.toString();

String _nodeDescription(Map<String, dynamic> node) {
  final kind = node['kind'];
  if (kind == 'repository') {
    final identity = _show(node['git_common_dir']);
    final root = identity.endsWith('/.git')
        ? identity.substring(0, identity.length - 5)
        : identity;
    final paths = node['paths'] is List ? node['paths'] as List : const [];
    final location = root.contains('/_archive/')
        ? 'Archivpfad'
        : 'Repositorygruppe';
    return '$location: $root\n${paths.length} erfasste Arbeitsverzeichnisse';
  }
  if (kind == 'registereintrag') {
    return 'Eintrag im Workspace-Manifest · kein eigenes Repository\n'
        'Kategorie: ${_show(node['category'])} · Status laut Register: ${_show(node['recorded_status'])}';
  }
  if (kind == 'vorschlag') {
    return 'Projektvorschlag · ${_show(node['proposal_status'])}';
  }
  if (kind == 'komponente') {
    return 'Komponente · Quelle: ${_show(node['source'])}';
  }
  if (kind == 'git_unaufgeloest') {
    return 'Git-Ort mit ungeklärter Zuordnung\n${_show(node['path'])}';
  }
  if (kind == 'nicht_git_kandidat') {
    return 'Projektkandidat ohne zugeordnetes Git-Repository\n${_show(node['path'])}';
  }
  if (kind == 'regelkreis') {
    return 'Geplanter oder dokumentierter Regelkreis · ${_show(node['loop_status'])}';
  }
  return '${_show(kind)} · Quelle: ${_show(node['source'])}';
}

const _areas = ['Firma', 'Fabrik', 'Produkte', 'Plattform', 'Unzugeordnet'];

class LandscapePanel extends StatefulWidget {
  const LandscapePanel({
    super.key,
    required this.data,
    required this.origin,
    required this.currentAssessment,
    required this.selectedId,
    required this.sources,
    required this.selectedSourceIndex,
    required this.onBindSource,
    required this.selectedLandingIndex,
    required this.onBindLanding,
    required this.onSelect,
    required this.onOpenY1,
  });
  final Map<String, dynamic> data;
  final String origin;
  final Map<String, dynamic> currentAssessment;
  final String? selectedId;
  final List<Map<String, dynamic>> sources;
  final int? selectedSourceIndex;
  final ValueChanged<int> onBindSource;
  final int? selectedLandingIndex;
  final ValueChanged<int> onBindLanding;
  final ValueChanged<String> onSelect;
  final VoidCallback onOpenY1;
  @override
  State<LandscapePanel> createState() => _LandscapePanelState();
}

class _LandscapePanelState extends State<LandscapePanel> {
  String query = '';
  String area = 'Alle';
  String relationType = 'Alle';

  @override
  Widget build(BuildContext context) {
    final nodes = _maps(widget.data['nodes']);
    final edges = _maps(widget.data['edges']);
    final byId = {for (final n in nodes) _show(n['id']): n};
    final visible = nodes.where((n) {
      final text = '${_show(n['name'])} ${_show(n['id'])} ${_show(n['kind'])}'
          .toLowerCase();
      final tags = n['areas'] is List ? (n['areas'] as List) : const [];
      return text.contains(query.toLowerCase()) &&
          (area == 'Alle' ||
              (area == 'Unzugeordnet' ? tags.isEmpty : tags.contains(area)));
    }).toList();
    visible.sort((a, b) {
      int rank(Map<String, dynamic> n) {
        final name = _show(n['name']).toLowerCase();
        final term = query.trim().toLowerCase();
        if (term.isEmpty) return 0;
        return name == term
            ? 0
            : name.startsWith(term)
            ? 1
            : 2;
      }

      final relevance = rank(a).compareTo(rank(b));
      if (relevance != 0) return relevance;
      final nameOrder = _show(
        a['name'],
      ).toLowerCase().compareTo(_show(b['name']).toLowerCase());
      if (nameOrder != 0) return nameOrder;
      final kindOrder = (a['kind'] == 'repository' ? 0 : 1).compareTo(
        b['kind'] == 'repository' ? 0 : 1,
      );
      return kindOrder != 0
          ? kindOrder
          : _show(a['id']).compareTo(_show(b['id']));
    });
    final selected = byId[widget.selectedId];
    final types = edges.map((e) => _show(e['type'])).toSet().toList()..sort();
    final effectiveType = types.contains(relationType) ? relationType : 'Alle';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Projektlandschaft',
          style: Theme.of(context).textTheme.headlineMedium,
        ),
        const SizedBox(height: 6),
        Text(
          '${widget.origin} · Quellenzeit: ${_show(widget.data['source_time_reported'])}',
        ),
        const Text(
          'Ausgewählte Quellenbehauptungen · Aktualität, Identität und Betrieb nicht geprüft.',
        ),
        const SizedBox(height: 16),
        TextField(
          key: const Key('landscape-search'),
          decoration: const InputDecoration(
            labelText: 'Projekt, Repository oder Komponente suchen',
            prefixIcon: Icon(Icons.search),
            border: OutlineInputBorder(),
          ),
          onChanged: (v) => setState(() => query = v),
        ),
        const SizedBox(height: 10),
        Wrap(
          spacing: 8,
          runSpacing: 4,
          children: [
            for (final label in ['Alle', ..._areas])
              ChoiceChip(
                label: Text(label),
                selected: area == label,
                onSelected: (_) => setState(() => area = label),
              ),
          ],
        ),
        const SizedBox(height: 4),
        Text(
          'Bereiche stammen aus Quellangaben bzw. Manifestkategorien und sind Suchhilfen, kein Produkt- oder Betriebsnachweis.',
          style: Theme.of(context).textTheme.bodySmall,
        ),
        const SizedBox(height: 14),
        LayoutBuilder(
          builder: (context, constraints) {
            final list = SizedBox(
              height: 350,
              child: Card(
                child: Column(
                  children: [
                    Padding(
                      padding: const EdgeInsets.all(12),
                      child: Align(
                        alignment: Alignment.centerLeft,
                        child: Text(
                          '${visible.length} Einträge · getrennte Identitäten',
                        ),
                      ),
                    ),
                    Expanded(
                      child: visible.isEmpty
                          ? const Center(
                              child: Text('Keine passenden Einträge.'),
                            )
                          : ListView.builder(
                              key: const Key('landscape-list'),
                              itemCount: visible.length,
                              itemBuilder: (context, i) {
                                final n = visible[i];
                                return ListTile(
                                  key: ValueKey('node-${n['id']}'),
                                  selected: n['id'] == widget.selectedId,
                                  title: Text(_show(n['name'])),
                                  subtitle: Text(_nodeDescription(n)),
                                  isThreeLine: _nodeDescription(
                                    n,
                                  ).contains('\n'),
                                  onTap: () => widget.onSelect(_show(n['id'])),
                                );
                              },
                            ),
                    ),
                  ],
                ),
              ),
            );
            final detail = selected == null
                ? const Card(
                    child: Padding(
                      padding: EdgeInsets.all(20),
                      child: Text(
                        'Eintrag auswählen, um Herkunft, Beziehungen und Lücken zu sehen.',
                      ),
                    ),
                  )
                : _detail(context, selected, byId, edges, types, effectiveType);
            if (constraints.maxWidth < 760) {
              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [list, const SizedBox(height: 12), detail],
              );
            }
            return Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SizedBox(width: 330, child: list),
                const SizedBox(width: 16),
                Expanded(child: detail),
              ],
            );
          },
        ),
        _coverage(context),
        if (_maps(widget.data['edges']).isEmpty)
          const Text('Keine Beziehungen in dieser Auswahl.'),
        if (widget.data['unresolved_endpoints'] is List &&
            (widget.data['unresolved_endpoints'] as List).isNotEmpty)
          Text(
            'Nicht aufgelöste Beziehungsendpunkte: ${(widget.data['unresolved_endpoints'] as List).join(', ')}',
          ),
      ],
    );
  }

  Widget _coverage(BuildContext context) {
    final scope = _map(widget.data['scope']);
    final summary = _map(widget.data['summary']);
    final notes = scope?['notes'] is List ? scope!['notes'] as List : const [];
    Widget entries(String title, dynamic raw) {
      if (raw is! List) return ListTile(title: Text('$title: unbekannt'));
      return ExpansionTile(
        title: Text('$title: ${raw.length}'),
        children: [
          SizedBox(
            height: 220,
            child: ListView.builder(
              itemCount: raw.length,
              itemBuilder: (_, i) =>
                  ListTile(dense: true, title: SelectableText(_show(raw[i]))),
            ),
          ),
        ],
      );
    }

    return ExpansionTile(
      title: const Text('Erfassungsumfang und Grenzen'),
      children: [
        ListTile(
          title: Text('Umfang: ${_show(scope?['policy'])}'),
          subtitle: Text(
            'Quelle meldet ${_show(summary?['nodes'])} Einträge und ${_show(summary?['edges'])} Beziehungen; Einträge sind keine eigenständigen Produkte.',
          ),
        ),
        for (final note in notes)
          ListTile(dense: true, title: Text(_show(note))),
        for (final supplement in _maps(widget.data['supplements']))
          ListTile(
            dense: true,
            title: Text(
              'Zusätzliche Quelle: ${_show(supplement['source_id'])} · ${_show(supplement['generated_at'])}',
            ),
          ),
        entries('Erfassungsprobleme', widget.data['problems']),
        entries('Ausgelassene Pfade', widget.data['excluded_paths']),
        entries('Nicht verfolgte Symlinks', widget.data['symlinks']),
      ],
    );
  }

  Widget _detail(
    BuildContext context,
    Map<String, dynamic> n,
    Map<String, Map<String, dynamic>> byId,
    List<Map<String, dynamic>> edges,
    List<String> types,
    String effectiveType,
  ) {
    final id = n['id'];
    final related = edges
        .where(
          (e) =>
              (e['from'] == id || e['to'] == id) &&
              (effectiveType == 'Alle' || e['type'] == effectiveType),
        )
        .toList();
    final attachments = _maps(
      widget.data['attachments'],
    ).where((a) => a['node_id'] == id);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _show(n['name']),
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            Text(_nodeDescription(n)),
            Text(
              'Technische Identität: ${_show(n['id'])}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 10),
            Text('Zweck: ${_show(n['purpose'])}'),
            Text(
              'Status der Quelle: ${_show(n['proposal_status'] ?? n['recorded_status'] ?? n['loop_status'])}',
            ),
            if (n['git_common_dir'] != null)
              SelectableText(
                'Lokale Repository-Identität: ${_show(n['git_common_dir'])}',
              ),
            if (n['paths'] is List && (n['paths'] as List).isNotEmpty)
              ExpansionTile(
                title: Text(
                  'Arbeitsverzeichnisse (${(n['paths'] as List).length})',
                ),
                children: [
                  for (final path in n['paths'] as List)
                    ListTile(dense: true, title: SelectableText(_show(path))),
                ],
              ),
            Text(
              'Zuständige Quelle: ${_show(n['source'] ?? widget.data['source_id'])}',
            ),
            Text(
              'Quellenrevision: ${_show(n['source_revision'] ?? widget.data['source_revision'])} · Zeit: ${_show(widget.data['source_time_reported'])}',
            ),
            const SizedBox(height: 18),
            for (final a in attachments) _caseLink(context, a),
            _projectSources(context, n),
            _landingSources(context, n, attachments.toList()),
            Text('Beziehungen', style: Theme.of(context).textTheme.titleLarge),
            DropdownButton<String>(
              key: const Key('relation-filter'),
              value: effectiveType,
              items: [
                for (final t in ['Alle', ...types])
                  DropdownMenuItem(value: t, child: Text(t)),
              ],
              onChanged: (v) => setState(() => relationType = v ?? 'Alle'),
            ),
            const Text(
              'Status und Beziehungen sind Aussagen der Quelle; eine Manifestabhängigkeit belegt keinen Betrieb.',
            ),
            if (related.isEmpty)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 12),
                child: Text(
                  'Keine Beziehung in dieser Auswahl; das belegt nicht deren Fehlen.',
                ),
              ),
            for (final e in related) _edge(context, e, byId, id),
          ],
        ),
      ),
    );
  }

  Widget _projectSources(BuildContext context, Map<String, dynamic> node) {
    final identity = node['git_common_dir'];
    if (node['kind'] != 'repository' ||
        identity is! String ||
        identity.isEmpty) {
      return const SizedBox.shrink();
    }
    final candidates = <int>[];
    for (var i = 0; i < widget.sources.length; i++) {
      final projection = _map(widget.sources[i]['data']);
      if (projection?['schema'] == 'aethel.plm.project-observation/v1' &&
          projection?['repository_id'] == identity) {
        candidates.add(i);
      }
    }
    final selected = widget.selectedSourceIndex;
    final selectedData = selected != null && candidates.contains(selected)
        ? _map(widget.sources[selected]['data'])
        : null;
    return Padding(
      padding: const EdgeInsets.only(bottom: 18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Projektbeobachtungen',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const Text(
            'Nur exakt gleiche lokale Repository-Identitäten sind auswählbar. Die Zuordnung gilt nur in dieser Sitzung und bestätigt keine Quelle.',
          ),
          if (candidates.isEmpty)
            const Text(
              'Keine passende ausgewählte Beobachtung; andere Quellen bleiben unzugeordnet.',
            ),
          for (final i in candidates)
            TextButton.icon(
              key: ValueKey('bind-source-$i'),
              onPressed: () => widget.onBindSource(i),
              icon: Icon(selected == i ? Icons.link : Icons.add_link),
              label: Text(
                '${selected == i ? 'Zugeordnet' : 'Temporär zuordnen'}: ${_show(widget.sources[i]['name'])}',
              ),
            ),
          if (selectedData != null) ...[
            Text(
              'Beobachtung: ${_show(widget.sources[selected!]['name'])} · Quelle und Aktualität ungeprüft.',
            ),
            Text(
              'Scan / Export: ${_show(selectedData['scan_generated_at_reported'])} / ${_show(selectedData['export_generated_at_reported'])}',
            ),
            SelectableText(
              'Gemeldeter Checkout-HEAD: ${_show(_map(selectedData['evidence'])?['candidate'])}',
            ),
            const Text(
              'Ein Checkout-HEAD ist kein Nachweis für einen bestimmten Fallkandidaten oder einen laufenden Auftrag.',
            ),
          ],
        ],
      ),
    );
  }

  Widget _landingSources(
    BuildContext context,
    Map<String, dynamic> node,
    List<Map<String, dynamic>> attachments,
  ) {
    final identity = node['git_common_dir'];
    if (node['kind'] != 'repository' ||
        identity is! String ||
        identity.isEmpty) {
      return const SizedBox.shrink();
    }
    final candidates = <int>[];
    for (var i = 0; i < widget.sources.length; i++) {
      final projection = _map(widget.sources[i]['data']);
      if (projection?['schema'] == 'aethel.plm.landing-observation/v1' &&
          projection?['repository_id'] == identity) {
        candidates.add(i);
      }
    }
    final selected = widget.selectedLandingIndex;
    final report = selected != null && candidates.contains(selected)
        ? _map(widget.sources[selected]['data'])
        : null;
    final attachedCandidate = attachments.isEmpty
        ? null
        : attachments.first['candidate'];
    final reportedHead = report?['head_supplied'];
    return Padding(
      padding: const EdgeInsets.only(bottom: 18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Landing · Review und Gate',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const Text(
            'Berichte werden explizit zugeordnet. Ein gemeldetes Ergebnis ist keine Landung, Installation oder Wirkungsprüfung.',
          ),
          if (candidates.isEmpty)
            const Text(
              'Kein passender Landing-Bericht ausgewählt; nicht geprüft.',
            ),
          for (final i in candidates)
            TextButton.icon(
              key: ValueKey('bind-landing-$i'),
              onPressed: () => widget.onBindLanding(i),
              icon: Icon(selected == i ? Icons.link : Icons.add_link),
              label: Text(
                '${selected == i ? 'Zugeordnet' : 'Temporär zuordnen'}: ${_show(widget.sources[i]['name'])}',
              ),
            ),
          if (report != null) ...[
            Text(
              'Ergebnis berichtet: ${_show(report['reported_ok'])} · ${_show(report['reported_reason'])}',
            ),
            SelectableText('Übergebener Prüfkopf: ${_show(reportedHead)}'),
            Text(
              'Quelle: ${_show(report['source_id'])} · Stand: ${_show(report['observed_at_supplied'])}',
            ),
            Text(
              attachedCandidate == null
                  ? 'Kein Fallkandidat für Vergleich angegeben.'
                  : reportedHead != attachedCandidate
                  ? 'Abweichender Kandidat: Bericht und Fall sind nicht derselbe Commit.'
                  : 'Kandidatenangaben stimmen überein; Quelle und Autorität sind nicht verifiziert.',
              key: const Key('landing-candidate-comparison'),
            ),
            const Text(
              'Der Kopf wurde dem Projektor separat übergeben; der Bericht authentifiziert die Bindung nicht.',
            ),
          ],
        ],
      ),
    );
  }

  Widget _edge(
    BuildContext context,
    Map<String, dynamic> e,
    Map<String, Map<String, dynamic>> byId,
    dynamic id,
  ) {
    final incoming = e['to'] == id;
    final otherId = _show(incoming ? e['from'] : e['to']);
    final other = byId[otherId];
    return Card.outlined(
      child: ListTile(
        title: Text(
          '${incoming ? 'Von' : 'Zu'} ${other == null ? 'nicht aufgelöst: $otherId' : _show(other['name'])}',
        ),
        subtitle: Text(
          '${_show(e['type'])} · Status berichtet: ${_show(e['status'])}\n'
          'Belegebene: ${e['status'] == 'geplant'
              ? 'Plan (berichtet)'
              : e['type'] == 'lokale Paketabhängigkeit' || e['type'] == 'deklariertes Cargo-Binärziel'
              ? 'Manifestdeklaration (berichtet)'
              : 'nicht ausgewiesen'}\n'
          '${_show(e['detail'])}\nQuelle: ${_show(e['evidence'])} · Revision: ${_show(e['source_revision'])}\nHerkunft: ${_show(e['origin'] ?? widget.data['source_id'])}',
        ),
        trailing: other == null ? null : const Icon(Icons.chevron_right),
        onTap: other == null ? null : () => widget.onSelect(otherId),
      ),
    );
  }

  Widget _caseLink(BuildContext context, Map<String, dynamic> a) {
    final caseId = _show(a['case_id']);
    final candidate = _show(a['candidate']);
    final top = widget.currentAssessment;
    final current = top['schema'] == 'aethel.plm.assessment/v1'
        ? _map(top['change'])
        : top['schema'] == 'aethel.plm.linked-assessment/v1'
        ? _map(_map(top['change'])?['change'])
        : null;
    final currentId = current?['id'];
    final currentCandidate = current?['candidate'];
    final comparison = currentId != caseId
        ? 'Ein anderer Fall ist geöffnet; keine automatische Zuordnung.'
        : currentCandidate == null
        ? 'Kandidat des geöffneten Falls ist unbekannt.'
        : currentCandidate != candidate
        ? 'Kandidat abweichend: historische Belege sind nicht dem geöffneten Kandidaten zugeordnet.'
        : 'Kandidatenangabe stimmt überein; Herkunft und Autorität sind nicht geprüft.';
    final hasExample =
        caseId == 'Y-1' &&
        candidate == 'c1b0c46cbae60a69a00332a050841044e64b32e1';
    final snapshot = _map(a['snapshot']);
    final claims = _maps(a['claims']);
    final followups = _maps(a['followups']);
    return Padding(
      padding: const EdgeInsets.only(bottom: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Fall $caseId · ${snapshot?['kind'] == 'historical' ? 'historisch: ${_show(snapshot?['captured_on'])}' : 'Zeitbezug unbekannt'}',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          SelectableText('Kandidat: $candidate'),
          Text(
            'Quelle: ${_show(a['case_source'])} · Identität und Quelle nicht verifiziert.',
          ),
          Text(comparison, key: const Key('candidate-comparison')),
          if (hasExample)
            TextButton.icon(
              onPressed: widget.onOpenY1,
              icon: const Icon(Icons.open_in_new),
              label: const Text('Y-1 öffnen'),
            )
          else
            const Text(
              'Eine Auswertung zu diesem Bezug ist nicht eingebunden.',
            ),
          ExpansionTile(
            title: const Text('Fallbezogene Befunde und nächste Schritte'),
            children: [
              if (claims.isEmpty)
                const ListTile(
                  title: Text('Fallbefunde nicht übergeben; nicht geprüft.'),
                ),
              for (final claim in claims) ...[
                ListTile(
                  title: Text(
                    '${_show(claim['statement'])} · Belegart: ${_show(claim['required_kind'])}',
                  ),
                  subtitle: Text(
                    _maps(claim['gaps']).isEmpty
                        ? 'Keine deklarierten Lücken; Quelle und Autorität bleiben ungeprüft.'
                        : _maps(claim['gaps'])
                              .map(
                                (g) =>
                                    '${_show(g['code'])}: ${_show(g['explanation'])}',
                              )
                              .join('\n'),
                  ),
                ),
                for (final f in followups.where(
                  (f) => f['claim_id'] == claim['id'],
                ))
                  ListTile(
                    dense: true,
                    title: Text(
                      'Nächster Schritt (Stand ${_show(f['as_of'])}): ${_show(f['next_step'])}',
                    ),
                    subtitle: Text(
                      'Zuständige Quelle: ${_show(f['responsible_source'])}',
                    ),
                  ),
                if (!followups.any((f) => f['claim_id'] == claim['id']))
                  const ListTile(
                    dense: true,
                    title: Text(
                      'Zuständige Quelle und nächster Schritt nicht angegeben.',
                    ),
                  ),
              ],
            ],
          ),
        ],
      ),
    );
  }
}
