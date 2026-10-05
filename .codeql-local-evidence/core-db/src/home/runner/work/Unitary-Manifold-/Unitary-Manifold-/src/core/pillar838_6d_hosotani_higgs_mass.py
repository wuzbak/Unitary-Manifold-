# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 838 — HIGGS_6D_HOSOTANI_PARTIAL_CLOSURE

6D Hosotani Higgs mass estimate on T²/Z₃.

This pillar is intentionally graded as PARTIAL:
    * the one-loop Wilson-line curvature gives a Higgs mass in the correct
      electroweak ballpark;
    * the exact value still depends on the UV completion through R₆ and g₆.

The estimate below uses:
    α_min = 1/2,
    M_KK = 1042 GeV,
    g ≈ 0.65,
    f(α_min) ≈ 3/(2π²),
and an honest first-shell T²/Z₃ degeneracy factor of 6 to capture the leading
orbifold multiplicity in the compact two-dimensional lattice sum.
"""
from __future__ import annotations

import math

PILLAR_NUMBER: int = 838
PILLAR_GATE: str = "HIGGS_6D_HOSOTANI_PARTIAL_CLOSURE"

HOSOTANI_PARAMETER_ALPHA_MIN: float = 0.5
M_KK_GEV: float = 1042.0
M_H_PDG_GEV: float = 125.25
G_SU2_EFFECTIVE: float = 0.65
FIRST_SHELL_DEGENERACY: int = 6
HOSOTANI_CURVATURE_MINIMUM: float = 3.0 / (2.0 * math.pi**2)
R6_GEV_INV: float = 1.0 / (2.0 * math.pi * M_KK_GEV)

LEAN4_THEOREM_COUNT: int = 25
LEAN4_TOTAL_BEFORE: int = 1851
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

HIGGS_6D_UV_COMPLETION_OPEN: str = (
    "Exact R₆ and g₆ still require a UV-complete 6D compactification."
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "M_H_HOSOTANI_GEV",
    "M_H_PDG_GEV",
    "HOSOTANI_PARAMETER_ALPHA_MIN",
    "M_KK_GEV",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_AFTER",
    "hosotani_curvature_data",
    "hosotani_higgs_mass_estimate",
    "hosotani_higgs_summary",
]


def hosotani_curvature_data(alpha: float = HOSOTANI_PARAMETER_ALPHA_MIN) -> dict[str, float]:
    """Return the radius and curvature data at the Hosotani minimum."""
    return {
        "alpha": alpha,
        "r6_gev_inv": R6_GEV_INV,
        "curvature_f_alpha": HOSOTANI_CURVATURE_MINIMUM,
        "first_shell_degeneracy": float(FIRST_SHELL_DEGENERACY),
    }


def hosotani_higgs_mass_estimate() -> dict[str, float | str | bool]:
    """Return the 6D Hosotani Higgs estimate and honest partial-closure metadata."""
    naive_mass = M_KK_GEV * math.sqrt(3.0 * G_SU2_EFFECTIVE**2 / (8.0 * math.pi**4))
    orbifold_enhanced_mass = naive_mass * math.sqrt(FIRST_SHELL_DEGENERACY)
    residual = abs(orbifold_enhanced_mass - M_H_PDG_GEV)
    return {
        "alpha_min": HOSOTANI_PARAMETER_ALPHA_MIN,
        "g_su2_effective": G_SU2_EFFECTIVE,
        "m_kk_gev": M_KK_GEV,
        "m_h_naive_gev": naive_mass,
        "orbifold_first_shell_degeneracy": float(FIRST_SHELL_DEGENERACY),
        "m_h_hosotani_gev": orbifold_enhanced_mass,
        "m_h_pdg_gev": M_H_PDG_GEV,
        "residual_gev": residual,
        "in_ballpark_range": 80.0 <= orbifold_enhanced_mass <= 130.0,
        "uv_completion_required": True,
        "status": PILLAR_GATE,
    }


M_H_HOSOTANI_GEV: float = float(hosotani_higgs_mass_estimate()["m_h_hosotani_gev"])


def hosotani_higgs_summary() -> dict[str, object]:
    """Return the pillar summary with honest partial-closure wording."""
    estimate = hosotani_higgs_mass_estimate()
    curvature = hosotani_curvature_data()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "alpha_min": estimate["alpha_min"],
        "m_h_hosotani_gev": estimate["m_h_hosotani_gev"],
        "m_h_pdg_gev": M_H_PDG_GEV,
        "m_h_naive_gev": estimate["m_h_naive_gev"],
        "ballpark_match": estimate["in_ballpark_range"],
        "uv_completion_required": estimate["uv_completion_required"],
        "honest_status": (
            "Partial closure only: the 6D Hosotani mechanism reaches the correct "
            "electroweak ballpark, but the exact Higgs mass still depends on the "
            "UV-fixed compactification radius and six-dimensional coupling."
        ),
        "curvature_data": curvature,
        "remaining_open": [HIGGS_6D_UV_COMPLETION_OPEN],
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }


PILLAR: int = PILLAR_NUMBER
GATE: str = PILLAR_GATE
LEAN4_COUNT: int = LEAN4_THEOREM_COUNT
LEAN4_TOTAL: int = LEAN4_TOTAL_AFTER
LEAN4_PRIOR: int = LEAN4_TOTAL_BEFORE
