import hashlib
import json
from types import SimpleNamespace

from conftest import git
from aethel_projects import codeanalysis, dossier


def test_analyzer_findings_bound_to_committed_content(mini_repo, tmp_path, monkeypatch):
    source = mini_repo / 'lib.rs'
    source.write_text('fn example() {}\n')
    git(mini_repo, 'add', 'lib.rs')
    git(mini_repo, 'commit', '-qm', 'add code')
    head = git(mini_repo, 'rev-parse', 'HEAD')
    binary = tmp_path / 'analyzer'
    binary.touch()
    monkeypatch.setattr(codeanalysis, 'find_analyzer', lambda: binary)
    monkeypatch.setattr(codeanalysis, '_analyzer_version', lambda _: '1.2')
    document = {'schema': codeanalysis.AIX_SCHEMA, 'findings': [
        {'file': 'lib.rs', 'line': 1, 'rule': 'example'},
        {'file': 'lib.rs', 'line': 8, 'rule': 'invalid'},
        {'file': '../outside', 'line': 1, 'rule': 'escape'}]}
    real_run = codeanalysis.subprocess.run
    def fake_run(command, **kwargs):
        if command[0] == 'nice':
            return SimpleNamespace(returncode=0, stdout=json.dumps(document), stderr='')
        return real_run(command, **kwargs)
    monkeypatch.setattr(codeanalysis.subprocess, 'run', fake_run)
    result = codeanalysis.head_findings(mini_repo, head)
    assert result['status'] == 'geprueft'
    assert result['findings'] == [{'path': 'lib.rs', 'line': 1, 'regel': 'example',
        'analyzer_version': '1.2', 'commit': head, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}]
    source.write_text('dirty\n')
    assert codeanalysis.head_findings(mini_repo, head)['findings'] == []


def test_missing_analyzer_is_not_an_empty_success(empty_report, tmp_path, monkeypatch):
    monkeypatch.setattr(codeanalysis, 'find_analyzer', lambda: None)
    root = tmp_path / 'repo'
    root.mkdir()
    row = empty_report.as_dict()
    row['path'] = str(root)
    result = dossier.project(row)
    assert result['code_befunde']['status'] == 'nicht_geprueft'
    assert result['code_befunde']['grund']


def test_stub_findings_bound_to_head_and_dirty_files_excluded(mini_repo, empty_report, monkeypatch):
    from dataclasses import replace
    monkeypatch.setattr(codeanalysis, 'find_analyzer', lambda: None)
    source = mini_repo / 'app.py'
    source.write_text('def unfinished(): pass\n')
    git(mini_repo, 'add', 'app.py')
    git(mini_repo, 'commit', '-qm', 'stub')
    head = git(mini_repo, 'rev-parse', 'HEAD')
    row = replace(empty_report, path=str(mini_repo)).as_dict()
    result = dossier.project(row)
    assert result['stubs'][0]['commit'] == head
    assert result['stubs'][0]['sha256'] == hashlib.sha256(source.read_bytes()).hexdigest()
    source.write_text('def changed(): pass\n')
    assert dossier.project(row)['stubs'] == []


def test_analyzer_version_runs_at_low_priority(monkeypatch, tmp_path):
    calls = []
    def fake_run(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(stdout='1.2', returncode=0)
    monkeypatch.setattr(codeanalysis.subprocess, 'run', fake_run)
    assert codeanalysis._analyzer_version(tmp_path / 'analyzer') == '1.2'
    assert calls[0][:3] == ['nice', '-n', '10']


def test_unknown_analyzer_version_is_not_checked(mini_repo, tmp_path, monkeypatch):
    head = git(mini_repo, 'rev-parse', 'HEAD')
    binary = tmp_path / 'analyzer'
    binary.touch()
    monkeypatch.setattr(codeanalysis, 'find_analyzer', lambda: binary)
    monkeypatch.setattr(codeanalysis, '_analyzer_version', lambda _: 'unbekannt')
    real_run = codeanalysis.subprocess.run
    def fake_run(command, **kwargs):
        if command[0] == 'nice':
            return SimpleNamespace(returncode=0, stdout=json.dumps({'schema': codeanalysis.AIX_SCHEMA, 'findings': []}), stderr='')
        return real_run(command, **kwargs)
    monkeypatch.setattr(codeanalysis.subprocess, 'run', fake_run)
    assert codeanalysis.head_findings(mini_repo, head)['status'] == 'nicht_geprueft'
