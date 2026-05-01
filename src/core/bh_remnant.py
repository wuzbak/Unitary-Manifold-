# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/bh_remnant.py
======================
Pillar 28 — Kaluza-Klein Black Hole Remnant (Theorem XVII).

Physical context
----------------
Standard Hawking evaporation predicts that a black hole shrinks indefinitely
until it reaches the Planck scale, at which point quantum gravity effects become
important and the evaporation history is unclear.  The most troubling consequence
is the **information paradox**: if the hole evaporates completely, any information
it swallowed is destroyed — violating unitarity.

In the Unitary Manifold framework the Goldberger–Wise stabilisation potential

    V(φ) = ½ m²_φ (φ − φ₀)²

provides a hard lower bound on the radion field:

    φ ≥ φ_min > 0

Because the Hawking temperature derived in Theorem XIV (evolution.py:
hawking_temperature) is

    T_H(x) = |∂_r φ / φ| / (2π)

and the GW restoring force caps the maximum gradient |∂_r φ| at

    |∂_r φ|_max = m_φ · (φ₀ − φ_min)

(the gradient that the GW potential produces when φ is pulled to its minimum
value φ_min), there is a maximum achievable Hawking temperature:

    T_H_max = m_φ (φ₀ − φ_min) / (2π φ_min)

A black hole whose mass has shrunk to the point where T_H = T_H_max cannot
lose any more mass: further evaporation would require |∂_r φ| > |∂_r φ|_max,
which the GW potential forbids.  The black hole freezes at the **remnant mass**:

    M_rem = φ_min / (8π m_φ (φ₀ − φ_min))

(derived from the surface-gravity relation κ = m_φ(φ₀−φ_min)/φ_min combined
with the Bekenstein–Hawking area formula; the product T_H_max × M_rem = 1/(16π²)
is a pure numerical constant in Planck units).

The remnant stores all information originally swallowed by the black hole as
5D topological geometry (Theorem XII, QUANTUM_THEOREMS.md §XII).  The
information content is

    I_rem = S_rem / ln 2 = 4π M_rem² / ln 2   (bits, Bekenstein–Hawking)

This result closely parallels the 7-dimensional study (Platania et al., 2024–2025)
in which hidden extra dimensions generate a repulsive force that halts evaporation.
The Unitary Manifold achieves the same outcome in 5 dimensions through the
Goldberger–Wise mechanism rather than by invoking three additional hidden
dimensions — it is dimensionally more parsimonious.

Connection to Pillar 6 (black_hole_transceiver.py)
----------------------------------------------------
The GW-echo delay τ_echo = 2π ⟨φ⟩ (gw_echo_delay in black_hole_transceiver.py)
acquires a physical floor: as φ → φ_min the round-trip time across the compact
dimension reaches its minimum, and the echo sequence terminates not at zero
amplitude but at the remnant entropy S_rem = 4π M_rem².  The remnant is the
final static topology that persists after the last echo.

All quantities are in **natural (Planck) units**: ℏ = c = G = k_B = 1.

Public API
----------
remnant_mass(phi_min, m_phi, phi0)
    Minimum BH mass below which Hawking evaporation halts:
        M_rem = φ_min / (8π m_φ (φ₀ − φ_min))

remnant_temperature(phi_min, phi0, m_phi)
    Maximum Hawking temperature — the temperature at which evaporation freezes:
        T_H_max = m_φ (φ₀ − φ_min) / (2π φ_min)

remnant_entropy(M_rem)
    Bekenstein–Hawking entropy of the remnant:
        S_rem = 4π M_rem²

remnant_information_bits(M_rem)
    Information stored in the remnant in bits:
        I_rem = S_rem / ln(2)

kk_stabilization_repulsion(phi, phi_min, m_phi)
    Effective GW repulsive potential energy density that prevents φ < φ_min:
        V_rep(φ) = ½ m_phi² (φ − phi_min)²

evaporation_fraction_remaining(M_initial, M_rem)
    Fraction of the original BH mass that survives in the remnant:
        f_rem = M_rem / M_initial

compare_7d_vs_5d_remnant(phi_min, m_phi, phi0)
    Compare the 5D UM remnant scale to the 7D framework prediction M_rem ∝ M_Planck.
    Returns a dict with keys '5d_M_rem', '7d_M_rem_planck_units', 'ratio',
    'dimension_count_5d', 'dimension_count_7d'.
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

import math


# ---------------------------------------------------------------------------
# Module-level constants (Planck units throughout)
# ---------------------------------------------------------------------------

_TWO_PI = 2.0 * math.pi
_FOUR_PI = 4.0 * math.pi
_EIGHT_PI = 8.0 * math.pi
_LN2 = math.log(2.0)

