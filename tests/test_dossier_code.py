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
    monkeypatch.setattr(codeanalysis.subprocess, 'run', lambda *a, **k:
                        SimpleNamespace(returncode=0, stdout=json.dumps(document), stderr=''))
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
