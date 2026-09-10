const test = require('node:test');
const assert = require('node:assert/strict');
const core = require('../desktop/lib/browser-core');
const context = require('../desktop/lib/page-context');

test('collectKeySentences returns the longest informative sentences', () => {
  const result = context.collectKeySentences('Short. This is a substantially longer sentence about PsiCat research memory. Another long sentence about browser notebooks and imports.');
  assert.equal(result.length, 2);
});

test('buildContextEnvelope includes current page and notebook entries', () => {
  let state = core.createInitialState();
  state = core.updateTab(state, state.activeTabId, { lastSnapshot: { title: 'Doc', url: 'https://example.com', text: 'Browser context for research notebook.' } });
  state = core.addNotebookEntry(state, { title: 'Memo', text: 'Notebook memory' });
  state = core.rememberPage(state, { title: 'Saved Page', url: 'https://saved.example', text: 'Remembered text' });
  state = core.importResearchItems(state, [{ title: 'Imported', text: 'Imported research text', source: 'fixture' }]);
  const envelope = context.buildContextEnvelope(state);
  assert.equal(envelope.current_page.title, 'Doc');
  assert.equal(envelope.notebook_entries[0].title, 'Memo');
  assert.equal(envelope.remembered_pages[0].title, 'Saved Page');
  assert.equal(envelope.imported_research[0].title, 'Imported');
});
