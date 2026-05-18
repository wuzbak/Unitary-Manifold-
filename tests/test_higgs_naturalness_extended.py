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
    three_loop_mixed_factor,
    two_loop_qcd_factor,
    uv_counterterm_factor,
)


def test_loop_factors_gt_one():
    assert two_loop_qcd_factor() > 1.0
    assert three_loop_mixed_factor() > 1.0


def test_uv_counterterm_factor_bounded():
    f = uv_counterterm_factor(1e54)
    assert 0.0 < f < 1.0


def test_higgs_naturalness_point_shape():
    row = higgs_naturalness_point(0.10)
    assert row["verdict"] in {"PASS", "TENSION", "FALSIFIED"}
    assert row["status"] in {
        "DERIVED_COMPLETE",
        "DERIVED_WITH_TENSION",
        "ARCHITECTURE_LIMIT_FAILED",
    }
    assert row["M_KK_GeV"] > 0.0
    assert "delta_renormalized" in row
    assert "uv_completion_closed" in row


def test_higgs_naturalness_sweep_length():
    rows = higgs_naturalness_sweep()
    assert len(rows) == len(K_SWEEP)


def test_higgs_naturalness_report_fields():
    report = higgs_naturalness_extended_report()
    assert report["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert report["overall_verdict"] in {"PASS", "TENSION", "FALSIFIED"}
    assert report["overall_status"] in {"DERIVED_COMPLETE", "DERIVED_WITH_RESIDUAL"}
    assert isinstance(report["scheme_spread"], float)
    assert isinstance(report["kk_cutoff_all_points"], bool)
    assert isinstance(report["closure_blocker"], str) and report["closure_blocker"]
    assert isinstance(report["blocker_owner"], str) and report["blocker_owner"]
    assert isinstance(report["stop_condition"], str) and report["stop_condition"]
