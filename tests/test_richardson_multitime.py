# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_richardson_multitime.py
====================================
Parametric Richardson convergence + over-diffusion diagnostic.
All tests in this module are marked ``@pytest.mark.slow`` and are
**skipped by default** (see ``pytest.ini``).

Run the fast suite (default):
    pytest -m "not slow"

Run only this file:
    pytest -m slow tests/test_richardson_multitime.py

Run everything:
    pytest -m ""

-----------------------------------------------------------------------
Design (pseudocode specification)
-----------------------------------------------------------------------
    DOMAIN  = 1.6
    grids   = [8, 16, 32]      dx(N) = DOMAIN / N
    T0      = 0.1              dt(N) = CFL * dx²   (CFL = 0.1)
    times   = [T0, 2·T0, 4·T0]
    A_sine  = 0.1              phi₀ = 1 + A·sin(2π x / DOMAIN)

    FOR each N, FOR each T:
        run simulation; stop early if metric_degenerate
        alpha[N][T] = mean(1/phi²)

    FOR each T:
        p_est = log2(|α₈−α₁₆| / |α₁₆−α₃₂|)

Pass conditions
---------------
    ASSERT no instability for any (N, T)
    ASSERT p_est > 0 at every T           (Richardson convergence holds)
    ASSERT p_est ≈ 2 at T = T₀           (second-order central differences)
    ASSERT |α₈−α₁₆| > |α₁₆−α₃₂| at T   (finer grid ⇒ smaller error)
    ASSERT α₈ < α₁₆ at every T           (over-diffusion flag: coarse-grid bias)

Over-diffusion diagnostic
-------------------------
    The N=8 grid (dx = 0.2) has a coarser finite-difference Laplacian than
    N=16 (dx=0.1) or N=32 (dx=0.05).  The additional truncation error in the
    Laplacian causes α(N=8) to deviate below α(N=16) at all observed times.
    Richardson convergence (p > 0) confirms this is a pure grid-spacing
    artefact: the bias vanishes as dx → 0.

Estimated wall-clock time
-------------------------
    ~115 s on a single core (cumulative RK4 steps: N=8→99, N=16→399,
    N=32→1599 at CFL=0.1).  Marked ``slow`` so the normal CI suite
    is not affected (see ``pytest.ini``).
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pytest

from src.core.evolution import FieldState, step as rk4_step

# ---------------------------------------------------------------------------
# Module-level constant
# ---------------------------------------------------------------------------

_ETA = np.diag([-1.0, 1.0, 1.0, 1.0])


# ---------------------------------------------------------------------------
# Helper: run one grid, record alpha at each checkpoint time
# ---------------------------------------------------------------------------

def _run_grid(N: int, *,
              domain: float, cfl: float, a_sine: float,
              t0: float, mults: list[int]) -> tuple[dict, dict]:
    """
    Evolve FieldState for N grid points up to max(mults)*t0, recording
    alpha = mean(1/phi²) at each checkpoint t0*mult.

    Returns
    -------
    alphas   : {mult -> float | None}   None if simulation became unstable
    unstable : {mult -> bool}
    """
    dx  = domain / N
    dt  = cfl * dx**2
    x   = np.arange(N) * dx
    phi = 1.0 + a_sine * np.sin(2.0 * np.pi * x / domain)

    state = FieldState(
        g   = np.tile(_ETA, (N, 1, 1)),
        B   = np.zeros((N, 4)),
        phi = phi,
        dx  = dx,
    )

    alphas:   dict[int, float | None] = {}
    unstable: dict[int, bool]         = {}

    cur_step    = 0
    is_unstable = False

    for mult in sorted(mults):
        n_target = int(mult * t0 / dt)

        if not is_unstable:
            while cur_step < n_target:
                state = rk4_step(state, dt)
                cur_step += 1
                if not (np.all(np.isfinite(state.phi)) and
                        np.all(np.isfinite(state.g))):
                    is_unstable = True
                    break

        unstable[mult] = is_unstable
        alphas[mult]   = (
            None if is_unstable
            else float(np.mean(1.0 / state.phi**2))
        )

    return alphas, unstable


# ===========================================================================
# Parametric Richardson convergence test class
# ===========================================================================

