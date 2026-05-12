# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_pillar228_cancer_bottleneck_calculator.py
=====================================================
Tests for Pillar 228: Cancer Bottleneck Calculator.

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

from src.core.pillar228_cancer_bottleneck_calculator import (
    # Constants
    N_W,
    K_CS,
    C_S,
    PHI0,
    # Empirical baselines
    FIVE_YEAR_SURVIVAL_RATE,
    PRECLINICAL_APPROVAL_RATE,
    TRIAL_PARTICIPATION_RATE,
    CTDNA_SENSITIVITY_EARLY,
    CTDNA_SENSITIVITY_LATE,
    CTDNA_SPECIFICITY,
    TMB_RESPONSE_THRESHOLD_MUT_PER_MB,
    # Roadblock A
    clonal_shannon_entropy,
    multi_drug_kill_probability,
    heterogeneity_resistance_factor,
    # Roadblock B
    resistance_probability,
    adaptive_fitness_selection,
    tmb_response_score,
    ftum_resistance_attractor,
    # Roadblock C
    preclinical_translation_success,
    preclinical_paradox_score,
    # Bottleneck 1
    enrollment_deficit,
    trial_timeline_extension,
    # Bottleneck 2
    drug_shortage_impact,
    # Bottleneck 3
    representation_bias_score,
    ai_equity_gap,
    # Bottleneck 4
    therapeutic_index,
    nanoparticle_delivery_efficiency,
    # Bottleneck 5
    activation_tail_months,
    # Bottleneck 6
    explainability_tradeoff,
    # Bottleneck 7
    access_barrier_fraction,
    # Bottleneck 8
    ctc_detection_sensitivity,
    # Bottleneck 9
    liquid_biopsy_ppv_npv,
    # Bottleneck 10
    trial_site_capacity,
    # Bottleneck 11
    genetic_testing_equity_gap,
    # Bottleneck 12
    survivorship_care_deficit,
    # Summary
    bottleneck_report,
)


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

    def test_survival_rate_reasonable(self):
        assert 0.5 <= FIVE_YEAR_SURVIVAL_RATE <= 1.0

    def test_preclinical_approval_rate_reasonable(self):
        assert 0.01 <= PRECLINICAL_APPROVAL_RATE <= 0.20

    def test_trial_participation_rate_reasonable(self):
        assert 0.01 <= TRIAL_PARTICIPATION_RATE <= 0.15

    def test_ctdna_sensitivity_ordering(self):
        """Late-stage sensitivity must exceed early-stage."""
        assert CTDNA_SENSITIVITY_LATE > CTDNA_SENSITIVITY_EARLY

    def test_ctdna_specificity_high(self):
        assert CTDNA_SPECIFICITY > 0.99

    def test_tmb_threshold_is_10(self):
        """FDA FoundationOne CDx threshold."""
        assert TMB_RESPONSE_THRESHOLD_MUT_PER_MB == 10.0


# ─────────────────────────────────────────────────────────────────────────────
# Roadblock A: Heterogeneity
# ─────────────────────────────────────────────────────────────────────────────

class TestClonalShannonEntropy:
    def test_monoclonal_zero_entropy(self):
        r = clonal_shannon_entropy([1.0])
        assert abs(r["entropy_bits"]) < 1e-12

    def test_two_equal_clones_one_bit(self):
        r = clonal_shannon_entropy([0.5, 0.5])
        assert abs(r["entropy_bits"] - 1.0) < 1e-12

    def test_four_equal_clones_two_bits(self):
        r = clonal_shannon_entropy([0.25, 0.25, 0.25, 0.25])
        assert abs(r["entropy_bits"] - 2.0) < 1e-12

    def test_normalised_entropy_range(self):
        r = clonal_shannon_entropy([0.6, 0.3, 0.1])
        assert 0.0 <= r["normalised_entropy"] <= 1.0

    def test_unequal_clones_less_than_max(self):
        r = clonal_shannon_entropy([0.7, 0.2, 0.1])
        assert r["entropy_bits"] < r["max_entropy_bits"]

    def test_equal_clones_normalised_is_one(self):
        r = clonal_shannon_entropy([1 / 3, 1 / 3, 1 / 3])
        assert abs(r["normalised_entropy"] - 1.0) < 1e-10

    def test_n_clones_correct(self):
        fracs = [0.6, 0.25, 0.10, 0.04, 0.01]
        r = clonal_shannon_entropy(fracs)
        assert r["n_clones"] == 5

    def test_invalid_sum_raises(self):
        with pytest.raises(ValueError):
            clonal_shannon_entropy([0.5, 0.4])

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            clonal_shannon_entropy([])

    def test_negative_fraction_raises(self):
        with pytest.raises(ValueError):
            clonal_shannon_entropy([1.1, -0.1])

    def test_entropy_increases_with_diversity(self):
        r2 = clonal_shannon_entropy([0.5, 0.5])
        r3 = clonal_shannon_entropy([1 / 3, 1 / 3, 1 / 3])
        assert r3["entropy_bits"] > r2["entropy_bits"]


