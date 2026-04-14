# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_medicine.py
=======================
Unit tests for the src/medicine package — Pillar 17: Health & Medicine.

Covers:
  - diagnosis.py  : diagnostic_snr, disease_phi_deviation, detection_threshold,
                    phi_screening_coverage, diagnostic_uncertainty,
                    information_current_loss, federated_phi_estimate,
                    bias_correction_factor, early_detection_benefit,
                    diagnostic_desert_index
  - treatment.py  : treatment_efficacy, drug_dose_response, resistance_probability,
                    combination_therapy_synergy, polypharmacy_interference,
                    dosing_error, access_barrier_factor, precision_medicine_gain,
                    clinical_trial_efficiency, cure_criterion
  - systemic.py   : system_entropy, administrative_overhead_fraction,
                    preventive_roi, inequality_phi_gradient,
                    clinician_burnout_risk, information_current_efficiency,
                    universal_coverage_phi, prevention_investment_optimal,
                    avoidable_mortality_index, health_equity_index
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pytest

from src.medicine.diagnosis import (
    diagnostic_snr,
    disease_phi_deviation,
    detection_threshold,
    phi_screening_coverage,
    diagnostic_uncertainty,
    information_current_loss,
    federated_phi_estimate,
    bias_correction_factor,
    early_detection_benefit,
    diagnostic_desert_index,
)
from src.medicine.treatment import (
    treatment_efficacy,
    drug_dose_response,
    resistance_probability,
    combination_therapy_synergy,
    polypharmacy_interference,
    dosing_error,
    access_barrier_factor,
    precision_medicine_gain,
    clinical_trial_efficiency,
    cure_criterion,
)
from src.medicine.systemic import (
    system_entropy,
    administrative_overhead_fraction,
    preventive_roi,
    inequality_phi_gradient,
    clinician_burnout_risk,
    information_current_efficiency,
    universal_coverage_phi,
    prevention_investment_optimal,
    avoidable_mortality_index,
    health_equity_index,
)


# ===========================================================================
# TestDiagnosis
# ===========================================================================

