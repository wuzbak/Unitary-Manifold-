# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/cold_fusion/tunneling.py
============================
Quantum tunneling with φ-field enhancement — Pillar 15.

In the Unitary Manifold, cold fusion (LENR) is reframed as coherent quantum
tunneling whose probability is amplified by the local entanglement-capacity
scalar φ.  When deuterium nuclei are confined in a Pd lattice, the radion field
φ concentrates at occupied octahedral sites, suppressing the Gamow tunneling
exponent and enabling fusion at sub-thermal energies.

Theory summary
--------------
Sommerfeld parameter:
    η = Z₁ Z₂ α_fs / v_rel

Standard Gamow factor (Coulomb barrier transmission):
    G = exp(−2π η)

φ-enhanced Gamow factor:
    G_eff = exp(−2π η / φ_local)

The local φ field divides the Gamow exponent, effectively lowering the Coulomb
barrier by a factor φ_local.  For φ_local > 1 (loaded lattice site) tunneling
is exponentially enhanced.

Tunneling rate per pair:
    Γ = (v_rel / R_site) · T

Enhancement ratio:
    R = G_eff(φ_enhanced) / G_eff(φ_ref)

Coherence length:
    ξ = 1 / sqrt(2 m_particle kT_nat φ²)
    with kT_nat = T_K · k_B_nat,  k_B_nat = 3.17 × 10⁻⁶  [Planck/K]

Public API
----------
sommerfeld_parameter(Z1, Z2, v_rel, alpha_fs)
    η = Z1 Z2 alpha_fs / v_rel.

gamow_factor(Z1, Z2, v_rel, alpha_fs)
    G = exp(-2π η), standard Coulomb tunneling suppression.

phi_enhanced_gamow(Z1, Z2, v_rel, phi_local, alpha_fs)
    G_eff = exp(-2π η / phi_local), φ-suppressed barrier.

tunneling_probability(Z1, Z2, v_rel, phi_local, alpha_fs)
    T = G_eff clamped to [0, 1].

coherence_length(T_K, phi_local, m_particle)
    ξ = 1 / sqrt(2 m kT_nat φ²).

barrier_suppression_factor(phi_local, phi_ref)
    S = phi_local / phi_ref.

wkb_barrier_width(E_kin, V_barrier)
    d = sqrt(V_barrier - E_kin) / V_barrier  (normalised).

phi_barrier_height(V0, phi_local)
    V_eff = V0 / phi_local.

tunneling_rate_per_pair(v_rel, phi_local, R_site, Z1, Z2, alpha_fs)
    Γ = v_rel / R_site · T.

enhancement_ratio(phi_enhanced, phi_ref, Z1, Z2, v_rel, alpha_fs)
    R = G_eff(phi_enhanced) / G_eff(phi_ref).

minimum_phi_for_fusion(Z1, Z2, v_rel, T_min, alpha_fs)
    φ_min such that tunneling_probability(φ_min) = T_min.
