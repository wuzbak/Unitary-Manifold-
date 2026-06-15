# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 463 — α_GW SC2 final floor certificate."""
from __future__ import annotations

import math
import pytest

from src.core.pillar463_alpha_gw_sc2_final import (
    ALPHA_GW_CENTRAL,
    ALPHA_GW_HIGH,
    ALPHA_GW_LOW,
    EPSILON_UV,
    PILLAR_STATUS,
    VERSION,
    cmbs4_discriminability,
    current_interval,
    five_d_eft_certified_floor,
    five_d_eft_floor_analysis,
    next_order_narrowing_estimate,
    pillar_report,
    ten_d_uv_requirement,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'ALPHA_GW_SC2_5D_EFT_FLOOR_CERTIFIED'

    def test_version(self):
        assert VERSION == 'v14.0'

    def test_interval_order(self):
        assert ALPHA_GW_LOW < ALPHA_GW_HIGH

    def test_central_midpoint(self):
        assert ALPHA_GW_CENTRAL == pytest.approx((ALPHA_GW_LOW + ALPHA_GW_HIGH) / 2)

    def test_epsilon_uv(self):
        assert EPSILON_UV == pytest.approx(0.04)


class TestCurrentInterval:
    def setup_method(self):
        self.result = current_interval()

    def test_low_value(self):
        assert self.result['low'] == pytest.approx(4.31e-10)

    def test_high_value(self):
        assert self.result['high'] == pytest.approx(4.67e-10)

    def test_width_value(self):
        assert self.result['width'] == pytest.approx(0.36e-10)

    def test_central_value(self):
        assert self.result['central'] == pytest.approx(4.49e-10)

    def test_relative_width(self):
        assert self.result['relative_width'] == pytest.approx((4.67e-10 - 4.31e-10) / 4.49e-10)


class TestFloorAnalysis:
    def setup_method(self):
        self.result = five_d_eft_floor_analysis()

    def test_floor_relative_width(self):
        assert self.result['floor_relative_width'] == pytest.approx(0.04)

    def test_floor_absolute_width(self):
        assert self.result['floor_absolute_width'] == pytest.approx(ALPHA_GW_CENTRAL * 0.04)

    def test_current_above_floor(self):
        assert self.result['above_floor'] is True

    def test_reducible_width_positive(self):
        assert self.result['reducible_width_before_floor'] > 0

    def test_reducible_fraction_between_zero_and_one(self):
        assert 0 < self.result['reducible_fraction_before_floor'] < 1

    def test_best_interval_centered(self):
        best = self.result['best_leading_order_interval']
        assert 0.5 * (best['low'] + best['high']) == pytest.approx(ALPHA_GW_CENTRAL)

    def test_best_interval_width_matches_floor(self):
        best = self.result['best_leading_order_interval']
        assert best['width'] == pytest.approx(self.result['floor_absolute_width'])

    def test_conclusion_mentions_5d(self):
        assert '5D' in self.result['conclusion']


class TestNextOrderEstimate:
    def setup_method(self):
        self.result = next_order_narrowing_estimate()

    def test_target_relative_width(self):
        assert self.result['target_relative_width'] == pytest.approx(0.02)

    def test_target_absolute_width(self):
        assert self.result['target_absolute_width'] == pytest.approx(ALPHA_GW_CENTRAL * 0.02)

    def test_improvement_greater_than_one(self):
        assert self.result['improvement_vs_current'] > 1

    def test_fractional_reduction_positive(self):
        assert self.result['fractional_reduction_vs_current'] > 0

    def test_interval_ordered(self):
        interval = self.result['estimated_interval']
        assert interval['low'] < interval['high']

    def test_interval_center(self):
        interval = self.result['estimated_interval']
        assert interval['central'] == pytest.approx(ALPHA_GW_CENTRAL)

    def test_interpretation_mentions_two_percent(self):
        assert '2%' in self.result['interpretation']


class TestTenDUVRequirement:
    def setup_method(self):
        self.result = ten_d_uv_requirement()

    def test_mentions_c_uv(self):
        assert 'c_UV' in self.result['five_d_gap']

    def test_required_input_mentions_cy3(self):
        assert 'CY₃' in self.result['required_input']

    def test_bridge_equation_present(self):
        assert 'alpha_gw_observed' in self.result['bridge_equation']

    def test_required_interval_ordered(self):
        interval = self.result['required_c_uv_interval']
        assert interval['low'] < interval['high']

    def test_benchmark_status_string(self):
        assert isinstance(self.result['benchmark_10d_status'], str)


class TestCMBS4Discriminability:
    def setup_method(self):
        self.result = cmbs4_discriminability()

    def test_current_interval_not_discriminable(self):
        assert self.result['can_discriminate_current_interval'] is False

    def test_next_order_not_discriminable(self):
        assert self.result['can_discriminate_next_order_interval'] is False

    def test_sigma_ratio_positive(self):
        assert self.result['sigma_r_over_r'] > 0

    def test_reason_mentions_degeneracies(self):
        assert 'degeneracies' in self.result['reason']

    def test_next_order_width_smaller(self):
        assert self.result['next_order_alpha_gw_relative_width'] < self.result['current_alpha_gw_relative_width']


class TestFinalCertification:
    def setup_method(self):
        self.result = five_d_eft_certified_floor()

    def test_status_matches(self):
        assert self.result['status'] == PILLAR_STATUS

    def test_can_narrow_further(self):
        assert self.result['five_d_can_narrow_further'] is True

    def test_cannot_uniquely_close(self):
        assert self.result['five_d_can_uniquely_close_alpha_gw'] is False

    def test_statement_mentions_10d(self):
        assert '10D' in self.result['final_statement']

    def test_next_order_embedded(self):
        assert self.result['next_order_estimate']['target_relative_width'] == pytest.approx(0.02)


class TestPillarReport:
    def setup_method(self):
        self.report = pillar_report()

    def test_pillar_number(self):
        assert self.report['pillar'] == 463

    def test_status(self):
        assert self.report['status'] == PILLAR_STATUS

    def test_version(self):
        assert self.report['version'] == 'v14.0'

    def test_contains_current_interval(self):
        assert 'current_interval' in self.report

    def test_contains_floor_analysis(self):
        assert 'five_d_floor_analysis' in self.report

    def test_contains_next_order(self):
        assert 'next_order_narrowing' in self.report

    def test_contains_ten_d_requirement(self):
        assert 'ten_d_uv_requirement' in self.report

    def test_contains_cmbs4(self):
        assert 'cmbs4_discriminability' in self.report

    def test_contains_certification(self):
        assert 'certification' in self.report
