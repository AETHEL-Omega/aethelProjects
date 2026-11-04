/// Adapts explicitly selected source documents for display; never grants authority.
Map<String, dynamic> readCockpit(Map<String, dynamic> data, String source) {
  if (data['schema'] != 'aethel.projects.cockpit/v1' ||
      data['kacheln'] is! List ||
      data['fehlt'] is! List ||
      data['quellen'] is! Map) {
    throw const FormatException('Ungültiger Projects-Leitstand');
  }
  for (final tile in data['kacheln'] as List) {
    if (tile is! Map ||
        tile['titel'] is! String ||
        tile['wert'] is! String ||
        tile['quelle'] is! String) {
      throw const FormatException('Ungültige Projects-Kachel');
    }
  }
  return {
    'schema': 'aethel.plm.cockpit-observation/v1',
    'source_id': source,
    'tiles': data['kacheln'],
    'missing': data['fehlt'],
    'sources': data['quellen'],
  };
}

Map<String, dynamic> readAixDashboard(
  Map<String, dynamic> data,
  String source,
) {
  if (data['schema'] != 'aix.dashboard.v2' ||
      data['projection_only'] != true ||
      data['timestamp'] is! String ||
      data['components'] is! List ||
      (data['latest_goal'] != null && data['latest_goal'] is! Map)) {
    throw const FormatException('Ungültige AIX-Dashboardprojektion');
  }
  final goal = data['latest_goal'] as Map?;
  // Do not retain prompt, raw telemetry, credentials, or unrelated ledgers.
  return {
    'source': source,
    'timestamp': data['timestamp'],
    'goal_id': goal?['goal_id'],
    'state': goal?['state'],
    'proof': goal?['proof'],
    'missing_bindings': goal?['missing_bindings'],
  };
}

Map<String, dynamic> readFactoryInput(
  Map<String, dynamic> data,
  String source,
) {
  if (data['schema'] != 'aix.engineering_input.v1' ||
      data['metadata'] is! Map ||
      data['project'] is! Map ||
      data['factory'] is! Map) {
    throw const FormatException('Kein AIX Engineering Input mit Fabrikteil');
  }
  final meta = data['metadata'] as Map;
  final factory = data['factory'] as Map;
  if (meta['id'] is! String ||
      (meta['id'] as String).trim().isEmpty ||
      (factory['pom'] != 'aix.production_operations_model.v1' &&
          factory['pom'] != 'aix.production_operations_model.v2')) {
    throw const FormatException('Auftragskennung oder POM-Version fehlt');
  }
  // This is a source assertion, not a POM validator or a product binding.
  return {
    'source': source,
    'id': meta['id'],
    'revision': meta['revision'],
    'project': data['project'],
    'enabled': factory['enabled'],
    'pom': factory['pom'],
    'work_order_id': factory['work_order_id'],
    'line': factory['line'],
    'station': factory['station'],
    'product_binding': factory['product_binding'],
    'substrate_binding': factory['substrate_binding'],
    'output_contract': factory['output_contract'],
  };
}
