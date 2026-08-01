# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 584 — Δm²₂₁ RGE tau-threshold consistency."""
from __future__ import annotations

import math

import pytest

from src.core.pillar584_dm21_rge_consistency_step2 import (
    COS2_THETA12,
    DM21_AFTER_RGE,
    DM21_AFTER_WS_V,
    M_KK_GEV,
    M_TAU_GEV,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    RGE_CORRECTION_FRAC,
    TENSION_AFTER_STEP2,
    THETA12_DEGREES,
    VERSION,
    Y_TAU,
    dm21_after_rge,
    pillar_report,
    rge_correction_fractional,
    tau_yukawa_rge,
    tension_evolution,
)


def test_pillar_identity():
    assert PILLAR_NUMBER == 584
    assert PILLAR_STATUS == "DM21_STEP2_RGE_TAU_THRESHOLD_CONSISTENCY"
    assert VERSION == "v20.1"


def test_input_constants():
    assert DM21_AFTER_WS_V == pytest.approx(6.978e-5)
    assert Y_TAU == pytest.approx(0.0102)
    assert COS2_THETA12 == pytest.approx(0.6955)
    assert M_KK_GEV == pytest.approx(1000.0)
    assert M_TAU_GEV == pytest.approx(1.777)


def test_tau_yukawa_rge_keys():
    data = tau_yukawa_rge()
    for key in [
        "y_tau",
        "theta12_degrees",
        "cos2_theta12_exact",
        "cos2_theta12_canonical",
        "log_mkk_over_mtau",
        "raw_tau_threshold_fraction",
        "adopted_fraction",
    ]:
        assert key in data


def test_cos2_exact_matches_angle():
    data = tau_yukawa_rge()
    expected = math.cos(math.radians(THETA12_DEGREES)) ** 2
    assert data["cos2_theta12_exact"] == pytest.approx(expected, rel=1e-12)


def test_cos2_canonical_close_to_exact():
    data = tau_yukawa_rge()
    assert data["cos2_theta12_canonical"] == pytest.approx(data["cos2_theta12_exact"], abs=2e-3)


def test_raw_rge_term_tiny():
    data = tau_yukawa_rge()
    assert data["raw_tau_threshold_fraction"] > 0.0
    assert data["raw_tau_threshold_fraction"] < 1e-4


def test_adopted_fraction_is_subpercent():
    data = tau_yukawa_rge()
    assert data["adopted_fraction"] == pytest.approx(RGE_CORRECTION_FRAC)
    assert 0.0 < data["adopted_fraction"] < 0.01


def test_adopted_fraction_is_point_22_percent():
    correction = rge_correction_fractional()
    assert correction["adopted_fraction"] == pytest.approx(0.0022)
    assert correction["adopted_percent"] == pytest.approx(0.22)
    assert correction["subdominant"] is True


def test_dm21_after_rge_keys():
    data = dm21_after_rge()
    for key in [
        "dm21_after_ws_v_ev2",
        "rge_fraction",
        "rge_correction_ev2",
        "dm21_after_rge_ev2",
    ]:
        assert key in data


def test_dm21_after_rge_formula():
    data = dm21_after_rge()
    expected = DM21_AFTER_WS_V * (1.0 + RGE_CORRECTION_FRAC)
    assert data["dm21_after_rge_ev2"] == pytest.approx(expected, rel=1e-12)


def test_dm21_after_rge_matches_canonical_constant():
    data = dm21_after_rge()
    assert data["dm21_after_rge_ev2"] == pytest.approx(DM21_AFTER_RGE, rel=2e-3)


def test_dm21_after_rge_above_step1():
    data = dm21_after_rge()
    assert data["dm21_after_rge_ev2"] > data["dm21_after_ws_v_ev2"]
    assert data["rge_correction_ev2"] > 0.0


def test_tension_evolution_keys():
    tension = tension_evolution()
    for key in [
        "tension_sigma_after_step1",
        "tension_sigma_after_step2",
        "improvement_step1_to_step2",
    ]:
        assert key in tension


def test_tension_step2_matches_physics():
    tension = tension_evolution()
    expected = abs(7.53e-5 - dm21_after_rge()["dm21_after_rge_ev2"]) / (0.18e-5)
    assert tension["tension_sigma_after_step2"] == pytest.approx(expected, rel=1e-12)
    assert tension["tension_sigma_after_step2"] == pytest.approx(TENSION_AFTER_STEP2, abs=0.03)


def test_tension_step2_improves_but_small_amount():
    tension = tension_evolution()
    assert tension["tension_sigma_after_step2"] < tension["tension_sigma_after_step1"]
    assert 0.0 < tension["improvement_step1_to_step2"] < 0.2


def test_report_structure():
    report = pillar_report()
    assert report["pillar"] == 584
    assert report["status"] == PILLAR_STATUS
    assert report["closure_step"] == 2
    assert report["remaining_steps"] == []


def test_report_honesty():
    report = pillar_report()
    assert any("not close" in item.lower() or "does not close" in item.lower()
               for item in report["what_is_NOT_claimed"])
    assert report["adjacent_track"] is False
    assert report["toe_score_delta"] == pytest.approx(0.0)
