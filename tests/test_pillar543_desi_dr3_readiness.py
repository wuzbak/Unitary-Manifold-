# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 543 — DESI DR3 Decision-Day Readiness Certificate."""
from __future__ import annotations

import pytest
from src.core.pillar543_desi_dr3_readiness import (
    DR2_STATUS,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    ROUTING_THRESHOLDS,
    SYNTHETIC_DR3_SCENARIOS,
    VERSION,
    current_tension_summary,
    decision_day_brief,
    pillar_report,
    preregistration_hash,
    route_desi_dr3,
    routing_rehearsal,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 543


def test_pillar_status():
    assert "DESI_DR3" in PILLAR_STATUS


def test_version():
    assert VERSION == "v19.0"


# ─── DR2 status ──────────────────────────────────────────────────────────────

def test_dr2_wa_central():
    assert DR2_STATUS["wa_central"] < 0
    assert abs(DR2_STATUS["wa_central"]) < 2.0


def test_dr2_tension_not_falsified():
    assert DR2_STATUS["tension_sigma_2d_cpl_corrected"] < 3.0


def test_dr2_tension_above_2sigma():
    assert DR2_STATUS["tension_sigma_2d_cpl_corrected"] >= 2.0


def test_dr2_verdict_not_falsified():
    assert "NOT FALSIFIED" in DR2_STATUS["verdict"]


# ─── Routing thresholds ──────────────────────────────────────────────────────

def test_falsification_threshold():
    assert ROUTING_THRESHOLDS["falsified_sigma"] == 3.0


def test_high_tension_threshold_below_falsification():
    assert ROUTING_THRESHOLDS["high_tension_sigma"] < ROUTING_THRESHOLDS["falsified_sigma"]


# ─── route_desi_dr3 ──────────────────────────────────────────────────────────

def test_route_falsified_strong():
    result = route_desi_dr3(wa_measured=-0.90, wa_sigma=0.30)
    assert result["verdict"] == "FALSIFIED"
    assert result["tension_sigma"] >= 3.0


def test_route_high_tension():
    result = route_desi_dr3(wa_measured=-0.62, wa_sigma=0.28)
    assert result["verdict"] == "HIGH_TENSION"
    assert 2.0 <= result["tension_sigma"] < 3.0


def test_route_pass():
    result = route_desi_dr3(wa_measured=-0.10, wa_sigma=0.25)
    assert result["verdict"] == "PASS"
    assert result["tension_sigma"] < 2.0


def test_route_exact_threshold():
    # Exactly at 3σ → FALSIFIED
    result = route_desi_dr3(wa_measured=-0.90, wa_sigma=0.30)
    assert result["tension_sigma"] == pytest.approx(3.0, abs=0.01)
    assert result["verdict"] == "FALSIFIED"


def test_route_um_prediction_always_zero():
    for wa in [-0.3, -0.6, -0.9]:
        result = route_desi_dr3(wa, 0.30)
        assert result["um_prediction_wa"] == 0.0


def test_route_returns_action():
    result = route_desi_dr3(-0.5, 0.3)
    assert isinstance(result["action"], str)
    assert len(result["action"]) > 0


def test_route_invalid_sigma():
    with pytest.raises(ValueError):
        route_desi_dr3(-0.5, 0.0)

    with pytest.raises(ValueError):
        route_desi_dr3(-0.5, -0.1)


# ─── Routing rehearsal ───────────────────────────────────────────────────────

def test_routing_rehearsal_all_correct():
    rehearsal = routing_rehearsal()
    assert rehearsal["all_branches_verified"] is True
    for s in rehearsal["scenarios"]:
        assert s["routing_correct"], (
            f"Scenario {s['scenario']}: expected {s['expected']}, "
            f"got {s['verdict']}"
        )


def test_routing_rehearsal_all_branches_tested():
    rehearsal = routing_rehearsal()
    assert rehearsal["falsified_branch_tested"] is True
    assert rehearsal["pass_branch_tested"] is True
    assert rehearsal["high_tension_branch_tested"] is True


def test_routing_rehearsal_five_scenarios():
    assert len(SYNTHETIC_DR3_SCENARIOS) == 5
    rehearsal = routing_rehearsal()
    assert len(rehearsal["scenarios"]) == 5


# ─── Current tension summary ─────────────────────────────────────────────────

def test_current_tension_not_falsified():
    summary = current_tension_summary()
    assert "NOT FALSIFIED" in summary["status"]


def test_current_tension_distance_positive():
    summary = current_tension_summary()
    assert summary["distance_to_falsification"] > 0


def test_current_tension_next_measurement():
    summary = current_tension_summary()
    assert "DR3" in summary["next_measurement"]


# ─── Decision day brief ──────────────────────────────────────────────────────

def test_decision_day_brief_contains_key_info():
    brief = decision_day_brief()
    assert "wₐ = 0" in brief
    assert "FALSIFIED" in brief
    assert "3.0" in brief
    assert "route_desi_dr3" in brief


def test_decision_day_brief_is_string():
    assert isinstance(decision_day_brief(), str)


# ─── Preregistration hash ────────────────────────────────────────────────────

def test_preregistration_hash_deterministic():
    h1 = preregistration_hash()
    h2 = preregistration_hash()
    assert h1 == h2


def test_preregistration_hash_length():
    # SHA-256 hex digest is always 64 chars
    assert len(preregistration_hash()) == 64


# ─── Full report ─────────────────────────────────────────────────────────────

def test_pillar_report_structure():
    report = pillar_report()
    assert report["pillar"] == 543
    assert report["adjacent_track"] is True
    assert report["routing_verified"] is True
    assert report["toe_score_delta"] == 0.0
