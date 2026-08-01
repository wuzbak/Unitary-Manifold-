# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 613 — Δm²₂₁ Step 5 two-loop KK electroweak correction."""
from __future__ import annotations

import math

import pytest

from src.core.pillar613_dm21_two_loop_ew_correction import (
    ALPHA_EW,
    BESSEL_ENHANCEMENT,
    BELOW_CLOSURE_THRESHOLD,
    CLOSURE_THRESHOLD,
    COS2_THETA12,
    DM21_AFTER_EW,
    DM21_AFTER_NLO,
    K_CS,
    K_CS_HALF,
    M_KK_GEV,
    M_Z_GEV,
    N_W,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    TENSION_AFTER_EW,
    TENSION_BEFORE,
    TWO_LOOP_EW_FRAC,
    VERSION,
    dm21_after_ew,
    pillar_report,
    step5_summary,
    tension_after_ew,
    two_loop_ew_correction,
    two_loop_ew_formula,
)

PRIMARY = step5_summary()
REPORT = pillar_report()
FORMULA = two_loop_ew_formula()
CORRECTION = two_loop_ew_correction()
TENSION = tension_after_ew()

PRIMARY_KEYS = ["pillar", "status", "step", "step_name", "formula", "correction", "dm21", "tension"]
REPORT_KEYS = [
    "pillar", "title", "status", "version", "adjacent_track",
    "two_loop_ew_formula", "two_loop_ew_correction", "dm21_after_ew",
    "tension_after_ew", "step5_summary",
]

NUMERIC_CHECKS = [
    abs(ALPHA_EW - 1.0 / 128.0) < 1e-12,
    abs(M_KK_GEV - 1000.0) < 1e-9,
    abs(M_Z_GEV - 91.18) < 1e-9,
    N_W == 5,
    K_CS == 74,
    K_CS_HALF == 37,
    abs(COS2_THETA12 - 0.6955) < 1e-12,
    abs(TWO_LOOP_EW_FRAC - 0.0079) < 1e-12,
    abs(DM21_AFTER_EW - DM21_AFTER_NLO * (1.0 + TWO_LOOP_EW_FRAC)) < 1e-15,
    TENSION_AFTER_EW < CLOSURE_THRESHOLD,
    BELOW_CLOSURE_THRESHOLD is True,
    TENSION_AFTER_EW < TENSION_BEFORE,
    abs(FORMULA["log_m_kk_over_m_z"] - math.log(1000.0 / 91.18)) < 1e-12,
    FORMULA["n_w_k_cs_half_over_k_cs"] == 5 * 37 / 74,
    abs(CORRECTION["delta_dm21_ev2"] - (DM21_AFTER_EW - DM21_AFTER_NLO)) < 1e-18,
    CORRECTION["step"] == 5,
    TENSION["below_closure_threshold"] is True,
    abs(TENSION["tension_after_sigma"] - TENSION_AFTER_EW) < 1e-12,
]

STRING_CHECKS = [
    PILLAR_STATUS == "DM21_STEP5_TWO_LOOP_EW_CORRECTION",
    "Step 5" in PILLAR_TITLE,
    "Two-Loop" in PILLAR_TITLE,
    VERSION == "v20.6",
    CORRECTION["type"] == "two_loop_KK_EW_gauge",
    CORRECTION["subdominant"] is True,
    REPORT["adjacent_track"] is False,
    len(PRIMARY["what_is_claimed"]) >= 4,
    len(PRIMARY["what_is_NOT_claimed"]) >= 4,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 613
    assert PILLAR_STATUS == "DM21_STEP5_TWO_LOOP_EW_CORRECTION"


def test_tension_drops_below_closure_threshold() -> None:
    """The solar tension must drop below 0.5σ for closure to be possible."""
    assert TENSION_AFTER_EW < 0.5
    assert TENSION_BEFORE > 0.5


def test_dm21_after_ew_in_physical_range() -> None:
    """DM21 after EW correction must be physically plausible (within 5% of PDG)."""
    PDG = 7.53e-5
    assert 0.95 * PDG < DM21_AFTER_EW < 1.05 * PDG


def test_two_loop_frac_small() -> None:
    """The two-loop correction must be sub-percent (subdominant)."""
    assert TWO_LOOP_EW_FRAC < 0.02
    assert TWO_LOOP_EW_FRAC > 0.0


def test_bessel_enhancement_positive() -> None:
    assert BESSEL_ENHANCEMENT > 1.0


def test_formula_consistency() -> None:
    """Leading-log × Bessel enhancement must be close to the adopted fraction."""
    leading = FORMULA["leading_log_fraction"]
    assert leading > 0.0
    ratio = FORMULA["consistency_ratio"]
    assert 0.5 < ratio < 2.0  # adopted fraction within factor-2 of analytic estimate


def test_no_toe_delta() -> None:
    assert REPORT["toe_score_delta"] == 0.0
    assert REPORT["hardgate_score_delta"] == 0.0


@pytest.mark.parametrize("key", PRIMARY_KEYS)
def test_primary_keys(key: str) -> None:
    assert key in PRIMARY


@pytest.mark.parametrize("key", REPORT_KEYS)
def test_report_keys(key: str) -> None:
    assert key in REPORT


@pytest.mark.parametrize("ok", NUMERIC_CHECKS)
def test_numeric_checks(ok: bool) -> None:
    assert ok


@pytest.mark.parametrize("ok", STRING_CHECKS)
def test_string_checks(ok: bool) -> None:
    assert ok
