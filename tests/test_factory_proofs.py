from aethel_projects import factory
from test_factory import _report


def test_paths_are_not_maturity_and_proofs_have_digests(tmp_path):
    repo = _report(tmp_path, 'sample', files={
        'docs/SPEC.md': '', 'docs/DESIGN.md': 'TODO: implement\n',
        'src/main.py': 'def work():\n    return 42\n'})
    view = factory.build((repo,)).as_dict()
    assert view['schema'] == 'aethel.projects.factory/v2'
    assert view['vorhanden']
    assert all(p['path'] not in ('docs/SPEC.md', 'docs/DESIGN.md') for p in view['belegt'])
    assert all(len(p['sha256']) == 64 and p['quelle'] for p in view['belegt'])
    assert view['reife'] <= 100


def test_production_stubs_reduce_maturity(tmp_path):
    clean = _report(tmp_path, 'clean', files={'src/app.py': 'def run():\n    return 1\n'})
    stub = _report(tmp_path, 'stub', files={'src/app.py': 'def run():\n    pass\n'})
    a = factory.build((clean,)).as_dict()
    b = factory.build((stub,)).as_dict()
    assert b['stubs']
    assert b['reife'] < a['reife']
