# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 431 — Lattice Braid QFT Formal Scope."""
from __future__ import annotations

import math
import pytest

from src.core.pillar431_lattice_braid_qft_scope import (
    PILLAR_STATUS,
    ADJACENCY_TRACK_LABEL,
    N_W,
    K_CS,
    C_S,
    PHI_STAR,
    C1_NP_ESTIMATE,
    GAMMA_GAP_FRACTION,
    lattice_action_parameters,
    degrees_of_freedom_estimate,
    algorithm_comparison,
    cost_estimate,
    cmb_observable_spec,
    lattice_braid_scope_report,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'LATTICE_BRAID_QFT_FORMALLY_SCOPED'

    def test_adjacency_track_label(self):
        assert '🔵' in ADJACENCY_TRACK_LABEL
        assert 'ADJACENT TRACK' in ADJACENCY_TRACK_LABEL

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_c_s(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-12

    def test_phi_star(self):
        assert abs(PHI_STAR - 2.0 * math.pi * N_W) < 1e-10

    def test_c1_np_estimate(self):
        assert C1_NP_ESTIMATE == pytest.approx(3.4, rel=0.01)

    def test_gamma_gap_fraction(self):
        assert abs(GAMMA_GAP_FRACTION - 0.27) < 0.01


class TestLatticeActionParameters:
    def setup_method(self):
        self.params = lattice_action_parameters()

    def test_returns_dict(self):
        assert isinstance(self.params, dict)

    def test_required_keys(self):
        for key in ['beta_braid', 'kappa_braid', 'm2_braid', 'lambda_braid',
                    'braid_bc', 'gauge_group', 'scalar_rep']:
            assert key in self.params

    def test_beta_braid_value(self):
        expected = K_CS / (4.0 * math.pi ** 2)
        assert self.params['beta_braid'] == pytest.approx(expected, rel=1e-10)

    def test_kappa_braid_value(self):
        expected = C_S / (2.0 * N_W)
        assert self.params['kappa_braid'] == pytest.approx(expected, rel=1e-10)

    def test_m2_braid_large_positive(self):
        assert self.params['m2_braid'] > 100.0  # large mass in Planck units

    def test_lambda_braid_value(self):
        expected = 1.0 / K_CS
        assert self.params['lambda_braid'] == pytest.approx(expected, rel=1e-10)

    def test_gauge_group_su2(self):
        assert self.params['gauge_group'] == 'SU(2)'

    def test_scalar_rep(self):
        assert 'adjoint' in self.params['scalar_rep']

    def test_braid_bc_contains_n_w_k_cs(self):
        bc = self.params['braid_bc']
        assert str(N_W) in bc and str(K_CS) in bc


class TestDegreesOfFreedom:
    def test_default_dof(self):
        dof = degrees_of_freedom_estimate()
        assert isinstance(dof, dict)

    def test_required_keys(self):
        dof = degrees_of_freedom_estimate()
        for key in ['N_s', 'N_y', 'n_sites', 'dof_per_config', 'physical_scale_MKK']:
            assert key in dof

    def test_n_sites_formula(self):
        dof = degrees_of_freedom_estimate(N_s=32, N_y=16)
        assert dof['n_sites'] == 32**3 * 16

    def test_dof_per_config_positive(self):
        dof = degrees_of_freedom_estimate()
        assert dof['dof_per_config'] > 0

    def test_custom_lattice_size(self):
        dof = degrees_of_freedom_estimate(N_s=16, N_y=8)
        assert dof['N_s'] == 16
        assert dof['N_y'] == 8
        assert dof['n_sites'] == 16**3 * 8


class TestAlgorithmComparison:
    def setup_method(self):
        self.algos = algorithm_comparison()

    def test_returns_list(self):
        assert isinstance(self.algos, list)

    def test_two_algorithms(self):
        assert len(self.algos) == 2

    def test_hmc_present(self):
        names = [a['algorithm'] for a in self.algos]
        assert any('HMC' in n for n in names)

    def test_tensor_network_present(self):
        names = [a['algorithm'] for a in self.algos]
        assert any('Tensor' in n for n in names)

    def test_each_has_required_keys(self):
        for algo in self.algos:
            assert 'algorithm' in algo
            assert 'advantages' in algo
            assert 'disadvantages' in algo
            assert 'recommendation' in algo

    def test_hmc_is_3d_plus_extra_dim(self):
        hmc = next(a for a in self.algos if 'HMC' in a['algorithm'])
        assert '3+1' in hmc['dimensions']

    def test_tn_is_1d(self):
        tn = next(a for a in self.algos if 'Tensor' in a['algorithm'])
        assert '1+1D' in tn['dimensions']

    def test_hmc_gpu_hours_estimate(self):
        hmc = next(a for a in self.algos if 'HMC' in a['algorithm'])
        assert hmc['gpu_hours_A100'] >= 100


class TestCostEstimate:
    def setup_method(self):
        self.cost = cost_estimate()

    def test_returns_dict(self):
        assert isinstance(self.cost, dict)

    def test_required_keys(self):
        for key in ['phase_1_tensor_network', 'phase_2_hmc', 'total_compute_estimate']:
            assert key in self.cost

    def test_phase_1_has_output(self):
        assert 'output' in self.cost['phase_1_tensor_network']

    def test_phase_2_has_output(self):
        assert 'output' in self.cost['phase_2_hmc']

    def test_phase_2_lattice_size(self):
        assert '32³' in self.cost['phase_2_hmc']['lattice_size'] or \
               '32^3' in self.cost['phase_2_hmc']['lattice_size']

    def test_total_compute_mention_gpu(self):
        assert 'GPU' in self.cost['total_compute_estimate'] or \
               'gpu' in self.cost['total_compute_estimate']


class TestCmbObservableSpec:
    def setup_method(self):
        self.obs = cmb_observable_spec()

    def test_returns_dict(self):
        assert isinstance(self.obs, dict)

    def test_required_keys(self):
        for key in ['c1_np_estimate', 'gamma_gap_fraction', 'cmbs4_sensitivity',
                    'litebird_sensitivity', 'discriminating_observable',
                    'resolution_criteria']:
            assert key in self.obs

    def test_c1_np_matches_constant(self):
        assert self.obs['c1_np_estimate'] == pytest.approx(C1_NP_ESTIMATE, rel=1e-8)

    def test_gamma_gap_matches_constant(self):
        assert self.obs['gamma_gap_fraction'] == pytest.approx(GAMMA_GAP_FRACTION, rel=0.01)

    def test_cmbs4_sensitivity_positive(self):
        assert self.obs['cmbs4_sensitivity'] > 0.0

    def test_litebird_sensitivity_smaller_than_cmbs4(self):
        assert self.obs['litebird_sensitivity'] <= self.obs['cmbs4_sensitivity']

    def test_four_resolution_criteria(self):
        assert len(self.obs['resolution_criteria']) == 4

    def test_discriminating_observable_string(self):
        assert len(self.obs['discriminating_observable']) > 0


class TestLatticeBraidScopeReport:
    def setup_method(self):
        self.report = lattice_braid_scope_report()

    def test_pillar_number(self):
        assert self.report['pillar'] == 431

    def test_status(self):
        assert self.report['status'] == 'LATTICE_BRAID_QFT_FORMALLY_SCOPED'

    def test_adjacency_present(self):
        assert '🔵' in self.report['adjacency']

    def test_parent_pillar(self):
        assert self.report['parent_pillar'] == 421

    def test_parent_status(self):
        assert self.report['parent_status'] == 'L2_GAMMA_BUDGET_CERTIFIED'

    def test_c1_np_estimate(self):
        assert self.report['c1_np_estimate'] == pytest.approx(C1_NP_ESTIMATE, rel=1e-8)

    def test_gamma_gap_fraction(self):
        assert abs(self.report['gamma_gap_fraction'] - GAMMA_GAP_FRACTION) < 0.01

    def test_lattice_action_present(self):
        assert 'lattice_action' in self.report
        assert 'beta_braid' in self.report['lattice_action']

    def test_dof_present(self):
        assert 'degrees_of_freedom' in self.report

    def test_algorithm_comparison_present(self):
        assert 'algorithm_comparison' in self.report
        assert len(self.report['algorithm_comparison']) == 2

    def test_cost_estimate_present(self):
        assert 'cost_estimate' in self.report

    def test_cmb_observable_present(self):
        assert 'cmb_observable' in self.report

    def test_summary_string(self):
        assert len(self.report['summary']) > 50
        assert 'c₁^{NP}' in self.report['summary'] or 'c1^' in self.report['summary'] or 'GPU' in self.report['summary']
