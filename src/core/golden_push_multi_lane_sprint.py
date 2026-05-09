# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Machine-readable golden-push orchestration for the post-v10.32 sprint.

This module operationalizes the requested "golden push" as a strict command
layer over the current locked state:
  - ToE score fixed at 21.5 / 28 (v10.32: P16 promoted CONSTRAINED→GEOMETRIC_PREDICTION),
  - no softened falsifiers,
  - no promotion by rhetoric.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Dict, List

from src.core.alpha_gw_10d_uv_completion import full_10d_uv_closure_report
from src.core.alpha_gw_uv_brane_derivation import alpha_gw_gap_closure_verdict
from src.core.cc_gap_precision_audit import p28_promotion_evaluation, verify_layer1_gap
from src.core.finish_line_command_structure import p16_finish_line_hardgate
from src.core.finish_line_observation_engine import route_finish_line_observation_bundle
from src.core.five_tier_execution_framework import FULL_REGRESSION_GATE_COMMAND
from src.core.neutrino_orbifold_branch_policy import neutrino_branch_policy
from src.core.toe_90_pathway import toe_90_pathway_verdict

__all__ = [
    "PROGRAMME_VERSION",
    "PROGRAMME_DATE",
    "CURRENT_TOE_SCORE",
    "TOTAL_TOE_SCORE",
    "TARGET_90_SCORE",
    "CANONICAL_TRUTH_SURFACES",
    "LANE_ORDER",
    "LANE_REGISTRY",
    "PHASE_SEQUENCE",
    "ACCEPTED_LANE_OUTCOMES",
    "list_lanes",
    "get_lane",
    "command_baseline",
    "list_phases",
    "highest_priority_scientific_pushes",
    "scorecard_strategy",
    "observation_falsification_operations",
    "integration_discipline",
    "lane_status_snapshot",
    "golden_push_sprint_board",
    "golden_push_release_decision",
]

PROGRAMME_VERSION: str = "v10.32"
PROGRAMME_DATE: str = "2026-05-09"

CURRENT_TOE_SCORE: float = 21.5
TOTAL_TOE_SCORE: float = 28.0
TARGET_90_SCORE: float = 25.2

CANONICAL_TRUTH_SURFACES: List[str] = [
    "docs/mas_tracker.yml",
    "docs/WAVE_CHANGELOG.md",
    "docs/CLAIM_MASTER_BOARD.md",
    "docs/TOE_SCORE_AUDIT.md",
]

LANE_ORDER: List[str] = [
    "Lane A",
    "Lane B",
    "Lane C",
    "Lane D",
    "Lane E",
    "Lane F",
    "Lane G",
]

LANE_REGISTRY: Dict[str, Dict[str, object]] = {
    "Lane A": {
        "title": "P16 closure attempt",
        "scope": "Attempt exact '+52' closure; if not possible, sharpen blocker map.",
        "owner_role": "P16 hardgate owner",
        "target_parameter": "P16",
    },
    "Lane B": {
        "title": "P26 branch closure",
        "scope": "Keep minimal-5D and UV-extended neutrino branches explicit and non-mixed.",
        "owner_role": "Neutrino branch owner",
        "target_parameter": "P26",
    },
    "Lane C": {
        "title": "P27/P28 architecture deepening",
        "scope": "Deepen architecture closure path without overclaiming promotion.",
        "owner_role": "Architecture frontier owner",
        "target_parameters": ["P27", "P28"],
    },
    "Lane D": {
        "title": "α_GW / CMB tension closure support",
        "scope": "Maintain 10D hardgate closure while preserving the retained 5D limitation note.",
        "owner_role": "Amplitude-tension owner",
        "target": "alpha_GW",
    },
    "Lane E": {
        "title": "Observation and falsification readiness",
        "scope": "Keep DESI/JUNO/Hyper-K/CMB-S4/LiteBIRD/LISA routing same-day ready.",
        "owner_role": "Observation routing owner",
    },
    "Lane F": {
        "title": "GP→DERIVED promotion scouting",
        "scope": "Rank realistic GP→DERIVED candidates by shared mechanism packages.",
        "owner_role": "Score frontier owner",
        "target": "ToE frontier",
    },
    "Lane G": {
        "title": "Regression, integration, and truth-sync",
        "scope": "Keep test baseline green and canonical truth surfaces synchronized.",
        "owner_role": "Integration lead",
    },
}

