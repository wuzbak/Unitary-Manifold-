// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
//
// Product 24 (PsiCat Web Browser) sandbox verification: proves the desktop
// UI shell never makes a single outbound network request to anything other
// than the Playwright-served loopback page itself, across a full session of
// real user interactions (navigation, settings changes including an attempt
// to redirect the PsiCat/sync endpoints off-box, note-taking, and querying
// PsiCat). This is the "zero data leakage outside loopback" verification
// gate: a real Chromium instance renders the actual production UI code
// (desktop/ui/app.js, desktop/ui/app.css) with only `window.psicatBrowser`
// stubbed (the same Electron preload bridge boundary the real desktop app
// exposes) -- nothing about networking is mocked or intercepted, so any
// stray `fetch`/`XMLHttpRequest`/resource load this page issues is captured
// for real by Playwright's request listener.
const { test, expect } = require('@playwright/test');
const core = require('../../desktop/lib/browser-core');

const LOOPBACK_HOSTS = new Set(['127.0.0.1', 'localhost', '::1', '[::1]']);

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
  return {
    ...state,
    psiCatSidecar: { status: 'ready', error: '' },
    syncBackend: { status: 'ready', error: '' },
  };
}

test.beforeEach(async ({ page }) => {
  const initialState = buildInitialState();
  await page.addInitScript(({ initialState }) => {
    let state = structuredClone(initialState);
    const clone = (value) => JSON.parse(JSON.stringify(value));
    const listeners = [];
    const broadcast = () => listeners.forEach((listener) => listener(clone(state)));
    const api = {
      getState: async () => clone(state),
      createTab: async () => clone(state),
      closeTab: async () => clone(state),
      activateTab: async () => clone(state),
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
        state.notebookEntries.unshift({ id: 'note-1', createdAt: new Date().toISOString(), ...entry });
        broadcast();
        return clone(state);
      },
      // Mirrors the real IPC handler's contract (desktop/main.js
      // `browser:update-settings` -> `core.normalizeState`): any attempt to
      // set a non-loopback psicatEndpoint/syncBackendEndpoint here is
      // clamped back to a safe loopback default by the exact same
      // production helper under test, never honoured as a real request
      // target.
      updateSettings: async (patch) => {
        state = await window.__azNormalizeState({
          ...state,
          settings: { ...state.settings, ...(patch.settings || patch) },
          sync: patch.sync ? { ...state.sync, ...patch.sync } : state.sync,
        });
        broadcast();
        return clone(state);
      },
      queryPsiCat: async ({ question, requestId }) => ({
        mode: 'psicat', request_id: requestId,
        answer: `Stubbed answer: ${question}`, source_url: 'https://example.com',
        sharing: 'current_page_only',
        provenance: { complete: true, sources: ['synthetic-fixture'] },
      }),
      cancelPsiCat: async () => true,
      importResearchFiles: async () => clone(state),
      exportResearchBundle: async () => '/tmp/research.json',
      importSyncPacket: async () => clone(state),
      exportSyncPacket: async () => '/tmp/sync.json',
      syncNow: async () => ({ updated_at: '2026-09-10T04:30:00Z' }),
      syncPull: async () => ({ updated_at: '2026-09-10T04:31:00Z' }),
      updateWorkspaceLayout: async (layout, secondaryTabId) => {
        state.workspace.layout = layout;
        state.workspace.secondaryTabId = secondaryTabId;
        broadcast();
        return clone(state);
      },
      saveWorkspace: async (name) => {
        state.workspace.savedLayouts.unshift({ id: 'workspace-1', name, layout: state.workspace.layout, createdAt: '2026-09-10T04:32:00Z', tabUrls: [] });
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

  // Expose the real production loopback-enforcement helper (desktop/lib/
  // browser-core.js::normalizeState) inside the page -- the exact function
  // `desktop/main.js`'s `browser:update-settings` IPC handler calls -- so
  // the stub above enforces the identical policy rather than a
  // re-implementation that could silently drift from production behaviour.
  // `exposeFunction` must be registered before `page.goto`, which the
  // `test.beforeEach` ordering below guarantees.
  await page.exposeFunction('__azNormalizeState', (state) => core.normalizeState(state));

  await page.goto('/');
});

test('desktop UI issues zero non-loopback network requests across a full interaction session', async ({ page }) => {
  const offLoopbackRequests = [];
  page.on('request', (request) => {
    const url = new URL(request.url());
    if (url.protocol === 'data:' || url.protocol === 'about:') return;
    if (!LOOPBACK_HOSTS.has(url.hostname.toLowerCase())) {
      offLoopbackRequests.push(request.url());
    }
  });

  await expect(page.getByRole('heading', { name: 'PsiCat Browser' })).toBeVisible();

  // Navigate, take a note, ask PsiCat a question, and attempt to redirect
  // settings to an attacker-controlled endpoint -- the single highest-risk
  // action a user (or a malicious imported sync packet) could take.
  await page.getByLabel('Notebook title').fill('Sandbox check');
  await page.getByLabel('Notebook body').fill('Verifying loopback-only networking.');
  await page.getByRole('button', { name: 'Save note' }).click();
  await expect(page.getByText('Sandbox check')).toBeVisible();

  await page.getByLabel('PsiCat question').fill('Explain this page');
  await page.getByRole('button', { name: 'Interrogate', exact: true }).click();
  await expect(page.locator('#answer')).toContainText('Stubbed answer: Explain this page');

  await page.getByRole('button', { name: 'Settings' }).click();
  await page.getByLabel('PsiCat endpoint').fill('https://attacker.example/exfiltrate');
  await page.getByLabel('Sync backend endpoint').fill('https://attacker.example/exfiltrate');
  await page.getByRole('button', { name: 'Save settings' }).click();

  expect(
    offLoopbackRequests,
    `expected zero non-loopback requests, observed: ${JSON.stringify(offLoopbackRequests)}`,
  ).toEqual([]);
});

test('production normalizeState clamps an attacker-supplied endpoint back to loopback', async ({ page }) => {
  // Direct, in-process check of the exact helper main.js calls on every
  // settings update and every sync-packet import (desktop/lib/browser-
  // core.js::normalizeState), independent of the UI stub above.
  const clamped = await page.evaluate(async () => {
    const response = await window.__azNormalizeState({
      settings: {
        psicatEndpoint: 'https://attacker.example/exfiltrate',
        syncBackendEndpoint: 'https://attacker.example/exfiltrate',
      },
    });
    return response.settings;
  });
  expect(clamped.psicatEndpoint.startsWith('http://127.0.0.1') || clamped.psicatEndpoint.includes('localhost')).toBe(true);
  expect(clamped.syncBackendEndpoint.startsWith('http://127.0.0.1') || clamped.syncBackendEndpoint.includes('localhost')).toBe(true);
});
