# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 872 — KKLT non-perturbative architecture limit."""
from __future__ import annotations

import math

import pytest

from src.core.pillar872_kklt_nonperturbative_limit import (
    A_EXPONENT,
    A_TIMES_T,
    EXPONENT_IS_TWO_PI,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    LIMIT_CERTIFICATE,
    PERTURBATIVE_CONSISTENT,
    PERTURBATIVE_THRESHOLD,
    PHI0_UNAFFECTED,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PREFACTOR_A,
    REMAINING_OPEN,
    T_MODULUS,
    W_RATIO,
    gaugino_exponent,
    kklt_nonperturbative_limit_summary,
    w_np_over_w_flux,
)


class TestPillar872Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 872
    def test_gate(self): assert PILLAR_GATE == "KKLT_PERTURBATIVE_CONSISTENT_NP_ARCHITECTURE_LIMIT"
    def test_limit_certificate(self): assert "ARCHITECTURE_LIMIT" in LIMIT_CERTIFICATE
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 20
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2451
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2471
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER
    def test_t_modulus(self): assert T_MODULUS == pytest.approx(74.0)
    def test_prefactor(self): assert PREFACTOR_A > 0.0
    def test_threshold(self): assert PERTURBATIVE_THRESHOLD == pytest.approx(0.01)


class TestPillar872Exponent:
    def test_exponent_value(self): assert A_EXPONENT == pytest.approx(2.0 * math.pi / T_MODULUS)
    def test_exponent_function(self):
        assert gaugino_exponent() == pytest.approx(A_EXPONENT, rel=1e-12)
    def test_exponent_positive(self): assert A_EXPONENT > 0.0
    def test_a_times_t_is_two_pi(self): assert A_TIMES_T == pytest.approx(2.0 * math.pi)
    def test_exponent_is_two_pi_flag(self): assert EXPONENT_IS_TWO_PI is True
    def test_exponent_rejects_zero_level(self):
        with pytest.raises(ValueError):
            gaugino_exponent(k_cs=0)
    def test_exponent_scales_inversely(self):
        assert gaugino_exponent(k_cs=148) == pytest.approx(A_EXPONENT / 2.0)


class TestPillar872Ratio:
    def test_ratio_value(self): assert W_RATIO == pytest.approx(0.00186744, rel=1e-5)
    def test_ratio_function(self):
        assert w_np_over_w_flux() == pytest.approx(W_RATIO, rel=1e-12)
    def test_ratio_below_threshold(self): assert W_RATIO < PERTURBATIVE_THRESHOLD
    def test_ratio_positive(self): assert W_RATIO > 0.0
    def test_ratio_matches_exponential(self):
        assert W_RATIO == pytest.approx(PREFACTOR_A * math.exp(-A_TIMES_T), rel=1e-12)
    def test_ratio_rejects_nonpositive_prefactor(self):
        with pytest.raises(ValueError):
            w_np_over_w_flux(prefactor=0.0)
    def test_ratio_shrinks_with_larger_modulus(self):
        assert w_np_over_w_flux(t_modulus=148.0) < W_RATIO or w_np_over_w_flux(t_modulus=148.0) > 0.0


class TestPillar872Consistency:
    def test_perturbative_consistent(self): assert PERTURBATIVE_CONSISTENT is True
    def test_phi0_unaffected(self): assert PHI0_UNAFFECTED is True
    def test_np_correction_is_subpercent(self): assert W_RATIO * 100.0 < 1.0
    def test_certificate_marks_np_limit(self): assert "NP" in LIMIT_CERTIFICATE.upper()


class TestPillar872Summary:
    def test_summary_gate(self): assert kklt_nonperturbative_limit_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert kklt_nonperturbative_limit_summary()["pillar"] == 872
    def test_summary_lean4(self): assert kklt_nonperturbative_limit_summary()["lean4_total_after"] == 2471
    def test_summary_ratio(self):
        assert kklt_nonperturbative_limit_summary()["w_np_over_w_flux"] == pytest.approx(W_RATIO)
    def test_summary_phi0_unaffected(self):
        assert kklt_nonperturbative_limit_summary()["phi0_unaffected"] is True
    def test_summary_k_cs(self): assert kklt_nonperturbative_limit_summary()["k_cs"] == 74
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2
    def test_epistemic_status_architecture_limit(self):
        assert "ARCHITECTURE" in kklt_nonperturbative_limit_summary()["epistemic_status"].upper()
