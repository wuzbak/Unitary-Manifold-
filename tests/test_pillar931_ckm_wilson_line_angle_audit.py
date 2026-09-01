# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 931 — CKM Wilson-Line Angle Audit."""
from __future__ import annotations
from src.core.pillar931_ckm_wilson_line_angle_audit import (
    N_W, K_CS, EPSILON_FN, DELTA_WL, N_SCAN,
    PDG_THETA_12, PDG_THETA_23, PDG_THETA_13,
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    wilson_line_scan, ckm_wilson_line_audit, ckm_wl_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 931
def test_gate(): assert PILLAR_GATE == "CKM_WILSON_LINE_ANGLE_AUDIT"
def test_n_w(): assert N_W == 5
def test_k_cs(): assert K_CS == 74
def test_epsilon_fn_range(): assert 0 < EPSILON_FN < 1
def test_delta_wl_value(): assert abs(DELTA_WL - N_W / K_CS) < 1e-12
def test_delta_wl_small(): assert DELTA_WL < 0.1
def test_n_scan(): assert N_SCAN == 200

def test_pdg_ordering(): assert PDG_THETA_12 > PDG_THETA_23 > PDG_THETA_13 > 0

def test_wilson_line_scan_returns_list():
    scan = wilson_line_scan(n_scan=10)
    assert isinstance(scan, list)
    assert len(scan) == 11   # n_scan + 1

def test_wilson_line_scan_fields():
    scan = wilson_line_scan(n_scan=5)
    for r in scan:
        assert "theta_wl_rad" in r
        assert "ordering_ok" in r
        assert "eps_eff" in r

def test_scan_theta_range():
    import math
    scan = wilson_line_scan(n_scan=10)
    assert scan[0]["theta_wl_rad"] == 0.0
    assert abs(scan[-1]["theta_wl_rad"] - math.pi) < 1e-12

def test_eps_eff_positive():
    scan = wilson_line_scan(n_scan=10)
    for r in scan:
        assert r["eps_eff"] > 0

def test_audit_returns_dict():
    res = ckm_wilson_line_audit()
    assert isinstance(res, dict)
    assert "status" in res

def test_audit_status_valid():
    valid_statuses = {
        "WILSON_LINE_CLOSED",
        "WILSON_LINE_ORDERING_ONLY",
        "IRREDUCIBLE_ARCHITECTURE_LIMIT",
    }
    assert PILLAR_STATUS in valid_statuses

def test_audit_n_scan():
    res = ckm_wilson_line_audit()
    assert res["n_scan"] == N_SCAN + 1

def test_audit_ordering_nonneg():
    res = ckm_wilson_line_audit()
    assert res["n_ordering_reproduced"] >= 0

def test_audit_best_error_positive():
    res = ckm_wilson_line_audit()
    assert res["best_max_fractional_error"] >= 0

def test_summary_returns_dict():
    s = ckm_wl_summary()
    assert s["pillar"] == 931
    assert s["gate"] == "CKM_WILSON_LINE_ANGLE_AUDIT"

def test_summary_status_matches():
    s = ckm_wl_summary()
    assert s["status"] == PILLAR_STATUS
