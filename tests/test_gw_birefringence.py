# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_gw_birefringence.py
================================
Test suite for Pillar 125 — Gravitational Wave Birefringence.
~55 tests across 6 classes.
"""

from __future__ import annotations

import math

import pytest

from src.core.gw_birefringence import (
    BETA_GW_DEG,
    BETA_GW_RAD,
    K_CS,
    N_W,
    R_BRAIDED,
    chiral_gw_spectrum,
    einstein_telescope_forecast,
    gw_polarization_rotation_rad,
    lisa_detectability,
    topology_induced_gw_beta,
    um_alignment,
)


# ---------------------------------------------------------------------------
# TestGwPolarizationRotation (10 tests)
# ---------------------------------------------------------------------------

class TestGwPolarizationRotation:
    def test_returns_float(self):
        result = gw_polarization_rotation_rad(1.0, 1.0)
        assert isinstance(result, float)

    def test_nonnegative_for_k0_l0(self):
        assert gw_polarization_rotation_rad(0.0, 0.0) >= 0.0

    def test_positive_for_k0_l1(self):
        assert gw_polarization_rotation_rad(0.0, 1.0) > 0.0

    def test_positive_for_large_k(self):
        assert gw_polarization_rotation_rad(1000.0, 1.0) > 0.0

    def test_at_least_beta_gw_rad(self):
        # Topology correction is non-negative, so result ≥ BETA_GW_RAD
        result = gw_polarization_rotation_rad(0.5, 0.5)
        assert result >= BETA_GW_RAD

    def test_k0_l1_equals_1p1_times_beta(self):
        # At k=0, exp(0)=1, delta_psi = BETA_GW_RAD*0.1, total = 1.1*BETA_GW_RAD
        result = gw_polarization_rotation_rad(0.0, 1.0)
        assert result == pytest.approx(1.1 * BETA_GW_RAD, rel=1e-9)

    def test_large_k_approaches_beta_gw_rad(self):
        # exp(-1000*1.0)*0.1 ≈ 0; total ≈ BETA_GW_RAD
        result = gw_polarization_rotation_rad(1000.0, 1.0)
        assert result == pytest.approx(BETA_GW_RAD, rel=1e-6)

    def test_valueerror_for_negative_k(self):
        with pytest.raises(ValueError):
            gw_polarization_rotation_rad(-0.1, 1.0)

    def test_valueerror_for_negative_l(self):
        with pytest.raises(ValueError):
            gw_polarization_rotation_rad(1.0, -0.1)

    def test_monotonically_decreasing_toward_beta_as_k_increases(self):
        # Higher k → smaller topology correction → closer to BETA_GW_RAD
        r1 = gw_polarization_rotation_rad(1.0, 1.0)
        r2 = gw_polarization_rotation_rad(5.0, 1.0)
        r3 = gw_polarization_rotation_rad(10.0, 1.0)
        assert r1 > r2 > r3 >= BETA_GW_RAD


# ---------------------------------------------------------------------------
# TestTopologyInducedGwBeta (10 tests)
# ---------------------------------------------------------------------------

class TestTopologyInducedGwBeta:
    def setup_method(self):
        self.result = topology_induced_gw_beta()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_beta_gw_deg(self):
        assert self.result["beta_gw_deg"] == BETA_GW_DEG

    def test_beta_gw_rad(self):
        assert self.result["beta_gw_rad"] == pytest.approx(BETA_GW_RAD, rel=1e-9)

    def test_beta_cmb_deg(self):
        assert self.result["beta_cmb_deg"] == pytest.approx(0.351, rel=1e-9)

    def test_consistency_check_is_true(self):
        assert self.result["consistency_check"] is True

    def test_cs_coupling(self):
        assert self.result["cs_coupling"] == 74

    def test_winding_number(self):
        assert self.result["winding_number"] == 5

    def test_topology_contribution_fraction(self):
        assert self.result["topology_contribution_fraction"] == pytest.approx(0.1)

    def test_total_birefringence_deg(self):
        assert self.result["total_birefringence_deg"] == pytest.approx(
            BETA_GW_DEG * 1.1, rel=1e-9
        )

    def test_parity_violation_source_nonempty(self):
        src = self.result["parity_violation_source"]
        assert isinstance(src, str) and len(src) > 0

    def test_epistemic_status_contains_predictive(self):
        assert "PREDICTIVE" in self.result["epistemic_status"]


# ---------------------------------------------------------------------------
# TestChiralGwSpectrum (12 tests)
# ---------------------------------------------------------------------------

class TestChiralGwSpectrum:
    _k = [1.0, 2.0, 3.0]
    _r = 0.0315

    def setup_method(self):
        self.result = chiral_gw_spectrum(self._k, self._r)

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_has_required_keys(self):
        for key in ("k", "h_L", "h_R", "delta_h", "chiral_asymmetry",
                    "r", "max_delta_h", "mean_h_L", "mean_h_R"):
            assert key in self.result

    def test_h_L_is_list(self):
        assert isinstance(self.result["h_L"], list)

    def test_h_R_is_list(self):
        assert isinstance(self.result["h_R"], list)

    def test_delta_h_is_list(self):
        assert isinstance(self.result["delta_h"], list)

    def test_lengths_match_k_array(self):
        assert len(self.result["h_L"]) == len(self._k)
        assert len(self.result["h_R"]) == len(self._k)
        assert len(self.result["delta_h"]) == len(self._k)

    def test_h_L_all_positive(self):
        assert all(v > 0 for v in self.result["h_L"])

    def test_h_R_all_positive(self):
        assert all(v > 0 for v in self.result["h_R"])

    def test_h_L_greater_than_h_R(self):
        for l, r in zip(self.result["h_L"], self.result["h_R"]):
            assert l > r

    def test_delta_h_all_positive(self):
        assert all(v > 0 for v in self.result["delta_h"])

    def test_valueerror_for_negative_r(self):
        with pytest.raises(ValueError):
            chiral_gw_spectrum([1.0, 2.0], -0.1)

    def test_valueerror_for_nonpositive_k(self):
        with pytest.raises(ValueError):
            chiral_gw_spectrum([1.0, 0.0, 2.0], 0.03)

    def test_max_delta_h_positive(self):
        assert self.result["max_delta_h"] > 0

    def test_chiral_asymmetry_true(self):
        assert self.result["chiral_asymmetry"] is True


# ---------------------------------------------------------------------------
# TestLisaDetectability (10 tests)
# ---------------------------------------------------------------------------

class TestLisaDetectability:
    def setup_method(self):
        self.result = lisa_detectability()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_instrument_name(self):
        assert self.result["instrument"] == "LISA"

    def test_sensitivity_strain(self):
        assert self.result["sensitivity_strain"] == pytest.approx(1e-23)

    def test_expected_chiral_signal_positive(self):
        assert self.result["expected_chiral_signal"] > 0

    def test_expected_chiral_signal_value(self):
        assert self.result["expected_chiral_signal"] == pytest.approx(
            R_BRAIDED * BETA_GW_RAD, rel=1e-9
        )

    def test_noise_per_mode(self):
        assert self.result["noise_per_mode"] == pytest.approx(0.001)

    def test_snr_positive(self):
        assert self.result["snr"] > 0

    def test_detectable_is_bool(self):
        assert isinstance(self.result["detectable"], bool)

    def test_frequency_band_hz_nonempty(self):
        band = self.result["frequency_band_hz"]
        assert isinstance(band, str) and len(band) > 0

    def test_mission_duration_years(self):
        assert self.result["mission_duration_years"] == pytest.approx(4.0)

    def test_reference_contains_lisa(self):
        assert "LISA" in self.result["reference"]


# ---------------------------------------------------------------------------
# TestEinsteinTelescopeForecast (8 tests)
# ---------------------------------------------------------------------------

class TestEinsteinTelescopeForecast:
    def setup_method(self):
        self.result = einstein_telescope_forecast()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_instrument_name(self):
        assert self.result["instrument"] == "Einstein Telescope"

    def test_expected_chiral_signal_positive(self):
        assert self.result["expected_chiral_signal"] > 0

    def test_detectable_true(self):
        assert self.result["detectable"] is True

    def test_mission_start_year(self):
        assert self.result["mission_start_year"] == 2035

    def test_reference_contains_et_info(self):
        ref = self.result["reference"]
        assert "Punturo" in ref or "ET" in ref or "Einstein" in ref

    def test_snr_positive(self):
        assert self.result["snr"] > 0

    def test_epistemic_status_contains_predictive(self):
        assert "PREDICTIVE" in self.result["epistemic_status"]

    def test_frequency_band_hz_nonempty(self):
        band = self.result["frequency_band_hz"]
        assert isinstance(band, str) and len(band) > 0


# ---------------------------------------------------------------------------
# TestUmAlignment (5 tests)
# ---------------------------------------------------------------------------

class TestUmAlignment:
    def setup_method(self):
        self.result = um_alignment()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar(self):
        assert self.result["pillar"] == 125

    def test_cs_coupling(self):
        assert self.result["cs_coupling"] == 74

    def test_winding_number(self):
        assert self.result["winding_number"] == 5

    def test_coupling_consistency_true(self):
        assert self.result["coupling_consistency"] is True

    def test_independent_falsifier_true(self):
        assert self.result["independent_falsifier"] is True
