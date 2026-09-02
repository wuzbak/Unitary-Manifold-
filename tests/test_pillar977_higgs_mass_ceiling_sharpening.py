# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 977 — G3 Higgs Mass Ceiling Sharpening."""

import math
import pytest

from src.core.pillar977_higgs_mass_ceiling_sharpening import (
    PILLAR_STATUS,
    PILLAR_VALID,
    M_H_PDG,
    M_H_CW_CEILING,
    M_H_GW_BOUND,
    M_H_GEOMETRIC_MEAN,
    M_H_GAP_CW,
    M_H_GAP_GW,
    M_H_IN_WINDOW,
    g3_higgs_bounds,
    g3_geometric_mean,
    g3_architecture_limit_update,
    higgs_window_certificate,
    fallibility_update,
    pillar977_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "HIGGS_MASS_CEILING_SHARPENED"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_core_mass_constants():
    assert M_H_PDG == 125.25
    assert M_H_CW_CEILING == 72.0
    assert M_H_GW_BOUND == 153.0


def test_geometric_mean_constant():
    assert abs(M_H_GEOMETRIC_MEAN - math.sqrt(72.0 * 153.0)) < 1e-12


def test_gap_constants():
    expected_cw = (125.25 - 72.0) / 125.25
    expected_gw = (153.0 - 125.25) / 153.0
    assert abs(M_H_GAP_CW - expected_cw) < 1e-12
    assert abs(M_H_GAP_GW - expected_gw) < 1e-12


def test_gap_sizes_reasonable():
    assert 0.4 < M_H_GAP_CW < 0.5
    assert 0.1 < M_H_GAP_GW < 0.2


def test_pdg_in_window_constant():
    assert M_H_IN_WINDOW is True


def test_g3_higgs_bounds():
    result = g3_higgs_bounds()
    assert result["CW_ceiling"] == 72.0
    assert result["GW_bound"] == 153.0
    assert result["PDG"] == 125.25
    assert result["in_window"] is True


def test_window_width():
    result = g3_higgs_bounds()
    assert result["window_width"] == 81.0


def test_geometric_mean_function():
    result = g3_geometric_mean()
    assert abs(result["geometric_mean"] - M_H_GEOMETRIC_MEAN) < 1e-12
    assert result["within_20_percent"] is True


def test_geometric_mean_gap():
    result = g3_geometric_mean()
    assert 0.15 < result["gap_to_PDG"] < 0.17


def test_architecture_limit_update():
    update = g3_architecture_limit_update()
    assert update["old_limit"]["ceiling_only"] == 72.0
    assert update["new_limit"]["window_low"] == 72.0
    assert update["new_limit"]["window_high"] == 153.0
    assert update["pdg_bracketed_now"] is True


def test_certificate_structure():
    cert = higgs_window_certificate()
    assert cert["gap_label"] == "G3"
    assert cert["type_b_classification"] == "TYPE_B_STRUCTURAL_FLOOR"
    assert cert["closure_claimed"] is False
    assert cert["architecture_limit_only"] is True


def test_certificate_gap_fields():
    cert = higgs_window_certificate()
    assert abs(cert["cw_gap_fraction"] - M_H_GAP_CW) < 1e-12
    assert abs(cert["gw_gap_fraction"] - M_H_GAP_GW) < 1e-12


def test_fallibility_update():
    fb = fallibility_update()
    assert fb["pillar"] == 977
    assert "[72,153]" in fb["new_status"]
    assert "NLO" in fb["key_result"] or "UV" in fb["key_result"]


def test_summary():
    summary = pillar977_summary()
    assert summary["pillar"] == 977
    assert summary["valid"] is True
    assert len(summary["derivation_chain"]) >= 5


def test_window_contains_pdg_directly():
    assert M_H_CW_CEILING <= M_H_PDG <= M_H_GW_BOUND
