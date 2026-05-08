# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/nined/cp_phase_9d_refinement.py — Track 2 (9D δ_CP Refinement)."""
from __future__ import annotations

import math
import pytest

from src.nined.cp_phase_9d_refinement import (
    ALPHA_9D,
    DELTA_CP_7D,
    DELTA_CP_PDG,
    GS_UNCERTAINTY_FRACTION,
    GS_FLUX_CONTRIBUTION,
    KK_9D_SCALE_RATIO,
    RESIDUAL_7D_PCT,
    RHOBAR_GATE_THRESHOLD_PCT,
    cp_phase_9d_gate_check,
    cp_phase_9d_summary,
    delta_cp_9d_correction,
    delta_cp_9d_uncertainty,
    delta_cp_9d_total,
    residual_pct_9d,
    rhobar_robustness_gate,
)


class TestConstants:
    def test_delta_cp_7d_is_pi_over_3(self):
        assert DELTA_CP_7D == pytest.approx(math.pi / 3, rel=1e-9)

    def test_delta_cp_pdg(self):
        assert DELTA_CP_PDG == pytest.approx(1.20, abs=0.001)

    def test_residual_7d_pct(self):
        assert RESIDUAL_7D_PCT == pytest.approx(12.7, abs=0.1)

    def test_kk_scale_ratio(self):
        assert KK_9D_SCALE_RATIO == pytest.approx(0.05, rel=1e-9)

    def test_gs_flux_contribution(self):
        assert GS_FLUX_CONTRIBUTION == pytest.approx(0.16, rel=1e-9)

    def test_alpha_9d(self):
        assert ALPHA_9D == pytest.approx(0.20, rel=1e-9)

    def test_gs_uncertainty_fraction(self):
        assert GS_UNCERTAINTY_FRACTION == pytest.approx(0.20, rel=1e-9)

    def test_rhobar_gate_threshold(self):
        assert RHOBAR_GATE_THRESHOLD_PCT == pytest.approx(5.0, rel=1e-9)

    def test_7d_residual_consistent(self):
        # Check RESIDUAL_7D_PCT is consistent with DELTA_CP_7D and DELTA_CP_PDG
        expected = abs(DELTA_CP_7D - DELTA_CP_PDG) / DELTA_CP_PDG * 100.0
        assert RESIDUAL_7D_PCT == pytest.approx(expected, rel=0.05)  # within 5% relative


class TestDeltaCP9DCorrection:
    def test_positive_correction(self):
        # Correction should be positive (moves toward PDG 1.20 rad)
        corr = delta_cp_9d_correction()
        assert corr > 0

    def test_correction_dominated_by_gs(self):
        # GS term >> KK term (KK is subleading n=2)
        gs_only = GS_FLUX_CONTRIBUTION * DELTA_CP_7D
        kk_only = ALPHA_9D * KK_9D_SCALE_RATIO**2
        assert gs_only > kk_only

    def test_kk_term_scales_quadratic(self):
        c1 = delta_cp_9d_correction(kk_ratio=0.05, gs_flux=0.0)
        c2 = delta_cp_9d_correction(kk_ratio=0.10, gs_flux=0.0)
        assert c2 == pytest.approx(4 * c1, rel=1e-9)

    def test_gs_term_scales_linearly(self):
        c1 = delta_cp_9d_correction(gs_flux=0.04, kk_ratio=0.0)
        c2 = delta_cp_9d_correction(gs_flux=0.08, kk_ratio=0.0)
        assert c2 == pytest.approx(2 * c1, rel=1e-9)

    def test_zero_params_zero_correction(self):
        corr = delta_cp_9d_correction(alpha_9d=0.0, kk_ratio=0.0, gs_flux=0.0)
        assert corr == pytest.approx(0.0, abs=1e-12)

    def test_returns_float(self):
        assert isinstance(delta_cp_9d_correction(), float)


class TestDeltaCP9DTotal:
    def test_greater_than_7d(self):
        # 9D correction adds to δ_CP → total > 7D baseline
        total = delta_cp_9d_total()
        assert total > DELTA_CP_7D

    def test_closer_to_pdg_than_7d(self):
        total = delta_cp_9d_total()
        dist_9d = abs(total - DELTA_CP_PDG)
        dist_7d = abs(DELTA_CP_7D - DELTA_CP_PDG)
        assert dist_9d < dist_7d

    def test_near_pdg(self):
        total = delta_cp_9d_total()
        assert abs(total - DELTA_CP_PDG) / DELTA_CP_PDG < 0.03

    def test_no_correction_equals_7d(self):
        total = delta_cp_9d_total(alpha_9d=0.0, kk_ratio=0.0, gs_flux=0.0)
        assert total == pytest.approx(DELTA_CP_7D, rel=1e-9)

    def test_additive_structure(self):
        total = delta_cp_9d_total()
        corr = delta_cp_9d_correction()
        assert total == pytest.approx(DELTA_CP_7D + corr, rel=1e-9)


