# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 588 — NP-BC-4 Sub-gap L: P8 Full Functional Space Algebraic Kernel."""
from __future__ import annotations

from pathlib import Path

import pytest

from src.core.pillar588_np_bc4_subgap_l_p8_functional import (
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    P8_NAMED_RESIDUAL_STATUS,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    PROVED_COMPONENTS,
    REMAINING_GAPS,
    SUBGAP_L_STATUS,
    VERSION,
    p8_extension_assessment,
    pillar_report,
    proved_components,
    remaining_gap_assessment,
    subgap_l_proof_state,
)


def test_pillar_identity() -> None:
    assert PILLAR_NUMBER == 588
    assert PILLAR_STATUS == "NP_BC4_SUBGAP_L_P8_FULL_FUNCTION_SPACE_KERNEL_PROVED"
    assert "P8" in PILLAR_TITLE and VERSION == "v20.1"


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("path", "lean4/UnitaryManifold/NPBC4SubgapL.lean"),
        ("theorems", 12),
        ("status", "P8_FULL_FUNCTION_SPACE_KERNEL_PROVED"),
    ],
)
def test_lean4_metadata(key: str, value: object) -> None:
    assert LEAN4_NEW_FILE[key] == value


def test_lean4_file_exists() -> None:
    assert Path(LEAN4_NEW_FILE["path"]).exists()


def test_lean4_content_mentions_1879() -> None:
    content = LEAN4_NEW_FILE["content"]
    assert "74/4=18" in content or "74/4 = 18" in content or "74; floor proxy 74/4=18" in content
    assert "79" in content and "35" in content


def test_lean4_honest_status_partial() -> None:
    assert "PARTIALLY_CLOSED" in LEAN4_NEW_FILE["honest_status"]


@pytest.mark.parametrize(
    ("key", "value"),
    [("total_previous", 262), ("total_new", 12), ("total", 274), ("NPBC4SubgapL.lean", 12)],
)
def test_theorem_count(key: str, value: int) -> None:
    assert LEAN4_THEOREM_COUNT[key] == value


def test_theorem_count_arithmetic() -> None:
    assert LEAN4_THEOREM_COUNT["total_previous"] + LEAN4_THEOREM_COUNT["total_new"] == 274


@pytest.mark.parametrize(
    ("key", "value"),
    [("kernel_proved", True), ("full_closure_achieved", False)],
)
def test_subgap_status_flags(key: str, value: object) -> None:
    assert SUBGAP_L_STATUS[key] == value


def test_subgap_status_source() -> None:
    assert "455" in SUBGAP_L_STATUS["source"] and "integer_lattice" in SUBGAP_L_STATUS["source"].lower()


def test_subgap_status_advance() -> None:
    assert "12-theorem" in SUBGAP_L_STATUS["advance_over_pillar_455"]


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("previous_status", "P8_PROVED_OVER_INTEGER_LATTICE__NAMED_RESIDUAL_FULL_FUNCTION_SPACE"),
        ("current_status", "ALGEBRAIC_KERNEL_PROVED"),
        ("integer_lattice_proof_retained", True),
        ("full_function_space_proved", False),
    ],
)
def test_named_residual_status(key: str, value: object) -> None:
    assert P8_NAMED_RESIDUAL_STATUS[key] == value


def test_named_residual_honesty_note() -> None:
    note = P8_NAMED_RESIDUAL_STATUS["honesty_note"]
    assert "would be false" in note and "k_CS - n_w² - n₂² = 0" in note


def test_proved_components_count() -> None:
    assert len(PROVED_COMPONENTS) == 12


@pytest.mark.parametrize("component", PROVED_COMPONENTS)
def test_proved_components_all_proved(component: dict[str, str]) -> None:
    assert component["status"] == "PROVED"
    assert len(component["content"]) > 15


def test_proved_components_include_honest_identity() -> None:
    assert any("honest" in c["name"].lower() or "would be false" in c["content"] for c in PROVED_COMPONENTS)


def test_proved_components_include_integer_lattice() -> None:
    assert any("integer lattice" in c["name"].lower() or "integer lattice" in c["content"].lower() for c in PROVED_COMPONENTS)


def test_proved_components_include_microstates() -> None:
    assert any("79" in c["content"] for c in PROVED_COMPONENTS)


def test_remaining_gaps_count() -> None:
    assert len(REMAINING_GAPS) == 3


@pytest.mark.parametrize("gap", REMAINING_GAPS)
def test_remaining_gap_open(gap: dict[str, str]) -> None:
    assert gap["status"] == "OPEN"
    assert len(gap["reason"]) > 20


def test_subgap_l_state_values() -> None:
    state = subgap_l_proof_state()
    assert state["subgap"] == "L"
    assert state["bc"] == "NP-BC-4"
    assert state["status"] == PILLAR_STATUS
    assert state["kernel_proved"] is True
    assert state["full_closure"] is False
    assert state["lean4_theorems"] == 12
    assert state["integer_lattice_proof_retained"] is True
    assert state["analytic_continuation_floor_proxy"] == 18


def test_p8_extension_assessment_values() -> None:
    assessment = p8_extension_assessment()
    assert assessment["pillar455_status"] == "P8_PROVED_OVER_INTEGER_LATTICE__NAMED_RESIDUAL_FULL_FUNCTION_SPACE"
    assert assessment["pillar588_status"] == "ALGEBRAIC_KERNEL_PROVED"
    assert assessment["integer_lattice_proof_retained"] is True
    assert assessment["full_function_space_proved"] is False
    assert "Infinite-dimensional" in assessment["named_residual_remaining"]
    assert "would be false" in assessment["honesty_note"]


def test_helpers_return_backing_data() -> None:
    assert proved_components() == PROVED_COMPONENTS
    assert remaining_gap_assessment() == REMAINING_GAPS


def test_pillar_report_keys() -> None:
    report = pillar_report()
    for key in ["pillar", "title", "status", "version", "lean4", "theorem_count", "subgap_l_status", "p8_named_residual_status", "proved", "remaining", "p8_extension"]:
        assert key in report


def test_pillar_report_values() -> None:
    report = pillar_report()
    assert report["pillar"] == 588
    assert report["version"] == "v20.1"
    assert report["lean4"]["theorems"] == 12
    assert report["theorem_count"]["total"] == 274
    assert report["subgap_l_status"]["kernel_proved"] is True
    assert report["p8_named_residual_status"]["current_status"] == "ALGEBRAIC_KERNEL_PROVED"
    assert len(report["proved"]) == 12
    assert len(report["remaining"]) == 3