class TestMultiDrugKillProbability:
    def test_single_drug_single_clone(self):
        r = multi_drug_kill_probability(1, 0.9, 1)
        assert abs(r["p_kill_all"] - 0.9) < 1e-12

    def test_ten_clones_90_percent_kill_rate(self):
        r = multi_drug_kill_probability(10, 0.9, 1)
        expected = 0.9 ** 10
        assert abs(r["p_kill_all"] - expected) < 1e-12

    def test_two_drugs_reduces_required_power(self):
        r1 = multi_drug_kill_probability(5, 0.9, 1)
        r2 = multi_drug_kill_probability(5, 0.9, 2)
        # Two drugs means p_kill_all = 0.9^(2*5) = 0.9^10 < 0.9^5
        assert r2["p_kill_all"] < r1["p_kill_all"]

    def test_perfect_kill_rate_kills_all(self):
        r = multi_drug_kill_probability(10, 1.0, 3)
        assert abs(r["p_kill_all"] - 1.0) < 1e-12

    def test_p_kill_plus_p_escape_equals_one(self):
        r = multi_drug_kill_probability(5, 0.8, 2)
        assert abs(r["p_kill_all"] + r["p_escape"] - 1.0) < 1e-12

    def test_invalid_n_clones(self):
        with pytest.raises(ValueError):
            multi_drug_kill_probability(0, 0.9)

    def test_invalid_kill_rate_zero(self):
        with pytest.raises(ValueError):
            multi_drug_kill_probability(5, 0.0)

    def test_invalid_kill_rate_over_one(self):
        with pytest.raises(ValueError):
            multi_drug_kill_probability(5, 1.1)

    def test_invalid_n_drugs(self):
        with pytest.raises(ValueError):
            multi_drug_kill_probability(5, 0.9, 0)


class TestHeterogeneityResistanceFactor:
    def test_monoclonal_factor_is_one(self):
        r = heterogeneity_resistance_factor(1)
        assert abs(r["resistance_factor"] - 1.0) < 1e-12

    def test_two_clones_factor(self):
        r = heterogeneity_resistance_factor(2)
        expected = 1.0 + 1 * C_S
        assert abs(r["resistance_factor"] - expected) < 1e-12

    def test_factor_increases_with_clones(self):
        r3 = heterogeneity_resistance_factor(3)
        r5 = heterogeneity_resistance_factor(5)
        assert r5["resistance_factor"] > r3["resistance_factor"]

    def test_saturation_at_nw(self):
        r = heterogeneity_resistance_factor(N_W)
        assert r["saturation_clones"] == N_W

    def test_mutation_capacity_positive(self):
        r = heterogeneity_resistance_factor(10)
        assert r["mutation_capacity_bits"] > 0

    def test_invalid_n_clones(self):
        with pytest.raises(ValueError):
            heterogeneity_resistance_factor(0)


# ─────────────────────────────────────────────────────────────────────────────
# Roadblock B: Treatment Resistance
# ─────────────────────────────────────────────────────────────────────────────

class TestResistanceProbability:
    def test_large_tumour_near_certain_resistance(self):
        """1 cm³ tumour at typical mutation rate: P(resistance) ≈ 1."""
        r = resistance_probability(1e-7, 1e9, 1)
        assert r["p_resistance"] > 0.9999

    def test_small_tumour_low_resistance(self):
        """Very small tumour (100 cells): P(resistance) much less than 1."""
        r = resistance_probability(1e-7, 100, 1)
        assert r["p_resistance"] < 0.01

    def test_single_mutation_exponential_formula(self):
        mu, N = 1e-6, 1e5
        r = resistance_probability(mu, N, 1)
        expected = 1.0 - math.exp(-mu * N)
        assert abs(r["p_resistance"] - expected) < 1e-12

    def test_p_resistance_plus_p_sensitive_equals_one(self):
        r = resistance_probability(1e-7, 1e6, 1)
        assert abs(r["p_resistance"] + r["p_sensitive"] - 1.0) < 1e-12

    def test_two_mutations_lower_probability(self):
        r1 = resistance_probability(1e-4, 1e4, 1)
        r2 = resistance_probability(1e-4, 1e4, 2)
        assert r2["p_resistance"] < r1["p_resistance"]

    def test_mu_n_stored_correctly(self):
        r = resistance_probability(2e-6, 5e5, 1)
        assert abs(r["mu_N"] - 1.0) < 1e-10

    def test_invalid_mu(self):
        with pytest.raises(ValueError):
            resistance_probability(0, 1e9, 1)

    def test_invalid_n_cells(self):
        with pytest.raises(ValueError):
            resistance_probability(1e-7, 0, 1)

    def test_invalid_k(self):
        with pytest.raises(ValueError):
            resistance_probability(1e-7, 1e9, 0)


