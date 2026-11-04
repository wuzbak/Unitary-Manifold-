const PROTOCOL = 'psicat-browser-lifecycle-v1';

function attachSuiteLifecycle({ processImpl = process, enabled = false, onShutdown }) {
  if (!enabled) return { enabled: false, notify: async () => false };
  if (typeof processImpl.send !== 'function' || !processImpl.connected) {
    throw new Error('PSICAT_BROWSER_SUITE_IPC=1 requires an inherited Node IPC channel.');
  }
  let requestId = null;
  processImpl.on('message', (message) => {
    if (message?.protocol !== PROTOCOL || message.type !== 'shutdown'
      || typeof message.request_id !== 'string' || !/^[a-zA-Z0-9-]{1,80}$/.test(message.request_id)) return;
    requestId ||= message.request_id;
    onShutdown();
  });
  processImpl.on('disconnect', onShutdown);
  return {
    enabled: true,
    notify: (type, { error, sync, navigator } = {}) => new Promise((resolve) => {
      if (!processImpl.connected) return resolve(false);
      const publicState = (state) => state && ({
        status: state.status, pid: state.pid, baseUrl: state.baseUrl, error: state.error,
      });
      const message = {
        protocol: PROTOCOL, type, product_id: 24, request_id: requestId,
        ...(error ? { error: String(error) } : {}),
        ...(sync ? { sync: publicState(sync) } : {}),
        ...(navigator ? { navigator: publicState(navigator) } : {}),
      };
      try {
        processImpl.send(message, (sendError) => resolve(!sendError));
      } catch (_error) {
        resolve(false);
      }
    }),
  };
}

module.exports = { attachSuiteLifecycle, PROTOCOL };
