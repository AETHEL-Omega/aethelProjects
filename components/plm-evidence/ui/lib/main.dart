import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:aethel_evidence_bridge/aethel_evidence_bridge.dart';
import 'package:flutter_rust_bridge/flutter_rust_bridge_for_generated.dart'
    show ExternalLibrary;
import 'package:file_selector/file_selector.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'landscape.dart';
import 'product_home.dart';
import 'source_adapters.dart';
import 'aix_live.dart';
import 'projects_file.dart';
import 'private_history.dart';
import 'private_bundle.dart';
import 'inventory_panel.dart';

void main() => runApp(const AethelPlm());

class AethelPlm extends StatelessWidget {
  const AethelPlm({
    super.key,
    this.initialJson,
    this.initialLandscapeJson,
    this.initialLandingJson,
  });
  final String? initialJson;
  final String? initialLandscapeJson;
  final String? initialLandingJson;
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'AETHEL Arbeitsraum',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(
      colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xff27566a)),
      useMaterial3: true,
    ),
    home: Workspace(
      initialJson: initialJson,
      initialLandscapeJson: initialLandscapeJson,
      initialLandingJson: initialLandingJson,
    ),
  );
}

/// Displays an assessment, never calculates or grants a verdict.
class Workspace extends StatefulWidget {
  const Workspace({
    super.key,
    this.initialJson,
    this.initialLandscapeJson,
    this.initialLandingJson,
  });
  final String? initialJson;
  final String? initialLandscapeJson;
  final String? initialLandingJson;
  @override
  State<Workspace> createState() => _WorkspaceState();
}

class _WorkspaceState extends State<Workspace> {
  Map<String, dynamic>? document;
  String? rawCase;
  Future<void>? nativeEvidenceInitialization;
  Map<String, dynamic>? landscape;
  Map<String, dynamic>? cockpit;
  Map<String, dynamic>? privateHistory;
  Map<String, dynamic>? liveInventory;
  XFile? inventoryFile;
  Timer? inventoryTimer;
  int inventoryGeneration = 0;
  bool inventoryLoading = false;
  String inventoryStatus = 'Inventurquelle noch nicht verbunden';
  static const inventoryChannel = MethodChannel('aethel.projects.inventory/v1');
  final Map<String, Map<String, dynamic>> sessionAnalyses = {};
  bool analysisRunning = false;
  String analysisStatus = '';
  XFile? privateFile;
  Timer? privateTimer;
  int privateGeneration = 0;
  bool privateLoading = false;
  String privateStatus = 'Keine private Erfassung ausgewählt';
  Timer? projectsTimer;
  XFile? projectsFile;
  int projectsGeneration = 0;
  bool projectsLoading = false;
  String projectsStatus = 'Mitgelieferte historische Momentaufnahme';
  Map<String, dynamic>? aixDashboard;
  Map<String, dynamic>? aixOrders;
  String aixOrdersStatus = 'AIX-Auftragsquelle nicht verbunden';
  Timer? aixTimer;
  int aixGeneration = 0;
  bool aixLoading = false;
  String aixStatus = 'Nicht verbunden';
  Map<String, dynamic>? factoryInput;
  String landscapeOrigin = 'Historische Recherche · Pfade pseudonymisiert';
  String? selectedLandscapeId;
  int landscapeGeneration = 0;
  final Map<String, int> boundProjectSources = {};
  final Map<String, int> boundLandingSources = {};
  final List<SourceItem> sources = [];
  String origin = 'Kein Dokument geöffnet';
  String? error;
  int section = 7;

  @override
  void initState() {
    super.initState();
    _loadCockpit();
    _restoreInventoryDirectory();
    if (widget.initialLandscapeJson == null) {
      _loadLandscape();
    } else {
      _setDocument(
        widget.initialLandscapeJson!,
        'Übergebene Landschaft',
        navigate: false,
      );
    }
    if (widget.initialLandingJson == null) {
      _loadLandingExample();
    } else {
      _setDocument(
        widget.initialLandingJson!,
        'Y-1 PR 1518 · Landing-Leseprobe 04.11.',
        navigate: false,
      );
    }
    if (widget.initialJson != null) {
      _setDocument(
        widget.initialJson!,
        'Übergebene Auswertung',
        navigate: false,
      );
    } else {
      _example(
        'assets/y1-assessment.json',
        'Historischer Pilot Y-1',
        navigate: false,
      );
    }
  }