class TestAdaptiveFitnessSelection:
    def test_final_fraction_increases(self):
        r = adaptive_fitness_selection(0.05, 100, 1e-4)
        assert r["f_final"] > 1e-4

    def test_high_advantage_rapid_takeover(self):
        r_low = adaptive_fitness_selection(0.01, 200, 1e-4)
        r_high = adaptive_fitness_selection(0.10, 200, 1e-4)
        assert r_high["f_final"] > r_low["f_final"]

    def test_doubling_time_from_s(self):
        s = 0.1
        r = adaptive_fitness_selection(s, 50, 1e-3)
        expected_doubling = math.log(2) / s
        assert abs(r["doubling_time_generations"] - expected_doubling) < 1e-10

    def test_f_final_bounded(self):
        r = adaptive_fitness_selection(0.5, 1000, 1e-6)
        assert 0.0 < r["f_final"] <= 1.0

    def test_trajectory_length(self):
        r = adaptive_fitness_selection(0.05, 100, 1e-4)
        # 10 steps + 1 (including t=0)
        assert len(r["fraction_trajectory"]) == 11

    def test_invalid_s(self):
        with pytest.raises(ValueError):
            adaptive_fitness_selection(0.0, 50, 1e-4)

    def test_invalid_n_gen(self):
        with pytest.raises(ValueError):
            adaptive_fitness_selection(0.1, 0, 1e-4)

    def test_invalid_initial_fraction_zero(self):
        with pytest.raises(ValueError):
            adaptive_fitness_selection(0.1, 50, 0.0)

    def test_invalid_initial_fraction_one(self):
        with pytest.raises(ValueError):
            adaptive_fitness_selection(0.1, 50, 1.0)


class TestTmbResponseScore:
    def test_above_threshold_response_predicted(self):
        r = tmb_response_score(15.0)
        assert r["predicted_response"] is True

    def test_at_threshold_response_predicted(self):
        r = tmb_response_score(10.0)
        assert r["predicted_response"] is True

    def test_below_threshold_no_response(self):
        r = tmb_response_score(5.0)
        assert r["predicted_response"] is False

    def test_normalised_per_kcs(self):
        tmb = 74.0
        r = tmb_response_score(tmb)
        assert abs(r["tmb_normalised_per_kcs"] - 1.0) < 1e-12

    def test_fold_above_threshold_correct(self):
        r = tmb_response_score(20.0)
        assert abs(r["fold_above_threshold"] - 2.0) < 1e-12

    def test_zero_tmb_no_response(self):
        r = tmb_response_score(0.0)
        assert r["predicted_response"] is False

    def test_invalid_negative_tmb(self):
        with pytest.raises(ValueError):
            tmb_response_score(-1.0)


class TestFtumResistanceAttractor:
    def test_convergence_to_phi0(self):
        r = ftum_resistance_attractor(200)
        assert abs(r["final_value"] - PHI0) < 1e-10

    def test_converged_flag_true(self):
        r = ftum_resistance_attractor(200)
        assert r["converged"] is True

    def test_not_converged_at_1_iteration(self):
        r = ftum_resistance_attractor(1)
        assert abs(r["final_value"] - PHI0) > 0.1

    def test_phi0_stored_correctly(self):
        r = ftum_resistance_attractor(100)
        assert abs(r["phi0"] - PHI0) < 1e-12

    def test_n_iterations_stored(self):
        r = ftum_resistance_attractor(42)
        assert r["n_iterations"] == 42

    def test_invalid_n_iterations(self):
        with pytest.raises(ValueError):
            ftum_resistance_attractor(0)


# ─────────────────────────────────────────────────────────────────────────────
# Roadblock C: Preclinical Paradox
# ─────────────────────────────────────────────────────────────────────────────

class TestPreclinicalTranslationSuccess:
    def test_valid_phases(self):
        for phase in ["preclinical", "phase1", "phase2", "phase3", "nda"]:
            r = preclinical_translation_success(phase)
            assert 0 < r["phase_success_rate"] <= 1.0

    def test_cumulative_decreases_with_later_phases(self):
        r_p1 = preclinical_translation_success("phase1")
        r_p2 = preclinical_translation_success("phase2")
        r_p3 = preclinical_translation_success("phase3")
        # Cumulative success drops at each phase
        assert r_p1["cumulative_success_from_preclinical"] > r_p2["cumulative_success_from_preclinical"]
        assert r_p2["cumulative_success_from_preclinical"] > r_p3["cumulative_success_from_preclinical"]

    def test_expected_failures_correct(self):
        r = preclinical_translation_success("preclinical")
        expected_fail = (1.0 / PRECLINICAL_APPROVAL_RATE) - 1.0
        assert abs(r["expected_failures_per_approval"] - expected_fail) < 0.01

    def test_invalid_phase_raises(self):
        with pytest.raises(ValueError):
            preclinical_translation_success("phase5")

    def test_preclinical_phase_success_rate_equals_approval_rate(self):
        r = preclinical_translation_success("preclinical")
        assert abs(r["phase_success_rate"] - PRECLINICAL_APPROVAL_RATE) < 1e-10


