# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""5D operator audit for the α_GW closure bottleneck."""
from __future__ import annotations

import math
from typing import Dict, List

from src.core.inflaton_5d_sector import gw_alpha_parameter

__all__ = [
    "PI_KR",
    "K_CS",
    "N_W",
    "ALPHA_GW_TARGET_LOWER",
    "ALPHA_GW_TARGET_UPPER",
    "freeze_5d_only_target",
    "separate_alpha_gw_closure_problems",
    "audit_current_rs1_transfer_law",
    "evaluate_candidate_5d_closure_lanes",
    "alpha_gw_5d_operator_assessment",
]

PI_KR: float = 37.0
K_CS: int = 74
N_W: int = 5
ALPHA_GW_TARGET_LOWER: float = 4.2e-10
ALPHA_GW_TARGET_UPPER: float = 4.8e-10

_CASIMIR_COEFF: float = float(K_CS * N_W) / (24.0 * math.pi**2)
_ALPHA_GW_TARGET_MID: float = 0.5 * (ALPHA_GW_TARGET_LOWER + ALPHA_GW_TARGET_UPPER)
_ALPHA_GW_RS1_BULK: float = _CASIMIR_COEFF * math.exp(-4.0 * PI_KR)


def freeze_5d_only_target() -> Dict[str, object]:
    """Freeze the honest 5D target and admissibility rules."""
    alpha_eff = float(gw_alpha_parameter()["alpha_eff_V0_over_mpl4"])
    return {
        "rs1_only_alpha_gw": _ALPHA_GW_RS1_BULK,
        "alpha_gw_target_interval": (ALPHA_GW_TARGET_LOWER, ALPHA_GW_TARGET_UPPER),
        "alpha_gw_target_midpoint": _ALPHA_GW_TARGET_MID,
        "pillar52_absolute_scale_anchor": alpha_eff,
        "pillar52_same_decade_as_target": abs(math.log10(alpha_eff) - math.log10(_ALPHA_GW_TARGET_MID)) < 0.5,
        "allowed_inputs": [
            "5D geometry",
            "orbifold structure",
            "RS1 boundary conditions",
            "accepted UM constants",
            "already-established 5D dynamical fields",
        ],
        "disallowed_inputs": [
            "10D flux data",
            "CY3 threshold data",
            "external UV benchmark coefficients",
        ],
        "status": "TARGET_FROZEN",
    }


def separate_alpha_gw_closure_problems() -> Dict[str, Dict[str, object]]:
    """Separate the absolute-scale and transfer-law bottlenecks."""
    frozen = freeze_5d_only_target()
    alpha_eff = float(frozen["pillar52_absolute_scale_anchor"])
    return {
        "problem_a_absolute_scale": {
            "quantity": "alpha_eff_v0_over_mpl4",
            "value": alpha_eff,
            "same_decade_as_target": frozen["pillar52_same_decade_as_target"],
            "derived_purely_in_5d": False,
            "note": (
                "Pillar 52 fixes the needed 10^-9 decade, but it is not yet a pure "
                "5D derivation from intrinsic RS1 data alone."
            ),
        },
        "problem_b_transfer_law": {
            "current_relation": "alpha_gw ~ c_cas * exp(-4*pi*k*R)",
            "rs1_only_alpha_gw": _ALPHA_GW_RS1_BULK,
            "gap_to_target_log10": math.log10(_ALPHA_GW_TARGET_MID / _ALPHA_GW_RS1_BULK),
            "note": (
                "The dominant mismatch is the observable-transfer law that sends the "
                "RS1-only estimate down to ~10^-65."
            ),
        },
    }


def audit_current_rs1_transfer_law() -> Dict[str, object]:
    """Audit the current bulk warp-power counting."""
    mkk_over_mpl = math.exp(-PI_KR)
    required_enhancement = _ALPHA_GW_TARGET_MID / _ALPHA_GW_RS1_BULK
    radion_reclassified_alpha = _CASIMIR_COEFF * mkk_over_mpl
    radion_residual = _ALPHA_GW_TARGET_MID / radion_reclassified_alpha
    topological_enhancement = float(K_CS * N_W) * PI_KR
    topological_alpha = _ALPHA_GW_RS1_BULK * topological_enhancement
    topological_residual = _ALPHA_GW_TARGET_MID / topological_alpha
    return {
        "casimir_coefficient": _CASIMIR_COEFF,
        "mkk_over_mpl": mkk_over_mpl,
        "bulk_transfer_relation": "alpha_gw ~ c_cas * (M_KK/M_Pl)^4",
        "bulk_warp_exponent": 4.0,
        "bulk_alpha_gw": _ALPHA_GW_RS1_BULK,
        "required_enhancement_to_target": required_enhancement,
        "required_enhancement_log10": math.log10(required_enhancement),
        "radion_best_case_relation": "alpha_gw ~ c_cas * (M_KK/M_Pl)",
        "radion_best_case_alpha": radion_reclassified_alpha,
        "radion_residual_enhancement_needed": radion_residual,
        "radion_residual_log10": math.log10(radion_residual),
        "topological_best_case_enhancement": topological_enhancement,
        "topological_best_case_alpha": topological_alpha,
        "topological_residual_enhancement_needed": topological_residual,
        "topological_residual_log10": math.log10(topological_residual),
        "present_bulk_transfer_viable": False,
        "bottleneck_statement": (
            "The present alpha_gw ~ exp(-4*pi*k*R) identification misses the target "
            "by ~55 orders of magnitude, so it cannot be the full observable "
            "normalization if a 5D closure exists."
        ),
    }


