# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 102 — Gravitational Waves from Brane Dynamics.

Covers brane-collision GW spectrum, radion GW signal, and the stochastic
KK-graviton tower background.  All results are ARCHITECTURE_LIMIT_CERTIFIED:
signals sit far above current detector bands.

Theory: ThomasCory Walker-Pearson (2026)
Code:   GitHub Copilot (AI)
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
# Module-level constants
# ---------------------------------------------------------------------------

class TestPillar102Constants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 102

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert PI_KR == 37.0

    def test_m_pl_order(self):
        # Planck mass ~ 1.22e19 GeV
        assert 1.2e19 < M_PL_GEV < 1.3e19

    def test_m_kk_positive(self):
        assert M_KK_GEV > 0

    def test_m_kk_approx_1042_gev(self):
        # RS1 warp factor exp(-πkR) with πkR = 37 → M_KK ≈ 1042 GeV
        assert abs(M_KK_GEV - 1042.0) < 5.0

    def test_m_radion_positive(self):
        assert M_RADION_GEV > 0

    def test_m_radion_approx_70_gev(self):
        # m_r = M_KK / sqrt(6 × πkR) ≈ 69.9 GeV
        assert abs(M_RADION_GEV - 69.9) < 1.0

    def test_f_peak_hz_positive(self):
        assert F_PEAK_HZ > 0

    def test_f_peak_hz_far_above_ligo(self):
        # LIGO band: 10–1000 Hz.  Brane peak is ~10^26 Hz.
        assert F_PEAK_HZ > 1e20

    def test_omega_gw_kk_positive(self):
        assert OMEGA_GW_KK > 0

    def test_omega_gw_kk_far_below_lisa(self):
        # LISA sensitivity ~ 10^-12; KK background ~ 10^-30
        assert OMEGA_GW_KK < 1e-12

    def test_m_kk_warp_formula(self):
        """M_KK = M_Pl × exp(-πkR) with πkR = K_CS/2 = 37."""
        expected = M_PL_GEV * math.exp(-PI_KR)
        assert abs(M_KK_GEV - expected) < 1e-3

    def test_m_radion_formula(self):
        """m_r = M_KK / sqrt(6 × πkR)."""
        expected = M_KK_GEV / math.sqrt(6.0 * PI_KR)
        assert abs(M_RADION_GEV - expected) < 1e-6

    def test_omega_gw_kk_formula(self):
        """Ω_GW_KK = (M_KK/M_Pl)² × πkR."""
        expected = (M_KK_GEV / M_PL_GEV) ** 2 * PI_KR
        assert abs(OMEGA_GW_KK - expected) < 1e-60


# ---------------------------------------------------------------------------
# pillar102_gw_spectrum
# ---------------------------------------------------------------------------

class TestGWSpectrum:
    @pytest.fixture
    def spectrum(self):
        return pillar102_gw_spectrum()

    def test_returns_dict(self, spectrum):
        assert isinstance(spectrum, dict)

    def test_pillar_key(self, spectrum):
        assert spectrum["pillar"] == 102

    def test_m_kk_gev_present(self, spectrum):
        assert "m_kk_gev" in spectrum
        assert abs(spectrum["m_kk_gev"] - M_KK_GEV) < 1e-6

    def test_f_peak_gev_present(self, spectrum):
        assert spectrum["f_peak_gev"] > 0

    def test_f_peak_hz_present(self, spectrum):
        assert spectrum["f_peak_hz"] > 1e20

    def test_omega_gw_peak_positive(self, spectrum):
        assert spectrum["omega_gw_peak"] > 0

    def test_status_architecture_limit(self, spectrum):
        assert "ARCHITECTURE_LIMIT" in spectrum["status"]

    def test_note_contains_hz(self, spectrum):
        assert "Hz" in spectrum["note"]

    def test_custom_bubble_rate(self):
        """Non-unity bubble nucleation rate scales omega_gw_peak linearly."""
        rate = 2.5
        s = pillar102_gw_spectrum(bubble_nucleation_rate_over_H4=rate)
        s_ref = pillar102_gw_spectrum()
        assert abs(s["omega_gw_peak"] / s_ref["omega_gw_peak"] - rate) < 1e-10

    def test_default_bubble_rate_stored(self, spectrum):
        assert abs(spectrum["bubble_nucleation_rate_over_H4"] - 1.0) < 1e-10


# ---------------------------------------------------------------------------
# radion_gw_signal
# ---------------------------------------------------------------------------

