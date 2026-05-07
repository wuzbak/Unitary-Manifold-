# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_pillar216_higgs_coleman_weinberg.py — Pillar 216 test suite."""
import math
import pytest
from src.core.pillar216_higgs_coleman_weinberg import (
    ARCHITECTURE_LIMIT,
    LAMBDA_H_PDG,
    M_H_GEV,
    V_EW_GEV,
    Y_T,
    M_KK_GEV,
    coleman_weinberg_correction,
    gauge_higgs_unification_lambda,
    higgs_mass_gap_quantification,
    pillar216_summary,
)


# ---------------------------------------------------------------------------
# Module-level flag
# ---------------------------------------------------------------------------
class TestArchitectureLimit:
    def test_flag_is_true(self):
        assert ARCHITECTURE_LIMIT is True

    def test_flag_is_bool(self):
        assert isinstance(ARCHITECTURE_LIMIT, bool)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
class TestConstants:
    def test_lambda_H_pdg_value(self):
        expected = M_H_GEV**2 / (2 * V_EW_GEV**2)
        assert abs(LAMBDA_H_PDG - expected) < 1e-6

    def test_lambda_H_pdg_range(self):
        assert 0.12 < LAMBDA_H_PDG < 0.14

    def test_v_ew_value(self):
        assert abs(V_EW_GEV - 246.22) < 0.01

    def test_m_H_pdg_value(self):
        assert abs(M_H_GEV - 125.25) < 0.01

    def test_y_t_range(self):
        assert 0.68 < Y_T < 0.72

    def test_m_kk_gev(self):
        assert abs(M_KK_GEV - 1000.0) < 1.0


# ---------------------------------------------------------------------------
# Coleman-Weinberg correction
# ---------------------------------------------------------------------------
class TestColemanWeinbergCorrection:
    def setup_method(self):
        self.result = coleman_weinberg_correction()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_has_delta_lambda(self):
        assert "delta_lambda_cw" in self.result

    def test_delta_lambda_negative(self):
        assert self.result["delta_lambda_cw"] < 0

    def test_delta_lambda_perturbative(self):
        assert abs(self.result["delta_lambda_cw"]) < 0.5

    def test_delta_lambda_small(self):
        assert abs(self.result["delta_lambda_cw"]) < 0.1

    def test_has_m_H_cw(self):
        assert "m_H_cw_gev" in self.result

    def test_m_H_cw_positive(self):
        assert self.result["m_H_cw_gev"] > 0

    def test_m_H_cw_reasonable(self):
        assert 50.0 < self.result["m_H_cw_gev"] < 300.0

    def test_has_pct_correction(self):
        assert "pct_correction" in self.result

    def test_pct_correction_positive(self):
        assert self.result["pct_correction"] > 0

    def test_pct_correction_lt_100(self):
        assert self.result["pct_correction"] < 100.0

    def test_pct_correction_gt_1(self):
        assert self.result["pct_correction"] > 1.0

    def test_has_lambda_H_pdg(self):
        assert "lambda_H_pdg" in self.result

    def test_lambda_H_pdg_matches(self):
        assert abs(self.result["lambda_H_pdg"] - LAMBDA_H_PDG) < 1e-10

    def test_has_y_t(self):
        assert "y_t" in self.result

    def test_y_t_value(self):
        assert abs(self.result["y_t"] - Y_T) < 1e-10

    def test_has_cutoff(self):
        assert "cutoff_gev" in self.result

    def test_cutoff_1tev(self):
        assert abs(self.result["cutoff_gev"] - 1000.0) < 1.0

    def test_log_factor_positive(self):
        log_factor = math.log((M_KK_GEV / 172.76) ** 2)
        assert log_factor > 0


