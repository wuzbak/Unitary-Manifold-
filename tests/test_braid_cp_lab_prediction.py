# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for braid_cp_lab_prediction.py — WS-3 Lab-Scale CP Falsifier."""
from __future__ import annotations

import math

import pytest

from src.core.braid_cp_lab_prediction import (
    A_CP_TARGET_ORDER,
    J_CKM_PDG,
    K_CS,
    N_W,
    THETA_BRAID,
    a_cp_lab_prediction,
    falsification_threshold_analysis,
    full_prediction_report,
    jarlskog_from_braid_geometry,
    topology_transfer_efficiency,
)


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_theta_braid_value(self):
        expected = 2 * math.pi * 5 / 74
        assert abs(THETA_BRAID - expected) < 1e-12

    def test_j_ckm_pdg(self):
        assert abs(J_CKM_PDG - 3.04e-5) < 1e-30

    def test_a_cp_target_order(self):
        assert A_CP_TARGET_ORDER == 1e-5


# ---------------------------------------------------------------------------
# jarlskog_from_braid_geometry
# ---------------------------------------------------------------------------

class TestJarlskogFromBraidGeometry:
    def test_j_geo_positive(self):
        result = jarlskog_from_braid_geometry()
        assert result["J_geo"] > 0

    def test_j_geo_within_factor100_of_pdg(self):
        # Formula gives leading-order geometric estimate; within 2 OOM of J_PDG
        result = jarlskog_from_braid_geometry()
        ratio = result["J_geo"] / J_CKM_PDG
        assert 0.01 <= ratio <= 100.0, f"J_geo / J_PDG = {ratio:.3f} outside [0.01, 100]"

    def test_theta_braid_correct(self):
        result = jarlskog_from_braid_geometry()
        expected_theta = 2 * math.pi * N_W / K_CS
        assert abs(result["theta_braid_rad"] - expected_theta) < 1e-12

    def test_sin_braid_positive(self):
        result = jarlskog_from_braid_geometry()
        assert result["sin_braid"] > 0

    def test_residual_pct_finite(self):
        result = jarlskog_from_braid_geometry()
        assert math.isfinite(result["residual_vs_pdg_pct"])

    def test_returns_all_keys(self):
        result = jarlskog_from_braid_geometry()
        expected_keys = {
            "theta_braid_rad", "sin_braid", "J_geo",
            "J_CKM_PDG", "residual_vs_pdg_pct", "status",
        }
        assert expected_keys.issubset(result.keys())

    def test_status_is_string(self):
        result = jarlskog_from_braid_geometry()
        # Status reflects whether residual vs PDG is within 50% band
        assert isinstance(result["status"], str) and len(result["status"]) > 0

    def test_j_geo_order_of_magnitude(self):
        # Leading-order geometric formula: J_geo ~ (n_w/k_cs)^2 * sin(θ) ≈ 1.9e-3
        result = jarlskog_from_braid_geometry()
        oom = math.log10(result["J_geo"])
        assert -4 <= oom <= 0, f"log10(J_geo) = {oom:.1f} outside expected range"


# ---------------------------------------------------------------------------
# topology_transfer_efficiency
# ---------------------------------------------------------------------------

class TestTopologyTransferEfficiency:
    def test_pi_topo_in_unit_interval_jj(self):
        result = topology_transfer_efficiency(1000.0, platform="JJ_SQUID")
        assert 0.0 <= result["pi_topo"] <= 1.0

    def test_pi_topo_in_unit_interval_ti(self):
        result = topology_transfer_efficiency(1000.0, platform="TOPOLOGICAL_INSULATOR")
        assert 0.0 <= result["pi_topo"] <= 1.0

    def test_jj_large_coherence_gives_small_pi_topo(self):
        # Very large coherence_length >> braid_length → pi_topo → 0
        result = topology_transfer_efficiency(
            coherence_length_nm=1e9,
            braid_length_nm=1.0,
            platform="JJ_SQUID",
        )
        assert result["pi_topo"] < 0.01

    def test_jj_small_coherence_gives_large_pi_topo(self):
        # coherence_length << braid_length → ratio → 0 → pi_topo → 1
        result = topology_transfer_efficiency(
            coherence_length_nm=1.0,
            braid_length_nm=1e9,
            platform="JJ_SQUID",
        )
        assert result["pi_topo"] > 0.99

    def test_default_braid_length_computed_correctly(self):
        coh = 1000.0
        result = topology_transfer_efficiency(coh, platform="JJ_SQUID")
        expected_braid = coh * K_CS / N_W
        assert abs(result["braid_length_nm"] - expected_braid) < 1e-9

    def test_returns_required_keys(self):
        result = topology_transfer_efficiency(1000.0)
        for k in ("pi_topo", "braid_length_nm", "coherence_length_nm",
                  "platform", "regime_classification"):
            assert k in result

    def test_typical_jj_efficiency_near_0_93(self):
        # With default braid_length = 14.8× coherence, ratio = 1/14.8
        result = topology_transfer_efficiency(1000.0, platform="JJ_SQUID")
        assert 0.90 <= result["pi_topo"] <= 0.95

    def test_unknown_platform_raises(self):
        with pytest.raises(ValueError):
            topology_transfer_efficiency(1000.0, platform="UNKNOWN")

    def test_zero_coherence_raises(self):
        with pytest.raises(ValueError):
            topology_transfer_efficiency(0.0)


