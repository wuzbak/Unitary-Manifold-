const { app, BrowserWindow, BrowserView, Menu, dialog, ipcMain, shell, session } = require('electron');
const path = require('node:path');
const fs = require('node:fs');
const fsp = require('node:fs/promises');
const crypto = require('node:crypto');
const { spawn } = require('node:child_process');
const core = require('./lib/browser-core');
const pageContext = require('./lib/page-context');

const PRODUCT_ROOT = path.resolve(__dirname, '..');
const REPO_ROOT = path.resolve(PRODUCT_ROOT, '..', '..');
const UI_ENTRY = path.join(__dirname, 'ui', 'index.html');
const PSICAT_RUN_PATH = path.resolve(PRODUCT_ROOT, '..', '20-psicat-navigator', 'run.py');
const SYNC_BACKEND_RUN_PATH = path.join(PRODUCT_ROOT, 'sync_backend', 'server.py');
const PSICAT_HOST = '127.0.0.1';
const PSICAT_PORT = 8020;
const SYNC_HOST = '127.0.0.1';
const SYNC_PORT = 8787;

let mainWindow;
let statePath;
let syncMirrorPath;
let state = core.createInitialState();
let tabViews = new Map();
let psiCatSidecar = { status: 'not_started', pid: null, baseUrl: `http://${PSICAT_HOST}:${PSICAT_PORT}`, error: '' };
let psiCatProcess = null;
let syncBackend = { status: 'not_started', pid: null, baseUrl: `http://${SYNC_HOST}:${SYNC_PORT}`, error: '' };
let syncBackendProcess = null;
const trackedSessions = new WeakSet();

function sha256(text) {
  return crypto.createHash('sha256').update(text).digest('hex');
}

async function loadState() {
  try {
    const raw = await fsp.readFile(statePath, 'utf-8');
    state = core.normalizeState(JSON.parse(raw));
  } catch (_error) {
    state = core.createInitialState();
  }
}

async function persistState() {
  await fsp.mkdir(path.dirname(statePath), { recursive: true });
  await fsp.writeFile(statePath, JSON.stringify(state, null, 2));
}

function getActiveTab() {
  return state.tabs.find((tab) => tab.id === state.activeTabId) || state.tabs[0];
}

function serializeState() {
  return { ...state, psiCatSidecar, syncBackend };
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function broadcastState() {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send('browser:state', serializeState());
  }
}

function createBrowserView(tab) {
  const view = new BrowserView({
    webPreferences: {
      partition: tab.private ? `memory:${tab.id}` : undefined,
      contextIsolation: true,
      sandbox: true,
    },
  });
  registerDownloadTracking(view.webContents.session);
  view.webContents.setWindowOpenHandler(({ url }) => {
    state = core.addTab(state, url, { title: 'New Tab' });
    const nextTab = getActiveTab();
    mountTab(nextTab);
    persistState().then(broadcastState);
    return { action: 'deny' };
  });
  view.webContents.on('page-title-updated', (_event, title) => {
    state = core.updateTab(state, tab.id, { title });
    persistState().then(broadcastState);
  });
  view.webContents.on('did-start-loading', () => {
    state = core.updateTab(state, tab.id, { loading: true });
    broadcastState();
  });
  view.webContents.on('did-stop-loading', () => {
    updateNavigationState(tab.id).then(() => captureSnapshot(tab.id));
  });
  view.webContents.on('did-navigate', (_event, url) => {
    state = core.updateTab(state, tab.id, { url });
    state = core.pushHistory(state, { title: view.webContents.getTitle() || tab.title, url });
    persistState().then(broadcastState);
  });
  view.webContents.on('did-navigate-in-page', (_event, url) => {
    state = core.updateTab(state, tab.id, { url });
    persistState().then(broadcastState);
  });
  view.webContents.on('render-process-gone', () => {
    state = core.updateTab(state, tab.id, { title: `${tab.title} (Recovered)` });
    persistState().then(broadcastState);
  });
  return view;
}

