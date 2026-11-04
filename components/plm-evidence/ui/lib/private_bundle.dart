import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:file_selector/file_selector.dart';
import 'package:flutter/material.dart';
import 'private_history.dart';

const privateBundleFiles = <String, String>{
  'coverage.json': 'Chatabdeckung und Prüfliste',
  'projektbezuege-kandidaten.json': 'Projektbezüge aus Chats · ungeprüft',
  'y1-arbeitsabgleich.json': 'aethelBrowser Y-1',
  'aix-projects-arbeitsabgleich.json': 'AIX und aethelProjects',
  'konzeptbefunde-k01-k08.json': 'Konzeptbefunde K-01 bis K-08',
  'review-umsetzungs-und-projektmatrix.json': 'Review- und Projektmatrix',
  'code-review-weiterer-bestand.json': 'Code-Review und Bestand',
  'analytics-und-projektfindung.json': 'Analytics und Projektfindung',
  'aiderdesktop-claude-abgleich.json': 'aiderDesktop-Abgleich',
  'review-pr-status-aktuell.json': 'PR-Stände und offene Prüfungen',
};

/// Last good document is retained on failure, and each source has an error.
Future<
  ({Map<String, Map<String, dynamic>> documents, Map<String, String> errors})
>
readPrivateBundle(
  String directory,
  Map<String, Map<String, dynamic>> previous,
) async {
  final next = Map<String, Map<String, dynamic>>.from(previous);
  final errors = <String, String>{};
  for (final name in privateBundleFiles.keys) {
    try {
      final path = '$directory/$name';
      if (await FileSystemEntity.type(path, followLinks: false) !=
          FileSystemEntityType.file) {
        throw const FormatException();
      }
      final file = File(path);
      if (await file.length() > 8 * 1024 * 1024) throw const FormatException();
      final raw = await file.readAsString();
      if (utf8.encode(raw).length > 8 * 1024 * 1024) {
        throw const FormatException();
      }
      final value = jsonDecode(raw);
      if (value is! Map<String, dynamic>) throw const FormatException();
      next[name] = value;
    } catch (_) {
      errors[name] = 'Nicht lesbar, fehlt oder ungültig';
    }
  }
  return (documents: next, errors: errors);
}

/// A user-selected private directory; never scans workspaces or starts services.
class PrivateBundlePanel extends StatefulWidget {
  const PrivateBundlePanel({
    super.key,
    required this.single,
    required this.singleStatus,
  });
  final Map<String, dynamic>? single;
  final String singleStatus;
  @override
  State<PrivateBundlePanel> createState() => _PrivateBundlePanelState();
}

class _PrivateBundlePanelState extends State<PrivateBundlePanel> {
  String? directory;
  Timer? timer;
  int generation = 0;
  bool loading = false;
  String status = 'Kein privater Ordner ausgewählt';
  Map<String, Map<String, dynamic>> docs = {};
  Map<String, String> failures = {};

  @override
  void dispose() {
    generation++;
    timer?.cancel();
    super.dispose();
  }

  Future<void> choose() async {
    final chosen = await getDirectoryPath(
      confirmButtonText: 'Privaten Ordner öffnen',
    );
    if (chosen == null || !mounted) return;
    timer?.cancel();
    final current = ++generation;
    loading = false;
    setState(() {
      directory = chosen;
      docs = {};
      failures = {};
      status = 'Ordner wird gelesen';
    });
    await refresh(current);
    if (mounted && generation == current) {
      timer = Timer.periodic(
        const Duration(seconds: 30),
        (_) => refresh(current),
      );
    }
  }

  Future<void> refresh(int current) async {
    if (loading || directory == null || generation != current) return;
    loading = true;
    final result = await readPrivateBundle(directory!, docs);
    if (mounted && generation == current) {
      setState(() {
        docs = result.documents;
        failures = result.errors;
        status =
            'Ordner gelesen: ${DateTime.now().toLocal()} · Quellenstand separat prüfen';
      });
      loading = false;
    }
  }

