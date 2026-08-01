# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 626 — F-theory Rung 10 G4 flux quantization full."""
import pytest
from src.core.pillar626_ftheory_rung10_g4_flux_full import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    K_CS,
    N_W,
    N_2,
    CY4_EULER_CHI,
    N_D3_TADPOLE,
    G4_BRAID_PRODUCT,
    N_FLUX_GUT_DIVISOR,
    FLUX_FRACTION,
    G4_QUANTIZATION_STATUS,
    BLOCKING_RESIDUAL_RESOLVED,
    g4_flux_quantization,
    tadpole_consistency,
    braid_flux_consistency,
    g4_certificate,
    pillar_report,
)

NUMERIC_CHECKS = [
    ("PILLAR_NUMBER", PILLAR_NUMBER, 626),
    ("K_CS", K_CS, 74),
    ("N_W", N_W, 5),
    ("N_2", N_2, 7),
    ("CY4_EULER_CHI", CY4_EULER_CHI, 1_820_160),
    ("N_D3_TADPOLE", N_D3_TADPOLE, 75_840),
    ("G4_BRAID_PRODUCT", G4_BRAID_PRODUCT, 1850),
    ("N_FLUX_GUT_DIVISOR", N_FLUX_GUT_DIVISOR, 1850 / 24),
]

STRING_CHECKS = [
    ("PILLAR_STATUS", PILLAR_STATUS, "FTHEORY_RUNG10_G4_FLUX_QUANTIZATION_FULL_ADJACENT"),
    ("G4_QUANTIZATION_STATUS", G4_QUANTIZATION_STATUS, "QUANTIZED_AT_REFERENCE_CY4"),
]


@pytest.mark.parametrize("name,actual,expected", NUMERIC_CHECKS)
def test_numeric_constant(name, actual, expected):
    assert actual == pytest.approx(expected, rel=1e-10), f"{name} mismatch"


@pytest.mark.parametrize("name,actual,expected", STRING_CHECKS)
def test_string_constant(name, actual, expected):
    assert actual == expected, f"{name} mismatch"


def test_blocking_residual_resolved():
    assert BLOCKING_RESIDUAL_RESOLVED is True


def test_braid_identity():
    assert N_W ** 2 + N_2 ** 2 == K_CS


def test_tadpole_exact():
    assert CY4_EULER_CHI // 24 == N_D3_TADPOLE


def test_flux_fraction_subdominant():
    # Gut-divisor flux < 1% of tadpole
    assert FLUX_FRACTION < 0.01


def test_g4_braid_product():
    assert G4_BRAID_PRODUCT == N_W ** 2 * K_CS


def test_g4_flux_quantization_structure():
    result = g4_flux_quantization()
    assert isinstance(result, dict)
    assert result["half_integer_shift_satisfied"] is True
    assert result["flux_subdominant"] is True
    assert result["n_d3_tadpole"] == N_D3_TADPOLE


def test_tadpole_consistency_structure():
    result = tadpole_consistency()
    assert result["tadpole_consistent"] is True
    assert result["exact_match"] is True


def test_braid_flux_consistency_structure():
    result = braid_flux_consistency()
    assert result["braid_equals_k_cs"] is True
    assert result["k_cs_preserved_in_g4_flux"] is True


def test_g4_certificate_structure():
    cert = g4_certificate()
    assert cert["blocking_residual_resolved"] is True
    assert len(cert["checks_passed"]) == 4


def test_pillar_report_structure():
    rpt = pillar_report()
    assert rpt["pillar"] == 626
    assert rpt["adjacent_track"] is True
    assert rpt["toe_score_delta"] == 0.0
    assert rpt["hardgate_score_delta"] == 0.0
    assert "g4_flux_quantization" in rpt
    assert "tadpole_consistency" in rpt
    assert "braid_flux_consistency" in rpt
    assert "g4_certificate" in rpt
