import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:aethel_plm/private_history.dart';

void main() {
  test('rejects foreign or malformed coverage', () {
    expect(
      () => validatePrivateHistory({'schema': 'wrong'}),
      throwsFormatException,
    );
    expect(
      () => validatePrivateHistory({
        'schema': 'aethel.projects.private-work-history/v1',
      }),
      throwsFormatException,
    );
  });
  testWidgets('shows gaps and avoids claiming completion', (tester) async {
    final data = <String, dynamic>{
      'schema': 'aethel.projects.private-work-history/v1',
      'sources': <dynamic>[],
      'events': 42,
      'catalog_without_transcript': 3,
      'review_queue': [
        <dynamic>['obtain_transcript', 3],
      ],
      'observed_at': '2026-11-04T00:00:00Z',
    };
    validatePrivateHistory(data);
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: PrivateHistoryPanel(data: data, status: 'Snapshot'),
        ),
      ),
    );
    expect(find.text('Katalogeinträge ohne Transkript: 3'), findsOneWidget);
    expect(find.text('Fehlendes Transkript beschaffen'), findsOneWidget);
    expect(
      find.textContaining('keine vollständige fachliche Bewertung'),
      findsOneWidget,
    );
  });
  testWidgets('private case shows source and unresolved items', (tester) async {
    final data = <String, dynamic>{
      'case': 'Y-1',
      'open': ['Login prüfen'],
      'chat_evidence': [
        <String, dynamic>{
          'actor': 'assistant',
          'kind': 'statement',
          'line': 8,
          'source': '/private/source',
          'preview': 'behauptet',
        },
      ],
    };
    validatePrivateHistory(data);
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: PrivateHistoryPanel(data: data, status: 'Snapshot'),
        ),
      ),
    );
    expect(find.text('Login prüfen'), findsOneWidget);
    expect(find.textContaining('/private/source'), findsOneWidget);
    expect(find.textContaining('keine Abnahme'), findsOneWidget);
  });
}
