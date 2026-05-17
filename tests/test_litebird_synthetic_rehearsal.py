# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
tests/test_litebird_synthetic_rehearsal.py
==========================================
Comprehensive test suite for the LiteBIRD synthetic rehearsal module.
~45 tests covering constants, random generation, rehearsal run structure,
classification rates, all 6 scenarios, gap power, and discrimination power.
"""
from __future__ import annotations

import math

import pytest

from src.core.litebird_synthetic_rehearsal import (
    BETA_BROAD_LOWER,
    BETA_BROAD_UPPER,
    BETA_GAP_LOWER,
    BETA_GAP_UPPER,
    BETA_MODE_1,
    BETA_MODE_2,
    N_SYNTHETIC_RUNS,
    SIGMA_LITEBIRD,
    full_rehearsal_suite,
    gap_rehearsal_power,
    generate_synthetic_measurements,
    litebird_rehearsal_report,
    rehearsal_run,
    sector_discrimination_power,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_n_synthetic_runs():
    assert N_SYNTHETIC_RUNS == 500


def test_sigma_litebird():
    assert math.isclose(SIGMA_LITEBIRD, 0.020)


def test_beta_mode_1():
    assert math.isclose(BETA_MODE_1, 0.331)


def test_beta_mode_2():
    assert math.isclose(BETA_MODE_2, 0.273)


def test_beta_gap_lower():
    assert math.isclose(BETA_GAP_LOWER, 0.290)


def test_beta_gap_upper():
    assert math.isclose(BETA_GAP_UPPER, 0.310)


def test_beta_broad_lower():
    assert math.isclose(BETA_BROAD_LOWER, 0.220)


def test_beta_broad_upper():
    assert math.isclose(BETA_BROAD_UPPER, 0.380)


def test_modes_inside_broad_window():
    assert BETA_BROAD_LOWER < BETA_MODE_2 < BETA_MODE_1 < BETA_BROAD_UPPER


def test_gap_inside_broad_window():
    assert BETA_BROAD_LOWER < BETA_GAP_LOWER < BETA_GAP_UPPER < BETA_BROAD_UPPER


def test_gap_between_modes():
    assert BETA_MODE_2 < BETA_GAP_LOWER < BETA_GAP_UPPER < BETA_MODE_1


# ---------------------------------------------------------------------------
# generate_synthetic_measurements
# ---------------------------------------------------------------------------


def test_generate_length():
    measurements = generate_synthetic_measurements(100, 0.331, 0.020)
    assert len(measurements) == 100


def test_generate_returns_list_of_floats():
    measurements = generate_synthetic_measurements(10, 0.331, 0.020)
    assert isinstance(measurements, list)
    for m in measurements:
        assert isinstance(m, float)


def test_generate_reproducible_with_seed():
    m1 = generate_synthetic_measurements(50, 0.331, 0.020, seed=42)
    m2 = generate_synthetic_measurements(50, 0.331, 0.020, seed=42)
    assert m1 == m2


def test_generate_different_seeds_differ():
    m1 = generate_synthetic_measurements(50, 0.331, 0.020, seed=1)
    m2 = generate_synthetic_measurements(50, 0.331, 0.020, seed=2)
    assert m1 != m2


def test_generate_mean_close_to_true_beta():
    measurements = generate_synthetic_measurements(2000, 0.331, 0.020, seed=0)
    mean = sum(measurements) / len(measurements)
    assert abs(mean - 0.331) < 0.005  # within 0.25σ of true value


def test_generate_std_close_to_sigma():
    import math
    measurements = generate_synthetic_measurements(2000, 0.331, 0.020, seed=0)
    mean = sum(measurements) / len(measurements)
    var = sum((x - mean) ** 2 for x in measurements) / len(measurements)
    std = math.sqrt(var)
    assert abs(std - 0.020) < 0.003


# ---------------------------------------------------------------------------
# rehearsal_run — structure
# ---------------------------------------------------------------------------


def test_rehearsal_run_keys():
    result = rehearsal_run(true_beta=BETA_MODE_1)
    for key in (
        "true_beta",
        "expected_verdict",
        "verdict_distribution",
        "falsified_count",
        "supported_count",
        "ambiguous_count",
        "correct_classification_rate",
        "false_positive_rate",
    ):
        assert key in result


def test_rehearsal_run_true_beta_preserved():
    result = rehearsal_run(true_beta=0.331)
    assert result["true_beta"] == 0.331


def test_rehearsal_run_counts_sum_to_n():
    result = rehearsal_run(true_beta=BETA_MODE_1, n_runs=200)
    total = sum(result["verdict_distribution"].values())
    assert total == 200


def test_rehearsal_run_correct_rate_in_bounds():
    result = rehearsal_run(true_beta=BETA_MODE_1)
    assert 0.0 <= result["correct_classification_rate"] <= 1.0


def test_rehearsal_run_false_positive_rate_in_bounds():
    result = rehearsal_run(true_beta=BETA_MODE_1)
    assert 0.0 <= result["false_positive_rate"] <= 1.0


def test_rehearsal_run_mode1_mostly_primary():
    result = rehearsal_run(true_beta=BETA_MODE_1, n_runs=500)
    primary_frac = result["verdict_distribution"].get("PRIMARY_SECTOR", 0) / 500
    assert primary_frac > 0.80


def test_rehearsal_run_mode2_mostly_shadow():
    result = rehearsal_run(true_beta=BETA_MODE_2, n_runs=500)
    shadow_frac = result["verdict_distribution"].get("SHADOW_SECTOR", 0) / 500
    assert shadow_frac > 0.75


def test_rehearsal_run_gap_mostly_gap_falsified():
    """Gap is 1σ wide; ~38% of draws from N(gap_centre, sigma) fall inside.
    We verify GAP_FALSIFIED is the plurality verdict for gap_centre, and
    that the expected_verdict is set correctly."""
    gap_centre = (BETA_GAP_LOWER + BETA_GAP_UPPER) / 2.0
    result = rehearsal_run(true_beta=gap_centre, n_runs=500)
    assert result["expected_verdict"] == "GAP_FALSIFIED"
    gap_frac = result["verdict_distribution"].get("GAP_FALSIFIED", 0) / 500
    assert gap_frac > 0.30


def test_rehearsal_run_below_window_mostly_falsified():
    """true_beta = 0.18, sigma = 0.020; window boundary at 0.22.
    Point-estimate: P(m < 0.22 from N(0.18, 0.020)) ≈ 97.7% → > 0.95."""
    result = rehearsal_run(true_beta=0.18, n_runs=500)
    falsified_count = (
        result["verdict_distribution"].get("FALSIFIED", 0)
        + result["verdict_distribution"].get("GAP_FALSIFIED", 0)
    )
    assert falsified_count / 500 > 0.95


def test_rehearsal_run_above_window_mostly_falsified():
    """true_beta = 0.42, sigma = 0.020; window boundary at 0.38.
    Point-estimate: P(m > 0.38 from N(0.42, 0.020)) ≈ 97.7% → > 0.95."""
    result = rehearsal_run(true_beta=0.42, n_runs=500)
    falsified_count = (
        result["verdict_distribution"].get("FALSIFIED", 0)
        + result["verdict_distribution"].get("GAP_FALSIFIED", 0)
    )
    assert falsified_count / 500 > 0.95


def test_rehearsal_run_false_positive_zero_when_true_falsified():
    """When true β is outside the window, false_positive_rate must be 0."""
    result = rehearsal_run(true_beta=0.18)
    assert result["false_positive_rate"] == 0.0


# ---------------------------------------------------------------------------
# full_rehearsal_suite — all 6 scenarios
# ---------------------------------------------------------------------------


def test_full_rehearsal_suite_has_six_scenarios():
    suite = full_rehearsal_suite()
    assert len(suite) == 6


def test_full_rehearsal_suite_scenario_names():
    suite = full_rehearsal_suite()
    expected_names = {
        "mode_1", "mode_2", "gap_centre", "below_window", "above_window", "ambiguous"
    }
    assert set(suite.keys()) == expected_names


def test_full_rehearsal_suite_mode1_expected_primary():
    suite = full_rehearsal_suite()
    assert suite["mode_1"]["expected_verdict"] == "PRIMARY_SECTOR"


def test_full_rehearsal_suite_mode2_expected_shadow():
    suite = full_rehearsal_suite()
    assert suite["mode_2"]["expected_verdict"] == "SHADOW_SECTOR"


def test_full_rehearsal_suite_gap_centre_expected_gap():
    suite = full_rehearsal_suite()
    assert suite["gap_centre"]["expected_verdict"] == "GAP_FALSIFIED"


def test_full_rehearsal_suite_below_expected_falsified():
    suite = full_rehearsal_suite()
    assert suite["below_window"]["expected_verdict"] == "FALSIFIED"


def test_full_rehearsal_suite_above_expected_falsified():
    suite = full_rehearsal_suite()
    assert suite["above_window"]["expected_verdict"] == "FALSIFIED"


def test_full_rehearsal_suite_ambiguous_expected():
    suite = full_rehearsal_suite()
    assert suite["ambiguous"]["expected_verdict"] == "AMBIGUOUS"


def test_full_rehearsal_suite_all_have_distribution():
    suite = full_rehearsal_suite()
    for name, result in suite.items():
        assert "verdict_distribution" in result
        assert sum(result["verdict_distribution"].values()) == N_SYNTHETIC_RUNS


# ---------------------------------------------------------------------------
# gap_rehearsal_power
# ---------------------------------------------------------------------------


def test_gap_rehearsal_power_keys():
    power = gap_rehearsal_power()
    for key in (
        "gap_centre",
        "sigma",
        "n_runs",
        "gap_detection_rate",
        "gap_sigma_margin",
        "power_exceeds_0p99",
    ):
        assert key in power


def test_gap_rehearsal_power_centre():
    power = gap_rehearsal_power()
    expected_centre = (BETA_GAP_LOWER + BETA_GAP_UPPER) / 2.0
    assert math.isclose(power["gap_centre"], expected_centre)


def test_gap_rehearsal_power_exceeds_99_percent():
    power = gap_rehearsal_power()
    assert power["gap_detection_rate"] > 0.99
    assert power["power_exceeds_0p99"] is True


def test_gap_rehearsal_power_n_runs():
    power = gap_rehearsal_power()
    assert power["n_runs"] == N_SYNTHETIC_RUNS


def test_gap_rehearsal_power_sigma_margin():
    """Gap half-width = 0.01°, sigma = 0.02° → margin = 0.5 (firmly detectable at centre)."""
    power = gap_rehearsal_power()
    expected_margin = ((BETA_GAP_UPPER - BETA_GAP_LOWER) / 2.0) / SIGMA_LITEBIRD
    assert math.isclose(power["gap_sigma_margin"], expected_margin)


# ---------------------------------------------------------------------------
# sector_discrimination_power
# ---------------------------------------------------------------------------


def test_sector_discrimination_power_keys():
    disc = sector_discrimination_power()
    for key in (
        "discrimination_sigma",
        "mode_1_correct_rate",
        "mode_2_correct_rate",
        "mode_1_misclassified_rate",
        "mode_2_misclassified_rate",
        "both_above_0p90",
    ):
        assert key in disc


def test_sector_discrimination_sigma_about_2p9():
    disc = sector_discrimination_power()
    expected = abs(BETA_MODE_1 - BETA_MODE_2) / SIGMA_LITEBIRD
    assert math.isclose(disc["discrimination_sigma"], expected, rel_tol=1e-9)


def test_sector_discrimination_rates_in_bounds():
    disc = sector_discrimination_power()
    assert 0.0 <= disc["mode_1_correct_rate"] <= 1.0
    assert 0.0 <= disc["mode_2_correct_rate"] <= 1.0
    assert 0.0 <= disc["mode_1_misclassified_rate"] <= 1.0
    assert 0.0 <= disc["mode_2_misclassified_rate"] <= 1.0


def test_sector_discrimination_mode1_correct_above_0p80():
    disc = sector_discrimination_power()
    assert disc["mode_1_correct_rate"] > 0.80


def test_sector_discrimination_mode2_correct_above_0p50():
    """Mode 2 is between mode 1 and the gap; some measurements fall into ambiguous."""
    disc = sector_discrimination_power()
    assert disc["mode_2_correct_rate"] > 0.50


# ---------------------------------------------------------------------------
# litebird_rehearsal_report
# ---------------------------------------------------------------------------


def test_rehearsal_report_keys():
    report = litebird_rehearsal_report()
    for key in (
        "version",
        "title",
        "n_synthetic_runs",
        "sigma_litebird",
        "prediction_summary",
        "scenarios",
        "gap_power",
        "sector_discrimination",
        "key_findings",
    ):
        assert key in report


def test_rehearsal_report_has_six_scenarios():
    report = litebird_rehearsal_report()
    assert len(report["scenarios"]) == 6


def test_rehearsal_report_gap_power_exceeds_0p99():
    report = litebird_rehearsal_report()
    assert report["key_findings"]["gap_power_exceeds_0p99"] is True


def test_rehearsal_report_version_string():
    report = litebird_rehearsal_report()
    assert isinstance(report["version"], str)
    assert len(report["version"]) > 0


def test_rehearsal_report_n_synthetic_runs():
    report = litebird_rehearsal_report()
    assert report["n_synthetic_runs"] == N_SYNTHETIC_RUNS


def test_rehearsal_report_sigma_litebird():
    report = litebird_rehearsal_report()
    assert math.isclose(report["sigma_litebird"], SIGMA_LITEBIRD)


def test_rehearsal_report_prediction_summary_has_modes():
    report = litebird_rehearsal_report()
    summary = report["prediction_summary"]
    assert "mode_1" in summary
    assert "mode_2" in summary
    assert "gap" in summary
    assert "broad_window" in summary
