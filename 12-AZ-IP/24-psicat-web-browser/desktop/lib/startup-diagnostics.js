const fs = require('node:fs');
const path = require('node:path');
const PROTOCOL = 'psicat-browser-lifecycle-v1';
const { safeFailureContext } = require('./component-diagnostics');

function createStartupDiagnostics({ processImpl = process, fsImpl = fs } = {}) {
  const directory = processImpl.env.PSICAT_BROWSER_USER_DATA;
  const paths = processImpl.platform === 'win32' ? path.win32 : path;
  const logPath = directory && paths.isAbsolute(directory)
    ? paths.join(directory, 'product24-startup.jsonl') : null;
  let phase = 'entry';
  const enabled = processImpl.env.PSICAT_BROWSER_SUITE_IPC === '1';
  const record = (type, extra = {}) => {
    const payload = {
      protocol: PROTOCOL, product_id: 24, type, phase, pid: processImpl.pid,
      platform: processImpl.platform, electron: processImpl.versions.electron || null,
      ipc_available: typeof processImpl.send === 'function', connected: processImpl.connected === true,
      ...extra,
    };
    if (enabled && logPath) {
      try {
        fsImpl.mkdirSync(directory, { recursive: true });
        fsImpl.appendFileSync(logPath, `${JSON.stringify(payload)}\n`, { encoding: 'utf8', mode: 0o600 });
      } catch (_error) {
        // IPC remains authoritative if the per-user diagnostic file is unavailable.
      }
    }
    try { processImpl.stderr.write(`[Product24] ${JSON.stringify(payload)}\n`); } catch (_error) {}
    return payload;
  };
  const send = (payload) => new Promise((resolve) => {
    if (!enabled || !processImpl.connected || typeof processImpl.send !== 'function') return resolve(false);
    let timer = setTimeout(() => resolve(false), 500);
    try {
      processImpl.send(payload, (error) => { clearTimeout(timer); resolve(!error); });
    } catch (_error) {
      clearTimeout(timer);
      resolve(false);
    }
  });
  return {
    mark(nextPhase) {
      phase = nextPhase;
      send(record('boot'));
    },
    failure(error, context) {
      // Unknown exception messages/stacks may contain credentials or page content.
      const name = typeof error?.name === 'string' && /^[A-Za-z]{1,40}$/.test(error.name) ? error.name : 'Error';
      const code = typeof error?.code === 'string' && /^[A-Z0-9_]{1,40}$/.test(error.code) ? error.code : null;
      const details = context ? safeFailureContext(context) : {};
      const failed = details.components?.[details.component];
      const summary = failed
        ? `; component=${details.component}, status=${failed.status}, code=${failed.failure_code}${failed.python_error ? `, python=${failed.python_error}` : ''}${failed.missing_module ? `, module=${failed.missing_module}` : ''}${failed.missing_resource ? `, resource=${failed.missing_resource}` : ''}${failed.exit_code !== undefined ? `, exit=${failed.exit_code}` : ''}`
        : '';
      return send(record('startup-failed', {
        error: `Product 24 failed during ${phase} (${name}${code ? `/${code}` : ''})${summary}; inspect the installed entry point and dependencies.`,
        ...details,
      }));
    },
  };
}

module.exports = { createStartupDiagnostics };
