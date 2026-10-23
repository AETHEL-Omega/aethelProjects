import copy
import hashlib
from datetime import datetime, timezone, timedelta

import pytest

from aethel_projects.aix_input import attach, digest
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


def test_only_context_changes_and_no_approval_or_authority_is_added(case):
    source, export, repo = case
    original = copy.deepcopy(source)
    result = attach(source, export)
    evidence = result['context'].pop('project_evidence')
    assert result == source == original
    assert evidence['source_digest'] == digest(export['projects'][0])
    assert evidence['bound_head'] == git(repo, 'rev-parse', 'HEAD')
    assert 'untrusted' in evidence['trust']
    assert 'approval' not in result


@pytest.mark.parametrize('mutation', ['head', 'file', 'duplicate', 'identity', 'stale', 'future', 'approval', 'sealed', 'overwrite', 'escape'])
def test_invalid_or_changed_evidence_fails_closed(case, mutation):
    source, export, repo = case
    row = export['projects'][0]
    if mutation == 'head':
        row['observed_head'] = '0' * 40
    elif mutation == 'file':
        (repo / 'README.md').write_text('changed')
    elif mutation == 'duplicate':
        export['projects'].append(copy.deepcopy(row))
    elif mutation == 'identity':
        row['repository_id'] = str(repo / 'other.git')
    elif mutation in ('stale', 'future'):
        delta = timedelta(hours=-2 if mutation == 'stale' else 2)
        export['generated_at'] = (datetime.now(timezone.utc) + delta).isoformat()
    elif mutation == 'approval':
        source['approval'] = {'state': 'APPROVED'}
    elif mutation == 'sealed':
        source['schema'] = 'aix.engineering_work_package.v2'
    elif mutation == 'overwrite':
        source['context']['project_evidence'] = {'old': 'retained'}
    elif mutation == 'escape':
        row['documents'][0]['path'] = '../outside'
    with pytest.raises(ValueError):
        attach(source, export)
