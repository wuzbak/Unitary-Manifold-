# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
recycling/thermochemical.py
============================
Chemical recovery as B_μ-field phase transitions — Pillar 16b.

In the Unitary Manifold, thermochemical recycling processes — pyrolysis,
gasification, solvolysis, thermal cracking — are not merely industrial
operations; they are B_μ-driven phase transitions in the φ landscape.

The crucial insight: mechanical recycling can never fully restore φ because
it does not surmount the depolymerization barrier; it merely reshapes the
polymer while keeping the same winding-number topology.  Chemical recycling,
by contrast, drives the system over the B_μ activation barrier back to the
monomer φ-minima, enabling genuine closed-loop recovery.

What humans get wrong
---------------------
1. Energy accounting — pyrolysis is counted as "recycling" but the manifold
   shows that unless E_in < Q_recovered, the process generates more entropy
   than it recovers.  The COP must exceed 1.
2. Yield overestimates — mixed-stream contamination raises the effective
   B_μ activation barrier, lowering actual yield below lab measurements.
3. CO₂ blindspot — the B_μ ratio of recovered φ to virgin φ directly
   predicts the relative CO₂ footprint; this ratio is almost never
   reported in industry benchmarks.

Theory summary
--------------
Pyrolysis onset temperature (B_μ phase transition):
    T_onset = E_a / (φ_chain · k_B · ln(A / k_rate_target))

Pyrolysis yield (Boltzmann weight across φ-barrier):
    Y = exp(−ΔE / (k_B T))  where  ΔE = E_a(φ_chain) − E_a(φ_monomer)

Gasification efficiency (φ-ratio of products to reactants):
    η_gas = min(φ_syngas / φ_solid, 1)

Solvolysis rate (Arrhenius with φ-solvent screening):
    k_sol = A · exp(−E_a / (φ_solvent · k_B · T))

B_μ field at solid/liquid phase boundary:
    B_boundary = sqrt(2 · (φ_solid − φ_liquid))   (φ_solid > φ_liquid)

Syngas effective φ (linear mixture):
    φ_syngas = H2_frac · φ_H2 + CO_frac · φ_CO

Thermal cracking threshold (φ-reduced barrier):
    V_eff = V_chain / φ_local

CO₂ reduction factor:
    f_CO2 = φ_recovery / φ_virgin   (lower is better for virgin production)

Chemical recycling COP:
    COP = energy_recovered / energy_in   (must be > 1 to net-reduce entropy)

Monomer purity from φ-ratio:
    purity_mono = min(φ_recovered / φ_virgin, 1)

Public API
----------
pyrolysis_onset_temperature(phi_chain, E_a, A, k_rate_target, k_B)
    T at which B_μ drives chain decomposition.

pyrolysis_yield(E_a_chain, E_a_monomer, T, k_B)
    Boltzmann weight for monomer recovery at temperature T.

gasification_efficiency(phi_solid, phi_syngas)
    η = min(φ_syngas / φ_solid, 1).

solvolysis_rate(T, phi_solvent, A, E_a, k_B)
    Arrhenius rate screened by φ_solvent.

activation_energy_chemical_recycling(H_max, phi_mean, lam)
    E_a = λ² φ² H_max² / 2.

b_field_phase_boundary(phi_solid, phi_liquid)
    B_boundary = sqrt(2 · (φ_solid − φ_liquid)).

syngas_phi(H2_fraction, CO_fraction, phi_H2, phi_CO)
    φ_syngas = H2_frac · φ_H2 + CO_frac · φ_CO.

thermal_cracking_threshold(V_chain, phi_local)
    V_eff = V_chain / φ_local.

co2_reduction_factor(phi_recovery, phi_virgin)
    f = φ_recovery / φ_virgin.

chemical_recycling_cop(energy_in, energy_recovered)
    COP = energy_recovered / energy_in.

