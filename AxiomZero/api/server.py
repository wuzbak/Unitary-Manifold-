# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# AxiomZero — Persistent AI Cognitive Layer for the Unitary Manifold
# Project: https://github.com/wuzbak/Unitary-Manifold-
# Theory & scientific direction: ThomasCory Walker-Pearson
# Code architecture & implementation: GitHub Copilot (AI)
"""
AxiomZero api/server.py — FastAPI API server

Endpoints:
  GET  /                         — Health check
  GET  /status                   — Orchestrator status
  POST /tasks                    — Submit a new task
  GET  /tasks/{task_id}          — Get task status & results
  GET  /tasks                    — List all tasks
  POST /tasks/{task_id}/approve  — HILS: approve or reject a task
  GET  /approvals/pending        — List tasks awaiting human approval
  GET  /logs                     — Recent agent audit log
  GET  /logs/notifications       — Events requiring human attention
  POST /rag/query                — Query the RAG vector store
  GET  /governance/violations    — HILS gate violations
  POST /governance/classify      — Pentad classification endpoint
  GET  /health/vram              — GPU VRAM status

Run::
    uvicorn AxiomZero.api.server:app --host 0.0.0.0 --port 8000 --reload

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel
    _FASTAPI = True
except ImportError:
    _FASTAPI = False
    logger.warning("FastAPI not installed — API server unavailable. pip install fastapi uvicorn")

from AxiomZero.core.agent_core import AxiomZeroOrchestrator, EpistemicLabel, AgentTask
from AxiomZero.governance.hils_gate import get_gate
from AxiomZero.memory.session_log import get_recent_events, get_human_notifications

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
if _FASTAPI:
    class TaskRequest(BaseModel):
        description: str
        epistemic_label: str = "HARDGATE"
        payload: Dict[str, Any] = {}
        max_cycles: int = 5

    class ApprovalRequest(BaseModel):
        approved: bool
        note: str = ""

    class RAGQueryRequest(BaseModel):
        query: str
        n_results: int = 5

    class GovernanceClassifyRequest(BaseModel):
        action_type: str
        payload: Dict[str, Any] = {}

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app() -> "FastAPI":
    if not _FASTAPI:
        raise ImportError("FastAPI required: pip install fastapi uvicorn")

    from AxiomZero import IDENTITY

    app = FastAPI(
        title="AxiomZero API",
        description=(
            "Persistent AI Cognitive Layer for the Unitary Manifold. "
            f"© 2026 {IDENTITY['author']} · {IDENTITY['license']}"
        ),
        version=IDENTITY["version"],
        contact={
            "name": IDENTITY["author"],
            "url": IDENTITY["repo"],
        },
        license_info={
            "name": IDENTITY["license"],
            "url": IDENTITY["repo"] + "/blob/main/LICENSE",
        },
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict in production via config
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Load orchestrator (lazy, shared across requests)
    _orchestrator: Optional[AxiomZeroOrchestrator] = None

    def get_orchestrator() -> AxiomZeroOrchestrator:
        nonlocal _orchestrator
        if _orchestrator is None:
            _orchestrator = AxiomZeroOrchestrator.from_config()
        return _orchestrator

    # ------------------------------------------------------------------
    # Health / root
    # ------------------------------------------------------------------

    @app.get("/", response_class=HTMLResponse)
    async def root():
        return _dashboard_html()

    @app.get("/health")
    async def health():
        from AxiomZero import IDENTITY
        return {
            "status": "ok",
            "service": "AxiomZero",
            "version": IDENTITY["version"],
            "author": IDENTITY["author"],
            "license": IDENTITY["license"],
            "repo": IDENTITY["repo"],
            "framework": IDENTITY["framework"],
        }

    @app.get("/identity")
    async def identity():
        """Return full IP provenance record for AxiomZero."""
        from AxiomZero import IDENTITY
        return IDENTITY

    @app.get("/health/vram")
    async def health_vram():
        try:
            from AxiomZero.core.model_router import _get_vram_pct
            pct = await _get_vram_pct()
            return {"vram_pct": pct, "paused": pct > 90}
        except Exception as exc:
            return {"vram_pct": None, "error": str(exc)}

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    @app.get("/status")
    async def status():
        orch = get_orchestrator()
        return orch.status()

    # ------------------------------------------------------------------
    # Tasks
    # ------------------------------------------------------------------

    @app.post("/tasks", status_code=202)
    async def submit_task(req: TaskRequest, background_tasks: BackgroundTasks):
        orch = get_orchestrator()
        try:
            label = EpistemicLabel(req.epistemic_label)
        except ValueError:
            raise HTTPException(400, f"Invalid epistemic_label: {req.epistemic_label}")

        # Run task in background
        task = AgentTask(
            description=req.description,
            epistemic_label=label,
            payload=req.payload,
            max_cycles=req.max_cycles,
        )
        background_tasks.add_task(
            orch.run_task,
            description=req.description,
            epistemic_label=label,
            payload=req.payload,
            max_cycles=req.max_cycles,
        )
        return {"task_id": task.task_id, "status": "submitted", "message": "Task queued"}

    @app.get("/tasks")
    async def list_tasks():
        orch = get_orchestrator()
        tasks = orch.list_tasks()
        return [_task_summary(t) for t in tasks]

    @app.get("/tasks/{task_id}")
    async def get_task(task_id: str):
        orch = get_orchestrator()
        task = orch.get_task(task_id)
        if task is None:
            raise HTTPException(404, f"Task {task_id} not found")
        return _task_detail(task)

    @app.post("/tasks/{task_id}/approve")
    async def approve_task(task_id: str, req: ApprovalRequest):
        orch = get_orchestrator()
        try:
            task = await orch.approve_task(task_id, req.approved)
            return {"task_id": task_id, "approved": req.approved, "status": task.status}
        except KeyError:
            raise HTTPException(404, f"Task {task_id} not found")
        except ValueError as exc:
            raise HTTPException(400, str(exc))

    @app.get("/approvals/pending")
    async def pending_approvals():
        orch = get_orchestrator()
        tasks = orch.pending_approvals()
        return [_task_detail(t) for t in tasks]

    # ------------------------------------------------------------------
    # Logs
    # ------------------------------------------------------------------

    @app.get("/logs")
    async def get_logs(n: int = 50, event_type: Optional[str] = None):
        return get_recent_events(n=n, event_type=event_type)

    @app.get("/logs/notifications")
    async def get_notifications():
        return get_human_notifications()

    # ------------------------------------------------------------------
    # RAG
    # ------------------------------------------------------------------

    @app.post("/rag/query")
    async def rag_query(req: RAGQueryRequest):
        try:
            from AxiomZero.memory.vector_store import VectorStore
            vs = VectorStore.from_config()
            results = vs.query(req.query, n_results=req.n_results)
            return {"query": req.query, "results": results}
        except Exception as exc:
            raise HTTPException(500, f"RAG query failed: {exc}")

    # ------------------------------------------------------------------
    # Governance
    # ------------------------------------------------------------------

    @app.get("/governance/violations")
    async def governance_violations():
        gate = get_gate()
        return {"violations": gate.get_violations()}

    @app.post("/governance/classify")
    async def governance_classify(req: GovernanceClassifyRequest):
        gate = get_gate()
        result = gate.classify_for_pentad(req.action_type, req.payload)
        check = gate.check_action(req.action_type, "api_caller", req.payload)
        return {**result, **check}

    return app


# ---------------------------------------------------------------------------
# Dashboard HTML (served at /)
# ---------------------------------------------------------------------------

def _dashboard_html() -> str:
    dashboard_path = Path(__file__).parent.parent / "ui" / "dashboard.html"
    if dashboard_path.exists():
        return dashboard_path.read_text()
    return """<!DOCTYPE html>
