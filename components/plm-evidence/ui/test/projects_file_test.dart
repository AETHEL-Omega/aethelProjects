import 'dart:io';
import 'package:file_selector/file_selector.dart';
import 'package:aethel_plm/projects_file.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test(
    'selected Projects file is reread and malformed replacement is rejected',
    () async {
      final dir = await Directory.systemTemp.createTemp('projects_read_');
      addTearDown(() => dir.delete(recursive: true));
      final path = '${dir.path}/cockpit.json';
      final file = File(path);
      const first =
          '{"schema":"aethel.projects.cockpit/v1","kacheln":[{"titel":"Projekte","wert":"1","quelle":"Ablage"}],"fehlt":[],"quellen":{}}';
      await file.writeAsString(first);
      final selected = XFile(path);
      final one = await readProjectsFile(selected);
      expect((one['tiles'] as List).first['wert'], '1');
      await file.writeAsString(first.replaceFirst('"wert":"1"', '"wert":"2"'));
      final two = await readProjectsFile(selected);
      expect((two['tiles'] as List).first['wert'], '2');
      await file.writeAsString('{');
      await expectLater(readProjectsFile(selected), throwsFormatException);
    },
  );
}
