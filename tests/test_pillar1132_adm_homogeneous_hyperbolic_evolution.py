# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

import src.core.pillar1132_adm_homogeneous_hyperbolic_evolution as p1132

from src.core.pillar1132_adm_homogeneous_hyperbolic_evolution import (
    DOES_NOT_ESTABLISH,
    NEW_CERTIFIED_SUBCASE,
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    REMAINING_RESIDUAL_OBLIGATIONS,
    VERSION,
    adm_homogeneous_hyperbolic_evolution_certificate,
    pillar1132_adm_homogeneous_hyperbolic_evolution,
    pillar1132_summary,
)


@pytest.fixture(scope="module")
def certificate():
    return adm_homogeneous_hyperbolic_evolution_certificate()


@pytest.fixture(scope="module")
def packet():
    return pillar1132_adm_homogeneous_hyperbolic_evolution()


def test_identity() -> None:
    assert PILLAR_NUMBER == 1132
    assert PILLAR_GATE == 'ADM_HOMOGENEOUS_HYPERBOLIC_EVOLUTION'
    assert PILLAR_STATUS == 'ADM_RESTRICTED_ACCELERATION_IDENTITIES_VERIFIED'
    assert VERSION == 'v38.4'
    assert NEXT_PILLAR_SLOT == 1133
    assert NEW_CERTIFIED_SUBCASE == (
        'ADM_OFF_SHELL_ACCELERATION_AND_STATIC_IDENTITIES_ONLY'
    )


def test_remaining_obligations_are_untouched() -> None:
    assert 'T_RELAXATION_LAW_DECLARED_NOT_DERIVED' in REMAINING_RESIDUAL_OBLIGATIONS
    assert 'PHYSICAL_TIME_EVOLUTION_NOT_CERTIFIED' in REMAINING_RESIDUAL_OBLIGATIONS
    # This pillar introduces a new sub-case rather than closing either obligation.
    assert NEW_CERTIFIED_SUBCASE not in REMAINING_RESIDUAL_OBLIGATIONS


def test_non_claims_are_stated() -> None:
    joined = ' '.join(DOES_NOT_ESTABLISH)
    assert 'gauge field B_mu is excluded' in joined
    assert 'NOT reinterpreted as coordinate time' in joined
    assert 'NOT closed by this pillar' in joined
    assert 'DELIVERABLES_EARNED_EVOLUTION_LAW_OPEN' in joined
    assert 'not a Lean proof' in joined


@pytest.mark.slow
def test_certificate_hyperbolicity_evidence(certificate) -> None:
    hyperbolicity = certificate['hyperbolicity']
    # Constraints (lapse, shift) carry no genuine second time derivative.
    assert hyperbolicity['h_equation_is_nondynamical'] is True
    assert hyperbolicity['N_equation_is_constraint'] is True
    assert hyperbolicity['Nx_equation_is_constraint'] is True
    # An off-shell acceleration term does not establish a constrained solution.
    assert hyperbolicity['p_equation_is_dynamical'] is True
    assert hyperbolicity['coeff_d2h_dt2_in_h_equation'] == 0
    assert hyperbolicity['coeff_d2p_dt2_in_p_equation'] != 0
    assert all(
        coefficient == 0
        for equation in hyperbolicity['constraint_acceleration_coefficients'].values()
        for coefficient in equation.values()
    )
    assert certificate['t_dynamics_derived_from_action'] is False
    assert certificate['off_shell_time_derivative_terms_derived'] is True
    assert certificate['constraint_compatible_nonconstant_scalar_evolution'] is False
    assert certificate['well_posedness_established'] is False


@pytest.mark.slow
def test_certificate_static_reduction_cross_check_is_exact(certificate) -> None:
    cross_check = certificate['static_reduction_cross_check']
    assert cross_check['h_equation_matches_exactly'] is True
    assert cross_check['p_equation_matches_exactly'] is True
    assert cross_check['diff_h_equation'] == 0
    assert cross_check['diff_p_equation'] == 0
    assert cross_check['repo_helpers_used'] == [
        '_symbolic_setup', '_sym_ricci_scalar', '_sym_reduced_lagrangian',
    ]


@pytest.mark.slow
def test_certificate_verified_and_fails_closed(certificate) -> None:
    assert certificate['verified'] is True
    assert all(certificate['evidence_checks'].values())
    assert certificate['closure_earned'] is False
    assert certificate['status'] == NEW_CERTIFIED_SUBCASE


def test_certificate_fails_closed_when_hyperbolicity_evidence_fails(monkeypatch) -> None:
    def failing_hyperbolicity():
        return {
            'h_equation_is_nondynamical': False,
            'p_equation_is_dynamical': True,
            'N_equation_is_constraint': True,
            'Nx_equation_is_constraint': True,
        }

    monkeypatch.setattr(p1132, '_adm_hyperbolicity_evidence', failing_hyperbolicity)
    result = p1132.adm_homogeneous_hyperbolic_evolution_certificate()
    assert result['verified'] is False
    assert result['status'] == 'ADM_HOMOGENEOUS_HYPERBOLIC_EVOLUTION_NOT_VERIFIED'


def test_certificate_fails_closed_when_cross_check_fails(monkeypatch) -> None:
    def failing_cross_check():
        return {
            'h_equation_matches_exactly': False,
            'p_equation_matches_exactly': True,
        }

    monkeypatch.setattr(p1132, '_adm_static_reduction_cross_check', failing_cross_check)
    result = p1132.adm_homogeneous_hyperbolic_evolution_certificate()
    assert result['verified'] is False


@pytest.mark.slow
def test_truth_surfaces_synchronized(packet) -> None:
    assert packet['truth_surface_sync']['all_pass'] is True


@pytest.mark.slow
def test_packet_valid(packet) -> None:
    assert packet['valid'] is True
    assert packet['status'] == PILLAR_STATUS
    assert packet['framework_closure_earned'] is False
    assert packet['remaining_residual_obligations'] == REMAINING_RESIDUAL_OBLIGATIONS


@pytest.mark.slow
def test_summary() -> None:
    summary = pillar1132_summary()
    assert summary['valid'] is True
    assert summary['verified'] is True
    assert summary['framework_closure_earned'] is False
    assert summary['status'] == PILLAR_STATUS
