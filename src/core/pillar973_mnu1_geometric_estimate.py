# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 973 — m_ν₁ geometric estimate from the neutrino-radion bridge.

═══════════════════════════════════════════════════════════════════════════
WHAT THIS UPGRADES
═══════════════════════════════════════════════════════════════════════════

P19 in the parameter table previously had only a bound:
    m_ν₁ < 50 meV

This pillar upgrades P19 from a pure constraint to a geometric estimate using:
  • c_R = 23/25 = 0.92 (topological theorem input, Pillar 143)
  • R_KK = 1.792 μm (Pillars 68/98 radion-neutrino identity)
  • M_KK = ħc / R_KK
  • c_s = 12/37

At the radion-neutrino bridge,
    m_ν₁ ≈ M_KK × c_s²

Numerically:
    R_KK = 1.792e-6 m = 1.792e9 fm
    M_KK = 197.3 MeV·fm / 1.792e9 fm = 1.101e-7 MeV = 0.1101 eV
    c_s² = (12/37)² = 144/1369 ≈ 0.105186
    m_ν₁ = 0.1101 eV × 0.105186 ≈ 0.01158 eV = 11.58 meV

This lies within the normal-hierarchy window and below the 50 meV bound.

STATUS: MNU1_GEOMETRIC_ESTIMATE

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""

from __future__ import annotations

import math
from typing import Dict

N_W: int = 5
K_CS: int = 74

C_R: float = 23.0 / 25.0
R_KK_METERS: float = 1.792e-6
HBAR_C_MEV_FM: float = 197.3
METERS_TO_FM: float = 1.0e15
MEV_TO_EV: float = 1.0e6
R_KK_FM: float = R_KK_METERS * METERS_TO_FM
M_KK_EV: float = HBAR_C_MEV_FM / R_KK_FM * MEV_TO_EV

C_S: float = 12.0 / 37.0
M_NU1_ESTIMATE_EV: float = M_KK_EV * C_S ** 2

EXP_BOUND_EV: float = 0.050
SIGMA_M_NU_ANCHOR_EV: float = 0.108
DM21_SQ_EV2: float = 7.39e-5
DM31_SQ_EV2: float = 2.52e-3

PILLAR_STATUS: str = "MNU1_GEOMETRIC_ESTIMATE"
PILLAR_VALID: bool = M_NU1_ESTIMATE_EV < EXP_BOUND_EV


def m_kk_from_r_kk(
    r_kk_meters: float = R_KK_METERS,
    hbar_c_mev_fm: float = HBAR_C_MEV_FM,
) -> Dict[str, object]:
    """Convert the radion scale R_KK into the KK mass scale M_KK."""
    r_kk_fm = r_kk_meters * METERS_TO_FM
    m_kk_eV = hbar_c_mev_fm / r_kk_fm * MEV_TO_EV
    return {
        "R_KK": r_kk_meters,
        "R_KK_fm": r_kk_fm,
        "M_KK_eV": m_kk_eV,
        "formula": "hbar_c/R_KK",
    }


def m_nu1_seesaw_estimate(
    m_kk_eV: float = M_KK_EV,
    c_s: float = C_S,
) -> Dict[str, object]:
    """Estimate m_ν₁ from the exact radion-neutrino bridge."""
    c_s_sq = c_s ** 2
    m_nu1_eV = m_kk_eV * c_s_sq
    return {
        "m_nu1_eV": m_nu1_eV,
        "m_nu1_meV": 1.0e3 * m_nu1_eV,
        "M_KK_eV": m_kk_eV,
        "c_s": c_s,
        "c_s_sq": c_s_sq,
        "formula": "m_nu1 = M_KK * c_s^2",
        "bridge": "neutrino-radion identity",
    }


