# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Deterministic Python↔Lean bridge contracts for proof-foundry units."""

from __future__ import annotations

from typing import Any

from src.core.formal_bridge_schema import (
    BRIDGE_ARCHITECTURE_LAYERS,
    CANONICAL_NORMALIZATION_FIELDS,
    CERTIFICATE_TYPES,
    NO_FLOAT_PROMOTION_POLICY,
    build_normalization_contract,
    certificate_requirements_for_row,
    certificate_types_for_proof_class,
)

_BACKEND_COMPARISON: list[dict[str, str]] = [
    {
        "backend_id": "leanclient_lsp",
        "primary_mechanism": "lean_lsp_wrapper",
        "core_use_case": "fast batch diagnostics, symbol queries, and file-level edits",
        "role_in_pipeline": "Tier-B static analysis lane",
    },
    {
        "backend_id": "leaninteract_repl",
        "primary_mechanism": "lean_repl_abstraction",
        "core_use_case": "scoped execution, temporary projects, and proof-state capture",
        "role_in_pipeline": "Tier-B scoped execution lane",
    },
    {
        "backend_id": "leandojo_dataset",
        "primary_mechanism": "proof_state_extraction_and_ml_corpus",
        "core_use_case": "dataset extraction, training, and automated theorem-proving research",
        "role_in_pipeline": "Tier-C training and evaluation augmentation",
    },
    {
        "backend_id": "leancall_ffi",
        "primary_mechanism": "direct_function_binding",
        "core_use_case": "later-stage stable kernel invocation with narrow signatures",
        "role_in_pipeline": "Deferred acceleration path only",
    },
]


def _lean_module_name(lean_file: str) -> str:
    rel = str(lean_file or "").strip()
    if not rel.startswith("lean4/") or not rel.endswith(".lean"):
        return ""
    stem = rel[len("lean4/") : -len(".lean")]
    return stem.replace("/", ".")


def _lean_project_relative_file(lean_file: str) -> str:
    rel = str(lean_file or "").strip()
    if not rel.startswith("lean4/"):
        return ""
    return rel[len("lean4/") :]


def _allowed_result_classes(epistemic_class: str) -> list[str]:
    mapping = {
        "LEAN_UNCONDITIONAL": ["UNCONDITIONAL_THEOREM", "BUILD_FAILURE", "ENVIRONMENT_BLOCKED"],
        "LEAN_CONDITIONAL_WITH_NAMED_AXIOMS": ["CONDITIONAL_THEOREM", "BUILD_FAILURE", "ENVIRONMENT_BLOCKED"],
        "EXECUTABLE_PYTHON_VALIDATION": ["EXECUTABLE_AUDIT", "MISMATCH_CERTIFICATE", "ENVIRONMENT_BLOCKED"],
    }
    return list(mapping.get(epistemic_class, ["ENVIRONMENT_BLOCKED"]))


