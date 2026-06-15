# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 468 — LiteBIRD discrimination protocol."""
from __future__ import annotations

import math
import pytest

from src.core.pillar468_litebird_discrimination_protocol import (
    PILLAR_STATUS,
    VERSION,
    fnl_discriminator,
    gap_discriminability,
    hllhc_discriminator,
    litebird_decision_tree,
    multi_instrument_verdict_protocol,
    pillar_report,
    roman_discriminability,
    sector_predictions,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'LITEBIRD_DISCRIMINATION_PROTOCOL_FORMALIZED'

    def test_version(self):
        assert VERSION == 'v14.0'


class TestSectorPredictions:
    def setup_method(self):
        self.preds = sector_predictions()

    def test_two_sectors_present(self):
        assert set(self.preds.keys()) == {'sector_57', 'sector_56'}

    def test_sector_57_beta(self):
        assert self.preds['sector_57']['beta_deg'] == pytest.approx(0.331)

    def test_sector_56_beta(self):
        assert self.preds['sector_56']['beta_deg'] == pytest.approx(0.273)

    def test_sector_57_kcs(self):
        assert self.preds['sector_57']['k_cs'] == 74

    def test_sector_56_kcs(self):
        assert self.preds['sector_56']['k_cs'] == 61

    def test_sector_56_cs(self):
        assert self.preds['sector_56']['c_s'] == pytest.approx(11 / 61)

    def test_sector_56_fnl_formula(self):
        expected = (35 / 108) * (1 / ((11 / 61) ** 2) - 1)
        assert self.preds['sector_56']['f_nl_equil'] == pytest.approx(expected)

    def test_sector_57_mass_larger(self):
        assert self.preds['sector_57']['m_kk_gev'] > self.preds['sector_56']['m_kk_gev']


class TestDecisionTree:
    def test_gap_falsifies(self):
        assert litebird_decision_tree(0.300, 0.02)['verdict'] == 'FALSIFIED'

    def test_sector_57_selected(self):
        result = litebird_decision_tree(0.331, 0.02)
        assert result['verdict'] == 'SECTOR_57_SELECTED'
        assert result['selected_sector'] == 'sector_57'

    def test_sector_56_selected(self):
        result = litebird_decision_tree(0.273, 0.02)
        assert result['verdict'] == 'SECTOR_56_SELECTED'
        assert result['selected_sector'] == 'sector_56'

    def test_outside_window_falsifies(self):
        assert litebird_decision_tree(0.40, 0.02)['verdict'] == 'FALSIFIED_OUTSIDE_WINDOW'

    def test_negative_error_rejected(self):
        with pytest.raises(ValueError):
            litebird_decision_tree(0.331, 0)

    def test_distance_sigma_zero_at_prediction(self):
        assert litebird_decision_tree(0.331, 0.02)['distance_to_57_sigma'] == pytest.approx(0.0)

    def test_gap_hit_flag(self):
        assert litebird_decision_tree(0.30, 0.02)['gap_hit'] is True

    def test_non_gap_hit_flag(self):
        assert litebird_decision_tree(0.331, 0.02)['gap_hit'] is False


class TestAuxiliaryDiscriminators:
    def test_fnl_difference_large(self):
        assert fnl_discriminator()['delta_f_nl'] > 6

    def test_fnl_threshold_one(self):
        assert fnl_discriminator()['discriminating_if_sigma_below'] == pytest.approx(1.0)

    def test_hllhc_discriminates(self):
        assert hllhc_discriminator()['discriminates'] is True

    def test_hllhc_relative_gap_positive(self):
        assert hllhc_discriminator()['relative_gap'] > 0

    def test_roman_not_discriminating(self):
        assert roman_discriminability()['discriminates'] is False

    def test_roman_same_w0(self):
        assert roman_discriminability()['shared_prediction']['w0'] == -1.0

    def test_gap_size(self):
        assert gap_discriminability()['gap_size_deg'] == pytest.approx(0.058)

    def test_gap_sigma(self):
        assert gap_discriminability()['gap_significance_sigma'] == pytest.approx(2.9)

    def test_gap_target_mentions_falsifies(self):
        assert 'falsifies' in gap_discriminability()['falsification_target']


class TestProtocolAndReport:
    def test_protocol_has_pre_litebird(self):
        assert 'pre_litebird' in multi_instrument_verdict_protocol()

    def test_protocol_has_litebird(self):
        assert 'litebird' in multi_instrument_verdict_protocol()

    def test_protocol_has_gap(self):
        assert 'gap' in multi_instrument_verdict_protocol()

    def test_report_pillar_number(self):
        assert pillar_report()['pillar'] == 468

    def test_report_status(self):
        assert pillar_report()['status'] == PILLAR_STATUS

    def test_report_contains_sector_predictions(self):
        assert 'sector_predictions' in pillar_report()

    def test_report_contains_protocol(self):
        assert 'protocol' in pillar_report()
