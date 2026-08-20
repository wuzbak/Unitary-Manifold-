/**
 * um-image-generator.js — Canvas 2D physics image generator for the public site.
 * Generates downloadable PNG visualizations for key Unitary Manifold concepts.
 */

export const N_S = 0.9635;
export const R_BRAIDED = 0.0315;
export const BETA_LOW = 0.273;
export const BETA_HIGH = 0.331;
export const BETA_FLOOR = 0.22;
export const BETA_CEILING = 0.38;
export const WINDING_NUMBER = 5;
export const K_CS = 74;
export const DM21_TENSIONS = Object.freeze([2.98, 1.16, 1.07]);
export const LEAN4_THEOREMS = 976;
export const TEST_COUNT = 56747;

export const UM_IMAGE_CONSTANTS = Object.freeze({
  N_S,
  R_BRAIDED,
  BETA_LOW,
  BETA_HIGH,
  BETA_FLOOR,
  BETA_CEILING,
  WINDING_NUMBER,
  K_CS,
  DM21_TENSIONS,
  LEAN4_THEOREMS,
  TEST_COUNT,
});

export const VISUALIZATION_METADATA = Object.freeze({
  cmb: {
    label: "CMB n_s / r Plane",
    shortLabel: "CMB plane",
    filename: "um-cmb-ns-r-plane.png",
    summary: "Planck-era scalar tilt / tensor ratio plane with the UM prediction at (0.9635, 0.0315).",
  },
  birefringence: {
    label: "Birefringence β Window",
    shortLabel: "β window",
    filename: "um-birefringence-window.png",
    summary: "Admissible window, forbidden gap, and canonical UM birefringence predictions for LiteBIRD-era review.",
  },
  kkTower: {
    label: "KK Mass Tower",
    shortLabel: "KK tower",
    filename: "um-kk-mass-tower.png",
    summary: "First ten Kaluza-Klein modes rendered as a normalized 1/n² spectral ladder.",
  },
  braid: {
    label: "(5,7) Braid Topology",
    shortLabel: "(5,7) braid",
    filename: "um-braid-topology.png",
    summary: "Interleaved helical strands labelled by the canonical winding number n_w = 5 and k_CS = 74 geometry.",
  },
  metric: {
    label: "5D Metric Structure",
    shortLabel: "5D metric",
    filename: "um-5d-metric-structure.png",
    summary: "Block schematic of 4D spacetime, compact S¹ fiber, gauge connection A_μ, and radion φ.",
  },
  dm21: {
    label: "Δm²₂₁ Tension Timeline",
    shortLabel: "Δm²₂₁ timeline",
    filename: "um-dm21-tension-timeline.png",
    summary: "Residual solar-splitting tension reduction across Pillars 584, 772, and 773.",
  },
  domains: {
    label: "Hardgate Domain Pie Chart",
    shortLabel: "domain pie",
    filename: "um-hardgate-domain-pie.png",
    summary: "Schematic domain allocation for the 208 core hardgate physics pillars.",
  },
  calendar: {
    label: "Falsification Calendar",
    shortLabel: "calendar",
    filename: "um-falsification-calendar.png",
    summary: "Public-facing timeline of the major empirical decision surfaces: DESI DR3, JUNO, CMB-S4, LiteBIRD.",
  },
});

const COLORS = Object.freeze({
  bgTop: "#071224",
  bgBottom: "#020611",
  card: "#0a1428",
  line: "#203455",
  text: "#ebf3ff",
  muted: "#91a7c5",
  accent: "#4ea1ff",
  accentSoft: "rgba(78, 161, 255, 0.18)",
  gold: "#f0c040",
  goldSoft: "rgba(240, 192, 64, 0.16)",
  green: "#32d27c",
  red: "#ff6b6b",
  violet: "#9c7cff",
  cyan: "#61dafb",
  orange: "#ff9f43",
});

const HARDGATE_DOMAIN_COUNTS = Object.freeze([
  { label: "Geometry", value: 44, color: "#4ea1ff" },
  { label: "Cosmology", value: 31, color: "#73b5ff" },
  { label: "Particle / Flavor", value: 36, color: "#9c7cff" },
  { label: "Quantum", value: 22, color: "#61dafb" },
  { label: "Holography", value: 14, color: "#32d27c" },
  { label: "Multiverse", value: 18, color: "#f0c040" },
  { label: "Atomic / Nuclear", value: 21, color: "#ff9f43" },
  { label: "Formal / Verification", value: 22, color: "#ff6b6b" },
]);

const CALENDAR_EVENTS = Object.freeze([
  { year: 2026, label: "DESI DR3", detail: "wₐ routing / falsification gate", color: COLORS.orange },
  { year: 2027, label: "JUNO", detail: "Δm²₂₁ / ordering precision", color: COLORS.green },
  { year: 2030, label: "CMB-S4", detail: "tensor and residual stress test", color: COLORS.accent },
  { year: 2032, label: "LiteBIRD", detail: "β birefringence primary falsifier", color: COLORS.gold },
]);

