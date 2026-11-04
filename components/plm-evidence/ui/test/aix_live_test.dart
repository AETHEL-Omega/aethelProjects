import 'dart:convert';
import 'dart:io';
import 'package:aethel_plm/aix_live.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('reads order projection from the local AIX route', () async {
    final server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
    addTearDown(() => server.close(force: true));
    server.listen((request) {
      expect(request.uri.path, '/api/orders');
      request.response.write(
        jsonEncode({
          'ok': true,
          'ergebnis': {
            'schema': 'aix.auftrag.leseprojektion.v1',
            'beobachtet_epoch': 100,
            'auftraege': [
              {
                'auftrag_ref': 'a1',
                'lesestatus': 'historisch_nicht_rekonstruiert',
                'revision': 2,
                'projekt': '/project',
                'kandidat': 'abc',
                'quelle_zeit': '90',
              },
            ],
          },
        }),
      );
      request.response.close();
    });
    final result = await readLocalAixOrders(port: server.port);
    final row = (result['auftraege'] as List).single;
    expect(row['auftrag_ref'], 'a1');
    expect(row['lesestatus'], 'historisch_nicht_rekonstruiert');
    expect(row['host_lease'], isNull);
  });
  test('reads local projection without retaining the prompt', () async {
    final server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
    addTearDown(() => server.close(force: true));
    server.listen((request) {
      expect(request.uri.path, '/api/state');
      request.response.write(
        jsonEncode({
          'schema': 'aix.dashboard.v2',
          'projection_only': true,
          'timestamp': '2026-11-04T12:00:00Z',
          'components': [],
          'latest_goal': {'goal_id': 'G-1', 'prompt': 'private'},
          'latest_kernel_transaction': {
            'transaction_id': 'tx-1',
            'state': 'open',
            'created_at': '2026-11-04',
            'intent': 'private',
          },
        }),
      );
      request.response.close();
    });
    final result = await readLocalAix(port: server.port);
    expect(result['goal_id'], 'G-1');
    expect(result['kernel_transaction']['id'], 'tx-1');
    expect(result.toString(), isNot(contains('private')));
  });
  test('does not follow a redirect from local source', () async {
    final server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
    addTearDown(() => server.close(force: true));
    server.listen((request) {
      request.response.statusCode = 302;
      request.response.headers.set('location', 'http://example.invalid/');
      request.response.close();
    });
    await expectLater(readLocalAix(port: server.port), throwsFormatException);
  });
}
