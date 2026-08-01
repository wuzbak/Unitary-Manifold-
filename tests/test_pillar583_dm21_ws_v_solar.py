# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 583 — Δm²₂₁ Step 1 WS-V solar correction."""
from __future__ import annotations

import pytest

from src.core.pillar583_dm21_ws_v_solar_step1 import (
    C_WS_12,
    DM21_AFTER_WS_V,
    DM21_BASELINE,
    DM21_PDG_EV2,
    DM21_SIGMA_EV2,
    DM31_CLOSED_EV2,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    RATIO_BRAID,
    TENSION_AFTER_STEP1,
    TENSION_BEFORE,
    VERSION,
    WS_V_CORRECTION_FRAC,
    WS_V_MIXING_AMPLITUDE,
    baseline_dm21,
    pillar_report,
    step1_summary,
    tension_after_step1,
    ws_v_solar_correction,
)


def test_pillar_identity():
    assert PILLAR_NUMBER == 583
    assert PILLAR_STATUS == "DM21_STEP1_SOLAR_WS_V_YUKAWA"
    assert "WS-V" in PILLAR_TITLE
    assert VERSION == "v20.1"


def test_core_constants():
    assert DM21_PDG_EV2 == pytest.approx(7.53e-5)
    assert DM21_SIGMA_EV2 == pytest.approx(0.18e-5)
    assert DM31_CLOSED_EV2 == pytest.approx(2.4110e-3)
    assert RATIO_BRAID == pytest.approx(36.0)


def test_solar_ws_coefficient():
    assert C_WS_12 == pytest.approx(6.0 / 37.0)
    assert 0.16 < C_WS_12 < 0.17


def test_baseline_formula():
    assert baseline_dm21() == pytest.approx(DM31_CLOSED_EV2 / RATIO_BRAID, rel=1e-12)


def test_baseline_matches_canonical_constant():
    assert baseline_dm21() == pytest.approx(DM21_BASELINE, rel=5e-4)


def test_baseline_below_pdg():
    assert baseline_dm21() < DM21_PDG_EV2


def test_ws_v_fraction_positive():
    assert WS_V_CORRECTION_FRAC > 0.0
    assert WS_V_CORRECTION_FRAC == pytest.approx(0.042)


def test_ws_v_formula_rounds_to_canonical():
    correction = ws_v_solar_correction()
    expected = 2.0 * C_WS_12 * WS_V_MIXING_AMPLITUDE
    assert correction["formula_fraction"] == pytest.approx(expected, rel=1e-12)
    assert correction["fractional_correction"] == pytest.approx(0.042, abs=3e-4)


def test_ws_v_percent_is_42():
    correction = ws_v_solar_correction()
    assert correction["fractional_correction_percent"] == pytest.approx(4.2)


def test_ws_v_after_value():
    correction = ws_v_solar_correction()
    assert correction["dm21_after_ws_v_ev2"] == pytest.approx(DM21_AFTER_WS_V, rel=1e-3)


def test_ws_v_after_above_baseline():
    correction = ws_v_solar_correction()
    assert correction["dm21_after_ws_v_ev2"] > correction["baseline_dm21_ev2"]


def test_ws_v_delta_positive():
    correction = ws_v_solar_correction()
    assert correction["delta_dm21_ev2"] > 0.0


def test_tension_keys():
    tension = tension_after_step1()
    for key in [
        "baseline_dm21_ev2",
        "dm21_after_step1_ev2",
        "tension_sigma_before",
        "tension_sigma_after",
        "improvement_sigma",
    ]:
        assert key in tension


def test_tension_before_matches_physics():
    tension = tension_after_step1()
    expected = abs(DM21_PDG_EV2 - baseline_dm21()) / DM21_SIGMA_EV2
    assert tension["tension_sigma_before"] == pytest.approx(expected, rel=1e-12)
    assert tension["tension_sigma_before"] == pytest.approx(TENSION_BEFORE, abs=0.02)


def test_tension_after_matches_physics():
    tension = tension_after_step1()
    expected = abs(DM21_PDG_EV2 - ws_v_solar_correction()["dm21_after_ws_v_ev2"]) / DM21_SIGMA_EV2
    assert tension["tension_sigma_after"] == pytest.approx(expected, rel=1e-12)
    assert tension["tension_sigma_after"] == pytest.approx(TENSION_AFTER_STEP1, abs=0.02)


def test_tension_improves():
    tension = tension_after_step1()
    assert tension["tension_sigma_after"] < tension["tension_sigma_before"]
    assert tension["improvement_sigma"] > 0.0


def test_step1_summary_identity():
    summary = step1_summary()
    assert summary["pillar"] == 583
    assert summary["step"] == 1
    assert summary["status"] == PILLAR_STATUS


def test_step1_summary_claims_not_overstated():
    summary = step1_summary()
    assert any("not closed" in item.lower() for item in summary["what_is_NOT_claimed"])
    assert summary["toe_score_delta"] == pytest.approx(0.0)


def test_step1_summary_has_three_claims():
    summary = step1_summary()
    assert len(summary["what_is_claimed"]) >= 3
    assert len(summary["what_is_NOT_claimed"]) >= 3


def test_report_structure():
    report = pillar_report()
    assert report["pillar"] == 583
    assert report["status"] == PILLAR_STATUS
    assert report["closure_step"] == 1
    assert report["remaining_steps"] == [2]


def test_report_is_not_adjacent():
    report = pillar_report()
    assert report["adjacent_track"] is False
    assert report["toe_score_delta"] == pytest.approx(0.0)
    assert report["hardgate_score_delta"] == pytest.approx(0.0)
