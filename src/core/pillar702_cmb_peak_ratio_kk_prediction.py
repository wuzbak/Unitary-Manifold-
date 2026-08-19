# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar702_cmb_peak_ratio_kk_prediction.py
===================================================
Pillar 702 — CMB Peak Ratio KK Prediction

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict

PILLAR_NUMBER = 702
N_W = 5
K_CS = 74
C_S = 12.0 / 37.0
DELTA_KK = 8.0e-4
LCDM_RATIO_2_TO_1 = 0.72
LCDM_RATIO_3_TO_1 = 0.55
PLANCK_RATIO_2_TO_1 = 0.72
PLANCK_RATIO_3_TO_1 = 0.55

__all__ = [
    "PILLAR_NUMBER",
    "N_W",
    "K_CS",
    "C_S",
    "DELTA_KK",
    "LCDM_RATIO_2_TO_1",
    "peak_height_ratios_um",
    "peak_ratio_kk_correction",
    "peak_ratio_planck_comparison",
]


def peak_ratio_kk_correction() -> Dict[str, float]:
    """Return the KK correction to acoustic peak ratios."""
    delta_ratio = C_S ** 2 * DELTA_KK / (2.0 * math.pi ** 2)
    return {
        "delta_ratio": delta_ratio,
        "formula": "c_s^2 * delta_kk / (2*pi^2)",
    }


def peak_height_ratios_um() -> Dict[str, float]:
    """Predict UM peak-height ratios 1:2:3 with the KK correction."""
    delta_ratio = peak_ratio_kk_correction()["delta_ratio"]
    ratio_2_to_1 = LCDM_RATIO_2_TO_1 * (1.0 + delta_ratio)
    ratio_3_to_1 = LCDM_RATIO_3_TO_1 * (1.0 + 2.0 * delta_ratio)
    return {
        "peak1": 1.0,
        "peak2": ratio_2_to_1,
        "peak3": ratio_3_to_1,
        "ratio_2_to_1": ratio_2_to_1,
        "ratio_3_to_1": ratio_3_to_1,
    }


def peak_ratio_planck_comparison() -> Dict[str, object]:
    """Compare the UM peak-ratio prediction to Planck-style reference ratios."""
    ratios = peak_height_ratios_um()
    return {
        "pillar": PILLAR_NUMBER,
        "um_ratios": ratios,
        "planck_reference": {
            "ratio_2_to_1": PLANCK_RATIO_2_TO_1,
            "ratio_3_to_1": PLANCK_RATIO_3_TO_1,
        },
        "delta_vs_planck": {
            "ratio_2_to_1": ratios["ratio_2_to_1"] - PLANCK_RATIO_2_TO_1,
            "ratio_3_to_1": ratios["ratio_3_to_1"] - PLANCK_RATIO_3_TO_1,
        },
        "status": "KK_RATIO_SHIFT_TINY_BUT_DEFINED",
    }
