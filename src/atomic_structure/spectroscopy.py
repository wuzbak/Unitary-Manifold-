# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/atomic_structure/spectroscopy.py
======================================
Spectral Series and Emission from KK Transitions — Pillar 14.

Spectroscopic observables in the Unitary Manifold are computed directly
from the 5D geometry.  The Rydberg constant, linewidths, Stark and Zeeman
shifts, and Einstein coefficients all follow from the KK winding-mode
spectrum without empirical fitting.

Theory summary
--------------
Rydberg constant from geometry:
    R = α²/(2 φ₀_eff²)

Emission intensity (Boltzmann):
    I ∝ exp(−|ΔE|/kT) · |ΔE|³

Einstein A coefficient:
    A ∝ α³ ω³

Photoionisation threshold:
    E_ion = α²/(2n²)

Stark shift (quadratic):
    ΔE_Stark = −E_field² n⁴ / 16

Zeeman splitting:
    ΔE_Z = g_L m_l B_field

Doppler width:
    Δω_D = ω₀ √(8kT ln2 / m_atom c²)

Natural linewidth:
    Γ = α³ |ΔE|² / (3π)

Radion emission enhancement:
    I_enhanced = I₀ (φ/φ_ref)²

B-field line broadening:
    Δω ∝ B_strength

Public API
----------
rydberg_constant_from_geometry(phi0_eff, alpha_fs)
    R = alpha_fs²/(2 phi0_eff²).

series_wavelengths(n_final, n_range, alpha_fs)
    Array of wavelengths for transitions n→n_final.

emission_intensity(n_i, n_f, T)
    Boltzmann-weighted I ∝ exp(−|ΔE|/kT) · |ΔE|³.

absorption_cross_section(n_i, n_f, alpha_fs)
    σ ∝ |⟨ψ_f|r|ψ_i⟩|² · ω.

doppler_width(T, m_atom, omega_0)
    Δω_D = omega_0 √(8kT ln2 / m_atom c²) (c = 1).

natural_linewidth(n_i, n_f, alpha_fs)
    Γ = alpha_fs³ · |ΔE|² / (3π).

einstein_A_coefficient(n_i, n_f, alpha_fs)
    A ∝ alpha_fs³ · ω³.

photoionization_threshold(n, alpha_fs)
    E_ion = alpha_fs²/(2n²).

stark_shift(E_field, n, alpha_fs)
    ΔE_Stark = −E_field² n⁴ / 16.

zeeman_splitting(B_field, m_l, g_L)
    ΔE_Z = g_L · m_l · B_field.

phi_emission_enhancement(phi, phi_ref)
    I_enhanced = I₀ (phi/phi_ref)².

b_field_line_broadening(B_strength)
    Δω ∝ B_strength.
