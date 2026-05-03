# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_lambda_topological_defect.py
========================================
Tests for Pillar 126 — Cosmological Constant as Topological Defect.
"""

from __future__ import annotations

import math

import pytest

from src.core.lambda_topological_defect import (
    LAMBDA_OBSERVED_M2,
    K_CS,
    N_W,
    RHO_PLANCK_KGM3,
    TWIST_ENERGY_SCALE,
    equation_of_state_w,
    falsification_conditions,
    hubble_tension_alignment,
    lambda_from_topology,
    twist_energy_density_SI,
    um_alignment,
)


class TestTwistEnergyDensitySI:
    def test_returns_float(self):
        assert isinstance(twist_energy_density_SI(), float)

    def test_positive(self):
        assert twist_energy_density_SI() > 0

    def test_finite(self):
        assert math.isfinite(twist_energy_density_SI())

    def test_less_than_planck_density(self):
        # TWIST_ENERGY_SCALE < 1, so product must be < RHO_PLANCK_KGM3
        assert twist_energy_density_SI() < RHO_PLANCK_KGM3

    def test_type_is_float(self):
        result = twist_energy_density_SI()
        assert type(result) is float

    def test_matches_formula(self):
        expected = TWIST_ENERGY_SCALE * RHO_PLANCK_KGM3
        assert twist_energy_density_SI() == pytest.approx(expected, rel=1e-9)


class TestLambdaFromTopology:
    def setup_method(self):
        self.result = lambda_from_topology()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_has_all_required_keys(self):
        required = {
            "lambda_observed_m2",
            "twist_rho_kgm3",
            "lambda_derived_m2",
            "ratio_derived_to_observed",
            "log10_ratio",
            "order_of_magnitude_match",
            "cs_coupling",
            "winding_number",
            "formula",
            "epistemic_status",
        }
        assert required.issubset(self.result.keys())

    def test_lambda_observed_value(self):
        assert self.result["lambda_observed_m2"] == pytest.approx(LAMBDA_OBSERVED_M2, rel=1e-9)

    def test_twist_rho_positive(self):
        assert self.result["twist_rho_kgm3"] > 0

    def test_lambda_derived_positive(self):
        assert self.result["lambda_derived_m2"] > 0

    def test_ratio_positive(self):
        assert self.result["ratio_derived_to_observed"] > 0

    def test_log10_ratio_is_float(self):
        assert isinstance(self.result["log10_ratio"], float)

    def test_order_of_magnitude_match_is_bool(self):
        assert isinstance(self.result["order_of_magnitude_match"], bool)

    def test_cs_coupling(self):
        assert self.result["cs_coupling"] == K_CS

    def test_winding_number(self):
        assert self.result["winding_number"] == N_W

    def test_formula_nonempty(self):
        assert isinstance(self.result["formula"], str)
        assert len(self.result["formula"]) > 0

    def test_epistemic_status_predictive(self):
        assert "PREDICTIVE" in self.result["epistemic_status"]


class TestEquationOfStateW:
    def test_returns_float(self):
        assert isinstance(equation_of_state_w(), float)

    def test_equals_minus_one(self):
        assert equation_of_state_w() == pytest.approx(-1.0)

    def test_type_is_float(self):
        assert type(equation_of_state_w()) is float

    def test_negative(self):
        assert equation_of_state_w() < 0

    def test_greater_than_minus_two(self):
        assert equation_of_state_w() > -2.0


class TestHubbleTensionAlignment:
    def setup_method(self):
        self.result = hubble_tension_alignment()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_has_all_required_keys(self):
        required = {
            "h0_cmb_kmsmpc",
            "h0_local_kmsmpc",
            "tension_sigma",
            "geometric_lambda_delta_h0",
            "direction",
            "tension_reduced",
            "mechanism",
            "prediction",
            "falsification",
            "epistemic_status",
        }
        assert required.issubset(self.result.keys())

    def test_h0_cmb(self):
        assert self.result["h0_cmb_kmsmpc"] == pytest.approx(67.4)

    def test_h0_local(self):
        assert self.result["h0_local_kmsmpc"] == pytest.approx(73.2)

    def test_tension_sigma(self):
        assert self.result["tension_sigma"] == pytest.approx(5.0)

    def test_delta_h0_positive(self):
        assert self.result["geometric_lambda_delta_h0"] > 0

    def test_direction_nonempty(self):
        assert isinstance(self.result["direction"], str)
        assert len(self.result["direction"]) > 0

    def test_tension_reduced_true(self):
        assert self.result["tension_reduced"] is True

    def test_mechanism_nonempty(self):
        assert isinstance(self.result["mechanism"], str)
        assert len(self.result["mechanism"]) > 0

    def test_prediction_nonempty(self):
        assert isinstance(self.result["prediction"], str)
        assert len(self.result["prediction"]) > 0

    def test_falsification_nonempty(self):
        assert isinstance(self.result["falsification"], str)
        assert len(self.result["falsification"]) > 0

    def test_epistemic_status_nonempty(self):
        assert isinstance(self.result["epistemic_status"], str)
        assert len(self.result["epistemic_status"]) > 0

    def test_tension_reduced_is_bool(self):
        assert type(self.result["tension_reduced"]) is bool


class TestUmAlignment:
    def setup_method(self):
        self.result = um_alignment()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar(self):
        assert self.result["pillar"] == 126

    def test_cs_coupling(self):
        assert self.result["cs_coupling"] == 74

    def test_winding_number(self):
        assert self.result["winding_number"] == 5

    def test_twist_energy_scale(self):
        assert self.result["twist_energy_scale"] == pytest.approx(TWIST_ENERGY_SCALE, rel=1e-9)

    def test_lambda_geometric_true(self):
        assert self.result["lambda_geometric"] is True

    def test_dark_energy_identification_nonempty(self):
        assert isinstance(self.result["dark_energy_identification"], str)
        assert len(self.result["dark_energy_identification"]) > 0

    def test_n_free_parameters_zero(self):
        assert self.result["n_free_parameters"] == 0

    def test_observables_list_min_length(self):
        obs = self.result["observables"]
        assert isinstance(obs, list)
        assert len(obs) >= 3


class TestFalsificationConditions:
    def setup_method(self):
        self.result = falsification_conditions()

    def test_returns_list(self):
        assert isinstance(self.result, list)

    def test_min_length_four(self):
        assert len(self.result) >= 4

    def test_each_item_is_dict(self):
        for item in self.result:
            assert isinstance(item, dict)

    def test_each_has_condition_number(self):
        for item in self.result:
            assert "condition_number" in item

    def test_each_has_description(self):
        for item in self.result:
            assert "description" in item

    def test_each_has_measurement(self):
        for item in self.result:
            assert "measurement" in item

    def test_each_has_threshold(self):
        for item in self.result:
            assert "threshold" in item

    def test_condition_numbers_sequential(self):
        numbers = [item["condition_number"] for item in self.result]
        assert numbers == list(range(1, len(self.result) + 1))

    def test_all_descriptions_nonempty(self):
        for item in self.result:
            assert isinstance(item["description"], str) and len(item["description"]) > 0

    def test_all_measurements_nonempty(self):
        for item in self.result:
            assert isinstance(item["measurement"], str) and len(item["measurement"]) > 0

    def test_first_condition_mentions_w(self):
        first_desc = self.result[0]["description"].lower()
        assert "w" in first_desc or "equation of state" in first_desc

    def test_one_condition_mentions_evolving(self):
        texts = " ".join(item["description"] for item in self.result).lower()
        assert "evolv" in texts or "dλ" in texts or "time" in texts

    def test_one_condition_mentions_e2_or_topology(self):
        texts = " ".join(item["description"] for item in self.result).lower()
        assert "e2" in texts or "topology" in texts

    def test_all_thresholds_nonempty(self):
        for item in self.result:
            assert isinstance(item["threshold"], str) and len(item["threshold"]) > 0
