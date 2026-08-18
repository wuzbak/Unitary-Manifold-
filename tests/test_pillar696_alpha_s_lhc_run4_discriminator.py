# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 696 — α_s LHC Run 4 discriminator."""

import math

from src.core.pillar696_alpha_s_lhc_run4_discriminator import (
    N_W,
    K_CS,
    ALPHA_S_PDG_MZ,
    SQRT_S_TEV,
    PI,
    alpha_s_kk_prediction,
    lhc_run4_snr,
    alpha_s_preregistration,
)


def test_constants():
    assert N_W == 5
    assert K_CS == 74
    assert ALPHA_S_PDG_MZ == 0.1180


def test_energy():
    assert abs(SQRT_S_TEV - 13.6) < 1e-12


def test_pi_matches_math():
    assert abs(PI - math.pi) < 1e-15


def test_prediction_returns_dict():
    assert isinstance(alpha_s_kk_prediction(), dict)


def test_prediction_negative_shift():
    pred = alpha_s_kk_prediction()
    assert pred["delta_alpha_s"] < 0.0


def test_prediction_shift_order():
    pred = alpha_s_kk_prediction()
    assert 0.0005 < abs(pred["delta_alpha_s"]) < 0.0020


def test_prediction_alpha_below_sm():
    pred = alpha_s_kk_prediction()
    assert pred["alpha_s_kk"] < pred["alpha_s_sm"]


def test_prediction_sign_label():
    pred = alpha_s_kk_prediction()
    assert pred["sign"] == "negative"


def test_snr_returns_dict():
    assert isinstance(lhc_run4_snr(), dict)


def test_snr_above_one():
    snr = lhc_run4_snr()
    assert snr["snr"] > 1.0


def test_snr_detectable():
    snr = lhc_run4_snr()
    assert snr["detectable"] is True


def test_preregistration_returns_dict():
    assert isinstance(alpha_s_preregistration(), dict)


def test_preregistration_status():
    prereg = alpha_s_preregistration()
    assert prereg["status"] == "PREREGISTERED"


def test_preregistration_formula():
    prereg = alpha_s_preregistration()
    expected = ALPHA_S_PDG_MZ * (1 - N_W / (K_CS * math.pi))
    assert abs(prereg["alpha_s_um"] - expected) < 1e-15


def test_preregistration_negative_shift():
    prereg = alpha_s_preregistration()
    assert prereg["delta_alpha_s"] < 0.0
