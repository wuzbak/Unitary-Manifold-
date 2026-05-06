# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_ckm_braid_lagrangian.py
====================================
Tests for Pillar 184 — Lagrangian Selection of the CKM Braid Pair (n₁,n₂)=(5,7).
(src/core/ckm_braid_lagrangian.py)

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations
import math
import pytest

from src.core.ckm_braid_lagrangian import (
    # Constants
    N_W, K_CS, N1_CANONICAL, N2_CANONICAL,
    # Core functions
    coprime_braid_selection,
    braid_pair_uniqueness_proof,
    cs_level_constraint,
    coprimality_constraint,
    asymmetry_constraint,
    # CKM consequence
    cp_phase_from_braid,
    ckm_cp_braid_lagrangian_derivation,
    # Summary
    pillar184_summary,
)


# ===========================================================================
# Module constants
# ===========================================================================

class TestModuleConstants:
    def test_n_w_is_5(self):
        assert N_W == 5

    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_n1_canonical_is_5(self):
        assert N1_CANONICAL == 5

    def test_n2_canonical_is_7(self):
        assert N2_CANONICAL == 7

    def test_cs_level_identity_holds(self):
        assert N1_CANONICAL**2 + N2_CANONICAL**2 == K_CS

    def test_coprimality_holds(self):
        assert math.gcd(N1_CANONICAL, N2_CANONICAL) == 1

    def test_asymmetry_holds(self):
        assert N2_CANONICAL > N1_CANONICAL


# ===========================================================================
# cs_level_constraint
# ===========================================================================

class TestCSLevelConstraint:
    def test_canonical_n2_squared(self):
        r = cs_level_constraint(5, 74)
        assert r["n2_squared"] == 49

    def test_canonical_n2_exact(self):
        r = cs_level_constraint(5, 74)
        assert r["n2_exact"] == pytest.approx(7.0, rel=1e-9)

    def test_canonical_n2_is_integer(self):
        r = cs_level_constraint(5, 74)
        assert r["n2_is_integer"] is True

    def test_canonical_n2_value(self):
        r = cs_level_constraint(5, 74)
        assert r["n2"] == 7

    def test_constraint_source_present(self):
        r = cs_level_constraint(5, 74)
        assert "K_CS" in r["constraint_source"]
        assert "n1" in r["constraint_source"] or "n₁" in r["constraint_source"]

    def test_non_perfect_square_k(self):
        # n1=5, k=75 → n2²=50 → √50 not integer
        r = cs_level_constraint(5, 75)
        assert r["n2_is_integer"] is False
        assert r["n2"] is None

    def test_negative_remainder(self):
        # n1=10, k=74 → 74-100 < 0
        r = cs_level_constraint(10, 74)
        assert r["n2"] is None
        assert math.isnan(r["n2_exact"])

    def test_small_example_3_4_5(self):
        # n1=3, k=25 → n2²=16 → n2=4
        r = cs_level_constraint(3, 25)
        assert r["n2"] == 4
        assert r["n2_is_integer"] is True

    def test_n1_equals_n2_case(self):
        # n1=5, k=50 → n2=5 (symmetric)
        r = cs_level_constraint(5, 50)
        assert r["n2"] == 5


# ===========================================================================
# coprimality_constraint
# ===========================================================================

class TestCoprimality:
    def test_5_7_coprime(self):
        r = coprimality_constraint(5, 7)
        assert r["is_coprime"] is True
        assert r["gcd"] == 1

    def test_4_6_not_coprime(self):
        r = coprimality_constraint(4, 6)
        assert r["is_coprime"] is False
        assert r["gcd"] == 2

    def test_5_5_not_coprime(self):
        # gcd(5,5) = 5
        r = coprimality_constraint(5, 5)
        assert r["is_coprime"] is False
        assert r["gcd"] == 5

    def test_reason_present(self):
        r = coprimality_constraint(5, 7)
        assert len(r["reason"]) > 10

    def test_3_7_coprime(self):
        r = coprimality_constraint(3, 7)
        assert r["is_coprime"] is True

    def test_6_9_not_coprime(self):
        r = coprimality_constraint(6, 9)
        assert r["gcd"] == 3


# ===========================================================================
# asymmetry_constraint
# ===========================================================================

