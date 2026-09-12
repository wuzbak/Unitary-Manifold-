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
    if epistemic_class == PROOF_CLASS_UNCONDITIONAL:
        ids = [
            "EXACT_IDENTITY",
            "INTERVAL_CERTIFIED_BOUND",
            "MONOTONICITY_CERTIFICATE",
            "RESIDUAL_CERTIFICATE",
            "TRUNCATION_DISCRETIZATION_CERTIFICATE",
        ]
    elif epistemic_class == PROOF_CLASS_CONDITIONAL:
        ids = [
            "EXACT_IDENTITY",
            "INTERVAL_CERTIFIED_BOUND",
            "MONOTONICITY_CERTIFICATE",
            "RESIDUAL_CERTIFICATE",
            "TRUNCATION_DISCRETIZATION_CERTIFICATE",
            "EXTERNAL_OBSERVATION_DEPENDENCY",
        ]
    else:
        ids = [
            "EXACT_IDENTITY",
            "INTERVAL_CERTIFIED_BOUND",
            "MONOTONICITY_CERTIFICATE",
            "RESIDUAL_CERTIFICATE",
            "TRUNCATION_DISCRETIZATION_CERTIFICATE",
            "EXTERNAL_OBSERVATION_DEPENDENCY",
        ]
    return [dict(_CERTIFICATE_MAP[item_id]) for item_id in ids]


def certificate_requirements_for_row(row: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return required certificate types for a specific traceability row."""
    row_id = str(row.get("id") or "")
    allowed = {item["id"]: item for item in certificate_types_for_proof_class(str(row.get("epistemic_class") or ""))}
    ids = _ROW_CERTIFICATE_REQUIREMENTS.get(row_id, [])
    if not ids:
        ids = [item["id"] for item in allowed.values() if item["promotion_eligible"]][:1]
    result = []
    for item_id in ids:
        if item_id in allowed:
            result.append(dict(allowed[item_id]))
        elif item_id in _CERTIFICATE_MAP:
            result.append(dict(_CERTIFICATE_MAP[item_id]))
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


__all__ = [
    "BRIDGE_ARCHITECTURE_LAYERS",
    "CANONICAL_NORMALIZATION_FIELDS",
    "CERTIFICATE_TYPES",
    "NO_FLOAT_PROMOTION_POLICY",
    "build_normalization_contract",
    "certificate_requirements_for_row",
    "certificate_types_for_proof_class",
]
