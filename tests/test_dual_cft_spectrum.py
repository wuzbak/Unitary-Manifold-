# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

import math

import pytest

from src.holography.dual_cft_spectrum import (
    cft_central_charge,
    cs_anomaly_coefficient,
    cs_field_to_cft_current,
    dual_cft_spectrum_report,
    gauge_field_to_cft_currents,
    graviton_to_cft_stresstensor,
    kk_tower_to_cft_operators,
    radion_to_cft_lagrangian_density,
)


def test_graviton_mapping_dimension_is_four():
    result = graviton_to_cft_stresstensor()
    assert result["status"] == "DERIVED"
    assert result["epistemic_status"] == "DUAL_CFT_SPECTRUM_SCAFFOLD"
    assert result["conformal_dimension"] == 4.0


def test_graviton_mapping_operator_name_mentions_stress_tensor():
    result = graviton_to_cft_stresstensor()
    assert "stress tensor" in result["cft_operator"]


def test_kk_tower_contains_requested_number_of_levels():
    result = kk_tower_to_cft_operators(n_max=4)
    assert result["n_max"] == 4
    assert len(result["operator_levels"]) == 4


def test_kk_tower_dimensions_step_by_two():
    result = kk_tower_to_cft_operators(n_max=3)
    dims = [level["conformal_dimension"] for level in result["operator_levels"]]
    assert dims == [6.0, 8.0, 10.0]


def test_kk_tower_masses_are_monotone():
    result = kk_tower_to_cft_operators(n_max=5)
    masses = [level["bulk_mass_gev"] for level in result["operator_levels"]]
    assert masses == sorted(masses)


def test_kk_tower_rejects_nonpositive_nmax():
    with pytest.raises(ValueError):
        kk_tower_to_cft_operators(n_max=0)


def test_radion_operator_has_dimension_four():
    result = radion_to_cft_lagrangian_density()
    assert result["conformal_dimension"] == 4.0
    assert result["status"] == "CONSTRAINED"


def test_radion_mass_reference_tracks_mkk():
    result = radion_to_cft_lagrangian_density()
    assert math.isclose(result["radion_mass_reference_gev"], result["m_kk_gev"], rel_tol=1e-12)


def test_cs_current_dimension_is_three():
    result = cs_field_to_cft_current()
    assert result["conformal_dimension"] == 3.0


def test_cs_current_coefficient_matches_formula():
    result = cs_field_to_cft_current(k_cs=74)
    expected = 74.0 / (2.0 * math.pi**2)
    assert math.isclose(result["anomaly_coefficient_current_normalization"], expected, rel_tol=1e-12)


def test_gauge_currents_cover_three_sm_groups():
    result = gauge_field_to_cft_currents()
    groups = {item["group"] for item in result["currents"]}
    assert groups == {"SU(3)_c", "SU(2)_L", "U(1)_Y"}


def test_fermion_sector_dimensions_match_requested_values():
    result = gauge_field_to_cft_currents()
    sector = result["fermionic_operator_sector"]
    assert sector["light_quark_conformal_dimension"] == 2.5
    assert sector["top_quark_conformal_dimension"] == 2.0


def test_central_charge_is_close_to_inverse_kcs():
    result = cft_central_charge()
    assert math.isclose(result["c_cft_reduced"], 1.0 / 74.0, rel_tol=1e-12)


def test_central_charge_direct_and_reduced_forms_agree():
    result = cft_central_charge()
    assert math.isclose(result["c_cft_direct"], result["c_cft_reduced"], rel_tol=1e-12)


def test_cs_anomaly_matches_ward_identity_coefficient():
    result = cs_anomaly_coefficient()
    expected = 74.0 / (16.0 * math.pi**2)
    assert math.isclose(result["axial_ward_identity_coefficient"], expected, rel_tol=1e-12)


def test_cs_anomaly_requires_positive_level():
    with pytest.raises(ValueError):
        cs_anomaly_coefficient(k_cs=0)


def test_report_contains_all_sections():
    report = dual_cft_spectrum_report()
    for key in ["graviton_sector", "kk_sector", "radion_sector", "cs_sector", "gauge_sector", "central_charge", "anomaly"]:
        assert key in report
    assert report["status"] == "SCAFFOLD"


def test_all_public_calls_include_status_and_epistemic_status():
    payloads = [
        graviton_to_cft_stresstensor(),
        kk_tower_to_cft_operators(),
        radion_to_cft_lagrangian_density(),
        cs_field_to_cft_current(),
        gauge_field_to_cft_currents(),
        cft_central_charge(),
        cs_anomaly_coefficient(),
        dual_cft_spectrum_report(),
    ]
    for payload in payloads:
        assert "status" in payload
        assert "epistemic_status" in payload
