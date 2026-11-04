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
