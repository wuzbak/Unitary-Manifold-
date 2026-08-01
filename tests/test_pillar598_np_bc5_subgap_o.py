# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 598 — NP-BC-5 Sub-gap O."""
from __future__ import annotations

import pytest

from src.core.pillar598_np_bc5_subgap_o_p8_spectral_gap import (
    K_CS,
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    N_W,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    PROVED_COMPONENTS,
    SPECTRAL_GAP_LOWER_BOUND,
    VERSION,
    lean4_certificate,
    pillar_report,
    remaining_gap_assessment,
    subgap_o_proof_state,
)

PRIMARY = subgap_o_proof_state()
REPORT = pillar_report()

PRIMARY_KEYS = ["subgap", "status", "spectral_gap_lower_bound", "bound_type", "lean4_new_file", "full_hilbert_space_gap_closed"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "subgap_o_proof_state", "proved_components", "lean4_certificate"]
NUMERIC_CHECKS = [
    N_W == 5,
    K_CS == 74,
    abs(SPECTRAL_GAP_LOWER_BOUND - (5.0 / 74.0) ** 2) < 1e-12,
    LEAN4_THEOREM_COUNT["total"] == 308,
    LEAN4_NEW_FILE["theorems"] == 12,
    len(PROVED_COMPONENTS) == 12,
]
STRING_CHECKS = [
    PILLAR_STATUS == "NP_BC5_SUBGAP_O_P8_SPECTRAL_GAP_KERNEL_PROVED",
    "Spectral Gap" in PILLAR_TITLE,
    VERSION == "v20.3",
    PRIMARY["bound_type"] == "lower_bound_only",
    remaining_gap_assessment()["full_p8_theorem_complete"] is False,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 598
    assert PILLAR_STATUS == "NP_BC5_SUBGAP_O_P8_SPECTRAL_GAP_KERNEL_PROVED"



def test_constants() -> None:
    assert 0.004 < SPECTRAL_GAP_LOWER_BOUND < 0.005
    assert LEAN4_NEW_FILE["path"].endswith("NPBC5SubgapO.lean")
    assert lean4_certificate()["proved_components"] == 12


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
