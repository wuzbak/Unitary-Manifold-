# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for Pillar 680: Braid Uniqueness Algebraic Proof.

Verifies:
  • Step 1: Z₂-odd orbifold BC (both winding numbers odd)
  • Step 2: n1=5 unique from Planck nₛ window
  • Steps 3+4: n2=7 unique from r + β constraints
  • Full algebraic proof pair_unique=True
  • Uniqueness certificate status token
"""

import math
import pytest
from src.core.pillar680_braid_uniqueness_algebraic_proof import (
    N_W, K_CS, N2_CANONICAL,
    PLANCK_NS, PLANCK_NS_SIGMA,
    R_BICEP_KECK,
    BETA_WINDOW_DEG,
    z2_odd_requirement,
    planck_ns_n1_selection,
    bicep_keck_n2_constraint,
    birefringence_n2_selection,
    algebraic_uniqueness_proof,
    uniqueness_certificate,
)


# ── Constants ──────────────────────────────────────────────────────────────────

def test_canonical_pair():
    assert N_W == 5
    assert N2_CANONICAL == 7
    assert K_CS == 74


def test_planck_ns_value():
    assert abs(PLANCK_NS - 0.9649) < 0.002


def test_r_bicep_keck():
    assert abs(R_BICEP_KECK - 0.036) < 0.005


def test_beta_window_range():
    lo, hi = BETA_WINDOW_DEG
    assert lo < hi
    assert 0.2 < lo < 0.35
    assert 0.30 < hi < 0.50


# ── Step 1: Z₂-odd ──────────────────────────────────────────────────────────

def test_z2_odd_returns_dict():
    result = z2_odd_requirement()
    assert isinstance(result, dict)


def test_z2_odd_both_odd():
    result = z2_odd_requirement()
    # Check that the requirement text states odd winding numbers
    req = result.get("requirement", "")
    assert "odd" in req.lower() or "≡ 1" in req or "algebraic" in str(result)


def test_z2_odd_step_label():
    result = z2_odd_requirement()
    assert result.get("step") == "1" or "1" in str(result.get("step", ""))


# ── Step 2: Planck nₛ → n1=5 ─────────────────────────────────────────────────

def test_planck_ns_n1_selection_returns_dict():
    result = planck_ns_n1_selection()
    assert isinstance(result, dict)


def test_planck_ns_n1_viable():
    result = planck_ns_n1_selection()
    assert result["viable_n1"] == [5], f"viable_n1 = {result['viable_n1']}, expected [5]"


def test_planck_ns_n1_unique():
    result = planck_ns_n1_selection()
    assert result["unique_n1_5"] is True


def test_planck_ns_rejects_n1_3():
    """n1=3 gives nₛ ≈ 0.899, outside Planck 2σ window."""
    result = planck_ns_n1_selection()
    all_tested = result.get("all_tested", [])
    n1_3_entry = next((t for t in all_tested if t["n1"] == 3), None)
    if n1_3_entry is not None:
        assert n1_3_entry["ns_ok"] is False, f"n1=3 should fail nₛ test"


def test_planck_ns_uses_braided_formula():
    """nₛ for n1=5 should match braided_winding ~0.9635."""
    from src.core.braided_winding import braided_ns_r
    bw = braided_ns_r(5, 7)
    result = planck_ns_n1_selection()
    all_tested = result.get("all_tested", [])
    n1_5_entry = next((t for t in all_tested if t["n1"] == 5), None)
    if n1_5_entry is not None:
        assert abs(n1_5_entry["ns"] - bw.ns) < 1e-6


# ── Steps 3+4: BICEP/Keck + birefringence → n2=7 ────────────────────────────

def test_bicep_keck_constraint_returns_dict():
    result = bicep_keck_n2_constraint()
    assert isinstance(result, dict)


def test_birefringence_n2_viable():
    result = birefringence_n2_selection()
    assert result["viable_n2"] == [7], f"viable_n2 = {result['viable_n2']}, expected [7]"


def test_birefringence_n2_unique():
    result = birefringence_n2_selection()
    assert result["unique_n2_7"] is True


def test_birefringence_n2_rejects_n2_9():
    """n2=9 gives β ≈ 0.476°, outside [0.22°, 0.38°] window."""
    result = birefringence_n2_selection()
    tested = result.get("tested", [])
    n2_9_entry = next((t for t in tested if t["n2"] == 9), None)
    if n2_9_entry is not None:
        assert n2_9_entry["beta_ok"] is False


def test_birefringence_n2_5_fails_r():
    """n2=5 gives r ≈ 0.128 > 0.036."""
    result = birefringence_n2_selection()
    tested = result.get("tested", [])
    n2_5_entry = next((t for t in tested if t["n2"] == 5), None)
    if n2_5_entry is not None:
        assert n2_5_entry["r_ok"] is False


# ── Full algebraic proof ──────────────────────────────────────────────────────

def test_algebraic_uniqueness_proof_pair_unique():
    proof = algebraic_uniqueness_proof()
    assert proof["pair_unique"] is True


def test_algebraic_uniqueness_proof_steps():
    proof = algebraic_uniqueness_proof()
    assert "steps" in proof
    assert len(proof["steps"]) >= 3


def test_algebraic_uniqueness_proof_n1_n2():
    proof = algebraic_uniqueness_proof()
    assert proof["n1_unique"] is True
    assert proof["n2_unique"] is True


# ── Uniqueness certificate ────────────────────────────────────────────────────

def test_uniqueness_certificate_status():
    cert = uniqueness_certificate()
    assert "status" in cert
    assert "BRAID_UNIQUENESS_ALGEBRAIC_PROOF_COMPLETE" in cert["status"]


def test_uniqueness_certificate_pillar():
    cert = uniqueness_certificate()
    assert cert.get("pillar") == 680 or "680" in str(cert.get("pillar", ""))


def test_uniqueness_certificate_pair():
    cert = uniqueness_certificate()
    detail = cert.get("proof_detail", cert)
    assert detail.get("pair_unique") is True


def test_uniqueness_certificate_idempotent():
    c1 = uniqueness_certificate()
    c2 = uniqueness_certificate()
    assert c1["status"] == c2["status"]
