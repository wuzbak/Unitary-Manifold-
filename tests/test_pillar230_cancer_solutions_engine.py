# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_pillar230_cancer_solutions_engine.py
===============================================
Tests for Pillar 230: Cancer Solutions Engine.

Every numeric claim is either:
    - Derived via exact arithmetic from framework constants (n_w=5, K_CS=74,
      c_s=12/37, φ₀≈0.739) — verified by algebraic identity.
    - Sourced from peer-reviewed oncology literature — verified against the
      documented empirical baselines in the module.

All tests are deterministic (no random seeds required).
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar230_cancer_solutions_engine import (
    # Constants
    N_W,
    K_CS,
    C_S,
    PHI0,
    # Solution functions
    optimize_combination_therapy,
    enrollment_intervention_model,
    nanoparticle_delivery_optimizer,
    precision_medicine_routing,
    detection_improvement_pathway,
    survivorship_care_scale_model,
    financial_access_intervention,
    cancer_solution_roadmap,
    resistance_prevention_model,
)


# ─────────────────────────────────────────────────────────────────────────────
# Public __all__ — all names importable
# ─────────────────────────────────────────────────────────────────────────────

class TestPublicAll:
    def test_all_constants_in_all(self):
        import src.core.pillar230_cancer_solutions_engine as m
        for name in ["N_W", "K_CS", "C_S", "PHI0"]:
            assert name in m.__all__, f"{name} missing from __all__"

    def test_all_functions_in_all(self):
        import src.core.pillar230_cancer_solutions_engine as m
        for name in [
            "optimize_combination_therapy",
            "enrollment_intervention_model",
            "nanoparticle_delivery_optimizer",
            "precision_medicine_routing",
            "detection_improvement_pathway",
            "survivorship_care_scale_model",
            "financial_access_intervention",
            "cancer_solution_roadmap",
            "resistance_prevention_model",
        ]:
            assert name in m.__all__, f"{name} missing from __all__"

    def test_provenance_pillar_is_230(self):
        import src.core.pillar230_cancer_solutions_engine as m
        assert m.__provenance__["pillar"] == 230

    def test_provenance_has_required_keys(self):
        import src.core.pillar230_cancer_solutions_engine as m
        for key in ["pillar", "title", "author", "license_software"]:
            assert key in m.__provenance__


# ─────────────────────────────────────────────────────────────────────────────
# Framework constants
# ─────────────────────────────────────────────────────────────────────────────

