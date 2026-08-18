# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 702 — CMB peak ratio KK prediction."""
from __future__ import annotations

import math

from src.core.pillar702_cmb_peak_ratio_kk_prediction import (
    C_S,
    DELTA_KK,
    LCDM_RATIO_2_TO_1,
    PILLAR_NUMBER,
    peak_height_ratios_um,
    peak_ratio_kk_correction,
    peak_ratio_planck_comparison,
)

CORRECTION = peak_ratio_kk_correction()
RATIOS = peak_height_ratios_um()
COMPARISON = peak_ratio_planck_comparison()


def test_pillar_number():
    assert PILLAR_NUMBER == 702


def test_delta_ratio_formula():
    expected = C_S ** 2 * DELTA_KK / (2.0 * math.pi ** 2)
    assert math.isclose(CORRECTION["delta_ratio"], expected, rel_tol=0.0, abs_tol=1e-18)


def test_delta_ratio_tiny():
    assert 0.0 < CORRECTION["delta_ratio"] < 1.0e-4


def test_peak1_normalized():
    assert RATIOS["peak1"] == 1.0


def test_ratio_2_to_1_near_lcdm():
    assert RATIOS["ratio_2_to_1"] > LCDM_RATIO_2_TO_1
    assert abs(RATIOS["ratio_2_to_1"] - LCDM_RATIO_2_TO_1) < 1.0e-3


def test_ratio_3_to_1_positive():
    assert RATIOS["ratio_3_to_1"] > 0.0


def test_peak_heights_descend():
    assert RATIOS["peak1"] > RATIOS["peak2"] > RATIOS["peak3"]


def test_comparison_status():
    assert COMPARISON["status"] == "KK_RATIO_SHIFT_TINY_BUT_DEFINED"


def test_comparison_contains_planck():
    assert "ratio_2_to_1" in COMPARISON["planck_reference"]


def test_comparison_delta_tiny():
    assert abs(COMPARISON["delta_vs_planck"]["ratio_2_to_1"]) < 1.0e-3
