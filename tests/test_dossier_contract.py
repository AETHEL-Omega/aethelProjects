import copy
import hashlib
from datetime import datetime, timezone

import pytest

from aethel_projects.aix_input import attach
from aethel_projects.dossier import build
from conftest import git


@pytest.fixture
def case(mini_repo):
    stamp = datetime.now(timezone.utc).isoformat()
    document = mini_repo / 'README.md'
    document.write_text('# Project\nDeclared goal.\n')
    source = {'schema': 'aix.engineering_input.v1',
        'project': {'path': str(mini_repo)},
        'context': {'existing': 'retained'},
        'execution': {'compute_mode': 'LOCAL_AI_ONLY'},
        'scope': {'include': ['src/'], 'allowed_effects': ['read']}}
    dossier = {'path': str(mini_repo), 'name': 'display-only',
        'repository_id': git(mini_repo, 'rev-parse', '--path-format=absolute', '--git-common-dir'),
        'observed_head': git(mini_repo, 'rev-parse', 'HEAD'),
        'documents': [{'path': 'README.md', 'state': 'read',
                       'sha256': hashlib.sha256(document.read_bytes()).hexdigest()}],
        'manifests': []}
    export = {'schema': 'aethel.projects.pm-input/v1', 'generated_at': stamp,
              'scan_generated_at': stamp, 'projects': [dossier]}
    return source, export, mini_repo



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
