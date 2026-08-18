# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 683: PMNS Reactor Angle θ₁₃ from 5D KK Wavefunction Overlaps."""

from __future__ import annotations

import math
import pytest

from src.core.pillar683_pmns_theta13_kk_overlap import (
    N_W, K_CS, KR_5D, LAMBDA_CABIBBO,
    SIN2_THETA13_PDG, SIN2_THETA13_PDG_ERR, SIN_THETA13_PDG, THETA13_PDG_DEG,
    DC_NU_13, FN_CHARGE_Q13, PI_KR,
    ir_wavefunction_value,
    kk_overlap_sin_theta13,
    calibrated_dc_nu13,
    sin2_theta13_prediction,
    self_consistency_check,
    reactor_angle_certificate,
    what_is_claimed,
    what_is_NOT_claimed,
    PILLAR_NUMBER, PILLAR_STATUS, VERSION,
)


# ── Constants ─────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 683


def test_version():
    assert VERSION == "v21.1"


def test_n_w_k_cs():
    assert N_W == 5
    assert K_CS == 74


def test_kr_5d():
    assert abs(KR_5D - 74.0 / 5.0) < 1e-10


def test_pi_kr():
    assert abs(PI_KR - math.pi * KR_5D) < 1e-10


def test_sin2_theta13_pdg_range():
    # PDG 2022: 0.02220 ± 0.00068
    assert abs(SIN2_THETA13_PDG - 0.02220) < 0.0001


def test_sin_theta13_pdg():
    assert abs(SIN_THETA13_PDG - math.sqrt(SIN2_THETA13_PDG)) < 1e-12


def test_theta13_pdg_deg():
    expected = math.degrees(math.asin(SIN_THETA13_PDG))
    assert abs(THETA13_PDG_DEG - expected) < 1e-10


def test_theta13_pdg_deg_range():
    # θ₁₃ ≈ 8.57°
    assert 8.0 < THETA13_PDG_DEG < 9.5


def test_lambda_cabibbo_range():
    assert 0.220 < LAMBDA_CABIBBO < 0.230


def test_fn_charge_q13():
    assert FN_CHARGE_Q13 == 1


def test_dc_nu13_physical():
    # Δc should be small positive (< 0.1)
    assert 0 < DC_NU_13 < 0.1


def test_dc_nu13_formula():
    # DC_NU_13 = -ln(sin_theta13 / lambda_C) / (pi * kr)
    expected = -math.log(SIN_THETA13_PDG / LAMBDA_CABIBBO) / PI_KR
    assert abs(DC_NU_13 - expected) < 1e-12


# ── ir_wavefunction_value ─────────────────────────────────────────────────────

def test_ir_wavefunction_c_half():
    # At c = 0.5 (flat profile): f = exp(0) = 1
    assert abs(ir_wavefunction_value(0.5) - 1.0) < 1e-10


def test_ir_wavefunction_c_above_half():
    # c > 0.5: UV-peaked, IR value suppressed < 1
    val = ir_wavefunction_value(0.6)
    assert val < 1.0
    assert val > 0


def test_ir_wavefunction_c_below_half():
    # c < 0.5: IR-peaked, wavefunction at IR > 1
    val = ir_wavefunction_value(0.4)
    assert val > 1.0


def test_ir_wavefunction_formula():
    c = 0.505
    expected = math.exp((0.5 - c) * PI_KR)
    assert abs(ir_wavefunction_value(c) - expected) < 1e-10


# ── kk_overlap_sin_theta13 ────────────────────────────────────────────────────

def test_kk_overlap_positive():
    val = kk_overlap_sin_theta13(DC_NU_13)
    assert val > 0


def test_kk_overlap_less_than_one():
    val = kk_overlap_sin_theta13(DC_NU_13)
    assert val < 1.0


def test_kk_overlap_at_dc_zero():
    # When Δc = 0: sin θ₁₃ = λ_C (just the FN suppression)
    val = kk_overlap_sin_theta13(0.0, q13=1)
    assert abs(val - LAMBDA_CABIBBO) < 1e-10


def test_kk_overlap_larger_dc_smaller():
    # Larger Δc → smaller sin θ₁₃
    val1 = kk_overlap_sin_theta13(0.001)
    val2 = kk_overlap_sin_theta13(0.01)
    assert val1 > val2


def test_kk_overlap_formula():
    dc = 0.005
    expected = LAMBDA_CABIBBO * math.exp(-dc * PI_KR)
    assert abs(kk_overlap_sin_theta13(dc, 1) - expected) < 1e-12


# ── calibrated_dc_nu13 ────────────────────────────────────────────────────────

def test_calibrated_dc_keys():
    c = calibrated_dc_nu13()
    for k in ["dc_nu_13", "pi_kr", "lambda_cabibbo", "sin_theta13_pdg",
              "sin_theta13_5d", "ratio_sin_lambda", "dc_physical_range"]:
        assert k in c


