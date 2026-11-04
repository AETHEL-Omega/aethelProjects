"""Repeat the existing read-only inventory and publish a bounded local observation."""
from __future__ import annotations

from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import time

from . import inventory, gitio, intent
from .work_history import _write_private, private_directory

SCHEMA = 'aethel.projects.inventory-live/v1'


def _complete(scan):
    summary = scan.get('summary') or {}
    return not scan.get('errors') and not summary.get('filesystem_errors') and not summary.get('checkout_errors')


def _identity(scan):
    return {x['git_common_dir']: x for x in scan.get('repositories', []) if x.get('git_common_dir')}


def _checkouts(scan):
    return {x['path']: {k: x.get(k) for k in ('head', 'branch', 'dirty_files', 'git_common_dir', 'dirty_signature')}
            for x in scan.get('checkouts', []) if x.get('path')}


def enrich_dirty(scan):
    """Fingerprint Git status and metadata for directly listed paths, without reading content."""
    for checkout in scan.get('checkouts', []):
        if not checkout.get('dirty_files') or not checkout.get('path'):
            continue
        root = Path(checkout['path'])
        status = gitio.run_git(root, 'status', '--porcelain', '-z', '--untracked-files=normal')
        if status is None:
            checkout['dirty_signature'] = None
            checkout.setdefault('errors', []).append('dirty fingerprint unavailable')
            scan.setdefault('summary', {})['checkout_errors'] = scan.get('summary', {}).get('checkout_errors', 0) + 1
            continue
        digest = hashlib.sha256(status.encode('utf-8'))
        for part in status.split('\0'):
            if len(part) >= 4 and part[2] == ' ':
                relative = part[3:]
            elif len(part) >= 3 and part[1] == ' ':
                # gitio strips leading whitespace from the first porcelain row.
                relative = part[2:]
            else:
                continue
            path = root / relative
            try:
                stat = path.lstat()
                digest.update(f'{stat.st_ino}:{stat.st_size}:{stat.st_mtime_ns}:{stat.st_mode}'.encode())
            except OSError:
                digest.update(b'unavailable')
        checkout['dirty_signature'] = digest.hexdigest()
    scan.setdefault('limitations', []).append('Dirty fingerprints use Git status and file metadata, not contents; nested untracked contents and equal metadata can escape detection.')
    return scan


def enrich_purposes(scan):
    """Reuse Projects' README extraction as a bounded, source-labelled observation."""
    checkouts = {x.get('path'): x for x in scan.get('checkouts', [])}
    for group in scan.get('repositories', []):
        paths = group.get('paths') or []
        common = Path(group.get('git_common_dir') or '/')
        primary = str(common.parent) if common.name == '.git' and str(common.parent) in paths else (paths[0] if paths else None)
        if not primary:
            continue
        root = Path(primary)
        for name in ('README.md', 'README.rst', 'README.txt'):
            path = root / name
            try:
                if path.is_symlink() or not path.is_file() or path.stat().st_size > 256_000:
                    continue
                before = path.read_bytes()
                purpose = intent._from_readme(path)
                after = path.read_bytes()
                if before != after or not purpose or not purpose.text:
                    continue
                checkout = checkouts.get(primary) or {}
                group['readme_purpose'] = {'text': purpose.text, 'source': str(path),
                    'sha256': hashlib.sha256(after).hexdigest(), 'head_observed': checkout.get('head'),
                    'dirty_files': checkout.get('dirty_files'), 'confidence': purpose.confidence,
                    'limitation': 'README working-copy statement; not proof of implemented or installed behavior.'}
                break
            except OSError:
                continue
    return scan


