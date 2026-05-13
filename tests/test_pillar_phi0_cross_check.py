# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for src/core/pillar_phi0_cross_check.py."""

from __future__ import annotations

import pytest

from src.core.pillar_phi0_cross_check import (
    BOUNDARY_PERIODICITY_FACTOR,
    HOLOGRAPHIC_BOUNDARY_CORRECTION,
    PHI0_CROSS_CHECK_RELATIVE_ERROR,
    phi0_from_pillar56,
    phi0_from_holographic_boundary,
    phi0_cross_check_relative_error,
    phi0_cross_check_summary,
)


class TestConstants:
    def test_periodicity_factor(self):
        assert BOUNDARY_PERIODICITY_FACTOR > 6.0

    def test_boundary_correction_gt_one(self):
        assert HOLOGRAPHIC_BOUNDARY_CORRECTION > 1.0

    def test_named_error_nonnegative(self):
        assert PHI0_CROSS_CHECK_RELATIVE_ERROR >= 0.0


class TestCoreFunctions:
    def test_phi0_from_pillar56_positive(self):
        assert phi0_from_pillar56() > 0.0

    def test_phi0_from_boundary_positive(self):
        assert phi0_from_holographic_boundary() > 0.0

    def test_phi0_boundary_invalid_nw_raises(self):
        with pytest.raises(ValueError):
            phi0_from_holographic_boundary(n_winding=0)

    def test_phi0_boundary_invalid_kcs_raises(self):
        with pytest.raises(ValueError):
            phi0_from_holographic_boundary(k_cs=0)

    def test_relative_error_default_lt_1pct(self):
        assert phi0_cross_check_relative_error() < 0.01

    def test_relative_error_named_constant_lt_1pct(self):
        assert PHI0_CROSS_CHECK_RELATIVE_ERROR < 0.01

    def test_relative_error_zero_for_equal_inputs(self):
        ref = phi0_from_pillar56()
        assert phi0_cross_check_relative_error(phi0_reference=ref, phi0_boundary=ref) == pytest.approx(0.0)

    def test_relative_error_invalid_reference_raises(self):
        with pytest.raises(ValueError):
            phi0_cross_check_relative_error(phi0_reference=0.0, phi0_boundary=1.0)


class TestSummary:
    def test_summary_keys(self):
        summary = phi0_cross_check_summary()
        for key in (
            "n_winding",
            "k_cs",
            "c_s",
            "phi0_pillar56",
            "phi0_holographic_boundary",
            "relative_error",
            "agreement_lt_1pct",
            "independent_path_note",
            "remaining_open_note",
        ):
            assert key in summary

    def test_summary_agreement_flag_true(self):
        summary = phi0_cross_check_summary()
        assert summary["agreement_lt_1pct"] is True

    def test_summary_relative_error_lt_1pct(self):
        summary = phi0_cross_check_summary()
        assert summary["relative_error"] < 0.01

    def test_summary_phi0_values_close(self):
        summary = phi0_cross_check_summary()
        assert abs(summary["phi0_pillar56"] - summary["phi0_holographic_boundary"]) < 0.5

    def test_summary_notes_nonempty(self):
        summary = phi0_cross_check_summary()
        assert len(summary["independent_path_note"]) > 20
        assert len(summary["remaining_open_note"]) > 20


class TestBehavioralCoverage:
    def test_boundary_phi0_scales_with_nw(self):
        p5 = phi0_from_holographic_boundary(n_winding=5, k_cs=74)
        p7 = phi0_from_holographic_boundary(n_winding=7, k_cs=74)
        assert p7 > p5

    def test_boundary_phi0_decreases_with_higher_kcs(self):
        p74 = phi0_from_holographic_boundary(n_winding=5, k_cs=74)
        p100 = phi0_from_holographic_boundary(n_winding=5, k_cs=100)
        assert p100 < p74

    def test_default_error_matches_summary(self):
        summary = phi0_cross_check_summary()
        assert phi0_cross_check_relative_error() == pytest.approx(summary["relative_error"])

    def test_named_error_matches_function(self):
        assert PHI0_CROSS_CHECK_RELATIVE_ERROR == pytest.approx(phi0_cross_check_relative_error())

    def test_reference_and_boundary_within_1_percent(self):
        ref = phi0_from_pillar56()
        bdy = phi0_from_holographic_boundary()
        rel = abs(ref - bdy) / ref
        assert rel < 0.01

    def test_summary_reference_value_is_reasonable(self):
        assert 30.0 < phi0_from_pillar56() < 33.0

    def test_summary_boundary_value_is_reasonable(self):
        assert 30.0 < phi0_from_holographic_boundary() < 33.5
