# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 334 — JUNO 2027 Full Prediction Package."""
import math
import json
import pytest

from src.core.pillar334_juno_prediction_package import (
    N_W, K_CS, PI_KR,
    THETA_12_DEG, THETA_13_DEG, THETA_23_DEG, DELTA_CP_RAD,
    THETA_12, THETA_13, THETA_23,
    DM21_SQ_EV2, DM31_SQ_EV2, DM32_SQ_EV2,
    JUNO_BASELINE_KM,
    JUNO_ENERGY_MIN_MEV, JUNO_ENERGY_MAX_MEV,
    V_CC_EV,
    PDG_DM21_SQ, PDG_DM31_SQ,
    separation_guard,
    oscillation_argument,
    survival_probability_vacuum,
    survival_probability_with_matter,
    matter_correction_fraction,
    oscillation_minimum_energy,
    juno_spectrum_sample,
    juno_precision_budget,
    route_juno_dr1,
    juno_prediction_manifest,
    juno_prediction_manifest_json,
    juno_full_report,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert abs(PI_KR - 37.0) < 1e-9

    def test_theta_12_physical(self):
        assert 30 < THETA_12_DEG < 40

    def test_theta_13_physical(self):
        assert 7 < THETA_13_DEG < 10

    def test_theta_23_physical(self):
        assert 40 < THETA_23_DEG < 55

    def test_delta_cp_range(self):
        assert 0 < DELTA_CP_RAD < math.pi

    def test_dm21_positive(self):
        assert DM21_SQ_EV2 > 0

    def test_dm31_positive_normal_ordering(self):
        assert DM31_SQ_EV2 > 0

    def test_dm32_derived(self):
        assert abs(DM32_SQ_EV2 - (DM31_SQ_EV2 - DM21_SQ_EV2)) < 1e-12

    def test_juno_baseline(self):
        assert abs(JUNO_BASELINE_KM - 52.5) < 0.1

    def test_juno_energy_range(self):
        assert JUNO_ENERGY_MIN_MEV < JUNO_ENERGY_MAX_MEV
        assert JUNO_ENERGY_MIN_MEV > 0

    def test_v_cc_tiny(self):
        # Matter potential at JUNO is extremely small
        assert V_CC_EV < 1e-12

    def test_pdg_dm21(self):
        assert abs(PDG_DM21_SQ - 7.53e-5) < 1e-7

    def test_pdg_dm31(self):
        assert abs(PDG_DM31_SQ - 2.453e-3) < 1e-6


class TestSeparationGuard:
    def test_is_string(self):
        assert isinstance(separation_guard(), str)

    def test_contains_adjacent(self):
        assert "ADJACENT" in separation_guard()

    def test_contains_juno(self):
        sg = separation_guard().upper()
        assert "JUNO" in sg


class TestOscillationArgument:
    def test_typical_value(self):
        # At E=5 MeV, L=52.5 km, Δm²₂₁ = 7.53e-5 eV²
        arg = oscillation_argument(DM21_SQ_EV2, JUNO_BASELINE_KM, 5.0)
        # Should be ~ 1.27 × 7.53e-5 × 52.5 / (5e-3) ≈ 1.0 rad
        assert 0.5 < arg < 2.5

    def test_proportional_to_dm_sq(self):
        arg1 = oscillation_argument(1e-4, 50.0, 5.0)
        arg2 = oscillation_argument(2e-4, 50.0, 5.0)
        assert abs(arg2 / arg1 - 2.0) < 1e-9

    def test_proportional_to_L(self):
        arg1 = oscillation_argument(DM21_SQ_EV2, 50.0, 5.0)
        arg2 = oscillation_argument(DM21_SQ_EV2, 100.0, 5.0)
        assert abs(arg2 / arg1 - 2.0) < 1e-9

    def test_inversely_proportional_to_E(self):
        arg1 = oscillation_argument(DM21_SQ_EV2, 50.0, 5.0)
        arg2 = oscillation_argument(DM21_SQ_EV2, 50.0, 10.0)
        assert abs(arg1 / arg2 - 2.0) < 1e-9


class TestSurvivalProbability:
    def test_probability_in_range(self):
        for E in [2.0, 5.0, 8.0]:
            p = survival_probability_vacuum(E)
            assert 0 <= p <= 1, f"P_ee out of range at E={E} MeV: {p}"

    def test_high_energy_limit(self):
        # At very high E, oscillations are slow → P_ee → 1 - (sum of sin²(small))
        # Not exactly 1 but close
        p = survival_probability_vacuum(1000.0)
        assert p > 0.9

    def test_probability_not_constant(self):
        # Should oscillate, not be constant
        p_vals = [survival_probability_vacuum(E) for E in [2, 3, 4, 5, 6, 7, 8]]
        assert max(p_vals) - min(p_vals) > 0.01

    def test_matter_vs_vacuum_similar(self):
        # Matter correction is sub-percent — should be < 1% difference
        for E in [2.0, 5.0, 8.0]:
            p_vac = survival_probability_vacuum(E)
            p_mat = survival_probability_with_matter(E)
            assert abs(p_mat - p_vac) < 0.01, (
                f"Matter correction unexpectedly large at E={E} MeV: {abs(p_mat-p_vac)}"
            )

    def test_matter_correction_tiny(self):
        frac = matter_correction_fraction(5.0)
        # ~0.02% at JUNO energies — small but physically non-zero
        assert frac < 0.01  # much less than JUNO ordering sensitivity (~10%)


class TestOscillationMinimum:
    def test_in_juno_energy_range(self):
        e_min = oscillation_minimum_energy()
        # Solar oscillation minimum should be in 1–20 MeV at 52.5 km
        assert 0.5 < e_min < 50.0

    def test_is_positive(self):
        assert oscillation_minimum_energy() > 0


class TestJunoSpectrum:
    def test_returns_list(self):
        spec = juno_spectrum_sample(10)
        assert isinstance(spec, list)
        assert len(spec) == 10

    def test_spectrum_keys(self):
        spec = juno_spectrum_sample(5)
        for entry in spec:
            assert "E_mev" in entry
            assert "P_ee_vacuum" in entry
            assert "P_ee_matter" in entry
            assert "matter_correction_frac" in entry

    def test_probabilities_in_range(self):
        spec = juno_spectrum_sample(10)
        for entry in spec:
            assert 0 <= entry["P_ee_vacuum"] <= 1
            assert 0 <= entry["P_ee_matter"] <= 1

    def test_energies_span_range(self):
        spec = juno_spectrum_sample(10)
        e_vals = [e["E_mev"] for e in spec]
        assert e_vals[0] == pytest.approx(JUNO_ENERGY_MIN_MEV, rel=1e-6)
        assert e_vals[-1] == pytest.approx(JUNO_ENERGY_MAX_MEV, rel=1e-6)

    def test_matter_corrections_subdominant(self):
        spec = juno_spectrum_sample(10)
        for entry in spec:
            assert entry["matter_correction_frac"] < 0.01


class TestPrecisionBudget:
    def test_returns_dict(self):
        budget = juno_precision_budget()
        assert isinstance(budget, dict)

    def test_has_parameters(self):
        budget = juno_precision_budget()
        assert "parameters" in budget

    def test_dm21_within_juno_target(self):
        budget = juno_precision_budget()
        dm21 = budget["parameters"]["dm21_sq_ev2"]
        # UM Δm²₂₁ exactly matches PDG → residual = 0%
        assert dm21["residual_percent"] < 1.0

    def test_dm31_residual_exists(self):
        budget = juno_precision_budget()
        dm31 = budget["parameters"]["dm31_sq_ev2"]
        assert "residual_percent" in dm31
        assert dm31["residual_percent"] < 5.0  # within 5%

    def test_mass_ordering_predicted(self):
        budget = juno_precision_budget()
        mo = budget["parameters"]["mass_ordering"]
        assert "NORMAL" in mo["um_prediction"]


class TestRoutingProtocol:
    def test_io_at_3sigma_falsified(self):
        result = route_juno_dr1("IO", 3.5)
        assert result["ordering_verdict"] == "FALSIFIED"

    def test_io_at_2sigma_tension(self):
        result = route_juno_dr1("IO", 2.5)
        assert result["ordering_verdict"] == "HIGH_TENSION"

    def test_no_at_3sigma_confirmed(self):
        result = route_juno_dr1("NO", 3.2)
        assert result["ordering_verdict"] == "CONFIRMED"

    def test_no_at_1sigma_consistent(self):
        result = route_juno_dr1("NO", 1.5)
        assert result["ordering_verdict"] == "CONSISTENT"

    def test_with_dm31_measurement(self):
        result = route_juno_dr1("NO", 3.5,
                                dm31_measured=2.454e-3,
                                dm31_sigma_percent=0.5)
        assert result["dm31_verdict"] is not None
        assert "CONSISTENT" in result["dm31_verdict"]

    def test_dm31_tension_flagged(self):
        # Shift Δm²₃₁ by 2% — at 0.5% precision this is 4σ
        result = route_juno_dr1("NO", 3.5,
                                dm31_measured=DM31_SQ_EV2 * 1.02,
                                dm31_sigma_percent=0.5)
        assert "TENSION" in result["dm31_verdict"]

    def test_result_has_actions(self):
        result = route_juno_dr1("IO", 3.5)
        assert isinstance(result["required_actions"], list)
        assert len(result["required_actions"]) > 0

    def test_result_has_pillar(self):
        result = route_juno_dr1("NO", 3.0)
        assert result["pillar"] == 334

    def test_io_case_insensitive(self):
        result = route_juno_dr1("io", 3.5)
        assert result["ordering_verdict"] == "FALSIFIED"


class TestManifest:
    def test_returns_dict(self):
        m = juno_prediction_manifest()
        assert isinstance(m, dict)

    def test_has_version(self):
        m = juno_prediction_manifest()
        assert "v11.18" in m["manifest_version"]

    def test_has_falsifier(self):
        m = juno_prediction_manifest()
        assert "falsifier" in m
        assert "IO" in m["falsifier"]["condition"]

    def test_has_parameters(self):
        m = juno_prediction_manifest()
        params = m["parameters"]
        assert "dm21_sq_ev2" in params
        assert "mass_ordering" in params
        assert params["mass_ordering"] == "NORMAL"

    def test_json_serializable(self):
        json_str = juno_prediction_manifest_json()
        parsed = json.loads(json_str)
        assert parsed["pillar"] == 334

    def test_spectrum_in_manifest(self):
        m = juno_prediction_manifest()
        assert len(m["spectrum_sample_10pts"]) == 10

    def test_matter_correction_documented(self):
        m = juno_prediction_manifest()
        # ~0.02% matter correction — sub-dominant to ordering effect
        assert m["juno_setup"]["matter_correction_typical_frac"] < 0.01


class TestFullReport:
    def test_returns_dict(self):
        report = juno_full_report()
        assert isinstance(report, dict)

    def test_pillar_number(self):
        assert juno_full_report()["pillar"] == 334

    def test_falsification_condition(self):
        report = juno_full_report()
        assert "IO" in report["falsification_condition"]
        assert "3σ" in report["falsification_condition"]

    def test_separation_guard_present(self):
        report = juno_full_report()
        assert "ADJACENT" in report["separation_guard"]

    def test_um_predictions_present(self):
        report = juno_full_report()
        assert "dm21_sq_ev2" in report["um_predictions"]
        assert "mass_ordering" in report["um_predictions"]

    def test_baseline_correct(self):
        report = juno_full_report()
        assert abs(report["baseline_km"] - 52.5) < 0.1

    def test_matter_correction_subdominant(self):
        report = juno_full_report()
        # ~0.02% at JUNO energies — sub-dominant
        assert report["matter_correction_at_5mev"] < 0.01
