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
const PSICAT_HOST = '127.0.0.1';
const PSICAT_PORT = 8020;

let mainWindow;
let statePath;
let state = core.createInitialState();
let tabViews = new Map();
let psiCatSidecar = { status: 'not_started', pid: null, baseUrl: `http://${PSICAT_HOST}:${PSICAT_PORT}`, error: '' };
let psiCatProcess = null;

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
  return { ...state, psiCatSidecar };
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
  for (const [tabId, view] of tabViews.entries()) {
    if (tabId !== active.id) {
      view.setBounds({ x: 0, y: 0, width: 0, height: 0 });
      continue;
    }
    view.setBounds({ x: 0, y: toolbarHeight, width: bounds.width - sidebarWidth, height: Math.max(200, bounds.height - toolbarHeight) });
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

async function addBookmark() {
  const active = getActiveTab();
  if (!active) return;
  const snapshot = active.lastSnapshot || {};
  state = core.addBookmark(state, { title: snapshot.title || active.title, url: snapshot.url || active.url });
  await persistState();
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
  psiCatSidecar = { ...psiCatSidecar, status: 'ready', pid: psiCatProcess.pid };
  psiCatProcess.on('exit', (code) => {
    psiCatSidecar = { ...psiCatSidecar, status: 'stopped', error: code === 0 ? '' : `PsiCat sidecar exited with code ${code}` };
    broadcastState();
  });
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
  ipcMain.handle('browser:reload', async () => navigateActive('reload'));
  ipcMain.handle('browser:stop', async () => navigateActive('stop'));
  ipcMain.handle('browser:add-bookmark', async () => { await addBookmark(); return serializeState(); });
  ipcMain.handle('browser:add-notebook-entry', async (_event, entry) => {
    state = core.addNotebookEntry(state, entry || {});
    await persistState();
    broadcastState();
    return serializeState();
  });
  ipcMain.handle('browser:update-settings', async (_event, patch) => {
    state = core.normalizeState({ ...state, settings: { ...state.settings, ...(patch || {}) } });
    await persistState();
    layoutViews();
    broadcastState();
    return serializeState();
  });
  ipcMain.handle('browser:query-psicat', async (_event, payload) => callPsiCat(String((payload || {}).question || '')));
  ipcMain.handle('browser:import-research-files', async () => handleImportResearchFiles());
  ipcMain.handle('browser:export-research-bundle', async () => handleExportResearchBundle());
  ipcMain.handle('browser:open-external', async (_event, url) => shell.openExternal(url));
}

app.whenReady().then(async () => {
  statePath = path.join(app.getPath('userData'), 'psicat-browser-state.json');
  await loadState();
  createWindow();
  buildMenu();
  installIpc();
  await startPsiCatSidecar();
  for (const tab of state.tabs) {
    if (tab.id === state.activeTabId) {
      mountTab(tab);
      break;
    }
  }
  const active = getActiveTab();
  if (active && !tabViews.has(active.id)) mountTab(active);
  session.defaultSession.on('will-download', (_event, item) => {
    state = core.addDownload(state, {
      url: item.getURL(),
      fileName: item.getFilename(),
      savePath: item.getSavePath(),
      totalBytes: item.getTotalBytes(),
    });
    persistState().then(broadcastState);
  });
  broadcastState();
});

app.on('window-all-closed', () => {
  if (psiCatProcess && !psiCatProcess.killed) psiCatProcess.kill();
  if (process.platform !== 'darwin') app.quit();
});
