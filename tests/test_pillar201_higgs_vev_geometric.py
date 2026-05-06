# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 201 — Geometric Higgs VEV from GW Braid Action."""

import math
import pytest

from src.core.pillar201_higgs_vev_geometric import (
    N_W, K_CS, N1, N2, N_C, M_PL_GEV, PI_KR, M_KK_GEV,
    NU_GEO, V_GW_GEV, V_GW_RESIDUAL_PCT,
    secondary_winding_number,
    gw_nu_from_braid,
    higgs_vev_gw,
    vev_comparison,
    axiom_zero_audit,
    pillar201_summary,
)


# ─────────────────────────────────────────────────────────────────────────────
# MODULE CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_n1_equals_nw(self):
        assert N1 == N_W

    def test_n2_is_7(self):
        assert N2 == 7

    def test_n2_squared_plus_n1_squared_is_kcs(self):
        assert N1 ** 2 + N2 ** 2 == K_CS

    def test_n_c_is_3(self):
        assert N_C == 3

    def test_pi_kr_is_37(self):
        assert PI_KR == pytest.approx(37.0)

    def test_m_kk_positive(self):
        assert M_KK_GEV > 0

    def test_m_kk_less_than_m_pl(self):
        assert M_KK_GEV < M_PL_GEV

    def test_m_kk_order_of_magnitude(self):
        # M_KK = 1.22e19 × exp(-37) ≈ 1041 GeV
        assert 900 < M_KK_GEV < 1200

    def test_nu_geo_value(self):
        expected = 3.0 / 49.0
        assert NU_GEO == pytest.approx(expected, rel=1e-6)

    def test_v_gw_gev_order(self):
        # Should be between 240 and 280 GeV
        assert 240 < V_GW_GEV < 280

    def test_v_gw_residual_below_5pct(self):
        assert V_GW_RESIDUAL_PCT < 5.0

    def test_v_gw_residual_positive(self):
        assert V_GW_RESIDUAL_PCT >= 0.0


# ─────────────────────────────────────────────────────────────────────────────
# SECONDARY WINDING NUMBER
# ─────────────────────────────────────────────────────────────────────────────

class TestSecondaryWindingNumber:
    def test_default_gives_7(self):
        assert secondary_winding_number() == 7

    def test_74_5_gives_7(self):
        assert secondary_winding_number(74, 5) == 7

    def test_braid_constraint_satisfied(self):
        n2 = secondary_winding_number(74, 5)
        assert 5 ** 2 + n2 ** 2 == 74

    def test_k_cs_50_n_w_1_gives_7(self):
        # 1² + 7² = 50
        n2 = secondary_winding_number(50, 1)
        assert n2 == 7

    def test_non_perfect_square_raises(self):
        with pytest.raises(ValueError):
            secondary_winding_number(75, 5)  # 75 - 25 = 50 — √50 not integer

    def test_k_cs_leq_n_w_squared_raises(self):
        with pytest.raises(ValueError):
            secondary_winding_number(25, 5)  # 25 - 25 = 0, no real n₂

    def test_k_cs_25_n_w_3_gives_4(self):
        # 3² + 4² = 25
        n2 = secondary_winding_number(25, 3)
        assert n2 == 4


# ─────────────────────────────────────────────────────────────────────────────
# GW ν FROM BRAID
# ─────────────────────────────────────────────────────────────────────────────

class TestGwNuFromBraid:
    def test_returns_dict(self):
        result = gw_nu_from_braid()
        assert isinstance(result, dict)

    def test_nu_geo_value(self):
        result = gw_nu_from_braid()
        assert result["nu_geo"] == pytest.approx(3.0 / 49.0, rel=1e-6)

    def test_fraction_string(self):
        result = gw_nu_from_braid()
        assert "3/49" in result["nu_geo_fraction"]

    def test_no_sm_anchors(self):
        result = gw_nu_from_braid()
        assert result["sm_anchors_used"] == []

    def test_status_says_derived(self):
        result = gw_nu_from_braid()
        assert "DERIVED" in result["status"]

    def test_nu_less_than_1(self):
        result = gw_nu_from_braid()
        assert result["nu_geo"] < 1.0

    def test_nu_positive(self):
        result = gw_nu_from_braid()
        assert result["nu_geo"] > 0.0

    def test_custom_n_c_n2(self):
        result = gw_nu_from_braid(n_c=4, n2=8)
        assert result["nu_geo"] == pytest.approx(4.0 / 64.0, rel=1e-6)


# ─────────────────────────────────────────────────────────────────────────────
# HIGGS VEV GW
# ─────────────────────────────────────────────────────────────────────────────

