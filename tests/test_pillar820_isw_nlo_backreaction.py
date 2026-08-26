# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 820 — ISW NLO Back-Reaction Closure."""
from __future__ import annotations

import numpy as np
import pytest

from src.core.pillar820_isw_nlo_backreaction import (
    ALPHA_BR,
    A_BR,
    ISW_NLO_RESULT,
    ISW_NLO_THRESHOLD,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    N_W,
    K_CS,
    PHI_0,
    PILLAR_GATE,
    PILLAR_NUMBER,
    compute_isw_nlo_correction,
    compute_isw_nlo_spectrum,
    isw_nlo_closure_verdict,
)


class TestPillar820Constants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 820

    def test_gate(self):
        assert PILLAR_GATE == "ISW_NLO_PERTURBATIVE_CLOSED"

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_phi_0(self):
        assert PHI_0 == 37.0

    def test_alpha_br(self):
        assert abs(ALPHA_BR - 25 / 148) < 1e-10

    def test_a_br(self):
        assert abs(A_BR - 6e-4) < 1e-12

    def test_isw_nlo_threshold(self):
        assert ISW_NLO_THRESHOLD == 1e-3

    def test_lean4_count(self):
        assert LEAN4_THEOREM_COUNT == 20

    def test_lean4_total_before(self):
        assert LEAN4_TOTAL_BEFORE == 1411

    def test_lean4_total_after(self):
        assert LEAN4_TOTAL_AFTER == LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT


class TestISWNLOCorrection:
    def test_correction_at_pivot_k(self):
        """ISW NLO correction at pivot wavenumber k=1e-4 Mpc⁻¹."""
        corr = compute_isw_nlo_correction(1e-4)
        assert corr >= 0.0

    def test_correction_sub_threshold(self):
        """Correction at any reasonable k must be well below 0.1%."""
        for k in [1e-4, 1e-3, 1e-2]:
            corr = compute_isw_nlo_correction(k)
            assert corr < ISW_NLO_THRESHOLD, f"k={k}: corr={corr} ≥ threshold"

    def test_correction_positive(self):
        """ISW always adds power (positive correction)."""
        corr = compute_isw_nlo_correction(1e-4)
        assert corr >= 0.0

    def test_correction_at_large_k_small(self):
        """Silk damping ensures correction drops at large k."""
        corr_small_k = compute_isw_nlo_correction(1e-4)
        corr_large_k = compute_isw_nlo_correction(1.0)
        assert corr_large_k <= corr_small_k + 1e-10

    def test_correction_formula(self):
        """Check correction = 4 × α_BR / φ₀ × δφ(η_rec, k)."""
        from src.core.pillar820_isw_nlo_backreaction import _radion_amplitude_at_recombination
        k = 1e-4
        delta_phi = _radion_amplitude_at_recombination(k)
        expected = 4.0 * ALPHA_BR / PHI_0 * delta_phi
        assert abs(compute_isw_nlo_correction(k) - expected) < 1e-15


class TestISWNLOSpectrum:
    def test_spectrum_runs(self):
        """Spectrum computation returns a valid ISWNLOResult."""
        result = compute_isw_nlo_spectrum(n_ell=10)
        assert result.isw_spectrum_ell.shape[0] == 10
        assert result.isw_spectrum_corr.shape[0] == 10

    def test_spectrum_all_positive(self):
        result = compute_isw_nlo_spectrum(n_ell=10)
        assert np.all(result.isw_spectrum_corr >= 0)

    def test_median_below_threshold(self):
        result = compute_isw_nlo_spectrum(n_ell=20)
        assert result.median_correction < ISW_NLO_THRESHOLD

    def test_is_perturbative_true(self):
        result = compute_isw_nlo_spectrum(n_ell=20)
        assert result.is_perturbative is True

    def test_gate_closed(self):
        result = compute_isw_nlo_spectrum(n_ell=20)
        assert result.gate == PILLAR_GATE

    def test_ell_range(self):
        result = compute_isw_nlo_spectrum(ell_min=2, ell_max=1000, n_ell=30)
        assert result.isw_spectrum_ell[0] >= 2
        assert result.isw_spectrum_ell[-1] <= 1000

    def test_max_correction_sub_percent(self):
        result = compute_isw_nlo_spectrum(n_ell=30)
        assert result.max_correction < 0.01  # sub-1%

    def test_delta_phi_rec_positive(self):
        result = compute_isw_nlo_spectrum(n_ell=10)
        assert result.delta_phi_rec >= 0


class TestISWNLOVerdict:
    def test_verdict_closure_true(self):
        verdict = isw_nlo_closure_verdict()
        assert verdict["closure"] is True

    def test_verdict_gate(self):
        verdict = isw_nlo_closure_verdict()
        assert verdict["gate"] == PILLAR_GATE

    def test_verdict_pillar(self):
        verdict = isw_nlo_closure_verdict()
        assert verdict["pillar"] == 820

    def test_verdict_open_items(self):
        verdict = isw_nlo_closure_verdict()
        assert len(verdict["open_items"]) >= 3

    def test_verdict_interpretation(self):
        verdict = isw_nlo_closure_verdict()
        assert "perturbative" in verdict["interpretation"].lower()

    def test_verdict_alpha_br(self):
        verdict = isw_nlo_closure_verdict()
        assert abs(verdict["alpha_br"] - ALPHA_BR) < 1e-10

    def test_verdict_lean4(self):
        verdict = isw_nlo_closure_verdict()
        assert verdict["lean4_theorems"] == 20
        assert verdict["lean4_total"] == 1431

    def test_verdict_is_perturbative(self):
        verdict = isw_nlo_closure_verdict()
        assert verdict["is_perturbative"] is True


class TestISWNLOModuleSingleton:
    def test_singleton_exists(self):
        assert ISW_NLO_RESULT is not None

    def test_singleton_is_perturbative(self):
        assert ISW_NLO_RESULT.is_perturbative is True

    def test_singleton_gate(self):
        assert ISW_NLO_RESULT.gate == PILLAR_GATE
