# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 599 — NP-BC-5 certificate."""
from __future__ import annotations

import pytest

from src.core.pillar599_np_bc5_certificate import (
    ALL_SUBGAPS_PROVED,
    CUMULATIVE_SUBGAP_THEOREMS,
    LEAN4_TOTAL,
    NP_BC5_SUBGAP_COUNT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    VERSION,
    cumulative_subgap_summary,
    np_bc5_certificate,
    np_bc_series_progress,
    pillar_report,
)

PRIMARY = np_bc5_certificate()
REPORT = pillar_report()

PRIMARY_KEYS = ["pillar", "status", "subgap_count", "all_subgaps_proved", "new_lean4_files", "lean4_total"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "np_bc5_certificate", "cumulative_subgap_summary", "np_bc_series_progress"]
NUMERIC_CHECKS = [
    LEAN4_TOTAL == 308,
    NP_BC5_SUBGAP_COUNT == 3,
    ALL_SUBGAPS_PROVED is True,
    CUMULATIVE_SUBGAP_THEOREMS == 169,
    cumulative_subgap_summary()["np_bc5_added_theorems"] == 34,
    np_bc_series_progress()["cumulative_theorems"] == 169,
]
STRING_CHECKS = [
    PILLAR_STATUS == "NP_BC5_ALL_THREE_SUBGAP_KERNELS_PROVED",
    "NP-BC-5" in PILLAR_TITLE,
    VERSION == "v20.3",
    len(PRIMARY["new_lean4_files"]) == 3,
    np_bc_series_progress()["maximum_claim"] == "ALL_FIFTEEN_SUBGAP_KERNELS_PROVED",
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 599
    assert PILLAR_STATUS == "NP_BC5_ALL_THREE_SUBGAP_KERNELS_PROVED"



def test_constants() -> None:
    assert PRIMARY["all_subgaps_proved"] is True
    assert REPORT["hardgate_score_delta"] == 0.0
    assert cumulative_subgap_summary()["full_np_bc_series_complete"] is False


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
