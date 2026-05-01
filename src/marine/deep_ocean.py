# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/marine/deep_ocean.py
=========================
Deep Ocean as Extreme φ-Field Environment — Pillar 23: Marine Science.

Theory
------
The deep ocean is the largest stable φ-reservoir on Earth.  Pressure
increases monotonically with depth, compressing the local φ-field and
creating a gradient that drives the biological pump — the downward flux
of organic carbon φ from the sunlit surface into the abyss.  Hydrothermal
vents are localised φ-sources where geothermal energy enters the ocean
irreversibility field, sustaining chemosynthetic ecosystems far from
solar φ input.
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


def pressure_phi_adaptation(depth_m: float, phi_surface: float = 1.0) -> float:
    """Pressure-scaled φ-field at ocean depth.

    φ(d) = φ_surface × (1 + d / 10)   (1 atm per 10 m of seawater)

    Parameters
    ----------
    depth_m     : float — depth in metres (must be ≥ 0)
    phi_surface : float — surface φ reference (default 1.0, must be > 0)

    Returns
    -------
    phi_d : float — pressure-adapted φ at depth
    """
    if depth_m < 0.0:
        raise ValueError(f"depth_m must be ≥ 0, got {depth_m!r}")
    if phi_surface <= 0.0:
        raise ValueError(f"phi_surface must be > 0, got {phi_surface!r}")
    return float(phi_surface * (1.0 + depth_m / 10.0))


def bioluminescence_phi(phi_chemical: float, efficiency: float = 0.95) -> float:
    """φ-photon output of bioluminescent organism.

    φ_light = efficiency × φ_chemical

    Parameters
    ----------
    phi_chemical : float — chemical φ energy input (must be ≥ 0)
    efficiency   : float — bioluminescent efficiency ∈ (0, 1] (default 0.95)

    Returns
    -------
    phi_light : float
    """
    if phi_chemical < 0.0:
        raise ValueError(f"phi_chemical must be ≥ 0, got {phi_chemical!r}")
    if not (0.0 < efficiency <= 1.0):
        raise ValueError(f"efficiency must be in (0,1], got {efficiency!r}")
    return float(efficiency * phi_chemical)


def hydrothermal_phi_flux(temperature_C: float, flow_rate_m3s: float,
                           phi_per_J: float = 1e-6) -> float:
    """φ-flux from a hydrothermal vent.

    J_vent = rho_water × c_p × flow_rate × temperature_C × phi_per_J

    Parameters
    ----------
    temperature_C : float — vent temperature in °C (must be > 0)
    flow_rate_m3s : float — volumetric flow rate m³/s (must be ≥ 0)
    phi_per_J     : float — φ per Joule of thermal energy (default 1e-6)

    Returns
    -------
    J_vent : float — φ flux
    """
    if temperature_C <= 0.0:
        raise ValueError(f"temperature_C must be > 0, got {temperature_C!r}")
    if flow_rate_m3s < 0.0:
        raise ValueError(f"flow_rate_m3s must be ≥ 0, got {flow_rate_m3s!r}")
    rho_cp = 1025.0 * 4000.0  # kg/m³ × J/(kg K)
    return float(rho_cp * flow_rate_m3s * temperature_C * phi_per_J)


def deep_sea_phi_density(phi_surface: float, depth_m: float,
                          scale_depth: float = 1000.0) -> float:
    """Exponential φ-density decrease with depth (biological pump).

    φ(d) = φ_surface × exp(−d / scale_depth)

    Parameters
    ----------
    phi_surface  : float — surface φ density (must be ≥ 0)
    depth_m      : float — depth in metres (must be ≥ 0)
    scale_depth  : float — e-folding scale depth in m (default 1000, must be > 0)

    Returns
    -------
    phi_d : float
    """
    if phi_surface < 0.0:
        raise ValueError(f"phi_surface must be ≥ 0, got {phi_surface!r}")
    if depth_m < 0.0:
        raise ValueError(f"depth_m must be ≥ 0, got {depth_m!r}")
    if scale_depth <= 0.0:
        raise ValueError(f"scale_depth must be > 0, got {scale_depth!r}")
    return float(phi_surface * math.exp(-depth_m / scale_depth))


def abyssal_phi_gradient(phi_deep: float, phi_bottom: float,
                          distance_m: float) -> float:
    """Vertical φ gradient in the abyssal zone.

    grad = (phi_deep − phi_bottom) / distance_m

    Parameters
    ----------
    phi_deep    : float — φ at upper abyssal boundary
    phi_bottom  : float — φ at seafloor
    distance_m  : float — vertical distance in metres (must be > 0)

    Returns
    -------
    grad : float
    """
    if distance_m <= 0.0:
        raise ValueError(f"distance_m must be > 0, got {distance_m!r}")
    return float((phi_deep - phi_bottom) / distance_m)


