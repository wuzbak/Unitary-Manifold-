/**
 * Unitary Manifold Braid Convergence Chart (U-BCC) — Interactive Renderer
 * AxiomZero Technologies & Consulting, SPC
 *
 * Renders a Smith-chart-analogue for the 5D/4D Kaluza-Klein state space.
 * All math derived from src/core/metric.py, src/core/fixed_point.py,
 * src/core/evolution.py, and src/core/chart_coords.py.
 *
 * Coordinate map (dimensionless, hat = normalised):
 *   r = sqrt(w_B·B̂² + w_φ·φ̂² + w_K·K̂² + w_U·Û²)    (radial, Eq. 2.1)
 *   θ = atan2(n₂, n₁) ∈ [0, 2π)                         (angular, Eq. 2.2)
 *   k_CS = n₁² + n₂²                                     (topological braid index)
 *
 * Level-set families:
 *   Resistance circles  → R₄ = const   (4D curvature, right sector)
 *   Reactance arcs      → G_eff = const (effective coupling, right sector)
 *   Curvature gradient  → ∇K = const   (left / bulk sector)
 *   Duality coefficient → U_bulk = const
 */

'use strict';

/* ─── Constants ─────────────────────────────────────────────────────────── */
const K_CS_CRITICAL = 74;          // k_CS = 5² + 7² = 74
const N1_CANONICAL  = 5;
const N2_CANONICAL  = 7;
const NS_CENTRAL    = 0.9635;      // spectral index central value
const NS_SIGMA      = 0.0042;      // ±1σ Planck uncertainty
const R_TENSOR      = 0.0315;      // tensor-to-scalar ratio
const C_BRAID       = 12 / 37;    // braided sound speed
const FIXED_POINT_R = 0.5;        // x* lives at r=0.5 on the stable groundline

/* ─── State ──────────────────────────────────────────────────────────────── */
let canvas, ctx, tooltip;
let W = 700, H = 700;   // canvas size (updated on resize)
let CX, CY, RADIUS;     // chart centre & radius (recomputed)

let params = {
  wB: 0.25, wPhi: 0.25, wK: 0.25, wU: 0.25,  // radial weights (sum to 1)
  n1: N1_CANONICAL, n2: N2_CANONICAL,
  eps: 1e-4,         // convergence threshold
  iterations: 20,    // fixed-point steps
  showResistance: true,
  showReactance: true,
  showBraidGrid: true,
  showTrajectory: true,
};

/* ─── Initialisation ─────────────────────────────────────────────────────── */
function initChart(canvasId, tooltipId) {
  canvas  = document.getElementById(canvasId);
  tooltip = document.getElementById(tooltipId);
  ctx     = canvas.getContext('2d');

  resizeChart();
  window.addEventListener('resize', resizeChart);
  canvas.addEventListener('mousemove', onMouseMove);
  canvas.addEventListener('mouseleave', onMouseLeave);
  canvas.addEventListener('click', onClick);

  render();
}

function resizeChart() {
  const container = canvas.parentElement;
  const size = Math.min(container.clientWidth, window.innerHeight * 0.85, 720);
  W = H = size;
  canvas.width  = W;
  canvas.height = H;
  CX     = W / 2;
  CY     = H / 2;
  RADIUS = W * 0.42;
  render();
}

/* ─── Top-level render ───────────────────────────────────────────────────── */
function render() {
  ctx.clearRect(0, 0, W, H);
  drawBackground();
  drawOuterScale();
  drawSectorBoundary();
  if (params.showResistance) drawResistanceCircles();
  if (params.showReactance)  drawReactanceArcs();
  if (params.showBraidGrid)  drawBraidGrid();
  if (params.showTrajectory) drawFixedPointTrajectory();
  drawCriticalPoints();
  drawGroundlines();
  drawAxisLabels();
  drawLegend();
}

/* ─── Background & outer ring ────────────────────────────────────────────── */
function drawBackground() {
  // Outer circle clip
  ctx.save();
  ctx.beginPath();
  ctx.arc(CX, CY, RADIUS, 0, Math.PI * 2);
  ctx.clip();

  // Left half: 5D bulk (parity-even) — deep navy
  ctx.fillStyle = '#0a1630';
  ctx.fillRect(0, 0, CX, H);

  // Right half: 4D brane (parity-odd) — slightly lighter
  ctx.fillStyle = '#0d1e3a';
  ctx.fillRect(CX, 0, W - CX, H);

  // Subtle radial gradient overlay
  const grd = ctx.createRadialGradient(CX, CY, 0, CX, CY, RADIUS);
  grd.addColorStop(0,   'rgba(59,139,255,0.06)');
  grd.addColorStop(0.6, 'rgba(59,139,255,0.02)');
  grd.addColorStop(1,   'rgba(0,0,0,0)');
  ctx.fillStyle = grd;
  ctx.fillRect(0, 0, W, H);

  ctx.restore();

  // Outer ring border
  ctx.beginPath();
  ctx.arc(CX, CY, RADIUS, 0, Math.PI * 2);
  ctx.strokeStyle = '#3b8bff';
  ctx.lineWidth = 2.5;
  ctx.stroke();
}

