# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 945 — CMB Amplitude WZ Cross-Check."""
from __future__ import annotations
from src.core.pillar945_cmb_amp_wz_crosscheck import (
    CMB_GAP_FACTOR,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    WZ_CORRECTION_FRACTIONAL,
    WZ_FILLS_FRACTION,
    cmb_wz_crosscheck_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 945
def test_gate(): assert PILLAR_GATE == "CMB_AMP_WZ_CROSSCHECK"

def test_wz_correction_tiny():
    # WZ correction must be astronomically small
    assert WZ_CORRECTION_FRACTIONAL < 1e-50

def test_wz_correction_positive():
    assert WZ_CORRECTION_FRACTIONAL > 0

def test_cmb_gap_factor_range():
    assert 4.0 <= CMB_GAP_FACTOR <= 7.0

def test_wz_fills_fraction_tiny():
    assert WZ_FILLS_FRACTION < 1e-50

def test_status():
    assert "ARCHITECTURE_LIMIT_CONFIRMED" in PILLAR_STATUS

def test_pillar_valid():
    assert PILLAR_VALID is True

def test_summary_keys():
    s = cmb_wz_crosscheck_summary()
    for key in ["pillar", "gate", "status", "valid",
                "wz_correction_fractional", "cmb_gap_factor",
                "wz_fills_fraction", "remaining"]:
        assert key in s

def test_summary_pillar():
    assert cmb_wz_crosscheck_summary()["pillar"] == 945

def test_remaining_mentions_architecture():
    s = cmb_wz_crosscheck_summary()
    assert "architecture" in s["remaining"].lower()

def test_wz_vs_gap():
    # WZ fills < 1e-40 of the gap
    assert WZ_FILLS_FRACTION < 1e-40

def test_gap_fractional_positive():
    s = cmb_wz_crosscheck_summary()
    assert s["gap_fractional"] > 0

def test_gap_fractional_less_than_one():
    s = cmb_wz_crosscheck_summary()
    assert s["gap_fractional"] < 1.0