def chemosynthesis_phi(phi_H2S: float, phi_O2: float,
                        efficiency: float = 0.05) -> float:
    """φ-productivity of chemosynthetic bacteria.

    φ_prod = efficiency × min(phi_H2S, phi_O2)

    Parameters
    ----------
    phi_H2S    : float — hydrogen sulphide φ (must be ≥ 0)
    phi_O2     : float — oxygen φ (must be ≥ 0)
    efficiency : float — chemosynthetic efficiency (default 0.05, must be in (0,1])

    Returns
    -------
    phi_prod : float
    """
    if phi_H2S < 0.0:
        raise ValueError(f"phi_H2S must be ≥ 0, got {phi_H2S!r}")
    if phi_O2 < 0.0:
        raise ValueError(f"phi_O2 must be ≥ 0, got {phi_O2!r}")
    if not (0.0 < efficiency <= 1.0):
        raise ValueError(f"efficiency must be in (0,1], got {efficiency!r}")
    return float(efficiency * min(phi_H2S, phi_O2))


def mesopelagic_phi_zone(phi_epipelagic: float,
                          attenuation: float = 0.01) -> float:
    """φ-flux reaching the mesopelagic zone (200–1000 m).

    φ_meso = phi_epipelagic × exp(−attenuation × 600)

    Parameters
    ----------
    phi_epipelagic : float — surface-zone φ flux (must be ≥ 0)
    attenuation    : float — attenuation coefficient m⁻¹ (must be ≥ 0)

    Returns
    -------
    phi_meso : float
    """
    if phi_epipelagic < 0.0:
        raise ValueError(f"phi_epipelagic must be ≥ 0, got {phi_epipelagic!r}")
    if attenuation < 0.0:
        raise ValueError(f"attenuation must be ≥ 0, got {attenuation!r}")
    return float(phi_epipelagic * math.exp(-attenuation * 600.0))


def bathypelagic_phi(phi_mesopelagic: float, attenuation: float = 0.001) -> float:
    """φ-flux reaching the bathypelagic zone (1000–4000 m).

    φ_batho = phi_mesopelagic × exp(−attenuation × 3000)

    Parameters
    ----------
    phi_mesopelagic : float — mesopelagic φ flux (must be ≥ 0)
    attenuation     : float — attenuation coefficient m⁻¹ (must be ≥ 0)

    Returns
    -------
    phi_batho : float
    """
    if phi_mesopelagic < 0.0:
        raise ValueError(f"phi_mesopelagic must be ≥ 0, got {phi_mesopelagic!r}")
    if attenuation < 0.0:
        raise ValueError(f"attenuation must be ≥ 0, got {attenuation!r}")
    return float(phi_mesopelagic * math.exp(-attenuation * 3000.0))


def hadal_phi_extreme(phi_bathypelagic: float,
                       pressure_multiplier: float = 1.1) -> float:
    """φ at hadal depths (> 6000 m), enhanced by extreme pressure.

    φ_hadal = phi_bathypelagic × pressure_multiplier

    Parameters
    ----------
    phi_bathypelagic    : float — bathypelagic φ (must be ≥ 0)
    pressure_multiplier : float — pressure enhancement factor (must be ≥ 1)

    Returns
    -------
    phi_hadal : float
    """
    if phi_bathypelagic < 0.0:
        raise ValueError(f"phi_bathypelagic must be ≥ 0, got {phi_bathypelagic!r}")
    if pressure_multiplier < 1.0:
        raise ValueError(f"pressure_multiplier must be ≥ 1, got {pressure_multiplier!r}")
    return float(phi_bathypelagic * pressure_multiplier)


def deep_current_phi(phi_dense: float, phi_ambient: float,
                      density_diff: float) -> float:
    """Bottom current φ-flux driven by density difference.

    J_current = density_diff × (phi_dense − phi_ambient)

    Parameters
    ----------
    phi_dense   : float — dense water mass φ
    phi_ambient : float — ambient water φ
    density_diff: float — density difference kg m⁻³ (must be ≥ 0)

    Returns
    -------
    J_current : float
    """
    if density_diff < 0.0:
        raise ValueError(f"density_diff must be ≥ 0, got {density_diff!r}")
    return float(density_diff * (phi_dense - phi_ambient))
