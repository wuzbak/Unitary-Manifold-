const test = require("node:test");
const assert = require("node:assert/strict");
const { EventEmitter } = require("node:events");
const { superviseDesktop, PROTOCOL } = require("../lib/desktop-runtime.cjs");

function fixture(options = {}) {
  const child = new EventEmitter();
  child.pid = 12345;
  child.send = (message, callback) => {
    callback();
    queueMicrotask(() => {
      child.emit("message", { protocol: PROTOCOL, product_id: 24, type: "stopped", request_id: message.request_id });
      child.emit("close", 0);
    });
  };
  const control = superviseDesktop(child, {
    readyDeadlineMs: 20, stopDeadlineMs: 20,
    terminateTree: async () => { throw new Error("Unexpected forced termination"); },
    ...options
  });
  return { child, control };
}
test("desktop readiness requires the owned protocol, actual sync readiness and navigator state", async () => {
  const { child, control } = fixture();
  child.emit("message", { protocol: "other", product_id: 24, type: "ready" });
  child.emit("message", { protocol: PROTOCOL, product_id: 24, type: "ready", sync: { status: "starting" } });
  child.emit("message", { protocol: PROTOCOL, product_id: 24, type: "ready", sync: { status: "ready" }, navigator: { status: "ready" } });
  await control.ready();
  assert.deepEqual(await control.stop(), { status: "stopped", forced: false });
});
test("desktop startup failure is explicit and still permits owned graceful cleanup", async () => {
  const { child, control } = fixture();
  child.emit("message", { protocol: PROTOCOL, product_id: 24, type: "startup-failed", error: "Port 8787 occupied" });
  await assert.rejects(control.ready(), /Port 8787 occupied/);
  await control.stop();
});
test("early native desktop exit reports the actual exit status instead of a blank failure", async () => {
  const { child, control } = fixture();
  const pending = control.ready();
  child.emit("close", 42, null);
  await assert.rejects(pending, /code 42, signal none/);
});
test("unresponsive graceful shutdown terminates only the owned tree and reports escalation", async () => {
  let terminated;
  const { child, control } = fixture({
    terminateTree: async (owned) => { terminated = owned.pid; owned.emit("close", 0); }
  });
  child.send = (_message, callback) => callback();
  const result = await control.stop();
  assert.equal(terminated, 12345);
  assert.equal(result.forced, true);
  assert.match(result.warning, /shutdown timed out/);
});
test("desktop cannot claim successful cleanup when its owned process remains alive", async () => {
  const { child, control } = fixture({ terminateTree: async () => {} });
  child.send = (_message, callback) => callback();
  await assert.rejects(control.stop(), /did not exit/);
});
test("a stop acknowledgement without process exit is not successful shutdown", async () => {
  const { child, control } = fixture({
    terminateTree: async (owned) => owned.emit("close", 0)
  });
  child.send = (message, callback) => {
    callback();
    child.emit("message", { protocol: PROTOCOL, product_id: 24, type: "stopped", request_id: message.request_id });
  };
  assert.equal((await control.stop()).forced, true);
});
