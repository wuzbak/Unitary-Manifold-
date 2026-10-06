# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Dedicated dimensional toy-scattering checks for Pillar 717."""

import math

import pytest

from src.core import pillar717_dm_direct_detection_xenon_routing as dm


def test_natural_newton_constant():
    assert dm.G_N_NEWTON == pytest.approx(6.7076234152e-39, rel=1e-10, abs=0)
    assert dm.G_N_NEWTON == pytest.approx(1 / (1.221e19) ** 2, abs=0)


def test_area_conversions_consistent():
    assert dm.GEV2_TO_PB == pytest.approx(3.894e8)
    assert dm.GEV2_TO_PB * 1e-36 == pytest.approx(dm.GEV2_TO_CM2, rel=1e-12, abs=0)


def test_contact_toy_uses_reduced_mass_with_area_dimension():
    mu = 1042 * 0.939 / (1042 + 0.939)
    expected = (1 / (1.221e19) ** 2) ** 2 * mu ** 2 / math.pi * 3.894e-28
    assert dm.sigma_si_grav_cm2() == pytest.approx(expected, abs=0)
    assert 4.8e-105 < expected < 5.0e-105


def test_gravitational_toy_heavy_mass_saturates():
    light = dm.sigma_si_grav_cm2(1042)
    heavy = dm.sigma_si_grav_cm2(10420)
    assert 1 < heavy / light < 1.002


def test_ew_formula_and_mass_scaling():
    expected = 0.357 ** 4 / (math.pi * 1042 ** 4) * (54 / 131) ** 2 * 0.939 ** 2
    assert dm.sigma_si_ew_cm2() == pytest.approx(expected * 3.894e-28, abs=0)
    assert dm.sigma_si_ew_cm2(2084) == pytest.approx(
        dm.sigma_si_ew_cm2() / 16, abs=0
    )


def test_summary_comparisons_and_model_limitations():
    summary = dm.direct_detection_summary()
    assert summary["sigma_si_grav_cm2"] == dm.sigma_si_grav_cm2()
    assert summary["sigma_si_ew_cm2"] == dm.sigma_si_ew_cm2()
    assert summary["grav_above_xenon"] is False
    assert summary["ew_above_xenon"] is True
    assert "toys" in summary["model_scope"]
    assert "cannot confirm" in summary["falsification"]


@pytest.mark.parametrize("mass", [0, -1, float("nan"), float("inf")])
def test_contact_toy_invalid_mass_rejected(mass):
    with pytest.raises(ValueError):
        dm.sigma_si_grav_cm2(mass)
    with pytest.raises(ValueError):
        dm.sigma_si_ew_cm2(mass)


@pytest.mark.parametrize("z,a", [(54, 0), (-1, 131), (132, 131)])
def test_invalid_nuclear_benchmark_rejected(z, a):
    with pytest.raises(ValueError):
        dm.sigma_si_ew_cm2(Z=z, A=a)