class TestPreclinicalParadoxScore:
    def test_expected_human_efficacy(self):
        r = preclinical_paradox_score(0.8)
        assert abs(r["expected_human_efficacy"] - 0.8 * PRECLINICAL_APPROVAL_RATE) < 1e-12

    def test_translation_efficiency_kcs(self):
        r = preclinical_paradox_score(0.8)
        expected_te = 0.8 * PRECLINICAL_APPROVAL_RATE * K_CS
        assert abs(r["translation_efficiency_kcs"] - expected_te) < 1e-10

    def test_above_kcs_threshold_high_efficacy(self):
        # animal_efficacy = 1.0: te = PRECLINICAL_APPROVAL_RATE * 74 ≈ 4.81 > 1
        r = preclinical_paradox_score(1.0)
        assert r["above_kcs_threshold"] is True

    def test_invalid_animal_efficacy(self):
        with pytest.raises(ValueError):
            preclinical_paradox_score(1.5)

    def test_invalid_translation_factor(self):
        with pytest.raises(ValueError):
            preclinical_paradox_score(0.8, human_translation_factor=0.0)


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 1: Trial Enrollment
# ─────────────────────────────────────────────────────────────────────────────

class TestEnrollmentDeficit:
    def test_enrolled_fraction_correct(self):
        r = enrollment_deficit(100_000, 0.04)
        assert abs(r["enrolled"] - 4_000) < 1e-6

    def test_not_enrolled_complement(self):
        r = enrollment_deficit(100_000, 0.04)
        assert abs(r["not_enrolled"] - 96_000) < 1e-6

    def test_deficit_fraction(self):
        r = enrollment_deficit(100_000, 0.05)
        assert abs(r["deficit_fraction"] - 0.95) < 1e-12

    def test_full_participation_no_deficit(self):
        r = enrollment_deficit(100_000, 1.0)
        assert abs(r["not_enrolled"]) < 1e-6

    def test_per_site_monthly_empirical_value(self):
        r = enrollment_deficit(100_000)
        assert abs(r["per_site_monthly_empirical"] - 0.3) < 1e-12

    def test_invalid_eligible_patients(self):
        with pytest.raises(ValueError):
            enrollment_deficit(0)

    def test_invalid_participation_rate(self):
        with pytest.raises(ValueError):
            enrollment_deficit(100_000, 1.5)


class TestTrialTimelineExtension:
    def test_no_underenrollment_no_extension(self):
        r = trial_timeline_extension(36, 0.0)
        assert abs(r["extension_months"]) < 1e-12

    def test_full_underenrollment_31_percent_extension(self):
        r = trial_timeline_extension(36, 1.0)
        assert abs(r["extension_months"] - 36 * 0.31) < 1e-10

    def test_total_months_correct(self):
        r = trial_timeline_extension(36, 0.5)
        expected = 36 + 36 * 0.31 * 0.5
        assert abs(r["total_months"] - expected) < 1e-10

    def test_invalid_base_months(self):
        with pytest.raises(ValueError):
            trial_timeline_extension(0, 0.5)

    def test_invalid_underenrollment(self):
        with pytest.raises(ValueError):
            trial_timeline_extension(36, 1.5)


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 2: Drug Shortages
# ─────────────────────────────────────────────────────────────────────────────

class TestDrugShortageImpact:
    def test_no_shortage_no_disruption(self):
        r = drug_shortage_impact(0.0, 100_000)
        assert r["patients_disrupted"] == 0.0

    def test_full_shortage_all_disrupted(self):
        r = drug_shortage_impact(1.0, 100_000)
        assert abs(r["patients_disrupted"] - 100_000) < 1e-6

    def test_disrupted_plus_optimal_equals_total(self):
        r = drug_shortage_impact(0.20, 500_000)
        assert abs(r["patients_disrupted"] + r["patients_with_optimal_care"]
                   - 500_000) < 1e-6

    def test_efficacy_loss(self):
        r = drug_shortage_impact(0.20, 500_000, 0.78)
        assert abs(r["efficacy_loss_fraction"] - 0.22) < 1e-12

    def test_outcome_reduction_correct(self):
        r = drug_shortage_impact(0.20, 500_000, 0.78)
        expected = 100_000 * 0.22
        assert abs(r["expected_outcome_reduction"] - expected) < 1e-6

    def test_invalid_shortage_fraction(self):
        with pytest.raises(ValueError):
            drug_shortage_impact(1.5, 100_000)

    def test_invalid_substitution_ratio(self):
        with pytest.raises(ValueError):
            drug_shortage_impact(0.2, 100_000, 0.0)


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 3: Data Silos
# ─────────────────────────────────────────────────────────────────────────────