class TestDiagnosis:
    # ---- diagnostic_snr ----

    def test_snr_positive_delta(self):
        assert diagnostic_snr(2.0, 1.0) == pytest.approx(2.0 / (1.0 + 1e-30))

    def test_snr_negative_delta_uses_abs(self):
        assert diagnostic_snr(-3.0, 1.0) == pytest.approx(diagnostic_snr(3.0, 1.0))

    def test_snr_zero_noise_large(self):
        snr = diagnostic_snr(5.0, 0.0)
        assert snr > 1e25

    def test_snr_monotone_with_delta(self):
        snr1 = diagnostic_snr(1.0, 1.0)
        snr2 = diagnostic_snr(2.0, 1.0)
        assert snr2 > snr1

    def test_snr_negative_noise_raises(self):
        with pytest.raises(ValueError):
            diagnostic_snr(1.0, -0.1)

    # ---- disease_phi_deviation ----

    def test_deviation_positive_hyperactive(self):
        assert disease_phi_deviation(1.5, 1.0) == pytest.approx(0.5)

    def test_deviation_negative_depleted(self):
        assert disease_phi_deviation(0.8, 1.0) == pytest.approx(-0.2)

    def test_deviation_zero_healthy(self):
        assert disease_phi_deviation(1.0, 1.0) == pytest.approx(0.0)

    # ---- detection_threshold ----

    def test_threshold_scales_with_noise(self):
        assert detection_threshold(2.0, 3.0) == pytest.approx(6.0)

    def test_threshold_zero_noise_gives_zero(self):
        assert detection_threshold(0.0, 2.0) == pytest.approx(0.0)

    def test_threshold_bad_noise_raises(self):
        with pytest.raises(ValueError):
            detection_threshold(-1.0, 2.0)

    def test_threshold_bad_sensitivity_raises(self):
        with pytest.raises(ValueError):
            detection_threshold(1.0, 0.0)

    # ---- phi_screening_coverage ----

    def test_coverage_full(self):
        assert phi_screening_coverage(1000, 1000) == pytest.approx(1.0)

    def test_coverage_zero_screened(self):
        assert phi_screening_coverage(0, 1000) == pytest.approx(0.0)

    def test_coverage_clipped_above_one(self):
        assert phi_screening_coverage(2000, 1000) == pytest.approx(1.0)

    def test_coverage_bad_population_raises(self):
        with pytest.raises(ValueError):
            phi_screening_coverage(10, 0)

    def test_coverage_negative_screened_raises(self):
        with pytest.raises(ValueError):
            phi_screening_coverage(-1, 100)

    # ---- diagnostic_uncertainty ----

    def test_uncertainty_single_sample(self):
        assert diagnostic_uncertainty(4.0, 1) == pytest.approx(4.0)

    def test_uncertainty_decreases_with_samples(self):
        s1 = diagnostic_uncertainty(1.0, 4)
        s2 = diagnostic_uncertainty(1.0, 16)
        assert s2 < s1

    def test_uncertainty_formula(self):
        assert diagnostic_uncertainty(9.0, 9) == pytest.approx(3.0)

    def test_uncertainty_bad_noise_raises(self):
        with pytest.raises(ValueError):
            diagnostic_uncertainty(-1.0, 5)

    def test_uncertainty_bad_n_raises(self):
        with pytest.raises(ValueError):
            diagnostic_uncertainty(1.0, 0)

    # ---- information_current_loss ----

    def test_loss_full_silo(self):
        assert information_current_loss(10.0, 1.0) == pytest.approx(10.0)

    def test_loss_no_silo(self):
        assert information_current_loss(10.0, 0.0) == pytest.approx(0.0)

    def test_loss_partial(self):
        assert information_current_loss(8.0, 0.5) == pytest.approx(4.0)

    def test_loss_bad_fraction_raises(self):
        with pytest.raises(ValueError):
            information_current_loss(10.0, 1.1)

    def test_loss_negative_J_raises(self):
        with pytest.raises(ValueError):
            information_current_loss(-1.0, 0.5)

    # ---- federated_phi_estimate ----

    def test_federated_uniform_mean(self):
        estimates = np.array([1.0, 2.0, 3.0])
        assert federated_phi_estimate(estimates) == pytest.approx(2.0, rel=1e-6)

    def test_federated_weighted(self):
        estimates = np.array([1.0, 3.0])
        weights = np.array([3.0, 1.0])
        result = federated_phi_estimate(estimates, weights)
        assert result == pytest.approx(1.5, rel=1e-6)

    def test_federated_single_node(self):
        assert federated_phi_estimate(np.array([5.0])) == pytest.approx(5.0, rel=1e-6)

    def test_federated_empty_raises(self):
        with pytest.raises(ValueError):
            federated_phi_estimate(np.array([]))

    def test_federated_negative_weight_raises(self):
        with pytest.raises(ValueError):
            federated_phi_estimate(np.array([1.0, 2.0]), np.array([-1.0, 1.0]))

    # ---- bias_correction_factor ----

    def test_bias_no_bias(self):
        assert bias_correction_factor(1.0, 1.0) == pytest.approx(1.0)

    def test_bias_under_represented(self):
        assert bias_correction_factor(0.8, 1.0) == pytest.approx(1.25)

    def test_bias_over_represented(self):
        assert bias_correction_factor(1.2, 1.0) == pytest.approx(1.0 / 1.2)

    def test_bias_zero_population_ref_raises(self):
        with pytest.raises(ValueError):
            bias_correction_factor(0.0, 1.0)

    def test_bias_zero_true_ref_raises(self):
        with pytest.raises(ValueError):
            bias_correction_factor(1.0, 0.0)

    # ---- early_detection_benefit ----

    def test_early_detection_positive_benefit(self):
        benefit = early_detection_benefit(0.5, 2.0, lam=1.0)
        assert benefit == pytest.approx(2.0**2 - 0.5**2)

    def test_early_detection_scales_with_lam(self):
        b1 = early_detection_benefit(0.5, 2.0, lam=1.0)
        b2 = early_detection_benefit(0.5, 2.0, lam=2.0)
        assert b2 == pytest.approx(2.0 * b1)

    def test_early_detection_same_deviation_zero(self):
        assert early_detection_benefit(1.0, 1.0) == pytest.approx(0.0)

    # ---- diagnostic_desert_index ----

    def test_ddi_no_providers(self):
        ddi = diagnostic_desert_index(0, 100.0)
        assert ddi == pytest.approx(100.0 / 1e-30)

    def test_ddi_decreases_with_providers(self):
        ddi1 = diagnostic_desert_index(1, 100.0)
        ddi2 = diagnostic_desert_index(10, 100.0)
        assert ddi2 < ddi1

    def test_ddi_negative_providers_raises(self):
        with pytest.raises(ValueError):
            diagnostic_desert_index(-1, 100.0)

    def test_ddi_zero_area_raises(self):
        with pytest.raises(ValueError):
            diagnostic_desert_index(5, 0.0)


