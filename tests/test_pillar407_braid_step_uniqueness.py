# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 407 — Minimum-Step Braid Step-Width Uniqueness Certificate."""
import math
import pytest

from src.core.pillar407_braid_step_uniqueness import (
    PILLAR_STATUS,
    ADMISSION_2_RESIDUAL_STATUS,
    K_CS_CANONICAL,
    PI_KR_CANONICAL,
    euclidean_cs_action_ratio,
    z2_odd_braid_pairs,
    pillar67_valid_braid_pairs,
    action_ratio_table,
    second_variation_positive,
    winding_tension_suppression,
    monotonicity_theorem,
    braid_uniqueness_certificate,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == "BRAID_UNIQUENESS_CERTIFIED"

    def test_admission_status(self):
        assert ADMISSION_2_RESIDUAL_STATUS == "BRAID_UNIQUENESS_CERTIFIED"

    def test_k_cs(self):
        assert K_CS_CANONICAL == 74

    def test_pi_kr(self):
        assert PI_KR_CANONICAL == 37

    def test_k_cs_is_5sq_plus_7sq(self):
        assert K_CS_CANONICAL == 5 ** 2 + 7 ** 2


class TestActionRatio:
    def test_canonical_ratio_is_1(self):
        ratio = euclidean_cs_action_ratio(5, 7)
        assert abs(ratio - 1.0) < 1e-10

    def test_action_formula(self):
        assert euclidean_cs_action_ratio(3, 5) == pytest.approx((9 + 25) / 74)

    def test_action_increases_with_winding(self):
        r57 = euclidean_cs_action_ratio(5, 7)
        r59 = euclidean_cs_action_ratio(5, 9)
        r511 = euclidean_cs_action_ratio(5, 11)
        assert r59 > r57
        assert r511 > r59

    def test_pillar67_valid_pairs_57_smallest(self):
        # Among Pillar-67-valid pairs {(5,7), (7,9)}, (5,7) has smaller action
        r57 = euclidean_cs_action_ratio(5, 7)
        r79 = euclidean_cs_action_ratio(7, 9)
        assert r57 < r79

    def test_57_is_global_minimum_among_valid(self):
        pairs = pillar67_valid_braid_pairs()
        min_ratio = min(euclidean_cs_action_ratio(n1, n2) for n1, n2 in pairs)
        assert abs(min_ratio - 1.0) < 1e-10


class TestZ2OddPairs:
    def test_57_in_list(self):
        pairs = z2_odd_braid_pairs(max_n=9)
        assert (5, 7) in pairs

    def test_all_pairs_odd(self):
        pairs = z2_odd_braid_pairs(max_n=15)
        for n1, n2 in pairs:
            assert n1 % 2 == 1 and n2 % 2 == 1

    def test_all_pairs_ordered(self):
        pairs = z2_odd_braid_pairs(max_n=15)
        for n1, n2 in pairs:
            assert n2 > n1

    def test_pair_count(self):
        pairs = z2_odd_braid_pairs(max_n=9)
        assert len(pairs) > 0

    def test_pillar67_valid_pairs_returns_two(self):
        pairs = pillar67_valid_braid_pairs()
        assert (5, 7) in pairs
        assert (7, 9) in pairs
        assert len(pairs) == 2


class TestActionRatioTable:
    def test_57_in_table(self):
        table = action_ratio_table(max_n=15)
        entry_57 = next((r for r in table if r["n1"] == 5 and r["n2"] == 7), None)
        assert entry_57 is not None

    def test_canonical_ratio_one(self):
        table = action_ratio_table(max_n=15)
        entry_57 = next(r for r in table if r["n1"] == 5 and r["n2"] == 7)
        assert abs(entry_57["action_ratio"] - 1.0) < 1e-6

    def test_79_subdominant(self):
        table = action_ratio_table(max_n=15)
        entry_79 = next(r for r in table if r["n1"] == 7 and r["n2"] == 9)
        assert entry_79["action_ratio"] > 1.0
        assert entry_79["subdominant"] is True

    def test_winding_suppression_minimum_step(self):
        table = action_ratio_table(max_n=9)
        for row in table:
            if row["n1"] == 5 and row["n2"] == 7:
                assert row["delta_n_above_min"] == 0
                assert abs(row["winding_suppression"] - 1.0) < 1e-10

    def test_winding_suppression_59(self):
        table = action_ratio_table(max_n=9)
        for row in table:
            if row["n1"] == 5 and row["n2"] == 9:
                assert row["delta_n_above_min"] == 2
                assert row["winding_suppression"] < 1e-30


class TestSecondVariation:
    def test_positive_definite(self):
        sv = second_variation_positive()
        assert sv["positive_definite"] is True

    def test_eigenvalue_positive(self):
        sv = second_variation_positive()
        assert sv["hessian_eigenvalue"] > 0

    def test_saddle_type(self):
        sv = second_variation_positive()
        assert sv["saddle_type"] == "STRICT_LOCAL_MINIMUM"

    def test_eigenvalue_formula(self):
        sv = second_variation_positive()
        expected = 2 * math.pi / 74
        assert abs(sv["hessian_eigenvalue"] - expected) < 1e-12


class TestWindingTensionSuppression:
    def test_57_is_minimum_step(self):
        data = winding_tension_suppression(5, 7)
        assert data["delta_n"] == 0
        assert abs(data["suppression_factor"] - 1.0) < 1e-10
        assert data["verdict"] == "MINIMUM_STEP"

    def test_59_suppressed(self):
        data = winding_tension_suppression(5, 9)
        assert data["delta_n"] == 2
        assert data["suppression_factor"] < 1e-30
        assert data["verdict"] == "SUPPRESSED"

    def test_511_more_suppressed_than_59(self):
        d59 = winding_tension_suppression(5, 9)
        d511 = winding_tension_suppression(5, 11)
        assert d511["suppression_factor"] < d59["suppression_factor"]

    def test_exponent_formula(self):
        data = winding_tension_suppression(5, 9)
        expected_exp = -2 * PI_KR_CANONICAL
        assert abs(data["suppression_exponent"] - expected_exp) < 1e-10


class TestMonotonicityTheorem:
    def test_theorem_verified(self):
        mono = monotonicity_theorem(n_w_values=(5, 7))
        assert mono["theorem_verified"] is True

    def test_unique_minimum_is_57(self):
        mono = monotonicity_theorem(n_w_values=(5, 7))
        assert mono["unique_global_minimum"] is True
        assert mono["minimum_pair"] == (5, 7)

    def test_all_ratios_above_1(self):
        mono = monotonicity_theorem(n_w_values=(5, 7))
        for row in mono["table"]:
            assert row["above_unity"] is True

    def test_min_ratio_is_1(self):
        mono = monotonicity_theorem(n_w_values=(5, 7))
        assert abs(mono["minimum_ratio"] - 1.0) < 1e-10


class TestBraidUniquenessCertificate:
    def test_status_certified(self):
        cert = braid_uniqueness_certificate()
        assert cert["status"] == "BRAID_UNIQUENESS_CERTIFIED"

    def test_admission_2_closed(self):
        cert = braid_uniqueness_certificate()
        assert cert["admission_2_residual"] == "BRAID_UNIQUENESS_CERTIFIED"

    def test_all_four_proofs(self):
        cert = braid_uniqueness_certificate()
        assert "proof_a_global_action_minimum" in cert
        assert "proof_b_second_variation" in cert
        assert "proof_c_winding_tension_suppression" in cert
        assert "proof_d_monotonicity_theorem" in cert

    def test_proof_a_verified(self):
        cert = braid_uniqueness_certificate()
        assert cert["proof_a_global_action_minimum"]["verified"] is True
        assert cert["proof_a_global_action_minimum"]["minimum_pair"] == (5, 7)

    def test_proof_b_verified(self):
        cert = braid_uniqueness_certificate()
        assert cert["proof_b_second_variation"]["positive_definite"] is True

    def test_proof_c_57_minimum_step(self):
        cert = braid_uniqueness_certificate()
        assert cert["proof_c_winding_tension_suppression"]["(5,7)_ref"]["verdict"] == "MINIMUM_STEP"

    def test_proof_c_higher_suppressed(self):
        cert = braid_uniqueness_certificate()
        for key in ["(5,9)", "(5,11)", "(7,11)"]:
            assert cert["proof_c_winding_tension_suppression"][key]["verdict"] == "SUPPRESSED"

    def test_proof_d_verified(self):
        cert = braid_uniqueness_certificate()
        assert cert["proof_d_monotonicity_theorem"]["theorem_verified"] is True

    def test_verdict_contains_closed(self):
        cert = braid_uniqueness_certificate()
        assert "Admission 2 residual CLOSED" in cert["verdict"]
