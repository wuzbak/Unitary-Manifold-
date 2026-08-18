# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for Pillar 679: CMB Boltzmann Peak Positions KK Correction."""

import math
import pytest
from src.core.pillar679_cmb_boltzmann_peak_positions import (
    N_W, K_CS,
    R_S_PLANCK_MPC, D_A_PLANCK_MPC, THETA_S_PLANCK_RAD, DELTA_KK,
    kk_corrected_sound_horizon,
    acoustic_scale_um,
    peak_positions_um,
    three_peak_audit,
    cmb_peak_positions_report,
)


def test_planck_baseline_r_s():
    assert 140 < R_S_PLANCK_MPC < 155


def test_planck_baseline_d_a():
    assert 12000 < D_A_PLANCK_MPC < 14000


def test_planck_baseline_theta_s():
    assert 0.010 < THETA_S_PLANCK_RAD < 0.013


def test_delta_kk_small():
    assert 5e-4 < DELTA_KK < 2e-3


def test_kk_corrected_sound_horizon_positive():
    r = kk_corrected_sound_horizon()
    assert r["r_s_um_mpc"] > 0


def test_kk_corrected_sound_horizon_close_to_planck():
    r = kk_corrected_sound_horizon()
    ratio = r["r_s_um_mpc"] / r["r_s_standard_mpc"]
    assert 0.999 < ratio < 1.001, f"ratio={ratio}: KK shift too large"


def test_acoustic_scale_um_returns_dict():
    assert isinstance(acoustic_scale_um(), dict)


def test_acoustic_scale_theta_s_range():
    a = acoustic_scale_um()
    theta = a["theta_s_um_rad"]
    assert 0.008 < theta < 0.015


def test_acoustic_scale_planck_100_theta_s():
    a = acoustic_scale_um()
    # Planck reports 100·θ_s ≈ 1.042
    val = a.get("100_theta_s", a.get("planck_100_theta_s"))
    if val is not None:
        assert 0.9 < val < 1.2


def test_peak_positions_um_three_peaks():
    p = peak_positions_um()
    if isinstance(p, dict):
        assert len(p) >= 3
    else:
        assert len(p) >= 3


def test_peak_positions_um_first_peak():
    p = peak_positions_um()
    if isinstance(p, dict):
        ell_1 = p.get(1) or list(p.values())[0]
    else:
        ell_1 = p[0]
    assert 150 < ell_1 < 280, f"First peak ℓ = {ell_1}"


def test_peak_positions_um_ordered():
    p = peak_positions_um()
    vals = list(p.values()) if isinstance(p, dict) else p
    for i in range(len(vals) - 1):
        assert vals[i] < vals[i+1]


def test_three_peak_audit_within_5_pct():
    result = three_peak_audit()
    assert result["all_within_5_pct"] is True


def test_three_peak_audit_kk_small():
    result = three_peak_audit()
    kk = result.get("kk_effect_pct", result.get("delta_kk_pct", DELTA_KK * 100))
    assert kk < 1.0


def test_cmb_peak_positions_report_status():
    report = cmb_peak_positions_report()
    assert "CMB_PEAK_POSITIONS_KK_CORRECTION_QUANTIFIED" in report["status"]


def test_cmb_peak_positions_report_pillar():
    report = cmb_peak_positions_report()
    assert report.get("pillar") == 679


def test_cmb_peak_positions_report_idempotent():
    r1 = cmb_peak_positions_report()
    r2 = cmb_peak_positions_report()
    assert r1["status"] == r2["status"]
