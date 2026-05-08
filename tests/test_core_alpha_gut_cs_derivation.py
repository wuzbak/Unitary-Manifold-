# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/alpha_gut_cs_derivation.py — α_GUT first-principles derivation."""
from __future__ import annotations

import math
import pytest

from src.core.alpha_gut_cs_derivation import (
    K_CS,
    N_W,
    N_C,
    ALPHA_GUT_GEO,
    ALPHA_GUT_FORMULA,
    step1_dirac_quantization,
    step2_kk_dimensional_reduction,
    step3_nonabelian_group_factor,
    alpha_gut_full_derivation,
    fallibility_status_update,
    alpha_gut_derivation_summary,
)


def test_constants():
    assert K_CS == 74
    assert N_W == 5
    assert N_C == 3


def test_alpha_gut_formula():
    """α_GUT = N_c/K_CS = 3/74."""
    expected = 3.0 / 74.0
    assert abs(ALPHA_GUT_GEO - expected) < 1e-15


def test_alpha_gut_reasonable():
    """α_GUT should be ~ 0.04 (typical GUT coupling)."""
    assert 0.03 < ALPHA_GUT_GEO < 0.06


def test_formula_string():
    assert "N_c" in ALPHA_GUT_FORMULA
    assert "K_CS" in ALPHA_GUT_FORMULA


# Step 1 — Dirac quantization
def test_step1_returns_dict():
    result = step1_dirac_quantization()
    assert isinstance(result, dict)
    for key in ("step", "g4_squared", "alpha_abelian", "status"):
        assert key in result


def test_step1_step_number():
    result = step1_dirac_quantization()
    assert result["step"] == 1


def test_step1_g4_squared_formula():
    """g₄² = 2π/K_CS."""
    result = step1_dirac_quantization()
    expected = 2.0 * math.pi / K_CS
    assert abs(result["g4_squared"] - expected) < 1e-12


def test_step1_status_derived():
    result = step1_dirac_quantization()
    assert "DERIVED" in result["status"]


# Step 2 — KK dimensional reduction
def test_step2_returns_dict():
    result = step2_kk_dimensional_reduction()
    assert isinstance(result, dict)
    assert result["step"] == 2


def test_step2_g4_squared_consistent():
    """Step 2 result should match Step 1."""
    r1 = step1_dirac_quantization()
    r2 = step2_kk_dimensional_reduction()
    assert abs(r1["g4_squared"] - r2["g4_squared"]) < 1e-12


def test_step2_status_derived():
    result = step2_kk_dimensional_reduction()
    assert "DERIVED" in result["status"]


# Step 3 — Non-Abelian group factor
def test_step3_returns_dict():
    result = step3_nonabelian_group_factor()
    assert isinstance(result, dict)
    assert result["step"] == 3


def test_step3_alpha_gut_correct():
    """Step 3 gives α_GUT = N_c/K_CS."""
    result = step3_nonabelian_group_factor()
    expected = float(N_C) / float(K_CS)
    assert abs(result["alpha_gut"] - expected) < 1e-15


def test_step3_dirac_condition():
    """K_CS × α_GUT = N_c must hold."""
    result = step3_nonabelian_group_factor()
    product = K_CS * result["alpha_gut"]
    assert abs(product - N_C) < 1e-10


def test_step3_status_derived():
    result = step3_nonabelian_group_factor()
    assert "DERIVED" in result["status"]


# Full derivation
def test_full_derivation_returns_dict():
    result = alpha_gut_full_derivation()
    assert isinstance(result, dict)
    for key in ("formula", "alpha_gut", "step1", "step2", "step3",
                "cross_check", "previous_status", "new_status"):
        assert key in result


def test_full_derivation_alpha_gut_value():
    result = alpha_gut_full_derivation()
    assert abs(result["alpha_gut"] - ALPHA_GUT_GEO) < 1e-15


def test_full_derivation_previous_status():
    result = alpha_gut_full_derivation()
    assert "POSTULATED" in result["previous_status"]


def test_full_derivation_new_status():
    result = alpha_gut_full_derivation()
    assert "DERIVED" in result["new_status"]
    assert "CS ACTION" in result["new_status"]


def test_full_derivation_cross_check_finite():
    result = alpha_gut_full_derivation()
    cc = result["cross_check"]
    assert math.isfinite(cc["alpha_s_at_gut"])
    assert math.isfinite(cc["residual_pct"])


# Fallibility status update
def test_fallibility_status_update_returns_dict():
    result = fallibility_status_update()
    assert isinstance(result, dict)
    for key in ("fallibility_section", "old_label", "new_label", "quantity", "module"):
        assert key in result


def test_fallibility_old_label():
    result = fallibility_status_update()
    assert "POSTULATED" in result["old_label"]


def test_fallibility_new_label():
    result = fallibility_status_update()
    assert "DERIVED" in result["new_label"]


def test_fallibility_module_path():
    result = fallibility_status_update()
    assert "alpha_gut_cs_derivation" in result["module"]


# Summary
def test_alpha_gut_summary_completeness():
    summary = alpha_gut_derivation_summary()
    for key in ("version", "title", "formula", "alpha_gut", "status",
                "derivation", "fallibility_update"):
        assert key in summary


def test_alpha_gut_summary_version():
    summary = alpha_gut_derivation_summary()
    assert summary["version"] == "v10.17"


def test_alpha_gut_summary_status():
    summary = alpha_gut_derivation_summary()
    assert "DERIVED" in summary["status"]
