const test = require('node:test');
const assert = require('node:assert/strict');
const core = require('../desktop/lib/browser-core');

test('sanitizeUrl converts hostnames to https and queries to search URLs', () => {
  assert.equal(core.sanitizeUrl('example.com'), 'https://example.com');
  assert.match(core.sanitizeUrl('psi cat notebook'), /duckduckgo/);
});

test('createInitialState starts with one active tab and settings', () => {
  const state = core.createInitialState();
  assert.equal(state.tabs.length, 1);
  assert.equal(state.activeTabId, state.tabs[0].id);
  assert.equal(state.settings.livePageCapture, true);
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
