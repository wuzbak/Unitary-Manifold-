# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 416 — c_L^phys Topological Form Search."""
import math
import pytest

from src.core.pillar416_cl_phys_topological import (
    PILLAR_STATUS,
    CL_PHYS_VALUE,
    CL_R_VALUE,
    N_W,
    K_CS,
    rational_search,
    um_expression_search,
    geometry_bounds,
    cl_phys_verdict,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'BOUNDED_FROM_GEOMETRY'

    def test_cl_phys_value(self):
        assert CL_PHYS_VALUE == pytest.approx(0.961)

    def test_cl_r_value(self):
        assert CL_R_VALUE == pytest.approx(23.0 / 25.0)

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74


class TestRationalSearch:
    @pytest.mark.parametrize('key', ['target', 'tolerance', 'best_rational', 'best_global_rational', 'all_close_rationals'])
    def test_expected_keys_present(self, key):
        assert key in rational_search()

    def test_best_rational_is_close(self):
        best = rational_search()['best_rational']
        assert abs(best['value'] - CL_PHYS_VALUE) / CL_PHYS_VALUE < 0.01

    def test_best_rational_error_pct_below_half_percent(self):
        assert rational_search()['best_rational']['error_pct'] < 0.5

    def test_best_rational_is_71_over_74(self):
        best = rational_search()['best_rational']
        assert best['numerator'] == 71
        assert best['denominator'] == 74

    def test_best_global_rational_even_better(self):
        data = rational_search()
        assert data['best_global_rational']['error_pct'] <= data['best_rational']['error_pct']

    def test_all_close_is_list(self):
        assert isinstance(rational_search()['all_close_rationals'], list)

    @pytest.mark.parametrize('target', [0.961, 0.95, 0.97, 0.75, 0.66, 1.02, 0.88, 0.51, 1.07])
    def test_positive_targets_return_dict(self, target):
        assert isinstance(rational_search(target=target), dict)

    def test_invalid_target_raises(self):
        with pytest.raises(ValueError):
            rational_search(target=0.0)

    def test_invalid_tolerance_raises(self):
        with pytest.raises(ValueError):
            rational_search(tolerance=0.0)


class TestUMExpressionSearch:
    def test_returns_dict(self):
        assert isinstance(um_expression_search(), dict)

    def test_contains_expressions(self):
        assert len(um_expression_search()['expressions']) >= 5

    def test_best_match_has_error_field(self):
        assert 'error_pct' in um_expression_search()['best_match']

    @pytest.mark.parametrize('label', ['71/74', '(K_CS-n_w)/K_CS', '1-n_w/K_CS'])
    def test_named_expressions_present(self, label):
        labels = {item['label'] for item in um_expression_search()['expressions']}
        assert label in labels

    def test_best_match_error_below_one_percent(self):
        assert um_expression_search()['best_match']['error_pct'] < 1.0


class TestGeometryBounds:
    def test_lower_bound(self):
        assert geometry_bounds()['lower_bound'] == pytest.approx(0.5)

    def test_upper_bound(self):
        assert geometry_bounds()['upper_bound'] == pytest.approx(2.0 - CL_R_VALUE)

    def test_value_in_bounds(self):
        assert geometry_bounds()['value_in_bounds'] is True

    def test_value_between_bounds(self):
        bounds = geometry_bounds()
        assert bounds['lower_bound'] < CL_PHYS_VALUE < bounds['upper_bound']


class TestCLPhysVerdict:
    @pytest.mark.parametrize('key', ['status', 'cl_phys_value', 'cl_r_value', 'best_rational_approximation', 'best_global_rational', 'um_expressions_tested', 'in_bounds', 'verdict'])
    def test_expected_keys_present(self, key):
        assert key in cl_phys_verdict()

    def test_status(self):
        assert cl_phys_verdict()['status'] == 'BOUNDED_FROM_GEOMETRY'

    def test_in_bounds_true(self):
        assert cl_phys_verdict()['in_bounds'] is True

    def test_um_expressions_tested_positive(self):
        assert cl_phys_verdict()['um_expressions_tested'] >= 5

    def test_verdict_mentions_no_exact(self):
        assert 'No exact' in cl_phys_verdict()['verdict']
