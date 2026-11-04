import 'dart:convert';
import 'dart:io';

import 'package:aethel_evidence_bridge/aethel_evidence_bridge.dart';
import 'package:flutter_rust_bridge/flutter_rust_bridge_for_generated.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';

void main() {
  setUpAll(() async {
    final name = Platform.isMacOS
        ? 'libaethel_evidence_bridge.dylib'
        : 'libaethel_evidence_bridge.so';
    final library = File('rust/target/debug/$name').absolute.path;
    await RustLib.init(externalLibrary: ExternalLibrary.open(library));
  });
  tearDownAll(RustLib.dispose);

  test(
    'native Rust assesses the historical Y-1 case without proving login',
    () async {
      final input = await File('../fixtures/y1-historical.json').readAsString();
      final result = jsonDecode(await assessCaseJson(input: input)) as Map;
      expect(result['schema'], 'aethel.plm.assessment/v1');
      final claims = result['claims'] as List;
      final login = claims.cast<Map>().singleWhere(
        (claim) => claim['id'] == 'login',
      );
      expect(
        (login['gaps'] as List).cast<Map>().map((g) => g['code']),
        contains('independent_verification_missing'),
      );
    },
  );

  test('native Rust preserves quality and linked contracts', () async {
    final quality = await File(
      '../fixtures/quality-synthetic.json',
    ).readAsString();
    final linked = await File(
      '../fixtures/linked-synthetic.json',
    ).readAsString();
    expect(
      (jsonDecode(await assessQualityJson(input: quality)) as Map)['schema'],
      'aethel.plm.quality-assessment/v1',
    );
    expect(
      (jsonDecode(await assessLinkedJson(input: linked)) as Map)['schema'],
      'aethel.plm.linked-assessment/v1',
    );
  });

  test('native Rust rejects invalid input', () async {
    await expectLater(assessCaseJson(input: '{'), throwsA(isA<Object>()));
  });

  testWidgets('Flutter panel renders the native Rust assessment', (
    tester,
  ) async {
    final input = File('../fixtures/y1-historical.json').readAsStringSync();
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: EvidencePanel(caseJson: input)),
      ),
    );
    await tester.runAsync(
      () => Future<void>.delayed(const Duration(milliseconds: 250)),
    );
    await tester.pump();
    expect(
      find.textContaining('keine unabhängige Verifikation'),
      findsOneWidget,
    );
    expect(
      find.text('Echter Login erreicht den angemeldeten Zustand.'),
      findsOneWidget,
    );
    expect(
      find.textContaining('Historische Momentaufnahme: 2026-11-04'),
      findsOneWidget,
    );
    expect(
      find.textContaining('c1b0c46cbae60a69a00332a050841044e64b32e1'),
      findsOneWidget,
    );
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: EvidencePanel(caseJson: '$input ')),
      ),
    );
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    expect(
      find.text('Echter Login erreicht den angemeldeten Zustand.'),
      findsNothing,
    );
    await tester.runAsync(
      () => Future<void>.delayed(const Duration(milliseconds: 250)),
    );
    await tester.pump();
    expect(
      find.text('Echter Login erreicht den angemeldeten Zustand.'),
      findsOneWidget,
    );
  });

  testWidgets('oversized case is rejected by the panel', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: EvidencePanel(caseJson: 'x' * (8 * 1024 * 1024 + 1)),
        ),
      ),
    );
    await tester.pump();
    expect(find.text('Auswertung nicht verfügbar.'), findsOneWidget);
  });
}
