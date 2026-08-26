/**
 * Falsification Observatory — JS engine
 * Unitary Manifold v23 | Pillar 787 | AxiomZero Technologies & Consulting, SPC
 *
 * Implements all 7 experiment routing functions in pure JavaScript,
 * mirroring the Python oracle in src/core/pillar787_falsification_routing_oracle.py
 *
 * Theory & scientific direction: ThomasCory Walker-Pearson
 * Code architecture & synthesis: GitHub Copilot (AI)
 */

'use strict';

const FO = (() => {

  // ── Framework predictions (mirrored from Python oracle) ──────────────────
  const PRED = {
    BETA_C1: 0.273,     // deg
    BETA_C2: 0.331,     // deg
    BETA_WIN_MIN: 0.22,
    BETA_WIN_MAX: 0.38,
    BETA_GAP_LO: 0.29,
    BETA_GAP_HI: 0.31,
    BETA_KILL_SIGMA: 3.0,

    WA_PRED: 0.0,
    WA_KILL_SIGMA: 3.0,

    DM21_PRED: 7.53e-5,   // eV²
    DM21_WIN_LO: 7.0e-5,
    DM21_WIN_HI: 8.1e-5,

    R_PRED: 0.0315,
    R_KILL: 0.036,

    MG_PRED: 2.5,         // TeV
    MG_KILL: 5.0,         // TeV

    KK_DM_EW: 1e-46,      // cm²
    XENON_SENS: 5e-47,
  };

  // ── Verdict colours ───────────────────────────────────────────────────────
  const COLORS = {
    PASS: '#22c55e',
    TENSION: '#f59e0b',
    FALSIFIED: '#ef4444',
    AWAITING_DATA: '#94a3b8',
  };

  // ── Routing functions ─────────────────────────────────────────────────────

  function routeLiteBIRD(beta, betaSigma) {
    if (beta == null) {
      return verdict('EXP-1', 'LiteBIRD Cosmic Birefringence', 'AWAITING_DATA',
        `β ∈ {≈${PRED.BETA_C1}°, ≈${PRED.BETA_C2}°}`,
        null, null,
        `β outside [${PRED.BETA_WIN_MIN}°,${PRED.BETA_WIN_MAX}°] or inside gap (${PRED.BETA_GAP_LO}°,${PRED.BETA_GAP_HI}°) at ≥3σ`,
        [11, 13, 765, 771],
        'LiteBIRD launch ~2032. Primary falsifier for the braided-winding mechanism.'
      );
    }
    const dist1 = Math.abs(beta - PRED.BETA_C1);
    const dist2 = Math.abs(beta - PRED.BETA_C2);
    const distNearest = Math.min(dist1, dist2);
    const sigDev = betaSigma ? distNearest / betaSigma : null;
    const outsideWin = beta < PRED.BETA_WIN_MIN || beta > PRED.BETA_WIN_MAX;
    const inGap = beta > PRED.BETA_GAP_LO && beta < PRED.BETA_GAP_HI;
    const killMet = (outsideWin || inGap) && sigDev != null && sigDev >= PRED.BETA_KILL_SIGMA;
    const v = killMet ? 'FALSIFIED'
            : (outsideWin || inGap || (sigDev != null && sigDev > 1.5)) ? 'TENSION'
            : 'PASS';
    return verdict('EXP-1', 'LiteBIRD Cosmic Birefringence', v,
      `β ∈ {≈${PRED.BETA_C1}°, ≈${PRED.BETA_C2}°}`,
      beta + '°', sigDev,
      `β outside [${PRED.BETA_WIN_MIN}°,${PRED.BETA_WIN_MAX}°] or inside gap at ≥3σ`,
      [11, 13, 765, 771],
      `Nearest canonical: ${dist1 <= dist2 ? PRED.BETA_C1 : PRED.BETA_C2}°; Δ = ${distNearest.toFixed(4)}°`
    );
  }

  function routeDESI(wa, waSigma) {
    const waVal  = wa    != null ? wa    : -0.40;
    const waSig  = waSigma != null ? waSigma : 0.193;
    const sigDev = Math.abs(waVal - PRED.WA_PRED) / waSig;
    const killMet = sigDev >= PRED.WA_KILL_SIGMA;
    const v = killMet ? 'FALSIFIED' : sigDev >= 1.5 ? 'TENSION' : 'PASS';
    const isDefault = wa == null;
    return verdict('EXP-2', 'DESI Dark Energy w_a', v,
      `w_a = ${PRED.WA_PRED} (KK compactification locks w_a)`,
      waVal.toFixed(3), sigDev,
      `w_a ≠ 0 at ≥${PRED.WA_KILL_SIGMA}σ`,
      [5, 29, 38, 727, 739, 771],
      isDefault ? 'DESI DR2 input (2.07σ from w_a=0). DR3 is the decision point.'
                : 'User-supplied measurement.'
    );
  }

  function routeJUNO(dm21_raw, dm21Sigma, ordering) {
    const dm21 = dm21_raw != null ? dm21_raw * 1e-5 : PRED.DM21_PRED;
    const sig  = dm21Sigma != null ? dm21Sigma * 1e-5 : 0.18e-5;
    const sigDev = Math.abs(dm21 - PRED.DM21_PRED) / sig;
    const outsideWin = dm21 < PRED.DM21_WIN_LO || dm21 > PRED.DM21_WIN_HI;
    const ihConfirmed = ordering === 'IH';
    const killMet = ihConfirmed || (outsideWin && sigDev >= 2.0);
    const v = killMet ? 'FALSIFIED'
            : (outsideWin || sigDev >= 1.0) ? 'TENSION'
            : 'PASS';
    return verdict('EXP-3', 'JUNO Neutrino Δm²₂₁ + Ordering', v,
      `NH; Δm²₂₁ ∈ [7.0, 8.1]×10⁻⁵ eV²`,
      `${(dm21 * 1e5).toFixed(2)}×10⁻⁵ eV²`, sigDev,
      'Δm²₂₁ outside window at ≥2σ, or IH confirmed at ≥3σ',
      [772, 773, 786],
      ihConfirmed ? '⚠ IH ordering selected — kill condition MET.'
        : 'JUNO precision ~0.3% expected by 2025–2028. NH predicted (Pillar 786).'
    );
  }

  function routeACT(r95) {
    const rVal = r95 != null ? r95 : PRED.R_KILL;
    const killMet = PRED.R_PRED >= rVal;
    const v = killMet ? 'FALSIFIED' : 'PASS';
    return verdict('EXP-4', 'CMB-S4/ACT Tensor-to-Scalar r', v,
      `r = ${PRED.R_PRED} (braided-winding, Pillar 11)`,
      `95% CL < ${rVal}`, null,
      `r_pred (${PRED.R_PRED}) exceeds 95% CL upper limit`,
      [11, 13, 765],
      killMet
        ? `⚠ r_pred = ${PRED.R_PRED} > limit ${rVal} — FALSIFIED.`
        : `Margin: r_limit − r_pred = ${(rVal - PRED.R_PRED).toFixed(4)}. CMB-S4 will discriminate at 10σ.`
    );
  }

  function routeHLLHC(mgExcl) {
    const mg = mgExcl != null ? mgExcl : 1.8;
    const v = mg >= PRED.MG_KILL ? 'FALSIFIED'
            : mg >= PRED.MG_PRED ? 'TENSION'
            : 'PASS';
    return verdict('EXP-5', 'HL-LHC KK Graviton M_G*', v,
      `M_G* ≈ ${PRED.MG_PRED} TeV (narrow-width RS1)`,
      `Exclusion to ${mg} TeV`, null,
      `No signal found through 5 TeV exclusion`,
      [709],
      `Current exclusion: ${mg} TeV. HL-LHC Run 4 will reach ~5 TeV. Prediction: ${PRED.MG_PRED} TeV.`
    );
  }

  function routeNEDM() {
    return verdict('EXP-6', 'nEDM@SNS Electric Dipole Moment', 'PASS',
      'd_n ≈ 1×10⁻³⁰ e·cm (residual CP phase)',
      'Awaiting nEDM@SNS', null,
      'Null result < 10⁻³² e·cm (would constrain CP sector)',
      [731, 786],
      'Current limit: 1.8×10⁻²⁶ e·cm. nEDM@SNS target: ~10⁻²⁸ e·cm. Framework prediction well below current limit.'
    );
  }

  function routeXENON() {
    const limit = PRED.XENON_SENS;
    const v = limit < PRED.KK_DM_EW * 0.1 ? 'FALSIFIED'
            : limit < PRED.KK_DM_EW ? 'TENSION'
            : 'PASS';
    return verdict('EXP-7', 'XENON-nT KK Dark Matter', v,
      `σ_EW ≈ 1×10⁻⁴⁶ cm² (EW channel, Pillar 717)`,
      `Sensitivity: ${PRED.XENON_SENS.toExponential(0)} cm²`, null,
      `Null below ${(PRED.KK_DM_EW * 0.1).toExponential(0)} cm²`,
      [717],
      'EW-channel prediction at 10⁻⁴⁶ cm² is within XENON-nT design reach. Gravitational channel ~10⁻⁵⁶ cm² (null).'
    );
  }

  function verdict(code, name, v, pred, obs, sigDev, kill, pillars, note) {
    return { code, name, verdict: v, prediction: pred, observed: obs, sigDev, killDesc: kill, pillars, note };
  }

  // ── Oracle aggregation ────────────────────────────────────────────────────

  function runOracle(inputs = {}) {
    return [
      routeLiteBIRD(inputs.beta, inputs.betaSigma),
      routeDESI(inputs.wa, inputs.waSigma),
      routeJUNO(inputs.dm21, inputs.dm21Sigma, inputs.ordering),
      routeACT(inputs.r95),
      routeHLLHC(inputs.mg),
      routeNEDM(),
      routeXENON(),
    ];
  }

  function summary(results) {
    const counts = { PASS: 0, TENSION: 0, FALSIFIED: 0, AWAITING_DATA: 0 };
    results.forEach(r => { counts[r.verdict] = (counts[r.verdict] || 0) + 1; });
    const status = counts.FALSIFIED > 0 ? 'FRAMEWORK_FALSIFIED'
                 : counts.TENSION > 0   ? 'FRAMEWORK_UNDER_TENSION'
                 : 'FRAMEWORK_CONSISTENT';
    return { counts, status };
  }

  // ── Rendering ─────────────────────────────────────────────────────────────

  function sigmaBarHTML(sigDev, verdict) {
    if (sigDev == null) return '';
    const color = verdict === 'FALSIFIED' ? COLORS.FALSIFIED
                : verdict === 'TENSION'   ? COLORS.TENSION
                : COLORS.PASS;
    const fillPct = Math.min(sigDev / 5 * 100, 100);
    const killPct = 3 / 5 * 100; // 3σ = kill
    return `
      <div>
        <div class="sigma-gauge-label">σ deviation from prediction</div>
        <div class="sigma-bar-track">
          <div class="sigma-bar-fill" style="width:${fillPct.toFixed(1)}%;background:${color};"></div>
          <div class="sigma-threshold-marker" style="left:${killPct.toFixed(1)}%;"></div>
        </div>
        <div class="sigma-value">${sigDev.toFixed(2)}σ &nbsp; (kill: 3.0σ)</div>
      </div>`;
  }

  function renderCard(exp) {
    const v = exp.verdict;
    const badgeClass = `badge-${v}`;
    const cardClass  = `verdict-${v}`;
    const obsStr = exp.observed != null ? String(exp.observed) : '—';

    return `
      <div class="exp-card ${cardClass}" data-code="${exp.code}">
        <div class="exp-header">
          <div>
            <span class="exp-code">${exp.code}</span>
            <div class="exp-name" style="margin-top:0.3rem;">${exp.name}</div>
          </div>
          <span class="exp-verdict-badge ${badgeClass}">${v.replace('_', ' ')}</span>
        </div>
        <div class="exp-body">
          <div class="exp-row"><strong>Prediction:</strong> ${exp.prediction}</div>
          <div class="exp-row"><strong>Observed/Current:</strong> ${obsStr}</div>
          ${sigmaBarHTML(exp.sigDev, v)}
          <div class="exp-row kill-row">☠ Kill: ${exp.killDesc}</div>
          <div class="pillars-tag">
            ${exp.pillars.map(p => `<span class="pillar-chip">P-${p}</span>`).join('')}
          </div>
        </div>
        <div class="exp-footer">${exp.note}</div>
      </div>`;
  }

  function renderStatusBar(sum) {
    const el = document.getElementById('framework-status-bar');
    const txt = document.getElementById('framework-status-text');
    el.className = '';
    if (sum.status === 'FRAMEWORK_FALSIFIED') {
      el.classList.add('status-falsified');
      txt.textContent = `⚠ ${sum.status} — ${sum.counts.FALSIFIED} experiment(s) met kill condition`;
    } else if (sum.status === 'FRAMEWORK_UNDER_TENSION') {
      el.classList.add('status-tension');
      txt.textContent = `${sum.status} — ${sum.counts.TENSION} experiment(s) in tension`;
    } else {
      el.classList.add('status-consistent');
      txt.textContent = `${sum.status} — all open experiments within predicted ranges`;
    }
  }

  function renderTally(counts) {
    document.getElementById('tally-pass').textContent    = counts.PASS || 0;
    document.getElementById('tally-tension').textContent = counts.TENSION || 0;
    document.getElementById('tally-falsified').textContent = counts.FALSIFIED || 0;
    document.getElementById('tally-awaiting').textContent = counts.AWAITING_DATA || 0;
  }

  // ── Public API ────────────────────────────────────────────────────────────

  function readInputs() {
    const g = id => { const el = document.getElementById(id); return el ? el.value.trim() : ''; };
    const n = id => { const v = parseFloat(g(id)); return isNaN(v) ? null : v; };
    return {
      beta:      n('in-beta'),
      betaSigma: n('in-beta-sigma'),
      wa:        n('in-wa'),
      waSigma:   n('in-wa-sigma'),
      dm21:      n('in-dm21'),          // entered as ×10⁻⁵ eV²
      ordering:  g('in-ordering') || null,
      r95:       n('in-r'),
      mg:        n('in-mg'),
    };
  }

  function run() {
    const inputs  = readInputs();
    const results = runOracle(inputs);
    const sum     = summary(results);

    const grid = document.getElementById('exp-grid');
    if (grid) grid.innerHTML = results.map(renderCard).join('');

    renderStatusBar(sum);
    renderTally(sum.counts);
  }

  function reset() {
    ['in-beta','in-beta-sigma','in-wa','in-wa-sigma','in-dm21','in-r','in-mg']
      .forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
    const sel = document.getElementById('in-ordering');
    if (sel) sel.value = '';
    run();
  }

  // ── Test harness (for test_falsification_observatory.py via jsdom) ────────
  // Expose engine internals for headless testing
  const _test = {
    routeLiteBIRD, routeDESI, routeJUNO, routeACT, routeHLLHC, routeNEDM, routeXENON,
    runOracle, summary, PRED, COLORS,
  };

  return { run, reset, _test };

})();

// Make _test accessible at module level for test runners
if (typeof module !== 'undefined') module.exports = FO;
