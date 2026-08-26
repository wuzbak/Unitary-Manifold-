/**
 * 18-interrogator.js — Axiom Zero Interrogator Engine
 * Pillar 791 / v23.1 — The Living Theory
 *
 * Three modes:
 *  1. Challenge Mode — search claims, see epistemic status + falsification
 *  2. Experiment Mode — pick experiment, see all pillars it tests
 *  3. Tension Map — visual canvas of σ tensions vs. confidence
 *
 * Zero dependencies. Zero server. Zero API keys.
 */

'use strict';

// ============================================================
// Constants
// ============================================================
const KB_URL = './interrogator-kb.json';

// Confidence scores by gate (for Y-axis in Tension Map)
const GATE_CONFIDENCE = {
  'DERIVED': 0.9,
  'FITTED': 0.65,
  'ARCHITECTURE_LIMIT': 0.35,
  'ADJACENT_TRACK': 0.15,
};

// Status → colour
const STATUS_COLOR = {
  'PASS': '#22c55e',
  'TENSION': '#f59e0b',
  'FALSIFIED': '#ef4444',
  'AWAITING': '#94a3b8',
  'ARCHITECTURE_LIMIT': '#8b5cf6',
  'ADJACENT_TRACK': '#3b82f6',
};

// ============================================================
// State
// ============================================================
let KB = null;
let activePanel = 'challenge';
let selectedExp = null;

// ============================================================
// Load KB and bootstrap
// ============================================================
async function loadKB() {
  try {
    const resp = await fetch(KB_URL);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    KB = await resp.json();
  } catch (e) {
    // Fallback: empty KB with error message
    KB = { entries: [], experiments: [], meta: { gates: [], gate_descriptions: {}, status_colors: {} } };
    document.getElementById('claims-list').innerHTML =
      '<div class="no-results">⚠ Could not load knowledge base. Run: <code>python3 TOOLS/build_interrogator_kb.py</code></div>';
  }
  bootstrap();
}

// ============================================================
// Bootstrap UI
// ============================================================
function bootstrap() {
  setupTabs();
  renderSummaryBar();
  renderClaimsList(KB.entries);
  setupSearch();
  renderExpGrid();
  renderTensionMap();
}

// ============================================================
// Tab routing
// ============================================================
function setupTabs() {
  document.querySelectorAll('.iq-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      const panel = btn.dataset.panel;
      document.querySelectorAll('.iq-tab').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.iq-panel').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById('panel-' + panel).classList.add('active');
      activePanel = panel;
      if (panel === 'tension') renderTensionMap();
    });
  });
}

// ============================================================
// Summary bar
// ============================================================
function renderSummaryBar() {
  const bar = document.getElementById('summary-bar');
  const counts = { PASS: 0, TENSION: 0, AWAITING: 0, ARCHITECTURE_LIMIT: 0 };
  KB.entries.forEach(e => {
    const s = normalizeStatus(e.status);
    if (s === 'PASS') counts.PASS++;
    else if (s === 'TENSION') counts.TENSION++;
    else if (s === 'AWAITING') counts.AWAITING++;
    else if (s === 'ARCHITECTURE_LIMIT' || e.gate === 'ARCHITECTURE_LIMIT') counts.ARCHITECTURE_LIMIT++;
  });

  bar.innerHTML = `
    <div class="summary-chip chip-pass">✅ ${counts.PASS} PASS</div>
    <div class="summary-chip chip-tension">⚠ ${counts.TENSION} TENSION</div>
    <div class="summary-chip chip-awaiting">⏳ ${counts.AWAITING} AWAITING</div>
    <div class="summary-chip chip-arch">🔒 ${counts.ARCHITECTURE_LIMIT} ARCH LIMIT</div>
  `;
}

function normalizeStatus(s) {
  if (!s) return 'AWAITING';
  s = s.toUpperCase();
  if (s === 'PASS' || s.includes('PASS') || s.includes('DERIVED') || s.includes('PROVED')) return 'PASS';
  if (s.includes('TENSION') || s.includes('SIGMA')) return 'TENSION';
  if (s.includes('FALSIFIED')) return 'FALSIFIED';
  if (s.includes('AWAITING') || s.includes('PENDING')) return 'AWAITING';
  if (s.includes('ARCHITECTURE_LIMIT') || s.includes('ARCHITECTURE')) return 'ARCHITECTURE_LIMIT';
  if (s.includes('ADJACENT') || s.includes('SPECULATIVE')) return 'ADJACENT_TRACK';
  return 'AWAITING';
}