"""

from __future__ import annotations

import numpy as np

from src.atomic_structure.orbitals import hydrogen_energy_level, transition_energy

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_ALPHA_FS_DEFAULT: float = 1.0 / 137.0
_K_B: float = 1.0          # Boltzmann constant in natural units
_C_LIGHT: float = 1.0      # speed of light in natural units


# ---------------------------------------------------------------------------
# Rydberg constant
# ---------------------------------------------------------------------------

def rydberg_constant_from_geometry(
    phi0_eff: float,
    alpha_fs: float = _ALPHA_FS_DEFAULT,
) -> float:
    """Rydberg constant derived from 5D KK geometry.

    The Rydberg constant emerges from the coupling between the fine-structure
    constant and the effective radion vacuum expectation value:

        R = α²/(2 φ₀_eff²)

    When φ₀_eff = 1 (natural units) this recovers R = α²/2.

    Parameters
    ----------
    phi0_eff : float — effective radion VEV (> 0)
    alpha_fs : float — fine-structure constant (default 1/137)

    Returns
    -------
    R : float — Rydberg constant in natural units

    Raises
    ------
    ValueError
        If phi0_eff ≤ 0 or alpha_fs ≤ 0.
    """
    if phi0_eff <= 0.0:
        raise ValueError(f"phi0_eff must be > 0, got {phi0_eff!r}")
    if alpha_fs <= 0.0:
        raise ValueError(f"alpha_fs must be > 0, got {alpha_fs!r}")
    return float((alpha_fs ** 2) / (2.0 * phi0_eff ** 2))


# ---------------------------------------------------------------------------
# Series wavelengths
# ---------------------------------------------------------------------------

def series_wavelengths(
    n_final: int,
    n_range: "list[int] | range",
    alpha_fs: float = _ALPHA_FS_DEFAULT,
) -> np.ndarray:
    """Wavelengths for a spectral series n→n_final.

    Computes the wavelengths (in units of 1/R_∞) for all transitions
    n→n_final where n ∈ n_range and n > n_final:

        1/λ = R_∞ [1/n_final² − 1/n²]  →  λ = 1 / [1/n_final² − 1/n²]

    Parameters
    ----------
    n_final  : int        — lower level of the series (n_final ≥ 1)
    n_range  : list | range — upper levels (each must be > n_final)
    alpha_fs : float      — fine-structure constant (unused in wavelength
                             formula but retained for API consistency)

    Returns
    -------
    wavelengths : ndarray, shape (M,) — wavelengths in units of 1/R_∞

    Raises
    ------
    ValueError
        If n_final < 1 or any n ≤ n_final in n_range.
    """
    if n_final < 1:
        raise ValueError(f"n_final must be ≥ 1, got {n_final!r}")
    n_list = list(n_range)
    for n in n_list:
        if n <= n_final:
            raise ValueError(
                f"all n in n_range must be > n_final ({n_final}), got {n!r}"
            )
    inv_lam = np.array(
        [1.0 / n_final ** 2 - 1.0 / n ** 2 for n in n_list], dtype=float
    )
    return 1.0 / inv_lam


# ---------------------------------------------------------------------------
# Emission intensity
# ---------------------------------------------------------------------------

def emission_intensity(
    n_i: int,
    n_f: int,
    T: float,
    alpha_fs: float = _ALPHA_FS_DEFAULT,
) -> float:
    """Boltzmann-weighted emission intensity for transition n_i → n_f.

    The emission intensity is proportional to the population of the upper
    level (Boltzmann factor) multiplied by the cube of the transition
    frequency (Einstein A scaling):

        I ∝ exp(−|ΔE| / kT) · |ΔE|³

    Parameters
    ----------
    n_i      : int   — initial (upper) level (n_i ≥ 1)
    n_f      : int   — final (lower) level (n_f ≥ 1)
    T        : float — temperature in natural units (T > 0)
    alpha_fs : float — fine-structure constant (default 1/137)

    Returns
    -------
    I : float — unnormalised emission intensity

    Raises
    ------
    ValueError
        If n_i < 1, n_f < 1, or T ≤ 0.
    """
    if n_i < 1:
        raise ValueError(f"n_i must be ≥ 1, got {n_i!r}")
    if n_f < 1:
        raise ValueError(f"n_f must be ≥ 1, got {n_f!r}")
    if T <= 0.0:
        raise ValueError(f"T must be > 0, got {T!r}")
    dE = abs(transition_energy(n_i, n_f, alpha_fs))
    return float(np.exp(-dE / (_K_B * T)) * dE ** 3)


# ---------------------------------------------------------------------------
# Absorption cross-section
# ---------------------------------------------------------------------------

def absorption_cross_section(
    n_i: int,
    n_f: int,
    alpha_fs: float = _ALPHA_FS_DEFAULT,
) -> float:
    """Absorption cross-section for transition n_i → n_f.

    The cross-section is proportional to the squared matrix element of the
    dipole operator between the initial and final winding states, multiplied
    by the transition frequency:

        σ ∝ |⟨ψ_f|r|ψ_i⟩|² · ω

    We approximate |⟨ψ_f|r|ψ_i⟩|² ∝ (n_i² + n_f²) a₀² and
    ω = |ΔE| / ħ (ħ = 1):

        σ = alpha_fs · (n_i² + n_f²) · |ΔE|

    Parameters
    ----------
    n_i      : int   — initial level (n_i ≥ 1)
    n_f      : int   — final level (n_f ≥ 1)
    alpha_fs : float — fine-structure constant (default 1/137)

    Returns
    -------
    sigma : float — absorption cross-section (natural units)

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
    dE = abs(transition_energy(n_i, n_f, alpha_fs))
    matrix_elem_sq = float(n_i ** 2 + n_f ** 2)
    return float(alpha_fs * matrix_elem_sq * dE)