class TestRepresentationBiasScore:
    def test_no_bias_equal_representation(self):
        r = representation_bias_score(0.6, 0.6)
        assert abs(r["bias_ratio"] - 1.0) < 1e-12

    def test_2x_bias_is_1_bit(self):
        r = representation_bias_score(0.8, 0.4)
        assert abs(r["log2_bias_bits"] - 1.0) < 1e-10

    def test_bias_ratio_gt_one_means_overrepresented(self):
        r = representation_bias_score(0.85, 0.40)
        assert r["bias_ratio"] > 1.0

    def test_minority_train_fraction_inferred(self):
        r = representation_bias_score(0.85, 0.40)
        assert abs(r["minority_train_fraction_inferred"] - 0.15) < 1e-12

    def test_invalid_majority_fraction(self):
        with pytest.raises(ValueError):
            representation_bias_score(0.0, 0.40)

    def test_invalid_minority_pop_fraction(self):
        with pytest.raises(ValueError):
            representation_bias_score(0.85, 0.0)


class TestAiEquityGap:
    def test_no_gap(self):
        r = ai_equity_gap(0.85, 0.85)
        assert abs(r["absolute_gap"]) < 1e-12

    def test_gap_correct(self):
        r = ai_equity_gap(0.90, 0.82)
        assert abs(r["absolute_gap"] - 0.08) < 1e-12

    def test_relative_gap_correct(self):
        r = ai_equity_gap(0.90, 0.82)
        expected_rel = 0.08 / 0.90
        assert abs(r["relative_gap"] - expected_rel) < 1e-12

    def test_invalid_majority_auc(self):
        with pytest.raises(ValueError):
            ai_equity_gap(0.3, 0.8)

    def test_invalid_minority_auc(self):
        with pytest.raises(ValueError):
            ai_equity_gap(0.85, 1.5)


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 4: Off-Target Toxicity
# ─────────────────────────────────────────────────────────────────────────────

class TestTherapeuticIndex:
    def test_ti_value_correct(self):
        r = therapeutic_index(30.0, 15.0)
        assert abs(r["therapeutic_index"] - 2.0) < 1e-12

    def test_narrow_ti_classification(self):
        r = therapeutic_index(4.5, 3.0)
        assert "NARROW" in r["classification"]

    def test_wide_ti_classification(self):
        r = therapeutic_index(100.0, 5.0)
        assert "WIDE" in r["classification"]

    def test_moderate_ti_classification(self):
        r = therapeutic_index(15.0, 4.0)
        # TI = 3.75 → MODERATE
        assert "MODERATE" in r["classification"]

    def test_invalid_ld50_zero(self):
        with pytest.raises(ValueError):
            therapeutic_index(0.0, 5.0)

    def test_invalid_ed50_zero(self):
        with pytest.raises(ValueError):
            therapeutic_index(10.0, 0.0)

    def test_ed50_ge_ld50_raises(self):
        with pytest.raises(ValueError):
            therapeutic_index(5.0, 5.0)

    def test_ed50_gt_ld50_raises(self):
        with pytest.raises(ValueError):
            therapeutic_index(5.0, 10.0)


class TestNanoparticleDeliveryEfficiency:
    def test_passive_only_no_enhancement(self):
        r = nanoparticle_delivery_efficiency(0.007, 1.0)
        assert abs(r["total_delivery_fraction"] - 0.007) < 1e-10

    def test_targeting_multiplies_delivery(self):
        r = nanoparticle_delivery_efficiency(0.007, 5.0)
        assert abs(r["total_delivery_fraction"] - min(0.007 * 5, 1.0)) < 1e-10

    def test_off_target_is_complement(self):
        r = nanoparticle_delivery_efficiency(0.01, 2.0)
        assert abs(r["off_target_fraction"] + r["total_delivery_fraction"] - 1.0) < 1e-10

    def test_delivery_capped_at_one(self):
        r = nanoparticle_delivery_efficiency(0.9, 5.0)
        assert r["total_delivery_fraction"] <= 1.0

    def test_nw_channels_stored(self):
        r = nanoparticle_delivery_efficiency(0.007)
        assert r["n_w_channels"] == N_W

    def test_invalid_epr_fraction(self):
        with pytest.raises(ValueError):
            nanoparticle_delivery_efficiency(0.0)

    def test_invalid_targeting_below_one(self):
        with pytest.raises(ValueError):
            nanoparticle_delivery_efficiency(0.007, 0.5)


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 5: Regulatory Delays
# ─────────────────────────────────────────────────────────────────────────────

