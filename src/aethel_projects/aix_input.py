"""Attach project observations to the existing AIX engineering input.

This adapter changes context only. AIX compiles a new proposal digest and owns
review, role/lease checks, approval, execution and landing. No second task store.
"""
from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from . import gitio
from .dossier import SCHEMA as DOSSIER_SCHEMA


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def _fresh(value: str, now: datetime, max_age_s: int) -> None:
    try:
        stamp = datetime.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError('Evidence timestamp missing or invalid') from exc
    if stamp.tzinfo is None:
        raise ValueError('Evidence timestamp must include timezone')
    age = (now - stamp).total_seconds()
    if age < -120 or age > max_age_s:
        raise ValueError('Evidence is stale or from the future; regenerate the dossier')


def attach(source: dict, export: dict, *, max_age_s: int = 3600,
           now: datetime | None = None) -> dict:
    """Return an unapproved AIX input bound to one exact local project dossier."""
    if not isinstance(source, dict) or source.get('schema') != 'aix.engineering_input.v1':
        raise ValueError('Expected raw aix.engineering_input.v1; compiled/approved packages cannot be edited')
    if source.get('approval') or source.get('proposal_digest') or source.get('dispatch_ready'):
        raise ValueError('An approved or sealed input must be proposed again, never amended')
    if not isinstance(export, dict) or export.get('schema') != DOSSIER_SCHEMA:
        raise ValueError('Expected aethel.projects.pm-input/v1 dossier export')
    if not isinstance(max_age_s, int) or isinstance(max_age_s, bool) or max_age_s <= 0:
        raise ValueError('max_age_s must be positive')
    moment = now or datetime.now(timezone.utc)
    _fresh(export.get('generated_at'), moment, max_age_s)
    _fresh(export.get('scan_generated_at'), moment, max_age_s)
    project = source.get('project')
    if not isinstance(project, dict) or not isinstance(project.get('path'), str):
        raise ValueError('AIX input must contain an explicit project.path')
    path = Path(project['path'])
    if not path.is_absolute() or not path.is_dir():
        raise ValueError('project.path must name an existing absolute project directory')
    path = path.resolve()
    matches = [row for row in export.get('projects', [])
               if isinstance(row, dict) and isinstance(row.get('path'), str)
               and Path(row['path']).resolve() == path]
    if len(matches) != 1:
        raise ValueError('Project evidence missing or ambiguous; names are not project identity')
    dossier = matches[0]
    common = gitio.run_git(path, 'rev-parse', '--path-format=absolute', '--git-common-dir')
    head = gitio.run_git(path, 'rev-parse', '--verify', 'HEAD')
    if not common or not dossier.get('repository_id') or Path(common).resolve() != Path(dossier['repository_id']).resolve():
        raise ValueError('Repository identity mismatch')
    if not head or head != dossier.get('observed_head'):
        raise ValueError('Project HEAD changed; regenerate the dossier')
    # Check documentary evidence again before binding it. Hashes do not turn
    # declarations into implementation/test receipts or authenticated authority.
    for proof in dossier.get('documents', []) + dossier.get('manifests', []):
        if proof.get('state') != 'read':
            continue
        relative = proof.get('path')
        if not isinstance(relative, str) or Path(relative).is_absolute():
            raise ValueError('Evidence path must be project-relative')
        target = (path / relative).resolve()
        if not target.is_relative_to(path):
            raise ValueError('Evidence path escapes project')
        try:
            with target.open('rb') as handle:
                content = handle.read(256_001)
        except OSError as exc:
            raise ValueError(f'Evidence source unavailable: {relative}') from exc
        if len(content) > 256_000 or hashlib.sha256(content).hexdigest() != proof.get('sha256'):
            raise ValueError(f'Evidence source changed: {relative}')
    context = source.get('context', {})
    if not isinstance(context, dict):
        raise ValueError('AIX context must be an object')
    if 'project_evidence' in context:
        raise ValueError('Existing project_evidence must not be silently overwritten')
    result = copy.deepcopy(source)
    result.setdefault('context', {})['project_evidence'] = {
        'producer': 'aethelProjects', 'source_schema': DOSSIER_SCHEMA,
        'source_digest': digest(dossier), 'input_before_digest': digest(source),
        'generated_at': export['generated_at'], 'scan_generated_at': export['scan_generated_at'],
        'bound_head': head, 'repository_id': str(Path(common).resolve()),
        'trust': 'untrusted_project_observations; no execution or acceptance authority',
        'limitations': copy.deepcopy(export.get('limitations', [])),
        'dossier': copy.deepcopy(dossier),
    }
    return result
