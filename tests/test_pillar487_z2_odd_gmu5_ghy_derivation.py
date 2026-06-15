# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 487 — Z₂-odd G_{μ5} GHY Boundary Action Derivation."""
from __future__ import annotations

import math

from src.core.pillar487_z2_odd_gmu5_ghy_derivation import (
    PILLAR_STATUS,
    PILLAR_NUMBER,
    N_W,
    K_CS,
    K_R,
    ETA_BAR,
    FIXED_PLANES,
    ghy_boundary_action_setup,
    extrinsic_curvature_z2_transform,
    bc_alternatives_for_gmu5,
    dirichlet_bc_forces_z2_odd,
    neumann_bc_ruled_out,
    variational_well_posedness,
    admission_1_chain_complete,
    pillar_report,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'Z2_ODD_GMU5_GHY_BOUNDARY_ACTION_DERIVED'

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 487

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_k_r(self):
        assert abs(K_R - 37.0) < 1e-10

    def test_k_r_is_half_k_cs(self):
        assert abs(K_R - K_CS / 2.0) < 1e-10

    def test_eta_bar(self):
        t_nw = N_W * (N_W + 1) // 2  # = 15
        expected = (t_nw / 2.0) % 1.0  # = 0.5
        assert abs(ETA_BAR - expected) < 1e-10

    def test_eta_bar_value(self):
        assert abs(ETA_BAR - 0.5) < 1e-10

    def test_cs_times_eta_bar_is_37(self):
        # k_CS × η̄ = 74 × 0.5 = 37 (odd → n_w = 5)
        assert abs(K_CS * ETA_BAR - 37.0) < 1e-10

    def test_cs_times_eta_bar_is_odd(self):
        val = int(K_CS * ETA_BAR)
        assert val % 2 == 1  # 37 is odd

    def test_fixed_planes(self):
        assert len(FIXED_PLANES) == 2
        assert any('y = 0' in p for p in FIXED_PLANES)
        assert any('πR' in p for p in FIXED_PLANES)


class TestGHYBoundaryActionSetup:
    def setup_method(self):
        self.setup = ghy_boundary_action_setup()

    def test_returns_dict(self):
        assert isinstance(self.setup, dict)

    def test_has_total_action(self):
        assert 'total_action' in self.setup
        assert 'EH' in self.setup['total_action'] and 'GHY' in self.setup['total_action']

    def test_has_seh(self):
        assert 'seh' in self.setup

    def test_has_sghy(self):
        assert 'sghy' in self.setup

    def test_has_fixed_planes(self):
        assert 'fixed_planes' in self.setup
        assert len(self.setup['fixed_planes']) == 2

    def test_k_cs_correct(self):
        assert self.setup['k_cs'] == K_CS

    def test_n_w_correct(self):
        assert self.setup['n_w'] == N_W

    def test_has_pillar_406_reference(self):
        assert 'pillar_406_reference' in self.setup
        assert '406' in self.setup['pillar_406_reference']


class TestExtrinsicCurvatureZ2Transform:
    def setup_method(self):
        self.ext = extrinsic_curvature_z2_transform()

    def test_returns_dict(self):
        assert isinstance(self.ext, dict)

    def test_z2_parity_is_odd(self):
        assert self.ext['z2_parity_K'] == 'ODD'

    def test_has_transform(self):
        assert 'z2_transform_K' in self.ext
        # K(-y) = -K(y)
        assert '-K_{μν}(y)' in self.ext['z2_transform_K']

    def test_has_off_diagonal_coupling(self):
        assert 'off_diagonal_coupling' in self.ext
        assert 'G_{μ5}' in self.ext['off_diagonal_coupling']


class TestBCAlternativesForGmu5:
    def setup_method(self):
        self.bc = bc_alternatives_for_gmu5()

    def test_returns_dict(self):
        assert isinstance(self.bc, dict)

    def test_has_option_a(self):
        assert 'option_A' in self.bc

    def test_has_option_b(self):
        assert 'option_B' in self.bc

    def test_option_a_is_dirichlet(self):
        assert self.bc['option_A']['name'] == 'Dirichlet'

    def test_option_b_is_neumann(self):
        assert self.bc['option_B']['name'] == 'Neumann'

    def test_option_a_selected(self):
        assert self.bc['option_A']['selected'] is True

    def test_option_b_not_selected(self):
        assert self.bc['option_B']['selected'] is False

    def test_option_a_z2_parity_odd(self):
        assert self.bc['option_A']['z2_parity'] == 'ODD'

    def test_option_b_z2_parity_even(self):
        assert self.bc['option_B']['z2_parity'] == 'EVEN'

    def test_neumann_ruled_out_reason(self):
        assert 'ruled_out_reason' in self.bc['option_B']
        assert 'k_CS' in self.bc['option_B']['ruled_out_reason'] or '74' in self.bc['option_B']['ruled_out_reason']


class TestDirichletBCForcesZ2Odd:
    def setup_method(self):
        self.result = dirichlet_bc_forces_z2_odd()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_has_statement(self):
        assert 'statement' in self.result
        assert 'Z₂-odd' in self.result['statement'] or 'Z2-odd' in self.result['statement']

    def test_has_proof(self):
        assert 'proof' in self.result
        assert len(self.result['proof']) > 50

    def test_z2_odd_confirmed(self):
        assert self.result['z2_odd_confirmed'] is True

    def test_k_cs_constraint(self):
        assert self.result['k_cs_constraint'] == K_CS

    def test_mode_spectrum(self):
        assert 'mode_spectrum' in self.result
        assert 'no zero mode' in self.result['mode_spectrum']


class TestNeumannBCRuledOut:
    def setup_method(self):
        self.result = neumann_bc_ruled_out()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_neumann_holonomy_zero(self):
        assert self.result['neumann_holonomy'] == 0.0

    def test_neumann_k_cs_times_hol_zero(self):
        assert self.result['neumann_k_cs_times_hol'] == 0.0

    def test_neumann_conflict_with_nonzero_kcs(self):
        assert self.result['neumann_conflict'] is True

    def test_dirichlet_eta_bar_correct(self):
        assert abs(self.result['dirichlet_eta_bar'] - 0.5) < 1e-10

    def test_dirichlet_cs_level_is_37(self):
        assert self.result['dirichlet_k_cs_times_eta_bar'] == 37

    def test_dirichlet_consistent_odd(self):
        assert self.result['dirichlet_consistent'] is True

    def test_conclusion(self):
        assert self.result['conclusion'] == 'NEUMANN_RULED_OUT'

    def test_ruling_out_argument_present(self):
        assert 'ruling_out_argument' in self.result
        assert '37' in self.result['ruling_out_argument']

    def test_k_cs_nonzero(self):
        assert self.result['k_cs_nonzero'] is True


class TestVariationalWellPosedness:
    def setup_method(self):
        self.result = variational_well_posedness()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_z2_odd_confirmed(self):
        assert self.result['z2_odd_confirmed'] is True

    def test_derivation_level(self):
        assert 'CLASSICAL' in self.result['derivation_level']

    def test_has_residual(self):
        assert 'residual' in self.result
        assert 'quantum' in self.result['residual'].lower()

    def test_conclusion_mentions_dirichlet(self):
        assert 'Dirichlet' in self.result['conclusion']

    def test_conclusion_mentions_z2_odd(self):
        assert 'Z₂-odd' in self.result['conclusion'] or 'Z2-odd' in self.result['conclusion']

    def test_has_bc_analysis(self):
        assert 'bc_analysis' in self.result

    def test_has_neumann_ruled_out(self):
        assert 'neumann_ruled_out' in self.result
        assert self.result['neumann_ruled_out']['conclusion'] == 'NEUMANN_RULED_OUT'


class TestAdmission1ChainComplete:
    def setup_method(self):
        self.chain = admission_1_chain_complete()

    def test_returns_dict(self):
        assert isinstance(self.chain, dict)

    def test_admission_number_1(self):
        assert self.chain['admission_number'] == 1

    def test_chain_has_minimum_steps(self):
        assert len(self.chain['chain']) >= 5

    def test_all_steps_complete(self):
        assert self.chain['all_steps_complete'] is True

    def test_classical_level(self):
        assert 'CLASSICAL' in self.chain['derivation_level']

    def test_has_residual(self):
        assert 'residual' in self.chain
        assert 'quantum' in self.chain['residual'].lower()

    def test_n_w_recovered(self):
        assert self.chain['n_w_recovered'] == N_W

    def test_cs_level_is_37(self):
        assert self.chain['cs_level_contribution'] == 37

    def test_eta_bar(self):
        assert abs(self.chain['eta_bar'] - 0.5) < 1e-10

    def test_has_new_status(self):
        assert 'new_status_p487' in self.chain
        assert 'Z2_ODD' in self.chain['new_status_p487'] or 'Z₂-odd' in self.chain['new_status_p487'] or 'GHY' in self.chain['new_status_p487']

    def test_k_cs_correct(self):
        assert self.chain['k_cs_check'] == K_CS


class TestPillarReport:
    def setup_method(self):
        self.report = pillar_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_pillar_number(self):
        assert self.report['pillar'] == 487

    def test_status(self):
        assert self.report['status'] == PILLAR_STATUS

    def test_has_prerequisites(self):
        prereqs = self.report['prerequisites']
        assert any('387' in p for p in prereqs)
        assert any('406' in p for p in prereqs)

    def test_has_variational_analysis(self):
        assert 'variational_analysis' in self.report
        assert self.report['variational_analysis']['z2_odd_confirmed'] is True

    def test_has_admission_1_chain(self):
        assert 'admission_1_chain' in self.report
        assert self.report['admission_1_chain']['all_steps_complete'] is True

    def test_verdict_mentions_dirichlet(self):
        assert 'Dirichlet' in self.report['verdict']

    def test_verdict_mentions_n_w_5(self):
        assert 'n_w = 5' in self.report['verdict'] or 'n_w=5' in self.report['verdict']
