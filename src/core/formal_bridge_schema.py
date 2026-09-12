# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Canonical normalization and certificate schema for the Python↔Lean bridge."""

from __future__ import annotations

from typing import Any, Dict, List

PROOF_CLASS_UNCONDITIONAL = "LEAN_UNCONDITIONAL"
PROOF_CLASS_CONDITIONAL = "LEAN_CONDITIONAL_WITH_NAMED_AXIOMS"
PROOF_CLASS_EXECUTABLE = "EXECUTABLE_PYTHON_VALIDATION"

BRIDGE_ARCHITECTURE_LAYERS: List[Dict[str, str]] = [
    {
        "id": "EXACT_MATHEMATICAL_SPECIFICATION",
        "name": "Exact mathematical specification",
        "responsibility": "Fix theorem statement, variables, domains, and assumptions before translation.",
    },
    {
        "id": "NORMALIZATION_TRANSLATION",
        "name": "Normalization / translation",
        "responsibility": "Normalize symbols, units, regularity, and statement shape across Python, Lean, and review surfaces.",
    },
    {
        "id": "CERTIFICATE_LAYER",
        "name": "Certificate layer",
        "responsibility": "Carry exact identities, bounds, residuals, monotonicity witnesses, truncation controls, and external-dependency markers.",
    },
    {
        "id": "LEAN_CHECKING",
        "name": "Lean checking layer",
        "responsibility": "Check only normalized claims with explicit certificate semantics and preserved proof-class boundaries.",
    },
]

CANONICAL_NORMALIZATION_FIELDS: List[Dict[str, str]] = [
    {"field": "symbol_names", "meaning": "Canonical Python/Lean/manuscript symbol mapping."},
    {"field": "parameter_meanings", "meaning": "Physical or geometric interpretation of each symbol."},
    {"field": "units_and_conventions", "meaning": "Named unit system and normalization convention."},
    {"field": "domains", "meaning": "Variable domains, admissible ranges, and function spaces."},
    {"field": "regularity_assumptions", "meaning": "Required differentiability, integrability, or Sobolev regularity."},
    {"field": "theorem_statement", "meaning": "Normalized proposition text with no silent notation drift."},
    {"field": "epistemic_class", "meaning": "Allowed proof class for promotion and reporting."},
]

CERTIFICATE_TYPES: List[Dict[str, Any]] = [
    {
        "id": "EXACT_IDENTITY",
        "summary": "Exact symbolic or algebraic identity with no floating-point dependence.",
        "promotion_eligible": True,
    },
    {
        "id": "INTERVAL_CERTIFIED_BOUND",
        "summary": "Bound established by explicit interval enclosure or equivalent exact bounding surface.",
        "promotion_eligible": True,
    },
    {
        "id": "RESIDUAL_CERTIFICATE",
        "summary": "Named operator residual or mismatch certificate on a stated domain.",
        "promotion_eligible": True,
    },
    {
        "id": "MONOTONICITY_CERTIFICATE",
        "summary": "Monotonicity or sign-control witness with explicit domain and assumptions.",
        "promotion_eligible": True,
    },
    {
        "id": "TRUNCATION_DISCRETIZATION_CERTIFICATE",
        "summary": "Explicit truncation, discretization, or approximation control surface.",
        "promotion_eligible": True,
    },
    {
        "id": "EXTERNAL_OBSERVATION_DEPENDENCY",
        "summary": "Marker that a claim depends on external observational input and is not first-principles closure.",
        "promotion_eligible": False,
    },
]

NO_FLOAT_PROMOTION_POLICY: Dict[str, Any] = {
    "raw_floats_do_not_promote": True,
    "forbidden_inputs": [
        "raw floating-point output",
        "unbounded numerical fit",
        "implicit discretization drift",
    ],
    "promotion_requires_one_of": [
        "exact symbolic normalization",
        "rational reconstruction",
        "interval enclosure",
        "formally stated perturbation theorem",
        "explicit residual bound against a named operator",
    ],
    "summary": (
        "Numerical execution may guide exploration, but it may not strengthen a claim class "
        "without an explicit certificate surface."
    ),
}

_CERTIFICATE_MAP = {item["id"]: item for item in CERTIFICATE_TYPES}
_DEFAULT_CERTIFICATE_IDS = [item["id"] for item in CERTIFICATE_TYPES]

_ROW_CERTIFICATE_REQUIREMENTS: Dict[str, List[str]] = {
    "APS_ETA_AXIOM_HALF_CLASS": ["EXTERNAL_OBSERVATION_DEPENDENCY"],
    "APS_MATHLIB_FORMALIZATION_GAP": ["EXTERNAL_OBSERVATION_DEPENDENCY"],
    "DIRAC_ORBIFOLD_PROXY_BOUNDARY": [
        "TRUNCATION_DISCRETIZATION_CERTIFICATE",
        "RESIDUAL_CERTIFICATE",
    ],
    "ACTION_TO_EVOLUTION_BOUNDARY": [
        "EXACT_IDENTITY",
        "RESIDUAL_CERTIFICATE",
        "TRUNCATION_DISCRETIZATION_CERTIFICATE",
    ],
}


def certificate_types_for_proof_class(epistemic_class: str) -> List[Dict[str, Any]]:
    """Return allowed certificate types for a proof class."""
    if epistemic_class in {
        PROOF_CLASS_UNCONDITIONAL,
        PROOF_CLASS_CONDITIONAL,
        PROOF_CLASS_EXECUTABLE,
    }:
        ids = list(_DEFAULT_CERTIFICATE_IDS)
    else:
        raise ValueError(f"Unknown proof class: {epistemic_class}")
    return [dict(_CERTIFICATE_MAP[item_id]) for item_id in ids]


