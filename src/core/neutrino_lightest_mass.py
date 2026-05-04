# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/neutrino_lightest_mass.py
====================================
Pillar 140 — Lightest Neutrino Mass from RS Dirac Zero-Mode Profiles.

HONEST IMPLEMENTATION
---------------------
The RS Dirac mechanism predicts m_ν = v × f₀(c_L) × f₀(c_R), where
f₀(c) is the normalised zero-mode wavefunction overlap on the IR brane.

With c_R = 23/25 = 0.920 (THEOREM from Pillar 143 orbifold fixed-point counting) and
c_L ≈ 0.776 (naive estimate from c_base=0.68 + n_w-correction):

    f₀(c_R=0.920) ≈ 1.623×10⁻⁷
    f₀(c_L=0.776) ≈ 2.720×10⁻⁵
    m_ν1 = 246.22 GeV × 2.720e-5 × 1.623e-7 ≈ 1.086 eV

This VIOLATES the Planck CMB bound Σm_ν < 0.12 eV (95% CL) because
even m_ν1 ≈ 1.086 eV alone exceeds the total allowed sum.

To satisfy Planck, the left-handed bulk mass parameter must be pushed to
c_L ≥ ~0.88, which suppresses f₀(c_L) by a further factor ~40.

This is documented honestly: c_L is NOT fixed by the current geometric
framework — it requires an additional input or UV condition.

