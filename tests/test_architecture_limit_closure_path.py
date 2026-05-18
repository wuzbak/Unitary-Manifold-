# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/architecture_limit_closure_path.py."""
from __future__ import annotations

from src.core.architecture_limit_closure_path import (
    ADJACENCY_TRACK_LABEL,
    architecture_limit_closure_path_report,
)


def test_architecture_limit_closure_path_report_shape():
    report = architecture_limit_closure_path_report()
    assert report["report_id"] == "ARCHITECTURE_LIMIT_CLOSURE_PATH"
    assert report["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert "A3" in report and "SC4" in report


def test_a3_sc4_have_blocker_owner_stop_condition():
    report = architecture_limit_closure_path_report()
    for key in ("A3", "SC4"):
        lane = report[key]
        assert isinstance(lane["closure_blocker"], str) and lane["closure_blocker"]
        assert isinstance(lane["owner"], str) and lane["owner"]
        assert isinstance(lane["stop_condition"], str) and lane["stop_condition"]