function registerDownloadTracking(targetSession) {
  if (!targetSession || trackedSessions.has(targetSession)) return;
  trackedSessions.add(targetSession);
  targetSession.on('will-download', (_event, item) => {
    state = core.addDownload(state, {
      url: item.getURL(),
      fileName: item.getFilename(),
      savePath: item.getSavePath(),
      totalBytes: item.getTotalBytes(),
    });
    persistState().then(broadcastState);
  });
}

async function updateNavigationState(tabId) {
  const view = tabViews.get(tabId);
  if (!view) return;
  state = core.updateTab(state, tabId, {
    url: view.webContents.getURL() || getActiveTab().url,
    title: view.webContents.getTitle() || getActiveTab().title,
    loading: view.webContents.isLoading(),
    canGoBack: view.webContents.navigationHistory.canGoBack(),
    canGoForward: view.webContents.navigationHistory.canGoForward(),
  });
  await persistState();
  broadcastState();
}

async function rememberActivePage() {
  const active = getActiveTab();
  if (!active) return serializeState();
  if (active.lastSnapshot) {
    state = core.rememberPage(state, active.lastSnapshot);
    state = core.addNotebookEntry(state, {
      title: `Remembered research — ${active.lastSnapshot.title || active.title}`,
      text: (active.lastSnapshot.selection || active.lastSnapshot.text || '').slice(0, 2000),
      tags: ['captured-page'],
      url: active.lastSnapshot.url || active.url,
    });
    await persistState();
    if (state.sync.accountEmail) await writeSyncMirror('local-mirror');
    broadcastState();
  }
  return serializeState();
}

async function captureSnapshot(tabId) {
  const view = tabViews.get(tabId);
  if (!view || !state.settings.livePageCapture) return;
  try {
    const snapshot = await view.webContents.executeJavaScript(`(() => ({
      title: document.title,
      url: location.href,
      selection: String(window.getSelection ? window.getSelection() : '').trim(),
      text: document.body ? document.body.innerText.slice(0, 12000) : '',
      capturedAt: new Date().toISOString()
    }))()`);
    state = core.updateTab(state, tabId, { lastSnapshot: snapshot });
    state = core.rememberPage(state, snapshot);
    await persistState();
    broadcastState();
  } catch (_error) {
    // Ignore pages that reject injection.
  }
}

function layoutViews() {
  if (!mainWindow || mainWindow.isDestroyed()) return;
  const bounds = mainWindow.getContentBounds();
  const toolbarHeight = 96;
  const sidebarWidth = Math.max(320, Math.min(640, Number(state.settings.sidebarWidth || 420)));
  const active = getActiveTab();
  const secondaryId = state.workspace?.layout === 'single' ? null : state.workspace?.secondaryTabId;
  const secondaryView = secondaryId ? tabViews.get(secondaryId) : null;
  const leftWidth = bounds.width - sidebarWidth;
  const splitVertical = state.workspace?.layout === 'split-vertical' && secondaryView;
  const splitHorizontal = state.workspace?.layout === 'split-horizontal' && secondaryView;
  for (const [tabId, view] of tabViews.entries()) {
    if (tabId !== active.id && tabId !== secondaryId) {
      view.setBounds({ x: 0, y: 0, width: 0, height: 0 });
      continue;
    }
    const fullHeight = Math.max(200, bounds.height - toolbarHeight);
    if (splitVertical) {
      const paneWidth = Math.max(200, Math.floor(leftWidth / 2));
      const isSecondary = tabId === secondaryId;
      view.setBounds({ x: isSecondary ? paneWidth : 0, y: toolbarHeight, width: paneWidth, height: fullHeight });
    } else if (splitHorizontal) {
      const paneHeight = Math.max(160, Math.floor(fullHeight / 2));
      const isSecondary = tabId === secondaryId;
      view.setBounds({ x: 0, y: toolbarHeight + (isSecondary ? paneHeight : 0), width: leftWidth, height: paneHeight });
    } else {
      view.setBounds({ x: 0, y: toolbarHeight, width: leftWidth, height: fullHeight });
    }
    view.setAutoResize({ width: true, height: true });
  }
}

