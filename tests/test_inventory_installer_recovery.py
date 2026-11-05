"""Installer recovery must preserve control of a loaded service and permit retry."""
from __future__ import annotations

import io
from pathlib import Path
import runpy
import tarfile
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


class InstallerRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.output = self.root / 'private' / 'inventory.json'
        self.output.parent.mkdir(mode=0o700)
        self.runtime = self.root / 'runtime' / 'bin'
        self.runtime.mkdir(parents=True)
        (self.runtime / 'aix-resource').touch()
        (self.runtime / '_aix_gate_lock.py').touch()
        self.namespace = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'bin' / 'install-inventory-agent'))
        self.main = self.namespace['main']
        self.home = patch.object(Path, 'home', return_value=self.root)
        self.home.start(); self.addCleanup(self.home.stop)
        self.plist = self.root / 'Library' / 'LaunchAgents' / 'com.aethel.projects.inventory.plist'

    def args(self, action):
        return ['install-inventory-agent', action, '--out', str(self.output), '--aix-runtime', str(self.runtime.parent)]

    def test_failed_stop_keeps_service_definition(self):
        self.plist.parent.mkdir(parents=True)
        self.plist.write_text('owned service')
        with patch('sys.argv', self.args('uninstall')), patch('subprocess.run', return_value=SimpleNamespace(returncode=1)):
            with self.assertRaises(SystemExit):
                self.main()
        self.assertTrue(self.plist.exists())

    def test_failed_bootstrap_allows_verified_same_revision_retry(self):
        payload = io.BytesIO()
        with tarfile.open(fileobj=payload, mode='w') as archive:
            data = b'fixture\n'
            info = tarfile.TarInfo('bin/aethel-projects')
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))
        calls = []
        def run(command, **kwargs):
            if command[0] == 'git':
                if 'rev-parse' in command: return SimpleNamespace(stdout='a' * 40 + '\n', returncode=0)
                if 'status' in command: return SimpleNamespace(stdout='', returncode=0)
                if 'archive' in command: return SimpleNamespace(stdout=payload.getvalue(), returncode=0)
            if command[0] == '/bin/launchctl' and command[1] == 'bootstrap':
                calls.append(command)
                return SimpleNamespace(returncode=1 if len(calls) == 1 else 0)
            raise AssertionError(command)
        with patch('sys.argv', self.args('install')), patch('subprocess.run', side_effect=run):
            with self.assertRaises(SystemExit):
                self.main()
            self.assertEqual(self.main(), 0)
        self.assertEqual(len(calls), 2)
        self.assertTrue(self.plist.is_file())


if __name__ == '__main__':
    unittest.main()
