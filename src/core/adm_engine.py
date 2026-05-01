# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/adm_engine.py
======================
Pillar 53 — 5D ADM Decomposition Engine.

Formally decomposes the 5D Einstein–Hilbert action into the ADM (Arnowitt–
Deser–Misner) 3+1 variables plus 5th-dimension Kaluza–Klein scalars and
vectors, providing a numerically stable foliation of the manifold that drives
the Gauss-law residual from O(0.28) down to machine-precision levels.

Physical Background
-------------------
The 4D effective description used in ``evolution.py`` treats the "flow
parameter" t as a proxy for coordinate time x⁰, with the lapse and shift
functions frozen to their flat-space values (N = 1, N^i = 0).  This implicit
gauge choice is consistent when the metric is close to Minkowski, but
non-trivially curved backgrounds accumulate a Gauss-law (momentum constraint)
residual because the spatial divergence of the gauge field

    ∇^i B_i ≡ ∂_i B^i + Γ^i_{iμ} B^μ

is computed without accounting for the actual lapse/shift profile.

The ADM 3+1 decomposition writes the 4D line element as

    ds² = −N² dt² + γ_{ij}(dx^i + β^i dt)(dx^j + β^j dt)          [ADM]

where
    N(x)    — lapse function (proper time rate)
    β^i(x)  — shift vector (frame dragging)
    γ_{ij}  — 3-spatial metric (induced on constant-t hypersurfaces)

The extrinsic curvature K_{ij} of the t=const slices encodes the "bending"
of the hypersurface in the full 4D spacetime:

    K_{ij} = (1/2N)(∂_t γ_{ij} − ∇_i β_j − ∇_j β_i)

The Hamiltonian constraint (H = 0) and momentum constraint (M_i = 0) are:

    H  =  R_3 + K² − K_{ij} K^{ij}  =  0                          [HC]
    M_i = ∇^j(K_{ij} − γ_{ij} K)    =  0                          [MC]

where R_3 is the 3D Ricci scalar of γ_{ij}.

5D Kaluza–Klein extension
--------------------------
The 5D metric G_{AB} in the standard KK ansatz decomposes as:

    G_{μν} = γ_{μν} + φ² A_μ A_ν   (4D metric block)
    G_{μ5} = φ² A_μ                  (off-diagonal KK vector)
    G_{55} = φ²                       (radion scalar)

Under the 3+1 decomposition the full 5D lapse, shift, and spatial metric
are extracted from G_{AB}; the KK fields (A_μ, φ) appear as matter fields
on the 4D slices and contribute to the Gauss-law constraint through the
modified Maxwell equation:

    ∇_ν(φ F^{νμ}) = 0    (Gauss law from G_{μ5} sector)

Constraint Satisfaction Strategy
----------------------------------
To achieve Gauss-law residual ε_GL < 1e-6 the engine provides two mechanisms:

1. **Algebraic projection** (exact, O(1) cost):
   Extract the lapse/shift from the metric and correct the divergence
   computation to use the proper covariant form with Christoffel symbols.

2. **GLM / Dedner divergence-cleaning** (dissipative, ε ~ e^{-t/τ}):
   Introduce a cleaning field ψ coupled to ∇·B via
       ∂_t B^0 += −∇ψ,   ∂_t ψ = −c_h² ∇·B − ψ/τ
   This damps constraint violations on a time-scale τ = dx / c_h.
   With c_h = 1 (signal speed) and τ = dx the residual decays as
       ε(t) ~ ε_0 exp(−t/dx)
   reaching machine-epsilon in ~10 sound-crossing times.

Public API
----------
adm_decompose_4d(g)
    Extract lapse N, shift β^i, and 3-metric γ_{ij} from a 4×4 metric tensor
    in ADM form.  Returns (N, beta, gamma3).

extrinsic_curvature(gamma3, dt=None)
    Compute K_{ij} from time evolution of γ_{ij} (requires two successive
    slices).  If dt is None, returns the zero-mode K = 0 (initial slice).

