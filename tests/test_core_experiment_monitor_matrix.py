# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/experiment_monitor_matrix.py."""
from __future__ import annotations

from src.core.experiment_monitor_matrix import (
    collect_monitor_reports,
    monitoring_status_table,
    high_priority_action_queue,
    overdue_priority_actions,
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
    assert len(table) == 5
    for row in table:
        for key in ("experiment", "status", "next_milestone"):
            assert key in row


def test_high_priority_action_queue_structure():
    queue = high_priority_action_queue()
    assert isinstance(queue, list)
    assert len(queue) == 5
    for row in queue:
        for key in ("id", "priority", "trigger", "status", "deadline_policy", "action"):
            assert key in row


def test_high_priority_action_queue_contains_desi_and_litebird():
    ids = {row["id"] for row in high_priority_action_queue()}
    assert "DESI_Y3_30_DAY_ROUTING" in ids
    assert "LITEBIRD_PRIMARY_FALSIFIER_READY" in ids


def test_overdue_priority_actions_detects_stale_entries():
    stale = overdue_priority_actions(
        last_updated={
            "DESI_Y3_30_DAY_ROUTING": "2026-01-01",
            "CMBS4_MONITOR_SYNC": "2026-05-01",
        },
        today="2026-05-08",
    )
    stale_ids = {row["id"] for row in stale}
    assert "DESI_Y3_30_DAY_ROUTING" in stale_ids
    assert "CMBS4_MONITOR_SYNC" not in stale_ids


def test_hard_gate_snapshot_structure():
    snap = hard_gate_snapshot()
    for key in ("pass", "fail_count", "failures", "policy"):
        assert key in snap
    assert isinstance(snap["fail_count"], int)
    assert isinstance(snap["failures"], list)


def test_machine_readable_monitor_bundle_structure():
    bundle = machine_readable_monitor_bundle()
    for key in (
        "schema_version",
        "generated_on",
        "monitor_suite_version",
        "reports",
        "status_table",
        "high_priority_queue",
        "overdue_actions",
        "hard_gate",
    ):
        assert key in bundle
    assert bundle["monitor_suite_version"] == "v10.18"
