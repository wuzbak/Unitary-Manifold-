# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for Tightening 3: PMNS Solar θ₁₂ HARDGATE Promotion."""

import math
import pytest
from src.core.tightening_pmns_solar_hardgate import (
    hardgate_certificate,
    pmns_solar_hardgate_promotion,
)


def test_pmns_promotion_returns_dict():
    assert isinstance(pmns_solar_hardgate_promotion(), dict)


def test_pmns_promotion_pdg_value():
    p = pmns_solar_hardgate_promotion()
    pdg = p["sin2_theta12_pdg"]
    assert abs(pdg - 0.307) < 0.01


def test_pmns_promotion_gate_threshold():
    p = pmns_solar_hardgate_promotion()
    assert p["gate_threshold_pct"] == 5.0


def test_pmns_promotion_residual_below_5pct():
    p = pmns_solar_hardgate_promotion()
    assert p["residual_pct"] < 5.0, f"residual={p['residual_pct']}% ≥ 5%"


def test_pmns_promotion_within_gate():
    p = pmns_solar_hardgate_promotion()
    assert p["within_gate"] is True


def test_pmns_promotion_sin2_theta12_range():
    p = pmns_solar_hardgate_promotion()
    val = p["sin2_theta12_mz"]
    assert 0.25 < val < 0.35


def test_pmns_promotion_sigma():
    p = pmns_solar_hardgate_promotion()
    sigma = p.get("sigma_away")
    if sigma is not None:
        assert sigma < 2.0


def test_pmns_promotion_allowed():
    p = pmns_solar_hardgate_promotion()
    assert p["promotion_allowed"] is True


def test_hardgate_certificate_status():
    cert = hardgate_certificate()
    assert "HARDGATE_PROMOTED" in cert["status"]


def test_hardgate_certificate_gate_field():
    cert = hardgate_certificate()
    assert "gate" in cert


def test_hardgate_certificate_idempotent():
    c1 = hardgate_certificate()
    c2 = hardgate_certificate()
    assert c1["status"] == c2["status"]
