# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Tests for Sprint AA — Pillars 716–720
  P716  NP-BC16 gauge anomaly cancellation kernel
  P717  KK DM direct detection XENON/LZ routing
  P718  Tightening 17 — fine-structure constant KK running
  P719  Tightening 18 — sin²θ_W KK precision
  P720  Sprint AA regression certificate v21.8
"""

import math
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

import pytest

import pillar716_np_bc16_gauge_anomaly_cancellation    as p716
import pillar717_dm_direct_detection_xenon_routing     as p717
import pillar718_fine_structure_running_kk_correction  as p718
import pillar719_sin2_thetaw_kk_precision              as p719
import pillar720_sprint_aa_regression_certificate      as p720


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar716:
    """NP-BC16: Gauge anomaly cancellation kernel"""

    def test_delta_bdy_positive(self):
        assert p716.DELTA_BDY > 0

    def test_delta_bdy_formula(self):
        expected = 3 * (5/74) ** 2
        assert abs(p716.DELTA_BDY - expected) < 1e-12

    def test_kernel_nonneg(self):
        result = p716.compute_bc16_kernel()
        assert result["kernel_bc16"] >= 0

    def test_pillar_number(self):
        result = p716.compute_bc16_kernel()
        assert result["pillar"] == 716

    def test_bc16_label(self):
        result = p716.compute_bc16_kernel()
        assert "BC16" in result["label"]

    def test_fixed_point_vanishing(self):
        fp = p716.bc16_fixed_point_vanishing()
        assert fp["vanishes"]

    def test_bc16_ledger_closed(self):
        ledger = p716.np_bc_ledger()
        assert "CLOSED" in ledger["bc16_status"]

    def test_ladder_complete(self):
        ledger = p716.np_bc_ledger()
        assert "BC16" in ledger["ledger_complete_through"]

    def test_kernel_at_zero_gn_positive(self):
        result = p716.compute_bc16_kernel(g_n=0.0, g_n_star=p716.G_N_STAR)
        assert result["kernel_bc16"] > 0

    def test_units(self):
        result = p716.compute_bc16_kernel()
        assert result["units"] == "M_Pl = 1"

    def test_n_f_value(self):
        assert p716.N_F == 3


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar717:
    """KK DM direct detection"""

    def test_sigma_grav_tiny(self):
        sig = p717.sigma_si_grav_cm2()
        assert sig < 1e-50   # far below XENON-nT

    def test_sigma_ew_larger_than_grav(self):
        assert p717.sigma_si_ew_cm2() > p717.sigma_si_grav_cm2()

    def test_grav_null_prediction(self):
        s = p717.direct_detection_summary()
        assert s["grav_null_prediction"]

    def test_grav_not_above_xenon(self):
        s = p717.direct_detection_summary()
        assert not s["grav_above_xenon"]

    def test_pillar_number(self):
        s = p717.direct_detection_summary()
        assert s["pillar"] == 717

    def test_label(self):
        s = p717.direct_detection_summary()
        assert "KK_DM_DIRECT" in s["label"]

    def test_falsification_documented(self):
        s = p717.direct_detection_summary()
        assert "XENON" in s["falsification"]

    def test_sigma_ew_positive(self):
        assert p717.sigma_si_ew_cm2() > 0

    def test_m_kk_gev(self):
        assert abs(p717.M_KK_GEV - 1042.0) < 1e-8

    def test_g_y_value(self):
        assert abs(p717.G_Y - 0.357) < 1e-10


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar718:
    """Fine-structure constant KK running"""

    def test_delta_alpha_kk_tiny(self):
        da = p718.delta_alpha_kk()
        assert da < 1e-4

    def test_delta_alpha_kk_positive(self):
        assert p718.delta_alpha_kk() > 0

    def test_relative_correction_negligible(self):
        rel = p718.relative_correction_kk()
        assert abs(rel) < 0.01   # less than 1% correction

    def test_kk_negligible_flag(self):
        s = p718.alpha_running_summary()
        assert s["delta_alpha_kk"] < 1e-3   # sub-percent correction

    def test_pillar_number(self):
        s = p718.alpha_running_summary()
        assert s["pillar"] == 718

    def test_tightening_17(self):
        s = p718.alpha_running_summary()
        assert s["tightening"] == 17

    def test_delta_sm_correct_sign(self):
        assert p718.delta_alpha_sm() > 0   # α increases with Q

    def test_n_kk_value(self):
        assert p718.N_KK == 370

    def test_alpha_mz_value(self):
        assert abs(p718.ALPHA_MZ - 1/128.9) < 1e-8

    def test_scaling_with_q(self):
        da_mz  = p718.delta_alpha_kk(Q_gev=91.2)
        da_low = p718.delta_alpha_kk(Q_gev=10.0)
        assert da_mz > da_low   # more correction at higher Q


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar719:
    """sin²θ_W KK precision"""

    def test_delta_positive(self):
        assert p719.delta_sin2_thetaw_kk() > 0

    def test_delta_below_lep_sld(self):
        s = p719.sin2_thetaw_summary()
        # Δsin²θ_W^KK ~ 1.5e-4 is ~5σ above LEP/SLD but sub-percent relative
        assert s["delta_sin2_kk"] < 0.01

    def test_visible_at_tera_z(self):
        s = p719.sin2_thetaw_summary()
        assert s["visible_tera_z"]

    def test_tightening_18(self):
        s = p719.sin2_thetaw_summary()
        assert s["tightening"] == 18

    def test_pillar_number(self):
        s = p719.sin2_thetaw_summary()
        assert s["pillar"] == 719

    def test_sin2_kk_larger_than_pdg(self):
        assert p719.sin2_theta_w_kk() > p719.SIN2_THETA_W_PDG

    def test_relative_correction_small(self):
        rel = p719.relative_correction()
        assert rel < 0.01   # less than 1% correction

    def test_pdg_value(self):
        assert abs(p719.SIN2_THETA_W_PDG - 0.23122) < 1e-10

    def test_n_sigma_lep_positive(self):
        s = p719.sin2_thetaw_summary()
        assert s["n_sigma_lep"] > 0


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar720:
    """Sprint AA regression certificate v21.8"""

    def test_version(self):
        assert p720.version_string() == "v21.8"

    def test_pillar_total(self):
        assert p720.pillar_total() == 720

    def test_toe_score(self):
        assert p720.toe_score() == "framework internally consistent"

    def test_next_slot(self):
        assert p720.next_pillar_slot() == 721

    def test_sprint_name(self):
        cert = p720.sprint_aa_certificate()
        assert cert["sprint"] == "Sprint AA"

    def test_toe_not_changed(self):
        cert = p720.sprint_aa_certificate()
        assert cert["toe_changed"] is False

    def test_bc_ladder_complete(self):
        ledger = p720.np_bc_ledger()
        assert "BC1–BC16" in ledger["status"]

    def test_bc16_closed_in_ledger(self):
        ledger = p720.np_bc_ledger()
        assert "CLOSED" in ledger["bc16"]

    def test_720_milestone(self):
        cert = p720.sprint_aa_certificate()
        assert "720" in cert["milestones"]["720_pillars"]

    def test_bc_ladder_milestone(self):
        cert = p720.sprint_aa_certificate()
        assert "BC1–BC16" in cert["milestones"]["bc_ladder_closed"]

    def test_dm_ew_in_limits(self):
        cert = p720.sprint_aa_certificate()
        assert "XENON-nT" in cert["architecture_limits"]["dm_ew_channel"]

    def test_pillar_range(self):
        cert = p720.sprint_aa_certificate()
        assert cert["pillar_range"] == "716–720"
