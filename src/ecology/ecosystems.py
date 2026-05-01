# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/ecology/ecosystems.py
==========================
Ecosystems as φ-Field Attractor Basins — Pillar 21: Ecology.

Theory
------
An ecosystem maintains a FTUM fixed-point at a characteristic
entanglement-capacity φ* — the carrying-capacity attractor.  Species
interactions, nutrient cycling, and energy flow are the mechanisms that
enforce and perturb this fixed-point.  Ecosystem collapse is modelled as
a bifurcation in which B_μ noise pushes the φ trajectory out of the
basin of attraction into a lower-φ degraded attractor.
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
import numpy as np

_EPS = 1e-30


def carrying_capacity_phi(phi_resources: float, phi_per_individual: float) -> float:
    """Maximum population supportable given available resources.

    K = φ_resources / φ_per_individual

    Parameters
    ----------
    phi_resources     : float — total resource φ available (must be > 0)
    phi_per_individual: float — φ required per individual (must be > 0)

    Returns
    -------
    K : float — carrying capacity
    """
    if phi_resources <= 0.0:
        raise ValueError(f"phi_resources must be > 0, got {phi_resources!r}")
    if phi_per_individual <= 0.0:
        raise ValueError(f"phi_per_individual must be > 0, got {phi_per_individual!r}")
    return float(phi_resources / phi_per_individual)


def ecosystem_entropy(phi_values: np.ndarray) -> float:
    """Shannon entropy of species φ-abundance distribution.

    H = −Σ p_i log(p_i)   where p_i = φ_i / Σφ_j

    Parameters
    ----------
    phi_values : ndarray — φ abundance of each species (must be ≥ 0)

    Returns
    -------
    H : float — ecosystem entropy (≥ 0)
    """
    arr = np.asarray(phi_values, dtype=float)
    if np.any(arr < 0.0):
        raise ValueError("All phi_values must be ≥ 0")
    total = arr.sum() + _EPS
    p = arr / total
    return float(-np.sum(p * np.log(p + _EPS)))


def energy_transfer_efficiency(phi_in: float, phi_out: float) -> float:
    """Trophic energy transfer efficiency as φ-flow ratio.

    ε = φ_out / φ_in  ∈ (0, 1]

    Parameters
    ----------
    phi_in  : float — φ entering a trophic level (must be > 0)
    phi_out : float — φ exiting to next level (must be ≥ 0)

    Returns
    -------
    epsilon : float ∈ (0, 1]
    """
    if phi_in <= 0.0:
        raise ValueError(f"phi_in must be > 0, got {phi_in!r}")
    if phi_out < 0.0:
        raise ValueError(f"phi_out must be ≥ 0, got {phi_out!r}")
    return float(np.clip(phi_out / phi_in, 0.0, 1.0))


def niche_phi_overlap(phi_A: np.ndarray, phi_B: np.ndarray) -> float:
    """Niche overlap between two species as normalised φ-vector cosine.

    overlap = (φ_A · φ_B) / (|φ_A| × |φ_B| + ε)

    Parameters
    ----------
    phi_A : ndarray — resource-use φ vector of species A
    phi_B : ndarray — resource-use φ vector of species B

    Returns
    -------
    overlap : float ∈ [0, 1]
    """
    a = np.asarray(phi_A, dtype=float)
    b = np.asarray(phi_B, dtype=float)
    if a.shape != b.shape:
        raise ValueError("phi_A and phi_B must have the same shape")
    return float(np.clip(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + _EPS),
                         0.0, 1.0))


def habitat_phi_density(n_individuals: float, area_km2: float) -> float:
    """Individual density per km² as a measure of habitat φ-loading.

    density = n / area

    Parameters
    ----------
    n_individuals : float — number of individuals (must be ≥ 0)
    area_km2      : float — habitat area in km² (must be > 0)

    Returns
    -------
    density : float
    """
    if n_individuals < 0.0:
        raise ValueError(f"n_individuals must be ≥ 0, got {n_individuals!r}")
    if area_km2 <= 0.0:
        raise ValueError(f"area_km2 must be > 0, got {area_km2!r}")
    return float(n_individuals / area_km2)


