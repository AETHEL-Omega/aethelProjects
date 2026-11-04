import 'dart:convert';
import 'dart:io';
import 'package:aethel_plm/product_home.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('product entry separates company, factory and missing mBOM', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(1600, 1800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    var opened = false;
    final cockpit =
        jsonDecode(File('assets/cockpit-2026-11-03.json').readAsStringSync())
            as Map<String, dynamic>;
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: ProductHome(
              cockpit: cockpit,
              aixDashboard: {
                'source': 'AIX Dashboard',
                'timestamp': '2026-11-04',
                'kernel_transaction': {
                  'id': 'tx-1',
                  'state': 'open',
                  'created_at': '2026-11-04',
                },
              },
              onOpenY1: () => opened = true,
              onLandscape: () {},
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('aethelBrowser · Pilot Y-1'), findsOneWidget);
    expect(find.text('Firma'), findsOneWidget);
    expect(find.text('Fabrik'), findsOneWidget);
    expect(find.text('mBOM'), findsOneWidget);
    expect(find.text('Letzte Kernel-Transaktion: tx-1'), findsOneWidget);
    expect(
      find.text('Lesende Projektion; Ledgerkette und Zuordnung nicht geprüft.'),
      findsOneWidget,
    );
    expect(
      find.textContaining('Eine Y-1-mBOM liegt dieser Sicht nicht vor'),
      findsOneWidget,
    );
    expect(
      find.textContaining('Zeitpunkt und Aktualität nicht unabhängig geprüft'),
      findsOneWidget,
    );
    expect(find.textContaining('Register-Drift'), findsOneWidget);
    await tester.tap(find.text('Fall Y-1 öffnen'));
    expect(opened, isTrue);
  });
}
