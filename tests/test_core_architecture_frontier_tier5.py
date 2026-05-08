# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/architecture_frontier_tier5.py."""
from __future__ import annotations

from src.core.architecture_frontier_tier5 import (
    P27_QUALITY_GAP_LOG10,
    P28_RESIDUAL_GAP_ORDERS,
    Q_PQ_GEV,
    tier5_architecture_frontier_report,
    tier5_p27_strong_cp_frontier,
    tier5_p28_lambda_frontier,
)


def test_constants_positive():
    assert Q_PQ_GEV > 0
    assert P27_QUALITY_GAP_LOG10 > 0
    assert P28_RESIDUAL_GAP_ORDERS > 0


def test_p27_packet():
    p27 = tier5_p27_strong_cp_frontier()
    assert p27["parameter"] == "P27"
    assert "ARCHITECTURE_LIMIT_CERTIFIED" in p27["status"]
    assert p27["toe_score_delta"] == 0.0


def test_p28_packet():
    p28 = tier5_p28_lambda_frontier()
    assert p28["parameter"] == "P28"
    assert p28["n_flux"] == 37
    assert p28["toe_score_delta"] == 0.0


def test_report_no_inflation():
    report = tier5_architecture_frontier_report()
    assert report["falsifier_integrity_preserved"] is True
    assert report["toe_score_delta"] == 0.0
    assert report["score_policy"] == "no_score_inflation_without_hardgate"
