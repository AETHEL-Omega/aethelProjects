from dataclasses import replace
import hashlib
import pytest
from aethel_projects.dossier import project, build
from aethel_projects.models import Intent


def test_architecture_evidence_dependencies_and_no_execution(empty_report, tmp_path):
    root = tmp_path / 'project'
    (root / 'docs').mkdir(parents=True)
    content = b'# Architecture\n\nCLI -> core\n'
    (root / 'docs/ARCHITECTURE.md').write_bytes(content)
    (root / 'Cargo.toml').write_text('[dependencies]\nmissing = {path = "../missing"}\n')
    report = replace(empty_report, path=str(root), commits_not_on_main=3,
                     intent=Intent('Declared goal', 'high', 'docs/SPEC.md'))
    result = project(report.as_dict())
    assert result['intent']['implemented'] == 'not_verified'
    assert result['architecture']['sources'][0]['sha256'] == hashlib.sha256(content).hexdigest()
    assert result['architecture']['runtime_conformance'] == 'not_verified'
    assert result['relationships']['declared_local_dependencies'][0]['exists'] is False
    assert any(q['code'] == 'unlanded_work' for q in result['questions_for_project_management'])
    assert result['repository_id'] == report.git_common_dir


def test_no_architecture_is_unknown_and_external_link_not_read(empty_report, tmp_path):
    root = tmp_path / 'project'
    root.mkdir()
    outside = tmp_path / 'outside'
    outside.write_text('must not be read')
    (root / 'ARCHITECTURE.md').symlink_to(outside)
    result = project(replace(empty_report, path=str(root)).as_dict())
    assert result['architecture']['sources'][0]['state'] == 'outside_project'
    assert result['architecture']['state'] == 'unknown'
    assert any(q['code'] == 'architecture_unknown' for q in result['questions_for_project_management'])
    assert 'must not be read' not in str(result)
    with pytest.raises(ValueError):
        build({'schema': 'foreign'})


def test_cli_exports_snapshot_without_starting_a_new_scan(empty_report, tmp_path, monkeypatch):
    import json
    from aethel_projects import cli
    monkeypatch.setattr(cli, 'scan_workspace', lambda *a, **k: pytest.fail('unexpected rescan'))
    snapshot = tmp_path / 'scan.json'
    snapshot.write_text(json.dumps({'schema': 'aethel.projects/v1', 'generated_at': 'fixture',
        'workspace_root': str(tmp_path), 'repos': [empty_report.as_dict()]}))
    output = tmp_path / 'pm.json'
    assert cli.main(['dossier', '--root', str(tmp_path), '--snapshot', str(snapshot), '--out', str(output)]) == 0
    result = json.loads(output.read_text())
    assert result['schema'] == 'aethel.projects.pm-input/v1'
    assert result['scan_generated_at'] == 'fixture'
    assert len(result['projects']) == 1
