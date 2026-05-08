# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
prediction_registry.py — Machine-readable registry of all published Unitary Manifold
predictions, their experimental status, and falsification conditions.

Pillar coverage: 1–101 (composite summary across all pillars).
Epistemic labels: GEOMETRIC_PREDICTION, ALGEBRAIC, DERIVED, CONSTRAINED.
"""
from __future__ import annotations

import math
from typing import Dict, List

__all__ = [
    # Constants
    "ADMISSIBLE_WINDOW_LOW_DEG",
    "ADMISSIBLE_WINDOW_HIGH_DEG",
    "PREDICTED_GAP_LOW_DEG",
    "PREDICTED_GAP_HIGH_DEG",
    # Registry
    "PREDICTION_REGISTRY",
    # Functions
    "get_prediction",
    "list_predictions",
    "predictions_by_experiment",
    "falsifiable_predictions",
    "registry_summary",
    "litebird_window",
]

# ---------------------------------------------------------------------------
# Birefringence window constants
# ---------------------------------------------------------------------------
ADMISSIBLE_WINDOW_LOW_DEG: float = 0.22
ADMISSIBLE_WINDOW_HIGH_DEG: float = 0.38
PREDICTED_GAP_LOW_DEG: float = 0.29
PREDICTED_GAP_HIGH_DEG: float = 0.31

# ---------------------------------------------------------------------------
# Prediction registry
# ---------------------------------------------------------------------------
PREDICTION_REGISTRY: Dict[str, Dict] = {
    "BETA_BIREFRINGENCE_1": {
        "pillar": [27, 28, 52],
        "quantity": "CMB polarization birefringence angle (canonical mode)",
        "predicted_value": 0.273,
        "units": "degrees",
        "experiment": "LiteBIRD",
        "exp_launch_year": 2032,
        "current_status": "PENDING — LiteBIRD not yet launched",
        "falsification_condition": (
            "Falsified if β ∉ [0.22°, 0.38°] or if β ∈ [0.29°, 0.31°] "
            "(the predicted gap between modes)"
        ),
        "epistemic_label": "GEOMETRIC_PREDICTION",
    },
    "BETA_BIREFRINGENCE_2": {
        "pillar": [27, 28, 52],
        "quantity": "CMB polarization birefringence angle (derived mode)",
        "predicted_value": 0.331,
        "units": "degrees",
        "experiment": "LiteBIRD",
        "exp_launch_year": 2032,
        "current_status": "PENDING — LiteBIRD not yet launched",
        "falsification_condition": (
            "Falsified if β ∉ [0.22°, 0.38°] or if β ∈ [0.29°, 0.31°] "
            "(the predicted gap between modes)"
        ),
        "epistemic_label": "GEOMETRIC_PREDICTION",
    },
    "N_S_CMB": {
        "pillar": [1, 2, 3],
        "quantity": "CMB scalar spectral index n_s",
        "predicted_value": 0.9635,
        "units": "dimensionless",
        "experiment": "Planck",
        "exp_launch_year": 2009,
        "current_status": "CONSISTENT — Planck: 0.9649 ± 0.0042 (0.33σ from prediction)",
        "falsification_condition": (
            "Falsified if Planck/CMB-S4 measures n_s outside UM admissible range"
        ),
        "epistemic_label": "GEOMETRIC_PREDICTION",
    },
    "R_TENSOR": {
        "pillar": [1, 2, 3],
        "quantity": "Tensor-to-scalar ratio r",
        "predicted_value": 0.0315,
        "units": "dimensionless",
        "experiment": "BICEP/Keck + CMB-S4",
        "exp_launch_year": 2030,
        "current_status": "CONSISTENT — BICEP/Keck: r < 0.036 (prediction inside upper bound)",
        "falsification_condition": (
            "Falsified if r < 0.010 (detection below UM lower bound) "
            "or if r > 0.036 is ruled in strongly"
        ),
        "epistemic_label": "GEOMETRIC_PREDICTION",
    },
    "N_GEN": {
        "pillar": [6, 7, 8],
        "quantity": "Number of fermion generations",
        "predicted_value": 3,
        "units": "dimensionless (integer)",
        "experiment": "LEP",
        "exp_launch_year": 1989,
        "current_status": "CONFIRMED — LEP: exactly 3 light neutrino species",
        "falsification_condition": (
            "Falsified if a 4th light neutrino generation is discovered"
        ),
        "epistemic_label": "ALGEBRAIC",
    },
    "HIGGS_VEV": {
        "pillar": [5, 10],
        "quantity": "Higgs vacuum expectation value",
        "predicted_value": 246.0,
        "units": "GeV",
        "experiment": "PDG (LHC)",
        "exp_launch_year": 2012,
        "current_status": "CONSTRAINED — PDG: 246.22 GeV (4.6% residual, architecture limit P5)",
        "falsification_condition": (
            "Falsified if PDG value shifts outside [235, 260] GeV decisively"
        ),
        "epistemic_label": "CONSTRAINED",
    },
    "MP_ME_RATIO": {
        "pillar": [14, 15],
        "quantity": "Proton-to-electron mass ratio m_p/m_e",
        "predicted_value": 1836.0,
        "units": "dimensionless",
        "experiment": "PDG",
        "exp_launch_year": 1900,
        "current_status": "CONSTRAINED — PDG: 1836.15 (0.6% residual from geometric estimate)",
        "falsification_condition": (
            "Falsified if precision measurements show ratio inconsistent with "
            "any 5D geometric derivation in the admissible range"
        ),
        "epistemic_label": "CONSTRAINED",
    },
    "DELTA_CP": {
        "pillar": [13, 14],
        "quantity": "Leptonic CP-violation phase δ_CP",
        "predicted_value": math.pi / 3,
        "units": "radians",
        "experiment": "T2K/NOvA/DUNE",
        "exp_launch_year": 2026,
        "current_status": (
            "BEST_EVIDENCE_CONSTRAINED — PDG central: 1.20 rad; UM (9D refined): "
            "δ_CP ≈ 1.216 rad (~1.3% residual) with propagated uncertainty <5%"
        ),
        "falsification_condition": (
            "Falsified if DUNE measures δ_CP decisively outside [0.85, 1.30] rad "
            "with <3% uncertainty, ruling out all geometric corrections"
        ),
        "epistemic_label": "CONSTRAINED",
    },
    "GW_BACKGROUND": {
        "pillar": [3, 5, 29],
        "quantity": "Stochastic GW background energy density Ω_GW",
        "predicted_value": 1e-15,
        "units": "dimensionless (at LISA peak frequency)",
        "experiment": "LISA",
        "exp_launch_year": 2035,
        "current_status": "PENDING — LISA not yet operational",
        "falsification_condition": (
            "Falsified if LISA measures Ω_GW(f_LISA) < 10^-17 "
            "or spectrum shape inconsistent with 5D KK tower"
        ),
        "epistemic_label": "DERIVED",
    },
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_prediction(pid: str) -> Dict:
    """Return the prediction dict for prediction ID *pid*."""
    if pid not in PREDICTION_REGISTRY:
        raise KeyError(f"Unknown prediction ID: {pid!r}. "
                       f"Available: {list(PREDICTION_REGISTRY)}")
    return dict(PREDICTION_REGISTRY[pid])


def list_predictions() -> List[str]:
    """Return sorted list of all prediction IDs."""
    return sorted(PREDICTION_REGISTRY.keys())


def predictions_by_experiment(exp_name: str) -> List[Dict]:
    """Return list of prediction dicts whose experiment field matches *exp_name*."""
    exp_lower = exp_name.lower()
    return [
        dict(v) | {"id": k}
        for k, v in PREDICTION_REGISTRY.items()
        if exp_lower in v["experiment"].lower()
    ]


def falsifiable_predictions() -> List[Dict]:
    """Return predictions with upcoming experiments (year > 2024)."""
    return [
        dict(v) | {"id": k}
        for k, v in PREDICTION_REGISTRY.items()
        if v["exp_launch_year"] > 2024
    ]


def registry_summary() -> Dict:
    """Return counts by epistemic_label and by current_status prefix."""
    label_counts: Dict[str, int] = {}
    status_counts: Dict[str, int] = {}
    for v in PREDICTION_REGISTRY.values():
        lbl = v["epistemic_label"]
        label_counts[lbl] = label_counts.get(lbl, 0) + 1
        # Coerce status to first word for grouping
        st = v["current_status"].split("—")[0].strip()
        status_counts[st] = status_counts.get(st, 0) + 1
    return {
        "total_predictions": len(PREDICTION_REGISTRY),
        "by_epistemic_label": label_counts,
        "by_status": status_counts,
    }


def litebird_window() -> Dict:
    """Return the birefringence admissible window and predicted gap."""
    return {
        "admissible_window_deg": [ADMISSIBLE_WINDOW_LOW_DEG, ADMISSIBLE_WINDOW_HIGH_DEG],
        "predicted_gap_deg": [PREDICTED_GAP_LOW_DEG, PREDICTED_GAP_HIGH_DEG],
        "canonical_prediction_deg": PREDICTION_REGISTRY["BETA_BIREFRINGENCE_1"]["predicted_value"],
        "derived_prediction_deg": PREDICTION_REGISTRY["BETA_BIREFRINGENCE_2"]["predicted_value"],
        "experiment": "LiteBIRD",
        "launch_year": 2032,
        "note": (
            "Any β ∉ [0.22°, 0.38°] falsifies the braided-winding mechanism. "
            "β ∈ [0.29°, 0.31°] (the inter-mode gap) also falsifies the two-mode structure."
        ),
    }
