# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 590 — Lean4 274-theorem milestone."""
from __future__ import annotations

import pytest

from src.core.pillar590_lean4_274_milestone import (
    LEAN4_TOTAL,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    SPRINT_E_SUMMARY,
    SUBSTACK_POST,
    TEST_COUNT_DELTA,
    VERSION,
    lean4_advancement,
    milestone_certificate,
    np_bc_complete_summary,
    pillar_report,
    sprint_e_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 590
    assert PILLAR_STATUS == "LEAN4_274_THEOREM_MILESTONE_CERTIFIED"
    assert "274-Theorem" in PILLAR_TITLE and VERSION == "v20.1"


def test_constants() -> None:
    assert LEAN4_TOTAL == 274
    assert TEST_COUNT_DELTA == 370
    assert SUBSTACK_POST == "#277 S03E055"


def test_sprint_e_summary_list() -> None:
    assert len(SPRINT_E_SUMMARY) == 5
    assert [p["pillar"] for p in SPRINT_E_SUMMARY] == [586, 587, 588, 589, 590]


def test_sprint_e_summary_lean4_additions() -> None:
    assert [p["lean4_new"] for p in SPRINT_E_SUMMARY] == [11, 11, 12, 0, 0]


def test_sprint_e_helper() -> None:
    summary = sprint_e_summary()
    assert summary["sprint"] == "Sprint E"
    assert summary["total_tests"] == 370
    assert summary["total_lean4_theorems_added"] == 34
    assert summary["lean4_before"] == 240
    assert summary["lean4_after"] == 274
    assert summary["substack_post"] == "#277 S03E055"


def test_lean4_advancement_values() -> None:
    adv = lean4_advancement()
    assert adv["before_sprint"] == 240
    assert adv["after_sprint"] == 274
    assert adv["new_theorems"] == 34
    assert adv["np_bc4_total"] == 34
    assert len(adv["new_files"]) == 3


def test_lean4_advancement_files() -> None:
    adv = lean4_advancement()
    assert any("NPBC4SubgapJ" in f for f in adv["new_files"])
    assert any("NPBC4SubgapK" in f for f in adv["new_files"])
    assert any("NPBC4SubgapL" in f for f in adv["new_files"])


def test_np_bc_complete_summary_values() -> None:
    summary = np_bc_complete_summary()
    assert summary["total_subgaps"] == 12
    assert summary["total_subgap_theorems"] == 135
    assert summary["total_lean4_theorems"] == 274
    assert summary["max_claim"] == "ALL_TWELVE_SUBGAP_KERNELS_PROVED"
    assert summary["full_np_bc_proof"] is False


def test_np_bc_complete_summary_breakdown() -> None:
    summary = np_bc_complete_summary()
    assert summary["np_bc1"]["theorems"] == 34
    assert summary["np_bc2"]["theorems"] == 33
    assert summary["np_bc3"]["theorems"] == 34
    assert summary["np_bc4"]["theorems"] == 34
    assert summary["np_bc4"]["subgaps"] == ["J", "K", "L"]


def test_milestone_certificate_values() -> None:
    cert = milestone_certificate()
    assert cert["pillar"] == 590
    assert cert["status"] == PILLAR_STATUS
    assert cert["lean4_before"] == 240
    assert cert["lean4_after"] == 274
    assert cert["theorem_delta"] == 34
    assert cert["substack_post"] == "#277 S03E055"
    assert cert["np_bc4_complete"] is True
    assert cert["total_subgap_kernels"] == 12
    assert cert["total_subgap_theorems"] == 135


def test_milestone_certificate_files() -> None:
    cert = milestone_certificate()
    assert cert["new_files"] == [
        "lean4/UnitaryManifold/NPBC4SubgapJ.lean",
        "lean4/UnitaryManifold/NPBC4SubgapK.lean",
        "lean4/UnitaryManifold/NPBC4SubgapL.lean",
    ]


def test_milestone_certificate_honesty() -> None:
    joined = " ".join(milestone_certificate()["what_is_NOT_claimed"])
    assert "NOT a full non-perturbative gravity proof" in joined
    assert "NOT completely proved" in joined


def test_pillar_report_keys() -> None:
    report = pillar_report()
    for key in ["pillar", "title", "status", "version", "adjacent_track", "sprint_e_summary", "lean4_advancement", "np_bc_complete_summary", "milestone_certificate", "toe_score_delta", "hardgate_score_delta"]:
        assert key in report


def test_pillar_report_values() -> None:
    report = pillar_report()
    assert report["pillar"] == 590
    assert report["adjacent_track"] is False
    assert report["sprint_e_summary"]["total_lean4_theorems_added"] == 34
    assert report["lean4_advancement"]["after_sprint"] == 274
    assert report["np_bc_complete_summary"]["total_subgap_theorems"] == 135
    assert report["milestone_certificate"]["substack_post"] == "#277 S03E055"
    assert report["toe_score_delta"] == 0.0
    assert report["hardgate_score_delta"] == 0.0
