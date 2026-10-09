# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

import src.core.pillar1131_offdiagonal_exact_reduction_closure as p1131

from src.core.pillar1131_offdiagonal_exact_reduction_closure import (
    CLOSED_RESIDUAL_OBLIGATION,
    DOES_NOT_ESTABLISH,
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    REMAINING_RESIDUAL_OBLIGATIONS,
    VERSION,
    current_residual_obligations,
    offdiagonal_exact_reduction_closure,
    pillar1131_summary,
)


@pytest.fixture(scope="module")
def packet():
    return offdiagonal_exact_reduction_closure()


def test_identity() -> None:
    assert PILLAR_NUMBER == 1131
    assert PILLAR_GATE == 'OFFDIAGONAL_EXACT_REDUCTION_IDENTITY_CLOSURE'
    assert PILLAR_STATUS == 'OFFDIAGONAL_REDUCTION_IDENTITY_EXACT_CLOSED'
    assert VERSION == 'v38.3'
    assert NEXT_PILLAR_SLOT == 1132
    assert CLOSED_RESIDUAL_OBLIGATION == 'EXACT_REDUCTION_IDENTITY_BEYOND_REDUCED_DIAGONAL_ANSATZ'


def test_remaining_obligations_are_explicit() -> None:
    assert CLOSED_RESIDUAL_OBLIGATION not in REMAINING_RESIDUAL_OBLIGATIONS
    assert 'T_RELAXATION_LAW_DECLARED_NOT_DERIVED' in REMAINING_RESIDUAL_OBLIGATIONS
    assert 'PHYSICAL_TIME_EVOLUTION_NOT_CERTIFIED' in REMAINING_RESIDUAL_OBLIGATIONS


def test_non_claims_are_stated() -> None:
    joined = ' '.join(DOES_NOT_ESTABLISH)
    assert 't-relaxation law is still declared' in joined
    assert 'DELIVERABLES_EARNED_EVOLUTION_LAW_OPEN' in joined
    assert 'not a Lean proof' in joined


@pytest.mark.slow
def test_closure_evidence_checks_pass(packet) -> None:
    assert packet['closed'] is True
    assert all(packet['evidence_checks'].values())
    assert packet['framework_closure_earned'] is False
    assert packet['direct_check']['ansatz'] == 'offdiagonal_two_component'
    assert packet['direct_check']['exact_identity_verified'] is True


@pytest.mark.slow
def test_closure_fails_closed_when_direct_check_fails(monkeypatch) -> None:
    def failing_check(*args, **kwargs):
        return {
            'ansatz': 'offdiagonal_two_component',
            'fields_varied': [],
            'max_abs_euler_operator_of_difference': 1.0,
            'reduction_verified': False,
            'exact_simplification_performed': True,
            'exact_identity_verified': False,
        }

    monkeypatch.setattr(p1131, 'symbolic_kk_reduction_check', failing_check)
    result = p1131.offdiagonal_exact_reduction_closure()
    assert result['closed'] is False
    assert result['status'] == 'OFFDIAGONAL_EXACT_REDUCTION_IDENTITY_CLOSURE_NOT_IN_EFFECT'


def test_current_residual_obligations_drops_closed_item_when_closed() -> None:
    previous = [
        'T_RELAXATION_LAW_DECLARED_NOT_DERIVED',
        CLOSED_RESIDUAL_OBLIGATION,
        'PHYSICAL_TIME_EVOLUTION_NOT_CERTIFIED',
    ]
    assert current_residual_obligations(previous) == [
        'T_RELAXATION_LAW_DECLARED_NOT_DERIVED',
        'PHYSICAL_TIME_EVOLUTION_NOT_CERTIFIED',
    ]


def test_current_residual_obligations_keeps_list_when_not_closed(monkeypatch) -> None:
    monkeypatch.setattr(p1131, 'offdiagonal_exact_reduction_closure', lambda: {'closed': False})
    previous = ['A', CLOSED_RESIDUAL_OBLIGATION, 'B']
    assert current_residual_obligations(previous) == previous


@pytest.mark.slow
def test_truth_surfaces_synchronized() -> None:
    summary = pillar1131_summary()
    assert summary['truth_surface_sync']['all_pass'] is True


@pytest.mark.slow
def test_summary_valid() -> None:
    summary = pillar1131_summary()
    assert summary['valid'] is True
    assert summary['closed'] is True
    assert summary['framework_closure_earned'] is False
    assert summary['status'] == PILLAR_STATUS