class TestActivationTailMonths:
    def test_zero_amendments_zero_amendment_delay(self):
        r = activation_tail_months(0, 3)
        assert abs(r["amendment_delay_months"]) < 1e-12

    def test_one_amendment_five_months(self):
        r = activation_tail_months(1, 0)
        assert abs(r["amendment_delay_months"] - 5.0) < 1e-12

    def test_site_activation_correct(self):
        r = activation_tail_months(0, 4, base_activation_months=2.0)
        assert abs(r["site_activation_months"] - 8.0) < 1e-12

    def test_total_delay_additive(self):
        r = activation_tail_months(3, 5)
        assert abs(r["total_delay_months"] - (3 * 5 + 5 * 2)) < 1e-12

    def test_invalid_negative_amendments(self):
        with pytest.raises(ValueError):
            activation_tail_months(-1, 3)

    def test_invalid_negative_sites(self):
        with pytest.raises(ValueError):
            activation_tail_months(2, -1)

    def test_invalid_base_months(self):
        with pytest.raises(ValueError):
            activation_tail_months(2, 3, base_activation_months=0.0)


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 6: Black-Box AI
# ─────────────────────────────────────────────────────────────────────────────

class TestExplainabilityTradeoff:
    def test_clinical_utility_product(self):
        r = explainability_tradeoff(0.90, 0.80)
        assert abs(r["clinical_utility"] - 0.90 * 0.80) < 1e-12

    def test_high_auc_low_interpretability_fails_phi0(self):
        r = explainability_tradeoff(0.93, 0.10)
        assert r["above_phi0_threshold"] is False

    def test_moderate_auc_high_interpretability_passes_phi0(self):
        # 0.82 × 0.95 = 0.779 > φ₀ ≈ 0.739
        r = explainability_tradeoff(0.82, 0.95)
        assert r["above_phi0_threshold"] is True

    def test_phi0_threshold_stored(self):
        r = explainability_tradeoff(0.85, 0.85)
        assert abs(r["phi0_threshold"] - PHI0) < 1e-12

    def test_invalid_auc(self):
        with pytest.raises(ValueError):
            explainability_tradeoff(1.5, 0.8)

    def test_invalid_interpretability(self):
        with pytest.raises(ValueError):
            explainability_tradeoff(0.85, 1.5)


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 7: Financial Asymmetry
# ─────────────────────────────────────────────────────────────────────────────

class TestAccessBarrierFraction:
    def test_out_of_pocket_correct(self):
        r = access_barrier_fraction(150_000, 62_000, 0.85)
        oop = 150_000 * 0.15
        assert abs(r["out_of_pocket_annual_usd"] - oop) < 1e-6

    def test_financially_toxic_high_cost(self):
        r = access_barrier_fraction(150_000, 62_000, 0.85)
        # OOP = 22,500; income_fraction = 22,500/62,000 ≈ 36.3% > 20%
        assert r["financially_toxic"] is True

    def test_not_toxic_low_cost(self):
        # OOP = 1,000; income fraction = 1,000/100,000 = 1% < 20%
        r = access_barrier_fraction(10_000, 100_000, 0.90)
        assert r["financially_toxic"] is False

    def test_income_fraction_correct(self):
        r = access_barrier_fraction(100_000, 50_000, 0.80)
        oop = 100_000 * 0.20
        expected = oop / 50_000
        assert abs(r["income_fraction"] - expected) < 1e-10

    def test_invalid_drug_cost(self):
        with pytest.raises(ValueError):
            access_barrier_fraction(0, 62_000)

    def test_invalid_income(self):
        with pytest.raises(ValueError):
            access_barrier_fraction(150_000, 0)

    def test_invalid_insurance_fraction(self):
        with pytest.raises(ValueError):
            access_barrier_fraction(150_000, 62_000, 1.0)


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 8: Metastasis Detection (CTC)
# ─────────────────────────────────────────────────────────────────────────────

class TestCtcDetectionSensitivity:
    def test_at_threshold_50_percent_detection(self):
        """At c = K (threshold), Hill equation gives P = 0.5."""
        r = ctc_detection_sensitivity(5.0, 5.0)
        assert abs(r["detection_probability"] - 0.5) < 1e-12

    def test_above_threshold_detected(self):
        r = ctc_detection_sensitivity(10.0, 5.0)
        assert r["above_clinical_threshold"] is True
        assert r["detection_probability"] > 0.5

    def test_below_threshold_not_detected(self):
        r = ctc_detection_sensitivity(2.0, 5.0)
        assert r["above_clinical_threshold"] is False
        assert r["detection_probability"] < 0.5

    def test_zero_ctc_zero_detection(self):
        r = ctc_detection_sensitivity(0.0, 5.0)
        assert abs(r["detection_probability"]) < 1e-12

    def test_hill_n_equals_nw(self):
        r = ctc_detection_sensitivity(5.0, 5.0)
        assert r["hill_n"] == N_W

    def test_detection_increases_with_ctc(self):
        r2 = ctc_detection_sensitivity(2.0, 5.0)
        r8 = ctc_detection_sensitivity(8.0, 5.0)
        assert r8["detection_probability"] > r2["detection_probability"]

    def test_invalid_negative_ctc(self):
        with pytest.raises(ValueError):
            ctc_detection_sensitivity(-1.0, 5.0)

    def test_invalid_threshold(self):
        with pytest.raises(ValueError):
            ctc_detection_sensitivity(5.0, 0.0)


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 9: Liquid Biopsy PPV/NPV
# ─────────────────────────────────────────────────────────────────────────────

