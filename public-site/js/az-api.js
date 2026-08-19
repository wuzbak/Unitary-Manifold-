/**
 * az-api.js — AxiomZero API Helper
 * Centralises base URLs, fetch patterns, loading states, and offline fallbacks
 * for all AZ-IP product pages.
 *
 * AxiomZero Technologies & Consulting, SPC — UBI 606 239 876
 */

(function(global) {
  'use strict';

  // ── Default endpoint registry (override per-page if self-hosting) ─────────
  const ENDPOINTS = {
    'lodge'       : 'https://lodge.axiomzero.io',
    '01-axiom-os' : 'https://axiom-os.axiomzerospc.org',
    '03-eige'     : 'https://eige.axiomzerospc.org',
    '04-um-sos'   : 'https://um-sos.axiomzerospc.org',
    '05-uos-kernel': 'https://uos.axiomzerospc.org',
    '08-axiom-journalist': 'https://journalist.axiomzerospc.org',
    '09-omegaholon': 'https://omegaholon.axiomzerospc.org',
    '10-filmers-companion': 'https://filmers.axiomzerospc.org',
    '11-terra-os' : 'https://terra.axiomzerospc.org',
    '12-lithos-os': 'https://lithos.axiomzerospc.org',
    '13-delphi'   : 'https://delphi.axiomzerospc.org',
    '16-oracle'   : 'https://oracle.axiomzerospc.org',
  };

  // ── Core fetch wrapper ────────────────────────────────────────────────────
  /**
   * call(appId, path, options)
   * Returns Promise<{ok, data, error, offline}>
   *
   * options = {
   *   method   : 'GET' | 'POST',
   *   body     : object (auto-JSON-serialised),
   *   baseUrl  : override endpoint (optional),
   *   timeout  : ms (default 12000)
   * }
   */
  async function call(appId, path, options) {
    options = options || {};
    const base    = options.baseUrl || ENDPOINTS[appId] || '';
    const timeout = options.timeout || 12000;
    const url     = base + path;

    const ctrl = new AbortController();
    const timer = setTimeout(function() { ctrl.abort(); }, timeout);

    const fetchOpts = {
      method : options.method || 'GET',
      signal : ctrl.signal,
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    };
    if (options.body) fetchOpts.body = JSON.stringify(options.body);

    try {
      const resp = await fetch(url, fetchOpts);
      clearTimeout(timer);
      if (!resp.ok) {
        return { ok: false, offline: false, error: 'HTTP ' + resp.status + ' ' + resp.statusText };
      }
      const data = await resp.json();
      return { ok: true, offline: false, data };
    } catch(e) {
      clearTimeout(timer);
      const isOffline = (e.name === 'AbortError' || e.name === 'TypeError');
      return { ok: false, offline: isOffline, error: e.message };
    }
  }

  // ── UI state helpers ──────────────────────────────────────────────────────

  /** Show loading spinner inside an element */
  function setLoading(el, active) {
    if (!el) return;
    if (active) {
      el.innerHTML = '<div class="az-loading"><span class="az-spinner"></span> Computing…</div>';
    }
  }

  /** Render an offline notice inside an element */
  function showOfflineNotice(el, appName) {
    if (!el) return;
    appName = appName || 'this app';
    el.innerHTML =
      '<div class="az-offline-notice">' +
        '<div class="az-offline-icon">📡</div>' +
        '<strong>Live API offline</strong>' +
        '<p>' + appName + ' backend is not reachable. ' +
        'Showing representative sample output below. ' +
        'To run live: deploy the backend from ' +
        '<a href="https://github.com/wuzbak/Unitary-Manifold-" target="_blank">the repository</a> ' +
        'and enter your endpoint URL above.</p>' +
      '</div>';
  }

  /** Render an error notice */
  function showError(el, message) {
    if (!el) return;
    el.innerHTML = '<div class="az-error-notice">⚠️ ' + (message || 'Unknown error') + '</div>';
  }

  /** Render a success result card */
  function showResult(el, html) {
    if (!el) return;
    el.innerHTML = html;
  }

  // ── Custom endpoint binding ───────────────────────────────────────────────
  /**
   * bindCustomEndpoint(inputId, appId)
   * Reads a text input and overrides the app's endpoint at runtime.
   */
  function bindCustomEndpoint(inputId, appId) {
    var inp = document.getElementById(inputId);
    if (!inp) return;
    var saved = localStorage.getItem('az-endpoint-' + appId);
    if (saved) { inp.value = saved; ENDPOINTS[appId] = saved; }
    inp.addEventListener('change', function() {
      var val = inp.value.trim().replace(/\/$/, '');
      if (val) {
        ENDPOINTS[appId] = val;
        localStorage.setItem('az-endpoint-' + appId, val);
      }
    });
  }

  // ── Exports ───────────────────────────────────────────────────────────────
  global.AZAPI = {
    call               : call,
    setLoading         : setLoading,
    showOfflineNotice  : showOfflineNotice,
    showError          : showError,
    showResult         : showResult,
    bindCustomEndpoint : bindCustomEndpoint,
    endpoints          : ENDPOINTS,
  };

})(window);
