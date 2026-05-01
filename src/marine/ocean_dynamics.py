# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/marine/ocean_dynamics.py
=============================
Ocean Circulation as φ-Field Fluid Dynamics — Pillar 23.
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


def thermohaline_phi(T: float, S: float,
                      alpha_T: float = 0.2, beta_S: float = 0.8) -> float:
    """Thermohaline circulation driving force.

    φ_THC = beta_S × S − alpha_T × T

    Dense, cold, salty water sinks: higher φ_THC → stronger overturning.

    Parameters
    ----------
    T       : float — temperature (°C)
    S       : float — salinity (PSU, must be ≥ 0)
    alpha_T : float — thermal expansion coefficient (default 0.2)
    beta_S  : float — haline contraction coefficient (default 0.8)

    Returns
    -------
    phi_THC : float — thermohaline driving φ
    """
    if S < 0.0:
        raise ValueError(f"S must be ≥ 0, got {S!r}")
    return float(beta_S * S - alpha_T * T)


def upwelling_phi_flux(phi_deep: float, phi_surface: float,
                        upwelling_rate: float) -> float:
    """Nutrient φ-flux from deep upwelling.

    J_up = upwelling_rate × (phi_deep − phi_surface)

    Parameters
    ----------
    phi_deep       : float — deep water nutrient φ (must be ≥ 0)
    phi_surface    : float — surface nutrient φ (must be ≥ 0)
    upwelling_rate : float — upwelling rate m/day (must be ≥ 0)

    Returns
    -------
    J_up : float
    """
    if phi_deep < 0.0:
        raise ValueError(f"phi_deep must be ≥ 0, got {phi_deep!r}")
    if phi_surface < 0.0:
        raise ValueError(f"phi_surface must be ≥ 0, got {phi_surface!r}")
    if upwelling_rate < 0.0:
        raise ValueError(f"upwelling_rate must be ≥ 0, got {upwelling_rate!r}")
    return float(upwelling_rate * (phi_deep - phi_surface))


def ocean_acidification_phi(ph: float, ph_ref: float = 8.2) -> float:
    """Ocean acidification φ-stress relative to pre-industrial pH.

    stress = max(0, ph_ref − ph)

    Parameters
    ----------
    ph     : float — current ocean surface pH (must be > 0)
    ph_ref : float — pre-industrial reference pH (default 8.2, must be > 0)

    Returns
    -------
    stress : float ≥ 0 (higher = more acidic)
    """
    if ph <= 0.0:
        raise ValueError(f"ph must be > 0, got {ph!r}")
    if ph_ref <= 0.0:
        raise ValueError(f"ph_ref must be > 0, got {ph_ref!r}")
    return float(max(0.0, ph_ref - ph))


def sea_level_phi_rise(phi_thermal_expansion: float,
                        phi_ice_melt: float) -> float:
    """Total sea level φ rise from thermal expansion and ice melt.

    SLR = phi_thermal_expansion + phi_ice_melt

    Parameters
    ----------
    phi_thermal_expansion : float — thermal expansion contribution (must be ≥ 0)
    phi_ice_melt          : float — ice melt contribution (must be ≥ 0)

    Returns
    -------
    SLR : float — total sea level rise φ (mm)
    """
    if phi_thermal_expansion < 0.0:
        raise ValueError(f"phi_thermal_expansion must be ≥ 0, got {phi_thermal_expansion!r}")
    if phi_ice_melt < 0.0:
        raise ValueError(f"phi_ice_melt must be ≥ 0, got {phi_ice_melt!r}")
    return float(phi_thermal_expansion + phi_ice_melt)


def gyre_phi_circulation(wind_stress: float, coriolis_f: float,
                          area_km2: float) -> float:
    """Sverdrup transport φ of an ocean gyre.

    transport = wind_stress / (coriolis_f × area_km2 + ε)

    Parameters
    ----------
    wind_stress : float — zonal wind stress Pa (must be ≥ 0)
    coriolis_f  : float — Coriolis parameter s⁻¹ (must be > 0)
    area_km2    : float — gyre area in km² (must be > 0)

    Returns
    -------
    transport : float — φ transport
    """
    if wind_stress < 0.0:
        raise ValueError(f"wind_stress must be ≥ 0, got {wind_stress!r}")
    if coriolis_f <= 0.0:
        raise ValueError(f"coriolis_f must be > 0, got {coriolis_f!r}")
    if area_km2 <= 0.0:
        raise ValueError(f"area_km2 must be > 0, got {area_km2!r}")
    return float(wind_stress / (coriolis_f * area_km2 + _EPS))


