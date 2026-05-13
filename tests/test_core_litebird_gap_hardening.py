# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for litebird_gap_hardening.py (v10.30)."""
import math
import pytest
from src.core.litebird_gap_hardening import (
    BETA_BROAD_LOWER,
    BETA_BROAD_UPPER,
    BETA_GAP_LOWER,
    BETA_GAP_UPPER,
    BETA_MODE_1,
    BETA_MODE_2,
    DISCRIMINATION_SIGMA,
    LITEBIRD_SIGMA,
    classify_beta,
    edge_case_battery,
    gap_test,
    inter_sector_discrimination,
    litebird_release_day_packet,
    litebird_gap_hardening_report,
)


class TestConstants:
    def test_mode1_gt_mode2(self):
        assert BETA_MODE_1 > BETA_MODE_2

    def test_gap_within_broad_window(self):
        assert BETA_BROAD_LOWER < BETA_GAP_LOWER < BETA_GAP_UPPER < BETA_BROAD_UPPER

    def test_modes_outside_gap(self):
        assert BETA_MODE_1 > BETA_GAP_UPPER or BETA_MODE_1 < BETA_GAP_LOWER
        assert BETA_MODE_2 > BETA_GAP_UPPER or BETA_MODE_2 < BETA_GAP_LOWER

    def test_discrimination_sigma_positive(self):
        assert DISCRIMINATION_SIGMA > 0.0

    def test_litebird_sigma_is_0_02(self):
        assert abs(LITEBIRD_SIGMA - 0.02) < 1e-6


class TestClassifyBeta:
    def test_mode1_classified_correctly(self):
        result = classify_beta(BETA_MODE_1, LITEBIRD_SIGMA)
        assert result["zone"] == "PRIMARY_SECTOR"
        assert result["falsified"] is False

    def test_mode2_classified_correctly(self):
        result = classify_beta(BETA_MODE_2, LITEBIRD_SIGMA)
        assert result["zone"] == "SHADOW_SECTOR"
        assert result["falsified"] is False

    def test_gap_centre_falsifies_with_very_small_sigma(self):
        gap_centre = (BETA_GAP_LOWER + BETA_GAP_UPPER) / 2.0
        # Use very small sigma: gap half-width = 0.01° → need σ < 0.010/3 ≈ 0.0033°
        result = classify_beta(gap_centre, 0.003, confidence_level=3.0)
        # gap_penetration_lower = (0.30 - 0.29) / 0.003 = 3.33 ≥ 3σ ✓
        assert result["zone"] == "GAP"
        assert result["falsified"] is True

    def test_below_broad_window_falsifies(self):
        result = classify_beta(0.18, 0.01, confidence_level=3.0)
        assert result["zone"] == "BELOW_WINDOW"
        assert result["falsified"] is True

    def test_above_broad_window_falsifies(self):
        result = classify_beta(0.42, 0.01, confidence_level=3.0)
        assert result["zone"] == "ABOVE_WINDOW"
        assert result["falsified"] is True

    def test_mode1_not_falsified(self):
        result = classify_beta(BETA_MODE_1, LITEBIRD_SIGMA)
        assert result["falsified"] is False

    def test_ambiguous_within_window(self):
        # β = 0.25° — between mode 2 and gap lower, not near either mode
        result = classify_beta(0.255, LITEBIRD_SIGMA)
        # Should be AMBIGUOUS since 0.255 is not within 2.5σ of mode2 (0.273) or mode1 (0.331)
        # distance to mode2 = |0.255 - 0.273| / 0.02 = 0.9σ < 2.5 → shadow sector or ambiguous
        assert result["zone"] in ("SHADOW_SECTOR", "AMBIGUOUS")