/* ─── Outer braid-index scale ────────────────────────────────────────────── */
function drawOuterScale() {
  // Marks every 10° around the outer ring with k_CS = n₁² + n₂² values
  const tickR  = RADIUS + 8;
  const labelR = RADIUS + 22;
  ctx.font = `${Math.max(9, W * 0.013)}px JetBrains Mono, monospace`;
  ctx.fillStyle   = '#7aa8d8';
  ctx.textAlign   = 'center';
  ctx.textBaseline = 'middle';
  ctx.strokeStyle = '#3b5f8a';
  ctx.lineWidth   = 1;

  for (let deg = 0; deg < 360; deg += 10) {
    const rad = degToRad(deg);
    const cos = Math.cos(rad), sin = Math.sin(rad);

    // Tick
    ctx.beginPath();
    ctx.moveTo(CX + RADIUS * cos, CY + RADIUS * sin);
    ctx.lineTo(CX + tickR  * cos, CY + tickR  * sin);
    ctx.stroke();

    // k_CS label every 30°
    if (deg % 30 === 0) {
      const n1 = Math.round(Math.cos(rad) * 7);
      const n2 = Math.round(Math.sin(rad) * 7);
      const kcs = n1 * n1 + n2 * n2;
      ctx.fillText(String(kcs), CX + labelR * cos, CY + labelR * sin);
    }
  }
}

/* ─── Sector boundary (parity split) ────────────────────────────────────── */
function drawSectorBoundary() {
  ctx.save();
  ctx.setLineDash([6, 4]);
  ctx.strokeStyle = 'rgba(180, 200, 255, 0.35)';
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.moveTo(CX, CY - RADIUS);
  ctx.lineTo(CX, CY + RADIUS);
  ctx.stroke();

  // Γ_L label (π sector)
  ctx.setLineDash([]);
  ctx.fillStyle = '#7aa8d8';
  ctx.font = `bold ${Math.max(11, W * 0.016)}px Inter, sans-serif`;
  ctx.textAlign = 'right';
  ctx.fillText('Γ_L', CX - 8, CY);

  // Γ_R label (0 sector)
  ctx.textAlign = 'left';
  ctx.fillText('Γ_R', CX + 8, CY);

  ctx.restore();
}

/* ─── Groundlines (analogous to 50Ω line) ───────────────────────────────── */
function drawGroundlines() {
  ctx.save();
  ctx.strokeStyle = 'rgba(59, 139, 255, 0.5)';
  ctx.lineWidth   = 1.5;
  ctx.setLineDash([]);

  // Horizontal real axis
  ctx.beginPath();
  ctx.moveTo(CX - RADIUS, CY);
  ctx.lineTo(CX + RADIUS, CY);
  ctx.stroke();

  // V* = 1.0 annotation
  ctx.fillStyle = '#7aa8d8';
  ctx.font = `${Math.max(9, W * 0.013)}px Inter, sans-serif`;
  ctx.textAlign = 'center';
  ctx.fillText('STABLE GROUNDLINE (V*=1.0)', CX - RADIUS * 0.35, CY + 14);
  ctx.fillText('STABLE GROUNDLINE (V*=1.0)', CX + RADIUS * 0.35, CY + 14);
  ctx.restore();
}

