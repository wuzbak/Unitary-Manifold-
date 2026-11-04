const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { PROTOCOL } = require('../desktop/lib/suite-lifecycle');

const root = path.resolve(__dirname, '..');
const executable = process.env.PSICAT_BROWSER_TEST_ELECTRON
  || path.join(root, 'node_modules', 'electron', 'dist', process.platform === 'win32' ? 'electron.exe' : 'electron');
if (!fs.existsSync(executable)) throw new Error('Installed Electron binary is required; this probe does not download dependencies.');
const work = fs.mkdtempSync(path.join(root, '.ipc-probe-'));
const env = { ...process.env, PSICAT_BROWSER_SUITE_IPC: '1', PSICAT_BROWSER_USER_DATA: work };
delete env.ELECTRON_RUN_AS_NODE;
const child = spawn(executable, [
  ...(process.platform === 'linux' && process.getuid?.() === 0 ? ['--no-sandbox'] : []),
  '--enable-logging=stderr', path.join(__dirname, 'electron-ipc-probe.js'),
], { cwd: root, env, stdio: ['ignore', 'pipe', 'pipe', 'ipc'], shell: false });
let stopped = false;
let ready = false;
let stderr = '';
child.stdout.on('data', (chunk) => process.stdout.write(chunk));
child.stderr.on('data', (chunk) => { stderr = `${stderr}${chunk}`.slice(-16000); });
const timeout = setTimeout(() => {
  console.error('Direct Electron IPC probe timed out (no Python children were started).');
  child.kill();
  process.exitCode = 1;
}, 15000);
child.on('message', (message) => {
  console.log(JSON.stringify(message));
  if (message.protocol !== PROTOCOL) return;
  if (message.type === 'ipc-probe-ready') {
    ready = true;
    child.send({ protocol: PROTOCOL, type: 'shutdown', request_id: 'ipc-probe-stop' });
  }
  if (message.type === 'stopped' && message.request_id === 'ipc-probe-stop') stopped = true;
});
child.once('error', (error) => { console.error(`IPC probe spawn error: ${error.code}`); process.exitCode = 1; });
child.once('close', (code, signal) => {
  clearTimeout(timeout);
  if (!ready || !stopped || code !== 0) {
    console.error(`IPC probe failed: code=${code}, signal=${signal}, ready=${ready}, stopped=${stopped}\n${stderr}`);
    const diagnosticFile = path.join(work, 'product24-startup.jsonl');
    if (fs.existsSync(diagnosticFile)) console.error(fs.readFileSync(diagnosticFile, 'utf8'));
    process.exitCode = 1;
  } else console.log('Direct Electron GUI inherited IPC probe passed (no Product 20/model build required).');
  fs.rmSync(work, { recursive: true, force: true });
});
