# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

import src.core.formal_bridge_schema as formal_bridge_schema
from src.core.formal_bridge_schema import (
    BRIDGE_ARCHITECTURE_LAYERS,
    CANONICAL_NORMALIZATION_FIELDS,
    CERTIFICATE_TYPES,
    NO_FLOAT_PROMOTION_POLICY,
    build_normalization_contract,
    certificate_requirements_for_row,
    certificate_types_for_proof_class,
    validate_certificate_requirements_override,
    validate_normalization_contract_override,
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


def test_unknown_proof_class_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown proof class"):
        certificate_types_for_proof_class("LEAN_TYPO")


def test_disallowed_row_certificate_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(
        formal_bridge_schema._ROW_CERTIFICATE_REQUIREMENTS,
        "TEST_ROW",
        ["EXTERNAL_OBSERVATION_DEPENDENCY"],
    )
    with pytest.raises(ValueError, match="disallowed certificate type|not allowed for proof class"):
        certificate_requirements_for_row(
            {
                "id": "TEST_ROW",
                "epistemic_class": "LEAN_UNCONDITIONAL",
            }
        )


def test_unmapped_row_gets_no_invented_certificate_requirements() -> None:
    assert certificate_requirements_for_row(
        {
            "id": "UNMAPPED_ROW",
            "epistemic_class": "LEAN_UNCONDITIONAL",
        }
    ) == []
    assert certificate_requirements_for_row({"id": "UNMAPPED_WITHOUT_CLASS"}) == []


def test_override_validators_enforce_schema() -> None:
    row = {
        "id": "TEST_ROW",
        "epistemic_class": "LEAN_UNCONDITIONAL",
        "summary": "test row",
        "lean_symbols": [],
        "python_modules": [],
    }
    normalization = validate_normalization_contract_override(
        {},
        row=row,
        proof_class="LEAN_UNCONDITIONAL",
    )
    assert normalization["silent_aliasing_forbidden"] is True
    assert normalization["allowed_epistemic_class"] == "LEAN_UNCONDITIONAL"
    assert validate_certificate_requirements_override(
        [],
        row_id="APS_ETA_AXIOM_HALF_CLASS",
        proof_class="LEAN_CONDITIONAL_WITH_NAMED_AXIOMS",
    ) == []
    override = validate_certificate_requirements_override(
        [{"id": "EXACT_IDENTITY", "summary": "ignored", "notes": "keep"}],
        row_id="ACTION_TO_EVOLUTION_BOUNDARY",
        proof_class="LEAN_UNCONDITIONAL",
    )
    assert override == [{
        "id": "EXACT_IDENTITY",
        "summary": "Exact symbolic or algebraic identity with no floating-point dependence.",
        "promotion_eligible": True,
        "notes": "keep",
    }]
    with pytest.raises(ValueError, match="not allowed"):
        validate_certificate_requirements_override(
            [{"id": "EXTERNAL_OBSERVATION_DEPENDENCY"}],
            row_id="ACTION_TO_EVOLUTION_BOUNDARY",
            proof_class="LEAN_UNCONDITIONAL",
        )


def test_mapped_row_without_proof_class_is_rejected_cleanly() -> None:
    with pytest.raises(ValueError, match="requires an epistemic_class"):
        certificate_requirements_for_row({"id": "ACTION_TO_EVOLUTION_BOUNDARY"})


def test_duplicate_certificate_override_is_rejected() -> None:
    with pytest.raises(ValueError, match="Duplicate certificate requirement id"):
        validate_certificate_requirements_override(
            [{"id": "EXACT_IDENTITY"}, {"id": "EXACT_IDENTITY"}],
            row_id="ACTION_TO_EVOLUTION_BOUNDARY",
            proof_class="LEAN_UNCONDITIONAL",
        )