/* ─── Resistance circles (constant-R₄ level sets) ───────────────────────── */
function drawResistanceCircles() {
  // In the Smith chart analogy, constant-R circles pass through Γ_R (right edge)
  // Mapped: circle centre at (CX + RADIUS·R/(R+1), CY), radius = RADIUS/(R+1)
  const rValues = [0, 0.2, 0.5, 1, 2, 5, 10, 20, 50];
  ctx.save();
  ctx.beginPath();
  ctx.arc(CX, CY, RADIUS, 0, Math.PI * 2);
  ctx.clip();

  rValues.forEach((R, idx) => {
    const cx   = CX + RADIUS * R / (R + 1);
    const r    = RADIUS / (R + 1);
    const hue  = 200 + idx * 8;
    ctx.beginPath();
    ctx.arc(cx, CY, r, 0, Math.PI * 2);
    ctx.strokeStyle = `hsla(${hue},60%,65%,0.28)`;
    ctx.lineWidth   = R === 1 ? 1.5 : 0.8;
    ctx.stroke();

    // Label inside chart
    if (r > RADIUS * 0.05) {
      ctx.fillStyle   = `hsla(${hue},60%,75%,0.55)`;
      ctx.font        = `${Math.max(8, W * 0.011)}px JetBrains Mono, monospace`;
      ctx.textAlign   = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(`R₄=${R}`, cx, CY - r * 0.35);
    }
  });

  ctx.restore();
}

/* ─── Reactance arcs (constant-G_eff level sets) ────────────────────────── */
function drawReactanceArcs() {
  // Constant-X arcs: centre at (CX + RADIUS, CY - RADIUS/X), radius = RADIUS/|X|
  const xValues = [0.2, 0.5, 1, 2, 5, -0.2, -0.5, -1, -2, -5];
  ctx.save();
  ctx.beginPath();
  ctx.arc(CX, CY, RADIUS, 0, Math.PI * 2);
  ctx.clip();

  xValues.forEach(X => {
    const cy_arc = CY - RADIUS / X;
    const r_arc  = Math.abs(RADIUS / X);
    ctx.beginPath();
    ctx.arc(CX + RADIUS, cy_arc, r_arc, 0, Math.PI * 2);
    ctx.strokeStyle = X > 0
      ? 'rgba(255, 160, 80, 0.22)'
      : 'rgba(160, 255, 180, 0.22)';
    ctx.lineWidth = 0.8;
    ctx.stroke();

    // Label
    const labelAngle = X > 0 ? -Math.PI * 0.35 : Math.PI * 0.35;
    const lx = CX + RADIUS + r_arc * Math.cos(labelAngle);
    const ly = cy_arc       + r_arc * Math.sin(labelAngle);
    if (lx > CX - RADIUS && lx < CX + RADIUS && ly > CY - RADIUS && ly < CY + RADIUS) {
      ctx.fillStyle = X > 0 ? 'rgba(255,160,80,0.6)' : 'rgba(160,255,180,0.6)';
      ctx.font = `${Math.max(8, W * 0.011)}px JetBrains Mono, monospace`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(`G=${X}`, lx, ly);
    }
  });

  ctx.restore();
}

/* ─── Braid grid (angular θ spokes for k_CS values) ─────────────────────── */
function drawBraidGrid() {
  // Draw spokes at θ = atan2(n₂,n₁) for small integer pairs
  const pairs = [
    [1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1],
    [2,1],[1,2],[-1,2],[-2,1],[-2,-1],[-1,-2],[1,-2],[2,-1],
    [3,1],[1,3],[-1,3],[-3,1],[-3,-1],[-1,-3],[1,-3],[3,-1],
    [5,7],[7,5],[-5,7],[-7,5],[-5,-7],[-7,-5],[5,-7],[7,-5],
  ];

  ctx.save();
  ctx.beginPath();
  ctx.arc(CX, CY, RADIUS, 0, Math.PI * 2);
  ctx.clip();

  pairs.forEach(([n1, n2]) => {
    const angle = Math.atan2(n2, n1);
    const kcs   = n1 * n1 + n2 * n2;
    const isCanonical = (Math.abs(n1) === 5 && Math.abs(n2) === 7) ||
                        (Math.abs(n1) === 7 && Math.abs(n2) === 5);

    ctx.beginPath();
    ctx.moveTo(CX, CY);
    ctx.lineTo(CX + RADIUS * Math.cos(angle), CY + RADIUS * Math.sin(angle));
    ctx.strokeStyle = isCanonical
      ? 'rgba(180, 120, 255, 0.55)'
      : 'rgba(100, 150, 220, 0.15)';
    ctx.lineWidth = isCanonical ? 1.5 : 0.7;
    ctx.stroke();

    // k_CS label near rim for canonical pair
    if (isCanonical) {
      const lr = RADIUS * 0.88;
      ctx.fillStyle   = '#b47aff';
      ctx.font        = `bold ${Math.max(10, W * 0.015)}px JetBrains Mono, monospace`;
      ctx.textAlign   = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(`k=${kcs}`, CX + lr * Math.cos(angle), CY + lr * Math.sin(angle));
    }
  });

  ctx.restore();
}

