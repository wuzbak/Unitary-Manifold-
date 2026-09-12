# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.lean_python_bridge_ir import get_python_lean_bridge_contract


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
