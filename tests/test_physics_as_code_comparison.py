# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 181 — Physics-as-Code Comparison Engine (Capstone)."""
import math
import pytest
from src.core.physics_as_code_comparison import (
    N_W, K_CS, UM_BETA_DEG, UM_N_S, UM_R,
    um_cmb_predictions, wolfram_cmb_convergence_check, e8_fermion_mass_ratios,
    gu_gauge_coupling_comparison, cdt_hausdorff_comparison, comparison_matrix,
    physics_as_code_advantage, pillar179_capstone_audit, pillar179_summary,
)

class TestConstants:
    def test_n_w(self): assert N_W == 5
    def test_k_cs(self): assert K_CS == 74
    def test_beta_length(self): assert len(UM_BETA_DEG) == 2
    def test_n_s(self): assert UM_N_S == pytest.approx(0.9635, rel=1e-4)
    def test_r(self): assert UM_R == pytest.approx(0.0315, rel=1e-4)

class TestCmbPredictions:
    def setup_method(self): self.r = um_cmb_predictions()
    def test_n_s(self): assert self.r["n_s"] == pytest.approx(UM_N_S, rel=1e-9)
    def test_r(self): assert self.r["r"] == pytest.approx(UM_R, rel=1e-9)
    def test_beta_list(self): assert isinstance(self.r["beta_deg"], list) and len(self.r["beta_deg"]) == 2

class TestWolframCheck:
    def setup_method(self): self.r = wolfram_cmb_convergence_check()
    def test_not_converged(self): assert self.r["converged"] is False
    def test_undetermined(self): assert self.r["agreement_with_um"] == "UNDETERMINED"

class TestE8MassRatios:
    def setup_method(self): self.r = e8_fermion_mass_ratios()
    def test_consistent(self): assert self.r["agreement"] == "CONSISTENT"
    def test_tb_ratio(self): assert 40 < self.r["e8_tb_ratio"] < 43

class TestGuCoupling:
    def setup_method(self): self.r = gu_gauge_coupling_comparison()
    def test_formula(self): assert self.r["um_alpha_mkk"] == pytest.approx(2.0*math.pi/(3*74), rel=1e-9)
    def test_agreement(self): assert self.r["agreement"] == "CONSISTENT_AT_GUT_SCALE"

class TestCdtHausdorff:
    def setup_method(self): self.r = cdt_hausdorff_comparison()
    def test_within_2sigma(self): assert self.r["within_2sigma"] is True
    def test_agreement(self): assert self.r["agreement"] == "CONSISTENT_WITHIN_2SIGMA"

class TestComparisonMatrix:
    def test_length_4(self): assert len(comparison_matrix()) == 4
    def test_has_wolfram(self): assert any("Wolfram" in m["theory"] for m in comparison_matrix())
    def test_has_cdt(self): assert any("CDT" in m["theory"] or "Causal" in m["theory"] for m in comparison_matrix())

class TestPhysicsAsCodeAdvantage:
    def setup_method(self): self.r = physics_as_code_advantage()
    def test_advantage_key(self): assert "advantage" in self.r
    def test_falsification_has_window(self):
        ft = self.r["falsification_transparency"]
        assert "0.22" in ft or "0.38" in ft or "β" in ft

class TestCapstoneAudit:
    def setup_method(self): self.r = pillar179_capstone_audit()
    def test_status(self): assert self.r["status"] == "CAPSTONE_COMPLETE"
    def test_pillar_count(self): assert self.r["pillar_count"] == 179
    def test_summary_litebird(self): assert "LiteBIRD" in self.r["summary"]

class TestPillar179Summary:
    def test_returns_string(self): assert isinstance(pillar179_summary(), str)
    def test_contains_179(self): assert "179" in pillar179_summary()
    def test_contains_status(self): assert "CAPSTONE_COMPLETE" in pillar179_summary()