/* ─── Fixed-point trajectory (iterates T(x)) ────────────────────────────── */
/**
 * Fixed-point map T(x) in polar (r,θ) coordinates:
 *   T_r(r, θ) = r · exp(−λ · (r − r*))        contractive in r
 *   T_θ(r, θ) = θ + δθ · sin(θ)               rotates toward real axis
 * where r* = FIXED_POINT_R, λ=2.5, δθ=−0.15
 * This is a phenomenological model matching src/core/fixed_point.py behaviour.
 */
function fixedPointMap(r, theta) {
  const rStar = FIXED_POINT_R;
  const lambda = 2.5;
  const dTheta = -0.15;
  const rNew     = r * Math.exp(-lambda * (r - rStar));
  const thetaNew = theta + dTheta * Math.sin(theta);
  return { r: Math.max(0, Math.min(1, rNew)), theta: thetaNew };
}

function drawFixedPointTrajectory() {
  const theta0 = params.n2 !== 0 || params.n1 !== 0
    ? Math.atan2(params.n2, params.n1)
    : Math.PI / 4;
  const kcs = params.n1 * params.n1 + params.n2 * params.n2;
  const r0  = Math.min(0.92, Math.sqrt(kcs) / 14);

  const points = [{ r: r0, theta: theta0 }];
  let state = { r: r0, theta: theta0 };
  let converged = false;

  for (let i = 0; i < params.iterations; i++) {
    state = fixedPointMap(state.r, state.theta);
    points.push({ ...state });
    if (state.r < params.eps + FIXED_POINT_R && Math.abs(state.r - FIXED_POINT_R) < params.eps) {
      converged = true;
      break;
    }
  }

  ctx.save();
  ctx.beginPath();
  ctx.arc(CX, CY, RADIUS, 0, Math.PI * 2);
  ctx.clip();

  // Draw trajectory path
  ctx.beginPath();
  points.forEach((pt, i) => {
    const { px, py } = polarToCanvas(pt.r, pt.theta);
    if (i === 0) ctx.moveTo(px, py);
    else ctx.lineTo(px, py);
  });
  ctx.strokeStyle = '#d44fa0';
  ctx.lineWidth   = 2;
  ctx.setLineDash([5, 3]);
  ctx.stroke();
  ctx.setLineDash([]);

  // Draw dots at each iterate
  points.forEach((pt, i) => {
    const { px, py } = polarToCanvas(pt.r, pt.theta);
    ctx.beginPath();
    ctx.arc(px, py, i === 0 ? 5 : 3, 0, Math.PI * 2);
    const t = i / points.length;
    ctx.fillStyle = `hsla(${320 - t * 80}, 80%, 65%, 0.85)`;
    ctx.fill();
  });

  // Convergence label near final point
  const last = points[points.length - 1];
  const { px: lx, py: ly } = polarToCanvas(last.r, last.theta);
  ctx.fillStyle = '#d44fa0';
  ctx.font = `${Math.max(9, W * 0.013)}px Inter, sans-serif`;
  ctx.textAlign = 'left';
  ctx.fillText(converged ? 'x* (converged)' : `x_${points.length}`, lx + 8, ly - 5);

  ctx.restore();
}

/* ─── Critical points ────────────────────────────────────────────────────── */
function drawCriticalPoints() {
  const points = [
    {
      r: 0.72, theta: Math.PI,           // Sector Point A: 5D bulk
      color: '#3b8bff', label: 'A (5D bulk)',
      fill: '#3b8bff', ring: false,
    },
    {
      r: 0.72, theta: 0,                 // Sector Point B: 4D brane
      color: '#e05050', label: 'B (4D brane)',
      fill: '#e05050', ring: false,
    },
    {
      r: FIXED_POINT_R, theta: 0,        // Fixed point x*
      color: '#ffffff', label: 'x* (fixed point)',
      fill: 'transparent', ring: true,
    },
    {
      r: RADIUS * 0.985 / RADIUS,        // k_CS = 74 on brane rim
      theta: Math.atan2(N2_CANONICAL, N1_CANONICAL),
      color: '#b47aff', label: `k_CS=${K_CS_CRITICAL}`,
      fill: '#b47aff', ring: false,
    },
  ];

  ctx.save();
  points.forEach(pt => {
    const { px, py } = polarToCanvas(pt.r, pt.theta);
    ctx.beginPath();
    ctx.arc(px, py, 7, 0, Math.PI * 2);
    if (pt.ring) {
      ctx.strokeStyle = pt.color;
      ctx.lineWidth   = 2;
      ctx.stroke();
    } else {
      ctx.fillStyle = pt.fill;
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth   = 1;
      ctx.stroke();
    }
    ctx.fillStyle = pt.color;
    ctx.font = `bold ${Math.max(9, W * 0.013)}px Inter, sans-serif`;
    ctx.textAlign = px < CX ? 'right' : 'left';
    ctx.fillText(pt.label, px + (px < CX ? -10 : 10), py - 10);
  });
  ctx.restore();
}

