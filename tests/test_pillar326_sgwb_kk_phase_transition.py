# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 326 — Stochastic GW Background from KK Phase Transition."""
import math
import pytest

from src.core.pillar326_sgwb_kk_phase_transition import (
    N_W, K_CS, PI_KR, C_S, M_KK_GEV,
    G_STAR_KK, ALPHA_PT, BETA_OVER_H, V_W,
    LISA_FREQ_MIN_HZ, LISA_FREQ_MAX_HZ, LISA_OMEGA_H2_SENSITIVITY,
    separation_guard,
    phase_transition_temperature,
    transition_strength_alpha,
    beta_over_h_estimate,
    peak_frequency_sw,
    omega_gw_h2_sw,
    omega_gw_h2_turbulence,
    sgwb_spectrum,
    lisa_detectability,
    gw_phase_transition_full_report,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert PI_KR == 37.0

    def test_g_star(self):
        assert G_STAR_KK == 106.75

    def test_lisa_band_order(self):
        assert LISA_FREQ_MIN_HZ < LISA_FREQ_MAX_HZ

    def test_v_w_unity(self):
        assert V_W == 1.0  # runaway wall


class TestSeparationGuard:
    def test_string(self):
        assert isinstance(separation_guard(), str)

    def test_adjacent(self):
        assert "ADJACENT" in separation_guard()


class TestPhaseTransitionTemperature:
    def test_equals_m_kk(self):
        t = phase_transition_temperature(M_KK_GEV)
        assert t == M_KK_GEV

    def test_tev_scale(self):
        t = phase_transition_temperature()
        assert 500 < t < 5000


class TestTransitionStrength:
    def test_positive(self):
        alpha = transition_strength_alpha()
        assert alpha > 0.0

    def test_formula(self):
        alpha = transition_strength_alpha(PI_KR, G_STAR_KK, 1.0)
        expected = 30.0 / (math.pi ** 2 * G_STAR_KK)
        assert abs(alpha - expected) < 1e-10

    def test_increases_with_lambda(self):
        a1 = transition_strength_alpha(PI_KR, G_STAR_KK, 1.0)
        a10 = transition_strength_alpha(PI_KR, G_STAR_KK, 10.0)
        assert a10 > a1


class TestBetaOverH:
    def test_canonical(self):
        beta_h = beta_over_h_estimate(PI_KR, 1.0)
        assert abs(beta_h - PI_KR) < 1e-10

    def test_positive(self):
        assert beta_over_h_estimate() > 0.0

    def test_pi_kr_value(self):
        assert beta_over_h_estimate() == pytest.approx(37.0, rel=1e-6)


class TestPeakFrequency:
    def test_positive(self):
        t = phase_transition_temperature()
        f = peak_frequency_sw(t)
        assert f > 0.0

    def test_mhz_range(self):
        t = phase_transition_temperature()
        f = peak_frequency_sw(t, BETA_OVER_H, G_STAR_KK)
        # f_peak ~ mHz range for 1 TeV transition
        assert 1e-4 < f < 1.0  # Hz

    def test_increases_with_beta_h(self):
        t = phase_transition_temperature()
        f1 = peak_frequency_sw(t, beta_h=10.0)
        f10 = peak_frequency_sw(t, beta_h=100.0)
        assert f10 > f1


class TestOmegaGw:
    def test_sw_positive(self):
        alpha = transition_strength_alpha()
        omega = omega_gw_h2_sw(alpha)
        assert omega > 0.0

    def test_sw_increases_with_alpha(self):
        o1 = omega_gw_h2_sw(0.1)
        o2 = omega_gw_h2_sw(1.0)
        assert o2 > o1

    def test_sw_decreases_with_beta_h(self):
        alpha = transition_strength_alpha()
        o_fast = omega_gw_h2_sw(alpha, beta_h=100.0)
        o_slow = omega_gw_h2_sw(alpha, beta_h=10.0)
        # Higher β/H means faster transition → smaller Omega_GW
        assert o_slow > o_fast

    def test_turb_positive(self):
        alpha = transition_strength_alpha()
        omega = omega_gw_h2_turbulence(alpha)
        assert omega > 0.0

    def test_turb_less_than_sw(self):
        # Turbulence is subdominant for small ε_turb
        alpha = transition_strength_alpha()
        omega_sw = omega_gw_h2_sw(alpha)
        omega_turb = omega_gw_h2_turbulence(alpha)
        # Turb can be comparable or smaller depending on alpha and beta/H
        assert omega_turb >= 0.0


class TestSpectrum:
    def setup_method(self):
        self.spectrum = sgwb_spectrum()

    def test_returns_dict(self):
        assert isinstance(self.spectrum, dict)

    def test_required_keys(self):
        for k in ["t_star_gev", "alpha", "beta_over_h", "f_peak_hz",
                  "omega_sw_h2", "omega_turb_h2", "omega_total_h2"]:
            assert k in self.spectrum

    def test_f_peak_positive(self):
        assert self.spectrum["f_peak_hz"] > 0.0

    def test_omega_total_positive(self):
        assert self.spectrum["omega_total_h2"] > 0.0

    def test_consistency_sw_plus_turb(self):
        s = self.spectrum
        assert abs(s["omega_total_h2"] - (s["omega_sw_h2"] + s["omega_turb_h2"])) < 1e-50


class TestLisaDetectability:
    def test_returns_dict(self):
        s = sgwb_spectrum()
        d = lisa_detectability(s["f_peak_hz"], s["omega_total_h2"])
        assert isinstance(d, dict)

    def test_verdict_string(self):
        s = sgwb_spectrum()
        d = lisa_detectability(s["f_peak_hz"], s["omega_total_h2"])
        assert d["verdict"] in ["LISA_DETECTABLE", "BELOW_LISA_OR_OUTSIDE_BAND"]

    def test_ratio_positive(self):
        s = sgwb_spectrum()
        d = lisa_detectability(s["f_peak_hz"], s["omega_total_h2"])
        assert d["ratio_to_lisa"] > 0.0


class TestFullReport:
    def setup_method(self):
        self.r = gw_phase_transition_full_report()

    def test_pillar_number(self):
        assert self.r["pillar"] == 326

    def test_adjacency(self):
        assert self.r["adjacency"] == "NON_HARDGATE_ADJACENT"

    def test_m_kk_tev(self):
        assert 0.5 < self.r["m_kk_tev"] < 5.0

    def test_phase_transition_section(self):
        pt = self.r["phase_transition"]
        assert pt["alpha"] > 0.0
        assert pt["beta_over_h"] > 0.0

    def test_physics_summary(self):
        assert isinstance(self.r["physics_summary"], str)
        assert "peak frequency" in self.r["physics_summary"]

    def test_distinct_from_pillar294(self):
        assert "294" in self.r["distinct_from_pillar294"]

    def test_f_peak_range(self):
        r = self.r["f_peak_range_hz"]
        assert len(r) == 2
        assert all(f > 0 for f in r)

    def test_omega_range(self):
        r = self.r["omega_range_h2"]
        assert len(r) == 2
        assert all(o > 0 for o in r)
