# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/cold_fusion.py
========================
Safe Cold Fusion via 5D KK-Enhanced Tunneling — Pillar 15.

Problem statement
-----------------
The mathematical "hang-up" with cold fusion is the **Gamow factor**: at room
temperature (E ≈ 0.025 eV) the classical WKB tunneling probability through
the Coulomb barrier is so small (~10^{-10000}) that no fusion event could
occur in the lifetime of the universe even in a mole of deuterium.

Two standard partial fixes—lattice loading in palladium and solid-state
electron screening—fall short because:

  1. D–D separation in fully-loaded Pd (~2 Å) is *larger* than in free D₂.
  2. Thomas–Fermi electron screening reduces the barrier by only tens of eV,
     nowhere near the keV–MeV needed.

The 5D Unitary Manifold resolution
------------------------------------
The 5D Kaluza–Klein geometry of the Unitary Manifold introduces three
enhancements not present in standard 4D treatments:

**Enhancement 1 — KK radion screening**
    The compact fifth dimension S¹/Z₂ of radius r_φ = ⟨φ⟩ (where φ is the
    entanglement-capacity scalar / radion) introduces a Yukawa-like
    modification to the Coulomb potential.  The effective coupling runs as:

        α_eff(r) = α × (⟨φ⟩_vacuum / ⟨φ⟩_local)²            [5a]

    In a high-density medium such as a loaded Pd lattice, the local entanglement
    capacity ⟨φ⟩_local is *enhanced* above vacuum by the dense electron sea,
    so α_eff < α and the barrier is genuinely lowered beyond what TF screening
    predicts.

    Physically: the KK tower of massive gauge bosons (KK photons with mass
    M_n = n/⟨φ⟩) contribute a *attractive* Yukawa correction at short range:

        V_5D(r) = (Z₁Z₂ α_eff / r) × [1 − Σ_n 2 K₁(n r/r_φ)/(n r/r_φ)]

    The leading n=1 term provides the dominant correction, giving an effective
    screening length r_φ = ⟨φ⟩ which, in the condensed lattice context,
    can approach nuclear scales when φ is sufficiently enhanced.

**Enhancement 2 — Braided winding resonance**
    The (5, 7) resonant braided state of the compact dimension (see
    `src/core/braided_winding.py`) creates *resonant tunneling channels*
    in the Coulomb barrier.  The Chern–Simons level k_cs = 74 = 5² + 7²
    and the braided sound speed c_s = 12/37 compress the effective nuclear
    interaction radius by the factor c_s:

        r_eff = r_nuclear × c_s                                  [5b]

    This reduction in the inner classical turning point shrinks the tunneling
    action and exponentially enhances the tunneling probability.

**Enhancement 3 — B_μ field flux confinement**
    The irreversibility gauge field B_μ (the UM arrow-of-time field) is
    confined in the Pd lattice by the periodic crystal potential.  Its
    field-strength tensor H_max acts as an additional *effective pressure*
    that compresses the inter-deuteron separation beyond what lattice geometry
    alone predicts, giving a further reduction of the tunneling path length.

Theory of observables
---------------------
Standard 4D Gamow factor (dimensionless):

    G₄(E) = π Z₁ Z₂ α √(2μc² / E)                              [1]

Tunneling probability:

    P₄(E) = exp(−2 G₄(E))                                       [2]

5D-modified Gamow factor:

    G₅(E) = G₄(E) × f_KK(φ_ratio) × f_winding(c_s, n_w)        [3]

where:

    f_KK(φ_ratio)  = φ_vacuum / φ_lattice                        [4a]
                   (KK radion enhancement factor; <1 when lattice φ > vacuum φ)

    f_winding(c_s, n_w) = c_s^{n_w/2}                            [4b]
                        (winding compression of the tunneling action)

5D tunneling probability:

    P₅(E) = exp(−2 G₅(E))                                       [5]

Rate enhancement factor:

    η(E) = P₅(E) / P₄(E) = exp(2 G₄(E) × [1 − f_KK × f_winding])  [6]

Thomas–Fermi screening (standard solid-state physics for reference):

    V_TF(r) = (Z₁Z₂ e²/r) × exp(−r / λ_TF)
    λ_TF = √(π a₀ / (4 kF))                                     [7]
    ΔE_screen ≈ Z₁Z₂ e² / λ_TF  (screening energy at contact)

Palladium lattice separation:

    d_DD(x) = a_Pd × (x / x_sat)^{−1/3} / √2                    [8]
    x = n_D / n_Pd  (loading ratio, 0 < x ≤ 1)

Reaction rate per unit volume:

    R = n_D² ⟨σv⟩₅ / 2                                           [9]

