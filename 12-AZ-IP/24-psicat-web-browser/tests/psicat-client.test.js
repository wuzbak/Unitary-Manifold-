const test = require('node:test');
const assert = require('node:assert/strict');
const { createHash } = require('node:crypto');
const { createServer } = require('node:http');
const { buildPageQuery, queryPsiCat, MAX_CONTEXT_BYTES } = require('../desktop/lib/psicat-client');
const { buildContextEnvelope } = require('../desktop/lib/page-context');

function fixture() {
  return {
    activeTabId: 'active',
    tabs: [{
      id: 'active', private: false,
      lastSnapshot: { title: 'Synthetic page', url: 'https://example.com/page', text: 'PAGE-MARKER', selection: 'SELECTION-MARKER', capturedAt: '2026-11-01T00:00:00Z' },
    }],
    rememberedPages: [{ title: 'Saved', text: 'SAVED-MARKER' }, { title: 'Private saved', text: 'SECRET', private: true }],
    notebookEntries: [{ title: 'Note', text: 'NOTE-MARKER' }, { title: 'Private note', text: 'SECRET', private: true }],
    importedResearch: [{ title: 'Import', text: 'IMPORT-MARKER' }, { title: 'Private import', text: 'SECRET', private: true }],
  };
}

function body(options = {}) {
  return buildPageQuery({ state: fixture(), question: 'Explain the selected evidence', requestId: 'request-123', ...options });
}

test('explicit query defaults to current page, selection and correlation without stored context', () => {
  const state = fixture();
  const before = JSON.stringify(state);
  const request = body({ state });
  assert.equal(request.page_context, 'SELECTION-MARKER');
  assert.equal(request.websearch, false);
  assert.equal(request.context_envelope.request_id, 'request-123');
  assert.equal(request.context_envelope.consent, 'explicit_query');
  assert.equal(request.context_envelope.sharing, 'current_page_only');
  assert.deepEqual(request.context_envelope.notebook_entries, []);
  assert.deepEqual(request.context_envelope.remembered_pages, []);
  assert.deepEqual(request.context_envelope.imported_research, []);
  assert.equal(JSON.stringify(state), before);
});

test('library opt-in excludes private artifacts from every collection', () => {
  const request = body({ includeLibrary: true });
  assert.equal(request.context_envelope.notebook_entries.length, 1);
  assert.equal(request.context_envelope.remembered_pages.length, 1);
  assert.equal(request.context_envelope.imported_research.length, 1);
  assert.doesNotMatch(JSON.stringify(request), /SECRET|Private/);
});

test('private active tab blocks transport and excludes stored library from local envelope', () => {
  const state = fixture();
  state.tabs[0].private = true;
  assert.throws(() => body({ state, includeLibrary: true }), /Private-tab context/);
  assert.deepEqual(buildContextEnvelope(state).notebook_entries, []);
  state.tabs[0].private = false;
  state.tabs[0].lastSnapshot.private = true;
  assert.throws(() => body({ state }), /Private-tab context/);
  state.activeTabId = 'missing';
  assert.throws(() => body({ state }), /Private-tab context/);
  assert.deepEqual(buildContextEnvelope(state).notebook_entries, []);
});

test('invalid question, correlation and oversized multibyte context are explicit errors', () => {
  assert.throws(() => body({ question: ' ' }), /nonempty question/);
  assert.throws(() => body({ question: 'x'.repeat(4001) }), /4000/);
  assert.throws(() => body({ requestId: '../unsafe' }), /correlation/);
  const state = fixture();
  state.notebookEntries = Array.from({ length: 12 }, () => ({ title: 'Large', text: '界'.repeat(1200) }));
  assert.throws(() => body({ state, includeLibrary: true }), /32000-byte/);
  assert.ok(Buffer.byteLength(JSON.stringify(state), 'utf8') > MAX_CONTEXT_BYTES);
});

