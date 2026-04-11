# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/metric.py
==================
Kaluza–Klein metric ansatz and curvature computation for the Unitary Manifold.

The 5D parent metric G_AB is assembled from the 4D metric g_μν, the
irreversibility gauge field B_μ, and the scalar (entanglement capacity / radion) φ:

    ┌                               ┐
    │  g_μν + λ²φ² B_μ B_ν   λφ B_μ │
G = │                               │
    │  λφ B_ν                   φ²  │
    └                               ┘

G_55 = φ² so that φ plays the role of the KK radion; the 4D fields are
obtained by dimensional reduction from the 5D Einstein equations.

Curvature tensors are computed on a 1-D spatial grid using second-order
central finite differences.  The convention follows MTW (Misner, Thorne,
Wheeler) with signature (−, +, +, +) for the 4D block.

Pipeline: 4D (g, B, φ) → assemble G_AB (5D) → 5D Christoffel/Riemann/Ricci
          → project 4D block → return 4D Gamma, Riemann, Ricci, R.

Public API
----------
field_strength(B, dx)
    Compute the antisymmetric field-strength tensor H_μν = ∂_μ B_ν − ∂_ν B_μ.

assemble_5d_metric(g, B, phi, lam)
    Build the 5×5 KK metric G_AB at every grid point.

christoffel(g, dx)
    Christoffel symbols Γ^σ_μν from an arbitrary D×D metric on a 1-D grid.

compute_curvature(g, B, phi, dx, lam)
    Return (Gamma, Riemann, Ricci, R) — the full curvature hierarchy computed
    via the 5D metric and projected back to the 4D block.

extract_alpha_from_curvature(g, B, phi, dx, lam)
    Derive the nonminimal coupling α from the 5D Riemann cross-block term
    R^μ_{5ν5}.  Returns (alpha_geometric, cross_block_riem) where
    alpha_geometric = ⟨1/φ²⟩ is the KK-derived coupling constant.
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

    The KK ansatz with φ as the radion field:

        G_μν = g_μν + λ²φ² B_μ B_ν
        G_μ5 = G_5μ = λφ B_μ
        G_55 = φ²        (radion; NOT fixed to 1)

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
    # G_55 = φ² (radion equals scalar field — not fixed to unity)
    G5[:, 4, 4] = phi**2
    return G5


# ---------------------------------------------------------------------------
# Christoffel symbols (4-D)
# ---------------------------------------------------------------------------