function getCanvasContext(canvas) {
  if (!(canvas instanceof HTMLCanvasElement)) {
    throw new Error("Expected an HTMLCanvasElement.");
  }
  const ctx = canvas.getContext("2d");
  if (!ctx) {
    throw new Error("2D canvas context unavailable.");
  }
  return ctx;
}

function paintBackground(ctx, width, height) {
  const gradient = ctx.createLinearGradient(0, 0, 0, height);
  gradient.addColorStop(0, COLORS.bgTop);
  gradient.addColorStop(1, COLORS.bgBottom);
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, width, height);

  ctx.save();
  ctx.globalAlpha = 0.16;
  for (let i = 0; i < 18; i += 1) {
    ctx.beginPath();
    ctx.strokeStyle = i % 2 === 0 ? COLORS.accent : COLORS.gold;
    ctx.lineWidth = 1;
    ctx.arc(width * 0.85, height * 0.15, 60 + i * 18, Math.PI * 0.6, Math.PI * 1.5);
    ctx.stroke();
  }
  ctx.restore();
}

function drawFrame(ctx, width, height) {
  ctx.save();
  ctx.strokeStyle = COLORS.line;
  ctx.lineWidth = 2;
  roundRect(ctx, 24, 24, width - 48, height - 48, 18);
  ctx.stroke();
  ctx.restore();
}

function roundRect(ctx, x, y, width, height, radius) {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + width - radius, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
  ctx.lineTo(x + width, y + height - radius);
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
  ctx.lineTo(x + radius, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
  ctx.closePath();
}

function writeHeader(ctx, title, subtitle, width) {
  ctx.save();
  ctx.fillStyle = COLORS.text;
  ctx.font = "700 40px Inter, Arial, sans-serif";
  ctx.fillText(title, 68, 86);
  ctx.fillStyle = COLORS.muted;
  ctx.font = "500 19px Inter, Arial, sans-serif";
  wrapText(ctx, subtitle, 68, 122, width - 136, 28);
  ctx.restore();
}

function writeFooter(ctx, width, height) {
  ctx.save();
  ctx.fillStyle = COLORS.muted;
  ctx.font = "600 16px Inter, Arial, sans-serif";
  ctx.fillText("AxiomZero Technologies & Consulting, SPC", 68, height - 46);
  ctx.font = "500 14px Inter, Arial, sans-serif";
  ctx.fillText("Open science artifact for human review · Canvas 2D export", 68, height - 22);
  ctx.textAlign = "right";
  ctx.fillStyle = COLORS.gold;
  ctx.font = "600 16px JetBrains Mono, monospace";
  ctx.fillText(`Lean4 ${LEAN4_THEOREMS} · tests ${TEST_COUNT.toLocaleString()}`, width - 68, height - 28);
  ctx.restore();
}

function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
  const words = text.split(/\s+/);
  let line = "";
  let lineCount = 0;
  words.forEach((word) => {
    const candidate = line ? `${line} ${word}` : word;
    if (ctx.measureText(candidate).width > maxWidth && line) {
      ctx.fillText(line, x, y + lineCount * lineHeight);
      line = word;
      lineCount += 1;
    } else {
      line = candidate;
    }
  });
  if (line) {
    ctx.fillText(line, x, y + lineCount * lineHeight);
  }
}

function drawTag(ctx, x, y, label, fill, stroke) {
  ctx.save();
  ctx.font = "600 15px JetBrains Mono, monospace";
  const textWidth = ctx.measureText(label).width;
  const width = textWidth + 24;
  const height = 32;
  ctx.fillStyle = fill;
  ctx.strokeStyle = stroke;
  ctx.lineWidth = 1;
  roundRect(ctx, x, y, width, height, 10);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = COLORS.text;
  ctx.fillText(label, x + 12, y + 21);
  ctx.restore();
}

function axisMap(value, domainMin, domainMax, rangeMin, rangeMax) {
  const t = (value - domainMin) / (domainMax - domainMin);
  return rangeMin + t * (rangeMax - rangeMin);
}

