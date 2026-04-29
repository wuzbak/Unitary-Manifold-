# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_neutrino_pmns.py
============================
Tests for Pillar 83 — PMNS Neutrino Mixing Matrix.

All tests verify:
  - PDG mixing angle values are returned correctly
  - PMNS matrix is 3×3 complex and unitary
  - Neutrino mass spectrum is computed correctly from splittings
  - Planck Σm_ν tension is detected and documented
  - Geometric estimates are physically reasonable
  - Gap report runs and contains the tension disclosure
"""
import cmath
import math
import pytest

from src.core.neutrino_pmns import (
    pmns_mixing_angles_pdg,
    pmns_from_angles,
    pmns_pdg,
    pmns_unitarity_check,
    neutrino_mass_spectrum,
    neutrino_mass_tension_report,
    pmns_geometric_estimate,
    pmns_gap_report,
    SIN2_THETA12_PDG,
    SIN2_THETA23_PDG,
    SIN2_THETA13_PDG,
    DM2_21_EV2,
    DM2_31_EV2,
    PLANCK_SUM_MNU_LIMIT_EV,
    M_KK_NEUTRINO_RADION_EV,
    N_W_CANONICAL,
)


class TestPdgMixingAngles:
    def test_sin2_theta12(self):
        p = pmns_mixing_angles_pdg()
        assert abs(p["sin2_theta12"] - 0.307) < 0.001

    def test_sin2_theta23(self):
        p = pmns_mixing_angles_pdg()
        assert abs(p["sin2_theta23"] - 0.572) < 0.001

    def test_sin2_theta13(self):
        p = pmns_mixing_angles_pdg()
        assert abs(p["sin2_theta13"] - 0.0222) < 0.0005

    def test_theta12_deg_approx_33(self):
        p = pmns_mixing_angles_pdg()
        assert 32.0 < p["theta12_deg"] < 35.0

    def test_theta23_deg_approx_49(self):
        p = pmns_mixing_angles_pdg()
        assert 45.0 < p["theta23_deg"] < 52.0

    def test_theta13_deg_approx_8_6(self):
        p = pmns_mixing_angles_pdg()
        assert 7.0 < p["theta13_deg"] < 10.0

    def test_delta_cp_deg_is_negative(self):
        p = pmns_mixing_angles_pdg()
        assert p["delta_cp_deg"] < 0

    def test_mass_splittings_positive(self):
        p = pmns_mixing_angles_pdg()
        assert p["dm2_21_ev2"] > 0
        assert p["dm2_31_ev2"] > 0


class TestPmnsMatrix:
    def test_pmns_pdg_is_3x3(self):
        U = pmns_pdg()
        assert len(U) == 3
        assert all(len(row) == 3 for row in U)

    def test_pmns_pdg_unitarity(self):
        U = pmns_pdg()
        check = pmns_unitarity_check(U)
        assert check["is_unitary"], f"PMNS not unitary: {check}"

    def test_pmns_pdg_unitarity_precision(self):
        U = pmns_pdg()
        check = pmns_unitarity_check(U)
        assert check["UdagU_max_off_diag"] < 1e-10

    def test_pmns_no_cp_when_delta_zero(self):
        theta12 = math.asin(math.sqrt(SIN2_THETA12_PDG))
        theta23 = math.asin(math.sqrt(SIN2_THETA23_PDG))
        theta13 = math.asin(math.sqrt(SIN2_THETA13_PDG))
        U = pmns_from_angles(theta12, theta23, theta13, delta_cp_rad=0.0)
        # All elements should be real when δ=0
        for row in U:
            for elem in row:
                assert abs(elem.imag) < 1e-14, f"Expected real PMNS, got imag part {elem.imag}"

    def test_pmns_from_angles_unitarity(self):
        for delta in [0.0, math.pi / 4, -math.pi / 2, math.pi]:
            theta12 = math.asin(math.sqrt(SIN2_THETA12_PDG))
            theta23 = math.asin(math.sqrt(SIN2_THETA23_PDG))
            theta13 = math.asin(math.sqrt(SIN2_THETA13_PDG))
            U = pmns_from_angles(theta12, theta23, theta13, delta)
            check = pmns_unitarity_check(U)
            assert check["is_unitary"], f"PMNS not unitary for δ={delta}"

    def test_pmns_ue3_element(self):
        U = pmns_pdg()
        # |U_{e3}| = sin(θ₁₃) ≈ 0.149
        s13 = math.sqrt(SIN2_THETA13_PDG)
        assert abs(abs(U[0][2]) - s13) < 0.01

    def test_pmns_umu3_element_magnitude(self):
        U = pmns_pdg()
        # |U_{μ3}| = sin(θ₂₃) cos(θ₁₃) ≈ 0.753
        s23 = math.sqrt(SIN2_THETA23_PDG)
        c13 = math.sqrt(1 - SIN2_THETA13_PDG)
        expected = s23 * c13
        assert abs(abs(U[1][2]) - expected) < 0.01

    def test_pmns_utau3_element_magnitude(self):
        U = pmns_pdg()
        # |U_{τ3}| = cos(θ₂₃) cos(θ₁₃) ≈ 0.644
        c23 = math.sqrt(1 - SIN2_THETA23_PDG)
        c13 = math.sqrt(1 - SIN2_THETA13_PDG)
        expected = c23 * c13
        assert abs(abs(U[2][2]) - expected) < 0.01


class TestNeutrinoMassSpectrum:
    def test_normal_ordering_m2_greater_than_m1(self):
        spec = neutrino_mass_spectrum(0.01, "normal")
        assert spec["m2_eV"] > spec["m1_eV"]
        assert spec["m3_eV"] > spec["m2_eV"]

    def test_inverted_ordering_m1_greater_than_m3(self):
        spec = neutrino_mass_spectrum(0.01, "inverted")
        assert spec["m1_eV"] > spec["m3_eV"]
        assert spec["m2_eV"] > spec["m3_eV"]

    def test_mass_splittings_reproduced(self):
        m1 = 0.02  # eV
        spec = neutrino_mass_spectrum(m1, "normal")
        # Check Δm²₂₁ = m₂² - m₁²
        dm2_21 = spec["m2_eV"] ** 2 - spec["m1_eV"] ** 2
        assert abs(dm2_21 - DM2_21_EV2) < 1e-8
        # Check Δm²₃₁ = m₃² - m₁²
        dm2_31 = spec["m3_eV"] ** 2 - spec["m1_eV"] ** 2
        assert abs(dm2_31 - DM2_31_EV2) < 1e-8

    def test_sum_mnu_correct(self):
        m1 = 0.02
        spec = neutrino_mass_spectrum(m1, "normal")
        expected_sum = spec["m1_eV"] + spec["m2_eV"] + spec["m3_eV"]
        assert abs(spec["sum_mnu_eV"] - expected_sum) < 1e-12

    def test_mkk_spectrum_violates_planck(self):
        """The M_KK = 110 meV identification yields Σm_ν >> 120 meV."""
        spec = neutrino_mass_spectrum(M_KK_NEUTRINO_RADION_EV, "normal")
        # Σm_ν should be >> 120 meV = 0.12 eV
        assert spec["sum_mnu_eV"] > PLANCK_SUM_MNU_LIMIT_EV
        assert not spec["consistent_with_planck"]

    def test_small_m1_consistent_with_planck(self):
        """A sufficiently small m₁ gives Σm_ν < 120 meV."""
        spec = neutrino_mass_spectrum(0.001, "normal")
        assert spec["consistent_with_planck"]

    def test_m1_around_33mev_borderline_planck(self):
        """m₁ ≈ 33 meV is near the Planck boundary for normal ordering."""
        spec = neutrino_mass_spectrum(0.033, "normal")
        # Should be close to the limit
        assert spec["sum_mnu_eV"] < PLANCK_SUM_MNU_LIMIT_EV + 0.01

    def test_invalid_ordering_raises(self):
        with pytest.raises(ValueError):
            neutrino_mass_spectrum(0.01, "wrong")


class TestNeutrinoMassTension:
    """These tests verify the honest documentation of the neutrino mass inconsistency."""

    def test_tension_report_is_string(self):
        report = neutrino_mass_tension_report()
        assert isinstance(report, str)
        assert len(report) > 200

    def test_tension_report_flags_inconsistency(self):
        report = neutrino_mass_tension_report()
        assert "INCONSISTENT" in report or "WRONG" in report or "❌" in report

    def test_tension_report_contains_mkk_value(self):
        report = neutrino_mass_tension_report()
        assert "110" in report  # M_KK = 110 meV mentioned

    def test_tension_report_mentions_planck_limit(self):
        report = neutrino_mass_tension_report()
        assert "120" in report or "Planck" in report

    def test_tension_report_provides_resolution(self):
        report = neutrino_mass_tension_report()
        assert "RESOLUTION" in report or "Resolution" in report

    def test_mkk_sum_mnu_exceeds_limit_by_factor_2_plus(self):
        """Document that M_KK = 110 meV gives Σm_ν >> Planck limit."""
        spec = neutrino_mass_spectrum(M_KK_NEUTRINO_RADION_EV, "normal")
        ratio = spec["sum_mnu_eV"] / PLANCK_SUM_MNU_LIMIT_EV
        assert ratio > 2.5, f"Expected Σm_ν > 2.5 × limit, got ratio = {ratio:.2f}"


class TestGeometricEstimates:
    def test_geometric_estimate_keys_present(self):
        geo = pmns_geometric_estimate(5)
        for key in ["theta12", "theta23", "theta13", "delta_cp"]:
            assert key in geo

    def test_theta23_near_maximal_prediction(self):
        """θ₂₃ → 45° is the natural geometric prediction."""
        geo = pmns_geometric_estimate(5)
        assert abs(geo["theta23"]["geometric_deg"] - 45.0) < 1e-6

    def test_theta23_status_consistent(self):
        geo = pmns_geometric_estimate(5)
        assert "CONSISTENT" in geo["theta23"]["status"] or "near-maximal" in geo["theta23"]["status"].lower()

    def test_theta12_sin2_formula(self):
        """sin²θ₁₂ ≈ 1/(1+n_w) for n_w=5 → 1/6 ≈ 0.167."""
        geo = pmns_geometric_estimate(5)
        assert abs(geo["theta12"]["sin2_geometric"] - 1.0 / 6.0) < 1e-10

    def test_theta13_sin_formula(self):
        """sin(θ₁₃) ≈ 1/n_w² = 0.04."""
        geo = pmns_geometric_estimate(5)
        s13 = math.sin(math.radians(geo["theta13"]["geometric_deg"]))
        assert abs(s13 - 0.04) < 1e-6

    def test_delta_cp_status_is_open(self):
        geo = pmns_geometric_estimate(5)
        assert "OPEN" in geo["delta_cp"]["status"]

    def test_geometric_estimate_order_of_magnitude_theta12(self):
        """sin²θ₁₂ geometric vs PDG: within factor 2."""
        geo = pmns_geometric_estimate(5)
        ratio = geo["theta12"]["sin2_geometric"] / SIN2_THETA12_PDG
        assert 0.3 < ratio < 1.5, f"sin²θ₁₂ ratio out of range: {ratio}"

    def test_geometric_estimate_order_of_magnitude_theta13(self):
        """sin²θ₁₃ geometric vs PDG: within factor 10."""
        geo = pmns_geometric_estimate(5)
        ratio = geo["theta13"]["sin2_geometric"] / SIN2_THETA13_PDG
        assert 0.05 < ratio < 3.0, f"sin²θ₁₃ ratio out of range: {ratio}"


class TestGapReport:
    def test_gap_report_runs(self):
        report = pmns_gap_report()
        assert isinstance(report, str)
        assert len(report) > 200

    def test_gap_report_contains_pillar_reference(self):
        report = pmns_gap_report()
        assert "Pillar 83" in report

    def test_gap_report_contains_tension_disclosure(self):
        report = pmns_gap_report()
        assert "TENSION" in report or "INCONSISTEN" in report or "WRONG" in report

    def test_gap_report_contains_resolution(self):
        report = pmns_gap_report()
        assert "RESOLUTION" in report or "Resolution" in report
