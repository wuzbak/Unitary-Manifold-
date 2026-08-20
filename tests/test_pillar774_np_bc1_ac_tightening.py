# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Pillar 774 — NP-BC-1 Sub-gaps A & C Tightening."""
from __future__ import annotations
import math
import pytest
from src.core.pillar774_np_bc1_ac_tightening import (
    PILLAR_NUMBER, PILLAR_STATUS, VERSION,
    LEAN4_NEW_THEOREMS, LEAN4_PREV_TOTAL, LEAN4_NEW_TOTAL,
    SUBGAP_A_NEW_STATUS, SUBGAP_C_NEW_STATUS, NP_BC1_OVERALL_STATUS,
    K_CS, N_W, C_L_WINDING, NU_BESSEL, N_MAX_TRUNCATION,
    kk_truncation_error_bound,
    cauchy_schwarz_completeness_defect,
    subgap_a_closure_certificate,
    subgap_c_closure_certificate,
    np_bc1_chain_status,
    pillar_report,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 774

def test_pillar_status():
    assert PILLAR_STATUS == "NP_BC1_AC_TIGHTENING_CLOSED"

def test_version():
    assert VERSION == "v22.5"

# ─── Lean4 accounting ────────────────────────────────────────────────────────

def test_lean4_prev_total():
    assert LEAN4_PREV_TOTAL == 872

def test_lean4_new_theorems():
    assert LEAN4_NEW_THEOREMS == 8

def test_lean4_new_total():
    assert LEAN4_NEW_TOTAL == 880

def test_lean4_total_formula():
    assert LEAN4_NEW_TOTAL == LEAN4_PREV_TOTAL + LEAN4_NEW_THEOREMS

# ─── Constants ───────────────────────────────────────────────────────────────

def test_k_cs():
    assert K_CS == 74

def test_n_w():
    assert N_W == 5

def test_c_l_winding():
    assert abs(C_L_WINDING - 5/74) < 1e-12

def test_nu_bessel():
    expected = abs(5/74 - 0.5)
    assert abs(NU_BESSEL - expected) < 1e-12

def test_n_max_truncation():
    assert N_MAX_TRUNCATION == K_CS

# ─── KK truncation error ─────────────────────────────────────────────────────

def test_kk_truncation_error_bound_keys():
    res = kk_truncation_error_bound()
    for k in ("n_w", "k_cs", "n_max", "eps_sq", "epsilon_trunc",
              "threshold", "truncation_error_below_threshold", "status"):
        assert k in res

def test_kk_truncation_eps_sq():
    res = kk_truncation_error_bound()
    assert abs(res["eps_sq"] - (5/74)**2) < 1e-12

def test_kk_truncation_epsilon_trunc():
    res = kk_truncation_error_bound()
    expected = (5/74)**2 / 74
    assert abs(res["epsilon_trunc"] - expected) < 1e-12

def test_kk_truncation_below_threshold():
    res = kk_truncation_error_bound()
    assert res["truncation_error_below_threshold"] is True

def test_kk_truncation_status_closed():
    res = kk_truncation_error_bound()
    assert res["status"] == SUBGAP_A_NEW_STATUS

def test_kk_truncation_custom_nmax():
    res = kk_truncation_error_bound(n_max=148)
    assert res["epsilon_trunc"] < res["threshold"]

# ─── Cauchy–Schwarz completeness defect ──────────────────────────────────────

def test_cauchy_schwarz_keys():
    res = cauchy_schwarz_completeness_defect()
    for k in ("n_w", "k_cs", "kr_canonical", "exp_val", "delta_cs",
              "negligible", "status"):
        assert k in res

def test_cauchy_schwarz_negligible():
    res = cauchy_schwarz_completeness_defect()
    assert res["negligible"] is True

def test_cauchy_schwarz_delta_cs_tiny():
    res = cauchy_schwarz_completeness_defect()
    assert res["delta_cs"] < 1e-8

def test_cauchy_schwarz_status():
    res = cauchy_schwarz_completeness_defect()
    assert res["status"] == SUBGAP_C_NEW_STATUS

def test_cauchy_schwarz_exp_val_positive():
    res = cauchy_schwarz_completeness_defect()
    assert res["exp_val"] > 0.0

def test_cauchy_schwarz_custom_kr():
    # Lower kR → larger defect, still negligible for kR >= pi
    res = cauchy_schwarz_completeness_defect(kr=math.pi)
    assert res["delta_cs"] > 0.0  # positive by definition

# ─── Closure certificates ────────────────────────────────────────────────────

def test_subgap_a_cert_sub_gap():
    cert = subgap_a_closure_certificate()
    assert cert["sub_gap"] == "A"

def test_subgap_a_cert_promoted():
    cert = subgap_a_closure_certificate()
    assert cert["promoted"] is True

def test_subgap_a_cert_new_status():
    cert = subgap_a_closure_certificate()
    assert cert["new_status"] == SUBGAP_A_NEW_STATUS

def test_subgap_a_cert_previous_status():
    cert = subgap_a_closure_certificate()
    assert cert["previous_status"] == "PARTIALLY_CLOSED"

def test_subgap_a_cert_has_remaining_open():
    cert = subgap_a_closure_certificate()
    assert isinstance(cert["remaining_open"], list)
    assert len(cert["remaining_open"]) > 0

def test_subgap_c_cert_sub_gap():
    cert = subgap_c_closure_certificate()
    assert cert["sub_gap"] == "C"

def test_subgap_c_cert_promoted():
    cert = subgap_c_closure_certificate()
    assert cert["promoted"] is True

def test_subgap_c_cert_new_status():
    cert = subgap_c_closure_certificate()
    assert cert["new_status"] == SUBGAP_C_NEW_STATUS

# ─── NP-BC-1 chain status ────────────────────────────────────────────────────

def test_chain_status_chain():
    chain = np_bc1_chain_status()
    assert chain["chain"] == "NP-BC-1"

def test_chain_status_overall():
    chain = np_bc1_chain_status()
    assert chain["overall_status"] == NP_BC1_OVERALL_STATUS

def test_chain_status_all_resolved():
    chain = np_bc1_chain_status()
    assert chain["all_sub_gaps_resolved"] is True

def test_chain_status_sub_gaps():
    chain = np_bc1_chain_status()
    subs = chain["sub_gaps"]
    assert subs["A"] == SUBGAP_A_NEW_STATUS
    assert subs["C"] == SUBGAP_C_NEW_STATUS

# ─── Pillar report ───────────────────────────────────────────────────────────

def test_pillar_report_structure():
    report = pillar_report()
    for k in ("pillar", "title", "status", "version", "lean4",
              "sub_gap_A", "sub_gap_C", "np_bc1_chain", "epistemic_deltas"):
        assert k in report

def test_pillar_report_lean4():
    lean4 = pillar_report()["lean4"]
    assert lean4["prev_total"] == LEAN4_PREV_TOTAL
    assert lean4["new_theorems"] == LEAN4_NEW_THEOREMS
    assert lean4["new_total"] == LEAN4_NEW_TOTAL

def test_pillar_report_epistemic_deltas():
    deltas = pillar_report()["epistemic_deltas"]
    assert isinstance(deltas, list)
    assert len(deltas) >= 2
    assert any("PARTIALLY_CLOSED" in d for d in deltas)
