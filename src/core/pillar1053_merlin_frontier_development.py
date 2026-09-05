# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1053 — Merlin frontier development sprint report."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any, Dict

from src.core.merlin_package_bootstrap import ensure_merlin_package_loaded
from src.core.pillar1052_targeted_closure_deterministic_rigor import targeted_closure_deterministic_rigor

PILLAR_NUMBER: int = 1053
PILLAR_GATE: str = "MERLIN_FRONTIER_DEVELOPMENT"
PILLAR_STATUS: str = "MERLIN_FRONTIER_DEVELOPMENT_COMPLETE"

_ROOT = Path(__file__).resolve().parents[2]
_PRODUCT_ROOT = _ROOT / "12-AZ-IP" / "20-merlin-navigator"


def _load(module_name: str):
    ensure_merlin_package_loaded(_PRODUCT_ROOT)
    return importlib.import_module(module_name)


def _json_safe(value: Any) -> Any:
    return json.loads(json.dumps(value))


def merlin_frontier_development() -> Dict[str, Any]:
    closure = targeted_closure_deterministic_rigor()
    tools = _load("ox_navigator.engine.merlin_tools")
    bench = _load("ox_navigator.engine.merlin_benchmark")
    memory_mod = _load("ox_navigator.engine.merlin_memory")
    runtime = _load("ox_navigator.engine.merlin_runtime")

    readiness = _json_safe(tools.route_tool("getMerlinFrontierReadiness", {"limit": 2}))
    control_tower = _json_safe(tools.route_tool("getMerlinControlTower", {"limit": 2}))
    stage_plan = _json_safe(bench.get_multi_stage_benchmark_plan())
    corpus = _json_safe(bench.get_benchmark_corpus(stage="all"))

    session = memory_mod.MerlinSession()
    session.add_turn("What is Merlin?", "HARDGATE profile answer")
    session.add_turn("What is Merlin?", "GOVERNANCE boundary answer")
    memory_state = _json_safe(session.get_memory_state())

    route_default = _json_safe(runtime.get_mythos_astra_runtime_contract())

    readiness_data = ((readiness.get("result") or {}).get("data") or {})
    control_tower_data = ((control_tower.get("result") or {}).get("data") or {})
    stage_plan_data = (
        stage_plan.get("data")
        if isinstance(stage_plan, dict) and isinstance(stage_plan.get("data"), dict)
        else stage_plan
    )
    stage_entries = (
        stage_plan_data.get("stages", [])
        if isinstance(stage_plan_data, dict)
        else []
    )
    promotion_blockers = list(readiness_data.get("promotion_blockers") or [])
    legacy_paths = route_default.get("capability_contract", {}).get("compatibility", {}).get("legacy_paths_retained") or []

    valid = bool(
        closure["valid"]
        and readiness.get("ok")
        and readiness_data.get("sovereign_primary") is True
        and readiness_data.get("openrouter_fallback_only") is True
        and len(promotion_blockers) >= 4
        and any(not b.get("pass") for b in promotion_blockers)
        and control_tower.get("ok") is True
        and control_tower_data.get("ok") is True
        and "stage_e_external_decommission" in [s.get("stage") for s in stage_entries if isinstance(s, dict)]
        and corpus.get("ok") is True
        and memory_state.get("contradiction_event_count", 0) >= 1
        and {"/api/ox", "/api/ox/status"}.issubset(set(legacy_paths))
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "dependencies": {
            "targeted_closure": closure["valid"],
        },
        "frontier_readiness": readiness_data,
        "control_tower": control_tower_data,
        "multi_stage_plan": stage_plan,
        "benchmark_corpora": corpus,
        "memory_contradiction_signal": {
            "contradiction_event_count": memory_state.get("contradiction_event_count", 0),
            "tiers": memory_state.get("tiers", []),
        },
        "runtime_contract": route_default,
        "non_claims": [
            "Merlin is not approved for broad autonomous replacement unless promotion blockers clear.",
            "OpenRouter remains compatibility-only fallback and is not a primary sovereignty lane.",
        ],
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(merlin_frontier_development()["valid"])
    except Exception:
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1053_summary() -> Dict[str, Any]:
    report = merlin_frontier_development()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Merlin Frontier Development",
        "status": PILLAR_STATUS,
        "valid": report["valid"],
        "blocker_count": len(report["frontier_readiness"].get("promotion_blockers", [])),
    }
