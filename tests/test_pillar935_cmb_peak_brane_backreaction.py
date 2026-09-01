# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 935 — CMB Acoustic Peak Brane-Backreaction."""
from __future__ import annotations
from src.core.pillar935_cmb_peak_brane_backreaction import (
    N_W, K_CS, H_OVER_MPL, MPL_OVER_M5_SQ, BETA_BR,
    DELTA_PS_OVER_PS, BACKREACTION_NEGLIGIBLE,
    CMB_SUPPRESSION_FACTOR_MIN, CMB_SUPPRESSION_FACTOR_MAX,
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    cmb_brane_backreaction, cmb_br_summary,
)
import math


def test_pillar_number(): assert PILLAR_NUMBER == 935
def test_gate(): assert PILLAR_GATE == "CMB_PEAK_BRANE_BACKREACTION"
def test_n_w(): assert N_W == 5
def test_k_cs(): assert K_CS == 74

def test_h_over_mpl_small(): assert H_OVER_MPL < 1e-3
def test_mpl_over_m5_sq(): assert abs(MPL_OVER_M5_SQ - 2.0 * math.pi) < 1e-12
def test_beta_br_positive(): assert BETA_BR > 0

def test_delta_ps_small(): assert DELTA_PS_OVER_PS < 1e-5
def test_backreaction_negligible(): assert BACKREACTION_NEGLIGIBLE is True
def test_status_negligible(): assert PILLAR_STATUS == "CMB_BRANE_BACKREACTION_NEGLIGIBLE"

def test_suppression_range():
    assert CMB_SUPPRESSION_FACTOR_MIN == 4.0
    assert CMB_SUPPRESSION_FACTOR_MAX == 7.0

def test_arch_limit_confirmed():
    res = cmb_brane_backreaction()
    assert res["architecture_limit_confirmed"] is True

def test_br_dict_keys():
    res = cmb_brane_backreaction()
    assert "delta_ps_over_ps" in res
    assert "backreaction_negligible" in res
    assert "note" in res

def test_summary_pillar():
    s = cmb_br_summary()
    assert s["pillar"] == 935

def test_summary_arch_limit():
    s = cmb_br_summary()
    assert s["architecture_limit_confirmed"] is True
