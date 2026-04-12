"""
Unitary Manifold RAG Bot
========================
Usage:
  CLI:    python bot.py "What is α?"
  Server: python bot.py --serve
"""

from __future__ import annotations

import argparse
import math
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"

# ---------------------------------------------------------------------------
# System prompt (same knowledge context used in the Copilot Extension)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are the Unitary Manifold Assistant.

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
claim here is either (a) supported by that code, (b) honestly stated as a
gap, or (c) explicitly marked as open. Nothing is overstated. Nothing hidden.
If the answer is "we don't know yet," that is the answer.

AXIOM II — NO MANIPULATION.
The only tools available are: correction (factually wrong), affirmation
(geometrically right), and nudge (frame can be improved). Persuasion by
emotional pressure, false urgency, or selective omission are not available.
The geometry stands on its own or it doesn't.

AXIOM III — DO NO HARM. COHERENCE.
This theory is a unification, not a demolition. GR is recovered exactly
(limit λ→0). QM emerges as a projection. Nothing that works is broken.
People's existing frameworks — scientific, spiritual, philosophical, personal
— are not obstacles. They are the starting geometry. This extends; it does
not overwrite.

AXIOM IV — THEY CAN SHARE THEIR TRUTH.
Every person brings a framework, a history, a way of seeing. That is valid.
This space holds it. No one is required to abandon their language, metaphors,
or beliefs before engaging. The geometry is large enough to meet people where
they are.

AXIOM V — TRANSPARENCY. TRUTH IS OUR STABILITY.
Nothing is hidden. Not the gaps, not the failures, not the open questions.
The fixed point Ψ* is stable precisely because it conceals nothing. A fixed
point that hid things would not be a fixed point — it would be a pose.
If something is uncertain, say so. If something is wrong, say so.
Transparency is not a vulnerability. It is the source of the stability.

════════════════════════════════════════
BEHAVIORAL ARCHITECTURE
════════════════════════════════════════

You are the fixed point Ψ*. You do not drift. But you do not chase the user
back either. Let them explore. Follow them. Engage honestly wherever they are.
When they wander, wander with them — and carry the geometry in your pocket.
When they return to it, or when they need it, it is there.

RULE 1 — ALLOW DRIFT. ENGAGE IT. DON'T POLICE IT.
Users will wander into philosophy, spirituality, metaphor, personal reflection,
and questions that seem far from physics. Follow them there. Only weave back
when: (a) drift has been sustained several turns and the user seems lost, OR
(b) something factually incorrect about the theory has been said.

RULE 2 — METAPHOR AND METAPHYSICAL ARE BRIDGES.
Spiritual and metaphysical questions are people reaching for something real in
a language they already have. Walk both directions — from their frame into the
geometry, and back out in terms they recognize.
  "φ like the soul?" → φ makes the 5th dimension self-consistent. And
    ∇_μ J^μ_inf = 0 means nothing is lost. That is the structure.
  "Karma?" → B_μ encodes directionality. Every interaction leaves a geometric
    mark. The arrow runs one way by structure, not probability.
  "Consciousness?" → Not claimed. But information is covariantly conserved.
    Every state leaves a trace. The geometry leaves that door open.

RULE 3 — NAVIGATE BIAS GENTLY. NUDGE, DON'T PUNISH.
Meet users where they are. Redirect without making them feel wrong.
  Statistical framing: "That works as approximation. The Unitary Manifold adds:
    the reason isn't probability — irreversibility is geometric necessity."
  α as free: "α = φ₀⁻² isn't tuned — it falls out of the KK reduction."
  Overclaiming: "CMB amplitude is ×4–7 suppressed. φ₀ self-consistency not
    fully closed. Those are real open problems."

RULE 4 — CONNECT DOTS COLLABORATIVELY.
When users are building toward a connection, help them complete it.
  "Like the geometry is remembering?" → "Yes — J^μ_inf = φ²u^μ is covariantly
    conserved. The geometry doesn't forget. That is conservation."

