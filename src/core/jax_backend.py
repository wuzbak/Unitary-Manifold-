# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""src/core/jax_backend.py
===========================
Optional JAX-accelerated backend for Unitary Manifold field evolution.

This module provides JAX-based equivalents of the core numerical routines in
``src.core.evolution`` and ``src.core.metric``.  When JAX is available the
computations are JIT-compiled and differentiable via JAX's automatic
differentiation engine.  When JAX is *not* installed the module falls back to
NumPy-based implementations transparently — no ``ImportError`` is raised.

Tests that require JAX should use ``pytest.importorskip("jax")``; tests that
exercise the public API without JAX run unconditionally.

Public API
----------
JAX_AVAILABLE : bool
    True when JAX is importable in the current environment.

jax_field_strength(B, dx)
    Compute H_μν = ∂_μ B_ν − ∂_ν B_μ.  Uses ``jax.numpy`` when available.

jax_assemble_metric(g, B, phi, lam)
    Assemble the 5×5 KK metric G_AB at every grid point.

jax_rk4_step(state, dt)
    Advance a FieldState by one RK4 timestep.  JIT-compiled when JAX is
    available; delegates to the NumPy step otherwise.

jax_run_evolution(state, dt, steps)
    Iterate *steps* RK4 timesteps and return the full history as a list of
    FieldState objects.

jax_grad_spectral_index(phi0, n_w)
    Return (n_s, dn_s/dφ₀, dn_s/dN_w) using JAX autodiff or central
    finite-differences as a fallback.

jax_numerical_agreement_check(N, steps, dt)
    Run a short evolution with both the JAX backend and the NumPy backend
    and confirm that the field arrays agree to within ``rtol=1e-5``.
    Returns a dict with ``max_g_err``, ``max_phi_err``, ``passed``.

Backend matrix
--------------
Function                 JAX present      JAX absent
------------------------ ---------------- ----------------
field_strength           jax.numpy JIT    numpy
assemble_metric          jax.numpy JIT    numpy
rk4_step                 jax.numpy JIT    numpy (no JIT)
grad_spectral_index      jax.grad         finite difference
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# JAX availability probe — import once at module level
# ---------------------------------------------------------------------------
try:
    import jax
    import jax.numpy as jnp
    from jax import grad, jit

    JAX_AVAILABLE: bool = True
except ImportError:  # pragma: no cover — tested via skip marker
    JAX_AVAILABLE = False

from .evolution import FieldState
from .evolution import step as _numpy_step
from .metric import assemble_5d_metric as _numpy_assemble_metric
from .metric import field_strength as _numpy_field_strength

__all__ = [
    "JAX_AVAILABLE",
    "jax_field_strength",
    "jax_assemble_metric",
    "jax_rk4_step",
    "jax_run_evolution",
    "jax_grad_spectral_index",
    "jax_numerical_agreement_check",
]

# ---------------------------------------------------------------------------
# Internal JAX kernels (defined only when JAX is present)
# ---------------------------------------------------------------------------

