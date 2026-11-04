import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:aethel_plm/inventory_panel.dart';

void main() {
  test('rejects non-inventory input', () {
    expect(
      () => validateInventory({'schema': 'foreign'}),
      throwsFormatException,
    );
  });
  testWidgets('shows project changes and never labels missing as deleted', (
    tester,
  ) async {
    final data = <String, dynamic>{
      'schema': 'aethel.projects.inventory-live/v1',
      'status': 'partial',
      'attempted_at': '2026-11-04T12:00:00Z',
      'last_success_at': '2026-11-04T11:00:00Z',
      'changes': {
        'new_repositories': ['/a/.git'],
        'changed_checkouts': [],
        'new_non_git_candidates': ['/c'],
      },
      'scan': {
        'repositories': [
          {
            'git_common_dir': '/a/.git',
            'paths': ['/a'],
          },
        ],
        'checkouts': [
          {
            'git_common_dir': '/a/.git',
            'path': '/a',
            'head': 'abc',
            'branch': 'main',
            'dirty_files': 1,
          },
        ],
        'projects_without_git': [
          {'path': '/c'},
        ],
      },
    };
    validateInventory(data);
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: InventoryPanel(data: data, status: 'Test'),
        ),
      ),
    );
    expect(find.text('a'), findsOneWidget);
    expect(
      find.byWidgetPredicate((w) => w is Text && w.data == 'c'),
      findsOneWidget,
    );
    await tester.tap(find.text('Quelle und Erfassungsdetails'));
    await tester.pumpAndSettle();
    expect(find.textContaining('nicht automatisch gelöscht'), findsOneWidget);
    expect(find.textContaining('Zustand: partial'), findsOneWidget);
    await tester.tap(find.text('Quelle und Erfassungsdetails'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField), '/c');
    await tester.pump();
    expect(
      find.byWidgetPredicate((w) => w is Text && w.data == 'c'),
      findsOneWidget,
    );
    expect(find.text('a'), findsNothing);
  });
  testWidgets('matching project name ranks before nested path-only matches', (tester) async {
    final data = <String, dynamic>{
      'schema': 'aethel.projects.inventory-live/v1', 'status': 'ok',
      'attempted_at': DateTime.now().toUtc().toIso8601String(),
      'scan': <String, dynamic>{
        'repositories': [
          <String, dynamic>{'git_common_dir': '/nuru/vendor/byztxt/.git', 'paths': ['/nuru/vendor/byztxt']},
          <String, dynamic>{'git_common_dir': '/heritage_nuru/.git', 'paths': ['/heritage_nuru']},
        ],
        'checkouts': <dynamic>[], 'projects_without_git': <dynamic>[],
      },
    };
    await tester.pumpWidget(MaterialApp(home: Scaffold(body: InventoryPanel(data: data, status: 'Test'))));
    await tester.enterText(find.byType(TextField), 'nuru');
    await tester.pump();
    expect(tester.getTopLeft(find.text('heritage_nuru')).dy, lessThan(tester.getTopLeft(find.text('byztxt')).dy));
  });
  testWidgets('analysis action binds the exact checkout identity', (
    tester,
  ) async {
    String? identity;
    String? path;
    final data = <String, dynamic>{
      'schema': 'aethel.projects.inventory-live/v1',
      'status': 'ok',
      'attempted_at': DateTime.now().toUtc().toIso8601String(),
      'scan': <String, dynamic>{
        'repositories': [
          <String, dynamic>{
            'git_common_dir': '/one/.git',
            'paths': ['/one'],
          },
        ],
        'checkouts': <dynamic>[],
        'projects_without_git': <dynamic>[],
      },
    };
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: InventoryPanel(
            data: data,
            status: 'Test',
            onAnalyze: (i, p) {
              identity = i;
              path = p;
            },
          ),
        ),
      ),
    );
    await tester.tap(find.text('one'));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Projekt analysieren'));
    await tester.tap(find.text('Projekt analysieren'));
    expect(identity, '/one/.git');
    expect(path, '/one');
  });
  testWidgets('only binds an AIX order to its unique real checkout', (
    tester,
  ) async {
    final root = Directory.systemTemp.createTempSync('aethel-orders-test');
    addTearDown(() => root.deleteSync(recursive: true));
    final repo = Directory('${root.path}/project')..createSync();
    final data = <String, dynamic>{
      'schema': 'aethel.projects.inventory-live/v1',
      'status': 'ok',
      'attempted_at': DateTime.now().toUtc().toIso8601String(),
      'scan': <String, dynamic>{
        'repositories': [
          <String, dynamic>{
            'git_common_dir': '${repo.path}/.git',
            'paths': [repo.path],
            'readme_purpose': <String, dynamic>{
              'text': 'Ein nützliches Projekt',
              'source': 'README',
              'sha256': 'abc',
            },
          },
        ],
        'checkouts': <dynamic>[],
        'projects_without_git': <dynamic>[],
      },
    };
    final orders = <String, dynamic>{
      'auftraege': [
        <String, dynamic>{
          'lesestatus': 'gebunden',
          'projekt': repo.path,
          'auftrag_ref': 'A-1',
          'revision': 1,
          'zustand': 'offen',
          'kandidat': 'abc',
        },
        <String, dynamic>{
          'lesestatus': 'historisch_nicht_rekonstruiert',
          'projekt': repo.path,
          'auftrag_ref': 'OLD',
        },
      ],
    };
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: InventoryPanel(data: data, status: 'Test', orders: orders),
        ),
      ),
    );
    expect(find.text('Laut README: Ein nützliches Projekt'), findsOneWidget);
    await tester.tap(find.text('project'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Auftrag A-1'), findsOneWidget);
    expect(find.textContaining('OLD'), findsNothing);
    expect(
      find.text('Codeanalyse: noch kein Ergebnis zugeordnet'),
      findsOneWidget,
    );
  });
  testWidgets('shows source-backed purpose and bounded analyzer findings', (
    tester,
  ) async {
    final data = <String, dynamic>{
      'schema': 'aethel.projects.inventory-live/v1',
      'status': 'ok',
      'attempted_at': DateTime.now().toUtc().toIso8601String(),
      'last_success_at': null,
      'changes': <String, dynamic>{},
      'scan': <String, dynamic>{
        'summary': <String, dynamic>{
          'checkout_errors': 0,
          'filesystem_errors': 0,
        },
        'repositories': [
          <String, dynamic>{
            'git_common_dir': '/nuru/.git',
            'paths': ['/nuru'],
            'direct_observation': <String, dynamic>{
              'state': 'source_bytes_match',
              'purpose': 'Bibel lesen',
              'finding': 'Lesefunktionen vorhanden',
              'next_step': 'Abnahme prüfen',
            },
            'analyzer_observation': <String, dynamic>{
              'reported_finding_count': 1,
              'release_reported': 'test-release',
              'observed_at': '2026-11-04',
              'source_state': 'matched_scanned_files',
              'incomplete_reasons': ['walk-limit'],
              'stub_coverage': {
                'lexical_rule_omissions': ['dart'],
              },
              'findings': [
                <String, dynamic>{
                  'file': 'lib/main.dart',
                  'line': 7,
                  'rule': 'example',
                  'severity': 'low',
                  'evidence_tier': 'heuristic',
                },
              ],
            },
          },
        ],
        'checkouts': <dynamic>[],
        'projects_without_git': <dynamic>[],
      },
    };
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: InventoryPanel(data: data, status: 'Test'),
        ),
      ),
    );
    expect(find.text('Bibel lesen'), findsOneWidget);
    await tester.tap(find.text('nuru'));
    await tester.pumpAndSettle();
    expect(find.text('Abnahme prüfen'), findsOneWidget);
    await tester.ensureVisible(find.text('Codeanalyse · 1 Hinweise'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Codeanalyse · 1 Hinweise'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Analyzer-Version: test-release'), findsOneWidget);
    expect(find.textContaining('walk-limit'), findsOneWidget);
    expect(find.textContaining('lexical_rule_omissions'), findsOneWidget);
    expect(find.textContaining('heuristic'), findsOneWidget);
  });
}
