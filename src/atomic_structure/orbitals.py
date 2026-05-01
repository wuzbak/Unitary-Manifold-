# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/atomic_structure/orbitals.py
=================================
Atomic Orbitals as KK Winding Modes — Pillar 14.

In the Unitary Manifold, atomic orbitals are not empirical constructs; they
are the quantised winding states of the compact S¹/Z₂ dimension.  The
principal quantum number n equals the KK winding number n_w, and every
orbital property follows from 5D geometry without free parameters.

Theory summary
--------------
Energy levels (Rydberg from KK geometry):
    E_n = −α²/(2n²)    (α = fine-structure constant ≈ 1/137)

Orbital radius (Bohr scaling from KK):
    r_n = n² a₀

Wavefunction amplitude (ground-state-like envelope):
    |ψ_n(r)|² ∝ exp(−2r / na₀) / (na₀)³

Shell degeneracy (winding quantisation):
    g(n) = 2n²

Angular momentum (quantised on compact dimension):
    L² = l(l+1) ħ²    → returns l(l+1)

Spin-orbit coupling:
    ΔE_SO = α²Z⁴ / [2n³ l(l+1)]   (l ≥ 1)

Transition energy:
    ΔE = E_nf − E_ni

Radion field at orbital:
    φ(n) = φ₀ / n   (entanglement capacity decreases with shell)

Public API
----------
hydrogen_energy_level(n, alpha_fs)
    E_n = −alpha_fs²/(2n²) in Rydberg units.

orbital_radius(n, a0)
    r_n = n² a₀.

wavefunction_amplitude(r, n, a0)
    |ψ_n(r)|² ∝ exp(−2r/na₀) / (na₀)³.

quantum_degeneracy(n)
    2n² states per shell.

angular_momentum_squared(l)
    l(l+1).

magnetic_quantum_states(l)
    List of integers m from −l to +l.

spin_orbital_coupling(n, l, j, Z)
    ΔE_SO = α²Z⁴ / [2n³ l(l+1)] for l ≥ 1.

transition_energy(n_i, n_f, alpha_fs)
    ΔE = E_nf − E_ni.

lyman_wavelength(n)
    λ in units of 1/R_∞ for Lyman series (n_final=1).

balmer_wavelength(n)
    λ in units of 1/R_∞ for Balmer series (n_final=2).

phi_field_at_orbital(n, phi0)
    φ(n) = φ₀/n.

selection_rule_allowed(l_i, l_j, m_i, m_j)
    True iff Δl = ±1 and Δm ∈ {0, ±1}.
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

_ALPHA_FS_DEFAULT: float = 1.0 / 137.0
_A0_DEFAULT: float = 1.0


# ---------------------------------------------------------------------------
# Energy levels
# ---------------------------------------------------------------------------

def hydrogen_energy_level(n: int, alpha_fs: float = _ALPHA_FS_DEFAULT) -> float:
    """Hydrogen energy level from KK winding geometry.

    The Rydberg energy spectrum emerges from the quantisation of winding
    states on S¹/Z₂.  For winding number n_w = n the orbital energy is:

        E_n = −α²/(2n²)

    The result is in Rydberg units (E₁ = −α²/2 ≈ −2.66 × 10⁻⁵ Rydberg).

    Parameters
    ----------
    n        : int   — principal quantum number / KK winding number (n ≥ 1)
    alpha_fs : float — fine-structure constant (default 1/137)

    Returns
    -------
    E_n : float — energy level in Rydberg units (≤ 0)

    Raises
    ------
    ValueError
        If n < 1 or alpha_fs ≤ 0.
    """
    if n < 1:
        raise ValueError(f"n must be ≥ 1, got {n!r}")
    if alpha_fs <= 0.0:
        raise ValueError(f"alpha_fs must be > 0, got {alpha_fs!r}")
    return float(-(alpha_fs ** 2) / (2.0 * n ** 2))


# ---------------------------------------------------------------------------
# Orbital radius
# ---------------------------------------------------------------------------

def orbital_radius(n: int, a0: float = _A0_DEFAULT) -> float:
    """Bohr-scaled orbital radius for principal quantum number n.

    The mean radius of the KK winding state n on the compactified S¹/Z₂
    scales as n² in Bohr units, reproducing the hydrogen exact result:

        r_n = n² a₀

    Parameters
    ----------
    n  : int   — principal quantum number (n ≥ 1)
    a0 : float — Bohr radius unit (default 1)

    Returns
    -------
    r_n : float — orbital radius

    Raises
    ------
    ValueError
        If n < 1 or a0 ≤ 0.
    """
    if n < 1:
        raise ValueError(f"n must be ≥ 1, got {n!r}")
    if a0 <= 0.0:
        raise ValueError(f"a0 must be > 0, got {a0!r}")
    return float(n ** 2 * a0)


# ---------------------------------------------------------------------------
# Wavefunction amplitude
# ---------------------------------------------------------------------------