def attach_observations(scan, directory):
    """Attach source-backed notes only on exact repository, checkout and source bytes."""
    if not directory:
        return scan
    try:
        base = Path(directory).expanduser().resolve()
        observations = json.loads((base / 'direct-observations.json').read_text())
        findings = json.loads((base / 'independent-findings.json').read_text())
        if not isinstance(observations.get('projects'), list) or not isinstance(findings.get('findings'), list):
            raise ValueError('invalid observation sources')
    except (OSError, ValueError, AttributeError):
        scan['external_observation_status'] = 'unavailable_or_invalid'
        return scan
    scan['external_observation_status'] = 'available_untrusted'
    checkouts = {x.get('path'): x for x in scan.get('checkouts', [])}
    by_common = {x.get('git_common_dir'): x for x in scan.get('repositories', [])}
    for obs in observations['projects']:
        if not isinstance(obs, dict):
            continue
        group = by_common.get(obs.get('common_dir'))
        checkout = checkouts.get(obs.get('path'))
        if not group or not checkout or checkout.get('git_common_dir') != obs.get('common_dir'):
            continue
        summary = {'state': 'no_matching_verified_finding', 'observed_at': obs.get('observed_at'),
                   'checkout': obs.get('path'), 'observed_head': obs.get('head')}
        group['direct_observation'] = summary
        if not obs.get('head') or checkout.get('head') != obs.get('head'):
            summary['state'] = 'stale_revision'
            continue
        if isinstance(obs.get('recent'), str):
            summary['recent'] = obs['recent'][:1000]
        repo = Path(obs['path']).resolve()
        for item in findings['findings']:
            if not isinstance(item, dict) or not isinstance(item.get('sources'), list) or not item['sources']:
                continue
            valid = True
            evidence = []
            for source in item['sources']:
                if not isinstance(source, dict) or not isinstance(source.get('path'), str):
                    valid = False; break
                path = Path(source['path'])
                try:
                    resolved = path.resolve(strict=True)
                    if not resolved.is_relative_to(repo) or not resolved.is_file() or resolved.stat().st_size > 2_000_000:
                        valid = False; break
                    digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
                    if digest != source.get('sha256'):
                        valid = False; break
                    evidence.append({'path': str(resolved), 'line': source.get('line'), 'sha256': digest})
                except OSError:
                    valid = False; break
            if valid:
                summary.update(state='source_bytes_match', purpose=item.get('purpose'),
                               finding=item.get('finding'), next_step=item.get('next_step'), sources=evidence,
                               limitation='Source observation, not a test, authority or installed-state proof.')
                break
    # Previously generated analyzer observations are optional, never executed here.
    for report_path in sorted(base.glob('*-analyzer.json'))[:100]:
        try:
            if report_path.is_symlink() or report_path.stat().st_size > 2_000_000:
                continue
            raw = report_path.read_bytes()
            report = json.loads(raw)
            run_path = report_path.with_name(report_path.name.replace('-analyzer.json', '-analyzer-run.json'))
            if run_path.is_symlink() or run_path.stat().st_size > 1_000_000:
                continue
            receipt = json.loads(run_path.read_text())
            if (report.get('schema') != 'aethel.code_analyzer.aix_findings.v1'
                    or receipt.get('returncode') != 0 or receipt.get('sha256') != hashlib.sha256(raw).hexdigest()
                    or not isinstance(report.get('findings'), list)):
                continue
            scope = report.get('scope')
            checkout = checkouts.get(scope)
            group = by_common.get(checkout.get('git_common_dir')) if checkout else None
            if not group or not isinstance(scope, str):
                continue
            project = Path(scope).resolve()
            digests = (report.get('scan') or {}).get('file_digests')
            if not isinstance(digests, dict) or not digests or len(digests) > 10_000:
                continue
            changed = 0
            for name, digest in digests.items():
                try:
                    relative = Path(name)
                    if relative.is_absolute() or '..' in relative.parts:
                        changed += 1; continue
                    path = (project / relative).resolve(strict=True)
                    if not path.is_relative_to(project) or not path.is_file() or path.stat().st_size > 4_000_000:
                        changed += 1; continue
                    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                        changed += 1
                except (OSError, TypeError, ValueError):
                    changed += 1
            findings_out = []
            for item in report['findings'][:100]:
                if isinstance(item, dict):
                    findings_out.append({key: item.get(key) for key in
                                         ('file', 'line', 'rule', 'severity', 'message', 'evidence_tier', 'kind')})
            group['analyzer_observation'] = {'source': str(report_path), 'observed_at': receipt.get('observed_at'),
                'release_reported': receipt.get('installed_release'), 'output_sha256': receipt['sha256'],
                'source_state': 'matched_scanned_files' if not changed else 'stale_or_missing_scanned_files',
                'changed_or_unavailable_files': changed, 'scanned_file_count': len(digests),
                'incomplete_reasons': (report.get('scan') or {}).get('incomplete_reasons', []),
                'truncated': report.get('truncated'), 'reported_finding_count': len(report['findings']),
                'findings': findings_out, 'limitation': 'Reported bounded scan; matching scanned files is not full-scope coverage, a clean result or a current release proof.'}
        except (OSError, ValueError, AttributeError, TypeError):
            continue
    return scan


