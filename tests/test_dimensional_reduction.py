# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_dimensional_reduction.py
=====================================
Dimensional-reduction invariance tests (362 → 370).

Verifies that the 5D → 4D KK reduction pipeline is internally consistent:
the derived coupling α and the cross-block Riemann tensor must satisfy the
expected KK relations regardless of the specific φ or B background.

Eight independent checks covering:

  1. TestAlphaFormulaConsistency     — α = ⟨1/φ²⟩ matches curvature pipeline
  2. TestAlphaScalesAsPhiSquareInv  — α(φ = c) = 1/c² for constant φ
  3. TestCrossBlockZeroAtBZero      — R^μ_{5ν5} = 0 for B = 0, φ = const
  4. TestCrossBlockNonzeroForBGrad  — R^μ_{5ν5} ≠ 0 when ∂_x B ≠ 0
  5. TestRicciScalarFlatSpace       — R → 0 on exact flat space
  6. TestRicciScalesWithPerturbation — |R| increases monotonically with noise
  7. TestAlphaIndependentOfB        — α depends only on φ, not on B
  8. TestRadionStabilityPositive    — V''(φ₀_eff) > 0 (radion is not tachyonic)
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pytest

from src.core.metric import (
    extract_alpha_from_curvature,
    compute_curvature,
)
from src.core.inflation import (
    gw_potential_derivs,
    effective_phi0_kk,
)

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

_ETA  = np.diag([-1.0, 1.0, 1.0, 1.0])
_N    = 8
_DX   = 0.1
_G_FLAT = np.tile(_ETA, (_N, 1, 1)).astype(float)
_B_ZERO = np.zeros((_N, 4))


# ===========================================================================
# 1 — α = ⟨1/φ²⟩ matches the curvature-pipeline formula
# ===========================================================================

class TestAlphaFormulaConsistency:
    """α from extract_alpha_from_curvature equals the direct formula 1/φ₀²."""

    def test_alpha_matches_phi_inverse_square(self):
        """For φ = 2.5 (constant), α_pipeline = 1/2.5² = 0.16 exactly."""
        phi_val = 2.5
        phi = np.full(_N, phi_val)
        alpha, _ = extract_alpha_from_curvature(_G_FLAT, _B_ZERO, phi, _DX)
        expected = 1.0 / phi_val ** 2
        assert abs(alpha - expected) < 1e-10, (
            f"α={alpha:.12f} ≠ expected={expected:.12f}"
        )

    def test_alpha_mean_over_non_uniform_phi(self):
        """For φ varying across the grid, α = mean(1/φ²) elementwise."""
        rng = np.random.default_rng(5)
        phi = 1.0 + 0.1 * rng.standard_normal(_N)
        phi = np.maximum(phi, 0.5)
        alpha, _ = extract_alpha_from_curvature(_G_FLAT, _B_ZERO, phi, _DX)
        expected = float(np.mean(1.0 / phi ** 2))
        assert abs(alpha - expected) < 1e-10


# ===========================================================================
# 2 — α = 1/φ² for any constant φ
# ===========================================================================

class TestAlphaScalesAsPhiSquareInv:
    """α = φ⁻² exactly for constant-φ backgrounds at four different values."""

    @pytest.mark.parametrize("phi_val", [0.5, 1.0, 2.0, 10.0])
    def test_alpha_equals_phi_inverse_square(self, phi_val):
        phi = np.full(_N, phi_val)
        alpha, _ = extract_alpha_from_curvature(_G_FLAT, _B_ZERO, phi, _DX)
        expected = 1.0 / phi_val ** 2
        assert abs(alpha - expected) < 1e-10, (
            f"φ={phi_val}: α={alpha:.12f} ≠ 1/φ²={expected:.12f}"
        )


# ===========================================================================
# 3 — Cross-block Riemann vanishes for B = 0, φ = const on flat space
# ===========================================================================

class TestCrossBlockZeroAtBZero:
    """R^μ_{5ν5} = 0 when B = 0 and φ is constant on flat space.

    For the block-diagonal 5D metric G = diag(η_μν, φ²) (with B = 0,
    φ = const), all derivatives of G vanish and therefore every Christoffel
    symbol and every Riemann component is identically zero.
    """

    def test_cross_block_zero_constant_phi_no_B(self):
        phi = np.ones(_N)
        _, cross = extract_alpha_from_curvature(_G_FLAT, _B_ZERO, phi, _DX)
        assert np.allclose(cross, 0.0, atol=1e-10), (
            f"max |cross| = {np.max(np.abs(cross)):.3e}"
        )

    def test_cross_block_zero_for_larger_phi(self):
        """Cross-block Riemann also vanishes for φ = 3 (constant)."""
        phi = np.full(_N, 3.0)
        _, cross = extract_alpha_from_curvature(_G_FLAT, _B_ZERO, phi, _DX)
        assert np.allclose(cross, 0.0, atol=1e-10), (
            f"max |cross| = {np.max(np.abs(cross)):.3e}"
        )


# ===========================================================================
# 4 — Cross-block Riemann is non-zero when ∂_x B ≠ 0
# ===========================================================================

