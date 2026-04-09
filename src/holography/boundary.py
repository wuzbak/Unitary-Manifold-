"""
src/holography/boundary.py
==========================
Pillar 4 — Holography and Boundary Dynamics.

Implements the Global Holographic Dictionary that maps bulk quantities
(metric, gauge field, scalar) to boundary data, as described in
Chapters 49–55 of the Unitary Manifold monograph.

Key relations
-------------
Entropy-area law:
    S_∂ = A_∂ / (4 G_4)

Boundary metric evolution:
    ∂_t h_ab = −2 K_ab  +  θ_ab[J_inf]  +  ω_ab[vorticity]
where K_ab is the extrinsic curvature, θ_ab is the information-flux
deformation, and ω_ab captures the surface-gravity vorticity.

Information conservation:
    d/dt ∫ J^0_inf dV  =  surface flux  (checked as a diagnostic)

Public API
----------
boundary_area(h)
    Proper area of the boundary from the 2-D induced metric h_ab.

entropy_area(h, G4)
    Bekenstein–Hawking entropy S_∂ = A_∂ / 4G_4.

BoundaryState
    Container for the boundary metric h_ab and information flux J_bdry.

BoundaryState.from_bulk(bulk_state)
    Project bulk fields onto the boundary.

evolve_boundary(bstate, bulk_state, dt)
    Advance boundary metric by one timestep.

information_conservation_check(J_bulk, J_bdry, dx)
    Verify ∂_t S_bulk ≈ boundary flux (returns relative residual).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..core.metric import field_strength
from ..core.evolution import information_current


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_G4_DEFAULT = 1.0   # Newton's constant in Planck units


# ---------------------------------------------------------------------------
# Area and entropy
# ---------------------------------------------------------------------------

def boundary_area(h: np.ndarray) -> float:
    """Proper area of a 2-D boundary with induced metric h_ab.

    Parameters
    ----------
    h : ndarray, shape (M, 2, 2)
        Induced metric on M boundary points.

    Returns
    -------
    A : float — total proper area  ∫ √det(h) da
    """
    det_h = np.linalg.det(h)                    # (M,)
    det_h = np.clip(det_h, 0.0, None)           # ensure non-negative
    return float(np.sum(np.sqrt(det_h)))


def entropy_area(h: np.ndarray, G4: float = _G4_DEFAULT) -> float:
    """Bekenstein–Hawking entropy  S_∂ = A_∂ / (4 G_4).

    Parameters
    ----------
    h  : ndarray, shape (M, 2, 2)
    G4 : Newton's constant (default 1 in Planck units)

    Returns
    -------
    S : float
    """
    return boundary_area(h) / (4.0 * G4)


# ---------------------------------------------------------------------------
# BoundaryState
# ---------------------------------------------------------------------------

@dataclass
class BoundaryState:
    """Induced boundary metric and information flux at the holographic screen."""

    h: np.ndarray        # shape (M, 2, 2) — induced 2-D metric
    J_bdry: np.ndarray   # shape (M,)       — normal information flux
    kappa: np.ndarray    # shape (M,)       — surface gravity κ
    t: float = 0.0

    # ------------------------------------------------------------------
    @classmethod
    def from_bulk(cls, g: np.ndarray, B: np.ndarray, phi: np.ndarray,
                  dx: float, t: float = 0.0) -> "BoundaryState":
        """Project bulk fields onto the boundary (last grid slice → screen).

        The holographic screen is identified with the boundary of the 1-D
        grid.  The induced metric is taken from the (1,1)–(2,2) block of
        the bulk metric evaluated at the endpoint.

        Parameters
        ----------
        g   : ndarray, shape (N, 4, 4)
        B   : ndarray, shape (N, 4)
        phi : ndarray, shape (N,)
        dx  : float
        t   : float

        Returns
        -------
        BoundaryState
        """
        # Boundary is the last point; replicate to form a M=N boundary surface
        M = g.shape[0]

        # Induced 2-D metric from spatial block (indices 1,2)
        h = g[:, 1:3, 1:3].copy()

        # Information current in bulk
        J_bulk = information_current(g, phi, dx)     # (N, 4)
        # Normal component (x-direction, index 1)
        J_bdry = J_bulk[:, 1]

        # Surface gravity κ ≈ ½ |∂_x g_00|  (Rindler-like approximation)
        kappa = 0.5 * np.abs(np.gradient(g[:, 0, 0], dx, edge_order=2))

        return cls(h=h, J_bdry=J_bdry, kappa=kappa, t=t)


# ---------------------------------------------------------------------------
# Boundary evolution
# ---------------------------------------------------------------------------

def _extrinsic_curvature_approx(h, dx):
    """Approximate extrinsic curvature K_ab ≈ ½ ∂_t h_ab via spatial proxy.

    In the 1-D reduction the extrinsic curvature is approximated by the
    Laplacian of the induced metric components.
    """
    K = np.zeros_like(h)
    for a in range(2):
        for b in range(2):
            K[:, a, b] = (
                np.roll(h[:, a, b], -1) - 2.0 * h[:, a, b] + np.roll(h[:, a, b], 1)
            ) / dx**2
    return K


def _vorticity_term(kappa, h):
    """Surface-gravity vorticity deformation ω_ab.

    ω_ab = κ δ_ab  (diagonal, isotropic approximation).
    """
    N = h.shape[0]
    omega = np.zeros_like(h)
    for a in range(2):
        omega[:, a, a] = kappa
    return omega


def _information_deformation(J_bdry, h):
    """Deformation θ_ab sourced by information flux.

    θ_ab = J_bdry δ_ab  (isotropic contribution from information current).
    """
    theta = np.zeros_like(h)
    for a in range(2):
        theta[:, a, a] = J_bdry
    return theta


def evolve_boundary(bstate: BoundaryState,
                    bulk_state,
                    dt: float) -> BoundaryState:
    """Advance the boundary metric by one timestep dt.

    Evolution law:
        ∂_t h_ab = −2 K_ab + θ_ab[J_inf] + ω_ab[κ]

    Parameters
    ----------
    bstate     : BoundaryState — current boundary state
    bulk_state : FieldState    — corresponding bulk state
    dt         : float

    Returns
    -------
    BoundaryState (updated)
    """
    dx = bulk_state.dx
    h = bstate.h

    K = _extrinsic_curvature_approx(h, dx)
    omega = _vorticity_term(bstate.kappa, h)
    theta = _information_deformation(bstate.J_bdry, h)

    dh = -2.0 * K + theta + omega
    h_new = h + dt * dh
    # Symmetrise
    h_new = 0.5 * (h_new + h_new.transpose(0, 2, 1))

    # Reproject information flux from updated bulk
    g, B, phi = bulk_state.g, bulk_state.B, bulk_state.phi
    J_bulk = information_current(g, phi, dx)
    J_bdry_new = J_bulk[:, 1]
    kappa_new = 0.5 * np.abs(np.gradient(g[:, 0, 0], dx, edge_order=2))

    return BoundaryState(h=h_new, J_bdry=J_bdry_new,
                         kappa=kappa_new, t=bstate.t + dt)


# ---------------------------------------------------------------------------
# Information conservation diagnostic
# ---------------------------------------------------------------------------

def information_conservation_check(J_bulk: np.ndarray,
                                    J_bdry: np.ndarray,
                                    dx: float) -> float:
    """Check bulk information conservation via Gauss's theorem.

    Computes the relative residual:
        |∫ ∇·J_bulk dV − ∮ J_bdry dA| / (|∫ J^0 dV| + ε)

    Parameters
    ----------
    J_bulk : ndarray, shape (N, 4)
    J_bdry : ndarray, shape (N,) — normal flux on boundary
    dx     : float

    Returns
    -------
    residual : float  (0 = perfectly conserved)
    """
    div_J = np.gradient(J_bulk[:, 1], dx, edge_order=2)   # ∂_x J^x
    bulk_integral = float(np.sum(div_J) * dx)
    bdry_flux = float(J_bdry[-1] - J_bdry[0])             # Gauss: endpoints
    charge = float(np.sum(np.abs(J_bulk[:, 0])) * dx) + 1e-12
    return abs(bulk_integral - bdry_flux) / charge
