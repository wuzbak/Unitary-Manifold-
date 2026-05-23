# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_pillar358_ckm_sin2beta_audit.py
==========================================
Test suite for Pillar 358 — CKM sin(2β) Dedicated Audit.
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar358_ckm_sin2beta_audit import (
    PILLAR_NUMBER, PILLAR_TITLE, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    LAMBDA_WLF, A_WLF, RHO_BAR, ETA_BAR,
    RHO_BAR_HISTORICAL, ETA_BAR_HISTORICAL,
    SIN2BETA_EXP, SIN2BETA_UNC,
    GAMMA_DEG_EXP, GAMMA_DEG_UNC,
    separation_guard,
    sin2beta_from_wolfenstein,
    gamma_angle_from_wolfenstein,
    historical_sin2beta,
    historical_tension_sigma,
    current_tension_sigma,
    theory_uncertainty_sin2beta,
    combined_tension_sigma,
    wolfenstein_parameter_audit,
    cabibbo_anomaly_ckm_status,
    ckm_sin2beta_full_audit,
    pillar358_summary,
)


class TestModuleConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 358

    def test_pillar_status(self):
        assert PILLAR_STATUS == "TENSION_RESOLVED"

    def test_adjacency_label(self):
        assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"

    def test_wolfenstein_lambda(self):
        assert abs(LAMBDA_WLF - 0.22500) < 1e-5

    def test_rho_bar(self):
        assert 0.10 < RHO_BAR < 0.30

    def test_eta_bar(self):
        assert 0.20 < ETA_BAR < 0.50

    def test_historical_eta_bar_larger(self):
        # Historical η̄ was larger, producing higher sin(2β)
        assert ETA_BAR_HISTORICAL > ETA_BAR

    def test_sin2beta_exp(self):
        assert abs(SIN2BETA_EXP - 0.699) < 1e-3


class TestSin2BetaFromWolfenstein:
    def test_current_value(self):
        s2b = sin2beta_from_wolfenstein()
        assert abs(s2b - 0.7194) < 0.002

    def test_range(self):
        s2b = sin2beta_from_wolfenstein()
        assert 0.0 < s2b < 1.0

    def test_symmetry_eta(self):
        # sin(2β) increases with η̄
        s2b_low = sin2beta_from_wolfenstein(rho_bar=0.152, eta_bar=0.3)
        s2b_high = sin2beta_from_wolfenstein(rho_bar=0.152, eta_bar=0.4)
        assert s2b_high > s2b_low

    def test_zero_eta(self):
        assert sin2beta_from_wolfenstein(rho_bar=0.152, eta_bar=0.0) == 0.0

    def test_custom_params(self):
        # Manual check: tan(β) = 0.360/0.848 = 0.4245
        # β = atan(0.4245) ≈ 0.402 rad → sin(2*0.402) ≈ 0.719
        s2b = sin2beta_from_wolfenstein(0.152, 0.360)
        assert abs(s2b - 0.719) < 0.002


class TestHistoricalValues:
    def test_historical_sin2beta(self):
        s2b_hist = historical_sin2beta()
        assert abs(s2b_hist - 0.823) < 0.010

    def test_historical_tension_high(self):
        # Historical σ should be high (~7σ)
        sigma_hist = historical_tension_sigma()
        assert sigma_hist > 5.0

    def test_historical_tension_known_value(self):
        # ~7.3σ from the documented changelog
        sigma_hist = historical_tension_sigma()
        assert abs(sigma_hist - 7.3) < 1.0


class TestCurrentTension:
    def test_current_tension_small(self):
        # Should be ~1.2σ
        sigma = current_tension_sigma()
        assert sigma < 3.0

    def test_current_tension_value(self):
        sigma = current_tension_sigma()
        assert abs(sigma - 1.2) < 0.5

    def test_tension_much_reduced(self):
        # Historical was ~7σ, current should be <3σ
        hist = historical_tension_sigma()
        curr = current_tension_sigma()
        assert curr < hist / 2.0


