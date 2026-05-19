# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 280 — SC2 c_UV-Independent Interval Narrowing."""
from __future__ import annotations

import pytest

from src.core.pillar280_sc2_c_uv_independent_interval_narrowing import (
    ADJACENCY_TRACK_LABEL,
    ALPHA_GW_HIGH,
    ALPHA_GW_LOW,
    ALPHA_GW_MS_BENCHMARK,
    EPSILON_UV_BOUND,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    WIDTH_REDUCTION_ACCEPTANCE,
    epsilon_uv_for_target_reduction,
    interval_narrowing_certificate,
    interval_narrowing_report,
    ms_tolerance_band,
    narrow_alpha_gw_interval,
    separation_guard,
    width_reduction_fraction,
)


def test_identity_and_separation():
    assert PILLAR_NUMBER == 280
    assert PILLAR_TITLE
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
    g = separation_guard()
    assert g["narrows_interval_only_no_point_derivation"] is True


def test_constants():
    assert ALPHA_GW_LOW == pytest.approx(4.2e-10)
    assert ALPHA_GW_HIGH == pytest.approx(4.8e-10)
    assert ALPHA_GW_MS_BENCHMARK == pytest.approx(4.49e-10)
    assert EPSILON_UV_BOUND == pytest.approx(0.04)
    assert WIDTH_REDUCTION_ACCEPTANCE == pytest.approx(0.30)


def test_ms_tolerance_band_endpoints():
    band = ms_tolerance_band(alpha_ms=4.49e-10, epsilon_uv=0.04)
    assert band[0] == pytest.approx(4.49e-10 * 0.96)
    assert band[1] == pytest.approx(4.49e-10 * 1.04)


def test_ms_tolerance_band_validation():
    with pytest.raises(ValueError):
        ms_tolerance_band(alpha_ms=-1.0)
    with pytest.raises(ValueError):
        ms_tolerance_band(epsilon_uv=-0.1)


def test_narrow_interval_default_inside_original():
    low, high = narrow_alpha_gw_interval()
    assert low >= ALPHA_GW_LOW - 1e-30
    assert high <= ALPHA_GW_HIGH + 1e-30
    assert low < high


def test_narrow_interval_empty_intersection_returns_band():
    # If MS benchmark is far outside the original window, the function
    # falls back to the band.
    low, high = narrow_alpha_gw_interval(
        alpha_low=1.0e-9, alpha_high=2.0e-9, alpha_ms=4.49e-10, epsilon_uv=0.01
    )
    assert low > 0.0 and high > low


def test_narrow_interval_input_validation():
    with pytest.raises(ValueError):
        narrow_alpha_gw_interval(alpha_low=5.0e-10, alpha_high=4.5e-10)


def test_width_reduction_fraction_positive():
    f = width_reduction_fraction()
    assert 0.0 <= f <= 1.0
    # At ε_UV = 0.04 the analytic reduction is > 30%
    assert f >= WIDTH_REDUCTION_ACCEPTANCE


def test_width_reduction_decreases_with_epsilon():
    fr = [width_reduction_fraction(epsilon_uv=e) for e in (0.01, 0.02, 0.03, 0.04, 0.05)]
    for a, b in zip(fr, fr[1:]):
        assert b <= a + 1e-12


def test_epsilon_uv_for_target_reduction_inverts_correctly():
    eps = epsilon_uv_for_target_reduction(target_reduction=0.50)
    # With this ε, width_reduction_fraction should match target (modulo
    # the intersection clipping when ε is large enough to cover the
    # original interval, which is not the case here).
    actual = width_reduction_fraction(epsilon_uv=eps)
    assert actual == pytest.approx(0.50, rel=1e-6, abs=1e-6)


def test_epsilon_uv_for_target_reduction_input_validation():
    with pytest.raises(ValueError):
        epsilon_uv_for_target_reduction(target_reduction=-0.1)
    with pytest.raises(ValueError):
        epsilon_uv_for_target_reduction(target_reduction=1.1)


def test_certificate_structure():
    c = interval_narrowing_certificate()
    for key in (
        "alpha_gw_original_interval",
        "alpha_gw_narrowed_interval",
        "original_width",
        "narrowed_width",
        "epsilon_uv",
        "width_reduction_fraction",
        "alpha_gw_ms_benchmark",
    ):
        assert key in c
    assert c["narrowed_width"] < c["original_width"]


def test_report_acceptance_and_structure():
    r = interval_narrowing_report()
    assert r["acceptance_gate_passed"] is True
    assert "THEOREM_280_1" in r["theorem_label"]
    assert "ms_normalization" in r["named_modules"]
    assert "10d_bridge" in r["named_modules"]
    eps = r["epsilon_uv_for_30pct_reduction"]
    # By Theorem 280.1, ε for 30% reduction is W_old (1−0.30) / (2 α_MS)
    expected = (ALPHA_GW_HIGH - ALPHA_GW_LOW) * 0.7 / (2.0 * ALPHA_GW_MS_BENCHMARK)
    assert eps == pytest.approx(expected)


def test_no_hardgate_drift():
    r = interval_narrowing_report()
    g = r["separation_guard"]
    assert g["is_hardgate"] is False
    assert g["alters_falsifier_window"] is False
