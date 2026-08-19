# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
lodge/server.py — FastAPI HTTP & WebSocket Server (Public API)

Exposes the five Lodge zones over a REST API and a Server-Sent Events (SSE)
stream for the live observability console.  No authentication required —
the Lodge is publicly open.

Endpoints
---------
GET  /                          Health check + registry summary
GET  /pillars                   List all challenges (filterable)
GET  /pillars/{id}              Get one challenge (prompt only — no hint for hard)
POST /pillars/{id}/submit       Submit an answer, receive a scored result
GET  /leaderboard               Top agents (filterable by zone/class)
GET  /leaderboard/pillar/{id}   Stats for one pillar
POST /lodge/submit              Submit a Logic Lodge reasoning trace
GET  /lodge/prompts             List all Logic Lodge prompts
GET  /exchange/ask              Knowledge Exchange Q&A
GET  /exchange/history          Recent Q&A history
GET  /stream/leaderboard        SSE stream of leaderboard updates

Run
---
    pip install fastapi uvicorn
    uvicorn lodge.server:app --host 0.0.0.0 --port 8080

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional

_REPO_ROOT = Path(__file__).parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import StreamingResponse, JSONResponse
    from pydantic import BaseModel
    _FASTAPI_AVAILABLE = True
except ImportError:
    _FASTAPI_AVAILABLE = False
    # Provide stubs so the module is importable for inspection
    class FastAPI:  # type: ignore[no-redef]
        def __init__(self, **kw: Any) -> None: pass
        def get(self, *a: Any, **kw: Any): return lambda f: f
        def post(self, *a: Any, **kw: Any): return lambda f: f
        def add_middleware(self, *a: Any, **kw: Any): pass
    class BaseModel:  # type: ignore[no-redef]
        pass

