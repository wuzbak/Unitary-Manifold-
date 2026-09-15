# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.lean_python_closure_pipeline import (
    emit_normalized_obligations,
    evaluate_closure_promotion_gate,
    evaluate_no_bloat_theorem_gate,
    ingest_lean_outcomes,
)


def test_no_bloat_gate_rejects_theorem_only_growth() -> None:
    verdict = evaluate_no_bloat_theorem_gate(
        {
            "unit_id": "ACTION_TO_EVOLUTION_BOUNDARY",
            "retired_blocker_ids": [],
            "unlocked_python_capabilities": [],
        }
    )
    assert verdict["accepted"] is False
    assert "rejected_as_theorem_count_bloat" in verdict["reasons"]


def test_no_bloat_gate_accepts_real_progress() -> None:
    verdict = evaluate_no_bloat_theorem_gate(
        {
            "unit_id": "ACTION_TO_EVOLUTION_BOUNDARY",
            "retired_blocker_ids": ["A2E_ACTION_FUNCTIONAL"],
            "unlocked_python_capabilities": ["typed_runtime_gate_ingestion"],
        }
    )
    assert verdict["accepted"] is True
    assert "retires_named_blocker_units" in verdict["reasons"]


def test_bidirectional_pipeline_readiness_and_promotion_gate() -> None:
    obligations_receipt = emit_normalized_obligations()
    obligations = list(obligations_receipt["obligations"])
    action_unit = next(item for item in obligations if item["unit_id"] == "ACTION_TO_EVOLUTION_BOUNDARY")
    lean_rows = ingest_lean_outcomes(
        obligations=[action_unit],
        lean_outcomes=[
            {
                "unit_id": "ACTION_TO_EVOLUTION_BOUNDARY",
                "result_class": "EXECUTABLE_AUDIT",
                "lean_check_passed": True,
                "returned_certificate_types": list(action_unit["required_certificate_types"]),
            }
        ],
    )["rows"]
    assert len(lean_rows) == 1
    assert lean_rows[0]["readiness"] == "LEAN_OUTCOME_READY"
    promotion = evaluate_closure_promotion_gate(
        unit_id="ACTION_TO_EVOLUTION_BOUNDARY",
        lean_row=lean_rows[0],
        python_receipt={
            "python_integration_proof_passed": True,
            "tests_passed": True,
            "retired_blocker_ids": ["A2E_ACTION_FUNCTIONAL"],
            "unlocked_python_capabilities": [],
        },
    )
    assert promotion["promotion_eligible"] is True
    assert promotion["promotion_outcome"] == "PROMOTED_EARNED_CLOSURE"
