# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 413 — Talagrand Convexity Conjecture: UM Geometric Analysis."""
from __future__ import annotations

import math
import pytest

from src.core.pillar413_talagrand_convexity import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    ADJACENCY_TRACK_LABEL,
    N_W,
    K_CS,
    C_S,
    ETA_BAR,
    SIGMA_KK_SQUARED,
    SIGMA_KK,
    C_UM,
    C_PROOF,
    N_C_COLORS,
    LAMBDA_C,
    EPSILON_TAL,
    kk_subgaussian_variance,
    kk_is_one_subgaussian,
    minkowski_step_count,
    nc_coincidence_check,
    ftum_concentration_bound,
    braid_gaussian_decomposition,
    talagrand_approximation_scale,
    mgf_kk_bound,
    proof_alignment_summary,
    pillar413_status,
)


# ── Identity tests ────────────────────────────────────────────────────────────


class TestPillarIdentity:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 413

    def test_pillar_status(self):
        assert PILLAR_STATUS == "STRUCTURAL_CORRESPONDENCE"

    def test_adjacency_label(self):
        assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"

    def test_pillar413_status_function(self):
        assert pillar413_status() == "STRUCTURAL_CORRESPONDENCE"


# ── UM constant tests ─────────────────────────────────────────────────────────


class TestUMConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_k_cs_is_5sq_plus_7sq(self):
        assert K_CS == 5 ** 2 + 7 ** 2

    def test_c_s(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-12

    def test_eta_bar(self):
        assert ETA_BAR == 0.5

    def test_c_proof(self):
        assert C_PROOF == 3

    def test_n_c_colors(self):
        assert N_C_COLORS == 3

    def test_lambda_c_equals_c_s(self):
        assert abs(LAMBDA_C - C_S) < 1e-12


# ── Subgaussian parameter tests ───────────────────────────────────────────────


class TestSubgaussianParameter:
    def test_sigma_kk_squared_formula(self):
        expected = 5 / 148  # n_w / (2 * K_CS)
        assert abs(SIGMA_KK_SQUARED - expected) < 1e-12

    def test_sigma_kk_squared_function(self):
        assert abs(kk_subgaussian_variance() - SIGMA_KK_SQUARED) < 1e-12

    def test_sigma_kk_squared_positive(self):
        assert kk_subgaussian_variance() > 0.0

    def test_sigma_kk_squared_less_than_1(self):
        assert kk_subgaussian_variance() < 1.0

    def test_sigma_kk_squared_value(self):
        # 5/148 ≈ 0.03378...
        assert abs(kk_subgaussian_variance() - 0.033783783783) < 1e-9

    def test_sigma_kk_is_sqrt_of_squared(self):
        assert abs(SIGMA_KK - math.sqrt(SIGMA_KK_SQUARED)) < 1e-12

    def test_sigma_kk_positive(self):
        assert SIGMA_KK > 0.0

    def test_sigma_kk_less_than_1(self):
        assert SIGMA_KK < 1.0


# ── 1-subgaussian check ────────────────────────────────────────────────────────


class TestOneSubgaussian:
    def test_kk_is_one_subgaussian(self):
        assert kk_is_one_subgaussian() is True

    def test_kk_subgaussian_much_less_than_1(self):
        # σ²_KK ≈ 0.034 is well within the 1-subgaussian threshold
        assert kk_subgaussian_variance() < 0.1

    def test_kk_subgaussian_threshold_margin(self):
        # The gap from threshold = 1 is substantial (> 0.96)
        assert (1.0 - kk_subgaussian_variance()) > 0.96


# ── Minkowski step count ───────────────────────────────────────────────────────


class TestMinkowskiStepCount:
    def test_c_um_equals_3(self):
        assert C_UM == 3

    def test_minkowski_step_count_function(self):
        assert minkowski_step_count() == 3

    def test_c_um_equals_c_proof(self):
        assert C_UM == C_PROOF

    def test_minkowski_count_matches_proof(self):
        assert minkowski_step_count() == C_PROOF

    def test_raw_ratio(self):
        # K_CS / (n_w * (n_w+2)) = 74/35 ≈ 2.114 → ceil = 3
        raw = K_CS / (N_W * (N_W + 2))
        assert abs(raw - 74.0 / 35.0) < 1e-10
        assert raw < 3.0
        assert math.ceil(raw) == 3

    def test_denominator_is_35(self):
        # n_w * (n_w + 2) = 5 * 7 = 35
        assert N_W * (N_W + 2) == 35


# ── Triple coincidence test ────────────────────────────────────────────────────


class TestTripleCoincidence:
    def test_nc_coincidence_all_equal(self):
        result = nc_coincidence_check()
        assert result["all_equal"] is True

    def test_nc_coincidence_c_proof(self):
        result = nc_coincidence_check()
        assert result["c_proof"] == 3

    def test_nc_coincidence_c_um(self):
        result = nc_coincidence_check()
        assert result["c_um"] == 3

    def test_nc_coincidence_n_c_colors(self):
        result = nc_coincidence_check()
        assert result["n_c_colors"] == 3

    def test_triple_all_same_value(self):
        result = nc_coincidence_check()
        assert result["c_proof"] == result["c_um"] == result["n_c_colors"]


# ── FTUM concentration bound ───────────────────────────────────────────────────


class TestFTUMConcentration:
    def test_ftum_bound_t0(self):
        # ε(0) = λ_c^0 = 1.0
        assert abs(ftum_concentration_bound(0) - 1.0) < 1e-12

    def test_ftum_bound_t1(self):
        # ε(1) = 12/37
        expected = 12.0 / 37.0
        assert abs(ftum_concentration_bound(1) - expected) < 1e-12

    def test_ftum_bound_decreasing(self):
        eps = [ftum_concentration_bound(t) for t in range(10)]
        for i in range(1, len(eps)):
            assert eps[i] < eps[i - 1]

    def test_ftum_bound_geometric(self):
        # ε(t) = (12/37)^t
        for t in range(1, 8):
            expected = (12.0 / 37.0) ** t
            assert abs(ftum_concentration_bound(t) - expected) < 1e-10

    def test_ftum_bound_large_t(self):
        # After 20 steps, residual < 1e-8
        assert ftum_concentration_bound(20) < 1e-8

    def test_ftum_bound_rate_lt_half(self):
        # λ_c = 12/37 < 0.5 → super-linear concentration
        assert LAMBDA_C < 0.5


# ── Braid Gaussian decomposition ──────────────────────────────────────────────


class TestBraidGaussianDecomposition:
    def test_n_components_is_3(self):
        d = braid_gaussian_decomposition()
        assert d["n_components"] == 3

    def test_sigma_sq_each(self):
        d = braid_gaussian_decomposition()
        assert abs(d["sigma_sq_each"] - kk_subgaussian_variance()) < 1e-12

    def test_total_variance(self):
        d = braid_gaussian_decomposition()
        expected = 3 * kk_subgaussian_variance()
        assert abs(d["total_variance"] - expected) < 1e-12

    def test_combined_sigma(self):
        d = braid_gaussian_decomposition()
        expected = math.sqrt(3 * kk_subgaussian_variance())
        assert abs(d["combined_sigma"] - expected) < 1e-12

    def test_label(self):
        d = braid_gaussian_decomposition()
        assert d["label"] == "BRAID_GAUSSIAN_DECOMPOSITION"

    def test_hst_alignment_label(self):
        d = braid_gaussian_decomposition()
        assert d["hst_theorem_alignment"] == "STRUCTURAL_CORRESPONDENCE"

    def test_total_variance_value(self):
        # 3 * (5/148) = 15/148 ≈ 0.10135
        d = braid_gaussian_decomposition()
        assert abs(d["total_variance"] - 15.0 / 148.0) < 1e-10

    def test_combined_sigma_positive(self):
        d = braid_gaussian_decomposition()
        assert d["combined_sigma"] > 0.0


# ── Talagrand approximation scale ─────────────────────────────────────────────


class TestApproximationScale:
    def test_epsilon_tal_formula(self):
        expected = math.sqrt(74 / 10)
        assert abs(EPSILON_TAL - expected) < 1e-10

    def test_epsilon_tal_function(self):
        assert abs(talagrand_approximation_scale() - EPSILON_TAL) < 1e-12

    def test_epsilon_tal_value(self):
        # √7.4 ≈ 2.720
        assert abs(EPSILON_TAL - 2.7202941017) < 1e-6

    def test_epsilon_tal_positive(self):
        assert EPSILON_TAL > 0.0

    def test_epsilon_tal_greater_than_2(self):
        assert EPSILON_TAL > 2.0

    def test_epsilon_tal_less_than_3(self):
        assert EPSILON_TAL < 3.0


# ── MGF bound ─────────────────────────────────────────────────────────────────


class TestMGFBound:
    def test_mgf_at_zero(self):
        # exp(0) = 1
        assert abs(mgf_kk_bound(0.0) - 1.0) < 1e-12

    def test_mgf_at_1(self):
        expected = math.exp(0.5 * kk_subgaussian_variance())
        assert abs(mgf_kk_bound(1.0) - expected) < 1e-10

    def test_mgf_at_minus_1(self):
        # Symmetric: MGF(-t) = MGF(t) for subgaussian
        assert abs(mgf_kk_bound(-1.0) - mgf_kk_bound(1.0)) < 1e-12

    def test_mgf_increasing(self):
        vals = [mgf_kk_bound(float(t)) for t in range(6)]
        for i in range(1, len(vals)):
            assert vals[i] > vals[i - 1]

    def test_mgf_is_gaussian_shaped(self):
        # The MGF of a subgaussian is dominated by exp(t^2 sigma^2 / 2)
        sigma_sq = kk_subgaussian_variance()
        for t in [0.5, 1.0, 2.0]:
            bound = mgf_kk_bound(t)
            expected = math.exp(0.5 * sigma_sq * t ** 2)
            assert abs(bound - expected) < 1e-10

    def test_mgf_small_t_approx(self):
        # For small t, MGF ≈ 1 + t^2 sigma^2/2
        t = 0.01
        sigma_sq = kk_subgaussian_variance()
        mgf = mgf_kk_bound(t)
        taylor = 1.0 + 0.5 * sigma_sq * t ** 2
        assert abs(mgf - taylor) < 1e-8


# ── Proof alignment summary ───────────────────────────────────────────────────


class TestProofAlignmentSummary:
    def test_returns_dict(self):
        result = proof_alignment_summary()
        assert isinstance(result, dict)

    def test_pillar_number(self):
        result = proof_alignment_summary()
        assert result["pillar"] == 413

    def test_status(self):
        result = proof_alignment_summary()
        assert result["status"] == "STRUCTURAL_CORRESPONDENCE"

    def test_adjacency(self):
        result = proof_alignment_summary()
        assert result["adjacency"] == "NON_HARDGATE_ADJACENT"

    def test_reference(self):
        result = proof_alignment_summary()
        assert "Hwa" in result["reference"]
        assert "2026" in result["reference"]

    def test_all_matched(self):
        result = proof_alignment_summary()
        assert result["all_matched"] is True

    def test_triple_coincidence(self):
        result = proof_alignment_summary()
        assert result["triple_coincidence"] is True

    def test_alignments_count(self):
        result = proof_alignment_summary()
        assert len(result["alignments"]) == 4

    def test_c_um_alignment_match(self):
        result = proof_alignment_summary()
        c_align = next(
            a for a in result["alignments"] if a["label"] == "C_UM_EQ_C_PROOF"
        )
        assert c_align["match"] is True
        assert c_align["um_value"] == 3
        assert c_align["hst_value"] == 3

    def test_nc_alignment_match(self):
        result = proof_alignment_summary()
        nc_align = next(
            a for a in result["alignments"] if a["label"] == "NC_EQ_C_PROOF"
        )
        assert nc_align["match"] is True

    def test_subgaussian_alignment_match(self):
        result = proof_alignment_summary()
        sg_align = next(
            a for a in result["alignments"]
            if a["label"] == "KK_IS_ONE_SUBGAUSSIAN"
        )
        assert sg_align["match"] is True
        assert sg_align["um_value"] < 1.0
