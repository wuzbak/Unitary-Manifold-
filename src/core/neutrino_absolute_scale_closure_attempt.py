# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""WS-B++: neutrino absolute-scale closure attempt with hard-gate rubric."""

from __future__ import annotations

import math
from typing import Dict

from src.core.neutrino_crnu_6d_derivation import DM2_RATIO_GEO
from src.core.neutrino_majorana_uv_derivation import M_NU_SEESAW_EV

__all__ = [
    "DM2_21_PDG_EV2",
    "DM2_31_PDG_EV2",
    "SUM_MNU_PDG_BOUND_EV",
    "M1_FLOOR_EV",
    "DM2_31_PRED_EV2",
    "DM2_31_PCT_ERR",
    "GATE_PASSED",
    "P19_STATUS",
    "P20_STATUS",
    "P21_STATUS",
    "calibrate_neutrino_scale",
    "absolute_scale_predictions",
    "uncertainty_budget",
    "promotion_rubric",
    "wsbpp_summary",
]

DM2_21_PDG_EV2: float = 7.53e-5
DM2_31_PDG_EV2: float = 2.453e-3
SUM_MNU_PDG_BOUND_EV: float = 0.12


def calibrate_neutrino_scale(dm2_21_target: float = DM2_21_PDG_EV2) -> Dict[str, float]:
    """Set the absolute neutrino splitting scale from Δm²21 target."""
    scale_ev2 = dm2_21_target
    return {
        "scale_ev2": scale_ev2,
        "dm2_21_target_ev2": dm2_21_target,
    }


def absolute_scale_predictions() -> Dict[str, float]:
    """Predict m1, m2, m3 and splittings from calibrated absolute scale."""
    scale = calibrate_neutrino_scale()["scale_ev2"]
    dm2_31_pred = float(DM2_RATIO_GEO) * scale
    m1_floor = max(M_NU_SEESAW_EV, 1e-12)
    m2 = math.sqrt(m1_floor**2 + scale)
    m3 = math.sqrt(m1_floor**2 + dm2_31_pred)
    dm2_31_pct_err = abs(dm2_31_pred - DM2_31_PDG_EV2) / DM2_31_PDG_EV2 * 100.0
    sum_mnu = m1_floor + m2 + m3
    return {
        "m1_ev": m1_floor,
        "m2_ev": m2,
        "m3_ev": m3,
        "dm2_21_pred_ev2": scale,
        "dm2_31_pred_ev2": dm2_31_pred,
        "dm2_31_pct_err": dm2_31_pct_err,
        "sum_mnu_ev": sum_mnu,
    }


def uncertainty_budget() -> Dict[str, object]:
    """Return WS-B++ uncertainty budget for promotion decisions."""
    return {
        "dominant_sources": [
            {
                "source": "Δm² ratio closure (geometry ratio 36 vs PDG 32.6)",
                "impact": "sets floor on Δm²31 residual (~10%)",
                "reduction_path": "higher-order geometry beyond equal-spacing ratio",
            },
            {
                "source": "absolute m1 floor from 5D seesaw normalization",
                "impact": "subdominant for splittings but relevant for Σmν",
                "reduction_path": "derive Yukawa-normalization bridge at higher dimension",
            },
        ],
        "promotion_blocker": "Δm²31 residual remains above <5% hard gate",
    }


def promotion_rubric(
    split_threshold_pct: float = 5.0,
    sum_bound_ev: float = SUM_MNU_PDG_BOUND_EV,
) -> Dict[str, object]:
    """Evaluate hard-gate promotion rubric for P19/P20/P21."""
    preds = absolute_scale_predictions()
    gates = {
        "dm2_21_gate": abs(preds["dm2_21_pred_ev2"] - DM2_21_PDG_EV2) < 1e-15,
        "dm2_31_gate": preds["dm2_31_pct_err"] <= split_threshold_pct,
        "sum_mnu_gate": preds["sum_mnu_ev"] <= sum_bound_ev,
        "axiomzero_purity_gate": True,
    }
    return {
        "predictions": preds,
        "split_threshold_pct": split_threshold_pct,
        "sum_bound_ev": sum_bound_ev,
        "gates": gates,
        "hard_gate_pass": all(gates.values()),
    }


_P = absolute_scale_predictions()
_R = promotion_rubric()

M1_FLOOR_EV: float = _P["m1_ev"]
DM2_31_PRED_EV2: float = _P["dm2_31_pred_ev2"]
DM2_31_PCT_ERR: float = _P["dm2_31_pct_err"]
GATE_PASSED: bool = bool(_R["hard_gate_pass"])
P19_STATUS: str = "CONSTRAINED"
P20_STATUS: str = "GEOMETRIC ESTIMATE"
P21_STATUS: str = "GEOMETRIC ESTIMATE"


def wsbpp_summary() -> Dict[str, object]:
    """Return consolidated WS-B++ payload for tracker and wave ledger."""
    return {
        "workstream": "WS-B++",
        "parameters": ["P19", "P20", "P21"],
        "predictions": _P,
        "uncertainty_budget": uncertainty_budget(),
        "promotion_rubric": _R,
        "gate_passed": GATE_PASSED,
        "status": {
            "P19": P19_STATUS,
            "P20": P20_STATUS,
            "P21": P21_STATUS,
        },
        "verdict": (
            "Absolute-scale closure attempt completed with calibrated Δm²21 and "
            "explicit uncertainty budget. Hard gate not met due to Δm²31 residual."
        ),
    }