function mountTab(tab) {
  if (!mainWindow) return;
  let view = tabViews.get(tab.id);
  if (!view) {
    view = createBrowserView(tab);
    tabViews.set(tab.id, view);
    mainWindow.addBrowserView(view);
    view.webContents.loadURL(tab.url);
  }
  state = core.activateTab(state, tab.id);
  layoutViews();
  persistState().then(broadcastState);
}

async function closeTab(tabId) {
  const view = tabViews.get(tabId);
  if (view && mainWindow) {
    mainWindow.removeBrowserView(view);
    view.webContents.close();
    tabViews.delete(tabId);
  }
  state = core.closeTab(state, tabId);
  const active = getActiveTab();
  if (active && !tabViews.has(active.id)) mountTab(active);
  ensureWorkspaceViews();
  await persistState();
  layoutViews();
  broadcastState();
}

function buildMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        { label: 'New Tab', accelerator: 'CmdOrCtrl+T', click: () => ipcCreateTab() },
        { label: 'New Private Tab', accelerator: 'CmdOrCtrl+Shift+P', click: () => ipcCreateTab(undefined, { private: true }) },
        { label: 'Import Research', click: () => handleImportResearchFiles() },
        { label: 'Export Research Packet', click: () => handleExportResearchBundle() },
        { label: 'Import Sync Packet', click: () => handleImportSyncPacket() },
        { label: 'Export Sync Packet', click: () => handleExportSyncPacket() },
        { type: 'separator' },
        { role: 'quit' },
      ],
    },
    { label: 'Edit', submenu: [{ role: 'undo' }, { role: 'redo' }, { type: 'separator' }, { role: 'cut' }, { role: 'copy' }, { role: 'paste' }] },
    { label: 'View', submenu: [{ role: 'reload' }, { role: 'toggleDevTools' }, { role: 'resetZoom' }, { role: 'zoomIn' }, { role: 'zoomOut' }] },
    {
      label: 'Browser',
      submenu: [
        { label: 'Back', accelerator: 'Alt+Left', click: () => navigateActive('back') },
        { label: 'Forward', accelerator: 'Alt+Right', click: () => navigateActive('forward') },
        { label: 'Home', accelerator: 'Alt+Home', click: () => navigateActive('load', state.settings.homePage) },
        { label: 'Reopen Closed Tab', accelerator: 'CmdOrCtrl+Shift+T', click: () => reopenClosedTab() },
        { label: 'Bookmark Page', accelerator: 'CmdOrCtrl+D', click: () => addBookmark() },
        { label: 'Settings', accelerator: 'CmdOrCtrl+,', click: () => broadcastState() },
      ],
    },
  ];
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

function ipcCreateTab(url, options = {}) {
  state = core.addTab(state, url || state.settings.homePage, options);
  mountTab(getActiveTab());
}

function ensureWorkspaceViews() {
  const active = getActiveTab();
  if (active && !tabViews.has(active.id)) mountTab(active);
  const secondaryId = state.workspace?.secondaryTabId;
  if (secondaryId) {
    const secondary = state.tabs.find((tab) => tab.id === secondaryId);
    if (secondary && !tabViews.has(secondary.id)) {
      let view = createBrowserView(secondary);
      tabViews.set(secondary.id, view);
      mainWindow.addBrowserView(view);
      view.webContents.loadURL(secondary.url);
    }
  }
  layoutViews();
}

async function reopenClosedTab() {
  const reopened = core.reopenLastClosedTab(state);
  if (reopened.activeTabId === state.activeTabId && reopened.tabs.length === state.tabs.length) {
    return serializeState();
  }
  state = reopened;
  mountTab(getActiveTab());
  ensureWorkspaceViews();
  await persistState();
  broadcastState();
  return serializeState();
}

