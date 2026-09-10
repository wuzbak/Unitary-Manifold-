const { test, expect } = require('@playwright/test');
const core = require('../../desktop/lib/browser-core');

function buildInitialState() {
  let state = core.createInitialState();
  state = core.updateTab(state, state.activeTabId, {
    title: 'AxiomZero Home',
    url: 'https://example.com',
    lastSnapshot: {
      title: 'AxiomZero Home',
      url: 'https://example.com',
      selection: '',
      text: 'Welcome to PsiCat Browser.',
      capturedAt: new Date().toISOString(),
    },
  });
  state = core.addTab(state, 'docs.python.org');
  state = core.updateTab(state, state.activeTabId, {
    title: 'Python Docs',
    url: 'https://docs.python.org',
  });
  return {
    ...state,
    psiCatSidecar: { status: 'ready', error: '' },
    syncBackend: { status: 'ready', error: '' },
  };
}

test.beforeEach(async ({ page }) => {
  const initialState = buildInitialState();
  await page.addInitScript(({ initialState }) => {
    const listeners = [];
    let state = structuredClone(initialState);
    const clone = (value) => JSON.parse(JSON.stringify(value));
    const broadcast = () => listeners.forEach((listener) => listener(clone(state)));
    let workspaceCounter = 1;
    const api = {
      getState: async () => clone(state),
      createTab: async () => clone(state),
      closeTab: async () => clone(state),
      activateTab: async (tabId) => {
        state.activeTabId = tabId;
        broadcast();
        return clone(state);
      },
      navigate: async (url) => {
        const active = state.tabs.find((tab) => tab.id === state.activeTabId);
        if (active) active.url = url;
        broadcast();
        return clone(state);
      },
      goBack: async () => clone(state),
      goForward: async () => clone(state),
      goHome: async () => clone(state),
      reload: async () => clone(state),
      stop: async () => clone(state),
      reopenClosedTab: async () => clone(state),
      addBookmark: async () => clone(state),
      rememberActivePage: async () => clone(state),
      addNotebookEntry: async (entry) => {
        state.notebookEntries.unshift({
          id: `note-${state.notebookEntries.length + 1}`,
          createdAt: new Date().toISOString(),
          ...entry,
        });
        broadcast();
        return clone(state);
      },
      updateSettings: async (patch) => {
        state.settings = { ...state.settings, ...(patch.settings || patch) };
        state.sync = patch.sync ? { ...state.sync, ...patch.sync } : state.sync;
        broadcast();
        return clone(state);
      },
      queryPsiCat: async ({ question }) => ({ answer: `Stubbed answer: ${question}` }),
      importResearchFiles: async () => clone(state),
      exportResearchBundle: async () => '/tmp/research.json',
      importSyncPacket: async () => clone(state),
      exportSyncPacket: async () => '/tmp/sync.json',
      syncNow: async () => ({ updated_at: '2026-09-10T04:30:00Z' }),
      syncPull: async () => {
        if (state.sync.mode === 'local-only') {
          return { skipped: true, message: 'Local-only mode leaves remote pull disabled.' };
        }
        return { updated_at: '2026-09-10T04:31:00Z' };
      },
      updateWorkspaceLayout: async (layout, secondaryTabId) => {
        state.workspace.layout = layout;
        state.workspace.secondaryTabId = secondaryTabId;
        broadcast();
        return clone(state);
      },
      saveWorkspace: async (name) => {
        state.workspace.savedLayouts.unshift({
          id: `workspace-${workspaceCounter++}`,
          name,
          layout: state.workspace.layout,
          createdAt: '2026-09-10T04:32:00Z',
          tabUrls: state.tabs.map((tab) => ({ url: tab.url, title: tab.title })),
        });
        broadcast();
        return clone(state);
      },
      applyWorkspace: async () => clone(state),
      openDownload: async () => {},
      openExternal: async () => {},
      onState: (callback) => listeners.push(callback),
    };
    Object.defineProperty(window, 'psicatBrowser', { value: api });
  }, { initialState });
  await page.goto('/');
});

test('desktop UI saves notes and saved workspaces through browser interactions', async ({ page }) => {
  await expect(page.getByText('PsiCat Browser')).toBeVisible();
  await expect(page.getByText(/Sync backend: ready/)).toBeVisible();

  await page.getByLabel('Workspace layout').selectOption('split-vertical');
  await page.getByLabel('Secondary workspace tab').selectOption({ index: 1 });
  await page.evaluate(() => { window.prompt = () => 'Research Split'; });
  await page.getByRole('button', { name: 'Save workspace' }).click();
  await expect(page.getByText('Research Split')).toBeVisible();

  await page.getByLabel('Notebook title').fill('Playwright note');
  await page.getByLabel('Notebook body').fill('Browser-first proving ground.');
  await page.getByRole('button', { name: 'Save note' }).click();
  await expect(page.getByText('Playwright note')).toBeVisible();
  await expect(page.getByText('Browser-first proving ground.')).toBeVisible();
});

test('desktop UI reflects local-only sync pull behavior in the browser shell', async ({ page }) => {
  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByLabel('Sync mode').selectOption('local-only');
  await page.getByRole('button', { name: 'Save settings' }).click();
  await page.getByRole('button', { name: 'Pull sync' }).click();
  await expect(page.locator('#answer')).toContainText('Local-only mode leaves remote pull disabled.');
});