// ============================================================
// Challenge Mode: claims list
// ============================================================
function renderClaimsList(entries) {
  const container = document.getElementById('claims-list');
  if (!entries.length) {
    container.innerHTML = '<div class="no-results">No matching claims found.</div>';
    return;
  }
  container.innerHTML = entries.map(entry => buildClaimCard(entry)).join('');

  // Expand/collapse
  container.querySelectorAll('.claim-card').forEach(card => {
    card.addEventListener('click', () => {
      const wasExpanded = card.classList.contains('expanded');
      container.querySelectorAll('.claim-card').forEach(c => c.classList.remove('expanded'));
      if (!wasExpanded) card.classList.add('expanded');
    });
  });
}

function buildClaimCard(entry) {
  const status = normalizeStatus(entry.status);
  const statusLabel = entry.status || status;
  const tensionStr = entry.tension_sigma != null
    ? `<span class="tension-val">${entry.tension_sigma.toFixed(2)}σ</span>`
    : '<span style="color:#475569">N/A</span>';
  const pillarsStr = (Array.isArray(entry.pillar) ? entry.pillar : [entry.pillar])
    .map(p => `P${p}`).join(', ');

  const exps = (entry.experiments || []).map(e =>
    `<span class="exp-chip">${e}</span>`
  ).join('');

  const shortStatus = abbreviateStatus(statusLabel);

  return `
    <div class="claim-card" data-id="${entry.id}">
      <div class="claim-header">
        <span class="gate-badge gate-${entry.gate || 'DERIVED'}">${entry.gate || 'DERIVED'}</span>
        <span class="claim-text">
          ${entry.claim}
          <span class="status-pill status-${status}">${shortStatus}</span>
        </span>
      </div>
      <div class="pillar-ref">${pillarsStr}</div>
      <div class="claim-detail">
        <div class="detail-grid">
          <div class="detail-block">
            <label>Prediction</label>
            <span>${entry.prediction || '—'}</span>
          </div>
          <div class="detail-block">
            <label>Uncertainty</label>
            <span>${entry.uncertainty || '—'}</span>
          </div>
          <div class="detail-block">
            <label>Current measurement</label>
            <span>${entry.measurement || '—'}</span>
          </div>
          <div class="detail-block">
            <label>Current tension</label>
            <span>${tensionStr}</span>
          </div>
          <div class="detail-block">
            <label>Timeline</label>
            <span>${entry.timeline || '—'}</span>
          </div>
          <div class="detail-block">
            <label>Tests by</label>
            <div class="experiments-list">${exps}</div>
          </div>
        </div>
        <div class="falsification-box">
          <label>☠ Falsification condition</label>
          <span>${entry.falsification || 'No explicit falsification condition stated.'}</span>
        </div>
      </div>
    </div>
  `;
}

function abbreviateStatus(s) {
  if (!s) return '?';
  s = s.toUpperCase();
  if (s === 'PASS') return 'PASS';
  if (s.includes('TENSION')) return 'TENSION';
  if (s.includes('FALSIFIED')) return 'FALSIFIED';
  if (s.includes('AWAITING')) return 'AWAITING';
  if (s.includes('ARCHITECTURE')) return 'ARCH LIMIT';
  if (s.includes('ADJACENT') || s.includes('SPECULATIVE')) return 'ADJ TRACK';
  if (s.includes('DERIVED') || s.includes('PROVED')) return 'DERIVED';
  if (s.includes('STABILITY')) return 'BASIN';
  if (s.includes('CANDIDATE')) return 'CANDIDATE';
  return s.slice(0, 12);
}

// ============================================================
// Challenge search
// ============================================================
function setupSearch() {
  const input = document.getElementById('challenge-search');
  input.addEventListener('input', () => {
    const q = input.value.trim().toLowerCase();
    if (!q) {
      renderClaimsList(KB.entries);
      return;
    }
    const filtered = KB.entries.filter(e => {
      const haystack = [
        e.claim, e.id, e.status, e.gate,
        e.prediction, e.falsification, e.timeline,
        ...(e.tags || []),
      ].filter(Boolean).join(' ').toLowerCase();
      return haystack.includes(q);
    });
    renderClaimsList(filtered);
  });
}

// ============================================================
// Experiment Mode
// ============================================================
function renderExpGrid() {
  const grid = document.getElementById('exp-grid');
  grid.innerHTML = KB.experiments.map(exp => `
    <div class="exp-card" data-expid="${exp.id}">
      <div class="exp-name">${exp.name}</div>
      <div class="exp-timeline">📅 ${exp.timeline}</div>
      <div class="exp-desc">${exp.description}</div>
    </div>
  `).join('');

  grid.querySelectorAll('.exp-card').forEach(card => {
    card.addEventListener('click', () => {
      grid.querySelectorAll('.exp-card').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
      const exp = KB.experiments.find(e => e.id === card.dataset.expid);
      showExpDetail(exp);
    });
  });
}