monomer_purity(phi_recovered, phi_virgin)
    purity = min(φ_recovered / φ_virgin, 1).
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_LAM_DEFAULT: float = 1.0
_NUMERICAL_EPSILON: float = 1e-30


# ---------------------------------------------------------------------------
# Pyrolysis onset temperature
# ---------------------------------------------------------------------------

def pyrolysis_onset_temperature(
    phi_chain: float,
    E_a: float,
    A: float = 1.0,
    k_rate_target: float = 1.0,
    k_B: float = 1.0,
) -> float:
    """Temperature at which the B_μ field drives polymer chain decomposition.

    Inverting the φ-suppressed Arrhenius equation gives the onset temperature
    at which the degradation rate first reaches k_rate_target:

        T_onset = φ_chain · E_a / (k_B · ln(A / k_rate_target))

    Higher φ_chain raises T_onset — more entangled chains require more
    thermal energy to decompose, consistent with the observation that
    high-MW polymers have higher pyrolysis temperatures.

    Parameters
    ----------
    phi_chain     : float — mean φ along the polymer chain (> 0)
    E_a           : float — activation energy for chain scission (> 0)
    A             : float — pre-exponential factor (default 1, must be > k_rate_target)
    k_rate_target : float — target degradation rate (default 1, must be > 0 and < A)
    k_B           : float — Boltzmann constant (default 1, Planck units)

    Returns
    -------
    T_onset : float — onset temperature (> 0)

    Raises
    ------
    ValueError
        If phi_chain ≤ 0, E_a ≤ 0, or A ≤ k_rate_target.
    """
    if phi_chain <= 0.0:
        raise ValueError(f"phi_chain must be > 0, got {phi_chain!r}")
    if E_a <= 0.0:
        raise ValueError(f"E_a must be > 0, got {E_a!r}")
    if A <= k_rate_target:
        raise ValueError(
            f"A must be > k_rate_target; got A={A!r}, k_rate_target={k_rate_target!r}"
        )
    return float(phi_chain * E_a / (k_B * np.log(A / k_rate_target)))


# ---------------------------------------------------------------------------
# Pyrolysis yield
# ---------------------------------------------------------------------------

def pyrolysis_yield(
    E_a_chain: float,
    E_a_monomer: float,
    T: float,
    k_B: float = 1.0,
) -> float:
    """Boltzmann-weighted monomer recovery fraction at pyrolysis temperature T.

    The yield is the Boltzmann factor for the barrier difference between
    surmounting the chain barrier (E_a_chain) vs. the monomer barrier
    (E_a_monomer):

        Y = exp(−(E_a_chain − E_a_monomer) / (k_B T))

    Y = 1.0 when E_a_chain = E_a_monomer (trivial barrier — full yield).
    Y < 1 when the chain barrier exceeds the monomer barrier (partial yield).

    Parameters
    ----------
    E_a_chain   : float — activation energy for chain scission (≥ 0)
    E_a_monomer : float — activation energy at monomer state (≥ 0)
    T           : float — pyrolysis temperature (must be > 0)
    k_B         : float — Boltzmann constant (default 1)

    Returns
    -------
    Y : float — monomer yield ∈ (0, 1]

    Raises
    ------
    ValueError
        If T ≤ 0.
    """
    if T <= 0.0:
        raise ValueError(f"T must be > 0, got {T!r}")
    dE = E_a_chain - E_a_monomer
    return float(np.clip(np.exp(-dE / (k_B * T)), 0.0, 1.0))


# ---------------------------------------------------------------------------
# Gasification efficiency
# ---------------------------------------------------------------------------

