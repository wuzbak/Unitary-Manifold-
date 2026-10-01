# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.action_to_evolution_el_mismatch_certificate import (
    euler_lagrange_mismatch_certificate,
    euler_lagrange_mismatch_receipt,
)


def test_el_mismatch_certificate_scaffold_is_explicit() -> None:
    cert = euler_lagrange_mismatch_certificate()
    assert cert['status'] == 'FIELD_EQUATIONS_DERIVED_RESIDUAL_CERTIFIED_PENDING_PROMOTION'
    assert cert['summary']['sectors_covered'] == 3
    assert cert['summary']['template_alignment_available'] is True
    assert cert['summary']['symbolic_mapping_receipt_ready'] is True
    assert cert['summary']['euler_lagrange_deliverable_earned'] is True
    assert cert['summary']['t_dynamics_derived_from_action'] is False
    assert cert['summary']['steward_promotion_required'] is True
    assert cert['summary']['closure_earned'] is False
    assert {row['verdict'] for row in cert['sector_rows']} == {
        'DERIVED_EULER_LAGRANGE_RESIDUAL_CERTIFIED_WITHIN_PERIMETER'
    }
    assert any('Z₂ orbifold' in item for item in cert['verified_perimeter'])


def test_el_mismatch_receipt_ready_without_overclaim() -> None:
    receipt = euler_lagrange_mismatch_receipt()
    assert receipt['status'] == 'RECEIPT_READY'
    assert receipt['checks']['sectors_cover_metric_gauge_scalar'] is True
    assert receipt['checks']['row_verdicts_match_evidence'] is True
    assert receipt['euler_lagrange_deliverable_earned'] is True
    assert receipt['closure_earned'] is False
