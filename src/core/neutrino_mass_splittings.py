# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/neutrino_mass_splittings.py
=====================================
Pillar 135 — Neutrino Mass Splittings from RS Dirac Zero-Mode Framework.

Physical Context
----------------
The two neutrino mass-squared differences:

    Δm²₂₁ = 7.53 × 10⁻⁵ eV²   (solar)
    Δm²₃₁ = 2.453 × 10⁻³ eV²  (atmospheric)

were previously labeled ❌ OPEN in the SM parameter table because the RS Dirac
zero-mode masses had not been formally connected to the braid geometry.  This
Pillar closes them to ⚠️ CONSTRAINED by:

  1. Deriving the three neutrino bulk-mass parameters c_L^{ν_i} from the
     braid geometry via the UM generation step δc_ν.
  2. Expressing the masses through the RS Dirac zero-mode formula.
  3. Predicting the splitting ratio Δm²₃₁/Δm²₂₁ from pure geometry (10% accuracy).
  4. Fixing the absolute scale from one PDG input (Δm²₂₁) and predicting Δm²₃₁.
  5. Checking consistency with Σm_ν < 120 meV (Planck).

RS Dirac Zero-Mode Mass Formula
---------------------------------
In the RS1 model, bulk fermions with 5D bulk mass M_bulk = c × k have a
zero-mode wavefunction profile on the IR brane:

    f₀(c) = √[(2c − 1) × k / (exp((2c−1) × πkR) − 1)]

where c > 1/2 for UV-localized modes (appropriate for light neutrinos).
In the limit (2c−1) × πkR >> 1:

    f₀(c) ≈ √[(2c−1) × k] × exp(−(c − 1/2) × πkR)

The 4D Dirac neutrino mass is then:

    m_νi = y_ν × v × f₀(c_L^{ν_i}) × f₀(c_R^{ν_i})

where y_ν is the 5D Yukawa coupling at the IR brane and v = 246 GeV is the
Higgs VEV.

Braid Geometry of the c_L^{ν_i} Parameters
-------------------------------------------
In the UM, the generation step between adjacent neutrino left-handed bulk mass
parameters is determined by the (n₁, n₂) = (5, 7) braid pair:

    δc_ν = ln(n₁ × n₂) / (2 × πkR) = ln(35) / (2 × 37) ≈ 0.04804

Physical origin: the braid winding cross-section √(n₁n₂) sets the ratio of
zero-mode profiles between adjacent generations.  Specifically:

    f₀(c_{n+1}) / f₀(c_n) ≈ exp(−δc_ν × πkR) = exp(−½ ln(n₁n₂)) = 1/√(n₁n₂)

For (n₁, n₂) = (5, 7): each step reduces the wavefunction (and hence mass)
by a factor of 1/√35 ≈ 0.169.

Normal-Hierarchy Mass Spectrum
-------------------------------
With c₁ > c₂ > c₃ (most UV-localized = lightest = ν₁):

    Bulk mass parameters: c₃ = c_base, c₂ = c_base + δc, c₁ = c_base + 2δc

    Mass ratios (purely geometric):
        m_ν₂ / m_ν₁ = √(n₁n₂) = √35  ≈  5.916
        m_ν₃ / m_ν₁ = n₁n₂ = 35

    Mass-squared splitting ratio (pure geometry):
        Δm²₃₁ / Δm²₂₁ = (m_ν₃² − m_ν₁²) / (m_ν₂² − m_ν₁²)
                        = ((n₁n₂)² − 1) / (n₁n₂ − 1)
                        = n₁n₂ + 1 = 36
        PDG ratio: 2.453e−3 / 7.53e−5 ≈ 32.6
        Accuracy: 10 %

Honest Status
-------------
  - The splitting RATIO Δm²₃₁/Δm²₂₁ = 36 is a pure geometric prediction
    (0 free parameters) with 10 % accuracy — ⚠️ CONSTRAINED.
  - The absolute scale requires one input (Δm²₂₁) to fix m_ν₁, then predicts
    Δm²₃₁ at 10 % accuracy — ⚠️ CONSTRAINED.
  - A fully zero-parameter derivation requires independently deriving the
    absolute neutrino mass scale from the RS Yukawa (y_ν) and right-handed
    bulk masses c_R^{ν_i} — still OPEN.

The improvement over the previous ❌ OPEN status: we now have a formal RS
Dirac framework connecting the c_L^{ν_i} parameters to the braid geometry,
and a parameter-free prediction of the splitting ratio (10% accuracy).

Public API
----------
neutrino_generation_step(n1, n2, pi_kr) → float
    δc_ν = ln(n₁n₂) / (2πkR).

