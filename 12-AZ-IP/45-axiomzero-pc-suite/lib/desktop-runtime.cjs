const crypto = require("node:crypto");
const PROTOCOL = "psicat-browser-lifecycle-v1";

function superviseDesktop(child, { readyDeadlineMs = 30000, stopDeadlineMs = 10000, terminateTree }) {
  let ready = false;
  let closed = false;
  let acknowledged = false;
  let stopping;
  let failure;
  let diagnostics = "";
  const record = (chunk) => { diagnostics = (diagnostics + chunk.toString("utf8")).slice(-4000); };
  child.stdout?.on("data", record);
  child.stderr?.on("data", record);
  const listeners = new Set();
  const update = () => { for (const notify of listeners) notify(); };
  const requestId = crypto.randomUUID();
  child.on("message", (message) => {
    if (message?.protocol !== PROTOCOL || message.product_id !== 24) return;
    if (message.type === "ready" && message.sync?.status === "ready" &&
        ["ready", "disabled"].includes(message.navigator?.status)) ready = true;
    if (message.type === "stopped" && message.request_id === requestId) acknowledged = true;
    if (["startup-failed", "shutdown-failed"].includes(message.type)) {
      failure = new Error(`Browser ${message.type}: ${String(message.error || "No diagnostic").slice(0, 4000)}`);
    }
    update();
  });
  child.on("error", (error) => { failure = error; update(); });
  child.on("close", () => {
    closed = true;
    if (!ready) failure ||= new Error(`Browser exited before readiness: ${diagnostics}`);
    update();
  });
  function waitUntil(predicate, deadlineMs, label, failOnError = false) {
    return new Promise((resolve, reject) => {
      const check = () => {
        if (failOnError && failure) finish(failure);
        else if (predicate()) finish();
        else if (failOnError && closed) finish(new Error("Browser exited before desktop readiness."));
      };
      const timer = setTimeout(() => finish(new Error(label)), deadlineMs);
      function finish(error) {
        clearTimeout(timer);
        listeners.delete(check);
        if (error) reject(error); else resolve();
      }
      listeners.add(check);
      check();
    });
  }
  return {
    ready: () => waitUntil(() => ready && !closed, readyDeadlineMs, "Browser desktop readiness timed out.", true),
    stop: () => {
      if (stopping) return stopping;
      stopping = (async () => {
        if (closed) return { status: "stopped", forced: false };
        let sendError;
        try {
          child.send({ protocol: PROTOCOL, type: "shutdown", request_id: requestId }, (error) => {
            sendError = error;
          });
          await waitUntil(() => acknowledged && closed, stopDeadlineMs, "Browser graceful shutdown timed out.");
          return { status: "stopped", forced: false };
        } catch (error) {
          if (closed) throw sendError || failure || error;
          const reason = sendError || failure || error;
          // Windows termination must include this owned Electron child's Python descendants.
          await terminateTree(child);
          await waitUntil(() => closed, stopDeadlineMs, "Owned browser process did not exit after tree termination.");
          return { status: "stopped", forced: true, warning: reason.message };
        }
      })().finally(() => { stopping = null; });
      return stopping;
    }
  };
}

module.exports = { superviseDesktop, PROTOCOL };
