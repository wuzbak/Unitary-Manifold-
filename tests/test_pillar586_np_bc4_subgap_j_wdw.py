# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 586 — NP-BC-4 Sub-gap J: Wheeler-DeWitt Mini-Superspace Algebraic Kernel."""
from __future__ import annotations

from pathlib import Path

import pytest

from src.core.pillar586_np_bc4_subgap_j_wdw import (
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    PROVED_COMPONENTS,
    REMAINING_GAPS,
    SUBGAP_J_STATUS,
    VERSION,
    advancement_certificate,
    pillar_report,
    proved_components,
    remaining_gap_assessment,
    subgap_j_proof_state,
)


def test_pillar_number() -> None:
    assert PILLAR_NUMBER == 586


def test_pillar_status() -> None:
    assert PILLAR_STATUS == "NP_BC4_SUBGAP_J_WDW_MINISUPERSPACE_KERNEL_PROVED"


def test_pillar_title() -> None:
    assert "Sub-gap J" in PILLAR_TITLE and "Wheeler-DeWitt" in PILLAR_TITLE


def test_version() -> None:
    assert VERSION == "v20.1"


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("path", "lean4/UnitaryManifold/NPBC4SubgapJ.lean"),
        ("theorems", 11),
        ("status", "WDW_MINISUPERSPACE_KERNEL_PROVED"),
    ],
)
def test_lean4_metadata(key: str, value: object) -> None:
    assert LEAN4_NEW_FILE[key] == value


def test_lean4_file_exists() -> None:
    assert Path(LEAN4_NEW_FILE["path"]).exists()


def test_lean4_content_mentions_2574() -> None:
    content = LEAN4_NEW_FILE["content"]
    assert "25/74" in content and "5/74" in content


def test_lean4_honest_status_partial() -> None:
    assert "PARTIALLY_CLOSED" in LEAN4_NEW_FILE["honest_status"]


@pytest.mark.parametrize(
    ("key", "value"),
    [("total_previous", 240), ("total_new", 11), ("total", 251), ("NPBC4SubgapJ.lean", 11)],
)
def test_theorem_count(key: str, value: int) -> None:
    assert LEAN4_THEOREM_COUNT[key] == value


def test_theorem_count_arithmetic() -> None:
    assert LEAN4_THEOREM_COUNT["total_previous"] + LEAN4_THEOREM_COUNT["total_new"] == LEAN4_THEOREM_COUNT["total"]


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("kernel_proved", True),
        ("full_closure_achieved", False),
        ("depends_on_pillar", 423),
    ],
)
def test_subgap_status_flags(key: str, value: object) -> None:
    assert SUBGAP_J_STATUS[key] == value


def test_subgap_status_source() -> None:
    assert "423" in SUBGAP_J_STATUS["source"] or "WDW" in SUBGAP_J_STATUS["source"]


def test_subgap_status_statement() -> None:
    statement = SUBGAP_J_STATUS["physical_statement"]
    assert "25/74" in statement and "odd parity" in statement


def test_subgap_status_advance() -> None:
    assert "11-theorem" in SUBGAP_J_STATUS["advance_over_pillar_423"]


def test_proved_components_count() -> None:
    assert len(PROVED_COMPONENTS) == 11


@pytest.mark.parametrize("component", PROVED_COMPONENTS)
def test_proved_component_status(component: dict[str, str]) -> None:
    assert component["status"] == "PROVED"


@pytest.mark.parametrize("name", [c["name"] for c in PROVED_COMPONENTS])
def test_proved_component_names(name: str) -> None:
    assert isinstance(name, str) and len(name) > 5


def test_proved_components_have_summary() -> None:
    assert any(c["theorem"] == "np_bc4_subgap_j_wdw_kernel" for c in PROVED_COMPONENTS)


def test_proved_components_have_boundary_condition() -> None:
    assert any("boundary" in c["name"].lower() or "boundary" in c["content"].lower() for c in PROVED_COMPONENTS)


def test_proved_components_have_braid_identity() -> None:
    assert any("5²" in c["content"] or "25 + 49 = 74" in c["content"] for c in PROVED_COMPONENTS)


def test_remaining_gaps_count() -> None:
    assert len(REMAINING_GAPS) == 3


@pytest.mark.parametrize("gap", REMAINING_GAPS)
def test_remaining_gaps_open(gap: dict[str, str]) -> None:
    assert gap["status"] == "OPEN" and "reason" in gap


def test_remaining_gaps_include_functional_equation() -> None:
    assert any("functional" in gap["name"].lower() for gap in REMAINING_GAPS)


def test_subgap_j_proof_state_keys() -> None:
    state = subgap_j_proof_state()
    for key in ["subgap", "bc", "status", "kernel_proved", "full_closure", "lean4_theorems", "mini_superspace_dim", "kk_wdw_correction", "pillar423_dependency"]:
        assert key in state


def test_subgap_j_proof_state_values() -> None:
    state = subgap_j_proof_state()
    assert state["subgap"] == "J"
    assert state["bc"] == "NP-BC-4"
    assert state["status"] == PILLAR_STATUS
    assert state["kernel_proved"] is True
    assert state["full_closure"] is False
    assert state["lean4_theorems"] == 11
    assert state["mini_superspace_dim"] == 1
    assert state["kk_wdw_correction"] == "25/74"
    assert state["pillar423_dependency"] == 423


def test_helpers_return_backing_data() -> None:
    assert proved_components() == PROVED_COMPONENTS
    assert remaining_gap_assessment() == REMAINING_GAPS


def test_advancement_certificate_basics() -> None:
    cert = advancement_certificate()
    assert cert["pillar"] == 586
    assert cert["subgap"] == "J"
    assert cert["bc"] == "NP-BC-4"
    assert cert["theorems_added"] == 11
    assert cert["total_lean4_theorems"] == 251


def test_advancement_certificate_honesty() -> None:
    cert = advancement_certificate()
    joined = " ".join(cert["what_is_NOT_claimed"])
    assert "NOT solved" in joined or "NOT fully closed" in joined


def test_pillar_report_keys() -> None:
    report = pillar_report()
    for key in ["pillar", "title", "status", "version", "lean4", "theorem_count", "subgap_j_status", "proved", "remaining", "certificate"]:
        assert key in report


def test_pillar_report_values() -> None:
    report = pillar_report()
    assert report["pillar"] == 586
    assert report["version"] == "v20.1"
    assert report["lean4"]["theorems"] == 11
    assert report["theorem_count"]["total"] == 251
    assert report["subgap_j_status"]["kernel_proved"] is True
    assert len(report["proved"]) == 11
    assert len(report["remaining"]) == 3
