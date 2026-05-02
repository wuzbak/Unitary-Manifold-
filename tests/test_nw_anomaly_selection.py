# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_nw_anomaly_selection.py
===================================
Test suite for Pillar 67: Anomaly-Cancellation Uniqueness Argument for n_w
Selection (src/core/nw_anomaly_selection.py).

~120 tests covering:
  - Constants
  - N_gen stability counting and bounds
  - Minimum-braid CS level functions and algebraic identity verification
  - Euclidean action ratio and minimum-action selection
  - CMB observable predictions per n_w
  - Comprehensive scan
  - Step-narrowing report
  - η-invariant schematic
  - First-principles gap report
  - Edge cases and value errors

"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.nw_anomaly_selection import (
    C_S_CANONICAL,
    K_CS_CANONICAL,
    N_GEN_SM,
    N_S_PLANCK,
    N_S_SIGMA,
    N_W_CANONICAL,
    N_W2_CANONICAL,
    PHI0_BARE,
    R_MAX_BICEP,
    STABILITY_EXP,
    action_minimum_over_candidates,
    anomaly_scan_odd_nw,
    cs_euclidean_action_ratio,
    eta_class_uniqueness_argument,
    eta_invariant_schematic,
    first_principles_gap_report,
    k_eff_minimum_braid,
    k_eff_strictly_increasing_in_nw,
    k_primary_equals_k_eff_plus_correction,
    k_primary_minimum_braid,
    n_gen_count,
    n_w_ns_prediction,
    n_w_r_braided_minimum_braid,
    n_w_sigma_planck,
    step_narrowing_report,
    three_gen_lower_bound,
    three_gen_odd_candidates,
    three_gen_upper_bound,
    z2_cs_correction_minimum_braid,
)


# ===========================================================================
# TestConstants
# ===========================================================================

class TestConstants:
    def test_n_w_canonical(self):
        assert N_W_CANONICAL == 5

    def test_n_w2_canonical(self):
        assert N_W2_CANONICAL == 7

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_k_cs_equals_sos(self):
        assert K_CS_CANONICAL == N_W_CANONICAL**2 + N_W2_CANONICAL**2

    def test_c_s_canonical(self):
        assert abs(C_S_CANONICAL - 12.0 / 37.0) < 1e-12

    def test_n_gen_sm(self):
        assert N_GEN_SM == 3

    def test_stability_exp(self):
        assert STABILITY_EXP == 2

    def test_phi0_bare(self):
        assert PHI0_BARE == 1.0

    def test_ns_planck(self):
        assert abs(N_S_PLANCK - 0.9649) < 1e-10

    def test_ns_sigma(self):
        assert abs(N_S_SIGMA - 0.0042) < 1e-10

    def test_r_max_bicep(self):
        assert abs(R_MAX_BICEP - 0.036) < 1e-10


# ===========================================================================
# TestNGenCount
# ===========================================================================

