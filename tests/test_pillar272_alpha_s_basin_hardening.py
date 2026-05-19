# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 272 — α_s basin hardening."""
from __future__ import annotations

from src.core.pillar272_alpha_s_basin_hardening import (
    ADJACENCY_TRACK_LABEL,
    alpha_s_basin_hardening_report,
    alpha_s_basin_scan,
)


def test_basin_scan_has_expected_grid_size():
    points = alpha_s_basin_scan()
    assert len(points) == 27


def test_basin_report_has_majority_passing_points():
    report = alpha_s_basin_hardening_report()
    assert report["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert report["n_points"] == 27
    assert report["basin_fraction"] > 0.5


def test_basin_status_is_robust():
    report = alpha_s_basin_hardening_report()
    assert report["status"] == "ROBUST_BASIN_CONFIRMED"