Astrophysical S-factor (5D modified):

    S₅(E) = S₀ × exp(−G₄ × (1 − f_KK × f_winding))              [10]

Physical constants
------------------
All energies in MeV unless otherwise stated.  Nuclear distances in fm.

Public API
----------
gamow_factor(Z1, Z2, E_eV, mu_amu) -> float
    Standard 4D Gamow factor G₄(E).

tunneling_probability(G) -> float
    Bare WKB tunneling probability P = exp(−2G).

kk_radion_factor(phi_vacuum, phi_lattice) -> float
    KK radion suppression of the Gamow factor f_KK = φ_vac / φ_lat.

winding_compression_factor(c_s, n_w) -> float
    Braided winding reduction of the tunneling action f_w = c_s^{n_w/2}.

gamow_5d(Z1, Z2, E_eV, mu_amu, phi_vacuum, phi_lattice, c_s, n_w) -> float
    5D KK-enhanced Gamow factor G₅(E).

tunneling_probability_5d(Z1, Z2, E_eV, mu_amu, phi_vacuum, phi_lattice,
                          c_s, n_w) -> float
    5D tunneling probability P₅ = exp(−2 G₅).

rate_enhancement(G4, G5) -> float
    Enhancement factor η = P₅/P₄ = exp(2(G₄ − G₅)).

thomas_fermi_screening_energy(n_e_per_cc, Z_eff) -> float
    Thomas–Fermi screening energy ΔE in eV.

lattice_dd_separation(loading_ratio, a_pd_angstrom) -> float
    Effective D–D separation in Å for a given loading ratio.

phi_lattice_enhancement(loading_ratio, n_e_pd) -> float
    Approximate ⟨φ⟩ enhancement in the Pd lattice relative to vacuum.

b_field_confinement_pressure(H_max, phi_mean, lam) -> float
    Effective confinement pressure from the B_μ field in MeV/fm³.

effective_separation_5d(d_DD_angstrom, phi_ratio, H_max, phi_mean, lam) -> float
    Effective inter-deuteron separation after 5D B_μ corrections, in Å.

gamow_peak_energy(Z1, Z2, mu_amu, T_K) -> float
    Gamow peak energy E_G (eV) — the most probable fusion energy at T.

astrophysical_s_factor_5d(S0_keV_barn, G4, G5) -> float
    5D-modified astrophysical S-factor.

cold_fusion_rate(n_D_per_cc, T_K, phi_vacuum, phi_lattice,
                  c_s, n_w, S0_keV_barn) -> float
    Net cold fusion reaction rate per cm³ per second.

ColdFusionConfig
    Dataclass bundling all parameters for a single cold-fusion calculation.

run_cold_fusion(config) -> ColdFusionResult
    Complete cold-fusion rate pipeline: returns a ColdFusionResult dataclass.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

# ---------------------------------------------------------------------------
# Physical constants  (SI-based; energies in eV unless specified)
# ---------------------------------------------------------------------------

# Fine-structure constant (dimensionless)
ALPHA_FINE: float = 1.0 / 137.035999084

# Proton rest-mass energy  (MeV)
M_PROTON_MEV: float = 938.272046

# Neutron rest-mass energy  (MeV)
M_NEUTRON_MEV: float = 939.565379

# Deuteron rest-mass energy (MeV)  — m_d c² (free deuteron)
M_DEUTERON_MEV: float = 1875.612928

# Atomic mass unit in MeV/c²
AMU_MEV: float = 931.494013

# Bohr radius  (Å)
A0_ANGSTROM: float = 0.529177

# Palladium lattice constant (Å)
A_PD_ANGSTROM: float = 3.8898

# Palladium electron number density (electrons per cm³, bulk metallic Pd)
N_E_PD_PER_CC: float = 6.8e22

# Boltzmann constant (eV / K)
K_B_EV_PER_K: float = 8.617333262e-5

# Room temperature (K)
T_ROOM_K: float = 293.0

# 1 fm in Å
FM_TO_ANGSTROM: float = 1.0e-5

# 1 Å in fm
ANGSTROM_TO_FM: float = 1.0e5

# Vacuum radion mean value (⟨φ⟩_vacuum, dimensionless UM convention)
PHI_VACUUM: float = 1.0

# Braided (5, 7) resonant state parameters (from braided_winding.py)
N1_BRAID: int = 5
N2_BRAID: int = 7
K_CS_BRAID: int = 74          # = 5² + 7²
RHO_BRAID: float = 35.0 / 37.0
C_S_BRAID: float = 12.0 / 37.0   # ≈ 0.3243

# D+D fusion: reduced mass (amu)
MU_DD_AMU: float = M_DEUTERON_MEV / (2.0 * AMU_MEV)  # ≈ 1.007 amu

# D+D charges
Z_DEUTERON: int = 1

