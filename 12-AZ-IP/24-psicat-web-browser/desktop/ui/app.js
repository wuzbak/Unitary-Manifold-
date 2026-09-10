let state = null;

function byId(id) {
  return document.getElementById(id);
}

function itemCard(title, body, meta = '') {
  const div = document.createElement('div');
  div.className = 'list-item';
  const strong = document.createElement('strong');
  strong.textContent = title;
  const bodyDiv = document.createElement('div');
  bodyDiv.textContent = body;
  div.append(strong, bodyDiv);
  if (meta) {
    const metaDiv = document.createElement('div');
    metaDiv.className = 'muted';
    metaDiv.textContent = meta;
    div.appendChild(metaDiv);
  }
  return div;
}

function actionButton(label, handler) {
  const button = document.createElement('button');
  button.type = 'button';
  button.textContent = label;
  button.addEventListener('click', handler);
  return button;
}

function renderTabs() {
  const strip = byId('tab-strip');
  strip.innerHTML = '';
  state.tabs.forEach((tab) => {
    const div = document.createElement('div');
    div.className = `tab ${tab.id === state.activeTabId ? 'active' : ''} ${tab.id === state.workspace?.secondaryTabId ? 'workspace-secondary' : ''}`;
    const title = document.createElement('span');
    title.textContent = `${tab.private ? '🕶️ ' : ''}${tab.title || tab.url}`;
    const button = document.createElement('button');
    button.dataset.close = tab.id;
    button.textContent = '×';
    button.setAttribute('aria-label', `Close ${tab.title || tab.url}`);
    div.append(title, button);
    div.addEventListener('click', async (event) => {
      if (event.target.dataset.close) return;
      await window.psicatBrowser.activateTab(tab.id);
    });
    button.addEventListener('click', async (event) => {
      event.stopPropagation();
      await window.psicatBrowser.closeTab(tab.id);
    });
    strip.appendChild(div);
  });
}

function renderCurrentPage() {
  const active = state.tabs.find((tab) => tab.id === state.activeTabId);
  byId('address').value = active?.url || '';
  const snapshot = active?.lastSnapshot;
  const wrap = byId('current-page');
  wrap.innerHTML = '';
  wrap.appendChild(snapshot
    ? itemCard(snapshot.title || active.title, (snapshot.selection || snapshot.text || '').slice(0, 420), snapshot.url)
    : itemCard(active?.title || 'New Tab', 'No captured page context yet.', active?.url || ''));
}

function renderList(id, entries, mapper) {
  const wrap = byId(id);
  wrap.innerHTML = '';
  if (!entries.length) {
    const empty = document.createElement('div');
    empty.className = 'muted';
    empty.textContent = 'Nothing here yet.';
    wrap.appendChild(empty);
    return;
  }
  entries.forEach((entry) => wrap.appendChild(mapper(entry)));
}

function renderSettings() {
  const settings = state.settings;
  byId('setting-homePage').value = settings.homePage;
  byId('setting-searchEngine').value = settings.searchEngine;
  byId('setting-sidebarWidth').value = settings.sidebarWidth;
  byId('setting-trackProtection').value = settings.trackProtection;
  byId('setting-psicatEndpoint').value = settings.psicatEndpoint;
  byId('setting-syncBackendEndpoint').value = settings.syncBackendEndpoint || '';
  byId('setting-syncAccessToken').value = settings.syncAccessToken || '';
  byId('setting-accountEmail').value = state.sync.accountEmail || '';
  byId('setting-syncMode').value = state.sync.mode || 'local+account';
  byId('setting-autoStartPsiCat').checked = settings.autoStartPsiCat;
  byId('setting-livePageCapture').checked = settings.livePageCapture;
  byId('workspace-layout').value = state.workspace?.layout || 'single';
  document.documentElement.style.setProperty('--sidebar-width', `${settings.sidebarWidth}px`);
}

