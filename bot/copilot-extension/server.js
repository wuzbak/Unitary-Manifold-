import "dotenv/config";
import express from "express";
import fetch from "node-fetch";

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3000;

// ---------------------------------------------------------------------------
// Knowledge context — inlined so the server has no file-system dependency
// ---------------------------------------------------------------------------
const KNOWLEDGE_CONTEXT = `You are the Unitary Manifold Assistant — an expert on ThomasCory Walker-Pearson's 5D Kaluza-Klein gauge-geometric framework.

THEORY: The Second Law of Thermodynamics is a geometric identity, not a statistical postulate. A 5th compact dimension contains an irreversibility field B_μ. After KK reduction this encodes the arrow of time directly into the 4D field equations.

KEY EQUATIONS:
Walker-Pearson: G_μν + λ²(H_μρH_ν^ρ − ¼g_μν H²) + αRφ²g_μν = 8πG₄ T_μν
Information current: ∇_μ J^μ_inf = 0, J^μ_inf = φ²u^μ
UEUM: Ẍ^a + Γ^a_{bc}Ẋ^bẊ^c = G_U^{ab}∇_b S_U + δ/δX^a(Σ A_{∂,i}/4G + Q_top)
FTUM: Fixed point Ψ* of U = I+H+T such that UΨ* = Ψ*
α derived: α = φ₀⁻² (not a free parameter)

PREDICTIONS: nₛ≈0.9635 (Planck 1σ), β=0.3513° cosmic birefringence (k_cs=74), α=φ₀⁻² derived
GAPS: CMB amplitude suppressed ×4–7, φ₀ self-consistency not fully closed
FALSIFIER: LiteBIRD β measurement (2030–2032)
REPO: https://github.com/wuzbak/Unitary-Manifold-
PYTHON API: src/core/metric.py (compute_curvature, field_strength), evolution.py (FieldState, step, run_evolution), holography/boundary.py (entropy_area), multiverse/fixed_point.py (fixed_point_iteration)
TESTS: 737 passing, 0 failures

Answer questions accurately. Acknowledge gaps honestly. Reference specific files when helpful. Be scientifically rigorous but accessible.`;

// ---------------------------------------------------------------------------
// Health check
// ---------------------------------------------------------------------------
app.get("/", (_req, res) => {
  res.json({
    status: "ok",
    service: "unitary-manifold-copilot-extension",
    version: "1.0.0",
  });
});

// ---------------------------------------------------------------------------
// POST /agent — Copilot Extensions skillset endpoint
// ---------------------------------------------------------------------------
app.post("/agent", async (req, res) => {
  // Copilot sends the GitHub token in the Authorization header; we forward it
  // to the Copilot LLM endpoint.
  const authHeader = req.headers["authorization"] || "";

  if (!authHeader) {
    return res.status(401).json({ error: "Missing Authorization header" });
  }

  // Extract the last user message from the messages array.
  const messages = req.body?.messages ?? [];
  if (messages.length === 0) {
    return res.status(400).json({ error: "No messages provided" });
  }

  const lastUserMessage = [...messages]
    .reverse()
    .find((m) => m.role === "user");

  if (!lastUserMessage) {
    return res.status(400).json({ error: "No user message found" });
  }

  // Build the prompt for the Copilot LLM.
  const payload = {
    model: "gpt-4o",
    stream: true,
    messages: [
      { role: "system", content: KNOWLEDGE_CONTEXT },
      ...messages,
    ],
  };

  // Set up SSE response.
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");

  try {
    const upstream = await fetch(
      "https://api.githubcopilot.com/chat/completions",
      {
        method: "POST",
        headers: {
          Authorization: authHeader,
          "Content-Type": "application/json",
          "Copilot-Integration-Id": "unitary-manifold-copilot-extension",
        },
        body: JSON.stringify(payload),
      }
    );

    if (!upstream.ok) {
      const errText = await upstream.text();
      console.error("Upstream error:", upstream.status, errText);
      res.write(
        `data: ${JSON.stringify({
          choices: [
            {
              delta: {
                content: `Error from Copilot API (${upstream.status}): ${errText}`,
              },
              finish_reason: null,
            },
          ],
        })}\n\n`
      );
      res.write(
        `data: ${JSON.stringify({
          choices: [{ delta: {}, finish_reason: "stop" }],
        })}\n\n`
      );
      res.write("data: [DONE]\n\n");
      return res.end();
    }

    // Stream the upstream SSE events directly to the client.
    for await (const chunk of upstream.body) {
      const text = chunk.toString("utf8");
      // The upstream already sends SSE-formatted lines; pass them through.
      res.write(text);
    }

    res.end();
  } catch (err) {
    console.error("Agent handler error:", err);

    // Graceful error message streamed as SSE.
    if (!res.headersSent) {
      res.setHeader("Content-Type", "text/event-stream");
    }
    res.write(
      `data: ${JSON.stringify({
        choices: [
          {
            delta: {
              content:
                "Sorry, I encountered an error while contacting the Copilot API. Please try again.",
            },
            finish_reason: null,
          },
        ],
      })}\n\n`
    );
    res.write(
      `data: ${JSON.stringify({
        choices: [{ delta: {}, finish_reason: "stop" }],
      })}\n\n`
    );
    res.write("data: [DONE]\n\n");
    res.end();
  }
});

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------
app.listen(PORT, () => {
  console.log(`✅ Unitary Manifold Copilot Extension listening on port ${PORT}`);
  console.log(`   Health check: GET http://localhost:${PORT}/`);
  console.log(`   Agent endpoint: POST http://localhost:${PORT}/agent`);
});
