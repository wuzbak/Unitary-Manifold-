# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import types

from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('hf_live_status', ROOT / 'hf-spaces/space_core/live_status.py')
loader = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(loader)


def test_loader_failure_and_null_are_not_zero():
    with patch.object(loader, '_build_from_generator', return_value=None), \
         patch.object(loader, '_read_json', return_value=None), \
         patch.object(loader, '_read_url', return_value=None):
        snapshot = loader.status_snapshot()
    assert snapshot['source'] == 'unavailable'
    assert snapshot['tests_failed'] is None
    assert snapshot['hardgate_pillars'] is None
    assert snapshot['date'] == 'unknown'


def test_loader_source_and_zero():
    payload = {'meta': {'version': '2', 'date': '2026-01-02'},
               'tests': {'passed': None, 'failed': 0}, 'lean4': {}, 'pillars': {}}
    with patch.object(loader, '_build_from_generator', return_value=None), \
         patch.object(loader, '_read_json', return_value=payload), \
         patch.object(loader, '_read_url', side_effect=AssertionError('unexpected remote request')):
        snapshot = loader.status_snapshot()
    assert (snapshot['source'], snapshot['date'], snapshot['version']) == ('local artifact', '2026-01-02', 'v2')
    assert snapshot['tests_passed'] is None
    assert snapshot['tests_failed'] == 0


def test_remote_source_includes_url():
    payload = {'meta': {}, 'tests': {}, 'lean4': {}, 'pillars': {}}
    with patch.object(loader, '_build_from_generator', return_value=None), \
         patch.object(loader, '_read_json', return_value=None), \
         patch.object(loader, '_read_url', return_value=payload):
        assert loader.status_snapshot()['source'] == loader.DEFAULT_STATUS_URL


def test_deployment_uploads_shared_package_for_every_space():
    text = (ROOT / '.github/workflows/deploy-hf-spaces.yml').read_text()
    block = text.split("python3 - <<'EOF'\n", 1)[1].split('\n          EOF', 1)[0]
    script = '\n'.join(line.removeprefix('          ') for line in block.splitlines())
    uploads = []
    class Api:
        def __init__(self, **kwargs): pass
        def whoami(self): return {'name': 'tester'}
        def create_repo(self, **kwargs): pass
        def upload_folder(self, **kwargs):
            folder = Path(kwargs['folder_path'])
            uploads.append({
                'repo_id': kwargs['repo_id'],
                'files': {path.relative_to(folder).as_posix() for path in folder.rglob('*') if path.is_file()},
            })
    with patch.dict(sys.modules, {'huggingface_hub': types.SimpleNamespace(HfApi=Api)}), \
         patch.dict('os.environ', {'HF_TOKEN': 'test'}):
        exec(script, {})
    apps = {p.name for p in (ROOT / 'hf-spaces').iterdir() if (p / 'app.py').is_file()}
    assert len(uploads) == len(apps)
    for app in apps:
        upload = next(u for u in uploads if u['repo_id'] == f'tester/{app}')
        assert f'{app}/app.py' not in upload['files']
        assert 'app.py' in upload['files']
        assert 'space_core/live_status.py' in upload['files']


def run_node(script):
    subprocess.run(['node', '-e', script], cwd=ROOT, check=True)


def test_bundled_page_snapshot_zero_null_and_failure():
    for page in ('public-site/status/index.html', 'public-site/portal/library/index.html'):
        text = (ROOT / page).read_text()
        assert '/api/status' not in text
        assert 'status-snapshot.js' in text
        assert 'status-source' in text
        assert 'Unavailable' in text
    run_node(r'''
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const nodes = Object.fromEntries(['count', 'zero', 'status-source'].map(id => [id, {textContent:'Unavailable'}]));
const context = {document: {getElementById: id => nodes[id]}, fetch: async () => ({ok:true, json:async () => ({tests_passed:null, tests_failed:0, date:'2026-11-07'})})};
vm.createContext(context); vm.runInContext(fs.readFileSync('public-site/js/status-snapshot.js','utf8'), context);
(async () => {
 await context.loadBundledStatus('snapshot.json', {tests_passed:['count'], tests_failed:['zero']});
 assert.equal(nodes.count.textContent, 'Unavailable'); assert.equal(nodes.zero.textContent, '0');
 assert.match(nodes['status-source'].textContent, /historical snapshot.*2026-11-07/);
 context.fetch = async () => { throw Error('offline'); };
 await context.loadBundledStatus('snapshot.json', {tests_failed:['zero']});
 assert.equal(nodes.zero.textContent, 'Unavailable');
 assert.equal(nodes['status-source'].textContent, 'Status snapshot unavailable.');
})().catch(e => {console.error(e); process.exitCode = 1});
''')


def test_desi_scalar_never_falsifies_and_dashboard_is_qualified():
    run_node(r'''
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const ctx = {}; vm.createContext(ctx); vm.runInContext(fs.readFileSync('public-site/js/physics-engine.js','utf8'), ctx);
for (const sigma of [0, 3, 5, 10]) {
 const r = vm.runInContext('UM', ctx).desiTensionTracker(sigma); assert.equal(r.falsified, null); assert.match(r.honest_note, /3 independent datasets/);
}
const d = vm.runInContext('UM', ctx).verificationDashboardData();
assert.equal(d.admissions.find(x => x.id === 8).closed, false);
assert.equal(d.admissions.find(x => x.id === 10).status, 'MODEL_DEPENDENT_UNESTABLISHED');
assert.equal(d.predictions.find(x => x.name === 'Tensor ratio r').status, 'IN_TENSION');
''')


if __name__ == '__main__':
    for name, test in list(globals().items()):
        if name.startswith('test_') and callable(test):
            test()
            print(f'PASS {name}')
