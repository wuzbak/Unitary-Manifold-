# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for lab_cp_experimental_design.py — WS-3 experimental design module."""
from __future__ import annotations

import math

import pytest

from src.core.lab_cp_experimental_design import (
    CONFIDENCE_LEVEL,
    N_REPLICATIONS_REQUIRED,
    SIGMA_A_DECISION_GRADE,
    blinding_protocol_spec,
    campaign_timeline_and_milestones,
    jj_squid_platform_spec,
    statistical_power_analysis,
    systematic_budget_allocation,
    topological_insulator_platform_spec,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_sigma_a_decision_grade(self):
        assert SIGMA_A_DECISION_GRADE == 1e-5

    def test_confidence_level(self):
        assert abs(CONFIDENCE_LEVEL - 0.95) < 1e-12

    def test_n_replications_required(self):
        assert N_REPLICATIONS_REQUIRED == 2


# ---------------------------------------------------------------------------
# statistical_power_analysis
# ---------------------------------------------------------------------------

class TestStatisticalPowerAnalysis:
    def test_large_n_gives_sigma_below_decision_grade(self):
        sigma_per = 1e-2
        n = 10**8  # large enough that σ_combined = 1e-2 / 1e4 = 1e-6
        result = statistical_power_analysis(1e-5, sigma_per, n)
        assert result["sigma_combined"] < SIGMA_A_DECISION_GRADE

    def test_snr_positive_for_nonzero_signal(self):
        result = statistical_power_analysis(1e-5, 1e-3, 10000)
        assert result["SNR"] > 0

    def test_power_increases_with_n(self):
        r1 = statistical_power_analysis(3e-5, 1e-3, 1000)
        r2 = statistical_power_analysis(3e-5, 1e-3, 1_000_000)
        assert r2["power_to_detect_signal_at_3sigma"] > r1["power_to_detect_signal_at_3sigma"]

    def test_sigma_combined_formula(self):
        sigma_per = 1e-3
        n = 100
        result = statistical_power_analysis(1e-5, sigma_per, n)
        expected = sigma_per / math.sqrt(n)
        assert abs(result["sigma_combined"] - expected) < 1e-20

    def test_time_estimate_positive(self):
        result = statistical_power_analysis(3e-5, 1e-3, 1000)
        assert result["time_estimate_hours_at_1ms_integration"] > 0

    def test_zero_n_raises(self):
        with pytest.raises(ValueError):
            statistical_power_analysis(1e-5, 1e-3, 0)

    def test_negative_sigma_raises(self):
        with pytest.raises(ValueError):
            statistical_power_analysis(1e-5, -1.0, 100)

    def test_returns_n_measurements_key(self):
        result = statistical_power_analysis(1e-5, 1e-3, 100)
        assert result["n_measurements"] == 100


# ---------------------------------------------------------------------------
# systematic_budget_allocation
# ---------------------------------------------------------------------------

class TestSystematicBudgetAllocation:
    def test_total_sigma_below_decision_grade(self):
        result = systematic_budget_allocation()
        assert result["total_sigma"] < SIGMA_A_DECISION_GRADE

    def test_budget_headroom_factor_above_1(self):
        result = systematic_budget_allocation()
        assert result["budget_headroom_factor"] > 1.0

    def test_budget_table_has_five_entries(self):
        result = systematic_budget_allocation()
        assert len(result["budget_table"]) == 5

    def test_fractions_sum_to_1(self):
        result = systematic_budget_allocation()
        total = sum(frac for _, frac, _ in result["budget_table"])
        assert abs(total - 1.0) < 1e-10

    def test_notes_key_present(self):
        result = systematic_budget_allocation()
        assert "notes" in result and len(result["notes"]) > 0


# ---------------------------------------------------------------------------
# jj_squid_platform_spec
# ---------------------------------------------------------------------------

class TestJjSquidPlatformSpec:
    def test_temperature_mk(self):
        spec = jj_squid_platform_spec()
        assert spec["temperature_mk"] == 20

    def test_topology_certification_method(self):
        spec = jj_squid_platform_spec()
        assert spec["topology_certification_method"] == "Andreev_reflection_spectroscopy"

    def test_blinding_protocol_present(self):
        spec = jj_squid_platform_spec()
        assert "blinding_protocol" in spec

    def test_winding_numbers_certified(self):
        spec = jj_squid_platform_spec()
        assert spec["winding_numbers_certified"] == (5, 7)

    def test_junction_critical_current(self):
        spec = jj_squid_platform_spec()
        assert spec["junction_critical_current_ua"] == 1.0


# ---------------------------------------------------------------------------
# topological_insulator_platform_spec
# ---------------------------------------------------------------------------

class TestTopologicalInsulatorPlatformSpec:
    def test_material_candidates_non_empty(self):
        spec = topological_insulator_platform_spec()
        assert len(spec["material_candidates"]) > 0

    def test_bi2se3_in_candidates(self):
        spec = topological_insulator_platform_spec()
        assert "Bi2Se3" in spec["material_candidates"]

    def test_transport_observable_present(self):
        spec = topological_insulator_platform_spec()
        assert "transport_observable" in spec

    def test_conjugate_protocol_present(self):
        spec = topological_insulator_platform_spec()
        assert "conjugate_protocol" in spec

    def test_operating_temperature(self):
        spec = topological_insulator_platform_spec()
        assert spec["operating_temperature_k"] == 4.0


# ---------------------------------------------------------------------------
# campaign_timeline_and_milestones
# ---------------------------------------------------------------------------

class TestCampaignTimelineAndMilestones:
    def test_phase_1_present(self):
        timeline = campaign_timeline_and_milestones()
        assert "Phase_1" in timeline

    def test_phase_2_present(self):
        timeline = campaign_timeline_and_milestones()
        assert "Phase_2" in timeline

    def test_phase_3_present(self):
        timeline = campaign_timeline_and_milestones()
        assert "Phase_3" in timeline

    def test_phase_4_present(self):
        timeline = campaign_timeline_and_milestones()
        assert "Phase_4" in timeline

    def test_falsification_possible_after_month_24(self):
        timeline = campaign_timeline_and_milestones()
        assert timeline["falsification_possible_after_month"] == 24

    def test_phase_1_has_deliverables(self):
        timeline = campaign_timeline_and_milestones()
        assert len(timeline["Phase_1"]["deliverables"]) > 0


# ---------------------------------------------------------------------------
# blinding_protocol_spec
# ---------------------------------------------------------------------------

class TestBlindingProtocolSpec:
    def test_pre_registration_required_is_true(self):
        spec = blinding_protocol_spec()
        assert spec["pre_registration_required"] is True

    def test_analysis_code_frozen(self):
        spec = blinding_protocol_spec()
        assert spec["analysis_code_frozen_before_unblinding"] is True

    def test_randomization_seed_custodian(self):
        spec = blinding_protocol_spec()
        assert spec["randomization_seed_custodian"] == "independent_statistician"

    def test_unblinding_condition_present(self):
        spec = blinding_protocol_spec()
        assert "unblinding_condition" in spec and len(spec["unblinding_condition"]) > 0