def certificate_requirements_for_row(row: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return required certificate types for a specific traceability row."""
    row_id = str(row.get("id") or "")
    ids = _ROW_CERTIFICATE_REQUIREMENTS.get(row_id, [])
    if not ids:
        return []
    proof_class = str(row.get("epistemic_class") or "").strip()
    if not proof_class:
        raise ValueError(
            f"Row {row_id or '<unknown>'} requires an epistemic_class before certificate requirements can be resolved"
        )
    allowed = {item["id"]: item for item in certificate_types_for_proof_class(proof_class)}
    result = []
    for item_id in ids:
        if item_id in allowed:
            result.append(dict(allowed[item_id]))
        else:
            raise ValueError(
                f"Row {row_id or '<unknown>'} requires disallowed certificate type {item_id}"
            )
    return result


def build_normalization_contract(row: Dict[str, Any]) -> Dict[str, Any]:
    """Return the canonical normalization contract for a theorem-bearing row."""
    proof_class = str(row.get("epistemic_class") or "")
    return {
        "field_registry": list(CANONICAL_NORMALIZATION_FIELDS),
        "silent_aliasing_forbidden": True,
        "normalized_theorem_statement": str(row.get("summary") or ""),
        "allowed_epistemic_class": proof_class,
        "units_policy": "Planck/natural units unless an explicit local override is named.",
        "domain_policy": "Every promoted claim must state domain, admissible range, and function-space boundary.",
        "regularity_policy": "Every promoted claim must state required differentiability/integrability assumptions explicitly.",
        "symbol_sources": {
            "lean_symbols": list(row.get("lean_symbols") or []),
            "python_modules": list(row.get("python_modules") or []),
        },
    }


def validate_normalization_contract_override(
    override: Dict[str, Any],
    *,
    row: Dict[str, Any],
    proof_class: str,
) -> Dict[str, Any]:
    """Validate an explicit normalization override against the canonical schema."""
    if not isinstance(override, dict):
        raise TypeError("normalization_contract override must be a dict")
    canonical = build_normalization_contract(row)
    field_registry = list(override.get("field_registry") or [])
    known_fields = {item["field"] for item in CANONICAL_NORMALIZATION_FIELDS}
    override_fields = {str(item.get("field") or "") for item in field_registry if isinstance(item, dict)}
    if override_fields and not override_fields <= known_fields:
        unknown = sorted(override_fields - known_fields)
        raise ValueError(f"Unknown normalization fields: {unknown}")
    override_class = override.get("allowed_epistemic_class")
    if override_class is not None and str(override_class) != proof_class:
        raise ValueError("normalization_contract override changes the row proof class")
    supported_keys = {
        "field_registry",
        "normalized_theorem_statement",
        "allowed_epistemic_class",
        "silent_aliasing_forbidden",
        "units_policy",
        "domain_policy",
        "regularity_policy",
        "symbol_sources",
        "notes",
    }
    unknown_keys = set(override) - supported_keys
    if unknown_keys:
        raise ValueError(f"Unsupported normalization override keys: {sorted(unknown_keys)}")
    merged = dict(canonical)
    for key in supported_keys:
        if key in override:
            merged[key] = override[key]
    merged["silent_aliasing_forbidden"] = True
    merged["allowed_epistemic_class"] = proof_class
    return merged


def validate_certificate_requirements_override(
    requirements: List[Dict[str, Any]],
    *,
    row_id: str,
    proof_class: str,
) -> List[Dict[str, Any]]:
    """Validate an explicit row-specific certificate override."""
    if not isinstance(requirements, list):
        raise TypeError("certificate_requirements override must be a list")
    if not str(proof_class).strip():
        if not requirements and row_id not in _ROW_CERTIFICATE_REQUIREMENTS:
            return []
        raise ValueError(
            f"Row {row_id or '<unknown>'} needs a valid proof_class before override certificate requirements can be resolved"
        )
    allowed_ids = {
        item["id"] for item in certificate_types_for_proof_class(proof_class)
    }
    row_allowed_ids = (
        set(_ROW_CERTIFICATE_REQUIREMENTS[row_id])
        if row_id in _ROW_CERTIFICATE_REQUIREMENTS
        else set(allowed_ids)
    )
    result = []
    seen_ids: set[str] = set()
    for item in requirements:
        if not isinstance(item, dict):
            raise TypeError("certificate_requirements override entries must be dicts")
        item_id = str(item.get("id") or "")
        if item_id in seen_ids:
            raise ValueError(f"Duplicate certificate requirement id: {item_id or '<missing>'}")
        if item_id not in allowed_ids:
            raise ValueError(
                f"Certificate requirement {item_id or '<missing>'} is not allowed for proof class {proof_class}"
            )
        if item_id not in row_allowed_ids:
            raise ValueError(
                f"Certificate requirement {item_id or '<missing>'} is not allowed for row {row_id or '<unknown>'}"
            )
        canonical = dict(_CERTIFICATE_MAP[item_id])
        if "notes" in item:
            canonical["notes"] = str(item["notes"])
        result.append(canonical)
        seen_ids.add(item_id)
    return result


__all__ = [
    "BRIDGE_ARCHITECTURE_LAYERS",
    "CANONICAL_NORMALIZATION_FIELDS",
    "CERTIFICATE_TYPES",
    "NO_FLOAT_PROMOTION_POLICY",
    "build_normalization_contract",
    "certificate_requirements_for_row",
    "certificate_types_for_proof_class",
    "validate_certificate_requirements_override",
    "validate_normalization_contract_override",
]
