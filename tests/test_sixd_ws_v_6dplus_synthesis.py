# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
test_sixd_ws_v_6dplus_synthesis.py — Tests for WS-V: 6D+ Full Geometry
Synthesis (P5 Higgs mass and P16 solar splitting).

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math

import pytest

from src.sixd.ws_v_6dplus_synthesis import (
    DM2_21_PDG,
    DM2_31_PDG,
    F_6D_GEOMETRIC,
    F_6D_TARGET,
    K_CS,
    M_H_5D_ESTIMATE,
    M_H_6D_ESTIMATE,
    M_H_PDG,
    N_C,
    N_W,
    PI_KR,
    RATIO_PDG,
    THETA_HR_ESTIMATE,
    TORSION_SPLIT_FACTOR,
    p5_higgs_6d_estimate,
    p16_solar_split_6d_estimate,
    ws_v_readiness_assessment,
)


class TestConstants:
    def test_k_cs(self):
        assert K_CS == 74

    def test_n_w(self):
        assert N_W == 5

    def test_n_c(self):
        assert N_C == 3

    def test_pi_kr(self):
        assert PI_KR == 37.0

    def test_m_h_pdg(self):
        assert M_H_PDG == pytest.approx(125.25, rel=1e-6)

    def test_m_h_5d_estimate(self):
        assert M_H_5D_ESTIMATE == pytest.approx(125.0, rel=1e-6)

    def test_theta_hr_estimate(self):
        expected = (3.0 / 74.0) ** 2
        assert THETA_HR_ESTIMATE == pytest.approx(expected, rel=1e-6)

    def test_theta_hr_positive_small(self):
        assert 0 < THETA_HR_ESTIMATE < 0.01

    def test_m_h_6d_estimate(self):
        expected = 125.25 * (1.0 + (3.0 / 74.0) ** 2)
        assert M_H_6D_ESTIMATE == pytest.approx(expected, rel=1e-6)

    def test_m_h_6d_above_pdg(self):
        # 6D correction pushes mass slightly above PDG value
        assert M_H_6D_ESTIMATE > M_H_PDG

    def test_dm2_21_pdg(self):
        assert DM2_21_PDG == pytest.approx(7.53e-5, rel=1e-6)

    def test_dm2_31_pdg(self):
        assert DM2_31_PDG == pytest.approx(2.453e-3, rel=1e-6)

    def test_ratio_pdg(self):
        expected = 7.53e-5 / 2.453e-3
        assert RATIO_PDG == pytest.approx(expected, rel=1e-6)

    def test_torsion_split_factor(self):
        expected = 1.0 / (2.0 * 74) ** 2
        assert TORSION_SPLIT_FACTOR == pytest.approx(expected, rel=1e-6)

    def test_f_6d_target(self):
        expected = RATIO_PDG / TORSION_SPLIT_FACTOR
        assert F_6D_TARGET == pytest.approx(expected, rel=1e-6)

    def test_f_6d_geometric(self):
        expected = 2.0 * 74 ** 2 / 3.0
        assert F_6D_GEOMETRIC == pytest.approx(expected, rel=1e-6)

    def test_f_6d_geometric_larger_than_target(self):
        assert F_6D_GEOMETRIC > F_6D_TARGET


class TestP5HiggsEstimate:
    @pytest.fixture
    def result(self):
        return p5_higgs_6d_estimate()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_expected_keys(self, result):
        expected = {
            "theta_hr_estimate",
            "m_h_5d_gev",
            "m_h_6d_gev",
            "m_h_pdg_gev",
            "residual_5d_pct",
            "residual_6d_pct",
            "improvement_pct",
            "status",
            "path_to_closure",
            "score_current",
            "score_if_6d_closed",
        }
        assert expected.issubset(result.keys())

    def test_theta_hr_positive(self, result):
        assert result["theta_hr_estimate"] > 0

    def test_m_h_6d_finite(self, result):
        assert math.isfinite(result["m_h_6d_gev"])

    def test_m_h_pdg_matches(self, result):
        assert result["m_h_pdg_gev"] == pytest.approx(125.25, rel=1e-6)

    def test_residuals_positive(self, result):
        assert result["residual_5d_pct"] > 0
        assert result["residual_6d_pct"] >= 0

    def test_6d_reduces_residual(self, result):
        # 6D estimate is closer to PDG than 5D estimate
        assert result["residual_6d_pct"] < result["residual_5d_pct"]

    def test_improvement_positive(self, result):
        assert result["improvement_pct"] > 0

    def test_status_contains_architecture_limit(self, result):
        assert "ARCHITECTURE_LIMIT" in result["status"]

    def test_score_current_low(self, result):
        assert result["score_current"] < result["score_if_6d_closed"]

    def test_residual_6d_below_5_pct(self, result):
        # 6D estimate must be within 5% of PDG
        assert result["residual_6d_pct"] < 5.0


class TestP16SolarSplitEstimate:
    @pytest.fixture
    def result(self):
        return p16_solar_split_6d_estimate()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_expected_keys(self, result):
        expected = {
            "ratio_pdg",
            "torsion_split_factor",
            "f_6d_target",
            "f_6d_geometric",
            "ratio_geometric",
            "ratio_residual_pct",
            "overshoot_factor",
            "status",
            "gap_summary",
            "path_to_closure",
        }
        assert expected.issubset(result.keys())

    def test_ratio_pdg_matches(self, result):
        assert result["ratio_pdg"] == pytest.approx(RATIO_PDG, rel=1e-6)

    def test_ratio_geometric_finite(self, result):
        assert math.isfinite(result["ratio_geometric"])

    def test_ratio_geometric_positive(self, result):
        assert result["ratio_geometric"] > 0

    def test_overshoot_factor_greater_than_one(self, result):
        # Geometric estimate overshoots the target
        assert result["overshoot_factor"] > 1.0

    def test_status_geometric_estimate(self, result):
        assert "GEOMETRIC_ESTIMATE" in result["status"]

    def test_residual_pct_positive_large(self, result):
        # Known gap: geometric estimate overshoots by ~5×, so residual >> 20%
        assert result["ratio_residual_pct"] > 20.0


class TestReadinessAssessment:
    @pytest.fixture
    def result(self):
        return ws_v_readiness_assessment()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_expected_keys(self, result):
        expected = {
            "workstream",
            "title",
            "p5_assessment",
            "p16_assessment",
            "prerequisites",
            "ready_to_execute",
            "readiness_blockers",
            "overall_status",
        }
        assert expected.issubset(result.keys())

    def test_workstream_label(self, result):
        assert result["workstream"] == "WS-V"

    def test_not_ready(self, result):
        # Prerequisites not yet met
        assert result["ready_to_execute"] is False

    def test_prerequisites_non_empty(self, result):
        assert len(result["prerequisites"]) > 0

    def test_blockers_non_empty(self, result):
        assert len(result["readiness_blockers"]) > 0

    def test_sub_assessments_are_dicts(self, result):
        assert isinstance(result["p5_assessment"], dict)
        assert isinstance(result["p16_assessment"], dict)
