# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/neutrino_precision_hardgate_cert.py."""
from __future__ import annotations

from src.core.neutrino_precision_hardgate_cert import (
    CONSTRAINED_PARAMETER_IDS,
    GP_THRESHOLD_PCT,
    P17_RESIDUAL_PCT,
    P18_RESIDUAL_ROUTE_A_PCT,
    P18_RESIDUAL_ROUTE_B_PCT,
    P18_ROUTE_SPREAD_PCT,
    P19_RESIDUAL_PCT,
    P19_ROBUSTNESS_WORST_PCT,
    P20_RESIDUAL_PCT,
    P20_ROBUSTNESS_WORST_PCT,
    P17_STATUS,
    P18_STATUS,
    P19_STATUS,
    P20_STATUS,
    TOTAL_TOE_SCORE_DELTA,
    constrained_followup_queue,
    tier23_hardgate_certificate,
    tier23_upgrade_summary,
)


def test_threshold_constant():
    assert GP_THRESHOLD_PCT == 5.0


def test_residual_shapes_and_ranges():
    assert P17_RESIDUAL_PCT > 0
    assert P18_RESIDUAL_ROUTE_A_PCT > 0
    assert P18_RESIDUAL_ROUTE_B_PCT > 0
    assert P18_ROUTE_SPREAD_PCT >= 0
    assert P19_RESIDUAL_PCT > 0
    assert P20_RESIDUAL_PCT > 0


def test_expected_gate_outcomes():
    assert P17_RESIDUAL_PCT > GP_THRESHOLD_PCT
    assert P18_RESIDUAL_ROUTE_A_PCT < GP_THRESHOLD_PCT
    assert P18_ROUTE_SPREAD_PCT < GP_THRESHOLD_PCT
    assert P19_RESIDUAL_PCT < GP_THRESHOLD_PCT
    assert P19_ROBUSTNESS_WORST_PCT < GP_THRESHOLD_PCT
    assert P20_RESIDUAL_PCT < GP_THRESHOLD_PCT
    assert P20_ROBUSTNESS_WORST_PCT > GP_THRESHOLD_PCT


def test_status_outcomes():
    assert P17_STATUS == "CONSTRAINED"
    assert P18_STATUS == "GEOMETRIC_PREDICTION"
    assert P19_STATUS == "GEOMETRIC_PREDICTION"
    assert P20_STATUS == "CONSTRAINED"
    assert abs(TOTAL_TOE_SCORE_DELTA - 0.6) < 1e-10


def test_constrained_parameter_ids():
    assert CONSTRAINED_PARAMETER_IDS == ("P17", "P20")


def test_certificate_structure():
    cert = tier23_hardgate_certificate()
    assert cert["package"]
    assert cert["policy"]["promotion_policy"] == "hardgate_only"
    assert set(cert["parameters"].keys()) == {"P17", "P18", "P19", "P20"}


def test_certificate_p18_and_p19_promoted():
    cert = tier23_hardgate_certificate()
    assert cert["parameters"]["P18"]["new_status"] == "GEOMETRIC_PREDICTION"
    assert cert["parameters"]["P19"]["new_status"] == "GEOMETRIC_PREDICTION"
    assert cert["parameters"]["P17"]["new_status"] == "CONSTRAINED"
    assert cert["parameters"]["P20"]["new_status"] == "CONSTRAINED"


def test_summary_promoted_list_and_delta():
    s = tier23_upgrade_summary()
    assert s["promoted_parameters"] == ["P18", "P19"]
    assert abs(s["total_toe_score_delta"] - 0.6) < 1e-10


def test_followup_queue_tracks_remaining_constraints():
    queue = constrained_followup_queue()
    assert [item["parameter"] for item in queue] == ["P17", "P20"]
    assert all(item["promotion_policy"] == "blocked_until_all_gates_pass" for item in queue)


def test_summary_carries_followup_queue():
    summary = tier23_upgrade_summary()
    assert [item["parameter"] for item in summary["constrained_followup"]] == ["P17", "P20"]
