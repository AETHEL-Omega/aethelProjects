"""Synthetic privacy, provenance and coverage regressions; no real user data."""
import hashlib
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from aethel_projects.work_history import build_history, ingest_file, normalize, private_directory, schema


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.home = self.root / 'home'
        for name in ['.codex/sessions', '.codex/archived_sessions', '.claude/projects',
                     'Library/Application Support/Claude/local-agent-mode-sessions']:
            (self.home / name).mkdir(parents=True)
        self.out = self.root / 'private'

    def tearDown(self):
        self.temp.cleanup()

    def write(self, relative, records):
        path = self.home / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(''.join(json.dumps(r)+'\n' for r in records))
        return path

    def test_statements_are_not_promoted_to_verified_work(self):
        self.write('.codex/sessions/a.jsonl', [
            {'type':'session_meta','payload':{'id':'session-a','cwd':str(self.home)}},
            {'type':'response_item','payload':{'type':'message','role':'assistant',
             'content':[{'type':'output_text','text':'All tests passed; deployed!'}]}},
        ])
        stats = build_history(self.home,self.out,False)
        with closing(sqlite3.connect(self.out/'history.sqlite')) as db:
            self.assertEqual(db.execute('select actor,kind from events').fetchone(),('assistant','statement'))
        self.assertEqual(stats['events'],1)
        self.assertFalse(stats['git_check_requested'])

    def test_private_output_cannot_be_in_repository_or_symlink(self):
        repo=self.root/'repo';repo.mkdir();(repo/'.git').write_text('gitdir: somewhere')
        with self.assertRaises(ValueError): private_directory(repo/'data')
        link=self.root/'link';link.symlink_to(self.home,target_is_directory=True)
        with self.assertRaises(ValueError): private_directory(link/'data')

    def test_tool_output_and_source_offsets_are_preserved(self):
        p=self.write('.claude/projects/a.jsonl', [
            {'type':'user','sessionId':'c','message':{'content':[{'type':'tool_result','tool_use_id':'t','is_error':True,'content':'failed'}]}},
        ])
        build_history(self.home,self.out,False)
        with closing(sqlite3.connect(self.out/'history.sqlite')) as db:
            row=db.execute('select byte_offset,record_hash,kind from events').fetchone()
        self.assertEqual(row,(0,hashlib.sha256(p.read_bytes()).hexdigest(),'result_error'))

    def test_bad_record_does_not_disappear_or_abort_other_sources(self):
        p=self.write('.codex/sessions/a.jsonl',[{'type':'event_msg','payload':{}}])
        with p.open('a') as f:f.write('{broken\n')
        self.write('.claude/projects/b.jsonl',[{'type':'user','sessionId':'b','message':{'content':'request'}}])
        stats=build_history(self.home,self.out,False)
        self.assertIn(['codex','partial_parse',1],stats['sources'])
        self.assertEqual(stats['records'],3)
        self.assertEqual(stats['events'],1)

    def test_preview_limit_is_explicit_and_html_cannot_execute(self):
        text='<script>alert(1)</script>'+('x'*2000)
        self.write('.claude/projects/a.jsonl',[{'type':'assistant','sessionId':'x','message':{'content':[{'type':'text','text':text}]}}])
        build_history(self.home,self.out,False)
        report='\n'.join(p.read_text() for p in self.out.glob('*.html'))
        self.assertNotIn('<script>',report)
        self.assertIn('&lt;script&gt;',report)
        with closing(sqlite3.connect(self.out/'history.sqlite')) as db:
            length,preview=db.execute('select text_length,preview from events').fetchone()
        self.assertEqual(length,len(text));self.assertEqual(len(preview),1600)
        self.assertEqual((self.out.stat().st_mode & 0o777),0o700)
        for name in ['index.html','coverage.json','history.sqlite']:
            self.assertEqual((self.out/name).stat().st_mode & 0o777,0o600)

    def test_catalog_without_transcript_is_an_explicit_gap(self):
        p=self.home/'Library/Application Support/Claude/claude-code-sessions/a.json'
        p.parent.mkdir(parents=True);p.write_text(json.dumps({'sessionId':'web','title':'private title'}))
        stats=build_history(self.home,self.out,False)
        self.assertEqual(stats['catalog_without_transcript'],1)
        self.assertNotIn('private title',json.dumps(stats))

    def test_rerun_replaces_projection_without_duplicating_events(self):
        self.write('.claude/projects/a.jsonl',[{'type':'user','sessionId':'x','message':{'content':'one'}}])
        build_history(self.home,self.out,False)
        stats=build_history(self.home,self.out,False)
        self.assertEqual(stats['events'],1)

    def test_commit_presence_is_not_delivery_and_catalog_gaps_remain(self):
        self.write('.codex/sessions/a.jsonl',[
            {'type':'session_meta','payload':{'id':'present','cwd':str(self.home)}},
            {'type':'response_item','payload':{'type':'message','role':'assistant','content':[{'text':'Commit abcdef123 created, all done'}]}},
        ])
        catalog=self.root/'catalog.json'
        catalog.write_text(json.dumps({'source':'codex-app-local-history','threads':[{'id':'present'},{'id':'missing'}]}))
        with patch('aethel_projects.gitio.run_git', return_value='a'*40) as git:
            stats=build_history(self.home,self.out,True,catalog)
        self.assertEqual(stats['catalog_coverage'],[['codex',2,1]])
        self.assertEqual(stats['git_observations'],[['commit_object_present_locally',1]])
        self.assertEqual(git.call_args.args[1:3],('rev-parse','--verify'))

    def test_reasoning_and_api_replay_are_not_copied(self):
        self.assertEqual(list(normalize('codex',{'type':'response_item','payload':{'type':'reasoning','summary':'private reasoning'}})),[])
        self.assertEqual(list(normalize('claude-code',{'type':'api-request-blob','message':{'content':'replayed prompt'}})),[])

    def test_disappearing_source_is_reported_instead_of_aborting(self):
        with closing(sqlite3.connect(':memory:')) as db:
            schema(db)
            ingest_file(db,'codex',self.root/'missing.jsonl','2026-01-01')
            self.assertEqual(db.execute('select coverage,errors,bytes from sources').fetchone(),
                             ('unreadable:FileNotFoundError',1,None))

    def test_metadata_only_session_is_not_a_reviewed_chat(self):
        self.write('.codex/sessions/a.jsonl',[{'type':'session_meta','payload':{'id':'empty'}}])
        stats=build_history(self.home,self.out,False)
        self.assertEqual(stats['sources_without_extracted_events'],[['codex',1]])
        self.assertEqual(stats['semantic_review']['state'],'not_performed')
        self.assertEqual(stats['catalog_with_extracted_events'],[])
        self.assertEqual(stats['review_queue'],[['inspect_format_or_compaction',1]])

    def test_integrated_cli_uses_private_output(self):
        from aethel_projects.cli import main
        from contextlib import redirect_stdout
        import io
        with redirect_stdout(io.StringIO()) as out:
            result=main(['work-history','--home',str(self.home),'--out',str(self.out),'--no-git'])
        self.assertEqual(result,0)
        self.assertEqual(json.loads(out.getvalue())['events'],0)
        self.assertTrue((self.out/'history.sqlite').is_file())

    def test_changed_source_is_not_reported_as_stable(self):
        p=self.write('.claude/projects/a.jsonl',[{'type':'user','sessionId':'x','message':{'content':'one'}}])
        from aethel_projects.work_history import source_stream
        from contextlib import contextmanager
        @contextmanager
        def changing_source(path):
            with source_stream(path) as stream:
                yield stream
            with path.open('a') as f: f.write('{}\n')
        with patch('aethel_projects.work_history.source_stream',changing_source):
            stats=build_history(self.home,self.out,False)
        self.assertIn(['claude-code','changed_during_read',1],stats['sources'])

    def test_output_symlink_does_not_overwrite_external_file(self):
        private_directory(self.out)
        external=self.root/'external'; external.write_text('preserve')
        (self.out/'index.html').symlink_to(external)
        with self.assertRaises(ValueError): build_history(self.home,self.out,False)
        self.assertEqual(external.read_text(),'preserve')

    def test_compressed_archive_is_read_when_decoder_available(self):
        try: from compression import zstd
        except ImportError: self.skipTest('stdlib zstd unavailable')
        p=self.home/'.codex/archived_sessions/archive.jsonl.zst'
        raw=json.dumps({'type':'session_meta','payload':{'id':'archived'}}).encode()+b'\n'
        p.write_bytes(zstd.compress(raw))
        stats=build_history(self.home,self.out,False)
        self.assertIn(['codex','parsed',1],stats['sources'])


if __name__=='__main__': unittest.main()