def build_formal_unit_ir(
    *,
    rows: list[dict[str, Any]],
    primary_lanes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Convert traceability rows into deterministic translation units."""
    lane_titles = {
        str(item.get("id") or ""): str(item.get("title") or "")
        for item in list(primary_lanes or [])
    }
    units: list[dict[str, Any]] = []
    for row in list(rows or []):
        unit_id = str(row.get("id") or "").strip()
        if not unit_id:
            continue
        lean_file = str(row.get("lean_file") or "")
        lean_module = _lean_module_name(lean_file)
        proof_class = str(row.get("epistemic_class") or "")
        lane_id = str(row.get("lane_id") or "")
        normalization_contract = (
            dict(row["normalization_contract"])
            if "normalization_contract" in row and row.get("normalization_contract") is not None
            else build_normalization_contract(row)
        )
        certificate_requirements = (
            list(row["certificate_requirements"])
            if "certificate_requirements" in row and row.get("certificate_requirements") is not None
            else certificate_requirements_for_row(row)
        )
        unit = {
            "unit_id": unit_id,
            "lane_id": lane_id,
            "lane_title": lane_titles.get(lane_id, ""),
            "kind": str(row.get("kind") or ""),
            "proof_class": proof_class,
            "summary": str(row.get("summary") or ""),
            "review_packet": str(row.get("review_packet") or ""),
            "work_queue": list(row.get("work_queue") or []),
            "python": {
                "modules": list(row.get("python_modules") or []),
                "tests": list(row.get("tests") or []),
                "status_entries": list(row.get("status_entries") or []),
            },
            "lean": {
                "file": lean_file,
                "module_name": lean_module,
                "project_relative_file": _lean_project_relative_file(lean_file),
                "build_target": lean_module,
                "check_target": _lean_project_relative_file(lean_file),
                "symbols": list(row.get("lean_symbols") or []),
            },
            "translation_contract": {
                "bridge_layers": list(BRIDGE_ARCHITECTURE_LAYERS),
                "source_plane": "python_formal_unit_contract",
                "target_plane": "lean_checked_artifact",
                "return_plane": "python_receipt_reingestion",
                "preferred_execution_mode": (
                    "scoped_repl_with_receipt"
                    if proof_class == "EXECUTABLE_PYTHON_VALIDATION"
                    else "lsp_plus_scoped_build"
                ),
                "allowed_result_classes": _allowed_result_classes(proof_class),
                "normalization_contract": normalization_contract,
                "certificate_contract": {
                    "required_certificate_types": certificate_requirements,
                    "allowed_certificate_types_for_proof_class": certificate_types_for_proof_class(proof_class),
                    "no_float_promotion_rule": dict(NO_FLOAT_PROMOTION_POLICY),
                },
                "promotion_guardrail": (
                    "Returned Python receipts must preserve the exact Lean proof class and may not inflate "
                    "closure beyond the checked artifact."
                ),
            },
        }
        units.append(unit)
    return units


def build_python_lean_bridge_contract(
    *,
    rows: list[dict[str, Any]],
    primary_lanes: list[dict[str, Any]],
    runtime_alignment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the canonical bridge contract for machine-to-machine interaction."""
    units = build_formal_unit_ir(rows=rows, primary_lanes=primary_lanes)
    alignment = dict(runtime_alignment or {})
    return {
        "contract_id": "python_lean_hybrid_bridge_v1",
        "strategy": "LSP_PLUS_REPL_HYBRID",
        "runtime_alignment_mode": str(alignment.get("mode") or "MANUAL_PORT_WITH_TRACEABILITY"),
        "bridge_architecture": list(BRIDGE_ARCHITECTURE_LAYERS),
        "normalization_dictionary": {
            "field_registry": list(CANONICAL_NORMALIZATION_FIELDS),
            "silent_aliasing_forbidden": True,
        },
        "certificate_types": list(CERTIFICATE_TYPES),
        "no_float_promotion_rule": dict(NO_FLOAT_PROMOTION_POLICY),
        "tiers": [
            {
                "tier": "A",
                "name": "python_orchestration",
                "responsibility": "emit formal-unit contracts, choose bridge mode, and re-ingest receipts",
            },
            {
                "tier": "B",
                "name": "lean_interaction_substrate",
                "responsibility": "batch diagnostics via LSP-class tools plus scoped REPL/build execution",
            },
            {
                "tier": "C",
                "name": "training_and_reporting",
                "responsibility": "route receipts into PsiCat, tests, review packets, and truth surfaces",
            },
        ],
        "backend_comparison": list(_BACKEND_COMPARISON),
        "governance": {
            "native_pipeline_rule": "Textual translation alone is never semantic proof equivalence.",
            "promotion_rule": "Only structured Lean receipts may strengthen downstream Python claims.",
            "fallback_rule": "Dataset-extraction and FFI layers are secondary to stable LSP/REPL execution.",
        },
        "formal_units": units,
        "counts": {
            "formal_unit_count": len(units),
            "lane_count": len(list(primary_lanes or [])),
            "bridge_architecture_layer_count": len(BRIDGE_ARCHITECTURE_LAYERS),
            "certificate_type_count": len(CERTIFICATE_TYPES),
        },
    }


def get_python_lean_bridge_contract() -> dict[str, Any]:
    """Convenience wrapper around the canonical traceability spine."""
    from src.core.formal_traceability_spine import formal_traceability_spine

    snapshot = formal_traceability_spine()
    return build_python_lean_bridge_contract(
        rows=list(snapshot.get("traceability_rows") or []),
        primary_lanes=list(snapshot.get("primary_lanes") or []),
        runtime_alignment=dict(snapshot.get("runtime_alignment") or {}),
    )


__all__ = [
    "build_formal_unit_ir",
    "build_python_lean_bridge_contract",
    "get_python_lean_bridge_contract",
]
