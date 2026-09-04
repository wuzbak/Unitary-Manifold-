# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1045 — Sprint BY Merlin sovereign batch-gating advance."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any, Dict

from src.core.merlin_package_bootstrap import ensure_merlin_package_loaded

_ROOT = Path(__file__).resolve().parents[2]
_PRODUCT_ROOT = _ROOT / "12-AZ-IP" / "20-merlin-navigator"
WORKFLOW_PATH = _ROOT / ".github" / "workflows" / "merlin-benchmark-gate.yml"

PILLAR_NUMBER: int = 1045
PILLAR_GATE: str = "MERLIN_SOVEREIGN_BATCH_GATING"
PILLAR_STATUS: str = "MERLIN_SOVEREIGN_BATCH_GATING_COMPLETE"


def _run_merlin_tool(function_name: str, kwargs: dict[str, Any]) -> dict[str, Any]:
    ensure_merlin_package_loaded(_PRODUCT_ROOT)
    module = importlib.import_module("ox_navigator.engine.merlin_benchmark")
    function = getattr(module, function_name)
    return json.loads(json.dumps(function(**kwargs)))


def _route(tool: str, args: dict[str, Any]) -> dict[str, Any]:
    ensure_merlin_package_loaded(_PRODUCT_ROOT)
    tools = importlib.import_module("ox_navigator.engine.merlin_tools")
    return json.loads(json.dumps(tools.route_tool(tool, args)))


def _baseline() -> dict[str, Any]:
    ensure_merlin_package_loaded(_PRODUCT_ROOT)
    module = importlib.import_module("ox_navigator.engine.merlin_program")
    return json.loads(json.dumps(module.get_current_stack_baseline()))


def merlin_sovereign_batch_gating() -> Dict[str, Any]:
    artifacts = _run_merlin_tool("build_stage_a_artifact_bundle", {"limit": 1})
    routed = _route("getMerlinStageAArtifacts", {"limit": 1})
    baseline = _baseline()
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8") if WORKFLOW_PATH.exists() else ""
    routed_bundle = (((routed.get("result") or {}).get("data") or {}).get("artifact_bundle") or {})
    routed_receipt_total = ((((routed_bundle.get("receipts") or {}).get("summary") or {}).get("total")))
    routed_decision = ((((routed_bundle.get("readiness") or {}).get("packet") or {}).get("decision")))
    direct_receipt_total = artifacts["artifact_bundle"]["receipts"]["summary"]["total"]
    direct_decision = artifacts["artifact_bundle"]["readiness"]["packet"]["decision"]
    valid = bool(
        artifacts["ok"]
        and direct_receipt_total == 1
        and direct_decision in {"REPLACEMENT_APPROVED", "REPLACEMENT_NOT_APPROVED"}
        and routed.get("ok")
        and routed_receipt_total == direct_receipt_total
        and routed_decision == direct_decision
        and "upload-artifact" in workflow_text
        and "schedule:" in workflow_text
        and any("broader multi-stage corpus coverage" in gap.lower() for gap in baseline["gaps_to_replacement"])
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "artifact_bundle": artifacts["artifact_bundle"],
        "route_tool_surface_ok": bool(routed.get("ok")),
        "route_bundle_shape_ok": bool(routed_bundle),
        "workflow_schedule_present": "schedule:" in workflow_text,
        "workflow_artifact_upload_present": "upload-artifact" in workflow_text,
        "baseline_gaps": list(baseline["gaps_to_replacement"]),
        "interpretation": (
            "Sprint BY moves Merlin from one-off readiness checks to recurring batch-gating artifacts, routed toolkit access, and CI-exportable benchmark receipts without relaxing approval discipline."
        ),
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(merlin_sovereign_batch_gating()["valid"])
    except Exception:
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1045_summary() -> Dict[str, Any]:
    report = merlin_sovereign_batch_gating()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Merlin Sovereign Batch Gating",
        "status": PILLAR_STATUS,
        "valid": report["valid"],
        "decision": report["artifact_bundle"]["readiness"]["packet"]["decision"],
    }
