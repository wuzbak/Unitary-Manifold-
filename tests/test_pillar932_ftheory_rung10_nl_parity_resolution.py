# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 932 — Rung 10 NL Parity Resolution."""
from __future__ import annotations
from src.core.pillar932_ftheory_rung10_nl_parity_resolution import (
    N_W, K_CS,
    NL_OBSTRUCTION_VALUE_BASE, NL_OBSTRUCTION_VALUE_TORSION,
    TORSION_REMOVES_OBSTRUCTION, NGEN_SHIFT_TORSION, NGEN_SHIFT_ACCEPTABLE,
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    nl_parity_resolution, nl_parity_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 932
def test_gate(): assert PILLAR_GATE == "FTHEORY_RUNG10_NL_PARITY_RESOLUTION"
def test_n_w(): assert N_W == 5
def test_k_cs(): assert K_CS == 74

def test_nl_obstruction_base_is_one(): assert NL_OBSTRUCTION_VALUE_BASE == 1   # n_w²=25 mod 2 = 1
def test_nl_torsion_is_zero(): assert NL_OBSTRUCTION_VALUE_TORSION == 0   # (n_w+1)²=36 mod 2 = 0
def test_torsion_removes_obstruction(): assert TORSION_REMOVES_OBSTRUCTION is True

def test_ngen_shift_value(): assert abs(NGEN_SHIFT_TORSION - 3 / 5) < 1e-12
def test_ngen_shift_acceptable(): assert NGEN_SHIFT_ACCEPTABLE is True

def test_status_resolved(): assert PILLAR_STATUS == "RUNG10_NL_PARITY_RESOLVED"

def test_resolution_dict_keys():
    res = nl_parity_resolution()
    assert "status" in res
    assert "torsion_removes_obstruction" in res
    assert "note" in res

def test_resolution_status_matches():
    res = nl_parity_resolution()
    assert res["status"] == PILLAR_STATUS

def test_n_w_plus1_sq(): assert (N_W + 1) ** 2 == 36
def test_n_w_plus1_sq_mod2(): assert (N_W + 1) ** 2 % 2 == 0

def test_summary_pillar():
    s = nl_parity_summary()
    assert s["pillar"] == 932

def test_summary_status():
    s = nl_parity_summary()
    assert s["status"] == "RUNG10_NL_PARITY_RESOLVED"