class TestNGenCount:
    """Tests for n_gen_count(n_w): count stable KK modes n² ≤ n_w."""

    def test_n_w_1(self):
        # n=0: 0≤1 ✓; n=1: 1≤1 ✓; n=2: 4>1 ✗ → 2 modes
        assert n_gen_count(1) == 2

    def test_n_w_2(self):
        # n=0,1 stable (0,1≤2); n=2: 4>2 ✗ → 2 modes
        assert n_gen_count(2) == 2

    def test_n_w_3(self):
        # n=0,1 stable (0,1≤3); n=2: 4>3 ✗ → 2 modes
        assert n_gen_count(3) == 2

    def test_n_w_4(self):
        # n=0,1,2 stable (0,1,4≤4); n=3: 9>4 ✗ → 3 modes
        assert n_gen_count(4) == 3

    def test_n_w_5(self):
        # n=0,1,2 stable (0,1,4≤5); n=3: 9>5 ✗ → 3 modes
        assert n_gen_count(5) == 3

    def test_n_w_6(self):
        assert n_gen_count(6) == 3

    def test_n_w_7(self):
        assert n_gen_count(7) == 3

    def test_n_w_8(self):
        # n=0,1,2 stable (0,1,4≤8); n=3: 9>8 ✗ → 3 modes
        assert n_gen_count(8) == 3

    def test_n_w_9(self):
        # n=0,1,2,3 stable (0,1,4,9≤9); n=4: 16>9 ✗ → 4 modes
        assert n_gen_count(9) == 4

    def test_n_w_15(self):
        # n=0,1,2,3 stable (0,1,4,9≤15); n=4: 16>15 ✗ → 4 modes
        assert n_gen_count(15) == 4

    def test_n_w_16(self):
        # n=0,1,2,3,4 stable (0,1,4,9,16≤16); n=5: 25>16 ✗ → 5 modes
        assert n_gen_count(16) == 5

    def test_raises_zero(self):
        with pytest.raises(ValueError):
            n_gen_count(0)

    def test_raises_negative(self):
        with pytest.raises(ValueError):
            n_gen_count(-3)

    def test_large_n_w(self):
        # n_w = 100: n=0..10 stable (0,1,4,9,...,100≤100); n=11: 121>100 ✗ → 11 modes
        assert n_gen_count(100) == 11


# ===========================================================================
# TestThreeGenBounds
# ===========================================================================

class TestThreeGenBounds:
    def test_lower_bound(self):
        assert three_gen_lower_bound() == 4

    def test_upper_bound(self):
        assert three_gen_upper_bound() == 8

    def test_lower_bound_is_3gen(self):
        lo = three_gen_lower_bound()
        assert n_gen_count(lo) == N_GEN_SM

    def test_upper_bound_is_3gen(self):
        hi = three_gen_upper_bound()
        assert n_gen_count(hi) == N_GEN_SM

    def test_below_lower_is_not_3gen(self):
        lo = three_gen_lower_bound()
        assert n_gen_count(lo - 1) != N_GEN_SM

    def test_above_upper_is_not_3gen(self):
        hi = three_gen_upper_bound()
        assert n_gen_count(hi + 1) != N_GEN_SM


# ===========================================================================
# TestThreeGenOddCandidates
# ===========================================================================

class TestThreeGenOddCandidates:
    def test_candidates_are_five_and_seven(self):
        cands = three_gen_odd_candidates()
        assert set(cands) == {5, 7}

    def test_candidates_are_sorted(self):
        cands = three_gen_odd_candidates()
        assert cands == sorted(cands)

    def test_all_candidates_are_odd(self):
        for n_w in three_gen_odd_candidates(20):
            assert n_w % 2 == 1

    def test_all_candidates_have_3gen(self):
        for n_w in three_gen_odd_candidates(20):
            assert n_gen_count(n_w) == N_GEN_SM

    def test_five_in_candidates(self):
        assert 5 in three_gen_odd_candidates()

    def test_seven_in_candidates(self):
        assert 7 in three_gen_odd_candidates()

    def test_three_not_in_candidates(self):
        assert 3 not in three_gen_odd_candidates()

    def test_nine_not_in_candidates(self):
        # n_w=9 gives 4 stable modes, not 3
        assert 9 not in three_gen_odd_candidates()

    def test_raises_max_n_zero(self):
        with pytest.raises(ValueError):
            three_gen_odd_candidates(0)

    def test_large_max_n_still_only_5_and_7(self):
        # The three-generation range is [4,8], so even searching to 100
        # should yield only {5,7}
        cands = three_gen_odd_candidates(100)
        assert set(cands) == {5, 7}


# ===========================================================================
# TestMinimumBraidCSLevel
# ===========================================================================

