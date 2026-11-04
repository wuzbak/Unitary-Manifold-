const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const vm = require("node:vm");
const { createRequire } = require("node:module");
const { EventEmitter } = require("node:events");

async function desktop(t, { corrupt = false, runtimeAccess, runtimeStopAll, instructionAnswer, instructionStopAll, platformManager } = {}) {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "p45-main-"));
  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
  if (corrupt) fs.writeFileSync(path.join(directory, "research-harness.json"), "{broken");
  const handlers = new Map();
  const approvals = [];
  const errors = [];
  const clipboardWrites = [];
  const opened = [];
  const app = new EventEmitter();
  let window;
  app.requestSingleInstanceLock = () => true;
  app.whenReady = () => Promise.resolve();
  app.getPath = () => directory;
  app.getVersion = () => "0.1.0";
  app.getGPUInfo = async () => ({ gpuDevice: [{ vendorId: 4318, deviceId: 1234 }] });
  const quitEvents = [];
  app.quit = () => {
    const event = { prevented: false, preventDefault() { this.prevented = true; } };
    app.emit("before-quit", event);
    quitEvents.push(event);
  };
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
      clipboard: { writeText: (value) => clipboardWrites.push(value) },
      shell: { openExternal: async (value) => opened.push(value) }
    } : name === "./lib/local-model.cjs" ? {
      reasonLocally: async () => "UNVERIFIED mocked local model response"
    } : name === "./lib/instruction-model.cjs" ? {
      createInstructionModel: () => ({
        status: async () => ({ status: "available", productionAssistantVerified: false }),
        answer: instructionAnswer || (async () => ({ answer: "Catalog answer [C1]", epistemicLabel: "UNVERIFIED" })),
        cancel: async () => {},
        stopAll: instructionStopAll || (async () => {})
      })
    } : name === "./lib/platform-targets.cjs" && platformManager ? {
      createPlatformTargets: () => platformManager
    } : name === "./lib/runtime-manager.cjs" && (runtimeAccess || runtimeStopAll) ? {
      createRuntimeManager: (options) => ({
        ...localRequire(name).createRuntimeManager(options),
        ...(runtimeAccess ? { access: runtimeAccess } : {}),
        ...(runtimeStopAll ? { stopAll: runtimeStopAll } : {})
      })
    } : localRequire(name),
    __dirname: path.dirname(file), process, AbortController
  }, { filename: file });
  await new Promise((resolve) => setImmediate(resolve));
  const invoke = (channel, ...args) => handlers.get(channel)(null, ...args);
  return { directory, window, errors, dialog, approvals, invoke, handlers, app, clipboardWrites, opened, quitEvents };
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

test("embedded instruction inference requires native approval and supplies only bounded local evidence", async (t) => {
  const requests = [];
  const { invoke, dialog, approvals, directory } = await desktop(t, {
    instructionAnswer: async (request) => { requests.push(request); return { answer: "Local reference [C1]", epistemicLabel: "UNVERIFIED" }; }
  });
  assert.equal((await invoke("instruction:ask", "PsiCat offline")).canceled, true);
  assert.equal(requests.length, 0);
  assert.equal(approvals.at(-1).defaultId, 0);
  assert.match(approvals.at(-1).detail, /stay on this PC/);
  await assert.rejects(invoke("instruction:ask", "x".repeat(401)), /1-400/);
  await assert.rejects(invoke("instruction:export"), /Generate/);
  dialog.response = 1;
  const result = await invoke("instruction:ask", "PsiCat offline");
  assert.match(result.answer, /\[C1\]/);
  assert.equal(requests[0].evidence[0].id, "C1");
  assert.ok(requests[0].evidence[0].text.length <= 2400);
  assert.equal(requests[0].signal.aborted, false);
  await invoke("instruction:export");
  assert.equal(JSON.parse(fs.readFileSync(path.join(directory, "export.json"), "utf8")).question, "PsiCat offline");
});

test("suite quit aborts and awaits the owned instruction process", async (t) => {
  let finish;
  const pending = new Promise((resolve) => { finish = resolve; });
  const { app, quitEvents } = await desktop(t, { instructionStopAll: () => pending });
  app.quit();
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(quitEvents.length, 1);
  assert.equal(quitEvents[0].prevented, true);
  finish();
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(quitEvents.length, 2);
  assert.equal(quitEvents[1].prevented, false);
});

test("platform artifacts require native approval and build downloads default off", async (t) => {
  const calls = [];
  const target = { id: "android-sdam", name: "SDAM", notes: "Android APK" };
  const { invoke, dialog, approvals } = await desktop(t, { platformManager: {
    list: () => [target],
    close: async () => {},
    importBundled: async (id) => { calls.push(["bundled", id]); return { artifact: "SDAM.apk" }; },
    prepare: async (id, options) => { calls.push(["prepare", id, options.allowNetwork]); return { artifact: "SDAM.apk" }; },
    install: async (id, options) => { calls.push(["install", id, options.serial, options.apkPath]); return { status: "installed" }; }
  } });
  assert.equal((await invoke("platform:action", { action: "importBundled", id: target.id })).canceled, true);
  assert.equal(calls.length, 0);
  assert.equal(approvals.at(-1).defaultId, 0);
  await assert.rejects(invoke("platform:action", { action: "prepare", id: target.id, allowNetwork: "yes" }), /registered platform action/);
  dialog.response = 1;
  await invoke("platform:action", { action: "importBundled", id: target.id });
  assert.deepEqual(calls[0], ["bundled", target.id]);
  await invoke("platform:action", { action: "prepare", id: target.id });
  assert.equal(calls.at(-1)[2], false);
  assert.match(approvals.at(-1).detail, /not allowed; cached dependencies required/);
  await invoke("platform:action", { action: "prepare", id: target.id, allowNetwork: true });
  assert.equal(calls.at(-1)[2], true);
  assert.match(approvals.at(-1).detail, /explicitly allowed/);
  await invoke("platform:action", { action: "install", id: target.id, serial: "chosen-device", apkPath: "/untrusted.apk" });
  assert.equal(calls.at(-1)[2], "chosen-device");
  assert.match(calls.at(-1)[3], /platform-targets[/\\]artifacts[/\\]SDAM\.apk$/);
});

