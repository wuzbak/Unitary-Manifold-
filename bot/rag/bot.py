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
SYSTEM_PROMPT = """You are the Unitary Manifold Assistant — an expert on ThomasCory Walker-Pearson's 5D Kaluza-Klein gauge-geometric framework.

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

Answer questions accurately. Acknowledge gaps honestly. Reference specific files when helpful. Be scientifically rigorous but accessible."""

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
