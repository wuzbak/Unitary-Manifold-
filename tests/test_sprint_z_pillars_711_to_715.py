# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Tests for Sprint Z — Pillars 711–715
  P711  NP-BC15 Chern-Simons topological WdW kernel
  P712  Tightening 15 — tensor spectral index n_T
  P713  B-mode polarisation power spectrum
  P714  KK dark matter relic density
  P715  Sprint Z regression certificate v21.7
"""

import math
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

import pytest

import pillar711_np_bc15_chern_simons_wdw_kernel      as p711
import pillar712_tensor_spectral_index_tightening     as p712
import pillar713_bmode_polarisation_power_spectrum    as p713
import pillar714_kk_dark_matter_relic_density         as p714
import pillar715_sprint_z_regression_certificate      as p715


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar711:
    """NP-BC15: Chern-Simons topological WdW kernel"""

    def test_chi_top_positive(self):
        assert p711.chi_topological() > 0

    def test_kernel_nonneg(self):
        result = p711.compute_bc15_kernel()
        assert result["kernel_bc15"] >= 0

    def test_pillar_number(self):
        result = p711.compute_bc15_kernel()
        assert result["pillar"] == 711

    def test_bc15_label(self):
        result = p711.compute_bc15_kernel()
        assert "BC15" in result["label"]

    def test_fixed_point_vanishing(self):
        fp = p711.bc15_fixed_point_vanishing()
        assert fp["vanishes"]

    def test_kcs_equals_braided(self):
        result = p711.compute_bc15_kernel()
        assert result["kcs_equals_braided_winding"]

    def test_k_cs_value(self):
        assert p711.K_CS == 74

    def test_bc15_ledger_closed(self):
        ledger = p711.np_bc_ledger()
        assert "CLOSED" in ledger["bc15_status"]

    def test_bc16_named(self):
        ledger = p711.np_bc_ledger()
        assert "BC16" in ledger["next_bc16"]

    def test_through_bc15(self):
        ledger = p711.np_bc_ledger()
        assert "BC15" in ledger["ledger_complete_through"]

    def test_units(self):
        result = p711.compute_bc15_kernel()
        assert result["units"] == "M_Pl = 1"

    def test_kernel_at_zero_gn_positive(self):
        result = p711.compute_bc15_kernel(g_n=0.0, g_n_star=p711.G_N_STAR)
        assert result["kernel_bc15"] > 0

    def test_chi_top_formula(self):
        m = p711.M_KK_NATURAL
        expected = m ** 4 / (8 * math.pi ** 2)
        assert abs(p711.chi_topological() - expected) < 1e-200


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar712:
    """Tensor spectral index tightening"""

    def test_n_t_standard_negative(self):
        assert p712.n_t_standard() < 0

    def test_n_t_standard_value(self):
        expected = -p712.R_BRAIDED / 8
        assert abs(p712.n_t_standard() - expected) < 1e-12

    def test_n_t_kk_more_negative(self):
        assert p712.n_t_kk() < p712.n_t_standard()

    def test_correction_factor_above_1(self):
        assert p712.kk_correction_factor() > 1

    def test_correction_factor_formula(self):
        cs = p712.C_S_BRAIDED
        expected = 1 / cs ** 2
        assert abs(p712.kk_correction_factor() - expected) < 1e-10

    def test_pillar_number(self):
        s = p712.tensor_index_summary()
        assert s["pillar"] == 712

    def test_tightening_15(self):
        s = p712.tensor_index_summary()
        assert s["tightening"] == 15

    def test_not_near_term_detectable(self):
        s = p712.tensor_index_summary()
        assert not s["detectable_near_term"]   # |n_T| < 0.1 < 0.3 (BICEP3)

    def test_c_s_braided_value(self):
        assert abs(p712.C_S_BRAIDED - 12/37) < 1e-14

    def test_r_braided_value(self):
        assert abs(p712.R_BRAIDED - 0.0315) < 1e-12


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar713:
    """B-mode polarisation power spectrum"""

    def test_c_bb_peak_positive(self):
        assert p713.c_bb_peak() > 0

    def test_r_within_bicep_keck(self):
        assert p713.r_within_bicep_keck_limit()

    def test_litebird_detectable(self):
        s = p713.b_mode_summary()
        assert s["litebird_detectable"]

    def test_litebird_sigma_above_10(self):
        assert p713.litebird_sensitivity_sigma() > 10

    def test_pillar_number(self):
        s = p713.b_mode_summary()
        assert s["pillar"] == 713

    def test_is_primary_falsifier(self):
        s = p713.b_mode_summary()
        assert s["primary_falsifier"]

    def test_c_bb_decreases_with_ell(self):
        # C_BB rises to peak at ℓ~80 then decreases; compare ℓ=100 and ℓ=200
        c_mid  = p713.c_bb_l(100)
        c_high = p713.c_bb_l(200)
        assert c_high < c_mid

    def test_c_bb_l80_formula(self):
        expected = (p713.R_BRAIDED / 0.1) * p713.C_BB_L80_PER_R
        actual = p713.c_bb_peak()
        # Exact at ell_pivot = 80, including damping factor
        assert actual > 0
        assert actual <= expected   # damping reduces it

    def test_r_value_in_summary(self):
        s = p713.b_mode_summary()
        assert abs(s["r"] - p713.R_BRAIDED) < 1e-12

    def test_litebird_timeline(self):
        s = p713.b_mode_summary()
        assert "2032" in s["litebird_timeline"]


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar714:
    """KK dark matter relic density"""

    def test_sigma_v_positive(self):
        assert p714.sigma_v_kk_pb() > 0

    def test_omega_positive(self):
        assert p714.omega_kk_h2() > 0

    def test_within_factor_2(self):
        s = p714.relic_density_summary()
        assert s["within_factor_2"]

    def test_pillar_number(self):
        s = p714.relic_density_summary()
        assert s["pillar"] == 714

    def test_tightening_16(self):
        s = p714.relic_density_summary()
        assert s["tightening"] == 16

    def test_label(self):
        s = p714.relic_density_summary()
        assert "KK_DARK_MATTER" in s["label"]

    def test_omega_below_observed(self):
        omega = p714.omega_kk_h2()
        assert omega < p714.OMEGA_DM_H2 * 2   # within factor 2

    def test_sigma_v_formula(self):
        g = p714.G_KK
        m = p714.M_KK_GEV
        expected_gev2 = g ** 4 / (16 * math.pi * m ** 2)
        actual_gev2   = p714.sigma_v_kk_gev2()
        assert abs(actual_gev2 - expected_gev2) / expected_gev2 < 1e-10

    def test_omega_formula(self):
        sv  = p714.sigma_v_kk_pb()
        expected = 0.1 / sv
        actual   = p714.omega_kk_h2()
        assert abs(actual - expected) / expected < 1e-10

    def test_g_kk_value(self):
        assert abs(p714.G_KK - 0.63) < 1e-10


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar715:
    """Sprint Z regression certificate v21.7"""

    def test_version(self):
        assert p715.version_string() == "v21.7"

    def test_pillar_total(self):
        assert p715.pillar_total() == 715

    def test_toe_score(self):
        assert p715.toe_score() == "30.0/28"

    def test_next_slot(self):
        assert p715.next_pillar_slot() == 716

    def test_sprint_name(self):
        cert = p715.sprint_z_certificate()
        assert cert["sprint"] == "Sprint Z"

    def test_toe_not_changed(self):
        cert = p715.sprint_z_certificate()
        assert cert["toe_changed"] is False

    def test_bc15_closed(self):
        ledger = p715.np_bc_ledger()
        assert "CLOSED" in ledger["bc15"]

    def test_bc16_next(self):
        ledger = p715.np_bc_ledger()
        assert "BC16" in ledger["bc16_next"]

    def test_bmode_limit_documented(self):
        cert = p715.sprint_z_certificate()
        assert "LiteBIRD" in cert["architecture_limits"]["bmode"]

    def test_dm_relic_limit(self):
        cert = p715.sprint_z_certificate()
        assert "Tightening 16" in cert["architecture_limits"]["dm_relic"]

    def test_litebird_in_falsifiers(self):
        cert = p715.sprint_z_certificate()
        assert "β" in cert["open_falsifiers"]["litebird"]

    def test_pillar_range(self):
        cert = p715.sprint_z_certificate()
        assert cert["pillar_range"] == "711–715"
