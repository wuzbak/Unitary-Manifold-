# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_fermion_cl_quantization.py
=======================================
Tests for Pillar 183 — Geometric Quantization of c_L from the UM Braid Spectrum.
(src/core/fermion_cl_quantization.py)

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations
import math
import pytest

from src.core.fermion_cl_quantization import (
    # Constants
    N_W, K_CS, PI_KR, N1, N2, C_S_BRAIDED, C_L_CRITICAL, BRAID_RESONANCE_WINDOW,
    # Functions
    z2_localisation_class,
    top_yukawa_cl_constraint,
    electron_hierarchy_cl_constraint,
    braid_resonance_cl_window,
    cl_constraints_from_braid,
    fermion_mass_parameterization_audit,
    pillar183_summary,
)


# ===========================================================================
# Module constants
# ===========================================================================

class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0, rel=1e-9)

    def test_n1_n2(self):
        assert N1 == 5
        assert N2 == 7

    def test_c_s_braided_value(self):
        # c_s = (49 - 25) / 74 = 24/74 = 12/37
        expected = 24.0 / 74.0
        assert C_S_BRAIDED == pytest.approx(expected, rel=1e-9)

    def test_c_s_equals_12_over_37(self):
        assert C_S_BRAIDED == pytest.approx(12.0 / 37.0, rel=1e-9)

    def test_c_l_critical(self):
        assert C_L_CRITICAL == pytest.approx(0.5, rel=1e-9)

    def test_braid_resonance_window(self):
        # n1/(n1+n2) = 5/12
        expected = 5.0 / 12.0
        assert BRAID_RESONANCE_WINDOW == pytest.approx(expected, rel=1e-9)

    def test_resonance_window_less_than_critical(self):
        assert BRAID_RESONANCE_WINDOW < C_L_CRITICAL


# ===========================================================================
# z2_localisation_class
# ===========================================================================

class TestZ2LocalisationClass:
    def test_uv_localised_above_half(self):
        result = z2_localisation_class(0.7)
        assert result["class_name"] == "UV-LOCALISED"
        assert result["is_uv"] is True
        assert result["is_ir"] is False
        assert result["is_critical"] is False

    def test_ir_localised_below_half(self):
        result = z2_localisation_class(0.3)
        assert result["class_name"] == "IR-LOCALISED"
        assert result["is_ir"] is True
        assert result["is_uv"] is False
        assert result["is_critical"] is False

    def test_critical_at_half(self):
        result = z2_localisation_class(0.5)
        assert result["class_name"] == "CRITICAL"
        assert result["is_critical"] is True
        assert result["is_uv"] is False
        assert result["is_ir"] is False

    def test_returns_c_l(self):
        result = z2_localisation_class(0.63)
        assert result["c_l"] == pytest.approx(0.63)

    def test_derivation_status_present(self):
        result = z2_localisation_class(0.5)
        assert "DERIVED" in result["derivation_status"]

    def test_uv_yukawa_suppression_contains_exp(self):
        result = z2_localisation_class(0.7)
        assert "exp" in result["yukawa_suppression"].lower()

    def test_ir_yukawa_suppression_contains_order_1(self):
        result = z2_localisation_class(0.1)
        assert "1" in result["yukawa_suppression"]


# ===========================================================================
# top_yukawa_cl_constraint
# ===========================================================================

class TestTopYukawaConstraint:
    def test_fermion_name(self):
        result = top_yukawa_cl_constraint()
        assert "top" in result["fermion"].lower()

    def test_ir_localised(self):
        result = top_yukawa_cl_constraint()
        assert result["is_ir_localised"] is True

    def test_c_l_below_half(self):
        result = top_yukawa_cl_constraint()
        assert result["c_l_estimate"] < 0.5

    def test_c_r_canonical(self):
        result = top_yukawa_cl_constraint()
        assert result["c_r_canonical"] == pytest.approx(0.920, rel=1e-6)

    def test_status_contains_constrained(self):
        result = top_yukawa_cl_constraint()
        assert "CONSTRAINED" in result["status"].upper()

    def test_what_is_derived(self):
        result = top_yukawa_cl_constraint()
        assert "IR" in result["what_is_derived"]


# ===========================================================================
# electron_hierarchy_cl_constraint
# ===========================================================================

class TestElectronHierarchyConstraint:
    def test_fermion_name(self):
        result = electron_hierarchy_cl_constraint()
        assert "electron" in result["fermion"].lower()

    def test_more_uv_than_top(self):
        """Electron c_L must be larger (more UV) than top c_L."""
        result = electron_hierarchy_cl_constraint()
        assert result["is_more_uv_than_top"] is True

    def test_delta_cl_positive(self):
        result = electron_hierarchy_cl_constraint()
        assert result["delta_cl"] > 0.0

    def test_c_l_electron_larger_than_top(self):
        result = electron_hierarchy_cl_constraint()
        assert result["c_l_electron_estimate_fixed_cr"] > result["c_l_top_estimate"]

    def test_mass_ratio_correct_order(self):
        result = electron_hierarchy_cl_constraint()
        # m_e / m_t ~ 3e-6
        assert result["mass_ratio_e_to_t"] < 1e-4
        assert result["mass_ratio_e_to_t"] > 1e-8

    def test_status_contains_constrained(self):
        result = electron_hierarchy_cl_constraint()
        assert "CONSTRAINED" in result["status"].upper()

    def test_fitted_value_from_pillar174_uv(self):
        """Fitted value from Pillar 174 should give UV-localised electron."""
        result = electron_hierarchy_cl_constraint()
        assert result["c_l_electron_fitted_pillar174"] > 0.5
        assert result["localisation_class_fitted"] == "UV-LOCALISED"