def wavefunction_amplitude(
    r: np.ndarray,
    n: int,
    a0: float = _A0_DEFAULT,
) -> np.ndarray:
    """Probability density |ψ_n(r)|² for KK winding state n.

    The radial probability density of the n-th winding state is modelled
    by the ground-state-like exponential envelope scaled by the shell radius
    na₀:

        |ψ_n(r)|² ∝ exp(−2r / na₀) / (na₀)³

    The prefactor ensures dimensional consistency; the result is not
    normalised to unity but provides the correct r-dependence.

    Parameters
    ----------
    r  : array-like — radial grid (r ≥ 0)
    n  : int        — principal quantum number (n ≥ 1)
    a0 : float      — Bohr radius unit (default 1)

    Returns
    -------
    psi2 : ndarray — probability density at each r

    Raises
    ------
    ValueError
        If n < 1 or a0 ≤ 0.
    """
    if n < 1:
        raise ValueError(f"n must be ≥ 1, got {n!r}")
    if a0 <= 0.0:
        raise ValueError(f"a0 must be > 0, got {a0!r}")
    r_arr = np.asarray(r, dtype=float)
    scale = n * a0
    return np.exp(-2.0 * r_arr / scale) / (scale ** 3)


# ---------------------------------------------------------------------------
# Degeneracy
# ---------------------------------------------------------------------------

def quantum_degeneracy(n: int) -> int:
    """Number of degenerate quantum states in shell n.

    The KK quantisation on S¹/Z₂ yields exactly 2n² distinct winding states
    per shell, which equals the degeneracy of the n-th hydrogen shell
    (including spin):

        g(n) = 2n²

    Parameters
    ----------
    n : int — principal quantum number (n ≥ 1)

    Returns
    -------
    g : int — degeneracy (2n²)

    Raises
    ------
    ValueError
        If n < 1.
    """
    if n < 1:
        raise ValueError(f"n must be ≥ 1, got {n!r}")
    return 2 * n ** 2


# ---------------------------------------------------------------------------
# Angular momentum
# ---------------------------------------------------------------------------

def angular_momentum_squared(l: int) -> float:
    """Squared angular momentum eigenvalue in units of ħ².

    The compact S¹/Z₂ geometry quantises orbital angular momentum such that:

        L² = l(l+1) ħ²   → returns l(l+1)

    Parameters
    ----------
    l : int — orbital angular momentum quantum number (l ≥ 0)

    Returns
    -------
    L2 : float — l(l+1)

    Raises
    ------
    ValueError
        If l < 0.
    """
    if l < 0:
        raise ValueError(f"l must be ≥ 0, got {l!r}")
    return float(l * (l + 1))


def magnetic_quantum_states(l: int) -> list[int]:
    """List of allowed magnetic quantum numbers for angular momentum l.

    For orbital quantum number l the magnetic quantum number m_l takes
    integer values from −l to +l inclusive, giving 2l+1 states:

        m_l ∈ {−l, −l+1, …, 0, …, l−1, l}

    Parameters
    ----------
    l : int — orbital angular momentum quantum number (l ≥ 0)

    Returns
    -------
    states : list[int] — magnetic quantum numbers

    Raises
    ------
    ValueError
        If l < 0.
    """
    if l < 0:
        raise ValueError(f"l must be ≥ 0, got {l!r}")
    return list(range(-l, l + 1))


# ---------------------------------------------------------------------------
# Spin-orbit coupling
# ---------------------------------------------------------------------------

def spin_orbital_coupling(
    n: int,
    l: int,
    j: float,
    Z: int,
    alpha_fs: float = _ALPHA_FS_DEFAULT,
) -> float:
    """Spin-orbit energy splitting from 5D geometry.

    The spin-orbit coupling arises from the curvature of the compact
    dimension.  For l ≥ 1 the energy shift is:

        ΔE_SO = α²Z⁴ / [2n³ l(l+1)]

    The j quantum number is accepted for API completeness (used by
    fine_structure.py for full Dirac treatment) but the leading-order result
    depends only on n, l, Z.

    Parameters
    ----------
    n        : int   — principal quantum number (n ≥ 1)
    l        : int   — orbital quantum number (l ≥ 1)
    j        : float — total angular momentum quantum number
    Z        : int   — nuclear charge (Z ≥ 1)
    alpha_fs : float — fine-structure constant (default 1/137)

    Returns
    -------
    dE_SO : float — spin-orbit energy splitting (in Rydberg units)

    Raises
    ------
    ValueError
        If n < 1, l < 1, Z < 1, or alpha_fs ≤ 0.
    """
    if n < 1:
        raise ValueError(f"n must be ≥ 1, got {n!r}")
    if l < 1:
        raise ValueError(f"l must be ≥ 1 for spin-orbit coupling, got {l!r}")
    if Z < 1:
        raise ValueError(f"Z must be ≥ 1, got {Z!r}")
    if alpha_fs <= 0.0:
        raise ValueError(f"alpha_fs must be > 0, got {alpha_fs!r}")
    return float((alpha_fs ** 2) * (Z ** 4) / (2.0 * n ** 3 * l * (l + 1)))


