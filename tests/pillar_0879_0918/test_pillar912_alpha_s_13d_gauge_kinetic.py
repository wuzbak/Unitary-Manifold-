# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 912 — 13D Gauge Kinetic Function and α_s Moduli Pathway."""
from __future__ import annotations
from src.core.pillar912_alpha_s_13d_gauge_kinetic import (
    N_W, K_CS, ALPHA_S_PDG, ALPHA_S_ADS_5D, ALPHA_S_13D_CENTRAL,
    ALPHA_S_13D_WINDOW, PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    gauge_kinetic_13d_full, alpha_s_13d_full, alpha_s_13d_summary,
)

def test_pillar_number(): assert PILLAR_NUMBER == 912
def test_gate(): assert PILLAR_GATE == "ALPHA_S_13D_GAUGE_KINETIC_PATHWAY"
def test_nw(): assert N_W == 5
def test_kcs(): assert K_CS == 74
def test_alpha_s_pdg(): assert abs(ALPHA_S_PDG - 0.1180) < 1e-6

def test_alpha_s_ads_positive(): assert ALPHA_S_ADS_5D > 0
def test_alpha_s_13d_positive(): assert ALPHA_S_13D_CENTRAL > 0
def test_alpha_s_window_ordered(): lo, hi = ALPHA_S_13D_WINDOW; assert lo <= hi
def test_alpha_s_window_positive(): lo, hi = ALPHA_S_13D_WINDOW; assert lo > 0

def test_status_valid(): assert PILLAR_STATUS in {"ALPHA_S_13D_WINDOW_NARROWED", "ALPHA_S_13D_IRREDUCIBLE"}

def test_gauge_kinetic_keys():
    g = gauge_kinetic_13d_full()
    for k in ["k_cs", "g_s", "delta_13d_sp2r", "delta_t2_threshold", "delta_rho_kahler",
              "alpha_s_ads_5d", "alpha_s_13d_central", "alpha_s_13d_window", "alpha_s_pdg"]:
        assert k in g

def test_gauge_kinetic_kcs(): assert gauge_kinetic_13d_full()["k_cs"] == 74
def test_residual_pct_computed(): assert "residual_pct_5d" in gauge_kinetic_13d_full()
def test_residual_pct_positive(): assert gauge_kinetic_13d_full()["residual_pct_5d"] > 0
def test_residual_pct_13d_positive(): assert gauge_kinetic_13d_full()["residual_pct_13d"] > 0

def test_alpha_s_full_keys():
    r = alpha_s_13d_full()
    for k in ["pillar", "gate", "status", "narrowed", "corrections", "interpretation"]:
        assert k in r

def test_corrections_positive():
    c = alpha_s_13d_full()["corrections"]
    assert c["delta_sp2r_moduli"] > 0

def test_summary_keys():
    s = alpha_s_13d_summary()
    for k in ["pillar", "gate", "status", "alpha_s_13d_central", "narrowed"]:
        assert k in s

def test_summary_pillar(): assert alpha_s_13d_summary()["pillar"] == 912
def test_13d_central_gt_5d_tree(): assert ALPHA_S_13D_CENTRAL > ALPHA_S_ADS_5D
