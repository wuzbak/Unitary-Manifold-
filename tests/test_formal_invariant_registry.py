# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.formal_invariant_registry import evaluate_formal_invariants, formal_invariant_registry


def test_formal_invariant_registry_is_focused_and_guarded() -> None:
    registry = formal_invariant_registry()
    assert registry["status"] == "FORMAL_INVARIANT_REGISTRY_READY"
    assert len(registry["invariants"]) == 4
    assert registry["interface_standard"]["lean4"]["required_fields"]
    assert registry["interface_standard"]["z3"]["required_fields"]
    assert "small high-leverage invariant set" in registry["scope_note"]


def test_formal_invariant_evaluation_passes_without_claiming_total_closure() -> None:
    evaluation = evaluate_formal_invariants()
    assert evaluation["status"] == "FORMAL_INVARIANTS_PASS"
    assert evaluation["summary"]["checked_count"] == 4
    assert evaluation["summary"]["all_pass"] is True
    assert "did not regress" in evaluation["guardrail"]