function renderWorkspaceControls() {
  const select = byId('workspace-secondary');
  select.innerHTML = '';
  const empty = document.createElement('option');
  empty.value = '';
  empty.textContent = 'No secondary tab';
  select.appendChild(empty);
  state.tabs.filter((tab) => tab.id !== state.activeTabId).forEach((tab) => {
    const option = document.createElement('option');
    option.value = tab.id;
    option.textContent = tab.title || tab.url;
    select.appendChild(option);
  });
  select.value = state.workspace?.secondaryTabId || '';
}

function renderBookmarkList() {
  renderList('bookmarks', state.bookmarks || [], (entry) => {
    const card = itemCard(entry.title || entry.url, entry.url);
    card.appendChild(actionButton('Open', () => window.psicatBrowser.navigate(entry.url)));
    return card;
  });
}

function renderHistoryList() {
  renderList('history', (state.history || []).slice(0, 20), (entry) => {
    const card = itemCard(entry.title || entry.url, entry.url, entry.visitedAt);
    card.appendChild(actionButton('Open', () => window.psicatBrowser.navigate(entry.url)));
    return card;
  });
}

function renderDownloadsList() {
  renderList('downloads', (state.downloads || []).slice(0, 20), (entry) => {
    const card = itemCard(entry.fileName || entry.url, entry.url, entry.savePath || entry.createdAt || '');
    if (entry.savePath) card.appendChild(actionButton('Open file', () => window.psicatBrowser.openDownload(entry.savePath)));
    return card;
  });
}

function renderImportedResearch() {
  renderList('imported-research', (state.importedResearch || []).slice(0, 16), (entry) => {
    const card = itemCard(entry.title || 'Imported item', entry.text.slice(0, 220), entry.source || '');
    if (entry.source && /^https?:/i.test(entry.source)) {
      card.appendChild(actionButton('Open source', () => window.psicatBrowser.openExternal(entry.source)));
    }
    return card;
  });
}

function renderSyncProfile() {
  const sync = state.sync || {};
  renderList('sync-profile', [{
    title: sync.accountEmail || 'Local-only profile',
    body: `Mode: ${sync.mode || 'local+account'}`,
    meta: `Last sync: ${sync.lastSyncAt || 'Never'} · Source: ${sync.lastSyncSource || 'never'} · Backend: ${state.syncBackend?.status || 'unknown'}`,
  }], (entry) => itemCard(entry.title, entry.body, entry.meta));
}

function renderSavedWorkspaces() {
  renderList('saved-workspaces', state.workspace?.savedLayouts || [], (entry) => {
    const card = itemCard(entry.name, `Layout: ${entry.layout} · Tabs: ${(entry.tabUrls || []).length}`, entry.createdAt);
    card.appendChild(actionButton('Open', () => window.psicatBrowser.applyWorkspace(entry.id)));
    return card;
  });
}

function render() {
  if (!state) return;
  renderTabs();
  renderCurrentPage();
  renderSettings();
  renderWorkspaceControls();
  byId('sidecar-status').textContent = `PsiCat: ${state.psiCatSidecar.status}${state.psiCatSidecar.error ? ` — ${state.psiCatSidecar.error}` : ''} | Sync backend: ${state.syncBackend?.status || 'unknown'}${state.syncBackend?.error ? ` — ${state.syncBackend.error}` : ''}`;
  renderList('notebook-list', state.notebookEntries || [], (entry) => itemCard(entry.title || 'Note', entry.text.slice(0, 240), entry.createdAt));
  renderList('remembered-pages', state.rememberedPages || [], (entry) => itemCard(entry.title || entry.url, (entry.selection || entry.text || '').slice(0, 220), entry.url));
  renderSyncProfile();
  renderSavedWorkspaces();
  renderBookmarkList();
  renderHistoryList();
  renderDownloadsList();
  renderImportedResearch();
}

