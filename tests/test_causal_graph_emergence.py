# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_causal_graph_emergence.py
======================================
Tests for Pillar 175 — Causal Graph Emergence (Wolfram alignment).

Theory, scientific direction, and framework: ThomasCory Walker-Pearson.
Tests: GitHub Copilot (AI).
"""
import math
import pytest
from src.core.causal_graph_emergence import (
    N_W, K_CS, BRAIDED_CS, PLANCK_LENGTH_M, L_KK_M, L_KK_GEV_INV,
    M_TO_GEV_INV,
    causal_invariance_from_information_current,
    kk_elementary_length,
    hausdorff_dimension_uv,
    hausdorff_dimension_ir,
    causal_graph_node_density,
    wolfram_um_correspondence_audit,
    pillar173_summary,
)


class TestConstants:
    def test_n_w_is_5(self): assert N_W == 5
    def test_k_cs_is_74(self): assert K_CS == 74
    def test_braided_cs(self): assert BRAIDED_CS == pytest.approx(12/37, rel=1e-9)
    def test_braided_cs_value(self): assert BRAIDED_CS == pytest.approx(0.32432, rel=1e-4)
    def test_planck_length(self): assert PLANCK_LENGTH_M == pytest.approx(1.616e-35, rel=1e-3)
    def test_planck_length_positive(self): assert PLANCK_LENGTH_M > 0
    def test_l_kk_m_positive(self): assert L_KK_M > 0
    def test_l_kk_m_formula(self): assert L_KK_M == pytest.approx(math.sqrt(74)*1.616e-35, rel=1e-6)
    def test_l_kk_m_larger_than_planck(self): assert L_KK_M > PLANCK_LENGTH_M
    def test_l_kk_m_order_of_magnitude(self): assert 1e-34 < L_KK_M < 2e-34
    def test_m_to_gev_inv(self): assert M_TO_GEV_INV == pytest.approx(5.068e15, rel=1e-3)
    def test_l_kk_gev_inv_positive(self): assert L_KK_GEV_INV > 0
    def test_l_kk_gev_inv_formula(self): assert L_KK_GEV_INV == pytest.approx(L_KK_M*5.068e15, rel=1e-6)
    def test_n_w_type(self): assert isinstance(N_W, int)
    def test_k_cs_type(self): assert isinstance(K_CS, int)


class TestCausalInvariance:
    def test_returns_dict(self): assert isinstance(causal_invariance_from_information_current(), dict)
    def test_has_divergence_norm(self): assert "divergence_norm" in causal_invariance_from_information_current()
    def test_has_causal_invariant(self): assert "causal_invariant" in causal_invariance_from_information_current()
    def test_has_interpretation(self): assert "interpretation" in causal_invariance_from_information_current()
    def test_has_wolfram_analogue(self): assert "wolfram_analogue" in causal_invariance_from_information_current()
    def test_has_status(self): assert "status" in causal_invariance_from_information_current()
    def test_divergence_norm_small(self): assert causal_invariance_from_information_current()["divergence_norm"] < 1e-2
    def test_divergence_norm_positive(self): assert causal_invariance_from_information_current()["divergence_norm"] >= 0
    def test_causal_invariant_true(self): assert causal_invariance_from_information_current()["causal_invariant"] is True
    def test_status_verified(self): assert causal_invariance_from_information_current()["status"] == "VERIFIED"
    def test_interpretation_string(self):
        r = causal_invariance_from_information_current()
        assert isinstance(r["interpretation"], str) and len(r["interpretation"]) > 5
    def test_wolfram_analogue_string(self): assert isinstance(causal_invariance_from_information_current()["wolfram_analogue"], str)
    def test_divergence_norm_float(self): assert isinstance(causal_invariance_from_information_current()["divergence_norm"], float)
    def test_causal_invariant_bool(self): assert isinstance(causal_invariance_from_information_current()["causal_invariant"], bool)
    def test_five_keys_present(self):
        r = causal_invariance_from_information_current()
        for key in ["divergence_norm","causal_invariant","interpretation","wolfram_analogue","status"]: assert key in r


class TestKKElementaryLength:
    def test_returns_float(self): assert isinstance(kk_elementary_length(), float)
    def test_equals_l_kk_m(self): assert kk_elementary_length() == pytest.approx(L_KK_M, rel=1e-9)
    def test_positive(self): assert kk_elementary_length() > 0
    def test_larger_than_planck(self): assert kk_elementary_length() > PLANCK_LENGTH_M
    def test_value_approx(self): assert kk_elementary_length() == pytest.approx(math.sqrt(74)*1.616e-35, rel=1e-6)
    def test_order_of_magnitude(self): assert 1e-34 < kk_elementary_length() < 2e-34


class TestHausdorffDimensionUV:
    def test_returns_float(self): assert isinstance(hausdorff_dimension_uv(), float)
    def test_value(self): assert hausdorff_dimension_uv() == pytest.approx(2.0+5/74, rel=1e-9)
    def test_greater_than_2(self): assert hausdorff_dimension_uv() > 2.0
    def test_less_than_3(self): assert hausdorff_dimension_uv() < 3.0
    def test_approx_2068(self): assert hausdorff_dimension_uv() == pytest.approx(2.0+5/74, abs=1e-6)
    def test_correction_is_nw_over_kcs(self): assert hausdorff_dimension_uv()-2.0 == pytest.approx(N_W/K_CS, rel=1e-9)


class TestHausdorffDimensionIR:
    def test_returns_float(self): assert isinstance(hausdorff_dimension_ir(), float)
    def test_value(self): assert hausdorff_dimension_ir() == pytest.approx(4.0-5/74, rel=1e-9)
    def test_less_than_4(self): assert hausdorff_dimension_ir() < 4.0
    def test_greater_than_3(self): assert hausdorff_dimension_ir() > 3.0
    def test_sum_uv_ir(self): assert hausdorff_dimension_uv()+hausdorff_dimension_ir() == pytest.approx(6.0, rel=1e-9)
    def test_ir_minus_uv(self):
        delta = N_W/K_CS
        assert hausdorff_dimension_ir()-hausdorff_dimension_uv() == pytest.approx(2.0-2*delta, rel=1e-9)


class TestNodeDensity:
    def test_positive_result(self): assert causal_graph_node_density(1.0) > 0
    def test_raises_on_zero(self):
        with pytest.raises((ValueError, ZeroDivisionError)): causal_graph_node_density(0.0)
    def test_raises_on_negative(self):
        with pytest.raises(ValueError): causal_graph_node_density(-1.0)
    def test_decreases_with_scale(self): assert causal_graph_node_density(1.0) > causal_graph_node_density(10.0)
    def test_returns_float(self): assert isinstance(causal_graph_node_density(1.0), float)
    def test_high_energy_higher_density(self): assert causal_graph_node_density(0.001) > causal_graph_node_density(1.0)
    def test_scaling_law(self): assert causal_graph_node_density(2.0) == pytest.approx(causal_graph_node_density(1.0)/8.0, rel=1e-9)
    def test_very_small_scale(self): assert causal_graph_node_density(1e-10) > 1.0
    def test_formula_consistency(self):
        scale = 0.5
        assert causal_graph_node_density(scale) == pytest.approx((scale*L_KK_GEV_INV)**(-3), rel=1e-9)


class TestWolframAudit:
    def test_returns_dict(self): assert isinstance(wolfram_um_correspondence_audit(), dict)
    def test_status(self): assert wolfram_um_correspondence_audit()["status"] == "ALIGNMENT_DEMONSTRATED"
    def test_elementary_length(self): assert wolfram_um_correspondence_audit()["elementary_length_m"] == pytest.approx(L_KK_M, rel=1e-9)
    def test_hausdorff_uv(self): assert wolfram_um_correspondence_audit()["hausdorff_uv"] == pytest.approx(hausdorff_dimension_uv(), rel=1e-9)
    def test_hausdorff_ir(self): assert wolfram_um_correspondence_audit()["hausdorff_ir"] == pytest.approx(hausdorff_dimension_ir(), rel=1e-9)
    def test_causal_invariant(self): assert wolfram_um_correspondence_audit()["causal_invariant"] is True
    def test_wolfram_similarity_str(self):
        r = wolfram_um_correspondence_audit()
        assert isinstance(r["wolfram_similarity"], str) and len(r["wolfram_similarity"]) > 10
    def test_um_advantage_litebird(self): assert "LiteBIRD" in wolfram_um_correspondence_audit()["um_advantage"]
    def test_um_advantage_wolfram(self): assert "Wolfram" in wolfram_um_correspondence_audit()["um_advantage"]
    def test_audit_keys_complete(self):
        r = wolfram_um_correspondence_audit()
        for key in ["elementary_length_m","hausdorff_uv","hausdorff_ir","causal_invariant","wolfram_similarity","um_advantage","status"]: assert key in r
    def test_elementary_length_positive(self): assert wolfram_um_correspondence_audit()["elementary_length_m"] > 0
    def test_hausdorff_uv_greater_than_2(self): assert wolfram_um_correspondence_audit()["hausdorff_uv"] > 2.0
    def test_hausdorff_ir_less_than_4(self): assert wolfram_um_correspondence_audit()["hausdorff_ir"] < 4.0


class TestPillar173Summary:
    def test_returns_string(self): assert isinstance(pillar173_summary(), str)
    def test_contains_173(self): assert "173" in pillar173_summary()
    def test_contains_status(self): assert "ALIGNMENT_DEMONSTRATED" in pillar173_summary()
    def test_contains_l_kk(self):
        s = pillar173_summary()
        assert "L_KK" in s or "kk" in s.lower()
    def test_contains_hausdorff_values(self):
        s = pillar173_summary()
        assert "d_H" in s or "2.0" in s
    def test_nonempty(self): assert len(pillar173_summary()) > 20
    def test_contains_causal_invariant(self):
        s = pillar173_summary()
        assert "causal_invariant" in s or "True" in s


class TestConsistency:
    def test_uv_plus_ir_symmetric(self):
        delta = N_W/K_CS
        assert hausdorff_dimension_uv() == pytest.approx(2.0+delta, rel=1e-9)
        assert hausdorff_dimension_ir() == pytest.approx(4.0-delta, rel=1e-9)
    def test_l_kk_order_of_magnitude(self): assert 1e-34 < kk_elementary_length() < 1e-33
    def test_audit_uv_matches_standalone(self): assert wolfram_um_correspondence_audit()["hausdorff_uv"] == pytest.approx(hausdorff_dimension_uv(), rel=1e-12)
    def test_audit_ir_matches_standalone(self): assert wolfram_um_correspondence_audit()["hausdorff_ir"] == pytest.approx(hausdorff_dimension_ir(), rel=1e-12)
    def test_audit_length_matches_standalone(self): assert wolfram_um_correspondence_audit()["elementary_length_m"] == pytest.approx(kk_elementary_length(), rel=1e-12)
    def test_braided_cs_less_than_1(self): assert BRAIDED_CS < 1.0
    def test_braided_cs_numerator_denominator(self): assert abs(BRAIDED_CS - 12/37) < 1e-15