class TestRadionGWSignal:
    @pytest.fixture
    def signal(self):
        return radion_gw_signal()

    def test_returns_dict(self, signal):
        assert isinstance(signal, dict)

    def test_pillar_key(self, signal):
        assert signal["pillar"] == 102

    def test_m_radion_gev_approx_70(self, signal):
        assert abs(signal["m_radion_gev"] - 69.9) < 1.0

    def test_decay_rate_positive(self, signal):
        assert signal["decay_rate_gev"] > 0

    def test_default_decay_rate_narrow_width(self, signal):
        """Default Γ = m_r / (8π)."""
        expected = M_RADION_GEV / (8.0 * math.pi)
        assert abs(signal["decay_rate_gev"] - expected) < 1e-8

    def test_gw_power_positive(self, signal):
        assert signal["gw_power_estimate"] > 0

    def test_gw_power_extremely_small(self, signal):
        # P_GW ~ G_N m_r² Γ_r² — hopelessly small in GeV⁻² units
        assert signal["gw_power_estimate"] < 1e-30

    def test_g_newton_gev2(self, signal):
        """G_N in GeV⁻² = 1/M_Pl²."""
        assert abs(signal["g_newton_gev2"] - 1.0 / M_PL_GEV ** 2) < 1e-60

    def test_status_architecture_limit(self, signal):
        assert "ARCHITECTURE_LIMIT" in signal["status"]

    def test_note_mentions_m_r(self, signal):
        assert "m_r" in signal["note"]

    def test_custom_decay_rate(self):
        """Custom decay rate changes gw_power_estimate quadratically."""
        gamma1 = 1.0  # GeV
        gamma2 = 2.0  # GeV
        s1 = radion_gw_signal(decay_rate_gev=gamma1)
        s2 = radion_gw_signal(decay_rate_gev=gamma2)
        ratio = s2["gw_power_estimate"] / s1["gw_power_estimate"]
        assert abs(ratio - 4.0) < 1e-8


# ---------------------------------------------------------------------------
# kk_graviton_gw_background
# ---------------------------------------------------------------------------

class TestKKGravitonBackground:
    @pytest.fixture
    def background(self):
        return kk_graviton_gw_background()

    def test_returns_dict(self, background):
        assert isinstance(background, dict)

    def test_pillar_key(self, background):
        assert background["pillar"] == 102

    def test_default_n_kk(self, background):
        """Default N_KK = int(πkR) = 37."""
        assert background["n_kk"] == 37

    def test_omega_gw_kk_positive(self, background):
        assert background["omega_gw_kk"] > 0

    def test_omega_gw_kk_matches_constant(self, background):
        assert abs(background["omega_gw_kk_reference"] - OMEGA_GW_KK) < 1e-60

    def test_omega_gw_kk_matches_formula(self, background):
        n = background["n_kk"]
        expected = (M_KK_GEV / M_PL_GEV) ** 2 * n
        assert abs(background["omega_gw_kk"] - expected) < 1e-60

    def test_status_architecture_limit(self, background):
        assert "ARCHITECTURE_LIMIT" in background["status"]

    def test_note_mentions_lisa(self, background):
        assert "LISA" in background["note"]

    def test_custom_n_kk(self):
        """Doubling N_KK doubles Ω_GW."""
        bg1 = kk_graviton_gw_background(n_kk=10)
        bg2 = kk_graviton_gw_background(n_kk=20)
        assert abs(bg2["omega_gw_kk"] / bg1["omega_gw_kk"] - 2.0) < 1e-10

    def test_m_kk_consistent(self, background):
        assert abs(background["m_kk_gev"] - M_KK_GEV) < 1e-6

    def test_pi_kr_correct(self, background):
        assert background["pi_kr"] == 37.0


# ---------------------------------------------------------------------------
# pillar102_summary
# ---------------------------------------------------------------------------

class TestPillar102Summary:
    @pytest.fixture(scope="class")
    def summary(self):
        return pillar102_summary()

    def test_returns_dict(self, summary):
        assert isinstance(summary, dict)

    def test_pillar_key(self, summary):
        assert summary["pillar"] == 102

    def test_title_present(self, summary):
        assert "Gravitational Waves" in summary["title"]

    def test_status_certified(self, summary):
        assert "ARCHITECTURE_LIMIT_CERTIFIED" in summary["status"]

    def test_m_kk_present(self, summary):
        assert abs(summary["m_kk_gev"] - M_KK_GEV) < 1e-6

    def test_m_radion_present(self, summary):
        assert abs(summary["m_radion_gev"] - M_RADION_GEV) < 1e-6

    def test_f_peak_hz_present(self, summary):
        assert summary["f_peak_hz"] > 1e20

    def test_omega_gw_kk_present(self, summary):
        assert summary["omega_gw_kk"] < 1e-12

    def test_architecture_limit_description(self, summary):
        desc = summary["architecture_limit"]
        assert "kHz" in desc or "Hz" in desc

    def test_sub_results_present(self, summary):
        sr = summary["sub_results"]
        assert "brane_collision_gw" in sr
        assert "radion_gw" in sr
        assert "kk_stochastic_background" in sr

    def test_sub_results_internally_consistent(self, summary):
        sr = summary["sub_results"]
        assert sr["brane_collision_gw"]["pillar"] == 102
        assert sr["radion_gw"]["pillar"] == 102
        assert sr["kk_stochastic_background"]["pillar"] == 102