class TestHiggsVevGw:
    def setup_method(self):
        self.result = higgs_vev_gw()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_axiom_zero_compliant(self):
        assert self.result["axiom_zero_compliant"] is True

    def test_no_sm_anchors(self):
        assert self.result["sm_anchors_used"] == []

    def test_v_gw_within_5pct_of_pdg(self):
        assert self.result["within_5pct_target"] is True

    def test_v_gw_value_approx(self):
        # Expected: M_KK × √3/7 ≈ 257.6 GeV
        assert 250 < self.result["v_gw_GeV"] < 265

    def test_residual_below_5(self):
        assert self.result["v_residual_pct"] < 5.0

    def test_improvement_positive(self):
        # Pillar 201 should improve over Pillar 200
        assert self.result["improvement_delta_pct"] > 0

    def test_pi_kr(self):
        assert self.result["derived"]["pi_kR"] == pytest.approx(37.0)

    def test_n2(self):
        assert self.result["derived"]["n2"] == 7

    def test_n_c(self):
        assert self.result["derived"]["N_c"] == 3

    def test_nu_geo(self):
        assert self.result["derived"]["nu_geo"] == pytest.approx(3.0 / 49.0, rel=1e-6)

    def test_formula_correct(self):
        assert "√(N_c)" in self.result["v_gw_formula"]

    def test_pillar_tag(self):
        assert self.result["pillar"] == "201"

    def test_p200_residual_larger(self):
        assert self.result["v_pillar200_residual_pct"] > self.result["v_residual_pct"]

    def test_status_says_geometric(self):
        assert "GEOMETRIC PREDICTION" in self.result["status"]

    def test_pdg_vev_stored(self):
        assert self.result["v_pdg_GeV"] == pytest.approx(246.22)


# ─────────────────────────────────────────────────────────────────────────────
# VEV COMPARISON
# ─────────────────────────────────────────────────────────────────────────────

class TestVevComparison:
    def setup_method(self):
        self.result = vev_comparison()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_p201_better_than_p200(self):
        assert self.result["pillar_201_residual_pct"] < self.result["pillar_200_residual_pct"]

    def test_improvement_factor_above_1(self):
        assert self.result["improvement_factor"] > 1.0

    def test_p200_residual_approx_14pct(self):
        assert 12.0 < self.result["pillar_200_residual_pct"] < 17.0

    def test_p201_residual_below_5pct(self):
        assert self.result["pillar_201_residual_pct"] < 5.0

    def test_pdg_vev(self):
        assert self.result["pdg_vev_GeV"] == pytest.approx(246.22)

    def test_verdict_present(self):
        assert "Pillar 201" in self.result["verdict"]


# ─────────────────────────────────────────────────────────────────────────────
# AXIOM ZERO AUDIT
# ─────────────────────────────────────────────────────────────────────────────

class TestAxiomZeroAudit:
    def setup_method(self):
        self.result = axiom_zero_audit()

    def test_compliant(self):
        assert self.result["axiom_zero_compliant"] is True

    def test_zero_sm_anchors(self):
        assert self.result["sm_anchors_count"] == 0

    def test_three_derivation_inputs(self):
        assert len(self.result["derivation_inputs"]) == 3

    def test_pdg_vev_in_excluded(self):
        excluded = " ".join(self.result["sm_quantities_not_used"])
        assert "246" in excluded or "246.22" in excluded

    def test_k_cs_in_inputs(self):
        inputs = " ".join(self.result["derivation_inputs"])
        assert "K_CS" in inputs or "74" in inputs


# ─────────────────────────────────────────────────────────────────────────────
# PILLAR 201 SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

class TestPillar201Summary:
    def setup_method(self):
        self.result = pillar201_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_tag(self):
        assert self.result["pillar"] == "201"

    def test_version_tag(self):
        assert "v10" in self.result["version"]

    def test_axiom_zero_compliant(self):
        assert self.result["axiom_zero_compliant"] is True

    def test_result_within_5pct(self):
        assert self.result["result"]["within_5pct"] is True

    def test_toe_score_shows_upgrade(self):
        toe = self.result["toe_score_impact"]
        assert "38%" in toe["toe_score_change"] or "10/26" in toe["toe_score_change"]

    def test_p4_upgraded_to_geometric(self):
        toe = self.result["toe_score_impact"]
        assert "GEOMETRIC PREDICTION" in toe["after"]

    def test_derivation_chain_has_5_steps(self):
        chain = self.result["derivation_chain"]
        assert len(chain) == 5

    def test_status_says_geometric_prediction(self):
        assert "GEOMETRIC PREDICTION" in self.result["status"]

    def test_open_items_nonempty(self):
        assert len(self.result["open_items"]) > 0

    def test_n2_in_derivation(self):
        chain = " ".join(self.result["derivation_chain"].values())
        assert "7" in chain
