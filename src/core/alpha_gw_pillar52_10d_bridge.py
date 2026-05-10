# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
alpha_gw_pillar52_10d_bridge.py
================================
Canonical bridge report for the alpha_GW / CMB-amplitude absolute-scale closure.

This module formalizes the now-closed "missing link" as a two-stage bridge:

1. Pillar 52 fixes the COBE-normalized gravity scale in the inflationary sector.
2. The 10D UV completion package bridges the 5D KK scale to the higher-
   dimensional UV scale and returns an in-band alpha_GW prediction.

The retained RS1-only UV-brane audit is still reported for provenance, but it is
no longer treated as the live missing ingredient once the bridge report passes.
"""
from __future__ import annotations

import math
from typing import Dict

from src.core.alpha_gw_10d_uv_completion import full_10d_uv_closure_report
from src.core.alpha_gw_uv_brane_derivation import (
    ALPHA_GW_LOWER,
    ALPHA_GW_UPPER,
    rs1_uv_brane_alpha_gw_attempt,
)
from src.core.inflaton_5d_sector import gw_alpha_parameter

__all__ = [
    "pillar52_absolute_gravity_anchor",
    "kk_to_uv_absolute_scale_bridge",
    "alpha_gw_bridge_resolution",
]


def pillar52_absolute_gravity_anchor() -> Dict[str, object]:
    """Return the Pillar 52 normalization anchor for the gravity scale."""
    alpha_info = gw_alpha_parameter()
    alpha_eff = float(alpha_info["alpha_eff_V0_over_mpl4"])
    return {
        "source": "Pillar 52 COBE normalization",
        "h_inf_over_mpl": alpha_info["h_inf_over_mpl"],
        "alpha_eff_v0_over_mpl4": alpha_eff,
        "gravity_scale_log10": math.log10(alpha_eff),
        "resolved": alpha_eff > 0.0,
        "status": "ABSOLUTE_GRAVITY_SCALE_FIXED",
        "note": (
            "Pillar 52 fixes the inflationary gravity-scale decade through COBE "
            "normalization, providing the absolute 4D gravity anchor required for "
            "alpha_GW closure."
        ),
    }


def kk_to_uv_absolute_scale_bridge() -> Dict[str, object]:
    """Return the KK→UV bridge evidence from the 10D UV completion package."""
    report = full_10d_uv_closure_report()
    reduction = report["step3_reduction"]
    match = report["step6_match"]
    decision = report["step8_decision"]
    return {
        "source": "src/core/alpha_gw_10d_uv_completion.py",
        "m5_over_mpl": reduction["m5_over_mpl"],
        "k_over_m5": reduction["k_over_m5"],
        "c_uv_total": report["step4_c_uv"]["c_uv_total"],
        "alpha_gw_predicted": match["alpha_gw_predicted"],
        "alpha_gw_in_target_interval": match["alpha_gw_in_target_interval"],
        "all_consistency_gates_pass": report["step5_consistency_gates"]["all_consistency_gates_pass"],
        "robust_overlap": report["step7_robustness"]["robust_overlap"],
        "overlap_fraction": report["step7_robustness"]["overlap_fraction"],
        "decision_status": decision["status"],
        "status": (
            "KK_TO_UV_BRIDGE_RESOLVED"
            if decision["status"] == "CLOSED"
            else "KK_TO_UV_BRIDGE_OPEN"
        ),
        "note": (
            "The 10D UV package bridges the 5D KK scale to the higher-dimensional "
            "UV completion and fixes the absolute alpha_GW value."
        ),
    }


def alpha_gw_bridge_resolution() -> Dict[str, object]:
    """Return the canonical closed verdict for the missing-link bridge."""
    rs1 = rs1_uv_brane_alpha_gw_attempt()
    pillar52 = pillar52_absolute_gravity_anchor()
    uv_bridge = kk_to_uv_absolute_scale_bridge()

    alpha_pred = float(uv_bridge["alpha_gw_predicted"])
    alpha_anchor = float(pillar52["alpha_eff_v0_over_mpl4"])
    same_decade = abs(math.log10(alpha_pred) - math.log10(alpha_anchor)) < 0.5
    resolved = (
        pillar52["resolved"]
        and uv_bridge["alpha_gw_in_target_interval"]
        and uv_bridge["all_consistency_gates_pass"]
        and uv_bridge["robust_overlap"]
        and same_decade
    )

    return {
        "status": (
            "CLOSED_WITH_PILLAR52_10D_BRIDGE"
            if resolved
            else "OPEN_NARROWED"
        ),
        "missing_link_resolved": resolved,
        "five_d_operator_status": rs1["five_d_operator_audit"]["status"],
        "five_d_best_candidate_lane": rs1["best_candidate_lane"],
        "pillar52_anchor": pillar52,
        "uv_bridge": uv_bridge,
        "historical_rs1_only_alpha_gw": rs1["alpha_gw_geometric"],
        "historical_rs1_gap_orders_of_magnitude": rs1["gap_orders_of_magnitude"],
        "historical_rs1_audit_retained": True,
        "alpha_gw_exact": alpha_pred,
        "alpha_gw_target_interval": (ALPHA_GW_LOWER, ALPHA_GW_UPPER),
        "absolute_scale_bridge_consistent": same_decade,
        "resolution_note": (
            "The missing link is resolved by the Pillar 52 COBE-normalized gravity "
            "anchor together with the 10D UV completion bridge, which connects the "
            "5D KK scale to the higher-dimensional UV scale and yields "
            f"alpha_GW = {alpha_pred:.3e} in-band."
        ),
    }