# Canonical GW parameters from the braided-winding sector
# (consistent with braided_winding.py and non_gaussianity.py)
PHI0_CANONICAL = 1.0        # Goldberger–Wise vacuum expectation value (Planck units)
M_PHI_CANONICAL = 1.0       # GW mass parameter (Planck units)
PHI_MIN_CANONICAL = 0.1     # representative lower bound on φ

# For compare_7d_vs_5d_remnant: 7D frameworks predict M_rem ~ O(1) × M_Planck
# (see Platania et al. 2024–2025 for the 7D prediction band)
_7D_M_REM_PLANCK = 1.0      # M_rem^{7D} ≈ 1 M_Planck (order-of-magnitude)


# ---------------------------------------------------------------------------
# remnant_mass
# ---------------------------------------------------------------------------

def remnant_mass(phi_min: float, m_phi: float, phi0: float) -> float:
    """Minimum BH mass below which Hawking evaporation cannot continue.

    Derived from the condition T_H = T_H_max:

        1 / (8π M_rem) = m_φ (φ₀ − φ_min) / (2π φ_min)

    Solving for M_rem:

        M_rem = φ_min / (8π m_φ (φ₀ − φ_min))

    Parameters
    ----------
    phi_min : float
        GW-stabilised lower bound on the radion field (φ_min > 0).
    m_phi : float
        Goldberger–Wise mass parameter (m_φ > 0).
    phi0 : float
        GW vacuum expectation value (φ₀ > φ_min).

    Returns
    -------
    M_rem : float
        Remnant mass in Planck units (> 0).

    Raises
    ------
    ValueError
        If phi_min ≤ 0, m_phi ≤ 0, phi0 ≤ phi_min.
    """
    _validate_phi(phi_min, m_phi, phi0)
    delta = phi0 - phi_min
    return phi_min / (_EIGHT_PI * m_phi * delta)


# ---------------------------------------------------------------------------
# remnant_temperature
# ---------------------------------------------------------------------------

def remnant_temperature(phi_min: float, phi0: float, m_phi: float) -> float:
    """Maximum Hawking temperature — the temperature at which evaporation halts.

    The Goldberger–Wise potential caps |∂_r φ| at m_φ (φ₀ − φ_min), so:

        T_H_max = m_φ (φ₀ − φ_min) / (2π φ_min)

    Parameters
    ----------
    phi_min : float — GW lower bound on the radion (> 0)
    phi0    : float — GW vacuum value (> phi_min)
    m_phi   : float — GW mass parameter (> 0)

    Returns
    -------
    T_H_max : float  (> 0)

    Raises
    ------
    ValueError
        If phi_min ≤ 0, m_phi ≤ 0, phi0 ≤ phi_min.
    """
    _validate_phi(phi_min, m_phi, phi0)
    delta = phi0 - phi_min
    return m_phi * delta / (_TWO_PI * phi_min)


# ---------------------------------------------------------------------------
# remnant_entropy
# ---------------------------------------------------------------------------

def remnant_entropy(M_rem: float) -> float:
    """Bekenstein–Hawking entropy of the BH remnant.

        S_rem = 4π M_rem²

    Parameters
    ----------
    M_rem : float — remnant mass in Planck units (≥ 0)

    Returns
    -------
    S_rem : float  (≥ 0)

    Raises
    ------
    ValueError
        If M_rem < 0.
    """
    if M_rem < 0.0:
        raise ValueError(f"M_rem must be ≥ 0, got {M_rem!r}")
    return _FOUR_PI * M_rem ** 2


# ---------------------------------------------------------------------------
# remnant_information_bits
# ---------------------------------------------------------------------------

def remnant_information_bits(M_rem: float) -> float:
    """Information stored in the BH remnant in bits.

        I_rem = S_rem / ln(2) = 4π M_rem² / ln(2)

    Parameters
    ----------
    M_rem : float — remnant mass in Planck units (≥ 0)

    Returns
    -------
    I_rem : float  (≥ 0, in bits)

    Raises
    ------
    ValueError
        If M_rem < 0.
    """
    return remnant_entropy(M_rem) / _LN2


# ---------------------------------------------------------------------------
# kk_stabilization_repulsion
# ---------------------------------------------------------------------------

