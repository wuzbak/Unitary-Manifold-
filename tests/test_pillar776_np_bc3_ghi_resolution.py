# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Pillar 776 — NP-BC-3 Sub-gaps G/H/I Resolution."""
from __future__ import annotations
import pytest
from src.core.pillar776_np_bc3_ghi_resolution import (
    PILLAR_NUMBER, PILLAR_STATUS, VERSION,
    LEAN4_NEW_THEOREMS, LEAN4_PREV_TOTAL, LEAN4_NEW_TOTAL,
    SUBGAP_G_NEW_STATUS, SUBGAP_H_NEW_STATUS, SUBGAP_I_NEW_STATUS,
    K_CS, N_W, XI_BRAID, L_LATTICE,
    braid_transfer_matrix_bound,
    cs_entanglement_scaffold_bound,
    subgap_i_irreducibility_certificate,
    subgap_g_closure_certificate,
    subgap_h_closure_certificate,
    np_bc3_chain_status,
    pillar_report,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 776

def test_pillar_status():
    assert PILLAR_STATUS == "NP_BC3_GHI_RESOLVED"

def test_lean4_accounting():
    assert LEAN4_PREV_TOTAL == 892
    assert LEAN4_NEW_THEOREMS == 10
    assert LEAN4_NEW_TOTAL == 902

def test_lean4_formula():
    assert LEAN4_NEW_TOTAL == LEAN4_PREV_TOTAL + LEAN4_NEW_THEOREMS

def test_xi_braid_positive():
    assert XI_BRAID > 0.0

def test_l_lattice():
    assert L_LATTICE == K_CS

# Sub-gap G

def test_braid_matrix_bound_negligible():
    res = braid_transfer_matrix_bound()
    assert res["negligible"] is True

def test_braid_matrix_bound_tiny():
    res = braid_transfer_matrix_bound()
    assert res["norm_bound"] < 1e-10

def test_braid_matrix_status():
    res = braid_transfer_matrix_bound()
    assert res["status"] == SUBGAP_G_NEW_STATUS

def test_braid_matrix_custom_l():
    res = braid_transfer_matrix_bound(l_sites=200)
    assert res["norm_bound"] < braid_transfer_matrix_bound(l_sites=74)["norm_bound"]

# Sub-gap H

def test_cs_entanglement_bound_positive():
    res = cs_entanglement_scaffold_bound()
    assert res["s_ee_upper_nats"] > 0.0

def test_cs_entanglement_status():
    res = cs_entanglement_scaffold_bound()
    assert res["status"] == SUBGAP_H_NEW_STATUS

def test_cs_entanglement_honest_caveat():
    res = cs_entanglement_scaffold_bound()
    assert "scaffold" in res["honest_caveat"].lower()

# Sub-gap I

def test_subgap_i_status():
    cert = subgap_i_irreducibility_certificate()
    assert cert["status"] == SUBGAP_I_NEW_STATUS

def test_subgap_i_thread_closed():
    cert = subgap_i_irreducibility_certificate()
    assert cert["research_thread_closed"] is True
    assert cert["no_further_pillars_proposed"] is True

def test_subgap_i_community_level():
    cert = subgap_i_irreducibility_certificate()
    assert cert["community_level"] is True

def test_subgap_i_conditions():
    cert = subgap_i_irreducibility_certificate()
    assert len(cert["irreducibility_conditions"]) >= 3

# Certificates

def test_subgap_g_cert():
    cert = subgap_g_closure_certificate()
    assert cert["sub_gap"] == "G"
    assert cert["promoted"] is True
    assert cert["new_status"] == SUBGAP_G_NEW_STATUS
    assert cert["previous_status"] == "PARTIALLY_CLOSED"

def test_subgap_h_cert():
    cert = subgap_h_closure_certificate()
    assert cert["sub_gap"] == "H"
    assert cert["promoted"] is True
    assert cert["new_status"] == SUBGAP_H_NEW_STATUS

# Chain status

def test_chain_status():
    chain = np_bc3_chain_status()
    assert chain["chain"] == "NP-BC-3"
    assert chain["research_thread_closed"] is True

def test_chain_sub_gaps():
    subs = np_bc3_chain_status()["sub_gaps"]
    assert subs["G"] == SUBGAP_G_NEW_STATUS
    assert subs["H"] == SUBGAP_H_NEW_STATUS
    assert subs["I"] == SUBGAP_I_NEW_STATUS

# Pillar report

def test_pillar_report_structure():
    report = pillar_report()
    for k in ("pillar", "title", "status", "version", "lean4",
              "sub_gap_G", "sub_gap_H", "sub_gap_I", "np_bc3_chain", "epistemic_deltas"):
        assert k in report

def test_pillar_report_lean4():
    lean4 = pillar_report()["lean4"]
    assert lean4["prev_total"] == 892
    assert lean4["new_total"] == 902

def test_epistemic_deltas_count():
    deltas = pillar_report()["epistemic_deltas"]
    assert len(deltas) >= 3

def test_subgap_i_delta_architecture_limit():
    deltas = pillar_report()["epistemic_deltas"]
    assert any("ARCHITECTURE_LIMIT" in d for d in deltas)
