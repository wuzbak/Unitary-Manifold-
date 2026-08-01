# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 596 — NP-BC-5 Sub-gap M."""
from __future__ import annotations

import pytest

from src.core.pillar596_np_bc5_subgap_m_wdw_full_field import (
    BRAIDED_SOUND_SPEED,
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    PROVED_COMPONENTS,
    STRUCTURE_CONSTANT,
    SUBGAP_M_STATUS,
    VERSION,
    lean4_certificate,
    pillar_report,
    proved_components,
    remaining_gap_assessment,
    subgap_m_proof_state,
)

PRIMARY = subgap_m_proof_state()
REPORT = pillar_report()

PRIMARY_KEYS = ["subgap", "status", "functional_space_dimension", "kernel_dimension", "structure_constant", "lean4_new_file"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "subgap_m_proof_state", "proved_components", "lean4_certificate"]
NUMERIC_CHECKS = [
    abs(BRAIDED_SOUND_SPEED - 12.0 / 37.0) < 1e-12,
    abs(STRUCTURE_CONSTANT - (12.0 / 37.0) ** 2) < 1e-12,
    LEAN4_NEW_FILE["theorems"] == 11,
    LEAN4_THEOREM_COUNT["total"] == 285,
    len(PROVED_COMPONENTS) == 11,
    lean4_certificate()["proved_components"] == 11,
]
STRING_CHECKS = [
    PILLAR_STATUS == "NP_BC5_SUBGAP_M_WDW_FULL_FIELD_KERNEL_PROVED",
    SUBGAP_M_STATUS == "WDW_FULL_FIELD_KERNEL_PROVED",
    "Sub-gap M" in PILLAR_TITLE,
    VERSION == "v20.3",
    remaining_gap_assessment()["full_quantization_complete"] is False,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 596
    assert PILLAR_STATUS == "NP_BC5_SUBGAP_M_WDW_FULL_FIELD_KERNEL_PROVED"



def test_constants() -> None:
    assert LEAN4_NEW_FILE["path"].endswith("NPBC5SubgapM.lean")
    assert PRIMARY["functional_space_dimension"] == "infinite"
    assert PRIMARY["kernel_dimension"] == "finite"


@pytest.mark.parametrize("key", PRIMARY_KEYS)
def test_primary_keys(key: str) -> None:
    assert key in PRIMARY


@pytest.mark.parametrize("key", REPORT_KEYS)
def test_report_keys(key: str) -> None:
    assert key in REPORT


@pytest.mark.parametrize("ok", NUMERIC_CHECKS)
def test_numeric_checks(ok: bool) -> None:
    assert ok


@pytest.mark.parametrize("ok", STRING_CHECKS)
def test_string_checks(ok: bool) -> None:
    assert ok