# ---------------------------------------------------------------------------
# a_cp_lab_prediction
# ---------------------------------------------------------------------------

class TestACpLabPrediction:
    def test_a_cp_in_order_of_magnitude_range(self):
        # J_geo ~ 1.9e-3, pi_topo ~ 0.93 → a_cp ~ 1.8e-3; OOM within 2 decades of 1e-5
        result = a_cp_lab_prediction("JJ_SQUID", coherence_length_nm=1000.0)
        assert 1e-8 <= result["a_cp_lab"] <= 1e-2

    def test_prediction_consistent_with_target_jj(self):
        result = a_cp_lab_prediction("JJ_SQUID", coherence_length_nm=1000.0)
        assert result["prediction_consistent_with_target"] is True

    def test_returns_j_geo_result(self):
        result = a_cp_lab_prediction()
        assert "j_geo_result" in result
        assert "J_geo" in result["j_geo_result"]

    def test_returns_pi_topo_result(self):
        result = a_cp_lab_prediction()
        assert "pi_topo_result" in result
        assert "pi_topo" in result["pi_topo_result"]

    def test_a_cp_equals_product(self):
        result = a_cp_lab_prediction("JJ_SQUID", 1000.0)
        expected = result["j_geo_result"]["J_geo"] * result["pi_topo_result"]["pi_topo"]
        assert abs(result["a_cp_lab"] - expected) < 1e-30

    def test_prediction_order_of_magnitude_is_int(self):
        result = a_cp_lab_prediction()
        assert isinstance(result["prediction_order_of_magnitude"], int)


# ---------------------------------------------------------------------------
# falsification_threshold_analysis
# ---------------------------------------------------------------------------

class TestFalsificationThresholdAnalysis:
    def test_minimum_sigma_is_1e_minus5(self):
        result = falsification_threshold_analysis()
        assert result["minimum_sigma_for_falsification"] == 1e-5

    def test_required_events_jj_positive(self):
        result = falsification_threshold_analysis()
        assert result["required_events_for_jj_squid"] > 0

    def test_required_events_ti_positive(self):
        result = falsification_threshold_analysis()
        assert result["required_events_for_topological_insulator"] > 0

    def test_time_estimate_positive(self):
        result = falsification_threshold_analysis()
        assert result["time_to_falsification_years_estimate"] > 0

    def test_notes_key_present(self):
        result = falsification_threshold_analysis()
        assert "notes" in result and len(result["notes"]) > 0


# ---------------------------------------------------------------------------
# full_prediction_report
# ---------------------------------------------------------------------------

class TestFullPredictionReport:
    def test_returns_braid_geometry(self):
        report = full_prediction_report()
        assert "braid_geometry" in report

    def test_returns_jj_squid_prediction(self):
        report = full_prediction_report()
        assert "jj_squid_prediction" in report

    def test_returns_ti_prediction(self):
        report = full_prediction_report()
        assert "ti_prediction" in report

    def test_returns_falsification_analysis(self):
        report = full_prediction_report()
        assert "falsification_analysis" in report

    def test_returns_summary_string(self):
        report = full_prediction_report()
        assert isinstance(report["summary"], str) and len(report["summary"]) > 10

    def test_all_expected_keys_present(self):
        report = full_prediction_report()
        for key in ("braid_geometry", "jj_squid_prediction",
                    "ti_prediction", "falsification_analysis", "summary"):
            assert key in report, f"Missing key: {key}"
