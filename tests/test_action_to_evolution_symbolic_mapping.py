# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.action_to_evolution_symbolic_mapping import (
    action_to_evolution_symbolic_mapping_receipt,
    action_to_evolution_symbolic_term_mapping,
)


def test_symbolic_mapping_surface_is_deterministic_and_guarded() -> None:
    mapping = action_to_evolution_symbolic_term_mapping()
    assert mapping['status'] == 'SYMBOLIC_MAPPING_SURFACED'
    assert mapping['summary']['sectors_covered'] == 3
    assert mapping['summary']['all_template_pass'] is True
    assert mapping['summary']['signed_mismatch_threshold'] == 0.0
    assert mapping['summary']['derivation_verified'] is False


def test_symbolic_mapping_receipt_is_ready_without_overclaim() -> None:
    receipt = action_to_evolution_symbolic_mapping_receipt()
    assert receipt['status'] == 'RECEIPT_READY'
    assert receipt['checks']['sectors_cover_metric_gauge_scalar'] is True
    assert receipt['checks']['signed_mismatch_fields_present'] is True
    assert receipt['checks']['all_rows_blocked_on_derivation'] is True
    assert receipt['derivation_verified'] is False