test('real loopback HTTP handshake and query preserve exact context and return provenance', async () => {
  const requests = [];
  const statusCookies = [];
  const server = createServer(async (request, response) => {
    response.setHeader('Content-Type', 'application/json');
    if (request.url === '/api/psicat/status') {
      statusCookies.push(request.headers.cookie || '');
      response.setHeader('Set-Cookie', 'psicat_profile_id=synthetic-cookie; HttpOnly; Path=/');
      response.end(JSON.stringify({
        memory_profile_token: 'synthetic-token',
        session_contract: { handshake: { challenge: 'challenge', receipt: 'receipt' } },
      }));
      return;
    }
    let text = '';
    for await (const chunk of request) text += chunk;
    requests.push(JSON.parse(text));
    assert.equal(request.headers.cookie, 'psicat_profile_id=synthetic-cookie');
    response.end(JSON.stringify({ answer: 'Synthetic evidence response', provenance: { complete: true, sources: ['fixture'] } }));
  });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  try {
    const request = body();
    const session = { cookie: '' };
    const options = { baseUrl: `http://127.0.0.1:${server.address().port}`, body: request, session };
    const result = await queryPsiCat(options);
    await queryPsiCat(options);
    assert.deepEqual(statusCookies, ['', 'psicat_profile_id=synthetic-cookie']);
    assert.deepEqual(requests[0].context_envelope, request.context_envelope);
    assert.equal(requests[0].page_context, 'SELECTION-MARKER');
    assert.equal(requests[0].psicat_handshake_proof, createHash('sha256').update('challenge:synthetic-token').digest('hex'));
    assert.equal(result.request_id, 'request-123');
    assert.equal(result.source_url, 'https://example.com/page');
    assert.equal(result.provenance.complete, true);
    assert.ok(!JSON.stringify(result).includes('synthetic-token'));
  } finally {
    server.closeAllConnections();
    await new Promise((resolve) => server.close(resolve));
  }
});

test('HTTP errors, missing handshake/session and empty answers cannot look successful', async () => {
  for (const failure of ['status', 'handshake', 'session', 'query', 'empty']) {
    let calls = 0;
    const fetchImpl = async () => {
      calls += 1;
      if (calls === 1) return new Response(JSON.stringify(failure === 'handshake' ? {} : {
        memory_profile_token: 'token', session_contract: { handshake: { challenge: 'challenge', receipt: 'receipt' } },
      }), {
        status: failure === 'status' ? 503 : 200,
        headers: failure === 'session' ? {} : { 'Set-Cookie': 'psicat_profile_id=synthetic-cookie; HttpOnly' },
      });
      return new Response(JSON.stringify({ answer: ' ' }), { status: failure === 'query' ? 403 : 200 });
    };
    await assert.rejects(queryPsiCat({ baseUrl: 'http://unused', body: body(), fetchImpl }), /HTTP|handshake|session cookie|valid answer/);
  }
});

test('legacy body-only responses remain valid without accepting arbitrary JSON as an answer', async () => {
  let calls = 0;
  const fetchImpl = async () => new Response(JSON.stringify(++calls === 1
    ? { memory_profile_token: 'token', session_contract: { handshake: { challenge: 'challenge', receipt: 'receipt' } } }
    : { body: 'Legacy valid answer' }), { headers: { 'Set-Cookie': 'psicat_profile_id=synthetic-cookie; HttpOnly' } });
  const result = await queryPsiCat({ baseUrl: 'http://unused', body: body(), fetchImpl });
  assert.equal(result.answer, 'Legacy valid answer');
});

test('pre-cancelled requests perform no fetch; deadlines abort in-flight work', async () => {
  const controller = new AbortController();
  controller.abort();
  await assert.rejects(queryPsiCat({
    baseUrl: 'http://unused', body: body(), signal: controller.signal,
    fetchImpl: () => assert.fail('Cancelled request must not fetch.'),
  }), { name: 'AbortError' });
  const keepAlive = setTimeout(() => {}, 100);
  try {
    await assert.rejects(queryPsiCat({
      baseUrl: 'http://unused', body: body(), timeoutMs: 10,
      fetchImpl: (_url, { signal }) => new Promise((_resolve, reject) => {
        signal.addEventListener('abort', () => reject(signal.reason), { once: true });
      }),
    }), { name: 'TimeoutError' });
  } finally {
    clearTimeout(keepAlive);
  }
});
