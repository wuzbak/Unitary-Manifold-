# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/marine/marine_life.py
==========================
Marine Life as φ-Field Biological Network — Pillar 23.
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


def coral_phi_bleaching(phi_symbiont: float, T_anomaly: float,
                         bleach_threshold: float = 1.0) -> float:
    """Symbiont φ remaining after thermal bleaching stress.

    φ_post = phi_symbiont × max(0, 1 − T_anomaly / bleach_threshold)

    Parameters
    ----------
    phi_symbiont     : float — baseline symbiont φ (must be ≥ 0)
    T_anomaly        : float — temperature anomaly above mean (°C)
    bleach_threshold : float — temperature anomaly for full bleaching (°C, must be > 0)

    Returns
    -------
    phi_post : float — surviving symbiont φ
    """
    if phi_symbiont < 0.0:
        raise ValueError(f"phi_symbiont must be ≥ 0, got {phi_symbiont!r}")
    if bleach_threshold <= 0.0:
        raise ValueError(f"bleach_threshold must be > 0, got {bleach_threshold!r}")
    survival = max(0.0, 1.0 - T_anomaly / bleach_threshold)
    return float(phi_symbiont * survival)


def reef_phi_health(phi_coral: float, phi_algae: float,
                     phi_fish: float) -> float:
    """Reef health index as balanced φ contribution.

    health = phi_coral / (phi_coral + phi_algae + phi_fish + ε)

    Parameters
    ----------
    phi_coral : float — coral cover φ (must be ≥ 0)
    phi_algae : float — macroalgae cover φ (must be ≥ 0)
    phi_fish  : float — fish biomass φ (must be ≥ 0)

    Returns
    -------
    health : float ∈ [0, 1]
    """
    for name, v in [("phi_coral", phi_coral), ("phi_algae", phi_algae), ("phi_fish", phi_fish)]:
        if v < 0.0:
            raise ValueError(f"{name} must be ≥ 0, got {v!r}")
    total = phi_coral + phi_algae + phi_fish + _EPS
    return float(phi_coral / total)


def phytoplankton_phi(nutrient_phi: float, light_phi: float,
                       max_growth_rate: float = 1.0) -> float:
    """Phytoplankton φ-productivity (Liebig's Law of the Minimum).

    φ_prod = max_growth_rate × min(nutrient_phi, light_phi)

    Parameters
    ----------
    nutrient_phi    : float — nutrient availability φ (must be ≥ 0)
    light_phi       : float — light availability φ (must be ≥ 0)
    max_growth_rate : float — maximum growth rate (default 1.0, must be > 0)

    Returns
    -------
    phi_prod : float
    """
    if nutrient_phi < 0.0:
        raise ValueError(f"nutrient_phi must be ≥ 0, got {nutrient_phi!r}")
    if light_phi < 0.0:
        raise ValueError(f"light_phi must be ≥ 0, got {light_phi!r}")
    if max_growth_rate <= 0.0:
        raise ValueError(f"max_growth_rate must be > 0, got {max_growth_rate!r}")
    return float(max_growth_rate * min(nutrient_phi, light_phi))


def zooplankton_phi_coupling(phi_phytoplankton: float,
                              grazing_rate: float) -> float:
    """Zooplankton φ uptake from phytoplankton grazing.

    φ_zoo = grazing_rate × phi_phytoplankton

    Parameters
    ----------
    phi_phytoplankton : float — phytoplankton φ (must be ≥ 0)
    grazing_rate      : float — grazing rate (must be ≥ 0)

    Returns
    -------
    phi_zoo : float
    """
    if phi_phytoplankton < 0.0:
        raise ValueError(f"phi_phytoplankton must be ≥ 0, got {phi_phytoplankton!r}")
    if grazing_rate < 0.0:
        raise ValueError(f"grazing_rate must be ≥ 0, got {grazing_rate!r}")
    return float(grazing_rate * phi_phytoplankton)


def marine_biodiversity_phi(species_phis: np.ndarray) -> float:
    """Total marine biodiversity φ as sum of species φ.

    Parameters
    ----------
    species_phis : ndarray — φ of each marine species (must be ≥ 0)

    Returns
    -------
    phi_total : float
    """
    arr = np.asarray(species_phis, dtype=float)
    if np.any(arr < 0.0):
        raise ValueError("species_phis must be ≥ 0")
    return float(arr.sum())


