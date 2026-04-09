"""
src/core/metric.py
==================
Kaluza–Klein metric ansatz and curvature computation for the Unitary Manifold.

The 5D parent metric G_AB is assembled from the 4D metric g_μν, the
irreversibility gauge field B_μ, and the scalar (entanglement capacity) φ:

    ┌                             ┐
    │  g_μν + λ²φ² B_μ B_ν   λφ B_μ │
G = │                             │
    │  λφ B_ν                  1  │
    └                             ┘

Curvature tensors are computed on a 1-D spatial grid using second-order
central finite differences.  The convention follows MTW (Misner, Thorne,
Wheeler) with signature (−, +, +, +) for the 4D block.

Public API
----------
field_strength(B, dx)
    Compute the antisymmetric field-strength tensor H_μν = ∂_μ B_ν − ∂_ν B_μ.

assemble_5d_metric(g, B, phi, lam)
    Build the 5×5 KK metric G_AB at every grid point.

christoffel(g, dx)
    Christoffel symbols Γ^σ_μν from a 4×4 metric on a 1-D grid.

compute_curvature(g, B, phi, dx, lam)
    Return (Gamma, Riemann, Ricci, R) — the full curvature hierarchy.
"""

import numpy as np


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _grad(f, dx, axis=0):
    """Central finite-difference gradient of array f along *axis*."""
    return np.gradient(f, dx, axis=axis, edge_order=2)


# ---------------------------------------------------------------------------
# Field strength
# ---------------------------------------------------------------------------

def field_strength(B, dx):
    """Return H_μν = ∂_μ B_ν − ∂_ν B_μ  (shape: N × 4 × 4).

    Parameters
    ----------
    B : ndarray, shape (N, 4)
        Gauge field B_μ sampled on N grid points.
    dx : float
        Spatial grid spacing.

    Returns
    -------
    H : ndarray, shape (N, 4, 4)
        Antisymmetric field-strength tensor.
    """
    N, D = B.shape
    H = np.zeros((N, D, D))
    for mu in range(D):
        for nu in range(D):
            if mu != nu:
                dBnu_dmu = _grad(B[:, nu], dx)
                dBmu_dnu = _grad(B[:, mu], dx)
                H[:, mu, nu] = dBnu_dmu - dBmu_dnu
    return H


# ---------------------------------------------------------------------------
# 5-D metric assembly
# ---------------------------------------------------------------------------

def assemble_5d_metric(g, B, phi, lam=1.0):
    """Assemble the 5×5 Kaluza–Klein metric G_AB at each grid point.

    Parameters
    ----------
    g   : ndarray, shape (N, 4, 4)
    B   : ndarray, shape (N, 4)
    phi : ndarray, shape (N,)
    lam : float, KK coupling constant λ (default 1).

    Returns
    -------
    G5 : ndarray, shape (N, 5, 5)
    """
    N = g.shape[0]
    G5 = np.zeros((N, 5, 5))

    lam_phi = lam * phi                          # shape (N,)
    lam_phi_B = lam_phi[:, None] * B            # shape (N, 4)

    # 4×4 block: g_μν + λ²φ² B_μ B_ν
    G5[:, :4, :4] = g + (lam_phi**2)[:, None, None] * np.einsum('ni,nj->nij', B, B)
    # Off-diagonal: G_μ5 = G_5μ = λφ B_μ
    G5[:, :4, 4] = lam_phi_B
    G5[:, 4, :4] = lam_phi_B
    # G_55 = 1 (radion fixed to unity)
    G5[:, 4, 4] = 1.0
    return G5


# ---------------------------------------------------------------------------
# Christoffel symbols (4-D)
# ---------------------------------------------------------------------------

