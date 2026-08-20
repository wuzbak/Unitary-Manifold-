# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Pillar 781 — FN Charge Orbifold Geometric Reduction."""
from __future__ import annotations
import pytest
from src.core.pillar781_fn_charge_geometric_reduction import (
    PILLAR_NUMBER, PILLAR_STATUS, VERSION,
    LEAN4_NEW_THEOREMS, LEAN4_PREV_TOTAL, LEAN4_NEW_TOTAL,
    FN_CHARGES_BEFORE, FN_CHARGES_CONSTRAINED, FN_CHARGES_IRREDUCIBLE,
    K_CS, N_W, N_SECTORS, EPSILON,
    svd_determinant_constraints,
    svd_ratio_constraints,
    constraint_rank_analysis,
    fn_charge_reduction,
    geometric_lower_bound,
    pillar_report,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 781

def test_pillar_status():
    assert PILLAR_STATUS == "FN_CHARGES_PARTIALLY_CONSTRAINED_BY_SVD"

def test_lean4_accounting():
    assert LEAN4_PREV_TOTAL == 944
    assert LEAN4_NEW_THEOREMS == 8
    assert LEAN4_NEW_TOTAL == 952

def test_lean4_formula():
    assert LEAN4_NEW_TOTAL == LEAN4_PREV_TOTAL + LEAN4_NEW_THEOREMS

def test_constants():
    assert K_CS == 74
    assert N_W == 5
    assert N_SECTORS == 3
    assert abs(EPSILON - 5/74) < 1e-12

def test_fn_charges_before():
    assert FN_CHARGES_BEFORE == 9

def test_fn_charges_irreducible():
    assert FN_CHARGES_IRREDUCIBLE == 3

def test_fn_charges_reduction():
    assert FN_CHARGES_IRREDUCIBLE < FN_CHARGES_BEFORE

# SVD constraints

def test_det_constraints_count():
    res = svd_determinant_constraints()
    assert res["n_constraints"] == N_SECTORS
    assert res["n_constraints"] == 3

def test_ratio_constraints_count():
    res = svd_ratio_constraints()
    assert res["n_constraints"] == 2 * N_SECTORS
    assert res["n_constraints"] == 6

def test_total_svd_constraints():
    det = svd_determinant_constraints()["n_constraints"]
    ratio = svd_ratio_constraints()["n_constraints"]
    assert det + ratio == 9

# Rank analysis

def test_rank_analysis_effective_rank():
    res = constraint_rank_analysis()
    assert res["effective_rank"] == 8

def test_rank_analysis_constrained():
    res = constraint_rank_analysis()
    assert res["n_constrained"] == 6

def test_rank_analysis_irreducible():
    res = constraint_rank_analysis()
    assert res["n_irreducible"] == 3

# FN charge reduction

def test_fn_charge_reduction_before():
    res = fn_charge_reduction()
    assert res["fn_charges_before"] == 9

def test_fn_charge_reduction_after():
    res = fn_charge_reduction()
    assert res["fn_charges_irreducible"] == 3

def test_fn_charge_reduction_constrained():
    res = fn_charge_reduction()
    assert res["fn_charges_constrained"] == 6

def test_fn_charge_reduction_achieved():
    res = fn_charge_reduction()
    assert res["reduction_achieved"] == 6

def test_fn_charge_reduction_gates():
    res = fn_charge_reduction()
    assert "ARCHITECTURE_LIMIT" in res["previous_gate"]
    assert "PARTIALLY_CONSTRAINED" in res["new_gate"]
    assert "3" in res["new_gate"]

def test_fn_charge_reduction_status():
    res = fn_charge_reduction()
    assert res["status"] == PILLAR_STATUS

# Geometric lower bound

def test_geometric_lower_bound_value():
    res = geometric_lower_bound()
    assert res["lower_bound_irreducible"] == N_SECTORS
    assert res["lower_bound_irreducible"] == 3

def test_geometric_lower_bound_consistent():
    res = geometric_lower_bound()
    assert res["bound_consistent"] is True

def test_geometric_lower_bound_status():
    res = geometric_lower_bound()
    assert res["status"] == "GEOMETRIC_LOWER_BOUND_PROVED"

def test_geometric_lower_bound_upper():
    res = geometric_lower_bound()
    assert res["upper_bound_irreducible"] == 9

# Pillar report

def test_pillar_report_structure():
    report = pillar_report()
    for k in ("pillar", "title", "status", "version", "lean4",
              "fn_charge_reduction", "geometric_lower_bound", "epistemic_deltas"):
        assert k in report

def test_pillar_report_lean4():
    lean4 = pillar_report()["lean4"]
    assert lean4["prev_total"] == 944
    assert lean4["new_total"] == 952

def test_epistemic_deltas():
    deltas = pillar_report()["epistemic_deltas"]
    assert any("PARTIALLY_CONSTRAINED" in d for d in deltas)
    assert any("3" in d for d in deltas)
    assert any("SVD" in d for d in deltas)
