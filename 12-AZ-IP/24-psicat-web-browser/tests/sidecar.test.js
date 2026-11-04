const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const net = require('node:net');
const http = require('node:http');
const { EventEmitter, once } = require('node:events');
const { execFileSync } = require('node:child_process');
const { Sidecar, pythonCommand, navigatorEnvironment } = require('../desktop/lib/sidecar');

const productRoot = path.resolve(__dirname, '..');
const script = path.join(productRoot, 'sync_backend', 'server.py');

function fakeChild() {
  const child = new EventEmitter();
  Object.assign(child, { pid: 12345, exitCode: null, signalCode: null, signals: [] });
  child.kill = (signal) => {
    child.signals.push(signal);
    child.signalCode = signal;
    queueMicrotask(() => { child.emit('exit', null, signal); child.emit('close', null, signal); });
    return true;
  };
  return child;
}

function fakeManager(overrides = {}) {
  const child = fakeChild();
  const calls = [];
  const manager = new Sidecar({
    name: 'Test sync', script, port: 8787, healthPath: '/api/sync/health',
    validateHealth: (payload) => payload.ok === true,
    checkPort: async () => {},
    spawnImpl: (...args) => { calls.push(args); return child; },
    fetchImpl: async () => ({ ok: true, json: async () => ({ ok: true }) }),
    timeoutMs: 100, probeTimeoutMs: 20, pollMs: 5, stopTimeoutMs: 20,
    ...overrides,
  });
  return { child, calls, manager };
}

test('native Windows uses py -3 unless an absolute suite interpreter is provided', () => {
  assert.deepEqual(pythonCommand({}, 'win32'), { executable: 'py', args: ['-3'] });
  assert.deepEqual(pythonCommand({}, 'linux'), { executable: 'python3', args: [] });
  assert.deepEqual(pythonCommand({ PSICAT_BROWSER_PYTHON: 'C:\\Program Files\\Suite\\python.exe' }, 'win32'),
    { executable: 'C:\\Program Files\\Suite\\python.exe', args: [] });
  assert.deepEqual(pythonCommand({ PSICAT_BROWSER_PYTHON: '/suite/python/bin/python' }, 'linux'),
    { executable: '/suite/python/bin/python', args: [] });
  assert.throws(() => pythonCommand({ PSICAT_BROWSER_PYTHON: 'python3 --unsafe' }, 'linux'), /absolute/);
  assert.throws(() => pythonCommand({ PSICAT_BROWSER_PYTHON: '"C:\\Suite\\python.exe"' }, 'win32'), /absolute/);
});

test('browser-owned Navigator never inherits suite operator or profile-resume secrets', () => {
  const env = { PATH: 'local', PSICAT_LOCAL_EXECUTION_TOKEN: 'operator',
    MERLIN_SESSION_SECRET: 'session', MERLIN_PROFILE_SHARED_KEY: 'profile', OPENROUTER_API_KEY: 'model' };
  assert.deepEqual(navigatorEnvironment(env), { PATH: 'local', OPENROUTER_API_KEY: 'model' });
  assert.equal(env.PSICAT_LOCAL_EXECUTION_TOKEN, 'operator');
});

test('owned launch uses argument arrays, no shell, loopback and a specific child shutdown', async () => {
  const { manager, child, calls } = fakeManager({ env: { PSICAT_BROWSER_PYTHON: '/suite/python' }, args: ['--store', '/suite user/store.json'] });
  await Promise.all([manager.start(), manager.start()]);
  assert.equal(manager.state.status, 'ready');
  assert.equal(calls.length, 1);
  assert.equal(calls[0][0], '/suite/python');
  assert.deepEqual(calls[0][1], ['-u', script, '--host', '127.0.0.1', '--port', '8787', '--store', '/suite user/store.json']);
  assert.equal(calls[0][2].shell, false);
  assert.equal(calls[0][2].detached, false);
  assert.equal(calls[0][2].windowsHide, true);
  await manager.stop();
  assert.equal(manager.state.status, 'stopped');
  assert.equal(manager.state.pid, null);
  assert.deepEqual(child.signals, ['SIGTERM']);
});

