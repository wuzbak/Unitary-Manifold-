# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/ecology/biodiversity.py
============================
Biodiversity as φ-Field Richness — Pillar 21.
"""

from __future__ import annotations
import math
import numpy as np

_EPS = 1e-30


def shannon_diversity_phi(abundances: np.ndarray) -> float:
    """Shannon-Wiener diversity index of species abundances.

    H' = −Σ p_i ln(p_i)

    Parameters
    ----------
    abundances : ndarray — species abundance counts (must be ≥ 0)

    Returns
    -------
    H : float ≥ 0
    """
    arr = np.asarray(abundances, dtype=float)
    if np.any(arr < 0.0):
        raise ValueError("abundances must be ≥ 0")
    total = arr.sum() + _EPS
    p = arr / total
    return float(-np.sum(p * np.log(p + _EPS)))


def species_phi_abundance(species_phi: float, total_phi: float) -> float:
    """Relative φ-abundance of a species.

    p_i = φ_i / Σφ_j  ∈ [0, 1]

    Parameters
    ----------
    species_phi : float — species' φ (must be ≥ 0)
    total_phi   : float — total community φ (must be > 0)

    Returns
    -------
    p_i : float ∈ [0, 1]
    """
    if species_phi < 0.0:
        raise ValueError(f"species_phi must be ≥ 0, got {species_phi!r}")
    if total_phi <= 0.0:
        raise ValueError(f"total_phi must be > 0, got {total_phi!r}")
    return float(np.clip(species_phi / total_phi, 0.0, 1.0))


def extinction_risk_phi(phi_population: float, phi_minimum_viable: float) -> float:
    """Extinction risk as fractional deficit below minimum viable population φ.

    risk = max(0,  1 − φ_population / φ_minimum_viable)

    Parameters
    ----------
    phi_population     : float — current population φ (must be ≥ 0)
    phi_minimum_viable : float — minimum viable φ (must be > 0)

    Returns
    -------
    risk : float ∈ [0, 1]
    """
    if phi_population < 0.0:
        raise ValueError(f"phi_population must be ≥ 0, got {phi_population!r}")
    if phi_minimum_viable <= 0.0:
        raise ValueError(f"phi_minimum_viable must be > 0, got {phi_minimum_viable!r}")
    return float(max(0.0, 1.0 - phi_population / phi_minimum_viable))


def invasive_phi_disruption(phi_native: float, phi_invasive: float,
                             competition_alpha: float) -> float:
    """φ-reduction of native species caused by invasive competitor.

    disruption = phi_invasive × competition_alpha / (phi_native + _EPS)

    Parameters
    ----------
    phi_native      : float — native species φ (must be ≥ 0)
    phi_invasive    : float — invasive species φ (must be ≥ 0)
    competition_alpha: float — competition coefficient (must be ≥ 0)

    Returns
    -------
    disruption : float ≥ 0
    """
    if phi_native < 0.0:
        raise ValueError(f"phi_native must be ≥ 0, got {phi_native!r}")
    if phi_invasive < 0.0:
        raise ValueError(f"phi_invasive must be ≥ 0, got {phi_invasive!r}")
    if competition_alpha < 0.0:
        raise ValueError(f"competition_alpha must be ≥ 0, got {competition_alpha!r}")
    return float(phi_invasive * competition_alpha / (phi_native + _EPS))


def biodiversity_snr(phi_diversity: float, B_noise: float) -> float:
    """Signal-to-noise ratio of biodiversity measurement.

    SNR = φ_diversity / (B_noise + ε)

    Parameters
    ----------
    phi_diversity : float — diversity φ signal (must be ≥ 0)
    B_noise       : float — measurement noise (must be ≥ 0)

    Returns
    -------
    SNR : float
    """
    if phi_diversity < 0.0:
        raise ValueError(f"phi_diversity must be ≥ 0, got {phi_diversity!r}")
    if B_noise < 0.0:
        raise ValueError(f"B_noise must be ≥ 0, got {B_noise!r}")
    return float(phi_diversity / (B_noise + _EPS))


def habitat_fragmentation_index(total_area: float, n_fragments: int,
                                 mean_fragment_area: float) -> float:
    """Habitat fragmentation index.

    HFI = n_fragments × mean_fragment_area / total_area

    Parameters
    ----------
    total_area         : float — original contiguous habitat area (must be > 0)
    n_fragments        : int   — number of fragments (must be ≥ 1)
    mean_fragment_area : float — mean fragment area (must be > 0)

    Returns
    -------
    HFI : float
    """
    if total_area <= 0.0:
        raise ValueError(f"total_area must be > 0, got {total_area!r}")
    if n_fragments < 1:
        raise ValueError(f"n_fragments must be ≥ 1, got {n_fragments!r}")
    if mean_fragment_area <= 0.0:
        raise ValueError(f"mean_fragment_area must be > 0, got {mean_fragment_area!r}")
    return float(n_fragments * mean_fragment_area / total_area)


def keystone_phi_effect(phi_ecosystem_with: float, phi_ecosystem_without: float) -> float:
    """φ impact of a keystone species on ecosystem φ.

    keystone_effect = phi_ecosystem_with − phi_ecosystem_without

    Parameters
    ----------
    phi_ecosystem_with    : float — ecosystem φ with the keystone species
    phi_ecosystem_without : float — ecosystem φ after its removal

    Returns
    -------
    effect : float (positive = ecosystem enhancer)
    """
    return float(phi_ecosystem_with - phi_ecosystem_without)


def phylogenetic_diversity_phi(branch_lengths: np.ndarray) -> float:
    """Faith's phylogenetic diversity as sum of unique branch-length φ.

    PD = Σ branch_length_i

    Parameters
    ----------
    branch_lengths : ndarray — unique branch lengths of a phylogeny (must be ≥ 0)

    Returns
    -------
    PD : float — total phylogenetic diversity
    """
    arr = np.asarray(branch_lengths, dtype=float)
    if np.any(arr < 0.0):
        raise ValueError("branch_lengths must be ≥ 0")
    return float(arr.sum())


def conservation_phi_investment(phi_gained: float, cost: float) -> float:
    """Return on conservation φ-investment.

    ROI = φ_gained / (cost + ε)

    Parameters
    ----------
    phi_gained : float — biodiversity φ preserved (must be ≥ 0)
    cost       : float — economic cost (must be ≥ 0)

    Returns
    -------
    ROI : float
    """
    if phi_gained < 0.0:
        raise ValueError(f"phi_gained must be ≥ 0, got {phi_gained!r}")
    if cost < 0.0:
        raise ValueError(f"cost must be ≥ 0, got {cost!r}")
    return float(phi_gained / (cost + _EPS))


def endemic_phi_concentration(phi_endemic: float, phi_total: float) -> float:
    """Fraction of total φ held by endemic species.

    endemism = φ_endemic / φ_total  ∈ [0, 1]

    Parameters
    ----------
    phi_endemic : float — φ of endemic species (must be ≥ 0)
    phi_total   : float — total ecosystem φ (must be > 0)

    Returns
    -------
    endemism : float ∈ [0, 1]
    """
    if phi_endemic < 0.0:
        raise ValueError(f"phi_endemic must be ≥ 0, got {phi_endemic!r}")
    if phi_total <= 0.0:
        raise ValueError(f"phi_total must be > 0, got {phi_total!r}")
    return float(np.clip(phi_endemic / phi_total, 0.0, 1.0))
