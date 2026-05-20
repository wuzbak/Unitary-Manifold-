# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 288 — ACT DR6 CMB Verdict Routing."""
import math
import pytest
from src.core.pillar288_act_dr6_cmb_verdict_routing import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    UM_NS,
    UM_R,
    UM_AS,
    ACT_DR6_NS,
    ACT_DR6_NS_SIGMA,
    ACT_DR6_R_UPPER_95,
    ACT_DR6_AS,
    P2_FALSIFIER_R_THRESHOLD,
    separation_guard,
    act_dr6_ns_verdict,
    act_dr6_r_verdict,
    act_dr6_as_verdict,
    act_dr6_cross_check_report,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 288


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_separation_guard_keys():
    g = separation_guard()
    assert g["pillar"] == 288
    assert g["is_hardgate"] is False
    assert g["modifies_hardgate_module"] is False
    assert g["alters_falsifier_window"] is False
    assert g["dataset"] == "ACT_DR6_2024"


def test_um_ns_value():
    assert abs(UM_NS - 0.9635) < 1e-6


def test_um_r_value():
    assert abs(UM_R - 0.0315) < 1e-6


def test_p2_falsifier_threshold():
    assert abs(P2_FALSIFIER_R_THRESHOLD - 0.010) < 1e-6


def test_um_r_exceeds_p2_falsifier():
    # UM r=0.0315 > 0.010: p2_falsifier_triggered would be False
    # (triggered = um_r < threshold, so False since 0.0315 > 0.010)
    assert UM_R > P2_FALSIFIER_R_THRESHOLD


def test_ns_verdict_sigma_pull():
    v = act_dr6_ns_verdict()
    # |0.9635 - 0.9660| / 0.0038 ≈ 0.66 < 1.0 → CONSISTENT
    assert v["sigma_pull"] < 1.0


def test_ns_verdict_consistent():
    v = act_dr6_ns_verdict()
    assert v["verdict"] == "CONSISTENT"


def test_ns_verdict_keys():
    v = act_dr6_ns_verdict()
    for key in ("um_ns", "act_ns", "sigma_pull", "verdict"):
        assert key in v


def test_ns_verdict_custom_values():
    v = act_dr6_ns_verdict(um_ns=0.97, act_ns=0.96, act_ns_sigma=0.004)
    assert v["sigma_pull"] > 0.0


def test_r_verdict_high_tension():
    v = act_dr6_r_verdict()
    assert v["verdict"] == "HIGH_TENSION"


def test_r_verdict_exceeds_limit():
    v = act_dr6_r_verdict()
    assert v["exceeds_95cl_limit"] is True


def test_r_verdict_p2_not_falsified():
    v = act_dr6_r_verdict()
    # UM r=0.0315 > P2_threshold=0.010, so p2_falsifier_triggered = (0.0315 < 0.010) = False
    assert v["p2_falsifier_triggered"] is False


def test_r_verdict_keys():
    v = act_dr6_r_verdict()
    for key in ("um_r", "act_r_upper_95", "exceeds_95cl_limit", "verdict",
                "p2_falsifier_triggered", "note"):
        assert key in v


def test_r_verdict_consistent_below_limit():
    v = act_dr6_r_verdict(um_r=0.005, act_r_upper_95=0.016)
    assert v["verdict"] == "CONSISTENT"


def test_as_verdict_consistent():
    v = act_dr6_as_verdict()
    assert v["verdict"] == "CONSISTENT"


def test_as_verdict_keys():
    v = act_dr6_as_verdict()
    for key in ("um_as", "act_as", "residual_pct", "verdict"):
        assert key in v


def test_as_residual_near_zero():
    v = act_dr6_as_verdict()
    assert v["residual_pct"] < 1.0  # UM_AS == ACT_DR6_AS


def test_cross_check_report_pillar():
    r = act_dr6_cross_check_report()
    assert r["pillar"] == 288


def test_cross_check_report_overall_status():
    r = act_dr6_cross_check_report()
    assert r["overall_status"] == "HIGH_TENSION_ON_R"


def test_cross_check_report_p2_not_triggered():
    r = act_dr6_cross_check_report()
    assert r["p2_falsifier_triggered"] is False


def test_cross_check_report_has_all_verdicts():
    r = act_dr6_cross_check_report()
    for key in ("ns_verdict", "r_verdict", "as_verdict"):
        assert key in r


def test_cross_check_report_summary_is_string():
    r = act_dr6_cross_check_report()
    assert isinstance(r["summary"], str)
    assert len(r["summary"]) > 10