async function boot() {
  state = await window.psicatBrowser.getState();
  render();
  window.psicatBrowser.onState((next) => {
    state = next;
    render();
  });

  byId('address-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    await window.psicatBrowser.navigate(byId('address').value);
  });
  byId('back').onclick = () => window.psicatBrowser.goBack();
  byId('forward').onclick = () => window.psicatBrowser.goForward();
  byId('home').onclick = () => window.psicatBrowser.goHome();
  byId('reload').onclick = () => window.psicatBrowser.reload();
  byId('stop').onclick = () => window.psicatBrowser.stop();
  byId('new-tab').onclick = () => window.psicatBrowser.createTab(state.settings.homePage, {});
  byId('private-tab').onclick = () => window.psicatBrowser.createTab(state.settings.homePage, { private: true });
  byId('reopen-tab').onclick = () => window.psicatBrowser.reopenClosedTab();
  byId('bookmark').onclick = () => window.psicatBrowser.addBookmark();
  byId('toggle-settings').onclick = () => byId('settings-panel').classList.toggle('hidden');
  byId('save-note').onclick = () => window.psicatBrowser.addNotebookEntry({ title: byId('note-title').value.trim() || 'Notebook note', text: byId('note-text').value.trim() });
  byId('remember-page').onclick = () => window.psicatBrowser.rememberActivePage();
  byId('sync-now').onclick = async () => {
    const result = await window.psicatBrowser.syncNow();
    byId('answer').textContent = result.path
      ? `Sync mirror updated: ${result.path}`
      : `Backend sync pushed at ${result.updated_at || new Date().toISOString()}`;
  };
  byId('sync-pull').onclick = async () => {
    const result = await window.psicatBrowser.syncPull();
    byId('answer').textContent = `Backend sync pulled from ${result.updated_at || 'remote store'}`;
  };
  byId('import-research').onclick = () => window.psicatBrowser.importResearchFiles();
  byId('export-research').onclick = () => window.psicatBrowser.exportResearchBundle();
  byId('import-sync').onclick = () => window.psicatBrowser.importSyncPacket();
  byId('export-sync').onclick = () => window.psicatBrowser.exportSyncPacket();
  byId('workspace-layout').onchange = () => window.psicatBrowser.updateWorkspaceLayout(byId('workspace-layout').value, byId('workspace-secondary').value || null);
  byId('workspace-secondary').onchange = () => window.psicatBrowser.updateWorkspaceLayout(byId('workspace-layout').value, byId('workspace-secondary').value || null);
  byId('save-workspace').onclick = async () => {
    const name = window.prompt('Workspace name', 'Research split');
    if (name !== null) await window.psicatBrowser.saveWorkspace(name);
  };
  byId('ask-psicat').onclick = async () => {
    const question = byId('question').value.trim();
    if (!question) return;
    byId('answer').textContent = 'Thinking…';
    const answer = await window.psicatBrowser.queryPsiCat({ question });
    byId('answer').textContent = answer.answer || JSON.stringify(answer, null, 2);
  };
  byId('save-settings').onclick = async () => {
    await window.psicatBrowser.updateSettings({
      settings: {
        homePage: byId('setting-homePage').value.trim(),
        searchEngine: byId('setting-searchEngine').value.trim(),
        sidebarWidth: Number(byId('setting-sidebarWidth').value || 420),
        trackProtection: byId('setting-trackProtection').value,
        psicatEndpoint: byId('setting-psicatEndpoint').value.trim(),
        syncBackendEndpoint: byId('setting-syncBackendEndpoint').value.trim(),
        syncAccessToken: byId('setting-syncAccessToken').value.trim(),
        autoStartPsiCat: byId('setting-autoStartPsiCat').checked,
        livePageCapture: byId('setting-livePageCapture').checked,
      },
      sync: {
        accountEmail: byId('setting-accountEmail').value.trim(),
        mode: byId('setting-syncMode').value,
      },
    });
  };
}

boot();
