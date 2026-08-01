# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 619 — NP-BC-6 Sub-gap Q (holographic screen kernel)."""
from __future__ import annotations

import pytest

from src.core.pillar619_np_bc6_subgap_q_holographic_screen import (
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
    SUBGAP_Q_STATUS,
    VERSION,
    lean4_certificate,
    pillar_report,
    proved_components,
    remaining_gap_assessment,
    subgap_q_proof_state,
)

PRIMARY = subgap_q_proof_state()
REPORT = pillar_report()
CERT = lean4_certificate()
GAP = remaining_gap_assessment()

PRIMARY_KEYS = ["subgap", "status", "np_bc_chain", "kernel_type", "n_w", "k_cs", "k_cs_half",
                "winding_screen_capacity", "lean4_new_file"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track",
               "subgap_q_proof_state", "proved_components", "lean4_certificate"]

NUMERIC_CHECKS = [
    N_W == 5,
    K_CS == 74,
    K_CS_HALF == 37,
    LEAN4_NEW_FILE["theorems"] == 11,
    LEAN4_THEOREM_COUNT["total"] == 330,
    LEAN4_THEOREM_COUNT["total_previous"] == 319,
    len(PROVED_COMPONENTS) == 11,
    CERT["new_theorems"] == 11,
    CERT["lean4_total_after"] == 330,
    PRIMARY["winding_screen_capacity"] == N_W * K_CS,
    PRIMARY["winding_screen_capacity"] == 370,
    PRIMARY["np_bc_chain"] == 6,
]

STRING_CHECKS = [
    PILLAR_STATUS == "NP_BC6_SUBGAP_Q_HOLOGRAPHIC_SCREEN_KERNEL_PROVED",
    SUBGAP_Q_STATUS == "HOLOGRAPHIC_SCREEN_KERNEL_PROVED",
    "Sub-gap Q" in PILLAR_TITLE,
    VERSION == "v20.7",
    LEAN4_NEW_FILE["path"].endswith("NPBC6SubgapQ.lean"),
    GAP["screen_kernel_proved"] is True,
    GAP["full_rt_formula_proved"] is False,
    REPORT["adjacent_track"] is False,
    PRIMARY["subgap"] == "Q",
    PRIMARY["kernel_type"] == "holographic_screen_entropy",
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 619
    assert PILLAR_STATUS == "NP_BC6_SUBGAP_Q_HOLOGRAPHIC_SCREEN_KERNEL_PROVED"


def test_lean4_count() -> None:
    assert LEAN4_THEOREM_COUNT["total"] == 330
    assert LEAN4_THEOREM_COUNT["total_previous"] + LEAN4_NEW_FILE["theorems"] == 330


def test_winding_screen_capacity() -> None:
    assert PRIMARY["winding_screen_capacity"] == 370


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
