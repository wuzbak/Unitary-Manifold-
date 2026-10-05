# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/jax_evolution.py
=========================
JAX-accelerated field evolution for the Unitary Manifold.

Provides a JAX RK4 integrator matching the two zero-mode flow laws in
``src/core/evolution.py``, with a JIT-compiled action-derived RHS for CPU/GPU
acceleration. Active KK-tower backreaction is rejected as unsupported.

Key speedups vs. the numpy evolution pipeline:

  1. **JIT compilation** — the action-derived RHS is traced once per array
     shape and compiled; the RK4 orchestration and validation remain in Python.
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
* In the legacy law the scalar Laplacian is periodic, but geometric first
  derivatives and gauge divergence use one-sided endpoints. Both laws use
  x at coordinate index 1.
* The default action-derived relaxation uses periodic central derivatives,
  Lorentzian contractions and the Einstein-frame metric, matching NumPy.
  Its parameter t is not physical coordinate time.
* The legacy phenomenological law is explicitly selectable. Only that law
  projects det g = −1 by default. Active KK-tower sources are unsupported
  and rejected rather than silently discarded.
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
    _jax_field_strength_impl,
    _grad_np_compat,
)
from .evolution import DEFAULT_FLOW_LAW, FLOW_LAW_ACTION_DERIVED, FLOW_LAW_LEGACY, FLOW_LAWS


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
    flow_law: str = DEFAULT_FLOW_LAW
    n_kk_modes: int = 0
    kk_backreaction_coupling: float = 0.0

    def __post_init__(self) -> None:
        if self.flow_law not in FLOW_LAWS:
            raise ValueError(f"flow_law must be one of {FLOW_LAWS}, got {self.flow_law!r}")

    @classmethod
    def flat(cls, N: int = 64, dx: float = 0.1,
             lam: float = 1.0, alpha: float = 0.1,
             phi0: float = 1.0, m_phi: float = 0.0,
             rng: Optional[np.random.Generator] = None,
             flow_law: str = DEFAULT_FLOW_LAW,
             n_kk_modes: int = 0,
             kk_backreaction_coupling: float = 0.0) -> "JaxFieldState":
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
            flow_law=flow_law, n_kk_modes=n_kk_modes,
            kk_backreaction_coupling=kk_backreaction_coupling,
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
        flow_law=jax_state.flow_law,
        n_kk_modes=jax_state.n_kk_modes,
        kk_backreaction_coupling=jax_state.kk_backreaction_coupling,
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
        flow_law=np_state.flow_law,
        n_kk_modes=np_state.n_kk_modes,
        kk_backreaction_coupling=np_state.kk_backreaction_coupling,
    )


# ---------------------------------------------------------------------------
# Internal JAX RHS helpers
# ---------------------------------------------------------------------------

def _jax_laplacian(f, dx):
    """JAX Laplacian: (f_{n+1} − 2f_n + f_{n-1}) / dx²."""
    return (jnp.roll(f, -1, axis=0) - 2.0 * f + jnp.roll(f, 1, axis=0)) / dx ** 2


def _jax_divergence_x(V, dx):
    """Spatial divergence ∂_x V^1 with the canonical one-sided endpoints."""
    return _grad_np_compat(V[:, 1], dx)


def _jax_stress_energy(B, phi, H, lam):
    """Approximate stress-energy T_μν sourced by B and φ (JAX version)."""
    H2 = jnp.einsum('nij,nij->n', H, H)             # (N,)
    HH = jnp.einsum('nir,njr->nij', H, H)           # (N, 4, 4)
    eye4 = jnp.eye(4)
    T = lam ** 2 * (HH - 0.25 * H2[:, None, None] * eye4[None, :, :])
    return T


def _jax_source_scalar(H):
    """Phenomenological source: half the Euclidean component norm of H."""
    return 0.5 * jnp.einsum('nij,nij->n', H, H)


def _jax_periodic_grad(f, dx):
    """Second-order periodic derivative used by the action-derived law."""
    return (jnp.roll(f, -1, axis=0) - jnp.roll(f, 1, axis=0)) / (2.0 * dx)


