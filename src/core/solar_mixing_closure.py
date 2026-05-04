# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/solar_mixing_closure.py
=================================
Pillar 138 — Solar Mixing Angle Closure.

Improved geometric formula for sin²θ₁₂:
    sin²θ₁₂ = 1/3 - 1/(6×n_w) + 1/(6×k_CS)
             = 1/3 - 1/30 + 1/444
             ≈ 0.302252

PDG value: 0.307   →   error ≈ 1.55%

Physical basis:
  - 1/3:       tribimaximal (TBM) leading order — exact democratic mixing
  - -1/(6n_w): winding correction from n_w = 5 orbifold geometry
  - +1/(6k_CS): Chern-Simons correction from k_CS = 74 = 5² + 7² braiding
"""

from __future__ import annotations
import math
from src.core.sm_free_parameters import (
    N_W, K_CS,
    SIN2_TH12_PMNS,
)

__all__ = [
    "solar_mixing_angle_corrected",
    "solar_mixing_decomposition",
    "solar_mixing_closure_status",
]

_TBM_TERM: float = 1.0 / 3.0
_NW_CORRECTION_DENOM: int = 6
_KCS_CORRECTION_DENOM: int = 6


def solar_mixing_angle_corrected(n_w: int = 5, k_cs: int = 74) -> dict:
    """Return the corrected solar mixing angle and error vs PDG.

    Formula:  sin²θ₁₂ = 1/3 - 1/(6 n_w) + 1/(6 k_cs)

    Returns
    -------
    dict with keys:
        sin2_th12       : float  — predicted value
        pct_error       : float  — |pred - PDG| / PDG × 100
        tbm_term        : float  — 1/3
        nw_correction   : float  — -1/(6 n_w)
        kcs_correction  : float  — +1/(6 k_cs)
        derivation      : str
    """
    tbm_term = 1.0 / 3.0
    nw_correction = -1.0 / (6.0 * n_w)
    kcs_correction = 1.0 / (6.0 * k_cs)
    sin2_th12 = tbm_term + nw_correction + kcs_correction
    pct_error = abs(sin2_th12 - SIN2_TH12_PMNS) / SIN2_TH12_PMNS * 100.0
    return {
        "sin2_th12": sin2_th12,
        "pct_error": pct_error,
        "tbm_term": tbm_term,
        "nw_correction": nw_correction,
        "kcs_correction": kcs_correction,
        "derivation": (
            f"sin²θ₁₂ = 1/3 - 1/(6×{n_w}) + 1/(6×{k_cs})"
            f" = {tbm_term:.6f} {nw_correction:+.6f} {kcs_correction:+.6f}"
            f" = {sin2_th12:.6f}  (PDG {SIN2_TH12_PMNS}, error {pct_error:.3f}%)"
        ),
    }


def solar_mixing_decomposition() -> dict:
    """Return the three-term decomposition with physical basis."""
    tbm = 1.0 / 3.0
    nw_corr = -1.0 / (6.0 * N_W)
    kcs_corr = 1.0 / (6.0 * K_CS)
    return {
        "tbm_term": {
            "value": tbm,
            "fraction": "1/3",
            "basis": "Tribimaximal (TBM) leading order — democratic mixing in 3 generations",
        },
        "nw_correction": {
            "value": nw_corr,
            "fraction": f"-1/(6×{N_W}) = -1/30",
            "basis": f"Winding correction from n_w={N_W} orbifold geometry",
        },
        "kcs_correction": {
            "value": kcs_corr,
            "fraction": f"+1/(6×{K_CS}) = +1/444",
            "basis": f"Chern-Simons correction from k_CS={K_CS} = 5²+7² braiding resonance",
        },
        "total": tbm + nw_corr + kcs_corr,
        "pdg": SIN2_TH12_PMNS,
    }


def solar_mixing_closure_status() -> dict:
    """Return closure status for Pillar 138."""
    result = solar_mixing_angle_corrected()
    return {
        "pillar": 138,
        "parameter": "sin²θ₁₂ (PMNS solar mixing angle)",
        "status": f"GEOMETRIC PREDICTION ({result['pct_error']:.2f}%)",
        "predicted": result["sin2_th12"],
        "pdg": SIN2_TH12_PMNS,
        "pct_error": result["pct_error"],
        "formula": "1/3 - 1/(6 n_w) + 1/(6 k_CS)",
        "inputs": ["n_w=5 (from Planck n_s)", "k_CS=74=5²+7² (from birefringence)"],
        "closed": True,
    }
