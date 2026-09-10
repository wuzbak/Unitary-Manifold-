# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from ox_navigator.engine.merlin_lean_bridge import (
    detect_lean_bridge_backends,
    get_live_theorem_count_receipt,
    get_merlin_lean_bridge_artifact,
    run_python_to_lean_bridge_receipt,
)


def test_theorem_count_receipt_uses_live_status() -> None:
    receipt = get_live_theorem_count_receipt()
    assert receipt["theorem_count"] == 4080
    assert receipt["source"] == "9-INFRASTRUCTURE/um_live_status.json"


def test_merlin_lean_bridge_artifact_contains_formal_units() -> None:
    artifact = get_merlin_lean_bridge_artifact(limit=2)
    assert artifact["artifact_id"] == "merlin_lean_bridge_artifact_v1"
    assert artifact["strategy"] == "LSP_PLUS_REPL_HYBRID"
    assert artifact["counts"]["formal_unit_count"] == 2
    assert artifact["formal_units"][0]["translation_contract"]["source_plane"] == "python_formal_unit_contract"


def test_run_python_to_lean_bridge_receipt_selects_formal_unit() -> None:
    receipt = run_python_to_lean_bridge_receipt(
        conjecture="derive n_w = 5 from first principles",
        context="review the open gap and the uniqueness burden",
        run_build=False,
    )
    assert receipt["receipt_id"] == "python_lean_bridge_receipt_v1"
    assert receipt["selected_unit_id"] in {"APS_MATHLIB_FORMALIZATION_GAP", "APS_ETA_AXIOM_HALF_CLASS"}
    assert receipt["scoped_build_receipt"]["status"] == "SKIPPED"


def test_backend_detection_contract_present() -> None:
    payload = detect_lean_bridge_backends()
    assert payload["recommended_stack"] == "LSP_PLUS_REPL_HYBRID"
    assert any(item["backend_id"] == "leaninteract_repl" for item in payload["external_backends"])
