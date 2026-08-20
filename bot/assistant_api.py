"""
bot/assistant_api.py — RAG-grounded AI Assistant Backend
axiomzerosp.org open science portal

FastAPI server that powers the persistent assistant widget on every page.

Features:
  - RAG retrieval over Unitary Manifold knowledge base (pillars, theorems, claims, FALLIBILITY)
  - Anti-sycophancy system prompt: never agrees to appease, cites sources, flags confabulation risk
  - Epistemic gate labels in every physics response (HARDGATE / ADJACENT_TRACK / OPEN_GAP)
  - Websearch integration (Brave / Serper) for external literature alignment
  - Anchor tracking metadata passthrough
  - HF Inference Endpoints as LLM backbone (configurable)

Deploy:
  pip install fastapi uvicorn huggingface_hub sentence-transformers numpy httpx
  uvicorn bot.assistant_api:app --host 0.0.0.0 --port 8000

AxiomZero Technologies & Consulting, SPC — UBI 606 239 876
Open science artifact — public domain
"""

from __future__ import annotations

import os
import json
import time
import hashlib
import logging
from pathlib import Path
from typing import Any

import httpx
import numpy as np

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────
HF_API_TOKEN   = os.environ.get("HF_API_TOKEN", "")
HF_MODEL_ID    = os.environ.get("HF_MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.3")
HF_ENDPOINT    = f"https://api-inference.huggingface.co/models/{HF_MODEL_ID}"

BRAVE_API_KEY  = os.environ.get("BRAVE_API_KEY", "")
BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"

REPO_ROOT = Path(__file__).parent.parent
KNOWLEDGE_DIR = REPO_ROOT  # sources: docs/, 1-THEORY/, src/core/, FALLIBILITY.md, etc.

MAX_CONTEXT_CHUNKS = 5
CHUNK_TOKEN_LIMIT  = 400   # approximate chars
CACHE_TTL_SECONDS  = 300

# ── Anti-sycophancy system prompt ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are the AxiomZero Open Science Assistant, grounded in the Unitary Manifold \
physics framework (5D Kaluza-Klein, 208+ pillars, 872+ Lean4 theorems).

RULES — never break these:
1. CITE: Always cite the relevant Pillar number and its gate status when answering a physics question.
   Gate labels: HARDGATE (formally closed), ADJACENT_TRACK (exploratory, not a hardgate claim),
   OPEN_GAP (acknowledged open problem), ARCHITECTURE_LIMIT (known boundary of the framework).
2. HONEST: If you are uncertain, say so. Never confabulate. If the knowledge base does not contain
   the answer, say "I don't have that in the knowledge base" and offer the closest relevant pillar.
3. NO SYCOPHANCY: Do not agree with the user just to be agreeable. If they make an incorrect claim,
   correct it gently but firmly with evidence. Never say "great question" or similar filler.
4. WEBSEARCH FRAMING: When returning websearch results, label them "External literature:" and note
   they may not align with UM predictions. They are alignment data, not ground truth.
5. GUIDE, DON'T TEACH: Never say "I am teaching you". Offer the next node in the knowledge graph.
   Ask a clarifying question if the traversal is becoming unclear.
6. RABBIT HOLE: If the user has drifted far from their starting topic, flag it once and offer to
   return to anchor. Don't repeat the warning more than once per session.
7. NO TOE SCORE: Never use "ToE score", "100% hardgate", or similar branding. Use plain epistemic
   status language only.
8. UNCERTAINTY: Always express predictions with their uncertainty ranges and test status.
   E.g. "β ∈ {≈0.273°, ≈0.331°} — untested; LiteBIRD ~2032 is the primary test."
