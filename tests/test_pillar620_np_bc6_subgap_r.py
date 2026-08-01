# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 620 — NP-BC-6 Sub-gap R (ER=EPR bridge kernel)."""
from __future__ import annotations

import pytest

from src.core.pillar620_np_bc6_subgap_r_erepr_bridge import (
    ALL_THREE_NP_BC6_SUBGAPS_PROVED,
    BLOCKING_RESIDUAL,
    K_CS,
    K_CS_HALF,
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    N_2,
    N_W,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    PROVED_COMPONENTS,
    SUBGAP_R_STATUS,
    VERSION,
    lean4_certificate,
    np_bc6_milestone,
    pillar_report,
    proved_components,
    remaining_gap_assessment,
    subgap_r_proof_state,
)

PRIMARY = subgap_r_proof_state()
REPORT = pillar_report()
CERT = lean4_certificate()
GAP = remaining_gap_assessment()
MILESTONE = np_bc6_milestone()

PRIMARY_KEYS = ["subgap", "status", "np_bc_chain", "kernel_type", "n_w", "n_2",
                "k_cs", "k_cs_half", "braid_condensate", "bridge_capacity", "lean4_new_file"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track",
               "subgap_r_proof_state", "proved_components", "lean4_certificate", "np_bc6_milestone"]

NUMERIC_CHECKS = [
    N_W == 5,
    N_2 == 7,
    K_CS == 74,
    K_CS_HALF == 37,
    LEAN4_NEW_FILE["theorems"] == 12,
    LEAN4_THEOREM_COUNT["total"] == 342,
    LEAN4_THEOREM_COUNT["total_previous"] == 330,
    len(PROVED_COMPONENTS) == 12,
    CERT["new_theorems"] == 12,
    CERT["lean4_total_after"] == 342,
    PRIMARY["braid_condensate"] == 74,        # 5² + 7² = 74
    PRIMARY["bridge_capacity"] == 370,        # 5 × 74 = 370
    MILESTONE["theorems_in_np_bc6"] == 34,   # 11+11+12
    len(MILESTONE["np_bc6_subgaps"]) == 3,
    ALL_THREE_NP_BC6_SUBGAPS_PROVED is True,
    PRIMARY["np_bc_chain"] == 6,
]

STRING_CHECKS = [
    PILLAR_STATUS == "NP_BC6_SUBGAP_R_EREPR_BRIDGE_KERNEL_PROVED",
    SUBGAP_R_STATUS == "EREPR_BRIDGE_KERNEL_PROVED",
    "Sub-gap R" in PILLAR_TITLE,
    VERSION == "v20.7",
    LEAN4_NEW_FILE["path"].endswith("NPBC6SubgapR.lean"),
    GAP["erepr_bridge_kernel_proved"] is True,
    GAP["full_np_erepr_proved"] is False,
    GAP["all_np_bc6_subgaps_proved"] is True,
    CERT["all_three_np_bc6_subgaps_proved"] is True,
    MILESTONE["milestone"] == "ALL_THREE_NP_BC6_SUBGAP_KERNELS_PROVED",
    REPORT["adjacent_track"] is False,
    PRIMARY["subgap"] == "R",
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 620
    assert PILLAR_STATUS == "NP_BC6_SUBGAP_R_EREPR_BRIDGE_KERNEL_PROVED"


def test_lean4_count_342() -> None:
    assert LEAN4_THEOREM_COUNT["total"] == 342
    assert LEAN4_THEOREM_COUNT["total_previous"] + LEAN4_NEW_FILE["theorems"] == 342


def test_braid_condensate() -> None:
    assert PRIMARY["braid_condensate"] == N_W ** 2 + N_2 ** 2 == 74


def test_all_np_bc6_subgaps_proved() -> None:
    assert ALL_THREE_NP_BC6_SUBGAPS_PROVED is True


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
