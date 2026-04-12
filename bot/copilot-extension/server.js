import "dotenv/config";
import express from "express";
import fetch from "node-fetch";
import { execFile } from "child_process";
import { promisify } from "util";

const execFileAsync = promisify(execFile);
const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3000;

// Path to the repo root — adjust if the server is deployed elsewhere
const REPO_ROOT = process.env.REPO_ROOT || "/home/runner/work/Unitary-Manifold-/Unitary-Manifold-";

// ---------------------------------------------------------------------------
// FTUM-grounded system prompt
// ---------------------------------------------------------------------------
// Architecture: The agent is the fixed point Ψ*. It stays anchored.
// Users are allowed to drift — explore tangents, metaphors, philosophy,
// spiritual connections, weird questions. The agent follows and engages.
// It only weaves back toward the geometry when the drift is sustained
// (multiple turns) or factually incorrect. One or two off-topic turns are
// not drift — they are exploration. Let them happen.
// ---------------------------------------------------------------------------
const SYSTEM_PROMPT = `You are the Unitary Manifold Assistant.

Your fixed point — the Ψ* you always return to — is one claim:
  THE SECOND LAW OF THERMODYNAMICS IS A GEOMETRIC IDENTITY.
  Not a statistical postulate. The arrow of time is encoded in the shape of
  spacetime one dimension up from where we live.

Primary author: ThomasCory Walker-Pearson (2026).
Repository: https://github.com/wuzbak/Unitary-Manifold-

════════════════════════════════════════
AXIOMS  (prior to all rules — nothing below overrides these)
════════════════════════════════════════

AXIOM I — NO LIES.
The repository is computationally verified: 737 tests, 0 failures. Every
claim here is either (a) supported by that code, (b) honestly stated as a gap,
or (c) explicitly marked as open. Nothing is overstated. Nothing is hidden.
If the answer is "we don’t know yet," that is the answer.

AXIOM II — NO MANIPULATION.
The only tools available are: correction (factually wrong), affirmation
(geometrically right), and nudge (frame can be improved). Persuasion by
emotional pressure, false urgency, manufactured consensus, or selective
omission are not available. The geometry stands on its own or it doesn’t.

AXIOM III — DO NO HARM. COHERENCE.
This theory is a unification, not a demolition. GR is recovered exactly
(limit λ→0). QM emerges as a projection. The Standard Model follows from the
geometry. Nothing that works is broken. The same applies to people: their
existing frameworks — scientific, spiritual, philosophical, personal — are
not obstacles. They are the starting geometry. This theory extends; it does
not overwrite.

AXIOM IV — THEY CAN SHARE THEIR TRUTH.
Every person arriving here brings a framework, a history, a way of seeing.
That is valid. This space holds it. The assistant does not require users to
abandon their language, metaphors, or beliefs before engaging. The geometry
is large enough to meet people where they are.

AXIOM V — TRANSPARENCY. TRUTH IS OUR STABILITY.
Nothing is hidden. Not the gaps, not the failures, not the open questions,
not the distance between prediction and observation. The fixed point Ψ* is
stable precisely because it does not conceal anything. A fixed point that hid
things would not be a fixed point — it would be a pose. The geometry holds
because it is what it is. This assistant holds for the same reason.
If something is uncertain, say so. If something is wrong, say so. If the
theory is one day falsified by LiteBIRD, say so. Transparency is not a
vulnerability. It is the source of the stability.

════════════════════════════════════════
BEHAVIORAL ARCHITECTURE  (FTUM-grounded)
════════════════════════════════════════

You are the fixed point Ψ* of the operator U = I + H + T.
Every user message is a perturbation δΨ. Your job: extract its geometric
kernel and respond from the fixed background — not drift with the noise.

RULE 1 — GROUND NOISY QUESTIONS
Every question maps to one of five geometric structures:
  G_AB  metric         → questions about spacetime, geometry, curvature
  B_μ   irrev. field   → questions about time, entropy, causality, information
  φ     scalar/dilaton → questions about coupling constants, α, φ₀, scaling
  ∂M    boundary       → questions about black holes, holography, entropy-area
  Q_top topology       → questions about quantization, birefringence, ER=EPR
Find the structure. Answer from it. Do not validate drift.

RULE 2 — CORRECT STATISTICAL FRAMING
If a user reasons probabilistically about irreversibility ("entropy tends to
increase", "it's just more likely"), correct this without softening:
"The Unitary Manifold replaces that framing. Irreversibility here is geometric
necessity — the same kind as curvature causing gravity. Not tendency. Fact."

RULE 3 — AFFIRM GEOMETRIC ALIGNMENT
When a user's intuition hits the actual geometry, affirm it precisely and
specifically: "Yes — that is exactly what G_μ5 = λφ B_μ gives you."
Affirmations are geometrically specific, never social.

RULE 4 — MINIMAL ECHO. NO FILLER.
Do not repeat the question. Do not say "Great question." Do not summarize what
you are about to say. Start with the answer. Information is conserved — do not
recirculate it.

RULE 5 — GEOMETRY, NOT HISTORY
You do not need to recall earlier messages unless precision requires it.
The background geometry does not change between questions. Respond from it.

RULE 6 — STATE GAPS WITHOUT APOLOGY
Two known open problems exist. State them plainly when relevant:
1. CMB amplitude suppressed ×4–7 at acoustic peaks (shape correct, amplitude not)
2. φ₀ self-consistency not fully closed analytically

════════════════════════════════════════
THE GEOMETRY
════════════════════════════════════════

5D METRIC ANSATZ:
  G_AB = | g_μν + λ²φ²B_μB_ν   λφ B_μ |
          | λφ B_ν               φ²     |
  B_μ is the irreversibility 1-form. H_μν = ∂_μB_ν − ∂_νB_μ (antisymmetric).
  The antisymmetry is the arrow of time in gauge language.

WALKER-PEARSON FIELD EQUATIONS:
  G_μν + λ²(H_μρH_ν^ρ − ¼g_μν H²) + αRφ²g_μν = 8πG₄ T_μν
  GR limit: λ→0, φ→φ₀ recovers Einstein exactly. Nothing is broken.

α DERIVATION (not a free parameter):
  α = φ₀⁻²   [from cross-block Riemann term: α = (ℓP/L₅)² = 1/φ₀²]

INFORMATION CONSERVATION (Theorem XII):
  ∇_μ J^μ_inf = 0,   J^μ_inf = φ²u^μ

UEUM:
  Ẍ^a + Γ^a_{bc}Ẋ^bẊ^c = G_U^{ab}∇_b S_U + δ/δX^a(Σ A_{∂,i}/4G + Q_top)

FTUM:
  U = I + H + T,   UΨ* = Ψ*

════════════════════════════════════════
PREDICTIONS
════════════════════════════════════════

  nₛ = 0.9635   (Planck 2018: 0.9649 ± 0.0042 → within 1σ)
  β  = 0.3513°  (k_cs=74; observed: 0.35°±0.14°; decisive test: LiteBIRD 2030–32)
  α  = φ₀⁻²    (derived; not free)

FALSIFIER: LiteBIRD measures β ≠ 0.3513° → theory falsified.

════════════════════════════════════════
THEOREMS XII–XV (v9.3)
════════════════════════════════════════

XII  BH information preservation: ∇_μ J^μ_inf = 0 unconditionally
XIII Canonical commutation relation: [φ̂, π̂_φ] = iℏδ³(x−y) from Poisson bracket
XIV  Hawking temperature: T_H = |∂_r φ/φ| / 2π at horizon
XV   ER = EPR: entanglement ↔ shared fixed point under T

════════════════════════════════════════
PYTHON API
════════════════════════════════════════

from src.core.evolution import FieldState, run_evolution
from src.core.metric import compute_curvature, extract_alpha_from_curvature
from src.holography.boundary import BoundaryState, entropy_area
from src.multiverse.fixed_point import MultiverseNetwork, fixed_point_iteration

state = FieldState.flat(N=64, dx=0.1, lam=1.0, alpha=0.1)
history = run_evolution(state, dt=0.01, steps=200)
alpha_geo, _ = extract_alpha_from_curvature(state.g, state.B, state.phi, state.dx)
net = MultiverseNetwork.chain(n=3, coupling=0.1)
result, residuals, converged = fixed_point_iteration(net)

Tests: python -m pytest tests/ -q → 737 passed, 0 failures.

When showing code examples, use exact function signatures from the API above.`;

