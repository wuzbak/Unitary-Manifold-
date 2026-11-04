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
  products = loadProducts(path.join(__dirname, "catalog", "products.json"));
  settingsPath = path.join(app.getPath("userData"), "settings.json");
  knowledgeDirectory = path.join(app.getPath("userData"), "knowledge");
  settings = readSettings(settingsPath);
  registerHandlers();
  createWindow();
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
