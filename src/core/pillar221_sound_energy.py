# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/pillar221_sound_energy.py
==================================
Pillar 221 — Sound and Sound Energy: physics, utility, and control.

Adjacent applied research track (non-hardgate): rigorous acoustics models for
signal transfer, power transfer, safety bounds, and engineering use-cases.
"""
from __future__ import annotations

import math

__provenance__ = {
    "pillar": 221,
    "title": "Sound and Sound Energy: physics, utility, and control",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": "ADJACENT RESEARCH TRACK — acoustics engineering and safety",
}

__all__ = [
    "N_W",
    "K_CS",
    "PHI0",
    "BRAIDED_SOUND_SPEED",
    "SOUND_SPEED_AIR_20C",
    "SOUND_SPEED_WATER_20C",
    "SOUND_SPEED_SOFT_TISSUE",
    "AIR_DENSITY_20C",
    "WATER_DENSITY_20C",
    "REFERENCE_PRESSURE_PA",
    "FDA_MECHANICAL_INDEX_LIMIT",
    "spl_from_pressure_rms",
    "pressure_rms_from_spl",
    "acoustic_intensity_from_spl",
    "acoustic_radiation_force",
    "piezoelectric_harvested_power",
    "ultrasound_attenuation",
    "cavitation_mechanical_index",
    "ultrasound_safety_window",
    "sound_energy_use_cases",
    "sound_energy_use_matrix",
    "pillar221_summary",
]

# ---------------------------------------------------------------------------
# Core manifold constants
# ---------------------------------------------------------------------------
N_W: int = 5
K_CS: int = 74
PHI0: float = 0.739085
BRAIDED_SOUND_SPEED: float = 12 / 37

# ---------------------------------------------------------------------------
# Physical constants / references
# ---------------------------------------------------------------------------
SOUND_SPEED_AIR_20C: float = 343.0
SOUND_SPEED_WATER_20C: float = 1482.0
SOUND_SPEED_SOFT_TISSUE: float = 1540.0
AIR_DENSITY_20C: float = 1.204
WATER_DENSITY_20C: float = 997.0
REFERENCE_PRESSURE_PA: float = 20e-6
FDA_MECHANICAL_INDEX_LIMIT: float = 1.9


def spl_from_pressure_rms(pressure_pa: float, pref_pa: float = REFERENCE_PRESSURE_PA) -> float:
    """Return SPL (dB re 20 µPa) from RMS pressure in pascals."""
    if pressure_pa <= 0:
        raise ValueError("pressure_pa must be positive.")
    if pref_pa <= 0:
        raise ValueError("pref_pa must be positive.")
    return 20.0 * math.log10(pressure_pa / pref_pa)


def pressure_rms_from_spl(spl_db: float, pref_pa: float = REFERENCE_PRESSURE_PA) -> float:
    """Return RMS pressure [Pa] from SPL in dB."""
    if pref_pa <= 0:
        raise ValueError("pref_pa must be positive.")
    return pref_pa * (10.0 ** (spl_db / 20.0))


def acoustic_intensity_from_spl(
    spl_db: float,
    medium_density_kg_m3: float = AIR_DENSITY_20C,
    sound_speed_m_s: float = SOUND_SPEED_AIR_20C,
) -> dict:
    """Compute plane-wave acoustic intensity from SPL."""
    if medium_density_kg_m3 <= 0:
        raise ValueError("medium_density_kg_m3 must be positive.")
    if sound_speed_m_s <= 0:
        raise ValueError("sound_speed_m_s must be positive.")

    p_rms = pressure_rms_from_spl(spl_db)
    intensity = (p_rms**2) / (medium_density_kg_m3 * sound_speed_m_s)
    return {
        "spl_db": spl_db,
        "pressure_rms_pa": p_rms,
        "intensity_w_m2": intensity,
        "acoustic_impedance_rayl": medium_density_kg_m3 * sound_speed_m_s,
    }


def acoustic_radiation_force(
    intensity_w_m2: float,
    target_area_m2: float,
    reflectivity: float = 1.0,
    sound_speed_m_s: float = SOUND_SPEED_WATER_20C,
) -> dict:
    """Estimate acoustic radiation force using momentum flux balance."""
    if intensity_w_m2 < 0:
        raise ValueError("intensity_w_m2 must be non-negative.")
    if target_area_m2 < 0:
        raise ValueError("target_area_m2 must be non-negative.")
    if not 0.0 <= reflectivity <= 1.0:
        raise ValueError("reflectivity must be in [0, 1].")
    if sound_speed_m_s <= 0:
        raise ValueError("sound_speed_m_s must be positive.")

    # Radiation pressure P_rad ≈ (1 + R) I / c
    radiation_pressure = (1.0 + reflectivity) * intensity_w_m2 / sound_speed_m_s
    force = radiation_pressure * target_area_m2
    return {
        "radiation_pressure_pa": radiation_pressure,
        "force_newton": force,
        "intensity_w_m2": intensity_w_m2,
        "target_area_m2": target_area_m2,
    }


def piezoelectric_harvested_power(
    spl_db: float,
    transducer_area_m2: float,
    conversion_efficiency: float,
    medium_density_kg_m3: float = AIR_DENSITY_20C,
    sound_speed_m_s: float = SOUND_SPEED_AIR_20C,
) -> dict:
    """Estimate electrical power harvested from incident acoustic energy."""
    if transducer_area_m2 < 0:
        raise ValueError("transducer_area_m2 must be non-negative.")
    if not 0.0 <= conversion_efficiency <= 1.0:
        raise ValueError("conversion_efficiency must be in [0, 1].")

    acoustic = acoustic_intensity_from_spl(spl_db, medium_density_kg_m3, sound_speed_m_s)
    incident_power = acoustic["intensity_w_m2"] * transducer_area_m2
    harvested = incident_power * conversion_efficiency
    return {
        "spl_db": spl_db,
        "incident_power_w": incident_power,
        "harvested_power_w": harvested,
        "conversion_efficiency": conversion_efficiency,
    }


def ultrasound_attenuation(
    center_frequency_mhz: float,
    propagation_depth_cm: float,
    attenuation_db_cm_mhz: float = 0.5,
) -> dict:
    """Attenuation model: loss[dB] = α[f MHz][depth cm], typical soft tissue α≈0.5."""
    if center_frequency_mhz <= 0:
        raise ValueError("center_frequency_mhz must be positive.")
    if propagation_depth_cm < 0:
        raise ValueError("propagation_depth_cm must be non-negative.")
    if attenuation_db_cm_mhz < 0:
        raise ValueError("attenuation_db_cm_mhz must be non-negative.")

    total_loss_db = attenuation_db_cm_mhz * center_frequency_mhz * propagation_depth_cm
    transmitted_fraction = 10.0 ** (-total_loss_db / 10.0)
    return {
        "center_frequency_mhz": center_frequency_mhz,
        "propagation_depth_cm": propagation_depth_cm,
        "total_loss_db": total_loss_db,
        "transmitted_fraction": transmitted_fraction,
    }


def cavitation_mechanical_index(
    peak_negative_pressure_mpa: float,
    center_frequency_mhz: float,
) -> dict:
    """Compute ultrasound mechanical index MI = P_neg / sqrt(f_MHz)."""
    if peak_negative_pressure_mpa < 0:
        raise ValueError("peak_negative_pressure_mpa must be non-negative.")
    if center_frequency_mhz <= 0:
        raise ValueError("center_frequency_mhz must be positive.")

    mi = peak_negative_pressure_mpa / math.sqrt(center_frequency_mhz)
    return {
        "mechanical_index": mi,
        "peak_negative_pressure_mpa": peak_negative_pressure_mpa,
        "center_frequency_mhz": center_frequency_mhz,
        "fda_limit": FDA_MECHANICAL_INDEX_LIMIT,
        "within_diagnostic_limit": mi <= FDA_MECHANICAL_INDEX_LIMIT,
    }


def ultrasound_safety_window(
    center_frequency_mhz: float,
    peak_negative_pressure_mpa: float,
    depth_cm: float,
) -> dict:
    """Combine attenuation and MI constraints into a practical safety assessment."""
    attenuation = ultrasound_attenuation(center_frequency_mhz, depth_cm)
    mi = cavitation_mechanical_index(peak_negative_pressure_mpa, center_frequency_mhz)
    effective_pressure_mpa = peak_negative_pressure_mpa * math.sqrt(attenuation["transmitted_fraction"])
    effective_mi = effective_pressure_mpa / math.sqrt(center_frequency_mhz)
    return {
        "input_mi": mi["mechanical_index"],
        "effective_mi_at_depth": effective_mi,
        "diagnostic_limit_mi": FDA_MECHANICAL_INDEX_LIMIT,
        "within_limit_at_depth": effective_mi <= FDA_MECHANICAL_INDEX_LIMIT,
        "attenuation_total_loss_db": attenuation["total_loss_db"],
    }


def sound_energy_use_cases() -> list[dict]:
    """Return rigor-focused mapping of major sound-energy applications."""
    return [
        {
            "domain": "medical_imaging",
            "primary_mechanism": "echo-based impedance contrast (ultrasound)",
            "typical_band": "1–15 MHz",
            "value": "real-time, non-ionizing imaging",
            "key_limit": "attenuation and acoustic-window dependence",
        },
        {
            "domain": "therapy_and_surgery",
            "primary_mechanism": "focused ultrasound heating / cavitation",
            "typical_band": "0.5–3 MHz",
            "value": "non-invasive ablation and neuromodulation research",
            "key_limit": "thermal and cavitation safety boundaries",
        },
        {
            "domain": "energy_harvesting",
            "primary_mechanism": "piezoelectric conversion of vibration/sound",
            "typical_band": "10 Hz–100 kHz",
            "value": "low-power autonomous sensors",
            "key_limit": "low power density outside resonance",
        },
        {
            "domain": "materials_and_nanocontrol",
            "primary_mechanism": "acoustic radiation force and microstreaming",
            "typical_band": "100 kHz–10 MHz",
            "value": "particle sorting, acoustic tweezers, mixing",
            "key_limit": "precision degrades with turbulence and heterogeneity",
        },
    ]


def sound_energy_use_matrix() -> list[dict]:
    """Backward-compatible alias for sound_energy_use_cases()."""
    return sound_energy_use_cases()


def pillar221_summary() -> dict:
    """Summary of key quantitative results for Pillar 221."""
    speech = acoustic_intensity_from_spl(60.0)
    industrial = piezoelectric_harvested_power(100.0, 0.01, 0.35)
    diagnostic = ultrasound_safety_window(
        center_frequency_mhz=3.0,
        peak_negative_pressure_mpa=1.2,
        depth_cm=5.0,
    )
    return {
        "pillar": 221,
        "title": "Sound and Sound Energy: physics, utility, and control",
        "status": "ADJACENT RESEARCH TRACK — acoustics engineering and safety",
        "speech_intensity_w_m2_at_60db": speech["intensity_w_m2"],
        "harvested_power_w_at_100db_1e2cm2": industrial["harvested_power_w"],
        "diagnostic_effective_mi_example": diagnostic["effective_mi_at_depth"],
        "diagnostic_within_limit_example": diagnostic["within_limit_at_depth"],
        "epistemic_note": (
            "Acoustics and safety equations are standard engineering models. "
            "Clinical deployment always requires protocol-level regulatory validation."
        ),
    }
