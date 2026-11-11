# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for critical-hydration exact kernels."""

from __future__ import annotations

import math

import pytest

from src.biology.critical_hydration_kernels import (
    BRAIDED_SOUND_SPEED,
    critical_dielectric_from_sound_speed,
    critical_hydration_kernel_report,
    critical_water_volume_fraction,
    maxwell_garnett_effective_dielectric,
    water_mass_ratio_from_volume_fraction,
)


def test_exact_dielectric_threshold_matches_rational_identity():
    expected = (37.0 / 12.0) ** 2
    assert math.isclose(critical_dielectric_from_sound_speed(), expected, rel_tol=0.0, abs_tol=1e-12)


def test_maxwell_garnett_is_monotone_in_water_fraction():
    dry = maxwell_garnett_effective_dielectric(0.0)
    wet = maxwell_garnett_effective_dielectric(0.3)
    wetter = maxwell_garnett_effective_dielectric(0.6)
    assert dry < wet < wetter


def test_maxwell_garnett_standard_spherical_inclusions():
    actual = maxwell_garnett_effective_dielectric(0.5, eps_water=9.0, eps_dry=4.5)
    assert actual == pytest.approx(45.0 / 7.0)
    assert maxwell_garnett_effective_dielectric(
        0.999999, eps_water=9.0, eps_dry=4.5
    ) == pytest.approx(9.0, rel=2e-6)


def test_target_above_both_thz_constituent_inputs_is_unreachable():
    with pytest.raises(ValueError, match="not reachable"):
        critical_water_volume_fraction(eps_water=9.0, eps_dry=4.5)


def test_default_assumed_dielectrics_give_correct_fraction():
    fraction = critical_water_volume_fraction()
    assert fraction == pytest.approx(0.3189195233776077)
    assert water_mass_ratio_from_volume_fraction(fraction) == pytest.approx(0.3601963625606616)


def test_decreasing_dielectric_mixture_inverts_correctly():
    fraction = critical_water_volume_fraction(eps_target=6.0, eps_water=4.5, eps_dry=9.0)
    assert maxwell_garnett_effective_dielectric(
        fraction, eps_water=4.5, eps_dry=9.0
    ) == pytest.approx(6.0)


@pytest.mark.parametrize("kwargs", [
    {"eps_target": float("nan")},
    {"eps_water": float("inf")},
    {"eps_water": 4.5, "eps_dry": 4.5},
    {"steps": 0},
])
def test_invalid_or_nonunique_hydration_models_raise(kwargs):
    with pytest.raises(ValueError):
        critical_water_volume_fraction(**kwargs)


def test_critical_water_fraction_hits_target_dielectric():
    target = critical_dielectric_from_sound_speed(BRAIDED_SOUND_SPEED)
    fraction = critical_water_volume_fraction(target)
    eff = maxwell_garnett_effective_dielectric(fraction)
    assert 0.0 < fraction < 1.0
    assert math.isclose(eff, target, rel_tol=0.0, abs_tol=1e-6)


def test_mass_ratio_formula_is_positive():
    assert water_mass_ratio_from_volume_fraction(0.25) > 0.0


def test_report_splits_exact_and_model_dependent_layers():
    report = critical_hydration_kernel_report()
    assert report["exact_kernel_status"] == "DERIVED_STRUCTURAL"
    assert report["model_dependent_prediction_status"] == "FALSIFIABLE_PREDICTION"
    assert report["exact_kernel"]["eps_r_critical"] > 9.0


@pytest.mark.parametrize("bad_speed", [0.0, -0.1])
def test_critical_dielectric_rejects_nonpositive_sound_speed(bad_speed: float):
    with pytest.raises(ValueError):
        critical_dielectric_from_sound_speed(bad_speed)


def test_unreachable_dielectric_target_raises():
    with pytest.raises(ValueError):
        critical_water_volume_fraction(eps_target=1000.0, eps_water=10.0, eps_dry=4.5)
