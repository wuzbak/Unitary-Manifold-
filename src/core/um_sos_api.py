from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Query

from pathlib import Path

from src.core.um_sos_rag import answer_with_labels, build_chunks
from src.core.pillar394_postulate_minimality_audit import ADMISSIONS
from src.core.prediction_registry import (
    PREDICTION_REGISTRY,
    list_predictions,
    registry_summary,
)
from src.core.um_sos_registry import export_registry

DEFAULT_AI_QUERY_SCOPE = [
    "docs/CLAIM_MASTER_BOARD.md",
    "docs/GATEKEEPER_SUMMARY.md",
    "FALLIBILITY.md",
]


def _normalize_prediction(pid: str) -> Dict[str, Any]:
    entry = dict(PREDICTION_REGISTRY[pid])
    entry["id"] = pid
    return entry


def _prediction_status_for_experiment(experiment: str) -> List[Dict[str, Any]]:
    exp = experiment.lower()
    return [
        _normalize_prediction(pid)
        for pid in list_predictions()
        if exp in PREDICTION_REGISTRY[pid]["experiment"].lower()
    ]


def _admissions() -> List[Dict[str, Any]]:
    return [
        {
            "name": record.name,
            "status": record.status.value,
            "breaks_if_fails": record.breaks_if_fails,
            "citation": record.citation,
            "closed_by": record.closed_by,
            "used_by": record.used_by,
        }
        for record in ADMISSIONS
    ]


def create_app() -> FastAPI:
    app = FastAPI(
        title="UM-SOS API",
        version="1.0.0",
        description="Unitary Manifold Scientific Operating System API",
    )

    @app.get("/api/v1/predictions/all")
    def all_predictions() -> Dict[str, Any]:
        rows = [_normalize_prediction(pid) for pid in list_predictions()]
        return {
            "count": len(rows),
            "summary": registry_summary(),
            "predictions": rows,
        }

    @app.get("/api/v1/status")
    def experiment_status(experiment: str = Query(..., description="Experiment name")) -> Dict[str, Any]:
        matches = _prediction_status_for_experiment(experiment)
        if not matches:
            return {
                "experiment": experiment,
                "count": 0,
                "status": "NO_MATCHES",
                "predictions": [],
            }

        statuses = sorted({item["current_status"] for item in matches})
        return {
            "experiment": experiment,
            "count": len(matches),
            "status": "MATCHED",
            "current_statuses": statuses,
            "predictions": matches,
        }

    @app.get("/api/v1/gaps")
    def admission_gaps(status: Optional[str] = Query(default=None)) -> Dict[str, Any]:
        rows = _admissions()
        if status:
            status_l = status.lower()
            rows = [row for row in rows if status_l in row["status"].lower()]
        return {"count": len(rows), "admissions": rows}

    @app.get("/api/v1/pillars")
    def pillar_info(pillar_id: int = Query(...)) -> Dict[str, Any]:
        registry = export_registry()
        match = next((e for e in registry["entries"] if e["pillar"] == pillar_id), None)
        if match:
            return {"found": True, "pillar": match}
        return {"found": False, "pillar_id": pillar_id}

    @app.post("/api/v1/governance/classify")
    def governance_classify(payload: Dict[str, Any]) -> Dict[str, Any]:
        text = str(payload.get("text", "")).lower()
        if any(k in text for k in ["falsify", "publish", "override", "critical", "safety"]):
            lane = "CRITICAL"
            action = "Human decision required"
        elif any(k in text for k in ["experiment", "routing", "review", "sensitive"]):
            lane = "SENSITIVE"
            action = "AI recommends, human reviews"
        else:
            lane = "ROUTINE"
            action = "AI may execute autonomously"
        return {"lane": lane, "recommended_action": action}

    @app.post("/api/v1/ai/query")
    def ai_query(payload: Dict[str, Any]) -> Dict[str, Any]:
        question = str(payload.get("question", "")).strip()
        scope = payload.get("scope") or DEFAULT_AI_QUERY_SCOPE
        repo_root = Path(__file__).resolve().parents[2]
        chunks = build_chunks([repo_root / rel for rel in scope if (repo_root / rel).exists()])
        answer = answer_with_labels(question, chunks)
        governance = governance_classify({"text": question})
        answer["governance_lane"] = governance["lane"]
        return answer

    @app.get("/api/v1/preregistered")
    def preregistered() -> Dict[str, Any]:
        return export_registry()

    return app
