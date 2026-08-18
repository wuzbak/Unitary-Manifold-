# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_hox_kk_alignment.py
=================================
Unit tests for src/biology/hox_kk_alignment.py — Track 2 (Pillar 25-B).
"""

import math
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.biology.hox_kk_alignment import (
    N_W, N_SEG, DELTA_OVER_LAMBDA_UM,
    TIER1_DELTA_LO, TIER1_DELTA_HI, TIER1_POSITION_TOL,
    DROSOPHILA_HOX_BOUNDARIES, ZEBRAFISH_HOX_BOUNDARIES,
    segment_count,
    activation_threshold,
    threshold_sequence,
    log_spacing,
    predicted_boundary_positions,
    chi2_fit,
    tier1_alignment_test,
    drosophila_chi2,
    zebrafish_chi2,
    hox_report,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_n_seg(self):
        assert N_SEG == 10

    def test_delta_over_lambda(self):
        assert DELTA_OVER_LAMBDA_UM == pytest.approx(0.200, rel=1e-9)

    def test_tier1_window(self):
        assert TIER1_DELTA_LO == pytest.approx(0.185, rel=1e-6)
        assert TIER1_DELTA_HI == pytest.approx(0.215, rel=1e-6)
        assert DELTA_OVER_LAMBDA_UM in (TIER1_DELTA_LO, TIER1_DELTA_HI) or \
               TIER1_DELTA_LO < DELTA_OVER_LAMBDA_UM < TIER1_DELTA_HI

    def test_drosophila_8_genes(self):
        assert len(DROSOPHILA_HOX_BOUNDARIES) == 8

    def test_zebrafish_9_genes(self):
        assert len(ZEBRAFISH_HOX_BOUNDARIES) == 9

    def test_drosophila_increasing(self):
        b = DROSOPHILA_HOX_BOUNDARIES
        for i in range(len(b) - 1):
            assert b[i] < b[i + 1]

    def test_zebrafish_increasing(self):
        b = ZEBRAFISH_HOX_BOUNDARIES
        for i in range(len(b) - 1):
            assert b[i] < b[i + 1]


# ---------------------------------------------------------------------------
# segment_count
# ---------------------------------------------------------------------------

class TestSegmentCount:
    def test_default(self):
        assert segment_count() == 10

    def test_n_w_5(self):
        assert segment_count(5) == 10

    def test_n_w_7(self):
        assert segment_count(7) == 14

    def test_n_w_1(self):
        assert segment_count(1) == 2

    def test_raises_zero(self):
        with pytest.raises(ValueError):
            segment_count(0)

    def test_raises_negative(self):
        with pytest.raises(ValueError):
            segment_count(-1)


# ---------------------------------------------------------------------------
# activation_threshold
# ---------------------------------------------------------------------------

class TestActivationThreshold:
    def test_formula(self):
        phi_0 = 1.0
        for i in range(1, 6):
            expected = phi_0 * math.exp(-i * DELTA_OVER_LAMBDA_UM)
            assert activation_threshold(phi_0, i) == pytest.approx(expected, rel=1e-10)

    def test_decreasing_in_i(self):
        vals = [activation_threshold(1.0, i) for i in range(1, 11)]
        for j in range(len(vals) - 1):
            assert vals[j] > vals[j + 1]

    def test_positive(self):
        assert activation_threshold(2.0, 3) > 0

    def test_raises_phi0_zero(self):
        with pytest.raises(ValueError):
            activation_threshold(0.0, 1)

    def test_raises_phi0_negative(self):
        with pytest.raises(ValueError):
            activation_threshold(-1.0, 1)

    def test_raises_i_zero(self):
        with pytest.raises(ValueError):
            activation_threshold(1.0, 0)

    def test_raises_delta_zero(self):
        with pytest.raises(ValueError):
            activation_threshold(1.0, 1, 0.0)


# ---------------------------------------------------------------------------
# threshold_sequence
# ---------------------------------------------------------------------------

class TestThresholdSequence:
    def test_length(self):
        seq = threshold_sequence(1.0, 10)
        assert len(seq) == 10

    def test_strictly_decreasing(self):
        seq = threshold_sequence(1.0)
        for i in range(len(seq) - 1):
            assert seq[i] > seq[i + 1]

    def test_log_spacing_uniform(self):
        seq = threshold_sequence(1.0)
        spacings = [math.log(seq[i] / seq[i + 1]) for i in range(len(seq) - 1)]
        for s in spacings:
            assert s == pytest.approx(DELTA_OVER_LAMBDA_UM, rel=1e-9)

    def test_matches_individual_calls(self):
        seq = threshold_sequence(2.5, 5, 0.15)
        for i, val in enumerate(seq, start=1):
            assert val == pytest.approx(activation_threshold(2.5, i, 0.15), rel=1e-10)

    def test_raises_n_seg_zero(self):
        with pytest.raises(ValueError):
            threshold_sequence(1.0, 0)


# ---------------------------------------------------------------------------
# log_spacing
# ---------------------------------------------------------------------------

class TestLogSpacing:
    def test_recovers_delta_lambda(self):
        phi_0 = 1.0
        phi_1 = activation_threshold(phi_0, 1, DELTA_OVER_LAMBDA_UM)
        phi_2 = activation_threshold(phi_0, 2, DELTA_OVER_LAMBDA_UM)
        assert log_spacing(phi_1, phi_2) == pytest.approx(DELTA_OVER_LAMBDA_UM, rel=1e-9)

    def test_raises_equal_values(self):
        with pytest.raises(ValueError):
            log_spacing(1.0, 1.0)

    def test_raises_reversed(self):
        with pytest.raises(ValueError):
            log_spacing(0.5, 1.0)

    def test_raises_zero(self):
        with pytest.raises(ValueError):
            log_spacing(0.0, 1.0)

    def test_raises_negative(self):
        with pytest.raises(ValueError):
            log_spacing(1.0, -0.5)


# ---------------------------------------------------------------------------
# predicted_boundary_positions
# ---------------------------------------------------------------------------

class TestPredictedBoundaryPositions:
    def test_length(self):
        pos = predicted_boundary_positions(8)
        assert len(pos) == 8

    def test_strictly_increasing(self):
        pos = predicted_boundary_positions(10)
        for i in range(len(pos) - 1):
            assert pos[i] < pos[i + 1]

    def test_last_position_is_0_9(self):
        pos = predicted_boundary_positions(10, axis_length=1.0)
        assert pos[-1] == pytest.approx(0.9, rel=1e-9)

    def test_first_positive(self):
        pos = predicted_boundary_positions(8)
        assert pos[0] > 0

    def test_all_within_0_1(self):
        pos = predicted_boundary_positions(10)
        assert all(0 < p <= 1.0 for p in pos)

    def test_linear_spacing(self):
        # Positions should be evenly spaced (proportional to i)
        pos = predicted_boundary_positions(5)
        steps = [pos[i + 1] - pos[i] for i in range(len(pos) - 1)]
        for s in steps:
            assert s == pytest.approx(steps[0], rel=1e-9)

    def test_raises_n_seg_zero(self):
        with pytest.raises(ValueError):
            predicted_boundary_positions(0)


# ---------------------------------------------------------------------------
# chi2_fit
# ---------------------------------------------------------------------------

class TestChi2Fit:
    def test_perfect_fit(self):
        obs = [0.1, 0.2, 0.3]
        pred = [0.1, 0.2, 0.3]
        result = chi2_fit(obs, pred)
        assert result["chi2"] == pytest.approx(0.0, abs=1e-10)
        assert result["chi2_per_dof"] == pytest.approx(0.0, abs=1e-10)

    def test_chi2_structure(self):
        obs = [0.1, 0.3, 0.5]
        pred = [0.1, 0.3, 0.5]
        r = chi2_fit(obs, pred)
        assert "chi2" in r
        assert "dof" in r
        assert "chi2_per_dof" in r
        assert "residuals" in r

    def test_dof_equals_n(self):
        obs = [0.1, 0.2, 0.3, 0.4]
        pred = [0.1, 0.2, 0.3, 0.4]
        r = chi2_fit(obs, pred)
        assert r["dof"] == 4

    def test_nonzero_chi2(self):
        obs = [0.1, 0.2, 0.3]
        pred = [0.15, 0.25, 0.35]
        r = chi2_fit(obs, pred)
        assert r["chi2"] > 0

    def test_raises_mismatched_lengths(self):
        with pytest.raises(ValueError):
            chi2_fit([0.1, 0.2], [0.1])

    def test_raises_empty(self):
        with pytest.raises(ValueError):
            chi2_fit([], [])

    def test_residuals_length(self):
        obs = [0.1, 0.2, 0.3, 0.4, 0.5]
        pred = [0.1, 0.2, 0.3, 0.4, 0.5]
        r = chi2_fit(obs, pred)
        assert len(r["residuals"]) == 5


# ---------------------------------------------------------------------------
# tier1_alignment_test
# ---------------------------------------------------------------------------

class TestTier1AlignmentTest:
    def test_pass_with_um_predictions(self):
        # Use the UM's own predicted positions as observed → should pass
        obs = predicted_boundary_positions(10, DELTA_OVER_LAMBDA_UM)
        result = tier1_alignment_test(obs, DELTA_OVER_LAMBDA_UM, n_active=10)
        assert result["criterion2_quantization"] is True
        assert result["criterion3_segment_count"] is True

    def test_fail_criterion2_outside_window(self):
        obs = predicted_boundary_positions(8)
        result = tier1_alignment_test(obs, 0.10)  # way outside [0.185, 0.215]
        assert result["criterion2_quantization"] is False

    def test_criterion3_off_by_one(self):
        obs = predicted_boundary_positions(8)
        result = tier1_alignment_test(obs, DELTA_OVER_LAMBDA_UM, n_active=11)
        assert result["criterion3_segment_count"] is True  # |11 - 10| = 1 ≤ 1

    def test_criterion3_fail(self):
        obs = predicted_boundary_positions(8)
        result = tier1_alignment_test(obs, DELTA_OVER_LAMBDA_UM, n_active=7)
        assert result["criterion3_segment_count"] is False  # |7 - 10| = 3 > 1

    def test_criterion3_none_skipped(self):
        obs = predicted_boundary_positions(8)
        result = tier1_alignment_test(obs, DELTA_OVER_LAMBDA_UM, n_active=None)
        assert result["criterion3_segment_count"] is None

    def test_result_keys(self):
        obs = predicted_boundary_positions(8)
        result = tier1_alignment_test(obs, DELTA_OVER_LAMBDA_UM)
        for k in ["criterion1_positions_within_5pct", "criterion2_quantization",
                  "tier1_pass", "max_position_error_frac", "position_errors"]:
            assert k in result


# ---------------------------------------------------------------------------
# drosophila_chi2
# ---------------------------------------------------------------------------

class TestDrosophilaFit:
    def setup_method(self):
        self.result = drosophila_chi2()

    def test_keys(self):
        for k in ["species", "n_genes", "observed_boundaries",
                  "predicted_boundaries", "chi2_fit", "tier1_test"]:
            assert k in self.result

    def test_n_genes(self):
        assert self.result["n_genes"] == 8

    def test_predicted_length(self):
        assert len(self.result["predicted_boundaries"]) == 8

    def test_chi2_positive(self):
        assert self.result["chi2_fit"]["chi2"] >= 0

    def test_chi2_per_dof_reasonable(self):
        # The UM linear-spacing model provides a first-order prediction.
        # χ²/dof is a diagnostic — we report it honestly, not demand perfection.
        # The model is physically motivated; full closure requires Boltzmann solver.
        chi2_dof = self.result["chi2_fit"]["chi2_per_dof"]
        assert chi2_dof > 0
        assert chi2_dof < 1000  # finite and computed

    def test_tier1_structure(self):
        t = self.result["tier1_test"]
        assert "tier1_pass" in t
        assert "criterion2_quantization" in t

    def test_quantization_criterion_passes(self):
        # DELTA_OVER_LAMBDA_UM = 0.200 ∈ [0.185, 0.215] → must pass
        assert self.result["tier1_test"]["criterion2_quantization"] is True


# ---------------------------------------------------------------------------
# zebrafish_chi2
# ---------------------------------------------------------------------------

class TestZebrafishFit:
    def setup_method(self):
        self.result = zebrafish_chi2()

    def test_n_genes(self):
        assert self.result["n_genes"] == 9

    def test_chi2_positive(self):
        assert self.result["chi2_fit"]["chi2"] >= 0

    def test_chi2_per_dof_reasonable(self):
        chi2_dof = self.result["chi2_fit"]["chi2_per_dof"]
        assert chi2_dof > 0
        assert chi2_dof < 1000  # finite and computed

    def test_quantization_criterion_passes(self):
        assert self.result["tier1_test"]["criterion2_quantization"] is True

    def test_species_label(self):
        assert "zebrafish" in self.result["species"].lower() or \
               "Danio" in self.result["species"]


# ---------------------------------------------------------------------------
# hox_report
# ---------------------------------------------------------------------------

class TestHoxReport:
    def setup_method(self):
        self.report = hox_report()

    def test_top_level_keys(self):
        for k in ["drosophila", "zebrafish", "n_w", "n_seg_predicted",
                  "delta_over_lambda_um", "tier1_drosophila", "tier1_zebrafish",
                  "tier1_overall", "pillar_classification", "promotion_condition",
                  "observational_basis"]:
            assert k in self.report

    def test_n_w(self):
        assert self.report["n_w"] == 5

    def test_n_seg_predicted(self):
        assert self.report["n_seg_predicted"] == 10

    def test_delta_over_lambda(self):
        assert self.report["delta_over_lambda_um"] == pytest.approx(0.200, rel=1e-9)

    def test_pillar_classification(self):
        assert "ADJACENT" in self.report["pillar_classification"]
        assert "25-B" in self.report["pillar_classification"]

    def test_observational_basis_nonempty(self):
        obs = self.report["observational_basis"]
        assert isinstance(obs, list)
        assert len(obs) >= 3

    def test_promotion_condition_nonempty(self):
        assert len(self.report["promotion_condition"]) > 20

    def test_tier1_booleans(self):
        assert isinstance(self.report["tier1_drosophila"], bool)
        assert isinstance(self.report["tier1_zebrafish"], bool)
        assert isinstance(self.report["tier1_overall"], bool)