function showExpDetail(exp) {
  const panel = document.getElementById('exp-detail-panel');
  const relatedClaims = KB.entries.filter(e => {
    const pillars = Array.isArray(e.pillar) ? e.pillar : [e.pillar];
    return exp.tests_pillars.some(p => pillars.includes(p));
  });

  const claimsHtml = relatedClaims.map(e => {
    const status = normalizeStatus(e.status);
    const tensionStr = e.tension_sigma != null
      ? `${e.tension_sigma.toFixed(2)}σ` : 'N/A';
    return `
      <tr>
        <td style="color:#e2e8f0;padding:0.5rem 0.7rem">${e.claim.slice(0, 70)}${e.claim.length > 70 ? '…' : ''}</td>
        <td><span class="gate-badge gate-${e.gate}">${e.gate}</span></td>
        <td style="padding:0.5rem;color:${STATUS_COLOR[status] || '#94a3b8'}">${status}</td>
        <td style="padding:0.5rem;font-family:monospace;font-size:0.8rem">${tensionStr}</td>
      </tr>
    `;
  }).join('');

  panel.innerHTML = `
    <h3 style="color:#f1f5f9;margin:0 0 0.5rem">${exp.name}</h3>
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#38bdf8;margin-bottom:0.7rem">
      📅 ${exp.timeline} &nbsp;|&nbsp; Observable: ${exp.observable}
    </div>
    <div style="color:#94a3b8;font-size:0.85rem;margin-bottom:1rem">${exp.description}</div>
    <div style="background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.15);border-radius:6px;padding:0.7rem 1rem;margin-bottom:1rem">
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#ef4444;text-transform:uppercase">Verdict threshold</span><br>
      <span style="font-size:0.85rem;color:#fca5a5">${exp.verdict_threshold}</span>
    </div>
    <h4 style="color:#94a3b8;font-size:0.85rem;margin-bottom:0.5rem">Claims tested by ${exp.name}</h4>
    ${relatedClaims.length ? `
    <table style="width:100%;border-collapse:collapse;font-size:0.83rem">
      <thead>
        <tr style="border-bottom:1px solid #1a2232">
          <th style="text-align:left;padding:0.4rem 0.7rem;color:#64748b;font-weight:500">Claim</th>
          <th style="text-align:left;padding:0.4rem;color:#64748b;font-weight:500">Gate</th>
          <th style="text-align:left;padding:0.4rem;color:#64748b;font-weight:500">Status</th>
          <th style="text-align:left;padding:0.4rem;color:#64748b;font-weight:500">Tension</th>
        </tr>
      </thead>
      <tbody>${claimsHtml}</tbody>
    </table>` : '<div style="color:#4a5568">No claims directly mapped to this experiment.</div>'}
  `;
  panel.classList.add('visible');
}