def gasification_efficiency(
    phi_solid: float,
    phi_syngas: float,
) -> float:
    """Conversion efficiency of solid polymer to syngas via φ-ratio.

    The fraction of the solid's φ-content successfully transferred to the
    syngas product stream:

        η_gas = min(φ_syngas / φ_solid, 1)

    η_gas < 1 when the syngas carries less φ than the input solid (some
    information/energy is lost as char or tar).  η_gas = 1 is the ideal
    complete gasification limit.

    Parameters
    ----------
    phi_solid  : float — φ of the solid polymer feedstock (> 0)
    phi_syngas : float — φ of the syngas product stream (≥ 0)

    Returns
    -------
    eta : float — gasification efficiency ∈ [0, 1]

    Raises
    ------
    ValueError
        If phi_solid ≤ 0 or phi_syngas < 0.
    """
    if phi_solid <= 0.0:
        raise ValueError(f"phi_solid must be > 0, got {phi_solid!r}")
    if phi_syngas < 0.0:
        raise ValueError(f"phi_syngas must be ≥ 0, got {phi_syngas!r}")
    return float(np.clip(phi_syngas / phi_solid, 0.0, 1.0))


# ---------------------------------------------------------------------------
# Solvolysis rate
# ---------------------------------------------------------------------------

def solvolysis_rate(
    T: float,
    phi_solvent: float,
    A: float = 1.0,
    E_a: float = 1.0,
    k_B: float = 1.0,
) -> float:
    """Solvolysis depolymerization rate screened by the solvent's φ field.

    The solvent reduces the effective activation barrier by its φ_solvent
    value (dielectric/entropic screening of the B_μ barrier):

        k_sol = A · exp(−E_a / (φ_solvent · k_B · T))

    A more polar or structured solvent (higher φ_solvent) lowers the
    effective barrier and accelerates depolymerization — the manifold
    explanation for why catalytic solvolysis outperforms simple hydrolysis.

    Parameters
    ----------
    T           : float — temperature (must be > 0)
    phi_solvent : float — φ of the solvent (must be > 0)
    A           : float — pre-exponential factor (default 1)
    E_a         : float — bare activation energy (default 1, ≥ 0)
    k_B         : float — Boltzmann constant (default 1)

    Returns
    -------
    k_sol : float — solvolysis rate (≥ 0)

    Raises
    ------
    ValueError
        If T ≤ 0 or phi_solvent ≤ 0.
    """
    if T <= 0.0:
        raise ValueError(f"T must be > 0, got {T!r}")
    if phi_solvent <= 0.0:
        raise ValueError(f"phi_solvent must be > 0, got {phi_solvent!r}")
    return float(A * np.exp(-E_a / (phi_solvent * k_B * T)))


# ---------------------------------------------------------------------------
# Activation energy for chemical recycling
# ---------------------------------------------------------------------------

def activation_energy_chemical_recycling(
    H_max: float,
    phi_mean: float,
    lam: float = _LAM_DEFAULT,
) -> float:
    """Activation energy for the chemical recycling B_μ phase transition.

    Identical form to the bond-scission activation energy; here it represents
    the field-strength barrier that must be overcome by the chemical process
    (acid, base, solvent, heat) to break every repeat-unit bond simultaneously:

        E_a = λ² φ_mean² H_max² / 2

    Parameters
    ----------
    H_max    : float — peak B_μ field-strength magnitude (≥ 0)
    phi_mean : float — mean radion ⟨φ⟩ along the chain (> 0)
    lam      : float — KK coupling λ (default 1, must be > 0)

    Returns
    -------
    E_a : float — activation energy in Planck units (≥ 0)

    Raises
    ------
    ValueError
        If phi_mean ≤ 0 or lam ≤ 0.
    """
    if phi_mean <= 0.0:
        raise ValueError(f"phi_mean must be > 0, got {phi_mean!r}")
    if lam <= 0.0:
        raise ValueError(f"lam must be > 0, got {lam!r}")
    return float(0.5 * lam ** 2 * phi_mean ** 2 * H_max ** 2)


# ---------------------------------------------------------------------------
# B_μ field at solid/liquid phase boundary
# ---------------------------------------------------------------------------