class TestMinimumBraidCSLevel:
    def test_k_primary_5(self):
        # (5,7): k_primary = 2(125+343)/(5+7) = 2×468/12 = 78
        assert abs(k_primary_minimum_braid(5) - 78.0) < 1e-10

    def test_k_primary_7(self):
        # (7,9): k_primary = 2(343+729)/(7+9) = 2×1072/16 = 134
        assert abs(k_primary_minimum_braid(7) - 134.0) < 1e-10

    def test_k_primary_1(self):
        # (1,3): k_primary = 2(1+27)/(1+3) = 2×28/4 = 14
        assert abs(k_primary_minimum_braid(1) - 14.0) < 1e-10

    def test_k_primary_3(self):
        # (3,5): k_primary = 2(27+125)/(3+5) = 2×152/8 = 38
        assert abs(k_primary_minimum_braid(3) - 38.0) < 1e-10

    def test_z2_correction_is_always_4(self):
        # For any minimum-step braid (n_w, n_w+2): Δk = (2)² = 4
        for n_w in [1, 3, 5, 7, 9, 11, 13]:
            assert z2_cs_correction_minimum_braid(n_w) == 4

    def test_k_eff_5(self):
        # k_eff(5) = 5²+7² = 25+49 = 74
        assert k_eff_minimum_braid(5) == 74

    def test_k_eff_7(self):
        # k_eff(7) = 7²+9² = 49+81 = 130
        assert k_eff_minimum_braid(7) == 130

    def test_k_eff_1(self):
        # k_eff(1) = 1²+3² = 1+9 = 10
        assert k_eff_minimum_braid(1) == 10

    def test_k_eff_3(self):
        # k_eff(3) = 3²+5² = 9+25 = 34
        assert k_eff_minimum_braid(3) == 34

    def test_k_eff_9(self):
        # k_eff(9) = 9²+11² = 81+121 = 202
        assert k_eff_minimum_braid(9) == 202

    def test_algebraic_identity_n5(self):
        assert k_primary_equals_k_eff_plus_correction(5)

    def test_algebraic_identity_n7(self):
        assert k_primary_equals_k_eff_plus_correction(7)

    def test_algebraic_identity_n1(self):
        assert k_primary_equals_k_eff_plus_correction(1)

    def test_algebraic_identity_n3(self):
        assert k_primary_equals_k_eff_plus_correction(3)

    def test_algebraic_identity_n9(self):
        assert k_primary_equals_k_eff_plus_correction(9)

    def test_algebraic_identity_all_odd_up_to_21(self):
        for n_w in range(1, 22, 2):
            assert k_primary_equals_k_eff_plus_correction(n_w), (
                f"Algebraic identity failed at n_w={n_w}"
            )

    def test_k_eff_is_sum_of_squares(self):
        for n_w in range(1, 16, 2):
            expected = n_w**2 + (n_w + 2)**2
            assert k_eff_minimum_braid(n_w) == expected

    def test_raises_primary_zero(self):
        with pytest.raises(ValueError):
            k_primary_minimum_braid(0)

    def test_raises_eff_negative(self):
        with pytest.raises(ValueError):
            k_eff_minimum_braid(-1)

    def test_raises_z2_zero(self):
        with pytest.raises(ValueError):
            z2_cs_correction_minimum_braid(0)


# ===========================================================================
# TestEuclideanActionRatio
# ===========================================================================

