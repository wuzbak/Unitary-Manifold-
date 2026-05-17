# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/higgs_naturalness_extended.py."""
from __future__ import annotations

from src.core.higgs_naturalness_extended import (
    ADJACENCY_TRACK_LABEL,
    K_SWEEP,
    higgs_naturalness_extended_report,
    higgs_naturalness_point,
    higgs_naturalness_sweep,
    two_loop_qcd_factor,
)


def test_two_loop_qcd_factor_gt_one():
    assert two_loop_qcd_factor() > 1.0


def test_higgs_naturalness_point_shape():
    row = higgs_naturalness_point(0.10)
    assert row["verdict"] in {"PASS", "TENSION", "FALSIFIED"}
    assert row["status"] in {
        "DERIVED_PARTIAL",
        "ARCHITECTURE_LIMIT_TENSION",
        "ARCHITECTURE_LIMIT_FAILED",
    }
    assert row["M_KK_GeV"] > 0.0


def test_higgs_naturalness_sweep_length():
    rows = higgs_naturalness_sweep()
    assert len(rows) == len(K_SWEEP)


def test_higgs_naturalness_report_fields():
    report = higgs_naturalness_extended_report()
    assert report["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert report["overall_verdict"] in {"PASS", "TENSION", "FALSIFIED"}
    assert isinstance(report["closure_blocker"], str) and report["closure_blocker"]
    assert isinstance(report["blocker_owner"], str) and report["blocker_owner"]
    assert isinstance(report["stop_condition"], str) and report["stop_condition"]
