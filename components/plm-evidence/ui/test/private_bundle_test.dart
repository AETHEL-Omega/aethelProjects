import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:aethel_plm/private_bundle.dart';

void main() {
  test(
    'reloads selected files, preserves last good value on failure and refuses symlinks',
    () async {
      final dir = await Directory.systemTemp.createTemp('private-bundle-test-');
      addTearDown(() async => dir.delete(recursive: true));
      final file = File('${dir.path}/coverage.json');
      await file.writeAsString('{"events":1}');
      final first = await readPrivateBundle(dir.path, {});
      expect(first.documents['coverage.json']?['events'], 1);
      await file.writeAsString('{"events":2}');
      final second = await readPrivateBundle(dir.path, first.documents);
      expect(second.documents['coverage.json']?['events'], 2);
      await file.writeAsString('{invalid');
      final third = await readPrivateBundle(dir.path, second.documents);
      expect(third.documents['coverage.json']?['events'], 2);
      expect(third.errors['coverage.json'], isNotNull);
      await file.delete();
      await Link(file.path).create('${dir.path}/missing');
      final fourth = await readPrivateBundle(dir.path, third.documents);
      expect(fourth.errors['coverage.json'], isNotNull);
      expect(fourth.documents['coverage.json']?['events'], 2);
    },
  );
  testWidgets('project source search stays explicitly unverified', (
    tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: PrivateSourceSearch(
              sources: [
                {
                  'source': '/one',
                  'names': {'aethelBrowser': 15},
                },
                {
                  'source': '/two',
                  'names': {'aethelBot': 9},
                },
              ],
            ),
          ),
        ),
      ),
    );
    await tester.tap(find.text('Quellverweise (2)'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField), 'aethelBot');
    await tester.pumpAndSettle();
    expect(find.text('/two'), findsOneWidget);
    expect(find.text('/one'), findsNothing);
    expect(find.textContaining('ungeprüfte Hinweise'), findsOneWidget);
  });
}