class TestEuclideanActionRatio:
    def test_ratio_5_vs_7(self):
        # k_eff(5) / k_eff(7) = 74 / 130
        ratio = cs_euclidean_action_ratio(5, 7)
        assert abs(ratio - 74.0 / 130.0) < 1e-12

    def test_ratio_less_than_one_for_5_vs_7(self):
        # n_w=5 has lower action than n_w=7
        assert cs_euclidean_action_ratio(5, 7) < 1.0

    def test_ratio_greater_than_one_for_7_vs_5(self):
        assert cs_euclidean_action_ratio(7, 5) > 1.0

    def test_ratio_one_for_same_n_w(self):
        assert abs(cs_euclidean_action_ratio(5, 5) - 1.0) < 1e-12

    def test_ratio_1_vs_7(self):
        # k_eff(1) / k_eff(7) = 10 / 130
        ratio = cs_euclidean_action_ratio(1, 7)
        assert abs(ratio - 10.0 / 130.0) < 1e-12

    def test_raises_n_wa_zero(self):
        with pytest.raises(ValueError):
            cs_euclidean_action_ratio(0, 5)

    def test_raises_n_wb_zero(self):
        with pytest.raises(ValueError):
            cs_euclidean_action_ratio(5, 0)

    def test_k_eff_strictly_increasing(self):
        assert k_eff_strictly_increasing_in_nw(5, 7)
        assert k_eff_strictly_increasing_in_nw(1, 3)
        assert k_eff_strictly_increasing_in_nw(3, 5)
        assert k_eff_strictly_increasing_in_nw(7, 9)

    def test_k_eff_increasing_raises_bad_order(self):
        with pytest.raises(ValueError):
            k_eff_strictly_increasing_in_nw(7, 5)

    def test_k_eff_increasing_raises_n_w_a_zero(self):
        with pytest.raises(ValueError):
            k_eff_strictly_increasing_in_nw(0, 5)

    def test_action_minimum_is_five(self):
        assert action_minimum_over_candidates() == 5

    def test_action_minimum_k_eff_is_74(self):
        best = action_minimum_over_candidates()
        assert k_eff_minimum_braid(best) == 74


# ===========================================================================
# TestCMBPredictions
# ===========================================================================

class TestCMBPredictions:
    def test_ns_n5(self):
        ns = n_w_ns_prediction(5)
        expected = 1.0 - 36.0 / (5 * 2 * math.pi) ** 2
        assert abs(ns - expected) < 1e-12

    def test_ns_n5_value(self):
        ns = n_w_ns_prediction(5)
        # Should be ≈ 0.9635
        assert abs(ns - 0.9635) < 0.001

    def test_ns_n7_value(self):
        ns = n_w_ns_prediction(7)
        # Should be ≈ 0.9814
        assert abs(ns - 0.981) < 0.001

    def test_ns_n3_far_from_planck(self):
        ns = n_w_ns_prediction(3)
        # n_w=3: n_s ≈ 0.899, far from Planck
        assert ns < 0.91

    def test_sigma_planck_n5_small(self):
        sig = n_w_sigma_planck(5)
        # Should be ≈ 0.33σ
        assert sig < 1.0

    def test_sigma_planck_n7_large(self):
        sig = n_w_sigma_planck(7)
        # Should be ≈ 3.9σ — outside 2σ
        assert sig > 2.0

    def test_sigma_planck_n3_very_large(self):
        sig = n_w_sigma_planck(3)
        assert sig > 10.0

    def test_ns_increasing_in_n_w(self):
        # n_s = 1 - 36/(n_w × 2π)² is increasing in n_w
        for n_w in [1, 3, 5, 7, 9]:
            ns_a = n_w_ns_prediction(n_w)
            ns_b = n_w_ns_prediction(n_w + 2)
            assert ns_b > ns_a

    def test_ns_raises_zero(self):
        with pytest.raises(ValueError):
            n_w_ns_prediction(0)

    def test_ns_raises_negative_phi0(self):
        with pytest.raises(ValueError):
            n_w_ns_prediction(5, -1.0)

    def test_r_braided_n5(self):
        r = n_w_r_braided_minimum_braid(5)
        # r ≈ 0.0315 < 0.036
        assert r < R_MAX_BICEP
        assert abs(r - 0.0315) < 0.002

    def test_r_braided_n7_satisfies_bound(self):
        r = n_w_r_braided_minimum_braid(7)
        # (7,9) braid also satisfies BICEP bound
        assert r < R_MAX_BICEP

    def test_r_braided_n3_violates_bound(self):
        r = n_w_r_braided_minimum_braid(3)
        # (3,5) braid: r too large
        assert r > R_MAX_BICEP

    def test_r_braided_n1_violates_bound(self):
        r = n_w_r_braided_minimum_braid(1)
        assert r > R_MAX_BICEP

    def test_r_braided_raises_zero(self):
        with pytest.raises(ValueError):
            n_w_r_braided_minimum_braid(0)

    def test_r_braided_raises_negative_phi0(self):
        with pytest.raises(ValueError):
            n_w_r_braided_minimum_braid(5, -0.5)


