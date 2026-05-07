# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for CC 5D Ceiling Proof (Pillar 224, Track A Session 7)."""

import math
import pytest

from src.core.cc_5d_ceiling_proof import (
    N_W, K_CS,
    M_PL_GEV, PI_KR, M_KK_GEV,
    LAMBDA_OBS_MPLAN4,
    LOG10_LAMBDA_OBS,
    LOG10_MKK4_MPLAN4,
    GAP_TOTAL_LOG10,
    GAP_REDUCED_BY_RS1,
    RESIDUAL_GAP_LOG10,
    ARCHITECTURE_LIMIT,
    REQUIRES_DIMENSION,
    enumerate_5d_mechanisms,
    mechanism_contribution,
    total_5d_reduction,
    ceiling_proof,
    why_10d_required,
    cc_5d_ceiling_audit,
    pillar224_summary,
)


class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_lambda_obs_tiny(self):
        assert LAMBDA_OBS_MPLAN4 < 1e-100

    def test_log10_lambda_obs_approx_minus122(self):
        assert LOG10_LAMBDA_OBS == pytest.approx(-122.0, abs=5.0)

    def test_log10_mkk4_negative(self):
        assert LOG10_MKK4_MPLAN4 < 0

    def test_log10_mkk4_approx_minus64(self):
        # 4 × πkR × log₁₀(e) ≈ 4 × 37 × 0.434 ≈ 64
        assert -70 < LOG10_MKK4_MPLAN4 < -55

    def test_gap_total_approx_122(self):
        assert 110 < GAP_TOTAL_LOG10 < 130

    def test_gap_reduced_by_rs1_approx_64(self):
        assert 55 < GAP_REDUCED_BY_RS1 < 75

    def test_residual_gap_approx_58(self):
        assert 45 < RESIDUAL_GAP_LOG10 < 70

    def test_residual_gap_less_than_total(self):
        assert RESIDUAL_GAP_LOG10 < GAP_TOTAL_LOG10

    def test_architecture_limit_true(self):
        assert ARCHITECTURE_LIMIT is True

    def test_requires_dimension_10(self):
        assert REQUIRES_DIMENSION == 10


class TestEnumerate5DMechanisms:
    def test_returns_list(self):
        result = enumerate_5d_mechanisms()
        assert isinstance(result, list)

    def test_has_8_mechanisms(self):
        result = enumerate_5d_mechanisms()
        assert len(result) == 8

    def test_mechanism_1_is_rs1_warp(self):
        result = enumerate_5d_mechanisms()
        assert "RS1" in result[0]["name"] or "warp" in result[0]["name"].lower()

    def test_mechanism_7_is_cs_zero(self):
        result = enumerate_5d_mechanisms()
        m7 = next(m for m in result if m["id"] == 7)
        assert m7["log10_reduction"] == 0.0

    def test_all_have_status(self):
        for m in enumerate_5d_mechanisms():
            assert "status" in m

    def test_all_have_id(self):
        for m in enumerate_5d_mechanisms():
            assert "id" in m


class TestMechanismContribution:
    def test_mechanism_1_valid(self):
        m1 = mechanism_contribution(1)
        assert m1["id"] == 1

    def test_mechanism_7_log10_zero(self):
        m7 = mechanism_contribution(7)
        assert m7["log10_reduction"] == pytest.approx(0.0)

    def test_invalid_id_raises(self):
        with pytest.raises(ValueError):
            mechanism_contribution(99)


class TestTotal5DReduction:
    def test_returns_dict(self):
        result = total_5d_reduction()
        assert isinstance(result, dict)

    def test_gap_total_matches_constant(self):
        result = total_5d_reduction()
        assert result["gap_total_log10"] == pytest.approx(GAP_TOTAL_LOG10, rel=1e-6)

    def test_rs1_reduction_is_dominant(self):
        result = total_5d_reduction()
        assert result["rs1_warp_reduction_log10"] > 50

    def test_residual_gap_present(self):
        result = total_5d_reduction()
        assert "residual_gap_log10" in result

    def test_fraction_closed_between_0_and_1(self):
        result = total_5d_reduction()
        assert 0 < result["fraction_closed_by_5d"] < 1


class TestCeilingProof:
    def test_returns_dict(self):
        result = ceiling_proof()
        assert isinstance(result, dict)

    def test_has_theorem(self):
        result = ceiling_proof()
        assert "theorem" in result

    def test_has_proof_steps(self):
        result = ceiling_proof()
        assert len(result["proof_steps"]) >= 7

    def test_verdict_mentions_proved(self):
        result = ceiling_proof()
        assert "PROVED" in result["verdict"] or "proved" in result["verdict"].lower()

    def test_all_mechanisms_evaluated(self):
        result = ceiling_proof()
        assert len(result["mechanisms_evaluated"]) == 8


class TestWhy10DRequired:
    def test_returns_dict(self):
        result = why_10d_required()
        assert isinstance(result, dict)

    def test_requires_dimension_10(self):
        result = why_10d_required()
        assert result["requires_dimension"] == 10

    def test_mechanism_is_bousso_polchinski(self):
        result = why_10d_required()
        assert "Bousso" in result["mechanism"] or "flux" in result["mechanism"].lower()

    def test_um_connection_mentions_k_cs(self):
        result = why_10d_required()
        assert "74" in result["um_connection"] or "k_CS" in result["um_connection"]

    def test_logic_steps_present(self):
        result = why_10d_required()
        assert len(result["logic"]) >= 4


class TestCC5DCeilingAudit:
    def test_returns_dict(self):
        result = cc_5d_ceiling_audit()
        assert isinstance(result, dict)

    def test_module_name(self):
        result = cc_5d_ceiling_audit()
        assert result["module"] == "cc_5d_ceiling_proof"

    def test_pillar_224(self):
        result = cc_5d_ceiling_audit()
        assert result["pillar"] == 224

    def test_verdict_present(self):
        result = cc_5d_ceiling_audit()
        assert len(result["verdict"]) > 50

    def test_constants_present(self):
        result = cc_5d_ceiling_audit()
        assert "LOG10_LAMBDA_OBS" in result["constants"]
        assert "RESIDUAL_GAP_LOG10" in result["constants"]


class TestPillar224Summary:
    def test_returns_dict(self):
        s = pillar224_summary()
        assert isinstance(s, dict)

    def test_pillar_224(self):
        s = pillar224_summary()
        assert s["pillar"] == 224

    def test_architecture_limit_true(self):
        s = pillar224_summary()
        assert s["architecture_limit"] is True

    def test_requires_dimension_10(self):
        s = pillar224_summary()
        assert s["requires_dimension"] == REQUIRES_DIMENSION

    def test_n_mechanisms_evaluated_is_8(self):
        s = pillar224_summary()
        assert s["n_mechanisms_evaluated"] == 8