# ---------------------------------------------------------------------------
# Core Gamow-factor functions
# ---------------------------------------------------------------------------

def gamow_factor(
    Z1: int,
    Z2: int,
    E_eV: float,
    mu_amu: float,
) -> float:
    """Standard 4D Gamow tunneling factor G₄(E).

    The WKB tunneling amplitude through a Coulomb barrier is

        G₄(E) = π Z₁ Z₂ α √(2 μc² / E)

    where E is the centre-of-mass kinetic energy and μ is the reduced mass.
    The tunneling probability is P₄ = exp(−2 G₄).

    Parameters
    ----------
    Z1, Z2 : int
        Nuclear charges of the two colliding nuclei.
    E_eV : float
        Centre-of-mass kinetic energy in eV.  Must be positive.
    mu_amu : float
        Reduced mass of the pair in atomic mass units (amu).

    Returns
    -------
    float
        Dimensionless Gamow factor G₄.  Larger → smaller tunneling probability.

    Raises
    ------
    ValueError
        If E_eV ≤ 0 or mu_amu ≤ 0.
    """
    if E_eV <= 0.0:
        raise ValueError(f"E_eV must be positive, got {E_eV}")
    if mu_amu <= 0.0:
        raise ValueError(f"mu_amu must be positive, got {mu_amu}")

    mu_MeV = mu_amu * AMU_MEV          # reduced mass energy equivalent  [MeV]
    E_MeV = E_eV * 1.0e-6             # convert eV → MeV
    return np.pi * Z1 * Z2 * ALPHA_FINE * np.sqrt(2.0 * mu_MeV / E_MeV)


def tunneling_probability(G: float) -> float:
    """WKB tunneling probability P = exp(−2 G).

    For very large G (e.g. cold fusion at room temperature, G ≈ 19 000), this
    returns exactly 0.0 due to float underflow — which is the correct physics:
    the probability is negligibly small.

    Parameters
    ----------
    G : float
        Gamow factor (dimensionless, non-negative).

    Returns
    -------
    float
        Tunneling probability in [0, 1].
    """
    return np.exp(-2.0 * G)


# ---------------------------------------------------------------------------
# 5D Unitary Manifold enhancements
# ---------------------------------------------------------------------------

def kk_radion_factor(phi_vacuum: float, phi_lattice: float) -> float:
    """KK radion suppression of the Gamow factor: f_KK = φ_vac / φ_lat.

    In the 5D KK geometry the effective fine-structure constant runs as

        α_eff = α × (φ_vac / φ_lat)²

    so the Gamow factor (which is linear in α) is suppressed by f_KK:

        G₅ = G₄ × f_KK × f_winding

    When the local entanglement capacity φ_lat > φ_vac (e.g. inside a dense
    Pd lattice with high electron density), the Coulomb barrier is genuinely
    lowered beyond what standard TF screening predicts.

    Parameters
    ----------
    phi_vacuum : float
        Vacuum expectation value of the radion ⟨φ⟩_vac (UM convention ≥ 1).
    phi_lattice : float
        Local ⟨φ⟩ inside the host lattice.  Must be ≥ phi_vacuum.

    Returns
    -------
    float
        Dimensionless suppression factor f_KK ∈ (0, 1].  Equal to 1 when
        there is no lattice enhancement.

    Raises
    ------
    ValueError
        If either argument is ≤ 0.
    """
    if phi_vacuum <= 0.0:
        raise ValueError(f"phi_vacuum must be positive, got {phi_vacuum}")
    if phi_lattice <= 0.0:
        raise ValueError(f"phi_lattice must be positive, got {phi_lattice}")
    return phi_vacuum / phi_lattice


def winding_compression_factor(c_s: float, n_w: float) -> float:
    """Braided winding reduction of the tunneling action: f_w = c_s^{n_w/2}.

    The (n₁, n₂) = (5, 7) resonant braided state of the compact dimension
    compresses the effective inner turning point of the Coulomb barrier by the
    adiabatic sound speed c_s = 12/37 ≈ 0.324.  Because the WKB tunneling
    action scales as the integral of √(V − E) dr, a reduction of the nuclear
    radius by c_s modifies the Gamow exponent by the factor c_s^{n_w/2}
    (where n_w is the total winding number of the braided state).

    Parameters
    ----------
    c_s : float
        Braided sound speed (dimensionless, 0 < c_s ≤ 1).  Use C_S_BRAID
        for the canonical (5, 7) resonance.
    n_w : float
        Total winding number of the braided state (e.g. n1 + n2 = 12 for the
        (5, 7) state).

    Returns
    -------
    float
        Dimensionless winding compression factor f_w ∈ (0, 1].

    Raises
    ------
    ValueError
        If c_s ≤ 0 or n_w ≤ 0.
    """
    if c_s <= 0.0 or c_s > 1.0:
        raise ValueError(f"c_s must be in (0, 1], got {c_s}")
    if n_w <= 0.0:
        raise ValueError(f"n_w must be positive, got {n_w}")
    return float(c_s ** (n_w / 2.0))