  @override
  void dispose() {
    aixTimer?.cancel();
    projectsTimer?.cancel();
    privateTimer?.cancel();
    inventoryTimer?.cancel();
    super.dispose();
  }

  Future<void> _initializeNativeEvidence() async {
    if (!Platform.isMacOS) {
      throw UnsupportedError('Native Bibliothek nicht verfügbar');
    }
    final executable = File(Platform.resolvedExecutable).parent.parent.path;
    await RustLib.init(
      externalLibrary: ExternalLibrary.open(
        '$executable/Frameworks/libaethel_evidence_bridge.dylib',
      ),
    );
  }

  Future<void> _analyzeProject(String identity, String path) async {
    if (analysisRunning) return;
    setState(() {
      analysisRunning = true;
      analysisStatus = 'Analyse läuft';
    });
    try {
      final raw = await inventoryChannel.invokeMethod<String>(
        'analyzeProject',
        {'path': path},
      );
      if (raw == null) {
        if (mounted) setState(() => analysisStatus = 'Analyse abgebrochen');
        return;
      }
      final value = jsonDecode(raw);
      if (value is! Map<String, dynamic> ||
          value['schema'] != 'aethel.code_analyzer.aix_findings.v1' ||
          value['scope'] != path ||
          value['findings'] is! List ||
          value['scan'] is! Map) {
        throw const FormatException(
          'Ungültiger Analysebericht oder abweichender Projektpfad',
        );
      }
      final scan = value['scan'] as Map;
      final findings = (value['findings'] as List)
          .whereType<Map>()
          .take(100)
          .map(
            (row) => {
              for (final key in [
                'file',
                'line',
                'rule',
                'severity',
                'message',
                'evidence_tier',
                'kind',
              ])
                key: row[key],
            },
          )
          .toList();
      if (mounted) {
        setState(() {
          sessionAnalyses[identity] = {
            'observed_at': DateTime.now().toUtc().toIso8601String(),
            'checkout': path,
            'source_state':
                'Sitzungsergebnis · Quellenänderung nicht automatisch geprüft',
            'reported_finding_count': (value['findings'] as List).length,
            'incomplete_reasons': scan['incomplete_reasons'],
            'stub_coverage': scan['stub_coverage'],
            'truncated': value['truncated'],
            'findings': findings,
          };
          analysisStatus = 'Analyse beendet · nur für diese Sitzung';
        });
      }
    } on PlatformException catch (e) {
      if (mounted) {
        setState(() => analysisStatus = e.message ?? 'Analyse nicht verfügbar');
      }
    } catch (_) {
      if (mounted) {
        setState(
          () => analysisStatus = 'Analysebericht ungültig oder nicht verfügbar',
        );
      }
    } finally {
      if (mounted) setState(() => analysisRunning = false);
    }
  }

  void _startAix() {
    aixTimer?.cancel();
    _refreshAix();
    aixTimer = Timer.periodic(
      const Duration(seconds: 30),
      (_) => _refreshAix(),
    );
  }

  void _stopAix() {
    aixTimer?.cancel();
    aixTimer = null;
    aixGeneration++;
    aixLoading = false;
    setState(() {
      aixStatus = 'Verbindung beendet; letzter Stand nicht aktuell';
      aixOrders = null;
      aixOrdersStatus = 'AIX-Verbindung beendet';
    });
  }