def _jax_action_derived_rhs(g, B, phi, dx, lam, phi0, m_phi):
    """Mirror action_derived_rhs, including its Einstein-to-Jordan chain rule."""
    gE = phi[:, None, None] * g
    gi = jnp.linalg.inv(gE)
    sqrt_g = jnp.sqrt(jnp.abs(jnp.linalg.det(gE)))
    psi = jnp.log(phi)
    dpsi = jnp.zeros_like(B).at[:, 1].set(_jax_periodic_grad(psi, dx))

    dgE = jnp.zeros((g.shape[0], 4, 4, 4), dtype=g.dtype)
    dgE = dgE.at[:, 1].set(_jax_periodic_grad(gE, dx))
    combo = dgE + dgE.transpose(0, 2, 1, 3) - dgE.transpose(0, 2, 3, 1)
    Gam = 0.5 * jnp.einsum('nsr,nmvr->nsmv', gi, combo)
    dGam = _jax_periodic_grad(Gam, dx)
    term2 = jnp.zeros_like(gE).at[:, 1, :].set(jnp.einsum('nrrs->ns', dGam))
    ric_vs = (
        dGam[:, 1] - term2
        + jnp.einsum('nl,nlvs->nvs', jnp.einsum('nrrl->nl', Gam), Gam)
        - jnp.einsum('nrvl,nlrs->nvs', Gam, Gam)
    )
    ric = 0.5 * (ric_vs + ric_vs.transpose(0, 2, 1))

    dB_dx = _jax_periodic_grad(B, dx)
    F = jnp.zeros_like(gE).at[:, 1, :].set(dB_dx)
    F = F.at[:, :, 1].add(-dB_dx)
    F_up = jnp.einsum('nai,nbj,nij->nab', gi, gi, F)
    F2 = jnp.einsum('nij,nij->n', F, F_up)
    FF = jnp.einsum('nma,nab,nvb->nmv', F, gi, F)
    w = lam ** 2 * phi ** 3
    U = 0.5 * m_phi ** 2 * (phi - phi0) ** 2 / phi
    dU_dpsi = m_phi ** 2 * (phi - phi0) - U
    E_metric = (
        ric - 1.5 * jnp.einsum('nm,nv->nmv', dpsi, dpsi)
        - 0.5 * w[:, None, None] * (FF - 0.25 * gE * F2[:, None, None])
        - 0.5 * U[:, None, None] * gE
    )
    E_gauge_up = _jax_periodic_grad(
        sqrt_g[:, None] * w[:, None] * F_up[:, 1, :], dx
    ) / sqrt_g[:, None]
    box_psi = _jax_periodic_grad(
        sqrt_g * jnp.einsum('nm,nm->n', gi[:, 1, :], dpsi), dx
    ) / sqrt_g
    dpsi_dt = (3.0 * box_psi - 0.75 * w * F2 - dU_dpsi) / 3.0
    dg = -2.0 * E_metric / phi[:, None, None] - g * dpsi_dt[:, None, None]
    return (0.5 * (dg + dg.transpose(0, 2, 1)),
            jnp.einsum('nvr,nr->nv', gE, E_gauge_up),
            phi * dpsi_dt)


if JAX_AVAILABLE:
    _jax_action_derived_rhs = jax.jit(_jax_action_derived_rhs)


def _jax_compute_rhs(g, B, phi, dx, lam, alpha, phi0, m_phi,
                     flow_law=DEFAULT_FLOW_LAW, n_kk_modes=0,
                     kk_backreaction_coupling=0.0):
    """Compute field equation RHS — fully vectorised JAX version.

    Returns (dg, dB, dphi) with the same shapes as (g, B, phi).
    """
    if flow_law not in FLOW_LAWS:
        raise ValueError(f"flow_law must be one of {FLOW_LAWS}, got {flow_law!r}")
    if n_kk_modes > 0 and kk_backreaction_coupling > 0.0:
        if flow_law == FLOW_LAW_ACTION_DERIVED:
            raise ValueError("KK-tower backreaction is not a term of the reduced action.")
        raise NotImplementedError("The JAX backend does not support active KK-tower backreaction.")
    if flow_law == FLOW_LAW_ACTION_DERIVED:
        if np.any(np.asarray(phi) <= 0.0):
            raise ValueError("action-derived equations require φ > 0 everywhere (G_55 = φ²).")
        return _jax_action_derived_rhs(g, B, phi, dx, lam, phi0, m_phi)

    # 5D curvature pipeline
    G5     = _jax_assemble_5d_metric_impl(g, B, phi, lam)
    Gamma5 = _jax_christoffel_impl(G5, dx, 5)
    Riem5  = _jax_riemann_from_christoffel(Gamma5, dx)

    # 5D Ricci → 4D projection
    Ricci5 = jnp.einsum('ncacb -> nab', Riem5)
    Ricci  = Ricci5[:, :4, :4]                       # (N, 4, 4)
    g_inv  = jnp.linalg.inv(g)
    R      = jnp.einsum('nij,nij->n', g_inv, Ricci)  # (N,)

    H = _jax_field_strength_impl(B, dx)

    # ∂_t g_μν = −2 R_μν + T_μν
    T  = _jax_stress_energy(B, phi, H, lam)
    dg = -2.0 * Ricci + T
    dg = 0.5 * (dg + dg.transpose(0, 2, 1))

    # ∂_t B_μ = ∂_ν (λ² H^νμ)
    H_up = jnp.einsum('nai,nbj,nij->nab', g_inv, g_inv, H)    # (N, 4, 4)
    # Spatial divergence: ∂_x H^1μ, with np.gradient-compatible endpoints.
    dB = _grad_np_compat(lam ** 2 * H_up, dx)[:, 1, :]  # x is coordinate 1

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

