# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
next_five_tiers_programme.py — Machine-readable post-freeze five-tier programme.

This module encodes the next independent research programme requested after the
v10.21 state (ToE ~63%, MAS closed). The programme does not reopen MAS and does
not create new MAS waves.

Tier scope:
  Tier-1: P3, P5 hardgate promotions to GEOMETRIC_PREDICTION
  Tier-2: P17, P18 neutrino precision upgrades
  Tier-3: P19, P20 mixing-angle hardgate closure package
  Tier-4: P7–P10 Yukawa hierarchy refinement
  Tier-5: P27, P28 architecture-limit mechanism deepening
"""
from __future__ import annotations

from copy import deepcopy
from typing import Dict, List

__all__ = [
    "PROGRAMME_VERSION",
    "PROGRAMME_DATE",
    "TIER_EXECUTION_ORDER",
    "TIER_CATALOGUE",
    "get_tier",
    "list_tiers",
    "tier_parameter_targets",
    "projected_toe_uplift_bounds",
    "programme_summary",
]

PROGRAMME_VERSION: str = "v10.22"
PROGRAMME_DATE: str = "2026-05-08"

TIER_EXECUTION_ORDER: List[str] = [
    "Tier-1",
    "Tier-2",
    "Tier-3",
    "Tier-4",
    "Tier-5",
]

TIER_CATALOGUE: Dict[str, Dict] = {
    "Tier-1": {
        "title": "Hardgate promotions of near-threshold wins",
        "target_parameters": ["P3", "P5"],
        "current_status": "GEOMETRIC_ESTIMATE_CERTIFIED",
        "target_status": "GEOMETRIC_PREDICTION",
        "priority": "highest",
        "acceptance_gates": [
            "nominal_residual_lt_5pct",
            "robustness_window_pass",
            "axiomzero_purity_pass",
        ],
        "mas_reopen_allowed": False,
    },
    "Tier-2": {
        "title": "Neutrino precision upgrade sprint",
        "target_parameters": ["P17", "P18"],
        "current_status": "CONSTRAINED",
        "target_status": "GEOMETRIC_PREDICTION",
        "priority": "high",
        "acceptance_gates": [
            "residual_lt_5pct",
            "higher_order_correction_stability",
            "robustness_gate_pass",
        ],
        "mas_reopen_allowed": False,
    },
    "Tier-3": {
        "title": "Mixing-angle closure package",
        "target_parameters": ["P19", "P20"],
        "current_status": "CONSTRAINED",
        "target_status": "GEOMETRIC_PREDICTION",
        "priority": "high",
        "acceptance_gates": [
            "hardgate_nominal_pass",
            "uncertainty_propagation_pass",
            "purity_check_pass",
        ],
        "mas_reopen_allowed": False,
    },
    "Tier-4": {
        "title": "Yukawa hierarchy refinement",
        "target_parameters": ["P7", "P8", "P9", "P10"],
        "current_status": "CONSTRAINED",
        "target_status": "GEOMETRIC_PREDICTION",
        "priority": "medium",
        "acceptance_gates": [
            "unified_overlap_integral_calibration",
            "cross_generation_consistency",
            "residual_compression",
        ],
        "mas_reopen_allowed": False,
    },
    "Tier-5": {
        "title": "Architecture-limit frontier",
        "target_parameters": ["P27", "P28"],
        "current_status": "ARCHITECTURE_LIMIT_CERTIFIED",
        "target_status": "ARCHITECTURE_LIMIT_CERTIFIED_MECHANISM_DEEPENED",
        "priority": "long_horizon",
        "acceptance_gates": [
            "mechanism_deepening_documented",
            "falsifier_integrity_preserved",
            "no_score_inflation_without_hardgate",
        ],
        "mas_reopen_allowed": False,
    },
}


def get_tier(tier_id: str) -> Dict:
    """Return a copy of the tier specification for *tier_id*."""
    if tier_id not in TIER_CATALOGUE:
        raise KeyError(
            f"Unknown tier: {tier_id!r}. "
            f"Available: {list(TIER_EXECUTION_ORDER)}"
        )
    return deepcopy(TIER_CATALOGUE[tier_id])


def list_tiers() -> List[str]:
    """Return the fixed execution order for the five tiers."""
    return list(TIER_EXECUTION_ORDER)


def tier_parameter_targets() -> Dict[str, List[str]]:
    """Return mapping tier ID -> target parameter IDs."""
    return {
        tier_id: list(TIER_CATALOGUE[tier_id]["target_parameters"])
        for tier_id in TIER_EXECUTION_ORDER
    }


def projected_toe_uplift_bounds() -> Dict[str, float]:
    """Return projected upper-bound ToE uplift if all promotable tiers succeed.

    This is an indicative planning bound only. Tier-5 is architecture-focused and
    does not assume automatic score promotion.
    """
    uplift_by_tier = {
        "Tier-1": 1.0,  # P3 + P5: 0.3 -> 0.8 each
        "Tier-2": 0.6,  # P17 + P18: 0.5 -> 0.8 each
        "Tier-3": 0.6,  # P19 + P20: 0.5 -> 0.8 each
        "Tier-4": 1.2,  # P7..P10: 0.5 -> 0.8 each
        "Tier-5": 0.0,  # mechanism deepening, no assumed status promotion
    }
    total_upper_bound = sum(uplift_by_tier.values())
    return {
        "tier_1_to_4_upper_bound": round(total_upper_bound, 3),
        "tier_5_assumed_uplift": uplift_by_tier["Tier-5"],
        "all_tiers_upper_bound": round(total_upper_bound, 3),
    }


def programme_summary() -> Dict:
    """Return the five-tier programme summary."""
    parameter_targets = tier_parameter_targets()
    unique_parameters = sorted(
        {
            pid
            for pids in parameter_targets.values()
            for pid in pids
        }
    )
    return {
        "programme_version": PROGRAMME_VERSION,
        "programme_date": PROGRAMME_DATE,
        "tier_count": len(TIER_EXECUTION_ORDER),
        "tier_ids": list_tiers(),
        "targets_by_tier": parameter_targets,
        "unique_target_parameters": unique_parameters,
        "unique_target_parameter_count": len(unique_parameters),
        "mas_reopen_allowed": False,
        "scope_rule": "independent_post_freeze_programme_only",
        "anti_recycle_rule": "no_recycle_into_mas_waves",
        "projected_uplift_bounds": projected_toe_uplift_bounds(),
        "note": (
            "Five independent tiers are defined for post-v10.21 advancement. "
            "All tiers preserve MAS closure and require hardgates for any status promotion."
        ),
    }

