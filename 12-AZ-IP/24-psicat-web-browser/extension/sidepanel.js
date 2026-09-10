function normalizeText(text) {
  return String(text || '').replace(/\s+/g, ' ').trim();
}

async function getStorage() {
  return chrome.storage.local.get(['notebook', 'rememberedPages', 'psicatEndpoint']);
}

async function setStorage(patch) {
  return chrome.storage.local.set(patch);
}

async function capturePage() {
  return chrome.runtime.sendMessage({ type: 'PSICAT_GET_ACTIVE_PAGE' });
}

function renderNotebook(entries) {
  const wrap = document.getElementById('notebook-list');
  wrap.innerHTML = '';
  entries.forEach((entry) => {
    const div = document.createElement('div');
    div.className = 'note';
    const title = document.createElement('strong');
    title.textContent = entry.title;
    const body = document.createElement('div');
    body.textContent = entry.text.slice(0, 240);
    div.append(title, body);
    wrap.appendChild(div);
  });
}

function localSummary(question, page, notebook) {
  const lines = [];
  if (page) lines.push(`Active page: ${page.title} (${page.url})`);
  if (page && page.text) lines.push(`Page excerpt: ${normalizeText(page.selection || page.text).slice(0, 600)}`);
  if (notebook.length) lines.push(`Notebook matches: ${notebook.map((note) => note.title).join('; ')}`);
  if (question) lines.push(`Question: ${question}`);
  return lines.join('\n');
}

async function askPsiCat(question, page) {
  const { notebook = [], rememberedPages = [], psicatEndpoint = 'http://127.0.0.1:8020' } = await getStorage();
  const payload = {
    current_page: page,
    remembered_pages: rememberedPages.slice(0, 5),
    notebook_entries: notebook.slice(0, 8),
  };
  try {
    const statusRes = await fetch(`${psicatEndpoint}/api/psicat/status`);
    const statusBody = await statusRes.json();
    const challenge = statusRes.headers.get('X-PsiCat-Handshake-Challenge') || statusBody?.session_contract?.handshake?.challenge;
    const receipt = statusRes.headers.get('X-PsiCat-Handshake-Receipt') || statusBody?.session_contract?.handshake?.receipt;
    const token = statusBody?.memory_profile_token;
    if (!challenge || !receipt || !token) throw new Error('PsiCat handshake unavailable');
    const proofBuffer = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(`${challenge}:${token}`));
    const proof = Array.from(new Uint8Array(proofBuffer)).map((byte) => byte.toString(16).padStart(2, '0')).join('');
    const answerRes = await fetch(`${psicatEndpoint}/api/psicat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: question,
        page_context: normalizeText(page?.text || page?.selection || '').slice(0, 4000),
        context_envelope: payload,
        memory_profile_token: token,
        psicat_handshake_challenge: challenge,
        psicat_handshake_receipt: receipt,
        psicat_handshake_proof: proof,
      }),
    });
    const answerBody = await answerRes.json();
    return answerBody.answer || answerBody.body || JSON.stringify(answerBody, null, 2);
  } catch (_error) {
    return `[Local mode]\n${localSummary(question, page, notebook)}`;
  }
}

async function boot() {
  let storage = await getStorage();
  renderNotebook(storage.notebook || []);

  document.getElementById('capture-page').addEventListener('click', async () => {
    const page = await capturePage();
    storage = await getStorage();
    const current = (storage.rememberedPages || []);
    current.unshift({ ...page, capturedAt: new Date().toISOString() });
    await setStorage({ rememberedPages: current.slice(0, 24) });
    document.getElementById('answer').textContent = localSummary('Captured page', page, storage.notebook || []);
  });

  document.getElementById('save-note').addEventListener('click', async () => {
    storage = await getStorage();
    const title = document.getElementById('note-title').value.trim() || 'Notebook note';
    const text = document.getElementById('note-text').value.trim();
    if (!text) return;
    const fresh = [{ title, text, createdAt: new Date().toISOString() }, ...(storage.notebook || [])].slice(0, 100);
    await setStorage({ notebook: fresh });
    storage = { ...storage, notebook: fresh };
    renderNotebook(fresh);
  });

  document.getElementById('ask-psicat').addEventListener('click', async () => {
    const page = await capturePage();
    const question = document.getElementById('question').value.trim();
    document.getElementById('answer').textContent = await askPsiCat(question, page);
  });

  document.getElementById('import-notes').addEventListener('click', () => document.getElementById('import-file').click());
  document.getElementById('import-file').addEventListener('change', async (event) => {
    storage = await getStorage();
    const file = event.target.files[0];
    if (!file) return;
    const text = await file.text();
    let entries;
    try {
      entries = JSON.parse(text);
    } catch (_error) {
      entries = [{ title: file.name, text }];
    }
    const merged = [...entries, ...(storage.notebook || [])].slice(0, 100);
    await setStorage({ notebook: merged });
    storage = { ...storage, notebook: merged };
    renderNotebook(merged);
  });

  document.getElementById('export-notes').addEventListener('click', async () => {
    storage = await getStorage();
    const blob = new Blob([JSON.stringify(storage.notebook || [], null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    await chrome.downloads.download({ url, filename: 'psicat-extension-notebook.json', saveAs: true });
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
}

boot();
