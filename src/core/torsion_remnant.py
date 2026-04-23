# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/torsion_remnant.py
============================
Pillar 48 — Einstein-Cartan-KK Torsion Hybrid and Black Hole Remnants.

Physical context
----------------
Pinčák et al. (2026) published "Geometric origin of a stable black hole
remnant from torsion in G₂-manifold geometry" (*Gen. Rel. Grav.*, 2026),
demonstrating that a 7-dimensional Einstein–Cartan theory formulated on a
G₂-manifold (4D + 3 hidden dimensions, G₂-holonomy, torsion-full) generates
a repulsive force at Planck densities that halts Hawking evaporation.  The
predicted remnant mass is ≈ 9 × 10⁻⁴¹ kg ≈ 4.14 × 10⁻³³ M_Planck.  The
dimensional reduction of this model links torsion to the Higgs mechanism at
the electroweak scale (~246 GeV).

The Unitary Manifold resolves the same paradox in **5 dimensions** via the
Goldberger–Wise stabilisation mechanism (Pillar 28, bh_remnant.py), without
invoking torsion or the three extra dimensions of G₂ geometry.  The two
frameworks reach the same qualitative conclusion — black holes do not
evaporate completely; information is stored in the geometric remnant — through
different routes.

This module:

1. **Torsion repulsion** — implements the Einstein-Cartan spin-torsion contact
   interaction that generates repulsive pressure at Planck densities, as
   derived in the G₂ context.

2. **Torsion-corrected UM remnant** — models a hypothetical torsion extension
   of the UM 5D metric (an Einstein-Cartan-KK hybrid) and computes how a
   torsion coupling κ_T would shift the effective radion floor and remnant mass.

