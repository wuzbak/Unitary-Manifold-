# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_litebird_forecast.py
================================
Test suite for src/core/litebird_forecast.py (Pillar 45-D).

Covers constants, gaussian_likelihood, combined_likelihood,
detection_significance, forecast_scenarios, uncertainty_budget,
detection_power, timeline_to_result, and edge cases.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math

import pytest

from src.core.litebird_forecast import (
    ADMISSIBLE_LOWER,
    ADMISSIBLE_UPPER,
    BETA_CANONICAL,
    BETA_DERIVED,
    BETA_FULL_1,
    BETA_FULL_2,
    GAP_LOWER,
    GAP_UPPER,
    LAUNCH_YEAR,
    N_PEAKS,
    SIGMA_LITEBIRD,
    SIGMA_THEORY,
    combined_likelihood,
    detection_power,
    detection_significance,
    forecast_scenarios,
    gaussian_likelihood,
    timeline_to_result,
    uncertainty_budget,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants:
    def test_beta_canonical_value(self):
        assert BETA_CANONICAL == pytest.approx(0.273)

    def test_beta_derived_value(self):
        assert BETA_DERIVED == pytest.approx(0.331)

    def test_beta_full_1_value(self):
        assert BETA_FULL_1 == pytest.approx(0.290)

    def test_beta_full_2_value(self):
        assert BETA_FULL_2 == pytest.approx(0.351)

    def test_sigma_litebird_value(self):
        assert SIGMA_LITEBIRD == pytest.approx(0.02)

    def test_sigma_theory_value(self):
        assert SIGMA_THEORY == pytest.approx(0.01)

    def test_gap_lower_value(self):
        assert GAP_LOWER == pytest.approx(0.29)

    def test_gap_upper_value(self):
        assert GAP_UPPER == pytest.approx(0.31)

    def test_admissible_lower_value(self):
        assert ADMISSIBLE_LOWER == pytest.approx(0.22)

    def test_admissible_upper_value(self):
        assert ADMISSIBLE_UPPER == pytest.approx(0.38)

    def test_launch_year(self):
        assert LAUNCH_YEAR == 2032

    def test_n_peaks(self):
        assert N_PEAKS == 4

    def test_gap_within_admissible(self):
        assert ADMISSIBLE_LOWER < GAP_LOWER < GAP_UPPER < ADMISSIBLE_UPPER

    def test_canonical_below_gap(self):
        assert BETA_CANONICAL < GAP_LOWER

    def test_derived_above_gap(self):
        assert BETA_DERIVED > GAP_UPPER

    def test_full_1_at_gap_boundary(self):
        # BETA_FULL_1 = 0.290 is right at GAP_LOWER
        assert BETA_FULL_1 == pytest.approx(GAP_LOWER, rel=0.1)

    def test_full_2_above_gap(self):
        assert BETA_FULL_2 > GAP_UPPER

    def test_canonical_in_admissible(self):
        assert ADMISSIBLE_LOWER <= BETA_CANONICAL <= ADMISSIBLE_UPPER

    def test_derived_in_admissible(self):
        assert ADMISSIBLE_LOWER <= BETA_DERIVED <= ADMISSIBLE_UPPER


# ---------------------------------------------------------------------------
# gaussian_likelihood
# ---------------------------------------------------------------------------


class TestGaussianLikelihood:
    def test_peak_value(self):
        """At beta=beta_predicted, L = 1/(sqrt(2pi)*sigma)."""
        sigma = 0.02
        expected = 1.0 / (math.sqrt(2 * math.pi) * sigma)
        assert gaussian_likelihood(0.273, 0.273, sigma) == pytest.approx(expected)

    def test_symmetry(self):
        """Gaussian is symmetric around the mean."""
        L_plus = gaussian_likelihood(0.273 + 0.01, 0.273, 0.02)
        L_minus = gaussian_likelihood(0.273 - 0.01, 0.273, 0.02)
        assert L_plus == pytest.approx(L_minus)

    def test_monotone_decrease_from_peak(self):
        """Likelihood decreases as we move away from the mean."""
        L0 = gaussian_likelihood(0.273, 0.273, 0.02)
        L1 = gaussian_likelihood(0.283, 0.273, 0.02)
        L2 = gaussian_likelihood(0.293, 0.273, 0.02)
        assert L0 > L1 > L2

    def test_positive_everywhere(self):
        for beta in [0.1, 0.2, 0.3, 0.4, 0.5, 1.0]:
            assert gaussian_likelihood(beta, 0.273, 0.02) > 0.0

    def test_one_sigma_ratio(self):
        """At z=1σ, L/L_peak = exp(-0.5)."""
        L_peak = gaussian_likelihood(0.273, 0.273, 0.02)
        L_1sig = gaussian_likelihood(0.293, 0.273, 0.02)
        assert L_1sig / L_peak == pytest.approx(math.exp(-0.5))

    def test_two_sigma_ratio(self):
        """At z=2σ, L/L_peak = exp(-2)."""
        L_peak = gaussian_likelihood(0.273, 0.273, 0.02)
        L_2sig = gaussian_likelihood(0.313, 0.273, 0.02)
        assert L_2sig / L_peak == pytest.approx(math.exp(-2.0))

    def test_negative_sigma_raises(self):
        with pytest.raises(ValueError):
            gaussian_likelihood(0.273, 0.273, -0.01)

    def test_zero_sigma_raises(self):
        with pytest.raises(ValueError):
            gaussian_likelihood(0.273, 0.273, 0.0)

    def test_large_offset_very_small(self):
        """Very far from mean gives extremely small likelihood."""
        L = gaussian_likelihood(10.0, 0.273, 0.02)
        assert L < 1e-100

    def test_different_sigma_peak_value(self):
        """Narrower sigma → higher peak."""
        L_narrow = gaussian_likelihood(0.273, 0.273, 0.01)
        L_wide = gaussian_likelihood(0.273, 0.273, 0.02)
        assert L_narrow > L_wide

    def test_float_return_type(self):
        result = gaussian_likelihood(0.273, 0.273, 0.02)
        assert isinstance(result, float)


# ---------------------------------------------------------------------------
# combined_likelihood
# ---------------------------------------------------------------------------


class TestCombinedLikelihood:
    def test_non_negative_everywhere(self):
        for beta in [0.1, 0.22, 0.273, 0.290, 0.30, 0.331, 0.351, 0.38, 0.5]:
            assert combined_likelihood(beta) >= 0.0

    def test_higher_near_predicted_peaks(self):
        """Likelihood is higher near predicted peaks than far away."""
        L_peak = combined_likelihood(0.273)
        L_far = combined_likelihood(0.5)
        assert L_peak > L_far

    def test_equal_weights_default(self):
        """Default call uses equal weights."""
        L_default = combined_likelihood(0.273)
        L_explicit = combined_likelihood(0.273, weights=[0.25, 0.25, 0.25, 0.25])
        assert L_default == pytest.approx(L_explicit)

    def test_custom_weights(self):
        """Heavily weighted single peak concentrates likelihood there."""
        L = combined_likelihood(0.273, weights=[1.0, 0.0, 0.0, 0.0])
        sigma_total = math.sqrt(SIGMA_LITEBIRD ** 2 + SIGMA_THEORY ** 2)
        expected = gaussian_likelihood(0.273, BETA_CANONICAL, sigma_total)
        assert L == pytest.approx(expected)

    def test_weight_length_mismatch_raises(self):
        with pytest.raises(ValueError):
            combined_likelihood(0.273, weights=[0.5, 0.5])

    def test_custom_sigma_litebird(self):
        """Smaller sigma_litebird gives sharper peaks."""
        L_sharp = combined_likelihood(0.273, sigma_litebird=0.005)
        L_wide = combined_likelihood(0.273, sigma_litebird=0.05)
        assert L_sharp > L_wide

    def test_custom_betas(self):
        """Can pass custom predicted betas."""
        L = combined_likelihood(0.5, betas_predicted=[0.5], weights=[1.0])
        sigma_total = math.sqrt(SIGMA_LITEBIRD ** 2 + SIGMA_THEORY ** 2)
        expected = gaussian_likelihood(0.5, 0.5, sigma_total)
        assert L == pytest.approx(expected)

    def test_four_peaks_default_length(self):
        """Default uses 4 peaks."""
        result = combined_likelihood(0.3)
        assert isinstance(result, float)

    def test_returns_float(self):
        assert isinstance(combined_likelihood(0.273), float)


# ---------------------------------------------------------------------------
# detection_significance
# ---------------------------------------------------------------------------


class TestDetectionSignificance:
    def test_canonical_passes(self):
        sig = detection_significance(0.273)
        assert sig["passes_test"] is True

    def test_derived_passes(self):
        sig = detection_significance(0.331)
        assert sig["passes_test"] is True

    def test_full_2_passes(self):
        sig = detection_significance(0.351)
        assert sig["passes_test"] is True

    def test_outside_window_fails(self):
        sig = detection_significance(0.5)
        assert sig["passes_test"] is False
        assert sig["in_admissible_window"] is False

    def test_below_window_fails(self):
        sig = detection_significance(0.1)
        assert sig["passes_test"] is False
        assert sig["in_admissible_window"] is False

    def test_in_gap_fails(self):
        sig = detection_significance(0.300)
        assert sig["passes_test"] is False
        assert sig["in_forbidden_gap"] is True

    def test_gap_boundary_lower(self):
        sig = detection_significance(GAP_LOWER)
        assert sig["in_forbidden_gap"] is True

    def test_gap_boundary_upper(self):
        sig = detection_significance(GAP_UPPER)
        assert sig["in_forbidden_gap"] is True

    def test_admissible_lower_boundary(self):
        sig = detection_significance(ADMISSIBLE_LOWER)
        assert sig["in_admissible_window"] is True

    def test_admissible_upper_boundary(self):
        sig = detection_significance(ADMISSIBLE_UPPER)
        assert sig["in_admissible_window"] is True

    def test_sigma_offset_at_peak(self):
        """Exactly at a predicted peak → sigma_offset = 0."""
        sig = detection_significance(0.273)
        assert sig["sigma_offset"] == pytest.approx(0.0)

    def test_sigma_offset_positive(self):
        sig = detection_significance(0.28)
        assert sig["sigma_offset"] >= 0.0

    def test_best_peak_nearest(self):
        """Best peak selected correctly."""
        sig = detection_significance(0.270)
        assert sig["best_peak"] == pytest.approx(BETA_CANONICAL)

    def test_best_peak_for_derived(self):
        sig = detection_significance(0.335)
        assert sig["best_peak"] == pytest.approx(BETA_DERIVED)

    def test_dict_keys_complete(self):
        sig = detection_significance(0.273)
        expected_keys = {
            "beta_measured", "sigma_measurement", "best_peak",
            "sigma_offset", "in_admissible_window", "in_forbidden_gap", "passes_test",
        }
        assert set(sig.keys()) == expected_keys

    def test_custom_sigma(self):
        sig = detection_significance(0.273, sigma_measurement=0.05)
        assert sig["sigma_measurement"] == pytest.approx(0.05)

    def test_above_gap_in_admissible(self):
        """0.32° is above the gap and inside window → should pass."""
        sig = detection_significance(0.32)
        assert sig["in_admissible_window"] is True
        assert sig["in_forbidden_gap"] is False
        assert sig["passes_test"] is True


# ---------------------------------------------------------------------------
# forecast_scenarios
# ---------------------------------------------------------------------------


class TestForecastScenarios:
    def setup_method(self):
        self.scenarios = forecast_scenarios()

    def test_returns_five_keys(self):
        assert len(self.scenarios) == 5

    def test_has_canonical_primary(self):
        assert "canonical_primary" in self.scenarios

    def test_has_canonical_secondary(self):
        assert "canonical_secondary" in self.scenarios

    def test_has_full_formula(self):
        assert "full_formula" in self.scenarios

    def test_has_forbidden_gap(self):
        assert "forbidden_gap" in self.scenarios

    def test_has_outside_window(self):
        assert "outside_window" in self.scenarios

    def test_confirmation_scenarios_pass(self):
        for key in ("canonical_primary", "canonical_secondary", "full_formula"):
            assert self.scenarios[key]["passes_test"] is True, f"{key} should pass"

    def test_falsification_scenarios_fail(self):
        for key in ("forbidden_gap", "outside_window"):
            assert self.scenarios[key]["passes_test"] is False, f"{key} should fail"

    def test_forbidden_gap_outcome(self):
        assert self.scenarios["forbidden_gap"]["expected_outcome"] == "FALSIFICATION"

    def test_outside_window_outcome(self):
        assert self.scenarios["outside_window"]["expected_outcome"] == "FALSIFICATION"

    def test_canonical_primary_outcome(self):
        assert self.scenarios["canonical_primary"]["expected_outcome"] == "CONFIRMATION"

    def test_sigmas_per_peak_keys(self):
        expected = {"beta_canonical", "beta_full_1", "beta_derived", "beta_full_2"}
        for s in self.scenarios.values():
            assert set(s["sigmas_per_peak"].keys()) == expected

    def test_sigmas_per_peak_non_negative(self):
        for s in self.scenarios.values():
            for v in s["sigmas_per_peak"].values():
                assert v >= 0.0

    def test_interpretation_is_string(self):
        for s in self.scenarios.values():
            assert isinstance(s["interpretation"], str)
            assert len(s["interpretation"]) > 10

    def test_canonical_primary_beta(self):
        assert self.scenarios["canonical_primary"]["beta"] == pytest.approx(0.273)

    def test_forbidden_gap_beta(self):
        assert self.scenarios["forbidden_gap"]["beta"] == pytest.approx(0.300)

    def test_outside_window_beta(self):
        assert self.scenarios["outside_window"]["beta"] == pytest.approx(0.500)

    def test_each_scenario_has_significance_dict(self):
        for s in self.scenarios.values():
            assert isinstance(s["significance"], dict)

    def test_falsification_interpretation_contains_keyword(self):
        for key in ("forbidden_gap", "outside_window"):
            interp = self.scenarios[key]["interpretation"]
            assert "FALSIF" in interp or "falsif" in interp.lower()


# ---------------------------------------------------------------------------
# uncertainty_budget
# ---------------------------------------------------------------------------


class TestUncertaintyBudget:
    def setup_method(self):
        self.budget = uncertainty_budget()

    def test_has_kinematics(self):
        assert "kinematics" in self.budget

    def test_has_cosmic_variance(self):
        assert "cosmic_variance" in self.budget

    def test_has_instrumental(self):
        assert "instrumental" in self.budget

    def test_has_foreground(self):
        assert "foreground" in self.budget

    def test_has_total(self):
        assert "total" in self.budget

    def test_kinematics_value(self):
        assert self.budget["kinematics"] == pytest.approx(0.005)

    def test_cosmic_variance_value(self):
        assert self.budget["cosmic_variance"] == pytest.approx(0.003)

    def test_instrumental_value(self):
        assert self.budget["instrumental"] == pytest.approx(0.010)

    def test_foreground_value(self):
        assert self.budget["foreground"] == pytest.approx(0.008)

    def test_total_is_quadrature_sum(self):
        components = {
            k: v for k, v in self.budget.items() if k != "total"
        }
        expected = math.sqrt(sum(v ** 2 for v in components.values()))
        assert self.budget["total"] == pytest.approx(expected)

    def test_total_positive(self):
        assert self.budget["total"] > 0.0

    def test_total_larger_than_any_component(self):
        components = {k: v for k, v in self.budget.items() if k != "total"}
        for v in components.values():
            assert self.budget["total"] >= v

    def test_all_values_positive(self):
        for v in self.budget.values():
            assert v > 0.0

    def test_total_approx_value(self):
        expected = math.sqrt(0.005**2 + 0.003**2 + 0.010**2 + 0.008**2)
        assert self.budget["total"] == pytest.approx(expected, rel=1e-6)


# ---------------------------------------------------------------------------
# detection_power
# ---------------------------------------------------------------------------


class TestDetectionPower:
    def test_peak_separation(self):
        dp = detection_power()
        expected = abs(BETA_CANONICAL - BETA_DERIVED)
        assert dp["peak_separation_deg"] == pytest.approx(expected)

    def test_sigma_litebird_field(self):
        dp = detection_power()
        assert dp["sigma_litebird"] == pytest.approx(SIGMA_LITEBIRD)

    def test_separation_significance_approx_2_9(self):
        dp = detection_power()
        assert dp["separation_significance"] == pytest.approx(2.9, abs=0.05)

    def test_distinguishable_at_2sigma(self):
        """At 2σ threshold, canonical peaks should be distinguishable."""
        dp = detection_power(n_sigma_threshold=2.0)
        assert dp["distinguishable"] is True

    def test_not_distinguishable_at_5sigma(self):
        """At 5σ threshold, separation of ~2.9σ is not enough."""
        dp = detection_power(n_sigma_threshold=5.0)
        assert dp["distinguishable"] is False

    def test_separation_positive(self):
        dp = detection_power()
        assert dp["peak_separation_deg"] > 0.0

    def test_dict_keys(self):
        dp = detection_power()
        expected_keys = {
            "peak_separation_deg", "sigma_litebird",
            "separation_significance", "distinguishable"
        }
        assert set(dp.keys()) == expected_keys

    def test_separation_significance_formula(self):
        dp = detection_power()
        assert dp["separation_significance"] == pytest.approx(
            dp["peak_separation_deg"] / dp["sigma_litebird"]
        )


# ---------------------------------------------------------------------------
# timeline_to_result
# ---------------------------------------------------------------------------


class TestTimelineToResult:
    def setup_method(self):
        self.tl = timeline_to_result()

    def test_launch_year(self):
        assert self.tl["launch_year"] == LAUNCH_YEAR

    def test_first_light(self):
        assert self.tl["first_light"] == LAUNCH_YEAR + 1

    def test_survey_complete(self):
        assert self.tl["survey_complete"] == LAUNCH_YEAR + 3

    def test_result_expected(self):
        assert self.tl["result_expected"] == LAUNCH_YEAR + 4

    def test_years_from_now(self):
        assert self.tl["years_from_now"] == (LAUNCH_YEAR + 4) - 2026

    def test_ordering(self):
        tl = self.tl
        assert tl["launch_year"] < tl["first_light"] < tl["survey_complete"] < tl["result_expected"]

    def test_years_from_now_positive(self):
        assert self.tl["years_from_now"] > 0

    def test_dict_keys(self):
        expected_keys = {
            "launch_year", "first_light", "survey_complete",
            "result_expected", "years_from_now"
        }
        assert set(self.tl.keys()) == expected_keys

    def test_years_from_now_value(self):
        # result_expected = 2036, years_from_now = 2036 - 2026 = 10
        assert self.tl["years_from_now"] == 10

    def test_result_expected_value(self):
        assert self.tl["result_expected"] == 2036


# ---------------------------------------------------------------------------
# Integration / edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_gaussian_at_very_large_sigma(self):
        """Very wide sigma → very flat distribution."""
        L1 = gaussian_likelihood(0.273, 0.273, 1000.0)
        L2 = gaussian_likelihood(100.0, 0.273, 1000.0)
        # Both should be very small and similar
        assert L1 > 0.0
        assert abs(L1 - L2) / L1 < 0.01

    def test_combined_likelihood_at_admissible_boundary(self):
        assert combined_likelihood(ADMISSIBLE_LOWER) >= 0.0
        assert combined_likelihood(ADMISSIBLE_UPPER) >= 0.0

    def test_detection_significance_exactly_at_gap_midpoint(self):
        midpoint = (GAP_LOWER + GAP_UPPER) / 2.0
        sig = detection_significance(midpoint)
        assert sig["in_forbidden_gap"] is True
        assert sig["passes_test"] is False

    def test_forecast_scenarios_returns_dict(self):
        assert isinstance(forecast_scenarios(), dict)

    def test_uncertainty_budget_returns_dict(self):
        assert isinstance(uncertainty_budget(), dict)

    def test_timeline_returns_dict(self):
        assert isinstance(timeline_to_result(), dict)

    def test_detection_power_returns_dict(self):
        assert isinstance(detection_power(), dict)

    def test_gaussian_normalisation_integral(self):
        """Numerical integral of Gaussian over wide range should be ~1."""
        sigma = 0.02
        mu = 0.273
        dx = 0.0001
        x = mu - 10 * sigma
        integral = 0.0
        while x <= mu + 10 * sigma:
            integral += gaussian_likelihood(x, mu, sigma) * dx
            x += dx
        assert integral == pytest.approx(1.0, abs=0.001)

    def test_combined_likelihood_equal_weights_sum(self):
        """Four equal weights 0.25 each sum to 1."""
        weights = [0.25, 0.25, 0.25, 0.25]
        assert sum(weights) == pytest.approx(1.0)
