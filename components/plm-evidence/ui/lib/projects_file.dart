import 'dart:convert';
import 'package:file_selector/file_selector.dart';
import 'source_adapters.dart';

/// Re-reads only the explicitly selected Projects export, never starts a scan.
Future<Map<String, dynamic>> readProjectsFile(XFile file) async {
  const limit = 8 * 1024 * 1024;
  if (await file.length() > limit) throw const FormatException('Datei zu groß');
  final content = await file.readAsString();
  if (utf8.encode(content).length > limit) {
    throw const FormatException('Datei zu groß');
  }
  final value = jsonDecode(content);
  if (value is! Map<String, dynamic>) {
    throw const FormatException('Ungültiges JSON');
  }
  return readCockpit(value, 'Datei: ${file.name}');
}
