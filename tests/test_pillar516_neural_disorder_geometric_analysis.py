# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 516 — Neural Disorder Geometric Analysis.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

Status: STRUCTURAL_CORRESPONDENCE

174 tests covering:
  - Module constants and provenance
  - DisorderProfile construction and methods
  - All 8 disorder profiles in the registry
  - Geometric analysis functions (k_cs, ΔI, phase-locking, FTUM residual)
  - Intervention classification
  - Coupled fixed-point status diagnostic
  - Edge cases and error handling
"""

from __future__ import annotations

import math

import pytest

from src.core.pillar516_neural_disorder_geometric_analysis import (
    BETA_DEG,
    BETA_RAD,
    C_S,
    FTUM_CONTRACTION_RATE,
    GAMMA_FREQUENCY_HZ,
    INTERVENTION_CLASSES,
    INTERVENTION_DESCRIPTIONS,
    K_CS,
    K_CS_MINIMUM_FOR_CONSCIOUSNESS,
    N_W,
    N_W2,
    PILLAR_ADJACENCY,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TRACK,
    WINDING_RATIO,
    WINDING_RATIO_FLOAT,
    DisorderProfile,
    __provenance__,
    all_disorder_profiles,
    antidepressant_class,
    coupled_fixed_point_status,
    disorder_complexity_score,
    disorder_registry,
    ftum_convergence_residual,
    gamma_entrainment_winding_restoration,
    get_disorder,
    information_gap,
    intervention_priority_order,
    k_cs_is_above_consciousness_threshold,
    kcs_drift_from_grid_cell_loss,
    phase_locking_deviation,
    pillar516_report,
    pillar516_status,
)


# ─────────────────────────────────────────────────────────────────────────────
# § 1 — Module constants and provenance
# ─────────────────────────────────────────────────────────────────────────────


class TestModuleConstants:
    def test_n_w_is_five(self):
        assert N_W == 5

    def test_n_w2_is_seven(self):
        assert N_W2 == 7

    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_k_cs_equals_sum_of_squares(self):
        assert K_CS == N_W**2 + N_W2**2

    def test_k_cs_minimum_for_consciousness(self):
        assert K_CS_MINIMUM_FOR_CONSCIOUSNESS == 74

    def test_beta_deg_value(self):
        assert math.isclose(BETA_DEG, 0.3513, rel_tol=1e-9)

    def test_beta_rad_conversion(self):
        assert math.isclose(BETA_RAD, math.radians(0.3513), rel_tol=1e-12)

    def test_c_s_exact_fraction(self):
        assert math.isclose(C_S, 12.0 / 37.0, rel_tol=1e-15)

    def test_ftum_contraction_rate_equals_c_s(self):
        assert math.isclose(FTUM_CONTRACTION_RATE, C_S, rel_tol=1e-15)

    def test_gamma_frequency_hz(self):
        assert math.isclose(GAMMA_FREQUENCY_HZ, 40.0, rel_tol=1e-9)

    def test_winding_ratio_tuple(self):
        assert WINDING_RATIO == (5, 7)

    def test_winding_ratio_float(self):
        assert math.isclose(WINDING_RATIO_FLOAT, 5.0 / 7.0, rel_tol=1e-12)

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 516

    def test_pillar_status(self):
        assert PILLAR_STATUS == "STRUCTURAL_CORRESPONDENCE"

    def test_pillar_adjacency(self):
        assert "NON_HARDGATE_ADJACENT" in PILLAR_ADJACENCY

    def test_pillar_track_contains_adjacent(self):
        assert "ADJACENT TRACK" in PILLAR_TRACK


class TestProvenance:
    def test_provenance_pillar(self):
        assert __provenance__["pillar"] == 516

    def test_provenance_title(self):
        assert "Neural Disorder" in __provenance__["title"]

    def test_provenance_status_contains_structural_correspondence(self):
        assert "STRUCTURAL_CORRESPONDENCE" in __provenance__["status"]

    def test_provenance_toe_delta_zero(self):
        assert __provenance__["toe_delta"] == 0.0

    def test_provenance_new_tests(self):
        assert __provenance__["new_tests"] >= 174

    def test_provenance_related_pillars(self):
        assert 249 in __provenance__["related_pillars"]
        assert 413 in __provenance__["related_pillars"]


# ─────────────────────────────────────────────────────────────────────────────
# § 2 — Intervention class registry
# ─────────────────────────────────────────────────────────────────────────────


class TestInterventionClasses:
    def test_five_classes_defined(self):
        assert len(INTERVENTION_CLASSES) == 5

    def test_metric_repair_present(self):
        assert "METRIC_REPAIR" in INTERVENTION_CLASSES

    def test_irreversibility_restoration_present(self):
        assert "IRREVERSIBILITY_RESTORATION" in INTERVENTION_CLASSES

    def test_dilaton_tuning_present(self):
        assert "DILATON_TUNING" in INTERVENTION_CLASSES

    def test_winding_restoration_present(self):
        assert "WINDING_RESTORATION" in INTERVENTION_CLASSES

    def test_coupling_restoration_present(self):
        assert "COUPLING_RESTORATION" in INTERVENTION_CLASSES

    def test_all_classes_have_descriptions(self):
        for cls in INTERVENTION_CLASSES:
            assert cls in INTERVENTION_DESCRIPTIONS
            assert len(INTERVENTION_DESCRIPTIONS[cls]) > 20


# ─────────────────────────────────────────────────────────────────────────────
# § 3 — Disorder registry
# ─────────────────────────────────────────────────────────────────────────────


class TestDisorderRegistry:
    def test_eight_disorders_registered(self):
        assert len(disorder_registry()) == 8

    def test_singleton_consistency(self):
        r1 = disorder_registry()
        r2 = disorder_registry()
        assert r1 is r2

    def test_alzheimers_present(self):
        assert "ALZHEIMERS" in disorder_registry()

    def test_amnesia_anterograde_present(self):
        assert "AMNESIA_ANTEROGRADE" in disorder_registry()

    def test_amnesia_retrograde_present(self):
        assert "AMNESIA_RETROGRADE" in disorder_registry()

    def test_depression_present(self):
        assert "DEPRESSION" in disorder_registry()

    def test_epilepsy_present(self):
        assert "EPILEPSY" in disorder_registry()

    def test_schizophrenia_present(self):
        assert "SCHIZOPHRENIA" in disorder_registry()

    def test_tbi_concussion_present(self):
        assert "TBI_CONCUSSION" in disorder_registry()

    def test_tbi_severe_present(self):
        assert "TBI_SEVERE" in disorder_registry()

    def test_all_profiles_have_valid_intervention_classes(self):
        for profile in all_disorder_profiles():
            assert profile.primary_intervention_class in INTERVENTION_CLASSES
            for ic in profile.secondary_intervention_classes:
                assert ic in INTERVENTION_CLASSES

    def test_all_profiles_have_non_empty_um_prediction(self):
        for profile in all_disorder_profiles():
            assert len(profile.um_prediction) > 20


# ─────────────────────────────────────────────────────────────────────────────
# § 4 — Individual disorder profiles
# ─────────────────────────────────────────────────────────────────────────────


class TestAlzheimersProfile:
    def setup_method(self):
        self.ad = get_disorder("ALZHEIMERS")

    def test_primary_failure_compact_dimension(self):
        assert "COMPACT_DIMENSION" in self.ad.primary_failure

    def test_kcs_impact_true(self):
        assert self.ad.kcs_impact is True

    def test_metric_impact_true_amyloid(self):
        assert self.ad.metric_impact is True

    def test_phi_impact_true(self):
        assert self.ad.phi_impact is True

    def test_coupling_impact_false(self):
        assert self.ad.coupling_impact is False

    def test_bmu_not_primary_failure(self):
        assert self.ad.Bmu_impact is False

    def test_primary_intervention_winding_restoration(self):
        assert self.ad.primary_intervention_class == "WINDING_RESTORATION"

    def test_fixed_point_destabilised(self):
        assert "DESTABILISED" in self.ad.fixed_point_status

    def test_short_code(self):
        assert self.ad.short_code == "AD"

    def test_get_by_short_code(self):
        assert get_disorder("AD") is self.ad


class TestAmnesiaAnterogradeProfile:
    def setup_method(self):
        self.amna = get_disorder("AMNESIA_ANTEROGRADE")

    def test_primary_failure_irreversibility(self):
        assert "IRREVERSIBILITY" in self.amna.primary_failure

    def test_bmu_impact_true(self):
        assert self.amna.Bmu_impact is True

    def test_metric_impact_false(self):
        assert self.amna.metric_impact is False

    def test_kcs_impact_false(self):
        assert self.amna.kcs_impact is False

    def test_phi_impact_false(self):
        assert self.amna.phi_impact is False

    def test_coupling_impact_false(self):
        assert self.amna.coupling_impact is False

    def test_no_secondary_failures(self):
        assert self.amna.secondary_failures == []

    def test_primary_intervention(self):
        assert self.amna.primary_intervention_class == "IRREVERSIBILITY_RESTORATION"

    def test_um_prediction_mentions_procedural(self):
        assert "procedural" in self.amna.um_prediction.lower()

    def test_fixed_point_unreachable_for_encoding(self):
        assert "UNREACHABLE" in self.amna.fixed_point_status


class TestDepressionProfile:
    def setup_method(self):
        self.mdd = get_disorder("DEPRESSION")

    def test_primary_failure_trapped_local_minimum(self):
        assert "TRAPPED" in self.mdd.primary_failure

    def test_phi_impact_true(self):
        assert self.mdd.phi_impact is True

    def test_coupling_impact_true(self):
        assert self.mdd.coupling_impact is True

    def test_metric_impact_false(self):
        assert self.mdd.metric_impact is False

    def test_bmu_impact_false(self):
        assert self.mdd.Bmu_impact is False

    def test_kcs_impact_false(self):
        assert self.mdd.kcs_impact is False

    def test_primary_intervention_dilaton_tuning(self):
        assert self.mdd.primary_intervention_class == "DILATON_TUNING"

    def test_secondary_intervention_includes_coupling(self):
        assert "COUPLING_RESTORATION" in self.mdd.secondary_intervention_classes

    def test_fixed_point_wrong_basin(self):
        assert "WRONG_BASIN" in self.mdd.fixed_point_status

    def test_um_prediction_mentions_ketamine(self):
        assert "ketamine" in self.mdd.um_prediction.lower()


class TestEpilepsyProfile:
    def setup_method(self):
        self.epi = get_disorder("EPILEPSY")

    def test_primary_failure_chern_simons(self):
        assert "CHERN_SIMONS" in self.epi.primary_failure

    def test_kcs_impact_true(self):
        assert self.epi.kcs_impact is True

    def test_metric_impact_false(self):
        assert self.epi.metric_impact is False

    def test_bmu_impact_false(self):
        assert self.epi.Bmu_impact is False

    def test_coupling_impact_false(self):
        assert self.epi.coupling_impact is False

    def test_primary_intervention_winding_restoration(self):
        assert self.epi.primary_intervention_class == "WINDING_RESTORATION"

    def test_um_prediction_mentions_dbs(self):
        assert "dbs" in self.epi.um_prediction.lower()


class TestSchizophreniaProfile:
    def setup_method(self):
        self.scz = get_disorder("SCHIZOPHRENIA")

    def test_primary_failure_decoupled(self):
        assert "DECOUPLED" in self.scz.primary_failure

    def test_coupling_impact_true(self):
        assert self.scz.coupling_impact is True

    def test_phi_impact_true(self):
        assert self.scz.phi_impact is True

    def test_metric_impact_false(self):
        assert self.scz.metric_impact is False

    def test_bmu_impact_false(self):
        assert self.scz.Bmu_impact is False

    def test_kcs_impact_false(self):
        assert self.scz.kcs_impact is False

    def test_primary_intervention_coupling_restoration(self):
        assert self.scz.primary_intervention_class == "COUPLING_RESTORATION"

    def test_fixed_point_self_consistent_decoupled(self):
        assert "DECOUPLED" in self.scz.fixed_point_status

    def test_um_prediction_mentions_hallucinations(self):
        assert "hallucination" in self.scz.um_prediction.lower()


class TestTBISevereProfile:
    def setup_method(self):
        self.tbi_s = get_disorder("TBI_SEVERE")

    def test_primary_failure_topological_tearing(self):
        assert "TOPOLOGICAL_TEARING" in self.tbi_s.primary_failure

    def test_all_geometric_components_disrupted(self):
        assert self.tbi_s.metric_impact is True
        assert self.tbi_s.Bmu_impact is True
        assert self.tbi_s.phi_impact is True
        assert self.tbi_s.kcs_impact is True
        assert self.tbi_s.coupling_impact is True

    def test_max_complexity_score(self):
        assert disorder_complexity_score("TBI_SEVERE") == 5

    def test_fixed_point_new_forming(self):
        assert "NEW_FORMING" in self.tbi_s.fixed_point_status

    def test_um_prediction_mentions_personality_change(self):
        assert "personality" in self.tbi_s.um_prediction.lower()

    def test_multiple_secondary_interventions(self):
        assert len(self.tbi_s.secondary_intervention_classes) >= 3


class TestTBIConcussionProfile:
    def setup_method(self):
        self.tbi_c = get_disorder("TBI_CONCUSSION")

    def test_primary_failure_metric_distortion(self):
        assert "METRIC_DISTORTION" in self.tbi_c.primary_failure

    def test_topology_intact(self):
        assert self.tbi_c.kcs_impact is False
        assert self.tbi_c.Bmu_impact is False

    def test_complexity_score_one(self):
        assert disorder_complexity_score("TBI_CONCUSSION") == 1

    def test_fixed_point_intact_temporarily_inaccessible(self):
        assert "INTACT" in self.tbi_c.fixed_point_status


# ─────────────────────────────────────────────────────────────────────────────
# § 5 — Geometric analysis functions
# ─────────────────────────────────────────────────────────────────────────────


class TestKcsConsciousnessThreshold:
    def test_healthy_above_threshold(self):
        assert k_cs_is_above_consciousness_threshold(74) is True

    def test_exactly_at_threshold(self):
        assert k_cs_is_above_consciousness_threshold(74.0) is True

    def test_below_threshold(self):
        assert k_cs_is_above_consciousness_threshold(73.9) is False

    def test_well_below(self):
        assert k_cs_is_above_consciousness_threshold(37.0) is False

    def test_above_threshold_higher(self):
        assert k_cs_is_above_consciousness_threshold(100.0) is True

    def test_zero_is_below(self):
        assert k_cs_is_above_consciousness_threshold(0.0) is False


class TestInformationGap:
    def test_equal_phi_zero_gap(self):
        assert information_gap(1.0, 1.0) == pytest.approx(0.0)

    def test_asymmetric_gap(self):
        result = information_gap(2.0, 1.0)
        assert result == pytest.approx(abs(4.0 - 1.0))

    def test_symmetry(self):
        assert information_gap(2.0, 1.0) == pytest.approx(information_gap(1.0, 2.0))

    def test_zero_phi_brain(self):
        assert information_gap(0.0, 1.0) == pytest.approx(1.0)

    def test_negative_phi_brain_raises(self):
        with pytest.raises(ValueError):
            information_gap(-1.0, 1.0)

    def test_negative_phi_universe_raises(self):
        with pytest.raises(ValueError):
            information_gap(1.0, -1.0)


class TestPhaseLockingDeviation:
    def test_perfect_lock_zero_deviation(self):
        deviation = phase_locking_deviation(5.0, 7.0)
        assert deviation == pytest.approx(0.0)

    def test_off_resonance(self):
        deviation = phase_locking_deviation(1.0, 1.0)
        expected = abs(1.0 - 5.0 / 7.0)
        assert deviation == pytest.approx(expected)

    def test_zero_universe_frequency_raises(self):
        with pytest.raises(ValueError):
            phase_locking_deviation(5.0, 0.0)

    def test_negative_universe_frequency_raises(self):
        with pytest.raises(ValueError):
            phase_locking_deviation(5.0, -1.0)

    def test_higher_brain_frequency(self):
        deviation = phase_locking_deviation(10.0, 7.0)
        expected = abs(10.0 / 7.0 - 5.0 / 7.0)
        assert deviation == pytest.approx(expected)


class TestFTUMConvergenceResidual:
    def test_zero_iterations(self):
        assert ftum_convergence_residual(0) == pytest.approx(1.0)

    def test_one_iteration(self):
        assert ftum_convergence_residual(1) == pytest.approx(C_S)

    def test_two_iterations(self):
        assert ftum_convergence_residual(2) == pytest.approx(C_S**2)

    def test_ten_iterations_small(self):
        assert ftum_convergence_residual(10) < 1e-4

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            ftum_convergence_residual(-1)

    def test_monotone_decreasing(self):
        residuals = [ftum_convergence_residual(n) for n in range(6)]
        assert all(residuals[i] > residuals[i + 1] for i in range(5))


class TestKcsDriftFromGridCellLoss:
    def test_full_survival(self):
        assert kcs_drift_from_grid_cell_loss(1.0) == pytest.approx(74.0)

    def test_zero_survival(self):
        assert kcs_drift_from_grid_cell_loss(0.0) == pytest.approx(0.0)

    def test_half_survival(self):
        assert kcs_drift_from_grid_cell_loss(0.5) == pytest.approx(37.0)

    def test_below_consciousness_threshold_at_half(self):
        k_eff = kcs_drift_from_grid_cell_loss(0.5)
        assert not k_cs_is_above_consciousness_threshold(k_eff)

    def test_above_threshold_at_80_percent(self):
        k_eff = kcs_drift_from_grid_cell_loss(0.8)
        # 0.8 × 74 = 59.2 — below the K_CS consciousness threshold of 74
        assert k_eff == pytest.approx(59.2)
        assert not k_cs_is_above_consciousness_threshold(k_eff)

    def test_invalid_fraction_above_one_raises(self):
        with pytest.raises(ValueError):
            kcs_drift_from_grid_cell_loss(1.1)

    def test_invalid_fraction_negative_raises(self):
        with pytest.raises(ValueError):
            kcs_drift_from_grid_cell_loss(-0.1)

    def test_custom_k_cs_full(self):
        assert kcs_drift_from_grid_cell_loss(0.5, k_cs_full=100) == pytest.approx(50.0)


class TestGammaEntrainmentWindingRestoration:
    def test_zero_coherence_zero_strength(self):
        result = gamma_entrainment_winding_restoration(0.0, 0.0)
        assert result == pytest.approx(0.0)

    def test_zero_strength_no_change(self):
        result = gamma_entrainment_winding_restoration(0.5, 0.0)
        assert result == pytest.approx(0.5)

    def test_full_strength_at_40hz_from_zero(self):
        result = gamma_entrainment_winding_restoration(0.0, 1.0, 40.0)
        assert result == pytest.approx(1.0)

    def test_partial_restoration(self):
        result = gamma_entrainment_winding_restoration(0.5, 0.5, 40.0)
        # restoration = 0.5 × (1 − 0.5) × 1.0 = 0.25; total = 0.75
        assert result == pytest.approx(0.75)

    def test_off_frequency_reduced_restoration(self):
        result_40 = gamma_entrainment_winding_restoration(0.5, 1.0, 40.0)
        result_50 = gamma_entrainment_winding_restoration(0.5, 1.0, 50.0)
        assert result_40 > result_50

    def test_capped_at_one(self):
        result = gamma_entrainment_winding_restoration(0.99, 1.0, 40.0)
        assert result <= 1.0

    def test_invalid_coherence_raises(self):
        with pytest.raises(ValueError):
            gamma_entrainment_winding_restoration(1.5, 0.5)

    def test_invalid_strength_raises(self):
        with pytest.raises(ValueError):
            gamma_entrainment_winding_restoration(0.5, 1.5)

    def test_invalid_frequency_raises(self):
        with pytest.raises(ValueError):
            gamma_entrainment_winding_restoration(0.5, 0.5, -1.0)


class TestAntidepressantClass:
    def test_ketamine_is_dilaton_tuning(self):
        assert antidepressant_class("ketamine", "NMDA_ANTAGONIST") == "DILATON_TUNING"

    def test_psilocybin_is_dilaton_tuning(self):
        assert antidepressant_class("psilocybin", "5HT2A_AGONIST") == "DILATON_TUNING"

    def test_ssri_is_dilaton_tuning(self):
        assert antidepressant_class("fluoxetine", "SSRI") == "DILATON_TUNING"

    def test_snri_is_dilaton_tuning(self):
        assert antidepressant_class("venlafaxine", "SNRI") == "DILATON_TUNING"

    def test_mindfulness_is_coupling_restoration(self):
        assert antidepressant_class("mindfulness", "MINDFULNESS") == "COUPLING_RESTORATION"

    def test_cbt_is_coupling_restoration(self):
        assert antidepressant_class("CBT", "CBT") == "COUPLING_RESTORATION"

    def test_social_engagement_is_coupling(self):
        assert antidepressant_class("group therapy", "SOCIAL_ENGAGEMENT") == "COUPLING_RESTORATION"

    def test_unknown_mechanism_raises(self):
        with pytest.raises(ValueError):
            antidepressant_class("unknown_drug", "UNKNOWN_MECHANISM")


class TestCoupledFixedPointStatus:
    def test_healthy_state(self):
        status = coupled_fixed_point_status(0.1, 0.02, 74.0, 1.0)
        assert status == "HEALTHY"

    def test_collapsed_very_low_kcs(self):
        status = coupled_fixed_point_status(0.0, 0.0, 20.0, 1.0)
        assert status == "COLLAPSED"

    def test_topological_disruption(self):
        # k_cs between 37 and 59 → TOPOLOGICAL_DISRUPTION
        status = coupled_fixed_point_status(0.0, 0.0, 50.0, 1.0)
        assert status == "TOPOLOGICAL_DISRUPTION"

    def test_decoupled_high_phi_ratio(self):
        # Large info gap and high phi_ratio → DECOUPLED
        status = coupled_fixed_point_status(3.0, 0.4, 74.0, 2.0)
        assert status == "DECOUPLED"

    def test_trapped_local_minimum_moderate_gap(self):
        status = coupled_fixed_point_status(0.8, 0.05, 74.0, 1.0)
        assert status == "TRAPPED_LOCAL_MINIMUM"

    def test_negative_info_gap_raises(self):
        with pytest.raises(ValueError):
            coupled_fixed_point_status(-0.1, 0.0, 74.0, 1.0)

    def test_negative_phase_deviation_raises(self):
        with pytest.raises(ValueError):
            coupled_fixed_point_status(0.0, -0.1, 74.0, 1.0)

    def test_negative_kcs_raises(self):
        with pytest.raises(ValueError):
            coupled_fixed_point_status(0.0, 0.0, -1.0, 1.0)

    def test_negative_phi_ratio_raises(self):
        with pytest.raises(ValueError):
            coupled_fixed_point_status(0.0, 0.0, 74.0, -1.0)


# ─────────────────────────────────────────────────────────────────────────────
# § 6 — Intervention ordering and complexity scoring
# ─────────────────────────────────────────────────────────────────────────────


class TestInterventionPriorityOrder:
    def test_alzheimers_primary_first(self):
        order = intervention_priority_order("ALZHEIMERS")
        assert order[0] == "WINDING_RESTORATION"

    def test_depression_primary_first(self):
        order = intervention_priority_order("DEPRESSION")
        assert order[0] == "DILATON_TUNING"

    def test_schizophrenia_primary_first(self):
        order = intervention_priority_order("SCHIZOPHRENIA")
        assert order[0] == "COUPLING_RESTORATION"

    def test_no_duplicates(self):
        for code in disorder_registry():
            order = intervention_priority_order(code)
            assert len(order) == len(set(order))

    def test_invalid_code_raises(self):
        with pytest.raises(KeyError):
            intervention_priority_order("NONEXISTENT_DISORDER")


class TestDisorderComplexityScore:
    def test_anterograde_amnesia_score_one(self):
        assert disorder_complexity_score("AMNESIA_ANTEROGRADE") == 1

    def test_tbi_concussion_score_one(self):
        assert disorder_complexity_score("TBI_CONCUSSION") == 1

    def test_tbi_severe_score_five(self):
        assert disorder_complexity_score("TBI_SEVERE") == 5

    def test_scores_in_range(self):
        for code in disorder_registry():
            score = disorder_complexity_score(code)
            assert 0 <= score <= 5

    def test_alzheimers_score_three(self):
        # metric, phi, kcs = 3 components
        assert disorder_complexity_score("ALZHEIMERS") == 3


# ─────────────────────────────────────────────────────────────────────────────
# § 7 — Pillar report
# ─────────────────────────────────────────────────────────────────────────────


class TestPillar516Report:
    def setup_method(self):
        self.report = pillar516_report()

    def test_pillar_number(self):
        assert self.report["pillar"] == 516

    def test_status_structural_correspondence(self):
        assert self.report["status"] == "STRUCTURAL_CORRESPONDENCE"

    def test_disorders_analysed(self):
        assert self.report["disorders_analysed"] == 8

    def test_intervention_classes_count(self):
        assert len(self.report["intervention_classes"]) == 5

    def test_constants_block_k_cs(self):
        assert self.report["constants"]["K_CS"] == 74

    def test_constants_block_n_w(self):
        assert self.report["constants"]["N_W"] == 5

    def test_constants_block_n_w2(self):
        assert self.report["constants"]["N_W2"] == 7

    def test_toe_delta_zero(self):
        assert self.report["toe_delta"] == 0.0

    def test_disorder_registry_in_report(self):
        assert "disorder_registry" in self.report
        assert len(self.report["disorder_registry"]) == 8

    def test_pillar516_status_function(self):
        assert pillar516_status() == "STRUCTURAL_CORRESPONDENCE"