<html><head><title>AxiomZero</title>
<style>body{font-family:monospace;background:#0d1117;color:#e6edf3;padding:2rem}
h1{color:#58a6ff}a{color:#79c0ff}.status{margin:1rem 0;padding:1rem;background:#161b22;border-radius:8px}
</style></head><body>
<h1>⚛ AxiomZero — Cognitive Layer</h1>
<p>Persistent AI intelligence layer for the Unitary Manifold physics framework.</p>
<div class="status">
<p><a href="/status">/status</a> — Orchestrator status</p>
<p><a href="/tasks">/tasks</a> — All tasks</p>
<p><a href="/approvals/pending">/approvals/pending</a> — Awaiting human approval</p>
<p><a href="/logs">/logs</a> — Agent audit log</p>
<p><a href="/logs/notifications">/logs/notifications</a> — Human notifications</p>
<p><a href="/health/vram">/health/vram</a> — GPU VRAM status</p>
<p><a href="/docs">/docs</a> — API documentation</p>
</div>
<p><em>Theory: ThomasCory Walker-Pearson · Code: GitHub Copilot (AI)</em></p>
</body></html>"""


def _task_summary(task: AgentTask) -> Dict:
    return {
        "task_id": task.task_id,
        "description": task.description[:100],
        "status": task.status,
        "epistemic_label": task.epistemic_label.value,
        "cycle_count": task.cycle_count,
        "requires_human_approval": task.requires_human_approval,
    }


def _task_detail(task: AgentTask) -> Dict:
    return {
        **_task_summary(task),
        "payload": {k: str(v)[:200] for k, v in task.payload.items()},
        "results": {k: str(v)[:500] for k, v in task.results.items()},
        "error": task.error,
        "created_at": task.created_at,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if _FASTAPI:
    app = create_app()