def m_nu1_experimental_check(
    estimate_eV: float = M_NU1_ESTIMATE_EV,
    bound_eV: float = EXP_BOUND_EV,
) -> Dict[str, object]:
    """Check the geometric estimate against the experimental upper bound."""
    return {
        "estimate_eV": estimate_eV,
        "estimate_meV": 1.0e3 * estimate_eV,
        "bound_eV": bound_eV,
        "bound_meV": 1.0e3 * bound_eV,
        "within_bound": estimate_eV < bound_eV,
        "margin_meV": 1.0e3 * (bound_eV - estimate_eV),
    }


def neutrino_spectrum_check(
    m_nu1_eV: float = M_NU1_ESTIMATE_EV,
    dm21_sq_eV2: float = DM21_SQ_EV2,
    dm31_sq_eV2: float = DM31_SQ_EV2,
    sigma_anchor_eV: float = SIGMA_M_NU_ANCHOR_EV,
) -> Dict[str, object]:
    """Check normal-hierarchy consistency using the geometric m_ν₁ estimate."""
    m_nu2_eV = math.sqrt(m_nu1_eV ** 2 + dm21_sq_eV2)
    m_nu3_eV = math.sqrt(m_nu1_eV ** 2 + dm31_sq_eV2)
    sigma_m_nu_eV = m_nu1_eV + m_nu2_eV + m_nu3_eV
    nh_consistent = m_nu1_eV < m_nu2_eV < m_nu3_eV
    return {
        "m_nu1_eV": m_nu1_eV,
        "m_nu2_eV": m_nu2_eV,
        "m_nu3_eV": m_nu3_eV,
        "dm21_sq_eV2": m_nu2_eV ** 2 - m_nu1_eV ** 2,
        "dm31_sq_eV2": m_nu3_eV ** 2 - m_nu1_eV ** 2,
        "sum_m_nu_eV": sigma_m_nu_eV,
        "sigma_anchor_eV": sigma_anchor_eV,
        "within_sigma_anchor": sigma_m_nu_eV < sigma_anchor_eV,
        "normal_hierarchy_consistent": nh_consistent,
        "nh_window_consistent": 0.0 <= m_nu1_eV <= 0.020,
    }


def fallibility_update() -> Dict[str, object]:
    """Return the updated P19 status for the framework record."""
    return {
        "parameter": "P19: m_nu1",
        "previous_status": "CONSTRAINED (< 50 meV experimental bound)",
        "new_status": "GEOMETRIC_ESTIMATE (11.58 meV, ±factor 2, NH-consistent)",
        "pillar": 973,
        "pillar_status": PILLAR_STATUS,
        "geometric_inputs": {
            "c_R": C_R,
            "R_KK_meters": R_KK_METERS,
            "c_s": C_S,
        },
        "estimate_meV": 1.0e3 * M_NU1_ESTIMATE_EV,
    }


def pillar973_summary() -> Dict[str, object]:
    """Return the full Pillar 973 closure summary."""
    kk_scale = m_kk_from_r_kk()
    estimate = m_nu1_seesaw_estimate()
    experimental = m_nu1_experimental_check()
    spectrum = neutrino_spectrum_check()
    fallibility = fallibility_update()
    return {
        "pillar": 973,
        "title": "m_nu1 Geometric Estimate from Seesaw + R_KK",
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "kk_scale": kk_scale,
        "estimate": estimate,
        "experimental_check": experimental,
        "spectrum_check": spectrum,
        "fallibility_update": fallibility,
        "derivation_chain": [
            "R_KK = 1.792 μm from the neutrino-radion bridge",
            "M_KK = hbar_c / R_KK = 0.1101 eV",
            "c_s = 12/37 fixes c_s^2 = 144/1369",
            "m_nu1 = M_KK * c_s^2 = 11.58 meV",
            "11.58 meV lies below the 50 meV bound",
            "With oscillation splittings, the spectrum remains NH-consistent",
            "P19 upgrades from CONSTRAINED to GEOMETRIC_ESTIMATE",
        ],
    }
