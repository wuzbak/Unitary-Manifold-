# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 589 — NP-BC-4 certificate."""
from __future__ import annotations

import pytest

from src.core.pillar589_np_bc4_certificate import (
    ALL_NPBC_SUMMARY,
    NP_BC4_SUMMARY,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    VERSION,
    advancement_certificate,
    all_npbc_summary,
    np_bc4_subgap_summary,
    pillar_report,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 589
    assert PILLAR_STATUS == "NP_BC4_ALL_THREE_SUBGAP_KERNELS_PROVED"
    assert "Certificate" in PILLAR_TITLE and VERSION == "v20.1"


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("all_three_subgap_kernels_proved", True),
        ("full_np_bc4_proved", False),
        ("np_bc4_total_subgap_theorems", 34),
        ("lean4_total_after_p588", 274),
    ],
)
def test_np_bc4_summary_flags(key: str, value: object) -> None:
    assert NP_BC4_SUMMARY[key] == value


@pytest.mark.parametrize(
    ("entry", "pillar", "theorems"),
    [("subgap_j", 586, 11), ("subgap_k", 587, 11), ("subgap_l", 588, 12)],
)
def test_np_bc4_subgaps(entry: str, pillar: int, theorems: int) -> None:
    assert NP_BC4_SUMMARY[entry]["pillar"] == pillar
    assert NP_BC4_SUMMARY[entry]["theorems"] == theorems


def test_np_bc4_epistemic_status_mentions_not_full() -> None:
    assert "NOT prove the full" in NP_BC4_SUMMARY["epistemic_status"]


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("total_subgap_kernels", 12),
        ("total_subgap_theorems", 135),
        ("lean4_total", 274),
        ("maximum_claim", "ALL_TWELVE_SUBGAP_KERNELS_PROVED"),
        ("full_nonperturbative_proof", False),
    ],
)
def test_all_npbc_summary_flags(key: str, value: object) -> None:
    assert ALL_NPBC_SUMMARY[key] == value


def test_all_npbc_per_series_theorems() -> None:
    assert ALL_NPBC_SUMMARY["NP-BC-1"]["theorems"] == 34
    assert ALL_NPBC_SUMMARY["NP-BC-2"]["theorems"] == 33
    assert ALL_NPBC_SUMMARY["NP-BC-3"]["theorems"] == 34
    assert ALL_NPBC_SUMMARY["NP-BC-4"]["theorems"] == 34


def test_all_npbc_theorem_sum() -> None:
    total = sum(ALL_NPBC_SUMMARY[key]["theorems"] for key in ["NP-BC-1", "NP-BC-2", "NP-BC-3", "NP-BC-4"])
    assert total == ALL_NPBC_SUMMARY["total_subgap_theorems"]


def test_np_bc4_subgap_summary_helper() -> None:
    assert np_bc4_subgap_summary() == NP_BC4_SUMMARY


def test_all_npbc_summary_helper() -> None:
    assert all_npbc_summary() == ALL_NPBC_SUMMARY


def test_certificate_values() -> None:
    cert = advancement_certificate()
    assert cert["pillar"] == 589
    assert cert["status"] == PILLAR_STATUS
    assert cert["np_bc4_total_subgap_theorems"] == 34
    assert cert["lean4_total"] == 274
    assert cert["np_bc_complete_total_subgap_theorems"] == 135
    assert cert["np_bc_complete_total_kernels"] == 12


def test_certificate_honesty() -> None:
    cert = advancement_certificate()
    joined = " ".join(cert["what_is_NOT_claimed"])
    assert "NOT fully proved" in joined
    assert "NOT closed" in joined or "NOT" in joined


def test_pillar_report_keys() -> None:
    report = pillar_report()
    for key in ["pillar", "title", "status", "version", "np_bc4_summary", "all_npbc_summary", "certificate"]:
        assert key in report


def test_pillar_report_values() -> None:
    report = pillar_report()
    assert report["pillar"] == 589
    assert report["version"] == "v20.1"
    assert report["np_bc4_summary"]["np_bc4_total_subgap_theorems"] == 34
    assert report["all_npbc_summary"]["total_subgap_theorems"] == 135
