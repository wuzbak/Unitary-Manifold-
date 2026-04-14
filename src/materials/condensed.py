# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/materials/condensed.py
===========================
Condensed Matter as φ-Field Lattice Dynamics — Pillar 26: Materials Science.

Theory
------
A crystalline solid is a φ-field lattice where electrons are collective
φ excitations and phonons are irreversibility-field oscillations.  The
band gap is the energy cost of promoting a φ excitation across the
forbidden zone — it is determined by the lattice B_μ symmetry breaking.
Phase transitions occur when thermal B_μ noise exceeds the coherence
energy of the φ order parameter.
"""

from __future__ import annotations
import math
import numpy as np

_EPS = 1e-30
_k_B = 8.617333262e-5   # eV K⁻¹


def band_gap_phi(E_gap_eV: float, k_BT_eV: float) -> float:
    """Thermal occupation of the conduction band via Boltzmann.

    n_cb = exp(−E_gap / (2 k_B T))   (intrinsic carrier fraction)

    Parameters
    ----------
    E_gap_eV : float — band gap in eV (must be ≥ 0)
    k_BT_eV  : float — thermal energy k_B T in eV (must be > 0)

    Returns
    -------
    n_cb : float — fractional conduction band occupation
    """
    if E_gap_eV < 0.0:
        raise ValueError(f"E_gap_eV must be ≥ 0, got {E_gap_eV!r}")
    if k_BT_eV <= 0.0:
        raise ValueError(f"k_BT_eV must be > 0, got {k_BT_eV!r}")
    return float(math.exp(-E_gap_eV / (2.0 * k_BT_eV)))


def fermi_phi_level(E_gap_eV: float, T_K: float,
                     donor_conc: float = 0.0, acceptor_conc: float = 0.0) -> float:
    """Fermi level position relative to mid-gap in eV.

    E_F = E_gap/2 + (k_B T / 2) × ln(donor_conc / acceptor_conc + 1)

    Parameters
    ----------
    E_gap_eV     : float — band gap eV (must be ≥ 0)
    T_K          : float — temperature K (must be > 0)
    donor_conc   : float — donor dopant concentration cm⁻³ (must be ≥ 0)
    acceptor_conc: float — acceptor dopant concentration cm⁻³ (must be ≥ 0)

    Returns
    -------
    E_F : float — Fermi level relative to valence band (eV)
    """
    if E_gap_eV < 0.0:
        raise ValueError(f"E_gap_eV must be ≥ 0, got {E_gap_eV!r}")
    if T_K <= 0.0:
        raise ValueError(f"T_K must be > 0, got {T_K!r}")
    if donor_conc < 0.0:
        raise ValueError(f"donor_conc must be ≥ 0, got {donor_conc!r}")
    if acceptor_conc < 0.0:
        raise ValueError(f"acceptor_conc must be ≥ 0, got {acceptor_conc!r}")
    kT = _k_B * T_K
    ratio = (donor_conc + _EPS) / (acceptor_conc + _EPS)
    return float(E_gap_eV / 2.0 + (kT / 2.0) * math.log(ratio))


def phonon_phi_scattering(mobility_0: float, T_K: float,
                           T_ref: float = 300.0, alpha: float = 1.5) -> float:
    """Phonon-limited carrier mobility via power-law temperature dependence.

    μ(T) = μ_0 × (T_ref / T)^alpha

    Parameters
    ----------
    mobility_0 : float — mobility at T_ref in cm² V⁻¹ s⁻¹ (must be > 0)
    T_K        : float — temperature K (must be > 0)
    T_ref      : float — reference temperature K (default 300, must be > 0)
    alpha      : float — scattering exponent (default 1.5)

    Returns
    -------
    mu : float — phonon-limited mobility
    """
    if mobility_0 <= 0.0:
        raise ValueError(f"mobility_0 must be > 0, got {mobility_0!r}")
    if T_K <= 0.0:
        raise ValueError(f"T_K must be > 0, got {T_K!r}")
    if T_ref <= 0.0:
        raise ValueError(f"T_ref must be > 0, got {T_ref!r}")
    return float(mobility_0 * (T_ref / T_K) ** alpha)


def electron_phi_mobility(mu_phonon: float, mu_impurity: float) -> float:
    """Matthiessen's rule: combined scattering-limited mobility.

    1/μ = 1/μ_phonon + 1/μ_impurity

    Parameters
    ----------
    mu_phonon  : float — phonon-limited mobility (must be > 0)
    mu_impurity: float — impurity-limited mobility (must be > 0)

    Returns
    -------
    mu : float — effective carrier mobility
    """
    if mu_phonon <= 0.0:
        raise ValueError(f"mu_phonon must be > 0, got {mu_phonon!r}")
    if mu_impurity <= 0.0:
        raise ValueError(f"mu_impurity must be > 0, got {mu_impurity!r}")
    return float(1.0 / (1.0 / mu_phonon + 1.0 / mu_impurity))


def thermal_phi_conductivity(kappa_0: float, T_K: float,
                              T_ref: float = 300.0, beta: float = 1.0) -> float:
    """Thermal conductivity φ with Umklapp phonon scattering.

    κ(T) = κ_0 × (T_ref / T)^beta

    Parameters
    ----------
    kappa_0 : float — thermal conductivity at T_ref W m⁻¹ K⁻¹ (must be > 0)
    T_K     : float — temperature K (must be > 0)
    T_ref   : float — reference temperature K (default 300, must be > 0)
    beta    : float — Umklapp exponent (default 1.0)

    Returns
    -------
    kappa : float
    """
    if kappa_0 <= 0.0:
        raise ValueError(f"kappa_0 must be > 0, got {kappa_0!r}")
    if T_K <= 0.0:
        raise ValueError(f"T_K must be > 0, got {T_K!r}")
    if T_ref <= 0.0:
        raise ValueError(f"T_ref must be > 0, got {T_ref!r}")
    return float(kappa_0 * (T_ref / T_K) ** beta)


def magnetic_phi_ordering(T_K: float, T_curie: float,
                           phi_0: float = 1.0) -> float:
    """Spontaneous magnetisation φ via mean-field theory.

    M(T) = phi_0 × max(0, 1 − T / T_Curie)^0.5

    Parameters
    ----------
    T_K     : float — temperature K (must be ≥ 0)
    T_curie : float — Curie temperature K (must be > 0)
    phi_0   : float — saturation magnetisation φ (default 1.0, must be ≥ 0)

    Returns
    -------
    M : float ∈ [0, phi_0]
    """
    if T_K < 0.0:
        raise ValueError(f"T_K must be ≥ 0, got {T_K!r}")
    if T_curie <= 0.0:
        raise ValueError(f"T_curie must be > 0, got {T_curie!r}")
    if phi_0 < 0.0:
        raise ValueError(f"phi_0 must be ≥ 0, got {phi_0!r}")
    return float(phi_0 * max(0.0, 1.0 - T_K / T_curie) ** 0.5)


def crystal_phi_defects(n_vacancies: int, n_interstitials: int,
                         n_sites: int) -> float:
    """Defect concentration φ relative to perfect lattice.

    defect_fraction = (n_vacancies + n_interstitials) / n_sites

    Parameters
    ----------
    n_vacancies    : int — number of vacancy defects (must be ≥ 0)
    n_interstitials: int — number of interstitial defects (must be ≥ 0)
    n_sites        : int — total lattice sites (must be > 0)

    Returns
    -------
    defect_fraction : float ∈ [0, 1]
    """
    if n_vacancies < 0:
        raise ValueError(f"n_vacancies must be ≥ 0, got {n_vacancies!r}")
    if n_interstitials < 0:
        raise ValueError(f"n_interstitials must be ≥ 0, got {n_interstitials!r}")
    if n_sites <= 0:
        raise ValueError(f"n_sites must be > 0, got {n_sites!r}")
    return float(np.clip((n_vacancies + n_interstitials) / n_sites, 0.0, 1.0))


def grain_boundary_phi(grain_size_um: float, phi_bulk: float,
                        gb_segregation: float = 0.1) -> float:
    """Effective φ at a grain boundary including segregation enhancement.

    phi_gb = phi_bulk × (1 + gb_segregation / grain_size_um)

    Parameters
    ----------
    grain_size_um    : float — mean grain size in μm (must be > 0)
    phi_bulk         : float — bulk φ property (must be ≥ 0)
    gb_segregation   : float — segregation enhancement coefficient (must be ≥ 0)

    Returns
    -------
    phi_gb : float
    """
    if grain_size_um <= 0.0:
        raise ValueError(f"grain_size_um must be > 0, got {grain_size_um!r}")
    if phi_bulk < 0.0:
        raise ValueError(f"phi_bulk must be ≥ 0, got {phi_bulk!r}")
    if gb_segregation < 0.0:
        raise ValueError(f"gb_segregation must be ≥ 0, got {gb_segregation!r}")
    return float(phi_bulk * (1.0 + gb_segregation / grain_size_um))


def dislocation_phi_density(n_dislocations: float, volume_cm3: float) -> float:
    """Dislocation density ρ in cm⁻².

    rho = n_dislocations / volume_cm3

    Parameters
    ----------
    n_dislocations : float — total dislocation length in cm (must be ≥ 0)
    volume_cm3     : float — material volume cm³ (must be > 0)

    Returns
    -------
    rho : float — cm⁻²
    """
    if n_dislocations < 0.0:
        raise ValueError(f"n_dislocations must be ≥ 0, got {n_dislocations!r}")
    if volume_cm3 <= 0.0:
        raise ValueError(f"volume_cm3 must be > 0, got {volume_cm3!r}")
    return float(n_dislocations / volume_cm3)


def phase_transition_phi(T_K: float, T_transition: float,
                          delta_phi: float) -> float:
    """φ discontinuity across a first-order phase transition.

    phi_change = delta_phi if T_K >= T_transition else 0.0

    Parameters
    ----------
    T_K          : float — current temperature K (must be ≥ 0)
    T_transition : float — transition temperature K (must be ≥ 0)
    delta_phi    : float — φ jump at transition

    Returns
    -------
    phi_change : float
    """
    if T_K < 0.0:
        raise ValueError(f"T_K must be ≥ 0, got {T_K!r}")
    if T_transition < 0.0:
        raise ValueError(f"T_transition must be ≥ 0, got {T_transition!r}")
    return float(delta_phi if T_K >= T_transition else 0.0)
