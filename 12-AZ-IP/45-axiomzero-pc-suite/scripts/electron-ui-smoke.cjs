const assert = require("node:assert/strict");

const port = Number(process.env.P45_SMOKE_PORT);
if (!Number.isInteger(port) || port < 1 || port > 65535) {
  throw new Error("P45_SMOKE_PORT must be a valid TCP port.");
}

async function waitForPage() {
  const endpoint = `http://127.0.0.1:${port}/json/list`;
  let lastError;
  for (let attempt = 0; attempt < 360; attempt += 1) {
    try {
      const response = await fetch(endpoint);
      if (response.ok) {
        const targets = await response.json();
        const page = targets.find((target) =>
          target.type === "page" &&
          target.url.endsWith("/index.html") &&
          target.webSocketDebuggerUrl
        );
        if (page) return page;
      }
    } catch (error) {
      lastError = error;
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error(`The Product 45 window did not become available: ${lastError?.message || "timeout"}`);
}

async function verifyWindow(target) {
  const socket = new WebSocket(target.webSocketDebuggerUrl);
  const pending = new Map();
  const exceptions = [];
  let nextId = 0;

  socket.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    if (message.method === "Runtime.exceptionThrown") {
      exceptions.push(message.params.exceptionDetails.text);
    }
    if (message.id !== undefined && pending.has(message.id)) {
      const { resolve, reject, timer } = pending.get(message.id);
      pending.delete(message.id);
      clearTimeout(timer);
      if (message.error) reject(new Error(message.error.message));
      else resolve(message.result);
    }
  });
  await new Promise((resolve, reject) => {
    socket.addEventListener("open", resolve, { once: true });
    socket.addEventListener("error", reject, { once: true });
  });

  function send(method, params = {}) {
    const id = ++nextId;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        pending.delete(id);
        reject(new Error(`DevTools request timed out: ${method}`));
      }, params.awaitPromise ? 60000 : 5000);
      pending.set(id, { resolve, reject, timer });
      socket.send(JSON.stringify({ id, method, params }));
    });
  }

  try {
    await send("Runtime.enable");
    let rendered;
    const renderDeadline = Date.now() + 60000;
    while (Date.now() < renderDeadline) {
      const response = await send("Runtime.evaluate", {
        expression: `({
          title: document.title,
          body: document.body.innerText,
          cards: document.querySelectorAll("#product-list .product-card").length,
          runtimes: document.querySelectorAll("#runtime-list .product-card").length,
          jaxInstallDisabled: document.querySelector('[data-runtime-action="install"][data-id="36"]')?.disabled,
          browserInstallDisabled: document.querySelector('[data-runtime-action="install"][data-id="24"]')?.disabled,
          posixInstallDisabled: document.querySelector('[data-runtime-action="install"][data-id="26"]')?.disabled
        })`,
        returnByValue: true
      });
      rendered = response.result.value;
      if (rendered?.cards === 45 && rendered.runtimes === 45) break;
      await new Promise((resolve) => setTimeout(resolve, 250));
    }
    assert.equal(rendered.title, "AxiomZero PC Suite");
    assert.equal(rendered.cards, 45, "all catalog entries should render");
    assert.equal(rendered.runtimes, 45, "all actual runtime contracts should render");
    assert.equal(rendered.jaxInstallDisabled, false, "the CPU JAX installer must be available");
    assert.equal(rendered.browserInstallDisabled, false, "the Windows browser installer must be available");
    assert.equal(rendered.posixInstallDisabled, true, "unsupported POSIX installation must remain blocked");
    for (const text of ["Ask PsiCat", "Local evidence library", "Search locally", "Open PsiCat Navigator", "Research control plane", "PC readiness assessment", "PsiCat native model", "Portfolio runtime manager"]) {
      assert.ok(rendered.body.includes(text), `the window should render "${text}"`);
    }
    const created = await send("Runtime.evaluate", {
      expression: `(async () => {
        document.querySelector("#harness-goal").value = "Smoke test offline memory";
        document.querySelector("#harness-form").requestSubmit();
        for (let i = 0; i < 100; i++) {
          const state = await window.axiomSuite.getHarness();
          const run = state.runs.at(-1);
          if (run?.goal === "Smoke test offline memory" && document.querySelector("#harness-detail h3")?.textContent === run.goal) {
            return {
              id: run.id, status: run.status, label: run.epistemicLabel,
              steps: run.steps.map(step => step.tool),
              controls: [...document.querySelectorAll("[data-harness-action]")].map(button => button.dataset.harnessAction)
            };
          }
          await new Promise(resolve => setTimeout(resolve, 50));
        }
        throw new Error("The research plan did not render.");
      })()`,
      returnByValue: true, awaitPromise: true
    });
    assert.equal(created.result.value?.status, "pending");
    assert.equal(created.result.value.label, "UNVERIFIED");
    assert.deepEqual(created.result.value.steps, ["catalog.search", "evidence.search", "report.compose"]);
    assert.deepEqual(created.result.value.controls, ["run", "pause", "cancel", "export", "remove"]);
    const cancelled = await send("Runtime.evaluate", {
      expression: `(async () => {
        document.querySelector('[data-harness-action="cancel"]').click();
        for (let i = 0; i < 100; i++) {
          const state = await window.axiomSuite.getHarness();
          const run = state.runs.find(run => run.id === ${JSON.stringify(created.result.value.id)});
          if (run?.status === "cancelled") return {
            status: run.status, attempts: run.attempts,
            outputs: run.steps.map(step => step.output),
            event: state.events.at(-1).action
          };
          await new Promise(resolve => setTimeout(resolve, 50));
        }
        throw new Error("The research task did not cancel.");
      })()`,
      returnByValue: true, awaitPromise: true
    });
    assert.equal(cancelled.result.value?.status, "cancelled");
    assert.equal(cancelled.result.value.attempts, 0);
    assert.deepEqual(cancelled.result.value.outputs, [null, null, null]);
    assert.equal(cancelled.result.value.event, "cancelled");
    const diagnostics = await send("Runtime.evaluate", {
      expression: `({
        available: typeof window.axiomSuite.detectHardware === "function",
        exportAvailable: typeof window.axiomSuite.exportHardware === "function",
        initialExportDisabled: document.querySelector("#hardware-export").disabled,
        initialResultHidden: document.querySelector("#hardware-result").hidden
      })`,
      returnByValue: true
    });
    assert.deepEqual(diagnostics.result.value, {
      available: true, exportAvailable: true, initialExportDisabled: true, initialResultHidden: true
    });
    const instruction = await send("Runtime.evaluate", {
      expression: `({
        ask: typeof window.axiomSuite.askInstructionModel === "function",
        cancel: typeof window.axiomSuite.cancelInstructionModel === "function",
        status: typeof window.axiomSuite.getInstructionModel === "function",
        export: typeof window.axiomSuite.exportInstructionAnswer === "function",
        cancelDisabled: document.querySelector("#instruction-cancel").disabled,
        defaultBackend: document.querySelector("#harness-model").value,
        output: document.querySelector("#instruction-output").textContent
      })`, returnByValue: true
    });
    assert.deepEqual(instruction.result.value, {
      ask: true, cancel: true, status: true, export: true, cancelDisabled: true,
      defaultBackend: "psicat:embedded", output: ""
    });
    const platforms = await send("Runtime.evaluate", {
      expression: `(async () => {
        await runPlatformAction("refresh");
        return {
          cards: document.querySelectorAll("#platform-list .product-card").length,
          downloads: document.querySelector("#platform-network").checked,
          device: document.querySelector("#platform-device").value,
          distro: document.querySelector("#platform-distro").value,
          message: document.querySelector("#platform-message").textContent
        };
      })()`, returnByValue: true, awaitPromise: true
    });
    assert.equal(platforms.result.value.cards, 4);
    assert.equal(platforms.result.value.downloads, false);
    assert.equal(platforms.result.value.device, "");
    assert.equal(platforms.result.value.distro, "");
    assert.match(platforms.result.value.message, /not hardware-execution certification/);
    const native = await send("Runtime.evaluate", {
      expression: `(async () => {
        const state = await window.axiomSuite.getNativeModel();
        return {
          status: state.status, context: state.contextLength,
          verified: state.productionAssistantVerified,
          runtimes: (await window.axiomSuite.listRuntimes()).length
        };
      })()`,
      returnByValue: true, awaitPromise: true
    });
    assert.deepEqual(native.result.value, { status: "ready", context: 64, verified: false, runtimes: 45 });
    assert.deepEqual(exceptions, [], "the renderer should not throw JavaScript exceptions");
  } finally {
    try {
      await send("Browser.close");
    } catch {}
    socket.close();
  }
}

waitForPage()
  .then(verifyWindow)
  .then(() => console.log("Product 45 rendered 45 products/runtime contracts, reached its native model and created/cancelled a checkpointed research task without renderer exceptions."))
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
