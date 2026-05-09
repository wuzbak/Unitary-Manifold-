# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
from __future__ import annotations

from src.core.alpha_gw_pillar52_10d_bridge import (
    alpha_gw_bridge_resolution,
    kk_to_uv_absolute_scale_bridge,
    pillar52_absolute_gravity_anchor,
)


def test_pillar52_anchor_fixes_absolute_gravity_scale():
    anchor = pillar52_absolute_gravity_anchor()
    assert anchor["status"] == "ABSOLUTE_GRAVITY_SCALE_FIXED"
    assert anchor["resolved"] is True
    assert 1e-10 < anchor["alpha_eff_v0_over_mpl4"] < 1e-8


def test_kk_to_uv_bridge_is_closed_and_in_band():
    bridge = kk_to_uv_absolute_scale_bridge()
    assert bridge["status"] == "KK_TO_UV_BRIDGE_RESOLVED"
    assert bridge["decision_status"] == "CLOSED"
    assert bridge["alpha_gw_in_target_interval"] is True
    assert bridge["all_consistency_gates_pass"] is True
    assert bridge["robust_overlap"] is True


def test_canonical_bridge_resolution_closes_missing_link():
    resolution = alpha_gw_bridge_resolution()
    assert resolution["status"] == "CLOSED_WITH_PILLAR52_10D_BRIDGE"
    assert resolution["missing_link_resolved"] is True
    assert resolution["historical_rs1_audit_retained"] is True
    assert resolution["historical_rs1_gap_orders_of_magnitude"] > 50.0
    low, high = resolution["alpha_gw_target_interval"]
    assert low <= resolution["alpha_gw_exact"] <= high
    assert resolution["absolute_scale_bridge_consistent"] is True
