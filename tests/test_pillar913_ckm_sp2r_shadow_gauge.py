# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 913 — CKM Flavour from Sp(2,ℝ) Shadow Gauge."""
from __future__ import annotations
from src.core.pillar913_ckm_sp2r_shadow_gauge import (
    N_W, K_CS, EPSILON_FN, WOLFENSTEIN_PDG,
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    shadow_gauge_scan, ckm_sp2r_shadow, ckm_sp2r_summary,
)

def test_pillar_number(): assert PILLAR_NUMBER == 913
def test_gate(): assert PILLAR_GATE == "CKM_SP2R_SHADOW_GAUGE"
def test_nw(): assert N_W == 5
def test_kcs(): assert K_CS == 74
def test_epsilon_fn_positive(): assert 0 < EPSILON_FN < 1
def test_wolfenstein_value(): assert abs(WOLFENSTEIN_PDG - 0.22650) < 1e-4

def test_status_valid():
    assert PILLAR_STATUS in {"CKM_SP2R_SHADOW_FIXED", "CKM_TENSION_PERSISTS_13D"}

def test_scan_length(): assert len(shadow_gauge_scan()) == N_W

def test_scan_n_shadow_range():
    scans = shadow_gauge_scan()
    assert [s["n_shadow"] for s in scans] == list(range(1, N_W + 1))

def test_scan_entry_keys():
    for entry in shadow_gauge_scan():
        for k in ["n_shadow", "fn_charges", "sin_theta12", "sin_theta23", "sin_theta13",
                  "ordering_ok", "lambda_pred", "lambda_ratio", "lambda_within_factor2"]:
            assert k in entry

def test_sin_angles_in_01():
    for entry in shadow_gauge_scan():
        assert 0 <= entry["sin_theta12"] <= 1
        assert 0 <= entry["sin_theta23"] <= 1
        assert 0 <= entry["sin_theta13"] <= 1

def test_ckm_shadow_keys():
    r = ckm_sp2r_shadow()
    for k in ["pillar", "gate", "status", "scan", "interpretation", "open_item"]:
        assert k in r

def test_ckm_shadow_pillar(): assert ckm_sp2r_shadow()["pillar"] == 913
def test_scan_in_result(): assert len(ckm_sp2r_shadow()["scan"]) == N_W

def test_summary_keys():
    s = ckm_sp2r_summary()
    for k in ["pillar", "gate", "status"]:
        assert k in s

def test_summary_pillar(): assert ckm_sp2r_summary()["pillar"] == 913
def test_open_item_present(): assert len(ckm_sp2r_shadow()["open_item"]) > 10
def test_references_present(): assert len(ckm_sp2r_shadow()["references"]) >= 2
