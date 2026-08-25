/**
 * public-site/js/19-ox-navigator.js
 * OX Navigator — Product 20
 *
 * Handles: status check, query dispatch to /api/ox, response rendering,
 * session history, gate-badge extraction, and temperature control.
 *
 * Requires backend: bot/assistant_api.py with OPENROUTER_API_KEY set.
 * Model: stealth/ox-alpha via OpenRouter.
 *
 * Theory & scientific direction: ThomasCory Walker-Pearson.
 * Code, engineering: GitHub Copilot (AI).
 * Open science artifact — public domain.
 */

(function () {
  'use strict';

  // ── Config ───────────────────────────────────────────────────────────────────
  const API_BASE = (window.AZ_API_BASE || 'https://api.axiomzerospc.org').replace(/\/$/, '');
  const MAX_HISTORY = 12;
  const GATE_LABELS = ['HARDGATE', 'ADJACENT_TRACK', 'OPEN_GAP', 'ARCHITECTURE_LIMIT', 'GOVERNANCE'];

  // ── Example queries ──────────────────────────────────────────────────────────
  const EXAMPLES = [
    'Which pillar closes the Δm²₂₁ tension?',
    'List all OPEN_GAP claims and their current σ tensions.',
    'What Lean4 theorems cover winding number selection n_w=5?',
    'Summarise the birefringence falsification conditions for LiteBIRD.',
    'Which pillars address the CMB amplitude suppression (Admission 1)?',
    'What is the difference between a hardgate pillar and an adjacent track?',
    'Which tests cover the holographic entropy-area relation (Pillar 4)?',
    'Explain the HILS governance boundary (SEPARATION.md).',
  ];

  // ── Session state ────────────────────────────────────────────────────────────
  let history = [];
  let lastAnswer = '';

  // ── DOM refs ─────────────────────────────────────────────────────────────────
  function el(id) { return document.getElementById(id); }

  // ── Init ─────────────────────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    renderChips();
    checkOxStatus();
    wireTemp();
    el('ox-query-input').addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { oxSend(); }
    });
  });

  // ── Example chips ─────────────────────────────────────────────────────────────
  function renderChips() {
    const wrap = el('ox-chips');
    if (!wrap) return;
    EXAMPLES.forEach(function (q) {
      const chip = document.createElement('button');
      chip.className = 'ox-chip';
      chip.textContent = q;
      chip.addEventListener('click', function () {
        el('ox-query-input').value = q;
        el('ox-query-input').focus();
      });
      wrap.appendChild(chip);
    });
  }

  // ── Temperature control ───────────────────────────────────────────────────────
  function wireTemp() {
    const slider = el('ox-temp');
    const valEl  = el('ox-temp-val');
    if (!slider || !valEl) return;
    slider.addEventListener('input', function () { valEl.textContent = slider.value; });
  }

  // ── Status check ─────────────────────────────────────────────────────────────
  async function checkOxStatus() {
    const dot  = el('ox-status-dot');
    const text = el('ox-status-text');
    const meta = el('ox-status-meta');
    try {
      const resp = await fetch(API_BASE + '/api/ox/status', { method: 'GET' });
      if (resp.ok) {
        const data = await resp.json();
        if (data.ox_available) {
          dot.className  = 'ox-status-dot ok';
          text.textContent = 'OX Alpha ready · ' + data.model;
          meta.textContent = data.context_pack_exists
            ? '· context pack loaded'
            : '· context pack missing (run ox_context_pack.py)';
        } else {
          dot.className  = 'ox-status-dot';
          text.textContent = 'OX Alpha unavailable — OPENROUTER_API_KEY not set on backend.';
          meta.textContent = '';
        }
      } else {
        dot.className  = 'ox-status-dot';
        text.textContent = 'Backend unreachable (HTTP ' + resp.status + '). Running in demo mode.';
        meta.textContent = '';
      }
    } catch (err) {
      dot.className  = 'ox-status-dot';
      text.textContent = 'Backend not reachable — running offline demo mode.';
      meta.textContent = String(err).slice(0, 60);
    }
  }

  // ── Send query ────────────────────────────────────────────────────────────────
  window.oxSend = async function () {
    const input  = el('ox-query-input');
    const query  = (input.value || '').trim();
    if (!query) { input.focus(); return; }

    const btn      = el('ox-send-btn');
    const spinner  = el('ox-spinner');
    const respCard = el('ox-response-card');
    const answer   = el('ox-answer');

    btn.disabled = true;
    spinner.classList.add('active');
    respCard.classList.remove('visible');

    const fullCtx = el('ox-full-ctx') ? el('ox-full-ctx').checked : true;
    const temp    = el('ox-temp')     ? parseFloat(el('ox-temp').value) : 0.2;
    const t0      = Date.now();

    try {
      const resp = await fetch(API_BASE + '/api/ox', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query, use_full_context: fullCtx, temperature: temp }),
      });

      const elapsed = ((Date.now() - t0) / 1000).toFixed(1);

      if (resp.ok) {
        const data = await resp.json();
        renderResponse(data, query, elapsed);
        addHistory(query, data.answer);
      } else {
        const errText = await resp.text().catch(() => 'Unknown error');
        renderError('API error ' + resp.status + ': ' + errText.slice(0, 200));
      }
    } catch (err) {
      renderError('Network error: ' + String(err));
    } finally {
      btn.disabled = false;
      spinner.classList.remove('active');
    }
  };

  // ── Render response ───────────────────────────────────────────────────────────
  function renderResponse(data, query, elapsed) {
    const respCard = el('ox-response-card');
    const ansEl    = el('ox-answer');
    const metaEl   = el('ox-response-meta');
    const gateStrip = el('ox-gate-strip');

    lastAnswer = data.answer || '';
    ansEl.textContent = lastAnswer;
    metaEl.textContent = data.model + ' · ' + elapsed + 's · ' + data.context_source;

    // Gate badges
    gateStrip.innerHTML = '';
    const found = [];
    GATE_LABELS.forEach(function (g) {
      if (lastAnswer.includes(g)) found.push(g);
    });
    if (found.length === 0) found.push('GOVERNANCE');  // always show governance badge
    found.forEach(function (g) {
      const badge = document.createElement('span');
      badge.className = 'ox-gate-badge gate-' + (g === 'GOVERNANCE' ? 'GOV' : g);
      badge.textContent = g;
      gateStrip.appendChild(badge);
    });

    respCard.classList.add('visible');
    respCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function renderError(msg) {
    const respCard = el('ox-response-card');
    const ansEl    = el('ox-answer');
    const gateStrip = el('ox-gate-strip');
    ansEl.textContent = '⚠️ ' + msg;
    gateStrip.innerHTML = '';
    lastAnswer = '';
    respCard.classList.add('visible');
  }

  // ── Copy ──────────────────────────────────────────────────────────────────────
  window.oxCopy = function () {
    if (!lastAnswer) return;
    navigator.clipboard.writeText(lastAnswer).catch(function () {
      const ta = document.createElement('textarea');
      ta.value = lastAnswer;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    });
  };

  // ── Clear ─────────────────────────────────────────────────────────────────────
  window.oxClear = function () {
    el('ox-query-input').value = '';
    el('ox-response-card').classList.remove('visible');
    el('ox-spinner').classList.remove('active');
    lastAnswer = '';
    el('ox-query-input').focus();
  };

  // ── Session history ───────────────────────────────────────────────────────────
  function addHistory(query, answer) {
    history.unshift({ query: query, answer: answer, ts: new Date().toISOString() });
    if (history.length > MAX_HISTORY) history.pop();
    renderHistory();
  }

  function renderHistory() {
    const wrap = el('ox-history');
    const list = el('ox-history-list');
    if (!wrap || !list) return;
    if (history.length === 0) { wrap.style.display = 'none'; return; }
    wrap.style.display = 'block';
    list.innerHTML = '';
    history.forEach(function (item) {
      const div = document.createElement('div');
      div.className = 'ox-history-item';
      div.innerHTML =
        '<div class="ox-history-q">' + escHtml(item.query) + '</div>' +
        '<div class="ox-history-ts">' + item.ts.replace('T', ' ').slice(0, 19) + ' UTC</div>';
      div.addEventListener('click', function () {
        el('ox-query-input').value = item.query;
        el('ox-response-card').classList.add('visible');
        el('ox-answer').textContent = item.answer;
        lastAnswer = item.answer;
      });
      list.appendChild(div);
    });
  }

  // ── Helpers ───────────────────────────────────────────────────────────────────
  function escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

}());