Status: CONSTRAINED (RS Dirac mechanism: c_R=0.920 from n_w=5; c_L needs
tuning c_L ≥ 0.88 to satisfy Planck bound Σm_ν < 0.12 eV)
"""

from __future__ import annotations
import math
from src.core.sm_free_parameters import (
    N_W, K_CS, PI_K_R,
    V_HIGGS_GEV,
    PLANCK_SUM_MNU_EV,
)
from src.core.rmatrix_braid_neutrino import c_right_from_orbifold

__all__ = [
    "c_right_neutrino_lightest",
    "rs_dirac_zero_mode_profile_local",
    "neutrino_lightest_mass_rs",
    "lightest_neutrino_closure_status",
    "neutrino_mass_pillar135_140_consistency",
]

_GEV_TO_EV: float = 1.0e9


def c_right_neutrino_lightest(n_w: int = 5) -> float:
    """Return the RS bulk-mass parameter for the right-handed lightest neutrino.

    THEOREM (Pillar 143 — Orbifold Fixed-Point Theorem):
        c_R = (n_w² − N_fp) / n_w²
    where N_fp = 2 is the number of Z₂ orbifold fixed points (UV + IR branes).

    For n_w = 5:  c_R = (25 − 2) / 25 = 23/25 = 0.920

    This value is now a DERIVED THEOREM, not a hardcoded constant.  The
    previous version documented this as a "KNOWN GAP"; it is now closed by
    the orbifold fixed-point counting derivation in Pillar 143.

    See src/core/rmatrix_braid_neutrino.py for the full proof.
    """
    return c_right_from_orbifold(n_w=n_w, n_fp=2)


def rs_dirac_zero_mode_profile_local(c: float, pi_kr: float = 37.0) -> float:
    """Normalised RS zero-mode wavefunction on the IR brane, f₀(c).

    Exact formula (valid for any c ≠ 1/2):
        x = (2c - 1) × πkR
        if x > 500:  f₀(c) = sqrt(2c - 1) × exp(-x/2)   [large-x limit]
        else:        f₀(c) = sqrt((2c - 1) / (exp(x) - 1))

    For c > 1/2 (UV-localised fermions) f₀ is exponentially suppressed,
    giving naturally small Dirac masses without fine-tuning the Yukawa.

    Parameters
    ----------
    c      : bulk-mass parameter (dimensionless)
    pi_kr  : Randall-Sundrum geometry parameter πkR (default 37)

    Returns
    -------
    float : f₀(c), the zero-mode IR-brane profile amplitude
    """
    x = (2.0 * c - 1.0) * pi_kr
    if x > 500.0:
        return math.sqrt(2.0 * c - 1.0) * math.exp(-0.5 * x)
    return math.sqrt((2.0 * c - 1.0) / (math.exp(x) - 1.0))


def neutrino_lightest_mass_rs(
    n_w: int = 5,
    k_cs: int = 74,
    pi_kr: float = 37.0,
) -> dict:
    """Predict the lightest Dirac neutrino mass from RS geometry.

    c_R is fixed geometrically at 23/25=0.920.
    c_L is estimated from c_base with an n_w-dependent correction.

    RESULT IS HONESTLY REPORTED: the naive estimate gives m_ν1 ≈ 1 eV,
    which violates the Planck CMB bound.

    Parameters
    ----------
    n_w    : winding number (default 5)
    k_cs   : Chern-Simons level (default 74, for context)
    pi_kr  : πkR (default 37)

    Returns
    -------
    dict with full honest calculation and Planck-consistency flag
    """
    c_rnu1 = c_right_neutrino_lightest(n_w)
    # c_L is fixed at 0.776 as derived in Pillar 140 via the RS wavefunction
    # hierarchy for the lightest neutrino.  Even this value violates the
    # Planck bound (see honest_note below); c_L >= 0.88 is required.
    c_lnu1 = 0.776

    f0_rnu1 = rs_dirac_zero_mode_profile_local(c_rnu1, pi_kr)
    f0_lnu1 = rs_dirac_zero_mode_profile_local(c_lnu1, pi_kr)

    # Dirac mass: m_ν = v × f₀(c_L) × f₀(c_R)
    m_nu1_gev = V_HIGGS_GEV * f0_lnu1 * f0_rnu1
    m_nu1_ev = m_nu1_gev * _GEV_TO_EV

    planck_consistent = m_nu1_ev < PLANCK_SUM_MNU_EV

    status = (
        "CONSTRAINED (RS Dirac: c_R=0.920 from n_w=5; "
        "c_L=0.776 gives ~1 eV violating Planck; need c_L≥0.88)"
    )

    honest_note = (
        f"With c_R={c_rnu1} and c_L={c_lnu1}, the RS Dirac zero-mode formula gives "
        f"m_ν1 ≈ {m_nu1_ev:.4f} eV.  The Planck bound is Σm_ν < {PLANCK_SUM_MNU_EV} eV, "
        f"so even the lightest neutrino mass alone exceeds the total allowed sum by "
        f"a factor ~{m_nu1_ev/PLANCK_SUM_MNU_EV:.1f}×.  "
        f"The geometry fixes c_R uniquely, but c_L requires an additional UV condition "
        f"(c_L ≥ ~0.88) to satisfy cosmological bounds.  "
        f"This is an open constraint, NOT a successful prediction."
    )

    return {
        "c_rnu1": c_rnu1,
        "c_lnu1": c_lnu1,
        "f0_rnu1": f0_rnu1,
        "f0_lnu1": f0_lnu1,
        "m_nu1_ev": m_nu1_ev,
        "planck_consistent": planck_consistent,
        "planck_limit_ev": PLANCK_SUM_MNU_EV,
        "status": status,
        "honest_note": honest_note,
    }


def lightest_neutrino_closure_status() -> dict:
    """Return honest closure status for Pillar 140."""
    r = neutrino_lightest_mass_rs()
    return {
        "pillar": 140,
        "parameter": "m_ν₁ (lightest neutrino mass)",
        "status": r["status"],
        "predicted_ev": r["m_nu1_ev"],
        "planck_bound_ev": r["planck_limit_ev"],
        "planck_consistent": r["planck_consistent"],
        "honest_note": r["honest_note"],
        "closed": False,
        "resolution_needed": "UV condition fixing c_L ≥ 0.88 from geometry",
    }


def neutrino_mass_pillar135_140_consistency() -> dict:
    """Cross-consistency check between Pillar 135 and Pillar 140 m_ν₁ estimates.

    OPEN INCONSISTENCY (documented)
    --------------------------------
    Pillar 135 infers m_ν₁ from the mass-ratio formula:
        m_ν₁ = √(Δm²₂₁ / (n₁n₂ − 1)) ≈ 1.49 meV
    This approach uses the PDG Δm²₂₁ as input and the braid ratio to set the
    absolute mass scale, bypassing the RS Dirac Yukawa entirely.

    Pillar 140 computes m_ν₁ directly from the RS Dirac zero-mode formula:
        m_ν₁ = v × f₀(c_L=0.776) × f₀(c_R=0.920) ≈ 1.086 eV

    These two estimates differ by ~3 orders of magnitude and both claim to
    arise from the same RS Dirac framework.  This inconsistency is a genuine
    structural problem: the two approaches use different parameterizations
    and cannot be simultaneously correct.

    Resolution path: a genuine zero-parameter derivation requires the RS
    Yukawa coupling y_ν and the right-handed bulk masses c_R^{ν_i} to be
    derived from geometry (not fitted), so that Pillar 140's RS Dirac formula
    reproduces the Planck-consistent value from Pillar 135's ratio approach.

    Returns
    -------
    dict
        'm_nu1_pillar135_meV': float — Pillar 135 implied m_ν₁ [meV]
        'm_nu1_pillar140_ev' : float — Pillar 140 RS Dirac m_ν₁ [eV]
        'ratio'              : float — Pillar 140 / Pillar 135 ratio
        'log10_ratio'        : float — log₁₀ of ratio
        'inconsistency_flag' : bool  — True if ratio > 100 (> 2 orders of magnitude)
        'status'             : str   — OPEN INCONSISTENCY label
    """
    # Pillar 135 implied m_ν₁: m_ν₁ = sqrt(Δm²₂₁ / (n₁n₂ − 1))
    dm2_21_ev2 = 7.53e-5  # PDG solar splitting [eV²]
    n1n2 = 5 * 7          # 35
    m_nu1_135_ev = math.sqrt(dm2_21_ev2 / float(n1n2 - 1))  # ≈ 0.00149 eV

    # Pillar 140 RS Dirac m_ν₁
    r140 = neutrino_lightest_mass_rs()
    m_nu1_140_ev = r140["m_nu1_ev"]  # ≈ 1.086 eV

    ratio = m_nu1_140_ev / m_nu1_135_ev if m_nu1_135_ev > 0 else float("inf")
    log10_ratio = math.log10(ratio) if ratio > 0 else float("inf")
    inconsistent = ratio > 100.0

    return {
        "m_nu1_pillar135_meV": m_nu1_135_ev * 1e3,
        "m_nu1_pillar135_ev": m_nu1_135_ev,
        "m_nu1_pillar140_ev": m_nu1_140_ev,
        "ratio_140_over_135": ratio,
        "log10_ratio": log10_ratio,
        "inconsistency_flag": inconsistent,
        "status": (
            "OPEN INCONSISTENCY: Pillar 135 (ratio method) gives m_ν₁ ≈ 1.49 meV; "
            "Pillar 140 (RS Dirac zero-mode) gives m_ν₁ ≈ 1.086 eV. "
            f"These differ by ~{ratio:.0f}× (~{log10_ratio:.1f} orders of magnitude). "
            "Resolution requires deriving RS Yukawa y_ν and c_R^{{ν_i}} from geometry "
            "so that both approaches agree."
        ),
        "pillar_135_note": (
            "Pillar 135 infers m_ν₁ from the braid ratio formula using Δm²₂₁ as input. "
            "It bypasses the RS Dirac Yukawa and cannot be reconciled with "
            "Pillar 140's c_L=0.776 result without additional UV conditions."
        ),
        "pillar_140_note": (
            "Pillar 140 uses the RS Dirac zero-mode formula with c_L=0.776 "
            "(naive geometric estimate) and gives m_ν₁ ≈ 1 eV, violating the "
            "Planck Σm_ν < 0.12 eV bound. c_L ≥ 0.88 is required."
        ),
    }
