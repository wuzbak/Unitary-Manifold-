# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/flux_landscape_extended_scan.py."""
from __future__ import annotations

from src.core.flux_landscape_extended_scan import (
    ADJACENCY_TRACK_LABEL,
    N_FLUX_REQUIRED_MIN,
    N_FLUX_SCAN_VALUES,
    classify_sc4_point,
    residual_log10_ratio,
    scan_flux_landscape,
    sc4_closure_summary,
)


def test_residual_log10_ratio_is_finite_positive():
    assert residual_log10_ratio(37) >= 0.0
    assert residual_log10_ratio(100) >= 0.0


def test_classify_sc4_point_pass():
    assert classify_sc4_point(61, 0.25) == "PASS"


def test_classify_sc4_point_tension():
    assert classify_sc4_point(10, 0.31) == "TENSION"


def test_effective_flux_threshold_changes_verdict():
    # With dual-flux multiplicity, n_flux=31 gives effective_n_flux=62 >= 61.
    r30 = residual_log10_ratio(30)
    r31 = residual_log10_ratio(31)
    assert classify_sc4_point(30, r30) == "TENSION"
    assert classify_sc4_point(31, r31) == "PASS"


def test_scan_flux_landscape_shape():
    rows = scan_flux_landscape()
    assert len(rows) == len(N_FLUX_SCAN_VALUES)
    assert all("n_flux" in r and "verdict" in r for r in rows)
    assert all("effective_n_flux" in r for r in rows)


def test_summary_has_explicit_blocker_owner_stop_condition():
    s = sc4_closure_summary()
    assert s["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert s["required_n_flux_min"] == N_FLUX_REQUIRED_MIN
    assert s["status"] in {"CLOSED_WITH_EFFECTIVE_FLUX_CHANNELS", "ARCHITECTURE_LIMIT"}
    assert isinstance(s["closure_blocker"], str) and s["closure_blocker"]
    assert isinstance(s["blocker_owner"], str) and s["blocker_owner"]
    assert isinstance(s["stop_condition"], str) and s["stop_condition"]
