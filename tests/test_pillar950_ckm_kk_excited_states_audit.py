# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 950 — CKM KK Excited-State Mixing Audit."""
from __future__ import annotations
import math
from src.core.pillar950_ckm_kk_excited_states_audit import (
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS, PILLAR_VALID,
    CKM_KK_OUTCOME, M_KK_PLANCK_UNITS, DELTA_THETA13_FRAC,
    KK_CORRECTION_REGIME, ckm_kk_excited_states_summary,
)

def test_pillar_number(): assert PILLAR_NUMBER == 950
def test_gate(): assert PILLAR_GATE == "CKM_KK_EXCITED_STATES_MIXING_AUDIT"
def test_valid(): assert PILLAR_VALID is True

def test_m_kk_positive(): assert M_KK_PLANCK_UNITS > 0
def test_m_kk_small():
    # Should be ≈ 5*exp(-5π) ≈ 2.6e-7
    assert 1e-8 < M_KK_PLANCK_UNITS < 1e-5

def test_m_kk_formula():
    expected = 5 * math.exp(-math.pi * 5)
    assert abs(M_KK_PLANCK_UNITS - expected) < 1e-15

def test_delta_theta13_tiny():
    assert DELTA_THETA13_FRAC < 1e-15   # negligible by many orders

def test_kk_correction_regime_negligible():
    assert KK_CORRECTION_REGIME == "NEGLIGIBLE"

def test_ckm_kk_outcome_negligible():
    assert "NEGLIGIBLE" in CKM_KK_OUTCOME

def test_pillar_status_negligible():
    assert "NEGLIGIBLE" in PILLAR_STATUS

def test_summary_keys():
    s = ckm_kk_excited_states_summary()
    for key in ["pillar", "gate", "status", "valid", "outcome",
                "m_kk_planck", "delta_theta13_frac", "kk_correction_regime",
                "interpretation"]:
        assert key in s

def test_summary_valid(): assert ckm_kk_excited_states_summary()["valid"] is True
def test_summary_pillar(): assert ckm_kk_excited_states_summary()["pillar"] == 950
def test_summary_regime(): assert ckm_kk_excited_states_summary()["kk_correction_regime"] == "NEGLIGIBLE"
def test_summary_frac_tiny(): assert ckm_kk_excited_states_summary()["delta_theta13_frac"] < 1e-15
def test_interpretation_architecture():
    s = ckm_kk_excited_states_summary()
    assert "ARCHITECTURE LIMIT" in s["interpretation"] or "architecture" in s["interpretation"].lower()