@pytest.mark.slow
class TestRichardsonConvergenceParametric:
    """Richardson convergence + over-diffusion diagnostic (SLOW).

    All data are computed once via a class-scoped fixture and reused across
    the individual assertion methods to avoid repeating the ~115 s simulation.
    """

    # -------------------------------------------------------------------
    # Simulation parameters (match the pseudocode specification exactly)
    # -------------------------------------------------------------------
    _DOMAIN = 1.6
    _GRIDS  = [8, 16, 32]
    _T0     = 0.1
    _MULTS  = [1, 2, 4]
    _CFL    = 0.1
    _A_SINE = 0.1

    # -------------------------------------------------------------------
    # Class-scoped fixture: run all (N, T) simulations once
    # -------------------------------------------------------------------

    @pytest.fixture(scope="class", autouse=True)
    def _precompute(self, request):
        """Populate cls._alphas, cls._unstable, cls._p_ests."""
        cls = request.cls

        all_alphas:   dict[tuple[int, int], float | None] = {}
        all_unstable: dict[tuple[int, int], bool]         = {}

        for N in cls._GRIDS:
            grid_alphas, grid_unstable = _run_grid(
                N,
                domain  = cls._DOMAIN,
                cfl     = cls._CFL,
                a_sine  = cls._A_SINE,
                t0      = cls._T0,
                mults   = cls._MULTS,
            )
            for mult in cls._MULTS:
                all_alphas[(N, mult)]   = grid_alphas[mult]
                all_unstable[(N, mult)] = grid_unstable[mult]

        # Compute Richardson convergence order for each time point
        p_ests: dict[int, float] = {}
        for mult in cls._MULTS:
            a8  = all_alphas.get((8,  mult))
            a16 = all_alphas.get((16, mult))
            a32 = all_alphas.get((32, mult))
            if None in (a8, a16, a32):
                p_ests[mult] = float("nan")
                continue
            d1 = abs(a8  - a16)
            d2 = abs(a16 - a32)
            p_ests[mult] = (
                float(np.log2(d1 / d2))
                if d1 > 1e-13 and d2 > 1e-13
                else float("nan")
            )

        cls._alphas   = all_alphas
        cls._unstable = all_unstable
        cls._p_ests   = p_ests

    # -------------------------------------------------------------------
    # 1. Stability: no (N, T) combination goes unstable
    # -------------------------------------------------------------------

    def test_no_instability_detected(self):
        """Every (N, T) combination stays numerically stable (no NaN/Inf).

        All three grids use CFL = 0.1, a conservative sub-CFL timestep, so
        no grid should develop a singular or non-finite state at any of the
        three checkpoint times.
        """
        for N in self._GRIDS:
            for mult in self._MULTS:
                assert not self._unstable[(N, mult)], (
                    f"Instability detected: N={N}, T={mult}×T₀={mult*self._T0:.2f}"
                )

    # -------------------------------------------------------------------
    # 2. Richardson convergence: d_coarse > d_fine at each T
    # -------------------------------------------------------------------

    @pytest.mark.parametrize("mult", [1, 2, 4])
    def test_richardson_convergence(self, mult):
        """|α(N=8)−α(N=16)| > |α(N=16)−α(N=32)| at T = mult × T₀.

        The finite-difference truncation error is O(dx²).  Doubling N (halving
        dx) should reduce the error by ~4×, so the coarse-grid error must be
        larger than the medium-grid error.
        """
        a8, a16, a32 = (self._alphas.get((N, mult)) for N in [8, 16, 32])
        if None in (a8, a16, a32):
            pytest.skip(f"Unstable at T={mult}×T₀")

        d_coarse = abs(a8  - a16)
        d_fine   = abs(a16 - a32)

        assert d_coarse > d_fine, (
            f"T={mult}×T₀={mult*self._T0:.2f}: "
            f"d_coarse={d_coarse:.3e} ≯ d_fine={d_fine:.3e}\n"
            f"  α(N=8)={a8:.8f}  α(N=16)={a16:.8f}  α(N=32)={a32:.8f}"
        )

    # -------------------------------------------------------------------
    # 3. Positive convergence order at each T
    # -------------------------------------------------------------------

    @pytest.mark.parametrize("mult", [1, 2, 4])
    def test_p_est_positive(self, mult):
        """p_est = log₂(d_coarse / d_fine) > 0 at T = mult × T₀.

        A positive p_est confirms that errors decrease with grid refinement
        (Richardson convergence), regardless of the exact convergence rate.
        """
        p = self._p_ests.get(mult, float("nan"))
        assert np.isfinite(p), (
            f"T={mult}×T₀: p_est is not finite (simulation may be unstable)"
        )
        assert p > 0.0, (
            f"T={mult}×T₀: p_est={p:.3f} ≤ 0 — errors are NOT decreasing "
            "with refinement (Richardson convergence violated)"
        )

    # -------------------------------------------------------------------
    # 4. p_est ≈ 2 at T = T₀  (second-order accuracy check)
    # -------------------------------------------------------------------

    def test_p_est_near_second_order_at_T0(self):
        """p_est ≈ 2 at T=T₀: consistent with second-order central differences.

        At early times the dominant error is the leading O(dx²) truncation
        error of the centred-difference Laplacian.  The Richardson estimator
        should therefore return p ≈ 2.  A tolerance of [1.0, 4.0] is used
        to allow for higher-order contributions at these grid sizes.
        """
        p = self._p_ests.get(1, float("nan"))
        assert np.isfinite(p), "p_est is not finite at T=T₀"
        assert 1.0 <= p <= 4.0, (
            f"p_est={p:.3f} at T=T₀ is outside [1.0, 4.0]; "
            "expected ≈ 2 for second-order finite differences"
        )

    # -------------------------------------------------------------------
    # 5. Over-diffusion flag: α₈ < α₁₆ at every T
    # -------------------------------------------------------------------

    @pytest.mark.parametrize("mult", [1, 2, 4])
    def test_over_diffusion_flagged_at_coarse_grid(self, mult):
        """α(N=8) < α(N=16) at T = mult × T₀: coarse-grid diffusion bias.

        The centred-difference Laplacian on the N=8 grid (dx = 0.2) is less
        accurate than on N=16 (dx = 0.1).  The resulting truncation error
        causes the coarse-grid α to systematically fall below the
        medium-grid α at all observed times — the over-diffusion signature.

        Richardson convergence (test_richardson_convergence) confirms this
        is a purely numerical artefact that vanishes as dx → 0, *not* a
        physical effect.
        """
        a8  = self._alphas.get((8,  mult))
        a16 = self._alphas.get((16, mult))
        if None in (a8, a16):
            pytest.skip(f"Unstable at T={mult}×T₀")

        assert a8 < a16, (
            f"T={mult}×T₀={mult*self._T0:.2f}: "
            f"α(N=8)={a8:.8f} ≥ α(N=16)={a16:.8f}; "
            "over-diffusion flag NOT triggered at coarse grid"
        )
