const { app, BrowserWindow, BrowserView, Menu, dialog, ipcMain, shell, session } = require('electron');
const path = require('node:path');
const { mkdirSync, existsSync } = require('node:fs');
const fsp = require('node:fs/promises');
const crypto = require('node:crypto');
const core = require('./lib/browser-core');
const pageContext = require('./lib/page-context');
const syncPolicy = require('./lib/sync-policy');
const psiCatClient = require('./lib/psicat-client');
const syncTransport = require('./lib/sync-transport');
const { Sidecar, navigatorEnvironment } = require('./lib/sidecar');
const { isTrustedSender, isWebUrl } = require('./lib/desktop-boundary');
const { attachSuiteLifecycle } = require('./lib/suite-lifecycle');
const startupDiagnostics = require('./lib/startup-diagnostics').createStartupDiagnostics();

const PRODUCT_ROOT = path.resolve(__dirname, '..');
const UI_ENTRY = path.join(__dirname, 'ui', 'index.html');
const PSICAT_RUN_PATH = process.env.PSICAT_BROWSER_NAVIGATOR_RUN
  || path.resolve(PRODUCT_ROOT, '..', '20-psicat-navigator', 'run.py');
const NAVIGATOR_REPO_ROOT = process.env.PSICAT_BROWSER_NAVIGATOR_REPO_ROOT
  || path.resolve(path.dirname(PSICAT_RUN_PATH), '..', '..');
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
let syncBackend = { status: 'not_started', pid: null, baseUrl: `http://${SYNC_HOST}:${SYNC_PORT}`, error: '' };
let psiCatManager;
let syncManager;
let shutdownComplete = false;
let shuttingDown = null;
let uiReadiness = { status: 'not_started', failure_code: 'UNKNOWN' };
let startupComponent = 'ui';
const trackedSessions = new WeakSet();
const queryControllers = new Map();
const psiCatQuerySession = { cookie: '' };
const suiteLifecycle = attachSuiteLifecycle({
  enabled: process.env.PSICAT_BROWSER_SUITE_IPC === '1',
  onShutdown: () => app.quit(),
});
startupDiagnostics.mark('lifecycle-attached');

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