# ===========================================================================
# braid_resonance_cl_window
# ===========================================================================

class TestBraidResonanceWindow:
    def test_n1_n2(self):
        result = braid_resonance_cl_window()
        assert result["n1"] == 5
        assert result["n2"] == 7

    def test_k_cs(self):
        result = braid_resonance_cl_window()
        assert result["k_cs"] == 74

    def test_c_s_braided(self):
        result = braid_resonance_cl_window()
        assert result["c_s_braided"] == pytest.approx(12.0 / 37.0, rel=1e-9)

    def test_three_zones_present(self):
        result = braid_resonance_cl_window()
        zones = result["zones"]
        assert "zone_1_deep_ir" in zones
        assert "zone_2_transition" in zones
        assert "zone_3_uv_suppression" in zones

    def test_top_in_zone_1(self):
        result = braid_resonance_cl_window()
        assert "top" in " ".join(result["zones"]["zone_1_deep_ir"]["expected_fermions"]).lower()

    def test_braid_resonance_scale(self):
        result = braid_resonance_cl_window()
        assert result["braid_resonance_scale"] == pytest.approx(5.0 / 12.0, rel=1e-9)

    def test_status_constrained(self):
        result = braid_resonance_cl_window()
        assert "CONSTRAINED" in result["derivation_status"].upper()


# ===========================================================================
# cl_constraints_from_braid
# ===========================================================================

class TestCLConstraintsFromBraid:
    def test_returns_dict(self):
        result = cl_constraints_from_braid()
        assert isinstance(result, dict)

    def test_4_derived_constraints(self):
        result = cl_constraints_from_braid()
        assert result["n_derived_constraints"] == 4

    def test_9_remaining_free(self):
        result = cl_constraints_from_braid()
        assert result["n_remaining_free"] == 9

    def test_overall_status(self):
        result = cl_constraints_from_braid()
        assert result["overall_status"] == "PARAMETERIZED-CONSTRAINED"

    def test_derived_constraints_list_non_empty(self):
        result = cl_constraints_from_braid()
        assert len(result["derived_constraints"]) > 0

    def test_honest_summary_present(self):
        result = cl_constraints_from_braid()
        assert "honest_summary" in result
        assert len(result["honest_summary"]) > 10


# ===========================================================================
# fermion_mass_parameterization_audit
# ===========================================================================

class TestFermionMassParameterizationAudit:
    def test_returns_dict(self):
        result = fermion_mass_parameterization_audit()
        assert isinstance(result, dict)

    def test_pillar_183(self):
        result = fermion_mass_parameterization_audit()
        assert result["pillar"] == 183

    def test_9_species_audited(self):
        result = fermion_mass_parameterization_audit()
        assert result["n_species_audited"] == 9

    def test_9_remaining_free(self):
        result = fermion_mass_parameterization_audit()
        assert result["n_remaining_free"] == 9

    def test_species_have_expected_ids(self):
        result = fermion_mass_parameterization_audit()
        ids = {s["id"] for s in result["species"]}
        expected = {"P6", "P7", "P8", "P9", "P10", "P11", "P16", "P17", "P18"}
        assert ids == expected

    def test_overall_status(self):
        result = fermion_mass_parameterization_audit()
        assert result["overall_status"] == "PARAMETERIZED-CONSTRAINED"

    def test_pillar174_confirmed(self):
        result = fermion_mass_parameterization_audit()
        assert result["pillar174_confirmed"] is True

    def test_top_quark_in_zone_1(self):
        result = fermion_mass_parameterization_audit()
        top = next(s for s in result["species"] if s["id"] == "P11")
        assert top["braid_zone"] == 1

    def test_top_quark_ir_localised(self):
        result = fermion_mass_parameterization_audit()
        top = next(s for s in result["species"] if s["id"] == "P11")
        assert top["localisation_class"] == "IR-LOCALISED"

    def test_electron_uv_localised(self):
        result = fermion_mass_parameterization_audit()
        electron = next(s for s in result["species"] if s["id"] == "P16")
        assert electron["localisation_class"] == "UV-LOCALISED"

    def test_all_species_have_epistemic_status(self):
        result = fermion_mass_parameterization_audit()
        for s in result["species"]:
            assert "PARAMETERIZED" in s["epistemic_status"].upper()

    def test_audit_verdict_present(self):
        result = fermion_mass_parameterization_audit()
        assert len(result["audit_verdict"]) > 20


# ===========================================================================
# pillar183_summary
# ===========================================================================

class TestPillar183Summary:
    def test_returns_dict(self):
        result = pillar183_summary()
        assert isinstance(result, dict)

    def test_pillar_183(self):
        result = pillar183_summary()
        assert result["pillar"] == 183

    def test_finding_is_parameterized_constrained(self):
        result = pillar183_summary()
        assert "PARAMETERIZED-CONSTRAINED" in result["finding"]

    def test_n_derived_constraints(self):
        result = pillar183_summary()
        assert result["n_derived_constraints"] == 4

    def test_n_remaining_free(self):
        result = pillar183_summary()
        assert result["n_remaining_free_params"] == 9

    def test_audit_response_present(self):
        result = pillar183_summary()
        assert "audit_response" in result
        assert len(result["audit_response"]) > 20

    def test_version_v937(self):
        result = pillar183_summary()
        assert "v9.37" in result["version"]
