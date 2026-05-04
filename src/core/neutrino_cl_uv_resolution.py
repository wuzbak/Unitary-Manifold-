# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/neutrino_cl_uv_resolution.py
======================================
Pillar 146 — Lightest Neutrino UV Resolution: Three-Branch Analysis.

The 730× Gap (Documented in Pillar 144)
-----------------------------------------
Pillar 140 finds that the naive RS Dirac zero-mode formula with c_L = 0.776
(geometric estimate from c_base = 0.68 + n_w-correction) gives:

    m_ν₁ ≈ 1.086 eV   (violates Planck Σmν < 0.12 eV by ~730×)

This pillar systematically investigates three resolution branches:

Branch A — RS Wavefunction Regime Change (c_L < 0.5)
-----------------------------------------------------
For c_L < 0.5, the fermion zero-mode localizes toward the IR brane rather than
the UV brane.  In this regime the RS profile becomes:

    f₀(c) = √[(1 − 2c) k / (1 − exp(−(1−2c)πkR))]   [IR-localized, c < 0.5]

For c_L → 0, f₀ → √(k) and m_ν grows LARGER than the SM Yukawa scale,
not smaller.  IR localization therefore makes the neutrino mass problem WORSE,
not better.  This branch is ELIMINATED.

Branch B — Type-I Seesaw with Geometric M_R
--------------------------------------------
If the right-handed neutrino ν_R is a bulk fermion with c_R = 23/25 (Pillar 143),
its zero-mode is UV-localized with:

    f₀(c_R = 0.920) ≈ 1.62 × 10⁻⁷

A brane-localised Majorana mass term at the UV brane gives:

    M_R ≈ M_brane × (1 / f₀(c_R)²)   [divergent wavefunction at UV fixed point
                                         → effectively UV-brane mass M_R ~ M_Pl]

The Type-I seesaw mass:
    m_ν = y_D² × v² / M_R

With y_D ~ O(1) and M_R ~ M_Pl = 1.22 × 10¹⁹ GeV:
    m_ν ≈ (1)² × (246 GeV)² / (1.22 × 10¹⁹ GeV) ≈ 5.0 × 10⁻¹⁵ GeV ≈ 5 meV

This is CONSISTENT with the Planck bound (Σmν < 0.12 eV requires each mν < 0.04 eV)!

The geometric input c_R = 23/25 naturally pushes ν_R to the UV brane, where the
Majorana mass is set by the Planck/GUT scale.  The seesaw mechanism then produces
sub-eV Dirac neutrino masses without fine-tuning.

STATUS: VIABLE MECHANISM (requires brane-localised Majorana mass at UV fixed point;
c_R = 23/25 geometric from Pillar 143; y_D ~ O(1) assumed).

Branch C — Open Constraint (Fallback Documentation)
----------------------------------------------------
If neither Branch A nor Branch B is invoked, the RS Dirac framework with c_L = 0.776
gives m_ν₁ ≈ 1 eV.  For Planck consistency:
    c_L ≥ ~0.88   required   (suppresses f₀(c_L) by factor ~40)

The geometric derivation of c_L = 0.776 from c_base uses n_w-dependent corrections
that do not naturally push c_L above 0.88 in the current framework.

RESULT: The seesaw Branch B is the viable path.  Branch A is eliminated.  Branch C
documents the minimum c_L required if neither B nor the Dirac mechanism is resolved.

Public API
----------
branch_a_ir_localization() → dict
    Show IR-localization makes mass larger, not smaller. ELIMINATED.

branch_b_seesaw_geometric() → dict
    Type-I seesaw with c_R=23/25 and UV-brane M_R. VIABLE.

branch_c_open_constraint() → dict
    Document c_L ≥ 0.88 requirement. OPEN.

neutrino_uv_resolution_summary() → dict
    Full Pillar 146 report combining all three branches.

required_cl_for_planck(m_nu_max_ev) → float
    Minimum c_L for Planck consistency.

seesaw_neutrino_mass_gev(y_dirac, m_r_gev) → float
    Type-I seesaw formula m_ν = y_D² v² / M_R.
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

