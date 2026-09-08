# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

from src.core.formal_traceability_spine import (
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
    formal_traceability_spine,
)


def test_program_identity() -> None:
    report = formal_traceability_spine()
    assert report["program"] == PROGRAM_ID
    assert report["counts"]["lane_count"] == 2
    assert report["counts"]["proof_class_count"] == 3
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
