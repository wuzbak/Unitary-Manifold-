# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_anisotropic_birefringence.py
=========================================
Tests for Pillar 118 — Anisotropic Birefringence β(n̂).

Covers all six public API functions across ~55 test methods.
"""

from __future__ import annotations

import math

import pytest

from src.core.anisotropic_birefringence import (
    BETA_ISO_DEG,
    BETA_ISO_RAD,
    E2_MODULATION_AMPLITUDE,
    E3_MODULATION_AMPLITUDE,
    K_CS,
    LITEBIRD_BETA_SENSITIVITY_RAD,
    N_W,
    beta_anisotropic,
    beta_isotropic,
    birefringence_power_spectrum,
    holonomy_modulation,
    litebird_sensitivity_forecast,
    um_alignment,
)


class TestBetaIsotropic:
    def test_returns_float(self):
        assert isinstance(beta_isotropic(), float)

    def test_value_positive(self):
        assert beta_isotropic() > 0.0

    def test_value_in_radians_range(self):
        # Must be well below 0.1 rad (≈ 5.7°)
        assert beta_isotropic() < 0.1

    def test_equals_beta_iso_rad_constant(self):
        assert beta_isotropic() == pytest.approx(BETA_ISO_RAD)

    def test_equals_formula_value(self):
        expected = 0.351 * math.pi / 180.0
        assert beta_isotropic() == pytest.approx(expected, rel=1e-9)

    def test_consistent_with_beta_iso_deg(self):
        from_deg = BETA_ISO_DEG * math.pi / 180.0
        assert beta_isotropic() == pytest.approx(from_deg, rel=1e-9)


class TestHolonomyModulation:
    def test_returns_float(self):
        assert isinstance(holonomy_modulation(math.pi / 2, 0.0), float)

    def test_north_pole_is_zero(self):
        # sin(0) = 0 → δ = 0 regardless of φ
        assert holonomy_modulation(0.0, 0.0) == pytest.approx(0.0, abs=1e-15)

    def test_south_pole_is_zero(self):
        # sin(π) = 0 → δ = 0
        assert holonomy_modulation(math.pi, 0.0) == pytest.approx(0.0, abs=1e-15)

    def test_equator_phi0_positive(self):
        # cos(0) = 1, sin(π/2) = 1 → δ = E2_MODULATION_AMPLITUDE > 0
        assert holonomy_modulation(math.pi / 2, 0.0) > 0.0

    def test_equator_phi_pi_negative(self):
        # cos(π) = -1 → δ < 0
        assert holonomy_modulation(math.pi / 2, math.pi) < 0.0

    def test_amplitude_at_equator_phi0(self):
        delta = holonomy_modulation(math.pi / 2, 0.0)
        assert delta == pytest.approx(E2_MODULATION_AMPLITUDE, rel=1e-9)

    def test_amplitude_at_equator_phi_pi(self):
        delta = holonomy_modulation(math.pi / 2, math.pi)
        assert delta == pytest.approx(-E2_MODULATION_AMPLITUDE, rel=1e-9)

    def test_magnitude_bounded_various_positions(self):
        positions = [
            (0.1, 0.5),
            (1.0, 1.0),
            (2.0, 3.0),
            (math.pi / 4, math.pi / 3),
            (2.5, 5.0),
        ]
        for theta, phi in positions:
            assert abs(holonomy_modulation(theta, phi)) <= E2_MODULATION_AMPLITUDE + 1e-12

    def test_phi_half_pi_gives_zero(self):
        # cos(π/2) = 0 → δ = 0 for any θ
        assert holonomy_modulation(math.pi / 2, math.pi / 2) == pytest.approx(0.0, abs=1e-15)

    def test_antisymmetry_phi_and_phi_plus_pi(self):
        theta = math.pi / 3
        phi = math.pi / 6
        d1 = holonomy_modulation(theta, phi)
        d2 = holonomy_modulation(theta, phi + math.pi)
        assert d1 == pytest.approx(-d2, rel=1e-9)


class TestBetaAnisotropic:
    def test_returns_float(self):
        assert isinstance(beta_anisotropic(math.pi / 2, 0.0), float)

    def test_always_positive_sample_positions(self):
        positions = [
            (0.0, 0.0),
            (math.pi / 4, 0.0),
            (math.pi / 2, 0.0),
            (math.pi / 2, math.pi),
            (math.pi / 2, math.pi / 2),
            (math.pi, 0.0),
            (1.0, 2.5),
        ]
        for theta, phi in positions:
            assert beta_anisotropic(theta, phi) > 0.0

    def test_equator_phi0_greater_than_isotropic(self):
        assert beta_anisotropic(math.pi / 2, 0.0) > beta_isotropic()

    def test_equator_phi_pi_less_than_isotropic_but_positive(self):
        val = beta_anisotropic(math.pi / 2, math.pi)
        assert val < beta_isotropic()
        assert val > 0.0

    def test_equals_formula(self):
        theta, phi = math.pi / 3, math.pi / 4
        expected = BETA_ISO_RAD * (1.0 + holonomy_modulation(theta, phi))
        assert beta_anisotropic(theta, phi) == pytest.approx(expected, rel=1e-9)

    def test_consistent_with_holonomy_modulation(self):
        theta, phi = 1.2, 0.8
        delta = holonomy_modulation(theta, phi)
        assert beta_anisotropic(theta, phi) == pytest.approx(BETA_ISO_RAD * (1.0 + delta), rel=1e-9)

    def test_at_poles_equals_isotropic(self):
        # At poles δ = 0 so β = β₀
        assert beta_anisotropic(0.0, 0.0) == pytest.approx(BETA_ISO_RAD, rel=1e-9)
        assert beta_anisotropic(math.pi, 1.0) == pytest.approx(BETA_ISO_RAD, rel=1e-9)

    def test_max_value_at_equator_phi0(self):
        val = beta_anisotropic(math.pi / 2, 0.0)
        assert val == pytest.approx(BETA_ISO_RAD * (1.0 + E2_MODULATION_AMPLITUDE), rel=1e-9)

    def test_min_value_at_equator_phi_pi(self):
        val = beta_anisotropic(math.pi / 2, math.pi)
        assert val == pytest.approx(BETA_ISO_RAD * (1.0 - E2_MODULATION_AMPLITUDE), rel=1e-9)

    def test_phi_half_pi_equals_isotropic(self):
        # cos(π/2) = 0 → no modulation
        assert beta_anisotropic(math.pi / 2, math.pi / 2) == pytest.approx(BETA_ISO_RAD, rel=1e-9)


class TestBirefringencePowerSpectrum:
    def test_returns_dict(self):
        result = birefringence_power_spectrum(5)
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = birefringence_power_spectrum(3)
        for key in ("l_max", "ells", "C_ell_delta_beta", "dominant_multipole", "physical_origin"):
            assert key in result

    def test_l_max_matches_input(self):
        result = birefringence_power_spectrum(7)
        assert result["l_max"] == 7

    def test_ells_length_equals_l_max(self):
        result = birefringence_power_spectrum(5)
        assert len(result["ells"]) == 5

    def test_c_ell_length_equals_l_max(self):
        result = birefringence_power_spectrum(5)
        assert len(result["C_ell_delta_beta"]) == 5

    def test_all_c_ell_positive(self):
        result = birefringence_power_spectrum(10)
        for c in result["C_ell_delta_beta"]:
            assert c > 0.0

    def test_dipole_l1_is_largest(self):
        result = birefringence_power_spectrum(5)
        c_ells = result["C_ell_delta_beta"]
        assert c_ells[0] == max(c_ells)

    def test_c_ell_decreasing_after_l1(self):
        result = birefringence_power_spectrum(6)
        c_ells = result["C_ell_delta_beta"]
        for i in range(1, len(c_ells) - 1):
            assert c_ells[i] > c_ells[i + 1]

    def test_dominant_multipole_is_1(self):
        result = birefringence_power_spectrum(4)
        assert result["dominant_multipole"] == 1

    def test_physical_origin_string(self):
        result = birefringence_power_spectrum(2)
        assert isinstance(result["physical_origin"], str)
        assert len(result["physical_origin"]) > 0

    def test_raises_value_error_l_max_zero(self):
        with pytest.raises(ValueError):
            birefringence_power_spectrum(0)

    def test_raises_value_error_l_max_negative(self):
        with pytest.raises(ValueError):
            birefringence_power_spectrum(-3)

    def test_l_max_1_single_element(self):
        result = birefringence_power_spectrum(1)
        assert len(result["ells"]) == 1
        assert result["ells"] == [1]
        assert len(result["C_ell_delta_beta"]) == 1

    def test_c1_formula(self):
        result = birefringence_power_spectrum(1)
        expected_c1 = (4.0 * math.pi / 3.0) * (BETA_ISO_RAD * E2_MODULATION_AMPLITUDE) ** 2
        assert result["C_ell_delta_beta"][0] == pytest.approx(expected_c1, rel=1e-9)


class TestLitebirdForecast:
    def test_returns_dict(self):
        result = litebird_sensitivity_forecast()
        assert isinstance(result, dict)

    def test_has_all_required_keys(self):
        result = litebird_sensitivity_forecast()
        required_keys = [
            "instrument",
            "iso_beta_sensitivity_deg",
            "aniso_beta_snr",
            "detection_threshold_deg",
            "expected_signal_deg",
            "detection_feasible",
            "mission_duration_years",
            "key_channels",
            "reference",
        ]
        for key in required_keys:
            assert key in result

    def test_instrument_is_litebird(self):
        result = litebird_sensitivity_forecast()
        assert result["instrument"] == "LiteBIRD"

    def test_mission_duration_years(self):
        result = litebird_sensitivity_forecast()
        assert result["mission_duration_years"] == pytest.approx(3.0)

    def test_aniso_beta_snr_is_positive_float(self):
        result = litebird_sensitivity_forecast()
        assert isinstance(result["aniso_beta_snr"], float)
        assert result["aniso_beta_snr"] > 0.0

    def test_detection_feasible_is_bool(self):
        result = litebird_sensitivity_forecast()
        assert isinstance(result["detection_feasible"], bool)

    def test_key_channels_is_list_of_three(self):
        result = litebird_sensitivity_forecast()
        assert isinstance(result["key_channels"], list)
        assert len(result["key_channels"]) == 3

    def test_reference_contains_litebird(self):
        result = litebird_sensitivity_forecast()
        assert "LiteBIRD" in result["reference"]

    def test_expected_signal_deg_positive(self):
        result = litebird_sensitivity_forecast()
        assert result["expected_signal_deg"] > 0.0

    def test_iso_beta_sensitivity_deg_positive(self):
        result = litebird_sensitivity_forecast()
        assert result["iso_beta_sensitivity_deg"] > 0.0

    def test_sensitivity_deg_formula(self):
        result = litebird_sensitivity_forecast()
        expected = LITEBIRD_BETA_SENSITIVITY_RAD * 180.0 / math.pi
        assert result["iso_beta_sensitivity_deg"] == pytest.approx(expected, rel=1e-9)

    def test_expected_signal_deg_formula(self):
        result = litebird_sensitivity_forecast()
        expected = BETA_ISO_DEG * E2_MODULATION_AMPLITUDE
        assert result["expected_signal_deg"] == pytest.approx(expected, rel=1e-9)


class TestUmAlignment:
    def test_returns_dict(self):
        assert isinstance(um_alignment(), dict)

    def test_pillar_is_118(self):
        assert um_alignment()["pillar"] == 118

    def test_cs_coupling_is_74(self):
        assert um_alignment()["cs_coupling"] == K_CS
        assert um_alignment()["cs_coupling"] == 74

    def test_winding_number_is_5(self):
        assert um_alignment()["winding_number"] == N_W
        assert um_alignment()["winding_number"] == 5

    def test_parameter_count_is_zero(self):
        assert um_alignment()["parameter_count"] == 0

    def test_observables_list_has_at_least_three(self):
        obs = um_alignment()["observables"]
        assert isinstance(obs, list)
        assert len(obs) >= 3

    def test_falsification_is_nonempty_string(self):
        f = um_alignment()["falsification"]
        assert isinstance(f, str)
        assert len(f) > 0

    def test_epistemic_status_is_nonempty_string(self):
        e = um_alignment()["epistemic_status"]
        assert isinstance(e, str)
        assert len(e) > 0
