"""Repeat the existing read-only inventory and publish a bounded local observation."""
from __future__ import annotations

from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import time

from . import inventory, gitio
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


def observe(root, previous=None, *, jobs=4, builder=None):
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
        result['scan'] = scan
        if not _complete(scan):
            result['status'] = 'partial'
        if previous and previous.get('scan') and _complete(previous['scan']):
            old, new = previous['scan'], scan
            old_ids, new_ids = _identity(old), _identity(new)
            result['changes']['new_repositories'] = sorted(set(new_ids) - set(old_ids))
            # Missing does not imply deleted; only compare fully readable inventories.
            if _complete(scan):
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


def watch_inventory(root, target, *, jobs=4, interval=300, once=False):
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
            result = observe(root, previous, jobs=jobs)
            _write_private(path, json.dumps(result, ensure_ascii=False))
            # Never compare to a failed/partial inventory; preserve prior good baseline.
            if result['status'] == 'ok':
                previous = result
            print(json.dumps({'status': result['status'], 'attempted_at': result['attempted_at']}), flush=True)
            if once:
                return result
            time.sleep(interval)