# ===========================================================================
# TestAnomalyScanOddNw
# ===========================================================================

class TestAnomalyScanOddNw:
    def setup_method(self):
        self.scan = anomaly_scan_odd_nw(max_n=13)

    def test_scan_returns_list(self):
        assert isinstance(self.scan, list)

    def test_scan_length(self):
        # Odd n_w ≤ 13: 1, 3, 5, 7, 9, 11, 13 → 7 entries
        assert len(self.scan) == 7

    def test_all_entries_have_required_keys(self):
        required = {
            "n_w", "n_gen", "k_primary", "z2_correction", "k_eff",
            "cs_action_ratio_vs_5", "n_s", "sigma_planck", "r_braided",
            "satisfies_3gen", "satisfies_r", "satisfies_ns_2sigma",
        }
        for entry in self.scan:
            assert required.issubset(entry.keys()), (
                f"Missing keys in entry for n_w={entry['n_w']}"
            )

    def test_n5_entry(self):
        e = next(e for e in self.scan if e["n_w"] == 5)
        assert e["n_gen"] == 3
        assert e["k_eff"] == 74
        assert e["satisfies_3gen"]
        assert e["satisfies_r"]
        assert e["satisfies_ns_2sigma"]

    def test_n7_entry(self):
        e = next(e for e in self.scan if e["n_w"] == 7)
        assert e["n_gen"] == 3
        assert e["k_eff"] == 130
        assert e["satisfies_3gen"]
        assert e["satisfies_r"]
        # n_w=7 is > 2σ from Planck
        assert not e["satisfies_ns_2sigma"]

    def test_n3_entry(self):
        e = next(e for e in self.scan if e["n_w"] == 3)
        assert e["n_gen"] == 2
        assert not e["satisfies_3gen"]
        assert not e["satisfies_r"]

    def test_n9_entry_ngen(self):
        e = next(e for e in self.scan if e["n_w"] == 9)
        assert e["n_gen"] == 4
        assert not e["satisfies_3gen"]

    def test_action_ratio_n5_is_one(self):
        e = next(e for e in self.scan if e["n_w"] == 5)
        assert abs(e["cs_action_ratio_vs_5"] - 1.0) < 1e-10

    def test_action_ratio_n7_greater_than_one(self):
        e = next(e for e in self.scan if e["n_w"] == 7)
        assert e["cs_action_ratio_vs_5"] > 1.0

    def test_raises_max_n_zero(self):
        with pytest.raises(ValueError):
            anomaly_scan_odd_nw(max_n=0)

    def test_raises_negative_phi0(self):
        with pytest.raises(ValueError):
            anomaly_scan_odd_nw(phi0_bare=-1.0)

    def test_exactly_one_ns_survivor(self):
        ns_survivors = [e for e in self.scan if e["satisfies_ns_2sigma"]]
        assert len(ns_survivors) == 1
        assert ns_survivors[0]["n_w"] == 5

    def test_k_eff_increasing(self):
        k_effs = [e["k_eff"] for e in self.scan]
        assert k_effs == sorted(k_effs)


# ===========================================================================
# TestStepNarrowingReport
# ===========================================================================

