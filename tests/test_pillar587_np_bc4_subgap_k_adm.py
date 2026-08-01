# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 587 — NP-BC-4 Sub-gap K: ADM Inhomogeneous Non-Perturbative Algebraic Kernel."""
from __future__ import annotations

from pathlib import Path

import pytest

from src.core.pillar587_np_bc4_subgap_k_adm import (
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    PROVED_COMPONENTS,
    REMAINING_GAPS,
    SUBGAP_K_STATUS,
    VERSION,
    pillar_report,
    proved_components,
    remaining_gap_assessment,
    subgap_k_proof_state,
)


def test_pillar_identity() -> None:
    assert PILLAR_NUMBER == 587
    assert PILLAR_STATUS == "NP_BC4_SUBGAP_K_ADM_INHOMOGENEOUS_KERNEL_PROVED"
    assert "ADM" in PILLAR_TITLE and VERSION == "v20.1"


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("path", "lean4/UnitaryManifold/NPBC4SubgapK.lean"),
        ("theorems", 11),
        ("status", "ADM_INHOMOGENEOUS_KERNEL_PROVED"),
    ],
)
def test_lean4_metadata(key: str, value: object) -> None:
    assert LEAN4_NEW_FILE[key] == value


def test_lean4_file_exists() -> None:
    assert Path(LEAN4_NEW_FILE["path"]).exists()


def test_lean4_content_mentions_adm() -> None:
    content = LEAN4_NEW_FILE["content"]
    assert "4" in content and "5/74" in content and "25/74" in content


def test_lean4_honest_status_partial() -> None:
    assert "PARTIALLY_CLOSED" in LEAN4_NEW_FILE["honest_status"]


@pytest.mark.parametrize(
    ("key", "value"),
    [("total_previous", 251), ("total_new", 11), ("total", 262), ("NPBC4SubgapK.lean", 11)],
)
def test_theorem_count(key: str, value: int) -> None:
    assert LEAN4_THEOREM_COUNT[key] == value


def test_theorem_count_arithmetic() -> None:
    assert LEAN4_THEOREM_COUNT["total_previous"] + LEAN4_THEOREM_COUNT["total_new"] == 262


@pytest.mark.parametrize(
    ("key", "value"),
    [("kernel_proved", True), ("full_closure_achieved", False)],
)
def test_subgap_status_flags(key: str, value: object) -> None:
    assert SUBGAP_K_STATUS[key] == value


def test_subgap_status_statement() -> None:
    assert "5/74" in SUBGAP_K_STATUS["physical_statement"]


def test_subgap_status_advance_statement() -> None:
    assert "11-theorem" in SUBGAP_K_STATUS["advance_statement"]


def test_proved_components_count() -> None:
    assert len(PROVED_COMPONENTS) == 11


@pytest.mark.parametrize("component", PROVED_COMPONENTS)
def test_proved_components_all_proved(component: dict[str, str]) -> None:
    assert component["status"] == "PROVED"
    assert component["theorem"]
    assert len(component["content"]) > 20


def test_proved_components_include_constraint_count() -> None:
    assert any("20" in c["content"] for c in PROVED_COMPONENTS)


def test_proved_components_include_mass_gap() -> None:
    assert any("25/74" in c["content"] for c in PROVED_COMPONENTS)


def test_remaining_gaps_count() -> None:
    assert len(REMAINING_GAPS) == 3


@pytest.mark.parametrize("gap", REMAINING_GAPS)
def test_remaining_gap_open(gap: dict[str, str]) -> None:
    assert gap["status"] == "OPEN"
    assert len(gap["reason"]) > 15


def test_remaining_gap_mentions_continuum() -> None:
    assert any("continuum" in g["name"].lower() or "continuum" in g["reason"].lower() for g in REMAINING_GAPS)


def test_subgap_k_state_keys() -> None:
    state = subgap_k_proof_state()
    for key in ["subgap", "bc", "status", "kernel_proved", "full_closure", "lean4_theorems", "constraint_count_proxy", "scalar_bound"]:
        assert key in state


def test_subgap_k_state_values() -> None:
    state = subgap_k_proof_state()
    assert state == {
        "subgap": "K",
        "bc": "NP-BC-4",
        "status": PILLAR_STATUS,
        "kernel_proved": True,
        "full_closure": False,
        "lean4_theorems": 11,
        "constraint_count_proxy": 20,
        "scalar_bound": "5/74",
    }


def test_helpers_return_backing_data() -> None:
    assert proved_components() == PROVED_COMPONENTS
    assert remaining_gap_assessment() == REMAINING_GAPS


def test_pillar_report_keys() -> None:
    report = pillar_report()
    for key in ["pillar", "title", "status", "version", "lean4", "theorem_count", "subgap_k_status", "proved", "remaining"]:
        assert key in report


def test_pillar_report_values() -> None:
    report = pillar_report()
    assert report["pillar"] == 587
    assert report["version"] == "v20.1"
    assert report["lean4"]["theorems"] == 11
    assert report["theorem_count"]["total"] == 262
    assert report["subgap_k_status"]["kernel_proved"] is True
    assert len(report["proved"]) == 11
    assert len(report["remaining"]) == 3
