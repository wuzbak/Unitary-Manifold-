# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 700 — CMB forecast residuals."""
from __future__ import annotations

from src.core.pillar700_cmb_s4_kk_residual_forecast import (
    DELTA_KK,
    PILLAR_NUMBER,
    SIGMA_PIXEL_CMB_S4,
    SIGMA_PIXEL_LITEBIRD,
    cmb_residual_after_phase2,
    kk_cmb_s4_snr,
    kk_litebird_snr,
)

S4 = kk_cmb_s4_snr()
LB = kk_litebird_snr()
RESIDUAL = cmb_residual_after_phase2()


def test_pillar_number():
    assert PILLAR_NUMBER == 700


def test_noise_constants():
    assert SIGMA_PIXEL_CMB_S4 == 1.0
    assert SIGMA_PIXEL_LITEBIRD == 2.0


def test_delta_kk_small_positive():
    assert 0.0 < DELTA_KK < 1.0e-2


def test_s4_experiment_label():
    assert S4["experiment"] == "CMB-S4"


def test_litebird_experiment_label():
    assert LB["experiment"] == "LiteBIRD"


def test_s4_ell_range():
    assert S4["ell_min"] == 2.0
    assert S4["ell_max"] == 3000.0


def test_litebird_ell_range():
    assert LB["ell_min"] == 2.0
    assert LB["ell_max"] == 500.0


def test_s4_snr_positive():
    assert S4["snr"] > 0.0


def test_litebird_snr_positive():
    assert LB["snr"] > 0.0


def test_s4_outperforms_litebird():
    assert S4["snr"] > LB["snr"]


def test_dominant_ell_within_range():
    assert S4["ell_min"] <= S4["dominant_ell"] <= S4["ell_max"]


def test_residual_contains_ratios():
    assert RESIDUAL["predicted_ratio"] > 0.0
    assert RESIDUAL["observed_ratio"] > 0.0


def test_residual_small_percent():
    assert RESIDUAL["residual_percent_of_observed"] < 10.0


def test_residual_total_gt_one():
    assert RESIDUAL["z_phi_total"] > 1.0