def kk_stabilization_repulsion(
    phi: float,
    phi_min: float,
    m_phi: float,
) -> float:
    """Effective GW repulsive potential energy density preventing φ < φ_min.

        V_rep(φ) = ½ m_φ² (φ − φ_min)²

    This is the contribution from the Goldberger–Wise potential evaluated at
    the floor value φ_min.  It acts as an effective repulsion — any attempt to
    push φ below φ_min increases this density, providing the restoring force.

    Parameters
    ----------
    phi     : float — current radion value (> 0)
    phi_min : float — GW stabilisation floor (> 0)
    m_phi   : float — GW mass parameter (> 0)

    Returns
    -------
    V_rep : float  (≥ 0)

    Raises
    ------
    ValueError
        If phi ≤ 0, phi_min ≤ 0, or m_phi ≤ 0.
    """
    if phi <= 0.0:
        raise ValueError(f"phi must be > 0, got {phi!r}")
    if phi_min <= 0.0:
        raise ValueError(f"phi_min must be > 0, got {phi_min!r}")
    if m_phi <= 0.0:
        raise ValueError(f"m_phi must be > 0, got {m_phi!r}")
    return 0.5 * m_phi ** 2 * (phi - phi_min) ** 2


# ---------------------------------------------------------------------------
# evaporation_fraction_remaining
# ---------------------------------------------------------------------------

def evaporation_fraction_remaining(M_initial: float, M_rem: float) -> float:
    """Fraction of the original BH mass that survives in the remnant.

        f_rem = M_rem / M_initial

    For a physical black hole M_initial > M_rem > 0, so 0 < f_rem < 1.

    Parameters
    ----------
    M_initial : float — initial BH mass (> M_rem > 0)
    M_rem     : float — remnant mass (> 0)

    Returns
    -------
    f_rem : float  (0 < f_rem < 1)

    Raises
    ------
    ValueError
        If M_initial ≤ 0, M_rem ≤ 0, or M_initial ≤ M_rem.
    """
    if M_initial <= 0.0:
        raise ValueError(f"M_initial must be > 0, got {M_initial!r}")
    if M_rem <= 0.0:
        raise ValueError(f"M_rem must be > 0, got {M_rem!r}")
    if M_initial <= M_rem:
        raise ValueError(
            f"M_initial ({M_initial!r}) must be > M_rem ({M_rem!r})"
        )
    return M_rem / M_initial


# ---------------------------------------------------------------------------
# compare_7d_vs_5d_remnant
# ---------------------------------------------------------------------------

def compare_7d_vs_5d_remnant(
    phi_min: float,
    m_phi: float,
    phi0: float,
) -> dict:
    """Compare the 5D UM remnant scale to the 7D framework prediction.

    The Unitary Manifold (5D) achieves remnant formation via the Goldberger–Wise
    stabilisation mechanism.  A recent 7-dimensional study (Platania et al.,
    2024–2025) requires 3 extra dimensions beyond 4D to generate a repulsive
    force that halts evaporation, predicting M_rem ~ O(1) × M_Planck.

    Both frameworks agree that black holes do not evaporate completely.  The UM
    result is dimensionally more parsimonious: only one extra dimension is needed.

    Parameters
    ----------
    phi_min : float — GW lower bound on the radion (> 0)
    m_phi   : float — GW mass parameter (> 0)
    phi0    : float — GW vacuum value (> phi_min)

    Returns
    -------
    result : dict with keys
        '5d_M_rem'              — UM remnant mass (Planck units)
        '7d_M_rem_planck_units' — 7D framework prediction (= 1.0 M_Planck)
        'ratio'                 — 5d_M_rem / 7d_M_rem_planck_units
        'dimension_count_5d'    — total spacetime dimensions in the UM (= 5)
        'dimension_count_7d'    — total spacetime dimensions in 7D study (= 7)
        'extra_dimensions_5d'   — number of extra dimensions in UM (= 1)
        'extra_dimensions_7d'   — number of extra dimensions in 7D study (= 3)

    Raises
    ------
    ValueError
        If phi_min ≤ 0, m_phi ≤ 0, phi0 ≤ phi_min.
    """
    _validate_phi(phi_min, m_phi, phi0)
    M_5d = remnant_mass(phi_min, m_phi, phi0)
    return {
        "5d_M_rem": M_5d,
        "7d_M_rem_planck_units": _7D_M_REM_PLANCK,
        "ratio": M_5d / _7D_M_REM_PLANCK,
        "dimension_count_5d": 5,
        "dimension_count_7d": 7,
        "extra_dimensions_5d": 1,
        "extra_dimensions_7d": 3,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _validate_phi(phi_min: float, m_phi: float, phi0: float) -> None:
    """Raise ValueError for unphysical GW parameter combinations."""
    if phi_min <= 0.0:
        raise ValueError(f"phi_min must be > 0, got {phi_min!r}")
    if m_phi <= 0.0:
        raise ValueError(f"m_phi must be > 0, got {m_phi!r}")
    if phi0 <= phi_min:
        raise ValueError(
            f"phi0 ({phi0!r}) must be strictly greater than phi_min ({phi_min!r})"
        )
