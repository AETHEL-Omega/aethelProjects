import 'dart:convert';
import 'dart:io';
import 'package:aethel_plm/main.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('private workspace is navigable without unbounded layout', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(1400, 1100);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(const AethelPlm());
    await tester.pumpAndSettle();
    await tester.tap(find.text('Privat'));
    await tester.pumpAndSettle();
    expect(find.text('Privaten Ordner öffnen'), findsOneWidget);
    expect(tester.takeException(), isNull);
    await tester.tap(find.text('Produkte'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Privat'));
    await tester.pumpAndSettle();
    expect(find.text('Privaten Ordner öffnen'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('inventory workspace opens without inventing a scan', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(1400, 1100);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(const AethelPlm());
    await tester.pumpAndSettle();
    await tester.tap(find.text('Projekte aktuell'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 500));
    expect(find.textContaining('Inventurdatei'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
  testWidgets('historical Rust output shows login evidence gaps', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(1400, 1100);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(
      AethelPlm(
        initialJson: File('assets/y1-assessment.json').readAsStringSync(),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Änderung'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Übergebene Auswertung'), findsOneWidget);
    expect(find.textContaining('Historisch: 2026-11-04'), findsOneWidget);
    expect(
      find.text('Echter Login erreicht den angemeldeten Zustand.'),
      findsOneWidget,
    );
    await tester.tap(
      find.text('Echter Login erreicht den angemeldeten Zustand.'),
    );
    await tester.pumpAndSettle();
    expect(find.text('missing_applicable_evidence'), findsWidgets);
    expect(find.textContaining('ua-chain · pass'), findsOneWidget);
    expect(
      find.textContaining('Quelle und Autorität nicht geprüft'),
      findsOneWidget,
    );
  });
  testWidgets('synthetic quality scenario preserves missing effectiveness', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(1400, 1100);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(
      AethelPlm(
        initialJson: File('assets/linked-assessment.json').readAsStringSync(),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Qualität'));
    await tester.pumpAndSettle();
    expect(
      find.text('Qualitätsakte synthetic-quality-example'),
      findsOneWidget,
    );
    expect(find.text('effectiveness_missing'), findsWidgets);
    expect(
      find.textContaining('Externe Autorität ist nicht verifiziert'),
      findsOneWidget,
    );
  });
  test('only supported assessment output is accepted', () async {
    final v =
        jsonDecode(File('assets/y1-assessment.json').readAsStringSync())
            as Map<String, dynamic>;
    expect(() => validateShape(v), returnsNormally);
    expect(changeAssessment(v)!['claims'], isA<List>());
    expect(
      () => validateShape({
        'schema': 'aethel.plm.assessment/v1',
        'change': 'bad',
        'claims': [],
      }),
      throwsFormatException,
    );
    expect(supported.contains('aethel.plm.assessment/v2'), isFalse);
  });
  testWidgets('additional source projections remain explicitly unlinked', (
    tester,
  ) async {
    final current =
        jsonDecode(File('assets/y1-assessment.json').readAsStringSync())
            as Map<String, dynamic>;
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: SourcePanel(
              data: current,
              sources: const [
                SourceItem('project.json', {
                  'schema': 'aethel.plm.project-observation/v1',
                  'repository_id': 'repo-1',
                  'product_reference': null,
                  'freshness': 'not_checked',
                  'assessment': 'source_assertion_only',
                }),
                SourceItem('goal.json', {
                  'schema': 'aethel.plm.copilot-observation/v1',
                  'goal_id': 'goal-123456abcdef',
                  'reported_actor': 'claude',
                  'reported_agent_id': 'agent-1',
                  'actual_inference_location': null,
                  'freshness': 'not_checked',
                  'assessment': 'source_assertion_only',
                }),
              ],
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(
      find.textContaining('nicht automatisch einer Änderung zugeordnet'),
      findsOneWidget,
    );
    expect(find.text('project.json'), findsOneWidget);
    expect(find.text('goal.json'), findsOneWidget);
    await tester.tap(find.text('goal.json'));
    await tester.pumpAndSettle();
    expect(find.text('goal-123456abcdef'), findsOneWidget);
    expect(find.textContaining('claude / agent-1'), findsOneWidget);
  });
  testWidgets('trace view displays actual links without inventing coverage', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(1400, 1100);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(
      AethelPlm(
        initialJson: File('assets/linked-assessment.json').readAsStringSync(),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Zusammenhang'));
    await tester.pumpAndSettle();
    expect(
      find.textContaining('Issue issue-1 → Maßnahme action-1'),
      findsOneWidget,
    );
    expect(find.textContaining('Belegreferenz: keine'), findsOneWidget);
    expect(
      find.textContaining('Sie belegen weder Prüfung noch Erfüllung'),
      findsOneWidget,
    );
  });
}
