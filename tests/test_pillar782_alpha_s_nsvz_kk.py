# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Pillar 782 — α_s Route D: NSVZ Exact Beta in KK Tower."""
from __future__ import annotations
import pytest
from src.core.pillar782_alpha_s_nsvz_kk import (
    PILLAR_NUMBER, PILLAR_STATUS, VERSION,
    LEAN4_NEW_THEOREMS, LEAN4_PREV_TOTAL, LEAN4_NEW_TOTAL,
    K_CS, N_W, C_L_WINDING, TWO_C_L_MINUS_1,
    ALPHA_S_PDG, ALPHA_S_UM_PREDICTION, B0_SU3, N_MAX_KK,
    kk_wavefunction_overlap_sum,
    nsvz_correction,
    alpha_s_after_nsvz,
    route_d_assessment,
    all_routes_summary,
    architecture_limit_certificate,
    pillar_report,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 782

def test_pillar_status():
    assert PILLAR_STATUS == "ALPHA_S_ALL_ROUTES_ARCHITECTURE_LIMIT"

def test_lean4_accounting():
    assert LEAN4_PREV_TOTAL == 952
    assert LEAN4_NEW_THEOREMS == 6
    assert LEAN4_NEW_TOTAL == 958

def test_lean4_formula():
    assert LEAN4_NEW_TOTAL == LEAN4_PREV_TOTAL + LEAN4_NEW_THEOREMS

def test_constants():
    assert K_CS == 74
    assert N_W == 5
    assert abs(C_L_WINDING - 5/74) < 1e-12
    assert N_MAX_KK == 74

def test_two_c_l_minus_1():
    expected = 2 * (5/74) - 1
    assert abs(TWO_C_L_MINUS_1 - expected) < 1e-12

def test_alpha_s_um_below_pdg():
    assert ALPHA_S_UM_PREDICTION < ALPHA_S_PDG

# KK wavefunction overlap sum

def test_overlap_sum_positive():
    res = kk_wavefunction_overlap_sum()
    assert res["overlap_sum_numerical"] > 0.0

def test_overlap_sum_large():
    # With negative exponent, sum should be large (many IR-peaked modes)
    res = kk_wavefunction_overlap_sum()
    assert res["overlap_sum_numerical"] > 10.0

def test_overlap_sum_nmax():
    res = kk_wavefunction_overlap_sum()
    assert res["n_max"] == N_MAX_KK

# NSVZ correction

def test_nsvz_correction_positive():
    # NSVZ threshold correction is positive (improves prediction direction)
    res = nsvz_correction()
    assert res["delta_nsvz"] > 0.0

def test_nsvz_correction_small():
    res = nsvz_correction()
    # Should be small (~0.5%) — insufficient to close 4.1% gap
    assert res["delta_nsvz"] < 0.10  # < 10%

def test_nsvz_correction_direction():
    res = nsvz_correction()
    assert res["direction"] == "improving"

# α_s after NSVZ

def test_alpha_s_after_positive():
    res = alpha_s_after_nsvz()
    assert res["alpha_s_after_nsvz"] > 0.0

def test_alpha_s_after_insufficient():
    res = alpha_s_after_nsvz()
    # Route D is insufficient: residual still > 3%
    assert not res["route_d_sufficient"]
    assert res["sufficiency_ratio"] < 1.0

# Route D assessment

def test_route_d_status():
    res = route_d_assessment()
    assert res["status"] == "ROUTE_D_INSUFFICIENT"

def test_route_d_not_sufficient():
    res = route_d_assessment()
    assert not res["sufficient"]

def test_route_d_route_label():
    res = route_d_assessment()
    assert res["route"] == "D"

# All routes summary

def test_all_routes_count():
    routes = all_routes_summary()
    assert len(routes) == 4

def test_all_routes_labels():
    routes = all_routes_summary()
    labels = [r["route"] for r in routes]
    assert set(labels) == {"A", "B", "C", "D"}

def test_all_routes_architecture_limits():
    routes = all_routes_summary()
    for r in routes:
        assert "ARCHITECTURE_LIMIT" in r["status"] or "INSUFFICIENT" in r["status"]

# Architecture limit certificate

def test_arch_limit_true():
    cert = architecture_limit_certificate()
    assert cert["architecture_limit"] is True

def test_arch_limit_status():
    cert = architecture_limit_certificate()
    assert cert["status"] == PILLAR_STATUS

def test_arch_limit_routes_exhausted():
    cert = architecture_limit_certificate()
    assert set(cert["routes_exhausted"]) == {"A", "B", "C", "D"}

def test_arch_limit_required_ingredients():
    cert = architecture_limit_certificate()
    assert len(cert["required_new_ingredient"]) >= 2

def test_arch_limit_thread_closed():
    cert = architecture_limit_certificate()
    assert "no further" in cert["research_thread_status"].lower()

# Pillar report

def test_pillar_report_structure():
    report = pillar_report()
    for k in ("pillar", "title", "status", "version", "lean4",
              "nsvz_correction", "alpha_s_after_nsvz", "route_d",
              "all_routes", "architecture_limit", "epistemic_deltas"):
        assert k in report

def test_pillar_report_lean4():
    lean4 = pillar_report()["lean4"]
    assert lean4["prev_total"] == 952
    assert lean4["new_total"] == 958

def test_epistemic_deltas():
    deltas = pillar_report()["epistemic_deltas"]
    assert any("ARCHITECTURE_LIMIT" in d for d in deltas)
    assert any("Route D" in d or "NSVZ" in d for d in deltas)