class TestAsymmetry:
    def test_5_7_asymmetric(self):
        r = asymmetry_constraint(5, 7)
        assert r["asymmetric"] is True
        assert r["j_nonzero"] is True

    def test_7_5_not_asymmetric(self):
        r = asymmetry_constraint(7, 5)
        assert r["asymmetric"] is False
        assert r["j_nonzero"] is True

    def test_5_5_symmetric_j_zero(self):
        r = asymmetry_constraint(5, 5)
        assert r["asymmetric"] is False
        assert r["j_nonzero"] is False

    def test_reason_present(self):
        r = asymmetry_constraint(5, 7)
        assert "CP" in r["reason"] or "Pillar 145" in r["reason"]

    def test_1_2_asymmetric(self):
        r = asymmetry_constraint(1, 2)
        assert r["asymmetric"] is True


# ===========================================================================
# coprime_braid_selection (central function)
# ===========================================================================

class TestCoprimeBraidSelection:
    def test_canonical_n2_is_7(self):
        r = coprime_braid_selection(5)
        assert r["n2"] == 7

    def test_canonical_free_parameters_zero(self):
        r = coprime_braid_selection(5)
        assert r["free_parameters"] == 0

    def test_canonical_n1_is_5(self):
        r = coprime_braid_selection(5)
        assert r["n1"] == 5

    def test_canonical_k_cs_is_74(self):
        r = coprime_braid_selection(5)
        assert r["k_cs"] == 74

    def test_canonical_all_conditions_satisfied(self):
        r = coprime_braid_selection(5)
        assert r["all_conditions_satisfied"] is True

    def test_canonical_n2_is_unique(self):
        r = coprime_braid_selection(5)
        assert r["n2_is_unique"] is True

    def test_canonical_status_contains_derived(self):
        r = coprime_braid_selection(5)
        assert "DERIVED" in r["status"]

    def test_canonical_status_contains_zero_free(self):
        r = coprime_braid_selection(5)
        assert "zero" in r["status"].lower() or "ZERO" in r["status"]

    def test_derivation_steps_has_7_steps(self):
        r = coprime_braid_selection(5)
        assert len(r["derivation_steps"]) == 7

    def test_derivation_step_1_n1(self):
        r = coprime_braid_selection(5)
        s1 = r["derivation_steps"][0]
        assert s1["step"] == 1
        assert "n₁" in s1["claim"] or "n1" in s1["claim"]
        assert "5" in s1["claim"]

    def test_derivation_step_2_k_cs(self):
        r = coprime_braid_selection(5)
        s2 = r["derivation_steps"][1]
        assert s2["step"] == 2
        assert "74" in s2["claim"] or "K_CS" in s2["claim"]

    def test_derivation_step_4_n2_calculation(self):
        r = coprime_braid_selection(5)
        s4 = r["derivation_steps"][3]
        assert s4["step"] == 4
        # n2 = sqrt(74-25) = sqrt(49) = 7
        assert "49" in s4["claim"]

    def test_derivation_step_7_uniqueness(self):
        r = coprime_braid_selection(5)
        s7 = r["derivation_steps"][6]
        assert s7["step"] == 7
        assert "UNIQUE" in s7["status"]

    def test_cs_constraint_subdict(self):
        r = coprime_braid_selection(5)
        cs = r["cs_constraint"]
        assert cs["n2"] == 7
        assert cs["n2_is_integer"] is True

    def test_coprimality_subdict(self):
        r = coprime_braid_selection(5)
        cop = r["coprimality"]
        assert cop["is_coprime"] is True
        assert cop["gcd"] == 1

    def test_asymmetry_subdict(self):
        r = coprime_braid_selection(5)
        asym = r["asymmetry"]
        assert asym["asymmetric"] is True
        assert asym["j_nonzero"] is True


# ===========================================================================
# braid_pair_uniqueness_proof
# ===========================================================================

class TestBraidPairUniquenessProof:
    def test_n2_derived_is_7(self):
        r = braid_pair_uniqueness_proof(5)
        assert r["n2_derived"] == 7

    def test_n2_is_unique_given_n1(self):
        r = braid_pair_uniqueness_proof(5)
        assert r["n2_is_unique_given_n1"] is True

    def test_all_coprime_pairs_fixed_n1(self):
        r = braid_pair_uniqueness_proof(5)
        # Only (5,7) satisfies all three conditions
        pairs = r["all_coprime_pairs_fixed_n1"]
        assert len(pairs) == 1
        assert pairs[0] == (5, 7)

    def test_all_valid_pairs_any_m(self):
        r = braid_pair_uniqueness_proof(5)
        # For K_CS=74: check (5,7) is in the list
        pairs = r["all_valid_pairs_any_m"]
        assert (5, 7) in pairs

    def test_uniqueness_certificate_present(self):
        r = braid_pair_uniqueness_proof(5)
        cert = r["uniqueness_certificate"]
        assert "n₂ = 7" in cert or "n2 = 7" in cert.lower()

    def test_peer_review_response_present(self):
        r = braid_pair_uniqueness_proof(5)
        pr = r["peer_review_response"]
        assert "NOT numerological" in pr or "not numerological" in pr.lower()
        assert "PREDICTION" in pr

    def test_peer_review_mentions_k_cs(self):
        r = braid_pair_uniqueness_proof(5)
        assert "K_CS" in r["peer_review_response"] or "74" in r["peer_review_response"]

    def test_k_cs_value(self):
        r = braid_pair_uniqueness_proof(5)
        assert r["k_cs"] == 74

    def test_n_w_value(self):
        r = braid_pair_uniqueness_proof(5)
        assert r["n_w"] == 5


