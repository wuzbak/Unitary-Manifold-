# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar696_alpha_s_lhc_run4_discriminator.py
====================================================
Pillar 696 — α_s LHC Run 4 Discriminator

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Any, Dict

__all__ = [
    "N_W",
    "K_CS",
    "ALPHA_S_PDG_MZ",
    "SQRT_S_TEV",
    "PI",
    "alpha_s_kk_prediction",
    "lhc_run4_snr",
    "alpha_s_preregistration",
]

N_W: int = 5
K_CS: int = 74
ALPHA_S_PDG_MZ: float = 0.1180
SQRT_S_TEV: float = 13.6
RELATIVE_PRECISION_RUN4: float = 0.003
PI: float = math.pi
PILLAR_NUMBER: str = "696"


def alpha_s_kk_prediction() -> Dict[str, Any]:
    """Conservative KK-threshold α_s shift relevant for LHC Run 4."""
    threshold_fraction = N_W / (2.0 * K_CS * PI)
    delta_alpha_s = -ALPHA_S_PDG_MZ * threshold_fraction
    alpha_s_kk = ALPHA_S_PDG_MZ + delta_alpha_s
    return {
        "pillar": PILLAR_NUMBER,
        "alpha_s_sm": ALPHA_S_PDG_MZ,
        "alpha_s_kk": alpha_s_kk,
        "delta_alpha_s": delta_alpha_s,
        "threshold_fraction": threshold_fraction,
        "sign": "negative",
        "expected_shift_scale": "O(10^-3)",
        "note": (
            "Positive winding n_w>0 lowers the effective high-pT α_s prediction, "
            f"giving Δα_s≈{delta_alpha_s:.6f}."
        ),
    }


def lhc_run4_snr() -> Dict[str, Any]:
    """Signal-to-noise estimate for the KK threshold signature at Run 4."""
    prediction = alpha_s_kk_prediction()
    experimental_sigma = RELATIVE_PRECISION_RUN4 * ALPHA_S_PDG_MZ
    snr = abs(prediction["delta_alpha_s"]) / experimental_sigma
    return {
        "pillar": PILLAR_NUMBER,
        "sqrt_s_tev": SQRT_S_TEV,
        "experimental_sigma_alpha_s": experimental_sigma,
        "delta_alpha_s": prediction["delta_alpha_s"],
        "snr": snr,
        "detectable": snr > 1.0,
        "note": (
            f"A {RELATIVE_PRECISION_RUN4:.1%} measurement implies σ(α_s)≈{experimental_sigma:.6f}, "
            f"so the KK signature has SNR≈{snr:.2f}."
        ),
    }


def alpha_s_preregistration() -> Dict[str, Any]:
    """Pre-register the full-sign benchmark shift for Run 4 comparisons."""
    alpha_s_um = ALPHA_S_PDG_MZ * (1.0 - N_W / (K_CS * PI))
    delta_alpha_s = alpha_s_um - ALPHA_S_PDG_MZ
    return {
        "pillar": PILLAR_NUMBER,
        "status": "PREREGISTERED",
        "alpha_s_pdg_mz": ALPHA_S_PDG_MZ,
        "alpha_s_um": alpha_s_um,
        "delta_alpha_s": delta_alpha_s,
        "formula": "alpha_s_pdg * (1 - n_w/(k_CS*pi))",
        "channel": "high-pT α_s at sqrt(s)=13.6 TeV",
        "prediction_sign": "negative",
    }
