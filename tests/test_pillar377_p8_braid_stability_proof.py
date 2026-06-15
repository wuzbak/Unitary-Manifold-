# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""tests/test_pillar377_p8_braid_stability_proof.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar377_p8_braid_stability_proof import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    N_W, N1, N2, K_CS, C_S, DELTA_N_MIN,
    separation_guard,
    dirichlet_bc_odd_constraint,
    minimum_step_derivation,
    second_variation_stability,
    larger_step_decay_rate,
    braid_action_comparison,
    z2_odd_braid_partners,
    p8_upgrade_certificate,
    pillar377_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 377
    def test_status(self): assert PILLAR_STATUS == "DERIVED_STRUCTURAL"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"
    def test_n_w(self): assert N_W == 5
    def test_n1(self): assert N1 == 5
    def test_n2(self): assert N2 == 7
    def test_k_cs(self): assert K_CS == 74
    def test_k_cs_from_n1_n2(self): assert N1**2 + N2**2 == K_CS
    def test_c_s(self): assert abs(C_S - 12.0/37.0) < 1e-10
    def test_delta_n_min(self): assert DELTA_N_MIN == 2
    def test_n1_odd(self): assert N1 % 2 == 1
    def test_n2_odd(self): assert N2 % 2 == 1


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
    def test_derived_structural(self): assert "DERIVED_STRUCTURAL" in separation_guard()
    def test_mentions_dirichlet(self):
        assert "BC" in separation_guard() or "Dirichlet" in separation_guard()


class TestDirichletBCOddConstraint:
    def test_returns_dict(self): assert isinstance(dirichlet_bc_odd_constraint(), dict)

    def test_n1_is_odd(self):
        r = dirichlet_bc_odd_constraint()
        assert r["n1_is_odd"] is True

    def test_n2_is_odd(self):
        r = dirichlet_bc_odd_constraint()
        assert r["n2_is_odd"] is True

    def test_both_valid(self):
        r = dirichlet_bc_odd_constraint()
        assert r["both_valid"] is True

    def test_odd_modes_correct(self):
        r = dirichlet_bc_odd_constraint()
        for m in r["odd_modes_first_10"]:
            assert m % 2 == 1

    def test_odd_above_nw(self):
        r = dirichlet_bc_odd_constraint()
        for m in r["odd_integers_above_nw"]:
            assert m > N_W
            assert m % 2 == 1

    def test_status_derived(self):
        r = dirichlet_bc_odd_constraint()
        assert "DERIVED" in r["status"]


class TestMinimumStepDerivation:
    def test_returns_dict(self): assert isinstance(minimum_step_derivation(), dict)

    def test_delta_n_equals_2(self):
        r = minimum_step_derivation()
        assert r["delta_n_min"] == 2

    def test_n2_unique_is_7(self):
        r = minimum_step_derivation()
        assert r["n2_unique"] == 7

    def test_k_cs_derived_equals_expected(self):
        r = minimum_step_derivation()
        assert r["k_cs_derived"] == K_CS
        assert r["k_cs_agrees"] is True

    def test_step_1_forbidden(self):
        r = minimum_step_derivation()
        assert r["step_plus_1"]["z2_compatible"] is False

    def test_step_2_allowed(self):
        r = minimum_step_derivation()
        assert r["step_plus_2"]["z2_compatible"] is True

    def test_derivation_chain_complete(self):
        r = minimum_step_derivation()
        assert "n_w=5" in r["derivation_chain"]

    def test_status_derived(self):
        r = minimum_step_derivation()
        assert "DERIVED" in r["status"]


class TestSecondVariationStability:
    def test_returns_dict(self):
        assert isinstance(second_variation_stability(), dict)

    def test_is_stable_default(self):
        r = second_variation_stability()
        assert r["is_stable"] is True

    def test_k_eff_correct(self):
        r = second_variation_stability()
        assert r["k_eff"] == K_CS

    def test_positivity_coefficient_positive(self):
        r = second_variation_stability()
        assert r["positivity_coefficient"] > 0

    def test_verdict_stable(self):
        r = second_variation_stability()
        assert "STABLE" in r["verdict"]

    def test_custom_n1_n2(self):
        r = second_variation_stability(n1=3, n2=5)
        assert r["is_stable"] is True
        assert r["k_eff"] == 3**2 + 5**2

    def test_positivity_scales_with_k_eff(self):
        r1 = second_variation_stability(5, 7)
        r2 = second_variation_stability(5, 9)
        assert r2["positivity_coefficient"] > r1["positivity_coefficient"]


