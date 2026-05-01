# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_completeness_theorem.py
===================================
Test suite for Pillar 74: The k_CS=74 Topological Completeness Theorem
(src/core/completeness_theorem.py).

~140 tests covering:
  - Constants
  - SOS resonance [C1]
  - CS gap saturation [C2]
  - Birefringence condition [C3]
  - Sound speed fraction [C4]
  - Moduli survival [C5]
  - Pillar count resonance [C6]
  - Back-reaction eigenvalue [C7]
  - Seven closure conditions list
  - Pillar count resonance function
  - Structural completeness theorem
  - Over-fitting boundary proof
  - Closure summary
  - Repository closure statement

"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.completeness_theorem import (
    BACK_REACTION_EIGENVALUE,
    BETA_DEGREES,
    C_S,
    CONDITION_LABELS,
    K_CS,
    N_CLOSURE_CONDITIONS,
    N_PILLARS,
    N_S_PLANCK,
    N_SURVIVING_DOF,
    N_W1,
    N_W2,
    R_BICEP,
    closure_summary,
    kcs_backreaction_eigenvalue,
    kcs_birefringence_condition,
    kcs_cs_gap_saturation,
    kcs_moduli_survival,
    kcs_pillar_count_resonance,
    kcs_seven_closure_conditions,
    kcs_sos_resonance,
    kcs_sound_speed_fraction,
    over_fitting_boundary_proof,
    pillar_count_resonance,
    repository_closure_statement,
    structural_completeness_theorem,
)


# ===========================================================================
# TestConstants
# ===========================================================================

