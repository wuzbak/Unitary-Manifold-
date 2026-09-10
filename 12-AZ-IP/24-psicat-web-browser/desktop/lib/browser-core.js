const crypto = require('node:crypto');

const DEFAULT_HOME = 'https://example.com';
const MAX_REMEMBERED_PAGES = 48;
const MAX_NOTEBOOK_ENTRIES = 200;
const MAX_HISTORY_ENTRIES = 250;
const MAX_IMPORT_ITEMS = 120;
const MAX_RECENTLY_CLOSED_TABS = 12;

function createSyncAccessToken() {
  return crypto.randomUUID().replace(/-/g, '');
}

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
    syncBackendEndpoint: 'http://127.0.0.1:8787',
    syncAccessToken: createSyncAccessToken(),
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
      lastSyncSource: 'never',
    },
    workspace: {
      layout: 'single',
      secondaryTabId: null,
      savedLayouts: [],
    },
    recentlyClosedTabs: [],
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
      lastSyncSource: 'never',
      ...(state.sync || {}),
    },
    workspace: {
      layout: 'single',
      secondaryTabId: null,
      savedLayouts: [],
      ...(state.workspace || {}),
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
  if (!merged.settings.syncAccessToken) {
    merged.settings.syncAccessToken = createSyncAccessToken();
  }
  if (!merged.settings.syncBackendEndpoint) {
    merged.settings.syncBackendEndpoint = 'http://127.0.0.1:8787';
  }
  if (!merged.tabs.some((tab) => tab.id === merged.workspace.secondaryTabId)) {
    merged.workspace.secondaryTabId = null;
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
  const closedTab = next.tabs[index];
  next.tabs.splice(index, 1);
  next.recentlyClosedTabs = [
    { ...closedTab, closedAt: new Date().toISOString() },
    ...(next.recentlyClosedTabs || []),
  ].slice(0, MAX_RECENTLY_CLOSED_TABS);
  if (next.activeTabId === tabId) {
    next.activeTabId = next.tabs[Math.max(0, index - 1)].id;
  }
  if (next.workspace.secondaryTabId === tabId) {
    next.workspace.secondaryTabId = null;
    next.workspace.layout = 'single';
  }
  return next;
}

function reopenLastClosedTab(state) {
  const next = normalizeState(state);
  const [lastClosed, ...remaining] = next.recentlyClosedTabs || [];
  if (!lastClosed) return next;
  const tab = createTab(lastClosed.url || DEFAULT_HOME, {
    title: lastClosed.title || 'Restored Tab',
    private: Boolean(lastClosed.private),
  });
  tab.lastSnapshot = lastClosed.lastSnapshot || null;
  next.tabs.push(tab);
  next.activeTabId = tab.id;
  next.recentlyClosedTabs = remaining;
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

function dedupeBy(items, keyBuilder) {
  const seen = new Set();
  return items.filter((item) => {
    const key = keyBuilder(item);
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function setWorkspaceLayout(state, layout) {
  const next = normalizeState(state);
  const allowed = new Set(['single', 'split-vertical', 'split-horizontal']);
  next.workspace.layout = allowed.has(layout) ? layout : 'single';
  if (next.workspace.layout === 'single') next.workspace.secondaryTabId = null;
  return next;
}

function setWorkspaceSecondaryTab(state, tabId) {
  const next = normalizeState(state);
  if (!tabId || tabId === next.activeTabId) {
    next.workspace.secondaryTabId = null;
    next.workspace.layout = 'single';
    return next;
  }
  if (next.tabs.some((tab) => tab.id === tabId)) {
    next.workspace.secondaryTabId = tabId;
    if (next.workspace.layout === 'single') next.workspace.layout = 'split-vertical';
  }
  return next;
}

function saveCurrentWorkspace(state, name) {
  const next = normalizeState(state);
  const saved = {
    id: crypto.randomUUID(),
    name: String(name || '').trim() || 'Workspace',
    layout: next.workspace.layout,
    activeTabId: next.activeTabId,
    secondaryTabId: next.workspace.secondaryTabId,
    tabUrls: next.tabs.map((tab) => ({ id: tab.id, url: tab.url, title: tab.title, private: Boolean(tab.private) })),
    createdAt: new Date().toISOString(),
  };
  next.workspace.savedLayouts = [saved, ...(next.workspace.savedLayouts || [])].slice(0, 12);
  return next;
}

function applySavedWorkspace(state, workspaceId) {
  const next = normalizeState(state);
  const saved = (next.workspace.savedLayouts || []).find((entry) => entry.id === workspaceId);
  if (!saved) return next;
  const tabs = (saved.tabUrls || []).map((entry) => createTab(sanitizeUrl(entry.url || DEFAULT_HOME, next.settings), {
    title: entry.title || 'Workspace Tab',
    private: Boolean(entry.private),
  }));
  if (!tabs.length) return next;
  next.tabs = tabs;
  const activeIndex = (saved.tabUrls || []).findIndex((entry) => entry.id === saved.activeTabId);
  next.activeTabId = tabs[activeIndex >= 0 ? activeIndex : 0].id;
  next.workspace.layout = saved.layout || 'single';
  const secondaryIndex = (saved.tabUrls || []).findIndex((entry) => entry.id === saved.secondaryTabId);
  next.workspace.secondaryTabId = tabs[secondaryIndex]?.id || null;
  return next;
}

function createSyncPacket(state) {
  const next = normalizeState(state);
  const syncableTabs = next.tabs.filter((tab) => !tab.private);
  const syncableUrls = new Set(syncableTabs.map((tab) => tab.url));
  const activeTab = syncableTabs.find((tab) => tab.id === next.activeTabId) || syncableTabs[0];
  const secondaryTab = syncableTabs.find((tab) => tab.id === next.workspace.secondaryTabId) || null;
  return {
    product: 24,
    exportedAt: new Date().toISOString(),
    sync: {
      ...next.sync,
      lastSyncAt: new Date().toISOString(),
    },
    settings: {
      homePage: next.settings.homePage,
      searchEngine: next.settings.searchEngine,
      trackProtection: next.settings.trackProtection,
      sidebarWidth: next.settings.sidebarWidth,
      psicatEndpoint: next.settings.psicatEndpoint,
      syncBackendEndpoint: next.settings.syncBackendEndpoint,
      livePageCapture: next.settings.livePageCapture,
    },
    tabs: syncableTabs.map((tab) => ({
      title: tab.title,
      url: tab.url,
      private: Boolean(tab.private),
      lastSnapshot: tab.lastSnapshot || null,
    })),
    workspace: {
      ...next.workspace,
      layout: secondaryTab ? next.workspace.layout : 'single',
      activeTabUrl: activeTab?.url || DEFAULT_HOME,
      secondaryTabUrl: secondaryTab?.url || null,
    },
    activeTabUrl: activeTab?.url || DEFAULT_HOME,
    bookmarks: next.bookmarks.filter((item) => !item.private).slice(0, MAX_HISTORY_ENTRIES),
    history: next.history.filter((item) => !item.private).slice(0, 100),
    downloads: next.downloads.slice(0, 40),
    notebookEntries: next.notebookEntries.filter((item) => !item.private).slice(0, 100),
    rememberedPages: next.rememberedPages.filter((item) => !item.private && syncableUrls.has(item.url)).slice(0, 40),
    importedResearch: next.importedResearch.slice(0, 100),
  };
}

function mergeSyncPacket(state, packet) {
  const next = normalizeState(state);
  if (!packet || typeof packet !== 'object') return next;
  const incomingTabs = Array.isArray(packet.tabs)
    ? packet.tabs.map((tab) => createTab(sanitizeUrl(tab.url || DEFAULT_HOME, next.settings), {
      title: tab.title || 'Imported Tab',
      private: Boolean(tab.private),
    }))
    : [];
  incomingTabs.forEach((tab, index) => {
    const raw = packet.tabs[index] || {};
    tab.lastSnapshot = raw.lastSnapshot || null;
  });
  const tabs = dedupeBy([...next.tabs, ...incomingTabs], (tab) => `${tab.private ? 'p' : 'n'}:${tab.url}`);
  const bookmarks = dedupeBy([...(packet.bookmarks || []), ...next.bookmarks], (item) => item.url).slice(0, MAX_HISTORY_ENTRIES);
  const history = dedupeBy([...(packet.history || []), ...next.history], (item) => `${item.url}:${item.title || ''}`).slice(0, MAX_HISTORY_ENTRIES);
  const downloads = dedupeBy([...(packet.downloads || []), ...next.downloads], (item) => `${item.url}:${item.fileName || ''}`).slice(0, MAX_HISTORY_ENTRIES);
  const notebookEntries = dedupeBy([...(packet.notebookEntries || []), ...next.notebookEntries], (item) => `${item.title}:${item.createdAt || item.text?.slice(0, 80) || ''}`).slice(0, MAX_NOTEBOOK_ENTRIES);
  const rememberedPages = dedupeBy([...(packet.rememberedPages || []), ...next.rememberedPages], (item) => item.url).slice(0, MAX_REMEMBERED_PAGES);
  const importedResearch = dedupeBy([...(packet.importedResearch || []), ...next.importedResearch], (item) => `${item.title}:${item.source || ''}`).slice(0, MAX_IMPORT_ITEMS);
  return normalizeState({
    ...next,
    tabs: tabs.length ? tabs : next.tabs,
    activeTabId: (tabs.find((tab) => tab.url === packet.activeTabUrl) || tabs[0] || next.tabs[0]).id,
    bookmarks,
    history,
    downloads,
    notebookEntries,
    rememberedPages,
    importedResearch,
    settings: {
      ...next.settings,
      ...(packet.settings || {}),
    },
    sync: {
      ...next.sync,
      ...(packet.sync || {}),
      lastSyncAt: new Date().toISOString(),
      lastSyncSource: 'imported-packet',
    },
    workspace: (() => {
      const incomingWorkspace = packet.workspace || {};
      const secondaryTab = tabs.find((tab) => tab.url === incomingWorkspace.secondaryTabUrl);
      return {
        ...next.workspace,
        ...incomingWorkspace,
        secondaryTabId: secondaryTab ? secondaryTab.id : null,
      };
    })(),
  });
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
  reopenLastClosedTab,
  setWorkspaceLayout,
  setWorkspaceSecondaryTab,
  saveCurrentWorkspace,
  applySavedWorkspace,
  createSyncPacket,
  mergeSyncPacket,
};
