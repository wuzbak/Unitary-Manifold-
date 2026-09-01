# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 922 — F-theory Rung 10 spectral cover global extension."""
from __future__ import annotations
from src.core.pillar922_ftheory_rung10_spectral_cover_global import (
    N_W, K_CS, NL_OBSTRUCTION_VALUE, NL_INTEGRALITY_SATISFIED,
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    noether_lefschetz_check, spectral_cover_global, spectral_cover_global_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 922
def test_gate(): assert PILLAR_GATE == "FTHEORY_RUNG10_SPECTRAL_COVER_GLOBAL"
def test_n_w(): assert N_W == 5
def test_k_cs(): assert K_CS == 74
def test_nl_obstruction_value_mod2(): assert NL_OBSTRUCTION_VALUE == N_W**2 % 2
def test_nw_sq(): assert N_W**2 == 25
def test_nl_integrality_is_bool(): assert isinstance(NL_INTEGRALITY_SATISFIED, bool)
def test_nl_obstruction_value_nonneg(): assert NL_OBSTRUCTION_VALUE >= 0

def test_pillar_status_valid():
    assert PILLAR_STATUS in {"RUNG10_GLOBAL_PROVED", "RUNG10_GLOBAL_OPEN"}

def test_nl_check_dict():
    r = noether_lefschetz_check()
    assert isinstance(r, dict)

def test_nl_check_c1():
    r = noether_lefschetz_check()
    assert r["c1_l_spec_sq_sgut"] == 25

def test_nl_check_obstruction():
    r = noether_lefschetz_check()
    assert r["nl_obstruction_value"] == NL_OBSTRUCTION_VALUE

def test_nl_check_integrality():
    r = noether_lefschetz_check()
    assert r["nl_integrality_satisfied"] == NL_INTEGRALITY_SATISFIED

def test_spectral_cover_dict():
    r = spectral_cover_global()
    assert isinstance(r, dict)

def test_spectral_cover_pillar():
    r = spectral_cover_global()
    assert r["pillar"] == 922

def test_spectral_cover_gate():
    r = spectral_cover_global()
    assert r["gate"] == "FTHEORY_RUNG10_SPECTRAL_COVER_GLOBAL"

def test_spectral_cover_status():
    r = spectral_cover_global()
    assert r["status"] == PILLAR_STATUS

def test_spectral_cover_interpretation():
    r = spectral_cover_global()
    assert isinstance(r["interpretation"], str) and len(r["interpretation"]) > 20

def test_spectral_cover_references():
    r = spectral_cover_global()
    assert isinstance(r["references"], list) and len(r["references"]) >= 4

def test_summary_dict():
    s = spectral_cover_global_summary()
    assert isinstance(s, dict)

def test_summary_pillar():
    s = spectral_cover_global_summary()
    assert s["pillar"] == 922

def test_summary_status():
    s = spectral_cover_global_summary()
    assert s["status"] == PILLAR_STATUS

def test_summary_nl_integrality():
    s = spectral_cover_global_summary()
    assert s["nl_integrality_satisfied"] == NL_INTEGRALITY_SATISFIED