"""



from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_K_B_NAT: float = 3.17e-6      # Boltzmann constant in Planck units per Kelvin
_ALPHA_FS_DEFAULT: float = 1.0 / 137.0
_NUMERICAL_EPSILON: float = 1e-30


# ---------------------------------------------------------------------------
# Sommerfeld parameter
# ---------------------------------------------------------------------------

def sommerfeld_parameter(
    Z1: float,
    Z2: float,
    v_rel: float,
    alpha_fs: float = _ALPHA_FS_DEFAULT,
) -> float:
    """Sommerfeld parameter η for Coulomb-barrier tunneling.

    The Sommerfeld parameter measures how strongly the Coulomb repulsion
    between two nuclei suppresses quantum tunneling.  Large η (low velocity
    or high charge) means exponentially suppressed penetration:

        η = Z₁ Z₂ α_fs / v_rel

    where v_rel is the relative velocity in units of c.

    Parameters
    ----------
    Z1       : float — charge number of first nucleus (Z ≥ 1)
    Z2       : float — charge number of second nucleus (Z ≥ 1)
    v_rel    : float — relative velocity in units of c (must be > 0)
    alpha_fs : float — fine-structure constant (default 1/137)

    Returns
    -------
    eta : float — dimensionless Sommerfeld parameter (≥ 0)

    Raises
    ------
    ValueError
        If v_rel ≤ 0.
    """
    if v_rel <= 0.0:
        raise ValueError(f"v_rel must be > 0, got {v_rel!r}")
    return float(Z1 * Z2 * alpha_fs / v_rel)


# ---------------------------------------------------------------------------
# Standard Gamow factor
# ---------------------------------------------------------------------------

def gamow_factor(
    Z1: float,
    Z2: float,
    v_rel: float,
    alpha_fs: float = _ALPHA_FS_DEFAULT,
) -> float:
    """Standard Gamow tunneling factor for a bare Coulomb barrier.

    The WKB transmission probability through the Coulomb barrier between two
    point charges is given by the Gamow factor:

        G = exp(−2π η)

    where η = Z₁ Z₂ α_fs / v_rel is the Sommerfeld parameter.  G lies in
    (0, 1] and decreases rapidly with charge or decreasing velocity.

    Parameters
    ----------
    Z1       : float — charge number of first nucleus
    Z2       : float — charge number of second nucleus
    v_rel    : float — relative velocity in units of c (must be > 0)
    alpha_fs : float — fine-structure constant (default 1/137)

    Returns
    -------
    G : float — bare Gamow tunneling factor in (0, 1]

    Raises
    ------
    ValueError
        If v_rel ≤ 0.
    """
    eta = sommerfeld_parameter(Z1, Z2, v_rel, alpha_fs)
    return float(np.exp(-2.0 * np.pi * eta))


# ---------------------------------------------------------------------------
# φ-enhanced Gamow factor
# ---------------------------------------------------------------------------

def phi_enhanced_gamow(
    Z1: float,
    Z2: float,
    v_rel: float,
    phi_local: float,
    alpha_fs: float = _ALPHA_FS_DEFAULT,
) -> float:
    """Gamow factor with φ-field enhancement of tunneling probability.

    The local entanglement-capacity scalar φ_local divides the Gamow exponent,
    effectively reducing the Coulomb barrier at the lattice site:

        G_eff = exp(−2π η / φ_local)

    For φ_local = 1 this recovers the bare Gamow factor.  For φ_local > 1
    (concentrated radion field at a loaded lattice site) the exponent is
    suppressed and tunneling is exponentially enhanced.

    Parameters
    ----------
    Z1        : float — charge number of first nucleus
    Z2        : float — charge number of second nucleus
    v_rel     : float — relative velocity in units of c (must be > 0)
    phi_local : float — local φ value at the lattice site (must be > 0)
    alpha_fs  : float — fine-structure constant (default 1/137)

    Returns
    -------
    G_eff : float — φ-enhanced Gamow factor in (0, 1]

    Raises
    ------
    ValueError
        If v_rel ≤ 0 or phi_local ≤ 0.
    """
    if phi_local <= 0.0:
        raise ValueError(f"phi_local must be > 0, got {phi_local!r}")
    eta = sommerfeld_parameter(Z1, Z2, v_rel, alpha_fs)
    return float(np.exp(-2.0 * np.pi * eta / phi_local))


# ---------------------------------------------------------------------------
# Tunneling probability
# ---------------------------------------------------------------------------

def tunneling_probability(
    Z1: float,
    Z2: float,
    v_rel: float,
    phi_local: float,
    alpha_fs: float = _ALPHA_FS_DEFAULT,
) -> float:
    """φ-enhanced tunneling probability clamped to [0, 1].

    Thin wrapper around phi_enhanced_gamow that guarantees the result lies
    in the physically meaningful range [0, 1]:

        T = G_eff = exp(−2π η / φ_local)

    Parameters
    ----------
    Z1        : float — charge number of first nucleus
    Z2        : float — charge number of second nucleus
    v_rel     : float — relative velocity in units of c (must be > 0)
    phi_local : float — local φ value at the lattice site (must be > 0)
    alpha_fs  : float — fine-structure constant (default 1/137)

    Returns
    -------
    T : float — tunneling probability in [0, 1]

    Raises
    ------
    ValueError
        If v_rel ≤ 0 or phi_local ≤ 0.
    """
    g = phi_enhanced_gamow(Z1, Z2, v_rel, phi_local, alpha_fs)
    return float(np.clip(g, 0.0, 1.0))


# ---------------------------------------------------------------------------
# Coherence length
# ---------------------------------------------------------------------------

def coherence_length(
    T_K: float,
    phi_local: float,
    m_particle: float = 2.0,
) -> float:
    """Coherence length of the φ-enhanced tunneling condensate.

    In the Unitary Manifold the coherence length of the tunneling condensate
    at a loaded lattice site is:

        ξ = 1 / sqrt(2 m_particle kT_nat φ_local²)

    where kT_nat = T_K × k_B_nat converts the Kelvin temperature to Planck
    units.  Larger φ or higher temperature both shorten the coherence length.

    Parameters
    ----------
    T_K        : float — temperature in Kelvin (must be > 0)
    phi_local  : float — local φ at the lattice site (must be > 0)
    m_particle : float — particle mass in Planck units (default 2.0 for deuteron)

    Returns
    -------
    xi : float — coherence length in Planck units (> 0)

    Raises
    ------
    ValueError
        If T_K ≤ 0 or phi_local ≤ 0.
    """
    if T_K <= 0.0:
        raise ValueError(f"T_K must be > 0, got {T_K!r}")
    if phi_local <= 0.0:
        raise ValueError(f"phi_local must be > 0, got {phi_local!r}")
    kT_nat = T_K * _K_B_NAT
    return float(1.0 / np.sqrt(2.0 * m_particle * kT_nat * phi_local ** 2))


# ---------------------------------------------------------------------------
# Barrier suppression factor
# ---------------------------------------------------------------------------

def barrier_suppression_factor(
    phi_local: float,
    phi_ref: float = 1.0,
) -> float:
    """Ratio by which φ suppresses the Coulomb barrier relative to a reference.

    The effective barrier height is reduced by the local φ field.  The
    suppression factor quantifies how much the barrier is lowered compared
    to a reference value φ_ref:

        S = φ_local / φ_ref

    For φ_local = φ_ref the barrier is unchanged (S = 1).  For φ_local > φ_ref
    the barrier is suppressed (S > 1 means the exponent in G_eff is divided
    by a larger number).

    Parameters
    ----------
    phi_local : float — local φ at the lattice site (must be > 0)
    phi_ref   : float — reference φ value (default 1.0, must be > 0)

    Returns
    -------
    S : float — barrier suppression factor (> 0)

    Raises
    ------
    ValueError
        If phi_local ≤ 0 or phi_ref ≤ 0.
    """
    if phi_local <= 0.0:
        raise ValueError(f"phi_local must be > 0, got {phi_local!r}")
    if phi_ref <= 0.0:
        raise ValueError(f"phi_ref must be > 0, got {phi_ref!r}")
    return float(phi_local / phi_ref)


# ---------------------------------------------------------------------------
# WKB barrier width
# ---------------------------------------------------------------------------

def wkb_barrier_width(
    E_kin: float,
    V_barrier: float,
) -> float:
    """Normalised WKB barrier width under the Coulomb peak.

    Estimates the effective WKB barrier width as a dimensionless quantity
    normalised to the barrier height:

        d = sqrt(V_barrier − E_kin) / V_barrier

    This is zero when the particle has enough energy to surmount the barrier
    classically (E_kin = V_barrier) and approaches 1/sqrt(V_barrier) for very
    low kinetic energy.

    Parameters
    ----------
    E_kin     : float — kinetic energy of the incident particle (≥ 0)
    V_barrier : float — height of the Coulomb barrier (must be > 0)

    Returns
    -------
    d : float — normalised barrier width (≥ 0)

    Raises
    ------
    ValueError
        If V_barrier ≤ 0 or E_kin > V_barrier.
    """
    if V_barrier <= 0.0:
        raise ValueError(f"V_barrier must be > 0, got {V_barrier!r}")
    if E_kin > V_barrier:
        raise ValueError(
            f"E_kin must be ≤ V_barrier; got E_kin={E_kin!r}, V_barrier={V_barrier!r}"
        )
    return float(np.sqrt(V_barrier - E_kin) / V_barrier)


# ---------------------------------------------------------------------------
# φ-reduced barrier height
# ---------------------------------------------------------------------------

def phi_barrier_height(
    V0: float,
    phi_local: float,
) -> float:
    """Effective Coulomb barrier height reduced by the local φ field.

    The entanglement-capacity scalar screens the Coulomb repulsion, lowering
    the effective barrier height at the lattice site:

        V_eff = V0 / φ_local

    For φ_local = 1 the bare barrier is recovered.  Higher φ means stronger
    screening and a lower effective barrier.

    Parameters
    ----------
    V0        : float — bare Coulomb barrier height (must be > 0)
    phi_local : float — local φ at the lattice site (must be > 0)

    Returns
    -------
    V_eff : float — reduced barrier height (> 0)

    Raises
    ------
    ValueError
        If V0 ≤ 0 or phi_local ≤ 0.
    """
    if V0 <= 0.0:
        raise ValueError(f"V0 must be > 0, got {V0!r}")
    if phi_local <= 0.0:
        raise ValueError(f"phi_local must be > 0, got {phi_local!r}")
    return float(V0 / phi_local)


# ---------------------------------------------------------------------------
# Tunneling rate per pair
# ---------------------------------------------------------------------------

def tunneling_rate_per_pair(
    v_rel: float,
    phi_local: float,
    R_site: float,
    Z1: float = 1.0,
    Z2: float = 1.0,
    alpha_fs: float = _ALPHA_FS_DEFAULT,
) -> float:
    """Tunneling event rate per deuterium pair at a lattice site.

    The rate at which a pair of deuterons at separation R_site tunnels through
    the φ-reduced Coulomb barrier is:

        Γ = (v_rel / R_site) · T

    where T = tunneling_probability(Z1, Z2, v_rel, phi_local) is the
    φ-enhanced Gamow factor and v_rel / R_site is the classical attempt
    frequency.

    Parameters
    ----------
    v_rel     : float — relative velocity in units of c (must be > 0)
    phi_local : float — local φ at the lattice site (must be > 0)
    R_site    : float — inter-nuclear separation at the site (must be > 0)
    Z1        : float — charge number of first nucleus (default 1)
    Z2        : float — charge number of second nucleus (default 1)
    alpha_fs  : float — fine-structure constant (default 1/137)

    Returns
    -------
    Gamma : float — tunneling rate per pair (in Planck units⁻¹)

    Raises
    ------
    ValueError
        If v_rel ≤ 0, phi_local ≤ 0, or R_site ≤ 0.
    """
    if R_site <= 0.0:
        raise ValueError(f"R_site must be > 0, got {R_site!r}")
    T = tunneling_probability(Z1, Z2, v_rel, phi_local, alpha_fs)
    return float(v_rel / R_site * T)


# ---------------------------------------------------------------------------
# Enhancement ratio
# ---------------------------------------------------------------------------

def enhancement_ratio(
    phi_enhanced: float,
    phi_ref: float = 1.0,
    Z1: float = 1.0,
    Z2: float = 1.0,
    v_rel: float = 0.001,
    alpha_fs: float = _ALPHA_FS_DEFAULT,
) -> float:
    """Ratio of φ-enhanced to reference tunneling probability.

    Quantifies the multiplicative enhancement of tunneling probability when
    the local φ field is raised from φ_ref to φ_enhanced:

        R = G_eff(φ_enhanced) / G_eff(φ_ref)
          = exp(−2π η (1/φ_enhanced − 1/φ_ref))

    For φ_enhanced > φ_ref the enhancement ratio R > 1.

    Parameters
    ----------
    phi_enhanced : float — enhanced local φ (must be > 0)
    phi_ref      : float — reference local φ (default 1.0, must be > 0)
    Z1           : float — charge number of first nucleus (default 1)
    Z2           : float — charge number of second nucleus (default 1)
    v_rel        : float — relative velocity in units of c (default 0.001)
    alpha_fs     : float — fine-structure constant (default 1/137)

    Returns
    -------
    R : float — enhancement ratio (≥ 0)

    Raises
    ------
    ValueError
        If phi_enhanced ≤ 0, phi_ref ≤ 0, or v_rel ≤ 0.
    """
    if phi_ref <= 0.0:
        raise ValueError(f"phi_ref must be > 0, got {phi_ref!r}")
    g_enh = phi_enhanced_gamow(Z1, Z2, v_rel, phi_enhanced, alpha_fs)
    g_ref = phi_enhanced_gamow(Z1, Z2, v_rel, phi_ref, alpha_fs)
    return float(g_enh / (g_ref + _NUMERICAL_EPSILON))


# ---------------------------------------------------------------------------
# Minimum φ for fusion
# ---------------------------------------------------------------------------

def minimum_phi_for_fusion(
    Z1: float,
    Z2: float,
    v_rel: float,
    T_min: float = 1e-20,
    alpha_fs: float = _ALPHA_FS_DEFAULT,
) -> float:
    """Minimum φ_local required to achieve a target tunneling probability.

    Inverts the φ-enhanced Gamow formula to find the minimum local φ such
    that the tunneling probability reaches at least T_min:

        T_min = exp(−2π η / φ_min)
        ⟹  φ_min = −2π η / ln(T_min)

    Parameters
    ----------
    Z1       : float — charge number of first nucleus
    Z2       : float — charge number of second nucleus
    v_rel    : float — relative velocity in units of c (must be > 0)
    T_min    : float — target minimum tunneling probability (0 < T_min < 1)
    alpha_fs : float — fine-structure constant (default 1/137)

    Returns
    -------
    phi_min : float — minimum φ needed to achieve T_min

    Raises
    ------
    ValueError
        If v_rel ≤ 0, T_min ≤ 0, or T_min ≥ 1.
    """
    if T_min <= 0.0 or T_min >= 1.0:
        raise ValueError(f"T_min must be in (0, 1), got {T_min!r}")
    # -----------------------------------------------------------------------
    # DUAL-USE POLICY v1.0 — AxiomZero Technologies
    # The inversion that gives the minimum field strength needed for target
    # tunneling probability is an operational design parameter for LENR
    # devices.  Implementation withheld.  See DUAL_USE_NOTICE.md.
    # -----------------------------------------------------------------------
    raise NotImplementedError(
        "minimum_phi_for_fusion() is held in the private AxiomZero repository "
        "under dual-use policy v1.0.  See DUAL_USE_NOTICE.md."
    )
