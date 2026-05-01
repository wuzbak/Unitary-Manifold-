# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/climate/carbon_cycle.py
============================
Carbon Cycle as φ-Field Mass-Balance — Pillar 22.
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
import numpy as np

_EPS = 1e-30


def carbon_phi_flux(delta_C: float, dt: float) -> float:
    """Net carbon φ-flux: ΔC / Δt.

    Parameters
    ----------
    delta_C : float — change in carbon pool φ (GtC)
    dt      : float — time interval (years, must be > 0)

    Returns
    -------
    flux : float — GtC yr⁻¹
    """
    if dt <= 0.0:
        raise ValueError(f"dt must be > 0, got {dt!r}")
    return float(delta_C / dt)


def ocean_uptake_phi(phi_atm: float, phi_ocean_surface: float,
                      piston_velocity: float) -> float:
    """Ocean CO₂ uptake as air-sea φ flux.

    F_ocean = piston_velocity × (φ_atm − φ_ocean_surface)

    Parameters
    ----------
    phi_atm           : float — atmospheric pCO₂ φ
    phi_ocean_surface : float — surface ocean pCO₂ φ
    piston_velocity   : float — gas transfer velocity (must be ≥ 0)

    Returns
    -------
    F_ocean : float — uptake flux (positive = ocean absorbs)
    """
    if piston_velocity < 0.0:
        raise ValueError(f"piston_velocity must be ≥ 0, got {piston_velocity!r}")
    return float(piston_velocity * (phi_atm - phi_ocean_surface))


def terrestrial_sequestration_phi(phi_npp: float, phi_respiration: float,
                                   phi_disturbance: float) -> float:
    """Net terrestrial carbon sequestration.

    NEP = φ_NPP − φ_respiration − φ_disturbance

    Parameters
    ----------
    phi_npp         : float — net primary productivity φ (must be ≥ 0)
    phi_respiration : float — ecosystem respiration φ (must be ≥ 0)
    phi_disturbance : float — disturbance (fire, harvest) φ loss (must be ≥ 0)

    Returns
    -------
    NEP : float — net ecosystem φ balance
    """
    if phi_npp < 0.0:
        raise ValueError(f"phi_npp must be ≥ 0, got {phi_npp!r}")
    if phi_respiration < 0.0:
        raise ValueError(f"phi_respiration must be ≥ 0, got {phi_respiration!r}")
    if phi_disturbance < 0.0:
        raise ValueError(f"phi_disturbance must be ≥ 0, got {phi_disturbance!r}")
    return float(phi_npp - phi_respiration - phi_disturbance)


def atmospheric_co2_phi(co2_ppm: float, co2_ref: float = 280.0) -> float:
    """Atmospheric CO₂ φ relative to pre-industrial baseline.

    φ_CO2 = co2_ppm / co2_ref

    Parameters
    ----------
    co2_ppm : float — current CO₂ in ppm (must be > 0)
    co2_ref : float — pre-industrial reference (default 280, must be > 0)

    Returns
    -------
    phi_CO2 : float — normalised CO₂ φ
    """
    if co2_ppm <= 0.0:
        raise ValueError(f"co2_ppm must be > 0, got {co2_ppm!r}")
    if co2_ref <= 0.0:
        raise ValueError(f"co2_ref must be > 0, got {co2_ref!r}")
    return float(co2_ppm / co2_ref)


def methane_phi_forcing(ch4_ppb: float, ch4_ref: float = 722.0) -> float:
    """Radiative forcing from methane.

    ΔF_CH4 = 0.036 × (sqrt(ch4_ppb) − sqrt(ch4_ref))   W m⁻²

    Parameters
    ----------
    ch4_ppb : float — current CH₄ in ppb (must be > 0)
    ch4_ref : float — pre-industrial CH₄ ppb (default 722, must be > 0)

    Returns
    -------
    delta_F : float — radiative forcing W m⁻²
    """
    if ch4_ppb <= 0.0:
        raise ValueError(f"ch4_ppb must be > 0, got {ch4_ppb!r}")
    if ch4_ref <= 0.0:
        raise ValueError(f"ch4_ref must be > 0, got {ch4_ref!r}")
    import math
    return float(0.036 * (math.sqrt(ch4_ppb) - math.sqrt(ch4_ref)))


