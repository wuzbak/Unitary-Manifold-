# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 102 — Gravitational Waves from Brane Dynamics.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math

import pytest

from src.core.pillar102_brane_gw import (
    F_PEAK_BRANE_GEV,
    F_PEAK_HZ,
    K_CS,
    M_KK_GEV,
    M_PL_GEV,
    M_RADION_GEV,
    OMEGA_GW_KK,
    PI_KR,
    PILLAR_NUMBER,
    kk_graviton_gw_background,
    pillar102_gw_spectrum,
    pillar102_summary,
    radion_gw_signal,
)


# ---------------------------------------------------------------------------
# Constants sanity checks
# ---------------------------------------------------------------------------

class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 102

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert PI_KR == 37.0

    def test_m_pl_gev_positive(self):
        assert M_PL_GEV > 0
        assert math.isfinite(M_PL_GEV)

    def test_m_kk_gev_positive_finite(self):
        assert M_KK_GEV > 0
        assert math.isfinite(M_KK_GEV)

    def test_m_kk_gev_in_tev_range(self):
        """M_KK should be ~1042 GeV, i.e. in the 500–5000 GeV range."""
        assert 500.0 < M_KK_GEV < 5000.0

    def test_m_radion_gev_positive_finite(self):
        assert M_RADION_GEV > 0
        assert math.isfinite(M_RADION_GEV)

    def test_m_radion_less_than_m_kk(self):
        """Radion mass must be lighter than the KK mass."""
        assert M_RADION_GEV < M_KK_GEV

    def test_m_radion_approx(self):
        """m_r ≈ M_KK / sqrt(6 πkR) ≈ 69.9 GeV; accept 50–120 GeV."""
        assert 50.0 < M_RADION_GEV < 120.0

    def test_f_peak_brane_gev_positive(self):
        assert F_PEAK_BRANE_GEV > 0
        assert math.isfinite(F_PEAK_BRANE_GEV)

    def test_f_peak_hz_very_large(self):
        """Brane collision frequency is enormous — above 10²⁰ Hz."""
        assert F_PEAK_HZ > 1e20

    def test_omega_gw_kk_positive_tiny(self):
        """Stochastic background should be extremely small."""
        assert OMEGA_GW_KK > 0
        assert math.isfinite(OMEGA_GW_KK)
        # Should be far below LISA sensitivity (~10^-12)
        assert OMEGA_GW_KK < 1e-10


# ---------------------------------------------------------------------------
# pillar102_gw_spectrum
# ---------------------------------------------------------------------------

class TestGWSpectrum:
    def test_returns_dict(self):
        result = pillar102_gw_spectrum()
        assert isinstance(result, dict)

    def test_expected_keys(self):
        result = pillar102_gw_spectrum()
        for key in ("pillar", "m_kk_gev", "f_peak_gev", "f_peak_hz",
                    "omega_gw_peak", "status", "note"):
            assert key in result, f"Missing key: {key}"

    def test_pillar_number_in_result(self):
        result = pillar102_gw_spectrum()
        assert result["pillar"] == 102

    def test_omega_gw_peak_positive(self):
        result = pillar102_gw_spectrum()
        assert result["omega_gw_peak"] > 0
        assert math.isfinite(result["omega_gw_peak"])

    def test_omega_gw_peak_tiny(self):
        """(M_KK/M_Pl)^4 should be astronomically small."""
        result = pillar102_gw_spectrum()
        assert result["omega_gw_peak"] < 1e-60

    def test_custom_nucleation_rate(self):
        result = pillar102_gw_spectrum(bubble_nucleation_rate_over_H4=2.0)
        result_default = pillar102_gw_spectrum(bubble_nucleation_rate_over_H4=1.0)
        assert abs(result["omega_gw_peak"] / result_default["omega_gw_peak"] - 2.0) < 1e-10

    def test_status_contains_architecture_limit(self):
        result = pillar102_gw_spectrum()
        assert "ARCHITECTURE_LIMIT" in result["status"]


# ---------------------------------------------------------------------------
# radion_gw_signal
# ---------------------------------------------------------------------------