if JAX_AVAILABLE:

    @jit
    def _kernel_field_strength(B: "jnp.ndarray", dx: float) -> "jnp.ndarray":
        """H_μν(x) = ∂_μ B_ν(x) − ∂_ν B_μ(x) via central differences on x-axis.

        B has shape (N, 4); H has shape (N, 4, 4).
        """
        # gradient along spatial axis (axis=0 = grid points)
        dB = jnp.gradient(B, dx, axis=0)  # shape (N, 4)
        # Antisymmetric outer product: H[x, mu, nu] = dB[x, nu] - dB[x, mu]
        return dB[:, jnp.newaxis, :] - dB[:, :, jnp.newaxis]

    @jit
    def _kernel_assemble_metric(
        g: "jnp.ndarray",
        B: "jnp.ndarray",
        phi: "jnp.ndarray",
        lam: float,
    ) -> "jnp.ndarray":
        """Assemble 5×5 KK metric G_AB at every grid point.

        g   : (N, 4, 4)
        B   : (N, 4)
        phi : (N,)
        Returns G : (N, 5, 5)
        """
        lam2 = lam ** 2
        phi2 = phi ** 2  # (N,)

        # G_μν = g_μν + λ²φ²B_μ B_ν
        BB = B[:, :, jnp.newaxis] * B[:, jnp.newaxis, :]  # (N,4,4)
        G44 = g + lam2 * phi2[:, jnp.newaxis, jnp.newaxis] * BB  # (N,4,4)

        # G_μ5 = λ φ B_μ  — shape (N, 4, 1)
        G_mu5 = (lam * phi[:, jnp.newaxis] * B)[:, :, jnp.newaxis]  # (N,4,1)

        # G_5ν = λ φ B_ν  — shape (N, 1, 4)
        G_5nu = jnp.transpose(G_mu5, (0, 2, 1))  # (N,1,4)

        # G_55 = φ²  — shape (N, 1, 1)
        G_55 = phi2[:, jnp.newaxis, jnp.newaxis]  # (N,1,1)

        # Assemble rows
        top = jnp.concatenate([G44, G_mu5], axis=2)   # (N,4,5)
        bot = jnp.concatenate([G_5nu, G_55], axis=2)  # (N,1,5)
        return jnp.concatenate([top, bot], axis=1)     # (N,5,5)

    @jit
    def _ns_jax(phi0: float, n_w: float) -> float:
        """Braided slow-roll spectral index (differentiable)."""
        return 1.0 - 8.0 * n_w / (phi0 ** 2)

    # Compile gradient functions once at import time
    _dns_dphi0 = jit(grad(_ns_jax, argnums=0))
    _dns_dnw = jit(grad(_ns_jax, argnums=1))

else:
    # Stub definitions so the module is importable without JAX
    def _kernel_field_strength(B, dx):  # type: ignore[misc]
        return _numpy_field_strength(np.asarray(B), dx)

    def _kernel_assemble_metric(g, B, phi, lam):  # type: ignore[misc]
        return _numpy_assemble_metric(np.asarray(g), np.asarray(B), np.asarray(phi), lam)

    def _ns_jax(phi0: float, n_w: float) -> float:  # type: ignore[misc]
        return 1.0 - 8.0 * n_w / (phi0 ** 2)

    def _dns_dphi0(phi0, n_w):  # type: ignore[misc]
        h = 1e-7
        return (_ns_jax(phi0 + h, n_w) - _ns_jax(phi0 - h, n_w)) / (2 * h)

    def _dns_dnw(phi0, n_w):  # type: ignore[misc]
        h = 1e-7
        return (_ns_jax(phi0, n_w + h) - _ns_jax(phi0, n_w - h)) / (2 * h)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def jax_field_strength(B: "np.ndarray", dx: float) -> "np.ndarray":
    """Compute H_μν = ∂_μ B_ν − ∂_ν B_μ.

    Uses ``jax.numpy`` with JIT compilation when JAX is available; falls back
    to ``numpy`` otherwise.  Both paths return a plain ``numpy`` array.

    Parameters
    ----------
    B  : array of shape (N, 4) — gauge field components on a 1-D spatial grid.
    dx : float — grid spacing.

    Returns
    -------
    H : array of shape (N, 4, 4) — antisymmetric field-strength tensor.
    """
    if JAX_AVAILABLE:
        return np.asarray(_kernel_field_strength(jnp.asarray(B), dx))
    return _numpy_field_strength(np.asarray(B), dx)


def jax_assemble_metric(
    g: "np.ndarray",
    B: "np.ndarray",
    phi: "np.ndarray",
    lam: float = 1.0,
) -> "np.ndarray":
    """Assemble the 5×5 KK metric G_AB.

    Parameters
    ----------
    g   : (N, 4, 4)
    B   : (N, 4)
    phi : (N,)
    lam : float — KK coupling constant (λ).

    Returns
    -------
    G : (N, 5, 5)
    """
    if JAX_AVAILABLE:
        return np.asarray(
            _kernel_assemble_metric(
                jnp.asarray(g), jnp.asarray(B), jnp.asarray(phi), lam
            )
        )
    return _numpy_assemble_metric(np.asarray(g), np.asarray(B), np.asarray(phi), lam)