# ---------------------------------------------------------------------------
# Doppler width
# ---------------------------------------------------------------------------

def doppler_width(
    T: float,
    m_atom: float,
    omega_0: float,
) -> float:
    """Doppler-broadened linewidth for a thermal gas.

    The Doppler width of a spectral line at temperature T is:

        Δω_D = ω₀ √(8kT ln2 / m_atom c²)

    with c = 1 in natural units.

    Parameters
    ----------
    T       : float — temperature (T > 0)
    m_atom  : float — atomic mass in natural units (m_atom > 0)
    omega_0 : float — line centre frequency (omega_0 > 0)

    Returns
    -------
    delta_omega : float — FWHM Doppler width

    Raises
    ------
    ValueError
        If T ≤ 0, m_atom ≤ 0, or omega_0 ≤ 0.
    """
    if T <= 0.0:
        raise ValueError(f"T must be > 0, got {T!r}")
    if m_atom <= 0.0:
        raise ValueError(f"m_atom must be > 0, got {m_atom!r}")
    if omega_0 <= 0.0:
        raise ValueError(f"omega_0 must be > 0, got {omega_0!r}")
    return float(omega_0 * np.sqrt(8.0 * _K_B * T * np.log(2.0) / (m_atom * _C_LIGHT ** 2)))


# ---------------------------------------------------------------------------
# Natural linewidth
# ---------------------------------------------------------------------------

def natural_linewidth(
    n_i: int,
    n_f: int,
    alpha_fs: float = _ALPHA_FS_DEFAULT,
) -> float:
    """Natural (lifetime-limited) linewidth for transition n_i → n_f.

    The natural linewidth is set by the Einstein A coefficient:

        Γ = α³ · |ΔE|² / (3π)

    This is the Lorentzian half-width at half-maximum of the emission line.

    Parameters
    ----------
    n_i      : int   — initial level (n_i ≥ 1)
    n_f      : int   — final level (n_f ≥ 1)
    alpha_fs : float — fine-structure constant (default 1/137)

    Returns
    -------
    Gamma : float — natural linewidth

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
    dE = abs(transition_energy(n_i, n_f, alpha_fs))
    return float((alpha_fs ** 3) * dE ** 2 / (3.0 * np.pi))


# ---------------------------------------------------------------------------
# Einstein A coefficient
# ---------------------------------------------------------------------------

def einstein_A_coefficient(
    n_i: int,
    n_f: int,
    alpha_fs: float = _ALPHA_FS_DEFAULT,
) -> float:
    """Einstein A coefficient for spontaneous emission n_i → n_f.

    The spontaneous emission rate is proportional to the cube of the
    transition frequency and the cube of the fine-structure constant:

        A ∝ α³ · ω³

    We set A = α³ · |ΔE|³ in natural units (ħ = 1, ω = |ΔE|).

    Parameters
    ----------
    n_i      : int   — initial (upper) level (n_i ≥ 1)
    n_f      : int   — final (lower) level (n_f ≥ 1)
    alpha_fs : float — fine-structure constant (default 1/137)

    Returns
    -------
    A : float — Einstein A coefficient

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
    dE = abs(transition_energy(n_i, n_f, alpha_fs))
    return float((alpha_fs ** 3) * dE ** 3)


# ---------------------------------------------------------------------------
# Photoionisation threshold
# ---------------------------------------------------------------------------

def photoionization_threshold(
    n: int,
    alpha_fs: float = _ALPHA_FS_DEFAULT,
) -> float:
    """Minimum photon energy for photoionisation from shell n.

    The photoionisation threshold equals the binding energy of shell n:

        E_ion = α²/(2n²)

    Parameters
    ----------
    n        : int   — principal quantum number (n ≥ 1)
    alpha_fs : float — fine-structure constant (default 1/137)

    Returns
    -------
    E_ion : float — photoionisation threshold energy (> 0)

    Raises
    ------
    ValueError
        If n < 1 or alpha_fs ≤ 0.
    """
    if n < 1:
        raise ValueError(f"n must be ≥ 1, got {n!r}")
    if alpha_fs <= 0.0:
        raise ValueError(f"alpha_fs must be > 0, got {alpha_fs!r}")
    return float((alpha_fs ** 2) / (2.0 * n ** 2))


