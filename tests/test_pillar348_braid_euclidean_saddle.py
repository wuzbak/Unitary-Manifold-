# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 348 — Euclidean KK Path Integral Braid Saddle."""
import math
import pytest
from src.core.pillar348_braid_euclidean_saddle import (
    ADJACENCY_TRACK_LABEL, PILLAR_NUMBER, PILLAR_TITLE, DERIVATION_STATUS,
    N_W, N_M_PRIMARY, K_EFF_PRIMARY, K_EFF_MIN_Z2ODD, BETA_57_DEG,
    euclidean_action_braid, saddle_point_scan, z2_odd_sector_minimum,
    sophie_germain_factorization, hessian_positivity_check,
    action_ratio_catalog, global_minimum_uniqueness_proof,
    braid_saddle_certificate, separation_guard,
)


# ── Identity ─────────────────────────────────────────────────────────────────────

def test_module_identity():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
    assert PILLAR_NUMBER == 348
    assert DERIVATION_STATUS == "PROVED__EUCLIDEAN_PATH_INTEGRAL"


def test_constants():
    assert N_W == 5
    assert N_M_PRIMARY == 7
    assert K_EFF_PRIMARY == 74   # = 5² + 7² = 25 + 49
    assert K_EFF_MIN_Z2ODD == 74
    assert abs(BETA_57_DEG - 0.331) < 1e-10


# ── Euclidean Action ─────────────────────────────────────────────────────────────

def test_euclidean_action_57():
    result = euclidean_action_braid(5, 7)
    assert result["k_eff"] == 74
    assert result["S_E_relative_to_57"] == pytest.approx(1.0)


def test_euclidean_action_56():
    result = euclidean_action_braid(5, 6)
    assert result["k_eff"] == 61   # = 25 + 36
    assert result["S_E_relative_to_57"] == pytest.approx(61 / 74, rel=1e-10)


def test_euclidean_action_59():
    result = euclidean_action_braid(5, 9)
    assert result["k_eff"] == 106  # = 25 + 81
    assert result["S_E_relative_to_57"] > 1.0


def test_euclidean_action_invalid():
    with pytest.raises(ValueError):
        euclidean_action_braid(0, 7)
    with pytest.raises(ValueError):
        euclidean_action_braid(5, -1)


def test_euclidean_action_formula():
    result = euclidean_action_braid(3, 4)
    assert result["k_eff"] == 25  # 9 + 16
    assert result["S_E_saddle"] == pytest.approx(25 / (4 * math.pi))


# ── Saddle-Point Scan ────────────────────────────────────────────────────────────

def test_saddle_scan_ascending():
    saddles = saddle_point_scan(n_w=5, n_max_step=5)
    actions = [s["S_E_saddle"] for s in saddles]
    assert actions == sorted(actions)


def test_saddle_scan_n_z2_odd():
    saddles = saddle_point_scan(n_w=5, n_max_step=10, require_z2_odd=True)
    for s in saddles:
        assert s["is_z2_odd"]


def test_saddle_scan_minimum_step1():
    saddles = saddle_point_scan(n_w=5, n_max_step=10)
    # Without Z₂ constraint, minimum is step 1 = n₂=6 (k_eff=61)
    assert saddles[0]["step"] == 1
    assert saddles[0]["k_eff"] == 61


# ── Z₂-Odd Sector Minimum ───────────────────────────────────────────────────────

def test_z2_odd_minimum_is_57():
    result = z2_odd_sector_minimum(n_w=5)
    assert result["minimum_n2"] == 7
    assert result["minimum_k_eff"] == 74
    assert result["is_57"]
    assert result["is_unique"]


def test_z2_odd_minimum_k_eff():
    result = z2_odd_sector_minimum(n_w=5, n_max=20)
    assert result["minimum_k_eff"] == K_EFF_PRIMARY


def test_z2_odd_minimum_monotone():
    result = z2_odd_sector_minimum(n_w=5, n_max=20)
    candidates = result["candidates"]
    k_vals = [c[1] for c in candidates]
    # k_eff should increase with n₂
    assert k_vals == sorted(k_vals)


# ── Sophie-Germain Factorization ─────────────────────────────────────────────────

def test_sophie_germain_74():
    result = sophie_germain_factorization(74)
    assert result["k"] == 74
    assert result["is_unique_sos"]
    assert result["number_of_representations"] == 1
    assert (5, 7) in result["sum_of_squares_representations"]
    assert result["fermat_condition_satisfied"]


