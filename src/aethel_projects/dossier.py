"""Evidence-backed project dossiers for a future project-management consumer.

An observation/proposal export, never a scheduler, task store or execution grant.
Documents are declarations, not proof of implemented architecture or behaviour.
"""
from __future__ import annotations

import hashlib
import json
import re
import tomllib
from datetime import datetime
from pathlib import Path

from . import gitio

SCHEMA = 'aethel.projects.pm-input/v1'
DOCUMENTS = ('README.md', 'docs/SPEC.md', 'SPEC.md', 'docs/ARCHITECTURE.md',
             'ARCHITECTURE.md', 'docs/architecture/README.md', '.aix/architecture.md',
             'docs/DESIGN.md', 'docs/ENTWURF.md', 'docs/STATUS.md')
MANIFESTS = ('Cargo.toml', 'pyproject.toml', 'package.json', 'pubspec.yaml')
MAX_BYTES = 256_000


def _source(root: Path, relative: str) -> dict | None:
    path = root / relative
    # Dossiers must not follow a document link out of the project.
    if not path.exists():
        return None
    if not path.resolve().is_relative_to(root.resolve()):
        return {'path': relative, 'state': 'outside_project', 'sha256': None}
    try:
        with path.open('rb') as stream:
            raw = stream.read(MAX_BYTES + 1)
    except OSError as error:
        return {'path': relative, 'state': 'unreadable', 'error': str(error), 'sha256': None}
    if len(raw) > MAX_BYTES:
        return {'path': relative, 'state': 'over_limit', 'sha256': None}
    content = raw.decode('utf-8', errors='replace')
    lines = content.splitlines()
    excerpt = '\n'.join(lines[:60])[:3000]
    return {'path': relative, 'state': 'read', 'sha256': hashlib.sha256(raw).hexdigest(),
            'source_kind': 'working_copy', 'excerpt': excerpt,
            'excerpt_truncated': excerpt != content.rstrip('\n'),
            'line_start': 1, 'headings': [x for x in lines if re.match(r'^#{1,4} ', x)][:30]}


def _local_dependencies(root: Path) -> tuple[list[dict], list[dict]]:
    dependencies, errors = [], []
    cargo = root / 'Cargo.toml'
    if cargo.is_file():
        try:
            # Same size and path constraints as documentary evidence.
            proof = _source(root, 'Cargo.toml')
            if proof['state'] != 'read':
                raise ValueError(proof['state'])
            document = tomllib.loads(cargo.read_text())
            sections = {k: document.get(k, {}) for k in ('dependencies', 'dev-dependencies', 'build-dependencies')}
            sections['workspace.dependencies'] = document.get('workspace', {}).get('dependencies', {})
            for section, values in sections.items():
                for name, spec in values.items():
                    if isinstance(spec, dict) and isinstance(spec.get('path'), str):
                        destination = (root / spec['path']).resolve()
                        dependencies.append({'name': name, 'kind': 'cargo_path', 'declared_path': spec['path'],
                            'resolved_path': str(destination), 'exists': destination.is_dir(),
                            'source': 'Cargo.toml', 'section': section, 'sha256': proof['sha256']})
        except (OSError, ValueError, AttributeError) as error:
            errors.append({'source': 'Cargo.toml', 'error': str(error)})
    return dependencies, errors


def project(repo: dict) -> dict:
    root = Path(repo['path'])
    documents = [proof for name in DOCUMENTS if (proof := _source(root, name)) is not None]
    manifests = [proof for name in MANIFESTS if (proof := _source(root, name)) is not None]
    dependencies, errors = _local_dependencies(root)
    architecture = [d for d in documents if 'architecture' in d['path'].lower()]
    gaps = []
    if not (repo.get('intent') or {}).get('text'):
        gaps.append({'code': 'intent_unknown', 'evidence': 'scan.intent', 'question': 'Welchem Nutzerproblem dient das Projekt?'})
    if not any(d['state'] == 'read' for d in architecture):
        gaps.append({'code': 'architecture_unknown', 'evidence': list(DOCUMENTS),
                     'question': 'Wo stehen Komponenten, Zuständigkeiten und Schnittstellen?'})
    if repo.get('commits_not_on_main', 0):
        gaps.append({'code': 'unlanded_work', 'evidence': 'scan.unmerged_branches',
                     'question': 'Welche Arbeit bleibt gültig, welche ist überholt? Nicht pauschal mergen.'})
    return {'repository_id': repo['git_common_dir'], 'name': repo['name'], 'path': repo['path'],
        'observed_head': gitio.run_git(root, 'rev-parse', '--verify', 'HEAD'),
        'intent': {'declared': repo.get('intent'), 'implemented': 'not_verified'},
        'architecture': {'state': 'documented' if any(d['state'] == 'read' for d in architecture) else 'unknown',
                         'sources': architecture, 'runtime_conformance': 'not_verified'},
        'documents': documents, 'manifests': manifests,
        'relationships': {'declared_local_dependencies': dependencies,
                          'coverage': 'root Cargo path dependencies only; not a complete dependency graph',
                          'errors': errors},
        'forensics': {key: repo.get(key) for key in ('current_branch', 'default_branch', 'worktree_paths',
            'commits_total', 'commits_not_on_main', 'unmerged_branches', 'dirty_files', 'last_commit_date')},
        'findings': repo.get('findings', []), 'questions_for_project_management': gaps,
        'authority': 'observation_only; no role, assignment, execution or merge permission'}


def build(snapshot: dict) -> dict:
    if snapshot.get('schema') != 'aethel.projects/v1' or not isinstance(snapshot.get('repos'), list):
        raise ValueError('Expected aethel.projects/v1 scan snapshot')
    return {'schema': SCHEMA, 'generated_at': datetime.now().astimezone().isoformat(timespec='seconds'),
        'scan_generated_at': snapshot['generated_at'], 'workspace_root': snapshot['workspace_root'],
        'consumer': 'aethelProjectManagement (proposed export; consumer not verified)',
        'projects': [project(repo) for repo in snapshot['repos']],
        'limitations': ['Git metrics come from the dated scan; documents and observed_head are read at export time.',
            'Working-copy documents may be uncommitted, outdated, templates or incompatible with current origin/main.',
            'Documented intent and architecture do not prove implementation, integration or product acceptance.',
            'Git histories and clones are not automatically distinct products; stable product assignment needs the authoritative registry.',
            'Questions are inputs for project management, never executable work orders.']}