class TestConstants:
    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_n_pillars_is_74(self):
        assert N_PILLARS == 74

    def test_n_closure_conditions_is_7(self):
        assert N_CLOSURE_CONDITIONS == 7

    def test_n_w1_is_5(self):
        assert N_W1 == 5

    def test_n_w2_is_7(self):
        assert N_W2 == 7

    def test_c_s_is_12_over_37(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-12

    def test_beta_degrees_is_0351(self):
        assert abs(BETA_DEGREES - 0.351) < 1e-10

    def test_n_s_planck(self):
        assert abs(N_S_PLANCK - 0.9649) < 1e-10

    def test_r_bicep(self):
        assert abs(R_BICEP - 0.0315) < 1e-10

    def test_n_surviving_dof_is_7(self):
        assert N_SURVIVING_DOF == 7

    def test_back_reaction_eigenvalue_is_1(self):
        assert abs(BACK_REACTION_EIGENVALUE - 1.0) < 1e-12

    def test_condition_labels_length_7(self):
        assert len(CONDITION_LABELS) == 7

    def test_condition_labels_is_tuple(self):
        assert isinstance(CONDITION_LABELS, tuple)

    def test_k_cs_equals_n_w1_sq_plus_n_w2_sq(self):
        assert K_CS == N_W1 ** 2 + N_W2 ** 2

    def test_k_cs_equals_n_pillars(self):
        assert K_CS == N_PILLARS

    def test_n_w1_sq_plus_n_w2_sq(self):
        assert N_W1 ** 2 + N_W2 ** 2 == 74

    def test_c_s_denominator_is_kcs(self):
        # 12/37 = 24/74; denominator 74 = K_CS
        assert abs(C_S - 24.0 / 74.0) < 1e-12

    def test_condition_labels_all_strings(self):
        assert all(isinstance(s, str) for s in CONDITION_LABELS)

    def test_n_w2_equals_n_surviving_dof(self):
        assert N_W2 == N_SURVIVING_DOF

    def test_back_reaction_eigenvalue_float(self):
        assert isinstance(BACK_REACTION_EIGENVALUE, float)


# ===========================================================================
# TestSosResonance
# ===========================================================================

class TestSosResonance:
    def test_returns_dict(self):
        assert isinstance(kcs_sos_resonance(), dict)

    def test_k_cs_value_is_74(self):
        assert kcs_sos_resonance()["k_cs_value"] == 74

    def test_k_cs_is_74(self):
        assert kcs_sos_resonance()["k_cs"] == 74

    def test_status_is_proved(self):
        assert kcs_sos_resonance()["status"] == "PROVED"

    def test_n1_is_5(self):
        assert kcs_sos_resonance()["n1"] == 5

    def test_n2_is_7(self):
        assert kcs_sos_resonance()["n2"] == 7

    def test_value_is_74(self):
        result = kcs_sos_resonance()
        assert result["value"] == 74

    def test_5_squared_plus_7_squared_is_74(self):
        result = kcs_sos_resonance()
        assert result["n1"] ** 2 + result["n2"] ** 2 == 74

    def test_formula_is_str(self):
        assert isinstance(kcs_sos_resonance()["formula"], str)

    def test_keys_present(self):
        result = kcs_sos_resonance()
        for key in ("n1", "n2", "k_cs", "formula", "status", "value", "k_cs_value"):
            assert key in result

    def test_k_cs_consistency(self):
        result = kcs_sos_resonance()
        assert result["k_cs"] == result["value"] == result["k_cs_value"]

    def test_formula_contains_74(self):
        result = kcs_sos_resonance()
        assert "74" in result["formula"]

    def test_formula_contains_5(self):
        result = kcs_sos_resonance()
        assert "5" in result["formula"]

    def test_formula_contains_7(self):
        result = kcs_sos_resonance()
        assert "7" in result["formula"]

    def test_value_positive(self):
        result = kcs_sos_resonance()
        assert result["value"] > 0

    def test_algebraic_identity_verified(self):
        result = kcs_sos_resonance()
        assert result["n1"] ** 2 + result["n2"] ** 2 == K_CS


# ===========================================================================
# TestCsGapSaturation
# ===========================================================================

class TestCsGapSaturation:
    def test_returns_dict(self):
        assert isinstance(kcs_cs_gap_saturation(), dict)

    def test_n_w_is_5(self):
        assert kcs_cs_gap_saturation()["n_w"] == 5

    def test_k_eff_is_74(self):
        assert kcs_cs_gap_saturation()["k_eff"] == 74

    def test_k_cs_value_is_74(self):
        assert kcs_cs_gap_saturation()["k_cs_value"] == 74

    def test_n_gen_is_3(self):
        assert kcs_cs_gap_saturation()["n_gen"] == 3

    def test_status_contains_proved(self):
        status = kcs_cs_gap_saturation()["status"]
        assert "PROVED" in status

    def test_stability_condition_is_str(self):
        assert isinstance(kcs_cs_gap_saturation()["stability_condition"], str)

    def test_k_eff_formula_verified(self):
        result = kcs_cs_gap_saturation()
        n_w = result["n_w"]
        assert n_w ** 2 + (n_w + 2) ** 2 == 74

    def test_keys_present(self):
        result = kcs_cs_gap_saturation()
        for key in ("n_w", "k_eff", "k_cs_value", "n_gen", "stability_condition",
                    "status", "formula"):
            assert key in result

    def test_formula_is_str(self):
        assert isinstance(kcs_cs_gap_saturation()["formula"], str)

    def test_k_eff_equals_k_cs(self):
        result = kcs_cs_gap_saturation()
        assert result["k_eff"] == K_CS

    def test_preferred_in_status(self):
        status = kcs_cs_gap_saturation()["status"]
        assert "PREFERRED" in status

    def test_n_gen_positive(self):
        assert kcs_cs_gap_saturation()["n_gen"] > 0

    def test_n_w_odd(self):
        assert kcs_cs_gap_saturation()["n_w"] % 2 == 1

    def test_k_cs_value_equals_k_eff(self):
        result = kcs_cs_gap_saturation()
        assert result["k_cs_value"] == result["k_eff"]


# ===========================================================================
# TestBirefringenceCondition
# ===========================================================================

class TestBirefringenceCondition:
    def test_returns_dict(self):
        assert isinstance(kcs_birefringence_condition(), dict)

    def test_k_cs_is_74(self):
        assert kcs_birefringence_condition()["k_cs"] == 74

    def test_k_cs_value_is_74(self):
        assert kcs_birefringence_condition()["k_cs_value"] == 74

    def test_beta_degrees_is_0351(self):
        result = kcs_birefringence_condition()
        assert abs(result["beta_degrees"] - 0.351) < 1e-10

    def test_status_is_cross_checked(self):
        result = kcs_birefringence_condition()
        assert result["status"] == "CROSS-CHECKED"

    def test_within_1sigma_is_bool(self):
        result = kcs_birefringence_condition()
        assert isinstance(result["within_1sigma"], bool)

    def test_minami_komatsu_value_present(self):
        result = kcs_birefringence_condition()
        assert "minami_komatsu_value" in result

    def test_within_1sigma_true_for_0351(self):
        result = kcs_birefringence_condition()
        # 0.351 is within 0.14° of 0.35
        assert result["within_1sigma"] is True

    def test_keys_present(self):
        result = kcs_birefringence_condition()
        for key in ("k_cs", "k_cs_value", "beta_degrees", "status",
                    "minami_komatsu_value", "within_1sigma", "formula"):
            assert key in result

    def test_formula_is_str(self):
        assert isinstance(kcs_birefringence_condition()["formula"], str)

    def test_beta_degrees_positive(self):
        assert kcs_birefringence_condition()["beta_degrees"] > 0.0

    def test_formula_contains_74(self):
        result = kcs_birefringence_condition()
        assert "74" in result["formula"]

    def test_minami_komatsu_value_near_0_35(self):
        result = kcs_birefringence_condition()
        assert abs(result["minami_komatsu_value"] - 0.35) < 0.01

    def test_k_cs_matches_module_constant(self):
        result = kcs_birefringence_condition()
        assert result["k_cs"] == K_CS

    def test_beta_matches_module_constant(self):
        result = kcs_birefringence_condition()
        assert abs(result["beta_degrees"] - BETA_DEGREES) < 1e-10

    def test_sigma_positive(self):
        result = kcs_birefringence_condition()
        if "minami_komatsu_sigma" in result:
            assert result["minami_komatsu_sigma"] > 0.0


# ===========================================================================
# TestSoundSpeedFraction
# ===========================================================================

class TestSoundSpeedFraction:
    def test_returns_dict(self):
        assert isinstance(kcs_sound_speed_fraction(), dict)

    def test_c_s_is_12_over_37(self):
        result = kcs_sound_speed_fraction()
        assert abs(result["c_s"] - 12.0 / 37.0) < 1e-12

    def test_denominator_is_74(self):
        result = kcs_sound_speed_fraction()
        assert result["denominator"] == 74

    def test_k_cs_value_is_74(self):
        result = kcs_sound_speed_fraction()
        assert result["k_cs_value"] == 74

    def test_numerator_is_24(self):
        result = kcs_sound_speed_fraction()
        assert result["numerator"] == 24

    def test_status_is_derived(self):
        result = kcs_sound_speed_fraction()
        assert result["status"] == "DERIVED"

    def test_keys_present(self):
        result = kcs_sound_speed_fraction()
        for key in ("c_s", "numerator", "denominator", "k_cs",
                    "k_cs_value", "status", "formula"):
            assert key in result

    def test_denominator_equals_k_cs(self):
        result = kcs_sound_speed_fraction()
        assert result["denominator"] == K_CS

    def test_c_s_positive(self):
        result = kcs_sound_speed_fraction()
        assert result["c_s"] > 0.0

    def test_c_s_less_than_1(self):
        result = kcs_sound_speed_fraction()
        assert result["c_s"] < 1.0

    def test_formula_is_str(self):
        assert isinstance(kcs_sound_speed_fraction()["formula"], str)

    def test_formula_contains_74(self):
        result = kcs_sound_speed_fraction()
        assert "74" in result["formula"]

    def test_numerator_formula(self):
        result = kcs_sound_speed_fraction()
        assert result["numerator"] == N_W2 ** 2 - N_W1 ** 2

    def test_c_s_matches_module_constant(self):
        result = kcs_sound_speed_fraction()
        assert abs(result["c_s"] - C_S) < 1e-12

    def test_k_cs_equals_denominator(self):
        result = kcs_sound_speed_fraction()
        assert result["k_cs"] == result["denominator"]


# ===========================================================================
# TestModuliSurvival
# ===========================================================================

class TestModuliSurvival:
    def test_returns_dict(self):
        assert isinstance(kcs_moduli_survival(), dict)

    def test_n_surviving_dof_is_7(self):
        assert kcs_moduli_survival()["n_surviving_dof"] == 7

    def test_k_cs_is_74(self):
        assert kcs_moduli_survival()["k_cs"] == 74

    def test_k_cs_value_is_74(self):
        assert kcs_moduli_survival()["k_cs_value"] == 74

    def test_n_w2_is_7(self):
        assert kcs_moduli_survival()["n_w2"] == 7

    def test_status_is_proved(self):
        assert kcs_moduli_survival()["status"] == "PROVED"

    def test_keys_present(self):
        result = kcs_moduli_survival()
        for key in ("n_surviving_dof", "k_cs", "k_cs_value", "n_w2",
                    "connection", "status", "formula"):
            assert key in result

    def test_connection_is_str(self):
        assert isinstance(kcs_moduli_survival()["connection"], str)

    def test_n_surviving_dof_equals_n_w2(self):
        result = kcs_moduli_survival()
        assert result["n_surviving_dof"] == result["n_w2"]

    def test_k_cs_value_consistent(self):
        result = kcs_moduli_survival()
        assert result["k_cs"] == result["k_cs_value"] == K_CS


# ===========================================================================
# TestPillarCountResonance
# ===========================================================================

class TestPillarCountResonance:
    def test_returns_dict(self):
        assert isinstance(kcs_pillar_count_resonance(), dict)

    def test_n_pillars_is_74(self):
        assert kcs_pillar_count_resonance()["n_pillars"] == 74

    def test_k_cs_is_74(self):
        assert kcs_pillar_count_resonance()["k_cs"] == 74

    def test_k_cs_value_is_74(self):
        assert kcs_pillar_count_resonance()["k_cs_value"] == 74

    def test_matches_is_true(self):
        assert kcs_pillar_count_resonance()["matches"] is True

    def test_status_is_structural(self):
        assert kcs_pillar_count_resonance()["status"] == "STRUCTURAL"

    def test_keys_present(self):
        result = kcs_pillar_count_resonance()
        for key in ("n_pillars", "k_cs", "k_cs_value", "matches", "status",
                    "formula", "interpretation"):
            assert key in result

    def test_formula_is_str(self):
        assert isinstance(kcs_pillar_count_resonance()["formula"], str)

    def test_interpretation_is_str(self):
        assert isinstance(kcs_pillar_count_resonance()["interpretation"], str)

    def test_matches_is_bool(self):
        assert isinstance(kcs_pillar_count_resonance()["matches"], bool)


# ===========================================================================
# TestBackreactionEigenvalue
# ===========================================================================

class TestBackreactionEigenvalue:
    def test_returns_dict(self):
        assert isinstance(kcs_backreaction_eigenvalue(), dict)

    def test_eigenvalue_is_1(self):
        assert abs(kcs_backreaction_eigenvalue()["eigenvalue"] - 1.0) < 1e-12

    def test_k_cs_value_is_74(self):
        assert kcs_backreaction_eigenvalue()["k_cs_value"] == 74

    def test_k_cs_numerator_is_74(self):
        assert kcs_backreaction_eigenvalue()["k_cs_numerator"] == 74

    def test_k_cs_denominator_is_74(self):
        assert kcs_backreaction_eigenvalue()["k_cs_denominator"] == 74

    def test_status_is_derived(self):
        assert kcs_backreaction_eigenvalue()["status"] == "DERIVED"

    def test_keys_present(self):
        result = kcs_backreaction_eigenvalue()
        for key in ("eigenvalue", "k_cs_value", "k_cs_numerator",
                    "k_cs_denominator", "interpretation", "status", "formula"):
            assert key in result

    def test_interpretation_is_str(self):
        assert isinstance(kcs_backreaction_eigenvalue()["interpretation"], str)

    def test_eigenvalue_equals_ratio(self):
        result = kcs_backreaction_eigenvalue()
        ratio = result["k_cs_numerator"] / result["k_cs_denominator"]
        assert abs(result["eigenvalue"] - ratio) < 1e-12

    def test_formula_is_str(self):
        assert isinstance(kcs_backreaction_eigenvalue()["formula"], str)


# ===========================================================================
# TestKcsSevenClosureConditions
# ===========================================================================

class TestKcsSevenClosureConditions:
    def test_returns_list(self):
        assert isinstance(kcs_seven_closure_conditions(), list)

    def test_length_is_7(self):
        assert len(kcs_seven_closure_conditions()) == 7

    def test_all_k_cs_value_74(self):
        for cond in kcs_seven_closure_conditions():
            assert cond["k_cs_value"] == 74

    def test_all_have_label(self):
        for cond in kcs_seven_closure_conditions():
            assert "label" in cond

    def test_all_have_status(self):
        for cond in kcs_seven_closure_conditions():
            assert "status" in cond

    def test_all_have_formula(self):
        for cond in kcs_seven_closure_conditions():
            assert "formula" in cond

    def test_all_labels_strings(self):
        for cond in kcs_seven_closure_conditions():
            assert isinstance(cond["label"], str)

    def test_all_status_strings(self):
        for cond in kcs_seven_closure_conditions():
            assert isinstance(cond["status"], str)

    def test_all_formula_strings(self):
        for cond in kcs_seven_closure_conditions():
            assert isinstance(cond["formula"], str)

    def test_labels_from_condition_labels(self):
        conditions = kcs_seven_closure_conditions()
        for i, cond in enumerate(conditions):
            assert cond["label"] == CONDITION_LABELS[i]

    def test_c1_proved(self):
        conditions = kcs_seven_closure_conditions()
        assert "PROVED" in conditions[0]["status"]

    def test_c7_derived(self):
        conditions = kcs_seven_closure_conditions()
        assert "DERIVED" in conditions[6]["status"]

    def test_each_has_detail(self):
        for cond in kcs_seven_closure_conditions():
            assert "detail" in cond

    def test_no_k_cs_value_different_from_74(self):
        for cond in kcs_seven_closure_conditions():
            assert cond["k_cs_value"] == K_CS

    def test_c6_structural(self):
        conditions = kcs_seven_closure_conditions()
        assert "STRUCTURAL" in conditions[5]["status"]

    def test_all_k_cs_value_ints(self):
        for cond in kcs_seven_closure_conditions():
            assert isinstance(cond["k_cs_value"], int)


# ===========================================================================
# TestPillarCountResonanceFunc
# ===========================================================================

class TestPillarCountResonanceFunc:
    def test_74_resonates(self):
        result = pillar_count_resonance(74)
        assert result["resonates"] is True

    def test_73_does_not_resonate(self):
        result = pillar_count_resonance(73)
        assert result["resonates"] is False

    def test_75_does_not_resonate(self):
        result = pillar_count_resonance(75)
        assert result["resonates"] is False

    def test_returns_dict(self):
        assert isinstance(pillar_count_resonance(74), dict)

    def test_n_pillars_stored(self):
        result = pillar_count_resonance(74)
        assert result["n_pillars"] == 74

    def test_k_cs_stored(self):
        result = pillar_count_resonance(74)
        assert result["k_cs"] == K_CS

    def test_keys_present(self):
        result = pillar_count_resonance(74)
        for key in ("n_pillars", "k_cs", "resonates", "interpretation", "message"):
            assert key in result

    def test_message_is_str(self):
        assert isinstance(pillar_count_resonance(74)["message"], str)

    def test_interpretation_is_str(self):
        assert isinstance(pillar_count_resonance(74)["interpretation"], str)

    def test_1_does_not_resonate(self):
        assert pillar_count_resonance(1)["resonates"] is False


# ===========================================================================
# TestStructuralCompletenessTheorem
# ===========================================================================

class TestStructuralCompletenessTheorem:
    def test_returns_dict(self):
        assert isinstance(structural_completeness_theorem(), dict)

    def test_keys_present(self):
        result = structural_completeness_theorem()
        for key in ("theorem", "k_cs", "n_closure_conditions", "conditions",
                    "all_conditions_yield_74", "overall_verdict",
                    "honest_status_summary", "weakest_link",
                    "falsification_statement"):
            assert key in result

    def test_conditions_length_7(self):
        result = structural_completeness_theorem()
        assert len(result["conditions"]) == 7

    def test_overall_verdict_is_str(self):
        result = structural_completeness_theorem()
        assert isinstance(result["overall_verdict"], str)

    def test_all_conditions_yield_74_true(self):
        result = structural_completeness_theorem()
        assert result["all_conditions_yield_74"] is True

    def test_weakest_link_is_str(self):
        result = structural_completeness_theorem()
        assert isinstance(result["weakest_link"], str)

    def test_weakest_link_mentions_c2(self):
        result = structural_completeness_theorem()
        assert "C2" in result["weakest_link"] or "APS" in result["weakest_link"]

    def test_falsification_statement_is_str(self):
        result = structural_completeness_theorem()
        assert isinstance(result["falsification_statement"], str)

    def test_k_cs_is_74(self):
        result = structural_completeness_theorem()
        assert result["k_cs"] == 74

    def test_honest_status_dict(self):
        result = structural_completeness_theorem()
        assert isinstance(result["honest_status_summary"], dict)


# ===========================================================================
# TestOverFittingBoundaryProof
# ===========================================================================

class TestOverFittingBoundaryProof:
    def test_returns_dict(self):
        assert isinstance(over_fitting_boundary_proof(), dict)

    def test_n_pillars_complete_is_74(self):
        assert over_fitting_boundary_proof()["n_pillars_complete"] == 74

    def test_n_pillars_overfit_is_75(self):
        assert over_fitting_boundary_proof()["n_pillars_overfit"] == 75

    def test_new_parameter_needed_is_str(self):
        result = over_fitting_boundary_proof()
        assert isinstance(result["new_parameter_needed"], str)

    def test_reason_is_str(self):
        result = over_fitting_boundary_proof()
        assert isinstance(result["reason"], str)

    def test_conclusion_is_str(self):
        result = over_fitting_boundary_proof()
        assert isinstance(result["conclusion"], str)

    def test_keys_present(self):
        result = over_fitting_boundary_proof()
        for key in ("n_pillars_complete", "n_pillars_overfit",
                    "new_parameter_needed", "reason", "conclusion", "k_cs"):
            assert key in result

    def test_k_cs_is_74(self):
        assert over_fitting_boundary_proof()["k_cs"] == 74

    def test_new_param_nonempty(self):
        result = over_fitting_boundary_proof()
        assert len(result["new_parameter_needed"]) > 0

    def test_n_pillars_overfit_equals_complete_plus_1(self):
        result = over_fitting_boundary_proof()
        assert result["n_pillars_overfit"] == result["n_pillars_complete"] + 1

    def test_reason_nonempty(self):
        result = over_fitting_boundary_proof()
        assert len(result["reason"]) > 0


# ===========================================================================
# TestClosureSummary
# ===========================================================================

class TestClosureSummary:
    def test_returns_dict(self):
        assert isinstance(closure_summary(), dict)

    def test_k_cs_is_74(self):
        assert closure_summary()["k_cs"] == 74

    def test_n_pillars_is_74(self):
        assert closure_summary()["n_pillars"] == 74

    def test_status_is_complete(self):
        assert closure_summary()["status"] == "COMPLETE"

    def test_falsifier_is_str(self):
        assert isinstance(closure_summary()["falsifier"], str)

    def test_keys_present(self):
        result = closure_summary()
        for key in ("framework", "n_pillars", "k_cs", "braid_pair",
                    "n_closure_conditions", "status", "falsifier"):
            assert key in result


# ===========================================================================
# TestRepositoryClosureStatement
# ===========================================================================

class TestRepositoryClosureStatement:
    def test_returns_str(self):
        assert isinstance(repository_closure_statement(), str)

    def test_contains_walker_pearson(self):
        assert "Walker-Pearson" in repository_closure_statement()

    def test_contains_74(self):
        assert "74" in repository_closure_statement()

    def test_contains_litebird_or_falsif(self):
        stmt = repository_closure_statement()
        assert "LiteBIRD" in stmt or "falsif" in stmt.lower()

    def test_nonempty(self):
        assert len(repository_closure_statement()) > 0
