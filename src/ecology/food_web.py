# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/ecology/food_web.py
========================
Food Webs as φ-Field Flow Networks — Pillar 21.
"""

from __future__ import annotations
import numpy as np

_EPS = 1e-30


def predator_prey_phi(phi_prey: float, phi_predator: float,
                       attack_rate: float) -> float:
    """φ consumed by predator per unit time (Holling type I).

    J_pred = attack_rate × φ_prey × φ_predator

    Parameters
    ----------
    phi_prey    : float — prey φ density (must be ≥ 0)
    phi_predator: float — predator φ density (must be ≥ 0)
    attack_rate : float — attack rate coefficient (must be ≥ 0)

    Returns
    -------
    J_pred : float — predation φ flux
    """
    if phi_prey < 0.0:
        raise ValueError(f"phi_prey must be ≥ 0, got {phi_prey!r}")
    if phi_predator < 0.0:
        raise ValueError(f"phi_predator must be ≥ 0, got {phi_predator!r}")
    if attack_rate < 0.0:
        raise ValueError(f"attack_rate must be ≥ 0, got {attack_rate!r}")
    return float(attack_rate * phi_prey * phi_predator)


def food_web_connectivity_phi(n_links: int, n_species: int) -> float:
    """Connectance of a food web.

    C = n_links / n_species²

    Parameters
    ----------
    n_links   : int — number of trophic links (must be ≥ 0)
    n_species : int — number of species (must be ≥ 1)

    Returns
    -------
    C : float ∈ [0, 1]
    """
    if n_links < 0:
        raise ValueError(f"n_links must be ≥ 0, got {n_links!r}")
    if n_species < 1:
        raise ValueError(f"n_species must be ≥ 1, got {n_species!r}")
    return float(np.clip(n_links / n_species ** 2, 0.0, 1.0))


def trophic_cascade_phi(phi_apex: float, n_levels: int,
                         amplification: float = 2.0) -> float:
    """φ-amplification of a trophic cascade from apex to base.

    φ_base = φ_apex × amplification^n_levels

    Parameters
    ----------
    phi_apex     : float — apex predator φ change (can be negative)
    n_levels     : int   — number of trophic levels (must be ≥ 0)
    amplification: float — cascade amplification factor (must be > 0)

    Returns
    -------
    phi_base : float — induced φ change at base trophic level
    """
    if n_levels < 0:
        raise ValueError(f"n_levels must be ≥ 0, got {n_levels!r}")
    if amplification <= 0.0:
        raise ValueError(f"amplification must be > 0, got {amplification!r}")
    return float(phi_apex * amplification ** n_levels)


def biomass_pyramid_phi(phi_primary: float, n_trophic: int,
                         efficiency: float = 0.1) -> float:
    """φ at the n-th trophic level (10% rule).

    φ_n = φ_primary × ε^(n−1)   for n ≥ 1

    Parameters
    ----------
    phi_primary : float — primary productivity φ (must be ≥ 0)
    n_trophic   : int   — trophic level (must be ≥ 1)
    efficiency  : float — trophic efficiency (default 0.1, must be in (0,1])

    Returns
    -------
    phi_n : float
    """
    if phi_primary < 0.0:
        raise ValueError(f"phi_primary must be ≥ 0, got {phi_primary!r}")
    if n_trophic < 1:
        raise ValueError(f"n_trophic must be ≥ 1, got {n_trophic!r}")
    if not (0.0 < efficiency <= 1.0):
        raise ValueError(f"efficiency must be in (0,1], got {efficiency!r}")
    return float(phi_primary * efficiency ** (n_trophic - 1))


def energy_phi_loss_per_trophic(phi_in: float, efficiency: float = 0.1) -> float:
    """φ dissipated at a trophic level as heat and respiration.

    loss = φ_in × (1 − efficiency)

    Parameters
    ----------
    phi_in     : float — φ entering the trophic level (must be ≥ 0)
    efficiency : float — transfer efficiency (must be in (0,1])

    Returns
    -------
    loss : float
    """
    if phi_in < 0.0:
        raise ValueError(f"phi_in must be ≥ 0, got {phi_in!r}")
    if not (0.0 < efficiency <= 1.0):
        raise ValueError(f"efficiency must be in (0,1], got {efficiency!r}")
    return float(phi_in * (1.0 - efficiency))


def apex_predator_phi(phi_ecosystem: float, apex_fraction: float) -> float:
    """φ-budget controlled by the apex predator.

    φ_apex = apex_fraction × φ_ecosystem

    Parameters
    ----------
    phi_ecosystem : float — total ecosystem φ (must be ≥ 0)
    apex_fraction : float — apex predator φ fraction ∈ [0, 1]

    Returns
    -------
    phi_apex : float
    """
    if phi_ecosystem < 0.0:
        raise ValueError(f"phi_ecosystem must be ≥ 0, got {phi_ecosystem!r}")
    if not (0.0 <= apex_fraction <= 1.0):
        raise ValueError(f"apex_fraction must be in [0,1], got {apex_fraction!r}")
    return float(phi_ecosystem * apex_fraction)


def decomposer_phi_flux(phi_dead_biomass: float, decomposition_rate: float) -> float:
    """φ released by decomposers per unit time.

    J_decomp = decomposition_rate × φ_dead_biomass

    Parameters
    ----------
    phi_dead_biomass    : float — dead organic φ pool (must be ≥ 0)
    decomposition_rate  : float — first-order decomp rate (must be ≥ 0)

    Returns
    -------
    J_decomp : float
    """
    if phi_dead_biomass < 0.0:
        raise ValueError(f"phi_dead_biomass must be ≥ 0, got {phi_dead_biomass!r}")
    if decomposition_rate < 0.0:
        raise ValueError(f"decomposition_rate must be ≥ 0, got {decomposition_rate!r}")
    return float(decomposition_rate * phi_dead_biomass)


def carbon_phi_sequestration_eco(phi_net_primary: float, phi_respiration: float) -> float:
    """Net ecosystem carbon φ sequestration.

    NEP = φ_net_primary − φ_respiration

    Parameters
    ----------
    phi_net_primary : float — net primary productivity φ (must be ≥ 0)
    phi_respiration : float — ecosystem respiration φ (must be ≥ 0)

    Returns
    -------
    NEP : float — net ecosystem production (positive = carbon sink)
    """
    if phi_net_primary < 0.0:
        raise ValueError(f"phi_net_primary must be ≥ 0, got {phi_net_primary!r}")
    if phi_respiration < 0.0:
        raise ValueError(f"phi_respiration must be ≥ 0, got {phi_respiration!r}")
    return float(phi_net_primary - phi_respiration)


def food_web_resilience_phi(phi_stable: float, phi_perturbed: float,
                             t_return: float) -> float:
    """Resilience of food web: rate of φ return after perturbation.

    R = |φ_stable − φ_perturbed| / t_return

    Parameters
    ----------
    phi_stable    : float — equilibrium φ (must be ≥ 0)
    phi_perturbed : float — post-perturbation φ (must be ≥ 0)
    t_return      : float — return time (must be > 0)

    Returns
    -------
    R : float — resilience rate
    """
    if phi_stable < 0.0:
        raise ValueError(f"phi_stable must be ≥ 0, got {phi_stable!r}")
    if phi_perturbed < 0.0:
        raise ValueError(f"phi_perturbed must be ≥ 0, got {phi_perturbed!r}")
    if t_return <= 0.0:
        raise ValueError(f"t_return must be > 0, got {t_return!r}")
    return float(abs(phi_stable - phi_perturbed) / t_return)


def interspecific_competition_phi(phi_A: float, phi_B: float,
                                   alpha_AB: float) -> float:
    """Competitive effect of species B on species A's φ-growth.

    delta_phi_A = −alpha_AB × phi_B

    Parameters
    ----------
    phi_A    : float — species A's φ (unused in formula but validated)
    phi_B    : float — species B's φ (must be ≥ 0)
    alpha_AB : float — competition coefficient B→A (must be ≥ 0)

    Returns
    -------
    delta : float — competitive suppression of A (≤ 0)
    """
    if phi_A < 0.0:
        raise ValueError(f"phi_A must be ≥ 0, got {phi_A!r}")
    if phi_B < 0.0:
        raise ValueError(f"phi_B must be ≥ 0, got {phi_B!r}")
    if alpha_AB < 0.0:
        raise ValueError(f"alpha_AB must be ≥ 0, got {alpha_AB!r}")
    return float(-alpha_AB * phi_B)
