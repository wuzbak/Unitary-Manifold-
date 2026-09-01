# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 838 — 6D Hosotani Higgs partial closure."""
from __future__ import annotations

import math

import pytest

from src.core.pillar838_6d_hosotani_higgs_mass import (
    FIRST_SHELL_DEGENERACY,
    GATE,
    HOSOTANI_PARAMETER_ALPHA_MIN,
    LEAN4_COUNT,
    LEAN4_PRIOR,
    LEAN4_TOTAL,
    M_H_HOSOTANI_GEV,
    M_H_PDG_GEV,
    M_KK_GEV,
    PILLAR,
    R6_GEV_INV,
    hosotani_curvature_data,
    hosotani_higgs_mass_estimate,
    hosotani_higgs_summary,
)


class TestPillar838Constants:
    def test_pillar_number(self): assert PILLAR == 838
    def test_gate(self): assert GATE == "HIGGS_6D_HOSOTANI_PARTIAL_CLOSURE"
    def test_alpha_min(self): assert HOSOTANI_PARAMETER_ALPHA_MIN == 0.5
    def test_mkk(self): assert M_KK_GEV == 1042.0
    def test_lean4_count(self): assert LEAN4_COUNT == 25
    def test_lean4_total(self): assert LEAN4_TOTAL == 1876
    def test_lean4_accumulates(self): assert LEAN4_TOTAL == LEAN4_PRIOR + LEAN4_COUNT


class TestHosotaniEstimate:
    def test_radius_positive(self):
        assert R6_GEV_INV > 0.0

    def test_curvature_data(self):
        data = hosotani_curvature_data()
        assert data["alpha"] == 0.5
        assert data["first_shell_degeneracy"] == float(FIRST_SHELL_DEGENERACY)

    def test_mass_range(self):
        assert 80.0 <= M_H_HOSOTANI_GEV <= 130.0

    def test_mass_value(self):
        assert M_H_HOSOTANI_GEV == pytest.approx(102.93725652143307, rel=1e-12)

    def test_estimate_is_ballpark(self):
        est = hosotani_higgs_mass_estimate()
        assert est["in_ballpark_range"] is True

    def test_residual_below_half_pdg(self):
        est = hosotani_higgs_mass_estimate()
        assert est["residual_gev"] < 0.5 * M_H_PDG_GEV


class TestHosotaniSummary:
    def test_summary_pillar(self):
        assert hosotani_higgs_summary()["pillar"] == 838

    def test_summary_gate(self):
        assert hosotani_higgs_summary()["gate"] == GATE

    def test_summary_partial_wording(self):
        assert "partial" in hosotani_higgs_summary()["honest_status"].lower()

    def test_summary_remaining_open(self):
        assert "UV" in hosotani_higgs_summary()["remaining_open"][0]

    def test_mass_below_pdg(self):
        assert hosotani_higgs_summary()["m_h_hosotani_gev"] < M_H_PDG_GEV