test('disabled or missing sidecars do not spawn', async () => {
  const disabled = fakeManager();
  await disabled.manager.start({ enabled: false });
  assert.equal(disabled.manager.state.status, 'disabled');
  assert.equal(disabled.calls.length, 0);
  const missing = fakeManager({ script: path.join(productRoot, 'no-such-sidecar.py') });
  await missing.manager.start();
  assert.equal(missing.manager.state.status, 'failed');
  assert.match(missing.manager.state.error, /entry point not found/);
  assert.equal(missing.calls.length, 0);
});

test('spawn errors and early exits are surfaced without unhandled error events', async () => {
  for (const mode of ['error', 'exit']) {
    const child = fakeChild();
    const { manager } = fakeManager({
      spawnImpl: () => {
        setImmediate(() => {
          if (mode === 'error') {
            child.emit('error', Object.assign(new Error('missing interpreter'), { code: 'ENOENT' }));
          } else {
            child.exitCode = 2;
            child.emit('exit', 2, null);
          }
          child.emit('close', 2, null);
        });
        return child;
      },
      fetchImpl: async () => { throw new Error('not listening'); },
    });
    await manager.start();
    assert.equal(manager.state.status, 'failed');
    assert.match(manager.state.error, mode === 'error' ? /ENOENT/ : /exited \(2\)/);
    assert.equal(manager.child, null);
  }
});

test('wrong health payload times out and kills only the spawned child', async () => {
  const { manager, child } = fakeManager({
    fetchImpl: async () => ({ ok: true, json: async () => ({ service: 'unrelated' }) }),
  });
  await manager.start();
  assert.equal(manager.state.status, 'failed');
  assert.match(manager.state.error, /deadline|timed out/);
  assert.deepEqual(child.signals, ['SIGTERM']);
  assert.equal(manager.child, null);
});

test('shutdown while port checking cancels startup before spawn', async () => {
  let release;
  const { manager, calls } = fakeManager({ checkPort: () => new Promise((resolve) => { release = resolve; }) });
  const starting = manager.start();
  const stopping = manager.stop();
  release();
  await Promise.all([starting, stopping]);
  assert.equal(calls.length, 0);
  assert.equal(manager.state.status, 'stopped');
});

test('shutdown during health probing cannot later mark the sidecar ready', async () => {
  let probe;
  const { manager, child } = fakeManager({
    fetchImpl: (_url, { signal }) => new Promise((_resolve, reject) => {
      probe();
      signal.addEventListener('abort', () => reject(signal.reason), { once: true });
    }),
  });
  const probing = new Promise((resolve) => { probe = resolve; });
  const starting = manager.start();
  await probing;
  await manager.stop();
  await starting;
  assert.equal(manager.state.status, 'stopped');
  assert.equal(manager.child, null);
  assert.deepEqual(child.signals, ['SIGTERM']);
});

test('unexpected exit after readiness is a visible failure', async () => {
  const { manager, child } = fakeManager();
  await manager.start();
  child.exitCode = 3;
  child.emit('exit', 3, null);
  child.emit('close', 3, null);
  assert.equal(manager.state.status, 'failed');
  assert.match(manager.state.error, /exited \(3\)/);
  assert.equal(manager.state.pid, null);
});

test('stubborn owned child receives bounded specific-process escalation', async () => {
  const child = fakeChild();
  const originalKill = child.kill;
  child.kill = (signal) => {
    if (signal === 'SIGKILL') return originalKill(signal);
    child.signals.push(signal);
    return true;
  };
  const { manager } = fakeManager({ spawnImpl: () => child });
  await manager.start();
  await manager.stop();
  assert.deepEqual(child.signals, ['SIGTERM', 'SIGKILL']);
});

