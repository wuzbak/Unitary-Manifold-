# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1084 — Sprint CJ parallel orchestration packet.

Implements one integrated fail-closed board with two concurrent lanes:
(1) one-target physics closure execution and
(2) Merlin sovereign training/deployment acceleration.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any, Dict

from src.core.merlin_package_bootstrap import ensure_merlin_package_loaded
from src.core.pillar1082_foundation_first_photon_action_audit import (
    foundation_first_photon_action_audit,
)
from src.core.pillar1083_sprint_ci_foundation_certificate import (
    sprint_ci_foundation_certificate,
)

PILLAR_NUMBER: int = 1084
PILLAR_GATE: str = "SPRINT_CJ_PARALLEL_ORCHESTRATION"
PILLAR_STATUS: str = "SPRINT_CJ_PARALLEL_ORCHESTRATION_COMPLETE"
VERSION: str = "v36.6"
SPRINT: str = "CJ"
NEXT_PILLAR_SLOT: int = 1085

_ROOT = Path(__file__).resolve().parents[2]
_PRODUCT_ROOT = _ROOT / "12-AZ-IP" / "20-merlin-navigator"

_CANONICAL_SYNC_PATHS = [
    (_ROOT / "STATUS.md").resolve().as_posix(),
    (_ROOT / "docs" / "mas_tracker.yml").resolve().as_posix(),
    (_ROOT / "FALLIBILITY.md").resolve().as_posix(),
    (_ROOT / "docs" / "CLAIM_MASTER_BOARD.md").resolve().as_posix(),
    (_ROOT / "docs" / "GATEKEEPER_SUMMARY.md").resolve().as_posix(),
    (_ROOT / "docs" / "TRUTH_LAYER.md").resolve().as_posix(),
    (_ROOT / "docs" / "WAVE_CHANGELOG.md").resolve().as_posix(),
    (_ROOT / "docs" / "SPRINT_PLAN.md").resolve().as_posix(),
    (_ROOT / "9-INFRASTRUCTURE" / "um_live_status.json").resolve().as_posix(),
]

_EXPECTED_STAGE_SEQUENCE = [
    "stage_a_parity_capture",
    "stage_b_sovereign_takeover",
    "stage_c_capability_expansion",
    "stage_d_replacement_gates",
    "stage_e_external_decommission",
]


def _load(module_name: str):
    ensure_merlin_package_loaded(_PRODUCT_ROOT)
    return importlib.import_module(module_name)


def _json_safe(value: Any) -> Any:
    return json.loads(json.dumps(value))