class TestTheoryUncertainty:
    def test_theory_unc_positive(self):
        assert theory_uncertainty_sin2beta() > 0

    def test_theory_unc_small(self):
        # Should be O(0.02)
        unc = theory_uncertainty_sin2beta()
        assert 0.001 < unc < 0.1

    def test_combined_sigma(self):
        sigma_comb = combined_tension_sigma()
        assert sigma_comb < 2.0  # Consistent when theory unc included

    def test_combined_less_than_exp_only(self):
        # Combined uncertainty is larger → tension smaller
        sigma_exp_only = current_tension_sigma()
        sigma_combined = combined_tension_sigma()
        assert sigma_combined <= sigma_exp_only


class TestGammaAngle:
    def test_gamma_value(self):
        gamma = gamma_angle_from_wolfenstein()
        assert 50 < gamma < 90  # Should be around 67°

    def test_gamma_specific(self):
        # arctan(0.360/0.152) ≈ 67.1°
        gamma = gamma_angle_from_wolfenstein()
        assert abs(gamma - 67.1) < 1.0

    def test_gamma_consistent_with_pdg(self):
        gamma = gamma_angle_from_wolfenstein()
        tension = abs(gamma - GAMMA_DEG_EXP) / GAMMA_DEG_UNC
        assert tension < 2.0


class TestWolfensteinParameterAudit:
    def test_returns_dict(self):
        result = wolfenstein_parameter_audit()
        assert isinstance(result, dict)

    def test_keys_present(self):
        result = wolfenstein_parameter_audit()
        for key in ["current_parameters", "historical_parameters",
                    "predictions", "experimental", "tensions", "resolution"]:
            assert key in result

    def test_historical_tension_high(self):
        result = wolfenstein_parameter_audit()
        assert result["tensions"]["historical_sigma"] > 5.0

    def test_current_tension_low(self):
        result = wolfenstein_parameter_audit()
        assert result["tensions"]["current_experimental_sigma"] < 3.0

    def test_resolution_string(self):
        result = wolfenstein_parameter_audit()
        assert "RESOLVED" in result["resolution"]
        assert "TENSION RESOLVED" in result["resolution"]

    def test_gamma_tension_low(self):
        result = wolfenstein_parameter_audit()
        assert result["tensions"]["gamma_sigma"] < 2.0


class TestCabibboAnomalyStatus:
    def test_returns_dict(self):
        result = cabibbo_anomaly_ckm_status()
        assert isinstance(result, dict)

    def test_cabibbo_anomaly_keys(self):
        result = cabibbo_anomaly_ckm_status()
        assert "cabibbo_anomaly" in result
        assert "gamma_angle" in result

    def test_gamma_consistent(self):
        result = cabibbo_anomaly_ckm_status()
        assert result["gamma_angle"]["verdict"] == "CONSISTENT"

    def test_architecture_limit_label(self):
        result = cabibbo_anomaly_ckm_status()
        assert "ARCHITECTURE_LIMIT" in result["cabibbo_anomaly"]["verdict"]

    def test_sigma_1_true_close_to_1(self):
        result = cabibbo_anomaly_ckm_status()
        sigma1 = result["cabibbo_anomaly"]["sigma_1_um_true"]
        assert abs(sigma1 - 1.0) < 0.01

    def test_vub_vcb_ratio_positive(self):
        result = cabibbo_anomaly_ckm_status()
        assert result["vub_vcb_ratio"]["prediction"] > 0


class TestFullAudit:
    def test_returns_dict(self):
        result = ckm_sin2beta_full_audit()
        assert isinstance(result, dict)

    def test_pillar_number(self):
        result = ckm_sin2beta_full_audit()
        assert result["pillar"] == 358

    def test_status(self):
        result = ckm_sin2beta_full_audit()
        assert result["status"] == "TENSION_RESOLVED"

    def test_key_finding_present(self):
        result = ckm_sin2beta_full_audit()
        assert "key_finding" in result
        assert "7σ" in result["key_finding"]
        assert "RESOLVED" in result["key_finding"]

    def test_summary_matches(self):
        summary = pillar358_summary()
        audit = ckm_sin2beta_full_audit()
        assert summary["pillar"] == audit["pillar"]


class TestSeparationGuard:
    def test_returns_string(self):
        assert isinstance(separation_guard(), str)

    def test_non_hardgate(self):
        assert "NON_HARDGATE" in separation_guard()

    def test_no_score_change(self):
        guard = separation_guard()
        assert "ToE score" in guard
