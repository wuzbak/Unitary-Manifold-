// Copyright (C) 2026  ThomasCory Walker-Pearson
// SPDX-License-Identifier: LicenseRef-DPC-1.0
// Axiom Zero Interrogator — JS Engine
// public-site/js/18-interrogator.js
// Theory: ThomasCory Walker-Pearson (2026)
// Code: GitHub Copilot (AI)

"use strict";

// ── Export constants (for test suite) ─────────────────────────────────────
export const INTERROGATOR_VERSION = "v23.0";
export const KB_PATH = "../data/interrogator-kb.json";

// Gate → display colour mapping
export const GATE_COLORS = {
  DERIVED:                          "#30d158",
  EMPIRICALLY_SELECTED:             "#3b8bff",
  FITTED:                           "#f0c040",
  ARCHITECTURE_LIMIT:               "#ff9f0a",
  ADJACENT_TRACK:                   "#7c4dff",
  OPEN_TENSION:                     "#ff453a",
  CLOSED:                           "#30d158",
  FALSIFIABLE_PREDICTION:           "#3b8bff",
  PROVED_CONDITIONAL:               "#3b8bff",
  ONE_LOOP_CONSISTENT:              "#30d158",
  LEPTON_JARLSKOG_LATTICE_DERIVED:  "#30d158",
  DM21_NLO_PARTIAL_CLOSURE:         "#f0c040",
  TYPE_AB_CLASSIFICATION_COMPLETE:  "#30d158",
  WINDING_BASIN_CLOSED:             "#30d158",
  FALSIFICATION_MAP_REGISTERED:     "#3b8bff",
  TENSION_MONITORED:                "#ff9f0a",
};

// Human-readable gate labels
export const GATE_LABELS = {
  DERIVED:                          "Geometrically Derived",
  EMPIRICALLY_SELECTED:             "Empirically Selected",
  FITTED:                           "Fitted Parameter",
  ARCHITECTURE_LIMIT:               "Architecture Limit",
  ADJACENT_TRACK:                   "Adjacent Track (non-hardgate)",
  OPEN_TENSION:                     "Open Tension",
  CLOSED:                           "Formally Closed",
  FALSIFIABLE_PREDICTION:           "Falsifiable Prediction",
  PROVED_CONDITIONAL:               "Proved Conditional",
  ONE_LOOP_CONSISTENT:              "One-Loop Consistent",
  LEPTON_JARLSKOG_LATTICE_DERIVED:  "Lattice Derived",
  DM21_NLO_PARTIAL_CLOSURE:        "NLO Partial Closure",
  TYPE_AB_CLASSIFICATION_COMPLETE:  "Classification Complete",
  WINDING_BASIN_CLOSED:             "Stability Basin Closed",
  FALSIFICATION_MAP_REGISTERED:     "Falsification Registered",
  TENSION_MONITORED:                "Tension Monitored",
};

// ── Epistemic gate ranking for colouring (0=worst, 3=best) ────────────────
export function gateRank(gate) {
  const ranks = {
    OPEN_TENSION: 0, ARCHITECTURE_LIMIT: 0,
    FITTED: 1, ADJACENT_TRACK: 1, TENSION_MONITORED: 1,
    DM21_NLO_PARTIAL_CLOSURE: 1, FALSIFIABLE_PREDICTION: 2,
    EMPIRICALLY_SELECTED: 2, PROVED_CONDITIONAL: 2,
    ONE_LOOP_CONSISTENT: 2, LEPTON_JARLSKOG_LATTICE_DERIVED: 2,
    TYPE_AB_CLASSIFICATION_COMPLETE: 2, WINDING_BASIN_CLOSED: 3,
    FALSIFICATION_MAP_REGISTERED: 3, DERIVED: 3, CLOSED: 3,
  };
  return ranks[gate] ?? 1;
}

// ── Search / fuzzy matching ────────────────────────────────────────────────

/**
 * Score a claim against a query string.
 * Returns a score 0–100; higher = better match.
 */
