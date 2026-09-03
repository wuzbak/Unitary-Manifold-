# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1020 — three-program open architecture registry."""

from __future__ import annotations

from src.core.pillar1020_three_program_open_architecture_registry import (
    ALL_OPEN_LANES,
    BOOKKEEPING_PROGRAM_ORDER,
    EXTERNAL_WAIT_LANES,
    OPEN_ARCHITECTURE_LANES,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    PRACTICAL_PRIORITY_ORDER,
    finish_path_execution_packet,
    pillar1020_summary,
    three_program_open_architecture_registry,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1020
    assert PILLAR_GATE == "THREE_PROGRAM_OPEN_ARCHITECTURE_REGISTRY"
    assert PILLAR_STATUS == "THREE_PROGRAM_OPEN_ARCHITECTURE_REGISTRY_COMPLETE"
    assert PILLAR_VALID is True


def test_registry_shape_and_lane_cover() -> None:
    report = three_program_open_architecture_registry()
    assert report["n_programs"] == 3
    assert report["n_lanes"] == 6
    assert report["all_lanes_covered_once"] is True
    assert report["unchanged_open_labels"] is True


def test_bookkeeping_and_practical_priority_are_both_explicit() -> None:
    report = three_program_open_architecture_registry()
    assert report["bookkeeping_program_order"] == BOOKKEEPING_PROGRAM_ORDER
    assert report["practical_priority_order"] == PRACTICAL_PRIORITY_ORDER
    assert report["program_number_is_not_execution_priority"] is True
    assert PRACTICAL_PRIORITY_ORDER[0] == "PROGRAM_3_SHARED_FLAVOR_GEOMETRY"


def test_cmb_program_keeps_non_fitted_binary_rule() -> None:
    program = three_program_open_architecture_registry()["programs"][0]
    assert program["program_id"] == "PROGRAM_1_CMB_NORMALIZATION_MECHANISM"
    assert program["current_runtime_status"] == "CMB_AMP_CONFIRMED_IRREDUCIBLE"
    assert program["binary_success_criteria"]["uses_external_as_target"] is False
    assert program["binary_success_criteria"]["new_fit_knobs_added"] == 0


def test_uv_program_is_shared_dual_lane() -> None:
    program = three_program_open_architecture_registry()["programs"][1]
    assert program["program_id"] == "PROGRAM_2_SHARED_UV_COMPACTIFICATION"
    assert program["lanes"] == [
        "ALPHA_S_TYPE_B_FLOOR",
        "HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW",
    ]
    assert "UV_HIGGS_MASS_GENERATING_OPERATOR" in program["shared_missing_objects"]
    assert program["binary_success_criteria"]["must_improve_alpha_s_and_higgs_together"] is True


def test_flavor_program_is_root_first() -> None:
    program = three_program_open_architecture_registry()["programs"][2]
    assert program["program_id"] == "PROGRAM_3_SHARED_FLAVOR_GEOMETRY"
    assert program["practical_priority_rank"] == 1
    assert program["binary_success_criteria"]["root_object_first"] == (
        "GLOBAL_FLAVOR_BUNDLE_WITH_NONLOCAL_OVERLAP_TENSOR"
    )
    assert program["binary_success_criteria"]["jarlskog_cannot_be_run_as_standalone_rescue_first"] is True


def test_open_lane_labels_match_expected_set() -> None:
    report = three_program_open_architecture_registry()
    flattened = [lane for program in report["programs"] for lane in program["lanes"]]
    assert sorted(flattened) == sorted(OPEN_ARCHITECTURE_LANES)


def test_summary() -> None:
    summary = pillar1020_summary()
    assert summary["pillar"] == 1020
    assert summary["valid"] is True
    assert summary["bookkeeping_program_order"] == BOOKKEEPING_PROGRAM_ORDER


def test_finish_path_execution_packet_contract() -> None:
    packet = finish_path_execution_packet()
    assert packet["has_clear_path"] is True
    assert packet["internal_attackable_lanes"] == OPEN_ARCHITECTURE_LANES
    assert packet["external_wait_lanes"] == EXTERNAL_WAIT_LANES
    assert packet["open_lanes"] == ALL_OPEN_LANES
    assert packet["hardest_internal_blocker"] == "CMB_AMP_CONFIRMED_IRREDUCIBLE"
    assert packet["registry_valid"] is True


def test_finish_path_execution_sequence_is_strict() -> None:
    packet = finish_path_execution_packet()
    sequence = packet["execution_sequence"]
    assert [row["step"] for row in sequence] == [1, 2, 3, 4, 5, 6]
    assert sequence[1]["program_id"] == "PROGRAM_3_SHARED_FLAVOR_GEOMETRY"
    assert sequence[2]["program_id"] == "PROGRAM_2_SHARED_UV_COMPACTIFICATION"
    assert sequence[3]["program_id"] == "PROGRAM_1_CMB_NORMALIZATION_MECHANISM"
    assert sequence[3]["forbid_external_as_target"] is True
    assert sequence[3]["forbid_new_fit_knobs"] is True
    assert sequence[4]["status_promotion_requires_runtime_change"] is True