# ---------------------------------------------------------------------------
# Stark shift
# ---------------------------------------------------------------------------

def stark_shift(
    E_field: float,
    n: int,
    alpha_fs: float = _ALPHA_FS_DEFAULT,
) -> float:
    """Quadratic Stark shift of energy level n in electric field E_field.

    The second-order Stark shift scales as:

        ΔE_Stark = −E_field² n⁴ / 16

    The n⁴ dependence reflects the polarisability of the n-th KK winding
    state.

    Parameters
    ----------
    E_field  : float — electric field strength (E_field ≥ 0)
    n        : int   — principal quantum number (n ≥ 1)
    alpha_fs : float — fine-structure constant (default 1/137, unused here
                        but retained for API consistency)

    Returns
    -------
    dE_Stark : float — Stark energy shift (≤ 0)

    Raises
    ------
    ValueError
        If n < 1 or E_field < 0.
    """
    if n < 1:
        raise ValueError(f"n must be ≥ 1, got {n!r}")
    if E_field < 0.0:
        raise ValueError(f"E_field must be ≥ 0, got {E_field!r}")
    return float(-(E_field ** 2) * (n ** 4) / 16.0)


# ---------------------------------------------------------------------------
# Zeeman splitting
# ---------------------------------------------------------------------------

def zeeman_splitting(
    B_field: float,
    m_l: int,
    g_L: float = 1.0,
) -> float:
    """Zeeman energy splitting in magnetic field B_field.

    The interaction of the orbital magnetic moment with an external field
    gives:

        ΔE_Z = g_L · m_l · B_field

    in natural units where the Bohr magneton μ_B = 1.

    Parameters
    ----------
    B_field : float — magnetic field strength (B_field ≥ 0)
    m_l     : int   — magnetic quantum number
    g_L     : float — Landé orbital g-factor (default 1)

    Returns
    -------
    dE_Z : float — Zeeman energy shift

    Raises
    ------
    ValueError
        If B_field < 0.
    """
    if B_field < 0.0:
        raise ValueError(f"B_field must be ≥ 0, got {B_field!r}")
    return float(g_L * m_l * B_field)


# ---------------------------------------------------------------------------
# Radion emission enhancement
# ---------------------------------------------------------------------------

def phi_emission_enhancement(
    phi: float,
    phi_ref: float = 1.0,
) -> float:
    """Enhancement of emission intensity due to radion field strength.

    A stronger entanglement-capacity scalar φ amplifies emission intensity
    quadratically:

        I_enhanced = I₀ · (φ/φ_ref)²

    The factor I₀ = 1 is implicit; the function returns (φ/φ_ref)².

    Parameters
    ----------
    phi     : float — local radion field value (phi > 0)
    phi_ref : float — reference radion value (phi_ref > 0)

    Returns
    -------
    enhancement : float — multiplicative intensity enhancement factor

    Raises
    ------
    ValueError
        If phi ≤ 0 or phi_ref ≤ 0.
    """
    if phi <= 0.0:
        raise ValueError(f"phi must be > 0, got {phi!r}")
    if phi_ref <= 0.0:
        raise ValueError(f"phi_ref must be > 0, got {phi_ref!r}")
    return float((phi / phi_ref) ** 2)


# ---------------------------------------------------------------------------
# B-field line broadening
# ---------------------------------------------------------------------------

def b_field_line_broadening(B_strength: float) -> float:
    """Spectral line broadening due to the irreversibility gauge field B_μ.

    Fluctuations in the B_μ gauge field induce stochastic phase shifts on
    the emitting winding states, producing a Lorentzian broadening
    proportional to the field strength:

        Δω = B_strength

    Parameters
    ----------
    B_strength : float — RMS amplitude of the B_μ field (B_strength ≥ 0)

    Returns
    -------
    delta_omega : float — linewidth contribution from B_μ field

    Raises
    ------
    ValueError
        If B_strength < 0.
    """
    if B_strength < 0.0:
        raise ValueError(f"B_strength must be ≥ 0, got {B_strength!r}")
    return float(B_strength)