# ---------------------------------------------------------------------------
# Gauge-Higgs unification lambda
# ---------------------------------------------------------------------------
class TestGaugeHiggsUnificationLambda:
    def setup_method(self):
        self.result = gauge_higgs_unification_lambda()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_has_lambda_ghu(self):
        assert "lambda_H_ghu" in self.result

    def test_lambda_ghu_positive(self):
        assert self.result["lambda_H_ghu"] > 0

    def test_lambda_ghu_small(self):
        assert self.result["lambda_H_ghu"] < 0.02

    def test_lambda_ghu_far_from_pdg(self):
        assert self.result["lambda_H_ghu"] < LAMBDA_H_PDG * 0.2

    def test_has_pct_error(self):
        assert "pct_error_vs_pdg" in self.result

    def test_pct_error_large(self):
        assert self.result["pct_error_vs_pdg"] > 50.0

    def test_has_status(self):
        assert "status" in self.result

    def test_status_is_architecture_limit(self):
        assert self.result["status"] == "ARCHITECTURE_LIMIT"

    def test_has_lambda_H_pdg(self):
        assert "lambda_H_pdg" in self.result

    def test_lambda_H_pdg_matches(self):
        assert abs(self.result["lambda_H_pdg"] - LAMBDA_H_PDG) < 1e-10


# ---------------------------------------------------------------------------
# Higgs mass gap quantification
# ---------------------------------------------------------------------------
class TestHiggsMassGapQuantification:
    def setup_method(self):
        self.result = higgs_mass_gap_quantification()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_has_lambda_pdg(self):
        assert "lambda_H_pdg" in self.result

    def test_has_best_geo(self):
        assert "best_geo_estimate" in self.result

    def test_best_geo_positive(self):
        assert self.result["best_geo_estimate"] > 0

    def test_has_gap_factor(self):
        assert "gap_factor" in self.result

    def test_gap_factor_gt_2(self):
        assert self.result["gap_factor"] > 2.0

    def test_gap_factor_gt_10(self):
        assert self.result["gap_factor"] > 10.0

    def test_has_gap_explanation(self):
        assert "gap_explanation" in self.result

    def test_gap_explanation_nonempty(self):
        assert len(self.result["gap_explanation"]) > 10

    def test_has_m_H_pdg(self):
        assert "m_H_pdg_gev" in self.result

    def test_m_H_pdg_value(self):
        assert abs(self.result["m_H_pdg_gev"] - M_H_GEV) < 0.01


# ---------------------------------------------------------------------------
# pillar216_summary
# ---------------------------------------------------------------------------
class TestPillar216Summary:
    def setup_method(self):
        self.result = pillar216_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_number(self):
        assert self.result["pillar"] == 216

    def test_architecture_limit_true(self):
        assert self.result["architecture_limit"] is True

    def test_p5_status_contains_architecture_limit(self):
        assert "ARCHITECTURE LIMIT" in self.result["p5_status"]

    def test_lambda_H_pdg(self):
        assert abs(self.result["lambda_H_pdg"] - LAMBDA_H_PDG) < 1e-10

    def test_m_H_pdg(self):
        assert abs(self.result["m_H_pdg_gev"] - M_H_GEV) < 0.01

    def test_has_cw_correction(self):
        assert "cw_correction" in self.result
        assert isinstance(self.result["cw_correction"], dict)

    def test_has_ghu_lambda(self):
        assert "ghu_lambda" in self.result
        assert isinstance(self.result["ghu_lambda"], dict)

    def test_has_gap_quantification(self):
        assert "gap_quantification" in self.result
        assert isinstance(self.result["gap_quantification"], dict)

    def test_toe_delta_zero(self):
        assert self.result["toe_delta"] == 0

    def test_conclusion_nonempty(self):
        assert len(self.result["conclusion"]) > 10

    def test_conclusion_mentions_bsm(self):
        assert "BSM" in self.result["conclusion"] or "brane" in self.result["conclusion"].lower()

    def test_cw_delta_negative(self):
        assert self.result["cw_correction"]["delta_lambda_cw"] < 0

    def test_ghu_status_architecture_limit(self):
        assert self.result["ghu_lambda"]["status"] == "ARCHITECTURE_LIMIT"

    def test_gap_factor_gt_2(self):
        assert self.result["gap_quantification"]["gap_factor"] > 2.0
