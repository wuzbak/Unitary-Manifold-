const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const { spawn } = require('node:child_process');
const { once } = require('node:events');
const { pythonCommand } = require('../desktop/lib/sidecar');
const { PROTOCOL } = require('../desktop/lib/suite-lifecycle');

function testPythonExecutable() {
  const command = process.env.PSICAT_BROWSER_PYTHON
    ? pythonCommand() : { executable: process.platform === 'win32' ? 'python' : 'python3', args: [] };
  return execFileSync(command.executable, [...command.args, '-c', 'import sys; print(sys.executable)'], { encoding: 'utf8' }).trim();
}

test('real Electron UI starts its owned sync sidecar and cleans it up on quit', {
  skip: process.env.PSICAT_BROWSER_ELECTRON_TEST !== '1',
  timeout: 90_000,
}, async () => {
  const { _electron } = require('playwright');
  const root = path.resolve(__dirname, '..');
  const work = fs.mkdtempSync(path.join(root, '.desktop-test-'));
  const python = testPythonExecutable();
  let desktop;
  try {
    desktop = await _electron.launch({
      args: [...(process.platform === 'linux' && process.getuid?.() === 0 ? ['--no-sandbox'] : []), '--enable-logging=stderr', root],
      env: { ...process.env, PSICAT_BROWSER_PYTHON: python,
        PSICAT_BROWSER_USER_DATA: path.join(work, 'user data'),
        PSICAT_BROWSER_DISABLE_NAVIGATOR: '1',
      },
    });

    async function verifySuiteIpc() {
      const root = path.resolve(__dirname, '..');
      const work = fs.mkdtempSync(path.join(root, '.suite-ipc-test-'));
      const python = testPythonExecutable();
      try {
        for (const scenario of ['success', 'invalid-python', 'invalid-user-data', 'navigator-enabled', 'navigator-missing']) {
          console.log(`Real Electron IPC scenario: ${scenario} (${process.platform})`);
          const invalidPython = scenario === 'invalid-python';
          const invalidUserData = scenario === 'invalid-user-data';
          const navigatorMissing = scenario === 'navigator-missing';
          const navigatorEnabled = scenario === 'navigator-enabled' || navigatorMissing;
          const desktop = spawn(require('electron'), [
            ...(process.platform === 'linux' && process.getuid?.() === 0 ? ['--no-sandbox'] : []), '--enable-logging=stderr', root,
          ], {
            env: { ...process.env, PSICAT_BROWSER_SUITE_IPC: '1',
              PSICAT_BROWSER_PYTHON: invalidPython ? path.join(work, 'missing-python.exe') : python,
              PSICAT_BROWSER_USER_DATA: invalidUserData ? 'relative-user-data' : path.join(work, scenario),
              PSICAT_BROWSER_DISABLE_NAVIGATOR: navigatorEnabled ? '0' : '1',
              MERLIN_MEMORY_STORE_PATH: path.join(work, scenario, 'navigator-memory.json'),
              PSICAT_BROWSER_NAVIGATOR_RUN: navigatorMissing ? path.join(work, 'missing-run.py')
                : path.resolve(root, '../20-psicat-navigator/run.py'),
            },
            stdio: ['ignore', 'pipe', 'pipe', 'ipc'], shell: false,
          });
          let stderr = '';
          let stdout = '';
          desktop.stdout.on('data', (chunk) => { stdout = `${stdout}${chunk}`.slice(-16000); });
          desktop.stderr.on('data', (chunk) => { stderr = `${stderr}${chunk}`.slice(-16000); });
          const messages = [];
          const exit = once(desktop, 'exit');
          const lifecycle = new Promise((resolve, reject) => {
            desktop.on('error', reject);
            desktop.on('message', (message) => {
              messages.push(message);
              if (['ready', 'startup-failed'].includes(message.type)) resolve(message);
            });
            desktop.once('exit', (code, signal) => reject(new Error(
              `Desktop exited before lifecycle result: code=${code}, signal=${signal}, boot=${JSON.stringify(messages.filter((message) => message.type === 'boot'))}\nstdout=${stdout}\nstderr=${stderr}`,
            )));
          });
          let timer;
          try {
            const result = await Promise.race([
              lifecycle,
              new Promise((_resolve, reject) => { timer = setTimeout(() => reject(new Error(`IPC readiness timed out: ${stderr}`)), 15000); }),
            ]);
            clearTimeout(timer);
            assert.equal(result.protocol, PROTOCOL);
            assert.equal(result.type, invalidPython || invalidUserData || navigatorMissing ? 'startup-failed' : 'ready',
              `${result.error || ''}\n${JSON.stringify(messages)}`);
            assert.equal(messages.some((message) => message.type === 'boot' && message.phase === 'entry'), true);
            if (!invalidPython && !invalidUserData && !navigatorMissing) {
              assert.equal(result.sync.status, 'ready');
              const health = await fetch(`${result.sync.baseUrl}/api/sync/health`).then((response) => response.json());
              assert.equal(health.ok, true);
              const pid = result.sync.pid;
              const navigatorPid = result.navigator.pid;
              if (navigatorEnabled) {
                assert.equal(result.navigator.status, 'ready', result.navigator.error);
                const status = await fetch(`${result.navigator.baseUrl}/api/psicat/status`).then((response) => response.json());
                assert.equal(status.psicat_available, true);
                assert.equal(typeof status.memory_profile_token, 'string');
              }
              desktop.send({ protocol: PROTOCOL, type: 'shutdown', request_id: 'parent-stop-1' });
              await exit;
              assert.equal(messages.find((message) => message.type === 'stopped')?.request_id, 'parent-stop-1');
              assert.throws(() => process.kill(pid, 0), { code: 'ESRCH' });
              if (navigatorPid) assert.throws(() => process.kill(navigatorPid, 0), { code: 'ESRCH' });
              await assert.rejects(fetch(`${result.sync.baseUrl}/api/sync/health`, { signal: AbortSignal.timeout(500) }));
            } else {
              await exit;
              assert.equal(messages.some((message) => message.type === 'ready'), false);
              if (invalidPython || navigatorMissing) {
                assert.equal(result.component, invalidPython ? 'sync' : 'navigator');
                assert.equal(result.components[result.component].failure_code, invalidPython ? 'SPAWN_ERROR' : 'ENTRY_NOT_FOUND');
                assert.equal(result.components.ui.status, 'ready');
              }
              if (!invalidUserData) assert.equal(messages.some((message) => message.type === 'stopped'), true);
              else assert.match(result.error, /entry/);
            }
            assert.equal(messages.some((message) => 'memory_profile_token' in message || 'cookie' in message), false);
            if (!invalidUserData) {
              const diagnostics = fs.readFileSync(path.join(work, scenario, 'product24-startup.jsonl'), 'utf8');
              assert.equal(diagnostics.includes('"phase":"entry"'), true);
              if (!invalidPython && !navigatorMissing) assert.equal(diagnostics.includes('"phase":"suite-ready"'), true);
            }
          } finally {
            clearTimeout(timer);
            if (desktop.exitCode === null && desktop.signalCode === null && desktop.connected) {
              desktop.send({ protocol: PROTOCOL, type: 'shutdown', request_id: 'test-cleanup' });
              await exit;
            }
          }
        }
      } finally {
        fs.rmSync(work, { recursive: true, force: true });
      }
    }
    const page = await desktop.firstWindow();
    await require('@playwright/test').expect.poll(
      () => page.evaluate(async () => (await window.psicatBrowser.getState()).syncBackend.status),
    ).toMatch(/^(ready|failed)$/);
    const state = await page.evaluate(() => window.psicatBrowser.getState());
    assert.equal(state.syncBackend.status, 'ready', state.syncBackend.error);
    assert.equal(state.psiCatSidecar.status, 'disabled');
    assert.equal(state.syncBackend.baseUrl, 'http://127.0.0.1:8787');
    assert.equal(await desktop.evaluate(({ app }) => app.getPath('userData')), path.join(work, 'user data'));
    const health = await fetch(`${state.syncBackend.baseUrl}/api/sync/health`).then((response) => response.json());
    assert.equal(health.ok, true);
    assert.equal(typeof health.instance_id, 'string');
    const protections = await desktop.evaluate(({ BrowserWindow }) => {
      const window = BrowserWindow.getAllWindows()[0];
      const view = window.getBrowserViews()[0];
      return {
        ui: window.webContents.getLastWebPreferences(),
        page: view.webContents.getLastWebPreferences(),
      };
    });
    assert.equal(protections.ui.contextIsolation, true);
    assert.equal(protections.page.nodeIntegration, false);
    assert.equal(protections.page.contextIsolation, true);
    assert.equal(protections.page.preload, undefined);
    await assert.rejects(page.evaluate(() => window.psicatBrowser.openExternal('ms-settings:privacy')), /HTTP\(S\)/);
    const pid = state.syncBackend.pid;
    await desktop.close();
    desktop = null;
    assert.throws(() => process.kill(pid, 0), { code: 'ESRCH' });
    await assert.rejects(fetch(`${state.syncBackend.baseUrl}/api/sync/health`, { signal: AbortSignal.timeout(500) }));
    await verifySuiteIpc();
  } finally {
    if (desktop) await desktop.close();
    fs.rmSync(work, { recursive: true, force: true });
  }
});
