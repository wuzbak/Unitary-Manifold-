# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 921 — N_gen APS index on second reference CY₄."""
from __future__ import annotations
from src.core.pillar921_ngen_13d_aps_second_cy4 import (
    N_W, K_CS, CHI_CY4_REF1, CHI_CY4_REF2,
    N_GEN_APS_REF1, N_GEN_APS_REF2,
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    aps_index_second_cy4, ngen_second_cy4_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 921
def test_gate(): assert PILLAR_GATE == "NGEN_13D_APS_SECOND_CY4"
def test_n_w(): assert N_W == 5
def test_k_cs(): assert K_CS == 74
def test_chi_cy4_ref1(): assert CHI_CY4_REF1 == 1_820_160
def test_chi_cy4_ref2(): assert CHI_CY4_REF2 == 480
def test_two_geometries_different(): assert CHI_CY4_REF1 != CHI_CY4_REF2
def test_n_gen_aps_ref1_nonneg(): assert N_GEN_APS_REF1 >= 0
def test_n_gen_aps_ref2_nonneg(): assert N_GEN_APS_REF2 >= 0
def test_pillar_status_valid():
    assert PILLAR_STATUS in {
        "NGEN_DEGENERACY_GEOMETRY_INDEPENDENT",
        "NGEN_DEGENERACY_CY4_SENSITIVE",
    }

def test_aps_index_dict():
    r = aps_index_second_cy4()
    assert isinstance(r, dict)

def test_aps_index_pillar():
    r = aps_index_second_cy4()
    assert r["pillar"] == 921

def test_aps_index_gate():
    r = aps_index_second_cy4()
    assert r["gate"] == "NGEN_13D_APS_SECOND_CY4"

def test_aps_index_status():
    r = aps_index_second_cy4()
    assert r["status"] == PILLAR_STATUS

def test_aps_index_has_two_geometries():
    r = aps_index_second_cy4()
    assert "cy4_ref1" in r and "cy4_ref2" in r

def test_aps_index_ref1_chi():
    r = aps_index_second_cy4()
    assert r["cy4_ref1"]["chi_cy4"] == CHI_CY4_REF1

def test_aps_index_ref2_chi():
    r = aps_index_second_cy4()
    assert r["cy4_ref2"]["chi_cy4"] == CHI_CY4_REF2

def test_aps_index_deg_l():
    r = aps_index_second_cy4()
    assert r["deg_L"] == -(N_W - 1)

def test_aps_index_sensitive_flag():
    r = aps_index_second_cy4()
    assert isinstance(r["geometry_sensitive"], bool)

def test_aps_index_interpretation():
    r = aps_index_second_cy4()
    assert isinstance(r["interpretation"], str) and len(r["interpretation"]) > 20

def test_aps_index_references():
    r = aps_index_second_cy4()
    assert isinstance(r["references"], list) and len(r["references"]) >= 3

def test_summary_dict():
    s = ngen_second_cy4_summary()
    assert isinstance(s, dict)

def test_summary_pillar():
    s = ngen_second_cy4_summary()
    assert s["pillar"] == 921

def test_summary_status():
    s = ngen_second_cy4_summary()
    assert s["status"] == PILLAR_STATUS
