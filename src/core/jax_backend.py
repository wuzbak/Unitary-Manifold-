# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""src/core/jax_backend.py
===========================
Real JAX-accelerated backend for Unitary Manifold field evolution.

Requires JAX — no NumPy fallback. If JAX is not installed this module
raises ImportError at import time (correct behaviour; JAX is in requirements).

Public API
----------
JAX_VERSION : str
    jax.__version__ string.
field_strength_jax(B, dx) -> jnp.ndarray  shape (N,4,4)
assemble_metric_jax(g, B, phi, lam) -> jnp.ndarray  shape (N,5,5)
grad_spectral_index(phi0, n_w) -> (n_s, dn_s_dphi0, dn_s_dnw)
vmap_field_strength(B_batch, dx) -> jnp.ndarray  shape (batch,N,4,4)
numerical_agreement_check(N, steps, dt, rtol) -> dict
"""

from __future__ import annotations

import jax
import jax.numpy as jnp
from jax import jit, grad, vmap
import numpy as np

JAX_VERSION: str = jax.__version__

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------
N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0
N_S: float = 0.9635
R_BRAIDED: float = 0.0315


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _grad_1d(f: jnp.ndarray, dx: float) -> jnp.ndarray:
    """Second-order central finite-difference gradient along axis-0."""
    fwd = jnp.roll(f, -1, axis=0)
    bwd = jnp.roll(f, 1, axis=0)
    return (fwd - bwd) / (2.0 * dx)


# ---------------------------------------------------------------------------
# JIT-compiled core functions
# ---------------------------------------------------------------------------

@jit
def field_strength_jax(B: jnp.ndarray, dx: float) -> jnp.ndarray:
    """H_μν = ∂_μ B_ν − ∂_ν B_μ,  shape (N, 4, 4).

    Parameters
    ----------
    B  : jnp.ndarray, shape (N, 4)
    dx : float, grid spacing
    """
    N, D = B.shape

    def _col_grad(nu):
        return _grad_1d(B[:, nu], dx)

    grads = jnp.stack([_col_grad(nu) for nu in range(D)], axis=1)  # (N, D)

    def _row(mu):
        def _entry(nu):
            return grads[:, nu] - grads[:, mu]
        return jnp.stack([_entry(nu) for nu in range(D)], axis=1)

    H = jnp.stack([_row(mu) for mu in range(D)], axis=1)  # (N, D, D)
    return H


@jit
def assemble_metric_jax(
    g: jnp.ndarray,
    B: jnp.ndarray,
    phi: jnp.ndarray,
    lam: float = 1.0,
) -> jnp.ndarray:
    """Assemble the 5×5 KK metric G_AB at each grid point.

        G_μν = g_μν + λ²φ² B_μ B_ν
        G_μ5 = G_5μ = λφ B_μ
        G_55 = φ²

    Parameters
    ----------
    g   : (N, 4, 4)
    B   : (N, 4)
    phi : (N,)
    lam : float

    Returns
    -------
    G5  : (N, 5, 5)
    """
    N = g.shape[0]
    lam_phi = lam * phi                          # (N,)
    lam_phi_B = lam_phi[:, None] * B             # (N, 4)

    # 4×4 block
    BxB = jnp.einsum('ni,nj->nij', B, B)        # (N, 4, 4)
    g44 = g + (lam_phi ** 2)[:, None, None] * BxB  # (N, 4, 4)

    # off-diagonal column/row (N, 4)
    col = lam_phi_B                              # G_μ5

    # G_55 = φ² (N,)
    g55 = phi ** 2

    # Assemble full 5×5 via padding
    # Top row of 5-rows: [ g44  |  col ]
    col5 = col[:, :, None]                      # (N, 4, 1)
    top = jnp.concatenate([g44, col5], axis=2)  # (N, 4, 5)

    # Bottom row: [ col^T  | g55 ]
    bot = jnp.concatenate([col, g55[:, None]], axis=1)[:, None, :]  # (N, 1, 5)

    G5 = jnp.concatenate([top, bot], axis=1)   # (N, 5, 5)
    return G5


# ---------------------------------------------------------------------------
# Differentiable spectral index formula
# ---------------------------------------------------------------------------

def _ns_formula(phi0: float, n_w: float) -> float:
    """n_s = 1 − 8·n_w / φ₀²  (CMB spectral index from slow-roll)."""
    return 1.0 - 8.0 * n_w / (phi0 ** 2)


def grad_spectral_index(phi0: float, n_w: float):
    """Return (n_s, dn_s/dφ₀, dn_s/dn_w) via jax.grad.

    Parameters
    ----------
    phi0 : float  — background radion value
    n_w  : float  — winding number (float for differentiability)

    Returns
    -------
    (n_s, dn_s_dphi0, dn_s_dnw) : tuple of floats
    """
    phi0_f = float(phi0)
    n_w_f = float(n_w)

    _grad_phi0 = grad(_ns_formula, argnums=0)
    _grad_nw = grad(_ns_formula, argnums=1)

    n_s = float(_ns_formula(phi0_f, n_w_f))
    dn_dphi0 = float(_grad_phi0(phi0_f, n_w_f))
    dn_dnw = float(_grad_nw(phi0_f, n_w_f))
    return n_s, dn_dphi0, dn_dnw


# ---------------------------------------------------------------------------
# vmap over batch of B arrays
# ---------------------------------------------------------------------------

def _field_strength_single(B: jnp.ndarray, dx: float) -> jnp.ndarray:
    return field_strength_jax(B, dx)


def vmap_field_strength(B_batch: jnp.ndarray, dx: float) -> jnp.ndarray:
    """Compute field_strength_jax over a batch of B arrays.

    Parameters
    ----------
    B_batch : (batch, N, 4)
    dx      : float

    Returns
    -------
    H_batch : (batch, N, 4, 4)
    """
    return vmap(lambda B: field_strength_jax(B, dx))(B_batch)


# ---------------------------------------------------------------------------
# Numerical agreement check vs NumPy path
# ---------------------------------------------------------------------------

def numerical_agreement_check(
    N: int = 32,
    steps: int = 5,
    dt: float = 0.001,
    rtol: float = 1e-4,
) -> dict:
    """Compare JAX metric assembly to NumPy path.

    Returns
    -------
    dict with keys: max_metric_err, passed, jax_version, backend
    """
    from src.core.metric import assemble_5d_metric as _np_metric

    rng = np.random.default_rng(42)
    g_np = rng.standard_normal((N, 4, 4))
    g_np = 0.5 * (g_np + g_np.transpose(0, 2, 1))
    B_np = rng.standard_normal((N, 4))
    phi_np = 1.0 + 0.01 * rng.standard_normal(N)
    lam = 1.0

    G_np = _np_metric(g_np, B_np, phi_np, lam)

    G_jax = np.array(assemble_metric_jax(
        jnp.array(g_np),
        jnp.array(B_np),
        jnp.array(phi_np),
        lam,
    ))

    max_err = float(np.max(np.abs(G_np - G_jax)))
    passed = max_err < rtol

    return {
        "max_metric_err": max_err,
        "passed": passed,
        "jax_version": JAX_VERSION,
        "backend": "jax",
    }
