const test = require('node:test');
const assert = require('node:assert/strict');
const { EventEmitter } = require('node:events');
const { attachSuiteLifecycle, PROTOCOL } = require('../desktop/lib/suite-lifecycle');

test('suite mode requires a private inherited IPC channel and standalone does not', async () => {
  assert.throws(() => attachSuiteLifecycle({ enabled: true, processImpl: {}, onShutdown() {} }), /IPC channel/);
  assert.equal(await attachSuiteLifecycle({}).notify('ready'), false);
});

test('only explicit lifecycle shutdown messages and IPC disconnect request shutdown', async () => {
  const proc = new EventEmitter();
  const messages = [];
  proc.connected = true;
  proc.send = (message, callback) => { messages.push(message); callback(null); };
  let shutdowns = 0;
  const channel = attachSuiteLifecycle({ enabled: true, processImpl: proc, onShutdown: () => { shutdowns += 1; } });
  for (const message of [{ type: 'shutdown' }, { protocol: PROTOCOL, type: 'shutdown', request_id: '../bad' },
    { protocol: PROTOCOL, type: 'ready', request_id: '123' }]) proc.emit('message', message);
  assert.equal(shutdowns, 0);
  proc.emit('message', { protocol: PROTOCOL, type: 'shutdown', request_id: 'suite-stop-1' });
  assert.equal(shutdowns, 1);
  await channel.notify('stopped', { sync: { status: 'stopped', pid: null, baseUrl: 'http://127.0.0.1:8787',
    error: '', token: 'never-send', cookie: 'never-send' }, secret: 'never-send' });
  assert.equal(messages[0].request_id, 'suite-stop-1');
  assert.equal(messages[0].product_id, 24);
  assert.equal(JSON.stringify(messages).includes('never-send'), false);
  proc.connected = false;
  proc.emit('disconnect');
  assert.equal(shutdowns, 2);
  assert.equal(await channel.notify('stopped'), false);
});

test('send failure remains bounded when the suite channel closes', async () => {
  const proc = new EventEmitter();
  proc.connected = true;
  proc.send = () => { throw new Error('IPC closed'); };
  const channel = attachSuiteLifecycle({ enabled: true, processImpl: proc, onShutdown() {} });
  assert.equal(await channel.notify('ready'), false);
});