function drawAxes(ctx, box, xTicks, yTicks, xLabel, yLabel) {
  ctx.save();
  ctx.strokeStyle = COLORS.line;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(box.left, box.bottom);
  ctx.lineTo(box.right, box.bottom);
  ctx.lineTo(box.right, box.top);
  ctx.stroke();

  ctx.fillStyle = COLORS.muted;
  ctx.font = "500 14px JetBrains Mono, monospace";

  xTicks.forEach((tick) => {
    const x = axisMap(tick.value, xTicks[0].value, xTicks[xTicks.length - 1].value, box.left, box.right);
    ctx.beginPath();
    ctx.moveTo(x, box.bottom);
    ctx.lineTo(x, box.bottom + 8);
    ctx.stroke();
    ctx.fillText(tick.label, x - 20, box.bottom + 28);
  });

  yTicks.forEach((tick) => {
    const y = axisMap(tick.value, yTicks[0].value, yTicks[yTicks.length - 1].value, box.bottom, box.top);
    ctx.beginPath();
    ctx.moveTo(box.left - 8, y);
    ctx.lineTo(box.left, y);
    ctx.stroke();
    ctx.fillText(tick.label, box.left - 56, y + 5);
  });

  ctx.fillStyle = COLORS.text;
  ctx.font = "600 16px Inter, Arial, sans-serif";
  ctx.fillText(xLabel, (box.left + box.right) / 2 - ctx.measureText(xLabel).width / 2, box.bottom + 58);
  ctx.save();
  ctx.translate(box.left - 74, (box.top + box.bottom) / 2);
  ctx.rotate(-Math.PI / 2);
  ctx.fillText(yLabel, -ctx.measureText(yLabel).width / 2, 0);
  ctx.restore();
  ctx.restore();
}

function paintCommon(ctx, canvas, title, subtitle) {
  paintBackground(ctx, canvas.width, canvas.height);
  drawFrame(ctx, canvas.width, canvas.height);
  writeHeader(ctx, title, subtitle, canvas.width);
  writeFooter(ctx, canvas.width, canvas.height);
}

