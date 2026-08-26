# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
from __future__ import annotations

import numpy as np

from .constants import (
    AREA_TO_ENTROPY_RATIO,
    BETA_CEILING,
    BETA_FLOOR,
    BETA_FORBIDDEN_HIGH,
    BETA_FORBIDDEN_LOW,
    BETA_HIGH,
    BETA_LOW,
    BOUNDARY_POINT_COUNT,
    BRAID_PARTNER,
    BRAIDED_SOUND_SPEED,
    CMB_BICEP_KECK_BOUND,
    CMB_X_RANGE,
    CMB_Y_RANGE,
    HOLOGRAPHIC_RADIUS,
    KK_MODE_COUNT,
    K_CS,
    N_S,
    PENROSE_ENTROPY_RATIO,
    PHI_0,
    PHI_MAX,
    PHI_MIN,
    PLANCK_CENTER,
    R_BRAIDED,
    WINDING_NUMBER,
    XI_C,
)


def generate_cmb_plane_data(scatter: np.ndarray | None = None) -> dict[str, np.ndarray | float]:
    x_ticks = np.linspace(CMB_X_RANGE[0], CMB_X_RANGE[1], 6)
    y_ticks = np.linspace(CMB_Y_RANGE[0], CMB_Y_RANGE[1], 5)
    default_scatter = np.array(
        [
            [0.9585, 0.0290],
            [0.9608, 0.0240],
            [0.9621, 0.0200],
            [0.9654, 0.0270],
            [0.9670, 0.0130],
            [0.9690, 0.0090],
        ],
        dtype=float,
    )
    points = default_scatter if scatter is None else np.asarray(scatter, dtype=float)
    return {
        "x_range": CMB_X_RANGE.copy(),
        "y_range": CMB_Y_RANGE.copy(),
        "x_ticks": x_ticks,
        "y_ticks": y_ticks,
        "planck_center": PLANCK_CENTER.copy(),
        "planck_radii": np.array([0.0045, 0.0090], dtype=float),
        "bicep_keck_bound": float(CMB_BICEP_KECK_BOUND),
        "prediction": np.array([N_S, R_BRAIDED], dtype=float),
        "scatter": points,
    }


def generate_birefringence_window_data() -> dict[str, np.ndarray | float]:
    predictions = np.array([BETA_LOW, BETA_HIGH], dtype=float)
    admissible_window = np.array([BETA_FLOOR, BETA_CEILING], dtype=float)
    forbidden_gap = np.array([BETA_FORBIDDEN_LOW, BETA_FORBIDDEN_HIGH], dtype=float)
    return {
        "axis_range": np.array([0.20, 0.40], dtype=float),
        "tick_values": np.linspace(0.20, 0.40, 11),
        "admissible_window": admissible_window,
        "forbidden_gap": forbidden_gap,
        "predictions": predictions,
        "predictions_in_bounds": (predictions >= admissible_window[0]) & (predictions <= admissible_window[1]),
        "predictions_outside_gap": (predictions < forbidden_gap[0]) | (predictions > forbidden_gap[1]),
    }


def generate_kk_tower_data(num_modes: int = KK_MODE_COUNT) -> dict[str, np.ndarray]:
    modes = np.arange(1, num_modes + 1, dtype=int)
    amplitudes = 1.0 / np.square(modes.astype(float))
    return {
        "modes": modes,
        "amplitudes": amplitudes,
        "masses": modes.astype(float),
        "normalized_amplitudes": amplitudes / amplitudes[0],
    }


def generate_winding_mode_data(num_samples: int = 321) -> dict[str, np.ndarray | int | float]:
    phase = np.linspace(0.0, 1.0, num_samples)
    angle = 2.0 * np.pi * WINDING_NUMBER * phase
    primary = np.sin(angle)
    companion = 0.82 * np.sin(angle + np.pi)
    return {
        "phase": phase,
        "primary_mode": primary,
        "companion_mode": companion,
        "mode_numbers": np.arange(1, WINDING_NUMBER + 1, dtype=int),
        "active_mode": WINDING_NUMBER,
        "braid_partner": BRAID_PARTNER,
        "k_cs": float(K_CS),
    }


