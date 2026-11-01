# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 914 — N_gen APS Index on CY₄ Elliptic Fiber."""
from __future__ import annotations
from src.core.pillar914_ngen_aps_index_cy4 import (
    N_W, K_CS, CHI_CY4, N_D3, G_SIGMA_REF, DEG_L, CHI_SIGMA_L, N_GEN_APS,
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    aps_index_cy4, ngen_aps_summary,
)

def test_pillar_number(): assert PILLAR_NUMBER == 914
def test_gate(): assert PILLAR_GATE == "NGEN_APS_INDEX_CY4_ITHEORY"
def test_nw(): assert N_W == 5
def test_kcs(): assert K_CS == 74
def test_chi_cy4(): assert CHI_CY4 == 1_820_160
def test_n_d3(): assert N_D3 == 75_840
def test_n_d3_arithmetic(): assert N_D3 * 24 == CHI_CY4
def test_g_sigma_positive(): assert G_SIGMA_REF > 1.0
def test_deg_l_value(): assert DEG_L == -(N_W - 1)
def test_chi_sigma_l_negative(): assert CHI_SIGMA_L < 0   # large negative due to g_Sigma
def test_n_gen_aps_positive(): assert N_GEN_APS > 0

def test_status_valid():
    assert PILLAR_STATUS in {"NGEN_CY4_APS_3_CONFIRMED", "NGEN_DEGENERACY_IRREDUCIBLE_13D"}

def test_aps_index_keys():
    r = aps_index_cy4()
    for k in ["pillar", "gate", "status", "chi_cy4", "n_d3_tadpole", "g_sigma_ref",
              "deg_L", "chi_sigma_L", "n_gen_aps", "n_gen_7d_limit", "n_gen_sm",
              "aps_gives_3", "interpretation", "caveats"]:
        assert k in r

def test_aps_pillar(): assert aps_index_cy4()["pillar"] == 914
def test_aps_ngen_sm_target(): assert aps_index_cy4()["n_gen_sm"] == 3
def test_aps_7d_limit(): assert aps_index_cy4()["n_gen_7d_limit"] == 2
def test_caveats_present(): assert len(aps_index_cy4()["caveats"]) >= 2
def test_references_present(): assert len(aps_index_cy4()["references"]) >= 3

def test_summary_keys():
    s = ngen_aps_summary()
    for k in ["pillar", "gate", "status", "n_gen_aps", "aps_gives_3"]:
        assert k in s

def test_summary_pillar(): assert ngen_aps_summary()["pillar"] == 914
def test_summary_aps_gives_3_bool(): assert isinstance(ngen_aps_summary()["aps_gives_3"], bool)
