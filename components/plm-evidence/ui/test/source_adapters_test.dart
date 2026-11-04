import 'dart:convert';
import 'dart:io';
import 'package:aethel_plm/source_adapters.dart';
import 'package:aethel_plm/product_home.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
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
        'pom': 'aix.production_operations_model.v1',
        'work_order_id': 'WO-TEST-001',
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