#: RS geometry parameter πkR (Pillar 81)
PI_KR: float = 37.0

#: Winding number n_w = 5
N_W: int = 5

#: c_R from Pillar 143 orbifold fixed-point theorem
C_R_GEOMETRIC: float = 23.0 / 25.0  # = 0.920

#: Naive c_L estimate from Pillar 140 (gives m_ν1 ≈ 1 eV → violates Planck)
C_L_NAIVE: float = 0.776

#: Planck bound on sum of neutrino masses [eV]
PLANCK_SUM_MNU_EV: float = 0.12

#: Higgs VEV [GeV]
HIGGS_VEV_GEV: float = 246.22

#: Planck mass [GeV]
M_PLANCK_GEV: float = 1.22089e19

#: Conversion factor
GEV_TO_EV: float = 1.0e9


# ---------------------------------------------------------------------------
# Helper: RS zero-mode profile
# ---------------------------------------------------------------------------

def _rs_profile(c: float, pi_kr: float = PI_KR) -> float:
    """RS zero-mode IR-brane profile f₀(c).

    Valid for c > 0.5 (UV-localised fermions).  For c < 0.5 see Branch A.
    """
    if c <= 0.5:
        raise ValueError(
            f"c = {c} ≤ 0.5 means IR-localised fermion; use branch_a_ir_localization()."
        )
    x = (2.0 * c - 1.0) * pi_kr
    if x > 500.0:
        return math.sqrt(2.0 * c - 1.0) * math.exp(-0.5 * x)
    return math.sqrt((2.0 * c - 1.0) / (math.exp(x) - 1.0))


def _rs_profile_ir(c: float, pi_kr: float = PI_KR) -> float:
    """RS zero-mode IR-brane profile for c < 0.5 (IR-localised).

    For c < 0.5: x = (1 − 2c) × πkR > 0.
        f₀(c) = √[(1 − 2c) / (1 − exp(−x))]

    For c → 0 this approaches √(1/(πkR)) × O(1) — not exponentially small.
    """
    if c >= 0.5:
        raise ValueError(f"c = {c} ≥ 0.5; use _rs_profile() instead.")
    if c < 0.0:
        raise ValueError(f"c = {c} < 0 is unphysical.")
    x = (1.0 - 2.0 * c) * pi_kr
    if x > 500.0:
        return math.sqrt(1.0 - 2.0 * c)
    return math.sqrt((1.0 - 2.0 * c) / (1.0 - math.exp(-x)))


# ---------------------------------------------------------------------------
# Branch A — IR localisation (ELIMINATED)
# ---------------------------------------------------------------------------

def branch_a_ir_localization(
    c_l_values: list[float] | None = None,
    pi_kr: float = PI_KR,
) -> Dict[str, object]:
    """Investigate whether c_L < 0.5 (IR-localization) helps.

    Parameters
    ----------
    c_l_values : list[float]
        Left-handed bulk mass values to test (default: 0.0, 0.1, 0.3, 0.49).
    pi_kr : float
        RS geometry parameter (default 37.0).

    Returns
    -------
    dict
        'branch'           : str — 'A'
        'verdict'          : str — 'ELIMINATED'
        'reason'           : str — explanation
        'profile_samples'  : list — (c_L, f₀, m_ν [eV]) tuples
        'conclusion'       : str
    """
    if c_l_values is None:
        c_l_values = [0.0, 0.10, 0.25, 0.40, 0.49]

    c_r = C_R_GEOMETRIC
    f0_r = _rs_profile(c_r, pi_kr)

    samples = []
    for c_l in c_l_values:
        try:
            f0_l = _rs_profile_ir(c_l, pi_kr)
        except ValueError:
            continue
        m_nu_gev = HIGGS_VEV_GEV * f0_l * f0_r
        m_nu_ev = m_nu_gev * GEV_TO_EV
        samples.append({
            "c_L": c_l,
            "f0_L": f0_l,
            "f0_R": f0_r,
            "m_nu_ev": m_nu_ev,
            "planck_consistent": m_nu_ev < PLANCK_SUM_MNU_EV,
        })

    # All IR-localized c_L give LARGER masses (not smaller)
    max_mass = max(s["m_nu_ev"] for s in samples) if samples else float("inf")

    return {
        "branch": "A",
        "verdict": "ELIMINATED",
        "reason": (
            "For c_L < 0.5 the zero-mode wavefunction is IR-localized. "
            "The RS profile f₀(c_L < 0.5) = √[(1−2c)/(1−e^{−(1−2c)πkR})] "
            "does NOT decay exponentially — it is O(1) rather than exponentially "
            "suppressed.  This gives m_ν >> 1 eV (worse than c_L = 0.776). "
            "Reducing c_L below 0.5 moves the fermion to the IR brane and "
            "increases the mass, contrary to what would help."
        ),
        "profile_samples": samples,
        "max_mass_ev": max_mass,
        "planck_limit_ev": PLANCK_SUM_MNU_EV,
        "conclusion": (
            "IR-localized ν_L (c_L < 0.5) gives m_ν > 1 eV for all tested values. "
            "Branch A is ELIMINATED: decreasing c_L below 0.5 makes the mass "
            "problem worse."
        ),
    }


