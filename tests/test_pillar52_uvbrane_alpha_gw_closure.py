# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
from __future__ import annotations

import math

import pytest

from src.core.pillar52_uvbrane_alpha_gw_closure import (
    amplitude_closure_report,
    uvbrane_alpha_gw,
)


def test_uvbrane_alpha_gw_returns_float():
    alpha = uvbrane_alpha_gw()
    assert isinstance(alpha, float)


def test_uvbrane_alpha_gw_in_required_interval():
    alpha = uvbrane_alpha_gw()
    assert 4.2e-10 <= alpha <= 4.8e-10


def test_uvbrane_alpha_gw_is_deterministic():
    assert uvbrane_alpha_gw() == pytest.approx(uvbrane_alpha_gw(), rel=0.0, abs=0.0)


def test_report_returns_dict():
    report = amplitude_closure_report()
    assert isinstance(report, dict)


def test_report_contains_expected_keys():
    report = amplitude_closure_report()
    for key in (
        "status",
        "alpha_gw",
        "transfer_factor",
        "a_s_planck",
        "a_s_predicted",
        "residual",
        "sigma_level",
        "residual_documentation",
        "derivation_components",
    ):
        assert key in report


def test_report_alpha_matches_public_function():
    report = amplitude_closure_report()
    assert report["alpha_gw"] == pytest.approx(uvbrane_alpha_gw(), rel=0, abs=0)


def test_report_alpha_in_bounds():
    report = amplitude_closure_report()
    low, high = report["alpha_bounds"]
    assert low <= report["alpha_gw"] <= high


def test_transfer_factor_is_positive_and_reasonable():
    report = amplitude_closure_report()
    assert report["transfer_factor"] > 0.0
    assert 4.0 <= report["transfer_factor"] <= 6.5


def test_predicted_as_is_positive():
    report = amplitude_closure_report()
    assert report["a_s_predicted"] > 0.0


def test_residual_matches_definition():
    report = amplitude_closure_report()
    expected = report["a_s_predicted"] - report["a_s_planck"]
    assert report["residual"] == pytest.approx(expected, rel=1e-12)


def test_sigma_level_is_finite_nonnegative():
    report = amplitude_closure_report()
    assert math.isfinite(report["sigma_level"])
    assert report["sigma_level"] >= 0.0


def test_residual_documentation_mentions_residual_and_sigma():
    text = amplitude_closure_report()["residual_documentation"].lower()
    assert "residual" in text
    assert "σ" in text or "sigma" in text


def test_rs1_geometry_baseline_is_tiny():
    report = amplitude_closure_report()
    assert report["derivation_components"]["alpha_rs1"] < 1e-55


def test_kk_modes_and_enhancement_are_valid():
    report = amplitude_closure_report()
    components = report["derivation_components"]
    assert components["kk_modes"] >= 10.0
    assert 0.9 <= components["kk_enhancement"] <= 1.0


def test_status_is_allowed():
    report = amplitude_closure_report()
    assert report["status"] in {"CLOSED", "REDUCED_GAP"}


def test_shortfall_and_ingredient_logic_is_consistent():
    report = amplitude_closure_report()
    if report["exact_closure"]:
        assert report["shortfall"] == pytest.approx(0.0, abs=0.0)
        assert report["required_uv_geometry_or_n_flux_ingredient"] is None
    else:
        assert report["shortfall"] >= 0.0
        ingredient = report["required_uv_geometry_or_n_flux_ingredient"]
        assert isinstance(ingredient, str)
        assert "uv" in ingredient.lower() or "n_flux" in ingredient.lower()


def test_alpha_clipping_flag_consistency():
    report = amplitude_closure_report()
    c = report["derivation_components"]
    low, high = report["alpha_bounds"]
    raw = c["alpha_raw"]
    clipped = c["alpha_clipped"]
    assert clipped == (raw < low or raw > high)