PHASE_SEQUENCE: List[Dict[str, object]] = [
    {
        "phase": "Phase 1",
        "title": "Baseline refresh and lane assignment",
        "deliverables": [
            "reconfirm_regression_green",
            "fix_lane_owners",
            "define_hardgate_exit_criteria",
        ],
        "focus_lanes": ["Lane G"],
    },
    {
        "phase": "Phase 2",
        "title": "Primary closure attacks",
        "deliverables": [
            "p16_closure_attempt_or_blocker_map",
            "p26_branch_criteria_hardening",
            "parallel_p27_p28_alpha_gw_frontier_push",
        ],
        "focus_lanes": ["Lane A", "Lane B", "Lane C", "Lane D"],
    },
    {
        "phase": "Phase 3",
        "title": "GP→DERIVED scouting in parallel",
        "deliverables": [
            "ranked_gp_to_derived_queue",
            "shared_mechanism_upgrade_packages",
        ],
        "focus_lanes": ["Lane F"],
    },
    {
        "phase": "Phase 4",
        "title": "Integration of auditable artifacts",
        "deliverables": [
            "merge_only_auditable_artifacts",
            "record_frontier_ledgers_without_overclaim",
        ],
        "focus_lanes": ["Lane G"],
    },
    {
        "phase": "Phase 5",
        "title": "Final truth-sync and release-quality review",
        "deliverables": [
            "truth_surface_sync",
            "full_regression_gate",
            "go_no_go_review",
        ],
        "focus_lanes": ["Lane E", "Lane G"],
    },
]

ACCEPTED_LANE_OUTCOMES: List[str] = [
    "PROMOTED",
    "NARROWED_HONESTLY",
    "BLOCKER_CLARIFIED",
]


def list_lanes() -> List[str]:
    """Return the fixed 7-lane order for the golden push."""
    return list(LANE_ORDER)


def get_lane(lane_id: str) -> Dict[str, object]:
    """Return one lane specification."""
    if lane_id not in LANE_REGISTRY:
        raise KeyError(f"Unknown lane: {lane_id!r}. Available: {LANE_ORDER}")
    return deepcopy(LANE_REGISTRY[lane_id])


def list_phases() -> List[Dict[str, object]]:
    """Return the fixed 5-phase sprint sequence."""
    return deepcopy(PHASE_SEQUENCE)


def command_baseline() -> Dict[str, object]:
    """Return baseline locks that must remain true throughout the sprint."""
    p16 = p16_finish_line_hardgate()
    return {
        "toe_score": {
            "current": CURRENT_TOE_SCORE,
            "total": TOTAL_TOE_SCORE,
            "target_90pct": TARGET_90_SCORE,
        },
        "status_lock": {
            "p16": p16["current_status"],
            "p26": "CONSTRAINED",
            "p27": "ARCHITECTURE_LIMIT_CERTIFIED",
            "p28": "ARCHITECTURE_LIMIT_CERTIFIED",
            "alpha_gw": "CLOSED_WITH_10D_HARDGATE_BENCHMARK",
        },
        "canonical_truth_surfaces": list(CANONICAL_TRUTH_SURFACES),
        "regression_gate_command": FULL_REGRESSION_GATE_COMMAND,
        "no_overclaim_policy": {
            "score_lift_without_hardgate": False,
            "promotion_without_hardgate": False,
            "falsifier_softening_allowed": False,
        },
    }


def highest_priority_scientific_pushes() -> Dict[str, Dict[str, object]]:
    """Return the top scientific pushes and their honest exit rules."""
    return {
        "P16": {
            "objective": "exact_plus52_wsiii_closure",
            "fallback": "convert_failure_to_clean_blocker_map",
            "accepted_outcomes": list(ACCEPTED_LANE_OUTCOMES),
        },
        "P26": {
            "objective": "explicit_branch_selection_criteria",
            "guardrail": "no_implicit_branch_mixing",
            "accepted_outcomes": list(ACCEPTED_LANE_OUTCOMES),
        },
        "P27": {
            "objective": "genuine_5d_strong_cp_closure_or_tighter_architecture_limit",
            "accepted_outcomes": list(ACCEPTED_LANE_OUTCOMES),
        },
        "P28": {
            "objective": "deepen_10d_11d_landscape_argument_beyond_n_flux_37",
            "honest_gap_reference": "10^57.26",
            "accepted_outcomes": list(ACCEPTED_LANE_OUTCOMES),
        },
        "alpha_gw": {
            "objective": "bound_or_derive_uv_brane_missing_ingredient",
            "accepted_outcomes": list(ACCEPTED_LANE_OUTCOMES),
        },
    }


def scorecard_strategy() -> Dict[str, object]:
    """Return score strategy rules for the golden push."""
    toe90 = toe_90_pathway_verdict()
    return {
        "rule": "chase_hardgates_not_rhetoric",
        "near_term_honest_closers": ["P26", "P27", "P28"],
        "closed_in_v10_32": ["P16"],
        "second_track_required": True,
        "gp_to_derived_queue_required": True,
        "target_90_requires_both_tracks": True,
        "toe90_verdict": toe90["status"],
        "required_delta_to_90": toe90["required_delta"],
    }


