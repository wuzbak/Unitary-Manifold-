# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_neutrino_pmns.py
============================
Tests for Pillar 83 — PMNS Neutrino Mixing Matrix (v9.21 updated formulas).
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
        for row in U:
            for elem in row:
                assert abs(elem.imag) < 1e-14

    def test_pmns_from_angles_unitarity(self):
        for delta in [0.0, math.pi / 4, -math.pi / 2, math.pi]:
            theta12 = math.asin(math.sqrt(SIN2_THETA12_PDG))
            theta23 = math.asin(math.sqrt(SIN2_THETA23_PDG))
            theta13 = math.asin(math.sqrt(SIN2_THETA13_PDG))
            U = pmns_from_angles(theta12, theta23, theta13, delta)
            check = pmns_unitarity_check(U)
            assert check["is_unitary"]

    def test_pmns_ue3_element(self):
        U = pmns_pdg()
        s13 = math.sqrt(SIN2_THETA13_PDG)
        assert abs(abs(U[0][2]) - s13) < 0.01

    def test_pmns_umu3_element_magnitude(self):
        U = pmns_pdg()
        s23 = math.sqrt(SIN2_THETA23_PDG)
        c13 = math.sqrt(1 - SIN2_THETA13_PDG)
        expected = s23 * c13
        assert abs(abs(U[1][2]) - expected) < 0.01

    def test_pmns_utau3_element_magnitude(self):
        U = pmns_pdg()
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
        m1 = 0.02
        spec = neutrino_mass_spectrum(m1, "normal")
        dm2_21 = spec["m2_eV"] ** 2 - spec["m1_eV"] ** 2
        assert abs(dm2_21 - DM2_21_EV2) < 1e-8
        dm2_31 = spec["m3_eV"] ** 2 - spec["m1_eV"] ** 2
        assert abs(dm2_31 - DM2_31_EV2) < 1e-8

    def test_sum_mnu_correct(self):
        m1 = 0.02
        spec = neutrino_mass_spectrum(m1, "normal")
        expected_sum = spec["m1_eV"] + spec["m2_eV"] + spec["m3_eV"]
        assert abs(spec["sum_mnu_eV"] - expected_sum) < 1e-12

    def test_mkk_spectrum_violates_planck(self):
        spec = neutrino_mass_spectrum(M_KK_NEUTRINO_RADION_EV, "normal")
        assert spec["sum_mnu_eV"] > PLANCK_SUM_MNU_LIMIT_EV
        assert not spec["consistent_with_planck"]

    def test_small_m1_consistent_with_planck(self):
        spec = neutrino_mass_spectrum(0.001, "normal")
        assert spec["consistent_with_planck"]

    def test_m1_around_33mev_borderline_planck(self):
        spec = neutrino_mass_spectrum(0.033, "normal")
        assert spec["sum_mnu_eV"] < PLANCK_SUM_MNU_LIMIT_EV + 0.01

    def test_invalid_ordering_raises(self):
        with pytest.raises(ValueError):
            neutrino_mass_spectrum(0.01, "wrong")


class TestNeutrinoMassTension:
    def test_tension_report_is_string(self):
        report = neutrino_mass_tension_report()
        assert isinstance(report, str)
        assert len(report) > 200

    def test_tension_report_flags_inconsistency(self):
        report = neutrino_mass_tension_report()
        assert "INCONSISTENT" in report or "WRONG" in report or "CORRECTED" in report or "RESOLVED" in report

    def test_tension_report_contains_mkk_value(self):
        report = neutrino_mass_tension_report()
        assert "110" in report

    def test_tension_report_mentions_planck_limit(self):
        report = neutrino_mass_tension_report()
        assert "120" in report or "Planck" in report

    def test_tension_report_provides_resolution(self):
        report = neutrino_mass_tension_report()
        assert "RESOLUTION" in report or "Resolution" in report

    def test_mkk_sum_mnu_exceeds_limit_by_factor_2_plus(self):
        spec = neutrino_mass_spectrum(M_KK_NEUTRINO_RADION_EV, "normal")
        ratio = spec["sum_mnu_eV"] / PLANCK_SUM_MNU_LIMIT_EV
        assert ratio > 2.5


