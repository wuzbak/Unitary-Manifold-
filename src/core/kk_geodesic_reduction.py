# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Conditional circle KK geodesic reduction in an affine 5D parameter.

For ds² = g dx² + φ²(dy + λB dx)² and ∂_y=0,

    p5 = φ²(u5 + λ B_mu u^mu)
    du^mu/dτ = -Γ^mu_ab(g) u^a u^b
               + λ p5 H^mu_nu u^nu + p5² φ^-3 ∂^mu φ.

The first integral p5 is conserved along geodesics, not for arbitrary sampled
velocities. The equation uses the affine 5D parameter, not an assumed 4D proper
time or measured charge-to-mass ratio. A=λB is the circle connection; this
Lorentz-type force does not identify the observed electromagnetic sector.
An odd orbifold metric vector has no photon zero mode.

Finite differences do not obey the continuum product rule exactly. The
independent full-geodesic check therefore converges with grid refinement.
"""

from typing import NamedTuple

import numpy as np

from .metric import assemble_5d_metric, christoffel, field_strength, _grad


class GeodesicDecomposition(NamedTuple):
    """Gravity and Lorentz terms compared to the full projected geodesic.

    acc_total excludes the radion term; residual is minus the radion force
    plus discretisation error. em_ratio is the coefficient λp5 multiplying H,
    NOT a physical charge-to-mass ratio without a parameter normalisation.
    """

    acc_geo: np.ndarray
    acc_lor: np.ndarray
    acc_total: np.ndarray
    acc_5d: np.ndarray
    residual: np.ndarray
    em_ratio: np.ndarray
    p5: np.ndarray


def fifth_momentum(B: np.ndarray, phi: np.ndarray,
                   u4: np.ndarray, u5: np.ndarray,
                   lam: float = 1.0) -> np.ndarray:
    """p5 = G_5A U^A = φ²(u5 + λB_mu u^mu)."""
    return phi**2 * (u5 + lam * np.einsum("ni,ni->n", B, u4))


def christoffel_5d_nu5_block(g: np.ndarray, B: np.ndarray,
                           phi: np.ndarray, dx: float,
                           lam: float = 1.0) -> np.ndarray:
    """Γ^μ_{ν5}; for constant radius it is exactly -λφ² H^μ_ν/2.

    A varying radius adds -λφ B_ν ∂^μ φ in the continuum.
    """
    return christoffel(assemble_5d_metric(g, B, phi, lam), dx)[:, :4, :4, 4]


def lorentz_acceleration(B: np.ndarray, phi: np.ndarray,
                         u4: np.ndarray, u5: np.ndarray,
                         g: np.ndarray, dx: float,
                         lam: float = 1.0) -> tuple:
    """Return (λp5 H^μ_ν u^ν, λp5), using the conserved momentum.

    The isolated coordinate cross-term -2Γ^μ_{ν5}u^νu5 is NOT the complete
    Lorentz force: additional B terms enter through Γ^μ_{αβ}.
    """
    p5 = fifth_momentum(B, phi, u4, u5, lam)
    H_up = np.einsum("nij,njk->nik", np.linalg.inv(g), field_strength(B, dx))
    coefficient = lam * p5
    return coefficient[:, None] * np.einsum("nij,nj->ni", H_up, u4), coefficient


def geodesic_decomposition(g: np.ndarray, B: np.ndarray, phi: np.ndarray,
                          u4: np.ndarray, u5: np.ndarray,
                          dx: float, lam: float = 1.0) -> GeodesicDecomposition:
    """Compare intrinsic gravity plus the Lorentz term to the full 5D geodesic."""
    p5 = fifth_momentum(B, phi, u4, u5, lam)
    acc_geo = -np.einsum("nabc,nb,nc->na", christoffel(g, dx), u4, u4)
    acc_lor, coefficient = lorentz_acceleration(B, phi, u4, u5, g, dx, lam)
    U = np.column_stack((u4, u5))
    Gamma5 = christoffel(assemble_5d_metric(g, B, phi, lam), dx)
    acc_5d = -np.einsum("nabc,nb,nc->na", Gamma5, U, U)[:, :4]
    total = acc_geo + acc_lor
    return GeodesicDecomposition(acc_geo, acc_lor, total, acc_5d,
                                 total - acc_5d, coefficient, p5)


def verify_christoffel_nu5(g: np.ndarray, B: np.ndarray, phi: np.ndarray,
                         dx: float, lam: float = 1.0) -> dict:
    """Compare to -λφ² H^μ_ν/2 - λφ B_ν ∂^μ φ (spatial index 1).

    Exact for constant φ to roundoff, otherwise a continuum convergence check.
    """
    actual = christoffel_5d_nu5_block(g, B, phi, dx, lam)
    inverse = np.linalg.inv(g)
    H_up = np.einsum("nij,njk->nik", inverse, field_strength(B, dx))
    grad_phi_up = inverse[:, :, 1] * _grad(phi, dx)[:, None]
    expected = -0.5 * lam * phi[:, None, None]**2 * H_up
    expected -= lam * phi[:, None, None] * grad_phi_up[:, :, None] * B[:, None, :]
    norm = np.linalg.norm(expected)
    error = np.linalg.norm(actual - expected)
    return {"Gamma_nu5": actual, "expected": expected,
            "rel_error": float(error / norm) if norm > 1e-14 else float("nan")}


def electromagnetic_potential(B: np.ndarray, lam: float = 1.0) -> np.ndarray:
    """Legacy API for the circle connection A=λB, not an orbifold photon."""
    return lam * B