async function updateWorkspaceLayout(layout, secondaryTabId = null) {
  state = core.setWorkspaceLayout(state, layout);
  state = core.setWorkspaceSecondaryTab(state, secondaryTabId);
  ensureWorkspaceViews();
  await persistState();
  broadcastState();
  return serializeState();
}

async function saveWorkspace(name) {
  state = core.saveCurrentWorkspace(state, name);
  await persistState();
  broadcastState();
  return serializeState();
}

async function applyWorkspace(workspaceId) {
  state = core.applySavedWorkspace(state, workspaceId);
  for (const [tabId, view] of tabViews.entries()) {
    if (mainWindow) mainWindow.removeBrowserView(view);
    view.webContents.close();
    tabViews.delete(tabId);
  }
  ensureWorkspaceViews();
  await persistState();
  broadcastState();
  return serializeState();
}

async function addBookmark() {
  const active = getActiveTab();
  if (!active) return;
  const snapshot = active.lastSnapshot || {};
  state = core.addBookmark(state, { title: snapshot.title || active.title, url: snapshot.url || active.url });
  await persistState();
  if (state.sync.accountEmail) await writeSyncMirror('local-mirror');
  broadcastState();
}

async function navigateActive(action, url) {
  const active = getActiveTab();
  const view = active ? tabViews.get(active.id) : null;
  if (!view) return serializeState();
  if (action === 'load') {
    const nextUrl = core.sanitizeUrl(url, state.settings);
    await view.webContents.loadURL(nextUrl);
  } else if (action === 'back' && view.webContents.navigationHistory.canGoBack()) {
    view.webContents.navigationHistory.goBack();
  } else if (action === 'forward' && view.webContents.navigationHistory.canGoForward()) {
    view.webContents.navigationHistory.goForward();
  } else if (action === 'reload') {
    view.webContents.reload();
  } else if (action === 'stop') {
    view.webContents.stop();
  }
  await updateNavigationState(active.id);
  return serializeState();
}

async function startPsiCatSidecar() {
  if (!state.settings.autoStartPsiCat || !fs.existsSync(PSICAT_RUN_PATH)) {
    psiCatSidecar = { ...psiCatSidecar, status: 'disabled', error: fs.existsSync(PSICAT_RUN_PATH) ? '' : 'Product 20 run.py not found' };
    return;
  }
  psiCatSidecar = { ...psiCatSidecar, status: 'starting', error: '' };
  broadcastState();
  psiCatProcess = spawn('python3', [PSICAT_RUN_PATH, '--host', PSICAT_HOST, '--port', String(PSICAT_PORT), '--no-open'], {
    cwd: path.dirname(PSICAT_RUN_PATH),
    env: process.env,
    stdio: 'ignore',
    detached: false,
  });
  psiCatSidecar = { ...psiCatSidecar, pid: psiCatProcess.pid };
  psiCatProcess.on('exit', (code) => {
    psiCatSidecar = { ...psiCatSidecar, status: 'stopped', error: code === 0 ? '' : `PsiCat sidecar exited with code ${code}` };
    broadcastState();
  });
  for (let attempt = 0; attempt < 20; attempt += 1) {
    try {
      const response = await fetch(`${psiCatSidecar.baseUrl}/api/psicat/status`);
      if (response.ok) {
        psiCatSidecar = { ...psiCatSidecar, status: 'ready', error: '' };
        broadcastState();
        return;
      }
    } catch (_error) {
      // wait for sidecar readiness
    }
    await delay(500);
  }
  psiCatSidecar = { ...psiCatSidecar, status: 'degraded', error: 'PsiCat sidecar did not become ready in time' };
  broadcastState();
}

