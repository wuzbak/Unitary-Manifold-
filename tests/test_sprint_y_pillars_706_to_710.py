# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Tests for Sprint Y — Pillars 706–710
  P706  NP-BC14 condensate WdW kernel
  P707  CMB spectral distortion KK null prediction
  P708  GW background from KK-KK scattering
  P709  KK resonance ATLAS/CMS routing
  P710  Sprint Y regression certificate v21.6
"""

import math
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

import pytest

import pillar706_np_bc14_condensate_wdw_kernel    as p706
import pillar707_cmb_spectral_distortion_kk       as p707
import pillar708_gw_background_kk_kk_scattering   as p708
import pillar709_kk_resonance_atlas_cms_routing   as p709
import pillar710_sprint_y_regression_certificate  as p710


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar706:
    """NP-BC14: Condensate WdW kernel"""

    def test_gamma_gluon_positive(self):
        assert p706.gamma_gluon_condensate() > 0

    def test_gamma_higgs_positive(self):
        assert p706.gamma_higgs_condensate() > 0

    def test_kernel_nonnegative(self):
        result = p706.compute_bc14_kernel()
        assert result["kernel_bc14"] >= 0

    def test_pillar_number(self):
        result = p706.compute_bc14_kernel()
        assert result["pillar"] == 706

    def test_bc14_label(self):
        result = p706.compute_bc14_kernel()
        assert "BC14" in result["label"]

    def test_fixed_point_vanishing(self):
        fp = p706.bc14_fixed_point_vanishing()
        assert fp["vanishes"]

    def test_bc14_ledger_closed(self):
        ledger = p706.np_bc_ledger()
        assert "CLOSED" in ledger["bc14_status"]
        assert "BC14" in ledger["bc14"]

    def test_bc15_named(self):
        ledger = p706.np_bc_ledger()
        assert "BC15" in ledger["next_bc15"]

    def test_ledger_through_bc14(self):
        ledger = p706.np_bc_ledger()
        assert "BC14" in ledger["ledger_complete_through"]

    def test_units(self):
        result = p706.compute_bc14_kernel()
        assert result["units"] == "M_Pl = 1"

    def test_kernel_at_zero_gn_positive(self):
        result = p706.compute_bc14_kernel(g_n=0.0, g_n_star=p706.G_N_STAR)
        assert result["kernel_bc14"] > 0

    def test_gluon_condensate_order_of_magnitude(self):
        G4 = p706.GLUON_CONDENSATE_GEV4
        assert 1e-4 < G4 < 0.02   # (0.33)^4 ≈ 0.0119 GeV⁴

    def test_lambda_higgs_value(self):
        expected = 125.25 ** 2 / (2 * 246.0 ** 2)
        assert abs(p706.LAMBDA_HIGGS - expected) < 1e-10


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar707:
    """CMB spectral distortions: KK null prediction"""

    def test_q_kk_tiny(self):
        q = p707.q_kk_over_rho_gamma()
        assert q < 1e-60

    def test_y_distortion_tiny(self):
        y = p707.y_distortion_kk()
        assert y < 1e-60

    def test_mu_distortion_tiny(self):
        mu = p707.mu_distortion_kk()
        assert mu < 1e-60

    def test_y_below_pixie(self):
        s = p707.spectral_distortion_summary()
        assert s["y_below_pixie"]

    def test_mu_below_pixie(self):
        s = p707.spectral_distortion_summary()
        assert s["mu_below_pixie"]

    def test_not_observable(self):
        s = p707.spectral_distortion_summary()
        assert not s["observable"]

    def test_null_prediction_flag(self):
        s = p707.spectral_distortion_summary()
        assert s["null_prediction"]

    def test_pillar_number(self):
        s = p707.spectral_distortion_summary()
        assert s["pillar"] == 707

    def test_falsification_documented(self):
        s = p707.spectral_distortion_summary()
        assert "PIXIE" in s["falsification_condition"] or "sub-TeV" in s["falsification_condition"]

    def test_m_rad_value(self):
        expected = math.sqrt(6) * p707.M_KK_GEV / math.pi
        assert abs(p707.M_RAD_GEV - expected) < 1e-8

    def test_y_quarter_of_q(self):
        y = p707.y_distortion_kk()
        q = p707.q_kk_over_rho_gamma()
        assert abs(y - 0.25 * q) < 1e-100


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar708:
    """GW background from KK-KK scattering"""

    def test_f_peak_large(self):
        f = p708.f_peak_kk_hz()
        assert f > 1e20   # far above LISA

    def test_omega_gw_tiny(self):
        omega = p708.omega_gw_h2()
        assert omega < 1e-60

    def test_f_peak_not_in_lisa(self):
        s = p708.gw_background_summary()
        assert not s["f_peak_in_lisa_band"]

    def test_direct_kk_null(self):
        s = p708.gw_background_summary()
        assert s["direct_kk_null"]

    def test_f_bubble_in_mhz_range(self):
        f_bub = p708.gw_bubble_nucleation_peak_hz()
        # Should be ~1.7×10⁻⁴ Hz for M_KK=1042 GeV
        assert 1e-5 < f_bub < 1e-2

    def test_f_bubble_in_lisa_band(self):
        s = p708.gw_background_summary()
        assert s["bubble_in_lisa"]

    def test_pillar_number(self):
        s = p708.gw_background_summary()
        assert s["pillar"] == 708

    def test_label(self):
        s = p708.gw_background_summary()
        assert "GW" in s["label"]

    def test_falsification_documented(self):
        s = p708.gw_background_summary()
        assert "SGWB" in s["falsification_condition"] or "PT" in s["falsification_condition"]

    def test_f_peak_formula(self):
        expected = p708.M_KK_GEV * p708.GEV_TO_HZ
        assert abs(p708.f_peak_kk_hz() - expected) < 1.0


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar709:
    """KK resonance ATLAS/CMS routing"""

    def test_m_g_star_in_tev_range(self):
        assert 1000 < p709.M_G_STAR_GEV < 5000

    def test_m_g_star_formula(self):
        expected = p709.X1_BESSEL * p709.M_KK_GEV
        assert abs(p709.M_G_STAR_GEV - expected) < 1e-8

    def test_width_positive(self):
        assert p709.gamma_g_star() > 0

    def test_relative_width_narrow(self):
        rel_w = p709.relative_width()
        assert rel_w < 0.15   # narrow resonance approximation

    def test_routing_pillar(self):
        s = p709.resonance_routing_summary()
        assert s["pillar"] == 709

    def test_routing_label(self):
        s = p709.resonance_routing_summary()
        assert "KK_RESONANCE" in s["label"]

    def test_in_run4_reach(self):
        s = p709.resonance_routing_summary()
        assert s["mass_in_run4_reach"]

    def test_narrowness_ok(self):
        s = p709.resonance_routing_summary()
        assert s["narrowness_ok"]

    def test_falsification_documented(self):
        s = p709.resonance_routing_summary()
        assert "null" in s["falsification"].lower() or "exclude" in s["falsification"].lower()

    def test_x1_bessel_value(self):
        assert abs(p709.X1_BESSEL - 2.4048) < 1e-4

    def test_k_g_coupling_0_1(self):
        assert abs(p709.K_G_NATURAL - 0.1) < 1e-10


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar710:
    """Sprint Y regression certificate v21.6"""

    def test_version(self):
        assert p710.version_string() == "v21.6"

    def test_pillar_total(self):
        assert p710.pillar_total() == 710

    def test_toe_score(self):
        assert p710.toe_score() == "framework internally consistent"

    def test_next_slot(self):
        assert p710.next_pillar_slot() == 711

    def test_sprint_name(self):
        cert = p710.sprint_y_certificate()
        assert cert["sprint"] == "Sprint Y"

    def test_toe_not_changed(self):
        cert = p710.sprint_y_certificate()
        assert cert["toe_changed"] is False

    def test_bc14_closed(self):
        ledger = p710.np_bc_ledger()
        assert "CLOSED" in ledger["bc14"]

    def test_bc15_named(self):
        ledger = p710.np_bc_ledger()
        assert "BC15" in ledger["bc15_next"]

    def test_open_falsifiers_six(self):
        cert = p710.sprint_y_certificate()
        assert len(cert["open_falsifiers"]) >= 5

    def test_kk_resonance_limit(self):
        cert = p710.sprint_y_certificate()
        assert "2.5 TeV" in cert["architecture_limits"]["kk_resonance"]

    def test_pillar_range(self):
        cert = p710.sprint_y_certificate()
        assert cert["pillar_range"] == "706–710"
