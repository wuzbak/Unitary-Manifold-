# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_neutrino_uv_bc.py
==============================
Tests for src/core/neutrino_uv_bc.py — Pillar 193.

Test coverage:
  - Module constants: N_W, N_INV, K_CS, C_L_NU_UV_BC, Y_D_MIN, Y_D_MAX
  - UV Dirichlet BC: c_L^ν = 25/74, not UV-localised (IR-class)
  - Geometric y_D range: [5/√74, √74/5], ratio = 74/25
  - Lightest neutrino mass: seesaw formula, Planck consistency
  - Neutrino mass window: [m_ν₁_min, m_ν₁_max], both Planck-consistent
  - NH mass spectrum: m_ν₂, m_ν₃ from PDG splittings, Σm_ν bound
  - IH exclusion: y_D_IH > y_D_max, verdict EXCLUDED
  - Mass ordering sealed: NH confirmed, IH excluded
  - Pillar 193 summary: all key fields present
"""

from __future__ import annotations

import math

import pytest

from src.core.neutrino_uv_bc import (
    # Constants
    N_W,
    N_INV,
    K_CS,
    PI_KR,
    M_PLANCK_GEV,
    V_HIGGS_GEV,
    C_R_RHN,
    C_L_NU_UV_BC,
    Y_D_MIN,
    Y_D_MAX,
    Y_D_GEO,
    # API
    uv_dirichlet_boundary_condition,
    geometric_yd_range,
    lightest_neutrino_mass_sealed,
    neutrino_mass_window,
    nh_mass_spectrum,
    ih_exclusion_from_uv_bc,
    mass_ordering_sealed,
    pillar193_summary,
)


# ===========================================================================
# Module Constants
# ===========================================================================

class TestModuleConstants:
    def test_n_w_is_5(self):
        assert N_W == 5

    def test_n_inv_is_7(self):
        assert N_INV == 7

    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_pi_kr_is_37(self):
        assert PI_KR == pytest.approx(37.0, rel=1e-9)

    def test_pi_kr_is_k_cs_over_2(self):
        assert PI_KR == pytest.approx(K_CS / 2.0, rel=1e-9)

    def test_m_planck_gev_order(self):
        assert 1.0e19 < M_PLANCK_GEV < 2.0e19

    def test_v_higgs_gev(self):
        assert V_HIGGS_GEV == pytest.approx(246.0, rel=1e-9)

    def test_c_r_rhn(self):
        assert C_R_RHN == pytest.approx(23.0 / 25.0, rel=1e-9)

    def test_c_l_nu_uv_bc_value(self):
        expected = 25.0 / 74.0
        assert C_L_NU_UV_BC == pytest.approx(expected, rel=1e-9)

    def test_c_l_nu_uv_bc_is_n_w_sq_over_k_cs(self):
        assert C_L_NU_UV_BC == pytest.approx(N_W**2 / K_CS, rel=1e-9)

    def test_c_l_nu_uv_bc_less_than_half(self):
        # IR-class ν_L (c_L < 1/2)
        assert C_L_NU_UV_BC < 0.5

    def test_y_d_min_formula(self):
        expected = N_W / math.sqrt(K_CS)
        assert Y_D_MIN == pytest.approx(expected, rel=1e-9)

    def test_y_d_max_formula(self):
        expected = math.sqrt(K_CS) / N_W
        assert Y_D_MAX == pytest.approx(expected, rel=1e-9)

    def test_y_d_geo_is_unity(self):
        assert Y_D_GEO == pytest.approx(1.0, rel=1e-9)

    def test_y_d_min_less_than_max(self):
        assert Y_D_MIN < Y_D_MAX

    def test_y_d_min_less_than_geo(self):
        assert Y_D_MIN < Y_D_GEO

    def test_y_d_max_greater_than_geo(self):
        assert Y_D_MAX > Y_D_GEO

    def test_y_d_min_approx(self):
        assert Y_D_MIN == pytest.approx(5.0 / math.sqrt(74.0), rel=1e-6)

    def test_y_d_max_approx(self):
        assert Y_D_MAX == pytest.approx(math.sqrt(74.0) / 5.0, rel=1e-6)

    def test_y_d_product_is_one(self):
        # y_d_min × y_d_max = (5/√74) × (√74/5) = 1
        assert Y_D_MIN * Y_D_MAX == pytest.approx(1.0, rel=1e-9)

    def test_y_d_ratio_is_k_cs_over_n_w_sq(self):
        # y_d_max / y_d_min = K_CS / n_w²
        assert (Y_D_MAX / Y_D_MIN) == pytest.approx(K_CS / N_W**2, rel=1e-9)

    def test_c_l_nu_and_y_d_min_consistency(self):
        # C_L_NU_UV_BC = n_w²/K_CS = Y_D_MIN²
        assert C_L_NU_UV_BC == pytest.approx(Y_D_MIN**2, rel=1e-9)

    def test_braid_pair_sum_of_squares(self):
        assert N_W**2 + N_INV**2 == K_CS


# ===========================================================================
# uv_dirichlet_boundary_condition
# ===========================================================================

class TestUVDirichletBC:
    @pytest.fixture(autouse=True)
    def result(self):
        self._r = uv_dirichlet_boundary_condition()

    def test_returns_dict(self):
        assert isinstance(self._r, dict)

    def test_c_l_nu_value(self):
        assert self._r["c_l_nu"] == pytest.approx(25.0 / 74.0, rel=1e-9)

    def test_c_l_nu_fraction_string(self):
        assert self._r["c_l_nu_fraction"] == "25/74"

    def test_c_l_nu_exact_matches(self):
        assert self._r["c_l_nu_exact"] == pytest.approx(25.0 / 74.0, rel=1e-9)

    def test_not_uv_localised(self):
        # c_L < 1/2 → IR-class (not UV-localised)
        assert self._r["uv_localised"] is False

    def test_is_ir_localised(self):
        assert self._r["ir_localised"] is True

    def test_brane_winding_n_w(self):
        assert self._r["brane_winding"]["primary"] == 5

    def test_brane_winding_n_inv(self):
        assert self._r["brane_winding"]["inverted"] == 7

    def test_brane_winding_k_cs(self):
        assert self._r["brane_winding"]["k_cs"] == 74

    def test_derivation_steps_is_list(self):
        assert isinstance(self._r["derivation_steps"], list)

    def test_derivation_steps_length(self):
        assert len(self._r["derivation_steps"]) == 4

    def test_status_is_geometric_derivation(self):
        assert "GEOMETRIC DERIVATION" in self._r["status"]

    def test_source_mentions_pillar(self):
        assert "Pillar 193" in self._r["source"]

    def test_honest_note_present(self):
        assert len(self._r["honest_note"]) > 20


# ===========================================================================
# geometric_yd_range
# ===========================================================================

class TestGeometricYDRange:
    @pytest.fixture(autouse=True)
    def result(self):
        self._r = geometric_yd_range()

    def test_returns_dict(self):
        assert isinstance(self._r, dict)

    def test_y_d_min_value(self):
        assert self._r["y_d_min"] == pytest.approx(5.0 / math.sqrt(74.0), rel=1e-6)

    def test_y_d_max_value(self):
        assert self._r["y_d_max"] == pytest.approx(math.sqrt(74.0) / 5.0, rel=1e-6)

    def test_y_d_geo_is_one(self):
        assert self._r["y_d_geo"] == pytest.approx(1.0, rel=1e-9)

    def test_ratio_max_min(self):
        assert self._r["ratio_max_min"] == pytest.approx(74.0 / 25.0, rel=1e-6)

    def test_ratio_exact_string(self):
        assert "74/25" in self._r["ratio_exact"]

    def test_winding_ratio(self):
        assert self._r["winding_ratio"] == pytest.approx(7.0 / 5.0, rel=1e-9)

    def test_y_d_min_less_than_max(self):
        assert self._r["y_d_min"] < self._r["y_d_max"]

    def test_y_d_geo_in_range(self):
        assert self._r["y_d_min"] < self._r["y_d_geo"] < self._r["y_d_max"]

    def test_interpretation_present(self):
        assert len(self._r["interpretation"]) > 20

    def test_status_present(self):
        assert "GEOMETRIC CONSTRAINT" in self._r["status"]


# ===========================================================================
# lightest_neutrino_mass_sealed
# ===========================================================================

class TestLightestNeutrinoMassSealed:
    def test_canonical_y_d_gives_5mev(self):
        r = lightest_neutrino_mass_sealed(1.0)
        # m_ν₁ ≈ 4.96 meV (v²/M_R in meV)
        assert r["m_nu1_mev"] == pytest.approx(4.96, abs=0.2)

    def test_canonical_planck_consistent(self):
        r = lightest_neutrino_mass_sealed(1.0)
        assert r["planck_consistent"] is True

    def test_y_d_min_in_range(self):
        r = lightest_neutrino_mass_sealed(Y_D_MIN)
        assert r["in_uv_bc_range"] is True

    def test_y_d_max_in_range(self):
        r = lightest_neutrino_mass_sealed(Y_D_MAX)
        assert r["in_uv_bc_range"] is True

    def test_y_d_large_not_in_range(self):
        r = lightest_neutrino_mass_sealed(5.0)
        assert r["in_uv_bc_range"] is False

    def test_mass_scales_as_yd_squared(self):
        r1 = lightest_neutrino_mass_sealed(1.0)
        r2 = lightest_neutrino_mass_sealed(2.0)
        assert r2["m_nu1_ev"] == pytest.approx(4.0 * r1["m_nu1_ev"], rel=1e-6)

    def test_formula_key_present(self):
        r = lightest_neutrino_mass_sealed()
        assert "y_D² × v² / M_R" in r["formula"]

    def test_uv_bc_range_in_output(self):
        r = lightest_neutrino_mass_sealed()
        assert r["uv_bc_y_d_range"] == pytest.approx((Y_D_MIN, Y_D_MAX), rel=1e-6)

    def test_all_uv_bc_range_masses_planck_ok(self):
        for y_d in [Y_D_MIN, Y_D_GEO, Y_D_MAX]:
            r = lightest_neutrino_mass_sealed(y_d)
            assert r["planck_consistent"] is True, f"y_D={y_d}: Planck inconsistent"

    def test_m_nu1_positive(self):
        r = lightest_neutrino_mass_sealed(0.5)
        assert r["m_nu1_ev"] > 0.0


# ===========================================================================
# neutrino_mass_window
# ===========================================================================

class TestNeutrinoMassWindow:
    @pytest.fixture(autouse=True)
    def result(self):
        self._r = neutrino_mass_window()

    def test_returns_dict(self):
        assert isinstance(self._r, dict)

    def test_m_nu1_min_approx_168_uev(self):
        # min ≈ (25/74) × 4.96 meV ≈ 1.68 meV
        assert self._r["m_nu1_min_mev"] == pytest.approx(1.675, abs=0.05)

    def test_m_nu1_max_approx_1480_uev(self):
        # max ≈ (74/25) × 4.96 meV ≈ 14.80 meV
        assert self._r["m_nu1_max_mev"] == pytest.approx(14.78, abs=0.1)

    def test_m_nu1_central_approx_5mev(self):
        assert self._r["m_nu1_central_mev"] == pytest.approx(4.96, abs=0.2)

    def test_min_less_than_central(self):
        assert self._r["m_nu1_min_ev"] < self._r["m_nu1_central_ev"]

    def test_central_less_than_max(self):
        assert self._r["m_nu1_central_ev"] < self._r["m_nu1_max_ev"]

    def test_ratio_min_is_25_over_74(self):
        assert self._r["ratio_min_to_central"] == pytest.approx(25.0 / 74.0, rel=1e-4)

    def test_ratio_max_is_74_over_25(self):
        assert self._r["ratio_max_to_central"] == pytest.approx(74.0 / 25.0, rel=1e-4)

    def test_sum_mnu_min_planck_ok(self):
        assert self._r["sum_mnu_min_planck_ok"] is True

    def test_sum_mnu_max_planck_ok(self):
        assert self._r["sum_mnu_max_planck_ok"] is True

    def test_planck_bound_is_012_ev(self):
        assert self._r["planck_bound_ev"] == pytest.approx(0.12, rel=1e-9)

    def test_falsification_condition_present(self):
        assert len(self._r["falsification_condition"]) > 20

    def test_status_is_sealed(self):
        assert "SEALED" in self._r["status"]

    def test_ratio_exact_string(self):
        assert "25/74" in self._r["ratio_min_exact"]
        assert "74/25" in self._r["ratio_max_exact"]


# ===========================================================================
# nh_mass_spectrum
# ===========================================================================

class TestNHMassSpectrum:
    def test_m1_passthrough(self):
        r = nh_mass_spectrum(5e-3)  # 5 meV
        assert r["m1_ev"] == pytest.approx(5e-3, rel=1e-9)

    def test_m2_from_solar_splitting(self):
        m1 = 5e-3
        r = nh_mass_spectrum(m1)
        expected_m2 = math.sqrt(m1**2 + 7.53e-5)
        assert r["m2_ev"] == pytest.approx(expected_m2, rel=1e-9)

    def test_m3_from_atmospheric_splitting(self):
        m1 = 5e-3
        r = nh_mass_spectrum(m1)
        expected_m3 = math.sqrt(m1**2 + 2.514e-3)
        assert r["m3_ev"] == pytest.approx(expected_m3, rel=1e-9)

    def test_ordering_m1_lt_m2_lt_m3(self):
        r = nh_mass_spectrum(5e-3)
        assert r["m1_ev"] < r["m2_ev"] < r["m3_ev"]

    def test_sum_mnu_is_sum_of_masses(self):
        r = nh_mass_spectrum(5e-3)
        assert r["sum_mnu_ev"] == pytest.approx(r["m1_ev"] + r["m2_ev"] + r["m3_ev"], rel=1e-9)

    def test_planck_consistent_for_small_m1(self):
        r = nh_mass_spectrum(1e-3)  # 1 meV
        assert r["planck_consistent"] is True

    def test_ordering_label(self):
        r = nh_mass_spectrum(5e-3)
        assert r["ordering"] == "NH"

    def test_splitting_checks_pass(self):
        r = nh_mass_spectrum(5e-3)
        assert r["delta_m2_21_check"] is True
        assert r["delta_m2_31_check"] is True

    def test_massless_m1_allowed(self):
        # NH allows massless lightest neutrino
        r = nh_mass_spectrum(0.0)
        assert r["m1_ev"] == pytest.approx(0.0, abs=1e-20)
        assert r["m2_ev"] == pytest.approx(math.sqrt(7.53e-5), rel=1e-6)
        assert r["planck_consistent"] is True

    def test_planck_bound_present(self):
        r = nh_mass_spectrum(5e-3)
        assert r["planck_bound_ev"] == pytest.approx(0.12, rel=1e-9)


# ===========================================================================
# ih_exclusion_from_uv_bc
# ===========================================================================

class TestIHExclusionFromUVBC:
    @pytest.fixture(autouse=True)
    def result(self):
        self._r = ih_exclusion_from_uv_bc()

    def test_returns_dict(self):
        assert isinstance(self._r, dict)

    def test_ih_quasi_deg_mass_50mev(self):
        assert self._r["ih_quasi_deg_mass_mev"] == pytest.approx(50.0, rel=1e-9)

    def test_y_d_required_ih_greater_than_max(self):
        assert self._r["y_d_required_ih"] > self._r["y_d_max_uv_bc"]

    def test_ih_excluded_is_true(self):
        assert self._r["ih_excluded"] is True

    def test_y_d_required_ih_approx_316(self):
        # y_D_IH ≈ √(50e-3/4.96e-3) ≈ √10.08 ≈ 3.175
        assert self._r["y_d_required_ih"] == pytest.approx(3.175, abs=0.05)

    def test_y_d_max_uv_bc_matches_module_constant(self):
        assert self._r["y_d_max_uv_bc"] == pytest.approx(Y_D_MAX, rel=1e-6)

    def test_ih_excess_ratio_gt_1(self):
        assert self._r["ih_excess_ratio"] > 1.0

    def test_ih_excess_ratio_approx_18(self):
        # ≈ 3.175/1.72 ≈ 1.85
        assert self._r["ih_excess_ratio"] == pytest.approx(1.85, abs=0.1)

    def test_proof_steps_list(self):
        assert isinstance(self._r["proof_steps"], list)

    def test_proof_steps_length(self):
        assert len(self._r["proof_steps"]) == 6

    def test_verdict_mentions_excluded(self):
        assert "EXCLUDED" in self._r["verdict"]

    def test_status_is_ih_excluded(self):
        assert "EXCLUDED" in self._r["status"]

    def test_exclusion_factor_matches_ratio(self):
        assert self._r["exclusion_factor"] == pytest.approx(
            self._r["ih_excess_ratio"], rel=1e-9
        )


# ===========================================================================
# mass_ordering_sealed
# ===========================================================================

class TestMassOrderingSealed:
    @pytest.fixture(autouse=True)
    def result(self):
        self._r = mass_ordering_sealed()

    def test_returns_dict(self):
        assert isinstance(self._r, dict)

    def test_pillar_is_193(self):
        assert self._r["pillar"] == 193

    def test_ih_excluded(self):
        assert self._r["ih_excluded"] is True

    def test_nh_confirmed(self):
        assert self._r["nh_confirmed"] is True

    def test_uv_bc_c_l_nu(self):
        assert self._r["uv_bc"]["c_l_nu"] == pytest.approx(25.0 / 74.0, rel=1e-6)

    def test_uv_bc_fraction(self):
        assert "25/74" in self._r["uv_bc"]["c_l_nu_fraction"]

    def test_yd_range_min_max(self):
        yd = self._r["geometric_yd_range"]
        assert yd["y_d_min"] == pytest.approx(Y_D_MIN, rel=1e-6)
        assert yd["y_d_max"] == pytest.approx(Y_D_MAX, rel=1e-6)

    def test_mass_window_min_mev(self):
        w = self._r["sealed_mass_window_mev"]
        assert w["m_nu1_min_mev"] == pytest.approx(1.675, abs=0.05)

    def test_mass_window_max_mev(self):
        w = self._r["sealed_mass_window_mev"]
        assert w["m_nu1_max_mev"] == pytest.approx(14.78, abs=0.1)

    def test_mass_ordering_verdict_text(self):
        assert "NORMAL HIERARCHY" in self._r["mass_ordering_verdict"]
        assert "EXCLUDED" in self._r["mass_ordering_verdict"]

    def test_status_sealed(self):
        assert "SEALED" in self._r["status"]

    def test_falsification_condition_present(self):
        assert len(self._r["falsification_condition"]) > 20


# ===========================================================================
# pillar193_summary
# ===========================================================================

class TestPillar193Summary:
    @pytest.fixture(autouse=True)
    def result(self):
        self._r = pillar193_summary()

    def test_returns_dict(self):
        assert isinstance(self._r, dict)

    def test_pillar_number(self):
        assert self._r["pillar"] == 193

    def test_version(self):
        assert self._r["version"] == "v10.2"

    def test_status_sealed(self):
        assert "SEALED" in self._r["status"]

    def test_key_results_c_l_nu(self):
        assert self._r["key_results"]["c_l_nu"] == pytest.approx(25.0 / 74.0, rel=1e-6)

    def test_key_results_y_d_range(self):
        yr = self._r["key_results"]["y_d_range"]
        assert yr[0] == pytest.approx(Y_D_MIN, rel=1e-6)
        assert yr[1] == pytest.approx(Y_D_MAX, rel=1e-6)

    def test_key_results_ih_excluded(self):
        assert self._r["key_results"]["ih_excluded"] is True

    def test_key_results_nh_confirmed(self):
        assert self._r["key_results"]["nh_confirmed"] is True

    def test_derived_from_geometry_list(self):
        assert isinstance(self._r["derived_from_geometry"], list)
        assert len(self._r["derived_from_geometry"]) >= 4

    def test_honest_gaps_list(self):
        assert isinstance(self._r["honest_gaps"], list)
        assert len(self._r["honest_gaps"]) >= 3

    def test_prior_pillars_unchanged_list(self):
        p = self._r["prior_pillars_unchanged"]
        assert isinstance(p, list)
        assert len(p) >= 4

    def test_addresses_review(self):
        assert "v10.2" in self._r["addresses_review"] or "Omega" in self._r["addresses_review"]

    def test_falsification_condition_present(self):
        assert len(self._r["falsification_condition"]) > 20

    def test_title_contains_neutrino(self):
        assert "Neutrino" in self._r["title"]

    def test_m_nu1_min_in_window(self):
        assert self._r["key_results"]["m_nu1_min_mev"] == pytest.approx(1.675, abs=0.05)

    def test_m_nu1_max_in_window(self):
        assert self._r["key_results"]["m_nu1_max_mev"] == pytest.approx(14.78, abs=0.1)


# ===========================================================================
# Cross-checks and self-consistency
# ===========================================================================

class TestCrossChecks:
    def test_c_l_nu_equals_y_d_min_squared(self):
        # C_L_NU_UV_BC = n_w²/K_CS = Y_D_MIN²
        assert C_L_NU_UV_BC == pytest.approx(Y_D_MIN**2, rel=1e-9)

    def test_y_d_min_times_y_d_max_is_one(self):
        assert Y_D_MIN * Y_D_MAX == pytest.approx(1.0, rel=1e-9)

    def test_mass_window_ratio_is_k_cs_sq_over_n_w_4th(self):
        # m_max/m_min = (y_d_max/y_d_min)² = (K_CS/n_w²)² = (74/25)² ≈ 8.758
        window = neutrino_mass_window()
        ratio = window["m_nu1_max_ev"] / window["m_nu1_min_ev"]
        expected = (K_CS / N_W**2)**2
        assert ratio == pytest.approx(expected, rel=1e-4)

    def test_ih_exclusion_and_mass_ordering_consistent(self):
        ih = ih_exclusion_from_uv_bc()
        ordering = mass_ordering_sealed()
        assert ih["ih_excluded"] == ordering["ih_excluded"]
        assert ordering["nh_confirmed"] is True

    def test_all_window_masses_satisfy_planck_bound(self):
        window = neutrino_mass_window()
        assert window["sum_mnu_min_ev"] < 0.12
        assert window["sum_mnu_max_ev"] < 0.12

    def test_ih_required_yd_exceeds_uv_bc_range(self):
        ih = ih_exclusion_from_uv_bc()
        yd_range = geometric_yd_range()
        assert ih["y_d_required_ih"] > yd_range["y_d_max"]

    def test_n_w_sq_plus_n_inv_sq_eq_k_cs(self):
        assert N_W**2 + N_INV**2 == K_CS

    def test_uv_bc_c_l_is_complement_of_c_r(self):
        # c_L^ν + c_R_RHN ~ 1 roughly (both quantized from n_w, K_CS)
        # Not an exact relation but c_L < 0.5 and c_R > 0.5
        assert C_L_NU_UV_BC < 0.5
        assert C_R_RHN > 0.5

    def test_nh_spectrum_at_central_mass_planck_ok(self):
        window = neutrino_mass_window()
        spec = nh_mass_spectrum(window["m_nu1_central_ev"])
        assert spec["planck_consistent"] is True

    def test_summary_and_window_min_consistent(self):
        summary = pillar193_summary()
        window = neutrino_mass_window()
        assert summary["key_results"]["m_nu1_min_mev"] == pytest.approx(
            window["m_nu1_min_mev"], rel=1e-6
        )