async function startSyncBackend() {
  if (!fs.existsSync(SYNC_BACKEND_RUN_PATH)) {
    syncBackend = { ...syncBackend, status: 'disabled', error: 'Sync backend server.py not found' };
    broadcastState();
    return;
  }
  syncBackend = { ...syncBackend, status: 'starting', error: '' };
  broadcastState();
  syncBackendProcess = spawn('python3', [SYNC_BACKEND_RUN_PATH, '--host', SYNC_HOST, '--port', String(SYNC_PORT)], {
    cwd: path.dirname(SYNC_BACKEND_RUN_PATH),
    env: process.env,
    stdio: 'ignore',
    detached: false,
  });
  syncBackend = { ...syncBackend, pid: syncBackendProcess.pid };
  syncBackendProcess.on('exit', (code) => {
    syncBackend = { ...syncBackend, status: 'stopped', error: code === 0 ? '' : `Sync backend exited with code ${code}` };
    broadcastState();
  });
  for (let attempt = 0; attempt < 20; attempt += 1) {
    try {
      const response = await fetch(`${syncBackend.baseUrl}/api/sync/health`);
      if (response.ok) {
        syncBackend = { ...syncBackend, status: 'ready', error: '' };
        broadcastState();
        return;
      }
    } catch (_error) {
      // wait for backend readiness
    }
    await delay(500);
  }
  syncBackend = { ...syncBackend, status: 'degraded', error: 'Sync backend did not become ready in time' };
  broadcastState();
}