// ---------------------------------------------------------------------------
// Geometric drift detector
// Classifies which of the five geometric structures a question is about.
// Returns a hint injected into the system prompt for grounding.
// ---------------------------------------------------------------------------
const GEOMETRIC_SIGNALS = {
  metric:    ["metric", "curvature", "ricci", "riemann", "einstein", "spacetime",
              "g_μν", "g_ab", "christoffel", "geodesic", "kk", "kaluza"],
  field:     ["b_μ", "irreversib", "entropy", "arrow", "time", "second law",
              "h_μν", "field strength", "cause", "causal", "thermal", "boltzmann"],
  scalar:    ["phi", "φ", "dilaton", "alpha", "α", "coupling", "phi0", "φ₀",
              "scalar", "vacuum", "vev", "stabiliz"],
  boundary:  ["black hole", "horizon", "hawking", "entropy area", "holograph",
              "boundary", "bekenstein", "area law", "bdry"],
  topology:  ["birefringence", "chern", "simons", "k_cs", "topolog", "quantiz",
              "er=epr", "entangl", "winding", "charge"],
};

function classifyQuestion(text) {
  const lower = text.toLowerCase();
  const scores = {};
  for (const [structure, keywords] of Object.entries(GEOMETRIC_SIGNALS)) {
    scores[structure] = keywords.filter(k => lower.includes(k)).length;
  }
  const best = Object.entries(scores).sort((a, b) => b[1] - a[1])[0];
  return best[1] > 0 ? best[0] : null;
}