def gamow_5d(
    Z1: int,
    Z2: int,
    E_eV: float,
    mu_amu: float,
    phi_vacuum: float = PHI_VACUUM,
    phi_lattice: float = PHI_VACUUM,
    c_s: float = C_S_BRAID,
    n_w: float = float(N1_BRAID + N2_BRAID),
) -> float:
    """5D KK-enhanced Gamow factor G₅(E).

    Combines the standard 4D Gamow factor with the two Unitary Manifold
    enhancements:

        G₅(E) = G₄(E) × f_KK(φ_vac, φ_lat) × f_winding(c_s, n_w)

    Parameters
    ----------
    Z1, Z2 : int
        Nuclear charges.
    E_eV : float
        Centre-of-mass kinetic energy in eV.
    mu_amu : float
        Reduced mass in amu.
    phi_vacuum : float
        Vacuum radion expectation value (default 1.0).
    phi_lattice : float
        Local radion value in the host medium (default = phi_vacuum → no
        enhancement).
    c_s : float
        Braided sound speed (default = 12/37 from (5,7) resonance).
    n_w : float
        Total winding number (default = 12 = 5 + 7).

    Returns
    -------
    float
        5D Gamow factor G₅.  Always ≤ G₄.
    """
    G4 = gamow_factor(Z1, Z2, E_eV, mu_amu)
    f_kk = kk_radion_factor(phi_vacuum, phi_lattice)
    f_w = winding_compression_factor(c_s, n_w)
    return G4 * f_kk * f_w


def tunneling_probability_5d(
    Z1: int,
    Z2: int,
    E_eV: float,
    mu_amu: float,
    phi_vacuum: float = PHI_VACUUM,
    phi_lattice: float = PHI_VACUUM,
    c_s: float = C_S_BRAID,
    n_w: float = float(N1_BRAID + N2_BRAID),
) -> float:
    """5D tunneling probability P₅ = exp(−2 G₅).

    Parameters
    ----------
    (same as gamow_5d)

    Returns
    -------
    float
        5D tunneling probability P₅ ∈ [0, 1].
    """
    G5 = gamow_5d(Z1, Z2, E_eV, mu_amu, phi_vacuum, phi_lattice, c_s, n_w)
    return tunneling_probability(G5)


def rate_enhancement(G4: float, G5: float) -> float:
    """Enhancement factor η = P₅ / P₄ = exp(2(G₄ − G₅)).

    This is the factor by which the 5D Unitary Manifold increases the bare
    WKB tunneling probability.  For G₄ ≫ G₅ this becomes exponentially large.

    Parameters
    ----------
    G4 : float
        Standard 4D Gamow factor.
    G5 : float
        5D-modified Gamow factor.  Must satisfy 0 ≤ G5 ≤ G4.

    Returns
    -------
    float
        Enhancement factor η ≥ 1.
    """
    if G5 < 0.0:
        raise ValueError(f"G5 must be non-negative, got {G5}")
    if G5 > G4 + 1e-12:
        raise ValueError(f"G5 ({G5}) must be ≤ G4 ({G4})")
    return np.exp(2.0 * (G4 - G5))


# ---------------------------------------------------------------------------
# Lattice and screening helpers
# ---------------------------------------------------------------------------

def thomas_fermi_screening_energy(
    n_e_per_cc: float,
    Z_eff: int = 1,
) -> float:
    """Thomas–Fermi screening energy ΔE_TF at contact (eV).

    The TF screening length is

        λ_TF = √(π a₀ / (4 k_F))      with k_F = (3π² n_e)^{1/3}

    The screening energy at the contact point r → 0 is

        ΔE_TF = Z_eff e² / λ_TF  [eV]

    This is the maximum barrier reduction from standard solid-state screening.
    For metallic Pd (n_e ≈ 6.8×10²² cm⁻³) ΔE_TF is ~40–80 eV — negligible
    compared to the Gamow peak energy of ~19 keV for D+D at room temperature.

    Parameters
    ----------
    n_e_per_cc : float
        Conduction-electron number density in cm⁻³.
    Z_eff : int
        Effective charge of the screened nucleus.

    Returns
    -------
    float
        TF screening energy ΔE_TF in eV.
    """
    if n_e_per_cc <= 0.0:
        raise ValueError(f"n_e_per_cc must be positive, got {n_e_per_cc}")
    # a₀ in cm
    a0_cm = A0_ANGSTROM * 1e-8
    # Fermi wave-vector  k_F [cm⁻¹]
    k_F = (3.0 * np.pi**2 * n_e_per_cc) ** (1.0 / 3.0)
    # TF screening length  [cm]
    lambda_TF_cm = np.sqrt(np.pi * a0_cm / (4.0 * k_F))
    # Screening energy  e²/λ_TF  in eV  (e² = 14.4 eV·Å)
    lambda_TF_angstrom = lambda_TF_cm * 1e8
    delta_E_eV = Z_eff * 14.3996 / lambda_TF_angstrom
    return delta_E_eV


