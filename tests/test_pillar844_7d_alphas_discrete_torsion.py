# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 844 — 7D α_s discrete-torsion Route D partial closure."""
from __future__ import annotations

import pytest

from src.sevend.pillar844_7d_alphas_discrete_torsion import (
    ALPHA_S_7D_CENTRAL,
    ALPHA_S_PDG,
    ALPHA_S_PDG_ERR,
    K_CS_7D,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    M_KK_GEV,
    M_Z_GEV,
    PILLAR_GATE,
    PILLAR_NUMBER,
    alpha_s_mkk,
    alphas_7d_summary,
    g3_squared_mkk,
    inverse_g3_squared,
    run_alpha_s_to_mz,
    volume_parameter_scan,
    volume_s1_z2,
    volume_t2_z3,
)


class TestPillar844Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 844
    def test_gate(self): assert PILLAR_GATE == "ALPHA_S_7D_TORSION_ROUTE_D_PARTIAL"
    def test_kcs(self): assert K_CS_7D == 74
    def test_mass_scales(self):
        assert M_KK_GEV == 1042.0
        assert M_Z_GEV == 91.2
    def test_lean4(self):
        assert LEAN4_THEOREM_COUNT == 20
        assert LEAN4_TOTAL_AFTER == 1996
    def test_pdg_constants(self):
        assert ALPHA_S_PDG == 0.1179
        assert ALPHA_S_PDG_ERR == 0.0010


class TestVolumesAndCoupling:
    def test_t2_z3_volume_positive(self):
        assert volume_t2_z3() > 0.0

    def test_s1_z2_volume_positive(self):
        assert volume_s1_z2() > 0.0

    def test_inverse_g3_positive(self):
        assert inverse_g3_squared() > 0.0

    def test_g3_squared_positive(self):
        assert g3_squared_mkk() > 0.0

    def test_alpha_mkk_reasonable(self):
        assert alpha_s_mkk() == pytest.approx(0.17004369039695794)


class TestRunning:
    def test_running_decreases_in_formula(self):
        high = alpha_s_mkk()
        low = run_alpha_s_to_mz(high)
        assert low < high

    def test_exported_central_value(self):
        assert ALPHA_S_7D_CENTRAL == pytest.approx(0.11635245329032427)

    def test_central_in_range(self):
        assert 0.10 <= ALPHA_S_7D_CENTRAL <= 0.13

    def test_close_to_pdg(self):
        assert abs(ALPHA_S_7D_CENTRAL - ALPHA_S_PDG) < 0.002


class TestVolumeScan:
    def test_scan_has_three_points(self):
        assert len(volume_parameter_scan()) == 3

    def test_scan_ordering(self):
        scan = volume_parameter_scan()
        alphas = [row["alpha_s_mz"] for row in scan]
        assert alphas[0] > alphas[1] > alphas[2]

    def test_scan_brackets_pdg(self):
        scan = volume_parameter_scan()
        vals = [row["alpha_s_mz"] for row in scan]
        assert min(vals) < ALPHA_S_PDG < max(vals)


class TestSummary:
    def test_returns_dict(self):
        assert isinstance(alphas_7d_summary(), dict)

    def test_summary_gate(self):
        assert alphas_7d_summary()["gate"] == PILLAR_GATE

    def test_summary_in_range(self):
        assert alphas_7d_summary()["in_expected_range"] is True

    def test_summary_has_open_items(self):
        assert len(alphas_7d_summary()["remaining_open"]) >= 1

    def test_summary_scan_range(self):
        scan_range = alphas_7d_summary()["scan_range_mz"]
        assert scan_range["min"] < scan_range["max"]
