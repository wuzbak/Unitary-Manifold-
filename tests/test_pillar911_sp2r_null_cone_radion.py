# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 911 — Sp(2,ℝ) Null-Cone Radion Consistency."""
from __future__ import annotations
import math
from src.core.pillar911_sp2r_null_cone_radion import (
    N_W, K_CS, PHI0_EFF, PHI_NULL, NULL_CONE_RESIDUAL,
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    sp2r_null_cone_check, null_cone_summary,
)

def test_pillar_number(): assert PILLAR_NUMBER == 911
def test_gate(): assert PILLAR_GATE == "SP2R_NULL_CONE_RADION_CONSISTENCY"
def test_nw(): assert N_W == 5
def test_kcs(): assert K_CS == 74
def test_phi0_eff(): assert abs(PHI0_EFF - 5 * 2 * math.pi) < 1e-12
def test_phi_null_equals_phi0(): assert abs(PHI_NULL - PHI0_EFF) < 1e-12
def test_null_cone_residual_small(): assert NULL_CONE_RESIDUAL < 1e-6
def test_status_consistent(): assert PILLAR_STATUS == "SP2R_NULL_CONE_CONSISTENT"

def test_sp2r_null_cone_check_keys():
    r = sp2r_null_cone_check()
    for k in ["pillar", "gate", "status", "phi0_eff_ftum", "phi_null", "null_cone_residual", "consistent"]:
        assert k in r

def test_sp2r_consistent(): assert sp2r_null_cone_check()["consistent"] is True
def test_sp2r_residual_numeric(): assert sp2r_null_cone_check()["null_cone_residual"] < 1e-6
def test_sp2r_phi_null_value(): assert abs(sp2r_null_cone_check()["phi_null"] - PHI0_EFF) < 1e-10
def test_null_cone_summary_keys():
    s = null_cone_summary()
    for k in ["pillar", "gate", "status", "null_cone_residual", "consistent"]:
        assert k in s
def test_null_cone_summary_consistent(): assert null_cone_summary()["consistent"] is True
def test_gauge_fixing_description(): assert "t1" in sp2r_null_cone_check()["gauge_fixing"]
def test_references_present(): assert len(sp2r_null_cone_check()["references"]) >= 2
def test_pillar_matches_number(): assert sp2r_null_cone_check()["pillar"] == 911