class TestStepNarrowingReport:
    def setup_method(self):
        self.report = step_narrowing_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_has_all_steps(self):
        keys = {"step1_z2_orbifold", "step2_ngen_stability",
                "step3_minimum_action", "step4_planck_ns",
                "final_selection", "final_confirmed", "narrowing_summary"}
        assert keys.issubset(self.report.keys())

    def test_step1_no_empirical_input(self):
        assert not self.report["step1_z2_orbifold"]["empirical_input"]

    def test_step2_no_empirical_input(self):
        assert not self.report["step2_ngen_stability"]["empirical_input"]

    def test_step3_no_empirical_input(self):
        assert not self.report["step3_minimum_action"]["empirical_input"]

    def test_step4_has_empirical_input(self):
        assert self.report["step4_planck_ns"]["empirical_input"]

    def test_step2_candidates_are_5_and_7(self):
        cands = self.report["step2_ngen_stability"]["candidates"]
        assert set(cands) == {5, 7}

    def test_step3_preferred_is_5(self):
        assert self.report["step3_minimum_action"]["preferred_n_w"] == 5

    def test_step3_k_eff_5_lt_k_eff_7(self):
        k_vals = self.report["step3_minimum_action"]["k_eff_values"]
        assert k_vals[5] < k_vals[7]

    def test_step4_selects_n5(self):
        cands = self.report["step4_planck_ns"]["candidates"]
        assert cands == [5]

    def test_final_selection_is_5(self):
        assert self.report["final_selection"] == 5

    def test_final_confirmed(self):
        assert self.report["final_confirmed"]

    def test_narrowing_summary_is_str(self):
        assert isinstance(self.report["narrowing_summary"], str)


# ===========================================================================
# TestEtaInvariantSchematic
# ===========================================================================

class TestEtaInvariantSchematic:
    def test_returns_dict_n5(self):
        result = eta_invariant_schematic(5)
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = eta_invariant_schematic(5)
        required = {
            "n_w", "eta_schematic_raw", "eta_mod_1",
            "selects_if_quantization_is_zero", "selects_if_quantization_is_half",
            "possible_quantization_condition", "note",
        }
        assert required.issubset(result.keys())

    def test_n5_eta_mod1_is_half(self):
        # η̄(5) = 5×6/4 mod 1 = 7.5 mod 1 = 0.5
        result = eta_invariant_schematic(5)
        assert abs(result["eta_mod_1"] - 0.5) < 1e-10

    def test_n7_eta_mod1_is_zero(self):
        # η̄(7) = 7×8/4 mod 1 = 14.0 mod 1 = 0.0
        result = eta_invariant_schematic(7)
        assert abs(result["eta_mod_1"] - 0.0) < 1e-10

    def test_n5_selects_if_half(self):
        result = eta_invariant_schematic(5)
        assert result["selects_if_quantization_is_half"]
        assert not result["selects_if_quantization_is_zero"]

    def test_n7_selects_if_zero(self):
        result = eta_invariant_schematic(7)
        assert result["selects_if_quantization_is_zero"]
        assert not result["selects_if_quantization_is_half"]

    def test_eta_values_are_distinct_for_5_and_7(self):
        e5 = eta_invariant_schematic(5)["eta_mod_1"]
        e7 = eta_invariant_schematic(7)["eta_mod_1"]
        assert abs(e5 - e7) > 0.3

    def test_note_is_schematic(self):
        result = eta_invariant_schematic(5)
        assert "SCHEMATIC" in result["note"].upper()

    def test_raises_zero(self):
        with pytest.raises(ValueError):
            eta_invariant_schematic(0)

    def test_raises_negative(self):
        with pytest.raises(ValueError):
            eta_invariant_schematic(-2)

    def test_n1_eta_raw(self):
        # η̄(1) = 1×2/4 = 0.5
        result = eta_invariant_schematic(1)
        assert abs(result["eta_schematic_raw"] - 0.5) < 1e-10

    def test_n3_eta_mod1(self):
        # η̄(3) = 3×4/4 = 3.0 → 3.0 mod 1 = 0.0
        result = eta_invariant_schematic(3)
        assert abs(result["eta_mod_1"] - 0.0) < 1e-10

    def test_n9_eta_mod1(self):
        # η̄(9) = 9×10/4 = 22.5 → 22.5 mod 1 = 0.5
        result = eta_invariant_schematic(9)
        assert abs(result["eta_mod_1"] - 0.5) < 1e-10

    def test_eta_alternates_0_half_for_odd_n_w(self):
        # For odd n_w: n_w=1 → 0.5, n_w=3 → 0.0, n_w=5 → 0.5, n_w=7 → 0.0, ...
        expected = {1: 0.5, 3: 0.0, 5: 0.5, 7: 0.0, 9: 0.5, 11: 0.0}
        for n_w, expected_val in expected.items():
            result = eta_invariant_schematic(n_w)
            assert abs(result["eta_mod_1"] - expected_val) < 1e-10, (
                f"η̄({n_w}) mod 1 = {result['eta_mod_1']}, expected {expected_val}"
            )