def tidal_phi_forcing(M2_amplitude: float, distance_from_moon: float,
                       ref_distance: float = 3.84e8) -> float:
    """Tidal φ-forcing from lunar gravitational gradient.

    F_tidal = M2_amplitude × (ref_distance / distance_from_moon)²

    Parameters
    ----------
    M2_amplitude      : float — principal lunar semi-diurnal amplitude (m, must be ≥ 0)
    distance_from_moon: float — Earth-Moon distance (m, must be > 0)
    ref_distance      : float — mean Earth-Moon distance (default 3.84e8 m)

    Returns
    -------
    F_tidal : float — scaled tidal forcing
    """
    if M2_amplitude < 0.0:
        raise ValueError(f"M2_amplitude must be ≥ 0, got {M2_amplitude!r}")
    if distance_from_moon <= 0.0:
        raise ValueError(f"distance_from_moon must be > 0, got {distance_from_moon!r}")
    return float(M2_amplitude * (ref_distance / distance_from_moon) ** 2)


def salinity_phi_gradient(S_high: float, S_low: float,
                           distance_km: float) -> float:
    """Salinity φ-gradient driving haline circulation.

    grad_S = (S_high − S_low) / distance_km

    Parameters
    ----------
    S_high      : float — high-salinity end (PSU, must be ≥ 0)
    S_low       : float — low-salinity end (PSU, must be ≥ 0)
    distance_km : float — horizontal distance in km (must be > 0)

    Returns
    -------
    grad_S : float
    """
    if S_high < 0.0:
        raise ValueError(f"S_high must be ≥ 0, got {S_high!r}")
    if S_low < 0.0:
        raise ValueError(f"S_low must be ≥ 0, got {S_low!r}")
    if distance_km <= 0.0:
        raise ValueError(f"distance_km must be > 0, got {distance_km!r}")
    return float((S_high - S_low) / distance_km)


def ocean_phi_heat_content(mass_kg: float, delta_T: float,
                            c_p: float = 4000.0) -> float:
    """Ocean heat content φ change.

    OHC = mass_kg × c_p × delta_T

    Parameters
    ----------
    mass_kg  : float — seawater mass in kg (must be > 0)
    delta_T  : float — temperature change K
    c_p      : float — specific heat J kg⁻¹ K⁻¹ (default 4000)

    Returns
    -------
    OHC : float — heat content change in Joules
    """
    if mass_kg <= 0.0:
        raise ValueError(f"mass_kg must be > 0, got {mass_kg!r}")
    if c_p <= 0.0:
        raise ValueError(f"c_p must be > 0, got {c_p!r}")
    return float(mass_kg * c_p * delta_T)


def el_nino_phi(sst_anomaly: float, threshold: float = 0.5) -> float:
    """El Niño strength as SST anomaly above threshold.

    strength = max(0, sst_anomaly − threshold)

    Parameters
    ----------
    sst_anomaly : float — sea surface temperature anomaly °C
    threshold   : float — El Niño onset threshold °C (default 0.5)

    Returns
    -------
    strength : float ≥ 0
    """
    return float(max(0.0, sst_anomaly - threshold))


def marine_phi_stratification(phi_warm: float, phi_cold: float,
                               depth_m: float) -> float:
    """Thermal stratification φ-index.

    stratification = (phi_warm − phi_cold) / depth_m

    Parameters
    ----------
    phi_warm : float — surface warm layer φ
    phi_cold : float — deep cold layer φ
    depth_m  : float — mixed layer depth in m (must be > 0)

    Returns
    -------
    stratification : float
    """
    if depth_m <= 0.0:
        raise ValueError(f"depth_m must be > 0, got {depth_m!r}")
    return float((phi_warm - phi_cold) / depth_m)