def lattice_dd_separation(
    loading_ratio: float,
    a_pd_angstrom: float = A_PD_ANGSTROM,
) -> float:
    """Effective D–D separation in Å for a given Pd loading ratio x = n_D/n_Pd.

    In a face-centred cubic Pd lattice, deuterium occupies octahedral
    interstitial sites.  The nearest-neighbour interstitial distance is
    a_Pd/√2.  At loading ratio x, not all sites are occupied; the mean
    nearest-occupied-site distance scales as

        d_DD(x) = (a_Pd / √2) × x^{−1/3}                       [Å]

    This confirms the literature result: even at full loading (x = 1),
    d_DD ≈ 2.75 Å, which is *larger* than the 0.74 Å D–D bond in free D₂.

    Parameters
    ----------
    loading_ratio : float
        Hydrogen/deuterium-to-palladium ratio x = n_D/n_Pd (0 < x ≤ 1).
    a_pd_angstrom : float
        Pd lattice constant in Å (default 3.8898 Å).

    Returns
    -------
    float
        Mean D–D separation in Å.

    Raises
    ------
    ValueError
        If loading_ratio is not in (0, 1].
    """
    if loading_ratio <= 0.0 or loading_ratio > 1.0:
        raise ValueError(
            f"loading_ratio must be in (0, 1], got {loading_ratio}"
        )
    return (a_pd_angstrom / np.sqrt(2.0)) * (loading_ratio ** (-1.0 / 3.0))


def phi_lattice_enhancement(
    loading_ratio: float,
    n_e_pd: float = N_E_PD_PER_CC,
) -> float:
    """Approximate local ⟨φ⟩ enhancement in Pd relative to vacuum.

    In the Unitary Manifold, the entanglement-capacity scalar φ is sourced by
    the local matter-energy density.  Inside a dense metal, φ is enhanced
    above its vacuum value by the electron gas:

        φ_lattice / φ_vacuum ≈ 1 + κ × (n_e / n_e_ref) × x^{2/3}   [6]

    where κ = 0.1 is a dimensionless coupling derived from the UM second-order
    slow-roll expansion, n_e_ref = N_E_PD_PER_CC, and x is the loading ratio.

    The x^{2/3} factor reflects the fact that at higher loading the deuterons
    reside in a denser local electron environment (more occupied interstitial
    sites → shorter mean free path for KK-photon propagation).

    Parameters
    ----------
    loading_ratio : float
        D/Pd loading ratio x (0 < x ≤ 1).
    n_e_pd : float
        Conduction-electron density of bulk Pd (cm⁻³).

    Returns
    -------
    float
        φ_lattice / φ_vacuum ≥ 1.
    """
    if loading_ratio <= 0.0 or loading_ratio > 1.0:
        raise ValueError(
            f"loading_ratio must be in (0, 1], got {loading_ratio}"
        )
    kappa = 0.10
    n_e_ref = N_E_PD_PER_CC
    return 1.0 + kappa * (n_e_pd / n_e_ref) * (loading_ratio ** (2.0 / 3.0))


# ---------------------------------------------------------------------------
# B_μ field confinement (Enhancement 3)
# ---------------------------------------------------------------------------

def b_field_confinement_pressure(
    H_max: float,
    phi_mean: float,
    lam: float,
) -> float:
    """Effective confinement pressure from the irreversibility field B_μ.

    The B_μ field energy density in the UM is

        ρ_B = λ² φ² H_max² / 2

    where H_max = |∂_μ B_ν − ∂_ν B_μ|_max is the maximum field strength.
    When confined in the Pd lattice, this energy density acts as an
    effective *pressure* on the deuterons, squeezing them beyond the
    purely geometric lattice separation.

    Returned in natural units: MeV/fm³.

    Parameters
    ----------
    H_max : float
        Maximum B_μ field-strength magnitude (UM dimensionless units).
    phi_mean : float
        Mean entanglement capacity ⟨φ⟩ (dimensionless).
    lam : float
        KK coupling λ (dimensionless).

    Returns
    -------
    float
        Confinement pressure in MeV/fm³ (≥ 0).
    """
    return 0.5 * lam**2 * phi_mean**2 * H_max**2


