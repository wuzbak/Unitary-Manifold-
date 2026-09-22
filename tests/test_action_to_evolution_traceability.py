# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.action_to_evolution_traceability import (
    TRACEABILITY_TOLERANCE,
    action_to_evolution_traceability_receipt,
    action_to_evolution_traceability_registry,
)


def test_action_traceability_registry_is_executable_and_not_closure() -> None:
    registry = action_to_evolution_traceability_registry()
    assert registry["status"] == "SYNTHETIC_TRACEABILITY_AUDIT_READY"
    assert registry["verification_mode"] == "NUMERICAL_SYNTHETIC_STATE_AUDIT"
    assert registry["summary"]["state_family_count"] == 3
    assert registry["summary"]["row_count"] == 9
    assert registry["summary"]["closure_earned"] is False
    assert registry["routing"]["theoretical_closure_allowed"] is False
    assert registry["tolerance"] == TRACEABILITY_TOLERANCE
    assert "Synthetic residual audits" in registry["guardrail"]


def test_action_traceability_receipt_blocks_promotion_language() -> None:
    receipt = action_to_evolution_traceability_receipt()
    assert receipt["status"] == "RECEIPT_READY"
    assert receipt["checks"]["covers_three_sectors_per_state"] is True
    assert receipt["checks"]["routing_blocks_closure_language"] is True
    assert receipt["promotion_language_allowed"] is False
