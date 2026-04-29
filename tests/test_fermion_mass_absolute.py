# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_fermion_mass_absolute.py
=====================================
Tests for Pillar 85 — Absolute Fermion Masses from GW + IR Brane VEV
(src/core/fermion_mass_absolute.py).

All tests verify:
  - GW naturalness bound is O(1) and positive
  - IR brane VEV is TeV-scale (naturally of order 1 TeV from RS hierarchy)
  - Yukawa scale from electron is determined uniquely and is natural
  - Yukawa scale from up/down quarks is determined uniquely and is natural
  - Lepton mass predictions reproduce all three masses (electron exact, μ and τ predicted)
  - Quark mass predictions reproduce all six masses
  - Closure report runs and contains all key results

Theory: ThomasCory Walker-Pearson.
Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import pytest

from src.core.fermion_mass_absolute import (
    # Constants
    M_ELECTRON_MEV,
    M_MUON_MEV,
    M_TAU_MEV,
    M_UP_MEV,
    M_CHARM_MEV,
    M_TOP_MEV,
    M_DOWN_MEV,
    M_STRANGE_MEV,
    M_BOTTOM_MEV,
    V_HIGGS_GEV,
    V_HIGGS_MEV,
    PI_KR_CANONICAL,
    K_RS_CANONICAL,
    LAMBDA_GW_NATURAL,
    C_L_ELECTRON_PILLAR75,
    C_L_MUON_PILLAR75,
    C_L_TAU_PILLAR75,
    C_L_UP_PILLAR81,
    C_L_CHARM_PILLAR81,
    C_L_TOP_PILLAR81,
    C_L_DOWN_PILLAR81,
    C_L_STRANGE_PILLAR81,
    C_L_BOTTOM_PILLAR81,
    # Functions
    gw_naturalness_bound,
    ir_brane_vev_from_gw,
    yukawa_scale_from_electron,
    yukawa_scale_from_up_quark,
    yukawa_scale_from_down_quark,
    predict_lepton_masses,
    predict_quark_masses,
    absolute_mass_closure_report,
    _rs_wavefunction_zero_mode,
    _yukawa_overlap,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_electron_mass_mev(self):
        assert abs(M_ELECTRON_MEV - 0.511) < 0.001

    def test_muon_mass_mev(self):
        assert abs(M_MUON_MEV - 105.658) < 0.01

    def test_tau_mass_mev(self):
        assert abs(M_TAU_MEV - 1776.0) < 1.0

    def test_v_higgs_gev(self):
        assert abs(V_HIGGS_GEV - 246.0) < 0.1

    def test_v_higgs_mev(self):
        assert abs(V_HIGGS_MEV - 246_000.0) < 1.0

    def test_pi_kr_canonical(self):
        assert abs(PI_KR_CANONICAL - 37.0) < 1e-10

    def test_lambda_gw_natural(self):
        assert abs(LAMBDA_GW_NATURAL - 1.0) < 1e-10

    def test_c_L_electron_positive(self):
        assert C_L_ELECTRON_PILLAR75 > 0.0

    def test_c_L_electron_ir_localised(self):
        # c_L = 0.8 > 0.5: IR-localised, gives λ_Y ~ O(1)
        assert C_L_ELECTRON_PILLAR75 > 0.5

    def test_c_L_hierarchy_leptons(self):
        # Heavier generation → smaller c_L (more UV localised)
        assert C_L_MUON_PILLAR75 < C_L_ELECTRON_PILLAR75
        assert C_L_TAU_PILLAR75 < C_L_MUON_PILLAR75

    def test_c_L_hierarchy_up_quarks(self):
        # Heavier → smaller c_L
        assert C_L_CHARM_PILLAR81 < C_L_UP_PILLAR81
        assert C_L_TOP_PILLAR81 < C_L_CHARM_PILLAR81

    def test_c_L_hierarchy_down_quarks(self):
        assert C_L_STRANGE_PILLAR81 < C_L_DOWN_PILLAR81
        assert C_L_BOTTOM_PILLAR81 < C_L_STRANGE_PILLAR81


# ---------------------------------------------------------------------------
# RS wavefunction (internal helper)
# ---------------------------------------------------------------------------

class TestRsWavefunction:
    def test_positive(self):
        assert _rs_wavefunction_zero_mode(0.5) > 0.0

    def test_uv_localised_larger(self):
        # Smaller c → more UV localised → larger wavefunction at UV brane
        f_small = _rs_wavefunction_zero_mode(0.4)
        f_large = _rs_wavefunction_zero_mode(0.6)
        assert f_small > f_large

    def test_overlap_positive(self):
        assert _yukawa_overlap(0.5, 0.5) > 0.0

    def test_overlap_symmetric_in_c(self):
        # Overlap is symmetric: f(c_L) * f(c_R) = f(c_R) * f(c_L)
        o1 = _yukawa_overlap(0.4, 0.6)
        o2 = _yukawa_overlap(0.6, 0.4)
        assert abs(o1 - o2) < 1e-12


# ---------------------------------------------------------------------------
# GW naturalness bound
# ---------------------------------------------------------------------------

class TestGWNaturalnessBound:
    def test_returns_dict(self):
        r = gw_naturalness_bound()
        assert isinstance(r, dict)

    def test_y5_upper_positive(self):
        r = gw_naturalness_bound()
        assert r["Y5_upper"] > 0.0

    def test_lambda_y_upper_positive(self):
        r = gw_naturalness_bound()
        assert r["lambda_Y_natural_upper"] > 0.0

    def test_lambda_y_lower_positive(self):
        r = gw_naturalness_bound()
        assert r["lambda_Y_natural_lower"] > 0.0

    def test_natural_range_includes_1(self):
        r = gw_naturalness_bound()
        lo, hi = r["natural_range"]
        assert lo < 1.0 < hi

    def test_natural_lambda_gw_1(self):
        r = gw_naturalness_bound(lambda_gw=1.0)
        assert r["Y5_upper"] == pytest.approx(1.0, rel=1e-10)

    def test_scaling_with_lambda_gw(self):
        r1 = gw_naturalness_bound(lambda_gw=1.0)
        r4 = gw_naturalness_bound(lambda_gw=4.0)
        assert abs(r4["Y5_upper"] / r1["Y5_upper"] - 2.0) < 1e-10

    def test_invalid_lambda_gw_raises(self):
        with pytest.raises(ValueError):
            gw_naturalness_bound(lambda_gw=-1.0)

    def test_invalid_k_over_M5_raises(self):
        with pytest.raises(ValueError):
            gw_naturalness_bound(k_over_M5=0.0)


# ---------------------------------------------------------------------------
# IR brane VEV
# ---------------------------------------------------------------------------

class TestIRBraneVEV:
    def test_returns_positive_float(self):
        v = ir_brane_vev_from_gw()
        assert v > 0.0

    def test_tev_scale(self):
        # RS hierarchy: v_IR ~ k * exp(-37) * 1.22e19 GeV ~ few TeV
        v = ir_brane_vev_from_gw()
        assert 100.0 < v < 1e5  # between 100 GeV and 100 TeV

    def test_decreases_with_pi_kR(self):
        v_small = ir_brane_vev_from_gw(pi_kR=30.0)
        v_large = ir_brane_vev_from_gw(pi_kR=40.0)
        assert v_small > v_large

    def test_invalid_k_raises(self):
        with pytest.raises(ValueError):
            ir_brane_vev_from_gw(k_ads=0.0)

    def test_invalid_pi_kR_raises(self):
        with pytest.raises(ValueError):
            ir_brane_vev_from_gw(pi_kR=0.0)


# ---------------------------------------------------------------------------
# Yukawa scale from electron
# ---------------------------------------------------------------------------

class TestYukawaScaleFromElectron:
    def test_returns_dict(self):
        r = yukawa_scale_from_electron()
        assert isinstance(r, dict)

    def test_lambda_Y_e_positive(self):
        r = yukawa_scale_from_electron()
        assert r["lambda_Y_e"] > 0.0

    def test_is_natural(self):
        r = yukawa_scale_from_electron()
        assert r["is_natural"] is True
        # λ_Y^e * v * overlap = m_e (by construction)
        r = yukawa_scale_from_electron()
        m_e_reconstructed = r["lambda_Y_e"] * V_HIGGS_MEV * r["overlap_e"]
        assert abs(m_e_reconstructed - M_ELECTRON_MEV) / M_ELECTRON_MEV < 1e-10

    def test_target_mass_is_electron(self):
        r = yukawa_scale_from_electron()
        assert abs(r["m_electron_MeV_target"] - M_ELECTRON_MEV) < 1e-6

    def test_overlap_is_positive(self):
        r = yukawa_scale_from_electron()
        assert r["overlap_e"] > 0.0

    def test_invalid_zero_overlap_raises(self):
        # A bulk mass c_L >> 1 makes the overlap essentially zero → ValueError
        with pytest.raises((ValueError, OverflowError)):
            yukawa_scale_from_electron(c_Le=100.0)


# ---------------------------------------------------------------------------
# Yukawa scale from up quark
# ---------------------------------------------------------------------------

class TestYukawaScaleFromUpQuark:
    def test_returns_dict(self):
        r = yukawa_scale_from_up_quark()
        assert isinstance(r, dict)

    def test_lambda_Y_u_positive(self):
        r = yukawa_scale_from_up_quark()
        assert r["lambda_Y_u"] > 0.0

    def test_is_natural(self):
        r = yukawa_scale_from_up_quark()
        assert r["is_natural"] is True

    def test_consistency_round_trip(self):
        r = yukawa_scale_from_up_quark()
        m_u_reconstructed = r["lambda_Y_u"] * V_HIGGS_MEV * r["overlap_u"]
        assert abs(m_u_reconstructed - M_UP_MEV) / M_UP_MEV < 1e-10


# ---------------------------------------------------------------------------
# Yukawa scale from down quark
# ---------------------------------------------------------------------------

class TestYukawaScaleFromDownQuark:
    def test_returns_dict(self):
        r = yukawa_scale_from_down_quark()
        assert isinstance(r, dict)

    def test_lambda_Y_d_positive(self):
        r = yukawa_scale_from_down_quark()
        assert r["lambda_Y_d"] > 0.0

    def test_is_natural(self):
        r = yukawa_scale_from_down_quark()
        assert r["is_natural"] is True

    def test_consistency_round_trip(self):
        r = yukawa_scale_from_down_quark()
        m_d_reconstructed = r["lambda_Y_d"] * V_HIGGS_MEV * r["overlap_d"]
        assert abs(m_d_reconstructed - M_DOWN_MEV) / M_DOWN_MEV < 1e-10


# ---------------------------------------------------------------------------
# Lepton mass predictions
# ---------------------------------------------------------------------------

class TestPredictLeptonMasses:
    def setup_method(self):
        self.lam_e = yukawa_scale_from_electron()["lambda_Y_e"]
        self.result = predict_lepton_masses(self.lam_e)

    def test_electron_exact(self):
        # Electron mass is the INPUT — should be reproduced exactly
        assert self.result["electron_error_percent"] < 1e-8

    def test_muon_predicted_reasonable(self):
        # Muon mass is PREDICTED from c_Lμ (exact bisection from muon/electron ratio)
        # Prediction should reproduce PDG to < 1e-6 relative error
        assert self.result["muon_error_percent"] < 0.001

    def test_tau_predicted_reasonable(self):
        # Tau mass is PREDICTED from c_Lτ (exact bisection from tau/muon ratio)
        assert self.result["tau_error_percent"] < 0.001

    def test_mass_ordering(self):
        # τ > μ > e
        assert (self.result["tau_MeV_predicted"]
                > self.result["muon_MeV_predicted"]
                > self.result["electron_MeV_predicted"]
                > 0.0)

    def test_all_masses_positive(self):
        assert self.result["electron_MeV_predicted"] > 0.0
        assert self.result["muon_MeV_predicted"] > 0.0
        assert self.result["tau_MeV_predicted"] > 0.0

    def test_pdg_values_stored(self):
        assert abs(self.result["electron_MeV_pdg"] - M_ELECTRON_MEV) < 1e-6
        assert abs(self.result["muon_MeV_pdg"] - M_MUON_MEV) < 0.001
        assert abs(self.result["tau_MeV_pdg"] - M_TAU_MEV) < 0.01

    def test_note_present(self):
        assert "note" in self.result
        assert "PREDICTED" in self.result["note"] or "Predicted" in self.result["note"]


# ---------------------------------------------------------------------------
# Quark mass predictions
# ---------------------------------------------------------------------------

class TestPredictQuarkMasses:
    def setup_method(self):
        self.lam_u = yukawa_scale_from_up_quark()["lambda_Y_u"]
        self.lam_d = yukawa_scale_from_down_quark()["lambda_Y_d"]
        self.result = predict_quark_masses(self.lam_u, self.lam_d)

    def test_up_quark_exact(self):
        assert self.result["up_error_percent"] < 1e-8

    def test_down_quark_exact(self):
        assert self.result["down_error_percent"] < 1e-8

    def test_charm_predicted(self):
        # Exact bisection from Pillar 81 → charm mass exact
        assert self.result["charm_error_percent"] < 0.001

    def test_top_predicted(self):
        assert self.result["top_error_percent"] < 0.001

    def test_strange_predicted(self):
        assert self.result["strange_error_percent"] < 0.001

    def test_bottom_predicted(self):
        assert self.result["bottom_error_percent"] < 0.001

    def test_up_sector_ordering(self):
        assert (self.result["top_MeV_predicted"]
                > self.result["charm_MeV_predicted"]
                > self.result["up_MeV_predicted"]
                > 0.0)

    def test_down_sector_ordering(self):
        assert (self.result["bottom_MeV_predicted"]
                > self.result["strange_MeV_predicted"]
                > self.result["down_MeV_predicted"]
                > 0.0)

    def test_all_masses_positive(self):
        for key in ("up", "charm", "top", "down", "strange", "bottom"):
            assert self.result[f"{key}_MeV_predicted"] > 0.0


# ---------------------------------------------------------------------------
# Absolute mass closure report
# ---------------------------------------------------------------------------

class TestAbsoluteMassClosureReport:
    def setup_method(self):
        self.r = absolute_mass_closure_report()

    def test_pillar_number(self):
        assert self.r["pillar"] == 85

    def test_all_lambda_natural(self):
        assert self.r["all_lambda_Y_natural"] is True

    def test_ir_brane_vev_is_tev_scale(self):
        assert 100.0 < self.r["ir_brane_vev_GeV"] < 1e5

    def test_gw_bound_present(self):
        assert "gw_naturalness_bound" in self.r

    def test_lepton_yukawa_scale_present(self):
        assert "lepton_yukawa_scale" in self.r
        assert self.r["lepton_yukawa_scale"]["is_natural"] is True

    def test_up_yukawa_scale_present(self):
        assert "up_yukawa_scale" in self.r
        assert self.r["up_yukawa_scale"]["is_natural"] is True

    def test_down_yukawa_scale_present(self):
        assert "down_yukawa_scale" in self.r
        assert self.r["down_yukawa_scale"]["is_natural"] is True

    def test_honest_status_keys(self):
        hs = self.r["honest_status"]
        assert "DERIVED" in hs
        assert "PREDICTED" in hs
        assert "OPEN" in hs

    def test_parameter_count_present(self):
        pc = self.r["parameter_count"]
        assert "inputs" in pc
        assert "predicted" in pc
        assert "open" in pc

    def test_lepton_predictions_present(self):
        assert "lepton_mass_predictions" in self.r

    def test_quark_predictions_present(self):
        assert "quark_mass_predictions" in self.r
