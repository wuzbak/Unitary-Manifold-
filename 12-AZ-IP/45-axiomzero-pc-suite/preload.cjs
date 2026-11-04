const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("axiomSuite", Object.freeze({
  getState: () => ipcRenderer.invoke("suite:get-state"),
  getProducts: () => ipcRenderer.invoke("suite:get-products"),
  connectRepository: () => ipcRenderer.invoke("suite:connect-repository"),
  disconnectRepository: () => ipcRenderer.invoke("suite:disconnect-repository"),
  openProductFolder: (id) => ipcRenderer.invoke("suite:open-product-folder", id),
  openProductReadme: (id) => ipcRenderer.invoke("suite:open-product-readme", id),
  openProductSurface: (id) => ipcRenderer.invoke("suite:open-product-surface", id),
  openPsiCat: () => ipcRenderer.invoke("suite:open-psicat"),
  openLegalNotices: () => ipcRenderer.invoke("suite:open-legal-notices"),
  openIpCategory: (category) => ipcRenderer.invoke("suite:open-ip-category", category),
  openWorkspace: () => ipcRenderer.invoke("suite:open-workspace"),
  detectHardware: () => ipcRenderer.invoke("hardware:detect"),
  exportHardware: () => ipcRenderer.invoke("hardware:export"),
  getNativeModel: () => ipcRenderer.invoke("native:status"),
  generateNativeModel: (prompt) => ipcRenderer.invoke("native:generate", prompt),
  trainNativeModel: (steps) => ipcRenderer.invoke("native:train", steps),
  cancelNativeModel: () => ipcRenderer.invoke("native:cancel"),
  listRuntimes: () => ipcRenderer.invoke("runtime:list"),
  installRuntimePython: () => ipcRenderer.invoke("runtime:python"),
  installRuntimeNode: () => ipcRenderer.invoke("runtime:node"),
  installRuntime: (id) => ipcRenderer.invoke("runtime:install", id),
  startRuntime: (id) => ipcRenderer.invoke("runtime:start", id),
  stopRuntime: (id) => ipcRenderer.invoke("runtime:stop", id),
  openRuntime: (id) => ipcRenderer.invoke("runtime:open", id),
  onRuntimesChanged: (callback) => {
    if (typeof callback !== "function") throw new TypeError("Runtime state listener must be a function.");
    const listener = () => callback();
    ipcRenderer.on("runtime:changed", listener);
    return () => ipcRenderer.removeListener("runtime:changed", listener);
  },
  getHarness: () => ipcRenderer.invoke("harness:state"),
  createHarnessTask: (request) => ipcRenderer.invoke("harness:create", request),
  runHarnessStep: (id) => ipcRenderer.invoke("harness:run-step", id),
  pauseHarnessTask: (id) => ipcRenderer.invoke("harness:pause", id),
  cancelHarnessTask: (id) => ipcRenderer.invoke("harness:cancel", id),
  removeHarnessTask: (id) => ipcRenderer.invoke("harness:remove", id),
  exportHarnessTask: (id) => ipcRenderer.invoke("harness:export", id),
  listKnowledge: () => ipcRenderer.invoke("knowledge:list"),
  importKnowledgeFolder: () => ipcRenderer.invoke("knowledge:import-folder"),
  importKnowledgeZip: () => ipcRenderer.invoke("knowledge:import-zip"),
  searchKnowledge: (query) => ipcRenderer.invoke("knowledge:search", query),
  refreshKnowledge: (id) => ipcRenderer.invoke("knowledge:refresh", id),
  removeKnowledge: (id) => ipcRenderer.invoke("knowledge:remove", id)
}));