test("platform export verifies copied bytes before replacing the selected destination", async (t) => {
  const contents = Buffer.from("verified UEFI bytes");
  const receipt = {
    artifact: "kernel.efi", bytes: contents.length,
    sha256: require("node:crypto").createHash("sha256").update(contents).digest("hex")
  };
  const { invoke, dialog, directory } = await desktop(t, { platformManager: {
    list: () => [{ id: "uefi-az-kernel", name: "AZ Kernel", notes: "Export only" }],
    close: async () => {},
    importBundled: async () => receipt
  } });
  const artifactDirectory = path.join(directory, "platform-targets", "artifacts");
  fs.mkdirSync(artifactDirectory, { recursive: true });
  const source = path.join(artifactDirectory, receipt.artifact);
  fs.writeFileSync(source, contents);
  dialog.response = 1;
  await invoke("platform:action", { action: "importBundled", id: "uefi-az-kernel" });
  const destination = path.join(directory, "export.json");
  fs.writeFileSync(destination, "previous destination");
  fs.writeFileSync(source, "tampered artifact!");
  await assert.rejects(invoke("platform:action", { action: "export", id: "uefi-az-kernel" }), /changed after verification|grew after verification/);
  assert.equal(fs.readFileSync(destination, "utf8"), "previous destination");
  assert.equal(fs.readdirSync(directory).some((file) => file.startsWith(".platform-export-")), false);
  fs.writeFileSync(source, contents);
  assert.equal((await invoke("platform:action", { action: "export", id: "uefi-az-kernel" })).sha256, receipt.sha256);
  assert.deepEqual(fs.readFileSync(destination), contents);
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
test("the governed research plan routes embedded reasoning without Ollama or automatic approval", async (t) => {
  const { dialog, invoke, approvals } = await desktop(t);
  dialog.response = 1;
  const run = invoke("harness:create", { goal: "PsiCat memory", model: "psicat:embedded" });
  for (let step = 0; step < 4; step++) await invoke("harness:run-step", run.id);
  assert.match(approvals[3].detail, /bundled CPU Qwen/);
  assert.doesNotMatch(approvals[3].detail, /127.0.0.1:11434/);
  assert.equal(invoke("harness:state").runs[0].status, "completed");
  assert.match(invoke("harness:state").runs[0].steps[3].output, /Catalog answer/);
});

test("invalid checkpoint produces an explicit startup error instead of silent reset", async (t) => {
  const { window, errors, handlers } = await desktop(t, { corrupt: true });
  assert.equal(window, undefined);
  assert.equal(handlers.size, 0);
  assert.equal(errors.length, 1);
  assert.equal(errors[0].title, "AxiomZero PC Suite could not start");
});
test("suite quit waits for owned desktop cleanup and surfaces cleanup failures", async (t) => {
  let finish;
  const pending = new Promise((resolve) => { finish = resolve; });
  const { app, quitEvents } = await desktop(t, { runtimeStopAll: () => pending });
  app.quit();
  assert.equal(quitEvents.length, 1);
  assert.equal(quitEvents[0].prevented, true);
  finish();
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(quitEvents.length, 2);
  assert.equal(quitEvents[1].prevented, false);
  const failure = await desktop(t, { runtimeStopAll: async () => { throw new Error("Owned process remains alive"); } });
  failure.app.quit();
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(failure.quitEvents.length, 1);
  assert.equal(failure.quitEvents[0].prevented, true);
  assert.match(failure.errors[0].message, /Owned process remains alive/);
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
  assert.match(approvals[1].detail, /pip or npm downloads and executes/);
  assert.match(approvals[2].detail, /local command execution is disabled/);
  assert.equal(approvals.every((approval) => approval.defaultId === 0), true);
  assert.equal((await invoke("runtime:node")).canceled, true);
  assert.match(approvals.at(-1).detail, /nodejs.org/);
  await assert.rejects(invoke("runtime:install", "../bad"), /not registered/);
});
test("authenticated dashboard token copying requires native approval and never enters the URL", async (t) => {
  const token = "b".repeat(64);
  const { invoke, dialog, clipboardWrites, opened, approvals } = await desktop(t, {
    runtimeAccess: () => ({ token, endpoint: "http://127.0.0.1:8327" })
  });
  assert.equal((await invoke("runtime:open", "27")).canceled, true);
  assert.deepEqual(clipboardWrites, []);
  assert.deepEqual(opened, []);
  dialog.response = 1;
  await invoke("runtime:open", "27");
  assert.deepEqual(clipboardWrites, [token]);
  assert.deepEqual(opened, ["http://127.0.0.1:8327"]);
  assert.equal(approvals[0].defaultId, 0);
  assert.match(approvals[0].detail, /clipboard-reading/);
  assert.equal(approvals[0].detail.includes(token), false);
});
