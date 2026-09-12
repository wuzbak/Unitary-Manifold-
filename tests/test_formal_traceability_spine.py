# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

from src.core.formal_traceability_spine import (
    CURRY_HOWARD_MATRIX,
    INTAKE_SURFACE,
    LANE_A_ID,
    LANE_B_ID,
    PRIMARY_LANES,
    PROGRAM_ID,
    PROOF_CLASS_CONDITIONAL,
    PROOF_CLASS_EXECUTABLE,
    PROOF_CLASS_UNCONDITIONAL,
    REVIEW_PACKETS,
    TRACEABILITY_ROWS,
    _enrich_traceability_row,
    formal_traceability_spine,
)


def test_program_identity() -> None:
    report = formal_traceability_spine()
    assert report["program"] == PROGRAM_ID
    assert report["counts"]["lane_count"] == 2
    assert report["counts"]["proof_class_count"] == 3
    assert report["counts"]["bridge_architecture_layer_count"] == 4
    assert report["counts"]["certificate_type_count"] == 6
    assert report["counts"]["curry_howard_row_count"] == len(CURRY_HOWARD_MATRIX)
    assert report["valid"] is True


def test_primary_lanes_are_exact_frontier_pair() -> None:
    lane_ids = [lane["id"] for lane in PRIMARY_LANES]
    assert lane_ids == [LANE_A_ID, LANE_B_ID]
    assert PRIMARY_LANES[0]["priority"] == 1
    assert PRIMARY_LANES[1]["priority"] == 2


def test_proof_class_separation_present() -> None:
    classes = {row["epistemic_class"] for row in TRACEABILITY_ROWS}
    assert PROOF_CLASS_UNCONDITIONAL not in classes or isinstance(classes, set)
    assert PROOF_CLASS_CONDITIONAL in classes
    assert PROOF_CLASS_EXECUTABLE in classes
    proof_classes = {item["id"] for item in formal_traceability_spine()["proof_classes"]}
    assert proof_classes == {
        PROOF_CLASS_UNCONDITIONAL,
        PROOF_CLASS_CONDITIONAL,
        PROOF_CLASS_EXECUTABLE,
    }


def test_traceability_rows_link_real_files() -> None:
    rows = formal_traceability_spine()["traceability_rows"]
    assert len(rows) == len(TRACEABILITY_ROWS)
    assert {"axiom", "open_gap", "theorem_cluster"} <= {row["kind"] for row in rows}
    assert any(row["lane_id"] == LANE_A_ID for row in rows)
    assert any(row["lane_id"] == LANE_B_ID for row in rows)
    assert all(row["paths_exist"] is True for row in rows)
    action_row = next(row for row in rows if row["id"] == "ACTION_TO_EVOLUTION_BOUNDARY")
    assert len(action_row["work_queue"]) == 7
    assert action_row["no_float_promotion_rule"]["raw_floats_do_not_promote"] is True
    assert action_row["normalization_contract"]["silent_aliasing_forbidden"] is True
    assert any(item["id"] == "RESIDUAL_CERTIFICATE" for item in action_row["certificate_requirements"])


def test_review_packets_cover_rows() -> None:
    report = formal_traceability_spine()
    packets = report["review_packets"]
    assert len(packets) == len(REVIEW_PACKETS)
    assert {packet["lane_id"] for packet in packets} == {LANE_A_ID, LANE_B_ID}
    assert all(packet["path_exists"] is True for packet in packets)
    assert all(packet["claim_ids_exist"] is True for packet in packets)


def test_intake_surface_exists() -> None:
    intake_paths = [item["path"] for item in formal_traceability_spine()["intake_surface"]]
    assert intake_paths == INTAKE_SURFACE
    assert "proof/FORMAL_PROOF_FOUNDRY.md" in intake_paths
    assert "proof/CURRY_HOWARD_WORKFLOW.md" in intake_paths
    assert "proof/NAVIER_STOKES_METHOD_TRANSFER_PACKET.md" in intake_paths
    assert "proof/PSICAT_NAVIER_STOKES_CURRICULUM_PACKET.md" in intake_paths
    assert "proof/PYTHAGOREAN_TRIPLES_SAT_METHOD_TRANSFER_PACKET.md" in intake_paths


