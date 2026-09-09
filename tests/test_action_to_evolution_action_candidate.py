# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.action_to_evolution_action_candidate import (
    candidate_action_surface_receipt,
    checkable_action_functional_candidate,
    time_domain_boundary_receipt,
)


def test_candidate_surface_is_explicit_and_bounded() -> None:
    candidate = checkable_action_functional_candidate()
    assert candidate['status'] == 'CHECKABLE_CANDIDATE_SURFACED'
    assert candidate['dynamical_fields'] == ['g_μν', 'B_μ', 'φ']
    assert 'symbolic_form' in candidate['action_density']
    assert candidate['euler_lagrange_comparison_template']['residual_table_required'] is True
    assert 'only' in candidate['promotion_boundary_note'].lower()


def test_candidate_receipt_marks_non_trivial_progress_without_closure() -> None:
    receipt = candidate_action_surface_receipt()
    assert receipt['status'] == 'RECEIPT_READY'
    assert receipt['checkable_action_deliverable_earned'] is True
    assert receipt['closure_earned'] is False


def test_time_domain_boundary_receipt_is_explicit() -> None:
    receipt = time_domain_boundary_receipt()
    assert receipt['status'] == 'RECEIPT_READY'
    assert receipt['checks']['time_identification_explicit'] is True
    assert receipt['checks']['domain_explicit'] is True
    assert receipt['time_domain_deliverable_earned'] is True
