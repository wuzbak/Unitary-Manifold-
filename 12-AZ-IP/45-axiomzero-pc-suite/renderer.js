const search = document.querySelector("#search");
const list = document.querySelector("#product-list");
const message = document.querySelector("#message");
const status = document.querySelector("#repository-status");
const disconnect = document.querySelector("#disconnect-repository");
const knowledgeCollections = document.querySelector("#knowledge-collections");
const knowledgeResults = document.querySelector("#knowledge-results");
const knowledgeQuery = document.querySelector("#knowledge-query");
const knowledgeMessage = document.querySelector("#knowledge-message");
let products = [];
let repositoryConnected = false;
let knowledgeBusy = false;
let knowledgeCollectionTotal = 0;
let harnessState;
let selectedTaskId;
let harnessBusy = false;
let hardwareBusy = false;
let nativeBusy = false;
let runtimeBusy = false;
let instructionBusy = false;
let platformBusy = false;

function renderPlatformTargets(targets) {
  const list = document.querySelector("#platform-list");
  list.replaceChildren();
  for (const target of targets) {
    const card = document.createElement("article");
    card.className = "product-card";
    const heading = document.createElement("h3");
    heading.textContent = `Product ${target.productId} | ${target.name}`;
    const description = document.createElement("p");
    description.className = "muted";
    description.textContent = `${target.status}: ${target.notes}${target.gradleOfflineError ? ` Offline cache error: ${target.gradleOfflineError}` : ""}`;
    const controls = document.createElement("div");
    controls.className = "harness-controls";
    const actions = target.kind === "wsl2" ? [["provision", "Provision selected WSL distro"], ["run", "Start selected WSL runtime"], ["stop", "Stop owned WSL runtime"]]
      : [...(target.bundled ? [["importBundled", "Use bundled artifact (offline)"]] : []),
        ["prepare", "Build artifact"], ["export", "Export prepared artifact"],
        ...(target.kind === "android" ? [["install", "Install on selected Android device"]] : [])];
    for (const [action, label] of actions) {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.platformId = target.id;
      button.dataset.platformAction = action;
      button.textContent = label;
      button.dataset.unavailable = String(target.status === "blocked" && (action === "prepare" || !target.bundled));
      button.disabled = platformBusy || button.dataset.unavailable === "true";
      controls.append(button);
    }
    card.append(heading, description, controls);
    list.append(card);
  }
}

async function runPlatformAction(action, id) {
  if (platformBusy) return;
  platformBusy = true;
  const message = document.querySelector("#platform-message");
  document.querySelectorAll("[data-platform-action], #platform-refresh, #platform-devices, #platform-distros").forEach((button) => { button.disabled = true; });
  message.textContent = "Inspecting prerequisites or awaiting native approval; builds may take up to 15 minutes...";
  try {
    if (action === "refresh") renderPlatformTargets(await window.axiomSuite.listPlatformTargets());
    else if (action === "devices" || action === "distros") {
      const select = document.querySelector(action === "devices" ? "#platform-device" : "#platform-distro");
      const values = action === "devices"
        ? (await window.axiomSuite.listAndroidDevices()).filter((entry) => entry.state === "device").map((entry) => entry.serial)
        : await window.axiomSuite.listWslDistros();
      const placeholder = document.createElement("option");
      placeholder.value = "";
      placeholder.textContent = "Select explicitly";
      select.replaceChildren(placeholder);
      for (const value of values) {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = value;
        select.append(option);
      }
      message.textContent = values.length ? "Select one target explicitly before proceeding." : "No available targets found. Check the required tooling and authorization.";
      return;
    } else {
      const result = await window.axiomSuite.runPlatformAction({
        action, id, serial: document.querySelector("#platform-device").value,
        distro: document.querySelector("#platform-distro").value,
        allowNetwork: document.querySelector("#platform-network").checked
      });
      message.textContent = result.canceled ? "Operation cancelled; no platform action approved." : JSON.stringify(result, null, 2);
      return;
    }
    message.textContent = "Target contracts shown. A build or prerequisite check is not hardware-execution certification.";
  } catch (error) { message.textContent = `Platform operation failed: ${error.message}`; }
  finally {
    platformBusy = false;
    document.querySelectorAll("#platform-refresh, #platform-devices, #platform-distros").forEach((button) => { button.disabled = false; });
    document.querySelectorAll("[data-platform-action]").forEach((button) => {
      button.disabled = button.dataset.unavailable === "true";
    });
  }
}