class TestGeometricEstimates:
    def test_geometric_estimate_keys_present(self):
        geo = pmns_geometric_estimate(5)
        for key in ["theta12", "theta23", "theta13", "delta_cp"]:
            assert key in geo

    def test_theta23_near_maximal_prediction(self):
        """sin2 theta23 = 29/50 from democratic TBM + second-order winding."""
        geo = pmns_geometric_estimate(5)
        expected_sin2 = 29.0 / 50.0
        assert abs(geo["theta23"]["sin2_geometric"] - expected_sin2) < 1e-10
        pdg_theta23 = math.degrees(math.asin(math.sqrt(SIN2_THETA23_PDG)))
        assert abs(geo["theta23"]["geometric_deg"] - pdg_theta23) < 1.0

    def test_theta23_status_consistent(self):
        geo = pmns_geometric_estimate(5)
        assert "CONSISTENT" in geo["theta23"]["status"] or "near-maximal" in geo["theta23"]["status"].lower()

    def test_theta12_sin2_formula(self):
        """sin2 theta12 uses second-order correction formula for n_w=5:
        sin²θ₁₂ = (n_w-1)(4n_w+3)/(12n_w²) = 4×23/300 = 92/300."""
        geo = pmns_geometric_estimate(5)
        expected = (5 - 1) * (4 * 5 + 3) / (12.0 * 5 ** 2)  # = 92/300
        assert abs(geo["theta12"]["sin2_geometric"] - expected) < 1e-10
        # Status should reflect the closure
        assert "CLOSED" in geo["theta12"]["status"]

    def test_theta13_sin2_formula(self):
        """sin2 theta13 = 1/(2n_w^2) = 1/50 for n_w=5."""
        geo = pmns_geometric_estimate(5)
        expected_sin2 = 1.0 / (2.0 * 5**2)
        assert abs(geo["theta13"]["sin2_geometric"] - expected_sin2) < 1e-10

    def test_delta_cp_status_is_closed(self):
        """delta_CP^PMNS = -108 deg is CLOSED by Pillar 86."""
        geo = pmns_geometric_estimate(5)
        status = geo["delta_cp"]["status"]
        assert "CLOSED" in status

    def test_geometric_estimate_order_of_magnitude_theta12(self):
        geo = pmns_geometric_estimate(5)
        ratio = geo["theta12"]["sin2_geometric"] / SIN2_THETA12_PDG
        assert 0.3 < ratio < 1.5

    def test_geometric_estimate_order_of_magnitude_theta13(self):
        geo = pmns_geometric_estimate(5)
        ratio = geo["theta13"]["sin2_geometric"] / SIN2_THETA13_PDG
        assert 0.05 < ratio < 3.0


class TestGapReport:
    def test_gap_report_runs(self):
        report = pmns_gap_report()
        assert isinstance(report, str)
        assert len(report) > 200

    def test_gap_report_contains_pillar_reference(self):
        report = pmns_gap_report()
        assert "Pillar 83" in report or "83" in report

    def test_gap_report_contains_tension_disclosure(self):
        report = pmns_gap_report()
        assert "TENSION" in report or "INCONSISTEN" in report or "WRONG" in report or "OPEN" in report

    def test_gap_report_contains_resolution(self):
        report = pmns_gap_report()
        assert "RESOLUTION" in report or "Resolution" in report or "CLOSED" in report


# ---------------------------------------------------------------------------
# TestNeutrinoSplittingsFromGeometry  (new function, Pillar 90 v9.23)
# ---------------------------------------------------------------------------

class TestNeutrinoSplittingsFromGeometry:
    """Tests for neutrino_splittings_from_geometry() — mass-squared splittings
    derived from the (n₁, n₂) = (5, 7) braid geometry."""

    def setup_method(self):
        from src.core.neutrino_pmns import neutrino_splittings_from_geometry
        self.res = neutrino_splittings_from_geometry()

    def test_returns_dict(self):
        assert isinstance(self.res, dict)

    def test_braid_product_is_35(self):
        assert self.res["braid_product_n1_n2"] == 35

    def test_dm2_21_geo_matches_pdg_constant(self):
        from src.core.neutrino_pmns import DM2_21_EV2
        assert abs(self.res["dm2_21_geo_eV2"] - DM2_21_EV2) < 1e-20

    def test_dm2_ratio_is_36(self):
        # Ratio = n₁n₂ + 1 = 35 + 1 = 36
        assert abs(self.res["dm2_ratio_geo"] - 36.0) < 1e-10

    def test_dm2_31_pct_err_below_15(self):
        assert self.res["dm2_31_pct_err"] < 15.0

    def test_sum_mnu_within_planck_limit(self):
        assert self.res["planck_consistent"] is True

    def test_mass_ratio_r_equals_sqrt35(self):
        expected = math.sqrt(35)
        assert abs(self.res["mass_ratio_r"] - expected) < 1e-10

    def test_masses_ordered_normal_hierarchy(self):
        assert self.res["m_nu1_eV"] < self.res["m_nu2_eV"] < self.res["m_nu3_eV"]

    def test_status_string_nonempty(self):
        assert len(self.res["status"]) > 20

    def test_derivation_string_nonempty(self):
        assert len(self.res["derivation"]) > 20
