# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""tests/test_pillar361_zphi_dyson_schwinger.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar361_zphi_dyson_schwinger import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    K_CS, PHI0_FTUM, Z_PHI_0, GAMMA_THEORY, GAMMA_FIT, LOOP_FACTOR,
    separation_guard, one_loop_self_energy, two_loop_self_energy,
    cs_induced_quartic, zphi_ds_fixed_point, two_loop_z_phi,
    gamma_two_loop, gamma_discrepancy_analysis, dyson_schwinger_report,
    pillar361_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 361
    def test_status(self): assert PILLAR_STATUS == "FRONTIER_COMPUTATION"
    def test_k_cs(self): assert K_CS == 74
    def test_phi0(self): assert PHI0_FTUM == 1.0
    def test_z_phi_0(self): assert abs(Z_PHI_0 - 5.301) < 0.01
    def test_gamma_theory(self): assert abs(GAMMA_THEORY - 0.242) < 0.01
    def test_gamma_fit(self): assert abs(GAMMA_FIT - 0.273) < 0.01
    def test_loop_factor(self): assert abs(LOOP_FACTOR - 1/(16*math.pi**2)) < 1e-10


class TestCsInducedQuartic:
    def test_positive(self): assert cs_induced_quartic() > 0
    def test_value(self): assert abs(cs_induced_quartic() - 1.0/74) < 1e-10
    def test_small(self): assert cs_induced_quartic() < 0.05


class TestSelfEnergy:
    def test_one_loop_positive(self): assert one_loop_self_energy() > 0
    def test_two_loop_positive(self): assert two_loop_self_energy() > 0
    def test_two_loop_smaller(self):
        assert two_loop_self_energy() < one_loop_self_energy()
    def test_one_loop_tiny(self): assert one_loop_self_energy() < 1e-50
    def test_two_loop_much_tinier(self): assert two_loop_self_energy() < 1e-100


class TestDsFixedPoint:
    def test_returns_dict(self): assert isinstance(zphi_ds_fixed_point(), dict)
    def test_converged(self): assert zphi_ds_fixed_point()["converged"] is True
    def test_fixed_point_matches_z_phi_0(self):
        result = zphi_ds_fixed_point()
        assert abs(result["z_phi_fixed_point"] - Z_PHI_0) < 1e-10
    def test_note_present(self): assert "note" in zphi_ds_fixed_point()


class TestTwoLoopZPhi:
    def test_returns_dict(self): assert isinstance(two_loop_z_phi(), dict)
    def test_two_loop_close_to_one_loop(self):
        result = two_loop_z_phi()
        assert abs(result["z_phi_two_loop"] - result["z_phi_one_loop"]) < 0.01
    def test_delta_2loop_tiny(self):
        result = two_loop_z_phi()
        assert result["delta_2loop"] < 1e-3
    def test_verdict_negligible(self):
        result = two_loop_z_phi()
        assert "negligible" in result["verdict"].lower()
    def test_fractional_correction_matches(self):
        result = two_loop_z_phi()
        assert abs(result["fractional_correction"] - result["delta_2loop"]) < 1e-12


class TestGammaTwoLoop:
    def test_returns_dict(self): assert isinstance(gamma_two_loop(), dict)
    def test_two_loop_close_to_one_loop(self):
        result = gamma_two_loop()
        assert abs(result["gamma_2loop"] - result["gamma_1loop"]) < 0.001
    def test_correction_tiny(self):
        result = gamma_two_loop()
        assert result["correction_pct"] < 0.1  # ~0.017% << 13% gap
    def test_gap_not_closed(self):
        result = gamma_two_loop()
        # 13% gap, two-loop reduces by < 0.01% → gap still large
        assert result["gap_after_pct"] > 10.0
    def test_verdict_cannot_explain(self):
        result = gamma_two_loop()
        assert "cannot" in result["verdict"].lower()


class TestGammaDiscrepancyAnalysis:
    def test_returns_dict(self): assert isinstance(gamma_discrepancy_analysis(), dict)
    def test_gap_pct(self):
        result = gamma_discrepancy_analysis()
        assert abs(result["gap_pct"] - 13.0) < 2.0
    def test_candidates_listed(self):
        result = gamma_discrepancy_analysis()
        assert len(result["candidate_explanations"]) >= 3
    def test_loop_ruled_out(self):
        result = gamma_discrepancy_analysis()
        assert "RULED_OUT" in result["candidate_explanations"][0]["verdict"]
    def test_formal_status(self):
        result = gamma_discrepancy_analysis()
        assert "L2" in result["formal_status"]
    def test_conclusion_present(self):
        assert "conclusion" in gamma_discrepancy_analysis()


class TestDysonSchwingerReport:
    def test_returns_dict(self): assert isinstance(dyson_schwinger_report(), dict)
    def test_pillar_number(self):
        result = dyson_schwinger_report()
        assert result["pillar"] == 361
    def test_key_results_present(self):
        result = dyson_schwinger_report()
        assert len(result["key_results"]) >= 3
    def test_summary_matches(self):
        summary = pillar361_summary()
        assert summary["pillar"] == 361


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_frontier(self): assert "FRONTIER_COMPUTATION" in separation_guard()
