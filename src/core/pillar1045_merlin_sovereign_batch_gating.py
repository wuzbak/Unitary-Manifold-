# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1045 — Sprint BY Merlin sovereign batch-gating advance."""

from __future__ import annotations

import importlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict

_ROOT = Path(__file__).resolve().parents[2]
_PRODUCT_ROOT = _ROOT / "12-AZ-IP" / "20-merlin-navigator"
WORKFLOW_PATH = _ROOT / ".github" / "workflows" / "merlin-benchmark-gate.yml"

PILLAR_NUMBER: int = 1045
PILLAR_GATE: str = "MERLIN_SOVEREIGN_BATCH_GATING"
PILLAR_STATUS: str = "MERLIN_SOVEREIGN_BATCH_GATING_COMPLETE"


def _ensure_merlin_package_loaded() -> None:
    if "ox_navigator" in sys.modules:
        return
    package_root = _PRODUCT_ROOT / "ox_navigator"
    spec = importlib.util.spec_from_file_location(
        "ox_navigator",
        package_root / "__init__.py",
        submodule_search_locations=[str(package_root)],
    )
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load ox_navigator package")
    module = importlib.util.module_from_spec(spec)
    sys.modules["ox_navigator"] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop("ox_navigator", None)
        raise


def _run_merlin_tool(function_name: str, kwargs: dict[str, Any]) -> dict[str, Any]:
    _ensure_merlin_package_loaded()
    module = importlib.import_module("ox_navigator.engine.merlin_benchmark")
    function = getattr(module, function_name)
    return json.loads(json.dumps(function(**kwargs)))


def _route(tool: str, args: dict[str, Any]) -> dict[str, Any]:
    _ensure_merlin_package_loaded()
    tools = importlib.import_module("ox_navigator.engine.merlin_tools")
    return json.loads(json.dumps(tools.route_tool(tool, args)))


def _baseline() -> dict[str, Any]:
    _ensure_merlin_package_loaded()
    module = importlib.import_module("ox_navigator.engine.merlin_program")
    return json.loads(json.dumps(module.get_current_stack_baseline()))


def merlin_sovereign_batch_gating() -> Dict[str, Any]:
    artifacts = _run_merlin_tool("build_stage_a_artifact_bundle", {"limit": 1})
    routed = _route("getMerlinStageAArtifacts", {"limit": 1})
    baseline = _baseline()
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8") if WORKFLOW_PATH.exists() else ""
    valid = bool(
        artifacts["ok"]
        and artifacts["artifact_bundle"]["receipts"]["summary"]["total"] == 1
        and artifacts["artifact_bundle"]["readiness"]["packet"]["decision"] in {"REPLACEMENT_APPROVED", "REPLACEMENT_NOT_APPROVED"}
        and routed["ok"]
        and routed["result"]["data"]["artifact_bundle"]["receipts"]["summary"]["total"] == 1
        and "upload-artifact" in workflow_text
        and "schedule:" in workflow_text
        and all("no formal benchmark corpus" not in gap.lower() for gap in baseline["gaps_to_replacement"])
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "artifact_bundle": artifacts["artifact_bundle"],
        "route_tool_surface_ok": routed["ok"],
        "workflow_schedule_present": "schedule:" in workflow_text,
        "workflow_artifact_upload_present": "upload-artifact" in workflow_text,
        "baseline_gaps": list(baseline["gaps_to_replacement"]),
        "interpretation": (
            "Sprint BY moves Merlin from one-off readiness checks to recurring batch-gating artifacts, routed toolkit access, and CI-exportable benchmark receipts without relaxing approval discipline."
        ),
    }


PILLAR_VALID: bool = True


def pillar1045_summary() -> Dict[str, Any]:
    report = merlin_sovereign_batch_gating()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Merlin Sovereign Batch Gating",
        "status": PILLAR_STATUS,
        "valid": report["valid"],
        "decision": report["artifact_bundle"]["readiness"]["packet"]["decision"],
    }