async function runInstructionAction(action) {
  const message = document.querySelector("#instruction-message");
  if (action === "cancel") {
    try {
      await window.axiomSuite.cancelInstructionModel();
      message.textContent = "Cancellation requested; the owned model process is being stopped.";
    } catch (error) { message.textContent = `Model cleanup failed: ${error.message}`; }
    return;
  }
  if (instructionBusy) return;
  instructionBusy = true;
  document.querySelector("#instruction-ask").disabled = true;
  document.querySelector("#instruction-status").disabled = true;
  document.querySelector("#instruction-export").disabled = true;
  document.querySelector("#instruction-cancel").disabled = action !== "ask";
  message.textContent = action === "ask" ? "Awaiting native approval, then verifying and running the local CPU model. Baseline CPUs may take several minutes; cancellation remains available." : "Checking the bundled instruction backend...";
  try {
    const result = action === "ask"
      ? await window.axiomSuite.askInstructionModel(document.querySelector("#instruction-question").value)
      : action === "export" ? await window.axiomSuite.exportInstructionAnswer()
      : await window.axiomSuite.getInstructionModel();
    if (result.canceled) { message.textContent = "Operation cancelled."; return; }
    if (action === "export") { message.textContent = "Answer and supplied evidence exported locally, without encryption."; return; }
    if (action === "status") {
      document.querySelector("#instruction-output").textContent = JSON.stringify(result, null, 2);
      message.textContent = "Backend status shown. Readiness is not a verified expert-quality certificate.";
    } else {
      document.querySelector("#instruction-output").textContent = `${result.answer}\n\n${result.status} | References: ${result.citations.map((id) => `[${id}]`).join(", ") || "none"}`;
      document.querySelector("#instruction-sources").textContent = result.sources.map((source) => `[${source.id}]\n${source.text}`).join("\n\n");
      document.querySelector("#instruction-export").disabled = false;
      message.textContent = "UNVERIFIED local answer. Check the cited sources before acting; no tools were executed.";
    }
  } catch (error) {
    document.querySelector("#instruction-output").textContent = "";
    document.querySelector("#instruction-sources").textContent = "";
    message.textContent = `Local assistant failed: ${error.message}`;
  } finally {
    instructionBusy = false;
    document.querySelector("#instruction-ask").disabled = false;
    document.querySelector("#instruction-status").disabled = false;
    document.querySelector("#instruction-cancel").disabled = true;
  }
}

function renderRuntimes(entries) {
  const list = document.querySelector("#runtime-list");
  list.replaceChildren();
  for (const entry of entries) {
    const card = document.createElement("article");
    card.className = "product-card";
    const heading = document.createElement("h3");
    heading.textContent = `Product ${entry.id} | ${entry.kind}`;
    const status = document.createElement("p");
    status.className = "muted";
    status.textContent = entry.running ? "Running in this desktop session" : entry.receipt?.status === "installed"
      ? "Dependencies installed (not a full capability certification)"
      : entry.receipt?.status === "failed" ? `Installation failed: ${entry.receipt.error}` : "Not provisioned by this suite";
    const details = document.createElement("details");
    const summary = document.createElement("summary");
    summary.textContent = "Prerequisites and operational limits";
    const text = document.createElement("p");
    text.className = "muted";
    text.textContent = `${entry.prerequisites.join("; ")}. ${entry.limitation}`;
    details.append(summary, text);
    const actions = document.createElement("div");
    actions.className = "harness-controls";
    for (const [action, label, disabled] of [
      ["install", "Install dependencies", (entry.installMode !== "python-venv" && !["24", "27"].includes(entry.id)) || runtimeBusy || entry.running || entry.id === "26"],
      ["start", entry.managedDesktop ? "Open browser desktop" : "Start local service", (!entry.managedService && !entry.managedDesktop) || entry.running || runtimeBusy || entry.receipt?.status !== "installed"],
      ["stop", entry.managedDesktop ? "Close browser desktop" : "Stop service", !entry.running],
      ["open", "Open running dashboard", !entry.running || runtimeBusy || entry.managedDesktop]
    ]) {
      const button = document.createElement("button");
      button.type = "button"; button.dataset.runtimeAction = action; button.dataset.id = entry.id;
      button.textContent = label; button.disabled = disabled; actions.append(button);
    }
    card.append(heading, status, details, actions);
    list.append(card);
  }
}

