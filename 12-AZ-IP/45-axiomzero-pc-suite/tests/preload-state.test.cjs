const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { EventEmitter } = require("node:events");

test("runtime state updates expose a bounded subscribe/unsubscribe bridge, not raw IPC", () => {
  const ipcRenderer = new EventEmitter();
  let api;
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, "../preload.cjs"), "utf8"), {
    require: () => ({ ipcRenderer, contextBridge: { exposeInMainWorld: (_name, value) => { api = value; } } })
  });

  assert.equal(Object.isFrozen(api), true);
  assert.equal(api.ipcRenderer, undefined);
  assert.throws(() => api.onRuntimesChanged("not callable"), /must be a function/);
  let notifications = 0;
  const unsubscribe = api.onRuntimesChanged(() => { notifications++; });
  ipcRenderer.emit("runtime:changed");
  assert.equal(notifications, 1);
  unsubscribe();
  ipcRenderer.emit("runtime:changed");
  assert.equal(notifications, 1);
});

test("instruction preload exposes fixed channels, not executable, endpoint or API-key selection", async () => {
  const calls = [];
  let api;
  const ipcRenderer = { invoke: async (...args) => { calls.push(args); return { status: "test" }; } };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, "../preload.cjs"), "utf8"), {
    require: () => ({ ipcRenderer, contextBridge: { exposeInMainWorld: (_name, value) => { api = value; } } })
  });
  await api.getInstructionModel();
  await api.askInstructionModel("What works offline?");
  await api.cancelInstructionModel();
  await api.exportInstructionAnswer();
  assert.deepEqual(calls, [
    ["instruction:status"], ["instruction:ask", "What works offline?"],
    ["instruction:cancel"], ["instruction:export"]
  ]);
  assert.equal(api.spawn, undefined);
  assert.equal(api.request, undefined);
});
