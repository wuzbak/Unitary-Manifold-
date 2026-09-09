# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.action_to_evolution_residual_table import (
    action_to_evolution_residual_receipt,
    action_to_evolution_residual_table,
)


def test_residual_table_surface_is_present_and_guarded() -> None:
    table = action_to_evolution_residual_table()
    assert table['status'] == 'TEMPLATE_ALIGNMENT_SURFACED'
    assert table['verification_mode'] == 'SIDE_BY_SIDE_TEMPLATE_ALIGNMENT_ONLY'
    assert table['summary']['sector_count'] == 3
    assert table['summary']['full_template_alignment'] is True
    assert table['summary']['euler_lagrange_derivation_verified'] is False
    assert 'does not certify Euler-Lagrange derivation' in table['guardrail']


def test_residual_receipt_is_ready_without_claiming_closure() -> None:
    receipt = action_to_evolution_residual_receipt()
    assert receipt['status'] == 'RECEIPT_READY'
    assert receipt['checks']['rows_cover_metric_gauge_scalar'] is True
    assert receipt['euler_lagrange_deliverable_earned'] is False
    assert receipt['closure_earned'] is False