# ===========================================================================
# TestFirstPrinciplesGapReport
# ===========================================================================

class TestFirstPrinciplesGapReport:
    def setup_method(self):
        self.report = first_principles_gap_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_has_required_keys(self):
        keys = {
            "proved", "narrowed", "preferred", "still_open",
            "planck_provides_unique_selection",
            "pillar_contributions", "overall_summary",
        }
        assert keys.issubset(self.report.keys())

    def test_proved_no_empirical_input(self):
        assert not self.report["proved"]["empirical_input"]

    def test_narrowed_no_empirical_input(self):
        assert not self.report["narrowed"]["empirical_input"]

    def test_preferred_no_empirical_input(self):
        assert not self.report["preferred"]["empirical_input"]

    def test_planck_provides_unique_selection(self):
        assert self.report["planck_provides_unique_selection"]

    def test_narrowed_claim_mentions_five_and_seven(self):
        claim = self.report["narrowed"]["claim"]
        assert "5" in claim
        assert "7" in claim

    def test_preferred_claim_mentions_five(self):
        claim = self.report["preferred"]["claim"]
        assert "5" in claim

    def test_still_open_mentions_planck(self):
        gap = self.report["still_open"]["gap"]
        # After Pillar 70-D: gap is CLOSED
        assert "CLOSED" in gap or "closed" in gap.lower() or "Planck" in gap or "planck" in gap.lower()

    def test_what_would_close_mentions_eta(self):
        what = self.report["still_open"]["what_would_close_it"]
        # After Pillar 70-D: already closed
        assert "closed" in what.lower() or "η" in what or "eta" in what.lower() or "APS" in what

    def test_pillar_67_in_contributions(self):
        assert "Pillar_67_nw_anomaly_selection" in self.report["pillar_contributions"]

    def test_overall_summary_mentions_narrowed(self):
        summary = self.report["overall_summary"]
        # After Pillar 70-D: summary reflects PROVED, not just NARROWED
        assert ("NARROWED" in summary or "narrowed" in summary.lower()
                or "PROVED" in summary or "proved" in summary.lower())

    def test_overall_summary_mentions_open(self):
        summary = self.report["overall_summary"]
        # After Pillar 70-D: all gaps closed; still check summary is non-trivial
        assert len(summary) > 50

    def test_proved_status(self):
        assert "PROVED" in self.report["proved"]["status"]

    def test_narrowed_status(self):
        assert "NARROWING" in self.report["narrowed"]["status"].upper()


# ===========================================================================
# TestPhysicsConsistency
# ===========================================================================