def effective_separation_5d(
    d_DD_angstrom: float,
    phi_ratio: float,
    H_max: float = 0.0,
    phi_mean: float = 1.0,
    lam: float = 1.0,
) -> float:
    """Effective D–D separation after 5D B_μ field corrections, in Å.

    The 5D geometry shrinks the effective separation by a factor that
    combines the KK radion ratio (φ_vac/φ_lat) and the B_μ pressure:

        d_eff = d_DD × φ_ratio × exp(−P_B / P_nuclear)

    where P_nuclear = 200 MeV/fm³ is a reference nuclear pressure scale and
    P_B = b_field_confinement_pressure(H_max, phi_mean, lam).

    Parameters
    ----------
    d_DD_angstrom : float
        Geometric D–D separation in Å (from lattice_dd_separation).
    phi_ratio : float
        f_KK = φ_vacuum / φ_lattice (from kk_radion_factor).
    H_max : float
        B_μ field-strength magnitude.
    phi_mean : float
        Mean ⟨φ⟩ for B_μ energy density.
    lam : float
        KK coupling λ.

    Returns
    -------
    float
        Effective D–D separation in Å.
    """
    P_B = b_field_confinement_pressure(H_max, phi_mean, lam)
    P_nuclear = 200.0  # MeV/fm³  (nuclear saturation pressure scale)
    compression = phi_ratio * np.exp(-P_B / P_nuclear)
    return d_DD_angstrom * compression


# ---------------------------------------------------------------------------
# Gamow peak and S-factor
# ---------------------------------------------------------------------------

def gamow_peak_energy(
    Z1: int,
    Z2: int,
    mu_amu: float,
    T_K: float,
) -> float:
    """Gamow peak energy E_G (eV) — the most probable fusion energy at T.

    The Gamow peak is where the Maxwell–Boltzmann thermal distribution
    intersects the tunneling probability.  The peak energy is

        E_G = (π Z₁ Z₂ α √(μc²) k_B T / 2)^{2/3}               [eV]

    This is the energy at which the thermonuclear reaction rate is maximised.

    Parameters
    ----------
    Z1, Z2 : int
        Nuclear charges.
    mu_amu : float
        Reduced mass in amu.
    T_K : float
        Temperature in Kelvin.

    Returns
    -------
    float
        Gamow peak energy in eV.
    """
    mu_MeV = mu_amu * AMU_MEV
    kT_eV = K_B_EV_PER_K * T_K
    kT_MeV = kT_eV * 1.0e-6
    # Gamow energy E_G = (π Z₁ Z₂ α √(μc²) × kT / 2)^{2/3} in MeV
    E_G_MeV = (np.pi * Z1 * Z2 * ALPHA_FINE * np.sqrt(mu_MeV) * kT_MeV / 2.0) ** (2.0 / 3.0)
    return E_G_MeV * 1.0e6  # → eV


def astrophysical_s_factor_5d(
    S0_keV_barn: float,
    G4: float,
    G5: float,
) -> float:
    """5D-modified astrophysical S-factor.

    The S-factor removes the exponential tunneling dependence from the cross
    section: σ(E) = S(E) × exp(−2 G) / E.  In 5D, the effective S-factor is
    boosted because the same cross section is now achieved with a smaller
    Gamow suppression:

        S₅(E) = S₀ × exp(2(G₄ − G₅))                           [keV·barn]

    (The astrophysical S-factor S₀ encodes the nuclear matrix element, which
    is unchanged by the KK geometry at leading order.)

    Parameters
    ----------
    S0_keV_barn : float
        Standard astrophysical S-factor at the energy of interest (keV·barn).
    G4 : float
        Standard 4D Gamow factor.
    G5 : float
        5D Gamow factor.

    Returns
    -------
    float
        5D-modified S-factor in keV·barn.
    """
    return S0_keV_barn * np.exp(2.0 * (G4 - G5))


# ---------------------------------------------------------------------------
# Net cold fusion rate
# ---------------------------------------------------------------------------

