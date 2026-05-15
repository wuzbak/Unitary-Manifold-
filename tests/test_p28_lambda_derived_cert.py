# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/p28_lambda_derived_cert.py — P28 DERIVED promotion cert."""
from __future__ import annotations

import math

import pytest

from src.core.p28_lambda_derived_cert import (
    P28_LOG10_RESIDUAL_THRESHOLD,
    P28_STATUS_AFTER,
    P28_STATUS_BEFORE,
    P28_TOE_SCORE_DELTA,
    p28_derived_gate_report,
    p28_derived_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_status_before(self):
        assert P28_STATUS_BEFORE == "GEOMETRIC_PREDICTION"

    def test_status_after(self):
        assert P28_STATUS_AFTER == "DERIVED"

    def test_toe_score_delta(self):
        assert P28_TOE_SCORE_DELTA == pytest.approx(0.2, abs=1e-12)

    def test_log10_residual_threshold_positive(self):
        assert P28_LOG10_RESIDUAL_THRESHOLD > 0.0

    def test_log10_residual_threshold_value(self):
        # Must be big enough to capture factor-2 accuracy (~0.31 orders)
        assert P28_LOG10_RESIDUAL_THRESHOLD >= 0.31


# ---------------------------------------------------------------------------
# Gate report structure
# ---------------------------------------------------------------------------

class TestGateReportStructure:
    @pytest.fixture(scope="class")
    def report(self):
        return p28_derived_gate_report()

    def test_parameter_label(self, report):
        assert report["parameter"] == "P28"

    def test_quantity_label(self, report):
        assert "Cosmological constant" in report["quantity"]

    def test_formula_present(self, report):
        assert "Λ_pred" in report["formula"]
        assert "K_CS" in report["formula"]

    def test_inputs_keys_present(self, report):
        for key in ("K_CS", "n_w", "pi_kR", "N_flux", "c_uv_total"):
            assert key in report["inputs"]

    def test_inputs_geometric_values(self, report):
        assert report["inputs"]["K_CS"] == 74
        assert report["inputs"]["n_w"] == 5
        assert report["inputs"]["pi_kR"] == pytest.approx(37.0, abs=0.01)
        assert report["inputs"]["N_flux"] == 37

    def test_lambda_pred_positive(self, report):
        assert report["lambda_pred_mplanck4"] > 0.0

    def test_lambda_pred_log10_finite(self, report):
        assert math.isfinite(report["lambda_pred_log10"])

    def test_lambda_pred_log10_negative(self, report):
        # CC is astronomically small relative to M_Pl^4
        assert report["lambda_pred_log10"] < -100.0

    def test_effective_n_flux_ge_61(self, report):
        assert report["effective_n_flux"] >= 61

    def test_axiomzero_inputs_empty(self, report):
        assert report["axiomzero_pdg_inputs"] == []

    def test_derivation_description_present(self, report):
        assert len(report["derivation"]) > 10

    def test_accuracy_note_present(self, report):
        assert len(report["accuracy_note"]) > 10


# ---------------------------------------------------------------------------
# Gate pass/fail values
# ---------------------------------------------------------------------------

class TestGates:
    @pytest.fixture(scope="class")
    def report(self):
        return p28_derived_gate_report()

    def test_gate1_first_principles_pass(self, report):
        assert report["gates"]["gate1_first_principles_derivation_pass"] is True

    def test_gate2_10d_closure_pass(self, report):
        assert report["gates"]["gate2_10d_closure_all_pass"] is True

    def test_gate3_within_factor2(self, report):
        assert report["gates"]["gate3_prediction_within_factor2"] is True

    def test_gate4_axiomzero_pass(self, report):
        assert report["gates"]["gate4_axiomzero_no_pdg_seed_inputs"] is True

    def test_all_gates_pass(self, report):
        assert report["all_gates_pass"] is True


# ---------------------------------------------------------------------------
# Promotion outcome
# ---------------------------------------------------------------------------

class TestPromotionOutcome:
    @pytest.fixture(scope="class")
    def report(self):
        return p28_derived_gate_report()

    def test_status_before(self, report):
        assert report["status_before"] == P28_STATUS_BEFORE

    def test_status_after_derived(self, report):
        assert report["status_after"] == P28_STATUS_AFTER

    def test_toe_score_delta_positive(self, report):
        assert report["toe_score_delta"] == pytest.approx(P28_TOE_SCORE_DELTA, abs=1e-12)

    def test_pred_to_obs_ratio_near_unity(self, report):
        # Within factor of 2 across 122 orders
        ratio = report["pred_to_obs_ratio"]
        assert 0.5 <= ratio <= 2.0

    def test_abs_log10_residual_within_threshold(self, report):
        assert report["abs_log10_residual"] < P28_LOG10_RESIDUAL_THRESHOLD

    def test_abs_log10_residual_positive(self, report):
        assert report["abs_log10_residual"] >= 0.0


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

class TestDerivedSummary:
    @pytest.fixture(scope="class")
    def report(self):
        return p28_derived_gate_report()

    @pytest.fixture(scope="class")
    def summary(self):
        return p28_derived_summary()

    def test_summary_sprint_label(self, summary):
        assert summary["sprint"] == "P28_LAMBDA_DERIVED_CERT"

    def test_summary_parameter(self, summary):
        assert summary["parameter"] == "P28"

    def test_summary_all_gates_pass(self, summary):
        assert summary["all_gates_pass"] is True

    def test_summary_status_after_derived(self, summary):
        assert summary["status_after"] == "DERIVED"

    def test_summary_toe_delta_matches_const(self, summary):
        assert summary["toe_score_delta"] == pytest.approx(P28_TOE_SCORE_DELTA, abs=1e-12)

    def test_summary_lambda_pred_log10_matches_report(self, report, summary):
        assert summary["lambda_pred_log10"] == pytest.approx(
            report["lambda_pred_log10"], abs=1e-10
        )

    def test_summary_abs_log10_residual_matches_report(self, report, summary):
        assert summary["abs_log10_residual"] == pytest.approx(
            report["abs_log10_residual"], abs=1e-10
        )

    def test_summary_formula_present(self, summary):
        assert "Λ_pred" in summary["formula"]
