const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

test("Windows UI smoke quotes and verifies its user-data path", () => {
  const script = fs.readFileSync(path.join(__dirname, "../scripts/windows-smoke.ps1"), "utf8");
  assert.match(script, /\$userData = Join-Path \$suiteDirectory "build\\p45 smoke-/);
  assert.match(script, /\$arguments = @\("--remote-debugging-port=\$port", \('--user-data-dir="\{0\}"' -f \$userData\)\)/);
  assert.match(script, /Test-Path -LiteralPath \$userData -PathType Container/);
});

test("Windows qualification installs the real local companion model and rejects missing or tampered parts", () => {
  const script = fs.readFileSync(path.join(__dirname, "../scripts/windows-smoke.ps1"), "utf8");
  assert.match(script, /Assert-InstallerRejected "missing"/);
  assert.match(script, /Assert-InstallerRejected "tampered"/);
  assert.match(script, /instruction_smoke\.cjs"\) \(Join-Path \$installDirectory "resources\\psicat-instruction"\)/);
  assert.doesNotMatch(script, /\$portable|win-unpacked/);
});
test("the complete Windows artifact kit and tagged release retain every companion asset", () => {
  const workflow = fs.readFileSync(path.join(__dirname, "../../../.github/workflows/pc-suite-windows.yml"), "utf8");
  assert.match(workflow, /name: axiomzero-pc-suite-windows/);
  for (const asset of ["dist/*.exe", "dist/*-offline.json", "dist/*-model.part*", "dist/SHA256SUMS.txt"]) {
    assert.ok(workflow.includes(asset), `missing installer kit asset ${asset}`);
  }
  assert.match(workflow, /if: startsWith\(github.ref, 'refs\/tags\/pc-suite-v'\)/);
  assert.match(workflow, /Release checksums do not cover every asset/);
  const nsis = fs.readFileSync(path.join(__dirname, "../scripts/offline-installer.nsh"), "utf8");
  assert.match(nsis, /complete offline installer kit is required, not just this EXE/);
  assert.match(nsis, /Extract the entire axiomzero-pc-suite-windows artifact ZIP/);
});

test("UI diagnostics retain bounded time for awaited installed-resource verification", () => {
  const script = fs.readFileSync(path.join(__dirname, "../scripts/electron-ui-smoke.cjs"), "utf8");
  assert.match(script, /params\.awaitPromise \? 60000 : 5000/);
  assert.match(script, /getNativeModel\(\)/);
  assert.match(script, /listRuntimes\(\)/);
  assert.match(script, /assert\.deepEqual\(exceptions, \[\]/);
});

test("native qualification requires consecutive fresh-process passes without retrying failures", () => {
  const workflow = fs.readFileSync(path.join(__dirname, "../../../.github/workflows/pc-suite-embedded-model.yml"), "utf8");
  assert.match(workflow, /foreach \(\$trial in 1\.\.3\) \{/);
  assert.match(workflow, /node 12-AZ-IP\/45-axiomzero-pc-suite\/scripts\/instruction_smoke\.cjs/);
  assert.match(workflow, /if \(\$LASTEXITCODE -ne 0\) \{ throw "Actual governed Node instruction runtime failed on trial \$trial\." \}/);
});

test("UI smoke waits for runtime contracts even after catalog cards have rendered", async () => {
  const script = fs.readFileSync(path.join(__dirname, "../scripts/electron-ui-smoke.cjs"), "utf8");
  let catalogPolls = 0;
  let finish;
  let fail;
  const completed = new Promise((resolve, reject) => { finish = resolve; fail = reject; });
  class DiagnosticSocket {
    addEventListener(event, listener) {
      if (event === "open") queueMicrotask(listener);
      if (event === "message") this.receive = listener;
    }
    send(raw) {
      const { id, method, params } = JSON.parse(raw);
      let value;
      const expression = params?.expression || "";
      if (method === "Runtime.evaluate") {
        if (expression.includes("title: document.title")) {
          catalogPolls += 1;
          value = {
            title: "AxiomZero PC Suite", cards: 46, runtimes: catalogPolls === 1 ? 0 : 45,
            jaxInstallDisabled: false, browserInstallDisabled: false, posixInstallDisabled: true,
            body: ["Ask PsiCat", "Local evidence library", "Search locally", "Open PsiCat Navigator",
              "Research control plane", "PC readiness assessment", "PsiCat native model",
              "Portfolio runtime manager"].join("\n")
          };
        } else if (expression.includes('document.querySelector("#harness-goal")')) {
          value = {
            id: "smoke-run", status: "pending", label: "UNVERIFIED",
            steps: ["catalog.search", "evidence.search", "report.compose"],
            controls: ["run", "pause", "cancel", "export", "remove"]
          };
        } else if (expression.includes('[data-harness-action="cancel"]')) {
          value = { status: "cancelled", attempts: 0, outputs: [null, null, null], event: "cancelled" };
        } else if (expression.includes("detectHardware")) {
          value = { available: true, exportAvailable: true, initialExportDisabled: true, initialResultHidden: true };
        } else if (expression.includes("askInstructionModel")) {
          value = { ask: true, cancel: true, status: true, export: true, cancelDisabled: true,
            defaultBackend: "psicat:embedded", modelDiscovery: true, discoveryEnabled: true,
            initialChoices: ["psicat:embedded"], discoveryMessage: "", output: "" };
        } else if (expression.includes("runPlatformAction")) {
          value = { cards: 4, downloads: false, device: "", distro: "",
            message: "not hardware-execution certification" };
        } else if (expression.includes("getNativeModel")) {
          value = { status: "ready", context: 64, verified: false, runtimes: 45 };
        } else {
          throw new Error("Unexpected UI smoke evaluation");
        }
      }
      queueMicrotask(() => this.receive({ data: JSON.stringify({ id, result: { result: { value } } }) }));
    }
    close() {}
  }
  vm.runInNewContext(script, {
    require, process: { env: { P45_SMOKE_PORT: "12345" } }, WebSocket: DiagnosticSocket,
    fetch: async () => ({ ok: true, json: async () => [{
      type: "page", url: "file:///index.html", webSocketDebuggerUrl: "ws://127.0.0.1:12345/page"
    }] }),
    console: { log: finish, error: fail },
    setTimeout: (callback, delay) => setTimeout(callback, delay === 250 ? 0 : delay),
    clearTimeout
  });
  await completed;
  assert.equal(catalogPolls, 2, "catalog-only readiness must not end the runtime render poll");
});
