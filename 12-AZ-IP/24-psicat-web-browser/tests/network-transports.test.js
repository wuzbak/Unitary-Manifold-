// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
const assert = require('node:assert/strict');
const { createServer } = require('node:http');
const { test } = require('node:test');
const core = require('../desktop/lib/browser-core');
const psiCatClient = require('../desktop/lib/psicat-client');
const syncTransport = require('../desktop/lib/sync-transport');

async function listen(handler) {
  const server = createServer(handler);
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  return server;
}

function close(server) {
  return new Promise((resolve, reject) => server.close((error) => error ? reject(error) : resolve()));
}

function handshake(response) {
  response.writeHead(200, {
    'Content-Type': 'application/json',
    'X-PsiCat-Handshake-Challenge': 'test-challenge',
    'X-PsiCat-Handshake-Receipt': 'test-receipt',
    'Set-Cookie': 'psicat_profile_id=test-profile; Path=/',
  });
  response.end(JSON.stringify({ memory_profile_token: 'test-token' }));
}

test('real query and sync transports stay on loopback after hostile settings and packet imports', async () => {
  const requests = [];
  const server = await listen(async (request, response) => {
    const chunks = [];
    for await (const chunk of request) chunks.push(chunk);
    requests.push({ path: request.url, headers: request.headers, body: Buffer.concat(chunks).toString() });
    if (request.url === '/api/psicat/status') return handshake(response);
    response.writeHead(200, { 'Content-Type': 'application/json' });
    response.end(JSON.stringify(request.url === '/api/psicat'
      ? { answer: 'Observable server answer' }
      : { updated_at: '2026-11-02T00:00:00.000Z', packet: core.createSyncPacket(core.createInitialState()) }));
  });
  try {
    const observedFetch = async (url, options) => {
      const target = new URL(url);
      assert.equal(target.hostname, '127.0.0.1');
      assert.equal(target.port, target.pathname.startsWith('/api/sync/') ? '8787' : '8020');
      // Keep the production-selected endpoint observable without reserving shared ports.
      target.port = String(server.address().port);
      return fetch(target, options);
    };
    const runProductionRequests = async (state) => {
      const body = psiCatClient.buildPageQuery({
        state, question: 'Verify loopback transport', requestId: 'network-sandbox',
      });
      const result = await psiCatClient.queryPsiCat({
        baseUrl: state.settings.psicatEndpoint, body, session: { cookie: '' }, fetchImpl: observedFetch,
      });
      assert.equal(result.answer, 'Observable server answer');
      const pushed = await syncTransport.pushSyncToBackend({
        state, endpoint: state.settings.syncBackendEndpoint, core, fetchImpl: observedFetch,
      });
      assert.equal(pushed.state.sync.lastSyncSource, 'backend-push');
      const pulled = await syncTransport.pullSyncFromBackend({
        state: pushed.state, endpoint: pushed.state.settings.syncBackendEndpoint, core, fetchImpl: observedFetch,
      });
      assert.equal(pulled.state.sync.lastSyncSource, 'backend-pull');
      assert.equal(pulled.payload.updated_at, '2026-11-02T00:00:00.000Z');
    };
    let state = core.normalizeState({
      ...core.createInitialState(),
      sync: { mode: 'local+account', accountEmail: 'test@example.invalid' },
      settings: {
        ...core.createDefaultSettings(),
        psicatEndpoint: 'https://attacker.example/query',
        syncBackendEndpoint: 'https://attacker.example/sync',
      },
    });
    await runProductionRequests(state);
    state = core.mergeSyncPacket(state, {
      settings: {
        psicatEndpoint: 'https://attacker.example/imported-query',
        syncBackendEndpoint: 'https://attacker.example/imported-sync',
      },
      sync: { accountEmail: 'imported@example.invalid' },
    });
    await runProductionRequests(state);
    assert.deepEqual(requests.map(({ path }) => path), [
      '/api/psicat/status', '/api/psicat', '/api/sync/push',
      '/api/sync/pull?account_email=test%40example.invalid',
      '/api/psicat/status', '/api/psicat', '/api/sync/push',
      '/api/sync/pull?account_email=imported%40example.invalid',
    ]);
    assert.ok(requests.filter(({ path }) => path.startsWith('/api/sync/'))
      .every(({ headers }) => headers['x-sync-token'] === state.settings.syncAccessToken));
    assert.equal(JSON.parse(requests[2].body).account_email, 'test@example.invalid');
    assert.equal(JSON.parse(requests[6].body).account_email, 'imported@example.invalid');
  } finally {
    await close(server);
  }
});

for (const redirectStatus of [true, false]) {
  test(`query and sync reject redirects without forwarding data (status redirect: ${redirectStatus})`, async () => {
    let redirectedRequests = 0;
    const paths = [];
    const target = await listen((_request, response) => {
      redirectedRequests += 1;
      response.end('should not be reached');
    });
    let redirect;
    try {
      redirect = await listen((request, response) => {
        paths.push(request.url);
        if (request.url === '/api/psicat/status' && !redirectStatus) return handshake(response);
        response.writeHead(307, { Location: `http://127.0.0.1:${target.address().port}/collect` });
        response.end();
      });
      const endpoint = `http://127.0.0.1:${redirect.address().port}`;
      await assert.rejects(psiCatClient.queryPsiCat({
        baseUrl: endpoint, session: { cookie: '' },
        body: { query: 'sensitive context', context_envelope: { request_id: 'redirect-test' } },
      }), /fetch failed/);
      const state = core.createInitialState();
      state.sync.accountEmail = 'test@example.invalid';
      await assert.rejects(syncTransport.pushSyncToBackend({ state, endpoint, core }), /fetch failed/);
      await assert.rejects(syncTransport.pullSyncFromBackend({ state, endpoint, core }), /fetch failed/);
      assert.deepEqual(paths, [
        '/api/psicat/status', ...(!redirectStatus ? ['/api/psicat'] : []),
        '/api/sync/push', '/api/sync/pull?account_email=test%40example.invalid',
      ]);
      assert.equal(redirectedRequests, 0);
    } finally {
      if (redirect) await close(redirect);
      await close(target);
    }
  });
}