def test_sophie_germain_74_brahmagupta():
    result = sophie_germain_factorization(74)
    bfia = result["brahmagupta_fibonacci_identity"]
    assert bfia is not None
    # The result string may have spaces: "5² + 7²" or "5²+7²"
    assert "5" in bfia["result"] and "7" in bfia["result"] and "74" in bfia["result"]


def test_sophie_germain_not_unique():
    # 50 = 1²+7² = 5²+5² → two representations
    result = sophie_germain_factorization(50)
    assert not result["is_unique_sos"]
    assert result["number_of_representations"] >= 2


def test_sophie_germain_prime():
    # 5 = 1²+2² (unique)
    result = sophie_germain_factorization(5)
    assert result["number_of_representations"] == 1


# ── Hessian Positivity ───────────────────────────────────────────────────────────

def test_hessian_positive_57():
    result = hessian_positivity_check(5, 7)
    assert result["is_positive_definite"]
    assert result["verdict"] == "POSITIVE_DEFINITE"
    assert result["H_minimum_eigenvalue"] == 74


def test_hessian_positive_all_pairs():
    for n2 in range(6, 16):
        result = hessian_positivity_check(5, n2)
        assert result["is_positive_definite"], f"Hessian not PD for (5,{n2})"


def test_hessian_formula():
    result = hessian_positivity_check(3, 4)
    assert result["k_eff"] == 25
    assert result["H_minimum_eigenvalue"] == 25


# ── Action Ratio Catalog ─────────────────────────────────────────────────────────

def test_action_catalog_57_first_z2odd():
    catalog = action_ratio_catalog(n_w=5, n_max_step=10)
    z2_odd = [e for e in catalog if e["is_z2_odd_pair"]]
    # The first Z₂-odd pair should be (5,7) with ratio = 1.0
    assert z2_odd[0]["n2"] == 7
    assert z2_odd[0]["S_E_ratio"] == pytest.approx(1.0)


def test_action_catalog_all_hessians_pd():
    catalog = action_ratio_catalog(n_w=5, n_max_step=10)
    for entry in catalog:
        assert entry["hessian_positive_definite"]


def test_action_catalog_roles():
    catalog = action_ratio_catalog(n_w=5, n_max_step=10)
    # Find (5,7)
    entry_57 = next(e for e in catalog if e["n2"] == 7)
    assert entry_57["role"] == "PRIMARY_Z2_ODD_MINIMUM"
    # Find (5,6)
    entry_56 = next(e for e in catalog if e["n2"] == 6)
    assert entry_56["role"] == "Z2_EVEN_SECTOR"


# ── Global Minimum Proof ─────────────────────────────────────────────────────────

def test_global_minimum_proof_complete():
    result = global_minimum_uniqueness_proof()
    assert result["proof_complete"]
    assert result["monotonicity_verified"]
    assert result["all_hessians_positive_definite"]


def test_global_minimum_certificates():
    result = global_minimum_uniqueness_proof()
    certs = result["certificates"]
    assert certs["MINIMUM_ACTION_UNIQUE_Z2ODD"]
    assert certs["HESSIAN_ALL_POSITIVE_DEFINITE"]
    assert certs["K_EFF_MONOTONE_INCREASING"]
    assert certs["SOPHIE_GERMAIN_UNIQUE"]
    assert certs["PROOF_COMPLETE"]


def test_global_minimum_theorem_text():
    result = global_minimum_uniqueness_proof()
    assert "Z₂-odd" in result["theorem"] or "Z2-odd" in result["theorem"]
    assert "7" in result["theorem"]


def test_global_minimum_p8_upgrade():
    result = global_minimum_uniqueness_proof()
    assert "PROVED" in result["p8_upgrade"]


# ── Braid Saddle Certificate ─────────────────────────────────────────────────────

def test_braid_saddle_certificate():
    cert = braid_saddle_certificate()
    assert cert["pillar"] == 348
    assert cert["derivation_status"] == "PROVED__EUCLIDEAN_PATH_INTEGRAL"
    assert cert["primary_braid"] == "(5,7)"
    assert cert["k_eff_primary"] == 74
    assert "PROVED" in cert["p8_status"]


# ── Separation Guard ─────────────────────────────────────────────────────────────

def test_separation_guard():
    guard = separation_guard()
    assert "SEPARATION_INTACT" in guard
    assert "348" in guard