async function runRuntimeAction(action, id) {
  const message = document.querySelector("#runtime-message");
  if (runtimeBusy && action !== "stop") return;
  if (action !== "stop") runtimeBusy = true;
  message.textContent = action === "refresh" ? "" : "Awaiting approval or executing the selected runtime operation...";
  document.querySelector("#runtime-python").disabled = runtimeBusy;
  document.querySelector("#runtime-node").disabled = runtimeBusy;
  try {
    let result;
    if (action === "python") result = await window.axiomSuite.installRuntimePython();
    else if (action === "node") result = await window.axiomSuite.installRuntimeNode();
    else if (action === "install") result = await window.axiomSuite.installRuntime(id);
    else if (action === "start") result = await window.axiomSuite.startRuntime(id);
    else if (action === "stop") result = await window.axiomSuite.stopRuntime(id);
    else if (action === "open") result = await window.axiomSuite.openRuntime(id);
    message.textContent = action === "refresh" ? "" : result?.canceled ? "Operation cancelled; no installation or launch was approved."
      : result?.forced ? `Owned browser tree was stopped after graceful cleanup failed: ${result.warning}`
      : "Operation finished. Inspect the per-product state and limits below.";
  } catch (error) { message.textContent = `Runtime operation failed: ${error.message}`; }
  finally {
    if (action !== "stop") runtimeBusy = false;
    document.querySelector("#runtime-python").disabled = runtimeBusy;
    document.querySelector("#runtime-node").disabled = runtimeBusy;
    try { renderRuntimes(await window.axiomSuite.listRuntimes()); }
    catch (error) { message.textContent = `Runtime state could not be read: ${error.message}`; }
  }
}

async function runNativeAction(action) {
  const message = document.querySelector("#native-message");
  if (action === "cancel") {
    try {
      await window.axiomSuite.cancelNativeModel();
      message.textContent = "Cancellation requested. A prior completed checkpoint is retained.";
    } catch (error) { message.textContent = error.message; }
    return;
  }
  if (nativeBusy) return;
  nativeBusy = true;
  document.querySelectorAll("#native-status, #native-train, #native-generate").forEach((button) => { button.disabled = true; });
  document.querySelector("#native-cancel").disabled = false;
  message.textContent = action === "train" ? "Awaiting corpus selection and native approval. Training may take up to ten minutes." : "Running the installed local model...";
  try {
    const result = await (action === "status" ? window.axiomSuite.getNativeModel()
      : action === "train" ? window.axiomSuite.trainNativeModel(500)
      : window.axiomSuite.generateNativeModel(document.querySelector("#native-prompt").value));
    if (result.canceled) { message.textContent = "Action cancelled."; return; }
    if (result.status === "blocked-vocabulary") {
      message.textContent = `The checkpoint cannot represent these prompt characters: ${result.unknownCharacters.join(" ")}`;
      return;
    }
    message.textContent = `${result.status}: own toroidal model. Output is UNVERIFIED; production assistant capability is not established.`;
    document.querySelector("#native-output").textContent = result.completion ?? JSON.stringify(result, null, 2);
  } catch (error) {
    message.textContent = `Native operation failed: ${error.message}`;
  } finally {
    nativeBusy = false;
    document.querySelectorAll("#native-status, #native-train, #native-generate").forEach((button) => { button.disabled = false; });
    document.querySelector("#native-cancel").disabled = true;
  }
}

function renderHardware(report) {
  const panel = document.querySelector("#hardware-result");
  panel.replaceChildren();
  panel.hidden = false;
  const lines = [
    `${report.platform} ${report.architecture} | ${report.cpuModel} | ${report.logicalCpuCount} logical CPUs`,
    `RAM: ${formatBytes(report.totalMemoryBytes)} total, ${formatBytes(report.availableMemoryBytes)} currently available`,
    `Free disk: ${formatBytes(report.freeDiskBytes)}. ${report.diskScope}`,
    `Measured: ${new Date(report.measuredAt).toLocaleString()}`,
    ...report.gpus.map((gpu) => `Graphics: ${gpu.device || "Unnamed device"} | vendor ${gpu.vendor || gpu.vendorId || "unknown"} | dedicated VRAM unverified`),
    `Assessment: ${report.assessment.status}. No model selected; training readiness not established.`,
    ...report.assessment.blockers,
    report.assessment.explanation,
    report.privacy
  ];
  for (const line of lines) {
    const item = document.createElement("p");
    item.textContent = line;
    panel.append(item);
  }
}

