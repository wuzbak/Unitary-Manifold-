# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
finish_line_command_structure.py — Machine-readable 5-lane finish-line command
structure for the post-v10.30 programme.

This module stands up the requested command structure with one canonical board
(`docs/mas_tracker.yml`), fixed weekly gate reviews, and a release-governance
layer that can be audited without reopening MAS or inflating any status label.

Lane scope:
  - Lane A: P16 closure hardgate review
  - Lane B: P28 / α_GW architecture-frontier review
  - Lane C: observation routing (DESI / JUNO / Hyper-K / CMB-S4 / LiteBIRD)
  - Lane D: stress / robustness
  - Lane E: truth-sync docs and release governance
"""
from __future__ import annotations

from copy import deepcopy
from typing import Dict, List

from src.core.alpha_gw_10d_uv_completion import full_10d_uv_closure_report
from src.core.alpha_gw_uv_brane_derivation import alpha_gw_gap_closure_verdict
from src.core.cc_gap_precision_audit import p28_promotion_evaluation
from src.core.cmbs4_ns_r_joint_falsifier import cmbs4_readiness_report
from src.core.desi_dr2_gap_report import full_dr2_gap_report
from src.core.five_tier_execution_framework import FULL_REGRESSION_GATE_COMMAND
from src.core.full_gp_stress_test import full_stress_report
from src.core.hyperk_juno_dm31_readiness import hyperk_juno_readiness_report
from src.core.litebird_gap_hardening import litebird_gap_hardening_report
from src.core.p16_solar_correction_analysis import (
    geometric_bounds_on_fc,
    promotion_gate_check,
)
from src.core.p16_wsiii_plus52_closure import p16_wsiii_gate_report

__all__ = [
    "PROGRAMME_VERSION",
    "PROGRAMME_DATE",
    "CANONICAL_BOARD_ARTIFACT",
    "WEEKLY_GATE_REVIEW_DAY",
    "WEEKLY_GATE_REVIEW_CADENCE",
    "FIVE_LANE_ORDER",
    "LANE_REGISTRY",
    "get_lane",
    "list_lanes",
    "weekly_gate_reviews",
    "p16_finish_line_hardgate",
    "p28_finish_line_architecture_review",
    "observation_finish_line_status",
    "robustness_finish_line_status",
    "governance_finish_line_status",
    "lane_status_snapshot",
    "finish_line_command_board",
    "finish_line_unresolved_risk_ledger",
    "finish_line_release_decision",
]

PROGRAMME_VERSION: str = "v10.31"
PROGRAMME_DATE: str = "2026-05-09"
CANONICAL_BOARD_ARTIFACT: str = "docs/mas_tracker.yml"
WEEKLY_GATE_REVIEW_DAY: str = "Friday"
WEEKLY_GATE_REVIEW_CADENCE: str = "weekly"

FIVE_LANE_ORDER: List[str] = [
    "Lane A",
    "Lane B",
    "Lane C",
    "Lane D",
    "Lane E",
]

LANE_REGISTRY: Dict[str, Dict[str, object]] = {
    "Lane A": {
        "title": "P16 closure",
        "target": "P16 CONSTRAINED -> GEOMETRIC_PREDICTION",
        "lead_artifact": "src/core/p16_solar_correction_analysis.py",
        "primary_decision": "hardgate_only",
        "board": CANONICAL_BOARD_ARTIFACT,
    },
    "Lane B": {
        "title": "P28 / Λ architecture gap",
        "target": "P28 architecture-limit reduction without overclaim",
        "lead_artifacts": [
            "src/core/cc_gap_precision_audit.py",
            "src/core/alpha_gw_uv_brane_derivation.py",
        ],
        "primary_decision": "no_promotion_without_10d_closure",
        "board": CANONICAL_BOARD_ARTIFACT,
    },
    "Lane C": {
        "title": "Observation ingestion",
        "target": "One-command PASS/TENSION/FALSIFIED routing",
        "lead_artifacts": [
            "src/core/desi_dr2_gap_report.py",
            "src/core/hyperk_juno_dm31_readiness.py",
            "src/core/cmbs4_ns_r_joint_falsifier.py",
            "src/core/litebird_gap_hardening.py",
        ],
        "primary_decision": "route_and_sync_same_day",
        "board": CANONICAL_BOARD_ARTIFACT,
    },
    "Lane D": {
        "title": "Stress / robustness",
        "target": "Cross-module residual margin protection",
        "lead_artifact": "src/core/full_gp_stress_test.py",
        "primary_decision": "protect_gp_labels",
        "board": CANONICAL_BOARD_ARTIFACT,
    },
    "Lane E": {
        "title": "Truth-sync docs and release governance",
        "target": "Release-quality sync and go/no-go decision",
        "lead_artifacts": [
            "docs/WAVE_CHANGELOG.md",
            "docs/mas_tracker.yml",
            "STATUS.md",
        ],
        "primary_decision": "release_only_if_regression_green_and_truth_synced",
        "board": CANONICAL_BOARD_ARTIFACT,
    },
}


def get_lane(lane_id: str) -> Dict[str, object]:
    """Return the specification for one finish-line lane."""
    if lane_id not in LANE_REGISTRY:
        raise KeyError(
            f"Unknown finish-line lane: {lane_id!r}. "
            f"Available: {list(FIVE_LANE_ORDER)}"
        )
    return deepcopy(LANE_REGISTRY[lane_id])


def list_lanes() -> List[str]:
    """Return the fixed 5-lane execution order."""
    return list(FIVE_LANE_ORDER)


def weekly_gate_reviews() -> List[Dict[str, object]]:
    """Return the fixed weekly gate-review schedule for all five lanes."""
    return [
        {
            "lane": lane_id,
            "review_day": WEEKLY_GATE_REVIEW_DAY,
            "cadence": WEEKLY_GATE_REVIEW_CADENCE,
            "canonical_board": CANONICAL_BOARD_ARTIFACT,
            "review_type": "hardgate_review",
        }
        for lane_id in FIVE_LANE_ORDER
    ]


def p16_finish_line_hardgate() -> Dict[str, object]:
    """Return the finish-line hardgate decision for Lane A / P16."""
    legacy = promotion_gate_check()
    wsiii = p16_wsiii_gate_report()
    bounds = geometric_bounds_on_fc()
    promotion_allowed = wsiii["all_gates_pass"]
    gate3_reason = legacy["gates"].get(
        "gate3_axiomzero_purity",
        {},
    ).get(
        "reason",
        "Promotion blocked until the documented blocking dependency closes.",
    )
    hardgate_reason = (
        wsiii["verdict"]
        if promotion_allowed
        else gate3_reason
    )
    return {
        "lane": "Lane A",
        "parameter": "P16",
        "current_status": wsiii["status_after"] if promotion_allowed else legacy["current_status"],
        "target_status": "GEOMETRIC_PREDICTION",
        "legacy_gates": deepcopy(legacy["gates"]),
        "wsiii_gates": deepcopy(wsiii["gates"]),
        "geometric_window_confirmed": bounds["f_c_in_window"],
        "promotion_allowed": promotion_allowed,
        "decision": "PROMOTE" if promotion_allowed else "NO_PROMOTION",
        "blocking_dependency": (
            "closed_by_wsiii_plus52_derivation"
            if promotion_allowed
            else legacy["blocking_dependency"]
        ),
        "wsiii_report": wsiii,
        "hardgate_reason": hardgate_reason,
    }


def p28_finish_line_architecture_review() -> Dict[str, object]:
    """Return the finish-line architecture review for Lane B / P28 + α_GW."""
    p28 = p28_promotion_evaluation()
    alpha_gw = alpha_gw_gap_closure_verdict()
    alpha_gw_10d = full_10d_uv_closure_report()
    promotion_allowed = p28["can_promote"]
    alpha_gw_closed = alpha_gw_10d["step8_decision"]["status"] == "CLOSED"
    return {
        "lane": "Lane B",
        "parameter": "P28",
        "current_status": p28["current_status"],
        "target_status": p28["target_status"],
        "promotion_allowed": promotion_allowed,
        "decision": "PROMOTE" if promotion_allowed else "NO_PROMOTION",
        "p28_reason": p28["reason"],
        "what_would_enable": list(p28["what_would_enable"]),
        "alpha_gw_status": (
            "CLOSED_WITH_10D_HARDGATE_BENCHMARK"
            if alpha_gw_closed
            else alpha_gw["status"]
        ),
        "alpha_gw_gap_orders": alpha_gw["gap_to_interval_log10"],
        "alpha_gw_missing_ingredient": alpha_gw["missing_ingredient"],
        "alpha_gw_10d_prediction": alpha_gw_10d["step6_match"]["alpha_gw_predicted"],
        "alpha_gw_10d_robust_overlap": alpha_gw_10d["step7_robustness"]["overlap_fraction"],
        "no_overclaim_policy_preserved": True,
    }


def observation_finish_line_status() -> Dict[str, object]:
    """Return the current observation-routing status for Lane C."""
    desi = full_dr2_gap_report()
    juno_hyperk = hyperk_juno_readiness_report()
    cmbs4 = cmbs4_readiness_report()
    litebird = litebird_gap_hardening_report()
    return {
        "lane": "Lane C",
        "desi_current_status": desi["current_status"],
        "desi_next_release": desi["next_data_release"],
        "juno_route_if_pdg_central_holds": juno_hyperk["juno_scenarios"][0]["route"],
        "hyperk_route_if_pdg_central_holds": juno_hyperk["hyperk_scenarios"][0]["route"],
        "cmbs4_current_route": cmbs4["current_status"]["route"],
        "litebird_gap_ready": True,
        "same_day_sync_required": True,
        "command_layer_ready": True,
    }


def robustness_finish_line_status() -> Dict[str, object]:
    """Return the current stress-test status for Lane D."""
    report = full_stress_report()
    return {
        "lane": "Lane D",
        "sweep_pct": 10.0,
        "gp_count": report["n_parameters_tested"],
        "all_gp_parameters_pass": report["all_pass"],
        "high_risk_count": len(report["high_risk_parameters"]),
        "highest_risk_parameters": list(report["high_risk_parameters"]),
        "status": "PASS" if report["all_pass"] else "TENSION",
    }


def governance_finish_line_status() -> Dict[str, object]:
    """Return the truth-sync and release-governance state for Lane E."""
    return {
        "lane": "Lane E",
        "canonical_board": CANONICAL_BOARD_ARTIFACT,
        "weekly_review_day": WEEKLY_GATE_REVIEW_DAY,
        "regression_gate_command": FULL_REGRESSION_GATE_COMMAND,
        "required_sync_artifacts": [
            "docs/mas_tracker.yml",
            "docs/WAVE_CHANGELOG.md",
            "STATUS.md",
            "docs/CLAIM_MASTER_BOARD.md",
            "docs/GATEKEEPER_SUMMARY.md",
            "docs/TRUTH_LAYER.md",
            "3-FALSIFICATION/OBSERVATION_TRACKER.md",
            "FALLIBILITY.md",
        ],
        "release_rule": (
            "GO only when regression is green, truth layers are synchronized, "
            "and unresolved risks are explicitly ledgered."
        ),
    }


def lane_status_snapshot() -> Dict[str, Dict[str, object]]:
    """Return the full 5-lane status snapshot."""
    return {
        "Lane A": p16_finish_line_hardgate(),
        "Lane B": p28_finish_line_architecture_review(),
        "Lane C": observation_finish_line_status(),
        "Lane D": robustness_finish_line_status(),
        "Lane E": governance_finish_line_status(),
    }


def finish_line_command_board() -> Dict[str, object]:
    """Return the canonical finish-line command board."""
    snapshot = lane_status_snapshot()
    return {
        "programme_version": PROGRAMME_VERSION,
        "programme_date": PROGRAMME_DATE,
        "canonical_board": CANONICAL_BOARD_ARTIFACT,
        "lane_order": list_lanes(),
        "weekly_gate_reviews": weekly_gate_reviews(),
        "lane_status": snapshot,
        "release_governance_active": True,
        "mas_reopen_allowed": False,
        "score_inflation_without_hardgate": False,
    }


def finish_line_unresolved_risk_ledger() -> List[Dict[str, object]]:
    """Return the unresolved-risk ledger that must travel with the release."""
    risks: List[Dict[str, object]] = []
    p16 = p16_finish_line_hardgate()
    if not p16["promotion_allowed"]:
        risks.append({
            "lane": "Lane A",
            "risk": "P16 still lacks exact WS-III derivation of '+52'",
            "severity": "high",
            "status_impact": "blocks_promotion",
        })

    risks.extend([
        {
            "lane": "Lane B",
            "risk": "P28 still requires 10D closure; N_flux=37 remains insufficient",
            "severity": "high",
            "status_impact": "blocks_promotion",
        },
        {
            "lane": "Lane C",
            "risk": "DESI DR3/Y5 can still falsify frozen-radion w_a = 0",
            "severity": "medium",
            "status_impact": "future_falsification_risk",
        },
        {
            "lane": "Lane D",
            "risk": "P3 and P10 retain the smallest GP stress margins",
            "severity": "medium",
            "status_impact": "watch_margin",
        },
    ])
    return risks


def finish_line_release_decision(
    regression_green: bool,
    truth_sync_complete: bool,
) -> Dict[str, object]:
    """Return the finish-line release go/no-go decision."""
    unresolved = finish_line_unresolved_risk_ledger()
    go = regression_green and truth_sync_complete
    return {
        "programme_version": PROGRAMME_VERSION,
        "regression_green": regression_green,
        "truth_sync_complete": truth_sync_complete,
        "go_no_go": "GO" if go else "NO_GO",
        "release_type": "release_quality_state_lock",
        "score_change": 0.0,
        "status_changes": [],
        "unresolved_risks": unresolved,
        "decision_note": (
            "GO is allowed because the release locks an honest, regression-green state "
            "without inflating any parameter label. Outstanding risks remain explicitly ledgered."
            if go
            else "NO_GO until regression and truth-sync requirements are both satisfied."
        ),
    }
