# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 332 — Neutrino Mass Ordering."""
import math
import pytest

from src.core.pillar332_neutrino_mass_ordering import (
    N_W, K_CS, N_GENERATIONS,
    KK_MODE_NUMBERS,
    DM21_SQ_EV2, DM31_SQ_EV2,
    M_NU1_EV,
    UM_PREDICTED_ORDERING, UM_ORDERING_LABEL,
    separation_guard,
    kk_mode_mass_hierarchy,
    dm31_sign_from_kk_ordering,
    predict_mass_ordering,
    mass_spectrum_prediction,
    splitting_ratio_prediction,
    juno_falsifier,
    neutrino_ordering_full_report,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_generations(self):
        assert N_GENERATIONS == 3

    def test_kk_modes(self):
        assert KK_MODE_NUMBERS == (0, 1, 2)

    def test_dm21_positive(self):
        assert DM21_SQ_EV2 > 0

    def test_dm31_positive(self):
        # Positive for normal ordering
        assert DM31_SQ_EV2 > 0

    def test_dm31_much_larger_than_dm21(self):
        # Atmospheric >> solar splitting
        assert DM31_SQ_EV2 > 10 * DM21_SQ_EV2

    def test_m_nu1_positive(self):
        assert M_NU1_EV > 0

    def test_predicted_ordering_normal(self):
        assert UM_PREDICTED_ORDERING == "NORMAL"

    def test_ordering_label(self):
        assert "CONDITIONAL" in UM_ORDERING_LABEL or "DERIVED" in UM_ORDERING_LABEL


class TestSeparationGuard:
    def test_is_string(self):
        assert isinstance(separation_guard(), str)

    def test_mentions_pillar_42(self):
        guard = separation_guard()
        assert "42" in guard or "P11" in guard


class TestKKModeHierarchy:
    def test_returns_dict(self):
        result = kk_mode_mass_hierarchy()
        assert isinstance(result, dict)

    def test_mode_numbers(self):
        result = kk_mode_mass_hierarchy()
        assert result["gen1_kk_mode"] == 0
        assert result["gen2_kk_mode"] == 1
        assert result["gen3_kk_mode"] == 2

    def test_eigenvalue_ordering(self):
        result = kk_mode_mass_hierarchy()
        ev1 = result["eigenvalue_gen1"]
        ev2 = result["eigenvalue_gen2"]
        ev3 = result["eigenvalue_gen3"]
        assert ev1 < ev2 < ev3

    def test_eigenvalues_correct(self):
        result = kk_mode_mass_hierarchy()
        assert result["eigenvalue_gen1"] == 0
        assert result["eigenvalue_gen2"] == 1
        assert result["eigenvalue_gen3"] == 4

    def test_ordering_label(self):
        result = kk_mode_mass_hierarchy()
        assert result["ordering"] == "gen1 < gen2 < gen3"


class TestDm31Sign:
    def test_returns_dict(self):
        result = dm31_sign_from_kk_ordering()
        assert isinstance(result, dict)

    def test_sign_positive_for_normal(self):
        result = dm31_sign_from_kk_ordering()
        assert result["dm31_sq_sign"] == "POSITIVE"

    def test_ordering_is_normal(self):
        result = dm31_sign_from_kk_ordering()
        assert result["ordering"] == "NORMAL"

    def test_epistemic_label(self):
        result = dm31_sign_from_kk_ordering()
        assert "CONDITIONAL" in result["epistemic_label"] or "DERIVATION" in result["epistemic_label"]

    def test_inverted_ordering_for_reversed_modes(self):
        # If gen1 = n=2 and gen3 = n=0, we get inverted
        result = dm31_sign_from_kk_ordering(kk_modes=(2, 1, 0))
        assert result["ordering"] == "INVERTED"

    def test_derivation_string(self):
        result = dm31_sign_from_kk_ordering()
        assert "NORMAL" in result["derivation"]


class TestPredictMassOrdering:
    def test_returns_dict(self):
        result = predict_mass_ordering()
        assert isinstance(result, dict)

    def test_ordering_is_normal(self):
        result = predict_mass_ordering()
        assert result["predicted_ordering"] == "NORMAL"

    def test_dm31_sign_positive(self):
        result = predict_mass_ordering()
        assert result["dm31_sign"] == "POSITIVE"

    def test_has_falsification(self):
        result = predict_mass_ordering()
        assert "falsification" in result
        assert "JUNO" in result["falsification"]

    def test_consistent_with_current_data(self):
        result = predict_mass_ordering()
        assert result["um_prediction_consistent_with_current_data"] is True

    def test_has_kk_hierarchy(self):
        result = predict_mass_ordering()
        assert "kk_hierarchy" in result


class TestMassSpectrum:
    def test_returns_dict(self):
        result = mass_spectrum_prediction()
        assert isinstance(result, dict)

    def test_ordering_normal(self):
        result = mass_spectrum_prediction()
        assert result["ordering"] == "NORMAL"

    def test_m2_gt_m1(self):
        result = mass_spectrum_prediction()
        assert result["m2_ev"] > result["m1_ev"]

    def test_m3_gt_m1(self):
        result = mass_spectrum_prediction()
        assert result["m3_ev"] > result["m1_ev"]

    def test_m3_gt_m2(self):
        result = mass_spectrum_prediction()
        assert result["m3_ev"] > result["m2_ev"]

    def test_masses_from_splittings(self):
        result = mass_spectrum_prediction(m1_ev=0.05)
        expected_m2 = math.sqrt(0.05 ** 2 + DM21_SQ_EV2)
        assert abs(result["m2_ev"] - expected_m2) < 1e-10

    def test_sum_mnu(self):
        result = mass_spectrum_prediction()
        expected_sum = result["m1_ev"] + result["m2_ev"] + result["m3_ev"]
        assert abs(result["sum_mnu_ev"] - expected_sum) < 1e-10

    def test_raises_on_negative_dm31(self):
        with pytest.raises(ValueError):
            mass_spectrum_prediction(dm31_sq=-1e-3)


class TestSplittingRatio:
    def test_returns_dict(self):
        result = splitting_ratio_prediction()
        assert isinstance(result, dict)

    def test_observed_ratio_large(self):
        result = splitting_ratio_prediction()
        assert result["observed_ratio"] > 10

    def test_kk_pure_prediction_is_4(self):
        result = splitting_ratio_prediction()
        assert abs(result["kk_pure_prediction"] - 4.0) < 1e-10

    def test_residual_factor_large(self):
        result = splitting_ratio_prediction()
        assert result["residual_factor"] > 5

    def test_ordering_sign_robust(self):
        result = splitting_ratio_prediction()
        assert result["ordering_sign_robust"] is True

    def test_ratio_not_closed(self):
        result = splitting_ratio_prediction()
        assert result["ratio_magnitude_closed"] is False

    def test_gap_label(self):
        result = splitting_ratio_prediction()
        assert "GAP" in result["gap_label"]


class TestJunoFalsifier:
    def test_returns_dict(self):
        result = juno_falsifier()
        assert isinstance(result, dict)

    def test_experiment_is_juno(self):
        result = juno_falsifier()
        assert "JUNO" in result["experiment"]

    def test_um_prediction_normal(self):
        result = juno_falsifier()
        assert "NORMAL" in result["um_prediction"]

    def test_has_falsification_condition(self):
        result = juno_falsifier()
        assert "falsification_condition" in result
        assert "INVERTED" in result["falsification_condition"]

    def test_has_expected_dr1(self):
        result = juno_falsifier()
        assert "expected_dr1" in result
        assert "2027" in result["expected_dr1"]

    def test_preregistration_status(self):
        result = juno_falsifier()
        assert "PREREGISTERED" in result["preregistration_status"]

    def test_current_status_mentions_sigma(self):
        result = juno_falsifier()
        assert "σ" in result["current_status"] or "sigma" in result["current_status"].lower()


class TestFullReport:
    def test_returns_dict(self):
        r = neutrino_ordering_full_report()
        assert isinstance(r, dict)

    def test_pillar_number(self):
        r = neutrino_ordering_full_report()
        assert r["pillar"] == 332

    def test_prediction_normal(self):
        r = neutrino_ordering_full_report()
        assert r["prediction"]["ordering"] == "NORMAL"

    def test_has_derivation(self):
        r = neutrino_ordering_full_report()
        assert "derivation" in r
        assert r["derivation"]["kk_modes"] == [0, 1, 2]

    def test_has_mass_spectrum(self):
        r = neutrino_ordering_full_report()
        assert "mass_spectrum" in r

    def test_has_juno_falsifier(self):
        r = neutrino_ordering_full_report()
        assert "juno_falsifier" in r

    def test_has_epistemic_status(self):
        r = neutrino_ordering_full_report()
        assert "epistemic_status" in r

    def test_consistent_with_current_data(self):
        r = neutrino_ordering_full_report()
        assert r["current_consistency"]["consistent_with_current_data"] is True