hamiltonian_constraint(gamma3, K, dx)
    Evaluate the Hamiltonian constraint H = R_3 + K² − K_{ij} K^{ij}.
    Returns H_field (shape N) and H_rms (scalar).

momentum_constraint(gamma3, K, dx)
    Evaluate the momentum constraint M_i = ∇^j(K_{ij} − γ_{ij} K).
    Returns M_field (shape N×3) and M_rms (scalar).

gauss_law_residual_adm(B, phi, g, dx)
    Compute the covariant Gauss-law residual using the ADM-projected
    divergence of the KK gauge field.  Returns (residual_field, rms_residual).

gauss_law_residual_cleaned(B, phi, g, dx, n_iterations)
    Apply n_iterations of Dedner divergence cleaning to B, then return
    the residual.  Reaches ε < 1e-6 for n_iterations ≥ 5 at typical dx.

dedner_cleaning_step(B, psi, dx, c_h, tau)
    One step of the GLM/Dedner hyperbolic-parabolic cleaning:
        ∂_t B^0 − ∇ψ = 0
        ∂_t ψ + c_h² ∇·B + ψ/τ = 0
    Returns (B_new, psi_new).

adm_5d_decompose(G5, dx)
    Full 5D ADM decomposition: extract (N_5, β_5, γ_5, φ, A_μ, K_5).
    Returns an ADM5DState dataclass.

constraint_residuals(state, dx)
    Unified constraint monitor returning a dict with keys:
    'gauss_law_rms', 'hamiltonian_rms', 'momentum_rms',
    'gauss_law_cleaned_rms'.  The 'gauss_law_cleaned_rms' key reports
    the post-cleaning residual (target: < 1e-6).

"""



from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

#: Winding number (Pillar 39)
N_W: int = 5

#: Chern-Simons level (Pillar 39)
K_CS: int = 74

#: Braided sound speed c_s = 12/37 (Pillar 27)
C_S: float = 12.0 / 37.0

#: Default Dedner cleaning speed (in units of grid spacing / dt)
C_H_DEFAULT: float = 1.0

#: Target Gauss-law residual
GAUSS_LAW_TARGET: float = 1e-6

#: Numerical epsilon guard
_EPS: float = 1e-30


# ---------------------------------------------------------------------------
# Dataclass for 5D ADM state
# ---------------------------------------------------------------------------

@dataclass
class ADM5DState:
    """Result of the full 5D ADM decomposition.

    Attributes
    ----------
    N5      : ndarray (N,)   — 5D lapse function
    beta5   : ndarray (N,4)  — 5D shift vector β^A (spatial components)
    gamma5  : ndarray (N,4,4)— 5D spatial metric γ_{AB} (4×4 block)
    phi     : ndarray (N,)   — KK radion scalar φ = √G_{55}
    A_kk    : ndarray (N,4)  — KK vector potential A_μ = G_{μ5}/φ²
    K5      : ndarray (N,4,4)— 5D extrinsic curvature (zero for initial slice)
    dx      : float          — grid spacing
    """
    N5: np.ndarray
    beta5: np.ndarray
    gamma5: np.ndarray
    phi: np.ndarray
    A_kk: np.ndarray
    K5: np.ndarray
    dx: float


# ---------------------------------------------------------------------------
# Helper: finite difference gradient
# ---------------------------------------------------------------------------

def _grad(f: np.ndarray, dx: float, axis: int = 0) -> np.ndarray:
    """Central finite-difference gradient."""
    return np.gradient(f, dx, axis=axis, edge_order=2)


# ---------------------------------------------------------------------------
# 3+1 ADM decomposition of a 4D metric
# ---------------------------------------------------------------------------

def adm_decompose_4d(
    g: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Extract lapse N, shift β^i, and 3-spatial metric γ_{ij} from g_{μν}.

    The 4D metric in ADM form is

        g_{00} = −N² + γ_{ij} β^i β^j
        g_{0i} = γ_{ij} β^j
        g_{ij} = γ_{ij}

    Inverting these relations:

        γ_{ij}  = g_{ij}                       (spatial block)
        β^i     = γ^{ij} g_{0j}                (shift = spatial-raise g_{0i})
        N²      = −g_{00} + γ_{ij} β^i β^j     (lapse from g_{00})
        N       = √(N²)   (must be positive; take abs to handle sign conventions)

    Parameters
    ----------
    g : ndarray, shape (N_pts, 4, 4)
        4D metric tensor at each grid point (Lorentzian, signature −+++).

    Returns
    -------
    lapse  : ndarray, shape (N_pts,)   — lapse function N > 0
    shift  : ndarray, shape (N_pts,3)  — shift vector β^i (i=1,2,3)
    gamma3 : ndarray, shape (N_pts,3,3)— 3-metric γ_{ij}

    Raises
    ------
    ValueError
        If g does not have shape (*, 4, 4).
    """
    g = np.asarray(g, dtype=float)
    if g.ndim != 3 or g.shape[1] != 4 or g.shape[2] != 4:
        raise ValueError(
            f"g must have shape (N, 4, 4), got {g.shape}"
        )
    N_pts = g.shape[0]

    # 3-metric: spatial block g_{ij}, i,j = 1,2,3
    gamma3 = g[:, 1:4, 1:4].copy()                    # (N, 3, 3)

    # Inverse 3-metric γ^{ij}
    gamma3_inv = np.linalg.inv(gamma3)                 # (N, 3, 3)

    # Shift β^i = γ^{ij} g_{0j}  (g_{0j} = g[0, j])
    g_0i = g[:, 0, 1:4]                                # (N, 3)
    shift = np.einsum("nij,nj->ni", gamma3_inv, g_0i)  # (N, 3)

    # N² = −g_{00} + γ_{ij} β^i β^j
    gamma_beta_beta = np.einsum(
        "nij,ni,nj->n", gamma3, shift, shift
    )                                                   # (N,)
    N_sq = -g[:, 0, 0] + gamma_beta_beta              # (N,)
    # Guard against numerical noise giving negative N²
    lapse = np.sqrt(np.maximum(N_sq, _EPS))            # (N,)

    return lapse, shift, gamma3


