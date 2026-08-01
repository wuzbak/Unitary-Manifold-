# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 621 — NP-BC-6 certificate."""
from __future__ import annotations

import pytest

from src.core.pillar621_np_bc6_certificate import (
    ALL_SUBGAPS_PROVED,
    CUMULATIVE_SUBGAP_THEOREMS,
    LEAN4_TOTAL,
    NP_BC6_SUBGAP_COUNT,
    NP_BC_CHAINS_COMPLETE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    VERSION,
    cumulative_subgap_summary,
    np_bc6_certificate,
    np_bc_series_progress,
    pillar_report,
)

PRIMARY = np_bc6_certificate()
REPORT = pillar_report()
CUMULATIVE = cumulative_subgap_summary()
SERIES = np_bc_series_progress()

PRIMARY_KEYS = ["pillar", "status", "subgap_count", "all_subgaps_proved",
                "new_lean4_files", "lean4_total", "np_bc_chains_complete"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track",
               "np_bc6_certificate", "cumulative_subgap_summary", "np_bc_series_progress"]

NUMERIC_CHECKS = [
    LEAN4_TOTAL == 342,
    NP_BC6_SUBGAP_COUNT == 3,
    ALL_SUBGAPS_PROVED is True,
    CUMULATIVE_SUBGAP_THEOREMS == 203,
    NP_BC_CHAINS_COMPLETE == 6,
    CUMULATIVE["np_bc6_added_theorems"] == 34,
    CUMULATIVE["cumulative_subgap_kernels"] == 18,
    CUMULATIVE["full_np_bc_series_complete"] is True,
    SERIES["cumulative_theorems"] == 203,
    SERIES["chains_complete"] == 6,
    SERIES["total_blocking_residuals"] == 18,
    len(PRIMARY["new_lean4_files"]) == 3,
    PRIMARY["np_bc_chains_complete"] == 6,
]

STRING_CHECKS = [
    PILLAR_STATUS == "NP_BC6_ALL_THREE_SUBGAP_KERNELS_PROVED",
    "NP-BC-6" in PILLAR_TITLE,
    VERSION == "v20.7",
    SERIES["maximum_claim"] == "ALL_EIGHTEEN_SUBGAP_KERNELS_PROVED",
    REPORT["adjacent_track"] is False,
    CUMULATIVE["full_np_bc_series_complete"] is True,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 621
    assert PILLAR_STATUS == "NP_BC6_ALL_THREE_SUBGAP_KERNELS_PROVED"


def test_cumulative_theorems() -> None:
    assert CUMULATIVE_SUBGAP_THEOREMS == 203
    prev = CUMULATIVE["previous_subgap_theorems"]
    added = CUMULATIVE["np_bc6_added_theorems"]
    assert prev + added == CUMULATIVE_SUBGAP_THEOREMS


def test_full_series_complete() -> None:
    assert CUMULATIVE["full_np_bc_series_complete"] is True
    assert NP_BC_CHAINS_COMPLETE == 6


def test_lean4_total_342() -> None:
    assert LEAN4_TOTAL == 342


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
