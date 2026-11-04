import json

from aethel_projects import factory
from test_factory import _report


def test_role_declaration_and_fallback(tmp_path):
    declared = _report(tmp_path, 'omega_domain', files={'.aethel/projekt.json': json.dumps({'rolle': 'wissen'})})
    broken = _report(tmp_path, 'heritageBible', files={'.aethel/projekt.json': '{'})
    result = factory.build((declared, broken)).as_dict()
    assert result['rollen_quelle']['omega_domain'] == 'deklariert'
    assert result['rollen_quelle']['heritageBible'] == 'vermutung_name'
    assert 'omega_domain' in result['roles']['wissen']


def test_market_only_documents(tmp_path):
    bad = _report(tmp_path, 'bad', files={'src/landing_authority.rs': 'code'})
    good = _report(tmp_path, 'good', files={'landing/index.html': 'page'})
    assert 'Landing oder Marktmaterial' not in factory._stage_evidence(bad, 'markt')
    assert 'Landing oder Marktmaterial' in factory._stage_evidence(good, 'markt')


def test_duplicate_names_keep_distinct_repos(tmp_path):
    a = _report(tmp_path / 'a', 'same', files={'docs/SPEC.md': 'a'})
    b = _report(tmp_path / 'b', 'same', files={'docs/DESIGN.md': 'b'})
    stage = next(s for s in factory.build((a, b)).stages if s.key == 'entwurf')
    assert set(stage.covered_by) == {'same (a/same)', 'same (b/same)'}
    assert not stage.carriers


def test_profiles_exempt_only_applicable_requirements(tmp_path):
    app = _report(tmp_path, 'app', files={'pubspec.yaml': 'name: app', 'macos/main.swift': 'code'})
    unknown = _report(tmp_path, 'unknown', files={'.aethel/projekt.json': '{'}, maturity=90)
    data = factory.build((app, unknown)).as_dict()
    assert 'Container' in data['nicht_anwendbar']['app']
    assert not data['nicht_anwendbar']['unknown']


def test_end_to_end_requires_all_applicable_stages(tmp_path):
    repo = _report(tmp_path, 'partial', files={'docs/SPEC.md': 'spec'}, maturity=90)
    data = factory.build((repo,)).as_dict()
    assert not data['end_to_end']
    assert 'Strukturindikator' in data['end_to_end_bedeutung']
    assert 'Einzelrepo' in data['kettenintegritaet_bedeutung']


def test_proof_levels_are_explicit(tmp_path):
    data = factory.build((_report(tmp_path, 'x'),)).as_dict()
    assert data['nachweisstufen']['struktur'] == 'gemessen: Pfadtreffer'
    assert data['nachweisstufen']['integration'] == 'nicht gemessen'


def test_six_stages_are_not_end_to_end_but_all_are(tmp_path):
    files = {
        'README.md': 'purpose', 'landing/index.html': 'page',
        'docs/SPEC.md': 'spec', 'docs/DESIGN.md': 'design', 'docs/ARCHITECTURE.md': 'architecture',
        'src/main.py': 'print(42)', 'tests/test_x.py': 'test',
        '.github/workflows/ci.yml': 'ci', '.aix/validation-contract.json': '{"ok": true}',
        'VERSION': '1.0', 'Dockerfile': 'FROM alpine', 'deploy/app.yaml': 'app',
        'scripts/install.sh': 'install', 'run.sh': 'run', 'scripts/health.sh': 'health',
        'systemd/app.service': 'service', 'feedback.md': 'feedback',
        'docs/review.md': 'review', '.aix/pcg.json': '{"ok": true}',
    }
    full = _report(tmp_path, 'full', files=files, maturity=90)
    partial_files = {k: v for k, v in files.items() if k not in ('systemd/app.service', 'docs/review.md')}
    partial = _report(tmp_path, 'partial_six', files=partial_files, maturity=90)
    assert factory.build((full,)).end_to_end == ('full',)
    assert not factory.build((partial,)).end_to_end


def test_declared_profile_precedes_detection_and_research_stages(tmp_path):
    app = _report(tmp_path, 'app_override', files={
        '.aethel/projekt.json': '{"profil": "unbestimmt", "rolle": "experiment"}',
        'pubspec.yaml': 'name: app', 'macos/main.swift': 'code'})
    research = _report(tmp_path, 'research', files={'.aethel/projekt.json': '{"profil": "forschung"}'})
    data = factory.build((app,)).as_dict()
    assert data['nicht_anwendbar']['app_override'] == []
    view = factory.build((research,))
    assert next(s for s in view.stages if s.key == 'betrieb').level == 'nicht_anwendbar'
    assert next(s for s in view.stages if s.key == 'bau').level == 'leer'