test('an unresponsive child produces a visible cleanup failure rather than false success', async () => {
  const child = fakeChild();
  child.kill = (signal) => { child.signals.push(signal); return false; };
  const { manager } = fakeManager({ spawnImpl: () => child });
  await manager.start();
  await assert.rejects(manager.stop(), /did not stop/);
  assert.equal(manager.state.status, 'failed');
  assert.equal(manager.child, child);
  assert.deepEqual(child.signals, ['SIGTERM', 'SIGKILL']);
  child.exitCode = 1;
  child.emit('exit', 1, null);
  child.emit('close', 1, null);
  await manager.stop();
});

async function listen(server) {
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  return server.address().port;
}

test('occupied loopback port fails closed without spawning or adopting another server', async () => {
  const server = net.createServer();
  const port = await listen(server);
  let spawned = false;
  const manager = new Sidecar({ name: 'Sync', script, port, healthPath: '/api/sync/health',
    validateHealth: () => true, spawnImpl: () => { spawned = true; throw new Error('must not spawn'); } });
  try {
    await manager.start();
    assert.equal(manager.state.status, 'failed');
    assert.match(manager.state.error, /unavailable/);
    assert.equal(spawned, false);
    assert.equal(server.listening, true);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test('a stalled HTTP response body is bounded and the owned child is stopped', async () => {
  const server = http.createServer((_req, res) => {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.write('{"ok":');
  });
  const port = await listen(server);
  const { manager, child } = fakeManager({ port, fetchImpl: fetch });
  try {
    await manager.start();
    assert.equal(manager.state.status, 'failed');
    assert.equal(manager.child, null);
    assert.deepEqual(child.signals, ['SIGTERM']);
  } finally {
    server.closeAllConnections();
    await new Promise((resolve) => server.close(resolve));
  }
});

test('real Python sync child starts, writes outside installed sources, health-checks and stops', async () => {
  const work = fs.mkdtempSync(path.join(productRoot, '.sidecar-test-'));
  const probe = net.createServer();
  const port = await listen(probe);
  await new Promise((resolve) => probe.close(resolve));
  const command = pythonCommand();
  const executable = execFileSync(command.executable, [...command.args, '-c', 'import sys; print(sys.executable)'], { encoding: 'utf8' }).trim();
  const store = path.join(work, 'user data', 'sync_store.json');
  const manager = new Sidecar({ name: 'Sync integration', script, port,
    env: { ...process.env, PSICAT_BROWSER_PYTHON: executable },
    args: ['--store', store, '--instance-id', 'product24-test'],
    healthPath: '/api/sync/health',
    validateHealth: (payload) => payload.ok && payload.service === 'psicat-sync-backend' && payload.instance_id === 'product24-test',
    timeoutMs: 5000,
  });
  try {
    await manager.start();
    assert.equal(manager.state.status, 'ready', manager.state.error);
    const pid = manager.state.pid;
    const response = await fetch(`${manager.state.baseUrl}/api/sync/push`, {
      method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Sync-Token': 'separate-browser-token' },
      body: JSON.stringify({ account_email: 'browser@example.com', packet: { product: 24 } }),
    });
    assert.equal(response.status, 200);
    assert.equal(JSON.parse(fs.readFileSync(store, 'utf8'))['browser@example.com'].packet.product, 24);
    await manager.stop();
    assert.equal(manager.state.status, 'stopped');
    assert.throws(() => process.kill(pid, 0), { code: 'ESRCH' });
    await assert.rejects(fetch(`${manager.state.baseUrl}/api/sync/health`, { signal: AbortSignal.timeout(500) }));
  } finally {
    await manager.stop();
    fs.rmSync(work, { recursive: true, force: true });
  }
});

test('a real invalid suite interpreter fails without retrying an ambient interpreter', async () => {
  const { manager } = fakeManager({
    spawnImpl: require('node:child_process').spawn,
    env: { ...process.env, PSICAT_BROWSER_PYTHON: path.join(productRoot, 'missing python', 'python.exe') },
    fetchImpl: async () => { throw new Error('not listening'); },
  });
  await manager.start();
  assert.equal(manager.state.status, 'failed');
  assert.match(manager.state.error, /ENOENT/);
  assert.equal(manager.child, null);
});