async function runHardwareAction(exporting = false) {
  if (hardwareBusy) return;
  hardwareBusy = true;
  const detect = document.querySelector("#hardware-detect");
  const save = document.querySelector("#hardware-export");
  const message = document.querySelector("#hardware-message");
  const hadReport = !document.querySelector("#hardware-result").hidden;
  detect.disabled = true;
  save.disabled = true;
  message.textContent = exporting ? "" : "Awaiting approval for local read-only hardware diagnostics...";
  let hasReport = hadReport;
  try {
    const result = await (exporting ? window.axiomSuite.exportHardware() : window.axiomSuite.detectHardware());
    if (result.canceled) message.textContent = "Action cancelled. No installation or download was performed.";
    else if (exporting) message.textContent = "Hardware assessment exported to your chosen file.";
    else {
      renderHardware(result.report);
      hasReport = true;
      message.textContent = "Assessment complete. Model selection remains gated on measured requirements and a license review.";
    }
  } catch (error) {
    message.textContent = `Hardware assessment failed: ${error.message}`;
  } finally {
    hardwareBusy = false;
    detect.disabled = false;
    save.disabled = !hasReport;
  }
}

function renderHarness(state) {
  harnessState = state;
  const tasks = document.querySelector("#harness-tasks");
  const detail = document.querySelector("#harness-detail");
  document.querySelector("#harness-count").textContent = `${state.runs.length} / ${state.policy.maxRuns} tasks`;
  document.querySelector("#harness-create").disabled = harnessBusy || state.runs.length >= state.policy.maxRuns;
  tasks.replaceChildren();
  if (!state.runs.some((run) => run.id === selectedTaskId)) selectedTaskId = state.runs.at(-1)?.id;
  for (const run of [...state.runs].reverse()) {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.taskId = run.id;
    button.setAttribute("aria-pressed", String(run.id === selectedTaskId));
    button.textContent = `${run.goal}\n${run.status} | ${run.steps.filter((step) => step.status === "completed").length}/${run.steps.length} steps`;
    tasks.append(button);
  }
  detail.replaceChildren();
  const run = state.runs.find((item) => item.id === selectedTaskId);
  if (!run) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "Create a task to review its plan, evidence, and audit trail.";
    detail.append(empty);
    return;
  }
  const heading = document.createElement("h3");
  heading.textContent = run.goal;
  const statusLine = document.createElement("p");
  statusLine.className = "muted";
  statusLine.textContent = `${run.status.toUpperCase()} | UNVERIFIED | ${run.attempts}/6 attempts | ${run.model === "psicat:embedded" ? "Bundled PsiCat CPU" : run.model ? `Ollama: ${run.model}` : "Evidence only"} | ${new Date(run.updatedAt).toLocaleString()}`;
  const controls = document.createElement("div");
  controls.className = "harness-controls";
  const terminal = ["completed", "cancelled"].includes(run.status);
  for (const [action, label, disabled] of [
    ["run", run.status === "failed" ? "Review & retry next step" : "Review & run next step", harnessBusy || terminal || run.attempts >= 6],
    ["pause", "Pause", terminal || run.status === "paused"],
    ["cancel", "Cancel task", terminal],
    ["export", "Export checkpoint", harnessBusy],
    ["remove", "Remove checkpoint", harnessBusy || !terminal]
  ]) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.dataset.harnessAction = action;
    button.dataset.taskId = run.id;
    button.disabled = disabled;
    if (action === "run") button.className = "primary";
    controls.append(button);
  }
  const plan = document.createElement("ol");
  for (const step of run.steps) {
    const item = document.createElement("li");
    item.textContent = `${step.tool} - ${step.status}`;
    if (step.error) {
      const error = document.createElement("p");
      error.className = "harness-step-error";
      error.textContent = step.error;
      item.append(error);
    }
    if (step.output !== null) {
      const output = document.createElement("details");
      output.open = step.tool === "report.compose" || step.tool === "model.reason";
      const summary = document.createElement("summary");
      summary.textContent = step.tool === "model.reason" ? "Unverified local model response" : "Checkpointed result";
      const text = document.createElement("pre");
      text.textContent = step.output;
      output.append(summary, text);
      item.append(output);
    }
    plan.append(item);
  }
  const audit = document.createElement("details");
  const auditLabel = document.createElement("summary");
  auditLabel.textContent = "Audit trail (bounded, hash-linked; not tamper-proof)";
  const events = document.createElement("pre");
  events.textContent = state.events.filter((event) => event.runId === run.id).map((event) =>
    `${event.sequence} | ${event.at} | ${event.action}\n${event.detail}\nSHA-256: ${event.hash}`
  ).join("\n\n");
  audit.append(auditLabel, events);
  detail.append(heading, statusLine, controls, plan, audit);
}