# ---------------------------------------------------------------------------
# Branch B — Type-I Seesaw with Geometric M_R (VIABLE)
# ---------------------------------------------------------------------------

def seesaw_neutrino_mass_gev(
    y_dirac: float = 1.0,
    m_r_gev: float = M_PLANCK_GEV,
    higgs_vev_gev: float = HIGGS_VEV_GEV,
) -> float:
    """Compute the Type-I seesaw Dirac neutrino mass.

        m_ν = y_D² × v² / M_R

    Parameters
    ----------
    y_dirac      : float  Dirac Yukawa coupling (default 1.0).
    m_r_gev      : float  Right-handed Majorana mass [GeV] (default M_Pl).
    higgs_vev_gev: float  Higgs VEV [GeV] (default 246.22 GeV).

    Returns
    -------
    float
        m_ν [GeV].
    """
    if m_r_gev <= 0:
        raise ValueError(f"m_r_gev must be positive; got {m_r_gev}.")
    if higgs_vev_gev <= 0:
        raise ValueError(f"higgs_vev_gev must be positive; got {higgs_vev_gev}.")
    return y_dirac ** 2 * higgs_vev_gev ** 2 / m_r_gev


def branch_b_seesaw_geometric(
    y_dirac: float = 1.0,
    pi_kr: float = PI_KR,
) -> Dict[str, object]:
    """Type-I seesaw with c_R = 23/25 UV-brane localization.

    Physical argument:
    - c_R = 23/25 = 0.920 places ν_R on the UV brane (UV-localized profile).
    - A brane-localised Majorana mass at the UV fixed point is geometrically
      natural: it is set by the UV-brane tension scale ≈ M_Pl.
    - The resulting seesaw mass m_ν = y_D² v² / M_R with M_R ~ M_Pl gives:
        m_ν ≈ (246 GeV)² / (1.22 × 10¹⁹ GeV) ≈ 5.0 meV
    - This is well within the Planck bound Σmν < 0.12 eV.

    Parameters
    ----------
    y_dirac : float  Dirac Yukawa coupling (default 1.0).
    pi_kr   : float  RS geometry parameter (default 37.0).

    Returns
    -------
    dict
        Full seesaw analysis result.
    """
    if y_dirac <= 0:
        raise ValueError(f"y_dirac must be positive; got {y_dirac}.")

    c_r = C_R_GEOMETRIC
    f0_r = _rs_profile(c_r, pi_kr)

    # UV-brane Majorana mass: M_R = M_Pl (UV-brane scale)
    m_r_gev = M_PLANCK_GEV
    m_nu_seesaw_gev = seesaw_neutrino_mass_gev(y_dirac, m_r_gev, HIGGS_VEV_GEV)
    m_nu_seesaw_ev = m_nu_seesaw_gev * GEV_TO_EV
    m_nu_seesaw_mev = m_nu_seesaw_ev * 1e3

    planck_consistent = m_nu_seesaw_ev < PLANCK_SUM_MNU_EV

    # Also compute for M_R at GUT scale (cross-check)
    m_gut_gev = 2.0e16
    m_nu_gut_gev = seesaw_neutrino_mass_gev(y_dirac, m_gut_gev, HIGGS_VEV_GEV)
    m_nu_gut_ev = m_nu_gut_gev * GEV_TO_EV

    return {
        "branch": "B",
        "verdict": "VIABLE",
        "c_r_geometric": c_r,
        "f0_r": f0_r,
        "y_dirac": y_dirac,
        "m_r_gev": m_r_gev,
        "m_r_label": "UV-brane Majorana mass (M_Pl scale)",
        "m_nu_seesaw_gev": m_nu_seesaw_gev,
        "m_nu_seesaw_ev": m_nu_seesaw_ev,
        "m_nu_seesaw_mev": m_nu_seesaw_mev,
        "planck_consistent": planck_consistent,
        "planck_limit_ev": PLANCK_SUM_MNU_EV,
        "m_nu_gut_scale_ev": m_nu_gut_ev,
        "geometric_input": (
            "c_R = 23/25 = 0.920 from Pillar 143 orbifold fixed-point theorem. "
            "UV-localized ν_R → M_R set by UV-brane (M_Pl scale). "
            "c_L for the left-handed neutrino remains as a free RS parameter "
            "in the Dirac mechanism but is irrelevant for the seesaw result."
        ),
        "conclusion": (
            f"Seesaw with M_R = M_Pl gives m_ν ≈ {m_nu_seesaw_ev * 1e6:.2f} μeV "
            f"(y_D = {y_dirac:.1f}). "
            f"Planck bound Σmν < {PLANCK_SUM_MNU_EV} eV: "
            f"{'CONSISTENT ✅' if planck_consistent else 'VIOLATED ❌'}. "
            "Branch B provides a viable neutrino mass mechanism via the "
            "Type-I seesaw with geometrically-motivated M_R ~ M_Pl. "
            "Note: m_ν ~ few μeV (sub-meV) is well within the Planck bound."
        ),
        "caveat": (
            "y_D ~ O(1) is assumed; deriving y_D from geometry is an open problem. "
            "This branch requires the UV brane to support a Majorana mass term — "
            "a physically natural but not yet proved requirement in the UM."
        ),
    }


