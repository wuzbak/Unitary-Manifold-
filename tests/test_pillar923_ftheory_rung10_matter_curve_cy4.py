# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 923 — F-theory Rung 10 matter-curve genus on CY₄."""
from __future__ import annotations
from src.core.pillar923_ftheory_rung10_matter_curve_cy4 import (
    N_W, K_CS, CHI_CY4, CHI_CY3, G_SIGMA_CY3, G_SIGMA_CY4, GENUS_CORRECTION,
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS,
    matter_curve_genus_cy4, matter_curve_cy4_summary,
)


def test_pillar_number(): assert PILLAR_NUMBER == 923
def test_gate(): assert PILLAR_GATE == "FTHEORY_RUNG10_MATTER_CURVE_CY4"
def test_chi_cy4(): assert CHI_CY4 == 1_820_160
def test_chi_cy3(): assert CHI_CY3 == -540
def test_g_sigma_cy3(): assert abs(G_SIGMA_CY3 - 1.0) < 1e-12
def test_g_sigma_cy4_large(): assert G_SIGMA_CY4 > 1.0
def test_genus_correction_positive(): assert GENUS_CORRECTION > 0
def test_pillar_status_valid():
    assert PILLAR_STATUS in {
        "RUNG10_MATTER_CURVE_CY4_PROVED",
        "RUNG10_MATTER_CURVE_OBSTRUCTION",
    }

def test_matter_curve_dict():
    r = matter_curve_genus_cy4()
    assert isinstance(r, dict)

def test_matter_curve_pillar():
    r = matter_curve_genus_cy4()
    assert r["pillar"] == 923

def test_matter_curve_gate():
    r = matter_curve_genus_cy4()
    assert r["gate"] == "FTHEORY_RUNG10_MATTER_CURVE_CY4"

def test_matter_curve_status():
    r = matter_curve_genus_cy4()
    assert r["status"] == PILLAR_STATUS

def test_matter_curve_g_sigma_cy3():
    r = matter_curve_genus_cy4()
    assert abs(r["g_sigma_cy3"] - G_SIGMA_CY3) < 1e-10

def test_matter_curve_g_sigma_cy4():
    r = matter_curve_genus_cy4()
    assert abs(r["g_sigma_cy4"] - G_SIGMA_CY4) < 1e-6

def test_matter_curve_correction():
    r = matter_curve_genus_cy4()
    assert r["genus_correction"] == GENUS_CORRECTION

def test_matter_curve_interpretation():
    r = matter_curve_genus_cy4()
    assert isinstance(r["interpretation"], str) and len(r["interpretation"]) > 20

def test_matter_curve_references():
    r = matter_curve_genus_cy4()
    assert isinstance(r["references"], list) and len(r["references"]) >= 3

def test_summary_dict():
    s = matter_curve_cy4_summary()
    assert isinstance(s, dict)

def test_summary_status():
    s = matter_curve_cy4_summary()
    assert s["status"] == PILLAR_STATUS
