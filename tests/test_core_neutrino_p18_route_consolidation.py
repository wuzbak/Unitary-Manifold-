# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/neutrino_p18_route_consolidation.py."""
from __future__ import annotations

from src.core.neutrino_p18_route_consolidation import (
    PDG_SIN2_THETA12,
    GP_THRESHOLD_PCT,
    ROUTE_A_GUT_VALUE,
    ROUTE_A_RESIDUAL_PCT,
    ROUTE_A_RGE_VALUE,
    ROUTE_A_RGE_RESIDUAL_PCT,
    CROSS_METHOD_SPREAD_PCT,
    ROUTE_B_RETIRED_RESIDUAL_PCT,
    P18_STATUS,
    TOE_DELTA,
    p18_route_consolidation_report,
    p18_hardgate_certificate,
)


def test_pdg_value():
    assert PDG_SIN2_THETA12 == 0.307


def test_route_a_gut_value():
    # 1/3 - 1/30 + 1/444
    expected = 1.0/3.0 - 1.0/30.0 + 1.0/444.0
    assert abs(ROUTE_A_GUT_VALUE - expected) < 1e-8


def test_route_a_residual_within_5pct():
    assert ROUTE_A_RESIDUAL_PCT < GP_THRESHOLD_PCT, (
        f"Route A residual {ROUTE_A_RESIDUAL_PCT:.3f}% exceeds 5% gate"
    )


def test_route_a_rge_residual_within_5pct():
    assert ROUTE_A_RGE_RESIDUAL_PCT < GP_THRESHOLD_PCT, (
        f"Route A + RGE residual {ROUTE_A_RGE_RESIDUAL_PCT:.3f}% exceeds 5% gate"
    )


def test_cross_method_spread_within_5pct():
    assert CROSS_METHOD_SPREAD_PCT < GP_THRESHOLD_PCT, (
        f"Cross-method spread {CROSS_METHOD_SPREAD_PCT:.3f}% exceeds 5% gate"
    )


def test_route_b_retired_is_larger():
    # Route B (4/15) should have larger residual than Route A
    assert ROUTE_B_RETIRED_RESIDUAL_PCT > ROUTE_A_RESIDUAL_PCT
    # Route B should be well outside the 5% gate
    assert ROUTE_B_RETIRED_RESIDUAL_PCT > GP_THRESHOLD_PCT


def test_route_a_rge_value_close_to_route_a():
    # RGE correction is tiny; Route A + RGE very close to Route A
    assert abs(ROUTE_A_RGE_VALUE - ROUTE_A_GUT_VALUE) < 0.002


def test_p18_promotes_to_geometric_prediction():
    assert P18_STATUS == "GEOMETRIC_PREDICTION"


def test_toe_delta():
    assert abs(TOE_DELTA - 0.3) < 1e-12


def test_report_structure():
    report = p18_route_consolidation_report()
    assert report["route_a"]["residual_pct"] == ROUTE_A_RESIDUAL_PCT
    assert report["route_b_retired"]["retired_residual_pct"] > 5.0
    assert report["all_gates_pass"] is True
    assert report["gates"]["nominal_residual_lt_5pct"] is True
    assert report["gates"]["cross_method_consistency_lt_5pct"] is True
    assert report["gates"]["axiomzero_purity"] is True


def test_certificate_structure():
    cert = p18_hardgate_certificate()
    assert cert["parameter"] == "P18"
    assert cert["new_status"] == "GEOMETRIC_PREDICTION"
    assert cert["all_gates_pass"] is True
    assert cert["previous_status"] == "CONSTRAINED"
    assert abs(cert["toe_delta"] - 0.3) < 1e-12
    assert cert["policy"] == "hardgate_only"


def test_route_b_retired_reason():
    report = p18_route_consolidation_report()
    reason = report["route_b_retired"]["reason_for_retirement"].lower()
    assert "superseded" in reason or "retired" in reason or "incomplete" in reason
    assert "RETIRED" in report["route_b_retired"]["status"]
