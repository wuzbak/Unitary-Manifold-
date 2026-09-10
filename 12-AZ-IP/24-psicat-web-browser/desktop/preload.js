const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('psicatBrowser', {
  getState: () => ipcRenderer.invoke('browser:get-state'),
  createTab: (url, options) => ipcRenderer.invoke('browser:create-tab', url, options),
  closeTab: (tabId) => ipcRenderer.invoke('browser:close-tab', tabId),
  activateTab: (tabId) => ipcRenderer.invoke('browser:activate-tab', tabId),
  navigate: (url) => ipcRenderer.invoke('browser:navigate', url),
  goBack: () => ipcRenderer.invoke('browser:go-back'),
  goForward: () => ipcRenderer.invoke('browser:go-forward'),
  reload: () => ipcRenderer.invoke('browser:reload'),
  stop: () => ipcRenderer.invoke('browser:stop'),
  addBookmark: () => ipcRenderer.invoke('browser:add-bookmark'),
  addNotebookEntry: (entry) => ipcRenderer.invoke('browser:add-notebook-entry', entry),
  updateSettings: (patch) => ipcRenderer.invoke('browser:update-settings', patch),
  queryPsiCat: (payload) => ipcRenderer.invoke('browser:query-psicat', payload),
  importResearchFiles: () => ipcRenderer.invoke('browser:import-research-files'),
  exportResearchBundle: () => ipcRenderer.invoke('browser:export-research-bundle'),
  openExternal: (url) => ipcRenderer.invoke('browser:open-external', url),
  onState: (callback) => ipcRenderer.on('browser:state', (_event, state) => callback(state)),
});
