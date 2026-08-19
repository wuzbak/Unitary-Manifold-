# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

from __future__ import annotations

import math

import pytest

from src.core.hopf_dirac_pmns import (
    EPISTEMIC_STATUS,
    HOPF_CHARGE,
    HOPF_LINKING_NUMBER,
    K_CS,
    N1,
    N2,
    PILLAR_NUMBER,
    STATUS,
    cp_phase_hopf_holonomy,
    dirac_eigenvalues_hopf,
    generation_mass_hierarchy_hopf,
    hopf_connection_1form,
    hopf_dirac_pmns_report,
    hopf_winding_pmns_angles,
    index_theorem_hopf,
)


class TestMetadata:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 778

    def test_status(self):
        assert STATUS == "HOPF_DIRAC_PMNS_CONSTRAINED"

    def test_epistemic_status(self):
        assert EPISTEMIC_STATUS == "CONSTRAINED"

    def test_braid_constants(self):
        assert (N1, N2, K_CS) == (5, 7, 74)
        assert HOPF_LINKING_NUMBER == 35
        assert HOPF_CHARGE == pytest.approx(35 / 74)


class TestHopfConnection:
    def test_connection_coefficients_sum_to_one(self):
        r = hopf_connection_1form()
        coeffs = r["coefficients"]
        assert coeffs["dphi1"] + coeffs["dphi2"] == pytest.approx(1.0)

    def test_connection_linking_number(self):
        r = hopf_connection_1form()
        assert r["hopf_linking_number"] == 35

    def test_connection_meta_keys_present(self):
        r = hopf_connection_1form()
        assert "status" in r and "epistemic_status" in r


class TestDiracSpectrum:
    def test_invalid_mode_count_raises(self):
        with pytest.raises(ValueError):
            dirac_eigenvalues_hopf(0)

    def test_lightest_mode_matches_73_over_37(self):
        r = dirac_eigenvalues_hopf(3)
        assert r["lightest_abs_eigenvalue"] == pytest.approx(73 / 37)

    def test_modes_are_symmetric(self):
        r = dirac_eigenvalues_hopf(4)
        for mode in r["modes"]:
            assert mode["modified_positive"] == pytest.approx(-mode["modified_negative"])

    def test_no_zero_mode_in_shifted_list(self):
        r = dirac_eigenvalues_hopf()
        assert r["zero_mode_present"] is False


class TestPMNSAngles:
    def test_theta12_exact_fraction(self):
        r = hopf_winding_pmns_angles()
        assert r["sin2_theta12"] == pytest.approx(3 / 10)

    def test_theta23_exact_fraction(self):
        r = hopf_winding_pmns_angles()
        assert r["sin2_theta23"] == pytest.approx(20 / 37)

    def test_theta13_exact_fraction(self):
        r = hopf_winding_pmns_angles()
        assert r["sin2_theta13"] == pytest.approx(1 / 48)

    def test_angle_ordering(self):
        r = hopf_winding_pmns_angles()
        assert r["theta23_deg"] > r["theta12_deg"] > r["theta13_deg"]


class TestCPPhase:
    def test_cp_phase_formula(self):
        r = cp_phase_hopf_holonomy()
        assert r["delta_cp_rad"] == pytest.approx(2 * math.pi * 35 / 74)

    def test_cp_phase_degree_value(self):
        r = cp_phase_hopf_holonomy()
        assert r["delta_cp_deg"] == pytest.approx(360 * 35 / 74)

    def test_cp_phase_residual_within_30pct(self):
        r = cp_phase_hopf_holonomy()
        assert r["residual_pct_vs_best_fit"] < 30.0


class TestGenerationHierarchy:
    def test_hierarchy_normalization(self):
        r = generation_mass_hierarchy_hopf()
        assert r["normalized_hierarchy"][0] == pytest.approx(1.0)

    def test_hierarchy_is_increasing(self):
        r = generation_mass_hierarchy_hopf()
        h = r["normalized_hierarchy"]
        assert h[0] < h[1] < h[2]

    def test_optional_mass_scale(self):
        r = generation_mass_hierarchy_hopf(m_kk_gev=1000.0)
        assert r["masses_gev"] is not None
        assert len(r["masses_gev"]) == 3


class TestIndexAndReport:
    def test_index_equals_linking_number(self):
        r = index_theorem_hopf()
        assert r["dirac_index"] == 35
        assert r["heavy_modes_decoupled"] == 32

    def test_report_contains_all_sections(self):
        r = hopf_dirac_pmns_report()
        for key in ["connection", "spectrum", "angles", "cp_phase", "generation_hierarchy", "index_theorem"]:
            assert key in r

    def test_report_meta_keys_present(self):
        r = hopf_dirac_pmns_report()
        assert r["status"] == STATUS
        assert r["epistemic_status"] == EPISTEMIC_STATUS
