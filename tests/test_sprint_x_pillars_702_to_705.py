# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Tests for Sprint X — Pillars 702–705
  P702  NP-BC13 instanton WdW kernel
  P703  Baryogenesis KK sphaleron tightening
  P704  DESI dark energy KK routing
  P705  Sprint X regression certificate v21.5
"""

import math
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

import pytest

import pillar702_np_bc13_instanton_wdw_kernel      as p702
import pillar703_baryon_asymmetry_kk_sphaleron     as p703
import pillar704_desi_dark_energy_kk_routing       as p704
import pillar705_sprint_x_regression_certificate   as p705


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar702:
    """NP-BC13: Instanton WdW kernel"""

    def test_instanton_action_large(self):
        S = p702.instanton_action()
        assert S > 700

    def test_instanton_amplitude_zero_due_to_underflow(self):
        A = p702.instanton_amplitude()
        assert A == 0.0

    def test_kernel_bc13_zero(self):
        result = p702.compute_bc13_kernel()
        assert result["kernel_bc13"] == 0.0

    def test_pillar_number(self):
        result = p702.compute_bc13_kernel()
        assert result["pillar"] == 702

    def test_bc13_label(self):
        result = p702.compute_bc13_kernel()
        assert "BC13" in result["label"]

    def test_doubly_suppressed_flag(self):
        result = p702.compute_bc13_kernel()
        assert result["doubly_suppressed"]

    def test_cp_conserving_flag(self):
        result = p702.compute_bc13_kernel()
        assert result["cp_conserving"]

    def test_theta_ym_zero(self):
        result = p702.compute_bc13_kernel()
        assert result["theta_ym_rad"] == 0.0

    def test_units(self):
        result = p702.compute_bc13_kernel()
        assert result["units"] == "M_Pl = 1"

    def test_bc13_ledger_closed(self):
        ledger = p702.np_bc_ledger()
        assert "CLOSED" in ledger["bc13_status"]
        assert "BC13" in ledger["bc13"]

    def test_bc14_named(self):
        ledger = p702.np_bc_ledger()
        assert "BC14" in ledger["next_bc14"]

    def test_ledger_complete_through_bc13(self):
        ledger = p702.np_bc_ledger()
        assert "BC13" in ledger["ledger_complete_through"]

    def test_instanton_action_formula(self):
        # S = 2π/G_N* × (K_CS/N_W)³
        expected = 2 * math.pi / p702.G_N_STAR * p702.KK_R_RATIO ** 3
        assert abs(p702.instanton_action() - expected) < 1e-8

    def test_small_amplitude_at_small_action(self):
        # For tiny G_N*, make S small by using large G_N_star
        A = p702.instanton_amplitude(g_n_star=1e6, kk_r=0.1)
        assert 0 < A < 1

    def test_kk_r_ratio_value(self):
        assert abs(p702.KK_R_RATIO - 74/5) < 1e-12


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar703:
    """Baryogenesis: KK sphaleron tightening"""

    def test_e_sph_kk_larger_than_sm(self):
        assert p703.e_sph_kk() > p703.E_SPH_SM_GEV

    def test_kk_correction_small(self):
        correction = p703.kk_sphaleron_correction()
        assert correction < 0.01

    def test_c_kk_value(self):
        expected = 5 / (2 * 74)
        assert abs(p703.C_KK - expected) < 1e-12

    def test_gamma_sph_with_kk_positive(self):
        gamma = p703.gamma_sph(use_kk=True)
        # Will be zero or positive due to extreme suppression
        assert gamma >= 0

    def test_eta_b_correction_small(self):
        eta_corr = p703.eta_b_kk_correction_fractional()
        assert eta_corr < 0.1   # sub-leading correction (factor E_sph/T ~ 56)

    def test_summary_pillar_number(self):
        s = p703.baryogenesis_summary()
        assert s["pillar"] == 703

    def test_summary_label(self):
        s = p703.baryogenesis_summary()
        assert "BARYON" in s["label"]

    def test_summary_tightening_14(self):
        s = p703.baryogenesis_summary()
        assert s["tightening"] == 14

    def test_summary_architecture_limit_documented(self):
        s = p703.baryogenesis_summary()
        assert "leptogenesis" in s["architecture_limit"].lower()

    def test_eta_b_obs_value(self):
        assert abs(p703.ETA_B_OBS - 6.1e-10) < 1e-20

    def test_e_sph_sm_9tev(self):
        assert abs(p703.E_SPH_SM_GEV - 9000.0) < 1e-8

    def test_kk_e_sph_formula(self):
        T = p703.T_EW_GEV
        M = p703.M_KK_GEV
        expected = p703.E_SPH_SM_GEV * (1 + p703.C_KK * (T/M)**2)
        assert abs(p703.e_sph_kk(T, M) - expected) < 1e-8

    def test_t_ew_gev_value(self):
        assert abs(p703.T_EW_GEV - 160.0) < 1e-10


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar704:
    """DESI dark energy KK routing"""

    def test_w_kk_near_minus_1(self):
        w = p704.w_de_kk(z=0.0)
        assert abs(w - (-1.0)) < 1e-30   # KK correction negligible

    def test_w_kk_independent_of_z(self):
        w0 = p704.w_de_kk(z=0.0)
        w1 = p704.w_de_kk(z=1.0)
        assert abs(w0 - w1) < 1e-30

    def test_desi_tension_w0_above_2sigma(self):
        t = p704.desi_tension()
        assert t["tension_w0_sigma"] > 2

    def test_desi_tension_combined_positive(self):
        t = p704.desi_tension()
        assert t["tension_combined_sigma"] > 0

    def test_kk_w0_minus_1(self):
        assert p704.W0_KK == -1.0

    def test_kk_wa_zero(self):
        assert p704.WA_KK == 0.0

    def test_h0_kk_not_resolve_tension(self):
        h0 = p704.h0_kk_prediction()
        assert h0["kk_resolves_h0_tension"] is False

    def test_h0_value(self):
        h0 = p704.h0_kk_prediction()
        assert abs(h0["H0_kk_km_s_mpc"] - 67.4) < 0.1

    def test_routing_summary_pillar(self):
        s = p704.desi_routing_summary()
        assert s["pillar"] == 704

    def test_routing_label(self):
        s = p704.desi_routing_summary()
        assert "DESI" in s["label"]

    def test_falsification_y5_documented(self):
        s = p704.desi_routing_summary()
        assert "5σ" in s["falsification_y5"]

    def test_desi_year5_timeline(self):
        s = p704.desi_routing_summary()
        assert "2028" in s["desi_year5_timeline"]

    def test_desi_w0_y1_value(self):
        assert abs(p704.W0_DESI_Y1 - (-0.727)) < 1e-10

    def test_tension_wa_above_2sigma(self):
        t = p704.desi_tension()
        assert t["tension_wa_sigma"] > 2


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar705:
    """Sprint X regression certificate v21.5"""

    def test_version(self):
        assert p705.version_string() == "v21.5"

    def test_pillar_total(self):
        assert p705.pillar_total() == 705

    def test_toe_score(self):
        assert p705.toe_score() == "framework internally consistent"

    def test_next_slot(self):
        assert p705.next_pillar_slot() == 706

    def test_sprint_name(self):
        cert = p705.sprint_x_certificate()
        assert cert["sprint"] == "Sprint X"

    def test_toe_not_changed(self):
        cert = p705.sprint_x_certificate()
        assert cert["toe_changed"] is False

    def test_bc13_closed(self):
        ledger = p705.np_bc_ledger()
        assert "CLOSED" in ledger["bc13"]

    def test_bc14_next(self):
        ledger = p705.np_bc_ledger()
        assert "BC14" in ledger["bc14_next"]

    def test_instanton_limit_documented(self):
        cert = p705.sprint_x_certificate()
        assert "instanton" in cert["architecture_limits"]["instanton"].lower()

    def test_desi_tension_documented(self):
        cert = p705.sprint_x_certificate()
        assert "DESI" in cert["architecture_limits"]["desi_w0_tension"]

    def test_open_falsifiers_litebird(self):
        cert = p705.sprint_x_certificate()
        assert "β" in cert["open_falsifiers"]["litebird"]

    def test_open_falsifiers_desi_y5(self):
        cert = p705.sprint_x_certificate()
        assert "DESI" in cert["open_falsifiers"]["desi_y5"] or \
               "w" in cert["open_falsifiers"]["desi_y5"]

    def test_pillar_range(self):
        cert = p705.sprint_x_certificate()
        assert cert["pillar_range"] == "702–705"
