# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 455 — P8 field-theoretic proof attempt."""
import math
import pytest

from src.core.pillar455_p8_field_theoretic_proof import (
    PILLAR_STATUS,
    VERSION,
    N_W,
    N_2,
    z2_odd_constraint,
    anomaly_cancellation_constraint,
    dirichlet_bc_quantization,
    second_variation_positivity,
    path_integral_dominance,
    all_five_constraints,
    prove_minimum_step_uniqueness,
    named_residual_statement,
    pillar_report,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'P8_PROVED_OVER_INTEGER_LATTICE__NAMED_RESIDUAL_FULL_FUNCTION_SPACE'

    def test_version(self):
        assert VERSION == 'v14.0'

    def test_canonical_pair(self):
        assert N_W == 5
        assert N_2 == 7


class TestZ2Constraint:
    @pytest.mark.parametrize('n_w', [1, 3, 5, 7, 9])
    def test_odd_values_pass(self, n_w):
        assert z2_odd_constraint(n_w)['passes'] is True

    @pytest.mark.parametrize('n_w', [0, 2, 4, 6, 8])
    def test_even_values_fail(self, n_w):
        assert z2_odd_constraint(n_w)['passes'] is False

    def test_constraint_name(self):
        assert z2_odd_constraint(5)['constraint'] == 'Z2_ODD_PARITY'

    def test_source_pillar(self):
        assert z2_odd_constraint(5)['source_pillar'] == 39


class TestAnomalyConstraint:
    @pytest.mark.parametrize('n_w', [5, 7])
    def test_survivors_pass(self, n_w):
        assert anomaly_cancellation_constraint(n_w)['passes'] is True

    @pytest.mark.parametrize('n_w', [1, 3, 9, 11])
    def test_non_survivors_fail(self, n_w):
        assert anomaly_cancellation_constraint(n_w)['passes'] is False

    def test_survivor_set(self):
        assert anomaly_cancellation_constraint(5)['survivors'] == [5, 7]


class TestDirichletQuantization:
    @pytest.mark.parametrize(
        'n_w,n2',
        [(5, 7), (5, 9), (7, 9), (7, 11), (3, 5), (9, 11)],
    )
    def test_positive_even_step_passes(self, n_w, n2):
        assert dirichlet_bc_quantization(n_w, n2)['passes'] is True

    @pytest.mark.parametrize(
        'n_w,n2',
        [(5, 6), (5, 5), (5, 4), (7, 8), (7, 7), (7, 6)],
    )
    def test_non_even_or_non_positive_fails(self, n_w, n2):
        assert dirichlet_bc_quantization(n_w, n2)['passes'] is False

    def test_delta_n_value(self):
        assert dirichlet_bc_quantization(5, 7)['delta_n'] == 2


class TestSecondVariation:
    @pytest.mark.parametrize('n_w,n2', [(5, 7), (5, 9), (7, 9), (7, 11), (1, 3), (3, 5)])
    def test_positive_gap_gives_positive_hessian(self, n_w, n2):
        r = second_variation_positivity(n_w, n2)
        assert r['passes'] is True
        assert r['k_eff'] > 0
        assert r['delta2_s_e'] > 0

    @pytest.mark.parametrize('n_w,n2', [(5, 5), (5, 3), (7, 7), (7, 5), (3, 3)])
    def test_zero_or_negative_gap_fails(self, n_w, n2):
        r = second_variation_positivity(n_w, n2)
        assert r['passes'] is False


class TestPathIntegralDominance:
    @pytest.mark.parametrize('n_w', [5, 7])
    def test_minimizing_n2_is_nw_plus_2(self, n_w):
        r = path_integral_dominance(n_w, n_w + 2)
        assert r['minimizing_n2'] == n_w + 2
        assert r['passes'] is True

    @pytest.mark.parametrize('n_w,n2', [(5, 9), (5, 11), (7, 11), (7, 13)])
    def test_larger_step_has_larger_action(self, n_w, n2):
        r = path_integral_dominance(n_w, n2)
        assert r['passes'] is False
        assert r['candidate_actions'][n2] > r['candidate_actions'][n_w + 2]

    def test_action_formula_matches_manual(self):
        r = path_integral_dominance(5, 7)
        expected = (5**2 + 7**2) * math.pi**2
        assert r['action'] == pytest.approx(expected)


class TestAllFiveConstraints:
    @pytest.mark.parametrize('n_w,n2', [(5, 7), (7, 9)])
    def test_local_minimum_step_pairs_satisfy_all(self, n_w, n2):
        assert all_five_constraints(n_w, n2)['all_satisfied'] is True

    @pytest.mark.parametrize('n_w,n2', [(5, 9), (5, 11), (7, 11), (3, 5), (9, 11), (5, 6), (5, 5)])
    def test_noncanonical_pairs_fail_some_constraint(self, n_w, n2):
        assert all_five_constraints(n_w, n2)['all_satisfied'] is False

    def test_canonical_pair_delta_two(self):
        assert all_five_constraints(5, 7)['delta_n'] == 2


class TestProofOfUniqueness:
    def test_integer_lattice_proved(self):
        assert prove_minimum_step_uniqueness()['integer_lattice_proved'] is True

    def test_all_local_pairs_have_delta_two(self):
        assert prove_minimum_step_uniqueness()['all_local_pairs_have_delta_n_2'] is True

    def test_local_pairs_are_two(self):
        assert prove_minimum_step_uniqueness()['local_minimum_step_pairs'] == [{'n_w': 5, 'n2': 7}, {'n_w': 7, 'n2': 9}]

    def test_unique_global_pair_is_5_7(self):
        assert prove_minimum_step_uniqueness()['unique_global_pair'] == {'n_w': 5, 'n2': 7}

    def test_global_action_minimum_positive(self):
        assert prove_minimum_step_uniqueness()['global_action_minimum'] > 0

    def test_verdict_name(self):
        assert prove_minimum_step_uniqueness()['verdict'] == 'INTEGER_LATTICE_PROOF_COMPLETE'

    def test_scan_has_many_pairs(self):
        assert len(prove_minimum_step_uniqueness()['scanned_pairs']) > 50


class TestNamedResidual:
    def test_status_named_residual(self):
        assert named_residual_statement()['status'] == 'NAMED_RESIDUAL'

    def test_scope_mentions_function_space(self):
        assert 'functional space' in named_residual_statement()['unproved_scope']

    def test_statement_mentions_nonperturbative_qft(self):
        assert 'non-perturbative QFT' in named_residual_statement()['residual_statement']

    def test_name_present(self):
        assert named_residual_statement()['name'] == 'FULL_FUNCTION_SPACE_NONPERTURBATIVE_QFT_OBSTRUCTION'


class TestPillarReport:
    def test_pillar_number(self):
        assert pillar_report()['pillar'] == 455

    def test_status(self):
        assert pillar_report()['status'] == PILLAR_STATUS

    def test_summary_mentions_5_7(self):
        assert '(5, 7)' in pillar_report()['summary']

    def test_report_contains_residual(self):
        assert 'named_residual' in pillar_report()
