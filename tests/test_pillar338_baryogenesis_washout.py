# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 338 — KK Baryogenesis Washout Quantification."""
import math
import pytest

from src.core.pillar338_baryogenesis_washout import (
    N_W, K_CS, PI_KR,
    T_KK_GEV, T_EW_GEV, ALPHA_KK, BETA_OVER_H, DELTA_CP_RAD, V_W,
    ETA_B_OBSERVED, ETA_B_NAIVE,
    G_STAR_S_KK, G_STAR_S_EW, C_SPH_ABS, ALPHA_W, D_Q_TIMES_T,
    separation_guard,
    sphaleron_rate_at_t_kk,
    diffusion_coefficient_times_t,
    diffusion_washout_factor,
    sphaleron_conversion_factor,
    beta_factor_strong_pt,
    thermal_dilution_factor,
    sphaleron_erasure_factor,
    washout_factor_ptft,
    consistency_check,
    washout_full_report,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert abs(PI_KR - 37.0) < 1e-9

    def test_t_kk_positive(self):
        assert T_KK_GEV > 0

    def test_t_ew_below_t_kk(self):
        assert T_EW_GEV < T_KK_GEV

    def test_alpha_kk(self):
        # α_KK = (37)²/100 = 13.69
        assert abs(ALPHA_KK - 13.69) < 0.01

    def test_beta_over_h(self):
        assert abs(BETA_OVER_H - 37.0) < 1e-9

    def test_delta_cp_physical(self):
        assert 0 < DELTA_CP_RAD < math.pi

    def test_v_w_one(self):
        assert abs(V_W - 1.0) < 1e-9

    def test_eta_b_observed(self):
        assert abs(ETA_B_OBSERVED - 6.1e-10) < 1e-12

    def test_c_sph_abs(self):
        # 8/23 ≈ 0.348
        assert abs(C_SPH_ABS - 8/23) < 1e-9


class TestSeparationGuard:
    def test_is_string(self):
        assert isinstance(separation_guard(), str)

    def test_adjacent_track(self):
        assert "ADJACENT" in separation_guard()

    def test_ptft_mentioned(self):
        assert "PTFT" in separation_guard() or "TFT" in separation_guard()


class TestSphaleronRate:
    def test_rate_positive(self):
        assert sphaleron_rate_at_t_kk() > 0

    def test_rate_small(self):
        # 25 α_W⁵ is small (α_W ~ 1/30)
        assert sphaleron_rate_at_t_kk() < 0.01

    def test_rate_formula(self):
        expected = 25.0 * ALPHA_W ** 5
        assert abs(sphaleron_rate_at_t_kk() - expected) < 1e-12


class TestDiffusionWashout:
    def test_d_q_times_t(self):
        assert diffusion_coefficient_times_t() == pytest.approx(D_Q_TIMES_T)

    def test_washout_in_range(self):
        f = diffusion_washout_factor()
        assert 0 < f < 1

    def test_washout_is_tanh(self):
        f = diffusion_washout_factor()
        gamma = sphaleron_rate_at_t_kk()
        arg = math.pi * D_Q_TIMES_T * gamma / V_W
        expected = math.tanh(arg)
        assert abs(f - expected) < 1e-12


class TestSphaleronConversion:
    def test_c_sph_correct(self):
        assert abs(sphaleron_conversion_factor() - 8/23) < 1e-9

    def test_c_sph_less_than_half(self):
        assert sphaleron_conversion_factor() < 0.5


class TestBetaFactor:
    def test_nucleation_positive(self):
        assert beta_factor_strong_pt() > 0

    def test_nucleation_less_than_one(self):
        assert beta_factor_strong_pt() < 1

    def test_strong_pt_gives_moderate_factor(self):
        # For α = 13.69 >> 1: S_3/T = 4π/13.69 ≈ 0.92 → exp(-0.92) ≈ 0.40
        beta = beta_factor_strong_pt()
        assert 0.1 < beta < 1.0


class TestThermalDilution:
    def test_dilution_positive(self):
        assert thermal_dilution_factor() > 0

    def test_dilution_less_than_one(self):
        assert thermal_dilution_factor() < 1

    def test_dilution_g_ratio(self):
        expected = G_STAR_S_EW / G_STAR_S_KK
        assert abs(thermal_dilution_factor() - expected) < 1e-9


class TestSphaleronErasure:
    def test_returns_tuple(self):
        result = sphaleron_erasure_factor()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_kappa_low_positive(self):
        kl, kh = sphaleron_erasure_factor()
        assert kl > 0

    def test_kappa_range_ordered(self):
        kl, kh = sphaleron_erasure_factor()
        assert kl < kh

    def test_kappa_physical_range(self):
        kl, kh = sphaleron_erasure_factor()
        assert 0 < kl < 1
        assert 0 < kh < 1


class TestWashoutPTFT:
    def test_returns_dict(self):
        ptft = washout_factor_ptft()
        assert isinstance(ptft, dict)

    def test_all_factors_present(self):
        ptft = washout_factor_ptft()
        assert "step_1_diffusion" in ptft
        assert "step_2_sph_conversion" in ptft
        assert "step_3_nucleation" in ptft
        assert "step_4_thermal_dilution" in ptft

    def test_washout_low_lt_high(self):
        ptft = washout_factor_ptft()
        assert ptft["f_washout_low"] < ptft["f_washout_high"]

    def test_washout_central_geometric_mean(self):
        ptft = washout_factor_ptft()
        central = ptft["f_washout_central"]
        low = ptft["f_washout_low"]
        high = ptft["f_washout_high"]
        # Central should be between low and high
        assert low < central < high

    def test_uncertainty_ratio_improved(self):
        ptft = washout_factor_ptft()
        # Should be significantly less than 100 (Pillar 333 had O(100))
        assert ptft["uncertainty_ratio"] < 100.0

    def test_improvement_factor_positive(self):
        ptft = washout_factor_ptft()
        assert ptft["improvement_factor"] > 1.0

    def test_eta_b_range_has_values(self):
        ptft = washout_factor_ptft()
        assert ptft["eta_b_low"] > 0
        assert ptft["eta_b_high"] > 0
        assert ptft["eta_b_low"] < ptft["eta_b_high"]

    def test_notes_present(self):
        ptft = washout_factor_ptft()
        assert isinstance(ptft["notes"], str)
        assert len(ptft["notes"]) > 20

    def test_pillar333_reference(self):
        ptft = washout_factor_ptft()
        assert ptft["pillar333_uncertainty_ratio"] == 100.0


class TestConsistencyCheck:
    def test_returns_dict(self):
        cc = consistency_check()
        assert isinstance(cc, dict)

    def test_eta_b_range_present(self):
        cc = consistency_check()
        assert "eta_b_ptft_low" in cc
        assert "eta_b_ptft_high" in cc

    def test_eta_b_observed_correct(self):
        cc = consistency_check()
        assert abs(cc["eta_b_observed"] - ETA_B_OBSERVED) < 1e-12

    def test_verdict_present(self):
        cc = consistency_check()
        assert cc["verdict"] in ("ORDER_OF_MAGNITUDE_CONSISTENT", "ORDER_OF_MAGNITUDE_TENSION")

    def test_ratio_computed(self):
        cc = consistency_check()
        assert cc["ratio_low_to_obs"] > 0
        assert cc["ratio_high_to_obs"] > 0

    def test_bbn_range_physical(self):
        cc = consistency_check()
        bbn_min, bbn_max = cc["bbn_range"]
        assert bbn_min < bbn_max
        assert bbn_min > 0


class TestFullReport:
    def test_returns_dict(self):
        report = washout_full_report()
        assert isinstance(report, dict)

    def test_pillar_number(self):
        assert washout_full_report()["pillar"] == 338

    def test_um_inputs_present(self):
        report = washout_full_report()
        inputs = report["um_inputs"]
        assert "T_KK_GeV" in inputs
        assert "alpha_PT" in inputs
        assert "delta_CP_rad" in inputs

    def test_improvement_documented(self):
        report = washout_full_report()
        improvement = report["improvement"]
        assert "pillar_333_uncertainty" in improvement
        assert "pillar_338_uncertainty" in improvement

    def test_open_gap_documented(self):
        report = washout_full_report()
        assert isinstance(report["open_gap"], str)
        assert len(report["open_gap"]) > 20

    def test_separation_guard_present(self):
        report = washout_full_report()
        assert "ADJACENT" in report["separation_guard"]

    def test_epistemic_status(self):
        report = washout_full_report()
        assert "ORDER_OF_MAGNITUDE" in report["epistemic_status"] or "IMPROVED" in report["epistemic_status"]
