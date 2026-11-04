import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'source_adapters.dart';

/// Only the existing local AIX dashboard, no redirects, proxies or persistence.
Future<Map<String, dynamic>> readLocalAix({
  HttpClient? client,
  int port = 7331,
}) async {
  final http = client ?? HttpClient();
  http.findProxy = (_) => 'DIRECT';
  http.connectionTimeout = const Duration(seconds: 3);
  try {
    final request = await http
        .getUrl(
          Uri(
            scheme: 'http',
            host: '127.0.0.1',
            port: port,
            path: '/api/state',
          ),
        )
        .timeout(const Duration(seconds: 3));
    request.followRedirects = false;
    final response = await request.close().timeout(const Duration(seconds: 3));
    if (response.statusCode != 200) {
      throw const FormatException('AIX HTTP-Status');
    }
    const limit = 1024 * 1024;
    if (response.contentLength > limit) {
      throw const FormatException('AIX-Ausgabe zu groß');
    }
    final bytes = <int>[];
    await for (final chunk in response.timeout(const Duration(seconds: 3))) {
      if (bytes.length + chunk.length > limit) {
        throw const FormatException('AIX-Ausgabe zu groß');
      }
      bytes.addAll(chunk);
    }
    final value = jsonDecode(utf8.decode(bytes));
    if (value is! Map<String, dynamic>) {
      throw const FormatException('AIX-Ausgabe ungültig');
    }
    return readAixDashboard(value, 'AIX Dashboard · 127.0.0.1:7331');
  } finally {
    http.close(force: true);
  }
}