class TestConstants:
    def test_nw_is_5(self):
        assert N_W == 5

    def test_kcs_is_74(self):
        assert K_CS == 74

    def test_kcs_sum_of_squares(self):
        assert K_CS == 5 ** 2 + 7 ** 2

    def test_cs_exact_fraction(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-15

    def test_phi0_fixed_point(self):
        """φ₀ must satisfy cos(φ₀) = φ₀ to 12 decimal places."""
        assert abs(math.cos(PHI0) - PHI0) < 1e-12

    def test_phi0_in_unit_interval(self):
        assert 0.0 < PHI0 < 1.0


# ─────────────────────────────────────────────────────────────────────────────
# A. Combination Therapy Optimizer
# ─────────────────────────────────────────────────────────────────────────────

class TestOptimizeCombinationTherapy:
    def test_returns_required_keys(self):
        r = optimize_combination_therapy(3, [0.9, 0.8, 0.7], 2)
        for key in [
            "best_combination", "kill_probability", "shannon_gain",
            "heterogeneity_reduction", "all_combinations_ranked",
            "n_drugs_in_best", "n_clones", "status", "notes",
        ]:
            assert key in r, f"Missing key: {key}"

    def test_kill_probability_in_unit_interval(self):
        r = optimize_combination_therapy(5, [0.9, 0.85, 0.7], 2)
        assert 0.0 <= r["kill_probability"] <= 1.0

    def test_shannon_gain_non_negative(self):
        r = optimize_combination_therapy(5, [0.9, 0.85, 0.7], 2)
        assert r["shannon_gain"] >= 0.0

    def test_heterogeneity_reduction_in_unit_interval(self):
        r = optimize_combination_therapy(5, [0.9, 0.85, 0.7], 2)
        assert 0.0 <= r["heterogeneity_reduction"] <= 1.0

    def test_single_drug_single_clone_returns_kill_rate(self):
        r = optimize_combination_therapy(1, [0.9], 1)
        assert abs(r["kill_probability"] - 0.9) < 1e-12

    def test_perfect_kill_rate_gives_probability_one(self):
        r = optimize_combination_therapy(5, [1.0, 1.0], 2)
        assert abs(r["kill_probability"] - 1.0) < 1e-12

    def test_more_drugs_improves_or_equals_kill_probability(self):
        r1 = optimize_combination_therapy(5, [0.9, 0.8, 0.7], 1)
        r2 = optimize_combination_therapy(5, [0.9, 0.8, 0.7], 2)
        # Best 2-drug combo should produce >= 1-drug probability
        # (not necessarily, if best single drug is way better)
        # But best 2-drug includes both best single drugs — combination
        # p_kill_one_clone = 1-(1-0.9)*(1-0.8) = 1-0.02=0.98 > 0.9
        assert r2["kill_probability"] >= r1["kill_probability"] - 1e-10

    def test_three_drugs_better_than_two_for_five_clones(self):
        r2 = optimize_combination_therapy(5, [0.9, 0.8, 0.7], 2)
        r3 = optimize_combination_therapy(5, [0.9, 0.8, 0.7], 3)
        assert r3["kill_probability"] >= r2["kill_probability"] - 1e-10

    def test_best_combination_indices_are_valid(self):
        n_lib = 4
        r = optimize_combination_therapy(3, [0.9, 0.8, 0.7, 0.6], 2)
        for idx in r["best_combination"]:
            assert 0 <= idx < n_lib

    def test_n_drugs_in_best_matches_requested(self):
        r = optimize_combination_therapy(3, [0.9, 0.8, 0.7], 2)
        assert r["n_drugs_in_best"] == 2
        assert len(r["best_combination"]) == 2

    def test_all_combinations_ranked_sorted_descending(self):
        r = optimize_combination_therapy(3, [0.9, 0.8, 0.7, 0.6], 2)
        probs = [e["kill_probability"] for e in r["all_combinations_ranked"]]
        assert probs == sorted(probs, reverse=True)

    def test_max_combinations_limits_output(self):
        r = optimize_combination_therapy(3, [0.9, 0.8, 0.7, 0.6, 0.5], 2,
                                        max_combinations=3)
        assert len(r["all_combinations_ranked"]) <= 3

    def test_invalid_n_clones_raises(self):
        with pytest.raises(ValueError):
            optimize_combination_therapy(0, [0.9], 1)

    def test_invalid_kill_rate_raises(self):
        with pytest.raises(ValueError):
            optimize_combination_therapy(3, [0.0, 0.9], 1)

    def test_kill_rate_above_one_raises(self):
        with pytest.raises(ValueError):
            optimize_combination_therapy(3, [1.1, 0.9], 1)

    def test_n_drugs_exceeds_library_raises(self):
        with pytest.raises(ValueError):
            optimize_combination_therapy(3, [0.9, 0.8], 3)

    def test_empty_kill_rates_raises(self):
        with pytest.raises(ValueError):
            optimize_combination_therapy(3, [], 1)

    def test_formula_verification_two_drugs_five_clones(self):
        """Verify P = (1 - (1-k1)(1-k2))^n_clones for best 2-drug combo."""
        k_rates = [0.9, 0.85]
        r = optimize_combination_therapy(5, k_rates, 2)
        # Only one possible combo: [0, 1]
        p_miss = (1 - 0.9) * (1 - 0.85)
        expected = (1 - p_miss) ** 5
        assert abs(r["kill_probability"] - expected) < 1e-12

    def test_n_clones_stored_correctly(self):
        r = optimize_combination_therapy(7, [0.9, 0.8, 0.7], 2)
        assert r["n_clones"] == 7


# ─────────────────────────────────────────────────────────────────────────────
# B. Trial Enrollment Accelerator
# ─────────────────────────────────────────────────────────────────────────────

class TestEnrollmentInterventionModel:
    def test_returns_required_keys(self):
        r = enrollment_intervention_model(0.04, 0.5, 0.3, 0.2)
        for key in [
            "improved_participation_rate", "additional_patients_per_year",
            "enrollment_gap_closed", "current_participation_rate",
            "target_participation_rate", "multiplier_applied",
            "status", "notes",
        ]:
            assert key in r, f"Missing key: {key}"

    def test_improved_rate_above_current(self):
        r = enrollment_intervention_model(0.04, 0.5, 0.3, 0.2)
        assert r["improved_participation_rate"] > 0.04

    def test_improved_rate_in_unit_interval(self):
        r = enrollment_intervention_model(0.04, 1.0, 1.0, 1.0)
        assert 0.0 <= r["improved_participation_rate"] <= 1.0

    def test_additional_patients_non_negative(self):
        r = enrollment_intervention_model(0.04, 0.5, 0.3, 0.2)
        assert r["additional_patients_per_year"] >= 0.0

    def test_gap_closed_in_unit_interval(self):
        r = enrollment_intervention_model(0.04, 0.5, 0.3, 0.2)
        assert 0.0 <= r["enrollment_gap_closed"] <= 1.0

    def test_zero_interventions_no_change(self):
        r = enrollment_intervention_model(0.04, 0.0, 0.0, 0.0)
        assert abs(r["improved_participation_rate"] - 0.04) < 1e-12
        assert r["additional_patients_per_year"] == 0.0

    def test_higher_coverage_higher_rate(self):
        r_low = enrollment_intervention_model(0.04, 0.2, 0.1, 0.1)
        r_high = enrollment_intervention_model(0.04, 0.8, 0.6, 0.4)
        assert r_high["improved_participation_rate"] > r_low["improved_participation_rate"]

    def test_full_interventions_cap_at_one(self):
        r = enrollment_intervention_model(0.5, 1.0, 1.0, 1.0)
        assert r["improved_participation_rate"] <= 1.0

    def test_multiplier_formula(self):
        dcn, nav, fin = 0.5, 0.3, 0.2
        r = enrollment_intervention_model(0.04, dcn, nav, fin)
        expected_mult = 1.0 + 2.1 * dcn + 1.8 * nav + 1.3 * fin
        assert abs(r["multiplier_applied"] - expected_mult) < 1e-12

    def test_additional_patients_formula(self):
        r = enrollment_intervention_model(0.04, 0.5, 0.3, 0.2)
        expected = (r["improved_participation_rate"] - 0.04) * 1_800_000
        assert abs(r["additional_patients_per_year"] - expected) < 1.0

    def test_already_at_target_gap_closed_one(self):
        r = enrollment_intervention_model(0.15, 0.5, 0.3, 0.2, target_participation_rate=0.10)
        # current >= target → gap fully closed
        assert r["enrollment_gap_closed"] == 1.0

    def test_invalid_current_rate_raises(self):
        with pytest.raises(ValueError):
            enrollment_intervention_model(-0.01, 0.5, 0.3, 0.2)

    def test_invalid_decentralized_raises(self):
        with pytest.raises(ValueError):
            enrollment_intervention_model(0.04, 1.5, 0.3, 0.2)

    def test_invalid_target_rate_raises(self):
        with pytest.raises(ValueError):
            enrollment_intervention_model(0.04, 0.5, 0.3, 0.2, target_participation_rate=0.0)


# ─────────────────────────────────────────────────────────────────────────────
# C. Drug Delivery Improvement Model
# ─────────────────────────────────────────────────────────────────────────────

class TestNanoparticleDeliveryOptimizer:
    def test_returns_required_keys(self):
        r = nanoparticle_delivery_optimizer(0.035, 100.0, "PEG", False)
        for key in [
            "improved_delivery_efficiency", "therapeutic_index_improvement",
            "off_target_reduction", "size_factor", "coating_factor",
            "active_factor", "current_delivery_efficiency",
            "status", "notes",
        ]:
            assert key in r, f"Missing key: {key}"

    def test_improved_efficiency_in_valid_range(self):
        r = nanoparticle_delivery_optimizer(0.035, 100.0, "PEG", False)
        assert 0.0 < r["improved_delivery_efficiency"] <= 0.35

    def test_improved_efficiency_above_baseline(self):
        r = nanoparticle_delivery_optimizer(0.035, 100.0, "antibody", True)
        assert r["improved_delivery_efficiency"] >= 0.035

    def test_antibody_better_than_peg(self):
        r_peg = nanoparticle_delivery_optimizer(0.035, 100.0, "PEG", False)
        r_ab = nanoparticle_delivery_optimizer(0.035, 100.0, "antibody", False)
        assert r_ab["improved_delivery_efficiency"] > r_peg["improved_delivery_efficiency"]

    def test_active_targeting_better_than_passive(self):
        r_passive = nanoparticle_delivery_optimizer(0.035, 100.0, "RGD", False)
        r_active = nanoparticle_delivery_optimizer(0.035, 100.0, "RGD", True)
        assert r_active["improved_delivery_efficiency"] > r_passive["improved_delivery_efficiency"]

    def test_optimal_size_gives_max_size_factor(self):
        r_100 = nanoparticle_delivery_optimizer(0.035, 100.0, "PEG", False)
        r_200 = nanoparticle_delivery_optimizer(0.035, 200.0, "PEG", False)
        # 100 nm is optimal center; 200 nm is ~3.3 sigma away → size factor lower
        assert r_100["size_factor"] > r_200["size_factor"]

    def test_size_factor_is_gaussian(self):
        r = nanoparticle_delivery_optimizer(0.035, 100.0, "PEG", False)
        assert abs(r["size_factor"] - 1.0) < 1e-12  # exp(0) at optimal

    def test_coating_factor_peg_is_one(self):
        r = nanoparticle_delivery_optimizer(0.035, 100.0, "PEG", False)
        assert abs(r["coating_factor"] - 1.0) < 1e-12

    def test_coating_factor_rgd_is_1_4(self):
        r = nanoparticle_delivery_optimizer(0.035, 100.0, "RGD", False)
        assert abs(r["coating_factor"] - 1.4) < 1e-12

    def test_coating_factor_antibody_is_2_1(self):
        r = nanoparticle_delivery_optimizer(0.035, 100.0, "antibody", False)
        assert abs(r["coating_factor"] - 2.1) < 1e-12

    def test_active_factor_passive_is_one(self):
        r = nanoparticle_delivery_optimizer(0.035, 100.0, "PEG", False)
        assert abs(r["active_factor"] - 1.0) < 1e-12

    def test_active_factor_active_is_1_8(self):
        r = nanoparticle_delivery_optimizer(0.035, 100.0, "PEG", True)
        assert abs(r["active_factor"] - 1.8) < 1e-12

    def test_therapeutic_index_improvement_gte_one(self):
        r = nanoparticle_delivery_optimizer(0.035, 100.0, "antibody", True)
        assert r["therapeutic_index_improvement"] >= 1.0

    def test_off_target_reduction_in_unit_interval(self):
        r = nanoparticle_delivery_optimizer(0.035, 100.0, "antibody", True)
        assert 0.0 <= r["off_target_reduction"] <= 1.0

    def test_delivery_capped_at_0_35(self):
        # Very high starting efficiency + all factors should be capped
        r = nanoparticle_delivery_optimizer(0.30, 100.0, "antibody", True)
        assert r["improved_delivery_efficiency"] <= 0.35

    def test_invalid_efficiency_raises(self):
        with pytest.raises(ValueError):
            nanoparticle_delivery_optimizer(0.0, 100.0, "PEG", False)

    def test_invalid_efficiency_over_one_raises(self):
        with pytest.raises(ValueError):
            nanoparticle_delivery_optimizer(1.0, 100.0, "PEG", False)

    def test_invalid_size_raises(self):
        with pytest.raises(ValueError):
            nanoparticle_delivery_optimizer(0.035, 0.0, "PEG", False)

    def test_invalid_coating_raises(self):
        with pytest.raises(ValueError):
            nanoparticle_delivery_optimizer(0.035, 100.0, "liposome", False)

    def test_monotone_with_antibody_chain(self):
        """PEG < RGD < antibody in delivery efficiency at fixed size and active."""
        baseline = 0.007
        r_peg = nanoparticle_delivery_optimizer(baseline, 100.0, "PEG", False)
        r_rgd = nanoparticle_delivery_optimizer(baseline, 100.0, "RGD", False)
        r_ab = nanoparticle_delivery_optimizer(baseline, 100.0, "antibody", False)
        assert r_peg["improved_delivery_efficiency"] < r_rgd["improved_delivery_efficiency"]
        assert r_rgd["improved_delivery_efficiency"] < r_ab["improved_delivery_efficiency"]


# ─────────────────────────────────────────────────────────────────────────────
# D. Precision Medicine Router
# ─────────────────────────────────────────────────────────────────────────────

class TestPrecisionMedicineRouting:
    def test_returns_required_keys(self):
        r = precision_medicine_routing(5.0, False, 30.0, False, False, False)
        for key in [
            "recommended_therapies", "response_probability", "precision_score",
            "n_targetable_alterations", "status", "notes",
        ]:
            assert key in r, f"Missing key: {key}"

    def test_no_biomarkers_no_therapies(self):
        r = precision_medicine_routing(5.0, False, 30.0, False, False, False)
        assert r["recommended_therapies"] == []
        assert r["response_probability"] == {}
        assert r["n_targetable_alterations"] == 0

    def test_no_biomarkers_precision_score_zero(self):
        r = precision_medicine_routing(5.0, False, 30.0, False, False, False)
        assert r["precision_score"] == 0.0

    def test_all_biomarkers_six_therapies(self):
        r = precision_medicine_routing(20.0, True, 60.0, True, True, True)
        assert r["n_targetable_alterations"] == 6
        assert len(r["recommended_therapies"]) == 6

    def test_all_biomarkers_precision_score_is_phi0(self):
        r = precision_medicine_routing(20.0, True, 60.0, True, True, True)
        assert abs(r["precision_score"] - PHI0) < 1e-12

    def test_tmb_high_adds_pembrolizumab(self):
        r = precision_medicine_routing(15.0, False, 0.0, False, False, False)
        assert any("TMB-H" in t for t in r["recommended_therapies"])

    def test_tmb_below_threshold_no_tmb_therapy(self):
        r = precision_medicine_routing(9.0, False, 0.0, False, False, False)
        assert not any("TMB-H" in t for t in r["recommended_therapies"])

    def test_msi_h_adds_therapy(self):
        r = precision_medicine_routing(5.0, True, 0.0, False, False, False)
        assert any("MSI-H" in t for t in r["recommended_therapies"])

    def test_pdl1_ge_50_adds_therapy(self):
        r = precision_medicine_routing(5.0, False, 60.0, False, False, False)
        assert any("PDL1" in t for t in r["recommended_therapies"])

    def test_pdl1_below_50_no_pdl1_therapy(self):
        r = precision_medicine_routing(5.0, False, 40.0, False, False, False)
        assert not any("PDL1" in t for t in r["recommended_therapies"])

    def test_her2_adds_trastuzumab(self):
        r = precision_medicine_routing(5.0, False, 0.0, True, False, False)
        assert any("HER2" in t for t in r["recommended_therapies"])

    def test_brca_adds_parp(self):
        r = precision_medicine_routing(5.0, False, 0.0, False, True, False)
        assert any("PARP" in t for t in r["recommended_therapies"])

    def test_kras_adds_sotorasib(self):
        r = precision_medicine_routing(5.0, False, 0.0, False, False, True)
        assert any("sotorasib" in t for t in r["recommended_therapies"])

    def test_response_probabilities_in_unit_interval(self):
        r = precision_medicine_routing(20.0, True, 60.0, True, True, True)
        for prob in r["response_probability"].values():
            assert 0.0 <= prob <= 1.0

    def test_tmb_response_prob_increases_with_tmb(self):
        r_low = precision_medicine_routing(12.0, False, 0.0, False, False, False)
        r_high = precision_medicine_routing(25.0, False, 0.0, False, False, False)
        prob_low = r_low["response_probability"].get("pembrolizumab (TMB-H)", 0)
        prob_high = r_high["response_probability"].get("pembrolizumab (TMB-H)", 0)
        assert prob_high > prob_low

    def test_tmb_response_prob_capped_at_0_55(self):
        # TMB = 10 + 20 = 30, prob = 0.35 + 0.01*20 = 0.55 (capped)
        r = precision_medicine_routing(100.0, False, 0.0, False, False, False)
        prob = r["response_probability"].get("pembrolizumab (TMB-H)", 0)
        assert prob <= 0.55

    def test_precision_score_in_unit_interval(self):
        r = precision_medicine_routing(20.0, True, 60.0, True, True, True)
        assert 0.0 <= r["precision_score"] <= 1.0

    def test_precision_score_formula(self):
        r = precision_medicine_routing(5.0, False, 0.0, True, True, False)
        # n_targetable = 2 (HER2, BRCA)
        assert r["n_targetable_alterations"] == 2
        expected = (2 / 6) * PHI0
        assert abs(r["precision_score"] - expected) < 1e-12

    def test_invalid_tmb_raises(self):
        with pytest.raises(ValueError):
            precision_medicine_routing(-1.0, False, 0.0, False, False, False)

    def test_invalid_pdl1_raises(self):
        with pytest.raises(ValueError):
            precision_medicine_routing(5.0, False, 110.0, False, False, False)


# ─────────────────────────────────────────────────────────────────────────────
# E. Early Detection Improvement Pathway
# ─────────────────────────────────────────────────────────────────────────────

class TestDetectionImprovementPathway:
    def test_returns_required_keys(self):
        r = detection_improvement_pathway(0.515, 0.995, 0.003)
        for key in [
            "current_ppv", "current_npv",
            "required_specificity_for_target_ppv",
            "required_sensitivity_for_target_ppv",
            "optimal_screening_prevalence",
            "target_ppv", "prevalence", "sensitivity", "specificity",
            "status", "notes",
        ]:
            assert key in r, f"Missing key: {key}"

    def test_ppv_bayes_exact_galleri_params(self):
        """Verify exact Bayes' theorem calculation for Galleri parameters."""
        Se, Sp, P = 0.515, 0.995, 0.003
        r = detection_improvement_pathway(Se, Sp, P)
        expected_ppv = (Se * P) / (Se * P + (1 - Sp) * (1 - P))
        assert abs(r["current_ppv"] - expected_ppv) < 1e-12

    def test_npv_bayes_exact(self):
        Se, Sp, P = 0.515, 0.995, 0.003
        r = detection_improvement_pathway(Se, Sp, P)
        expected_npv = (Sp * (1 - P)) / ((1 - Se) * P + Sp * (1 - P))
        assert abs(r["current_npv"] - expected_npv) < 1e-12

    def test_current_ppv_in_unit_interval(self):
        r = detection_improvement_pathway(0.515, 0.995, 0.003)
        assert 0.0 <= r["current_ppv"] <= 1.0

    def test_current_npv_in_unit_interval(self):
        r = detection_improvement_pathway(0.515, 0.995, 0.003)
        assert 0.0 <= r["current_npv"] <= 1.0

    def test_required_specificity_in_unit_interval(self):
        r = detection_improvement_pathway(0.515, 0.995, 0.003)
        assert 0.0 <= r["required_specificity_for_target_ppv"] <= 1.0

    def test_required_sensitivity_in_unit_interval(self):
        r = detection_improvement_pathway(0.515, 0.995, 0.003)
        assert 0.0 <= r["required_sensitivity_for_target_ppv"] <= 1.0

    def test_optimal_prevalence_in_unit_interval(self):
        r = detection_improvement_pathway(0.515, 0.995, 0.003)
        assert 0.0 <= r["optimal_screening_prevalence"] <= 1.0

    def test_high_prevalence_raises_ppv(self):
        r_low = detection_improvement_pathway(0.515, 0.995, 0.003)
        r_high = detection_improvement_pathway(0.515, 0.995, 0.05)
        assert r_high["current_ppv"] > r_low["current_ppv"]

    def test_high_specificity_raises_ppv(self):
        r_low = detection_improvement_pathway(0.515, 0.990, 0.003)
        r_high = detection_improvement_pathway(0.515, 0.999, 0.003)
        assert r_high["current_ppv"] > r_low["current_ppv"]

    def test_required_specificity_raises_ppv_when_used(self):
        """Plugging required_specificity back in should give target_ppv."""
        Se, P = 0.515, 0.003
        target = 0.80
        r = detection_improvement_pathway(Se, 0.995, P, target_ppv=target)
        req_sp = r["required_specificity_for_target_ppv"]
        achieved_ppv = (Se * P) / (Se * P + (1 - req_sp) * (1 - P))
        assert abs(achieved_ppv - target) < 1e-8

    def test_optimal_prevalence_achieves_target_ppv(self):
        """Plugging optimal_prevalence back in should give target_ppv."""
        Se, Sp = 0.515, 0.995
        target = 0.80
        r = detection_improvement_pathway(Se, Sp, 0.003, target_ppv=target)
        P_opt = r["optimal_screening_prevalence"]
        achieved_ppv = (Se * P_opt) / (Se * P_opt + (1 - Sp) * (1 - P_opt))
        assert abs(achieved_ppv - target) < 1e-8

    def test_invalid_sensitivity_raises(self):
        with pytest.raises(ValueError):
            detection_improvement_pathway(1.5, 0.995, 0.003)

    def test_invalid_specificity_raises(self):
        with pytest.raises(ValueError):
            detection_improvement_pathway(0.515, -0.1, 0.003)

    def test_invalid_prevalence_raises(self):
        with pytest.raises(ValueError):
            detection_improvement_pathway(0.515, 0.995, 1.5)


# ─────────────────────────────────────────────────────────────────────────────
# F. Survivorship Care Scale Model
# ─────────────────────────────────────────────────────────────────────────────

class TestSurvivorshipCareScaleModel:
    def test_returns_required_keys(self):
        r = survivorship_care_scale_model(18_000_000, 0.60, 0.20, 0.10, 0.25)
        for key in [
            "effective_capacity", "unmet_contacts_remaining",
            "deficit_reduction_fraction", "contacts_served",
            "contacts_required", "current_capacity_fraction",
            "current_survivors", "status", "notes",
        ]:
            assert key in r, f"Missing key: {key}"

    def test_effective_capacity_never_exceeds_one(self):
        r = survivorship_care_scale_model(18_000_000, 0.60, 1.0, 1.0, 1.0)
        assert r["effective_capacity"] <= 1.0

    def test_effective_capacity_never_below_zero(self):
        r = survivorship_care_scale_model(18_000_000, 0.0, 0.0, 0.0, 0.0)
        assert r["effective_capacity"] >= 0.0

    def test_unmet_contacts_non_negative(self):
        r = survivorship_care_scale_model(18_000_000, 0.60, 0.20, 0.10, 0.25)
        assert r["unmet_contacts_remaining"] >= 0.0

    def test_contacts_served_le_contacts_required(self):
        r = survivorship_care_scale_model(18_000_000, 0.60, 0.20, 0.10, 0.25)
        assert r["contacts_served"] <= r["contacts_required"] + 1e-6

    def test_deficit_reduction_in_unit_interval(self):
        r = survivorship_care_scale_model(18_000_000, 0.60, 0.20, 0.10, 0.25)
        assert 0.0 <= r["deficit_reduction_fraction"] <= 1.0

    def test_full_interventions_serve_all_contacts(self):
        r = survivorship_care_scale_model(18_000_000, 0.60, 1.0, 1.0, 1.0)
        # effective_capacity = 1.0 → all contacts served
        assert abs(r["unmet_contacts_remaining"]) < 1e-3

    def test_more_interventions_reduce_unmet_contacts(self):
        r_low = survivorship_care_scale_model(18_000_000, 0.60, 0.05, 0.05, 0.05)
        r_high = survivorship_care_scale_model(18_000_000, 0.60, 0.20, 0.15, 0.25)
        assert r_high["unmet_contacts_remaining"] < r_low["unmet_contacts_remaining"]

    def test_contacts_required_formula(self):
        survivors = 10_000_000
        r = survivorship_care_scale_model(survivors, 0.60, 0.0, 0.0, 0.0)
        assert abs(r["contacts_required"] - survivors * 2.3) < 1e-3

    def test_zero_survivors_zero_unmet(self):
        r = survivorship_care_scale_model(0, 0.60, 0.20, 0.10, 0.25)
        assert r["unmet_contacts_remaining"] == 0.0
        assert r["contacts_required"] == 0.0

    def test_baseline_capacity_matches_input(self):
        r = survivorship_care_scale_model(18_000_000, 0.75, 0.0, 0.0, 0.0)
        assert abs(r["current_capacity_fraction"] - 0.75) < 1e-12

    def test_invalid_capacity_raises(self):
        with pytest.raises(ValueError):
            survivorship_care_scale_model(18_000_000, 1.5, 0.0, 0.0, 0.0)

    def test_invalid_telehealth_raises(self):
        with pytest.raises(ValueError):
            survivorship_care_scale_model(18_000_000, 0.60, -0.1, 0.0, 0.0)

    def test_invalid_survivors_raises(self):
        with pytest.raises(ValueError):
            survivorship_care_scale_model(-1, 0.60, 0.0, 0.0, 0.0)


# ─────────────────────────────────────────────────────────────────────────────
# G. Financial Access Intervention
# ─────────────────────────────────────────────────────────────────────────────

class TestFinancialAccessIntervention:
    def test_returns_required_keys(self):
        r = financial_access_intervention(150_000, 0.85, 62_000, 6_000)
        for key in [
            "oop_before", "oop_after",
            "toxicity_score_before", "toxicity_score_after",
            "financially_toxic_before", "financially_toxic_after",
            "toxicity_eliminated", "oop_reduction",
            "status", "notes",
        ]:
            assert key in r, f"Missing key: {key}"

    def test_oop_before_formula(self):
        r = financial_access_intervention(150_000, 0.85, 62_000, 6_000)
        expected = 150_000 * (1 - 0.85)
        assert abs(r["oop_before"] - expected) < 1e-6

    def test_oop_after_capped_at_cap(self):
        r = financial_access_intervention(150_000, 0.85, 62_000, 6_000)
        assert r["oop_after"] <= 6_000

    def test_oop_after_le_oop_before(self):
        r = financial_access_intervention(150_000, 0.85, 62_000, 6_000)
        assert r["oop_after"] <= r["oop_before"]

    def test_toxicity_score_before_formula(self):
        r = financial_access_intervention(150_000, 0.85, 62_000, 6_000)
        expected = r["oop_before"] / 62_000
        assert abs(r["toxicity_score_before"] - expected) < 1e-10

    def test_toxicity_score_after_formula(self):
        r = financial_access_intervention(150_000, 0.85, 62_000, 6_000)
        expected = r["oop_after"] / 62_000
        assert abs(r["toxicity_score_after"] - expected) < 1e-10

    def test_anti_pd1_financially_toxic_before(self):
        """Anti-PD1 at $150k, 85% coverage, $62k income → financially toxic."""
        r = financial_access_intervention(150_000, 0.85, 62_000, 100_000)
        # oop_before = 22,500; toxicity = 22500/62000 = 0.363 > 0.20
        assert r["financially_toxic_before"] is True

    def test_oop_cap_eliminates_toxicity(self):
        """OOP cap at $6,000 on $62k income: 6000/62000 = 0.097 < 0.20 threshold."""
        r = financial_access_intervention(150_000, 0.85, 62_000, 6_000)
        assert r["financially_toxic_after"] is False
        assert r["toxicity_eliminated"] is True

    def test_high_cap_does_not_eliminate_toxicity(self):
        r = financial_access_intervention(150_000, 0.85, 62_000, 50_000)
        # oop_after = 22,500; 22500/62000 = 0.363 > 0.20
        assert r["financially_toxic_after"] is True
        assert r["toxicity_eliminated"] is False

    def test_zero_cost_drug_no_toxicity(self):
        r = financial_access_intervention(0, 0.85, 62_000, 6_000)
        assert r["oop_before"] == 0.0
        assert r["financially_toxic_before"] is False
        assert r["toxicity_eliminated"] is False

    def test_oop_reduction_formula(self):
        r = financial_access_intervention(150_000, 0.85, 62_000, 6_000)
        assert abs(r["oop_reduction"] - (r["oop_before"] - r["oop_after"])) < 1e-6

    def test_invalid_cost_raises(self):
        with pytest.raises(ValueError):
            financial_access_intervention(-1, 0.85, 62_000, 6_000)

    def test_invalid_coverage_raises(self):
        with pytest.raises(ValueError):
            financial_access_intervention(150_000, 1.5, 62_000, 6_000)

    def test_invalid_income_raises(self):
        with pytest.raises(ValueError):
            financial_access_intervention(150_000, 0.85, 0, 6_000)

    def test_invalid_oop_cap_raises(self):
        with pytest.raises(ValueError):
            financial_access_intervention(150_000, 0.85, 62_000, -1)


# ─────────────────────────────────────────────────────────────────────────────
# H. Integrated Solution Roadmap
# ─────────────────────────────────────────────────────────────────────────────

class TestCancerSolutionRoadmap:
    def test_returns_list(self):
        r = cancer_solution_roadmap()
        assert isinstance(r, list)

    def test_default_5_entries(self):
        r = cancer_solution_roadmap()
        assert len(r) == 5

    def test_n_years_respected(self):
        for n in [1, 2, 3, 4, 5]:
            r = cancer_solution_roadmap(n_years=n)
            assert len(r) == n

    def test_each_entry_has_required_keys(self):
        r = cancer_solution_roadmap()
        for entry in r:
            for key in [
                "year", "interventions_applied", "estimated_lives_impacted",
                "bottleneck_gaps_closed", "cumulative_lives_impacted",
                "budget_usd", "status", "notes",
            ]:
                assert key in entry, f"Missing key: {key}"

    def test_years_are_sequential(self):
        r = cancer_solution_roadmap()
        for i, entry in enumerate(r):
            assert entry["year"] == i + 1

    def test_cumulative_increases_monotonically(self):
        r = cancer_solution_roadmap()
        for i in range(1, len(r)):
            assert r[i]["cumulative_lives_impacted"] >= r[i - 1]["cumulative_lives_impacted"]

    def test_estimated_lives_positive(self):
        r = cancer_solution_roadmap()
        for entry in r:
            assert entry["estimated_lives_impacted"] > 0

    def test_interventions_non_empty(self):
        r = cancer_solution_roadmap()
        for entry in r:
            assert len(entry["interventions_applied"]) > 0

    def test_budget_stored_correctly(self):
        r = cancer_solution_roadmap(budget_usd_per_year=2e9)
        for entry in r:
            assert entry["budget_usd"] == 2e9

    def test_n_years_greater_than_5_works(self):
        r = cancer_solution_roadmap(n_years=7)
        assert len(r) == 7

    def test_invalid_budget_raises(self):
        with pytest.raises(ValueError):
            cancer_solution_roadmap(budget_usd_per_year=0)

    def test_invalid_n_years_raises(self):
        with pytest.raises(ValueError):
            cancer_solution_roadmap(n_years=0)

    def test_cumulative_at_year_5_positive(self):
        r = cancer_solution_roadmap(n_years=5)
        assert r[-1]["cumulative_lives_impacted"] > 0


# ─────────────────────────────────────────────────────────────────────────────
# I. Resistance Prevention Model
# ─────────────────────────────────────────────────────────────────────────────

class TestResistancePreventionModel:
    def test_returns_required_keys(self):
        r = resistance_prevention_model(
            int(1e9), 1e-7, 3, 5, 0.30
        )
        for key in [
            "base_resistance_probability", "resistance_suppression",
            "final_resistance_probability", "recommended_strategy",
            "p_sensitive_to_any_one_drug", "n_drugs_in_combination",
            "status", "notes",
        ]:
            assert key in r, f"Missing key: {key}"

    def test_probabilities_in_unit_interval(self):
        r = resistance_prevention_model(int(1e9), 1e-7, 3, 5, 0.30)
        assert 0.0 <= r["base_resistance_probability"] <= 1.0
        assert 0.0 <= r["final_resistance_probability"] <= 1.0

    def test_resistance_suppression_non_negative(self):
        r = resistance_prevention_model(int(1e9), 1e-7, 3, 5, 0.30)
        assert r["resistance_suppression"] >= 0.0

    def test_final_le_base_resistance(self):
        r = resistance_prevention_model(int(1e9), 1e-7, 3, 5, 0.30)
        assert r["final_resistance_probability"] <= r["base_resistance_probability"] + 1e-12

    def test_final_resistance_non_negative(self):
        r = resistance_prevention_model(int(1e9), 1e-7, 3, 10, 0.50)
        assert r["final_resistance_probability"] >= 0.0

    def test_small_tumour_low_resistance(self):
        r = resistance_prevention_model(1000, 1e-9, 1, 0, 0.0)
        assert r["base_resistance_probability"] < 0.01

    def test_large_tumour_high_resistance(self):
        r = resistance_prevention_model(int(1e9), 1e-7, 1, 0, 0.0)
        assert r["base_resistance_probability"] > 0.99

    def test_more_drugs_reduces_base_probability(self):
        r1 = resistance_prevention_model(int(1e6), 1e-7, 1, 0, 0.0)
        r3 = resistance_prevention_model(int(1e6), 1e-7, 3, 0, 0.0)
        assert r3["base_resistance_probability"] <= r1["base_resistance_probability"]

    def test_adaptive_therapy_reduces_final_probability(self):
        r_std = resistance_prevention_model(int(1e6), 1e-7, 2, 0, 0.0)
        r_adp = resistance_prevention_model(int(1e6), 1e-7, 2, 5, 0.30)
        assert r_adp["final_resistance_probability"] <= r_std["final_resistance_probability"] + 1e-12

    def test_zero_adaptive_cycles_no_suppression(self):
        r = resistance_prevention_model(int(1e6), 1e-7, 2, 0, 0.30)
        assert r["resistance_suppression"] == 0.0

    def test_recommended_strategy_is_string(self):
        r = resistance_prevention_model(int(1e9), 1e-7, 2, 5, 0.30)
        assert isinstance(r["recommended_strategy"], str)
        assert len(r["recommended_strategy"]) > 0

    def test_p_sensitive_bayes_formula(self):
        """Verify Luria-Delbrück formula: P = 1 - exp(-mu*N)."""
        mu, N = 1e-7, 1e6
        r = resistance_prevention_model(int(N), mu, 1, 0, 0.0)
        expected = 1.0 - math.exp(-mu * N)
        assert abs(r["p_sensitive_to_any_one_drug"] - expected) < 1e-12

    def test_n_drugs_stored_correctly(self):
        r = resistance_prevention_model(int(1e6), 1e-7, 4, 0, 0.0)
        assert r["n_drugs_in_combination"] == 4

    def test_invalid_tumor_size_raises(self):
        with pytest.raises(ValueError):
            resistance_prevention_model(0, 1e-7, 2, 5, 0.30)

    def test_invalid_mutation_rate_raises(self):
        with pytest.raises(ValueError):
            resistance_prevention_model(int(1e6), 0.0, 2, 5, 0.30)

    def test_invalid_n_drugs_raises(self):
        with pytest.raises(ValueError):
            resistance_prevention_model(int(1e6), 1e-7, 0, 5, 0.30)

    def test_invalid_adaptive_cycles_raises(self):
        with pytest.raises(ValueError):
            resistance_prevention_model(int(1e6), 1e-7, 2, -1, 0.30)

    def test_invalid_holiday_fraction_raises(self):
        with pytest.raises(ValueError):
            resistance_prevention_model(int(1e6), 1e-7, 2, 5, 1.5)