def observation_falsification_operations() -> Dict[str, object]:
    """Return observation-routing posture and protected falsifier set."""
    routed = route_finish_line_observation_bundle()
    return {
        "same_day_ready": True,
        "tracked_experiments": [
            "DESI",
            "JUNO",
            "Hyper-K",
            "CMB-S4",
            "LiteBIRD",
            "LISA",
        ],
        "protected_falsifiers": [
            "LiteBIRD beta window and inter-sector gap",
            "JUNO P17 precision risk",
            "DESI frozen-radion w_a = 0 risk",
            "CMB-S4 r threshold risk",
        ],
        "routing_snapshot": {
            "desi": routed["results"]["desi"]["current_status"],
            "juno": routed["results"]["juno"]["route"],
            "hyperk": routed["results"]["hyperk"]["route"],
            "cmbs4": routed["results"]["cmbs4"]["route"],
            "litebird": routed["results"]["litebird"]["route"],
        },
    }


def integration_discipline() -> Dict[str, object]:
    """Return integration rules that govern all lane merges."""
    return {
        "allowed_lane_outcomes": list(ACCEPTED_LANE_OUTCOMES),
        "merge_rule": "merge_only_with_regression_green_and_truth_sync",
        "post_batch_required_updates": list(CANONICAL_TRUTH_SURFACES),
        "release_quality_review_required": True,
    }


def lane_status_snapshot() -> Dict[str, Dict[str, object]]:
    """Return a live status snapshot for lanes A-G."""
    p16 = p16_finish_line_hardgate()
    p26 = neutrino_branch_policy()
    p28 = p28_promotion_evaluation()
    p28_gap = verify_layer1_gap()
    alpha = alpha_gw_gap_closure_verdict()
    alpha_10d = full_10d_uv_closure_report()
    alpha_closed = alpha_10d["step8_decision"]["status"] == "CLOSED"
    return {
        "Lane A": {
            "parameter": "P16",
            "promotion_allowed": p16["promotion_allowed"],
            "status": p16["current_status"],
            "decision": p16["decision"],
            "blocking_dependency": p16["blocking_dependency"],
        },
        "Lane B": {
            "parameter": "P26",
            "status": "CONSTRAINED",
            "policy_status": p26["status"],
            "runtime_branch": p26["canonical_runtime_branch"],
        },
        "Lane C": {
            "parameter": "P28",
            "status": p28["current_status"],
            "promotion_allowed": p28["can_promote"],
            "residual_gap_log10": p28_gap["residual_log10"],
        },
        "Lane D": {
            "target": "alpha_gw",
            "status": (
                "CLOSED_WITH_10D_HARDGATE_BENCHMARK"
                if alpha_closed
                else alpha["status"]
            ),
            "missing_ingredient": alpha["missing_ingredient"],
            "benchmark_prediction": alpha_10d["step6_match"]["alpha_gw_predicted"],
        },
        "Lane E": {
            "target": "observation_readiness",
            "status": "READY",
        },
        "Lane F": {
            "target": "gp_to_derived_scouting",
            "status": "REQUIRED",
        },
        "Lane G": {
            "target": "integration_and_truth_sync",
            "status": "MANDATORY",
        },
    }


def golden_push_sprint_board() -> Dict[str, object]:
    """Return the full golden-push orchestration board."""
    return {
        "programme_version": PROGRAMME_VERSION,
        "programme_date": PROGRAMME_DATE,
        "command_baseline": command_baseline(),
        "lane_order": list_lanes(),
        "lane_registry": deepcopy(LANE_REGISTRY),
        "phase_sequence": list_phases(),
        "highest_priority_pushes": highest_priority_scientific_pushes(),
        "scorecard_strategy": scorecard_strategy(),
        "observation_falsification_operations": observation_falsification_operations(),
        "integration_discipline": integration_discipline(),
        "lane_status_snapshot": lane_status_snapshot(),
        "success_condition": {
            "best_case": (
                "One or more of P16/P26/P27/P28 materially advances or closes "
                "with hardgate evidence."
            ),
            "minimum_acceptable": (
                "Every remaining gap is narrowed into a sharper machine-auditable "
                "blocker without loss of falsifier integrity."
            ),
            "non_negotiables": [
                "zero_regression_failures",
                "no_score_inflation",
                "no_status_promotion_without_hardgate",
            ],
        },
    }


def golden_push_release_decision(
    regression_green: bool,
    truth_sync_complete: bool,
) -> Dict[str, object]:
    """Return GO/NO_GO decision for the golden-push integration checkpoint."""
    go = regression_green and truth_sync_complete
    return {
        "programme_version": PROGRAMME_VERSION,
        "regression_green": regression_green,
        "truth_sync_complete": truth_sync_complete,
        "go_no_go": "GO" if go else "NO_GO",
        "required_condition": "both_regression_green_and_truth_sync_complete",
        "score_change": 0.0,
        "status_changes": [],
    }
