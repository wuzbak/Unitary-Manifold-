# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 438 — Lattice Braid QFT Phase 1."""
from __future__ import annotations

import math
import pytest

from src.core.pillar438_lattice_braid_phase1 import (
    PILLAR_STATUS,
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    N_W,
    K_CS,
    C_S,
    BETA_BRAID,
    C1_NP_TARGET,
    GAMMA_GAP_FRACTION,
    GAMMA_THEORY,
    GAMMA_FIT,
    L_MAX_PHASE1,
    N_STATES,
    transfer_matrix,
    largest_eigenvalues,
    order_parameter,
    correlation_length,
    string_tension,
    gamma_c1_from_lattice,
    cmb_correction_fnl,
    finite_size_extrapolation,
    phase1_report,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'LATTICE_BRAID_PHASE1_COMPUTED'

    def test_adjacency_label(self):
        assert '🔵' in ADJACENCY_TRACK_LABEL
        assert 'ADJACENT TRACK' in ADJACENCY_TRACK_LABEL

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 438

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_c_s(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-12

    def test_beta_braid(self):
        expected = 74.0 / (4.0 * math.pi ** 2)
        assert abs(BETA_BRAID - expected) < 1e-10

    def test_beta_braid_approx(self):
        assert 1.8 < BETA_BRAID < 2.0

    def test_c1_np_target(self):
        assert C1_NP_TARGET == pytest.approx(3.4, rel=0.01)

    def test_gamma_values(self):
        assert GAMMA_THEORY < GAMMA_FIT

    def test_gamma_gap_fraction(self):
        assert abs(GAMMA_GAP_FRACTION - 0.27) < 0.01

    def test_l_max_phase1(self):
        assert L_MAX_PHASE1 == 12

    def test_n_states(self):
        assert N_STATES == 15


class TestTransferMatrix:
    def test_returns_square_matrix(self):
        T = transfer_matrix(1.0, n_states=5)
        assert len(T) == 5
        assert all(len(row) == 5 for row in T)

    def test_positive_entries(self):
        T = transfer_matrix(1.0, n_states=5)
        assert all(T[i][j] > 0 for i in range(5) for j in range(5))

    def test_symmetric(self):
        T = transfer_matrix(1.0, n_states=5)
        for i in range(5):
            for j in range(5):
                assert abs(T[i][j] - T[j][i]) < 1e-10

    def test_circulant(self):
        # T[i][j] depends only on (i-j) mod n
        T = transfer_matrix(1.0, n_states=5)
        for i in range(5):
            for j in range(5):
                k = (i - j) % 5
                assert abs(T[i][j] - T[k][0]) < 1e-10

    def test_diagonal_is_max(self):
        T = transfer_matrix(1.0, n_states=5)
        # T[0][0] = exp(beta * cos(0)) = exp(beta) is maximum
        max_val = max(T[0][j] for j in range(5))
        assert T[0][0] == pytest.approx(max_val)

    def test_larger_beta_larger_entries(self):
        T1 = transfer_matrix(1.0, n_states=5)
        T2 = transfer_matrix(2.0, n_states=5)
        assert T2[0][0] > T1[0][0]


class TestLargestEigenvalues:
    def test_returns_sorted_descending(self):
        T = transfer_matrix(1.0, n_states=7)
        eigs = largest_eigenvalues(T, n_eig=3)
        assert eigs[0] >= eigs[1] >= eigs[2]

    def test_positive_eigenvalues(self):
        T = transfer_matrix(1.0, n_states=7)
        eigs = largest_eigenvalues(T, n_eig=2)
        assert all(e > 0 for e in eigs)

    def test_largest_bigger_than_others(self):
        T = transfer_matrix(BETA_BRAID, n_states=N_STATES)
        eigs = largest_eigenvalues(T, n_eig=3)
        assert eigs[0] > eigs[1]


class TestOrderParameter:
    def test_positive(self):
        op = order_parameter(BETA_BRAID)
        assert op > 0.0

    def test_less_than_one(self):
        op = order_parameter(BETA_BRAID)
        assert op <= 1.0

    def test_larger_beta_larger_op(self):
        op1 = order_parameter(1.0)
        op2 = order_parameter(5.0)
        assert op2 > op1

    def test_small_beta_small_op(self):
        op = order_parameter(0.01)
        assert op < 0.5

    def test_large_beta_approaches_one(self):
        op = order_parameter(100.0)
        assert op > 0.9


class TestCorrelationLength:
    def test_positive_finite(self):
        xi = correlation_length(BETA_BRAID)
        assert 0 < xi < float('inf')

    def test_larger_beta_larger_xi(self):
        xi1 = correlation_length(1.0)
        xi2 = correlation_length(5.0)
        assert xi2 > xi1

    def test_very_large_beta_large_xi(self):
        xi = correlation_length(100.0)
        assert xi > 10.0


class TestStringTension:
    def test_positive(self):
        sigma = string_tension(BETA_BRAID)
        assert sigma >= 0.0

    def test_larger_beta_smaller_tension(self):
        # Higher coupling → more ordered → smaller string tension
        s1 = string_tension(1.0)
        s2 = string_tension(5.0)
        assert s2 < s1

    def test_inverse_of_correlation_length(self):
        # sigma ≈ 1/xi (for simple model)
        sigma = string_tension(BETA_BRAID)
        xi = correlation_length(BETA_BRAID)
        # They should satisfy sigma ≈ -log(op) and xi = -1/log(op) → sigma * xi = 1
        assert abs(sigma * xi - 1.0) < 0.01


class TestGammaC1FromLattice:
    def test_returns_dict(self):
        result = gamma_c1_from_lattice(BETA_BRAID)
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = gamma_c1_from_lattice(BETA_BRAID)
        for key in ['c1_lattice', 'c1_np_target', 'gamma_convergence', 'verdict']:
            assert key in result

    def test_c1_positive(self):
        result = gamma_c1_from_lattice(BETA_BRAID)
        assert result['c1_lattice'] >= 0.0

    def test_target_is_c1_np(self):
        result = gamma_c1_from_lattice(BETA_BRAID)
        assert result['c1_np_target'] == C1_NP_TARGET

    def test_verdict_is_string(self):
        result = gamma_c1_from_lattice(BETA_BRAID)
        assert result['verdict'] in ('CONVERGENT', 'INSUFFICIENT')


class TestCmbCorrectionFnl:
    def test_returns_dict(self):
        result = cmb_correction_fnl(BETA_BRAID)
        assert isinstance(result, dict)

    def test_delta_fnl_small(self):
        # CMB correction is suppressed by k_CMB/k_KK ~ 1e-5
        result = cmb_correction_fnl(BETA_BRAID, k_ratio=1e-5)
        assert abs(result['delta_fnl']) < 0.01

    def test_beta_braid_correct(self):
        result = cmb_correction_fnl(BETA_BRAID)
        assert result['beta_braid'] == BETA_BRAID

    def test_c_s_correct(self):
        result = cmb_correction_fnl()
        assert result['c_s'] == pytest.approx(C_S)


class TestFiniteSizeExtrapolation:
    def test_returns_dict(self):
        result = finite_size_extrapolation(BETA_BRAID)
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = finite_size_extrapolation(BETA_BRAID)
        for key in ['beta', 'l_values', 'op_values', 'op_extrapolated', 'verdict']:
            assert key in result

    def test_l_values_match_op_values(self):
        result = finite_size_extrapolation(BETA_BRAID)
        assert len(result['l_values']) == len(result['op_values'])

    def test_all_op_in_range(self):
        result = finite_size_extrapolation(BETA_BRAID)
        for op in result['op_values']:
            assert 0.0 <= op <= 1.0

    def test_verdict_valid(self):
        result = finite_size_extrapolation(BETA_BRAID)
        assert result['verdict'] in ('ORDERED', 'DISORDERED_OR_CRITICAL')


class TestPhase1Report:
    def setup_method(self):
        self.report = phase1_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_pillar_number(self):
        assert self.report['pillar'] == 438

    def test_status(self):
        assert self.report['status'] == 'LATTICE_BRAID_PHASE1_COMPUTED'

    def test_adjacency(self):
        assert '🔵' in self.report['adjacency']

    def test_observables_keys(self):
        obs = self.report['observables']
        for key in ['order_parameter', 'correlation_length', 'string_tension']:
            assert key in obs

    def test_order_parameter_positive(self):
        assert self.report['observables']['order_parameter'] > 0.0

    def test_c1_analysis(self):
        c1 = self.report['c1_analysis']
        assert 'c1_lattice' in c1

    def test_l2_status(self):
        l2 = self.report['l2_status']
        assert l2['c1_np_target'] == C1_NP_TARGET
        assert l2['gamma_gap_explained_total'] == pytest.approx(0.73)

    def test_beta_braid_stored(self):
        assert abs(self.report['beta_braid'] - BETA_BRAID) < 1e-10