  Future<void> _refreshAix() async {
    if (aixLoading) return;
    aixLoading = true;
    final generation = ++aixGeneration;
    if (mounted) setState(() => aixStatus = 'AIX wird abgefragt');
    try {
      final data = await readLocalAix();
      Map<String, dynamic>? orders;
      String orderStatus;
      try {
        orders = await readLocalAixOrders();
        orderStatus = 'AIX-Auftragsquelle aktualisiert';
      } catch (_) {
        orderStatus =
            'AIX-Auftragsquelle nicht erreichbar oder nicht bereitgestellt';
      }
      if (mounted && generation == aixGeneration) {
        setState(() {
          aixDashboard = data;
          aixOrders = orders;
          aixOrdersStatus = orderStatus;
          aixStatus = 'Automatisch aktualisiert · alle 30 Sekunden';
        });
      }
    } catch (_) {
      if (mounted && generation == aixGeneration) {
        setState(() {
          aixStatus =
              'AIX nicht erreichbar oder ungültig · letzter Stand möglicherweise veraltet';
          aixOrders = null;
          aixOrdersStatus = 'AIX-Auftragsquelle nicht erreichbar';
        });
      }
    } finally {
      if (generation == aixGeneration) aixLoading = false;
    }
  }

  void _stopProjects() {
    projectsTimer?.cancel();
    projectsTimer = null;
    projectsFile = null;
    projectsGeneration++;
    projectsLoading = false;
    setState(
      () =>
          projectsStatus = 'Automatisches Neulesen beendet; letzter Dateistand',
    );
  }

  void _watchProjects(XFile file, Map<String, dynamic> initial) {
    projectsTimer?.cancel();
    projectsGeneration++;
    projectsLoading = false;
    projectsFile = file;
    setState(() {
      cockpit = initial;
      projectsStatus =
          'Ausgewählte Datei · automatisches Neulesen alle 30 Sekunden';
      section = 0;
      error = null;
    });
    projectsTimer = Timer.periodic(
      const Duration(seconds: 30),
      (_) => _refreshProjects(),
    );
  }

  Future<void> _refreshProjects() async {
    final file = projectsFile;
    if (file == null || projectsLoading) return;
    projectsLoading = true;
    final generation = ++projectsGeneration;
    try {
      final value = await readProjectsFile(file);
      if (mounted && generation == projectsGeneration) {
        setState(() {
          cockpit = value;
          projectsStatus =
              'Datei erneut gelesen · Datenalter durch Projects-Quelle bestimmt';
        });
      }
    } catch (_) {
      if (mounted && generation == projectsGeneration) {
        setState(
          () => projectsStatus =
              'Datei nicht lesbar oder ungültig · letzter Stand möglicherweise veraltet',
        );
      }
    } finally {
      if (generation == projectsGeneration) projectsLoading = false;
    }
  }

  Future<void> _loadCockpit() async {
    try {
      final value = jsonDecode(
        await rootBundle.loadString('assets/cockpit-2026-11-03.json'),
      );
      if (value is! Map<String, dynamic>) throw const FormatException();
      validateShape(value);
      if (mounted && cockpit == null) setState(() => cockpit = value);
    } catch (_) {
      if (mounted) {
        setState(
          () => error = 'Projects-Leitstand konnte nicht geladen werden.',
        );
      }
    }
  }

  Future<void> _loadLandingExample() async {
    try {
      final value = jsonDecode(
        await rootBundle.loadString('assets/y1-landing-observation.json'),
      );
      if (value is! Map<String, dynamic>) throw const FormatException();
      validateShape(value);
      if (mounted) {
        setState(
          () => sources.add(
            SourceItem('Y-1 PR 1518 · Landing-Leseprobe 04.11.', value),
          ),
        );
      }
    } catch (_) {
      if (mounted) {
        setState(
          () => error = 'Landing-Leseprobe konnte nicht geladen werden.',
        );
      }
    }
  }

  Future<void> _loadLandscape() async {
    final generation = landscapeGeneration;
    try {
      final value = jsonDecode(
        await rootBundle.loadString('assets/landscape-historical.json'),
      );
      if (value is! Map<String, dynamic>) throw const FormatException();
      validateShape(value);
      if (mounted && generation == landscapeGeneration) {
        setState(() => landscape = value);
      }
    } catch (_) {
      if (mounted && generation == landscapeGeneration) {
        setState(
          () => error = 'Projektlandschaft konnte nicht geladen werden.',
        );
      }
    }
  }

