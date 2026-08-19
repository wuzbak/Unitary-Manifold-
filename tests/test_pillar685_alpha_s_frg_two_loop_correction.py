# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 685: α_s Two-Loop fRG Correction from NP-BC8 WdW Fixed Point."""

from __future__ import annotations

import math
import pytest

from src.core.pillar685_alpha_s_frg_two_loop_correction import (
    N_W, K_CS, PI_KR, G_N_STAR, M_KK_NATURAL, M_KK_SQ_OVER_MPL_SQ,
    ALPHA_S_PDG, ALPHA_S_ADS_QCD, FRG_RELATIVE_CORRECTION,
    frg_gravity_correction,
    combined_alpha_s_maximum,
    architecture_limit_precision_audit,
    alpha_s_frg_certificate,
    what_is_claimed,
    what_is_NOT_claimed,
    PILLAR_NUMBER, PILLAR_STATUS, VERSION,
)


# ── Constants ─────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 685


def test_version():
    assert VERSION == "v21.1"


def test_n_w_k_cs():
    assert N_W == 5
    assert K_CS == 74


def test_pi_kr():
    expected = math.pi * K_CS / N_W
    assert abs(PI_KR - expected) < 1e-10


def test_g_n_star():
    expected = 3.0 * math.pi / (N_W * K_CS - 10)
    assert abs(G_N_STAR - expected) < 1e-12


def test_m_kk_natural():
    expected = math.exp(-PI_KR)
    assert abs(M_KK_NATURAL - expected) < 1e-25


def test_m_kk_sq_over_mpl_sq():
    expected = M_KK_NATURAL ** 2
    assert abs(M_KK_SQ_OVER_MPL_SQ - expected) < 1e-50


def test_alpha_s_pdg():
    assert abs(ALPHA_S_PDG - 0.118) < 0.001


def test_alpha_s_ads_qcd():
    expected = math.pi**2 / (2 * K_CS)
    assert abs(ALPHA_S_ADS_QCD - expected) < 1e-12


def test_alpha_s_ads_range():
    # Should be ~0.0667
    assert 0.06 < ALPHA_S_ADS_QCD < 0.08


def test_frg_relative_correction_tiny():
    # Should be ~10^-43 — completely negligible
    assert FRG_RELATIVE_CORRECTION < 1e-30


def test_frg_relative_correction_positive():
    # |correction| is positive (magnitude)
    assert FRG_RELATIVE_CORRECTION >= 0


# ── frg_gravity_correction ────────────────────────────────────────────────────

def test_frg_correction_keys():
    frg = frg_gravity_correction()
    for k in ["g_n_star", "m_kk_sq_over_mpl_sq", "frg_relative_correction",
              "alpha_s_ads_qcd", "delta_alpha_s_frg", "correction_is_negligible"]:
        assert k in frg


def test_frg_correction_negligible():
    frg = frg_gravity_correction()
    assert frg["correction_is_negligible"] is True


def test_frg_delta_alpha_s_tiny():
    frg = frg_gravity_correction()
    assert abs(frg["delta_alpha_s_frg"]) < 1e-30


def test_frg_delta_alpha_s_negative():
    frg = frg_gravity_correction()
    assert frg["delta_alpha_s_frg"] < 0


def test_frg_alpha_s_corrected_close_to_ads():
    frg = frg_gravity_correction()
    # Corrected value should be virtually identical to AdS/QCD value
    assert abs(frg["alpha_s_with_frg"] - ALPHA_S_ADS_QCD) < 1e-30


def test_frg_formula_string():
    frg = frg_gravity_correction()
    assert "Δα_s" in frg["formula"] or "alpha" in frg["formula"].lower()


# ── combined_alpha_s_maximum ──────────────────────────────────────────────────

def test_combined_keys():
    c = combined_alpha_s_maximum()
    for k in ["alpha_s_pdg", "alpha_s_ads_qcd", "alpha_s_maximum",
              "residual_pct", "architecture_limit"]:
        assert k in c


def test_combined_architecture_limit():
    c = combined_alpha_s_maximum()
    assert c["architecture_limit"] is True


def test_combined_residual_large():
    c = combined_alpha_s_maximum()
    # Residual > 35% (architecture limit)
    assert c["residual_pct"] > 35.0