def whale_phi_communication(frequency_Hz: float, depth_m: float,
                              phi_signal: float) -> float:
    """Whale song φ-signal attenuation with depth.

    φ_received = phi_signal × exp(−depth_m / 1000) / (1 + frequency_Hz / 1000)

    Parameters
    ----------
    frequency_Hz : float — call frequency (must be > 0)
    depth_m      : float — transmission depth (must be ≥ 0)
    phi_signal   : float — source signal φ (must be ≥ 0)

    Returns
    -------
    phi_received : float
    """
    if frequency_Hz <= 0.0:
        raise ValueError(f"frequency_Hz must be > 0, got {frequency_Hz!r}")
    if depth_m < 0.0:
        raise ValueError(f"depth_m must be ≥ 0, got {depth_m!r}")
    if phi_signal < 0.0:
        raise ValueError(f"phi_signal must be ≥ 0, got {phi_signal!r}")
    return float(phi_signal * math.exp(-depth_m / 1000.0) / (1.0 + frequency_Hz / 1000.0))


def migration_phi_navigation(phi_magnetic: float, phi_chemical: float,
                               phi_celestial: float) -> float:
    """Composite navigation φ for marine migration.

    φ_nav = phi_magnetic + phi_chemical + phi_celestial

    Parameters
    ----------
    phi_magnetic  : float — geomagnetic cue φ (must be ≥ 0)
    phi_chemical  : float — olfactory cue φ (must be ≥ 0)
    phi_celestial : float — celestial orientation φ (must be ≥ 0)

    Returns
    -------
    phi_nav : float
    """
    for name, v in [("phi_magnetic", phi_magnetic), ("phi_chemical", phi_chemical),
                    ("phi_celestial", phi_celestial)]:
        if v < 0.0:
            raise ValueError(f"{name} must be ≥ 0, got {v!r}")
    return float(phi_magnetic + phi_chemical + phi_celestial)


def schooling_phi_coherence(n_fish: int, phi_individual: float,
                              coherence_factor: float = 0.9) -> float:
    """Collective φ of a fish school (emergent coherence above individual sum).

    φ_school = n_fish × phi_individual × coherence_factor

    Parameters
    ----------
    n_fish           : int   — school size (must be ≥ 1)
    phi_individual   : float — individual fish φ (must be ≥ 0)
    coherence_factor : float — coherence enhancement (default 0.9, ∈ (0,1])

    Returns
    -------
    phi_school : float
    """
    if n_fish < 1:
        raise ValueError(f"n_fish must be ≥ 1, got {n_fish!r}")
    if phi_individual < 0.0:
        raise ValueError(f"phi_individual must be ≥ 0, got {phi_individual!r}")
    if not (0.0 < coherence_factor <= 1.0):
        raise ValueError(f"coherence_factor must be in (0,1], got {coherence_factor!r}")
    return float(n_fish * phi_individual * coherence_factor)


def kelp_phi_forest(phi_irradiance: float, nutrient_phi: float,
                     growth_rate: float = 0.3) -> float:
    """Kelp forest φ-productivity.

    φ_kelp = growth_rate × phi_irradiance × nutrient_phi

    Parameters
    ----------
    phi_irradiance : float — light φ reaching canopy (must be ≥ 0)
    nutrient_phi   : float — dissolved nutrient φ (must be ≥ 0)
    growth_rate    : float — kelp growth coefficient (default 0.3, must be > 0)

    Returns
    -------
    phi_kelp : float
    """
    if phi_irradiance < 0.0:
        raise ValueError(f"phi_irradiance must be ≥ 0, got {phi_irradiance!r}")
    if nutrient_phi < 0.0:
        raise ValueError(f"nutrient_phi must be ≥ 0, got {nutrient_phi!r}")
    if growth_rate <= 0.0:
        raise ValueError(f"growth_rate must be > 0, got {growth_rate!r}")
    return float(growth_rate * phi_irradiance * nutrient_phi)


def marine_phi_toxin_snr(phi_toxin: float, B_noise: float) -> float:
    """Signal-to-noise ratio of harmful algal bloom toxin detection.

    SNR = phi_toxin / (B_noise + ε)

    Parameters
    ----------
    phi_toxin : float — toxin concentration φ (must be ≥ 0)
    B_noise   : float — background noise (must be ≥ 0)

    Returns
    -------
    SNR : float
    """
    if phi_toxin < 0.0:
        raise ValueError(f"phi_toxin must be ≥ 0, got {phi_toxin!r}")
    if B_noise < 0.0:
        raise ValueError(f"B_noise must be ≥ 0, got {B_noise!r}")
    return float(phi_toxin / (B_noise + _EPS))