def evaluate_candidate_5d_closure_lanes() -> Dict[str, object]:
    """Evaluate the three candidate 5D closure lanes against a hard litmus test."""
    frozen = freeze_5d_only_target()
    transfer = audit_current_rs1_transfer_law()
    alpha_eff = float(frozen["pillar52_absolute_scale_anchor"])

    lanes: List[Dict[str, object]] = [
        {
            "lane": "induced_gravity_uv_localized",
            "candidate_relation": "alpha_gw ~ O(1) * alpha_eff",
            "best_case_alpha": alpha_eff,
            "same_decade_as_target": frozen["pillar52_same_decade_as_target"],
            "residual_factor_to_target": _ALPHA_GW_TARGET_MID / alpha_eff,
            "uses_only_admissible_5d_inputs": False,
            "numerically_viable": True,
            "full_5d_closure": False,
            "failure_mode": (
                "This lane can remove the exp(-4*pi*k*R) bottleneck only by leaning on "
                "the Pillar 52 anchor or an as-yet underived UV-localized coefficient."
            ),
        },
        {
            "lane": "radion_normalization",
            "candidate_relation": "alpha_gw ~ c_cas * (M_KK/M_Pl)",
            "best_case_alpha": transfer["radion_best_case_alpha"],
            "same_decade_as_target": False,
            "residual_factor_to_target": transfer["radion_residual_enhancement_needed"],
            "uses_only_admissible_5d_inputs": True,
            "numerically_viable": transfer["radion_residual_enhancement_needed"] <= 10.0,
            "full_5d_closure": False,
            "failure_mode": (
                "Even the optimistic exponent reclassification leaves a residual "
                "enhancement of order 10^6."
            ),
        },
        {
            "lane": "topological_anomaly",
            "candidate_relation": "alpha_gw ~ polynomial(K_CS, n_w, pi*k*R) * c_cas * exp(-4*pi*k*R)",
            "best_case_alpha": transfer["topological_best_case_alpha"],
            "same_decade_as_target": False,
            "residual_factor_to_target": transfer["topological_residual_enhancement_needed"],
            "uses_only_admissible_5d_inputs": True,
            "numerically_viable": transfer["topological_residual_enhancement_needed"] <= 10.0,
            "full_5d_closure": False,
            "failure_mode": (
                "Polynomial or loop-sized 5D coefficients are far too small to supply "
                "the required ~10^55 enhancement."
            ),
        },
    ]

    best_lane = max(
        lanes,
        key=lambda lane: (
            int(bool(lane["numerically_viable"])),
            -abs(math.log10(max(float(lane["residual_factor_to_target"]), 1e-300))),
        ),
    )

    return {
        "litmus_threshold_enhancement": transfer["required_enhancement_to_target"],
        "litmus_threshold_log10": transfer["required_enhancement_log10"],
        "lanes": lanes,
        "best_lane": best_lane["lane"],
        "any_pure_5d_full_closure": any(bool(lane["full_5d_closure"]) for lane in lanes),
        "best_lane_requires_non_5d_input": not bool(best_lane["uses_only_admissible_5d_inputs"]),
    }


def alpha_gw_5d_operator_assessment() -> Dict[str, object]:
    """Return the consolidated 5D-only assessment."""
    frozen = freeze_5d_only_target()
    problems = separate_alpha_gw_closure_problems()
    transfer = audit_current_rs1_transfer_law()
    candidates = evaluate_candidate_5d_closure_lanes()
    induced_lane = next(
        lane for lane in candidates["lanes"] if lane["lane"] == "induced_gravity_uv_localized"
    )

    return {
        "status": "OPERATOR_RECLASSIFICATION_NEEDED_BUT_NOT_CLOSED_IN_5D",
        "target": frozen,
        "problem_split": problems,
        "transfer_audit": transfer,
        "candidate_lanes": candidates,
        "present_transfer_law_survives": False,
        "best_candidate_lane": candidates["best_lane"],
        "best_candidate_requires_non_5d_input": candidates["best_lane_requires_non_5d_input"],
        "induced_gravity_same_decade_as_target": induced_lane["same_decade_as_target"],
        "any_pure_5d_full_closure": candidates["any_pure_5d_full_closure"],
        "conclusion": (
            "The exp(-4*pi*k*R) bulk identification fails as a full observable "
            "normalization. A UV-localized induced-gravity style operator is the only "
            "lane that can land in the right decade, but it does not yet provide a "
            "pure 5D derivation of either alpha_eff or c_UV. The honest fallback is "
            "therefore a stronger 5D no-go with an operator-reclassification hint, "
            "not a pure-5D closure."
        ),
    }