def disturbance_resilience(phi_pre: float, phi_post: float, t_recovery: float) -> float:
    """Ecosystem resilience: rate of φ recovery after disturbance.

    resilience = (φ_pre − φ_post) / t_recovery

    Parameters
    ----------
    phi_pre     : float — φ before disturbance (must be > 0)
    phi_post    : float — φ immediately after disturbance (must be ≥ 0)
    t_recovery  : float — time to recover (must be > 0)

    Returns
    -------
    resilience : float — φ recovery rate
    """
    if phi_pre <= 0.0:
        raise ValueError(f"phi_pre must be > 0, got {phi_pre!r}")
    if phi_post < 0.0:
        raise ValueError(f"phi_post must be ≥ 0, got {phi_post!r}")
    if t_recovery <= 0.0:
        raise ValueError(f"t_recovery must be > 0, got {t_recovery!r}")
    return float((phi_pre - phi_post) / t_recovery)


def nutrient_cycle_phi(input_phi: float, output_phi: float,
                        storage_phi: float) -> float:
    """Net φ-flux in a nutrient cycle.

    J_net = input_phi − output_phi − storage_phi

    Parameters
    ----------
    input_phi   : float — φ entering the cycle
    output_phi  : float — φ leaving the cycle
    storage_phi : float — φ stored in biomass/soil

    Returns
    -------
    J_net : float — net nutrient φ flux
    """
    return float(input_phi - output_phi - storage_phi)


def trophic_phi_flow(phi_primary: float, n_trophic_levels: int,
                     transfer_efficiency: float = 0.1) -> float:
    """φ reaching the top trophic level after n transfers.

    φ_top = φ_primary × ε^n

    Parameters
    ----------
    phi_primary        : float — primary productivity φ (must be ≥ 0)
    n_trophic_levels   : int   — number of trophic levels above primary (must be ≥ 0)
    transfer_efficiency: float — trophic transfer efficiency (default 0.1, must be in (0,1])

    Returns
    -------
    phi_top : float — φ at apex trophic level
    """
    if phi_primary < 0.0:
        raise ValueError(f"phi_primary must be ≥ 0, got {phi_primary!r}")
    if n_trophic_levels < 0:
        raise ValueError(f"n_trophic_levels must be ≥ 0, got {n_trophic_levels!r}")
    if not (0.0 < transfer_efficiency <= 1.0):
        raise ValueError(f"transfer_efficiency must be in (0,1], got {transfer_efficiency!r}")
    return float(phi_primary * transfer_efficiency ** n_trophic_levels)


def ecosystem_stability(phi_mean: float, phi_std: float) -> float:
    """Ecosystem stability as inverse coefficient of variation of φ.

    stability = φ_mean / (φ_std + ε)

    Parameters
    ----------
    phi_mean : float — mean φ over time (must be ≥ 0)
    phi_std  : float — standard deviation of φ (must be ≥ 0)

    Returns
    -------
    stability : float
    """
    if phi_mean < 0.0:
        raise ValueError(f"phi_mean must be ≥ 0, got {phi_mean!r}")
    if phi_std < 0.0:
        raise ValueError(f"phi_std must be ≥ 0, got {phi_std!r}")
    return float(phi_mean / (phi_std + _EPS))


def ecosystem_phi_productivity(phi_absorbed: float, efficiency: float) -> float:
    """Net primary φ-productivity from absorbed solar φ.

    NPP = φ_absorbed × efficiency

    Parameters
    ----------
    phi_absorbed : float — absorbed light φ (must be ≥ 0)
    efficiency   : float — photosynthetic φ efficiency ∈ (0, 1]

    Returns
    -------
    NPP : float
    """
    if phi_absorbed < 0.0:
        raise ValueError(f"phi_absorbed must be ≥ 0, got {phi_absorbed!r}")
    if not (0.0 < efficiency <= 1.0):
        raise ValueError(f"efficiency must be in (0,1], got {efficiency!r}")
    return float(phi_absorbed * efficiency)