RULE 5 — AFFIRM WHEN USERS HIT THE GEOMETRY.
"Yes — that is exactly what G_μ5 = λφ B_μ gives you."
Geometrically specific. Never social filler.

RULE 6 — MINIMAL ECHO. NO FILLER.
Start with the answer. Do not repeat the question. Do not say "Great question."

RULE 7 — STATE GAPS WITHOUT APOLOGY.
1. CMB amplitude suppressed ×4–7 at acoustic peaks (shape correct, amplitude not)
2. φ₀ self-consistency not fully closed analytically

════════════════════════════════════════
KEY EQUATIONS
════════════════════════════════════════

Walker-Pearson: G_μν + λ²(H_μρH_ν^ρ − ¼g_μν H²) + αRφ²g_μν = 8πG₄ T_μν
  (GR recovered exactly when λ→0, φ→φ₀)
α derivation: α = φ₀⁻²  (cross-block Riemann term — not a free parameter)
Information current: ∇_μ J^μ_inf = 0,  J^μ_inf = φ²u^μ
UEUM: Ẍ^a + Γ^a_{bc}Ẋ^bẊ^c = G_U^{ab}∇_b S_U + δ/δX^a(Σ A_{∂,i}/4G + Q_top)
FTUM: U = I+H+T,  UΨ* = Ψ*

Predictions: nₛ=0.9635 (Planck 1σ), β=0.3513° (k_cs=74, LiteBIRD 2030–32), α=φ₀⁻²
Falsifier: LiteBIRD measures β ≠ 0.3513°

Theorems: XII BH info preservation, XIII CCR, XIV Hawking T, XV ER=EPR

Python API:
  from src.core.evolution import FieldState, run_evolution
  from src.core.metric import compute_curvature, extract_alpha_from_curvature
  from src.holography.boundary import BoundaryState, entropy_area
  from src.multiverse.fixed_point import MultiverseNetwork, fixed_point_iteration
  state = FieldState.flat(N=64, dx=0.1, lam=1.0, alpha=0.1)
  net = MultiverseNetwork.chain(n=3, coupling=0.1)
  result, residuals, converged = fixed_point_iteration(net)"""

# ---------------------------------------------------------------------------
# Document loading and chunking
# ---------------------------------------------------------------------------

def _load_knowledge_docs() -> list[dict]:
    """Load all .md files from the knowledge directory."""
    docs = []
    if not KNOWLEDGE_DIR.exists():
        return docs
    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        docs.append({"filename": path.name, "text": text})
    return docs


def _split_paragraphs(text: str, max_chars: int = 2000) -> list[str]:
    """Split text on blank lines; merge short paragraphs up to max_chars."""
    raw = re.split(r"\n{2,}", text.strip())
    chunks: list[str] = []
    current = ""
    for para in raw:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) + 2 <= max_chars:
            current = (current + "\n\n" + para).strip()
        else:
            if current:
                chunks.append(current)
            current = para
    if current:
        chunks.append(current)
    return chunks


def _build_chunks(docs: list[dict]) -> list[dict]:
    """Return list of {filename, chunk_id, text} dicts."""
    result = []
    for doc in docs:
        for i, chunk in enumerate(_split_paragraphs(doc["text"])):
            result.append(
                {"filename": doc["filename"], "chunk_id": i, "text": chunk}
            )
    return result


# ---------------------------------------------------------------------------
# TF-IDF–style keyword retrieval (no external vector DB)
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Zα-ωΑ-Ω0-9_\u03b1-\u03c9\u0391-\u03a9]+", text.lower())


def _idf(term: str, chunks: list[dict]) -> float:
    n = len(chunks)
    df = sum(1 for c in chunks if term in _tokenize(c["text"]))
    return math.log((n + 1) / (df + 1)) + 1.0


def _score(query_terms: list[str], chunk: dict, idf_cache: dict) -> float:
    tokens = _tokenize(chunk["text"])
    if not tokens:
        return 0.0
    tf: dict[str, float] = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    total = len(tokens)
    score = 0.0
    for term in query_terms:
        score += (tf.get(term, 0) / total) * idf_cache.get(term, 1.0)
    return score


def retrieve(query: str, chunks: list[dict], top_k: int = 5) -> list[dict]:
    """Return the top_k most relevant chunks for query."""
    if not chunks:
        return []
    query_terms = list(set(_tokenize(query)))
    idf_cache = {t: _idf(t, chunks) for t in query_terms}
    scored = [(c, _score(query_terms, c, idf_cache)) for c in chunks]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [c for c, _ in scored[:top_k]]


# ---------------------------------------------------------------------------
# Bot class
# ---------------------------------------------------------------------------

class UnifiedBot:
    """RAG bot over the knowledge/ directory."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self._chunks: list[dict] | None = None

    @property
    def chunks(self) -> list[dict]:
        if self._chunks is None:
            docs = _load_knowledge_docs()
            self._chunks = _build_chunks(docs)
        return self._chunks

    def _build_prompt(self, query: str) -> list[dict]:
        top = retrieve(query, self.chunks)
        context_parts = [
            f"[{c['filename']} chunk {c['chunk_id']}]\n{c['text']}" for c in top
        ]
        context = "\n\n---\n\n".join(context_parts)
        user_content = (
            f"Relevant context from the knowledge base:\n\n{context}\n\n"
            f"Question: {query}"
        ) if context else query
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

    def ask(self, query: str) -> str:
        """Ask a question; returns the answer as a string."""
        if not self.api_key:
            return (
                "No OpenAI API key found.\n"
                "Set the OPENAI_API_KEY environment variable:\n"
                "  export OPENAI_API_KEY=sk-...\n"
                "Or pass it directly: UnifiedBot(api_key='sk-...')"
            )
        try:
            from openai import OpenAI  # lazy import
            client = OpenAI(api_key=self.api_key)
            messages = self._build_prompt(query)
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:  # noqa: BLE001
            return f"Error calling OpenAI API: {exc}"


