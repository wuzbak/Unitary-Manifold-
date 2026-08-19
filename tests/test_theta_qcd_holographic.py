# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

import math

import pytest

from src.holography.theta_qcd_holographic import (
    THETA_EXPERIMENTAL_BOUND,
    holographic_theta_boundary_value,
    holographic_vs_pq_comparison,
    no_light_axion_proof,
    radiative_theta_correction,
    theta_qcd_holographic_report,
    z2_parity_a5,
)


def test_z2_parity_is_odd():
    result = z2_parity_a5()
    assert result["z2_parity"] == "odd"


def test_z2_parity_sets_both_boundaries_to_zero():
    result = z2_parity_a5()
    assert result["uv_boundary_value"] == 0.0
    assert result["ir_boundary_value"] == 0.0


def test_z2_parity_rejects_bad_pi_kr():
    with pytest.raises(ValueError):
        z2_parity_a5(pi_kr=0.0)


def test_theta_boundary_value_is_exactly_zero():
    result = holographic_theta_boundary_value()
    assert result["theta_qcd"] == 0.0


def test_theta_boundary_formula_mentions_a5():
    result = holographic_theta_boundary_value()
    assert "A_5" in result["formula"]


def test_theta_boundary_rejects_bad_kcs():
    with pytest.raises(ValueError):
        holographic_theta_boundary_value(k_cs=0)


def test_radiative_theta_bound_is_tiny():
    result = radiative_theta_correction()
    assert result["delta_theta_upper_bound"] < 1e-30


def test_radiative_theta_is_below_experimental_bound():
    result = radiative_theta_correction()
    assert result["delta_theta_upper_bound"] < THETA_EXPERIMENTAL_BOUND
    assert result["satisfies_experimental_bound"] is True


def test_radiative_theta_rejects_bad_alpha_s():
    with pytest.raises(ValueError):
        radiative_theta_correction(alpha_s=0.0)


def test_no_light_axion_statement_is_negative():
    result = no_light_axion_proof()
    assert result["has_a5_zero_mode"] is False


def test_no_light_axion_first_mode_is_at_kk_scale():
    result = no_light_axion_proof()
    assert result["lightest_kk_mode_mass_gev"] > 1000.0


def test_comparison_says_holographic_route_needs_no_pq_symmetry():
    result = holographic_vs_pq_comparison()
    assert result["holographic_mechanism"]["requires_pq_symmetry"] is False
    assert result["pq_reference_mechanism"]["requires_pq_symmetry"] is True


def test_comparison_tracks_light_axion_difference():
    result = holographic_vs_pq_comparison()
    assert result["holographic_mechanism"]["light_axion_present"] is False
    assert result["pq_reference_mechanism"]["light_axion_present"] is True


def test_report_contains_all_sections():
    report = theta_qcd_holographic_report()
    for key in ["z2_parity", "theta_boundary", "radiative_correction", "axion_sector", "comparison"]:
        assert key in report


def test_report_uses_derived_status():
    report = theta_qcd_holographic_report()
    assert report["status"] == "DERIVED"
    assert report["epistemic_status"] == "THETA_QCD_HOLOGRAPHIC_DERIVED"


def test_all_public_calls_include_status_and_epistemic_status():
    payloads = [
        z2_parity_a5(),
        holographic_theta_boundary_value(),
        radiative_theta_correction(),
        no_light_axion_proof(),
        holographic_vs_pq_comparison(),
        theta_qcd_holographic_report(),
    ]
    for payload in payloads:
        assert "status" in payload
        assert "epistemic_status" in payload


def test_naive_loop_estimate_exceeds_stronger_parity_bound():
    result = radiative_theta_correction()
    assert result["naive_one_loop_prefactor_estimate"] > result["delta_theta_upper_bound"]