export function scoreMatch(claim, query) {
  if (!query || query.length < 2) return 0;
  const q = query.toLowerCase();
  const words = q.split(/\s+/).filter(w => w.length > 1);
  let score = 0;

  const searchableText = [
    claim.claim,
    claim.gate,
    claim.predicted_value ?? "",
    claim.observed_value ?? "",
    claim.falsification ?? "",
    claim.admission ?? "",
    ...(claim.tags ?? []),
    String(claim.pillar ?? ""),
  ].join(" ").toLowerCase();

  // Full query in claim text
  if (searchableText.includes(q)) score += 40;

  // Individual word matches
  for (const word of words) {
    if (searchableText.includes(word)) score += 10;
  }

  // Tag exact match bonus
  if (claim.tags && claim.tags.some(t => t.toLowerCase().includes(q))) score += 20;

  // Pillar number match
  if (claim.pillar && String(claim.pillar).includes(q)) score += 30;

  // Claim text starts with query
  if (claim.claim.toLowerCase().startsWith(q)) score += 15;

  return Math.min(score, 100);
}

/**
 * Search KB claims by query string. Returns sorted matches with scores.
 */
export function searchClaims(kb, query) {
  if (!kb || !query || query.trim().length < 2) return [];
  const results = kb.claims
    .map(claim => ({ claim, score: scoreMatch(claim, query.trim()) }))
    .filter(r => r.score > 0)
    .sort((a, b) => b.score - a.score);
  return results;
}

/**
 * Find all claims tested by a given experiment id.
 */
export function claimsForExperiment(kb, experimentId) {
  const expEntry = kb.experiments.find(e => e.id === experimentId);
  if (!expEntry) return [];
  const ids = new Set(expEntry.tests_pillars);
  return kb.claims.filter(c => ids.has(c.id));
}

/**
 * Return all tensions sorted by severity (sigma desc, then confidence desc).
 */
export function sortedTensions(kb) {
  return [...(kb.tensions ?? [])].sort((a, b) => {
    const sa = a.sigma ?? 0;
    const sb = b.sigma ?? 0;
    if (sb !== sa) return sb - sa;
    return (b.confidence ?? 0) - (a.confidence ?? 0);
  });
}

// ── Tension Map canvas renderer ────────────────────────────────────────────

/**
 * Draw the tension constellation on a canvas element.
 * x-axis: current tension (σ), y-axis: theoretical confidence (0–1).
 * Returns array of hit-test regions {tension, x, y, r}.
 */