def test_combined_alpha_max_below_pdg():
    c = combined_alpha_s_maximum()
    assert c["alpha_s_maximum"] < ALPHA_S_PDG


def test_combined_f_gw_above_one():
    c = combined_alpha_s_maximum()
    assert c["f_gw"] > 1.0


def test_combined_frg_improvement_negligible():
    c = combined_alpha_s_maximum()
    # fRG improvement over GW is tiny
    assert c["frg_improvement_over_gw"] < 1e-30


def test_combined_alpha_gw_above_ads():
    c = combined_alpha_s_maximum()
    assert c["alpha_s_gw"] > c["alpha_s_ads_qcd"]


# ── architecture_limit_precision_audit ───────────────────────────────────────

def test_audit_confirmed():
    audit = architecture_limit_precision_audit()
    assert audit["architecture_limit_confirmed"] is True


def test_audit_minimum_residual_above_35():
    audit = architecture_limit_precision_audit()
    assert audit["minimum_residual_pct"] > 35.0


def test_audit_certified_floor():
    audit = architecture_limit_precision_audit()
    assert audit["certified_floor_residual_pct"] == 40.0


def test_audit_frg_negligibility_string():
    audit = architecture_limit_precision_audit()
    assert isinstance(audit["frg_negligibility"], str)
    assert "negligible" in audit["frg_negligibility"].lower()


def test_audit_status_token():
    audit = architecture_limit_precision_audit()
    assert audit["status_token"] == PILLAR_STATUS


def test_audit_corrections_keys():
    audit = architecture_limit_precision_audit()
    corrections = audit["corrections"]
    for k in ["ads_qcd_base_pct", "gw_vev_improvement_pct", "frg_correction_relative"]:
        assert k in corrections


# ── alpha_s_frg_certificate ───────────────────────────────────────────────────

def test_certificate_keys():
    cert = alpha_s_frg_certificate()
    for k in ["pillar", "title", "version", "status", "frg_relative_correction",
              "claimed", "not_claimed", "p3_status", "toe_impact"]:
        assert k in cert


def test_certificate_pillar():
    cert = alpha_s_frg_certificate()
    assert cert["pillar"] == 685


def test_certificate_p3_unchanged():
    cert = alpha_s_frg_certificate()
    assert "unchanged" in cert["p3_status"].lower()


def test_certificate_pillar678_confirmed():
    cert = alpha_s_frg_certificate()
    assert cert["pillar_678_confirmed"] is True


def test_certificate_toe_zero():
    cert = alpha_s_frg_certificate()
    assert "0" in cert["toe_impact"]


def test_certificate_frg_relative_tiny():
    cert = alpha_s_frg_certificate()
    assert cert["frg_relative_correction"] < 1e-30


# ── claimed / not_claimed ─────────────────────────────────────────────────────

def test_claimed_list():
    c = what_is_claimed()
    assert isinstance(c, list)
    assert len(c) >= 4


def test_not_claimed_list():
    nc = what_is_NOT_claimed()
    assert isinstance(nc, list)
    assert len(nc) >= 3


def test_not_claimed_no_p3_closure():
    for item in what_is_NOT_claimed():
        if "CLOSED" in item or "closure" in item.lower():
            break
    else:
        pytest.fail("not_claimed should mention that P3 does not close")


# ── Numerical consistency ─────────────────────────────────────────────────────

def test_frg_formula_check():
    # |Δα_s|/α_s = 9 × G_N* × M_KK² / (960) — but formula uses M_KK^2/M_Pl^2
    # = 9 M_KK^2 / (960 M_Pl^2) since M_Pl = 1
    expected = 9.0 * M_KK_SQ_OVER_MPL_SQ / 960.0
    assert abs(FRG_RELATIVE_CORRECTION - expected) < 1e-50


def test_alpha_s_ads_formula():
    expected = math.pi**2 / (2 * K_CS)
    assert abs(ALPHA_S_ADS_QCD - expected) < 1e-12


def test_status_token():
    assert PILLAR_STATUS == "ALPHA_S_TWO_LOOP_FRG_ARCHITECTURE_LIMIT_CONFIRMED"