function broadcastState() {
  suiteLifecycle.notify('state', { sync: syncBackend, navigator: psiCatSidecar });
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
      nodeIntegration: false,
    },
  });
  registerDownloadTracking(view.webContents.session);
  view.webContents.setWindowOpenHandler(({ url }) => {
    if (!isWebUrl(url)) return { action: 'deny' };
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
    state = core.pushHistory(state, { title: view.webContents.getTitle() || tab.title, url, private: Boolean(tab.private) });
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
      private: Boolean(active.private),
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
    const tab = state.tabs.find((entry) => entry.id === tabId);
    const scopedSnapshot = { ...snapshot, private: Boolean(tab?.private) };
    state = core.updateTab(state, tabId, { lastSnapshot: scopedSnapshot });
    state = core.rememberPage(state, scopedSnapshot);
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
  state = core.addBookmark(state, { title: snapshot.title || active.title, url: snapshot.url || active.url, private: Boolean(active.private) });
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
  psiCatManager ||= new Sidecar({
    name: 'PsiCat Navigator', script: PSICAT_RUN_PATH, port: PSICAT_PORT,
    args: ['--no-open', '--local-execution', 'off'],
    healthPath: '/api/psicat/status',
    validateHealth: (payload) => payload.psicat_available === true && typeof payload.memory_profile_token === 'string',
    timeoutMs: 30_000,
    env: navigatorEnvironment(process.env, NAVIGATOR_REPO_ROOT),
    onChange: (next) => { psiCatSidecar = next; broadcastState(); },
  });
  await psiCatManager.start({
    enabled: state.settings.autoStartPsiCat && process.env.PSICAT_BROWSER_DISABLE_NAVIGATOR !== '1',
  });
}

async function startSyncBackend() {
  if (!syncManager) {
    const instanceId = crypto.randomUUID();
    syncManager = new Sidecar({
      name: 'Browser sync backend', script: SYNC_BACKEND_RUN_PATH, port: SYNC_PORT,
      args: ['--store', path.join(app.getPath('userData'), 'sync-backend', 'sync_store.json'), '--instance-id', instanceId],
      healthPath: '/api/sync/health',
      validateHealth: (payload) => payload.ok === true && payload.service === 'psicat-sync-backend' && payload.instance_id === instanceId,
      onChange: (next) => { syncBackend = next; broadcastState(); },
    });
  }
  await syncManager.start();
}

async function callPsiCat({ question, requestId, includeLibrary = false }) {
  let body;
  try {
    body = psiCatClient.buildPageQuery({ state, question, requestId, includeLibrary });
  } catch (error) {
    return { mode: 'blocked', request_id: requestId, answer: `Query blocked: ${error.message}` };
  }
  if (!['ready', 'degraded'].includes(psiCatSidecar.status) || !psiCatManager?.child) {
    return {
      mode: 'local',
      request_id: requestId,
      answer: `[Local research only; PsiCat unavailable: ${psiCatSidecar.error || psiCatSidecar.status}]\n${pageContext.summarizeResearchBundle({ question, state })}`,
    };
  }
  if (queryControllers.size) return { mode: 'blocked', request_id: requestId, answer: 'A PsiCat query is already running.' };
  const controller = new AbortController();
  queryControllers.set(requestId, controller);
  try {
    const result = await psiCatClient.queryPsiCat({
      baseUrl: psiCatSidecar.baseUrl, body, signal: controller.signal, session: psiCatQuerySession,
    });
    psiCatSidecar = { ...psiCatSidecar, status: 'ready', error: '' };
    broadcastState();
    return result;
  } catch (error) {
    if (controller.signal.aborted) {
      return { mode: 'cancelled', request_id: requestId, answer: 'Query cancelled locally. Server work may already have begun.' };
    }
    psiCatSidecar = { ...psiCatSidecar, status: 'degraded', error: String(error.message || error) };
    broadcastState();
    return {
      mode: 'local-fallback',
      request_id: requestId,
      answer: `[PsiCat failed: ${error.message || error}; local research fallback only]\n${pageContext.summarizeResearchBundle({ question, state })}`,
    };
  } finally {
    queryControllers.delete(requestId);
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
  if (syncBackend.status !== 'ready') throw new Error(`Sync backend unavailable: ${syncBackend.error || syncBackend.status}`);
  const endpoint = state.settings.syncBackendEndpoint || syncBackend.baseUrl;
  const result = await syncTransport.pushSyncToBackend({ state, endpoint, core, getState: () => state });
  state = result.state;
  await persistState();
  broadcastState();
  return result.payload;
}

async function pullSyncFromBackend() {
  if (syncBackend.status !== 'ready') throw new Error(`Sync backend unavailable: ${syncBackend.error || syncBackend.status}`);
  const endpoint = state.settings.syncBackendEndpoint || syncBackend.baseUrl;
  const result = await syncTransport.pullSyncFromBackend({ state, endpoint, core, getState: () => state });
  state = result.state;
  ensureWorkspaceViews();
  await persistState();
  broadcastState();
  return result.payload;
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
  uiReadiness = { status: 'starting', failure_code: 'UNKNOWN' };
  mainWindow = new BrowserWindow({
    width: 1600,
    height: 980,
    backgroundColor: '#07090e',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      sandbox: true,
      nodeIntegration: false,
    },
  });
  const loaded = mainWindow.loadFile(UI_ENTRY).then(() => {
    uiReadiness = { status: 'ready', failure_code: 'UNKNOWN' };
  }, (error) => {
    uiReadiness = { status: 'failed', failure_code: 'UI_LOAD_FAILED' };
    throw error;
  });
  mainWindow.webContents.on('will-navigate', (event) => event.preventDefault());
  mainWindow.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  mainWindow.on('resize', layoutViews);
  mainWindow.on('maximize', layoutViews);
  return loaded;
}

function installIpc() {
  const handle = (channel, listener) => ipcMain.handle(channel, (event, ...args) => {
    if (!isTrustedSender(event, mainWindow, UI_ENTRY)) throw new Error('Browser IPC requires the local desktop UI main frame.');
    return listener(event, ...args);
  });
  handle('browser:get-state', async () => serializeState());
  handle('browser:create-tab', async (_event, url, options) => {
    ipcCreateTab(url, options || {});
    return serializeState();
  });
  handle('browser:close-tab', async (_event, tabId) => {
    await closeTab(tabId);
    return serializeState();
  });
  handle('browser:activate-tab', async (_event, tabId) => {
    state = core.activateTab(state, tabId);
    mountTab(getActiveTab());
    return serializeState();
  });
  handle('browser:navigate', async (_event, url) => navigateActive('load', url));
  handle('browser:go-back', async () => navigateActive('back'));
  handle('browser:go-forward', async () => navigateActive('forward'));
  handle('browser:go-home', async () => navigateActive('load', state.settings.homePage));
  handle('browser:reload', async () => navigateActive('reload'));
  handle('browser:stop', async () => navigateActive('stop'));
  handle('browser:reopen-closed-tab', async () => reopenClosedTab());
  handle('browser:update-workspace-layout', async (_event, layout, secondaryTabId) => updateWorkspaceLayout(layout, secondaryTabId));
  handle('browser:save-workspace', async (_event, name) => saveWorkspace(name));
  handle('browser:apply-workspace', async (_event, workspaceId) => applyWorkspace(workspaceId));
  handle('browser:add-bookmark', async () => { await addBookmark(); return serializeState(); });
  handle('browser:remember-active-page', async () => rememberActivePage());
  handle('browser:add-notebook-entry', async (_event, entry) => {
    state = core.addNotebookEntry(state, entry || {});
    await persistState();
    if (state.sync.accountEmail) await writeSyncMirror('local-mirror');
    broadcastState();
    return serializeState();
  });
  handle('browser:update-settings', async (_event, patch) => {
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
  handle('browser:query-psicat', async (_event, payload) => callPsiCat({
    question: String(payload?.question || ''),
    requestId: payload?.requestId || crypto.randomUUID(),
    includeLibrary: payload?.includeLibrary === true,
  }));
  handle('browser:cancel-psicat', (_event, requestId) => {
    const controller = queryControllers.get(requestId);
    if (!controller) return false;
    controller.abort();
    return true;
  });
  handle('browser:import-research-files', async () => handleImportResearchFiles());
  handle('browser:export-research-bundle', async () => handleExportResearchBundle());
  handle('browser:export-sync-packet', async () => handleExportSyncPacket());
  handle('browser:import-sync-packet', async () => handleImportSyncPacket());
  handle('browser:sync-now', async () => {
    if (!syncPolicy.shouldUseBackendSync(state)) return writeSyncMirror('local-mirror');
    return pushSyncToBackend();
  });
  handle('browser:sync-pull', async () => {
    if (!syncPolicy.shouldUseBackendSync(state)) {
      return { skipped: true, message: 'Local-only mode leaves remote pull disabled.' };
    }
    return pullSyncFromBackend();
  });
  handle('browser:open-external', async (_event, url) => {
    if (!isWebUrl(url)) throw new Error('Only HTTP(S) external URLs are supported.');
    return shell.openExternal(url);
  });
  handle('browser:open-download', async (_event, downloadPath) => {
    if (!state.downloads.some((download) => download.savePath === downloadPath)) throw new Error('Unknown browser download.');
    return shell.openPath(downloadPath);
  });
}

if (process.env.PSICAT_BROWSER_USER_DATA) {
  if (!path.isAbsolute(process.env.PSICAT_BROWSER_USER_DATA)) throw new Error('PSICAT_BROWSER_USER_DATA must be an absolute writable directory.');
  mkdirSync(process.env.PSICAT_BROWSER_USER_DATA, { recursive: true });
  app.setPath('userData', process.env.PSICAT_BROWSER_USER_DATA);
}

if (process.env.PSICAT_BROWSER_NAVIGATOR_RUN && !path.isAbsolute(PSICAT_RUN_PATH)) {
  throw new Error('PSICAT_BROWSER_NAVIGATOR_RUN must be an absolute run.py path.');
}
if (!path.isAbsolute(NAVIGATOR_REPO_ROOT)) throw new Error('PSICAT_BROWSER_NAVIGATOR_REPO_ROOT must be an absolute repository source root.');

const ownsInstance = app.requestSingleInstanceLock();
startupDiagnostics.mark(ownsInstance ? 'instance-owned' : 'instance-rejected');
if (!ownsInstance) {
  suiteLifecycle.notify('startup-failed', { error: 'Another Product 24 instance owns this user-data directory.' }).then(() => app.quit());
}

app.whenReady().then(async () => {
  if (!ownsInstance) return;
  startupDiagnostics.mark('electron-ready');
  statePath = path.join(app.getPath('userData'), 'psicat-browser-state.json');
  syncMirrorPath = path.join(app.getPath('userData'), 'psicat-browser-sync.json');
  await loadState();
  startupDiagnostics.mark('state-loaded');
  if (shuttingDown || shutdownComplete) return;
  buildMenu();
  installIpc();
  await Promise.all([createWindow(), startPsiCatSidecar(), startSyncBackend()]);
  startupDiagnostics.mark('ui-and-sidecars-settled');
  if (shuttingDown) return;
  ensureWorkspaceViews();
  registerDownloadTracking(session.defaultSession);
  broadcastState();
  if (suiteLifecycle.enabled) {
    if (syncBackend.status !== 'ready') {
      startupComponent = 'sync';
      throw new Error('Required sync sidecar failed.');
    }
    if (psiCatSidecar.status !== 'disabled' && psiCatSidecar.status !== 'ready') {
      startupComponent = 'navigator';
      throw new Error('Enabled Navigator sidecar failed.');
    }
    await suiteLifecycle.notify('ready', { sync: syncBackend, navigator: psiCatSidecar });
    startupDiagnostics.mark('suite-ready');
  }
}).catch(async (error) => {
  const resources = [
    ['run.py', PSICAT_RUN_PATH],
    ['ox_navigator/app/server.py', path.join(path.dirname(PSICAT_RUN_PATH), 'ox_navigator', 'app', 'server.py')],
    ['ox_navigator/engine/merlin_benchmark.py', path.join(path.dirname(PSICAT_RUN_PATH), 'ox_navigator', 'engine', 'merlin_benchmark.py')],
    ['src/infrastructure/execution_spine.py', path.join(NAVIGATOR_REPO_ROOT, 'src', 'infrastructure', 'execution_spine.py')],
    ['bot/assistant_api.py', path.join(NAVIGATOR_REPO_ROOT, 'bot', 'assistant_api.py')],
    ['bot/rag_index.py', path.join(NAVIGATOR_REPO_ROOT, 'bot', 'rag_index.py')],
    ['bot/__init__.py', path.join(NAVIGATOR_REPO_ROOT, 'bot', '__init__.py')],
    ['bot/session_bootstrap.py', path.join(NAVIGATOR_REPO_ROOT, 'bot', 'session_bootstrap.py')],
    ['bot/research_resources.py', path.join(NAVIGATOR_REPO_ROOT, 'bot', 'research_resources.py')],
    ['ui/interrogator-kb.json', path.join(path.dirname(PSICAT_RUN_PATH), 'ui', 'interrogator-kb.json')],
    ['9-INFRASTRUCTURE/ox_full_context.md', path.join(NAVIGATOR_REPO_ROOT, '9-INFRASTRUCTURE', 'ox_full_context.md')],
    ['sync_backend/server.py', SYNC_BACKEND_RUN_PATH],
    ['desktop/ui/index.html', UI_ENTRY],
    ['desktop/ui/app.js', path.join(__dirname, 'ui', 'app.js')],
    ['desktop/ui/app.css', path.join(__dirname, 'ui', 'app.css')],
  ].map(([resource, file]) => ({ resource, exists: existsSync(file) }));
  await startupDiagnostics.failure(error, {
    component: startupComponent, components: { ui: uiReadiness, sync: syncBackend, navigator: psiCatSidecar }, resources,
  });
  if (!suiteLifecycle.enabled) dialog.showErrorBox('PsiCat Browser startup failed', String(error.message || error));
  app.quit();
});

async function stopSidecars() {
  psiCatQuerySession.cookie = '';
  for (const controller of queryControllers.values()) controller.abort();
  const results = await Promise.allSettled([psiCatManager?.stop(), syncManager?.stop()]);
  const failure = results.find((result) => result.status === 'rejected');
  if (failure) throw failure.reason;
}

app.on('before-quit', (event) => {
  if (shutdownComplete) return;
  event.preventDefault();
  shuttingDown ||= stopSidecars().then(async () => {
    shutdownComplete = true;
    await suiteLifecycle.notify('stopped', { sync: syncBackend, navigator: psiCatSidecar });
    app.quit();
  }).catch(async (error) => {
    shuttingDown = null;
    await suiteLifecycle.notify('shutdown-failed', { error: error.message || error, sync: syncBackend, navigator: psiCatSidecar });
    if (!suiteLifecycle.enabled) dialog.showErrorBox('PsiCat Browser cleanup failed', String(error.message || error));
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
  else stopSidecars().catch((error) => dialog.showErrorBox('PsiCat Browser cleanup failed', error.message));
});

app.on('activate', async () => {
  if (BrowserWindow.getAllWindows().length || shuttingDown) return;
  tabViews.clear();
  await Promise.all([createWindow(), startPsiCatSidecar(), startSyncBackend()]);
  if (shuttingDown) return;
  ensureWorkspaceViews();
  broadcastState();
});