# ===========================================================================
# TestTreatment
# ===========================================================================

class TestTreatment:
    # ---- treatment_efficacy ----

    def test_efficacy_complete_cure(self):
        assert treatment_efficacy(1.0, 1.0, 0.0) == pytest.approx(1.0)

    def test_efficacy_no_effect(self):
        assert treatment_efficacy(0.0, 1.0, 0.0) == pytest.approx(0.0)

    def test_efficacy_partial(self):
        # phi_pre=0, phi_target=2, phi_post=1 → (0-1)/(0-2)=0.5
        assert treatment_efficacy(1.0, 2.0, 0.0) == pytest.approx(0.5)

    def test_efficacy_overshoot_clipped_to_one(self):
        # phi_pre=0, phi_target=2, phi_post=3 → overshoots → clipped to 1
        assert treatment_efficacy(3.0, 2.0, 0.0) == pytest.approx(1.0)

    def test_efficacy_equal_pre_target_raises(self):
        with pytest.raises(ValueError):
            treatment_efficacy(1.0, 1.0, 1.0)

    # ---- drug_dose_response ----

    def test_dose_zero_gives_zero(self):
        assert drug_dose_response(0.0, 10.0, 1.0) == pytest.approx(0.0)

    def test_dose_ec50_gives_half_max(self):
        assert drug_dose_response(1.0, 10.0, 1.0) == pytest.approx(5.0)

    def test_dose_large_approaches_max(self):
        r = drug_dose_response(1e9, 10.0, 1.0)
        assert r == pytest.approx(10.0, rel=1e-6)

    def test_dose_monotone_with_dose(self):
        r1 = drug_dose_response(1.0, 10.0, 1.0)
        r2 = drug_dose_response(2.0, 10.0, 1.0)
        assert r2 > r1

    def test_dose_negative_dose_raises(self):
        with pytest.raises(ValueError):
            drug_dose_response(-1.0, 10.0, 1.0)

    def test_dose_zero_phi_max_raises(self):
        with pytest.raises(ValueError):
            drug_dose_response(1.0, 0.0, 1.0)

    def test_dose_zero_ec50_raises(self):
        with pytest.raises(ValueError):
            drug_dose_response(1.0, 10.0, 0.0)

    # ---- resistance_probability ----

    def test_resistance_zero_cycles(self):
        assert resistance_probability(0.0, 0, base_prob=0.01) == pytest.approx(
            1.0 - np.exp(0.0)
        )

    def test_resistance_increases_with_cycles(self):
        p1 = resistance_probability(0.0, 1)
        p2 = resistance_probability(0.0, 10)
        assert p2 > p1

    def test_resistance_high_B_suppresses(self):
        p_low_B = resistance_probability(0.1, 5)
        p_high_B = resistance_probability(10.0, 5)
        assert p_high_B < p_low_B

    def test_resistance_bounded_01(self):
        p = resistance_probability(0.0, 100, base_prob=0.5)
        assert 0.0 <= p <= 1.0

    def test_resistance_negative_B_raises(self):
        with pytest.raises(ValueError):
            resistance_probability(-1.0, 5)

    def test_resistance_bad_base_prob_raises(self):
        with pytest.raises(ValueError):
            resistance_probability(0.0, 5, base_prob=1.5)

    # ---- combination_therapy_synergy ----

    def test_synergy_bliss_independence(self):
        # rho=1: 0.5 + 0.5 - 0.5*0.5 = 0.75
        assert combination_therapy_synergy(0.5, 0.5, rho=1.0) == pytest.approx(0.75)

    def test_synergy_rho_less_one_exceeds_bliss(self):
        bliss = combination_therapy_synergy(0.5, 0.5, rho=1.0)
        synerg = combination_therapy_synergy(0.5, 0.5, rho=0.5)
        assert synerg > bliss

    def test_synergy_zero_both_gives_zero(self):
        assert combination_therapy_synergy(0.0, 0.0) == pytest.approx(0.0)

    def test_synergy_clipped_to_one(self):
        assert combination_therapy_synergy(1.0, 1.0, rho=0.0) == pytest.approx(1.0)

    def test_synergy_bad_efficacy_a_raises(self):
        with pytest.raises(ValueError):
            combination_therapy_synergy(-0.1, 0.5)

    def test_synergy_bad_efficacy_b_raises(self):
        with pytest.raises(ValueError):
            combination_therapy_synergy(0.5, 1.5)

    # ---- polypharmacy_interference ----

    def test_interference_single_drug(self):
        assert polypharmacy_interference(np.array([3.0])) == pytest.approx(3.0)

    def test_interference_two_equal_drugs(self):
        result = polypharmacy_interference(np.array([3.0, 4.0]))
        assert result == pytest.approx(5.0)

    def test_interference_negative_raises(self):
        with pytest.raises(ValueError):
            polypharmacy_interference(np.array([1.0, -1.0]))

    def test_interference_less_than_sum(self):
        B = np.array([1.0, 1.0, 1.0])
        assert polypharmacy_interference(B) < np.sum(B)

    # ---- dosing_error ----

    def test_dosing_error_exact_hit(self):
        assert dosing_error(2.0, 2.0) == pytest.approx(0.0)

    def test_dosing_error_underdose(self):
        assert dosing_error(1.5, 2.0) == pytest.approx(0.25)

    def test_dosing_error_overdose(self):
        assert dosing_error(3.0, 2.0) == pytest.approx(0.5)

    def test_dosing_error_zero_target_raises(self):
        with pytest.raises(ValueError):
            dosing_error(1.0, 0.0)

    # ---- access_barrier_factor ----

    def test_barrier_zero_distance(self):
        assert access_barrier_factor(0.0, 0.5) == pytest.approx(0.0)

    def test_barrier_increases_with_distance(self):
        b1 = access_barrier_factor(10.0, 0.5)
        b2 = access_barrier_factor(100.0, 0.5)
        assert b2 > b1

    def test_barrier_full_income_gives_zero(self):
        assert access_barrier_factor(100.0, 1.0) == pytest.approx(0.0, abs=1e-10)

    def test_barrier_clipped_below_one(self):
        b = access_barrier_factor(1e6, 0.0)
        assert b < 1.0

    def test_barrier_negative_distance_raises(self):
        with pytest.raises(ValueError):
            access_barrier_factor(-1.0, 0.5)

    # ---- precision_medicine_gain ----

    def test_precision_zero_individual_std(self):
        gain = precision_medicine_gain(2.0, 0.0)
        assert gain == pytest.approx(1.0, rel=1e-6)

    def test_precision_equal_stds_zero_gain(self):
        assert precision_medicine_gain(1.0, 1.0) == pytest.approx(0.0, abs=1e-10)

    def test_precision_clipped_below_one(self):
        gain = precision_medicine_gain(1.0, 0.01)
        assert gain < 1.0

    def test_precision_zero_population_std_raises(self):
        with pytest.raises(ValueError):
            precision_medicine_gain(0.0, 0.5)

    def test_precision_negative_individual_std_raises(self):
        with pytest.raises(ValueError):
            precision_medicine_gain(1.0, -0.1)

    # ---- clinical_trial_efficiency ----

    def test_trial_efficiency_scales_with_arms(self):
        eta1 = clinical_trial_efficiency(1, 1.0, 0.0)
        eta2 = clinical_trial_efficiency(4, 1.0, 0.0)
        assert eta2 == pytest.approx(4.0 * eta1, rel=1e-6)

    def test_trial_efficiency_bad_arms_raises(self):
        with pytest.raises(ValueError):
            clinical_trial_efficiency(0, 1.0, 0.0)

    def test_trial_efficiency_bad_width_raises(self):
        with pytest.raises(ValueError):
            clinical_trial_efficiency(2, 0.0, 1.0)

    def test_trial_efficiency_bad_sigma_raises(self):
        with pytest.raises(ValueError):
            clinical_trial_efficiency(2, 1.0, -1.0)

    # ---- cure_criterion ----

    def test_cure_within_tolerance(self):
        assert cure_criterion(1.05, 1.0, tolerance=0.1) is True

    def test_cure_outside_tolerance(self):
        assert cure_criterion(1.2, 1.0, tolerance=0.1) is False

    def test_cure_exact_match(self):
        assert cure_criterion(1.0, 1.0, tolerance=0.01) is True

    def test_cure_zero_tolerance_raises(self):
        with pytest.raises(ValueError):
            cure_criterion(1.0, 1.0, tolerance=0.0)


