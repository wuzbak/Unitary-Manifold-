# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 951 — Fermion R_i Constraint Scaffold."""
from __future__ import annotations
import math
from src.core.pillar951_fermion_ri_constraint_scaffold import (
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS, PILLAR_VALID,
    FERMION_RI_OUTCOME, DR21_UP, DR32_UP, DR21_DOWN, DR32_DOWN,
    R0_PLANCK, CONSISTENCY_RATIO_MAX, RI_WINDOW_STATUS,
    fermion_ri_constraint_summary,
)

def test_pillar_number(): assert PILLAR_NUMBER == 951
def test_gate(): assert PILLAR_GATE == "FERMION_RI_CONSTRAINT_SCAFFOLD"
def test_valid(): assert PILLAR_VALID is True

def test_r0_planck_positive(): assert R0_PLANCK > 0
def test_r0_planck_large():
    expected = math.exp(5 * math.pi) / 5
    assert abs(R0_PLANCK - expected) < 1.0

def test_dr21_up_negative():
    # Heavier = smaller (more suppressed) → negative ΔR
    assert DR21_UP < 0

def test_dr32_up_negative():
    assert DR32_UP < 0

def test_dr21_down_negative():
    assert DR21_DOWN < 0

def test_dr32_down_negative():
    assert DR32_DOWN < 0

def test_dr32_up_larger_than_dr21_up():
    # 3rd gen jump > 2nd gen jump (larger mass ratio t vs u)
    assert abs(DR32_UP) > abs(DR21_UP)

def test_all_dr_sub_r0():
    for dr in [DR21_UP, DR32_UP, DR21_DOWN, DR32_DOWN]:
        assert abs(dr) < 1.0

def test_consistency_ratio_max():
    expected = max(abs(DR21_UP), abs(DR32_UP), abs(DR21_DOWN), abs(DR32_DOWN))
    assert abs(CONSISTENCY_RATIO_MAX - expected) < 1e-12

def test_consistency_ratio_below_fine_tuning():
    assert CONSISTENCY_RATIO_MAX < 0.5

def test_ri_window_constrained():
    assert RI_WINDOW_STATUS == "R_I_WINDOW_CONSTRAINED"

def test_fermion_ri_outcome_constrained():
    assert "CONSTRAINED" in FERMION_RI_OUTCOME

def test_summary_keys():
    s = fermion_ri_constraint_summary()
    for key in ["pillar", "gate", "status", "valid", "outcome",
                "n_w", "r0_planck", "dr21_up", "dr32_up", "dr21_down", "dr32_down",
                "consistency_ratio_max", "ri_window_status", "interpretation"]:
        assert key in s

def test_summary_valid(): assert fermion_ri_constraint_summary()["valid"] is True
def test_summary_pillar(): assert fermion_ri_constraint_summary()["pillar"] == 951
def test_summary_all_constraints():
    s = fermion_ri_constraint_summary()
    assert s["constraint_1_radius_sub_r0"] is True
    assert s["constraint_2_cabibbo_mismatch"] is True
    assert s["constraint_3_flavor_dependent_allowed"] is True
    assert s["constraint_4_no_fine_tuning"] is True
