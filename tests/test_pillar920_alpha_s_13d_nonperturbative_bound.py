# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 920 — α_s 13D non-perturbative instanton bound."""
from __future__ import annotations
from src.core.pillar920_alpha_s_13d_nonperturbative_bound import (
    N_W, K_CS, G_S, ALPHA_S_PDG, ALPHA_S_ADS_5D, ALPHA_S_13D_CENTRAL,
    ALPHA_S_NP_CENTRAL, ALPHA_S_NP_WINDOW, INSTANTON_ACTION,
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    instanton_correction, alpha_s_np_bound, alpha_s_np_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 920
def test_gate(): assert PILLAR_GATE == "ALPHA_S_13D_NONPERTURBATIVE_BOUND"
def test_n_w(): assert N_W == 5
def test_k_cs(): assert K_CS == 74
def test_g_s_value(): assert abs(G_S - 0.72) < 1e-12
def test_alpha_s_pdg(): assert abs(ALPHA_S_PDG - 0.1180) < 1e-6
def test_alpha_s_ads_5d_positive(): assert ALPHA_S_ADS_5D > 0
def test_alpha_s_ads_5d_below_pdg(): assert ALPHA_S_ADS_5D < ALPHA_S_PDG
def test_alpha_s_13d_central_positive(): assert ALPHA_S_13D_CENTRAL > 0
def test_instanton_action_positive(): assert INSTANTON_ACTION > 0
def test_alpha_s_np_central_ge_13d(): assert ALPHA_S_NP_CENTRAL >= ALPHA_S_ADS_5D
def test_window_is_ordered(): assert ALPHA_S_NP_WINDOW[0] <= ALPHA_S_NP_WINDOW[1]
def test_window_contains_central():
    lo, hi = ALPHA_S_NP_WINDOW
    assert lo <= ALPHA_S_NP_CENTRAL <= hi

def test_pillar_status_valid():
    assert PILLAR_STATUS in {"ALPHA_S_13D_CLOSED", "ALPHA_S_13D_NP_IRREDUCIBLE"}

def test_instanton_correction_dict():
    r = instanton_correction()
    assert isinstance(r, dict)

def test_instanton_correction_keys():
    r = instanton_correction()
    for k in ["instanton_action", "alpha_s_np_central", "window_includes_pdg"]:
        assert k in r

def test_instanton_action_value():
    r = instanton_correction()
    assert r["instanton_action"] == INSTANTON_ACTION

def test_alpha_s_np_bound_dict():
    r = alpha_s_np_bound()
    assert isinstance(r, dict)

def test_alpha_s_np_bound_pillar():
    r = alpha_s_np_bound()
    assert r["pillar"] == 920

def test_alpha_s_np_bound_gate():
    r = alpha_s_np_bound()
    assert r["gate"] == "ALPHA_S_13D_NONPERTURBATIVE_BOUND"

def test_alpha_s_np_bound_status():
    r = alpha_s_np_bound()
    assert r["status"] == PILLAR_STATUS

def test_alpha_s_np_bound_interpretation():
    r = alpha_s_np_bound()
    assert isinstance(r["interpretation"], str) and len(r["interpretation"]) > 20

def test_alpha_s_np_bound_references():
    r = alpha_s_np_bound()
    assert isinstance(r["references"], list) and len(r["references"]) >= 3

def test_summary_dict():
    s = alpha_s_np_summary()
    assert isinstance(s, dict)

def test_summary_pillar():
    s = alpha_s_np_summary()
    assert s["pillar"] == 920

def test_summary_status():
    s = alpha_s_np_summary()
    assert s["status"] == PILLAR_STATUS
