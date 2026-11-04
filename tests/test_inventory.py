"""Coverage regression tests: deep worktrees, bare repos, non-Git and failures."""
from pathlib import Path
from unittest.mock import patch
from conftest import make_repo, git
from aethel_projects.discovery import discover
from aethel_projects.inventory import build, census
from aethel_projects import gitio


def test_deep_hidden_worktree_and_bare(tmp_path):
    repo = make_repo(tmp_path / 'owner')
    wt = tmp_path / '.hidden' / 'nested' / 'worktrees' / 'deep'
    git(repo, 'worktree', 'add', '-b', 'deep', str(wt))
    (wt / 'dirty.txt').write_text('unsaved')
    bare = tmp_path / 'mirrors' / 'repository.git'
    bare.mkdir(parents=True)
    git(bare, 'init', '--bare')
    identities = discover(tmp_path)
    assert len(identities) == 2
    assert str(wt) in next(i for i in identities if i.path == str(repo)).worktree_paths
    result = build(tmp_path)
    assert result['summary']['repositories'] == 2
    assert result['summary']['git_markers'] == 3
    assert result['summary']['dirty_checkouts'] == 1
    assert result['summary']['bare_repositories'] == 1


def test_components_non_git_invalid_and_exclusions(tmp_path):
    repo = make_repo(tmp_path / 'real')
    (repo / 'package.json').write_text('{}')
    project = tmp_path / 'ungit' / 'nested'
    project.mkdir(parents=True)
    (project / 'pyproject.toml').write_text('')
    bad = tmp_path / 'broken'
    bad.mkdir()
    (bad / '.git').write_text('gitdir: missing')
    excluded = tmp_path / 'node_modules'
    excluded.mkdir()
    make_repo(excluded / 'dependency')
    (tmp_path / 'alias').symlink_to(repo, target_is_directory=True)
    result = build(tmp_path)
    assert result['summary']['invalid_git_markers'] == 1
    assert [p['path'] for p in result['projects_without_git']] == [str(project)]
    assert str(excluded) in result['excluded_paths']
    assert len(result['symlinks']) == 1
    assert len(result['top_entries']) == 5


def test_root_itself_and_worktree_with_owner_outside(tmp_path):
    owner = make_repo(tmp_path / 'outside')
    root = tmp_path / 'scan'
    root.mkdir()
    wt = root / 'only'
    git(owner, 'worktree', 'add', '-b', 'feature', str(wt))
    identity = discover(root)[0]
    assert identity.path == str(wt)
    registrations = build(root)['repositories'][0]['registered_worktrees']
    assert any(w['path'] == str(owner) and w['outside_root'] for w in registrations)
    assert discover(owner)[0].path == str(owner)
    assert census(tmp_path / 'absent')['errors']


def test_runtime_rejects_writes_and_network_before_subprocess(tmp_path):
    with patch('subprocess.run') as run:
        for args in [('push',), ('fetch',), ('remote', 'add', 'x', 'url'),
                     ('config', 'user.name', 'changed'), ('worktree', 'add', 'x')]:
            assert gitio.run_git(tmp_path, *args) is None
        run.assert_not_called()


def test_project_profile_binding_is_observed_not_invented(tmp_path):
    import json
    repo = make_repo(tmp_path / 'bound')
    profile = repo / '.aix' / 'project-profile.json'
    profile.parent.mkdir()
    profile.write_text(json.dumps({'project_id': 'bound', 'rollen': {'bauer': 'builder'}}))
    result = build(tmp_path)['repositories'][0]
    assert result['checkout_profile']['roles'] == {'bauer': 'builder'}
    assert not result['validation_contract_present']
    profile.write_text('{broken')
    assert build(tmp_path)['repositories'][0]['checkout_profile']['state'] == 'unreadable'