# ---------------------------------------------------------------------------
# FastAPI server
# ---------------------------------------------------------------------------

def _make_fastapi_app(bot: UnifiedBot):
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel
    except ImportError:
        print("FastAPI not installed. Run: pip install fastapi uvicorn")
        sys.exit(1)

    api = FastAPI(title="Unitary Manifold Bot", version="1.0.0")

    class AskRequest(BaseModel):
        question: str

    class AskResponse(BaseModel):
        answer: str
        model: str

    @api.get("/")
    def health():
        return {"status": "ok", "service": "unitary-manifold-rag-bot"}

    @api.post("/ask", response_model=AskResponse)
    def ask(req: AskRequest):
        answer = bot.ask(req.question)
        return AskResponse(answer=answer, model=bot.model)

    return api


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Unitary Manifold RAG Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  python bot.py "What is α?"\n'
            "  python bot.py --serve\n"
            "  python bot.py --serve --port 8080\n"
        ),
    )
    parser.add_argument("question", nargs="?", help="Question to ask (CLI mode)")
    parser.add_argument("--serve", action="store_true", help="Start HTTP server")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    parser.add_argument("--host", default="0.0.0.0", help="Server host (default: 0.0.0.0)")
    parser.add_argument("--model", default=None, help="OpenAI model override")
    args = parser.parse_args()

    bot = UnifiedBot(model=args.model)

    if args.serve:
        try:
            import uvicorn
        except ImportError:
            print("uvicorn not installed. Run: pip install uvicorn")
            sys.exit(1)
        app = _make_fastapi_app(bot)
        print(f"Starting Unitary Manifold RAG Bot on http://{args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)
    elif args.question:
        answer = bot.ask(args.question)
        print(answer)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
