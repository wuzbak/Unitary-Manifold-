# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/experiment_monitor_matrix.py."""
from __future__ import annotations

from src.core.experiment_monitor_matrix import (
    collect_monitor_reports,
    monitoring_status_table,
    hard_gate_snapshot,
    machine_readable_monitor_bundle,
)


def test_collect_monitor_reports_structure():
    reports = collect_monitor_reports()
    for key in ("version", "cmbs4", "dune", "hyperk_juno", "desi_year3"):
        assert key in reports
    assert reports["version"] == "v10.18"


def test_monitoring_status_table_structure():
    table = monitoring_status_table()
    assert isinstance(table, list)
    assert len(table) == 4
    for row in table:
        for key in ("experiment", "status", "next_milestone"):
            assert key in row


def test_hard_gate_snapshot_structure():
    snap = hard_gate_snapshot()
    for key in ("pass", "fail_count", "failures", "policy"):
        assert key in snap
    assert isinstance(snap["fail_count"], int)
    assert isinstance(snap["failures"], list)


def test_machine_readable_monitor_bundle_structure():
    bundle = machine_readable_monitor_bundle()
    for key in ("schema_version", "generated_on", "monitor_suite_version", "reports", "status_table", "hard_gate"):
        assert key in bundle
    assert bundle["monitor_suite_version"] == "v10.18"
