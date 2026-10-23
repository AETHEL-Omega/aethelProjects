"""Local coverage ledger: directories, Git identities and individual checkouts.

No network, builds, model calls or project scripts. Exclusions and read failures
are explicit; this is an observation, never another project registry.
"""
from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from . import gitio

SKIP = frozenset({'.git', 'node_modules', 'target', 'build', 'dist', '.dart_tool',
                 '.venv', 'venv', '.build', '.gradle', 'Pods', '__pycache__',
                 'site-packages', '.tox'})
PROJECT_MARKERS = frozenset({'Cargo.toml', 'pubspec.yaml', 'package.json',
                            'pyproject.toml', 'CMakeLists.txt', 'Package.swift',
                            'go.mod', 'aethel.manifest.json'})


def census(root: Path | str) -> dict:
    root = Path(root).expanduser().resolve()
    result = {'root': str(root), 'git_candidates': [], 'bare_candidates': [],
              'project_candidates': [], 'top_entries': [], 'symlinks': [],
              'excluded_paths': [], 'errors': [], 'excluded_names': sorted(SKIP),
              'policy': 'recursive; no symlink traversal; generated directories excluded'}
    if not root.is_dir():
        result['errors'].append({'path': str(root), 'error': 'root is not a directory'})
        return result

    def onerror(error):
        result['errors'].append({'path': error.filename, 'error': str(error)})

    for base, dirs, files in os.walk(root, topdown=True, followlinks=False, onerror=onerror):
        path = Path(base)
        names = set(files) | set(dirs)
        if path == root:
            result['top_entries'] = [{'path': str(path / n),
                                     'kind': 'symlink' if (path / n).is_symlink() else
                                             'directory' if n in dirs else 'file'}
                                    for n in sorted(names)]
        if '.git' in names:
            result['git_candidates'].append(str(path))
        if {'HEAD', 'objects', 'refs'}.issubset(names):
            result['git_candidates'].append(str(path))
            result['bare_candidates'].append(str(path))
            dirs[:] = []
            continue
        markers = sorted(PROJECT_MARKERS & set(files))
        if markers:
            result['project_candidates'].append({'path': str(path), 'markers': markers})
        keep = []
        for name in sorted(dirs):
            child = path / name
            if child.is_symlink():
                result['symlinks'].append({'path': str(child), 'target': os.readlink(child)})
            elif name in SKIP or name.startswith(('.venv', '.tox')):
                result['excluded_paths'].append(str(child))
            else:
                keep.append(name)
        dirs[:] = keep
    result['git_candidates'] = sorted(set(result['git_candidates']))
    return result


def _checkout(path: str) -> dict:
    root = Path(path)
    common = gitio.run_git(root, 'rev-parse', '--path-format=absolute', '--git-common-dir')
    result = {'path': path, 'git_common_dir': common, 'errors': []}
    if common is None:
        result['errors'].append('unreadable or invalid Git marker')
        return result
    if not Path(common).is_absolute():
        result['git_common_dir'] = str((root / common).resolve())
    bare = gitio.run_git(root, 'rev-parse', '--is-bare-repository')
    result['bare'] = bare == 'true'
    result['git_directory_only'] = str(root) == result['git_common_dir']
    result['head'] = gitio.run_git(root, 'rev-parse', '--verify', 'HEAD')
    result['branch'] = gitio.run_git(root, 'symbolic-ref', '--quiet', '--short', 'HEAD')
    result['last_commit'] = gitio.run_git(root, 'log', '-1', '--format=%cI %s')
    if not result['bare'] and not result['git_directory_only']:
        status = gitio.run_git(root, 'status', '--porcelain', '--untracked-files=normal')
        result['dirty_files'] = len(status.splitlines()) if status is not None else None
        if status is None:
            result['errors'].append('status unavailable')
    else:
        result['dirty_files'] = None
    result['remotes'] = gitio.run_git(root, 'remote', 'get-url', 'origin')
    return result


def repository_details(group: dict, root: Path) -> dict:
    """Registered worktrees can live outside the scanned workspace."""
    result = dict(group)
    path = Path(group['paths'][0])
    output = gitio.run_git(path, 'worktree', 'list', '--porcelain')
    registered = []
    if output is not None:
        for block in output.split('\n\n'):
            fields = dict(line.split(' ', 1) if ' ' in line else (line, True)
                          for line in block.splitlines())
            if 'worktree' in fields:
                worktree = Path(fields['worktree'])
                registered.append({'path': str(worktree), 'head': fields.get('HEAD'),
                    'branch': fields.get('branch'), 'prunable': fields.get('prunable'),
                    'outside_root': not worktree.is_relative_to(root),
                    'exists': worktree.is_dir()})
    result['registered_worktrees'] = registered
    result['registration_error'] = output is None
    result['origin_head'] = gitio.run_git(path, 'symbolic-ref', '--quiet', '--short',
                                        'refs/remotes/origin/HEAD')
    result['origin_main_oid'] = gitio.run_git(path, 'rev-parse', '--verify', 'refs/remotes/origin/main')
    profile = path / '.aix' / 'project-profile.json'
    result['checkout_profile'] = {'path': str(profile), 'state': 'missing', 'roles': None}
    if profile.is_file():
        try:
            document = json.loads(profile.read_text())
            result['checkout_profile'] = {'path': str(profile), 'state': 'read',
                'project_id': document.get('project_id'), 'roles': document.get('rollen')}
        except (OSError, ValueError, AttributeError) as error:
            result['checkout_profile']['state'] = 'unreadable'
            result['checkout_profile']['error'] = str(error)
    result['validation_contract_present'] = (path / '.aix' / 'validation-contract.json').is_file()
    return result


