const crypto = require('node:crypto');

const DEFAULT_HOME = 'https://example.com';
const MAX_REMEMBERED_PAGES = 48;
const MAX_NOTEBOOK_ENTRIES = 200;
const MAX_HISTORY_ENTRIES = 250;
const MAX_IMPORT_ITEMS = 120;

function createDefaultSettings() {
  return {
    homePage: DEFAULT_HOME,
    searchEngine: 'https://duckduckgo.com/?q=%s',
    theme: 'dark',
    sidebarWidth: 420,
    rememberSessions: true,
    trackProtection: 'standard',
    downloadBehavior: 'ask',
    notebookAutosave: true,
    localResearchRetention: 'persistent',
    psicatEndpoint: 'http://127.0.0.1:8020',
    autoStartPsiCat: true,
    livePageCapture: true,
  };
}

function createTab(url = DEFAULT_HOME, options = {}) {
  return {
    id: crypto.randomUUID(),
    url,
    title: options.title || 'New Tab',
    private: Boolean(options.private),
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    loading: false,
    canGoBack: false,
    canGoForward: false,
    lastSnapshot: null,
  };
}

function createInitialState() {
  const settings = createDefaultSettings();
  const firstTab = createTab(settings.homePage);
  return {
    version: 1,
    tabs: [firstTab],
    activeTabId: firstTab.id,
    bookmarks: [],
    history: [],
    downloads: [],
    notebookEntries: [],
    rememberedPages: [],
    importedResearch: [],
    settings,
    sync: {
      mode: 'local+account',
      accountEmail: '',
      lastSyncAt: null,
    },
  };
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function normalizeState(state) {
  if (!state || typeof state !== 'object') return createInitialState();
  const merged = {
    ...createInitialState(),
    ...clone(state),
    settings: {
      ...createDefaultSettings(),
      ...(state.settings || {}),
    },
    sync: {
      mode: 'local+account',
      accountEmail: '',
      lastSyncAt: null,
      ...(state.sync || {}),
    },
  };
  if (!Array.isArray(merged.tabs) || !merged.tabs.length) {
    const fresh = createInitialState();
    merged.tabs = fresh.tabs;
    merged.activeTabId = fresh.activeTabId;
  }
  if (!merged.tabs.some((tab) => tab.id === merged.activeTabId)) {
    merged.activeTabId = merged.tabs[0].id;
  }
  return merged;
}

function sanitizeUrl(input, settings = createDefaultSettings()) {
  const raw = String(input || '').trim();
  if (!raw) return settings.homePage || DEFAULT_HOME;
  if (/^[a-zA-Z]+:\/\//.test(raw)) return raw;
  if (/^(localhost|\d+\.\d+\.\d+\.\d+|[\w.-]+\.[a-z]{2,})(:\d+)?(\/.*)?$/i.test(raw)) {
    return `https://${raw}`;
  }
  const encoded = encodeURIComponent(raw);
  return String(settings.searchEngine || createDefaultSettings().searchEngine).replace('%s', encoded);
}

function addTab(state, url, options = {}) {
  const next = normalizeState(state);
  const tab = createTab(sanitizeUrl(url, next.settings), options);
  next.tabs.push(tab);
  next.activeTabId = tab.id;
  return next;
}

function activateTab(state, tabId) {
  const next = normalizeState(state);
  if (next.tabs.some((tab) => tab.id === tabId)) next.activeTabId = tabId;
  return next;
}

function closeTab(state, tabId) {
  const next = normalizeState(state);
  if (next.tabs.length === 1) return next;
  const index = next.tabs.findIndex((tab) => tab.id === tabId);
  if (index === -1) return next;
  next.tabs.splice(index, 1);
  if (next.activeTabId === tabId) {
    next.activeTabId = next.tabs[Math.max(0, index - 1)].id;
  }
  return next;
}

function updateTab(state, tabId, patch) {
  const next = normalizeState(state);
  next.tabs = next.tabs.map((tab) => tab.id === tabId ? { ...tab, ...patch, updatedAt: new Date().toISOString() } : tab);
  return next;
}

function pushHistory(state, entry) {
  const next = normalizeState(state);
  const history = [
    {
      id: crypto.randomUUID(),
      visitedAt: new Date().toISOString(),
      ...entry,
    },
    ...next.history.filter((item) => item.url !== entry.url),
  ];
  next.history = history.slice(0, MAX_HISTORY_ENTRIES);
  return next;
}

function rememberPage(state, snapshot) {
  const next = normalizeState(state);
  if (!snapshot || !snapshot.url) return next;
  const remembered = [
    {
      id: crypto.randomUUID(),
      rememberedAt: new Date().toISOString(),
      ...snapshot,
    },
    ...next.rememberedPages.filter((item) => item.url !== snapshot.url),
  ];
  next.rememberedPages = remembered.slice(0, MAX_REMEMBERED_PAGES);
  return next;
}

function addNotebookEntry(state, entry) {
  const next = normalizeState(state);
  const notebookEntries = [
    {
      id: crypto.randomUUID(),
      createdAt: new Date().toISOString(),
      tags: [],
      ...entry,
    },
    ...next.notebookEntries,
  ];
  next.notebookEntries = notebookEntries.slice(0, MAX_NOTEBOOK_ENTRIES);
  return next;
}

function addBookmark(state, bookmark) {
  const next = normalizeState(state);
  if (!bookmark || !bookmark.url) return next;
  next.bookmarks = [
    { id: crypto.randomUUID(), createdAt: new Date().toISOString(), ...bookmark },
    ...next.bookmarks.filter((item) => item.url !== bookmark.url),
  ];
  return next;
}

function addDownload(state, download) {
  const next = normalizeState(state);
  next.downloads = [
    { id: crypto.randomUUID(), createdAt: new Date().toISOString(), ...download },
    ...next.downloads,
  ].slice(0, MAX_HISTORY_ENTRIES);
  return next;
}

function importResearchItems(state, items) {
  const next = normalizeState(state);
  const normalized = (Array.isArray(items) ? items : []).map((item) => ({
    id: crypto.randomUUID(),
    importedAt: new Date().toISOString(),
    title: String(item.title || item.name || 'Imported item'),
    text: String(item.text || ''),
    source: String(item.source || 'import'),
  })).filter((item) => item.text.trim());
  next.importedResearch = [...normalized, ...next.importedResearch].slice(0, MAX_IMPORT_ITEMS);
  return next;
}

module.exports = {
  DEFAULT_HOME,
  MAX_REMEMBERED_PAGES,
  createDefaultSettings,
  createInitialState,
  normalizeState,
  sanitizeUrl,
  addTab,
  activateTab,
  closeTab,
  updateTab,
  pushHistory,
  rememberPage,
  addNotebookEntry,
  addBookmark,
  addDownload,
  importResearchItems,
};