# ---------------------------------------------------------------------------
# Branch C — Open constraint documentation
# ---------------------------------------------------------------------------

def required_cl_for_planck(
    m_nu_max_ev: float = PLANCK_SUM_MNU_EV / 3.0,
    pi_kr: float = PI_KR,
) -> float:
    """Find minimum c_L such that m_ν₁ ≤ m_nu_max_ev.

    Uses binary search on the RS Dirac formula:
        m_ν₁ = v × f₀(c_L) × f₀(c_R=23/25)

    Parameters
    ----------
    m_nu_max_ev : float  Maximum allowed m_ν₁ [eV] (default Planck/3 ≈ 0.04 eV).
    pi_kr       : float  RS geometry parameter (default 37.0).

    Returns
    -------
    float
        Minimum c_L for Planck consistency.
    """
    if m_nu_max_ev <= 0:
        raise ValueError(f"m_nu_max_ev must be positive; got {m_nu_max_ev}.")

    c_r = C_R_GEOMETRIC
    f0_r = _rs_profile(c_r, pi_kr)
    target_gev = m_nu_max_ev / GEV_TO_EV

    # Binary search: c_L in (0.5, 1.0)
    lo, hi = 0.501, 0.9999
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        f0_l = _rs_profile(mid, pi_kr)
        m_nu = HIGGS_VEV_GEV * f0_l * f0_r
        if m_nu > target_gev:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def branch_c_open_constraint(pi_kr: float = PI_KR) -> Dict[str, object]:
    """Document the OPEN c_L ≥ 0.88 constraint.

    Parameters
    ----------
    pi_kr : float  RS geometry parameter (default 37.0).

    Returns
    -------
    dict
        Open constraint documentation.
    """
    m_nu_max_ev = PLANCK_SUM_MNU_EV / 3.0  # conservative single-species bound
    c_l_required = required_cl_for_planck(m_nu_max_ev, pi_kr)

    # Current geometric estimate and its predicted mass
    c_l_naive = C_L_NAIVE
    f0_r = _rs_profile(C_R_GEOMETRIC, pi_kr)
    f0_l_naive = _rs_profile(c_l_naive, pi_kr)
    m_nu_naive_ev = HIGGS_VEV_GEV * f0_l_naive * f0_r * GEV_TO_EV

    f0_l_req = _rs_profile(c_l_required, pi_kr)
    m_nu_req_ev = HIGGS_VEV_GEV * f0_l_req * f0_r * GEV_TO_EV

    return {
        "branch": "C",
        "verdict": "OPEN",
        "c_l_naive_geometric": c_l_naive,
        "m_nu_naive_ev": m_nu_naive_ev,
        "c_l_required_for_planck": c_l_required,
        "m_nu_max_ev": m_nu_max_ev,
        "m_nu_at_required_cl_ev": m_nu_req_ev,
        "planck_limit_ev": PLANCK_SUM_MNU_EV,
        "gap_factor": m_nu_naive_ev / m_nu_max_ev,
        "conclusion": (
            f"The RS Dirac framework with c_L = {c_l_naive} gives m_ν₁ ≈ "
            f"{m_nu_naive_ev:.3f} eV, violating the Planck bound by "
            f"~{m_nu_naive_ev / m_nu_max_ev:.0f}×. "
            f"Planck consistency requires c_L ≥ {c_l_required:.4f}. "
            "The current geometric derivation of c_L from n_w=5 corrections "
            "does not naturally produce c_L ≥ 0.88 — this is an OPEN constraint."
        ),
    }