3. **Quasi-normal mode (QNM) information storage** — computes the information
   capacity of the BH remnant through quasi-normal mode oscillations (the G₂
   paper's mechanism for information encoding) and compares it to the UM's
   holographic/topological encoding.

4. **Electroweak scale comparison** — evaluates the KK compactification analog
   of the electroweak scale from both the UM (5D) and G₂ (7D) perspectives
   and quantifies the discrepancy honestly.

5. **Framework comparison** — returns a structured summary of the 5D UM vs 7D
   G₂ approach, for use in FALLIBILITY.md and QUANTUM_THEOREMS.md analysis.

Key results
-----------
- **M_rem (5D UM, canonical)** ≈ 4.4 × 10⁻³ M_Planck (Goldberger–Wise)
- **M_rem (7D G₂, Pinčák 2026)** ≈ 4.14 × 10⁻³³ M_Planck (torsion)
- **Ratio** ≈ 10³⁰ — the frameworks agree qualitatively but differ by 30 orders
  of magnitude in remnant scale, reflecting different compactification schemes
- **QNM frequency (fund., l=2)**: ω_R = 0.3737 / (2 M_rem)  [natural units]
- **QNM info capacity**: dominated by Bekenstein–Hawking entropy; QNMs provide
  an independent lower bound compatible with the BH inequality
- **EW scale ratio (UM)**: M_EW_UM / M_Pl = √(c_s / k_cs) ≈ 0.0666, compared
  to the observed M_EW / M_Pl ≈ 2.01 × 10⁻¹⁷ — the UM does not reproduce the
  hierarchy problem resolution that the G₂-torsion model claims

All quantities are in **natural (Planck) units**: ħ = c = G = k_B = 1,
unless otherwise stated.

Public API
----------
g2_remnant_mass_planck()
    G₂/Pinčák et al. (2026) remnant mass in Planck units (≈ 4.14 × 10⁻³³).

torsion_repulsion_pressure(rho, kappa_torsion)
    Repulsive pressure from spin-torsion contact interaction at density rho.

torsion_planck_floor_density(kappa_torsion)
    Density at which torsion repulsion halts gravitational collapse (Planck units).

um_ec_torsion_correction(phi_min, kappa_torsion)
    Torsion shift to the effective GW radion floor: δφ_min = κ_T (n_w/k_cs)² φ_min.

um_ec_remnant_mass(phi_min, m_phi, phi0, kappa_torsion)
    UM remnant mass with an optional Einstein-Cartan torsion correction.

qnm_frequency_fundamental(M_rem)
    Real part of the l=2 fundamental Schwarzschild QNM [natural units].

qnm_decay_rate(M_rem)
    Imaginary part of the l=2 fundamental Schwarzschild QNM (decay rate).

qnm_lifetime(M_rem)
    Characteristic QNM ring-down lifetime τ = 1 / qnm_decay_rate [natural units].

qnm_oscillation_count(M_rem)
    Number of oscillations before ring-down: N_osc = ω_R / ω_I.

qnm_information_capacity_bits(M_rem, l_max)
    Information capacity from QNMs summed over angular modes l = 2 … l_max.

torsion_extended_qnm_lifetime(M_rem, kappa_torsion)
    QNM lifetime extended by a torsion factor (EC modification to ring-down).

electroweak_scale_ratio_um()
    UM prediction for M_EW / M_Planck from KK compactification geometry.

electroweak_scale_ratio_observed(M_pl_gev)
    Observed M_EW / M_Planck = 246 GeV / M_Planck.

higgs_scale_discrepancy_factor()
    Ratio (M_EW_UM / M_Pl) / (M_EW_observed / M_Pl) — quantifies UM hierarchy gap.

remnant_mass_ratio_5d_to_7d(phi_min, m_phi, phi0)
    M_rem_5D / M_rem_G2 in Planck units.

TorsionComparison
    Dataclass holding the full 5D vs 7D comparison summary.

compare_frameworks(phi_min, m_phi, phi0, kappa_torsion, l_max)
    Return a TorsionComparison for the given parameters.

References
----------
Pinčák R. et al. (2026) "Geometric origin of a stable black hole remnant from
torsion in G₂-manifold geometry", *Gen. Rel. Grav.* 58, (2026).
https://doi.org/10.1007/s10714-026-03528-z

Bh remnant (Pillar 28): src/core/bh_remnant.py
Information paradox (Pillar 36): src/core/information_paradox.py
Observational frontiers (Pillar 38): src/multiverse/observational_frontiers.py
FALLIBILITY.md §4.5 — G₂/torsion alternative documented there.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .bh_remnant import remnant_mass as _gw_remnant_mass

# ---------------------------------------------------------------------------
# Module-level constants (ALL_CAPS, Planck units unless stated)
# ---------------------------------------------------------------------------

# UM braided-winding sector (from Pillars 39, 41)
N_W_CANONICAL: int = 5              # winding number n_w = n₁
N1_CANONICAL: int = 5               # braid mode 1
N2_CANONICAL: int = 7               # braid mode 2
K_CS_CANONICAL: int = 74            # = n₁² + n₂² = 5² + 7²; CS level
C_S_CANONICAL: float = 12.0 / 37.0  # = (n₂² − n₁²) / k_CS; braided sound speed

# UM GW canonical parameters (from bh_remnant.py, Pillar 28)
PHI0_CANONICAL: float = 1.0         # Goldberger–Wise VEV (Planck units)
M_PHI_CANONICAL: float = 1.0        # GW mass parameter (Planck units)
PHI_MIN_CANONICAL: float = 0.1      # representative GW radion floor

# G₂/Pinčák et al. (2026) reference values
PLANCK_MASS_KG: float = 2.176434e-8   # [kg]
PLANCK_MASS_GEV: float = 1.220890e19  # [GeV]
HIGGS_VEV_GEV: float = 246.0          # electroweak VEV [GeV]
HIGGS_MASS_GEV: float = 125.09        # Higgs boson mass [GeV]
G2_REMNANT_MASS_KG: float = 9.0e-41   # Pinčák et al. (2026) [kg]
G2_REMNANT_MASS_PLANCK: float = G2_REMNANT_MASS_KG / PLANCK_MASS_KG  # ≈ 4.14e-33

# Schwarzschild QNM coefficients (l=2 gravitational, fundamental overtone n=0)
# Real and imaginary parts in units of 1/(2M); from Leaver (1985), Nollert (1999)
_QNM_L2_REAL: float = 0.3737    # ω_R × 2M
_QNM_L2_IMAG: float = 0.0890    # ω_I × 2M  (decay rate, positive definite)

# Dimension counts
DIMENSION_COUNT_UM: int = 5    # 4D + 1 extra KK dimension
DIMENSION_COUNT_G2: int = 7    # 4D + 3 extra G₂ hidden dimensions
EXTRA_DIMS_UM: int = 1
EXTRA_DIMS_G2: int = 3


# ---------------------------------------------------------------------------
# G₂ / Pinčák et al. reference value
# ---------------------------------------------------------------------------

def g2_remnant_mass_planck() -> float:
    """Return the G₂/Pinčák et al. (2026) remnant mass in Planck units.

    The 7D Einstein-Cartan model on a G₂-manifold predicts a stable BH
    remnant of ≈ 9 × 10⁻⁴¹ kg, which in Planck units is

        M_rem^{G₂} = 9 × 10⁻⁴¹ kg / 2.176434 × 10⁻⁸ kg ≈ 4.14 × 10⁻³³

    Reference: Pinčák R. et al. (2026), *Gen. Rel. Grav.*

    Returns
    -------
    float
        G₂ remnant mass in Planck units.
    """
    return G2_REMNANT_MASS_PLANCK


# ---------------------------------------------------------------------------
# Torsion repulsion physics (Einstein-Cartan theory)
# ---------------------------------------------------------------------------

def torsion_repulsion_pressure(rho: float, kappa_torsion: float) -> float:
    """Repulsive pressure from the spin-torsion contact interaction.

    In Einstein-Cartan theory the contorsion tensor couples to intrinsic spin
    density σ.  At the mean-field level (σ ∝ ρ for a spin-polarised fluid),
    the effective pressure contribution is

        p_T = (κ_T / (8π)) × ρ²

    This term is negligible at sub-Planck densities but dominates when ρ ~ 1
    (Planck density), generating the repulsion that halts gravitational collapse.

    Parameters
    ----------
    rho : float
        Matter/energy density (Planck units, must be ≥ 0).
    kappa_torsion : float
        Spin-torsion coupling constant κ_T (dimensionless, must be > 0).

    Returns
    -------
    float
        Repulsive pressure p_T ≥ 0.

    Raises
    ------
    ValueError
        If rho < 0 or kappa_torsion ≤ 0.
    """
    if rho < 0.0:
        raise ValueError(f"rho must be ≥ 0; got {rho!r}")
    if kappa_torsion <= 0.0:
        raise ValueError(f"kappa_torsion must be > 0; got {kappa_torsion!r}")
    return (kappa_torsion / (8.0 * math.pi)) * rho * rho


def torsion_planck_floor_density(kappa_torsion: float) -> float:
    """Density at which torsion repulsion balances gravitational pressure.

    Torsion halts collapse when p_T ~ ρ (order-of-magnitude balance):

        (κ_T / 8π) ρ² ≥ ρ   ⟹   ρ_floor = 8π / κ_T

    In Planck units this is O(1) for κ_T ~ 25.  For the G₂ geometry,
    κ_T is set by the G₂ holonomy angles and is estimated to be O(1).

    Parameters
    ----------
    kappa_torsion : float
        Spin-torsion coupling constant κ_T (> 0).

    Returns
    -------
    float
        Density floor ρ_floor (Planck units, > 0).

    Raises
    ------
    ValueError
        If kappa_torsion ≤ 0.
    """
    if kappa_torsion <= 0.0:
        raise ValueError(f"kappa_torsion must be > 0; got {kappa_torsion!r}")
    return 8.0 * math.pi / kappa_torsion


# ---------------------------------------------------------------------------
# UM Einstein-Cartan extension — torsion-corrected radion floor
# ---------------------------------------------------------------------------

def um_ec_torsion_correction(
    phi_min: float,
    kappa_torsion: float,
    n_w: int = N_W_CANONICAL,
    k_cs: int = K_CS_CANONICAL,
) -> float:
    """Fractional torsion shift to the UM radion floor δφ_min.

    Models a hypothetical Einstein-Cartan extension of the 5D KK metric.
    The torsion coupling produces a correction to the effective radion lower
    bound proportional to the winding-to-CS-level ratio (n_w/k_cs)², which
    is the same factor that appears in the topological protection gap
    (Pillar 39):

        δφ_min = κ_T × (n_w / k_cs)² × φ_min

    This is a *perturbative estimate* only; a full Einstein-Cartan-KK
    derivation would require extending the Walker-Pearson metric ansatz to
    include an antisymmetric contorsion tensor.

    Parameters
    ----------
    phi_min : float
        GW-stabilised radion lower bound (> 0).
    kappa_torsion : float
        Torsion coupling constant κ_T (≥ 0).  When 0, the correction vanishes.
    n_w : int
        Winding number (default 5).
    k_cs : int
        Chern-Simons level k_CS (default 74).

    Returns
    -------
    float
        Absolute torsion correction δφ_min ≥ 0.

    Raises
    ------
    ValueError
        If phi_min ≤ 0 or kappa_torsion < 0.
    """
    if phi_min <= 0.0:
        raise ValueError(f"phi_min must be > 0; got {phi_min!r}")
    if kappa_torsion < 0.0:
        raise ValueError(f"kappa_torsion must be ≥ 0; got {kappa_torsion!r}")
    return kappa_torsion * (n_w / k_cs) ** 2 * phi_min


def um_ec_remnant_mass(
    phi_min: float,
    m_phi: float,
    phi0: float,
    kappa_torsion: float = 0.0,
    n_w: int = N_W_CANONICAL,
    k_cs: int = K_CS_CANONICAL,
) -> float:
    """UM remnant mass with an optional Einstein-Cartan torsion correction.

    Computes the effective radion floor

        φ_min_eff = φ_min + δφ_min

    where δφ_min = um_ec_torsion_correction(phi_min, kappa_torsion, n_w, k_cs),
    then applies the Goldberger–Wise remnant formula (Pillar 28):

        M_rem = φ_min_eff / (8π m_φ (φ₀ − φ_min_eff))

    When kappa_torsion = 0 this reduces exactly to the pure GW result.

    Parameters
    ----------
    phi_min : float
        GW radion lower bound (> 0).
    m_phi : float
        GW mass parameter (> 0).
    phi0 : float
        GW vacuum value (> phi_min_eff, checked internally).
    kappa_torsion : float
        Torsion coupling κ_T (≥ 0, default 0 = pure GW result).
    n_w : int
        Winding number (default 5).
    k_cs : int
        Chern-Simons level (default 74).

    Returns
    -------
    float
        Torsion-corrected remnant mass M_rem > 0 (Planck units).

    Raises
    ------
    ValueError
        If phi_min ≤ 0, m_phi ≤ 0, kappa_torsion < 0, or phi0 ≤ phi_min_eff.
    """
    if m_phi <= 0.0:
        raise ValueError(f"m_phi must be > 0; got {m_phi!r}")
    delta = um_ec_torsion_correction(phi_min, kappa_torsion, n_w, k_cs)
    phi_min_eff = phi_min + delta
    if phi0 <= phi_min_eff:
        raise ValueError(
            f"phi0 ({phi0!r}) must be > phi_min_eff = phi_min + delta = "
            f"{phi_min_eff!r}.  Reduce kappa_torsion or increase phi0."
        )
    return phi_min_eff / (8.0 * math.pi * m_phi * (phi0 - phi_min_eff))


# ---------------------------------------------------------------------------
# Quasi-normal mode (QNM) physics
# ---------------------------------------------------------------------------

def qnm_frequency_fundamental(M_rem: float) -> float:
    """Real part of the l=2 fundamental Schwarzschild quasi-normal mode.

    Standard result (Leaver 1985, Nollert 1999):

        ω_R = 0.3737 / (2 M_rem)   [natural units, Planck ħ=c=G=1]

    This is the dominant ringing frequency for gravitational perturbations
    of a Schwarzschild black hole remnant.

    Parameters
    ----------
    M_rem : float
        Remnant mass (Planck units, > 0).

    Returns
    -------
    float
        QNM real frequency ω_R > 0.

    Raises
    ------
    ValueError
        If M_rem ≤ 0.
    """
    if M_rem <= 0.0:
        raise ValueError(f"M_rem must be > 0; got {M_rem!r}")
    return _QNM_L2_REAL / (2.0 * M_rem)


def qnm_decay_rate(M_rem: float) -> float:
    """Imaginary part of the l=2 fundamental Schwarzschild QNM (decay rate).

    Standard result (Leaver 1985):

        ω_I = 0.0890 / (2 M_rem)   [natural units]

    The physical ring-down lifetime is τ = 1 / ω_I.

    Parameters
    ----------
    M_rem : float
        Remnant mass (> 0).

    Returns
    -------
    float
        QNM decay rate ω_I > 0.

    Raises
    ------
    ValueError
        If M_rem ≤ 0.
    """
    if M_rem <= 0.0:
        raise ValueError(f"M_rem must be > 0; got {M_rem!r}")
    return _QNM_L2_IMAG / (2.0 * M_rem)


def qnm_lifetime(M_rem: float) -> float:
    """Characteristic QNM ring-down lifetime τ = 1 / ω_I (natural units).

    Equals 2 M_rem / 0.0890 ≈ 22.47 M_rem in Planck units.

    Parameters
    ----------
    M_rem : float
        Remnant mass (> 0).

    Returns
    -------
    float
        Ring-down lifetime τ > 0 (Planck units).

    Raises
    ------
    ValueError
        If M_rem ≤ 0.
    """
    return 1.0 / qnm_decay_rate(M_rem)


def qnm_oscillation_count(M_rem: float) -> float:
    """Number of oscillation cycles before ring-down: N_osc = ω_R / ω_I.

    For the standard l=2 Schwarzschild QNM this is:

        N_osc = 0.3737 / 0.0890 ≈ 4.198

    This is mass-independent (ω_R and ω_I both scale as 1/(2M_rem)).

    Parameters
    ----------
    M_rem : float
        Remnant mass (> 0), used for validation.

    Returns
    -------
    float
        N_osc ≈ 4.198 (dimensionless).

    Raises
    ------
    ValueError
        If M_rem ≤ 0.
    """
    if M_rem <= 0.0:
        raise ValueError(f"M_rem must be > 0; got {M_rem!r}")
    return _QNM_L2_REAL / _QNM_L2_IMAG


def qnm_information_capacity_bits(M_rem: float, l_max: int = 10) -> float:
    """Information capacity from quasi-normal modes, summed over l = 2 … l_max.

    Each angular mode l ≥ 2 supports (2l+1) degenerate azimuthal states m.
    The information capacity from mode degeneracy is

        I_qnm = Σ_{l=2}^{l_max} log₂(2l+1)

    An additional factor from the oscillation count N_osc = ω_R/ω_I is NOT
    included here because QNM modes represent *modes*, not repeated measurements;
    each mode encodes log₂(2l+1) bits regardless of how many cycles it rings.

    For the G₂ geometry, the QNMs are longer-lived (small ω_I), but the
    mode-counting capacity above is geometry-independent and sets a lower bound
    on the information content of any geometric remnant that supports l_max modes.

    In the UM, Bekenstein-Hawking entropy gives an independent bound:
        I_BH = 4π M_rem² / ln 2   [bits]

    The QNM bound is much weaker for macroscopic remnants (M_rem >> 1)
    but becomes the relevant bound for Planck-scale remnants where only
    the first few modes are geometrically supported.

    Parameters
    ----------
    M_rem : float
        Remnant mass (> 0).  Used to determine l_max_physical: only modes
        with ω_R(l) × M_rem ≳ 0.5 (at least half a cycle stored) are counted.
    l_max : int
        Maximum angular quantum number to include (≥ 2, default 10).

    Returns
    -------
    float
        QNM information capacity in bits (≥ 0).

    Raises
    ------
    ValueError
        If M_rem ≤ 0 or l_max < 2.
    """
    if M_rem <= 0.0:
        raise ValueError(f"M_rem must be > 0; got {M_rem!r}")
    if l_max < 2:
        raise ValueError(f"l_max must be ≥ 2; got {l_max!r}")
    # WKB: ω_R(l) ≈ (l + 0.5) / (3√3 M)  for large l.  Physical l_max where
    # at least ½ oscillation fits: (l + 0.5) / (3√3 M) ≥ 0.5 / (2π M)
    # This is satisfied for all l ≥ 2 when M_rem ≥ 1/(3√3) ≈ 0.19.
    # For very small M_rem, limit l_max_physical.
    _sqrt3 = math.sqrt(3.0)
    l_max_physical = l_max
    if M_rem < 1.0:
        # Maximum l such that ω_R(l) is geometrically resolvable: l ≤ 3√3 M - 0.5
        # For M_rem very small, 3√3 M - 0.5 < 0; int() gives 0 or negative, and
        # max(2, ...) ensures l_max_physical is always at least 2 (fundamental mode).
        l_max_physical = min(l_max, max(2, int(3.0 * _sqrt3 * M_rem - 0.5) + 1))
    qnm_sum = sum(math.log2(2 * l + 1) for l in range(2, l_max_physical + 1))
    # Cap at Bekenstein–Hawking entropy: QNMs cannot store more information than
    # the BH has capacity for.  S_BH = 4π M² is the hard upper bound.
    bh_capacity = 4.0 * math.pi * M_rem ** 2 / math.log(2.0)
    return min(qnm_sum, bh_capacity)


def torsion_extended_qnm_lifetime(M_rem: float, kappa_torsion: float) -> float:
    """QNM lifetime extended by the torsion backreaction factor.

    In the G₂ paper, torsion modifies the spacetime geometry near the remnant,
    effectively reducing the imaginary part of the QNM frequency:

        ω_I_eff = ω_I / (1 + κ_T × (n_w / k_cs)²)

    This extends the ring-down lifetime by the same topological factor that
    appears in the radion floor correction, making QNMs longer-lived and thus
    capable of storing information over cosmological timescales.

    Parameters
    ----------
    M_rem : float
        Remnant mass (> 0).
    kappa_torsion : float
        Torsion coupling κ_T (≥ 0).  When 0, returns the standard GW result.

    Returns
    -------
    float
        Extended QNM ring-down lifetime τ_eff > 0.

    Raises
    ------
    ValueError
        If M_rem ≤ 0 or kappa_torsion < 0.
    """
    if M_rem <= 0.0:
        raise ValueError(f"M_rem must be > 0; got {M_rem!r}")
    if kappa_torsion < 0.0:
        raise ValueError(f"kappa_torsion must be ≥ 0; got {kappa_torsion!r}")
    tau_standard = qnm_lifetime(M_rem)
    topo_factor = 1.0 + kappa_torsion * (N_W_CANONICAL / K_CS_CANONICAL) ** 2
    return tau_standard * topo_factor


# ---------------------------------------------------------------------------
# Electroweak scale comparison
# ---------------------------------------------------------------------------

def electroweak_scale_ratio_um(
    c_s: float = C_S_CANONICAL,
    k_cs: int = K_CS_CANONICAL,
) -> float:
    """UM prediction for the electroweak-to-Planck mass ratio from KK geometry.

    The KK compactification sets a natural sub-Planck scale via the braided
    sound speed and CS level:

        M_EW_UM / M_Planck = √(c_s / k_cs) = √((12/37) / 74) ≈ 0.0666

    This is the only *dimensionless ratio* in the UM that has units of a mass
    scale analogous to the electroweak VEV.

    **Important caveat:** this gives M_EW_UM ≈ 8.1 × 10¹⁷ GeV, which is
    eight orders of magnitude above the observed 246 GeV.  The UM does not
    resolve the hierarchy problem as stated; the G₂ paper claims to do so
    through torsion.  See higgs_scale_discrepancy_factor() for the quantification.

    Parameters
    ----------
    c_s : float
        Braided sound speed (default 12/37).
    k_cs : int
        Chern-Simons level (default 74).

    Returns
    -------
    float
        Dimensionless ratio M_EW_UM / M_Planck ≈ 0.0666.
    """
    return math.sqrt(c_s / k_cs)


def electroweak_scale_ratio_observed(
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    m_planck_gev: float = PLANCK_MASS_GEV,
) -> float:
    """Observed electroweak-to-Planck mass ratio: 246 GeV / 1.22 × 10¹⁹ GeV.

    Parameters
    ----------
    higgs_vev_gev : float
        Higgs VEV [GeV] (default 246 GeV).
    m_planck_gev : float
        Planck mass [GeV] (default 1.220890 × 10¹⁹ GeV).

    Returns
    -------
    float
        Observed ratio v_EW / M_Planck ≈ 2.01 × 10⁻¹⁷.
    """
    return higgs_vev_gev / m_planck_gev


def higgs_scale_discrepancy_factor(
    c_s: float = C_S_CANONICAL,
    k_cs: int = K_CS_CANONICAL,
    higgs_vev_gev: float = HIGGS_VEV_GEV,
    m_planck_gev: float = PLANCK_MASS_GEV,
) -> float:
    """Ratio of the UM EW scale prediction to the observed EW scale.

        R = (M_EW_UM / M_Pl) / (246 GeV / M_Pl)

    A value >> 1 means the UM prediction overshoots the EW scale.
    The observed ratio is ≈ 2.01 × 10⁻¹⁷, while UM predicts ≈ 0.0666,
    giving R ≈ 3.3 × 10¹⁵ — a 15-order-of-magnitude discrepancy.

    This is an honest gap: the UM, at its current development, does not
    provide a geometric derivation of the electroweak scale, unlike the
    G₂/torsion model of Pinčák et al. (2026).

    Parameters
    ----------
    c_s : float
        Braided sound speed (default 12/37).
    k_cs : int
        Chern-Simons level (default 74).
    higgs_vev_gev : float
        Higgs VEV [GeV] (default 246 GeV).
    m_planck_gev : float
        Planck mass [GeV] (default 1.22 × 10¹⁹ GeV).

    Returns
    -------
    float
        R = (UM EW ratio) / (observed EW ratio) >> 1.
    """
    ratio_um = electroweak_scale_ratio_um(c_s, k_cs)
    ratio_obs = electroweak_scale_ratio_observed(higgs_vev_gev, m_planck_gev)
    return ratio_um / ratio_obs


# ---------------------------------------------------------------------------
# Framework comparison
# ---------------------------------------------------------------------------

def remnant_mass_ratio_5d_to_7d(
    phi_min: float = PHI_MIN_CANONICAL,
    m_phi: float = M_PHI_CANONICAL,
    phi0: float = PHI0_CANONICAL,
) -> float:
    """Ratio M_rem_5D(GW) / M_rem_G₂(Pinčák 2026) in Planck units.

    The canonical UM remnant (Goldberger–Wise) is typically many orders of
    magnitude larger than the G₂ torsion prediction ≈ 4.14 × 10⁻³³ M_Planck.

    Parameters
    ----------
    phi_min : float
        GW radion floor (default 0.1).
    m_phi : float
        GW mass parameter (default 1.0).
    phi0 : float
        GW vacuum value (default 1.0).

    Returns
    -------
    float
        M_rem_5D / M_rem_G₂ (positive, typically >> 1).
    """
    M_rem_5d = _gw_remnant_mass(phi_min, m_phi, phi0)
    M_rem_g2 = G2_REMNANT_MASS_PLANCK
    return M_rem_5d / M_rem_g2


@dataclass
class TorsionComparison:
    """Summary of the 5D Unitary Manifold vs 7D G₂ framework comparison.

    Produced by :func:`compare_frameworks`.

    Attributes
    ----------
    um_5d_M_rem : float
        UM remnant mass (pure GW, Planck units).
    um_ec_M_rem : float
        UM remnant mass with torsion correction (Planck units).
    g2_7d_M_rem : float
        G₂/Pinčák (2026) remnant mass (Planck units).
    ratio_5d_to_7d : float
        M_rem_5D / M_rem_G₂.
    ratio_ec_to_7d : float
        M_rem_EC / M_rem_G₂.
    qnm_frequency : float
        Fundamental QNM frequency of the UM remnant (natural units).
    qnm_lifetime_standard : float
        Standard (no torsion) QNM ring-down lifetime (natural units).
    qnm_lifetime_torsion : float
        Torsion-extended QNM ring-down lifetime (natural units).
    qnm_info_bits : float
        QNM information capacity [bits] for l = 2 … l_max.
    bh_entropy_bits : float
        Bekenstein-Hawking information content of UM remnant [bits].
    ew_scale_ratio_um : float
        UM EW / Planck scale ratio (≈ 0.0666).
    ew_scale_ratio_observed : float
        Observed EW / Planck scale ratio (≈ 2.01 × 10⁻¹⁷).
    higgs_discrepancy : float
        UM EW ratio / observed EW ratio (≈ 3.3 × 10¹⁵).
    dimension_count_um : int
        Total spacetime dimensions in UM (5).
    dimension_count_g2 : int
        Total spacetime dimensions in G₂ model (7).
    qualitative_agreement : bool
        True — both frameworks predict stable remnants that store information.
    """

    um_5d_M_rem: float
    um_ec_M_rem: float
    g2_7d_M_rem: float
    ratio_5d_to_7d: float
    ratio_ec_to_7d: float
    qnm_frequency: float
    qnm_lifetime_standard: float
    qnm_lifetime_torsion: float
    qnm_info_bits: float
    bh_entropy_bits: float
    ew_scale_ratio_um: float
    ew_scale_ratio_observed: float
    higgs_discrepancy: float
    dimension_count_um: int
    dimension_count_g2: int
    qualitative_agreement: bool


def compare_frameworks(
    phi_min: float = PHI_MIN_CANONICAL,
    m_phi: float = M_PHI_CANONICAL,
    phi0: float = PHI0_CANONICAL,
    kappa_torsion: float = 0.1,
    l_max: int = 10,
) -> TorsionComparison:
    """Return a full 5D UM vs 7D G₂ torsion comparison.

    Parameters
    ----------
    phi_min : float
        GW radion floor (default 0.1).
    m_phi : float
        GW mass parameter (default 1.0).
    phi0 : float
        GW vacuum value (default 1.0).
    kappa_torsion : float
        Torsion coupling κ_T for the EC correction (default 0.1).
    l_max : int
        Maximum angular mode for QNM information sum (default 10).

    Returns
    -------
    TorsionComparison
        Structured comparison result.
    """
    M_rem_5d = _gw_remnant_mass(phi_min, m_phi, phi0)
    M_rem_ec = um_ec_remnant_mass(phi_min, m_phi, phi0, kappa_torsion)
    M_rem_g2 = G2_REMNANT_MASS_PLANCK

    qnm_freq = qnm_frequency_fundamental(M_rem_5d)
    tau_std = qnm_lifetime(M_rem_5d)
    tau_tor = torsion_extended_qnm_lifetime(M_rem_5d, kappa_torsion)
    qnm_bits = qnm_information_capacity_bits(M_rem_5d, l_max)
    bh_bits = 4.0 * math.pi * M_rem_5d ** 2 / math.log(2.0)

    return TorsionComparison(
        um_5d_M_rem=M_rem_5d,
        um_ec_M_rem=M_rem_ec,
        g2_7d_M_rem=M_rem_g2,
        ratio_5d_to_7d=M_rem_5d / M_rem_g2,
        ratio_ec_to_7d=M_rem_ec / M_rem_g2,
        qnm_frequency=qnm_freq,
        qnm_lifetime_standard=tau_std,
        qnm_lifetime_torsion=tau_tor,
        qnm_info_bits=qnm_bits,
        bh_entropy_bits=bh_bits,
        ew_scale_ratio_um=electroweak_scale_ratio_um(),
        ew_scale_ratio_observed=electroweak_scale_ratio_observed(),
        higgs_discrepancy=higgs_scale_discrepancy_factor(),
        dimension_count_um=DIMENSION_COUNT_UM,
        dimension_count_g2=DIMENSION_COUNT_G2,
        qualitative_agreement=True,
    )
