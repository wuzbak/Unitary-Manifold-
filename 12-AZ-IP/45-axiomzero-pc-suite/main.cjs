const { app, BrowserWindow, dialog, ipcMain, shell } = require("electron");
const fs = require("node:fs");
const path = require("node:path");
const { pathToFileURL } = require("node:url");
const { loadProducts } = require("./lib/catalog.cjs");
const {
  validateCheckout,
  resolveProductFolder,
  resolveProductReadme
} = require("./lib/repository.cjs");
const { readSettings, writeSettings } = require("./lib/settings.cjs");
const { createExclusiveOperation } = require("./lib/operation-lock.cjs");
const { ResearchHarness, searchCatalog, composeReport } = require("./lib/harness.cjs");
const { searchEvidence } = require("./lib/worker-search.cjs");
const { reasonLocally } = require("./lib/local-model.cjs");
const { detectHardware } = require("./lib/hardware.cjs");
const { createNativeModel } = require("./lib/native-model.cjs");
const { createRuntimeManager } = require("./lib/runtime-manager.cjs");
const { materializePortfolioSource } = require("./lib/portfolio-source.cjs");
const {
  MAX_COLLECTIONS,
  buildCollection,
  loadCollection,
  removeCollection,
  saveCollection,
  searchCollections,
  summarizeCollection
} = require("./lib/knowledge.cjs");

let mainWindow;
let products;
let settingsPath;
let knowledgeDirectory;
let settings;
let harness;
let hardwareReport;
let nativeModel;
let runtimeManager;
const runNativeMutation = createExclusiveOperation("Another own-model operation is in progress.");
const runHardwareDetection = createExclusiveOperation("Hardware detection is already in progress.");
const ownsInstance = app.requestSingleInstanceLock();
if (!ownsInstance) app.quit();
app.on("second-instance", () => {
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore();
    mainWindow.show();
    mainWindow.focus();
  }
});
const knowledgeCache = new Map();
const runKnowledgeMutation = createExclusiveOperation(
  "Another local library change is already in progress."
);

function knowledgeCollections() {
  return settings.knowledgeCollectionIds.map((id) => {
    if (!knowledgeCache.has(id)) {
      knowledgeCache.set(id, loadCollection(knowledgeDirectory, id));
    }
    return knowledgeCache.get(id);
  });
}

async function importKnowledgeSource(properties, filters, title) {
  if (settings.knowledgeCollectionIds.length >= MAX_COLLECTIONS) {
    throw new Error(`The local library is limited to ${MAX_COLLECTIONS} collections.`);
  }
  const options = { title, properties };
  if (filters) options.filters = filters;
  const result = await dialog.showOpenDialog(mainWindow, options);
  if (result.canceled || result.filePaths.length === 0) {
    return { canceled: true };
  }
  const collection = await buildCollection(result.filePaths[0]);
  saveCollection(knowledgeDirectory, collection);
  knowledgeCache.set(collection.id, collection);
  settings = {
    ...settings,
    knowledgeCollectionIds: [...settings.knowledgeCollectionIds, collection.id]
  };
  writeSettings(settingsPath, settings);
  return {
    canceled: false,
    collections: knowledgeCollections().map(summarizeCollection)
  };
}

function productById(id) {
  if (typeof id !== "string") {
    throw new TypeError("Product identifier must be text.");
  }
  const product = products.find((entry) => entry.id === id);
  if (!product) {
    throw new Error("That product is not in the bundled catalog.");
  }
  return product;
}

function requireRepository() {
  if (!settings.repositoryRoot) {
    throw new Error("Connect a local repository checkout first.");
  }
  return validateCheckout(settings.repositoryRoot);
}

async function openLocalPath(target) {
  const error = await shell.openPath(target);
  if (error) {
    throw new Error(`The system could not open the selected location: ${error}`);
  }
}

