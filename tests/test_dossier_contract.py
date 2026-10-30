import copy

import pytest

from aethel_projects.aix_input import attach
from aethel_projects.dossier import build
from test_aix_input import case  # noqa: F401


def test_pm_import_is_not_claimed_without_consumer_evidence(empty_report, tmp_path):
    snapshot = {'schema': 'aethel.projects/v1', 'generated_at': 'fixture',
                'workspace_root': str(tmp_path), 'repos': [empty_report.as_dict()]}
    assert build(snapshot)['pm_import'] == 'nicht_belegt'


@pytest.mark.parametrize('field', ['documents', 'manifests'])
def test_v1_consumer_contract_requires_evidence_lists(case, field):
    source, export, _ = case
    export = copy.deepcopy(export)
    del export['projects'][0][field]
    with pytest.raises(ValueError):
        attach(source, export)


def test_consumer_rejects_changed_code_evidence(case):
    import hashlib
    from conftest import git
    source, export, repo = case
    path = repo / 'code.py'
    path.write_text('def unfinished(): pass\n')
    git(repo, 'add', 'code.py')
    git(repo, 'commit', '-qm', 'code')
    row = export['projects'][0]
    row['observed_head'] = git(repo, 'rev-parse', 'HEAD')
    row['stubs'] = [{'path': 'code.py', 'line': 1, 'commit': row['observed_head'],
                     'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}]
    attach(source, export)
    path.write_text('changed\n')
    with pytest.raises(ValueError):
        attach(source, export)