export function drawTensionMap(canvas, tensions, selectedId) {
  const ctx = canvas.getContext("2d");
  const W = canvas.width;
  const H = canvas.height;
  const PAD = 56;
  const plotW = W - PAD * 2;
  const plotH = H - PAD * 2;

  ctx.clearRect(0, 0, W, H);

  // Background
  ctx.fillStyle = "#050a1a";
  ctx.fillRect(0, 0, W, H);

  // Grid lines
  ctx.strokeStyle = "#1a2a4a";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const x = PAD + (i / 4) * plotW;
    ctx.beginPath(); ctx.moveTo(x, PAD); ctx.lineTo(x, PAD + plotH); ctx.stroke();
    const y = PAD + (i / 4) * plotH;
    ctx.beginPath(); ctx.moveTo(PAD, y); ctx.lineTo(PAD + plotW, y); ctx.stroke();
  }

  // Axes labels
  ctx.fillStyle = "#7a8ba8";
  ctx.font = "11px 'JetBrains Mono', monospace";
  ctx.textAlign = "center";
  for (let sig = 0; sig <= 3; sig++) {
    const x = PAD + (sig / 3) * plotW;
    ctx.fillText(sig + "σ", x, PAD + plotH + 18);
  }
  ctx.textAlign = "right";
  for (let conf = 0; conf <= 4; conf++) {
    const y = PAD + plotH - (conf / 4) * plotH;
    ctx.fillText((conf * 25) + "%", PAD - 6, y + 4);
  }

  // Axis titles
  ctx.save();
  ctx.translate(14, PAD + plotH / 2);
  ctx.rotate(-Math.PI / 2);
  ctx.textAlign = "center";
  ctx.fillStyle = "#7a8ba8";
  ctx.font = "11px 'JetBrains Mono', monospace";
  ctx.fillText("Theoretical Confidence", 0, 0);
  ctx.restore();
  ctx.textAlign = "center";
  ctx.fillText("Current Tension (σ)", PAD + plotW / 2, H - 8);

  // Falsification threshold line at 3σ
  const falseX = PAD + (3 / 3) * plotW;
  ctx.strokeStyle = "rgba(255,69,58,0.35)";
  ctx.lineWidth = 1.5;
  ctx.setLineDash([4, 4]);
  ctx.beginPath(); ctx.moveTo(falseX, PAD); ctx.lineTo(falseX, PAD + plotH); ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = "rgba(255,69,58,0.7)";
  ctx.font = "10px 'JetBrains Mono', monospace";
  ctx.fillText("Falsification →", falseX - 4, PAD - 6);

  // Draw tension nodes
  const hitRegions = [];
  for (const t of tensions) {
    const sigma = t.sigma ?? 0;
    const conf = t.confidence ?? 0.5;
    const px = PAD + Math.min(sigma / 3, 1) * plotW;
    const py = PAD + plotH - conf * plotH;
    const isSelected = t.id === selectedId;
    const r = isSelected ? 14 : 10;

    // Node glow
    const sigmaFrac = Math.min(sigma / 3, 1);
    const nodeColor = `hsl(${200 - sigmaFrac * 160}, 80%, 60%)`;

    if (isSelected) {
      ctx.shadowBlur = 18;
      ctx.shadowColor = nodeColor;
    }
    ctx.beginPath();
    ctx.arc(px, py, r, 0, Math.PI * 2);
    ctx.fillStyle = isSelected ? nodeColor : nodeColor.replace("60%", "45%");
    ctx.fill();
    ctx.strokeStyle = isSelected ? "#e8ecf4" : "rgba(232,236,244,0.4)";
    ctx.lineWidth = isSelected ? 2 : 1;
    ctx.stroke();
    ctx.shadowBlur = 0;

    hitRegions.push({ tension: t, x: px, y: py, r });

    // Label
    ctx.fillStyle = isSelected ? "#e8ecf4" : "#7a8ba8";
    ctx.font = isSelected ? "bold 11px 'JetBrains Mono', monospace" : "10px 'JetBrains Mono', monospace";
    ctx.textAlign = "center";
    ctx.fillText(t.label.length > 18 ? t.label.slice(0, 17) + "…" : t.label, px, py - r - 5);
  }

  return hitRegions;
}

// ── Card rendering helpers ─────────────────────────────────────────────────

export function gateColor(gate) {
  return GATE_COLORS[gate] ?? "#7a8ba8";
}

export function gateLabel(gate) {
  return GATE_LABELS[gate] ?? gate;
}

export function formatTension(sigma) {
  if (sigma == null) return "—";
  return sigma.toFixed(2) + "σ";
}

export function trackBadge(track) {
  const map = {
    HARDGATE: { label: "HARDGATE", color: "#30d158" },
    ADJACENT_TRACK: { label: "ADJACENT", color: "#7c4dff" },
    OPEN_TENSION: { label: "OPEN TENSION", color: "#ff453a" },
  };
  return map[track] ?? { label: track, color: "#7a8ba8" };
}

// ── Claim card HTML ────────────────────────────────────────────────────────

