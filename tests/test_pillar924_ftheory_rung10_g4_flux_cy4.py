# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 924 — F-theory Rung 10 G₄ flux quantization."""
from __future__ import annotations
from src.core.pillar924_ftheory_rung10_g4_flux_cy4 import (
    N_W, K_CS, CHI_CY4, N_D3_TADPOLE, G4_FLUX_INT,
    G4_QUANTIZATION_OK, G4_PRIMITIVITY_OK,
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    g4_flux_quantization, g4_flux_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 924
def test_gate(): assert PILLAR_GATE == "FTHEORY_RUNG10_G4_FLUX_CY4"
def test_chi_cy4(): assert CHI_CY4 == 1_820_160
def test_n_d3_tadpole(): assert N_D3_TADPOLE == CHI_CY4 // 24
def test_g4_flux_int_positive(): assert G4_FLUX_INT > 0
def test_g4_primitivity_ok(): assert G4_PRIMITIVITY_OK is True
def test_pillar_status_valid():
    assert PILLAR_STATUS in {"RUNG10_G4_PROVED", "RUNG10_G4_OBSTRUCTION"}

def test_quantization_consistency():
    """Status matches quantization condition."""
    if G4_QUANTIZATION_OK:
        assert PILLAR_STATUS == "RUNG10_G4_PROVED"
    else:
        assert PILLAR_STATUS == "RUNG10_G4_OBSTRUCTION"

def test_g4_dict():
    r = g4_flux_quantization()
    assert isinstance(r, dict)

def test_g4_pillar():
    r = g4_flux_quantization()
    assert r["pillar"] == 924

def test_g4_gate():
    r = g4_flux_quantization()
    assert r["gate"] == "FTHEORY_RUNG10_G4_FLUX_CY4"

def test_g4_status():
    r = g4_flux_quantization()
    assert r["status"] == PILLAR_STATUS

def test_g4_n_d3():
    r = g4_flux_quantization()
    assert r["n_d3_tadpole"] == N_D3_TADPOLE

def test_g4_flux_int():
    r = g4_flux_quantization()
    assert abs(r["g4_flux_integral"] - G4_FLUX_INT) < 1e-10

def test_g4_interpretation():
    r = g4_flux_quantization()
    assert isinstance(r["interpretation"], str) and len(r["interpretation"]) > 10

def test_g4_references():
    r = g4_flux_quantization()
    assert isinstance(r["references"], list) and len(r["references"]) >= 3

def test_summary_dict():
    s = g4_flux_summary()
    assert isinstance(s, dict)

def test_summary_pillar():
    s = g4_flux_summary()
    assert s["pillar"] == 924

def test_summary_status():
    s = g4_flux_summary()
    assert s["status"] == PILLAR_STATUS
