# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 434 — ADM BSSN Lapse Closure."""
from __future__ import annotations

import math
import pytest

from src.core.pillar434_adm_bssn_lapse import (
    PILLAR_STATUS,
    PILLAR_NUMBER,
    N_W,
    K_CS,
    C_S,
    PHI_0,
    M_KK_DEFAULT,
    EPSILON_SR,
    DN_OVER_N_UPPER_BOUND,
    FALLIBILITY_BOUND,
    bssn_conformal_variables,
    hamiltonian_constraint,
    bssn_lapse_correction,
    slow_roll_lapse_correction,
    adm_lapse_closure_report,
    verify_lapse_below_bound,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'ADM_LAPSE_BSSN_CLOSED'

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 434

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_c_s(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-12

    def test_phi_0(self):
        assert abs(PHI_0 - 2.0 * math.pi * N_W) < 1e-10

    def test_epsilon_sr_small(self):
        assert EPSILON_SR < 0.01

    def test_epsilon_sr_formula(self):
        cs2 = C_S ** 2
        expected = 3.0 * (1.0 + cs2) / (PHI_0 ** 2)
        assert abs(EPSILON_SR - expected) < 1e-12

    def test_dn_over_n_far_below_fallibility_bound(self):
        assert DN_OVER_N_UPPER_BOUND < FALLIBILITY_BOUND / 10.0

    def test_fallibility_bound(self):
        assert FALLIBILITY_BOUND == pytest.approx(0.006, rel=0.01)


class TestBssnConformalVariables:
    def test_returns_dict(self):
        result = bssn_conformal_variables(1.0)
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = bssn_conformal_variables(1.0)
        for key in [
            'phi_radion', 'phi_bssn', 'scale_factor_a', 'gamma_tilde_diag',
            'K_trace', 'A_tilde_trace', 'R_tilde', 'H_hub', 'N_kinematic'
        ]:
            assert key in result

    def test_scale_factor_positive(self):
        result = bssn_conformal_variables(1.0)
        assert result['scale_factor_a'] > 0.0

    def test_k_trace_negative(self):
        # K = -3H should be negative in de Sitter
        result = bssn_conformal_variables(1.0)
        assert result['K_trace'] < 0.0

    def test_a_tilde_zero(self):
        # Isotropic → traceless extrinsic curvature = 0
        result = bssn_conformal_variables(1.0)
        assert result['A_tilde_trace'] == 0.0

    def test_r_tilde_zero(self):
        # Flat conformal metric → R̃ = 0
        result = bssn_conformal_variables(1.0)
        assert result['R_tilde'] == 0.0

    def test_n_kinematic_equals_phi(self):
        phi = 0.7
        result = bssn_conformal_variables(phi)
        assert result['N_kinematic'] == phi

    def test_gamma_tilde_unit(self):
        result = bssn_conformal_variables(1.0)
        assert result['gamma_tilde_diag'] == [1.0, 1.0, 1.0]


class TestHamiltonianConstraint:
    def test_returns_dict(self):
        result = hamiltonian_constraint(1.0)
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = hamiltonian_constraint(1.0)
        for key in ['K_trace', 'H_residual', 'fractional_violation',
                    'constraint_satisfied_to_01pct']:
            assert key in result

    def test_de_sitter_residual_zero(self):
        # With rho_correction = 0 (exact de Sitter), H_residual should be 0
        result = hamiltonian_constraint(1.0, rho_correction=0.0)
        assert abs(result['H_residual']) < 1e-10

    def test_constraint_satisfied_de_sitter(self):
        result = hamiltonian_constraint(1.0)
        assert result['constraint_satisfied_to_01pct']

    def test_nonzero_correction_breaks_constraint(self):
        result = hamiltonian_constraint(1.0, rho_correction=1.0)
        assert result['H_residual'] != 0.0


class TestBssnLapseCorrection:
    def test_returns_dict(self):
        result = bssn_lapse_correction(1.0)
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = bssn_lapse_correction(1.0)
        for key in [
            'phi_radion', 'N_kinematic', 'delta_N', 'delta_N_over_N',
            'delta_N_percent', 'N_dynamical', 'below_fallibility_bound', 'verdict'
        ]:
            assert key in result

    def test_delta_n_small(self):
        result = bssn_lapse_correction(1.0)
        assert abs(result['delta_N_over_N']) < FALLIBILITY_BOUND

    def test_below_fallibility_bound(self):
        result = bssn_lapse_correction(1.0)
        assert result['below_fallibility_bound']

    def test_verdict_is_closed(self):
        result = bssn_lapse_correction(1.0)
        assert result['verdict'] == 'ADM_LAPSE_BSSN_CLOSED'

    def test_dynamical_lapse_close_to_kinematic(self):
        phi = 0.8
        result = bssn_lapse_correction(phi)
        # N_dynamical should be very close to phi (kinematic lapse)
        assert abs(result['N_dynamical'] - phi) < 0.01 * phi

    def test_correction_less_than_01pct(self):
        result = bssn_lapse_correction(1.0)
        assert result['delta_N_percent'] < 0.1


class TestSlowRollLapseCorrection:
    def test_returns_dict(self):
        result = slow_roll_lapse_correction()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = slow_roll_lapse_correction()
        for key in [
            'phi_0', 'c_s', 'epsilon_sr', 'delta_N_over_N',
            'below_fallibility_bound', 'verdict'
        ]:
            assert key in result

    def test_epsilon_sr_matches_constant(self):
        result = slow_roll_lapse_correction()
        assert abs(result['epsilon_sr'] - EPSILON_SR) < 1e-12

    def test_below_fallibility_bound(self):
        result = slow_roll_lapse_correction()
        assert result['below_fallibility_bound']

    def test_verdict_closed(self):
        result = slow_roll_lapse_correction()
        assert result['verdict'] == 'ADM_LAPSE_BSSN_CLOSED'

    def test_small_correction(self):
        result = slow_roll_lapse_correction()
        assert result['delta_N_percent'] < 0.1


class TestVerifyLapseBelow:
    def test_at_ftum_fixed_point(self):
        assert verify_lapse_below_bound(1.0) is True

    def test_at_small_phi(self):
        assert verify_lapse_below_bound(0.1) is True

    def test_at_large_phi(self):
        assert verify_lapse_below_bound(10.0) is True


class TestAdmLapseClosureReport:
    def setup_method(self):
        self.report = adm_lapse_closure_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_pillar_number(self):
        assert self.report['pillar'] == 434

    def test_status(self):
        assert self.report['status'] == 'ADM_LAPSE_BSSN_CLOSED'

    def test_gap_closed(self):
        assert 'FALLIBILITY' in self.report['gap_closed']
        assert 'BSSN' in self.report['gap_closed']

    def test_prior_status(self):
        assert 'PARTIALLY_CLOSED' in self.report['prior_status']

    def test_new_status(self):
        assert self.report['new_status'] == 'ADM_LAPSE_BSSN_CLOSED'

    def test_no_residual(self):
        assert self.report['residual'] is None

    def test_closure_summary_verdict(self):
        assert self.report['closure_summary']['verdict'] == 'ADM_LAPSE_BSSN_CLOSED'

    def test_correction_small(self):
        pct_str = self.report['closure_summary']['bssn_correction_pct']
        # Parse the percentage value
        pct = float(pct_str.replace('%', ''))
        assert pct < 0.1  # < 0.1%

    def test_ratio_below_one(self):
        ratio = self.report['closure_summary']['ratio_correction_to_bound']
        assert ratio < 1.0

    def test_references_not_empty(self):
        assert len(self.report['references']) >= 3


class TestNumerics:
    def test_mkk_over_h_sq(self):
        # H = M_KK/(4π) → (M_KK/H)² = (4π)²
        expected = (4.0 * math.pi) ** 2
        actual = (M_KK_DEFAULT / (M_KK_DEFAULT / (4.0 * math.pi))) ** 2
        assert abs(actual - expected) < 0.01

    def test_dn_n_formula(self):
        expected = EPSILON_SR / (4.0 * math.pi) ** 2
        assert abs(DN_OVER_N_UPPER_BOUND - expected) < 1e-15

    def test_ratio_to_fallibility_bound(self):
        ratio = DN_OVER_N_UPPER_BOUND / FALLIBILITY_BOUND
        # Should be << 1 (correction ≪ 0.6% bound)
        assert ratio < 0.05