def test_calibrated_dc_match_pdg():
    c = calibrated_dc_nu13()
    # sin_theta13_5d should match sin_theta13_pdg (calibrated by construction)
    assert abs(c["sin_theta13_5d"] - c["sin_theta13_pdg"]) < 1e-10


def test_calibrated_ratio():
    c = calibrated_dc_nu13()
    expected_ratio = SIN_THETA13_PDG / LAMBDA_CABIBBO
    assert abs(c["ratio_sin_lambda"] - expected_ratio) < 1e-12


def test_calibrated_dc_physical():
    c = calibrated_dc_nu13()
    assert c["dc_physical_range"] is True


# ── sin2_theta13_prediction ───────────────────────────────────────────────────

def test_sin2_prediction_keys():
    pred = sin2_theta13_prediction()
    for k in ["sin2_theta13_5d", "sin2_theta13_pdg", "residual_pct",
              "sigma_away", "theta13_5d_deg", "theta13_pdg_deg"]:
        assert k in pred


def test_sin2_prediction_residual_small():
    pred = sin2_theta13_prediction()
    # Residual < 0.5% by calibration
    assert pred["residual_pct"] < 0.5


def test_sin2_prediction_sigma_small():
    pred = sin2_theta13_prediction()
    assert pred["sigma_away"] < 1.0


def test_sin2_prediction_theta13_deg():
    pred = sin2_theta13_prediction()
    assert 8.0 < pred["theta13_5d_deg"] < 9.5


def test_sin2_prediction_dc_positive():
    pred = sin2_theta13_prediction()
    assert pred["dc_nu13"] > 0


def test_sin2_prediction_formula_string():
    pred = sin2_theta13_prediction()
    assert "λ_C" in pred["formula"] or "lambda" in pred["formula"].lower()


# ── self_consistency_check ────────────────────────────────────────────────────

def test_self_consistency_passes():
    sc = self_consistency_check()
    assert sc["self_consistent"] is True


def test_self_consistency_residual_ok():
    sc = self_consistency_check()
    assert sc["residual_ok"] is True


def test_self_consistency_dc_physical():
    sc = self_consistency_check()
    assert sc["dc_physical"] is True


def test_self_consistency_caveat():
    sc = self_consistency_check()
    assert "construction" in sc["caveat"].lower()


def test_self_consistency_has_prediction():
    sc = self_consistency_check()
    assert "prediction" in sc
    assert "sin2_theta13_5d" in sc["prediction"]


# ── reactor_angle_certificate ─────────────────────────────────────────────────

def test_certificate_keys():
    cert = reactor_angle_certificate()
    for k in ["pillar", "title", "version", "status", "sin2_theta13_pdg",
              "residual_pct", "claimed", "not_claimed", "next_steps"]:
        assert k in cert


def test_certificate_pillar():
    cert = reactor_angle_certificate()
    assert cert["pillar"] == 683


def test_certificate_status():
    assert PILLAR_STATUS == "PMNS_THETA13_KK_OVERLAP_CONSISTENCY_CHECKED"
    cert = reactor_angle_certificate()
    assert cert["status"] == PILLAR_STATUS


def test_certificate_toe_zero():
    cert = reactor_angle_certificate()
    assert "0" in cert["toe_impact"]


def test_certificate_next_steps():
    cert = reactor_angle_certificate()
    assert len(cert["next_steps"]) >= 2


def test_certificate_fn_charge():
    cert = reactor_angle_certificate()
    assert cert["fn_charge_q13"] == 1


# ── claimed / not_claimed ─────────────────────────────────────────────────────

def test_claimed_list():
    c = what_is_claimed()
    assert isinstance(c, list)
    assert len(c) >= 4


def test_not_claimed_list():
    nc = what_is_NOT_claimed()
    assert isinstance(nc, list)
    assert len(nc) >= 3


def test_not_claimed_no_ab_initio():
    for item in what_is_NOT_claimed():
        if "ab initio" in item.lower() or "calibrated" in item.lower():
            break
    else:
        pytest.fail("not_claimed should mention calibrated/ab-initio caveat")


# ── Numerical consistency ─────────────────────────────────────────────────────

def test_sin2_theta13_equals_sin_squared():
    pred = sin2_theta13_prediction()
    sin_t13 = pred["sin_theta13_5d"]
    sin2_t13 = pred["sin2_theta13_5d"]
    assert abs(sin2_t13 - sin_t13**2) < 1e-15


def test_dc_nu13_recovers_pdg():
    # sin θ₁₃ = λ_C × exp(−DC_NU_13 × PI_KR) should equal SIN_THETA13_PDG
    predicted = LAMBDA_CABIBBO * math.exp(-DC_NU_13 * PI_KR)
    assert abs(predicted - SIN_THETA13_PDG) < 1e-12


def test_kr_5d_equals_k_cs_over_n_w():
    assert abs(KR_5D - K_CS / N_W) < 1e-10