# ===========================================================================
# cp_phase_from_braid
# ===========================================================================

class TestCPPhaseFromBraid:
    def test_canonical_delta_deg(self):
        r = cp_phase_from_braid(5, 7)
        # delta = 2*arctan(5/7) ≈ 71.08°
        assert r["delta_deg"] == pytest.approx(71.08, abs=0.05)

    def test_canonical_delta_rad(self):
        r = cp_phase_from_braid(5, 7)
        expected = 2.0 * math.atan2(5, 7)
        assert r["delta_rad"] == pytest.approx(expected, rel=1e-9)

    def test_pdg_central_value(self):
        r = cp_phase_from_braid(5, 7)
        assert r["pdg_deg"] == pytest.approx(68.5, rel=1e-9)

    def test_pdg_sigma(self):
        r = cp_phase_from_braid(5, 7)
        assert r["pdg_sigma_deg"] == pytest.approx(2.6, rel=1e-9)

    def test_sigma_tension_under_2(self):
        r = cp_phase_from_braid(5, 7)
        # |71.08 - 68.5| / 2.6 ≈ 0.99σ
        assert r["sigma_tension"] < 2.0

    def test_sigma_tension_value(self):
        r = cp_phase_from_braid(5, 7)
        expected = abs(r["delta_deg"] - 68.5) / 2.6
        assert r["sigma_tension"] == pytest.approx(expected, rel=1e-6)

    def test_consistent_is_true(self):
        r = cp_phase_from_braid(5, 7)
        assert r["consistent"] is True

    def test_symmetric_braid_5_5(self):
        r = cp_phase_from_braid(5, 5)
        # arctan(1) = 45°, 2*45 = 90°
        assert r["delta_deg"] == pytest.approx(90.0, abs=0.01)

    def test_large_tension_8_3(self):
        # arctan(8/3) ≈ 69.4°, 2*69.4 ≈ 138.8° → large tension
        r = cp_phase_from_braid(8, 3)
        assert r["sigma_tension"] > 20.0


# ===========================================================================
# ckm_cp_braid_lagrangian_derivation
# ===========================================================================

class TestCKMCPBraidLagrangianDerivation:
    def test_returns_total_free_params_zero(self):
        r = ckm_cp_braid_lagrangian_derivation(5)
        assert r["total_free_parameters"] == 0

    def test_step1_n1(self):
        r = ckm_cp_braid_lagrangian_derivation(5)
        assert r["step_1_n1"]["n1"] == 5
        assert r["step_1_n1"]["free_params"] == 0

    def test_step2_k_cs(self):
        r = ckm_cp_braid_lagrangian_derivation(5)
        assert r["step_2_k_cs"]["k_cs"] == 74
        assert r["step_2_k_cs"]["free_params"] == 0

    def test_step3_n2(self):
        r = ckm_cp_braid_lagrangian_derivation(5)
        assert r["step_3_n2"]["n2"] == 7
        assert r["step_3_n2"]["uniqueness"] is True
        assert r["step_3_n2"]["free_params"] == 0

    def test_step4_delta(self):
        r = ckm_cp_braid_lagrangian_derivation(5)
        s4 = r["step_4_delta"]
        assert s4["delta_deg"] == pytest.approx(71.08, abs=0.05)
        assert s4["sigma_tension"] < 2.0
        assert s4["consistent"] is True
        assert s4["free_params"] == 0

    def test_lagrangian_justification_present(self):
        r = ckm_cp_braid_lagrangian_derivation(5)
        lj = r["lagrangian_justification"]
        assert "CS" in lj or "Chern-Simons" in lj
        assert "PREDICTION" in lj or "prediction" in lj

    def test_audit_response_present(self):
        r = ckm_cp_braid_lagrangian_derivation(5)
        ar = r["audit_response"]
        assert "CLOSED" in ar
        assert "Pillar 184" in ar

    def test_lagrangian_input_present(self):
        r = ckm_cp_braid_lagrangian_derivation(5)
        assert "S_CS" in r["lagrangian_input"] or "Chern-Simons" in r["lagrangian_input"]


