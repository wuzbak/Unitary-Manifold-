# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/ws_i_iv_execution_programme.py."""
from __future__ import annotations

import pytest

from src.core.ws_i_iv_execution_programme import (
    EXECUTION_DATE,
    EXECUTION_ORDER,
    FULL_REGRESSION_GATE_COMMAND,
    UMBRELLA_TRACKER_ARTIFACT,
    WS_EXECUTION_PROGRAMME,
    execution_programme_summary,
    get_programme_workstream,
    list_programme_workstreams,
)


def test_execution_date_fixed():
    assert EXECUTION_DATE == "2026-05-08"


def test_execution_order_matches_plan():
    assert EXECUTION_ORDER == ["WS-II", "WS-III", "WS-I", "WS-IV"]
    assert list_programme_workstreams() == EXECUTION_ORDER


def test_umbrella_tracker_artifact_path():
    assert UMBRELLA_TRACKER_ARTIFACT == "docs/WS_I_IV_EXECUTION_PROGRAMME_ISSUE.md"


def test_has_exactly_four_workstreams():
    assert set(WS_EXECUTION_PROGRAMME.keys()) == {"WS-I", "WS-II", "WS-III", "WS-IV"}


def test_each_entry_has_required_keys():
    required = {
        "order",
        "parameter_target",
        "execution_artifact",
        "test_artifact",
        "status",
        "outcome",
        "post_freeze_action",
        "recycle_into_mas",
    }
    for ws_id, entry in WS_EXECUTION_PROGRAMME.items():
        assert required <= set(entry.keys()), f"Missing keys in {ws_id}"


def test_statuses_binary_freeze_policy():
    valid = {"PASS_FREEZE", "TARGETED_FOLLOW_UP_FREEZE"}
    for entry in WS_EXECUTION_PROGRAMME.values():
        assert entry["status"] in valid


def test_ws2_is_pass_freeze():
    assert WS_EXECUTION_PROGRAMME["WS-II"]["status"] == "PASS_FREEZE"


def test_other_workstreams_targeted_follow_up_freeze():
    for ws_id in ("WS-I", "WS-III", "WS-IV"):
        assert WS_EXECUTION_PROGRAMME[ws_id]["status"] == "TARGETED_FOLLOW_UP_FREEZE"


def test_no_recycle_into_mas_for_any_workstream():
    assert all(not entry["recycle_into_mas"] for entry in WS_EXECUTION_PROGRAMME.values())


def test_get_programme_workstream_returns_copy():
    ws1 = get_programme_workstream("WS-II")
    ws2 = get_programme_workstream("WS-II")
    ws1["status"] = "MUTATED"
    assert ws2["status"] == "PASS_FREEZE"


def test_unknown_workstream_raises():
    with pytest.raises(KeyError, match="WS-UNKNOWN"):
        get_programme_workstream("WS-UNKNOWN")


def test_summary_shape_and_counts():
    s = execution_programme_summary()
    assert s["workstream_count"] == 4
    assert s["pass_freeze_count"] == 1
    assert s["targeted_follow_up_freeze_count"] == 3
    assert s["mas_reopen_allowed"] is False
    assert s["recycle_into_mas_allowed"] is False
    assert s["all_records_no_mas_recycle"] is True


def test_summary_order_and_gate_command():
    s = execution_programme_summary()
    assert s["execution_order"] == ["WS-II", "WS-III", "WS-I", "WS-IV"]
    assert "pytest tests/ recycling/" in FULL_REGRESSION_GATE_COMMAND
    assert "test_symbolic_metric.py" in FULL_REGRESSION_GATE_COMMAND

