# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 964 — c_L^phys Analytic Closure."""

import math
import pytest
from src.core.pillar964_cl_phys_analytic_closure import (
    K_CS,
    N_W,
    CL_PHYS_ZERO_ORDER,
    CL_PHYS_NLO,
    CL_PHYS_RGE,
    CL_RGE_NLO_RESIDUAL,
    PILLAR_STATUS,
    PILLAR_VALID,
    cl_phys_zero_order,
    cl_phys_nlo_correction,
    cl_phys_full,
    cl_phys_uniqueness_proof,
    fallibility_update,
    pillar964_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "CL_PHYS_ANALYTICALLY_DERIVED"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_constants():
    assert K_CS == 74
    assert N_W == 5


def test_zero_order_constant_value():
    assert CL_PHYS_ZERO_ORDER == pytest.approx(69.0 / 74.0)


def test_nlo_constant_value():
    expected = 69.0 / 74.0 - 5.0 / (2.0 * 74.0**2)
    assert CL_PHYS_NLO == pytest.approx(expected)


def test_rge_constant_value():
    assert CL_PHYS_RGE == pytest.approx(0.961)


def test_residual_value():
    assert CL_RGE_NLO_RESIDUAL == pytest.approx(abs(0.961 - 69.0 / 74.0))


def test_zero_order_function_formula():
    result = cl_phys_zero_order()
    assert result["formula"] == "(K_CS-N_W)/K_CS"
    assert result["fraction"] == (69, 74)


def test_zero_order_function_value():
    result = cl_phys_zero_order()
    assert result["c_L_0"] == pytest.approx(CL_PHYS_ZERO_ORDER)


def test_nlo_function_order():
    result = cl_phys_nlo_correction()
    assert result["order"] == "1/K_CS^2"


def test_nlo_function_negative_shift():
    result = cl_phys_nlo_correction()
    assert result["delta_c_L"] < 0.0
    assert result["subleading_to_rge_residual"] is True


def test_full_function_named_gap():
    result = cl_phys_full()
    assert result["RGE_gap"] == "named_residual"
    assert result["c_L_RGE"] == pytest.approx(0.961)


def test_full_function_shift_matches_uv_difference():
    result = cl_phys_full()
    assert result["RGE_shift"] == pytest.approx(CL_PHYS_RGE - CL_PHYS_ZERO_ORDER)


def test_full_function_nlo_shift_matches_nlo_difference():
    result = cl_phys_full()
    assert result["RGE_shift_from_NLO"] == pytest.approx(CL_PHYS_RGE - CL_PHYS_NLO)


def test_uniqueness_proof_flags():
    result = cl_phys_uniqueness_proof()
    assert result["Z2_odd_BC"] is True
    assert result["CS_winding"] is True
    assert result["unique"] is True


def test_fallibility_update_upgrade():
    result = fallibility_update()
    assert result["pillar"] == 964
    assert "ANALYTICALLY_DERIVED" in result["new_status"]


def test_summary_identity():
    result = pillar964_summary()
    assert result["pillar"] == 964
    assert result["status"] == PILLAR_STATUS
    assert result["valid"] is True


def test_summary_contains_all_sections():
    result = pillar964_summary()
    for key in ("zero_order", "nlo_correction", "full_physical_value", "uniqueness", "fallibility_update"):
        assert key in result


def test_summary_derivation_chain_length():
    result = pillar964_summary()
    assert len(result["derivation_chain"]) >= 5