def b_field_phase_boundary(
    phi_solid: float,
    phi_liquid: float,
) -> float:
    """B_μ field strength at the solid/liquid phase boundary during chemical recycling.

    The phase boundary is a surface of constant φ.  The B_μ field strength
    at the boundary equals the square root of twice the φ-difference:

        B_boundary = sqrt(2 · (φ_solid − φ_liquid))

    This requires φ_solid > φ_liquid (the solid has higher entanglement
    capacity than the dissolved liquid phase).  B_boundary marks the onset
    of the phase transition: beyond it the polymer dissolves.

    Parameters
    ----------
    phi_solid  : float — φ of the solid polymer phase (> phi_liquid)
    phi_liquid : float — φ of the dissolved/liquid phase (≥ 0)

    Returns
    -------
    B_boundary : float — B_μ field strength at the phase boundary (≥ 0)

    Raises
    ------
    ValueError
        If phi_solid ≤ phi_liquid.
    """
    if phi_solid <= phi_liquid:
        raise ValueError(
            f"phi_solid must be > phi_liquid; got {phi_solid!r} ≤ {phi_liquid!r}"
        )
    return float(np.sqrt(2.0 * (phi_solid - phi_liquid)))


# ---------------------------------------------------------------------------
# Syngas effective φ
# ---------------------------------------------------------------------------

def syngas_phi(
    H2_fraction: float,
    CO_fraction: float,
    phi_H2: float = 1.2,
    phi_CO: float = 0.9,
) -> float:
    """Effective φ of a syngas mixture from H₂ and CO fractions.

    The syngas stream is a linear mixture of the two principal components.
    Their φ values differ because H₂ has a higher specific entanglement
    capacity (lighter, more quantum) than CO:

        φ_syngas = H2_frac · φ_H2 + CO_frac · φ_CO

    Parameters
    ----------
    H2_fraction : float — mole fraction of H₂ (∈ [0, 1])
    CO_fraction : float — mole fraction of CO (∈ [0, 1])
    phi_H2      : float — φ of H₂ component (default 1.2)
    phi_CO      : float — φ of CO component (default 0.9)

    Returns
    -------
    phi_sg : float — effective φ of the syngas mixture (> 0)

    Raises
    ------
    ValueError
        If H2_fraction or CO_fraction is outside [0, 1] or their sum > 1.
    """
    if not (0.0 <= H2_fraction <= 1.0):
        raise ValueError(f"H2_fraction must be ∈ [0, 1], got {H2_fraction!r}")
    if not (0.0 <= CO_fraction <= 1.0):
        raise ValueError(f"CO_fraction must be ∈ [0, 1], got {CO_fraction!r}")
    if H2_fraction + CO_fraction > 1.0 + 1e-9:
        raise ValueError(
            f"H2_fraction + CO_fraction must be ≤ 1; got {H2_fraction + CO_fraction!r}"
        )
    return float(H2_fraction * phi_H2 + CO_fraction * phi_CO)


# ---------------------------------------------------------------------------
# Thermal cracking threshold
# ---------------------------------------------------------------------------

def thermal_cracking_threshold(
    V_chain: float,
    phi_local: float,
) -> float:
    """Effective barrier height for thermal cracking, reduced by local φ.

    The local entanglement-capacity scalar screens the backbone bond
    potential, lowering the effective cracking barrier:

        V_eff = V_chain / φ_local

    Regions of high φ_local (near crystalline domains, cross-links) have
    lower V_eff and crack first — explaining why semi-crystalline polymers
    often fracture at spherulite boundaries during pyrolysis.

    Parameters
    ----------
    V_chain    : float — bare chain bond potential (> 0)
    phi_local  : float — local φ at the crack site (> 0)

    Returns
    -------
    V_eff : float — effective cracking barrier (> 0)

    Raises
    ------
    ValueError
        If V_chain ≤ 0 or phi_local ≤ 0.
    """
    if V_chain <= 0.0:
        raise ValueError(f"V_chain must be > 0, got {V_chain!r}")
    if phi_local <= 0.0:
        raise ValueError(f"phi_local must be > 0, got {phi_local!r}")
    return float(V_chain / phi_local)