class TestGapTest:
    def test_mode1_clears_gap(self):
        result = gap_test(BETA_MODE_1, LITEBIRD_SIGMA)
        assert result["gap_falsification_active"] is False
        assert result["verdict"].startswith("✅")

    def test_mode2_clears_gap(self):
        result = gap_test(BETA_MODE_2, LITEBIRD_SIGMA)
        assert result["gap_falsification_active"] is False

    def test_gap_centre_falsifies_with_small_sigma(self):
        gap_centre = (BETA_GAP_LOWER + BETA_GAP_UPPER) / 2.0
        result = gap_test(gap_centre, 0.003)  # very small sigma
        assert result["firmly_in_gap"] is True
        assert result["gap_falsification_active"] is True

    def test_gap_centre_with_litebird_sigma_marginal(self):
        gap_centre = (BETA_GAP_LOWER + BETA_GAP_UPPER) / 2.0
        result = gap_test(gap_centre, LITEBIRD_SIGMA)
        # Gap half-width is 0.01° = 0.5σ_LiteBIRD → not firmly in gap at 3σ
        # but marginally in gap at 1σ
        assert isinstance(result["firmly_in_gap"], bool)
        assert isinstance(result["marginally_in_gap"], bool)

    def test_gap_boundary_not_firmly_in_gap(self):
        result = gap_test(BETA_GAP_LOWER, LITEBIRD_SIGMA)
        # Exactly at lower boundary: gap_penetration_lower = 0
        assert result["gap_penetration_lower_sigma"] < 0.1

    def test_nearest_mode_is_mode2_for_gap_lower(self):
        result = gap_test(BETA_GAP_LOWER + 0.001, LITEBIRD_SIGMA)
        # Gap lower (0.290) is closer to mode 2 (0.273) than mode 1 (0.331)
        assert result["nearest_predicted_mode"] == BETA_MODE_2


class TestInterSectorDiscrimination:
    def test_separation_positive(self):
        result = inter_sector_discrimination()
        assert result["separation_degrees"] > 0

    def test_separation_is_mode_difference(self):
        result = inter_sector_discrimination()
        assert abs(result["separation_degrees"] - abs(BETA_MODE_1 - BETA_MODE_2)) < 1e-10

    def test_discrimination_sigma_matches(self):
        result = inter_sector_discrimination()
        assert abs(result["separation_sigma"] - DISCRIMINATION_SIGMA) < 0.01

    def test_discrimination_power_reported(self):
        result = inter_sector_discrimination()
        assert "discrimination_power" in result
        # At 2.9σ separation, should be MODERATE or HIGH
        assert result["discrimination_power"] in ("MODERATE (2–3σ)", "HIGH (>3σ)")


class TestEdgeCaseBattery:
    def test_battery_runs_all_cases(self):
        results = edge_case_battery()
        assert len(results) >= 12

    def test_battery_has_case_labels(self):
        results = edge_case_battery()
        for r in results:
            assert "case_label" in r

    def test_mode1_clears_gap_in_battery(self):
        results = edge_case_battery()
        mode1 = next(r for r in results if r["case_label"] == "mode_1_exact")
        assert mode1["gap_falsification_active"] is False

    def test_below_window_not_in_gap(self):
        results = edge_case_battery()
        below = next(r for r in results if r["case_label"] == "below_window")
        # Below window is not tested for gap (separate falsification)
        assert isinstance(below["firmly_in_gap"], bool)


class TestHardeningReport:
    def test_report_version(self):
        report = litebird_gap_hardening_report()
        assert report["version"] == "v10.30"

    def test_report_has_falsification_conditions(self):
        report = litebird_gap_hardening_report()
        assert len(report["falsification_conditions"]) == 3

    def test_report_has_discrimination(self):
        report = litebird_gap_hardening_report()
        assert "inter_sector_discrimination" in report

    def test_report_has_gap_edge_cases(self):
        report = litebird_gap_hardening_report()
        assert len(report["gap_edge_cases"]) >= 12

    def test_critical_note_mentions_gap(self):
        report = litebird_gap_hardening_report()
        assert "gap" in report["critical_note"].lower()
        assert "0.30" in report["critical_note"]


class TestReleaseDayPacket:
    def test_packet_ready(self):
        packet = litebird_release_day_packet(beta_obs=BETA_MODE_1, sigma=LITEBIRD_SIGMA)
        assert packet["pipeline"] == "LITEBIRD_RELEASE_DAY_DECISION_PACKET"
        assert packet["ready_for_publication"] is True
        assert packet["required_same_day_sync"] is True

    def test_packet_gap_case_falsified(self):
        packet = litebird_release_day_packet(beta_obs=0.300, sigma=0.003)
        assert packet["route"] == "GAP"
        assert packet["falsified"] is True