class TestRadionGWSignal:
    def test_returns_dict(self):
        result = radion_gw_signal()
        assert isinstance(result, dict)

    def test_expected_keys(self):
        result = radion_gw_signal()
        for key in ("pillar", "m_radion_gev", "decay_rate_gev",
                    "gw_power_estimate", "status", "note"):
            assert key in result, f"Missing key: {key}"

    def test_default_decay_rate(self):
        result = radion_gw_signal()
        expected = M_RADION_GEV / (8.0 * math.pi)
        assert abs(result["decay_rate_gev"] - expected) < 1e-10

    def test_custom_decay_rate(self):
        result = radion_gw_signal(decay_rate_gev=1.0)
        assert abs(result["decay_rate_gev"] - 1.0) < 1e-14

    def test_gw_power_positive_finite(self):
        result = radion_gw_signal()
        assert result["gw_power_estimate"] > 0
        assert math.isfinite(result["gw_power_estimate"])

    def test_gw_power_tiny(self):
        """G_N in GeV⁻² is ~6.7e-39; power should be tiny."""
        result = radion_gw_signal()
        assert result["gw_power_estimate"] < 1e-30

    def test_status_contains_architecture_limit(self):
        result = radion_gw_signal()
        assert "ARCHITECTURE_LIMIT" in result["status"]


# ---------------------------------------------------------------------------
# kk_graviton_gw_background
# ---------------------------------------------------------------------------

class TestKKGravitonBackground:
    def test_returns_dict(self):
        result = kk_graviton_gw_background()
        assert isinstance(result, dict)

    def test_expected_keys(self):
        result = kk_graviton_gw_background()
        for key in ("pillar", "m_kk_gev", "pi_kr", "n_kk",
                    "omega_gw_kk", "status", "note"):
            assert key in result, f"Missing key: {key}"

    def test_default_n_kk(self):
        result = kk_graviton_gw_background()
        assert result["n_kk"] == int(PI_KR)

    def test_custom_n_kk(self):
        result = kk_graviton_gw_background(n_kk=10)
        assert result["n_kk"] == 10

    def test_omega_gw_positive_tiny(self):
        result = kk_graviton_gw_background()
        assert result["omega_gw_kk"] > 0
        assert result["omega_gw_kk"] < 1e-10

    def test_omega_gw_scales_with_n_kk(self):
        r1 = kk_graviton_gw_background(n_kk=10)
        r2 = kk_graviton_gw_background(n_kk=20)
        ratio = r2["omega_gw_kk"] / r1["omega_gw_kk"]
        assert abs(ratio - 2.0) < 1e-10

    def test_status_contains_architecture_limit(self):
        result = kk_graviton_gw_background()
        assert "ARCHITECTURE_LIMIT" in result["status"]

    def test_omega_matches_module_constant(self):
        result = kk_graviton_gw_background()
        assert abs(result["omega_gw_kk"] - OMEGA_GW_KK) < 1e-40


# ---------------------------------------------------------------------------
# pillar102_summary
# ---------------------------------------------------------------------------

class TestPillar102Summary:
    def test_returns_dict(self):
        result = pillar102_summary()
        assert isinstance(result, dict)

    def test_expected_top_keys(self):
        result = pillar102_summary()
        for key in ("pillar", "title", "status", "m_kk_gev", "m_radion_gev",
                    "f_peak_hz", "omega_gw_kk", "architecture_limit", "sub_results"):
            assert key in result, f"Missing key: {key}"

    def test_status_certified(self):
        result = pillar102_summary()
        assert "ARCHITECTURE_LIMIT_CERTIFIED" in result["status"]

    def test_sub_results_keys(self):
        result = pillar102_summary()
        sub = result["sub_results"]
        for key in ("brane_collision_gw", "radion_gw", "kk_stochastic_background"):
            assert key in sub, f"Missing sub_result key: {key}"

    def test_m_kk_consistent(self):
        result = pillar102_summary()
        assert abs(result["m_kk_gev"] - M_KK_GEV) < 1e-6

    def test_m_radion_consistent(self):
        result = pillar102_summary()
        assert abs(result["m_radion_gev"] - M_RADION_GEV) < 1e-10

    def test_architecture_limit_string_non_empty(self):
        result = pillar102_summary()
        assert len(result["architecture_limit"]) > 20