  Future<void> _example(
    String asset,
    String title, {
    bool navigate = true,
  }) async {
    try {
      _setDocument(
        await rootBundle.loadString(asset),
        title,
        navigate: navigate,
      );
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
      final value = jsonDecode(content);
      if (value is Map<String, dynamic> &&
          value['schema'] == 'aethel.projects.inventory-live/v1') {
        _watchInventory(file, value);
      } else if (value is Map<String, dynamic> && isPrivateHistory(value)) {
        _watchPrivate(file, value);
      } else if (value is Map<String, dynamic> &&
          value['schema'] == 'aethel.projects.cockpit/v1') {
        final initial = readCockpit(value, 'Datei: ${file.name}');
        if (mounted) _watchProjects(file, initial);
      } else {
        _setDocument(content, 'Datei: ${file.name}');
      }
    } catch (_) {
      if (mounted) {
        setState(
          () => error = 'Datei konnte nicht geöffnet werden oder ist zu groß.',
        );
      }
    }
  }

  Future<void> _restoreInventoryDirectory() async {
    try {
      final directory = await inventoryChannel.invokeMethod<String>(
        'restoreDirectory',
      );
      if (!mounted || directory == null || inventoryFile != null) return;
      _watchInventory(
        XFile('$directory/inventory.json'),
        null,
        navigate: false,
      );
    } catch (_) {
      if (mounted) {
        setState(() => inventoryStatus = 'Inventurordner erneut auswählen');
      }
    }
  }

  Future<void> _chooseInventoryDirectory() async {
    try {
      final directory = await inventoryChannel.invokeMethod<String>(
        'chooseDirectory',
      );
      if (!mounted || directory == null) return;
      _watchInventory(XFile('$directory/inventory.json'), null);
    } catch (_) {
      if (mounted) {
        setState(
          () => inventoryStatus =
              'Inventurordner nicht verfügbar oder nicht freigegeben',
        );
      }
    }
  }

  void _watchInventory(
    XFile file,
    Map<String, dynamic>? initial, {
    bool navigate = true,
  }) {
    if (initial != null) validateInventory(initial);
    inventoryTimer?.cancel();
    inventoryFile = file;
    final generation = ++inventoryGeneration;
    inventoryLoading = false;
    setState(() {
      if (initial != null) liveInventory = initial;
      if (navigate) section = 7;
      inventoryStatus = 'Inventurquelle verbunden · Neulesen alle 30 Sekunden';
      error = null;
    });
    Future<void> refresh() async {
      if (inventoryLoading) return;
      inventoryLoading = true;
      try {
        if (await file.length() > 8 * 1024 * 1024) {
          throw const FormatException();
        }
        final raw = await file.readAsString();
        if (utf8.encode(raw).length > 8 * 1024 * 1024) {
          throw const FormatException();
        }
        final value = jsonDecode(raw);
        if (value is! Map<String, dynamic>) throw const FormatException();
        validateInventory(value);
        if (mounted && generation == inventoryGeneration) {
          setState(() {
            liveInventory = value;
            inventoryStatus =
                'Quelle verbunden · Scannerstand und Fehler beachten';
          });
        }
      } catch (_) {
        if (mounted && generation == inventoryGeneration) {
          setState(
            () => inventoryStatus =
                'Inventurquelle nicht erreichbar · letzter Stand möglicherweise veraltet',
          );
        }
      } finally {
        if (generation == inventoryGeneration) inventoryLoading = false;
      }
    }

    refresh();
    inventoryTimer = Timer.periodic(
      const Duration(seconds: 30),
      (_) => refresh(),
    );
  }

