# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar694_alpha_s_rge_kk_tower_nlo.py
==============================================
Pillar 694 — α_s RGE KK Tower NLO

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
    "M_Z_GEV",
    "M_KK_MEV",
    "M_KK_GEV",
    "PI",
    "beta_function_kk_corrected",
    "alpha_s_nlo_kk_tower",
    "nlo_residual",
]

N_W: int = 5
K_CS: int = 74
N_C: int = 3
ALPHA_S_PDG_MZ: float = 0.1180
M_Z_GEV: float = 91.1876
M_KK_MEV: float = 110.0
M_KK_GEV: float = M_KK_MEV / 1000.0
PI: float = math.pi
ALPHA_S_KK_GEOMETRIC: float = 2.0 * PI / (N_C * K_CS)
PILLAR_NUMBER: str = "694"


def beta_function_kk_corrected() -> Dict[str, Any]:
    """Return the SM and KK-corrected one-loop beta coefficients."""
    b_0_sm = (11.0 * 3.0 - 2.0 * 6.0 / 2.0 - 0.5) / (2.0 * PI)
    kk_increment = N_W / (2.0 * PI)
    b_0_kk = b_0_sm + kk_increment
    return {
        "b_0_sm": b_0_sm,
        "b_0_kk": b_0_kk,
        "kk_increment": kk_increment,
        "b_0_sm_formula": "(11*3 - 2*6/2 - 1/2)/(2π)",
        "b_0_kk_formula": "b_0_sm + n_w/(2π)",
        "alpha_s_kk": ALPHA_S_KK_GEOMETRIC,
    }


def alpha_s_nlo_kk_tower() -> Dict[str, Any]:
    """Run α_s from M_KK to M_Z with the KK-corrected NLO denominator."""
    beta_data = beta_function_kk_corrected()
    alpha_s_kk = beta_data["alpha_s_kk"]
    log_ratio = math.log((M_Z_GEV ** 2) / (M_KK_GEV ** 2))
    denominator = 1.0 + (beta_data["b_0_kk"] / (2.0 * PI)) * alpha_s_kk * log_ratio
    alpha_s_mz_nlo = alpha_s_kk / denominator
    residual_pct = abs(alpha_s_mz_nlo - ALPHA_S_PDG_MZ) / ALPHA_S_PDG_MZ * 100.0
    return {
        "pillar": PILLAR_NUMBER,
        "alpha_s_kk": alpha_s_kk,
        "alpha_s_mz_nlo": alpha_s_mz_nlo,
        "alpha_s_pdg_mz": ALPHA_S_PDG_MZ,
        "log_mz2_over_mkk2": log_ratio,
        "denominator": denominator,
        "residual_pct": residual_pct,
        "verdict": "MECHANISM_FOUND" if residual_pct < 10.0 else "IRREDUCIBLE",
        "note": (
            f"The full KK-tower correction increases b₀ to {beta_data['b_0_kk']:.4f}, "
            f"but the large log ln(M_Z²/M_KK²)={log_ratio:.3f} still leaves "
            f"α_s(M_Z)≈{alpha_s_mz_nlo:.5f}, far below PDG."
        ),
    }


def nlo_residual() -> Dict[str, Any]:
    """Return the Pillar 694 residual certificate."""
    result = alpha_s_nlo_kk_tower()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "α_s RGE KK Tower NLO",
        "status": "ARCHITECTURE_LIMIT_CERTIFIED" if result["verdict"] == "IRREDUCIBLE" else "MECHANISM_FOUND",
        "beta_function": beta_function_kk_corrected(),
        "result": result,
        "honest_statement": (
            "Including the KK tower at NLO shifts the running modestly but does "
            "not close the α_s residual below the 10% mechanism-found threshold."
        ),
    }
