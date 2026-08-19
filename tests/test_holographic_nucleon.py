# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

import math

import pytest

from src.holography.holographic_nucleon import (
    clat_holographic_estimate,
    holographic_nucleon_mass,
    holographic_nucleon_report,
    nucleon_coupling_thooft,
    proton_regge_trajectory,
    skyrmion_size_rs1,
)


def test_skyrmion_size_is_positive():
    result = skyrmion_size_rs1()
    assert result["skyrmion_radius_gev_inverse"] > 0.0
    assert result["skyrmion_radius_fm"] > 0.0


def test_skyrmion_size_is_small_in_fm_units():
    result = skyrmion_size_rs1()
    assert result["skyrmion_radius_fm"] < 1e-3


def test_skyrmion_size_rejects_nonpositive_pi_kr():
    with pytest.raises(ValueError):
        skyrmion_size_rs1(pi_kr=0.0)


def test_thooft_coupling_matches_input_formula():
    result = nucleon_coupling_thooft()
    expected = 3.0 * 4.0 * math.pi / 7.5
    assert math.isclose(result["thooft_lambda"], expected, rel_tol=1e-12)


def test_thooft_coupling_is_moderate():
    result = nucleon_coupling_thooft()
    assert 4.0 < result["thooft_lambda"] < 6.0


def test_thooft_coupling_rejects_nonpositive_nc():
    with pytest.raises(ValueError):
        nucleon_coupling_thooft(n_c=0)


def test_holographic_proton_mass_is_in_expected_range():
    result = holographic_nucleon_mass()
    assert 1.0 < result["m_p_holographic_gev"] < 1.2


def test_holographic_proton_mass_fractional_error_is_about_twenty_percent():
    result = holographic_nucleon_mass()
    assert 0.15 < result["fractional_error_vs_pdg"] < 0.25


def test_holographic_proton_mass_rejects_bad_intercept():
    with pytest.raises(ValueError):
        holographic_nucleon_mass(n0_intercept=-1.0)


def test_clat_estimate_lies_inside_claimed_window():
    result = clat_holographic_estimate()
    assert result["lies_in_claimed_window"] is True


def test_clat_estimate_is_near_five():
    result = clat_holographic_estimate()
    assert 4.8 < result["c_lat_holographic"] < 5.5


def test_clat_rejects_bad_winding():
    with pytest.raises(ValueError):
        clat_holographic_estimate(n_w=0)


def test_regge_trajectory_has_requested_levels():
    result = proton_regge_trajectory(n_max=4)
    assert len(result["trajectory"]) == 4


def test_regge_trajectory_masses_increase_with_n():
    result = proton_regge_trajectory(n_max=4)
    masses = [level["mass_gev"] for level in result["trajectory"]]
    assert masses == sorted(masses)


def test_regge_trajectory_rejects_nonpositive_nmax():
    with pytest.raises(ValueError):
        proton_regge_trajectory(n_max=0)


def test_report_contains_all_sections():
    report = holographic_nucleon_report()
    for key in ["skyrmion_size", "nucleon_mass", "c_lat", "regge_trajectory", "thooft_coupling"]:
        assert key in report
    assert report["status"] == "PARTIAL"


def test_report_preserves_epistemic_status():
    report = holographic_nucleon_report()
    assert report["epistemic_status"] == "C_LAT_HOLOGRAPHIC_PARTIAL"


def test_all_public_calls_include_status_and_epistemic_status():
    payloads = [
        skyrmion_size_rs1(),
        holographic_nucleon_mass(),
        clat_holographic_estimate(),
        proton_regge_trajectory(),
        nucleon_coupling_thooft(),
        holographic_nucleon_report(),
    ]
    for payload in payloads:
        assert "status" in payload
        assert "epistemic_status" in payload
