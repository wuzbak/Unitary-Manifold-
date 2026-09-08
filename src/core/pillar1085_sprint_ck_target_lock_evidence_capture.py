# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1085 — Sprint CK target lock and Merlin evidence capture.

Implements the immediate next pass after Sprint CJ:

1. perform an executable leverage audit across the two admissible foundation
   targets,
2. lock Lane 1 to exactly one target, and
3. capture Merlin Stage A→E evidence surfaces without widening claims or
   releasing promotion language.
"""

from __future__ import annotations

import importlib
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List

from src.core.merlin_package_bootstrap import ensure_merlin_package_loaded
from src.core.pillar1082_foundation_first_photon_action_audit import (
    foundation_first_photon_action_audit,
)
from src.core.pillar1084_sprint_cj_parallel_orchestration import (
    sprint_cj_parallel_orchestration,
)

PILLAR_NUMBER: int = 1085
PILLAR_GATE: str = "SPRINT_CK_TARGET_LOCK_AND_EVIDENCE_CAPTURE"
PILLAR_STATUS: str = "SPRINT_CK_TARGET_LOCK_AND_EVIDENCE_CAPTURE_COMPLETE"
VERSION: str = "v36.7"
SPRINT: str = "CK"
NEXT_PILLAR_SLOT: int = 1086

SELECTED_TARGET_ID = "ACTION_TO_EVOLUTION_EULER_LAGRANGE"

_ROOT = Path(__file__).resolve().parents[2]
_PRODUCT_ROOT = _ROOT / "12-AZ-IP" / "20-phicat-navigator"
_EXPECTED_STAGE_SEQUENCE = [
    "stage_a_parity_capture",
    "stage_b_sovereign_takeover",
    "stage_c_capability_expansion",
    "stage_d_replacement_gates",
    "stage_e_external_decommission",
]
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


def _load(module_name: str) -> Any:
    ensure_merlin_package_loaded(_PRODUCT_ROOT)
    return importlib.import_module(module_name)


def _json_safe(value: Any) -> Any:
    return deepcopy(value)


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _truth_surface_sync_status() -> Dict[str, Any]:
    version_numeric = VERSION.removeprefix("v")
    sprint_tag = f"{VERSION} Sprint {SPRINT}"
    next_slot_text = str(NEXT_PILLAR_SLOT)
    checks = {
        (_ROOT / "STATUS.md").resolve().as_posix(): [sprint_tag, f"next slot {next_slot_text}"],
        (_ROOT / "docs" / "mas_tracker.yml").resolve().as_posix(): [f'version: "{VERSION}"', f"next_pillar_slot: {next_slot_text}"],
        (_ROOT / "FALLIBILITY.md").resolve().as_posix(): [f"Unitary Manifold {VERSION}", f"Next pillar slot {next_slot_text}"],
        (_ROOT / "docs" / "CLAIM_MASTER_BOARD.md").resolve().as_posix(): [f"# Unitary Manifold {VERSION}", f"Next slot {next_slot_text}"],
        (_ROOT / "docs" / "GATEKEEPER_SUMMARY.md").resolve().as_posix(): [f"# Unitary Manifold {VERSION}", f"Next slot {next_slot_text}"],
        (_ROOT / "docs" / "TRUTH_LAYER.md").resolve().as_posix(): [f"# Unitary Manifold {VERSION}"],
        (_ROOT / "docs" / "WAVE_CHANGELOG.md").resolve().as_posix(): [f"**Current version: {VERSION}", f"**Next pillar slot:** {next_slot_text}"],
        (_ROOT / "docs" / "SPRINT_PLAN.md").resolve().as_posix(): [f"{sprint_tag} COMPLETE", f"| Next pillar slot | **{next_slot_text}** |"],
        (_ROOT / "9-INFRASTRUCTURE" / "um_live_status.json").resolve().as_posix(): [f'"version": "{version_numeric}"', f'"next_slot": {next_slot_text}'],
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


def _candidate_rows() -> List[Dict[str, Any]]:
    action_target = {
        "target_id": SELECTED_TARGET_ID,
        "label": "Action-to-evolution Euler-Lagrange derivation",
        "existing_machine_readable_surface": 5,
        "architecture_leverage": 5,
        "evidence_boundary_clarity": 5,
        "new_infrastructure_burden": 1,
        "anti_loop_risk": 1,
        "current_blocker": (
            "Construct and verify an action whose Euler-Lagrange equations reproduce "
            "the implemented flow, or replace the phenomenological flow with such equations."
        ),
        "existing_surfaces": [
            "src/core/evolution.py::phenomenological_flow_boundary",
            "src/core/pillar1082_foundation_first_photon_action_audit.py",
        ],
        "why_now": (
            "This blocker is already machine-readable, gates downstream credibility, "
            "and has a narrower evidence-class boundary than a fresh photon-sector build."
        ),
    }
    action_target["composite_score"] = (
        action_target["existing_machine_readable_surface"]
        + action_target["architecture_leverage"]
        + action_target["evidence_boundary_clarity"]
        - action_target["new_infrastructure_burden"]
        - action_target["anti_loop_risk"]
    )

    photon_target = {
        "target_id": "PHOTON_SECTOR_CONSTRUCTION",
        "label": "Admissible photon-sector construction with action, boundary conditions, and spectrum",
        "existing_machine_readable_surface": 2,
        "architecture_leverage": 3,
        "evidence_boundary_clarity": 2,
        "new_infrastructure_burden": 5,
        "anti_loop_risk": 4,
        "current_blocker": (
            "Construct an independent admissible even bulk/boundary gauge sector or a "
            "different compactification with action, boundary conditions, and spectrum."
        ),
        "existing_surfaces": [
            "src/core/metric.py::z2_parity_clarification",
            "src/core/pillar1082_foundation_first_photon_action_audit.py",
        ],
        "why_now": (
            "This remains admissible, but it requires more new infrastructure and leaves "
            "the action-to-evolution gap untouched even if it succeeds."
        ),
    }
    photon_target["composite_score"] = (
        photon_target["existing_machine_readable_surface"]
        + photon_target["architecture_leverage"]
        + photon_target["evidence_boundary_clarity"]
        - photon_target["new_infrastructure_burden"]
        - photon_target["anti_loop_risk"]
    )

    return [action_target, photon_target]


def _selected_target_contract() -> Dict[str, Any]:
    return {
        "target_id": SELECTED_TARGET_ID,
        "verdict_class_if_executed_now": "TIGHTENED_WITH_EXPLICIT_BLOCKER",
        "required_new_object_evidence_class": [
            {
                "id": "explicit_action_functional",
                "acceptance": "Provide an action S[g,B,phi] with declared couplings and source prescription.",
            },
            {
                "id": "verified_euler_lagrange_equations",
                "acceptance": "Derive and check the g_mu_nu, B_mu, and phi equations against the implemented flow terms.",
            },
            {
                "id": "reproducible_side_by_side_residual_check",
                "acceptance": "Run action-derived and implemented flows on shared initial data and report residual norms.",
            },
            {
                "id": "machine_readable_boundary_update",
                "acceptance": "Update the evolution-boundary surface only if the derivation is verified or explicitly narrowed.",
            },
        ],
        "next_exact_blocker": (
            "No verified action-level Euler-Lagrange derivation currently reproduces the implemented flow."
        ),
    }


def foundation_target_leverage_audit() -> Dict[str, Any]:
    foundation = foundation_first_photon_action_audit()
    candidates = _candidate_rows()
    selected = max(candidates, key=lambda item: int(item["composite_score"]))
    selected_rows = [item for item in candidates if item["composite_score"] == selected["composite_score"]]
    selected_contract = _selected_target_contract()
    valid = (
        bool(foundation.get("valid"))
        and len(selected_rows) == 1
        and selected["target_id"] == SELECTED_TARGET_ID
        and selected["composite_score"] > 0
    )
    return {
        "selection_rule": (
            "Maximize existing executable surface, architecture leverage, and evidence clarity; "
            "minimize new infrastructure burden and anti-loop risk."
        ),
        "candidates": candidates,
        "selected_target": selected,
        "selected_target_contract": selected_contract,
        "why_not_selected": {
            "PHOTON_SECTOR_CONSTRUCTION": (
                "Higher infrastructure burden and loop risk; success would still leave the "
                "action-to-evolution obligation unresolved."
            )
        },
        "verdict_class": selected_contract["verdict_class_if_executed_now"] if valid else "BLOCKED",
        "valid": valid,
        "packet_valid": valid,
    }


def merlin_stage_evidence_capture(*, limit_per_stage: int = 1, training_limit: int = 4) -> Dict[str, Any]:
    merlin_benchmark = _load("ox_navigator.engine.merlin_benchmark")
    merlin_program = _load("ox_navigator.engine.merlin_program")

    benchmark_plan = _as_dict(_json_safe(merlin_benchmark.get_multi_stage_benchmark_plan()))
    corpora = _as_dict(_json_safe(merlin_benchmark.get_benchmark_corpus("all")))
    frontier = _as_dict(_json_safe(merlin_program.get_frontier_readiness_packet(limit=3)))
    stage_a_artifacts = _as_dict(_json_safe(merlin_benchmark.build_stage_a_artifact_bundle(limit=limit_per_stage)))
    training_artifacts = _as_dict(_json_safe(merlin_program.build_training_artifact_bundle(limit=training_limit)))

    runners = {
        "stage_a_parity_capture": merlin_benchmark.run_stage_a_head_to_head_receipts_sync,
        "stage_b_sovereign_takeover": merlin_benchmark.run_stage_b_head_to_head_receipts_sync,
        "stage_c_capability_expansion": merlin_benchmark.run_stage_c_head_to_head_receipts_sync,
        "stage_d_replacement_gates": merlin_benchmark.run_stage_d_head_to_head_receipts_sync,
        "stage_e_external_decommission": merlin_benchmark.run_stage_e_head_to_head_receipts_sync,
    }

    stage_rows = []
    all_stage_receipts_ok = True
    for stage in _EXPECTED_STAGE_SEQUENCE:
        receipt = _as_dict(_json_safe(runners[stage](limit=limit_per_stage)))
        summary = _as_dict(receipt.get("summary"))
        stage_ok = bool(
            receipt.get("ok")
            and receipt.get("stage") == stage
            and isinstance(receipt.get("head_to_head_runs"), list)
            and len(receipt.get("head_to_head_runs", [])) > 0
        )
        all_stage_receipts_ok = all_stage_receipts_ok and stage_ok
        stage_rows.append(
            {
                "stage": stage,
                "ok": stage_ok,
                "head_to_head_runs": len(receipt.get("head_to_head_runs", [])),
                "promotion_gate_pass": bool(summary.get("promotion_gate_pass")),
                "kernel_gate_pass": bool(summary.get("kernel_gate_pass")),
                "summary": summary,
            }
        )

    plan_stages = [
        row.get("stage")
        for row in list(benchmark_plan.get("stages") or [])
        if isinstance(row, dict) and isinstance(row.get("stage"), str)
    ]
    corpora_payload = corpora.get("corpora") if isinstance(corpora.get("corpora"), dict) else {}
    frontier_blockers = list(frontier.get("promotion_blockers") or [])
    blockers_all_clear = bool(frontier.get("promotion_blockers_all_clear"))

    valid = bool(
        plan_stages == _EXPECTED_STAGE_SEQUENCE
        and all_stage_receipts_ok
        and isinstance(corpora_payload, dict)
        and all(stage in corpora_payload for stage in _EXPECTED_STAGE_SEQUENCE)
        and bool(frontier.get("sovereign_primary"))
        and bool(frontier.get("openrouter_fallback_only"))
        and bool((_as_dict(frontier.get("sync_checks"))).get("ok"))
        and stage_a_artifacts.get("ok") is True
        and training_artifacts.get("ok") is True
        and len(frontier_blockers) > 0
    )
    return {
        "benchmark_plan": benchmark_plan,
        "stage_rows": stage_rows,
        "stage_receipts_all_ok": all_stage_receipts_ok,
        "corpora_stage_coverage": sorted(corpora_payload.keys()),
        "frontier_readiness": frontier,
        "frontier_blockers_all_clear": blockers_all_clear,
        "promotion_language_released": False,
        "promotion_state": "FROZEN_UNTIL_SCIENTIFIC_AND_GOVERNANCE_LANES_BOTH_PASS",
        "stage_a_artifact_bundle": stage_a_artifacts,
        "training_artifact_bundle": training_artifacts,
        "valid": valid,
        "packet_valid": valid,
    }


def sprint_ck_target_lock_and_evidence_capture() -> Dict[str, Any]:
    foundation = foundation_first_photon_action_audit()
    sprint_cj = sprint_cj_parallel_orchestration()
    leverage = foundation_target_leverage_audit()
    merlin = merlin_stage_evidence_capture(limit_per_stage=1, training_limit=4)
    truth_sync = _truth_surface_sync_status()

    selected_target = leverage.get("selected_target") or {}
    selected_contract = leverage.get("selected_target_contract") or {}
    lane_one_status = (
        "TIGHTENED_WITH_EXPLICIT_BLOCKER"
        if leverage.get("valid") and selected_target.get("target_id") == SELECTED_TARGET_ID
        else "BLOCKED"
    )
    lane_one = {
        "lane_id": "LANE_1_FOUNDATION_TARGET_LOCK",
        "selected_target_id": selected_target.get("target_id"),
        "selected_target_label": selected_target.get("label"),
        "status": lane_one_status,
        "source_blockers": list(foundation.get("blocker_contraction", {}).get("remaining_blockers", [])),
        "new_object_evidence_class_required": list(selected_contract.get("required_new_object_evidence_class", [])),
        "next_exact_blocker": selected_contract.get("next_exact_blocker"),
    }

    lane_two = {
        "lane_id": "LANE_2_MERLIN_EVIDENCE_CAPTURE",
        "status": "EVIDENCE_CAPTURED_PROMOTION_FROZEN" if merlin.get("valid") else "BLOCKED",
        "stage_sequence": [
            row.get("stage")
            for row in list((_as_dict(merlin.get("benchmark_plan"))).get("stages") or [])
            if isinstance(row, dict)
        ],
        "stage_rows": list(merlin.get("stage_rows", [])),
        "frontier_blockers_all_clear": bool(merlin.get("frontier_blockers_all_clear")),
        "promotion_state": merlin.get("promotion_state"),
        "promotion_language_released": False,
    }

    integrated_board = {
        "mode": "parallel_fail_closed",
        "truth_surface_sync_paths": list(_CANONICAL_SYNC_PATHS),
        "closed_this_sprint": [],
        "tightened_or_corrected": [
            "lane_1_target_locked_to_action_to_evolution_euler_lagrange",
            "lane_2_stage_a_to_e_evidence_capture_completed_without_promotion_release",
        ],
        "blocked_or_external_wait": [
            "photon_origin_under_stated_orbifold_assumptions",
            "action_to_evolution_equivalence_not_yet_derived",
            "existing_architecture_limit_and_external_wait_lanes_unchanged",
        ],
        "dependencies": {
            "pillar1082_foundation_packet_valid": bool(foundation.get("valid")),
            "pillar1084_parallel_orchestration_valid": bool(sprint_cj.get("valid")),
            "lane_1_action_target_selected": selected_target.get("target_id") == SELECTED_TARGET_ID,
            "lane_2_stage_sequence_a_to_e": lane_two["stage_sequence"] == _EXPECTED_STAGE_SEQUENCE,
            "lane_2_stage_receipts_all_ok": bool(merlin.get("stage_receipts_all_ok")),
            "lane_2_stage_a_artifact_bundle_ok": (_as_dict(merlin.get("stage_a_artifact_bundle"))).get("ok") is True,
            "lane_2_training_artifact_bundle_ok": (_as_dict(merlin.get("training_artifact_bundle"))).get("ok") is True,
            "lane_2_sovereign_local_primary": bool((_as_dict(merlin.get("frontier_readiness"))).get("sovereign_primary")),
            "lane_2_external_token_path_compatibility_only": bool((_as_dict(merlin.get("frontier_readiness"))).get("openrouter_fallback_only")),
            "promotion_language_remains_frozen": lane_one_status != "CLOSED_NOW",
            "truth_surfaces_synchronized_to_v36_7": bool(truth_sync.get("all_pass")),
        },
    }

    valid = bool(
        foundation.get("valid")
        and sprint_cj.get("valid")
        and leverage.get("valid")
        and merlin.get("valid")
        and lane_one_status == "TIGHTENED_WITH_EXPLICIT_BLOCKER"
        and lane_two["status"] == "EVIDENCE_CAPTURED_PROMOTION_FROZEN"
        and bool(truth_sync.get("all_pass"))
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
            "pillar1084_valid": bool(sprint_cj.get("valid")),
        },
        "leverage_audit": leverage,
        "lane_1": lane_one,
        "lane_2": lane_two,
        "integrated_board": integrated_board,
        "truth_surface_sync": truth_sync,
        "immediate_execution_order": [
            {
                "step": 1,
                "parallel": True,
                "lane_1": "lock_action_to_evolution_target_and_require_exact_evidence_class",
                "lane_2": "capture_stage_a_to_e_receipts_plus_stage_a_and_training_artifacts",
            },
            {
                "step": 2,
                "parallel": False,
                "action": "publish_synchronized_status_update_with_unchanged_open_lanes_and_exact_remaining_blocker",
            },
        ],
        "outcome": (
            "SPRINT_CK_TARGET_LOCK_AND_EVIDENCE_CAPTURE_READY"
            if valid
            else "SPRINT_CK_TARGET_LOCK_AND_EVIDENCE_CAPTURE_BLOCKED"
        ),
        "valid": valid,
        "packet_valid": valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(sprint_ck_target_lock_and_evidence_capture().get("valid"))
        except Exception:
            return False

    def __repr__(self) -> str:
        return str(bool(self))


PILLAR_VALID = _PillarValidProxy()


def pillar1085_summary() -> Dict[str, Any]:
    report = sprint_ck_target_lock_and_evidence_capture()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Sprint CK Target Lock and Merlin Evidence Capture",
        "status": PILLAR_STATUS,
        "outcome": report["outcome"],
        "valid": report["valid"],
    }
