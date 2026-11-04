"""Private, offline projection of local conversation evidence; never an executor.

Every source is read to a fixed byte boundary. Text previews are explicitly
limited; original records remain addressable by source, line and byte offset.
Parsing a statement never promotes it to a verified delivery or approval.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile

VERSION = 1
PREVIEW = 1600
COMMIT = re.compile(r"(?i)\b(?:commit|revision|head)\s*[:=]?\s*[`\"]?([0-9a-f]{7,40})\b")


def private_directory(path: Path) -> Path:
    path = path.expanduser()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('Private output must not follow symlinks')
    path = path.resolve()
    if any((p / '.git').exists() for p in (path, *path.parents)):
        raise ValueError('Private history cannot be written inside a Git checkout')
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path, 0o700)
    return path


def text_of(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return '\n'.join(text_of(x) for x in value)
    if isinstance(value, dict):
        if 'text' in value:
            return str(value['text'])
        if 'content' in value:
            return text_of(value['content'])
        return json.dumps(value, ensure_ascii=False)
    return ''


def normalize(provider: str, record: dict):
    """Yield statements, never inferred completion. Ignore reasoning/auth config."""
    typ = record.get('type')
    if provider == 'codex':
        p = record.get('payload', {})
        if not isinstance(p, dict) or typ != 'response_item':
            return
        kind = p.get('type')
        if kind == 'message' and p.get('role') in ('user', 'assistant'):
            yield p['role'], 'statement', text_of(p.get('content')), p.get('id', ''), ''
        elif kind in ('function_call', 'custom_tool_call'):
            yield 'tool', 'call', str(p.get('arguments', p.get('input', ''))), p.get('call_id', ''), p.get('name', '')
        elif kind in ('function_call_output', 'custom_tool_call_output'):
            yield 'tool', 'result', text_of(p.get('output')), p.get('call_id', ''), ''
    elif provider == 'claude-code' and typ in ('user', 'assistant'):
        p = record.get('message', {})
        if not isinstance(p, dict):
            return
        content = p.get('content', [])
        if isinstance(content, str):
            yield typ, 'statement', content, record.get('uuid', ''), ''
        elif isinstance(content, list):
            for i, block in enumerate(content):
                if not isinstance(block, dict):
                    continue
                kind = block.get('type')
                if kind == 'text':
                    yield typ, 'statement', text_of(block), f"{record.get('uuid', '')}:{i}", ''
                elif kind == 'tool_use':
                    yield 'tool', 'call', json.dumps(block.get('input', {}), ensure_ascii=False), block.get('id', ''), block.get('name', '')
                elif kind == 'tool_result':
                    yield 'tool', 'result_error' if block.get('is_error') else 'result', text_of(block.get('content')), block.get('tool_use_id', ''), ''


def schema(db):
    db.executescript('''
    CREATE TABLE sources(path TEXT PRIMARY KEY, provider TEXT, session_id TEXT,
      cwd TEXT, parent_id TEXT, subagent INTEGER, bytes INTEGER, mtime_ns INTEGER,
      sha256 TEXT, records INTEGER, events INTEGER, errors INTEGER, coverage TEXT,
      types_json TEXT, observed_at TEXT);
    CREATE TABLE events(source TEXT, line INTEGER, byte_offset INTEGER, record_hash TEXT,
      timestamp TEXT, actor TEXT, kind TEXT, event_id TEXT, tool_name TEXT,
      preview TEXT, text_length INTEGER, refs_json TEXT);
    CREATE INDEX event_source ON events(source);
    CREATE TABLE session_catalog(provider TEXT, session_id TEXT, title TEXT, cwd TEXT,
      archived INTEGER, source TEXT, PRIMARY KEY(provider,session_id,source));
    CREATE TABLE git_refs(cwd TEXT, candidate TEXT, object_id TEXT, observation TEXT,
      PRIMARY KEY(cwd,candidate));
    CREATE TABLE run(key TEXT PRIMARY KEY,value TEXT);
    CREATE VIEW review_queue AS
      SELECT provider, session_id, path AS source, cwd,
        CASE WHEN coverage!='parsed' THEN 'repair_source'
             WHEN events=0 THEN 'inspect_format_or_compaction'
             ELSE 'bind_work_and_validate_claims' END AS next_action
      FROM sources
      UNION ALL
      SELECT c.provider,c.session_id,c.source,c.cwd,'obtain_transcript'
      FROM session_catalog c WHERE NOT EXISTS
        (SELECT 1 FROM sources s WHERE s.provider=c.provider AND s.session_id=c.session_id);
    ''')


def discover(roots):
    files, errors = [], []
    for provider, root in roots:
        if root.is_symlink():
            errors.append({'provider': provider, 'reason': 'root_symlink_skipped'})
            continue
        if not root.is_dir():
            errors.append({'provider': provider, 'reason': 'root_unavailable'})
            continue
        def failed(error):
            errors.append({'provider': provider, 'reason': type(error).__name__})
        for base, dirs, names in os.walk(root, followlinks=False, onerror=failed):
            dirs[:] = sorted(d for d in dirs if not (Path(base) / d).is_symlink())
            for name in sorted(names):
                p = Path(base) / name
                if not p.is_symlink() and (name.endswith('.jsonl') or name.endswith('.jsonl.zst')):
                    files.append((provider, p))
    return sorted(set(files), key=lambda item: str(item[1])), errors


@contextmanager
def source_stream(path):
    if path.name.endswith('.zst'):
        try:
            from compression import zstd
        except ImportError as e:
            raise ValueError('zstd reader unavailable; use Python with compression.zstd') from e
        with zstd.open(path, 'rb') as stream:
            yield stream, True
    else:
        with path.open('rb') as stream:
            yield stream, False


def ingest_file(db, provider, path, observed):
    before = None
    digest = hashlib.sha256()
    session_id = path.name.removesuffix('.zst').removesuffix('.jsonl')
    cwd = parent = ''
    count = emitted = bad = offset = 0
    types = Counter()
    coverage = 'parsed'
    subagent = 'subagents' in path.parts or path.name.startswith('agent-')
    try:
        before = path.stat()
        with source_stream(path) as (stream, compressed):
            while compressed or offset < before.st_size:
                raw = stream.readline() if compressed else stream.readline(before.st_size - offset)
                if not raw:
                    break
                start = offset
                offset += len(raw)
                digest.update(raw)
                count += 1
                try:
                    record = json.loads(raw)
                    if not isinstance(record, dict):
                        raise ValueError('not an object')
                except (ValueError, UnicodeError):
                    bad += 1
                    continue
                typ = str(record.get('type', 'unknown'))
                types[typ] += 1
                p = record.get('payload', {})
                if provider == 'codex' and typ == 'session_meta' and isinstance(p, dict):
                    session_id = str(p.get('id') or p.get('session_id') or session_id)
                    cwd = str(p.get('cwd') or cwd)
                elif provider == 'claude-code':
                    session_id = str(record.get('sessionId') or record.get('session_id') or session_id)
                    cwd = str(record.get('cwd') or cwd)
                    if record.get('isSidechain'):
                        subagent = True
                    parent = str(record.get('parentSessionId') or parent)
                for actor, kind, text, event_id, tool in normalize(provider, record):
                    if not text:
                        continue
                    refs = sorted(set(COMMIT.findall(text)))
                    db.execute('INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',
                        (str(path), count, start, hashlib.sha256(raw).hexdigest(),
                         str(record.get('timestamp', '')), actor, kind, str(event_id), str(tool),
                         text[:PREVIEW], len(text), json.dumps(refs)))
                    emitted += 1
        after = path.stat()
        if before.st_size != after.st_size or before.st_mtime_ns != after.st_mtime_ns:
            coverage = 'changed_during_read'
        if bad:
            coverage = 'partial_parse'
    except (OSError, ValueError, EOFError) as e:
        coverage = 'unreadable:' + type(e).__name__
        bad += 1
    db.execute('INSERT INTO sources VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
        (str(path), provider, session_id, cwd, parent, int(subagent), before.st_size if before else None,
         before.st_mtime_ns if before else None, digest.hexdigest(), count, emitted, bad, coverage,
         json.dumps(types), observed))


def read_catalog(db, home):
    root = home / 'Library/Application Support/Claude/claude-code-sessions'
    errors = 0
    if not root.exists():
        return {'available': False, 'errors': 0}
    for p in sorted(root.rglob('*.json')):
        if p.is_symlink():
            continue
        try:
            data = json.loads(p.read_text())
            if not isinstance(data, dict) or not data.get('sessionId'):
                continue
            sid = data.get('cliSessionId') or data['sessionId']
            db.execute('INSERT OR REPLACE INTO session_catalog VALUES(?,?,?,?,?,?)',
                ('claude-code', str(sid), str(data.get('title', '')), str(data.get('cwd', '')),
                 int(bool(data.get('isArchived'))), str(p)))
        except (OSError, ValueError):
            errors += 1
    return {'available': True, 'errors': errors}


def read_codex_catalog(db, path):
    if path is None:
        return {'available': False, 'reason': 'app_catalog_not_supplied'}
    data = json.loads(Path(path).read_text())
    if data.get('source') != 'codex-app-local-history' or not isinstance(data.get('threads'), list):
        raise ValueError('Expected explicit Codex app history export')
    for item in data['threads']:
        if not isinstance(item, dict) or not isinstance(item.get('id'), str):
            raise ValueError('Invalid catalog thread')
        db.execute('INSERT OR REPLACE INTO session_catalog VALUES(?,?,?,?,?,?)',
            ('codex', item['id'], str(item.get('title', '')), str(item.get('cwd', '')),
             int(bool(item.get('archived'))), str(path)))
    return {'available': True, 'threads': len(data['threads']), 'observed_date': data.get('observed_date')}


def verify_git(db):
    """Existence only: never equate an existing object with authored/tested/landed."""
    pairs = set()
    for cwd, refs in db.execute('SELECT s.cwd,e.refs_json FROM events e JOIN sources s ON s.path=e.source WHERE e.refs_json != "[]"'):
        pairs.update((cwd, ref) for ref in json.loads(refs))
    from .gitio import run_git
    for cwd, ref in sorted(pairs):
        oid = ''
        observation = 'repository_unavailable'
        if cwd and Path(cwd).is_dir():
            result = run_git(Path(cwd), 'rev-parse', '--verify', '--end-of-options', ref + '^{commit}', timeout=3)
            if result and re.fullmatch(r'[0-9a-f]{40,64}', result.strip()):
                oid = result.strip()
                observation = 'commit_object_present_locally'
            else:
                observation = 'not_resolved_as_local_commit'
        db.execute('INSERT INTO git_refs VALUES(?,?,?,?)', (cwd, ref, oid, observation))


def summary(db, discovery_errors, catalog):
    q = lambda sql: [list(r) for r in db.execute(sql)]
    return {'schema': 'aethel.projects.private-work-history/v1',
        'parser_version': VERSION, 'sources': q('SELECT provider,coverage,count(*) FROM sources GROUP BY provider,coverage'),
        'records': db.execute('SELECT coalesce(sum(records),0) FROM sources').fetchone()[0],
        'events': db.execute('SELECT count(*) FROM events').fetchone()[0],
        'sessions': q('SELECT provider,count(DISTINCT session_id) FROM sources GROUP BY provider'),
        'sources_without_extracted_events': q('SELECT provider,count(*) FROM sources WHERE events=0 GROUP BY provider'),
        'catalog_with_extracted_events': q('SELECT c.provider,count(DISTINCT c.session_id) FROM session_catalog c WHERE EXISTS (SELECT 1 FROM sources s WHERE s.provider=c.provider AND s.session_id=c.session_id AND s.events>0) GROUP BY c.provider'),
        'semantic_review': {'state': 'not_performed', 'task_binding': 'unresolved'},
        'review_queue': q('SELECT next_action,count(*) FROM review_queue GROUP BY next_action'),
        'git_observations': q('SELECT observation,count(*) FROM git_refs GROUP BY observation'),
        'catalog_without_transcript': db.execute('SELECT count(DISTINCT c.session_id) FROM session_catalog c WHERE NOT EXISTS (SELECT 1 FROM sources s WHERE s.provider=c.provider AND s.session_id=c.session_id)').fetchone()[0],
        'catalog_coverage': q('SELECT c.provider,count(DISTINCT c.session_id),count(DISTINCT CASE WHEN EXISTS (SELECT 1 FROM sources s WHERE s.provider=c.provider AND s.session_id=c.session_id) THEN c.session_id END) FROM session_catalog c GROUP BY c.provider'),
        'discovery_errors': discovery_errors, 'claude_desktop_catalog': catalog,
        'limits': ['Only explicitly selected local sources; no live access to other hosts or Claude web accounts.',
            'Parsed does not mean semantically reviewed, verified, approved or delivered.',
            'Previews are truncated; source line/offset/hash locates original record.',
            'Git checks only local commit existence, not authorship, tests, push or installation.',
            'Commit extraction recognizes commit/revision/head followed by a hexadecimal candidate; other reference formats remain unclassified.',
            'Tool output is recorded evidence, not an independent re-execution.',
            'Not an atomic snapshot across applications; messages added after each file boundary are excluded.',
            'Source cwd is a grouping hint, not an authoritative project or work-item identity; many-to-many binding remains open.',
            'Source session_id is the last structured identity seen in that file; mixed-session exports require record-level identity attribution.',
            'A source with no extracted events may be metadata, an unsupported log or compacted history; it is not a reviewed chat.',
            'Quoted text inside user or assistant messages is not separately attributed and cannot authorize actions.',
            'Hash of compressed sources refers to decompressed bytes; running files have a snapshot boundary.']}


def _write_private(target, text):
    if target.is_symlink():
        raise ValueError('Refusing symlink output')
    fd, name = tempfile.mkstemp(prefix='.report-', dir=target.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(text)
        os.replace(name, target)
    finally:
        if Path(name).exists():
            Path(name).unlink()


def write_report(db, directory, stats):
    esc = lambda x: html.escape(str(x), quote=True)
    header = '<!doctype html><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'"><title>Private Arbeitsnachweise</title><style>body{font:16px system-ui;max-width:1100px;margin:2em auto;padding:1em}pre{white-space:pre-wrap;overflow-wrap:anywhere}details{border:1px solid #aaa;padding:1em;margin:1em 0}td,th{padding:.5em;text-align:left;border-bottom:1px solid #bbb}dd{margin:0}summary{cursor:pointer}</style>'
    intro = '<p>Private lokale Projektion. Eine Aussage ist kein Prüfnachweis; ein vorhandener Commit ist keine Lieferung. Originale bleiben unverändert. Jüngste Beiträge zuerst, alle extrahierten Ereignisse in history.sqlite. Vollständige fachliche Bewertung und Zuordnung zu AIX-Aufträgen bleiben offen.</p>'
    intro += '<p>Erfassungsbeginn: '+esc(stats.get('observed_at','unbekannt'))+' · Kein atomarer oder laufend aktualisierter Gesamtstand.</p>'
    index = []
    for cwd, count, errors in db.execute('SELECT cwd,count(*),sum(errors) FROM sources GROUP BY cwd ORDER BY cwd'):
        page_name = 'project-' + hashlib.sha256(cwd.encode()).hexdigest()[:24] + '.html'
        index.append(f'<tr><td><a href="{page_name}">{esc(cwd or "Projekt nicht zugeordnet")}</a></td><td>{count}</td><td>{errors}</td></tr>')
        cards = []
        for provider,sid,coverage,path,subagent in db.execute('SELECT provider,session_id,coverage,path,subagent FROM sources WHERE cwd=? ORDER BY provider,session_id', (cwd,)):
            snippets = []
            for label, actor, kind in [('Beauftragtes / Nutzerbeiträge','user','statement'),('Behaupteter Stand / offene Punkte','assistant','statement'),('Protokollierte Tool-Ergebnisse','tool','result'),('Protokollierte Tool-Fehler','tool','result_error')]:
                events = list(db.execute('SELECT preview,line,text_length,timestamp FROM events WHERE source=? AND actor=? AND kind=? ORDER BY rowid DESC LIMIT 2', (path,actor,kind)))
                if events:
                    snippets.append('<h3>'+label+'</h3><dl>'+''.join(f'<dt>{esc(ts)} · Zeile {line} · {length} Zeichen</dt><dd><pre>{esc(text)}</pre></dd>' for text,line,length,ts in events)+'</dl>')
            cards.append(f'<details><summary>{esc(provider)} · {esc(sid)} · {esc(coverage)}'+(' · Unterlauf' if subagent else '')+f'</summary><p>Quelle: {esc(path)}</p>'+(''.join(snippets) if snippets else '<p>Keine anzeigbaren Nachrichten extrahiert. Format / Kompaktierung prüfen; keine abgeschlossene fachliche Auswertung.</p>')+'</details>')
        git_rows = ''.join(f'<tr><td>{esc(ref)}</td><td>{esc(oid)}</td><td>{esc(state)}</td></tr>' for ref,oid,state in db.execute('SELECT candidate,object_id,observation FROM git_refs WHERE cwd=? ORDER BY candidate',(cwd,)))
        _write_private(directory/page_name, header+'<a href="index.html">Alle Projekte</a><h1>'+esc(cwd or 'Nicht zugeordnet')+'</h1>'+intro+'<h2>Lokal geprüfte Commit-Verweise</h2><table>'+git_rows+'</table><h2>Quellen und jüngste Beiträge je Quelle</h2>'+''.join(cards))
    gaps = list(db.execute('SELECT DISTINCT c.provider,c.session_id,c.title FROM session_catalog c WHERE NOT EXISTS (SELECT 1 FROM sources s WHERE s.provider=c.provider AND s.session_id=c.session_id) ORDER BY c.provider,c.session_id'))
    missing = '<h2>Katalogeinträge ohne gefundenes Transkript</h2><table>'+''.join(f'<tr><td>{esc(provider)}</td><td>{esc(sid)}</td><td>{esc(title)}</td></tr>' for provider,sid,title in gaps)+'</table>'
    _write_private(directory/'index.html', header+'<h1>Private Arbeitsnachweise</h1>'+intro+'<details><summary>Abdeckung und Grenzen</summary><pre>'+esc(json.dumps(stats,ensure_ascii=False,indent=2))+'</pre></details><h2>Protokollierte Arbeitsverzeichnisse</h2><p>Gruppierungshilfe; Projektidentitäten und Mehrfachbezüge sind noch nicht abgeglichen.</p><table><tr><th>Kontext aus den Quellen</th><th>Protokolldateien</th><th>Lesefehler</th></tr>'+''.join(index)+'</table>'+missing)
    _write_private(directory/'coverage.json',json.dumps(stats,ensure_ascii=False,indent=2))


def build_history(home: Path, output: Path, check_git: bool = True,
                  codex_catalog: Path | None = None, claude_roots: list[Path] | None = None):
    directory=private_directory(output)
    roots=[('codex',home/'.codex/sessions'),('codex',home/'.codex/archived_sessions'),('claude-code',home/'.claude/projects'),
           ('claude-code',home/'Library/Application Support/Claude/local-agent-mode-sessions')]
    roots.extend(('claude-code', path.expanduser().absolute()) for path in (claude_roots or []))
    files, errors=discover(roots)
    fd, tmp=tempfile.mkstemp(prefix='history-',suffix='.sqlite',dir=directory)
    os.close(fd)
    db=sqlite3.connect(tmp)
    try:
        schema(db)
        observed=datetime.now(timezone.utc).isoformat()
        for i,(provider,path) in enumerate(files):
            ingest_file(db,provider,path,observed)
            if (i+1)%100==0:
                db.commit()
                print(json.dumps({'files_processed':i+1,'files_discovered':len(files)}),flush=True)
        catalog=read_catalog(db,home)
        codex_catalog_status=read_codex_catalog(db,codex_catalog)
        if check_git:
            verify_git(db)
        stats=summary(db,errors,catalog)
        stats['git_check_requested']=check_git
        stats['codex_app_catalog']=codex_catalog_status
        stats['additional_claude_roots_count']=len(claude_roots or [])
        stats['observed_at']=observed
        db.execute('INSERT INTO run VALUES(?,?)',('coverage',json.dumps(stats)))
        db.execute('INSERT INTO run VALUES(?,?)',('observed_at',observed))
        db.commit()
        write_report(db,directory,stats)
        db.close()
        target=directory/'history.sqlite'
        if target.is_symlink():raise ValueError('Refusing symlink database')
        os.replace(tmp,target)
        os.chmod(target,0o600)
        return stats
    finally:
        db.close()
        if Path(tmp).exists():Path(tmp).unlink()


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home',type=Path,default=Path.home())
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--no-git',action='store_true')
    parser.add_argument('--codex-catalog',type=Path)
    parser.add_argument('--claude-root',type=Path,action='append',default=[],
                        help='Additional local Claude export directory; repeatable')
    args=parser.parse_args(argv)
    print(json.dumps(build_history(args.home,args.out,not args.no_git,args.codex_catalog,args.claude_root),ensure_ascii=False))


if __name__=='__main__':
    main()
