# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_fuzzing.py
=====================
Adversarial fuzzing tests (342 → 362).

For each of several (seed, noise_amplitude) pairs a randomly perturbed
near-Minkowski state is constructed and the full pipeline is run.  The
five physical invariants that must hold across ALL random perturbations are:

  1. α = ⟨1/φ²⟩ is finite and positive            (no hidden singularity)
  2. det(g) < 0 after step()                        (Lorentzian volume preserved)
  3. Eigenvalue signature (−,+,+,+) after evolution (signature cannot flip)
  4. R_max bounded after several steps              (no integrator runaway)
  5. |J_x| ≤ |J_t| everywhere                      (information causality)

Each test class is parametrized over four (seed, noise_amp) pairs so that
different random patterns and different perturbation magnitudes are tested.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pytest

from src.core.metric import extract_alpha_from_curvature, compute_curvature
from src.core.evolution import (
    FieldState,
    step,
    information_current,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ETA = np.diag([-1.0, 1.0, 1.0, 1.0])
_N   = 8
_DX  = 0.1
_DT  = 0.001   # CFL-safe for N≤24, dx=0.1

# Noise-amplitude parameters: (seed, noise_amp).
# "alpha" and "causality" tests can handle larger noise (no sustained
# evolution required); "evolution" tests are capped at 2e-3 for stability.
_ALPHA_PARAMS = [(0, 1e-4), (7, 1e-3), (13, 1e-2), (42, 5e-2)]
_EVOL_PARAMS  = [(0, 1e-4), (7, 5e-4), (13, 1e-3), (42, 2e-3)]


def _make_fuzz_state(seed: int, noise_amp: float,
                     N: int = _N, dx: float = _DX) -> FieldState:
    """Near-Minkowski FieldState with reproducible random perturbations."""
    rng = np.random.default_rng(seed)
    g_raw = np.tile(_ETA, (N, 1, 1)) + noise_amp * rng.standard_normal((N, 4, 4))
    g = 0.5 * (g_raw + g_raw.transpose(0, 2, 1))   # symmetrise
    B   = noise_amp * rng.standard_normal((N, 4))
    phi = np.ones(N) + noise_amp * rng.standard_normal(N)
    phi = np.maximum(phi, 0.1)                       # prevent φ → 0 in fuzz
    return FieldState(g=g, B=B, phi=phi, dx=dx)


# ===========================================================================
# 1 — α = ⟨1/φ²⟩ is finite and positive
# ===========================================================================

class TestFuzzAlphaFinitePositive:
    """Adversarial α extraction: finite and positive under random inputs.

    Tests that no combination of random near-Minkowski metric, random B
    field, or random radion perturbation drives α to zero, infinity, or NaN.
    Covers noise amplitudes from 1e-4 to 5e-2.
    """

    @pytest.mark.parametrize("seed,noise_amp", _ALPHA_PARAMS)
    def test_alpha_finite_positive(self, seed, noise_amp):
        state = _make_fuzz_state(seed, noise_amp)
        alpha, _ = extract_alpha_from_curvature(
            state.g, state.B, state.phi, state.dx
        )
        assert np.isfinite(alpha), (
            f"seed={seed}, noise={noise_amp}: α={alpha} is not finite"
        )
        assert alpha > 0.0, (
            f"seed={seed}, noise={noise_amp}: α={alpha} ≤ 0"
        )


# ===========================================================================
# 2 — det(g) < 0 after evolution
# ===========================================================================

class TestFuzzDeterminantSign:
    """det(g) < 0 at every grid point after 5 RK4 steps.

    _project_metric_volume normalises det(g) → −1, so every Lorentzian
    grid point must have det < 0 after each call to step().
    """

    @pytest.mark.parametrize("seed,noise_amp", _EVOL_PARAMS)
    def test_det_negative_after_step(self, seed, noise_amp):
        state = _make_fuzz_state(seed, noise_amp)
        for _ in range(5):
            state = step(state, dt=_DT)
        dets = np.linalg.det(state.g)
        assert np.all(dets < 0.0), (
            f"seed={seed}, noise={noise_amp}: "
            f"positive det(g) found: max={dets.max():.3e}"
        )


# ===========================================================================
# 3 — Lorentzian signature (−,+,+,+) preserved through evolution
# ===========================================================================

class TestFuzzLorentzianSignature:
    """Signature (−,+,+,+) never flips during evolution.

    At each grid point the metric must have exactly one negative and three
    positive real eigenvalues after 5 RK4 steps.  A sign flip would
    indicate that the timelike direction has become spacelike, which is
    unphysical.
    """

    @pytest.mark.parametrize("seed,noise_amp", _EVOL_PARAMS)
    def test_lorentzian_signature(self, seed, noise_amp):
        state = _make_fuzz_state(seed, noise_amp)
        for _ in range(5):
            state = step(state, dt=_DT)
        for n in range(state.g.shape[0]):
            evals = np.linalg.eigvalsh(state.g[n])
            n_neg = int(np.sum(evals < 0))
            assert n_neg == 1, (
                f"seed={seed}, noise={noise_amp}, point {n}: "
                f"expected 1 negative eigenvalue, got {n_neg}; "
                f"evals={evals}"
            )


# ===========================================================================
# 4 — Ricci scalar bounded after evolution
# ===========================================================================

class TestFuzzRicciBounded:
    """R_max < 1e4 after 5 RK4 steps on randomly perturbed near-flat space.

    Tests that the integrator does not produce runaway curvature.  The
    conservative bound of 1e4 is well above the typical O(1) curvature
    produced by 1e-3 noise on a dx=0.1 grid but far below the numerical
    overflow regime.
    """

    @pytest.mark.parametrize("seed,noise_amp", _EVOL_PARAMS)
    def test_ricci_bounded_after_steps(self, seed, noise_amp):
        state = _make_fuzz_state(seed, noise_amp)
        for _ in range(5):
            state = step(state, dt=_DT)
        _, _, _, R = compute_curvature(
            state.g, state.B, state.phi, state.dx
        )
        R_max = float(np.max(np.abs(R)))
        assert R_max < 1e4, (
            f"seed={seed}, noise={noise_amp}: R_max={R_max:.3e} ≥ 1e4"
        )


# ===========================================================================
# 5 — Information causality: |J_x| ≤ |J_t|
# ===========================================================================

class TestFuzzInformationCausality:
    """Spatial information current never exceeds temporal component.

    In the definition of information_current():
        J_t = ρ / √|g_00|        (ρ = φ²)
        J_x = ρ (∂_x φ) / (‖∂φ‖ · √|g_00|)

    Because ‖∂φ‖ = √((∂_x φ)² + ε) ≥ |∂_x φ|, we always have
    |J_x| ≤ J_t.  This must hold for any random initial φ and g.
    Covers noise amplitudes from 1e-4 to 5e-2 (no evolution needed).
    """

    @pytest.mark.parametrize("seed,noise_amp", _ALPHA_PARAMS)
    def test_information_causality(self, seed, noise_amp):
        state = _make_fuzz_state(seed, noise_amp)
        J = information_current(state.g, state.phi, state.dx)
        # |J_x| ≤ J_t at every grid point (with a small floating-point margin)
        assert np.all(np.abs(J[:, 1]) <= np.abs(J[:, 0]) + 1e-12), (
            f"seed={seed}, noise={noise_amp}: causality violated; "
            f"max excess = {(np.abs(J[:,1]) - np.abs(J[:,0])).max():.3e}"
        )