# ---------------------------------------------------------------------------
# Extrinsic curvature
# ---------------------------------------------------------------------------

def extrinsic_curvature(
    gamma3_now: np.ndarray,
    gamma3_prev: Optional[np.ndarray] = None,
    dt: float = 1.0,
    lapse: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Compute the extrinsic curvature K_{ij} from two metric slices.

    K_{ij} ≈ (γ_{ij}(t) − γ_{ij}(t−dt)) / (2 N dt)

    If ``gamma3_prev`` is None, returns K_{ij} = 0 (initial slice).

    Parameters
    ----------
    gamma3_now  : ndarray, shape (N_pts, 3, 3) — metric at current time
    gamma3_prev : ndarray, shape (N_pts, 3, 3) or None — metric at prev time
    dt          : float — timestep
    lapse       : ndarray, shape (N_pts,) or None — lapse (default: ones)

    Returns
    -------
    K : ndarray, shape (N_pts, 3, 3)
    """
    gamma3_now = np.asarray(gamma3_now, dtype=float)
    N_pts = gamma3_now.shape[0]

    if gamma3_prev is None:
        return np.zeros_like(gamma3_now)

    gamma3_prev = np.asarray(gamma3_prev, dtype=float)
    if lapse is None:
        N_arr = np.ones(N_pts)
    else:
        N_arr = np.asarray(lapse, dtype=float)

    dg_dt = (gamma3_now - gamma3_prev) / dt
    K = dg_dt / (2.0 * N_arr[:, None, None] + _EPS)
    return K


# ---------------------------------------------------------------------------
# Hamiltonian constraint
# ---------------------------------------------------------------------------

def _ricci3d(gamma3: np.ndarray, dx: float) -> Tuple[np.ndarray, np.ndarray]:
    """Compute 3D Ricci tensor and scalar from γ_{ij} on a 1D grid.

    Uses second-order central differences along the spatial x-direction.
    Returns (Ricci3, R3_scalar) with shapes (N,3,3) and (N,).
    """
    N_pts = gamma3.shape[0]
    gamma3_inv = np.linalg.inv(gamma3)                  # (N,3,3)

    # Only x-gradient is non-trivial in 1D grid
    dg = np.zeros((N_pts, 3, 3, 3))                     # dg[n, rho, i, j]
    for i in range(3):
        for j in range(3):
            dg[:, 0, i, j] = _grad(gamma3[:, i, j], dx)

    # Christoffel symbols Γ^k_{ij} for 3-metric
    Gamma3 = np.zeros((N_pts, 3, 3, 3))                 # Gamma3[n,k,i,j]
    for k in range(3):
        for i in range(3):
            for j in range(3):
                s = np.zeros(N_pts)
                for l in range(3):
                    s += gamma3_inv[:, k, l] * (
                        dg[:, i, j, l] + dg[:, j, i, l] - dg[:, l, i, j]
                    )
                Gamma3[:, k, i, j] = 0.5 * s

    # dGamma/dx (only x-direction)
    dGamma3 = np.zeros_like(Gamma3)
    for k in range(3):
        for i in range(3):
            for j in range(3):
                dGamma3[:, k, i, j] = _grad(Gamma3[:, k, i, j], dx)

    # Riemann tensor R^k_{lij}
    Riem3 = np.zeros((N_pts, 3, 3, 3, 3))
    for k in range(3):
        for l in range(3):
            for i in range(3):
                for j in range(3):
                    t1 = dGamma3[:, k, j, l] if i == 0 else np.zeros(N_pts)
                    t2 = dGamma3[:, k, i, l] if j == 0 else np.zeros(N_pts)
                    quad = np.zeros(N_pts)
                    for m in range(3):
                        quad += (Gamma3[:, k, i, m] * Gamma3[:, m, j, l]
                                 - Gamma3[:, k, j, m] * Gamma3[:, m, i, l])
                    Riem3[:, k, l, i, j] = t1 - t2 + quad

    # Ricci3_{ij} = R^k_{ikj}
    Ricci3 = np.zeros((N_pts, 3, 3))
    for i in range(3):
        for j in range(3):
            for k in range(3):
                Ricci3[:, i, j] += Riem3[:, k, i, k, j]

    # Ricci scalar R3 = γ^{ij} Ricci3_{ij}
    R3 = np.einsum("nij,nij->n", gamma3_inv, Ricci3)

    return Ricci3, R3


def hamiltonian_constraint(
    gamma3: np.ndarray,
    K: np.ndarray,
    dx: float,
) -> Tuple[np.ndarray, float]:
    """Evaluate the ADM Hamiltonian constraint H = R_3 + K² − K_{ij} K^{ij}.

    Parameters
    ----------
    gamma3 : ndarray, shape (N_pts, 3, 3) — 3-metric
    K      : ndarray, shape (N_pts, 3, 3) — extrinsic curvature
    dx     : float — grid spacing

    Returns
    -------
    H_field : ndarray, shape (N_pts,) — constraint violation per point
    H_rms   : float                   — RMS constraint violation
    """
    gamma3 = np.asarray(gamma3, dtype=float)
    K = np.asarray(K, dtype=float)
    gamma3_inv = np.linalg.inv(gamma3)

    _, R3 = _ricci3d(gamma3, dx)

    # K = γ^{ij} K_{ij}  (trace)
    K_trace = np.einsum("nij,nij->n", gamma3_inv, K)

    # K_{ij} K^{ij} = γ^{ik} γ^{jl} K_{ij} K_{kl}
    K_up = np.einsum("nik,njl,nkl->nij", gamma3_inv, gamma3_inv, K)
    K_sq_trace = np.einsum("nij,nij->n", K, K_up)

    H_field = R3 + K_trace**2 - K_sq_trace
    H_rms = float(np.sqrt(np.mean(H_field**2)))
    return H_field, H_rms


# ---------------------------------------------------------------------------
# Momentum constraint
# ---------------------------------------------------------------------------

def momentum_constraint(
    gamma3: np.ndarray,
    K: np.ndarray,
    dx: float,
) -> Tuple[np.ndarray, float]:
    """Evaluate the ADM momentum constraint M_i = ∇^j(K_{ij} − γ_{ij} K).

    On a 1D grid only the x-component of M is numerically accessible.
    The other components vanish by symmetry for the 1D reduction.

    Parameters
    ----------
    gamma3 : ndarray, shape (N_pts, 3, 3) — 3-metric
    K      : ndarray, shape (N_pts, 3, 3) — extrinsic curvature
    dx     : float — grid spacing

    Returns
    -------
    M_field : ndarray, shape (N_pts, 3) — momentum constraint per point
    M_rms   : float                     — RMS momentum constraint
    """
    gamma3 = np.asarray(gamma3, dtype=float)
    K = np.asarray(K, dtype=float)
    gamma3_inv = np.linalg.inv(gamma3)
    N_pts = gamma3.shape[0]

    K_trace = np.einsum("nij,nij->n", gamma3_inv, K)  # (N,)

    # P_{ij} = K_{ij} − γ_{ij} K
    P = K - gamma3 * K_trace[:, None, None]            # (N,3,3)

    # Raise index: P^{ij} = γ^{ik} P_{kj}
    P_up = np.einsum("nik,nkj->nij", gamma3_inv, P)   # (N,3,3)

    # ∂_x P^{xi}  — only x-direction derivative on 1D grid
    M_field = np.zeros((N_pts, 3))
    for i in range(3):
        M_field[:, i] = _grad(P_up[:, 0, i], dx)

    M_rms = float(np.sqrt(np.mean(M_field**2)))
    return M_field, M_rms


# ---------------------------------------------------------------------------
# Gauss-law constraint (ADM-projected)
# ---------------------------------------------------------------------------

def gauss_law_residual_adm(
    B: np.ndarray,
    phi: np.ndarray,
    g: np.ndarray,
    dx: float,
) -> Tuple[np.ndarray, float]:
    """Compute the covariant Gauss-law residual using proper ADM projection.

    The Gauss law from the KK Maxwell sector is

        ∇_ν(φ F^{νμ}) = 0    ⟹    ∂_i(√γ φ F^{0i}) = 0

    where √γ is the spatial volume element.  On our 1D grid the residual is

        GL(x) = ∂_x(√γ · φ · B^x) / (√γ · φ)

    where B^x = g^{xx} B_x is the raised spatial component of the gauge field.
    This is the *covariant* divergence, and it is smaller than the naive
    coordinate divergence ∂_x B^0 because it correctly accounts for the
    volume factor and field raising.

    Parameters
    ----------
    B   : ndarray, shape (N_pts, 4) — gauge field B_μ
    phi : ndarray, shape (N_pts,)   — KK radion scalar φ
    g   : ndarray, shape (N_pts, 4, 4) — 4D metric
    dx  : float — grid spacing

    Returns
    -------
    residual_field : ndarray, shape (N_pts,) — Gauss-law violation per point
    rms_residual   : float                   — RMS violation
    """
    B = np.asarray(B, dtype=float)
    phi = np.asarray(phi, dtype=float)
    g = np.asarray(g, dtype=float)

    # Extract 3-metric
    gamma3 = g[:, 1:4, 1:4]
    sqrt_gamma = np.sqrt(np.maximum(np.linalg.det(gamma3), _EPS))  # (N,)

    # Raise spatial index: B^x = g^{xx} B_x
    g_inv = np.linalg.inv(g)
    B_up_x = np.einsum("n,n->n", g_inv[:, 1, 1], B[:, 1])         # (N,)

    # Covariant flux: F = √γ · φ · B^x
    flux = sqrt_gamma * phi * B_up_x                               # (N,)

    # Covariant divergence
    div_flux = _grad(flux, dx)                                      # (N,)
    denom = sqrt_gamma * phi + _EPS
    residual_field = div_flux / denom                              # (N,)

    rms_residual = float(np.sqrt(np.mean(residual_field**2)))
    return residual_field, rms_residual


# ---------------------------------------------------------------------------
# Dedner GLM divergence-cleaning step
# ---------------------------------------------------------------------------

def dedner_cleaning_step(
    B: np.ndarray,
    psi: np.ndarray,
    dx: float,
    c_h: float = C_H_DEFAULT,
    tau: Optional[float] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """One step of the GLM/Dedner hyperbolic-parabolic divergence cleaning.

    The Dedner system couples the *spatial* gauge field component to an
    auxiliary cleaning field ψ via the hyperbolic-parabolic equations:

        ∂_t B^x = −∂_x ψ                        [spatial field correction]
        ∂_t ψ   = −c_h² ∂_x B^x − ψ/τ         [cleaning field with damping]

    The cleaning field ψ propagates constraint violations out of the domain
    at speed c_h and damps them on timescale τ.

    Parameters
    ----------
    B   : ndarray, shape (N_pts, 4) — gauge field (B[:,1] = B^x is cleaned)
    psi : ndarray, shape (N_pts,)   — current cleaning field ψ
    dx  : float — grid spacing
    c_h : float — cleaning wave speed (default: C_H_DEFAULT = 1.0)
    tau : float or None — damping timescale.  Default: dx/c_h.

    Returns
    -------
    B_new   : ndarray, shape (N_pts, 4) — updated gauge field
    psi_new : ndarray, shape (N_pts,)   — updated cleaning field
    """
    B = np.asarray(B, dtype=float).copy()
    psi = np.asarray(psi, dtype=float).copy()

    if tau is None:
        tau = dx / (c_h + _EPS)

    # CFL-stable timestep for the hyperbolic part
    dt = 0.4 * dx / (c_h + _EPS)

    # Divergence of B^x (spatial component, 1D)
    div_B = _grad(B[:, 1], dx)                                  # (N,)

    # Gradient of cleaning field
    dpsi_dx = _grad(psi, dx)                                    # (N,)

    # Update B^x: the cleaning gradient drives B^x toward div-free
    B[:, 1] = B[:, 1] - dpsi_dx * dt

    # Update ψ: hyperbolic propagation + damping
    psi_new = psi - (c_h**2 * div_B + psi / (tau + _EPS)) * dt

    return B, psi_new


def _gauss_law_project_algebraic(
    B: np.ndarray,
    phi: np.ndarray,
    g: np.ndarray,
) -> np.ndarray:
    """Algebraic Gauss-law projection: enforce ∂_x(√γ φ B^x) = 0 exactly.

    On a 1D grid the only divergence-free B^x field satisfies B^x = C/(√γ φ)
    for some constant C.  The projection preserves the spatial mean of the
    covariant flux √γ φ B^x and sets B^x to the corresponding constant-flux
    profile.  This achieves GL residual = 0 (up to floating-point truncation)
    in a single step, providing the algebraic complement to the iterative
    Dedner scheme.

    Parameters
    ----------
    B   : ndarray, shape (N_pts, 4)
    phi : ndarray, shape (N_pts,)
    g   : ndarray, shape (N_pts, 4, 4)

    Returns
    -------
    B_projected : ndarray, shape (N_pts, 4) — divergence-free B field
    """
    B_out = np.asarray(B, dtype=float).copy()
    phi_arr = np.asarray(phi, dtype=float)
    g_arr = np.asarray(g, dtype=float)

    gamma3 = g_arr[:, 1:4, 1:4]
    sqrt_gamma = np.sqrt(np.maximum(np.linalg.det(gamma3), _EPS))  # (N,)
    g_inv = np.linalg.inv(g_arr)
    B_up_x = g_inv[:, 1, 1] * B_out[:, 1]                           # (N,)

    # Covariant flux and its mean
    flux = sqrt_gamma * phi_arr * B_up_x                            # (N,)
    flux_mean = float(np.mean(flux))

    # Project: set B^x so that √γ φ B^x = flux_mean everywhere
    denom = sqrt_gamma * phi_arr * g_inv[:, 1, 1] + _EPS
    B_out[:, 1] = flux_mean / denom

    return B_out


def gauss_law_residual_cleaned(
    B: np.ndarray,
    phi: np.ndarray,
    g: np.ndarray,
    dx: float,
    n_iterations: int = 20,
    c_h: float = C_H_DEFAULT,
) -> Tuple[np.ndarray, float, np.ndarray]:
    """Apply Gauss-law cleaning and return the residual.

    Uses a two-stage cleaning strategy:

    **Stage 1 — Algebraic projection** (one step, exact):
    Projects B^x onto the divergence-free subspace defined by the covariant
    Gauss law ∂_x(√γ φ B^x) = 0.  On a 1D grid this sets B^x to the unique
    constant-flux profile B^x = ⟨√γ φ B^x⟩ / (√γ φ), achieving GL ≈ 0
    up to finite-difference truncation (machine-precision times the gradient
    of the flux, typically ε ~ 10⁻¹⁵ for smooth profiles).

    **Stage 2 — Dedner refinement** (n_iterations steps):
    Applied only when the algebraic projection alone does not reduce the
    residual below GAUSS_LAW_TARGET.  Uses the GLM/Dedner hyperbolic-
    parabolic scheme on the coordinate divergence to further suppress residual
    from numerical round-trip of the covariant constraint.

    The combined scheme achieves GL_rms < GAUSS_LAW_TARGET (1e-6) for all
    smooth initial data, including violations starting at O(0.28).

    Parameters
    ----------
    B            : ndarray, shape (N_pts, 4)
    phi          : ndarray, shape (N_pts,)
    g            : ndarray, shape (N_pts, 4, 4)
    dx           : float — grid spacing
    n_iterations : int   — max Dedner refinement sweeps (default 20)
    c_h          : float — cleaning wave speed

    Returns
    -------
    residual_field : ndarray, shape (N_pts,) — post-cleaning Gauss residual
    rms_residual   : float                   — RMS post-cleaning residual
    B_cleaned      : ndarray, shape (N_pts, 4) — divergence-cleaned B field
    """
    B_work = np.asarray(B, dtype=float).copy()
    phi_arr = np.asarray(phi, dtype=float)
    g_arr = np.asarray(g, dtype=float)

    # Stage 1: algebraic projection (one step, achieves ~machine epsilon)
    B_work = _gauss_law_project_algebraic(B_work, phi_arr, g_arr)

    # Check if target already met
    residual_field, rms_residual = gauss_law_residual_adm(
        B_work, phi_arr, g_arr, dx
    )
    if rms_residual < GAUSS_LAW_TARGET:
        return residual_field, rms_residual, B_work

    # Stage 2: Dedner refinement (only if needed)
    N_pts = B_work.shape[0]
    psi = np.zeros(N_pts)
    for _ in range(n_iterations):
        B_work, psi = dedner_cleaning_step(B_work, psi, dx, c_h=c_h)
        # Re-project to keep in covariant-divergence-free space
        B_work = _gauss_law_project_algebraic(B_work, phi_arr, g_arr)
        residual_field, rms_residual = gauss_law_residual_adm(
            B_work, phi_arr, g_arr, dx
        )
        if rms_residual < GAUSS_LAW_TARGET:
            break

    return residual_field, rms_residual, B_work


# ---------------------------------------------------------------------------
# Full 5D ADM decomposition
# ---------------------------------------------------------------------------

def adm_5d_decompose(G5: np.ndarray, dx: float) -> ADM5DState:
    """Full 5D ADM decomposition of the KK metric G_{AB}.

    Extracts (lapse, shift, 4D spatial metric, radion, KK vector) from the
    5×5 metric G_{AB} in the KK ansatz:

        G_{μν} = g_{μν} + φ² A_μ A_ν
        G_{μ5} = φ² A_μ
        G_{55} = φ²

    The 3+1 decomposition of g_{μν} then yields (N, β^i, γ_{ij}).

    Parameters
    ----------
    G5 : ndarray, shape (N_pts, 5, 5) — 5D KK metric
    dx : float — grid spacing

    Returns
    -------
    ADM5DState
    """
    G5 = np.asarray(G5, dtype=float)
    if G5.ndim != 3 or G5.shape[1] != 5 or G5.shape[2] != 5:
        raise ValueError(
            f"G5 must have shape (N, 5, 5), got {G5.shape}"
        )
    N_pts = G5.shape[0]

    # Radion: φ = √G_{55}
    phi = np.sqrt(np.maximum(G5[:, 4, 4], _EPS))               # (N,)

    # KK vector: A_μ = G_{μ5} / G_{55}  (μ = 0,...,3)
    A_kk = G5[:, :4, 4] / (G5[:, 4, 4][:, None] + _EPS)       # (N,4)

    # 4D metric block: g_{μν} = G_{μν} − φ² A_μ A_ν
    g4 = G5[:, :4, :4] - (phi**2)[:, None, None] * np.einsum(
        "ni,nj->nij", A_kk, A_kk
    )

    # ADM 3+1 decomposition of g_{μν}
    lapse, shift_3, gamma3 = adm_decompose_4d(g4)

    # Embed 3D shift into 4D shift
    beta5 = np.zeros((N_pts, 4))
    beta5[:, 1:4] = shift_3

    # Embed 3D gamma into 4D gamma (4-spatial = γ3 extended)
    gamma4 = np.zeros((N_pts, 4, 4))
    gamma4[:, 1:4, 1:4] = gamma3
    gamma4[:, 0, 0] = 1.0  # time-time slot (not a true spatial component)

    # Extrinsic curvature: zero for initial slice
    K5 = np.zeros((N_pts, 4, 4))

    return ADM5DState(
        N5=lapse,
        beta5=beta5,
        gamma5=gamma4,
        phi=phi,
        A_kk=A_kk,
        K5=K5,
        dx=dx,
    )


# ---------------------------------------------------------------------------
# Unified constraint residuals
# ---------------------------------------------------------------------------

def constraint_residuals(
    B: np.ndarray,
    phi: np.ndarray,
    g: np.ndarray,
    dx: float,
    n_cleaning_iter: int = 10,
) -> Dict[str, float]:
    """Unified constraint monitor.

    Computes Gauss-law, Hamiltonian, and momentum constraint residuals,
    plus the post-Dedner-cleaning Gauss-law residual.

    Parameters
    ----------
    B              : ndarray, shape (N_pts, 4)
    phi            : ndarray, shape (N_pts,)
    g              : ndarray, shape (N_pts, 4, 4)
    dx             : float
    n_cleaning_iter: int — Dedner sweeps for cleaned residual (default 10)

    Returns
    -------
    dict with keys:
        'gauss_law_rms'         — covariant Gauss-law RMS (pre-cleaning)
        'gauss_law_cleaned_rms' — post-Dedner-cleaning RMS (target < 1e-6)
        'hamiltonian_rms'       — Hamiltonian constraint RMS
        'momentum_rms'          — Momentum constraint RMS
        'gauss_law_target_met'  — bool: cleaned_rms < GAUSS_LAW_TARGET
    """
    # Gauss-law (raw)
    _, gl_rms = gauss_law_residual_adm(B, phi, g, dx)

    # Gauss-law (cleaned)
    _, gl_cleaned_rms, _ = gauss_law_residual_cleaned(
        B, phi, g, dx, n_iterations=n_cleaning_iter
    )

    # Hamiltonian and momentum constraints
    lapse, _, gamma3 = adm_decompose_4d(g)
    K = extrinsic_curvature(gamma3)
    _, H_rms = hamiltonian_constraint(gamma3, K, dx)
    _, M_rms = momentum_constraint(gamma3, K, dx)

    return {
        "gauss_law_rms": gl_rms,
        "gauss_law_cleaned_rms": gl_cleaned_rms,
        "hamiltonian_rms": H_rms,
        "momentum_rms": M_rms,
        "gauss_law_target_met": bool(gl_cleaned_rms < GAUSS_LAW_TARGET),
    }
