# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

import src.core.pillar1130_action_derived_flow_steward_promotion as p1130

from src.core.pillar1130_action_derived_flow_steward_promotion import (
    DOES_NOT_ESTABLISH,
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PROMOTED_DELIVERABLE_ID,
    RESIDUAL_OBLIGATIONS,
    STEWARD_PROMOTION_RECORD,
    VERSION,
    action_derived_flow_steward_promotion,
    pillar1130_summary,
    steward_promotion_decision,
)


@pytest.fixture(scope="module")
def report():
    return action_derived_flow_steward_promotion()


def test_identity() -> None:
    assert PILLAR_NUMBER == 1130
    assert PILLAR_GATE == 'ACTION_DERIVED_FLOW_STEWARD_PROMOTION'
    assert PILLAR_STATUS == 'ACTION_DERIVED_FLOW_PROMOTED_WITHIN_DECLARED_PERIMETER'
    assert VERSION == 'v38.2'
    assert NEXT_PILLAR_SLOT == 1131


def test_steward_record_is_explicit() -> None:
    assert STEWARD_PROMOTION_RECORD['decision'] == 'PROMOTE_WITHIN_DECLARED_PERIMETER'
    assert STEWARD_PROMOTION_RECORD['deliverable_id'] == PROMOTED_DELIVERABLE_ID
    assert 'merge' in STEWARD_PROMOTION_RECORD['ratification']
    assert STEWARD_PROMOTION_RECORD['reviewed_evidence']


def test_decision_passes_every_evidence_check() -> None:
    decision = steward_promotion_decision()
    assert decision['promoted'] is True
    assert decision['deliverable_status'] == 'EARNED'
    assert all(decision['evidence_checks'].values())
    assert decision['framework_closure_earned'] is False
    assert decision['verified_perimeter']


def test_non_claims_and_residual_obligations_are_stated() -> None:
    joined = ' '.join(DOES_NOT_ESTABLISH)
    assert 't-relaxation law is declared' in joined
    assert 'legacy phenomenological flow' in joined
    assert 'not a Lean proof' in joined
    assert 'T_RELAXATION_LAW_DECLARED_NOT_DERIVED' in RESIDUAL_OBLIGATIONS


def test_decision_fails_closed_when_evidence_fails(monkeypatch) -> None:
    failing = {
        'status': 'DERIVED_FLOW_VERIFICATION_FAILED',
        'verified_perimeter': [],
        'summary': {
            'field_equations_derived_from_action': True,
            'residual_certificate_present': False,
            'all_checks_pass': False,
            't_dynamics_derived_from_action': False,
            'closure_earned': False,
        },
    }
    monkeypatch.setattr(p1130, 'derived_flow_verification_certificate', lambda: failing)
    decision = p1130.steward_promotion_decision()
    assert decision['promoted'] is False
    assert decision['deliverable_status'] == 'DERIVED_PENDING_STEWARD_PROMOTION'


def test_contract_reflects_decision_without_closure(report) -> None:
    assert report['contract_reflects_decision'] is True
    assert report['evolution_law_still_open'] is True
    assert report['contract_status'] == 'DELIVERABLES_EARNED_EVOLUTION_LAW_OPEN'


def test_truth_surfaces_synchronized(report) -> None:
    assert report['truth_surface_sync']['all_pass'] is True


def test_valid(report) -> None:
    assert report['valid'] is True
    assert report['status'] == PILLAR_STATUS


def test_summary() -> None:
    summary = pillar1130_summary()
    assert summary['valid'] is True
    assert summary['promoted'] is True
    assert summary['framework_closure_earned'] is False
