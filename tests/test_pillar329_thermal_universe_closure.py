# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 329 — Thermal Universe Closure."""
import math
import pytest

from src.core.pillar329_thermal_universe_closure import (
    N_W, K_CS, PI_KR, C_S,
    M_PL_GEV, M_KK_GEV, M_KK_TEV,
    T_KK_GEV, T_EW_GEV, T_QCD_GEV, T_BBN_GEV, T_CMB_EV,
    ALPHA_KK, BETA_OVER_H_KK,
    DERIVATION_STATUS,
    separation_guard,
    kk_temperature,
    ew_temperature,
    qcd_temperature,
    bbn_temperature,
    cmb_temperature_today,
    transition_ratio,
    kk_gw_peak_frequency,
    kk_gw_omega_h2_estimate,
    thermal_timeline,
    thermal_history_full_report,
    observational_windows,
    entropy_conservation_check,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert abs(PI_KR - 37.0) < 1e-9

    def test_c_s(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-12

    def test_m_pl_positive(self):
        assert M_PL_GEV > 1e18

    def test_m_kk_order_of_magnitude(self):
        # M_KK ~ 1 TeV = 1000 GeV
        assert 100.0 < M_KK_GEV < 1e5

    def test_m_kk_tev(self):
        assert abs(M_KK_TEV - M_KK_GEV / 1000.0) < 1e-6

    def test_t_kk_equals_m_kk(self):
        assert abs(T_KK_GEV - M_KK_GEV) < 1e-3

    def test_t_ew_order(self):
        assert 50.0 < T_EW_GEV < 300.0

    def test_t_qcd_order(self):
        # T_QCD ~ 0.1–0.3 GeV
        assert 0.1 < T_QCD_GEV < 0.5

    def test_t_bbn_order(self):
        # T_BBN ~ 0.7 MeV = 7e-4 GeV
        assert 1e-4 < T_BBN_GEV < 5e-3

    def test_t_cmb_ev(self):
        # T_CMB ~ 2.35e-4 eV
        assert 1e-4 < T_CMB_EV < 1e-3

    def test_alpha_kk(self):
        assert abs(ALPHA_KK - PI_KR ** 2 / 100.0) < 1e-9

    def test_beta_over_h(self):
        assert abs(BETA_OVER_H_KK - 37.0) < 1e-9


class TestTemperatureOrdering:
    """Thermal transitions must be strictly decreasing in temperature."""

    def test_t_kk_gt_t_ew(self):
        assert T_KK_GEV > T_EW_GEV

    def test_t_ew_gt_t_qcd(self):
        assert T_EW_GEV > T_QCD_GEV

    def test_t_qcd_gt_t_bbn(self):
        assert T_QCD_GEV > T_BBN_GEV

    def test_t_bbn_gt_t_cmb(self):
        assert T_BBN_GEV > T_CMB_EV * 1e-9  # both in GeV

    def test_full_ordering(self):
        temps = [T_KK_GEV, T_EW_GEV, T_QCD_GEV, T_BBN_GEV]
        for i in range(len(temps) - 1):
            assert temps[i] > temps[i + 1]


class TestDerivationStatus:
    def test_has_all_transitions(self):
        for key in ["T_KK", "T_EW", "T_QCD", "T_BBN", "T_CMB"]:
            assert key in DERIVATION_STATUS

    def test_t_kk_derived(self):
        assert DERIVATION_STATUS["T_KK"]["label"] == "DERIVED"

    def test_t_ew_derived(self):
        assert DERIVATION_STATUS["T_EW"]["label"] == "DERIVED"

    def test_t_qcd_has_systematic(self):
        assert "SYSTEMATIC" in DERIVATION_STATUS["T_QCD"]["label"]

    def test_t_bbn_sm_consistent(self):
        assert "SM" in DERIVATION_STATUS["T_BBN"]["label"]

    def test_t_cmb_external(self):
        assert "EXTERNALLY" in DERIVATION_STATUS["T_CMB"]["label"]


class TestSeparationGuard:
    def test_is_string(self):
        assert isinstance(separation_guard(), str)

    def test_adjacent_track(self):
        assert "ADJACENT" in separation_guard()

    def test_no_hardgate_claim(self):
        assert "NON_HARDGATE" in separation_guard()


class TestTemperatureFunctions:
    def test_kk_temperature(self):
        t = kk_temperature()
        assert abs(t - T_KK_GEV) < 1e-3

    def test_kk_temperature_parameterized(self):
        t = kk_temperature(m_pl_gev=1.22091e19, pi_kr=37.0)
        assert t > 0

    def test_ew_temperature(self):
        t = ew_temperature()
        assert abs(t - T_EW_GEV) < 1e-6

    def test_ew_temperature_scales_with_mw(self):
        t1 = ew_temperature(79.985)
        t2 = ew_temperature(80.377)
        assert t2 > t1

    def test_qcd_temperature(self):
        t = qcd_temperature()
        assert abs(t - T_QCD_GEV) < 1e-6

    def test_bbn_temperature(self):
        t = bbn_temperature()
        assert abs(t - T_BBN_GEV) < 1e-12

    def test_cmb_temperature_today(self):
        k, ev, label = cmb_temperature_today()
        assert abs(k - 2.72548) < 0.001
        assert ev > 0
        assert "EXTERNAL" in label


class TestTransitionRatio:
    def test_ratio_kk_bbn(self):
        r = transition_ratio(T_KK_GEV, T_BBN_GEV)
        # Should be ~ 1e6 (TeV / MeV)
        assert r > 1e5

    def test_ratio_unity_for_same(self):
        r = transition_ratio(1.0, 1.0)
        assert abs(r - 1.0) < 1e-10

    def test_raises_on_zero(self):
        with pytest.raises(ValueError):
            transition_ratio(1.0, 0.0)

    def test_temperature_ratios_consistent(self):
        r_kk_ew = transition_ratio(T_KK_GEV, T_EW_GEV)
        r_ew_qcd = transition_ratio(T_EW_GEV, T_QCD_GEV)
        r_qcd_bbn = transition_ratio(T_QCD_GEV, T_BBN_GEV)
        # All ratios should be > 1
        assert r_kk_ew > 1
        assert r_ew_qcd > 1
        assert r_qcd_bbn > 1


class TestGWPredictions:
    def test_peak_frequency_positive(self):
        f = kk_gw_peak_frequency()
        assert f > 0

    def test_peak_frequency_in_mhz_range(self):
        # Expected ~ 7 mHz = 7e-3 Hz
        f = kk_gw_peak_frequency()
        assert 1e-4 < f < 1.0

    def test_omega_gw_range(self):
        lo, hi = kk_gw_omega_h2_estimate()
        assert lo > 0
        assert hi > lo
        assert lo < 1e-6  # below 10^{-6}

    def test_omega_gw_monotone_in_efficiency(self):
        lo, hi = kk_gw_omega_h2_estimate(ALPHA_KK, BETA_OVER_H_KK, 106.75)
        assert lo < hi

    def test_peak_frequency_scales_with_T(self):
        f1 = kk_gw_peak_frequency(T_KK_GEV)
        f2 = kk_gw_peak_frequency(T_KK_GEV * 2)
        assert f2 > f1


class TestThermalTimeline:
    def test_returns_list(self):
        tl = thermal_timeline()
        assert isinstance(tl, list)

    def test_five_transitions(self):
        tl = thermal_timeline()
        assert len(tl) == 5

    def test_epochs_present(self):
        tl = thermal_timeline()
        epochs = [e["epoch"] for e in tl]
        for ep in ["T_KK", "T_EW", "T_QCD", "T_BBN", "T_CMB"]:
            assert ep in epochs

    def test_ordered_by_temperature(self):
        tl = thermal_timeline()
        temps = [e["t_gev"] for e in tl]
        for i in range(len(temps) - 1):
            assert temps[i] > temps[i + 1]

    def test_gw_signal_only_at_kk(self):
        tl = thermal_timeline()
        gw_epochs = [e["epoch"] for e in tl if e["gw_signal"]]
        assert gw_epochs == ["T_KK"]

    def test_kk_entry_has_gw_frequency(self):
        tl = thermal_timeline()
        kk = next(e for e in tl if e["epoch"] == "T_KK")
        assert kk["gw_peak_hz"] is not None
        assert kk["gw_peak_hz"] > 0

    def test_all_have_derivation(self):
        tl = thermal_timeline()
        for e in tl:
            assert "derivation" in e
            assert e["derivation"]


class TestObservationalWindows:
    def test_returns_dict(self):
        w = observational_windows()
        assert isinstance(w, dict)

    def test_has_all_epochs(self):
        w = observational_windows()
        for ep in ["T_KK", "T_EW", "T_QCD", "T_BBN", "T_CMB"]:
            assert ep in w

    def test_kk_has_gw(self):
        w = observational_windows()
        assert "gw" in w["T_KK"]
        assert "LISA" in w["T_KK"]["gw"]


class TestEntropyConservation:
    def test_returns_dict(self):
        ec = entropy_conservation_check()
        assert isinstance(ec, dict)

    def test_g_star_ordering(self):
        ec = entropy_conservation_check()
        # g_{*S} at KK should be higher than at BBN
        assert ec["g_star_KK"] > ec["g_star_BBN"]

    def test_entropy_consistent_flag(self):
        ec = entropy_conservation_check()
        assert ec["entropy_consistent"] is True

    def test_t_ratio_large(self):
        ec = entropy_conservation_check()
        # T_KK / T_BBN ~ 10^6
        assert ec["t_ratio_KK_over_BBN"] > 1e5


class TestFullReport:
    def test_returns_dict(self):
        r = thermal_history_full_report()
        assert isinstance(r, dict)

    def test_pillar_number(self):
        r = thermal_history_full_report()
        assert r["pillar"] == 329

    def test_inputs_correct(self):
        r = thermal_history_full_report()
        assert r["inputs"]["n_w"] == 5
        assert r["inputs"]["k_cs"] == 74

    def test_has_timeline(self):
        r = thermal_history_full_report()
        assert "timeline" in r
        assert len(r["timeline"]) == 5

    def test_has_gw_signal(self):
        r = thermal_history_full_report()
        assert "gw_signal" in r
        assert r["gw_signal"]["peak_frequency_hz"] > 0

    def test_has_summary(self):
        r = thermal_history_full_report()
        assert "summary" in r

    def test_raises_on_wrong_n_w(self):
        with pytest.raises(ValueError):
            thermal_history_full_report(n_w=7, k_cs=74)

    def test_raises_on_wrong_k_cs(self):
        with pytest.raises(ValueError):
            thermal_history_full_report(n_w=5, k_cs=100)

    def test_n_derived_nonzero(self):
        r = thermal_history_full_report()
        assert r["summary"]["n_derived"] >= 2

    def test_primary_falsifier_present(self):
        r = thermal_history_full_report()
        assert "LiteBIRD" in r["summary"]["primary_falsifier"]
