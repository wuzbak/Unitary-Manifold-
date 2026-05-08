# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
test_tend_ws_vi_cy3_synthesis.py — Tests for WS-VI: 10D CY₃ Full Moduli +
Flux Synthesis for P3 (α_s).

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math

import pytest

from src.tend.ws_vi_cy3_synthesis import (
    ALPHA_S_5D,
    ALPHA_S_CY3_CORRECTED,
    ALPHA_S_PDG,
    ALPHA_S_10D_ESTIMATE,
    DELTA_ALPHA_S_GAP,
    K_CS,
    N_FLUX,
    ws_vi_readiness_assessment,
    ws_vi_synthesis_report,
)


class TestConstants:
    def test_k_cs(self):
        assert K_CS == 74

    def test_n_flux(self):
        assert N_FLUX == 37

    def test_alpha_s_pdg(self):
        assert ALPHA_S_PDG == pytest.approx(0.1179, rel=1e-6)

    def test_alpha_s_5d_positive(self):
        assert ALPHA_S_5D > 0

    def test_alpha_s_5d_below_pdg(self):
        assert ALPHA_S_5D < ALPHA_S_PDG

    def test_delta_gap_positive(self):
        assert DELTA_ALPHA_S_GAP > 0

    def test_delta_gap_equals_diff(self):
        assert DELTA_ALPHA_S_GAP == pytest.approx(ALPHA_S_PDG - ALPHA_S_5D, rel=1e-6)

    def test_alpha_s_10d_between_5d_and_pdg(self):
        assert ALPHA_S_5D < ALPHA_S_10D_ESTIMATE

    def test_alpha_s_cy3_corrected_finite(self):
        assert math.isfinite(ALPHA_S_CY3_CORRECTED)

    def test_alpha_s_cy3_corrected_positive(self):
        assert ALPHA_S_CY3_CORRECTED > 0

    def test_alpha_s_cy3_larger_than_5d(self):
        assert ALPHA_S_CY3_CORRECTED > ALPHA_S_5D


class TestSynthesisReport:
    @pytest.fixture
    def report(self):
        return ws_vi_synthesis_report()

    def test_returns_dict(self, report):
        assert isinstance(report, dict)

    def test_expected_keys(self, report):
        expected = {
            "alpha_s_pdg",
            "alpha_s_5d",
            "alpha_s_10d_estimate",
            "alpha_s_cy3_full",
            "delta_gap_total",
            "delta_covered_10d",
            "delta_covered_full",
            "residual_5d_pct",
            "residual_10d_pct",
            "residual_full_pct",
            "kahler_shift",
            "cs_shift",
            "flux_shift",
            "ws_iv_gate",
            "status",
            "gap_narrative",
        }
        assert expected.issubset(report.keys())

    def test_alpha_s_pdg_matches(self, report):
        assert report["alpha_s_pdg"] == pytest.approx(ALPHA_S_PDG, rel=1e-6)

    def test_alpha_s_5d_matches(self, report):
        assert report["alpha_s_5d"] == pytest.approx(ALPHA_S_5D, rel=1e-6)

    def test_residuals_finite(self, report):
        assert math.isfinite(report["residual_5d_pct"])
        assert math.isfinite(report["residual_10d_pct"])
        assert math.isfinite(report["residual_full_pct"])

    def test_residuals_positive(self, report):
        assert report["residual_5d_pct"] > 0
        assert report["residual_full_pct"] > 0

    def test_full_residual_below_5d(self, report):
        # Full moduli/flux treatment should narrow the gap vs bare 5D
        assert report["residual_full_pct"] < report["residual_5d_pct"]

    def test_shifts_positive(self, report):
        assert report["kahler_shift"] > 0
        assert report["cs_shift"] > 0
        assert report["flux_shift"] > 0

    def test_delta_gap_total_matches(self, report):
        assert report["delta_gap_total"] == pytest.approx(DELTA_ALPHA_S_GAP, rel=1e-6)

    def test_delta_covered_full_positive(self, report):
        assert report["delta_covered_full"] > 0

    def test_ws_iv_gate_is_dict(self, report):
        assert isinstance(report["ws_iv_gate"], dict)
        assert "gate_pass" in report["ws_iv_gate"]

    def test_status_architecture_limit(self, report):
        assert "ARCHITECTURE_LIMIT" in report["status"]

    def test_gap_narrative_non_empty(self, report):
        assert len(report["gap_narrative"]) > 20


class TestReadinessAssessment:
    @pytest.fixture
    def result(self):
        return ws_vi_readiness_assessment()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_expected_keys(self, result):
        expected = {
            "workstream",
            "title",
            "current_best",
            "prerequisites",
            "ready_to_execute",
            "readiness_blockers",
            "overall_status",
        }
        assert expected.issubset(result.keys())

    def test_workstream_label(self, result):
        assert result["workstream"] == "WS-VI"

    def test_current_best_keys(self, result):
        expected = {"alpha_s_5d", "alpha_s_cy3_full", "alpha_s_pdg", "residual_pct"}
        assert expected.issubset(result["current_best"].keys())

    def test_current_best_residual_finite(self, result):
        assert math.isfinite(result["current_best"]["residual_pct"])

    def test_prerequisites_non_empty(self, result):
        assert len(result["prerequisites"]) > 0

    def test_blockers_non_empty(self, result):
        assert len(result["readiness_blockers"]) > 0

    def test_ready_to_execute_is_bool(self, result):
        assert isinstance(result["ready_to_execute"], bool)

    def test_overall_status_non_empty(self, result):
        assert len(result["overall_status"]) > 0
