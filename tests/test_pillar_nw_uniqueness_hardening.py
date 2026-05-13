# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for src/core/pillar_nw_uniqueness_hardening.py."""

from __future__ import annotations

import pytest

from src.core.pillar_nw_uniqueness_hardening import (
    PLANCK_NS_CENTRAL,
    PLANCK_NS_SIGMA,
    N_W_SCAN_MIN,
    N_W_SCAN_MAX,
    N_W_FINALISTS,
    REMAINING_OPEN_FIRST_PRINCIPLES_ARGUMENT,
    enumerate_nw_candidates,
    quantified_elimination_report,
    preferred_winding_from_spectral_residuals,
)


class TestConstants:
    def test_scan_bounds(self):
        assert N_W_SCAN_MIN == 1
        assert N_W_SCAN_MAX == 10

    def test_planck_constants_positive(self):
        assert PLANCK_NS_CENTRAL > 0
        assert PLANCK_NS_SIGMA > 0

    def test_finalists(self):
        assert set(N_W_FINALISTS) == {5, 7}

    def test_open_argument_nonempty(self):
        assert len(REMAINING_OPEN_FIRST_PRINCIPLES_ARGUMENT) > 20


class TestEnumeration:
    def test_default_scan_size(self):
        scan = enumerate_nw_candidates()
        assert len(scan) == 10

    def test_scan_includes_1_to_10(self):
        scan = enumerate_nw_candidates()
        assert [row["n_w"] for row in scan] == list(range(1, 11))

    def test_invalid_range_raises(self):
        with pytest.raises(ValueError):
            enumerate_nw_candidates(0, 10)
        with pytest.raises(ValueError):
            enumerate_nw_candidates(5, 4)

    def test_records_have_required_keys(self):
        row = enumerate_nw_candidates()[0]
        for key in (
            "n_w",
            "odd_z2",
            "stable_generation_count",
            "three_generation_window",
            "k_cs_minimum_step",
            "ns_prediction",
            "ns_residual",
            "chi2",
            "hard_constraints_pass",
            "eliminated",
            "elimination_reasons",
        ):
            assert key in row


class TestConstraintEliminationPerCandidate:
    @pytest.mark.parametrize("n_w", [1, 2, 3, 4, 6, 8, 9, 10])
    def test_non_57_candidates_eliminated(self, n_w):
        row = [r for r in enumerate_nw_candidates() if r["n_w"] == n_w][0]
        assert row["eliminated"] is True

    @pytest.mark.parametrize("n_w", [5, 7])
    def test_57_survive_hard_constraints(self, n_w):
        row = [r for r in enumerate_nw_candidates() if r["n_w"] == n_w][0]
        assert row["hard_constraints_pass"] is True

    def test_even_numbers_fail_z2(self):
        for n_w in [2, 4, 6, 8, 10]:
            row = [r for r in enumerate_nw_candidates() if r["n_w"] == n_w][0]
            assert row["odd_z2"] is False

    def test_three_generation_window_true_only_for_4_to_8(self):
        scan = enumerate_nw_candidates()
        for row in scan:
            expected = 4 <= row["n_w"] <= 8
            assert row["three_generation_window"] is expected

    def test_reason_present_for_nw1(self):
        row = [r for r in enumerate_nw_candidates() if r["n_w"] == 1][0]
        assert len(row["elimination_reasons"]) >= 1

    def test_reason_present_for_nw2(self):
        row = [r for r in enumerate_nw_candidates() if r["n_w"] == 2][0]
        assert any("Z2" in reason or "Z2" in reason for reason in row["elimination_reasons"])

    def test_reason_present_for_nw9(self):
        row = [r for r in enumerate_nw_candidates() if r["n_w"] == 9][0]
        assert any("three-generation" in reason for reason in row["elimination_reasons"])


class TestQuantifiedReport:
    def test_report_structure(self):
        report = quantified_elimination_report()
        for key in (
            "scan_range",
            "total_candidates",
            "survivors",
            "survivor_nw",
            "eliminated",
            "eliminated_nw",
            "remaining_open_first_principles_argument",
        ):
            assert key in report

    def test_survivors_are_5_and_7(self):
        report = quantified_elimination_report()
        assert set(report["survivor_nw"]) == {5, 7}

    def test_eliminated_count_is_8(self):
        report = quantified_elimination_report()
        assert len(report["eliminated_nw"]) == 8

    def test_total_candidates_is_10(self):
        report = quantified_elimination_report()
        assert report["total_candidates"] == 10

    def test_survivor_records_not_eliminated(self):
        report = quantified_elimination_report()
        for row in report["survivors"]:
            assert row["eliminated"] is False

    def test_eliminated_records_flagged(self):
        report = quantified_elimination_report()
        for row in report["eliminated"]:
            assert row["eliminated"] is True


class TestSpectralScoring:
    def test_preferred_winding_is_5(self):
        pref = preferred_winding_from_spectral_residuals()
        assert pref["preferred_n_w"] == 5

    def test_runner_up_is_7(self):
        pref = preferred_winding_from_spectral_residuals()
        assert pref["runner_up_n_w"] == 7

    def test_chi2_gap_positive(self):
        pref = preferred_winding_from_spectral_residuals()
        assert pref["chi2_gap"] > 0.0

    def test_best_chi2_less_than_runner_up(self):
        pref = preferred_winding_from_spectral_residuals()
        assert pref["best_chi2"] < pref["runner_up_chi2"]

    def test_nw5_residual_less_than_nw7_residual(self):
        pref = preferred_winding_from_spectral_residuals()
        assert pref["best_ns_residual"] < pref["runner_up_ns_residual"]

    def test_all_candidates_have_nonnegative_chi2(self):
        pref = preferred_winding_from_spectral_residuals()
        for row in pref["all_candidates"]:
            assert row["chi2"] >= 0.0

    def test_ns_prediction_ordering(self):
        scan = enumerate_nw_candidates()
        row5 = [r for r in scan if r["n_w"] == 5][0]
        row7 = [r for r in scan if r["n_w"] == 7][0]
        assert abs(row5["ns_prediction"] - PLANCK_NS_CENTRAL) < abs(row7["ns_prediction"] - PLANCK_NS_CENTRAL)

    def test_nw5_close_to_planck(self):
        row5 = [r for r in enumerate_nw_candidates() if r["n_w"] == 5][0]
        assert row5["ns_residual"] < 2.0 * PLANCK_NS_SIGMA

    def test_nw7_farther_than_nw5(self):
        scan = enumerate_nw_candidates()
        row5 = [r for r in scan if r["n_w"] == 5][0]
        row7 = [r for r in scan if r["n_w"] == 7][0]
        assert row7["chi2"] > row5["chi2"]


class TestRangeCustomization:
    def test_custom_range(self):
        scan = enumerate_nw_candidates(3, 8)
        assert [row["n_w"] for row in scan] == [3, 4, 5, 6, 7, 8]

    def test_custom_range_survivors(self):
        report = quantified_elimination_report(3, 8)
        assert set(report["survivor_nw"]) == {5, 7}

    def test_open_argument_preserved(self):
        report = quantified_elimination_report()
        assert "first-principles" in report["remaining_open_first_principles_argument"]
