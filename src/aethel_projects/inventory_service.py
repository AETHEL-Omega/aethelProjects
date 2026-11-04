"""Run one existing inventory under the installed AIX resource and gate leases."""
from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import re
import subprocess

from .inventory_live import watch_inventory
from .work_history import _write_private, private_directory


def _resource(executable, *args):
    result = subprocess.run([str(executable), *args], capture_output=True, text=True, timeout=30, check=False)
    if result.returncode:
        raise RuntimeError('Ressourcenautorität verweigert oder nicht erreichbar')
    return json.loads(result.stdout)


def run_once(root, target, runtime, *, observations_dir=None):
    """Fail closed; release both leases even when a scan raises."""
    output = Path(target).expanduser()
    directory = private_directory(output.parent)
    status_file = directory / 'inventory-service-status.json'
    gate_file = None
    gate = None
    lease = None
    resource = Path(runtime).expanduser() / 'bin' / 'aix-resource'
    gate_path = Path(runtime).expanduser() / 'bin' / '_aix_gate_lock.py'
    status = {'state': 'deferred', 'at': datetime.now(timezone.utc).isoformat()}
    try:
        spec = importlib.util.spec_from_file_location('_aethel_existing_gate_lock', gate_path)
        if spec is None or spec.loader is None or not resource.is_file():
            raise RuntimeError('Installierte AIX-Ressourcenautorität fehlt')
        gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gate)
        gate_file, _, capped = gate.acquire(timeout_s=0, quiet=True, art='projects-inventory', erwartet_s=900)
        if capped or gate_file is None:
            raise RuntimeError('Gate belegt; Inventur verschoben')
        decision = _resource(resource, 'acquire', 'IO_TASK', '1', '--owner', 'projects-inventory', '--task', 'index')
        candidate = decision.get('lease_id')
        if decision.get('ok') is not True or not isinstance(candidate, str) or not re.fullmatch(r'[0-9a-f]{12}', candidate):
            raise RuntimeError('Keine gebuchte IO-Ressourcenlease')
        lease = candidate
        result = watch_inventory(root, output, jobs=1, once=True, observations_dir=observations_dir)
        status = {'state': result.get('status', 'error'), 'at': result.get('attempted_at')}
        return result
    except Exception as error:
        status['reason'] = str(error)[:160]
        raise
    finally:
        if lease:
            try:
                subprocess.run([str(resource), 'release', 'IO_TASK', '1', '--lease', lease],
                               capture_output=True, text=True, timeout=30, check=True)
            except (OSError, subprocess.SubprocessError):
                status['lease_release'] = 'unconfirmed'
        if gate is not None and gate_file is not None:
            try:
                gate.release(gate_file)
            except OSError:
                status['gate_release'] = 'unconfirmed'
        _write_private(status_file, json.dumps(status, ensure_ascii=False))
