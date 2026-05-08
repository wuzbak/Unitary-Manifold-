# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/alpha_gw_casimir_closure.py."""
from __future__ import annotations

from src.core.alpha_gw_casimir_closure import (
    ALPHA_GW_LOWER,
    ALPHA_GW_UPPER,
    SUPPRESSION_TARGET,
    alpha_gw_bound_from_geometry,
    alpha_gw_closure_certificate,
    as_consistency_window,
)


def test_bounds_ordered():
    assert ALPHA_GW_LOWER < ALPHA_GW_UPPER


def test_target_positive():
    assert SUPPRESSION_TARGET > 0


def test_bound_shape():
    bound = alpha_gw_bound_from_geometry()
    assert bound["k_cs"] == 74
    assert bound["n_w"] == 5
    assert bound["bound_width"] > 0


def test_as_window_within_factor_5():
    window = as_consistency_window()
    assert window["suppression_low"] < window["suppression_high"]
    assert window["within_factor_5"] is True


def test_certificate_status_constrained():
    cert = alpha_gw_closure_certificate()
    assert cert["status"] == "CONSTRAINED"
    assert cert["gates"]["a_s_within_factor_5"] is True
    assert abs(cert["toe_score_delta"] - 0.2) < 1e-12
