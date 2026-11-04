import tempfile
import os
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch
from aethel_projects.inventory_live import observe, watch_inventory


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
