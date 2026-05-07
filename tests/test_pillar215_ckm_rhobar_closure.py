# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_pillar215_ckm_rhobar_closure.py — Pillar 215 tests."""
from __future__ import annotations
import math
import pytest
from src.core.pillar215_ckm_rhobar_closure import (
    delta_wzw_deg, delta_q_deg, pi_kr_color_correction,
    ckm_predictions_wzw, ckm_predictions_q,
    rhobar_residual_diagnosis, pillar215_summary,
    N_W, N1_BRAID, N2_BRAID, K_CS, N_C, PI_K_R,
    W_RHOBAR_PDG, W_ETABAR_PDG, DELTA_CP_PDG_DEG,
)

class TestDeltaWzw:
    def test_returns_float(self): assert isinstance(delta_wzw_deg(), float)
    def test_approx_71_08(self): assert abs(delta_wzw_deg() - 71.08) < 0.1
    def test_positive(self): assert delta_wzw_deg() > 0
    def test_less_than_90(self): assert delta_wzw_deg() < 90
    def test_formula(self): assert abs(delta_wzw_deg() - math.degrees(math.asin(35/37))) < 1e-10

class TestDeltaQ:
    def test_returns_float(self): assert isinstance(delta_q_deg(), float)
    def test_approx_68_52(self): assert abs(delta_q_deg() - 68.52) < 0.1
    def test_less_than_wzw(self): assert delta_q_deg() < delta_wzw_deg()
    def test_matches_pdg(self): assert abs(delta_q_deg() - DELTA_CP_PDG_DEG) < 0.1
    def test_positive(self): assert delta_q_deg() > 0
    def test_formula(self): assert abs(delta_q_deg() - math.degrees(math.asin(35/37.6))) < 1e-10
    def test_pdg_error_tiny(self): assert abs(delta_q_deg() - 68.5) < 0.1

class TestPiKrCorrection:
    def test_value(self): assert pi_kr_color_correction() == pytest.approx(0.6)
    def test_is_n_c_over_n_w(self): assert pi_kr_color_correction() == N_C / N_W
    def test_returns_float(self): assert isinstance(pi_kr_color_correction(), float)

class TestCkmPredictionsWzw:
    def setup_method(self): self.p = ckm_predictions_wzw()
    def test_returns_dict(self): assert isinstance(self.p, dict)
    def test_keys(self):
        for k in ("delta_deg","R_b_geo","rhobar","etabar","rhobar_pct_err","etabar_pct_err"):
            assert k in self.p
    def test_delta_deg(self): assert abs(self.p["delta_deg"] - 71.08) < 0.1
    def test_rhobar_positive(self): assert self.p["rhobar"] > 0
    def test_etabar_positive(self): assert self.p["etabar"] > 0
    def test_rhobar_pct_err_gt_20(self): assert self.p["rhobar_pct_err"] > 20
    def test_etabar_pct_err_lt_5(self): assert self.p["etabar_pct_err"] < 5
    def test_r_b_geo_positive(self): assert self.p["R_b_geo"] > 0
    def test_r_b_geo_reasonable(self): assert 0.3 < self.p["R_b_geo"] < 0.5

class TestCkmPredictionsQ:
    def setup_method(self): self.p = ckm_predictions_q()
    def test_returns_dict(self): assert isinstance(self.p, dict)
    def test_keys(self):
        for k in ("delta_deg","R_b_geo","rhobar","etabar","rhobar_pct_err","etabar_pct_err","pi_kr_eff"):
            assert k in self.p
    def test_delta_deg(self): assert abs(self.p["delta_deg"] - 68.52) < 0.1
    def test_rhobar_pct_err_lt_20(self): assert self.p["rhobar_pct_err"] < 20
    def test_rhobar_pct_err_gt_5(self): assert self.p["rhobar_pct_err"] > 5
    def test_etabar_pct_err_lt_1(self): assert self.p["etabar_pct_err"] < 1.0
    def test_pi_kr_eff(self): assert abs(self.p["pi_kr_eff"] - 37.6) < 1e-10
    def test_improvement_over_wzw(self):
        wzw = ckm_predictions_wzw()
        assert wzw["rhobar_pct_err"] > self.p["rhobar_pct_err"]
    def test_etabar_near_pdg(self): assert abs(self.p["etabar"] - W_ETABAR_PDG) / W_ETABAR_PDG < 0.01
    def test_rhobar_positive(self): assert self.p["rhobar"] > 0

class TestResidualDiagnosis:
    def setup_method(self): self.d = rhobar_residual_diagnosis()
    def test_returns_dict(self): assert isinstance(self.d, dict)
    def test_keys(self):
        for k in ("R_b_geo","R_b_pdg","R_b_gap_pct","cos_delta_q",
                  "cos_delta_sensitivity","rhobar_pct_err","path_to_closure","p14_status"):
            assert k in self.d
    def test_r_b_gap_positive(self): assert self.d["R_b_gap_pct"] > 0
    def test_r_b_gap_small(self): assert self.d["R_b_gap_pct"] < 10
    def test_cos_delta_reasonable(self): assert 0 < self.d["cos_delta_q"] < 1
    def test_path_mentions_fermion(self): assert "fermion" in self.d["path_to_closure"].lower()
    def test_p14_status_geometric(self): assert "GEOMETRIC ESTIMATE" in self.d["p14_status"]

class TestPillar215Summary:
    def setup_method(self): self.s = pillar215_summary()
    def test_returns_dict(self): assert isinstance(self.s, dict)
    def test_pillar_number(self): assert self.s["pillar"] == 215
    def test_delta_wzw(self): assert abs(self.s["delta_wzw_deg"] - 71.08) < 0.1
    def test_delta_q(self): assert abs(self.s["delta_q_deg"] - 68.52) < 0.1
    def test_delta_pdg(self): assert self.s["delta_cp_pdg_deg"] == 68.5
    def test_color_correction(self): assert self.s["pi_kr_color_correction"] == pytest.approx(0.6)
    def test_wzw_predictions_dict(self): assert isinstance(self.s["wzw_predictions"], dict)
    def test_q_predictions_dict(self): assert isinstance(self.s["q_predictions"], dict)
    def test_improvement_positive(self): assert self.s["improvement_rhobar_pct"] > 0
    def test_etabar_pct_err_q_lt_1(self): assert self.s["etabar_pct_err_q"] < 1.0
    def test_honest_status_str(self): assert isinstance(self.s["honest_status"], str)
    def test_p14_status_geometric(self): assert "GEOMETRIC ESTIMATE" in self.s["p14_status"]
    def test_toe_delta_zero(self): assert self.s["toe_delta"] == 0
    def test_residual_diagnosis_dict(self): assert isinstance(self.s["residual_diagnosis"], dict)
    def test_delta_q_closer_to_pdg(self):
        assert abs(self.s["delta_q_deg"] - 68.5) < abs(self.s["delta_wzw_deg"] - 68.5)

class TestConstants:
    def test_n_w(self): assert N_W == 5
    def test_n_c(self): assert N_C == 3
    def test_k_cs(self): assert K_CS == 74
    def test_pi_k_r(self): assert PI_K_R == 37.0
    def test_n1_n2(self): assert N1_BRAID * N2_BRAID == 35
    def test_pdg_delta(self): assert DELTA_CP_PDG_DEG == 68.5