  @override
  Widget build(BuildContext context) => Column(
    children: [
      Padding(
        padding: const EdgeInsets.all(12),
        child: Wrap(
          spacing: 12,
          children: [
            FilledButton.tonalIcon(
              onPressed: choose,
              icon: const Icon(Icons.folder_open),
              label: const Text('Privaten Ordner öffnen'),
            ),
            Text(status),
          ],
        ),
      ),
      const Padding(
        padding: EdgeInsets.symmetric(horizontal: 12),
        child: Text(
          'Dateien werden alle 30 Sekunden neu gelesen. Es werden keine neuen Scans erzeugt; Inhalte und Freigaben bleiben ungeprüft.',
        ),
      ),
      Expanded(
        child: directory == null
            ? PrivateHistoryPanel(
                data: widget.single,
                status: widget.singleStatus,
              )
            : ListView.builder(
                itemCount: privateBundleFiles.length,
                itemBuilder: (context, index) {
                  final name = privateBundleFiles.keys.elementAt(index);
                  final data = docs[name];
                  return ExpansionTile(
                    title: Text(privateBundleFiles[name]!),
                    subtitle: Text(
                      failures[name] == null
                          ? (data == null
                                ? 'Noch nicht geladen'
                                : 'Quelle: $name · Stand: ${data['observed_at'] ?? 'unbekannt'}')
                          : '${failures[name]}${data == null ? '' : ' · letzter Stand möglicherweise veraltet'}',
                    ),
                    children: data == null
                        ? []
                        : [PrivateDocumentView(name: name, data: data)],
                  );
                },
              ),
      ),
    ],
  );
}

class PrivateDocumentView extends StatelessWidget {
  const PrivateDocumentView({
    super.key,
    required this.name,
    required this.data,
  });
  final String name;
  final Map<String, dynamic> data;
  @override
  Widget build(BuildContext context) {
    final entries = data.entries
        .where(
          (e) =>
              e.key != 'sources' &&
              e.key != 'chat_evidence' &&
              e.key != 'pair_counts',
        )
        .toList();
    final pairs = data['pair_counts'];
    final evidence = data['chat_evidence'];
    final sources = data['sources'];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ...entries.map(
          (e) => ExpansionTile(
            title: Text(e.key),
            children: [
              Padding(
                padding: const EdgeInsets.all(12),
                child: SelectableText(
                  const JsonEncoder.withIndent('  ').convert(e.value),
                ),
              ),
            ],
          ),
        ),
        if (pairs is List)
          ExpansionTile(
            title: Text('Beziehungskandidaten (${pairs.length})'),
            subtitle: const Text(
              'Gemeinsame Nennung ist keine bestätigte Beziehung',
            ),
            children: pairs
                .take(100)
                .map((e) => ListTile(title: SelectableText(jsonEncode(e))))
                .toList(),
          ),
        if (pairs is List && pairs.length > 100)
          const Text(
            'Erste 100 Kandidaten angezeigt; vollständige Liste in der privaten Quelldatei.',
          ),
        if (name == 'projektbezuege-kandidaten.json' && sources is List)
          PrivateSourceSearch(sources: sources),
        if (evidence is List)
          ExpansionTile(
            title: Text('Chatbelege (${evidence.length})'),
            children: evidence
                .whereType<Map<String, dynamic>>()
                .map(
                  (e) => ExpansionTile(
                    title: Text(
                      '${e['actor'] ?? 'unbekannt'} · Zeile ${e['line'] ?? '?'}',
                    ),
                    subtitle: Text('${e['source'] ?? 'Quelle unbekannt'}'),
                    children: [SelectableText('${e['preview'] ?? ''}')],
                  ),
                )
                .toList(),
          ),
      ],
    );
  }
}

class PrivateSourceSearch extends StatefulWidget {
  const PrivateSourceSearch({super.key, required this.sources});
  final List<dynamic> sources;
  @override
  State<PrivateSourceSearch> createState() => _PrivateSourceSearchState();
}

class _PrivateSourceSearchState extends State<PrivateSourceSearch> {
  String query = '';
  @override
  Widget build(BuildContext context) {
    final matches = widget.sources.whereType<Map<String, dynamic>>().where((
      item,
    ) {
      final text = jsonEncode(item).toLowerCase();
      return query.isEmpty || text.contains(query.toLowerCase());
    }).toList();
    return ExpansionTile(
      title: Text('Quellverweise (${widget.sources.length})'),
      subtitle: const Text(
        'Namen und Zeilen sind ungeprüfte Hinweise, keine Aufgaben oder Identitätsnachweise.',
      ),
      children: [
        TextField(
          decoration: const InputDecoration(
            labelText: 'Projekt oder Quelle suchen',
          ),
          onChanged: (v) => setState(() => query = v.trim()),
        ),
        Text('${matches.length} Treffer · höchstens 100 angezeigt'),
        ...matches
            .take(100)
            .map(
              (item) => ListTile(
                title: SelectableText(
                  '${item['source'] ?? 'Quelle unbekannt'}',
                ),
                subtitle: SelectableText(jsonEncode(item['names'] ?? {})),
              ),
            ),
      ],
    );
  }
}