class TestLiquidBiopsyPpvNpv:
    def test_ppv_bayes_correct(self):
        sens, spec, prev = 0.515, 0.995, 0.003
        r = liquid_biopsy_ppv_npv(sens, spec, prev)
        expected_ppv = (sens * prev) / (sens * prev + (1 - spec) * (1 - prev))
        assert abs(r["ppv"] - expected_ppv) < 1e-12

    def test_npv_bayes_correct(self):
        sens, spec, prev = 0.515, 0.995, 0.003
        r = liquid_biopsy_ppv_npv(sens, spec, prev)
        expected_npv = (spec * (1 - prev)) / (spec * (1 - prev) + (1 - sens) * prev)
        assert abs(r["npv"] - expected_npv) < 1e-12

    def test_ppv_low_at_low_prevalence(self):
        """Low prevalence → most positives are false alarms."""
        r = liquid_biopsy_ppv_npv(0.515, 0.995, 0.003)
        assert r["ppv"] < 0.5

    def test_ppv_higher_at_high_prevalence(self):
        r_low = liquid_biopsy_ppv_npv(0.515, 0.995, 0.003)
        r_high = liquid_biopsy_ppv_npv(0.515, 0.995, 0.10)
        assert r_high["ppv"] > r_low["ppv"]

    def test_npv_high_when_sensitivity_high(self):
        r = liquid_biopsy_ppv_npv(0.90, 0.995, 0.003)
        assert r["npv"] > 0.99

    def test_fpr_equals_one_minus_spec(self):
        r = liquid_biopsy_ppv_npv(0.80, 0.99, 0.01)
        assert abs(r["false_positive_rate"] - 0.01) < 1e-12

    def test_fnr_equals_one_minus_sens(self):
        r = liquid_biopsy_ppv_npv(0.80, 0.99, 0.01)
        assert abs(r["false_negative_rate"] - 0.20) < 1e-12

    def test_invalid_sensitivity(self):
        with pytest.raises(ValueError):
            liquid_biopsy_ppv_npv(0.0, 0.99, 0.01)

    def test_invalid_specificity(self):
        with pytest.raises(ValueError):
            liquid_biopsy_ppv_npv(0.80, 0.0, 0.01)

    def test_invalid_prevalence_zero(self):
        with pytest.raises(ValueError):
            liquid_biopsy_ppv_npv(0.80, 0.99, 0.0)

    def test_invalid_prevalence_one(self):
        with pytest.raises(ValueError):
            liquid_biopsy_ppv_npv(0.80, 0.99, 1.0)


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 10: Site Bandwidth
# ─────────────────────────────────────────────────────────────────────────────

class TestTrialSiteCapacity:
    def test_slots_per_chair_floor_division(self):
        r = trial_site_capacity(4, 8.0, 3.0)
        assert r["slots_per_chair_per_day"] == math.floor(8.0 / 3.0)

    def test_daily_capacity_correct(self):
        r = trial_site_capacity(4, 8.0, 3.0)
        assert r["daily_capacity"] == 4 * math.floor(8.0 / 3.0)

    def test_annual_capacity_correct(self):
        r = trial_site_capacity(4, 8.0, 3.0, 250)
        expected = 4 * math.floor(8.0 / 3.0) * 250
        assert r["annual_capacity"] == expected

    def test_doubled_capacity_correct(self):
        r = trial_site_capacity(4, 8.0, 3.0, 250)
        assert r["annual_capacity_if_doubled"] == 2 * r["annual_capacity"]

    def test_more_chairs_higher_capacity(self):
        r4 = trial_site_capacity(4, 8.0, 3.0)
        r8 = trial_site_capacity(8, 8.0, 3.0)
        assert r8["annual_capacity"] == 2 * r4["annual_capacity"]

    def test_invalid_chairs(self):
        with pytest.raises(ValueError):
            trial_site_capacity(0, 8.0, 3.0)

    def test_invalid_hours(self):
        with pytest.raises(ValueError):
            trial_site_capacity(4, 0.0, 3.0)

    def test_invalid_duration(self):
        with pytest.raises(ValueError):
            trial_site_capacity(4, 8.0, 0.0)

    def test_invalid_operating_days(self):
        with pytest.raises(ValueError):
            trial_site_capacity(4, 8.0, 3.0, 0)


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 11: Health Disparities
# ─────────────────────────────────────────────────────────────────────────────

