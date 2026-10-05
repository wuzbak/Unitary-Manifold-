# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar700_cmb_s4_kk_residual_forecast.py
==================================================
Pillar 700 — CMB-S4 / LiteBIRD KK Residual Forecast

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict

PILLAR_NUMBER = 700
N_W = 5
K_CS = 74
C_S = 12.0 / 37.0
DELTA_KK = 8.0e-4
A_S_LCDM = 2.10e-9
N_S = 0.9649
Z_PHI_PHASE1 = 5.30
SIGMA_PIXEL_CMB_S4 = 1.0
SIGMA_PIXEL_LITEBIRD = 2.0
OBSERVED_SUPPRESSION_CENTRAL = 5.5

__all__ = [
    "PILLAR_NUMBER",
    "N_W",
    "K_CS",
    "C_S",
    "DELTA_KK",
    "SIGMA_PIXEL_CMB_S4",
    "SIGMA_PIXEL_LITEBIRD",
    "kk_cmb_s4_snr",
    "kk_litebird_snr",
    "cmb_residual_after_phase2",
]


def _zphi_total() -> float:
    return Z_PHI_PHASE1 * (1.0 + N_W * C_S ** 2 / (4.0 * math.pi ** 2))


def _baseline_cl(ell: int) -> float:
    tilt = (max(ell, 2) / 100.0) ** (N_S - 1.0)
    acoustic = max(0.35, 1.0 + 0.18 * math.cos(math.pi * (ell - 200.0) / 340.0))
    damping = math.exp(-ell / 1800.0)
    return A_S_LCDM * tilt * acoustic * damping


def _snr_for_range(ell_min: int, ell_max: int, sigma_pixel: float) -> Dict[str, float]:
    snr_sq = 0.0
    dominant_ell = ell_min
    dominant_weight = -1.0
    noise_floor = (sigma_pixel * 1.0e-6) ** 2
    for ell in range(ell_min, ell_max + 1):
        c_ell = _baseline_cl(ell)
        fractional = DELTA_KK * (ell / 100.0) ** 2
        delta_c_ell = fractional * c_ell
        sigma_c_ell = math.sqrt(2.0 / (2.0 * ell + 1.0)) * c_ell + noise_floor
        weight = (delta_c_ell / sigma_c_ell) ** 2
        snr_sq += weight
        if weight > dominant_weight:
            dominant_weight = weight
            dominant_ell = ell
    return {
        "ell_min": float(ell_min),
        "ell_max": float(ell_max),
        "sigma_pixel_uK_arcmin": sigma_pixel,
        "snr": math.sqrt(snr_sq),
        "snr_squared": snr_sq,
        "dominant_ell": float(dominant_ell),
    }


def kk_cmb_s4_snr() -> Dict[str, float]:
    """Forecast KK detectability for CMB-S4 up to ell=3000."""
    result = _snr_for_range(2, 3000, SIGMA_PIXEL_CMB_S4)
    result["experiment"] = "CMB-S4"
    return result


def kk_litebird_snr() -> Dict[str, float]:
    """Forecast KK detectability for LiteBIRD up to ell=500."""
    result = _snr_for_range(2, 500, SIGMA_PIXEL_LITEBIRD)
    result["experiment"] = "LiteBIRD"
    return result


def cmb_residual_after_phase2() -> Dict[str, float]:
    """Return the residual amplitude mismatch after Phase 2 Z_phi closure."""
    z_total = _zphi_total()
    predicted_ratio = 1.0 / z_total
    observed_ratio = 1.0 / OBSERVED_SUPPRESSION_CENTRAL
    residual = predicted_ratio - observed_ratio
    return {
        "predicted_ratio": predicted_ratio,
        "observed_ratio": observed_ratio,
        "residual": residual,
        "residual_percent_of_observed": abs(residual) / observed_ratio * 100.0,
        "z_phi_total": z_total,
    }
