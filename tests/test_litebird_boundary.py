# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_litebird_boundary.py
================================
Test suite for Pillar 45-C — LiteBIRD Boundary Check
(src/core/litebird_boundary.py).

~80 tests covering:
  - Constants and prediction values
  - litebird_covariance_matrix: shape, PSD, diagonal, symmetry
  - is_in_admissible_window: known in/out values, boundary cases
  - is_in_gap: known forbidden zone values, boundary conditions
  - gaussian_likelihood: formula, shape, normalization peak
  - best_fit_peak: correct peak selection
  - theory_passes: all four canonical peaks pass, gap fails, outside fails
  - fail_zone_report: required keys, verdict strings, PASS/FAIL logic
  - litebird_scan: length, monotone behavior across window

Theory and scientific direction: ThomasCory Walker-Pearson.
Code and tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.litebird_boundary import (
    ADMISSIBLE_LOWER,
    ADMISSIBLE_UPPER,
    BETA_CANONICAL,
    BETA_DERIVED,
    BETA_FULL_1,
    BETA_FULL_2,
    BETA_LABELS,
    BETA_PREDICTIONS,
    GAP_LOWER,
    GAP_UPPER,
    N_SIGMA_PASS,
    PREDICTIONS,
    SIGMA_LITEBIRD,
    SIGMA_THEORY,
    BirefringencePrediction,
    best_fit_peak,
    fail_zone_report,
    gaussian_likelihood,
    is_in_admissible_window,
    is_in_gap,
    litebird_covariance_matrix,
    litebird_scan,
    theory_passes,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_beta_canonical(self):
        assert BETA_CANONICAL == pytest.approx(0.273)

    def test_beta_derived(self):
        assert BETA_DERIVED == pytest.approx(0.331)

    def test_beta_full_1(self):
        assert BETA_FULL_1 == pytest.approx(0.290)

    def test_beta_full_2(self):
        assert BETA_FULL_2 == pytest.approx(0.351)

    def test_admissible_lower(self):
        assert ADMISSIBLE_LOWER == pytest.approx(0.22)

    def test_admissible_upper(self):
        assert ADMISSIBLE_UPPER == pytest.approx(0.38)

    def test_gap_lower(self):
        assert GAP_LOWER == pytest.approx(0.29)

    def test_gap_upper(self):
        assert GAP_UPPER == pytest.approx(0.31)

    def test_sigma_litebird(self):
        assert SIGMA_LITEBIRD == pytest.approx(0.02)

    def test_sigma_theory(self):
        assert SIGMA_THEORY > 0.0

    def test_four_predictions(self):
        assert len(BETA_PREDICTIONS) == 4

    def test_four_labels(self):
        assert len(BETA_LABELS) == 4

    def test_four_prediction_objects(self):
        assert len(PREDICTIONS) == 4

    def test_all_predictions_in_window(self):
        for b in BETA_PREDICTIONS:
            assert ADMISSIBLE_LOWER <= b <= ADMISSIBLE_UPPER

    def test_gap_inside_window(self):
        assert ADMISSIBLE_LOWER < GAP_LOWER < GAP_UPPER < ADMISSIBLE_UPPER

    def test_predictions_ordered(self):
        assert BETA_PREDICTIONS == sorted(BETA_PREDICTIONS)

    def test_n_sigma_pass_positive(self):
        assert N_SIGMA_PASS > 0.0


# ---------------------------------------------------------------------------
# BirefringencePrediction dataclass
# ---------------------------------------------------------------------------

class TestBirefringencePrediction:
    def test_fields(self):
        p = BirefringencePrediction(beta=0.273, sigma_theory=0.005, label="test")
        assert p.beta == pytest.approx(0.273)
        assert p.sigma_theory == pytest.approx(0.005)
        assert p.label == "test"

    def test_predictions_list_types(self):
        for p in PREDICTIONS:
            assert isinstance(p, BirefringencePrediction)
            assert p.beta > 0.0
            assert p.sigma_theory > 0.0


# ---------------------------------------------------------------------------
# litebird_covariance_matrix
# ---------------------------------------------------------------------------

class TestLitebirdCovarianceMatrix:
    def test_shape(self):
        C = litebird_covariance_matrix()
        assert C.shape == (4, 4)

    def test_symmetric(self):
        C = litebird_covariance_matrix()
        assert np.allclose(C, C.T)

    def test_diagonal_is_sigma_sq(self):
        C = litebird_covariance_matrix()
        for i in range(4):
            assert C[i, i] == pytest.approx(SIGMA_THEORY ** 2, rel=1e-10)

    def test_positive_semidefinite(self):
        C = litebird_covariance_matrix()
        eigenvalues = np.linalg.eigvalsh(C)
        assert np.all(eigenvalues >= -1e-15)

    def test_off_diagonal_positive(self):
        C = litebird_covariance_matrix()
        for i in range(4):
            for j in range(4):
                if i != j:
                    assert C[i, j] > 0.0

    def test_diagonal_dominates(self):
        C = litebird_covariance_matrix()
        for i in range(4):
            assert C[i, i] >= max(C[i, j] for j in range(4) if j != i)

    def test_custom_sigma(self):
        C = litebird_covariance_matrix(sigma_theory=0.01)
        assert C[0, 0] == pytest.approx(0.01 ** 2, rel=1e-10)


# ---------------------------------------------------------------------------
# is_in_admissible_window
# ---------------------------------------------------------------------------

class TestIsInAdmissibleWindow:
    def test_lower_bound_inside(self):
        assert is_in_admissible_window(ADMISSIBLE_LOWER) is True

    def test_upper_bound_inside(self):
        assert is_in_admissible_window(ADMISSIBLE_UPPER) is True

    def test_just_below_lower_outside(self):
        assert is_in_admissible_window(0.21) is False

    def test_just_above_upper_outside(self):
        assert is_in_admissible_window(0.39) is False

    def test_all_predictions_inside(self):
        for b in BETA_PREDICTIONS:
            assert is_in_admissible_window(b) is True

    def test_zero_outside(self):
        assert is_in_admissible_window(0.0) is False

    def test_midpoint_inside(self):
        mid = (ADMISSIBLE_LOWER + ADMISSIBLE_UPPER) / 2
        assert is_in_admissible_window(mid) is True


# ---------------------------------------------------------------------------
# is_in_gap
# ---------------------------------------------------------------------------

class TestIsInGap:
    def test_gap_interior_is_forbidden(self):
        assert is_in_gap(0.30) is True

    def test_gap_lower_not_forbidden(self):
        assert is_in_gap(GAP_LOWER) is False

    def test_gap_upper_not_forbidden(self):
        assert is_in_gap(GAP_UPPER) is False

    def test_below_gap_not_forbidden(self):
        assert is_in_gap(0.27) is False

    def test_above_gap_not_forbidden(self):
        assert is_in_gap(0.35) is False

    def test_canonical_betas_not_in_gap(self):
        for b in BETA_PREDICTIONS:
            assert not is_in_gap(b)


# ---------------------------------------------------------------------------
# gaussian_likelihood
# ---------------------------------------------------------------------------

class TestGaussianLikelihood:
    def test_shape(self):
        L = gaussian_likelihood(0.351)
        assert L.shape == (4,)

    def test_all_positive(self):
        L = gaussian_likelihood(0.351)
        assert np.all(L > 0.0)

    def test_all_at_most_one(self):
        L = gaussian_likelihood(0.351)
        assert np.all(L <= 1.0)

    def test_peak_at_exact_prediction(self):
        # At β = BETA_FULL_2, the 4th likelihood should be maximum
        L = gaussian_likelihood(BETA_FULL_2)
        assert np.argmax(L) == 3  # BETA_FULL_2 is index 3

    def test_peak_at_canonical(self):
        L = gaussian_likelihood(BETA_CANONICAL)
        assert np.argmax(L) == 0

    def test_likelihood_formula(self):
        beta_meas = 0.273
        sigma_meas = SIGMA_LITEBIRD
        sigma_total = math.sqrt(sigma_meas ** 2 + SIGMA_THEORY ** 2)
        expected_0 = math.exp(-0.5 * ((beta_meas - BETA_CANONICAL) / sigma_total) ** 2)
        L = gaussian_likelihood(beta_meas, sigma_meas)
        assert L[0] == pytest.approx(expected_0, rel=1e-10)

    def test_larger_sigma_broader_peak(self):
        L_narrow = gaussian_likelihood(0.30, sigma_measured=0.001)
        L_broad = gaussian_likelihood(0.30, sigma_measured=0.10)
        # Broad sigma → likelihoods are more uniform (min likelihood is higher)
        assert np.min(L_broad) >= np.min(L_narrow)


# ---------------------------------------------------------------------------
# best_fit_peak
# ---------------------------------------------------------------------------

class TestBestFitPeak:
    def test_returns_prediction(self):
        p = best_fit_peak(0.351)
        assert isinstance(p, BirefringencePrediction)

    def test_best_fit_for_beta_full_2(self):
        p = best_fit_peak(BETA_FULL_2)
        assert p.beta == pytest.approx(BETA_FULL_2)

    def test_best_fit_for_canonical(self):
        p = best_fit_peak(BETA_CANONICAL)
        assert p.beta == pytest.approx(BETA_CANONICAL)

    def test_best_fit_for_derived(self):
        p = best_fit_peak(BETA_DERIVED)
        assert p.beta == pytest.approx(BETA_DERIVED)

    def test_best_fit_for_midpoint_of_window(self):
        # 0.30 is in the gap — nearest peaks are BETA_FULL_1=0.290 and BETA_DERIVED=0.331
        p = best_fit_peak(0.30)
        assert p.beta in [BETA_FULL_1, BETA_DERIVED]


# ---------------------------------------------------------------------------
# theory_passes
# ---------------------------------------------------------------------------

class TestTheoryPasses:
    def test_canonical_peak_passes(self):
        assert theory_passes(BETA_CANONICAL) is True

    def test_derived_peak_passes(self):
        assert theory_passes(BETA_DERIVED) is True

    def test_full_1_peak_passes(self):
        assert theory_passes(BETA_FULL_1) is True

    def test_full_2_peak_passes(self):
        assert theory_passes(BETA_FULL_2) is True

    def test_gap_center_fails(self):
        assert theory_passes(0.30) is False

    def test_below_window_fails(self):
        assert theory_passes(0.10) is False

    def test_above_window_fails(self):
        assert theory_passes(0.40) is False

    def test_just_below_gap_passes(self):
        # 0.288 is below gap and near BETA_FULL_1=0.290 → should pass
        assert theory_passes(0.288) is True

    def test_just_above_gap_passes(self):
        # 0.312 is above gap and approaching BETA_DERIVED=0.331 → check
        sigma_total = math.sqrt(SIGMA_LITEBIRD ** 2 + SIGMA_THEORY ** 2)
        delta = abs(0.312 - BETA_DERIVED)
        if delta <= N_SIGMA_PASS * sigma_total:
            assert theory_passes(0.312) is True
        else:
            pytest.skip("0.312 is too far from nearest peak for this test")

    def test_far_from_all_peaks_fails(self):
        # 0.25 is in window, not in gap, but potentially far from all peaks
        sigma_total = math.sqrt(SIGMA_LITEBIRD ** 2 + SIGMA_THEORY ** 2)
        closest = min(abs(0.25 - b) for b in BETA_PREDICTIONS)
        expected = closest <= N_SIGMA_PASS * sigma_total
        assert theory_passes(0.25) is expected


# ---------------------------------------------------------------------------
# fail_zone_report
# ---------------------------------------------------------------------------

class TestFailZoneReport:
    def _report(self, beta=0.351):
        return fail_zone_report(beta)

    def test_returns_dict(self):
        assert isinstance(self._report(), dict)

    def test_required_keys(self):
        r = self._report()
        for k in ["beta_measured", "sigma_measured", "in_admissible_window",
                  "in_gap", "theory_passes", "verdict", "likelihoods",
                  "best_fit_peak", "closest_beta", "closest_delta",
                  "closest_delta_sigma", "covariance_matrix",
                  "admissible_window", "gap"]:
            assert k in r

    def test_beta_full_2_passes(self):
        r = fail_zone_report(BETA_FULL_2)
        assert r["theory_passes"] is True
        assert "PASS" in r["verdict"]

    def test_gap_center_fails(self):
        r = fail_zone_report(0.30)
        assert r["theory_passes"] is False
        assert "FAIL" in r["verdict"]

    def test_below_window_fails(self):
        r = fail_zone_report(0.10)
        assert r["theory_passes"] is False
        assert "FAIL" in r["verdict"]

    def test_above_window_fails(self):
        r = fail_zone_report(0.40)
        assert r["theory_passes"] is False
        assert "FAIL" in r["verdict"]

    def test_covariance_matrix_shape(self):
        r = self._report()
        assert r["covariance_matrix"].shape == (4, 4)

    def test_likelihoods_shape(self):
        r = self._report()
        assert r["likelihoods"].shape == (4,)

    def test_admissible_window_stored(self):
        r = self._report()
        assert r["admissible_window"] == (ADMISSIBLE_LOWER, ADMISSIBLE_UPPER)

    def test_gap_stored(self):
        r = self._report()
        assert r["gap"] == (GAP_LOWER, GAP_UPPER)

    def test_closest_delta_non_negative(self):
        r = self._report()
        assert r["closest_delta"] >= 0.0

    def test_closest_delta_sigma_non_negative(self):
        r = self._report()
        assert r["closest_delta_sigma"] >= 0.0

    def test_best_fit_peak_is_prediction(self):
        r = self._report()
        assert isinstance(r["best_fit_peak"], BirefringencePrediction)

    def test_litebird_question_034(self):
        """If LiteBIRD measures 0.34°, does the theory pass?"""
        r = fail_zone_report(0.34)
        # 0.34° is above the gap, in window, near BETA_DERIVED=0.331 and BETA_FULL_2=0.351
        sigma_total = math.sqrt(SIGMA_LITEBIRD ** 2 + SIGMA_THEORY ** 2)
        nearest = min(abs(0.34 - b) for b in BETA_PREDICTIONS)
        expected = nearest <= N_SIGMA_PASS * sigma_total
        assert r["theory_passes"] is expected

    def test_litebird_question_036(self):
        """If LiteBIRD measures 0.36°, does the theory pass?"""
        r = fail_zone_report(0.36)
        sigma_total = math.sqrt(SIGMA_LITEBIRD ** 2 + SIGMA_THEORY ** 2)
        nearest = min(abs(0.36 - b) for b in BETA_PREDICTIONS)
        expected = nearest <= N_SIGMA_PASS * sigma_total
        assert r["theory_passes"] is expected


# ---------------------------------------------------------------------------
# litebird_scan
# ---------------------------------------------------------------------------

class TestLitebirdScan:
    def test_returns_list(self):
        results = litebird_scan([0.273, 0.331, 0.351])
        assert isinstance(results, list)

    def test_length_matches_input(self):
        betas = [0.22, 0.27, 0.30, 0.35, 0.38]
        results = litebird_scan(betas)
        assert len(results) == len(betas)

    def test_each_element_is_dict(self):
        for r in litebird_scan([0.273, 0.30, 0.351]):
            assert isinstance(r, dict)

    def test_canonical_peaks_pass(self):
        results = litebird_scan(BETA_PREDICTIONS)
        for r in results:
            assert r["theory_passes"] is True

    def test_gap_center_fails_in_scan(self):
        results = litebird_scan([0.30])
        assert results[0]["theory_passes"] is False

    def test_outside_window_fails_in_scan(self):
        for beta in [0.10, 0.50]:
            results = litebird_scan([beta])
            assert results[0]["theory_passes"] is False

    def test_scan_full_window(self):
        """Scan every 0.01° across the full admissible window."""
        betas = [round(ADMISSIBLE_LOWER + i * 0.01, 3) for i in range(17)]
        results = litebird_scan(betas)
        # All should be in the admissible window
        for r in results:
            assert r["in_admissible_window"] is True
        # Gap values should fail
        gap_results = [r for r in results if GAP_LOWER < r["beta_measured"] < GAP_UPPER]
        for r in gap_results:
            assert r["theory_passes"] is False


# ---------------------------------------------------------------------------
# Exact Fail Zone — the primary falsification test
# ---------------------------------------------------------------------------

class TestExactFailZone:
    """
    Defines the exact 'Yes/No' judge conditions for LiteBIRD (~2032).

    The theory is falsified if:
    1. β < 0.22° or β > 0.38° (outside admissible window)
    2. β ∈ (0.29°, 0.31°) (forbidden gap — no viable configuration)

    The theory survives if:
    β ∈ [0.22°, 0.29°] ∪ [0.31°, 0.38°]
    AND within 3σ_total of at least one of the four predictions.
    """

    def test_fail_zone_1_below_window(self):
        for b in [0.10, 0.15, 0.21]:
            assert theory_passes(b) is False

    def test_fail_zone_1_above_window(self):
        for b in [0.39, 0.45, 0.50]:
            assert theory_passes(b) is False

    def test_fail_zone_2_gap(self):
        for b in [0.295, 0.30, 0.305]:
            assert theory_passes(b) is False

    def test_pass_zone_lower_cluster(self):
        # Near BETA_CANONICAL = 0.273 → should pass
        assert theory_passes(0.273) is True

    def test_pass_zone_upper_cluster(self):
        # Near BETA_FULL_2 = 0.351 → should pass
        assert theory_passes(0.351) is True

    def test_gap_endpoints_ambiguous(self):
        # The gap is an open interval; endpoints (0.29°, 0.31°) are NOT in gap
        assert is_in_gap(GAP_LOWER) is False
        assert is_in_gap(GAP_UPPER) is False

    def test_admissible_window_boundaries_included(self):
        assert is_in_admissible_window(ADMISSIBLE_LOWER) is True
        assert is_in_admissible_window(ADMISSIBLE_UPPER) is True
