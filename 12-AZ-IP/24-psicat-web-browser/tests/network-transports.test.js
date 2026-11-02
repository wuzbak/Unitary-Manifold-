// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
const assert = require('node:assert/strict');
const { createServer } = require('node:http');
const { test } = require('node:test');
const core = require('../desktop/lib/browser-core');
const psiCatClient = require('../desktop/lib/psicat-client');
const syncTransport = require('../desktop/lib/sync-transport');

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
  return state;
}

test('production query and sync transports stay on loopback after hostile settings and packet imports', async () => {
  const requests = [];
  const recordRequest = async (request, response) => {
    const chunks = [];
    for await (const chunk of request) chunks.push(chunk);
    requests.push({ path: request.url, headers: request.headers, body: Buffer.concat(chunks).toString() });
    if (request.url === '/api/psicat/status') {
      response.writeHead(200, {
        'Content-Type': 'application/json',
        'X-PsiCat-Handshake-Challenge': 'test-challenge',
        'X-PsiCat-Handshake-Receipt': 'test-receipt',
        'Set-Cookie': 'psicat_profile_id=test-profile; Path=/',
      });
      response.end(JSON.stringify({ memory_profile_token: 'test-token' }));
      return;
    }
    if (request.url === '/api/psicat') {
      response.writeHead(200, { 'Content-Type': 'application/json' });
      response.end(JSON.stringify({ answer: 'Observable server answer' }));
      return;
    }
    response.writeHead(200, { 'Content-Type': 'application/json' });
    response.end(JSON.stringify({
      updated_at: '2026-11-02T00:00:00.000Z',
      packet: core.createSyncPacket(core.createInitialState()),
    }));
  };
  const psiCatServer = createServer(recordRequest);
  const syncServer = createServer(recordRequest);
  const listen = (server, port) => new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(port, '127.0.0.1', resolve);
  });
  const close = (server) => new Promise((resolve) => {
    if (!server.listening) return resolve();
    server.close(resolve);
  });

  try {
    await Promise.all([listen(psiCatServer, 8020), listen(syncServer, 8787)]);
    const observedFetch = async (url, options) => {
      assert.equal(new URL(url).hostname, '127.0.0.1');
      return fetch(url, options);
    };
    const querySession = { cookie: '' };
    const runProductionRequests = async (state) => {
      const body = psiCatClient.buildPageQuery({
        state,
        question: 'Verify loopback transport',
        requestId: 'network-sandbox',
      });
      const result = await psiCatClient.queryPsiCat({
        baseUrl: 'http://127.0.0.1:8020',
        body,
        session: querySession,
        fetchImpl: observedFetch,
      });
      assert.equal(result.answer, 'Observable server answer');

      const pushed = await syncTransport.pushSyncToBackend({
        state,
        endpoint: state.settings.syncBackendEndpoint,
        core,
        fetchImpl: observedFetch,
      });
      assert.equal(pushed.payload.updated_at, '2026-11-02T00:00:00.000Z');
      const pulled = await syncTransport.pullSyncFromBackend({
        state: pushed.state,
        endpoint: pushed.state.settings.syncBackendEndpoint,
        core,
        fetchImpl: observedFetch,
      });
      assert.equal(pulled.state.sync.lastSyncSource, 'backend-pull');
    };

    let state = core.normalizeState({
      ...buildInitialState(),
      sync: { mode: 'local+account', accountEmail: 'test@example.invalid' },
      settings: {
        ...core.createDefaultSettings(),
        psicatEndpoint: 'https://attacker.example/query',
        syncBackendEndpoint: 'https://attacker.example/sync',
      },
    });
    assert.equal(state.settings.psicatEndpoint, 'http://127.0.0.1:8020');
    assert.equal(state.settings.syncBackendEndpoint, 'http://127.0.0.1:8787');
    await runProductionRequests(state);

    state = core.mergeSyncPacket(state, {
      settings: {
        psicatEndpoint: 'https://attacker.example/imported-query',
        syncBackendEndpoint: 'https://attacker.example/imported-sync',
      },
      sync: { accountEmail: 'imported@example.invalid' },
    });
    assert.equal(state.settings.psicatEndpoint, 'http://127.0.0.1:8020');
    assert.equal(state.settings.syncBackendEndpoint, 'http://127.0.0.1:8787');
    await runProductionRequests(state);

    assert.deepEqual(requests.map(({ path }) => path), [
      '/api/psicat/status',
      '/api/psicat',
      '/api/sync/push',
      '/api/sync/pull?account_email=test%40example.invalid',
      '/api/psicat/status',
      '/api/psicat',
      '/api/sync/push',
      '/api/sync/pull?account_email=imported%40example.invalid',
    ]);
    assert.ok(requests.filter(({ path }) => path === '/api/sync/push')
      .every(({ headers }) => headers['x-sync-token'] === state.settings.syncAccessToken));
  } finally {
    await Promise.all([close(psiCatServer), close(syncServer)]);
  }
});

test('PsiCat and sync transports reject redirects before forwarding request data', async () => {
  let redirectedRequests = 0;
  const target = createServer((_request, response) => {
    redirectedRequests += 1;
    response.end('should not be reached');
  });
  const redirect = createServer((request, response) => {
    if (request.url === '/api/psicat/status') {
      response.writeHead(200, {
        'Content-Type': 'application/json',
        'X-PsiCat-Handshake-Challenge': 'test-challenge',
        'X-PsiCat-Handshake-Receipt': 'test-receipt',
        'Set-Cookie': 'psicat_profile_id=test-profile; Path=/',
      });
      response.end(JSON.stringify({ memory_profile_token: 'test-token' }));
      return;
    }
    response.writeHead(307, { Location: `http://127.0.0.1:${target.address().port}/collect` });
    response.end();
  });
  const listen = (server) => new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  const close = (server) => new Promise((resolve) => {
    if (!server.listening) return resolve();
    server.close(resolve);
  });

  try {
    await listen(target);
    await listen(redirect);
    const endpoint = `http://127.0.0.1:${redirect.address().port}`;
    await assert.rejects(psiCatClient.queryPsiCat({
      baseUrl: endpoint,
      body: { query: 'sensitive page context', context_envelope: { request_id: 'redirect-test' } },
      session: { cookie: '' },
    }));

    const state = buildInitialState();
    state.sync.accountEmail = 'test@example.invalid';
    await assert.rejects(syncTransport.pushSyncToBackend({ state, endpoint, core }));
    await assert.rejects(syncTransport.pullSyncFromBackend({ state, endpoint, core }));
    assert.equal(redirectedRequests, 0);
  } finally {
    await Promise.all([close(redirect), close(target)]);
  }
});