# ===========================================================================
# TestSystemic
# ===========================================================================

class TestSystemic:
    # ---- system_entropy ----

    def test_entropy_additive(self):
        assert system_entropy(0.3, 0.4) == pytest.approx(0.7)

    def test_entropy_zero_both(self):
        assert system_entropy(0.0, 0.0) == pytest.approx(0.0)

    def test_entropy_negative_fragmentation_raises(self):
        with pytest.raises(ValueError):
            system_entropy(-0.1, 0.3)

    def test_entropy_bad_gini_raises(self):
        with pytest.raises(ValueError):
            system_entropy(0.3, 1.5)

    # ---- administrative_overhead_fraction ----

    def test_overhead_half(self):
        assert administrative_overhead_fraction(50.0, 100.0) == pytest.approx(
            0.5, rel=1e-6
        )

    def test_overhead_zero_admin(self):
        assert administrative_overhead_fraction(0.0, 100.0) == pytest.approx(0.0)

    def test_overhead_clipped_below_one(self):
        frac = administrative_overhead_fraction(100.0, 100.0)
        assert frac < 1.0

    def test_overhead_negative_admin_raises(self):
        with pytest.raises(ValueError):
            administrative_overhead_fraction(-10.0, 100.0)

    def test_overhead_negative_total_raises(self):
        with pytest.raises(ValueError):
            administrative_overhead_fraction(10.0, -100.0)

    # ---- preventive_roi ----

    def test_roi_scales_with_lambda(self):
        r1 = preventive_roi(1.0, 1.0, 10.0)
        r2 = preventive_roi(1.0, 2.0, 10.0)
        assert r2 == pytest.approx(2.0 * r1)

    def test_roi_zero_investment(self):
        assert preventive_roi(0.0, 2.0, 5.0) == pytest.approx(0.0)

    def test_roi_bad_investment_raises(self):
        with pytest.raises(ValueError):
            preventive_roi(-1.0, 1.0, 10.0)

    def test_roi_bad_horizon_raises(self):
        with pytest.raises(ValueError):
            preventive_roi(1.0, 1.0, 0.0)

    # ---- inequality_phi_gradient ----

    def test_gradient_zero_inequality(self):
        assert inequality_phi_gradient(2.0, 2.0) == pytest.approx(0.0, abs=1e-6)

    def test_gradient_extreme_inequality(self):
        g = inequality_phi_gradient(100.0, 0.01)
        assert g > 0.9

    def test_gradient_clipped_below_one(self):
        g = inequality_phi_gradient(1e6, 1e-6)
        assert g < 1.0

    def test_gradient_phi_rich_less_than_poor_raises(self):
        with pytest.raises(ValueError):
            inequality_phi_gradient(0.5, 1.0)

    def test_gradient_negative_phi_raises(self):
        with pytest.raises(ValueError):
            inequality_phi_gradient(-1.0, -2.0)

    # ---- clinician_burnout_risk ----

    def test_burnout_zero_admin_fraction(self):
        assert clinician_burnout_risk(60.0, 0.0, 1.0) == pytest.approx(0.0)

    def test_burnout_high_hours_high_risk(self):
        r1 = clinician_burnout_risk(40.0, 0.5, 1.0)
        r2 = clinician_burnout_risk(80.0, 0.5, 1.0)
        assert r2 > r1

    def test_burnout_clipped_below_one(self):
        r = clinician_burnout_risk(1000.0, 1.0, 1e-10)
        assert r < 1.0

    def test_burnout_bad_hours_raises(self):
        with pytest.raises(ValueError):
            clinician_burnout_risk(-10.0, 0.5, 1.0)

    def test_burnout_bad_admin_fraction_raises(self):
        with pytest.raises(ValueError):
            clinician_burnout_risk(40.0, 1.5, 1.0)

    # ---- information_current_efficiency ----

    def test_current_efficiency_perfect(self):
        assert information_current_efficiency(0.0, 1.0) == pytest.approx(1.0)

    def test_current_efficiency_all_denied(self):
        assert information_current_efficiency(1.0, 1.0) == pytest.approx(0.0)

    def test_current_efficiency_partial(self):
        eta = information_current_efficiency(0.2, 0.8)
        assert eta == pytest.approx(0.64)

    def test_current_efficiency_bad_denied_raises(self):
        with pytest.raises(ValueError):
            information_current_efficiency(1.5, 0.8)

    def test_current_efficiency_bad_interop_raises(self):
        with pytest.raises(ValueError):
            information_current_efficiency(0.1, -0.1)

    # ---- universal_coverage_phi ----

    def test_coverage_full_insured(self):
        assert universal_coverage_phi(2.0, 1.0, 1.0) == pytest.approx(2.0)

    def test_coverage_none_insured(self):
        assert universal_coverage_phi(2.0, 1.0, 0.0) == pytest.approx(1.0)

    def test_coverage_interpolation(self):
        assert universal_coverage_phi(2.0, 0.0, 0.5) == pytest.approx(1.0)

    def test_coverage_bad_fraction_raises(self):
        with pytest.raises(ValueError):
            universal_coverage_phi(2.0, 1.0, 1.5)

    # ---- prevention_investment_optimal ----

    def test_optimal_investment_formula(self):
        phi_opt = prevention_investment_optimal(2.0, 0.1)
        assert phi_opt == pytest.approx(2.0 / 0.1)

    def test_optimal_investment_zero_discount(self):
        phi_opt = prevention_investment_optimal(1.0, 0.0)
        assert phi_opt > 1e25

    def test_optimal_investment_bad_lambda_raises(self):
        with pytest.raises(ValueError):
            prevention_investment_optimal(-1.0, 0.1)

    def test_optimal_investment_bad_discount_raises(self):
        with pytest.raises(ValueError):
            prevention_investment_optimal(1.0, -0.1)

    # ---- avoidable_mortality_index ----

    def test_ami_no_gap(self):
        assert avoidable_mortality_index(1.0, 1.0, 1000) == pytest.approx(0.0, abs=1e-6)

    def test_ami_large_gap_large_ami(self):
        ami = avoidable_mortality_index(0.5, 1.0, 1000)
        assert ami > 0.0

    def test_ami_scales_with_population(self):
        ami1 = avoidable_mortality_index(0.5, 1.0, 1000)
        ami2 = avoidable_mortality_index(0.5, 1.0, 2000)
        assert ami2 == pytest.approx(2.0 * ami1, rel=1e-6)

    def test_ami_bad_phi_actual_raises(self):
        with pytest.raises(ValueError):
            avoidable_mortality_index(-1.0, 1.0, 1000)

    def test_ami_bad_phi_optimal_raises(self):
        with pytest.raises(ValueError):
            avoidable_mortality_index(0.5, 0.0, 1000)

    # ---- health_equity_index ----

    def test_hei_perfect_equity(self):
        phi = np.array([2.0, 2.0, 2.0])
        assert health_equity_index(phi) == pytest.approx(1.0, abs=1e-6)

    def test_hei_dispersion_reduces_index(self):
        phi_eq = np.array([2.0, 2.0, 2.0])
        phi_ineq = np.array([1.0, 2.0, 3.0])
        assert health_equity_index(phi_ineq) < health_equity_index(phi_eq)

    def test_hei_empty_raises(self):
        with pytest.raises(ValueError):
            health_equity_index(np.array([]))

    def test_hei_two_groups(self):
        phi = np.array([1.0, 3.0])
        hei = health_equity_index(phi)
        assert hei < 1.0
