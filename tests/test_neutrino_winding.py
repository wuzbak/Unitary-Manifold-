# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_neutrino_winding.py
================================
Tests for src/core/neutrino_winding.py — Pillar 190.

Test coverage:
  - Inverted braid parameter algebra
  - RHN UV-localization geometry
  - Seesaw mass calculation and Planck consistency
  - Normal hierarchy compatibility
  - Jarlskog residual audit (source tracing)
  - Topological inversion verdict structure
  - Module constants and self-consistency
"""

from __future__ import annotations

import math

import pytest

from src.core.neutrino_winding import (
    C_R_NEUTRINO,
    K_CS,
    M_PLANCK_GEV,
    N_W_INVERTED,
    N_W_PRIMARY,
    PI_KR,
    V_HIGGS_GEV,
    inverted_braid_parameters,
    inversion_jarlskog_residual_audit,
    mass_ordering_check,
    rhn_uv_localization,
    seesaw_from_inverted_braid,
    topological_inversion_verdict,
    _zero_mode_profile,
)


# ===========================================================================
# Module Constants
# ===========================================================================


class TestModuleConstants:
    def test_n_w_primary(self):
        assert N_W_PRIMARY == 5

    def test_n_w_inverted(self):
        assert N_W_INVERTED == 7

    def test_k_cs_value(self):
        assert K_CS == 74

    def test_pi_kr_value(self):
        assert PI_KR == pytest.approx(37.0)

    def test_k_cs_from_pair(self):
        # K_CS = 5² + 7² = 74 (algebraic identity, Pillar 58)
        assert N_W_PRIMARY**2 + N_W_INVERTED**2 == K_CS

    def test_k_cs_inverted_pair(self):
        # K_CS = 7² + 5² = 74 (preserved under inversion)
        assert N_W_INVERTED**2 + N_W_PRIMARY**2 == K_CS

    def test_pi_kr_from_k_cs(self):
        assert PI_KR == pytest.approx(K_CS / 2.0)

    def test_c_r_neutrino_value(self):
        assert C_R_NEUTRINO == pytest.approx(23.0 / 25.0, rel=1e-10)

    def test_c_r_neutrino_uv_localised(self):
        # c_R > 1/2 means UV-localised
        assert C_R_NEUTRINO > 0.5

    def test_m_planck_gev_order(self):
        assert 1.0e18 < M_PLANCK_GEV < 1.3e19

    def test_v_higgs_gev(self):
        assert V_HIGGS_GEV == pytest.approx(246.0)

    def test_winding_product(self):
        # n₁ × n₂ = 35 (braid invariant preserved under inversion)
        assert N_W_PRIMARY * N_W_INVERTED == 35


# ===========================================================================
# Inverted Braid Parameters
# ===========================================================================


class TestInvertedBraidParameters:
    def setup_method(self):
        self.result = inverted_braid_parameters()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_primary_pair(self):
        assert self.result["primary_pair"] == (5, 7)

    def test_inverted_pair(self):
        assert self.result["inverted_pair"] == (7, 5)

    def test_winding_product(self):
        assert self.result["winding_product"] == 35

    def test_k_cs_primary(self):
        assert self.result["k_cs_primary"] == 74

    def test_k_cs_inverted(self):
        assert self.result["k_cs_inverted"] == 74

    def test_k_cs_preserved(self):
        assert self.result["k_cs_preserved"] is True

    def test_uv_winding(self):
        assert self.result["uv_winding"] == 7

    def test_ir_winding(self):
        assert self.result["ir_winding"] == 5

    def test_new_free_parameters(self):
        # Inversion introduces zero new free parameters
        assert self.result["new_free_parameters"] == 0

    def test_interpretation_string(self):
        assert "K_CS" in self.result["interpretation"]
        assert "74" in self.result["interpretation"]

    def test_k_cs_algebra_both_orientations(self):
        p, q = self.result["primary_pair"]
        pi, qi = self.result["inverted_pair"]
        assert p**2 + q**2 == pi**2 + qi**2 == 74

    def test_inverted_pair_is_swap(self):
        p1, p2 = self.result["primary_pair"]
        i1, i2 = self.result["inverted_pair"]
        assert (p1, p2) == (i2, i1)


# ===========================================================================
# RHN UV Localization
# ===========================================================================


class TestRHNUVLocalization:
    def setup_method(self):
        self.result = rhn_uv_localization()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_c_r_default(self):
        assert self.result["c_r"] == pytest.approx(C_R_NEUTRINO)

    def test_uv_localised_flag(self):
        assert self.result["uv_localised"] is True

    def test_delta_positive(self):
        # 2×c_R − 1 = 0.84 > 0 → UV-localised
        assert self.result["delta_2cr_m1"] == pytest.approx(2 * C_R_NEUTRINO - 1.0)
        assert self.result["delta_2cr_m1"] > 0

    def test_profile_ir_small(self):
        # Profile at IR brane should be exponentially suppressed for c_R = 0.92
        assert self.result["profile_ir"] < 1e-5

    def test_suppression_exponent_positive(self):
        exp = self.result["profile_ir_suppression_exponent"]
        assert exp > 0
        assert exp == pytest.approx((2 * C_R_NEUTRINO - 1.0) * PI_KR, rel=1e-8)

    def test_majorana_scale_order(self):
        m_r = self.result["majorana_scale_gev"]
        assert 1e18 < m_r < 2e19

    def test_majorana_scale_equals_planck(self):
        assert self.result["majorana_scale_gev"] == pytest.approx(M_PLANCK_GEV, rel=1e-6)

    def test_pillar_citations(self):
        assert "143" in self.result["localization_source"]
        assert "150" in self.result["majorana_source"]

    def test_ir_localized_control(self):
        # c_L = 0.1 (IR-localised) should give larger IR profile
        result_ir = rhn_uv_localization(c_r=0.1)
        assert result_ir["uv_localised"] is False
        # Profile at IR brane is O(1) for strongly IR-localised
        assert result_ir["profile_ir"] > self.result["profile_ir"]

    def test_c_r_half_flat(self):
        # c_R = 0.5: flat profile
        result_flat = rhn_uv_localization(c_r=0.5)
        assert result_flat["delta_2cr_m1"] == pytest.approx(0.0, abs=1e-12)


# ===========================================================================
# Zero-Mode Profile Helper
# ===========================================================================


class TestZeroModeProfile:
    def test_uv_localised_c09(self):
        # Large c → exponentially small profile at IR
        val = _zero_mode_profile(0.9)
        assert val < 1e-5

    def test_ir_localised_c01(self):
        # Small c → O(1) profile at IR
        val = _zero_mode_profile(0.1)
        assert val > 0.01

    def test_c_half_flat(self):
        # c = 0.5 gives 1/sqrt(PI_KR)
        val = _zero_mode_profile(0.5)
        expected = 1.0 / math.sqrt(PI_KR)
        assert val == pytest.approx(expected, rel=1e-6)

    def test_monotone_in_c(self):
        # Profile at IR decreases as c increases (more UV-localised)
        vals = [_zero_mode_profile(c) for c in [0.2, 0.4, 0.6, 0.8, 0.9]]
        for i in range(len(vals) - 1):
            assert vals[i] >= vals[i + 1]


# ===========================================================================
# Seesaw from Inverted Braid
# ===========================================================================


class TestSeesawFromInvertedBraid:
    def setup_method(self):
        self.result = seesaw_from_inverted_braid()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_formula_string(self):
        assert "y_D" in self.result["formula"]
        assert "M_R" in self.result["formula"]

    def test_m_nu_ev_positive(self):
        assert self.result["m_nu_ev"] > 0

    def test_m_nu_order_of_magnitude(self):
        # Should be in the sub-eV range for y_D=1, M_R=M_Pl
        # y_D=1, v=246 GeV, M_R=1.22e19 GeV → m_ν = v²/M_R ≈ 5e-6 eV
        m_ev = self.result["m_nu_ev"]
        assert 1e-7 < m_ev < 1.0  # sanity: between 100 peV and 1 eV

    def test_planck_consistent_default(self):
        assert self.result["planck_consistent"] is True

    def test_m_nu_mev_consistent_with_ev(self):
        assert self.result["m_nu_mev"] == pytest.approx(self.result["m_nu_ev"] * 1e3, rel=1e-10)

    def test_sum_mnu_estimate(self):
        assert self.result["sum_mnu_estimate_ev"] == pytest.approx(3.0 * self.result["m_nu_ev"], rel=1e-10)

    def test_status_label(self):
        assert self.result["status"] == "TOPOLOGICAL INTERPRETATION"

    def test_geometric_inputs_listed(self):
        assert len(self.result["geometric_inputs"]) >= 3

    def test_honest_gaps_listed(self):
        assert len(self.result["honest_gaps"]) >= 2
        # y_D must be mentioned as a gap
        assert any("y_D" in gap for gap in self.result["honest_gaps"])

    def test_seesaw_formula_numerics(self):
        # m_ν = y_D² × v² / M_R (in GeV), converted to eV
        y_d = 1.0
        m_r = M_PLANCK_GEV
        v = V_HIGGS_GEV
        expected_ev = y_d**2 * v**2 / m_r * 1e9
        assert self.result["m_nu_ev"] == pytest.approx(expected_ev, rel=1e-8)

    def test_larger_y_d_gives_larger_mass(self):
        r2 = seesaw_from_inverted_braid(y_d=2.0)
        r1 = seesaw_from_inverted_braid(y_d=1.0)
        assert r2["m_nu_ev"] == pytest.approx(4.0 * r1["m_nu_ev"], rel=1e-8)

    def test_smaller_m_r_gives_larger_mass(self):
        r_gut = seesaw_from_inverted_braid(m_r_gev=2e16)
        r_planck = seesaw_from_inverted_braid(m_r_gev=M_PLANCK_GEV)
        assert r_gut["m_nu_ev"] > r_planck["m_nu_ev"]

    def test_y_d_stored_in_result(self):
        r = seesaw_from_inverted_braid(y_d=2.5)
        assert r["y_d"] == pytest.approx(2.5)

    def test_planck_bound_ev_present(self):
        assert "planck_bound_ev" in self.result
        assert self.result["planck_bound_ev"] == pytest.approx(0.12)


# ===========================================================================
# Mass Ordering Check
# ===========================================================================


class TestMassOrderingCheck:
    def setup_method(self):
        self.result = mass_ordering_check()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_m1_positive(self):
        assert self.result["m1_ev"] > 0

    def test_nh_ordering(self):
        m1 = self.result["m1_ev"]
        m2 = self.result["m2_ev"]
        m3 = self.result["m3_ev"]
        assert m3 > m2 > m1

    def test_mass_ordering_label(self):
        assert self.result["mass_ordering"] == "NORMAL HIERARCHY"

    def test_planck_consistent(self):
        assert self.result["planck_consistent"] is True

    def test_sum_mnu_below_planck_bound(self):
        assert self.result["sum_mnu_ev"] < self.result["planck_bound_ev"]

    def test_delta_m2_21_satisfied(self):
        assert self.result["delta_m2_21_check"] is True

    def test_delta_m2_31_satisfied(self):
        assert self.result["delta_m2_31_check"] is True

    def test_m2_from_m1_and_splitting(self):
        m1 = self.result["m1_ev"]
        delta21 = self.result["delta_m2_21_ev2"]
        m2_expected = math.sqrt(m1**2 + delta21)
        assert self.result["m2_ev"] == pytest.approx(m2_expected, rel=1e-10)

    def test_m3_from_m1_and_splitting(self):
        m1 = self.result["m1_ev"]
        delta31 = self.result["delta_m2_31_ev2"]
        m3_expected = math.sqrt(m1**2 + delta31)
        assert self.result["m3_ev"] == pytest.approx(m3_expected, rel=1e-10)

    def test_sum_mnu_correct(self):
        m1 = self.result["m1_ev"]
        m2 = self.result["m2_ev"]
        m3 = self.result["m3_ev"]
        assert self.result["sum_mnu_ev"] == pytest.approx(m1 + m2 + m3, rel=1e-10)

    def test_status_contains_compatible(self):
        assert "COMPATIBLE" in self.result["status"]

    def test_pdg_splittings_stored(self):
        assert self.result["delta_m2_21_ev2"] == pytest.approx(7.53e-5, rel=1e-8)
        assert self.result["delta_m2_31_ev2"] == pytest.approx(2.514e-3, rel=1e-8)


# ===========================================================================
# Jarlskog Residual Audit
# ===========================================================================


class TestInversionJarlskogResidualAudit:
    def setup_method(self):
        self.result = inversion_jarlskog_residual_audit()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_j_pdg_value(self):
        assert self.result["j_pdg"] == pytest.approx(3.08e-5, rel=1e-6)

    def test_j_consistent_geo_value(self):
        assert self.result["j_consistent_geo"] == pytest.approx(3.45e-5, rel=1e-6)

    def test_j_ratio_approximately_12pct(self):
        # J_consistent_geo / J_PDG ≈ 1.12
        ratio = self.result["j_ratio"]
        assert ratio == pytest.approx(3.45e-5 / 3.08e-5, rel=1e-6)

    def test_pct_gap_approximately_12(self):
        assert 10.0 < self.result["pct_gap"] < 15.0

    def test_source_module_points_to_ckm(self):
        assert "ckm_scaffold_analysis" in self.result["source_module"]
        assert "188" in self.result["source_module"]

    def test_layer_2_mentioned(self):
        assert "Layer 2" in self.result["source_description"]

    def test_seesaw_connection_is_none(self):
        assert self.result["seesaw_connection"].startswith("NONE")

    def test_verdict_mentions_ckm(self):
        assert "CKM" in self.result["verdict"]

    def test_status_is_open(self):
        assert "OPEN" in self.result["status"]

    def test_seesaw_status_resolved(self):
        assert "Planck" in self.result["seesaw_status"]


# ===========================================================================
# Topological Inversion Verdict
# ===========================================================================


class TestTopologicalInversionVerdict:
    def setup_method(self):
        self.result = topological_inversion_verdict()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_number(self):
        assert self.result["pillar"] == 190

    def test_status_label(self):
        assert self.result["status"] == "TOPOLOGICAL INTERPRETATION"

    def test_version(self):
        assert "10.1" in self.result["version"]

    def test_braid_k_cs_preserved(self):
        assert self.result["braid_inversion"]["k_cs_preserved"] is True

    def test_braid_no_new_params(self):
        assert self.result["braid_inversion"]["new_free_parameters"] == 0

    def test_rhn_uv_localised(self):
        assert self.result["rhn_localization"]["uv_localised"] is True

    def test_rhn_c_r(self):
        assert self.result["rhn_localization"]["c_r"] == pytest.approx(C_R_NEUTRINO)

    def test_seesaw_planck_consistent(self):
        assert self.result["seesaw"]["planck_consistent"] is True

    def test_mass_ordering_nh(self):
        assert self.result["mass_ordering"]["planck_consistent"] is True

    def test_jarlskog_source_ckm(self):
        assert "CKM" in self.result["jarlskog_audit"]["source"]

    def test_jarlskog_seesaw_connection_none(self):
        assert self.result["jarlskog_audit"]["seesaw_connection"] == "NONE"

    def test_derived_from_geometry_list(self):
        items = self.result["derived_from_geometry"]
        assert len(items) >= 4
        # Pillar 143 and 150 must be cited
        assert any("143" in item for item in items)
        assert any("150" in item for item in items)

    def test_honest_gaps_list(self):
        gaps = self.result["honest_gaps"]
        assert len(gaps) >= 2
        assert any("y_D" in gap for gap in gaps)

    def test_addresses_review_claim(self):
        assert "10.1" in self.result["addresses_review"]

    def test_fallibility_note_present(self):
        assert "TOPOLOGICAL INTERPRETATION" in self.result["fallibility_note"]

    def test_inverted_pair_in_verdict(self):
        inv = self.result["braid_inversion"]["inverted_pair"]
        assert inv == (7, 5)