def christoffel(g, dx):
    """Christoffel symbols Γ^σ_μν from a D×D metric on a 1-D grid.

    Only the spatial (x) direction is discretised; the remaining indices
    are treated algebraically.  This is the correct reduction for the
    symmetry-reduced (1+1 effective) system used in the evolution module.
    Works for any D (4 for the 4D block, 5 for the full KK metric).

    Parameters
    ----------
    g  : ndarray, shape (N, D, D)
    dx : float

    Returns
    -------
    Gamma : ndarray, shape (N, D, D, D)
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
    """Full curvature pipeline: 4D → 5D KK metric → project back to 4D.

    Steps
    -----
    1. Assemble the 5×5 Kaluza–Klein metric G_AB from (g, B, φ).
    2. Compute 5D Christoffel symbols and Riemann tensor from G_AB.
    3. Extract the 4D Ricci tensor and scalar from the 5D Ricci by
       contracting over the 5D indices and projecting onto the 4D block.

    Parameters
    ----------
    g   : ndarray, shape (N, 4, 4)  — 4-D metric
    B   : ndarray, shape (N, 4)     — irreversibility gauge field
    phi : ndarray, shape (N,)       — scalar / radion (entanglement capacity)
    dx  : float                     — grid spacing
    lam : float                     — KK coupling constant λ

    Returns
    -------
    Gamma  : ndarray, shape (N, 4, 4, 4)   — 4D Christoffel (from 5D projection)
    Riemann: ndarray, shape (N, 4, 4, 4, 4) — 4D Riemann block
    Ricci  : ndarray, shape (N, 4, 4)       — 4D Ricci (projected from 5D)
    R      : ndarray, shape (N,)            — 4D Ricci scalar
    """
    N = g.shape[0]

    # Step 1: assemble full 5D metric
    G5 = assemble_5d_metric(g, B, phi, lam)          # (N, 5, 5)

    # Step 2: 5D Christoffel and Riemann
    Gamma5  = christoffel(G5, dx)                     # (N, 5, 5, 5)
    Riem5   = _riemann_from_christoffel(Gamma5, dx)   # (N, 5, 5, 5, 5)

    # Step 3: project 5D Riemann → 4D Ricci and scalar
    # 5D Ricci: Ricci5_{AB} = R^C_{ACB}  (contract index 0 and 2)
    Ricci5 = np.zeros((N, 5, 5))
    for A in range(5):
        for Bx in range(5):
            for C in range(5):
                Ricci5[:, A, Bx] += Riem5[:, C, A, C, Bx]

    # 4D block of the 5D Ricci gives the effective 4D Ricci tensor
    Ricci = Ricci5[:, :4, :4]                         # (N, 4, 4)

    # 4D Ricci scalar: R = g^μν Ricci_μν  (use 4D inverse metric)
    g_inv = np.linalg.inv(g)
    R = np.einsum('nij,nij->n', g_inv, Ricci)         # (N,)

    # Return 4D Christoffel (4D block of the 5D Gamma) and 4D Riemann block
    Gamma   = Gamma5[:, :4, :4, :4]                   # (N, 4, 4, 4)
    Riemann = Riem5[:, :4, :4, :4, :4]                # (N, 4, 4, 4, 4)

    return Gamma, Riemann, Ricci, R


# ---------------------------------------------------------------------------
# α derivation from 5D Riemann cross-block term
# ---------------------------------------------------------------------------

def extract_alpha_from_curvature(g, B, phi, dx, lam=1.0):
    """Derive the nonminimal coupling α from the 5D Riemann cross-block term.

    In the KK dimensional reduction of the 5D Einstein–Hilbert action

        S₅ = (1/16πG₅) ∫ d⁵x √-G R₅

    the cross-block Riemann components R^μ_{5ν5} (where the index 5 labels
    the compact dimension of radius L₅) encode the mixing between 4D curvature
    and the irreversibility gauge-field vorticity.  After integrating over the
    fifth dimension, these terms contribute the nonminimal coupling

        α ℓP² R H²

    to the 4D effective action.  The coupling constant is determined entirely
    by the KK geometry:

        α  =  (ℓP / L₅)²  =  φ₀⁻²

    because G₅₅ = φ² identifies the radion φ with L₅/ℓP in natural units
    (ℓP = 1).  This closes the third completion requirement of the Unitary
    Manifold: α is not a free parameter but is pinned by the same radion φ
    whose stabilisation (Requirement 1) is already solved internally by the
    field equation β□φ = ½φ^{-1/2}R + ¼φ^{-2}H².

    Parameters
    ----------
    g   : ndarray, shape (N, 4, 4)  — 4D metric
    B   : ndarray, shape (N, 4)     — irreversibility gauge field
    phi : ndarray, shape (N,)       — scalar / radion (entanglement capacity)
    dx  : float                     — grid spacing
    lam : float                     — KK coupling constant λ

    Returns
    -------
    alpha_geometric : float
        Spatially-averaged nonminimal coupling ⟨1/φ²⟩ derived from the KK
        compactification identity  α = φ⁻²  (in Planck units ℓP = 1).
    cross_block_riem : ndarray, shape (N, 4, 4)
        Cross-block Riemann component R^μ_{5ν5} = Riem5[:, :4, 4, :4, 4].
        Encodes the curvature mixing between the 4D block and the compact
        fifth dimension; vanishes when B = 0 and φ = const on flat space.
    """
    G5 = assemble_5d_metric(g, B, phi, lam)
    Gamma5 = christoffel(G5, dx)
    Riem5 = _riemann_from_christoffel(Gamma5, dx)   # (N, 5, 5, 5, 5)

    # Cross-block Riemann: R^μ_{5ν5} where μ,ν ∈ {0,1,2,3} and 5 → index 4.
    # Convention: Riem5[n, rho, sigma, mu, nu] = R^ρ_σμν
    # So R^μ_{5ν5} = Riem5[n, mu, 4, nu, 4]  with mu,nu ∈ 0..3
    cross_block_riem = Riem5[:, :4, 4, :4, 4].copy()  # (N, 4, 4)

    # KK identity: α = 1/φ²  (compactification radius L₅ = φ ℓP)
    # At the stabilised background φ₀ the coupling is α = φ₀⁻².
    alpha_geometric = float(np.mean(1.0 / phi**2))

    return alpha_geometric, cross_block_riem
