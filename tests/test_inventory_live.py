import tempfile
import os
import json
import hashlib
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch
from aethel_projects.inventory_live import observe, watch_inventory, attach_observations, enrich_purposes


def scan(*, repos=(), checks=(), non_git=(), errors=0):
    return {'root':'/synthetic','summary':{'filesystem_errors':errors,'checkout_errors':0},
            'errors':[] if not errors else [{'error':'denied'}],
            'repositories':[{'git_common_dir':x,'paths':[x]} for x in repos],
            'checkouts':[{'path':p,'head':h,'branch':'main','dirty_files':n,'git_common_dir':p} for p,h,n in checks],
            'projects_without_git':[{'path':p} for p in non_git]}

class InventoryLiveTests(unittest.TestCase):
    def test_new_and_changed_are_observations_not_assumed_products(self):
        first=observe('/synthetic',builder=lambda root,jobs: scan(repos=['/a'],checks=[('/a','a',0)]))
        second=observe('/synthetic',first,builder=lambda root,jobs: scan(repos=['/a','/b'],checks=[('/a','b',1)],non_git=['/c']))
        self.assertEqual(second['changes']['new_repositories'],['/b'])
        self.assertEqual(second['changes']['changed_checkouts'],['/a'])
        self.assertEqual(second['changes']['new_non_git_candidates'],['/c'])

    def test_partial_scan_never_claims_missing_is_deleted(self):
        first=observe('/synthetic',builder=lambda root,jobs:scan(repos=['/a']))
        result=observe('/synthetic',first,builder=lambda root,jobs:scan(errors=1))
        self.assertEqual(result['status'],'partial')
        self.assertEqual(result['changes']['missing_repositories'],[])
        self.assertEqual(result['last_success_at'],first['last_success_at'])

    def test_exception_retains_last_snapshot(self):
        first=observe('/synthetic',builder=lambda root,jobs:scan(repos=['/a']))
        def fail(root,jobs): raise OSError('hidden path')
        result=observe('/synthetic',first,builder=fail)
        self.assertEqual(result['status'],'error')
        self.assertEqual(result['scan'],first['scan'])
        self.assertNotIn('hidden path',result['message'])

    def test_repeated_partial_scans_can_find_new_observations_but_not_removals(self):
        first=observe('/synthetic',builder=lambda root,jobs:scan(repos=['/a'],errors=1))
        second=observe('/synthetic',first,builder=lambda root,jobs:scan(repos=['/b'],errors=1))
        self.assertFalse(second['baseline'])
        self.assertEqual(second['changes']['new_repositories'],['/b'])
        self.assertEqual(second['changes']['missing_repositories'],[])
        self.assertIsNone(second['last_success_at'])

    def test_real_inventory_detects_new_repo_and_repeated_dirty_change(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t).resolve()
            first=observe(root)
            repo=root/'project';repo.mkdir()
            env={**os.environ,'GIT_CONFIG_COUNT':'1','GIT_CONFIG_KEY_0':'commit.gpgsign','GIT_CONFIG_VALUE_0':'false',
                 'GIT_AUTHOR_NAME':'Test','GIT_AUTHOR_EMAIL':'test@example.invalid',
                 'GIT_COMMITTER_NAME':'Test','GIT_COMMITTER_EMAIL':'test@example.invalid'}
            def git(*args): subprocess.run(['git','-C',str(repo),*args],env=env,check=True,capture_output=True)
            git('init');f=repo/'code.txt';f.write_text('initial');git('add','code.txt');git('commit','-m','fixture')
            second=observe(root,first)
            self.assertEqual(len(second['changes']['new_repositories']),1)
            f.write_text('first change');third=observe(root,second)
            self.assertIn(str(repo),third['changes']['changed_checkouts'])
            f.write_text('different length and contents');fourth=observe(root,third)
            self.assertIn(str(repo),fourth['changes']['changed_checkouts'])

    def test_readme_purpose_is_source_labelled_and_symlinks_are_not_read(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t).resolve(); repo=root/'project'; repo.mkdir()
            readme=repo/'README.md'; readme.write_text('# Project\n\nA useful project for testing.\n')
            result={'repositories':[{'git_common_dir':str(repo/'.git'),'paths':[str(repo)]}],
                    'checkouts':[{'path':str(repo),'head':'a1','dirty_files':0}]}
            enrich_purposes(result)
            purpose=result['repositories'][0]['readme_purpose']
            self.assertEqual(purpose['source'],str(readme))
            self.assertEqual(purpose['sha256'],hashlib.sha256(readme.read_bytes()).hexdigest())
            self.assertEqual(purpose['head_observed'],'a1')
            readme.unlink();readme.symlink_to(root/'outside')
            result['repositories'][0].pop('readme_purpose')
            enrich_purposes(result)
            self.assertNotIn('readme_purpose',result['repositories'][0])

    def test_observation_requires_exact_identity_revision_and_source_bytes(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t).resolve();repo=root/'repo';repo.mkdir();source=repo/'README.md';source.write_text('Evidence')
            common=str(repo/'.git');path=str(repo);evidence=root/'evidence';evidence.mkdir()
            observation={'projects':[{'path':path,'common_dir':common,'head':'a1','observed_at':'now'}]}
            finding={'findings':[{'purpose':'Useful','finding':'Observed','next_step':'Check','sources':[{'path':str(source),'line':1,'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}]}]}
            (evidence/'direct-observations.json').write_text(json.dumps(observation));(evidence/'independent-findings.json').write_text(json.dumps(finding))
            inventory={'repositories':[{'git_common_dir':common,'paths':[path]}], 'checkouts':[{'path':path,'git_common_dir':common,'head':'a1'}]}
            attach_observations(inventory,evidence)
            self.assertEqual(inventory['repositories'][0]['direct_observation']['purpose'],'Useful')
            source.write_text('Changed')
            attach_observations(inventory,evidence)
            self.assertEqual(inventory['repositories'][0]['direct_observation']['state'],'no_matching_verified_finding')
            inventory['checkouts'][0]['head']='b2'
            attach_observations(inventory,evidence)
            self.assertEqual(inventory['repositories'][0]['direct_observation']['state'],'stale_revision')

    def test_analyzer_report_requires_scope_and_digest_and_never_exposes_repro(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t).resolve();repo=root/'repo';repo.mkdir();source=repo/'main.py';source.write_text('evidence')
            common=str(repo/'.git');evidence=root/'evidence';evidence.mkdir();path=str(repo)
            (evidence/'direct-observations.json').write_text(json.dumps({'projects':[]}))
            (evidence/'independent-findings.json').write_text(json.dumps({'findings':[]}))
            report={'schema':'aethel.code_analyzer.aix_findings.v1','scope':path,'scan':{'file_digests':{'main.py':hashlib.sha256(source.read_bytes()).hexdigest()},'incomplete_reasons':['limited']},'truncated':False,'findings':[{'file':'main.py','line':1,'rule':'x','evidence_tier':'heuristic','repro':'do not execute'}]}
            raw=json.dumps(report).encode();(evidence/'test-analyzer.json').write_bytes(raw)
            (evidence/'test-analyzer-run.json').write_text(json.dumps({'returncode':0,'sha256':hashlib.sha256(raw).hexdigest()}))
            inventory={'repositories':[{'git_common_dir':common,'paths':[path]}], 'checkouts':[{'path':path,'git_common_dir':common,'head':'a1'}]}
            attach_observations(inventory,evidence);result=inventory['repositories'][0]['analyzer_observation']
            self.assertEqual(result['source_state'],'matched_scanned_files');self.assertEqual(result['incomplete_reasons'],['limited'])
            self.assertNotIn('repro',result['findings'][0])
            source.write_text('changed');attach_observations(inventory,evidence)
            self.assertEqual(inventory['repositories'][0]['analyzer_observation']['source_state'],'stale_or_missing_scanned_files')

    def test_rejects_public_directory_and_fast_poll(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t).resolve(); public=root/'public';public.mkdir(mode=0o755)
            with self.assertRaises(ValueError):watch_inventory(root,public/'out.json',once=True)
            with self.assertRaises(ValueError):watch_inventory(root,root/'private'/'out.json',interval=10,once=True)

    def test_private_atomic_output(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t).resolve();target=root/'private'/'out.json'
            with patch('aethel_projects.inventory_live.inventory.build',return_value=scan()):
                result=watch_inventory('/synthetic',target,once=True)
            self.assertEqual(result['status'],'ok')
            self.assertEqual(target.stat().st_mode & 0o777,0o600)
            self.assertEqual(target.parent.stat().st_mode & 0o777,0o700)

if __name__=='__main__':unittest.main()
