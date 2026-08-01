# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 597 — NP-BC-5 Sub-gap N."""
from __future__ import annotations

import pytest

from src.core.pillar597_np_bc5_subgap_n_adm_momentum import (
    K_CS,
    KK_MOMENTUM_CORRECTION,
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    MOMENTUM_CONSTRAINT_COUNT,
    N_W,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    PROVED_COMPONENTS,
    VERSION,
    lean4_certificate,
    pillar_report,
    remaining_gap_assessment,
    subgap_n_proof_state,
)

PRIMARY = subgap_n_proof_state()
REPORT = pillar_report()

PRIMARY_KEYS = ["subgap", "status", "momentum_constraint_count", "kk_momentum_correction", "lean4_new_file", "lapse_shift_preserves_braid"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "subgap_n_proof_state", "proved_components", "lean4_certificate"]
NUMERIC_CHECKS = [
    N_W == 5,
    K_CS == 74,
    abs(KK_MOMENTUM_CORRECTION - 5.0 / 74.0) < 1e-12,
    MOMENTUM_CONSTRAINT_COUNT == 3,
    LEAN4_THEOREM_COUNT["total"] == 296,
    len(PROVED_COMPONENTS) == 11,
]
STRING_CHECKS = [
    PILLAR_STATUS == "NP_BC5_SUBGAP_N_ADM_MOMENTUM_KERNEL_PROVED",
    "ADM Momentum" in PILLAR_TITLE,
    VERSION == "v20.3",
    LEAN4_NEW_FILE["path"].endswith("NPBC5SubgapN.lean"),
    remaining_gap_assessment()["full_adm_quantization_complete"] is False,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 597
    assert PILLAR_STATUS == "NP_BC5_SUBGAP_N_ADM_MOMENTUM_KERNEL_PROVED"



def test_constants() -> None:
    assert PRIMARY["subgap"] == "N"
    assert PRIMARY["lapse_shift_preserves_braid"] is True
    assert lean4_certificate()["proved_components"] == 11


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
