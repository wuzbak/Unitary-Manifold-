# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Pillar 775 — NP-BC-2 Sub-gaps D/E/F Tightening."""
from __future__ import annotations
import math
import pytest
from src.core.pillar775_np_bc2_def_tightening import (
    PILLAR_NUMBER, PILLAR_STATUS, VERSION,
    LEAN4_NEW_THEOREMS, LEAN4_PREV_TOTAL, LEAN4_NEW_TOTAL,
    SUBGAP_D_NEW_STATUS, SUBGAP_E_NEW_STATUS, SUBGAP_F_NEW_STATUS,
    K_CS, N_W, N_2, THETA_IR_LOWER, THETA_IR_UPPER,
    mixing_angle_extremal_bound,
    saddle_expansion_matrix_bound,
    uv_ir_sturm_liouville_bound,
    subgap_d_closure_certificate,
    subgap_e_closure_certificate,
    subgap_f_closure_certificate,
    np_bc2_chain_status,
    pillar_report,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 775

def test_pillar_status():
    assert PILLAR_STATUS == "NP_BC2_DEF_TIGHTENING_BOUNDED"

def test_lean4_accounting():
    assert LEAN4_PREV_TOTAL == 880
    assert LEAN4_NEW_THEOREMS == 12
    assert LEAN4_NEW_TOTAL == 892

def test_lean4_total_formula():
    assert LEAN4_NEW_TOTAL == LEAN4_PREV_TOTAL + LEAN4_NEW_THEOREMS

def test_constants():
    assert K_CS == 74
    assert N_W == 5
    assert N_2 == 7

def test_theta_ir_lower_positive():
    assert THETA_IR_LOWER > 0.0

def test_theta_ir_upper_less_than_pi_half():
    assert THETA_IR_UPPER < math.pi / 2

def test_theta_ir_ordering():
    assert THETA_IR_LOWER < THETA_IR_UPPER

# Sub-gap D

def test_mixing_angle_bounded():
    res = mixing_angle_extremal_bound()
    assert res["bounded"] is True

def test_mixing_angle_saddle_unique():
    res = mixing_angle_extremal_bound()
    assert res["saddle_unique"] is True

def test_mixing_angle_status():
    res = mixing_angle_extremal_bound()
    assert res["status"] == SUBGAP_D_NEW_STATUS

def test_mixing_angle_lower_from_constants():
    res = mixing_angle_extremal_bound()
    assert abs(res["theta_ir_lower_rad"] - math.atan(N_W / K_CS)) < 1e-10

def test_mixing_angle_upper_from_constants():
    res = mixing_angle_extremal_bound()
    assert abs(res["theta_ir_upper_rad"] - math.atan(N_W / N_2)) < 1e-10

# Sub-gap E

def test_saddle_matrix_bound_closed():
    res = saddle_expansion_matrix_bound()
    assert res["proxy_closed"] is True

def test_saddle_matrix_rel_error():
    res = saddle_expansion_matrix_bound()
    assert res["relative_error_bound"] < 1.0e-3

def test_saddle_matrix_status():
    res = saddle_expansion_matrix_bound()
    assert res["status"] == SUBGAP_E_NEW_STATUS

def test_saddle_matrix_custom_ndim():
    res = saddle_expansion_matrix_bound(n_dim=148)
    assert res["relative_error_bound"] < saddle_expansion_matrix_bound(n_dim=74)["relative_error_bound"]

# Sub-gap F

def test_sturm_liouville_closed():
    res = uv_ir_sturm_liouville_bound()
    assert res["proxy_closed"] is True

def test_sturm_liouville_error():
    res = uv_ir_sturm_liouville_bound()
    assert res["sl_eigenvalue_error_bound"] < 0.01

def test_sturm_liouville_status():
    res = uv_ir_sturm_liouville_bound()
    assert res["status"] == SUBGAP_F_NEW_STATUS

# Certificates

def test_subgap_d_cert():
    cert = subgap_d_closure_certificate()
    assert cert["sub_gap"] == "D"
    assert cert["promoted"] is True
    assert cert["new_status"] == SUBGAP_D_NEW_STATUS
    assert cert["previous_status"] == "PARTIALLY_CLOSED"

def test_subgap_e_cert():
    cert = subgap_e_closure_certificate()
    assert cert["sub_gap"] == "E"
    assert cert["promoted"] is True
    assert cert["new_status"] == SUBGAP_E_NEW_STATUS

def test_subgap_f_cert():
    cert = subgap_f_closure_certificate()
    assert cert["sub_gap"] == "F"
    assert cert["promoted"] is True
    assert cert["new_status"] == SUBGAP_F_NEW_STATUS

# Chain status

def test_chain_status():
    chain = np_bc2_chain_status()
    assert chain["chain"] == "NP-BC-2"
    assert chain["overall_status"] == "NP_BC2_FULLY_BOUNDED"
    assert chain["all_promoted"] is True

def test_chain_sub_gaps():
    subs = np_bc2_chain_status()["sub_gaps"]
    assert subs["D"] == SUBGAP_D_NEW_STATUS
    assert subs["E"] == SUBGAP_E_NEW_STATUS
    assert subs["F"] == SUBGAP_F_NEW_STATUS

# Pillar report

def test_pillar_report_structure():
    report = pillar_report()
    for k in ("pillar", "title", "status", "version", "lean4",
              "sub_gap_D", "sub_gap_E", "sub_gap_F", "np_bc2_chain", "epistemic_deltas"):
        assert k in report

def test_pillar_report_lean4():
    lean4 = pillar_report()["lean4"]
    assert lean4["prev_total"] == 880
    assert lean4["new_theorems"] == 12
    assert lean4["new_total"] == 892

def test_epistemic_deltas():
    deltas = pillar_report()["epistemic_deltas"]
    assert len(deltas) >= 3
    statuses = [SUBGAP_D_NEW_STATUS, SUBGAP_E_NEW_STATUS, SUBGAP_F_NEW_STATUS]
    for s in statuses:
        assert any(s in d for d in deltas)
