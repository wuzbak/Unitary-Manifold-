# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/kk_collider_resonances.py
====================================
Pillar 43 — Kaluza-Klein Collider Resonances: Planck-Scale Prediction.

Physical context
----------------
The Unitary Manifold is a 5D Kaluza–Klein theory with the compact dimension
stabilised at radius

    R  =  φ₀ × ℓ_P  =  n_w × 2π × ℓ_Planck

where φ₀ = n_w × 2π (from Pillar 39, solitonic_charge.py) and n_w = 5.
In SI units this gives

    R  ≈  5 × 2π × 1.616 × 10⁻³⁵ m  ≈  5.07 × 10⁻³⁴ m

The n-th KK excitation of any Standard Model particle has mass

    m_n  =  n / R  =  n × M_Planck / (n_w × 2π)                       [1]

For the first excitation (n=1) with n_w=5:

    m_1  =  M_Planck / (5 × 2π)  ≈  1.95 × 10¹⁷ GeV                  [2]

where M_Planck = 1.2209 × 10¹⁹ GeV (reduced Planck mass in natural units is
2.435 × 10¹⁸ GeV; here we use the unreduced value for the KK mass formula).

This is the **primary falsification prediction of Gap 5**:

    The lightest KK resonance sits at m_1 ≈ 1.95 × 10¹⁷ GeV.

Experimental status
-------------------
* LHC (CERN)     : CoM energy 14 TeV = 1.4 × 10⁴ GeV  →  m_1 / E_LHC ≈ 10¹³
* FCC-hh (future): CoM energy 100 TeV                   →  still ≈ 10¹² below m_1
* Muon collider  : CoM energy ~10 TeV–100 TeV            →  same gap

No forseeable collider can reach the KK resonance scale in the single-extra-
dimension (5D) picture.  This is consistent with the non-observation of KK
states at the LHC and fixes the "naturalness" question for this framework:
the hierarchy is not a fine-tuning problem — it is the geometric ratio φ₀ ≈ 31.4.

Falsification window
--------------------
If a new resonance is discovered at a mass E_res < m_1(n_w=5), it could
indicate:
    (a)  A different n_w (requires re-deriving the Atiyah-Singer index)
    (b)  An additional compactified dimension with larger radius (new physics)
    (c)  A non-KK resonance (composite state, dark sector, etc.)

For cases (a) and (b) to be consistent with the current framework, the new
observation would need to agree with some (n_w', R') while still matching the
CMB birefringence prediction β ∈ {0.273°, 0.331°}.

Cross-section scaling
---------------------
The production cross-section for a spin-2 KK graviton at collider energy √s:

    σ(q q̄ → G_KK) ∝  (√s / M_Planck)² / m_1²                         [3]

At LHC energies (√s = 14 TeV), this is suppressed by a factor of order
(14 TeV / 10¹⁷ GeV)² ~ 10⁻²⁶, making KK graviton production unobservable.

Public API
----------
M_PLANCK_GEV : float
    Planck mass in GeV.

kk_first_excitation_mass(n_w, phi0_natural)
    Mass of the n=1 KK excitation in Planck units.

kk_mode_mass_gev(n, n_w)
    KK excitation mass in GeV for mode n.

lhc_reach_ratio(n_w)
    Ratio m_1 / E_LHC  (how many orders of magnitude above LHC).

fcc_reach_ratio(n_w)
    Ratio m_1 / E_FCC.

collider_cross_section_ratio(sqrt_s_gev, n_w)
    Dimensionless suppression factor (√s / m_1)² for KK graviton production.

falsification_window(n_w)
    Dict describing the mass range within which a discovery would falsify
    the 5D Planck-scale picture.

kk_tower_masses_gev(n_w, n_max)
    List of the first n_max KK excitation masses in GeV.

kk_resonance_summary(n_w)
    Full summary dict of the KK resonance prediction.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

#: Unreduced Planck mass in GeV  (M_Pl = √(ℏc/G) ≈ 1.2209×10¹⁹ GeV)
M_PLANCK_GEV: float = 1.2209e19

#: LHC centre-of-mass energy in GeV (design: 14 TeV)
E_LHC_GEV: float = 14.0e3

#: Future Circular Collider (FCC-hh) design energy in GeV (100 TeV)
E_FCC_GEV: float = 100.0e3