function registerHandlers() {
  ipcMain.handle("runtime:list", () => runtimeManager.list());
  ipcMain.handle("runtime:python", async () => {
    const response = await dialog.showMessageBox(mainWindow, {
      type: "warning", title: "Install Windows Python prerequisite",
      message: "Use Windows Package Manager to install Python 3.12 for this user?",
      detail: "This downloads third-party software through winget and accepts that package/source's agreements. Python is required by the managed portfolio environments, not by the embedded model. Review the Python license first. No administrator elevation is requested. This requires internet access and an available Windows Package Manager.",
      buttons: ["Cancel", "Install user-scoped Python"], defaultId: 0, cancelId: 0, noLink: true
    });
    if (response.response !== 1) return { canceled: true };
    return runtimeManager.installPython();
  });
  ipcMain.handle("runtime:install", async (_event, id) => {
    const entry = runtimeManager.list().find((item) => item.id === id);
    if (!entry) throw new Error("That runtime is not registered.");
    const response = await dialog.showMessageBox(mainWindow, {
      type: "warning", title: `Install Product ${id} dependencies`,
      message: "Provision this product in its own local Python environment?",
      detail: `${entry.limitation}\n\nThe suite copies its bundled tracked source into a user-data worktree if no checkout is connected. pip downloads and executes package installation code from the configured package index; installation may take ten minutes. External services/credentials and target-specific compatibility remain separate. Dependency success is not full product certification.`,
      buttons: ["Cancel", "Install this runtime"], defaultId: 0, cancelId: 0, noLink: true
    });
    if (response.response !== 1) return { canceled: true };
    return runtimeManager.install(id);
  });
  ipcMain.handle("runtime:start", async (_event, id) => {
    const response = await dialog.showMessageBox(mainWindow, {
      type: "question", title: `Start Product ${id}`,
      message: "Start the registered local runtime?",
      detail: "This executes the installed product code with your user permissions. It may read/write its own local state and use its documented network integrations. Only reviewed loopback launches are offered. Product 20 local command execution is disabled. The desktop owns this process and stops it when quitting.",
      buttons: ["Cancel", "Start local runtime"], defaultId: 0, cancelId: 0, noLink: true
    });
    if (response.response !== 1) return { canceled: true };
    return runtimeManager.start(id);
  });
  ipcMain.handle("runtime:stop", (_event, id) => runtimeManager.stop(id));
  ipcMain.handle("native:status", () => nativeModel.status());
  ipcMain.handle("native:generate", (_event, prompt) => runNativeMutation(async () => {
    if (typeof prompt !== "string" || !prompt.trim() || prompt.length > 400) throw new Error("Enter a prompt of 1-400 characters.");
    const response = await dialog.showMessageBox(mainWindow, {
      type: "question", title: "Run embedded PsiCat model",
      message: "Generate locally using the installed own toroidal model?",
      detail: "This is experimental character generation, not a verified assistant answer. No cloud provider or external service is used; the model cannot execute tools. Output is unverified.",
      buttons: ["Cancel", "Generate locally"], defaultId: 0, cancelId: 0, noLink: true
    });
    if (response.response !== 1) return { canceled: true };
    return nativeModel.generate(prompt);
  }));
  ipcMain.handle("native:train", (_event, steps) => runNativeMutation(async () => {
    if (!Number.isInteger(steps) || steps < 1 || steps > 2000) throw new Error("Choose a training budget of 1-2000 steps.");
    const source = await dialog.showOpenDialog(mainWindow, {
      title: "Select an approved UTF-8 training corpus (up to 8 MiB)",
      properties: ["openFile"], filters: [{ name: "Text corpus", extensions: ["txt", "md"] }]
    });
    if (source.canceled) return { canceled: true };
    const response = await dialog.showMessageBox(mainWindow, {
      type: "warning", title: "Train your own PsiCat checkpoint",
      message: `Train for ${steps} steps on the selected corpus?`,
      detail: "This starts real CPU training, up to ten minutes, on the selected text only. The corpus is not uploaded. A completed checkpoint replaces only this suite's previous trained model; interrupted/failed training keeps the old model. Weights may memorize private text: protect the local user profile. Training is experimental and does not certify assistant competence.",
      buttons: ["Cancel", "Train locally"], defaultId: 0, cancelId: 0, noLink: true
    });
    if (response.response !== 1) return { canceled: true };
    return nativeModel.train(source.filePaths[0], steps);
  }));
  ipcMain.handle("native:cancel", () => nativeModel.cancel());
  ipcMain.handle("hardware:detect", () => runHardwareDetection(async () => {
    const response = await dialog.showMessageBox(mainWindow, {
      type: "question",
      title: "Detect local model hardware",
      message: "Inspect RAM, CPU, application-data disk space and graphics diagnostics?",
      detail: "Read-only local diagnostics. No files, serial numbers or account identity are collected, no network calls or downloads are made, and nothing is installed. GPU diagnostics do not certify VRAM or training capability. Results remain in memory until you explicitly export.",
      buttons: ["Cancel", "Detect hardware"], defaultId: 0, cancelId: 0, noLink: true
    });
    if (response.response !== 1) return { canceled: true };
    hardwareReport = await detectHardware(app.getPath("userData"), (kind) => app.getGPUInfo(kind));
    return { canceled: false, report: hardwareReport };
  }));
  ipcMain.handle("hardware:export", async () => {
    if (!hardwareReport) throw new Error("Detect hardware before exporting a report.");
    const result = await dialog.showSaveDialog(mainWindow, {
      title: "Export local hardware assessment",
      defaultPath: "axiomzero-hardware-assessment.json",
      filters: [{ name: "Hardware assessment", extensions: ["json"] }]
    });
    if (result.canceled) return { canceled: true };
    fs.writeFileSync(result.filePath, `${JSON.stringify(hardwareReport, null, 2)}\n`, { mode: 0o600 });
    return { canceled: false };
  });
  ipcMain.handle("harness:state", () => harness.snapshot());
  ipcMain.handle("harness:create", (_event, request) => harness.create(request));
  ipcMain.handle("harness:run-step", async (_event, id) => {
    const proposal = harness.proposal(id);
    await harness.execute(proposal, async (step) => {
      const response = await dialog.showMessageBox(mainWindow, {
        type: "question",
        title: "Approve one harness step",
        message: `${step.tool} for "${step.goal}"`,
        detail: `${step.disclosure}\n\nAttempt budget: six per task. Deadline: 60 seconds per step. Approval applies only to this step and expires if its checkpoint changes.${step.contextTruncated ? "\nPrior context is truncated to 12,000 characters; full results remain in the checkpoint." : ""}`,
        buttons: ["Cancel", "Approve this step"],
        defaultId: 0, cancelId: 0, noLink: true
      });
      return response.response === 1;
    });
    return harness.snapshot();
  });
  ipcMain.handle("harness:pause", (_event, id) => {
    harness.stop(id);
    return harness.snapshot();
  });
  ipcMain.handle("harness:cancel", (_event, id) => {
    harness.stop(id, true);
    return harness.snapshot();
  });
  ipcMain.handle("harness:remove", async (_event, id) => {
    const run = harness.get(id);
    const response = await dialog.showMessageBox(mainWindow, {
      type: "warning", title: "Remove harness checkpoint?",
      message: `Remove the task and results for "${run.goal}"?`,
      detail: "Export first if needed. Original sources are unchanged. The bounded audit trail retains task IDs and action metadata, not the removed results.",
      buttons: ["Cancel", "Remove checkpoint"], defaultId: 0, cancelId: 0, noLink: true
    });
    if (response.response === 1) harness.remove(id);
    return harness.snapshot();
  });
  ipcMain.handle("harness:export", async (_event, id) => {
    harness.get(id);
    const result = await dialog.showSaveDialog(mainWindow, {
      title: "Export research checkpoint and audit",
      defaultPath: `axiomzero-research-${id}.json`,
      filters: [{ name: "Research checkpoint", extensions: ["json"] }]
    });
    if (result.canceled) return { canceled: true };
    fs.writeFileSync(result.filePath, `${JSON.stringify(harness.export(id), null, 2)}\n`, { mode: 0o600 });
    return { canceled: false };
  });
  ipcMain.handle("suite:get-state", () => ({
    repositoryRoot: settings.repositoryRoot,
    productCount: products.length,
    version: app.getVersion()
  }));
  ipcMain.handle("suite:get-products", () => products);
  ipcMain.handle("knowledge:list", () =>
    knowledgeCollections().map(summarizeCollection)
  );
  ipcMain.handle("knowledge:import-folder", () =>
    runKnowledgeMutation(() =>
      importKnowledgeSource(["openDirectory"], undefined, "Select a local source folder")
    )
  );
  ipcMain.handle("knowledge:import-zip", () =>
    runKnowledgeMutation(() =>
      importKnowledgeSource(
        ["openFile"],
        [{ name: "ZIP archives", extensions: ["zip"] }],
        "Select a local ZIP archive"
      )
    )
  );
  ipcMain.handle("knowledge:search", (_event, query) =>
    searchCollections(knowledgeCollections(), query)
  );
  ipcMain.handle("knowledge:refresh", (_event, id) =>
    runKnowledgeMutation(async () => {
      const collection = knowledgeCollections().find((item) => item.id === id);
      if (!collection) {
        throw new Error("That local library collection is no longer available.");
      }
      const updated = await buildCollection(collection.root, collection.id);
      saveCollection(knowledgeDirectory, updated);
      knowledgeCache.set(updated.id, updated);
      return knowledgeCollections().map(summarizeCollection);
    })
  );
  ipcMain.handle("knowledge:remove", (_event, id) =>
    runKnowledgeMutation(async () => {
      const collection = knowledgeCollections().find((item) => item.id === id);
      if (!collection) {
        throw new Error("That local library collection is no longer available.");
      }
      const confirmation = await dialog.showMessageBox(mainWindow, {
        type: "warning",
        title: "Remove local search index?",
        message: `Remove the local index for "${collection.name}"?`,
        detail: "The original folder or ZIP is not changed. Indexed text is stored locally without encryption.",
        buttons: ["Cancel", "Remove index"],
        defaultId: 0,
        cancelId: 0,
        noLink: true
      });
      if (confirmation.response !== 1) {
        return { canceled: true };
      }
      removeCollection(knowledgeDirectory, id);
      knowledgeCache.delete(id);
      settings = {
        ...settings,
        knowledgeCollectionIds: settings.knowledgeCollectionIds.filter((item) => item !== id)
      };
      writeSettings(settingsPath, settings);
      return {
        canceled: false,
        collections: knowledgeCollections().map(summarizeCollection)
      };
    })
  );

  ipcMain.handle("suite:connect-repository", async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
      title: "Select the Unitary Manifold repository folder",
      properties: ["openDirectory"]
    });
    if (result.canceled || result.filePaths.length === 0) {
      return { canceled: true };
    }
    const root = validateCheckout(result.filePaths[0]);
    settings = { ...settings, repositoryRoot: root };
    writeSettings(settingsPath, settings);
    return { canceled: false, repositoryRoot: root };
  });

  ipcMain.handle("suite:disconnect-repository", () => {
    settings = { ...settings, repositoryRoot: null };
    writeSettings(settingsPath, settings);
    return { repositoryRoot: null };
  });

  ipcMain.handle("suite:open-product-folder", async (_event, id) => {
    const product = productById(id);
    const root = requireRepository();
    const target = resolveProductFolder(root, product.folder);
    if (!fs.statSync(target).isDirectory()) {
      throw new Error(`The product folder is missing: ${product.folder}`);
    }
    await openLocalPath(target);
    return { opened: product.id };
  });

  ipcMain.handle("suite:open-product-readme", async (_event, id) => {
    const product = productById(id);
    const root = requireRepository();
    const readme = resolveProductReadme(root, product.folder);
    if (!fs.existsSync(readme) || !fs.statSync(readme).isFile()) {
      throw new Error(`No README.md is available for ${product.name}.`);
    }
    await openLocalPath(readme);
    return { opened: product.id };
  });

  ipcMain.handle("suite:open-product-surface", async (_event, id) => {
    const product = productById(id);
    const address = product.endpoint;
    if (!/^https?:\/\/(?:localhost|127\.0\.0\.1)(?::\d{1,5})?(?:\/[^\s]*)?$/i.test(address)) {
      throw new Error("This catalog entry has no supported loopback service endpoint.");
    }
    await shell.openExternal(address);
    return { opened: product.id };
  });

  ipcMain.handle("suite:open-psicat", async () => {
    await shell.openExternal("http://127.0.0.1:8020");
    return { opened: "psicat-navigator" };
  });

  ipcMain.handle("suite:open-legal-notices", async () => {
    const legalDirectory = app.isPackaged
      ? process.resourcesPath
      : path.resolve(__dirname, "..");
    const notice = path.join(legalDirectory, "NOTICE");
    if (!fs.existsSync(notice) || !fs.statSync(notice).isFile()) {
      throw new Error("The bundled software notice is missing.");
    }
    await openLocalPath(notice);
    return { opened: "NOTICE" };
  });

  ipcMain.handle("suite:open-ip-category", async (_event, category) => {
    const root = requireRepository();
    const allowed = new Set(["apps", "calculators", "engines", "os", "tools", "lib"]);
    if (typeof category !== "string" || !allowed.has(category)) {
      throw new Error("That portfolio category is not available.");
    }
    const target = resolveProductFolder(root, `12-AZ-IP/${category}`);
    if (!fs.existsSync(target) || !fs.statSync(target).isDirectory()) {
      throw new Error(`The ${category} portfolio folder is not present in this checkout.`);
    }
    await openLocalPath(target);
    return { opened: category };
  });

  ipcMain.handle("suite:open-workspace", async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
      title: "Choose a local work folder",
      properties: ["openDirectory", "createDirectory"]
    });
    if (result.canceled || result.filePaths.length === 0) {
      return { canceled: true };
    }
    await openLocalPath(path.resolve(result.filePaths[0]));
    return { canceled: false };
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1180,
    height: 820,
    minWidth: 760,
    minHeight: 580,
    title: "AxiomZero PC Suite",
    backgroundColor: "#111827",
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    }
  });
  mainWindow.webContents.setWindowOpenHandler(() => ({ action: "deny" }));
  mainWindow.webContents.on("will-navigate", (event, target) => {
    if (target !== pathToFileURL(path.join(__dirname, "index.html")).href) {
      event.preventDefault();
    }
  });
  mainWindow.webContents.on("will-redirect", (event) => {
    event.preventDefault();
  });
  mainWindow.loadFile(path.join(__dirname, "index.html"));
}

