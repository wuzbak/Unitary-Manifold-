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
    ANCHOR_ALPHA_RANGE,
    ANCHOR_GS_RANGE,
    KK_9D_SCALE_RATIO,
    RESIDUAL_7D_PCT,
    RHOBAR_GATE_THRESHOLD_PCT,
    anchor_independence_scan,
    cp_phase_anchor_robustness_report,
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

    def test_anchor_alpha_range(self):
        assert ANCHOR_ALPHA_RANGE[0] < ALPHA_9D < ANCHOR_ALPHA_RANGE[1]

    def test_anchor_gs_range(self):
        assert ANCHOR_GS_RANGE[0] < GS_FLUX_CONTRIBUTION < ANCHOR_GS_RANGE[1]

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

    def test_parameter_perturbation_stays_below_3pct(self):
        for alpha_scale in (0.9, 1.0, 1.1):
            for kk_scale in (0.9, 1.0, 1.1):
                for gs_scale in (0.9, 1.0, 1.1):
                    resid = residual_pct_9d(
                        alpha_9d=ALPHA_9D * alpha_scale,
                        kk_ratio=KK_9D_SCALE_RATIO * kk_scale,
                        gs_flux=GS_FLUX_CONTRIBUTION * gs_scale,
                    )
                    assert resid < 3.0, (
                        "Residual exceeded 3% for scales "
                        f"(alpha={alpha_scale}, kk={kk_scale}, gs={gs_scale})"
                    )


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


class TestAnchorIndependenceScan:
    def test_scan_returns_dict(self):
        scan = anchor_independence_scan()
        assert isinstance(scan, dict)

    def test_scan_grid_size(self):
        scan = anchor_independence_scan(points=5)
        assert scan["grid_points"] == 25

    def test_scan_residual_band_below_gate(self):
        scan = anchor_independence_scan()
        assert scan["residual_max_pct"] < RHOBAR_GATE_THRESHOLD_PCT

    def test_scan_uncertainty_band_below_gate(self):
        scan = anchor_independence_scan()
        assert scan["uncertainty_max_pct"] < RHOBAR_GATE_THRESHOLD_PCT

    def test_scan_all_points_pass(self):
        scan = anchor_independence_scan()
        assert scan["all_points_gate_pass"] is True

    def test_scan_bad_points_raises(self):
        with pytest.raises(ValueError):
            anchor_independence_scan(points=1)


class TestAnchorRobustnessReport:
    def test_report_returns_dict(self):
        report = cp_phase_anchor_robustness_report()
        assert isinstance(report, dict)

    def test_report_status_pass(self):
        report = cp_phase_anchor_robustness_report()
        assert "PASS" in report["status"]

    def test_report_scan_present(self):
        report = cp_phase_anchor_robustness_report()
        assert "scan" in report
        assert report["scan"]["all_points_gate_pass"] is True


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
                    "residual_7d_pct", "residual_9d_pct", "gate", "anchor_robustness", "note"]:
            assert key in s