/* ─── Axis labels ────────────────────────────────────────────────────────── */
function drawAxisLabels() {
  const f = Math.max(10, W * 0.014);
  ctx.font = `bold ${f}px Inter, sans-serif`;
  ctx.textAlign = 'center';

  // Top: +B_μ
  ctx.fillStyle = '#a0c0ff';
  ctx.fillText('+B_μ (IRREVERSIBILITY AXIS)', CX, CY - RADIUS - 28);

  // Bottom: −B_μ / braid index scale
  ctx.fillStyle = '#a0c0ff';
  ctx.fillText('−B_μ  |  TOPOLOGICAL BRAID INDEX k_CS', CX, CY + RADIUS + 28);

  // Left sector label
  ctx.font = `${Math.max(9, W * 0.012)}px Inter, sans-serif`;
  ctx.fillStyle = '#6699cc';
  ctx.fillText('5D GEOMETRIC / BULK SECTOR (parity-even)', CX - RADIUS * 0.5, CY - RADIUS * 0.78);

  // Right sector label
  ctx.fillStyle = '#6699cc';
  ctx.fillText('4D EFFECTIVE / BRANE SECTOR (parity-odd)', CX + RADIUS * 0.5, CY - RADIUS * 0.78);

  // n_s annotation with uncertainty
  ctx.font = `${Math.max(8, W * 0.012)}px JetBrains Mono, monospace`;
  ctx.fillStyle = '#88bbee';
  ctx.textAlign = 'left';
  ctx.fillText(`nₛ = ${NS_CENTRAL} ± ${NS_SIGMA}  [Planck 2018]`, CX - RADIUS + 8, CY + RADIUS - 24);
  ctx.fillText(`r = ${R_TENSOR}  [BICEP/Keck < 0.036]`, CX - RADIUS + 8, CY + RADIUS - 10);
}

/* ─── Legend ─────────────────────────────────────────────────────────────── */
function drawLegend() {
  const items = [
    { color: '#5599cc', dash: false, label: 'R₄ = const (4D curvature level sets)' },
    { color: '#e09050', dash: false, label: 'G_eff = const (effective coupling arcs)' },
    { color: '#b47aff', dash: false, label: 'Braid spokes (k_CS = n₁²+n₂²)' },
    { color: '#d44fa0', dash: true,  label: 'Evolution trajectory  xₖ₊₁ = T(xₖ)' },
    { color: '#3b8bff', dash: false, label: '● Sector Point A (5D bulk)' },
    { color: '#e05050', dash: false, label: '● Sector Point B (4D brane)' },
    { color: '#ffffff', dash: false, label: '○ Fixed Point x* (converged)' },
  ];

  const lx  = 12;
  let   ly  = 16;
  const lh  = Math.max(16, W * 0.023);
  ctx.font  = `${Math.max(9, W * 0.012)}px Inter, sans-serif`;

  items.forEach(item => {
    ctx.save();
    if (item.dash) ctx.setLineDash([5, 3]);
    ctx.strokeStyle = item.color;
    ctx.lineWidth   = 1.5;
    ctx.beginPath();
    ctx.moveTo(lx, ly + lh * 0.5 - 4);
    ctx.lineTo(lx + 20, ly + lh * 0.5 - 4);
    ctx.stroke();
    ctx.restore();
    ctx.fillStyle = item.color;
    ctx.textAlign = 'left';
    ctx.fillText(item.label, lx + 26, ly + lh * 0.5 - 2);
    ly += lh;
  });
}