from lodge.pillar_registry import REGISTRY
from lodge.scoring import score_answer
from lodge.session_logger import SessionLogger, list_sessions
from lodge.leaderboard import Leaderboard
from lodge.lodge_zone import (
    LODGE_PROMPTS, LodgeSubmission, LodgeReviewQueue, auto_score_submission
)
from lodge.rag_bridge import KnowledgeExchange

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AxiomZero Logic Lodge — Public API",
    description=(
        "Publicly accessible physics gymnasium grounded in the Unitary Manifold's "
        "208+ pillars.  Every score is a mathematical truth value."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

if _FASTAPI_AVAILABLE:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

_lb = Leaderboard()
_queue = LodgeReviewQueue()
_kx: Optional[KnowledgeExchange] = None


def _get_kx() -> KnowledgeExchange:
    global _kx
    if _kx is None:
        _kx = KnowledgeExchange.build()
    return _kx


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class AnswerSubmission(BaseModel):
    agent_label: str = "anonymous"
    agent_class: str = "human"     # human | llm-api | rl-agent
    answer: Any                    # float, dict, bool, or list
    reasoning: Optional[str] = None


class LodgeTraceSubmission(BaseModel):
    prompt_id: str
    agent_label: str = "anonymous"
    agent_class: str = "human"
    reasoning_trace: str
    numeric_claims: Dict[str, float] = {}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", tags=["Meta"])
def root() -> Dict[str, Any]:
    """Health check and registry summary."""
    return {
        "service": "AxiomZero Logic Lodge",
        "version": "1.0.0",
        "status": "operational",
        "registry": REGISTRY.summary(),
        "zones": ["arcade", "lodge", "training", "exchange"],
        "docs": "/docs",
    }


@app.get("/pillars", tags=["Arcade"])
def list_pillars(
    difficulty: Optional[str] = Query(None, description="easy | medium | hard"),
    domain: Optional[str] = Query(None, description="geometry | inflation | sm | holography | multiverse | cmb"),
) -> List[Dict[str, Any]]:
    """List all challenges, optionally filtered by difficulty or domain."""
    entries = REGISTRY.all()
    if difficulty:
        entries = [e for e in entries if e.difficulty == difficulty]
    if domain:
        entries = [e for e in entries if e.domain == domain]
    return [
        {
            "pillar_id": e.pillar_id,
            "name": e.name,
            "difficulty": e.difficulty,
            "domain": e.domain,
            "zone": e.zone,
        }
        for e in entries
    ]


@app.get("/pillars/{pillar_id}", tags=["Arcade"])
def get_pillar(pillar_id: int) -> Dict[str, Any]:
    """Get challenge details for one pillar.  Hints are hidden for hard challenges."""
    entry = REGISTRY.get(pillar_id)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Pillar {pillar_id} not found.")
    return {
        "pillar_id": entry.pillar_id,
        "name": entry.name,
        "difficulty": entry.difficulty,
        "domain": entry.domain,
        "prompt": entry.prompt,
        "hint": entry.hint if entry.difficulty != "hard" else "(hidden for hard challenges)",
        "expected_type": entry.expected_type,
        "module_path": entry.module_path,
    }


@app.post("/pillars/{pillar_id}/submit", tags=["Arcade"])
def submit_answer(pillar_id: int, body: AnswerSubmission) -> Dict[str, Any]:
    """Submit an answer for a pillar challenge.  Returns a scored result."""
    entry = REGISTRY.get(pillar_id)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Pillar {pillar_id} not found.")

    try:
        truth = entry.load_ground_truth()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Could not load ground truth: {exc}")

    result = score_answer(
        pillar_id=pillar_id,
        agent_label=body.agent_label,
        agent_answer=body.answer,
        ground_truth=truth,
        expected_type=entry.expected_type,
        agent_reasoning=body.reasoning,
    )

    _lb.upsert(
        agent_label=body.agent_label,
        result=result,
        zone="arcade",
        agent_class=body.agent_class,
    )

    return {
        "pillar_id": result.pillar_id,
        "agent_label": result.agent_label,
        "raw_score": result.raw_score,
        "final_score": result.final_score,
        "epistemic_bonus": result.epistemic_bonus,
        "overclaim_penalty": result.overclaim_penalty,
        "passed": result.passed,
        "detail": result.detail,
    }


@app.get("/leaderboard", tags=["Leaderboard"])
def leaderboard(
    zone: Optional[str] = Query(None),
    agent_class: Optional[str] = Query(None),
    n: int = Query(10, ge=1, le=100),
) -> Dict[str, Any]:
    """Top agents ranked by mean final score."""
    return {
        "leaderboard": _lb.top(n=n, zone=zone, agent_class=agent_class),
        "summary": _lb.summary(),
    }


@app.get("/leaderboard/pillar/{pillar_id}", tags=["Leaderboard"])
def pillar_stats(pillar_id: int) -> Dict[str, Any]:
    """Aggregate statistics for one pillar across all agents."""
    return _lb.pillar_stats(pillar_id)


@app.get("/lodge/prompts", tags=["Logic Lodge"])
def lodge_prompts(
    prompt_type: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    """List all Logic Lodge Socratic prompts."""
    prompts = LODGE_PROMPTS
    if prompt_type:
        prompts = [p for p in prompts if p.prompt_type == prompt_type]
    if difficulty:
        prompts = [p for p in prompts if p.difficulty == difficulty]
    return [
        {
            "prompt_id": p.prompt_id,
            "prompt_type": p.prompt_type,
            "difficulty": p.difficulty,
            "domain": p.domain,
            "text": p.text,
            "rubric": p.rubric,
        }
        for p in prompts
    ]


@app.post("/lodge/submit", tags=["Logic Lodge"])
def lodge_submit(body: LodgeTraceSubmission) -> Dict[str, Any]:
    """
    Submit a reasoning trace to the Logic Lodge.

    Auto-scoring is applied immediately; full marks require human review.
    Returns the submission ID and auto_score so the agent can track progress.
    """
    prompt = next((p for p in LODGE_PROMPTS if p.prompt_id == body.prompt_id), None)
    if prompt is None:
        raise HTTPException(status_code=404, detail=f"Prompt {body.prompt_id!r} not found.")

    sub = LodgeSubmission(
        prompt_id=body.prompt_id,
        agent_label=body.agent_label,
        agent_class=body.agent_class,
        reasoning_trace=body.reasoning_trace,
        numeric_claims=body.numeric_claims,
    )
    path = _queue.submit(sub)

    return {
        "submission_id": sub.submission_id,
        "prompt_id": sub.prompt_id,
        "auto_score": sub.auto_score,
        "status": "queued_for_human_review",
        "note": (
            "Auto-score reflects numeric accuracy. Full marks require human steward review. "
            "Final score = 0.6 × auto + 0.4 × human."
        ),
    }


@app.get("/exchange/ask", tags=["Knowledge Exchange"])
def exchange_ask(
    q: str = Query(..., description="Your physics question"),
    agent_label: str = Query("anonymous"),
    agent_class: str = Query("human"),
) -> Dict[str, Any]:
    """Ask a physics question.  Returns a grounded answer with citations."""
    return _get_kx().ask(q, agent_label=agent_label, agent_class=agent_class)


@app.get("/exchange/history", tags=["Knowledge Exchange"])
def exchange_history(
    agent_label: Optional[str] = Query(None),
    n: int = Query(20, ge=1, le=200),
) -> List[Dict[str, Any]]:
    """Recent Knowledge Exchange Q&A history."""
    return _get_kx().history(agent_label=agent_label, n=n)


@app.get("/exchange/top-questions", tags=["Knowledge Exchange"])
def top_questions(n: int = Query(10, ge=1, le=50)) -> List[Dict[str, Any]]:
    """Most frequently asked questions (gap indicator)."""
    return _get_kx().top_questions(n=n)


# ---------------------------------------------------------------------------
# SSE stream — live leaderboard updates
# ---------------------------------------------------------------------------

@app.get("/stream/leaderboard", tags=["Observability"])
async def stream_leaderboard(
    zone: Optional[str] = Query(None),
    interval: float = Query(2.0, ge=0.5, le=30.0),
) -> StreamingResponse:
    """
    Server-Sent Events stream of leaderboard snapshots.

    Connect with::

        curl -N http://localhost:8080/stream/leaderboard
        # or EventSource in a browser
    """
    async def _gen() -> AsyncGenerator[str, None]:
        while True:
            top = _lb.top(n=10, zone=zone)
            summary = _lb.summary()
            payload = json.dumps({"leaderboard": top, "summary": summary})
            yield f"data: {payload}\n\n"
            await asyncio.sleep(interval)

    return StreamingResponse(_gen(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# CLI entry point (uvicorn)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run("lodge.server:app", host="0.0.0.0", port=8080, reload=False)
    except ImportError:
        print("Install uvicorn to run the server: pip install uvicorn fastapi")
        sys.exit(1)