async function runHarnessAction(action, id) {
  const text = document.querySelector("#harness-message");
  if (["pause", "cancel"].includes(action)) {
    try {
      renderHarness(await (action === "pause"
        ? window.axiomSuite.pauseHarnessTask(id)
        : window.axiomSuite.cancelHarnessTask(id)));
      text.textContent = action === "pause" ? "Task paused. A fresh approval is required to continue." : "Task cancelled. Completed checkpoints retained.";
    } catch (error) {
      text.textContent = error.message;
    }
    return;
  }
  if (harnessBusy) return;
  harnessBusy = true;
  if (harnessState) renderHarness(harnessState);
  text.textContent = action === "run" ? "Awaiting your native approval, then running one bounded step. Pause or cancel remains available." : "";
  try {
    if (action === "create") {
      const useModel = document.querySelector("#harness-use-model").checked;
      const run = await window.axiomSuite.createHarnessTask({
        goal: document.querySelector("#harness-goal").value,
        model: useModel ? document.querySelector("#harness-model").value : null
      });
      selectedTaskId = run.id;
      text.textContent = "Plan checkpointed. Review and approve the first step to begin.";
    } else if (action === "run") {
      renderHarness(await window.axiomSuite.runHarnessStep(id));
      const run = harnessState.runs.find((item) => item.id === id);
      text.textContent = `Task ${run.status}. Each remaining step requires a fresh approval.`;
    } else if (action === "remove") {
      renderHarness(await window.axiomSuite.removeHarnessTask(id));
    } else if (action === "export") {
      const result = await window.axiomSuite.exportHarnessTask(id);
      text.textContent = result.canceled ? "Export cancelled." : "Research checkpoint and bounded audit exported.";
    }
  } catch (error) {
    text.textContent = error.message || "Harness action failed.";
  } finally {
    harnessBusy = false;
    try {
      renderHarness(await window.axiomSuite.getHarness());
    } catch (error) {
      text.textContent = `Harness checkpoint could not be loaded: ${error.message}`;
    }
  }
}

function showMessage(text) {
  message.textContent = text;
}

function showKnowledgeMessage(text) {
  knowledgeMessage.textContent = text;
}

function escapeText(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[character]);
}

function canOpenSurface(endpoint) {
  return /^https?:\/\/(?:localhost|127\.0\.0\.1)(?::\d{1,5})?(?:\/[^\s]*)?$/i.test(endpoint);
}

function render() {
  const query = search.value.trim().toLocaleLowerCase();
  const matches = products.filter((product) =>
    `${product.id} ${product.name} ${product.version} ${product.trl} ${product.endpoint} ${product.description}`
      .toLocaleLowerCase()
      .includes(query)
  );
  document.querySelector("#product-count").textContent = String(products.length);
  list.replaceChildren();
  if (matches.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "No products match this search.";
    list.append(empty);
    return;
  }
  for (const product of matches) {
    const card = document.createElement("article");
    card.className = "product-card";
    card.innerHTML = `
      <div class="product-title">
        <span class="product-number">#${escapeText(product.id)}</span>
        <h3>${escapeText(product.name)}</h3>
      </div>
      <p class="meta">${escapeText(product.version)} · ${escapeText(product.trl)} · ${escapeText(product.endpoint)}</p>
      <p class="product-description">${escapeText(product.description)}</p>
      <div class="product-actions">
        <button data-action="folder" data-id="${escapeText(product.id)}" ${repositoryConnected ? "" : "disabled"}>Open folder</button>
        <button data-action="readme" data-id="${escapeText(product.id)}" ${repositoryConnected ? "" : "disabled"}>Read guide</button>
        ${canOpenSurface(product.endpoint) ? `<button data-action="surface" data-id="${escapeText(product.id)}">Open local service</button>` : ""}
      </div>`;
    list.append(card);
  }
}