def observe(root, previous=None, *, jobs=4, builder=None, observations_dir=None):
    """A delta is an observation, not a product or deletion decision."""
    now = datetime.now(timezone.utc).isoformat()
    result = {'schema': SCHEMA, 'attempted_at': now, 'status': 'ok', 'scan': None,
              'changes': {'new_repositories': [], 'changed_checkouts': [], 'missing_repositories': [],
                          'new_non_git_candidates': []}, 'baseline': previous is None}
    try:
        scan = (builder or inventory.build)(root, jobs=jobs)
        if not isinstance(scan, dict) or not isinstance(scan.get('summary'), dict):
            raise ValueError('inventory result invalid')
        if builder is None:
            enrich_dirty(scan)
            enrich_purposes(scan)
        attach_observations(scan, observations_dir)
        result['scan'] = scan
        if not _complete(scan):
            result['status'] = 'partial'
        if previous and previous.get('scan'):
            old, new = previous['scan'], scan
            old_ids, new_ids = _identity(old), _identity(new)
            result['changes']['new_repositories'] = sorted(set(new_ids) - set(old_ids))
            # Missing does not imply deleted; only compare fully readable inventories.
            if _complete(old) and _complete(scan):
                result['changes']['missing_repositories'] = sorted(set(old_ids) - set(new_ids))
            before, after = _checkouts(old), _checkouts(scan)
            result['changes']['changed_checkouts'] = sorted(k for k in before.keys() & after.keys() if before[k] != after[k])
            old_paths = {x['path'] for x in old.get('projects_without_git', [])}
            result['changes']['new_non_git_candidates'] = sorted(x['path'] for x in scan.get('projects_without_git', []) if x['path'] not in old_paths)
        elif previous:
            result['baseline'] = True
        result['last_success_at'] = now if _complete(scan) else (previous or {}).get('last_success_at')
        if not _complete(scan):
            result['message'] = 'Inventur unvollständig; fehlende Einträge sind keine Löschungen.'
    except Exception as error:
        result.update(status='error', message=type(error).__name__,
                      scan=(previous or {}).get('scan'), last_success_at=(previous or {}).get('last_success_at'))
    return result


def watch_inventory(root, target, *, jobs=4, interval=300, once=False, observations_dir=None):
    if interval < 300:
        raise ValueError('interval must be at least 300 seconds')
    path = Path(target).expanduser()
    if path.parent.exists() and path.parent.stat().st_mode & 0o077:
        raise ValueError('output directory must already be private (0700), or be newly created')
    directory = private_directory(path.parent)
    path = directory / path.name
    if path.is_symlink():
        raise ValueError('refusing symlink output')
    lockpath = directory / ('.' + path.name + '.lock')
    fd = os.open(lockpath, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'r+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        previous = None
        if path.is_file():
            try:
                previous = json.loads(path.read_text())
                if previous.get('schema') != SCHEMA or previous.get('scan', {}).get('root') != str(Path(root).expanduser().resolve()):
                    previous = None
            except (OSError, ValueError, AttributeError):
                previous = None
        while True:
            result = observe(root, previous, jobs=jobs, observations_dir=observations_dir)
            _write_private(path, json.dumps(result, ensure_ascii=False))
            # A partial scan can identify newly observed entries, but never removals.
            # An exception retains the most recent readable observation as baseline.
            if result['status'] in ('ok', 'partial'):
                previous = result
            print(json.dumps({'status': result['status'], 'attempted_at': result['attempted_at']}), flush=True)
            if once:
                return result
            time.sleep(interval)