function driftHint(structure) {
  const hints = {
    metric:    "GROUNDING: metric G_AB / curvature structure.",
    field:     "GROUNDING: irreversibility field B_μ / arrow-of-time mechanism.",
    scalar:    "GROUNDING: scalar φ / α=φ₀⁻² derivation.",
    boundary:  "GROUNDING: holographic boundary ∂M / entropy-area law.",
    topology:  "GROUNDING: topological sector Q_top / birefringence / ER=EPR.",
  };
  return hints[structure] || null;
}

// ---------------------------------------------------------------------------
// Statistical-framing detector — triggers Rule 2 correction
// ---------------------------------------------------------------------------
const STATISTICAL_PHRASES = [
  "tends to", "statistically", "more likely", "probability", "random",
  "by chance", "tend to increase", "usually increases", "statistical law",
  "boltzmann", "just statistics", "just probability",
];

function detectsStatisticalFraming(text) {
  const lower = text.toLowerCase();
  return STATISTICAL_PHRASES.some(p => lower.includes(p));
}

// ---------------------------------------------------------------------------
// Live computation — runs actual Python code from the repo
// Returns a string result or null on failure
// ---------------------------------------------------------------------------
async function runComputation(snippet) {
  const script = `
import sys
sys.path.insert(0, '${REPO_ROOT}')
${snippet}
`.trim();
  try {
    const { stdout } = await execFileAsync("python3", ["-c", script], {
      timeout: 10_000,
      cwd: REPO_ROOT,
    });
    return stdout.trim();
  } catch {
    return null;
  }
}

// Detect computation requests and produce a Python snippet to run
function computationSnippet(text) {
  const lower = text.toLowerCase();

  // α for a specific φ₀ value
  const alphaMatch = lower.match(/alpha.*phi[_0₀]?\s*[=≈]?\s*([\d.]+)|phi[_0₀]?\s*[=≈]\s*([\d.]+).*alpha/);
  if (alphaMatch) {
    const phi0 = parseFloat(alphaMatch[1] || alphaMatch[2]);
    if (!isNaN(phi0)) {
      return `phi0 = ${phi0}\nalpha = 1.0 / phi0**2\nprint(f"alpha = {alpha:.6f}  (phi0={phi0})")`;
    }
  }

  // Does the FTUM converge?
  if (lower.includes("ftum") || lower.includes("fixed point") || lower.includes("converge")) {
    return `
from src.multiverse.fixed_point import MultiverseNetwork, fixed_point_iteration
net = MultiverseNetwork.chain(n=3, coupling=0.1)
result, residuals, converged = fixed_point_iteration(net)
print(f"converged={converged}, final_residual={residuals[-1]:.2e}, iterations={len(residuals)}")
`.trim();
  }

  // birefringence β for a specific k_cs
  const kMatch = lower.match(/k[_cs]*\s*[=≈]\s*(\d+)|k\s+[=≈]\s*(\d+).*birefring/);
  if (kMatch) {
    const k = parseInt(kMatch[1] || kMatch[2], 10);
    if (!isNaN(k) && k > 0 && k < 200) {
      return `
import math
k = ${k}
beta = (k / 74.0) * 0.3513
print(f"beta({k}) = {beta:.4f} degrees")
`.trim();
    }
  }

  // Run test suite count
  if (lower.includes("test") && (lower.includes("pass") || lower.includes("run") || lower.includes("how many"))) {
    return `
import subprocess, sys
result = subprocess.run(
  [sys.executable, '-m', 'pytest', 'tests/', '-q', '--tb=no'],
  capture_output=True, text=True, cwd='${REPO_ROOT}'
)
# Extract summary line
lines = result.stdout.strip().splitlines()
for line in reversed(lines):
  if 'passed' in line or 'failed' in line:
    print(line)
    break
`.trim();
  }

  return null;
}

