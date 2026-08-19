# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
from __future__ import annotations

import math

import pytest

from src.core.photon_propagator_rs1 import (
    K_CS,
    M_KK_GEV,
    M_PL_GEV,
    N_W,
    PHOTON_KK_ROOTS,
    PI_K_R,
    PILLAR,
    PILLAR_STATUS,
    birefringence_warp_correction,
    cs_photon_overlap_integral,
    photon_kk_spectrum,
    photon_propagator_rs1_report,
    photon_propagator_zero_mode,
    photon_zero_mode_wavefunction,
)


def test_constants_match_context():
    assert N_W == 5
    assert K_CS == 74
    assert PI_K_R == pytest.approx(37.0)
    assert M_KK_GEV == pytest.approx(M_PL_GEV * math.exp(-PI_K_R), rel=1e-12)


def test_pillar_metadata():
    assert PILLAR == 772
    assert PILLAR_STATUS == "PHOTON_PROPAGATOR_RS1_DERIVED"


def test_zero_mode_returns_dict():
    result = photon_zero_mode_wavefunction()
    assert isinstance(result, dict)
    assert result["status"] == "DERIVED"
    assert result["epistemic_status"] == "DERIVED"


def test_zero_mode_is_massless_and_even():
    result = photon_zero_mode_wavefunction()
    assert result["massless"] is True
    assert result["z2_parity"] == "even"


def test_zero_mode_normalization_is_unity():
    result = photon_zero_mode_wavefunction()
    assert result["normalization_check"] == pytest.approx(1.0, rel=1e-12)


def test_zero_mode_radius_positive():
    result = photon_zero_mode_wavefunction()
    assert result["radius_gev_inv"] > 0
    assert result["normalization_length_gev_inv"] > 0


def test_kk_roots_are_increasing():
    assert PHOTON_KK_ROOTS[1] > PHOTON_KK_ROOTS[0]
    assert PHOTON_KK_ROOTS[2] > PHOTON_KK_ROOTS[1]


def test_photon_kk_spectrum_returns_requested_number_of_modes():
    result = photon_kk_spectrum(n_modes=3)
    assert len(result["modes"]) == 3
    assert result["n_modes"] == 3


def test_first_kk_photon_mass_is_rs1_scale():
    result = photon_kk_spectrum(n_modes=1)
    first = result["first_mode_mass_gev"]
    assert 2000.0 < first < 3000.0


def test_first_mode_tracks_bessel_root():
    result = photon_kk_spectrum(n_modes=1)
    expected = PHOTON_KK_ROOTS[0] * M_KK_GEV
    assert result["first_mode_mass_gev"] == pytest.approx(expected, rel=1e-12)


def test_kk_masses_increase_with_mode_number():
    result = photon_kk_spectrum(n_modes=3)
    masses = [mode["m_n_gev"] for mode in result["modes"]]
    assert masses[1] > masses[0]
    assert masses[2] > masses[1]


def test_kk_bessel_coefficients_are_finite():
    result = photon_kk_spectrum(n_modes=3)
    for mode in result["modes"]:
        assert math.isfinite(mode["b_n"])
        assert math.isfinite(mode["ir_profile_unnormalized"])


def test_zero_mode_propagator_matches_inverse_p2():
    result = photon_propagator_zero_mode(10.0)
    assert result["value"] == pytest.approx(0.1, rel=1e-12)
    assert result["mass_pole_gev"] == 0.0


def test_zero_mode_propagator_has_massless_pole():
    result = photon_propagator_zero_mode(0.0)
    assert math.isinf(result["value"])


def test_negative_p2_raises():
    with pytest.raises(ValueError):
        photon_propagator_zero_mode(-1.0)


def test_cs_overlap_matches_large_warp_limit():
    result = cs_photon_overlap_integral()
    assert result["overlap_integral"] == pytest.approx(1.0 / (3.0 * PI_K_R), rel=1e-10)


def test_cs_overlap_value_is_expected_percent_level():
    result = cs_photon_overlap_integral()
    assert 0.008 < result["overlap_integral"] < 0.010


def test_beta_correction_factor_is_about_ten_percent():
    result = cs_photon_overlap_integral()
    assert 0.09 < result["beta_correction_factor"] < 0.10


def test_birefringence_correction_suppresses_beta():
    result = birefringence_warp_correction(0.302)
    assert result["beta_corrected_deg"] < result["beta_bare_deg"]
    assert 0.02 < result["beta_corrected_deg"] < 0.04


def test_negative_beta_raises():
    with pytest.raises(ValueError):
        birefringence_warp_correction(-0.1)


def test_custom_pi_kr_changes_overlap():
    default = cs_photon_overlap_integral()["overlap_integral"]
    larger = cs_photon_overlap_integral(pi_kr=40.0)["overlap_integral"]
    assert larger < default


def test_report_contains_all_subsections():
    report = photon_propagator_rs1_report()
    assert report["status"] == PILLAR_STATUS
    assert report["epistemic_status"] == "DERIVED"
    for key in ("zero_mode", "kk_spectrum", "cs_overlap", "beta_example"):
        assert key in report


def test_report_kk_correction_scale_positive():
    report = photon_propagator_rs1_report()
    scale = report["value"]["kk_correction_low_energy_scale_gev_minus2"]
    assert scale > 0
    assert scale < 1e-5