  void _watchPrivate(XFile file, Map<String, dynamic> value) {
    validatePrivateHistory(value);
    privateTimer?.cancel();
    privateFile = file;
    final generation = ++privateGeneration;
    privateLoading = false;
    setState(() {
      privateHistory = value;
      privateStatus = 'Private Datei ausgewählt · Neulesen alle 30 Sekunden';
      section = 6;
      error = null;
    });
    privateTimer = Timer.periodic(const Duration(seconds: 30), (_) async {
      if (privateLoading) return;
      privateLoading = true;
      try {
        if (await file.length() > 8 * 1024 * 1024) {
          throw const FormatException();
        }
        final raw = await file.readAsString();
        if (utf8.encode(raw).length > 8 * 1024 * 1024) {
          throw const FormatException();
        }
        final value = jsonDecode(raw);
        if (value is! Map<String, dynamic>) throw const FormatException();
        validatePrivateHistory(value);
        if (mounted && generation == privateGeneration) {
          setState(() {
            privateHistory = value;
            privateStatus =
                'Datei erneut gelesen · Erfassung kann veraltet sein';
          });
        }
      } catch (_) {
        if (mounted && generation == privateGeneration) {
          setState(
            () => privateStatus =
                'Datei nicht lesbar · letzter Stand möglicherweise veraltet',
          );
        }
      } finally {
        if (generation == privateGeneration) privateLoading = false;
      }
    });
  }

