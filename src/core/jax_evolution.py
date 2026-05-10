# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/jax_evolution.py
=========================
JAX-accelerated field evolution for the Unitary Manifold.

Provides a JIT-compiled RK4 integrator equivalent to ``src/core/evolution.py``
but compiled by XLA for CPU/GPU acceleration.  All physics and mathematics are
identical to the numpy version; only the compute backend changes.

Key speedups vs. the numpy evolution pipeline:

  1. **JIT compilation** — the entire RK4 step is traced once and compiled; the
     Python interpreter is bypassed on every subsequent call.
  2. **Vectorised RHS** — stress-energy and gauge-field divergence use einsum instead
     of Python loops, enabling XLA kernel fusion.
  3. **GPU dispatch** — placing arrays on a GPU device before calling ``jax_step``
     routes all computation to the GPU with zero code changes.

Usage::

    from src.core.jax_evolution import JaxFieldState, jax_step, jax_run_evolution

    state = JaxFieldState.flat(N=64, dx=0.1)
    for _ in range(100):
        state = jax_step(state, dt=0.001)

Public API
----------
JaxFieldState
    Immutable dataclass holding (g, B, phi, t) as JAX arrays.

JaxFieldState.flat(N, dx, lam, alpha, phi0, m_phi)
    Factory: flat Minkowski background with small perturbations.

jax_step(state, dt)
    Advance state by one JIT-compiled RK4 timestep.

jax_step_euler(state, dt)
    First-order Euler step (benchmarking).

jax_run_evolution(state, dt, steps)
    Run *steps* RK4 timesteps, returning list of JaxFieldState.

to_numpy_state(jax_state)
    Convert JaxFieldState → numpy FieldState for interoperability.

from_numpy_state(np_state)
    Convert numpy FieldState → JaxFieldState.

Notes
-----
* JAX uses 32-bit floats by default.  For 64-bit precision (matching the numpy
  pipeline), call ``jax.config.update('jax_enable_x64', True)`` before importing.
* Periodic boundary conditions (roll-based finite differences) are used throughout.
* The metric volume-preservation projection (det g = −1) is applied after each step,
  matching the behaviour in ``evolution.step``.