// ============================================================
// Tension Map (Canvas)
// ============================================================
function renderTensionMap() {
  const wrap = document.getElementById('tension-canvas-wrap');
  const canvas = document.getElementById('tension-canvas');
  const tooltip = document.getElementById('tension-tooltip');
  if (!KB || !KB.entries.length) return;

  const W = wrap.clientWidth;
  const H = wrap.clientHeight;
  canvas.width = W;
  canvas.height = H;

  const ctx = canvas.getContext('2d');
  const PAD = { top: 30, right: 30, bottom: 50, left: 60 };
  const plotW = W - PAD.left - PAD.right;
  const plotH = H - PAD.top - PAD.bottom;

  ctx.clearRect(0, 0, W, H);

  // Background grid
  ctx.strokeStyle = '#1a2232';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 5; i++) {
    const y = PAD.top + (plotH * i / 5);
    ctx.beginPath(); ctx.moveTo(PAD.left, y); ctx.lineTo(W - PAD.right, y); ctx.stroke();
  }
  for (let i = 0; i <= 5; i++) {
    const x = PAD.left + (plotW * i / 5);
    ctx.beginPath(); ctx.moveTo(x, PAD.top); ctx.lineTo(x, H - PAD.bottom); ctx.stroke();
  }

  // Axis labels
  ctx.fillStyle = '#4a5568';
  ctx.font = '11px JetBrains Mono, monospace';
  ctx.textAlign = 'center';
  ctx.fillText('← safer', PAD.left + plotW * 0.05, H - 12);
  ctx.fillText('σ tension →', PAD.left + plotW * 0.8, H - 12);
  ctx.fillText('0', PAD.left, H - PAD.bottom + 14);
  ctx.fillText('3σ', PAD.left + plotW * 0.75, H - PAD.bottom + 14);

  ctx.save();
  ctx.translate(18, H / 2);
  ctx.rotate(-Math.PI / 2);
  ctx.textAlign = 'center';
  ctx.fillText('theoretical confidence ↑', 0, 0);
  ctx.restore();

  // Danger zone (sigma > 3)
  const dangerX = PAD.left + (3 / 4) * plotW;
  ctx.fillStyle = 'rgba(239,68,68,0.04)';
  ctx.fillRect(dangerX, PAD.top, W - PAD.right - dangerX, plotH);
  ctx.strokeStyle = 'rgba(239,68,68,0.15)';
  ctx.setLineDash([4, 4]);
  ctx.beginPath(); ctx.moveTo(dangerX, PAD.top); ctx.lineTo(dangerX, H - PAD.bottom); ctx.stroke();
  ctx.setLineDash([]);

  // Plot nodes
  const maxSigma = 4;
  const nodes = [];

  KB.entries.forEach((entry, i) => {
    const sigma = entry.tension_sigma != null ? Math.min(entry.tension_sigma, maxSigma) : 0;
    const conf = GATE_CONFIDENCE[entry.gate] || 0.5;
    const status = normalizeStatus(entry.status);

    // Add small jitter to avoid overlap
    const jitterX = (Math.sin(i * 137.5) * 0.015) * plotW;
    const jitterY = (Math.cos(i * 97.3) * 0.015) * plotH;

    const cx = PAD.left + (sigma / maxSigma) * plotW * 0.95 + jitterX;
    const cy = PAD.top + plotH - (conf * plotH * 0.9) + jitterY;

    const color = STATUS_COLOR[status] || '#94a3b8';
    const r = 8 + (entry.tension_sigma != null && entry.tension_sigma > 1 ? 3 : 0);

    // Draw node
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fillStyle = color + '28';
    ctx.fill();
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.stroke();

    // Label (short)
    const label = entry.id.replace(/_/g, ' ').slice(0, 12);
    ctx.fillStyle = '#94a3b8';
    ctx.font = '9px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(label, cx, cy + r + 11);

    nodes.push({ cx, cy, r: r + 4, entry, color });
  });

  // Hover/click interaction
  canvas.onmousemove = (e) => {
    const rect = canvas.getBoundingClientRect();
    const mx = (e.clientX - rect.left) * (W / rect.width);
    const my = (e.clientY - rect.top) * (H / rect.height);
    const hit = nodes.find(n => Math.hypot(mx - n.cx, my - n.cy) < n.r + 6);
    if (hit) {
      const entry = hit.entry;
      const tensionStr = entry.tension_sigma != null ? `${entry.tension_sigma.toFixed(2)}σ` : 'N/A';
      tooltip.style.display = 'block';
      tooltip.style.left = Math.min(e.offsetX + 14, W - 280) + 'px';
      tooltip.style.top = Math.min(e.offsetY + 14, H - 120) + 'px';
      tooltip.innerHTML = `
        <strong style="color:${hit.color}">${entry.id.replace(/_/g, ' ')}</strong><br>
        <span style="color:#64748b;font-size:0.75rem">Gate: ${entry.gate}</span><br>
        <span style="font-size:0.8rem">${entry.claim.slice(0, 80)}…</span><br>
        <span style="font-size:0.75rem;color:#94a3b8">Tension: ${tensionStr}</span>
      `;
      canvas.style.cursor = 'pointer';
    } else {
      tooltip.style.display = 'none';
      canvas.style.cursor = 'default';
    }
  };

  canvas.onclick = (e) => {
    const rect = canvas.getBoundingClientRect();
    const mx = (e.clientX - rect.left) * (W / rect.width);
    const my = (e.clientY - rect.top) * (H / rect.height);
    const hit = nodes.find(n => Math.hypot(mx - n.cx, my - n.cy) < n.r + 6);
    if (hit) {
      // Switch to challenge mode and open this card
      document.querySelector('[data-panel="challenge"]').click();
      const card = document.querySelector(`[data-id="${hit.entry.id}"]`);
      if (card) {
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
        setTimeout(() => card.classList.add('expanded'), 400);
      }
    }
  };
}

// Re-render tension map on resize
window.addEventListener('resize', () => {
  if (activePanel === 'tension') renderTensionMap();
});

// ============================================================
// Init
// ============================================================
loadKB();
