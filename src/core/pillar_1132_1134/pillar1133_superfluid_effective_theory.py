# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1133: a bounded Bogoliubov toolkit for a dilute Bose gas.

🔵 ADJACENT TRACK — NOT A HARDGATE PHYSICS CLAIM

This module implements the zero-temperature, homogeneous, three-dimensional,
weakly interacting Bose-gas dispersion in SI units. It is not the relativistic
equation-of-state EFT of Son, a superfluid-dark-matter model, or a derived
connection to the Unitary Manifold.
"""

from __future__ import annotations

import math
from numbers import Real

PILLAR_NUMBER = 1133
PILLAR_GATE = "SUPERFLUID_EFFECTIVE_THEORY_REFERENCE_CALCULATION"
PILLAR_STATUS = "BOGOLIUBOV_DILUTE_GAS_REFERENCE_CALCULATION"
ADJACENT_TRACK_LABEL = "🔵 ADJACENT TRACK — NOT A HARDGATE PHYSICS CLAIM"

# CODATA 2018 value, in J s. Precision is more than adequate for this
# leading-order reference calculation.
HBAR_J_S = 1.054571817e-34


def _finite_real(name: str, value: Real) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")
    try:
        converted = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} must be finite") from exc
    if not math.isfinite(converted):
        raise ValueError(f"{name} must be finite")
    return converted


def _validate_gas_parameters(
    particle_mass_kg: Real,
    number_density_m3: Real,
    scattering_length_m: Real,
) -> tuple[float, float, float]:
    mass = _finite_real("particle_mass_kg", particle_mass_kg)
    density = _finite_real("number_density_m3", number_density_m3)
    scattering_length = _finite_real("scattering_length_m", scattering_length_m)
    if mass <= 0.0:
        raise ValueError("particle_mass_kg must be positive")
    if density < 0.0:
        raise ValueError("number_density_m3 must be non-negative")
    if scattering_length < 0.0:
        raise ValueError("scattering_length_m must be non-negative")
    return mass, density, scattering_length


def bogoliubov_energy_joule(
    wave_number_m_inv: Real,
    particle_mass_kg: Real,
    number_density_m3: Real,
    scattering_length_m: Real,
) -> float:
    """Return the Bogoliubov quasiparticle energy in joules.

    Convention and regime: a uniform 3D Bose gas at zero temperature with
    repulsive, short-range s-wave interactions, treated at leading
    Bogoliubov/mean-field order. The contact coupling is
    ``g = 4*pi*HBAR_J_S**2*scattering_length_m/particle_mass_kg`` (J m^3),
    ``epsilon_k = HBAR_J_S**2*k**2/(2*m)``, and
    ``E_k = sqrt(epsilon_k*(epsilon_k + 2*g*n))``. Here ``k`` is the
    magnitude of the wave vector (rad/m convention, numerically m^-1).

    ``k >= 0``, ``m > 0``, ``n >= 0`` and ``a_s >= 0`` are required. The
    zero-density or zero-scattering-length limit reduces to a free particle.
    """
    wave_number = _finite_real("wave_number_m_inv", wave_number_m_inv)
    mass, density, scattering_length = _validate_gas_parameters(
        particle_mass_kg, number_density_m3, scattering_length_m
    )
    if wave_number < 0.0:
        raise ValueError("wave_number_m_inv must be non-negative")

    try:
        epsilon_k = HBAR_J_S**2 * wave_number**2 / (2.0 * mass)
        interaction_energy = (
            4.0 * math.pi * HBAR_J_S**2 * scattering_length * density / mass
        )
        energy = math.sqrt(epsilon_k) * math.sqrt(
            epsilon_k + 2.0 * interaction_energy
        )
    except (OverflowError, ValueError, ZeroDivisionError) as exc:
        raise ValueError("parameters exceed the finite range of this calculation") from exc
    if not math.isfinite(energy):
        raise ValueError("parameters exceed the finite range of this calculation")
    return energy


def bogoliubov_angular_frequency_rad_s(
    wave_number_m_inv: Real,
    particle_mass_kg: Real,
    number_density_m3: Real,
    scattering_length_m: Real,
) -> float:
    """Return ``E_k / hbar`` in radians per second."""
    frequency = bogoliubov_energy_joule(
        wave_number_m_inv,
        particle_mass_kg,
        number_density_m3,
        scattering_length_m,
    ) / HBAR_J_S
    if not math.isfinite(frequency):
        raise ValueError("parameters exceed the finite range of this calculation")
    return frequency


def bogoliubov_sound_speed_m_s(
    particle_mass_kg: Real,
    number_density_m3: Real,
    scattering_length_m: Real,
) -> float:
    """Return the long-wavelength mean-field sound speed in m/s.

    The value is ``sqrt(g*n/m)`` under the same contact-interaction
    assumptions as :func:`bogoliubov_energy_joule`. It is zero when ``n`` or
    ``a_s`` is zero.
    """
    mass, density, scattering_length = _validate_gas_parameters(
        particle_mass_kg, number_density_m3, scattering_length_m
    )
    try:
        speed = math.sqrt(
            4.0 * math.pi * HBAR_J_S**2 * scattering_length * density / mass**2
        )
    except (OverflowError, ValueError, ZeroDivisionError) as exc:
        raise ValueError("parameters exceed the finite range of this calculation") from exc
    if not math.isfinite(speed):
        raise ValueError("parameters exceed the finite range of this calculation")
    return speed


__all__ = [
    "ADJACENT_TRACK_LABEL",
    "HBAR_J_S",
    "PILLAR_GATE",
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "bogoliubov_angular_frequency_rad_s",
    "bogoliubov_energy_joule",
    "bogoliubov_sound_speed_m_s",
]
