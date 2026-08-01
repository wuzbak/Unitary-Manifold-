# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 618 — NP-BC-6 Sub-gap P (KK loop kernel)."""
from __future__ import annotations

import pytest

from src.core.pillar618_np_bc6_subgap_p_kk_loop import (
    BLOCKING_RESIDUAL,
    K_CS,
    K_CS_HALF,
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    N_W,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    PROVED_COMPONENTS,
    SUBGAP_P_STATUS,
    VERSION,
    lean4_certificate,
    pillar_report,
    proved_components,
    remaining_gap_assessment,
    subgap_p_proof_state,
)

PRIMARY = subgap_p_proof_state()
REPORT = pillar_report()
CERT = lean4_certificate()
GAP = remaining_gap_assessment()

PRIMARY_KEYS = ["subgap", "status", "np_bc_chain", "kernel_type", "n_w", "k_cs", "lean4_new_file"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track",
               "subgap_p_proof_state", "proved_components", "lean4_certificate"]

NUMERIC_CHECKS = [
    N_W == 5,
    K_CS == 74,
    K_CS_HALF == 37,
    LEAN4_NEW_FILE["theorems"] == 11,
    LEAN4_THEOREM_COUNT["total"] == 319,
    LEAN4_THEOREM_COUNT["total_previous"] == 308,
    len(PROVED_COMPONENTS) == 11,
    CERT["new_theorems"] == 11,
    CERT["lean4_total_after"] == 319,
    CERT["proved_components"] == 11,
    PRIMARY["np_bc_chain"] == 6,
]

STRING_CHECKS = [
    PILLAR_STATUS == "NP_BC6_SUBGAP_P_KK_LOOP_KERNEL_PROVED",
    SUBGAP_P_STATUS == "KK_LOOP_KERNEL_PROVED",
    "Sub-gap P" in PILLAR_TITLE,
    VERSION == "v20.7",
    LEAN4_NEW_FILE["path"].endswith("NPBC6SubgapP.lean"),
    GAP["loop_kernel_proved"] is True,
    GAP["full_loop_integral_proved"] is False,
    REPORT["adjacent_track"] is False,
    PRIMARY["subgap"] == "P",
    PRIMARY["kernel_type"] == "KK_loop_correction",
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 618
    assert PILLAR_STATUS == "NP_BC6_SUBGAP_P_KK_LOOP_KERNEL_PROVED"


def test_lean4_theorem_count() -> None:
    assert LEAN4_THEOREM_COUNT["total"] == 319
    assert LEAN4_THEOREM_COUNT["total_previous"] + LEAN4_NEW_FILE["theorems"] == LEAN4_THEOREM_COUNT["total"]


def test_all_components() -> None:
    assert len(proved_components()) == 11


def test_no_toe_delta() -> None:
    assert REPORT["toe_score_delta"] == 0.0


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
