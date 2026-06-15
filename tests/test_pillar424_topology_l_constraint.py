# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 424 — Quadrupole Topology L Constraint from Inflation."""
import math
import pytest

from src.core.pillar424_topology_l_constraint import (
    PILLAR_STATUS,
    R_TENSOR_TO_SCALAR,
    A_S,
    H_0_GEV,
    T_RH_GEV,
    T_CMB_GEV,
    D_H_GPC,
    L_WINDOW_MIN_GPC,
    L_WINDOW_MAX_GPC,
    L_PLANCK_LOWER_GPC,
    compute_h_inf,
    compute_l_inf_comoving,
    topology_window_analysis,
    topology_l_constraint_verdict,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'TOPOLOGY_L_INFLATION_ARCHITECTURE_LIMIT'

    def test_r_reasonable(self):
        assert 0.02 < R_TENSOR_TO_SCALAR < 0.05

    def test_a_s_order_of_magnitude(self):
        assert 1e-10 < A_S < 1e-8

    def test_d_h_reasonable(self):
        assert 13.0 < D_H_GPC < 16.0

    def test_window_min_less_than_max(self):
        assert L_WINDOW_MIN_GPC < L_WINDOW_MAX_GPC

    def test_planck_lower_above_window_max(self):
        # The Planck lower bound is above the P410 required window
        assert L_PLANCK_LOWER_GPC > L_WINDOW_MAX_GPC


class TestComputeHInf:
    def test_returns_positive(self):
        assert compute_h_inf() > 0.0

    def test_order_of_magnitude(self):
        # H_inf ~ 10^14 GeV for r~0.03
        h = compute_h_inf()
        assert 1e13 < h < 1e16

    def test_increases_with_r(self):
        h1 = compute_h_inf(r=0.03)
        h2 = compute_h_inf(r=0.06)
        assert h2 > h1

    def test_increases_with_a_s(self):
        h1 = compute_h_inf(a_s=1e-9)
        h2 = compute_h_inf(a_s=4e-9)
        assert h2 > h1


class TestComputeLInfComoving:
    def test_returns_dict(self):
        assert isinstance(compute_l_inf_comoving(), dict)

    @pytest.mark.parametrize('key', ['h_inf_gev', 'h0_over_hinf', 'trh_over_tcmb',
                                     'l_over_dh', 'l_gpc', 'log10_l_over_dh'])
    def test_expected_keys(self, key):
        assert key in compute_l_inf_comoving()

    def test_l_over_dh_tiny(self):
        # L_inf / D_H should be many orders of magnitude smaller than 1
        data = compute_l_inf_comoving()
        assert data['l_over_dh'] < 1e-20

    def test_log10_l_over_dh_very_negative(self):
        data = compute_l_inf_comoving()
        assert data['log10_l_over_dh'] < -20

    def test_l_gpc_much_smaller_than_window(self):
        data = compute_l_inf_comoving()
        assert data['l_gpc'] < L_WINDOW_MIN_GPC * 1e-20


class TestTopologyWindowAnalysis:
    def test_returns_dict(self):
        assert isinstance(topology_window_analysis(), dict)

    @pytest.mark.parametrize('key', ['l_inf_comoving_gpc', 'l_window_min_gpc',
                                     'l_window_max_gpc', 'l_planck_lower_gpc',
                                     'in_p410_window', 'above_planck_lower_bound',
                                     'inflation_can_set_topology_scale',
                                     'orders_of_magnitude_short'])
    def test_expected_keys(self, key):
        assert key in topology_window_analysis()

    def test_not_in_p410_window(self):
        assert topology_window_analysis()['in_p410_window'] is False

    def test_not_above_planck_bound(self):
        assert topology_window_analysis()['above_planck_lower_bound'] is False

    def test_inflation_cannot_set_scale(self):
        assert topology_window_analysis()['inflation_can_set_topology_scale'] is False

    def test_many_orders_short(self):
        assert topology_window_analysis()['orders_of_magnitude_short'] > 20

    def test_p410_window_conflicts_with_planck(self):
        # P410 window max (11.4 Gpc) < Planck lower bound (13.9 Gpc)
        assert topology_window_analysis()['p410_window_planck_compatible'] is False


class TestTopologyLConstraintVerdict:
    def test_returns_dict(self):
        assert isinstance(topology_l_constraint_verdict(), dict)

    def test_status(self):
        assert topology_l_constraint_verdict()['status'] == 'TOPOLOGY_L_INFLATION_ARCHITECTURE_LIMIT'

    @pytest.mark.parametrize('key', ['l_inf_comoving', 'window_analysis', 'blockers', 'verdict'])
    def test_expected_keys(self, key):
        assert key in topology_l_constraint_verdict()

    def test_has_blockers(self):
        verdict = topology_l_constraint_verdict()
        assert len(verdict['blockers']) >= 3

    def test_verdict_is_string(self):
        assert isinstance(topology_l_constraint_verdict()['verdict'], str)

    def test_verdict_mentions_architecture_limit(self):
        verdict = topology_l_constraint_verdict()['verdict']
        assert 'ARCHITECTURE_LIMIT' in verdict
