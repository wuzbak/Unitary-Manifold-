# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Pillar 780 — CMB Peak Shape: Analytic Term Decomposition v2."""
from __future__ import annotations
import pytest
from src.core.pillar780_cmb_peak_residual_decomposition_v2 import (
    PILLAR_NUMBER, PILLAR_STATUS, VERSION,
    LEAN4_NEW_THEOREMS, LEAN4_PREV_TOTAL, LEAN4_NEW_TOTAL,
    K_CS, N_W, TOTAL_RESIDUAL_FRACTION,
    EPSILON_KK_TRUNCATION, DELTA_SILK, R_IRREDUCIBLE,
    UNKNOWN_RESIDUAL_BEFORE, UNKNOWN_RESIDUAL_AFTER,
    kk_truncation_error,
    silk_damping_modification,
    irreducible_as_mismatch,
    residual_decomposition,
    certified_bounds,
    fallibility_update,
    pillar_report,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 780

def test_pillar_status():
    assert PILLAR_STATUS == "CMB_PEAK_RESIDUAL_DECOMPOSED_V2"

def test_lean4_accounting():
    assert LEAN4_PREV_TOTAL == 938
    assert LEAN4_NEW_THEOREMS == 6
    assert LEAN4_NEW_TOTAL == 944

def test_lean4_formula():
    assert LEAN4_NEW_TOTAL == LEAN4_PREV_TOTAL + LEAN4_NEW_THEOREMS

def test_constants():
    assert K_CS == 74
    assert N_W == 5

# Residual fractions

def test_epsilon_kk_value():
    assert abs(EPSILON_KK_TRUNCATION - 1.0/74) < 1e-12

def test_delta_silk_value():
    assert abs(DELTA_SILK - (5/74)**4) < 1e-15

def test_r_irreducible_value():
    expected = TOTAL_RESIDUAL_FRACTION - EPSILON_KK_TRUNCATION - DELTA_SILK
    assert abs(R_IRREDUCIBLE - expected) < 1e-12

def test_unknown_before_after():
    assert UNKNOWN_RESIDUAL_BEFORE == TOTAL_RESIDUAL_FRACTION
    assert UNKNOWN_RESIDUAL_AFTER == R_IRREDUCIBLE
    assert UNKNOWN_RESIDUAL_AFTER < UNKNOWN_RESIDUAL_BEFORE

# KK truncation error

def test_kk_truncation_status():
    res = kk_truncation_error()
    assert res["status"] == "COMPUTABLE_BOUNDED"

def test_kk_truncation_value():
    res = kk_truncation_error()
    assert abs(res["value"] - 1.0/74) < 1e-12

def test_kk_truncation_percent():
    res = kk_truncation_error()
    assert 1.0 < res["percent"] < 2.0  # ~1.35%

def test_kk_truncation_upper_bound():
    res = kk_truncation_error()
    assert res["upper_bound"] == res["value"]

# Silk damping

def test_silk_status():
    res = silk_damping_modification()
    assert res["status"] == "COMPUTABLE_NEGLIGIBLE"

def test_silk_value_tiny():
    res = silk_damping_modification()
    assert res["value"] < 1e-4  # negligible

def test_silk_percent():
    res = silk_damping_modification()
    assert res["percent"] < 0.01  # < 0.01%

# Irreducible mismatch

def test_irreducible_status():
    res = irreducible_as_mismatch()
    assert res["status"] == "ARCHITECTURE_LIMIT"

def test_irreducible_architecture_limit():
    res = irreducible_as_mismatch()
    assert res["architecture_limit"] is True

def test_irreducible_dominant():
    res = irreducible_as_mismatch()
    # Should be dominant fraction (~33.6% of 35%)
    assert res["value"] > 0.3

# Decomposition

def test_decomposition_consistent():
    res = residual_decomposition()
    assert res["decomposition_consistent"] is True

def test_decomposition_sum():
    res = residual_decomposition()
    assert abs(res["decomposition_sum"] - TOTAL_RESIDUAL_FRACTION) < 1e-10

# Certified bounds

def test_certified_bounds_status():
    res = certified_bounds()
    assert res["status"] == "BOUNDS_CERTIFIED"

def test_certified_bounds_reduction():
    res = certified_bounds()
    assert res["reduction_in_unknown_fraction"] > 0.0
    assert res["unknown_residual_after"] < res["unknown_residual_before"]

def test_certified_bounds_computable():
    res = certified_bounds()
    assert res["computable_upper_bound"] > 0.0
    assert res["computable_upper_bound"] < TOTAL_RESIDUAL_FRACTION

# Fallibility update

def test_fallibility_update_admission():
    res = fallibility_update()
    assert res["admission"] == "2"

def test_fallibility_update_breakdown():
    res = fallibility_update()
    bd = res["breakdown"]
    assert "kk_truncation_percent" in bd
    assert "silk_damping_percent" in bd
    assert "irreducible_as_percent" in bd

def test_fallibility_update_sum():
    res = fallibility_update()
    bd = res["breakdown"]
    total_pct = bd["kk_truncation_percent"] + bd["silk_damping_percent"] + bd["irreducible_as_percent"]
    assert abs(total_pct - TOTAL_RESIDUAL_FRACTION * 100.0) < 1e-8

# Pillar report

def test_pillar_report_structure():
    report = pillar_report()
    for k in ("pillar", "title", "status", "version", "lean4",
              "decomposition", "certified_bounds", "fallibility_update", "epistemic_deltas"):
        assert k in report

def test_pillar_report_lean4():
    lean4 = pillar_report()["lean4"]
    assert lean4["prev_total"] == 938
    assert lean4["new_total"] == 944

def test_epistemic_deltas():
    deltas = pillar_report()["epistemic_deltas"]
    assert any("ARCHITECTURE_LIMIT_DECOMPOSED" in d for d in deltas)
    assert any("bounded" in d.lower() for d in deltas)