/* ─── Hit test & coordinate readout ─────────────────────────────────────── */
function hitTest(mouseX, mouseY) {
  const dx = mouseX - CX;
  const dy = mouseY - CY;
  const r  = Math.sqrt(dx * dx + dy * dy) / RADIUS;
  if (r > 1) return null;

  const theta = Math.atan2(dy, dx);
  const kcs   = params.n1 * params.n1 + params.n2 * params.n2;

  // Recover dimensionless state components from r and θ (equal-weight approximation)
  const Bhat  = Math.sqrt(params.wB)  * r * Math.cos(theta);
  const Phihat = Math.sqrt(params.wPhi) * r * Math.sin(theta);
  const Khat  = r * Math.sqrt(params.wK);
  const Uhat  = r * Math.sqrt(params.wU);

  return {
    r: r.toFixed(4),
    theta_deg: (theta * 180 / Math.PI).toFixed(2),
    theta_rad: theta.toFixed(4),
    Bhat: Bhat.toFixed(4),
    Phihat: Phihat.toFixed(4),
    Khat: Khat.toFixed(4),
    Uhat: Uhat.toFixed(4),
    kcs,
    sector: dx < 0 ? '5D Bulk (parity-even)' : '4D Brane (parity-odd)',
  };
}

function onMouseMove(e) {
  const rect = canvas.getBoundingClientRect();
  const mx = (e.clientX - rect.left) * (W / rect.width);
  const my = (e.clientY - rect.top)  * (H / rect.height);
  const state = hitTest(mx, my);
  if (!state || !tooltip) return;

  tooltip.innerHTML = `
    <div class="tt-row"><span>r</span><span>${state.r}</span></div>
    <div class="tt-row"><span>θ</span><span>${state.theta_deg}°</span></div>
    <div class="tt-row"><span>B̂</span><span>${state.Bhat}</span></div>
    <div class="tt-row"><span>φ̂</span><span>${state.Phihat}</span></div>
    <div class="tt-row"><span>K̂</span><span>${state.Khat}</span></div>
    <div class="tt-row"><span>Û</span><span>${state.Uhat}</span></div>
    <div class="tt-row"><span>k_CS</span><span>${state.kcs}</span></div>
    <div class="tt-row"><span>Sector</span><span>${state.sector}</span></div>`;
  tooltip.style.display = 'block';
  tooltip.style.left    = (e.clientX + 14) + 'px';
  tooltip.style.top     = (e.clientY - 10) + 'px';
}

function onMouseLeave() {
  if (tooltip) tooltip.style.display = 'none';
}

/* ─── Click: set trajectory start at clicked point ──────────────────────── */
function onClick(e) {
  const rect = canvas.getBoundingClientRect();
  const mx = (e.clientX - rect.left) * (W / rect.width);
  const my = (e.clientY - rect.top)  * (H / rect.height);
  const dx = mx - CX, dy = my - CY;
  const r  = Math.sqrt(dx * dx + dy * dy) / RADIUS;
  if (r > 1) return;

  const theta = Math.atan2(dy, dx);
  // Reverse-map theta to nearest integer (n1,n2)
  params.n1 = Math.round(Math.cos(theta) * 7);
  params.n2 = Math.round(Math.sin(theta) * 7);
  if (params.n1 === 0 && params.n2 === 0) params.n1 = 1;

  // Sync sliders if present
  const n1El = document.getElementById('n1');
  const n2El = document.getElementById('n2');
  if (n1El) { n1El.value = params.n1; document.getElementById('n1-val').textContent = params.n1; }
  if (n2El) { n2El.value = params.n2; document.getElementById('n2-val').textContent = params.n2; }

  render();
}

/* ─── Export ─────────────────────────────────────────────────────────────── */
function exportPNG() {
  const link    = document.createElement('a');
  link.download = `u-bcc-chart-k${params.n1}${params.n2 >= 0 ? '+' : ''}${params.n2}.png`;
  link.href     = canvas.toDataURL('image/png');
  link.click();
}

/* ─── Utility ────────────────────────────────────────────────────────────── */
function degToRad(d) { return d * Math.PI / 180; }

function polarToCanvas(r, theta) {
  return {
    px: CX + r * RADIUS * Math.cos(theta),
    py: CY + r * RADIUS * Math.sin(theta),
  };
}

function updateParam(key, value) {
  params[key] = parseFloat(value);
  render();
}

function updateBoolParam(key, value) {
  params[key] = !!value;
  render();
}

function normaliseWeights() {
  const total = params.wB + params.wPhi + params.wK + params.wU;
  if (total === 0) return;
  params.wB   /= total;
  params.wPhi /= total;
  params.wK   /= total;
  params.wU   /= total;
  // Update displays
  ['wB','wPhi','wK','wU'].forEach(k => {
    const el  = document.getElementById(k + '-val');
    if (el) el.textContent = params[k].toFixed(3);
  });
  render();
}