export function renderClaimCard(claim, score) {
  const gc = gateColor(claim.gate);
  const gl = gateLabel(claim.gate);
  const tb = trackBadge(claim.track);

  const admHtml = claim.admission
    ? `<div class="iq-admission">⚠️ ${escHtml(claim.admission)}</div>`
    : "";
  const tensHtml = claim.tension_sigma != null
    ? `<div class="iq-tension">Current tension: <strong>${formatTension(claim.tension_sigma)}</strong></div>`
    : "";
  const scoreHtml = score != null
    ? `<span class="iq-score">Match: ${score}%</span>`
    : "";
  const pillarHtml = claim.pillar != null
    ? `<span class="iq-pillar-badge">Pillar ${claim.pillar}</span>` : "";

  return `
<div class="iq-card" data-id="${escHtml(claim.id)}">
  <div class="iq-card-header">
    <div class="iq-badges">
      ${pillarHtml}
      <span class="iq-track-badge" style="color:${tb.color};border-color:${tb.color}40">${tb.label}</span>
      <span class="iq-gate-badge" style="color:${gc};border-color:${gc}40;background:${gc}12">${gl}</span>
      ${scoreHtml}
    </div>
    <div class="iq-claim-text">${escHtml(claim.claim)}</div>
  </div>
  <div class="iq-card-body">
    <div class="iq-row"><span class="iq-label">Predicted:</span><span class="iq-val">${escHtml(claim.predicted_value ?? "—")}</span></div>
    <div class="iq-row"><span class="iq-label">Observed:</span><span class="iq-val">${escHtml(claim.observed_value ?? "—")}</span></div>
    ${tensHtml}
    <div class="iq-falsification">🔬 Falsifies if: ${escHtml(claim.falsification ?? "Not applicable")}</div>
    ${admHtml}
  </div>
  <div class="iq-tags">${(claim.tags ?? []).map(t => `<span class="iq-tag">${escHtml(t)}</span>`).join("")}</div>
</div>`;
}

export function escHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// ── Main app controller ────────────────────────────────────────────────────

export class Interrogator {
  constructor() {
    this.kb = null;
    this.mode = "challenge"; // challenge | experiment | tension
    this.hitRegions = [];
    this.selectedTensionId = null;
  }

  async init() {
    const resp = await fetch(KB_PATH);
    this.kb = await resp.json();
    this._setupUI();
    this._renderExperimentList();
    this._renderTensionMap();
  }

  _setupUI() {
    // Mode tabs
    document.querySelectorAll(".iq-tab").forEach(tab => {
      tab.addEventListener("click", () => {
        this.setMode(tab.dataset.mode);
      });
    });

    // Challenge search
    const input = document.getElementById("iq-challenge-input");
    const btn = document.getElementById("iq-challenge-btn");
    if (input && btn) {
      btn.addEventListener("click", () => this._runChallenge(input.value));
      input.addEventListener("keydown", e => { if (e.key === "Enter") this._runChallenge(input.value); });
      input.addEventListener("input", () => {
        if (input.value.length >= 3) this._runChallenge(input.value);
        else document.getElementById("iq-challenge-results").innerHTML = "";
      });
    }

    // Tension map canvas click
    const canvas = document.getElementById("iq-tension-canvas");
    if (canvas) {
      canvas.addEventListener("click", e => this._handleCanvasClick(e, canvas));
      canvas.addEventListener("mousemove", e => this._handleCanvasHover(e, canvas));
    }
  }

  setMode(mode) {
    this.mode = mode;
    document.querySelectorAll(".iq-tab").forEach(t => {
      t.classList.toggle("active", t.dataset.mode === mode);
    });
    document.querySelectorAll(".iq-panel").forEach(p => {
      p.classList.toggle("active", p.dataset.panel === mode);
    });
    if (mode === "tension") this._renderTensionMap();
  }

  _runChallenge(query) {
    const container = document.getElementById("iq-challenge-results");
    if (!container || !this.kb) return;
    if (!query || query.trim().length < 2) { container.innerHTML = ""; return; }

    const results = searchClaims(this.kb, query);
    if (results.length === 0) {
      container.innerHTML = `<div class="iq-empty">No matching claims found for "${escHtml(query)}".<br>Try: "birefringence", "Higgs", "n_s", "CMB", "neutrino", or a pillar number.</div>`;
      return;
    }
    container.innerHTML = results.slice(0, 8).map(r => renderClaimCard(r.claim, r.score)).join("");
  }

  _renderExperimentList() {
    const container = document.getElementById("iq-experiment-list");
    const detail = document.getElementById("iq-experiment-detail");
    if (!container || !this.kb) return;

    container.innerHTML = this.kb.experiments.map(exp => `
      <div class="iq-exp-item" data-id="${escHtml(exp.id)}">
        <div class="iq-exp-name">${escHtml(exp.name)}</div>
        <div class="iq-exp-status">${escHtml(exp.status.replace(/_/g, " "))}</div>
      </div>`).join("");

    container.querySelectorAll(".iq-exp-item").forEach(item => {
      item.addEventListener("click", () => {
        container.querySelectorAll(".iq-exp-item").forEach(i => i.classList.remove("selected"));
        item.classList.add("selected");
        this._showExperimentDetail(item.dataset.id, detail);
      });
    });
  }

