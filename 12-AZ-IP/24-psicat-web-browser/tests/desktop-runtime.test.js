const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const { spawn } = require('node:child_process');
const { once } = require('node:events');
const { pythonCommand } = require('../desktop/lib/sidecar');
const { PROTOCOL } = require('../desktop/lib/suite-lifecycle');

test('real Electron UI starts its owned sync sidecar and cleans it up on quit', {
  skip: process.env.PSICAT_BROWSER_ELECTRON_TEST !== '1',
  timeout: 30_000,
}, async () => {
  const { _electron } = require('playwright');
  const root = path.resolve(__dirname, '..');
  const work = fs.mkdtempSync(path.join(root, '.desktop-test-'));
  const command = pythonCommand();
  const python = execFileSync(command.executable, [...command.args, '-c', 'import sys; print(sys.executable)'], { encoding: 'utf8' }).trim();
  let desktop;
  try {
    desktop = await _electron.launch({
      args: [...(process.platform === 'linux' && process.getuid?.() === 0 ? ['--no-sandbox'] : []), root],
      env: { ...process.env, PSICAT_BROWSER_PYTHON: python,
        PSICAT_BROWSER_USER_DATA: path.join(work, 'user data'),
        PSICAT_BROWSER_DISABLE_NAVIGATOR: '1',
      },
    });

    async function verifySuiteIpc() {
      const root = path.resolve(__dirname, '..');
      const work = fs.mkdtempSync(path.join(root, '.suite-ipc-test-'));
      const command = pythonCommand();
      const python = execFileSync(command.executable, [...command.args, '-c', 'import sys; print(sys.executable)'], { encoding: 'utf8' }).trim();
      try {
        for (const invalidPython of [false, true]) {
          const desktop = spawn(require('electron'), [
            ...(process.platform === 'linux' && process.getuid?.() === 0 ? ['--no-sandbox'] : []), root,
          ], {
            env: { ...process.env, PSICAT_BROWSER_SUITE_IPC: '1',
              PSICAT_BROWSER_PYTHON: invalidPython ? path.join(work, 'missing-python.exe') : python,
              PSICAT_BROWSER_USER_DATA: path.join(work, invalidPython ? 'failure' : 'success'),
              PSICAT_BROWSER_DISABLE_NAVIGATOR: '1',
            },
            stdio: ['ignore', 'ignore', 'pipe', 'ipc'], shell: false,
          });
          let stderr = '';
          desktop.stderr.on('data', (chunk) => { stderr += chunk; });
          const messages = [];
          const exit = once(desktop, 'exit');
          const lifecycle = new Promise((resolve, reject) => {
            desktop.on('error', reject);
            desktop.on('message', (message) => {
              messages.push(message);
              if (['ready', 'startup-failed'].includes(message.type)) resolve(message);
            });
            desktop.once('exit', () => reject(new Error(`Desktop exited before lifecycle result: ${stderr}`)));
          });
          let timer;
          try {
            const result = await Promise.race([
              lifecycle,
              new Promise((_resolve, reject) => { timer = setTimeout(() => reject(new Error(`IPC readiness timed out: ${stderr}`)), 15000); }),
            ]);
            clearTimeout(timer);
            assert.equal(result.protocol, PROTOCOL);
            assert.equal(result.type, invalidPython ? 'startup-failed' : 'ready', result.error);
            if (!invalidPython) {
              assert.equal(result.sync.status, 'ready');
              const health = await fetch(`${result.sync.baseUrl}/api/sync/health`).then((response) => response.json());
              assert.equal(health.ok, true);
              const pid = result.sync.pid;
              desktop.send({ protocol: PROTOCOL, type: 'shutdown', request_id: 'parent-stop-1' });
              await exit;
              assert.equal(messages.find((message) => message.type === 'stopped')?.request_id, 'parent-stop-1');
              assert.throws(() => process.kill(pid, 0), { code: 'ESRCH' });
              await assert.rejects(fetch(`${result.sync.baseUrl}/api/sync/health`, { signal: AbortSignal.timeout(500) }));
            } else {
              await exit;
              assert.equal(messages.some((message) => message.type === 'ready'), false);
              assert.equal(messages.some((message) => message.type === 'stopped'), true);
            }
            assert.equal(messages.some((message) => 'memory_profile_token' in message || 'cookie' in message), false);
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
