# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 328 — CKM Cabibbo Anomaly from Braid Geometry."""
import math
import pytest

from src.core.pillar328_ckm_cabibbo_anomaly import (
    N_W, K_CS, PI_KR, M_KK_GEV,
    V_UD_EXP, V_US_EXP, V_UB_EXP,
    V_UD_UNC, V_US_UNC, V_UB_UNC,
    V_UD_UM, V_US_UM, V_UB_UM,
    SIGMA1_EXP, SIGMA1_UNC, CABIBBO_DEFICIT, CABIBBO_SIGNIFICANCE,
    LAMBDA_WLF, A_WLF, RHO_BAR, ETA_BAR,
    M_W_GEV,
    separation_guard,
    ckm_first_row_sum,
    kk_w_correction_to_vud,
    kk_corrected_first_row_sum,
    cabibbo_anomaly_analysis,
    lhcb_belle2_predictions,
    ckm_unitarity_full_report,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_v_ud_exp_range(self):
        assert 0.97 < V_UD_EXP < 0.98

    def test_v_us_exp_range(self):
        assert 0.22 < V_US_EXP < 0.23

    def test_v_ub_exp_small(self):
        assert V_UB_EXP < 0.01

    def test_experimental_sum_less_than_one(self):
        assert SIGMA1_EXP < 1.0

    def test_cabibbo_deficit_positive(self):
        assert CABIBBO_DEFICIT > 0.0

    def test_cabibbo_significance_moderate(self):
        # Known ~2-4 sigma
        assert 1.0 < CABIBBO_SIGNIFICANCE < 10.0

    def test_um_wolfenstein_lambda(self):
        assert 0.20 < LAMBDA_WLF < 0.25

    def test_m_w_gev(self):
        assert 80.0 < M_W_GEV < 81.0


class TestSeparationGuard:
    def test_string(self):
        assert isinstance(separation_guard(), str)

    def test_adjacent(self):
        assert "ADJACENT" in separation_guard()


class TestCkmFirstRowSum:
    def test_experimental_consistent(self):
        s = ckm_first_row_sum(V_UD_EXP, V_US_EXP, V_UB_EXP)
        assert abs(s - SIGMA1_EXP) < 1e-10

    def test_exact_unitarity(self):
        # V_ud = 1, V_us = 0, V_ub = 0 → sum = 1
        s = ckm_first_row_sum(1.0, 0.0, 0.0)
        assert s == 1.0

    def test_positive(self):
        assert ckm_first_row_sum() >= 0.0

    def test_um_prediction_near_unity(self):
        s = ckm_first_row_sum(V_UD_UM, V_US_UM, V_UB_UM)
        # UM should give near-exact unitarity (within Wolfenstein truncation)
        assert abs(s - 1.0) < 0.01


class TestKkWCorrection:
    def test_positive(self):
        delta = kk_w_correction_to_vud()
        assert delta > 0.0

    def test_small(self):
        # (M_W/M_KK)^2 ~ (80/1040)^2 ~ 6e-3
        delta = kk_w_correction_to_vud()
        assert 1e-4 < delta < 1e-1

    def test_decreases_with_heavier_kk(self):
        d1 = kk_w_correction_to_vud(m_kk_gev=1000.0)
        d2 = kk_w_correction_to_vud(m_kk_gev=5000.0)
        assert d1 > d2

    def test_formula(self):
        delta = kk_w_correction_to_vud(m_kk_gev=1040.0, m_w_gev=80.0, v_ud=0.97)
        expected = 0.97 ** 2 * (80.0 / 1040.0) ** 2
        assert abs(delta - expected) < 1e-10


class TestKkCorrectedSum:
    def test_returns_dict(self):
        r = kk_corrected_first_row_sum()
        assert isinstance(r, dict)

    def test_measured_larger_than_true(self):
        r = kk_corrected_first_row_sum()
        # KK correction is positive, so measured > true
        assert r["sigma_measured_kk"] > r["sigma_true"]

    def test_delta_vud_positive(self):
        r = kk_corrected_first_row_sum()
        assert r["delta_vud_sq_kk"] > 0.0


class TestCabiboAnomalyAnalysis:
    def test_returns_dict(self):
        r = cabibbo_anomaly_analysis()
        assert isinstance(r, dict)

    def test_experimental_section(self):
        r = cabibbo_anomaly_analysis()
        assert "experimental" in r
        assert abs(r["experimental"]["sigma_1"] - SIGMA1_EXP) < 1e-10

    def test_um_exact_unitarity(self):
        r = cabibbo_anomaly_analysis()
        sigma_true = r["um_prediction"]["sigma_1_true"]
        # UM should be very close to 1 by construction
        assert abs(sigma_true - 1.0) < 0.01

    def test_kk_does_not_explain_anomaly(self):
        r = cabibbo_anomaly_analysis()
        assert r["kk_explains_anomaly"] is False

    def test_verdict_string(self):
        r = cabibbo_anomaly_analysis()
        assert isinstance(r["verdict"], str)


class TestLhcbBelle2Predictions:
    def test_returns_dict(self):
        r = lhcb_belle2_predictions()
        assert isinstance(r, dict)

    def test_sin2beta_range(self):
        r = lhcb_belle2_predictions()
        # sin(2β) should be in [0.5, 0.9] range
        assert 0.3 < r["sin_2beta"] < 1.0

    def test_gamma_range(self):
        r = lhcb_belle2_predictions()
        # γ should be ~ 60-70 degrees
        assert 40.0 < r["gamma_deg"] < 90.0

    def test_v_ub_over_v_cb_small(self):
        r = lhcb_belle2_predictions()
        ratio = r["v_ub_over_v_cb"]
        # ~ |V_ub/V_cb| ~ 0.09
        assert 0.01 < ratio < 0.5

    def test_tension_sigma_finite(self):
        r = lhcb_belle2_predictions()
        assert r["sin2beta_tension_sigma"] >= 0.0
        assert r["gamma_tension_sigma"] >= 0.0

    def test_experimental_context(self):
        r = lhcb_belle2_predictions()
        assert "sin2beta_exp" in r["experimental_context"]


class TestFullReport:
    def setup_method(self):
        self.r = ckm_unitarity_full_report()

    def test_pillar_number(self):
        assert self.r["pillar"] == 328

    def test_adjacency(self):
        assert self.r["adjacency"] == "NON_HARDGATE_ADJACENT"

    def test_physics_summary(self):
        assert isinstance(self.r["physics_summary"], str)
        assert len(self.r["physics_summary"]) > 100

    def test_honest_assessment(self):
        assert isinstance(self.r["honest_assessment"], str)
        assert "anomaly" in self.r["honest_assessment"].lower()

    def test_falsifier(self):
        assert isinstance(self.r["falsifier"], str)

    def test_m_kk_tev(self):
        assert 0.5 < self.r["m_kk_tev"] < 5.0

    def test_cabibbo_section(self):
        ca = self.r["cabibbo_anomaly"]
        assert "experimental" in ca
        assert "um_prediction" in ca

    def test_lhcb_section(self):
        assert "sin_2beta" in self.r["lhcb_belle2"]
