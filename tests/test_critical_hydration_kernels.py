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
