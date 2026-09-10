let state = null;

function byId(id) {
  return document.getElementById(id);
}

function itemCard(title, body, meta = '') {
  return `<div class="list-item"><strong>${title}</strong><div>${body}</div>${meta ? `<div class="muted">${meta}</div>` : ''}</div>`;
}

function renderTabs() {
  const strip = byId('tab-strip');
  strip.innerHTML = '';
  state.tabs.forEach((tab) => {
    const div = document.createElement('div');
    div.className = `tab ${tab.id === state.activeTabId ? 'active' : ''}`;
    div.innerHTML = `<span>${tab.private ? '🕶️ ' : ''}${tab.title || tab.url}</span><button data-close="${tab.id}">×</button>`;
    div.addEventListener('click', async (event) => {
      if (event.target.dataset.close) return;
      await window.psicatBrowser.activateTab(tab.id);
    });
    div.querySelector('button').addEventListener('click', async (event) => {
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
  byId('current-page').innerHTML = snapshot
    ? itemCard(snapshot.title || active.title, (snapshot.selection || snapshot.text || '').slice(0, 420), snapshot.url)
    : itemCard(active?.title || 'New Tab', 'No captured page context yet.', active?.url || '');
}

function renderList(id, entries, mapper) {
  const wrap = byId(id);
  wrap.innerHTML = entries.length ? entries.map(mapper).join('') : '<div class="muted">Nothing here yet.</div>';
}

function renderSettings() {
  const settings = state.settings;
  byId('setting-homePage').value = settings.homePage;
  byId('setting-searchEngine').value = settings.searchEngine;
  byId('setting-sidebarWidth').value = settings.sidebarWidth;
  byId('setting-trackProtection').value = settings.trackProtection;
  byId('setting-psicatEndpoint').value = settings.psicatEndpoint;
  byId('setting-autoStartPsiCat').checked = settings.autoStartPsiCat;
  byId('setting-livePageCapture').checked = settings.livePageCapture;
  document.documentElement.style.setProperty('--sidebar-width', `${settings.sidebarWidth}px`);
}

function render() {
  if (!state) return;
  renderTabs();
  renderCurrentPage();
  renderSettings();
  byId('sidecar-status').textContent = `PsiCat status: ${state.psiCatSidecar.status}${state.psiCatSidecar.error ? ` — ${state.psiCatSidecar.error}` : ''}`;
  renderList('notebook-list', state.notebookEntries || [], (entry) => itemCard(entry.title || 'Note', entry.text.slice(0, 240), entry.createdAt));
  renderList('remembered-pages', state.rememberedPages || [], (entry) => itemCard(entry.title || entry.url, (entry.selection || entry.text || '').slice(0, 220), entry.url));
  renderList('bookmarks', state.bookmarks || [], (entry) => itemCard(entry.title || entry.url, entry.url));
  renderList('history', (state.history || []).slice(0, 20), (entry) => itemCard(entry.title || entry.url, entry.url, entry.visitedAt));
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
  byId('reload').onclick = () => window.psicatBrowser.reload();
  byId('stop').onclick = () => window.psicatBrowser.stop();
  byId('new-tab').onclick = () => window.psicatBrowser.createTab(state.settings.homePage, {});
  byId('private-tab').onclick = () => window.psicatBrowser.createTab(state.settings.homePage, { private: true });
  byId('bookmark').onclick = () => window.psicatBrowser.addBookmark();
  byId('toggle-settings').onclick = () => byId('settings-panel').classList.toggle('hidden');
  byId('save-note').onclick = () => window.psicatBrowser.addNotebookEntry({ title: byId('note-title').value.trim() || 'Notebook note', text: byId('note-text').value.trim() });
  byId('remember-page').onclick = () => window.psicatBrowser.addNotebookEntry({ title: `Remembered research — ${new Date().toLocaleString()}`, text: (state.tabs.find((tab) => tab.id === state.activeTabId)?.lastSnapshot?.text || '').slice(0, 2000), tags: ['captured-page'] });
  byId('import-research').onclick = () => window.psicatBrowser.importResearchFiles();
  byId('export-research').onclick = () => window.psicatBrowser.exportResearchBundle();
  byId('ask-psicat').onclick = async () => {
    const question = byId('question').value.trim();
    if (!question) return;
    byId('answer').textContent = 'Thinking…';
    const answer = await window.psicatBrowser.queryPsiCat({ question });
    byId('answer').textContent = answer.answer || JSON.stringify(answer, null, 2);
  };
  byId('save-settings').onclick = async () => {
    await window.psicatBrowser.updateSettings({
      homePage: byId('setting-homePage').value.trim(),
      searchEngine: byId('setting-searchEngine').value.trim(),
      sidebarWidth: Number(byId('setting-sidebarWidth').value || 420),
      trackProtection: byId('setting-trackProtection').value,
      psicatEndpoint: byId('setting-psicatEndpoint').value.trim(),
      autoStartPsiCat: byId('setting-autoStartPsiCat').checked,
      livePageCapture: byId('setting-livePageCapture').checked,
    });
  };
}

boot();
