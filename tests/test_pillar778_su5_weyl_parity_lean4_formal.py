# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Pillar 778 — SU(5) Weyl Parity Full Lean4 Formalisation."""
from __future__ import annotations
import math
import pytest
from src.core.pillar778_su5_weyl_parity_lean4_formal import (
    PILLAR_NUMBER, PILLAR_STATUS, VERSION,
    LEAN4_NEW_THEOREMS, LEAN4_PREV_TOTAL, LEAN4_NEW_TOTAL,
    GAP3_NEW_STATUS, DIM_SU5, RANK_SU5, N_POSITIVE_ROOTS, N_TOTAL_ROOTS,
    WEYL_ORDER, N_EVEN_GENERATORS, N_ODD_GENERATORS, KAWAMURA_PARITY,
    N_SM_GENERATORS, N_PROJECTED_OUT,
    su5_group_constants,
    kawamura_matrix_properties,
    z2_eigenspace_completeness,
    su321_projection_uniqueness,
    gap3_lean4_formal_certificate,
    proxy_theorem_chain,
    pillar_report,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 778

def test_pillar_status():
    assert PILLAR_STATUS == "SU5_WEYL_PARITY_PROVED_LEAN4_FORMAL"

def test_lean4_accounting():
    assert LEAN4_PREV_TOTAL == 910
    assert LEAN4_NEW_THEOREMS == 18
    assert LEAN4_NEW_TOTAL == 928

def test_lean4_formula():
    assert LEAN4_NEW_TOTAL == LEAN4_PREV_TOTAL + LEAN4_NEW_THEOREMS

# Group constants

def test_dim_su5():
    assert DIM_SU5 == 5 ** 2 - 1

def test_rank_su5():
    assert RANK_SU5 == 5 - 1

def test_positive_roots():
    assert N_POSITIVE_ROOTS == 5 * 4 // 2

def test_total_roots():
    assert N_TOTAL_ROOTS == 2 * N_POSITIVE_ROOTS

def test_weyl_order():
    assert WEYL_ORDER == math.factorial(5)

# Kawamura matrix

def test_kawamura_parity_length():
    assert len(KAWAMURA_PARITY) == 5

def test_kawamura_parity_squared():
    for x in KAWAMURA_PARITY:
        assert x * x == 1

def test_kawamura_trace():
    assert sum(KAWAMURA_PARITY) == 1

def test_kawamura_det():
    det = 1
    for x in KAWAMURA_PARITY:
        det *= x
    assert det == 1

def test_kawamura_eigenvalue_split():
    n_even = sum(1 for x in KAWAMURA_PARITY if x == 1)
    n_odd = sum(1 for x in KAWAMURA_PARITY if x == -1)
    assert n_even == 3
    assert n_odd == 2

# Group constant functions

def test_su5_group_constants_all_correct():
    res = su5_group_constants()
    assert res["all_correct"] is True

def test_su5_group_constants_values():
    res = su5_group_constants()
    assert res["dim_su5"] == 24
    assert res["rank_su5"] == 4
    assert res["weyl_order"] == 120

# Kawamura properties

def test_kawamura_matrix_all_checks():
    res = kawamura_matrix_properties()
    assert res["all_checks"] is True

def test_kawamura_matrix_eigenvalues():
    res = kawamura_matrix_properties()
    assert res["n_even_eigenvalues"] == 3
    assert res["n_odd_eigenvalues"] == 2

def test_kawamura_matrix_trace():
    res = kawamura_matrix_properties()
    assert res["trace_p"] == 1

# Z2 eigenspace

def test_z2_eigenspace_all_checks():
    res = z2_eigenspace_completeness()
    assert res["all_checks"] is True

def test_z2_eigenspace_completeness():
    res = z2_eigenspace_completeness()
    assert res["completeness"] is True

def test_z2_sm_content_correct():
    res = z2_eigenspace_completeness()
    assert res["sm_content_correct"] is True
    assert res["sm_total"] == 12

# SU(3)×SU(2)×U(1) projection

def test_su321_projection_unique():
    res = su321_projection_uniqueness()
    assert res["projection_unique"] is True
    assert res["all_checks"] is True

def test_su321_reflection_matches():
    res = su321_projection_uniqueness()
    assert res["reflection_matches_kawamura"] is True

def test_su321_gap3_status():
    res = su321_projection_uniqueness()
    assert res["gap3_status"] == GAP3_NEW_STATUS

# Gap3 certificate

def test_gap3_cert_new_status():
    cert = gap3_lean4_formal_certificate()
    assert cert["new_status"] == GAP3_NEW_STATUS

def test_gap3_cert_all_proved():
    cert = gap3_lean4_formal_certificate()
    assert cert["all_theorems_proved"] is True

def test_gap3_cert_n_theorems():
    cert = gap3_lean4_formal_certificate()
    assert cert["n_proxy_theorems_total"] == 18

def test_gap3_cert_previous_status():
    cert = gap3_lean4_formal_certificate()
    assert cert["previous_status"] == "PROVED_CONDITIONAL"

def test_gap3_cert_lean4_files():
    cert = gap3_lean4_formal_certificate()
    assert "SU5OrbifoldWeylParity" in cert["lean4_file_primary"]
    assert "SU5WeylParityFull" in cert["lean4_file_new"]

# Proxy theorem chain

def test_proxy_theorem_chain_length():
    chain = proxy_theorem_chain()
    assert len(chain) == 18

def test_proxy_theorem_chain_all_proved():
    chain = proxy_theorem_chain()
    for t in chain:
        assert t["proved"] is True, f"Theorem {t['n']} ({t['name']}) not proved"

def test_proxy_theorem_chain_numbered():
    chain = proxy_theorem_chain()
    for i, t in enumerate(chain):
        assert t["n"] == i + 1

# Pillar report

def test_pillar_report_structure():
    report = pillar_report()
    for k in ("pillar", "title", "status", "version", "lean4",
              "gap3", "proxy_theorems", "n_proxy_theorems_proved",
              "n_proxy_theorems_total", "epistemic_deltas"):
        assert k in report

def test_pillar_report_all_proved():
    report = pillar_report()
    assert report["n_proxy_theorems_proved"] == 18
    assert report["n_proxy_theorems_total"] == 18

def test_epistemic_delta_gap3():
    deltas = pillar_report()["epistemic_deltas"]
    assert any("PROVED_LEAN4_FORMAL" in d for d in deltas)
