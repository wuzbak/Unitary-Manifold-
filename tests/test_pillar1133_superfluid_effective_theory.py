# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import math

import pytest

from src.core.pillar1133_superfluid_effective_theory import (
    ADJACENT_TRACK_LABEL,
    HBAR_J_S,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    bogoliubov_angular_frequency_rad_s,
    bogoliubov_energy_joule,
    bogoliubov_sound_speed_m_s,
)


MASS_KG = 6.6464764e-27
DENSITY_M3 = 1.0e20
SCATTERING_LENGTH_M = 5.1e-9


def test_pillar_identity_and_adjacent_track_scope() -> None:
    assert PILLAR_NUMBER == 1133
    assert PILLAR_GATE == "SUPERFLUID_EFFECTIVE_THEORY_REFERENCE_CALCULATION"
    assert PILLAR_STATUS == "BOGOLIUBOV_DILUTE_GAS_REFERENCE_CALCULATION"
    assert ADJACENT_TRACK_LABEL == "🔵 ADJACENT TRACK — NOT A HARDGATE PHYSICS CLAIM"


def test_bogoliubov_dispersion_matches_declared_si_formula() -> None:
    wave_number = 2.0e6
    coupling = (
        4.0
        * math.pi
        * HBAR_J_S**2
        * SCATTERING_LENGTH_M
        / MASS_KG
    )
    epsilon_k = HBAR_J_S**2 * wave_number**2 / (2.0 * MASS_KG)
    expected = math.sqrt(epsilon_k * (epsilon_k + 2.0 * coupling * DENSITY_M3))

    assert bogoliubov_energy_joule(
        wave_number, MASS_KG, DENSITY_M3, SCATTERING_LENGTH_M
    ) == pytest.approx(expected, rel=1e-14)


@pytest.mark.parametrize(
    ("density", "scattering_length"),
    [(0.0, SCATTERING_LENGTH_M), (DENSITY_M3, 0.0), (0.0, 0.0)],
)
def test_zero_interaction_limit_is_free_particle(
    density: float, scattering_length: float
) -> None:
    wave_number = 4.0e7
    free_particle_energy = HBAR_J_S**2 * wave_number**2 / (2.0 * MASS_KG)
    assert bogoliubov_energy_joule(
        wave_number, MASS_KG, density, scattering_length
    ) == pytest.approx(free_particle_energy, rel=1e-14)
    assert bogoliubov_sound_speed_m_s(
        MASS_KG, density, scattering_length
    ) == 0.0


def test_zero_wave_number_is_gapless() -> None:
    assert bogoliubov_energy_joule(
        0.0, MASS_KG, DENSITY_M3, SCATTERING_LENGTH_M
    ) == 0.0


def test_long_wavelength_limit_matches_mean_field_sound_speed() -> None:
    wave_number = 1.0e2
    energy = bogoliubov_energy_joule(
        wave_number, MASS_KG, DENSITY_M3, SCATTERING_LENGTH_M
    )
    speed = bogoliubov_sound_speed_m_s(
        MASS_KG, DENSITY_M3, SCATTERING_LENGTH_M
    )
    assert energy / (HBAR_J_S * wave_number) == pytest.approx(speed, rel=1e-7)


def test_angular_frequency_obeys_planck_relation() -> None:
    wave_number = 3.0e6
    energy = bogoliubov_energy_joule(
        wave_number, MASS_KG, DENSITY_M3, SCATTERING_LENGTH_M
    )
    angular_frequency = bogoliubov_angular_frequency_rad_s(
        wave_number, MASS_KG, DENSITY_M3, SCATTERING_LENGTH_M
    )
    assert HBAR_J_S * angular_frequency == pytest.approx(energy, rel=1e-15)


def test_angular_frequency_rejects_overflow() -> None:
    with pytest.raises(ValueError, match="finite range"):
        bogoliubov_angular_frequency_rad_s(
            1.0e150, 1.0e-68, 0.0, 0.0
        )


@pytest.mark.parametrize(
    ("wave_number", "mass", "density", "scattering_length"),
    [
        (-1.0, MASS_KG, DENSITY_M3, SCATTERING_LENGTH_M),
        (1.0, 0.0, DENSITY_M3, SCATTERING_LENGTH_M),
        (1.0, MASS_KG, -1.0, SCATTERING_LENGTH_M),
        (1.0, MASS_KG, DENSITY_M3, -1.0),
        (math.inf, MASS_KG, DENSITY_M3, SCATTERING_LENGTH_M),
    ],
)
def test_invalid_or_nonfinite_inputs_fail_closed(
    wave_number: float, mass: float, density: float, scattering_length: float
) -> None:
    with pytest.raises(ValueError):
        bogoliubov_energy_joule(wave_number, mass, density, scattering_length)


def test_non_real_input_is_rejected() -> None:
    with pytest.raises(TypeError):
        bogoliubov_energy_joule("not a wave number", MASS_KG, DENSITY_M3, SCATTERING_LENGTH_M)  # type: ignore[arg-type]
