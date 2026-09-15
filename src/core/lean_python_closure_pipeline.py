# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Closure-first bidirectional Python↔Lean execution pipeline."""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.lean_python_bridge_ir import get_python_lean_bridge_contract

NO_BLOAT_THEOREM_GATE_VERSION = "NO_BLOAT_THEOREM_GATE_V1"


def _string_list(values: Any) -> List[str]:
    if not isinstance(values, list):
        return []
    result: List[str] = []
    for item in values:
        text = str(item or "").strip()
        if text:
            result.append(text)
    return result


def evaluate_no_bloat_theorem_gate(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """Accept theorem additions only when they retire blockers or unlock runtime capability."""
    unit_id = str(candidate.get("unit_id") or "").strip()
    retired_blockers = _string_list(candidate.get("retired_blocker_ids"))
    unlocked_capabilities = _string_list(candidate.get("unlocked_python_capabilities"))
    accepted = bool(retired_blockers or unlocked_capabilities)
    reasons = []
    if retired_blockers:
        reasons.append("retires_named_blocker_units")
    if unlocked_capabilities:
        reasons.append("unlocks_concrete_python_runtime_or_checking_capability")
    if not reasons:
        reasons.append("rejected_as_theorem_count_bloat")
    return {
        "gate_version": NO_BLOAT_THEOREM_GATE_VERSION,
        "unit_id": unit_id,
        "accepted": accepted,
        "retired_blocker_ids": retired_blockers,
        "unlocked_python_capabilities": unlocked_capabilities,
        "reasons": reasons,
    }


def emit_normalized_obligations() -> Dict[str, Any]:
    """Emit normalized formal obligations from the canonical bridge contract."""
    contract = get_python_lean_bridge_contract()
    obligations = []
    for unit in list(contract.get("formal_units") or []):
        translation_contract = dict(unit.get("translation_contract") or {})
        obligations.append(
            {
                "unit_id": str(unit.get("unit_id") or ""),
                "lane_id": str(unit.get("lane_id") or ""),
                "proof_class": str(unit.get("proof_class") or ""),
                "lean_target": str((unit.get("lean") or {}).get("build_target") or ""),
                "python_modules": list((unit.get("python") or {}).get("modules") or []),
                "python_tests": list((unit.get("python") or {}).get("tests") or []),
                "status_entries": list((unit.get("python") or {}).get("status_entries") or []),
                "work_queue": list(unit.get("work_queue") or []),
                "normalization_contract": dict(translation_contract.get("normalization_contract") or {}),
                "required_certificate_types": list(
                    (translation_contract.get("certificate_contract") or {}).get("required_certificate_types") or []
                ),
                "allowed_result_classes": list(translation_contract.get("allowed_result_classes") or []),
            }
        )
    return {
        "pipeline_id": "python_lean_bidirectional_execution_v1",
        "source_contract_id": str(contract.get("contract_id") or ""),
        "obligations": obligations,
        "counts": {
            "obligation_count": len(obligations),
        },
    }


def ingest_lean_outcomes(
    *,
    obligations: List[Dict[str, Any]],
    lean_outcomes: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Ingest Lean outcomes and classify per-unit closure readiness."""
    obligation_map = {str(item.get("unit_id") or ""): item for item in list(obligations or [])}
    rows = []
    for outcome in list(lean_outcomes or []):
        unit_id = str(outcome.get("unit_id") or "").strip()
        obligation = obligation_map.get(unit_id, {})
        allowed = set(_string_list(obligation.get("allowed_result_classes")))
        result_class = str(outcome.get("result_class") or "").strip()
        result_class_allowed = bool(result_class and result_class in allowed)
        returned_certificate_ids = {
            str(item.get("id") or "") for item in list(outcome.get("returned_certificate_types") or []) if isinstance(item, dict)
        }
        required_certificate_ids = {
            str(item.get("id") or "") for item in list(obligation.get("required_certificate_types") or []) if isinstance(item, dict)
        }
        required_certificates_present = required_certificate_ids <= returned_certificate_ids
        lean_check_passed = bool(outcome.get("lean_check_passed"))
        readiness = (
            "LEAN_OUTCOME_READY"
            if result_class_allowed and required_certificates_present and lean_check_passed
            else "LEAN_OUTCOME_BLOCKED"
        )
        rows.append(
            {
                "unit_id": unit_id,
                "result_class": result_class,
                "result_class_allowed": result_class_allowed,
                "required_certificates_present": required_certificates_present,
                "lean_check_passed": lean_check_passed,
                "readiness": readiness,
                "missing_required_certificate_ids": sorted(required_certificate_ids - returned_certificate_ids),
            }
        )
    return {
        "pipeline_id": "python_lean_bidirectional_execution_v1",
        "rows": rows,
        "summary": {
            "ready_units": sum(1 for row in rows if row.get("readiness") == "LEAN_OUTCOME_READY"),
            "blocked_units": sum(1 for row in rows if row.get("readiness") != "LEAN_OUTCOME_READY"),
        },
    }


def evaluate_closure_promotion_gate(
    *,
    unit_id: str,
    lean_row: Dict[str, Any],
    python_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    """Require Lean + Python + tests + blocker/capability evidence for promotion."""
    retired_blockers = _string_list(python_receipt.get("retired_blocker_ids"))
    unlocked_capabilities = _string_list(python_receipt.get("unlocked_python_capabilities"))
    python_integration_proof = bool(python_receipt.get("python_integration_proof_passed"))
    tests_passed = bool(python_receipt.get("tests_passed"))
    lean_ready = str(lean_row.get("readiness") or "") == "LEAN_OUTCOME_READY"
    evidence_ok = bool(retired_blockers or unlocked_capabilities)
    promoted = lean_ready and python_integration_proof and tests_passed and evidence_ok
    return {
        "unit_id": str(unit_id or "").strip(),
        "lean_outcome_ready": lean_ready,
        "python_integration_proof_passed": python_integration_proof,
        "tests_passed": tests_passed,
        "retired_blocker_ids": retired_blockers,
        "unlocked_python_capabilities": unlocked_capabilities,
        "promotion_eligible": promoted,
        "promotion_outcome": "PROMOTED_EARNED_CLOSURE" if promoted else "BLOCKED_OR_CONDITIONAL_ONLY",
    }


__all__ = [
    "NO_BLOAT_THEOREM_GATE_VERSION",
    "emit_normalized_obligations",
    "evaluate_closure_promotion_gate",
    "evaluate_no_bloat_theorem_gate",
    "ingest_lean_outcomes",
]
