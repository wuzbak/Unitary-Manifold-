const diagnostics = require('../desktop/lib/startup-diagnostics').createStartupDiagnostics();
diagnostics.mark('ipc-probe-entry');
const { app, BrowserWindow } = require('electron');
const { attachSuiteLifecycle } = require('../desktop/lib/suite-lifecycle');
let lifecycle;
try {
  lifecycle = attachSuiteLifecycle({ enabled: true, onShutdown: () => app.quit() });
} catch (error) {
  diagnostics.failure(error).finally(() => app.exit(1));
}
if (lifecycle) {
  let exiting = false;
  app.on('before-quit', (event) => {
    if (exiting) return;
    event.preventDefault();
    exiting = true;
    lifecycle.notify('stopped').finally(() => app.quit());
  });
  app.whenReady().then(async () => {
    diagnostics.mark('ipc-probe-electron-ready');
    const window = new BrowserWindow({
      show: false, webPreferences: { sandbox: true, nodeIntegration: false, contextIsolation: true },
    });
    await window.loadURL('about:blank');
    await lifecycle.notify('ipc-probe-ready');
  }).catch(async (error) => {
    await diagnostics.failure(error);
    app.quit();
  });
}