async function callPsiCat(question) {
  const envelope = pageContext.buildContextEnvelope(state);
  const activeText = envelope.current_page ? (envelope.current_page.excerpt || envelope.current_page.bullets.join(' ')) : '';
  if (psiCatSidecar.status !== 'ready') {
    return {
      mode: 'local',
      answer: `[Local research mode]\n${pageContext.summarizeResearchBundle({ question, state })}`,
    };
  }
  try {
    const statusResponse = await fetch(`${psiCatSidecar.baseUrl}/api/psicat/status`);
    const statusPayload = await statusResponse.json();
    const challenge = statusResponse.headers.get('X-PsiCat-Handshake-Challenge') || statusPayload?.session_contract?.handshake?.challenge;
    const receipt = statusResponse.headers.get('X-PsiCat-Handshake-Receipt') || statusPayload?.session_contract?.handshake?.receipt;
    const token = statusPayload?.memory_profile_token;
    if (!challenge || !receipt || !token) throw new Error('Missing PsiCat handshake material');
    const response = await fetch(`${psiCatSidecar.baseUrl}/api/psicat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: question,
        page_context: activeText,
        user_context: 'PsiCat Browser Product 24 desktop shell',
        context_envelope: envelope,
        memory_profile_token: token,
        psicat_handshake_challenge: challenge,
        psicat_handshake_receipt: receipt,
        psicat_handshake_proof: sha256(`${challenge}:${token}`),
      }),
    });
    const payload = await response.json();
    return {
      mode: 'psicat',
      answer: payload.answer || payload.body || JSON.stringify(payload, null, 2),
      raw: payload,
    };
  } catch (error) {
    psiCatSidecar = { ...psiCatSidecar, status: 'degraded', error: String(error.message || error) };
    broadcastState();
    return {
      mode: 'local-fallback',
      answer: `[Local fallback]\n${pageContext.summarizeResearchBundle({ question, state })}`,
    };
  }
}

async function handleImportResearchFiles() {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile', 'multiSelections'],
    filters: [{ name: 'Research Files', extensions: ['txt', 'md', 'json', 'html'] }],
  });
  if (result.canceled) return serializeState();
  const items = [];
  for (const filePath of result.filePaths) {
    const text = await fsp.readFile(filePath, 'utf-8');
    items.push({ title: path.basename(filePath), text, source: filePath });
  }
  state = core.importResearchItems(state, items);
  await persistState();
  if (state.sync.accountEmail) await writeSyncMirror('local-mirror');
  broadcastState();
  return serializeState();
}

async function handleExportResearchBundle() {
  const result = await dialog.showSaveDialog(mainWindow, {
    defaultPath: 'psicat-research-bundle.json',
    filters: [{ name: 'JSON', extensions: ['json'] }],
  });
  if (result.canceled || !result.filePath) return null;
  const payload = {
    exportedAt: new Date().toISOString(),
    state: serializeState(),
    context: pageContext.buildContextEnvelope(state),
  };
  await fsp.writeFile(result.filePath, JSON.stringify(payload, null, 2));
  return result.filePath;
}

async function writeSyncMirror(source = 'local-mirror') {
  const packet = core.createSyncPacket(state);
  const syncState = {
    ...state.sync,
    lastSyncAt: packet.exportedAt,
    lastSyncSource: source,
  };
  state = core.normalizeState({ ...state, sync: syncState });
  await persistState();
  await fsp.writeFile(syncMirrorPath, JSON.stringify(packet, null, 2));
  broadcastState();
  return { path: syncMirrorPath, exportedAt: packet.exportedAt };
}

async function pushSyncToBackend() {
  if (!state.sync.accountEmail) throw new Error('Sync account email is required before backend sync.');
  const endpoint = state.settings.syncBackendEndpoint || syncBackend.baseUrl;
  const packet = core.createSyncPacket(state);
  const response = await fetch(`${endpoint}/api/sync/push`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      account_email: state.sync.accountEmail,
      packet,
    }),
  });
  if (!response.ok) throw new Error(`Sync push failed with status ${response.status}`);
  const payload = await response.json();
  state = core.normalizeState({
    ...state,
    sync: {
      ...state.sync,
      lastSyncAt: payload.updated_at || packet.exportedAt,
      lastSyncSource: 'backend-push',
    },
  });
  await persistState();
  broadcastState();
  return payload;
}

async function pullSyncFromBackend() {
  if (!state.sync.accountEmail) throw new Error('Sync account email is required before backend sync.');
  const endpoint = state.settings.syncBackendEndpoint || syncBackend.baseUrl;
  const response = await fetch(`${endpoint}/api/sync/pull?account_email=${encodeURIComponent(state.sync.accountEmail)}`);
  if (response.status === 404) throw new Error('No backend sync packet found for this account.');
  if (!response.ok) throw new Error(`Sync pull failed with status ${response.status}`);
  const payload = await response.json();
  state = core.mergeSyncPacket(state, payload.packet || {});
  state = core.normalizeState({
    ...state,
    sync: {
      ...state.sync,
      lastSyncAt: payload.updated_at || new Date().toISOString(),
      lastSyncSource: 'backend-pull',
    },
  });
  ensureWorkspaceViews();
  await persistState();
  broadcastState();
  return payload;
}

async function handleExportSyncPacket() {
  const packet = core.createSyncPacket(state);
  const result = await dialog.showSaveDialog(mainWindow, {
    defaultPath: 'psicat-browser-sync.json',
    filters: [{ name: 'JSON', extensions: ['json'] }],
  });
  if (result.canceled || !result.filePath) return null;
  await fsp.writeFile(result.filePath, JSON.stringify(packet, null, 2));
  state = core.normalizeState({
    ...state,
    sync: {
      ...state.sync,
      lastSyncAt: packet.exportedAt,
      lastSyncSource: 'exported-packet',
    },
  });
  await persistState();
  broadcastState();
  return result.filePath;
}

async function handleImportSyncPacket() {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [{ name: 'JSON', extensions: ['json'] }],
  });
  if (result.canceled || !result.filePaths[0]) return serializeState();
  const packet = JSON.parse(await fsp.readFile(result.filePaths[0], 'utf-8'));
  state = core.mergeSyncPacket(state, packet);
  ensureWorkspaceViews();
  await persistState();
  broadcastState();
  return serializeState();
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1600,
    height: 980,
    backgroundColor: '#07090e',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      sandbox: true,
    },
  });
  mainWindow.loadFile(UI_ENTRY);
  mainWindow.on('resize', layoutViews);
  mainWindow.on('maximize', layoutViews);
}

function installIpc() {
  ipcMain.handle('browser:get-state', async () => serializeState());
  ipcMain.handle('browser:create-tab', async (_event, url, options) => {
    ipcCreateTab(url, options || {});
    return serializeState();
  });
  ipcMain.handle('browser:close-tab', async (_event, tabId) => {
    await closeTab(tabId);
    return serializeState();
  });
  ipcMain.handle('browser:activate-tab', async (_event, tabId) => {
    state = core.activateTab(state, tabId);
    mountTab(getActiveTab());
    return serializeState();
  });
  ipcMain.handle('browser:navigate', async (_event, url) => navigateActive('load', url));
  ipcMain.handle('browser:go-back', async () => navigateActive('back'));
  ipcMain.handle('browser:go-forward', async () => navigateActive('forward'));
  ipcMain.handle('browser:go-home', async () => navigateActive('load', state.settings.homePage));
  ipcMain.handle('browser:reload', async () => navigateActive('reload'));
  ipcMain.handle('browser:stop', async () => navigateActive('stop'));
  ipcMain.handle('browser:reopen-closed-tab', async () => reopenClosedTab());
  ipcMain.handle('browser:update-workspace-layout', async (_event, layout, secondaryTabId) => updateWorkspaceLayout(layout, secondaryTabId));
  ipcMain.handle('browser:save-workspace', async (_event, name) => saveWorkspace(name));
  ipcMain.handle('browser:apply-workspace', async (_event, workspaceId) => applyWorkspace(workspaceId));
  ipcMain.handle('browser:add-bookmark', async () => { await addBookmark(); return serializeState(); });
  ipcMain.handle('browser:remember-active-page', async () => rememberActivePage());
  ipcMain.handle('browser:add-notebook-entry', async (_event, entry) => {
    state = core.addNotebookEntry(state, entry || {});
    await persistState();
    if (state.sync.accountEmail) await writeSyncMirror('local-mirror');
    broadcastState();
    return serializeState();
  });
  ipcMain.handle('browser:update-settings', async (_event, patch) => {
    const nextPatch = patch || {};
    state = core.normalizeState({
      ...state,
      settings: { ...state.settings, ...(nextPatch.settings || nextPatch) },
      sync: nextPatch.sync ? { ...state.sync, ...nextPatch.sync } : state.sync,
    });
    await persistState();
    layoutViews();
    if (state.sync.accountEmail) await writeSyncMirror('local-mirror');
    broadcastState();
    return serializeState();
  });
  ipcMain.handle('browser:query-psicat', async (_event, payload) => callPsiCat(String((payload || {}).question || '')));
  ipcMain.handle('browser:import-research-files', async () => handleImportResearchFiles());
  ipcMain.handle('browser:export-research-bundle', async () => handleExportResearchBundle());
  ipcMain.handle('browser:export-sync-packet', async () => handleExportSyncPacket());
  ipcMain.handle('browser:import-sync-packet', async () => handleImportSyncPacket());
  ipcMain.handle('browser:sync-now', async () => {
    if (state.sync.mode === 'local-only' || !state.sync.accountEmail) return writeSyncMirror('local-mirror');
    return pushSyncToBackend();
  });
  ipcMain.handle('browser:sync-pull', async () => pullSyncFromBackend());
  ipcMain.handle('browser:open-external', async (_event, url) => shell.openExternal(url));
  ipcMain.handle('browser:open-download', async (_event, downloadPath) => shell.openPath(downloadPath));
}

app.whenReady().then(async () => {
  statePath = path.join(app.getPath('userData'), 'psicat-browser-state.json');
  syncMirrorPath = path.join(app.getPath('userData'), 'psicat-browser-sync.json');
  await loadState();
  createWindow();
  buildMenu();
  installIpc();
  await startPsiCatSidecar();
  await startSyncBackend();
  ensureWorkspaceViews();
  registerDownloadTracking(session.defaultSession);
  broadcastState();
});

app.on('window-all-closed', () => {
  if (psiCatProcess && !psiCatProcess.killed) psiCatProcess.kill();
  if (syncBackendProcess && !syncBackendProcess.killed) syncBackendProcess.kill();
  if (process.platform !== 'darwin') app.quit();
});
