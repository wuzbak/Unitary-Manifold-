# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1084 — Sprint CJ parallel orchestration packet.

Implements one integrated fail-closed board with two concurrent lanes:
(1) one-target physics closure execution and
(2) Merlin sovereign training/deployment acceleration.
"""

from __future__ import annotations

import importlib
from copy import deepcopy
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


def _load(module_name: str) -> Any:
    ensure_merlin_package_loaded(_PRODUCT_ROOT)
    return importlib.import_module(module_name)


def _json_safe(value: Any) -> Any:
    return deepcopy(value)


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _truth_surface_sync_status() -> Dict[str, Any]:
    checks = {
        (_ROOT / "STATUS.md").resolve().as_posix(): [f"{VERSION} Sprint {SPRINT}", f"Pillar {PILLAR_NUMBER}"],
        (_ROOT / "docs" / "mas_tracker.yml").resolve().as_posix(): ["v36_6_sprint_cj:", "  next_pillar_slot: 1085"],
        (_ROOT / "FALLIBILITY.md").resolve().as_posix(): ["Foundation reassessment (2026-09-05)", "action-to-evolution"],
        (_ROOT / "docs" / "CLAIM_MASTER_BOARD.md").resolve().as_posix(): [f"*P{PILLAR_NUMBER} ({VERSION}):", PILLAR_STATUS],
        (_ROOT / "docs" / "GATEKEEPER_SUMMARY.md").resolve().as_posix(): [f"**Sprint {SPRINT} ({VERSION}", f"P{PILLAR_NUMBER}"],
        (_ROOT / "docs" / "TRUTH_LAYER.md").resolve().as_posix(): ["### Sprint CJ orchestration implementation", "Stage A→E benchmark/training progression"],
        (_ROOT / "docs" / "WAVE_CHANGELOG.md").resolve().as_posix(): [f"## {VERSION} (2026-09-07 — Sprint {SPRINT}: Pillar {PILLAR_NUMBER})", "**Next pillar slot:** 1085"],
        (_ROOT / "docs" / "SPRINT_PLAN.md").resolve().as_posix(): ["## SPRINT CJ PARALLEL ORCHESTRATION PROTOCOL", "Historical continuity: v36.6 Sprint CJ"],
        (_ROOT / "9-INFRASTRUCTURE" / "um_live_status.json").resolve().as_posix(): ['"closure_earned": false', '"action_to_evolution"'],
    }
    file_checks = []
    for file_path, required_fragments in checks.items():
        candidate = Path(file_path)
        exists = candidate.is_file()
        read_ok = True
        content = ""
        if exists:
            try:
                content = candidate.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                read_ok = False
        fragments_pass = all(fragment in content for fragment in required_fragments)
        file_checks.append(
            {
                "path": file_path,
                "exists": exists,
                "read_ok": read_ok,
                "required_fragments": list(required_fragments),
                "pass": exists and read_ok and fragments_pass,
            }
        )
    return {
        "all_pass": all(item["pass"] for item in file_checks),
        "files": file_checks,
    }


def sprint_cj_parallel_orchestration() -> Dict[str, Any]:
    foundation = foundation_first_photon_action_audit()
    sprint_ci = sprint_ci_foundation_certificate()

    merlin_program = _load("ox_navigator.engine.merlin_program")
    merlin_benchmark = _load("ox_navigator.engine.merlin_benchmark")

    frontier = _as_dict(_json_safe(merlin_program.get_frontier_readiness_packet(limit=3)))
    benchmark_plan = _as_dict(_json_safe(merlin_benchmark.get_multi_stage_benchmark_plan()))
    corpora = _as_dict(_json_safe(merlin_benchmark.get_benchmark_corpus(stage="all")))
    dual_loop = _as_dict(_json_safe(merlin_program.get_dual_loop_learning_contract()))
    mirrored_cycle = _as_dict(_json_safe(merlin_program.get_mirrored_training_cycle_contract()))
    proof_contract = _as_dict(_json_safe(merlin_program.get_deterministic_proof_closure_contract()))

    stage_rows = benchmark_plan.get("stages")
    stage_list_shape_ok = (
        isinstance(stage_rows, list)
        and len(stage_rows) > 0
        and all(isinstance(row, dict) and isinstance(row.get("stage"), str) for row in stage_rows)
    )
    plan_stages = [row["stage"] for row in stage_rows] if stage_list_shape_ok else []
    frontier_stage_rows = (
        frontier.get("multi_stage_plan", {}).get("stages")
        if isinstance(frontier.get("multi_stage_plan", {}), dict)
        else []
    )
    frontier_stage_list_shape_ok = (
        isinstance(frontier_stage_rows, list)
        and len(frontier_stage_rows) > 0
        and all(isinstance(row, dict) and isinstance(row.get("stage"), str) for row in frontier_stage_rows)
    )
    frontier_stage_sequence = [row["stage"] for row in frontier_stage_rows] if frontier_stage_list_shape_ok else []
    frontier_stage_sequence_ok = frontier_stage_sequence == _EXPECTED_STAGE_SEQUENCE
    raw_promotion_blockers = frontier.get("promotion_blockers")
    promotion_blockers = list(raw_promotion_blockers) if isinstance(raw_promotion_blockers, list) else []
    blockers_all_clear_raw = frontier.get("promotion_blockers_all_clear", None)
    blockers_all_clear_type_ok = blockers_all_clear_raw is None or isinstance(blockers_all_clear_raw, bool)
    blockers_all_clear_declared = blockers_all_clear_raw if isinstance(blockers_all_clear_raw, bool) else None
    promotion_blockers_declared = isinstance(raw_promotion_blockers, list)
    blockers_are_dicts = all(isinstance(item, dict) for item in promotion_blockers)
    blocker_pass_field_types_ok = blockers_are_dicts and all(isinstance(item.get("pass"), bool) for item in promotion_blockers)
    effective_all_clear = blocker_pass_field_types_ok and all(item.get("pass") is True for item in promotion_blockers)
    declared_all_clear_semantics = effective_all_clear
    declared_matches_effective = (
        blockers_all_clear_declared == effective_all_clear
        if blockers_all_clear_declared is not None
        else True
    )
    if blockers_all_clear_declared is None:
        blocker_consistency_pass = (
            blockers_are_dicts
            and blocker_pass_field_types_ok
            and promotion_blockers_declared
            and blockers_all_clear_type_ok
        )
        blockers_all_clear_effective = effective_all_clear
    else:
        blocker_consistency_pass = (
            blockers_are_dicts
            and blocker_pass_field_types_ok
            and promotion_blockers_declared
            and blockers_all_clear_type_ok
            and blockers_all_clear_declared == declared_all_clear_semantics
        )
        blockers_all_clear_effective = effective_all_clear
    policy_text = str(frontier.get("policy", ""))
    policy_normalized = policy_text.lower().replace("-", " ")
    policy_declares_fail_closed = "fail closed" in policy_normalized
    frontier_packet_ok = bool(
        isinstance(frontier, dict)
        and isinstance(frontier.get("sync_checks"), dict)
        and frontier.get("sync_checks", {}).get("ok") is True
        and isinstance(frontier.get("control_tower"), dict)
        and len(frontier.get("control_tower", {})) > 0
        and isinstance(frontier.get("control_tower", {}).get("replacement_readiness"), dict)
        and len(frontier.get("control_tower", {}).get("replacement_readiness", {})) > 0
        and isinstance(frontier.get("control_tower", {}).get("longitudinal_acceptance"), dict)
        and len(frontier.get("control_tower", {}).get("longitudinal_acceptance", {})) > 0
        and isinstance(frontier.get("multi_stage_plan"), dict)
        and frontier_stage_list_shape_ok
        and frontier_stage_sequence_ok
        and promotion_blockers_declared
        and blocker_pass_field_types_ok
        and blockers_all_clear_type_ok
        and policy_declares_fail_closed
    )
    if not frontier_packet_ok or not blocker_consistency_pass:
        promotion_policy_state = "INVALID"
    elif (
        frontier_packet_ok
        and blocker_consistency_pass
        and blockers_all_clear_effective
        and bool(foundation.get("valid"))
        and bool(sprint_ci.get("valid"))
    ):
        promotion_policy_state = "PASS"
    elif not blockers_all_clear_effective:
        promotion_policy_state = "FREEZE"
    else:
        promotion_policy_state = "INVALID"

    promotion_language_gate_pass = promotion_policy_state == "PASS"
    promotion_language_freeze_enforced = promotion_policy_state == "FREEZE"
    corpora_payload = corpora.get("corpora") if isinstance(corpora.get("corpora"), dict) else {}
    corpora_stage_coverage_pass = (
        isinstance(corpora_payload, dict)
        and all(stage in corpora_payload for stage in _EXPECTED_STAGE_SEQUENCE)
        and all(
            isinstance((corpora_payload.get(stage) or {}).get("benchmarks"), list)
            and len((corpora_payload.get(stage) or {}).get("benchmarks") or []) > 0
            for stage in _EXPECTED_STAGE_SEQUENCE
        )
    )
    truth_sync = _truth_surface_sync_status()

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
        "promotion_blockers_all_clear_declared": blockers_all_clear_declared,
        "promotion_blockers_all_clear": blockers_all_clear_effective,
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
            "lane_2_stage_list_shape_ok": stage_list_shape_ok,
            "lane_2_frontier_stage_sequence_ok": frontier_stage_sequence_ok,
            "lane_2_requires_promotion_blockers_declared": promotion_blockers_declared,
            "lane_2_blockers_all_clear_type_ok": blockers_all_clear_type_ok,
            "lane_2_blocker_pass_fields_are_boolean": blocker_pass_field_types_ok,
            "lane_2_declared_all_clear_matches_effective_semantics": declared_matches_effective,
            "lane_2_frontier_packet_ok": frontier_packet_ok,
            "lane_2_blocker_consistency_ok": blocker_consistency_pass,
            "lane_2_requires_nonempty_stage_corpora": corpora_stage_coverage_pass,
            "truth_surfaces_synchronized_to_v36_6": bool(truth_sync.get("all_pass")),
            "promotion_language_gate_pass": promotion_language_gate_pass,
            "promotion_language_freeze_enforced": promotion_language_freeze_enforced,
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
        and stage_list_shape_ok
        and plan_stages == _EXPECTED_STAGE_SEQUENCE
        and frontier_packet_ok
        and blocker_consistency_pass
        and corpora_stage_coverage_pass
        and bool(truth_sync.get("all_pass"))
        and (
            bool(integrated_board["dependencies"]["promotion_language_gate_pass"])
            or bool(integrated_board["dependencies"]["promotion_language_freeze_enforced"])
        )
        and (promotion_language_gate_pass or not blockers_all_clear_effective)
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
        "promotion_policy_state": promotion_policy_state,
        "truth_surface_sync": truth_sync,
        "benchmark_corpora_check": {
            "expected_stages": list(_EXPECTED_STAGE_SEQUENCE),
            "stage_coverage_pass": corpora_stage_coverage_pass,
        },
        "benchmark_corpora_available": sorted(corpora_payload.keys()),
        "proof_first_contract": proof_contract,
        "immediate_execution_order": immediate_execution_order,
        "outcome": "SPRINT_CJ_PARALLEL_ORCHESTRATION_READY" if valid else "SPRINT_CJ_PARALLEL_ORCHESTRATION_BLOCKED",
        "valid": valid,
        "packet_valid": valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(sprint_cj_parallel_orchestration().get("valid"))
        except Exception:
            return False

    def __repr__(self) -> str:
        return str(bool(self))


PILLAR_VALID = _PillarValidProxy()


def pillar1084_summary() -> Dict[str, Any]:
    report = sprint_cj_parallel_orchestration()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CJ Parallel Orchestration",
        "status": PILLAR_STATUS,
        "outcome": report["outcome"],
        "valid": report["valid"],
    }