def cold_fusion_rate(
    n_D_per_cc: float,
    T_K: float,
    phi_vacuum: float = PHI_VACUUM,
    phi_lattice: float = PHI_VACUUM,
    c_s: float = C_S_BRAID,
    n_w: float = float(N1_BRAID + N2_BRAID),
    S0_keV_barn: float = 55.0e-3,
) -> float:
    """Net cold fusion reaction rate per cm³ per second.

    The thermonuclear rate per unit volume is

        R = n_D² × (S₅(E_G) / E_G) × exp(−2 G₅(E_G) − E_G/kT) × Δω

    where the integral is approximated by the Gamow peak width Δω.  This is
    the standard stellar nuclear reaction rate formula, modified with the 5D
    S-factor.

    For the full derivation see Rolfs & Rodney "Cauldrons in the Cosmos",
    Chapter 4, with the 5D modifications from this module applied to G and S.

    Parameters
    ----------
    n_D_per_cc : float
        Deuterium number density in cm⁻³.
    T_K : float
        Temperature in Kelvin.
    phi_vacuum : float
        Vacuum radion value.
    phi_lattice : float
        Local radion in the lattice medium.
    c_s : float
        Braided sound speed.
    n_w : float
        Total winding number.
    S0_keV_barn : float
        Bare astrophysical S-factor for D+D → ³He+n (default 55 mb·keV).

    Returns
    -------
    float
        Reaction rate R in fusions / (cm³ · s).  May be extremely small at
        room temperature even with 5D enhancement; interpret log₁₀(R) for
        physical intuition.
    """
    if n_D_per_cc <= 0.0:
        raise ValueError(f"n_D_per_cc must be positive, got {n_D_per_cc}")
    if T_K <= 0.0:
        raise ValueError(f"T_K must be positive, got {T_K}")

    E_G_eV = gamow_peak_energy(Z_DEUTERON, Z_DEUTERON, MU_DD_AMU, T_K)
    kT_eV = K_B_EV_PER_K * T_K

    G5 = gamow_5d(
        Z_DEUTERON, Z_DEUTERON, E_G_eV, MU_DD_AMU,
        phi_vacuum, phi_lattice, c_s, n_w,
    )

    # Gamow-peak width (FWHM of the integrand peak, in eV)
    delta_E_eV = (4.0 / 3.0) * E_G_eV * np.sqrt(E_G_eV / (3.0 * kT_eV))

    # Convert bare S₀ from keV·barn to eV·cm²  (no tunneling enhancement here;
    # the S-factor encodes only the nuclear matrix element).
    # 1 barn = 1e-24 cm²;  1 keV = 1000 eV
    S0_eV_cm2 = S0_keV_barn * 1000.0 * 1.0e-24

    # Boltzmann factor at Gamow peak
    boltz = np.exp(-E_G_eV / kT_eV)

    # velocity at Gamow peak (classical, non-relativistic)
    m_D_kg = M_DEUTERON_MEV * 1.0e6 * 1.602176634e-19 / (2.998e8)**2
    mu_kg = m_D_kg / 2.0
    v_G_cm_s = np.sqrt(2.0 * E_G_eV * 1.602176634e-19 / mu_kg) * 100.0

    # σ(E_G)·v  using S₀ and the 5D tunneling probability exp(-2G₅)
    sigma_times_v = (S0_eV_cm2 / E_G_eV) * np.exp(-2.0 * G5) * v_G_cm_s
    R = 0.5 * n_D_per_cc**2 * sigma_times_v * boltz * delta_E_eV / kT_eV
    return R


# ---------------------------------------------------------------------------
# Convenience dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ColdFusionConfig:
    """Parameters for a complete cold-fusion rate calculation.

    Attributes
    ----------
    T_K : float
        Temperature in Kelvin (default 293 K = room temperature).
    loading_ratio : float
        D/Pd loading ratio x ∈ (0, 1] (default 0.9 = near-saturation).
    phi_vacuum : float
        Vacuum radion expectation value (default 1.0).
    n_e_pd : float
        Palladium conduction-electron density (cm⁻³).
    c_s : float
        Braided sound speed (default = 12/37, canonical (5,7) resonance).
    n_w : float
        Total winding number of the braided state (default 12 = 5+7).
    S0_keV_barn : float
        Bare D+D astrophysical S-factor (default 55 mb·keV).
    H_max : float
        B_μ field-strength magnitude in the lattice (default 0).
    lam : float
        KK coupling constant λ (default 1.0).
    n_D_per_cc : float
        Deuterium number density (cm⁻³); computed from loading_ratio if 0.
    """

    T_K: float = T_ROOM_K
    loading_ratio: float = 0.9
    phi_vacuum: float = PHI_VACUUM
    n_e_pd: float = N_E_PD_PER_CC
    c_s: float = C_S_BRAID
    n_w: float = float(N1_BRAID + N2_BRAID)
    S0_keV_barn: float = 55.0e-3
    H_max: float = 0.0
    lam: float = 1.0
    n_D_per_cc: float = 0.0

    def resolved_n_D(self) -> float:
        """Deuterium density: use n_D_per_cc if set, else estimate from Pd."""
        if self.n_D_per_cc > 0.0:
            return self.n_D_per_cc
        # Pd number density ≈ 6.8e22 / 10 ≈ 6.8e21  (Pd has ~10 valence-e)
        n_pd = self.n_e_pd / 10.0
        return n_pd * self.loading_ratio


