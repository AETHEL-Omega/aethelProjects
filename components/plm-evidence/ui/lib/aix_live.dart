import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'source_adapters.dart';

/// Only the existing local AIX dashboard, no redirects, proxies or persistence.
Future<Map<String, dynamic>> readLocalAix({
  HttpClient? client,
  int port = 7331,
}) async => readAixDashboard(
  await _readLocalProjection('/api/state', client: client, port: port),
  'AIX Dashboard · 127.0.0.1:$port',
);

/// Uses the existing AIX dashboard's lightweight order endpoint.
Future<Map<String, dynamic>> readLocalAixOrders({
  HttpClient? client,
  int port = 7331,
}) async => readAixOrders(
  await _readLocalProjection('/api/orders', client: client, port: port),
  'AIX Auftragsquelle · 127.0.0.1:$port',
);

Future<Map<String, dynamic>> _readLocalProjection(
  String path, {
  HttpClient? client,
  required int port,
}) async {
  final http = client ?? HttpClient();
  http.findProxy = (_) => 'DIRECT';
  http.connectionTimeout = const Duration(seconds: 3);
  try {
    final request = await http
        .getUrl(Uri(scheme: 'http', host: '127.0.0.1', port: port, path: path))
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
    return value;
  } finally {
    http.close(force: true);
  }
}