# ---------------------------------------------------------------------------
# Transition energy
# ---------------------------------------------------------------------------

def transition_energy(
    n_i: int,
    n_f: int,
    alpha_fs: float = _ALPHA_FS_DEFAULT,
) -> float:
    """Photon energy emitted or absorbed in an n_i → n_f transition.

    The transition energy is the difference of the two energy levels:

        ΔE = E_nf − E_ni = −α²/(2n_f²) + α²/(2n_i²)

    A positive result means emission (n_i > n_f); negative means absorption.

    Parameters
    ----------
    n_i      : int   — initial principal quantum number (n_i ≥ 1)
    n_f      : int   — final principal quantum number (n_f ≥ 1)
    alpha_fs : float — fine-structure constant (default 1/137)

    Returns
    -------
    dE : float — transition energy in Rydberg units

    Raises
    ------
    ValueError
        If n_i < 1, n_f < 1, or alpha_fs ≤ 0.
    """
    if n_i < 1:
        raise ValueError(f"n_i must be ≥ 1, got {n_i!r}")
    if n_f < 1:
        raise ValueError(f"n_f must be ≥ 1, got {n_f!r}")
    if alpha_fs <= 0.0:
        raise ValueError(f"alpha_fs must be > 0, got {alpha_fs!r}")
    return float(hydrogen_energy_level(n_f, alpha_fs) - hydrogen_energy_level(n_i, alpha_fs))


# ---------------------------------------------------------------------------
# Spectral series wavelengths
# ---------------------------------------------------------------------------

def lyman_wavelength(n: int) -> float:
    """Wavelength for Lyman series transition n → 1.

    The inverse wavelength (in units of the Rydberg constant R_∞) is:

        1/λ = R_∞ (1 − 1/n²)

    Returns λ = 1 / R_∞(1 − 1/n²) in units of 1/R_∞.

    Parameters
    ----------
    n : int — upper level (n ≥ 2)

    Returns
    -------
    lam : float — wavelength in units of 1/R_∞

    Raises
    ------
    ValueError
        If n < 2.
    """
    if n < 2:
        raise ValueError(f"n must be ≥ 2 for Lyman series, got {n!r}")
    return float(1.0 / (1.0 - 1.0 / n ** 2))


def balmer_wavelength(n: int) -> float:
    """Wavelength for Balmer series transition n → 2.

    The inverse wavelength (in units of R_∞) is:

        1/λ = R_∞ (1/4 − 1/n²)

    Returns λ = 1 / R_∞(1/4 − 1/n²) in units of 1/R_∞.

    Parameters
    ----------
    n : int — upper level (n ≥ 3)

    Returns
    -------
    lam : float — wavelength in units of 1/R_∞

    Raises
    ------
    ValueError
        If n < 3.
    """
    if n < 3:
        raise ValueError(f"n must be ≥ 3 for Balmer series, got {n!r}")
    return float(1.0 / (0.25 - 1.0 / n ** 2))


# ---------------------------------------------------------------------------
# Radion field at orbital
# ---------------------------------------------------------------------------

def phi_field_at_orbital(n: int, phi0: float = 1.0) -> float:
    """Radion scalar field value at the n-th orbital.

    The entanglement-capacity scalar decreases with increasing shell number,
    reflecting the dilution of the compact dimension curvature at larger
    winding radii:

        φ(n) = φ₀ / n

    Parameters
    ----------
    n    : int   — principal quantum number (n ≥ 1)
    phi0 : float — scalar field at n=1 (default 1)

    Returns
    -------
    phi_n : float — radion field value at shell n

    Raises
    ------
    ValueError
        If n < 1 or phi0 ≤ 0.
    """
    if n < 1:
        raise ValueError(f"n must be ≥ 1, got {n!r}")
    if phi0 <= 0.0:
        raise ValueError(f"phi0 must be > 0, got {phi0!r}")
    return float(phi0 / n)


# ---------------------------------------------------------------------------
# Selection rules
# ---------------------------------------------------------------------------

def selection_rule_allowed(
    l_i: int,
    l_j: int,
    m_i: int,
    m_j: int,
) -> bool:
    """Check electric-dipole selection rule for an atomic transition.

    The electric-dipole selection rules require:

        Δl = l_j − l_i = ±1
        Δm = m_j − m_i ∈ {−1, 0, +1}

    Both conditions must be satisfied for the transition to be allowed.

    Parameters
    ----------
    l_i : int — initial orbital quantum number (l ≥ 0)
    l_j : int — final orbital quantum number (l ≥ 0)
    m_i : int — initial magnetic quantum number
    m_j : int — final magnetic quantum number

    Returns
    -------
    allowed : bool — True if both selection rules are satisfied
    """
    delta_l = l_j - l_i
    delta_m = m_j - m_i
    return delta_l in (-1, 1) and delta_m in (-1, 0, 1)