class TestResidualPct9D:
    def test_improved_vs_7d(self):
        resid = residual_pct_9d()
        assert resid < RESIDUAL_7D_PCT

    def test_in_0_to_3_pct_range(self):
        resid = residual_pct_9d()
        assert 0.0 < resid < 3.0

    def test_below_gate_threshold(self):
        resid = residual_pct_9d()
        assert resid < RHOBAR_GATE_THRESHOLD_PCT

    def test_zero_correction_gives_7d_residual(self):
        resid = residual_pct_9d(alpha_9d=0.0, kk_ratio=0.0, gs_flux=0.0)
        expected = abs(DELTA_CP_7D - DELTA_CP_PDG) / DELTA_CP_PDG * 100.0
        assert resid == pytest.approx(expected, rel=1e-6)

    def test_returns_positive_float(self):
        resid = residual_pct_9d()
        assert resid > 0
        assert isinstance(resid, float)


class TestRhobarRobustnessGate:
    def test_small_uncertainty_passes(self):
        gate = rhobar_robustness_gate(0.01)  # 0.01/1.20 ≈ 0.83%
        assert gate["gate_pass"] is True

    def test_large_uncertainty_fails(self):
        gate = rhobar_robustness_gate(0.20)  # 0.20/1.20 ≈ 16.7%
        assert gate["gate_pass"] is False

    def test_uncertainty_pct_calculation(self):
        gate = rhobar_robustness_gate(0.06)  # 0.06/1.20 = 5%
        assert gate["uncertainty_pct"] == pytest.approx(5.0, rel=1e-6)

    def test_threshold_value(self):
        gate = rhobar_robustness_gate(0.0)
        assert gate["gate_threshold_pct"] == pytest.approx(5.0, rel=1e-9)

    def test_returns_required_keys(self):
        gate = rhobar_robustness_gate(0.1)
        for key in ["delta_cp_uncertainty_rad", "uncertainty_pct",
                    "gate_threshold_pct", "gate_pass", "status"]:
            assert key in gate

    def test_status_string_on_fail(self):
        gate = rhobar_robustness_gate(0.15)
        assert "FAIL" in gate["status"]

    def test_status_string_on_pass(self):
        gate = rhobar_robustness_gate(0.005)
        assert "PASS" in gate["status"]


class TestDeltaCP9DUncertainty:
    def test_uncertainty_positive(self):
        assert delta_cp_9d_uncertainty() > 0

    def test_uncertainty_below_gate_threshold(self):
        uncertainty_pct = delta_cp_9d_uncertainty() / DELTA_CP_PDG * 100.0
        assert uncertainty_pct < RHOBAR_GATE_THRESHOLD_PCT


class TestCPPhase9DGateCheck:
    def test_gate_passed(self):
        gate = cp_phase_9d_gate_check()
        assert gate["gate_pass"] is True

    def test_improvement_positive(self):
        gate = cp_phase_9d_gate_check()
        assert gate["improvement_pct"] > 0

    def test_residual_9d_less_than_7d(self):
        gate = cp_phase_9d_gate_check()
        assert gate["residual_9d_pct"] < gate["residual_7d_pct"]

    def test_status_contains_best_evidence(self):
        gate = cp_phase_9d_gate_check()
        assert "BEST_EVIDENCE_CONSTRAINED" in gate["status"]

    def test_returns_required_keys(self):
        gate = cp_phase_9d_gate_check()
        for key in ["delta_cp_7d_rad", "delta_cp_9d_correction_rad", "delta_cp_9d_total_rad",
                    "delta_cp_pdg_rad", "residual_7d_pct", "residual_9d_pct",
                    "improvement_pct", "gate_pass", "rhobar_robustness_gate",
                    "uncertainty_9d_rad", "uncertainty_9d_pct"]:
            assert key in gate

    def test_pdg_value(self):
        gate = cp_phase_9d_gate_check()
        assert gate["delta_cp_pdg_rad"] == pytest.approx(DELTA_CP_PDG, rel=1e-9)


class TestCPPhase9DSummary:
    def test_returns_dict(self):
        s = cp_phase_9d_summary()
        assert isinstance(s, dict)

    def test_overall_status_best_evidence(self):
        s = cp_phase_9d_summary()
        assert "BEST_EVIDENCE_CONSTRAINED" in s["overall_status"]

    def test_residual_improved(self):
        s = cp_phase_9d_summary()
        assert s["residual_9d_pct"] < s["residual_7d_pct"]

    def test_required_keys(self):
        s = cp_phase_9d_summary()
        for key in ["alpha_9d", "kk_9d_scale_ratio", "gs_flux_contribution",
                    "gs_uncertainty_fraction",
                    "delta_cp_7d_rad", "delta_cp_9d_rad", "delta_cp_pdg_rad",
                    "residual_7d_pct", "residual_9d_pct", "gate", "note"]:
            assert key in s