#: High-energy muon collider target energy in GeV (10 TeV)
E_MUON_GEV: float = 10.0e3

#: Canonical winding number from Atiyah-Singer (Pillar 7)
N_W_CANONICAL: int = 5

#: Canonical Chern-Simons level (Pillar 39)
K_CS_CANONICAL: int = 74

#: φ₀ = n_w × 2π (Planck units); compact radius R = φ₀ × ℓ_Planck
PHI_0_CANONICAL: float = N_W_CANONICAL * 2.0 * math.pi


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def kk_first_excitation_mass(
    n_w: int = N_W_CANONICAL,
    phi0_natural: float = PHI_0_CANONICAL,
) -> float:
    """Mass of the first (n=1) KK excitation in Planck units.

    The compact radius is R = φ₀ (in Planck units), so

        m_1 = 1 / R = 1 / φ₀ = 1 / (n_w × 2π)

    Parameters
    ----------
    n_w           : int   — winding number (default 5)
    phi0_natural  : float — φ₀ in Planck units (default n_w × 2π)

    Returns
    -------
    float
        m_1 in Planck units.

    Raises
    ------
    ValueError
        If n_w ≤ 0 or phi0_natural ≤ 0.
    """
    if n_w <= 0:
        raise ValueError(f"n_w must be positive, got {n_w}")
    if phi0_natural <= 0.0:
        raise ValueError(f"phi0_natural must be positive, got {phi0_natural}")
    return 1.0 / phi0_natural


def kk_mode_mass_gev(n: int, n_w: int = N_W_CANONICAL) -> float:
    """KK excitation mass for mode n in GeV.

        m_n = n × M_Planck / (n_w × 2π)

    Parameters
    ----------
    n    : int — KK mode number (n ≥ 1 for excited states)
    n_w  : int — winding number (default 5)

    Returns
    -------
    float
        m_n in GeV.

    Raises
    ------
    ValueError
        If n < 0 or n_w ≤ 0.
    """
    if n < 0:
        raise ValueError(f"Mode number n must be ≥ 0, got {n}")
    if n_w <= 0:
        raise ValueError(f"n_w must be positive, got {n_w}")
    if n == 0:
        return 0.0
    phi0 = n_w * 2.0 * math.pi
    # m_n in Planck units = n / phi0; convert to GeV
    return n * M_PLANCK_GEV / phi0


def lhc_reach_ratio(n_w: int = N_W_CANONICAL) -> float:
    """Ratio m_1 / E_LHC — how many times m_1 exceeds the LHC energy.

    A ratio >> 1 confirms that KK excitations are invisible at the LHC.

    Parameters
    ----------
    n_w : int — winding number (default 5)

    Returns
    -------
    float
        m_1(GeV) / E_LHC(GeV).
    """
    return kk_mode_mass_gev(1, n_w) / E_LHC_GEV


def fcc_reach_ratio(n_w: int = N_W_CANONICAL) -> float:
    """Ratio m_1 / E_FCC — how many times m_1 exceeds the FCC energy.

    Parameters
    ----------
    n_w : int — winding number (default 5)

    Returns
    -------
    float
        m_1(GeV) / E_FCC(GeV).
    """
    return kk_mode_mass_gev(1, n_w) / E_FCC_GEV


def collider_cross_section_ratio(
    sqrt_s_gev: float,
    n_w: int = N_W_CANONICAL,
) -> float:
    """Dimensionless suppression factor for KK graviton production.

    For a spin-2 KK graviton produced at centre-of-mass energy √s:

        suppression ∝ (√s / m_1)²

    A value much less than 1 means the process is entirely inaccessible.

    Parameters
    ----------
    sqrt_s_gev : float — collider centre-of-mass energy in GeV
    n_w        : int   — winding number (default 5)

    Returns
    -------
    float
        (√s / m_1)² — dimensionless suppression factor.

    Raises
    ------
    ValueError
        If sqrt_s_gev ≤ 0.
    """
    if sqrt_s_gev <= 0.0:
        raise ValueError(f"sqrt_s_gev must be positive, got {sqrt_s_gev}")
    m1 = kk_mode_mass_gev(1, n_w)
    return (sqrt_s_gev / m1) ** 2