# ---------------------------------------------------------------------------
# Full Pillar 146 summary
# ---------------------------------------------------------------------------

def neutrino_uv_resolution_summary(pi_kr: float = PI_KR) -> Dict[str, object]:
    """Return the full Pillar 146 three-branch analysis summary.

    Parameters
    ----------
    pi_kr : float  RS geometry parameter (default 37.0).

    Returns
    -------
    dict
        'pillar'     : int — 146
        'branch_A'   : dict — IR localization (ELIMINATED)
        'branch_B'   : dict — Type-I seesaw (VIABLE)
        'branch_C'   : dict — open constraint (OPEN)
        'resolution' : str  — recommended path
        'status'     : str  — overall Pillar 146 status
    """
    bA = branch_a_ir_localization(pi_kr=pi_kr)
    bB = branch_b_seesaw_geometric(pi_kr=pi_kr)
    bC = branch_c_open_constraint(pi_kr=pi_kr)

    return {
        "pillar": 146,
        "title": "Lightest Neutrino UV Resolution — Three-Branch Analysis",
        "branch_A": bA,
        "branch_B": bB,
        "branch_C": bC,
        "resolution": (
            "Branch A (IR localization) is ELIMINATED — makes mass problem worse. "
            "Branch B (Type-I seesaw with M_R ~ M_Pl from c_R=23/25) is VIABLE — "
            "gives m_ν ~ few μeV (y_D=1, M_R=M_Pl), well within the Planck bound. "
            "Branch C (OPEN c_L constraint) documents the remaining gap in the "
            "Dirac mechanism if Branch B is not invoked. "
            "RECOMMENDED: Branch B (geometric seesaw via c_R=23/25 from Pillar 143)."
        ),
        "status": (
            "⚠️ PARTIALLY RESOLVED — Branch B (Type-I seesaw) is viable and "
            "Planck-consistent; requires brane-localised Majorana mass at UV fixed "
            "point (physically natural; not yet proved from 5D action). "
            "The Dirac mechanism (Branch C) remains OPEN pending c_L UV derivation."
        ),
        "c_r_source": "Pillar 143 orbifold fixed-point theorem (c_R = 23/25 = 0.920)",
        "pillar_references": ["Pillar 140 (Dirac gap)", "Pillar 143 (c_R theorem)",
                               "Pillar 144 (730× diagnosis)"],
    }
