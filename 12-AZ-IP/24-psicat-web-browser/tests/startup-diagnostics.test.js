const test = require('node:test');
const assert = require('node:assert/strict');
const { createStartupDiagnostics } = require('../desktop/lib/startup-diagnostics');

function fixture(overrides = {}) {
  const records = [];
  const messages = [];
  const stderr = [];
  const proc = {
    env: { PSICAT_BROWSER_SUITE_IPC: '1', PSICAT_BROWSER_USER_DATA: 'C:\\Suite User\\Product24' },
    platform: 'win32', pid: 123, versions: { electron: '44.10.2' }, connected: true,
    send(message, callback) { messages.push(message); callback(null); },
    stderr: { write(line) { stderr.push(line); } },
    ...overrides,
  };
  const fsImpl = {
    mkdirSync() {},
    appendFileSync(...args) { records.push(args); },
  };
  return { proc, records, messages, stderr, diagnostics: createStartupDiagnostics({ processImpl: proc, fsImpl }) };
}

test('early Windows diagnostics use only the explicit per-user path and credential-free fields', async () => {
  const { diagnostics, records, messages, stderr } = fixture();
  diagnostics.mark('entry');
  await diagnostics.failure(Object.assign(new Error('token=never-leak page=never-leak'), { code: 'ENOENT' }));
  assert.equal(records[0][0], 'C:\\Suite User\\Product24\\product24-startup.jsonl');
  assert.equal(records[0][2].mode, 0o600);
  assert.equal(messages[0].type, 'boot');
  assert.equal(messages[0].ipc_available, true);
  assert.equal(messages[1].type, 'startup-failed');
  assert.match(messages[1].error, /entry.*Error\/ENOENT/);
  assert.equal(JSON.stringify({ records, messages, stderr }).includes('never-leak'), false);
});

test('missing IPC reports availability accurately without silently adopting another transport', async () => {
  const { diagnostics, records, messages } = fixture({ connected: false, send: undefined });
  diagnostics.mark('entry');
  assert.equal(await diagnostics.failure(new Error('missing IPC')), false);
  assert.equal(messages.length, 0);
  assert.equal(JSON.parse(records[0][1]).ipc_available, false);
  assert.equal(JSON.parse(records[0][1]).connected, false);
});

test('relative user-data paths never become diagnostic write targets', async () => {
  const { diagnostics, records } = fixture({ env: { PSICAT_BROWSER_SUITE_IPC: '1', PSICAT_BROWSER_USER_DATA: '../wrong' } });
  diagnostics.mark('entry');
  await diagnostics.failure(new Error('bad path'));
  assert.equal(records.length, 0);
});

test('blocked stderr and storage do not prevent startup failure over owned IPC', async () => {
  const proc = fixture().proc;
  proc.stderr.write = () => { throw new Error('closed'); };
  const diagnostics = createStartupDiagnostics({
    processImpl: proc, fsImpl: { mkdirSync() { throw new Error('denied'); } },
  });
  diagnostics.mark('entry');
  assert.equal(await diagnostics.failure(new Error('startup failure')), true);
});
