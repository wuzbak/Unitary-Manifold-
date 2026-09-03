/**
 * Merlin — Product 20 frontend shell
 *
 * Structured response rendering, localStorage-backed active session memory,
 * follow-up chips, source cards, and compatibility with the standalone
 * Merlin backend endpoints.
 */

(function () {
  'use strict';

  const API_BASE = (window.AZ_API_BASE || window.location.origin).replace(/\/$/, '');
  const STORAGE_KEY = 'merlin_active_session';
  const MAX_HISTORY = 50;
  const GATE_LABELS = ['HARDGATE', 'ADJACENT_TRACK', 'OPEN_GAP', 'ARCHITECTURE_LIMIT', 'GOVERNANCE'];
  const EXAMPLES = [
    'What is the current birefringence falsifier and which gate does it sit under?',
    'Explain the difference between HARDGATE, OPEN_GAP, and ARCHITECTURE_LIMIT.',
    'Which pillar should I read first if I want the cleanest entry into the framework?',
    'Summarise the current open tensions and tell me what LiteBIRD could falsify.',
    'Use fourth-wall mode to explain why k_CS = 74 matters.',
    'Trace this through the interrogator knowledge base and point me to the closest pillar.',
  ];
  const THOUGHTS = [
    'Merlin is aligning gate badges…',
    'Merlin is checking the nearest pillar trail…',
    'Merlin is combing the fallibility register…',
    'Merlin is keeping the architecture limits visible…',
  ];

  let history = [];
  let lastResponse = null;
  let thoughtTimer = null;
  let thoughtIndex = 0;

  function el(id) { return document.getElementById(id); }

  document.addEventListener('DOMContentLoaded', function () {
    loadHistory();
    renderChips();
    renderHistory();
    checkMerlinStatus();
    const input = el('ox-query-input');
    if (input) {
      input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) merlinSend();
      });
    }
  });

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

  function checkMerlinStatus() {
    const dot = el('ox-status-dot');
    const text = el('ox-status-text');
    const meta = el('ox-status-meta');
    fetch(API_BASE + '/api/merlin/status')
      .then(function (resp) { return resp.ok ? resp.json() : Promise.reject(new Error('HTTP ' + resp.status)); })
      .then(function (data) {
        const repo = data.live_status || {};
        const live = data.live_model_available ? 'live model ready' : 'offline RAG fallback ready';
        dot.className = 'ox-status-dot ok';
        text.textContent = 'Merlin available · ' + live;
        meta.textContent = 'v' + ((repo.meta && repo.meta.version) || 'unknown') +
          ' · ' + (((repo.tests || {}).passed || 0).toLocaleString()) + ' tests' +
          ' · ' + (((repo.lean4 || {}).theorem_count || 0).toLocaleString()) + ' Lean4';
      })
      .catch(function () {
        dot.className = 'ox-status-dot';
        text.textContent = 'Merlin backend unreachable — local page shell only.';
        meta.textContent = '';
      });
  }

  function startThoughts() {
    const spinner = el('ox-spinner');
    const thoughts = el('ox-thoughts');
    if (!spinner || !thoughts) return;
    spinner.classList.add('active');
    thoughtIndex = 0;
    thoughts.textContent = THOUGHTS[thoughtIndex];
    clearInterval(thoughtTimer);
    thoughtTimer = setInterval(function () {
      thoughtIndex = (thoughtIndex + 1) % THOUGHTS.length;
      thoughts.textContent = THOUGHTS[thoughtIndex];
    }, 900);
  }

  function stopThoughts() {
    const spinner = el('ox-spinner');
    if (spinner) spinner.classList.remove('active');
    clearInterval(thoughtTimer);
    thoughtTimer = null;
  }

  function parseMerlinResponse(answer) {
    const text = String(answer || '');
    const split = text.split('\n---\n');
    const body = split[0] || text;
    const rest = split[1] || '';
    const followups = [];
    const sources = [];
    let section = '';
    rest.split('\n').forEach(function (line) {
      if (line.startsWith('FOLLOWUPS:')) { section = 'followups'; return; }
      if (line.startsWith('Sources:')) { section = 'sources'; return; }
      if (section === 'followups') {
        const match = line.match(/^\d+\.\s+(.*)$/);
        if (match) followups.push(match[1]);
      } else if (section === 'sources') {
        const match = line.match(/^- (.*?) \| (.*?) \| (.*)$/);
        if (match) sources.push({ label: match[1], type: match[2], description: match[3] });
      }
    });
    return { body: body.trim(), followups: followups, sources: sources };
  }

  function extractGateBadges(text) {
    const sample = String(text || '');
    return GATE_LABELS.filter(function (gate) { return sample.indexOf(gate) !== -1; });
  }

  window.merlinSend = async function () {
    const input = el('ox-query-input');
    const query = (input.value || '').trim();
    if (!query) { input.focus(); return; }
    const btn = el('ox-send-btn');
    btn.disabled = true;
    startThoughts();
    el('ox-response-card').classList.remove('visible');

    const payload = {
      query: query,
      fourth_wall: !!(el('ox-fourth-wall') && el('ox-fourth-wall').checked),
      websearch: !!(el('ox-websearch') && el('ox-websearch').checked),
      page_context: 'Product 20 Merlin shell',
    };
    const t0 = Date.now();

    try {
      const resp = await fetch(API_BASE + '/api/merlin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const elapsed = ((Date.now() - t0) / 1000).toFixed(1);
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || ('HTTP ' + resp.status));
      renderResponse(data, query, elapsed);
      addHistory(query, data);
    } catch (err) {
      renderError(String(err));
    } finally {
      btn.disabled = false;
      stopThoughts();
    }
  };

  function renderResponse(data, query, elapsed) {
    const parsed = data.body ? {
      body: data.body,
      followups: data.followups || [],
      sources: data.sources || [],
    } : parseMerlinResponse(data.answer);
    lastResponse = {
      query: query,
      answer: data.answer,
      body: parsed.body,
      followups: parsed.followups,
      sources: parsed.sources,
      gate_badges: data.gate_badges || extractGateBadges(data.answer || parsed.body),
      persona_mode: data.persona_mode || 'storyteller',
      context_source: data.context_source || 'unknown',
    };

    el('ox-response-title').textContent = 'Merlin Response';
    el('ox-answer').textContent = parsed.body;
    el('ox-response-meta').textContent =
      (lastResponse.persona_mode || 'storyteller') + ' · ' + elapsed + 's · ' + lastResponse.context_source;

    renderGateStrip(lastResponse.gate_badges);
    renderFollowups(parsed.followups);
    renderSources(parsed.sources);
    el('ox-response-card').classList.add('visible');
    el('ox-response-card').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function renderGateStrip(gates) {
    const wrap = el('ox-gate-strip');
    wrap.innerHTML = '';
    (gates || []).forEach(function (gate) {
      const badge = document.createElement('span');
      badge.className = 'ox-gate-badge gate-' + gate;
      badge.textContent = gate;
      wrap.appendChild(badge);
    });
    if (!wrap.children.length) {
      const badge = document.createElement('span');
      badge.className = 'ox-gate-badge gate-ARCHITECTURE_LIMIT';
      badge.textContent = 'NO_DIRECT_GATE';
      wrap.appendChild(badge);
    }
  }

  function renderFollowups(followups) {
    const wrap = el('ox-followups');
    wrap.innerHTML = '';
    (followups || []).forEach(function (item) {
      const btn = document.createElement('button');
      btn.className = 'ox-chip';
      btn.textContent = item;
      btn.addEventListener('click', function () {
        el('ox-query-input').value = item;
        el('ox-query-input').focus();
      });
      wrap.appendChild(btn);
    });
  }

  function renderSources(sources) {
    const wrap = el('ox-sources');
    wrap.innerHTML = '';
    (sources || []).forEach(function (source) {
      const card = document.createElement('div');
      card.className = 'ox-source-card';
      const type = document.createElement('div');
      type.className = 'ox-source-type';
      type.textContent = source.type || 'SOURCE';
      const label = document.createElement('div');
      label.className = 'ox-source-label';
      label.textContent = source.label || '';
      const desc = document.createElement('div');
      desc.className = 'ox-source-desc';
      desc.textContent = source.description || '';
      card.appendChild(type);
      card.appendChild(label);
      card.appendChild(desc);
      wrap.appendChild(card);
    });
  }

  function renderError(msg) {
    el('ox-response-title').textContent = 'Merlin Error';
    el('ox-answer').textContent = '⚠️ ' + msg;
    el('ox-response-meta').textContent = 'offline';
    renderGateStrip([]);
    renderFollowups([]);
    renderSources([]);
    el('ox-response-card').classList.add('visible');
    lastResponse = null;
  }

  function addHistory(query, data) {
    history.unshift({
      query: query,
      response: data.answer,
      body: data.body || parseMerlinResponse(data.answer).body,
      followups: data.followups || [],
      sources: data.sources || [],
      gate_badges: data.gate_badges || [],
      persona_mode: data.persona_mode || 'storyteller',
      context_source: data.context_source || 'unknown',
      ts: new Date().toISOString(),
    });
    if (history.length > MAX_HISTORY) history = history.slice(0, MAX_HISTORY);
    saveHistory();
    renderHistory();
  }

  function renderHistory() {
    const wrap = el('ox-history');
    const list = el('ox-history-list');
    if (!wrap || !list) return;
    if (!history.length) { wrap.style.display = 'none'; return; }
    wrap.style.display = 'block';
    list.innerHTML = '';
    history.forEach(function (item) {
      const div = document.createElement('div');
      div.className = 'ox-history-item';
      const question = document.createElement('div');
      question.className = 'ox-history-q';
      question.textContent = item.query;
      const ts = document.createElement('div');
      ts.className = 'ox-history-ts';
      ts.textContent = item.ts.replace('T', ' ').slice(0, 19) + ' UTC';
      div.appendChild(question);
      div.appendChild(ts);
      div.addEventListener('click', function () {
        renderResponse({
          answer: item.response,
          body: item.body,
          followups: item.followups,
          sources: item.sources,
          gate_badges: item.gate_badges,
          persona_mode: item.persona_mode,
          context_source: item.context_source,
        }, item.query, '0.0');
      });
      list.appendChild(div);
    });
  }

  function saveHistory() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(history)); } catch (e) {}
  }

  function loadHistory() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      history = raw ? JSON.parse(raw) : [];
    } catch (e) {
      history = [];
    }
  }

  window.oxCopy = function () {
    if (!lastResponse || !lastResponse.answer) return;
    navigator.clipboard.writeText(lastResponse.answer).catch(function () {});
  };

  window.oxClear = function () {
    el('ox-query-input').value = '';
    el('ox-response-card').classList.remove('visible');
    lastResponse = null;
  };

  window.oxResetSession = function () {
    history = [];
    saveHistory();
    renderHistory();
    window.oxClear();
  };
}());
