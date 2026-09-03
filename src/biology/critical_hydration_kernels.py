# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/biology/critical_hydration_kernels.py
=========================================
Critical-hydration exact kernel and model-dependent conversion helpers.

Promotion-safe scope:
    ε_r,crit = 1 / c_s²

Retained as executable but not promoted as exact theorem:
    Maxwell-Garnett conversion from dielectric threshold to water fraction /
    mass ratio, because that step depends on medium assumptions.
"""

from __future__ import annotations

from typing import Any, Dict

__all__ = [
    "BRAIDED_SOUND_SPEED",
    "DEFAULT_EPS_WATER",
    "DEFAULT_EPS_DRY",
    "critical_dielectric_from_sound_speed",
    "maxwell_garnett_effective_dielectric",
    "critical_water_volume_fraction",
    "water_mass_ratio_from_volume_fraction",
    "critical_hydration_kernel_report",
]

BRAIDED_SOUND_SPEED: float = 12.0 / 37.0
DEFAULT_EPS_WATER: float = 80.0
DEFAULT_EPS_DRY: float = 4.5


def critical_dielectric_from_sound_speed(sound_speed: float = BRAIDED_SOUND_SPEED) -> float:
    """Return the exact dielectric threshold 1/c_s²."""
    if sound_speed <= 0.0:
        raise ValueError(f"sound_speed must be > 0, got {sound_speed!r}")
    return 1.0 / (sound_speed * sound_speed)


def maxwell_garnett_effective_dielectric(
    water_fraction: float,
    eps_water: float = DEFAULT_EPS_WATER,
    eps_dry: float = DEFAULT_EPS_DRY,
) -> float:
    """Return the Maxwell-Garnett effective dielectric for a wet/dry mixture."""
    if not (0.0 <= water_fraction < 1.0):
        raise ValueError(f"water_fraction must be in [0,1), got {water_fraction!r}")
    if eps_water <= 0.0 or eps_dry <= 0.0:
        raise ValueError("dielectric constants must be positive")
    contrast = (eps_water - eps_dry) / (eps_water + 2.0 * eps_dry)
    numerator = 1.0 + 3.0 * water_fraction * contrast
    denominator = 1.0 - water_fraction * contrast
    if denominator <= 0.0:
        raise ValueError("mixture is outside the Maxwell-Garnett admissible range")
    return eps_dry * numerator / denominator


def critical_water_volume_fraction(
    eps_target: float | None = None,
    eps_water: float = DEFAULT_EPS_WATER,
    eps_dry: float = DEFAULT_EPS_DRY,
    steps: int = 120,
) -> float:
    """Solve for the water volume fraction reaching a target dielectric."""
    if eps_target is None:
        eps_target = critical_dielectric_from_sound_speed()
    if eps_target <= 0.0:
        raise ValueError("eps_target must be positive")
    low = maxwell_garnett_effective_dielectric(0.0, eps_water, eps_dry)
    high = maxwell_garnett_effective_dielectric(0.999999, eps_water, eps_dry)
    if not (low <= eps_target <= high):
        raise ValueError("target dielectric is not reachable with the supplied medium inputs")
    lo, hi = 0.0, 0.999999
    for _ in range(steps):
        mid = 0.5 * (lo + hi)
        if maxwell_garnett_effective_dielectric(mid, eps_water, eps_dry) < eps_target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def water_mass_ratio_from_volume_fraction(
    water_fraction: float,
    rho_water: float = 1.0,
    rho_dry: float = 1.3,
) -> float:
    """Convert a water volume fraction to g water / g dry."""
    if not (0.0 <= water_fraction < 1.0):
        raise ValueError(f"water_fraction must be in [0,1), got {water_fraction!r}")
    if rho_water <= 0.0 or rho_dry <= 0.0:
        raise ValueError("densities must be positive")
    dry_fraction = 1.0 - water_fraction
    return (water_fraction * rho_water) / (dry_fraction * rho_dry)


def critical_hydration_kernel_report() -> Dict[str, Any]:
    """Return the exact and model-dependent parts of the hydration lane."""
    eps_crit = critical_dielectric_from_sound_speed()
    volume_fraction = critical_water_volume_fraction(eps_target=eps_crit)
    return {
        "exact_kernel_status": "DERIVED_STRUCTURAL",
        "exact_kernel": {
            "formula": "ε_r,crit = 1 / c_s²",
            "c_s": BRAIDED_SOUND_SPEED,
            "eps_r_critical": eps_crit,
        },
        "model_dependent_prediction_status": "FALSIFIABLE_PREDICTION",
        "model_dependent_prediction": {
            "formula": "Maxwell-Garnett wet/dry effective dielectric",
            "eps_water": DEFAULT_EPS_WATER,
            "eps_dry": DEFAULT_EPS_DRY,
            "critical_water_fraction": volume_fraction,
            "critical_mass_ratio_g_per_g": water_mass_ratio_from_volume_fraction(volume_fraction),
        },
        "honest_note": (
            "Only the dielectric threshold is exact. Water-fraction and mass-ratio "
            "predictions remain medium-dependent and are kept as executable "
            "prediction helpers rather than promoted theorem claims."
        ),
    }
