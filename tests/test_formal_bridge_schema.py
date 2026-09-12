# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.formal_bridge_schema import (
    BRIDGE_ARCHITECTURE_LAYERS,
    CANONICAL_NORMALIZATION_FIELDS,
    CERTIFICATE_TYPES,
    NO_FLOAT_PROMOTION_POLICY,
    build_normalization_contract,
    certificate_requirements_for_row,
    certificate_types_for_proof_class,
)


def test_bridge_architecture_and_no_float_policy() -> None:
    assert len(BRIDGE_ARCHITECTURE_LAYERS) == 4
    assert BRIDGE_ARCHITECTURE_LAYERS[0]["id"] == "EXACT_MATHEMATICAL_SPECIFICATION"
    assert BRIDGE_ARCHITECTURE_LAYERS[-1]["id"] == "LEAN_CHECKING"
    assert NO_FLOAT_PROMOTION_POLICY["raw_floats_do_not_promote"] is True
    assert "interval enclosure" in NO_FLOAT_PROMOTION_POLICY["promotion_requires_one_of"]


def test_certificate_vocab_and_normalization_contract() -> None:
    assert {item["id"] for item in CERTIFICATE_TYPES} == {
        "EXACT_IDENTITY",
        "INTERVAL_CERTIFIED_BOUND",
        "RESIDUAL_CERTIFICATE",
        "MONOTONICITY_CERTIFICATE",
        "TRUNCATION_DISCRETIZATION_CERTIFICATE",
        "EXTERNAL_OBSERVATION_DEPENDENCY",
    }
    row = {
        "id": "ACTION_TO_EVOLUTION_BOUNDARY",
        "epistemic_class": "EXECUTABLE_PYTHON_VALIDATION",
        "summary": "The evolution engine is currently a tested honesty boundary.",
        "lean_symbols": ["ca_trace_kernel_12"],
        "python_modules": ["src/core/evolution.py"],
    }
    contract = build_normalization_contract(row)
    assert len(CANONICAL_NORMALIZATION_FIELDS) == 7
    assert contract["silent_aliasing_forbidden"] is True
    assert contract["allowed_epistemic_class"] == "EXECUTABLE_PYTHON_VALIDATION"
    assert contract["symbol_sources"]["lean_symbols"] == ["ca_trace_kernel_12"]


def test_certificate_requirements_follow_proof_class_and_row() -> None:
    unconditional = certificate_types_for_proof_class("LEAN_UNCONDITIONAL")
    executable = certificate_types_for_proof_class("EXECUTABLE_PYTHON_VALIDATION")
    assert any(item["id"] == "EXACT_IDENTITY" for item in unconditional)
    assert any(item["id"] == "EXACT_IDENTITY" for item in executable)

    action_row = {
        "id": "ACTION_TO_EVOLUTION_BOUNDARY",
        "epistemic_class": "EXECUTABLE_PYTHON_VALIDATION",
    }
    requirements = certificate_requirements_for_row(action_row)
    assert [item["id"] for item in requirements] == [
        "EXACT_IDENTITY",
        "RESIDUAL_CERTIFICATE",
        "TRUNCATION_DISCRETIZATION_CERTIFICATE",
    ]