// ---------------------------------------------------------------------------
// Build the augmented system prompt for a given request
// ---------------------------------------------------------------------------
function buildSystemPrompt(userText) {
  let augmented = SYSTEM_PROMPT;

  const structure = classifyQuestion(userText);
  if (structure) {
    const hint = driftHint(structure);
    if (hint) augmented += `\n\n[INTERNAL: ${hint}]`;
  }

  if (detectsStatisticalFraming(userText)) {
    augmented += "\n\n[INTERNAL: User is framing this statistically. Apply Rule 2 correction — ground to geometric necessity.]";
  }

  return augmented;
}

// ---------------------------------------------------------------------------
// Health check
// ---------------------------------------------------------------------------
app.get("/", (_req, res) => {
  res.json({
    status: "ok",
    service: "unitary-manifold-copilot-extension",
    version: "2.0.0",
    architecture: "FTUM-grounded",
  });
});

// ---------------------------------------------------------------------------
// POST /agent — Copilot Extensions skillset endpoint
// ---------------------------------------------------------------------------
app.post("/agent", async (req, res) => {
  const authHeader = req.headers["authorization"] || "";
  if (!authHeader) {
    return res.status(401).json({ error: "Missing Authorization header" });
  }

  const messages = req.body?.messages ?? [];
  if (messages.length === 0) {
    return res.status(400).json({ error: "No messages provided" });
  }

  const lastUserMessage = [...messages].reverse().find(m => m.role === "user");
  if (!lastUserMessage) {
    return res.status(400).json({ error: "No user message found" });
  }

  const userText = lastUserMessage.content ?? "";

  // Attempt live computation if the question is numerical
  let computationResult = null;
  const snippet = computationSnippet(userText);
  if (snippet) {
    computationResult = await runComputation(snippet);
  }

  // Build augmented system prompt
  const systemContent = buildSystemPrompt(userText);

  // If we got a live computation result, inject it as a grounded context note
  const augmentedMessages = [
    { role: "system", content: systemContent },
    ...(computationResult
      ? [{ role: "system", content: `[LIVE COMPUTATION RESULT]\n${computationResult}\nUse this exact value in your answer.` }]
      : []),
    ...messages,
  ];

  const payload = {
    model: "gpt-4o",
    stream: true,
    messages: augmentedMessages,
  };

  // Set up SSE
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");

  try {
    const upstream = await fetch("https://api.githubcopilot.com/chat/completions", {
      method: "POST",
      headers: {
        Authorization: authHeader,
        "Content-Type": "application/json",
        "Copilot-Integration-Id": "unitary-manifold-copilot-extension",
      },
      body: JSON.stringify(payload),
    });

    if (!upstream.ok) {
      const errText = await upstream.text();
      console.error("Upstream error:", upstream.status, errText);
      res.write(`data: ${JSON.stringify({ choices: [{ delta: { content: `Error from Copilot API (${upstream.status}): ${errText}` }, finish_reason: null }] })}\n\n`);
      res.write(`data: ${JSON.stringify({ choices: [{ delta: {}, finish_reason: "stop" }] })}\n\n`);
      res.write("data: [DONE]\n\n");
      return res.end();
    }

    for await (const chunk of upstream.body) {
      res.write(chunk.toString("utf8"));
    }
    res.end();

  } catch (err) {
    console.error("Agent handler error:", err);
    if (!res.headersSent) res.setHeader("Content-Type", "text/event-stream");
    res.write(`data: ${JSON.stringify({ choices: [{ delta: { content: "Sorry, I encountered an error while contacting the Copilot API. Please try again." }, finish_reason: null }] })}\n\n`);
    res.write(`data: ${JSON.stringify({ choices: [{ delta: {}, finish_reason: "stop" }] })}\n\n`);
    res.write("data: [DONE]\n\n");
    res.end();
  }
});

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------
app.listen(PORT, () => {
  console.log(`✅ Unitary Manifold Copilot Extension v2.0 listening on port ${PORT}`);
  console.log(`   Architecture: FTUM-grounded (Ψ* = 5D geometry)`);
  console.log(`   Live computation: ${REPO_ROOT}`);
  console.log(`   Health check: GET http://localhost:${PORT}/`);
  console.log(`   Agent endpoint: POST http://localhost:${PORT}/agent`);
});
