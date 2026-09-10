const test = require('node:test');
const assert = require('node:assert/strict');
const core = require('../desktop/lib/browser-core');
const syncPolicy = require('../desktop/lib/sync-policy');

test('sanitizeUrl converts hostnames to https and queries to search URLs', () => {
  assert.equal(core.sanitizeUrl('example.com'), 'https://example.com');
  assert.match(core.sanitizeUrl('psi cat notebook'), /duckduckgo/);
});

test('createInitialState starts with one active tab and settings', () => {
  const state = core.createInitialState();
  assert.equal(state.tabs.length, 1);
  assert.equal(state.activeTabId, state.tabs[0].id);
  assert.equal(state.settings.livePageCapture, true);
  assert.equal(state.settings.syncBackendEndpoint, 'http://127.0.0.1:8787');
});

test('rememberPage deduplicates by url and caps recent memory', () => {
  let state = core.createInitialState();
  state = core.rememberPage(state, { title: 'A', url: 'https://a.test', text: 'first' });
  state = core.rememberPage(state, { title: 'B', url: 'https://a.test', text: 'second' });
  assert.equal(state.rememberedPages.length, 1);
  assert.equal(state.rememberedPages[0].title, 'B');
});

test('addTab preserves private-tab flag for in-memory browsing state', () => {
  const state = core.addTab(core.createInitialState(), 'example.org', { private: true });
  const active = state.tabs.find((tab) => tab.id === state.activeTabId);
  assert.equal(active.private, true);
  assert.equal(active.url, 'https://example.org');
});

test('importResearchItems caps imported research corpus', () => {
  let state = core.createInitialState();
  state = core.importResearchItems(
    state,
    Array.from({ length: 140 }, (_, index) => ({ title: `Item ${index}`, text: `Text ${index}`, source: 'test' })),
  );
  assert.equal(state.importedResearch.length, 120);
});

test('normalizeState restores a valid active tab when persisted state is malformed', () => {
  const state = core.normalizeState({ tabs: [{ id: 'a', url: 'https://example.com', title: 'A' }], activeTabId: 'missing' });
  assert.equal(state.activeTabId, 'a');
});

test('closeTab keeps one tab alive and reassigns the active tab', () => {
  let state = core.createInitialState();
  state = core.addTab(state, 'example.net');
  const firstTabId = state.tabs[0].id;
  const secondTabId = state.activeTabId;
  state = core.closeTab(state, secondTabId);
  assert.equal(state.tabs.length, 1);
  assert.equal(state.activeTabId, firstTabId);
});

test('closeTab tracks recently closed tabs and reopenLastClosedTab restores one', () => {
  let state = core.createInitialState();
  state = core.addTab(state, 'example.net');
  const closedUrl = state.tabs.find((tab) => tab.id === state.activeTabId).url;
  state = core.closeTab(state, state.activeTabId);
  assert.equal(state.recentlyClosedTabs.length, 1);
  state = core.reopenLastClosedTab(state);
  assert.equal(state.recentlyClosedTabs.length, 0);
  assert.equal(state.tabs.find((tab) => tab.id === state.activeTabId).url, closedUrl);
});

test('createSyncPacket and mergeSyncPacket preserve imported browser state', () => {
  let state = core.createInitialState();
  state = core.addBookmark(state, { title: 'Example', url: 'https://example.com' });
  state = core.addNotebookEntry(state, { title: 'Memo', text: 'Sync me' });
  state = core.addTab(state, 'docs.python.org');
  state = core.setWorkspaceLayout(state, 'split-vertical');
  state = core.setWorkspaceSecondaryTab(state, state.tabs[0].id);
  const packet = core.createSyncPacket(state);
  const merged = core.mergeSyncPacket(core.createInitialState(), packet);
  assert.equal(merged.bookmarks[0].url, 'https://example.com');
  assert.equal(merged.notebookEntries[0].title, 'Memo');
  assert.equal(merged.sync.lastSyncSource, 'imported-packet');
  assert.equal(merged.workspace.layout, 'split-vertical');
  assert.ok(merged.workspace.secondaryTabId);
});

test('workspace helpers save and restore a split layout', () => {
  let state = core.createInitialState();
  state = core.addTab(state, 'example.net');
  const secondaryTabId = state.tabs[0].id;
  state = core.setWorkspaceLayout(state, 'split-horizontal');
  state = core.setWorkspaceSecondaryTab(state, secondaryTabId);
  state = core.saveCurrentWorkspace(state, 'Research');
  const workspaceId = state.workspace.savedLayouts[0].id;
  const restored = core.applySavedWorkspace(state, workspaceId);
  assert.equal(restored.workspace.layout, 'split-horizontal');
  assert.ok(restored.workspace.secondaryTabId);
  assert.equal(restored.tabs.length, 2);
});

test('createSyncPacket excludes private browsing artifacts', () => {
  let state = core.createInitialState();
  state = core.addTab(state, 'private.example', { private: true });
  const privateTabId = state.activeTabId;
  state = core.updateTab(state, privateTabId, { lastSnapshot: { url: 'https://private.example', title: 'Private', text: 'secret', private: true } });
  state = core.pushHistory(state, { title: 'Private', url: 'https://private.example', private: true });
  state = core.addBookmark(state, { title: 'Private', url: 'https://private.example', private: true });
  state = core.addNotebookEntry(state, { title: 'Private note', text: 'secret', private: true });
  state = core.rememberPage(state, { title: 'Private', url: 'https://private.example', text: 'secret', private: true });
  state = core.addDownload(state, { fileName: 'kept-download.bin', url: 'https://downloads.example/file.bin' });
  const packet = core.createSyncPacket(state);
  assert.equal(packet.tabs.some((tab) => tab.private), false);
  assert.equal(packet.history.some((entry) => entry.private), false);
  assert.equal(packet.bookmarks.some((entry) => entry.private), false);
  assert.equal(packet.notebookEntries.some((entry) => entry.private), false);
  assert.equal(packet.rememberedPages.some((entry) => entry.private), false);
  assert.equal(packet.downloads[0].fileName, 'kept-download.bin');
});

test('sync policy only uses backend for account-enabled sync', () => {
  assert.equal(syncPolicy.shouldUseBackendSync({ sync: { mode: 'local-only', accountEmail: 'user@example.com' } }), false);
  assert.equal(syncPolicy.shouldUseBackendSync({ sync: { mode: 'local+account', accountEmail: '' } }), false);
  assert.equal(syncPolicy.shouldUseBackendSync({ sync: { mode: 'local+account', accountEmail: 'user@example.com' } }), true);
});
