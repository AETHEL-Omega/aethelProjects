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
    expect(find.textContaining('nicht automatisch gelöscht'), findsOneWidget);
    expect(find.textContaining('Zustand: partial'), findsOneWidget);
    await tester.enterText(find.byType(TextField), '/c');
    await tester.pump();
    expect(
      find.byWidgetPredicate((w) => w is Text && w.data == 'c'),
      findsOneWidget,
    );
    expect(find.text('a'), findsNothing);
  });
}
