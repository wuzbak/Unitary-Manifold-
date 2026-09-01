# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 937 — α_s 13D Window Tightening."""
from __future__ import annotations
from src.core.pillar937_alpha_s_13d_window_tighten import (
    N_W, K_CS, ALPHA_S_PDG,
    WINDOW_P920, WINDOW_BF, WINDOW_TIGHTENED,
    WINDOW_TIGHTENED_WIDTH, WINDOW_P920_WIDTH,
    PDG_IN_TIGHTENED_WINDOW,
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    alpha_s_window_tighten, alpha_s_window_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 937
def test_gate(): assert PILLAR_GATE == "ALPHA_S_13D_WINDOW_TIGHTEN"
def test_n_w(): assert N_W == 5
def test_k_cs(): assert K_CS == 74

def test_pdg_alpha_s(): assert abs(ALPHA_S_PDG - 0.1180) < 1e-6

def test_window_p920_valid(): assert WINDOW_P920[0] < WINDOW_P920[1]
def test_window_bf_valid(): assert WINDOW_BF[0] < WINDOW_BF[1]
def test_window_tightened_valid(): assert WINDOW_TIGHTENED[0] < WINDOW_TIGHTENED[1]

def test_pdg_in_tightened_window(): assert PDG_IN_TIGHTENED_WINDOW is True

def test_tightened_width_positive(): assert WINDOW_TIGHTENED_WIDTH > 0
def test_p920_width_positive(): assert WINDOW_P920_WIDTH > 0

def test_status_valid():
    valid = {"ALPHA_S_13D_WINDOW_TIGHTENED", "ALPHA_S_13D_WINDOW_IRREDUCIBLE"}
    assert PILLAR_STATUS in valid

def test_status_tightened(): assert PILLAR_STATUS == "ALPHA_S_13D_WINDOW_TIGHTENED"

def test_tighten_dict_keys():
    res = alpha_s_window_tighten()
    assert "window_tightened" in res
    assert "pdg_in_tightened" in res
    assert "status" in res

def test_summary_pillar():
    s = alpha_s_window_summary()
    assert s["pillar"] == 937

def test_summary_pdg_in_tightened():
    s = alpha_s_window_summary()
    assert s["pdg_in_tightened"] is True