  _showExperimentDetail(expId, container) {
    if (!this.kb) return;
    const exp = this.kb.experiments.find(e => e.id === expId);
    if (!exp) return;
    const claims = claimsForExperiment(this.kb, expId);
    const claimsHtml = claims.length > 0
      ? claims.map(c => renderClaimCard(c, null)).join("")
      : `<div class="iq-empty">No specific claims pre-registered for this experiment yet.<br>Check back after Pillar 790 (KK dark matter candidate).</div>`;

    container.innerHTML = `
      <h3 class="iq-exp-detail-title">${escHtml(exp.name)}</h3>
      <p class="iq-exp-desc">${escHtml(exp.description)}</p>
      <div class="iq-detail-meta">
        <span class="iq-gate-badge" style="color:#3b8bff;border-color:#3b8bff40;background:#3b8bff12">Status: ${escHtml(exp.status.replace(/_/g, " "))}</span>
        ${exp.primary ? '<span class="iq-gate-badge" style="color:#ff453a;border-color:#ff453a40;background:#ff453a12">PRIMARY FALSIFIER</span>' : ""}
      </div>
      <h4 class="iq-section-title">Claims this experiment tests:</h4>
      ${claimsHtml}`;
  }

  _renderTensionMap() {
    const canvas = document.getElementById("iq-tension-canvas");
    const detail = document.getElementById("iq-tension-detail");
    if (!canvas || !this.kb) return;

    const tensions = sortedTensions(this.kb);
    this.hitRegions = drawTensionMap(canvas, tensions, this.selectedTensionId);

    if (detail && this.selectedTensionId) {
      const t = tensions.find(t => t.id === this.selectedTensionId);
      if (t) this._showTensionDetail(t, detail);
    }
  }

  _handleCanvasClick(e, canvas) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const mx = (e.clientX - rect.left) * scaleX;
    const my = (e.clientY - rect.top) * scaleY;

    for (const region of this.hitRegions) {
      const dx = mx - region.x, dy = my - region.y;
      if (Math.sqrt(dx * dx + dy * dy) <= region.r + 4) {
        this.selectedTensionId = region.tension.id;
        this._renderTensionMap();
        const detail = document.getElementById("iq-tension-detail");
        if (detail) this._showTensionDetail(region.tension, detail);
        return;
      }
    }
  }

  _handleCanvasHover(e, canvas) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const mx = (e.clientX - rect.left) * scaleX;
    const my = (e.clientY - rect.top) * scaleY;
    let hit = false;
    for (const region of this.hitRegions) {
      const dx = mx - region.x, dy = my - region.y;
      if (Math.sqrt(dx * dx + dy * dy) <= region.r + 4) { hit = true; break; }
    }
    canvas.style.cursor = hit ? "pointer" : "default";
  }

  _showTensionDetail(t, container) {
    const claims = (t.pillar_ids ?? [])
      .map(id => this.kb.claims.find(c => c.id === id))
      .filter(Boolean);

    container.innerHTML = `
      <h3 class="iq-exp-detail-title">${escHtml(t.label)}</h3>
      <p class="iq-exp-desc">${escHtml(t.description)}</p>
      <div class="iq-detail-meta">
        <span class="iq-gate-badge" style="color:#ff9f0a;border-color:#ff9f0a40;background:#ff9f0a12">
          Tension: ${formatTension(t.sigma)}
        </span>
        <span class="iq-gate-badge" style="color:#3b8bff;border-color:#3b8bff40;background:#3b8bff12">
          Confidence: ${Math.round((t.confidence ?? 0) * 100)}%
        </span>
      </div>
      <div class="iq-row" style="margin:.75rem 0"><span class="iq-label">Next test:</span><span class="iq-val">${escHtml(t.experiment)}</span></div>
      <h4 class="iq-section-title">Related claims:</h4>
      ${claims.map(c => renderClaimCard(c, null)).join("") || '<div class="iq-empty">No linked claims.</div>'}`;
  }
}
