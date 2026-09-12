# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.lean_python_bridge_ir import (
    build_python_lean_bridge_contract,
    get_python_lean_bridge_contract,
)


def test_python_lean_bridge_contract_structure() -> None:
    contract = get_python_lean_bridge_contract()
    assert contract["contract_id"] == "python_lean_hybrid_bridge_v1"
    assert contract["strategy"] == "LSP_PLUS_REPL_HYBRID"
    assert len(contract["tiers"]) == 3
    assert len(contract["bridge_architecture"]) == 4
    assert len(contract["certificate_types"]) == 6
    assert contract["no_float_promotion_rule"]["raw_floats_do_not_promote"] is True
    assert any(item["backend_id"] == "leanclient_lsp" for item in contract["backend_comparison"])
    assert any(unit["lean"]["module_name"].startswith("UnitaryManifold.") for unit in contract["formal_units"])
    assert any(
        unit["translation_contract"]["preferred_execution_mode"] == "lsp_plus_scoped_build"
        for unit in contract["formal_units"]
    )
    action_unit = next(unit for unit in contract["formal_units"] if unit["unit_id"] == "ACTION_TO_EVOLUTION_BOUNDARY")
    assert len(action_unit["work_queue"]) == 7
    assert action_unit["translation_contract"]["normalization_contract"]["silent_aliasing_forbidden"] is True
    assert any(
        item["id"] == "TRUNCATION_DISCRETIZATION_CERTIFICATE"
        for item in action_unit["translation_contract"]["certificate_contract"]["required_certificate_types"]
    )


def test_empty_row_overrides_are_preserved() -> None:
    contract = build_python_lean_bridge_contract(
        rows=[
            {
                "id": "TEST_UNIT",
                "lane_id": "LANE_TEST",
                "kind": "open_gap",
                "epistemic_class": "EXECUTABLE_PYTHON_VALIDATION",
                "summary": "test row",
                "review_packet": "proof/FORMAL_PROOF_FOUNDRY.md",
                "python_modules": [],
                "tests": [],
                "status_entries": [],
                "lean_file": "lean4/UnitaryManifold/SprintCAFormalTraceability.lean",
                "lean_symbols": [],
                "normalization_contract": {},
                "certificate_requirements": [],
                "work_queue": [],
            }
        ],
        primary_lanes=[{"id": "LANE_TEST", "title": "Test lane"}],
        runtime_alignment={"mode": "MANUAL_PORT_WITH_TRACEABILITY"},
    )
    unit = contract["formal_units"][0]
    assert unit["translation_contract"]["normalization_contract"] == {}
    assert unit["translation_contract"]["certificate_contract"]["required_certificate_types"] == []
