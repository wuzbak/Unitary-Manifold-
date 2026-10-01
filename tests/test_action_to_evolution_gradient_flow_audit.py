# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import numpy as np
import pytest

from src.core.action_to_evolution_contract import action_to_evolution_deliverable_contract
from src.core.action_to_evolution_el_mismatch_certificate import (
    euler_lagrange_mismatch_certificate,
    euler_lagrange_mismatch_receipt,
)
from src.core.action_to_evolution_gradient_flow_audit import (
    ACTION_FORCED_TERMS,
    MATCH_TOLERANCE,
    audit_reference_state,
    coupled_block_asymmetry_table,
    cross_coupling_obstruction,
    gauge_sector_gradient_check,
    gradient_flow_audit_certificate,
    scalar_sector_gradient_check,
)


def test_reference_state_is_nontrivial_and_deterministic() -> None:
    a = audit_reference_state()
    b = audit_reference_state()
    assert np.array_equal(a.g, b.g) and np.array_equal(a.B, b.B) and np.array_equal(a.phi, b.phi)
    assert np.max(np.abs(a.B)) > 0.0
    assert np.std(a.phi) > 0.0
    assert a.kk_backreaction_coupling == 0.0


def test_scalar_sector_is_frozen_background_gradient_flow() -> None:
    check = scalar_sector_gradient_check()
    assert check['gradient_flow_match'] is True
    assert check['max_relative_residual'] < MATCH_TOLERANCE


def test_scalar_check_tracks_negative_alpha() -> None:
    state = audit_reference_state()
    state.alpha = -state.alpha
    flipped = scalar_sector_gradient_check(state)
    assert flipped['gradient_flow_match'] is True


def test_scalar_check_rejects_active_kk_source() -> None:
    state = audit_reference_state()
    state.n_kk_modes = 3
    state.kk_backreaction_coupling = 0.1
    with pytest.raises(ValueError):
        scalar_sector_gradient_check(state)


def test_gauge_sector_interior_match_and_boundary_failure() -> None:
    check = gauge_sector_gradient_check()
    assert check['interior_gradient_flow_match'] is True
    assert check['interior_max_relative_residual'] < MATCH_TOLERANCE
    assert check['boundary_gradient_flow_match'] is False


def test_cross_coupling_obstruction_is_exact_zero_vs_nonzero() -> None:
    obs = cross_coupling_obstruction()
    assert obs['max_abs_dF_B_dphi'] == 0.0
    assert obs['max_abs_dF_phi_dB_directional'] > 1e-3
    assert obs['H_nonzero'] is True
    assert obs['gradient_flow_refuted_in_class'] is True
    assert obs['not_excluded']


def test_obstruction_vanishes_when_gauge_field_is_zero() -> None:
    state = audit_reference_state()
    state.B = np.zeros_like(state.B)
    obs = cross_coupling_obstruction(state)
    assert obs['H_nonzero'] is False
    assert obs['gradient_flow_refuted_in_class'] is False


def test_certificate_refutes_without_overclaiming() -> None:
    cert = gradient_flow_audit_certificate()
    assert cert['status'] == 'GRADIENT_FLOW_FORM_REFUTED_FOR_IMPLEMENTED_COUPLED_FLOW_IN_STATED_CLASS'
    summary = cert['summary']
    assert summary['coupled_flow_gradient_form_refuted_in_class'] is True
    assert summary['euler_lagrange_match_verified'] is False
    assert summary['closure_earned'] is False
    assert len(cert['action_forced_terms_missing_from_implementation']) == len(ACTION_FORCED_TERMS) >= 3
    assert cert['guardrail']


def test_el_certificate_and_contract_consume_audit_without_promotion() -> None:
    cert = euler_lagrange_mismatch_certificate()
    assert cert['gradient_flow_audit']['summary']['closure_earned'] is False
    assert cert['summary']['coupled_flow_gradient_form_refuted_in_class'] is True
    assert cert['summary']['euler_lagrange_deliverable_earned'] is True
    assert cert['summary']['closure_earned'] is False
    assert all(row['gradient_flow_audit_finding'] for row in cert['sector_rows'])
    receipt = euler_lagrange_mismatch_receipt()
    assert receipt['checks']['gradient_flow_audit_present'] is True
    contract = action_to_evolution_deliverable_contract()
    assert contract['promotion_ready'] is False
    el = contract['primary_deliverables'][1]
    assert el['earned'] is True
    assert el['status'] == 'EARNED'
    assert 'block-diagonal' in el['current_gap']


@pytest.mark.slow
def test_full_block_asymmetry_table() -> None:
    table = coupled_block_asymmetry_table(audit_reference_state(N=10))
    rows = {row['block_pair']: row for row in table['rows']}
    assert rows['B-B']['symmetric_within_tolerance'] is True
    assert rows['B-phi']['symmetric_within_tolerance'] is False
    assert rows['g-g']['symmetric_within_tolerance'] is False
    assert table['l2_gradient_flow'] is False
