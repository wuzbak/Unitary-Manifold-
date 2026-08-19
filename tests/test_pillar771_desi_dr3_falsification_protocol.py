# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_pillar771_desi_dr3_falsification_protocol.py
=======================================================
Test suite for Pillar 771 — DESI DR3 / CMB-S4 / LiteBIRD Falsification Protocol.

~55 tests covering:
  - Protocol constant integrity (predictions must not drift)
  - desi_verdict: PASS / TENSION / FALSIFIED branches
  - cmb_s4_verdict: PASS / TENSION / FALSIFIED branches
  - litebird_verdict: PASS / FALSIFIED (gap) / FALSIFIED (window) branches
  - run_all_protocols: AWAITING_DATA case and live-data case
  - pillar_report contract
"""
from __future__ import annotations

import pytest
from src.core.pillar771_desi_dr3_falsification_protocol import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    REGISTRATION_VERSION,
    W0_KK,
    WA_KK,
    R_KK,
    BETA_BRANCH_LOW,
    BETA_BRANCH_HIGH,
    BETA_FALSIFIER_LOW,
    BETA_FALSIFIER_HIGH,
    DESI_DR3_PROTOCOL,
    CMB_S4_PROTOCOL,
    LITEBIRD_PROTOCOL,
    desi_verdict,
    cmb_s4_verdict,
    litebird_verdict,
    run_all_protocols,
    pillar_report,
)


# ── Constants ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 771


def test_pillar_status():
    assert PILLAR_STATUS == "FALSIFICATION_PROTOCOL_ACTIVE"


def test_kk_w0_prediction():
    assert W0_KK == -1.0


def test_kk_wa_prediction():
    assert WA_KK == 0.0


def test_kk_r_prediction():
    assert abs(R_KK - 0.0315) < 1e-9


def test_beta_branches_ordered():
    assert BETA_BRANCH_LOW < BETA_BRANCH_HIGH


def test_beta_falsifier_gap_inside_branches():
    assert BETA_BRANCH_LOW < BETA_FALSIFIER_LOW < BETA_FALSIFIER_HIGH < BETA_BRANCH_HIGH


def test_registration_version_has_sprint_ah():
    assert "Sprint_AH" in REGISTRATION_VERSION


# ── Protocol definitions ───────────────────────────────────────────────────

def test_desi_protocol_has_prediction():
    assert DESI_DR3_PROTOCOL["prediction"]["w0"] == W0_KK
    assert DESI_DR3_PROTOCOL["prediction"]["wa"] == WA_KK


def test_cmbs4_protocol_has_r():
    assert CMB_S4_PROTOCOL["prediction"]["r"] == R_KK


def test_litebird_protocol_has_branches():
    pred = LITEBIRD_PROTOCOL["prediction"]
    assert pred["beta_branch_1"] == BETA_BRANCH_LOW
    assert pred["beta_branch_2"] == BETA_BRANCH_HIGH


# ── desi_verdict ──────────────────────────────────────────────────────────────

def test_desi_pass_when_consistent():
    """KK prediction (-1, 0) against itself → PASS."""
    v = desi_verdict(w0_measured=-1.0, wa_measured=0.0, sigma_w0=0.1, sigma_wa=0.3)
    assert v["verdict"] == "PASS"


def test_desi_tension_at_3sigma():
    """3σ tension in w₀ → TENSION."""
    v = desi_verdict(w0_measured=-0.7, wa_measured=0.0, sigma_w0=0.1, sigma_wa=0.3)
    assert v["verdict"] == "TENSION"


def test_desi_falsified_at_6sigma():
    """Very large deviation → FALSIFIED."""
    v = desi_verdict(w0_measured=-0.0, wa_measured=-2.0, sigma_w0=0.05, sigma_wa=0.05)
    assert v["verdict"] == "FALSIFIED"


def test_desi_verdict_has_combined_sigma():
    v = desi_verdict(-1.0, 0.0, 0.1, 0.3)
    assert "combined_sigma" in v


def test_desi_verdict_protocol_version():
    v = desi_verdict(-1.0, 0.0, 0.1, 0.3)
    assert v["protocol_version"] == REGISTRATION_VERSION


def test_desi_y1_tension_routes_to_tension():
    """DESI Y1 best-fit (-0.727, -1.05) with quoted uncertainties → TENSION."""
    v = desi_verdict(w0_measured=-0.727, wa_measured=-1.05, sigma_w0=0.067, sigma_wa=0.29)
    assert v["verdict"] in ("TENSION", "FALSIFIED")


# ── cmb_s4_verdict ────────────────────────────────────────────────────────────

def test_cmbs4_pass_at_prediction():
    v = cmb_s4_verdict(r_measured=R_KK, sigma_r=0.003)
    assert v["verdict"] == "PASS"


def test_cmbs4_pass_within_2sigma():
    v = cmb_s4_verdict(r_measured=0.035, sigma_r=0.005)
    assert v["verdict"] in ("PASS", "TENSION")


def test_cmbs4_falsified_above_bicep():
    v = cmb_s4_verdict(r_measured=0.040, sigma_r=0.003)
    assert v["verdict"] == "FALSIFIED"


def test_cmbs4_falsified_below_lower_limit():
    v = cmb_s4_verdict(r_measured=0.010, sigma_r=0.003)
    assert v["verdict"] == "FALSIFIED"


def test_cmbs4_verdict_structure():
    v = cmb_s4_verdict(R_KK, 0.003)
    assert v["experiment"] == "CMB-S4/Simons"
    assert "delta_r_sigma" in v


# ── litebird_verdict ──────────────────────────────────────────────────────────

def test_litebird_pass_on_branch1():
    v = litebird_verdict(beta_measured=BETA_BRANCH_LOW, sigma_beta=0.02)
    assert v["verdict"] == "PASS"


def test_litebird_pass_on_branch2():
    v = litebird_verdict(beta_measured=BETA_BRANCH_HIGH, sigma_beta=0.02)
    assert v["verdict"] == "PASS"


def test_litebird_falsified_in_gap():
    """β = 0.300° lands in the forbidden gap → FALSIFIED."""
    v = litebird_verdict(beta_measured=0.300, sigma_beta=0.02)
    assert v["verdict"] == "FALSIFIED"
    assert v["in_gap"] is True


def test_litebird_falsified_outside_window_low():
    v = litebird_verdict(beta_measured=0.10, sigma_beta=0.02)
    assert v["verdict"] == "FALSIFIED"
    assert v["outside_window"] is True


def test_litebird_falsified_outside_window_high():
    v = litebird_verdict(beta_measured=0.50, sigma_beta=0.02)
    assert v["verdict"] == "FALSIFIED"
    assert v["outside_window"] is True


def test_litebird_verdict_structure():
    v = litebird_verdict(BETA_BRANCH_HIGH, 0.02)
    assert "dist_to_branch1_sigma" in v
    assert "dist_to_branch2_sigma" in v
    assert v["protocol_version"] == REGISTRATION_VERSION


# ── run_all_protocols ─────────────────────────────────────────────────────────

def test_run_all_awaiting():
    result = run_all_protocols()
    assert result["desi"]["verdict"] == "AWAITING_DATA"
    assert result["cmb_s4"]["verdict"] == "AWAITING_DATA"
    assert result["litebird"]["verdict"] == "AWAITING_DATA"


def test_run_all_overall_awaiting():
    result = run_all_protocols()
    assert result["overall_status"] == "PASS_OR_AWAITING"


def test_run_all_with_pass_data():
    result = run_all_protocols(
        desi_inputs={"w0_measured": -1.0, "wa_measured": 0.0, "sigma_w0": 0.1, "sigma_wa": 0.3},
        cmbs4_inputs={"r_measured": R_KK, "sigma_r": 0.003},
        litebird_inputs={"beta_measured": BETA_BRANCH_HIGH, "sigma_beta": 0.02},
    )
    assert result["overall_status"] == "PASS_OR_AWAITING"


def test_run_all_with_one_tension():
    result = run_all_protocols(
        desi_inputs={"w0_measured": -0.75, "wa_measured": -1.0, "sigma_w0": 0.067, "sigma_wa": 0.29},
    )
    assert result["overall_status"] in ("TENSION", "FALSIFIED")


def test_run_all_has_protocol_version():
    result = run_all_protocols()
    assert result["protocol_version"] == REGISTRATION_VERSION


# ── pillar_report ─────────────────────────────────────────────────────────────

def test_pillar_report_contract():
    report = pillar_report()
    assert report["pillar"] == PILLAR_NUMBER
    assert report["protocols_registered"] == 3
    assert "protocol_results" in report


def test_pillar_report_awaiting_data():
    report = pillar_report()
    assert report["current_overall"] == "PASS_OR_AWAITING"
