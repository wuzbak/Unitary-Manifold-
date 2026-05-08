# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/simons_obs_readiness.py."""
from __future__ import annotations

from src.core.simons_obs_readiness import (
    BETA_MODE_PRIMARY,
    BETA_MODE_SHADOW,
    SIMONS_SIGMA_BETA,
    beta_mode_separation_sigma,
    simons_discrimination_forecast,
)


def test_constants():
    assert BETA_MODE_PRIMARY > BETA_MODE_SHADOW
    assert SIMONS_SIGMA_BETA == 0.05


def test_separation_sigma_value():
    sep = beta_mode_separation_sigma()
    assert 1.0 < sep < 2.0


def test_forecast_structure():
    forecast = simons_discrimination_forecast()
    assert forecast["experiment"] == "Simons Observatory"
    assert forecast["mode_separation_sigma"] > 0


def test_forecast_default_verdict():
    forecast = simons_discrimination_forecast()
    assert forecast["verdict"] == "CONSISTENT_NOT_DISCRIMINATING"