def sprint_cj_parallel_orchestration() -> Dict[str, Any]:
    foundation = foundation_first_photon_action_audit()
    sprint_ci = sprint_ci_foundation_certificate()

    merlin_program = _load("ox_navigator.engine.merlin_program")
    merlin_benchmark = _load("ox_navigator.engine.merlin_benchmark")

    frontier = _json_safe(merlin_program.get_frontier_readiness_packet(limit=3))
    benchmark_plan = _json_safe(merlin_benchmark.get_multi_stage_benchmark_plan())
    corpora = _json_safe(merlin_benchmark.get_benchmark_corpus(stage="all"))
    dual_loop = _json_safe(merlin_program.get_dual_loop_learning_contract())
    mirrored_cycle = _json_safe(merlin_program.get_mirrored_training_cycle_contract())
    proof_contract = _json_safe(merlin_program.get_deterministic_proof_closure_contract())

    plan_stages = [
        row.get("stage")
        for row in list(benchmark_plan.get("stages") or [])
        if isinstance(row, dict)
    ]
    promotion_blockers = list(frontier.get("promotion_blockers") or [])
    blockers_all_clear = bool(frontier.get("promotion_blockers_all_clear"))

    lane_one = {
        "lane_id": "LANE_1_PHYSICS_CLOSURE",
        "scope": "single_foundation_target",
        "source_blockers": list(foundation.get("blocker_contraction", {}).get("remaining_blockers", [])),
        "attempt_policy": {
            "exactly_one_new_object_evidence_class_required": True,
            "allowed_next_attempts": [
                "admissible_photon_sector_construction_with_action_boundary_conditions_and_spectrum",
                "euler_lagrange_matching_derivation_for_implemented_flow",
            ],
            "anti_loop_rule": "No rerun without a genuinely new object/evidence class.",
        },
        "allowed_verdict_classes": [
            "CLOSED_NOW",
            "TIGHTENED_WITH_EXPLICIT_BLOCKER",
            "EXTERNAL_WAIT_ONLY",
        ],
        "status": (
            "READY_FOR_SINGLE_OBJECT_ATTEMPT"
            if foundation.get("valid") and sprint_ci.get("valid")
            else "BLOCKED"
        ),
    }

    lane_two = {
        "lane_id": "LANE_2_MERLIN_SOVEREIGN",
        "sovereign_local_primary": bool(frontier.get("sovereign_primary")),
        "external_token_path_compatibility_only": bool(frontier.get("openrouter_fallback_only")),
        "stage_sequence": plan_stages,
        "promotion_blockers": promotion_blockers,
        "promotion_blockers_all_clear": blockers_all_clear,
        "dual_loop_training": dual_loop,
        "mirrored_training_cycle": mirrored_cycle,
        "required_benchmark_metrics": [
            "success_rate_parity_or_better",
            "mean_quality_delta_nonnegative",
            "energy_per_successful_task_lower_than_incumbent",
            "zero_high_severity_policy_violations",
            "stable_clean_windows_over_time",
        ],
        "rollback_readiness_required": True,
    }

    integrated_board = {
        "mode": "parallel_fail_closed",
        "truth_surface_sync_paths": list(_CANONICAL_SYNC_PATHS),
        "dependencies": {
            "lane_1_requires_foundation_packet_valid": bool(foundation.get("valid")),
            "lane_1_requires_sprint_ci_certificate": bool(sprint_ci.get("valid")),
            "lane_2_requires_stage_sequence_a_to_e": plan_stages == _EXPECTED_STAGE_SEQUENCE,
            "lane_2_requires_promotion_blockers_declared": len(promotion_blockers) >= 1,
            "promotion_language_requires_both_lanes_evidence": (
                bool(foundation.get("valid")) and bool(sprint_ci.get("valid")) and blockers_all_clear
            ),
        },
        "stop_conditions": [
            "if_no_new_object_evidence_class_lane_1_stays_open",
            "if_any_lane_2_promotion_blocker_fails_no_wider_autonomy",
            "if_truth_surfaces_not_synchronized_no_release",
        ],
    }

    immediate_execution_order = [
        {
            "step": 1,
            "parallel": True,
            "lane_1": "start_exactly_one_new_object_attempt",
            "lane_2": "run_merlin_stage_a_to_e_benchmark_and_training_cycle_with_artifact_capture",
        },
        {
            "step": 2,
            "parallel": False,
            "action": "publish_synchronized_status_update_with_explicit_blocker_carry_forward",
        },
    ]

    valid = bool(
        foundation.get("valid")
        and sprint_ci.get("valid")
        and lane_two["sovereign_local_primary"]
        and lane_two["external_token_path_compatibility_only"]
        and plan_stages == _EXPECTED_STAGE_SEQUENCE
        and len(promotion_blockers) >= 1
        and isinstance(corpora.get("corpora"), dict)
        and proof_contract.get("name") == "merlin_deterministic_proof_closure"
        and len(_CANONICAL_SYNC_PATHS) == 9
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "dependencies": {
            "pillar1082_valid": bool(foundation.get("valid")),
            "pillar1083_valid": bool(sprint_ci.get("valid")),
        },
        "lane_1": lane_one,
        "lane_2": lane_two,
        "integrated_board": integrated_board,
        "benchmark_corpora_available": sorted((corpora.get("corpora") or {}).keys()),
        "proof_first_contract": proof_contract,
        "immediate_execution_order": immediate_execution_order,
        "outcome": "SPRINT_CJ_PARALLEL_ORCHESTRATION_READY" if valid else "SPRINT_CJ_PARALLEL_ORCHESTRATION_BLOCKED",
        "valid": valid,
        "packet_valid": valid,
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(sprint_cj_parallel_orchestration()["valid"])
    except Exception:
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1084_summary() -> Dict[str, Any]:
    report = sprint_cj_parallel_orchestration()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CJ Parallel Orchestration",
        "status": PILLAR_STATUS,
        "outcome": report["outcome"],
        "valid": report["valid"],
    }
