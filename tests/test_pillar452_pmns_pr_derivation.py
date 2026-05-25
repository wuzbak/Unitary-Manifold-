# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 452 — PMNS p_R Interval Constraint from 2-Loop KK Yukawa."""
import math
import pytest
from src.core.pillar452_pmns_pr_derivation import (
    PILLAR_STATUS, VERSION,
    P_R_FITTED_P383, P_R_GEOMETRIC_MIN, P_R_GEOMETRIC_MAX,
    P_R_CONSTRAINED_MIN, P_R_CONSTRAINED_MAX,
    DM31_PDG, DM31_UM_P17, DM31_NLO_UNC,
    DELTA_ELL_12, DELTA_ELL_23, FACTOR,
    geometric_bound_from_rs1, two_loop_tightening, constrained_p_r_interval,
    p_r_analytic, dm31_from_p_r, juno_implication, pillar_report,
)


class TestConstants:
    def test_p_r_fitted_p383(self):
        assert abs(P_R_FITTED_P383 - 0.364) < 1e-3

    def test_p_r_geometric_bounds(self):
        assert P_R_GEOMETRIC_MIN == 1e-5
        assert P_R_GEOMETRIC_MAX == 0.535

    def test_constrained_interval_inside_geometric(self):
        assert P_R_CONSTRAINED_MIN > P_R_GEOMETRIC_MIN
        assert P_R_CONSTRAINED_MAX < P_R_GEOMETRIC_MAX

    def test_fitted_in_constrained_interval(self):
        assert P_R_CONSTRAINED_MIN <= P_R_FITTED_P383 <= P_R_CONSTRAINED_MAX

    def test_dm31_pdg_order_of_magnitude(self):
        assert 2.4e-3 < DM31_PDG < 2.6e-3

    def test_factor_value(self):
        assert abs(FACTOR - 37.0) < 1e-10


class TestGeometricBound:
    def test_min_lt_max(self):
        r = geometric_bound_from_rs1()
        assert r['p_r_min'] < r['p_r_max']

    def test_warp_factor_small(self):
        r = geometric_bound_from_rs1()
        assert r['warp_factor'] < 1e-10

    def test_p383_bounds_preserved(self):
        r = geometric_bound_from_rs1()
        assert abs(r['p_r_min'] - P_R_GEOMETRIC_MIN) < 1e-10
        assert abs(r['p_r_max'] - P_R_GEOMETRIC_MAX) < 1e-10


class TestTwoLoopTightening:
    def test_interval_tightened(self):
        r = two_loop_tightening()
        p_r_width = r['p_r_constrained_max'] - r['p_r_constrained_min']
        geometric_width = P_R_GEOMETRIC_MAX - P_R_GEOMETRIC_MIN
        assert p_r_width < geometric_width

    def test_fitted_value_in_constrained_interval(self):
        r = two_loop_tightening()
        assert r['contains_fitted_value'] is True

    def test_delta_2loop_applied(self):
        r = two_loop_tightening()
        assert r['delta_2loop_max'] > 0
        assert r['delta_kt'] == pytest.approx(0.053, abs=0.001)

    def test_constrained_min_lt_constrained_max(self):
        r = two_loop_tightening()
        assert r['p_r_constrained_min'] < r['p_r_constrained_max']


class TestConstrainedInterval:
    def test_fitted_in_interval(self):
        r = constrained_p_r_interval()
        assert r['fitted_in_interval'] is True

    def test_not_uniquely_determined(self):
        r = constrained_p_r_interval()
        assert r['uniquely_determined'] is False

    def test_architecture_limit_named(self):
        r = constrained_p_r_interval()
        assert 'P271' in r['architecture_limit']

    def test_interval_ordering(self):
        r = constrained_p_r_interval()
        assert r['p_r_min'] < r['p_r_max']

    def test_central_in_interval(self):
        r = constrained_p_r_interval()
        assert r['p_r_min'] <= r['p_r_central'] <= r['p_r_max']


class TestPRAnalytic:
    def test_constrained_not_unique(self):
        r = p_r_analytic()
        assert r['uniquely_determined'] is False

    def test_interval_present(self):
        r = p_r_analytic()
        assert 'p_r_interval' in r
        lo, hi = r['p_r_interval']
        assert lo < hi

    def test_fitted_in_interval(self):
        r = p_r_analytic()
        lo, hi = r['p_r_interval']
        assert lo <= P_R_FITTED_P383 <= hi

    def test_architecture_limit_named(self):
        r = p_r_analytic()
        assert r['architecture_limit'] is not None

    def test_next_step_present(self):
        r = p_r_analytic()
        assert 'P271' in r['next_step']


class TestDm31Derivation:
    def test_dm31_positive(self):
        r = dm31_from_p_r()
        assert r['dm31_derived'] > 0

    def test_juno_testable(self):
        r = dm31_from_p_r()
        assert r['juno_testable'] is True

    def test_dm31_close_to_p17(self):
        r = dm31_from_p_r(P_R_FITTED_P383)
        # Should match P17 exactly when using fitted p_R
        assert abs(r['dm31_derived'] - DM31_UM_P17) < 1e-30

    def test_still_conditional(self):
        r = dm31_from_p_r()
        assert 'CONDITIONAL' in r['status']

    def test_not_no_free_parameters(self):
        r = dm31_from_p_r()
        assert r['no_free_parameters'] is False


class TestJunoImplication:
    def test_conditional_not_removed(self):
        r = juno_implication()
        assert r['conditional_removed'] is False

    def test_p_r_status_constrained(self):
        r = juno_implication()
        assert 'CONSTRAINED' in r['p_r_status']

    def test_juno_testable(self):
        r = juno_implication()
        assert r['juno_testable'] is True

    def test_dm31_unc_total_present(self):
        r = juno_implication()
        assert 'dm31_total_unc_ev2' in r
        assert r['dm31_total_unc_ev2'] > DM31_NLO_UNC

    def test_architecture_limit_named(self):
        r = juno_implication()
        assert 'P271' in r['architecture_limit']


class TestPillarReport:
    def test_pillar_number(self):
        r = pillar_report()
        assert r['pillar'] == 452

    def test_status(self):
        r = pillar_report()
        assert r['status'] == PILLAR_STATUS

    def test_architecture_limit_in_upgrades(self):
        r = pillar_report()
        assert 'architecture_limit' in r['label_upgrades']
