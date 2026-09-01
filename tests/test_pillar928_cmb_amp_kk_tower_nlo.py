# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 928 — CMB peak amplitude KK tower n=1 NLO correction."""
from __future__ import annotations
from src.core.pillar928_cmb_amp_kk_tower_nlo import (
    N_W, K_CS, PHI0, M_KK_N1, H_RECOMB, C_KK, DELTA_AS_RATIO_N1,
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    cmb_kk_tower_n1, cmb_kk_tower_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 928
def test_gate(): assert PILLAR_GATE == "CMB_AMP_KK_TOWER_NLO"
def test_n_w(): assert N_W == 5
def test_k_cs(): assert K_CS == 74
def test_phi0_value(): assert abs(PHI0 - N_W * 2 * 3.141592653589793) < 1e-10
def test_m_kk_positive(): assert M_KK_N1 > 0
def test_h_recomb_small(): assert H_RECOMB < 1.0  # much less than Planck
def test_m_kk_much_larger_than_h():
    assert M_KK_N1 > 1e10 * H_RECOMB  # extreme hierarchy
def test_c_kk_positive(): assert C_KK > 0
def test_delta_as_ratio_tiny(): assert DELTA_AS_RATIO_N1 < 1e-4  # Boltzmann suppressed
def test_pillar_status_negligible(): assert PILLAR_STATUS == "CMB_AMP_KK1_NEGLIGIBLE"

def test_cmb_kk_dict():
    r = cmb_kk_tower_n1()
    assert isinstance(r, dict)

def test_cmb_kk_pillar():
    r = cmb_kk_tower_n1()
    assert r["pillar"] == 928

def test_cmb_kk_gate():
    r = cmb_kk_tower_n1()
    assert r["gate"] == "CMB_AMP_KK_TOWER_NLO"

def test_cmb_kk_status():
    r = cmb_kk_tower_n1()
    assert r["status"] == PILLAR_STATUS

def test_cmb_kk_phi0():
    r = cmb_kk_tower_n1()
    assert abs(r["phi0"] - PHI0) < 1e-10

def test_cmb_kk_boltzmann_suppression():
    r = cmb_kk_tower_n1()
    assert r["boltzmann_suppression"] < 1e-100  # essentially zero

def test_cmb_kk_architecture_limit_unchanged():
    r = cmb_kk_tower_n1()
    assert r["architecture_limit_unchanged"] is True

def test_cmb_kk_tower_isw_open_closed():
    r = cmb_kk_tower_n1()
    assert r["kk_tower_isw_open_closed"] is True

def test_cmb_kk_interpretation():
    r = cmb_kk_tower_n1()
    assert isinstance(r["interpretation"], str) and len(r["interpretation"]) > 20

def test_cmb_kk_references():
    r = cmb_kk_tower_n1()
    assert isinstance(r["references"], list) and len(r["references"]) >= 3

def test_summary_dict():
    s = cmb_kk_tower_summary()
    assert isinstance(s, dict)

def test_summary_pillar():
    s = cmb_kk_tower_summary()
    assert s["pillar"] == 928

def test_summary_status():
    s = cmb_kk_tower_summary()
    assert s["status"] == PILLAR_STATUS