  void _setDocument(String content, String title, {bool navigate = true}) {
    try {
      final value = jsonDecode(content);
      if (value is! Map<String, dynamic>) {
        throw const FormatException();
      }
      if (value['schema'] == 'aethel.projects.cockpit/v1') {
        final adapted = readCockpit(value, title);
        if (mounted) {
          setState(() {
            cockpit = adapted;
            section = 0;
            error = null;
          });
        }
        return;
      }
      if (value['schema'] == 'aix.dashboard.v2') {
        final adapted = readAixDashboard(value, title);
        aixTimer?.cancel();
        aixTimer = null;
        aixGeneration++;
        aixLoading = false;
        if (mounted) {
          setState(() {
            aixDashboard = adapted;
            aixStatus =
                'Manuell geöffnete Datei · keine automatische Aktualisierung';
            section = 0;
            error = null;
          });
        }
        return;
      }
      if (value['schema'] == 'aix.engineering_input.v1') {
        final adapted = readFactoryInput(value, title);
        if (mounted) {
          setState(() {
            factoryInput = adapted;
            section = 0;
            error = null;
          });
        }
        return;
      }
      if (value['schema'] == 'aethel.plm.case/v1') {
        if (utf8.encode(content).length > 8 * 1024 * 1024) {
          throw const FormatException();
        }
        if (mounted) {
          setState(() {
            rawCase = content;
            document = null;
            origin = title;
            if (navigate) section = 2;
            error = null;
          });
        }
        return;
      }
      if (!supported.contains(value['schema'])) {
        throw const FormatException();
      }
      validateShape(value);
      if (mounted) {
        setState(() {
          if (value['schema'] == 'aethel.plm.cockpit-observation/v1') {
            projectsTimer?.cancel();
            projectsTimer = null;
            projectsFile = null;
            projectsGeneration++;
            projectsLoading = false;
            projectsStatus =
                'Manuell geöffnete Projektion · kein automatisches Neulesen';
            cockpit = value;
            if (navigate) section = 0;
          } else if (value['schema'] == 'aethel.plm.landscape-projection/v1') {
            landscapeGeneration++;
            landscape = value;
            landscapeOrigin = title;
            selectedLandscapeId = null;
            boundProjectSources.clear();
            boundLandingSources.clear();
            if (navigate) section = 1;
          } else if (value['schema'] == 'aethel.plm.project-observation/v1' ||
              value['schema'] == 'aethel.plm.copilot-observation/v1' ||
              value['schema'] == 'aethel.plm.landing-observation/v1') {
            sources.add(SourceItem(title, value));
            if (navigate) section = 5;
          } else {
            document = value;
            rawCase = null;
            origin = title;
            if (navigate) section = 2;
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
    final data = document ?? <String, dynamic>{};
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
              section == 0 || section == 1
                  ? '$landscapeOrigin · Lesende Ansicht · Angaben nicht live geprüft'
                  : '$origin · Lesende Ansicht · Quelle und Autorität nicht geprüft',
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
          if (document == null && rawCase == null)
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
                              SingleChildScrollView(
                                scrollDirection: Axis.horizontal,
                                child: SegmentedButton<int>(
                                  segments: const [
                                    ButtonSegment(
                                      value: 0,
                                      label: Text('Produkte'),
                                    ),
                                    ButtonSegment(
                                      value: 1,
                                      label: Text('Landschaft'),
                                    ),
                                    ButtonSegment(
                                      value: 2,
                                      label: Text('Änderung'),
                                    ),
                                    ButtonSegment(
                                      value: 3,
                                      label: Text('Qualität'),
                                    ),
                                    ButtonSegment(
                                      value: 4,
                                      label: Text('Zusammenhang'),
                                    ),
                                    ButtonSegment(
                                      value: 5,
                                      label: Text('Quelle'),
                                    ),
                                    ButtonSegment(
                                      value: 6,
                                      label: Text('Privat'),
                                    ),
                                    ButtonSegment(
                                      value: 7,
                                      label: Text('Projekte aktuell'),
                                    ),
                                  ],
                                  selected: {section},
                                  onSelectionChanged: (v) =>
                                      setState(() => section = v.first),
                                ),
                              ),
                            Expanded(
                              child: IndexedStack(
                                index: section == 6
                                    ? 1
                                    : (section == 7 ? 2 : 0),
                                children: [
                                  SingleChildScrollView(
                                    padding: const EdgeInsets.all(24),
                                    child: Center(
                                      child: ConstrainedBox(
                                        constraints: const BoxConstraints(
                                          maxWidth: 1100,
                                        ),
                                        child: switch (section) {
                                          0 => ProductHome(
                                            cockpit: cockpit,
                                            projectsStatus: projectsStatus,
                                            onProjectsStop: projectsFile == null
                                                ? null
                                                : _stopProjects,
                                            aixDashboard: aixDashboard,
                                            aixStatus: aixStatus,
                                            aixConnected: aixTimer != null,
                                            onAixConnect: _startAix,
                                            onAixDisconnect: _stopAix,
                                            factoryInput: factoryInput,
                                            onOpenY1: () => _example(
                                              'assets/y1-assessment.json',
                                              'Historischer Pilot Y-1',
                                            ),
                                            onLandscape: () =>
                                                setState(() => section = 1),
                                          ),
                                          1 =>
                                            landscape == null
                                                ? const EmptyPanel(
                                                    'Keine Projektlandschaft geladen.',
                                                  )
                                                : LandscapePanel(
                                                    data: landscape!,
                                                    origin: landscapeOrigin,
                                                    currentAssessment: data,
                                                    selectedId:
                                                        selectedLandscapeId,
                                                    sources: [
                                                      for (final s in sources)
                                                        {
                                                          'name': s.name,
                                                          'data': s.data,
                                                        },
                                                    ],
                                                    selectedSourceIndex:
                                                        boundProjectSources[selectedLandscapeId],
                                                    onBindSource: (index) =>
                                                        setState(
                                                          () =>
                                                              boundProjectSources[selectedLandscapeId!] =
                                                                  index,
                                                        ),
                                                    selectedLandingIndex:
                                                        boundLandingSources[selectedLandscapeId],
                                                    onBindLanding: (index) =>
                                                        setState(
                                                          () =>
                                                              boundLandingSources[selectedLandscapeId!] =
                                                                  index,
                                                        ),
                                                    onSelect: (id) => setState(
                                                      () =>
                                                          selectedLandscapeId =
                                                              id,
                                                    ),
                                                    onOpenY1: () => _example(
                                                      'assets/y1-assessment.json',
                                                      'Historischer Pilot Y-1',
                                                    ),
                                                  ),
                                          2 =>
                                            rawCase == null
                                                ? ChangePanel(data: data)
                                                : FutureBuilder<void>(
                                                    future: nativeEvidenceInitialization ??=
                                                        _initializeNativeEvidence(),
                                                    builder: (context, snapshot) {
                                                      if (snapshot
                                                              .connectionState !=
                                                          ConnectionState.done) {
                                                        return const Center(
                                                          child:
                                                              CircularProgressIndicator(),
                                                        );
                                                      }
                                                      if (snapshot.hasError) {
                                                        return const EmptyPanel(
                                                          'Native Rust-Auswertung nicht verfügbar.',
                                                        );
                                                      }
                                                      return EvidencePanel(
                                                        caseJson: rawCase!,
                                                      );
                                                    },
                                                  ),
                                          3 => QualityPanel(data: data),
                                          4 => TracePanel(data: data),
                                          _ => SourcePanel(
                                            data: data,
                                            sources: sources,
                                          ),
                                        },
                                      ),
                                    ),
                                  ),
                                  PrivateBundlePanel(
                                    single: privateHistory,
                                    singleStatus: privateStatus,
                                  ),
                                  InventoryPanel(
                                    data: liveInventory,
                                    status: inventoryStatus,
                                    orders: aixOrders,
                                    orderStatus: aixOrdersStatus,
                                    analyses: sessionAnalyses,
                                    analysisStatus: analysisStatus,
                                    analysisRunning: analysisRunning,
                                    onAnalyze: _analyzeProject,
                                    onConnectOrders: _startAix,
                                    onChooseSource: _chooseInventoryDirectory,
                                  ),
                                ],
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
    icon: Icon(Icons.dashboard_outlined),
    label: Text('Produkte'),
  ),
  NavigationRailDestination(
    icon: Icon(Icons.grid_view_outlined),
    label: Text('Projektlandschaft'),
  ),
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
  NavigationRailDestination(
    icon: Icon(Icons.lock_outline),
    label: Text('Privat'),
  ),
  NavigationRailDestination(
    icon: Icon(Icons.folder_special_outlined),
    label: Text('Projekte aktuell'),
  ),
];
const supported = {
  'aethel.plm.cockpit-observation/v1',
  'aethel.plm.landscape-projection/v1',
  'aethel.plm.landing-observation/v1',
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
  if (schema == 'aethel.plm.cockpit-observation/v1' &&
      (data['tiles'] is! List ||
          data['missing'] is! List ||
          object(data['sources']) == null)) {
    throw const FormatException();
  }
  if (schema == 'aethel.plm.landscape-projection/v1' &&
      (data['nodes'] is! List ||
          data['edges'] is! List ||
          data['attachments'] is! List ||
          data['unresolved_endpoints'] is! List)) {
    throw const FormatException();
  }
  if (schema == 'aethel.plm.landscape-projection/v1') {
    final identities = <String, Map<String, dynamic>>{};
    for (final entry in data['nodes'] as List) {
      final node = object(entry);
      final id = node?['id'];
      if (id is! String ||
          id.trim().isEmpty ||
          node?['name'] is! String ||
          node?['kind'] is! String ||
          identities.containsKey(id)) {
        throw const FormatException();
      }
      identities[id] = node!;
    }
    for (final entry in data['edges'] as List) {
      final edge = object(entry);
      if (edge == null ||
          ['from', 'to', 'type', 'status', 'evidence', 'detail'].any(
            (key) =>
                edge[key] is! String || (edge[key] as String).trim().isEmpty,
          )) {
        throw const FormatException();
      }
    }
    for (final entry in data['attachments'] as List) {
      final attachment = object(entry);
      final node = identities[attachment?['node_id']];
      if (attachment == null ||
          node?['kind'] != 'repository' ||
          node?['git_common_dir'] is! String ||
          node?['git_common_dir'] != attachment['repository_id'] ||
          attachment['case_id'] is! String ||
          attachment['candidate'] is! String ||
          attachment['claims'] is! List ||
          attachment['followups'] is! List) {
        throw const FormatException();
      }
    }
  }
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
  if (schema == 'aethel.plm.landing-observation/v1' &&
      (data['repository_id'] is! String ||
          data['head_supplied'] is! String ||
          data['reported_ok'] is! bool ||
          data['reported_reason'] is! String ||
          data['reported_verdicts'] is! List)) {
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
        if (data['schema'] == 'aethel.plm.landing-observation/v1') ...[
          Fact('Landing-Kopf (mitgeliefert)', show(data['head_supplied'])),
          Fact(
            'Landing-Ergebnis (berichtet)',
            '${show(data['reported_ok'])} · ${show(data['reported_reason'])}',
          ),
          Fact(
            'Quellenzeit (mitgeliefert)',
            show(data['observed_at_supplied']),
          ),
          const Text(
            'Keine Bestätigung von Quelle, Kandidatenbindung oder Landung.',
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
