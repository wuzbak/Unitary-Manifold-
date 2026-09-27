# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Three-sector cosmology impact audit for certified architecture limits.

This module compares baseline UM architecture-limit anchors with a three-sector
UV/bulk/IR modifier model. It answers only one question:
does the three-sector architecture reduce AL-1..AL-4 in a measurable way?

The baseline values are taken from canonical hardgate modules and certificates.
"""

from __future__ import annotations

from typing import Dict

from src.core.b_mu_dynamical_dark_energy import (
    DESI_TARGET_WA,
    WA_FIT_TOLERANCE,
    evaluate_gamma_models_for_wa,
)
from src.core.de_equation_of_state_desi import um_dark_energy_eos
from src.core.pillar396_act_r_tension_architecture_limit import R_ACT_UPPER, R_BRAIDED
from src.core.z2_odd_power_suppression import al1_al2_delta_report

# Baseline architecture limits (current certified lane)
AL1_BASELINE_CMB_SUPPRESSION: float = 5.3  # central ×4–7 suppression
AL2_BASELINE_R: float = float(R_BRAIDED)   # ≈ 0.0315
AL2_TARGET_R_MAX: float = float(R_ACT_UPPER)  # 0.016
AL3_BASELINE_WA: float = 0.0
AL3_TARGET_WA_DR2: float = float(DESI_TARGET_WA)
AL4_BASELINE_LAMBDA_LOG10_GAP: float = 55.0
WA_THREE_SECTOR_SHIFT_COEFF: float = -0.02  # conservative phenomenological shift

# Three-sector UV/bulk/IR coefficients (assessed, not fitted to data)
SECTOR_WEIGHTS = (5.0 / 18.0, 6.0 / 18.0, 7.0 / 18.0)
SECTOR_SUM = sum(SECTOR_WEIGHTS)


def _weight_metrics(weights: tuple[float, float, float]) -> Dict[str, float]:
    return {
        "sum": sum(weights),
        "spread": max(weights) - min(weights),
        "l2": sum(w * w for w in weights),
    }


def three_sector_modifiers() -> Dict[str, float]:
    """Return architecture modifiers implied by simple three-sector weighting."""
    metrics = _weight_metrics(SECTOR_WEIGHTS)
    # Conservative effects driven by weight asymmetry and concentration.
    m_as = 1.0 - 0.12 * metrics["spread"] - 0.03 * metrics["l2"]
    m_r = 1.0 - 0.10 * metrics["spread"] - 0.02 * metrics["l2"]
    m_wa = 1.0 - 0.08 * metrics["spread"] - 0.04 * metrics["l2"]
    m_lambda = 1.0 - 0.06 * metrics["spread"] - 0.01 * metrics["l2"]
    return {
        "modifier_as": m_as,
        "modifier_r": m_r,
        "modifier_wa": m_wa,
        "modifier_lambda_gap": m_lambda,
    }


def three_sector_predictions() -> Dict[str, float]:
    """Return updated predictions under the three-sector modifier model."""
    m = three_sector_modifiers()
    w0_baseline = float(um_dark_energy_eos()["w_kk"])
    wa_shift = WA_THREE_SECTOR_SHIFT_COEFF * SECTOR_SUM
    return {
        "as_suppression_factor": AL1_BASELINE_CMB_SUPPRESSION * m["modifier_as"],
        "r_prediction": AL2_BASELINE_R * m["modifier_r"],
        "wa_prediction": AL3_BASELINE_WA * m["modifier_wa"] + wa_shift,
        "w0_prediction": w0_baseline,
        "lambda_log10_gap": AL4_BASELINE_LAMBDA_LOG10_GAP * m["modifier_lambda_gap"],
    }


def architecture_limit_delta_report() -> Dict[str, object]:
    """Quantify AL-1..AL-4 deltas and closure verdicts."""
    pred = three_sector_predictions()
    z2 = al1_al2_delta_report()
    gamma = evaluate_gamma_models_for_wa()
    delta_al1 = AL1_BASELINE_CMB_SUPPRESSION - pred["as_suppression_factor"]
    delta_al2 = AL2_BASELINE_R - pred["r_prediction"]
    delta_al3 = abs(AL3_TARGET_WA_DR2 - AL3_BASELINE_WA) - abs(AL3_TARGET_WA_DR2 - pred["wa_prediction"])
    delta_al4 = AL4_BASELINE_LAMBDA_LOG10_GAP - pred["lambda_log10_gap"]

    # Keep core architecture verdict tied to this module's three-sector predictions.
    resolved_al1 = pred["as_suppression_factor"] <= 1.5
    resolved_al2 = pred["r_prediction"] <= AL2_TARGET_R_MAX
    resolved_al3 = abs(AL3_TARGET_WA_DR2 - pred["wa_prediction"]) < WA_FIT_TOLERANCE
    resolved_al4 = pred["lambda_log10_gap"] <= 1.0

    n_resolved = sum(int(v) for v in (resolved_al1, resolved_al2, resolved_al3, resolved_al4))
    if n_resolved == 0:
        status = "OPEN_GAP"
    elif n_resolved == 4:
        status = "FULL_RESOLUTION"
    else:
        status = "PARTIAL_REDUCTION"

    al1_three_sector_pct = 100.0 * delta_al1 / AL1_BASELINE_CMB_SUPPRESSION
    al2_three_sector_pct = 100.0 * delta_al2 / AL2_BASELINE_R
    al3_baseline_gap = abs(AL3_TARGET_WA_DR2 - AL3_BASELINE_WA)
    al3_three_sector_pct = 0.0 if al3_baseline_gap <= 0 else max(0.0, 100.0 * delta_al3 / al3_baseline_gap)
    al4_three_sector_pct = 100.0 * delta_al4 / AL4_BASELINE_LAMBDA_LOG10_GAP
    z2_route_flags = {
        "AL1": z2["al1_check"]["within_1pct"],
        "AL2": z2["al2_check"]["approaches_bound"],
        "AL3": False,
        "AL4": False,
    }
    z2_route_resolved = sum(int(v) for v in z2_route_flags.values())
    if z2_route_resolved == 0:
        z2_route_status = "OPEN_GAP"
    elif z2_route_resolved == 4:
        z2_route_status = "FULL_RESOLUTION"
    else:
        z2_route_status = "PARTIAL_REDUCTION"
    gamma_route_flags = {
        "AL1": False,
        "AL2": False,
        "AL3": abs(gamma["best_wa"] - AL3_TARGET_WA_DR2) < WA_FIT_TOLERANCE,
        "AL4": False,
    }
    gamma_route_resolved = sum(int(v) for v in gamma_route_flags.values())
    if gamma_route_resolved == 0:
        gamma_route_status = "OPEN_GAP"
    elif gamma_route_resolved == 4:
        gamma_route_status = "FULL_RESOLUTION"
    else:
        gamma_route_status = "PARTIAL_REDUCTION"

    return {
        "baseline": {
            "AL1_cmb_suppression": AL1_BASELINE_CMB_SUPPRESSION,
            "AL2_r": AL2_BASELINE_R,
            "AL3_wa": AL3_BASELINE_WA,
            "AL4_lambda_log10_gap": AL4_BASELINE_LAMBDA_LOG10_GAP,
        },
        "three_sector": pred,
        "z2_odd": z2,
        "gamma_dynamic": gamma,
        "z2_odd_route_assessment": {
            **z2_route_flags,
            "status": z2_route_status,
            "epistemic_note": (
                "This route is a fitted extension and is reported separately from "
                "the core three-sector architecture verdict."
            ),
        },
        "dynamic_gamma_route_assessment": {
            **gamma_route_flags,
            "status": gamma_route_status,
            "epistemic_note": (
                "This route tracks Γ(t)-driven dark-energy dynamics and is separate "
                "from Z₂-odd scalar/tensor suppression."
            ),
        },
        "delta": {
            "AL1_reduction": delta_al1,
            "AL2_reduction": delta_al2,
            "AL3_reduction": delta_al3,
            "AL4_reduction": delta_al4,
        },
        "resolved": {
            "AL1": resolved_al1,
            "AL2": resolved_al2,
            "AL3": resolved_al3,
            "AL4": resolved_al4,
        },
        "comparison_table": [
            {
                "AL": "AL-1",
                "three_sector_reduction_percent": round(al1_three_sector_pct, 2),
                "separate_route_assessment": (
                    f"Z₂-odd: {z2['scalar']['odd_fraction_removed']*100:.2f}% removed "
                    f"(target mismatch {z2['al1_check']['target_mismatch']*100:.2f}%)"
                ),
                "target": "33.6% mismatch",
            },
            {
                "AL": "AL-2",
                "three_sector_reduction_percent": round(al2_three_sector_pct, 2),
                "separate_route_assessment": (
                    f"Z₂-odd: r × 25/49 = {z2['r_correction']['r_corrected']:.6f}"
                ),
                "target": "r < 0.016",
            },
            {
                "AL": "AL-3",
                "three_sector_reduction_percent": round(al3_three_sector_pct, 2),
                "separate_route_assessment": f"Γ(t) route: best w_a proxy={gamma['best_wa']:.2f}",
                "target": "w_a ≈ -0.55",
            },
            {
                "AL": "AL-4",
                "three_sector_reduction_percent": round(al4_three_sector_pct, 2),
                "separate_route_assessment": "No separate route closure; remains architecture-limit scale",
                "target": "10^55 hierarchy gap",
            },
        ],
        "status": status,
        "epistemic_note": (
            "Core three-sector weighting still leaves AL-1..AL-4 open. A separate fitted "
            "Z₂-odd route shows partial reductions and is reported independently."
        ),
    }
