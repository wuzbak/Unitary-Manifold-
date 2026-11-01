# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 915 — CMB Amplitude in 13D Rolling-Radion Bulk."""
from __future__ import annotations
from src.core.pillar915_cmb_amp_13d_radion import (
    N_W, K_CS, LAMBDA_WZ, SUPPRESSION_BASELINE, SUPPRESSION_13D, DELTA_AS_FRAC,
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    cmb_amp_13d, cmb_amp_summary,
)

def test_pillar_number(): assert PILLAR_NUMBER == 915
def test_gate(): assert PILLAR_GATE == "CMB_AMP_13D_ROLLING_RADION"
def test_nw(): assert N_W == 5
def test_kcs(): assert K_CS == 74
def test_lambda_wz_positive(): assert LAMBDA_WZ > 0
def test_suppression_baseline(): assert 4.0 <= SUPPRESSION_BASELINE <= 7.0
def test_suppression_13d_positive(): assert SUPPRESSION_13D > 0
def test_delta_as_frac_finite():
    import math; assert math.isfinite(DELTA_AS_FRAC)

def test_status_valid():
    assert PILLAR_STATUS in {"CMB_AMP_13D_PARTIAL_CLOSURE", "CMB_AMP_13D_ARCHITECTURE_LIMIT"}

def test_cmb_amp_keys():
    r = cmb_amp_13d()
    for k in ["pillar", "gate", "status", "suppression_baseline", "lambda_wz",
              "epsilon_sr", "c_wz", "delta_as_frac", "suppression_13d",
              "partial_closure", "interpretation", "open_item"]:
        assert k in r

def test_cmb_pillar(): assert cmb_amp_13d()["pillar"] == 915
def test_suppression_range_registered(): r = cmb_amp_13d(); assert isinstance(r["suppression_baseline_range"], list)
def test_lambda_wz_formula(): assert "n_w" in cmb_amp_13d()["lambda_wz_formula"]
def test_open_item_present(): assert len(cmb_amp_13d()["open_item"]) > 10
def test_references_present(): assert len(cmb_amp_13d()["references"]) >= 3

def test_summary_keys():
    s = cmb_amp_summary()
    for k in ["pillar", "gate", "status", "suppression_13d", "partial_closure"]:
        assert k in s

def test_summary_pillar(): assert cmb_amp_summary()["pillar"] == 915
def test_partial_closure_bool(): assert isinstance(cmb_amp_summary()["partial_closure"], bool)