def build(root: Path | str, jobs: int = 4) -> dict:
    result = census(root)
    with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        result['checkouts'] = list(pool.map(_checkout, result['git_candidates']))
    groups: dict[str, list[str]] = {}
    for checkout in result['checkouts']:
        common = checkout['git_common_dir']
        if common:
            groups.setdefault(common, []).append(checkout['path'])
    result['repositories'] = [{'git_common_dir': k, 'paths': sorted(v)}
                              for k, v in sorted(groups.items())]
    with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        result['repositories'] = list(pool.map(
            lambda group: repository_details(group, Path(result['root'])), result['repositories']))
    checkout_paths = [Path(c['path']) for c in result['checkouts'] if c['git_common_dir']]
    # Package candidates within a checkout are components, not independent products.
    git_candidates = [Path(p) for p in result['git_candidates']]
    result['projects_without_git'] = [p for p in result['project_candidates']
        if not any(Path(p['path']).is_relative_to(c) for c in git_candidates)]
    invalid = [Path(c['path']) for c in result['checkouts'] if not c['git_common_dir']]
    result['projects_with_unresolved_git'] = [p for p in result['project_candidates']
        if any(Path(p['path']).is_relative_to(c) for c in invalid)]
    for entry in result['top_entries']:
        path = Path(entry['path'])
        entry['git_paths_below'] = sum(c.is_relative_to(path) for c in checkout_paths)
        entry['project_markers_below'] = sum(Path(p['path']).is_relative_to(path)
                                            for p in result['project_candidates'])
    result['generated_at'] = datetime.now().astimezone().isoformat(timespec='seconds')
    result['summary'] = {'git_markers': len(result['git_candidates']),
        'repositories': len(groups), 'bare_layout_candidates': len(result['bare_candidates']),
        'bare_repositories': sum(bool(c.get('bare')) for c in result['checkouts']),
        'git_directories_without_checkout': sum(bool(c.get('git_directory_only')) for c in result['checkouts']),
        'invalid_git_markers': sum(not c['git_common_dir'] for c in result['checkouts']),
        'dirty_checkouts': sum(bool(c.get('dirty_files')) for c in result['checkouts']),
        'projects_without_git': len(result['projects_without_git']),
        'filesystem_errors': len(result['errors']),
        'checkout_errors': sum(bool(c['errors']) for c in result['checkouts']),
        'registered_worktrees_outside_root': sum(w['outside_root'] for g in result['repositories']
                                                for w in g['registered_worktrees']),
        'project_profiles_with_roles': sum(bool(g['checkout_profile']['roles']) for g in result['repositories'])}
    result['limitations'] = [
        'Local snapshot only; remote tracking refs may be stale. No fetch or GitHub billing query.',
        'Excluded paths and symlink targets are not traversed; completeness is limited to this policy.',
        'Project markers identify candidates and packages, not confirmed products.',
        'Bare repositories have no working tree; absent HEAD can also mean an unborn repository.',
        'A changing workspace is not an atomic snapshot.']
    return result


def render_markdown(data: dict) -> str:
    lines = ['# Workspace-Inventar', '', f"Stand: {data['generated_at']}", '',
             'Nur lokale Beobachtung; keine neue Registry und keine Netzaufrufe.', '',
             '```json', json.dumps(data['summary'], ensure_ascii=False, indent=2), '```', '',
             '## Erfassungsgrenzen', '']
    lines.extend('- ' + x for x in data['limitations'])
    lines += ['', '## Jeder Git-Checkout', '',
              '| Pfad | Branch | HEAD | Dirty | Fehler |', '|---|---|---|---:|---|']
    for c in data['checkouts']:
        lines.append('| ' + ' | '.join(str(x).replace('|', '\\|') for x in
            (c['path'], c.get('branch'), c.get('head'), c.get('dirty_files'), '; '.join(c['errors']))) + ' |')
    lines += ['', '## Projektkandidaten ohne Git', '']
    lines.extend(f"- {p['path']} ({', '.join(p['markers'])})" for p in data['projects_without_git'])
    lines += ['', '## Alle Einträge direkt im Workspace', '',
              '| Pfad | Art | Git-Pfade darunter | Projektmarker darunter |', '|---|---|---:|---:|']
    lines.extend(f"| {e['path']} | {e['kind']} | {e['git_paths_below']} | {e['project_markers_below']} |"
                 for e in data['top_entries'])
    return '\n'.join(lines)
