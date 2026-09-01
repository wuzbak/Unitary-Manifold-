# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 880 — LiteBIRD birefringence discrimination preparation."""
from __future__ import annotations

import pytest

from src.core.pillar880_birefringence_litebird_prep import (
    BETA_HIGH_DEG,
    BETA_LOW_DEG,
    BRANCHES_OUTSIDE_GAP,
    DELTA_BETA_DEG,
    DISCRIMINATION_POSSIBLE,
    GAP_INSIDE_WINDOW,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    LITEBIRD_LAUNCH_YEAR,
    LITEBIRD_SIGMA_BETA_DEG,
    MEASUREMENT_AVAILABLE,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    SNR_BRANCH,
    SNR_DISCRIMINATE,
    beta_falsifies,
    branch_separation_deg,
    litebird_prep_summary,
    snr_branch,
    snr_discriminate,
)


class TestPillar880Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 880
    def test_gate(self): assert PILLAR_GATE == "LITEBIRD_DISCRIMINATION_PREPARED"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 15
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2591
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2606
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER
    def test_launch_year(self): assert LITEBIRD_LAUNCH_YEAR == 2032
    def test_measurement_not_available(self): assert MEASUREMENT_AVAILABLE is False


class TestPillar880Branches:
    def test_beta_low(self): assert BETA_LOW_DEG == pytest.approx(0.273)
    def test_beta_high(self): assert BETA_HIGH_DEG == pytest.approx(0.331)
    def test_branch_ordering(self): assert BETA_LOW_DEG < BETA_HIGH_DEG
    def test_separation(self): assert DELTA_BETA_DEG == pytest.approx(0.058, abs=1e-12)
    def test_separation_function(self):
        assert branch_separation_deg() == pytest.approx(DELTA_BETA_DEG, rel=1e-12)
    def test_separation_positive(self): assert DELTA_BETA_DEG > 0.0
    def test_branches_outside_gap(self): assert BRANCHES_OUTSIDE_GAP is True
    def test_gap_inside_window(self): assert GAP_INSIDE_WINDOW is True


class TestPillar880SNR:
    def test_sigma_beta(self): assert LITEBIRD_SIGMA_BETA_DEG == pytest.approx(0.010)
    def test_snr_branch(self): assert SNR_BRANCH == pytest.approx(5.8, rel=1e-9)
    def test_snr_branch_function(self):
        assert snr_branch() == pytest.approx(SNR_BRANCH, rel=1e-12)
    def test_snr_branch_rejects_zero_sigma(self):
        with pytest.raises(ValueError):
            snr_branch(sigma_beta=0.0)
    def test_snr_discriminate(self): assert SNR_DISCRIMINATE == pytest.approx(4.10121933, rel=1e-7)
    def test_snr_discriminate_function(self):
        assert snr_discriminate() == pytest.approx(SNR_DISCRIMINATE, rel=1e-12)
    def test_discriminate_is_branch_over_root_two(self):
        assert SNR_DISCRIMINATE == pytest.approx(SNR_BRANCH / (2.0**0.5), rel=1e-12)
    def test_discrimination_possible(self): assert DISCRIMINATION_POSSIBLE is True
    def test_discrimination_above_three_sigma(self): assert SNR_DISCRIMINATE > 3.0
    def test_snr_scales_inversely_with_sigma(self):
        assert snr_branch(sigma_beta=0.02) < SNR_BRANCH


class TestPillar880Falsification:
    def test_below_window_falsifies(self): assert beta_falsifies(0.10) is True
    def test_above_window_falsifies(self): assert beta_falsifies(0.50) is True
    def test_low_branch_does_not_falsify(self): assert beta_falsifies(BETA_LOW_DEG) is False
    def test_high_branch_does_not_falsify(self): assert beta_falsifies(BETA_HIGH_DEG) is False
    def test_gap_centre_falsifies(self): assert beta_falsifies(0.30) is True
    def test_admissible_window(self):
        assert litebird_prep_summary()["admissible_window_deg"] == [0.22, 0.38]
    def test_forbidden_gap(self):
        assert litebird_prep_summary()["forbidden_gap_deg"] == [0.29, 0.31]


class TestPillar880Summary:
    def test_summary_gate(self): assert litebird_prep_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert litebird_prep_summary()["pillar"] == 880
    def test_summary_lean4(self): assert litebird_prep_summary()["lean4_total_after"] == 2606
    def test_summary_no_measurement(self):
        assert litebird_prep_summary()["measurement_available"] is False
    def test_summary_discrimination(self):
        assert litebird_prep_summary()["discrimination_possible"] is True
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2
    def test_epistemic_status_prepared_not_confirmed(self):
        status = litebird_prep_summary()["epistemic_status"].upper()
        assert "CONFIRMED" not in status