class TestCrossBlockNonzeroForBGrad:
    """R^μ_{5ν5} ≠ 0 when the gauge field has a spatial gradient.

    A linearly varying B_1 makes G_{15} = G_{51} = λφ B_1 depend on x,
    which yields non-zero 5D Christoffel symbols and hence non-zero
    cross-block Riemann components.
    """

    def test_cross_block_nonzero_with_linear_B(self):
        phi = np.ones(_N)
        B = np.zeros((_N, 4))
        x = np.arange(_N) * _DX
        B[:, 1] = 0.5 * x          # linear gradient in B_1
        _, cross = extract_alpha_from_curvature(_G_FLAT, B, phi, _DX)
        assert not np.allclose(cross, 0.0, atol=1e-6), (
            f"Expected non-zero cross-block for B with gradient; "
            f"max |cross| = {np.max(np.abs(cross)):.3e}"
        )


# ===========================================================================
# 5 — Ricci scalar vanishes on exact flat space
# ===========================================================================

class TestRicciScalarFlatSpace:
    """R = 0 on exact Minkowski background with B = 0 and φ = const.

    All first derivatives of the 5D metric vanish ⟹ all Christoffels vanish
    ⟹ Riemann = 0 ⟹ Ricci = 0 ⟹ R = 0.  This tests the 4D→5D→4D
    pipeline returns the correct flat-space limit.
    """

    def test_ricci_zero_on_exact_flat_space(self):
        phi = np.ones(_N)
        _, _, _, R = compute_curvature(_G_FLAT, _B_ZERO, phi, _DX)
        assert np.max(np.abs(R)) < 1e-10, (
            f"Expected R ≈ 0 on flat space, got R_max = {np.max(np.abs(R)):.3e}"
        )


# ===========================================================================
# 6 — |R| increases monotonically with perturbation amplitude
# ===========================================================================

class TestRicciScalesWithPerturbation:
    """|R| grows as the metric perturbation grows (monotone in noise).

    For a fixed random perturbation pattern h (shape N×4×4), scaling it by
    ε₁ < ε₂ must give |R(ε₁)| < |R(ε₂)|.  This verifies that the
    curvature pipeline is sensitive to the perturbation amplitude.
    """

    def test_ricci_increases_with_noise_amplitude(self):
        rng = np.random.default_rng(42)
        h_raw = rng.standard_normal((_N, 4, 4))
        h = 0.5 * (h_raw + h_raw.transpose(0, 2, 1))   # symmetrise
        phi = np.ones(_N)

        amps = [1e-6, 1e-4, 1e-2]
        R_maxes = []
        for amp in amps:
            g = _G_FLAT + amp * h
            _, _, _, R = compute_curvature(g, _B_ZERO, phi, _DX)
            R_maxes.append(float(np.max(np.abs(R))))

        for i in range(len(amps) - 1):
            assert R_maxes[i] < R_maxes[i + 1], (
                f"Expected R_max({amps[i]}) < R_max({amps[i+1]}); "
                f"got {R_maxes[i]:.3e} vs {R_maxes[i+1]:.3e}"
            )


# ===========================================================================
# 7 — α is independent of B (depends only on φ)
# ===========================================================================

class TestAlphaIndependentOfB:
    """The nonminimal coupling α = ⟨1/φ²⟩ does not depend on B.

    α is computed as the spatial average of 1/φ², so it is determined
    entirely by the radion field φ.  Changing B (which enters only through
    the off-diagonal KK block G_{μ5}) must not alter α.
    """

    def test_alpha_same_for_zero_and_nonzero_B(self):
        phi = np.full(_N, 1.5)
        rng = np.random.default_rng(99)
        B_large = 0.5 * rng.standard_normal((_N, 4))

        alpha_zero, _ = extract_alpha_from_curvature(
            _G_FLAT, _B_ZERO, phi, _DX
        )
        alpha_nonzero, _ = extract_alpha_from_curvature(
            _G_FLAT, B_large, phi, _DX
        )
        assert abs(alpha_zero - alpha_nonzero) < 1e-10, (
            f"α changed with B: α(B=0)={alpha_zero:.12f}, "
            f"α(B≠0)={alpha_nonzero:.12f}"
        )


# ===========================================================================
# 8 — V''(φ₀_eff) > 0 (radion is not tachyonic at the KK fixed point)
# ===========================================================================

class TestRadionStabilityPositive:
    """V''(φ₀_eff) > 0: the GW potential stabilises the radion.

    The Goldberger–Wise potential V(φ) = λ(φ² − φ₀²)² has its minimum at
    φ = φ₀_eff with V = V' = 0 and V'' = 8λφ₀² > 0.  A positive second
    derivative means the radion is a massive, stable excitation (not
    tachyonic), which is required for the compact dimension to remain stable.
    α = 1/φ₀_eff² > 0 is separately verified to confirm the coupling is
    finite and derived.
    """

    def test_Vpp_positive_at_phi0_eff(self):
        phi0_eff = effective_phi0_kk(1.0, 5)          # ≈ 31.42
        _, Vp, Vpp = gw_potential_derivs(phi0_eff, lam=1.0, phi0=phi0_eff)
        assert abs(Vp) < 1e-8, (
            f"V'(φ₀_eff) should be 0 at the minimum; got {Vp:.3e}"
        )
        assert Vpp > 0.0, (
            f"V''(φ₀_eff) = {Vpp:.3e} ≤ 0: radion is tachyonic"
        )

    def test_alpha_positive_at_phi0_eff(self):
        phi0_eff = effective_phi0_kk(1.0, 5)
        alpha = 1.0 / phi0_eff ** 2
        assert alpha > 0.0
        assert np.isfinite(alpha)
