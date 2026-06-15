# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 415 — Fermion FN Charge Continuous Scan."""
import math
import pytest

from src.core.pillar415_fermion_fn_continuous import (
    PILLAR_STATUS,
    HIERARCHY_STATUS,
    N_W,
    K_CS,
    PI_KR,
    DELTA_C,
    SM_FERMION_TABLE,
    continuous_fn_scan,
    fn_naturalness_check,
    hierarchy_continuous_verdict,
)

SCAN = continuous_fn_scan()
SCAN_BY_NAME = {row['name']: row for row in SCAN}


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'HIERARCHY_FN_CONTINUOUS_CONSTRAINED'

    def test_hierarchy_status(self):
        assert HIERARCHY_STATUS == 'HIERARCHY_FN_CONTINUOUS_CONSTRAINED'

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert PI_KR == 37

    def test_delta_c(self):
        assert DELTA_C == pytest.approx(5.0 / 74.0)

    def test_table_length(self):
        assert len(SM_FERMION_TABLE) == 9

    @pytest.mark.parametrize('name', ['top', 'bottom', 'charm', 'strange', 'up', 'down', 'tau', 'muon', 'electron'])
    def test_expected_fermion_names_present(self, name):
        assert any(row['name'] == name for row in SM_FERMION_TABLE)


class TestContinuousFNScan:
    def test_returns_nine_rows(self):
        assert len(SCAN) == 9

    @pytest.mark.parametrize('name', ['top', 'bottom', 'charm', 'strange', 'up', 'down', 'tau', 'muon', 'electron'])
    def test_each_entry_present(self, name):
        assert name in SCAN_BY_NAME

    @pytest.mark.parametrize('name', ['top', 'bottom', 'charm', 'strange', 'up', 'down', 'tau', 'muon', 'electron'])
    def test_delta_in_unit_interval(self, name):
        delta = SCAN_BY_NAME[name]['fn_correction_delta']
        assert 0.0 <= delta < 1.0

    @pytest.mark.parametrize('name', ['top', 'bottom', 'charm', 'strange', 'up', 'down', 'tau', 'muon', 'electron'])
    def test_predicted_mass_matches_actual(self, name):
        row = SCAN_BY_NAME[name]
        assert row['predicted_mass_continuous_GeV'] == pytest.approx(row['actual_mass_GeV'], rel=1e-12, abs=1e-12)

    @pytest.mark.parametrize('name', ['top', 'bottom', 'charm', 'strange', 'up', 'down', 'tau', 'muon', 'electron'])
    def test_floor_index_is_integer(self, name):
        assert isinstance(SCAN_BY_NAME[name]['floor_index'], int)

    @pytest.mark.parametrize('name', ['top', 'bottom', 'charm', 'strange', 'up', 'down', 'tau', 'muon', 'electron'])
    def test_ell_required_nonnegative(self, name):
        assert SCAN_BY_NAME[name]['ell_m_required'] >= 0.0

    def test_up_fractional_part_matches_prompt(self):
        assert SCAN_BY_NAME['up']['fn_correction_delta'] == pytest.approx(0.255, abs=0.01)

    def test_electron_fractional_part_matches_prompt(self):
        assert SCAN_BY_NAME['electron']['fn_correction_delta'] == pytest.approx(0.548, abs=0.01)

    def test_top_has_zero_delta(self):
        assert SCAN_BY_NAME['top']['fn_correction_delta'] == pytest.approx(0.0)

    def test_electron_has_larger_required_index_than_top(self):
        assert SCAN_BY_NAME['electron']['ell_m_required'] > SCAN_BY_NAME['top']['ell_m_required']

    def test_up_and_electron_are_natural(self):
        assert SCAN_BY_NAME['up']['is_natural'] is True
        assert SCAN_BY_NAME['electron']['is_natural'] is True


class TestFNNaturalnessCheck:
    def test_all_natural(self):
        assert fn_naturalness_check()['all_natural'] is True

    def test_n_natural_is_nine(self):
        assert fn_naturalness_check()['n_natural'] == 9

    def test_max_delta_less_than_one(self):
        assert fn_naturalness_check()['max_delta_fn'] < 1.0

    def test_max_delta_less_than_point_six(self):
        assert fn_naturalness_check()['max_delta_fn'] < 0.6

    def test_mean_delta_positive(self):
        assert fn_naturalness_check()['mean_delta_fn'] > 0.0

    def test_results_length(self):
        assert len(fn_naturalness_check()['results']) == 9

    @pytest.mark.parametrize('name', ['top', 'bottom', 'charm', 'strange', 'up', 'down', 'tau', 'muon', 'electron'])
    def test_results_retain_name(self, name):
        names = {row['name'] for row in fn_naturalness_check()['results']}
        assert name in names


class TestHierarchyContinuousVerdict:
    def test_status(self):
        assert hierarchy_continuous_verdict()['status'] == 'HIERARCHY_FN_CONTINUOUS_CONSTRAINED'

    def test_previous_status(self):
        assert hierarchy_continuous_verdict()['previous_status'] == 'HIERARCHY_PARTIALLY_CONSTRAINED'

    def test_n_fermions(self):
        assert hierarchy_continuous_verdict()['n_fermions'] == 9

    def test_n_exactly_reproduced(self):
        assert hierarchy_continuous_verdict()['n_exactly_reproduced'] == 9

    def test_n_natural_fn(self):
        assert hierarchy_continuous_verdict()['n_natural_fn'] == 9

    def test_verdict_mentions_exactly(self):
        assert 'exactly' in hierarchy_continuous_verdict()['verdict'].lower()