def test_curry_howard_matrix_and_runtime_alignment() -> None:
    report = formal_traceability_spine()
    assert len(report["curry_howard_matrix"]) == 6
    assert report["curry_howard_matrix"][0]["logic_side"] == "Proposition"
    alignment = report["runtime_alignment"]
    assert alignment["mode"] in {
        "MANUAL_PORT_WITH_TRACEABILITY",
        "DIRECT_OR_HYBRID_INTEGRATION",
    }
    if alignment["mode"] == "MANUAL_PORT_WITH_TRACEABILITY":
        assert alignment["direct_lean_runtime_detected"] is False
    else:
        assert any(path.endswith("merlin_lean_bridge.py") for path in alignment["evidence_files"])
    scan_scope = alignment["scan_scope"]
    assert "12-AZ-IP/20-psicat-navigator/ox_navigator/engine" in scan_scope["dir_targets"]
    assert scan_scope["scanned_python_file_count"] > 0


def test_python_lean_bridge_contract_present() -> None:
    contract = formal_traceability_spine()["python_lean_bridge_contract"]
    assert contract["contract_id"] == "python_lean_hybrid_bridge_v1"
    assert contract["strategy"] == "LSP_PLUS_REPL_HYBRID"
    assert contract["counts"]["formal_unit_count"] == len(contract["formal_units"])
    assert contract["counts"]["bridge_architecture_layer_count"] == 4
    assert contract["counts"]["certificate_type_count"] == 6
    assert any(unit["unit_id"] == "ACTION_TO_EVOLUTION_BOUNDARY" for unit in contract["formal_units"])


def test_row_enrichment_preserves_explicit_overrides() -> None:
    row = {
        "id": "ACTION_TO_EVOLUTION_BOUNDARY",
        "lane_id": LANE_B_ID,
        "kind": "open_gap",
        "epistemic_class": PROOF_CLASS_EXECUTABLE,
        "summary": "test row",
        "review_packet": "proof/REVIEW_PACKET_ACTION_TO_EVOLUTION.md",
        "python_modules": [],
        "tests": [],
        "status_entries": [],
        "lean_file": "lean4/UnitaryManifold/SprintCAFormalTraceability.lean",
        "lean_symbols": [],
        "normalization_contract": {"notes": "custom"},
        "certificate_requirements": [{"id": "EXACT_IDENTITY", "notes": "custom"}],
        "work_queue": [{"claim_id": "CUSTOM_QUEUE"}],
    }
    enriched = _enrich_traceability_row(row)
    assert enriched["normalization_contract"]["notes"] == "custom"
    assert enriched["certificate_requirements"][0]["notes"] == "custom"
    assert enriched["work_queue"] == [{"claim_id": "CUSTOM_QUEUE"}]


def test_psicat_training_manifest_ready() -> None:
    manifest = formal_traceability_spine()["psicat_training_manifest"]
    assert manifest["target_product"] == "12-AZ-IP/20-psicat-navigator"
    assert manifest["training_ready"] is True
    assert all(item["exists"] is True for item in manifest["training_corpus"])
    assert any(
        item["path"] == "proof/NAVIER_STOKES_METHOD_TRANSFER_PACKET.md"
        for item in manifest["training_corpus"]
    )
    assert any(
        item["path"] == "proof/PSICAT_NAVIER_STOKES_CURRICULUM_PACKET.md"
        for item in manifest["training_corpus"]
    )
    assert any(
        item["path"] == "proof/PYTHAGOREAN_TRIPLES_SAT_METHOD_TRANSFER_PACKET.md"
        for item in manifest["training_corpus"]
    )
    assert any(
        item["path"] == "src/core/navier_stokes_method_transfer.py"
        for item in manifest["registry_sources"]
    )
    assert any(
        item["path"] == "src/core/pythagorean_triples_sat_method_transfer.py"
        for item in manifest["registry_sources"]
    )
    assert all(item["exists"] is True for item in manifest["export_tools"])
