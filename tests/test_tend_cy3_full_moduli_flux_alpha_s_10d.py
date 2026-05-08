# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/tend/cy3_full_moduli_flux_alpha_s_10d.py."""
from __future__ import annotations

from src.tend.cy3_full_moduli_flux_alpha_s_10d import (
    ALPHA_S_BASE_5D,
    ALPHA_S_PDG,
    alpha_s_full_moduli_flux,
    complex_structure_sector_shift,
    flux_lattice_shift,
    kahler_sector_shift,
    ws_iv_full_geometry_gate,
)


def test_each_shift_positive():
    assert kahler_sector_shift() > 0.0
    assert complex_structure_sector_shift() > 0.0
    assert flux_lattice_shift() > 0.0


def test_alpha_s_improves_over_5d_base():
    pred = alpha_s_full_moduli_flux()
    assert pred > ALPHA_S_BASE_5D


def test_alpha_s_close_to_pdg():
    pred = alpha_s_full_moduli_flux()
    residual = abs(pred - ALPHA_S_PDG) / ALPHA_S_PDG * 100.0
    assert residual < 5.0


def test_alpha_s_in_falsification_band():
    pred = alpha_s_full_moduli_flux()
    assert 0.08 <= pred <= 0.14


def test_ws_iv_gate_passes():
    gate = ws_iv_full_geometry_gate()
    assert gate["gate_pass"] is True
    assert gate["within_falsification_band"] is True
    assert gate["high_precision_closure"] is True
    assert "PASS_FREEZE" in gate["status"]