app.whenReady().then(() => {
  if (!ownsInstance) return;
  products = loadProducts(path.join(__dirname, "catalog", "products.json"));
  settingsPath = path.join(app.getPath("userData"), "settings.json");
  knowledgeDirectory = path.join(app.getPath("userData"), "knowledge");
  settings = readSettings(settingsPath);
  const runtimeEntries = JSON.parse(fs.readFileSync(path.join(__dirname, "catalog/runtimes.json"), "utf8"));
  function portfolioRoot() {
    if (settings.repositoryRoot) return requireRepository();
    if (!app.isPackaged) return validateCheckout(path.resolve(__dirname, "../.."));
    return materializePortfolioSource(
      path.join(process.resourcesPath, "portfolio"),
      path.join(app.getPath("userData"), "portfolio")
    );
  }
  runtimeManager = createRuntimeManager({
    entries: runtimeEntries, sourceRoot: portfolioRoot,
    dataDirectory: path.join(app.getPath("userData"), "runtimes")
  });
  const nativeDirectory = app.isPackaged
    ? path.join(process.resourcesPath, "psicat-native")
    : path.join(__dirname, "build/native");
  nativeModel = createNativeModel({
    executable: path.join(nativeDirectory, "PsiCatCore", process.platform === "win32" ? "PsiCatCore.exe" : "PsiCatCore"),
    seed: path.join(nativeDirectory, "psicat-seed.npz"),
    userDirectory: path.join(app.getPath("userData"), "psicat-model")
  });
  harness = new ResearchHarness(path.join(app.getPath("userData"), "research-harness.json"), {
    "catalog.search": ({ goal }) => searchCatalog(products, goal),
    "evidence.search": ({ goal, signal }) => runKnowledgeMutation(() => searchEvidence({
      directory: knowledgeDirectory, ids: [...settings.knowledgeCollectionIds], goal, signal
    })),
    "report.compose": composeReport,
    "model.reason": ({ goal, model, context, signal }) => reasonLocally({ goal, model, context, signal })
  });
  registerHandlers();
  createWindow();
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
}).catch((error) => {
  dialog.showErrorBox("AxiomZero PC Suite could not start", error.message);
  app.quit();
});

app.on("before-quit", () => {
  if (harness?.active) harness.stop(harness.active.id);
  if (nativeModel?.isActive()) nativeModel.cancel();
  runtimeManager?.stopAll();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
