# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/pillar222_nanotechnology_control_systems.py
=====================================================
Pillar 222 — Nanotechnology and Control Systems.

Adjacent applied research track (non-hardgate): nanoscale transport models,
closed-loop control metrics, and deployment-readiness quantification.
"""
from __future__ import annotations

import math

__provenance__ = {
    "pillar": 222,
    "title": "Nanotechnology and Control Systems",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": "ADJACENT RESEARCH TRACK — nanosystems engineering",
}

__all__ = [
    "N_W",
    "K_CS",
    "PHI0",
    "BRAIDED_SOUND_SPEED",
    "BOLTZMANN_SI",
    "BODY_TEMPERATURE_K",
    "WATER_VISCOSITY_BODY_PA_S",
    "stokes_einstein_diffusion",
    "nanoparticle_diffusion_time",
    "first_order_nano_release",
    "pid_nano_positioning",
    "nanosensor_snr_db",
    "nanotech_control_readiness",
    "pillar222_summary",
]

N_W: int = 5
K_CS: int = 74
PHI0: float = 0.739085
BRAIDED_SOUND_SPEED: float = 12 / 37

BOLTZMANN_SI: float = 1.380649e-23
BODY_TEMPERATURE_K: float = 310.15
WATER_VISCOSITY_BODY_PA_S: float = 0.0007


def stokes_einstein_diffusion(
    radius_nm: float,
    temperature_k: float = BODY_TEMPERATURE_K,
    viscosity_pa_s: float = WATER_VISCOSITY_BODY_PA_S,
) -> dict:
    """Diffusion coefficient from Stokes-Einstein relation."""
    if radius_nm <= 0:
        raise ValueError("radius_nm must be positive.")
    if temperature_k <= 0:
        raise ValueError("temperature_k must be positive.")
    if viscosity_pa_s <= 0:
        raise ValueError("viscosity_pa_s must be positive.")

    radius_m = radius_nm * 1e-9
    diffusion = BOLTZMANN_SI * temperature_k / (6.0 * math.pi * viscosity_pa_s * radius_m)
    return {
        "radius_nm": radius_nm,
        "temperature_k": temperature_k,
        "viscosity_pa_s": viscosity_pa_s,
        "diffusion_m2_s": diffusion,
    }


def nanoparticle_diffusion_time(
    distance_um: float,
    radius_nm: float,
    temperature_k: float = BODY_TEMPERATURE_K,
    viscosity_pa_s: float = WATER_VISCOSITY_BODY_PA_S,
) -> dict:
    """Estimate mean diffusion time t≈x²/(2D) over a 1D characteristic length."""
    if distance_um < 0:
        raise ValueError("distance_um must be non-negative.")

    diffusion = stokes_einstein_diffusion(radius_nm, temperature_k, viscosity_pa_s)
    distance_m = distance_um * 1e-6
    D = diffusion["diffusion_m2_s"]
    time_s = (distance_m**2) / (2.0 * max(D, 1e-30))
    return {
        "distance_um": distance_um,
        "radius_nm": radius_nm,
        "diffusion_m2_s": D,
        "diffusion_time_s": time_s,
    }


def first_order_nano_release(initial_load_mg: float, half_life_h: float, time_h: float) -> dict:
    """First-order release/clearance model for nano-delivered payloads."""
    if initial_load_mg < 0:
        raise ValueError("initial_load_mg must be non-negative.")
    if half_life_h <= 0:
        raise ValueError("half_life_h must be positive.")
    if time_h < 0:
        raise ValueError("time_h must be non-negative.")

    rate = math.log(2.0) / half_life_h
    remaining = initial_load_mg * math.exp(-rate * time_h)
    released = initial_load_mg - remaining
    return {
        "initial_load_mg": initial_load_mg,
        "half_life_h": half_life_h,
        "time_h": time_h,
        "remaining_mg": remaining,
        "released_mg": released,
        "released_fraction": released / initial_load_mg if initial_load_mg > 0 else 0.0,
    }


def pid_nano_positioning(
    setpoint_nm: float,
    kp: float,
    ki: float,
    kd: float,
    disturbance_nm: float = 0.0,
    dt_ms: float = 0.1,
    tau_ms: float = 1.0,
    steps: int = 2000,
) -> dict:
    """Discrete PID simulation for nanoscale stage positioning."""
    if setpoint_nm < 0:
        raise ValueError("setpoint_nm must be non-negative.")
    if kp < 0 or ki < 0 or kd < 0:
        raise ValueError("kp, ki, kd must be non-negative.")
    if dt_ms <= 0:
        raise ValueError("dt_ms must be positive.")
    if tau_ms <= 0:
        raise ValueError("tau_ms must be positive.")
    if steps < 1:
        raise ValueError("steps must be >= 1.")

    dt = dt_ms
    tau = tau_ms
    x = 0.0
    integral = 0.0
    prev_error = setpoint_nm
    abs_errors = []
    max_x = x
    settling_time_ms: float | None = None
    settle_tol = max(0.1, 0.01 * max(setpoint_nm, 1.0))
    settle_window = max(20, int(0.02 * steps))

    for i in range(steps):
        error = setpoint_nm - x
        integral += error * dt
        derivative = (error - prev_error) / dt
        control = kp * error + ki * integral + kd * derivative

        # First-order stage dynamics: dx/dt = (u + d - x) / tau
        x += dt * ((control + disturbance_nm - x) / tau)
        prev_error = error
        max_x = max(max_x, x)
        abs_errors.append(abs(error))

        if i >= settle_window and settling_time_ms is None:
            tail = abs_errors[i - settle_window:i]
            if tail and max(tail) <= settle_tol:
                settling_time_ms = i * dt_ms

    final_error = setpoint_nm - x
    rmse = math.sqrt(sum(e * e for e in abs_errors) / len(abs_errors))
    overshoot = max(0.0, max_x - setpoint_nm)
    return {
        "setpoint_nm": setpoint_nm,
        "final_position_nm": x,
        "final_error_nm": final_error,
        "rmse_nm": rmse,
        "overshoot_nm": overshoot,
        "settling_time_ms": settling_time_ms,
    }


def nanosensor_snr_db(signal_amplitude: float, noise_rms: float) -> float:
    """Signal-to-noise ratio in decibels."""
    if signal_amplitude < 0:
        raise ValueError("signal_amplitude must be non-negative.")
    if noise_rms <= 0:
        raise ValueError("noise_rms must be positive.")
    if signal_amplitude == 0:
        return float("-inf")
    return 20.0 * math.log10(signal_amplitude / noise_rms)


def nanotech_control_readiness(
    precision_nm: float,
    settling_time_ms: float,
    snr_db: float,
    cytotoxicity_index: float,
) -> dict:
    """Heuristic readiness score integrating control, sensing, and bio-safety."""
    if precision_nm < 0:
        raise ValueError("precision_nm must be non-negative.")
    if settling_time_ms < 0:
        raise ValueError("settling_time_ms must be non-negative.")
    if not 0.0 <= cytotoxicity_index <= 1.0:
        raise ValueError("cytotoxicity_index must be in [0, 1].")

    precision_score = math.exp(-precision_nm / 10.0)
    settling_score = math.exp(-settling_time_ms / 50.0)
    snr_score = 1.0 / (1.0 + math.exp(-(snr_db - 20.0) / 5.0))
    safety_score = 1.0 - cytotoxicity_index
    readiness = 0.30 * precision_score + 0.25 * settling_score + 0.25 * snr_score + 0.20 * safety_score
    return {
        "readiness_score": max(0.0, min(1.0, readiness)),
        "precision_score": precision_score,
        "settling_score": settling_score,
        "snr_score": snr_score,
        "safety_score": safety_score,
    }


def pillar222_summary() -> dict:
    """Summary snapshot for Pillar 222."""
    diff = stokes_einstein_diffusion(50.0)
    travel = nanoparticle_diffusion_time(100.0, 50.0)
    pid = pid_nano_positioning(setpoint_nm=25.0, kp=0.4, ki=12.0, kd=0.0005)
    readiness = nanotech_control_readiness(
        precision_nm=abs(pid["final_error_nm"]),
        settling_time_ms=pid["settling_time_ms"] or 1e6,
        snr_db=35.0,
        cytotoxicity_index=0.08,
    )
    return {
        "pillar": 222,
        "title": "Nanotechnology and Control Systems",
        "status": "ADJACENT RESEARCH TRACK — nanosystems engineering",
        "diffusion_m2_s_at_50nm": diff["diffusion_m2_s"],
        "diffusion_time_s_100um_50nm": travel["diffusion_time_s"],
        "pid_rmse_nm_example": pid["rmse_nm"],
        "readiness_score_example": readiness["readiness_score"],
        "epistemic_note": (
            "Transport and control equations are standard approximations; "
            "clinical/industrial deployment requires platform-specific calibration."
        ),
    }
