# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Pillar 777 — NP-BC-4 K/L + de Radion Loop Tightening."""
from __future__ import annotations
import pytest
from src.core.pillar777_np_bc4_kl_radion_tightening import (
    PILLAR_NUMBER, PILLAR_STATUS, VERSION,
    LEAN4_NEW_THEOREMS, LEAN4_PREV_TOTAL, LEAN4_NEW_TOTAL,
    SUBGAP_K_NEW_STATUS, SUBGAP_L_NEW_STATUS, RADION_LOOP_NEW_STATUS,
    K_CS, N_W, BSSN_DN_N_RATIO, C_ADM_NP_BOUND, NP_ADM_OPERATOR_BOUND,
    TWO_LOOP_RELATIVE_BOUND,
    adm_np_operator_bound,
    p8_lean4_closure_status,
    radion_two_loop_bound,
    subgap_k_closure_certificate,
    subgap_l_closure_certificate,
    radion_loop_closure_certificate,
    np_bc4_chain_status,
    pillar_report,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 777

def test_pillar_status():
    assert PILLAR_STATUS == "NP_BC4_KL_RADION_TIGHTENING_CLOSED"

def test_lean4_accounting():
    assert LEAN4_PREV_TOTAL == 902
    assert LEAN4_NEW_THEOREMS == 8
    assert LEAN4_NEW_TOTAL == 910

def test_lean4_formula():
    assert LEAN4_NEW_TOTAL == LEAN4_PREV_TOTAL + LEAN4_NEW_THEOREMS

def test_constants():
    assert K_CS == 74
    assert N_W == 5

def test_bssn_ratio_small():
    assert BSSN_DN_N_RATIO < 0.001

def test_np_adm_bound_small():
    assert NP_ADM_OPERATOR_BOUND < 0.001

def test_two_loop_relative_bound_tiny():
    assert TWO_LOOP_RELATIVE_BOUND < 1e-3  # sub-per-mil

# Sub-gap K

def test_adm_np_bound_status():
    res = adm_np_operator_bound()
    assert res["status"] == SUBGAP_K_NEW_STATUS

def test_adm_np_bound_negligible():
    res = adm_np_operator_bound()
    assert res["negligible_relative_to_pert"] is True

def test_adm_np_bound_honest_caveat():
    res = adm_np_operator_bound()
    assert "community" in res["honest_caveat"].lower()

def test_adm_np_bound_formula():
    res = adm_np_operator_bound()
    expected = BSSN_DN_N_RATIO * K_CS / N_W * N_W / K_CS
    assert abs(res["np_adm_operator_bound"] - expected) < 1e-15

# Sub-gap L

def test_p8_sorry_stubs():
    res = p8_lean4_closure_status()
    assert res["sorry_stubs_remaining"] == 0

def test_p8_proxy_theorems():
    res = p8_lean4_closure_status()
    assert res["proxy_theorems"] == 18

def test_p8_status():
    res = p8_lean4_closure_status()
    assert res["status"] == SUBGAP_L_NEW_STATUS

def test_p8_lean4_file():
    res = p8_lean4_closure_status()
    assert "P8FunctionalFull" in res["lean4_file"]

# de Radion Loop

def test_radion_two_loop_negligible():
    res = radion_two_loop_bound()
    assert res["negligible"] is True

def test_radion_two_loop_status():
    res = radion_two_loop_bound()
    assert res["status"] == RADION_LOOP_NEW_STATUS

def test_radion_two_loop_relative_bound():
    res = radion_two_loop_bound()
    assert res["two_loop_relative_bound"] < 1e-3

# Certificates

def test_subgap_k_cert():
    cert = subgap_k_closure_certificate()
    assert cert["sub_gap"] == "K"
    assert cert["promoted"] is True
    assert cert["new_status"] == SUBGAP_K_NEW_STATUS
    assert cert["previous_status"] == "PARTIALLY_CLOSED"

def test_subgap_l_cert():
    cert = subgap_l_closure_certificate()
    assert cert["sub_gap"] == "L"
    assert cert["promoted"] is True
    assert cert["new_status"] == SUBGAP_L_NEW_STATUS
    assert cert["sorry_stubs_remaining"] == 0

def test_radion_loop_cert():
    cert = radion_loop_closure_certificate()
    assert cert["new_status"] == RADION_LOOP_NEW_STATUS
    assert cert["promoted"] is True

# Chain status

def test_chain_status():
    chain = np_bc4_chain_status()
    assert chain["chain"] == "NP-BC-4"

def test_chain_sub_gaps():
    subs = np_bc4_chain_status()["sub_gaps"]
    assert subs["K"] == SUBGAP_K_NEW_STATUS
    assert subs["L"] == SUBGAP_L_NEW_STATUS

# Pillar report

def test_pillar_report_structure():
    report = pillar_report()
    for k in ("pillar", "title", "status", "version", "lean4",
              "sub_gap_K", "sub_gap_L", "radion_loop", "np_bc4_chain", "epistemic_deltas"):
        assert k in report

def test_pillar_report_lean4():
    lean4 = pillar_report()["lean4"]
    assert lean4["prev_total"] == 902
    assert lean4["new_total"] == 910

def test_epistemic_deltas():
    deltas = pillar_report()["epistemic_deltas"]
    assert any("CLOSED_VIA_LEAN4" in d for d in deltas)
    assert any("LOOP_CORRECTION_CLOSED" in d for d in deltas)