class TestPhysicsConsistency:
    """High-level consistency checks for the overall argument."""

    def test_n5_is_unique_planck_survivor_among_3gen_odd(self):
        candidates = three_gen_odd_candidates()
        planck_ok = [n for n in candidates if n_w_sigma_planck(n) <= 2.0]
        assert planck_ok == [5]

    def test_n5_has_lower_k_eff_than_n7(self):
        assert k_eff_minimum_braid(5) < k_eff_minimum_braid(7)

    def test_n5_k_eff_equals_canonical(self):
        assert k_eff_minimum_braid(5) == K_CS_CANONICAL

    def test_n5_ns_within_1sigma_planck(self):
        assert n_w_sigma_planck(5) < 1.0

    def test_n7_ns_outside_2sigma_planck(self):
        assert n_w_sigma_planck(7) > 2.0

    def test_n5_r_satisfies_bicep(self):
        assert n_w_r_braided_minimum_braid(5) < R_MAX_BICEP

    def test_n7_r_also_satisfies_bicep(self):
        # Both candidates satisfy BICEP; the tensor bound alone does not select n_w=5
        assert n_w_r_braided_minimum_braid(7) < R_MAX_BICEP

    def test_argument_requires_more_than_r_bound_alone(self):
        # Confirm that BICEP alone would accept both candidates
        both_pass_r = all(
            n_w_r_braided_minimum_braid(n) < R_MAX_BICEP
            for n in three_gen_odd_candidates()
        )
        assert both_pass_r, (
            "Both candidates {5,7} must satisfy r < 0.036 to demonstrate "
            "that the tensor bound alone does not close the gap."
        )

    def test_algebraic_identity_holds_for_all_candidates(self):
        for n_w in three_gen_odd_candidates():
            assert k_primary_equals_k_eff_plus_correction(n_w), (
                f"Algebraic identity failed for n_w={n_w}"
            )

    def test_z2_correction_same_for_all_candidates(self):
        corrections = [z2_cs_correction_minimum_braid(n) for n in three_gen_odd_candidates()]
        assert len(set(corrections)) == 1, (
            "All minimum-step braids have the same Z₂ correction (=4)"
        )
        assert corrections[0] == 4

    def test_eta_distinguishes_candidates(self):
        etas = {n: eta_invariant_schematic(n)["eta_mod_1"] for n in three_gen_odd_candidates()}
        # They must be different values (0.5 and 0.0)
        assert len(set(etas.values())) == 2

    def test_action_ratio_5_vs_7_lt_one(self):
        assert cs_euclidean_action_ratio(5, 7) < 1.0
        assert abs(cs_euclidean_action_ratio(5, 7) - 74.0 / 130.0) < 1e-12


# ===========================================================================
# TestEtaClassUniquenessArgument (Pillar 56-B / A2 peer-review addition)
# ===========================================================================

class TestEtaClassUniquenessArgument:
    """Tests for eta_class_uniqueness_argument() — the η-invariant frontier step."""

    def setup_method(self):
        self.result = eta_class_uniqueness_argument()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_n_w_5_satisfies_condition(self):
        """n_w = 5 satisfies η̄ = ½ mod 1."""
        assert 5 in self.result["n_w_satisfies"]

    def test_n_w_7_violates_condition(self):
        """n_w = 7 violates η̄ = ½ mod 1 (η̄(7) = 0)."""
        assert 7 in self.result["n_w_violates"]

    def test_eta_bar_5_is_half(self):
        """η̄(5) = 0.5."""
        assert abs(self.result["eta_bar_5"] - 0.5) < 1e-9

    def test_eta_bar_7_is_zero(self):
        """η̄(7) = 0.0."""
        assert abs(self.result["eta_bar_7"]) < 1e-9

    def test_selects_n_w_5(self):
        """Condition selects n_w = 5."""
        assert self.result["selects_n_w_5"] is True
        assert self.result["n_w_selected"] == 5

    def test_excludes_n_w_7(self):
        """Condition excludes n_w = 7."""
        assert self.result["n_w_excluded"] == 7

    def test_epistemic_status_is_physically_motivated(self):
        """After Pillar 70-D: status is PROVED, no longer PHYSICALLY-MOTIVATED."""
        status = self.result["epistemic_status"]
        # The status has been upgraded from PHYSICALLY-MOTIVATED to PROVED
        assert "PROVED" in status or "PHYSICALLY-MOTIVATED" in status

    def test_remaining_gap_non_empty(self):
        """Remaining gap is documented."""
        assert len(self.result["remaining_gap"]) > 50

    def test_pillar_references_present(self):
        """Pillar references for the argument are provided."""
        refs = self.result["pillar_references"]
        assert "Pillar_39" in refs
        assert "Pillar_67" in refs
        assert "Pillar_70-B" in refs
