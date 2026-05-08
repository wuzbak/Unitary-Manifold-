# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/solar_splitting_constrained_cert.py."""
from __future__ import annotations

from src.core.solar_splitting_constrained_cert import (
    CONSTRAINED_THRESHOLD_PCT,
    FLUX_BACKREACTION_FACTOR,
    P16_STATUS,
    P16_TOE_SCORE_DELTA,
    flux_backreaction_corrected_estimate,
    p16_constrained_certificate,
)


def test_constants():
    assert CONSTRAINED_THRESHOLD_PCT == 50.0
    assert 0 < FLUX_BACKREACTION_FACTOR < 1.0


def test_corrected_estimate_under_threshold():
    corr = flux_backreaction_corrected_estimate()
    assert corr["dm2_21_corrected_eV2"] > 0.0
    assert corr["residual_pct"] < CONSTRAINED_THRESHOLD_PCT


def test_certificate_passes():
    cert = p16_constrained_certificate()
    assert cert["all_gates_pass"] is True
    assert cert["gates"]["residual_lt_50pct"] is True


def test_status_upgrade_and_delta():
    assert P16_STATUS == "CONSTRAINED"
    assert abs(P16_TOE_SCORE_DELTA - 0.2) < 1e-12