async function runAction(action) {
  showMessage("");
  try {
    const state = await window.axiomSuite.getState();
    if (action.type === "connect") {
      const result = await window.axiomSuite.connectRepository();
      if (!result.canceled) {
        updateState({ ...state, repositoryRoot: result.repositoryRoot });
      }
    } else if (action.type === "disconnect") {
      updateState(await window.axiomSuite.disconnectRepository());
    } else if (action.type === "workspace") {
      await window.axiomSuite.openWorkspace();
    } else if (action.type === "folder") {
      await window.axiomSuite.openProductFolder(action.id);
    } else if (action.type === "readme") {
      await window.axiomSuite.openProductReadme(action.id);
    } else if (action.type === "surface") {
      await window.axiomSuite.openProductSurface(action.id);
    } else if (action.type === "psicat") {
      await window.axiomSuite.openPsiCat();
    } else if (action.type === "legal") {
      await window.axiomSuite.openLegalNotices();
    } else if (action.type === "category") {
      await window.axiomSuite.openIpCategory(action.category);
    }
  } catch (error) {
    showMessage(error.message || "The requested action failed.");
  }
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function renderKnowledgeCollections(collections) {
  knowledgeCollectionTotal = collections.length;
  document.querySelector("#knowledge-count").textContent =
    `${collections.length} collection${collections.length === 1 ? "" : "s"}`;
  knowledgeCollections.replaceChildren();
  for (const collection of collections) {
    const card = document.createElement("article");
    card.className = "knowledge-card";
    const name = document.createElement("h3");
    name.textContent = collection.name;
    const summary = document.createElement("p");
    summary.textContent =
      `${collection.sourceType === "zip" ? "ZIP archive" : "Folder"} · ` +
      `${collection.indexedTextFiles} text files indexed · ${collection.totalFiles} files considered · ` +
      `${formatBytes(collection.textBytes)} searchable text`;
    const skips = document.createElement("p");
    skips.className = "knowledge-skips";
    skips.textContent =
      `${collection.unsupportedFiles} unsupported · ${collection.oversizedFiles} over 8 MiB · ` +
      `${collection.textLimitFiles} over text limit · ${collection.unreadableFiles} unreadable · ` +
      `${collection.symlinksSkipped} links skipped · ` +
      `${collection.excludedDirectories} excluded directories`;
    if (collection.truncated) {
      skips.textContent += " · scan stopped at an entry or depth limit";
    }
    const importDetails = document.createElement("details");
    const detailsSummary = document.createElement("summary");
    detailsSummary.textContent =
      `Skipped-file details (${collection.skippedFiles.length + collection.omittedSkippedFiles} listed)`;
    importDetails.append(detailsSummary);
    if (collection.skippedFiles.length > 0) {
      const skippedList = document.createElement("ul");
      for (const skippedFile of collection.skippedFiles) {
        const item = document.createElement("li");
        const reason = skippedFile.status === "oversized"
          ? "over 8 MiB"
          : skippedFile.status === "text-limit"
            ? "collection text limit reached"
            : skippedFile.status === "unreadable"
              ? "unreadable"
              : skippedFile.status === "symlink"
                ? "link skipped"
                : "unsupported format or encoding";
        item.textContent = `${reason} · ${skippedFile.path} · ${formatBytes(skippedFile.sizeBytes)}`;
        skippedList.append(item);
      }
      importDetails.append(skippedList);
    } else {
      const noSkips = document.createElement("p");
      noSkips.textContent = "No skipped text files.";
      importDetails.append(noSkips);
    }
    if (collection.omittedSkippedFiles > 0) {
      const omitted = document.createElement("p");
      omitted.textContent = `${collection.omittedSkippedFiles} additional skipped files are not shown here.`;
      importDetails.append(omitted);
    }
    const actions = document.createElement("div");
    actions.className = "knowledge-card-actions";
    for (const [action, label] of [["refresh", "Refresh"], ["remove", "Remove index"]]) {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.action = action;
      button.dataset.id = collection.id;
      button.textContent = label;
      button.disabled = knowledgeBusy;
      actions.append(button);
    }
    card.append(name, summary, skips, importDetails, actions);
    knowledgeCollections.append(card);
  }
  const searchButton = document.querySelector("#knowledge-search-form button");
  searchButton.disabled = knowledgeBusy || collections.length === 0;
  if (collections.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "No local sources yet. Import the Webspace seed or PsiCat Mind ZIP to begin.";
    knowledgeCollections.append(empty);
  }
}

function renderKnowledgeResults(result) {
  knowledgeResults.replaceChildren();
  const heading = document.createElement("p");
  heading.className = "knowledge-result-count";
  heading.textContent = result.totalMatches === 0
    ? "No matching evidence found in the indexed text."
    : `Showing ${result.results.length} of ${result.totalMatches} matching files.`;
  knowledgeResults.append(heading);
  for (const match of result.results) {
    const card = document.createElement("article");
    card.className = "evidence-card";
    const citation = document.createElement("p");
    citation.className = "evidence-citation";
    citation.textContent = `${match.collectionName} · ${match.citation}`;
    const excerpt = document.createElement("pre");
    excerpt.textContent = match.excerpt;
    const hash = document.createElement("details");
    const summary = document.createElement("summary");
    summary.textContent = "Source SHA-256";
    const digest = document.createElement("code");
    digest.textContent = match.sha256;
    hash.append(summary, digest);
    card.append(citation, excerpt, hash);
    knowledgeResults.append(card);
  }
}

function updateKnowledgeControls() {
  const panel = document.querySelector(".knowledge");
  panel.setAttribute("aria-busy", String(knowledgeBusy));
  panel.querySelectorAll("button, input").forEach((control) => {
    control.disabled = knowledgeBusy ||
      (control.id === "knowledge-search-button" && knowledgeCollectionTotal === 0);
  });
}

async function runKnowledgeAction(action) {
  if (knowledgeBusy) return;
  knowledgeBusy = true;
  updateKnowledgeControls();
  showKnowledgeMessage("");
  const knowledgePanel = document.querySelector(".knowledge");
  if (action === "import-folder" || action === "import-zip") {
    showKnowledgeMessage("Indexing the selected source locally...");
  } else if (action.startsWith("refresh:")) {
    showKnowledgeMessage("Refreshing the local evidence index...");
  }
  if (action === "import-folder" || action === "import-zip" || action.startsWith("refresh:")) {
    knowledgeResults.replaceChildren();
  }
  try {
    let result;
    if (action === "import-folder") {
      result = await window.axiomSuite.importKnowledgeFolder();
    } else if (action === "import-zip") {
      result = await window.axiomSuite.importKnowledgeZip();
    } else if (action === "search") {
      knowledgeResults.replaceChildren();
      renderKnowledgeResults(await window.axiomSuite.searchKnowledge(knowledgeQuery.value));
      return;
    } else if (action.startsWith("refresh:")) {
      result = { collections: await window.axiomSuite.refreshKnowledge(action.slice(8)) };
    } else if (action.startsWith("remove:")) {
      result = await window.axiomSuite.removeKnowledge(action.slice(7));
    }
    if (result?.canceled) {
      showKnowledgeMessage("");
      return;
    }
    if (result?.collections) renderKnowledgeCollections(result.collections);
    if (action === "import-folder" || action === "import-zip") {
      const added = result.collections.at(-1);
      const skipped =
        added.unsupportedFiles + added.oversizedFiles + added.textLimitFiles +
        added.unreadableFiles + added.symlinksSkipped;
      showKnowledgeMessage(
        `Indexed ${added.indexedTextFiles} text files from ${added.name}. ` +
        `${skipped} files or links were not searched.`
      );
    }
    if (action.startsWith("refresh:")) showKnowledgeMessage("Local evidence index refreshed.");
    if (action.startsWith("remove:")) knowledgeResults.replaceChildren();
  } catch (error) {
    showKnowledgeMessage(error.message || "The local knowledge action failed.");
  } finally {
    knowledgeBusy = false;
    updateKnowledgeControls();
  }
}

function updateState(state) {
  repositoryConnected = Boolean(state.repositoryRoot);
  status.textContent = state.repositoryRoot
    ? state.repositoryRoot
    : "Not connected. Select a repository checkout to open its apps and documentation.";
  disconnect.hidden = !repositoryConnected;
  render();
}

async function loadCatalog() {
  const [catalog, state] = await Promise.all([
    window.axiomSuite.getProducts(),
    window.axiomSuite.getState()
  ]);
  products = catalog;
  if (!Array.isArray(products) || products.length < 1) {
    throw new Error("The product catalog is empty.");
  }
  render();
  updateState(state);
  try {
    renderRuntimes(await window.axiomSuite.listRuntimes());
  } catch (error) {
    document.querySelector("#runtime-message").textContent = `Runtime manager unavailable: ${error.message}`;
  }
  try {
    renderHarness(await window.axiomSuite.getHarness());
  } catch (error) {
    document.querySelector("#harness-message").textContent = `Harness unavailable: ${error.message}`;
  }
  try {
    renderKnowledgeCollections(await window.axiomSuite.listKnowledge());
  } catch (error) {
    showKnowledgeMessage(`The local evidence library could not be loaded: ${error.message}`);
  }
}

search.addEventListener("input", render);
document.querySelector("#runtime-python").addEventListener("click", () => runRuntimeAction("python"));
document.querySelector("#runtime-node").addEventListener("click", () => runRuntimeAction("node"));
document.querySelector("#runtime-refresh").addEventListener("click", () => runRuntimeAction("refresh"));
window.axiomSuite.onRuntimesChanged(async () => {
  try { renderRuntimes(await window.axiomSuite.listRuntimes()); }
  catch (error) { document.querySelector("#runtime-message").textContent = `Runtime state could not be read: ${error.message}`; }
});
document.querySelector("#runtime-list").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-runtime-action]");
  if (button && !button.disabled) runRuntimeAction(button.dataset.runtimeAction, button.dataset.id);
});
document.querySelector("#instruction-form").addEventListener("submit", (event) => {
  event.preventDefault();
  runInstructionAction("ask");
});
document.querySelector("#platform-refresh").addEventListener("click", () => runPlatformAction("refresh"));
document.querySelector("#platform-devices").addEventListener("click", () => runPlatformAction("devices"));
document.querySelector("#platform-distros").addEventListener("click", () => runPlatformAction("distros"));
document.querySelector("#platform-list").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-platform-action]");
  if (button && !button.disabled) runPlatformAction(button.dataset.platformAction, button.dataset.platformId);
});
document.querySelector("#instruction-status").addEventListener("click", () => runInstructionAction("status"));
document.querySelector("#instruction-cancel").addEventListener("click", () => runInstructionAction("cancel"));
document.querySelector("#instruction-export").addEventListener("click", () => runInstructionAction("export"));
document.querySelector("#native-status").addEventListener("click", () => runNativeAction("status"));
document.querySelector("#native-train").addEventListener("click", () => runNativeAction("train"));
document.querySelector("#native-cancel").addEventListener("click", () => runNativeAction("cancel"));
document.querySelector("#native-form").addEventListener("submit", (event) => {
  event.preventDefault();
  runNativeAction("generate");
});
document.querySelector("#hardware-detect").addEventListener("click", () => runHardwareAction());
document.querySelector("#hardware-export").addEventListener("click", () => runHardwareAction(true));
document.querySelector("#harness-use-model").addEventListener("change", (event) => {
  const model = document.querySelector("#harness-model");
  model.disabled = !event.target.checked;
  model.required = event.target.checked;
});
document.querySelector("#harness-list-models").addEventListener("click", async () => {
  const button = document.querySelector("#harness-list-models");
  if (button.disabled) return;
  const message = document.querySelector("#harness-model-message");
  button.disabled = true;
  message.textContent = "Awaiting native approval for installed model metadata only...";
  try {
    const result = await window.axiomSuite.listOllamaModels();
    if (result.canceled) {
      message.textContent = "Cancelled. No model service was contacted.";
      return;
    }
    const options = document.querySelector("#harness-model-options");
    const embedded = document.createElement("option");
    embedded.value = "psicat:embedded";
    options.replaceChildren(embedded);
    for (const model of result.models) {
      const option = document.createElement("option");
      option.value = model.name;
      option.label = `${(model.sizeBytes / 1024 ** 3).toFixed(2)} GiB · engine-reported, UNVERIFIED`;
      options.append(option);
    }
    message.textContent = `${result.models.length} installed local choices; ${result.omitted} entries omitted. ${result.boundary} Enable local reasoning and choose a name explicitly; the current backend has not changed.`;
  } catch (error) {
    message.textContent = `Model discovery failed: ${error.message} The selected backend has not changed.`;
  } finally {
    button.disabled = false;
  }
});
document.querySelector("#harness-form").addEventListener("submit", (event) => {
  event.preventDefault();
  runHarnessAction("create");
});
document.querySelector("#harness-tasks").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-task-id]");
  if (!button) return;
  selectedTaskId = button.dataset.taskId;
  renderHarness(harnessState);
});
document.querySelector("#harness-detail").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-harness-action]");
  if (!button || button.disabled) return;
  runHarnessAction(button.dataset.harnessAction, button.dataset.taskId);
});
document.querySelector("#import-knowledge-folder").addEventListener("click", () =>
  runKnowledgeAction("import-folder")
);
document.querySelector("#import-knowledge-zip").addEventListener("click", () =>
  runKnowledgeAction("import-zip")
);
document.querySelector("#knowledge-search-form").addEventListener("submit", (event) => {
  event.preventDefault();
  runKnowledgeAction("search");
});
knowledgeCollections.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  runKnowledgeAction(`${button.dataset.action}:${button.dataset.id}`);
});
document.querySelector("#connect-repository").addEventListener("click", () => runAction({ type: "connect" }));
disconnect.addEventListener("click", () => runAction({ type: "disconnect" }));
document.querySelector("#open-workspace").addEventListener("click", () => runAction({ type: "workspace" }));
document.querySelector("#open-psicat").addEventListener("click", () => runAction({ type: "psicat" }));
document.querySelector("#open-legal").addEventListener("click", () => runAction({ type: "legal" }));
document.querySelectorAll("[data-category]").forEach((button) => {
  button.addEventListener("click", () => runAction({ type: "category", category: button.dataset.category }));
});
list.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (button && !button.disabled) {
    runAction({ type: button.dataset.action, id: button.dataset.id });
  }
});

loadCatalog().catch((error) => showMessage(error.message || "The suite could not start."));
