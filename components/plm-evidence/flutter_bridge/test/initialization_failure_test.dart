import 'dart:io';

import 'package:aethel_evidence_bridge/aethel_evidence_bridge.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets(
    'missing native initialization is visible as an unavailable result',
    (tester) async {
      final validCase = File(
        '../fixtures/y1-historical.json',
      ).readAsStringSync();
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: EvidencePanel(caseJson: validCase)),
        ),
      );
      await tester.pump();
      expect(find.text('Auswertung nicht verfügbar.'), findsOneWidget);
    },
  );
}