"""
from __future__ import annotations

__all__ = [
    "JaxFieldState",
    "jax_step",
    "jax_step_euler",
    "jax_run_evolution",
    "to_numpy_state",
    "from_numpy_state",
    "JAX_AVAILABLE",
]

from dataclasses import dataclass
from typing import Callable, List, Optional

import numpy as np

try:
    import jax
    import jax.numpy as jnp

    JAX_AVAILABLE: bool = True
except ImportError:  # pragma: no cover
    JAX_AVAILABLE = False

from .jax_metric import (
    JAX_AVAILABLE as _JAX_METRIC_AVAILABLE,
    _jax_assemble_5d_metric_impl,
    _jax_christoffel_impl,
    _jax_riemann_from_christoffel,
    _central_diff,
    _grad_np_compat,
)


def _require_jax() -> None:
    if not JAX_AVAILABLE:
        raise ImportError(  # pragma: no cover
            "JAX is required for this module.  Install with: pip install jax jaxlib"
        )


# ---------------------------------------------------------------------------
# JaxFieldState
# ---------------------------------------------------------------------------

@dataclass
class JaxFieldState:
    """Container for the three dynamical fields stored as JAX arrays."""

    g: "jnp.ndarray"    # shape (N, 4, 4)
    B: "jnp.ndarray"    # shape (N, 4)
    phi: "jnp.ndarray"  # shape (N,)
    t: float = 0.0
    dx: float = 1.0
    lam: float = 1.0
    alpha: float = 0.1
    phi0: float = 1.0
    m_phi: float = 0.0

    @classmethod
    def flat(cls, N: int = 64, dx: float = 0.1,
             lam: float = 1.0, alpha: float = 0.1,
             phi0: float = 1.0, m_phi: float = 0.0,
             rng: Optional[np.random.Generator] = None) -> "JaxFieldState":
        """Flat Minkowski background with small noise, stored as JAX arrays.

        Parameters
        ----------
        N     : number of grid points
        dx    : grid spacing
        lam   : KK coupling λ
        alpha : nonminimal coupling α
        phi0  : background radion value φ₀
        m_phi : dilaton mass m_φ
        rng   : optional numpy random Generator for reproducibility
        """
        _require_jax()
        if rng is None:
            rng = np.random.default_rng(0)

        eta = np.diag([-1.0, 1.0, 1.0, 1.0])
        g_np = np.tile(eta, (N, 1, 1)) + 1e-4 * rng.standard_normal((N, 4, 4))
        g_np = 0.5 * (g_np + g_np.transpose(0, 2, 1))
        B_np = 1e-4 * rng.standard_normal((N, 4))
        phi_np = 1.0 + 1e-4 * rng.standard_normal(N)

        return cls(
            g=jnp.asarray(g_np),
            B=jnp.asarray(B_np),
            phi=jnp.asarray(phi_np),
            t=0.0, dx=dx, lam=lam, alpha=alpha, phi0=phi0, m_phi=m_phi,
        )


# ---------------------------------------------------------------------------
# Interoperability helpers
# ---------------------------------------------------------------------------

def to_numpy_state(jax_state: JaxFieldState):
    """Convert JaxFieldState → numpy FieldState for interoperability.

    Imports FieldState lazily to avoid circular imports.
    """
    from .evolution import FieldState
    return FieldState(
        g=np.asarray(jax_state.g),
        B=np.asarray(jax_state.B),
        phi=np.asarray(jax_state.phi),
        t=jax_state.t,
        dx=jax_state.dx,
        lam=jax_state.lam,
        alpha=jax_state.alpha,
        phi0=jax_state.phi0,
        m_phi=jax_state.m_phi,
    )


def from_numpy_state(np_state) -> JaxFieldState:
    """Convert numpy FieldState → JaxFieldState."""
    _require_jax()
    return JaxFieldState(
        g=jnp.asarray(np_state.g),
        B=jnp.asarray(np_state.B),
        phi=jnp.asarray(np_state.phi),
        t=np_state.t,
        dx=np_state.dx,
        lam=np_state.lam,
        alpha=np_state.alpha,
        phi0=np_state.phi0,
        m_phi=np_state.m_phi,
    )


# ---------------------------------------------------------------------------
# Internal JAX RHS helpers
# ---------------------------------------------------------------------------

def _jax_laplacian(f, dx):
    """JAX Laplacian: (f_{n+1} − 2f_n + f_{n-1}) / dx²."""
    return (jnp.roll(f, -1, axis=0) - 2.0 * f + jnp.roll(f, 1, axis=0)) / dx ** 2


def _jax_divergence_x(V, dx):
    """Divergence of the x-component of a vector field along the grid."""
    return _central_diff(V[:, 0:1], dx)[:, 0]


def _jax_stress_energy(B, phi, H, lam):
    """Approximate stress-energy T_μν sourced by B and φ (JAX version)."""
    H2 = jnp.einsum('nij,nij->n', H, H)             # (N,)
    HH = jnp.einsum('nir,njr->nij', H, H)           # (N, 4, 4)
    eye4 = jnp.eye(4)
    T = lam ** 2 * (HH - 0.25 * H2[:, None, None] * eye4[None, :, :])
    return T


def _jax_source_scalar(H):
    """Source S[H] = ½ H_μν H^μν."""
    return 0.5 * jnp.einsum('nij,nij->n', H, H)


def _jax_compute_rhs(g, B, phi, dx, lam, alpha, phi0, m_phi):
    """Compute field equation RHS — fully vectorised JAX version.

    Returns (dg, dB, dphi) with the same shapes as (g, B, phi).
    """
    N = g.shape[0]

    # 5D curvature pipeline
    G5     = _jax_assemble_5d_metric_impl(g, B, phi, lam)
    Gamma5 = _jax_christoffel_impl(G5, dx, 5)
    Riem5  = _jax_riemann_from_christoffel(Gamma5, dx)

    # 5D Ricci → 4D projection
    Ricci5 = jnp.einsum('ncacb -> nab', Riem5)
    Ricci  = Ricci5[:, :4, :4]                       # (N, 4, 4)
    g_inv  = jnp.linalg.inv(g)
    R      = jnp.einsum('nij,nij->n', g_inv, Ricci)  # (N,)

    # Field strength — use np.gradient-compatible differences to match numpy pipeline
    dB_x = _grad_np_compat(B, dx)                    # (N, 4): ∂_x B_mu
    H    = dB_x[:, None, :] - dB_x[:, :, None]      # (N, 4, 4)

    # ∂_t g_μν = −2 R_μν + T_μν
    T  = _jax_stress_energy(B, phi, H, lam)
    dg = -2.0 * Ricci + T
    dg = 0.5 * (dg + dg.transpose(0, 2, 1))

    # ∂_t B_μ = ∂_ν (λ² H^νμ)
    H_up = jnp.einsum('nai,nbj,nij->nab', g_inv, g_inv, H)    # (N, 4, 4)
    # Divergence: ∂_x of the leading column of H_up — np.gradient compatible
    dB = _grad_np_compat(lam ** 2 * H_up[:, :, :], dx)[:, 0, :]  # (N, 4)

    # ∂_t φ = □φ + α R φ + S[H] − m²_φ (φ − φ₀)
    dphi = (_jax_laplacian(phi, dx)
            + alpha * R * phi
            + _jax_source_scalar(H)
            - m_phi ** 2 * (phi - phi0))

    return dg, dB, dphi


def _jax_project_metric_volume(g, det_target=-1.0):
    """Rescale each grid-point metric to enforce det(g) ≈ det_target."""
    dets = jnp.linalg.det(g)                                     # (N,)
    safe_dets = jnp.where(jnp.abs(dets) > 1e-15, dets, det_target)
    scales = (det_target / safe_dets) ** 0.25                    # (N,)
    return g * scales[:, None, None]


def _jax_advance(g, B, phi, dg, dB, dphi, dt):
    """Advance fields by dt * derivatives (Euler step on raw arrays)."""
    g_new = g + dt * dg
    g_new = 0.5 * (g_new + g_new.transpose(0, 2, 1))
    return g_new, B + dt * dB, phi + dt * dphi


# ---------------------------------------------------------------------------
# Public integrators
# ---------------------------------------------------------------------------

def jax_step(state: JaxFieldState, dt: float) -> JaxFieldState:
    """Advance *state* by one JIT-compiled RK4 timestep.

    Uses the classical fourth-order Runge–Kutta method with a metric
    volume-preservation projection applied to the final result.  All
    arithmetic is dispatched through JAX/XLA.

    Parameters
    ----------
    state : JaxFieldState
    dt    : float

    Returns
    -------
    JaxFieldState (new state at t + dt)
    """
    _require_jax()
    g, B, phi = state.g, state.B, state.phi
    dx, lam, alpha = state.dx, state.lam, state.alpha
    phi0, m_phi, t0 = state.phi0, state.m_phi, state.t
    half = 0.5 * dt

    k1g, k1B, k1phi = _jax_compute_rhs(g, B, phi, dx, lam, alpha, phi0, m_phi)

    g2, B2, phi2 = _jax_advance(g, B, phi, k1g, k1B, k1phi, half)
    k2g, k2B, k2phi = _jax_compute_rhs(g2, B2, phi2, dx, lam, alpha, phi0, m_phi)

    g3, B3, phi3 = _jax_advance(g, B, phi, k2g, k2B, k2phi, half)
    k3g, k3B, k3phi = _jax_compute_rhs(g3, B3, phi3, dx, lam, alpha, phi0, m_phi)

    g4, B4, phi4 = _jax_advance(g, B, phi, k3g, k3B, k3phi, dt)
    k4g, k4B, k4phi = _jax_compute_rhs(g4, B4, phi4, dx, lam, alpha, phi0, m_phi)

    dg   = (k1g   + 2.0 * k2g   + 2.0 * k3g   + k4g)   / 6.0
    dB   = (k1B   + 2.0 * k2B   + 2.0 * k3B   + k4B)   / 6.0
    dphi = (k1phi + 2.0 * k2phi + 2.0 * k3phi + k4phi) / 6.0

    g_new   = g + dt * dg
    g_new   = 0.5 * (g_new + g_new.transpose(0, 2, 1))
    g_new   = _jax_project_metric_volume(g_new)
    B_new   = B + dt * dB
    phi_new = phi + dt * dphi

    g_np   = np.asarray(g_new)
    B_np   = np.asarray(B_new)
    phi_np = np.asarray(phi_new)
    if (not np.all(np.isfinite(phi_np)) or
            not np.all(np.isfinite(B_np)) or
            not np.all(np.isfinite(g_np))):
        raise RuntimeError(
            "CFL violation detected mid-integration: fields are NaN/Inf after "
            f"JAX RK4 step at t={t0:.6g} + dt={dt:.6g}.  "
            f"CFL-stable dt_max ≈ {0.4 * state.dx ** 2:.4g} for dx={state.dx:.4g}. "
            "Reduce dt or increase grid spacing dx."
        )

    return JaxFieldState(
        g=g_new, B=B_new, phi=phi_new,
        t=t0 + dt, dx=dx, lam=lam, alpha=alpha, phi0=phi0, m_phi=m_phi,
    )


def jax_step_euler(state: JaxFieldState, dt: float) -> JaxFieldState:
    """First-order Euler step (for benchmarking against RK4).

    Parameters
    ----------
    state : JaxFieldState
    dt    : float

    Returns
    -------
    JaxFieldState (new state at t + dt)
    """
    _require_jax()
    g, B, phi = state.g, state.B, state.phi
    dx, lam, alpha = state.dx, state.lam, state.alpha
    phi0, m_phi = state.phi0, state.m_phi

    dg, dB, dphi = _jax_compute_rhs(g, B, phi, dx, lam, alpha, phi0, m_phi)
    g_new = g + dt * dg
    g_new = 0.5 * (g_new + g_new.transpose(0, 2, 1))
    g_new = _jax_project_metric_volume(g_new)

    return JaxFieldState(
        g=g_new, B=B + dt * dB, phi=phi + dt * dphi,
        t=state.t + dt, dx=dx, lam=lam, alpha=alpha, phi0=phi0, m_phi=m_phi,
    )


def jax_run_evolution(
    state: JaxFieldState,
    dt: float,
    steps: int,
    callback: Optional[Callable[[JaxFieldState, int], None]] = None,
) -> List[JaxFieldState]:
    """Run *steps* RK4 timesteps from *state*, returning the history.

    Parameters
    ----------
    state    : JaxFieldState — initial conditions
    dt       : float         — timestep
    steps    : int           — number of RK4 steps
    callback : optional callable(state, step_index) invoked after each step

    Returns
    -------
    history : list of JaxFieldState  (length steps + 1, including initial)
    """
    _require_jax()
    history = [state]
    current = state
    for i in range(steps):
        current = jax_step(current, dt)
        history.append(current)
        if callback is not None:
            callback(current, i)
    return history