# ---------------------------------------------------------------------------
# CO₂ reduction factor
# ---------------------------------------------------------------------------

def co2_reduction_factor(
    phi_recovery: float,
    phi_virgin: float,
) -> float:
    """Relative CO₂ emission factor: chemical recycling vs. virgin production.

    The B_μ field work required to produce a material is proportional to φ.
    Chemical recycling that recovers φ_recovery from a stream that required
    φ_virgin to produce has a relative CO₂ factor:

        f_CO2 = 1 − φ_recovery / φ_virgin

    f_CO2 = 0 → perfect closed-loop (no extra CO₂ vs. a hypothetical
    100 % recovery baseline).  f_CO2 = 1 → total loss (virgin production
    required from scratch).

    Parameters
    ----------
    phi_recovery : float — φ of the chemically recovered material (≥ 0)
    phi_virgin   : float — φ of the equivalent virgin material (> 0)

    Returns
    -------
    f_CO2 : float — relative CO₂ factor ∈ [0, 1]

    Raises
    ------
    ValueError
        If phi_virgin ≤ 0 or phi_recovery < 0.
    """
    if phi_virgin <= 0.0:
        raise ValueError(f"phi_virgin must be > 0, got {phi_virgin!r}")
    if phi_recovery < 0.0:
        raise ValueError(f"phi_recovery must be ≥ 0, got {phi_recovery!r}")
    return float(np.clip(1.0 - phi_recovery / phi_virgin, 0.0, 1.0))


# ---------------------------------------------------------------------------
# Chemical recycling COP
# ---------------------------------------------------------------------------

def chemical_recycling_cop(
    energy_in: float,
    energy_recovered: float,
) -> float:
    """Coefficient of performance for a chemical recycling process.

    The manifold criterion for a net-entropy-reducing process is COP > 1:

        COP = energy_recovered / energy_in

    COP ≤ 1 means the process consumes more energy than it recovers and
    therefore increases the total entropy of the universe — it is
    thermodynamically indistinguishable from incineration with extra steps.
    COP > 1 is the minimum requirement for genuine recycling in the
    manifold framework.

    Parameters
    ----------
    energy_in        : float — total energy input to the process (> 0)
    energy_recovered : float — energy/material value recovered (≥ 0)

    Returns
    -------
    cop : float — coefficient of performance (≥ 0)

    Raises
    ------
    ValueError
        If energy_in ≤ 0 or energy_recovered < 0.
    """
    if energy_in <= 0.0:
        raise ValueError(f"energy_in must be > 0, got {energy_in!r}")
    if energy_recovered < 0.0:
        raise ValueError(f"energy_recovered must be ≥ 0, got {energy_recovered!r}")
    return float(energy_recovered / energy_in)


# ---------------------------------------------------------------------------
# Monomer purity
# ---------------------------------------------------------------------------

def monomer_purity(
    phi_recovered: float,
    phi_virgin: float,
) -> float:
    """Monomer purity estimated from the φ-ratio of recovered to virgin.

    A perfectly pure monomer stream has φ_recovered = φ_virgin, giving
    purity = 1.0.  Contamination or incomplete depolymerization lowers φ
    and hence purity:

        purity = min(φ_recovered / φ_virgin, 1)

    Parameters
    ----------
    phi_recovered : float — φ of the recovered monomer stream (≥ 0)
    phi_virgin    : float — φ of the virgin monomer reference (> 0)

    Returns
    -------
    purity : float — monomer purity ∈ [0, 1]

    Raises
    ------
    ValueError
        If phi_virgin ≤ 0 or phi_recovered < 0.
    """
    if phi_virgin <= 0.0:
        raise ValueError(f"phi_virgin must be > 0, got {phi_virgin!r}")
    if phi_recovered < 0.0:
        raise ValueError(f"phi_recovered must be ≥ 0, got {phi_recovered!r}")
    return float(np.clip(phi_recovered / phi_virgin, 0.0, 1.0))