# ===========================================================================
# pillar184_summary
# ===========================================================================

class TestPillar184Summary:
    def test_pillar_number(self):
        r = pillar184_summary()
        assert r["pillar"] == 184

    def test_n1_is_5(self):
        r = pillar184_summary()
        assert r["n1"] == 5

    def test_k_cs_is_74(self):
        r = pillar184_summary()
        assert r["k_cs"] == 74

    def test_n2_derived_is_7(self):
        r = pillar184_summary()
        assert r["n2_derived"] == 7

    def test_n2_is_unique(self):
        r = pillar184_summary()
        assert r["n2_is_unique"] is True

    def test_cp_phase_deg(self):
        r = pillar184_summary()
        assert r["cp_phase_deg"] == pytest.approx(71.08, abs=0.05)

    def test_cp_tension_under_2sigma(self):
        r = pillar184_summary()
        assert r["cp_tension_sigma"] < 2.0

    def test_cp_consistent_2sigma(self):
        r = pillar184_summary()
        assert r["cp_consistent_2sigma"] is True

    def test_free_parameters_zero(self):
        r = pillar184_summary()
        assert r["free_parameters"] == 0

    def test_status_contains_closed(self):
        r = pillar184_summary()
        assert "CLOSED" in r["status"]

    def test_status_contains_zero_free(self):
        r = pillar184_summary()
        assert "zero" in r["status"].lower() or "Zero" in r["status"]

    def test_sources_list_present(self):
        r = pillar184_summary()
        sources = r["sources"]
        assert isinstance(sources, list)
        assert len(sources) >= 3

    def test_sources_contains_this_module(self):
        r = pillar184_summary()
        combined = " ".join(r["sources"])
        assert "ckm_braid_lagrangian" in combined or "Pillar 184" in combined

    def test_peer_review_response_present(self):
        r = pillar184_summary()
        assert "peer_review_response" in r
        assert len(r["peer_review_response"]) > 50

    def test_version_v9_39(self):
        r = pillar184_summary()
        assert "v9.39" in r["version"] or "9.39" in r["version"]

    def test_title_mentions_ckm(self):
        r = pillar184_summary()
        assert "CKM" in r["title"] or "Braid" in r["title"]


# ===========================================================================
# Cross-consistency tests
# ===========================================================================

class TestCrossConsistency:
    def test_n1_n2_satisfies_k_cs(self):
        r = coprime_braid_selection(5)
        assert r["n1"]**2 + r["n2"]**2 == r["k_cs"]

    def test_n1_n2_coprime(self):
        r = coprime_braid_selection(5)
        assert math.gcd(r["n1"], r["n2"]) == 1

    def test_derivation_chain_consistent(self):
        selection = coprime_braid_selection(5)
        proof = braid_pair_uniqueness_proof(5)
        cp = cp_phase_from_braid(selection["n1"], selection["n2"])
        chain = ckm_cp_braid_lagrangian_derivation(5)

        assert selection["n2"] == proof["n2_derived"]
        assert chain["step_3_n2"]["n2"] == selection["n2"]
        assert chain["step_4_delta"]["delta_deg"] == pytest.approx(cp["delta_deg"], rel=1e-9)

    def test_summary_consistent_with_functions(self):
        summary = pillar184_summary()
        cp = cp_phase_from_braid()
        assert summary["cp_phase_deg"] == pytest.approx(cp["delta_deg"], rel=1e-9)
        assert summary["cp_tension_sigma"] == pytest.approx(cp["sigma_tension"], rel=1e-6)

    def test_all_derivation_steps_have_proved_status(self):
        r = coprime_braid_selection(5)
        statuses = [s["status"] for s in r["derivation_steps"]]
        # Steps 5, 6, 7 should be VERIFIED or UNIQUE (not FAILED)
        assert "FAILED" not in statuses

    def test_cp_phase_formula(self):
        # Verify the formula independently
        delta = 2.0 * math.atan2(5, 7)
        r = cp_phase_from_braid(5, 7)
        assert r["delta_rad"] == pytest.approx(delta, rel=1e-9)
        assert r["delta_deg"] == pytest.approx(math.degrees(delta), rel=1e-9)