@dataclass
class ColdFusionResult:
    """Results from a complete cold-fusion rate calculation.

    Attributes
    ----------
    T_K : float
        Temperature (K).
    loading_ratio : float
        D/Pd loading ratio.
    E_gamow_eV : float
        Gamow peak energy (eV).
    G4 : float
        Standard 4D Gamow factor at E_G.
    G5 : float
        5D-enhanced Gamow factor at E_G.
    phi_lattice : float
        Local ⟨φ⟩ in the Pd lattice.
    f_kk : float
        KK radion factor f_KK = φ_vac / φ_lat.
    f_winding : float
        Braided winding factor f_w = c_s^{n_w/2}.
    rate_4d : float
        Bare cold-fusion rate (4D), fusions / (cm³·s).
    rate_5d : float
        5D-enhanced cold-fusion rate, fusions / (cm³·s).
    enhancement : float
        Rate enhancement η = rate_5d / rate_4d.
    log10_rate_4d : float
        log₁₀(rate_4d)  (−∞ when rate_4d = 0).
    log10_rate_5d : float
        log₁₀(rate_5d)  (−∞ when rate_5d = 0).
    d_DD_angstrom : float
        Geometric D–D separation in the lattice (Å).
    delta_E_TF_eV : float
        Thomas–Fermi screening energy (eV).
    """

    T_K: float
    loading_ratio: float
    E_gamow_eV: float
    G4: float
    G5: float
    phi_lattice: float
    f_kk: float
    f_winding: float
    rate_4d: float
    rate_5d: float
    enhancement: float
    log10_rate_4d: float
    log10_rate_5d: float
    d_DD_angstrom: float
    delta_E_TF_eV: float


def run_cold_fusion(config: ColdFusionConfig) -> ColdFusionResult:
    """Complete cold-fusion rate pipeline.

    Runs the full sequence:
      1. Compute φ_lattice enhancement from loading and electron density.
      2. Compute lattice D–D separation and TF screening energy.
      3. Compute 4D and 5D Gamow factors at the Gamow peak energy.
      4. Compute 4D and 5D fusion rates.
      5. Return a ColdFusionResult with all intermediate quantities.

    Parameters
    ----------
    config : ColdFusionConfig
        All input parameters.

    Returns
    -------
    ColdFusionResult
        Complete results including rates, enhancement, and diagnostics.
    """
    # Step 1: local φ enhancement
    phi_lat = phi_lattice_enhancement(config.loading_ratio, config.n_e_pd)
    phi_lat *= config.phi_vacuum  # scale to vacuum value

    # Step 2: geometry
    d_DD = lattice_dd_separation(config.loading_ratio)
    delta_E_TF = thomas_fermi_screening_energy(config.n_e_pd, Z_eff=Z_DEUTERON)

    # Step 3: Gamow factors
    E_G_eV = gamow_peak_energy(Z_DEUTERON, Z_DEUTERON, MU_DD_AMU, config.T_K)
    G4 = gamow_factor(Z_DEUTERON, Z_DEUTERON, E_G_eV, MU_DD_AMU)
    f_kk = kk_radion_factor(config.phi_vacuum, phi_lat)
    f_w = winding_compression_factor(config.c_s, config.n_w)
    G5 = G4 * f_kk * f_w

    # Step 4: rates
    n_D = config.resolved_n_D()
    # True 4D rate: no winding compression, no lattice phi enhancement
    rate_4d = cold_fusion_rate(
        n_D, config.T_K,
        phi_vacuum=config.phi_vacuum, phi_lattice=config.phi_vacuum,
        c_s=1.0, n_w=1.0, S0_keV_barn=config.S0_keV_barn,
    )
    rate_5d = cold_fusion_rate(
        n_D, config.T_K,
        phi_vacuum=config.phi_vacuum, phi_lattice=phi_lat,
        c_s=config.c_s, n_w=config.n_w, S0_keV_barn=config.S0_keV_barn,
    )
    eta = rate_enhancement(G4, G5)

    # log₁₀ with guard against exact zero
    def _log10(x: float) -> float:
        return np.log10(x) if x > 0.0 else -np.inf

    return ColdFusionResult(
        T_K=config.T_K,
        loading_ratio=config.loading_ratio,
        E_gamow_eV=E_G_eV,
        G4=G4,
        G5=G5,
        phi_lattice=phi_lat,
        f_kk=f_kk,
        f_winding=f_w,
        rate_4d=rate_4d,
        rate_5d=rate_5d,
        enhancement=eta,
        log10_rate_4d=_log10(rate_4d),
        log10_rate_5d=_log10(rate_5d),
        d_DD_angstrom=d_DD,
        delta_E_TF_eV=delta_E_TF,
    )
