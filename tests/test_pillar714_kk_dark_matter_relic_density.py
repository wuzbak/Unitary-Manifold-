# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Dedicated unit and output checks for the Pillar 714 toy benchmark."""

import math

import pytest

from src.core import pillar714_kk_dark_matter_relic_density as dm


def test_gev_inverse_squared_to_pb():
    assert dm.PB_PER_GEV2 == pytest.approx(3.894e8)
    assert dm.GEV2_PER_PB == pytest.approx(2.5680534155e-9, rel=1e-10, abs=0)
    assert dm.sigma_v_kk_pb() == pytest.approx(
        dm.sigma_v_kk_gev2() * 3.894e8
    )


def test_actual_benchmark_outputs():
    sigma = 0.63 ** 4 / (16 * math.pi * 1042 ** 2)
    assert sigma == pytest.approx(2.8864025832e-9, rel=1e-10, abs=0)
    assert dm.sigma_v_kk_pb() == pytest.approx(sigma * 3.894e8)
    assert dm.omega_kk_h2() == pytest.approx(0.1 / (sigma * 3.894e8))
    assert 0.088 < dm.omega_kk_h2() < 0.090


def test_summary_supplied_not_derived():
    summary = dm.relic_density_summary()
    assert summary["m_kk_gev"] == 1042.0
    assert summary["omega_kk_h2"] == dm.omega_kk_h2()
    assert summary["ratio_to_observed"] == pytest.approx(dm.omega_kk_h2() / 0.12)
    assert summary["within_factor_2"] is True
    assert "supplied" in summary["model_scope"]
    assert "not a mass derivation" in summary["model_scope"]


def test_mass_and_coupling_scaling():
    assert dm.sigma_v_kk_pb(2084) == pytest.approx(dm.sigma_v_kk_pb() / 4)
    assert dm.omega_kk_h2(2084) == pytest.approx(dm.omega_kk_h2() * 4)
    assert dm.sigma_v_kk_pb(g_kk=1.26) == pytest.approx(dm.sigma_v_kk_pb() * 16)


def test_zero_coupling_not_zero_relic_density():
    assert dm.sigma_v_kk_pb(g_kk=0) == 0
    assert math.isinf(dm.omega_kk_h2(g_kk=0))
    assert dm.relic_density_summary(g_kk=0)["within_factor_2"] is False


@pytest.mark.parametrize("mass", [0, -1, float("nan"), float("inf")])
def test_invalid_mass_rejected(mass):
    with pytest.raises(ValueError):
        dm.omega_kk_h2(mass)


@pytest.mark.parametrize("coupling", [-1, float("nan"), float("inf")])
def test_invalid_coupling_rejected(coupling):
    with pytest.raises(ValueError):
        dm.omega_kk_h2(g_kk=coupling)
