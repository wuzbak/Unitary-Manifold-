const { spawn } = require('node:child_process');
const path = require('node:path');
const { pythonCommand } = require('../desktop/lib/sidecar');

const command = pythonCommand();
const child = spawn(command.executable, [
  ...command.args, '-m', 'http.server', '4173', '--bind', '127.0.0.1',
  '--directory', path.resolve(__dirname, '../desktop/ui'),
], { stdio: 'inherit', shell: false, detached: false, windowsHide: true });

child.on('error', (error) => {
  console.error(`UI test server could not start (${error.code || 'spawn error'}). Check PSICAT_BROWSER_PYTHON.`);
  process.exitCode = 1;
});
child.once('exit', (code) => { process.exitCode = code || 0; });
for (const signal of ['SIGTERM', 'SIGINT']) {
  process.on(signal, () => child.kill('SIGTERM'));
}
