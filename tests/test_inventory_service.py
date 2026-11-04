import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from aethel_projects import inventory_service


class InventoryServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.target = self.base / 'private' / 'inventory.json'
        self.runtime = self.base / 'runtime'
        (self.runtime / 'bin').mkdir(parents=True)
        (self.runtime / 'bin' / 'aix-resource').touch()
        self.released = []
        self.gate = SimpleNamespace(acquire=lambda **kw: ('lock', 0, False),
                                    release=lambda lock: self.released.append(lock))
        loader = SimpleNamespace(exec_module=lambda module: None)
        self.spec = SimpleNamespace(loader=loader)
        self.patches = [patch.object(inventory_service.importlib.util, 'spec_from_file_location', return_value=self.spec),
                        patch.object(inventory_service.importlib.util, 'module_from_spec', return_value=self.gate)]
        for item in self.patches:
            item.start(); self.addCleanup(item.stop)

    def test_cli_guard_requires_single_watch_and_output(self):
        from aethel_projects.cli import _build_parser, _cmd_inventory, EXIT_USAGE
        args = _build_parser().parse_args(['inventory', '--aix-runtime', str(self.runtime)])
        self.assertEqual(_cmd_inventory(args), EXIT_USAGE)

    def test_resource_denial_keeps_previous_inventory(self):
        self.target.parent.mkdir(mode=0o700)
        self.target.write_text('previous')
        with patch.object(inventory_service, '_resource', side_effect=RuntimeError('denied')), \
             patch.object(inventory_service, 'watch_inventory') as scan:
            with self.assertRaises(RuntimeError):
                inventory_service.run_once('/work', self.target, self.runtime)
            scan.assert_not_called()
        self.assertEqual(self.target.read_text(), 'previous')
        self.assertEqual(self.released, ['lock'])

    def test_unbooked_lease_never_runs_scan_and_releases_gate(self):
        with patch.object(inventory_service, '_resource', return_value={'ok': True, 'lease_id': 'unbooked-123'}), \
             patch.object(inventory_service, 'watch_inventory') as scan:
            with self.assertRaises(RuntimeError):
                inventory_service.run_once('/work', self.target, self.runtime)
            scan.assert_not_called()
        self.assertEqual(self.released, ['lock'])
        self.assertEqual(json.loads((self.target.parent / 'inventory-service-status.json').read_text())['state'], 'deferred')

    def test_busy_gate_does_not_acquire_resource(self):
        self.gate.acquire = lambda **kw: (None, 0, True)
        with patch.object(inventory_service, '_resource') as resource:
            with self.assertRaises(RuntimeError):
                inventory_service.run_once('/work', self.target, self.runtime)
            resource.assert_not_called()

    def test_scan_error_releases_both_leases(self):
        with patch.object(inventory_service, '_resource', return_value={'ok': True, 'lease_id': 'abc123abc123'}), \
             patch.object(inventory_service, 'watch_inventory', side_effect=OSError('scan error')), \
             patch.object(inventory_service.subprocess, 'run') as run:
            with self.assertRaises(OSError):
                inventory_service.run_once('/work', self.target, self.runtime)
            self.assertIn('abc123abc123', run.call_args.args[0])
        self.assertEqual(self.released, ['lock'])

    def test_success_is_bounded_to_one_worker(self):
        result = {'status': 'partial', 'attempted_at': 'now'}
        with patch.object(inventory_service, '_resource', return_value={'ok': True, 'lease_id': 'abc123abc123'}), \
             patch.object(inventory_service, 'watch_inventory', return_value=result) as scan, \
             patch.object(inventory_service.subprocess, 'run'):
            self.assertEqual(inventory_service.run_once('/work', self.target, self.runtime), result)
            self.assertEqual(scan.call_args.kwargs['jobs'], 1)
            self.assertTrue(scan.call_args.kwargs['once'])
        self.assertEqual(self.released, ['lock'])


if __name__ == '__main__':
    unittest.main()
