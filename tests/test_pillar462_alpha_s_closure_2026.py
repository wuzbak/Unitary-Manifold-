# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 462 — α_s PDG 2026 closure audit."""
import pytest

from src.core.pillar462_alpha_s_closure_2026 import (
    PILLAR_STATUS,
    VERSION,
    pdg_2026_alpha_s,
    um_prediction_alpha_s,
    tension_assessment,
    what_would_close_the_gap,
    alpha_s_closure_verdict,
    pillar_report,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'ALPHA_S_PDG2026_MARGIN_ZONE_CONFIRMED'

    def test_version(self):
        assert VERSION == 'v14.0'


class TestPDGValues:
    def test_central(self):
        assert pdg_2026_alpha_s()['central'] == pytest.approx(0.1180)

    def test_sigma(self):
        assert pdg_2026_alpha_s()['sigma'] == pytest.approx(0.0009)

    def test_two_sigma_low(self):
        assert pdg_2026_alpha_s()['two_sigma_low'] == pytest.approx(0.1162)

    def test_two_sigma_high(self):
        assert pdg_2026_alpha_s()['two_sigma_high'] == pytest.approx(0.1198)


class TestUMPrediction:
    def test_value(self):
        assert um_prediction_alpha_s()['value'] == pytest.approx(0.113)

    def test_source(self):
        assert um_prediction_alpha_s()['source'] == 'geometric KK chain'


class TestTension:
    def test_gap_to_central(self):
        assert tension_assessment()['gap_to_central'] == pytest.approx(0.0050)

    def test_gap_to_two_sigma_low(self):
        assert tension_assessment()['gap_to_two_sigma_low'] == pytest.approx(0.0032)

    def test_status(self):
        assert tension_assessment()['status'] == 'OUTSIDE_2SIGMA_LOW'

    def test_sigma_tension_from_central_large(self):
        assert tension_assessment()['sigma_tension_from_central'] > 5.0

    def test_sigma_tension_below_2sigma_low(self):
        assert tension_assessment()['sigma_tension_below_2sigma_low'] == pytest.approx(0.0032 / 0.0009)


class TestClosurePath:
    def test_mentions_three_loop(self):
        assert '3-loop KK threshold correction' in what_would_close_the_gap()['closure_path']

    def test_loop_order_required(self):
        assert what_would_close_the_gap()['loop_order_required'] == '3-loop'


class TestVerdict:
    def test_status(self):
        assert alpha_s_closure_verdict()['status'] == 'MARGIN_ZONE_CONFIRMED'

    def test_not_closed(self):
        assert alpha_s_closure_verdict()['closed'] is False

    def test_gap(self):
        assert alpha_s_closure_verdict()['gap'] == pytest.approx(0.0032)

    def test_fractional_gap_pct(self):
        assert alpha_s_closure_verdict()['fractional_gap_from_central_pct'] == pytest.approx((0.005 / 0.1180) * 100.0)

    def test_sigma_gap_below_2sigma_window(self):
        assert alpha_s_closure_verdict()['sigma_gap_below_2sigma_window'] == pytest.approx(0.0032 / 0.0009)


class TestAdditionalConsistency:
    def test_fractional_gap_positive(self):
        assert tension_assessment()['fractional_gap_to_central'] > 0

    def test_fractional_gap_below_ten_percent(self):
        assert tension_assessment()['fractional_gap_to_central'] < 0.1

    def test_pdg_window_contains_central(self):
        pdg = pdg_2026_alpha_s()
        assert pdg['two_sigma_low'] < pdg['central'] < pdg['two_sigma_high']

    def test_um_below_two_sigma_low(self):
        assert um_prediction_alpha_s()['value'] < pdg_2026_alpha_s()['two_sigma_low']

    def test_verdict_uses_pillar_status(self):
        assert alpha_s_closure_verdict()['pillar_status'] == PILLAR_STATUS

    def test_verdict_um_value_matches_function(self):
        assert alpha_s_closure_verdict()['um_value'] == um_prediction_alpha_s()['value']

    def test_verdict_pdg_value_matches_function(self):
        assert alpha_s_closure_verdict()['pdg_central'] == pdg_2026_alpha_s()['central']

    def test_report_version(self):
        assert pillar_report()['version'] == VERSION

    def test_report_pdg_matches_function(self):
        assert pillar_report()['pdg'] == pdg_2026_alpha_s()

    def test_report_prediction_matches_function(self):
        assert pillar_report()['um_prediction'] == um_prediction_alpha_s()

    def test_report_tension_matches_function(self):
        assert pillar_report()['tension'] == tension_assessment()

    def test_report_verdict_matches_function(self):
        assert pillar_report()['verdict'] == alpha_s_closure_verdict()


class TestPillarReport:
    def test_pillar_number(self):
        assert pillar_report()['pillar'] == 462

    def test_status(self):
        assert pillar_report()['status'] == PILLAR_STATUS

    def test_sections_present(self):
        report = pillar_report()
        for key in ['pdg', 'um_prediction', 'tension', 'closure_path', 'verdict']:
            assert key in report