class TestLargerStepDecayRate:
    def test_returns_dict(self):
        assert isinstance(larger_step_decay_rate(9), dict)

    def test_n2_59_metastable(self):
        r = larger_step_decay_rate(9)
        assert r["verdict"] == "METASTABLE"

    def test_n2_511_metastable(self):
        r = larger_step_decay_rate(11)
        assert r["verdict"] == "METASTABLE"

    def test_delta_k_positive(self):
        r = larger_step_decay_rate(9)
        assert r["delta_k"] > 0

    def test_suppression_between_0_and_1(self):
        r = larger_step_decay_rate(9)
        assert 0 < r["rg_suppression_factor"] < 1

    def test_decay_branching_positive(self):
        r = larger_step_decay_rate(9)
        assert 0 < r["decay_branching_ratio"] < 1

    def test_action_ratio_greater_than_1(self):
        r = larger_step_decay_rate(9)
        assert r["action_ratio_larger_over_min"] > 1

    def test_invalid_even_n2(self):
        with pytest.raises(ValueError):
            larger_step_decay_rate(8)

    def test_invalid_small_n2(self):
        with pytest.raises(ValueError):
            larger_step_decay_rate(5)


class TestBraidActionComparison:
    def test_returns_list(self): assert isinstance(braid_action_comparison(), list)

    def test_minimum_step_present(self):
        results = braid_action_comparison()
        min_step = [r for r in results if r["is_minimum_step"]]
        assert len(min_step) == 1
        assert min_step[0]["n2"] == N2

    def test_sorted_by_k_eff(self):
        results = braid_action_comparison()
        k_effs = [r["k_eff"] for r in results]
        assert k_effs == sorted(k_effs)

    def test_all_n2_odd(self):
        results = braid_action_comparison()
        for r in results:
            assert r["n2"] % 2 == 1

    def test_ground_state_has_lowest_k_eff(self):
        results = braid_action_comparison()
        ground = [r for r in results if r["is_minimum_step"]][0]
        assert ground["k_eff"] == min(r["k_eff"] for r in results)


class TestZ2OddBraidPartners:
    def test_all_odd(self):
        partners = z2_odd_braid_partners()
        for n in partners:
            assert n % 2 == 1

    def test_all_above_nw(self):
        partners = z2_odd_braid_partners()
        for n in partners:
            assert n > N_W

    def test_first_partner_is_7(self):
        partners = z2_odd_braid_partners()
        assert partners[0] == 7

    def test_even_n_w_raises(self):
        with pytest.raises(ValueError):
            z2_odd_braid_partners(n_w=4)


class TestP8UpgradeCertificate:
    def test_returns_dict(self): assert isinstance(p8_upgrade_certificate(), dict)

    def test_all_conditions_satisfied(self):
        r = p8_upgrade_certificate()
        assert r["all_conditions_satisfied"] is True

    def test_previous_status(self):
        r = p8_upgrade_certificate()
        assert r["previous_status"] == "POSTULATED"

    def test_new_status(self):
        r = p8_upgrade_certificate()
        assert r["new_status"] == "DERIVED_STRUCTURAL"

    def test_derivation_chain_5_steps(self):
        r = p8_upgrade_certificate()
        assert len(r["derivation_chain"]) >= 5

    def test_certificate_p8_derived(self):
        r = p8_upgrade_certificate()
        assert "P8_DERIVED" in r["certificate_status"]

    def test_upstream_claims_listed(self):
        r = p8_upgrade_certificate()
        assert len(r["upstream_claims_strengthened"]) >= 3

    def test_k_cs_in_chain(self):
        r = p8_upgrade_certificate()
        chain = " ".join(r["derivation_chain"])
        assert "74" in chain or "k_CS" in chain.lower() or "K_CS" in chain


class TestPillar377Summary:
    def test_returns_dict(self): assert isinstance(pillar377_summary(), dict)

    def test_pillar_number(self):
        r = pillar377_summary()
        assert r["pillar_number"] == PILLAR_NUMBER

    def test_status(self):
        r = pillar377_summary()
        assert r["status"] == "DERIVED_STRUCTURAL"

    def test_key_result_present(self):
        r = pillar377_summary()
        assert "key_result" in r
        assert len(r["key_result"]) > 50

    def test_previous_and_new_status(self):
        r = pillar377_summary()
        assert r["previous_status"] == "POSTULATED"
        assert r["new_status"] == "DERIVED_STRUCTURAL"

    def test_falsification_present(self):
        r = pillar377_summary()
        assert "falsification" in r
