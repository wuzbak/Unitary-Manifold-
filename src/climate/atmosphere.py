# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/climate/atmosphere.py
==========================
Atmosphere as a φ-Field Radiative Engine — Pillar 22: Climate Science.

Theory
------
The atmosphere is a φ-field thermal bath where greenhouse gases act as
B_μ-coupling agents that trap outgoing infrared φ-flux.  The radiative
balance at the top of the atmosphere is the equilibrium condition:

    φ_in(solar) = φ_out(IR) + φ_trapped(GHG)

A positive radiative imbalance (φ_in > φ_out) drives planetary warming —
a displacement of the global φ fixed-point toward a higher-temperature
attractor.  The irreversibility field B_μ encodes the one-way nature of
this energy flow: entropy increases monotonically as φ is trapped.
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
_SIGMA = 5.670374419e-8  # Stefan-Boltzmann constant W m⁻² K⁻⁴


def greenhouse_forcing_phi(co2_ppm: float, co2_ref: float = 280.0) -> float:
    """Radiative forcing from CO₂ increase above pre-industrial reference.

    ΔF = 5.35 × ln(CO₂ / CO₂_ref)   W m⁻²  (IPCC formula)

    Parameters
    ----------
    co2_ppm : float — current CO₂ concentration in ppm (must be > 0)
    co2_ref : float — pre-industrial reference ppm (default 280, must be > 0)

    Returns
    -------
    delta_F : float — radiative forcing in W m⁻²
    """
    if co2_ppm <= 0.0:
        raise ValueError(f"co2_ppm must be > 0, got {co2_ppm!r}")
    if co2_ref <= 0.0:
        raise ValueError(f"co2_ref must be > 0, got {co2_ref!r}")
    return float(5.35 * math.log(co2_ppm / co2_ref))


def radiative_balance_phi(solar_in: float, albedo: float,
                           outgoing_ir: float) -> float:
    """Net radiative energy balance at the top of the atmosphere.

    Fnet = solar_in × (1 − albedo) − outgoing_ir

    Parameters
    ----------
    solar_in    : float — incoming solar flux W m⁻² (must be ≥ 0)
    albedo      : float — planetary albedo ∈ [0, 1]
    outgoing_ir : float — outgoing longwave radiation W m⁻² (must be ≥ 0)

    Returns
    -------
    F_net : float — net flux (positive = warming)
    """
    if solar_in < 0.0:
        raise ValueError(f"solar_in must be ≥ 0, got {solar_in!r}")
    if not (0.0 <= albedo <= 1.0):
        raise ValueError(f"albedo must be in [0,1], got {albedo!r}")
    if outgoing_ir < 0.0:
        raise ValueError(f"outgoing_ir must be ≥ 0, got {outgoing_ir!r}")
    return float(solar_in * (1.0 - albedo) - outgoing_ir)


def temperature_phi_anomaly(T_current: float, T_baseline: float) -> float:
    """Temperature anomaly relative to a baseline period.

    ΔT = T_current − T_baseline

    Parameters
    ----------
    T_current  : float — current global mean temperature (K or °C)
    T_baseline : float — baseline period mean temperature

    Returns
    -------
    delta_T : float — temperature anomaly
    """
    return float(T_current - T_baseline)


def albedo_feedback_phi(delta_T: float, dalpha_dT: float = -0.01) -> float:
    """Ice-albedo feedback change per degree of warming.

    Δα = (dα/dT) × ΔT

    As temperature rises, ice melts → albedo decreases → more absorption.

    Parameters
    ----------
    delta_T    : float — temperature change (K)
    dalpha_dT  : float — albedo sensitivity (default -0.01 K⁻¹)

    Returns
    -------
    delta_alpha : float — albedo change (negative = more absorption)
    """
    return float(dalpha_dT * delta_T)


