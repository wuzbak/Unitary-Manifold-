const test = require('node:test');
const assert = require('node:assert/strict');
const { pythonFailure, safeFailureContext } = require('../desktop/lib/component-diagnostics');
const { createStartupDiagnostics } = require('../desktop/lib/startup-diagnostics');

test('Python stderr yields allowlisted import/error classifications only, not arbitrary output', () => {
  assert.deepEqual(pythonFailure("secret never-leak\nModuleNotFoundError: No module named 'src.infrastructure.execution_spine'\n"),
    { python_error: 'MODULE_NOT_FOUND', missing_module: 'src.infrastructure.execution_spine' });
  assert.deepEqual(pythonFailure("ModuleNotFoundError: No module named 'credential.never-leak'\n"),
    { python_error: 'MODULE_NOT_FOUND', missing_module: 'other' });
  assert.deepEqual(pythonFailure("FileNotFoundError: never-leak/path.json\n"), { python_error: 'FILE_NOT_FOUND' });
  assert.deepEqual(pythonFailure('unexpected never-leak'), {});
  assert.deepEqual(pythonFailure("FileNotFoundError: [Errno 2] No such file or directory: '/private/never-leak/bot/assistant_api.py'\n"),
    { python_error: 'FILE_NOT_FOUND', missing_resource: 'bot/assistant_api.py' });
});

test('component failure context strips secrets and arbitrary paths/codes', () => {
  const context = safeFailureContext({
    component: 'navigator',
    components: { navigator: { status: 'failed', failure_code: 'PROCESS_EXIT', exit_code: 1,
      python_error: 'MODULE_NOT_FOUND', missing_module: 'src', error: 'never-leak', token: 'never-leak' } },
    resources: [{ resource: 'src/infrastructure/execution_spine.py', exists: false },
      { resource: '/private/never-leak', exists: false }],
  });
  assert.equal(context.components.navigator.exit_code, 1);
  assert.equal(context.resources.length, 1);
  assert.equal(JSON.stringify(context).includes('never-leak'), false);
});

test('first startup-failed packet explains the failed component without leaking exception text', async () => {
  const messages = [];
  const diagnostics = createStartupDiagnostics({
    processImpl: { env: { PSICAT_BROWSER_SUITE_IPC: '1' }, platform: 'linux', pid: 12,
      versions: { electron: '44.10.2' }, connected: true, stderr: { write() {} },
      send(message, callback) { messages.push(message); callback(null); } },
  });
  diagnostics.mark('ui-and-sidecars-settled');
  await diagnostics.failure(new Error('never-leak'), {
    component: 'navigator', components: {
      sync: { status: 'ready' },
      navigator: { status: 'failed', failure_code: 'PROCESS_EXIT', exit_code: 1,
        python_error: 'MODULE_NOT_FOUND', missing_module: 'httpx' },
    },
  });
  assert.match(messages[1].error, /component=navigator.*code=PROCESS_EXIT.*module=httpx.*exit=1/);
  assert.equal(messages[1].components.sync.status, 'ready');
  assert.equal(JSON.stringify(messages).includes('never-leak'), false);
});