rs_dirac_zero_mode_profile(c, pi_kr) → float
    f₀(c) = √[(2c−1)/(exp((2c−1)πkR)−1)].

rs_neutrino_mass_ratio(n1, n2) → dict
    Mass ratios m_ν₂/m_ν₁ and m_ν₃/m_ν₁ from braid geometry.

neutrino_c_parameters(c_base, n1, n2, pi_kr) → dict
    The three c_L^{ν_i} values from braid geometry and c_base.

neutrino_mass_splittings_rs(n1, n2, pi_kr, dm2_21_input_ev2) → dict
    Full RS Dirac derivation of Δm²₂₁, Δm²₃₁ with predictions and residuals.

neutrino_sum_constraint(n1, n2, dm2_21_ev2) → dict
    Verify Σm_ν < 120 meV.

pillar135_summary() → dict
    Structured closure status.

Code architecture, test suites, document engineering, and synthesis:
"""

from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
}

import math
from typing import Dict

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------

#: Canonical braided pair (Pillar 58)
N1_CANONICAL: int = 5
N2_CANONICAL: int = 7

#: RS compactification: πkR (Pillar 81)
PI_KR_CANONICAL: float = 37.0

#: PDG 2024 solar mass-squared splitting [eV²]
DM2_21_PDG_EV2: float = 7.53e-5

#: PDG 2024 atmospheric mass-squared splitting [eV²]
DM2_31_PDG_EV2: float = 2.453e-3

#: PDG ratio Δm²₃₁/Δm²₂₁
DM2_RATIO_PDG: float = DM2_31_PDG_EV2 / DM2_21_PDG_EV2  # ≈ 32.57

#: Planck CMB neutrino mass sum upper limit [eV]
SUM_MNU_PLANCK_EV: float = 0.12

#: Geometric prediction for splitting ratio: n₁n₂ + 1
DM2_RATIO_GEO: float = float(N1_CANONICAL * N2_CANONICAL + 1)  # = 36


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def neutrino_generation_step(
    n1: int = N1_CANONICAL,
    n2: int = N2_CANONICAL,
    pi_kr: float = PI_KR_CANONICAL,
) -> float:
    """Compute the neutrino bulk-mass generation step δc_ν.

    δc_ν = ln(n₁ × n₂) / (2 × πkR)

    Parameters
    ----------
    n1, n2 : int   Braided winding numbers.
    pi_kr  : float πkR (default 37.0).

    Returns
    -------
    float
        δc_ν (dimensionless).
    """
    if n1 <= 0 or n2 <= 0:
        raise ValueError(f"Winding numbers must be positive; got n1={n1}, n2={n2}.")
    if pi_kr <= 0:
        raise ValueError(f"pi_kr must be positive; got {pi_kr}.")
    return math.log(float(n1 * n2)) / (2.0 * pi_kr)


def rs_dirac_zero_mode_profile(
    c: float,
    pi_kr: float = PI_KR_CANONICAL,
) -> float:
    """Compute the RS Dirac zero-mode wavefunction profile f₀(c).

    f₀(c) = √[(2c−1) / (exp((2c−1) × πkR) − 1)]

    Valid for c > 1/2 (UV-localized modes).  For the limit (2c−1)πkR >> 1:
    f₀(c) ≈ √(2c−1) × exp(−(c−1/2) × πkR).

    Parameters
    ----------
    c      : float  Bulk mass parameter c > 1/2.
    pi_kr  : float  πkR (default 37.0).

    Returns
    -------
    float
        f₀(c) — zero-mode profile value (positive).
    """
    if c <= 0.5:
        raise ValueError(
            f"c must be > 1/2 for UV-localized neutrino zero modes; got c={c}."
        )
    if pi_kr <= 0:
        raise ValueError(f"pi_kr must be positive; got {pi_kr}.")
    x = (2.0 * c - 1.0) * pi_kr
    # Protect against overflow: for large x, exp(x) - 1 ≈ exp(x)
    if x > 500:
        return math.sqrt(2.0 * c - 1.0) * math.exp(-0.5 * x)
    return math.sqrt((2.0 * c - 1.0) / (math.exp(x) - 1.0))


def rs_neutrino_mass_ratio(
    n1: int = N1_CANONICAL,
    n2: int = N2_CANONICAL,
) -> Dict[str, object]:
    """Return geometric neutrino mass ratios from the braid winding pair.

    Mass ratios (normal hierarchy):
        m_ν₂ / m_ν₁ = √(n₁n₂) = √35 ≈ 5.916
        m_ν₃ / m_ν₁ = n₁n₂ = 35

    Splitting ratio (pure geometry):
        Δm²₃₁ / Δm²₂₁ = n₁n₂ + 1 = 36

    Parameters
    ----------
    n1, n2 : int  Braid winding numbers (default 5, 7).

    Returns
    -------
    dict
        'm32_over_m21'    : float — m_ν₂/m_ν₁ = √(n₁n₂).
        'm31_over_m11'    : float — m_ν₃/m_ν₁ = n₁n₂.
        'splitting_ratio_geo' : float — Δm²₃₁/Δm²₂₁ = n₁n₂+1.
        'splitting_ratio_pdg' : float — PDG ratio.
        'splitting_ratio_pct_err': float — accuracy.
    """
    if n1 <= 0 or n2 <= 0:
        raise ValueError("Winding numbers must be positive.")
    bp = n1 * n2
    m21_ratio = math.sqrt(float(bp))
    m31_ratio = float(bp)
    split_geo = float(bp + 1)
    split_err = abs(split_geo - DM2_RATIO_PDG) / DM2_RATIO_PDG * 100.0

    return {
        "n1": n1,
        "n2": n2,
        "braid_product": bp,
        "m_nu2_over_m_nu1": m21_ratio,
        "m_nu3_over_m_nu1": m31_ratio,
        "splitting_ratio_geo": split_geo,
        "splitting_ratio_pdg": DM2_RATIO_PDG,
        "splitting_ratio_pct_err": split_err,
        "derivation": (
            f"m_ν₂/m_ν₁ = √(n₁n₂) = √{bp} = {m21_ratio:.4f}. "
            f"m_ν₃/m_ν₁ = n₁n₂ = {bp}. "
            f"Δm²₃₁/Δm²₂₁ = n₁n₂+1 = {split_geo:.0f}. "
            f"PDG {DM2_RATIO_PDG:.1f}. Accuracy: {split_err:.0f}%."
        ),
    }


def neutrino_c_parameters(
    c_base: float = 0.68,
    n1: int = N1_CANONICAL,
    n2: int = N2_CANONICAL,
    pi_kr: float = PI_KR_CANONICAL,
) -> Dict[str, object]:
    """Derive the three neutrino bulk-mass parameters from braid geometry.

    The generation step δc_ν = ln(n₁n₂)/(2πkR) separates adjacent
    neutrino c_L values.  In the normal hierarchy:
        c_ν₁ = c_base + 2δc  (lightest, most UV-localized)
        c_ν₂ = c_base + δc
        c_ν₃ = c_base         (heaviest, least UV-localized)

    Parameters
    ----------
    c_base : float  Base bulk mass parameter (default 0.68).
    n1, n2 : int    Braid winding numbers.
    pi_kr  : float  πkR.

    Returns
    -------
    dict
        'c_nu1', 'c_nu2', 'c_nu3' : float — bulk mass parameters.
        'delta_c'                  : float — generation step δc_ν.
        'f0_nu1', 'f0_nu2', 'f0_nu3': float — zero-mode profiles.
    """
    if n1 <= 0 or n2 <= 0:
        raise ValueError("Winding numbers must be positive.")
    dc = neutrino_generation_step(n1, n2, pi_kr)
    c1 = c_base + 2.0 * dc
    c2 = c_base + dc
    c3 = c_base
    f0_1 = rs_dirac_zero_mode_profile(c1, pi_kr)
    f0_2 = rs_dirac_zero_mode_profile(c2, pi_kr)
    f0_3 = rs_dirac_zero_mode_profile(c3, pi_kr)
    return {
        "c_base": c_base,
        "delta_c": dc,
        "c_nu1": c1,
        "c_nu2": c2,
        "c_nu3": c3,
        "f0_nu1": f0_1,
        "f0_nu2": f0_2,
        "f0_nu3": f0_3,
        "profile_ratio_21": f0_2 / f0_1 if f0_1 > 0 else float("inf"),
        "profile_ratio_31": f0_3 / f0_1 if f0_1 > 0 else float("inf"),
        "derivation": (
            f"δc_ν = ln({n1}×{n2})/(2×{pi_kr}) = {dc:.5f}. "
            f"c_ν₁ = {c1:.5f}, c_ν₂ = {c2:.5f}, c_ν₃ = {c3:.5f}. "
            f"f₀(c₁) = {f0_1:.4e}, f₀(c₂) = {f0_2:.4e}, f₀(c₃) = {f0_3:.4e}."
        ),
    }


def neutrino_mass_splittings_rs(
    n1: int = N1_CANONICAL,
    n2: int = N2_CANONICAL,
    pi_kr: float = PI_KR_CANONICAL,
    dm2_21_input_ev2: float = DM2_21_PDG_EV2,
) -> Dict[str, object]:
    """Derive Δm²₂₁ and Δm²₃₁ from the RS Dirac zero-mode framework.

    Uses the braid geometry to set the neutrino mass hierarchy, then fixes
    the absolute scale from the input Δm²₂₁.

    Derivation
    ----------
    1. Braid geometry gives: m_ν₂/m_ν₁ = √(n₁n₂), m_ν₃/m_ν₁ = n₁n₂.
    2. From Δm²₂₁ (input): m_ν₁ = √(Δm²₂₁ / (n₁n₂ − 1)).
    3. Geometric prediction: Δm²₃₁ = (n₁n₂² − 1) × m_ν₁² = (n₁n₂ + 1) × Δm²₂₁.

    Parameters
    ----------
    n1, n2           : int   Braid winding numbers (default 5, 7).
    pi_kr            : float πkR (default 37.0).
    dm2_21_input_ev2 : float Δm²₂₁ input [eV²] (default PDG 7.53×10⁻⁵ eV²).

    Returns
    -------
    dict
        'm_nu1_eV', 'm_nu2_eV', 'm_nu3_eV': float — neutrino masses [eV].
        'dm2_21_geo_eV2'  : float — geometric Δm²₂₁ (= input, by construction).
        'dm2_31_geo_eV2'  : float — geometric Δm²₃₁ prediction [eV²].
        'dm2_31_pdg_eV2'  : float — PDG Δm²₃₁ [eV²].
        'dm2_31_pct_err'  : float — accuracy of Δm²₃₁ prediction [%].
        'splitting_ratio_geo' : float — Δm²₃₁/Δm²₂₁ (should be ≈ 36).
        'splitting_ratio_pdg' : float — PDG ratio.
        'sum_mnu_eV'      : float — Σm_ν [eV].
        'planck_consistent': bool — Σm_ν < 0.12 eV.
        'status'          : str.
    """
    if n1 <= 0 or n2 <= 0:
        raise ValueError("Winding numbers must be positive.")
    if dm2_21_input_ev2 <= 0:
        raise ValueError("dm2_21_input_ev2 must be positive.")

    bp = n1 * n2       # 35
    r = math.sqrt(float(bp))  # √35

    # Absolute scale from Δm²₂₁
    m_nu1_sq = dm2_21_input_ev2 / float(bp - 1)  # / 34
    m_nu1 = math.sqrt(m_nu1_sq)
    m_nu2 = r * m_nu1
    m_nu3 = float(bp) * m_nu1

    # Geometric Δm² predictions
    dm2_21_geo = m_nu2 ** 2 - m_nu1 ** 2
    dm2_31_geo = m_nu3 ** 2 - m_nu1 ** 2

    dm2_31_pct_err = abs(dm2_31_geo - DM2_31_PDG_EV2) / DM2_31_PDG_EV2 * 100.0
    split_ratio_geo = dm2_31_geo / dm2_21_input_ev2
    split_ratio_pdg = DM2_RATIO_PDG

    split_ratio_pct = abs(split_ratio_geo - split_ratio_pdg) / split_ratio_pdg * 100.0

    sum_mnu = m_nu1 + m_nu2 + m_nu3
    planck_ok = sum_mnu < SUM_MNU_PLANCK_EV

    dc = neutrino_generation_step(n1, n2, pi_kr)

    if dm2_31_pct_err < 5.0:
        status = "✅ DERIVED — Δm²₃₁ predicted to < 5%"
    elif dm2_31_pct_err < 15.0:
        status = "⚠️ CONSTRAINED — Δm²₃₁ predicted to ~10% accuracy"
    else:
        status = f"⚠️ ESTIMATE — {dm2_31_pct_err:.0f}% accuracy on Δm²₃₁"

    return {
        "n1": n1,
        "n2": n2,
        "braid_product": bp,
        "delta_c": dc,
        "m_nu1_eV": m_nu1,
        "m_nu2_eV": m_nu2,
        "m_nu3_eV": m_nu3,
        "dm2_21_input_eV2": dm2_21_input_ev2,
        "dm2_21_geo_eV2": dm2_21_geo,
        "dm2_31_geo_eV2": dm2_31_geo,
        "dm2_31_pdg_eV2": DM2_31_PDG_EV2,
        "dm2_31_pct_err": dm2_31_pct_err,
        "splitting_ratio_geo": split_ratio_geo,
        "splitting_ratio_pdg": split_ratio_pdg,
        "splitting_ratio_pct_err": split_ratio_pct,
        "sum_mnu_eV": sum_mnu,
        "planck_consistent": planck_ok,
        "status": status,
        "derivation": (
            f"Braid product n₁n₂ = {bp}; r = √{bp} = {r:.4f}.\n"
            f"Generation step: δc_ν = ln({bp})/(2×{pi_kr}) = {dc:.5f}.\n"
            f"From Δm²₂₁ = {dm2_21_input_ev2:.3e} eV²: "
            f"m_ν₁ = √(Δm²₂₁/{bp-1}) = {m_nu1*1e3:.3f} meV.\n"
            f"m_ν₂ = √{bp} × m_ν₁ = {m_nu2*1e3:.3f} meV, "
            f"m_ν₃ = {bp} × m_ν₁ = {m_nu3*1e3:.3f} meV.\n"
            f"Δm²₃₁ = {dm2_31_geo:.4e} eV² (PDG {DM2_31_PDG_EV2:.4e} eV², "
            f"{dm2_31_pct_err:.1f}% off).\n"
            f"Σm_ν = {sum_mnu*1e3:.2f} meV "
            f"{'< 120 meV ✓' if planck_ok else '> 120 meV ✗'}."
        ),
    }


def neutrino_sum_constraint(
    n1: int = N1_CANONICAL,
    n2: int = N2_CANONICAL,
    dm2_21_ev2: float = DM2_21_PDG_EV2,
) -> Dict[str, object]:
    """Verify the neutrino mass sum constraint Σm_ν < 120 meV.

    Parameters
    ----------
    n1, n2     : int    Braid winding numbers.
    dm2_21_ev2 : float  Solar mass splitting [eV²].

    Returns
    -------
    dict
        'sum_mnu_eV'      : float — Σm_ν [eV].
        'planck_limit_eV' : float — Planck limit [eV].
        'consistent'      : bool.
        'headroom_meV'    : float — remaining headroom [meV].
    """
    result = neutrino_mass_splittings_rs(n1, n2, PI_KR_CANONICAL, dm2_21_ev2)
    sum_mnu = result["sum_mnu_eV"]
    headroom = SUM_MNU_PLANCK_EV - sum_mnu
    return {
        "n1": n1,
        "n2": n2,
        "sum_mnu_eV": sum_mnu,
        "planck_limit_eV": SUM_MNU_PLANCK_EV,
        "consistent": sum_mnu < SUM_MNU_PLANCK_EV,
        "headroom_meV": headroom * 1000.0,
        "m_nu1_meV": result["m_nu1_eV"] * 1000.0,
        "m_nu2_meV": result["m_nu2_eV"] * 1000.0,
        "m_nu3_meV": result["m_nu3_eV"] * 1000.0,
    }


def pillar135_summary() -> Dict[str, object]:
    """Return a structured summary of Pillar 135 closure status.

    Returns
    -------
    dict
        Full closure status for documentation and audit tools.
    """
    result = neutrino_mass_splittings_rs()
    ratios = rs_neutrino_mass_ratio()
    constraint = neutrino_sum_constraint()

    return {
        "pillar": 135,
        "title": "Neutrino Mass Splittings — RS Dirac Zero-Mode Framework",
        "braid_pair": (N1_CANONICAL, N2_CANONICAL),
        "splitting_ratio_geo": result["splitting_ratio_geo"],
        "splitting_ratio_pdg": DM2_RATIO_PDG,
        "splitting_ratio_pct_err": result["splitting_ratio_pct_err"],
        "dm2_21_input_eV2": DM2_21_PDG_EV2,
        "dm2_31_predicted_eV2": result["dm2_31_geo_eV2"],
        "dm2_31_pdg_eV2": DM2_31_PDG_EV2,
        "dm2_31_pct_err": result["dm2_31_pct_err"],
        "sum_mnu_meV": result["sum_mnu_eV"] * 1000.0,
        "planck_consistent": result["planck_consistent"],
        "status": result["status"],
        "toe_status": "⚠️ CONSTRAINED (ratio 10%, absolute scale from Δm²₂₁ input)",
        "remaining_gap": (
            "Full zero-parameter derivation requires RS Dirac Yukawa y_ν "
            "and right-handed bulk masses c_R^{ν_i} from geometry."
        ),
        "improvement_over_open": (
            "RS Dirac zero-mode framework formally established; "
            "splitting ratio predicted from pure geometry to 10%; "
            "Δm²₃₁ predicted from Δm²₂₁ input to 10%; "
            "Σm_ν < 120 meV verified."
        ),
    }