class TestGeneticTestingEquityGap:
    def test_no_gap_equal_rates(self):
        r = genetic_testing_equity_gap(0.70, 0.70)
        assert abs(r["absolute_gap"]) < 1e-12
        assert abs(r["equity_ratio"] - 1.0) < 1e-12

    def test_absolute_gap_correct(self):
        r = genetic_testing_equity_gap(0.72, 0.38)
        assert abs(r["absolute_gap"] - 0.34) < 1e-12

    def test_equity_ratio_correct(self):
        r = genetic_testing_equity_gap(0.72, 0.38)
        expected = 0.72 / 0.38
        assert abs(r["equity_ratio"] - expected) < 1e-10

    def test_patients_missing_correct(self):
        r = genetic_testing_equity_gap(0.72, 0.38)
        assert abs(r["patients_missing_testing_per_1000"] - 340.0) < 1e-6

    def test_log2_gap_positive(self):
        r = genetic_testing_equity_gap(0.72, 0.38)
        assert r["log2_equity_gap_bits"] > 0

    def test_invalid_minority_zero(self):
        with pytest.raises(ValueError):
            genetic_testing_equity_gap(0.72, 0.0)

    def test_invalid_majority_rate(self):
        with pytest.raises(ValueError):
            genetic_testing_equity_gap(1.5, 0.38)


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 12: Survivorship Gap
# ─────────────────────────────────────────────────────────────────────────────

class TestSurvivorshipCareDeficit:
    def test_full_capacity_no_deficit(self):
        r = survivorship_care_deficit(1_000_000, 1.0)
        assert abs(r["unmet_care_contacts_annually"]) < 1e-6

    def test_half_capacity_half_unmet(self):
        r = survivorship_care_deficit(1_000_000, 0.5)
        needed = 1_000_000 * 2.3
        assert abs(r["unmet_care_contacts_annually"] - needed * 0.5) < 1e-6

    def test_deficit_fraction_correct(self):
        r = survivorship_care_deficit(1_000_000, 0.60)
        assert abs(r["deficit_fraction"] - 0.40) < 1e-12

    def test_care_contacts_needed(self):
        r = survivorship_care_deficit(18_000_000, 0.60)
        expected_needed = 18_000_000 * 2.3
        assert abs(r["care_contacts_needed_annually"] - expected_needed) < 1.0

    def test_delivered_plus_unmet_equals_needed(self):
        r = survivorship_care_deficit(5_000_000, 0.65)
        assert abs(
            r["care_contacts_delivered_annually"]
            + r["unmet_care_contacts_annually"]
            - r["care_contacts_needed_annually"]
        ) < 1e-6

    def test_invalid_survivors(self):
        with pytest.raises(ValueError):
            survivorship_care_deficit(0, 0.60)

    def test_invalid_capacity_fraction(self):
        with pytest.raises(ValueError):
            survivorship_care_deficit(1_000_000, 1.5)

    def test_invalid_unmet_needs_negative(self):
        with pytest.raises(ValueError):
            survivorship_care_deficit(1_000_000, 0.60, -1.0)


# ─────────────────────────────────────────────────────────────────────────────
# Summary report
# ─────────────────────────────────────────────────────────────────────────────

class TestBottleneckReport:
    def setup_method(self):
        self.report = bottleneck_report()

    def test_report_has_15_entries(self):
        """3 roadblocks + 12 bottlenecks = 15 entries."""
        assert len(self.report) == 15

    def test_all_entries_have_required_keys(self):
        required = {"index", "title", "result_summary", "status"}
        for entry in self.report:
            assert required.issubset(entry.keys()), (
                f"Entry {entry.get('index')} missing keys: "
                f"{required - set(entry.keys())}"
            )

    def test_roadblock_a_present(self):
        indices = [e["index"] for e in self.report]
        assert "Roadblock A" in indices

    def test_roadblock_b_present(self):
        indices = [e["index"] for e in self.report]
        assert "Roadblock B" in indices

    def test_roadblock_c_present(self):
        indices = [e["index"] for e in self.report]
        assert "Roadblock C" in indices

    def test_all_12_bottlenecks_present(self):
        indices = {e["index"] for e in self.report}
        for i in range(1, 13):
            assert f"Bottleneck {i}" in indices

    def test_result_summaries_nonempty(self):
        for entry in self.report:
            assert len(entry["result_summary"]) > 0

    def test_status_fields_nonempty(self):
        for entry in self.report:
            assert len(entry["status"]) > 0

    def test_custom_clone_fractions_accepted(self):
        r = bottleneck_report([0.5, 0.3, 0.2])
        assert len(r) == 15

    def test_enrollment_bottleneck_result_contains_enrolled(self):
        entry = next(e for e in self.report if e["index"] == "Bottleneck 1")
        assert "enrolled" in entry["result_summary"].lower()

    def test_liquid_biopsy_result_contains_ppv(self):
        entry = next(e for e in self.report if e["index"] == "Bottleneck 9")
        assert "PPV" in entry["result_summary"]

    def test_survivorship_gap_result_contains_unmet(self):
        entry = next(e for e in self.report if e["index"] == "Bottleneck 12")
        assert "unmet" in entry["result_summary"].lower()
