# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

from src.core.closure_hardgate_registry import (
    hardgate_completion_report,
    load_hardgate_registry,
    workstream_partition,
)


def test_registry_has_expected_shape():
    registry = load_hardgate_registry()
    assert "canonical_status_tokens" in registry
    assert "gates" in registry
    assert len(registry["gates"]) >= 4


def test_workstream_partition_contains_a_and_b():
    partition = workstream_partition()
    assert "A" in partition
    assert "B" in partition
    assert len(partition["A"]) >= 1
    assert len(partition["B"]) >= 1


def test_hardgate_report_tracks_artifacts_and_tests():
    report = hardgate_completion_report(test_results={})
    assert report["gate_count"] >= 4
    assert "results" in report
    for gate_key, gate_data in report["results"].items():
        assert "artifacts_ready" in gate_data, gate_key
        assert "tests_ready" in gate_data, gate_key
        assert "complete" in gate_data, gate_key


def test_hardgate_report_none_test_results_marks_unavailable():
    report = hardgate_completion_report()
    assert report["gate_count"] >= 1
    for gate_data in report["results"].values():
        assert gate_data["tests_ready"] is False