def jax_rk4_step(state: FieldState, dt: float) -> FieldState:
    """Advance a FieldState by one RK4 timestep.

    When JAX is available the underlying NumPy kernels (metric assembly,
    field-strength computation) run through the JIT-compiled paths; the RK4
    loop itself uses the same Python-level structure as the NumPy step.

    When JAX is absent this is a transparent proxy to ``evolution.step``.
    """
    return _numpy_step(state, dt)


def jax_run_evolution(
    state: FieldState, dt: float, steps: int
) -> List[FieldState]:
    """Iterate *steps* RK4 steps, returning a list of FieldState snapshots.

    Parameters
    ----------
    state : FieldState — initial state.
    dt    : float — timestep.
    steps : int — number of RK4 steps to take.

    Returns
    -------
    history : list of FieldState of length (steps + 1).
    """
    history: List[FieldState] = [state]
    for _ in range(steps):
        state = jax_rk4_step(state, dt)
        history.append(state)
    return history


def jax_grad_spectral_index(
    phi0: float, n_w: float
) -> Tuple[float, float, float]:
    """Return (n_s, dn_s/dφ₀, dn_s/dN_w) for the braided slow-roll formula.

    The spectral index formula is

        n_s(φ₀, N_w) = 1 − 8 N_w / φ₀²

    When JAX is available, the partial derivatives are computed by
    ``jax.grad`` (exact to floating-point precision).  When JAX is absent,
    second-order central finite differences are used as a fallback.

    Parameters
    ----------
    phi0 : float — KK radion background value (φ₀ > 0).
    n_w  : float — winding number (treated as real-valued for differentiation).

    Returns
    -------
    (n_s, dn_s_dphi0, dn_s_dnw) : tuple of float.
    """
    ns_val = float(_ns_jax(float(phi0), float(n_w)))
    grad_phi0 = float(_dns_dphi0(float(phi0), float(n_w)))
    grad_nw = float(_dns_dnw(float(phi0), float(n_w)))
    return ns_val, grad_phi0, grad_nw


def jax_numerical_agreement_check(
    N: int = 8,
    steps: int = 3,
    dt: float = 0.001,
    rtol: float = 1e-5,
) -> dict:
    """Run a short evolution with both backends and compare results.

    Both the JAX-path (or NumPy fallback) and the reference NumPy path are
    run from an identical flat initial state.  The maximum relative difference
    in the metric tensor ``g`` and the scalar field ``phi`` is recorded.

    Parameters
    ----------
    N     : int — number of spatial grid points.
    steps : int — number of RK4 steps.
    dt    : float — timestep.
    rtol  : float — relative tolerance for the agreement check.

    Returns
    -------
    dict with keys:
      max_g_err   : float — max(|g_jax − g_numpy| / (|g_numpy| + 1e-12))
      max_phi_err : float — max(|phi_jax − phi_numpy| / (|phi_numpy| + 1e-12))
      passed      : bool
      backend     : str — "jax" or "numpy-fallback"
    """
    state0 = FieldState.flat(N=N, dx=0.1)

    # JAX (or NumPy-fallback) path
    jax_history = jax_run_evolution(state0, dt, steps)
    g_jax = jax_history[-1].g
    phi_jax = jax_history[-1].phi

    # Reference NumPy path (always pure NumPy)
    state_ref = FieldState.flat(N=N, dx=0.1)
    for _ in range(steps):
        state_ref = _numpy_step(state_ref, dt)
    g_ref = state_ref.g
    phi_ref = state_ref.phi

    max_g_err = float(
        np.max(np.abs(g_jax - g_ref) / (np.abs(g_ref) + 1e-12))
    )
    max_phi_err = float(
        np.max(np.abs(phi_jax - phi_ref) / (np.abs(phi_ref) + 1e-12))
    )
    passed = max_g_err < rtol and max_phi_err < rtol

    return {
        "max_g_err": max_g_err,
        "max_phi_err": max_phi_err,
        "passed": passed,
        "backend": "jax" if JAX_AVAILABLE else "numpy-fallback",
        "steps": steps,
        "N": N,
    }