def generate_phi_landscape_data(num_points: int = 401) -> dict[str, np.ndarray | float | int]:
    phi = np.linspace(PHI_MIN, PHI_MAX, num_points)
    delta = phi - PHI_0
    potential = delta**2 + 0.15 * delta**4
    gradient = 2.0 * delta + 0.60 * delta**3
    minimum_index = int(np.argmin(potential))
    return {
        "phi": phi,
        "potential": potential,
        "gradient": gradient,
        "minimum_index": minimum_index,
        "minimum_phi": float(phi[minimum_index]),
        "minimum_value": float(potential[minimum_index]),
        "phi_0": float(PHI_0),
    }


def generate_penrose_entropy_data(masses: np.ndarray | None = None) -> dict[str, np.ndarray]:
    mass_values = np.linspace(0.5, 5.0, 10) if masses is None else np.asarray(masses, dtype=float)
    areas = 16.0 * np.pi * np.square(mass_values)
    entropy = PENROSE_ENTROPY_RATIO * areas
    return {
        "masses": mass_values,
        "areas": areas,
        "entropy": entropy,
        "entropy_to_area_ratio": np.full_like(mass_values, PENROSE_ENTROPY_RATIO, dtype=float),
        "area_to_entropy_ratio": np.full_like(mass_values, AREA_TO_ENTROPY_RATIO, dtype=float),
    }


def generate_holographic_boundary_data(
    radius: float = HOLOGRAPHIC_RADIUS,
    num_points: int = BOUNDARY_POINT_COUNT,
) -> dict[str, np.ndarray | float]:
    theta = np.linspace(0.0, 2.0 * np.pi, num_points, endpoint=False)
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    area = 4.0 * np.pi * radius**2
    entropy = PENROSE_ENTROPY_RATIO * area
    return {
        "theta": theta,
        "boundary_x": x,
        "boundary_y": y,
        "radius": float(radius),
        "area": float(area),
        "entropy": float(entropy),
        "entropy_to_area_ratio": float(entropy / area),
        "area_to_entropy_ratio": float(area / entropy),
    }


def generate_braided_sound_speed_data(num_points: int = 120) -> dict[str, np.ndarray | float]:
    wave_number = np.linspace(0.0, 12.0, num_points)
    angular_frequency = BRAIDED_SOUND_SPEED * wave_number
    phase_velocity = np.full_like(wave_number, BRAIDED_SOUND_SPEED, dtype=float)
    group_velocity = np.full_like(wave_number, BRAIDED_SOUND_SPEED, dtype=float)
    return {
        "wave_number": wave_number,
        "angular_frequency": angular_frequency,
        "phase_velocity": phase_velocity,
        "group_velocity": group_velocity,
        "c_s": float(BRAIDED_SOUND_SPEED),
        "xi_c": float(XI_C),
    }


VISUALIZATION_FUNCTIONS = {
    "cmb": generate_cmb_plane_data,
    "birefringence": generate_birefringence_window_data,
    "kk_tower": generate_kk_tower_data,
    "winding_mode": generate_winding_mode_data,
    "phi_landscape": generate_phi_landscape_data,
    "penrose_entropy": generate_penrose_entropy_data,
    "holographic_boundary": generate_holographic_boundary_data,
    "braided_sound_speed": generate_braided_sound_speed_data,
}

__all__ = [
    "generate_cmb_plane_data",
    "generate_birefringence_window_data",
    "generate_kk_tower_data",
    "generate_winding_mode_data",
    "generate_phi_landscape_data",
    "generate_penrose_entropy_data",
    "generate_holographic_boundary_data",
    "generate_braided_sound_speed_data",
    "VISUALIZATION_FUNCTIONS",
]
