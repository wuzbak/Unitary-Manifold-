const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const PROTOCOL = "psicat-browser-lifecycle-v1";

function readStartupDiagnostics(directory, pid) {
  const filename = path.join(directory, "product24-startup.jsonl");
  if (!fs.existsSync(filename)) return "No Product 24 entry record was written; its bootstrap may not have loaded.";
  const relative = path.relative(fs.realpathSync(directory), fs.realpathSync(filename));
  if (relative === ".." || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) {
    throw new Error("Browser startup diagnostics escape the owned data directory.");
  }
  const fd = fs.openSync(filename, "r");
  let text;
  try {
    if (!fs.fstatSync(fd).isFile()) throw new Error("Browser startup diagnostics are not a regular file.");
    const buffer = Buffer.alloc(65537);
    let count = 0;
    while (count < buffer.length) {
      const received = fs.readSync(fd, buffer, count, buffer.length - count, count);
      if (!received) break;
      count += received;
    }
    if (count > 65536) throw new Error("Browser startup diagnostics exceed the 64 KiB limit.");
    text = new TextDecoder("utf-8", { fatal: true }).decode(buffer.subarray(0, count));
  } finally { fs.closeSync(fd); }
  const records = [];
  for (const line of text.split("\n").filter((value) => value.trim())) {
    const record = JSON.parse(line);
    if (!record || typeof record !== "object" || Array.isArray(record)) throw new Error("Browser startup diagnostic record is invalid.");
    if (record.pid !== pid) continue;
    const filtered = {};
    for (const key of ["protocol", "product_id", "type", "phase", "pid", "platform", "electron", "ipc_available", "connected"]) {
      const value = record[key];
      if (typeof value === "string") filtered[key] = value.slice(0, 160);
      else if (typeof value === "boolean" || (typeof value === "number" && Number.isFinite(value))) filtered[key] = value;
    }
    if (record.error && typeof record.error === "object") {
      filtered.error = {};
      for (const key of ["name", "code"]) {
        if (typeof record.error[key] === "string") filtered.error[key] = record.error[key].slice(0, 160);
      }
    }
    records.push(filtered);
  }
  return records.length ? JSON.stringify(records) : "No startup record matches the owned browser PID.";
}

function superviseDesktop(child, { readyDeadlineMs = 30000, stopDeadlineMs = 10000, terminateTree, startupDirectory }) {
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
  child.on("close", (code, signal) => {
    closed = true;
    if (!ready && !failure) {
      let boot = "";
      if (startupDirectory) {
        try { boot = readStartupDiagnostics(startupDirectory, child.pid); }
        catch (error) {
          const reason = error instanceof SyntaxError ? "invalid JSON" :
            error instanceof TypeError ? "invalid UTF-8" : "unreadable, unsafe or over the 64 KiB limit";
          boot = `Startup diagnostic read failed: ${reason}.`;
        }
      }
      failure = new Error(`Browser exited before readiness (code ${code}, signal ${signal || "none"}): ${diagnostics} ${boot}`);
    }
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

module.exports = { superviseDesktop, readStartupDiagnostics, PROTOCOL };