def christoffel(g, dx):
    """Christoffel symbols Γ^σ_μν from the 4-D metric g on a 1-D grid.

    Only the spatial (x) direction is discretised; the remaining indices
    are treated algebraically.  This is the correct reduction for the
    symmetry-reduced (1+1 effective) system used in the evolution module.

    Parameters
    ----------
    g  : ndarray, shape (N, 4, 4)
    dx : float

    Returns
    -------
    Gamma : ndarray, shape (N, 4, 4, 4)
        Gamma[n, sigma, mu, nu]
    """
    N, D, _ = g.shape
    # Inverse metric
    g_inv = np.linalg.inv(g)                    # (N, 4, 4)

    # Partial derivatives ∂_ρ g_μν  — only x-component is non-trivial on 1-D grid
    # We store dg[n, rho, mu, nu]; rho=0 is x, others are zero for this reduction.
    dg = np.zeros((N, D, D, D))
    for mu in range(D):
        for nu in range(D):
            dg[:, 0, mu, nu] = _grad(g[:, mu, nu], dx)

    # Γ^σ_μν = ½ g^{σρ} (∂_μ g_{νρ} + ∂_ν g_{μρ} − ∂_ρ g_{μν})
    Gamma = np.zeros((N, D, D, D))
    for sigma in range(D):
        for mu in range(D):
            for nu in range(D):
                s = np.zeros(N)
                for rho in range(D):
                    s += g_inv[:, sigma, rho] * (
                        dg[:, mu, nu, rho] +
                        dg[:, nu, mu, rho] -
                        dg[:, rho, mu, nu]
                    )
                Gamma[:, sigma, mu, nu] = 0.5 * s
    return Gamma


# ---------------------------------------------------------------------------
# Riemann, Ricci, Ricci scalar
# ---------------------------------------------------------------------------

def _riemann_from_christoffel(Gamma, dx):
    """R^ρ_σμν from Christoffel symbols (1-D grid, x-direction only).

    R^ρ_σμν = ∂_μ Γ^ρ_νσ − ∂_ν Γ^ρ_μσ + Γ^ρ_μλ Γ^λ_νσ − Γ^ρ_νλ Γ^λ_μσ
    """
    N, D = Gamma.shape[0], Gamma.shape[1]
    Riem = np.zeros((N, D, D, D, D))

    dGamma = np.zeros_like(Gamma)              # ∂_x Gamma only
    for s in range(D):
        for m in range(D):
            for n in range(D):
                dGamma[:, s, m, n] = _grad(Gamma[:, s, m, n], dx)

    for rho in range(D):
        for sigma in range(D):
            for mu in range(D):
                for nu in range(D):
                    # Derivative terms (only mu=0 or nu=0 contributes on 1-D grid)
                    term1 = dGamma[:, rho, nu, sigma] if mu == 0 else np.zeros(N)
                    term2 = dGamma[:, rho, mu, sigma] if nu == 0 else np.zeros(N)
                    # Quadratic terms
                    quad = np.zeros(N)
                    for lam in range(D):
                        quad += (Gamma[:, rho, mu, lam] * Gamma[:, lam, nu, sigma] -
                                 Gamma[:, rho, nu, lam] * Gamma[:, lam, mu, sigma])
                    Riem[:, rho, sigma, mu, nu] = term1 - term2 + quad
    return Riem


def compute_curvature(g, B, phi, dx, lam=1.0):
    """Full curvature pipeline for the Walker–Pearson system.

    Parameters
    ----------
    g   : ndarray, shape (N, 4, 4)  — 4-D metric
    B   : ndarray, shape (N, 4)     — irreversibility gauge field
    phi : ndarray, shape (N,)       — scalar (entanglement capacity)
    dx  : float                     — grid spacing
    lam : float                     — KK coupling constant λ

    Returns
    -------
    Gamma  : ndarray, shape (N, 4, 4, 4)
    Riemann: ndarray, shape (N, 4, 4, 4, 4)
    Ricci  : ndarray, shape (N, 4, 4)
    R      : ndarray, shape (N,)
    """
    N, D = g.shape[0], g.shape[1]
    Gamma = christoffel(g, dx)
    Riemann = _riemann_from_christoffel(Gamma, dx)
    # Ricci_μν = R^ρ_{μρν}  (contract first and third indices of Riemann)
    Ricci = np.zeros((N, D, D))
    for mu in range(D):
        for nu in range(D):
            for rho in range(D):
                Ricci[:, mu, nu] += Riemann[:, rho, mu, rho, nu]

    g_inv = np.linalg.inv(g)
    R = np.einsum('nij,nij->n', g_inv, Ricci)
    return Gamma, Riemann, Ricci, R