def falsification_window(n_w: int = N_W_CANONICAL) -> Dict:
    """Describe the mass range in which a discovery would falsify the 5D picture.

    A new resonance at energy E_res falsifies the single-extra-dimension
    Planck-scale picture iff E_res < m_1(n_w=5) and E_res is confirmed to be
    a KK excitation (spin-2 graviton mode).

    Returns
    -------
    dict with keys:
        ``m1_gev``              : float — predicted m_1 in GeV
        ``falsifying_mass_gev`` : float — any confirmed KK mass below this falsifies
        ``current_lhc_limit_gev``: float — current LHC energy (conservative bound)
        ``safety_ratio``        : float — m_1 / E_LHC
        ``falsified``           : bool  — True if a KK mode at LHC energy is seen
        ``summary``             : str   — human-readable description
    """
    m1 = kk_mode_mass_gev(1, n_w)
    ratio = m1 / E_LHC_GEV
    return {
        "m1_gev": m1,
        "falsifying_mass_gev": m1,
        "current_lhc_limit_gev": E_LHC_GEV,
        "safety_ratio": ratio,
        "falsified": False,  # no KK mode observed at LHC
        "summary": (
            f"Predicted KK first excitation: m_1 ≈ {m1:.3e} GeV. "
            f"LHC at {E_LHC_GEV:.0f} GeV is a factor of {ratio:.2e} below. "
            f"Discovery of a KK graviton below m_1 would falsify n_w=5."
        ),
    }


def kk_tower_masses_gev(
    n_w: int = N_W_CANONICAL,
    n_max: int = 5,
) -> List[Dict[str, float]]:
    """First n_max KK excitation masses in GeV.

    Parameters
    ----------
    n_w   : int — winding number (default 5)
    n_max : int — number of excited modes to compute (default 5)

    Returns
    -------
    list of dict
        Each entry: {'n': int, 'm_gev': float, 'm_planck_units': float}
    """
    if n_max < 1:
        raise ValueError(f"n_max must be ≥ 1, got {n_max}")
    phi0 = n_w * 2.0 * math.pi
    tower = []
    for n in range(1, n_max + 1):
        m_planck = n / phi0
        m_gev = n * M_PLANCK_GEV / phi0
        tower.append({"n": n, "m_gev": m_gev, "m_planck_units": m_planck})
    return tower


def kk_resonance_summary(n_w: int = N_W_CANONICAL) -> Dict:
    """Full summary of the KK collider resonance prediction.

    Returns
    -------
    dict with keys:
        ``n_w``, ``phi0_planck``, ``compact_radius_m``,
        ``m1_gev``, ``m1_planck``,
        ``lhc_ratio``, ``fcc_ratio``,
        ``lhc_suppression``, ``fcc_suppression``,
        ``falsification_window``,
        ``tower`` (first 3 modes),
        ``summary``
    """
    phi0 = n_w * 2.0 * math.pi
    lp_m = 1.616e-35  # Planck length in metres
    r_m = phi0 * lp_m
    m1_planck = 1.0 / phi0
    m1_gev = kk_mode_mass_gev(1, n_w)
    lhc_r = lhc_reach_ratio(n_w)
    fcc_r = fcc_reach_ratio(n_w)
    lhc_sup = collider_cross_section_ratio(E_LHC_GEV, n_w)
    fcc_sup = collider_cross_section_ratio(E_FCC_GEV, n_w)
    fw = falsification_window(n_w)
    tower = kk_tower_masses_gev(n_w, n_max=3)

    return {
        "n_w": n_w,
        "phi0_planck": phi0,
        "compact_radius_m": r_m,
        "m1_gev": m1_gev,
        "m1_planck": m1_planck,
        "lhc_ratio": lhc_r,
        "fcc_ratio": fcc_r,
        "lhc_suppression": lhc_sup,
        "fcc_suppression": fcc_sup,
        "falsification_window": fw,
        "tower": tower,
        "summary": (
            f"5D KK theory with n_w={n_w}: compact radius R={r_m:.2e} m. "
            f"First KK excitation m_1={m1_gev:.3e} GeV. "
            f"LHC is {lhc_r:.1e}× below m_1; FCC is {fcc_r:.1e}× below. "
            f"KK modes invisible to all foreseeable colliders."
        ),
    }