export function drawCmbParameterPlane(canvas, params = {}) {
  const ctx = getCanvasContext(canvas);
  const width = canvas.width;
  const height = canvas.height;
  paintCommon(
    ctx,
    canvas,
    "CMB nₛ / r parameter plane",
    "UM prediction point at nₛ = 0.9635 and r = 0.0315, shown against a schematic Planck-era ellipse and BICEP/Keck upper band.",
  );

  const box = { left: 140, right: width - 110, top: 190, bottom: height - 120 };
  const xMin = 0.952;
  const xMax = 0.972;
  const yMin = 0.0;
  const yMax = 0.04;
  drawAxes(
    ctx,
    box,
    [0.952, 0.956, 0.960, 0.964, 0.968, 0.972].map((v) => ({ value: v, label: v.toFixed(3) })),
    [0.00, 0.01, 0.02, 0.03, 0.04].map((v) => ({ value: v, label: v.toFixed(2) })),
    "scalar tilt nₛ",
    "tensor ratio r",
  );

  const rBoundY = axisMap(0.036, yMin, yMax, box.bottom, box.top);
  ctx.save();
  ctx.fillStyle = "rgba(240, 192, 64, 0.08)";
  ctx.fillRect(box.left, box.top, box.right - box.left, rBoundY - box.top);
  ctx.strokeStyle = COLORS.gold;
  ctx.setLineDash([10, 8]);
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(box.left, rBoundY);
  ctx.lineTo(box.right, rBoundY);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = COLORS.gold;
  ctx.font = "600 15px Inter, Arial, sans-serif";
  ctx.fillText("BICEP/Keck upper band r < 0.036", box.right - 280, rBoundY - 10);
  ctx.restore();

  const ellipseCenterX = axisMap(0.9649, xMin, xMax, box.left, box.right);
  const ellipseCenterY = axisMap(0.018, yMin, yMax, box.bottom, box.top);
  ctx.save();
  ctx.fillStyle = "rgba(78, 161, 255, 0.10)";
  ctx.strokeStyle = COLORS.accent;
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.ellipse(ellipseCenterX, ellipseCenterY, 150, 90, -0.25, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = COLORS.accent;
  ctx.font = "600 16px Inter, Arial, sans-serif";
  ctx.fillText("schematic Planck ellipse", ellipseCenterX - 86, ellipseCenterY - 106);
  ctx.restore();

  const scatter = params.scatter || [
    { n: 0.9585, r: 0.029, color: COLORS.cyan },
    { n: 0.9608, r: 0.024, color: COLORS.violet },
    { n: 0.9621, r: 0.020, color: COLORS.green },
    { n: 0.9654, r: 0.027, color: COLORS.orange },
    { n: 0.9670, r: 0.013, color: COLORS.accent },
    { n: 0.9690, r: 0.009, color: COLORS.gold },
  ];
  scatter.forEach((point) => {
    const x = axisMap(point.n, xMin, xMax, box.left, box.right);
    const y = axisMap(point.r, yMin, yMax, box.bottom, box.top);
    ctx.save();
    ctx.globalAlpha = 0.95;
    ctx.fillStyle = point.color;
    ctx.beginPath();
    ctx.arc(x, y, 8, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  });

  const px = axisMap(N_S, xMin, xMax, box.left, box.right);
  const py = axisMap(R_BRAIDED, yMin, yMax, box.bottom, box.top);
  ctx.save();
  ctx.strokeStyle = COLORS.gold;
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(px - 16, py);
  ctx.lineTo(px + 16, py);
  ctx.moveTo(px, py - 16);
  ctx.lineTo(px, py + 16);
  ctx.stroke();
  ctx.fillStyle = COLORS.gold;
  ctx.beginPath();
  ctx.arc(px, py, 7, 0, Math.PI * 2);
  ctx.fill();
  drawTag(ctx, px + 18, py - 52, `UM (${N_S.toFixed(4)}, ${R_BRAIDED.toFixed(4)})`, COLORS.goldSoft, COLORS.gold);
  ctx.restore();

  drawTag(ctx, 68, 148, `n_w=${WINDING_NUMBER}`, COLORS.accentSoft, COLORS.accent);
  drawTag(ctx, 178, 148, `k_CS=${K_CS}`, COLORS.goldSoft, COLORS.gold);
}

export function drawBirefringenceWindow(canvas) {
  const ctx = getCanvasContext(canvas);
  const width = canvas.width;
  const height = canvas.height;
  paintCommon(
    ctx,
    canvas,
    "Birefringence β window",
    "Admissible interval [0.22°, 0.38°], forbidden gap [0.29°, 0.31°], and the two canonical UM predictions β = 0.273° and β = 0.331°.",
  );

  const left = 110;
  const right = width - 110;
  const y = height * 0.55;
  const min = 0.20;
  const max = 0.40;

  ctx.save();
  ctx.strokeStyle = COLORS.line;
  ctx.lineWidth = 10;
  ctx.lineCap = "round";
  ctx.beginPath();
  ctx.moveTo(left, y);
  ctx.lineTo(right, y);
  ctx.stroke();
  ctx.restore();

  const floorX = axisMap(BETA_FLOOR, min, max, left, right);
  const ceilX = axisMap(BETA_CEILING, min, max, left, right);
  const gapLeft = axisMap(0.29, min, max, left, right);
  const gapRight = axisMap(0.31, min, max, left, right);

  ctx.save();
  ctx.fillStyle = "rgba(50, 210, 124, 0.14)";
  roundRect(ctx, floorX, y - 45, ceilX - floorX, 90, 22);
  ctx.fill();
  ctx.fillStyle = "rgba(255, 107, 107, 0.18)";
  roundRect(ctx, gapLeft, y - 45, gapRight - gapLeft, 90, 18);
  ctx.fill();
  ctx.restore();

  [0.20, 0.22, 0.24, 0.26, 0.28, 0.30, 0.32, 0.34, 0.36, 0.38, 0.40].forEach((value) => {
    const x = axisMap(value, min, max, left, right);
    ctx.strokeStyle = COLORS.line;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(x, y - 14);
    ctx.lineTo(x, y + 14);
    ctx.stroke();
    ctx.fillStyle = COLORS.muted;
    ctx.font = "500 15px JetBrains Mono, monospace";
    ctx.fillText(`${value.toFixed(2)}°`, x - 18, y + 44);
  });

  [
    { beta: BETA_LOW, label: "β₁ = 0.273°", color: COLORS.accent },
    { beta: BETA_HIGH, label: "β₂ = 0.331°", color: COLORS.gold },
  ].forEach((entry, index) => {
    const x = axisMap(entry.beta, min, max, left, right);
    ctx.save();
    ctx.strokeStyle = entry.color;
    ctx.fillStyle = entry.color;
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(x, y - 70);
    ctx.lineTo(x, y + 70);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(x, y, 10, 0, Math.PI * 2);
    ctx.fill();
    drawTag(ctx, x - 56, index === 0 ? y - 124 : y - 164, entry.label, entry.color === COLORS.accent ? COLORS.accentSoft : COLORS.goldSoft, entry.color);
    ctx.restore();
  });

  drawTag(ctx, 92, 170, "admissible [0.22°, 0.38°]", "rgba(50, 210, 124, 0.14)", COLORS.green);
  drawTag(ctx, 360, 170, "forbidden gap [0.29°, 0.31°]", "rgba(255, 107, 107, 0.16)", COLORS.red);
  drawTag(ctx, 720, 170, "LiteBIRD ~2032", COLORS.goldSoft, COLORS.gold);

  ctx.fillStyle = COLORS.text;
  ctx.font = "600 18px Inter, Arial, sans-serif";
  ctx.fillText("Any measured β outside the green band, or inside the red gap, falsifies the braided-winding mechanism.", 110, height - 120);
}

export function drawKkMassTower(canvas) {
  const ctx = getCanvasContext(canvas);
  const width = canvas.width;
  const height = canvas.height;
  paintCommon(
    ctx,
    canvas,
    "Kaluza-Klein mass tower",
    "Normalized 1/n² spectral ladder for the first ten KK modes. Heights are relative weights, not collider-scale absolute masses.",
  );

  const box = { left: 110, right: width - 80, top: 220, bottom: height - 140 };
  const barWidth = (box.right - box.left) / 14;
  ctx.save();
  ctx.strokeStyle = COLORS.line;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(box.left, box.bottom);
  ctx.lineTo(box.right, box.bottom);
  ctx.moveTo(box.left, box.top);
  ctx.lineTo(box.left, box.bottom);
  ctx.stroke();
  ctx.restore();

  for (let n = 1; n <= 10; n += 1) {
    const spectralWeight = 1 / (n * n);
    const barHeight = spectralWeight * (box.bottom - box.top) * 0.9;
    const x = box.left + n * barWidth;
    const y = box.bottom - barHeight;
    const fill = n % 2 === 0 ? "rgba(78, 161, 255, 0.75)" : "rgba(240, 192, 64, 0.72)";
    ctx.fillStyle = fill;
    ctx.strokeStyle = n % 2 === 0 ? COLORS.accent : COLORS.gold;
    ctx.lineWidth = 2;
    roundRect(ctx, x, y, barWidth * 0.72, barHeight, 12);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = COLORS.text;
    ctx.font = "600 15px JetBrains Mono, monospace";
    ctx.fillText(`n=${n}`, x - 2, box.bottom + 28);
    ctx.fillStyle = COLORS.muted;
    ctx.font = "500 13px JetBrains Mono, monospace";
    ctx.fillText((spectralWeight).toFixed(3), x - 2, y - 12);
  }

  drawTag(ctx, 112, 162, "mₙ ∝ 1 / n²", COLORS.accentSoft, COLORS.accent);
  drawTag(ctx, 248, 162, "10 visible modes", COLORS.goldSoft, COLORS.gold);
  drawTag(ctx, 418, 162, `k_CS=${K_CS}`, COLORS.accentSoft, COLORS.accent);

  ctx.fillStyle = COLORS.muted;
  ctx.font = "500 16px Inter, Arial, sans-serif";
  ctx.fillText("normalized spectral weight", 118, box.top - 18);
}

export function drawBraidTopology(canvas) {
  const ctx = getCanvasContext(canvas);
  const width = canvas.width;
  const height = canvas.height;
  paintCommon(
    ctx,
    canvas,
    "(5,7) braid topology schematic",
    "Two interleaved helical strands rendered as a 2D projection of the canonical braided winding geometry.",
  );

  const centerX = width * 0.5;
  const centerY = height * 0.56;
  const length = width * 0.62;
  const amplitude = 92;
  const turns = 5;

  ctx.save();
  ctx.lineWidth = 14;
  ctx.lineCap = "round";
  ctx.strokeStyle = COLORS.accent;
  ctx.beginPath();
  for (let i = 0; i <= 320; i += 1) {
    const t = i / 320;
    const x = centerX - length / 2 + t * length;
    const y = centerY + Math.sin(t * Math.PI * turns * 2) * amplitude;
    if (i === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  }
  ctx.stroke();

  ctx.strokeStyle = COLORS.gold;
  ctx.beginPath();
  for (let i = 0; i <= 320; i += 1) {
    const t = i / 320;
    const x = centerX - length / 2 + t * length;
    const y = centerY + Math.sin(t * Math.PI * turns * 2 + Math.PI) * amplitude * 0.82;
    if (i === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  }
  ctx.stroke();
  ctx.restore();

  ctx.save();
  ctx.strokeStyle = "rgba(255,255,255,0.08)";
  ctx.lineWidth = 2;
  for (let i = 0; i <= 7; i += 1) {
    const x = centerX - length / 2 + (i / 7) * length;
    ctx.beginPath();
    ctx.moveTo(x, centerY - 150);
    ctx.lineTo(x, centerY + 150);
    ctx.stroke();
  }
  ctx.restore();

  drawTag(ctx, 120, 166, `n_w = ${WINDING_NUMBER}`, COLORS.accentSoft, COLORS.accent);
  drawTag(ctx, 250, 166, "interleaved helices", COLORS.goldSoft, COLORS.gold);
  drawTag(ctx, 452, 166, `k_CS = ${K_CS} = 5² + 7²`, COLORS.accentSoft, COLORS.accent);

  ctx.fillStyle = COLORS.text;
  ctx.font = "600 20px Inter, Arial, sans-serif";
  ctx.fillText("primary strand", centerX - length / 2, centerY - 144);
  ctx.fillStyle = COLORS.muted;
  ctx.font = "500 18px Inter, Arial, sans-serif";
  ctx.fillText("shadow / companion winding", centerX + 124, centerY + 164);
}

export function drawMetricStructure(canvas) {
  const ctx = getCanvasContext(canvas);
  const width = canvas.width;
  const height = canvas.height;
  paintCommon(
    ctx,
    canvas,
    "5D metric structure",
    "Schematic block rendering of the 4D base manifold, compact S¹ fiber, off-diagonal gauge connection A_μ, and radion φ scaling.",
  );

  const mainBox = { x: 120, y: 250, w: 430, h: 270 };
  const fiberBox = { x: 760, y: 280, w: 220, h: 220 };
  const gaugeBox = { x: 580, y: 340, w: 140, h: 110 };

  ctx.save();
  ctx.fillStyle = "rgba(78, 161, 255, 0.12)";
  ctx.strokeStyle = COLORS.accent;
  ctx.lineWidth = 3;
  roundRect(ctx, mainBox.x, mainBox.y, mainBox.w, mainBox.h, 24);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = COLORS.text;
  ctx.font = "700 28px Inter, Arial, sans-serif";
  ctx.fillText("4D spacetime", mainBox.x + 36, mainBox.y + 64);
  ctx.font = "500 20px JetBrains Mono, monospace";
  ctx.fillText("e^{2αφ} g_μν dx^μ dx^ν", mainBox.x + 36, mainBox.y + 122);
  ctx.fillStyle = COLORS.muted;
  ctx.font = "500 18px Inter, Arial, sans-serif";
  ctx.fillText("Lorentzian base metric", mainBox.x + 36, mainBox.y + 166);
  ctx.restore();

  ctx.save();
  ctx.fillStyle = "rgba(240, 192, 64, 0.12)";
  ctx.strokeStyle = COLORS.gold;
  ctx.lineWidth = 3;
  roundRect(ctx, fiberBox.x, fiberBox.y, fiberBox.w, fiberBox.h, 24);
  ctx.fill();
  ctx.stroke();
  ctx.beginPath();
  ctx.strokeStyle = COLORS.gold;
  ctx.lineWidth = 5;
  ctx.arc(fiberBox.x + fiberBox.w / 2, fiberBox.y + fiberBox.h / 2, 62, 0, Math.PI * 2);
  ctx.stroke();
  ctx.fillStyle = COLORS.text;
  ctx.font = "700 26px Inter, Arial, sans-serif";
  ctx.fillText("compact S¹", fiberBox.x + 44, fiberBox.y + 54);
  ctx.font = "500 18px JetBrains Mono, monospace";
  ctx.fillText("e^{2βφ}(dy + A_μ dx^μ)²", fiberBox.x - 26, fiberBox.y + fiberBox.h + 42);
  ctx.restore();

  ctx.save();
  ctx.fillStyle = "rgba(156, 124, 255, 0.14)";
  ctx.strokeStyle = COLORS.violet;
  ctx.lineWidth = 2;
  roundRect(ctx, gaugeBox.x, gaugeBox.y, gaugeBox.w, gaugeBox.h, 18);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = COLORS.text;
  ctx.font = "700 26px Inter, Arial, sans-serif";
  ctx.fillText("A_μ", gaugeBox.x + 42, gaugeBox.y + 58);
  ctx.fillStyle = COLORS.muted;
  ctx.font = "500 16px Inter, Arial, sans-serif";
  ctx.fillText("gauge connection", gaugeBox.x + 16, gaugeBox.y + 88);
  ctx.restore();

  ctx.save();
  ctx.strokeStyle = COLORS.cyan;
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.moveTo(mainBox.x + mainBox.w, mainBox.y + mainBox.h / 2);
  ctx.lineTo(gaugeBox.x, gaugeBox.y + gaugeBox.h / 2);
  ctx.lineTo(fiberBox.x, fiberBox.y + fiberBox.h / 2);
  ctx.stroke();
  ctx.fillStyle = COLORS.cyan;
  ctx.font = "600 17px Inter, Arial, sans-serif";
  ctx.fillText("connection / compactification", mainBox.x + mainBox.w + 26, mainBox.y + mainBox.h / 2 - 16);
  ctx.restore();

  drawTag(ctx, 120, 170, "5D KK ansatz", COLORS.accentSoft, COLORS.accent);
  drawTag(ctx, 265, 170, "4D + compact S¹", COLORS.goldSoft, COLORS.gold);
  drawTag(ctx, 450, 170, "radion φ scaling", "rgba(156, 124, 255, 0.14)", COLORS.violet);
}

export function drawDm21Timeline(canvas) {
  const ctx = getCanvasContext(canvas);
  const width = canvas.width;
  const height = canvas.height;
  paintCommon(
    ctx,
    canvas,
    "Δm²₂₁ tension timeline",
    "Residual solar-splitting tension tightened from 2.98σ to 1.16σ to 1.07σ across the Step-2, LJL, and NLO lattice milestones.",
  );

  const stages = [
    { pillar: 584, label: "Step-2 RGE consistency", sigma: DM21_TENSIONS[0], color: COLORS.orange },
    { pillar: 772, label: "Lepton Jarlskog lattice", sigma: DM21_TENSIONS[1], color: COLORS.accent },
    { pillar: 773, label: "NLO lattice correction", sigma: DM21_TENSIONS[2], color: COLORS.green },
  ];

  const left = 120;
  const right = width - 120;
  const baseY = height - 190;
  const topY = 250;
  const maxSigma = 3.2;
  const spacing = (right - left) / (stages.length - 1);

  ctx.save();
  ctx.strokeStyle = COLORS.line;
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.moveTo(left, baseY);
  ctx.lineTo(right, baseY);
  ctx.stroke();
  ctx.restore();

  ctx.save();
  ctx.strokeStyle = COLORS.gold;
  ctx.lineWidth = 5;
  ctx.beginPath();
  stages.forEach((stage, index) => {
    const x = left + spacing * index;
    const y = axisMap(stage.sigma, 0, maxSigma, baseY, topY);
    if (index === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  });
  ctx.stroke();
  ctx.restore();

  stages.forEach((stage, index) => {
    const x = left + spacing * index;
    const y = axisMap(stage.sigma, 0, maxSigma, baseY, topY);
    ctx.save();
    ctx.fillStyle = stage.color;
    ctx.strokeStyle = stage.color;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(x, y, 12, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x, baseY);
    ctx.stroke();
    drawTag(ctx, x - 84, y - 82, `Pillar ${stage.pillar}`, stage.color === COLORS.orange ? "rgba(255, 159, 67, 0.18)" : stage.color === COLORS.green ? "rgba(50, 210, 124, 0.16)" : COLORS.accentSoft, stage.color);
    ctx.fillStyle = COLORS.text;
    ctx.font = "700 28px Inter, Arial, sans-serif";
    ctx.fillText(`${stage.sigma.toFixed(2)}σ`, x - 38, y - 26);
    ctx.fillStyle = COLORS.muted;
    ctx.font = "500 17px Inter, Arial, sans-serif";
    wrapText(ctx, stage.label, x - 90, baseY + 42, 180, 22);
    ctx.restore();
  });

  drawTag(ctx, 118, 170, "2.98σ → 1.16σ → 1.07σ", COLORS.goldSoft, COLORS.gold);
  drawTag(ctx, 395, 170, "quantified residual, not erased", COLORS.accentSoft, COLORS.accent);
}

export function drawPillarDomainPieChart(canvas) {
  const ctx = getCanvasContext(canvas);
  const width = canvas.width;
  const height = canvas.height;
  paintCommon(
    ctx,
    canvas,
    "Hardgate physics domain pie chart",
    "Schematic allocation of the 208 closed-form hardgate pillars across major physics domains.",
  );

  const total = HARDGATE_DOMAIN_COUNTS.reduce((sum, item) => sum + item.value, 0);
  const centerX = 420;
  const centerY = 470;
  const radius = 210;
  let start = -Math.PI / 2;

  HARDGATE_DOMAIN_COUNTS.forEach((item) => {
    const delta = (item.value / total) * Math.PI * 2;
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.arc(centerX, centerY, radius, start, start + delta);
    ctx.closePath();
    ctx.fillStyle = item.color;
    ctx.globalAlpha = 0.92;
    ctx.fill();
    ctx.lineWidth = 3;
    ctx.strokeStyle = COLORS.bgBottom;
    ctx.stroke();
    ctx.restore();
    start += delta;
  });

  ctx.save();
  ctx.fillStyle = COLORS.card;
  ctx.beginPath();
  ctx.arc(centerX, centerY, 88, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = COLORS.text;
  ctx.font = "700 38px Inter, Arial, sans-serif";
  ctx.fillText("208", centerX - 34, centerY + 8);
  ctx.fillStyle = COLORS.muted;
  ctx.font = "500 18px Inter, Arial, sans-serif";
  ctx.fillText("core pillars", centerX - 44, centerY + 36);
  ctx.restore();

  const legendX = 760;
  let legendY = 260;
  HARDGATE_DOMAIN_COUNTS.forEach((item) => {
    ctx.save();
    ctx.fillStyle = item.color;
    roundRect(ctx, legendX, legendY - 16, 28, 28, 8);
    ctx.fill();
    ctx.fillStyle = COLORS.text;
    ctx.font = "600 20px Inter, Arial, sans-serif";
    ctx.fillText(item.label, legendX + 44, legendY + 4);
    ctx.fillStyle = COLORS.muted;
    ctx.font = "500 16px JetBrains Mono, monospace";
    ctx.fillText(`${item.value} pillars · ${((item.value / total) * 100).toFixed(1)}%`, legendX + 44, legendY + 28);
    ctx.restore();
    legendY += 62;
  });

  drawTag(ctx, 112, 170, "schematic domain grouping", COLORS.accentSoft, COLORS.accent);
}

export function drawFalsificationCalendar(canvas) {
  const ctx = getCanvasContext(canvas);
  const width = canvas.width;
  const height = canvas.height;
  paintCommon(
    ctx,
    canvas,
    "Falsification calendar",
    "Major observational checkpoints that can sharpen, route, or falsify headline UM predictions across the current public timeline.",
  );

  const left = 130;
  const right = width - 120;
  const y = height * 0.58;
  const startYear = 2026;
  const endYear = 2032;

  ctx.save();
  ctx.strokeStyle = COLORS.line;
  ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.moveTo(left, y);
  ctx.lineTo(right, y);
  ctx.stroke();
  ctx.restore();

  for (let year = startYear; year <= endYear; year += 1) {
    const x = axisMap(year, startYear, endYear, left, right);
    ctx.strokeStyle = COLORS.line;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(x, y - 14);
    ctx.lineTo(x, y + 14);
    ctx.stroke();
    ctx.fillStyle = COLORS.muted;
    ctx.font = "500 16px JetBrains Mono, monospace";
    ctx.fillText(String(year), x - 18, y + 46);
  }

  CALENDAR_EVENTS.forEach((event, index) => {
    const x = axisMap(event.year, startYear, endYear, left, right);
    const bubbleY = index % 2 === 0 ? y - 118 : y + 118;
    ctx.save();
    ctx.strokeStyle = event.color;
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x, bubbleY);
    ctx.stroke();
    ctx.fillStyle = event.color;
    ctx.beginPath();
    ctx.arc(x, y, 10, 0, Math.PI * 2);
    ctx.fill();

    const boxY = bubbleY < y ? bubbleY - 92 : bubbleY - 24;
    const boxH = 84;
    const boxW = 220;
    ctx.fillStyle = event.color === COLORS.gold ? COLORS.goldSoft : event.color === COLORS.green ? "rgba(50, 210, 124, 0.15)" : event.color === COLORS.orange ? "rgba(255, 159, 67, 0.16)" : COLORS.accentSoft;
    ctx.strokeStyle = event.color;
    roundRect(ctx, x - boxW / 2, boxY, boxW, boxH, 18);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = COLORS.text;
    ctx.font = "700 21px Inter, Arial, sans-serif";
    ctx.fillText(event.label, x - boxW / 2 + 18, boxY + 30);
    ctx.fillStyle = COLORS.muted;
    ctx.font = "500 15px Inter, Arial, sans-serif";
    wrapText(ctx, event.detail, x - boxW / 2 + 18, boxY + 56, boxW - 36, 18);
    ctx.restore();
  });

  drawTag(ctx, 112, 170, "public decision surfaces", COLORS.accentSoft, COLORS.accent);
  drawTag(ctx, 338, 170, "LiteBIRD 2032 primary β test", COLORS.goldSoft, COLORS.gold);
}

export const VISUALIZATION_RENDERERS = Object.freeze({
  cmb: drawCmbParameterPlane,
  birefringence: drawBirefringenceWindow,
  kkTower: drawKkMassTower,
  braid: drawBraidTopology,
  metric: drawMetricStructure,
  dm21: drawDm21Timeline,
  domains: drawPillarDomainPieChart,
  calendar: drawFalsificationCalendar,
});

export function renderVisualization(type, canvas, params = {}) {
  const renderer = VISUALIZATION_RENDERERS[type];
  if (!renderer) {
    throw new Error(`Unknown visualization type: ${type}`);
  }
  renderer(canvas, params);
}

export function canvasToDataUrl(canvas) {
  return canvas.toDataURL("image/png");
}

export function downloadCanvasAsPng(canvas, filename = "um-physics-visualization.png") {
  const link = document.createElement("a");
  link.href = canvasToDataUrl(canvas);
  link.download = filename;
  link.click();
}

if (typeof window !== "undefined") {
  window.UMImageGenerator = {
    UM_IMAGE_CONSTANTS,
    VISUALIZATION_METADATA,
    VISUALIZATION_RENDERERS,
    renderVisualization,
    canvasToDataUrl,
    downloadCanvasAsPng,
    drawCmbParameterPlane,
    drawBirefringenceWindow,
    drawKkMassTower,
    drawBraidTopology,
    drawMetricStructure,
    drawDm21Timeline,
    drawPillarDomainPieChart,
    drawFalsificationCalendar,
  };
}
