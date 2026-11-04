import 'dart:convert';
import 'dart:io';

import 'package:aethel_plm/main.dart';
import 'package:aethel_plm/landscape.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

Map<String, dynamic> load(String file) =>
    jsonDecode(File('assets/$file').readAsStringSync()) as Map<String, dynamic>;

void main() {
  testWidgets(
    'Nuru project ranks before embedded sources; changing search clears stale detail',
    (tester) async {
      tester.view.physicalSize = const Size(1600, 1300);
      tester.view.devicePixelRatio = 2;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      await tester.pumpWidget(
        AethelPlm(
          initialJson: File('assets/y1-assessment.json').readAsStringSync(),
          initialLandscapeJson: File(
            'assets/landscape-historical.json',
          ).readAsStringSync(),
        ),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.text('Projektlandschaft'));
      await tester.pumpAndSettle();
      await tester.enterText(
        find.byKey(const Key('landscape-search')),
        'aethelNuru',
      );
      await tester.pumpAndSettle();
      final project = find.byKey(const ValueKey('node-repo:8f2116efa04affb1'));
      final embedded = find.byKey(const ValueKey('node-repo:4606a176bfd35952'));
      expect(
        tester.getTopLeft(project).dy,
        lessThan(tester.getTopLeft(embedded).dy),
      );
      await tester.ensureVisible(embedded);
      await tester.pumpAndSettle();
      await tester.tap(embedded);
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('landscape-detail')), findsOneWidget);
      await tester.ensureVisible(find.byKey(const Key('landscape-search')));
      await tester.enterText(
        find.byKey(const Key('landscape-search')),
        'aethelema',
      );
      await tester.pumpAndSettle();
      expect(
        find.text(
          'Eintrag auswählen, um Herkunft, Beziehungen und Lücken zu sehen.',
        ),
        findsOneWidget,
      );
    },
  );

  testWidgets(
    'at desktop window width selection and explanation are side by side',
    (tester) async {
      tester.view.physicalSize = const Size(1600, 1300);
      tester.view.devicePixelRatio = 2;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      await tester.pumpWidget(
        AethelPlm(
          initialJson: File('assets/y1-assessment.json').readAsStringSync(),
          initialLandscapeJson: File(
            'assets/landscape-historical.json',
          ).readAsStringSync(),
          initialLandingJson: File(
            'assets/y1-landing-observation.json',
          ).readAsStringSync(),
        ),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.text('Projektlandschaft'));
      await tester.pumpAndSettle();
      await tester.enterText(
        find.byKey(const Key('landscape-search')),
        'aethelema',
      );
      await tester.pumpAndSettle();
      expect(
        find.textContaining('2 Repositorygruppen · 1 Registereintrag'),
        findsOneWidget,
      );
      final result = find.byKey(const ValueKey('node-repo:f7581357c91c83dd'));
      await tester.ensureVisible(result);
      await tester.tap(result);
      await tester.pumpAndSettle();
      expect(
        find.textContaining('Eine im Scan ermittelte Git-Historie'),
        findsOneWidget,
      );
      expect(
        find.textContaining('experimentelle P2P-Kommunikationsbibliothek'),
        findsWidgets,
      );
      expect(find.text('Installierter Stand'), findsOneWidget);
      expect(
        tester.getTopLeft(find.byKey(const Key('landscape-detail'))).dx,
        greaterThan(
          tester.getTopLeft(find.byKey(const Key('landscape-list'))).dx,
        ),
      );
    },
  );

  testWidgets(
    'same-named archive, repository and registry entry explain their difference',
    (tester) async {
      tester.view.physicalSize = const Size(1600, 1300);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      await tester.pumpWidget(
        AethelPlm(
          initialJson: File('assets/y1-assessment.json').readAsStringSync(),
          initialLandscapeJson: File(
            'assets/landscape-historical.json',
          ).readAsStringSync(),
          initialLandingJson: File(
            'assets/y1-landing-observation.json',
          ).readAsStringSync(),
        ),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.text('Projektlandschaft'));
      await tester.pumpAndSettle();
      await tester.enterText(
        find.byKey(const Key('landscape-search')),
        'aethelema',
      );
      await tester.pumpAndSettle();
      expect(
        find.textContaining(
          'Archivpfad: ~/workspace/_archive/_cloned_from_github/aethelema',
        ),
        findsOneWidget,
      );
      expect(
        find.textContaining('Repositorygruppe: ~/workspace/aethelema'),
        findsOneWidget,
      );
      await tester.scrollUntilVisible(
        find.byKey(const ValueKey('node-registry:45c03bd290fea35b')),
        120,
        scrollable: find.descendant(
          of: find.byKey(const Key('landscape-list')),
          matching: find.byType(Scrollable),
        ),
      );
      expect(
        find.textContaining(
          'Eintrag im Workspace-Manifest · kein eigenes Repository',
        ),
        findsOneWidget,
      );
    },
  );

  testWidgets('find Browser, bind reported Landing head, open Y-1 and return', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(1600, 1300);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(
      AethelPlm(
        initialJson: File('assets/y1-assessment.json').readAsStringSync(),
        initialLandscapeJson: File(
          'assets/landscape-historical.json',
        ).readAsStringSync(),
        initialLandingJson: File(
          'assets/y1-landing-observation.json',
        ).readAsStringSync(),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Projektlandschaft'));
    await tester.pumpAndSettle();
    await tester.enterText(
      find.byKey(const Key('landscape-search')),
      'aethelBrowser',
    );
    await tester.pumpAndSettle();
    expect(
      find.textContaining('Einträge · getrennte Identitäten'),
      findsOneWidget,
    );
    await tester.tap(find.byKey(const ValueKey('node-repo:ed4da66dacb79098')));
    await tester.pumpAndSettle();
    expect(find.textContaining('Fall Y-1'), findsOneWidget);
    expect(find.text('Drei Sichten auf Y-1'), findsOneWidget);
    expect(find.textContaining('Firma: Produktentscheidung'), findsOneWidget);
    expect(
      find.textContaining('Fabrik: Ein qualifizierter Arbeitsauftrag'),
      findsOneWidget,
    );
    expect(
      find.textContaining('Produkt: Historischer Codekandidat'),
      findsOneWidget,
    );
    expect(find.textContaining('Von aethelBrowser'), findsWidgets);
    expect(find.textContaining('Zu memoristorCursor'), findsWidgets);
    expect(find.textContaining('Bereiche sind Suchhilfen'), findsOneWidget);
    final bind = find.textContaining('Temporär zuordnen: Y-1 PR 1518');
    await tester.ensureVisible(bind);
    await tester.tap(bind);
    await tester.pumpAndSettle();
    expect(
      find.textContaining('no_structured_verdict_for_head'),
      findsOneWidget,
    );
    expect(find.textContaining('Abweichender Kandidat'), findsOneWidget);
    final open = find.text('Y-1 öffnen');
    await tester.ensureVisible(open);
    await tester.tap(open);
    await tester.pumpAndSettle();
    expect(find.text('Änderung Y-1'), findsOneWidget);
    await tester.tap(find.text('Projektlandschaft'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Fall Y-1'), findsOneWidget);
    expect(find.textContaining('Abweichender Kandidat'), findsOneWidget);
  });

  testWidgets(
    'different cases, candidates, endpoints and source identities stay distinct',
    (tester) async {
      tester.view.physicalSize = const Size(1600, 1400);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      final data = load('landscape-historical.json');
      final repository = (data['nodes'] as List)
          .cast<Map<String, dynamic>>()
          .firstWhere((n) => n['id'] == 'repo:ed4da66dacb79098');
      final attachment = Map<String, dynamic>.from(
        (data['attachments'] as List).first as Map,
      );
      attachment['case_id'] = 'OTHER';
      attachment['claims'] = [];
      attachment['followups'] = [];
      final fixture = <String, dynamic>{
        'nodes': [
          repository,
          {
            'id': 'registry:same-name',
            'name': 'aethelBrowser',
            'kind': 'registereintrag',
            'areas': [],
          },
          {
            'id': 'component:1',
            'name': 'Werkzeug',
            'kind': 'komponente',
            'areas': ['Fabrik', 'Plattform'],
          },
        ],
        'edges': [
          {
            'from': 'registry:same-name',
            'to': repository['id'],
            'type': 'benennt',
            'status': 'ungeprüft',
            'evidence': 'registry',
            'detail': 'Namensgleichheit',
          },
          {
            'from': repository['id'],
            'to': 'component:1',
            'type': 'erstens',
            'status': 'geplant',
            'evidence': 'plan',
            'detail': 'Plan',
          },
          {
            'from': repository['id'],
            'to': 'component:1',
            'type': 'zweitens',
            'status': 'bestehend',
            'evidence': 'manifest',
            'detail': 'Deklaration',
          },
          {
            'from': 'missing:id',
            'to': repository['id'],
            'type': 'unbekannt',
            'status': 'ungeprüft',
            'evidence': 'source',
            'detail': 'offen',
          },
        ],
        'attachments': [attachment],
        'unresolved_endpoints': ['missing:id'],
      };
      final current = load('y1-assessment.json');
      int? bound;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: StatefulBuilder(
                builder: (context, setState) => LandscapePanel(
                  data: fixture,
                  origin: 'Test',
                  currentAssessment: current,
                  selectedId: repository['id'] as String,
                  sources: [
                    {
                      'name': 'falsch',
                      'data': {
                        'schema': 'aethel.plm.project-observation/v1',
                        'repository_id': 'other-repository',
                      },
                    },
                    {
                      'name': 'passend',
                      'data': {
                        'schema': 'aethel.plm.project-observation/v1',
                        'repository_id': repository['git_common_dir'],
                        'evidence': {'candidate': 'other-head'},
                      },
                    },
                  ],
                  selectedSourceIndex: bound,
                  onBindSource: (i) => setState(() => bound = i),
                  selectedLandingIndex: null,
                  onBindLanding: (_) {},
                  onSelect: (_) {},
                  onOpenY1: () {},
                ),
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.textContaining('Fall OTHER'), findsOneWidget);
      expect(
        find.textContaining('Ein anderer Fall ist geöffnet'),
        findsOneWidget,
      );
      expect(find.text('Y-1 öffnen'), findsNothing);
      expect(find.textContaining('echte Anmeldung'), findsNothing);
      expect(find.textContaining('Von aethelBrowser'), findsOneWidget);
      expect(find.textContaining('Zu Werkzeug'), findsNWidgets(2));
      expect(
        find.textContaining('nicht aufgelöst: missing:id'),
        findsOneWidget,
      );
      expect(find.textContaining('Temporär zuordnen: falsch'), findsNothing);
      final button = find.textContaining('Temporär zuordnen: passend');
      await tester.ensureVisible(button);
      await tester.tap(button);
      await tester.pumpAndSettle();
      expect(
        find.textContaining('Gemeldeter Checkout-HEAD: other-head'),
        findsOneWidget,
      );
    },
  );

  test(
    'projection validation rejects duplicate identities and foreign attachment',
    () {
      final data = load('landscape-historical.json');
      validateShape(data);
      final bad = Map<String, dynamic>.from(data);
      bad['nodes'] = [...data['nodes'] as List, (data['nodes'] as List).first];
      expect(() => validateShape(bad), throwsFormatException);
      final wrong = Map<String, dynamic>.from(data);
      final a = Map<String, dynamic>.from(
        (data['attachments'] as List).first as Map,
      );
      a['repository_id'] = 'foreign';
      wrong['attachments'] = [a];
      expect(() => validateShape(wrong), throwsFormatException);
    },
  );

  testWidgets(
    'a changed candidate is never shown as matched to historical evidence',
    (tester) async {
      tester.view.physicalSize = const Size(1600, 1300);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      final data = load('landscape-historical.json');
      final changed = load('y1-assessment.json');
      (changed['change'] as Map<String, dynamic>)['candidate'] =
          'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: LandscapePanel(
                data: data,
                origin: 'Test',
                currentAssessment: changed,
                selectedId: 'repo:ed4da66dacb79098',
                sources: const [],
                selectedSourceIndex: null,
                onBindSource: (_) {},
                selectedLandingIndex: null,
                onBindLanding: (_) {},
                onSelect: (_) {},
                onOpenY1: () {},
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(
        find.textContaining('Kandidat abweichend: historische Belege'),
        findsOneWidget,
      );
      expect(
        find.textContaining('Kandidatenangabe stimmt überein'),
        findsNothing,
      );
    },
  );

  testWidgets(
    'actual analyzer observation preserves rejected findings and unknown configuration',
    (tester) async {
      tester.view.physicalSize = const Size(1600, 1300);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      final data = load('landscape-historical.json');
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: LandscapePanel(
                data: data,
                origin: 'Test',
                currentAssessment: load('y1-assessment.json'),
                selectedId: 'repo:a9be6f68e2d93f19',
                sources: const [],
                selectedSourceIndex: null,
                onBindSource: (_) {},
                selectedLandingIndex: null,
                onBindLanding: (_) {},
                onSelect: (_) {},
                onOpenY1: () {},
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.textContaining('2187 Fundstellen'), findsOneWidget);
      expect(find.textContaining('Nicht zuordenbar: 4'), findsOneWidget);
      expect(find.text('Werkzeugkonfiguration: nicht belegt'), findsOneWidget);
      expect(
        find.textContaining('keine Gesamtbewertung der Softwarequalität'),
        findsOneWidget,
      );
    },
  );
}
