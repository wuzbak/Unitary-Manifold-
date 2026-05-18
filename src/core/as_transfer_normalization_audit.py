# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""SC2 A_s transfer-normalization audit with complete deterministic verdict logic.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

This module provides full chain routing:
1) transfer uncertainty gate,
2) α_GW in-band gate,
3) midpoint consistency gate,
4) c_UV point-derivation consistency,
5) robustness overlap gate.
"""
from __future__ import annotations

from src.core.alpha_gw_10d_uv_completion import freeze_target_equation_and_normalization, full_10d_uv_closure_report
from src.core.alpha_gw_pillar52_10d_bridge import alpha_gw_bridge_resolution

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "M_KK_WARP_RELATIVE_UNCERTAINTY",
    "SC2_PASS_THRESHOLD",
    "SC2_TENSION_THRESHOLD",
    "classify_sc2_step",
    "as_transfer_chain_audit",
    "sc2_chain_verdict",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"

# Conservative thresholding for transfer-normalization uncertainty.
M_KK_WARP_RELATIVE_UNCERTAINTY: float = 0.08
SC2_PASS_THRESHOLD: float = 0.10
SC2_TENSION_THRESHOLD: float = 0.20
MIN_INTERVAL_WIDTH: float = 1e-30
# Require at least 20% in-band support from the bounded robustness scan to
# classify the closure as robust rather than fine-tuned.
ROBUSTNESS_OVERLAP_MIN: float = 0.20


def classify_sc2_step(metric: float, pass_threshold: float, tension_threshold: float) -> str:
    """Classify a scalar residual metric as PASS/TENSION/FALSIFIED."""
    if metric <= pass_threshold:
        return "PASS"
    if metric <= tension_threshold:
        return "TENSION"
    return "FALSIFIED"


def as_transfer_chain_audit() -> dict[str, object]:
    """Return deterministic full SC2 audit packet."""
    bridge = alpha_gw_bridge_resolution()
    frozen = freeze_target_equation_and_normalization()
    uv_report = full_10d_uv_closure_report()

    alpha_exact = float(bridge["alpha_gw_exact"])
    alpha_low, alpha_high = bridge["alpha_gw_target_interval"]
    alpha_mid = 0.5 * (alpha_low + alpha_high)

    step1_metric = M_KK_WARP_RELATIVE_UNCERTAINTY
    step1_verdict = classify_sc2_step(
        metric=step1_metric,
        pass_threshold=SC2_PASS_THRESHOLD,
        tension_threshold=SC2_TENSION_THRESHOLD,
    )

    if alpha_low <= alpha_exact <= alpha_high:
        step2_metric = 0.0
    else:
        interval = max(alpha_high - alpha_low, MIN_INTERVAL_WIDTH)
        nearest = min(abs(alpha_exact - alpha_low), abs(alpha_exact - alpha_high))
        step2_metric = nearest / interval
    step2_verdict = classify_sc2_step(
        metric=step2_metric,
        pass_threshold=0.0,
        tension_threshold=0.10,
    )

    step3_metric = abs(alpha_exact - alpha_mid) / alpha_mid
    step3_verdict = classify_sc2_step(
        metric=step3_metric,
        pass_threshold=0.12,
        tension_threshold=0.25,
    )

    c_uv_exact = float(uv_report["step4_c_uv"]["c_uv_total"])
    c_uv_low, c_uv_high = frozen["c_uv_required_interval"]
    c_uv_mid = 0.5 * (c_uv_low + c_uv_high)
    c_uv_interval = max(c_uv_high - c_uv_low, MIN_INTERVAL_WIDTH)

    if c_uv_low <= c_uv_exact <= c_uv_high:
        step4_metric = 0.0
    else:
        step4_metric = min(abs(c_uv_exact - c_uv_low), abs(c_uv_exact - c_uv_high)) / c_uv_interval
    step4_verdict = classify_sc2_step(
        metric=step4_metric,
        pass_threshold=0.0,
        tension_threshold=0.15,
    )

    robustness_overlap = float(uv_report["step7_robustness"]["overlap_fraction"])
    step5_metric = max(0.0, ROBUSTNESS_OVERLAP_MIN - robustness_overlap)
    step5_verdict = classify_sc2_step(
        metric=step5_metric,
        pass_threshold=0.0,
        tension_threshold=0.05,
    )

    verdicts = (step1_verdict, step2_verdict, step3_verdict, step4_verdict, step5_verdict)
    if "FALSIFIED" in verdicts:
        chain_verdict = "FALSIFIED"
    elif "TENSION" in verdicts:
        chain_verdict = "TENSION"
    else:
        chain_verdict = "PASS"

    return {
        "audit_id": "SC2_AS_TRANSFER_NORMALIZATION_AUDIT",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "step1_mkk_transfer_uncertainty": {
            "metric": step1_metric,
            "pass_threshold": SC2_PASS_THRESHOLD,
            "tension_threshold": SC2_TENSION_THRESHOLD,
            "verdict": step1_verdict,
        },
        "step2_alpha_gw_bridge": {
            "alpha_exact": alpha_exact,
            "alpha_interval": (alpha_low, alpha_high),
            "normalized_distance_metric": step2_metric,
            "verdict": step2_verdict,
        },
        "step3_as_consistency": {
            "alpha_midpoint": alpha_mid,
            "relative_residual": step3_metric,
            "verdict": step3_verdict,
        },
        "step4_cuv_point_consistency": {
            "c_uv_exact": c_uv_exact,
            "c_uv_interval": (c_uv_low, c_uv_high),
            "c_uv_midpoint": c_uv_mid,
            "normalized_distance_metric": step4_metric,
            "verdict": step4_verdict,
        },
        "step5_robustness_overlap": {
            "overlap_fraction": robustness_overlap,
            "required_minimum": ROBUSTNESS_OVERLAP_MIN,
            "deficit_metric": step5_metric,
            "verdict": step5_verdict,
        },
        "chain_is_closed": chain_verdict == "PASS",
        "chain_verdict": chain_verdict,
        "status": (
            "CLOSED_FULL_POINT_DERIVATION" if chain_verdict == "PASS" else "OPEN_RESIDUAL"
        ),
    }


def sc2_chain_verdict() -> str:
    """Convenience accessor for the SC2 chain verdict."""
    return str(as_transfer_chain_audit()["chain_verdict"])
