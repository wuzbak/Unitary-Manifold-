const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const vm = require("node:vm");
const { createRequire } = require("node:module");
const { EventEmitter } = require("node:events");

async function desktop(t, { corrupt = false } = {}) {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "p45-main-"));
  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
  if (corrupt) fs.writeFileSync(path.join(directory, "research-harness.json"), "{broken");
  const handlers = new Map();
  const approvals = [];
  const errors = [];
  const app = new EventEmitter();
  let window;
  app.requestSingleInstanceLock = () => true;
  app.whenReady = () => Promise.resolve();
  app.getPath = () => directory;
  app.getVersion = () => "0.1.0";
  app.getGPUInfo = async () => ({ gpuDevice: [{ vendorId: 4318, deviceId: 1234 }] });
  app.quit = () => { app.emit("before-quit"); };
  class BrowserWindow {
    constructor(options) {
      this.options = options;
      this.webContents = new EventEmitter();
      this.webContents.setWindowOpenHandler = () => {};
      window = this;
    }
    loadFile(file) { this.file = file; }
    static getAllWindows() { return window ? [window] : []; }
  }
  const dialog = {
    response: 0,
    showMessageBox: async (_window, request) => {
      approvals.push(request);
      return { response: dialog.response };
    },
    showSaveDialog: async () => ({ canceled: false, filePath: path.join(directory, "export.json") }),
    showErrorBox: (title, message) => errors.push({ title, message })
  };
  const file = path.join(__dirname, "..", "main.cjs");
  const localRequire = createRequire(file);
  vm.runInNewContext(fs.readFileSync(file, "utf8"), {
    require: (name) => name === "electron" ? {
      app, BrowserWindow, dialog,
      ipcMain: { handle: (channel, handler) => handlers.set(channel, handler) },
      shell: {}
    } : name === "./lib/local-model.cjs" ? {
      reasonLocally: async () => "UNVERIFIED mocked local model response"
    } : localRequire(name),
    __dirname: path.dirname(file), process
  }, { filename: file });
  await new Promise((resolve) => setImmediate(resolve));
  const invoke = (channel, ...args) => handlers.get(channel)(null, ...args);
  return { directory, window, errors, dialog, approvals, invoke, handlers, app };
}

test("desktop starts and wires real harness IPC, native approvals and evidence worker", async (t) => {
  const { window, errors, dialog, approvals, invoke, directory } = await desktop(t);
  assert.deepEqual(errors, []);
  assert.equal(window.options.webPreferences.contextIsolation, true);
  assert.equal(window.options.webPreferences.sandbox, true);
  assert.match(window.file, /index.html$/);
  const run = invoke("harness:create", { goal: "PsiCat offline memory" });
  let state = await invoke("harness:run-step", run.id);
  assert.equal(state.runs[0].attempts, 0);
  assert.equal(approvals[0].defaultId, 0);
  assert.deepEqual(Array.from(approvals[0].buttons), ["Cancel", "Approve this step"]);
  dialog.response = 1;
  for (let step = 0; step < 3; step++) state = await invoke("harness:run-step", run.id);
  assert.equal(state.runs[0].status, "completed");
  assert.match(state.runs[0].steps[0].output, /Product 20/);
  assert.match(state.runs[0].steps[1].output, /No imported evidence/);
  assert.match(state.runs[0].steps[2].output, /UNVERIFIED/);
  assert.equal(approvals.length, 4);
  await invoke("harness:export", run.id);
  assert.equal(JSON.parse(fs.readFileSync(path.join(directory, "export.json"), "utf8")).run.id, run.id);
  await invoke("harness:remove", run.id);
  assert.equal(invoke("harness:state").runs.length, 0);
});

test("optional reasoning is a separate disclosed native approval, never an automatic cloud action", async (t) => {
  const { dialog, invoke, approvals } = await desktop(t);
  dialog.response = 1;
  const run = invoke("harness:create", { goal: "PsiCat memory", model: "llama3.2:3b" });
  for (let step = 0; step < 3; step++) await invoke("harness:run-step", run.id);
  assert.equal(invoke("harness:state").runs[0].steps[3].status, "pending");
  await invoke("harness:run-step", run.id);
  assert.match(approvals[3].detail, /127.0.0.1:11434/);
  assert.match(approvals[3].detail, /retention/);
  assert.equal(invoke("harness:state").runs[0].status, "completed");
});

test("invalid checkpoint produces an explicit startup error instead of silent reset", async (t) => {
  const { window, errors, handlers } = await desktop(t, { corrupt: true });
  assert.equal(window, undefined);
  assert.equal(handlers.size, 0);
  assert.equal(errors.length, 1);
  assert.equal(errors[0].title, "AxiomZero PC Suite could not start");
});

test("hardware diagnostics require native consent and export only after detection", async (t) => {
  const { invoke, dialog, approvals, directory } = await desktop(t);
  await assert.rejects(invoke("hardware:export"), /Detect hardware/);
  assert.equal((await invoke("hardware:detect")).canceled, true);
  dialog.response = 1;
  const result = await invoke("hardware:detect");
  assert.equal(result.canceled, false);
  assert.equal(result.report.assessment.modelSelected, false);
  assert.equal(approvals.at(-1).defaultId, 0);
  assert.equal(approvals.at(-1).title, "Detect local model hardware");
  await invoke("hardware:export");
  const exported = JSON.parse(fs.readFileSync(path.join(directory, "export.json"), "utf8"));
  assert.equal(exported.schema, "axiomzero-hardware-assessment-v1");
  assert.equal(exported.assessment.trainingReady, false);
});
test("runtime provisioning and service execution require separate native approvals", async (t) => {
  const { invoke, approvals } = await desktop(t);
  const entries = invoke("runtime:list");
  assert.equal(entries.length, 45);
  assert.equal((await invoke("runtime:python")).canceled, true);
  assert.equal((await invoke("runtime:install", "43")).canceled, true);
  assert.equal((await invoke("runtime:start", "43")).canceled, true);
  assert.match(approvals[0].detail, /third-party software/);
  assert.match(approvals[1].detail, /pip downloads and executes/);
  assert.match(approvals[2].detail, /local command execution is disabled/);
  assert.equal(approvals.every((approval) => approval.defaultId === 0), true);
  await assert.rejects(invoke("runtime:install", "../bad"), /not registered/);
});
