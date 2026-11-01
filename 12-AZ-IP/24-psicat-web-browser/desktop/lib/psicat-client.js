const { createHash } = require('node:crypto');
const { buildContextEnvelope } = require('./page-context');

const QUERY_TIMEOUT_MS = 35_000;
const MAX_QUESTION_CHARACTERS = 4000;
const MAX_CONTEXT_BYTES = 32_000;

function buildPageQuery({ state, question, requestId, includeLibrary = false }) {
  if (typeof question !== 'string' || !question.trim() || question.length > MAX_QUESTION_CHARACTERS) {
    throw new Error('A nonempty question of at most 4000 characters is required.');
  }
  if (typeof requestId !== 'string' || !/^[a-zA-Z0-9-]{1,80}$/.test(requestId)) {
    throw new Error('A valid request correlation ID is required.');
  }
  const activeTab = (state.tabs || []).find((tab) => tab.id === state.activeTabId) || state.tabs?.[0];
  if (activeTab?.private || activeTab?.lastSnapshot?.private) {
    throw new Error('Private-tab context is not sent to PsiCat. Use local research or a non-private tab.');
  }
  const envelope = buildContextEnvelope(state, { includeLibrary: includeLibrary === true });
  const snapshot = activeTab?.lastSnapshot;
  const pageText = String(snapshot?.selection || snapshot?.text || '').slice(0, 4000);
  const body = {
    query: question.trim(),
    page_context: pageText,
    user_context: 'PsiCat Browser Product 24 desktop shell',
    websearch: false,
    context_envelope: {
      ...envelope,
      schema: 'psicat_browser_query_v1',
      request_id: requestId,
      source: 'product24_desktop',
      captured_at: snapshot?.capturedAt || null,
      sharing: includeLibrary === true ? 'page_and_nonprivate_library' : 'current_page_only',
      consent: 'explicit_query',
    },
  };
  if (Buffer.byteLength(JSON.stringify(body), 'utf8') > MAX_CONTEXT_BYTES) {
    throw new Error('Browser query context exceeds the 32000-byte transport budget.');
  }
  return body;
}

async function queryPsiCat({ baseUrl, body, signal, session, fetchImpl = fetch, timeoutMs = QUERY_TIMEOUT_MS }) {
  const deadline = AbortSignal.timeout(timeoutMs);
  const requestSignal = signal ? AbortSignal.any([signal, deadline]) : deadline;
  requestSignal.throwIfAborted();
  const status = await fetchImpl(`${baseUrl}/api/psicat/status`, {
    signal: requestSignal,
    headers: session?.cookie ? { Cookie: session.cookie } : {},
  });
  if (!status.ok) throw new Error(`PsiCat status failed (HTTP ${status.status}).`);
  const statusPayload = await status.json();
  const challenge = status.headers.get('X-PsiCat-Handshake-Challenge') || statusPayload?.session_contract?.handshake?.challenge;
  const receipt = status.headers.get('X-PsiCat-Handshake-Receipt') || statusPayload?.session_contract?.handshake?.receipt;
  const token = statusPayload?.memory_profile_token;
  if (![challenge, receipt, token].every((value) => typeof value === 'string' && value)) {
    throw new Error('Missing PsiCat handshake material.');
  }
  const cookies = status.headers.getSetCookie()
    .map((cookie) => cookie.split(';', 1)[0])
    .filter((cookie) => /^(psicat_profile_id|merlin_profile_id)=[^;\s,]+$/.test(cookie))
    .join('; ');
  if (!cookies) throw new Error('Missing PsiCat session cookie.');
  if (session) session.cookie = cookies;
  const response = await fetchImpl(`${baseUrl}/api/psicat`, {
    method: 'POST',
    signal: requestSignal,
    headers: { 'Content-Type': 'application/json', Cookie: cookies },
    body: JSON.stringify({
      ...body,
      psicat_handshake_profile_token: token,
      psicat_handshake_challenge: challenge,
      psicat_handshake_receipt: receipt,
      psicat_handshake_proof: createHash('sha256').update(`${challenge}:${token}`).digest('hex'),
    }),
  });
  if (!response.ok) throw new Error(`PsiCat query failed (HTTP ${response.status}).`);
  const payload = await response.json();
  const answer = typeof payload?.answer === 'string' && payload.answer.trim() ? payload.answer : payload?.body;
  if (typeof answer !== 'string' || !answer.trim()) {
    throw new Error('PsiCat returned no valid answer.');
  }
  return {
    mode: 'psicat',
    request_id: body.context_envelope.request_id,
    source_url: body.context_envelope.current_page?.url || '',
    sharing: body.context_envelope.sharing,
    answer,
    provenance: payload.provenance || null,
  };
}

module.exports = { buildPageQuery, queryPsiCat, QUERY_TIMEOUT_MS, MAX_CONTEXT_BYTES };
