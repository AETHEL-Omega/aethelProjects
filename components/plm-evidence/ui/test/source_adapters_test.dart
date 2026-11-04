import 'dart:convert';
import 'dart:io';
import 'package:aethel_plm/source_adapters.dart';
import 'package:aethel_plm/product_home.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test(
    'AIX order projection preserves identity without inventing lease or output',
    () {
      final response = {
        'ok': true,
        'ergebnis': {
          'schema': 'aix.auftrag.leseprojektion.v1',
          'beobachtet_epoch': 100,
          'auftraege': [
            {
              'auftrag_ref': 'a1',
              'lesestatus': 'gebunden',
              'revision': 2,
              'projekt': '/p',
              'kandidat': 'abc',
              'zustand': 'aktiv',
              'besitz': {'eigentuemer': 'x', 'generation': 3},
              'private': 'secret',
              'host_lease': {'private': 'secret'},
            },
          ],
        },
      };
      final value = readAixOrders(response, 'AIX');
      final row = (value['auftraege'] as List).single;
      expect(row['auftrag_ref'], 'a1');
      expect(row['owner_generation'], 3);
      expect(row['host_lease'], isNull);
      expect(row['output'], isNull);
      expect(value.toString(), isNot(contains('secret')));
      final mixed = Map<String, dynamic>.from(response);
      final resultData = Map<String, dynamic>.from(response['ergebnis'] as Map);
      resultData['auftraege'] = [
        ...resultData['auftraege'] as List,
        {'auftrag_ref': 'a2', 'lesestatus': 'unlesbar', 'private': 'secret'},
        {
          'auftrag_ref': 'a3',
          'lesestatus': 'historisch_nicht_rekonstruiert',
          'revision': 1,
          'projekt': '/old',
          'kandidat': 'abc',
          'quelle_zeit': '1000',
          'private': 'secret',
        },
      ];
      mixed['ergebnis'] = resultData;
      final entries = readAixOrders(mixed, 'AIX')['auftraege'] as List;
      expect(entries.length, 3);
      expect(entries[1]['lesestatus'], 'unlesbar');
      expect(entries.last['lesestatus'], 'historisch_nicht_rekonstruiert');
      expect(entries.last['owner'], isNull);
      expect(entries.toString(), isNot(contains('secret')));
      expect(() => readAixOrders({'ok': false}, 'AIX'), throwsFormatException);
    },
  );
  final projectsPath = Platform.environment['PROJECTS_COCKPIT_TEST'];
  final aixPath = Platform.environment['AIX_DASHBOARD_TEST'];
  if (projectsPath != null && aixPath != null) {
    test('actual Projects and AIX outputs are readable', () {
      final projects =
          jsonDecode(File(projectsPath).readAsStringSync())
              as Map<String, dynamic>;
      final aix =
          jsonDecode(File(aixPath).readAsStringSync()) as Map<String, dynamic>;
      expect(readCockpit(projects, 'Projects CLI')['tiles'], isA<List>());
      expect(readAixDashboard(aix, 'AIX CLI')['timestamp'], isA<String>());
    });
  }

  testWidgets('selected AIX input is visible without assigning it to Y-1', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(1600, 2400);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    final source = {
      'schema': 'aix.engineering_input.v1',
      'metadata': {'id': 'E-1', 'revision': 1},
      'project': {'id': 'other'},
      'factory': {
        'pom': 'aix.production_operations_model.v2',
        'work_order_id': 'WO-TEST-001',
        'product_binding': {
          'spec_digest': 'abc',
          'spec_session_path': 'spec/session.json',
          'model_refs': ['REQ-1'],
          'production_mode': 'prototype',
        },
        'substrate_binding': {
          'host_profile': 'test-host',
          'compute_mode': 'LOCAL_AI_ONLY',
        },
        'output_contract': {
          'pbom_schema': 'aix.pbom.v2',
          'required_fields': ['tree_sha'],
        },
      },
    };
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: ProductHome(
              cockpit: null,
              factoryInput: readFactoryInput(source, 'input.json'),
              onOpenY1: () {},
              onLandscape: () {},
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Ausgewählter Fertigungsvertrag'), findsOneWidget);
    expect(find.textContaining('WO-TEST-001'), findsOneWidget);
    expect(find.text('Projekt laut Quelle: other'), findsOneWidget);
    expect(find.text('Spezifikationsdigest: abc'), findsOneWidget);
    expect(
      find.text('Spec-Session im Kandidaten: spec/session.json'),
      findsOneWidget,
    );
    expect(find.text('Modellreferenzen: REQ-1'), findsOneWidget);
    expect(find.text('Hostprofil: test-host'), findsOneWidget);
    expect(find.text('Erwartete Outputfelder: tree_sha'), findsOneWidget);
    expect(
      find.textContaining('keine Validierung, Freigabe oder Zuordnung zu Y-1'),
      findsOneWidget,
    );
  });
  test('Projects cockpit keeps source, tiles and missing information', () {
    final source = {
      'schema': 'aethel.projects.cockpit/v1',
      'kacheln': [
        {'titel': 'Projekte', 'wert': '2', 'quelle': 'Export'},
      ],
      'fehlt': ['Owner'],
      'quellen': {'scan': 'historisch'},
    };
    final result = readCockpit(source, 'Datei: cockpit.json');
    expect(result['source_id'], 'Datei: cockpit.json');
    expect(result['missing'], ['Owner']);
    expect(result['tiles'], source['kacheln']);
    expect(
      () => readCockpit({'schema': 'aethel.projects.cockpit/v1'}, 'x'),
      throwsFormatException,
    );
  });
  test(
    'AIX preview carries reported spec comparison without assigning Y-1',
    () {
      final preview = {
        'state': 'INPUT_REVIEW',
        'compiled_input': {
          'canonical_input': {
            'schema': 'aix.engineering_input.v1',
            'metadata': {'id': 'E-1'},
            'project': {'id': 'other'},
            'factory': {'pom': 'aix.production_operations_model.v2'},
          },
        },
        'assm_admission': {
          'schema': 'aix.assm.work_package_admission.v1',
          'vorpruefung': {
            'spec_inhaltspruefung': {'content_matches': true},
          },
        },
      };
      final result = readAixInputPreview(preview, 'preview.json');
      expect(result['spec_content_matches'], true);
      expect(result.containsKey('y1_binding'), isFalse);
      expect(
        () => readAixInputPreview({...preview, 'assm_admission': {}}, 'x'),
        throwsFormatException,
      );
    },
  );
  test(
    'AIX dashboard is projection only and excludes prompt and telemetry',
    () {
      final source = {
        'schema': 'aix.dashboard.v2',
        'projection_only': true,
        'timestamp': '2026-11-04T10:00:00+01:00',
        'components': [],
        'latest_goal': {'goal_id': 'G-1', 'state': 'open', 'prompt': 'private'},
        'tokens': {'private': 'data'},
      };
      final result = readAixDashboard(source, 'aix.json');
      expect(result['goal_id'], 'G-1');
      expect(result.toString(), isNot(contains('private')));
      final nested = readAixDashboard({
        ...source,
        'latest_kernel_transaction': {
          'transaction_id': {'intent': 'private'},
          'state': ['private'],
          'created_at': {'private': true},
        },
      }, 'aix.json');
      expect(nested.toString(), isNot(contains('private')));
      expect(
        () => readAixDashboard({...source, 'projection_only': false}, 'x'),
        throwsFormatException,
      );
    },
  );
  test('factory input retains missing binding and never assigns a product', () {
    final source = {
      'schema': 'aix.engineering_input.v1',
      'metadata': {'id': 'E-1', 'revision': 1},
      'project': {'name': 'aethelBrowser'},
      'factory': {
        'pom': 'aix.production_operations_model.v1',
        'work_order_id': 'WO-TEST-001',
        'line': 'aix-line',
        'station': 'verify',
      },
    };
    final result = readFactoryInput(source, 'input.json');
    expect(result['work_order_id'], 'WO-TEST-001');
    expect(result['product_binding'], isNull);
    expect(result.containsKey('y1_binding'), isFalse);
    expect(
      () => readFactoryInput({
        ...source,
        'factory': {'pom': 'unsupported'},
      }, 'x'),
      throwsFormatException,
    );
  });
}