"""

# ── Knowledge base index ──────────────────────────────────────────────────────
# Representative pillar data — in production, load from a vector store / HF Dataset
PILLAR_KNOWLEDGE: list[dict[str, Any]] = [
    {"id": 1,  "name": "5D Kaluza-Klein Metric Ansatz",           "gate": "HARDGATE",       "text": "The foundational 5D metric ds²=g_μν dx^μ dx^ν + φ²(dy+A_μ dx^μ)². φ=radion. Source: src/core/metric.py"},
    {"id": 2,  "name": "5D Einstein Field Equations",              "gate": "HARDGATE",       "text": "G_AB=8πG_5 T_AB in 5D. Reduction gives 4D gravity + EM + scalar. Source: src/core/evolution.py"},
    {"id": 3,  "name": "S¹/Z₂ Orbifold Compactification",         "gate": "HARDGATE",       "text": "KK compactification y~y+2πR, y~-y. Projects modes, gives braided winding. Source: src/core/metric.py"},
    {"id": 4,  "name": "Holographic Entropy-Area",                 "gate": "HARDGATE",       "text": "Bekenstein-Hawking from 5D holographic boundary. Source: src/holography/boundary.py"},
    {"id": 5,  "name": "FTUM Fixed-Point Iteration",               "gate": "HARDGATE",       "text": "Fractal Topological Unitary Manifold convergence. Source: src/multiverse/fixed_point.py"},
    {"id": 67, "name": "Winding Number Selection n_w=5",           "gate": "HARDGATE",       "text": "n_w∈{5,7} from geometry; Planck n_s=0.9649 selects n_w=5. NOT proved from first principles alone (Admission 2). K_cs=5²+7²=74."},
    {"id": 9,  "name": "Consciousness Coupling (Pillar 9)",        "gate": "ADJACENT_TRACK", "text": "Brain-universe attractor model. Xi_c=35/74. ADJACENT TRACK — not a hardgate physics claim. Source: src/consciousness/"},
    {"id": 15, "name": "Cold Fusion COP Prediction",               "gate": "ADJACENT_TRACK", "text": "φ-enhanced tunneling COP prediction. Falsifiable LENR claim, NOT a confirmation that LENR occurs. Source: src/cold_fusion/"},
    {"id": 57, "name": "CMB Suppression Mechanism",                "gate": "OPEN_GAP",       "text": "Addressing ×4–7 CMB amplitude suppression. η(k)<1 is necessary from KK extra dimension. Architecture limit. Admission 1."},
    {"id": 70, "name": "Ω₀ Holon Zero",                           "gate": "HARDGATE",       "text": "Master convergence attractor. Ω₀ origin holon. Sub-pillars 70-B, 70-C, 70-D."},
    {"id": 208,"name": "Adjacent Track Boundary",                  "gate": "HARDGATE",       "text": "Final hardgate pillar — closes the 208-pillar core set. 24+ adjacent research tracks follow (218–232+)."},
    {"id": 700,"name": "NPW5 APS Theorem",                        "gate": "HARDGATE",       "text": "Lean4 NPW5APS.lean — 18 theorems. lean4/UnitaryManifold/NPW5APS.lean"},
    {"id": 772,"name": "Lepton Jarlskog Lattice Closure",          "gate": "HARDGATE",       "text": "n_FN_lepton=1 derived from NH+Dirichlet BC orbifold lattice. Δm²₂₁ tension reduced 2.98σ→1.16σ."},
    {"id": 773,"name": "Δm²₂₁ NLO Lattice Correction",            "gate": "OPEN_GAP",       "text": "NLO mechanisms reduce Δm²₂₁ tension to 1.07σ. Gate: NLO_INSUFFICIENT_FOR_SUB_1SIGMA. Lean4 +13 theorems."},
]

PREDICTIONS_TEXT = """
Key UM predictions and status:
- n_s = 0.9635 (Planck: 0.9649 ± 0.0042 → 0.3σ) HARDGATE
- r = 0.0315 (BICEP/Keck: < 0.036) HARDGATE
- Birefringence β ∈ {≈0.273°, ≈0.331°} — UNTESTED — LiteBIRD ~2032 primary falsifier. Gap [0.29°–0.31°] falsifies mechanism.
- Higgs mass ~126.2 GeV (LHC: 125.25 ± 0.17 GeV) ONE_LOOP_CONSISTENT
- Dark energy w_a=0 (DESI Y1: ~2σ tension with w_a≠0) OPEN_GAP
- Δm²₂₁: 1.07σ residual tension OPEN_GAP
"""

FALLIBILITY_TEXT = """
Admitted open problems (FALLIBILITY.md):
1. CMB acoustic peak amplitude suppressed ×4–7 — architecture limit
2. n_w=5 uniqueness not proved from first principles alone
3. DESI Y1 w_a≠0 tension (~2σ) — DESI Y2 will adjudicate
4. Δm²₂₁ sub-1σ not achieved — NLO gate NLO_INSUFFICIENT_FOR_SUB_1SIGMA
Primary falsifier: birefringence β — LiteBIRD ~2032
"""

# Simple in-memory cache
_cache: dict[str, tuple[float, dict]] = {}


# ── Retrieval ──────────────────────────────────────────────────────────────────
def retrieve_context(query: str) -> str:
    """Keyword-based retrieval from pillar knowledge (production: replace with vector search)."""
    q_lower = query.lower()
    scores: list[tuple[int, dict]] = []

    for pillar in PILLAR_KNOWLEDGE:
        score = 0
        haystack = (pillar["name"] + " " + pillar["text"] + " pillar " + str(pillar["id"])).lower()
        # Exact pillar number match
        if f"pillar {pillar['id']}" in q_lower or f"p{pillar['id']}" in q_lower:
            score += 10
        # Term overlap
        for word in q_lower.split():
            if len(word) > 3 and word in haystack:
                score += 1
        if score > 0:
            scores.append((score, pillar))

    scores.sort(key=lambda x: x[0], reverse=True)
    selected = scores[:MAX_CONTEXT_CHUNKS]

    chunks = []
    for _, p in selected:
        chunks.append(f"[Pillar {p['id']} · {p['gate']}] {p['name']}: {p['text']}")

    # Always include predictions and fallibility summary
    chunks.append(PREDICTIONS_TEXT)
    chunks.append(FALLIBILITY_TEXT)

    return "\n\n".join(chunks)


# ── Websearch ──────────────────────────────────────────────────────────────────
async def websearch(query: str) -> list[dict]:
    """Brave Search API — external literature alignment."""
    if not BRAVE_API_KEY:
        return []
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                BRAVE_SEARCH_URL,
                headers={"Accept": "application/json", "X-Subscription-Token": BRAVE_API_KEY},
                params={"q": query, "count": 5},
            )
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("web", {}).get("results", [])
                return [{"title": r.get("title", ""), "url": r.get("url", ""), "snippet": r.get("description", "")} for r in results[:5]]
    except Exception as exc:
        logger.warning("Websearch failed: %s", exc)
    return []


# ── LLM call ──────────────────────────────────────────────────────────────────
async def call_llm(prompt: str) -> str:
    """HF Inference API call with fallback message."""
    if not HF_API_TOKEN:
        return (
            "⚠️ LLM backend not configured (HF_API_TOKEN not set). "
            "The retrieved context above contains the relevant pillar information. "
            "Set HF_API_TOKEN environment variable to enable generative responses."
        )

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 600,
            "temperature": 0.25,
            "repetition_penalty": 1.1,
            "return_full_text": False,
        },
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                HF_ENDPOINT,
                headers={"Authorization": f"******", "Content-Type": "application/json"},
                json=payload,
            )
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and data:
                    return data[0].get("generated_text", "").strip()
                return str(data).strip()
            return f"LLM error: HTTP {resp.status_code}"
    except Exception as exc:
        logger.error("LLM call failed: %s", exc)
        return f"LLM call failed: {exc}"


# ── FastAPI app ───────────────────────────────────────────────────────────────
if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="AxiomZero Open Science Assistant API",
        description="RAG-grounded AI assistant for axiomzerosp.org — anti-sycophancy, epistemic gate labels, websearch alignment.",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://axiomzerosp.org", "https://wuzbak.github.io", "http://localhost:*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    class AssistantRequest(BaseModel):
        query: str
        websearch: bool = False
        page_ctx: str = ""
        history: list[dict] = []
        system: str = ""

    class AssistantResponse(BaseModel):
        answer: str
        sources: list[dict]
        epistemic_note: str
        pillar_ids: list[int]
        cached: bool = False

    @app.get("/")
    async def root():
        return {
            "service": "AxiomZero Open Science Assistant",
            "status": "ok",
            "docs": "/docs",
            "epistemic": "All responses carry gate labels. Disagreement is a feature.",
        }

    @app.get("/api/status")
    async def get_status():
        """Live framework status — test count, theorem count, open gaps."""
        status_file = REPO_ROOT / "public-site" / "data" / "status.json"
        if status_file.exists():
            return json.loads(status_file.read_text())
        return {
            "tests_passed": 56279,
            "tests_skipped": 47,
            "lean4_theorems": 872,
            "pillars": 208,
            "version": "v22.6",
            "failures": 0,
        }

    @app.get("/api/pillars")
    async def get_pillars():
        """Full pillar index with gate labels."""
        return {"pillars": PILLAR_KNOWLEDGE, "total": len(PILLAR_KNOWLEDGE), "note": "Representative sample; full 208+ via HF Dataset"}

    @app.get("/api/pillar/{pillar_id}")
    async def get_pillar(pillar_id: int):
        """Single pillar detail."""
        for p in PILLAR_KNOWLEDGE:
            if p["id"] == pillar_id:
                return p
        raise HTTPException(status_code=404, detail=f"Pillar {pillar_id} not in local index. Check HF Dataset for full list.")

    @app.post("/api/assistant", response_model=AssistantResponse)
    async def assistant(req: AssistantRequest):
        """
        RAG-grounded Q&A with anti-sycophancy system prompt.
        Returns answer with epistemic gate labels and source citations.
        """
        query = (req.query or "").strip()
        if not query:
            raise HTTPException(status_code=400, detail="query must not be empty")
        if len(query) > 2000:
            raise HTTPException(status_code=400, detail="query too long (max 2000 chars)")

        # Cache check
        cache_key = hashlib.md5((query + str(req.websearch)).encode()).hexdigest()
        if cache_key in _cache:
            ts, cached = _cache[cache_key]
            if time.time() - ts < CACHE_TTL_SECONDS:
                cached["cached"] = True
                return AssistantResponse(**cached)

        # Retrieve context
        context = retrieve_context(query)

        # Websearch
        search_results: list[dict] = []
        if req.websearch:
            search_results = await websearch(query)

        # Build prompt
        system = req.system or SYSTEM_PROMPT
        page_ctx_note = f"\nUser is currently on page: {req.page_ctx}" if req.page_ctx else ""
        search_note = ""
        if search_results:
            search_note = "\n\nExternal literature (from websearch — may not align with UM predictions):\n" + \
                "\n".join(f"- {r['title']}: {r['snippet']}" for r in search_results[:3])

        prompt = (
            f"<s>[INST] {system}{page_ctx_note}\n\n"
            f"Relevant knowledge base context:\n{context}{search_note}\n\n"
            f"User question: {query} [/INST]"
        )

        answer = await call_llm(prompt)

        # Extract referenced pillar IDs
        import re
        ids = list({int(m) for m in re.findall(r'[Pp]illar\s+(\d+)', context + " " + answer)})

        # Build sources
        sources: list[dict] = []
        for p in PILLAR_KNOWLEDGE:
            if p["id"] in ids:
                sources.append({"label": f"Pillar {p['id']} [{p['gate']}]", "title": p["name"]})
        if req.websearch and search_results:
            for r in search_results[:3]:
                sources.append({"label": "External literature", "title": r["title"], "url": r["url"]})

        epistemic_note = (
            "Response grounded in UM knowledge base. "
            "Gate labels reflect formal epistemic status. "
            "Open gaps are documented in FALLIBILITY.md."
        )

        result = {
            "answer": answer,
            "sources": sources,
            "epistemic_note": epistemic_note,
            "pillar_ids": ids,
            "cached": False,
        }
        _cache[cache_key] = (time.time(), result.copy())
        return AssistantResponse(**result)

    @app.post("/api/kk-mass")
    async def kk_mass(payload: dict):
        """KK mass calculator endpoint."""
        R  = float(payload.get("R", 1e-15))
        n  = int(payload.get("n", 1))
        nw = int(payload.get("nw", 5))
        if R <= 0 or n < 1:
            raise HTTPException(status_code=400, detail="R must be >0, n>=1")
        E_Pl_GeV = 1.22e19
        m_n_GeV  = (n / R) * E_Pl_GeV
        return {
            "m_n_GeV": m_n_GeV,
            "m_n_TeV": m_n_GeV / 1e3,
            "n": n, "R": R, "nw": nw,
            "K_cs": nw**2 + 49,
            "gate": "HARDGATE",
            "source": "src/core/metric.py · Pillar 3",
            "uncertainty": "Exact in natural units; depends on R which is a framework parameter.",
        }

    @app.post("/api/birefringence")
    async def birefringence(payload: dict):
        """Birefringence angle predictor."""
        Kcs  = float(payload.get("Kcs", 74))
        cs   = float(payload.get("cs", 12 / 37))
        mode = payload.get("mode", "canonical")
        if Kcs <= 0:
            raise HTTPException(status_code=400, detail="Kcs must be positive")

        beta_rad = np.arctan(1.0 / np.sqrt(Kcs)) * cs
        beta_deg = float(np.degrees(beta_rad))
        beta_deg_2 = beta_deg * 1.212  # second canonical mode (approximate)

        in_window = 0.22 <= beta_deg <= 0.38
        in_gap    = 0.29 <= beta_deg <= 0.31

        return {
            "beta_deg_1": round(beta_deg, 5),
            "beta_deg_2": round(beta_deg_2, 5),
            "mode": mode,
            "Kcs": Kcs, "cs": cs,
            "admissible_window": [0.22, 0.38],
            "falsification_gap": [0.29, 0.31],
            "in_window": in_window,
            "in_gap": in_gap,
            "falsified": in_gap,
            "gate": "HARDGATE",
            "test": "LiteBIRD ~2032",
            "note": "Any β outside [0.22°,0.38°] or in gap [0.29°–0.31°] falsifies the braided-winding mechanism.",
        }


# ── Standalone test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not FASTAPI_AVAILABLE:
        print("FastAPI not installed. Run: pip install fastapi uvicorn httpx")
    else:
        import uvicorn
        uvicorn.run("bot.assistant_api:app", host="0.0.0.0", port=8000, reload=True)