def jax_step(state: JaxFieldState, dt: float,
             project_metric_volume: Optional[bool] = None) -> JaxFieldState:
    """Advance *state* by one JAX RK4 timestep.

    Uses the classical fourth-order Runge–Kutta method with a metric
    volume-preservation projection applied by default only for the legacy law. All
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
    rhs_params = (dx, lam, alpha, phi0, m_phi, state.flow_law,
                  state.n_kk_modes, state.kk_backreaction_coupling)

    k1g, k1B, k1phi = _jax_compute_rhs(g, B, phi, *rhs_params)

    g2, B2, phi2 = _jax_advance(g, B, phi, k1g, k1B, k1phi, half)
    k2g, k2B, k2phi = _jax_compute_rhs(g2, B2, phi2, *rhs_params)

    g3, B3, phi3 = _jax_advance(g, B, phi, k2g, k2B, k2phi, half)
    k3g, k3B, k3phi = _jax_compute_rhs(g3, B3, phi3, *rhs_params)

    g4, B4, phi4 = _jax_advance(g, B, phi, k3g, k3B, k3phi, dt)
    k4g, k4B, k4phi = _jax_compute_rhs(g4, B4, phi4, *rhs_params)

    dg   = (k1g   + 2.0 * k2g   + 2.0 * k3g   + k4g)   / 6.0
    dB   = (k1B   + 2.0 * k2B   + 2.0 * k3B   + k4B)   / 6.0
    dphi = (k1phi + 2.0 * k2phi + 2.0 * k3phi + k4phi) / 6.0

    g_new   = g + dt * dg
    g_new   = 0.5 * (g_new + g_new.transpose(0, 2, 1))
    if project_metric_volume is None:
        project_metric_volume = state.flow_law == FLOW_LAW_LEGACY
    if project_metric_volume:
        g_new = _jax_project_metric_volume(g_new)
    B_new   = B + dt * dB
    phi_new = phi + dt * dphi

    g_np   = np.asarray(g_new)
    B_np   = np.asarray(B_new)
    phi_np = np.asarray(phi_new)
    if (not np.all(np.isfinite(g_np)) or
            not np.all(np.isfinite(B_np)) or
            not np.all(np.isfinite(phi_np))):
        raise RuntimeError(
            "CFL violation detected mid-integration: fields are NaN/Inf after "
            f"JAX RK4 step at t={t0:.6g} + dt={dt:.6g}.  "
            f"CFL-stable dt_max ≈ {0.4 * state.dx ** 2:.4g} for dx={state.dx:.4g}. "
            "Reduce dt or increase grid spacing dx."
        )

    return JaxFieldState(
        g=g_new, B=B_new, phi=phi_new,
        t=t0 + dt, dx=dx, lam=lam, alpha=alpha, phi0=phi0, m_phi=m_phi,
        flow_law=state.flow_law, n_kk_modes=state.n_kk_modes,
        kk_backreaction_coupling=state.kk_backreaction_coupling,
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

    dg, dB, dphi = _jax_compute_rhs(
        g, B, phi, dx, lam, alpha, phi0, m_phi, state.flow_law,
        state.n_kk_modes, state.kk_backreaction_coupling,
    )
    g_new = g + dt * dg
    g_new = 0.5 * (g_new + g_new.transpose(0, 2, 1))
    if state.flow_law == FLOW_LAW_LEGACY:
        g_new = _jax_project_metric_volume(g_new)

    return JaxFieldState(
        g=g_new, B=B + dt * dB, phi=phi + dt * dphi,
        t=state.t + dt, dx=dx, lam=lam, alpha=alpha, phi0=phi0, m_phi=m_phi,
        flow_law=state.flow_law, n_kk_modes=state.n_kk_modes,
        kk_backreaction_coupling=state.kk_backreaction_coupling,
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
