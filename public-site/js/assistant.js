/**
 * assistant.js — Persistent AI Assistant Widget
 * axiomzerospc.org open science portal
 *
 * Features:
 *  - Floating drawer on every page (right sidebar)
 *  - RAG-grounded responses via /api/assistant endpoint (or HF Inference fallback)
 *  - Anti-sycophancy: never simply agrees; cites pillars; flags confabulation risk
 *  - Anchor tracking: remembers session origin, warns on deep rabbit-hole traversal
 *  - Epistemic nudging: inline gate-status badges on physics claims
 *  - Websearch alignment (framed as "what does outside literature say?")
 *
 * AxiomZero Technologies & Consulting, SPC — UBI 606 239 876
 * Open science artifact — public domain
 */

(function(global) {
  'use strict';

  // ── Configuration ─────────────────────────────────────────────────────────
  var CFG = {
    apiEndpoints   : [
      '/api/assistant',
      'https://api.axiomzerospc.org/api/assistant'
    ],                                           // canonical API first, Base44 compatibility edge second
    hfEndpoint     : 'https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3',
    hfToken        : '',                         // Set via window.AZ_HF_TOKEN or env
    maxHops        : 3,                          // Rabbit-hole threshold
    storageKey     : 'az-assistant-session',
    systemPrompt   : [
      'You are the AxiomZero Open Science Assistant grounded in the Unitary Manifold physics framework.',
      'Rules you must never break:',
      '1. Always cite the relevant Pillar number and its epistemic gate (HARDGATE / ADJACENT_TRACK / OPEN_GAP) when answering a physics question.',
      '2. If you are uncertain, say so explicitly. Never confabulate facts or agree merely to satisfy the user.',
      '3. If the user makes an incorrect claim, correct it gently but firmly with evidence. Do not agree to be agreeable.',
      '4. When you use a websearch result, label it "External literature:" and note it may not align with UM predictions.',
      '5. Do not use the phrase "I am teaching you". Guide by offering the next node in the knowledge graph.',
      '6. Flag when you detect the user is more than 3 hops from their starting topic: offer an anchor card.',
      '7. Epistemic status labels: HARDGATE = formally closed pillar, ADJACENT_TRACK = not a hardgate claim, OPEN_GAP = documented open problem.',
      '8. Never use "ToE score" or "100% hardgate" language — these are misleading.',
    ].join(' '),
  };

  // ── Session state ─────────────────────────────────────────────────────────
  var state = {
    open       : false,
    messages   : [],
    hops       : 0,
    anchor     : null,          // { label, url } set on first user question
    pageCtx    : '',            // injected by each page
    searching  : false,
  };

  function saveState() {
    try {
      sessionStorage.setItem(CFG.storageKey, JSON.stringify({
        messages : state.messages.slice(-40),
        hops     : state.hops,
        anchor   : state.anchor,
      }));
    } catch(e) {}
  }

  function loadState() {
    try {
      var raw = sessionStorage.getItem(CFG.storageKey);
      if (raw) {
        var s = JSON.parse(raw);
        state.messages = s.messages || [];
        state.hops     = s.hops || 0;
        state.anchor   = s.anchor || null;
      }
    } catch(e) {}
  }

  // ── DOM builder ───────────────────────────────────────────────────────────
  function buildWidget() {
    // Inject CSS link if not present
    if (!document.getElementById('az-assistant-css')) {
      var l = document.createElement('link');
      l.id   = 'az-assistant-css';
      l.rel  = 'stylesheet';
      l.href = resolveRoot() + 'css/assistant.css';
      document.head.appendChild(l);
    }

    var wrapper = document.createElement('div');
    wrapper.id = 'az-assistant';
    wrapper.innerHTML = [
      '<button id="az-assistant-toggle" aria-label="Open AI Assistant" title="Open AI Assistant">',
        '<span class="az-a-icon">⊛</span>',
        '<span class="az-a-badge" id="az-a-badge" hidden></span>',
      '</button>',
      '<div id="az-assistant-drawer" role="dialog" aria-label="AxiomZero AI Assistant" aria-hidden="true">',
        '<div class="az-a-header">',
          '<div class="az-a-title">',
            '<span class="az-a-icon-sm">⊛</span>',
            '<span>AZ Assistant</span>',
            '<span class="az-a-tag">RAG · Anti-sycophancy</span>',
          '</div>',
          '<div class="az-a-header-actions">',
            '<button id="az-a-search-btn" title="Web alignment search" aria-label="Web alignment search">🌐</button>',
            '<button id="az-a-anchor-btn" title="Show anchor / breadcrumb" aria-label="Show anchor">⚓</button>',
            '<button id="az-a-clear-btn" title="Clear session" aria-label="Clear session">✕</button>',
            '<button id="az-a-close-btn" title="Close" aria-label="Close assistant">‹</button>',
          '</div>',
        '</div>',
        '<div id="az-a-anchor-bar" class="az-a-anchor-bar" hidden></div>',
        '<div id="az-a-messages" class="az-a-messages" role="log" aria-live="polite"></div>',
        '<div class="az-a-input-row">',
          '<textarea id="az-a-input" rows="2" placeholder="Ask about a pillar, concept, or tool…" aria-label="Message input"></textarea>',
          '<button id="az-a-send" aria-label="Send">↑</button>',
        '</div>',
        '<div class="az-a-footer">',
          'Open science artifact · <a href="https://axiomzerospc.org/portal/library/" target="_blank">Knowledge base</a>',
          ' · <a href="https://github.com/wuzbak/Unitary-Manifold-" target="_blank">Source</a>',
        '</div>',
      '</div>',
    ].join('');
    document.body.appendChild(wrapper);

    // Wire events
    document.getElementById('az-assistant-toggle').addEventListener('click', toggleDrawer);
    document.getElementById('az-a-close-btn').addEventListener('click', closeDrawer);
    document.getElementById('az-a-clear-btn').addEventListener('click', clearSession);
    document.getElementById('az-a-anchor-btn').addEventListener('click', showAnchorBar);
    document.getElementById('az-a-search-btn').addEventListener('click', triggerWebSearch);
    document.getElementById('az-a-send').addEventListener('click', sendMessage);
    document.getElementById('az-a-input').addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });
  }

  function resolveRoot() {
    // Try to find relative path back to public-site root
    var depth = (window.location.pathname.match(/\//g) || []).length - 1;
    if (depth <= 0) return '';
    return '../'.repeat(Math.max(0, depth - 1));
  }

  // ── Drawer controls ───────────────────────────────────────────────────────
  function toggleDrawer() {
    state.open ? closeDrawer() : openDrawer();
  }

  function openDrawer() {
    state.open = true;
    document.getElementById('az-assistant-drawer').classList.add('open');
    document.getElementById('az-assistant-drawer').setAttribute('aria-hidden', 'false');
    hideBadge();
    renderMessages();
    if (state.messages.length === 0) showWelcome();
    document.getElementById('az-a-input').focus();
  }

  function closeDrawer() {
    state.open = false;
    document.getElementById('az-assistant-drawer').classList.remove('open');
    document.getElementById('az-assistant-drawer').setAttribute('aria-hidden', 'true');
  }

  function clearSession() {
    state.messages = [];
    state.hops     = 0;
    state.anchor   = null;
    sessionStorage.removeItem(CFG.storageKey);
    renderMessages();
    showWelcome();
  }

  function hideBadge() {
    var b = document.getElementById('az-a-badge');
    if (b) b.hidden = true;
  }

  function showBadge() {
    var b = document.getElementById('az-a-badge');
    if (b) { b.hidden = false; b.textContent = '•'; }
  }

  // ── Welcome message ───────────────────────────────────────────────────────
  function showWelcome() {
    var ctx = state.pageCtx || 'this page';
    appendMessage('assistant', [
      'Hello. I\'m grounded in the Unitary Manifold knowledge base — 208+ physics pillars, ',
      'the live Lean4 theorem corpus, and the full AxiomZero product suite.',
      '\n\nI\'m on <strong>' + escHtml(ctx) + '</strong>. What would you like to explore? ',
      'I\'ll cite sources and flag open gaps honestly — and I\'ll push back if something ',
      'doesn\'t hold up.',
      '\n\n<span class="az-a-hint">Try: "What is Pillar 4?" · "How does the KK metric work?" ',
      '· "Show me open gaps" · "What does LiteBIRD test?"</span>',
    ].join(''));
  }

  // ── Anchor / breadcrumb ───────────────────────────────────────────────────
  function showAnchorBar() {
    var bar = document.getElementById('az-a-anchor-bar');
    if (!bar) return;
    if (state.anchor) {
      bar.hidden = false;
      bar.innerHTML = [
        '<span class="az-a-anchor-label">⚓ Anchor:</span> ',
        '<strong>' + escHtml(state.anchor.label) + '</strong>',
        state.hops > 0 ? ' · <span class="az-a-hops">' + state.hops + ' hop' + (state.hops !== 1 ? 's' : '') + ' deep</span>' : '',
        state.hops >= CFG.maxHops
          ? ' <span class="az-a-warn">rabbit-hole territory — want to return?</span>' +
            ' <button class="az-a-anchor-return" onclick="AZAssistant.returnToAnchor()">Return</button>'
          : '',
      ].join('');
    } else {
      bar.hidden = false;
      bar.innerHTML = '<span class="az-a-anchor-label">No anchor set yet — ask your first question to begin.</span>';
    }
  }

  function returnToAnchor() {
    if (state.anchor && state.anchor.url) window.location.href = state.anchor.url;
  }

  // ── Web search mode ───────────────────────────────────────────────────────
  function triggerWebSearch() {
    var inp = document.getElementById('az-a-input');
    if (inp) {
      inp.value = '[websearch] ' + (inp.value || '');
      inp.focus();
    }
  }

  // ── Messaging ─────────────────────────────────────────────────────────────
  function sendMessage() {
    var inp  = document.getElementById('az-a-input');
    var text = (inp.value || '').trim();
    if (!text) return;
    inp.value = '';

    // Set anchor on first message
    if (!state.anchor) {
      state.anchor = {
        label : text.length > 60 ? text.slice(0, 60) + '…' : text,
        url   : window.location.href,
      };
    } else {
      state.hops++;
    }

    appendMessage('user', text);
    saveState();

    // Check rabbit-hole
    if (state.hops === CFG.maxHops) {
      appendMessage('assistant',
        '⚓ <strong>Anchor check:</strong> You\'re ' + state.hops + ' hops deep from your starting question ' +
        '("<em>' + escHtml(state.anchor.label) + '</em>"). Still on track? ' +
        'Use the ⚓ button to view your trail or return. I\'ll keep going — just flagging.',
        'nudge'
      );
    }

    // Detect websearch request
    var isWebSearch = text.startsWith('[websearch]');
    var query = isWebSearch ? text.replace('[websearch]', '').trim() : text;

    query = query; // used below
    callAPI(query, isWebSearch);
  }

  async function callAPI(query, isWebSearch) {
    var sendBtn = document.getElementById('az-a-send');
    if (sendBtn) sendBtn.disabled = true;
    appendTypingIndicator();

    try {
      // Build messages for context
      var history = state.messages.slice(-8).map(function(m) {
        return { role: m.role === 'user' ? 'user' : 'assistant', content: stripHtml(m.text) };
      });

      var payload = {
        query      : query,
        websearch  : isWebSearch,
        page_ctx   : state.pageCtx,
        history    : history,
        system     : CFG.systemPrompt,
      };

      var endpoints = Array.isArray(global.AZ_API_ENDPOINTS) && global.AZ_API_ENDPOINTS.length
        ? global.AZ_API_ENDPOINTS
        : CFG.apiEndpoints;
      var resp = null;
      for (var i = 0; i < endpoints.length; i++) {
        try {
          resp = await fetch(endpoints[i], {
            method  : 'POST',
            headers : { 'Content-Type': 'application/json' },
            body    : JSON.stringify(payload),
            signal  : AbortSignal.timeout(25000),
          });
          if (resp.ok) break;
        } catch (err) {}
      }

      removeTypingIndicator();

      if (resp && resp.ok) {
        var data = await resp.json();
        var answer = data.answer || data.response || data.text || '(no response)';
        var sources = data.sources || [];
        appendMessage('assistant', formatAnswer(answer, sources, isWebSearch));
      } else {
        // Fallback: HF direct inference
        await callHFFallback(query, isWebSearch);
      }
    } catch(e) {
      removeTypingIndicator();
      await callHFFallback(query, isWebSearch);
    }

    if (sendBtn) sendBtn.disabled = false;
    saveState();
  }

  async function callHFFallback(query, isWebSearch) {
    // Minimal HF Inference API call (no RAG — note this clearly)
    var token = CFG.hfToken || (global.AZ_HF_TOKEN) || '';
    if (!token) {
      appendMessage('assistant',
        '⚠️ <strong>Backend offline</strong> — the RAG API is not reachable and no HF token is configured. ' +
        'To enable live responses, deploy the assistant backend from ' +
        '<a href="https://github.com/wuzbak/Unitary-Manifold-" target="_blank">the repository</a> ' +
        'or set <code>window.AZ_HF_TOKEN</code>.<br><br>' +
        '<em>Your question is noted. Explore the ' +
        '<a href="https://axiomzerospc.org/portal/knowledge/">Knowledge Portal</a> ' +
        'for pillar documentation while offline.</em>',
        'error'
      );
      return;
    }

    try {
      var prompt = CFG.systemPrompt + '\n\nUser: ' + query + '\n\nAssistant:';
      var hfResp = await fetch(CFG.hfEndpoint, {
        method  : 'POST',
        headers : {
          'Authorization' : 'Bearer ' + token,
          'Content-Type'  : 'application/json',
        },
        body    : JSON.stringify({ inputs: prompt, parameters: { max_new_tokens: 512, temperature: 0.3 } }),
        signal  : AbortSignal.timeout(30000),
      });
      if (hfResp.ok) {
        var hfData = await hfResp.json();
        var text = Array.isArray(hfData) ? hfData[0].generated_text : hfData.generated_text || '';
        // Strip the prompt prefix
        var answer = text.replace(prompt, '').trim();
        appendMessage('assistant',
          '<span class="az-a-tag">HF direct · no RAG</span> ' + escHtml(answer)
        );
      } else {
        throw new Error('HF ' + hfResp.status);
      }
    } catch(e) {
      appendMessage('assistant',
        '⚠️ Both the RAG backend and HF fallback are unreachable. ' +
        'Check your connection or visit the <a href="https://axiomzerospc.org/portal/knowledge/">Knowledge Portal</a> to browse pillars directly.',
        'error'
      );
    }
  }

  function formatAnswer(answer, sources, isWebSearch) {
    var html = escHtml(answer).replace(/\n/g, '<br>');
    // Highlight pillar references
    html = html.replace(/Pillar\s+(\d+)/gi, '<a class="az-a-pillar" href="https://axiomzerospc.org/portal/knowledge/?p=$1" target="_blank">Pillar $1</a>');
    // Highlight gate labels
    html = html.replace(/\b(HARDGATE|ADJACENT_TRACK|OPEN_GAP|ARCHITECTURE_LIMIT|NLO_INSUFFICIENT)\b/g,
      '<span class="az-a-gate az-a-gate-$1">$1</span>');
    if (isWebSearch && sources.length > 0) {
      html += '<div class="az-a-sources"><strong>External literature:</strong><ul>' +
        sources.map(function(s) {
          return '<li><a href="' + escAttr(s.url) + '" target="_blank" rel="noopener">' + escHtml(s.title) + '</a></li>';
        }).join('') + '</ul><em>External sources may not align with UM predictions — treat as alignment data, not ground truth.</em></div>';
    } else if (sources.length > 0) {
      html += '<div class="az-a-sources"><strong>Sources:</strong> ' +
        sources.map(function(s) { return escHtml(s.label || s.title || s); }).join(' · ') + '</div>';
    }
    return html;
  }

  // ── Message rendering ─────────────────────────────────────────────────────
  function appendMessage(role, html, cls) {
    state.messages.push({ role: role, text: html, cls: cls });
    if (state.open) renderLastMessage();
    else if (role === 'assistant') showBadge();
  }

  function renderMessages() {
    var el = document.getElementById('az-a-messages');
    if (!el) return;
    el.innerHTML = '';
    state.messages.forEach(function(m) { renderMsg(el, m); });
    el.scrollTop = el.scrollHeight;
  }

  function renderLastMessage() {
    var el = document.getElementById('az-a-messages');
    if (!el) return;
    renderMsg(el, state.messages[state.messages.length - 1]);
    el.scrollTop = el.scrollHeight;
  }

  function renderMsg(container, m) {
    var div = document.createElement('div');
    div.className = 'az-a-msg az-a-msg-' + m.role + (m.cls ? ' az-a-msg-' + m.cls : '');
    div.innerHTML = m.text;
    container.appendChild(div);
  }

  function appendTypingIndicator() {
    var el = document.getElementById('az-a-messages');
    if (!el) return;
    var div = document.createElement('div');
    div.id = 'az-a-typing';
    div.className = 'az-a-msg az-a-msg-assistant az-a-typing';
    div.innerHTML = '<span></span><span></span><span></span>';
    el.appendChild(div);
    el.scrollTop = el.scrollHeight;
  }

  function removeTypingIndicator() {
    var el = document.getElementById('az-a-typing');
    if (el) el.remove();
  }

  // ── Utilities ─────────────────────────────────────────────────────────────
  function escHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function escAttr(s) { return escHtml(s); }

  function stripHtml(s) {
    // Remove all HTML-special characters to produce safe plain text for API history
    return String(s).replace(/[<>"'&]/g, ' ').replace(/\s+/g, ' ').trim();
  }

  // ── Page context injection API ────────────────────────────────────────────
  /**
   * Call from each page to tell the assistant what tool/pillar the user is viewing.
   * e.g. AZAssistant.setPageContext('Oracle — Product 16 Grand Synthesis Engine')
   */
  function setPageContext(ctx) {
    state.pageCtx = ctx;
  }

  // ── Epistemic nudge for inline pillar badges ──────────────────────────────
  /**
   * Call once per page to auto-badge elements with data-pillar and data-gate attrs.
   * e.g. <span data-pillar="4" data-gate="HARDGATE">holographic entropy</span>
   */
  function nudgeInlineGates() {
    document.querySelectorAll('[data-gate]').forEach(function(el) {
      if (el.querySelector('.az-gate-badge')) return; // already done
      var gate  = el.getAttribute('data-gate');
      var pillar = el.getAttribute('data-pillar');
      var badge = document.createElement('span');
      badge.className = 'az-gate-badge az-gate-' + gate;
      badge.title = gateDescription(gate) + (pillar ? ' (Pillar ' + pillar + ')' : '');
      badge.textContent = gate === 'HARDGATE' ? '✓' : gate === 'ADJACENT_TRACK' ? '◈' : '○';
      el.appendChild(badge);
    });
  }

  function gateDescription(gate) {
    var map = {
      'HARDGATE'         : 'Formally closed pillar — highest epistemic confidence',
      'ADJACENT_TRACK'   : 'Adjacent research track — not a hardgate physics claim',
      'OPEN_GAP'         : 'Documented open problem — actively being worked',
      'ARCHITECTURE_LIMIT': 'Framework architecture limit — acknowledged boundary',
    };
    return map[gate] || gate;
  }

  // ── Init ──────────────────────────────────────────────────────────────────
  function init() {
    loadState();
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function() { buildWidget(); nudgeInlineGates(); });
    } else {
      buildWidget();
      nudgeInlineGates();
    }
  }

  init();

  // Public API
  global.AZAssistant = {
    open            : openDrawer,
    close           : closeDrawer,
    setPageContext  : setPageContext,
    nudgeInlineGates: nudgeInlineGates,
    returnToAnchor  : returnToAnchor,
    send            : function(msg) {
      var inp = document.getElementById('az-a-input');
      if (inp) { inp.value = msg; sendMessage(); }
    },
  };

})(window);