def aerosol_phi_scattering(aerosol_optical_depth: float,
                            solar_flux: float) -> float:
    """Solar φ-flux scattered back to space by aerosols.

    F_scatter = aerosol_optical_depth × solar_flux

    Parameters
    ----------
    aerosol_optical_depth : float — AOD (must be ≥ 0)
    solar_flux            : float — incident solar flux W m⁻² (must be ≥ 0)

    Returns
    -------
    F_scatter : float — scattered flux W m⁻²
    """
    if aerosol_optical_depth < 0.0:
        raise ValueError(f"aerosol_optical_depth must be ≥ 0, got {aerosol_optical_depth!r}")
    if solar_flux < 0.0:
        raise ValueError(f"solar_flux must be ≥ 0, got {solar_flux!r}")
    return float(aerosol_optical_depth * solar_flux)


def stratospheric_ozone_phi(ozone_column_du: float,
                             ozone_ref_du: float = 300.0) -> float:
    """Normalised stratospheric ozone φ relative to reference.

    φ_O3 = ozone_column_du / ozone_ref_du

    Parameters
    ----------
    ozone_column_du : float — current ozone column in Dobson units (must be > 0)
    ozone_ref_du    : float — reference ozone column (default 300 DU, must be > 0)

    Returns
    -------
    phi_O3 : float — normalised ozone φ (1.0 = healthy)
    """
    if ozone_column_du <= 0.0:
        raise ValueError(f"ozone_column_du must be > 0, got {ozone_column_du!r}")
    if ozone_ref_du <= 0.0:
        raise ValueError(f"ozone_ref_du must be > 0, got {ozone_ref_du!r}")
    return float(ozone_column_du / ozone_ref_du)


def atmospheric_phi_circulation(phi_equator: float, phi_pole: float,
                                  distance_km: float) -> float:
    """Meridional φ-gradient driving atmospheric circulation.

    grad_phi = (φ_equator − φ_pole) / distance_km

    Parameters
    ----------
    phi_equator  : float — equatorial temperature φ
    phi_pole     : float — polar temperature φ
    distance_km  : float — equator-to-pole distance in km (must be > 0)

    Returns
    -------
    grad_phi : float — φ gradient (positive = equatorward drive)
    """
    if distance_km <= 0.0:
        raise ValueError(f"distance_km must be > 0, got {distance_km!r}")
    return float((phi_equator - phi_pole) / distance_km)


def humidity_phi_coupling(T_K: float, relative_humidity: float) -> float:
    """Atmospheric water-vapour φ capacity at temperature T.

    φ_H2O = RH × 6.112 × exp(17.67 × (T_C) / (T_C + 243.5))  (Magnus formula, hPa)

    Parameters
    ----------
    T_K               : float — temperature in Kelvin (must be > 0)
    relative_humidity : float — relative humidity ∈ [0, 1]

    Returns
    -------
    phi_H2O : float — water vapour partial pressure in hPa
    """
    if T_K <= 0.0:
        raise ValueError(f"T_K must be > 0, got {T_K!r}")
    if not (0.0 <= relative_humidity <= 1.0):
        raise ValueError(f"relative_humidity must be in [0,1], got {relative_humidity!r}")
    T_C = T_K - 273.15
    e_sat = 6.112 * math.exp(17.67 * T_C / (T_C + 243.5))
    return float(relative_humidity * e_sat)


def jet_stream_phi(phi_mid_lat: float, phi_polar: float) -> float:
    """Jet stream φ-pressure gradient driving zonal wind.

    ΔP_jet = φ_mid_lat − φ_polar

    Parameters
    ----------
    phi_mid_lat : float — mid-latitude pressure φ
    phi_polar   : float — polar pressure φ

    Returns
    -------
    delta_P : float — jet stream pressure gradient
    """
    return float(phi_mid_lat - phi_polar)


def tropospheric_phi_mixing(phi_surface: float, phi_tropopause: float,
                             mixing_depth_km: float) -> float:
    """Vertical φ-mixing rate in the troposphere.

    J_mix = (φ_surface − φ_tropopause) / mixing_depth_km

    Parameters
    ----------
    phi_surface     : float — surface layer φ
    phi_tropopause  : float — tropopause φ
    mixing_depth_km : float — tropospheric depth in km (must be > 0)

    Returns
    -------
    J_mix : float — vertical mixing flux
    """
    if mixing_depth_km <= 0.0:
        raise ValueError(f"mixing_depth_km must be > 0, got {mixing_depth_km!r}")
    return float((phi_surface - phi_tropopause) / mixing_depth_km)
