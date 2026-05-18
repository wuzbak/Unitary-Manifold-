# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 257 — Repository Shakedown & Reassembly Engine."""

from __future__ import annotations

import pytest

from src.core.pillar257_repository_shakedown_reassembly_engine import (
    ADJACENCY_TRACK_LABEL,
    BASELINE_REGRESSION_COMMAND,
    BASELINE_REGRESSION_COUNTS,
    BASELINE_REGRESSION_RUNTIME_SECONDS,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    baseline_regression_snapshot,
    canonical_surface_sync_check,
    decomposition_inventory,
    drift_detection_check,
    falsifier_rigidity_check,
    pillar257_repository_shakedown_report,
    reassembly_reconciliation_matrix,
    separation_guard,
    theorem_kernel_integrity_check,
)


def test_constants():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
    assert PILLAR_NUMBER == 257
    assert "Shakedown" in PILLAR_TITLE


def test_separation_guard():
    assert separation_guard() is True


def test_decomposition_inventory_structure():
    row = decomposition_inventory()
    assert row["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert row["minimum_expected_buckets"] >= 8
    assert row["complete_bucket_scan"] is True
    assert row["total_python_modules"] > 0


def test_decomposition_inventory_contains_expected_buckets():
    row = decomposition_inventory()
    buckets = row["bucket_counts"]
    for key in (
        "core",
        "holography",
        "multiverse",
        "quantum",
        "theory_docs",
        "falsification_docs",
        "outreach_docs",
        "tests",
    ):
        assert key in buckets
        assert buckets[key] >= 0


def test_theorem_kernel_integrity_is_complete():
    row = theorem_kernel_integrity_check()
    assert row["status"] == "PASS"
    assert row["is_complete"] is True
    assert row["missing_paths"] == []
    assert len(row["required_paths"]) >= 7


def test_canonical_surface_sync_shape():
    row = canonical_surface_sync_check()
    assert row["all_surfaces_present"] is True
    assert len(row["surfaces_present"]) >= 6
    assert row["missing_surfaces"] == []


def test_canonical_surface_sync_version_tags_present():
    row = canonical_surface_sync_check()
    tags = row["version_tags"]
    assert tags["status_has_v11_1"] is True
    assert tags["fallibility_has_v11_1"] is True
    assert tags["claim_board_has_v11_0_or_v11_1"] is True
    assert tags["truth_layer_has_v11_0_or_v11_1"] is True


def test_drift_detection_flags_historical_surfaces():
    row = drift_detection_check()
    assert row["mas_tracker_mixed_era_flag"] is True
    assert row["falsification_register_historical_flag"] is True
    assert row["drift_count"] >= 2
    assert row["status"] == "TENSION"


def test_falsifier_rigidity_is_enforced():
    row = falsifier_rigidity_check()
    assert row["window_enforced"] is True
    assert row["gap_enforced"] is True
    assert row["primary_falsifier_language_enforced"] is True
    assert row["status"] == "PASS"


def test_baseline_snapshot_matches_known_counts():
    row = baseline_regression_snapshot()
    assert row["command"] == BASELINE_REGRESSION_COMMAND
    assert row["counts"] == BASELINE_REGRESSION_COUNTS
    assert row["runtime_seconds"] == pytest.approx(BASELINE_REGRESSION_RUNTIME_SECONDS)
    assert row["status"] == "PASS"


def test_baseline_snapshot_no_failures():
    row = baseline_regression_snapshot()
    assert row["counts"]["failed"] == 0
    assert row["warnings_recorded"] is True


def test_reconciliation_matrix_shape():
    row = reassembly_reconciliation_matrix()
    assert "checks" in row
    assert len(row["checks"]) == 4
    assert "open_actions" in row
    assert row["open_action_count"] == len(row["open_actions"])


def test_reconciliation_matrix_has_drift_action():
    row = reassembly_reconciliation_matrix()
    assert row["status"] in {
        "RECONCILED_WITH_OPEN_DOCUMENTATION_TENSIONS",
        "FULLY_RECONCILED",
    }
    assert row["open_action_count"] >= 1


def test_integrated_report_shape():
    report = pillar257_repository_shakedown_report()
    for key in (
        "pillar",
        "title",
        "adjacency_label",
        "timestamp_utc",
        "separation_guard",
        "decomposition_inventory",
        "theorem_kernel_integrity",
        "canonical_surface_sync",
        "drift_detection",
        "falsifier_rigidity",
        "baseline_regression",
        "reassembly_reconciliation",
        "hard_fails",
        "transparency_findings",
        "overall_status",
        "non_hardgate_statement",
    ):
        assert key in report


def test_integrated_report_identity_and_guard():
    report = pillar257_repository_shakedown_report()
    assert report["pillar"] == 257
    assert report["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert report["separation_guard"] is True
    assert "does not modify hardgate claims" in report["non_hardgate_statement"]


def test_integrated_report_status_is_honest():
    report = pillar257_repository_shakedown_report()
    assert report["overall_status"] in {"PASS", "PASS_WITH_DOCUMENTATION_TENSIONS", "REJECTED"}
    assert report["overall_status"] == "PASS_WITH_DOCUMENTATION_TENSIONS"
    assert report["hard_fails"] == []
    assert len(report["transparency_findings"]) >= 1