def carbon_budget_phi(emissions: float, ocean_sink: float,
                       land_sink: float) -> float:
    """Remaining atmospheric CO₂ after natural sinks.

    airborne = emissions − ocean_sink − land_sink

    Parameters
    ----------
    emissions  : float — anthropogenic carbon emissions GtC yr⁻¹ (must be ≥ 0)
    ocean_sink : float — ocean uptake GtC yr⁻¹ (must be ≥ 0)
    land_sink  : float — land uptake GtC yr⁻¹ (must be ≥ 0)

    Returns
    -------
    airborne : float — airborne fraction accumulating in atmosphere
    """
    if emissions < 0.0:
        raise ValueError(f"emissions must be ≥ 0, got {emissions!r}")
    if ocean_sink < 0.0:
        raise ValueError(f"ocean_sink must be ≥ 0, got {ocean_sink!r}")
    if land_sink < 0.0:
        raise ValueError(f"land_sink must be ≥ 0, got {land_sink!r}")
    return float(emissions - ocean_sink - land_sink)


def permafrost_phi_release(phi_permafrost: float, T_anomaly: float,
                            sensitivity: float = 0.02) -> float:
    """Carbon φ released from thawing permafrost.

    φ_release = phi_permafrost × sensitivity × max(0, T_anomaly)

    Parameters
    ----------
    phi_permafrost : float — permafrost carbon φ store (must be ≥ 0)
    T_anomaly      : float — temperature anomaly (K)
    sensitivity    : float — release sensitivity per K (must be ≥ 0)

    Returns
    -------
    phi_release : float — carbon φ released
    """
    if phi_permafrost < 0.0:
        raise ValueError(f"phi_permafrost must be ≥ 0, got {phi_permafrost!r}")
    if sensitivity < 0.0:
        raise ValueError(f"sensitivity must be ≥ 0, got {sensitivity!r}")
    return float(phi_permafrost * sensitivity * max(0.0, T_anomaly))


def deforestation_phi_loss(phi_forest: float, deforestation_rate: float) -> float:
    """Carbon φ lost per year from deforestation.

    φ_loss = phi_forest × deforestation_rate

    Parameters
    ----------
    phi_forest         : float — standing forest carbon φ (must be ≥ 0)
    deforestation_rate : float — annual fractional rate (must be ≥ 0)

    Returns
    -------
    phi_loss : float
    """
    if phi_forest < 0.0:
        raise ValueError(f"phi_forest must be ≥ 0, got {phi_forest!r}")
    if deforestation_rate < 0.0:
        raise ValueError(f"deforestation_rate must be ≥ 0, got {deforestation_rate!r}")
    return float(phi_forest * deforestation_rate)


def net_carbon_phi(phi_sources: float, phi_sinks: float) -> float:
    """Net atmospheric carbon φ balance.

    net = phi_sources − phi_sinks

    Parameters
    ----------
    phi_sources : float — total source φ (must be ≥ 0)
    phi_sinks   : float — total sink φ (must be ≥ 0)

    Returns
    -------
    net : float — net φ (positive = atmospheric accumulation)
    """
    if phi_sources < 0.0:
        raise ValueError(f"phi_sources must be ≥ 0, got {phi_sources!r}")
    if phi_sinks < 0.0:
        raise ValueError(f"phi_sinks must be ≥ 0, got {phi_sinks!r}")
    return float(phi_sources - phi_sinks)


def carbon_phi_feedback(delta_T: float, gamma: float = 20.0) -> float:
    """Climate-carbon feedback: additional CO₂ released per degree of warming.

    ΔC_feedback = gamma × delta_T   GtC K⁻¹

    Parameters
    ----------
    delta_T : float — temperature change (K)
    gamma   : float — carbon-climate feedback parameter (GtC K⁻¹, default 20)

    Returns
    -------
    delta_C : float — additional carbon φ released (GtC)
    """
    return float(gamma * delta_T)
